"""Accent grammar utilities.

Subcommands:
    run-ply
                Run the Python PLY port over the WLC prose corpus
                (wlc-utils-io/in/wlc422/wlc422_ps.txt, genre-filtered) and write
                out/accgram/ply/*_ag.txt (mirrors `accents -p`).  A verse the
                grammar cannot parse at all is a fatal error.  Use --book to
                restrict to specific books (e.g. --book ob).
    run-ply-poetic
                Run the POETIC (Three Books) PLY scanner + grammar over the
                poetic corpus (Psalms, Proverbs, poetically-cantillated Job) and
                write out/accgram/ply-poetic/*_ag.txt.  Unparseable verses are
                emitted as NO_PARSE lines and tallied, not fatal.  Use --book to
                restrict (ps, pr, jb).
    xcheck-poetic
                Cross-check the poetic scanner's disjunctive segmentation against
                MAM-simple and write out/accgram/ply-poetic/_mam_xcheck.txt (a
                per-book agreement tally plus every divergence grouped by edit
                signature).  The Phase 2 validation surface.
    servi-xcheck
                Cross-check, per disjunctive, the servant (conjunctive) the WLC
                scanner and MAM-simple put immediately before it, and write
                out/accgram/ply-poetic/_servi_xcheck.txt.  The second-witness gate
                for vetting Breuer servant-adjacency rules (it settled deḥi and
                small revia).  Use --target to restrict.
    run-ply-poetic-oddballs
                Collect the residual poetic oddballs (the missing-silluq
                ERROR-leaf trees and the NO_PARSE anomalies) from the poetic
                corpus, enrich each with its M-C body, scanned token sequence,
                rendered tree, and WLC-vs-MAM-simple disjunctive comparison, and
                write out/accgram/ply-poetic/_oddballs.json plus the HTML report
                gh-pages/accgram/poetic.html.  The optional Phase 4 analogue of
                research-oddballs.  Run run-ply-poetic first.
    research-oddballs
                Derive the PLY-based oddball set from the PLY outputs
                (out/accgram/ply) into out/accgram/ply/_oddballs.json, then enrich
                each with its matching wlc422-kq-u verse object and structured
                XML-ish UXLC verse node and write out/accgram/research-oddballs.json
                plus the HTML report gh-pages/accgram/goerwitz.html.
    test-fixes
                For every annotated prose oddball, test whether adopting its
                MAM-simple value clears the ERROR: splice the MAM value into the
                M-C body, re-scan + re-parse, and classify CONFIRMED / DENIED /
                CHANGED / UNTESTABLE.  Cross-checks each verdict against the
                ob_notes claim and writes out/accgram/fix-tester/_fix_tester.{txt,json}.
                Run run-ply first.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py run-ply
    .venv/Scripts/python.exe py/main_accgram.py run-ply --book ob
    .venv/Scripts/python.exe py/main_accgram.py research-oddballs
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import fix_tester
from accgram import poetic_oddballs
from accgram import research_tao
from accgram import run_ply
from accgram import run_ply_poetic
from accgram import servi_xcheck
from accgram import xcheck_poetic
from cmn.utf8_io import force_utf8_io


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_research_tao(args: argparse.Namespace) -> None:
    research_tao.run(args)


def _run_run_ply(args: argparse.Namespace) -> None:
    run_ply.run(args)


def _run_run_ply_poetic(args: argparse.Namespace) -> None:
    run_ply_poetic.run(args)


def _run_xcheck_poetic(args: argparse.Namespace) -> None:
    xcheck_poetic.run(args)


def _run_servi_xcheck(args: argparse.Namespace) -> None:
    servi_xcheck.run(args)


def _run_poetic_oddballs(args: argparse.Namespace) -> None:
    poetic_oddballs.run(args)


def _run_fix_tester(args: argparse.Namespace) -> None:
    fix_tester.run(args)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
    subparsers.required = True

    run_ply_parser = subparsers.add_parser(
        "run-ply",
        help=(
            "Run the Python PLY port over the WLC prose corpus and write "
            "out/accgram/ply/*_ag.txt (mirrors `accents -p`). Use --book to "
            "restrict (e.g. --book ob)."
        ),
    )
    run_ply.add_args(run_ply_parser, repo_root=_repo_root())
    run_ply_parser.set_defaults(func=_run_run_ply)

    run_ply_poetic_parser = subparsers.add_parser(
        "run-ply-poetic",
        help=(
            "Run the poetic (Three Books) PLY scanner + grammar over Psalms, "
            "Proverbs, and poetically-cantillated Job and write "
            "out/accgram/ply-poetic/*_ag.txt. Unparseable verses become NO_PARSE "
            "lines (not fatal). Use --book to restrict (ps, pr, jb)."
        ),
    )
    run_ply_poetic.add_args(run_ply_poetic_parser, repo_root=_repo_root())
    run_ply_poetic_parser.set_defaults(func=_run_run_ply_poetic)

    xcheck_poetic_parser = subparsers.add_parser(
        "xcheck-poetic",
        help=(
            "Cross-check the poetic scanner's disjunctive segmentation against "
            "MAM-simple and write out/accgram/ply-poetic/_mam_xcheck.txt."
        ),
    )
    xcheck_poetic.add_args(xcheck_poetic_parser, repo_root=_repo_root())
    xcheck_poetic_parser.set_defaults(func=_run_xcheck_poetic)

    servi_xcheck_parser = subparsers.add_parser(
        "servi-xcheck",
        help=(
            "Cross-check, per disjunctive, the servant (conjunctive) the WLC scanner "
            "and MAM-simple put immediately before it -- the second-witness gate for "
            "vetting Breuer servant-adjacency rules. Writes "
            "out/accgram/ply-poetic/_servi_xcheck.txt. Use --target to restrict."
        ),
    )
    servi_xcheck.add_args(servi_xcheck_parser, repo_root=_repo_root())
    servi_xcheck_parser.set_defaults(func=_run_servi_xcheck)

    poetic_oddballs_parser = subparsers.add_parser(
        "run-ply-poetic-oddballs",
        help=(
            "Collect the residual poetic oddballs (missing-silluq ERROR-leaf trees "
            "and NO_PARSE anomalies), enrich each with its M-C body, token sequence, "
            "tree, and WLC-vs-MAM disjunctive comparison, and write "
            "out/accgram/ply-poetic/_oddballs.json + gh-pages/accgram/poetic.html."
        ),
    )
    poetic_oddballs.add_args(poetic_oddballs_parser, repo_root=_repo_root())
    poetic_oddballs_parser.set_defaults(func=_run_poetic_oddballs)

    research_tao_parser = subparsers.add_parser(
        "research-oddballs",
        help=(
            "Enrich the PLY-derived _oddballs.json entries with matching "
            "wlc422-kq-u verse objects and XML-ish UXLC verse nodes, and write "
            "the filterable goerwitz.html report."
        ),
    )
    research_tao.add_args(research_tao_parser, repo_root=_repo_root())
    research_tao_parser.set_defaults(func=_run_research_tao)

    fix_tester_parser = subparsers.add_parser(
        "test-fixes",
        help=(
            "Test whether adopting each annotated prose oddball's MAM-simple value "
            "clears its ERROR; write out/accgram/fix-tester/_fix_tester.{txt,json}. "
            "Run run-ply first."
        ),
    )
    fix_tester.add_args(fix_tester_parser, repo_root=_repo_root())
    fix_tester_parser.set_defaults(func=_run_fix_tester)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    force_utf8_io()
    main()
