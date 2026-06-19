"""Canonical token-type names for the POETIC (Three Books) accent grammar.

Single source of truth for the poetic PLY *token type* strings, so the (variable,
dot-losing) ASCII transliterations are spelled exactly once instead of as bare
string literals scattered across ply_grammar_poetic, ply_scanner_poetic,
mam_poetic_accents, xcheck_poetic and their tests.  Import these and compare/use
the constants; never re-type the literal.

One unavoidable exception: PLY builds the grammar from the *docstrings* of the
``p_*`` rule functions, which it parses textually -- the terminal names there must
be written literally and cannot be constants.  The ``tokens`` tuple is built from
these constants, and the grammar's parse / zero-conflict tests fail loudly if a
docstring terminal ever drifts from a constant, so the literal docstrings stay
pinned to this file.

Transliteration choices (avoid proliferating spellings; follow existing precedent):
Spellings follow the canonical display names in ``py/mb_diff_mpu/describe_diff.py``
(ACCENT_NAMES / POETIC_ACCENTS), uppercased with its ``ḥ`` written **X** for ASCII:
  - deḥi -> DEXI, munaḥ -> MUNAX (ḥ -> X; cf. mb_cmn ``DEX``).
  - tsinnor -> TSINNOR (describe_diff "tsinnor", doubled n).
  - merkha -> MERKHA, mahapakh -> MAHAPAKH (cf. Unicode names; the kaf-dropping
    Goerwitz "MEREKA"/"MAHPAK" lose to the full forms).
  - names describe_diff spells plainly keep the plain Goerwitz form (ply_grammar.py):
    SILLUQ, PAZER, LEGARMEH, AZLA, GALGAL, REVIA, SHALSHELET.

Maintainer overrides of describe_diff:
  - ATNAX, not ETNAXTA (describe_diff calls the accent "etnaḥta").
  - TARXA, not TARHA: describe_diff's plain "tarha" is a bug; the ḥet takes X.
  - ILLUY, not ILUY: doubled L preferred.
  - OLEH_WEYORED keeps "we-" (no "veyored" precedent in the tree).

NOTE: the prose grammar (a port of the Goerwitz C oracle acc2tre.y) now adopts the
shared spellings ATNAX / MUNAX / MERKHA / MAHAPAKH, so there is one transliteration
per use case across prose and poetic; see issue #13.  (Byte-for-byte parity with the
Goerwitz C output is no longer a goal.)  TARXA stays poetic-only: the tifcha-shaped
sign is a *distinct accent* in each system -- prose tipeḥa (TIPEXA, with mayela as
its variant) vs poetic tarḥa (TARXA) -- that merely shares one Unicode code point, so
the two keep separate names.
"""

from __future__ import annotations

# --- structural bookends -------------------------------------------------------
TILDE = "TILDE"
SOFPASUQ = "SOFPASUQ"

# --- disjunctives (greatest -> least) ------------------------------------------
SILLUQ = "SILLUQ"
ATNAX = "ATNAX"  # etnahta
OLEH_WEYORED = "OLEH_WEYORED"
REVIA_GADOL = "REVIA_GADOL"
REVIA_MUGRASH = "REVIA_MUGRASH"
REVIA_QATAN = "REVIA_QATAN"
DEXI = "DEXI"  # deḥi
TSINNOR = "TSINNOR"  # tsinnor (Unicode "zinor")
PAZER = "PAZER"
LEGARMEH = "LEGARMEH"
SHALSHELET_GEDOLAH = "SHALSHELET_GEDOLAH"

# Generic revia (M-C 81, no geresh muqdam): a scanner-internal token reclassified
# to REVIA_GADOL / REVIA_QATAN / REVIA_MUGRASH by position; never reaches the
# grammar.  Likewise SHALSHELET is the scanner/MAM-internal provisional that
# becomes SHALSHELET_GEDOLAH (with paseq) or is swallowed (bare = qetannah).
REVIA = "REVIA"
SHALSHELET = "SHALSHELET"

# --- conjunctive servi ---------------------------------------------------------
MUNAX = "MUNAX"  # munaḥ
MERKHA = "MERKHA"
MAHAPAKH = "MAHAPAKH"
AZLA = "AZLA"
GALGAL = "GALGAL"
ILLUY = "ILLUY"  # doubled L preferred over describe_diff's "iluy"
TARXA = "TARXA"  # tarḥa (poetic name for the tipeḥa-shaped sign; describe_diff's
# plain "tarha" is a bug per the maintainer -- the ḥet takes X like MUNAX/DEXI)

# The disjunctive token types, for the revia gadol/qatan/mugrash lookahead and the
# WLC-vs-MAM cross-check.
POETIC_DISJUNCTIVES = frozenset(
    {
        SILLUQ,
        ATNAX,
        OLEH_WEYORED,
        REVIA,
        REVIA_MUGRASH,
        REVIA_GADOL,
        REVIA_QATAN,
        DEXI,
        TSINNOR,
        PAZER,
        LEGARMEH,
        SHALSHELET_GEDOLAH,
    }
)
