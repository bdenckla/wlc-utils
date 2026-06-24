# Plan B: generated "almost errors" HTML page

**Status (2026-06-24):** **DONE** — implemented as `py/accgram/almost_errors.py`
(subcommand `main_accgram.py generate-almost-errors-html`), output
`gh-pages/accgram/almost-errors.html`, linked from `index.html` and cross-linked
from both `goerwitz.html` (prose) and `poetic.html` (poetic) intros. Tests in
`py/tests/test_almost_errors.py`. **Scope expanded** per the maintainer from
"editorial charities" to **"almost errors"**: the page now also documents
**ek20:31** (`mahapakh!azla`) — which is *not* a charity (not an LC/BHS/WLC leniency)
but a puzzling-yet-standard masoretic tradition, MAM-confirmed (MAM keeps both marks;
its doc-note calls it the only word in Scripture with two conjunctive accents on one
letter, citing Yeivin Ch.1 p.232). The generated alternate-reading trees (telisha-
gedola exhibit) plus the live ek20:31 / lv25:20 trees are regenerated from the grammar
at build time via `ob_error_context.parse_tree_from_text` (a new clean-tree variant of
`parse_error_tree_from_text`) + the shared `ob_tree_table` renderer.

**Taxonomy corrected during implementation (maintainer, 2026-06-24):** the
telisha-gedola + geresh/gershayim family (the "drop-to-telg" five) and the
swallowed-helper fusions are **not charities** — they are *masoretically-blessed
oddities*, 100% official tradition attested in the standard witnesses, not leniencies
specific to LC/BHS/WLC. The checker isn't forgiving anything there; its only decision is
**representation** (which mark to keep / how to fuse), and the telg exhibit shows that
decision is a choice among grammatically-clean readings. So the page now has two H2s:
**Editorial charities** (geresh-muqdam→geresh, ps124:4 geresh→revia-mugrash, and
lv25:20's lexical re-classification of a genuine L anomaly) and **Masoretically-blessed
oddities (not charities)** (the telg five with the exhibit, ek20:31, the helper fusions).
One bridge case: **2 Kings 17:13** spans both — its prose geresh-muqdam first gets the
*charity* conversion to plain geresh, and only then is the resulting telg+geresh a
non-charity oddity like the other four.

Companion to **Plan A** (`doc/PLAN-A-same-letter-accent-pairs.md`), which defines the
charities this page documents and the taxonomy behind them. One-way dependency: Plan B
consumes Plan A's content, so Plan A's definitions (and the lv25:20 verdict) were
settled first.

## Goal

A **generated** HTML page that documents, in one place, every editorial "charity" the
accgram checkers apply — places where we *normalize away* a quirk of WLC (sometimes a
real Leningrad feature, sometimes an artifact introduced in BHS or WLC) and read the
text charitably rather than flagging it. The point is transparency: a reader (or future
us) can see exactly what we silently fix and why, with the alternatives we did **not**
choose shown as parse trees so the choices are visibly choices, not forced moves.

Linked from both the prose and poetic goerwitz pages. (Those two pages are expected to
be **merged** eventually; the charities page should be written so it serves the merged
page without rework.)

## Charities to document

Each entry: what we normalize, why, the direction, and a citation.

- **geresh-muqdam → geresh (prose).** WLC uses geresh-muqdam (U+059D), a poetic-only
  sign, in the 21 prose books only twice (lv1:3 alone; 2k17:13) as a typographic device
  for a plain geresh. Read as geresh. Cite tanach.us changes `2020.09.22-1`, `-2`.
- **plain geresh → geresh-muqdam (poetic), a charitable promotion.** A plain geresh in a
  poetic verse is otherwise a fail-fast lexical error (Plan A); the **sole exception** is
  ps124:4's revia + plain geresh on **one letter**, read charitably as revia-mugrash. The
  mechanism is two ingredients: within-letter order-normalization (revia+geresh ≡
  geresh+revia — same-letter only, cross-letter order preserved) **plus** promotion of the
  geresh to geresh-muqdam. NB this is **not** what makes ps124:4 parse *today* (today the
  geresh is silently swallowed and the bare revia reclassified) — it is the *principled*
  replacement. Cite <https://tanach.us/Notes/Psalms/Psalms.124.4.4-c.html>.
- **telisha-gedola + geresh/gershayim → telisha-gedola (drop).** Five words; keep the
  telg, drop the geresh/gershayim companion. (See the alternate-tree exhibit below.)
- **swallowed-helper fusions.** Stress-helper tsinnorit fused onto zinor (zarqa),
  doubled pashta, doubled telisha-qetana — fused into one token by the scanner.
- **mahapakh + tipeḥa → lexical error (lv25:20).** Not a charity that *hides* a quirk
  but a charity of *classification*: flagged as an alphabet (lexical) error, not a
  grammatical one (Plan A decision). Document alongside so the lexical-vs-grammatical
  distinction is visible.

## Exhibit: alternate readings of the five telg+gerstar verses

Verses: gn5:29, zp2:15 (same-letter); 2k17:13 (same-letter, geresh-muqdam); lv10:4,
ek48:10 (cross-letter, same word). Show, per verse, the parse tree under all three
readings to make visible that the chosen drop-to-telg is a choice among grammatical
options:

1. **chosen** — drop the gerstar, keep the telg;
2. **keep_gerstar** — drop the telg, keep the gerstar;
3. **keep_both** — keep both, as a telg-then-gerstar sequence.

**Prototyped and confirmed (2026-06-23):** all 5 × 3 = 15 parse **clean** (no ERROR, no
NO_PARSE). The trees differ exactly where expected — e.g. zp2:15: chosen →
`big_telisha_phrase(telishagedola)`; keep_gerstar → `geresh_phrase(gershayim)`;
keep_both → `big_telisha_phrase` **then a nested** `geresh_phrase` (the telg→gerstar
sequence, one tree level deeper). The variant logic (a mode-parameterized
`word_to_marks` that drops telg / drops gerstar / drops neither, scoped to words holding
*both*) drops cleanly into the page generator; the **full prototype is in the Appendix
below** — it produced the confirmation above and regenerates every tree the exhibit
shows.

### Finding that affects presentation

Even the **same-letter** keep_both case (zp2:15) already renders **as a sequence**
(telg-phrase then geresh-phrase at different depths), *not* a fused same-letter cluster
— because telg is prepositive (relocated to the front of the word) and the scanner
emits the two marks as separate tokens. So:

- The repeated-word didactic trick (e.g. showing `זאת` twice — first with telg, then
  with gerstar — to illustrate the sequence) is **not needed** to make the sequence
  visible; the real word's keep_both tree already shows it.
- If we use the repeated-word version anyway for clarity, the page **must label it as a
  synthetic / constructed token stream**, not a real WLC reading (faithfulness).

## Open questions

- Generator: where do the prose/poetic goerwitz pages get built, and what's the cleanest
  hook to emit a sibling page + cross-links? (Scope this when starting.)
- How much of the taxonomy (Plan A) belongs on the page vs. linked-to?
- Tree rendering: reuse `ply_tree.print_tree` (monospace) or render structured HTML?

## Appendix: prototype (regenerates the exhibit)

Run from `py/`, `PYTHONIOENCODING=utf-8`, via `../.venv/Scripts/python.exe`. Read-only;
no module is modified (it temporarily swaps `uni_to_marks.word_to_marks` for a
mode-aware copy, scoped to words carrying *both* telg and a gerstar, then restores it).

```python
from pathlib import Path
from accgram import rtms_data, research_tao, uni_to_marks, ply_scanner, ply_grammar
from accgram.uni_to_marks import (
    _is_base_letter, _is_accent, _KEPT_NON_ACCENT, _PREPOSITIVE_MARKS, _MAQAF,
)
from accgram import accent_marks as am
from accgram.ply_scanner import Token, HasLegarmeh
from accgram.ply_tree import print_tree

_GG = frozenset((am.GERESH, am.GERSHAYIM))


def build_word(word: str, mode: str) -> str:
    """word_to_marks, but for a word carrying BOTH telg and a gerstar, apply `mode`."""
    has_telg = am.TELISHA_GEDOLA in word
    has_gerstar = any((am.GERESH if c == am.GERESH_MUQDAM else c) in _GG for c in word)
    both = has_telg and has_gerstar
    skeleton: list[str | None] = []
    prepos: list[str] = []
    other: list[str] = []
    telg_seen = 0
    for ch in word:
        if _is_base_letter(ch):
            skeleton.append(am.LETTER); continue
        if ch == _MAQAF:
            skeleton.append(am.MAQAF); continue
        mark: str | None = None
        if _is_accent(ch):
            if ch == am.TELISHA_GEDOLA:
                telg_seen += 1
                if telg_seen > 1:
                    continue
                if both and mode == "keep_gerstar":
                    continue  # drop the telg
                mark = am.TELISHA_GEDOLA
            else:
                as_geresh = am.GERESH if ch == am.GERESH_MUQDAM else ch
                if as_geresh in _GG:
                    if both and mode == "chosen":
                        continue  # drop the gerstar (current behavior)
                    mark = as_geresh
                else:
                    mark = ch
        elif ch in _KEPT_NON_ACCENT:
            mark = ch
        if mark is None:
            continue
        skeleton.append(None)
        (prepos if mark in _PREPOSITIVE_MARKS else other).append(mark)
    marks = iter(prepos + other)
    return "".join(next(marks) if p is None else p for p in skeleton)


index = rtms_data.load_wlc422_index(
    research_tao.default_wlc422_kq_u_dir(Path("..").resolve()))
parser = ply_grammar.build_parser()

REFS = ["gn5:29", "zp2:15", "2k17:13", "lv10:4", "ek48:10"]
MODES = ["chosen", "keep_gerstar", "keep_both"]


def verdict_and_tree(bcv, mode):
    bb = bcv[:2]; ch, vr = bcv[2:].split(":")
    orig = uni_to_marks.word_to_marks
    uni_to_marks.word_to_marks = lambda w: build_word(w, mode)
    try:
        body = uni_to_marks.verse_to_marks(index[bcv])
    finally:
        uni_to_marks.word_to_marks = orig
    toks = [Token("TILDE", "")] + ply_scanner.scan_accents(
        body, bb, int(ch), int(vr), HasLegarmeh())
    tree = ply_grammar.parse_tokens(parser, toks)
    has_error = tree is not None and "ERROR" in print_tree(tree)
    v = "NO_PARSE" if tree in (None, ply_grammar.LOCATION_ONLY) else (
        "ERROR" if has_error else "ok")
    return v, tree


for bcv in REFS:
    print("=" * 70); print(bcv)
    for mode in MODES:
        v, _ = verdict_and_tree(bcv, mode)
        print(f"  {mode:13s} -> {v}")

for bcv in ["zp2:15", "lv10:4"]:          # one same-letter, one cross-letter
    for mode in MODES:
        print("\n" + "#" * 70); print(f"{bcv}  [{mode}]")
        v, tree = verdict_and_tree(bcv, mode)
        print(print_tree(tree) if tree not in (None, ply_grammar.LOCATION_ONLY) else v)
```
