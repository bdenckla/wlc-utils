# Issue #69: the page-prose pass — adjudicated decisions

Drafted and adjudicated 2026-07-24 (Ben). This is the settled record of what the three
printed-Decalogue page generators say about the fourteen verified Decalogues, and why. The draft
that preceded it was `.novc/issue69_prose_decisions_brief.md`.

Sources, in order of authority: issue #69's body (Results 1–11),
`py/tests/test_edition_transcriptions.py`, the transcription headers under
`in/accgram/edition_transcriptions/`, `py/tests/test_ctr_decalogue.py`.

## 0. The claim set is TWELVE, and CTR is not in it

**Adjudicated.** All overall claims concern **the twelve** — four Decalogues each from Simanim's
Tiqqun, Simanim's Tanakh, and Koren's Classic Tanakh. CTR is deliberately **not** ranked among
them: it is a curiosity, presented as one, and no claim on any page rests on it.

This also repairs a statement that had gone stale. #69's "Consequences for page wording" section
(written when three transcriptions existed) says the claim that survived every transcription is
"the chanted verse boundaries plus the disjunctive skeleton". With all fourteen in that was no
longer true as a blanket. Scoped to the twelve it is true again, and needs no exception clause:

| claim | of the twelve |
|---|---|
| every chanted verse boundary agrees with the strand followed | **12 of 12 — exceptionless** |
| follows its strand in every accent | 7 of 12 |
| the disjunctive skeleton is untouched | 10 of 12 (`simtiq_dt_taxton`, `simtan_dt_taxton` excepted) |

## 1. Word-division and two-accent-compound findings

**Adjudicated: name the class, not the sites**, with one exception promoted to its own sentence on
the hub — at ובנך־ובתך, Simanim's Tiqqun and Koren each print two separately accented chanted
words where the p-trad עליון has one. Two editions dividing the same chanted word alike and
against the strand they otherwise follow is a fact about the strand, not about either edition, so
it belongs on the hub rather than half-told on each satellite.

