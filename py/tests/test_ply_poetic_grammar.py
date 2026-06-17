"""Smoke tests for the poetic (Three Books) PLY grammar.

The poetic grammar (accgram.ply_grammar_poetic) is derived from Yeivin ITM
#358-374, not from a C oracle, so these tests pin two things:

  1. the LALR table builds with no shift/reduce or reduce/reduce conflicts;
  2. hand-built poetic verse token streams parse into trees whose nesting matches
     Yeivin's disjunctive hierarchy (oleh-we-yored > atnah > revia mugrash >
     silluq; revia gadol / dehi / sinnor / revia qatan under them; pazer and
     legarmeh as the lesser dividers).

These are structural, not corpus-validated; they exercise the grammar, not a
golden oracle output.  Token-type names come from accgram.poetic_accent_names so
the (variable) transliterations are never re-typed as literals here.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_poetic_grammar.py -v
"""

from accgram import poetic_accent_names as pan
from accgram.ply_grammar_poetic import build_parser, parse_tokens
from accgram.ply_tree import print_tree


def _verse(*accents):
    """Build a (type, leaf) token stream: TILDE, accents..., SOFPASUQ.

    The leaf is just the lowercased token type (these grammar tests don't run the
    scanner, so the display string is arbitrary).
    """
    toks = [(pan.TILDE, "")]
    toks += [(a, a.lower()) for a in accents]
    toks.append((pan.SOFPASUQ, "sof pasuq"))
    return toks


def test_builds_without_conflicts():
    _parser, warnings = build_parser(capture_warnings=True)
    assert warnings.strip() == ""


def test_silluq_only():
    parser = build_parser()
    tree = parse_tokens(parser, _verse(pan.MUNAX, pan.SILLUQ))
    assert tree is not None
    assert print_tree(tree, 0) == "0 silluq_phrase\n  munax silluq \n"


def test_atnah_divided_verse():
    """A short verse: atnah is the great divider, silluq ends it."""
    parser = build_parser()
    tree = parse_tokens(parser, _verse(pan.MERKHA, pan.ATNAX, pan.MERKHA, pan.SILLUQ))
    assert tree is not None
    assert print_tree(tree, 0) == (
        "0 silluq_clause\n"
        "  1 atnach_phrase\n"
        "    merkha atnax \n"
        "  1 silluq_phrase\n"
        "    merkha silluq \n"
    )


def test_revia_mugrash_before_silluq():
    """Revia mugrash is the near divider before silluq, under atnah (#366)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.MUNAX, pan.ATNAX, pan.MERKHA, pan.REVIA_MUGRASH,
            pan.TARXA, pan.MUNAX, pan.SILLUQ,
        ),
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
            pan.REVIA_GADOL, pan.MERKHA, pan.REVIA_QATAN, pan.GALGAL, pan.OLEH_WEYORED,
            pan.MUNAX, pan.ATNAX, pan.MERKHA, pan.REVIA_MUGRASH, pan.SILLUQ,
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
            pan.PAZER, pan.LEGARMEH, pan.REVIA_GADOL, pan.MERKHA, pan.TSINNOR,
            pan.GALGAL, pan.OLEH_WEYORED,
            pan.MUNAX, pan.DEXI, pan.MERKHA, pan.ATNAX,
            pan.MERKHA, pan.REVIA_MUGRASH, pan.SILLUQ,
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
        parser, _verse(pan.SHALSHELET_GEDOLAH, pan.TARXA, pan.MUNAX, pan.SILLUQ)
    )
    assert tree is not None
    assert "shalshelet_gedolah_phrase" in print_tree(tree, 0)


# --- Phase 3: lower disjunctives directly subdividing higher domains ------------
# L (MAM-confirmed) uses a lower disjunctive directly within a higher domain when
# the unit is short, exactly as the prose silluq/atnah domains admit their lower
# dividers.  These pin the rank-ordered near-divider cascades added in Phase 3.


def test_legarmeh_directly_under_atnah():
    """legarmeh subdivides the atnah domain directly (Ps 31:15)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.LEGARMEH, pan.MUNAX, pan.MUNAX, pan.ATNAX,
            pan.REVIA_MUGRASH, pan.MERKHA, pan.SILLUQ,
        ),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    # legarmeh nests as a subdivider inside the atnah clause, above atnah's phrase
    assert "atnach_clause" in out
    assert out.index("legarmeh_phrase") < out.index("atnach_phrase")


