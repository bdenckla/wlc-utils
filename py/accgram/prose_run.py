"""Driver for the Python port: mirrors `accents -p` on the WLC prose corpus.

Reads the canonical `-kq-u` Unicode source `out/wlc422-kq-u/`, transcodes
each verse into per-book scanner-ready mark text (uni_to_marks, applying the genre
filter so poetic books never reach the prose grammar), scans each verse into a token
stream (prose_scanner), parses it into a tree (prose_ply_grammar), and writes one
JSON record per verse to out/accgram/prose/wlc_422_ps_<bb>_ag.json (issue #20,
replacing the legacy bespoke indented-tree text).  Each record pairs the verse's
``input`` (pointed-Hebrew unicode + raw mark body + token stream) with the full parse
``tree`` -- so "how the input parses" is shown for every verse, not just the handful
of illegal-mark cases the old text format named.

A verse the grammar cannot parse at all (parse_tokens returns None) is a fatal
error: it signals a residual prose-grammar gap that must be surfaced, not silently
skipped. ERROR-trees and location-only (pasuq-level error) verses are not None --
they still emit a record and remain "oddballs".
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from accgram import accent_marks as am
from accgram import lexical_validation
from accgram import prose_filter
from accgram import rtms_data
from accgram import uni_to_marks
from accgram.prose_ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.prose_scanner import scan_book
from accgram.tree import TN, add_leaves, tree_to_obj
import wlc_provenance as provenance

import repo_paths

# Base letter the JSON ``input.marks`` field hangs each accent on.  The scanner's
# own mark body uses the opaque ``am.LETTER`` ("X") placeholder, but a Hebrew accent
# combining mark sitting on a Latin X renders unpredictably across fonts, so the
# display copy substitutes alef -- a true Hebrew base.  Display only: the scanned
# ``verse.body`` keeps "X" for the grammar/lexical layers.
_MARKS_BASE_LETTER = "א"  # alef (א)


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

    Each illegal mark carries a ``rep_char`` -- a codepoint of the offending word unique
    enough to locate it (``82`` = the zarqa stress-helper U+0598; a same-letter pair =
    its first/distinguishing mark, e.g. mahapakh U+05A4, NOT the tipeḥa that recurs
    elsewhere in lv25:20).  Collect the words carrying each rep_char in order and pair
    them with ``marks``.  Falls back to a mark's raw M-C atom if the Unicode word cannot
    be located (so the label is always populated)."""
    rep_chars = {mark.rep_char for mark in marks}
    by_char: dict[str, list[str]] = {}
    for word in _verse_display_words(verse):
        for char in rep_chars:
            if char in word:
                by_char.setdefault(char, []).append(word)
    cursor: dict[str, int] = {}
    out: list[str] = []
    for mark in marks:
        char = mark.rep_char
        candidates = by_char.get(char, [])
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


def _tree_has_error(tree: TN | None) -> bool:
    """True if any leaf of ``tree`` carries the ERROR token (an oddball verse)."""
    if tree is None:
        return False
    if tree.left is not None:
        return _tree_has_error(tree.left) or _tree_has_error(tree.right)
    return "ERROR" in tree.leaves


