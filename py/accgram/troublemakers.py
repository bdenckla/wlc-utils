from __future__ import annotations

import json
import re
from pathlib import Path

from mb_cmn import provenance


_SOURCE_VERSE_LINE_RE = re.compile(r"^([0-9a-z]{2})(\d+):(\d+)\s+(.*)$")


HARDCODED_REFS: frozenset[tuple[str, int, int]] = frozenset(
    {
        ("ob", 1, 1),
        ("ek", 11, 1),
        ("je", 9, 11),
        ("lv", 19, 1),
    }
)


def default_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz" / "_troublemakers.json"


def is_hardcoded_ref(bb: str, chnu: int, vrnu: int) -> bool:
    return (bb, chnu, vrnu) in HARDCODED_REFS


def format_ref(ref: tuple[str, int, int]) -> str:
    bb, chnu, vrnu = ref
    return f"{bb} {chnu}:{vrnu}"


def collect_source_lines(
    input_path: Path,
    troublemaker_refs: set[tuple[str, int, int]],
) -> dict[tuple[str, int, int], str]:
    source_lines: dict[tuple[str, int, int], str] = {}
    if not troublemaker_refs:
        return source_lines

    with input_path.open("r", encoding="utf-8") as f_in:
        for raw_line in f_in:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            m = _SOURCE_VERSE_LINE_RE.match(stripped)
            if m is None:
                continue

            ref = (m.group(1), int(m.group(2)), int(m.group(3)))
            if ref in troublemaker_refs and ref not in source_lines:
                source_lines[ref] = m.group(4)

    return source_lines


def write_json(
    troublemakers_out_path: Path,
    troublemaker_refs: set[tuple[str, int, int]],
    source_lines: dict[tuple[str, int, int], str],
) -> None:
    sorted_refs = sorted(troublemaker_refs)
    payload: dict[str, object] = {
        "artifacts_description": "hardcoded troublemaker verse exclusions",
        "payload_provenance_note": (
            "These verses are excluded by explicit hardcoded rules in this repo "
            "to avoid known parser-breaker inputs."
        ),
        "summary": {
            "troublemakers_excluded": len(sorted_refs),
            "books_with_troublemakers": len({bb for bb, _, _ in sorted_refs}),
        },
        "troublemakers": [
            {
                "ref": format_ref(ref),
                "content": source_lines.get(ref, ""),
            }
            for ref in sorted_refs
        ],
    }
    payload = provenance.with_json_provenance(payload, __file__)

    troublemakers_out_path.parent.mkdir(parents=True, exist_ok=True)
    with troublemakers_out_path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
