from __future__ import annotations

import re
from pathlib import Path

_OUTPUT_VERSE_LABEL_RE = re.compile(
    r"^(?:[1-3]\s*)?[A-Z][A-Za-z_]*(?:\s+[A-Z][A-Za-z_]*)*\s+(\d+):(\d+)\b"
)
_ERROR_TOKEN_RE = re.compile(r"\bERROR\b")


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
