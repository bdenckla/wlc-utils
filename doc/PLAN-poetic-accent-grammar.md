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

**Phase 2 DONE** (MAM-simple cross-check + the one safe scanner fix):
- `py/accgram/mam_poetic_accents.py` — extracts the ordered *disjunctive* sequence
  from MAM-simple's pointed Unicode (legarmeh/shalshelet-gedolah via the
  `lp-legarmeih` paseq node; revia/oleh/etc. by combining accent). Servi dropped
  (L and MAM pick different conjunctive signs; no oracle for servus chains).
- `py/accgram/xcheck_poetic.py` + `xcheck-poetic` subcommand → writes git-tracked
  `out/accgram/ply-poetic/_mam_xcheck.txt` (per-book agreement + every divergence
  grouped by difflib edit signature, each flagged parses/NO_PARSE). The Phase 2
  verification surface.
- **Scanner fix landed:** `_recover_unmarked_oleh` — when L drops the ole sign
  (#363; user-confirmed LC habit) leaving only the yored merka, a galgal servus
  (93) immediately before the bare merka recovers it as OLEH_WEYORED. Oracle-
  validated: +9 agreement, **0 new disagreements**. The "revia precedes" variant
  is left unrecovered (its signal breaks ~1400 verses; see the helper docstring).
- Result after fix: parse **ps 2426/2527, pr 898/915, jb 1003/1023; total
  4327/4465 (96.9%)**; MAM agreement **4392/4465 (98.37%)**, 73 divergences.
- **Divergence taxonomy** (the 73): only the dropped-oleh class was a scanner bug.
  The rest are *faithful-to-L* and split into: missing silluq (13, = category A);
  dehi⇄munah/tarḥa (L vs MAM differ on dehi, ~25); legarmeh⇄plain-paseq (L vs MAM
  differ on paseq, ~19); revia present/absent (~8); the remaining unrecovered
  dropped-oleh (revia-precedes, ~7); one missing atnah. These are real L/MAM
  textual differences, not scanner errors — document, do not "correct" in-scanner.
- **book-of-job cross-validation:** `../book-of-job` is a critical review of BHQ
  (vs BHS/WLC/UXLC/manuscripts; thesis: BHQ barely improves on BHS). The Job dehi
  divergences were checked against its `out/enriched-quirkrecs.json` (the
  `zdexiWLC` "טרחא not דחי" etc. quirk records). 6 reproduced and directionally consistent (e.g. Job 6:17 "דחי
  not מונח" ↔ checker WLC-extra-DEHI). 31 book-of-job dehi quirks are invisible to
  this checker because **WLC already fixes a BHS *transcription* error (tarḥa→deḥi)**
  — WLC began as a near-perfect copy of BHS and corrects these, flagging them with
  `]c` (e.g. `13YOWM]c` in Job 3:3). This is transcriptional, NOT a manuscript
  defect: the LC mark should be transcribed grammar-sensitively as deḥi (a
  disjunctive in that slot), which BHS got wrong and WLC corrected — exactly the
  distinction a grammar-aware checker exists to make. 2 checker-only dehi cases
  book-of-job's set omits: Job 5:27 (WLC dehi vs MAM tarḥa) and Job 31:26 (WLC
  tarḥa `73` vs MAM deḥi — a BHS transcription error WLC did NOT fix?) — worth a look.
- Next: **Phase 3** (structural tail: missing-silluq A, legarmeh-under-atnah B,
  pazer-before-silluq C, singletons D — per the open decisions below).

Built and tested (full suite: 51 passing):
- `py/accgram/ply_scanner_poetic.py` — M-C accent codes → poetic tokens.
- `py/accgram/ply_grammar_poetic.py` — PLY grammar; **zero LALR conflicts**.
- `py/accgram/mam_poetic_accents.py` — MAM-simple → poetic disjunctive sequence.
- `py/tests/test_ply_scanner_poetic.py`, `py/tests/test_ply_poetic_grammar.py`,
  `py/tests/test_mam_poetic_accents.py`.

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
4. **Token-type names are constants, not literals.** All poetic token-type strings
   live in `py/accgram/poetic_accent_names.py` (the single source of truth);
   grammar/scanner/MAM-extractor/tests import and reference them — never re-type the
   literal. (PLY's `p_*` rule docstrings are the one forced exception: PLY parses
   them textually, so terminals are spelled literally there and the `tokens` tuple +
   parse/conflict tests keep them pinned.) Spellings follow the canonical names in
   `py/mb_diff_mpu/describe_diff.py`, uppercased with its `ḥ` written **X**: DEXI,
   MUNAX (deḥi/munaḥ), TSINNOR, MERKHA, MAHAPAKH. Maintainer overrides of
   describe_diff: **ATNAX** (it calls the accent "etnaḥta"), **TARXA** (its plain
   "tarha" is a bug — ḥet takes X), **ILLUY** (doubled L over "iluy"); OLEH_WEYORED
   keeps "we-" (no `veyored` precedent). Poetic intentionally diverges from the
   prose Goerwitz grammar (ATNACH/MUNACH/MEREKA/MAHPAK/TIFCHA), a frozen C-oracle
   port. Tree *outputs* are unaffected (they use lowercase `_LEAF` display names +
   nonterminal labels); only the `NO_PARSE:` diagnostic lines show the spellings.

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

## Phase 2 — MAM-simple cross-check + scanner fixes  — DONE (see Status above)

Goal: confirm the trees' segmentation is *correct*, not just parseable, and fix
scanner bugs it surfaces.

Outcome: the disjunctive cross-check (`mam_poetic_accents` + `xcheck-poetic`)
validated 98.37% of verses against MAM-simple. The only true scanner bug surfaced
was the galgal-adjacent dropped oleh-we-yored, now fixed and oracle-validated; the
other ~64 divergences are genuine L/MAM textual differences (faithful to L) and are
documented in the Status taxonomy, not corrected in the scanner. Of the original
"known suspects" below, only the unmarked-ole one was real-and-fixable from L alone;
the yored-on-next-word (maqqef) and shalshelet-qetannah suspects did not surface as
disjunctive-level errors against MAM and are left as-is.

- MAM-simple is the sibling repo `../MAM-simple` (all repos sit flat under
  `GitRepos/`); poetic data is `json-vtrad-bhs/{Ps,Prov,Job}.json`. **Loading is
  already built** — the prose `research-oddballs` workflow integrates it:
  `mam_simple_verse.load_mam_simple_for_refs` (+ `default_mam_simple_dir` =
  `repo_root.parent/MAM-simple/json-vtrad-bhs`) and `mam_simple_diff.py`. Reuse
  these for the poetic cross-check rather than rebuilding the loader.
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
