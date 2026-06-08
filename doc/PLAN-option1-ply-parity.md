# Stage 1 Specific Plan: PLY Parity Port

This document describes Stage 1 only. It is intentionally detailed because it is
the first part of a larger overall plan in which Stage 2 performs a later
architectural refactor. Stage 1's sole job is **behavioral parity** with the
existing C program; cleanliness is Stage 2's problem.

## Goal
Port the C program in `accents-1.1.4/` to Python so that the Python port
reproduces the C program's tree output, byte-for-byte, for the parity corpus
defined below.

The C program (referred to in this repo as the "goerwitz" binary) reads
Michigan-Claremont/WLC text and prints, for each verse, a reference line
followed by an indented binary accent tree (when run with `-p`). The Python port
must produce identical stdout.

## What "the C program" actually is (source map)
The port target is four C source files under `accents-1.1.4/`:

- `tnk2acc.l` — the lexer (flex). Two input dialects share this file: an **old**
  betacode/TLG dialect (start states `AA`–`DD`, dispatched through
  `betacode_2_string`) and a **new** dialect with booknames at each chapter head
  and bare 2-digit accent codes (start states `EE`/`FF`/`GG`/`HH`). State `GG` is
  the accent scanner that emits the cantillation tokens.
- `acc2tre.y` — the yacc/bison grammar. It reduces the token stream for one verse
  (`TILDE silluq_clause SOFPASUQ`) into a binary tree via `make_node` /
  `add_leaves`, and prints it via `print_tree`. `#include "tnk2acc.c"` at the end
  means lexer and parser compile into one unit.
- `accutil.c` — tree node utilities: `make_node`, `add_leaves`, `print_tree`,
  `free_nodes`. **These define the exact output format** (see Output contract).
- `accents.c` — `main`, CLI flag handling, and the `accents_warning` /
  `accents_error` message text used on stderr.
- `parsebc.c` — betacode parser. **Old dialect only; out of scope** (see Scope).

## Scope
- **Input dialect: new format only** (the `Obad.new` style; booknames at chapter
  heads, bare 2-digit accent codes). The split WLC fixtures the harness already
  produces (`wlc_422_ps_<bb>.txt`) are in this dialect. The betacode path
  (`parsebc.c`, lexer states `AA`–`DD`, `betacode_2_string`) is **not ported** in
  Stage 1.
- **Display mode only: `-p` (display_tree = 1, display_all = 1).** The harness
  always invokes the binary as `accents -p`. We therefore only need the tree-
  building behavior. Note: when `display_tree == 0`, `make_node` returns its left
  child and `add_leaves` returns `NULL` — that code path is irrelevant to parity
  and need not be ported.
- **Functional target:** for each verse, match (a) whether a reference line is
  printed, (b) the exact reference string, and (c) the exact indented tree.
- **Non-goal for Stage 1:** architectural cleanup, the old betacode dialect,
  Psalms/Proverbs/poetic-Job (excluded upstream — see Corpus), and stderr message
  parity (stderr is diagnostic; only stdout defines parity — but see Risks).

## Current state (ground truth as of this revision)
This section replaces the earlier, inaccurate progress notes. Verified against
the actual code and artifacts.

**Already built — the oracle harness (not the port):**
- `py/main_accgram.py` with subcommands: `filter-split-wlc`, `run-goerwitz`,
  `fresh-run-goerwitz`, `research-tms-and-oddballs`. (There is no `split-wlc`,
  `run-orig`, or `out/accgram/orig` — earlier log entries naming those are stale.)
- `accgram/filter_split_wlc.py` + `accgram/split_wlc.py`: split
  `wlc422_ps.txt` into per-book new-format files and write a filtered copy that
  drops Psalms/Proverbs, poetically-cantillated Job verses, the Decalogue dual-
  cantillation ranges, and hard-coded "troublemaker" verses.
- `accgram/run_goerwitz.py`: runs the **C binary via WSL** (`wsl accents -p`)
  over the filtered fixtures and writes the oracle:
  `out/accgram/goerwitz/wlc_422_ps_<bb>_ag.txt` (stdout) and
  `out/accgram/goerwitz-stderr/...` (stderr), plus `_missing_verses.json`,
  `_oddballs.json`.
