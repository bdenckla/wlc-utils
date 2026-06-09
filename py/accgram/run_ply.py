"""Driver for the Python PLY port: mirrors `accents -p` on a new-format book file.

Stage 1 / Phase B.  Reads a book file, scans each verse into a token stream
(ply_scanner), parses it into a tree (ply_grammar), and prints the reference
line followed by the indented tree (ply_tree.print_tree) -- the same stdout the
C "goerwitz" binary produces with `-p`.  Output goes to out/accgram/ply/ for
side-by-side diffing with the frozen oracle via `compare-ply`.

Verses the Phase-B grammar subset cannot yet parse are skipped (and counted);
they become "missing" in the comparator until Phase C widens the grammar.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.ply_scanner import scan_book
from accgram.ply_tree import print_tree


@dataclass(frozen=True)
class BookRun:
    bb: str
    verse_count: int
    parsed_count: int
    skipped_refs: list[str]


def render_book(text: str, parser) -> tuple[str, BookRun, str]:
    """Return (output_text, stats, bb) for one book file's text."""
    verses = scan_book(text)
    out_lines: list[str] = []
    parsed = 0
    skipped: list[str] = []
    for verse in verses:
        tree = parse_tokens(parser, verse.tokens)
        if tree is None:
            skipped.append(verse.reference)
            continue
        parsed += 1
        out_lines.append(verse.reference + "\n")
        # pasuq-level error verses print the reference line only (no tree); the C
        # `pasuq : error` actions call free_nodes without print_tree.
        if tree is not LOCATION_ONLY:
            out_lines.append(print_tree(tree, 0))
    stats = BookRun(bb="", verse_count=len(verses), parsed_count=parsed, skipped_refs=skipped)
    return "".join(out_lines), stats, ""


def default_in_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "goerwitz" / "wlc_422_psf"


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--in-dir",
        type=Path,
        default=default_in_dir(repo_root),
        help="Directory containing new-format input files named wlc_422_ps_<bb>.txt.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_out_dir(repo_root),
        help="Directory for PLY outputs named wlc_422_ps_<bb>_ag.txt.",
    )
    parser.add_argument(
        "--book",
        action="append",
        default=None,
        metavar="BB",
        help="Restrict to these book codes (e.g. --book ob). Repeatable. "
        "Default: all input files.",
    )


def _bb_of(input_path: Path) -> str:
    # wlc_422_ps_ob.txt -> ob
    return input_path.stem.removeprefix("wlc_422_ps_")


def run(args: argparse.Namespace) -> None:
    in_dir: Path = args.in_dir
    out_dir: Path = args.out_dir
    if not in_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)

    only = set(args.book) if args.book else None
    parser = build_parser()

    inputs = sorted(
        p
        for p in in_dir.iterdir()
        if p.is_file() and p.name.startswith("wlc_422_ps_") and p.suffix.lower() == ".txt"
    )

    total_parsed = 0
    total_verses = 0
    for input_path in inputs:
        bb = _bb_of(input_path)
        if only is not None and bb not in only:
            continue
        text = input_path.read_text(encoding="utf-8")
        output_text, stats, _ = render_book(text, parser)
        out_path = out_dir / f"wlc_422_ps_{bb}_ag.txt"
        # LF newlines, UTF-8, matching the oracle.
        out_path.write_text(output_text, encoding="utf-8", newline="\n")
        total_parsed += stats.parsed_count
        total_verses += stats.verse_count
        skipped_note = ""
        if stats.skipped_refs:
            shown = ", ".join(stats.skipped_refs[:5])
            if len(stats.skipped_refs) > 5:
                shown += ", ..."
            skipped_note = f"  (skipped {len(stats.skipped_refs)}: {shown})"
        print(
            f"{bb}: parsed {stats.parsed_count}/{stats.verse_count} verses -> {out_path}"
            + skipped_note
        )

    print(f"\nTotal: parsed {total_parsed}/{total_verses} verses across selected books.")
