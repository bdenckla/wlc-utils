"""HTML rendering for the "almost errors" page.

The presentation layer: page-data constants, small render helpers, the page
sections (mostly long prose), and ``render_body_contents`` which assembles them.
The "real computing" -- the mode-aware parse trees and verdicts these sections
display -- lives in ``almost_errors_trees``; this module imports it and only
formats its output.

It shares goerwitz.html's stylesheet + width-limited shell and the shared
error-tree table renderer (``ob_tree_table``), so a later merge with the
prose/poetic reports is mechanical.
"""

from __future__ import annotations

from accgram import almost_errors_trees as aet
from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import rtms_report
from accgram import rtmsr_media
from accgram.ply_scanner import HasLegarmeh
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from py_html import wlc_utils_html as H
from py_wlc import my_wlc_bcv_str

_REPORT_TITLE = "Almost errors"
_WIDTH_CLASS = "goerwitz-tms-width-limited"

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

# The five ways to hand ek20:31's mahapakh + qadma pair to the grammar: the fused token
# the checker actually emits, plus the four alternatives (drop one mark, or keep both as
# a sequence in either order).  Only two parse cleanly: the fused token and the
# qadma-then-mahapakh sequence.
#
# The reason is the *three*-servus context, which is easy to miss.  This pashta (on the
# following word גִּלּוּלֵיכֶם) is served by three conjunctives: a telisha qetanna on the
# preceding word אַתֶּם, then the azla (qadma) and mahapakh that share ek20:31's alef.  Every
# pashta_phrase rule for a telisha-qetanna-headed chain puts AZLA directly after the
# TELISHAQETANNA -- TELISHAQETANNA AZLA MAHAPAKH PASHTA, or its one-token analogue
# TELISHAQETANNA MAHAPAKHAZLA PASHTA -- because the masoretic rule is that a telisha
# qetanna is *always* followed by azla (Yeivin #246).  So here azla is an obligatory
# bridge, not an optional mark:
#   fused          TELISHAQETANNA MAHAPAKHAZLA PASHTA  -> clean
#   seq_azla_mah   TELISHAQETANNA AZLA MAHAPAKH PASHTA -> clean (same reading, two letters)
#   drop_azla      TELISHAQETANNA MAHAPAKH PASHTA      -> no rule (mahapakh can't follow telq)
#   drop_mahapakh  TELISHAQETANNA AZLA PASHTA          -> no rule (azla needs mahapakh/merkha)
#   seq_mah_azla   TELISHAQETANNA MAHAPAKH AZLA PASHTA -> wrong order
# A *bare* MAHAPAKH PASHTA rule does exist (a one-servus pashta), so dropping the azla
# would parse if this pashta stood alone -- but it never does here, because the telisha
# qetanna makes the chain three deep.  The verdict table makes the clean/ERROR split
# visible.
_EK_MODES = (
    ("fused", "fuse into one mahapakh!azla token (what the checker does)"),
    ("drop_azla", "keep the mahapakh, drop the qadma"),
    ("drop_mahapakh", "keep the qadma, drop the mahapakh"),
    ("seq_azla_mah", "keep both, as a qadma then mahapakh sequence"),
    ("seq_mah_azla", "keep both, as a mahapakh then qadma sequence"),
)

# MAM's documentation note on ek20:31 (from MAM-parsed-plus / MAM-with-doc), the
# witness that ek20:31's double-marking is standard masoretic tradition, not an L
# anomaly.  Quoted (Hebrew) and paraphrased (English) on the page.
_EK2031_MAM_NOTE_HE = (
    "זאת התיבה היחידה בכל המקרא שיש בה שני טעמים מחברים בהברה אחת."
    " הקדמא קודמת למהפך בקריאה, כמו בעוד שש מקומות במקרא (שבהם הקדמא"
    " במקום הראוי לגעיה והמהפך בהברת הטעם), כגון: ויקרא כה,מו; במדבר [כ,א]."
)

# The six places (besides ek20:31) where a qadma sits in a syllable fit for a ga'ya and
# a mahapakh on the stressed syllable -- the pattern the MAM note above invokes.  The note
# names only the first two as examples (and miscites Num 20:1 as "21:1"); the other four
# are flagged ``supplied`` so the page can list them separately as our additions, not the
# note's.  (bb, chnu, vrnu, display, supplied)
_QADMA_GAYA_REFS = (
    ("lv", 25, 46, "Lev. 25:46", False),
    ("nu", 20, 1, "Num. 20:1", False),
    ("ek", 43, 11, "Ezek. 43:11", True),
    ("2c", 35, 25, "2 Chron. 35:25", True),
    ("da", 3, 2, "Dan. 3:2", True),
    ("er", 7, 24, "Ezra 7:24", True),
)


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


