# Plan E: prose same-letter whitelist — the prose analogue of Plan D's guard

**Status (2026-06-23):** new, **not started** — investigation done, implementation pending
the open question below. Spun off from **Plan D**
(`doc/PLAN-D-faithful-same-letter-bangs.md`), which gave the *poetic* system a same-letter
"only whitelisted pairs may share a letter; anything else is a bang → NO_PARSE oddball"
guard. The maintainer asked whether the prose system has an equivalent (much stricter)
rule, suspecting the prose whitelist might be empty.

## The question

Poetic's same-letter whitelist is three pairs (revia+geresh-muqdam, deḥi+munaḥ,
oleh+yored) — **all poetic-specific accents that do not exist in the prose system**. So
what is the prose whitelist, and should prose get the same "flag any non-whitelisted
same-letter accent pair" guard?

## Empirical finding — the prose corpus has exactly TWO same-letter accent pairs

Scan of the **prose scanner body** (`uni_to_marks.verse_to_marks`, `prose_filter` so
decalogues / Gn 35:22 are already excluded) for two adjacent accents (no `X` between →
same letter):

| pair | count | verse | status |
|---|---|---|---|
| mahapakh + qadma | 1 | ek20:31 | the "known exception" — fused to `mahapakh!azla`, **accepted** |
| mahapakh + tipeḥa | 1 | lv25:20 | **flagged illegal** via `lexical_validation.illegal_below_pairs` |

Reproduce (run from `py/`, `PYTHONIOENCODING=utf-8`):
```python
from pathlib import Path
from collections import defaultdict
from accgram import rtms_data, research_tao, uni_to_marks, prose_filter
from accgram import accent_marks as am
def isacc(c): return '֑'<=c<='֮'
index=rtms_data.load_wlc422_index(research_tao.default_wlc422_kq_u_dir(Path('..').resolve()))
pairs=defaultdict(list)
for bcv,verse in index.items():
    bb=bcv[:2]; ch,_,vr=bcv[2:].partition(':')
    if not prose_filter.should_keep_line(bb,int(ch),int(vr)): continue
    body=uni_to_marks.verse_to_marks(verse)
    for i in range(len(body)-1):
        if isacc(body[i]) and isacc(body[i+1]): pairs[(body[i],body[i+1])].append(bcv)
print(pairs)   # -> only (mahapakh,qadma):[ek20:31] and (mahapakh,tipeha):[lv25:20]
```
The prose stress-helper fusions (zarqa = tsinnorit+zinor, doubled pashta, doubled
telisha-qetanna) are **cross-letter** (their scanner rules allow `_TEXT` between the two
marks), so they never produce a same-letter pair — confirmed: they do not appear above.

## MAM evidence — the whitelist is {mahapakh+qadma}, and it is two-witness-confirmed

- **ek20:31** `נִטְמְאִ֤֨ים` carries mahapakh (U+05A4) + qadma (U+05A8) on one letter,
  **no `]c` note**. **MAM keeps BOTH** marks (`MAM-simple/json-vtrad-bhs/Ezek.json`,
  same word `נִטְמְאִ֤֨ים`). So this is a **genuine, two-witness-confirmed** same-letter
  pair — a real exception, not just a special-case.
