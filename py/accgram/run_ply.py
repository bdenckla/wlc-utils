"""Driver for the Python PLY port: mirrors `accents -p` on the WLC prose corpus.

Reads the canonical `-kq-u` Unicode source `wlc-utils-io/out/wlc422-kq-u/`, transcodes
each verse into per-book scanner-ready M-C text (uni_to_mc_body, applying the genre
filter so poetic books never reach the prose grammar), scans each verse into a token
stream
(ply_scanner), parses it into a tree (ply_grammar), and writes the reference line
followed by the indented tree (ply_tree.print_tree) -- the same stdout the C
"goerwitz" binary produced with `-p`. Output goes to out/accgram/ply/.

A verse the grammar cannot parse at all (parse_tokens returns None) is a fatal
error: it signals a residual prose-grammar gap that must be surfaced, not silently
skipped. ERROR-trees and location-only (pasuq-level error) verses are not None --
they still print and remain "oddballs".
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from accgram import lexical_validation
from accgram import prose_filter
from accgram import rtms_data
from accgram import uni_to_mc_body
from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.ply_scanner import scan_book
from accgram.ply_tree import add_leaves, print_tree


# The Unicode codepoint each stranded M-C stress-helper code carries, so the
# illegal_mark label can name the offending *Unicode* word (issue #9: M-C dropped,
# reports show the actual pointed Hebrew).  Only ``82`` (zarqa stress-helper /
# tsinnorit, U+0598) is wired up in lexical_validation today.
_STRESS_HELPER_CHAR = {"82": "֘"}


def _illegal_mark_tree(
    marks: list[lexical_validation.StrandedMark], words: list[str]
):
    """Degenerate ERROR tree for a verse carrying stranded stress-helper(s).

    The branch label names each offending code and the pointed-Hebrew word it was
    found in (e.g. ``illegal_mark 82 in יִשְׂרָאֵ֘ל``), so the oddball reports pinpoint
    the word; the single terminal leaf is the bare ``ERROR`` token that
    accgram.oddballs keys on.  ``words`` is the offending Unicode word per mark, in
    order (see `_stranded_unicode_words`).  The *structure* is uniform across all such
    verses (one branch + one ERROR leaf) -- only the descriptive label varies -- so the
    error is attributed to the stranded mark itself rather than to whatever the rest of
    the accent sequence would have parsed into.
    """
    detail = "; ".join(
        f"{mark.code} in {word}" for mark, word in zip(marks, words)
    )
    return add_leaves(f"illegal_mark {detail}", "ERROR")


def _stranded_unicode_words(
    marks: list[lexical_validation.StrandedMark],
    verse: object,
) -> list[str]:
    """The pointed-Hebrew word bearing each stranded mark, aligned to ``marks``.

    Each stranded helper (today only ``82`` = U+0598) lives in exactly one verse word;
    collect the words carrying that codepoint in order and pair them with ``marks``.
    Falls back to a mark's raw M-C atom if the Unicode word cannot be located (so the
    label is always populated)."""
    by_char: dict[str, list[str]] = {}
    for word in _verse_display_words(verse):
        for char in set(by_char) | set(_STRESS_HELPER_CHAR.values()):
            if char in word:
                by_char.setdefault(char, []).append(word)
    cursor: dict[str, int] = {}
    out: list[str] = []
    for mark in marks:
        char = _STRESS_HELPER_CHAR.get(mark.code)
        candidates = by_char.get(char, []) if char else []
        i = cursor.get(char, 0)
        if i < len(candidates):
            out.append(candidates[i])
            cursor[char] = i + 1
        else:
            out.append(mark.atom)
    return out


def _verse_display_words(verse: object):
    """The verse's Unicode words in order, descending into ketiv-qere (qere side)."""
    vels = verse.get("vels") if isinstance(verse, dict) else None
    if not isinstance(vels, list):
        return
    for vel in vels:
        if isinstance(vel, str):
            yield vel
        elif isinstance(vel, dict):
            word = vel.get("word")
            if isinstance(word, str):
                yield word
            kq = vel.get("kq")
            if isinstance(kq, (list, tuple)) and len(kq) == 2:
                for qvel in kq[1]:
                    if isinstance(qvel, str):
                        yield qvel
                    elif isinstance(qvel, dict) and isinstance(qvel.get("word"), str):
                        yield qvel["word"]


