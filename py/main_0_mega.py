"""Run all top-level wlc-utils Python workflows in sequence."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from cmn.utf8_io import force_utf8_io


@dataclass(frozen=True)
class Step:
    name: str
    argv: tuple[str, ...]


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _steps(repo_root: Path) -> tuple[Step, ...]:
    py_dir = repo_root / "py"
    return (
        Step(
            name="update_vendored_files",
            argv=(sys.executable, str(py_dir / "main_update_vendored_files.py")),
        ),
        Step(
            name="accgram_run_ply",
            argv=(sys.executable, str(py_dir / "main_accgram.py"), "run-ply-goerwitz"),
        ),
        Step(
            name="accgram_research_oddballs",
            argv=(
                sys.executable,
                str(py_dir / "main_accgram.py"),
                "generate-goerwitz-html",
            ),
        ),
        Step(
            name="wlc_json_and_unicode",
            argv=(sys.executable, str(py_dir / "main_wlc_json_and_unicode.py")),
        ),
        Step(
            name="wlc_diffs_420422",
            argv=(sys.executable, str(py_dir / "main_wlc_diffs_420422.py")),
        ),
        Step(
            name="wlc_a_notes",
            argv=(sys.executable, str(py_dir / "main_wlc_a_notes.py")),
        ),
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the workflow steps without executing them.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    repo_root = _repo_root()
    steps = _steps(repo_root)

    if args.list:
        for index, step in enumerate(steps, start=1):
            print(f"{index}. {step.name}: {' '.join(step.argv)}")
        return

    started_all = time.perf_counter()
    print(f"[mega] Starting {len(steps)} steps from {repo_root}")

    for index, step in enumerate(steps, start=1):
        started_step = time.perf_counter()
        print("")
        print(f"[mega] Step {index}/{len(steps)}: {step.name}")
        print(f"[mega] Command: {' '.join(step.argv)}")

        completed = subprocess.run(step.argv, cwd=repo_root, check=False)
        elapsed_step = time.perf_counter() - started_step
        print(f"[mega] Step result: rc={completed.returncode} in {elapsed_step:.2f}s")

        if completed.returncode != 0:
            elapsed_all = time.perf_counter() - started_all
            print(f"[mega] Stopped after failure in {elapsed_all:.2f}s")
            raise SystemExit(completed.returncode)

    elapsed_all = time.perf_counter() - started_all
    print("")
    print(f"[mega] Complete: all steps succeeded in {elapsed_all:.2f}s")


if __name__ == "__main__":
    force_utf8_io()
    main()
