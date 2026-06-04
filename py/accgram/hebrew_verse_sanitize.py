from __future__ import annotations

_HEBREW_LETTER_START = ord("\u05d0")
_HEBREW_LETTER_END = ord("\u05ea")
_HEBREW_ACCENT_START = ord("\u0591")
_HEBREW_ACCENT_END = ord("\u05af")
_HEBREW_MAQAF = "\u05be"
_HEBREW_METEG = "\u05bd"
_HEBREW_PASEQ = "\u05c0"
_HEBREW_SOF_PASUQ = "\u05c3"
_HEBREW_TELISHA_GEDOLA = "\u05a0"


def sanitize_verse_text_payload(
    payload: object,
    *,
    remove_duplicate_telisha_gedola: bool = False,
    preserve_all_meteg: bool = False,
) -> object:
    mutable = _deep_clone_jsonish(payload)
    slots: list[tuple[list[object] | dict[str, object], int | str]] = []
    _collect_hebrew_string_slots(mutable, slots)

    # Preserve Unicode METEG only on the final Hebrew token in the verse payload.
    last_hebrew_slot: tuple[list[object] | dict[str, object], int | str] | None = None
    for container, key in slots:
        value = container[key]
        if isinstance(value, str) and _has_hebrew_letter(value):
            last_hebrew_slot = (container, key)

    for container, key in slots:
        value = container[key]
        if not isinstance(value, str):
            continue
        keep_last_meteg = (
            last_hebrew_slot is not None
            and container is last_hebrew_slot[0]
            and key == last_hebrew_slot[1]
        )
        keep_all_meteg = preserve_all_meteg and _has_hebrew_letter(value)
        container[key] = _sanitize_hebrew_token(
            value,
            keep_last_meteg=keep_last_meteg,
            keep_all_meteg=keep_all_meteg,
            remove_duplicate_telisha_gedola=remove_duplicate_telisha_gedola,
        )

    return mutable


def _deep_clone_jsonish(value: object) -> object:
    if isinstance(value, dict):
        return {k: _deep_clone_jsonish(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deep_clone_jsonish(v) for v in value]
    return value


def _collect_hebrew_string_slots(
    value: object,
    out: list[tuple[list[object] | dict[str, object], int | str]],
) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str):
                if _has_hebrew_block_char(child):
                    out.append((value, key))
            else:
                _collect_hebrew_string_slots(child, out)
        return

    if isinstance(value, list):
        for idx, child in enumerate(value):
            if isinstance(child, str):
                if _has_hebrew_block_char(child):
                    out.append((value, idx))
            else:
                _collect_hebrew_string_slots(child, out)


def _has_hebrew_block_char(text: str) -> bool:
    return any(0x0590 <= ord(ch) <= 0x05FF for ch in text)


def _has_hebrew_letter(text: str) -> bool:
    return any(_HEBREW_LETTER_START <= ord(ch) <= _HEBREW_LETTER_END for ch in text)


def _sanitize_hebrew_token(
    text: str,
    *,
    keep_last_meteg: bool,
    keep_all_meteg: bool,
    remove_duplicate_telisha_gedola: bool,
) -> str:
    last_meteg_idx = text.rfind(_HEBREW_METEG) if keep_last_meteg else -1
    out_chars: list[str] = []
    for idx, ch in enumerate(text):
        codepoint = ord(ch)
        if _HEBREW_LETTER_START <= codepoint <= _HEBREW_LETTER_END:
            out_chars.append(ch)
            continue
        if _HEBREW_ACCENT_START <= codepoint <= _HEBREW_ACCENT_END:
            out_chars.append(ch)
            continue
        if ch in {_HEBREW_MAQAF, _HEBREW_PASEQ, _HEBREW_SOF_PASUQ}:
            out_chars.append(ch)
            continue
        if ch == _HEBREW_METEG and (keep_all_meteg or idx == last_meteg_idx):
            out_chars.append(ch)
    sanitized = "".join(out_chars)
    if remove_duplicate_telisha_gedola:
        sanitized = _drop_duplicate_telisha_gedola(sanitized)
    return sanitized


def _drop_duplicate_telisha_gedola(text: str) -> str:
    out_chars: list[str] = []
    seen_in_token = False
    for ch in text:
        if ch in {_HEBREW_MAQAF, _HEBREW_PASEQ, _HEBREW_SOF_PASUQ}:
            seen_in_token = False
            out_chars.append(ch)
            continue
        if ch == _HEBREW_TELISHA_GEDOLA:
            if seen_in_token:
                continue
            seen_in_token = True
            out_chars.append(ch)
            continue
        if _HEBREW_LETTER_START <= ord(ch) <= _HEBREW_LETTER_END:
            out_chars.append(ch)
            continue
        out_chars.append(ch)
    return "".join(out_chars)
