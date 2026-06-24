"""Generate gh-pages/accgram/almost-errors.html -- the "almost errors" page.

It documents, in one place, both

  * the **editorial charities** -- places where the accgram checkers silently
    *normalize away* a quirk of WLC (sometimes a genuine Leningrad feature,
    sometimes an artifact introduced in BHS or WLC) and read the text charitably
    rather than flagging it; and

  * one **almost-error that is NOT a charity** -- Ezekiel 20:31's
    ``mahapakh!azla`` same-letter pair, which looks like an error (two cantillation
    accents on one letter) but is a genuine, MAM-confirmed masoretic tradition, not
    a leniency specific to LC/BHS/WLC.

The unifying theme is "almost errors": features that a naive checker would flag,
where the right call -- charity or acceptance -- is a *choice*, and this page makes
those choices visible (with, for the telisha gedola + geresh family, the parse
trees of the readings we did **not** choose).

The page is **generated** rather than hand-authored for one reason: the alternate-
reading parse trees in the telisha gedola exhibit, and the live tree for ek20:31,
are produced from the actual grammar at build time (a mode-aware copy
of ``uni_to_marks.word_to_marks`` drives the three alternate telg readings), so they
can never drift from the checker's real behaviour. It shares goerwitz.html's
stylesheet + width-limited shell and the shared error-tree table renderer
(``ob_tree_table``), so a later merge with the prose/poetic reports is mechanical.

Run via ``main_accgram.py generate-html`` (read-only; no module is
mutated permanently -- the ``word_to_marks`` swap is scoped and restored).
"""

from __future__ import annotations

import argparse
import contextlib
from pathlib import Path

from accgram import accent_marks as am
from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import rtms_data
from accgram import rtms_report
from accgram import run_ply
from accgram import uni_to_marks
from accgram import lexical_validation
from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.ply_scanner import HasLegarmeh, Token, scan_accents
from accgram.ply_tree import print_tree
from accgram.uni_to_marks import (
    _KEPT_NON_ACCENT,
    _MAQAF,
    _PREPOSITIVE_MARKS,
    _is_accent,
    _is_base_letter,
)
from cmn.utf8_io import force_utf8_io
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import provenance
from py_html import wlc_utils_html as H
from py_wlc import my_wlc_bcv_str

_REPORT_TITLE = "Almost errors"
_WIDTH_CLASS = "goerwitz-tms-width-limited"

# The geresh family (plain geresh U+059C, gershayim U+059D's plain sibling, and the
# geresh muqdam U+059D promoted/demoted form) the telisha gedola companion-drop concerns.
_GG = frozenset((am.GERESH, am.GERSHAYIM))

# The five WLC words carrying BOTH telisha gedola and a geresh-family mark -- the
# companions the checker drops to keep just the telg.  (gn5:29 / zp2:15 same-letter;
# 2k17:13 same-letter with geresh muqdam; lv10:4 / ek48:10 cross-letter, same word.)
_TELG_EXHIBIT_REFS = ("gn5:29", "zp2:15", "2k17:13", "lv10:4", "ek48:10")

# The two verses whose full alternate-reading trees the exhibit draws: one same-letter
# (zp2:15), one cross-letter (lv10:4).  The other three get a verdict-table row only --
# their trees differ in the same place and would only repeat the lesson.
_TELG_TREE_REFS = ("zp2:15", "lv10:4")

_TELG_MODES = (
    ("chosen", "drop the geresh-family mark, keep the telisha gedola (what the checker does)"),
    ("keep_gerstar", "drop the telisha gedola, keep the geresh-family mark"),
    ("keep_both", "keep both, as a telisha gedola then a geresh phrase"),
)

# MAM's documentation note on ek20:31 (from MAM-parsed-plus / MAM-with-doc), the
# witness that ek20:31's double-marking is standard masoretic tradition, not an L
# anomaly.  Quoted (Hebrew) and paraphrased (English) on the page.
_EK2031_MAM_NOTE_HE = (
    "זאת התיבה היחידה בכל המקרא שיש בה שני טעמים מחברים בהברה אחת."
    " הקדמא קודמת למהפך בקריאה, כמו בעוד שש מקומות במקרא (שבהם הקדמא"
    " במקום הראוי לגעיה והמהפך בהברת הטעם), כגון: ויקרא כה,מו; במדבר כא,א."
)

