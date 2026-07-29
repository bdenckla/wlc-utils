# PLAN — two accents on one chanted word (prose)

Teach the prose checker that a chanted word normally has exactly one accent, and flag a chanted
word with two unless the pair matches a known, very restrictive pattern. The same rules apply to
an **atomic** chanted word as to a **maqaf compound**; this is a chanted-word rule, not a maqaf
feature.

Planning session 2026-07-28. **Phase 1 is implemented** — see §7 at the foot of this file for
what changed, what was verified, and what Phase 2 starts from.

Every number below marked *(probe)* came from a scratch script run during planning, **not** from
a regenerated tracked artifact. Phase 1 re-derived all of them in
`py/accgram/chanted_word_accents.py`; the tables below are now annotated with what the real
module measures, and §7 lists every place the probe was wrong.

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
| WLC prose | 233,238 (196,418 atomic + 36,820 compound) | **1,602** (1,107 atomic, 495 compound) | 33 |
| MAM prose | 234,985 (198,199 atomic + 36,786 compound) | **1,644** (1,160 atomic, 484 compound) | 19 |

*(Re-derived. The hit counts and their atomic/compound splits are the probe's exactly; the WLC
chanted-word totals are not, because the probe counted the swallowed ketiv of a ketiv-qere and
the petuhah/setumah markers as chanted words and the module does not. Both sequence counts were
wrong in the probe.)*

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
| §216 | mayela with etnaḥta | "in ten or eleven cases" | **11** — his eleven |
| §219/§221 | munaḥ-zaqef | "in many cases"; a fourth variant of the zaqef melody | 1374 |
| §223/224 | metigah-zaqef | — | one token; invisible to this rule |
| §233 | merkha with tipeḥa | "in 8 cases", listed | 12 — **explained**, see §7 |
| §236 | munaḥ with revia | "in five cases" | **5** — his five (Ex 32:31, Gen 45:5, Qoh 4:10, Zech 7:14, Dan 1:7) |
| §241 | **mehuppak with pashṭa** | "in five cases", all on the prefixed ־ש | 8 (his five, plus three compounds) |
| §244 | the two servi of pashta on one word | "in eight places", listed | his eight, inside a 13-strong union of `qadma+mahapakh`, `qadma+merkha`, `munax+mahapakh` |
| §253 | merkha-tevir | "some hundred cases" | 69 |
| §268 | **azla-geresh on one word** | "often" | **126** |
| §276 | munaḥ on the word bearing pazer | "in one case, Gen 50:17" | **1**, at gn50:17 |
| §372/§373 | tsinnorit, poetic metigah | poetic | out of scope |

*(Re-derived; every measured figure above is now read out of `out/accgram/chanted-word-accents.json`.
Two section numbers were wrong in the planning pass: the "fourth variant of the zaqef melody"
sentence is **§219**, not §221 — §221 gives munaḥ-zaqef's conditions — and the pazer case is
**§276**, which the plan had cited only by OCR line number.)*

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
no argument of its own. ITM **§302** (not §301, which is about maqaf variants between
manuscripts): *"From the point of view of the accentuation, words joined by maqqef are considered
as a single unit, and are treated so in the marking of conjunctives, secondary accents, and
gaʿya"*, illustrated with אל־האשה taking munaḥ-zaqef precisely because the maqaf makes it one unit.

### The residue

After the whitelist above, MAM prose leaves **18** chanted words whose token sequence no section
of Yeivin's inventory names — `qadma+darga` 6 (including Job's prose frame ×4), `merkha+silluq` 5,
the five telisha-gedola + geresh-family words already whitelisted elsewhere in
`lexical_validation`, `merkha+pashta` 1, `merkha+munax` 1. That is a publishable finding on its
own: the whole prose Tanakh, in the corpus a grammatical claim takes, has eighteen chanted words
with two accents that Yeivin's inventory does not name, and five of those eighteen are the
telisha-gedola words the almost-errors page already documents. The list is carried as
`mam_residue` in the JSON.

WLC's residue is larger and different in kind, and includes the cases the pages already care
about: `munax+munax` at 1c27:14 לעשתי־עשר, 2c1:11 ויאמר־אלהים and ek8:6 מה־הם (which the probe
missed), plus one atomic `munax+munax` at gn36:13. **MAM has none.**

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

---

## 7. Phase 1 state (executed 2026-07-28)

### Main moved under this phase, and Phase 1 was rebased onto it

Phase 1 was written against `48137a6`. While it ran, Ben committed **`832df3e`, "Report the pairs
that occur, and count them on simple chanted words too"**, which cut the whole route
classification out of `maqaf-nonfinal-accents.html` — the undecided and no-named-configuration
rows, the §§293/357 paragraph, the Judges 7:13 positional worked example, and two `pin_claims`
assertions — and added, to the survey, a per-pair count of the **simple chanted words** carrying
two different accents. Phase 1 was rebased onto it, and that changed what Phase 1 lands:

