from __future__ import annotations

import json
import re
from collections.abc import Callable

from accgram import rtms_meteg_witness
from accgram import rtms_report_bracket_notes
from accgram import rtms_report_diff_format
from accgram import rtms_report_sat_notes_column
from accgram import rtms_report_wlc_word_format
from accgram.rtms_assessment_auto import try_auto_assessment_descriptor
from accgram import tm_sanity
from py_html import wlc_utils_html

_ASSESSMENT_KEYS = ("manuscript", "bhs", "wlc", "uxlc", "mam")
_WLC_FOCUS_ROW_KEYS = {"wlc_focus"}
_SAT_A_KEY_MERGE_TARGETS: dict[str, str] = {
    "a.wlc": "wlc_focus",
    "a.uxlc": "diff_wlc_uxlc",
    "a.mam": "diff_wlc_mam",
}
_SAT_ROW_SUPPRESSIONS_BY_REF: dict[str, set[str]] = {
    "1k 16:33": {"diff_wlc_uxlc[1]"},
    "mi 2:7": {"diff_wlc_mam[2]"},
}

# Internal SAT row shape: (value_cell, middle_description_cell, key_cell).
SatRow = tuple[str, str, str]
StructuredTextLookup = Callable[[dict[str, object], str], object]


def render_sat_table(
    row: dict[str, object],
    *,
    row_ref: str,
    structured_text_lookup: StructuredTextLookup,
    wlc_tokens: list[object],
) -> object:
    wlc_focus = structured_text_lookup(row, "wlc_focus")
    wlc_focus_str = (
        _normalize_whitespace(wlc_focus) if isinstance(wlc_focus, str) else ""
    )
    wlc_focus_notes = (
        rtms_report_wlc_word_format.collect_wlc_word_bracket_notes(
            wlc_tokens,
            wlc_focus_str or None,
            render_sat_value=render_sat_value,
        )
    )
    sat_notes_by_key: dict[str, str] = {}
    rendered_wlc_focus_notes = rtms_report_wlc_word_format.render_note_values(
        wlc_focus_notes
    )
    if rendered_wlc_focus_notes:
        sat_notes_by_key["wlc_focus"] = rendered_wlc_focus_notes

    sat_rows: list[SatRow] = [_sat_row(key="wlc_focus", value=wlc_focus_str)]
    sat_rows.extend(
        [
            _sat_row(key=label, value=value)
            for label, value in rtms_report_diff_format.normalize_diff_rows(
                "diff_wlc_uxlc",
                row.get("diff_wlc_uxlc"),
                row=row,
                rhs_key="uxlc",
                render_sat_value=render_sat_value,
                structured_text_lookup=structured_text_lookup,
            )
        ]
    )
    sat_rows.extend(
        [
            _sat_row(key=label, value=value)
            for label, value in rtms_report_diff_format.normalize_diff_rows(
                "diff_wlc_mam",
                row.get("diff_wlc_mam"),
                row=row,
                rhs_key="mam_simple",
                render_sat_value=render_sat_value,
                structured_text_lookup=structured_text_lookup,
            )
        ]
    )

    sat_rows.extend(
        _assessment_sat_rows(
            row,
            structured_text_lookup=structured_text_lookup,
            existing_sat_rows=sat_rows,
            wlc_focus=wlc_focus_str or None,
        )
    )
    sat_rows = _apply_sat_row_suppressions(row_ref, sat_rows)
    sat_rows = _merge_assessment_rows_into_sat_middle_column(sat_rows, row=row)
    sat_rows = _move_assessment_values_to_sat_middle_column(sat_rows)
    notes_column_plan = (
        rtms_report_sat_notes_column.build_sat_notes_column_plan(
            sat_rows,
            notes_by_key=sat_notes_by_key,
        )
    )

    table_rows: list[object] = []
    for value, notes_value, middle_description, key in notes_column_plan.render_rows:
        if notes_column_plan.include_notes_column:
            table_rows.append(
                wlc_utils_html.table_row_of_data(
                    (
                        rtms_report_bracket_notes.annotate_bracket_note_tokens(
                            value
                        ),
                        rtms_report_bracket_notes.annotate_bracket_note_tokens(
                            notes_value
                        ),
                        middle_description,
                        key,
                    ),
                    tdattrs=(
                        _sat_value_cell_attr(key, value),
                        rtms_report_sat_notes_column.notes_cell_attr(
                            notes_column_plan.include_notes_column
                        ),
                        None,
                        None,
                    ),
                )
            )
            continue

        table_rows.append(
            wlc_utils_html.table_row_of_data(
                (
                    rtms_report_bracket_notes.annotate_bracket_note_tokens(
                        value
                    ),
                    middle_description,
                    key,
                ),
                tdattrs=(_sat_value_cell_attr(key, value), None, None),
            )
        )

    return wlc_utils_html.table(
        tuple(table_rows),
        {"class": "goerwitz-tms-sat"},
    )


