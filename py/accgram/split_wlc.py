from __future__ import annotations

import re
from collections import OrderedDict
from pathlib import Path

from cmn.wlc_book_codes import wlc_bb_to_goerwitz_book_name

_BOOK_LINE_RE = re.compile(r"^([0-9a-z]{2})(\d+):(\d+)\b")
_LINE_REF_RE = re.compile(r"^([0-9a-z]{2})(\d+:\d+\s+.*)$")
_SOURCE_VERSE_LINE_RE = re.compile(r"^([0-9a-z]{2})(\d+):(\d+)\s+(.*)$")


def split_wlc_to_book_texts(
    input_path: Path,
    keep_line_fn=None,
) -> "OrderedDict[str, str]":
    """Split wlc422_ps.txt into per-book scanner-ready text, in memory.

    Returns an OrderedDict mapping each WLC 2-char book code to the text the PLY
    scanner expects: a goerwitz book-name header line followed by normalized
    ``ch:vr <accents>`` lines (the 2-char WLC book code dropped). ``keep_line_fn``,
    if given, is called as ``keep_line_fn(bb, chnu, vrnu)`` and may exclude verses
    (e.g. the genre filter); excluded verses never appear in the output.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    per_book: OrderedDict[str, list[str]] = OrderedDict()
    malformed: list[str] = []

    with input_path.open("r", encoding="utf-8") as f_in:
        for line_no, raw_line in enumerate(f_in, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            m = _BOOK_LINE_RE.match(stripped)
            if m is None:
                if len(malformed) < 10:
                    malformed.append(f"line {line_no}: {stripped[:120]}")
                continue

            bb = m.group(1)
            chnu = int(m.group(2))
            vrnu = int(m.group(3))

            if keep_line_fn is not None and not keep_line_fn(bb, chnu, vrnu):
                continue

            per_book.setdefault(bb, []).append(raw_line)

    if malformed:
        preview = "\n".join(malformed)
        raise ValueError(
            "Encountered malformed non-comment lines while splitting input. "
            f"First {len(malformed)} examples:\n{preview}"
        )

    book_texts: OrderedDict[str, str] = OrderedDict()
    for bb, lines in per_book.items():
        book_name = wlc_bb_to_goerwitz_book_name(bb)
        output_lines = [f"{book_name}\n"]
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped:
                continue
            # Core transformation: "gn1:2 ..." -> "1:2 ..." (drop 2-char WLC book code).
            m = _LINE_REF_RE.match(stripped)
            if m is None:
                raise ValueError(
                    "Unexpected verse line format during goerwitz normalization: "
                    f"bb={bb} line={stripped[:120]}"
                )
            output_lines.append(f"{m.group(2)}\n")
        book_texts[bb] = "".join(output_lines)

    return book_texts


def collect_source_lines(
    input_path: Path,
    refs: set[tuple[str, int, int]],
) -> dict[tuple[str, int, int], str]:
    """Return the raw verse text (accents) for each requested ``(bb, chnu, vrnu)``."""
    source_lines: dict[tuple[str, int, int], str] = {}
    if not refs:
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
            if ref in refs and ref not in source_lines:
                source_lines[ref] = m.group(4)

    return source_lines
