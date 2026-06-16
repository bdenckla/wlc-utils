"""PLY yacc grammar for the POETIC (Three Books) accent system.

This is the poetic counterpart of accgram.ply_grammar (which ports acc2tre.y, the
prose / Twenty-One Books grammar).  There is no Goerwitz C oracle for the poetic
books; the productions here are derived from Yeivin, *Introduction to the Tiberian
Masorah* (ITM), the section "The Accents of the Three Books" (Psalms, Proverbs,
and the poetic core of Job), paragraphs 358-374.  Section numbers are cited
inline.  See also mb_cmn.hebrew_accents, whose poetic conjunctive list cites ITM
#358 / #361.

Design: strict clause hierarchy, permissive servus chains.
  The *clause* rules encode Yeivin's disjunctive hierarchy strictly (this is the
  linguistically meaningful structure).  The *phrase* rules, by contrast, accept
  any run of conjunctive servi before a disjunctive, because Yeivin describes the
  poetic servi only loosely -- "up to N servi", "various combinations", "governed
  by intricate rules" -- and there is no oracle to pin exact patterns against.  So
  every ``D_phrase`` is just ``D`` optionally preceded by a ``servi`` chain; the
  particular servus counts/orders Yeivin documents (munah/merka before silluq,
  galgal+mahpak/azla before pazer, the galgal "v"-servus of oleh-we-yored, etc.)
  are admitted but not required.  Tightening the servus rules to what L actually
  attests is left to a corpus-validation pass.

Hierarchy of disjunctives (greater divider -> the divider one rank below it):

  silluq (verse end, #359)
    great division: oleh-we-yored (distant) OR atnah (close)             (#361)
    near division before silluq: revia mugrash / shalshelet gedolah  (#366, #371)
  oleh-we-yored (the main verse divider, #363)
    main subdivider: revia gadol; immediately preceded by revia qatan
    (no servus) or sinnor (with servus)                          (#363, #365, #368)
  atnah (#362)               -> dehi (near) / revia gadol (distant)  (#362, #364)
  revia gadol (#363)         -> pazer / legarmeh
  revia qatan (#368)         -> legarmeh only
  revia mugrash (#366-367)   -> pazer / legarmeh (with geresh, tifcha-like);
                                also dehi / revia gadol when "without geresh" it
                                acts as the main verse divider like atnah (#367)
  dehi (#364)                -> pazer / legarmeh
  sinnor (#365)              -> pazer / legarmeh
  pazer (#369)               -> legarmeh only
  legarmeh (#370)            -> (terminal lowest disjunctive)

Token disambiguation that the scanner (accgram.ply_scanner_poetic) performs and
this grammar relies on: the three revias share signs but are distinct tokens here
(REVIA_GADOL / REVIA_QATAN / REVIA_MUGRASH); the scanner separates them by the
geresh muqdam (mugrash) and by position (qatan only before oleh-we-yored, a bare
revia before silluq = mugrash without geresh, #391).

Grammar actions build trees with ply_tree.make_node / add_leaves, as the prose
grammar does, so accgram.ply_tree.print_tree renders poetic trees identically.
"""

from __future__ import annotations

import sys

from ply import yacc

from accgram import poetic_accent_names as pan
from accgram.ply_tree import add_leaves, make_node

# Token-type names come from poetic_accent_names (the single source of truth).  The
# terminals are still spelled literally in the p_* rule docstrings below because
# PLY parses those textually; this tuple keeps them pinned to the constants, and
# the parse / zero-conflict tests fail if a docstring terminal ever drifts.
#
# NOTE: the conjunctive shalshelet qetannah (#371) is a real poetic servus but
# occurs in only eight verses, each as one link in a chain of conjunctives before
# silluq/atnah/revia-mugrash-without-geresh.  Yeivin gives no exact chains, so it
# is left unmodeled (no token) rather than fabricated.
tokens = (
    # structure
    pan.TILDE,
    pan.SOFPASUQ,
    # disjunctives (greatest -> least)
    pan.SILLUQ,
    pan.OLEH_WEYORED,
    pan.ATNAX,
    pan.REVIA_GADOL,
    pan.REVIA_MUGRASH,
    pan.REVIA_QATAN,
    pan.DEXI,
    pan.TSINNOR,
    pan.PAZER,
    pan.LEGARMEH,
    pan.SHALSHELET_GEDOLAH,
    # conjunctive servi (ITM #358; GALGAL also serves oleh-we-yored, #363)
    pan.MUNAX,
    pan.MERKHA,
    pan.MAHAPAKH,
    pan.AZLA,
    pan.GALGAL,
    pan.ILLUY,
    pan.TARXA,
)