The two-accent-compound finding gets a clause, not a sentence: what it bears on is the apparatus
(it falsified `edition_transcription.py`'s "a maqaf-joined proclitic cannot bear an accent"), not
the tradition question.

## 2. Verdicts are per-Decalogue, at four levels

Never per-edition — p. 247's Shabbat departure and pp. 208–209's exact agreement cannot share a
sentence. Four deliberately distinct phrasings, so no two Decalogues read as sharing a verdict:

- **A — zero divergences (7).** "Follows *〈strand〉* in every accent."
- **B — word division only (2).** "Every accent; differs only in how it divides two chanted words."
- **C — conjunctive only (1).** "Every chanted verse boundary and the whole disjunctive skeleton;
  differs at *N* conjunctives."
- **D — tradition content (2).** Named in full, no template.

| edition | Decalogue | pages | strand | level |
|---|---|---|---|---|
| Simanim Tiqqun | Exodus main | 83–84 | p-trad עליון | B (ובנך־ובתך, לא־תחמד) |
| | Exodus appendix | 246 | p-trad תחתון | C (3) |
| | Deuteronomy main | 208–209 | p-trad עליון | A |
| | Deuteronomy appendix | 247 | p-trad תחתון | D — m-trad accents at the Shabbat commandment; the chanted verse division stays p-trad (13) |
| Koren | Exodus main | 113–114 | p-trad תחתון | A (weakly discriminating) |
| | Deuteronomy main | 280–281 | p-trad תחתון | A — five discriminators, all p-trad |
| | Exodus appendix | A38 | p-trad עליון | B (יהיה־לך, ובנך־ובתך) |
| | Deuteronomy appendix | A39 | p-trad עליון | A — joins both compounds its Exodus sibling splits |
| Simanim Tanakh | Exodus main | 119–120 | m-trad תחתון | A |
| | Deuteronomy main | 297–298 | m-trad תחתון | D — *qadma* on ויום (5:13), agreeing with neither תחתון strand |
| | Exodus appendix | 350 | m-trad עליון | A |
| | Deuteronomy appendix | 351 | m-trad עליון | A |

## 3. How the evidence basis is described

**Adjudicated.** Both satellite pages replace "since no digital X exists, I established this by
visually spot-checking" with a two-stage account: the signal words place the edition among the four
strands; a hand transcription of every printed accent, diffed against that strand, says how far it
follows it.

**3a.** Both pages already use "transcription" for the **note** transcriptions. On first mention
the new ones are "hand transcriptions of the printed accents"; where both appear in one section,
the old sense is "the note transcriptions".

## 4. Where Simanim Tanakh and CTR live

**4a — Simanim Tanakh: the Simanim page, not a new page.** It already lives there as a scope note
with two figures; it gains verdicts. A separate page would duplicate the apparatus for four
Decalogues whose whole interest is the contrast with the Tiqqun on the same page.

**4b — CTR: stays the `<h3>` aside it is.** Superseded my own draft recommendation, which was to
promote it to its own `<h2>`; decision 0 rules that out. It gains one sentence for the
Exodus finding and keeps its existing register (the page quotes Ben's own review — "certainly the
weirdest Hebrew Bible on the web, and possibly the worst"). Guardrails preserved: the "on the web"
scoping is load-bearing (it makes no claim about print editions — an earlier draft's "gap in Koren
and Simanim" was false for Koren), and the aside stays where the Sabbath connection is.

**CTR's Exodus division, stated in chanted verses only.** The probe behind this
(`.novc/ctr_ex_division_probe.py`) exists because a draft described it as "the ordinary
numbered-verse division", which is both off-subject and wrong. CTR's Exodus 20 has **16** chanted
verses: the תחתון's thirteen, with each of the three short prohibitions split into its own chanted
verse, as only an עליון strand does. Its word-accents are the עליון's. So it matches neither
strand. Deuteronomy 5 is 13, identical to the p-trad תחתון. Numbering is not the subject anywhere
on these pages.

**The numbered-verse phrasing was fixed in code and in the issue too** (Ben, 2026-07-24 — raised as
a loose end, then fixed on the spot rather than filed). `ctr_decalogue.py`'s module docstring had
said CTR's Exodus "keeps the ordinary numbered-verse division — a sof pasuq at every numbered
verse", and #69's Result 11 said the same. Both are off-subject and false: Exodus 20:13 holds
**four** sof pasuqs, which is where three of the sixteen come from, so the module contradicted its
own `chanted_verses` docstring. Both now state the division in chanted verses only. The docstring
also gained a standing rule against the numbering framing, and `has` replaced `carries`.

## 5. Koren's "unqualified" p-trad allegiance

**Adjudicated: keep it, and state the bound.** The transcriptions make it stronger, not weaker —
across all four Koren Decalogues not one divergence takes an m-trad side. Unqualified **as to
tradition**; the one Decalogue that diverges at all diverges only in word division, and no
vendored strand anywhere separates יהיה from לך, so that split is Koren's alone and
tradition-neutral.

**5a — a sentence that is now false, and must go.** "I have not chased Koren's Deuteronomy עליון
through its appendix, so the Deuteronomy half of the claim rests on the תחתון alone."
`koren_dt_elyon` (p. A39, 4bd3b69) is that Decalogue: transcribed, zero divergences.

## 6. What goes on which page

The hub must not assert what a satellite page does not document.

**Hub** — the two "See also" blurbs rewritten to per-Decalogue verdicts at headline grain; the
twelve-Decalogue basis and the shared ובנך־ובתך split added to the four-strands section; the CTR
aside updated. Unchanged: the verdict table, the four-strands table, the merged-first-verse
finding, the Sabbath diff appendix — none is a claim about a real edition.

**Simanim page** — verdict table for the Tiqqun's four in the conclusion, before the Shabbat scope
note it substantiates; verdict table for the Tanakh's four in the second scope note; the
evidence-basis rewrite; the return link to the Koren page. Unchanged: the two note sections, the
Aleppo Codex section, and the title, whose exact claim is now machine-checked and survives verbatim.

**Koren page** — verdict table in the conclusion; decisions 5 and 5a; the evidence-basis rewrite;
the page-number fixes. Unchanged: the p. A38 note section, the title.

## 7. Mechanical

1. Simanim page → Koren page return link (the cross-reference ran only Koren → Simanim).
2. "p. 113" → "pp. 113–114" at the three Koren prose sites. The p. 113 **figure caption** is left
   alone: it captions a scan of the Decalogue's start, where p. 113 is accurate.
3. The Koren appendix Deuteronomy Decalogue is cited **p. A39**, per that page's settled A-prefix
   rule. The transcription files keep their own "p. 39" spelling — they are committed inputs.
4. The hub's Koren blurb was Exodus-scoped; Koren's Deuteronomy is established (#66) and now
   transcribed in both strands.
5. The Koren module docstring's DRAFT-STAGE list called p. 113 unverified; transcription settled it
   as pp. 113–114. A38 is unaffected.

## 8. The two uncertain readings — no page mention at all

**Adjudicated.** `koren_ex_taxton` (p. 114 line 1, the לא of לא תרצח) and `koren_dt_taxton`
(p. 281 line 2, the *tipeḥa* on את־שמו) get **no mention on the Koren page in any form** — not a
footnote, not a small line. Their only reader-facing home is #70. Ben is confident enough in both,
and no surprising result hinges on either, that the pages **assume them true**; the verdicts for
pp. 113–114 and pp. 280–281 are stated flat.

This governs the rendered documents. The machine-checked record — the `.txt` headers, the JSON
`uncertain_readings` fields, the `_UNCERTAIN_READINGS` pins — is audit infrastructure and is
untouched.
