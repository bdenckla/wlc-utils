from __future__ import annotations

from pathlib import Path

from accgram import ob_data
from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import rtms_ref
from accgram import rtms_report
from accgram import rtmsr_subsets
from accgram import rtmsr_sat
from accgram import rtmsr_verse
from mb_cmn import provenance
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

    error_trees_by_ref = ob_error_context.collect_error_trees_by_ref(
        enriched_oddball_rows,
        goerwitz_out_dir,
    )

    body_contents = _build_body_contents(
        enriched_oddball_rows,
        error_trees_by_ref=error_trees_by_ref,
        main_html_out_path=main_html_out_path,
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


def _build_body_contents(
    enriched_oddball_rows: list[dict[str, object]],
    *,
    error_trees_by_ref: dict[str, ob_error_context.ErrorTree | None],
    main_html_out_path: Path,
) -> tuple[object, ...]:
    sections: list[object] = [
        wlc_utils_html.heading_level_1(_REPORT_HEADING),
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(
            (
                f"These {len(enriched_oddball_rows)} verses did not cause trouble for the Goerwitz accent grammar checker,",
                " but did contain the string “ERROR” in their parse trees."
                "Each section below includes links, WLC verse, SAT rows, and a complete parse tree table.",
            )
        ),
        *_related_pages_contents(main_html_out_path),
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
                error_tree=error_trees_by_ref.get(ref),
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
    overview_name = rtmsr_subsets.overview_html_out_path(main_html_out_path).name
    return (
        wlc_utils_html.heading_level_2("Related pages"),
        wlc_utils_html.unordered_list(
            (
                wlc_utils_html.anchor(
                    "Goerwitz run on WLC",
                    {"href": overview_name},
                ),
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
    error_tree: ob_error_context.ErrorTree | None,
) -> tuple[object, ...]:
    if error_tree is None:
        raise ValueError(
            "Oddball row is missing a parsed ERROR tree; oddballs must include at "
            f"least one ERROR leaf (ref={_row_ref(row)!r})."
        )

    details: list[object] = [
        wlc_utils_html.div(
            (ob_tree_table.render_error_tree_table(error_tree),),
            {"class": "goerwitz-obs-tree-wrap"},
        ),
    ]
    return tuple(details)


def _structured_text_value(row: dict[str, object], key: str) -> object:
    if key == "st-summary":
        derived_summary = rtmsr_sat.derive_summary_from_sat_descriptors(
            row,
            row_ref=_row_ref(row),
            structured_text_lookup=_structured_text_value,
            wlc_tokens=rtmsr_verse.wlc_verse_vels(row),
        )
        return derived_summary or ""

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
