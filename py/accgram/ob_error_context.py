from __future__ import annotations

import re
from pathlib import Path
from typing import TypedDict

from accgram import prose_oddballs
from accgram import ob_tree_parse

_OUTPUT_FILE_BB_RE = re.compile(r"^wlc_422_ps_([A-Za-z0-9]+)_ag\.txt$")
_NODE_LINE_RE = re.compile(r"^\s*(\d+)\s+(\S(?:.*\S)?)\s*$")
_ERROR_TOKEN_RE = re.compile(r"\bERROR\b")


class ErrorPath(TypedDict):
    path_labels: list[str]
    leaf: str


ErrorTree = ob_tree_parse.ErrorTree


def collect_error_trees_by_ref(
    rows: list[dict[str, object]],
    base_dir: Path,
) -> dict[str, ErrorTree | None]:
    # All oddball ERROR trees live in a single output dir (base_dir).
    refs_by_file: dict[str, set[str]] = {}
    for row in rows:
        ref = _row_ref(row)
        output_file = _row_output_file(row)
        refs_by_file.setdefault(output_file, set()).add(ref)

    out: dict[str, ErrorTree | None] = {}
    for output_file, refs in refs_by_file.items():
        output_path = base_dir / output_file
        bb = _bb_from_output_file(output_file)
        if bb is None:
            for ref in refs:
                out[ref] = None
            continue

        verse_lines_by_ref = _collect_verse_lines_by_ref(
            output_path=output_path,
            bb=bb,
            requested_refs=refs,
        )
        for ref in refs:
            out[ref] = _extract_error_tree(verse_lines_by_ref.get(ref, []))

    return out


def collect_error_tree_for_ref(
    *,
    ref: str,
    output_file: str,
    goerwitz_out_dir: Path,
) -> ErrorTree | None:
    output_path = goerwitz_out_dir / output_file
    bb = _bb_from_output_file(output_file)
    if bb is None:
        return None

    verse_lines_by_ref = _collect_verse_lines_by_ref(
        output_path=output_path,
        bb=bb,
        requested_refs={ref},
    )
    return _extract_error_tree(verse_lines_by_ref.get(ref, []))


def collect_error_paths_by_ref(
    rows: list[dict[str, object]],
    goerwitz_out_dir: Path,
) -> dict[str, list[ErrorPath]]:
    refs_by_output_file: dict[str, set[str]] = {}
    for row in rows:
        ref = _row_ref(row)
        output_file = _row_output_file(row)
        refs_by_output_file.setdefault(output_file, set()).add(ref)

    out: dict[str, list[ErrorPath]] = {}
    for output_file, refs in refs_by_output_file.items():
        output_path = goerwitz_out_dir / output_file
        bb = _bb_from_output_file(output_file)
        if bb is None:
            for ref in refs:
                out[ref] = []
            continue

        verse_lines_by_ref = _collect_verse_lines_by_ref(
            output_path=output_path,
            bb=bb,
            requested_refs=refs,
        )
        for ref in refs:
            verse_lines = verse_lines_by_ref.get(ref, [])
            out[ref] = _extract_error_paths(verse_lines)

    return out


def collect_error_paths_for_ref(
    *,
    ref: str,
    output_file: str,
    goerwitz_out_dir: Path,
) -> list[ErrorPath]:
    output_path = goerwitz_out_dir / output_file
    bb = _bb_from_output_file(output_file)
    if bb is None:
        return []

    verse_lines_by_ref = _collect_verse_lines_by_ref(
        output_path=output_path,
        bb=bb,
        requested_refs={ref},
    )
    return _extract_error_paths(verse_lines_by_ref.get(ref, []))


def max_error_path_depth(error_paths: list[ErrorPath]) -> int:
    if not error_paths:
        return 0
    return max(len(path["path_labels"]) for path in error_paths)


def _collect_verse_lines_by_ref(
    *,
    output_path: Path,
    bb: str,
    requested_refs: set[str],
) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    if not output_path.is_file():
        return out

    current_ref: str | None = None
    with output_path.open("r", encoding="utf-8") as f_in:
        for raw_line in f_in:
            line = raw_line.rstrip("\r\n")
            stripped = line.strip()
            heading_match = prose_oddballs._OUTPUT_VERSE_LABEL_RE.match(stripped)
            if heading_match is not None:
                chnu = int(heading_match.group(1))
                vrnu = int(heading_match.group(2))
                current_ref = f"{bb} {chnu}:{vrnu}"
                if current_ref in requested_refs:
                    out.setdefault(current_ref, [])
                continue

            if current_ref is None or current_ref not in requested_refs:
                continue

            out[current_ref].append(line)

    return out


def _extract_error_paths(verse_lines: list[str]) -> list[ErrorPath]:
    error_paths: list[ErrorPath] = []
    stack: list[tuple[int, str]] = []

    for line in verse_lines:
        stripped = line.strip()
        if not stripped:
            continue

        node_match = _NODE_LINE_RE.match(line)
        if node_match is not None:
            depth = int(node_match.group(1))
            label = node_match.group(2).strip()
            while stack and stack[-1][0] >= depth:
                stack.pop()
            stack.append((depth, label))
            continue

        if _ERROR_TOKEN_RE.search(stripped) is None:
            continue

        error_paths.append(
            {
                "path_labels": [label for _depth, label in stack],
                "leaf": stripped,
            }
        )

    return error_paths


def parse_error_tree_from_text(tree_text: str) -> ErrorTree | None:
    """Parse an already-rendered ERROR tree (e.g. poetic ``print_tree`` output)
    into an ``ErrorTree``, single-sourcing the node/ERROR line regexes.

    Returns None when the text holds no ERROR leaf (so a clean tree, or a
    non-tree line such as the poetic ``NO_PARSE: ...`` form, yields None).
    """
    return _extract_error_tree(tree_text.splitlines())


def parse_tree_from_text(tree_text: str) -> ErrorTree | None:
    """Parse a rendered ``print_tree`` -- clean OR ERROR -- into an ``ErrorTree``.

    Unlike :func:`parse_error_tree_from_text` (which yields None for an
    error-free tree), this returns the parsed tree regardless of whether it
    holds an ERROR leaf, so a clean parse can still be rendered as a table by
    ``ob_tree_table.render_error_tree_table`` (error cells are simply absent).
    Returns None only when the text has no tree node lines at all.
    """
    lines = tree_text.splitlines()
    if not lines:
        return None
    tree = ob_tree_parse.parse_verse_tree(
        verse_lines=lines,
        node_line_re=_NODE_LINE_RE,
        error_token_re=_ERROR_TOKEN_RE,
    )
    return tree if tree.roots else None


def _extract_error_tree(verse_lines: list[str]) -> ErrorTree | None:
    if not verse_lines:
        return None

    tree = ob_tree_parse.parse_verse_tree(
        verse_lines=verse_lines,
        node_line_re=_NODE_LINE_RE,
        error_token_re=_ERROR_TOKEN_RE,
    )
    if not tree.has_error_leaf:
        return None
    return tree


def _bb_from_output_file(output_file: str) -> str | None:
    match = _OUTPUT_FILE_BB_RE.match(output_file)
    if match is None:
        return None
    return match.group(1).lower()


def _row_ref(row: dict[str, object]) -> str:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Oddball row is missing non-empty string field 'ref'")
    return ref.strip()


def _row_output_file(row: dict[str, object]) -> str:
    output_file = row.get("output_file")
    if not isinstance(output_file, str) or not output_file.strip():
        raise ValueError("Oddball row is missing non-empty string field 'output_file'")
    return output_file.strip()