# The six places (besides ek20:31) where a qadma sits in a syllable fit for a ga'ya and
# a mahapakh on the stressed syllable -- the pattern the MAM note above invokes.  The note
# names only the first two as examples (and miscites Num 20:1 as "21:1"); the other four
# are flagged ``bracketed`` so the page can mark them as our additions, not the note's.
# (bb, chnu, vrnu, display, bracketed)
_QADMA_GAYA_REFS = (
    ("lv", 25, 46, "Lev. 25:46", False),
    ("nu", 20, 1, "Num. 20:1", False),
    ("ek", 43, 11, "Ezek. 43:11", True),
    ("2c", 35, 25, "2 Chron. 35:25", True),
    ("da", 3, 2, "Dan. 3:2", True),
    ("er", 7, 24, "Ezra 7:24", True),
)


# --------------------------------------------------------------------------- #
# Tree generation
# --------------------------------------------------------------------------- #
def _build_word_variant(word: str, mode: str) -> str:
    """``uni_to_marks.word_to_marks``, but for a word carrying BOTH a telisha gedola
    and a geresh-family mark, apply ``mode`` (chosen / keep_gerstar / keep_both).

    A faithful copy of the Plan B prototype: it rebuilds the mark skeleton, dropping
    the telg or the geresh-family companion per ``mode`` (or neither, for keep_both),
    scoped to words holding *both*; every other word is transcoded normally.
    """
    has_telg = am.TELISHA_GEDOLA in word
    has_gerstar = any((am.GERESH if c == am.GERESH_MUQDAM else c) in _GG for c in word)
    both = has_telg and has_gerstar
    skeleton: list[str | None] = []
    prepos: list[str] = []
    other: list[str] = []
    telg_seen = 0
    for ch in word:
        if _is_base_letter(ch):
            skeleton.append(am.LETTER)
            continue
        if ch == _MAQAF:
            skeleton.append(am.MAQAF)
            continue
        mark: str | None = None
        if _is_accent(ch):
            if ch == am.TELISHA_GEDOLA:
                telg_seen += 1
                if telg_seen > 1:
                    continue
                if both and mode == "keep_gerstar":
                    continue  # drop the telg
                mark = am.TELISHA_GEDOLA
            else:
                as_geresh = am.GERESH if ch == am.GERESH_MUQDAM else ch
                if as_geresh in _GG:
                    if both and mode == "chosen":
                        continue  # drop the geresh-family companion (current behaviour)
                    mark = as_geresh
                else:
                    mark = ch
        elif ch in _KEPT_NON_ACCENT:
            mark = ch
        if mark is None:
            continue
        skeleton.append(None)
        (prepos if mark in _PREPOSITIVE_MARKS else other).append(mark)
    marks = iter(prepos + other)
    return "".join(next(marks) if p is None else p for p in skeleton)


@contextlib.contextmanager
def _word_to_marks_mode(mode: str):
    """Temporarily swap ``uni_to_marks.word_to_marks`` for the mode-aware variant,
    restoring the original on exit (read-only: the module is never left mutated)."""
    original = uni_to_marks.word_to_marks
    uni_to_marks.word_to_marks = lambda w: _build_word_variant(w, mode)
    try:
        yield
    finally:
        uni_to_marks.word_to_marks = original


def _scan_and_parse(bcv: str, body: str, parser, has_legarmeh: HasLegarmeh):
    bb = bcv[:2]
    chnu, vrnu = (int(part) for part in bcv[2:].split(":"))
    tokens = [Token("TILDE", "")] + scan_accents(body, bb, chnu, vrnu, has_legarmeh)
    return parse_tokens(parser, tokens)


def _tree_text(tree) -> str:
    if tree in (None, LOCATION_ONLY):
        return "NO_PARSE"
    return print_tree(tree, 0).rstrip("\n")


def _telg_verdict(tree) -> str:
    if tree in (None, LOCATION_ONLY):
        return "NO_PARSE"
    return "ERROR" if "ERROR" in print_tree(tree) else "clean"


