"""Unit tests for the prose lexical-validation layer (stranded stress-helpers).

Pin the pure-function semantics of `stranded_stress_helpers`: a prose tsinnorit
(M-C ``82``) is an alphabet error unless it is fused with a later zinor (M-C ``02``)
in the *same* maqaf/space-delimited atom.  These guard the fuse-vs-strand and
atom-boundary logic so a regression fails here rather than silently shifting the
oddball corpus.  Bodies are written over the Unicode mark alphabet (issue #9, Phase
2); arbitrary capital letters stand in for consonant filler.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_lexical_validation.py -v
"""

from __future__ import annotations

from accgram import accent_marks as am
from accgram.lexical_validation import illegal_below_pairs, stranded_stress_helpers

_TS = am.TSINNORIT  # M-C 82 (zarqa stress-helper)
_ZI = am.ZINOR      # M-C 02 (zinor / zarqa main)
_MA = am.MAHAPAKH   # U+05A4 (below)
_TI = am.TIPEXA     # U+0596 (below)


def _codes(body: str) -> list[str]:
    return [m.code for m in stranded_stress_helpers(body)]


def _below(body: str) -> list[str]:
    return [m.code for m in illegal_below_pairs(body)]


def test_bare_82_is_stranded():
    # gn 47:29-style: a tsinnorit with no later zinor anywhere -> stranded.
    assert _codes("YISRA" + _TS + "L]s") == ["82"]


def test_82_fused_with_later_02_same_atom_is_clean():
    # A real zarqa stress-helper: tsinnorit{TEXT}zinor on one atom fuses into one ZARQA.
    assert _codes("X" + _TS + "Y" + _ZI + "Z") == []


def test_82_two_letters_back_still_stranded():
    # gn 17:20: the tsinnorit sits two letters before the lamed; still no zinor -> stranded.
    assert _codes("W" + am.METEG + "LYISMA" + _TS + ")L]S]s") == ["82"]


def test_02_in_a_different_atom_does_not_rescue_82():
    # Maqaf/space ends the atom, so a zinor across the boundary cannot fuse.
    assert _codes("A" + _TS + "B-C" + _ZI + "D") == ["82"]
    assert _codes("A" + _TS + "B C" + _ZI + "D") == ["82"]


def test_02_before_82_does_not_fuse():
    # Fusion requires the zinor to follow the tsinnorit; an earlier zinor leaves it stranded.
    assert _codes("A" + _ZI + "B" + _TS + "C") == ["82"]


def test_no_82_anywhere_is_clean():
    assert _codes("WAYO" + am.MERKHA + "MER" + am.PASHTA + " )ELOHI" + am.ATNAX + "YM" + am.SOF_PASUQ) == []


def test_atom_with_both_returns_the_atom_text():
    body = "YISRA" + _TS + "L]s"
    [mark] = stranded_stress_helpers(body)
    assert mark.code == "82"
    assert mark.atom == body


# --- illegal same-letter below-pair (mahapakh!tipexa, lv25:20) -----------------


def test_mahapakh_tipexa_same_letter_is_illegal():
    # lv25:20 word נֹּאכַל: mahapakh + tipeḥa adjacent (one letter) -> illegal below-pair.
    assert _below("XX-XXX" + _MA + _TI + "X]c]n") == ["mahapakh!tipexa"]


def test_below_pair_matches_either_within_letter_order():
    # within-letter order is not meaningful; the reversed order is equally illegal.
    assert _below("X" + _TI + _MA + "X") == ["mahapakh!tipexa"]


def test_below_accents_on_different_letters_are_clean():
    # An X (base letter) between them => different letters => a legal sequence, not a pair.
    assert _below("X" + _MA + "X" + _TI + "X") == []


def test_below_accents_across_atom_boundary_are_clean():
    assert _below("X" + _MA + "-X" + _TI + "X") == []
    assert _below("X" + _MA + " X" + _TI + "X") == []


def test_no_below_pair_is_clean():
    assert _below("XX" + _MA + "X XXX" + _TI + "X" + am.SOF_PASUQ) == []
    assert _below("YISRA" + _TS + "L]s") == []  # a stranded 82 is not a below-pair