def _verse_record(
    verse, bb: str, parser, wlc_index: dict[str, dict] | None
) -> dict[str, object]:
    """Build one verse's JSON record: ref, bcv, status, input, tree, [errors].

    ``status`` is one of ``illegal_mark`` (a lexical/alphabet error, fixed ERROR
    tree), ``location_only`` (a pasuq-level error, no tree), ``oddball`` (a parse
    tree carrying an ERROR leaf), or ``clean``.  The ``input`` block carries the
    pointed-Hebrew ``unicode`` (from the -kq-u source), the ``marks`` body (the scan
    body with its accents re-based onto alef for font safety, see _MARKS_BASE_LETTER),
    and the ``tokens`` stream, for every verse -- not just the illegal-mark cases.
    """
    tail = verse.reference.rpartition(" ")[2]
    chnu_str, _, vrnu_str = tail.partition(":")
    bcv = f"{bb}{tail}"
    record: dict[str, object] = {
        "ref": verse.reference,
        "bcv": bcv,
        "input": {
            "unicode": rtms_data.verse_unicode_text(
                wlc_index, bb, int(chnu_str), int(vrnu_str)
            )
            if wlc_index
            else "",
            "marks": verse.body.replace(am.LETTER, _MARKS_BASE_LETTER),
            "tokens": [token.type for token in verse.tokens],
        },
    }

    # Prose lexical layer (divergence from the goerwitz C oracle): an alphabet /
    # word-placement error -- a stranded stress-helper, a same-letter accent pair, or
    # a misplaced telisha qetanna (full enumeration in lexical_validation.lexical_
    # oddballs).  Flag it uniformly with a fixed ERROR tree and skip the grammar
    # entirely -- the context need not be parsed, and all such verses read identically.
    stranded = lexical_validation.lexical_oddballs(verse.body)
    if stranded:
        kq_verse = wlc_index.get(bcv) if wlc_index else None
        words = _stranded_unicode_words(stranded, kq_verse)
        record["status"] = "illegal_mark"
        record["errors"] = [
            {"code": mark.code, "word": word, "atom": mark.atom}
            for mark, word in zip(stranded, words)
        ]
        record["tree"] = tree_to_obj(_illegal_mark_tree(stranded, words))
        return record

    tree = parse_tokens(parser, verse.tokens)
    if tree is None:
        raise RuntimeError(f"parser produced no output for {verse.reference}")
    # pasuq-level error verses carry no tree; the C `pasuq : error` actions call
    # free_nodes without print_tree.
    if tree is LOCATION_ONLY:
        record["status"] = "location_only"
        record["tree"] = None
    else:
        record["status"] = "oddball" if _tree_has_error(tree) else "clean"
        record["tree"] = tree_to_obj(tree)
    return record


def render_book(
    text: str, parser, bb: str, wlc_index: dict[str, dict] | None = None
) -> tuple[list[dict[str, object]], BookRun]:
    """Return (verse_records, stats) for one book's scanner-ready text.

    ``wlc_index`` (the kq-u verse index, keyed by bcv) supplies each verse's
    pointed-Hebrew ``input.unicode`` and the illegal_mark label word; omit it to
    leave unicode empty and fall back to the raw M-C atom.
    """
    verses = scan_book(text, bb)
    records = [_verse_record(verse, bb, parser, wlc_index) for verse in verses]
    stats = BookRun(bb=bb, verse_count=len(verses), parsed_count=len(records))
    return records, stats


def default_input_path(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "wlc422-kq-u"


def default_out_dir(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "accgram" / "prose"


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
        help="Directory for outputs named wlc_422_ps_<bb>_ag.json.",
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

    book_texts = uni_to_marks.build_book_texts(
        input_path, keep_line_fn=prose_filter.should_keep_line
    )
    wlc_index = rtms_data.load_wlc422_index(input_path)

    total_parsed = 0
    total_verses = 0
    for bb, text in book_texts.items():
        if only is not None and bb not in only:
            continue
        records, stats = render_book(text, parser, bb, wlc_index)
        out_path = out_dir / f"wlc_422_ps_{bb}_ag.json"
        _write_book_json(out_path, records)
        total_parsed += stats.parsed_count
        total_verses += stats.verse_count
        print(
            f"{bb}: parsed {stats.parsed_count}/{stats.verse_count} verses -> {out_path}"
        )

    print(f"\nTotal: parsed {total_parsed}/{total_verses} verses across selected books.")


def _book_summary(records: list[dict[str, object]]) -> dict[str, int]:
    counts = {"verses": len(records), "oddballs": 0, "illegal_marks": 0, "location_only": 0}
    for record in records:
        if record["status"] == "oddball":
            counts["oddballs"] += 1
        elif record["status"] == "illegal_mark":
            counts["illegal_marks"] += 1
        elif record["status"] == "location_only":
            counts["location_only"] += 1
    return counts


def _write_book_json(out_path: Path, records: list[dict[str, object]]) -> None:
    payload: dict[str, object] = {
        "summary": _book_summary(records),
        "verses": records,
    }
    payload = provenance.with_json_provenance(payload, __file__)
    with out_path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
