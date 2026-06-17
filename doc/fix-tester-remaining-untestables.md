# Fix-tester: the remaining untestables

What the fix-tester ([`py/accgram/fix_tester.py`](../py/accgram/fix_tester.py)) does:
for every annotated prose oddball it splices the proposed fix into the
Michigan-Claremont (M-C) body, re-scans + re-parses with the real scanner/grammar,
and classifies the outcome `CONFIRMED` / `DENIED` / `CHANGED` / `UNTESTABLE`. The
proposed fix is normally "adopt the MAM-simple value", but when MAM equals WLC the
note's hand-authored `synth_fix` is tested instead (flagged `synthesized`).

As of 2026-06-16: **91 tested — 58 CONFIRMED, 0 DENIED, 0 CHANGED, 33 UNTESTABLE.**
This file enumerates the 33 untestables, why each cannot be mechanically tested, and
whether the barrier is an *apparatus limit* (could be lifted with more tooling) or
*inherent* (the change cannot affect the grammar, so there is nothing to test).

`UNTESTABLE` is not a verdict on the oddball — it means the fix could not be reduced
to a single, safely-appliable accent splice. The verdict counts (`agree`/`disagree`)
ignore these.

| reason | count | kind | path to testability |
|---|---:|---|---|
| `alignment_failure` | 12 | apparatus | fix the M-C-atom ↔ WLC-word alignment (off-by-one) |
| `ambiguous_accent` (zarshit) | 11 | apparatus / deliberate | handle the code-82 zarqa lexical pair |
| `meteg_only` | 8 | inherent | grammar is blind to meteg; needs a real accent hypothesis (`synth_fix`) |
| `multi_accent` | 1 | apparatus | support a 1→many accent splice |
| `no_mam_diff` | 1 | inherent | not a word-accent change at all |

---

## `alignment_failure` (12) — apparatus

The splice locates the changed word by index-aligning the M-C body's word-atoms
(`fix_apply._word_atom_spans`) 1:1 with the WLC verse's word tokens
(`fix_apply.verse_words`). In every one of these cases the body has **exactly one
more** word-atom than the WLC word list, so the alignment is rejected before any
splice is attempted.

| ref | proposed fix | grammar error | atoms vs words |
|---|---|---|---|
| 1k 8:11 | מפנ֥י → מפנ֣י | atnach_phrase | 15 vs 14 |
| 1k 20:25 | וס֣וס → וס֥וס | legarmeh_phrase | 23 vs 22 |
| 2c 22:12 | שנ֖ים → שנ֑ים | silluq_phrase | 12 vs 11 |
| 2c 24:27 | י֧ר֞ב → י֧רב | revia_phrase | 18 vs 17 |
| ek 11:1 | שר֖י → שר֥י | silluq_phrase | 31 vs 30 |
| ek 14:11 | וה֥יו ל֣י → והיו־ ל֣י | revia_phrase | 23 vs 22 |
| je 9:10 | מבל֖י → מבל֥י | silluq_phrase | 14 vs 13 |
| je 9:11 | מבל֖י → מבל֥י | silluq_phrase | 21 vs 20 |
| je 49:19 | אריצ֨נו → אריצ֙נו֙ | tifcha_phrase | 28 vs 27 |
| js 10:30 | ישרא֘ל → ישראל֮ | illegal_mark:82 | 27 vs 26 |
| js 15:47 | עז֥ה → עז֛ה | tifcha_phrase | 13 vs 12 |
| ju 13:18 | פ֛לאי׃ → פֽלאי׃ | silluq_phrase | 11 vs 10 |

The consistent +1 points at a single tokenization mismatch between the two word
counts (e.g. a paseq / maqaf / standalone punctuation atom counted on one side but
not the other), not 12 distinct problems. **Lifting this is the highest-value next
step**: it would unblock testing of 12 oddballs at once (note 1k 20:25 and ek 14:11
also exercise the multi-word splice path). Investigate `_word_atom_spans`
vs `verse_words` on one case (e.g. ju 13:18, the shortest) to find the extra atom.

---

## `ambiguous_accent` — zarshit / code 82 (11) — apparatus, deliberately refused

Every one of these moves a **zarshit** (the medial zarqa/tsinnorit stress-helper,
M-C code 82) — and every one already carries an `illegal_mark:82` lexical error.
`(zarshit)` is listed in `fix_tester_codes.UNTESTABLE_ABBREVS` on purpose: code 82 is
a lexical pair, not a context-free accent, so the splice refuses it rather than
guess.

