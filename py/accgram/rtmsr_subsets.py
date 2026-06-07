from __future__ import annotations

from pathlib import Path

from accgram import rtms_missing_sof_pasuq_descriptions
from py_html import wlc_utils_html

_MISSING_SOF_PASUQ_YES_LABEL = "troublemakers missing sof pasuq (msp-y)"
_MISSING_SOF_PASUQ_NO_LABEL = "troublemakers not missing sof pasuq (msp-n)"
_OVERVIEW_LABEL = "Goerwitz run on WLC 4.22"

_MSP_Y_HTML_NAME = "goerwitz-tms-msp-y.html"
_MSP_N_HTML_NAME = "goerwitz-tms-msp-n.html"
_OVERVIEW_HTML_NAME = "goerwitz.html"


def overview_html_out_path(main_html_out_path: Path) -> Path:
    return main_html_out_path.parent / _OVERVIEW_HTML_NAME


def missing_sof_pasuq_yes_html_out_path(main_html_out_path: Path) -> Path:
    return main_html_out_path.parent / _MSP_Y_HTML_NAME


def missing_sof_pasuq_no_html_out_path(main_html_out_path: Path) -> Path:
    return main_html_out_path.parent / _MSP_N_HTML_NAME


def filter_missing_sof_pasuq_yes_rows(
    enriched_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [row for row in enriched_rows if _row_is_missing_sof_pasuq_yes(row)]


def filter_missing_sof_pasuq_no_rows(
    enriched_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return [row for row in enriched_rows if not _row_is_missing_sof_pasuq_yes(row)]


def build_main_subsets_top_contents(main_html_out_path: Path) -> tuple[object, ...]:
    overview_name = overview_html_out_path(main_html_out_path).name
    yes_name = missing_sof_pasuq_yes_html_out_path(main_html_out_path).name
    no_name = missing_sof_pasuq_no_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (wlc_utils_html.anchor(_OVERVIEW_LABEL, {"href": overview_name}),)
        ),
        wlc_utils_html.heading_level_2("Subsets"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_YES_LABEL, {"href": yes_name}),
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_NO_LABEL, {"href": no_name}),
            )
        ),
    )


def build_msp_yes_related_pages_top_contents(
    main_html_out_path: Path,
) -> tuple[object, ...]:
    overview_name = overview_html_out_path(main_html_out_path).name
    main_name = main_html_out_path.name
    no_name = missing_sof_pasuq_no_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor(_OVERVIEW_LABEL, {"href": overview_name}),
                wlc_utils_html.anchor("main troublemakers page", {"href": main_name}),
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_NO_LABEL, {"href": no_name}),
            )
        ),
    )


def build_msp_no_related_pages_top_contents(
    main_html_out_path: Path,
) -> tuple[object, ...]:
    overview_name = overview_html_out_path(main_html_out_path).name
    main_name = main_html_out_path.name
    yes_name = missing_sof_pasuq_yes_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor(_OVERVIEW_LABEL, {"href": overview_name}),
                wlc_utils_html.anchor("main troublemakers page", {"href": main_name}),
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_YES_LABEL, {"href": yes_name}),
            )
        ),
    )


def _row_is_missing_sof_pasuq_yes(row: dict[str, object]) -> bool:
    return rtms_missing_sof_pasuq_descriptions.row_is_missing_sof_pasuq_yes(row)
