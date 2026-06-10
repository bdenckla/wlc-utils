"""Run the PLY port on the hard-coded "troublemaker" verses and categorize.

The 49 troublemakers (accgram.tms.HARDCODED_REFS) produce *no output* from the
Goerwitz C `accents` binary, so they are excluded from the normal pipeline before
either parser sees them.  This driver asks the empirical question: what does the
*PLY* port do with them?  It reads them from the **unfiltered** split dir
(wlc_422_ps/, which still contains them), scans + parses each, and sorts the result
into one of four buckets:

    clean          -- a tree with no ERROR leaf (full parse)
    error-tree     -- a tree containing >=1 ERROR leaf (grammar error, recovered)
    location-only  -- pasuq-level error: reference line only, no tree
    no-output      -- parse failed with no recovery (same trouble as the C binary)

`clean` + `error-tree` are the verses PLY handles gracefully -- candidates for
reclassification out of HARDCODED_REFS (reported, never auto-applied here).

Outputs (default out/accgram/ply-tms/):
  - wlc_422_ps_<bb>_ag.txt   per-book trees (reference line + tree, like run-ply)
  - _run_ply_tms.json        per-verse buckets + summary + candidate list
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from accgram import tms
from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.ply_scanner import scan_book
from accgram.ply_tree import print_tree
from mb_cmn import provenance

# Same ERROR-token detection convention used by oddballs.py.
_ERROR_RE = re.compile(r"\bERROR\b")

# Bucket names (also the JSON/console keys).
CLEAN = "clean"
ERROR_TREE = "error-tree"
LOCATION_ONLY_BUCKET = "location-only"
NO_OUTPUT = "no-output"
MISSING_INPUT = "missing-input"

_BUCKET_ORDER = (CLEAN, ERROR_TREE, LOCATION_ONLY_BUCKET, NO_OUTPUT, MISSING_INPUT)

# Buckets where PLY produced strictly more than the C binary's nothing AND a tree.
_GRACEFUL = (CLEAN, ERROR_TREE)


@dataclass
class VerseResult:
    ref: tuple[str, int, int]  # (bb, chnu, vrnu)
    reference: str  # full new-format reference, e.g. "Obadiah 1:1" ("" if missing)
    bucket: str
    tree_text: str  # rendered tree ("" for location-only / no-output / missing)

    @property
    def ref_str(self) -> str:
        return tms.format_ref(self.ref)


def default_in_dir(repo_root: Path) -> Path:
    # Unfiltered split -- still contains the troublemakers (filtered psf/ does not).
    return repo_root.parent / "wlc-utils-io" / "out" / "goerwitz" / "wlc_422_ps"


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-tms"


def _refs_by_book() -> dict[str, set[tuple[int, int]]]:
    by_book: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for bb, chnu, vrnu in tms.HARDCODED_REFS:
        by_book[bb].add((chnu, vrnu))
    return by_book


def _ref_chvs(reference: str) -> tuple[int, int] | None:
    """Extract (chnu, vrnu) from a new-format reference like "Obadiah 1:1"."""
    tail = reference.rsplit(" ", 1)[-1]
    if ":" not in tail:
        return None
    ch, _, vs = tail.partition(":")
    if not (ch.isdigit() and vs.isdigit()):
        return None
    return int(ch), int(vs)


def _classify(tree) -> tuple[str, str]:
    """Return (bucket, tree_text) for a parse_tokens result."""
    if tree is None:
        return NO_OUTPUT, ""
    if tree is LOCATION_ONLY:
        return LOCATION_ONLY_BUCKET, ""
    tree_text = print_tree(tree, 0)
    bucket = ERROR_TREE if _ERROR_RE.search(tree_text) else CLEAN
    return bucket, tree_text


def run_book(bb: str, text: str, wanted: set[tuple[int, int]], parser) -> list[VerseResult]:
    """Parse the troublemaker verses of one book; return one VerseResult each."""
    found: dict[tuple[int, int], VerseResult] = {}
    for verse in scan_book(text):
        chvs = _ref_chvs(verse.reference)
        if chvs is None or chvs not in wanted:
            continue
        bucket, tree_text = _classify(parse_tokens(parser, verse.tokens))
        chnu, vrnu = chvs
        found[chvs] = VerseResult(
            ref=(bb, chnu, vrnu),
            reference=verse.reference,
            bucket=bucket,
            tree_text=tree_text,
        )
    # Any wanted ref not present in the unfiltered input is flagged, not dropped.
    for chnu, vrnu in wanted:
        found.setdefault(
            (chnu, vrnu),
            VerseResult(ref=(bb, chnu, vrnu), reference="", bucket=MISSING_INPUT, tree_text=""),
        )
    return [found[chvs] for chvs in sorted(found)]


def _book_output_text(results: list[VerseResult]) -> str:
    """Reference line + tree for verses that produced output (like run_ply)."""
    out: list[str] = []
    for r in results:
        if r.bucket in (CLEAN, ERROR_TREE):
            out.append(r.reference + "\n")
            out.append(r.tree_text)
        elif r.bucket == LOCATION_ONLY_BUCKET:
            out.append(r.reference + "\n")
    return "".join(out)


def _write_report_json(results: list[VerseResult], out_path: Path) -> None:
    counts = {bucket: 0 for bucket in _BUCKET_ORDER}
    for r in results:
        counts[r.bucket] += 1
    candidates = [r.ref_str for r in results if r.bucket in _GRACEFUL]
    payload = {
        "summary": {
            "troublemakers_total": len(results),
            "by_bucket": counts,
            "reclassification_candidates": candidates,
        },
        "verses": [
            {
                "ref": r.ref_str,
                "reference": r.reference,
                "bucket": r.bucket,
                "tree": r.tree_text,
            }
            for r in results
        ],
    }
    payload = provenance.with_json_provenance(payload, __file__)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")


def _print_summary(results: list[VerseResult], in_dir: Path, out_dir: Path) -> None:
    counts = {bucket: 0 for bucket in _BUCKET_ORDER}
    for r in results:
        counts[r.bucket] += 1
    print("=== PLY on troublemakers ===")
    print(f"Input:  {in_dir}")
    print(f"Output: {out_dir}")
    print()
    total = len(results)
    for bucket in _BUCKET_ORDER:
        print(f"  {bucket:<14} {counts[bucket]:>3} / {total}")
    print()
    graceful = [r for r in results if r.bucket in _GRACEFUL]
    print(f"PLY handles {len(graceful)}/{total} gracefully (clean + error-tree):")
    for r in graceful:
        print(f"  {r.ref_str:<10} {r.bucket}")
    stuck = [r for r in results if r.bucket in (NO_OUTPUT, MISSING_INPUT)]
    if stuck:
        print()
        print("Still no tree:")
        for r in stuck:
            print(f"  {r.ref_str:<10} {r.bucket}")


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--in-dir",
        type=Path,
        default=default_in_dir(repo_root),
        help="Unfiltered new-format input dir (wlc_422_ps_<bb>.txt) that still "
        "contains the troublemakers.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_out_dir(repo_root),
        help="Directory for per-book trees and _run_ply_tms.json.",
    )
    parser.add_argument(
        "--book",
        action="append",
        default=None,
        metavar="BB",
        help="Restrict to these book codes (e.g. --book ob). Repeatable.",
    )


def classify_all(in_dir: Path, only: set[str] | None = None) -> list[VerseResult]:
    """Parse every troublemaker (optionally restricted to `only` books)."""
    if not in_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")
    parser = build_parser()
    results: list[VerseResult] = []
    for bb, wanted in sorted(_refs_by_book().items()):
        if only is not None and bb not in only:
            continue
        book_path = in_dir / f"wlc_422_ps_{bb}.txt"
        if not book_path.is_file():
            for chnu, vrnu in sorted(wanted):
                results.append(
                    VerseResult(ref=(bb, chnu, vrnu), reference="", bucket=MISSING_INPUT, tree_text="")
                )
            continue
        results.extend(run_book(bb, book_path.read_text(encoding="utf-8"), wanted, parser))
    return results


def run(args: argparse.Namespace) -> None:
    in_dir: Path = args.in_dir
    out_dir: Path = args.out_dir
    only = set(args.book) if args.book else None

    results = classify_all(in_dir, only)

    out_dir.mkdir(parents=True, exist_ok=True)
    by_book: dict[str, list[VerseResult]] = defaultdict(list)
    for r in results:
        by_book[r.ref[0]].append(r)
    for bb, book_results in sorted(by_book.items()):
        text = _book_output_text(book_results)
        if text:
            (out_dir / f"wlc_422_ps_{bb}_ag.txt").write_text(
                text, encoding="utf-8", newline="\n"
            )

    _write_report_json(results, out_dir / "_run_ply_tms.json")
    _print_summary(results, in_dir, out_dir)