def _telg_tree_text(bcv: str, mode: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    """Tree text for one telg-exhibit verse under one alternate reading ``mode``."""
    with _word_to_marks_mode(mode):
        body = uni_to_marks.verse_to_marks(index[bcv])
    return _tree_text(_scan_and_parse(bcv, body, parser, has_legarmeh))


def _telg_verdict_for(bcv: str, mode: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    with _word_to_marks_mode(mode):
        body = uni_to_marks.verse_to_marks(index[bcv])
    return _telg_verdict(_scan_and_parse(bcv, body, parser, has_legarmeh))


def _prose_verse_tree_text(bcv: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    """The checker's *live* tree text for a prose verse, exactly as run_ply renders it.

    Reuses the run_ply lexical layer (so lv25:20 reads as its ``illegal_mark`` tree,
    grammar skipped) and the same illegal-mark label, so the page can never drift from
    the corpus output."""
    verse = index[bcv]
    body = uni_to_marks.verse_to_marks(verse)
    stranded = lexical_validation.stranded_stress_helpers(
        body
    ) + lexical_validation.illegal_same_letter_pairs(body)
    if stranded:
        words = run_ply._stranded_unicode_words(stranded, verse)
        return print_tree(run_ply._illegal_mark_tree(stranded, words), 0).rstrip("\n")
    return _tree_text(_scan_and_parse(bcv, body, parser, has_legarmeh))


# --------------------------------------------------------------------------- #
# Rendering helpers
# --------------------------------------------------------------------------- #
def _ref_display(bcv: str) -> str:
    bb = bcv[:2]
    chv = bcv[2:]
    return f"{wlc_bb_to_bk39id(bb)} {chv}"


def _verse_links(bcv: str) -> object:
    bb, chnu, vrnu, _bcv = rtms_report.parse_ref_to_wlc_bcv(f"{bcv[:2]} {bcv[2:]}")
    links = (
        H.anchor("UXLC", {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)}),
        " | ",
        H.anchor("MAM", {"href": rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)}),
    )
    return H.para(links)


def _render_tree(tree_text: str) -> object:
    tree = ob_error_context.parse_tree_from_text(tree_text)
    if tree is not None:
        return H.div(
            (ob_tree_table.render_error_tree_table(tree),),
            {"class": "goerwitz-obs-tree-wrap"},
        )
    return H.div(
        (H.htel_mk_inline("pre", None, tree_text),),
        {"class": "goerwitz-obs-tree-wrap"},
    )


def _qadma_gaya_list() -> tuple[object, ...]:
    """The six qadma-as-ga'ya + mahapakh places as a ``; ``-joined run of MAM-with-doc
    links, with the four not named in the MAM note wrapped in square brackets."""
    nodes: list[object] = []
    for index, (bb, chnu, vrnu, display, bracketed) in enumerate(_QADMA_GAYA_REFS):
        if index:
            nodes.append("; ")
        link = _link(display, rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu))
        nodes.extend(("[", link, "]") if bracketed else (link,))
    return tuple(nodes)


def _hbo(text: str) -> object:
    return H.span(text, {"lang": "hbo"})


def _link(text: str, href: str) -> object:
    return H.anchor(text, {"href": href})


def _uxlc_change_link(compact: str) -> object:
    """Anchor to a tanach.us changeset, labelled by its ``changeset-n`` id.

    ``compact`` is the ``release/changeset-n`` form (e.g. ``2020.10.19/2020.09.22-1``)
    the goerwitz page's “UXLC change” links use, expanded by the shared
    ``rtms_report`` helper so the URL form stays single-sourced."""
    changeset_n = compact.partition("/")[2]
    return H.anchor(changeset_n, {"href": rtms_report._expand_uxlc_change_ref(compact)})


