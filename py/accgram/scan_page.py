"""Bring up a page of a book scan, downscaled to something readable.

Usage:
    .venv/Scripts/python.exe py/accgram/scan_page.py <book-dir> <name> [<name> ...] \
        [--width N] [--crop L T R B] [--name STEM]

<name> is a scan filename with or without the .jpg (e.g. C085, A2-E-113, V-038).  Output is
written to .novc/scans/ -- gitignored, since a rendering is disposable and can be regenerated
from the scan, but stable across sessions unlike a temp directory.

The scans themselves are a personal archive outside the repo (see WLC_SCANS_DIR).  Filename
conventions differ per book: the Simanim Tiqqun's main body is an identity map from printed
page to C<page:03d>.jpg, while the Koren Classic Tanakh numbers the Torah continuously as
A<n>-<letter>-<page:03d>.jpg and gives its appendix a separate V-<page:03d>.jpg sequence.

This only WRITES the PNG.  Two ways to view one, both fine: open its file:// URL in Claude's
Browser pane, or PowerShell `Start-Process <path>` for the desktop viewer.  Use Start-Process
rather than Invoke-Item -- Invoke-Item launched Photos with no window at all.  Either way the
desktop window will not come to the foreground (Windows denies SetForegroundWindow to a
background process), so it waits in the taskbar.

The raw scans are ~5100x7100 and 4-13 MB, too big to open comfortably or to hand to the Read
tool, which is the whole reason this exists.

--crop takes four fractions of the page in 0..1, left top right bottom, applied before the
resize -- so cropping to a quarter of the page and keeping --width the same doubles the
effective resolution.  That is what makes a conjunctive legible: a whole Tiqqun page at 1400px
shows the disjunctive skeleton and the maqafs, but merkha vs. meteg needs the zoom.
Right-hand (accented) column of a SimTiq two-column page is roughly --crop 0.5 0 1 1.

--name sets the output stem, so successive crops of one page do not overwrite each other
(a crop otherwise lands on <name>-crop.png regardless of which region it is).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent)
)  # run directly as a script

import repo_paths  # noqa: E402
from PIL import Image  # noqa: E402

# The scans are a personal archive outside any repo, so this is the one machine-specific path
# here; WLC_SCANS_DIR overrides it, in the style of repo_paths' sibling-repo overrides.
SCANS = Path(
    os.environ.get("WLC_SCANS_DIR", Path.home() / "OneDrive/Documents/ScansOfBooks")
)
# Renderings are disposable and can be large, so they go to gitignored scratch, not out/.
OUT = repo_paths.repo_root() / ".novc" / "scans"


def _take(args: list[str], flag: str, count: int) -> list[str] | None:
    """Pull `count` values following `flag` out of `args`, or None if absent."""
    if flag not in args:
        return None
    i = args.index(flag)
    values = args[i + 1 : i + 1 + count]
    del args[i : i + 1 + count]
    return values


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    width_arg = _take(args, "--width", 1)
    width = int(width_arg[0]) if width_arg else 1400
    crop = _take(args, "--crop", 4)
    name_arg = _take(args, "--name", 1)
    book, names = args[0], args[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        stem = name.removesuffix(".jpg")
        src = SCANS / book / f"{stem}.jpg"
        img = Image.open(src)
        if crop:
            left, top, right, bottom = (float(v) for v in crop)
            img = img.crop(
                (
                    round(left * img.width),
                    round(top * img.height),
                    round(right * img.width),
                    round(bottom * img.height),
                )
            )
            stem = f"{stem}-crop"
        if name_arg:
            stem = name_arg[0]
        scale = width / img.width
        small = img.resize((width, round(img.height * scale)), Image.LANCZOS)
        dst = OUT / f"{stem}.png"
        small.save(dst)
        print(f"{src.name} -> {dst}  ({small.width}x{small.height})")


if __name__ == "__main__":
    main()
