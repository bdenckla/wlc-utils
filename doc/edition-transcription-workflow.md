# Transcribing a printed edition's Decalogue

The procedure behind `in/accgram/edition_transcriptions/`, tracked by
[#69](https://github.com/bdenckla/wlc-utils/issues/69). Written down so a session can pick the
work up from here rather than from a long handoff.

**Division of labour: the assistant displays, aligns and reports; Ben reads the accents.** A
transcription's header claims primary observation read off the book, and the tests pin its
divergences as established — so a machine-read token would be recorded as an edition's real
divergence rather than caught as an error. Offer zoomed crops to make the reading easier; never
offer your own token readings as the transcription.

## 1. Find the page and build the editor

Scans live outside the repo (see the `book-scan-page-naming` note; `WLC_SCANS_DIR` overrides
the root). Render a whole page first to locate the Decalogue and pick a crop:

```bash
.venv/Scripts/python.exe py/accgram/scan_page.py "Feldheim Simanim Tiqqun" C208 --width 1100
```

Then build the per-line editor over the pointed text column only — a two-column page profiled
whole has no clean troughs. `--debug` also writes `<stem>-lines.png` with the detected bands
drawn on, which is worth checking before anyone types into it:

```bash
.venv/Scripts/python.exe py/accgram/transcription_editor.py "Feldheim Simanim Tiqqun" C208 \
    --crop 0.452 0.540 0.856 0.830 --name simanim_dt_elyon_p208 --width 1300 --debug
```

Crop tight enough to exclude the neighbouring column: a sliver of foreign glyphs at either edge
shows up in the debug overlay. Open `.novc/scans/<stem>-editor.html` in the Browser pane. A
Decalogue spanning two printed pages gets one editor per page.

**Opening a local file in the Browser pane works, and sessions keep concluding it does not.**
No dev server and no `.claude/launch.json` are needed or wanted — a `file://` URL with an
absolute path in forward slashes is enough: `preview_start` with
`file:///C:/.../wlc-utils/.novc/scans/<stem>-editor.html`, then `tabs_context` to see which
tab actually holds it, then a screenshot **with an explicit `tabId`**. Four things mislead,
each looking like "the file did not load": `computer` without a `tabId` fails
input-validation, which reads as a load failure on the first screenshot; `navigate` reports
success while the content lands in a different tab than the id passed, leaving the named one
answering "No site is open in this tab"; the pane fits an image to the viewport and does not
scroll, so a tall debug overlay is unreadable there and the Read tool on the PNG is the better
check anyway; and the "renders as static snapshots" note means only that there is no
live-reload — scripts run, the editor's inputs accept typing, and its `localStorage` survives
across sessions, which is what makes the typed-line persistence below work at all.
Regenerating a PNG in place will **not** refresh an open tab, so write a fresh filename and
open a fresh tab, and screenshot before believing any of it.

**That "tight" is about the HORIZONTAL bound only. Vertically, do the opposite: crop to the
middle of the line above and the middle of the line below.** Hebrew stacks marks above *and*
below its letters, so a vertical crop trimmed to the transcribed text cuts the outermost line's
marks off — and a half-line of context is what lets its own above-marks be told apart from the
last full line's below-marks. Be decisive about it, because the half-measure is the worst
option: a crop that clips only a *sliver* of the next line leaves a fragment shorter than a
half-line, which `_absorb_slivers` folds into the last real band. On Koren A5-D-281 a bottom of
0.5945 clipped line 17, and 0.610/0.614 — chosen to avoid exactly that — gave the last band a
height of 208 and 232 px against a true 127. Clear the next line entirely, or take half of it.

The editor now says so itself: it warns when a band is too tall to be one line (the merge
above), and notes when the first or last band touches a crop edge. The note is deliberately not
a warning, since on a correct crop the outermost band *is* the context half-line and touches the
edge by design — check which band number it names.

**Measure the column's edges; do not eyeball them.** On C247 a crop guessed by eye landed
~0.006 of the page width inside the true right edge and clipped the first letter of every line
— in RTL, where the line *starts*. The debug overlay does not show this: a third of a letter
missing still looks like a line. Profile the ink instead (dark-pixel fraction per x column over
the text's vertical band) and set the crop from the numbers, then leave a margin. Only
*prepositive* accents sit at a word's right edge, so a right-edge clip endangers those; a
left-edge clip endangers postpositives.

## 2. Ben types; **Save JSON** exports to Downloads

**Hand over the editor, do not merely announce that it exists.** The handoff is a step of this
procedure, not a courtesy at the end of one: paste the `file://` URL of each page's editor in
full so it can be clicked, say which bands to type and which are context to leave blank, and
bring the page up in the Browser pane and screenshot it so the handoff message can state that
the editor is live and how many bands it found. A turn that ends with the crops measured and no
link is a turn that has not delivered the thing the transcriber needs. Keep the reasoning that
led to the crop out of the handoff, or below the instructions; what belongs at the top is the
URL, the band ranges, and any question only Ben can answer (whether the edition distinguishes
paseq from legarmeh, say).

Hebrew is typed, not Latin: translating every mark in your head while holding your place on the
line is the thing to avoid. Any **unique prefix of the accent's Hebrew name** works — `זר`
zarqa, `פז` pazer, `סג` segolta — and the full name always does. An ambiguous prefix is rejected
with its candidates rather than guessed. `תג`/`תק` and `גר` are explicit exceptions.

Three ways to record a pasoleg, and which one is right is a fact about the **edition**, not
about the position: `מונ_לג` (`mun_leg` in the `.txt`) asserts munaḥ legarmeh, `[פסק]`
(`[paseq]`) asserts a narrow-sense paseq, and `[פסלג]` (`[pasoleg]`) says only that a stroke
stands there. The third exists because not every edition draws the distinction — Koren prints
the stroke without saying which it is, so either of the first two would claim more than the
book does. Record which the edition does in the `.txt` header, as
`pasoleg_kinds: distinguished` or `not distinguished`; a test then holds a `not distinguished`
transcription to using no kind-asserting notation, in either file and either spelling.

Three joiners now, and they are not interchangeable. `-` is a **maqaf**, binding two accents
into one chanted word (`mun-mer`). `+` is its **simple-word** counterpart — two accents on a
word that is no compound at all, as in `קד+גר` on ויצאך (p. 247), where the first accent is by
convention called *metigah* rather than *qadma*. Both contribute one token per accent; keeping
them distinct is what lets a difference still be read as word-division or not. `_` binds two
**marks** into one accent (`מונ_לג`) and contributes one token.

Where the joiners are implemented matters, because it once went wrong. `+` was added to
`edition_transcription.py` and not to `transcription_check.py`, which split chunks by its own
copy of the same rule; the .txt came out right while the check that guards it rejected `קד+גר`
as an unknown abbreviation. Splitting a chunk into its accents now lives in one function,
`edition_transcription.editor_accents`, which the check and the .txt writer both call, and
`test_editor_export_and_txt_agree` runs an export down both routes so a future divergence fails
a test rather than surfacing as a puzzling runtime message.

## 3. Check before committing

```bash
.venv/Scripts/python.exe py/accgram/transcription_check.py \
    ~/Downloads/simanim_dt_elyon_p208-transcription.json \
    ~/Downloads/simanim_dt_elyon_p209-transcription.json --key dt elyon printed
```

It reports token and chanted-verse counts, every difference region with the reference word and
the printed page and line it came from, and the pasoleg placements — the transcribed side
mapped through the diff into reference coordinates first, since the two sides index different
token streams and an insertion upstream of a pasoleg would otherwise shift it off its
reference position. Run it on a partly typed page too — a problem then shows up before the rest
is typed.

For any difference, before calling it an accent difference:

- **Look at the word.** If the two texts divide words differently (maqaf vs. space), the marking
  usually follows mechanically. "Usually" — a maqaf compound *can* bear two accents, written
  `mun-mer`; p. 246 has two.
- **Zoom the printed line** and let Ben re-read it. Never crop at the band edge:
  ```bash
  .venv/Scripts/python.exe py/accgram/zoom_line.py <export.json> 12
  ```
  `zoom_line` pads a full band height above, because a tight crop once cut the upper dot off a
  zaqef qatan and left something that reads exactly like a revia. It also pads *sideways* past
  the crop it was given, so that a too-tight page crop cannot bound the zoom made to check it.
  A zoom shows the padding band above as a second line of text — the line being adjudicated is
  the **lower** one.
- **Check all eight strands** before concluding whose divergence it is:
  ```bash
  .venv/Scripts/python.exe py/accgram/transcription_check.py --site השבת לקדשו
  ```
  The site is located by the skeleton of the word *and* of the word after it. Confirm all eight
  strands are **listed**, and that every zero-hit row has an explanation — the word is absent
  from that strand's text, or the pair straddles a chanted-verse boundary there — rather than a
  skeleton typo. Do not expect eight *hits*: a word present in all eight gives eight, and the
  השבת example above is one (Deuteronomy's tenth commandment opens ולא where Exodus's opens לא,
  and a filter that missed that once made a four-strand result look like eight), but a
  legitimate discriminator gives fewer — `אתה ובנך` hits only the two `ex/taxton` strands.

## 4. Commit the pair

`<stem>.txt` (canonical for the parser) and `<stem>.json` (the audit trail: what was typed, per
line, against coordinates in both the rendering and the source scan, with the scan's sha256). A
two-page Decalogue puts both exports under `pages`, in page order. Derive the `.txt` from the
corrected export rather than typing it, so the two cannot drift; a correction made after export
goes into the JSON with the superseded reading kept in `corrected_from`, and into the `.txt`
header.

Then pin the result in `py/tests/test_edition_transcriptions.py`: the divergence list (exactly,
even when empty) and the chanted-verse count.

## What the harness cannot tell you

**The review loop is asymmetric.** It flags only positions where transcription and reference
already disagree, so only those get re-read. "No divergences" means no divergence survived a
procedure that never inspects the agreeing majority. The Exodus elyon's two real divergences
cancelled in the token count, so equal totals are not agreement either.

**On a page where a divergence is expected, the asymmetry runs the other way** — the loop
re-examines only positions that already disagree, so on such a page it pushes toward
*confirming* the thing you went in expecting. Run the eight-strand `--site` check before
forming a view, not after, and where possible get evidence the loop had no stake in. The one
that worked on p. 247 was **re-running the whole comparison against a different strand**: the
transcription agreed with the p-trad everywhere except the Shabbat commandment and with the
m-trad exactly there, the two partitioning the differences with nothing left over. Agreement
over a contiguous run with a strand nothing had flagged is positive evidence; a flagged
position surviving a re-read is not.

**Legarmeh vs. narrow-sense paseq is not checkable against the vendored data.** Its fetch folds
`{{מ:לגרמיה}}` and `{{מ:פסק}}` both onto U+05C0, so those positions score as neither agreement
nor disagreement — see #69's re-vendoring item. MAM-parsed-plus *does* keep them distinct (cell
E, per strand via `מ:כפול` א/ב), but only for the m-trad; see
[#68](https://github.com/bdenckla/wlc-utils/issues/68).
