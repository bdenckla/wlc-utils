"""Pin each committed hand transcription against its vendored Wikisource strand.

These tests turn "edition X follows strand Y in every accent" from prose on a page into a
machine-checked claim.  Each transcription's divergences from its strand are pinned exactly:
a re-vendoring, an upstream Wikisource revision, or a corrected transcription that changes
the divergence set fails here instead of quietly falsifying a page.

Skips if the vendored source JSON is absent (regenerate via printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_edition_transcriptions.py -v
"""

from __future__ import annotations

import json

import pytest

from accgram import edition_transcription as et
from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds
from accgram import transcription_build as tb
from accgram import transcription_check as tc

# The divergences established for each transcription, keyed by its filename stem.  Each entry
# is (reference tokens, transcribed tokens, the reference word the region starts on).
#
# Simanim's Exodus main Decalogue (elyon, pp. 83-84) diverges from the Wikisource p-trad elyon
# at exactly two points, and BOTH are word-division differences rather than cantillation
# choices -- Simanim splits a maqaf compound the reference joins, and joins one the reference
# splits.  The conjunctive/meteg marking then follows mechanically, because a maqaf-joined
# proclitic cannot bear an accent while a free-standing word must:
#
#   * ובנך ובתך (Shabbat commandment): reference joins them under one telisha gedola, so ובנך
#     takes a meteg and no accent; Simanim sets them as two words, so ובנך takes a munax.
#     Simanim's reading here is attested by none of the eight Wikisource strands.
#   * לא תחמד בית (tenth commandment): reference sets לא free with its own merkha; Simanim
#     joins it by maqaf, so לא takes a meteg and no accent.  All four Exodus strands agree
#     with the reference here, so it is Simanim that diverges.
#
# The two cancel in the token count (+1 munax, -1 merkha), which is why the totals match at
# 142 despite two real divergences.  Do not read equal totals as agreement.
#
# RE-TRANSCRIBED 2026-07-22 with the line editor, this file having been the last one with no
# committed export, and the divergence set came back UNCHANGED -- the same two regions, token
# for token, from an independent second reading of the same pages.  What the redo did add is the
# audit trail (so every export-based test below now covers this stem too) and the pasoleg KINDS,
# which the first transcription's conventions had dropped: Simanim distinguishes the two, and
# the four strokes split 2 narrow paseq (16 פסל, 19 בשמים) and 2 legarmeh (25 במים, 75 שבת),
# each landing on its exact reference position.
#
# Words are pinned by LETTER SKELETON (``pds.base_skeleton``), not by their pointed form: the
# skeleton is stable, readable in a diff, and does not embed a fragile sequence of combining
# marks in this file.
_EXPECTED_DIVERGENCES = {
    "simanim_ex_elyon": [
        # base_skeleton drops the maqaf along with the points, so the reference's joining of
        # these two atoms -- the very thing at issue -- is not visible in the pinned skeleton.
        ("", "mun", "ובנךובתך"),
        ("mer", "", "לא"),
    ],
    # Simanim's Exodus appendix Decalogue (taxton, p. 246) diverges at three points, and
    # unlike the elyon's pair, two of them are genuine ACCENT differences:
    #
    #   * לא־יהיה (20:3) and לא־תעשה (20:4): Simanim accents BOTH atoms of the maqaf compound
    #     -- munax on the joined לא, against merkha and qadma on the second atoms -- where all
    #     eight strands have a meteg on the לא and no accent.  Two accents on one chanted word
    #     is rare, and none of the eight does it at either site.  It is not a house habit of
    #     the edition either: לא־תעשה recurs at 20:10 (לא־תעשה כל־מלאכה) and Simanim agrees
    #     with the reference there.
    #   * לא תחמד (tenth commandment): the reference sets לא free with its own merkha; Simanim
    #     joins it by maqaf, so it takes no accent.  A word-division difference, and the SAME
    #     one found in Simanim's Exodus elyon -- two independently transcribed Simanim
    #     Decalogues agreeing with each other and against all eight strands, which have merkha
    #     on the free (ו)לא and tipexa on תחמד in both books.
    #
    # Both munax insertions and the merkha deletion are conjunctive, so the disjunctive
    # skeleton is untouched; see test_pinned_divergences_leave_the_disjunctive_skeleton_alone.
    "simanim_ex_taxton": [
        ("", "mun", "לאיהיה"),
        ("", "mun", "לאתעשה"),
        ("mer", "", "לא"),
    ],
    # Simanim's Deuteronomy main Decalogue (elyon, pp. 208-209) diverges NOWHERE: 164 reference
    # tokens against 164 transcribed, agreeing at every one.  It is the first transcription for
    # which "follows the p-trad with respect to every accent" is actually true, and pinning the
    # empty list is what keeps it honest -- a re-vendoring that moved any accent in this strand
    # would break this test rather than quietly weaken the claim to nothing.
    #
    # How it was reached bears on how much it is worth, and the .txt header says so at length:
    # the harness flags only positions where the two disagree, so only those were re-read.
    # Three were, and all three turned out to be transcription slips rather than edition
    # divergences.  The ~161 agreeing positions were never re-examined, so this is "no
    # divergence survived a procedure that only inspects candidate divergences" -- and the
    # Exodus elyon above, whose two real divergences cancelled in the token count, is the
    # standing proof that compensating errors are possible in exactly this material.
    "simanim_dt_elyon": [],
    # Simanim's Deuteronomy appendix Decalogue (taxton, p. 247) is the edition's KNOWN m-trad
    # departure, and the first transcription whose divergences are neither word-division
    # differences nor confined to conjunctives.  All three regions fall inside the Shabbat
    # commandment, and there the page reads m-trad throughout -- the three signal words
    # (כל־מלאכה pazer not geresh, ועבדך־ואמתך telisha gedola not revia, וכל־בהמתך revia not
    # zaqef qatan), the surrounding stretch token for token, and the word division too, לא and
    # תעשה being separately accented where the p-trad joins them by maqaf.
    #
    # The finding does not rest on the review loop's asymmetry.  Compared against the m-trad
    # taxton instead, this transcription is 166 tokens against 166 with three difference
    # regions, ALL of them inside the FIRST commandment: the two strands partition the
    # differences with nothing left over.  Agreement with a strand the harness had no stake in,
    # over a contiguous run, is positive evidence rather than survival of a flag.
    #
    # What the departure does NOT extend to is the chanted verse division, which stays p-trad
    # (13 verses, pinned below; the m-trad has 12).  Accents only.
    "simanim_dt_taxton": [
        ("", "mun mun paz mun mun tg", "לאתעשה"),
        ("mun mun", "", "אתה"),
        ("mah pash zaq", "", "ושורך"),
    ],
    # Koren's Exodus main Decalogue (taxton, pp. 113-114) diverges NOWHERE: 142 reference
    # tokens against 142.  The second transcription for which "follows the p-trad in every
    # accent" holds, and the first for an edition other than Simanim.
    #
    # What it licenses is narrower than the count suggests, and the .txt header says so at
    # length.  The Shabbat commandment cannot discriminate in EXODUS -- ex/taxton/printed and
    # ex/taxton/manuscript are identical at כל־מלאכה, both geresh -- so this is no support
    # for Koren following the p-trad there; the printed/manuscript split at Shabbat is
    # Deuteronomy-only.  Nor does the pasoleg discriminate: ex/taxton has exactly one, on אתה,
    # in both traditions.  The one discriminator this Decalogue reaches is the CHANTED VERSE
    # BOUNDARY at עבדים, pinned below at 13.
    "koren_ex_taxton": [],
    # Also empty, but this one licenses far more than the Exodus page above.  The Deuteronomy
    # taxton strands differ in five independent ways and Koren takes the p-trad side of every
    # one: כל־מלאכה (geresh / pazer), ועבדך־ואמתך (revia / telisha gedola), וכל־בהמתך (zaqef /
    # revia -- dt/taxton/printed is the ONLY one of the eight strands to depart there), the
    # pasoleg on אתה (present / absent, so the pasoleg COUNT discriminates), and the chanted
    # verse boundary at עבדים pinned below.  The first four sit inside the Shabbat commandment,
    # exactly where simanim_dt_taxton departs TO the m-trad -- so these two transcriptions
    # disagree about the same commandment, and neither is the other's rounding error.
    "koren_dt_taxton": [],
    # Koren's Exodus APPENDIX Decalogue (elyon, p. 38) is the FIRST Koren page to diverge:
    # 142 reference tokens against 144, at TWO points.  Both are WORD-DIVISION differences, not
    # tradition ones -- at two maqaf compounds the vendored ex/elyon/printed strand writes as a
    # single chanted word, Koren prints the two atoms as separate accented words:
    #   * לֹא יִהְיֶה לְךָ (20:3): Koren gives יהיה its own munax where the reference joins
    #     יהיה־לך (so יהיה carries only a meteg).  The region anchors at the reference word לא,
    #     hence the "לא" skeleton; the inserted accent is the munax on יהיה.
    #   * אַתָּה וּבִנְךָ וּבִתֶּךָ (Shabbat): Koren gives ובנך its own munax where the reference
    #     joins ובנך־ובתך.  base_skeleton drops the maqaf, so it pins as "ובנךובתך" -- the same
    #     limitation, and the SAME divergence token for token, as simanim_ex_elyon above.
    # Both inserted accents are conjunctive (munax), so the disjunctive skeleton is untouched
    # (koren_ex_elyon is in _SKELETON_UNTOUCHED below).  The ובנך split is corroborated: the two
    # ex/taxton strands separate ובנך with a munax too, and simanim_ex_elyon pins the identical
    # region -- two independently transcribed elyon editions splitting where the vendored elyon
    # strand joins.  The יהיה split is Koren-alone: no vendored strand separates יהיה־לך and
    # simanim_ex_elyon does not either.  The .txt header states that asymmetry rather than hiding
    # it.  The chanted verse boundary at עבדים stays p-trad (9 verses, pinned below).
    "koren_ex_elyon": [
        ("", "mun", "לא"),
        ("", "mun", "ובנךובתך"),
    ],
    # Koren's Deuteronomy APPENDIX Decalogue (elyon, p. 39) diverges NOWHERE: 164 reference
    # tokens vs 164, agreeing at every accent.  It is the counterpart to koren_ex_elyon, and the
    # contrast is the point.  Where the Exodus elyon page SPLITS two maqaf compounds the vendored
    # strand joins (יהיה־לך and ובנך־ובתך), printing each atom as its own accented word, this page
    # JOINS both, matching dt/elyon/printed -- so that split is a fact about Koren's Exodus page,
    # not a house style.  Checked against all eight strands: none anywhere separates יהיה from לך,
    # and in Deuteronomy all four dt strands JOIN ובנך־ובתך.  That last is the REVERSE of Exodus,
    # where the two ex/taxton strands split ובנך and so corroborated the koren_ex_elyon split; in
    # Deuteronomy no strand splits it, so a split here would have been Koren-alone -- and Koren
    # makes none.  One token-invisible word-division difference is kept in the .txt but is not a
    # divergence: לא־תעשה is a maqaf compound on the page (mun-mun, line 12) where the reference
    # sets לא and תעשה apart, both munax, so the token stream is identical either way.  Three
    # transcription slips were corrected before this list: line 5 and line 8 each skipped a munax
    # on כי, and line 9 read ינקה as pazer where all eight strands (and the page) have pashta.
    "koren_dt_elyon": [],
    # Simanim TANAKH's Exodus main Decalogue (taxton, pp. 119-120) -- a different edition from
    # the Tiqqun though Feldheim publishes both, and the FIRST transcription pinned against a
    # MANUSCRIPT-tradition strand: the eight above are all against a printed-tradition one.  It
    # diverges NOWHERE: 142 reference tokens vs 142, agreeing at every accent, with the single
    # pasoleg (אתה) on its exact reference position.
    #
    # What makes the empty list worth more than the usual "no divergence survived a procedure
    # that only inspects candidate divergences" is the cross-strand re-run, and what makes it
    # worth LESS is how little this Decalogue can decide.  Both are in the .txt header; the
    # short form is that ex/taxton/manuscript and ex/taxton/printed differ in exactly THREE
    # regions and nowhere else in 142 tokens -- אנכי (pashta / tipexa), אלהיך (zaqef qatan /
    # etnaxta), and מבית עבדים (munax + etnaxta / merkha + silsof, the verse boundary pinned
    # below at 12).  This transcription takes the m-trad side of all three; the other 133 tokens
    # are identical in both traditions and so say nothing about which one the page follows.
    # A re-vendoring that moved any of the three fails here rather than quietly turning the
    # m-trad verdict into an unsupported one.
    "simanim_tanakh_ex_taxton": [],
    # Simanim TANAKH's Deuteronomy main Decalogue (taxton, pp. 297-298), the second m-trad pin
    # here and by far the sharper test: where the Exodus taxton's two strands differ in only
    # three regions, the two dt/taxton strands differ in EIGHT (issue #69 Result 6's five, plus
    # the word division at לא תעשה, plus the stroke count).  This transcription takes the m-trad
    # side of every one, so what is pinned below is the single place it agrees with NEITHER.
    #
    # qadma on ויום (5:13) where dt/taxton/manuscript -- and every other taxton strand -- has
    # pashta.  Confirmed off the page rather than corrected: Ben flagged it while typing as a
    # probable error in the edition and re-read it against a zoom.  All four ELYON strands do
    # have qadma there, but the elyon pairs it with geresh on השביעי where this page keeps the
    # taxton's zaqef qatan, so the page prints an elyon-shaped accent inside a taxton phrase
    # rather than an elyon phrase.  The pair it makes, qadma before zaqef qatan, is the one the
    # prose scanner reads as methiga-zaqef, so this is one attested zaqef phrase for another.
    #
    # It REMOVES a disjunctive, which is why this stem is absent from _SKELETON_UNTOUCHED -- the
    # second transcription of the ten whose divergence touches the skeleton, after
    # simanim_dt_taxton, and unlike that one it is a single word rather than a whole commandment.
    "simanim_tanakh_dt_taxton": [
        ("pash", "qad", "ויום"),
    ],
    # Simanim TANAKH's Exodus APPENDIX Decalogue (elyon, p. 350), the first ELYON pin from this
    # edition -- its two main-text Decalogues above are taxton -- and the third m-trad pin here.
    # It diverges NOWHERE: 142 reference tokens vs 142, agreeing at every accent, with all four
    # pasoleg strokes on their exact reference positions (16 פסל, 19 בשמים, 25 במים, 75 שבת).
    #
    # The empty list is worth more than the usual "no divergence survived a procedure that only
    # inspects candidate divergences", and for the same reason the Exodus taxton's is: the
    # cross-strand re-run.  ex/elyon/manuscript and ex/elyon/printed differ in exactly TWO regions
    # and nowhere else in 142 tokens -- אנכי (tipexa / pashta) and אלהיך ... עבדים (m-trad closing
    # the chanted verse at עבדים / p-trad running on, the boundary pinned below at 10) -- and this
    # transcription takes the m-trad side of both, the other 133 tokens being common to both
    # traditions.  It is the taxton pages' signature mirrored: there the m-trad ran ON at עבדים,
    # here it CLOSES there.
    #
    # One correction preceded this list, a transcription slip and not an edition divergence: p. 350
    # line 3 dropped one of the three munax that close on לא תעשה־לך פסל (20:4), the only difference
    # that survived against BOTH ex/elyon strands.  Restored on a re-read of the page.
    #
    # The four pasoleg strokes split two HOLLOW (narrow-sense paseq: 16 פסל, 19 בשמים) and two
    # SOLID (legarmeh: 25 במים, 75 שבת), each on its exact reference position and each solid one in
    # the legarmeh-before-revia environment.  It is the first Simanim TANAKH page to carry a hollow
    # bar at all -- both taxton pages had a single solid stroke -- but the contrast is not new to
    # the repo: the identical 2-and-2 split, at these same positions, is already on record in the
    # sibling Tiqqun's simanim_ex_elyon, the same reading in the other Feldheim edition.
    "simanim_tanakh_ex_elyon": [],
    # Simanim TANAKH's Deuteronomy APPENDIX Decalogue (elyon, p. 351) -- the LAST of issue #69's
    # fourteen, closing issue #72, and the fourth m-trad pin here.  It diverges NOWHERE: 164
    # reference tokens vs 164, agreeing at every accent, with all SEVEN pasoleg strokes on their
    # exact reference positions (16 פסל, 19 בשמים, 25 במים, 69 צוך, 79 שבת, 101 היית, 126 למען).
    #
    # The empty list is worth more than the usual "no divergence survived a procedure that only
    # inspects candidate divergences", and for the same reason its Exodus counterpart's is: the
    # cross-strand re-run.  dt/elyon/manuscript and dt/elyon/printed differ in exactly TWO regions
    # and nowhere else in 164 tokens -- אנכי (tipexa / pashta) and אלהיך ... עבדים (m-trad closing
    # the chanted verse at עבדים / p-trad running on, the boundary pinned below at 10) -- and this
    # transcription takes the m-trad side of both, the other ~155 tokens being common to both
    # traditions.  It is the taxton pages' signature mirrored, exactly as p. 350 is: there the
    # m-trad ran ON at עבדים, here it CLOSES there.
    #
    # Two corrections preceded this list, both transcription slips and neither an edition
    # divergence: band 2 dropped the darga on אשר (5:6), which every manuscript strand has; band
    # 23 typed the geresh on שדהו (5:18) as a qadma, and geresh is what all four Deuteronomy
    # strands have there.  Both restored on a re-read of the page, the שדהו one flagged against
    # BOTH dt/elyon strands (the slip signature).
    #
    # The seven strokes split two HOLLOW (narrow-sense paseq: 16 פסל, 19 בשמים, each before a
    # pazer) and five SOLID (legarmeh: 25 במים, 69 צוך, 79 שבת, 101 היית, 126 למען, each before a
    # revia).  It is the richest stroke page from this edition -- the two taxton pages had one each
    # and p. 350 four -- but the 2-and-5 split is not new: the sibling Tiqqun's simanim_dt_elyon
    # has the same seven at the same positions, the same reading in the other Feldheim edition.
    "simanim_tanakh_dt_elyon": [],
}

