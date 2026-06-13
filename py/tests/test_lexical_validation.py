"""Unit tests for the prose lexical-validation layer (stranded stress-helpers).

Pin the pure-function semantics of `stranded_stress_helpers`: a prose `82` is an
alphabet error unless it is fused with a later `02` in the *same* maqaf/space-
delimited atom.  These guard the fuse-vs-strand and atom-boundary logic so a
regression fails here rather than silently shifting the oddball corpus.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_lexical_validation.py -v
"""

from __future__ import annotations

from accgram.lexical_validation import stranded_stress_helpers


def _codes(body: str) -> list[str]:
    return [m.code for m in stranded_stress_helpers(body)]


def test_bare_82_is_stranded():
    # gn 47:29-style: 82 with no later 02 anywhere -> stranded.
    assert _codes('YI&:RF)"82L]s') == ["82"]


def test_82_fused_with_later_02_same_atom_is_clean():
    # A real zarqa stress-helper: 82{TEXT}02 on one atom fuses into one ZARQA.
    assert _codes("X82Y02Z") == []


def test_82_two_letters_back_still_stranded():
    # gn 17:20: the 82 sits two letters before the lamed; still no 02 -> stranded.
    assert _codes('W.75/L:/YI$:MF("82)L]S]s') == ["82"]


def test_02_in_a_different_atom_does_not_rescue_82():
    # Maqaf/space ends the atom, so an 02 across the boundary cannot fuse.
    assert _codes("A82B-C02D") == ["82"]
    assert _codes("A82B C02D") == ["82"]


def test_02_before_82_does_not_fuse():
    # Fusion requires the 02 to follow the 82; an earlier 02 leaves it stranded.
    assert _codes("A02B82C") == ["82"]


def test_no_82_anywhere_is_clean():
    assert _codes("WA/Y.O71MER03 )ELOHI92YM00") == []


def test_atom_with_both_returns_the_atom_text():
    [mark] = stranded_stress_helpers('YI&:RF)"82L]s')
    assert mark.code == "82"
    assert mark.atom == 'YI&:RF)"82L]s'
