# Plan A: same-letter accent pairs — unified treatment + two open verses

**Status (2026-06-23):** the design has converged on a single taxonomy that makes
the formerly ad-hoc handling principled. Almost all of it *describes what the code
already does*; the only live code change is **lv25:20** (decided below). Companion:
**Plan B** (`doc/PLAN-editorial-charities-page.md`) — the generated HTML page that
documents these "charities" and shows the alternate readings. Resolved precedents:
ek20:31 (mahapakh+azla, **fused**); the telisha-gedola + geresh-family family (5 words,
**drop-to-telg**); poetic revia-mugrash (established single token). See also the durable
design note in memory `fused-impositive-cluster-token`, and the worked example
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

The only poetic same-letter pairs that *can* matter touch the **disjunctive** skeleton,
and those are already handled: revia-mugrash (lexicalized), ps124:4 (absorbed as
revia-mugrash; see below), doubled tsinnor (Ps 17:14, collapsed). So the poetic side of
this problem is effectively closed; all remaining work is **prose**, where the grammar
constrains servi and placement tightly enough for a pair to produce a verdict worth
deciding.

(Caveat — "pretty much ignore" is not "entirely ignore": a few narrow poetic spots make
a conjunctive structural — the unmarked-oleh recovery reclassifies a post-galgal merkha
to `OLEH_WEYORED`; oleh-we-yored / revia-mugrash *consume* a merkha / revia. None are
same-letter-pair situations and all are MAM-cross-checked.)

## The two open verses (this session's original topic)

### ps124:4 — documentation only (no behavior change)

revia + plain geresh, the *reversed* order of revia-mugrash's geresh+revia. It already
parses clean as revia-mugrash: the plain geresh is not a poetic accent (swallowed), and
the bare revia before silluq is reclassified to `REVIA_MUGRASH` (#367). The only thing
to do is **document the rationale** as the within-letter **order-normalization charity**
(revia+geresh ≡ geresh+revia), the poetic mirror of the prose geresh-muqdam→geresh
charity. Cite <https://tanach.us/Notes/Psalms/Psalms.124.4.4-c.html>.

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
     returning the same `StrandedMark`-style record (label + atom), not an overload of
     `stranded_stress_helpers`.
  2. In `run_ply.py`, call the new detector alongside `stranded_stress_helpers` and feed
     both into the existing `_illegal_mark_tree` / skip-grammar block.
  3. **Scope to the attested pair only** — hardcode mahapakh+tipeḥa; do **not**
     generalize to "any two below-accents" (memory `parse-rate-not-a-goal`).
  4. Test in `py/tests/test_lexical_validation.py`; verify by regenerating the prose
     corpus (`main_accgram.py run-ply-goerwitz`) and confirming **only lv25:20** flips
     from `tipexa_phrase → ERROR` to `illegal_mark`.
- **Before wiring it:** confirm the "illegal" status against Yeivin (the Yeivin docx —
  memory `tanakh-docx-paths`) or a MAM doc-note (<https://bdenckla.github.io/MAM-with-doc/>,
  by chapter+verse). There is no grammaticality question — only the framing (settled)
  and the report mechanics.

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

1. **ps124:4** — fold the order-normalization charity into the docs (and Plan B page).
   No code.
2. **lv25:20** — extend `lexical_validation` to flag the two-below-accent combination as
   a lexical error (decision recorded above); confirm illegal status against Yeivin /
   MAM first.
3. Hand the charity inventory + alternate-tree exhibit to **Plan B**.
