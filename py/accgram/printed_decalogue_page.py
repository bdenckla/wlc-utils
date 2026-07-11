r"""Generate gh-pages/accgram/printed-decalogue.html -- the printed-tradition Decalogue
grammaticality report (issue #52).

Companion to the dual-cantillation work of issue #36 (which grammar-checks the *manuscript*
taxton/elyon strands by detangling WLC): this page reports whether the *printed tradition*'s
(דפוסים) taxton and elyon accentuations of the two Decalogues parse under the same prose
grammar checker.  It renders live from ``printed_decalogue.check_all`` over the vendored
readings, so it can never drift from the checker's real behaviour.

It also lays out the four cantillation strands of the opening אנכי...עבדים unit (manuscript /
printed x taḥton / elyon) as a MAM-simple-style range table, resolved by the shared
``printed_decalogue_strands`` module.  The Simanim-witness companion page
(``printed_decalogue_simanim_page``) links back to that table rather than duplicating it.

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
from mb_cmn import hebrew_punctuation as hpunc
import wlc_provenance as provenance

from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "In the printed tradition, are the accents of the Decalogue grammatical?"

_GOERWITZ_URL = "goerwitz.html"
_SOURCE_URL = "https://he.wikisource.org/wiki/עשרת_הדברות_בסיס/טעמים"


# Strand names are single-sourced in printed_decalogue_strands (see its module docstring). These
# thin local aliases let the Hebrew strand words drop straight into the prose -- bare in a string
# or as {_TAHTON} / {_ELYON} inside an f-string -- rather than through a lang="he" <span> (issue
# #58), matching the Simanim companion page. Genuinely *pointed* Hebrew still goes through hbo()
# (lang="hbo" -> the Taamey pointed-text font); only bare consonantal terms are inlined this way.
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=pd.default_source_path())
    parser.add_argument("--html-out", type=Path, default=default_html_out_path(repo_root))


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _by_key(results: list[pd.VersionResult]) -> dict[tuple[str, str, str], pd.VersionResult]:
    return {(vr.book, vr.reading, vr.tradition): vr for vr in results}


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.heading_level_2("The question"),
        H.para(
            (
                "Each Decalogue — the one in ",
                H.bold("Exodus"),
                " and the one in ",
                H.bold("Deuteronomy"),
                " — has two strands of cantillation, the טעם תחתון and the טעם עליון; in truth"
                " there are ",
                H.bold("four"),
                ", because at the opening commandment the ",
                H.bold("printed tradition"),
                " (p-trad) differs from the ",
                H.bold("manuscript tradition"),
                f" (m-trad), yielding two different {_ELYON} strands and two different"
                f" {_TAHTON} strands. Richard Goerwitz's ",
                link("accent grammar checker", _GOERWITZ_URL),
                " vets the manuscript tradition's cantillation as grammatical prose; this page"
                " asks the companion question for the ",
                H.bold("printed tradition"),
                " (still visible in more traditional editions like Koren and Simanim): fed"
                f" through the same grammar checker, are its {_TAHTON} and {_ELYON}"
                " accentuations grammatical too?",
            )
        ),
        H.para(
            (
                "There is no dual cantillation to detangle here. Where the Tiberian manuscript"
                " packs both of its strands into one text, the Wikisource base page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                " spells out all the strands — printed and manuscript alike — separately and"
                " word-for-word, each as plain single cantillation. Every chanted verse"
                " (delimited by its own sof pasuq) is grammar-checked on its own. The"
                " manuscript tradition is the baseline — MAM's own authoritative text, expected"
                " to parse clean throughout — and the printed tradition is the object of study.",
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


def _verdict_table(by_key: dict) -> object:
    header = H.table_row_of_headers(("", "Manuscript tradition", "Printed tradition"))
    rows = [header]
    for book in ("ex", "dt"):
        for reading in ("taxton", "elyon"):
            label = f"{pd.BOOK_LABELS[book]} — {pd.READING_LABELS[reading]}"
            rows.append(
                H.table_row(
                    (
                        H.table_header(label),
                        _cell(by_key[(book, reading, "manuscript")]),
                        _cell(by_key[(book, reading, "printed")]),
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
                H.bold(_TAHTON),
                f" is grammatical everywhere — both books, both traditions. The printed {_TAHTON}"
                " differs from the manuscript only in details that do not touch the accent "
                "grammar (vocalization such as ",
                hbo("תִּרְצַח"),
                " vs ",
                hbo("תִּרְצָח"),
                " at לא תרצח, and where a maqaf or ga‘ya falls), and in one verse boundary: the "
                f"printed {_TAHTON} ends its first verse at מבית עבדים (so it has one more verse "
                "than the manuscript, which runs the first two commandments together). Both "
                "parse clean.",
            )
        ),
        H.para(
            (
                H.bold(_ELYON),
                " is grammatical in the manuscript but ",
                H.bold("not"),
                f" in the printed tradition: the printed {_ELYON} of ",
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
    and is dropped. MAM-simple style, via the shared mb_cmn.hebrew_accent_strip kernel (cf.
    MAM-basics ``versification_and_cantillation/strands.py::_strip_pointing``)."""
    keep_meteg = has.METEG_SILLUQ if hpunc.SOPA in word else has.METEG_DROP
    return has.strip_to_accents(word, keep_meteg=keep_meteg)