def render_sat_value(value: object) -> str:
    if isinstance(value, str):
        return value

    if value is None:
        return ""

    if isinstance(value, list):
        rendered_items = [render_sat_value(item) for item in value if item is not None]
        rendered_items = [item for item in rendered_items if item]
        if not rendered_items:
            return "[]"
        return f"[{' | '.join(rendered_items)}]"

    if isinstance(value, dict):
        token_like = _render_token_like_dict(value)
        if token_like is not None:
            return token_like

        parts = []
        for key, val in value.items():
            rendered = render_sat_value(val)
            parts.append(f"{key}: {rendered}" if rendered else str(key))
        return "; ".join(parts)

    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value)


def _sat_value_cell_attr(label: str, value: str) -> dict[str, str] | None:
    if (
        label in _WLC_FOCUS_ROW_KEYS
        and rtms_report_diff_format.contains_hebrew(value)
    ):
        return {"lang": "hbo", "dir": "rtl"}

    if label.startswith(
        "diff_wlc_"
    ) and rtms_report_diff_format.is_plain_hebrew_string(value):
        return {"lang": "hbo", "dir": "rtl"}

    return None


def _assessment_sat_rows(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
    existing_sat_rows: list[SatRow],
    wlc_focus: str | None,
) -> list[SatRow]:
    rows: list[SatRow] = []

    assessment_values: dict[str, object] = {}
    assessment = structured_text_lookup(row, "assessment")
    if isinstance(assessment, dict):
        assessment_values.update(assessment)

    for key in ("wlc", "uxlc", "mam"):
        if key in assessment_values:
            continue
        if not _sat_html_wants_assessment_key(existing_sat_rows, assessment_key=key):
            continue
        descriptor = try_auto_assessment_descriptor(
            assessment_key=key,
            enriched_row=row,
            wlc_focus=wlc_focus,
        )
        if isinstance(descriptor, str) and descriptor.strip():
            assessment_values[key] = descriptor

    for key in _ASSESSMENT_KEYS:
        value = assessment_values.get(key)
        if value is None:
            continue
        rows.append(_sat_row(key=f"a.{key}", value=render_sat_value(value)))

    return rows


def _sat_html_wants_assessment_key(
    existing_sat_rows: list[SatRow], *, assessment_key: str
) -> bool:
    merge_target_key = _sat_merge_target_key_for_assessment_key(f"a.{assessment_key}")
    if merge_target_key is None:
        return False
    return bool(
        _find_sat_merge_target_row_indices(
            existing_sat_rows,
            merge_target_base_key=merge_target_key,
        )
    )


def _apply_sat_row_suppressions(ref: str, rows: list[SatRow]) -> list[SatRow]:
    suppressed_labels = _SAT_ROW_SUPPRESSIONS_BY_REF.get(ref)
    if not suppressed_labels:
        return rows

    return [
        sat_row for sat_row in rows if _sat_row_key(sat_row) not in suppressed_labels
    ]


def _sat_row(*, key: str, value: str, middle_description: str = "") -> SatRow:
    return (value, middle_description, key)


def _sat_row_key(row: SatRow) -> str:
    return row[2]


def _move_assessment_values_to_sat_middle_column(rows: list[SatRow]) -> list[SatRow]:
    moved_rows: list[SatRow] = []
    for value, middle_description, key in rows:
        if key.startswith("a.") and value:
            moved_rows.append(
                _sat_row(
                    key=key,
                    value="",
                    middle_description=middle_description or value,
                )
            )
        else:
            moved_rows.append((value, middle_description, key))

    return moved_rows


def _sat_merge_target_key_for_assessment_key(key: str) -> str | None:
    return _SAT_A_KEY_MERGE_TARGETS.get(key)


def _sat_row_merge_target_priority(
    *, row_key: str, merge_target_base_key: str
) -> int | None:
    # Prefer the direct key match, then indexed keys.
    if row_key == merge_target_base_key:
        return 0
    if re.fullmatch(rf"{re.escape(merge_target_base_key)}\[\d+\]", row_key):
        return 1
    return None


