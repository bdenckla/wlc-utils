from __future__ import annotations

import json
import re
from pathlib import Path

_TROUBLEMAKER_REF_RE = re.compile(r"^(?P<bb>[0-9a-z]{2})\s+(?P<ch>\d+):(?P<vr>\d+)$")


ParsedRow = tuple[dict[str, object], str, str]


def read_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as f_in:
        return json.load(f_in)


def parse_ref(ref: str, *, row_kind: str = "troublemaker") -> tuple[str, int, int]:
    match = _TROUBLEMAKER_REF_RE.match(ref.strip())
    if match is None:
        raise ValueError(f"Malformed {row_kind} ref: {ref}")
    bb = match.group("bb")
    chnu = int(match.group("ch"))
    vrnu = int(match.group("vr"))
    return bb, chnu, vrnu


def to_compact_bcv(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb}{chnu}:{vrnu}"


def to_ref(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb} {chnu}:{vrnu}"


def parse_troublemaker_rows(
    troubles_in_path: Path,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> list[ParsedRow]:
    return _parse_rows(
        in_path=troubles_in_path,
        payload_key="troublemakers",
        row_kind="troublemaker",
        invalid_payload_message=(
            f"Expected list at troubles payload key 'troublemakers': {troubles_in_path}"
        ),
        row_object_message="Troublemaker rows must be JSON objects",
        missing_ref_message="Troublemaker row is missing string field 'ref'",
        refs_by_book=refs_by_book,
    )


def parse_oddball_rows(
    oddballs_in_path: Path,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> list[ParsedRow]:
    return _parse_rows(
        in_path=oddballs_in_path,
        payload_key="oddballs",
        row_kind="oddball",
        invalid_payload_message=(
            f"Expected list at oddballs payload key 'oddballs': {oddballs_in_path}"
        ),
        row_object_message="Oddball rows must be JSON objects",
        missing_ref_message="Oddball row is missing string field 'ref'",
        refs_by_book=refs_by_book,
    )


def _parse_rows(
    *,
    in_path: Path,
    payload_key: str,
    row_kind: str,
    invalid_payload_message: str,
    row_object_message: str,
    missing_ref_message: str,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> list[ParsedRow]:
    payload = read_json(in_path)
    rows = payload.get(payload_key) if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise ValueError(invalid_payload_message)

    parsed_rows: list[ParsedRow] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(row_object_message)
        ref_value = row.get("ref")
        if not isinstance(ref_value, str):
            raise ValueError(missing_ref_message)

        bb, chnu, vrnu = parse_ref(ref_value, row_kind=row_kind)
        bcv = to_compact_bcv(bb, chnu, vrnu)
        ref = to_ref(bb, chnu, vrnu)
        refs_by_book.setdefault(bb, set()).add((chnu, vrnu))
        parsed_rows.append((row, bcv, ref))

    return parsed_rows