- `accgram/tms.py` / `tm_*.py` / `oddballs.py` / research + HTML reporting.

**Not started — the actual Stage 1 deliverable:**
- No Python tokenizer, no grammar, no tree layer. **PLY is not even installed**
  (`import ply` fails in `.venv`). Every "in progress" item on the old status
  board that refers to the port itself was aspirational.

**The oracle (parity baseline) exists and is frozen:**
- `out/accgram/goerwitz/*_ag.txt`: 37 book files, **18,666 verse trees total**.
- **51 "oddball" verses** (tree contains an `ERROR` node — the grammar's error
  productions fired) — `out/accgram/goerwitz/_oddballs.json`.
- **49 "troublemaker" verses** excluded from input before the C run —
  `out/accgram/goerwitz/_troublemakers.json`.
- **0 missing verses** (every filtered input verse appears in output).

## Architecture decisions (Stage 1)
1. **Hand-written tokenizer + PLY `yacc` for the grammar.** PLY's lexer does
   **not** implement lex *trailing context* (the `/` operator), and the C lexer's
   most load-bearing rules depend on it:
   - `35|75|95/[^ 379...]*00` → silluq (metheg/silluq immediately before sof
     pasuq),
   - `73/(...)*(00|92)` → mayela (tifcha variant before atnach/silluq),
   - `74{TEXT}05/[^12368]*...81` → legarmeh (munach+paseq before revia),
   - new-format `^[1-9][0-9]*:/[1-9]` → chapter token with verse lookahead.

   A faithful PLY-lex port is therefore impossible for exactly these rules.
   Instead, write a small scanner that reproduces the `GG`-state machine and its
   lookahead explicitly, emitting the same token stream PLY `yacc` will consume.
   PLY `yacc` *is* a good fit for the grammar (the grammar uses no trailing
   context, only ordinary productions + `error` recovery + one `%prec`).

2. **Match oddball verses too, tracked separately.** The 51 ERROR-node trees are
   still deterministic C output. Parity requires reproducing them byte-for-byte,
   but the verification report breaks results into `clean` vs `oddball` buckets so
   either can regress visibly.

## Output contract (must be reproduced exactly)
Derived from `accutil.c::print_tree` and `add_leaves`, and confirmed against
`out/accgram/goerwitz/wlc_422_ps_ob_ag.txt`:

- One verse = a reference line (e.g. `Obadiah 1:2`) printed by the `pasuq`
  action, followed by the tree from `print_tree(tree, 0)`.
- `print_tree` for an **internal node**: `indent_level` copies of the two-space
  `INDENT_STRING`, then `"<level> <label>\n"` (the integer level, a space, the
  node label).
- For a **leaf node** (left child is NULL): the node's own
  `"<level> <label>\n"` line, then `indent_level + 1` copies of the indent, then
  the leaves string. The leaves string is the space-joined leaf names **with a
  trailing space** (each `add_leaves` arg is followed by `" "`), e.g.
  `mereka tevir ` (note trailing space).
- Node labels come from the grammar actions: phrase nodes keep their phrase label
  (`silluq_phrase`, `atnach_phrase`, …); `make_node` builds internal nodes whose
  label is the *clause* name passed in (`silluq_clause`, `atnach_clause`, …).
- Error productions emit a leaf with the literal leaf name `ERROR` under the
  appropriate `*_phrase` label.

The reference string is built by the lexer's new-format path
(bookname + chapter + verse); reproduce its spacing exactly (treat the oracle as
the spec; do not "tidy" it).

## Token model (from `tnk2acc.l` GG state)
33 grammar tokens. Accent 2-digit code → token (leaf name in parentheses; the
leaf name is what appears in the tree):

