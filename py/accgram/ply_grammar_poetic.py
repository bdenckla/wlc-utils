"""PLY yacc grammar for the POETIC (Three Books) accent system.

This is the poetic counterpart of accgram.ply_grammar (which ports acc2tre.y, the
prose / Twenty-One Books grammar).  There is no Goerwitz C oracle for the poetic
books; the productions here are derived directly from Yeivin, *Introduction to the
Tiberian Masorah* (ITM), the section "The Accents of the Three Books" (Psalms,
Proverbs, and the poetic core of Job), paragraphs 358-374.  Section numbers are
cited inline.  See also accgram-adjacent mb_cmn.hebrew_accents, whose poetic
conjunctive list already cites ITM #358 / #361.

Hierarchy of disjunctives (greater divider -> the divider one rank below that
subdivides its domain), per Yeivin:

  silluq (verse end, ITM #359)
    great division: oleh-we-yored (distant) OR atnah (close)   (#361)
    near division before silluq: revia mugrash / shalshelet gedolah  (#366, #371)
  oleh-we-yored (the main verse divider, #363)
    main subdivider: revia gadol; immediately preceded by revia qatan (no
    servus) or sinnor (with servus)                            (#363, #365, #368)
  atnah (#362)
    subdivider: dehi (near) / revia gadol (distant)            (#362, #364)
  revia gadol (#363)        -> pazer (distant) / legarmeh (near)
  revia qatan (#368)        -> legarmeh only
  revia mugrash (#366)      -> pazer / legarmeh
  dehi (#364)               -> pazer / legarmeh
  sinnor (#365)             -> pazer / legarmeh
  pazer (#369)              -> legarmeh only
  legarmeh (#370)           -> (terminal lowest disjunctive)

As in the prose grammar, each disjunctive D gets:
  - a ``D_phrase`` rule: the disjunctive sign with its permitted conjunctive
    servi (the servus patterns are taken from Yeivin's described examples; where
    Yeivin says the rules are "intricate" or gives only rare examples, the open
    cases are noted rather than enumerated exhaustively -- this grammar has not
    yet been validated against the L corpus);
  - a ``D_clause`` rule: a ``D_phrase`` optionally preceded by a clause of each
    disjunctive that may subdivide D's domain.

Caveats (why this grammar is not yet wired into a driver):
  - Scanner disambiguation is unsolved.  Several poetic disjunctives share a
    Unicode sign and therefore a Michigan-Claremont code with each other or with
    a prose accent: the three revias (gadol/qatan/mugrash) are one dot (prose
    code 81); dehi and the conjunctive tarha both use the tifcha sign (73);
    sinnor uses the zarqa sign (02).  Telling them apart needs positional /
    contextual logic the prose ply_scanner does not perform, so a poetic scanner
    is future work.  This module therefore works on already-classified poetic
    token *types* and is exercised by hand-built token streams (see the module
    test) rather than by run_ply.
  - No error-recovery productions: the prose grammar's ``error`` rules are a
    faithful port of acc2tre.y's recovery; there is no analogous poetic oracle to
    reproduce, so error handling is deferred.

Grammar actions build trees with ply_tree.make_node / add_leaves, exactly as the
prose grammar does, so accgram.ply_tree.print_tree renders poetic trees in the
same indented format.
"""

from __future__ import annotations

import sys

from ply import yacc

from accgram.ply_tree import add_leaves, make_node

# Poetic token set.  Disjunctives and structure first, then the conjunctive
# servi.  The three revias are distinct tokens (distinct grammatical roles) even
# though they share one sign; likewise DEHI vs TARHA and SINNOR share signs with
# prose accents -- disambiguation is the scanner's job (see module docstring).
tokens = (
    # structure
    "TILDE",
    "SOFPASUQ",
    # disjunctives (greatest -> least)
    "SILLUQ",
    "OLEH_WEYORED",
    "ATNACH",
    "REVIA_GADOL",
    "REVIA_MUGRASH",
    "REVIA_QATAN",
    "DEHI",
    "SINNOR",
    "PAZER",
    "LEGARMEH",
    "SHALSHELET_GEDOLAH",
    # conjunctive servi (ITM #358; ATNAH_HAFUKH per #363)
    "MUNACH",
    "MEREKA",
    "MAHPAK",
    "AZLA",
    "GALGAL",
    "ILLUY",
    "TARHA",
    "ATNAH_HAFUKH",
    # NOTE: the conjunctive shalshelet qetannah (#371) is a real poetic servus but
    # occurs in only eight verses, each time as one link in a chain of conjunctives
    # before silluq, atnah, or revia mugrash without geresh.  Yeivin does not give
    # the exact chains, so it is left unmodeled (no token) rather than fabricated;
    # see the shalshelet gedolah section below.
)

