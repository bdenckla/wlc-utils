"""PLY yacc grammar: Phase-C expansion of acc2tre.y.

Stage 1 / Phase C (full grammar for Obadiah).  Extends the Phase-B subset with
the remaining accent families needed for 100% Obadiah parity: revia, geresh,
big_telisha, pazer, legarmeh.  Also extends the existing clause rules (zaqef,
tifcha, pashta, tevir) with the new clause variants that reference these families.

Deferred (not needed for Obadiah):
  - segolta, zarqa, shalshelet families (no occurrences in Obadiah)
  - mayela handling in tifcha_phrase (Phase D)
  - segolta_silluq_clause, segolta_atnach_clause (Phase E)
  - per-phrase `error` recovery productions (build the 51 oddball ERROR trees,
    none of which are in Obadiah; deferred to Phase E)
  - additional pashta_phrase / tevir_phrase variants from C grammar not needed
    for Obadiah (Phase E)

Grammar actions build trees with ply_tree.make_node / add_leaves, exactly as the
C actions call make_node / add_leaves.  Token values carry the leaf-name string
(yylval.leaf), so add_leaves uses p[i] verbatim.
"""

from __future__ import annotations

import sys

from ply import yacc

from accgram.ply_scanner import Token
from accgram.ply_tree import TN, add_leaves, make_node

# All 33 grammar tokens (declared even when unused by subsets, to mirror
# acc2tre.y's %token list and keep the token namespace stable).
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
                    | pashta_zaqef_clause
                    | revia_zaqef_clause"""
    p[0] = p[1]


def p_pashta_zaqef_clause(p):
    """pashta_zaqef_clause : pashta_clause zaqef_phrase
                           | pashta_clause pashta_zaqef_clause
                           | pashta_clause revia_zaqef_clause"""
    p[0] = make_node("zaqef_clause", p[1], p[2])


def p_revia_zaqef_clause(p):
    """revia_zaqef_clause : revia_clause zaqef_phrase
                          | revia_clause pashta_zaqef_clause
                          | revia_clause revia_zaqef_clause"""
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
                     | pashta_tifcha_clause
                     | revia_tifcha_clause"""
    p[0] = p[1]


def p_tevir_tifcha_clause(p):
    """tevir_tifcha_clause : tevir_clause tifcha_phrase
                           | tevir_clause tevir_tifcha_clause"""
    p[0] = make_node("tifcha_clause", p[1], p[2])


def p_pashta_tifcha_clause(p):
    """pashta_tifcha_clause : pashta_clause tifcha_phrase
                            | pashta_clause tevir_tifcha_clause
                            | pashta_clause pashta_tifcha_clause
                            | pashta_clause revia_tifcha_clause"""
    p[0] = make_node("tifcha_clause", p[1], p[2])


def p_revia_tifcha_clause(p):
    """revia_tifcha_clause : revia_clause tifcha_phrase
                           | revia_clause tevir_tifcha_clause
                           | revia_clause pashta_tifcha_clause
                           | revia_clause revia_tifcha_clause"""
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
    """tevir_clause : tevir_phrase
                    | legarmeh_tevir_clause
                    | geresh_tevir_clause
                    | big_telisha_tevir_clause
                    | pazer_tevir_clause"""
    p[0] = p[1]


def p_legarmeh_tevir_clause(p):
    """legarmeh_tevir_clause : legarmeh_phrase tevir_phrase
                             | legarmeh_phrase legarmeh_tevir_clause"""
    p[0] = make_node("tevir_clause", p[1], p[2])


def p_geresh_tevir_clause(p):
    """geresh_tevir_clause : geresh_clause tevir_phrase
                           | geresh_clause legarmeh_tevir_clause
                           | geresh_clause geresh_tevir_clause
                           | geresh_clause big_telisha_tevir_clause"""
    p[0] = make_node("tevir_clause", p[1], p[2])


def p_big_telisha_tevir_clause(p):
    """big_telisha_tevir_clause : big_telisha_clause tevir_phrase
                                | big_telisha_clause legarmeh_tevir_clause
                                | big_telisha_clause geresh_tevir_clause
                                | big_telisha_clause big_telisha_tevir_clause"""
    p[0] = make_node("tevir_clause", p[1], p[2])


def p_pazer_tevir_clause(p):
    """pazer_tevir_clause : pazer_clause tevir_phrase
                          | pazer_clause legarmeh_tevir_clause
                          | pazer_clause geresh_tevir_clause
                          | pazer_clause big_telisha_tevir_clause
                          | pazer_clause pazer_tevir_clause"""
    p[0] = make_node("tevir_clause", p[1], p[2])


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
    """pashta_clause : pashta_phrase
                     | legarmeh_pashta_clause
                     | geresh_pashta_clause
                     | big_telisha_pashta_clause
                     | pazer_pashta_clause"""
    p[0] = p[1]


