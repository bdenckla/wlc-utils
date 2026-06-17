# Fix-tester: the remaining untestables

What the fix-tester ([`py/accgram/fix_tester.py`](../py/accgram/fix_tester.py)) does:
for every annotated prose oddball it splices the proposed fix into the
Michigan-Claremont (M-C) body, re-scans + re-parses with the real scanner/grammar,
and classifies the outcome `CONFIRMED` / `DENIED` / `CHANGED` / `UNTESTABLE`. The
proposed fix is normally "adopt the MAM-simple value", but when MAM equals WLC the
note's hand-authored `synth_fix` is tested instead (flagged `synthesized`).

As of 2026-06-16: **91 tested — 90 CONFIRMED, 0 DENIED, 0 CHANGED, 1 UNTESTABLE.**
This file enumerates the one remaining untestable, why it cannot be mechanically
tested, and the four apparatus barriers that were lifted to get here. Each barrier
was either an *apparatus limit* (could be lifted with more tooling) or *inherent*
(the change cannot affect the grammar, so there is nothing to test).

The sole remaining untestable is **inherent**: there is no word-accent change to
splice. All four apparatus barriers (`alignment_failure`, `ambiguous_accent`/zarshit,
`multi_accent`, and the verse-final-silluq promotion that had mislabelled 8 cases
`meteg_only`) have been lifted.

`UNTESTABLE` is not a verdict on the oddball — it means the fix could not be reduced
to a single, safely-appliable accent splice. The verdict counts (`agree`/`disagree`)
ignore these.

| reason | count | kind | path to testability |
|---|---:|---|---|
| `no_mam_diff` | 1 | inherent | not a word-accent change at all |

(`alignment_failure` (12), `ambiguous_accent` / zarshit (12), `multi_accent` (2), and
the 8 formerly-`meteg_only` were all RESOLVED 2026-06-16 — see below.)

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
`_accent_name_diff` strips `(mos)` from both sides of the diff — but here it
discarded the *silluq* the fix was supposed to add. The splice degenerated to
"delete the tevir, add nothing", leaving the word accent-less and still failing
`silluq_phrase`.