start = "pasuq"


# --- conjunctive servi (permissive chain, see module docstring) ----------------
def p_conj(p):
    """conj : MUNAX
            | MERKHA
            | MAHAPAKH
            | AZLA
            | GALGAL
            | ILLUY
            | TARXA"""
    p[0] = p[1]  # the leaf-name string


def p_servi_one(p):
    "servi : conj"
    p[0] = [p[1]]


def p_servi_many(p):
    "servi : servi conj"
    p[0] = p[1] + [p[2]]


# --- pasuq ---------------------------------------------------------------------
def p_pasuq(p):
    "pasuq : TILDE silluq_clause SOFPASUQ"
    p[0] = p[2]


# --- phrases (disjunctive + optional servus chain) -----------------------------
# One uniform pair of productions per disjunctive: the bare sign, or a servus
# chain followed by the sign.
def p_silluq_phrase(p):
    """silluq_phrase : SILLUQ
                     | servi SILLUQ"""
    _phrase(p, "silluq_phrase")


def p_oleh_weyored_phrase(p):
    """oleh_weyored_phrase : OLEH_WEYORED
                           | servi OLEH_WEYORED"""
    # The characteristic servus is the "v"-shaped sign, coded as galgal in L (the
    # same sign as pazer's servus; #363); mahpak/merka also occur.  The yored
    # (merka below the stress) is part of the oleh-we-yored sign and is folded into
    # the OLEH_WEYORED token by the scanner, not a servus.
    _phrase(p, "oleh_weyored_phrase")


def p_atnach_phrase(p):
    """atnach_phrase : ATNAX
                     | servi ATNAX"""
    _phrase(p, "atnach_phrase")


def p_revia_gadol_phrase(p):
    """revia_gadol_phrase : REVIA_GADOL
                          | servi REVIA_GADOL"""
    _phrase(p, "revia_gadol_phrase")


def p_revia_qatan_phrase(p):
    """revia_qatan_phrase : REVIA_QATAN
                          | servi REVIA_QATAN"""
    _phrase(p, "revia_qatan_phrase")


def p_revia_mugrash_phrase(p):
    """revia_mugrash_phrase : REVIA_MUGRASH
                            | servi REVIA_MUGRASH"""
    _phrase(p, "revia_mugrash_phrase")


def p_dehi_phrase(p):
    """dehi_phrase : DEXI
                   | servi DEXI"""
    _phrase(p, "dehi_phrase")


def p_sinnor_phrase(p):
    """sinnor_phrase : TSINNOR
                     | servi TSINNOR"""
    _phrase(p, "sinnor_phrase")


def p_pazer_phrase(p):
    """pazer_phrase : PAZER
                    | servi PAZER"""
    _phrase(p, "pazer_phrase")


def p_legarmeh_phrase(p):
    """legarmeh_phrase : LEGARMEH
                       | servi LEGARMEH"""
    _phrase(p, "legarmeh_phrase")


def p_shalshelet_gedolah_phrase(p):
    """shalshelet_gedolah_phrase : SHALSHELET_GEDOLAH
                                 | servi SHALSHELET_GEDOLAH"""
    _phrase(p, "shalshelet_gedolah_phrase")


def _phrase(p, label):
    """Shared action: build a phrase leaf from optional servi + the disjunctive."""
    if len(p) == 2:  # bare disjunctive
        p[0] = add_leaves(label, p[1])
    else:  # servi (a list) + disjunctive
        p[0] = add_leaves(label, *p[1], p[2])


