# PLAN — Flag a stranded `82` (zarqa stress-helper without its `02`) as a lexical oddball

Status: **DONE 2026-06-12.** Executed: new `accgram/lexical_validation.py` +
`run_ply` wiring; all 12 zarqa-on-lamed verses now emit the uniform
`illegal_mark`/`ERROR` tree; oddball total 86→91 (+5); ob_notes for the 5 new refs
added (incl. new `ob_notes_gn.py`); "seven"→"twelve" wording fixed and the
`_NU_2019_01` puzzlement resolved; `test_ob_notes_equivalence` baseline rebased to
91; full suite green (29 passed). Cascade step 6 (C-oracle parity) was a no-op: no
`out/accgram/goerwitz/` artifact is active. Created 2026-06-12.

## Decision (settled — not an open question)

**Treat a prose `82` that is not fused with a following `02` on the same atom as an
intrinsic *lexical* error ("alphabet error"), independent of surrounding context,
so that all 12 such verses are flagged as oddballs uniformly.** Today only 7 of the
12 are flagged, and only by accident (see Root cause). This diverges from the
goerwitz C oracle, which swallows the stray `82` — the same kind of deliberate,
documented extension already made for `MISSING_SOFPASUQ` and the tevir/tifcha
recoveries. Per `doc/agent-planning-principles.md`, the regenerated artifacts are
the test.

**Scope: `82` only, and prose only.** The sibling stress-helpers (`44`, lone `24`)
and the unknown codes (`11`/`12`) are deliberately *out of scope* here — they need a
scholarly call and are tracked in a separate GitHub issue. `82` is the only
high-volume, unambiguously-wrong case (12 occurrences, all errors).

**Prose-only is intentional and burns no bridge.** A bare `82` is *valid* in the
poetic accent system (it is tsinnorit, >200 uses). The genre split already happens
upstream (`accgram/prose_filter.py` strips Psalms/Proverbs/poetic-Job before
scanning), so within this pipeline a bare `82` is unconditionally illegal. A future
poetic checker is expected to have **its own lexer** (the maintainer confirmed
"start from scratch even with its own lexer" is acceptable), where `82` is a
first-class token. Therefore the prose scanner/validator may hard-code prose
semantics with no genre parameter.

## Root cause (precise, already analyzed)

- `82` is a *stress-helper*: well-formed only as the left half of `82{TEXT}02` on one
  atom, where it fuses into a single `ZARQA` token
  (`accgram/ply_scanner.py:90`, `_TEXT = [^ \r\n\-]*` keeps the pair inside one
  maqaf/space-delimited atom). See `py/py_wlc_json_and_unicode/wlc_uword.py:180`.
- When there is no `02` on the atom, the `82` falls through to the swallow rule
  `35|75|95|44|05|82|52 -> None` (`accgram/ply_scanner.py:113`) and **emits no
  token at all** — the intended accent simply vanishes from the stream.
- An oddball is any verse whose PLY tree contains an `ERROR` leaf
  (`accgram/oddballs.py:9,29`; classified by `accgram/ply_classify.py`). With the
  `82` silently gone, whether the verse becomes an oddball depends entirely on
  whether the *rest* of the accent sequence still parses:
  - It still parses (NOT flagged) when the now-accentless word was governed only by
    re-absorbable material — nothing, plain conjunctives (`munach`/`mereka`), or a
    `revia` that may sit directly before segolta. **5 cases.**
  - It fails (flagged, via incidental error recovery) when the deleted zarqa was the
    head of a **geresh / azla-geresh** sub-clause (or a lone azla): a geresh-clause
    must head a revia/zarqa/pashta/tevir phrase and can never attach to the
    following segolta/zaqef, so it is left dangling. **7 cases.**

The 7-vs-12 split is therefore **not** a property of WLC's error (all 12 are equally
wrong); it is an artifact of downstream parse luck. This resolves the open note
`_NU_2019_01` in `accgram/ob_notes_nu.py:37-40`.

### The 12 verses (audited against the genre-filtered prose corpus)

