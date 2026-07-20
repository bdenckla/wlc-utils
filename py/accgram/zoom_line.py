"""Crop one printed line out of a scan, padded so no accent can be clipped.

Usage:
    .venv/Scripts/python.exe py/accgram/zoom_line.py <export.json> <line> [<line> ...]

``export.json`` is a line editor export (``transcription_editor.py``), committed or freshly
downloaded.  The crop comes from the line's own ``px_source`` band, so it is anchored to the
same coordinates the transcription was read at, and the printed text of that line is echoed
alongside the filename.  Output goes to ``.novc/scans/``.

WHY THE PADDING IS LARGE, AND ASYMMETRIC.  A band is a horizontal INK-FRACTION band, not a
glyph bounding box: a faint mark near its edge falls below the line-finder's ink cutoff and
lies OUTSIDE the band.  Cropping at the band edge therefore clips accents -- and clipping is
not a neutral loss.  On C208 line 1 a crop taken ~20 source pixels above the band cut the
UPPER DOT OFF A ZAQEF QATAN, leaving a single dot that reads as a revia: the crop manufactured
a wrong reading of the very mark it was made to adjudicate.  Accents sit above the letters, so
the headroom is the point; the bottom needs only enough for descenders and lower points.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent)
)  # run directly as a script

sys.stdout.reconfigure(encoding="utf-8")

PAD_ABOVE = 1.0  # band heights above the line
PAD_BELOW = 0.5  # and below
PAD_SIDES = 0.012  # page widths beyond the transcription crop, left and right
WIDTH = 2400  # wide, because the point is to magnify one line


def main() -> None:
    export = Path(sys.argv[1])
    wanted = {int(n) for n in sys.argv[2:]}
    record = json.loads(export.read_text(encoding="utf-8"))
    # A two-page Decalogue keeps one export per page under "pages"; a one-page one is its own
    # only page.  Line numbers restart per page, so a wanted number may match in both.
    for page in record.get("pages", [record]):
        _zoom_page(page, wanted)


def _zoom_page(page: dict, wanted: set[int]) -> None:
    book = page["source"]["book"]
    name = page["source"]["file"].removesuffix(".jpg")
    page_height = page["source"]["size"][1]
    # Widen past the transcription crop rather than inheriting it exactly.  That crop is a
    # guess at where the column ends, and on C247 it was set ~0.006 of the page width inside
    # the true right edge -- clipping the first letter of every line, which in RTL is where
    # each line STARTS.  A zoom exists to adjudicate a mark, so it must not be bounded by the
    # same guess that may be at fault; pulling in a sliver of the neighbouring column is a
    # trivial cost next to cropping away the thing being read.
    # ``crop`` is null when the page was rendered whole; the full width then IS the crop.
    left, _, right, _ = page["render"]["crop"] or (0.0, 0.0, 1.0, 1.0)
    left = max(0.0, left - PAD_SIDES)
    right = min(1.0, right + PAD_SIDES)
    repo = Path(__file__).resolve().parent.parent.parent
    for line in page["lines"]:
        if wanted and line["n"] not in wanted:
            continue
        top, bottom = line["px_source"]
        height = bottom - top
        lo = max(0, top - PAD_ABOVE * height) / page_height
        hi = min(page_height, bottom + PAD_BELOW * height) / page_height
        stem = f"zoom-{page['stem'].split('_')[-1]}-line{line['n']:02d}"
        # Output is captured so scan_page's own line does not repeat under every zoom, which
        # means a failure's stderr has to be surfaced here or it is silently swallowed.
        proc = subprocess.run(
            [
                sys.executable,
                str(repo / "py" / "accgram" / "scan_page.py"),
                book,
                name,
                "--crop",
                f"{left}",
                f"{lo:.4f}",
                f"{right}",
                f"{hi:.4f}",
                "--name",
                stem,
                "--width",
                str(WIDTH),
            ],
            capture_output=True,
            text=True,
        )
        if proc.returncode:
            sys.exit(f"scan_page failed on line {line['n']}:\n{proc.stderr}")
        print(f"line {line['n']:2d}  source rows {top}-{bottom}  -> {stem}.png")
        print(f"          {line['text']}")


if __name__ == "__main__":
    main()