# --- silluq clause (#359, #361, #366, #371) ------------------------------------
# The silluq domain is the whole verse.  Its near divider before silluq is revia
# mugrash or shalshelet gedolah; its great divider is atnah or oleh-we-yored.
# oleh-we-yored, when present, is the topmost divider and may contain an
# atnah-divided remainder before silluq.
def p_silluq_clause(p):
    """silluq_clause : silluq_phrase
                     | revia_mugrash_silluq_clause
                     | shalshelet_silluq_clause
                     | atnach_silluq_clause
                     | oleh_silluq_clause"""
    p[0] = p[1]


def p_revia_mugrash_silluq_clause(p):
    "revia_mugrash_silluq_clause : revia_mugrash_clause silluq_phrase"
    p[0] = make_node("silluq_clause", p[1], p[2])


def p_shalshelet_silluq_clause(p):
    "shalshelet_silluq_clause : shalshelet_gedolah_clause silluq_phrase"
    p[0] = make_node("silluq_clause", p[1], p[2])


def p_atnach_silluq_clause(p):
    """atnach_silluq_clause : atnach_clause silluq_phrase
                            | atnach_clause revia_mugrash_silluq_clause
                            | atnach_clause shalshelet_silluq_clause"""
    p[0] = make_node("silluq_clause", p[1], p[2])


def p_oleh_silluq_clause(p):
    """oleh_silluq_clause : oleh_clause silluq_phrase
                          | oleh_clause revia_mugrash_silluq_clause
                          | oleh_clause shalshelet_silluq_clause
                          | oleh_clause atnach_silluq_clause"""
    p[0] = make_node("silluq_clause", p[1], p[2])


# --- oleh-we-yored clause (#363, #365, #368) -----------------------------------
# Immediately preceded by revia qatan (no servus) or sinnor (with servus); the
# main subdivider of its domain is revia gadol, standing before that.
def p_oleh_clause(p):
    """oleh_clause : oleh_weyored_phrase
                   | revia_qatan_oleh_clause
                   | sinnor_oleh_clause
                   | revia_gadol_oleh_clause"""
    p[0] = p[1]


def p_revia_qatan_oleh_clause(p):
    "revia_qatan_oleh_clause : revia_qatan_clause oleh_weyored_phrase"
    p[0] = make_node("oleh_weyored_clause", p[1], p[2])


def p_sinnor_oleh_clause(p):
    "sinnor_oleh_clause : sinnor_clause oleh_weyored_phrase"
    p[0] = make_node("oleh_weyored_clause", p[1], p[2])


def p_revia_gadol_oleh_clause(p):
    """revia_gadol_oleh_clause : revia_gadol_clause oleh_weyored_phrase
                               | revia_gadol_clause revia_qatan_oleh_clause
                               | revia_gadol_clause sinnor_oleh_clause
                               | revia_gadol_clause revia_gadol_oleh_clause"""
    p[0] = make_node("oleh_weyored_clause", p[1], p[2])


# --- atnah clause (#362, #364) -------------------------------------------------
# Subdivided by dehi (near) or revia gadol (distant); revia gadol is the higher
# divider, so it may contain a dehi subdivision but not vice versa.
def p_atnach_clause(p):
    """atnach_clause : atnach_phrase
                     | dehi_atnach_clause
                     | revia_gadol_atnach_clause"""
    p[0] = p[1]


def p_dehi_atnach_clause(p):
    """dehi_atnach_clause : dehi_clause atnach_phrase
                          | dehi_clause dehi_atnach_clause"""
    p[0] = make_node("atnach_clause", p[1], p[2])


def p_revia_gadol_atnach_clause(p):
    """revia_gadol_atnach_clause : revia_gadol_clause atnach_phrase
                                 | revia_gadol_clause dehi_atnach_clause
                                 | revia_gadol_clause revia_gadol_atnach_clause"""
    p[0] = make_node("atnach_clause", p[1], p[2])


# --- revia gadol clause (#363) -------------------------------------------------
# A near/minor division is legarmeh; a distant/major one is pazer; pazer is the
# higher of the two and may contain legarmeh.
def p_revia_gadol_clause(p):
    """revia_gadol_clause : revia_gadol_phrase
                          | legarmeh_revia_gadol_clause
                          | pazer_revia_gadol_clause"""
    p[0] = p[1]


