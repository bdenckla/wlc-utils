# Fix-tester: the remaining untestables

What the fix-tester ([`py/accgram/fix_tester.py`](../py/accgram/fix_tester.py)) does:
for every annotated prose oddball it splices the proposed fix into the
Michigan-Claremont (M-C) body, re-scans + re-parses with the real scanner/grammar,
and classifies the outcome `CONFIRMED` / `DENIED` / `CHANGED` / `UNTESTABLE`. The
proposed fix is normally "adopt the MAM-simple value", but when MAM equals WLC the
note's hand-authored `synth_fix` is tested instead (flagged `synthesized`).

As of 2026-06-16: **91 tested — 68 CONFIRMED, 0 DENIED, 0 CHANGED, 23 UNTESTABLE.**
This file enumerates the 23 untestables, why each cannot be mechanically tested, and
whether the barrier is an *apparatus limit* (could be lifted with more tooling) or
*inherent* (the change cannot affect the grammar, so there is nothing to test).

`UNTESTABLE` is not a verdict on the oddball — it means the fix could not be reduced
to a single, safely-appliable accent splice. The verdict counts (`agree`/`disagree`)
ignore these.

| reason | count | kind | path to testability |
|---|---:|---|---|
| `ambiguous_accent` (zarshit) | 12 | apparatus / deliberate | handle the code-82 zarqa lexical pair |
| `meteg_only` | 8 | inherent | grammar is blind to meteg; needs a real accent hypothesis (`synth_fix`) |
| `multi_accent` | 2 | apparatus | support a 1→many accent splice |
| `no_mam_diff` | 1 | inherent | not a word-accent change at all |

---

## `alignment_failure` — RESOLVED 2026-06-16 (was 12, apparatus)

**Fixed.** Of the 12, **10 now CONFIRMED** and **2 fell through to their next
barrier** (je 49:19 → `multi_accent`, js 10:30 → `ambiguous_accent`/zarshit — it was
always in both lists). ju 13:18 first surfaced as a *false* DENIED; a second fix
(verse-final silluq promotion, below) turned it into the 10th CONFIRMED.

The doc's hypothesis was exactly right: a single shared tokenization bug, not 12
distinct problems. The splice located the changed word by index-aligning the M-C
body's word-atoms (`fix_apply._word_atom_spans`) 1:1 with the WLC word tokens
(`fix_apply.verse_words`); each body had **exactly one more** word-atom.

The extra atom was the **section marker**: every petuhah (`P`), setumah (`S`), and
nun-inversum (`N`) is encoded in the M-C body as a bare single-letter atom. The WLC
side already drops it (`verse_words` skips it — no Hebrew consonant; rtms_data tags
it `sam_pe_inun`), but `_word_atom_spans` kept it, because `S`/`P` double as the
M-C consonants samekh and pe and so matched `_MC_LETTER_RE`. The fix: a
`_SECTION_MARKER_RE` (`^[PSN](?:\].)*$`) excludes a *lone* P/S/N (a real word
bearing those consonants always carries vowels), mirroring
`wlc_read_and_parse_mdc._distinguish_sam_pe_inun`. Covered by
`test_section_marker_atom_excluded_from_alignment`.

| ref | proposed fix | grammar error | new verdict |
|---|---|---|---|
| 1k 8:11 | מפנ֥י → מפנ֣י | atnach_phrase | CONFIRMED |
| 1k 20:25 | וס֣וס → וס֥וס | legarmeh_phrase | CONFIRMED (multi-word path) |
| 2c 22:12 | שנ֖ים → שנ֑ים | silluq_phrase | CONFIRMED |
| 2c 24:27 | י֧ר֞ב → י֧רב | revia_phrase | CONFIRMED |
| ek 11:1 | שר֖י → שר֥י | silluq_phrase | CONFIRMED |
| ek 14:11 | וה֥יו ל֣י → והיו־ ל֣י | revia_phrase | CONFIRMED (multi-word path) |
| je 9:10 | מבל֖י → מבל֥י | silluq_phrase | CONFIRMED |
| je 9:11 | מבל֖י → מבל֥י | silluq_phrase | CONFIRMED |
| je 49:19 | אריצ֨נו → אריצ֙נו֙ | tifcha_phrase | UNTESTABLE → `multi_accent` |
| js 10:30 | ישרא֘ל → ישראל֮ | illegal_mark:82 | UNTESTABLE → `ambiguous_accent` |
| js 15:47 | עז֥ה → עז֛ה | tifcha_phrase | CONFIRMED |
| ju 13:18 | פ֛לאי׃ → פֽלאי׃ | silluq_phrase | CONFIRMED (silluq promotion, below) |

