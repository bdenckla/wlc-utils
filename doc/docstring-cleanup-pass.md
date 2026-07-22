# Docstring/comment cleanup pass — decisions log

Goal: trim redundancy between a module's comments/docstrings and the prose that module
actually **emits** into generated HTML — **without changing the generated HTML**.

This log was originally scratch (`.novc/docstring_cleanup_pass.md`, gitignored), which is
why round 2 nearly evaporated: round 1's own "follow-up candidates" list was the only
record that two prose modules had been skipped on a technicality. It now lives here,
tracked.

## Rules in force

- Cut only clear **output-restatements**: a docstring/comment that repeats, in substance,
  text the module prints a few lines below.
- When a line is ambiguously **map-or-copy** — it might be the module's one-place synopsis
  rather than a duplicate — **keep it and record the judgment**. Most of this log is
  things deliberately *not* cut, and why.
- Preserve invisible-in-output material unconditionally: why, constraints, provenance,
  cross-page/cross-repo pointers, algorithm notes, editorial history.
- The most valuable find is not redundancy but **stale drift** — a comment asserting a
  number or fact the code computes live. Hunt for that shape specifically.

## The safety invariant (mechanical — after every edit)

1. `.venv/Scripts/python.exe py/main_accgram.py generate-html`
2. `git status --porcelain gh-pages/accgram` must be **empty**. Any output means rendered
   prose changed — revert that edit.
3. Establish the baseline *before* editing: `generate-html` must already be byte-identical
   to committed `gh-pages`.
4. `.venv/Scripts/python.exe -m pytest` at baseline and at the end.
5. black the touched files only.

---

# Pass A — the printed-decalogue / doc-notes / exhibit / prose-report core

Scope: 15 files in 4 sub-passes.
Baseline: `generate-html` byte-identical to committed gh-pages (verified).

## A1 — printed decalogue

### printed_decalogue_koren_page.py

Rendered HTML has NO "Yitro"/"reprint\*" — all 4 occurrences are invisible drift.

CUT / DE-STALE:

- docstring L12: dropped stale "(Yitro)" + "printed twice"; kept the finding-map and the
  editorial why (body asserted-not-transcribed). "printed twice"/"reprinted" was
  semantically wrong: the appendix prints the *other strand* (elyon), not a re-print.
- docstring L35 terminology bullet: "reprinted separately" → "printed separately" (kept
  the running-text/appendix/body/note distinction — a constraint).
- const comment L90–92: de-staled and trimmed (constant names + filenames already encode
  taxton/elyon and running-text/appendix).
- `_body_scans` docstring L199–202: CUT the strand/page restatement (verbatim in the two
  figcaptions four lines below — the flagship "comment next to the literal" case); kept
  only the invisible why (these scans are the evidence against the page's assertion
  elsewhere).

KEEP + NOTE (unsure map-vs-copy, per the conservative rule):

- docstring L15–24 (the "one note / more-for-fun" intro and the A38 bullet): restates the
  note section, but reads as the module's one-place synopsis/map. Candidate for a future
  more-aggressive pass.

### printed_decalogue_simanim_page.py

Output *does* use "(Yitro)" here, so that is not stale (it was koren-specific). Only the
two local paraphrase spots trimmed, parallel to koren:

- `_body_scans` docstring: cut the strand/page restatement (present in captions + intro),
  kept the editorial history ("replaced the old apology").
- const comment for `_P*_BODY_IMG`: cut the p.83/p.246 strand mapping (encoded in the
  constant names + filenames), kept the "distinct from the two note scans"
  disambiguation.

KEEP: the big module docstring — mostly the "three term pairs kept strictly apart" plus
side-margin-vs-footnote constraints (gold constraint material) and four-strands
provenance. The two note bullets (L8–14) restate the note sections but are the one-place
synopsis.

### printed_decalogue_page.py

**No cuts.** Comments/docstrings are entirely algorithm (letter-balancing, column
derivation), data-drift guards, the silluq-vs-meteg strip rule, bidi/`<bdi>` rules,
CSS-choice rationale, the CTR-aside "on the web" guardrail, and cross-page conventions —
all invisible-in-output why/constraint. No restatement of emitted prose found.

Result: HTML byte-identical, tests green. black reformatted koren (moved a closing `"""`
to its own line — no string-value change; HTML re-verified identical).

## A2 — doc notes: no cuts (all four files)

