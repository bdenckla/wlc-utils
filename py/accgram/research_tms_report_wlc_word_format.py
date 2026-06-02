from __future__ import annotations

from typing import Callable


WLC_WORD_NOTES_LABEL = "wlc_word.notes"


def build_wlc_word_rows(wlc_word_text: str, wlc_word_notes: list[str]) -> list[tuple[str, str]]:
    if wlc_word_notes:
        return [
            ("wlc_word.hbo", wlc_word_text),
            (WLC_WORD_NOTES_LABEL, render_note_values(wlc_word_notes)),
        ]

    return [("wlc_word", wlc_word_text)]


def collect_wlc_word_bracket_notes(
    tokens: list[object],
    wlc_word: str | None,
    *,
    render_sat_value: Callable[[object], str],
) -> list[str]:
    if not wlc_word:
        return []

    notes: list[str] = []
    for token in tokens:
        if not isinstance(token, dict):
            continue
        if token.get("word") != wlc_word:
            continue
        token_notes = token.get("notes")
        if token_notes is None:
            continue
        rendered_notes = render_sat_value(token_notes).strip()
        if rendered_notes:
            notes.append(rendered_notes)

    # Preserve order while dropping duplicates.
    return list(dict.fromkeys(notes))


def render_note_values(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    return f"[{' | '.join(values)}]"


def is_redundant_wlc_word_bracket_notes_row(
    bracket_notes: list[str],
    *,
    wlc_word: str | None,
    wlc_word_notes: list[str],
) -> bool:
    if not wlc_word or not wlc_word_notes:
        return False

    wlc_word_bracket_notes = {f"{wlc_word}: {note}" for note in wlc_word_notes}
    return bool(bracket_notes) and set(bracket_notes).issubset(wlc_word_bracket_notes)