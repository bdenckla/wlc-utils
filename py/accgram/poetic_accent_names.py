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
# becomes SHALSHELET_GEDOLAH (with paseq) or SHALSHELET_QETANNAH (bare conjunctive).
REVIA = "REVIA"
SHALSHELET = "SHALSHELET"

# A *stray* accent (any U+0591..U+05AE the poetic rules cannot consume): the scanner
# emits this in place of silently swallowing it, and the grammar has no terminal for
# it, so any verse carrying one becomes a NO_PARSE with the stray accent as its stall
# locus.  Zero live customers today -- the lone attested catch-all accent (the ps124:4
# geresh) is consumed by the same-letter revia-mugrash charity -- so this is a
# future-proofing guard, the poetic side of "nothing vanishes silently".
STRAY_ACCENT = "STRAY_ACCENT"

# --- conjunctive servi ---------------------------------------------------------
MUNAX = "MUNAX"  # munaḥ
MERKHA = "MERKHA"
MAHAPAKH = "MAHAPAKH"
AZLA = "AZLA"
GALGAL = "GALGAL"
ILLUY = "ILLUY"  # doubled L preferred over describe_diff's "iluy"
TARXA = "TARXA"  # tarḥa (poetic name for the tipeḥa-shaped sign; describe_diff's
# plain "tarha" is a bug per the maintainer -- the ḥet takes X like MUNAX/DEXI)

# --- fused tsinnorit servi and the conjunctive shalshelet ----------------------
# A mahapakh / merkha carrying a tsinnorit (U+0598) secondary on the open syllable
# before the stress: Yeivin §372's "mehuppak mesunnar", Breuer Ch. 9 §22's "mahpakh
# metzunar" / "merkha metzunar".  The scanner fuses the tsinnorit onto its mahapakh /
# merkha partner (in the same chanted word) into one of these tokens instead of
# dropping it.  Functionally still the conjunctive (the tsinnorit is only a secondary),
# so each joins the permissive `conj` servus chain -- no disjunctive-skeleton change.
# Spelling "metsunnar" = "me" + the vowel-permuted repo-standard "tsinnor".
MAHAPAKH_METSUNNAR = "MAHAPAKH_METSUNNAR"
MERKHA_METSUNNAR = "MERKHA_METSUNNAR"

# The conjunctive shalshelet qetannah (#371): bare shalshelet (U+0593, no following
# paseq), distinct from the disjunctive shalshelet gedolah (shalshelet + paseq).  A
# real poetic servus in eight verses; emitted (not swallowed) and absorbed by `conj`.
SHALSHELET_QETANNAH = "SHALSHELET_QETANNAH"

# A same-letter pair: merkha (U+05A5) + qadma/azla (U+05A8) on one base letter (ps56:10,
# the lone poetic case).  Emitting them as an ordered MERKHA AZLA *sequence* presents an
# arbitrary order as if it were meaningful (the leaf even flipped azla<->merkha across
# code versions), so the scanner fuses them into one order-less `!` bang token (Plan D),
# the poetic sibling of prose ek20:31's `mahapakh!azla` (memory
# `fused-impositive-cluster-token`).  The leaf `merkha!azla` follows the prose bang
# convention (the lower-codepoint mark first; storage order U+05A5<U+05A8 matches it).
#
# Unlike the metsunnar / shalshelet-qetannah servi, this is *not* a grammar token: two
# impositive accents sharing one letter is a lexical anomaly, so the bang has no `conj`
# terminal and the verse dead-ends to NO_PARSE (the poetic lexical-error surface),
# surfacing ps56:10 as a flagged oddball.  Manuscript rationale: MAM carries azla alone
# and, according to Breuer, so does the Aleppo Codex, while Sassoon 1053 carries merkha
# alone -- L's double-marking looks like a conflation of the two single-accent traditions
# (see poetic_ob_notes["ps 56:10"]).
#
# MERKHA_AZLA is the canonical instance of the GENERAL impositive-pair guard
# (ply_scanner_poetic): the scanner emits a bang for ANY two adjacent impositive accents,
# deriving the type/leaf per pair (_impositive_pair_token) -- merkha+qadma yields exactly
# this "MERKHA_AZLA" / "merkha!azla".  Kept as a named constant because it is the only
# attested case and is referenced by tests and servi_xcheck; other pairs get their own
# dynamic "A_B" type (none occur in the corpus).
MERKHA_AZLA = "MERKHA_AZLA"

# Scanner-internal sentinel: the impositive-pair rule emits this, and scan_accents
# replaces it with the per-pair dynamic (type, leaf) from _impositive_pair_token.  Never
# reaches the grammar (the dynamic type does, and is rejected -> NO_PARSE).
IMPOSITIVE_PAIR = "IMPOSITIVE_PAIR"

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
