# PLAN — Fix the `has_legarmeh` book-name mismatch (discard goerwitz parity)

Status: **approved, not started.** Created 2026-06-12. Resume in a fresh session.

## Decision (settled — not an open question)

**Discard byte-for-byte parity with the goerwitz C binary for this issue, and
make `has_legarmeh` fire for all 17 of its passages.** Parity here was based on
*bad input data*: the new-format corpus feeds the scanner book-name headers
(e.g. `Levit`, `1Samuel`, `Daniel`) that do **not** match the abbreviation scheme
the C author's `passages[]` list expects (`Lev`, `1Sam`, `Dan`). The C binary
silently mis-fired on that data — only `Ruth` happened to match — so reproducing
its output faithfully reproduces a latent upstream defect. The author's stated
intent (tnk2acc.l comment) is that **all 17** munaḥ+paseq-not-before-revia
passages count as legarmeh; honoring that intent is the correct behavior, so the
divergence from the C oracle is intended and desirable.

This supersedes the parity goal in `doc/PLAN-option1-ply-parity.md` *for these 17
passages only*; the rest of the port stays as-is.

## Root cause (precise)

- The scanner builds the verse reference as `f"{book} {ch}:{vs}"`, where `book`
  is the chapter-head header line. That header is produced by
  `split_wlc.split_wlc_to_book_texts` → `cmn.wlc_book_codes.wlc_bb_to_goerwitz_book_name(bb)`,
  which returns `info.goerwitz_book_name or info.bk39id` — i.e. the `mb_cmn`
  `bk39id` constants (`BK_LEVIT="Levit"`, `BK_FST_SAM="1Samuel"`, …).
- `accgram/ply_scanner.py::HasLegarmeh._PASSAGES` is a verbatim copy of the C
  `passages[]` array, which uses a *different* abbreviation scheme.
- The two schemes coincide only for `Ruth`, so `has_legarmeh` fires for exactly
  one verse (Ruth 1:2) across the whole corpus. This is documented in the
  `accgram/ply_scanner.py` module docstring (the "Quirk reproduced" note).

### The 17 passages: C list key → actual scanner-emitted location

| # | C `passages[]` key | scanner emits | matches today? |
|---|---|---|---|
| 1 | `Gen 28:9`   | `Genesis 28:9`      | no |
| 2 | `Lev 10:6`   | `Levit 10:6`        | no |
| 3 | `Lev 21:10`  | `Levit 21:10`       | no |
| 4 | `1Sam 14:3`  | `1Samuel 14:3`      | no |
| 5 | `1Sam 14:47` | `1Samuel 14:47`     | no (counter passage) |
| 6 | `2Sam 13:32` | `2Samuel 13:32`     | no |
| 7 | `2Kgs 18:17` | `2Kings 18:17`      | no |
| 8 | `Isa 36:2`   | `Isaiah 36:2`       | no |
| 9 | `Jer 4:19`   | `Jeremiah 4:19`     | no |
| 10 | `Jer 38:11` | `Jeremiah 38:11`    | no |
| 11 | `Jer 40:11` | `Jeremiah 40:11`    | no |
| 12 | `Ezek 9:2`  | `Ezekiel 9:2`       | no |
| 13 | `Hag 2:12`  | `Haggai 2:12`       | no |
| 14 | `Ruth 1:2`  | `Ruth 1:2`          | **yes** (the lone coincidence) |
| 15 | `Dan 3:2`   | `Daniel 3:2`        | no |
| 16 | `Neh 8:7`   | `Nehemiah 8:7`      | no |
| 17 | `2Chr 26:15`| `2Chronicles 26:15` | no |

(Forms confirmed by grepping `out/accgram/ply/wlc_422_ps_*_ag.txt` verse headings,
which equal the `location` string passed to `has_legarmeh`.)

## Fix approach

Two options; **recommend Option B.**

- **Option A (minimal):** rewrite `_PASSAGES` to the scanner-emitted forms in the
  table above. One-line-per-string change, preserves order. Downside: couples the
  list to display-name idiosyncrasies (`Levit`, `1Samuel`) and to string
  formatting (`f"{book} {ch}:{vs}"`, single space); brittle if either changes.

