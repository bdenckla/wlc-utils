# CLAUDE.md

## Read `doc/agent-planning-principles.md` before planning work here

That file holds this repo's planning preferences (phase sizing, new-features-as-new-modules,
writing state back between phases, keeping verification close to the real workflow). Nothing
in the tree referenced it, so for a long time no agent ever loaded it — hence this pointer.

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
