# PLAN — two accents on one chanted word (prose)

Teach the prose checker that a chanted word normally has exactly one accent, and flag a chanted
word with two unless the pair matches a known, very restrictive pattern. The same rules apply to
an **atomic** chanted word as to a **maqaf compound**; this is a chanted-word rule, not a maqaf
feature.

Planning session 2026-07-28. Nothing implemented. Every number below marked *(probe)* comes from
a scratch script run against the committed corpora during planning, **not** from a regenerated
tracked artifact — Phase 1 re-derives all of them in a real module, and the plan's prose must be
rewritten against that module's JSON before any of it reaches a page.

---

## 1. What the checker can and cannot see today

`prose_scanner.scan_accents` reads a **mark body** in which maqaf (`-`) and space survive as
structural filler beside the opaque `LETTER` placeholder, so the boundaries are all there. But it
returns `list[Token]`, and a `Token` is `(type, leaf)` — no position. The PLY grammar therefore
consumes accent types alone and cannot see a chanted-word boundary at all.

A few scanner rules already read the filler locally, and each of them is load-bearing for this
work because each **fuses two written marks into one token**:

| rule | what it fuses | crosses a maqaf? |
| --- | --- | --- |
| `METHIGAZAQEF` | qadma … zaqef qatan | yes, deliberately |
| `PASHTA` | stress-helper pashta + main pashta | no (`TEXT` stays in one atom) |
| `ZARQA` | tsinnorit + tsinnor | no |
| `TELISHAQETANNA` | helper telisha + main telisha | no |
| `MAHAPAKHQADMA` | the same-letter bang cluster | n/a (one letter) |
| `LEGARMEH` | munaḥ + U+05C0 | no |
| `AZLA` (lookahead only) | nothing — it renames a qadma | crosses a word boundary |

**This is the key design fact.** Counting *tokens* rather than *marks* disposes of four of the
five confounds for free:

1. a stress helper written twice is already one token;
2. a fused impositive cluster (`mahapakh!qadma`, `merkha!azla`) is already one token;
3. meteg emits no token, and U+05BD becomes `SILLUQ` only immediately before sof pasuq;
4. legarmeh is one token, and a narrow-sense paseq is swallowed.

It also disposes of metigah-zaqef, which is *already* one `METHIGAZAQEF` token and so never
presents as two accents on one chanted word — 324 of them in WLC prose *(probe)*.

The fifth confound survives and must be handled by hand: **a repeated geresh or gershayim is one
accent written twice, and the scanner does not fuse it.** MAM's Lev 10:4 and Ezek 48:10 come out
as three tokens apiece (`gershayim+telishagedola+gershayim`, `geresh+telishagedola+geresh`)
*(probe)*.

### Two consumer paths, and only one of them runs the word-level layer

- `prose_run._verse_record` → `lexical_validation.lexical_ungrammatical(body)`, then the grammar.
- `printed_decalogue.parse_marks_body` → the grammar **only**. The Wikisource strands and all
  twelve hand transcriptions reach the grammar through this path, so `lexical_validation` never
  sees them — including `koren_dt_elyon`, the case that motivates the whole exercise.

`lexical_validation` also **short-circuits**: a verse with a hit gets a fixed one-leaf ERROR tree
and the grammar is skipped entirely. Routing a chanted-word rule through it would discard the
parse tree of every affected verse and would overwrite, rather than sit beside, the verdict
SimTiq's Exodus appendix taḥton already has for an unrelated reason.

---

## 2. What is actually out there — the measurement nobody had

The compound half was surveyed by `maqaf_nonfinal_accents` (WLC prose 139 hits, MAM prose 233).
That survey asks a **narrower** question than this one: it counts an accent on a **non-final**
atom, so it never sees two accents that both sit on a compound's last atom, and it counts marks
rather than tokens, so its 202 MAM `qad-zaq` compounds are one token each here.

The atomic half had never been measured at all. It is the larger half.

### Chanted words with two or more accent tokens *(probe)*

| | chanted words | with ≥2 accent tokens | distinct token sequences |
| --- | --- | --- | --- |
| WLC prose | 237,220 (200,353 atomic + 36,867 compound) | **1,602** (1,107 atomic, 495 compound) | 47 |
| MAM prose | 234,985 (198,199 atomic + 36,786 compound) | **1,644** (1,160 atomic, 484 compound) | 33 |

