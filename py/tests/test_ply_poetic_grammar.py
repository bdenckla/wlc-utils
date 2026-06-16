"""Smoke tests for the poetic (Three Books) PLY grammar.

The poetic grammar (accgram.ply_grammar_poetic) is derived from Yeivin ITM
#358-374, not from a C oracle, so these tests pin two things:

  1. the LALR table builds with no shift/reduce or reduce/reduce conflicts;
  2. hand-built poetic verse token streams parse into trees whose nesting matches
     Yeivin's disjunctive hierarchy (oleh-we-yored > atnah > revia mugrash >
     silluq; revia gadol / dehi / sinnor / revia qatan under them; pazer and
     legarmeh as the lesser dividers).

These are structural, not corpus-validated (no poetic scanner exists yet); they
exercise the grammar, not a golden oracle output.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_poetic_grammar.py -v
"""

from accgram.ply_grammar_poetic import build_parser, parse_tokens
from accgram.ply_tree import print_tree


def _verse(*accents):
    """Build a (type, leaf) token stream: TILDE, accents..., SOFPASUQ."""
    toks = [("TILDE", "")]
    toks += [(a, a.lower()) for a in accents]
    toks.append(("SOFPASUQ", "sof pasuq"))
    return toks


def test_builds_without_conflicts():
    _parser, warnings = build_parser(capture_warnings=True)
    assert warnings.strip() == ""


def test_silluq_only():
    parser = build_parser()
    tree = parse_tokens(parser, _verse("MUNACH", "SILLUQ"))
    assert tree is not None
    assert print_tree(tree, 0) == "0 silluq_phrase\n  munach silluq \n"


def test_atnah_divided_verse():
    """A short verse: atnah is the great divider, silluq ends it."""
    parser = build_parser()
    tree = parse_tokens(parser, _verse("MEREKA", "ATNACH", "MEREKA", "SILLUQ"))
    assert tree is not None
    assert print_tree(tree, 0) == (
        "0 silluq_clause\n"
        "  1 atnach_phrase\n"
        "    mereka atnach \n"
        "  1 silluq_phrase\n"
        "    mereka silluq \n"
    )


def test_revia_mugrash_before_silluq():
    """Revia mugrash is the near divider before silluq, under atnah (#366)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse("MUNACH", "ATNACH", "MEREKA", "REVIA_MUGRASH", "TARHA", "MUNACH", "SILLUQ"),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    assert "revia_mugrash_phrase" in out
    # revia mugrash nests inside the second-half silluq_clause, below atnah
    assert out.index("atnach_phrase") < out.index("revia_mugrash_phrase")


def test_oleh_weyored_is_topmost_divider():
    """oleh-we-yored divides the whole verse; atnah divides its second half (#361)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            "REVIA_GADOL", "MEREKA", "REVIA_QATAN", "ATNAH_HAFUKH", "OLEH_WEYORED",
            "MUNACH", "ATNACH", "MEREKA", "REVIA_MUGRASH", "SILLUQ",
        ),
    )
    assert tree is not None
    # top node is the verse silluq_clause; its left child is the oleh clause
    assert tree.label == "silluq_clause"
    assert tree.left.label == "oleh_weyored_clause"
    out = print_tree(tree, 0)
    # revia qatan stands immediately before oleh-we-yored
    assert "revia_qatan_phrase" in out
    assert "oleh_weyored_phrase" in out


def test_full_hierarchy_pazer_legarmeh_dehi_sinnor():
    """A verse exercising every rank: pazer/legarmeh under revia gadol, sinnor
    before oleh, dehi under atnah."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            "PAZER", "LEGARMEH", "REVIA_GADOL", "MEREKA", "SINNOR",
            "ATNAH_HAFUKH", "OLEH_WEYORED",
            "MUNACH", "DEHI", "MEREKA", "ATNACH",
            "MEREKA", "REVIA_MUGRASH", "SILLUQ",
        ),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    for label in (
        "pazer_phrase", "legarmeh_phrase", "revia_gadol_clause",
        "sinnor_phrase", "oleh_weyored_phrase", "dehi_phrase",
        "atnach_phrase", "revia_mugrash_phrase", "silluq_phrase",
    ):
        assert label in out, label


def test_shalshelet_gedolah_before_silluq():
    parser = build_parser()
    tree = parse_tokens(
        parser, _verse("SHALSHELET_GEDOLAH", "TARHA", "MUNACH", "SILLUQ")
    )
    assert tree is not None
    assert "shalshelet_gedolah_phrase" in print_tree(tree, 0)
