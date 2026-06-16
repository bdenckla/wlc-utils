# Plan: Poetic (Three Books) Accent Grammar — Validation & Corpus Run

Handoff for a fresh session. The *scanner + grammar* exist and parse 96.4% of
Psalms+Proverbs; this plan covers the corpus run over all three books, validation
against MAM-simple, and resolving the structural tail. Read this top-to-bottom,
then start at "Phase 1".

The phases below are verification checkpoints, not size-budgeted chunks (see
`doc/agent-planning-principles.md` → "Size Phases to Natural Boundaries"): a
session can carry several in one go — the boundaries just mark where to
regenerate outputs and confirm before moving on.

## Status (2026-06-16)

**Phase 1 DONE** (commit `poetic corpus driver + run`): driver + corpus run landed.
- `py/accgram/poetic_filter.py` — inverse of `prose_filter` (ps/pr + poetcant Job).
- `py/accgram/ply_scanner_poetic.py::scan_book` — book text → Verses, clean
  `bk39id` references ("Job", not "Defeatmatchforjob").
- `py/accgram/run_ply_poetic.py` + `run-ply-poetic` subcommand → writes
  `out/accgram/ply-poetic/wlc_422_ps_{ps,pr,jb}_ag.txt` (git-tracked). Unparseable
  verses are non-fatal `NO_PARSE: <token types>` lines (greppable), tallied.
- Run: **ps 2421/2527 (95.8%), pr 897/915 (98.0%), jb 1001/1023 (97.8%); total
  4319/4465 (96.7%)**. 146 NO_PARSE = the structural tail (categories A–D below).
- Next: **Phase 2** (MAM-simple cross-check + scanner fixes).

Built and tested (full suite: 42 passing):
- `py/accgram/ply_scanner_poetic.py` — M-C accent codes → poetic tokens.
- `py/accgram/ply_grammar_poetic.py` — PLY grammar; **zero LALR conflicts**.
- `py/tests/test_ply_scanner_poetic.py`, `py/tests/test_ply_poetic_grammar.py`.

Derived from Yeivin, *Introduction to the Tiberian Masorah* (ITM) §358–374, and
the M-C accent table `wlc-utils-io/in/wlc420/supplmt.wts` (column II = poetic),
cross-checked against decoded L verses.

Baseline parse rate (ad-hoc script over `wlc-utils-io/in/wlc422/wlc422_ps.txt`,
`ps`+`pr` only): **3318/3442 = 96.4%** (ps 95.8%, pr 98.0%). Job not yet run.

## Design invariants (do not regress these)

1. **Strict clause hierarchy + permissive servus chains.** Clause rules encode
   Yeivin's disjunctive hierarchy strictly; every `D_phrase : D | servi D` accepts
   any conjunctive run, because Yeivin describes poetic servi loosely and there is
   no C oracle. Keep this split. Do not re-enumerate exact servus patterns unless
   a real error-detection need emerges from MAM cross-check.
2. **Zero LALR conflicts.** After any grammar edit, run
   `build_parser(capture_warnings=True)` and assert the log is empty
   (`test_builds_without_conflicts` already does this).
3. **Scanner code facts** (grounded in decoded verses — see the scanner docstring
   and `[[poetic-ply-grammar]]` memory): legarmeh = `63|70`+`05`; revia mugrash =
   `11`(+`81`); oleh-we-yored = `60`(+`71` yored, folded in); oleh servus = `93`
   galgal (not atnah-hafukh); dehi = `13`; sinnor = `02`. Bare `81` reclassified:
   next disjunct oleh → revia qatan; next silluq → revia mugrash w/o geresh; else
   revia gadol.

## Remaining-failure taxonomy (the ~3.6%, all real oddballs)

A. **13 verses lack any silluq code** (e.g. ps 37:31 `…):A$URFY/W00`). Parallels
   the prose missing-silluq case, which prose handles with an `error`-token ERROR
   leaf; poetic has **no error productions yet**.
B. **legarmeh directly under atnah** (ps 5:5 `LEGARMEH ATNACH SILLUQ`): atnah's
   only modeled subdividers are dehi/revia gadol.
C. **pazer directly before silluq** in short superscriptions (ps 18:2, 30:1
   `PAZER SILLUQ`): silluq's modeled near-dividers are revia mugrash / shalshelet
   gedolah only.
D. Long-tail singletons (e.g. ps 3:1 `ATNACH REVIA_MUGRASH LEGARMEH SILLUQ`) —
   inspect case-by-case; may be scanner misfires (a `11` mis-read) rather than
   grammar gaps.

## Open decisions (maintainer's call — do not presume)

- **Missing silluq (A):** inject an implied SILLUQ in the scanner (clean parse) vs.
  emit an ERROR/oddball mirroring prose. The prose system treats these as ERROR
  oddballs; matching that is the conservative default, but poetic has no oracle.
- **revia trichotomy:** keep three distinct tokens (current) vs. one REVIA token
  with gadol/qatan/mugrash inferred purely from tree position. Current approach
  works; only revisit if MAM cross-check shows misclassification.
- **Tests vs. generated outputs:** per `doc/agent-planning-principles.md`, once a
  poetic driver writes git-tracked tree outputs, those outputs become the primary
  verification surface; the unit tests can stay as fast guards.

## Reference: the prose workflow to mirror

