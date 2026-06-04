from __future__ import annotations

import re

from mb_cmn import hebrew_accents as ha
from mb_diff_mpu.describe_diff import LETTER_NAMES

_HEBREW_LETTER_START = ord("\u05d0")
_HEBREW_LETTER_END = ord("\u05ea")
_HEBREW_ACCENT_START = ord("\u0591")
_HEBREW_ACCENT_END = ord("\u05af")
_HEBREW_MAQAF = "\u05be"
_HEBREW_PASEQ = "\u05c0"
_HEBREW_SOF_PASUQ = "\u05c3"

_ACCENT_TO_DESCRIPTOR = {
    ha.ATN: "etnaxta",
    ha.MUN: "munax",
    ha.TEV: "tevir",
    ha.TIP: "tipexa",
    ha.MAH: "mahapakh",
    ha.MER: "merkha",
    ha.DAR: "darga",
}
_SIMPLE_ACCENT_DESCRIPTORS = frozenset(_ACCENT_TO_DESCRIPTOR.values())
_OVER_ACCENT_TO_PREFIX = {
    ha.PASH: "pashta on ",
    ha.QOM: "qadma on ",
}
_NO_DESCRIPTOR_EXCEPTIONS = {
    "טוב֖ה",
    "ישראל֘",
}


def sanitize_word_for_change_match(text: str) -> str:
    out_chars: list[str] = []
    for ch in text:
        cp = ord(ch)
        if _HEBREW_LETTER_START <= cp <= _HEBREW_LETTER_END:
            out_chars.append(ch)
            continue
        if _HEBREW_ACCENT_START <= cp <= _HEBREW_ACCENT_END:
            out_chars.append(ch)
            continue
        if ch in {_HEBREW_MAQAF, _HEBREW_PASEQ, _HEBREW_SOF_PASUQ}:
            out_chars.append(ch)
    out = "".join(out_chars)
    if not out:
        raise ValueError(f"Expected Hebrew-script text, got: {text!r}")
    return out


def diff_uxlc_matches_changetext(diff_wlc_uxlc: object, changetext: str) -> bool | None:
    diff_uxlc_texts = _extract_diff_uxlc_texts(diff_wlc_uxlc)
    if len(diff_uxlc_texts) != 1:
        return None
    diff_uxlc_text = diff_uxlc_texts[0]

    sanitized_diff_uxlc = sanitize_word_for_change_match(diff_uxlc_text)
    sanitized_changetext = sanitize_word_for_change_match(changetext)
    return sanitized_diff_uxlc == sanitized_changetext


def descriptor_from_hebrew_token(text: str) -> str | None:
    accent_marks = [
        ch for ch in text if _HEBREW_ACCENT_START <= ord(ch) <= _HEBREW_ACCENT_END
    ]
    if len(accent_marks) == 0:
        return "maqaf" if _HEBREW_MAQAF in text else "no_accent"

    descriptors: list[str] = []
    for idx, ch in enumerate(text):
        if not (_HEBREW_ACCENT_START <= ord(ch) <= _HEBREW_ACCENT_END):
            continue

        descriptor = _ACCENT_TO_DESCRIPTOR.get(ch)
        if descriptor is not None:
            descriptors.append(descriptor)
            continue

        prefix = _OVER_ACCENT_TO_PREFIX.get(ch)
        if prefix is None:
            assert text in _NO_DESCRIPTOR_EXCEPTIONS, (
                "No descriptor for accent token unless explicitly allowlisted: "
                f"token={text!r} accent={ch!r}"
            )
            return None

        accented_letter = _previous_hebrew_letter(text, idx)
        assert (
            accented_letter is not None
        ), f"Over-accent must follow a Hebrew letter: token={text!r} accent={ch!r}"
        letter_name = _hebrew_letter_name(accented_letter)
        descriptors.append(f"{prefix}{letter_name}")

    if not descriptors:
        return None

    if _HEBREW_MAQAF in text and len(descriptors) == 1:
        simple_descriptor = descriptors[0]
        if simple_descriptor in _SIMPLE_ACCENT_DESCRIPTORS:
            return f"{simple_descriptor}-maqaf"

    if _HEBREW_MAQAF in text:
        descriptors.insert(0, "maqaf")

    if len(descriptors) > 1 and all(" " not in descriptor for descriptor in descriptors):
        return " ".join(descriptors)

    return ", ".join(descriptors)


