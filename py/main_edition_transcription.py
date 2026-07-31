"""Printed-edition transcription workflow.

The interactive, machine-local half of the printed-Decalogue work: it reads a personal scan
archive outside the repo (see WLC_SCANS_DIR) and writes disposable renderings to the
gitignored .novc/scans/.  Kept apart from main_accgram.py deliberately -- that entry point is
corpus runs and page generation, which need no scans and produce tracked output.

Subcommands:
    scan-page
                Render one page (or several) of a book scan, downscaled to something
                readable, to .novc/scans/<stem>.png.  --crop takes four fractions of
                the page in 0..1, left top right bottom, applied before the resize, so
                a quarter-page crop at the same --width doubles the effective
                resolution -- which is what makes merkha vs. meteg legible.  --name
                sets the output stem, so successive crops of one page do not overwrite
                each other, and therefore refuses more than one page.
    editor
                Build a per-line transcription editor over one page, to
                .novc/scans/<stem>-editor.html: the page image with a text field that
                follows the line being transcribed down it, so the eye never leaves
                that line.  --crop's L and R bound the text column, while its T and B
                name the LINES TO TRANSCRIBE -- band detection runs over a region grown
                about a line past them, so a boundary line is never clipped and its
                neighbours come through dimmed as context.  --debug also writes
                <stem>-lines.png with the detected bands drawn on the page.
    zoom-line
                Crop one printed line (or several, or with no line numbers all of
                them) out of the scan a line editor export was read from, padded so
                no accent can be clipped, and echo that line's transcribed text.  The
                band comes from the export's own px_source coordinates, so the zoom is
                anchored to what was transcribed.

    (check and build join them here as the rest of the toolchain converts.)

The output is only ever written.  To put a rendering in front of the reader, hand over a
``file:///`` link to it and open nothing -- no Start-Process, no browser pane.

Examples:
    .venv/Scripts/python.exe py/main_edition_transcription.py scan-page \
        "Feldheim Simanim Tiqqun" C246 --width 1100
    .venv/Scripts/python.exe py/main_edition_transcription.py scan-page \
        "Feldheim Simanim Tiqqun" C246 --crop 0.5 0 1 1 --name C246-right
    .venv/Scripts/python.exe py/main_edition_transcription.py editor \
        "Feldheim Simanim Tiqqun" C246 --crop 0.5 0.30 1 0.45 --name C246-v --debug
    .venv/Scripts/python.exe py/main_edition_transcription.py zoom-line \
        in/accgram/edition_transcriptions/simtiq_ex_taxton.json 12 13
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import scan_page
from accgram import transcription_editor
from accgram import zoom_line
from cmn.utf8_io import force_utf8_io

import repo_paths


def _repo_root() -> Path:
    return repo_paths.repo_root()


def _run_scan_page(args: argparse.Namespace) -> None:
    scan_page.run(args)


def _run_editor(args: argparse.Namespace) -> None:
    transcription_editor.run(args)


def _run_zoom_line(args: argparse.Namespace) -> None:
    zoom_line.run(args)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
    subparsers.required = True

    scan_page_parser = subparsers.add_parser(
        "scan-page",
        help=(
            "Render a page of a book scan, downscaled, to .novc/scans/<stem>.png. "
            "--crop L T R B takes fractions of the page in 0..1 and is applied before "
            "the resize; --name sets the output stem and takes one page only."
        ),
    )
    scan_page.add_args(scan_page_parser, repo_root=_repo_root())
    scan_page_parser.set_defaults(func=_run_scan_page)

    editor_parser = subparsers.add_parser(
        "editor",
        help=(
            "Build a per-line transcription editor over one page, to "
            ".novc/scans/<stem>-editor.html. --crop L T R B bounds the text column "
            "left and right and names the lines to transcribe top and bottom; --debug "
            "also writes <stem>-lines.png with the detected bands drawn on."
        ),
    )
    transcription_editor.add_args(editor_parser, repo_root=_repo_root())
    editor_parser.set_defaults(func=_run_editor)

    zoom_line_parser = subparsers.add_parser(
        "zoom-line",
        help=(
            "Crop one printed line out of the scan an export was read from, padded so "
            "no accent can be clipped, and echo its transcribed text. With no line "
            "numbers, every line of the export."
        ),
    )
    zoom_line.add_args(zoom_line_parser, repo_root=_repo_root())
    zoom_line_parser.set_defaults(func=_run_zoom_line)

    args = parser.parse_args()
    # `or 0` because a subcommand that returns None succeeded; the non-None case is a gate
    # such as transcription_build --check, whose non-zero return has to reach the shell.
    raise SystemExit(args.func(args) or 0)


if __name__ == "__main__":
    force_utf8_io()
    main()