- `00` → SOFPASUQ (`sof pasuq`); `92` → ATNACH (`atnach`)
- `35|75|95`+`00` lookahead → SILLUQ (`silluq`)
- `01`(rep)`01` → SEGOLTA (`segolta`); `65..05` → SHALSHELET (`shalshelet`)
- `63...80` → METHIGAZAQEF (`methiga-zaqef`); `80` → ZAQEF; `85` → ZAQEFGADOL
- `81` → REVIA; `73`+lookahead → MAYELA; `73` → TIFCHA
- `82?02` → ZARQA; `33?03` → PASHTA; `10` → YETIV; `91` → TEVIR
- `61` → GERESH; `62` → GERSHAYIM; `83` → PAZER; `84` → PAZERGADOL
- `14` → TELISHAGEDOLA; `74...05`+revia-lookahead-or-`has_legarmeh` → LEGARMEH
  else MUNACH; `74` → MUNACH; `70` → MAHPAK; `71` → MEREKA; `72` → MEREKAKEFULA
- `94` → DARGA; `63` → AZLA; `24...04`|`04`|`24` → TELISHAQETANNA; `93` → GALGAL
- `TILDE` is emitted at verse start (new-format chapter rule); swallowed codes
  (`35|75|95|44|05|82|52` leftovers, `**`, `*...`) emit nothing.

**Stateful special case — `has_legarmeh` (`tnk2acc.l`).** 17 passages where
munach+paseq counts as legarmeh even without a following revia, plus the
`1Sam 14:47` "second occurrence only" rule, implemented with C `static`
`count`/`old_i`. Because the harness runs **one process per book file**, this
static state resets per book; a per-book Python invocation reproduces that
naturally. Port the list and the counter logic verbatim and keep per-book
isolation.

## Parity definition
For each book file, the port's stdout must be **byte-identical** (LF newlines,
UTF-8) to the corresponding `out/accgram/goerwitz/wlc_422_ps_<bb>_ag.txt`.
Report results in two buckets: `clean` verses and the 51 `oddball` verses.
Acceptance is per-verse, derived by splitting both outputs on reference lines so a
single divergent verse is pinpointed rather than failing a whole book.

