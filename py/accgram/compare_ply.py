"""Per-verse parity comparator: out/accgram/ply/ vs out/accgram/goerwitz/.

Results are split into clean and oddball buckets (oddballs = verses whose
goerwitz tree contains at least one ERROR node, listed in _oddballs.json).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_VERSE_LABEL_RE = re.compile(
    r"^(?:[1-3]\s*)?[A-Z][A-Za-z_]*(?:\s+[A-Z][A-Za-z_]*)*\s+(\d+):(\d+)\b"
)


def _split_verses(path: Path) -> dict[str, str]:
    """Return {reference_line: verse_block} for every verse in path.

    Each value includes the reference line itself plus all following tree
    lines up to (not including) the next reference line.  Returns {} if the
    file does not exist.
    """
    if not path.is_file():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    verses: dict[str, str] = {}
    current_ref: str | None = None
    current_lines: list[str] = []
    for line in lines:
        stripped = line.rstrip("\r\n")
        if _VERSE_LABEL_RE.match(stripped):
            if current_ref is not None:
                verses[current_ref] = "".join(current_lines)
            current_ref = stripped
            current_lines = [line]
        elif current_ref is not None:
            current_lines.append(line)
    if current_ref is not None:
        verses[current_ref] = "".join(current_lines)
    return verses


def _load_oddball_key_set(oddballs_json: Path) -> set[tuple[str, int, int]]:
    """Return {(bb, ch, vr)} from _oddballs.json entries.

    Each entry's "ref" field has the form "{bb} {ch}:{vr}", e.g. "ob 1:5".
    """
    if not oddballs_json.is_file():
        return set()
    data = json.loads(oddballs_json.read_text(encoding="utf-8"))
    result: set[tuple[str, int, int]] = set()
    for entry in data.get("oddballs", []):
        ref = entry["ref"]
        left, vr_str = ref.rsplit(":", 1)
        bb, ch_str = left.rsplit(" ", 1)
        result.add((bb, int(ch_str), int(vr_str)))
    return result


@dataclass
class BookResult:
    bb: str
    oracle_count: int
    ply_count: int
    clean_match: int = 0
    clean_mismatch: int = 0
    clean_missing: int = 0
    oddball_match: int = 0
    oddball_mismatch: int = 0
    oddball_missing: int = 0
    first_mismatches: list[str] = field(default_factory=list)

    @property
    def total_match(self) -> int:
        return self.clean_match + self.oddball_match

    @property
    def total_oracle(self) -> int:
        return self.oracle_count


@dataclass
class CompareResult:
    books: list[BookResult] = field(default_factory=list)

    @property
    def total_oracle(self) -> int:
        return sum(b.total_oracle for b in self.books)

    @property
    def total_match(self) -> int:
        return sum(b.total_match for b in self.books)

    @property
    def clean_oracle(self) -> int:
        return sum(b.oracle_count - (b.oddball_match + b.oddball_mismatch + b.oddball_missing) for b in self.books)

    @property
    def clean_match(self) -> int:
        return sum(b.clean_match for b in self.books)

    @property
    def oddball_oracle(self) -> int:
        return sum(b.oddball_match + b.oddball_mismatch + b.oddball_missing for b in self.books)

    @property
    def oddball_match(self) -> int:
        return sum(b.oddball_match for b in self.books)


_MAX_MISMATCHES_PER_BOOK = 5


def compare_all(oracle_dir: Path, ply_dir: Path, oddballs_json: Path) -> CompareResult:
    oddball_keys = _load_oddball_key_set(oddballs_json)

    oracle_paths = sorted(
        p
        for p in oracle_dir.iterdir()
        if p.is_file()
        and p.name.startswith("wlc_422_ps_")
        and p.name.endswith("_ag.txt")
    )

    result = CompareResult()
    for oracle_path in oracle_paths:
        stem = oracle_path.stem  # "wlc_422_ps_ob_ag"
        bb = stem.removeprefix("wlc_422_ps_").removesuffix("_ag")

        ply_path = ply_dir / oracle_path.name
        oracle_verses = _split_verses(oracle_path)
        ply_verses = _split_verses(ply_path)

        br = BookResult(bb=bb, oracle_count=len(oracle_verses), ply_count=len(ply_verses))

        for ref_line, oracle_text in oracle_verses.items():
            m = _VERSE_LABEL_RE.match(ref_line)
            ch, vr = (int(m.group(1)), int(m.group(2))) if m else (0, 0)
            is_oddball = (bb, ch, vr) in oddball_keys

            ply_text = ply_verses.get(ref_line)
            if ply_text is None:
                match_ok = False
                missing = True
            else:
                match_ok = ply_text == oracle_text
                missing = False

            if is_oddball:
                if missing:
                    br.oddball_missing += 1
                elif match_ok:
                    br.oddball_match += 1
                else:
                    br.oddball_mismatch += 1
            else:
                if missing:
                    br.clean_missing += 1
                elif match_ok:
                    br.clean_match += 1
                else:
                    br.clean_mismatch += 1

            if not match_ok and not missing and len(br.first_mismatches) < _MAX_MISMATCHES_PER_BOOK:
                br.first_mismatches.append(ref_line)

        result.books.append(br)

    return result


def _pct(num: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    return f"{100.0 * num / denom:.1f}%"


def print_report(result: CompareResult, oracle_dir: Path, ply_dir: Path) -> None:
    print("=== PLY Parity Report ===")
    print(f"Oracle: {oracle_dir}")
    print(f"PLY:    {ply_dir}")
    print()

    clean_tot = result.clean_oracle
    odd_tot = result.oddball_oracle
    total = result.total_oracle

    print(
        f"Clean verses:   {result.clean_match:>6} / {clean_tot:<6} match  ({_pct(result.clean_match, clean_tot)})"
    )
    print(
        f"Oddball verses: {result.oddball_match:>6} / {odd_tot:<6} match  ({_pct(result.oddball_match, odd_tot)})"
    )
    print(
        f"Total:          {result.total_match:>6} / {total:<6} match  ({_pct(result.total_match, total)})"
    )
    print()

    if any(br.first_mismatches or br.clean_mismatch or br.oddball_mismatch for br in result.books):
        print("First mismatches per book:")
        for br in result.books:
            if br.first_mismatches:
                label = f"  {br.bb}: " + ", ".join(br.first_mismatches[:3])
                if len(br.first_mismatches) == _MAX_MISMATCHES_PER_BOOK:
                    label += " ..."
                print(label)
        print()

    print("Per-book breakdown:")
    header = f"  {'bb':<4}  {'oracle':>6}  {'match':>6}  {'c-ok':>5}  {'c-diff':>6}  {'c-miss':>6}  {'o-ok':>4}  {'o-diff':>6}  {'o-miss':>6}"
    print(header)
    for br in result.books:
        row = (
            f"  {br.bb:<4}  {br.oracle_count:>6}  {br.total_match:>6}"
            f"  {br.clean_match:>5}  {br.clean_mismatch:>6}  {br.clean_missing:>6}"
            f"  {br.oddball_match:>4}  {br.oddball_mismatch:>6}  {br.oddball_missing:>6}"
        )
        print(row)


def write_report_json(result: CompareResult, report_path: Path) -> None:
    books_data = []
    for br in result.books:
        books_data.append(
            {
                "bb": br.bb,
                "oracle_count": br.oracle_count,
                "ply_count": br.ply_count,
                "clean_match": br.clean_match,
                "clean_mismatch": br.clean_mismatch,
                "clean_missing": br.clean_missing,
                "oddball_match": br.oddball_match,
                "oddball_mismatch": br.oddball_mismatch,
                "oddball_missing": br.oddball_missing,
                "first_mismatches": br.first_mismatches,
            }
        )
    payload = {
        "summary": {
            "total_oracle": result.total_oracle,
            "total_match": result.total_match,
            "clean_oracle": result.clean_oracle,
            "clean_match": result.clean_match,
            "oddball_oracle": result.oddball_oracle,
            "oddball_match": result.oddball_match,
        },
        "books": books_data,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def default_oracle_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz"


def default_ply_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply"


def default_oddballs_json(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz" / "_oddballs.json"


def default_report_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply" / "_parity_report.json"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--oracle-dir",
        type=Path,
        default=default_oracle_dir(repo_root),
        help="Directory containing goerwitz *_ag.txt oracle files.",
    )
    parser.add_argument(
        "--ply-dir",
        type=Path,
        default=default_ply_dir(repo_root),
        help="Directory containing PLY *_ag.txt output files to compare.",
    )
    parser.add_argument(
        "--oddballs-json",
        type=Path,
        default=default_oddballs_json(repo_root),
        help="Path to _oddballs.json (used to classify oddball verses).",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=None,
        help="If given, write a JSON parity report to this path.",
    )


def run(args: argparse.Namespace) -> None:
    if not args.oracle_dir.is_dir():
        print(f"Error: oracle directory not found: {args.oracle_dir}", file=sys.stderr)
        sys.exit(1)

    result = compare_all(
        oracle_dir=args.oracle_dir,
        ply_dir=args.ply_dir,
        oddballs_json=args.oddballs_json,
    )

    print_report(result, args.oracle_dir, args.ply_dir)

    if args.report is not None:
        write_report_json(result, args.report)
        print(f"\nReport written to: {args.report}")