- Driver `py/accgram/run_ply.py` (via `py/main_accgram.py run-ply`) reads
  `wlc-utils-io/in/wlc422/wlc422_ps.txt`, applies `prose_filter.should_keep_line`,
  scans+parses each verse, writes `out/accgram/ply/wlc_422_ps_<bb>_ag.txt`.
- `py/main_accgram.py research-oddballs` → `out/accgram/ply/_oddballs.json`,
  `out/accgram/research-oddballs.json`, `gh-pages/accgram/goerwitz.html`
  (`py/accgram/oddballs.py`, `py/accgram/research_tao.py`).
- `prose_filter.should_keep_line` already classifies poetic vs prose
  (`tbn.is_poetcant`, and excludes `ps`/`pr` wholesale) — the poetic filter is its
  inverse.

---

## Phase 1 — Poetic driver + corpus run (establish the verification surface)

Goal: a driver that runs the poetic scanner+grammar over the **three books**
(Psalms, Proverbs, and the poetic core of Job) and writes git-tracked tree
outputs, recording unparseable verses rather than crashing.

- New module `py/accgram/poetic_filter.py`: `should_keep_line(bb, chnu, vrnu)` =
  the inverse of `prose_filter` — keep `ps`, `pr`, and poetic-cantillation Job
  verses; reuse `mb_cmn.bib_locales.is_poetcant` exactly as `prose_filter` does.
- New module `py/accgram/run_ply_poetic.py` modeled on `run_ply.py`: split via
  `split_wlc.split_wlc_to_book_texts(..., keep_line_fn=poetic_filter.should_keep_line)`,
  scan with `ply_scanner_poetic.scan_verse`, parse with `ply_grammar_poetic`.
  **Unlike prose, an unparseable verse is NOT fatal** — emit the reference line
  plus a placeholder marker (e.g. a `NO_PARSE` line) and tally it, so the run
  completes and the failures are inspectable in the tracked output.
- Wire a `run-ply-poetic` subcommand into `py/main_accgram.py`.
- Output dir `out/accgram/ply-poetic/` (keep separate from prose `ply/`).

Verification: run the real command
`.venv/Scripts/python.exe py/main_accgram.py run-ply-poetic`; confirm per-book
parse counts (expect ~96% ps/pr; Job is new — note its rate), and eyeball a few
trees (Ps 1:1, 3:3, 37:28) against the structures in this plan. Commit the
tracked outputs so later phases diff against them.

Handoff: parse rate per book recorded; Job rate known; failure list captured in
the output.

## Phase 2 — MAM-simple cross-check + scanner fixes

Goal: confirm the trees' segmentation is *correct*, not just parseable, and fix
scanner bugs it surfaces.

- Locate MAM-simple (the user references `MAM-simple/json-vtrad-bhs/…`; it is NOT
  in this repo — find or obtain it; `prose_filter.py` comments cite its path).
- For a structurally diverse sample (verses with oleh-we-yored, two revias before
  silluq, dehi under atnah, sinnor before oleh, nested pazer/legarmeh), compare
  the poetic tree's implied division points against MAM-simple's accents. The user
  notes MAM **always supplies the revia** even where L omits it under a geresh
  muqdam — a good check that the `11`(+implied `81`) handling is right.
- Fix scanner edge cases this surfaces. Known suspects from the build:
  - oleh-we-yored whose ole is unmarked (only the yored merka written, when a
    revia precedes — §363): currently its yored is read as a servus.
  - yored merka on the *next* word (maqqef cases, §363): the `60…71` same-word
    rule misses it.
  - shalshelet qetannah (the conjunctive, 8 verses) is currently swallowed.

Verification: regenerate `out/accgram/ply-poetic/` and diff; cross-checked verses
match MAM-simple; document any intentional divergences.

Handoff: scanner correctness validated on a sample; bug fixes landed; outputs
regenerated.

## Phase 3 — Resolve the structural tail

Goal: drive the parse rate toward ~100% or convert each residual to a documented
oddball, deciding the open questions above per category.

- A (missing silluq, 13 verses): implement the chosen approach (implied-silluq
  injection vs. ERROR/oddball). If ERROR, add poetic error productions modeled on
  the prose `error`-token rules (`ply_grammar.py` §"error recovery").
- B (legarmeh under atnah): if MAM confirms it is well-formed, add
  `legarmeh_atnach_clause` (and likely `pazer_atnach_clause`) so atnah, like
  silluq, admits the lower dividers directly. Re-check zero conflicts.
- C (pazer before silluq): add `pazer_silluq_clause` (and reconsider whether the
  silluq domain should admit pazer/legarmeh directly, as in superscriptions).
- D: inspect singletons; fix scanner misfires or add narrowly-scoped rules.

Verification: regenerate outputs; parse rate reported; every remaining non-parse
is listed with a one-line reason. Re-run the unit tests.

Handoff: residual oddball set enumerated and explained.

## Phase 4 — Oddball report (optional, mirrors prose)

Goal: a poetic analogue of `research-oddballs` — JSON + HTML enriching each
remaining oddball with its verse object, for review.

- Mirror `oddballs.py` / `research_tao.py` for the poetic outputs; new
  `run-ply-poetic-oddballs` subcommand; write
  `out/accgram/ply-poetic/_oddballs.json` and a `gh-pages/accgram/poetic.html`.

Verification: run the command; inspect the HTML report.

Handoff: reviewable poetic oddball report; project state written back here.
