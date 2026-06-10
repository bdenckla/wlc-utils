"""Accent grammar utilities.

Subcommands:
    filter-split-wlc
                Split wlc422_ps.txt twice: once as unfiltered per-book files
                and once as filtered per-book files (excluding Psalms/Proverbs,
                poetically-cantillated Job verses, and hardcoded troublemaker
                verses) and write out/accgram/goerwitz/_troublemakers.json.
    research-tms-and-oddballs
                Enrich out/accgram/goerwitz/_troublemakers.json with matching
                wlc422-kq-u verse objects and structured XML-ish UXLC verse
                nodes and write out/accgram/research-troublemakers.json.
                Also enrich out/accgram/goerwitz/_oddballs.json and write
                out/accgram/research-oddballs.json, plus HTML reports
                including gh-pages/accgram/goerwitz.html and
                gh-pages/accgram/goerwitz-obs.html.
    fresh-run-goerwitz
                Run filter-split-wlc, then run goerwitz on the freshly written
                filtered split files.
    run-goerwitz
                Run goerwitz (via WSL) on split files and write *_ag outputs.
                Also writes out/accgram/goerwitz/_oddballs.json.
    compare-ply
                Compare out/accgram/ply/ outputs against the frozen goerwitz
                oracle (out/accgram/goerwitz/) on a per-verse basis, split into
                clean and oddball buckets.  Prints a parity summary; optionally
                writes a JSON report with --report.
    run-ply
                Run the Python PLY port over new-format input files and write
                out/accgram/ply/*_ag.txt (mirrors `accents -p`).  Use --book to
                restrict to specific books (e.g. --book ob).
    run-ply-tms
                Run the PLY port on the hard-coded troublemaker verses (which the
                C binary emits no output for) and categorize each as clean /
                error-tree / location-only / no-output.  Writes a per-verse report
                and per-book trees to out/accgram/ply-tms/.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py filter-split-wlc
    .venv/Scripts/python.exe py/main_accgram.py research-tms-and-oddballs
    .venv/Scripts/python.exe py/main_accgram.py fresh-run-goerwitz
    .venv/Scripts/python.exe py/main_accgram.py run-goerwitz
    .venv/Scripts/python.exe py/main_accgram.py compare-ply
    .venv/Scripts/python.exe py/main_accgram.py compare-ply --report out/accgram/ply/_parity_report.json
    .venv/Scripts/python.exe py/main_accgram.py run-ply --book ob
    .venv/Scripts/python.exe py/main_accgram.py run-ply-tms
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import filter_split_wlc, split_wlc
from accgram import run_goerwitz
from accgram import research_tao
from accgram import compare_ply
from accgram import run_ply
from accgram import run_ply_tms


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


def _run_research_tao(args: argparse.Namespace) -> None:
    research_tao.run(args)


def _run_compare_ply(args: argparse.Namespace) -> None:
    compare_ply.run(args)


def _run_run_ply(args: argparse.Namespace) -> None:
    run_ply.run(args)


def _run_run_ply_tms(args: argparse.Namespace) -> None:
    run_ply_tms.run(args)


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
            "plus stderr sidecars, _missing_verses.json, and _oddballs.json "
            "(default: out/accgram/goerwitz-stderr)."
        ),
    )
    run_goerwitz.add_args(run_goerwitz_parser, repo_root=_repo_root())
    run_goerwitz_parser.set_defaults(func=_run_goerwitz)

    research_tao_parser = subparsers.add_parser(
        "research-tms-and-oddballs",
        help=(
            "Enrich existing _troublemakers.json entries (plus _oddballs.json) "
            "with matching wlc422-kq-u verse objects and XML-ish UXLC verse nodes, "
            "and write goerwitz.html and goerwitz-obs.html alongside existing "
            "troublemaker pages."
        ),
    )
    research_tao.add_args(research_tao_parser, repo_root=_repo_root())
    research_tao_parser.set_defaults(func=_run_research_tao)

    compare_ply_parser = subparsers.add_parser(
        "compare-ply",
        help=(
            "Compare out/accgram/ply/ outputs against the frozen goerwitz oracle "
            "per-verse, split into clean and oddball buckets."
        ),
    )
    compare_ply.add_args(compare_ply_parser, repo_root=_repo_root())
    compare_ply_parser.set_defaults(func=_run_compare_ply)

    run_ply_parser = subparsers.add_parser(
        "run-ply",
        help=(
            "Run the Python PLY port over new-format input files and write "
            "out/accgram/ply/*_ag.txt (mirrors `accents -p`). Use --book to "
            "restrict (e.g. --book ob)."
        ),
    )
    run_ply.add_args(run_ply_parser, repo_root=_repo_root())
    run_ply_parser.set_defaults(func=_run_run_ply)

    run_ply_tms_parser = subparsers.add_parser(
        "run-ply-tms",
        help=(
            "Run the PLY port on the hard-coded troublemaker verses (which the C "
            "binary emits no output for) and categorize each as clean / error-tree "
            "/ location-only / no-output. Writes out/accgram/ply-tms/."
        ),
    )
    run_ply_tms.add_args(run_ply_tms_parser, repo_root=_repo_root())
    run_ply_tms_parser.set_defaults(func=_run_run_ply_tms)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