| ref | proposed fix | grammar error |
|---|---|---|
| ex 6:6 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| ex 30:12 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| ex 36:2 | בצלא֘ל → בצלאל֮ | illegal_mark:82 |
| gn 17:20 | ולישמע֘אל → ולישמעאל֮ | illegal_mark:82 |
| gn 47:29 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| dt 14:24 | תוכ֘ל → תוכל֮ | illegal_mark:82 |
| dt 31:7 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| lv 4:2 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| lv 20:2 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| nu 20:19 | ישרא֘ל → ישראל֮ | illegal_mark:82 |
| js 4:8 | ישרא֘ל → ישראל֮ | illegal_mark:82 |

These are the **stranded-82** family: the mark sits in a medial position (U+0598
zarshit) where WLC should have a proper zarqa. The fix is the same shape across all
11 (relocate/normalize the zarqa). Making them testable would mean teaching the
splice the 82 lexical pair — a deliberate, contained extension, but one that
overlaps the lexical-validation layer rather than the accent grammar. (Several of
these also fall under `alignment_failure`, e.g. js 4:8 vs js 10:30, so both barriers
would need lifting.)

---

## `meteg_only` (8) — inherent

The sole difference between WLC and MAM here is a **meteg** (U+05BD). The scanner
swallows meteg (and vowels) — only accents and punctuation reach the grammar — so
adopting MAM cannot change the parse. Every one is flagged `silluq_phrase`, i.e. the
real complaint is about the verse-final silluq / sof-pasuq region, which the meteg
diff does not touch.

| ref | proposed fix | grammar error |
|---|---|---|
| dt 10:15 | הזה׃ → הזֽה׃ | silluq_phrase |
| dt 12:2 | רענן׃ → רענֽן׃ | silluq_phrase |
| dt 23:18 | ישראל׃ → ישראֽל׃ | silluq_phrase |
| gn 32:24 | לו׃ → לֽו׃ | silluq_phrase |
| ho 11:7 | ירומם׃ → ירומֽם׃ | silluq_phrase |
| is 13:7 | ימס׃ → ימֽס׃ | silluq_phrase |
| lv 26:28 | חטאתיכם׃ → חטאתיכֽם׃ | silluq_phrase |
| nu 27:9 | לאחיו׃ → לאחֽיו׃ | silluq_phrase |

These are correctly inert: there is nothing to test, because the meteg is invisible
to the grammar. If a real accent-level hypothesis exists for any of them (as with
is 45:1's segolta), it can be authored as a `synth_fix` and *that* will be tested —
see the [is 45:1 pattern](../py/accgram/ob_notes_is.py).

---

## `multi_accent` (1) — apparatus

| ref | proposed fix | grammar error | splice |
|---|---|---|---|
| 1k 19:11 | הר֨וח → הר֙וח֙ | zaqef_phrase | `['63']` → `['03','03']` |

The MAM reading replaces one accent (azla, 63) with **two** (two pashtas, 03 03) on
the same word. `fix_apply._splice` handles 1→1, delete-only, and insert-only; a
1→many replacement is refused. Supporting it (delete the old code, insert the new
ones at the right offset) would make this one testable.

---

## `no_mam_diff` (1) — inherent

| ref | proposed fix | grammar error |
|---|---|---|
| nu 25:19 | (MAM equals WLC; nothing to adopt) | silluq_phrase, sof_pasuq_phrase |

MAM equals WLC and no `synth_fix` is authored, because this oddball is a misplaced
verse-number (a BHS structural artifact), not a word-accent change. There is no
single-word reading to splice, so it stays untestable by design.

---

## Summary of next steps, by leverage

1. **`alignment_failure` (12)** — find the M-C-atom/WLC-word off-by-one in
   `fix_apply`. Single fix, unblocks the most cases.
2. **zarshit / code-82 (11)** — decide whether the splice should handle the 82
   lexical pair, or whether these belong wholly to the lexical-validation layer.
3. **`multi_accent` (1)** — extend `_splice` to 1→many.
4. **`meteg_only` (8)** and **`no_mam_diff` (1)** — inherent; testable only by
   authoring a `synth_fix` where a genuine accent hypothesis exists.
