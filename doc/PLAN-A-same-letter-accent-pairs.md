# Plan A: same-letter accent pairs — unified treatment + two open verses

**Status (2026-06-23):** **DONE** — the design converged on a single taxonomy that makes
the formerly ad-hoc handling principled, and both live code changes have landed:
**lv25:20** (prose lexical error) and **ps124:4** (poetic geresh charity). The one piece
*not* done here is the poetic catch-all **fail-fast guard**, deliberately **deferred to
Plan C** (see the ps124:4 section): research showed the catch-all is load-bearing (it
swallows every `X`/space/maqaf/note marker — geresh is its only *accent* customer), so a
fail-fast must be a narrow stray-accent rule, and Plan C is already rebuilding that exact
swallow region. The charity alone makes ps124:4 principled. Companions: **Plan B**
(`doc/PLAN-B-editorial-charities-page.md`) — the generated HTML page that documents these
"charities"; **Plan C** (`doc/PLAN-C-poetic-swallowed-accents.md`) — the poetic
scanner's silent-swallowing defect (tsinnorit, shalshelet qetannah), discovered while
running down the ps124:4 geresh; and **Plan D**
(`doc/PLAN-D-faithful-same-letter-bangs.md`) — the spin-off "no swallowed *bangs*" goal
(represent same-letter co-equal pairs as one `!` token rather than a reorderable
sequence), prompted by ps56:10. Resolved precedents: ek20:31 (mahapakh+azla, **fused**);
the telisha-gedola + geresh-family family (5 words, **drop-to-telg**); poetic
revia-mugrash (established single token). See also the durable design note in memory
`fused-impositive-cluster-token`, and the worked example
`doc/PLAN-ezekiel-20-31-azla-mahapakh-order.md` (slated for deletion).

## The unifying question

How should the accgram checkers treat **two cantillation accents** that land close
together (same letter, or same word)? The answer is keyed by *what the two marks are
to each other*, not by a per-pair enumeration. Five readings:

| reading | when | mechanism | examples |
|---|---|---|---|
| **sequence** *(default)* | two ordinary accents adjacent; one prepositive/postpositive, or just neighbors | tokenize each in source order; **normalize order only within a letter** (never across letters) | munaḥ+deḥi (poetic); most same-letter pairs |
| **fuse (`!`)** | co-equal accents, **no natural order**, **and a licit combination** | one `a!b` token, accepted | `mahapakh!azla` (ek20:31, prose) |
| **idiom** | an established compound accent | one named token | revia-mugrash, oleh-we-yored, methiga-zaqef |
| **drop** | a redundant companion of a prepositive/postpositive | drop the secondary | telg + geresh/gershayim → telg |
| **unlexical** | a same-letter combination that is positionally/grammatically **illicit** (even when each accent alone is fine) — i.e. a same-letter accent pair **not on the whitelist** (revia+geresh-muqdam, deḥi+munaḥ, oleh+yored) | flagged, not parsed: prose `lexical_validation` (skip grammar); poetic = no `conj` terminal → NO_PARSE oddball | `mahapakh!tipexa` (lv25:20, two below-accents); `merkha!azla` (ps56:10) |

The orthographic convention already encodes part of this: a single word (`zaqefgadol`,
`merkhakefula`) = one accent with a traditional compound name; a **hyphen**
(`methiga-zaqef`) = an *ordered, cross-letter* idiom; a **bang** (`mahapakh!azla`) =
an *order-less, same-letter* cluster. The bang is a **representation** convention,
orthogonal to the *verdict*: it labels both the licit `fuse` case (`mahapakh!azla`,
accepted) and the `unlexical` case (`mahapakh!tipexa`, `merkha!azla`, flagged).

### Order normalization is same-letter only

We are liberal about mark order **within a single letter** (questionable penmanship is
not our concern) but must **preserve order across letters** (cross-letter order is
meaningful reading order). Implementation guard: normalize order **only between two
accents with no base consonant between them** — consonant-adjacent marks are by
definition on one letter, so such a swap can never reach across letters. A naive
"sort all marks in the word" would violate this. The cross-letter fusions are
order-*sensitive* and would break under normalization, which is why this scoping
matters: methiga-zaqef (qadma **before** zaqef), oleh-we-yored (ole **before** merka),
revia-mugrash (geresh-muqdam **before** revia), legarmeh / shalshelet-gedolah
(conjunctive/shalshelet **before** paseq).

### Prose / poetic asymmetry — the real work is all in prose

