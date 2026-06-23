# Plan D: faithful same-letter bangs — stop swallowing the bang into a sequence

**Status (2026-06-23):** new, not started — the **next plan to execute** (its sibling
**Plan C** is **DONE/committed `d50e021`**; Plan B, the charities page, is best done last
so it documents the settled state). Spun off from **Plan A**
(`doc/PLAN-A-same-letter-accent-pairs.md`), whose taxonomy and `!` convention this plan
extends; sibling of **Plan C** (`doc/PLAN-C-poetic-swallowed-accents.md`). The two are the
matched halves of one "stop silently flattening the text" discipline:

- **Plan C — stop swallowing real *accents*.** A mark that is *dropped* (emitted as
  nothing) should instead be *represented* (fused / emitted). Defect: an accent vanishes.
- **Plan D — stop swallowing real *bangs*.** A same-letter *co-equal pair* that is
  *flattened into an ordered two-token sequence* should instead be *represented as one
  order-less `!` token*. Defect: nothing vanishes, but the **co-equal / no-natural-order
  relationship** does — it is silently replaced by an arbitrary order.

Both edit the same `ply_scanner_poetic` (and, for prose, `ply_scanner`) region and must
coordinate (see *Coordination* below).

## The defect, and how it was found

Found while regenerating the poetic corpus during Plan A's ps124:4 work: **Ps 56:10**'s
first word `אָ֥֨ז` carries **merkha (U+05A5) + qadma/azla (U+05A8) on one letter** (mark
body `X֥֨X` — two marks, no `X` between). The scanner emits them as a two-token sequence,
and the leaf order **flipped** `azla merkha` ↔ `merkha azla` between code versions. That
flip is the tell: the two marks are **co-equal with no natural order**, yet we present
them *as if* one preceded the other. Plan A itself declares within-letter order "not our
concern" (we are liberal about it) — which is precisely the situation the **bang** (`!`)
was invented for: *"an order-less, same-letter duress cluster."*

So the honest representation of `אָ֥֨ז` is one **`merkha!azla`** servus token, not a
reorderable `merkha azla` / `azla merkha` sequence.

## Why Plan A doesn't already do this — the "under duress" gate

Plan A's taxonomy has a `fuse` row — *"co-equal accents, no natural order, **under
duress** → one `a!b` token"* — but gates it to the **under-duress** case: a pair the
*grammar is forced to decide*, like prose **ek20:31** (`mahapakh!azla`, where leaving a
bare sequence would misparse). Poetic conjunctives are **never under duress**: the poetic
grammar's `conj` chain absorbs any run of servi regardless of order or count, so the
*grammaticality verdict* is identical whether we emit `merkha azla`, `azla merkha`, or
`merkha!azla`. Plan A therefore (correctly, on the *verdict* axis) files ps56:10 and its
kin as "non-issues" and routes them to `sequence`.

**Plan D's thesis:** faithfulness is a *different axis* from the verdict. On the
faithfulness axis, the bang is the right representation for *every* same-letter co-equal
pair, duress or not. Plan D **drops the "under duress" gate** for same-letter co-equal
pairs, promoting the bang from a grammar-forced device to a representation-faithful one.

## Scope — which pairs become bangs

A bang is for **two co-equal same-letter accents** — same role, no inherent order. It is
**not** for:

- **prepositive / postpositive neighbors**, which *do* have a defined position (those stay
  a `sequence`; Plan A's within-letter order-normalization still applies to them);
- **idioms** (revia-mugrash, oleh-we-yored, methiga-zaqef — established compound names);
- **drop** pairs (telg + geresh-family);
- **stress-helper + main** fusions, already fused (zarqa-helper+zinor, doubled
  pashta/telisha, tsinnorit→metzunar in Plan C) — those are a helper *onto* its main, a
  different relationship from two co-equals.

The seed cases (from Plan A's enumeration; **to be confirmed and completed by a sweep**):

- **merkha + qadma** — ps56:10 (poetic), and any others the sweep finds;
- **a secondary merkha / secondary mahapakh** sharing a letter with another co-equal
  conjunctive (Plan A lists these as "never constrained" — candidates, pending the sweep);
- (deḥi + munaḥ is **not** a candidate: deḥi is disjunctive, munaḥ conjunctive — not
  co-equal; it is a servus-absorbed sequence and stays a sequence.)

**Prose vs poetic:** ps56:10 is poetic, but the same faithfulness argument applies in
prose. The sweep must cover both genres; the only *already-correct* prose case is
ek20:31's `mahapakh!azla` (already a bang). Anything else currently emitted as a
same-letter co-equal *sequence* in either genre is in scope.

## Method (reuse Plan A's faithful-scan recipe)

1. **Sweep** the raw `-kq-u` words (Plan A's *Faithful scan recipe*) for every same-letter
   cluster of exactly two accents, in both genres. Classify each by the taxonomy: drop the
   idiom / drop / prepositive-neighbor / helper-fusion cases; what remains — **two co-equal
   accents** — is Plan D's worklist. `log` the full list (no silent caps).
2. **Decide the canonical bang spelling.** A bang is order-less, but the *token string*
   must be deterministic. Options: storage order, or a fixed accent-precedence order
   (e.g. alphabetical by accent name, as `mahapakh!azla` already is). Pick one rule and
   apply it uniformly so the leaf no longer flips. (Open question below.)
3. **Add scanner fusion rules.** In `ply_scanner_poetic` (poetic) / `ply_scanner` (prose),
   match the two co-equal marks **adjacent** (no `X` between → same letter), in storage
   order, emitting one `a!b` token — above the single-mark rules, exactly as ek20:31's
   `mahapakh!azla` and the helper-fusions are done. Add only **attested** pairs (memory
   `parse-rate-not-a-goal`); do not invent a general "fuse any two adjacent servi" rule
   beyond what the sweep attests.
4. **Make the grammar accept the fused token.** Poetic: add each `a!b` servus to the
   permissive `conj` terminal list (same mechanism as Plan C's shalshelet qetannah / the
   metzunar tokens) so the disjunctive skeleton is untouched. Prose: only if the sweep
   finds a prose case beyond ek20:31; add the attested rule.

## Coordination with Plan A and Plan C

- **Plan A** is updated to record that the "under duress" gate is *lifted for same-letter
  co-equal pairs by Plan D*; the `fuse` row's examples grow beyond ek20:31. Plan A keeps
  the taxonomy and the `!` convention; Plan D is its faithfulness-driven extension.
- **Plan C** edits the same poetic-scanner swallow/fusion region (tsinnorit→metzunar,
  shalshelet qetannah, the stray-accent fail-fast). Plan D adds *more* fusion rules there.
  **Plan C is DONE and committed (`d50e021`, 2026-06-23)** — its representation work
  landed first, as planned (token spelling settled on `metsunnar`; fused tokens
  `MAHAPAKH_METSUNNAR` / `MERKHA_METSUNNAR` and `SHALSHELET_QETANNAH` join the `conj`
  chain in `ply_grammar_poetic`). Plan D's bangs now build on that committed region; add
  the bang rules above the bare-servus rules (as C's metsunnar rules are) and re-run the
  full poetic regen so D's diff is attributable on top of C's leaf-only baseline.
- The shared token-minting convention: helper→main fusions and idioms keep their named
  tokens; **bangs** use the literal `a!b` spelling (memory `fused-impositive-cluster-token`).

## Verification

- `pytest` (scanner unit tests: each attested same-letter co-equal pair fuses to its
  `a!b` token; a cross-letter pair of the same two accents does **not** fuse).
- Regenerate both corpora (`main_accgram.py run-ply-goerwitz`, `run-ply-poetic`); confirm
  the diff is **only** targeted `a b` → `a!b` leaf changes (sequence → bang) on the swept
  words — **no** verse changes its disjunctive skeleton, gains/loses an `ERROR`, or flips
  well-formed↔ill-formed. ps56:10's `merkha azla` becomes `merkha!azla` (or the chosen
  canonical spelling), and never flips again.
- Cross-check the disjunctive oracle (`xcheck_poetic`) is unchanged.

## Open questions

- **Canonical bang spelling / ordering.** `merkha!azla` vs `azla!merkha`: storage order,
  or a fixed accent precedence? Whatever the rule, it must be deterministic so the leaf
  stops flipping. (ek20:31 is `mahapakh!azla` — is that storage order or a precedence we
  should generalize?)
- **Exact membership of "co-equal."** Both-conjunctive is clear; are there same-letter
  two-*disjunctive* co-equal pairs (e.g. doubled tsinnor, Ps 17:14 — currently
  "collapsed")? Decide whether collapse vs bang is right for those.
- **Does Plan B want to show bangs?** Like Plan C's tsinnorit/shalshelet note: bangs are
  **not charities** (they hide nothing — they *stop* hiding the co-equality), but they are
  part of the same "faithful representation" story; the charities page may want a sibling
  section.

## Remaining work

1. Run the same-letter two-accent sweep (both genres); produce the attested co-equal-pair
   worklist.
2. Decide the canonical bang spelling.
3. Add scanner fusion rules + grammar terminals for each attested pair.
4. Verify (pytest + dual corpus regen + xcheck); confirm verdict-neutral, leaf-only diff.
5. Update Plan A's `fuse`-row examples; hand the "we now represent bangs" note to Plan B.
