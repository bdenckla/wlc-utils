from __future__ import annotations

from pathlib import Path

from accgram import ob_data
from accgram import ob_error_context
from accgram import rtms_ref
from accgram import rtms_report
from py_html import wlc_utils_html

_GOERWITZ_OBS_WIDTH_CLASS = "goerwitz-tms-width-limited"
_REPORT_TITLE = "Goerwitz Oddballs"
_REPORT_HEADING = "Goerwitz Oddballs"


def oddball_html_out_path(main_html_out_path: Path) -> Path:
    return main_html_out_path.parent / "goerwitz-obs.html"


def write_goerwitz_obs_html_report(
    main_html_out_path: Path,
    enriched_oddball_rows: list[dict[str, object]],
    goerwitz_out_dir: Path,
) -> Path:
    html_out_path = oddball_html_out_path(main_html_out_path)
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    error_paths_by_ref = ob_error_context.collect_error_paths_by_ref(
        enriched_oddball_rows,
        goerwitz_out_dir,
    )

    body_contents = _build_body_contents(
        enriched_oddball_rows,
        error_paths_by_ref=error_paths_by_ref,
        main_html_out_path=main_html_out_path,
    )
    wlc_utils_html.write_html_to_file(
        body_contents=body_contents,
        write_ctx=wlc_utils_html.WriteCtx(
            title=_REPORT_TITLE,
            path=str(html_out_path),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out_path),
    )
    return html_out_path


def _build_body_contents(
    enriched_oddball_rows: list[dict[str, object]],
    *,
    error_paths_by_ref: dict[str, list[ob_error_context.ErrorPath]],
    main_html_out_path: Path,
) -> tuple[object, ...]:
    sections: list[object] = [
        wlc_utils_html.heading_level_1(_REPORT_HEADING),
        *_related_pages_contents(main_html_out_path),
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(
            (
                f"These {len(enriched_oddball_rows)} verses are oddballs from Goerwitz output. ",
                "Each section below includes links, WLC verse, SAT rows, and a compact ERROR hierarchy table.",
            )
        ),
    ]

    for index, row in enumerate(enriched_oddball_rows):
        ref = _row_ref(row)
        bcv = _ref_bcv(ref)
        section_anchor_id = _oddball_anchor_id(bcv)

        sections.extend(
            rtms_report.render_row_section_with_anchor_id(
                row,
                section_anchor_id=section_anchor_id,
                structured_text_lookup=_structured_text_value,
            )
        )
        sections.extend(
            _render_error_context_section(
                row,
                error_paths=error_paths_by_ref.get(ref, []),
            )
        )

        if index + 1 < len(enriched_oddball_rows):
            sections.append(wlc_utils_html.horizontal_rule())

    return (
        wlc_utils_html.div(
            tuple(sections),
            {"class": _GOERWITZ_OBS_WIDTH_CLASS},
        ),
    )


def _related_pages_contents(main_html_out_path: Path) -> tuple[object, ...]:
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor(
                    "Goerwitz troublemakers",
                    {"href": main_html_out_path.name},
                ),
            )
        ),
    )


def _render_error_context_section(
    row: dict[str, object],
    *,
    error_paths: list[ob_error_context.ErrorPath],
) -> tuple[object, ...]:
    output_file = row.get("output_file")
    output_file_text = output_file if isinstance(output_file, str) else ""

    if not error_paths:
        return (
            wlc_utils_html.heading_level_3("ERROR hierarchy"),
            wlc_utils_html.para(
                "No ERROR leaf was found for this ref in the parsed Goerwitz output file.",
                {"class": "goerwitz-obs-error-note"},
            ),
        )

    max_depth = ob_error_context.max_error_path_depth(error_paths)
    headers = tuple([*(f"Depth {i}" for i in range(max_depth)), "Leaf"])

    rows: list[object] = [wlc_utils_html.table_row_of_headers(headers)]
    for error_path in error_paths:
        labels = error_path["path_labels"]
        leaf = error_path["leaf"]
        row_values = [labels[i] if i < len(labels) else "" for i in range(max_depth)]
        row_values.append(leaf)

        tdattrs: list[dict[str, str] | None] = [None] * max_depth
        tdattrs.append(
            {"class": "goerwitz-obs-error-cell"} if "ERROR" in leaf else None
        )
        rows.append(
            wlc_utils_html.table_row_of_data(
                tuple(row_values),
                tdattrs=tuple(tdattrs),
            )
        )

    details: list[object] = [
        wlc_utils_html.heading_level_3("ERROR hierarchy"),
        wlc_utils_html.para(
            (
                "Goerwitz output file: ",
                wlc_utils_html.code(output_file_text),
            ),
            {"class": "goerwitz-obs-error-note"},
        ),
        wlc_utils_html.table(
            tuple(rows),
            {"class": "goerwitz-obs-error-table"},
        ),
    ]
    return tuple(details)


def _structured_text_value(row: dict[str, object], key: str) -> object:
    structured_text = ob_data.get_structured_text().get(_row_ref(row))
    if not isinstance(structured_text, dict):
        return None
    return structured_text.get(key)


def _row_ref(row: dict[str, object]) -> str:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Oddball row is missing non-empty string field 'ref'")
    return ref.strip()


def _ref_bcv(ref: str) -> str:
    bb, chnu, vrnu = rtms_ref.parse_ref(ref, row_kind="oddball")
    return rtms_ref.to_compact_bcv(bb, chnu, vrnu)


def _oddball_anchor_id(bcv: str) -> str:
    return f"ob{bcv.replace(':', 'v')}"
