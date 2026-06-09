"""PLY yacc grammar: Phase-D completion of acc2tre.y (all non-error productions).

Stage 1 / Phase D.  Extends the Phase-C grammar with every remaining *non-error*
production from acc2tre.y, so all clean (non-oddball) verses parse:
  - segolta family (segolta_phrase incl. SHALSHELET, segolta_clause, zarqa/
    pashta/revia_segolta_clause) and its wiring into silluq_clause /
    atnach_clause via segolta_silluq_clause / segolta_atnach_clause;
  - zarqa family (zarqa_phrase, zarqa_clause, legarmeh/geresh/big_telisha/
    pazer_zarqa_clause);
  - METHIGAZAQEF as a zaqef_phrase; MAYELA variants in tifcha_phrase;
  - the remaining pashta_phrase and tevir_phrase servus combinations.

Result: 100% byte-parity on every clean verse across all 37 books.

Deferred to Phase E:
  - per-phrase `error` recovery productions (the 51 oddball ERROR-node trees)
    and the LOW_PRECEDENCE `pasuq : error` rule.  A verse that needs error
    recovery currently returns None (the driver records it as skipped/missing).

Grammar actions build trees with ply_tree.make_node / add_leaves, exactly as the
C actions call make_node / add_leaves.  Token values carry the leaf-name string
(yylval.leaf), so add_leaves uses p[i] verbatim.

Quirk reproduced: the C actions for `MAHPAK MAHPAK PASHTA` and
`MAHPAK MEREKA PASHTA` call add_leaves with count 2 (only $1,$2), dropping the
trailing PASHTA leaf; the Python actions pass only p[1],p[2] to match.
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
                     | segolta_silluq_clause
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


def p_segolta_silluq_clause(p):
    """segolta_silluq_clause : segolta_clause silluq_phrase
                             | segolta_clause tifcha_silluq_clause"""
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
                     | zaqef_atnach_clause
                     | segolta_atnach_clause"""
    p[0] = p[1]


def p_tifcha_atnach_clause(p):
    "tifcha_atnach_clause : tifcha_clause atnach_phrase"
    p[0] = make_node("atnach_clause", p[1], p[2])


def p_zaqef_atnach_clause(p):
    """zaqef_atnach_clause : zaqef_clause atnach_phrase
                           | zaqef_clause tifcha_atnach_clause
                           | zaqef_clause zaqef_atnach_clause"""
    p[0] = make_node("atnach_clause", p[1], p[2])


def p_segolta_atnach_clause(p):
    """segolta_atnach_clause : segolta_clause atnach_phrase
                             | segolta_clause tifcha_atnach_clause
                             | segolta_clause zaqef_atnach_clause"""
    p[0] = make_node("atnach_clause", p[1], p[2])


# --- zaqef ---------------------------------------------------------------------
def p_zaqef_phrase_zaqef(p):
    "zaqef_phrase : ZAQEF"
    p[0] = add_leaves("zaqef_phrase", p[1])


def p_zaqef_phrase_methigazaqef(p):
    # Methiga zaqef looks just like AZLA ZAQEF in the M-C BHS text.
    "zaqef_phrase : METHIGAZAQEF"
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


# --- segolta -------------------------------------------------------------------
# Pashta below = converted revia.  Segolta is like a strong zaqef.  Shalshelet
# is treated as a segolta_phrase variant (see segolta_phrase below).
def p_segolta_phrase_segolta(p):
    "segolta_phrase : SEGOLTA"
    p[0] = add_leaves("segolta_phrase", p[1])


def p_segolta_phrase_shalshelet(p):
    "segolta_phrase : SHALSHELET"
    p[0] = add_leaves("segolta_phrase", p[1])


def p_segolta_phrase_munach(p):
    "segolta_phrase : MUNACH SEGOLTA"
    p[0] = add_leaves("segolta_phrase", p[1], p[2])


def p_segolta_phrase_munach2(p):
    "segolta_phrase : MUNACH MUNACH SEGOLTA"
    p[0] = add_leaves("segolta_phrase", p[1], p[2], p[3])


def p_segolta_clause(p):
    """segolta_clause : segolta_phrase
                      | zarqa_segolta_clause
                      | pashta_segolta_clause
                      | revia_segolta_clause"""
    p[0] = p[1]