# Chanted verse count per transcription -- the exceptionless claim, checked in both directions
# below.  The elyon's nine and the taxton's thirteen are the p-trad's own verse divisions.
_CHANTED_VERSES = {
    "simanim_ex_elyon": 9,
    "simanim_ex_taxton": 13,
    "simanim_dt_elyon": 9,
    "simanim_dt_taxton": 13,
    # The p-trad taxton's own division, and for Koren the ONE thing this Decalogue adjudicates:
    # עבדים takes etnaxta in ex/taxton/manuscript, which runs 12 chanted verses, but closes its
    # own verse in ex/taxton/printed, which runs 13.  Everything else on these pages is common
    # to both traditions.
    "koren_ex_taxton": 13,
    # Same boundary, in Deuteronomy: עבדים takes etnaxta in dt/taxton/manuscript (12 verses)
    # and closes its own verse in dt/taxton/printed (13).  Unlike Exodus, this is only one of
    # five discriminators the page reaches -- see the divergence pin above.
    "koren_dt_taxton": 13,
    # The elyon's own division, and the one thing this Decalogue was expected to reach: עבדים
    # closes its own verse in ex/elyon/manuscript (10 verses) but runs on in ex/elyon/printed
    # (9).  This transcription has 9, the printed side.  Its two divergences are both mid-verse,
    # so they leave the boundary count alone.
    "koren_ex_elyon": 9,
    # The elyon's own division again, in Deuteronomy: עבדים closes its own verse in
    # dt/elyon/manuscript (10) but runs on in dt/elyon/printed (9).  This transcription has 9,
    # the printed side, with no divergence anywhere to move a boundary.
    "koren_dt_elyon": 9,
    # The FIRST m-trad count pinned here, and the first that is not the printed tradition's.
    # Same boundary as every entry above, taken the other way: עבדים carries an etnaxta and the
    # chanted verse runs on into לא־יהיה לך, closing only at על־פני -- ex/taxton/manuscript's
    # twelve, against ex/taxton/printed's thirteen.  Corroborated off the page independently of
    # any mark, by the edition's own printed verse numbers, which run ב-יג: twelve.
    "simanim_tanakh_ex_taxton": 12,
    # The same m-trad twelve, in Deuteronomy: עבדים carries an etnaxta and the chanted verse
    # runs on into לא־יהיה לך, against dt/taxton/printed's thirteen.  Corroborated off the page
    # by the edition's own printed verse numbers, which run ו-יז: twelve.  This stem's one
    # divergence is mid-verse, so it cannot move a boundary.
    "simanim_tanakh_dt_taxton": 12,
    # The first ELYON count pinned here, and the mirror of the taxton twelves above: in the elyon
    # the boundary at עבדים falls the OTHER way -- עבדים CLOSES its own chanted verse in
    # ex/elyon/manuscript (10 verses) but runs on in ex/elyon/printed (9).  This transcription has
    # 10, the m-trad side, with no divergence anywhere to move a boundary.
    "simanim_tanakh_ex_elyon": 10,
    # The second ELYON count pinned here, in Deuteronomy, and the same m-trad ten as its Exodus
    # counterpart: עבדים CLOSES its own chanted verse in dt/elyon/manuscript (10 verses) but runs
    # on in dt/elyon/printed (9).  This transcription has 10, the m-trad side, with no divergence
    # anywhere to move a boundary.
    "simanim_tanakh_dt_elyon": 10,
}