The poetic grammar treats conjunctives as a **fully permissive servus chain** (every
`D_phrase` is `D` optionally preceded by *any* run of servi; every Breuer servant-type
constraint was tested against L+MAM and **deliberately not encoded** — see the `issue
#18` notes throughout `ply_grammar_poetic.py`). So the poetic grammaticality verdict is
a function of the **disjunctive skeleton alone**. Consequence: **every same-letter pair
that includes a conjunctive is automatically a non-issue for the *grammaticality
verdict*** —

- deḥi + munaḥ (munaḥ is a servus, absorbed into `dexi_phrase`);
- merkha + qadma, ps56:10 (both are conjunctives — just servi);
- a secondary merkha / secondary mahapakh (conjunctives; never constrained).

**But a non-issue for the verdict is not a non-issue for faithful *representation*.** Such
a pair is two co-equal same-letter accents with no natural order (ps56:10's leaf even
flipped `azla merkha`↔`merkha azla` across code versions — the signature of "no natural
order"), so by the taxonomy's `fuse` row it arguably wants **one `merkha!azla` bang**, not
a reorderable sequence. Plan A does **not** do that here: bangs are gated to the *under
duress* case (a grammar-forced decision, like prose ek20:31), and poetic conjunctives are
never under duress. The faithful-representation half of that — emitting **one
`merkha!azla` bang** instead of a reorderable sequence — is spun off as **Plan D**
(`doc/PLAN-D-faithful-same-letter-bangs.md`), **now DONE**. But Plan D's *verdict* landed
on the opposite of "lift the gate to accept it": ps56:10 is treated as a **lexical
anomaly** (its merkha+azla is a same-letter pair *not on the whitelist* of legitimate
same-letter pairs — revia+geresh-muqdam, deḥi+munaḥ, oleh+yored), faithfully represented
as the bang yet flagged as a NO_PARSE oddball, with manuscript evidence (MAM carries azla
alone and, according to Breuer, so does the Aleppo Codex, while Sassoon 1053 carries
merkha alone — L conflates the two). The sweep confirmed ps56:10 is the *only* such
non-whitelisted same-letter pair in either genre beyond ek20:31. (Whether prose ek20:31's
`mahapakh!azla` should likewise be reclassified unlexical under the same whitelist is
deferred with the conjunctive-grammaticality work — see Plan D.)

The only poetic same-letter pairs that *can* matter touch the **disjunctive** skeleton:
revia-mugrash (lexicalized), ps124:4 (geresh+revia — **charitable promotion** to
revia-mugrash; the one live poetic change, see below), doubled tsinnor (Ps 17:14,
collapsed). So the poetic side of *this* problem reduces to ps124:4; the rest of the
remaining work is **prose**, where the grammar constrains servi and placement tightly
enough for a pair to produce a verdict worth deciding. (Separately, Plan C fixes the
poetic scanner's silent *swallowing* of real accents — tsinnorit, shalshelet qetannah —
which is faithfulness, not a same-letter-pair verdict.)

(Caveat — "pretty much ignore" is not "entirely ignore": a few narrow poetic spots make
a conjunctive structural — the unmarked-oleh recovery reclassifies a post-galgal merkha
to `OLEH_WEYORED`; oleh-we-yored / revia-mugrash *consume* a merkha / revia. None are
same-letter-pair situations and all are MAM-cross-checked.)

## The two open verses (the original topic of this plan)

### ps124:4 — geresh: fail-fast lexical error, with a same-letter charitable promotion

revia + plain geresh (U+059C) on **one letter**. **Today it passes incidentally, for the
wrong reason:** plain geresh is absent from the poetic rule table, so the scanner's
catch-all *silently swallows* it (the **only** catch-all swallow in the whole poetic
corpus — see Plan C), leaving a bare revia that `_reclassify_revia` maps to
`REVIA_MUGRASH` (#367, "revia mugrash without geresh"). The *token* is right but nothing
principled produced it, and the geresh is dropped regardless of where it sits — so the
earlier **"within-letter order-normalization charity" framing was wrong** (order plays no
role in today's behavior). Drop that framing.

**Intended handling:** a plain geresh in a poetic verse is a **lexical (pre-grammatical)
error** and should **fail fast** — the poetic analog of lv25:20 / the prose
`lexical_validation` layer (and of Plan C's "stop swallowing"). The **sole charitable
exception** is a geresh sharing a letter with a revia (the ps124:4 shape): read it
charitably as revia-mugrash. Document the charity on the Plan B page. Cite
<https://tanach.us/Notes/Psalms/Psalms.124.4.4-c.html>.

**Mechanism (verified empirically).** The charity is **two ingredients, both required** —
within-letter order-normalization **and** geresh→geresh-muqdam promotion:

1. **order-normalize within the letter** — `revia + geresh` → `geresh + revia` (legal:
   we are liberal about mark order *within* a single letter, never across letters); then
2. **promote** the plain geresh to **geresh-muqdam**, so the existing
   `GERESH_MUQDAM + REVIA → REVIA_MUGRASH` scanner rule consumes both as one token.

This vindicates the order-normalization *intuition* as a genuine ingredient — but it is
**not** the explanation of today's behavior (swallow + reclassify), and it is **not
sufficient alone**. Tested on ps124:4: promoting the geresh *in place* (keeping
revia-then-geresh order) **breaks** it — `REVIA_GADOL` + `REVIA_MUGRASH`, two
disjunctives; only after the same-letter swap does the single `REVIA_MUGRASH` survive.

**Implementation — DONE (charity); fail-fast deferred to Plan C.** The same-letter geresh
charity landed as one fusion rule in `ply_scanner_poetic._POETIC_GG_RULES`:
`REVIA + GERESH → REVIA_MUGRASH`, placed above the bare `REVIA` rule (longest-match wins;
adjacency = same-letter, no `X` between). Verified: ps124:4 still yields a single
`REVIA_MUGRASH` — now because the geresh is *consumed*, not swallowed — and the corpus
regen produces **no output diff at ps124:4** (the token was already right) and **no new
errors anywhere** (clean/oddball/NO_PARSE counts unchanged). Test:
`test_ps124_4_plain_geresh_charity_to_revia_mugrash` (+ a same-vs-cross-letter guard) in
`py/tests/test_ply_scanner_poetic.py`.

**Correction to the original premise (verified by corpus sweep):** "geresh is the
catch-all's only customer" is true **only for accents**. The `.` catch-all is
**load-bearing** — it is the scanner's general skip for every `X` placeholder (126,913×),
space, maqaf, and `]N` note marker. So it **cannot** be flipped wholesale; a fail-fast
must be a narrow rule matching a *stray accent* (U+0591–U+05AE) **above** the catch-all,
leaving the catch-all swallowing structural junk. After the charity that rule has **zero
live customers** (geresh is now consumed), so its representation is corpus-neutral — and a
poetic lexical-error representation doesn't exist yet (no poetic analog of prose
`lexical_validation`). Per the maintainer (2026-06-23), the **fail-fast guard is deferred
to Plan C**, which is already rebuilding this swallow region (tsinnorit / shalshelet
qetannah) and establishing the poetic "nothing vanishes" discipline holistically.

(Terminology note: geresh-muqdam **is** prepositive, but the revia/geresh here are
ordinary same-letter marks; keep "within-letter order normalization" for *same-letter*
swaps only — never cross-letter, which is meaningful reading order.)

### lv25:20 — DECIDED: a *lexical* error, not a grammatical one

**Decision (2026-06-23):** mahapakh + tipeḥa (two *below*-accents on one letter) is to
be treated as a **lexical (alphabet) error**, not a grammatical one. Two below-accents
cannot share a letter — the fault is *intrinsic to the letter*, independent of context;
it is an *unknown accent*, not a known accent in an illegal sequence. This is the same
seam as the stranded tsinnorit (M-C `82`) already handled in
`accgram.lexical_validation` (whose docstring anticipates "other stranded
stress-helpers... added later").

- **Supersedes** today's handling, which flags the verse via `tipexa_phrase → ERROR`
  (a grammatical-sequence verdict — the wrong rationale).
- **Why this is clean (no grammar change needed):** `run_ply.py` (~L132–140) already
  calls `lexical_validation.stranded_stress_helpers(verse.body)` for every prose verse
  and, when it returns anything, emits an `illegal_mark` ERROR tree and **skips the
  grammar entirely**. So a lexical flag on lv25:20 automatically pre-empts today's
  `tipexa_phrase → ERROR`.
- **Implementation — DONE (2026-06-23).** All six steps landed as specified; the prose
  regen flips **only** lv25:20, now reading `illegal_mark mahapakh!tipexa in נֹּאכַ֤֖ל`
  (the precise intended label). New detector `lexical_validation.illegal_below_pairs`
  (matches the pair in either within-letter order), wired into `run_ply.render_book`
  alongside `stranded_stress_helpers`; the rep-char map was renamed
  `_STRESS_HELPER_CHAR → _ILLEGAL_MARK_REP_CHAR` and keyed on mahapakh (U+05A4). Tests in
  `py/tests/test_lexical_validation.py`. Original step list, for the record:
  1. Add a detector to `lexical_validation` for one letter carrying **both mahapakh
     (U+05A4) and tipeḥa (U+0596)** — two *below*-accents adjacent in the mark string
     (no base letter between). This is a *different shape* from the existing
     stranded-helper check, so add a **sibling function** (e.g. `illegal_below_pairs`)
     returning the same `StrandedMark`-style record, not an overload of
     `stranded_stress_helpers`.
  2. **Report label uses the bang** (our same-letter-pair convention, memory
     `fused-impositive-cluster-token`): the verse should read
     `illegal_mark mahapakh!tipexa in נֹּאכַ֤֖ל` (not `+`). Put `"mahapakh!tipexa"` in the
     record's `code` field.
  3. **Word location needs the locator generalized, not bypassed.** `verse.body` is
     Unicode-marks text with consonants masked to `X` (the offending atom is literally
     `XXX֤֖X]c]n`), so the clean pointed word comes only from the kq-u index via
     `_stranded_unicode_words`, which maps a *code → representative char*
     (`_STRESS_HELPER_CHAR`). Rename that map to something neutral (e.g.
     `_ILLEGAL_MARK_REP_CHAR`) and key the new entry on **mahapakh (U+05A4)** — *not*
     tipeḥa, which recurs elsewhere in lv25:20 (word `נֶאֱסֹף`) and would mis-locate.
  4. In `run_ply.py`, call the new detector alongside `stranded_stress_helpers` and feed
     both into the existing `_illegal_mark_tree` / skip-grammar block.
  5. **Scope to the attested pair only** — hardcode mahapakh+tipeḥa; do **not**
     generalize to "any two below-accents" (memory `parse-rate-not-a-goal`).
  6. Test in `py/tests/test_lexical_validation.py`; verify by regenerating the prose
     corpus (`main_accgram.py run-ply-goerwitz`) and confirming **only lv25:20** flips
     from `tipexa_phrase → ERROR` to `illegal_mark`. A raw `-kq-u` scan (see *Faithful
     scan recipe* below) confirms lv25:20 is the **unique** non-decalogue verse with a
     same-letter mahapakh+tipeḥa pair, so the blast radius is exactly one verse.
- **Illegal status — confirmed (2026-06-23), gate satisfied.** No need to block on Yeivin:
  - **MAM has only the tipeḥa** — `MAM-simple/json-vtrad-bhs/Lev.json`, word `נֹּאכַל`
    carries `TIPEHA` alone; MAM dropped the mahapakh WLC keeps.
  - **WLC's own note is `]c]n`** — and `]n` = *"An anomalous form in the text of ל"*
    (`py/cmn/wlc_bracket_note_definitions.py`); `]c` = accent differs from BHS, "often a
    BHS typographical error." So WLC itself tags the word anomalous.
  - Per the maintainer, Breuer/Da-at Miqra is silent and Yeivin is unlikely to mention it.
  There is no grammaticality question — only the framing (settled) and report mechanics.

## Method (per cluster), reusing the ek20:31 precedent

1. Confirm same-letter (raw scan) and grammar-checked genre (prose vs poetic; not
   decalogue/gn35:22).
2. Classify by the taxonomy above (sequence / fuse / idiom / drop / unlexical).
3. If **fusing**: add a rule in the relevant scanner (`ply_scanner` prose,
   `ply_scanner_poetic` poetic) matching the two marks **adjacent** (no `X` between →
   same letter), in storage order, emitting one `!`-joined token, above the single-mark
   rules. Add only the **attested** grammar rule(s) (memory `parse-rate-not-a-goal`).
4. If **unlexical**: extend `lexical_validation` (the lv25:20 path).
5. Verify: `pytest`; regenerate the affected corpus (`main_accgram.py
   run-ply-goerwitz` prose, `run-ply-poetic` poetic) and confirm the diff is only the
   intended verses.

## Faithful scan recipe

Scan the **raw `-kq-u` words**, NOT `uni_to_marks` output (which *drops* swallowed
secondaries and would hide clusters). A "same-letter cluster" = ≥2 accents
(U+0591..U+05AE, meteg U+05BD excluded) between two base consonants. **Confirmed:** a
single letter never carries more than 2 accents (corpus-wide). Dual-cantillation verses
(decalogues Exod 20 / Deut 5, and Gen 35:22) are not grammar-checked — ignore them.

```python
from pathlib import Path
from collections import Counter, defaultdict
from accgram import rtms_data, accent_marks as am, research_tao
index = rtms_data.load_wlc422_index(
    research_tao.default_wlc422_kq_u_dir(Path('..').resolve()))
NAME = {getattr(am,n): n for n in dir(am)
        if isinstance(getattr(am,n),str) and len(getattr(am,n))==1 and '֑'<=getattr(am,n)<='֮'}
# group accents between base letters (א..ת); report groups with len>=2, with bcv refs.
# Run from py/, PYTHONIOENCODING=utf-8.
```

## Drive one verse (test recipe)

To see/​test what one verse tokenizes/parses to. Run from `py/`,
`PYTHONIOENCODING=utf-8`. A verse is **ungrammatical** iff its tree contains an `ERROR`
leaf (poetic-only: a `NO_PARSE` = total failure). Committed trees: prose
`out/accgram/ply/wlc_422_ps_<bb>_ag.txt`; poetic `out/accgram/ply-poetic/...`.

```python
from pathlib import Path
from accgram import rtms_data, research_tao, uni_to_marks, ply_scanner, ply_grammar
from accgram.ply_scanner import Token, HasLegarmeh
from accgram.ply_tree import print_tree
index = rtms_data.load_wlc422_index(research_tao.default_wlc422_kq_u_dir(Path('..').resolve()))
parser, HL = ply_grammar.build_parser(), HasLegarmeh()
bcv = 'lv25:20'; bb = bcv[:2]; ch, vr = bcv[2:].split(':')
body = uni_to_marks.verse_to_marks(index[bcv])      # <- mutate to test a hypothetical
toks = [Token('TILDE', '')] + ply_scanner.scan_accents(body, bb, int(ch), int(vr), HL)
tree = ply_grammar.parse_tokens(parser, toks)       # None | LOCATION_ONLY | TN
print(print_tree(tree) if tree and tree is not ply_grammar.LOCATION_ONLY else tree)
```

The leading `('TILDE', '')` is **mandatory** (`pasuq : TILDE … SOFPASUQ`). Poetic is the
same shape with `ply_scanner_poetic` / `ply_grammar_poetic`, but the faithful pipeline
first runs `poetic_reconcile.reconcile_tokens` then
`ply_grammar_poetic.parse_tokens_accepting_repeats`; oddballs via
`run_ply_poetic._has_error_leaf`. For a quick check prefer regenerating
(`main_accgram.py run-ply-poetic --book ps`) and grepping the output.

## Remaining work

1. ~~**ps124:4** — make the geresh principled.~~ **DONE** (charity rule). The catch-all
   **fail-fast guard** is **moved to Plan C** (the catch-all is load-bearing; only a
   narrow stray-accent rule is needed, with zero live customers after the charity).
2. ~~**lv25:20** — extend `lexical_validation` to flag mahapakh!tipeḥa.~~ **DONE**
   (`illegal_below_pairs`; label `mahapakh!tipexa`; locator keyed on mahapakh).
3. Hand the charity inventory + alternate-tree exhibit to **Plan B** (still open — Plan B).
4. **Plan C** owns the two *legal* swallowed poetic accents (tsinnorit, shalshelet
   qetannah) **and now also the catch-all stray-accent fail-fast guard** (geresh's charity
   already landed here; the fail-fast representation is built there, alongside the
   explicit-swallow conversions, as the unified poetic "stop swallowing" pass).
5. ~~**Plan D** owns the "stop swallowing *bangs*" goal — representing same-letter co-equal
   conjunctive pairs (ps56:10's merkha+qadma, etc.) as one `!` token rather than a
   reorderable sequence.~~ **DONE** — the sweep found ps56:10's `merkha+qadma` is the
   *sole* in-scope pair (everything else is idiom / drop / prepositive-neighbor /
   unlexical / already-fused), now represented as one `merkha!azla` bang but **flagged
   as a lexical anomaly** (NO_PARSE oddball, with LC/MAM/Aleppo/Sassoon manuscript notes
   + images). See `doc/PLAN-D-faithful-same-letter-bangs.md`.

> **Side note from the regen (the seed of Plan D):** regenerating the poetic corpus
> surfaced a **pre-existing stale output** at **Psalms 56:10** — current HEAD code emits
> the within-letter servus order `merkha azla` but the committed file still had
> `azla merkha` (the merkha+qadma same-letter pair). This drift predates and is
> independent of the geresh charity (it reproduces with the charity reverted); the
> regenerated file now matches current code. The fact that the *order flips at all* is
> exactly what motivates **Plan D**: a same-letter co-equal pair has no natural order, so
> emitting it as an ordered sequence presents an arbitrary order as if it were meaningful.
