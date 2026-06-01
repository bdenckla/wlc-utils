from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import unquote, urlparse

from accgram.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn.uxlc_change_url import uxlc_change_url
from py_uxlc.my_uxlc_book_abbreviations import BKNA_MAP_UXLC_TO_STD


_WLC_BOOK_CODES = (
    "gn", "ex", "lv", "nu", "dt", "js", "ju", "1s", "2s", "1k", "2k", "is", "je", "ek",
    "ho", "jl", "am", "ob", "jn", "mi", "na", "hb", "zp", "hg", "zc", "ma", "ps", "pr",
    "jb", "ca", "ru", "lm", "ec", "es", "da", "er", "ne", "1c", "2c",
)


def _normalize_book_token(book: str) -> str:
    return re.sub(r"[\s.]", "", book).lower()


_STD_BKID_TO_WLC_BB = {wlc_bb_to_bk39id(bb): bb for bb in _WLC_BOOK_CODES}
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
            errors.append(f"Malformed structured_text.uxlc_change URL for {ref}: {uxlc_change}")
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
            errors.append(f"all_changes.json row is missing string citation for URL {canonical_url}")
            continue

        if not _citation_matches_ref(citation, ref):
            errors.append(
                "citation/ref mismatch for structured_text.uxlc_change "
                f"for {ref}: citation={citation} url={uxlc_change}"
            )

        assessment = structured.get("assessment")
        assessment_uxlc = assessment.get("uxlc") if isinstance(assessment, dict) else None
        if isinstance(assessment_uxlc, str):
            changetext = change_row.get("changetext")
            if not isinstance(changetext, str):
                errors.append(f"all_changes.json row is missing string changetext for URL {canonical_url}")
                continue
            sanitized_changetext = sanitize_word_for_change_match(changetext)
            sanitized_assessment_uxlc = sanitize_word_for_change_match(assessment_uxlc)

            # assessment.uxlc is often a descriptor label (e.g. "munax").
            # Compare only when it contains Hebrew-script text after sanitization.
            if sanitized_assessment_uxlc and sanitized_assessment_uxlc != sanitized_changetext:
                errors.append(
                    "changetext/assessment.uxlc mismatch after sanitization "
                    f"for {ref}: changetext={changetext} assessment.uxlc={assessment_uxlc}"
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
    return "".join(out_chars)


def _read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f_in:
        return json.load(f_in)


def _url_for_all_changes_row(row: dict[str, object]) -> str:
    release = row.get("release")
    changeset = row.get("changeset")
    n = row.get("n")
    if not isinstance(release, str) or not isinstance(changeset, str) or not isinstance(n, int):
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

    bb = _STD_BKID_TO_WLC_BB.get(std_bkid)
    if bb is None:
        raise ValueError(f"Could not map citation book to WLC bb code: {citation_book}")

    return bb, int(match.group("ch")), int(match.group("vr"))