def test_legarmeh_directly_before_silluq_under_revia_mugrash():
    """revia mugrash near-divides silluq, then legarmeh divides the final unit
    (Ps 3:1, ATNAX REVIA_MUGRASH LEGARMEH SILLUQ)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.MERKHA, pan.ATNAX, pan.REVIA_MUGRASH,
            pan.LEGARMEH, pan.ILLUY, pan.SILLUQ,
        ),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    # legarmeh is the last divider, immediately above the silluq phrase
    assert out.index("revia_mugrash_phrase") < out.index("legarmeh_phrase")
    assert out.index("legarmeh_phrase") < out.index("silluq_phrase")


def test_dehi_directly_before_silluq():
    """dehi may stand directly before silluq (Ps, ATNAX DEXI SILLUQ -- faithful to
    L; an L/MAM divergence the xcheck flags separately)."""
    parser = build_parser()
    tree = parse_tokens(
        parser, _verse(pan.MERKHA, pan.ATNAX, pan.DEXI, pan.MUNAX, pan.SILLUQ)
    )
    assert tree is not None
    out = print_tree(tree, 0)
    assert out.index("atnach_phrase") < out.index("dehi_phrase")
    assert out.index("dehi_phrase") < out.index("silluq_phrase")


def test_pazer_directly_before_silluq():
    """pazer directly before silluq in a short superscription (Ps 18:2, 30:1)."""
    parser = build_parser()
    tree = parse_tokens(parser, _verse(pan.PAZER, pan.TARXA, pan.MUNAX, pan.SILLUQ))
    assert tree is not None
    out = print_tree(tree, 0)
    assert "pazer_phrase" in out
    assert out.index("pazer_phrase") < out.index("silluq_phrase")


def test_sinnor_subdivides_revia_qatan_before_oleh():
    """When sinnor and revia qatan both precede oleh-we-yored, revia qatan is the
    near divider and sinnor subdivides its domain (Ps 13:6,
    LEGARMEH TSINNOR REVIA_QATAN OLEH_WEYORED ...)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.LEGARMEH, pan.TSINNOR, pan.REVIA_QATAN, pan.OLEH_WEYORED,
            pan.MERKHA, pan.ATNAX, pan.MERKHA, pan.SILLUQ,
        ),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    # revia_qatan_clause contains a sinnor subdivision, which contains legarmeh
    assert "revia_qatan_clause" in out
    assert out.index("sinnor_phrase") < out.index("revia_qatan_phrase")
    assert out.index("legarmeh_phrase") < out.index("sinnor_phrase")


def test_revia_qatan_requires_merka_servant():
    """Breuer Ch 11 §16, confirmed by both witnesses (servi_before oracle): the
    servant adjacent to a small revia' is merka (a mahpakh may precede it).  A
    merka-served small revia parses; a non-merka adjacent servant (here munah) does
    not, even though the position is otherwise valid.  This rule is faithful but
    currently inert on the corpus (L marks merka in 125/125 cases)."""
    parser = build_parser()
    tail = (pan.OLEH_WEYORED, pan.MERKHA, pan.ATNAX, pan.MERKHA, pan.SILLUQ)
    # merka adjacent, with a mahpakh before it ("a mahpakh precedes it") -> parses
    ok = parse_tokens(parser, _verse(pan.MAHAPAKH, pan.MERKHA, pan.REVIA_QATAN, *tail))
    assert ok is not None
    assert "revia_qatan_phrase" in print_tree(ok, 0)
    # munah adjacent to the small revia -> rejected (no parse)
    bad = parse_tokens(parser, _verse(pan.MUNAX, pan.REVIA_QATAN, *tail))
    assert bad is None


def test_missing_silluq_recovers_as_error_tree():
    """Category A: a verse with no silluq code (servi then sof pasuq) recovers into
    a tree whose silluq_phrase is ERROR, preserving the rest of the structure
    (Ps 37:31, MUNAX MUNAX ATNAX TARXA MUNAX)."""
    parser = build_parser()
    tree = parse_tokens(
        parser, _verse(pan.MUNAX, pan.MUNAX, pan.ATNAX, pan.TARXA, pan.MUNAX)
    )
    assert tree is not None
    out = print_tree(tree, 0)
    assert "atnach_phrase" in out  # the rest of the verse is preserved
    assert "ERROR" in out  # the absent silluq is flagged
    assert "silluq_phrase" in out


def test_misplaced_disjunctive_stays_no_parse():
    """A genuine hierarchy violation (sinnor before legarmeh, an L anomaly MAM
    reads differently) is NOT masked by error recovery -- parse_tokens returns None
    so the driver records an informative NO_PARSE line (Ps 68:20)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.MAHAPAKH, pan.MUNAX, pan.TSINNOR, pan.LEGARMEH, pan.MERKHA,
            pan.REVIA_MUGRASH, pan.MAHAPAKH, pan.ILLUY, pan.SILLUQ,
        ),
    )
    assert tree is None


def test_pazer_directly_under_atnah():
    """pazer subdivides the atnah domain directly, with legarmeh below it
    (LEGARMEH PAZER ATNAX REVIA_MUGRASH SILLUQ)."""
    parser = build_parser()
    tree = parse_tokens(
        parser,
        _verse(
            pan.LEGARMEH, pan.PAZER, pan.ATNAX,
            pan.REVIA_MUGRASH, pan.SILLUQ,
        ),
    )
    assert tree is not None
    out = print_tree(tree, 0)
    assert "atnach_clause" in out
    assert out.index("pazer_phrase") < out.index("atnach_phrase")
    assert out.index("legarmeh_phrase") < out.index("pazer_phrase")
