# CLAUDE.md

## Read `doc/agent-planning-principles.md` before planning work here

That file holds this repo's planning preferences (phase sizing, new-features-as-new-modules,
writing state back between phases, keeping verification close to the real workflow). Nothing
in the tree referenced it, so for a long time no agent ever loaded it — hence this pointer.

## Rendered-prose conventions: `py/accgram/printed_decalogue_strands.py`'s module docstring

That docstring is where the editorial conventions for accgram's **rendered prose** are recorded
— strand names in Hebrew letters and never transliterated, the two signal-word sets, the
single-sourced `ROM_*` romanizations and their italic wrapper, "the Simanim Tiqqun" and never a
bare "Simanim", real em dashes, no English sentence opening on a Hebrew word. It lives in the
printed-Decalogue trio because that is where each rule was settled, but the rules are not
trio-specific: read it before writing or editing prose on **any** accgram page. Same problem as
the pointer above — nothing referenced it, so it was discoverable only by already editing the
file it governs.

One of those conventions is a claim about Hebrew accentuation rather than about this repo:

**Maqaf is the last rung of one scale.** Disjunctives, then conjunctives, then maqaf — a maqaf
separates the word it sits on from the next even less than a conjunctive does, so it carries the
weakest *separating* force on the scale. (Never write a bare "weakest": a maqaf *binds* tightest,
so unqualified it reads as backwards.) There is no second ledger for "word division". A maqaf
difference is counted **once**, at the word whose marking changed, never as a regrouping plus an
accent; and it is stated as an **exchange with both marks named** — "a maqaf where its Wikisource
strand has a merkha" — never as the absent maqaf alone. Do not define a maqaf as "the atom left
blank of an accent": that is only the normal case, and `koren_dt_elyon`'s `mun-mun` on לא־תעשה is
a maqaf compound whose joined atom keeps its munaḥ — as are the Simanim Tiqqun's two munaḥ-on-לא.
But do not swing the other way either: in the **prose** system a second accent on a compound is
rare, and is with very few (perhaps zero) exceptions just a consequence of the compound being one
chanted word — the accents found there are the ones that can be the first of two on an atomic
word (the metigah of metigah-zaqef, perhaps a few munaḥ). The **poetic** system is far more
willing to put two accents on one chanted word; that asymmetry is a major difference between the
systems, not a detail. `edition_transcription`'s "HOW RARE THAT IS IN PROSE" paragraph has it with
its Breuer citations. The verbatim reader-facing statement is
`MAQAF_IS_THE_LAST_RUNG`; its guardrail comment records the convention it replaced (a 2026-07-25
audit fix that made maqaf differences non-differences) and why that one was wrong, so it does not
get reinstated. Issue #76.

## Running tests

From the **repo root**, with the venv's own interpreter (the system Python has neither pytest
nor PLY):

```bash
.venv/Scripts/pytest.exe py/tests
```

## Writing tests — differential and lint-shaped only

`doc/agent-planning-principles.md` §"Generated Outputs Are the Tests" is the full rule with
its evidence. In short: **do not add a test file or test case unless it is one of the two
shapes that have actually found things here**, or I ask for it.

- **Differential check against an independent oracle** — the PLY parity comparator against the
  frozen C checker, the Decalogue transcriptions against their vendored strands.
- **Mechanical lint over the tree** — `py/tests/test_transliterations.py` (#26).

Everything else: regenerate the tracked JSON/HTML with the real CLI command and read the diff.
That is the test. Do not write an example-based unit test that pins one hand-picked case, a
string, or a name — no such test is recorded as ever having caught anything in this repo, and
they all have to be dragged through every terminology rename.

**A missing input must FAIL, never skip.** `25a7800` removed twenty-one skip guards that
reported green having verified nothing. Skips are a *semantic* channel in this suite (a skip
reports that a page diverges from its strand), so an environment skip mixed in corrupts the
signal. An empty `@parametrize` list also reports as a skip — hence the `or ["(none
committed)"]` fallbacks, which are the failure mechanism and must stay.