- **Dropped**, as superseded: every page-side edit. `_CONFIG_DISPLAY` no longer exists, so the
  labels, the `ROM_AZLA` constant added for them, the reworded route sentence and the two new
  `pin_claims` assertions all went with it. `maqaf_nonfinal_accents_page.py` and
  `printed_decalogue_strands.py` are untouched by this phase, and
  **`gh-pages/accgram/maqaf-nonfinal-accents.html` does not move at all.**
- **Kept**: the new module, `Token.start`, the subcommand, and the citation corrections — the
  survey still computes the routes, so `_NAMED_CONFIGURATIONS` is still live and still wrong
  without them. It is now only the JSON's `by_configuration` that moves.
- **Also kept from Ben's rewrite**: his rule that it is "the mayela", never "the mayela tipexa".
  The new module's §210 and §216 entries follow it.

**A convergence worth acting on in Phase 2 or 3.** `832df3e`'s own message says of its new simple
chanted-word count that "two marks are not always two accents — 135 of them are a tsinnorit beside
a tsinnor, which in a prose verse is the zarqa written twice — and telling those apart wants the
scanner's tokenization rather than this scan." That is exactly what `chanted_word_accents` does:
the scanner fuses tsinnorit + tsinnor into one `ZARQA` token, so its atomic counts have the 135
already removed. The two measures should be reconciled rather than left to disagree.

### What changed

**New: `py/accgram/chanted_word_accents.py`** — pure computation plus a JSON writer, modelled on
`maqaf_nonfinal_accents`. It builds each verse's mark body **atom by atom**, keeping every
fragment's Unicode beside its marks, so a token position is an offset into the same string the
chanted-word boundaries are offsets into. For WLC the rebuilt body is asserted equal to
`uni_to_marks.verse_to_marks`' own output for every verse of WLC 4.22, poetic ones included,
which is what makes the Unicode-to-marks alignment a checked fact rather than a claim. It writes
`out/accgram/chanted-word-accents.json` (29,710 lines).

**New subcommand** `survey-chanted-word-accents` in `main_accgram.py`. Phase 3's page generator
should either call this module or replace the subcommand, as
`generate-html-maqaf-nonfinal-accents` does for the other survey.

**`prose_scanner.Token` gained `start`**, as `field(default=-1, compare=False, repr=False)`.
Excluding it from `__eq__`/`__hash__`/`__repr__` is stronger than the plan proposed and costs
nothing: two tokens of the same type and leaf stay equal and interchangeable everywhere the repo
already treats them so, and the six positional `Token("TILDE", "")` constructions are unaffected.
`scan_accents` sets it at emit time; the recovered verse-final `SILLUQ` of a sof-pasuq-less verse
carries the position of the U+05BD it came from.

**Reuse hooks in `maqaf_nonfinal_accents`**: `_UXLC_FILE_TO_BB` → `UXLC_FILE_TO_BB` and
`_uxlc_text` → `uxlc_text`, since the new module reads the same XML for atoms rather than for
chanted words.

**The two citation faults are fixed**, and four sections added, in
`maqaf_nonfinal_accents._NAMED_CONFIGURATIONS`:

- merkha-tevir is **§253**, not "§§233, 241".
- `(MAHAPAKH, TEVIR)` — which had never fired in any corpus, in either genre, since the survey
  was written — is replaced by `(MAHAPAKH, PASHTA)`, §241's real pairing.
- added: §268 azla-geresh, §215 munaḥ-with-etnaḥta, §236 munaḥ-with-revia, §276 munaḥ-with-pazer;
  and §216 / §210 now carry their section numbers on the two mayela labels.

`maqaf_nonfinal_accents_page` is **not** touched. It was, until the rebase onto `832df3e` above
made every one of those edits unnecessary.

### What was verified

1. **`out/accgram/chanted-word-accents.json` written and read back.** Every figure quoted here
   and in the tables above is read out of the regenerated file.
2. **The closed-list assertions pass and raise on drift.** §210's five, §215's two, §216's
   eleven, §236's five and §276's one at gn50:17 match exactly; §233's eight, §241's five and
   §244's eight are each fully contained in the measurement, with the surplus recorded as data.
   The assertion **earned its keep on the first run**: it rejected `nu2:26` for §216, and the OCR
   line ("בשבעת יכם 8:26 2 Nu") turns out to be Numbers **28**:26 with the 28 broken across the
   reference. That transcription slip would have stood unnoticed without the check.
3. **§233's discrepancy is explained**, in the JSON's `merkha_tipexa_discrepancy`. All eight of
   Yeivin's have both marks on ONE atom (four atomic chanted words, four compounds with the
   merkha on the same atom as the tipeḥa); all four beyond his list instead have the merkha on a
   non-final atom — is66:8 אם־יולד־גוי, ek1:4 ונגה־לו, 2c8:11 אשר־באה־אליהם, 2c14:6 וינח־לנו.
   §241's three-case surplus has exactly the same shape. **This is left as an open question, not
   a verdict**, because the two surveys currently answer it differently: `_NAMED_CONFIGURATIONS`
   labels a merkha on a non-final atom with a tipeḥa on the compound as §233's secondary merkha,
   which is precisely those four, while Yeivin's own list excludes them. Issue #82.
