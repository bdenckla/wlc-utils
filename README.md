# wlc-utils

Data and documentation derived from the Westminster Leningrad Codex (WLC), together with the
accent-grammar (`accgram`) study built on it. **This repository contains no code.** As of
2026-08-01 all of its Python lives in the sibling repository
[MAM-basics](https://github.com/bdenckla/MAM-basics), under `py/`, and generates into this one.

## What is here

- `in/` — inputs: the WLC 4.20 and 4.22 source XML, the vendored UXLC XML and change lists, and
  the hand-authored printed-Decalogue transcriptions under `in/accgram/`.
- `out/` — generated JSON and text: the WLC in JSON and in Unicode, the 4.20/4.22 and
  WLC/UXLC diffs, and the accent-grammar parse records under `out/accgram/`.
- `gh-pages/` — the generated static site (below).
- `data/` — a hand-maintained lookup table, `data/lci_recs.json`.
- `doc/` — design notes and plans, including `doc/agent-planning-principles.md`.

`in/accgram/uxlc_accent_changes.json` is the exception to the usual reading of those directory
names: it lives under `in/` but is written by a program, not by hand.

## Regenerating it

From a clone of MAM-basics sitting beside this one, with that repo's own interpreter:

```powershell
C:\Users\BenDe\GitRepos\MAM-basics\.venv\Scripts\python.exe C:\Users\BenDe\GitRepos\MAM-basics\py\main_0_mega.py
```

That covers all of `gh-pages/` and most of `out/`. A handful of generators sit outside it and
have to be run by hand — `main_uxlc_grammar_test.py`, `main_find_uxlc_accent_changes.py`, and
several `py\main_accgram.py` subcommands. `CLAUDE.md` lists each of them and says what it writes.

Regenerating should produce **no diff**. An unexplained one is a bug, in this repo's data or in
MAM-basics' code; that is how the real defects here have actually been found.

## GitHub Pages

The static site under `gh-pages/` is deployed by `.github/workflows/pages.yml`, which involves no
Python and is unaffected by the move. Published sections:

- `https://bdenckla.github.io/wlc-utils/` — site root, `gh-pages/index.html`
- `https://bdenckla.github.io/wlc-utils/accgram/` — the accent-grammar pages
- `https://bdenckla.github.io/wlc-utils/420422/` — the WLC 4.20 / 4.22 word diffs
- `https://bdenckla.github.io/wlc-utils/wlc-a-notes/` — the WLC a-notes family

`gh-pages/` deliberately stays in this repository: moving it would break published links.
