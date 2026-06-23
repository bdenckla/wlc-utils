# Plan: same-letter accent pairs (general)

**Status:** in progress. Resolved so far: ek20:31 (mahapakh+azla, **fused**); the whole
telisha-gedola + geresh-family family (5 words, **drop-to-telg**); geresh-muqdam in prose
(read as geresh); poetic revia-mugrash (already an established single token). Remaining:
the illegal mahapakh+tipeḥa (lv25:20), and a "check current handling" pass on the poetic
pairs. See `doc/PLAN-ezekiel-20-31-azla-mahapakh-order.md` (a worked example, slated for
eventual deletion) and the durable design note in memory `fused-impositive-cluster-token`.

## Goal

Decide, cluster by cluster, how the accgram grammar-checker should treat **two
cantillation accents sharing one base letter**. The resolved precedent: such a pair
has no natural order, so it is not a *sequence* for the grammar to judge — fuse it
into one unitary token with an `!`-joined leaf (e.g. `mahapakh!azla`), then write the
grammar rule(s) the real occurrences need. Some clusters are *illegal* (the fused
token should land in an ERROR/oddball context, not a clean rule); some are *normal*
(esp. in the poetic books) and may already be handled.

**Confirmed:** a single letter never carries more than 2 accents — only pairs, never
triples (corpus-wide scan, see Recipe below).

## Faithful scan recipe (IMPORTANT)

Scan the **raw `-kq-u` words**, NOT the `uni_to_marks` output: `uni_to_marks`
*drops* swallowed-secondary telisha-gedola/gershayim (and would thus hide some
clusters). Walk each word; a "same-letter cluster" = ≥2 accents (U+0591..U+05AE,
meteg U+05BD excluded) between two base consonants.

```python
from pathlib import Path
from collections import Counter, defaultdict
from accgram import rtms_data, accent_marks as am, research_tao
index = rtms_data.load_wlc422_index(
    research_tao.default_wlc422_kq_u_dir(Path('..').resolve()))
NAME = {getattr(am,n): n for n in dir(am)
        if isinstance(getattr(am,n),str) and len(getattr(am,n))==1 and '֑'<=getattr(am,n)<='֮'}
# for each word: group accents between base letters (א..ת); report groups with len>=2,
# keyed by the accents' source order, with bcv refs.  (Run from py/, PYTHONIOENCODING=utf-8.)
```

## Inventory (corpus-wide, source order)

Two populations. **Dual-cantillation verses** carry both ta'am elyon and ta'am
tachton, so nearly every letter is double-accented; these are *excluded from / not
grammar-checked* and should be ignored here: the **decalogues** (Exodus 20, Deut 5)
and **Genesis 35:22** (Reuben). They account for the bulk of raw scan rows
(atnax+zaqef, tipeha+munah, munah+pashta, pazer+zaqef, …) — all noise for this task.

The **real targets** (normally-cantillated text, dual-cantillation refs removed):

