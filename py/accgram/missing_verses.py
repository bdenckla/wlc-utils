from __future__ import annotations

import json
import re
from pathlib import Path

from mb_cmn import provenance

_INPUT_VERSE_LINE_RE = re.compile(r"^(\d+):(\d+)\s+(.*)$")
_OUTPUT_VERSE_LABEL_RE = re.compile(
    r"^(?:[1-3]\s*)?[A-Z][A-Za-z_]*(?:\s+[A-Z][A-Za-z_]*)*\s+(\d+):(\d+)\b"
)


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


def _collect_output_refs(output_path: Path) -> set[tuple[int, int]]:
    verse_refs: set[tuple[int, int]] = set()
    if not output_path.is_file():
        return verse_refs

    with output_path.open("r", encoding="utf-8") as f_out:
        for raw_line in f_out:
            stripped = raw_line.strip()
            if not stripped:
                continue

            match = _OUTPUT_VERSE_LABEL_RE.match(stripped)
            if match is None:
                continue
            verse_refs.add((int(match.group(1)), int(match.group(2))))
    return verse_refs


def write_missing_verses_json(
    in_dir: Path, out_dir: Path, missing_verses_out_path: Path
) -> None:
    missing_rows: list[dict[str, object]] = []
    books_with_missing_verses: set[str] = set()

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
        output_refs = _collect_output_refs(output_path)

        for ref in sorted(input_verses):
            chnu, vrnu = ref
            if (chnu, vrnu) in output_refs:
                continue
            missing_rows.append(
                {
                    "ref": f"{bb} {chnu}:{vrnu}",
                    "content": input_verses[ref],
                    "output_file": output_path.name,
                }
            )
            books_with_missing_verses.add(bb)

    payload: dict[str, object] = {
        "artifacts_description": "missing verses from goerwitz *_ag.txt outputs",
        "payload_provenance_note": (
            "These verses are present in the split input book files but have no verse label in the "
            "corresponding goerwitz *_ag.txt output files."
        ),
        "summary": {
            "missing_verses": len(missing_rows),
            "books_with_missing_verses": len(books_with_missing_verses),
        },
        "missing_verses": missing_rows,
    }
    payload = provenance.with_json_provenance(payload, __file__)

    missing_verses_out_path.parent.mkdir(parents=True, exist_ok=True)
    with missing_verses_out_path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
