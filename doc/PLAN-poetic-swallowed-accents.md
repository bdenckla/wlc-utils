# Plan C: faithful poetic scanning — stop swallowing real accents

**Status (2026-06-23):** new, not started. Companion to **Plan A**
(`doc/PLAN-same-letter-accent-pairs.md`) and **Plan B**
(`doc/PLAN-editorial-charities-page.md`). Discovered while running down the ps124:4
geresh: the poetic scanner (`ply_scanner_poetic`) **silently swallows real accents**
instead of representing them. This plan owns the two *legal* swallowed accents —
**tsinnorit** and **shalshelet qetannah** — whose fix is faithful *representation* (fuse
/ emit), with **no grammaticality verdict change**. The third swallowed accent, the
*illegal* poetic **geresh** (the catch-all's only customer), stays in **Plan A** because
its fix is fail-fast + a same-letter charitable promotion, and geresh+revia is a
same-letter pair.

## The defect, and how it was found

The poetic scanner's rule table ends with a catch-all `(re.compile(r".", re.DOTALL),
None)` and an explicit swallow set `[TSINNORIT SHALSHELET METEG PASEQ UPPER_DOT
LOWER_DOT]` ([`ply_scanner_poetic.py`](../py/accgram/ply_scanner_poetic.py) ~L120–131).
A `None` rule consumes its match and emits nothing — the accent vanishes, and whether
the verse is still well-formed is left to downstream luck.

**Systematic method (reusable).** There are two drop stages; sweep both across the whole
poetic corpus:

1. **`uni_to_marks.word_to_marks`** (pre-scan) drops only the non-first of a repeated
   telisha-gedola and a geresh/gershayim sharing a word with telisha-gedola — the five
   telg words, **all in prose books**, so **zero poetic impact**.
2. **The scanner's `None` rules.** Replicate the rule loop; when the winning rule's token
   type is `None`, record the accent codepoints in the matched span, attributed to
   *catch-all* vs *explicit-set*.

Sweeping every poetic verse (U+0591..U+05AE) yields exactly three swallowed accents:

| accent | count | rule | verdict |
|---|---|---|---|
| **geresh** (U+059C) | 1 (ps124:4) | catch-all `.` | illegal — **Plan A** (fail-fast + charity) |
| **tsinnorit** (U+0598) | 198 | explicit set | **real accent — fuse (this plan)** |
| **shalshelet** (U+0593, no bar) | 8 | explicit set | **real conjunctive — emit (this plan)** |

The permanent, self-checking version of the method is the fix itself: replace the
catch-all `None` with a **fail-fast** lexical flag (Plan A), and convert the two
explicit-set swallows into real rules — after which *nothing* a poetic verse can carry
disappears silently.

## tsinnorit (U+0598) → mahpakh / merkha *metzunar*

Tsinnorit is a **real poetic accent**, not noise — the "centered lookalike" of
tsinnor/zarqa (slanted right; tsinnor is vertical). U+0598 is **conflated**: in the 21
prose books the same codepoint is the zarqa stress-helper (fused onto zinor → ZARQA in
`ply_scanner`/`lexical_validation`); in the 3 poetic books it is the tsinnorit proper.
The prose side already *fuses* it; the poetic side wrongly *drops* it.

**Sources agree on its partner.**

- **Yeivin §372 ("Sinnorit")**: *"a secondary accent in words with conjunctive
  accents… marked on an open syllable immediately before the stress syllable… not used
  before a shewa or hatef shewa… generally used with mehuppak, and occurs rarely also
  with merka."* Names the combination **"mehuppak mesunnar"** (mehuppak with sinnorit).
- **Breuer, *Cantillation of Scripture* Ch. 9, §22 + fn. 9** (transliterated
  **tzinnorit**, tz not ts; combination **"mahpakh metzunar" / "merkha metzunar"**): fn.
  9 *doubts it is even a servant* — *"it only serves as a secondary accent before a
  mahpakh or merkha; thus it is possible to consider it part of a 'mahpakh metzunar' or
  'merkha metzunar.'"* §22: appears in the word of **any mahpakh**; with **merkha** only
  *before pasek + siluk or after small shalshelet*. Tzinnorit and its partner *"can only
  appear successively in the same [chanted] word, but cannot follow one another in two
  separate words."*

**Empirical confirmation (WLC, all 198 poetic tsinnorits).** Every one resolves to a
mahpakh/merkha partner in the **same chanted word** — none are anomalous:

| chanted word is… | partner | count |
|---|---|---|
| a **simple atom** | mahpakh (171) / merkha (12) | 183 |
| a **maqaf-compound with the maqaf graphically omitted** | mahpakh / merkha in the next sub-atom | 15 |

The 15 are Breuer §22's **omitted-hyphen** case (his own example **Ps 49:15**,
`וירדו בם` for `וירדו־בם`): *"customary to omit the hyphen which was supposed to appear
after the tzinnorit… the word is still considered joined by hyphen."* In WLC all 15 use
the omitted (space) maqaf, never a written `־`.

**Fix — fuse, don't drop.** Add scanner rules emitting one *metzunar* token (a
conjunctive), above the bare MAHAPAKH/MERKHA rules, exactly as the scanner already fuses
oleh→OLEH_WEYORED, geresh-muqdam→REVIA_MUGRASH, and (prose) zarqa-helper+zinor→ZARQA. Two
graphical shapes of the one phenomenon:

- **intra-atom:** `TSINNORIT + _TEXT + (MAHAPAKH | MERKHA)` → metzunar (183).
- **across an omitted maqaf, within one chanted word:** a tsinnorit-only atom (no main
  accent of its own) is the cue that it is the first sub-atom of a maqaf-compound; the
  following atom completes the chanted word and carries the mahpakh/merkha (15). The rule
  must reconstitute the chanted word across the omitted maqaf — the scanner's `_TEXT`
  class is atom-scoped (stops at space/maqaf), so this shape needs explicit handling, not
  just a wider `_TEXT`.

The result is **conjunctive**, absorbed by the permissive servus chain, so **no
disjunctive verdict changes** — this is faithfulness, not correctness. Mint a
`MAHAPAKH_METZUNAR` / `MERKHA_METZUNAR` token pair (or one parameterized token) in
`poetic_accent_names` and add to the `conj` servus list (see shalshelet below — same
mechanism).

**Terminology guards (carry into the docs):**

- Tsinnorit is **not prepositive.** It sits *relative to the stress* (the open syllable
  before it), never at the word edge. The prepositive accents are exactly
  `_PREPOSITIVE_MARKS = {yetiv, geresh-muqdam, dehi, telisha-gedola}`
  ([`uni_to_marks.py`](../py/accgram/uni_to_marks.py) L62–64). Avoid "preposed" for it
  (collides with "prepositive").
- **Chanted word** = a maqaf-compound *or* a simple (non-compound) atom. The scanner's
  *atom* (space/maqaf-delimited) is **not** a chanted word; the 15 compound cases are
  single chanted words with an omitted maqaf, not cross-word fusions.

## shalshelet qetannah (U+0593, no bar) → emit + add the 8th servus

Bare shalshelet in the 3 books is a **real conjunctive servus** (shalshelet qetannah);
shalshelet + the legarmeh-bar is the disjunctive shalshelet gedolah. Yeivin: *"In the
accentuation of the three books, the zigzag line is used to mark a conjunctive shalshelet,
and also a disjunctive one, which is distinguished from the conjunctive by the following
paseq."* (Yeivin's **"paseq"** here is the *broad / Unicode sense* — the bar mark U+05C0
itself; the bar is doing the **legarmeh**-style disjunctive-making job. "legarmeh" would
have been the precise word. The code already models this: one `am.PASEQ` codepoint,
disambiguated by context — `SHALSHELET + PASEQ` → gedolah, `(QADMA|MAHAPAKH) + PASEQ` →
legarmeh, bare `PASEQ` → swallowed separator.)

**Why it is dropped so early** — a shortcut, not a principle. Every *other* poetic
conjunctive is emitted as a servus token (MUNAX, MERKHA, MAHAPAKH, AZLA, GALGAL, ILLUY,
TARXA) and absorbed by the permissive `conj` chain. But the grammar's `conj` production
has exactly those **seven terminals** and **no shalshelet qetannah**
([`ply_grammar_poetic.py`](../py/accgram/ply_grammar_poetic.py) L92–93, 127–133), which
the grammar itself flags: *"the conjunctive shalshelet qetannah (#371) is a real poetic
servus but occurs in only eight verses…"* With no terminal to consume it, *emitting* a
token would fail to parse — so the scanner swallows it upstream. The scanner docstring
calls it a **"Known gap … swallowed, not emitted."**

**Fix — close the gap.** (1) Add `SHALSHELET_QETANNAH` to `poetic_accent_names`; (2) emit
it from the scanner (bare shalshelet, i.e. the existing swallow case minus the
gedolah/paseq match); (3) add it as the **8th `conj` terminal**. It is then absorbed
exactly like the other seven servi → **no verdict change**, 8 verses, full faithfulness.

## Design principle — the poetic mirror of prose `lexical_validation`

Plan A's lv25:20 work adds a prose layer that **surfaces a silently-swallowed malformed
mark** as an explicit oddball instead of letting the C lexer drop it. This plan is the
poetic counterpart of the same principle — *stop silently swallowing* — but the poetic
marks here are **legal**, so the faithful response is **representation** (fuse tsinnorit;
emit shalshelet qetannah), not error. The *illegal* poetic case (geresh) is the fail-fast
analog and lives in Plan A. Together: the poetic scanner should emit a token for every
real accent and fail fast on every impossible one — nothing vanishes.

## Verification

- `pytest` (add scanner/grammar unit tests for the new tokens, incl. Ps 49:15's omitted
  maqaf and an intra-atom mahpakh-metzunar; a shalshelet-qetannah verse).
- Regenerate the poetic corpus (`main_accgram.py run-ply-poetic`); confirm the diff is
  **only** added/renamed *conjunctive* leaves — **no** verse changes its disjunctive
  skeleton, gains/loses an `ERROR`, or flips well-formed↔ill-formed.
- Cross-check the disjunctive oracle (`xcheck_poetic`) is unchanged.

(Faithful-scan and drive-one-verse recipes: reuse Plan A's, swapping `ply_scanner_poetic`
/ `ply_grammar_poetic` and the poetic faithful pipeline `poetic_reconcile.reconcile_tokens`
→ `parse_tokens_accepting_repeats`; oddballs via `run_ply_poetic._has_error_leaf`.)

## Remaining work

1. **tsinnorit** — mint the metzunar token(s); scanner rules for both shapes (intra-atom;
   omitted-maqaf chanted word); add to `conj`. Verify all 198 fuse, none strand.
2. **shalshelet qetannah** — token + emit + 8th `conj` terminal. Verify the 8 verses.
3. Hand the tsinnorit/shalshelet "we now *represent* rather than drop" note to **Plan B**
   if the charities page wants to show them (they are not charities — they hide nothing —
   but they are part of the same "stop swallowing" story).
