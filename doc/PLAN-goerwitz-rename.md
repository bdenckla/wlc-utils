## Plan: Accgram Goerwitz Terminology Rename

Rename vague accgram uses of accents to goerwitz in Python symbols/comments/docstrings/user-facing strings, and rename orig output-directory tokens in the accgram output path defaults. Keep all Hebrew-linguistics accents terminology untouched outside the accgram tooling context.

**Steps**
1. Phase 1: Core renames in accgram runner (blocking).
2. In c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/run_orig.py, rename output path token orig to goerwitz for default out-dir and rename orig-stderr to goerwitz-stderr for default stderr-dir. This satisfies the requested output path change and updates behavior defaults.
3. In c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/run_orig.py, rename CLI argument --accents-bin to --goerwitz-bin and its bound namespace field, then rename related Python symbols default_accents_bin, accents_bin parameter/locals, and accents_wsl_path to goerwitz equivalents. Update all related help/error/status strings to goerwitz terminology.
4. Phase 2: WLC header-name helper renames (depends on 1).
5. In c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/wlc_book_codes.py, rename symbols accents_book_name, _ACCENTS_BOOK_HEADER_RE, and wlc_bb_to_accents_book_name to goerwitz equivalents. Update all internal references and the ValueError wording that currently says accents header expectations.
6. Phase 3: Downstream callers/imports (depends on 2).
7. In c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/split_wlc.py, update import and call sites to the renamed goerwitz helper, and update the ambiguous message Unexpected verse line format during accents normalization to goerwitz-focused wording aligned with your decision to rename vague accgram-facing text.
8. In c:/Users/BenDe/GitRepos/MAM-basics/py/main_accgram.py, update subcommand description/help text from Run accents (via WSL) to Run goerwitz (via WSL), and change default path text from out/accgram/orig-stderr to out/accgram/goerwitz-stderr.
9. Phase 4: Test updates (parallel with 3 once symbols stabilize).
10. In c:/Users/BenDe/GitRepos/MAM-basics/py/tests/test_accgram_run_orig.py, rename fixture/local parameter names accents_bin to goerwitz_bin, and update asserted warning/error substrings that mention accents so tests match new runtime text.
11. Phase 5: Safety sweep and compatibility check (depends on 1-4).
12. Run targeted grep for remaining accgram-context uses of accents and old output tokens orig/orig-stderr in Python files; keep unchanged any true Hebrew-accent domain references outside accgram.
13. Confirm no lingering callers use args.accents_bin or function names removed in this rename.

**Relevant files**
- c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/run_orig.py — primary CLI, runtime execution path, defaults for out/stderr dirs, and user-facing status/error strings.
- c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/wlc_book_codes.py — WLC code-to-book-name mapping APIs and validation regex constant.
- c:/Users/BenDe/GitRepos/MAM-basics/py/accgram/split_wlc.py — importer/caller of renamed helper and one accgram-facing normalization error message.
- c:/Users/BenDe/GitRepos/MAM-basics/py/main_accgram.py — CLI docs/help text and default output path wording shown to users.
- c:/Users/BenDe/GitRepos/MAM-basics/py/tests/test_accgram_run_orig.py — unit tests that reference renamed parameters and expected output strings.

**Verification**
1. Run python -m unittest py/tests/test_accgram_run_orig.py from c:/Users/BenDe/GitRepos/MAM-basics and confirm all tests pass.
2. Run grep search for accents in py/accgram and py/main_accgram.py and verify only non-vague/tool-binary path pieces remain intentionally (for example accents-1.1.4/accents executable path if retained).
3. Run grep search for out/accgram/orig and orig-stderr in Python files to ensure these are replaced with goerwitz variants.
4. Optional manual CLI smoke: invoke py/main_accgram.py run-orig --help and confirm --goerwitz-bin and updated descriptions/default path strings render correctly.

**Decisions**
- Confirmed: rename CLI option to --goerwitz-bin (breaking compatibility is accepted).
- Confirmed: rename all vague accgram-facing accents text (messages/help/tests) to goerwitz.
- Scope included: Python symbols, comments/docstrings, and accgram-facing runtime/help strings in accgram workflow.
- Scope excluded: linguistic/biblical accents terminology and modules outside the accgram tooling context.
- Path interpretation: apply rename to out/accgram/orig and out/accgram/orig-stderr (user phrasing included out/accgram-orig-stderr; repository uses nested out/accgram/orig-stderr).

**Further Considerations**
1. Backward compatibility alias option: if needed later, add hidden/deprecated --accents-bin that maps to --goerwitz-bin for one transition cycle.
2. If on-disk output folders already exist, decide whether to keep old folders as historical artifacts or migrate them in a separate filesystem-only step.
