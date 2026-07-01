"""Repo maintenance: clean .novc/, run the pytest suite, run the routine rebuild.

Run from anywhere (each step resolves paths via ``repo_paths.repo_root()``):

    python py/main_repo_maintenance.py
    python py/main_repo_maintenance.py --skip-novc
    python py/main_repo_maintenance.py --skip-tests
    python py/main_repo_maintenance.py --skip-rebuild
    python py/main_repo_maintenance.py --continue-on-test-failure

Three independent steps, in order:

1. Wipe the gitignored ``.novc/`` scratch dir. Everything in it is a
   regenerable download cache or tool output, never a durable result.
2. Run ``pytest py/tests`` (the whole repo's test suite).
3. Run ``py/main_0_mega.py``, the routine downstream rebuild -- every
   parameterless, non-download rebuild step (vendored-file sync, WLC
   JSON/Unicode, accgram, the 4.20/4.22 diffs, and the a-notes build).

The rebuild step is skipped if the test step failed, unless
``--continue-on-test-failure`` is given.
"""

import argparse
import shutil
import subprocess
import sys

from cmn.utf8_io import force_utf8_io

import repo_paths

_REPO = repo_paths.repo_root()
_NOVC = _REPO / ".novc"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-novc", action="store_true", help="don't clean .novc/"
    )
    parser.add_argument(
        "--skip-tests", action="store_true", help="don't run the test suite"
    )
    parser.add_argument(
        "--skip-rebuild", action="store_true", help="don't run py/main_0_mega.py"
    )
    parser.add_argument(
        "--continue-on-test-failure",
        action="store_true",
        help="run the rebuild step even if a test failed",
    )
    return parser.parse_args()


def clean_novc() -> None:
    if not _NOVC.exists():
        print(".novc: nothing to clean (directory does not exist)")
        return
    removed = sorted(p.name for p in _NOVC.iterdir())
    shutil.rmtree(_NOVC)
    _NOVC.mkdir()
    if removed:
        print(f".novc: removed {len(removed)} entries: {', '.join(removed)}")
    else:
        print(".novc: already empty")


def run_tests() -> bool:
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "py/tests"], cwd=_REPO
    )
    ok = result.returncode == 0
    print(f"tests: {'OK' if ok else f'FAILED (exit {result.returncode})'}")
    return ok


def run_rebuild() -> bool:
    script = _REPO / "py" / "main_0_mega.py"
    result = subprocess.run([sys.executable, str(script)], cwd=_REPO)
    print(
        "rebuild: OK"
        if result.returncode == 0
        else f"rebuild: FAILED (exit {result.returncode})"
    )
    return result.returncode == 0


def main() -> None:
    # Line-buffer so status lines interleave correctly with the child
    # processes' own output when stdout isn't a live terminal (e.g. redirected
    # to a log file).
    sys.stdout.reconfigure(line_buffering=True)
    args = _parse_args()
    ok = True
    tests_ok = True

    if not args.skip_novc:
        clean_novc()

    if not args.skip_tests:
        tests_ok = run_tests()
        ok = tests_ok and ok

    if not args.skip_rebuild:
        if tests_ok or args.continue_on_test_failure:
            ok = run_rebuild() and ok
        else:
            print(
                "rebuild: skipped (tests failed; pass --continue-on-test-failure "
                "to run anyway)"
            )
            ok = False

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    force_utf8_io()
    main()