- **lv25:20** `נֹּאכַ֤֖ל` carries mahapakh + tipeḥa (two *below* accents). **MAM keeps only
  the tipeḥa** (dropped the mahapakh) — an L anomaly, already flagged (`]c]n` in WLC; see
  Plan A's lv25:20 section).

**Contrast with poetic ps56:10** (`merkha!azla`): there MAM dropped the merkha (L-only),
so Plan D flagged it. ek20:31 is the mirror image — MAM agrees — so it is **legitimately
whitelisted**. This resolves the ek20:31-vs-ps56:10 consistency question that Plan D
deferred: they are treated differently *because the witnesses differ*.

**Conclusion:** the prose whitelist is **exactly one pair, `{mahapakh+qadma}`**, and it is
evidence-backed. (Slightly stronger than "empty": there *is* one whitelisted pair, but it
is the only one, and it is real.) Everything else two-on-a-letter is illicit.

## Current handling vs the proposed strict rule

Prose already enforces this *piecemeal*, not as a principle:
- ek20:31 → scanner fusion rule `am.MAHAPAKH + am.QADMA → MAHAPAKHAZLA`
  (`ply_scanner.py`), leaf `mahapakh!azla`, accepted by the grammar. (The whitelist.)
- lv25:20 → `lexical_validation.illegal_below_pairs` detects **mahapakh+tipeḥa
  specifically** → `illegal_mark` tree, grammar skipped (wired in `run_ply.render_book`).

**Proposed (the equivalent of Plan D's whitelist guard):** replace the *specific*
`illegal_below_pairs` (mahapakh+tipeḥa only) with a **general** detector — "any two
accents on one base letter (adjacent in the body, no `X` between) that is **not** the
whitelisted `mahapakh+qadma` → `illegal_mark`." This:
- keeps lv25:20 flagged (now via the general rule, label still `mahapakh!tipexa`);
- keeps ek20:31 accepted (the scanner fuses it to `MAHAPAKHAZLA` before the grammar; the
  detector whitelists `mahapakh+qadma`);
- guards any *future* same-letter prose pair (parity with poetic; cf. memory
  `parse-rate-not-a-goal` — principled tightening, even if it flags nothing new today);
- is **output-neutral** on today's corpus (only ek20:31 and lv25:20 exist, both unchanged).

**Key surface difference from Plan D:** poetic had no lexical layer, so its guard emits a
bang token with **no grammar terminal → NO_PARSE** (`ply_scanner_poetic._BANG_GUARD`).
Prose **already has** the lexical-error surface (`lexical_validation` → `illegal_mark`,
skip grammar), so the prose guard belongs **in `lexical_validation`**, not the scanner.
The label convention is the same bang (`a!b`), already used by both `mahapakh!azla`
(ek20:31, accepted) and `mahapakh!tipexa` (lv25:20, illegal) — see Plan A: the bang is a
*representation* orthogonal to the verdict.

## First step on resume (Phase-1 mapping was interrupted)

Read these to confirm exact signatures before editing (the Explore pass did not run):
- `py/accgram/lexical_validation.py` — `illegal_below_pairs`, `stranded_stress_helpers`,
  the returned record (a `StrandedMark`-style dataclass with a `code` field holding the
  bang string), and `_ILLEGAL_MARK_REP_CHAR` + `_stranded_unicode_words` (the
  code→representative-char map used to locate the offending pointed word from the kq-u
  index). The new general detector must mint the same record shape with `code = "a!b"`,
  keyed on a representative codepoint for word location.
- `py/accgram/run_ply.py` (`render_book`) — where it calls the detectors, ORs their
  results, and emits `_illegal_mark_tree` + skips the grammar. The general detector slots
  in alongside (or replaces) `illegal_below_pairs` in that block.
- `py/accgram/ply_scanner.py` — the `MAHAPAKHAZLA` rule + `_LEAF` (the whitelist member,
  left as-is); confirm the helper fusions are cross-letter.

## Implementation sketch

1. In `lexical_validation.py`, add a detector e.g. `illegal_same_letter_pairs(body)` that
   scans the body for two adjacent accents (`[֑-֮]{2}`, no `X` between) and
   returns an illegal-mark record for each pair **except** the whitelisted `mahapakh+qadma`
   (U+05A4 + U+05A8). Label `code = f"{name_a}!{name_b}"` reusing the prose leaf names
   (mahapakh, tipexa, azla, …). Key the rep-char on the pair's first/distinguishing
   codepoint for `_stranded_unicode_words` word location (mirror how lv25:20 keyed on
   mahapakh, NOT tipeḥa, which recurs elsewhere in the verse).
2. Define the whitelist as a small constant (e.g. `_WHITELISTED_SAME_LETTER = {am.MAHAPAKH+am.QADMA}`),
   the prose analogue of `ply_scanner_poetic._WHITELISTED_ADJACENT_PAIRS`.
3. Either **replace** `illegal_below_pairs` with the general detector (lv25:20 becomes a
   sub-case) or have the general one subsume it; update `run_ply.render_book` wiring.
4. Keep the ek20:31 scanner fusion (`MAHAPAKHAZLA`) — it is the whitelisted, MAM-confirmed
   pair; do **not** flag it.

## Verification

- `pytest` (extend `py/tests/test_lexical_validation.py`: lv25:20 mahapakh+tipeḥa still
  flagged via the general rule; a *third* hypothetical same-letter pair flags; ek20:31's
  mahapakh+qadma does **not** flag; a cross-letter pair does not flag).
- Regenerate the prose corpus (`main_accgram.py run-ply-goerwitz`) and confirm the diff is
  **empty** (output-neutral: lv25:20 still `illegal_mark mahapakh!tipexa`, ek20:31 still a
  clean tree with `mahapakh!azla`, nothing else changes).
- Drive-one-verse / faithful-scan recipes: reuse Plan A's (`doc/PLAN-A-same-letter-accent-pairs.md`).

## Open question for the maintainer (decide before implementing)

The investigation is done and the rule is output-neutral. The choice is whether to
**build the general guard** (generalize `lexical_validation`; future-proofing + conceptual
parity with poetic Plan D) or **leave the current piecemeal handling** (specific
`illegal_below_pairs` for lv25:20 + the `MAHAPAKHAZLA` fuse for ek20:31) and just record
the finding that the prose whitelist = {mahapakh+qadma}, MAM-confirmed.

Note either way: **ek20:31 stays accepted** (MAM confirms the double-marking), so the
Plan D deferred item "revisit prose ek20:31 under the whitelist" resolves to **keep it** —
it is the (sole, legitimate) prose whitelist entry, not an anomaly.