- **Option B (robust, recommended):** key the 17 passages on **structured book
  refs**, not formatted strings. Store `_PASSAGES` as `(wlc_bb, chnu, vrnu)`
  tuples (e.g. `("lv", 10, 6)`), thread the `bb`/`chnu`/`vrnu` to `has_legarmeh`
  instead of (or alongside) the formatted `location`, and compare structurally.
  `cmn.wlc_book_codes` is already the single source of truth for `bb`; this
  decouples legarmeh detection from header spelling entirely. Keep the
  `count`/`old_i` "Jewish order" monotonic-counter logic and the 1Sam 14:47
  "second occurrence only" rule unchanged (book order is preserved).

Either way, after the fix verify all 17 locations resolve `74{TEXT}05`-not-before-
revia to `LEGARMEH`.

## Cascade (everything that must change / regenerate)

1. **`accgram/ply_scanner.py`** — the fix itself (`_PASSAGES` + possibly
   `HasLegarmeh.__call__`/`scan_accents`/`scan_book` signatures for Option B).
   Update the module docstring: the "only Ruth fires" quirk is gone.
2. **`py/tests/test_ply_scanner_lookaheads.py`** — rewrite the assertions that
   encode the *current* behavior: `test_munach_when_paseq_not_before_revia_outside_has_legarmeh_passage`,
   `test_has_legarmeh_fires_only_at_matching_location`,
   `test_has_legarmeh_1sam_14_47_second_occurrence_only`,
   `test_has_legarmeh_plain_passage_fires_first_time`,
   `test_has_legarmeh_old_i_is_monotonic`. They use the abbreviated keys and the
   "only Ruth in new format" premise; both change.
3. **Regenerate outputs:**
   - `.venv/Scripts/python.exe py/main_accgram.py run-ply`
     → rewrites `out/accgram/ply/*_ag.txt` and `_oddballs.json`,
     `_parity_report.json`, `_troublemakers.json`.
   - `.venv/Scripts/python.exe py/main_accgram.py research-oddballs`
     → rewrites `gh-pages/accgram/goerwitz.html`.
   - Lev 10:6, Lev 21:10, and the other ~13 currently-oddball
     "⅃-leg…non-revia" verses should drop out of the oddball set; the oddball
     count moves off 100. Confirm exactly which of the 15 resolve (legarmeh may
     not be the only problem in some) and re-baseline.
4. **Parity test / oracle** — the parity comparison against `out/accgram/goerwitz/`
   will now (intentionally) diverge for these verses. Retire or re-scope it: per
   the decision, the corrected PLY output is the new baseline, not the C oracle.
5. **Open Issues section** — `accgram/rtmsr_open_issues.py` and `accgram/xx_data.py`:
   the `_ITEM_FOI_NON_REVIA` framing ("15 of 17 are oddballs; only Daniel 3:2 and
   Ruth 1:2 are not") becomes obsolete once all 17 fire legarmeh. The Ruth-1:2 vs
   Daniel-3:2 contrast trees added on 2026-06-12 also change (Daniel 3:2's mark
   becomes a legarmeh too), so that contrast dissolves. Rewrite or remove the item
   and its trees. Also revisit the per-verse oddball comments in
   `accgram/xx_data.py` / `rtmsr_open_issues.py::non_revia_comment` that cite the
   "15 oddballs / only 2 not" counts.
6. **Golden test** — `py/tests/test_ply_tree_golden.py` pins Obadiah 1:2 only
   (unaffected), but run the full suite to confirm.

## Verification

- `.venv/Scripts/python.exe -m pytest py/tests -q` green after test rewrites.
- Spot-check trees: Lev 10:6 / Lev 21:10 now parse (no `ERROR`) with a
  `legarmeh_phrase` node; all 17 locations fire exactly the intended legarmeh
  count.
- Diff the regenerated `_oddballs.json` to confirm only the expected verses left
  the oddball set, and `log()`/note any of the 15 that did **not** resolve (so the
  reduction isn't silently overstated).

## Out of scope / notes

- The scholarly-comment restoration in `accgram/ply_grammar.py` (2026-06-12) is
  unrelated and already committed/landed; leave it.
- This is a behavior change → its own branch + commit, separate from the
  docs-only work that preceded it.
- If desired, also reconcile the `bk39id` display forms (`Levit`, `1Samuel`) with
  the C header expectations — but that is cosmetic and not required by this fix.