## Work Breakdown
1. **Baseline and fixtures — DONE (reuse, don't rebuild).**
   - Filtered per-book fixtures and the frozen oracle already exist
     (`filter-split-wlc`, `run-goerwitz`). Freeze them as the parity baseline.
   - Add a tiny `Obad.new` smoke fixture for fast iteration.

2. **Token model.**
   - Encode the code→token table above and the leaf-name strings.
   - Capture the swallow set and the TILDE/SOFPASUQ verse delimiters.

3. **Scanner (hand-written, replaces PLY lex).**
   - Reproduce the new-format state machine: bookname line → `EE` → chapter token
     (emit TILDE) → `FF` verse number (set location) → `GG` accent scan → `00`
     returns to `EE`.
   - Implement the four lookahead rules (silluq, mayela, legarmeh, chapter) by
     explicit peeking, matching flex longest-match + trailing-context semantics.
   - Port `has_legarmeh` with its static counter, per-book reset.
   - Build the location/reference string to match the oracle exactly.

4. **Grammar (PLY `yacc`).**
   - Translate `acc2tre.y` productions one-to-one (phrases, clauses, the `error`
     recovery rules, `%prec LOW_PRECEDENCE`).
   - Reproduce the `pasuq`-level behavior: print reference line, build/print tree,
     `are_errors`/`location_printed` bookkeeping, `free_nodes` reset.

5. **Tree and utility layer.**
   - Port `make_node` / `add_leaves` / `print_tree` for the `display_tree == 1`
     path only, preserving label strings, indentation, and the trailing-space
     leaf format.

6. **CLI wrapper.**
   - A Python entry point that reads a book file and prints the tree output,
     mirroring `accents -p`. Wire it as a new `main_accgram.py` subcommand
     (e.g. `run-ply`) writing to `out/accgram/ply/` for side-by-side diffing.

7. **Verification.**
   - Diff `out/accgram/ply/*_ag.txt` against `out/accgram/goerwitz/*_ag.txt`
     per verse; emit a parity report with `clean` and `oddball` buckets and a
     list of first-divergence verses.
   - Drive iteration to the acceptance threshold below.

8. **Hardening.**
   - One regression test per resolved mismatch class.
   - Document how to run the parity check; list any accepted residual diffs.

## Progress Tracking
Use this file as the canonical progress record for Stage 1.

Status labels: Not started · In progress · Blocked · Done

Cadence: update on each meaningful landing; entries stay factual and short
(date, change, evidence, next step).

### Stage 1 Status Board
- 1. Baseline and fixtures: **Done** (oracle frozen: 37 books / 18,666 verses;
  49 troublemakers excluded; 51 oddballs; 0 missing)
- 2. Token model definition: **Not started**
- 3. Scanner (hand-written): **Not started**
- 4. Grammar port (PLY yacc): **Not started** (PLY not yet installed)
- 5. Tree and utility layer: **Not started**
- 6. CLI wrapper: **Not started**
- 7. Verification: **Not started** (oracle exists; comparator not written)
- 8. Hardening: **Not started**

### Progress Log
- 2026-06-08: Revised the whole plan against the actual C source and repo state.
  Findings: (a) only the *new* input dialect and the `-p`/display_tree path are in
  scope; betacode (`parsebc.c`) is out. (b) PLY's lexer cannot express lex
  trailing context, which the silluq/mayela/legarmeh/chapter rules require →
  decision: **hand-written scanner + PLY yacc**. (c) Oracle already exists and is
  frozen (18,666 verses / 37 books; 51 oddballs; 49 troublemakers; 0 missing);
  earlier log entries naming `split-wlc`/`run-orig`/`out/accgram/orig` are stale —
  actual subcommands are `filter-split-wlc`/`run-goerwitz`/`fresh-run-goerwitz`/
  `research-tms-and-oddballs`. (d) Decision: oddballs are in the parity target but
  reported separately. Evidence: read `tnk2acc.l`, `acc2tre.y`, `accutil.c`,
  `accents.c`, `parsebc.c`, `accents.h`, `run_goerwitz.py`, `filter_split_wlc.py`,
  `oddballs.py`; counted 18,666 verse-label lines across `*_ag.txt`. Next: start
  item 2 (token model) and install PLY.

## Acceptance Criteria
- Byte-identical stdout vs the frozen oracle for every non-troublemaker verse, in
  both the `clean` and `oddball` buckets, across all 37 book files.
- The output contract (labels, two-space indentation, trailing-space leaves,
  reference strings) is reproduced exactly.
- Special-case behaviors (`has_legarmeh`, silluq/mayela lookahead, the per-clause
  `error` recovery productions) are covered by explicit regression tests.
- Any remaining differences are enumerated and explicitly accepted.

## Risks and Mitigations
- **PLY cannot express lex trailing context.** Mitigation: hand-written scanner
  with explicit lookahead; unit-test each lookahead rule against verses known to
  exercise it (mayela: Jer 2:31, Dan 4:9/18; legarmeh: the 17-passage list;
  silluq-missing: Gen 32:24).
- **flex longest-match semantics.** The scanner must prefer the longest match and
  honor rule order exactly as flex does, or token boundaries drift. Mitigation:
  fixture tests around multi-code words and maqqef-joined sequences.
- **`has_legarmeh` order/state dependence.** Mitigation: keep per-book process
  isolation; assert the `1Sam 14:47` count==2 behavior directly.
- **Grammar `error` recovery divergence.** PLY's `error` token + `yyerrok`
  analogue must mirror yacc's recovery, which determines the ERROR-leaf trees of
  the 51 oddballs. Mitigation: golden tests on all 51 oddball verses.
- **Reference-string spacing quirks.** Some oracle quirks (e.g. dropped/leading
  verses) come from the lexer, not the grammar. Mitigation: treat the oracle as
  the spec; reproduce quirks rather than "correcting" them.
- **stderr is out of parity scope** but is the only signal for some error classes.
  Mitigation: keep stderr capture available for debugging even though it is not
  an acceptance gate.

## Exit Criteria for Stage 1
Stage 1 is complete when the parity acceptance criteria are met and documented,
enabling transition to the Stage 2 refactor under the overall plan.
