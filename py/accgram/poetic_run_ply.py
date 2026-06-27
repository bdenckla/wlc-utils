"""Driver for the POETIC (Three Books) PLY scanner + grammar over the corpus.

The poetic counterpart of accgram.prose_run_ply.  Reads the canonical `-kq-u` Unicode source
``out/wlc422-kq-u/`` (transcoded to scanner-ready M-C text by
uni_to_marks), keeps only the poetic verses (Psalms and Proverbs wholesale plus
poetically-cantillated Job, via poetic_filter), scans each
verse with poetic_ply_scanner, reconciles the tokens against MAM (poetic_reconcile:
the legarmeh-vs-paseq and unmarked-oleh corrections the M-C source cannot express),
parses the result with poetic_ply_grammar, then writes the reference line followed by
the indented tree -- the same shape prose_run_ply writes for the prose books.  Output goes
to out/accgram/ply-poetic/.

Unlike the prose driver, an unparseable verse is NOT fatal.  The poetic grammar is
derived from Yeivin (no C oracle) and a small fraction of verses are known
structural oddballs; making each one fatal would block the whole corpus run.  So a
verse the grammar cannot parse (parse_tokens returns None) is emitted as a
``NO_PARSE`` line
carrying its scanned token types -- inspectable in the tracked output and tallied
-- and the run continues.  This output is the verification surface later phases
diff against.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from accgram import poetic_filter
from accgram import uni_to_marks
from accgram.mam_poetic_accents import load_poetic_disjunctives
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram.poetic_ply_grammar import (
    ParseError,
    build_parser,
    parse_tokens_accepting_repeats,
)
from accgram.poetic_ply_scanner import scan_book
from accgram.ply_tree import TN, print_tree
from accgram.poetic_reconcile import reconcile_tokens

import repo_paths


@dataclass(frozen=True)
class BookRun:
    bb: str
    verse_count: int
    parsed_count: int  # clean parses (no ERROR leaf)
    oddball_count: int  # category-A missing-silluq ERROR-leaf trees
    no_parse_count: int  # unrecoverable failures (NO_PARSE lines)


def has_error_leaf(tree: TN) -> bool:
    """True if the tree contains an ERROR leaf (a recovered missing-silluq verse)."""
    if tree.left is None:
        return "ERROR" in tree.leaves
    return has_error_leaf(tree.left) or has_error_leaf(tree.right)


def no_parse_line(
    tokens: list[tuple[str, str]], error: ParseError | None = None
) -> str:
    """A greppable placeholder for an unparseable verse, naming its token types.

    The TILDE/SOFPASUQ structural bookends are dropped; only the accent token types
    between them are listed, so the failing accent sequence is visible at a glance
    (e.g. ``NO_PARSE: PAZER SILLUQ``).

    When ``error`` (the ParseError from parse_tokens_diagnostic) is supplied, the
    stall accent is bracketed with ``>> <<`` and a trailing ``(stalled at accent
    k/n)`` note is appended, so the line pinpoints where the parse dead-ended rather
    than implicating the whole verse.  The ``NO_PARSE:`` prefix is kept either way so
    the lines stay greppable.
    """
    accents = [t for t, _ in tokens if t not in ("TILDE", "SOFPASUQ")]
    if error is None:
        return "NO_PARSE: " + " ".join(accents) + "\n"
    marked = list(accents)
    i = error.accent_index - 1
    if 0 <= i < len(marked):
        marked[i] = f">>{marked[i]}<<"
    return (
        "NO_PARSE: "
        + " ".join(marked)
        + f"  (stalled at accent {error.accent_index}/{len(accents)}: "
        + f"{error.token_type})\n"
    )


def render_book(
    text: str, parser, bb: str, mam_disj_by_ref: dict[str, list[str]]
) -> tuple[str, BookRun]:
    """Return (output_text, stats) for one book's scanner-ready text.

    Each verse's scanned tokens are first reconciled (poetic_reconcile) against the
    MAM disjunctive skeleton so the legarmeh-vs-paseq and unmarked-oleh corrections
    WLC's M-C source cannot express are applied before the grammar sees the tokens.
    """
    verses = scan_book(text, bb)
    out_lines: list[str] = []
    parsed = 0
    oddballs = 0
    no_parse = 0
    for verse in verses:
        out_lines.append(verse.reference + "\n")
        tokens = reconcile_tokens(
            verse.reference,
            verse.body,
            list(verse.tokens),
            mam_disj_by_ref.get(verse.reference),
            parser,
        )
        tree, error = parse_tokens_accepting_repeats(parser, tokens)
        if tree is None:
            no_parse += 1
            out_lines.append(no_parse_line(tokens, error))
            continue
        if has_error_leaf(tree):
            oddballs += 1
        else:
            parsed += 1
        out_lines.append(print_tree(tree, 0))
    return "".join(out_lines), BookRun(
        bb=bb,
        verse_count=len(verses),
        parsed_count=parsed,
        oddball_count=oddballs,
        no_parse_count=no_parse,
    )


def default_input_path(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "wlc422-kq-u"


def default_out_dir(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "accgram" / "ply-poetic"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input_path(repo_root),
        help="Directory of the -kq-u Unicode source (wlc422-kq-u/1verses_*.json).",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_out_dir(repo_root),
        help="Directory for poetic PLY outputs named wlc_422_ps_<bb>_ag.txt.",
    )
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=default_mam_simple_dir(repo_root),
        help="Directory containing MAM-simple json-vtrad-bhs book files "
        "(the legarmeh-vs-paseq oracle for token reconciliation).",
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
    mam_disj_by_ref = load_poetic_disjunctives(args.mam_simple_dir)

    book_texts = uni_to_marks.build_book_texts(
        input_path, keep_line_fn=poetic_filter.should_keep_line
    )

    total_parsed = 0
    total_oddballs = 0
    total_no_parse = 0
    total_verses = 0
    for bb, text in book_texts.items():
        if only is not None and bb not in only:
            continue
        output_text, stats = render_book(text, parser, bb, mam_disj_by_ref)
        out_path = out_dir / f"wlc_422_ps_{bb}_ag.txt"
        # UTF-8; native platform line endings (CRLF on Windows), per .gitattributes / issue #14.
        out_path.write_text(output_text, encoding="utf-8")
        total_parsed += stats.parsed_count
        total_oddballs += stats.oddball_count
        total_no_parse += stats.no_parse_count
        total_verses += stats.verse_count
        rate = 100.0 * stats.parsed_count / stats.verse_count if stats.verse_count else 0.0
        print(
            f"{bb}: parsed {stats.parsed_count}/{stats.verse_count} ({rate:.1f}%) clean"
            f"; {stats.oddball_count} missing-silluq oddball(s), "
            f"{stats.no_parse_count} NO_PARSE -> {out_path}"
        )

    total_rate = 100.0 * total_parsed / total_verses if total_verses else 0.0
    print(
        f"\nTotal: {total_parsed}/{total_verses} ({total_rate:.2f}%) clean parses"
        f"; {total_oddballs} missing-silluq ERROR-leaf oddball(s); "
        f"{total_no_parse} NO_PARSE across selected poetic books."
    )
