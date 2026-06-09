"""PLY yacc grammar: a Phase-B subset of acc2tre.y.

Stage 1 / Phase B (walking skeleton).  Translates the silluq / atnach / zaqef /
tifcha / tevir / pashta families one-to-one from acc2tre.y -- enough to make the
prose-cantillation Obadiah verses that use only those families byte-identical.

Deferred to Phase C (full grammar, family by family): revia, segolta, zarqa,
geresh, big_telisha, pazer, legarmeh, mayela, shalshelet -- and the per-clause
`error` recovery productions that build the 51 oddballs' ERROR trees.

Grammar actions build trees with ply_tree.make_node / add_leaves, exactly as the
C actions call make_node / add_leaves.  Token values carry the leaf-name string
(yylval.leaf), so add_leaves uses p[i] verbatim.
"""

from __future__ import annotations

import sys

from ply import yacc

from accgram.ply_scanner import Token
from accgram.ply_tree import TN, add_leaves, make_node

# All 33 grammar tokens (declared even when unused by the Phase-B subset, to
# mirror acc2tre.y's %token list and keep the token namespace stable).
tokens = (
    "TILDE",
    "SOFPASUQ",
    "SILLUQ",
    "ATNACH",
    "SEGOLTA",
    "SHALSHELET",
    "ZAQEF",
    "METHIGAZAQEF",
    "ZAQEFGADOL",
    "REVIA",
    "TIFCHA",
    "ZARQA",
    "PASHTA",
    "YETIV",
    "TEVIR",
    "GERESH",
    "GERSHAYIM",
    "PAZER",
    "PAZERGADOL",
    "TELISHAGEDOLA",
    "LEGARMEH",
    "MUNACH",
    "MAHPAK",
    "MEREKA",
    "MEREKAKEFULA",
    "DARGA",
    "AZLA",
    "TELISHAQETANNA",
    "GALGAL",
    "MAYELA",
)

start = "pasuq"


# --- pasuq ---------------------------------------------------------------------
def p_pasuq(p):
    "pasuq : TILDE silluq_clause SOFPASUQ"
    p[0] = p[2]


# --- silluq --------------------------------------------------------------------
def p_silluq_phrase_silluq(p):
    "silluq_phrase : SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1])


def p_silluq_phrase_mereka(p):
    "silluq_phrase : MEREKA SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1], p[2])


def p_silluq_clause(p):
    """silluq_clause : silluq_phrase
                     | tifcha_silluq_clause
                     | zaqef_silluq_clause
                     | atnach_silluq_clause"""
    p[0] = p[1]


def p_tifcha_silluq_clause(p):
    "tifcha_silluq_clause : tifcha_clause silluq_phrase"
    p[0] = make_node("silluq_clause", p[1], p[2])


def p_zaqef_silluq_clause(p):
    """zaqef_silluq_clause : zaqef_clause silluq_phrase
                           | zaqef_clause tifcha_silluq_clause
                           | zaqef_clause zaqef_silluq_clause"""
    p[0] = make_node("silluq_clause", p[1], p[2])


def p_atnach_silluq_clause(p):
    """atnach_silluq_clause : atnach_clause silluq_phrase
                            | atnach_clause tifcha_silluq_clause
                            | atnach_clause zaqef_silluq_clause"""
    p[0] = make_node("silluq_clause", p[1], p[2])


# --- atnach --------------------------------------------------------------------
def p_atnach_phrase_atnach(p):
    "atnach_phrase : ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1])


def p_atnach_phrase_munach(p):
    "atnach_phrase : MUNACH ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2])


def p_atnach_phrase_munach2(p):
    "atnach_phrase : MUNACH MUNACH ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2], p[3])


def p_atnach_clause(p):
    """atnach_clause : atnach_phrase
                     | tifcha_atnach_clause
                     | zaqef_atnach_clause"""
    p[0] = p[1]


def p_tifcha_atnach_clause(p):
    "tifcha_atnach_clause : tifcha_clause atnach_phrase"
    p[0] = make_node("atnach_clause", p[1], p[2])


def p_zaqef_atnach_clause(p):
    """zaqef_atnach_clause : zaqef_clause atnach_phrase
                           | zaqef_clause tifcha_atnach_clause
                           | zaqef_clause zaqef_atnach_clause"""
    p[0] = make_node("atnach_clause", p[1], p[2])


# --- zaqef ---------------------------------------------------------------------
def p_zaqef_phrase_zaqef(p):
    "zaqef_phrase : ZAQEF"
    p[0] = add_leaves("zaqef_phrase", p[1])


def p_zaqef_phrase_zaqefgadol(p):
    "zaqef_phrase : ZAQEFGADOL"
    p[0] = add_leaves("zaqef_phrase", p[1])


def p_zaqef_phrase_munach(p):
    "zaqef_phrase : MUNACH ZAQEF"
    p[0] = add_leaves("zaqef_phrase", p[1], p[2])


