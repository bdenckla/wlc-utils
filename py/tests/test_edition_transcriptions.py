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
}

# Chanted verse count per transcription -- the exceptionless claim, checked in both directions
# below.  The elyon's nine and the taxton's thirteen are the p-trad's own verse divisions.
_CHANTED_VERSES = {
    "simanim_ex_elyon": 9,
    "simanim_ex_taxton": 13,
    "simanim_dt_elyon": 9,
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


@pytest.mark.parametrize("stem", sorted(_EXPECTED_DIVERGENCES))
def test_pinned_divergences_leave_the_disjunctive_skeleton_alone(stem: str) -> None:
    """No divergence adds or removes a disjunctive: every one differs in a conjunctive only.

    This is what licenses saying Simanim follows the p-trad's accent STRUCTURE while denying
    that it follows it in every accent -- a distinction the taxton makes load-bearing, since
    two of its three divergences really are accent differences rather than word-division ones.
    """
    conjunctive_or_absent = {"", "mun", "mer", "mah", "dar", "qad", "tq", "mer2"}
    source = _source_or_skip()
    transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
    for difference in et.compare(source, transcription):
        for token in difference.reference + difference.transcribed:
            assert (
                token in conjunctive_or_absent
            ), f"{difference.describe()}: not conjunctive"


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


def _stems_with_exports() -> list[str]:
    """Transcriptions that have the line editor's JSON export committed beside them.

    Not all do: simanim_ex_elyon was transcribed before the editor existed.
    """
    return sorted(p.stem for p in et.transcriptions_dir().glob("*.json"))


@pytest.mark.parametrize("stem", _stems_with_exports() or ["(none committed)"])
def test_editor_export_and_txt_agree(stem: str) -> None:
    """The committed export and the .txt say the same thing, through ``hebrew_token``.

    The .txt is canonical for the parser, but it is written in a shorthand nobody typed; what
    was actually typed, line by line against page coordinates, is the JSON.  Without this the
    two could drift and the audit trail would quietly stop describing the .txt beside it.
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
