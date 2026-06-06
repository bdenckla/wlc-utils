from __future__ import annotations

from pathlib import Path

from accgram import rtms_report
from accgram import rtmsr_intro
from accgram import rtmsr_subsets
from mb_cmn import provenance
from py_html import wlc_utils_html

_REPORT_TITLE = "Goerwitz Run on WLC"
_REPORT_HEADING = "Goerwitz Run on WLC"
_WIDTH_CLASS = "goerwitz-tms-width-limited"


def write_goerwitz_overview_html_report(main_html_out_path: Path) -> Path:
    html_out_path = rtmsr_subsets.overview_html_out_path(main_html_out_path)
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    oddballs_name = main_html_out_path.parent.joinpath("goerwitz-obs.html").name
    body_contents = (
        wlc_utils_html.div(
            (
                wlc_utils_html.heading_level_1(_REPORT_HEADING),
                wlc_utils_html.para(
                    (
                        "My analysis of the output of the Goerwitz accent grammar checker run on WLC 4.22 is divided into two parts:"
                    )
                ),
                wlc_utils_html.unordered_list(
                    (
                        wlc_utils_html.anchor(
                            "Goerwitz troublemakers",
                            {"href": main_html_out_path.name},
                        ),
                        wlc_utils_html.anchor(
                            "Goerwitz oddballs",
                            {"href": oddballs_name},
                        ),
                    )
                ),
                *rtmsr_intro.checker_article_citation_contents(),
            ),
            {"class": _WIDTH_CLASS},
        ),
    )

    wlc_utils_html.write_html_to_file(
        body_contents=body_contents,
        write_ctx=wlc_utils_html.WriteCtx(
            title=_REPORT_TITLE,
            path=str(html_out_path),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out_path),
    )
    return html_out_path