The fix (`fix_apply._accent_name_diff` + `fix_tester_codes`): a `(mos)` that
**replaces** a real WLC accent on a sof-pasuq-bearing word is the verse-final
silluq, not a meteg — it is promoted to a synthetic `(sil)` abbreviation mapping to
M-C code 35, which the scanner tokenizes as SILLUQ before sof-pasuq
(`(?:35|75|95)(?=…00)`). At first this promotion fired only for a *replacement*
(`removed and not added`); a `(mos)` merely *added* was left inert, which
mislabelled 8 pure-addition cases `meteg_only` — corrected below (see
[`meteg_only` — RESOLVED](#meteg_only--resolved-2026-06-16-was-8-mislabelled-inherent)),
where the promotion was extended to pure addition. The splice then swaps tevir
(91) → silluq (35), the verse parses CLEAN, and the verdict **agrees** with the
note. Covered by `test_verse_final_silluq_swap_applies` and
`test_meteg_added_to_word_that_already_has_silluq_stays_inert`.

---

## `ambiguous_accent` — zarshit / code 82 — RESOLVED 2026-06-16 (was 12, apparatus)

**Fixed. All 12 now CONFIRMED.** Every one of these is the **stranded-82** family:
a medial **zarshit** (the zarqa/tsinnorit stress-helper, U+0598 / M-C code 82) sits
where WLC should have a proper postpositive zarqa, with no fusion partner `02` in
the atom, so each already carries an `illegal_mark:82` lexical error. MAM has the
proper zarqa (`(zarnor)` / U+05AE / M-C code 02); the diff is a clean
`(zarshit)` → `(zarnor)`, i.e. **82 → 02**.

The barrier was *not* the lexical-pair complexity it looked like — the fix-tester's
checker already re-runs the lexical layer (`fix_tester._evaluate` calls
`lexical_validation.stranded_stress_helpers` before the grammar), so removing the 82
clears the error and the word then parses as a normal ZARQA. The only thing in the
way was a single bailout: `(zarshit)` is in `fix_tester_codes.UNTESTABLE_ABBREVS`
because code 82 has **no standalone token type** (alone the scanner swallows it; it
only means *zarqa* when fused as `82{TEXT}02`), so it was barred from
`SAFE_ABBREV_TO_CODE` and `_codes_for` returned it as unmappable.

But that invariant governs **adding** an accent. For this fix the 82 is only ever
**deleted** (located by its literal code and removed), and deletion needs no token
type. The fix splits the two concerns:

- `fix_tester_codes.REMOVAL_ONLY_ABBREV_TO_CODE` (`{"(zarshit)": "82"}`) + a new
  `removal_code()` resolve delete-only accents that `accent_code()` still refuses.
- `fix_apply._codes_for` gained a `for_removal` flag; `_splice_word` passes it for
  the *removed* side only. The diff is then a normal 1→1 swap (82 → 02), the atom
  re-scans as ZARQA, the lexical layer no longer flags it, and the verse parses
  CLEAN.

`(zarshit)` stays in `UNTESTABLE_ABBREVS` (it genuinely cannot be *added*); the
removal path is orthogonal. Covered by `test_stranded_zarshit_swapped_to_zarqa` and
`test_zarshit_addable_only_via_removal`.

| ref | proposed fix | transform | new verdict |
|---|---|---|---|
| ex 6:6 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| ex 30:12 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| ex 36:2 | בצלא֘ל → בצלאל֮ | 82 → 02 | CONFIRMED |
| gn 17:20 | ולישמע֘אל → ולישמעאל֮ | 82 → 02 | CONFIRMED |
| gn 47:29 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| dt 14:24 | תוכ֘ל → תוכל֮ | 82 → 02 | CONFIRMED |
| dt 31:7 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| lv 4:2 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| lv 20:2 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| nu 20:19 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| js 4:8 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |
| js 10:30 | ישרא֘ל → ישראל֮ | 82 → 02 | CONFIRMED |

(js 10:30 joined this family on 2026-06-16 once the `alignment_failure` barrier was
lifted; it was always in both lists.)

Note: the swap is **in-place** (the 02 lands where the 82 was, medial), not moved to
the word end as the philological fix would. It is mechanically equivalent — the
scanner rule `(?:82{TEXT})?02 → ZARQA` reads a bare `02` as ZARQA anywhere in the
atom — so the parse outcome is identical.

---

## `meteg_only` — RESOLVED 2026-06-16 (was 8, **mislabelled inherent**)

**Fixed. All 8 now CONFIRMED.** These had been filed as *inherent* on the reasoning
that *"the scanner swallows meteg, so adopting MAM cannot change the parse."* **That
reasoning was wrong.** Each of the 8 is a verse-final word that carries *no accent at
all* in WLC — which is exactly why it is flagged `silluq_phrase` (a missing
verse-final silluq) — and the U+05BD that MAM adds sits before the sof pasuq. A
U+05BD before `00` is a **silluq, not a meteg**: the scanner's silluq
trailing-context rule (`(?:35|75|95)(?=[^ 379…]*00)`, `ply_scanner.py`) tokenizes a
code-35 anywhere in the final word as SILLUQ. So the splice *does* reach the grammar,
and supplying the silluq clears `silluq_phrase`.

The real barrier was the one ju 13:18 exposed, in two parts — both in `fix_apply`:

1. **Promotion scoped to replacement only.** `_accent_name_diff` strips the `(mos)`
   abbreviation (meteg-**or**-silluq, U+05BD) from both sides, then re-promoted it to
   a real silluq *only* when MAM **replaced** a WLC accent (`removed and not added` —
   the ju 13:18 tevir→silluq case). A `(mos)` merely **added** stayed stripped → an
   empty diff → labelled `meteg_only`. But an added `(mos)` on a sof-pasuq word with
   no prior silluq *is* the missing verse-final silluq. The promotion now also fires
   on pure addition, guarded by `wlc_mos == 0` (the WLC word has no silluq of its
   own, so no risk of scanning a duplicate). A `(mos)` added to a word that *already*
   has one stays an inert medial meteg.

2. **Placement after the last letter, not before the sof pasuq.** Once promoted, the
   silluq was inserted "after the last M-C letter." For 5 of the 8 the atom carries a
   trailing note-marker whose payload is a *letter* (`…00]U`), so the silluq landed
   *past* the `00` (`…00]U35`), where the scanner — which stops at sof pasuq — never
   reaches it (a false DENIED). `_insert_codes` now places a verse-final silluq
   immediately **before** the `00` (`_insert_before_first_code`), which is also where
   the `…00]1` atoms' silluq already landed — so both trailing-marker shapes are
   handled uniformly.

| ref | proposed fix | grammar error | splice | new verdict |
|---|---|---|---|---|
| dt 10:15 | הזה׃ → הזֽה׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| dt 12:2 | רענן׃ → רענֽן׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| dt 23:18 | ישראל׃ → ישראֽל׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| gn 32:24 | לו׃ → לֽו׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| ho 11:7 | ירומם׃ → ירומֽם׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| is 13:7 | ימס׃ → ימֽס׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| lv 26:28 | חטאתיכם׃ → חטאתיכֽם׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |
| nu 27:9 | לאחיו׃ → לאחֽיו׃ | silluq_phrase | +silluq (35) before 00 | CONFIRMED |

Covered by `test_verse_final_silluq_added_when_word_lacks_one`,
`test_verse_final_silluq_inserts_before_sof_pasuq_not_after_note_marker`, and
`test_meteg_added_to_word_that_already_has_silluq_stays_inert`.

A *genuine* medial meteg — a `(mos)` added to a word that already has its silluq, or
on a non-final word — is still grammar-inert and would still correctly file as
`meteg_only`; none remain among the annotated oddballs. If a real accent-level
hypothesis exists for a truly-inert case (as with is 45:1's segolta), it can be
authored as a `synth_fix` and *that* will be tested — see the
[is 45:1 pattern](../py/accgram/ob_notes_is.py).

---

## `multi_accent` — RESOLVED 2026-06-16 (was 2, apparatus)

**Fixed. Both now CONFIRMED.** Each replaces one accent (azla, 63) with **two**
(two pashtas, 03 03) on the same word — a 1→many splice that
`fix_apply._splice` refused, handling only 1→1, delete-only, and insert-only.

| ref | proposed fix | grammar error | splice | new verdict |
|---|---|---|---|---|
| 1k 19:11 | הר֨וח → הר֙וח֙ | zaqef_phrase | `['63']` → `['03','03']` | CONFIRMED |
| je 49:19 | אריצ֨נו → אריצ֙נו֙ | tifcha_phrase | `['63']` → `['03','03']` | CONFIRMED |

The fix collapsed delete-only and insert-only into one **delete-then-insert** path:
`_splice` keeps the in-place 1→1 swap special-cased (so an in-place zarshit 82→02 or
verse-final silluq 91→35 stays at its offset), then for everything else deletes
every removed code and, if any codes are added, inserts them after the last M-C
letter via the existing `_insert_after_last_letter`. That placement is exactly the
simplification the insert-only path always made — the offset among letters is
irrelevant to tokenization, and pashta is postpositive, so both `03`s belong on the
final consonant anyway. The splice lands them *before* a trailing note-marker (e.g.
1k 19:11's `…XA]1` → `…XA0303]1`), so no `]1`+`03` digit-fusion. The `_MULTI_SPLICE`
sentinel and the `multi_accent` UntestableFix reason are gone. Covered by
`test_azla_to_double_pashta_applies`.

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
1. ~~**zarshit / code-82 (12)**~~ — DONE 2026-06-16 (delete-only `removal_code` for
   `(zarshit)`, `for_removal` flag in `_codes_for`): all 12 CONFIRMED via 82 → 02.
2. ~~**`multi_accent` (2)**~~ — DONE 2026-06-16 (delete-then-insert path in
   `_splice`, replacing the `_MULTI_SPLICE` bailout): both CONFIRMED via 63 → 03 03.
3. ~~**`meteg_only` (8)**~~ — DONE 2026-06-16 (verse-final-silluq promotion extended
   to pure addition guarded by `wlc_mos == 0`, plus before-sof-pasuq placement in
   `_insert_codes`): all 8 CONFIRMED. These had been **mislabelled inherent** — the
   added U+05BD before sof pasuq is a silluq, not a meteg.
4. **`no_mam_diff` (1)** — the only inherent untestable; not a word-accent change, so
   there is nothing to splice. Testable only if a genuine accent hypothesis is
   authored as a `synth_fix`. **No apparatus barriers remain.**
