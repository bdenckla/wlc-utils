from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


SUMMARY_FILENAME = "_summary.stderr.json"
VERSE_REF_RE = re.compile(
    r"(?P<verse>(?:[1-3]\s*)?[A-Z][A-Za-z_]*(?:\s+[A-Z][A-Za-z_]*)*\s+\d+:\d+)\s*$"
)


@dataclass(frozen=True)
class StderrSummaryResult:
    summary_path: Path
    files_scanned: int
    files_with_nonempty_stderr: int
    total_stderr_lines: int
    total_unique_verse_messages: int
    total_unique_non_verse_messages: int


def _normalize_ws(text: str) -> str:
    return " ".join(text.split())


def _parse_stderr_line(line: str) -> tuple[str | None, str]:
    normalized = _normalize_ws(line.strip())
    if not normalized:
        return (None, "")

    match = VERSE_REF_RE.search(normalized)
    if not match:
        return (None, normalized)

    verse_ref = _normalize_ws(match.group("verse"))
    message_without_ref = normalized[: match.start()].rstrip(" ,;:-")
    if not message_without_ref:
        # Be conservative: if we cannot confidently recover a message body,
        # keep the line in the non-verse bucket.
        return (None, normalized)
    return (verse_ref, message_without_ref)


def write_stderr_summary(stderr_dir: Path, summary_path: Path) -> StderrSummaryResult:
    sidecar_paths = sorted(stderr_dir.glob("*_ag.stderr.txt"))

    verse_counts: dict[str, Counter[str]] = {}
    non_verse_counts: Counter[str] = Counter()
    per_file_counters: list[dict[str, object]] = []

    files_with_nonempty_stderr = 0
    total_stderr_lines = 0

    for sidecar_path in sidecar_paths:
        content = sidecar_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        file_line_count = 0
        file_verse_counter: Counter[tuple[str, str]] = Counter()
        file_non_verse_counter: Counter[str] = Counter()

        for raw_line in lines:
            verse_ref, message = _parse_stderr_line(raw_line)
            if not message:
                continue

            file_line_count += 1
            if verse_ref is None:
                non_verse_counts[message] += 1
                file_non_verse_counter[message] += 1
            else:
                if verse_ref not in verse_counts:
                    verse_counts[verse_ref] = Counter()
                verse_counts[verse_ref][message] += 1
                file_verse_counter[(verse_ref, message)] += 1

        total_stderr_lines += file_line_count
        if file_line_count > 0:
            files_with_nonempty_stderr += 1

        per_file_counters.append(
            {
                "file": sidecar_path.name,
                "stderr_lines": file_line_count,
                "unique_verse_messages": len(file_verse_counter),
                "unique_non_verse_messages": len(file_non_verse_counter),
            }
        )

    verse_message_aggregates: list[dict[str, object]] = []
    for verse_ref in sorted(verse_counts):
        message_counter = verse_counts[verse_ref]
        message_rows = [
            {"message": message, "count": message_counter[message]}
            for message in sorted(message_counter)
        ]
        verse_message_aggregates.append(
            {
                "verse_ref": verse_ref,
                "messages": message_rows,
                "unique_messages": len(message_rows),
                "total_count": sum(message_counter.values()),
            }
        )

    non_verse_message_aggregates = [
        {"message": message, "count": non_verse_counts[message]}
        for message in sorted(non_verse_counts)
    ]

    total_unique_verse_messages = sum(len(counter) for counter in verse_counts.values())
    total_unique_non_verse_messages = len(non_verse_counts)

    summary_obj = {
        "run_metadata": {
            "summary_version": 1,
            "stderr_dir": str(stderr_dir),
            "summary_path": str(summary_path),
            "source_glob": "*_ag.stderr.txt",
        },
        "file_counters": {
            "files_scanned": len(sidecar_paths),
            "files_with_nonempty_stderr": files_with_nonempty_stderr,
            "total_stderr_lines": total_stderr_lines,
            "total_unique_verse_messages": total_unique_verse_messages,
            "total_unique_non_verse_messages": total_unique_non_verse_messages,
        },
        "verse_message_aggregates": verse_message_aggregates,
        "non_verse_message_aggregates": non_verse_message_aggregates,
        "per_file_counters": per_file_counters,
    }

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_text = json.dumps(summary_obj, ensure_ascii=False, indent=2)
    summary_path.write_text(f"{summary_text}\n", encoding="utf-8", newline="\n")

    return StderrSummaryResult(
        summary_path=summary_path,
        files_scanned=len(sidecar_paths),
        files_with_nonempty_stderr=files_with_nonempty_stderr,
        total_stderr_lines=total_stderr_lines,
        total_unique_verse_messages=total_unique_verse_messages,
        total_unique_non_verse_messages=total_unique_non_verse_messages,
    )