def p_legarmeh_pashta_clause(p):
    """legarmeh_pashta_clause : legarmeh_phrase pashta_phrase
                              | legarmeh_phrase legarmeh_pashta_clause"""
    p[0] = make_node("pashta_clause", p[1], p[2])


def p_geresh_pashta_clause(p):
    """geresh_pashta_clause : geresh_clause pashta_phrase
                            | geresh_clause legarmeh_pashta_clause
                            | geresh_clause big_telisha_pashta_clause
                            | geresh_clause geresh_pashta_clause"""
    p[0] = make_node("pashta_clause", p[1], p[2])


def p_big_telisha_pashta_clause(p):
    """big_telisha_pashta_clause : big_telisha_clause pashta_phrase
                                 | big_telisha_clause legarmeh_pashta_clause
                                 | big_telisha_clause geresh_pashta_clause
                                 | big_telisha_clause big_telisha_pashta_clause"""
    p[0] = make_node("pashta_clause", p[1], p[2])


def p_pazer_pashta_clause(p):
    """pazer_pashta_clause : pazer_clause pashta_phrase
                           | pazer_clause legarmeh_pashta_clause
                           | pazer_clause geresh_pashta_clause
                           | pazer_clause big_telisha_pashta_clause
                           | pazer_clause pazer_pashta_clause"""
    p[0] = make_node("pashta_clause", p[1], p[2])


# --- revia ---------------------------------------------------------------------
def p_revia_phrase_revia(p):
    "revia_phrase : REVIA"
    p[0] = add_leaves("revia_phrase", p[1])


def p_revia_phrase_munach(p):
    "revia_phrase : MUNACH REVIA"
    p[0] = add_leaves("revia_phrase", p[1], p[2])


def p_revia_phrase_darga_munach(p):
    "revia_phrase : DARGA MUNACH REVIA"
    p[0] = add_leaves("revia_phrase", p[1], p[2], p[3])


def p_revia_phrase_munach_munach(p):
    "revia_phrase : MUNACH MUNACH REVIA"
    p[0] = add_leaves("revia_phrase", p[1], p[2], p[3])


def p_revia_phrase_munach_darga_munach(p):
    "revia_phrase : MUNACH DARGA MUNACH REVIA"
    p[0] = add_leaves("revia_phrase", p[1], p[2], p[3], p[4])


def p_revia_clause(p):
    """revia_clause : revia_phrase
                    | legarmeh_revia_clause
                    | geresh_revia_clause
                    | big_telisha_revia_clause
                    | pazer_revia_clause"""
    p[0] = p[1]


def p_legarmeh_revia_clause(p):
    """legarmeh_revia_clause : legarmeh_phrase revia_phrase
                             | legarmeh_phrase legarmeh_revia_clause"""
    p[0] = make_node("revia_clause", p[1], p[2])


def p_geresh_revia_clause(p):
    """geresh_revia_clause : geresh_clause revia_phrase
                           | geresh_clause legarmeh_revia_clause
                           | geresh_clause geresh_revia_clause"""
    p[0] = make_node("revia_clause", p[1], p[2])


def p_big_telisha_revia_clause(p):
    """big_telisha_revia_clause : big_telisha_clause revia_phrase
                                | big_telisha_clause legarmeh_revia_clause
                                | big_telisha_clause geresh_revia_clause
                                | big_telisha_clause big_telisha_revia_clause"""
    p[0] = make_node("revia_clause", p[1], p[2])


def p_pazer_revia_clause(p):
    """pazer_revia_clause : pazer_clause revia_phrase
                          | pazer_clause legarmeh_revia_clause
                          | pazer_clause geresh_revia_clause
                          | pazer_clause big_telisha_revia_clause
                          | pazer_clause pazer_revia_clause"""
    p[0] = make_node("revia_clause", p[1], p[2])


# --- geresh --------------------------------------------------------------------
def p_geresh_phrase_gershayim(p):
    "geresh_phrase : GERSHAYIM"
    p[0] = add_leaves("geresh_phrase", p[1])


def p_geresh_phrase_munach_gershayim(p):
    "geresh_phrase : MUNACH GERSHAYIM"
    p[0] = add_leaves("geresh_phrase", p[1], p[2])


def p_geresh_phrase_geresh(p):
    "geresh_phrase : GERESH"
    p[0] = add_leaves("geresh_phrase", p[1])


def p_geresh_phrase_munach_geresh(p):
    "geresh_phrase : MUNACH GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2])


def p_geresh_phrase_azla_geresh(p):
    "geresh_phrase : AZLA GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2])


def p_geresh_phrase_telq_azla(p):
    "geresh_phrase : TELISHAQETANNA AZLA GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2], p[3])


def p_geresh_phrase_munach_telq_azla(p):
    "geresh_phrase : MUNACH TELISHAQETANNA AZLA GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2], p[3], p[4])


def p_geresh_phrase_munach2_telq_azla(p):
    "geresh_phrase : MUNACH MUNACH TELISHAQETANNA AZLA GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2], p[3], p[4], p[5])


