"""Regression test: a verse missing its sof pasuq is a flagged oddball, not a
no-output troublemaker.

The scanner recovers the verse-final silluq (so the anomaly is attributed to the
sof pasuq, not misread as a missing silluq) and appends a MISSING_SOFPASUQ
terminator; the grammar then flags the verse with a distinct sof_pasuq_phrase ERROR
leaf.  Clean verses (which end in code 00) are untouched.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_missing_sof_pasuq.py -v
"""

from __future__ import annotations

import pytest

from accgram.prose_ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.prose_scanner import scan_book
from accgram.tree import print_tree
from tests.mc_marks import mc_to_marks


def _parse_one(book: str, verse_line: str, bb: str = "xx") -> tuple[list[str], str]:
    """Scan + parse a single verse; return (token types, rendered tree).

    The verse bodies are written in the legacy M-C encoding for readability and
    converted to the Phase-2 mark alphabet here (issue #9).  `bb` is irrelevant to
    these sof-pasuq tests (none is a has_legarmeh passage), so it defaults to a dummy
    code.
    """
    cv, _sep, body = verse_line.partition(" ")
    verse_line = f"{cv} {mc_to_marks(body)}"
    verses = scan_book(f"{book}\n{verse_line}\n", bb)
    assert len(verses) == 1, f"expected one verse, got {len(verses)}"
    verse = verses[0]
    tree = parse_tokens(build_parser(), verse.tokens)
    assert tree is not None and tree is not LOCATION_ONLY, tree
    return [t.type for t in verse.tokens], print_tree(tree, 0)


def test_no_sof_pasuq_recovers_silluq_and_flags_sof_pasuq():
    # lv 19:1: ends in a silluq (75) with no sof pasuq (no 00).
    types, tree = _parse_one("Leviticus", r'19:1 WA/Y:DAB."71R Y:HWF73H )EL-MO$E71H L."/)MO75R]1')
    # The trailing silluq is recovered, then a synthetic terminator is appended.
    assert types[-2:] == ["SILLUQ", "MISSING_SOFPASUQ"]
    # The sof pasuq is flagged distinctly...
    assert "sof_pasuq_phrase" in tree and "ERROR" in tree
    # ...and the silluq is NOT misreported as missing (it parses as "merkha silluq").
    assert "merkha silluq" in tree


def test_pasoleg_recovers_silluq_and_flags_sof_pasuq():
    # ek 33:20: silluq (75) before a pasoleg (" P"), still no sof pasuq.
    types, tree = _parse_one(
        "Ezekiel",
        r'33:20 WA/):AMAR:T.E85M LO71) YIT.FK"73N D.E74REK: ):ADON/F92Y )I94Y$ '
        r'K.I/D:RFKF91Y/W )E$:P.O71W+ )ET/:KE73M B."71YT YI&:RF)"75L]p P',
    )
    assert types[-2:] == ["SILLUQ", "MISSING_SOFPASUQ"]
    assert "sof_pasuq_phrase" in tree and "merkha silluq" in tree


def test_missing_both_silluq_and_sof_pasuq_flags_both():
    # nu 25:19: ends in atnax (92), no silluq and no sof pasuq -> both flagged.
    types, tree = _parse_one("Numbers", r'25:19 WA/Y:HI73Y )AX:AR"74Y HA/M.AG."PF92H]1 P')
    assert types[-1] == "MISSING_SOFPASUQ"
    assert "SILLUQ" not in types  # nothing to recover
    assert "silluq_phrase" in tree and "sof_pasuq_phrase" in tree
    assert tree.count("ERROR") == 2


def test_clean_verse_is_untouched():
    # A normal verse (Obadiah 1:2) ends in sof pasuq (00): no synthetic terminator, no ERROR.
    types, tree = _parse_one(
        "Obadiah",
        r'1:2 HIN."71H QF+O91N N:TAT.I73Y/KF B.A/G.OWYI92M B.FZ71W.Y )AT.F73H M:)O75D00',
    )
    assert "MISSING_SOFPASUQ" not in types
    assert types[-1] == "SOFPASUQ"
    assert "ERROR" not in tree


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