start = "pasuq"


# --- pasuq ---------------------------------------------------------------------
def p_pasuq(p):
    "pasuq : TILDE silluq_clause SOFPASUQ"
    p[0] = p[2]


# --- silluq (#359) -------------------------------------------------------------
# Up to four servi.  A single servus is usually munah (Ps 1:1) or merka (Ps 1:2);
# two servi are usually tarha + munah (Ps 1:6).  Three and four servi follow
# "intricate rules" (Yeivin) and are not enumerated here.
def p_silluq_phrase_silluq(p):
    "silluq_phrase : SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1])


def p_silluq_phrase_munach(p):
    "silluq_phrase : MUNACH SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1], p[2])


def p_silluq_phrase_mereka(p):
    "silluq_phrase : MEREKA SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1], p[2])


def p_silluq_phrase_tarha_munach(p):
    "silluq_phrase : TARHA MUNACH SILLUQ"
    p[0] = add_leaves("silluq_phrase", p[1], p[2], p[3])


# The silluq domain is the whole verse.  Its near divider before silluq is revia
# mugrash or shalshelet gedolah (#366, #371); its great divider is atnah or
# oleh-we-yored (#361).  oleh-we-yored, when present, is the topmost divider and
# may itself contain an atnah-divided remainder before silluq (#361).
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


# --- oleh-we-yored (#363) ------------------------------------------------------
# The main verse divider.  One servus or none.  The characteristic servus is the
# "v"-shaped sign (atnah hafukh); mehuppak where the word is stressed on its first
# syllable, occasionally merka.
def p_oleh_phrase_bare(p):
    "oleh_weyored_phrase : OLEH_WEYORED"
    p[0] = add_leaves("oleh_weyored_phrase", p[1])


def p_oleh_phrase_atnah_hafukh(p):
    "oleh_weyored_phrase : ATNAH_HAFUKH OLEH_WEYORED"
    p[0] = add_leaves("oleh_weyored_phrase", p[1], p[2])


def p_oleh_phrase_mahpak(p):
    "oleh_weyored_phrase : MAHPAK OLEH_WEYORED"
    p[0] = add_leaves("oleh_weyored_phrase", p[1], p[2])


def p_oleh_phrase_mereka(p):
    "oleh_weyored_phrase : MEREKA OLEH_WEYORED"
    p[0] = add_leaves("oleh_weyored_phrase", p[1], p[2])


# oleh-we-yored is "always preceded by revia [qatan] or sinnor" (#363, #371): the
# immediate predecessor is revia qatan (no servus) or sinnor (with servus).  The
# main subdivider of its domain is revia gadol, which stands before the
# revia-qatan/sinnor.
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


# --- atnah (#362) --------------------------------------------------------------
# Up to five servi.  A single servus is munah when dehi precedes, else merka; two
# servi are both munah; with paseq before atnah the servi are tarha + merka.
def p_atnach_phrase_bare(p):
    "atnach_phrase : ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1])


def p_atnach_phrase_munach(p):
    "atnach_phrase : MUNACH ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2])


def p_atnach_phrase_mereka(p):
    "atnach_phrase : MEREKA ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2])


def p_atnach_phrase_munach2(p):
    "atnach_phrase : MUNACH MUNACH ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2], p[3])


def p_atnach_phrase_tarha_mereka(p):
    "atnach_phrase : TARHA MEREKA ATNACH"
    p[0] = add_leaves("atnach_phrase", p[1], p[2], p[3])


# The atnah domain is subdivided by dehi (near) or revia gadol (distant); revia
# gadol is the higher divider, so it may contain a dehi subdivision but not vice
# versa.
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


# --- revia gadol (#363) --------------------------------------------------------
# Rarely more than one servus: merka, or mehuppak, or illuy (one of the shofar
# accents).  Mehuppak with sinnorit ("mehuppak mesunnar") -- the sinnorit is a
# secondary "helping tune" the scanner swallows, so only MAHPAK is seen here.
def p_revia_gadol_phrase_bare(p):
    "revia_gadol_phrase : REVIA_GADOL"
    p[0] = add_leaves("revia_gadol_phrase", p[1])


def p_revia_gadol_phrase_mereka(p):
    "revia_gadol_phrase : MEREKA REVIA_GADOL"
    p[0] = add_leaves("revia_gadol_phrase", p[1], p[2])


def p_revia_gadol_phrase_mahpak(p):
    "revia_gadol_phrase : MAHPAK REVIA_GADOL"
    p[0] = add_leaves("revia_gadol_phrase", p[1], p[2])


