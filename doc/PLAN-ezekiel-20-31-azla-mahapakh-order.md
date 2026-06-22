# Handoff: Ezekiel 20:31 — azla/mahapakh accent-order divergence after Phase 2

**Status:** RESOLVED 2026-06-22 (see "Resolution" below). Isolated to a single
verse. This document is mostly *context* — it records what was discovered and why.

## Resolution (2026-06-22)

Chosen approach: a **fourth option** beyond the three below — treat the two
impositive accents sharing one letter as a **single unitary token**, not as a
servus *sequence*. Two impositives on one letter (here an above-accent, qadma/azla,
and a below-accent, mahapakh) have no natural order; judging their "order" is a
category error for a grammar whose job is sequencing. So we fuse them into one
token. The scanner already collapses mark-clusters into one token elsewhere, but
none is a true analog and they are not even like each other: helper+main fusions
(`pashta`/`zarqa`/`telisha-qetana`; telisha-gedola is *main+helper*) merely re-mark
**one** accent with a stress-helper — droppable for grammar-checking (one could drop
all helpers, or all helped mains) — whereas `methiga-zaqef` (qadma+zaqef) is a
genuine **cross-letter** sequence of two distinct impositive accents (more analogous
to mayela-silluq / mayela-atnax). The same-letter `mahapakh+azla` cluster is its own
category: two distinct impositive accents on **one** letter, with no natural order.
The fused leaf is `mahapakh!azla` — `!` (not `_`) marks an extraordinary,
orderless, sometimes-illegal cluster, rather than one accent with a space in its
name (which `_` would imply). For more on this extraordinary accentuation, consult
an edition of MAM showing its doc-notes, e.g.
<https://bdenckla.github.io/MAM-with-doc/C3-Ezekiel.html#c20v31>.

The mechanism falls out of the mark string: same-letter ⇔ the two accent codepoints
are **adjacent with no `X` between**, so the scanner rule `MAHAPAKH QADMA` (storage
order, U+05A4<U+05A8) fires *only* for the same-letter cluster. The genuine
cross-letter/word `qadma…mehuppakh` servus still tokenizes as `AZLA` then `MAHAPAKH`
and uses the untouched `AZLA MAHAPAKH PASHTA` rules — so the fused token exists
exactly when there is no sequence, and the two-token sequence survives exactly when
there is one.

The cross-letter `TELISHAQETANNA AZLA MAHAPAKH PASHTA` rule is **kept**: it is
heavily live, matching 253 true cross-letter telisha-qetanna+qadma+mehuppakh+pashta
sequences across the corpus (gn14:16 … ne12:31), with `AZLA MAHAPAKH` adjacency
(the ordinary cross-letter qadma→mehuppakh servus) occurring 1828 times overall.
This is **not** to be confused with the one-time-only case of azla and mahapakh on
the *same* letter in Ezekiel 20:31 — that verse was never a true sequence; under M-C
it merely fell through this rule by coincidence of serialization order, and now
routes to the fused `MAHAPAKHAZLA` rule instead.

Changes: `ply_scanner.py` (fused `_GG_RULES` entry + `MAHAPAKHAZLA` leaf),
`ply_grammar.py` (token + `pashta_phrase : TELISHAQETANNA MAHAPAKHAZLA PASHTA`; the
MUNAX-prefixed siblings of the AZLA MAHAPAKH family deliberately not mirrored — no
attested occurrence). Ezekiel 20:31 now parses to `telishaqetanna mahapakh!azla
pashta`; this is **not** byte-identical to the stale committed M-C parse (one fused
leaf, not two), which is the intended, more-honest representation.

Verification: 111/111 pytest; full prose-corpus regeneration moves *only* ek 20:31
(ERROR → fused parse); a whole-index scan for same-letter mahapakh+qadma found just
`ex20:10`, `dt5:15` (both decalogue, excluded from the grammar-checked corpus) and
`ek20:31`; no poetic occurrence.

**Deferred siblings (separate pass):** apply the same unitary-token philosophy to
the other "two accents on one letter" clusters — `mahapakh!tipexa` (Lev 25:20, both
below-accents, *illegal*) and the telisha-gedola + geresh / gershayim above-prepositive
pairs. Note the latter are *currently handled by the opposite strategy* — dropping
the secondary in `uni_to_marks` (gn 5:29 / Zeph 2:15, lines ~119-124) — so unifying
on fusion means revisiting those drops.

## Original handoff (context, pre-resolution)


## One-line summary

