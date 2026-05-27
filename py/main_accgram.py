"""Accent grammar utilities.

Subcommands:
    filter-split-wlc
                Split wlc422_ps.txt twice: once as unfiltered per-book files
                and once as filtered per-book files (excluding Psalms/Proverbs,
                poetically-cantillated Job verses, and hardcoded troublemaker
                verses) and write out/accgram/goerwitz/_troublemakers.json.
    research-tms
                Enrich out/accgram/goerwitz/_troublemakers.json with matching
                wlc422-kq-u verse objects and structured XML-ish UXLC verse
                nodes and write out/accgram/research-troublemakers.json.
    fresh-run-goerwitz
                Run filter-split-wlc, then run goerwitz on the freshly written
                filtered split files.
    run-goerwitz
                Run goerwitz (via WSL) on split files and write *_ag outputs.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py filter-split-wlc
    .venv/Scripts/python.exe py/main_accgram.py research-tms
    .venv/Scripts/python.exe py/main_accgram.py fresh-run-goerwitz
    .venv/Scripts/python.exe py/main_accgram.py run-goerwitz
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import filter_split_wlc, research_troublemakers, split_wlc
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


def _run_research_troublemakers(args: argparse.Namespace) -> None:
    research_troublemakers.run(args)


def _run_fresh_run_goerwitz(args: argparse.Namespace) -> None:
    filter_split_wlc.run(args, split_wlc.split_wlc_to_books)
    run_goerwitz.run(
        argparse.Namespace(
            in_dir=args.out_dir,
            out_dir=args.goerwitz_out_dir,
            stderr_dir=args.stderr_dir,
            goerwitz_bin=args.goerwitz_bin,
        )
    )


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

    fresh_run_goerwitz_parser = subparsers.add_parser(
        "fresh-run-goerwitz",
        help=(
            "Run filter-split-wlc, then run goerwitz on the freshly filtered split files "
            "using that filtered output directory as the goerwitz input."
        ),
    )
    filter_split_wlc.add_args(
        fresh_run_goerwitz_parser,
        default_input_path=_default_input_path(),
        repo_root=_repo_root(),
    )
    fresh_run_goerwitz_parser.add_argument(
        "--goerwitz-out-dir",
        type=Path,
        default=run_goerwitz.default_out_dir(_repo_root()),
        help="Directory for goerwitz outputs named *_ag.txt.",
    )
    fresh_run_goerwitz_parser.add_argument(
        "--stderr-dir",
        type=Path,
        default=run_goerwitz.default_stderr_dir(_repo_root()),
        help="Directory for goerwitz stderr sidecars named *_ag.stderr.txt.",
    )
    fresh_run_goerwitz_parser.add_argument(
        "--goerwitz-bin",
        type=Path,
        default=run_goerwitz.default_goerwitz_bin(_repo_root()),
        help="Path to Linux goerwitz binary (invoked via WSL).",
    )
    fresh_run_goerwitz_parser.set_defaults(func=_run_fresh_run_goerwitz)

    run_goerwitz_parser = subparsers.add_parser(
        "run-goerwitz",
        help=(
            "Run goerwitz (via WSL) on split input files and write *_ag.txt outputs "
            "plus stderr sidecars and _missing_verses.json (default: out/accgram/goerwitz-stderr)."
        ),
    )
    run_goerwitz.add_args(run_goerwitz_parser, repo_root=_repo_root())
    run_goerwitz_parser.set_defaults(func=_run_goerwitz)

    research_tms_parser = subparsers.add_parser(
        "research-tms",
        help=(
            "Enrich existing _troublemakers.json entries with matching "
            "wlc422-kq-u verse objects and XML-ish UXLC verse nodes."
        ),
    )
    research_troublemakers.add_args(research_tms_parser, repo_root=_repo_root())
    research_tms_parser.set_defaults(func=_run_research_troublemakers)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