def p_revia_gadol_phrase_illuy(p):
    "revia_gadol_phrase : ILLUY REVIA_GADOL"
    p[0] = add_leaves("revia_gadol_phrase", p[1], p[2])


# A near/minor division is legarmeh; a distant/major one is pazer; both may occur
# (#363).  pazer is the higher of the two, so it may contain legarmeh.
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


# --- revia qatan (#368) --------------------------------------------------------
# Only immediately before oleh-we-yored.  Up to three servi: one merka; two are
# mehuppak + merka, or two merkas (Ps 67:5); three only in Ps 1:2.
def p_revia_qatan_phrase_bare(p):
    "revia_qatan_phrase : REVIA_QATAN"
    p[0] = add_leaves("revia_qatan_phrase", p[1])


def p_revia_qatan_phrase_mereka(p):
    "revia_qatan_phrase : MEREKA REVIA_QATAN"
    p[0] = add_leaves("revia_qatan_phrase", p[1], p[2])


def p_revia_qatan_phrase_mahpak_mereka(p):
    "revia_qatan_phrase : MAHPAK MEREKA REVIA_QATAN"
    p[0] = add_leaves("revia_qatan_phrase", p[1], p[2], p[3])


def p_revia_qatan_phrase_mereka_mereka(p):
    "revia_qatan_phrase : MEREKA MEREKA REVIA_QATAN"
    p[0] = add_leaves("revia_qatan_phrase", p[1], p[2], p[3])


# The only subordinate disjunctive is legarmeh (#368).
def p_revia_qatan_clause(p):
    """revia_qatan_clause : revia_qatan_phrase
                          | legarmeh_revia_qatan_clause"""
    p[0] = p[1]


def p_legarmeh_revia_qatan_clause(p):
    """legarmeh_revia_qatan_clause : legarmeh_clause revia_qatan_phrase
                                    | legarmeh_clause legarmeh_revia_qatan_clause"""
    p[0] = make_node("revia_qatan_clause", p[1], p[2])


# --- revia mugrash (#366-367) --------------------------------------------------
# The last disjunctive before silluq (masoretic "tifha"); functions like prose
# tifcha.  With geresh: one or two merka servi.  "Without geresh" (when no atnah
# in the verse, acting as main verse divider): up to four servi, two being
# tarha + merka.  The geresh stroke is orthographic, so both share one token.
def p_revia_mugrash_phrase_bare(p):
    "revia_mugrash_phrase : REVIA_MUGRASH"
    p[0] = add_leaves("revia_mugrash_phrase", p[1])


def p_revia_mugrash_phrase_mereka(p):
    "revia_mugrash_phrase : MEREKA REVIA_MUGRASH"
    p[0] = add_leaves("revia_mugrash_phrase", p[1], p[2])


def p_revia_mugrash_phrase_mereka2(p):
    "revia_mugrash_phrase : MEREKA MEREKA REVIA_MUGRASH"
    p[0] = add_leaves("revia_mugrash_phrase", p[1], p[2], p[3])


def p_revia_mugrash_phrase_tarha_mereka(p):
    "revia_mugrash_phrase : TARHA MEREKA REVIA_MUGRASH"
    p[0] = add_leaves("revia_mugrash_phrase", p[1], p[2], p[3])


# Lower divisions under revia mugrash are the universal lesser dividers pazer /
# legarmeh (as for revia gadol).
def p_revia_mugrash_clause(p):
    """revia_mugrash_clause : revia_mugrash_phrase
                            | legarmeh_revia_mugrash_clause
                            | pazer_revia_mugrash_clause"""
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


# --- dehi (#364) ---------------------------------------------------------------
# Subordinate to atnah; prepositive tifha-shaped stroke.  Up to three servi: one
# munah; a second servus is various, e.g. mehuppak; three only Ps 56:10/Job 34:37.
def p_dehi_phrase_bare(p):
    "dehi_phrase : DEHI"
    p[0] = add_leaves("dehi_phrase", p[1])


def p_dehi_phrase_munach(p):
    "dehi_phrase : MUNACH DEHI"
    p[0] = add_leaves("dehi_phrase", p[1], p[2])


def p_dehi_phrase_mahpak_munach(p):
    "dehi_phrase : MAHPAK MUNACH DEHI"
    p[0] = add_leaves("dehi_phrase", p[1], p[2], p[3])


# Divisions under dehi are legarmeh or pazer or both (#364).
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


# --- sinnor (#365) -------------------------------------------------------------
# Subordinate to oleh-we-yored; postpositive zarqa-shaped sign.  One or two servi:
# one is merka or munah; two are usually merka + munah, sometimes mehuppak + munah.
def p_sinnor_phrase_bare(p):
    "sinnor_phrase : SINNOR"
    p[0] = add_leaves("sinnor_phrase", p[1])