Of WLC's 495 compounds, 450 have both tokens on the **final atom** and only 45 split across
atoms — which is why the existing maqaf-non-final survey sees so few of them.

MAM is markedly the more regular corpus, as the 33-vs-47 sequence count says: every one of WLC's
odd shapes (`munax+munax`, `pashta+zaqef`, `zaqef+tipexa`, `darga+tevir`, `tipexa+munax`,
`telishagedola+revia`, `merkha+legarmeh`, `mahapakh+tipexa`) is absent from MAM. A grammatical
claim takes MAM, so **MAM is the corpus the whitelist must be closed against**, and WLC's residue
is then a statement about the Westminster transcription of L rather than about the accentuation.

### MAM prose, every sequence *(probe)*

| tokens | atomic | compound | total |
| --- | --- | --- | --- |
| munaḥ + zaqef | 959 | 415 | 1374 |
| azla + geresh | 99 | 27 | **126** |
| merkha + tevir | 61 | 8 | 69 |
| merkha + tipeḥa | 4 | 8 | 12 |
| mayela + etnaḥta | 3 | 8 | 11 |
| mahapakh + pashta | 3 | 5 | 8 |
| qadma + merkha | 3 | 3 | 6 |
| qadma + mahapakh | 4 | 2 | 6 |
| qadma + darga | 5 | 1 | 6 |
| mayela + silluq | 4 | 1 | 5 |
| munaḥ + revia | 4 | 1 | 5 |
| merkha + silluq | 1 | 4 | 5 |
| gershayim/geresh with telisha gedola | 5 | 0 | 5 |
| munaḥ + etnaḥta | 2 | 0 | 2 |
| munaḥ + pazer | 1 | 0 | 1 |
| munaḥ + mahapakh | 1 | 0 | 1 |
| merkha + pashta | 0 | 1 | 1 |
| merkha + munaḥ | 1 | 0 | 1 |

---

## 3. Yeivin's inventory is larger than the whitelist as stated, and most of it is closed lists

Grepping the full OCR at `../yeivin-itm/md-export-of-docx/` turns up a **named section for each
of these**, and the closed ones match the measured MAM counts case for case. This is the plan's
central finding: the whitelist is not something to invent, it is something to transcribe, and
transcribing it yields a differential check against an independent oracle — the one test shape
that has ever paid in this repo.

| ITM § | what it names | Yeivin's own count | MAM measured *(probe)* |
| --- | --- | --- | --- |
| §210 | mayela with silluq | "in five places" | **5** — and his five verses are the measured five (Lev 21:4, Nu 15:21, Is 8:17, Hos 11:6, 1C 2:53) |
| §215 | munaḥ with etnaḥta | "in two cases" | **2** — his two (2S 12:25, 1C 5:20) |
| §216 | mayela with etnaḥta | "in ten or eleven cases" | **11** |
| §221 | munaḥ-zaqef | "in many cases"; a fourth variant of the zaqef melody | 1374 |
| §223/224 | metigah-zaqef | — | one token; invisible to this rule |
| §233 | merkha with tipeḥa | "in 8 cases", listed | 12 — **does not match; investigate** |
| §236 | munaḥ with revia | "in five cases" | **5** — his five (Ex 32:31, Gen 45:5, Qoh 4:10, Zech 7:14, Dan 1:7) |
| §241 | **mehuppak with pashṭa** | "in five cases", all on the prefixed ־ש | 8 (his five, plus three compounds) |
| §244 | the two servi of pashta on one word | "in eight places", listed | spread over `qadma+mahapakh`, `qadma+merkha`, `munax+mahapakh` |
| §253 | merkha-tevir | "some hundred cases" | 69 |
| §268 | **azla-geresh on one word** | "often" | **126** |
| N0241:827 | munaḥ on the word bearing pazer | "in one case, Gen 50:17" | **1**, at gn50:17 |
| §372/§373 | tsinnorit, poetic metigah | poetic | out of scope |

Three consequences, each of which changes the work:

**(a) `azla-geresh` (§268) is missing from the whitelist as stated, and it is the second-largest
class.** 126 chanted words in both WLC and MAM. Yeivin frames it in exactly Ben's terms:
*"Azla is often marked as a secondary accent on the word bearing geresh. This occurs under
conditions similar to those governing the marking of munaḥ on the word bearing zaqef, or merka on
the word bearing tevir (#221, 253)."*

**(b) `maqaf_nonfinal_accents._NAMED_CONFIGURATIONS` has two citation faults.** It cites
"ITM §§233, 241" for the secondary merkha in a tevir's chanted word; the section is **§253**
(`Merka-tevir and the Servi of Tevir`). And its `(MAHAPAKH, TEVIR)` entry has never fired in any
corpus, because **§241 is mehuppak with *pashṭa*, not with tevir** — which is also why
`mahapakh+pashta` shows up in the measurement and `mahapakh+tevir` does not.

**(c) Yeivin states Ben's own principle outright**, so the atomic-and-compound unification needs
no argument of its own. ITM §301: *"words joined by maqqef are considered as a single unit, and
are treated so in the marking of conjunctives, secondary accents, and gaʿya"*, illustrated with
אל־האשה taking munaḥ-zaqef precisely because the maqaf makes it one unit.

### The residue

After the whitelist above, MAM prose leaves roughly twenty chanted words unnamed *(probe)* —
`qadma+darga` 6 (including Job's prose frame ×4), `merkha+silluq` 5, the five telisha-gedola +
geresh-family words already whitelisted elsewhere in `lexical_validation`, `merkha+pashta`,
`merkha+munax`. That is a publishable finding on its own: the whole prose Tanakh, in the corpus a
grammatical claim takes, has about twenty chanted words with two accents that Yeivin's inventory
does not name.

WLC's residue is larger and different in kind, and includes the two cases the pages already care
about: `munax+munax` at 1c27:14 לעשתי־עשר and 2c1:11 ויאמר־אלהים, plus one atomic `munax+munax` at
gn36:13. **MAM has none.**

---

## 4. Recommendations

### 4.1 A new module, not a change to the grammar

`py/accgram/chanted_word_accents.py` (+ `_page`), beside `maqaf_nonfinal_accents`.

Teaching the PLY grammar about boundaries means threading a boundary token through every
production of a 39,000-line grammar file whose completion criterion was byte-identical parity with
the frozen Goerwitz C checker. The rule is not a rule about accent *sequence* — the grammar's
whole subject — it is a rule about how a sequence is distributed over chanted words. This repo
already has a home for word-level rules the C grammar has no notion of (`lexical_validation`'s
three checks), and the precedent is a separate layer, not a grammar change.

The one enabling change to mature code is small and additive: give `prose_scanner.Token` a
`start: int = -1` field, set at emit time. Nothing in the repo compares `Token` instances — only
`.type` and `.leaf` are read — and the six positional `Token("TILDE", "")` constructions keep
working.

### 4.2 A separate diagnostic channel first; the ERROR leaf is a later, gated decision

Recommend recording hits as their own field on the verse record, leaving `status` and `tree`
untouched, and deciding promotion only once the whitelist is closed. Three reasons:

- `lexical_validation` short-circuits, so routing through it discards parse trees and **overwrites**
  the SimTiq Exodus taḥton verdict instead of standing beside it. Ben's instruction is explicit
  that the new rule be evaluated against the existing verdicts.
- `parse_marks_body` — the Koren path — does not call `lexical_validation` at all, so an
  `illegal_mark` implementation would miss the motivating case unless separately wired.
- A channel makes the whitelist reviewable against evidence before it changes any verdict, and the
  promotion is then a one-line change with a readable diff.

A clean rate is not a goal, so this is not a reluctance to flag; it is sequencing.

---

## 5. Phases

### Phase 1 — Measure both halves, and transcribe Yeivin's inventory

New `py/accgram/chanted_word_accents.py`: pure computation plus a JSON writer, the shape
`maqaf_nonfinal_accents` already has.

- Re-derive every *(probe)* number above in the module, over WLC 4.22, UXLC and MAM-simple, prose
  verses only, routed by `prose_filter.should_keep_line`.
- Per hit: `bcv`, the chanted word in **letters and accents, no vowels**
  (`almost_errors_html_shared.accents_and_letters`, lifted from the corpus, never retyped), the
  token sequence, and the kind (atomic / compound with the accents split across atoms / compound
  with both on the final atom).
- A `yeivin_inventory` table transcribed from `../yeivin-itm/md-export-of-docx/`: section number,
  what it names, Yeivin's stated count, his listed verses where he lists them, and the measured
  count beside it. Where his list is closed, assert set equality and **raise** on drift.
- Correct `maqaf_nonfinal_accents._NAMED_CONFIGURATIONS`: §253 for merkha-tevir; replace the
  never-firing `(MAHAPAKH, TEVIR)` with §241's mehuppak-with-pashṭa; add §268 azla-geresh, §215,
  §236, §210's silluq mayela and the §pazer case as far as that survey's shape allows.
- Note as data, not as prose: 5 of 324 `METHIGAZAQEF` tokens span a chanted-word boundary
  *(probe)* — the fusion the design leans on is not perfectly word-internal, and the five cases
  should be named.

**Verification.** `out/accgram/chanted-word-accents.json` is written and read; the closed-list
assertions pass (§210's five, §215's two, §236's five, §244's eight, the one §pazer case); the
§233 mismatch (8 stated vs 12 measured) is either explained or recorded as an open question.
Regenerate `out/accgram/maqaf-nonfinal-accents.json` and its page with
`generate-html-maqaf-nonfinal-accents` and read the diff — the citation corrections should move
`by_configuration` labels and nothing else.

**Handoff.** The whitelist table, closed against MAM and cited to Yeivin, plus the named residue.

### Phase 2 — The whitelist, the token positions, and the diagnostic channel

- `prose_scanner.Token` gains `start`.
- `chanted_word_accents.classify_verse(body, tokens)` → the hits of one verse, each named
  (with its ITM section) or unnamed. The whitelist is keyed on the **token pair**, not on a verse
  reference (decision 1): Yeivin's closed lists are checked in Phase 1's data, not consulted here.
- Wire it into **both** consumer paths as an additive field: `prose_run._verse_record` and
  `printed_decalogue.parse_marks_body` (which covers the eight Wikisource strands and all twelve
  transcriptions in one stroke).

**Verification.** Regenerate `out/accgram/prose/*_ag.json` (`run-prose`) and
`out/accgram/printed-decalogue/_printed_decalogue.json` (`run-printed-decalogue`). Every existing
`status`, `errors` and `tree` must be **byte-identical**; the only diff anywhere is the new field.
That invariant is the phase's test, and it is checkable by eye in the diff.

### Phase 3 — The rendered page

`chanted_word_accents_page.py` → `gh-pages/accgram/chanted-word-accents.html`, wired into
`generate-html` and `generate-html-chanted-word-accents`, one run writing both the JSON and the
page, with a `pin_claims` that re-derives every stated number from the data and raises on drift.

One page, one question: **does a chanted word with two accents that Yeivin's inventory does not
name have a precedent in the prose Tanakh?** Koren's Deuteronomy appendix עליון sets לא־תעשה with
a munaḥ on each atom; the answer the data gives is that WLC has three such chanted words and MAM
none. Everything else — the route split, the §233 discrepancy, the METHIGAZAQEF boundary cases —
goes to a linked GitHub issue rather than onto the page.

### Phase 4 — Promotion (gated on the answers in §6)

If the flag becomes an ERROR, `classify.py` and the goerwitz page pick it up with no further
wiring. Verification is the ungrammatical-set diff, read against the existing verdicts: SimTiq's
Exodus appendix taḥton third chanted verse is already ungrammatical for an unrelated reason
(three servi where the pashta phrase takes two), so what the phase must show is which verdicts are
**newly** ungrammatical, not a total.

---

## 6. Decisions (settled with Ben, 2026-07-28)

1. **Pin Yeivin's lists as DATA, allow the configuration as the RULE.** Where he gives a closed
   list, the `yeivin_inventory` section of the JSON carries his verses and the module asserts set
   equality against the measurement, raising on drift — so the differential oracle is kept in full.
   The checker's own whitelist is nonetheless **configuration-level**: `munax+revia` is named
   wherever it occurs, not only at §236's five. This keeps verse references out of the flagging
   path while keeping the sharpness where it earns its keep.
2. **Survey WLC, UXLC and MAM; flag WLC (and the Decalogue paths) only.** The whitelist is closed
   against MAM, as a grammatical claim requires, but the per-verse field lands in
   `out/accgram/prose` and `_printed_decalogue.json`, which is where verdicts live today. Record
   plainly that Isaiah 40:7 נבל־ציץ is therefore a MAM-only case the WLC flag never sees: WLC sets
   נבל and ציץ as two chanted words.
3. **CTR stays glyph-level.** Its two cases are recorded in `ctr_decalogue` as evidence about CTR;
   grammar-checking it would produce verdicts that invite reading it as a precedent, which it is
   not.
4. **Channel first, promotion decided later** — §4.2 as written. Phases 1–3 add a diagnostic field
   only; Phase 4 revisits it once the whitelist is closed and the residue is visible.
