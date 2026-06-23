# Plan C: faithful poetic scanning — stop swallowing real accents

**Status (2026-06-23):** **DONE** — all three pieces landed and verified. The poetic
scanner now **represents every real accent and fails fast on impossible ones; nothing
vanishes silently.** Companion to **Plan A**
(`doc/PLAN-A-same-letter-accent-pairs.md`) and **Plan B**
(`doc/PLAN-B-editorial-charities-page.md`); sibling of **Plan D**
(`doc/PLAN-D-faithful-same-letter-bangs.md`), which pursues the parallel "stop swallowing
*bangs*" goal and edits the same scanner region (land its bangs after this; re-run the
regen so each diff is attributable). Discovered while running down the ps124:4
geresh: the poetic scanner (`ply_scanner_poetic`) **silently swallowed real accents**
instead of representing them. This plan owns the two *legal* swallowed accents —
**tsinnorit** and **shalshelet qetannah** — whose fix is faithful *representation* (fuse
/ emit), with **no grammaticality verdict change**. The third swallowed accent, the
*illegal* poetic **geresh**, split: its same-letter **charity** (read revia+geresh as
revia mugrash) **landed in Plan A** (geresh+revia is a same-letter pair), but the
**fail-fast guard** for the catch-all came back **here** once Plan A's research showed the
catch-all is load-bearing (geresh is its only *accent* customer, now consumed) — so the
guard is a narrow stray-accent rule with zero live customers, best built alongside this
plan's "stop swallowing" conversions. See *Design principle* below.

**What landed (2026-06-23).** All in `py/accgram/`, verified by `pytest` (125 pass,
incl. new scanner + grammar tests) and a full poetic regen whose diff is **leaf-only**
(no disjunctive-skeleton change, no new ERROR/NO_PARSE):

- **tsinnorit → metsunnar** (198/198 fuse, 0 strand). New conjunctive tokens
  `MAHAPAKH_METSUNNAR` / `MERKHA_METSUNNAR` (spelling "metsunnar" = "me" + the
  vowel-permuted repo-standard "tsinnor"; leaves `mahapakh metsunnar` / `merkha
  metsunnar`), four scanner rules (intra-atom × {mahapakh, merkha}; omitted-maqaf ×
  {mahapakh, merkha}, gated by `_TSINNORIT_ATOM_TAIL` = a tsinnorit-only atom), both
  added to the grammar `conj` chain. Output: 179 mahapakh + 19 merkha metsunnar = 198.
- **shalshelet qetannah → emit + 8th `conj`** (8 verses). Token `SHALSHELET_QETANNAH`,
  a bare-shalshelet scanner rule below the gedolah rule (longest-match keeps gedolah
  when a paseq follows), added to `conj`. Output: 8 emitted, each absorbed into its
  existing disjunctive phrase (e.g. Ps 137:9 `illuy revia mugrash` → `shalshelet
  qetannah illuy revia mugrash`, the `revia_mugrash_phrase` unchanged).
- **stray-accent fail-fast guard** (0 live customers). A `[U+0591–U+05AE]` rule above
  the retained `.` catch-all emits `STRAY_ACCENT`, which the grammar has no terminal
  for → `NO_PARSE` (the poetic-native error surface, chosen over building a new
  lexical layer for zero customers). Corpus count: 0 (the lone ps124:4 geresh is
  consumed by Plan A's charity).
- **servant cross-check stayed byte-identical.** A metsunnar servant is its base
  mahapakh/merkha for servant-TYPE purposes (the tsinnorit is a secondary MAM's oracle
  does not catalog), so `servi_xcheck._l_servi_before` normalizes it via
  `_METSUNNAR_BASE`; `_mam_xcheck.txt` (the disjunctive oracle) and `_servi_xcheck.txt`
  are both unchanged.

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

**Independently confirmed against MAM (2026-06-23).** All **15/15** are marked **gray
maqaf** (מקף אפור, the *notionally-present-but-unwritten* hyphen) in **MAM-parsed-plus**
(`../MAM-parsed/plus/D{1,2,3}-*.json`, template `מ:מקף אפור`), each joining the
tsinnorit-bearing word to its mahapakh/merkha partner word — exactly the junction this
scanner reconstitutes. This is a **two-witness** agreement that the chanted word is
joined across the WLC space. (The distinction is invisible in **MAM-simple**, which
promotes gray maqaf to an ordinary maqaf — hence the check ran against MAM-parsed-plus;
2 of the 15, Ps 5:5 and 18:20, carry the gray maqaf *inside* a `נוסח` variant template,
and Ps 5:5's note even cites Breuer 11.54 on "mahapakh as a secondary accent" = the
metsunnar reading.) See memory [[mam-parsed-plus-gray-maqaf]].

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
emit shalshelet qetannah), not error. The *illegal* poetic case is the **plain geresh**:
its same-letter charity (read revia+geresh as revia mugrash) **already landed in Plan A**,
but the **fail-fast guard** for any *other* stray accent is **inherited by this plan**
(see below). Together: the poetic scanner should emit a token for every real accent and
fail fast on every impossible one — nothing vanishes.

**Inherited from Plan A — the catch-all fail-fast guard (with a corrected premise).**
Plan A's research established that the `.` catch-all is **load-bearing**: corpus-wide it
swallows every `X` placeholder (126,913×), space, maqaf, and `]N` note marker — geresh
(U+059C) is its only *accent* customer, exactly once (ps124:4), and that customer is now
consumed by the charity. So the fail-fast is **not** "flip the catch-all"; it is a narrow
new rule matching a *stray accent* (`[U+0591–U+05AE]`) placed **above** the catch-all,
which keeps swallowing structural junk. It has **zero live customers** today, so its job
is purely to guarantee no future stray accent vanishes silently. Build its representation
**here**, unified with the tsinnorit/shalshelet conversions, since poetic has no
lexical-error surface yet (no analog of prose `lexical_validation` / `_illegal_mark_tree`)
and this plan is the natural home for the whole "stop swallowing" discipline.

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

1. ~~**tsinnorit** — mint the metzunar token(s); scanner rules for both shapes; add to
   `conj`. Verify all 198 fuse, none strand.~~ **DONE** (`MAHAPAKH_METSUNNAR` /
   `MERKHA_METSUNNAR`; 198/198 fuse, 0 strand).
2. ~~**shalshelet qetannah** — token + emit + 8th `conj` terminal. Verify the 8
   verses.~~ **DONE** (`SHALSHELET_QETANNAH`; 8 emitted).
3. ~~**catch-all stray-accent fail-fast guard** — add a `[U+0591–U+05AE]` rule above the
   (retained) `.` catch-all and choose its lexical-error representation.~~ **DONE**
   (`STRAY_ACCENT` → NO_PARSE; 0 live customers; no output change).
4. **Open (Plan B):** hand the tsinnorit/shalshelet "we now *represent* rather than drop"
   note to **Plan B** if the charities page wants to show them (they are not charities —
   they hide nothing — but they are part of the same "stop swallowing" story).
