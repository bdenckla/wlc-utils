# Agent Planning Principles

These principles capture planning preferences for AI coding agents working in this repository.

## Generated Outputs Are the Tests

For workflows whose important behavior is expressed through generated, git-tracked artifacts, do not add test files or test cases unless explicitly requested.

Instead, use the generated outputs as the verification surface:

- Regenerate the relevant JSON and HTML artifacts with the real CLI command.
- Inspect the generated output files for expected changes.
- Confirm that files expected to remain unchanged do remain unchanged, aside from normal generated metadata if applicable.
- Treat unexpected diffs in generated JSON or HTML as test failures until explained.

In these workflows, examining the generated HTML and JSON is the test.

## Prefer New Files For New Features

Implement new features in new focused modules/files as much as practical.

Prefer small, purpose-named modules for new feature areas rather than swelling existing large files. Existing files should usually receive only the wiring, reuse hooks, and documentation needed to connect the new behavior to the established workflow.

This keeps review simpler and makes it easier to abandon, revise, or phase in new behavior without disturbing mature code paths.

## Size Phases to Natural Boundaries

Size phases to coherent goals and natural verification points, not to any model's context limit. A capable agent can take on a large phase in one session, so do not pre-fragment work to fit a smaller executor; combine steps that share a goal and a verification point.

A good phase should have:

- A coherent implementation goal.
- A natural verification point.
- A clear handoff boundary to the next phase.

Limited blast radius and fresh-session executability are virtues, but they follow from a coherent goal rather than from an imposed size budget. Do not make every mechanical step its own phase. For example, styling and docs are often too small to be standalone phases; they usually belong with the functional work they support. Conversely, a risky refactor that preserves existing behavior may deserve its own phase before new behavior is added.

## Write State Back Before Continuing

At the end of each phase, write the current state back into the plan before proceeding.

The phase-end update should include:

- What changed.
- What verification was run.
- What generated outputs changed or intentionally did not change.
- Any unexpected findings or unresolved risks.
- The exact next phase to execute.

After writing the phase state back, compact the conversation context before continuing. This acts as a poor man's fresh session: the next phase starts with a short, current plan rather than stale conversational residue.

## Keep Verification Close To The Workflow

Prefer real workflow commands over narrow synthetic checks. For generated-output workflows, the primary verification should be the same CLI command a maintainer would run to refresh the artifacts.

If a smaller local invocation is useful inside an intermediate phase, use it only as provisional verification. The final phase should still run the real regeneration command and inspect the resulting tracked artifacts.
