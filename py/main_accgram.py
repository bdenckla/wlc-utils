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
    research-oddballs
                Derive the PLY-based oddball set from the PLY outputs
                (out/accgram/ply) into out/accgram/ply/_oddballs.json, then enrich
                each with its matching wlc422-kq-u verse object and structured
                XML-ish UXLC verse node and write out/accgram/research-oddballs.json
                plus the HTML report gh-pages/accgram/goerwitz.html.

Examples:
    .venv/Scripts/python.exe py/main_accgram.py run-ply
    .venv/Scripts/python.exe py/main_accgram.py run-ply --book ob
    .venv/Scripts/python.exe py/main_accgram.py research-oddballs
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import research_tao
from accgram import run_ply
from accgram import run_ply_poetic
from cmn.utf8_io import force_utf8_io


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _run_research_tao(args: argparse.Namespace) -> None:
    research_tao.run(args)


def _run_run_ply(args: argparse.Namespace) -> None:
    run_ply.run(args)


def _run_run_ply_poetic(args: argparse.Namespace) -> None:
    run_ply_poetic.run(args)


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

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    force_utf8_io()
    main()