def p_zaqef_phrase_munach2(p):
    "zaqef_phrase : MUNACH MUNACH ZAQEF"
    p[0] = add_leaves("zaqef_phrase", p[1], p[2], p[3])


def p_zaqef_clause(p):
    """zaqef_clause : zaqef_phrase
                    | pashta_zaqef_clause"""
    p[0] = p[1]


def p_pashta_zaqef_clause(p):
    """pashta_zaqef_clause : pashta_clause zaqef_phrase
                           | pashta_clause pashta_zaqef_clause"""
    p[0] = make_node("zaqef_clause", p[1], p[2])


# --- tifcha --------------------------------------------------------------------
def p_tifcha_phrase_tifcha(p):
    "tifcha_phrase : TIFCHA"
    p[0] = add_leaves("tifcha_phrase", p[1])


def p_tifcha_phrase_mereka(p):
    "tifcha_phrase : MEREKA TIFCHA"
    p[0] = add_leaves("tifcha_phrase", p[1], p[2])


def p_tifcha_clause(p):
    """tifcha_clause : tifcha_phrase
                     | tevir_tifcha_clause
                     | pashta_tifcha_clause"""
    p[0] = p[1]


def p_tevir_tifcha_clause(p):
    """tevir_tifcha_clause : tevir_clause tifcha_phrase
                           | tevir_clause tevir_tifcha_clause"""
    p[0] = make_node("tifcha_clause", p[1], p[2])


def p_pashta_tifcha_clause(p):
    """pashta_tifcha_clause : pashta_clause tifcha_phrase
                            | pashta_clause tevir_tifcha_clause
                            | pashta_clause pashta_tifcha_clause"""
    p[0] = make_node("tifcha_clause", p[1], p[2])


# --- tevir ---------------------------------------------------------------------
def p_tevir_phrase_tevir(p):
    "tevir_phrase : TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1])


def p_tevir_phrase_darga(p):
    "tevir_phrase : DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2])


def p_tevir_phrase_mereka(p):
    "tevir_phrase : MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2])


def p_tevir_phrase_munach_darga(p):
    "tevir_phrase : MUNACH DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_phrase_munach_mereka(p):
    "tevir_phrase : MUNACH MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_clause(p):
    "tevir_clause : tevir_phrase"
    p[0] = p[1]


# --- pashta --------------------------------------------------------------------
def p_pashta_phrase_yetiv(p):
    "pashta_phrase : YETIV"
    p[0] = add_leaves("pashta_phrase", p[1])


def p_pashta_phrase_pashta(p):
    "pashta_phrase : PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1])


def p_pashta_phrase_mahpak(p):
    "pashta_phrase : MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2])


def p_pashta_phrase_mereka(p):
    "pashta_phrase : MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2])


def p_pashta_phrase_munach_mahpak(p):
    "pashta_phrase : MUNACH MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3])


def p_pashta_phrase_munach_mereka(p):
    "pashta_phrase : MUNACH MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3])


def p_pashta_phrase_azla_mahpak(p):
    "pashta_phrase : AZLA MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3])


def p_pashta_phrase_azla_mereka(p):
    "pashta_phrase : AZLA MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3])


def p_pashta_clause(p):
    "pashta_clause : pashta_phrase"
    p[0] = p[1]


# --- error handling ------------------------------------------------------------
# Phase B does not port the grammar's `error` recovery productions; a verse the
# subset can't parse simply fails (parse() returns None) and the driver skips it.
_HAD_ERROR = False


def p_error(p):  # noqa: D401  (PLY callback)
    global _HAD_ERROR
    _HAD_ERROR = True


class _LexToken:
    """Minimal PLY-compatible token object."""

    __slots__ = ("type", "value", "lineno", "lexpos", "lexer")

    def __init__(self, ttype: str, value: str):
        self.type = ttype
        self.value = value
        self.lineno = 0
        self.lexpos = 0
        self.lexer = None


class _TokenStream:
    """Adapts a list[Token] to PLY's lexer interface (input/token)."""

    def __init__(self, toks: list[Token]):
        self._it = iter(toks)

    def input(self, _s):  # PLY may call this; we ignore it.
        pass

    def token(self):
        try:
            t = next(self._it)
        except StopIteration:
            return None
        return _LexToken(t.type, t.leaf)


def build_parser():
    """Build the PLY parser (no table files, warnings silenced)."""
    return yacc.yacc(
        module=sys.modules[__name__],
        write_tables=False,
        debug=False,
        errorlog=yacc.NullLogger(),
    )


def parse_tokens(parser, toks: list[Token]) -> TN | None:
    """Parse one verse's token stream into a tree, or None on syntax error."""
    global _HAD_ERROR
    _HAD_ERROR = False
    result = parser.parse(lexer=_TokenStream(toks))
    if _HAD_ERROR:
        return None
    return result