def _abbr(letter: str, title: str) -> object:
    return H.htel_mk_inline("abbr", {"title": title}, letter)


def _range_cell(words: tuple[str, ...], *, attr=None) -> object:
    """A ``first … last`` range label (stripped to consonants + accents), the range a complete
    verse: its first word is tinted green (start) and its last word red (stop), as the TEMBte
    tables do. ``lang="hbo"`` goes on the ``<td>`` (not the spans): the cells carry accents, and
    this page's convention (issue #58) gives accent-bearing Hebrew ``lang="hbo"`` → the Taamey
    font; one attr on the td keeps the ``…`` and words at a single size."""
    td_attr = {"lang": "hbo", **(attr or {})}
    first = H.span_c(_strip_pointing(words[0]), "vc-start")
    last = H.span_c(_strip_pointing(words[-1]), "vc-stop")
    return H.table_datum((first, "…", last), td_attr)


# --------------------------------------------------------------------------- #
# The four-strands table (issue #52)
# --------------------------------------------------------------------------- #
# Two-char row-header abbreviations for the four strands, coherent with the merged table's
# single E/T letters below; the dotted-underline title spells each out (romanized taḥton/elyon is
# fine in an attribute). m/p = manuscript/printed tradition, T/E = taxton/elyon strand. The titles
# say NO "upper"/"lower" -- that gloss invites confusion with above-letter vs below-letter accents
# (see printed_decalogue_strands module docstring; same rule on both printed-Decalogue pages).
_STRAND_ABBRS: dict[str, tuple[str, str]] = {
    "m-trad taḥton": ("mT", "manuscript-tradition taḥton (cantillation strand)"),
    "m-trad elyon": ("mE", "manuscript-tradition elyon (cantillation strand)"),
    "p-trad taḥton": ("pT", "printed-tradition taḥton (cantillation strand)"),
    "p-trad elyon": ("pE", "printed-tradition elyon (cantillation strand)"),
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
    ones keep going, making the subset relation and common start legible down the columns."""
    end = _MILESTONES.index(r.first_verse_end)
    cells: list[object] = []
    for i, skel in enumerate(_MILESTONES):
        if i > end:
            cells.append(H.table_datum("", {"lang": "hbo"}))  # verse ends before this milestone
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
    "(cantillation strand)" parenthetical is factored out to the end rather than repeated."""
    suffix = " (cantillation strand)"
    la, ta = _STRAND_ABBRS[_MERGED_STRANDS[0]]
    lb, tb = _STRAND_ABBRS[_MERGED_STRANDS[1]]
    title = f"{ta.removesuffix(suffix)} = {tb.removesuffix(suffix)} (cantillation strands, identical opening)"
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


def _verse_counts_table(readings: list[pds.Reading]) -> object:
    """A small plain table of how many chanted verses each strand divides the Exodus Decalogue
    into (12 / 10 / 13 / 9). No class: it takes the global zebra styling, like the verdict
    table -- the verse count would not fit the strand table's range cells."""
    header = H.table_row_of_headers(("strand", "chanted verses (Exodus)"))
    rows = [header]
    for r in readings:
        rows.append(
            H.table_row(
                (
                    H.table_header(pds.render_reading_name(r.name)),
                    H.table_datum(str(r.n_verses)),
                )
            )
        )
    return H.table(tuple(rows))


def _four_strands_section(readings: list[pds.Reading]) -> tuple[object, ...]:
    return (
        H.heading_level_2("The four strands of אנכי…עבדים", {"id": "four-strands"}),
        H.para(
            (
                "The manuscript and printed traditions accent the Decalogue's אנכי…עבדים unit "
                "differently. The accent on עבדים is what decides the structure: a ",
                H.bold(pds.ROM_SILLUQ_SOF_PASUQ),
                " there ends the verse, so אנכי…עבדים stands as its own verse; an ",
                H.bold(pds.ROM_ETNAHTA),
                " or ",
                H.bold(pds.ROM_REVIA),
                " there is mid-verse, folding אנכי…עבדים into a longer verse. The table below "
                "lays all four strands over the same milestone columns — אנכי (their common "
                "start), then עבדים, על־פני, and מצותי — so their subset relation is plain: every "
                "verse starts green at אנכי and ends red at its own last word, the shorter ones "
                "stopping where the longer ones keep going. Each strand keeps its own accent on "
                "עבדים, the structure-deciding mark (the column ordering is schematic — it shows "
                "only which endpoint comes before which, not the real distances between them):",
            )
        ),
        _four_strands_table(readings),
        H.para(
            (
                "How many chanted verses each strand divides the Exodus Decalogue into:",
            )
        ),
        _verse_counts_table(readings),
        H.unordered_list(
            (
                (
                    H.bold(f"Printed {_TAHTON} = manuscript {_ELYON}."),
                    " Once אנכי…עבדים is its own verse there is only one grammatical way to"
                    " accent it — ",
                    pds.ROM_ETNAHTA,
                    " in the middle, ",
                    pds.ROM_SILLUQ,
                    " at the end — so both traditions land on the same marks (consonants,"
                    " accents, and accent-boundary marks: ",
                    pds.ROM_SOF_PASUQ,
                    ", ",
                    pds.ROM_MAQAF,
                    ", ",
                    pds.ROM_LEGARMEH,
                    "). They differ only by an immaterial ",
                    pds.ROM_METEG,
                    " (which the stripped cells above drop), so the table gives them a single"
                    " shared row, labelled mE/pT.",
                ),
                (
                    H.bold(f"Printed {_ELYON} ≠ manuscript {_ELYON}."),
                    f" The printed {_ELYON} puts ",
                    H.bold(pds.ROM_REVIA),
                    " on עבדים and runs the first two commandments together into one verse (→ ",
                    H.bold("9"),
                    f" total), where the manuscript {_ELYON} closes on ",
                    pds.ROM_SILLUQ,
                    " (→ ",
                    H.bold("10"),
                    ").",
                ),
                (
                    f"The manuscript {_TAHTON} does not give אנכי…עבדים its own verse either — it"
                    " runs אנכי…פני together (",
                    pds.ROM_ETNAHTA,
                    " at עבדים, ",
                    pds.ROM_SOF_PASUQ,
                    " at פני), a third structure again.",
                ),
            )
        ),
        H.para(
            (
                f"Only one of these four strands is ungrammatical — the printed {_ELYON}, whose "
                "merged opening verse the ",
                link("section below", "#why-the-printed-elyon-fails"),
                " dissects.",
            )
        ),
    )


# --------------------------------------------------------------------------- #
# The merged-verse table (issue #59)
# --------------------------------------------------------------------------- #
# A range-divided view of the one ungrammatical printed-elyon verse, stripped to consonants +
# accents (MAM-simple style). The printed tradition merges the first two commandments into a
# single chanted verse, which the printed taxton instead keeps as five ordinary verses. Modeled
# on MAM-simple's versification-and-cantillation "TEMBte" tables, but: no M/B verse-number rows
# and the *printed* strands rather than the manuscript ones. The words keep their cantillation
# accents (only the vowels/dagesh/ordinary-meteg are stripped) because the divergence this table
# shows lives in the accents; the range division is what the green/red endpoints mark. (The M/B
# numbering is dropped because the printed taxton splits the first commandment from the second
# where the MAM taxton merges them into one chanted verse, so a single "MAM verse number" row
# cannot align 1:1 with the printed columns; issue #59.)
_ELYON_TITLE = "elyon (cantillation strand)"
_TAXTON_TITLE = "taḥton (cantillation strand)"
_ELYON_GRAD_TITLE = "schematic color gradient for the elyon verse"
_TAXTON_GRAD_TITLE = "schematic color gradient for the taḥton verse(s)"


def _taxton_columns(tax: pd.VersionResult, n_words: int) -> list[pd.ChantedVerseResult]:
    """The leading printed-taḥton chanted verses whose words together make up the merged
    printed-elyon verse. Aligned by word count: the two strands are the same word sequence,
    differing only in vocalization/accents."""
    cols: list[pd.ChantedVerseResult] = []
    total = 0
    for cv in tax.chanted_verses:
        cols.append(cv)
        total += len(cv.words)
        if total >= n_words:
            break
    return cols


def _merged_verse_table(by_key: dict) -> object:
    merged = by_key[("ex", "elyon", "printed")].ungrammatical[0]
    cols = _taxton_columns(by_key[("ex", "taxton", "printed")], len(merged.words))
    n = len(cols)

    def row(letter: str, title: str, cells: tuple[object, ...]) -> object:
        return H.table_row((H.table_header(_abbr(letter, title)), *cells))

    # E: the printed elyon — one verse spanning all the taxton columns.
    e_row = row("E", _ELYON_TITLE, (_range_cell(merged.words, attr={"colspan": str(n)}),))
    # T: the printed taxton — each column a complete ordinary verse.
    t_row = row("T", _TAXTON_TITLE, tuple(_range_cell(cv.words) for cv in cols))
    # e / t: the schematic gradient bars — one span for the merged elyon verse, one per taxton.
    e_grad = row("e", _ELYON_GRAD_TITLE, (H.table_datum("", {"class": "vc-grad", "colspan": str(n)}),))
    t_grad = row("t", _TAXTON_GRAD_TITLE, tuple(H.table_datum("", {"class": "vc-grad"}) for _ in cols))
    return H.table((e_row, t_row, e_grad, t_grad), {"class": "strand-table", "dir": "rtl"})


def _finding_section(by_key: dict) -> tuple[object, ...]:
    ex_ms = by_key[("ex", "elyon", "manuscript")]
    ms_cmd1, ms_cmd2 = ex_ms.chanted_verses[0], ex_ms.chanted_verses[1]
    return (
        H.heading_level_2(
            f"Why the printed {_ELYON} fails: the merged first verse",
            {"id": "why-the-printed-elyon-fails"},
        ),
        H.para(
            (
                f"In the manuscript {_ELYON}, the first commandment ",
                hbo("אָנֹכִי … עֲבָדִים"),
                " is its own chanted verse, and לא יהיה לך אלהים אחרים begins the next — two "
                "separate verses, ",
                H.bold("both of which parse clean"),
                ". The printed tradition instead merges the first two commandments into a single "
                "verse (nine chanted verses in all, against the manuscript’s ten). That one "
                "merged verse is what the grammar rejects. Shown stripped to consonants and "
                f"accents (MAM-simple style) and divided at the printed {_TAHTON}’s verse "
                f"boundaries — one {_ELYON} verse (E) spanning the five ordinary {_TAHTON} "
                "verses (T) it merges:",
            )
        ),
        _merged_verse_table(by_key),
        H.para(
            (
                "The single etnaḥta falls at ",
                hbo("לְשֹׂנְאָי"),
                ", leaving an over-long first half that has a segolta plus three separate "
                "revia domains (at ",
                hbo("עֲבָדִים"),
                ", ",
                hbo("עַל־פָּנַי"),
                ", and ",
                hbo("לָאָרֶץ"),
                "); the prose grammar cannot build it and returns a ",
                H.code("pashta_phrase"),
                " error — the same failure, at the same structural point, in both Decalogues.",
            )
        ),
        H.para(
            (
                "The cause is the merged ",
                H.bold("structure"),
                f", not sheer length: Deuteronomy’s printed {_ELYON} Sabbath verse runs 55 "
                "words and parses clean, while this merged verse (51 words) does not. Keeping "
                "the two commandments as the manuscript’s two separate verses (",
                f"{len(ms_cmd1.words)} and {len(ms_cmd2.words)} words) ",
                "is exactly what lets them parse.",
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
                "All eight readings (two books × taḥton/elyon × manuscript/printed) are "
                "taken from the Wikisource base page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                f" (revision {oldid}, {ts[:10]}), which every printed-vs-manuscript comparison "
                "table there transcludes. A handful of wiki templates are resolved to plain "
                "pointed text (legarmeh/paseq to a paseq mark, qere for ketiv-qere, paragraph "
                "and pisqa markers dropped); the chanted verses are split at sof pasuq.",
            )
        ),
        H.para(
            (
                "See also ",
                link("Simanim's Tiqqun as an independent witness", "printed-decalogue-simanim.html"),
                f": two notes from Simanim's Tiqqun — its main text uses the printed {_ELYON} "
                f"and its appendix the printed {_TAHTON} (issue #62). That page now leans on "
                "this page's ",
                link("four-strands table", "#four-strands"),
                " rather than repeating it.",
            )
        ),
    )


def render_body_contents(results: list[pd.VersionResult], source: dict) -> tuple[object, ...]:
    by_key = _by_key(results)
    readings = pds.resolve_readings(results)
    return (
        *_intro(),
        *_verdict_section(by_key),
        *_four_strands_section(readings),
        *_finding_section(by_key),
        *_provenance_section(source),
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
