from __future__ import annotations

from typing import Callable


def contains_hebrew(text: str) -> bool:
    return any("\u0590" <= char <= "\u05FF" for char in text)


def is_plain_hebrew_string(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    for char in stripped:
        if char.isspace():
            continue
        if "\u0590" <= char <= "\u05FF":
            continue
        return False

    return True


def normalize_diff_rows(
    label: str,
    diff_value: object,
    *,
    row: dict[str, object],
    rhs_key: str,
    render_sat_value: Callable[[object], str],
    structured_text_lookup: Callable[[dict[str, object], str], object],
) -> list[tuple[str, str]]:
    entries = _as_nonempty_list(diff_value)
    rows: list[tuple[str, str]] = []
    for idx, entry in enumerate(entries, start=1):
        row_label = label if len(entries) == 1 else f"{label}[{idx}]"

        split_rows = _split_note_bearing_diff_rows(
            row_label,
            label=label,
            entry=entry,
            render_sat_value=render_sat_value,
        )
        if split_rows is not None:
            rows.extend(split_rows)
            continue

        rows.append(
            (
                row_label,
                _render_diff_entry_value(
                    entry,
                    row=row,
                    rhs_key=rhs_key,
                    render_sat_value=render_sat_value,
                    structured_text_lookup=structured_text_lookup,
                ),
            )
        )
    return rows


def _split_note_bearing_diff_rows(
    row_label: str,
    *,
    label: str,
    entry: object,
    render_sat_value: Callable[[object], str],
) -> list[tuple[str, str]] | None:
    if label != "diff_wlc_uxlc":
        return None
    if not isinstance(entry, dict):
        return None

    uxlc_side = entry.get("uxlc")
    hbo_text, note_text = _extract_token_text_and_note(uxlc_side, render_sat_value=render_sat_value)
    if not hbo_text or not note_text:
        return None
    if not contains_hebrew(hbo_text):
        return None

    return [
        (f"{row_label}.hbo", hbo_text),
        (f"{row_label}.note", note_text),
    ]


def _extract_token_text_and_note(
    value: object,
    *,
    render_sat_value: Callable[[object], str],
) -> tuple[str | None, str | None]:
    if not isinstance(value, dict):
        return None, None

    token_text: str | None = None
    if isinstance(value.get("text"), str):
        token_text = value["text"].strip()
    elif isinstance(value.get("word"), str):
        token_text = value["word"].strip()

    note_payload = value.get("note")
    if note_payload is None:
        note_payload = value.get("notes")

    note_text = render_sat_value(note_payload).strip()
    if not token_text or not note_text:
        return None, None

    return token_text, note_text


def _render_diff_entry_value(
    entry: object,
    *,
    row: dict[str, object],
    rhs_key: str,
    render_sat_value: Callable[[object], str],
    structured_text_lookup: Callable[[dict[str, object], str], object],
) -> str:
    if not isinstance(entry, dict):
        return render_sat_value(entry)

    if "wlc422" not in entry or rhs_key not in entry:
        return render_sat_value(entry)

    wlc_focus = structured_text_lookup(row, "wlc_focus")
    if not isinstance(wlc_focus, str):
        return render_sat_value(entry)

    wlc_side = render_sat_value(entry.get("wlc422"))
    rhs_side = render_sat_value(entry.get(rhs_key))
    if wlc_side == wlc_focus:
        return rhs_side

    return render_sat_value(entry)


def _as_nonempty_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item is not None]
    return [value]