# Stems whose every divergence differs in a CONJUNCTIVE only, leaving the disjunctive skeleton
# intact.  This was once true of every transcription and the test below said so unconditionally
# -- until simanim_dt_taxton, whose Shabbat commandment swaps disjunctive for disjunctive
# (geresh -> pazer, revia -> telisha gedola, zaqef qatan -> revia).  That is what makes it a
# TRADITION difference rather than the word-division and conjunctive-marking quirks the other
# three amount to, so it is pinned as its own claim below rather than excused as an exception.
_SKELETON_UNTOUCHED = {
    "simanim_ex_elyon",
    "simanim_ex_taxton",
    "simanim_dt_elyon",
    "koren_ex_taxton",
    "koren_dt_taxton",
    # Its two divergences insert a munax each -- a conjunctive -- where Koren splits a maqaf
    # compound the reference joins, so no disjunctive is added or removed.  A word-division
    # difference, like simanim_ex_elyon, not the disjunctive swap simanim_dt_taxton makes.
    "koren_ex_elyon",
    # Zero divergences at all, so nothing touches the skeleton -- the strongest case here.
    "koren_dt_elyon",
    # Zero divergences too, and against a manuscript-tradition strand.
    "simanim_tanakh_ex_taxton",
    # Zero divergences too -- the elyon counterpart of simanim_tanakh_ex_taxton, against a
    # manuscript-tradition strand.
    "simanim_tanakh_ex_elyon",
    # Zero divergences too, and the last of the fourteen -- the Deuteronomy counterpart of
    # simanim_tanakh_ex_elyon, against a manuscript-tradition strand.
    "simanim_tanakh_dt_elyon",
}