def p_sinnor_phrase_mereka(p):
    "sinnor_phrase : MEREKA SINNOR"
    p[0] = add_leaves("sinnor_phrase", p[1], p[2])


def p_sinnor_phrase_munach(p):
    "sinnor_phrase : MUNACH SINNOR"
    p[0] = add_leaves("sinnor_phrase", p[1], p[2])


def p_sinnor_phrase_mereka_munach(p):
    "sinnor_phrase : MEREKA MUNACH SINNOR"
    p[0] = add_leaves("sinnor_phrase", p[1], p[2], p[3])


def p_sinnor_phrase_mahpak_munach(p):
    "sinnor_phrase : MAHPAK MUNACH SINNOR"
    p[0] = add_leaves("sinnor_phrase", p[1], p[2], p[3])


# Divisions under sinnor are legarmeh or pazer or both (#365).
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


# --- pazer (#369) --------------------------------------------------------------
# Up to three servi.  A single servus is rare, usually merka.  Two servi (system
# of A and L): the servus immediately before pazer is galgal, the second is
# mehuppak (word stressed on first syllable) else azla.  A third servus is various.
def p_pazer_phrase_bare(p):
    "pazer_phrase : PAZER"
    p[0] = add_leaves("pazer_phrase", p[1])


def p_pazer_phrase_mereka(p):
    "pazer_phrase : MEREKA PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2])


def p_pazer_phrase_mahpak_galgal(p):
    "pazer_phrase : MAHPAK GALGAL PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3])


def p_pazer_phrase_azla_galgal(p):
    "pazer_phrase : AZLA GALGAL PAZER"
    p[0] = add_leaves("pazer_phrase", p[1], p[2], p[3])


# The only subordinate disjunctive is legarmeh (#369).
def p_pazer_clause(p):
    """pazer_clause : pazer_phrase
                    | legarmeh_pazer_clause"""
    p[0] = p[1]


def p_legarmeh_pazer_clause(p):
    """legarmeh_pazer_clause : legarmeh_clause pazer_phrase
                             | legarmeh_clause legarmeh_pazer_clause"""
    p[0] = make_node("pazer_clause", p[1], p[2])


# --- legarmeh (#370) -----------------------------------------------------------
# Conjunctive (azla or mehuppak) + paseq; azla legarmeh and mehuppak legarmeh are
# variant forms of one accent, so both are the LEGARMEH token.  One or two servi:
# the commonest single servus is mehuppak, also illuy or merka; two servi occur in
# three places only.  The lowest disjunctive: it takes no subordinate disjunctive,
# but legarmeh may itself repeat in a chain.
def p_legarmeh_phrase_bare(p):
    "legarmeh_phrase : LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1])


def p_legarmeh_phrase_mahpak(p):
    "legarmeh_phrase : MAHPAK LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2])


def p_legarmeh_phrase_illuy(p):
    "legarmeh_phrase : ILLUY LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2])


def p_legarmeh_phrase_mereka(p):
    "legarmeh_phrase : MEREKA LEGARMEH"
    p[0] = add_leaves("legarmeh_phrase", p[1], p[2])


def p_legarmeh_clause(p):
    """legarmeh_clause : legarmeh_phrase
                       | legarmeh_clause legarmeh_phrase"""
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = make_node("legarmeh_clause", p[1], p[2])


# --- shalshelet gedolah (#371) -------------------------------------------------
# A disjunctive in the second half of the verse, followed by the two servi of
# silluq (so it sits at the revia-mugrash rank before silluq).  As a rule it has
# no servi (one servus in Ps 89:2, two in rare cases), so only the bare phrase /
# clause is given.  Distinct from the conjunctive shalshelet qetannah, which never
# carries the following paseq.
def p_shalshelet_gedolah_phrase(p):
    "shalshelet_gedolah_phrase : SHALSHELET_GEDOLAH"
    p[0] = add_leaves("shalshelet_gedolah_phrase", p[1])


def p_shalshelet_gedolah_clause(p):
    "shalshelet_gedolah_clause : shalshelet_gedolah_phrase"
    p[0] = p[1]


# --- error callback ------------------------------------------------------------
def p_error(p):  # noqa: D401  (PLY callback)
    # No poetic error-recovery productions yet (see module docstring): on a syntax
    # error PLY has nothing to recover with, so the parse fails (parser.parse
    # returns None).  Kept as a no-op so PLY does not raise.
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
    reduce/reduce conflict warnings) is returned alongside the parser, for
    grammar development; otherwise warnings are silenced like the prose grammar.
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