def _merge_assessment_rows_into_sat_middle_column(
    rows: list[SatRow],
    *,
    row: dict[str, object],
) -> list[SatRow]:
    merged_rows = list(rows)
    consumed_indices: set[int] = set()

    for row_idx, sat_row in enumerate(rows):
        row_key = _sat_row_key(sat_row)
        merge_target_base_key = _sat_merge_target_key_for_assessment_key(row_key)
        if merge_target_base_key is None:
            continue

        target_indices = _find_sat_merge_target_row_indices(
            merged_rows,
            merge_target_base_key=merge_target_base_key,
        )
        if not target_indices:
            continue

        assessment_value, _assessment_middle, _assessment_key = sat_row
        merge_target_idx: int | None = None
        for target_idx in target_indices:
            target_value, _target_middle, _target_key = merged_rows[target_idx]
            if (
                _sat_assessment_value_describes_target_value(
                    assessment_value=assessment_value,
                    target_value=target_value,
                )
                is True
            ):
                merge_target_idx = target_idx
                break

        if merge_target_idx is None:
            continue

        target_value, _target_middle, target_key = merged_rows[merge_target_idx]
        target_value = _maybe_restore_value_from_witness(
            row=row,
            target_key=target_key,
            target_value=target_value,
            assessment_value=assessment_value,
        )

        merged_rows[merge_target_idx] = _sat_row(
            key=target_key,
            value=target_value,
            middle_description=assessment_value,
        )
        consumed_indices.add(row_idx)

    if not consumed_indices:
        return merged_rows

    return [
        sat_row
        for idx, sat_row in enumerate(merged_rows)
        if idx not in consumed_indices
    ]


def _find_sat_merge_target_row_indices(
    rows: list[SatRow], *, merge_target_base_key: str
) -> list[int]:
    prioritized_indices: list[tuple[int, int]] = []
    for idx, sat_row in enumerate(rows):
        priority = _sat_row_merge_target_priority(
            row_key=_sat_row_key(sat_row),
            merge_target_base_key=merge_target_base_key,
        )
        if priority is None:
            continue
        prioritized_indices.append((priority, idx))

    prioritized_indices.sort()
    return [idx for _priority, idx in prioritized_indices]


def _sat_assessment_value_describes_target_value(
    *, assessment_value: str, target_value: str
) -> bool | None:
    assessment_text = assessment_value.strip()
    target_text = target_value.strip()
    if not assessment_text or not target_text:
        return None

    if not rtms_report_diff_format.is_plain_hebrew_string(target_text):
        return None

    try:
        return tm_sanity.assessment_descriptor_matches_hebrew_token(
            assessment_descriptor=assessment_text,
            hebrew_token=target_text,
        )
    except (AssertionError, ValueError):
        # Descriptor inference failures are indeterminate for SAT merge purposes.
        return None


def _maybe_restore_value_from_witness(
    *,
    row: dict[str, object],
    target_key: str,
    target_value: str,
    assessment_value: str,
) -> str:
    normalized_assessment = assessment_value.strip()
    if normalized_assessment not in {
        "meteg-space",
        "meteg-maqaf",
        "meteg-meteg-maqaf",
    }:
        return target_value

    if not rtms_report_diff_format.is_plain_hebrew_string(target_value):
        return target_value

    side_key = _witness_side_key_for_sat_row_key(target_key)
    if side_key is None:
        return target_value

    source_witness_payload = rtms_meteg_witness.witness_payload_for_side(
        row,
        side_key=side_key,
    )
    if source_witness_payload is None:
        return target_value

    witness_token = rtms_meteg_witness.match_unique_witness_token(
        sanitized_token=target_value,
        source_witness_payload=source_witness_payload,
    )
    if not isinstance(witness_token, str) or not witness_token.strip():
        return target_value

    if not rtms_meteg_witness.token_has_meteg(witness_token):
        return target_value

    has_maqaf = rtms_meteg_witness.token_has_maqaf(witness_token)
    if normalized_assessment == "meteg-space" and has_maqaf:
        return target_value
    if normalized_assessment in {"meteg-maqaf", "meteg-meteg-maqaf"} and not has_maqaf:
        return target_value

    return witness_token


def _witness_side_key_for_sat_row_key(row_key: str) -> str | None:
    base_key = row_key
    bracket_idx = base_key.find("[")
    if bracket_idx >= 0:
        base_key = base_key[:bracket_idx]

    if base_key == "diff_wlc_uxlc":
        return "uxlc"
    if base_key == "diff_wlc_mam":
        return "mam_simple"
    return None


def _render_token_like_dict(value: dict[str, object]) -> str | None:
    token_text: str | None = None
    if isinstance(value.get("word"), str):
        token_text = str(value["word"])
    elif isinstance(value.get("text"), str):
        token_text = str(value["text"])

    if token_text is None:
        return None

    note_key: str | None = None
    if "notes" in value:
        note_key = "notes"
    elif "note" in value:
        note_key = "note"

    out = token_text
    if note_key is not None:
        note_text = render_sat_value(value.get(note_key))
        if note_text:
            out = f"{out} ({note_key}: {note_text})"

    extras: list[str] = []
    for key, val in value.items():
        if key in {"word", "text", "notes", "note"}:
            continue
        rendered = render_sat_value(val)
        extras.append(f"{key}: {rendered}" if rendered else str(key))

    if extras:
        out = f"{out} ({'; '.join(extras)})"

    return out


def _normalize_whitespace(value: str | None) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())