# Transcriptions carrying a reading the transcriber flagged as not fully read off the page,
# stem -> how many.  Pinned because this is the one doubt the review loop CANNOT surface: a
# reading supplied from expectation agrees with the reference by construction, so it sits in
# the agreeing majority nothing re-reads, and an empty divergence list absorbs it silently.
# Pinning the count is what stops the flag evaporating when the .txt is re-derived.
_UNCERTAIN_READINGS = {
    # p. 114 line 1, the לא of לא תרצח: taken as merkha partly from expectation, the mark
    # being unclear on the scan.  Bounded by what the word discriminates -- all four taxton
    # strands have merkha there and all four elyon tipexa, so it is a taxton/elyon
    # discriminator, not a p-trad/m-trad one, and cannot touch the finding above.  To be
    # checked against the physical book (Ben regains access about 2026-09-08).
    "koren_ex_taxton": 1,
    # p. 281 line 2, the tipexa on את־שמו: an artifact overlies the mark, from the scan or the
    # printing.  Bounded even more tightly than the Exodus one -- ALL EIGHT strands have tipexa
    # there, so it discriminates nothing whatever and at worst is a lone accent against every
    # strand.  Ben raised the doubt during transcription with a provisional "?" suffix, which
    # is not supported notation; it moved here and survives in the line's corrected_from.
    "koren_dt_taxton": 1,
}