def p_legarmeh_revia_gadol_clause(p):
    """legarmeh_revia_gadol_clause : legarmeh_clause revia_gadol_phrase
                                    | legarmeh_clause legarmeh_revia_gadol_clause"""
    p[0] = make_node("revia_gadol_clause", p[1], p[2])


def p_pazer_revia_gadol_clause(p):
    """pazer_revia_gadol_clause : pazer_clause revia_gadol_phrase
                                | pazer_clause legarmeh_revia_gadol_clause
                                | pazer_clause pazer_revia_gadol_clause"""
    p[0] = make_node("revia_gadol_clause", p[1], p[2])


# --- revia qatan clause (#368) -------------------------------------------------
# The only subordinate disjunctive is legarmeh.
def p_revia_qatan_clause(p):
    """revia_qatan_clause : revia_qatan_phrase
                          | legarmeh_revia_qatan_clause"""
    p[0] = p[1]


def p_legarmeh_revia_qatan_clause(p):
    """legarmeh_revia_qatan_clause : legarmeh_clause revia_qatan_phrase
                                    | legarmeh_clause legarmeh_revia_qatan_clause"""
    p[0] = make_node("revia_qatan_clause", p[1], p[2])


# --- revia mugrash clause (#366-367) -------------------------------------------
# With the geresh stroke: the last disjunctive before silluq, like prose tifcha,
# subdivided by the lesser dividers pazer / legarmeh.  "Without the geresh" (a bare
# revia before silluq when the verse has no atnah) it acts as the main verse
# divider "like atnah", so it is also subdivided by dehi (near) and revia gadol
# (distant).  Both roles share the REVIA_MUGRASH token, so all four are allowed.
def p_revia_mugrash_clause(p):
    """revia_mugrash_clause : revia_mugrash_phrase
                            | legarmeh_revia_mugrash_clause
                            | pazer_revia_mugrash_clause
                            | dehi_revia_mugrash_clause
                            | revia_gadol_revia_mugrash_clause"""
    p[0] = p[1]


def p_legarmeh_revia_mugrash_clause(p):
    """legarmeh_revia_mugrash_clause : legarmeh_clause revia_mugrash_phrase
                                      | legarmeh_clause legarmeh_revia_mugrash_clause"""
    p[0] = make_node("revia_mugrash_clause", p[1], p[2])


def p_pazer_revia_mugrash_clause(p):
    """pazer_revia_mugrash_clause : pazer_clause revia_mugrash_phrase
                                  | pazer_clause legarmeh_revia_mugrash_clause
                                  | pazer_clause pazer_revia_mugrash_clause"""
    p[0] = make_node("revia_mugrash_clause", p[1], p[2])


def p_dehi_revia_mugrash_clause(p):
    """dehi_revia_mugrash_clause : dehi_clause revia_mugrash_phrase
                                 | dehi_clause dehi_revia_mugrash_clause"""
    p[0] = make_node("revia_mugrash_clause", p[1], p[2])


def p_revia_gadol_revia_mugrash_clause(p):
    """revia_gadol_revia_mugrash_clause : revia_gadol_clause revia_mugrash_phrase
                                        | revia_gadol_clause dehi_revia_mugrash_clause
                                        | revia_gadol_clause revia_gadol_revia_mugrash_clause"""
    p[0] = make_node("revia_mugrash_clause", p[1], p[2])


# --- dehi clause (#364) --------------------------------------------------------
def p_dehi_clause(p):
    """dehi_clause : dehi_phrase
                   | legarmeh_dehi_clause
                   | pazer_dehi_clause"""
    p[0] = p[1]


def p_legarmeh_dehi_clause(p):
    """legarmeh_dehi_clause : legarmeh_clause dehi_phrase
                            | legarmeh_clause legarmeh_dehi_clause"""
    p[0] = make_node("dehi_clause", p[1], p[2])


def p_pazer_dehi_clause(p):
    """pazer_dehi_clause : pazer_clause dehi_phrase
                         | pazer_clause legarmeh_dehi_clause
                         | pazer_clause pazer_dehi_clause"""
    p[0] = make_node("dehi_clause", p[1], p[2])


# --- sinnor clause (#365) ------------------------------------------------------
def p_sinnor_clause(p):
    """sinnor_clause : sinnor_phrase
                     | legarmeh_sinnor_clause
                     | pazer_sinnor_clause"""
    p[0] = p[1]