4. **`generate-html-maqaf-nonfinal-accents` regenerated, diff read.** Hit sets, per-hit shapes,
   oracle evidence, the whole gray-maqaf section and **the rendered page itself** are unchanged in
   all three corpora and both genres. What moved, in the JSON only: the label renames, and six
   hits reclassified from route (b)/undecided into route (a) now that §§215, 236 and 241 name them
   (WLC prose 126→132 route (a), UXLC 120→124, MAM 230→233). MAM prose now has neither a route-(b)
   nor an undecided case. §268 and §276 name nothing in *that* survey, since no compound anywhere
   has a qadma on a non-final atom with a geresh on the compound; they are correct entries that
   this shape cannot express, which is why the wider survey exists.
5. **`run-prose` regenerated: `out/accgram/prose/*_ag.json` byte-identical**, 18,724/18,724 verses.
   The `Token.start` field is invisible to the outputs.
6. **`.venv/Scripts/pytest.exe py/tests`: 487 passed, 5 skipped.** The tree-wide transliteration
   lint caught Yeivin's `mehuppak` and `merka` spellings on first run; his verbatim quotes now
   carry `# translit-ok`, and every line of the repo's own prose says `mahapakh` and `merkha`.
7. **black** run on all six touched files.

### Generated outputs: what moved and what deliberately did not

| file | moved? |
| --- | --- |
| `out/accgram/chanted-word-accents.json` | **new** |
| `out/accgram/maqaf-nonfinal-accents.json` | yes — route/configuration labels and six reclassified hits; no hit, shape, oracle or gray-maqaf change |
| `gh-pages/accgram/maqaf-nonfinal-accents.html` | **no** — `832df3e` had already cut the classification out of the page |
| `out/accgram/prose/*_ag.json` | **no**, byte-identical, and that is the check on `Token.start` |
| everything else under `out/` and `gh-pages/` | not regenerated and not touched |

### Unresolved risks and open questions

- **The §233/§241 surplus (above) is unresolved**, and the two surveys disagree about it. It has
  to be settled before either the route-(b) material or a Phase 3 page states what those hits
  are. Issue #82.
- **`(MERKHA, SILLUQ)` is cited to §233 in `_NAMED_CONFIGURATIONS`, and §233 is about tipeḥa.**
  Yeivin has no section naming a secondary merkha in a silluq's chanted word — §209 gives silluq
  one conjunctive, merkha, and says nothing of a secondary. Left alone this phase (it is the same
  #82 question). Less urgent since `832df3e`, which stopped the page printing the label at all,
  but it still covers four MAM prose hits in the JSON.
- **`(QADMA, ZAQEF_QATAN)` is cited to §224.** §223 is where metigah-zaqef is defined; §224 is
  the retraction of methigah. Not wrong — §224 does discuss the combination — but not the
  defining section either. Left alone as out of this phase's scope.
- **MAM's `merkha tevir` is 69, WLC's is 2 and UXLC's is 10.** Yeivin §254 predicts exactly this
  ("Already in L gaʿya occurs in most of the cases where merka is expected"), and a meteg emits no
  token, so a manuscript that has one there shows a single accent token. The WLC-to-UXLC gap is
  Kimball's corrections. Worth a sentence somewhere; it is a finding, not a defect.
- **The METHIGAZAQEF fuse is not perfectly word-internal**, as the plan suspected: 5 of WLC's 324
  prose tokens span a chanted-word boundary (gn18:18, je37:10, je49:19, mi2:7, ne9:20), 3 of
  UXLC's 324, and 1 of MAM's 410 (lv13:33). Named in each corpus's `methigazaqef.crossings`. The
  design leans on the fuse, so Phase 2's whitelist should not assume it stays inside one chanted
  word.
- **Two `geresh_folds` fired, both in MAM** (lv10:4 קרבו, ek48:10 ולאלה), exactly as the plan
  predicted; WLC and UXLC need no fold. Each is recorded with its scanned and its counted
  sequence.

### The exact next phase

**Phase 2 as written in §5**, unchanged except that its first bullet is already done:

- ~~`prose_scanner.Token` gains `start`~~ — done in Phase 1, with `compare=False, repr=False`.
- Write `chanted_word_accents.classify_verse(body, tokens)` → the hits of one verse, each named
  with its ITM section or unnamed. Key the whitelist on the **token pair**, not on a verse
  reference (decision 1); Yeivin's closed lists are checked in Phase 1's data and are not
  consulted here. The whitelist is the `token_sequences` of the §-entries in `YEIVIN_ENTRIES`,
  which is already the right shape to read it off; the 18 in `mam_residue` are what it will flag.
- Wire it into **both** consumer paths as an additive field: `prose_run._verse_record` and
  `printed_decalogue.parse_marks_body`.
- **Verification**: regenerate `out/accgram/prose/*_ag.json` and
  `out/accgram/printed-decalogue/_printed_decalogue.json`; every existing `status`, `errors` and
  `tree` must be byte-identical, the new field the only diff anywhere.
