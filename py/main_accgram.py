"""Accent grammar utilities.

Subcommands:
    run-prose
                Run the Python port over the WLC prose corpus
                (out/wlc422-kq-u, genre-filtered) and write
                out/accgram/prose/*_ag.json (mirrors `accents -p`, one JSON record
                per verse).  A verse the grammar cannot parse at all is a fatal
                error.  Use --book to restrict to specific books (e.g. --book ob).
    run-poetic
                Run the POETIC (Three Books) scanner + grammar over the
                poetic corpus (Psalms, Proverbs, poetically-cantillated Job) and
                write out/accgram/poetic/*_ag.json (one JSON record per verse).
                Unparseable verses are recorded as no_parse and tallied, not
                fatal.  Use --book to restrict (ps, pr, jb).
    xcheck-poetic
                Cross-check the poetic scanner's disjunctive segmentation against
                MAM-simple and write out/accgram/poetic/_mam_xcheck.txt (a
                per-book agreement tally plus every divergence grouped by edit
                signature).  The Phase 2 validation surface.
    servi-xcheck
                Cross-check, per disjunctive, the servant (conjunctive) the WLC
                scanner and MAM-simple put immediately before it, and write
                out/accgram/poetic/_servi_xcheck.txt.  The second-witness gate
                for vetting Breuer servant-adjacency rules (it settled deḥi and
                small revia).  Use --target to restrict.
    generate-html
                Generate the accgram HTML reports in one pass:

                  * gh-pages/accgram/poetic.html -- the residual poetic oddballs
                    (missing-silluq ERROR-leaf trees and NO_PARSE anomalies),
                    each enriched with its pointed-Hebrew text, scanned token
                    sequence, rendered tree, and WLC-vs-MAM-simple disjunctive
                    comparison (plus out/accgram/poetic/_oddballs.json).
                    Run run-poetic first.
                  * gh-pages/accgram/goerwitz.html -- the prose oddball
                    set (from out/accgram/prose), enriched with its matching
                    wlc422-kq-u verse object and structured XML-ish UXLC verse
                    node (plus out/accgram/research-oddballs.json).
                  * gh-pages/accgram/almost-errors.html -- the "almost errors"
                    page documenting the editorial charities the checker applies
                    and the non-charity ek20:31 mahapakh!qadma, with live parse
                    trees regenerated from the grammar at build time.
                  * gh-pages/accgram/telg-doc-notes.html -- a deep-dive
                    translation of MAM's documentation notes on the five
                    telisha-gedola + geresh/gershayim words (companion to the
                    telg exhibit on the almost-errors page).
                  * gh-pages/accgram/ps17v14-mam-doc-notes.html and
                    ps17v14-double-tsinnor.html -- the Psalms 17:14 deep dives,
                    generated from their committed htel bodies.

                Each report runs with its default paths.
    grammaticality
                Estimate a PCFG over the committed prose + poetic parse trees
                (one production per tree node) and score each verse's
                log-likelihood -- a continuous companion to the binary
                clean/oddball verdict (issue #11).  Reports the learned grammar,
                the rarest-but-legal verses (per-accent log-likelihood, with the
                least-probable production drilled out), and a validation that the
                flagged oddballs score at the bottom; an n-gram baseline is kept
                as a sanity check.  Writes out/accgram/_grammaticality.txt.  Run
                run-prose + run-poetic first (it reads their committed JSON).
    test-fixes
                For every annotated prose oddball, test whether adopting its
                MAM-simple value clears the ERROR: substitute the MAM value into the
                verse, re-transcode + re-scan + re-parse, and classify CONFIRMED / DENIED /
                CHANGED / UNTESTABLE.  Cross-checks each verdict against the
                prose_ob_notes claim and writes out/accgram/fix-tester/_fix_tester.{txt,json}.
                Run run-prose first.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py run-prose
    .venv/Scripts/python.exe py/main_accgram.py run-prose --book ob
    .venv/Scripts/python.exe py/main_accgram.py generate-html
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import almost_errors
from accgram import fix_tester
from accgram import grammaticality
from accgram import poetic_oddballs
from accgram import ps17v14_double_tsinnor
from accgram import ps17v14_doc_notes
from accgram import research_tao
from accgram import prose_run
from accgram import poetic_run
from accgram import servi_xcheck
from accgram import telg_doc_notes
from accgram import poetic_xcheck
from cmn.utf8_io import force_utf8_io

import repo_paths


def _repo_root() -> Path:
    return repo_paths.repo_root()


def _run_run_prose(args: argparse.Namespace) -> None:
    prose_run.run(args)


def _run_run_poetic(args: argparse.Namespace) -> None:
    poetic_run.run(args)


def _run_xcheck_poetic(args: argparse.Namespace) -> None:
    poetic_xcheck.run(args)


def _run_servi_xcheck(args: argparse.Namespace) -> None:
    servi_xcheck.run(args)


def _run_fix_tester(args: argparse.Namespace) -> None:
    fix_tester.run(args)


def _run_grammaticality(args: argparse.Namespace) -> None:
    grammaticality.run(args)


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

    run_prose_parser = subparsers.add_parser(
        "run-prose",
        help=(
            "Run the Python port over the WLC prose corpus and write "
            "out/accgram/prose/*_ag.json (mirrors `accents -p`). Use --book to "
            "restrict (e.g. --book ob)."
        ),
    )
    prose_run.add_args(run_prose_parser, repo_root=_repo_root())
    run_prose_parser.set_defaults(func=_run_run_prose)

    run_poetic_parser = subparsers.add_parser(
        "run-poetic",
        help=(
            "Run the poetic (Three Books) scanner + grammar over Psalms, "
            "Proverbs, and poetically-cantillated Job and write "
            "out/accgram/poetic/*_ag.json (one JSON record per verse). "
            "Unparseable verses become no_parse records (not fatal). Use "
            "--book to restrict (ps, pr, jb)."
        ),
    )
    poetic_run.add_args(run_poetic_parser, repo_root=_repo_root())
    run_poetic_parser.set_defaults(func=_run_run_poetic)

    xcheck_poetic_parser = subparsers.add_parser(
        "xcheck-poetic",
        help=(
            "Cross-check the poetic scanner's disjunctive segmentation against "
            "MAM-simple and write out/accgram/poetic/_mam_xcheck.txt."
        ),
    )
    poetic_xcheck.add_args(xcheck_poetic_parser, repo_root=_repo_root())
    xcheck_poetic_parser.set_defaults(func=_run_xcheck_poetic)

    servi_xcheck_parser = subparsers.add_parser(
        "servi-xcheck",
        help=(
            "Cross-check, per disjunctive, the servant (conjunctive) the WLC scanner "
            "and MAM-simple put immediately before it -- the second-witness gate for "
            "vetting Breuer servant-adjacency rules. Writes "
            "out/accgram/poetic/_servi_xcheck.txt. Use --target to restrict."
        ),
    )
    servi_xcheck.add_args(servi_xcheck_parser, repo_root=_repo_root())
    servi_xcheck_parser.set_defaults(func=_run_servi_xcheck)

    fix_tester_parser = subparsers.add_parser(
        "test-fixes",
        help=(
            "Test whether adopting each annotated prose oddball's MAM-simple value "
            "clears its ERROR; write out/accgram/fix-tester/_fix_tester.{txt,json}. "
            "Run run-prose first."
        ),
    )
    fix_tester.add_args(fix_tester_parser, repo_root=_repo_root())
    fix_tester_parser.set_defaults(func=_run_fix_tester)

    grammaticality_parser = subparsers.add_parser(
        "grammaticality",
        help=(
            "Estimate a PCFG over the committed prose + poetic parse trees and "
            "score every verse's log-likelihood -- a continuous companion to the "
            "binary clean/oddball verdict (issue #11). Writes "
            "out/accgram/_grammaticality.txt. Run run-prose + run-poetic first."
        ),
    )
    grammaticality.add_args(grammaticality_parser, repo_root=_repo_root())
    grammaticality_parser.set_defaults(func=_run_grammaticality)

    generate_html_parser = subparsers.add_parser(
        "generate-html",
        help=(
            "Generate the accgram HTML reports in one pass: "
            "gh-pages/accgram/poetic.html (run run-poetic first), "
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
