"""Build a per-line transcription editor for a page of a book scan.

Usage:
    .venv/Scripts/python.exe py/accgram/transcription_editor.py <book-dir> <name> \
        [--crop L T R B] [--width N] [--name STEM] [--debug]

Writes .novc/scans/<stem>-editor.html: the page image with a text field that sits directly
under whichever line is being transcribed, on top of the image.  The field follows the
current line down the page, so the eye never leaves the line it is reading -- the ergonomic
problem with transcribing a whole page in one go.  It covers the NEXT line while it is open,
which costs nothing, since that line is not the one being read.  --debug additionally writes
<stem>-lines.png with the detected line bands drawn on the page, to check the segmentation
before typing into it.

Line finding is a horizontal projection profile, not OCR: the fraction of each pixel row that
is ink, smoothed; rows above a threshold are text and the troughs between them are the gaps.
Nothing here reads a letter or an accent -- it only finds where the lines are.  Binarizing and
then resizing the column to one pixel wide with a BOX filter gives that per-row ink fraction
directly, which is why this needs no numpy.

The projection is taken over the CROPPED region, so crop to a single text column first: a
two-column page profiled whole has no clean troughs, since the columns' lines do not align.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent)
)  # run directly as a script

import repo_paths  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

# The scans are a personal archive outside any repo, so this is the one machine-specific path
# here; WLC_SCANS_DIR overrides it, in the style of repo_paths' sibling-repo overrides.
SCANS = Path(
    os.environ.get("WLC_SCANS_DIR", Path.home() / "OneDrive/Documents/ScansOfBooks")
)
# The editor and its rendering are disposable -- rebuilt from the scan whenever the crop
# changes -- so they go to gitignored scratch.  What is meant to be kept is the JSON the Save
# button exports, which is committed beside the transcription it records.
OUT = repo_paths.repo_root() / ".novc" / "scans"

# A row is text when its ink rises this far from the page's own baseline toward a full line's
# density.  Relative, not absolute, because a crop that clips the page's vertical border rule
# carries a constant ink offset in EVERY row, gaps included, which no fixed floor separates.
# Kept small because a closing line of two or three words covers very little of the column
# and anything scaled to a full line's density silently loses it.
INK_CUTOFF = 0.08
INK_LEVEL = 128  # gray below this is ink
SMOOTH_RADIUS = 3  # rows; blurs out the gap between a letter body and its accents
MIN_LINE_FRACTION = (
    0.25  # of median band height -- below this a band is speck, not a line
)
MIN_GAP_FRACTION = (
    0.35  # of median band height -- shorter gaps are within-line, so merge
)
MAX_LINE_UNITS = (
    1.6  # a band taller than this many single lines is holding more than one
)
# Below this fraction of a single line, a band is a fragment or a decorative rule, not a line.
# Safe at half a line because a SHORT line is short horizontally, not vertically: it still
# stands a full line tall, so this cannot swallow one.
SLIVER_FRACTION = 0.5


def _take(args: list[str], flag: str, count: int) -> list[str] | None:
    if flag not in args:
        return None
    i = args.index(flag)
    values = args[i + 1 : i + 1 + count]
    del args[i : i + 1 + count]
    return values


def row_profile(img: Image.Image) -> list[float]:
    """Fraction of each pixel row that is ink, 0.0 to 1.0.

    Binarize first, then average: averaging raw gray instead would weight a row by how dark
    it is rather than how much of it is covered, and short lines vanish.
    """
    ink = img.convert("L").point(lambda v: 255 if v < INK_LEVEL else 0)
    column = ink.resize((1, img.height), Image.BOX)
    return [v / 255 for v in column.getdata()]


def smooth(values: list[float], radius: int) -> list[float]:
    out = []
    for i in range(len(values)):
        lo, hi = max(0, i - radius), min(len(values), i + radius + 1)
        out.append(sum(values[lo:hi]) / (hi - lo))
    return out


def find_bands(profile: list[float]) -> list[tuple[int, int]]:
    """Contiguous row ranges that hold text, as (top, bottom) pairs."""
    ordered = sorted(profile)
    baseline = ordered[
        int(0.05 * (len(ordered) - 1))
    ]  # a gap row, border rule included
    busy = ordered[int(0.90 * (len(ordered) - 1))]  # a full line of text
    cutoff = baseline + INK_CUTOFF * (busy - baseline)

    bands, start = [], None
    for i, value in enumerate(profile):
        if value >= cutoff and start is None:
            start = i
        elif value < cutoff and start is not None:
            bands.append((start, i))
            start = None
    if start is not None:
        bands.append((start, len(profile)))
    if not bands:
        return []

    # Two clean-ups, in this order: close the gaps inside a line first (a row of accents can
    # sit clear of its letters), then drop what is still too short to be a line.
    heights = sorted(b - a for a, b in bands)
    median = heights[len(heights) // 2]
    merged = [list(bands[0])]
    for top, bottom in bands[1:]:
        if top - merged[-1][1] < MIN_GAP_FRACTION * median:
            merged[-1][1] = bottom
        else:
            merged.append([top, bottom])
    heights = sorted(b - a for a, b in merged)
    median = heights[len(heights) // 2]
    kept = [(a, b) for a, b in merged if (b - a) >= MIN_LINE_FRACTION * median]
    return _split_tall(kept, profile)


def _split_tall(
    bands: list[tuple[int, int]], profile: list[float]
) -> list[tuple[int, int]]:
    """Cut apart bands too tall to be one printed line.

    The cutoff that is low enough to catch a two-word closing line is also low enough to stop
    separating neighbours whose gap is partly filled by accents above and below, so some bands
    arrive holding two or three lines.  Rather than trade one failure against the other by
    tuning, use the regularity of printed text: take the single-line height from the shorter
    quartile of bands (a short line is narrow, not shallow, so it still measures one line
    tall), then repeatedly cut any over-tall band at its emptiest interior row.
    """
    if not bands:
        return bands
    heights = sorted(b - a for a, b in bands)
    unit = heights[max(0, len(heights) // 4)]
    out, todo = [], list(bands)
    while todo:
        top, bottom = todo.pop()
        if bottom - top <= MAX_LINE_UNITS * unit:
            out.append((top, bottom))
            continue
        # Search only the middle, so the cut lands in a gap rather than shaving off an edge.
        margin = max(1, round(0.3 * unit))
        lo, hi = top + margin, bottom - margin
        if hi <= lo:
            out.append((top, bottom))
            continue
        cut = min(range(lo, hi), key=lambda i: profile[i])
        todo.extend([(top, cut), (cut, bottom)])
    return _absorb_slivers(sorted(out), unit)


def _absorb_slivers(bands: list[tuple[int, int]], unit: int) -> list[tuple[int, int]]:
    """Fold anything too short to be a line into the neighbour it sits closest to.

    Splitting can shave a fragment off a band's edge, and the page's decorative rules survive
    as slivers of their own.  Absorb rather than discard: a dropped band is a line with no
    field to type into, which is a silent hole in the transcription, while an absorbed one
    only makes a neighbouring band slightly tall.
    """
    if not bands:
        return bands
    out = [list(bands[0])]
    for top, bottom in bands[1:]:
        if (bottom - top) < SLIVER_FRACTION * unit:
            out[-1][1] = bottom  # nearest neighbour above; gaps here are sub-pixel
        elif (out[-1][1] - out[-1][0]) < SLIVER_FRACTION * unit:
            out[-1][1] = bottom
        else:
            out.append([top, bottom])
    return [(a, b) for a, b in out]


def source_fingerprint(src: Path) -> dict:
    """Identify the exact scan file a transcription was read from.

    The scans are not in the repo, so a committed transcription otherwise names a page with
    no way to tell whether the file behind that name is still the same one.  The digest makes
    that checkable.
    """
    digest = hashlib.sha256(src.read_bytes()).hexdigest()
    with Image.open(src) as img:
        size = list(img.size)
    return {"file": src.name, "book": src.parent.name, "sha256": digest, "size": size}


def build_html(
    stem: str,
    image_name: str,
    bands: list[tuple[int, int]],
    height: int,
    meta: dict,
    origin: int,
    scale: float,
) -> str:
    """Positions are percentages of image height, so any display width works.

    Each band is also recorded twice in pixels: ``px`` in the rendered PNG, and ``px_source``
    in the original scan.  The rendered PNG is disposable -- regenerate at another --width and
    its coordinates mean something different -- so an audit trail that cited only those would
    decay.  ``px_source`` stays valid for as long as the scan does, which is what the sha256
    pins.
    """
    rows = [
        {
            "n": i + 1,
            "top": 100.0 * top / height,
            "height": 100.0 * (bottom - top) / height,
            "px": [top, bottom],
            "px_source": [round(origin + top * scale), round(origin + bottom * scale)],
        }
        for i, (top, bottom) in enumerate(bands)
    ]
    return (
        _HTML.replace("__STEM__", stem)
        .replace("__IMAGE__", image_name)
        .replace("__ROWS__", json.dumps(rows))
        .replace("__META__", json.dumps(meta))
    )


_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>__STEM__ - line transcription</title>
<style>
  body { margin: 0; font: 14px/1.4 system-ui, sans-serif; background: #1b1b1b; color: #eee; }
  header { padding: 10px 16px; background: #222; position: sticky; top: 0; z-index: 20;
           display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  button { font: inherit; padding: 5px 12px; border-radius: 5px; border: 1px solid #555;
           background: #333; color: #eee; cursor: pointer; }
  button:hover { background: #444; }
  #status { color: #9a9; }
  #hint { color: #777; font-size: 13px; }
  #wrap { padding: 16px; }
  #sheet { position: relative; display: inline-block; }
  #sheet img { display: block; width: 100%; }

  /* One click target per printed line, lying over the image. */
  .hit { position: absolute; left: 0; width: 100%; cursor: text; }
  .hit.on { background: rgba(110, 200, 255, 0.18);
            box-shadow: inset 0 0 0 1px rgba(110, 200, 255, 0.7); }
  /* A line already typed keeps a marker, since its text is hidden once focus moves on. */
  .hit.done { border-left: 6px solid rgba(80, 200, 110, 0.85); }

  /* The entry field sits UNDER its line rather than in a side gutter: a gutter is a
     horizontal eye-jump on every single line, which is the thing this is meant to avoid.
     Only the active one is shown, so the line it covers is never a line being read. */
  .entry { position: absolute; left: 0; width: 100%; display: none; z-index: 10;
           align-items: center; gap: 8px; }
  .entry.on { display: flex; }
  .entry .num { flex: 0 0 auto; font: 15px ui-monospace, Consolas, monospace; color: #9cf;
                background: #0b1a22; padding: 4px 8px; border-radius: 4px 0 0 4px;
                border: 1px solid #6cf; border-right: none; }
  /* RTL to match the page: the first token lands under the line's first word, at the right,
     and the caret travels leftward with the reading. */
  .entry input { flex: 1 1 auto; font: 26px/1.25 ui-monospace, Consolas, monospace;
                 background: #0b1a22; color: #eaf6ff; border: 1px solid #6cf;
                 border-radius: 0 4px 4px 0; padding: 4px 10px; text-align: right; }
  .entry input:focus { outline: none; box-shadow: 0 0 0 2px rgba(110, 200, 255, 0.35); }

  #out { width: 100%; height: 160px; font: 13px ui-monospace, Consolas, monospace;
         background: #111; color: #ddd; border: 1px solid #444; }
  #outwrap { padding: 0 16px 24px; }
</style>
</head>
<body>
<header>
  <strong>__STEM__</strong>
  <button id="copy">Copy transcription</button>
  <button id="save">Save JSON</button>
  <button id="clear">Clear</button>
  <span id="status"></span>
  <span id="hint">click a line to start &middot; Enter = next &middot; Shift+Enter = previous
    &middot; Esc = close</span>
</header>
<div id="wrap"><div id="sheet"><img src="__IMAGE__" alt=""></div></div>
<div id="outwrap"><textarea id="out" readonly
  placeholder="Copy transcription puts the text here"></textarea></div>
<script>
const ROWS = __ROWS__;
const META = __META__;
const KEY = "linetx:__STEM__";
const sheet = document.getElementById("sheet");
const saved = JSON.parse(localStorage.getItem(KEY) || "{}");
const hits = [], entries = [], inputs = [];

ROWS.forEach((r, idx) => {
  const hit = document.createElement("div");
  hit.className = "hit";
  hit.style.top = r.top + "%";
  hit.style.height = r.height + "%";
  hit.addEventListener("mousedown", e => { e.preventDefault(); focusLine(idx); });
  sheet.appendChild(hit);
  hits.push(hit);

  const entry = document.createElement("div");
  entry.className = "entry";
  // Sit just below the line.  The last line has nothing beneath it on the page, so its field
  // goes above instead rather than hanging off the bottom edge.
  const below = r.top + r.height;
  const next = ROWS[idx + 1];
  entry.style.top = (next ? next.top : Math.max(0, r.top - r.height)) + "%";
  const num = document.createElement("span");
  num.className = "num";
  num.textContent = r.n;
  const input = document.createElement("input");
  input.type = "text";
  input.dir = "rtl";
  input.spellcheck = false;
  input.autocapitalize = "off";
  input.value = saved[r.n] || "";
  input.addEventListener("input", save);
  input.addEventListener("keydown", e => {
    if (e.key === "Escape") { input.blur(); close(); return; }
    if (e.key !== "Enter") return;
    e.preventDefault();
    focusLine(idx + (e.shiftKey ? -1 : 1));
  });
  entry.append(num, input);
  sheet.appendChild(entry);
  entries.push(entry);
  inputs.push(input);
});

function close() {
  hits.forEach(h => h.classList.remove("on"));
  entries.forEach(e => e.classList.remove("on"));
}

function focusLine(idx) {
  if (idx < 0 || idx >= ROWS.length) return;
  close();
  hits[idx].classList.add("on");
  entries[idx].classList.add("on");
  const input = inputs[idx];
  input.focus();
  input.setSelectionRange(input.value.length, input.value.length);
  hits[idx].scrollIntoView({ block: "center", behavior: "smooth" });
  save();
}

function save() {
  const data = {};
  inputs.forEach((inp, i) => {
    const text = inp.value.trim();
    if (text) data[ROWS[i].n] = text;
    hits[i].classList.toggle("done", !!text);
  });
  localStorage.setItem(KEY, JSON.stringify(data));
  document.getElementById("status").textContent =
    Object.keys(data).length + " of " + ROWS.length + " lines - saved";
}

document.getElementById("copy").addEventListener("click", () => {
  // One printed line per output line: keeps the transcription checkable against the page.
  const text = inputs.map(i => i.value.trim()).filter(Boolean).join("\\n");
  const out = document.getElementById("out");
  out.value = text;
  navigator.clipboard.writeText(text).then(
    () => document.getElementById("status").textContent = "copied to clipboard",
    () => { out.select(); document.getElementById("status").textContent = "select and copy"; }
  );
});

document.getElementById("save").addEventListener("click", () => {
  // The audit trail: what was typed, on which line, at which coordinates of which scan.
  // Only lines with text are written -- a blank field means not yet transcribed, which is
  // not the same claim as a line that carries no accent.
  const record = {
    stem: META.stem,
    source: META.source,
    render: META.render,
    transcribed_utc: new Date().toISOString(),
    line_count: ROWS.length,
    lines: ROWS.map((r, i) => ({
             n: r.n, px: r.px, px_source: r.px_source, text: inputs[i].value.trim()
           })).filter(l => l.text)
  };
  const blob = new Blob([JSON.stringify(record, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = META.stem + "-transcription.json";
  a.click();
  URL.revokeObjectURL(a.href);
  document.getElementById("status").textContent =
    "saved " + a.download + " to your downloads";
});

document.getElementById("clear").addEventListener("click", () => {
  if (!confirm("Clear all typed lines?")) return;
  localStorage.removeItem(KEY);
  inputs.forEach(i => { i.value = ""; });
  close();
  save();
});

save();
</script>
</body>
</html>
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    debug = "--debug" in args
    args = [a for a in args if a != "--debug"]
    width_arg = _take(args, "--width", 1)
    width = int(width_arg[0]) if width_arg else 1200
    crop = _take(args, "--crop", 4)
    name_arg = _take(args, "--name", 1)
    book, name = args[0], args[1]

    stem = name_arg[0] if name_arg else name.removesuffix(".jpg")
    src = SCANS / book / f"{name.removesuffix('.jpg')}.jpg"
    img = Image.open(src)
    source_height = img.height
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
    # Remember where the crop started and how far it was scaled, so line coordinates can be
    # reported against the original scan as well as against the rendering.
    crop_top_px = round(float(crop[1]) * source_height) if crop else 0
    cropped_height = img.height
    img = img.resize((width, round(img.height * width / img.width)), Image.LANCZOS)
    source_scale = cropped_height / img.height

    bands = find_bands(smooth(row_profile(img), SMOOTH_RADIUS))
    OUT.mkdir(parents=True, exist_ok=True)
    image_name = f"{stem}.png"
    img.save(OUT / image_name)

    meta = {
        "stem": stem,
        "source": source_fingerprint(src),
        # Enough to redo the exact rendering the line coordinates refer to.
        "render": {
            "crop": [float(v) for v in crop] if crop else None,
            "width": width,
            "size": [img.width, img.height],
        },
    }

    if debug:
        marked = img.convert("RGB")
        draw = ImageDraw.Draw(marked, "RGBA")
        for i, (top, bottom) in enumerate(bands):
            draw.rectangle([0, top, marked.width - 1, bottom], fill=(255, 40, 40, 40))
            draw.line([0, top, marked.width, top], fill=(255, 0, 0), width=2)
            draw.line([0, bottom, marked.width, bottom], fill=(0, 120, 255), width=2)
            draw.text((6, top + 2), str(i + 1), fill=(200, 0, 0))
        marked.save(OUT / f"{stem}-lines.png")
        print(f"debug overlay -> {OUT / f'{stem}-lines.png'}")

    html = OUT / f"{stem}-editor.html"
    html.write_text(
        build_html(
            stem, image_name, bands, img.height, meta, crop_top_px, source_scale
        ),
        encoding="utf-8",
    )
    heights = [b - a for a, b in bands]
    print(f"{src.name}: {len(bands)} lines detected")
    if heights:
        print(
            f"  line height min/median/max: {min(heights)}/"
            f"{sorted(heights)[len(heights) // 2]}/{max(heights)} px"
        )
    print(f"editor -> {html}")


if __name__ == "__main__":
    main()
