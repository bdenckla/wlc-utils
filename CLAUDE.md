# CLAUDE.md

## This repo contains no Python. Its generators live in `../MAM-basics/py/`

wlc-utils is data and documentation: `in/`, `out/`, `gh-pages/`, `data/`, `doc/`. Everything
under `out/` and `gh-pages/` is generated, and **every generator lives in the sibling repo
`../MAM-basics`**, which writes back into this one. All 267 tracked `.py` files left this repo on
2026-08-01; do not add one back, and do not go looking here for the code that produced a file you
are reading. Run everything below from `C:\Users\BenDe\GitRepos\MAM-basics`, with that repo's own
interpreter — this repo's `requirements.txt` went with the code, and whatever `.venv` is left
here has nothing to run.

Almost all of it regenerates in one command:

```powershell
C:\Users\BenDe\GitRepos\MAM-basics\.venv\Scripts\python.exe C:\Users\BenDe\GitRepos\MAM-basics\py\main_0_mega.py
```

Its wlc-utils steps, in the order they must run: `wlc-vendor-uxlc`, `wlc-json-and-unicode`,
`accgram-run-prose`, `accgram-test-fixes`, `accgram-run-poetic`, `accgram-generate-html`,
`wlc-diffs-420422`, `wlc-a-notes`. (They are no longer the mega's *last* steps: a repo-wide
vendoring audit closes the run.) The individual entry points behind them, all under
`MAM-basics/py/`:

- `main_accgram.py` — the accent-grammar work, and everything under `out/accgram/` and
  `gh-pages/accgram/`. Many subcommands; `--help` lists them. Only `run-prose`, `test-fixes`,
  `run-poetic` and `generate-html` are in the mega (`test-fixes` since 2026-08-04 —
  MAM-basics#219 — its tracked `out/accgram/fix-tester/` having twice gone stale outside it),
  so `run-dual-cant`, `run-printed-decalogue`, `survey-chanted-word-accents`, `xcheck-poetic`,
  `servi-xcheck` and `grammaticality` have to be run by hand — as do
  `vendor-printed-decalogue` and `vendor-ctr-decalogue`, which refresh vendored strands rather
  than regenerate anything.
- `main_edition_transcription.py` — the printed-Decalogue transcriptions under `in/accgram/`,
  including the `highlight-picker` subcommand. `build --check` re-derives every committed
  transcription body and is the cheapest check that they are still consistent.
- `main_wlc_json_and_unicode.py` — `out/wlc420.json`, `out/wlc422-kq-u` and friends.
- `main_wlc_a_notes.py` — `gh-pages/wlc-a-notes/`.
- `main_wlc_diffs_420422.py` — `gh-pages/420422/`.
- `main_wlc_vendor_uxlc.py` — refreshes `in/UXLC-39` and `in/UXLC-misc` from UXLC-utils.
- `main_find_uxlc_accent_changes.py` — writes the tracked `in/accgram/uxlc_accent_changes.json`.
  **Not in the mega**, so nothing rewrites it routinely.
- `main_uxlc_grammar_test.py` — `out/accgram/uxlc_grammar_test.txt`. **Also not in the mega**,
  which is exactly how it once sat stale in the tree for two days short of a month.

Not everything under those two directories is generated at all: 73 static assets under
`gh-pages/accgram/` (three `.js`, seventy `.png`/`.jpg`) and the 38 files under
`out/accgram/goerwitz-stderr/`, which is captured stderr from the original C `accents` checker.
Deleting and regenerating will not bring those back.

`.novc/` stays here — it is this repo's gitignored scratch directory, and the highlight picker and
`scan_page.py`'s renderings still write into it. MAM-basics' `py/main_repo_maintenance.py` wipes
it along with its own.

**Prose, terminology and testing rules moved to `../MAM-basics/CLAUDE.md`** along with the code
they govern. Read that file before editing anything that generates text here.

## This repo's issues stay here; new ones are filed in MAM-basics

The 88 issues were **not** transferred when the Python left on 2026-08-01. They keep their numbers
and stay in `bdenckla/wlc-utils`, and this is still where they are read, commented on and closed.
So **a bare `#NN` in this repo's `doc/`, `in/` and this file still means a wlc-utils issue**; not
one of those references was requalified, because qualifying them would imply they had been
ambiguous.

New issues, including new work on the generators now in `../MAM-basics/py/`, are filed in
**MAM-basics**. There a bare `#NN` means a MAM-basics issue, and the moved code cites this repo's
as `wlc-utils#NN` — both trackers hold issues in the 1-88 range, and the prefix is the only thing
keeping wlc-utils#52 (the printed Decalogue) apart from MAM-basics #52 (a meteg in Ezekiel).

## Read `doc/agent-planning-principles.md` before planning work here

That file holds this repo's planning preferences (phase sizing, new-features-as-new-modules,
writing state back between phases, keeping verification close to the real workflow). Nothing
in the tree referenced it, so for a long time no agent ever loaded it — hence this pointer.
It is still the fullest statement of the "Generated Outputs Are the Tests" rule, and
`MAM-basics/CLAUDE.md` cites it from there.

## There is no `wlc-koren-12th` repo

`~/GitRepos/wlc-koren-12th` was never a repo of its own. It was a **worktree of wlc-utils** on
branch `claude/koren-12th-site`, which is why it sat flat among the siblings and answered
`git remote -v` with `bdenckla/wlc-utils`. Its copies of files like
`py/accgram/poetic_ply_grammar.py` were the same files on an older branch — never duplicates to
reconcile or keep in sync. Repeated sessions read it as a twin repo and burned a turn
"reconciling" it; that is the whole reason for this note.

Deleted 2026-07-27, along with the fully-merged leftover branches `claude/koren-12th-site` (tip
8b699ab) and `claude/festive-napier-38d58d` (tip 153f921). Both were 0 commits ahead of `main`
and contained in `origin/main`, so the work survives there; `git branch -d` (never `-D`)
accepting them is the record that nothing was lost. Nothing anywhere referenced the path — a
sweep of every repo under `~/GitRepos` plus the settings files found zero hits — so no config or
doc was left pointing at it, and nothing in git history names it either, a directory being the
one thing git does not record. The only place the name survives is old Claude session
transcripts under `~/.claude/projects/`, which is exactly where the wrong conclusion kept being
copied from.

**General lesson:** a directory sitting flat under `~/GitRepos` is not necessarily a repo. Run
`git -C <dir> rev-parse --git-common-dir` (or `git worktree list` from the repo you suspect)
before treating one as a peer whose files need syncing.
