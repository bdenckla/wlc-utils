r"""Generate gh-pages/accgram/maqaf-nonfinal-accents.html, and the JSON behind it.

The rendered account of ``maqaf_nonfinal_accents``' survey: how often a non-final atom of a
compound has an accent of its own, what the two routes to that are, and what it means for
``koren_dt_elyon``'s ``mun-mun`` on לא־תעשה.  Every number on the page is spliced from the survey
this run computes, and the same run writes ``out/accgram/maqaf-nonfinal-accents.json``, so page
and data cannot drift.

Rendered-prose conventions are ``printed_decalogue_strands``' module docstring; the romanizations
come from its ``ROM_*`` constants and are never retyped here.

Run via ``main_accgram.py generate-html-maqaf-nonfinal-accents``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import accent_marks as am
from accgram import maqaf_nonfinal_accents as mpa
from accgram import rtms_report
from accgram.almost_errors_html_shared import link, wrap_hebrew_runs
from accgram.printed_decalogue_strands import (
    ROM_ETNAHTA,
    ROM_MERKHA,
    ROM_MUNAX,
    ROM_QADMA,
    ROM_SILLUQ,
    ROM_TIPEHA,
    ROM_ZAQEF_QATAN,
)
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import wlc_utils_html as H

import repo_paths

# "Non-final atom of a compound", not "proclitic" and not "maqaf-joined atom".  "Proclitic"  # prose-ok: names the rejected term
# asserted a grammatical role the scan never checks -- route (b) is precisely an atom that keeps
# its own accent, so it is proclitic by position only.  # prose-ok: names the rejected term  And a lone atom is never "maqaf-joined"
# full stop: it is joined TO the next one, or else the two of them are joined to each other.
# Naming the atom by its POSITION in the compound says what the scan measures and nothing more,
# and it matches the module basenames.  A title is short on space and there is no other kind of
# compound here, so "maqaf" is dropped from "maqaf compound" in this one place; the body says it
# in full.  (#81's sweep settled "atom" as a reader-facing term, which is what lets it stand bare.)
PAGE_TITLE = "Accents on a Non-Final Atom of a Compound"
_WIDTH_CLASS = "goerwitz-tms-width-limited"

# The corpora, in the order the page discusses them, with the standing each has.  A reader must
# not take three columns for three independent readings, which is the page's central caveat.
_CORPUS_ROWS = (
    ("wlc422", "WLC 4.22"),
    ("uxlc", "UXLC"),
    ("mam_simple", "MAM"),
)


def _n(survey: dict, corpus: str, genre: str, field: str) -> int:
    return survey["corpora"][corpus][genre][field]


def _route_count(survey: dict, corpus: str, genre: str, route: str) -> int:
    return survey["corpora"][corpus][genre]["by_route"].get(route, 0)


def _occurrences(survey: dict, corpus: str, genre: str) -> list[dict]:
    return survey["corpora"][corpus][genre]["occurrences"]


def pin_claims(survey: dict) -> None:
    """Fail the build if the data stops supporting a claim the prose states in words.

    The counts on this page are spliced from the survey, so they cannot drift.  Its
    ARGUMENT cannot be spliced, and every sentence of it rests on a handful of facts that a
    re-vendoring or a corpus bump could quietly overturn.  So they are pinned here, and this
    raises rather than warns -- the same build-fails-on-data-drift behavior
    ``printed_decalogue_strands.resolve_readings`` has, and for the same reason: a warning in
    a generator's output is a warning nobody reads.
    """
    assert (
        _route_count(survey, "mam_simple", "prose", mpa.ROUTE_HABIT) == 0
    ), "MAM is stated to have no bare-habit case in prose"

    # The intro speaks for MAM, and says of EVERY hit there that its two accents sit on two
    # atoms and never both on one, the compound having two atoms or occasionally three.  None
    # of that is spliced, so all of it is pinned: one four-atom hit, one atom carrying a stacked
    # pair, or one hit with a single accent would leave those words quietly wrong -- and each of
    # those does occur elsewhere in the survey (WLC's Joshua 20:4 has the single accent, the
    # poetic corpus has revia mugrash), so none is a hypothetical.  A field of REPEATS is the one
    # thing allowed: MAM's Ezekiel 16:12 נֶ֙זֶם֙ has ``pash+pash``, one accent written twice.
    for o in _occurrences(survey, "mam_simple", "prose"):
        atoms = o["shape"].split("-")
        assert len(atoms) in (2, 3), o
        assert len([a for a in atoms if a != "0"]) == 2, o
        assert all(len(set(a.split("+"))) == 1 for a in atoms), o

    # THE PAGE'S ANSWER, in two claims that only the data can keep true: no MAM compound is
    # accented alike twice, in either genre, and the single one whose non-final atom has a munax
    # is Isaiah 40:7.  Both are stated flatly in the intro and again under "Koren's reading".
    for genre in ("prose", "poetic"):
        same = [
            o
            for o in _occurrences(survey, "mam_simple", genre)
            if len({a for a in o["shape"].split("-") if a != "0"}) == 1
        ]
        assert (
            not same
        ), f"MAM {genre} is stated to have no compound accented alike twice: {same}"
    mam_munax = [
        o
        for o in _occurrences(survey, "mam_simple", "prose")
        if o["shape"].split("-")[0] == mpa.shape_of([[am.MUNAX]])
    ]
    assert [o["bcv"] for o in mam_munax] == ["is40:7"], mam_munax


def _intro(survey: dict) -> tuple[object, ...]:
    # The headline frequency is MAM's, not WLC's.  A claim about what the accentuation DOES
    # wants a consensus text; WLC is one manuscript as one transcription reads it, and its
    # blemishes are visible in this very count (Joshua 20:4 זקני־העיר, whose compound has its
    # only accent on the non-final atom because the mark on העיר is a mid-verse meteg).  WLC and
    # UXLC keep their table columns, which are about the texts themselves; what they no longer do
    # is answer the page's question.  Ben, 2026-07-26: "let's leave WLC (and indeed the LC) out of
    # this" -- so the two WLC compounds with a munax on each atom (2 Chr 1:11, 1 Chr 27:14), and
    # the paragraphs that read them as Koren's nearest precedent, are gone rather than demoted.
    mam_prose = survey["corpora"]["mam_simple"]["prose"]
    pct = 100.0 * mam_prose["hits"] / mam_prose["maqaf_compounds"]
    return (
        H.heading_level_1(PAGE_TITLE),
        H.para(
            wrap_hebrew_runs(
                "Maqaf marks join two or more atoms into a single chanted word. In the prose"
                " system a chanted word usually has exactly one accent, and only in a small"
                f" minority of cases two. Of the {mam_prose['maqaf_compounds']:,} maqaf"
                f" compounds in the prose verses of MAM, {mam_prose['hits']} ({pct:.2f}%) have"
                " an accent on a non-final atom. In every one of them the two accents sit on"
                " two atoms of the compound and never both on one, the compound itself having"
                " two atoms, or occasionally three. This page counts those cases, sorts them,"
                " and asks what they mean for one printed reading in particular."
            )
        ),
        H.para(
            (
                "The reading is Koren's Deuteronomy ",
                *[link("appendix Decalogue", "printed-decalogue-koren.html"), ", "],
                *wrap_hebrew_runs(
                    "which sets לא־תעשה as a maqaf compound and accents BOTH atoms with a"
                    f" {ROM_MUNAX}, where the strand it otherwise follows in every accent sets"
                    " the two atoms apart as chanted words of their own. Is there anything in"
                    " Tanakh like it?"
                ),
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "There is not. No maqaf compound in MAM has the same accent on both atoms —"
                " not in prose verses, not in poetic ones, not once. Nearly all of the"
                f" {mam_prose['hits']} prose cases are a single grammatical category, a"
                f" {ROM_QADMA} before a {ROM_ZAQEF_QATAN}; and the one case whose non-final"
                f" atom has a {ROM_MUNAX} — Isaiah 40:7 נבל־ציץ — has a {ROM_ZAQEF_QATAN} as"
                f" the compound's own accent, not a second {ROM_MUNAX}. Nor is any printed"
                " edition known to have Koren's reading before it."
            )
        ),
    )


def _what_is_counted() -> tuple[object, ...]:
    return (
        H.heading_level_2("What is counted"),
        H.para(
            wrap_hebrew_runs(
                "The test is mechanical: inside one space-delimited chanted word, is there an"
                " accent both before and after a maqaf? A maqaf compound has no space in it, so"
                " splitting on spaces really does give chanted words, and splitting those on"
                " maqaf gives their atoms. A meteg counts as an accent only on the last chanted"
                f" word of a verse, where the same sign is a {ROM_SILLUQ}; anywhere else it is a"
                " meteg, which is not an accent at all."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "Shapes are written the way the edition transcriptions write them, one field"
                " per atom with the dash standing for the maqaf itself: qad-zaq is a qadma on"
                " the non-final atom and a zaqef qatan on the final one, and 0-mer-sil"
                " is a three-atom compound whose first atom has nothing."
            )
        ),
    )


def _corpus_caveat(survey: dict) -> tuple[object, ...]:
    return (
        H.heading_level_2("What these three columns are, and are not"),
        H.para(
            "Three columns are not three independent readings, and nothing on this page"
            " should be read as though they were."
        ),
        H.unordered_list(
            (
                (
                    H.bold("WLC"),
                    " is the Westminster transcription of the Leningrad Codex — a diplomatic"
                    " text, one manuscript as it stands.",
                ),
                (
                    H.bold("UXLC"),
                    " is not a second manuscript. Its own file header records that it was"
                    " produced from WLC 4.20 by WLC2XML, so it is the same transcription with"
                    " Kimball's corrections applied. Where the two agree, that is one hand"
                    " agreeing with itself.",
                ),
                (
                    H.bold("MAM"),
                    " is a consensus text rather than a diplomatic one: no single manuscript's"
                    " reading, but the accentuation the Masoretic tradition converges on. It"
                    " largely follows Breuer, but it is not one of Breuer's own editions.",
                ),
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "So there is no second manuscript here at all. The first two columns are the"
                " Leningrad Codex as Westminster reads it, and the third is a consensus text"
                " that has L among its sources. That matters especially for this feature,"
                " because two of the three"
                " Leningrad readings Yeivin cites for it do not survive contact with the"
                " transcription: he reports that the manuscript marks a maqaf in ועזר־מצריו"
                " (Deuteronomy 33:7) and omits one in כל קדשיו (Deuteronomy 33:3), and WLC has"
                " the opposite of both. (His third, שנאי־בצע at Exodus 18:21, he gives for a"
                " different manuscript, and WLC duly sets those two atoms apart.)"
            )
        ),
    )


def _two_routes() -> tuple[object, ...]:
    return (
        H.heading_level_2("Two routes, and why they must be counted apart"),
        H.para(
            "One bucket of “compounds with two accents” hides the distinction that decides"
            " what any of this means. There are two quite different reasons a non-final atom can"
            " end up with an accent."
        ),
        H.unordered_list(
            (
                (
                    H.bold("A secondary accent the compound inherits."),
                    " The compound is one chanted word, and a mark that belongs to the"
                    " chanted word as a whole lands on the non-final atom. This is a"
                    " grammatical category with a closed list, which Yeivin gives for the"
                    f" prose system: {ROM_QADMA} before a {ROM_ZAQEF_QATAN} (metigah-zaqef,"
                    f" §224), {ROM_MUNAX} before a {ROM_ZAQEF_QATAN} (§221), a secondary"
                    f" {ROM_MERKHA} in the chanted word of a {ROM_TIPEHA} or of a tevir"
                    f" (§§233, 241), and the mayela {ROM_TIPEHA} before an {ROM_ETNAHTA} or"
                    f" a {ROM_SILLUQ}. Membership is decided by which accent sits on the"
                    " non-final atom and which the compound has.",
                ),
                (
                    H.bold("A maqaf written after an atom that keeps its own accent."),
                    " No grammatical trigger at all — a habit of the scribe who did the"
                    " pointing. Yeivin (§293) reports it of several manuscripts, notes it"
                    " is commonest where the non-final atom is stressed on its next-to-last"
                    " syllable, and names the Leningrad Codex for it specifically, as"
                    " showing “a tradition somewhat different from the standard”. §21"
                    " lists the habit among the features by which one manuscript is told"
                    " from another.",
                ),
            )
        ),
    )


def _position_is_evidence() -> tuple[object, ...]:
    return (
        H.heading_level_2("How a hit is assigned to a route"),
        H.para(
            wrap_hebrew_runs(
                "The configuration decides, and one further question corroborates it: does the"
                " accent sit where THAT ATOM's own accent sits? That is answered without any"
                " phonology, by looking the atom up elsewhere in the same text standing free —"
                " a chanted word by itself, so it has its own accent — and comparing how many"
                " letters follow the accent in each. No syllable counting, no maters, no"
                " furtive vowels — the two spellings compared are the same spelling."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "A NO settles it. Numbers 9:17 ואחרי־כן puts its munaḥ three letters from the"
                " end, where the twenty-one free-standing ואחרי put theirs one letter from the"
                " end; so the mark cannot be that atom's own accent, and it is the secondary"
                " munaḥ of §221."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "A YES settles nothing, which is the trap. A secondary accent can land on the"
                " atom's own stress anyway. MAM's שלף־חרב agrees with all six free-standing"
                " שלף — because the stress has retracted before חרב — and it is still a"
                " secondary merkha. So position corroborates the configuration; it never"
                " overrules it."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "One thing this page does NOT establish is Yeivin's own explanation of the"
                " habit, that it goes with next-to-last-syllable stress. Testing that needs a"
                " model of where the stress falls, which this survey does not have."
            )
        ),
    )


def _prose_table(survey: dict) -> object:
    header = H.table_row_of_headers(
        (
            "",
            "maqaf compounds",
            "accent on a non-final atom",
            "secondary (inherited)",
            "own accent kept",
            "undecided",
        )
    )
    rows = [header]
    for key, label in _CORPUS_ROWS:
        rows.append(
            H.table_row_of_data(
                (
                    H.bold(label),
                    f"{_n(survey, key, 'prose', 'maqaf_compounds'):,}",
                    str(_n(survey, key, "prose", "hits")),
                    str(_route_count(survey, key, "prose", mpa.ROUTE_SECONDARY)),
                    H.bold(str(_route_count(survey, key, "prose", mpa.ROUTE_HABIT))),
                    str(_route_count(survey, key, "prose", mpa.ROUTE_UNDECIDED)),
                )
            )
        )
    return H.table(tuple(rows), {"class": "goerwitz-tms-table"})


def _prose_section(survey: dict) -> tuple[object, ...]:
    wlc_configs = survey["corpora"]["wlc422"]["prose"]["by_configuration"]
    named = sorted(
        ((c, n) for c, n in wlc_configs.items() if c and not c.startswith("unnamed")),
        key=lambda cn: -cn[1],
    )
    return (
        H.heading_level_2("The prose verses"),
        _prose_table(survey),
        H.para(
            wrap_hebrew_runs(
                "The zero is the striking cell. MAM has only the named grammatical"
                " configurations and never the bare habit — consistent with Breuer's own rule"
                " that an accent and a maqaf are mutually exclusive, a mark following the"
                " regular order of the accents cancelling the maqaf, while the secondary"
                " marks, which are there only BECAUSE the atom is joined, never do."
            )
        ),
        H.para(
            "Its total is nonetheless the largest of the three, and that is not a"
            " contradiction: MAM has secondary marks in places where the manuscript has none,"
            " and has none of the habit where the manuscript has it. A single total would have"
            " shown neither."
        ),
        H.para("WLC's inherited-secondary cases, by configuration:"),
        H.unordered_list(
            tuple(f"{config} — {n}" for config, n in named),
        ),
    )


def _koren_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Koren's reading"),
        H.para(
            wrap_hebrew_runs(
                "Every named configuration above pairs two DIFFERENT accents: the compound's own"
                " accent, and a secondary mark of a shape that can precede it. Koren's two are"
                " the same accent twice, and no chanted word in MAM is accented that way — so"
                " there is no category the reading could be said to be following, and nothing"
                " in MAM it could be said to be repeating."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "The Decalogue's own Exodus 20:10 לא־תעשה shows a munaḥ on each atom, but that"
                " is the two cantillations tangled together rather than either one of them:"
                " untangled, MAM's עליון has no maqaf, and לא and תעשה are two chanted words,"
                " each with a munaḥ of its own — the very two atoms Koren has as one maqaf"
                " compound."
            )
        ),
        H.heading_level_3("The nearest thing in a printed edition"),
        H.para(
            (
                *wrap_hebrew_runs(
                    "No printed edition on these pages has the shape either. The nearest is the "
                ),
                link("Simanim Tiqqun", "printed-decalogue-simanim.html"),
                *wrap_hebrew_runs(
                    "'s munaḥ on the joined לא of לא־יהיה and of לא־תעשה — the same phenomenon,"
                    " a non-final atom keeping its accent, one step short of the same shape, and"
                    " in this very passage."
                ),
            )
        ),
    )


def _poetic_section(survey: dict) -> tuple[object, ...]:
    rows = [
        H.table_row_of_headers(("", "maqaf compounds", "accent on a non-final atom"))
    ]
    for key, label in _CORPUS_ROWS:
        rows.append(
            H.table_row_of_data(
                (
                    H.bold(label),
                    f"{_n(survey, key, 'poetic', 'maqaf_compounds'):,}",
                    str(_n(survey, key, "poetic", "hits")),
                )
            )
        )
    return (
        H.heading_level_2(
            "The poetic verses, and why the count cannot answer for them"
        ),
        H.table(tuple(rows), {"class": "goerwitz-tms-table"}),
        H.para(
            wrap_hebrew_runs(
                "These numbers are a floor, and they are not comparable with the prose ones."
                " Breuer records that in poetic verses the maqaf after a secondary"
                " mark is customarily left unwritten while the atom still counts as joined —"
                " so most of what would be counted here is invisible to a maqaf test by"
                " construction."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "His own short list of places where the maqaf IS written bears that out from"
                " the other side. Job 6:10 ותהי־עוד and Proverbs 25:20 מעדה־בגד are set"
                " WITHOUT a maqaf in WLC and UXLC, and with one only in MAM: the maqaf there is"
                " the editor's restoration, not the manuscript's writing."
            )
        ),
        H.para(
            "The routes are not attempted for these verses either. Both halves of the split"
            " above are prose doctrine, and the poetic counterpart is a different list; running"
            " the prose one over poetic verses would file a poetic secondary as a scribal"
            " habit."
        ),
    )


def render_body_contents(survey: dict) -> tuple[object, ...]:
    pin_claims(survey)
    sections: list[object] = [
        *_intro(survey),
        *_what_is_counted(),
        *_corpus_caveat(survey),
        *_two_routes(),
        *_position_is_evidence(),
        *_prose_section(survey),
        *_koren_section(),
        *_poetic_section(survey),
    ]
    return (H.div(tuple(sections), {"class": _WIDTH_CLASS}),)


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "maqaf-nonfinal-accents.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the maqaf-nonfinal-accents page.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=mpa.default_json_out_path(),
        help="Output JSON path for the survey behind the page.",
    )


def run(args: argparse.Namespace) -> None:
    survey = mpa.build_survey()
    mpa.write_json(survey, args.json_out)

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(survey),
        write_ctx=H.WriteCtx(
            title=PAGE_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    prose_hits = _n(survey, "wlc422", "prose", "hits")
    print(f"JSON: {args.json_out}")
    print(f"HTML: {html_out} (WLC prose hits: {prose_hits})")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
