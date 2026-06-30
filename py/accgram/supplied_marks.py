r"""Generate gh-pages/accgram/supplied-marks.html -- the supplied-mark inventory (#36).

A *supplied mark* is a third kind of editorial charity, distinct from the two on the
almost-errors page.  Those *reinterpret* a mark the manuscript already has (a prose
geresh muqdam read as a plain geresh; a poetic plain geresh promoted to revia mugrash).
A supplied mark instead *adds* a mark WLC lacks: when WLC's dual cantillation drops
one reading's accent on a word (it committed to the other reading's word-division), the
dual-cantillation detangler supplies that one accent from MAM so the reading's chanted
verse parses.  Because it is a new kind of charity, it gets its own page rather than a row
in "Editorial charities".

A supplied-mark word parses clean -- the supply is exactly what lets it parse -- so it is
surfaced ONLY here, never counted as a prose ungrammatical verse.  (A genuine WLC dual-cantillation
*error*, where WLC has an accent neither reading explains, is the opposite case: it is
not supplied but flagged, and appears in the prose ungrammatical-verse report.)

The page has two inventories, both generated live from the detangling run
(accgram.dual_cant_run) so they can never drift from the checker's real behaviour:

  * "Supplied accents": each of the five supplied accents in turn -- its reading, the
    accent supplied, what WLC has instead, and the LC manuscript image; and
  * "Erased and added maqaf and sof pasuq marks": the word-division marks each reading
    adds or erases relative to WLC's tangled form (narrow-sense paseq is not part of the
    accent grammar and is not tracked).

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import accent_marks as am
from accgram import dual_cant_run
from accgram import rtms_report
from accgram import rtmsr_media
from accgram.almost_errors_html_shared import (
    accents_and_letters,
    hbo,
    link,
    ref_display,
    wrap_hebrew_runs,
)
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram import rtms_data
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import my_html_for_img
from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "Supplied and erased marks"
_WIDTH_CLASS = "goerwitz-tms-width-limited"

# ḥet is transliterated X in the detangler's ASCII labels and ḥ (h + combining dot below,
# never plain h) in the page's Unicode prose -- see the repo transliteration standard.
_HET = "ḥ"
_TAXTON = "ta" + _HET + "ton"
_ELYON = "elyon"
_MUNAX = "muna" + _HET
_TIPEXA = "tipe" + _HET + "a"

# X-form (ASCII) label -> the page's Unicode ḥ display form.
_TRANSLIT = {"taxton": _TAXTON, "tipexa": _TIPEXA, "atnax": "atna" + _HET}

_UXLC_DT58_NOTE = "https://tanach.us/Notes/Deuteronomy/Deuteronomy.5.8.2-t.html"

# Each supplied accent, paired with its manuscript image.  Keyed by (bcv, strand, accent
# codepoint) and cross-checked at render time against the live supplies, so it cannot drift.
# Four are LC crops (the LC-... names carry their own Sefaria source link/caption); dt 5:8
# has no clean LC line of its own here, so we borrow the crop from its UXLC note.
_LC, _UXLC_NOTE = "lc", "uxlc-note"
_CASE_IMAGE: dict[tuple[str, str, str], tuple[str, str]] = {
    ("dt5:6", "bet", am.TIPEXA): ("LC-102A-col-3-line-19-Deut-5v6.png", _LC),
    ("dt5:6", "bet", am.ATNAX): ("LC-102A-col-3-line-20-Deut-5v6.png", _LC),
    ("dt5:8", "alef", am.QADMA): ("Deut-5v8-uxlc-note.jpg", _UXLC_NOTE),
    ("dt5:17", "alef", am.TIPEXA): ("LC-102B-col-2-line-9-Deut-5v17.png", _LC),
    ("ex20:3", "alef", am.MERKHA): ("LC-043A-col-2-line-19-Exod-20-v3.png", _LC),
}

_PASSAGE_RANK = {"gn": 0, "ex": 1, "dt": 2}


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "supplied-marks.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=rtms_data.default_wlc422_kq_u_dir(repo_root),
        help="Directory of WLC 4.22 ketiv/qere Unicode 1verses_*.json files.",
    )
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=default_mam_simple_dir(repo_root),
        help="Directory of MAM-simple json-vtrad-bhs book files.",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the supplied-marks page.",
    )


def _translit(text: str) -> str:
    """Render the detangler's ASCII ḥet (X) labels in the page's Unicode ḥ form."""
    for ascii_form, uni_form in _TRANSLIT.items():
        text = text.replace(ascii_form, uni_form)
    return text


def _comment(contents) -> object:
    return H.para(contents, {"class": "goerwitz-tms-comment"})


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.heading_level_2("Introduction"),
        H.para(
            (
                "WLC, like the LC itself, has three dually-cantillated prose passages:"
                " the two Decalogues (Exodus 20, Deuteronomy 5)"
                " and the Reuben/Bilhah verse (Genesis 35:22)."
                " Before attempting to grammar-check one of these passages we"
                " detangle"
                " it into its two single-cantillation strands, guided by MAM’s"
                " strands."
                " After detangling a passage, we feed each strand’s chanted verses to"
                " the ordinary prose accent grammar checker."
                " The accents checked are WLC’s own, except for the cases described below.",
            )
        ),
        H.para(
            (
                "Sometimes WLC leaves a word without an accent in one strand."
                " In these cases, the detangler ",
                H.bold("supplies"),
                " that one accent from MAM, making that strand’s chanted verse grammatical."
                " These charitably-supplied accents are recorded below."
                " This is a third kind of charity, distinct from the two reinterpretations on the",
                *[" ", link("almost-errors page", "almost-errors.html"), ":"],
                " those reinterpret the type of geresh present in WLC,"
                " whereas a supplied mark adds a mark not present in WLC.",
            )
        ),
        H.para(
            (
                "A verse with a supplied mark parses cleanly,"
                " so it is listed here since it will not be"
                " listed among the ungrammatical verses."
                f" One verse, Deuteronomy 5:8, gets a supplied accent that fixes the {_TAXTON} strand, but the {_ELYON} strand’s accent is ungrammatical."
                " Therefore, the beleaguered word of that verse is listed both here and among",
                *[" ", link("the ungrammatical verses", "goerwitz.html#obdt5v8"), "."],
            )
        ),
    )


# --------------------------------------------------------------------------- #
# "Supplied accents": each supply in turn, with explanatory text and its image.
# --------------------------------------------------------------------------- #
def _image_block(img_file: str, kind: str) -> object:
    if kind == _LC:
        # rtmsr_media builds the "Image source: <page> column N line N" caption + Sefaria link.
        figures = rtmsr_media.render_image_paragraphs(
            {"img": img_file}, structured_text_lookup=lambda row, key: row.get(key)
        )
        return figures[0]
    # The UXLC-note crop: credit the note (an LC image, served via Sefaria).
    para = my_html_for_img.html_for_single_img(
        img_file, img_para_attr={"class": "goerwitz-tms-image"}
    )
    caption = H.figcaption(
        (
            "Image source: ",
            H.anchor("tanach.us note", {"href": _UXLC_DT58_NOTE}),
            " (Leningrad Codex, via Sefaria.org).",
        ),
        {"class": "goerwitz-tms-image-caption"},
    )
    return H.figure((para, caption), {"class": "goerwitz-tms-figure"})


def _case_extra(s) -> tuple[object, ...]:
    """Extra prose for Deuteronomy 5:8."""
    key = (s.bcv, s.strand, s.accent)
    if key == ("dt5:8", "alef", am.QADMA):
        return (
            _comment(
                (
                    f"This word is further discussed",
                    *[" ", link("here", "goerwitz.html#obdt5v8"), ","],
                    " among the ungrammatical verses."
                )
            ),
        )
    return ()


def _supplied_case(s) -> tuple[object, ...]:
    img_file, kind = _CASE_IMAGE[(s.bcv, s.strand, s.accent)]
    header = H.para(
        f"{ref_display(s.bcv)}: the detangler supplies the {_translit(s.strand_label)}’s"
        f" {_translit(s.accent_name)}",
        {"class": "goerwitz-tms-reading-label"},
    )
    reason = _comment(wrap_hebrew_runs(_translit(s.reason)))
    return (header, reason, *_case_extra(s), _image_block(img_file, kind))


def _supplied_section(supplies: list) -> tuple[object, ...]:
    blocks: list[object] = [H.heading_level_2("Supplied accents")]
    if not supplies:
        blocks.append(H.para("No marks were supplied."))
        return tuple(blocks)
    for s in supplies:
        if (s.bcv, s.strand, s.accent) not in _CASE_IMAGE:
            raise KeyError(
                f"supplied-marks page has no image/case for {s.bcv} {s.strand}"
                f" {s.accent_name}; add it to _CASE_IMAGE."
            )
    for s in sorted(supplies, key=_reading_order_key):
        blocks.extend(_supplied_case(s))
    return tuple(blocks)


def _reading_order_key(s) -> tuple:
    bb = s.bcv[:2]
    chnu, vrnu = (int(p) for p in s.bcv[2:].split(":"))
    # alef strand (taxton/pashut) before bet (elyon/midrashit) within a verse
    return (_PASSAGE_RANK.get(bb, 9), chnu, vrnu, 0 if s.strand == "alef" else 1)


# --------------------------------------------------------------------------- #
# "Erased and added maqaf and sof pasuq marks": the word-division inventory.
# --------------------------------------------------------------------------- #
def _carrying_form(changes: list, bcv: str, mark: str, delta: str, strand: str) -> object:
    """The pointed form (as an hbo span) that carries a given division change in one strand:
    WLC's word when the mark is erased, MAM's strand word when it is added."""
    for d in changes:
        if (d.bcv, d.mark, d.delta, d.strand) == (bcv, mark, delta, strand):
            return hbo(d.wlc_word if delta == "erased" else d.mam_word)
    return "?"


def _division_prose(changes: list) -> tuple[object, ...]:
    yihye = _carrying_form(changes, "ex20:3", "maqaf", "erased", "alef")  # taḥton drops WLC's יִהְיֶה־
    lo_added = _carrying_form(changes, "ex20:3", "maqaf", "added", "alef")  # the taḥton's added לֹא־
    lo_elyon = _carrying_form(changes, "ex20:10", "maqaf", "erased", "bet")  # elyon drops WLC's לֹא־
    return (
        _comment(
            "Genesis 35:22: the pashut strand breaks the verse in two, adding a mid-verse"
            " sof pasuq that WLC — and the midrashit strand — do not have."
        ),
        _comment(
            f"The Decalogues (Exodus 20, Deuteronomy 5): the {_TAXTON} subdivides into short"
            " chanted verses, adding a sof pasuq inside several numbered verses (Exodus 20:3,"
            " 20:4, 20:8, 20:9, 20:10; Deuteronomy 5:12) and erasing WLC’s verse-final one"
            " where the commandment runs on (Exodus 20:2 and the short prohibitions 20:13–15;"
            f" Deuteronomy 5:6, 5:17–19). The {_ELYON} does the reverse, grouping the"
            " commandments into long chanted verses and so erasing WLC’s internal sof pasuqs"
            " (Exodus 20:5; Deuteronomy 5:7, 5:8, 5:9, 5:13, 5:14)."
        ),
        _comment(
            (
                f"The maqaf joins are re-cut to match. At Exodus 20:3 the {_TAXTON} drops"
                " WLC’s join ",
                yihye,
                " — the supplied merkha makes that word stand on its own — and instead joins ",
                lo_added,
                f"; the {_ELYON}, conversely, drops WLC’s join ",
                lo_elyon,
                " at Exodus 20:10 (and likewise at Deuteronomy 5:8).",
            )
        ),
    )


def _division_sort_key(d) -> tuple:
    chnu, vrnu = (int(p) for p in d.bcv[2:].split(":"))
    return (_PASSAGE_RANK.get(d.bcv[:2], 9), 0 if d.strand == "alef" else 1, chnu, vrnu, d.mark, d.delta)


def _division_table(changes: list) -> object:
    header = H.table_row_of_headers(("Verse", "Strand", "Mark", "Change", "Word"))
    rows = [header]
    for d in sorted(changes, key=_division_sort_key):
        carrier = d.wlc_word if d.delta == "erased" else d.mam_word
        rows.append(
            H.table_row_of_data(
                (ref_display(d.bcv), _translit(d.strand_label), d.mark, d.delta, hbo(carrier))
            )
        )
    return H.table(tuple(rows), {"class": "goerwitz-obs-tree-table"})


def _legarmeh_para() -> object:
    bamayim = hbo(accents_and_letters("בַּמַּ֖֣יִם"))  # WLC's tangled tipeḥa+munaḥ form
    return _comment(
        (
            "Legarmeh is neither added nor erased. The three passages carry nine legarmeh"
            f" accents (a {_MUNAX} with a following paseq, before a revia), but every one sits"
            f" on a word WLC itself has with that {_MUNAX} and paseq — the paseq is never"
            " supplied from MAM. A legarmeh comes and goes with its corresponding"
            f" {_MUNAX}, just as a sof pasuq comes and goes with its corresponding silluq,"
            " so a legarmeh surfaces only in the strand that takes"
            " WLC’s ",
            _MUNAX,
            ": WLC’s tangled ",
            bamayim,
            f" (Exodus 20:4), for instance, carries both a {_TIPEXA} and a {_MUNAX}, so the"
            f" {_ELYON} (taking the {_MUNAX}) reads a legarmeh there while the {_TAXTON}"
            f" (taking the {_TIPEXA}) does not. So the inventory above is maqaf and sof"
            " pasuq only.",
        )
    )


def _division_section(changes: list) -> tuple[object, ...]:
    if not changes:
        return (
            H.heading_level_2("Erased and added maqaf and sof pasuq marks"),
            H.para("No maqaf or sof pasuq marks were added or erased."),
        )
    return (
        H.heading_level_2("Erased and added maqaf and sof pasuq marks"),
        H.para(
            (
                "Detangling also reconfigures the way that atoms are joined into chanted words."
                " Each strand’s maqaf marks (or lack thereof, i.e. spaces) are taken from MAM,"
                " so, relative to WLC’s tangled form, the checker both adds and removes maqaf marks."
                " (WLC has a mix of the two strands’ maqaf marks; it is not simply “maqaf-maximalist”.)"
                " (Narrow-sense paseq is not part of the accent grammar, so it is not tracked.)"
                f" The {len(changes)} additions and erasures are itemized in the table below;"
                " the pattern in each passage is as follows."
            )
        ),
        *_division_prose(changes),
        _division_table(changes),
        _legarmeh_para(),
    )


def render_body_contents(supplies: list, division_changes: list) -> tuple[object, ...]:
    sections: list[object] = [
        *_intro(),
        *_supplied_section(supplies),
        *_division_section(division_changes),
    ]
    wrapper = H.div(tuple(sections), {"class": _WIDTH_CLASS})
    return (wrapper,)


def run(args: argparse.Namespace) -> None:
    results = dual_cant_run.detangle_results(args.wlc422_kq_u_dir, args.mam_simple_dir)
    supplies = [s for pr in results for s in pr.supplied_marks]
    division_changes = [d for pr in results for d in pr.division_changes]

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(supplies, division_changes),
        write_ctx=H.WriteCtx(
            title=REPORT_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    print(
        f"HTML: {html_out} ({len(supplies)} supplied marks, "
        f"{len(division_changes)} division changes)"
    )


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