def _source_or_skip() -> dict:
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    return pd.load_source(src)


def _transcriptions() -> list[et.Transcription]:
    found = et.load_all_transcriptions()
    if not found:
        pytest.skip(f"no transcriptions committed under {et.transcriptions_dir()}")
    return found


def test_every_transcription_names_a_real_strand() -> None:
    """Each transcription's (book, reading, tradition) triple resolves in the vendored data."""
    source = _source_or_skip()
    for transcription in _transcriptions():
        tokens, _, _ = et.reference_tokens(source, transcription.key)
        assert tokens, f"{transcription.label}: strand resolved to no accents"


@pytest.mark.parametrize("stem", sorted(_EXPECTED_DIVERGENCES))
def test_divergences_are_exactly_as_established(stem: str) -> None:
    """The divergence set is pinned, region by region, with the word each sits on."""
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    got = [
        (" ".join(d.reference), " ".join(d.transcribed), pds.base_skeleton(d.word))
        for d in et.compare(source, transcription)
    ]
    assert got == _EXPECTED_DIVERGENCES[stem]


@pytest.mark.parametrize("stem", sorted(_CHANTED_VERSES))
def test_every_chanted_verse_boundary_agrees(stem: str) -> None:
    """The exceptionless claim: Simanim has the p-trad strand's own verse divisions.

    Weaker than accent agreement and independent of it -- every known divergence is mid-verse
    -- and it is the claim the Simanim page's title actually rests on.  Checked in both
    directions: the counts match, AND no difference region touches a silsof, which a bare
    count would not catch if one boundary moved and another appeared.
    """
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    ref, _, _ = et.reference_tokens(source, transcription.key)
    assert ref.count("silsof") == _CHANTED_VERSES[stem]
    assert list(transcription.tokens).count("silsof") == ref.count("silsof")
    for difference in et.compare(source, transcription):
        assert "silsof" not in difference.reference + difference.transcribed


_CONJUNCTIVE_OR_ABSENT = {"", "mun", "mer", "mah", "dar", "qad", "tq", "mer2"}


@pytest.mark.parametrize("stem", sorted(_SKELETON_UNTOUCHED))
def test_pinned_divergences_leave_the_disjunctive_skeleton_alone(stem: str) -> None:
    """No divergence adds or removes a disjunctive: every one differs in a conjunctive only.

    This is what licenses saying Simanim follows the p-trad's accent STRUCTURE while denying
    that it follows it in every accent -- a distinction the Exodus taxton makes load-bearing,
    since two of its three divergences really are accent differences rather than word-division
    ones.  Scoped to _SKELETON_UNTOUCHED: it is not true of the Deuteronomy taxton, and the
    test below pins that it is not.
    """
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    for difference in et.compare(source, transcription):
        for token in difference.reference + difference.transcribed:
            assert (
                token in _CONJUNCTIVE_OR_ABSENT
            ), f"{difference.describe()}: not conjunctive"


def test_deuteronomy_taxton_does_touch_the_disjunctive_skeleton() -> None:
    """The Shabbat departure swaps disjunctive for disjunctive, and that is the point.

    Pinned in the positive direction so the distinction cannot erode from either end: if a
    re-vendoring or a corrected transcription ever made these divergences conjunctive-only,
    this fails rather than letting the page keep calling p. 247 an m-trad departure.  Every
    other transcription's divergences leave the skeleton alone; this one's must not.
    """
    stem = "simanim_dt_taxton"
    assert stem not in _SKELETON_UNTOUCHED
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    disjunctives = {
        token
        for difference in et.compare(source, transcription)
        for token in difference.reference + difference.transcribed
        if token not in _CONJUNCTIVE_OR_ABSENT
    }
    assert disjunctives == {"paz", "tg", "pash", "zaq"}


def test_simanim_tanakh_deuteronomy_drops_one_disjunctive() -> None:
    """The second stem to touch the skeleton, and it touches it the other way.

    simanim_dt_taxton above swaps disjunctive FOR disjunctive across a whole commandment, which
    is what makes it a tradition difference.  This one replaces a single pashta with a qadma, so
    it REMOVES a disjunctive and adds nothing -- an edition's own departure, not a tradition's.
    Pinned positively for the same reason as that test: a re-vendoring that made this
    conjunctive-only, or a re-read that made the divergence vanish, should fail here rather than
    quietly turning "follows dt/taxton/manuscript except at one word" into an unqualified claim.
    """
    stem = "simanim_tanakh_dt_taxton"
    assert stem not in _SKELETON_UNTOUCHED
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    removed = [
        token
        for difference in et.compare(source, transcription)
        for token in difference.reference
        if token not in _CONJUNCTIVE_OR_ABSENT
    ]
    added = [
        token
        for difference in et.compare(source, transcription)
        for token in difference.transcribed
        if token not in _CONJUNCTIVE_OR_ABSENT
    ]
    assert removed == ["pash"]
    assert added == []


@pytest.mark.parametrize(
    "written,expected",
    [
        ("זר", "zar"),  # zarqa: ז alone would also reach זקף
        ("פז", "paz"),  # pazer: פ alone would also reach פשטא
        ("סג", "seg"),  # segolta: ס alone would also reach סילוק
        ("סגולתא", "seg"),  # the full name always works
        ("זקף", "zaq"),  # an exact name beats any longer name extending it
        ("גרשיים", "ger2"),
        ("גר", "ger"),  # agreed shorthand: a prefix of גרש and גרשיים alike
        ("תג", "tg"),  # a letter per word, so not a prefix of תלישא גדולה at all
        ("מונ_לגרמיה", "mun_leg"),
        ("מונ_לג", "mun_leg"),
    ],
)
def test_hebrew_token_resolves_by_unique_prefix(written: str, expected: str) -> None:
    """Any unique prefix of an accent's Hebrew name names it; the full name always does.

    This is what lets a page be transcribed without first agreeing a spelling for every
    accent it might contain -- the rule the earlier fixed table could not offer.
    """
    assert et.hebrew_token(written) == expected