### Prose
| cluster (source order) | refs | notes |
|---|---|---|
| mahapakh + qadma/azla | ek20:31 | **DONE** → fused `mahapakh!azla`; legal, clean parse. |
| telisha-gedola + gershayim (same letter) | gn5:29, zp2:15 | **DONE** → keep telg, **drop the gershayim** (read as the telg's stress-helper companion). Telg-only, clean parse. (Previously *both* were dropped — the word was silently unaccented.) |
| telisha-gedola + geresh-muqdam (same letter) | 2k17:13 | **DONE** → geresh-muqdam charitably read as geresh (it is a poetic-only sign; its use in prose is typographic), then dropped as the companion (`telg!germuq → telg!geresh → telg`). Telg-only, clean parse. |
| mahapakh + tipeḥa | lv25:20 | The "mahapakh-tipeḥa" — both *below*-accents, considered an **error**/illegal. Wants `mahapakh!tipexa` landing in an oddball/ERROR, not a clean rule. |

**Note — telisha-gedola + geresh/gershayim (resolved together).** There are exactly
**five** words corpus-wide carrying both a telisha-gedola and a geresh or gershayim
(counting 2k17:13's prose geresh-muqdam as the plain geresh it stands for): the three
same-letter ones above plus two **cross-letter, same-word** ones — lv10:4 (telg…gershayim)
and ek48:10 (telg…geresh). All five are now handled in `uni_to_marks.word_to_marks` as
**two conceptual steps, in order**: (1) read a prose geresh-muqdam as the plain geresh it
mis-encodes (it is a poetic-only sign — see below); then (2) if a word has a telisha-gedola,
keep it and drop any geresh or gershayim in that word. Rationale: the
(prepositive) telg is treated as analogous to the (prepositive) geresh-muqdam, and the
geresh (or gershayim) as analogous to the revia of *revia mugrash* — a prepositive whose
stress-helper is always written even when (the stress being initial) it is not needed.
The manuscripts drop that revia on initial stress but cannot drop the geresh/gershayim
(the word would then read as a plain telisha-gedola). Two **alternatives are equally
grammatical** (verified for all five): drop the telg and keep the geresh/gershayim; or
keep both and read the same-letter pairs as a telg-then-geresh *sequence* (the cross-word
telg → geresh/gershayim bigram occurs ~165×, so the sequence parses cleanly). The
sequential reading is **deliberately not** chosen — it is not the right way to think of
these words, even the two cross-letter ones. Note this is **drop**, not **fusion** — the
opposite resolution from ek20:31's `mahapakh!azla`.

**Note — geresh-muqdam in prose (lv1:3, 2k17:13).** *In WLC*, geresh-muqdam (U+059D)
appears in the 21 prose books only twice — a property (arguably a bug) of **WLC**, not a
statement about the wider Masoretic tradition. Both are typographic devices for a plain
geresh: lv1:3 (alone) and 2k17:13 (the telg word above). The prose scanner reads it as
geresh (lv1:3 — previously silently dropped); the 2k17:13 one is read as geresh and then
dropped upstream as the telg companion. Cited in code: tanach.us changes
`2020.09.22-1` (lv1:3) and `2020.09.22-2` (2k17:13).

### Poetic
| cluster (source order) | refs | notes |
|---|---|---|
| geresh-muqdam + revia | 241× (all Psalms: ps7:1, ps11:1, …) | This is **revia mugrash**, a *normal* poetic accent (geresh + revia as one unit). Almost certainly already handled by the poetic scanner — verify it parses, don't "fix" it. The high count is the tell. |
| merkha + qadma | ps56:10 | Check current handling. |
| munah + deḥi | ps135:2, jb32:13 | deḥi is prepositive. Check current handling. |
| revia + geresh | ps124:4 | Note the *reversed* order vs revia-mugrash's geresh+revia — a variant/anomaly to look at. |

(Exact counts/refs as of 2026-06-22 against `wlc422-kq-u`. Re-run the recipe to refresh.)

## Method (per cluster), reusing the ek20:31 precedent

1. Confirm same-letter (raw scan) and whether the occurrences are in grammar-checked
   genre (prose vs poetic; not decalogue/gn35:22).
2. Decide legal vs illegal (consult Yeivin / a MAM edition's doc-notes, e.g.
   <https://bdenckla.github.io/MAM-with-doc/> by chapter+verse).
3. If fusing: add a `_GG_RULES` entry in the relevant scanner (`ply_scanner` for
   prose, `ply_scanner_poetic` for poetic) matching the two marks **adjacent** (no
   `X` between → same letter), in storage/codepoint order, emitting one token with an
   `!`-joined leaf; add it *above* the single-mark rules (longest-match wins anyway).
   Add the grammar token + only the **attested** rule(s) (no speculative variants —
   see memory `parse-rate-not-a-goal`).
4. For clusters currently handled by **dropping** a secondary (telisha-gedola +
   gershayim/geresh-muqdam), the choice is fuse-vs-keep-dropping; unifying on fusion
   means revisiting `uni_to_marks` lines ~115-124.
5. Verify: `pytest`; regenerate the affected corpus (`main_accgram.py
   run-ply-goerwitz` for prose, the poetic entrypoint for poetic) and confirm the
   diff is only the intended verses.

## Open questions

- ~~Is the poetic revia-mugrash (geresh-muqdam+revia, 241×) already a recognized single
  token…?~~ **RESOLVED:** yes — `ply_scanner_poetic` already emits one `REVIA_MUGRASH`
  token (`GERESH_MUQDAM [+ REVIA]`); it is an established accent, out of scope here.
- Should the illegal clusters (mahapakh!tipexa) get a *named* fused leaf at all, or
  is a distinct ERROR/oddball flavor better, so they read as wrong rather than as a
  recognized unit?  *(Still open — the only remaining prose cluster.)*
- ~~Consistency: one uniform strategy (fusion) for all same-letter pairs?~~ **RESOLVED
  as: no, not uniform.** Strategy is per-cluster by what the pair *means*: **fuse** when
  the two accents are a genuine unit with no natural order (ek20:31 `mahapakh!azla`);
  **drop** the companion when one accent is a stress-helper of a prepositive
  (telg + geresh-family → telg). The drop-secondary approach in `uni_to_marks` is kept,
  now stated as a principled rule rather than an incidental clustered-secondary drop.

## Remaining (poetic, lower priority)

The poetic same-letter pairs (merkha+qadma ps56:10, munah+deḥi ps135:2/jb32:13,
revia+geresh ps124:4 — the reversed-order anomaly) still want a "check current handling"
pass; revia-mugrash itself is resolved (above).