def p_geresh_phrase_munach3_telq_azla(p):
    "geresh_phrase : MUNACH MUNACH MUNACH TELISHAQETANNA AZLA GERESH"
    p[0] = add_leaves("geresh_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_geresh_clause(p):
    """geresh_clause : geresh_phrase
                     | legarmeh_geresh_clause"""
    p[0] = p[1]


def p_legarmeh_geresh_clause(p):
    """legarmeh_geresh_clause : legarmeh_phrase geresh_phrase
                              | legarmeh_phrase legarmeh_geresh_clause"""
    p[0] = make_node("geresh_clause", p[1], p[2])


# --- big_telisha ---------------------------------------------------------------
def p_big_telisha_phrase_telg(p):
    "big_telisha_phrase : TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1])


def p_big_telisha_phrase_munach(p):
    "big_telisha_phrase : MUNACH TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1], p[2])


def p_big_telisha_phrase_munach2(p):
    "big_telisha_phrase : MUNACH MUNACH TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1], p[2], p[3])


def p_big_telisha_phrase_munach3(p):
    "big_telisha_phrase : MUNACH MUNACH MUNACH TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1], p[2], p[3], p[4])


def p_big_telisha_phrase_munach4(p):
    "big_telisha_phrase : MUNACH MUNACH MUNACH MUNACH TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1], p[2], p[3], p[4], p[5])


def p_big_telisha_phrase_munach5(p):
    "big_telisha_phrase : MUNACH MUNACH MUNACH MUNACH MUNACH TELISHAGEDOLA"
    p[0] = add_leaves("big_telisha_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_big_telisha_clause(p):
    """big_telisha_clause : big_telisha_phrase
                          | legarmeh_big_telisha_clause"""
    p[0] = p[1]


def p_legarmeh_big_telisha_clause(p):
    """legarmeh_big_telisha_clause : legarmeh_phrase big_telisha_phrase
                                   | legarmeh_phrase legarmeh_big_telisha_clause"""
    p[0] = make_node("big_telisha_clause", p[1], p[2])


# --- pazer ---------------------------------------------------------------------
def p_pazer_phrase_pazer(p):
    "pazer_phrase : PAZER"
    p[0] = add_leaves("pazer_phrase", p[1])


def p_pazer_phrase_munach(p):
    "pazer_phrase : MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2])


def p_pazer_phrase_munach2(p):
    "pazer_phrase : MUNACH MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3])


def p_pazer_phrase_munach3(p):
    "pazer_phrase : MUNACH MUNACH MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4])


def p_pazer_phrase_munach4(p):
    "pazer_phrase : MUNACH MUNACH MUNACH MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5])


def p_pazer_phrase_munach5(p):
    "pazer_phrase : MUNACH MUNACH MUNACH MUNACH MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_pazer_phrase_munach6(p):
    "pazer_phrase : MUNACH MUNACH MUNACH MUNACH MUNACH MUNACH PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_pazer_phrase_galgal(p):
    "pazer_phrase : MUNACH GALGAL PAZERGADOL"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3])


def p_pazer_phrase_munach_galgal2(p):
    "pazer_phrase : MUNACH MUNACH GALGAL PAZERGADOL"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4])


def p_pazer_phrase_munach3_galgal(p):
    "pazer_phrase : MUNACH MUNACH MUNACH GALGAL PAZERGADOL"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5])


def p_pazer_phrase_munach4_galgal(p):
    "pazer_phrase : MUNACH MUNACH MUNACH MUNACH GALGAL PAZERGADOL"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_pazer_phrase_munach5_galgal(p):
    "pazer_phrase : MUNACH MUNACH MUNACH MUNACH MUNACH GALGAL PAZERGADOL"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_pazer_clause(p):
    """pazer_clause : pazer_phrase
                    | legarmeh_pazer_clause"""
    p[0] = p[1]


def p_legarmeh_pazer_clause(p):
    """legarmeh_pazer_clause : legarmeh_phrase pazer_phrase
                             | legarmeh_phrase legarmeh_pazer_clause"""
    p[0] = make_node("pazer_clause", p[1], p[2])


# --- legarmeh ------------------------------------------------------------------
def p_legarmeh_phrase_legarmeh(p):
    "legarmeh_phrase : LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1])


def p_legarmeh_phrase_mereka(p):
    "legarmeh_phrase : MEREKA LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2])


def p_legarmeh_phrase_azla_mereka(p):
    "legarmeh_phrase : AZLA MEREKA LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2], p[3])


def p_legarmeh_phrase_munach_mereka(p):
    "legarmeh_phrase : MUNACH MEREKA LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2], p[3])


def p_legarmeh_phrase_munach_munach(p):
    "legarmeh_phrase : MUNACH MUNACH LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2], p[3])


# --- error handling ------------------------------------------------------------
# Per-phrase error recovery productions (for the 51 oddball ERROR-node trees) are
# deferred to Phase E.  A verse that can't be parsed returns None; the driver
# records it as skipped.
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
