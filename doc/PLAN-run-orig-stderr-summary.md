# Plan: Run-orig stderr JSON summary

Date: 2026-05-26

## Goal
Add a deterministic final-step JSON summary to run-orig so each run produces an aggregate artifact for all out/accgram/orig-stderr/*_ag.stderr.txt files.

The summary will:
- Group and count unique stderr messages by verse reference when present.
- Group and count unique stderr messages not tied to a verse.
- Run after all sidecars are written.

## Decisions
- Summary format: JSON report.
- Aggregation semantics: store every unique message related to a particular verse, with counts for repeated messages; also store messages not related to particular verses.
- In scope: final-step summarization as part of run-orig execution.
- Out of scope: redesign of run-orig pipeline, historical dashboards, parser parity fixes.

## Implementation Steps
1. Phase 1: schema and output contract.
2. Add summary artifact path under the existing stderr directory. Recommended filename: out/accgram/orig-stderr/_summary.stderr.json.
3. Define JSON schema with stable ordering:
   - Run metadata.
   - File counters.
   - Verse-message aggregates.
   - Non-verse-message aggregates.
   - Optional per-file counters.
4. Include explicit totals:
   - Files scanned.
   - Files with non-empty stderr.
   - Total stderr lines.
   - Total unique verse messages.
   - Total unique non-verse messages.
5. Phase 2: run-orig integration.
6. In py/accgram/run_orig.py, add a final-step helper invoked from run(args) immediately after run_orig(...) returns.
7. Read all *_ag.stderr.txt files in args.stderr_dir using sorted iteration for deterministic output.
8. Parse each stderr line into verse-related or non-verse:
   - For verse-related lines, normalize key as verse_ref + message_text_without_ref, then increment counts.
   - For non-verse lines, normalize key as message_text, then increment counts.
9. Persist summary JSON with UTF-8, indent=2, and trailing newline.
10. Print one additional console line indicating summary path and key totals.
11. Phase 3: message parsing rules.
12. Implement verse extraction rules tuned to observed accents stderr formats, including lines ending in Book Chapter:Verse (example: Obadiah 1:2).
13. Keep parser conservative:
   - If a line does not confidently match a verse reference, place it in non-verse bucket.
14. Add normalization for whitespace and repeated spaces so semantically identical lines count together.
15. Phase 4: robustness and non-goals.
16. Ensure summary generation does not break primary output generation.
17. Initial behavior should preserve existing run-orig success behavior.
18. Exclude cross-run accumulation and non-JSON reporting from this task.
19. Phase 5: verification.
20. Run main_accgram run-orig and verify summary file is regenerated under out/accgram/orig-stderr.
21. Validate totals against directory reality:
   - Number of *_ag.stderr.txt files.
   - Non-empty sidecar count.
   - Repeated warning counts for known files like Exodus and Obadiah.
22. Spot-check JSON buckets:
   - Verse aggregates should include entries like Obadiah 1:2 warning families.
   - Non-verse bucket should exist even if empty.
23. Confirm main_0_mega integration remains unchanged except for one additional run-orig stdout line.

## Relevant Files
- py/accgram/run_orig.py
- py/main_accgram.py
- py/accgram/filter_split_wlc.py
- out/accgram/orig-stderr/

## Verification Checklist
1. Execute main_accgram run-orig and confirm completion with existing counters plus one summary output line.
2. Verify summary JSON exists at out/accgram/orig-stderr/_summary.stderr.json and contains deterministic sorted sections.
3. Re-run run-orig and confirm summary output is deterministic for unchanged inputs.
4. Compare a few per-file counts in JSON against raw stderr files (at least Exodus, Obadiah, and one empty file like Genesis).
5. Confirm no behavior regressions in produced *_ag.txt and *_ag.stderr.txt artifacts.

## Further Considerations
1. Keep filename prefixed with underscore to avoid confusion with payload files.
2. Add optional strict mode later only if needed, to fail run-orig when summary generation fails.
3. If downstream joins are needed later, add a secondary flattened section in JSON without removing grouped sections.
