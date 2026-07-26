r"""Generate gh-pages/accgram/maqaf-proclitic-accents.html, and the JSON behind it.

The rendered account of ``maqaf_proclitic_accents``' survey: how often a maqaf-joined proclitic
carries an accent of its own, what the two routes to that are, and what it means for
``koren_dt_elyon``'s ``mun-mun`` on לא־תעשה.  Every number on the page is spliced from the survey
this run computes, and the same run writes ``out/accgram/maqaf-proclitic-accents.json``, so page
and data cannot drift.

Rendered-prose conventions are ``printed_decalogue_strands``' module docstring; the romanizations
come from its ``ROM_*`` constants and are never retyped here.

Run via ``main_accgram.py generate-html-maqaf-proclitic-accents``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import accent_marks as am
from accgram import maqaf_proclitic_accents as mpa
from accgram import rtms_report
from accgram.almost_errors_html_shared import link, wrap_hebrew_runs
from accgram.printed_decalogue_strands import (
    ROM_ETNAHTA,
    ROM_MERKHA,
    ROM_MUNAX,
    ROM_PASEQ,
    ROM_PAZER,
    ROM_QADMA,
    ROM_SILLUQ,
    ROM_TIPEHA,
    ROM_ZAQEF_QATAN,
)
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import wlc_utils_html as H

import repo_paths

PAGE_TITLE = "Accents on a Maqaf-Joined Proclitic"
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


def _find(survey: dict, corpus: str, genre: str, bcv: str) -> dict | None:
    return next(
        (o for o in _occurrences(survey, corpus, genre) if o["bcv"] == bcv), None
    )


def pin_claims(survey: dict) -> None:
    """Fail the build if the data stops supporting a claim the prose states in words.

    The counts on this page are spliced from the survey, so they cannot drift.  Its
    ARGUMENT cannot be spliced, and every sentence of it rests on a handful of facts that a
    re-vendoring or a corpus bump could quietly overturn.  So they are pinned here, and this
    raises rather than warns -- the same build-fails-on-data-drift behavior
    ``printed_decalogue_strands.resolve_readings`` has, and for the same reason: a warning in
    a generator's output is a warning nobody reads.
    """
    koren_shape = mpa.shape_of([[am.MUNAX], [am.MUNAX]])  # Koren's own ``mun-mun``
    mun_mun = {
        corpus: [
            o
            for o in _occurrences(survey, corpus, "prose")
            if o["shape"] == koren_shape
        ]
        for corpus, _label in _CORPUS_ROWS
    }
    wlc_bcvs = {o["bcv"] for o in mun_mun["wlc422"]}
    assert wlc_bcvs == {"2c1:11", "1c27:14"}, wlc_bcvs
    assert all(o["route"] == mpa.ROUTE_HABIT for o in mun_mun["wlc422"]), mun_mun[
        "wlc422"
    ]
    assert {o["bcv"] for o in mun_mun["uxlc"]} == {"2c1:11"}, mun_mun["uxlc"]
    assert mun_mun["mam_simple"] == [], mun_mun["mam_simple"]
    assert (
        _route_count(survey, "mam_simple", "prose", mpa.ROUTE_HABIT) == 0
    ), "MAM is stated to have no bare-habit case in prose"


def _intro(survey: dict) -> tuple[object, ...]:
    wlc_prose = survey["corpora"]["wlc422"]["prose"]
    pct = 100.0 * wlc_prose["hits"] / wlc_prose["maqaf_compounds"]
    return (
        H.heading_level_1(PAGE_TITLE),
        H.para(
            wrap_hebrew_runs(
                "A maqaf joins two words into one chanted word, and the joined word normally"
                f" gives up its own accent to do so. Normally, but not always: in"
                f" {wlc_prose['maqaf_compounds']:,} maqaf compounds across the prose books,"
                f" {wlc_prose['hits']} ({pct:.2f}%) carry an accent on a non-final atom. This"
                " page counts those, sorts them, and asks what they mean for one printed"
                " reading in particular."
            )
        ),
        H.para(
            (
                "The reading is Koren's Deuteronomy ",
                *[link("appendix Decalogue", "printed-decalogue-koren.html"), ", "],
                *wrap_hebrew_runs(
                    "which sets לא־תעשה as a maqaf compound and accents BOTH atoms with a"
                    f" {ROM_MUNAX}, where the strand it otherwise follows in every accent sets"
                    " the two words apart. Is there anything in Tanakh like it?"
                ),
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "There is. The answer, with the counts below behind it: two prose compounds"
                f" carry a {ROM_MUNAX} on each atom, and the closer of them matches Koren not"
                " only in shape but in its surroundings. The reading is rare, and it is the"
                " kind of thing the Leningrad Codex itself does — but no printed edition is"
                " known to have done it before."
            )
        ),
    )


def _what_is_counted() -> tuple[object, ...]:
    return (
        H.heading_level_2("What is counted"),
        H.para(
            wrap_hebrew_runs(
                "The test is mechanical: inside one space-delimited word, is there an accent"
                " both before and after a maqaf? A meteg counts as an accent only on the last"
                f" chanted word of a verse, where the same sign is a {ROM_SILLUQ}; anywhere"
                " else it is a meteg, which is not an accent at all."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "Shapes are written the way the edition transcriptions write them, one field"
                " per atom with the dash standing for the maqaf itself: qad-zaq is a qadma on"
                " the joined word and a zaqef qatan on the word it is joined to, and 0-mer-sil"
                " is a three-atom compound whose first atom carries nothing."
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
                    " is the Westminster transcription of the Leningrad Codex.",
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
                    " is Breuer's edition — an edited text, not a manuscript reading.",
                ),
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "So there is no independent manuscript here at all. Every count below measures"
                " the Leningrad Codex as Westminster reads it, and what an edition does with"
                " it. That matters especially for this feature, because two of the three"
                " Leningrad readings Yeivin cites for it do not survive contact with the"
                " transcription: he reports that the manuscript marks a maqaf in ועזר־מצריו"
                " (Deuteronomy 33:7) and omits one in כל קדשיו (Deuteronomy 33:3), and WLC has"
                " the opposite of both. (His third, שנאי־בצע at Exodus 18:21, he gives for a"
                " different manuscript, and WLC duly sets those two words apart.)"
            )
        ),
    )


def _two_routes() -> tuple[object, ...]:
    return (
        H.heading_level_2("Two routes, and why they must be counted apart"),
        H.para(
            "One bucket of “compounds with two accents” hides the distinction that decides"
            " what any of this means. There are two quite different reasons a joined word can"
            " end up with an accent."
        ),
        H.unordered_list(
            (
                (
                    H.bold("A secondary accent the compound inherits."),
                    " The compound is one chanted word, and a mark that belongs to the"
                    " chanted word as a whole lands on the joined half. This is a"
                    " grammatical category with a closed list, which Yeivin gives for the"
                    f" prose books: {ROM_QADMA} before a {ROM_ZAQEF_QATAN} (metigah-zaqef,"
                    f" §224), {ROM_MUNAX} before a {ROM_ZAQEF_QATAN} (§221), a secondary"
                    f" {ROM_MERKHA} on the word of a {ROM_TIPEHA} or of a tevir (§§233,"
                    f" 241), and the mayela {ROM_TIPEHA} before an {ROM_ETNAHTA} or a"
                    f" {ROM_SILLUQ}. Membership is decided by which accent sits on the"
                    " joined word and which the compound bears.",
                ),
                (
                    H.bold("A maqaf written after a word that keeps its own accent."),
                    " No grammatical trigger at all — a habit of the scribe who did the"
                    " pointing. Yeivin (§293) reports it of several manuscripts, notes it"
                    " is commonest where the joined word is stressed on its next-to-last"
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
                " accent sit where THAT WORD's own accent sits? That is answered without any"
                " phonology, by looking the word up elsewhere in the same text standing free"
                " and bearing its own accent, and comparing how many letters follow the accent"
                " in each. No syllable counting, no maters, no furtive vowels — the two"
                " spellings compared are the same spelling."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "A NO settles it. Numbers 9:17 ואחרי־כן puts its munaḥ three letters from the"
                " end, where the twenty-one free-standing ואחרי put theirs one letter from the"
                " end; so the mark cannot be that word's own accent, and it is the secondary"
                " munaḥ of §221."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "A YES settles nothing, which is the trap. A secondary accent can land on the"
                " word's own stress anyway. MAM's שלף־חרב agrees with all six free-standing"
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
        H.heading_level_2("The prose books"),
        _prose_table(survey),
        H.para(
            wrap_hebrew_runs(
                "The zero is the striking cell. Breuer's edition contains only the named"
                " grammatical configurations and never the bare habit — consistent with his"
                " own rule that an accent and a maqaf are mutually exclusive, a mark following"
                " the regular order of the accents cancelling the maqaf, while the secondary"
                " marks, which are in that word only BECAUSE it is joined, never do."
            )
        ),
        H.para(
            "Its total is nonetheless the largest of the three, and that is not a"
            " contradiction: Breuer both restores secondary marks the manuscript lacks and"
            " normalizes the habit away. A single total would have shown neither."
        ),
        H.para("WLC's inherited-secondary cases, by configuration:"),
        H.unordered_list(
            tuple(f"{config} — {n}" for config, n in named),
        ),
    )


def _koren_section(survey: dict) -> tuple[object, ...]:
    free_n = _find(survey, "wlc422", "prose", "2c1:11")["oracle"]["free_occurrences"]
    return (
        H.heading_level_2("Koren's reading, and what precedes it"),
        H.para(
            wrap_hebrew_runs(
                "Both prose compounds bearing a munaḥ on each atom fall on the habit side, not"
                " the grammatical one — so neither is a category Koren could be said to be"
                " following."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                f"2 Chronicles 1:11 ויאמר־אלהים ׀ לשלמה is the close one. Its {ROM_MUNAX} sits"
                f" exactly where all {free_n:,} free-standing ויאמר put theirs, so it is not a"
                " slip of the pointing. And the surroundings match: the stroke after אלהים is"
                f" a narrow-sense {ROM_PASEQ} rather than a legarmeh, which leaves both"
                f" {ROM_MUNAX}s plain servants of the {ROM_PAZER} on the following word — which"
                " is precisely what Koren has, a revia, then the two-munaḥ compound, then a"
                " pazer. Breuer's edition cancels that maqaf."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "1 Chronicles 27:14 לעשתי־עשר, before a zaqef qatan, is the other. It is in WLC"
                " 4.20 and 4.22 alike but in neither UXLC nor MAM, so it rests on less."
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "The Decalogue's own Exodus 20:10 לא־תעשה shows a munaḥ on each atom in all"
                " three texts, but that is the two cantillations tangled together rather than"
                " either one of them: untangled, MAM's עליון cancels the maqaf and sets לא and"
                " תעשה as two separate munaḥ words — which is exactly what Koren joins."
            )
        ),
        H.heading_level_3("Ask it of manuscripts and of printed editions separately"),
        H.para(
            (
                *wrap_hebrew_runs(
                    "The precedent above is a manuscript one, and a thin one: a single"
                    " Leningrad reading, in a transcription whose fidelity on this very"
                    " feature the caveat above puts in question. Among printed editions"
                    " nothing here has the shape at all. The nearest is the "
                ),
                link("Simanim Tiqqun", "printed-decalogue-simanim.html"),
                *wrap_hebrew_runs(
                    "'s munaḥ on the joined לא of לא־יהיה and of לא־תעשה — the same phenomenon,"
                    " a joined word keeping its accent, one step short of the same shape, and"
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
        H.heading_level_2("The poetic books, and why the count cannot answer for them"),
        H.table(tuple(rows), {"class": "goerwitz-tms-table"}),
        H.para(
            wrap_hebrew_runs(
                "These numbers are a floor, and they are not comparable with the prose ones."
                " Breuer records that in the three poetic books the maqaf after a secondary"
                " mark is customarily left unwritten while the word still counts as joined —"
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
            "The routes are not attempted for these books either. Both halves of the split"
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
        *_koren_section(survey),
        *_poetic_section(survey),
    ]
    return (H.div(tuple(sections), {"class": _WIDTH_CLASS}),)


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "maqaf-proclitic-accents.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the maqaf-proclitic-accents page.",
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
