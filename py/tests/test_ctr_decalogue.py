"""Pin CTR's two Decalogues against the reference strands (issue #73).

CTR (The Complete Tanach with Rashi, chabad.org) is a VENDORED STRAND, not a hand
transcription: digital, accent-exact Hebrew, compared at the GLYPH level because its encoding
cannot distinguish the lookalike accent pairs a reader resolves by grammar (see
``accgram/ctr_decalogue.py``).  These tests pin the surprise the comparison found and guard it
against a re-fetch or a re-vendoring that would quietly change it:

* CTR's Exodus 20 carries the ta'am ELYON word-accents (not the taxton expected of a running
  text), with its own numbered-verse-based division.
* CTR's Deuteronomy 5 is the taxton, division and all.

Every residual difference from the followed strand is CONJUNCTIVE -- the disjunctive skeleton,
which is what #69 claims survives, is intact in both books.

Skips if either vendored JSON is absent (regenerate via ctr_decalogue_fetch.py /
printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ctr_decalogue.py -v
"""

from __future__ import annotations

import pytest

from accgram import ctr_decalogue as cd
from accgram import ctr_decalogue_fetch as cdf
from accgram import printed_decalogue as pd

# (glyph-agreeing words, total words) established against the followed strand, and the exact
# set of residual chanted-word skeletons -- every one conjunctive-only.  Pinned so a re-fetch
# that moved an accent, or a fold that stopped hiding a lookalike pair, fails here.
_EXPECTED = {
    "ex": {
        "primary": "elyon",
        "agree": 139,
        "total": 142,
        # CTR prints a munax on the proclitic atom of two maqaf compounds (יהיה־לך, ובנך־ובתך)
        # and swaps a munax for the reference's merkha on one ואשר.  All conjunctive.
        "residuals": {"יהיהלך", "ואשר", "ובנךובתך"},
        "ctr_chanted_verses": 16,
    },
    "dt": {
        "primary": "taxton",
        "agree": 163,
        "total": 164,
        # A single munax/merkha swap on ולא.
        "residuals": {"ולא"},
        "ctr_chanted_verses": 13,
    },
}


def _ctr_or_skip() -> dict:
    path = cd.default_ctr_path()
    if not path.is_file():
        pytest.skip(
            f"vendored CTR Decalogue not present at {path} (run ctr_decalogue_fetch.py)"
        )
    return cd.load_ctr(path)


def _source_or_skip() -> dict:
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    return pd.load_source(src)


def test_vendored_ctr_has_both_decalogue_spans() -> None:
    """The snapshot holds Exodus 20:2-14 and Deuteronomy 5:6-18, 13 verses each."""
    ctr = _ctr_or_skip()
    assert set(ctr["chapters"]) == {"ex", "dt"}
    assert list(ctr["chapters"]["ex"]["decalogue_verses"]) == [
        f"20:{v}" for v in range(2, 15)
    ]
    assert list(ctr["chapters"]["dt"]["decalogue_verses"]) == [
        f"5:{v}" for v in range(6, 19)
    ]


@pytest.mark.parametrize("book", ["ex", "dt"])
def test_ctr_follows_its_strand_at_the_glyph_level(book: str) -> None:
    """CTR agrees with its followed strand at exactly the pinned word count."""
    ctr, source = _ctr_or_skip(), _source_or_skip()
    exp = _EXPECTED[book]
    cmp = cd.compare(ctr, source, book, exp["primary"])
    assert cmp.agree == exp["agree"]
    assert cmp.agree + len(cmp.diffs) == exp["total"]


@pytest.mark.parametrize("book", ["ex", "dt"])
def test_residual_differences_are_exactly_these_and_all_conjunctive(book: str) -> None:
    """The residuals are the pinned words, and every one leaves the disjunctive skeleton intact."""
    ctr, source = _ctr_or_skip(), _source_or_skip()
    exp = _EXPECTED[book]
    cmp = cd.compare(ctr, source, book, exp["primary"])
    assert {d.skeleton for d in cmp.diffs} == exp["residuals"]
    assert cmp.disjunctive_skeleton_intact
    for d in cmp.diffs:
        assert (
            d.conjunctive_only
        ), f"{d.skeleton}: {d.ctr} vs {d.strand} touches a disjunctive"


@pytest.mark.parametrize("book", ["ex", "dt"])
def test_the_cross_strand_agreement_collapses(book: str) -> None:
    """Against the OTHER tradition, agreement collapses -- the evidence the match is real.

    A clean match against the followed strand could in principle be an artifact of the glyph
    fold; that the SAME comparison against the other tradition falls apart is what rules that
    out.  Pinned loosely (a wide margin) rather than to an exact count, since the cross diff is
    not the finding and its exact difflib alignment is not worth freezing.
    """
    ctr, source = _ctr_or_skip(), _source_or_skip()
    exp = _EXPECTED[book]
    primary = cd.compare(ctr, source, book, exp["primary"])
    cross = cd.compare(ctr, source, book, cd.CROSS[book])
    assert cross.agree < primary.agree - 40


@pytest.mark.parametrize("book", ["ex", "dt"])
def test_ctr_chanted_verse_structure(book: str) -> None:
    """Deuteronomy shares the taxton's 13-verse division; Exodus keeps its own (16), the elyon
    word-accents notwithstanding -- it does not group the commandments the elyon way."""
    ctr, source = _ctr_or_skip(), _source_or_skip()
    exp = _EXPECTED[book]
    n_cv = len(cd.chanted_verses(ctr, book))
    assert n_cv == exp["ctr_chanted_verses"]
    strand_cv = cd.strand_chanted_verse_count(source, book, exp["primary"])
    if book == "dt":
        assert n_cv == strand_cv  # taxton division IS the numbered verses
    else:
        assert n_cv != strand_cv  # elyon groups into 9; CTR does not


def test_clean_verse_drops_rendering_cruft_but_keeps_the_qere() -> None:
    """clean_verse strips the ketiv note and section markers, keeps the accented qere text."""
    raw = (
        'foo <co:instructional ksiv="מצותו">'
        "מִצְוֺתָֽי</co:instructional>"
        '<span class="instructional ksiv"> (כתיב מצותו) </span>'
        ": ס bar:"
    )
    cleaned = cdf.clean_verse(raw)
    assert "<" not in cleaned and ">" not in cleaned
    assert "ס" not in cleaned.split()  # bare samekh section marker dropped
    assert "(" not in cleaned  # the ketiv parenthetical note is gone
    assert "מִצְוֺתָֽי" in cleaned  # the accented qere survives