# --------------------------------------------------------------------------- #
# Page sections
# --------------------------------------------------------------------------- #
def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(_REPORT_TITLE),
        H.heading_level_2("Introduction"),
        H.para(
            "This page documents the accent-grammar checker's “almost errors”:"
            " cantillation features that a naïve checker would flag, but that we"
            " do not flag — and, in each case, the reading we chose is a choice,"
            " not a forced move. Two kinds appear here."
        ),
        H.para(
            (
                "First, the ",
                H.bold("editorial charities"),
                ": places where the checker silently normalizes away a genuine quirk"
                " of WLC — sometimes a real Leningrad Codex feature, sometimes an"
                " artifact introduced in BHS or WLC — and reads the text charitably"
                " rather than reporting an error. Here something at least questionable"
                " is being forgiven; the value is transparency about exactly what the"
                " checker quietly fixes, in which direction, and why.",
            )
        ),
        H.para(
            (
                "Second, the ",
                H.bold("masoretically-blessed oddities"),
                ": features that look error-like — two cantillation accents crowding"
                " one letter or one word, or a stress-helper riding a disjunctive — but"
                " that are 100% official masoretic tradition, attested in the standard"
                " witnesses, ",
                H.bold("not"),
                " leniencies specific to LC, BHS, or WLC. Nothing here is forgiven; the"
                " checker accepts these, and where it must pick how to represent one for"
                " parsing — which mark to carry into the parse, or how to fuse a pair —"
                " that choice is among readings that all parse cleanly (the"
                " telisha gedola exhibit below shows the alternatives). The headline case"
                " is Ezekiel 20:31’s mahapakh + azla (",
                H.code("mahapakh!azla"),
                "), the only word in Tanakh with two conjunctive accents on"
                " one letter.",
            )
        ),
        H.para(
            (
                "Companion pages: the prose ",
                _link("Goerwitz checker run", "goerwitz.html"),
                " and the ",
                _link("poetic checker run", "poetic.html"),
                " list the verses the checker actually flags; this page is the"
                " inventory of what it deliberately does not.",
            )
        ),
    )


def _charities_intro() -> tuple[object, ...]:
    return (
        H.heading_level_2("Editorial charities"),
        H.para(
            "Each charity below names what the checker normalizes, the direction, and"
            " why, with a citation. Both reinterpret a mark the manuscript should not"
            " have here — a prose geresh muqdam read as a plain geresh, and a stray"
            " poetic geresh promoted into a revia mugrash."
        ),
    )


def _geresh_muqdam_section() -> tuple[object, ...]:
    return (
        H.heading_level_3("Geresh muqdam → geresh (prose)"),
        H.para(
            (
                "Geresh muqdam (U+059D) is a poetic-only sign. In the 21 prose books"
                " WLC uses it just twice — Lev. 1:3 (alone) and 2 Kings 17:13 —"
                " as a typographic device standing in for"
                " a plain geresh. The checker reads it as a plain geresh, so the prose"
                " grammar (which has no geresh muqdam) sees the geresh it expects."
                " Direction: poetic-looking sign → its prose counterpart. tanach.us"
                " itself made the same correction in both verses — changes ",
                _uxlc_change_link("2020.10.19/2020.09.22-1"),
                " (Lev. 1:3) and ",
                _uxlc_change_link("2020.10.19/2020.09.22-2"),
                " (2 Kings 17:13), each described “Change geresh muqdam to geresh.”",
            )
        ),
        H.para(
            (
                "The two verses differ in what happens next. In Lev. 1:3 the"
                " geresh muqdam stands alone, so the charity is the whole story. In 2"
                " Kings 17:13 the converted geresh then sits on a word that also carries"
                " a telisha gedola — so once the charity has run, what remains is one of"
                " the telisha gedola + geresh oddities below (the only one of those five"
                " whose geresh reaches the checker by way of a charity).",
            )
        ),
    )


def _ps124_section() -> tuple[object, ...]:
    return (
        H.heading_level_3("Plain geresh → revia mugrash (poetic): Psalms 124:4"),
        H.para(
            (
                "A plain geresh in a poetic verse is otherwise a fail-fast lexical"
                " error: the poetic grammar has no plain geresh. The sole charitable"
                " exception is Psalms 124:4, where a revia and a plain geresh share"
                " one letter. There the"
                " checker reads the pair charitably as a single revia mugrash — the"
                " established poetic compound — by normalizing the two same-letter"
                " marks into order (revia + geresh → geresh + revia) and promoting the"
                " plain geresh to geresh muqdam, so the existing geresh muqdam + revia"
                " → revia mugrash rule consumes both as one token.",
            )
        ),
        H.para(
            (
                "This within-letter order normalization is licit precisely because it"
                " stays within a single letter — we are liberal about mark order on one"
                " letter (questionable penmanship is not our concern) but preserve order"
                " across letters, which is meaningful reading order. Cite ",
                _link(
                    "tanach.us Psalms 124:4 note",
                    "https://tanach.us/Notes/Psalms/Psalms.124.4.4-c.html",
                ),
                ".",
            )
        ),
    )


