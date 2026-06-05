from __future__ import annotations

from pathlib import Path

from py_html import wlc_utils_html

_MISSING_SOF_PASUQ_TOKENS = (
    "silluq-no_sof_pasuq",
    "silluq-pasoleg",
)
_MISSING_SOF_PASUQ_YES_LABEL = "missing sof pasuq: yes"
_MISSING_SOF_PASUQ_NO_LABEL = "missing sof pasuq: no"

_MSP_Y_HTML_NAME = "goerwitz-tms-msp-y.html"
_MSP_N_HTML_NAME = "goerwitz-tms-msp-n.html"


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
    yes_name = missing_sof_pasuq_yes_html_out_path(main_html_out_path).name
    no_name = missing_sof_pasuq_no_html_out_path(main_html_out_path).name
    return (
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
    main_name = main_html_out_path.name
    no_name = missing_sof_pasuq_no_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor("main page", {"href": main_name}),
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_NO_LABEL, {"href": no_name}),
            )
        ),
    )


def build_msp_no_related_pages_top_contents(
    main_html_out_path: Path,
) -> tuple[object, ...]:
    main_name = main_html_out_path.name
    yes_name = missing_sof_pasuq_yes_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor("main page", {"href": main_name}),
                wlc_utils_html.anchor(_MISSING_SOF_PASUQ_YES_LABEL, {"href": yes_name}),
            )
        ),
    )


def _row_is_missing_sof_pasuq_yes(row: dict[str, object]) -> bool:
    structured_text = row.get("structured_text")
    if not isinstance(structured_text, dict):
        return False

    assessment = structured_text.get("assessment")
    if not isinstance(assessment, dict):
        return False

    return any(
        _assessment_value_contains_missing_sof_pasuq_marker(value)
        for value in assessment.values()
    )


def _assessment_value_contains_missing_sof_pasuq_marker(value: object) -> bool:
    if isinstance(value, str):
        return any(token in value for token in _MISSING_SOF_PASUQ_TOKENS)

    if isinstance(value, list):
        return any(
            _assessment_value_contains_missing_sof_pasuq_marker(item) for item in value
        )

    if isinstance(value, dict):
        return any(
            _assessment_value_contains_missing_sof_pasuq_marker(item)
            for item in value.values()
        )

    return False
