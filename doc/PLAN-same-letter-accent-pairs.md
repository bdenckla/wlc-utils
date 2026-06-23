# Plan A: same-letter accent pairs — unified treatment + two open verses

**Status (2026-06-23):** the design has converged on a single taxonomy that makes
the formerly ad-hoc handling principled. Two live code changes remain: **lv25:20**
(prose lexical error — settled below) and **ps124:4** (poetic geresh — reframed below as
fail-fast + charity, *no longer* "documentation only"). Companions: **Plan B**
(`doc/PLAN-editorial-charities-page.md`) — the generated HTML page that documents these
"charities"; and **Plan C** (`doc/PLAN-poetic-swallowed-accents.md`) — the poetic
scanner's silent-swallowing defect (tsinnorit, shalshelet qetannah), discovered while
running down the ps124:4 geresh. Resolved precedents: ek20:31 (mahapakh+azla, **fused**);
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
| **fuse (`!`)** | co-equal accents, **no natural order**, under duress | one `a!b` token | `mahapakh!azla` (ek20:31) |
| **idiom** | an established compound accent | one named token | revia-mugrash, oleh-we-yored, methiga-zaqef |
| **drop** | a redundant companion of a prepositive/postpositive | drop the secondary | telg + geresh/gershayim → telg |
| **unlexical** | a positionally/grammatically **impossible** combination | alphabet-error post-pass (`lexical_validation`), *before* the grammar | `mahapakh!tipexa` (lv25:20) |

The orthographic convention already encodes part of this: a single word (`zaqefgadol`,
`merkhakefula`) = one accent with a traditional compound name; a **hyphen**
(`methiga-zaqef`) = an *ordered, cross-letter* idiom; a **bang** (`mahapakh!azla`) =
an *order-less, same-letter* duress cluster.

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
that includes a conjunctive is automatically a non-issue in poetic** —

- deḥi + munaḥ (munaḥ is a servus, absorbed into `dexi_phrase`);
- merkha + qadma, ps56:10 (both are conjunctives — just servi);
- a secondary merkha / secondary mahapakh (conjunctives; never constrained).

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

**Implementation:** flip the poetic scanner's catch-all from silent-swallow (`None`) to a
fail-fast lexical flag, with the same-letter geresh charity (order-normalize + promote)
**above** it. Geresh is the catch-all's only current customer, so this flip is scoped to
the geresh question and lives here; the *explicit-swallow* real accents (tsinnorit,
shalshelet qetannah) are **Plan C**'s. Verify only ps124:4 still yields revia-mugrash and
that **no other poetic verse newly errors** (Plan C's corpus swallow-sweep confirms
geresh is the lone catch-all hit, so the blast radius is exactly ps124:4).

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
- **Implementation:**
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

1. **ps124:4** — make the geresh principled: flip the poetic catch-all to fail-fast, add
   the same-letter charity (order-normalize + promote to geresh-muqdam). Live code, blast
   radius = ps124:4 only. Document the charity on the Plan B page.
2. **lv25:20** — extend `lexical_validation` to flag mahapakh!tipeḥa as a lexical error
   (label `mahapakh!tipexa`, generalized word-locator keyed on mahapakh). Illegal status
   **confirmed** (MAM + WLC `]n`); no further sourcing needed.
3. Hand the charity inventory + alternate-tree exhibit to **Plan B**.
4. **Plan C** owns the two *legal* swallowed poetic accents (tsinnorit, shalshelet
   qetannah); coordinate the shared catch-all-vs-explicit-swallow boundary (geresh's
   fail-fast flip is here; the explicit-swallow conversions are there).