Source: `wlc-utils-io/in/wlc422/wlc422_ps.txt`. Each has the `82` immediately before
a final lamed (except gn 17:20, where it is *two* letters back — the
"more than one letter too far back" case named in `_NU_2019_05`).

| ref | word | currently | preceding the deleted zarqa |
|---|---|---|---|
| gn 17:20 | Ishmael | **ok** | (nothing — bare) |
| gn 47:29 | Israel | **ok** | munach |
| ex 6:6 | Israel | ERROR | gershayim (+mereka) |
| ex 30:12 | Israel | ERROR | gershayim |
| ex 36:2 | Betzalel | **ok** | munach revia |
| lv 4:2 | Israel | ERROR | gershayim + munach |
| lv 20:2 | Israel | **ok** | munach |
| nu 20:19 | Israel | ERROR | azla + mereka |
| dt 14:24 | tukhal | **ok** | munach munach |
| dt 31:7 | Israel | ERROR | azla geresh + munach |
| js 4:8 | Israel | ERROR | azla geresh → revia |
| js 10:30 | Israel | ERROR | telishaqetanna azla geresh |

The 5 currently-**ok** verses (gn 17:20, gn 47:29, ex 36:2, lv 20:2, dt 14:24) are
the ones this plan newly flags. (Reproduce the audit with the one-off script in the
resolving session, or re-derive: for each kept prose verse, split the body on space
and `-`, and flag any atom whose code list contains `82` with no later `02`.)

## Fix approach (recommended)

Detect the stranded `82` in a **new prose lexical-validation layer** and
short-circuit the verse to a uniform `ERROR` tree — do **not** route it through the
grammar (it is an alphabet error; the context need not be parsed). This keeps the
faithful C-port scanner/grammar untouched and reuses the entire existing
oddball-reporting pipeline (which only looks for an `ERROR` leaf in `*_ag.txt`).

Concretely (per `doc/agent-planning-principles.md` "prefer new files"):

1. **New module `accgram/lexical_validation.py`.** A pure function, e.g.
   `stranded_stress_helpers(body: str) -> list[StrandedMark]`, that re-derives the
   per-atom 2-digit code stream (split body on `[ \-]+`, pair the digit runs) and
   returns each `82` with no later `02` in the same atom. Self-contained; no
   dependency on the scanner internals. (Keep it general enough that `44`/unknowns
   could be added later, but only wire up `82` now.)
2. **Wire into `accgram/run_ply.py::render_book`** (the per-verse emission point,
   `run_ply.py:36-52`). Before/instead of `parse_tokens`, if the verse body has a
   stranded `82`, emit a uniform fixed tree carrying an `ERROR` leaf and the
   reference line, e.g.
   ```
   Genesis 17:20
   0 illegal_mark
     ERROR
   ```
   (exact node name/leaf is a style choice; it must contain `\bERROR\b` so
   `accgram/oddballs.py` classifies it, and should be identical across all 12).
   Do not call the parser for these verses.
3. **Leave `accgram/ply_scanner.py` and `accgram/ply_grammar.py` unchanged** — the
   C-port faithfulness property is preserved; the new behavior is a prose layer on
   top. (The unused `UNKNOWN_ACCENT` token / `TILDE error UNKNOWN_ACCENT SOFPASUQ`
   rule remains dead for now; revisiting it belongs to the separate issue.)

Consequence to accept on purpose: the **7** verses that currently produce varied
grammar-derived `ERROR` trees will now produce the *same* uniform lexical-error
tree as the other 5. That is the point ("treat all 12 the same"), and it is an
improvement: the old trees pinned the error on a stranded geresh, not on the real
cause.

## Cascade (everything that must change / regenerate)

1. **`accgram/lexical_validation.py`** (new) + minimal wiring in
   `accgram/run_ply.py`. Module docstring: state the prose-only assumption and the
   intended divergence from the goerwitz C oracle.
2. **Regenerate PLY outputs:**
   `.venv/Scripts/python.exe py/main_accgram.py run-ply`
   → rewrites `out/accgram/ply/*_ag.txt` and `out/accgram/ply/_oddballs.json`.
   Expect: all 12 verses now carry the uniform lexical-error tree; the global
   oddball count rises by **+5** (the gn 17:20, gn 47:29, ex 36:2, lv 20:2,
   dt 14:24 additions); the 7 existing ones change tree shape.