@pytest.mark.parametrize("written", ["ז", "פ", "ס", "מ", "ת"])
def test_ambiguous_prefixes_are_rejected_not_guessed(written: str) -> None:
    """A prefix reaching more than one name is an error naming the candidates."""
    with pytest.raises(ValueError, match="ambiguous"):
        et.hebrew_token(written)


def test_a_modifier_cannot_stand_alone_as_an_accent() -> None:
    """לגרמיה names a mark bound into an accent, not an accent, so it is not a token."""
    with pytest.raises(ValueError, match="unknown"):
        et.hebrew_token("לגרמיה")


@pytest.mark.parametrize(
    "written,expected",
    [
        ("[פסק]", "paseq"),
        ("[paseq]", "paseq"),  # the .txt's spelling of the same aside
        ("[פסלג]", "unspecified"),
        ("[pasoleg]", "unspecified"),
    ],
)
def test_an_aside_records_the_kind_it_names(written: str, expected: str) -> None:
    """Three pasoleg kinds, and the aside says which -- it is no longer assumed.

    ``unspecified`` is what an edition that prints the stroke WITHOUT distinguishing legarmeh
    from narrow-sense paseq needs; Koren is one, so writing מונ_לג or [פסק] there would assert
    something the book does not say.  Both spellings resolve, because the editor takes Hebrew
    and the .txt is written in ASCII.
    """
    assert et.aside_kind(written) == expected


@pytest.mark.parametrize("written", ["[page break]", "[p. 209]", "[]"])
def test_an_unknown_aside_raises_rather_than_becoming_a_paseq_claim(
    written: str,
) -> None:
    """The old fallback made every unrecognized aside a silent narrow-sense-paseq claim.

    Positional asides like these live only in .txt bodies today, which ``_pasolegs`` never
    reads; if one ever reaches an export, raising forces the vocabulary to be extended
    deliberately instead of quietly asserting the strongest of the three kinds.
    """
    with pytest.raises(ValueError, match="unknown transcription aside"):
        et.aside_kind(written)


def test_txt_lines_keeps_the_printed_line_structure_and_the_asides() -> None:
    """The .txt body is DERIVED from the export: one .txt line per printed line, asides kept.

    Asides are dropped from both token streams, so the body is the only place a reader of the
    committed file sees that a stroke stood there and which kind it was.  A maqaf compound
    split by a line break lands on the line it STARTED on, as everywhere else.
    """
    maqaf = "\N{HEBREW PUNCTUATION MAQAF}"
    lines = [f"מונח{maqaf}", "מרכא [פסלג] קדמא+גרש", "מונ_לג [פסק]"]
    assert et.txt_lines(lines) == [
        "mun-mer",
        "[pasoleg] qad+ger",
        "mun_leg [paseq]",
    ]


def _export_pages(stem: str) -> list[dict]:
    """One transcription's editor export(s): a two-page Decalogue holds one per page."""
    record = json.loads(
        (et.transcriptions_dir() / f"{stem}.json").read_text(encoding="utf-8")
    )
    return record.get("pages", [record])


def _kind_agnostic_stems() -> list[str]:
    """Transcriptions whose header says the edition does not distinguish the two kinds."""
    return sorted(
        t.path.stem
        for t in et.load_all_transcriptions()
        if t.header.get("pasoleg_kinds") == "not distinguished"
    )


