from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from accgram.goerwitz_stderr_summary import SUMMARY_FILENAME, write_stderr_summary
from accgram.missing_verses import write_missing_verses_json
from accgram.oddballs import write_oddballs_json


@dataclass(frozen=True)
class RunResult:
    input_count: int
    output_count: int
    nonempty_output_count: int
    stderr_nonempty_count: int
    nonzero_exit_count: int


def default_in_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "goerwitz" / "wlc_422_psf"


def default_out_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz"


def default_stderr_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz-stderr"


def default_goerwitz_bin(repo_root: Path) -> Path:
    return repo_root / "accents-1.1.4" / "accents"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--in-dir",
        type=Path,
        default=default_in_dir(repo_root),
        help="Directory containing input files named wlc_422_ps_bb.txt.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=default_out_dir(repo_root),
        help="Directory for outputs named *_ag.txt.",
    )
    parser.add_argument(
        "--stderr-dir",
        type=Path,
        default=default_stderr_dir(repo_root),
        help="Directory for stderr sidecars named *_ag.stderr.txt.",
    )
    parser.add_argument(
        "--goerwitz-bin",
        type=Path,
        default=default_goerwitz_bin(repo_root),
        help="Path to Linux goerwitz binary (invoked via WSL).",
    )


def _to_wsl_path(path: Path) -> str:
    resolved = path.resolve()
    drive = resolved.drive.rstrip(":")
    if not drive:
        return str(resolved).replace("\\", "/")
    rest = resolved.as_posix().split(":", 1)[1]
    return f"/mnt/{drive.lower()}{rest}"


def run(args: argparse.Namespace) -> None:
    result = run_goerwitz_binary(
        in_dir=args.in_dir,
        out_dir=args.out_dir,
        stderr_dir=args.stderr_dir,
        goerwitz_bin=args.goerwitz_bin,
    )
    print(f"Input directory: {args.in_dir}")
    print(f"Output directory: {args.out_dir}")
    print(f"Stderr directory: {args.stderr_dir}")
    print(f"Inputs processed: {result.input_count}")
    print(f"Outputs written: {result.output_count}")
    print(f"Non-empty outputs: {result.nonempty_output_count}")
    print(f"Files with non-empty stderr sidecars: {result.stderr_nonempty_count}")
    print(f"Nonzero goerwitz exit codes: {result.nonzero_exit_count}")

    missing_verses_path = args.out_dir / "_missing_verses.json"
    write_missing_verses_json(args.in_dir, args.out_dir, missing_verses_path)
    print(f"Missing verses JSON: {missing_verses_path}")

    oddballs_path = args.out_dir / "_oddballs.json"
    write_oddballs_json(args.in_dir, args.out_dir, oddballs_path)
    print(f"Oddballs JSON: {oddballs_path}")

    summary_path = args.stderr_dir / SUMMARY_FILENAME
    try:
        summary_result = write_stderr_summary(
            stderr_dir=args.stderr_dir, summary_path=summary_path
        )
        print(
            "Stderr summary: "
            f"{summary_result.summary_path} "
            f"(files={summary_result.files_scanned}, "
            f"non-empty={summary_result.files_with_nonempty_stderr}, "
            f"lines={summary_result.total_stderr_lines}, "
            f"unique-verse-messages={summary_result.total_unique_verse_messages}, "
            f"unique-non-verse-messages={summary_result.total_unique_non_verse_messages})"
        )
    except Exception as exc:  # pragma: no cover - preserve primary pipeline success.
        print(
            f"Warning: failed to write stderr summary at {summary_path}: {exc}",
            file=sys.stderr,
        )


def run_goerwitz_binary(
    in_dir: Path,
    out_dir: Path,
    stderr_dir: Path,
    goerwitz_bin: Path,
) -> RunResult:
    if not in_dir.is_dir():
        raise FileNotFoundError(f"Input directory not found: {in_dir}")
    if not goerwitz_bin.is_file():
        raise FileNotFoundError(f"goerwitz binary not found: {goerwitz_bin}")

    out_dir.mkdir(parents=True, exist_ok=True)
    stderr_dir.mkdir(parents=True, exist_ok=True)

    input_paths = sorted(
        p for p in in_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    nonempty_output_count = 0
    stderr_nonempty_count = 0
    nonzero_exit_count = 0

    goerwitz_wsl_path = _to_wsl_path(goerwitz_bin)
    for input_path in input_paths:
        stem = input_path.stem
        output_path = out_dir / f"{stem}_ag.txt"
        stderr_path = stderr_dir / f"{stem}_ag.stderr.txt"

        payload = input_path.read_text(encoding="utf-8")

        cp = subprocess.run(
            ["wsl", goerwitz_wsl_path, "-p"],
            input=payload.encode("utf-8"),
            capture_output=True,
            check=False,
        )

        stdout_text = cp.stdout.decode("utf-8", errors="replace")
        stderr_text = cp.stderr.decode("utf-8", errors="replace")

        output_path.write_text(stdout_text, encoding="utf-8", newline="\n")
        if stdout_text:
            nonempty_output_count += 1

        if cp.returncode != 0:
            nonzero_exit_count += 1
            if not stderr_text:
                stderr_text = f"goerwitz exited with code {cp.returncode} and produced no stderr output.\n"

        stderr_path.write_text(stderr_text, encoding="utf-8", newline="\n")
        if stderr_text:
            stderr_nonempty_count += 1

    return RunResult(
        input_count=len(input_paths),
        output_count=len(input_paths),
        nonempty_output_count=nonempty_output_count,
        stderr_nonempty_count=stderr_nonempty_count,
        nonzero_exit_count=nonzero_exit_count,
    )