3. **Regenerate research artifacts:**
   `.venv/Scripts/python.exe py/main_accgram.py research-oddballs`
   → rewrites `out/accgram/research-oddballs.json` and
   `gh-pages/accgram/goerwitz.html`.
4. **Oddball research notes (`accgram/ob_notes_*.py`).** These are keyed by ref and
   drive the research-oddballs output:
   - **Add entries for the 5 newly-flagged refs:** gn 17:20 (`ob_notes_gn.py`),
     gn 47:29 (`ob_notes_gn.py`), ex 36:2 (`ob_notes_ex.py`), lv 20:2
     (`ob_notes_lv.py`), dt 14:24 (`ob_notes_dt.py`). The three "Israel" ones
     (gn 47:29, lv 20:2) reuse `_ZARQA_WHIM` from `ob_notes_shared.py`; ex 36:2
     (Betzalel), dt 14:24 (tukhal), gn 17:20 (Ishmael) need their own `wlc_focus`
     strings (construct via the existing uword convention) but the same summary.
     (Check whether `ob_notes_gn.py` exists; create it + register it if not — follow
     how `ob_notes_js.py` is wired.)
   - **Fix the "seven" → "twelve" wording** now that all 12 are flagged:
     `ob_notes_shared.py::_ZARQA_WHIM` ("one of seven items of this type"),
     `ob_notes_nu.py::_NU_2019_01` (rewrite the "I would have expected 12 but only
     seven are" puzzlement to the resolved behavior) and `_NU_2019_07` ("one of
     seven oddballs"). Note `_NU_2019_05` already anticipates gn 17:20 (the
     "more than one letter too far back" case), which is now actually flagged.
5. **Verse-label regex sanity.** `accgram/oddballs.py::_OUTPUT_VERSE_LABEL_RE`
   (`oddballs.py:6-8`) must still match the reference line of the uniform tree —
   keep the emitted header identical in form to the normal `*_ag.txt` headers
   (e.g. `Genesis 17:20`), which step 2's format already does.
6. **Parity / oracle.** If a parity comparison against `out/accgram/goerwitz/` is
   still active, it will (intentionally) diverge for these 12 verses — re-baseline
   or re-scope it exactly as the `has_legarmeh` plan did (the corrected PLY output
   is the new baseline, not the C oracle).
7. **Tests.** Per `agent-planning-principles.md`, prefer the regenerated artifacts
   as the verification surface; add unit tests only if a pure-function check of
   `lexical_validation.stranded_stress_helpers` is wanted. Run the full suite
   (`py/tests`) to confirm nothing pinned (e.g. golden trees) broke.

## Verification

- `.venv/Scripts/python.exe py/main_accgram.py run-ply` then confirm in
  `out/accgram/ply/_oddballs.json`: all 12 refs present, each with the uniform
  lexical-error tree; oddball total moved by exactly +5; **no other verse** changed
  status (diff the JSON).
- `research-oddballs` regenerates `gh-pages/accgram/goerwitz.html` cleanly; the 5
  new refs render with notes; the "seven"/"twelve" wording is consistent.
- `.venv/Scripts/python.exe -m pytest py/tests -q` green.
- Spot-check one previously-ok (gn 47:29) and one previously-ERROR (lv 4:2) verse:
  both now show the identical lexical-error tree.

## Out of scope / notes

- `44` (3 standalone prose uses: gn 5:29, 2k 17:13, zp 2:15), lone `24` handling
  (currently emitted as `TELISHAQETANNA`, `ply_scanner.py:110` — maintainer is "not
  convinced that is what I want"), and unknown codes `11`/`12` → tracked in the
  separate GitHub issue, not here.
- A future **poetic** accent checker is expected to be a separate lexer+grammar; do
  not parameterize genre into the prose scanner for it.
- This is a behavior change → its own branch + commit.
- After landing, update the memory note in
  `.claude/projects/.../memory/` and delete/clear the resolved `_NU_2019_01`
  puzzlement.