- `telg_doc_notes.py`: module docstring = purpose map + sigil policy / the
  no-retype-combining-marks constraint (matches the global orphan-combining-mark rule) +
  byte-exact provenance; inline comments = `_REFS` ordering rationale ("order almost-errors
  presents them") + key-table construction conventions. Docstring para 2
  (companion/argues/translate) overlaps the emitted intro but is the one-place synopsis and
  adds the ps17v14-analogue cross-pointer → KEEP + NOTE.
- `telg_mam_doc_notes.py`: data module; docstring is pure provenance (verbatim from
  MAM-with-doc) plus the edit-the-generator-not-the-HTML convention. KEEP.
- `ps17v14_doc_notes.py` / `ps17v14_double_tsinnor.py`: thin replay shells — the prose lives
  in the `*_body` modules, so the docstrings (one-line content synopsis + byte-exact-replay
  provenance + cross-page links) have nothing to restate. KEEP.

No edits, so no regen needed; gh-pages untouched.

## A3 — exhibit pages

- `dual_under_bars_page.py`: **CUT.** The module docstring duplicated the emitted `_intro`
  almost word for word (paras 1–2). Trimmed to a map: kept filename/#53, the invisible
  cross-repo "design doc §2, UXLC-utils" pointer, the deliberate "draws no conclusion"
  stance, and an `_IMAGES` pointer; dropped the verbatim re-listing of the crops (present in
  the intro and in the `_IMAGES` labels).
- `almost_errors.py`: **no cuts.** CLI shell; the docstring is a charity/non-charity map +
  why-generated (live parse trees cannot drift) + architecture (shell / `_trees` / `_html`).
  The prose lives in `almost_errors_html.py`, which was **not in the approved file list** →
  flagged as a follow-up candidate. *(This is the gap pass B closes.)*
- `supplied_marks.py`: **no cuts.** The definitional paragraphs overlap the intro but carry
  invisible nuggets (own-page rationale; "a genuine error is the opposite case"; the
  paseq-not-tracked constraint) and are the one-place synopsis — not a verbatim copy. Inline
  comments are transliteration standard / live-cannot-drift / deep-link rationale.
  KEEP + NOTE.

Result: HTML byte-identical, black clean.

## A4 — prose report

- `rtms_report.py`: **no cuts.** No module docstring; the function docstrings and comments
  are rendering algorithm and data transform (dual-cant layout, leaf-column graying, URL
  expansion). No prose restatement. *(The prose lives one module over, in the `rtmsr_*`
  set — flagged as a follow-up candidate. This is the other gap pass B closes.)*
- `ob_page.py`: **no cuts.** Shared assembly core; the docstring is a pure architecture map
  and the comments are filter-script constraints. Emits controls and wrappers, not prose.
- `research_tao.py`: **no cuts.** No module docstring; a goerwitz.html orchestration driver;
  comments are data-flow/why. Emits no prose itself.
- `poetic_oddballs.py`: **one edit — the flagship stale-drift kind.** The module docstring
  hardcoded "the 13 verses" missing_silluq and "the 1 NO_PARSE (Job 31:15)", while the page
  computes and shows both counts live — and no_parse had drifted to 2 (Psalms 56:10 joined
  Job 31:15; ps56:10 is a known handled case, cf. the comment near line 548). De-counted
  both bullets: "the 13 verses" → "verses"; "the 1 NO_PARSE (Job 31:15)" → "an L anomaly …
  e.g. Job 31:15 and Psalms 56:10"; "a second such case" → "another such case". Substance
  and the ps17v14 provenance kept. The rest of the (large) docstring is a developer-facing
  architecture map (module names, row-key reference, issue refs) → KEEP.

Result: HTML byte-identical, black clean.

---

# Pass B — the two modules pass A skipped on a technicality

Both pass-A "no cuts" verdicts were correct *about the file named*, and wrong about the
page: in each case the approved list named a shell or an algorithm module while the prose
lived one module over. Pass B follows the prose.

Baseline re-established: `generate-html` byte-identical to committed gh-pages; 323 tests
pass.

## B1 — the almost-errors prose renderers

Pass A's list said `almost_errors.py`; the prose is in `almost_errors_html.py` and, below
it, the two per-section modules it threads together. All four examined.

### almost_errors_html.py

**CUT:** the two grouping comments inside `render_body_contents` —

- `# Charities: forgive a genuine LC/BHS/WLC quirk or anomaly.`
- `# Masoretically-blessed oddities: legitimate tradition the checker accepts, where the
  only decision is representation (which the telg exhibit makes visible).`

Both compress the emitted intro paragraphs **in the same file, ~50 lines above** — down to
the telg-exhibit parenthetical, which the intro also has. The remaining structure is
carried by the section function names and by the docstring's own two-bullet map, so
nothing invisible was lost.

**KEEP:** the module docstring in full. Its bullets name modules, not page sections (a
code map), and the closing paragraph — shares goerwitz.html's stylesheet, width-limited
shell, and `ob_tree_table`, "so a later merge with the prose/poetic reports is mechanical"
— is pure invisible architecture/why.

### almost_errors_html_shared.py

**No cuts.** The lowest presentation layer; it emits no prose of its own. Docstrings are
either signature-level (`ref_short`'s `G5:29` example) or invisible why:
`accents_and_letters` ("illustrate accent placement, not vocalization"),
`wrap_hebrew_runs` ("Hebrew is never italicized"), `uxlc_change_link` (single-sourced URL
form), and the `_HEBREW_RUN_RE` comment (why whole phrases stay in one `hbo` span).

### almost_errors_charities.py

**CUT** the docstring's second sentence: "a prose geresh muqdam read as a plain geresh, and
a stray poetic geresh read as a geresh muqdam (Psalms 124:4)" is **word-for-word** the
emitted `charities_intro` text fifteen lines below, and also restates the two `h3` headings
verbatim. Replaced with the structural map ("one `*_section` function per charity, after
the section intro"); kept the invisible "pure prose — no parse trees — so this module needs
only the shared link helpers."

### almost_errors_oddities.py — where the drift was

**DE-STALE (the pass-B counterpart of poetic_oddballs).** The module docstring opened
"**Two** exhibits, each backed by live parse trees from `almost_errors_trees`:" and then
listed **three** bullets. Both halves were wrong:

- the count never got updated when the Psalms 17:14 exhibit was added (the leftover "; and"
  at the end of the *second* bullet is the fossil of the old two-item list); and
- "each backed by live parse trees" is false for that third exhibit — `double_tsinnor_section`
  draws no tree at all, as its own docstring says.

Rewritten as a map that keeps the one genuinely invisible fact — *which* exhibits are
tree-backed and which is not, which is also why `double_tsinnor_section` alone takes no
`index`/`parser` — and drops the three descriptive bullets (each a restatement of its own
section's emitted prose; e.g. bullet 2's "the only word in Tanakh with two conjunctive
accents on one letter" is emitted twice, in this module and in the page intro).

**DE-STALE, second find.** The `_TELG_TREE_REFS` comment said the other three verses "get a
**verdict-table** row only". There is no telg verdict table: `_telg_forms_table` renders
`("verse", "word", "telg", "gerstar", "same letter?")` and its own docstring says "No parse
verdict: every reading parses cleanly." Corrected to "forms-table row only"; the invisible
why ("their trees differ in the same place and would only repeat the lesson") kept.

**CUT** in the same comment: "one same-letter (zp2:15), one cross-letter (lv10:4)" — emitted
twice (the "two examples … one same-letter case, one cross-letter" paragraph and the
note under the trees).

**CUT** the `_TELG_EXHIBIT_REFS` parenthetical "(gn5:29 / zp2:15 same-letter; 2k17:13
same-letter with geresh muqdam; lv10:4 / ek48:10 cross-letter, same word.)" and the trailing
"the checker keeps both, reading them in their Unicode (manuscript) mark order". Both are
emitted prose — and the same-letter split is worse than redundant: `_telg_forms_table`
**computes it live** (`forms.same_letter`) into the table's last column, so the comment is a
hand-maintained copy of a computed fact, the exact drift shape. Kept the identifying
sentence.

**CUT** the first sentence of the `_PS17V14_DEEP_DIVE` comment ("manuscript images, MAM
documentation notes, Breuer's structural analysis") — verbatim the emitted closing link
paragraph. Kept "this page carries only the short summary and links out" and, crucially,
the invisible editorial history: "the verse left the poetic ungrammatical-verse report once
the checker began accepting it."

**CUT** the second paragraph of `double_tsinnor_section`'s docstring, which re-derived the
LALR(1)/pre-parse-deletion argument that the emitted prose makes at length, ending on the
same parenthetical ("…which is also why there is no alternate-reading tree to show here").
Replaced with the part a code reader cannot see from the page: why this section function
alone takes no `index`/`parser`.

**KEEP + NOTE — the big `_EK_MODES` comment (L54–75).** This is the closest call in the
pass. Its five-line ASCII table and three-servus explanation overlap the emitted "why the
other three readings fail" paragraph nearly point for point, and its `-> clean` / `-> no
rule` column duplicates verdicts `aet._ek_verdict_for` computes live (checked against the
rendered table: fused and seq_qadma_mah clean, the other three ERROR — accurate, not
stale). But it is keyed by the `_EK_MODES` **code identifiers** and spells out grammar
internals the page never shows — the `pashta_phrase` rule name and the
`TELISHAQETANNA QADMA MAHAPAKH PASHTA` token spellings. Ambiguous map-or-copy → kept per
the rule. If a later pass wants it shorter, the safe cut is the verdict column alone,
leaving the token sequences.

**KEEP** (invisible, unconditionally preserved): the `_EK2031_MAM_NOTE_HE` provenance
comment (MAM-parsed-plus / MAM-with-doc, quoted + paraphrased); the `_QADMA_GAYA_REFS`
comment — its "(and miscites Num 20:1 as '21:1')" *is* emitted, but it is also the reason
the constant lists 20:1, and the trailing `(bb, chnu, vrnu, display, supplied)` is the tuple
shape; the LTR/RTL `tdattrs` comment; the "Taamey D doesn't support combining dot above
well" note; and `_telg_forms_table`'s column map, which adds "post-charity" and the
no-verdict rationale.

## B2 — the `rtmsr_*` prose-report modules: no cuts (all 11)

Pass A flagged these because `rtms_report.py` held only algorithm. Following the prose one
module over turns out to land somewhere with nothing to trim — **`rtmsr_intro.py`, which
holds essentially all of the goerwitz page's emitted prose, has no docstrings and no
comments at all.** There is nothing there to restate the prose. The other ten are
algorithm, data-shape, or naming modules:

- `rtmsr_intro.py` — all the page's intro prose (and the Goerwitz citation constants); zero
  comments/docstrings. Nothing to cut.
- `rtmsr_overview.py` — page assembler. `_Entry` field comments (category/source slugs) and
  `_SOURCE_LABELS`' "why the slug lives beside the prose" note are data-contract material;
  `_source`'s docstring records the hard-error constraint; `_build_facets`' docstring
  records the no-JS-fallback-vs-live-recount contract; `_render_verse_section`'s comment is
  the issue-#36 dual-cant bypass. All invisible.
- `rtmsr_verse.py` — `_dual_cant_verse_contents`' docstring is algorithm (run coalescing,
  spacing identical to the plain join). Its one factual claim, that on the dt 5:8 row the
  5:7/5:9/5:10 words become context, was **checked against live output** (the rendered
  labels are `taḥton (5:8)` and `elyon (5:7–10)`) — accurate, no drift.
- `rtmsr_sat.py` — `row_has_rendered_bracket_note`'s docstring records the
  agrees-with-the-visible-spans contract and its deliberate exclusion; the
  `_SAT_ROW_SUPPRESSIONS_BY_REF` inline note ("secondary tsinnorit diff on השמים, unrelated
  to the telisha") is per-datum why. Invisible.
- `rtmsr_media.py` — the `_IMG_BASE` comment is a path constraint; `_render_comment_item`'s
  comment is the htel-vs-string dispatch rule. Invisible.
- `rtmsr_bracket_notes.py`, `rtmsr_wlc_word_format.py` — one comment each, both
  order-preservation notes on a `dict.fromkeys` dedupe. Invisible.
- `rtmsr_sat_notes_column.py` — two row-shape comments. Invisible.
- `rtmsr_contracts.py`, `rtmsr_diff_format.py`, `rtmsr_subsets.py` — no docstrings or
  comments at all.

No edits, so no regen needed for B2.

## Pass B result

HTML byte-identical after every edit (`generate-html` → `git status --porcelain
gh-pages/accgram` empty); 323 tests pass; black clean on the three touched files.

## Follow-up candidates (not edited)

- The `_EK_MODES` verdict column in `almost_errors_oddities.py` (see B1) — the one
  deliberately-kept duplicate of a live-computed fact.
- The pass-A KEEP + NOTE items — `printed_decalogue_koren_page.py` L15–24,
  `printed_decalogue_simanim_page.py` L8–14, `telg_doc_notes.py` para 2,
  `supplied_marks.py`'s definitional paragraphs — all held back only by the
  "unsure ⇒ leave it" rule, and all still standing.
