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
        ("je", 9, 10),
        ("je", 9, 11),
        ("ju", 13, 18),
        ("lv", 19, 1),
        ("1k", 6, 2),
        ("1k", 16, 33),
        ("1k", 19, 11),
        ("1k", 20, 29),
        ("1s", 6, 19),
        ("2c", 22, 12),
        ("2c", 26, 15),
        ("2k", 23, 36),
        ("am", 1, 14),
        ("am", 6, 6),
        ("am", 9, 5),
        ("da", 2, 41),
        ("dt", 9, 20),
        ("dt", 13, 15),
        ("dt", 25, 9),
        ("ec", 9, 18),
        ("ec", 7, 21),
        ("ek", 14, 11),
        ("ek", 33, 20),
        ("ex", 2, 5),
        ("ex", 14, 25),
        ("ex", 14, 29),
        ("ex", 34, 6),
        ("hg", 2, 12),
        ("ho", 4, 19),
        ("ho", 8, 9),
        ("is", 36, 2),
        ("je", 4, 19),
        ("je", 10, 3),
        ("je", 31, 32),
        ("je", 38, 11),
        ("je", 48, 12),
        ("je", 49, 19),
        ("lm", 5, 5),
        ("lv", 18, 17),
        ("lv", 26, 7),
        ("mi", 2, 7),
        ("nu", 7, 32),
        ("nu", 7, 40),
        ("nu", 7, 55),
        ("nu", 7, 68),
        ("nu", 20, 19),
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
