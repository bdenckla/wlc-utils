r"""Generate gh-pages/accgram/supplied-marks.html -- the supplied-mark inventory (#36).

A *supplied mark* is a third kind of editorial charity, distinct from the two on the
almost-errors page.  Those *reinterpret* a mark the manuscript already wrote (a prose
geresh muqdam read as a plain geresh; a poetic plain geresh promoted to revia mugrash).
A supplied mark instead *adds* a mark WLC never wrote: when WLC's dual cantillation drops
one reading's accent on a word (it committed to the other reading's word-division), the
dual-cantillation detangler supplies that one accent from MAM so the reading's chanted
verse parses.  Because it is a new kind of charity, it gets its own page rather than a row
in "Editorial charities".

A supplied-mark word parses clean -- the supply is exactly what lets it parse -- so it is
surfaced ONLY here, never counted as a prose oddball.  (A genuine WLC dual-cantillation
*error*, where WLC wrote an accent neither reading explains, is the opposite case: it is
not supplied but flagged, and appears in the prose oddball report.)

The page is generated live from the detangling run (accgram.dual_cant_run), so the
inventory can never drift from the checker's real behaviour.

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import dual_cant_run
from accgram import rtms_report
from accgram.almost_errors_html_shared import accents_and_letters, hbo, link, ref_display
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram import rtms_data
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "Supplied marks"
_WIDTH_CLASS = "goerwitz-tms-width-limited"


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


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.heading_level_2("Introduction"),
        H.para(
            (
                "WLC’s three dually-cantillated prose passages — the two Decalogues"
                " (Exodus 20, Deuteronomy 5) and the Reuben/Bilhah verse (Genesis 35:22)"
                " — carry two cantillation readings at once. To grammar-check them, the"
                " checker ",
                link("detangles", "goerwitz.html"),
                " each into its two single-cantillation readings, guided by MAM’s"
                " already-separated strands, and feeds each reading’s chanted verses to"
                " the ordinary prose grammar. The accents checked are WLC’s own, except for"
                " the cases described below.",
            )
        ),
        H.para(
            (
                "Sometimes WLC commits to one reading’s word-division and thereby writes"
                " no distinct accent for the other reading on a word (most often a"
                " maqaf-join, or a verse-final silluq that belongs to only one reading)."
                " There the detangler ",
                H.bold("supplies"),
                " that one accent from MAM so the reading’s chanted verse parses, and"
                " records it below. This is a third kind of charity, distinct from the"
                " two reinterpretations on the ",
                link("almost-errors page", "almost-errors.html"),
                ": those reread a mark present in WLC, whereas a supplied"
                " mark adds a mark not present in WLC.",
            )
        ),
        H.para(
            (
                "A supplied-mark word parses clean — the supply is what lets it parse —"
                " so it is inventoried here and ",
                H.bold("not"),
                " counted as an oddball. A genuine WLC dual-cantillation error (WLC"
                " writing an accent neither reading explains) is the opposite: it is not"
                " supplied but flagged in the ",
                link("prose checker run", "goerwitz.html"),
                ".",
            )
        ),
    )


def _table(supplies: list) -> object:
    header = H.table_row_of_headers(
        ("Verse", "Reading", "Word", "Supplied accent", "WLC writes", "Why")
    )
    rows = [header]
    for s in supplies:
        wlc_cell = hbo(accents_and_letters(s.wlc_word)) if s.wlc_word else "—"
        rows.append(
            H.table_row_of_data(
                (
                    ref_display(s.bcv),
                    s.strand_label,
                    hbo(accents_and_letters(s.mam_word)),
                    s.accent_name,
                    wlc_cell,
                    s.reason,
                )
            )
        )
    return H.table(tuple(rows), {"class": "goerwitz-obs-tree-table"})


def _reading_order_key(s) -> tuple:
    bb = s.bcv[:2]
    chnu, vrnu = (int(p) for p in s.bcv[2:].split(":"))
    # alef strand (taxton/pashut) before bet (elyon/midrashit) within a verse
    return (bb, chnu, vrnu, 0 if s.strand == "alef" else 1)


def render_body_contents(supplies: list) -> tuple[object, ...]:
    sections: list[object] = [*_intro()]
    if supplies:
        sections.append(_table(sorted(supplies, key=_reading_order_key)))
    else:
        sections.append(H.para("No marks were supplied."))
    wrapper = H.div(tuple(sections), {"class": _WIDTH_CLASS})
    return (wrapper,)


def run(args: argparse.Namespace) -> None:
    results = dual_cant_run.detangle_results(args.wlc422_kq_u_dir, args.mam_simple_dir)
    supplies = [s for pr in results for s in pr.supplied_marks]

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(supplies),
        write_ctx=H.WriteCtx(
            title=REPORT_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    print(f"HTML: {html_out} ({len(supplies)} supplied marks)")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