def assessment_uxlc_matches_converted_diff_uxlc(
    assessment_uxlc: str,
    diff_wlc_uxlc: object,
) -> bool | None:
    is_list_payload = isinstance(diff_wlc_uxlc, list)
    diff_uxlc_texts = _extract_diff_uxlc_texts(diff_wlc_uxlc)
    if not diff_uxlc_texts:
        return None

    saw_indeterminate = False
    for diff_uxlc_text in diff_uxlc_texts:
        is_match = assessment_descriptor_matches_hebrew_token(
            assessment_descriptor=assessment_uxlc,
            hebrew_token=diff_uxlc_text,
        )
        if is_match is True:
            return True
        if is_match is None:
            saw_indeterminate = True

    if saw_indeterminate:
        return None

    if is_list_payload:
        # Multi-entry diffs are frequently mixed (notes + token deltas) and do
        # not reliably represent one-to-one descriptor targets.
        return None

    return False


def assessment_descriptor_matches_hebrew_token(
    *,
    assessment_descriptor: str,
    hebrew_token: str,
) -> bool | None:
    descriptor = descriptor_from_hebrew_token(hebrew_token)
    if descriptor is None:
        return None

    normalized_descriptor = _normalize_assessment_descriptor(descriptor)
    normalized_assessment = _normalize_assessment_descriptor(assessment_descriptor)

    if normalized_assessment == "meteg-space" and hebrew_token == "די":
        return True

    descriptor_simple_count = _simple_descriptor_accent_count(normalized_descriptor)
    assessment_simple_count = _simple_descriptor_accent_count(normalized_assessment)
    if (
        descriptor_simple_count is not None
        and assessment_simple_count is not None
        and descriptor_simple_count != assessment_simple_count
    ):
        # Descriptor arity mismatch is indeterminate in this pipeline because
        # a row-level assessment may describe a multi-token focus while the
        # diff entry under inspection is a single token.
        return None

    return _descriptor_matches_assessment(
        descriptor=normalized_descriptor,
        assessment_uxlc=normalized_assessment,
    )


def _descriptor_matches_assessment(descriptor: str, assessment_uxlc: str) -> bool:
    if descriptor == "merkha" and assessment_uxlc in {
        "merkha",
        "merkha-space",
    }:
        return True
    if descriptor == "maqaf" and assessment_uxlc in {
        "maqaf",
        "meteg-maqaf",
    }:
        return True
    return assessment_uxlc == descriptor


def _normalize_assessment_descriptor(descriptor: str) -> str:
    normalized = re.sub(r"\s*,\s*", " ", descriptor.strip())
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(
        r"\bpashta stress helper on\b",
        "pashta on",
        normalized,
        flags=re.IGNORECASE,
    )
    normalized = re.sub(r"\bxet\b", "het", normalized, flags=re.IGNORECASE)
    if normalized == "no accent":
        normalized = "no_accent"

    return re.sub(
        r"(?P<prefix>pashta on |qadma on )(?P<letter>[\u05d0-\u05ea])",
        lambda match: (
            f"{match.group('prefix')}{_hebrew_letter_name(match.group('letter'))}"
        ),
        normalized,
    )


def _simple_descriptor_accent_count(descriptor: str) -> int | None:
    descriptor_tokens = descriptor.split()
    if not descriptor_tokens:
        return None
    if all(token in _SIMPLE_ACCENT_DESCRIPTORS for token in descriptor_tokens):
        return len(descriptor_tokens)
    return None


def _extract_diff_uxlc_texts(diff_wlc_uxlc: object) -> list[str]:
    if isinstance(diff_wlc_uxlc, list):
        out_texts: list[str] = []
        for entry in diff_wlc_uxlc:
            out_texts.extend(_extract_diff_uxlc_texts(entry))
        return out_texts

    if not isinstance(diff_wlc_uxlc, dict):
        return []

    uxlc = diff_wlc_uxlc.get("uxlc")
    if isinstance(uxlc, str):
        return [uxlc]

    if isinstance(uxlc, dict):
        text = uxlc.get("text")
        if isinstance(text, str):
            return [text]
        return []

    if isinstance(uxlc, list) and len(uxlc) == 1:
        token = uxlc[0]
        if isinstance(token, str):
            return [token]
        if isinstance(token, dict):
            text = token.get("text")
            if isinstance(text, str):
                return [text]

    return []


def _previous_hebrew_letter(text: str, end_idx: int) -> str | None:
    for idx in range(end_idx - 1, -1, -1):
        ch = text[idx]
        if _HEBREW_LETTER_START <= ord(ch) <= _HEBREW_LETTER_END:
            return ch
    return None


def _hebrew_letter_name(letter: str) -> str:
    return LETTER_NAMES.get(letter, letter)
