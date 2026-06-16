"""Driver for the POETIC (Three Books) PLY scanner + grammar over the corpus.

The poetic counterpart of accgram.run_ply.  Reads the canonical source
``wlc-utils-io/in/wlc422/wlc422_ps.txt``, keeps only the poetic verses (Psalms and
Proverbs wholesale plus poetically-cantillated Job, via poetic_filter), scans each
verse with ply_scanner_poetic and parses it with ply_grammar_poetic, then writes
the reference line followed by the indented tree -- the same shape run_ply writes
for the prose books.  Output goes to out/accgram/ply-poetic/.

Unlike the prose driver, an unparseable verse is NOT fatal.  The poetic grammar is
derived from Yeivin (no C oracle) and ~3.6% of verses are known structural
oddballs; making each one fatal would block the whole corpus run.  So a verse the
grammar cannot parse (parse_tokens returns None) is emitted as a ``NO_PARSE`` line
carrying its scanned token types -- inspectable in the tracked output and tallied
-- and the run continues.  This output is the verification surface later phases
diff against.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from accgram import poetic_filter
from accgram import split_wlc
from accgram.ply_grammar_poetic import build_parser, parse_tokens
from accgram.ply_scanner_poetic import scan_book
from accgram.ply_tree import print_tree


@dataclass(frozen=True)
class BookRun:
    bb: str
    verse_count: int
    parsed_count: int


def _no_parse_line(tokens: list[tuple[str, str]]) -> str:
    """A greppable placeholder for an unparseable verse, naming its token types.

    The TILDE/SOFPASUQ structural bookends are dropped; only the accent token types
    between them are listed, so the failing accent sequence is visible at a glance
    (e.g. ``NO_PARSE: PAZER SILLUQ``).
    """
    accents = [t for t, _ in tokens if t not in ("TILDE", "SOFPASUQ")]
    return "NO_PARSE: " + " ".join(accents) + "\n"


def render_book(text: str, parser, bb: str) -> tuple[str, BookRun]:
    """Return (output_text, stats) for one book's scanner-ready text."""
    verses = scan_book(text, bb)
    out_lines: list[str] = []
    parsed = 0
    for verse in verses:
        out_lines.append(verse.reference + "\n")
        tree = parse_tokens(parser, verse.tokens)
        if tree is None:
            out_lines.append(_no_parse_line(verse.tokens))
            continue
        parsed += 1
        out_lines.append(print_tree(tree, 0))
    return "".join(out_lines), BookRun(bb=bb, verse_count=len(verses), parsed_count=parsed)


def default_input_path(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "in" / "wlc422" / "wlc422_ps.txt"


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-poetic"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input_path(repo_root),
        help="Path to source wlc422_ps.txt file.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_out_dir(repo_root),
        help="Directory for poetic PLY outputs named wlc_422_ps_<bb>_ag.txt.",
    )
    parser.add_argument(
        "--book",
        action="append",
        default=None,
        metavar="BB",
        help="Restrict to these book codes (ps, pr, jb). Repeatable. "
        "Default: all three poetic books.",
    )


def run(args: argparse.Namespace) -> None:
    input_path: Path = args.input
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    only = set(args.book) if args.book else None
    parser = build_parser()

    book_texts = split_wlc.split_wlc_to_book_texts(
        input_path, keep_line_fn=poetic_filter.should_keep_line
    )

    total_parsed = 0
    total_verses = 0
    for bb, text in book_texts.items():
        if only is not None and bb not in only:
            continue
        output_text, stats = render_book(text, parser, bb)
        out_path = out_dir / f"wlc_422_ps_{bb}_ag.txt"
        # LF newlines, UTF-8.
        out_path.write_text(output_text, encoding="utf-8", newline="\n")
        total_parsed += stats.parsed_count
        total_verses += stats.verse_count
        rate = 100.0 * stats.parsed_count / stats.verse_count if stats.verse_count else 0.0
        print(
            f"{bb}: parsed {stats.parsed_count}/{stats.verse_count} "
            f"({rate:.1f}%) verses -> {out_path}"
        )

    total_rate = 100.0 * total_parsed / total_verses if total_verses else 0.0
    print(
        f"\nTotal: parsed {total_parsed}/{total_verses} ({total_rate:.1f}%) "
        "verses across selected poetic books."
    )