### Verse-final silluq promotion (the ju 13:18 fix)

Once the section-marker fix let ju 13:18 splice, it came out **DENIED** — but that
was a false negative, an apparatus artifact. The ob_note's claim is *"BHQ
transcribes a silluq as a tevir due to a speck"*: the fix is **tevir → verse-final
silluq**, and adopting it parses clean.

The trap: a silluq and a meteg are the **same glyph** (U+05BD), so
`uni_heb.accent_names` reduces both to `(mos)` (meteg-**o**r-**s**illuq).
`_accent_name_diff` strips `(mos)` from both sides of the diff — correct for the 8
`meteg_only` cases (a meteg is invisible to the grammar) — but here it discarded the
*silluq* the fix was supposed to add. The splice degenerated to "delete the tevir,
add nothing", leaving the word accent-less and still failing `silluq_phrase`.

The fix (`fix_apply._accent_name_diff` + `fix_tester_codes`): a `(mos)` that
**replaces** a real WLC accent on a sof-pasuq-bearing word is the verse-final
silluq, not a meteg — it is promoted to a synthetic `(sil)` abbreviation mapping to
M-C code 35, which the scanner tokenizes as SILLUQ before sof-pasuq
(`(?:35|75|95)(?=…00)`). A `(mos)` merely *added* (nothing removed) stays an inert
meteg, so the `meteg_only` cases are unaffected. The splice then swaps tevir (91) →
silluq (35), the verse parses CLEAN, and the verdict **agrees** with the note.
Covered by `test_verse_final_silluq_swap_applies` and
`test_meteg_added_on_sof_pasuq_word_stays_inert`.

---

## `ambiguous_accent` — zarshit / code 82 (12) — apparatus, deliberately refused

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
| js 10:30 | ישרא֘ל → ישראל֮ | illegal_mark:82 |

(js 10:30 joined this family on 2026-06-16 once the `alignment_failure` barrier was
lifted; it was always in both lists.)

These are the **stranded-82** family: the mark sits in a medial position (U+0598
zarshit) where WLC should have a proper zarqa. The fix is the same shape across all
12 (relocate/normalize the zarqa). Making them testable would mean teaching the
splice the 82 lexical pair — a deliberate, contained extension, but one that
overlaps the lexical-validation layer rather than the accent grammar.

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

## `multi_accent` (2) — apparatus

| ref | proposed fix | grammar error | splice |
|---|---|---|---|
| 1k 19:11 | הר֨וח → הר֙וח֙ | zaqef_phrase | `['63']` → `['03','03']` |
| je 49:19 | אריצ֨נו → אריצ֙נו֙ | tifcha_phrase | `['63']` → `['03','03']` |

The MAM reading replaces one accent (azla, 63) with **two** (two pashtas, 03 03) on
the same word. `fix_apply._splice` handles 1→1, delete-only, and insert-only; a
1→many replacement is refused. Supporting it (delete the old code, insert the new
ones at the right offset) would make these testable. (je 49:19 joined this category
on 2026-06-16 once the `alignment_failure` barrier was lifted — same azla→pashta×2
shape as 1k 19:11.)

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

0. ~~**`alignment_failure` (12)**~~ — DONE 2026-06-16 (section-marker exclusion in
   `_word_atom_spans`, plus verse-final silluq promotion in `_accent_name_diff`):
   10 CONFIRMED, 2 fell through to the barriers below; 0 DENIED.
1. **zarshit / code-82 (12)** — decide whether the splice should handle the 82
   lexical pair, or whether these belong wholly to the lexical-validation layer.
2. **`multi_accent` (2)** — extend `_splice` to 1→many.
3. **`meteg_only` (8)** and **`no_mam_diff` (1)** — inherent; testable only by
   authoring a `synth_fix` where a genuine accent hypothesis exists.
