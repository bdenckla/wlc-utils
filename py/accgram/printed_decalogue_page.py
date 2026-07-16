r"""Generate gh-pages/accgram/printed-decalogue.html -- the printed-tradition Decalogue
grammaticality report (issue #52).

Companion to the dual-cantillation work of issue #36 (which grammar-checks the *manuscript*
taxton/elyon strands by detangling WLC): this page reports whether the *printed tradition*'s
(דפוסים) taxton and elyon accentuations of the two Decalogues parse under the same prose
grammar checker.  It renders live from ``printed_decalogue.check_all`` over the vendored
readings, so it can never drift from the checker's real behaviour.

It also lays out the four cantillation strands of the opening אנכי...עבדים unit (manuscript /
printed x taḥton / elyon) over shared milestone words, resolved by the shared
``printed_decalogue_strands`` module.  The Simanim- and Koren-witness companion pages
(``printed_decalogue_simanim_page``, ``printed_decalogue_koren_page``) link back to that table
rather than duplicating it.

Editorial / style conventions for the rendered prose are single-sourced in
``printed_decalogue_strands`` (bare-Hebrew strand names תחתון / עליון in output, romanized only
in ``title`` / ``alt`` attributes and internal keys; ``ROM_*`` accent names never retyped; real
em dashes).

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds
from accgram import rtms_report
from accgram.almost_errors_html_shared import hbo, link
from cmn.utf8_io import force_utf8_io
from mb_cmn import hebrew_accent_strip as has
from mb_cmn import hebrew_accents as ha
from mb_cmn import hebrew_punctuation as hpunc
import wlc_provenance as provenance

from py_html import wlc_utils_html as H
from py_html.my_html_span_romanized import rmn

import repo_paths

REPORT_TITLE = "In the printed tradition, are the accents of the Decalogue grammatical?"

_GOERWITZ_URL = "goerwitz.html"
_SOURCE_URL = "https://he.wikisource.org/wiki/עשרת_הדברות_בסיס/טעמים"

_CTR_REVIEW_URL = (
    "https://bdenckla.github.io/MAM-with-doc/misc/rocc_0_review_of_ctr.html"
)

# In-page anchor for the appendix cataloguing the grammar-irrelevant p-trad-vs-m-trad תחתון
# differences (single-sourced: used as both the verdict-paragraph link's href fragment and the
# appendix heading's id, matching the #four-strands / #why-the-printed-elyon-fails style).
_TAHTON_DETAILS_ID = "tahton-details"


# Strand names are single-sourced in printed_decalogue_strands (see its module docstring). These
# thin local aliases let the Hebrew strand words drop straight into the prose -- bare in a string
# or as {_TAHTON} / {_ELYON} inside an f-string -- rather than through a lang="he" <span> (issue
# #58), matching the Simanim companion page. Genuinely *pointed* Hebrew still goes through hbo()
# (lang="hbo" -> the Taamey pointed-text font); only bare consonantal terms are inlined this way.
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON


# Romanized accent/mark names, each pre-wrapped ONCE in <span class="romanized"> (italic) so every
# prose site below is styled without a per-site rmn() call -- issue #65, finding C2; the rule and
# its exclusions are documented in printed_decalogue_strands' module docstring. These are HTML
# nodes, not strings: splice them into a contents tuple, never into an f-string. The underlying
# spellings stay single-sourced in pds -- don't retype them inline.
_ROM_ETNAHTA = rmn(pds.ROM_ETNAHTA)
_ROM_LEGARMEH = rmn(pds.ROM_LEGARMEH)
_ROM_PASEQ = rmn(pds.ROM_PASEQ)
_ROM_REVIA = rmn(pds.ROM_REVIA)
_ROM_SEGOLTA = rmn(pds.ROM_SEGOLTA)
_ROM_SOF_PASUQ = rmn(pds.ROM_SOF_PASUQ)
_ROM_TIPEHA = rmn(pds.ROM_TIPEHA)
_ROM_SILLUQ_SOF_PASUQ = rmn(pds.ROM_SILLUQ_SOF_PASUQ)


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=pd.default_source_path())
    parser.add_argument(
        "--html-out", type=Path, default=default_html_out_path(repo_root)
    )


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
# Keys into the by-key dict are prefixed (bk-/sk-/tk-) to mark them, at a glance, as internal
# lookup tokens rather than user-visible strings. The raw VersionResult fields are bare
# ("ex", "taxton", "manuscript"); this is the one place they get promoted to prefixed keys, so
# every lookup below must use the prefixed form.
def _bk(vr: pd.VersionResult) -> tuple[str, str, str]:
    return (f"bk-{vr.book}", f"sk-{vr.reading}", f"tk-{vr.tradition}")


def _by_key(
    results: list[pd.VersionResult],
) -> dict[tuple[str, str, str], pd.VersionResult]:
    return {_bk(vr): vr for vr in results}


def _intro() -> tuple[object, ...]:
    # This is the ONE full statement of the four strands in the page trio (issue #65, finding V5).
    # The two satellite pages (printed_decalogue_simanim_page, printed_decalogue_koren_page) used to
    # duplicate this paragraph verbatim; each now opens with a single "As the companion page
    # explains..." sentence linking here instead, so a reader arriving from a satellite can tell
    # reiteration from new material. Keep it that way: don't re-expand the satellites. The one
    # thing all three pages DO say verbatim is the closing pds.MOST_STRIKING sentence, single-
    # sourced there rather than retyped here -- so edit that constant, not this paragraph, to
    # restate the difference; everything else in this paragraph is the main page's alone.
    return (
        H.heading_level_1(REPORT_TITLE),
        H.heading_level_2("The question"),
        H.para(
            (
                "Roughly speaking, each Decalogue",
                " has two strands of cantillation, the טעם תחתון and the טעם עליון.",
                " Why is this only roughly true? Because in detail there are",
                *[" ", H.bold("four"), " strands: the"],
                *[" ", H.bold("printed tradition"), " (p-trad)"],
                " and the",
                *[" ", H.bold("manuscript tradition"), " (m-trad)"],
                " differ in cantillation,",
                f" yielding two different {_ELYON} strands and two different {_TAHTON} strands.",
                #
                " (The p-trad is fading, but still visible in editions like Koren and Simanim's"
                " Tiqqun.)",
                #
                # Single-sourced in pds and shared verbatim with the two satellite pages; see
                # pds.MOST_STRIKING for why the difference is stated over this span rather than
                # as the older yes/no question about אנכי…עבדים.
                " " + pds.MOST_STRIKING,
            )
        ),
        H.para(
            (
                "I have run Richard Goerwitz's ",
                link("accent grammar checker", _GOERWITZ_URL),
                " against the m-trad strands (as represented by WLC); this page"
                " shows what happens when the checker is run against the p-trad strands.",
            )
        ),
        H.para(
            (
                "There is no dual cantillation to detangle here. Whereas the Tiberian manuscripts (and WLC)"
                " pack both of their strands onto one set of letters, the Wikisource page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                " spells out all the strands separately — p-trad and m-trad alike —"
                " each as single cantillation. Every chanted verse"
                " (delimited by its own ",
                _ROM_SOF_PASUQ,
                ") is grammar-checked on its own. The"
                " m-trad is the baseline — MAM's own authoritative text, expected"
                " to parse clean throughout — and the p-trad is the object of study.",
            )
        ),
    )


def _cell(vr: pd.VersionResult) -> object:
    n = len(vr.chanted_verses)
    bad = vr.ungrammatical
    if not bad:
        return H.table_datum(f"✓ all {n} clean", {"class": "clean"})
    which = ", ".join(f"verse {cv.index}" for cv in bad)
    return H.table_datum(
        f"✗ {len(bad)} of {n} ungrammatical ({which})", {"class": "ungrammatical"}
    )


# The traditional strand name for each reading (report labels only). No "upper"/"lower" gloss:
# it invites confusion with above-letter vs below-letter accents (see printed_decalogue_strands
# module docstring for the cross-page rule).
_STRAND_LABELS: dict[str, str] = {
    "sk-taxton": "תחתון",
    "sk-elyon": "עליון",
}  # sk: strand key
_BOOK_LABELS: dict[str, str] = {"bk-ex": "Ex.", "bk-dt": "Deut."}  # bk: book key


def _verdict_table(by_key: dict) -> object:
    header = H.table_row_of_headers(("", "m-trad verses", "p-trad verses"))
    rows = [header]
    for book in ("bk-ex", "bk-dt"):
        for strand in ("sk-taxton", "sk-elyon"):
            label = f"{_BOOK_LABELS[book]} {_STRAND_LABELS[strand]}"
            rows.append(
                H.table_row(
                    (
                        H.table_header(label),
                        _cell(by_key[(book, strand, "tk-manuscript")]),
                        _cell(by_key[(book, strand, "tk-printed")]),
                    )
                )
            )
    return H.table(tuple(rows), {"class": "printed-decalogue-verdict"})


def _verdict_section(by_key: dict) -> tuple[object, ...]:
    return (
        H.heading_level_2("The verdict"),
        _verdict_table(by_key),
        H.para(
            (
                f"The {_TAHTON}"
                f" is grammatical everywhere — both books, both traditions. In terms of verse"
                f" boundaries, the p-trad {_TAHTON} differs from the m-trad in only one place: the "
                f"p-trad {_TAHTON} ends its first verse at מבית עבדים (so it has one more verse "
                "than the m-trad, whose first verse runs on to על־פני instead). Both "
                "parse clean. It also differs in some further details — several of them "
                "changes of cantillation that give the two strands genuinely different parses, "
                "but none that costs either its grammaticality (",
                link("catalogued in an appendix below", f"#{_TAHTON_DETAILS_ID}"),
                ").",
            )
        ),
        H.para(
            (
                f"The {_ELYON}" " is grammatical in the m-trad but ",
                H.bold("not"),
                f" in the p-trad: the p-trad {_ELYON} of ",
                H.bold("each"),
                " Decalogue has exactly one ungrammatical chanted verse — its opening one.",
            )
        ),
    )


# --------------------------------------------------------------------------- #
# Word stripping and the shared range cell
# --------------------------------------------------------------------------- #
def _strip_pointing(word: str) -> str:
    """Reduce a pointed Hebrew word to consonants + cantillation accents + accent-coupled
    punctuation (maqaf, sof pasuq, legarmeh), dropping vowels, dagesh, shin/sin dots, rafe,
    and ordinary meteg. A word's U+05BD is *silluq* (an accent, kept) exactly when the word is
    verse-final, i.e. carries sof pasuq; otherwise every U+05BD is an ordinary meteg (a ga'ya)
    and is dropped. Done with the shared mb_cmn.hebrew_accent_strip kernel (cf. MAM-basics
    ``versification_and_cantillation/strands.py::_strip_pointing``)."""
    keep_meteg = has.METEG_SILLUQ if hpunc.SOPA in word else has.METEG_DROP
    return has.strip_to_accents(word, keep_meteg=keep_meteg)


# The `title` text here is an ATTRIBUTE context, so it keeps the romanized "taxton"/"elyon" even
# though the visible prose names the strands in Hebrew letters. That asymmetry is deliberate and
# settled -- see the "Attribute contexts are EXEMPT" bullet in printed_decalogue_strands' module
# docstring before "correcting" any title/alt string on this page or its two satellites.
def _abbr(letter: str, title: str) -> object:
    return H.htel_mk_inline("abbr", {"title": title}, letter)


# ── Letter-equalizing the paired taxton/elyon boundary cells (ported from MAM-basics #201) ──
# Each column shows one underlying text span read by both strands, so the two cells should share
# a consonant skeleton at each boundary. They can still tokenize a boundary word differently —
# most visibly the leading לא of a negative commandment, which the taxton maqaf-joins to the next
# word (one token לא־תעשה) while the elyon leaves it free (לא as its own word). _balanced_sides
# pulls extra boundary words inward, word by word, until the two sides' skeletons match, so the
# sibling cells align (e.g. taxton לא־תעשה לך … / elyon לא תעשה־לך …) instead of a bare לא sitting
# under a fuller taxton cell. It asserts equality — a guard that fires loudly on any column it
# cannot reconcile.
def _skel(word: str) -> str:
    """A word's consonant skeleton: only the Hebrew letters (alef…tav), dropping points, accents,
    maqaf, sof pasuq and legarmeh — so a maqaf-joined לא־תעשה and a space-separated לא תעשה compare
    equal. Uses the same letter bounds as the strip kernel (private today; cf. MAM-basics #198).
    """
    return "".join(ch for ch in word if has._LETTER_LO <= ord(ch) <= has._LETTER_HI)


def _balance_boundary(
    t_words, e_words, *, grow_backward: bool, label: str
) -> tuple[int, int]:
    """How many boundary words each strand must show for their skeletons to match at one end of a
    column. Compares the taxton's and elyon's leading (or, with ``grow_backward``, trailing) run
    of words, growing the shorter-skeleton side inward one word at a time while it stays a prefix/
    suffix of the longer. Raises with the column ``label`` if the skeletons diverge or a side runs
    out of words."""

    def seg(words, take):
        chosen = words[-take:] if grow_backward else words[:take]
        return "".join(_skel(w) for w in chosen)

    t_take = e_take = 1
    while True:
        ts, es = seg(t_words, t_take), seg(e_words, e_take)
        if ts == es:
            return t_take, e_take
        short, long_ = (ts, es) if len(ts) < len(es) else (es, ts)
        aligned = long_.endswith(short) if grow_backward else long_.startswith(short)
        grow_t = len(ts) < len(es)
        room = (t_take < len(t_words)) if grow_t else (e_take < len(e_words))
        if not aligned or not room:
            raise AssertionError(
                f"cannot letter-equalize the {label} boundary — taxton skeleton {ts!r} vs "
                f"elyon skeleton {es!r}; taxton words={t_words!r}, elyon words={e_words!r}"
            )
        if grow_t:
            t_take += 1
        else:
            e_take += 1


def _balanced_sides(t_words, e_words, *, label: str):
    """Letter-balance both ends of a column, returning the displayed boundary word lists
    ``(t_first, t_last, e_first, e_last)`` — each the word(s) whose skeletons the two strands
    share after any pulling."""
    tf, ef = _balance_boundary(
        t_words, e_words, grow_backward=False, label=f"{label} first"
    )
    tl, el = _balance_boundary(
        t_words, e_words, grow_backward=True, label=f"{label} last"
    )
    return t_words[:tf], t_words[-tl:], e_words[:ef], e_words[-el:]


def _range_cell(first_words, last_words, *, start: bool, stop: bool) -> object:
    """A ``first … last`` range cell: the (already letter-balanced) boundary word(s) at each end,
    stripped to consonants + accents and joined by an ellipsis. The verse-initial word is green
    when ``start`` and the verse-final word red when ``stop``; any word pulled in only for
    letter-alignment renders plain. ``lang="hbo"`` → Taamey font (issue #58)."""
    fw = [_strip_pointing(w) for w in first_words]
    lw = [_strip_pointing(w) for w in last_words]
    fw[0] = H.span_c(fw[0], "vc-start") if start else fw[0]
    lw[-1] = H.span_c(lw[-1], "vc-stop") if stop else lw[-1]
    # fw words (space-separated), then the ellipsis, then lw words (space-separated).
    nodes: list[object] = []
    for i, node in enumerate(fw):
        if i:
            nodes.append(" ")
        nodes.append(node)
    nodes.append("…")
    for i, node in enumerate(lw):
        if i:
            nodes.append(" ")
        nodes.append(node)
    return H.table_datum(tuple(nodes), {"lang": "hbo"})


# --------------------------------------------------------------------------- #
# The four-strands table (issue #52)
# --------------------------------------------------------------------------- #
# Two-char row-header abbreviations for the four strands, coherent with the merged table's
# single E/T letters below; the dotted-underline title spells each out (the romanized form is
# fine in an attribute). m/p = m-trad/p-trad, T/E = taxton/elyon strand. The titles
# say NO "upper"/"lower" -- that gloss invites confusion with above-letter vs below-letter accents
# (see printed_decalogue_strands module docstring; same rule on both printed-Decalogue pages).
_STRAND_ABBRS: dict[str, tuple[str, str]] = {
    "m-trad taḥton": ("mT", "manuscript-tradition taḥton"),
    "m-trad elyon": ("mE", "manuscript-tradition elyon"),
    "p-trad taḥton": ("pT", "printed-tradition taḥton"),
    "p-trad elyon": ("pE", "printed-tradition elyon"),
}

# m-trad elyon and p-trad taxton accent אנכי…עבדים identically (tipexa on אנכי, silluq on עבדים)
# and give it the same first chanted verse, so the two collapse into a single "mE/pT" row rather
# than two rows sharing a rowspan.
_MERGED_STRANDS = ("m-trad elyon", "p-trad taḥton")

# The opening unit's four positional milestones, in verse order (rtl: אנכי rightmost →
# מצותי leftmost). Every strand starts at אנכי (their common point) and ends at one of the later
# three; the strands nest — m-trad elyon / p-trad taxton stop at עבדים, m-trad taxton at על־פני,
# p-trad elyon at מצותי — so laying them over these shared columns shows that subset relation and
# their common start at a glance (schematic: only the ORDER of the endpoints is shown, not the
# real word-distances between them). Skeletons are consonants-only (base_skeleton form), matching
# each reading's pds.STRUCTURE end_skel so an endpoint's column is derived, never hard-assigned.
_MILESTONES: tuple[str, ...] = ("אנכי", "עבדים", "עלפני", "מצותי")


def _word_at(r: pds.Reading, skeleton: str) -> str:
    """The strand's own pointed word at a milestone, matched by consonantal skeleton within its
    first chanted verse. Each strand keeps ITS OWN accent on a shared milestone (e.g. עבדים is
    etnaḥta / silluq / revia across strands), which is the structure-deciding signal, so the cell
    must show the per-strand form rather than one canonical word per column."""
    for word in r.first_verse_words:
        if pds.base_skeleton(word) == skeleton:
            return word
    raise AssertionError(
        f"{r.name}: no word with skeleton {skeleton!r} in its first chanted verse "
        "-- the vendored readings drifted"
    )


def _milestone_cells(r: pds.Reading) -> list[object]:
    """One strand's row of milestone cells over the shared _MILESTONES columns: its start word
    (אנכי) green, its endpoint word red, any interior milestones neutral, and every milestone
    LATER than its endpoint an empty cell — so a shorter verse visibly stops where the longer
    ones keep going, making the subset relation and common start legible down the columns.
    """
    end = _MILESTONES.index(r.first_verse_end)
    cells: list[object] = []
    for i, skel in enumerate(_MILESTONES):
        if i > end:
            cells.append(
                H.table_datum("", {"lang": "hbo"})
            )  # verse ends before this milestone
            continue
        cls = "vc-start" if i == 0 else "vc-stop" if i == end else "vc-mid"
        span = H.span_c(_strip_pointing(_word_at(r, skel)), cls)
        cells.append(H.table_datum((span,), {"lang": "hbo"}))
    return cells


def _assert_merged_identical(r: pds.Reading, other: pds.Reading) -> None:
    """The two merged strands share ONE row (label "mE/pT"), so they must read identically.
    Compare the STRIPPED forms at each shared milestone, not the full words: their full אנכי /
    עבדים differ only by an immaterial meteg, which _strip_pointing correctly drops. Do NOT "fix"
    this to full-word equality — it would fire on that immaterial meteg. Same
    fail-the-build-on-data-drift style as resolve_readings."""
    for skel in _MILESTONES[: _MILESTONES.index(r.first_verse_end) + 1]:
        if _strip_pointing(_word_at(r, skel)) != _strip_pointing(_word_at(other, skel)):
            raise AssertionError(
                f"{r.name} and {other.name} share one row, but their stripped "
                f"{skel} forms differ -- the vendored readings drifted"
            )


def _merged_header() -> object:
    """The single row header for the two identically-opening strands: visible "mE/pT", its title
    stating the identity (both halves already free of any upper/lower gloss). The shared
    "(cantillation strand)" parenthetical is factored out to the end rather than repeated.
    """
    la, ta = _STRAND_ABBRS[_MERGED_STRANDS[0]]
    lb, tb = _STRAND_ABBRS[_MERGED_STRANDS[1]]
    title = f"{ta} = {tb} (same in the first chanted verse only)"
    return H.table_header(_abbr(f"{la}/{lb}", title))


def _four_strands_table(readings: list[pds.Reading]) -> object:
    by_name = {r.name: r for r in readings}
    rows: list[object] = []
    for r in readings:
        if r.name == _MERGED_STRANDS[1]:
            continue  # folded into the single mE/pT row emitted at _MERGED_STRANDS[0]
        if r.name == _MERGED_STRANDS[0]:
            _assert_merged_identical(r, by_name[_MERGED_STRANDS[1]])
            header = _merged_header()
        else:
            letter, title = _STRAND_ABBRS[r.name]
            header = H.table_header(_abbr(letter, title))
        rows.append(H.table_row((header, *_milestone_cells(r))))
    return H.table(tuple(rows), {"class": "strand-table", "dir": "rtl"})


_UL_ITEM_1 = (
    H.bold(f"P-trad {_TAHTON} = m-trad {_ELYON} — but only in the first chanted verse"),
    ", where the table gives them a single shared row, labelled mE/pT."
    " The equality stops there: past this first"
    " verse the two strands diverge — the p-trad ",
    *[f"{_TAHTON} divides each Decalogue into ", H.bold("13")],
    *[f" chanted verses, the m-trad {_ELYON} into only ", H.bold("10"), "."],
)

_UL_ITEM_2 = (
    H.bold(f"P-trad {_ELYON} ≠ m-trad {_ELYON}."),
    f" The p-trad {_ELYON} puts ",
    H.bold(_ROM_REVIA),
    " on עבדים and runs the first two commandments together into one verse,"
    " leading to only ",
    H.bold("9"),
    " chanted verses total. In contrast, the first chanted verse of the m-trad's"
    f" {_ELYON} ends on עבדים, leading to ",
    H.bold("10"),
    " chanted verses total.",
)

_UL_ITEM_3 = (
    f"The m-trad {_TAHTON} does not give אנכי…עבדים its own verse either — it"
    " runs אנכי…פני together (",
    _ROM_ETNAHTA,
    " at עבדים, ",
    _ROM_SOF_PASUQ,
    " at פני), a third structure again.",
)


def _four_strands_section(readings: list[pds.Reading]) -> tuple[object, ...]:
    return (
        H.heading_level_2("The four strands of אנכי…עבדים", {"id": "four-strands"}),
        H.para(
            (
                "The m-trad and p-trad accent the Decalogue's אנכי…עבדים unit differently."
                " The accent on עבדים is what decides the structure: a ",
                H.bold(_ROM_SILLUQ_SOF_PASUQ),
                " there ends the verse, so אנכי…עבדים stands as its own verse; an ",
                H.bold(_ROM_ETNAHTA),
                " or ",
                H.bold(_ROM_REVIA),
                " there is mid-verse, folding אנכי…עבדים into a longer verse. The table below "
                "lays all four strands over the same milestone words — ",
                H.bdi("אנכי"),
                " (their common start), then ",
                # bdi_multi isolates each RTL item so the LTR list order survives however a viewer
                # resolves the bidirectional text (else the items merge across the commas).
                *H.bdi_multi(
                    "עבדים",
                    "על־פני",
                    "מצותי",
                ),
                " — so their subset relation is plain: every "
                "verse starts green at אנכי and ends red at its own last word, the shorter ones "
                "stopping where the longer ones keep going. Each strand keeps its own accent on "
                "עבדים, the structure-deciding mark:",
            )
        ),
        _four_strands_table(readings),
        H.unordered_list(
            (
                _UL_ITEM_1,
                _UL_ITEM_2,
                _UL_ITEM_3,
            )
        ),
        H.para(
            (
                f"Of these four strands, only the p-trad {_ELYON} is ungrammatical — the "
                "verdict above already said so — and the ",
                link("section below", "#why-the-printed-elyon-fails"),
                " dissects its merged opening verse.",
            )
        ),
    )


# --------------------------------------------------------------------------- #
# The nesting tables (issues #59, #62)
# --------------------------------------------------------------------------- #
# Two transposed strand tables over the SAME opening region (commandments 1-2, the 51 words
# אנכי...מצותי): one for the printed tradition (pE/pT), one for the manuscript tradition (mE/mT),
# so the reader can compare how each tradition's elyon and taxton verses nest. The layout echoes
# the table in MAM-simple/gh-pages/versification-and-cantillation.html (the source of the analogy,
# not of the text), but with no M/B verse-number rows. Each cell is a first…last range (consonants
# + accents; vowels/dagesh/ordinary-meteg stripped), green where a column begins one of the
# strand's verses and red where it ends one. The columns are the finest common subdivision: the
# union of both strands' verse boundaries. Because the p-trad taxton breaks at every boundary
# either m-trad strand uses, BOTH tables end up with the same five columns (widths 9,5,14,17,6);
# what differs is which column edges are true verse starts/stops. Where a verse straddles a column
# edge of the other strand (the m-trad taxton's אנכי...על־פני crossing the elyon's break after
# עבדים) the cell shows a start with no matching stop, or vice versa — the "straddling" that makes
# the m-trad nesting less tidy than the p-trad's clean five-in-one. (M/B numbering is dropped because the two traditions
# split this region differently, so no single verse-number row aligns with the columns; issue #59.)


def _leading_verses(
    version: pd.VersionResult, n_words: int
) -> list[pd.ChantedVerseResult]:
    """The leading chanted verses of ``version`` whose words together cover the first ``n_words``
    (the opening region). The strands are the same word sequence, differing only in vocalization/
    accents, so this splits the shared region consistently for each strand."""
    out: list[pd.ChantedVerseResult] = []
    total = 0
    for cv in version.chanted_verses:
        out.append(cv)
        total += len(cv.words)
        if total >= n_words:
            break
    return out


def _verse_ends(verses: list[pd.ChantedVerseResult]) -> list[int]:
    """The cumulative word-offset at which each verse ends, e.g. ``[9, 51]`` for a 9- then
    42-word pair."""
    ends: list[int] = []
    total = 0
    for v in verses:
        total += len(v.words)
        ends.append(total)
    return ends


def _columns(*verse_lists: list[pd.ChantedVerseResult]) -> list[tuple[int, int]]:
    """Column ``(start, end)`` word-offsets = the segments delimited by the union of every
    strand's verse boundaries, so within a column no strand breaks."""
    cuts = sorted({0, *(e for verses in verse_lists for e in _verse_ends(verses))})
    return list(zip(cuts, cuts[1:]))


def _labeled_row(letter: str, title: str, cells: list[object]) -> object:
    return H.table_row((H.table_header(_abbr(letter, title)), *cells))


def _grad_row(
    letter: str,
    title: str,
    verses: list[pd.ChantedVerseResult],
    columns: list[tuple[int, int]],
) -> object:
    """A strand's schematic gradient bar: one cell per verse, colspanned across the columns that
    verse covers (a verse spanning k columns is one k-wide green→red bar)."""
    ends = _verse_ends(verses)
    spans = list(zip([0, *ends[:-1]], ends))
    cells = []
    for vs, ve in spans:
        k = sum(1 for a, b in columns if vs <= a and b <= ve)
        attr = {"class": "vc-grad", **({"colspan": str(k)} if k > 1 else {})}
        cells.append(H.table_datum("", attr))
    return H.table_row((H.table_header(_abbr(letter, title)), *cells))


def _nesting_table(
    elyon: pd.VersionResult, taxton: pd.VersionResult, n_words: int, *, pfx: str
) -> object:
    """The transposed strand table for one tradition over the opening ``n_words``-word region.
    ``pfx`` ("p" / "m") prefixes the row labels — pE/pT and the gradient rows pe/pt (mE/mT, me/mt) —
    matching the four-strands table's mT/pE convention. Both traditions land on the same columns.
    """
    trad = {"p": "printed", "m": "manuscript"}[pfx]
    e_verses = _leading_verses(elyon, n_words)
    t_verses = _leading_verses(taxton, n_words)
    e_words = tuple(w for cv in e_verses for w in cv.words)
    t_words = tuple(w for cv in t_verses for w in cv.words)
    columns = _columns(e_verses, t_verses)
    e_ends, t_ends = _verse_ends(e_verses), _verse_ends(t_verses)
    e_starts, e_stops = {0, *e_ends[:-1]}, set(e_ends)
    t_starts, t_stops = {0, *t_ends[:-1]}, set(t_ends)
    # Build the two text rows together, column by column: each column's elyon and taxton slices
    # are letter-balanced against each other (issue #201) before rendering, so sibling cells align.
    e_cells: list[object] = []
    t_cells: list[object] = []
    for a, b in columns:
        t_first, t_last, e_first, e_last = _balanced_sides(
            t_words[a:b], e_words[a:b], label=f"{pfx} {a}:{b}"
        )
        e_cells.append(
            _range_cell(e_first, e_last, start=a in e_starts, stop=b in e_stops)
        )
        t_cells.append(
            _range_cell(t_first, t_last, start=a in t_starts, stop=b in t_stops)
        )
    rows = (
        _labeled_row(pfx + "E", f"{trad}-tradition elyon", e_cells),
        _labeled_row(pfx + "T", f"{trad}-tradition taḥton", t_cells),
        _grad_row(
            pfx + "e",
            f"schematic color gradient for the {trad} elyon verse(s)",
            e_verses,
            columns,
        ),
        _grad_row(
            pfx + "t",
            f"schematic color gradient for the {trad} taḥton verse(s)",
            t_verses,
            columns,
        ),
    )
    return H.table(rows, {"class": "strand-table", "dir": "rtl"})


def _finding_section(by_key: dict) -> tuple[object, ...]:
    ex_ms = by_key[("bk-ex", "sk-elyon", "tk-manuscript")]
    ms_cmd1, ms_cmd2 = ex_ms.chanted_verses[0], ex_ms.chanted_verses[1]
    merged = by_key[("bk-ex", "sk-elyon", "tk-printed")].ungrammatical[0]
    n_words = len(merged.words)
    p_table = _nesting_table(
        by_key[("bk-ex", "sk-elyon", "tk-printed")],
        by_key[("bk-ex", "sk-taxton", "tk-printed")],
        n_words,
        pfx="p",
    )
    m_table = _nesting_table(
        ex_ms,
        by_key[("bk-ex", "sk-taxton", "tk-manuscript")],
        n_words,
        pfx="m",
    )
    return (
        H.heading_level_2(
            f"Why the p-trad {_ELYON} fails: the merged first verse",
            {"id": "why-the-printed-elyon-fails"},
        ),
        H.para(
            (
                "As the ",
                link("four-strands table above", "#four-strands"),
                f" laid out, in the m-trad {_ELYON} the first commandment אנכי…עבדים is its "
                "own chanted verse, and לא יהיה לך אלהים אחרים begins the next — two "
                "separate verses, ",
                H.bold("both of which parse clean"),
                ". The p-trad instead merges the first two commandments into a single "
                "verse. That one "
                "merged verse is what the grammar rejects. Shown stripped to consonants and "
                f"accents and divided at the p-trad {_TAHTON}'s verse boundaries — one p-trad "
                f"{_ELYON} verse (pE) spanning the five ordinary p-trad {_TAHTON} verses (pT) "
                "it merges:",
            )
        ),
        p_table,
        H.para(
            (
                "The single ",
                _ROM_ETNAHTA,
                " falls at לשנאי, leaving a first half crowded with a ",
                _ROM_SEGOLTA,
                " plus three separate ",
                _ROM_REVIA,
                " domains (at ",
                *H.bdi_multi("עבדים", "על־פני", "לארץ"),
                "); the prose grammar cannot build it and returns a ",
                H.code("pashta_phrase"),
                " error — the same failure, at the same structural point, in both Decalogues.",
            )
        ),
        H.para(
            (
                "The cause is the merged ",
                H.bold("structure"),
                f", not sheer length: Deuteronomy's p-trad {_ELYON} Sabbath verse runs 55 "
                "words and parses clean, while this merged verse (51 words) does not. Keeping "
                "the two commandments as the m-trad's two separate verses (",
                f"{len(ms_cmd1.words)} and {len(ms_cmd2.words)} words) ",
                "is exactly what lets them parse.",
            )
        ),
        H.heading_level_3("A tidier nesting — until you scrutinize it"),
        H.para(
            (
                f"It is tempting to call the p-trad's arrangement the neater one. Its five "
                f"{_TAHTON} verses nest perfectly inside a single {_ELYON} verse — a clean "
                "five-in-one — whereas the m-trad divides the very same words into ",
                H.bold("two"),
                f" {_ELYON} verses and ",
                H.bold("four"),
                f" {_TAHTON} verses that do not nest cleanly at all: the m-trad ",
                f"{_TAHTON}'s opening verse אנכי…על־פני straddles the {_ELYON}'s break "
                f"after עבדים, so neither strand's verses sit wholly inside the other's. In "
                "the gradient "
                "bars below, mE's first break lands inside mT's first verse, which runs on to "
                "על־פני — that is the straddle:",
            )
        ),
        m_table,
        H.para(
            (
                "But the p-trad's tidiness is bought with an ungrammatical cantillation — the "
                "very one dissected above. Once you see the accents that buy the five-in-one, "
                "its neatness evaporates. This is ",
                H.bold("not"),
                " to say the tidier nesting could not have been cantillated grammatically; "
                "perhaps some other accentuation would have carried it off. That is a "
                "theoretical question I am not prepared to settle here.",
            )
        ),
    )


def _provenance_section(source: dict) -> tuple[object, ...]:
    prov = source.get("provenance", {})
    oldid = prov.get("oldid")
    ts = prov.get("revision_timestamp", "")
    return (
        H.heading_level_2("Source"),
        H.para(
            (
                f"All eight strands (two books × {_TAHTON}/{_ELYON} × m-trad/p-trad) are "
                "taken from the Wikisource base page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                f" (revision {oldid}, {ts[:10]}), which every p-trad-vs-m-trad comparison "
                "table there transcludes. A handful of wiki templates are resolved to plain "
                "pointed text (",
                _ROM_LEGARMEH,
                "/",
                _ROM_PASEQ,
                " to a ",
                _ROM_PASEQ,
                " mark, qere for ketiv-qere, paragraph and pisqa markers dropped); the chanted "
                "verses are split at ",
                _ROM_SOF_PASUQ,
                ".",
            )
        ),
        H.para(
            (
                "See also ",
                link(
                    "Simanim's Tiqqun as an independent witness",
                    "printed-decalogue-simanim.html",
                ),
                f": two notes from Simanim's Tiqqun — its main text uses the p-trad {_ELYON} "
                "and its appendix the p-trad "
                f"{_TAHTON}. That page links to this page's ",
                link("four-strands table", "#four-strands"),
                " rather than repeating it.",
            )
        ),
        H.para(
            (
                "See also the ",
                link("Koren Tanakh", "printed-decalogue-koren.html"),
                f" as a second independent witness: it prints the p-trad {_TAHTON} in its "
                f"Exodus running text and the p-trad {_ELYON} in an appendix, with a note "
                "(citing רוו״ה) flagging the standalone-verse alternative it declines to "
                "print. That page, too, links to this page's ",
                link("four-strands table", "#four-strands"),
                " rather than repeating it.",
            )
        ),
    )


# --------------------------------------------------------------------------- #
# Appendix: the grammaticality-irrelevant תחתון differences
# --------------------------------------------------------------------------- #
# Spun out of the verdict paragraph's parenthetical (which now just links here): a plain-prose
# catalogue of how the p-trad and m-trad תחתון differ WITHOUT touching grammaticality (several DO
# change the parse tree — e.g. a disjunctive-rank accent swap — but leave both strands well-formed).
# Both strands parse clean everywhere, so none of this bears on the page's question; it is here only
# to substantiate the verdict's point that these differences never cost either strand its
# grammaticality. The prose is hand-written documentary colour, not part of the live grammaticality
# result; but the Hebrew it displays for the Deuteronomy differences — where the תחתון cantillation
# differences cluster, in the Sabbath commandment — is pulled live from the data and reduced, again
# live, to just the stretch the two strands accent differently (_sabbath_diff_table), so it can't
# drift from the text the page grammar-checks. The verse-boundary difference (p-trad first verse
# ending at מבית עבדים) and the boundary accents it drags along are the verdict's own point and are
# deliberately NOT repeated here.

# The prose books' conjunctive accents (Yeivin ITM §194, encoded once in mb_cmn.hebrew_accents);
# every other cantillation accent is disjunctive. Used only to verify, live, that each displayed
# line really does end on a disjunctive.
_PROSE_CONJUNCTIVES = set(ha.CONJUNCTIVES_BCC["cant-sys-prose"])
_ACCENT_LO = ord("\N{HEBREW ACCENT ETNAHTA}")  # U+0591, first cantillation accent
_ACCENT_HI = ord("\N{HEBREW ACCENT ZINOR}")  # U+05AE, last (meteg U+05BD is excluded)

# The three shared boundaries at which the differing stretch is broken into aligned line-pairs.
# Each is a consonantal skeleton (cf. _MILESTONES) that ends a line in BOTH strands and carries a
# disjunctive accent in both — the only kind of point where a break keeps the m-trad and p-trad
# lines aligned. These three (of the stretch's shared disjunctive boundaries) give three ~even
# pairs. _split_into_lines asserts each lands, in order, and is genuinely disjunctive, so any drift
# in the vendored accents fails the build instead of silently mis-breaking.
_SABBATH_LINE_ENDS: tuple[str, ...] = ("כלמלאכה", "ועבדךואמתך", "וכלבהמתך")


def _ends_on_disjunctive(word: str) -> bool:
    """True if a pointed prose word's cantillation accent is disjunctive: it bears an accent in the
    U+0591..U+05AE block that is not one of the prose conjunctives (Yeivin ITM §194)."""
    return any(
        _ACCENT_LO <= ord(ch) <= _ACCENT_HI and ch not in _PROSE_CONJUNCTIVES
        for ch in word
    )


def _dt_taxton_sabbath_words(
    results: list[pd.VersionResult], tradition: str
) -> list[str]:
    """The words of the Deuteronomy תחתון Sabbath chanted verse (``tradition`` = "manuscript" /
    "printed"), pulled live from the vendored data — the one chanted verse whose words include the
    skeleton בהמתך. Asserts exactly one match so a data change that moved or renumbered the verse
    fails the build rather than silently mis-rendering."""
    by_key = {(vr.book, vr.reading, vr.tradition): vr for vr in results}
    vr = by_key[("dt", "taxton", tradition)]
    sabbath = [
        cv
        for cv in vr.chanted_verses
        if any("בהמתך" in pds.base_skeleton(w) for w in cv.words)
    ]
    if len(sabbath) != 1:
        raise AssertionError(
            f"dt taxton {tradition}: expected exactly 1 Sabbath verse (skeleton בהמתך), "
            f"found {len(sabbath)} -- the vendored readings drifted"
        )
    return sabbath[0].words


def _differing_span(
    m_words: list[str], p_words: list[str]
) -> tuple[list[str], list[str]]:
    """The (m, p) sub-lists bracketing every difference between the two strands: the shared,
    byte-identical prefix and suffix are stripped, leaving the contiguous stretch where the strands
    differ. (They share a consonantal text, so any difference is an accent or a maqaf/paseq mark;
    the identical head and tail are common context we omit.)"""
    head = 0
    while head < min(len(m_words), len(p_words)) and m_words[head] == p_words[head]:
        head += 1
    tail = 0
    while (
        tail < min(len(m_words), len(p_words)) - head
        and m_words[-1 - tail] == p_words[-1 - tail]
    ):
        tail += 1
    return m_words[head : len(m_words) - tail], p_words[head : len(p_words) - tail]


def _split_into_lines(words: list[str], line_ends: tuple[str, ...]) -> list[list[str]]:
    """Split ``words`` into the successive line groups ending at each skeleton in ``line_ends``.
    Asserts every break lands, in order, consumes the whole stretch, and ends on a word that really
    carries a disjunctive accent — so any drift in the vendored words/accents fails the build.
    """
    lines: list[list[str]] = []
    cur: list[str] = []
    pending = list(line_ends)
    for w in words:
        cur.append(w)
        if pending and pds.base_skeleton(w) == pending[0]:
            if not _ends_on_disjunctive(w):
                raise AssertionError(
                    f"line-end {w!r} no longer carries a disjunctive accent -- readings drifted"
                )
            lines.append(cur)
            cur, pending = [], pending[1:]
    if cur or pending:
        raise AssertionError(
            f"sabbath line split: leftover words {cur!r} / unconsumed line-ends {pending!r} "
            "-- the vendored readings drifted"
        )
    return lines


def _diff_row(label: str, words: list[str]) -> object:
    """One table row: a bold m-trad/p-trad label cell, then the strand's line of words as a
    right-aligned (dir=rtl) hbo cell so the three pairs' Hebrew all line up flush-right. Each word
    is shown in the classic consonants-plus-accents form (_strip_pointing: vowels, dagesh, and
    mid-verse meteg dropped), so only the cantillation differences remain -- the vowel-pointing
    differences are catalogued separately in the bullets below."""
    line = " ".join(_strip_pointing(w) for w in words)
    return H.table_row(
        (
            H.table_datum(H.bold(label)),
            H.table_datum(hbo(line), {"dir": "rtl"}),
        )
    )


def _sabbath_diff_table(results: list[pd.VersionResult]) -> object:
    """The differing stretch of the two Deuteronomy תחתון Sabbath strands, as a table of three
    line-pairs (an m-trad row directly above its p-trad row), each line a short run of words ending
    on a shared disjunctive; the head and tail the two strands share verbatim are omitted. The table
    picks up the shared centered layout and the lang="hbo" font; its lone class turns OFF the shared
    odd-row zebra, which -- the rows alternating m-trad/p-trad -- tinted exactly the three m-trad
    rows and so read as if the stripe meant "m-trad" (issue #65, finding C3). Span, breaks, and the
    disjunctive check are all derived live from the data, so nothing here can drift from the
    grammar-checked text."""
    m_span, p_span = _differing_span(
        _dt_taxton_sabbath_words(results, "manuscript"),
        _dt_taxton_sabbath_words(results, "printed"),
    )
    m_lines = _split_into_lines(m_span, _SABBATH_LINE_ENDS)
    p_lines = _split_into_lines(p_span, _SABBATH_LINE_ENDS)
    rows: list[object] = []
    for m_line, p_line in zip(m_lines, p_lines):
        rows.append(_diff_row("m-trad", m_line))
        rows.append(_diff_row("p-trad", p_line))
    return H.table(tuple(rows), {"class": "printed-decalogue-sabbath-diff"})


def _appendix_section(results: list[pd.VersionResult]) -> tuple[object, ...]:
    return (
        H.heading_level_2(
            f"Appendix: how the two {_TAHTON} strands differ",
            {"id": _TAHTON_DETAILS_ID},
        ),
        H.para(
            (
                f"Both {_TAHTON} strands parse clean everywhere, so none of the differences below "
                "bears on the grammaticality question this page asks — not even the several that "
                "do change the parse. They are gathered here only to make concrete the verdict's "
                "point that the strands differ in ways that never cost either its grammaticality. "
                "The one structural difference — the p-trad ending its first verse at מבית עבדים, "
                "and the boundary accents on ",
                *H.bdi_multi(
                    "אנכי",
                    "אלהיך",
                    "מבית",
                    "עבדים",
                ),
                " that follow from it — is the verdict's own point and is not repeated here.",
            )
        ),
        H.para(
            (
                "In Exodus the two strands differ in essentially one grammar-irrelevant respect: "
                "the vocalization of לא תרצח — ",
                hbo("תִּרְצָ֖ח"),
                " (m-trad, qamats) against ",
                hbo("תִּרְצַ֖ח"),
                " (p-trad, patax). Both have the same ",
                _ROM_TIPEHA,
                "; only the vowel differs.",
            )
        ),
        H.para(
            (
                "Deuteronomy differs in more ways. Three are differences of cantillation — "
                "which, unlike the Exodus vowel-swap, do change the parse — and all three fall "
                "within a single stretch "
                "of the Sabbath commandment. Below is just that stretch — the run of words the two "
                "strands accent differently, everything before and after it being identical — shown "
                "in each strand, m-trad above p-trad, stripped to consonants and accents (so the "
                "vowel-pointing differences noted below drop out and only the cantillation shows), "
                "each line ending on a disjunctive accent:",
            )
        ),
        # Just the differing stretch of the Sabbath verse, pulled and reduced live from the data (so
        # it can never drift from the accentuation the rest of the page grammar-checks), as a table
        # of three line-pairs, m-trad above p-trad, each line ending on a shared disjunctive.
        _sabbath_diff_table(results),
        H.para(
            (
                "Two further differences are purely vocalization — vowel-pointing, not "
                "cantillation:",
            )
        ),
        H.unordered_list(
            (
                (
                    # The verse is named in Hebrew (unpointed), not by an English gloss; bdi-wrap
                    # it so the bold RTL label sits cleanly at the head of the LTR list item.
                    H.bold((H.bdi(hbo("לא תרצח")), ".")),
                    # Each "X / Y" is two adjacent RTL words separated only by a neutral slash, so
                    # both are <bdi>-isolated (around the lang="hbo" span) to keep the pair from
                    # rendering reversed. Lone hbo forms elsewhere, bounded by English, need no bdi.
                    " The same ",
                    H.bdi(hbo("תִּרְצָ֖ח")),
                    " / ",
                    H.bdi(hbo("תִּרְצַ֖ח")),
                    " split as in Exodus.",
                ),
                (
                    H.bold("Qamats qatan vs. plain qamats."),
                    " Two words the m-trad points with qamats qatan but the p-trad with plain "
                    "qamats — ",
                    H.bdi(hbo("כׇל")),
                    " / ",
                    H.bdi(hbo("וְכׇל")),
                    " against ",
                    H.bdi(hbo("כָל")),
                    " / ",
                    H.bdi(hbo("וְכָל")),
                    ". This one is not a real m-trad/p-trad difference at all, but a defect "
                    "in the source: the p-trad supplies only the cantillation, and the "
                    f"vowel-pointing under it is Wikisource's own, so the p-trad {_TAHTON} "
                    "vendored here is simply mispointed in Deuteronomy — its own Exodus "
                    f"{_TAHTON} points the same words with qamats qatan. Reported as ",
                    link(
                        "MAM-basics issue #202",
                        "https://github.com/bdenckla/MAM-basics/issues/202",
                    ),
                    ".",
                ),
            )
        ),
        # An aside (issue #52 follow-up, corrected by issue #66): the p-trad תחתון Sabbath
        # cantillation dissected just above also turns up in CTR, the web edition my CTR review
        # judges the weirdest, and possibly worst, on the web. The aside exists for that quip.
        # Its "on the web" scoping is load-bearing, not incidental: it deliberately makes no claim
        # about which PRINT editions show the cantillation. Koren prints it too, in its own
        # Deuteronomy (issue #66); an earlier draft asserted a "gap in Koren and Simanim" that was
        # simply false for Koren. Keep any rewrite of the aside scoped to the web.
        *_chabad_witness(),
    )


# --------------------------------------------------------------------------- #
# The CTR aside: a p-trad Bible on the web (see the guardrail comment at the call site above)
# --------------------------------------------------------------------------- #
def _chabad_witness() -> tuple[object, ...]:
    return (
        H.heading_level_3("A p-trad Bible on the web: CTR"),
        H.para(
            (
                "Possibly the only p-trad Bible on the web is CTR:"
                " a web version of The Complete Tanach with Rashi."
                " (CTR is served from Chabad.org.)"
                f" CTR has not only the characteristic opening verse of the p-trad {_TAHTON}"
                f" but also the p-trad {_TAHTON} accents in the Sabbath commandment."
            )
        ),
        H.para(
            (
                *["For more on CTR: see my ", link("review", _CTR_REVIEW_URL), ","],
                " which calls it"
                " “certainly the weirdest Hebrew Bible on the web, and possibly the worst.”",
            )
        ),
    )


def render_body_contents(
    results: list[pd.VersionResult], source: dict
) -> tuple[object, ...]:
    by_key = _by_key(results)
    readings = pds.resolve_readings(results)
    return (
        *_intro(),
        *_verdict_section(by_key),
        *_four_strands_section(readings),
        *_finding_section(by_key),
        *_provenance_section(source),
        *_appendix_section(results),
    )


def run(args: argparse.Namespace) -> None:
    source = pd.load_source(args.source)
    results = pd.check_all(source)

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(results, source),
        write_ctx=H.WriteCtx(
            title=REPORT_TITLE,
            path=str(html_out),
            centered=True,
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    n_bad = sum(len(vr.ungrammatical) for vr in results)
    print(f"HTML: {html_out} ({len(results)} versions, {n_bad} ungrammatical)")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
