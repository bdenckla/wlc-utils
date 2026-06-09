"""End-to-end golden test: scanner -> grammar -> tree on real Obadiah input.

Phase C: all 20 Obadiah verses must parse byte-identical to the frozen oracle.
The grammar now covers revia / geresh / big_telisha / pazer / legarmeh families
in addition to the Phase-B set, so no verses are deferred.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_end_to_end_ob.py -v
"""

from pathlib import Path

import pytest

from accgram.compare_ply import _split_verses
from accgram.ply_grammar import build_parser, parse_tokens
from accgram.ply_scanner import HasLegarmeh, scan_accents, scan_book
from accgram.ply_tree import print_tree

_REPO_ROOT = Path(__file__).resolve().parents[2]
_OB_INPUT = (
    _REPO_ROOT.parent
    / "wlc-utils-io"
    / "out"
    / "goerwitz"
    / "wlc_422_psf"
    / "wlc_422_ps_ob.txt"
)
_OB_ORACLE = _REPO_ROOT / "out" / "accgram" / "goerwitz" / "wlc_422_ps_ob_ag.txt"

# Phase C: no verses are deferred; all 20 Obadiah verses should parse.
_DEFERRED: set[str] = set()


@pytest.mark.skipif(not _OB_INPUT.is_file(), reason="Obadiah input fixture not present")
def test_ob_1_2_tokens():
    """The scanner produces the expected token stream for Obadiah 1:2."""
    body = "HIN.\"71H QF+O91N N:TAT.I73Y/KF B.A/G.OWYI92M B.FZ71W.Y )AT.F73H M:)O75D00"
    types = [t.type for t in scan_accents(body, "Obadiah 1:2", HasLegarmeh())]
    assert types == [
        "MEREKA",
        "TEVIR",
        "TIFCHA",
        "ATNACH",
        "MEREKA",
        "TIFCHA",
        "SILLUQ",
        "SOFPASUQ",
    ]


@pytest.mark.skipif(not _OB_INPUT.is_file(), reason="Obadiah input fixture not present")
def test_ob_parsed_verses_match_oracle():
    """Every verse the Phase-B subset parses is byte-identical to the oracle."""
    oracle = _split_verses(_OB_ORACLE)
    parser = build_parser()
    parsed_refs = set()
    for verse in scan_book(_OB_INPUT.read_text(encoding="utf-8")):
        tree = parse_tokens(parser, verse.tokens)
        if tree is None:
            continue
        parsed_refs.add(verse.reference)
        got = verse.reference + "\n" + print_tree(tree, 0)
        assert got == oracle[verse.reference], f"mismatch at {verse.reference}"
    # The skeleton parses exactly the non-deferred verses.
    assert parsed_refs == set(oracle) - _DEFERRED
