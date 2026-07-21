"""Tests for the per-line transcription editor's crop diagnostics.

``crop_warnings`` exists because both ways of misplacing a vertical crop are SILENT: the debug
overlay draws a plausible band for a clipped line and for a merged one alike.  The numbers
below are the real ones from Koren A5-D-281, where both mistakes were made in one sitting.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from accgram.transcription_editor import crop_warnings, find_bands  # noqa: E402

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


# ---------------------------------------------------------------------------
# Trailing-line recovery.  Koren hangs a Decalogue's closing word on a line of its own; being
# horizontally short it clears the ink cutoff only faintly and only in fragments, so the
# min-height filter drops it as speckle -- a silent hole.  ``find_bands`` recovers it as a final
# band, but only from BELOW the last kept band, so the recovery cannot renumber a line already
# found: it is purely additive at the tail.  The numbers below are scaled so the cutoff lands at
# 0.04 (baseline 0 + INK_CUTOFF * a busy row of 0.5), a full line's ink is 60 * 0.5 = 30, and a
# single line stands 60px tall -- the same shape as the real Koren page, in round figures.

FULL_VALUE = 0.5  # a full line's per-row ink fraction; the cutoff falls at 0.04
# Five full printed lines: height 60, gaps 40 (wider than any within-line accent gap).
LINES = [(40, 100), (140, 200), (240, 300), (340, 400), (440, 500)]
BASE = [(a, b, FULL_VALUE) for a, b in LINES]


def _profile(length, blocks):
    """A row profile ``length`` rows long, blank but for ``blocks`` of ``(top, bottom, value)``."""
    prof = [0.0] * length
    for top, bottom, value in blocks:
        for i in range(top, bottom):
            prof[i] = value
    return prof


def test_a_hung_closing_word_is_recovered_as_a_final_band():
    """The bug: a short final line, split by sub-cutoff gaps into fragments each too short to
    keep and too far apart to merge, vanished entirely.

    Three faint clusters (0.06, just over the 0.04 cutoff) at 25px spacing stand in for the word;
    individually they are specks, together they are a line half again as tall as the threshold.
    """
    word = BASE + [
        (540, 548, 0.06),
        (548, 573, 0.02),  # sub-cutoff gap between letter cores
        (573, 580, 0.06),
        (580, 605, 0.02),
        (605, 609, 0.06),
    ]
    bands = find_bands(_profile(730, word))
    assert len(bands) == 6
    # Additive at the tail: the five full lines are untouched, the recovered word is appended.
    assert bands[:5] == [(40, 100), (140, 200), (240, 300), (340, 400), (440, 500)]
    assert bands[5] == (540, 609)  # bracketed from its first to its last inked row


def test_a_blank_bottom_margin_is_not_recovered_as_a_line():
    """The ordinary correct case: nothing hangs below the last line, so nothing is invented."""
    assert find_bands(_profile(730, BASE)) == [
        (40, 100),
        (140, 200),
        (240, 300),
        (340, 400),
        (440, 500),
    ]


def test_a_thin_decorative_rule_is_not_recovered():
    """A decorative rule is dense enough to clear the cutoff but only a few rows tall.  It fails
    the height gate -- a real line stands half a line tall even when it is horizontally short.
    """
    rule = BASE + [(540, 543, 0.7)]  # 3px, near-full width: high ink, no height
    assert len(find_bands(_profile(730, rule))) == 5


def test_a_faint_smudge_spanning_half_a_line_is_not_recovered():
    """The height gate alone would pass this: two faint marks 30px apart span half a line.  The
    ink gate is what rejects it -- there is too little ink between and within them to be a word.
    """
    smudge = BASE + [(540, 544, 0.045), (544, 574, 0.015), (574, 578, 0.045)]
    assert len(find_bands(_profile(730, smudge))) == 5


def test_a_line_clipped_to_a_stub_at_the_crop_bottom_is_not_recovered():
    """Word-like ink, but jammed against the image bottom with no margin below.  That is the
    signature of a next line the crop cut through, which ``crop_warnings`` should flag -- not a
    whole hung line to recover.  The bottom-clearance gate leaves it alone."""
    clipped = BASE + [
        (540, 548, 0.06),
        (548, 573, 0.02),
        (573, 580, 0.06),
        (580, 605, 0.02),
        (605, 611, 0.06),  # runs to the image bottom at 612
    ]
    assert len(find_bands(_profile(612, clipped))) == 5
