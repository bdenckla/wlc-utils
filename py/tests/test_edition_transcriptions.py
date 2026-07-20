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

import pytest

from accgram import edition_transcription as et
from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds

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


def test_simanim_ex_elyon_agrees_on_every_chanted_verse_boundary() -> None:
    """The exceptionless claim: Simanim's Exodus elyon has the p-trad elyon's verse divisions.

    Weaker than accent agreement and independent of it -- the two known divergences are
    mid-verse -- and it is the claim the Simanim page's title actually rests on.
    """
    source = _source_or_skip()
    transcription = et.load_transcription(
        et.transcriptions_dir() / "simanim_ex_elyon.txt"
    )
    ref, _, _ = et.reference_tokens(source, transcription.key)
    assert ref.count("silsof") == 9
    assert list(transcription.tokens).count("silsof") == ref.count("silsof")
    for difference in et.compare(source, transcription):
        assert "silsof" not in difference.reference + difference.transcribed


def test_known_divergences_leave_the_disjunctive_skeleton_alone() -> None:
    """Neither divergence adds or removes a disjunctive: both differ only in a conjunctive.

    This is what licenses saying Simanim follows the p-trad elyon's accent STRUCTURE while
    denying that it follows it in every accent.
    """
    conjunctive_or_absent = {"", "mun", "mer", "mah", "dar", "qad", "tq", "mer2"}
    source = _source_or_skip()
    transcription = et.load_transcription(
        et.transcriptions_dir() / "simanim_ex_elyon.txt"
    )
    for difference in et.compare(source, transcription):
        for token in difference.reference + difference.transcribed:
            assert (
                token in conjunctive_or_absent
            ), f"{difference.describe()}: not conjunctive"