def p_legarmeh_sinnor_clause(p):
    """legarmeh_sinnor_clause : legarmeh_clause sinnor_phrase
                              | legarmeh_clause legarmeh_sinnor_clause"""
    p[0] = make_node("sinnor_clause", p[1], p[2])


def p_pazer_sinnor_clause(p):
    """pazer_sinnor_clause : pazer_clause sinnor_phrase
                           | pazer_clause legarmeh_sinnor_clause
                           | pazer_clause pazer_sinnor_clause"""
    p[0] = make_node("sinnor_clause", p[1], p[2])


# --- pazer clause (#369) -------------------------------------------------------
# The only subordinate disjunctive is legarmeh.
def p_pazer_clause(p):
    """pazer_clause : pazer_phrase
                    | legarmeh_pazer_clause"""
    p[0] = p[1]


def p_legarmeh_pazer_clause(p):
    """legarmeh_pazer_clause : legarmeh_clause pazer_phrase
                             | legarmeh_clause legarmeh_pazer_clause"""
    p[0] = make_node("pazer_clause", p[1], p[2])


# --- legarmeh clause (#370) ----------------------------------------------------
# The lowest disjunctive: no subordinate disjunctive, but legarmeh may repeat.
def p_legarmeh_clause(p):
    """legarmeh_clause : legarmeh_phrase
                       | legarmeh_clause legarmeh_phrase"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = make_node("legarmeh_clause", p[1], p[2])


# --- shalshelet gedolah clause (#371) ------------------------------------------
# A disjunctive in the second half before silluq (revia-mugrash rank).  As a rule
# it has no servi; distinct from the conjunctive shalshelet qetannah.
def p_shalshelet_gedolah_clause(p):
    "shalshelet_gedolah_clause : shalshelet_gedolah_phrase"
    p[0] = p[1]


# --- error callback ------------------------------------------------------------
def p_error(p):  # noqa: D401  (PLY callback)
    # No poetic error-recovery productions yet (the prose grammar's recovery is a
    # port of acc2tre.y; there is no poetic oracle).  On a syntax error PLY has
    # nothing to recover with, so parse_tokens returns None.
    pass


class _LexToken:
    """Minimal PLY-compatible token object (mirrors ply_grammar._LexToken)."""

    __slots__ = ("type", "value", "lineno", "lexpos", "lexer")

    def __init__(self, ttype: str, value: str):
        self.type = ttype
        self.value = value
        self.lineno = 0
        self.lexpos = 0
        self.lexer = None


class _TokenStream:
    """Adapts a list of (type, leaf) pairs to PLY's lexer interface."""

    def __init__(self, toks):
        self._it = iter(toks)

    def input(self, _s):  # PLY may call this; we ignore it.
        pass

    def token(self):
        try:
            ttype, leaf = next(self._it)
        except StopIteration:
            return None
        return _LexToken(ttype, leaf)


def build_parser(*, capture_warnings: bool = False):
    """Build the poetic PLY parser.

    With ``capture_warnings=True`` the LALR construction log (shift/reduce and
    reduce/reduce conflict warnings) is returned alongside the parser, for grammar
    development; otherwise warnings are silenced like the prose grammar.
    """
    if capture_warnings:
        import io
        import logging

        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        log = logging.getLogger("ply_grammar_poetic")
        log.handlers = [handler]
        log.setLevel(logging.WARNING)
        parser = yacc.yacc(
            module=sys.modules[__name__],
            write_tables=False,
            debug=False,
            errorlog=log,
        )
        return parser, buf.getvalue()
    return yacc.yacc(
        module=sys.modules[__name__],
        write_tables=False,
        debug=False,
        errorlog=yacc.NullLogger(),
    )


def parse_tokens(parser, toks):
    """Parse one poetic verse's token stream.

    ``toks`` is a list of (token_type, leaf_name) pairs beginning with
    ('TILDE', '') and ending with ('SOFPASUQ', 'sof pasuq').  Returns the tree
    (ply_tree.TN) or None if the parse fails.
    """
    return parser.parse(lexer=_TokenStream(toks))
