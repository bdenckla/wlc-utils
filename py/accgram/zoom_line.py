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
    left, _, right, _ = page["render"]["crop"]
    repo = Path(__file__).resolve().parent.parent.parent
    for line in page["lines"]:
        if wanted and line["n"] not in wanted:
            continue
        top, bottom = line["px_source"]
        height = bottom - top
        lo = max(0, top - PAD_ABOVE * height) / page_height
        hi = min(page_height, bottom + PAD_BELOW * height) / page_height
        stem = f"zoom-{page['stem'].split('_')[-1]}-line{line['n']:02d}"
        subprocess.run(
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
            check=True,
            capture_output=True,
        )
        print(f"line {line['n']:2d}  source rows {top}-{bottom}  -> {stem}.png")
        print(f"          {line['text']}")


if __name__ == "__main__":
    main()
