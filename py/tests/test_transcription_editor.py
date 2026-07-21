"""Tests for the per-line transcription editor's crop diagnostics.

``crop_warnings`` exists because both ways of misplacing a vertical crop are SILENT: the debug
overlay draws a plausible band for a clipped line and for a merged one alike.  The numbers
below are the real ones from Koren A5-D-281, where both mistakes were made in one sitting.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accgram.transcription_editor import crop_warnings  # noqa: E402

MEDIAN = 64  # a printed line on that page, in rendered pixels


def _levels(warnings):
    return [level for level, _ in warnings]


def test_a_crop_clear_of_its_neighbours_says_nothing():
    """The quiet case: every band a full line, none touching an edge."""
    bands = [(10, 74), (100, 164), (190, 254)]
    assert crop_warnings(bands, height=300) == []


def test_a_band_that_absorbed_a_clipped_sliver_warns():
    """Koren p. 281 at bottom 0.614: band 17 came out 117px against a median of 64.

    ``_absorb_slivers`` folds a sub-half-line fragment into its neighbour, which is right for
    a fragment shaved off by a split and wrong for a genuine next line the crop cut through.
    """
    bands = [(10, 74), (100, 217), (240, 304)]
    warnings = crop_warnings(bands, height=400)
    assert _levels(warnings) == ["WARNING"]
    assert "117px" in warnings[0][1] and "64px" in warnings[0][1]


def test_a_band_touching_the_crop_edge_is_a_note_not_a_warning():
    """Ambiguous by construction, so it must not cry wolf.

    On a CORRECT crop the outermost band is the half-line of context the Hebrew cropping rule
    asks for, and it necessarily touches the edge; on a wrong one it is a transcribed line cut
    short.  Both are simply short, so the geometry cannot separate them and the message states
    both readings instead of asserting one.
    """
    for bands, height in (([(0, 64), (100, 164)], 200), ([(10, 74), (100, 164)], 164)):
        warnings = crop_warnings(bands, height)
        assert _levels(warnings) == ["note"], bands
        assert "clipped if it is a line you mean to transcribe" in warnings[0][1]


def test_the_merge_trap_reports_both_at_once():
    """The 0.614 crop really did trip both: an over-tall band that also touched the edge."""
    bands = [(10, 74), (100, 164), (190, 307)]
    assert _levels(crop_warnings(bands, height=307)) == ["WARNING", "note"]


def test_no_bands_is_not_an_error():
    assert crop_warnings([], height=100) == []
