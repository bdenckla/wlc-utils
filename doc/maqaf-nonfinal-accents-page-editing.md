# Editing `maqaf-nonfinal-accents.html` — the working track

**This is not a plan.** It is the persistent state of a free-form, cross-session track in which
Ben requests edits to one rendered page, one at a time, and they are applied. There is no phase
sequence, no deliverable to build toward, and no next step to execute unasked. A session resuming
here waits for Ben to ask for something.

**It is a different track from `PLAN-two-accents-on-one-chanted-word.md`**, and the confusion is
worth stating plainly because it has already happened: that plan's subject is a *rule in the prose
checker*, and this track's subject is the *wording and shape of one page*. The page is about the
same phenomenon, which is what makes them easy to conflate, but editing the page is not work on
the checker. Do not fold this track's state into that plan, and do not read that plan's phases as
instructions for this page.

## The artifacts

| what | where |
| --- | --- |
| the page | `gh-pages/accgram/maqaf-nonfinal-accents.html` |
| its generator | `py/accgram/maqaf_nonfinal_accents_page.py` |
| the survey behind it | `py/accgram/maqaf_nonfinal_accents.py` |
| the tracked data | `out/accgram/maqaf-nonfinal-accents.json` |

One run writes both the JSON and the page, so the two cannot drift:

```
cd py && ../.venv/Scripts/python.exe main_accgram.py generate-html-maqaf-nonfinal-accents
```

Then black every touched `.py`, and `.venv/Scripts/pytest.exe py/tests` from the repo root.

## How Ben works this track

- **One wording change at a time**, and he does not read long replies. Apply it, regenerate,
  report in a line or two.
- **Hand him a clickable `file:///` link** to the page — plain text, in a fenced block. Never
  launch a browser, never stand up a server. Verify what you wrote with `Read` on the generated
  file, which is the only evidence available. **Omit the link on a turn where the page did not
  change**; a link to an unchanged page reads as a second modified file and has already confused
  him once.
- **Prefer cutting to explaining.** He is narrowing this page's scope hard — "get out alive". One
  page, one question; narrow the *rendering*, not the data.
- **File cut material as a GitHub issue** rather than deleting it. #83 holds this page's cuts.
- **Never retype an accent.** Lift the Hebrew from the vendored data at generation time, letters
  and accents only, no vowels (`accents_and_letters`). `_find_span()` plus `_render_span()` is the
  pattern: a search pattern of atom letters per chanted word, an assertion that it matches exactly
  one place, and the maqafs put back. It replaced `lo_taase_atoms()` / `simtiq_lo_compounds()` on
  2026-07-29.
- **Show it in Unicode, not in words.** Ben, 2026-07-29: "I can't process all the verbosity, I
  need to just see this using actual unicode. You've fallen into the trap of not giving me
  Unicode." Naming an accent in prose is not a substitute for showing the form; where two or three
  texts are being compared, the shape that works is a table whose cells are the forms.
- **Struck from this page**, each its own cleanup: "own" as filler; "secondary" in a rendered
  label; "witness"; any agentive verb where "has" will do. Treat a new synonym the same way.
- The standing rules for the prose itself are the `hebrew-prose` skill's, and the rendered-prose
  conventions are `printed_decalogue_strands.py`'s module docstring. **Load the skill before
  editing any of this page's text.**

## Where the page stands

`h1` "Accents on a Non-Final Atom of a Compound", then an intro, then `The prose verses`,
`The poetic verses`, and two appendices — `the pairs that occur on a simple chanted word only`
and `the chanted words whose two marks sit on one letter`.

The intro shows the three printed maqaf compounds accented on both atoms — Koren's Deuteronomy
appendix compound, and the Simanim Tiqqun's two Exodus ones — and asks whether MAM has anything
like any of them. It does not, and `pin_claims` fails the build if any of the three pairs ever
turns up in the data, via `unprecedented_pairs()`.

Since 2026-07-29 those three are a **table**, one row per (edition, compound) case, with three
form columns: the printed edition, that book's Wikisource strand of the same name, and that book's
other strand. The third column is there because the mark each printed form has and its own strand
lacks is a mark the other strand has — Koren's maqaf, the Simanim Tiqqun's munaḥ on the joined לא —
so the page can offer a cross-strand carry-over. It must **not** call either an error: Ben assumes
the Simanim Tiqqun's is one but "I'd prefer not to state that in the document". Every strand the
page reads is p-trad, said once in the sentence above the table and dropped from the individual
mentions; `_p_trad_strand` is where that is fixed in code.

**Do not restate the page's numbers here.** They live in the JSON and in `pin_claims`, which
re-derives every stated claim and raises on drift; a copy in this file would be stale from the day
it was written.

## Each round's account is its commit message

That is deliberate and is the durable record — `829d1f6..` on `main`, of which `0ab2c6a` is the
fullest. Read the messages rather than re-deriving what a round decided. This file carries only
what a commit message is the wrong place for: the working rules above, and the open items below.

## Open on this track

- **A clause offered and not answered.** That in some traditions a qadma azla is sung to a
  different melody from a qadma geresh (Jacobson, CHB p. 187). Offered 2026-07-29; Ben did not
  answer either way. The full record is in `_geresh_or_azla_note`'s docstring, beside the note it
  would have joined. **Do not add it unasked, and do not re-offer it as though it were new.**

## Closed, so it is not re-derived

- **The zarqa's stress helper.** `7aeeeb0` finished the `fb3e5cc` sweep in
  `maqaf_nonfinal_accents.py`. `accent_marks`' `TSINNORIT`/`TSINNOR` and this page's
  `_ACCENT_SHORTHAND` are both **deliberately** left spelling the poetic sense, for reasons
  written into the code beside each. Issue #85.
- **The mark-versus-token count reconciliation** belongs to the checker track, not to this page.
  Ben ruled it off the page on 2026-07-29; it is issue #86.
