"""Accent grammar utilities.

Subcommands:
    filter-split-wlc
                Split wlc422_ps.txt twice: once as unfiltered per-book files
                and once as filtered per-book files (excluding Psalms/Proverbs,
                poetically-cantillated Job verses, and hardcoded troublemaker
                verses) and write out/accgram/goerwitz/_troublemakers.json.
    run-goerwitz
                Run goerwitz (via WSL) on split files and write *_ag outputs.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py filter-split-wlc
    .venv/Scripts/python.exe py/main_accgram.py run-goerwitz
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import filter_split_wlc, split_wlc
from accgram import run_goerwitz


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_input_path() -> Path:
    # Sibling checkout expected by the user:
    #   GitRepos/wlc-utils-io/in/wlc422/wlc422_ps.txt
    return _repo_root().parent / "wlc-utils-io" / "in" / "wlc422" / "wlc422_ps.txt"


def _run_filter_split_wlc(args: argparse.Namespace) -> None:
    filter_split_wlc.run(args, split_wlc.split_wlc_to_books)


def _run_goerwitz(args: argparse.Namespace) -> None:
    run_goerwitz.run(args)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
    subparsers.required = True

    filter_split_wlc_parser = subparsers.add_parser(
        "filter-split-wlc",
        help=(
            "Split wlc422_ps.txt to both raw and filtered output directories "
            "(filtered excludes Psalms/Proverbs, poetic Job verses, and "
            "hardcoded troublemaker verses; writes _troublemakers.json)."
        ),
    )
    filter_split_wlc.add_args(
        filter_split_wlc_parser,
        default_input_path=_default_input_path(),
        repo_root=_repo_root(),
    )
    filter_split_wlc_parser.set_defaults(func=_run_filter_split_wlc)

    run_goerwitz_parser = subparsers.add_parser(
        "run-goerwitz",
        help=(
            "Run goerwitz (via WSL) on split input files and write *_ag.txt outputs "
            "plus stderr sidecars (default: out/accgram/goerwitz-stderr)."
        ),
    )
    run_goerwitz.add_args(run_goerwitz_parser, repo_root=_repo_root())
    run_goerwitz_parser.set_defaults(func=_run_goerwitz)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