Under the current (Phase-2, Unicode-mark) scanner, **Ezekiel 20:31 parses to an
`ERROR` oddball** where it previously parsed cleanly. The cause is that a single
word carrying both *mahapakh* and *qadma/azla* is now tokenized in the order
`MAHAPAKH AZLA`, but the grammar only recognizes the servus chain in the order
`AZLA MAHAPAKH` (rule `pashta_phrase : TELISHAQETANNA AZLA MAHAPAKH PASHTA`). With
no rule for the swapped order, the parser falls into `error PASHTA` recovery and
emits an `ERROR` leaf.

## How this surfaced

While fixing the unrelated pashta-leaf bug (issue #5, commit `0f52948`), the full
prose corpus was regenerated. That regeneration changed exactly **three** output
files: two were the intended leaf fix (2Kings 13:16, Exodus 10:13); the third,
`out/accgram/ply/wlc_422_ps_ek_ag.txt` at Ezekiel 20:31, was **not** caused by the
pashta change — it reproduces even with the grammar edit reverted. It was kept out
of commit `0f52948` (the `ek` file was `git checkout`-reverted before committing),
so the committed `ek` output still shows the old clean parse.

### Why the committed output didn't already show it (staleness)

- `out/accgram/ply/wlc_422_ps_ek_ag.txt` was last regenerated in `ea97ece`
  (2026-06-19 13:35) — accent-translit standardization (#13).
- The scanner was then rewritten in `7b27ad0` (2026-06-19 22:13) — "phase 2 of
  ditching M-C input" (issue #9, the Unicode-mark alphabet).
- **`7b27ad0` did not regenerate the `ek` output.** So the committed `ek` predates
  the Phase-2 scanner and still reflects the pre-Phase-2 (M-C) tokenization.

Across all 39 prose books, Ezekiel 20:31 is the **only** verse whose current-code
output diverges from the committed outputs (besides the two intended pashta-leaf
verses). So Phase-2 is byte-identical to the committed corpus *except this one
verse* — i.e. this is an isolated, single-verse divergence, not a broad regression.

## Root cause (mechanism)

Word 6 of Ezekiel 20:31 (0-indexed over the verse's words) carries **two
non-prepositive conjunctive accents on one word**: mahapakh and qadma/azla. Their
**Unicode storage order is mahapakh-then-qadma** (U+05A4 before U+05A8).

The Phase-2 transcoder `accgram/uni_to_marks.py` (`word_to_marks`) emits
non-prepositive accents in **codepoint/storage order**. It only relocates the four
marks in `_PREPOSITIVE_MARKS` (yetiv, geresh-muqdam, dehi, telisha-gedola) to the
front of the word; mahapakh and qadma are *not* in that set, so they pass through in
storage order → `MAHAPAKH` then `AZLA`.

The pre-Phase-2 **M-C** pipeline encoded this word's accents in the order **azla
(code 63) then mahapakh (code 70)** — the order the grammar rule expects.

So the divergence is an **accent-ordering gap in the transcoder**: for this
mahapakh+qadma cluster, Unicode storage order ≠ M-C order, and the transcoder's
prepositive-relocation does not cover it.

### The token streams

Current (Phase-2) scanner, Ezekiel 20:31:

```
TILDE MUNAX PAZER TELISHAQETANNA AZLA GERESH TELISHAQETANNA MAHAPAKH AZLA PASHTA
ZAQEF TEVIR MERKHA TIPEXA MUNAX ATNAX REVIA PASHTA MUNAX ZAQEF TIPEXA SILLUQ SOFPASUQ
```

The failing region is `TELISHAQETANNA MAHAPAKH AZLA PASHTA`. The grammar has
`TELISHAQETANNA AZLA MAHAPAKH PASHTA` (azla before mahapakh) but no rule for the
`MAHAPAKH AZLA` order, so the parse errors at this point.

### Word → accent map (Ezekiel 20:31)

```
 0  munax
 1  pazer
 2  telisha-q
 3  azla
 4  geresh
 5  telisha-q
 6  mahapakh+azla   <-- the offending word: storage order mahapakh, then qadma/azla
 8  pashta
14  munax
18  pashta
19  munax
```

### Trees, before vs after

Committed (old M-C scanner), the relevant phrase parses cleanly:

```
          5 pashta_phrase
            telishaqetanna azla mahapakh pashta
```

Current (Phase-2 scanner), same position:

```
          5 pashta_phrase
            ERROR
```

(The surrounding `pashta_clause` / `geresh_phrase: telishaqetanna azla geresh` /
`pazer_phrase` structure is otherwise unchanged.)

## Relevant code

- **`py/accgram/uni_to_marks.py`** — `word_to_marks`, the accent-ordering logic.
  `_PREPOSITIVE_MARKS` (≈ lines 61-63) is the only reordering; non-prepositive
  accents (incl. mahapakh, qadma) are appended in storage order (`other_marks`).
  The module docstring (≈ lines 21-23, 55-60) explains the prepositive relocation
  and its goal of restoring "M-C order so the scanner reads the accents in M-C
  order" — this case is the exception that escapes it.
- **`py/accgram/ply_grammar.py`** — the `pashta_phrase` rules, including
  `TELISHAQETANNA AZLA MAHAPAKH PASHTA` (`p_pashta_phrase_telq_azla_mahapakh`) and
  the `error PASHTA` recovery (`p_pashta_phrase_error`) that produces the `ERROR`
  leaf.
- **`py/accgram/accent_marks.py`** — mark codepoints. Note `QADMA = U+05A8`
  (this is "azla"); `MAHAPAKH = U+05A4`.

## The open question (candidate resolutions — not yet chosen)

What is the *correct* order for mahapakh + qadma/azla on a single word in a servus
chain before pashta, and therefore which layer should change?

1. **Transcoder normalization.** If azla-before-mahapakh is the canonical reading
   order (the grammar and the clean pre-Phase-2 parse both assume it), extend
   `uni_to_marks` to emit this cluster in that order — i.e. treat it like the
   prepositive relocation, restoring M-C order for the mahapakh/qadma case. This
   keeps the grammar untouched and restores the clean parse.
2. **Grammar rule.** If the Unicode storage order (mahapakh-then-azla) is the
   "true" order, add a `TELISHAQETANNA MAHAPAKH AZLA PASHTA` rule (and any siblings)
   so the new order parses. Riskier: it asserts a new legal servus order.
3. **Accept as oddball.** If the sequence is genuinely anomalous, the `ERROR` may be
   acceptable — but note it parsed cleanly for years under M-C, and it is real WLC
   text, so this seems least likely.

Resolving this is a scholarly/grammar call (consult Yeivin on the qadma+mehuppach
servus order), not a pure code call. Likely (1), but verify the on-the-word order
question first.

## Scope / done-when

- Only Ezekiel 20:31 is affected in the whole prose corpus. Once the order question
  is decided and implemented, regenerate the prose corpus and confirm the **only**
  resulting diff is `ek` at 20:31 returning to a clean parse (no other book moves).
- Consider whether the same mahapakh+qadma-on-one-word cluster occurs elsewhere
  without changing a parse (it would not have shown up in the corpus diff, but could
  still be mis-ordered silently). A targeted scan of the kq-u source for words
  bearing both U+05A4 and U+05A8 would find them.

## Reconciliation note

The memory note records Phase-1+2 parity as "byte-identical except 1 intended
`uxlc_grammar_test` improvement." Ezekiel 20:31 is a **second** Phase-2 divergence
that the committed goerwitz outputs did not capture (because `ek` wasn't
regenerated after `7b27ad0`). Worth reconciling whether the Phase-2 parity check
covered the goerwitz `*_ag.txt` outputs at all, or only `uxlc_grammar_test`.

## Reproduce (fresh session)

```bash
# from repo root; regenerate just Ezekiel to a scratch dir
cd py && ../.venv/Scripts/python.exe main_accgram.py run-ply-goerwitz \
    --book ek --out-dir /tmp/ek_check
# inspect Ezekiel 20:31 (ERROR leaf under the inner pashta_phrase)
#   /tmp/ek_check/wlc_422_ps_ek_ag.txt  vs  out/accgram/ply/wlc_422_ps_ek_ag.txt

# dump the token stream + word/accent map (PYTHONIOENCODING=utf-8 to print Hebrew):
#   scan_book(uni_to_marks.build_book_texts(...)['ek'], 'ek'), find ref ...20:31
```

## Related

- Issue #5 (closed): item 3 ("the `[0-9][0-9]` swallow") is unrelated to this; it
  was about the catch-all, now moot post-Phase-2.
- Issue #9 / commit `7b27ad0`: the Phase-2 Unicode-mark port that introduced the
  divergence.
- No GitHub issue is open for this yet — opening one (or folding it into the #9
  Phase-2 follow-up) is a reasonable first step.