@pytest.mark.parametrize("stem", _kind_agnostic_stems() or ["(none committed)"])
def test_a_kind_agnostic_edition_asserts_no_kind_anywhere(stem: str) -> None:
    """``pasoleg_kinds: not distinguished`` must hold in BOTH files and BOTH spellings.

    Whether an edition distinguishes legarmeh from narrow-sense paseq is a fact about the
    physical book that is recorded nowhere else, so the header records it -- and this is what
    makes the header load-bearing rather than decorative.  Checking one file or one spelling
    would miss half the ways the overclaim can re-enter: the committed files write asides in
    ASCII in the .txt and in Hebrew in the JSON, and מונ_לג/mun_leg asserts legarmeh without
    an aside at all.

    Scoped to where notation can actually LIVE -- the .txt's non-comment lines and the
    export's typed line texts -- rather than to the raw bytes of each file.  Scanning whole
    files fails on a header that explains why the edition uses none of these, which is exactly
    the prose a reader most needs; a guard that forbids naming the thing it forbids is too
    blunt to keep.
    """
    if not _kind_agnostic_stems():
        pytest.skip("no kind-agnostic transcription committed")
    txt = et.transcriptions_dir() / f"{stem}.txt"
    written = [
        line
        for line in txt.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    typed = [
        text
        for page in _export_pages(stem)
        for line in page["lines"]
        for text in (line["text"], line.get("corrected_from", ""))
    ]
    for source, lines in ((txt.name, written), (f"{stem}.json", typed)):
        for line in lines:
            for notation in et.KIND_ASSERTING:
                assert (
                    notation not in line
                ), f"{source} asserts a pasoleg kind: {notation} in {line!r}"


def _stems_with_exports() -> list[str]:
    """Transcriptions that have the line editor's JSON export committed beside them.

    All of them do, as of the simanim_ex_elyon redo: it was the last one transcribed before the
    editor existed, and re-doing it closed the gap.  The lookup stays a glob rather than a list
    because a transcription typed but not yet exported is the state this is meant to tolerate.
    """
    return sorted(p.stem for p in et.transcriptions_dir().glob("*.json"))


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_editor_export_and_txt_agree(stem: str) -> None:
    """The committed export and the .txt say the same thing, through ``hebrew_token``.

    The .txt is canonical for the parser, but it is written in a shorthand nobody typed; what
    was actually typed, line by line against page coordinates, is the JSON.  Without this the
    two could drift and the audit trail would quietly stop describing the .txt beside it.

    Checked along BOTH routes from the export, because there are two: ``hebrew_chunks``, which
    writes the .txt, and ``transcription_check``, which resolves an export directly to score it
    before it is committed.  They once split a chunk into accents separately, and when the
    SIMPLE_JOINER was added to the first only, the second went on rejecting ``qad+ger`` as an
    unknown abbreviation -- the .txt looked right and the check that guards it was broken.
    Both now go through ``et.editor_accents``; this is what would notice if they stopped.
    """
    if not _stems_with_exports():
        pytest.skip(f"no editor exports committed under {et.transcriptions_dir()}")
    path = et.transcriptions_dir() / f"{stem}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    # One Decalogue can span two printed pages, and then the audit trail holds one editor
    # export per page under "pages", in page order.  A single-page export is its own only page.
    exports = record.get("pages", [record])
    chunks = et.hebrew_chunks(
        [line["text"] for export in exports for line in export["lines"]]
    )
    from_export = [token for chunk in chunks for token in et.expand_chunk(chunk)]
    from_txt = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt").tokens
    assert from_export == list(from_txt)

    from_check, origin = tc._tokens_with_origin(exports)
    # The check side resolves but does not normalize -- normalization belongs to the
    # comparison -- so fold legarmeh onto a plain munax before comparing with the .txt.
    assert [et._normalize(t) for t in from_check] == list(from_txt)
    assert tc.UNRESOLVED not in from_check
    assert len(origin) == len(
        from_check
    ), "every token needs a printed line to go back to"


def test_the_check_counts_the_same_tokens_per_chunk_as_it_resolves() -> None:
    """``_pasolegs`` walks the token stream by counting, so its count must be the resolver's.

    It is a third user of "how many accents does this chunk hold", and the one whose being
    wrong is hardest to see: an undercount does not raise, it silently shifts every pasoleg
    reported after it onto the wrong token.  A ``qad+ger`` chunk counted as one accent did
    exactly that to the Deuteronomy taxton's lone legarmeh.
    """
    for stem in _stems_with_exports():
        record = json.loads(
            (et.transcriptions_dir() / f"{stem}.json").read_text(encoding="utf-8")
        )
        exports = record.get("pages", [record])
        counted = sum(
            len(et.editor_accents(chunk))
            for chunk, _, _ in tc._chunks_with_origin(exports)
            if not chunk.startswith("[")
        )
        resolved, _ = tc._tokens_with_origin(exports)
        assert counted == len(resolved), stem


@pytest.mark.parametrize(
    "chunk,expected",
    [
        ("qad", ["qad"]),
        ("mun_leg", ["mun_leg"]),  # UNIT_JOINER binds two marks into ONE accent
        ("mun-mer", ["mun", "mer"]),  # a maqaf compound, both atoms accented
        ("qad+ger", ["qad", "ger"]),  # a simple word bearing two accents
        ("mer-mun_leg", ["mer", "mun_leg"]),  # both kinds of joiner at once
    ],
)
def test_written_accents_splits_on_the_accent_joiners_only(
    chunk: str, expected: list[str]
) -> None:
    """A chunk holds one token per ACCENT: the maqaf and ``+`` split it, ``_`` does not."""
    assert et.written_accents(chunk) == expected


def test_editor_accents_maps_the_typed_maqaf_onto_the_written_joiner() -> None:
    """The editor records the literal maqaf that was typed; the .txt writes it as ``-``.

    Both joiners survive the trip, so the .txt keeps saying which of the two was on the page
    -- the word-division fact every difference has to be read against.
    """
    maqaf = "\N{HEBREW PUNCTUATION MAQAF}"
    assert et.editor_accents(f"מונח{maqaf}מרכא") == [("מונח", ""), ("מרכא", "-")]
    assert et.editor_accents("קדמא+גרש") == [("קדמא", ""), ("גרש", "+")]
    assert et.editor_accents("מונ_לגרמיה") == [("מונ_לגרמיה", "")]


def test_rejoin_carries_a_split_compound_across_an_intervening_aside() -> None:
    """A compound split by a line break rejoins even with an aside standing between.

    The rejoin once lived in two places that disagreed on exactly this case: ``hebrew_chunks``
    dropped asides before rejoining, so a compound continued across one, while the check tool
    kept asides in place and the aside then blocked the rejoin.  One implementation now
    (``rejoin_editor_chunks``), so pin its choice: the aside passes through, the compound
    continues, and the joined chunk keeps the origin of the line it STARTED on -- the line to
    go back and re-read.
    """
    maqaf = "\N{HEBREW PUNCTUATION MAQAF}"
    items = [
        (f"מונח{maqaf}", ("p246", 3)),
        ("[פסק]", ("p246", 3)),
        ("מרכא", ("p246", 4)),
    ]
    assert et.rejoin_editor_chunks(items) == [
        (f"מונח{maqaf}מרכא", ("p246", 3)),
        ("[פסק]", ("p246", 3)),
    ]


def test_to_reference_maps_through_the_diff_not_by_raw_index() -> None:
    """A transcribed index means nothing against a reference position until mapped.

    Inside an equal block the mapping is exact; inside a difference region the token has no
    reference counterpart, so the region's start comes back as an anchor flagged inexact --
    context to display, never a position that agrees.
    """
    opcodes = tc._opcodes(["a", "b", "c"], ["a", "x", "y", "b", "c"])
    assert tc._to_reference(0, opcodes) == (0, True)
    assert tc._to_reference(1, opcodes) == (1, False)  # inserted: no counterpart
    assert tc._to_reference(2, opcodes) == (1, False)
    assert tc._to_reference(3, opcodes) == (1, True)  # past the insertion: exact again
    assert tc._to_reference(4, opcodes) == (2, True)


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_pasolegs_land_on_reference_pasoleg_positions(stem: str) -> None:
    """Every pasoleg that maps exactly through the diff lands on a reference U+05C0 position.

    Pasolegs are the one check that does not share the review loop's asymmetry -- they are
    independent anchors -- but only in reference coordinates.  ``_pasolegs`` indexes the
    TRANSCRIBED stream, so each index goes through ``_to_reference`` first; comparing raw was
    the report's original sin, and on the Deuteronomy taxton it looked right only because two
    errors cancelled (see the test below).
    """
    if not _stems_with_exports():
        pytest.skip(f"no editor exports committed under {et.transcriptions_dir()}")
    source = _source_or_skip()
    pages = _export_pages(stem)
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    ref, words, _ = et.reference_tokens(source, transcription.key)
    got, _ = tc._tokens_with_origin(pages)
    opcodes = tc._opcodes(ref, got)
    spots = {i for i, w in enumerate(words) if et.PASEQ in w and ref[i] == "mun"}
    mapped = [tc._to_reference(j, opcodes) for j, _ in tc._pasolegs(pages)]
    assert {i for i, exact in mapped if exact} <= spots


def test_deuteronomy_taxton_pasoleg_is_transcribed_128_reference_127() -> None:
    """The lone legarmeh: transcribed token 128, reference token 127, on למען.

    Pinned numerically because this is where the two cancelling errors lived: ``_pasolegs``
    once counted ``qad+ger`` as one token (reporting 128 as 127), and the report compared
    that raw against reference positions -- where the net +1 of the Shabbat difference
    regions made the wrong 127 land on the right word.  Fixing the count alone made the
    report look WORSE (token 128 displayed as יאריכן, a word with no pasoleg at all); this
    holds both halves of the fix in place.

    The reference's own positions are pinned too: the p-trad has a second pasoleg at 84
    (אתה׀, inside the Shabbat commandment), and its absence from the page is part of the
    m-trad-departure finding -- the transcription and the m-trad have one pasoleg, the p-trad
    two.
    """
    source = _source_or_skip()
    pages = _export_pages("simanim_dt_taxton")
    transcription = et.load_transcription(
        et.transcriptions_dir() / "simanim_dt_taxton.txt"
    )
    ref, words, _ = et.reference_tokens(source, transcription.key)
    got, _ = tc._tokens_with_origin(pages)
    opcodes = tc._opcodes(ref, got)
    marked = tc._pasolegs(pages)
    assert [j for j, _ in marked] == [128]
    assert [tc._to_reference(j, opcodes) for j, _ in marked] == [(127, True)]
    assert pds.base_skeleton(words[127]) == "למען"
    spots = [i for i, w in enumerate(words) if et.PASEQ in w and ref[i] == "mun"]
    assert spots == [84, 127]
    assert pds.base_skeleton(words[84]) == "אתה"


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_uncertain_readings_are_pinned_in_both_the_export_and_the_txt_header(
    stem: str,
) -> None:
    """A flagged reading must survive in the JSON AND be declared in the .txt header.

    Both halves matter and for different reasons.  The JSON entry is the substance -- which
    word, what was taken, why -- and is what ``transcription_check`` prints on every run.  The
    header count is what a reader of the committed .txt sees without opening the export, and
    what would go missing first if the .txt were ever re-derived by something that did not
    know about the field.  Pinning them against each other, and both against this table, is
    what keeps a doubt from quietly becoming a claim.
    """
    if not _stems_with_exports():
        pytest.skip(f"no editor exports committed under {et.transcriptions_dir()}")
    expected = _UNCERTAIN_READINGS.get(stem, 0)
    found = et.uncertain_readings(_export_pages(stem))
    assert len(found) == expected
    header = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt").header
    assert int(header.get("uncertain_readings", 0)) == expected


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_the_derived_txt_body_holds_the_same_accents_as_the_export(stem: str) -> None:
    """``txt_lines`` and ``hebrew_chunks`` differ only in structure, never in accents.

    The derivation that writes a committed .txt is the one that keeps the printed lines and
    the asides, so it is not the function the export/txt agreement test runs through.  Pin
    that the two stay the same transcription: drop the asides and the line breaks from the
    derived body and the token stream must be identical.
    """
    if not _stems_with_exports():
        pytest.skip(f"no editor exports committed under {et.transcriptions_dir()}")
    lines = [line["text"] for export in _export_pages(stem) for line in export["lines"]]
    derived = [
        chunk
        for txt_line in et.txt_lines(lines)
        for chunk in txt_line.split()
        if not chunk.startswith("[")
    ]
    assert derived == et.hebrew_chunks(lines)


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_the_committed_txt_is_byte_for_byte_its_own_derived_body(stem: str) -> None:
    """``transcription_build --check``, graduated into the suite.

    The workflow doc calls the derive step mandatory -- "derive the .txt from the corrected
    export rather than typing it, so the two cannot drift" -- and the tests above enforce that
    the two say the same ACCENTS.  This is stronger and cheaper: the committed file must be
    exactly what re-deriving its body under its own header produces.  So the rule is now
    enforced by the tool that implements it rather than alongside it, and a hand-edited body
    line, a stale .txt, or a whitespace difference fails here rather than surviving because
    the token streams happen to agree.

    It is not hypothetical.  The per-transcription scratch scripts this replaced had already
    diverged on whether a page's TRAILING empty lines are dropped, and the .txt committed by
    the copy that did not carried a trailing blank line no derivation would produce.
    """
    if not _stems_with_exports():
        pytest.skip(f"no editor exports committed under {et.transcriptions_dir()}")
    committed = (et.transcriptions_dir() / f"{stem}.txt").read_text(encoding="utf-8")
    assert tb.derived_text(stem) == committed


def test_a_trailing_empty_band_is_dropped_per_page_and_an_interior_one_kept() -> None:
    """The rule the two scratch copies disagreed about, pinned.

    A band carrying no accent contributes an empty .txt line, and since the editor is built
    over the whole page by default, its bands run past the Decalogue's end -- eleven of them on
    p. 298, cleared as out of span.  Those are noise at the foot of a page and go.  An interior
    empty line stays: it is a printed line that really carries no accent, and dropping it would
    shift every line number after it away from the printed page.  Dropped PER PAGE, so an
    out-of-span band at the foot of the first page does not survive into the page marker.
    """
    record = {
        "pages": [
            {
                "stem": "demo_p350",
                "lines": [
                    {"n": 1, "text": "מונח"},
                    {"n": 2, "text": ""},
                    {"n": 3, "text": "מרכא"},
                    {"n": 4, "text": ""},
                    {"n": 5, "text": ""},
                ],
            },
            {
                "stem": "demo_p351",
                "lines": [{"n": 1, "text": "טפחא"}, {"n": 2, "text": ""}],
            },
        ]
    }
    assert tb.body_lines(record) == ["mun", "", "mer", "", "[p. 351]", "tip"]