def _telg_section(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    items: list[object] = [
        H.heading_level_3("telisha gedola + geresh/gershayim (five words)"),
        H.para(
            "Five WLC words carry both a telisha gedola and a geresh-family companion"
            " (a plain geresh or gershayim — or, in 2 Kings 17:13, a geresh that the"
            " geresh muqdam charity above produced). This double-marking is not a quirk"
            " to forgive: it is official masoretic tradition, attested in the standard"
            " witnesses. What the checker must decide is only how to represent it for"
            " parsing — and there it keeps the telisha gedola and drops the companion."
            " That is a choice, but a choice among grammatically-clean options: the"
            " verses also parse cleanly if the telisha gedola is dropped instead, or if"
            " both marks are kept as a sequence."
        ),
        _telg_verdict_table(index, parser, has_legarmeh),
        H.para(
            "Every one of the five verses parses cleanly under all three readings"
            " (no ERROR, no NO_PARSE), so the choice is not forced by grammaticality —"
            " it is purely a representation preference for the telisha gedola. The two"
            " verses below show the full parse tree under each reading (one same-letter"
            " case, one cross-letter); the trees differ exactly at the companion word,"
            " as expected."
        ),
    ]
    for bcv in _TELG_TREE_REFS:
        items.append(H.htel_mk("h4", None, _ref_display(bcv)))
        items.append(_verse_links(bcv))
        for mode, label in _TELG_MODES:
            items.append(
                H.para(
                    (H.bold(f"{mode}: "), label),
                    {"class": "goerwitz-obs-error-note"},
                )
            )
            items.append(_render_tree(_telg_tree_text(bcv, mode, index, parser, has_legarmeh)))
    items.append(
        H.para(
            (
                "A presentation note: even the same-letter keep-both case"
                " (Zephaniah 2:15) renders as a sequence — a telisha gedola phrase,"
                " then a geresh"
                " phrase, one tree level deeper — not as a fused same-letter cluster,"
                " because the telisha gedola is prepositive (relocated to the front of"
                " the word) and the scanner emits the two marks as separate tokens. So"
                " the real word’s keep-both tree already makes the sequence visible; no"
                " synthetic repeated-word illustration is needed.",
            )
        )
    )
    return tuple(items)


def _telg_verdict_table(index, parser, has_legarmeh: HasLegarmeh) -> object:
    header = H.table_row_of_headers(
        ("verse", "companion word", *(mode for mode, _label in _TELG_MODES))
    )
    rows: list[object] = [header]
    for bcv in _TELG_EXHIBIT_REFS:
        word = _telg_gerstar_word(index[bcv])
        verdicts = tuple(
            _telg_verdict_for(bcv, mode, index, parser, has_legarmeh)
            for mode, _label in _TELG_MODES
        )
        rows.append(
            H.table_row_of_data(
                (
                    H.anchor(
                        _ref_display(bcv),
                        {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)},
                    ),
                    _hbo(word) if word else "—",
                    *verdicts,
                )
            )
        )
    return H.table(tuple(rows), {"class": "limited-width"})


def _telg_gerstar_word(verse: object) -> str | None:
    for word in run_ply._verse_display_words(verse):
        has_telg = am.TELISHA_GEDOLA in word
        has_gerstar = any((am.GERESH if c == am.GERESH_MUQDAM else c) in _GG for c in word)
        if has_telg and has_gerstar:
            return word
    return None


def _oddities_intro() -> tuple[object, ...]:
    return (
        H.heading_level_2("Masoretically-blessed oddities (not charities)"),
        H.para(
            "The features below would make a naïve checker blink — two accents sharing"
            " one letter or one word, or a stress-helper fused onto a disjunctive — but"
            " none of them is a quirk of LC, BHS, or WLC to be forgiven. They are"
            " official masoretic tradition, attested in the standard witnesses. The"
            " checker accepts them; its only real decision is one of representation —"
            " which mark to carry into the parse, or how to fuse a pair — and, as the"
            " telisha gedola exhibit shows, that decision is a choice among readings"
            " that all parse cleanly."
        ),
    )


