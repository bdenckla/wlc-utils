from __future__ import annotations

import json
import re
from pathlib import Path

from mb_cmn import provenance

_INPUT_VERSE_LINE_RE = re.compile(r"^(\d+):(\d+)\s+(.*)$")
_OUTPUT_VERSE_LABEL_RE = re.compile(
    r"^(?:[1-3]\s*)?[A-Z][A-Za-z_]*(?:\s+[A-Z][A-Za-z_]*)*\s+(\d+):(\d+)\b"
)
_ERROR_TOKEN_RE = re.compile(r"\bERROR\b")


def _collect_input_verses(input_path: Path) -> dict[tuple[int, int], str]:
    verse_lines: dict[tuple[int, int], str] = {}
    with input_path.open("r", encoding="utf-8") as f_in:
        for raw_line in f_in:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            match = _INPUT_VERSE_LINE_RE.match(stripped)
            if match is None:
                continue

            ref = (int(match.group(1)), int(match.group(2)))
            verse_lines.setdefault(ref, match.group(3))
    return verse_lines


def _collect_oddball_refs(output_path: Path) -> set[tuple[int, int]]:
    oddball_refs: set[tuple[int, int]] = set()
    if not output_path.is_file():
        return oddball_refs

    current_ref: tuple[int, int] | None = None
    with output_path.open("r", encoding="utf-8") as f_out:
        for raw_line in f_out:
            stripped = raw_line.strip()
            if not stripped:
                continue

            match = _OUTPUT_VERSE_LABEL_RE.match(stripped)
            if match is not None:
                current_ref = (int(match.group(1)), int(match.group(2)))
                continue

            if current_ref is not None and _ERROR_TOKEN_RE.search(stripped):
                oddball_refs.add(current_ref)

    return oddball_refs


def write_oddballs_json(in_dir: Path, out_dir: Path, oddballs_out_path: Path) -> None:
    oddball_rows: list[dict[str, object]] = []
    books_with_oddballs: set[str] = set()

    input_paths = sorted(
        p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    for input_path in input_paths:
        stem = input_path.stem
        if not stem.startswith("wlc_422_ps_"):
            continue

        bb = stem.removeprefix("wlc_422_ps_")
        output_path = out_dir / f"{stem}_ag.txt"

        input_verses = _collect_input_verses(input_path)
        oddball_refs = _collect_oddball_refs(output_path)

        for ref in sorted(oddball_refs):
            chnu, vrnu = ref
            oddball_rows.append(
                {
                    "ref": f"{bb} {chnu}:{vrnu}",
                    "content": input_verses.get(ref, ""),
                    "output_file": output_path.name,
                }
            )
            books_with_oddballs.add(bb)

    payload: dict[str, object] = {
        "artifacts_description": "oddball verses with ERROR nodes in goerwitz *_ag.txt outputs",
        "payload_provenance_note": (
            "These verses are present in goerwitz *_ag.txt outputs, but their parsed tree "
            "contains at least one line with the token ERROR."
        ),
        "summary": {
            "oddballs": len(oddball_rows),
            "books_with_oddballs": len(books_with_oddballs),
        },
        "oddballs": oddball_rows,
    }
    payload = provenance.with_json_provenance(payload, __file__)

    oddballs_out_path.parent.mkdir(parents=True, exist_ok=True)
    with oddballs_out_path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
