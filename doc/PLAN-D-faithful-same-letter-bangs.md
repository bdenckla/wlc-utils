# Plan D: faithful same-letter bangs — stop swallowing the bang into a sequence

**Status (2026-06-23):** **DONE** — the sweep proved the worklist is a *single* poetic
pair (ps56:10's `merkha+qadma`). It is now faithfully **represented** as one order-less
**`merkha!azla`** bang but, after review (see *Revision* below), **not blessed
grammatically**: a same-letter accent pair outside a small **whitelist** is treated as a
**lexical anomaly**, so the bang has no `conj` terminal and ps56:10 surfaces as a **NO_PARSE
oddball** (the poetic lexical-error surface) annotated with manuscript evidence + the two
images, rather than a silently-clean parse. Verified: `pytest` (128 pass), poetic regen
diff is **one line** (`merkha azla` clean tree → `NO_PARSE` at ps56:10; nothing else
changes), both cross-checks (`_mam_xcheck.txt`, `_servi_xcheck.txt`) regenerate
**byte-identical**, and the regenerated `poetic.html` shows the ps56:10 oddball with its
summary, three comment paragraphs, and the LC + Da'at-Miqra images. Sibling **Plan C** is
**DONE/committed `d50e021`**; Plan B, the charities page, is best done last so it
documents the settled state. Spun off from **Plan A**
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
4. ~~**Make the grammar accept the fused token.**~~ **SUPERSEDED by the Revision below.**
   The original intent was to add each `a!b` servus to the permissive `conj` list. On
   review this was rejected: a same-letter co-occurrence is *not* automatically licit, so
   `MERKHA_AZLA` is left out of the grammar (→ NO_PARSE lexical anomaly) rather than
   blessed. See *Revision*.

## Coordination with Plan A and Plan C

- **Plan A** is updated (note: the "lift the gate" framing was **superseded** — see
  *Revision*). What actually landed: `merkha!azla` is added to Plan A's **`unlexical`**
  row (not `fuse`), and the `!` bang is documented as a *representation* orthogonal to the
  verdict (it labels both the licit `mahapakh!azla` and the unlexical
  `mahapakh!tipexa` / `merkha!azla`). Plan A keeps the taxonomy and the `!` convention.
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

## Open questions — RESOLVED

- **Canonical bang spelling / ordering — RESOLVED: lower-codepoint mark first, `!`-joined.**
  The sweep attests `merkha+qadma` in exactly one storage order (merkha U+05A5 *then*
  qadma U+05A8), which already coincides with both codepoint order and the prose
  `mahapakh!azla` convention (mahapakh U+05A4 < qadma U+05A8) — so all three rules agree
  and the leaf is `merkha!azla`. Per memory `parse-rate-not-a-goal`, only the **attested**
  storage-order rule is added (`am.MERKHA + am.QADMA`); a reverse `azla!merkha` order
  never occurs, so no second rule is invented.
- **Exact membership of "co-equal" — RESOLVED empirically: no same-letter two-*disjunctive*
  pair exists.** The sweep's only doubled-divider candidate, Ps 17:14's tsinnor+tsinnor,
  is **cross-letter** (two consecutive TSINNOR tokens, handled by
  `collapse_repeated_sinnor`), not same-letter — so the collapse-vs-bang question never
  arises on one letter. Every same-letter two-accent cluster in the corpus is one of:
  revia-mugrash (idiom), munah+dehi (not co-equal — disjunctive+conjunctive), telg
  companions (drop), the lv25:20 illegal below-pair (unlexical), the ek20:31 /ps56:10
  co-equal conjunctive bangs, or the ps124:4 geresh charity.
- **Does Plan B want to show bangs? — handed to Plan B (still open there).** Bangs are
  **not charities** (they hide nothing — they *stop* hiding the co-equality), but they are
  part of the same "faithful representation" story; the charities page may want a sibling
  section noting both `mahapakh!azla` (prose) and `merkha!azla` (poetic).

## The single worklist case (full sweep result)

The same-letter two-accent sweep (both genres, raw `-kq-u`, decalogues/Gn35:22 excluded)
found these clusters; only one is an in-scope Plan D bang:

| pair (storage order) | count / genre | classification | action |
|---|---|---|---|
| geresh-muqdam + revia | 241 poetic | idiom (revia mugrash); geresh-muqdam prepositive | drop (already fused) |
| munah + dehi | 2 poetic | not co-equal (conj + disjunctive); dehi prepositive | sequence (unchanged) |
| telg + gershayim / + geresh-muqdam | 3 prose | drop-class telg companion | drop (uni_to_marks) |
| mahapakh + qadma | 1 prose (ek20:31) | co-equal under duress | **already `mahapakh!azla`** |
| mahapakh + tipeha | 1 prose (lv25:20) | unlexical (two below-accents) | Plan A `illegal_below_pairs` |
| revia + geresh | 1 poetic (ps124:4) | same-letter geresh charity | Plan A `REVIA+GERESH→revia mugrash` |
| **merkha + qadma** | **1 poetic (ps56:10)** | **same-letter pair, not whitelisted → unlexical** | **→ `merkha!azla` bang, flagged NO_PARSE (this plan)** |

No single letter carries more than two accents (re-confirms Plan A's corpus-wide claim).

## Revision — the bang is a *lexical anomaly*, not a blessed servus

The first cut (above) added `MERKHA_AZLA` to the permissive `conj` chain, leaving ps56:10
a clean parse. On review the maintainer rejected that: **"a verse grammatical with x then
y does not make x stacked on y grammatical"** — the same point the codebase already makes
for lv25:20's `mahapakh!tipexa` (a fine *sequence*, an impossible *stack*). Putting
`MERKHA_AZLA` in `conj` silently encoded a grammaticality verdict that was never
established. So Plan D's *representation* (the bang) is kept, but its *verdict* is flipped
to **unlexical**: a same-letter accent pair outside a small **whitelist** is illicit.

**Manuscript rationale (the maintainer's reading).** Across witnesses the two marks split
cleanly one-each: **MAM carries azla alone** and, according to Breuer, so does the
**Aleppo Codex**, while **Sassoon 1053 carries merkha alone**. L's carrying of *both*, on one letter,
looks less like a genuine two-accent reading than a **conflation** preserving both
single-accent traditions (recording the options, not choosing). The upper mark (the
qadma/azla) is in any case oddly placed and shaped — it could be a misshapen part of the
alef, much as the Job 31:15 geresh-muqdam — so even the azla half is uncertain. (Whether
prose ek20:31's `mahapakh!azla` should be reclassified the same way is deferred with the
conjunctive-grammaticality work below.)

**The "how legal" measure (`bang_legality`).** A separate diagnostic measures *how legal*
a bang `a x!y b` is by which of its four interpretations parse: `a x b` (x only), `a y b`
(y only), `a x y b`, `a y x b`. ps56:10 scores **4/4** — every reading is grammatical — so
it is a *maximally-legal anomaly*: flagged, but harmless however resolved. **Caveat the
maintainer flagged:** the poetic `conj` chain is fully permissive, so for an all-
conjunctive bang the measure is near-vacuous (it tends to 4/4 regardless). It only gains
teeth once **conjunctive grammaticality is strengthened** — a noted, deferred direction
(remaining levers: secondary/ga`ya positional rules; per-witness legality). The
**same-letter whitelist rule is now implemented** as a general scanner guard (below), so
this anomaly falls out of a principle rather than a special-cased pair. The module is in
`py/accgram/bang_legality.py`, unwired pending the grammaticality work.

## What landed (2026-06-23)

- **scanner — a same-letter WHITELIST guard.** One rule in
  `ply_scanner_poetic._POETIC_GG_RULES` (`_BANG_GUARD`) matches **any two adjacent accents**
  (`_ANY_ACCENT`×2 — no X between → same letter) **except a whitelisted pair**, and fuses
  them into one order-less `a!b` bang, the per-pair type/leaf computed by `_bang_pair_token`
  (merkha+qadma → `MERKHA_AZLA` / `merkha!azla`, exactly the prior output). It beats the
  bare single-mark rules by longest-match. The legitimate same-letter pairs are either
  **fused upstream** (revia+geresh-muqdam / revia+geresh → revia mugrash; ole+merkha →
  oleh-we-yored) and so never reach it, or are the **deḥi+munaḥ** sequence, spared by
  `_WHITELISTED_ADJACENT_PAIRS` (a negative lookahead). Everything else → bang. This
  whitelist supersedes the earlier "two impositive accents" blacklist, which leaned on
  contested positional classifications (tsinnorit, ole) of marks that — per the corpus —
  never share a letter anyway; the whitelist is the honest rule and is *stricter* (it also
  flags a non-impositive-involving stack that isn't whitelisted). Corpus-wide it fires
  only at ps56:10; the generality guards any other / future same-letter stack.
- **grammar** the dynamic bang type (e.g. `MERKHA_AZLA`) is deliberately **NOT** a grammar
  token / not in `p_conj`: with no terminal the parser dead-ends → **NO_PARSE** (the
  poetic lexical-error surface, as `STRAY_ACCENT`), so ps56:10 is a flagged oddball.
  `pan.MERKHA_AZLA` is kept as the named canonical instance; `pan.BANG_PAIR` is the
  scanner-internal sentinel the rule emits before `_bang_pair_token` resolves it.
- **oddball annotation** `poetic_ob_notes["ps 56:10"]` — `st-summary` + three `comment`
  paragraphs (the manuscript/conflation/paleography argument) + the two images
  (`img` = `LC-376B-col-2-line-5-Ps-56v10.png`, `Da-at Miqra img` =
  `Da-at-Miqra-Ps-56v10.png`). `poetic_oddballs._render_oddball_section` now also calls
  `rtmsr_media.render_image_paragraphs` (poetic oddballs previously rendered comments but
  not images).
- **how-legal diagnostic** `bang_legality.py` (the four-interpretation measure; ps56:10 →
  4/4, near-vacuous until conj grammaticality is strengthened).
- **servant cross-check** `servi_xcheck._METSUNNAR_BASE` generalized to
  `_FUSED_SERVANT_BASE` with `MERKHA_AZLA → AZLA`; zero live customers (the bang is not
  adjacent to any target), so `_servi_xcheck.txt` stays byte-identical.
- **tests** `test_same_letter_merkha_azla_fuses_to_bang`,
  `test_cross_letter_merkha_then_azla_stays_a_sequence`,
  `test_non_whitelisted_pair_fuses_to_bang` (a *different* pair, munah+merkha, proving
  generality), `test_whitelisted_pairs_not_flagged` (deḥi+munaḥ / tsinnorit+mahapakh
  do **not** fire the guard) (`test_ply_scanner_poetic.py`);
  `test_merkha_azla_bang_is_unparseable` (`test_ply_poetic_grammar.py`). 130 pass.

## Remaining work

1. ~~Run the same-letter two-accent sweep (both genres); produce the worklist.~~ **DONE**
   (table above; the single in-scope pair is ps56:10).
2. ~~Decide the canonical bang spelling.~~ **DONE** (`merkha!azla`, lower-codepoint-first).
3. ~~Add scanner fusion rule + grammar terminal.~~ **DONE (revised twice)** — the scanner
   rule was first the attested merkha+qadma, then **generalized to a same-letter
   whitelist guard** (`_BANG_GUARD`: any two adjacent accents except a whitelisted pair);
   the grammar terminal was **removed** so the bang is a lexical anomaly (NO_PARSE), not a
   blessed servus.
4. ~~Verify.~~ **DONE** (130 pass; ps56:10 → NO_PARSE; the generalization is **output-
   neutral** — corpus and both cross-checks byte-identical; `poetic.html` shows the
   oddball + images).
5. ~~Update Plan A's taxonomy~~ **DONE** (`merkha!azla` moved to the `unlexical` row; the
   `!` bang documented as a representation orthogonal to the verdict). Hand the bangs note
   to **Plan B** (still open — Plan B).
6. ~~Make the structural same-letter rule.~~ **DONE** — the general whitelist scanner
   guard (`_BANG_GUARD`): only whitelisted pairs may share a letter; everything else is a
   bang. (Supersedes the interim "two impositive accents" blacklist.)
7. ~~Confirm the whitelist membership.~~ **DONE / complete** — the body scan is
   exhaustive: the *only* adjacent-accent pairs anywhere in the poetic corpus are
   geresh-muqdam+revia, deḥi+munaḥ, merkha+qadma, and revia+geresh; every one except
   merkha+qadma is whitelisted or fused, so no legitimate same-letter pair is omitted.
8. **Deferred (noted, not acted):** strengthen *conjunctive* grammaticality so the
   `bang_legality` measure stops being near-vacuous (levers: secondary/ga`ya positional
   rules; per-witness legality); revisit prose ek20:31 under the same-letter whitelist;
   wire `bang_legality` once it has teeth.