def p_zarqa_segolta_clause(p):
    """zarqa_segolta_clause : zarqa_clause segolta_phrase
                            | zarqa_clause zarqa_segolta_clause"""
    p[0] = make_node("segolta_clause", p[1], p[2])


def p_pashta_segolta_clause(p):
    """pashta_segolta_clause : pashta_clause segolta_phrase
                             | pashta_clause zarqa_segolta_clause
                             | pashta_clause pashta_segolta_clause
                             | pashta_clause revia_segolta_clause"""
    p[0] = make_node("segolta_clause", p[1], p[2])


def p_revia_segolta_clause(p):
    """revia_segolta_clause : revia_clause segolta_phrase
                            | revia_clause zarqa_segolta_clause
                            | revia_clause pashta_segolta_clause
                            | revia_clause revia_segolta_clause"""
    p[0] = make_node("segolta_clause", p[1], p[2])


# --- tifcha --------------------------------------------------------------------
def p_tifcha_phrase_tifcha(p):
    "tifcha_phrase : TIFCHA"
    p[0] = add_leaves("tifcha_phrase", p[1])


def p_tifcha_phrase_mereka(p):
    "tifcha_phrase : MEREKA TIFCHA"
    p[0] = add_leaves("tifcha_phrase", p[1], p[2])


def p_tifcha_phrase_darga_merekakefula(p):
    "tifcha_phrase : DARGA MEREKAKEFULA TIFCHA"
    p[0] = add_leaves("tifcha_phrase", p[1], p[2], p[3])


# Mayela is a variant of tifcha: it can take a tevir before it (Jer 2:31) and
# azla before it (Dan 4:9,18), unlike a plain conjunctive.
def p_tifcha_phrase_mayela(p):
    "tifcha_phrase : MAYELA"
    p[0] = add_leaves("tifcha_phrase", p[1])


def p_tifcha_phrase_mereka_mayela(p):
    "tifcha_phrase : MEREKA MAYELA"
    p[0] = add_leaves("tifcha_phrase", p[1], p[2])


def p_tifcha_phrase_azla_mayela(p):
    "tifcha_phrase : AZLA MAYELA"
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


def p_tevir_phrase_azla_darga(p):
    "tevir_phrase : AZLA DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_phrase_azla_mereka(p):
    "tevir_phrase : AZLA MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_phrase_munach_darga(p):
    "tevir_phrase : MUNACH DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_phrase_munach_mereka(p):
    "tevir_phrase : MUNACH MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3])


def p_tevir_phrase_telq_azla_darga(p):
    "tevir_phrase : TELISHAQETANNA AZLA DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3], p[4])


def p_tevir_phrase_telq_azla_mereka(p):
    "tevir_phrase : TELISHAQETANNA AZLA MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3], p[4])


def p_tevir_phrase_munach_telq_azla_darga(p):
    "tevir_phrase : MUNACH TELISHAQETANNA AZLA DARGA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3], p[4], p[5])


def p_tevir_phrase_munach_telq_azla_mereka(p):
    "tevir_phrase : MUNACH TELISHAQETANNA AZLA MEREKA TEVIR"
    p[0] = add_leaves("tevir_phrase", p[1], p[2], p[3], p[4], p[5])


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


# --- zarqa ---------------------------------------------------------------------
# Before segolta (with only one exception - Isa 45:1).  Zarqa is probably a
# specially converted pashta, used before segolta.
def p_zarqa_phrase_zarqa(p):
    "zarqa_phrase : ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1])


def p_zarqa_phrase_munach(p):
    "zarqa_phrase : MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2])


def p_zarqa_phrase_mereka(p):
    "zarqa_phrase : MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2])


def p_zarqa_phrase_mereka_munach(p):
    "zarqa_phrase : MEREKA MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_mereka_mereka(p):
    "zarqa_phrase : MEREKA MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_munach_munach(p):
    "zarqa_phrase : MUNACH MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_munach_mereka(p):
    "zarqa_phrase : MUNACH MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_azla_munach(p):
    "zarqa_phrase : AZLA MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_azla_mereka(p):
    "zarqa_phrase : AZLA MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3])


def p_zarqa_phrase_telq_azla_munach(p):
    "zarqa_phrase : TELISHAQETANNA AZLA MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3], p[4])


def p_zarqa_phrase_telq_azla_mereka(p):
    "zarqa_phrase : TELISHAQETANNA AZLA MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3], p[4])


