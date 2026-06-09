"""Phase E regression test: the 51 oddball ERROR-node trees.

Drives the real scanner -> grammar -> tree pipeline on each oddball verse body
(from _oddballs.json) and asserts the produced tree is byte-identical to the
frozen goerwitz oracle.  This locks in the `error`-token recovery productions
(ply_grammar's error-recovery section) that build the ERROR leaves.

The oracle reference line uses the full book name (e.g. "Genesis 32:24") while
_oddballs.json uses the book code (e.g. "gn 32:24"); we therefore compare only
the tree portion of each block (everything after the reference line), matched to
the oracle by (chapter, verse) within the verse's output_file.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_oddballs.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from accgram.compare_ply import _VERSE_LABEL_RE, _split_verses
from accgram.ply_grammar import build_parser, parse_tokens
from accgram.ply_scanner import HasLegarmeh, Token, scan_accents
from accgram.ply_tree import print_tree

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GOERWITZ = _REPO_ROOT / "out" / "accgram" / "goerwitz"
_ODDBALLS_JSON = _GOERWITZ / "_oddballs.json"


def _oddball_entries() -> list[dict]:
    if not _ODDBALLS_JSON.is_file():
        return []
    data = json.loads(_ODDBALLS_JSON.read_text(encoding="utf-8"))
    return data.get("oddballs", [])


def _tree_part(block: str) -> str:
    """Return a verse block with its first (reference) line stripped off."""
    _, _, rest = block.partition("\n")
    return rest


_ENTRIES = _oddball_entries()


@pytest.mark.skipif(not _ENTRIES, reason="_oddballs.json not present")
def test_oddball_count():
    """The frozen oracle defines exactly 51 oddball verses."""
    assert len(_ENTRIES) == 51


@pytest.mark.skipif(not _ENTRIES, reason="_oddballs.json not present")
@pytest.mark.parametrize("entry", _ENTRIES, ids=lambda e: e["ref"])
def test_oddball_tree_matches_oracle(entry):
    """Each oddball verse's ERROR-node tree is byte-identical to the oracle."""
    ref = entry["ref"]  # e.g. "gn 32:24" -> bb="gn", ch=32, vr=24
    left, vr_str = ref.rsplit(":", 1)
    _bb, ch_str = left.rsplit(" ", 1)
    ch, vr = int(ch_str), int(vr_str)
    body = entry["content"]
    oracle_path = _GOERWITZ / entry["output_file"]

    # Locate the oracle block for this (chapter, verse).
    oracle_verses = _split_verses(oracle_path)
    oracle_block = None
    for ref_line, block in oracle_verses.items():
        m = _VERSE_LABEL_RE.match(ref_line)
        if m and (int(m.group(1)), int(m.group(2))) == (ch, vr):
            oracle_block = block
            break
    assert oracle_block is not None, f"no oracle block for {ref}"

    parser = build_parser()
    tokens = [Token("TILDE", "")] + scan_accents(body, ref, HasLegarmeh())
    tree = parse_tokens(parser, tokens)
    assert tree is not None, f"{ref} failed to parse"

    got_tree = print_tree(tree, 0)
    assert "ERROR" in got_tree, f"{ref} produced no ERROR leaf"
    assert got_tree == _tree_part(oracle_block), f"tree mismatch at {ref}"
