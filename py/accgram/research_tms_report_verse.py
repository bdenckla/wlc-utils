from __future__ import annotations

from collections.abc import Callable

from accgram import research_tms_report_sat
from py_html import wlc_utils_html

_GOERWITZ_TMS_VERSE_CLASS = "goerwitz-tms-verse"
_GOERWITZ_TMS_FOCUS_HIGHLIGHT_CLASS = "goerwitz-tms-focus-highlight"

StructuredTextLookup = Callable[[dict[str, object], str], object]


def render_wlc_verse_paragraph(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> object:
    verse_text = _wlc_verse_text(row)
    wlc_focus = structured_text_lookup(row, "wlc_focus")
    wlc_focus_str = wlc_focus if isinstance(wlc_focus, str) else None
    contents = _wlc_verse_contents_with_highlight(
        verse_text=verse_text,
        wlc_focus=wlc_focus_str,
    )
    return wlc_utils_html.para(
        contents,
        {
            "class": _GOERWITZ_TMS_VERSE_CLASS,
            "lang": "hbo",
            "dir": "rtl",
        },
    )


def wlc_verse_vels(row: dict[str, object]) -> list[object]:
    wlc_verse = row.get("wlc422_kq_u_verse")
    if not isinstance(wlc_verse, dict):
        return []
    vels = wlc_verse.get("vels")
    if not isinstance(vels, list):
        return []
    return vels


def _wlc_verse_contents_with_highlight(
    *, verse_text: str, wlc_focus: str | None
) -> object:
    normalized_focus = _normalize_whitespace(wlc_focus)
    if not normalized_focus:
        return verse_text

    before_focus, focus_text, after_focus = _split_unique_focus_by_tokens(
        verse_text=verse_text,
        wlc_focus=normalized_focus,
    )
    if focus_text is None:
        return verse_text

    contents: list[object] = []
    if before_focus:
        contents.append(f"{before_focus} ")
    contents.append(
        wlc_utils_html.span(
            focus_text,
            {"class": _GOERWITZ_TMS_FOCUS_HIGHLIGHT_CLASS},
        )
    )
    if after_focus:
        contents.append(f" {after_focus}")

    if len(contents) == 1:
        return contents[0]
    return tuple(contents)


def _split_unique_focus_by_tokens(
    *, verse_text: str, wlc_focus: str
) -> tuple[str, str | None, str]:
    verse_tokens = verse_text.split()
    focus_tokens = wlc_focus.split()
    if not verse_tokens or not focus_tokens:
        return verse_text, None, ""

    if len(focus_tokens) > len(verse_tokens):
        return verse_text, None, ""

    match_indexes = [
        start
        for start in range(len(verse_tokens) - len(focus_tokens) + 1)
        if verse_tokens[start : start + len(focus_tokens)] == focus_tokens
    ]
    if len(match_indexes) != 1:
        return verse_text, None, ""

    start = match_indexes[0]
    end = start + len(focus_tokens)
    before_focus = " ".join(verse_tokens[:start])
    focus_text = " ".join(verse_tokens[start:end])
    after_focus = " ".join(verse_tokens[end:])
    return before_focus, focus_text, after_focus


def _normalize_whitespace(value: str | None) -> str:
    if not isinstance(value, str):
        return ""
    return " ".join(value.split())


def _wlc_verse_text(row: dict[str, object]) -> str:
    tokens = wlc_verse_vels(row)
    text_parts = [_token_text(token) for token in tokens]
    compact = " ".join(part for part in text_parts if part)
    return " ".join(compact.split())


def _token_text(token: object) -> str:
    if isinstance(token, str):
        return token

    if isinstance(token, dict):
        word = token.get("word")
        if isinstance(word, str):
            return word

        text = token.get("text")
        if isinstance(text, str):
            return text

    return research_tms_report_sat.render_sat_value(token)