def p_zarqa_phrase_munach_telq_azla_munach(p):
    "zarqa_phrase : MUNACH TELISHAQETANNA AZLA MUNACH ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3], p[4], p[5])


def p_zarqa_phrase_munach_telq_azla_mereka(p):
    "zarqa_phrase : MUNACH TELISHAQETANNA AZLA MEREKA ZARQA"
    p[0] = add_leaves("zarqa_phrase", p[1], p[2], p[3], p[4], p[5])


def p_zarqa_clause(p):
    """zarqa_clause : zarqa_phrase
                    | legarmeh_zarqa_clause
                    | geresh_zarqa_clause
                    | big_telisha_zarqa_clause
                    | pazer_zarqa_clause"""
    p[0] = p[1]


def p_legarmeh_zarqa_clause(p):
    """legarmeh_zarqa_clause : legarmeh_phrase zarqa_phrase
                             | legarmeh_phrase legarmeh_zarqa_clause"""
    p[0] = make_node("zarqa_clause", p[1], p[2])


def p_geresh_zarqa_clause(p):
    """geresh_zarqa_clause : geresh_clause zarqa_phrase
                           | geresh_clause legarmeh_zarqa_clause
                           | geresh_clause big_telisha_zarqa_clause
                           | geresh_clause geresh_zarqa_clause"""
    p[0] = make_node("zarqa_clause", p[1], p[2])


def p_big_telisha_zarqa_clause(p):
    """big_telisha_zarqa_clause : big_telisha_clause zarqa_phrase
                                | big_telisha_clause legarmeh_zarqa_clause
                                | big_telisha_clause geresh_zarqa_clause
                                | big_telisha_clause big_telisha_zarqa_clause"""
    p[0] = make_node("zarqa_clause", p[1], p[2])


def p_pazer_zarqa_clause(p):
    """pazer_zarqa_clause : pazer_clause zarqa_phrase
                          | pazer_clause legarmeh_zarqa_clause
                          | pazer_clause geresh_zarqa_clause
                          | pazer_clause big_telisha_zarqa_clause
                          | pazer_clause pazer_zarqa_clause"""
    p[0] = make_node("zarqa_clause", p[1], p[2])


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


def p_pashta_phrase_mahpak_mahpak(p):
    # Quirk (Judg 15:13): C action is add_leaves(2, ..., $1, $2) -- the trailing
    # PASHTA leaf is intentionally dropped.  Reproduce by passing only p[1],p[2].
    "pashta_phrase : MAHPAK MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2])


def p_pashta_phrase_mahpak_mereka(p):
    # Quirk (1Sam 30:9; Exod 10:13): C action drops the trailing PASHTA leaf.
    "pashta_phrase : MAHPAK MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2])


def p_pashta_phrase_telq_azla_mahpak(p):
    "pashta_phrase : TELISHAQETANNA AZLA MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4])


def p_pashta_phrase_telq_azla_mereka(p):
    "pashta_phrase : TELISHAQETANNA AZLA MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4])


def p_pashta_phrase_m_telq_azla_mahpak(p):
    "pashta_phrase : MUNACH TELISHAQETANNA AZLA MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5])


def p_pashta_phrase_m_telq_azla_mereka(p):
    "pashta_phrase : MUNACH TELISHAQETANNA AZLA MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5])


def p_pashta_phrase_m2_telq_azla_mahpak(p):
    "pashta_phrase : MUNACH MUNACH TELISHAQETANNA AZLA MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_pashta_phrase_m2_telq_azla_mereka(p):
    "pashta_phrase : MUNACH MUNACH TELISHAQETANNA AZLA MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5], p[6])


def p_pashta_phrase_m3_telq_azla_mahpak(p):
    "pashta_phrase : MUNACH MUNACH MUNACH TELISHAQETANNA AZLA MAHPAK PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_pashta_phrase_m3_telq_azla_mereka(p):
    "pashta_phrase : MUNACH MUNACH MUNACH TELISHAQETANNA AZLA MEREKA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2], p[3], p[4], p[5], p[6], p[7])


def p_pashta_phrase_telq(p):
    "pashta_phrase : TELISHAQETANNA PASHTA"
    p[0] = add_leaves("pashta_phrase", p[1], p[2])


def p_pashta_phrase_munach_telq(p):
    "pashta_phrase : MUNACH TELISHAQETANNA PASHTA"
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