@dataclass(frozen=True)
class BookRun:
    bb: str
    verse_count: int
    parsed_count: int


def render_book(
    text: str, parser, bb: str, wlc_index: dict[str, dict] | None = None
) -> tuple[str, BookRun, str]:
    """Return (output_text, stats, bb) for one book's scanner-ready text.

    ``wlc_index`` (the kq-u verse index, keyed by bcv) supplies the pointed-Hebrew word
    for the illegal_mark label; omit it to fall back to the raw M-C atom.
    """
    verses = scan_book(text, bb)
    out_lines: list[str] = []
    parsed = 0
    for verse in verses:
        # Prose lexical layer (divergence from the goerwitz C oracle): a stranded
        # stress-helper (e.g. a `82` with no fused `02`) is an alphabet error.  Flag
        # it uniformly with a fixed ERROR tree and skip the grammar entirely -- the
        # context need not be parsed, and all such verses must read identically.
        stranded = lexical_validation.stranded_stress_helpers(verse.body)
        if stranded:
            parsed += 1
            out_lines.append(verse.reference + "\n")
            bcv = f"{bb}{verse.reference.rpartition(' ')[2]}"
            kq_verse = wlc_index.get(bcv) if wlc_index else None
            words = _stranded_unicode_words(stranded, kq_verse)
            out_lines.append(print_tree(_illegal_mark_tree(stranded, words), 0))
            continue
        tree = parse_tokens(parser, verse.tokens)
        if tree is None:
            raise RuntimeError(f"PLY produced no output for {verse.reference}")
        parsed += 1
        out_lines.append(verse.reference + "\n")
        # pasuq-level error verses print the reference line only (no tree); the C
        # `pasuq : error` actions call free_nodes without print_tree.
        if tree is not LOCATION_ONLY:
            out_lines.append(print_tree(tree, 0))
    stats = BookRun(bb="", verse_count=len(verses), parsed_count=parsed)
    return "".join(out_lines), stats, ""


def default_input_path(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "wlc422-kq-u"


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply"


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
        help="Directory for PLY outputs named wlc_422_ps_<bb>_ag.txt.",
    )
    parser.add_argument(
        "--book",
        action="append",
        default=None,
        metavar="BB",
        help="Restrict to these book codes (e.g. --book ob). Repeatable. "
        "Default: all books.",
    )


def run(args: argparse.Namespace) -> None:
    input_path: Path = args.input
    out_dir: Path = args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    only = set(args.book) if args.book else None
    parser = build_parser()

    book_texts = uni_to_mc_body.build_book_texts(
        input_path, keep_line_fn=prose_filter.should_keep_line
    )
    wlc_index = rtms_data.load_wlc422_index(input_path)

    total_parsed = 0
    total_verses = 0
    for bb, text in book_texts.items():
        if only is not None and bb not in only:
            continue
        output_text, stats, _ = render_book(text, parser, bb, wlc_index)
        out_path = out_dir / f"wlc_422_ps_{bb}_ag.txt"
        # UTF-8; native platform line endings (CRLF on Windows), per .gitattributes / issue #14.
        out_path.write_text(output_text, encoding="utf-8")
        total_parsed += stats.parsed_count
        total_verses += stats.verse_count
        print(
            f"{bb}: parsed {stats.parsed_count}/{stats.verse_count} verses -> {out_path}"
        )

    print(f"\nTotal: parsed {total_parsed}/{total_verses} verses across selected books.")