def _ek2031_section(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    tree_text = _prose_verse_tree_text("ek20:31", index, parser, has_legarmeh)
    return (
        H.heading_level_3("Mahapakh + azla (Ezekiel 20:31)"),
        _verse_links("ek20:31"),
        H.para(
            (
                "In Ezekiel 20:31, ",
                _hbo("נִטְמְאִ֤֨ים"),
                " carries both a mahapakh and a qadma on its"
                " alef. It is the only word in"
                " Tanakh with two conjunctive accents on one letter. The"
                " checker accepts it outright: the scanner fuses the pair into one ",
                H.code("mahapakh!azla"),
                " token, which the grammar parses as an ordinary accent. Unlike the"
                " telisha gedola words, nothing is dropped: both marks survive into the"
                " single fused token.",
            )
        ),
        H.para(
            (
                "MAM has this double accent, and has a documentation note"
                " citing support for this from three standard witnesses (Aleppo, Leningrad, Cairo)"
                " and their masorot. It also cites Yeivin 28.1 p. 232 and spells out why this double accent is"
                " puzzling yet standard:",
            )
        ),
        H.blockquote(_hbo(_EK2031_MAM_NOTE_HE), {"dir": "rtl"}),
        H.para(
            (
                "That is:"
                " this is the only word in all of Tanakh with two conjunctive accents on one letter;"
                " the qadma precedes the mahapakh in reading,"
                " as in six other places where"
                " a qadma occupies a syllable suitable for a ga‘ya"
                " and a mahapakh occupies the stressed syllable: ",
                *_qadma_gaya_list(),
                ". The note names only the first two as examples — and writes"
                " “Num. 21:1” where it means Num. 20:1 (21:1 carries no qadma) —"
                " so the four bracketed references are the remaining places,"
                " supplied here rather than drawn from the note."
                " See the full note on the ",
                _link(
                    "MAM-with-doc Ezekiel page",
                    "https://bdenckla.github.io/MAM-with-doc/C3-Ezekiel.html#c20v31",
                ),
                ". Because the witnesses agree, this double accent is whitelisted"
                " rather than treated an error.",
            )
        ),
        H.para(
            (
                "The instructive contrast is Lev. 25:20, the ",
                H.bold("only other"),
                " prose word with two accents on one letter (a mahapakh and a tipeḥa)."
                " There the witnesses do ",
                H.bold("not"),
                " agree — MAM keeps only the tipeḥa and WLC tags the word anomalous —"
                " so it may well be an error in the LC, and the checker flags it (as a"
                " lexical error). Same surface shape, opposite verdict, decided by the"
                " witnesses. Its full treatment is on the ",
                _link("Goerwitz page", "goerwitz.html#oblv25v20"),
                ". The poetic ",
                H.code("merkha!azla"),
                " of Psalms 56:10 is the same story on the poetic side: the double accent in the LC has no"
                " support from other manuscripts, so it, like Lev. 25:20, is flagged as an error.",
            )
        ),
        H.para(
            "The checker’s parse tree for the verse, with the fused token shown as"
            " mahapakh!azla:"
        ),
        _render_tree(tree_text),
    )


def render_body_contents(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    sections: list[object] = [
        *_intro(),
        # Charities: forgive a genuine LC/BHS/WLC quirk or anomaly.
        *_charities_intro(),
        *_geresh_muqdam_section(),
        *_ps124_section(),
        # Masoretically-blessed oddities: legitimate tradition the checker accepts,
        # where the only decision is representation (which the telg exhibit makes visible).
        *_oddities_intro(),
        *_telg_section(index, parser, has_legarmeh),
        *_ek2031_section(index, parser, has_legarmeh),
    ]
    wrapper = H.div(tuple(sections), {"class": _WIDTH_CLASS})
    return (wrapper,)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def default_html_out_path(repo_root: Path) -> Path:
    return repo_root / "gh-pages" / "accgram" / "almost-errors.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=rtms_data.default_wlc422_kq_u_dir(repo_root),
        help="Directory of WLC 4.22 ketiv/qere Unicode 1verses_*.json files.",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the almost-errors page.",
    )


def run(args: argparse.Namespace) -> None:
    index = rtms_data.load_wlc422_index(args.wlc422_kq_u_dir)
    parser = build_parser()
    has_legarmeh = HasLegarmeh()

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(index, parser, has_legarmeh),
        write_ctx=H.WriteCtx(
            title=_REPORT_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    print(f"HTML: {html_out}")


def main() -> None:
    force_utf8_io()
    repo_root = Path(__file__).resolve().parent.parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
