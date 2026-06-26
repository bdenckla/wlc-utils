"""Accent grammar utilities.

Subcommands:
    run-ply-goerwitz
                Run the Python PLY port over the WLC prose corpus
                (out/wlc422-kq-u, genre-filtered) and write
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
    generate-html
                Generate the accgram HTML reports in one pass:

                  * gh-pages/accgram/poetic.html -- the residual poetic oddballs
                    (missing-silluq ERROR-leaf trees and NO_PARSE anomalies),
                    each enriched with its pointed-Hebrew text, scanned token
                    sequence, rendered tree, and WLC-vs-MAM-simple disjunctive
                    comparison (plus out/accgram/ply-poetic/_oddballs.json).
                    Run run-ply-poetic first.
                  * gh-pages/accgram/goerwitz.html -- the PLY-based prose oddball
                    set (from out/accgram/ply), enriched with its matching
                    wlc422-kq-u verse object and structured XML-ish UXLC verse
                    node (plus out/accgram/research-oddballs.json).
                  * gh-pages/accgram/almost-errors.html -- the "almost errors"
                    page documenting the editorial charities the checker applies
                    and the non-charity ek20:31 mahapakh!azla, with live parse
                    trees regenerated from the grammar at build time.
                  * gh-pages/accgram/telg-doc-notes.html -- a deep-dive
                    translation of MAM's documentation notes on the five
                    telisha-gedola + geresh/gershayim words (companion to the
                    telg exhibit on the almost-errors page).
                  * gh-pages/accgram/ps17v14-mam-doc-notes.html and
                    ps17v14-double-tsinnor.html -- the Psalms 17:14 deep dives,
                    generated from their committed htel bodies.

                Each report runs with its default paths.
    test-fixes
                For every annotated prose oddball, test whether adopting its
                MAM-simple value clears the ERROR: substitute the MAM value into the
                verse, re-transcode + re-scan + re-parse, and classify CONFIRMED / DENIED /
                CHANGED / UNTESTABLE.  Cross-checks each verdict against the
                ob_notes claim and writes out/accgram/fix-tester/_fix_tester.{txt,json}.
                Run run-ply-goerwitz first.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py run-ply-goerwitz
    .venv/Scripts/python.exe py/main_accgram.py run-ply-goerwitz --book ob
    .venv/Scripts/python.exe py/main_accgram.py generate-html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import almost_errors
from accgram import fix_tester
from accgram import poetic_oddballs
from accgram import ps17v14_double_tsinnor
from accgram import ps17v14_doc_notes
from accgram import research_tao
from accgram import run_ply
from accgram import run_ply_poetic
from accgram import servi_xcheck
from accgram import telg_doc_notes
from accgram import xcheck_poetic
from cmn.utf8_io import force_utf8_io


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_run_ply(args: argparse.Namespace) -> None:
    run_ply.run(args)


def _run_run_ply_poetic(args: argparse.Namespace) -> None:
    run_ply_poetic.run(args)


def _run_xcheck_poetic(args: argparse.Namespace) -> None:
    xcheck_poetic.run(args)


def _run_servi_xcheck(args: argparse.Namespace) -> None:
    servi_xcheck.run(args)


def _run_fix_tester(args: argparse.Namespace) -> None:
    fix_tester.run(args)


def _run_generate_html(_args: argparse.Namespace) -> None:
    """Run all three HTML generators, each with its own default arguments."""
    repo_root = _repo_root()
    for module in (
        poetic_oddballs,
        research_tao,
        almost_errors,
        telg_doc_notes,
        ps17v14_doc_notes,
        ps17v14_double_tsinnor,
    ):
        sub = argparse.ArgumentParser()
        module.add_args(sub, repo_root=repo_root)
        module.run(sub.parse_args([]))


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
    subparsers.required = True

    run_ply_parser = subparsers.add_parser(
        "run-ply-goerwitz",
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

    fix_tester_parser = subparsers.add_parser(
        "test-fixes",
        help=(
            "Test whether adopting each annotated prose oddball's MAM-simple value "
            "clears its ERROR; write out/accgram/fix-tester/_fix_tester.{txt,json}. "
            "Run run-ply-goerwitz first."
        ),
    )
    fix_tester.add_args(fix_tester_parser, repo_root=_repo_root())
    fix_tester_parser.set_defaults(func=_run_fix_tester)

    generate_html_parser = subparsers.add_parser(
        "generate-html",
        help=(
            "Generate the accgram HTML reports in one pass: "
            "gh-pages/accgram/poetic.html (run run-ply-poetic first), "
            "goerwitz.html, almost-errors.html, and telg-doc-notes.html. Each "
            "runs with its default paths; live trees are regenerated from the "
            "grammar."
        ),
    )
    generate_html_parser.set_defaults(func=_run_generate_html)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    force_utf8_io()
    main()