def _qadma_gaya_links(*, supplied: bool) -> tuple[object, ...]:
    """The qadma-as-ga'ya + mahapakh places as a ``; ``-joined run of MAM-with-doc links,
    filtered to either the two the MAM note names as examples (``supplied=False``) or the
    four supplied here (``supplied=True``)."""
    nodes: list[object] = []
    for bb, chnu, vrnu, display, is_supplied in _QADMA_GAYA_REFS:
        if is_supplied != supplied:
            continue
        if nodes:
            nodes.append("; ")
        nodes.append(_link(display, rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)))
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
                " one letter or one word — but"
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
                "A plain geresh in a poetic verse is otherwise a lexical"
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
                " across letters, which is meaningful reading order. See the ",
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
            items.append(_render_tree(aet._telg_tree_text(bcv, mode, index, parser, has_legarmeh)))
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
        word = aet._telg_gerstar_word(index[bcv])
        verdicts = tuple(
            aet._telg_verdict_for(bcv, mode, index, parser, has_legarmeh)
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


def _ek_verdict_table(index, parser, has_legarmeh: HasLegarmeh) -> object:
    """One row per ek20:31 reading (``_EK_MODES``): the reading and its parse verdict."""
    rows: list[object] = [H.table_row_of_headers(("reading", "verdict"))]
    for mode, label in _EK_MODES:
        verdict = aet._ek_verdict_for(mode, index, parser, has_legarmeh)
        rows.append(H.table_row_of_data((label, verdict)))
    return H.table(tuple(rows), {"class": "limited-width"})


def _oddities_intro() -> tuple[object, ...]:
    return (
        H.heading_level_2("Masoretically-blessed oddities (not charities)"),
        H.para(
            "The features below would make a naïve checker blink — two accents sharing"
            " one letter or one word — but"
            " none of them is a quirk of LC, BHS, or WLC to be forgiven. They are"
            " official masoretic tradition, attested in the standard witnesses. The"
            " checker accepts them; its only real decision is one of representation —"
            " which mark to carry into the parse, or how to fuse a pair — and, as the"
            " telisha gedola exhibit shows, that decision is a choice among readings"
            " that all parse cleanly."
        ),
    )


def _ek2031_section(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    tree_text = aet._prose_verse_tree_text("ek20:31", index, parser, has_legarmeh)
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
                "That this double accent is intentional in the LC is"
                " supported by the word’s masorah qetannah note,"
                " ל̇ בטע̇" # we purposely don't format this as hbo because Taamey D doesn't support "combining dot above" well
                " (“[this is the] one [word in all Tanakh that appears] with [these]"
                " accents [arranged like this]”):",
            )
        ),
        *rtmsr_media.render_image_paragraphs(
            {"img": "LC-286A-col-3-line-21-Ezek-20v31.png"},
            structured_text_lookup=lambda row, key: row.get(key),
        ),
        H.para(
            (
                "MAM has this double accent,"
                " and has a documentation note citing support for it from"
                " three standard witnesses (Aleppo, Leningrad, Cairo) and their masorot."
                " MAM also cites Yeivin 28.1 p. 232."
                " MAM spells out why this double accent is puzzling yet standard:",
            )
        ),
        H.blockquote(_EK2031_MAM_NOTE_HE, {"dir": "rtl"}),
        H.blockquote(
            (
                "This is the only word in all of Tanakh with two conjunctive accents on one letter;"
                " the qadma precedes the mahapakh in chanting,"
                " as in six other places where [(on a single word)]"
                " a qadma occupies a syllable fit for a ga‘ya"
                " and a mahapakh occupies the stressed syllable, for example: ",
                *_qadma_gaya_links(supplied=False),
                ".",
            )
        ),
        H.para(
            (
                "The note names only those two as examples — and writes"
                " “Num. 21:1” where it means Num. 20:1. The other four verses alluded to"
                " above are as follows, making six total: ",
                *_qadma_gaya_links(supplied=True),
                ". See the full note on the ",
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
            (
                "How forced is the fusion? Unlike the telisha gedola readings above — where"
                " every alternative parses cleanly and the choice is merely cosmetic — here"
                " the grammar all but dictates it. The table below runs the verse through"
                " the real checker under each of the five ways to present the pair: the"
                " fused token, dropping either mark, and keeping both as a sequence in"
                " either order. Only two parse: the fused ",
                H.code("mahapakh!azla"),
                " token and the qadma-then-mahapakh sequence — and those coincide,"
                " because the same pashta phrase rule that accepts the fused cluster also"
                " accepts the cross-letter ",
                H.code("azla mahapakh"),
                " pair, in exactly the reading order the MAM note describes (qadma before"
                " mahapakh).",
            )
        ),
        H.para(
            (
                "Why the other three readings fail is worth spelling out, because it is"
                " not merely that “a word needs an accent.” The pashta here is served by"
                " three conjunctives: a telisha qetanna on the preceding word ",
                _hbo("אַתֶּם"),
                ", then the qadma and mahapakh sharing this word’s alef. Once a"
                " telisha qetanna heads the chain, the grammar admits only ",
                H.code("telisha-qetanna azla mahapakh pashta"),
                " (or its one-token analogue ",
                H.code("telisha-qetanna mahapakh!azla pashta"),
                ") — the azla is obligatory, because the masoretic rule (Yeivin §246) is"
                " that a telisha qetanna is always followed by azla. So ",
                H.bold("keep the mahapakh, drop the qadma"),
                " leaves a telisha qetanna directly before a bare mahapakh — a sequence"
                " the tradition never produces and the grammar has no rule for — and the"
                " parse falls into error recovery (verdict ERROR, not even a clean"
                " non-parse). Dropping the mahapakh instead leaves an azla with nothing"
                " between it and the pashta, also unruled (azla must be followed by"
                " mahapakh or merkha); and the mahapakh-then-qadma order is simply"
                " backwards. A bare ",
                H.code("mahapakh pashta"),
                " is a perfectly legal one-servus pashta elsewhere, so dropping the qadma"
                " would parse if this pashta stood alone — but it does not, because the"
                " telisha qetanna makes the chain three deep.",
            )
        ),
        _ek_verdict_table(index, parser, has_legarmeh),
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
