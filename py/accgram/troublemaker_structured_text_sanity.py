from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from cmn.wlc_book_codes import bk39id_to_wlc_bb
from mb_cmn import hebrew_accents as ha
from mb_diff_mpu.describe_diff import LETTER_NAMES
from mb_cmn.uxlc_change_url import uxlc_change_url
from py_uxlc.my_uxlc_book_abbreviations import BKNA_MAP_UXLC_TO_STD


def _normalize_book_token(book: str) -> str:
    return re.sub(r"[\s.]", "", book).lower()


_CITATION_BOOK_TO_STD_BKID = {
    _normalize_book_token(book_ua): std_bkid
    for book_ua, std_bkid in BKNA_MAP_UXLC_TO_STD.items()
}

_REF_RE = re.compile(r"^(?P<bb>[0-9a-z]{2})\s+(?P<ch>\d+):(?P<vr>\d+)$")
_CITATION_RE = re.compile(r"^(?P<book>.+?)\s+(?P<ch>\d+):(?P<vr>\d+)(?:\.\d+)?$")
_RELEASE_LABEL_RE = re.compile(r"^(?P<date>\d{4}\.\d{2}\.\d{2})\s*-\s*Changes$")

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


def sanity_check_structured_text(
    refs: list[str],
    structured_text_by_ref: dict[str, dict[str, object]],
    all_changes_path: Path,
) -> None:
    if not all_changes_path.is_file():
        raise FileNotFoundError(f"all_changes.json not found: {all_changes_path}")

    all_changes = _read_json(all_changes_path)
    if not isinstance(all_changes, list):
        raise ValueError(f"Expected list in all_changes.json: {all_changes_path}")

    by_change_url: dict[str, dict[str, object]] = {}
    for row in all_changes:
        if not isinstance(row, dict):
            continue
        url = _url_for_all_changes_row(row)
        by_change_url[url] = row

    errors: list[str] = []
    for ref in refs:
        structured = structured_text_by_ref.get(ref)
        if structured is None:
            continue

        uxlc_change = structured.get("uxlc_change")
        if not isinstance(uxlc_change, str) or not uxlc_change.strip():
            continue

        canonical_url = _canonicalize_uxlc_change_url(uxlc_change)
        if canonical_url is None:
            errors.append(
                f"Malformed structured_text.uxlc_change URL for {ref}: {uxlc_change}"
            )
            continue

        change_row = by_change_url.get(canonical_url)
        if change_row is None:
            errors.append(
                "structured_text.uxlc_change not found in all_changes.json "
                f"for {ref}: {uxlc_change}"
            )
            continue

        citation = change_row.get("citation")
        if not isinstance(citation, str):
            errors.append(
                f"all_changes.json row is missing string citation for URL {canonical_url}"
            )
            continue

        if not _citation_matches_ref(citation, ref):
            errors.append(
                "citation/ref mismatch for structured_text.uxlc_change "
                f"for {ref}: citation={citation} url={uxlc_change}"
            )

    if errors:
        first_errors = errors[:20]
        remainder_count = len(errors) - len(first_errors)
        details = "\n".join(f"- {error}" for error in first_errors)
        if remainder_count > 0:
            details = f"{details}\n- ... and {remainder_count} more"
        raise ValueError(
            "structured_text sanity checks failed against all_changes.json:\n"
            f"{details}"
        )


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


def load_all_changes_by_url(all_changes_path: Path) -> dict[str, dict[str, object]]:
    if not all_changes_path.is_file():
        raise FileNotFoundError(f"all_changes.json not found: {all_changes_path}")

    all_changes = _read_json(all_changes_path)
    if not isinstance(all_changes, list):
        raise ValueError(f"Expected list in all_changes.json: {all_changes_path}")

    by_change_url: dict[str, dict[str, object]] = {}
    for row in all_changes:
        if not isinstance(row, dict):
            continue
        url = _url_for_all_changes_row(row)
        by_change_url[url] = row
    return by_change_url


def canonicalize_uxlc_change_url(url: str) -> str | None:
    return _canonicalize_uxlc_change_url(url)


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
    if descriptor == "maqaf" and assessment_uxlc in {
        "maqaf",
        "meteg-maqaf",
    }:
        return True
    return assessment_uxlc == descriptor


def _normalize_assessment_descriptor(descriptor: str) -> str:
    normalized = re.sub(r"\s*,\s*", " ", descriptor.strip())
    normalized = re.sub(r"\s+", " ", normalized)
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


def _read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f_in:
        return json.load(f_in)


def _url_for_all_changes_row(row: dict[str, object]) -> str:
    release = row.get("release")
    changeset = row.get("changeset")
    n = row.get("n")
    if (
        not isinstance(release, str)
        or not isinstance(changeset, str)
        or not isinstance(n, int)
    ):
        raise ValueError("Malformed all_changes.json row: missing release/changeset/n")
    return uxlc_change_url(release, f"{changeset}-{n}")


def _canonicalize_uxlc_change_url(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.query:
        return None

    path_parts = [part for part in parsed.path.split("/") if part]
    if len(path_parts) < 2:
        return None

    release_label = unquote(path_parts[-2])
    match = _RELEASE_LABEL_RE.match(release_label)
    if match is None:
        return None

    release = match.group("date")
    change_id = parsed.query
    return uxlc_change_url(release, change_id)


def _citation_matches_ref(citation: str, ref: str) -> bool:
    citation_bb, citation_ch, citation_vr = _parse_citation(citation)
    ref_bb, ref_ch, ref_vr = _parse_ref(ref)
    return citation_bb == ref_bb and citation_ch == ref_ch and citation_vr == ref_vr


def _parse_ref(ref: str) -> tuple[str, int, int]:
    match = _REF_RE.match(ref.strip())
    if match is None:
        raise ValueError(f"Malformed ref: {ref}")
    return match.group("bb"), int(match.group("ch")), int(match.group("vr"))


def _parse_citation(citation: str) -> tuple[str, int, int]:
    match = _CITATION_RE.match(citation.strip())
    if match is None:
        raise ValueError(f"Malformed citation: {citation}")

    citation_book = match.group("book")
    std_bkid = _CITATION_BOOK_TO_STD_BKID.get(_normalize_book_token(citation_book))
    if std_bkid is None:
        raise ValueError(f"Unknown citation book abbreviation: {citation_book}")

    try:
        bb = bk39id_to_wlc_bb(std_bkid)
    except ValueError as exc:
        raise ValueError(
            f"Could not map citation book to WLC bb code: {citation_book}"
        ) from exc

    return bb, int(match.group("ch")), int(match.group("vr"))
