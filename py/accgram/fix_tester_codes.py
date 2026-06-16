"""Accent-name <-> Michigan-Claremont (M-C) code bridge for the fix-tester.

The PLY scanner/grammar consume M-C 2-digit accent *codes* (74 = munaH,
71 = mereka, 92 = atnaH, ...).  A proposed "fix" is the MAM-simple *Unicode*
value, and ``mb_cmn.uni_heb.accent_names`` reduces a Unicode word to the ordered
list of accent abbreviations it carries (``(mun)``, ``(mer)``, ``(tip)``, ...).
To re-test a fix we must splice the changed accent's M-C code into the M-C body,
so this module maps those abbreviations to canonical M-C codes.

Only accents whose M-C code is a single, *context-free* 2-digit literal are
mappable; context-dependent ones (silluq/mayela/legarmeh -- decided by trailing
context or the has_legarmeh passage list) and the ``(mos)`` meteg/silluq
pseudo-accent are deliberately refused so the fix-tester marks those cases
UNTESTABLE rather than guessing.

``assert_in_sync_with_gg_rules`` guards two invariants so the table cannot drift
silently from the scanner: every abbreviation in ``uni_heb`` is classified
(mappable or untestable), and every mappable code still scans to the token type
this module claims for it.
"""

from __future__ import annotations

from accgram.ply_scanner import HasLegarmeh, scan_accents
from mb_cmn import uni_heb

# Accent abbreviation (as returned by uni_heb.accent_names, parens included) ->
# the canonical M-C 2-digit code that scans to a single accent token of the
# matching type.  See SAFE_ABBREV_TO_TYPE for the expected token type.
SAFE_ABBREV_TO_CODE: dict[str, str] = {
    "(atn)": "92",
    "(zaq_q)": "80",
    "(zaq_g)": "85",
    "(rev)": "81",
    "(tip)": "73",
    "(yet)": "10",
    "(tev)": "91",
    "(ger)": "61",
    "(ger_2)": "62",
    "(paz)": "83",
    "(qar)": "84",
    "(tel_g)": "14",
    "(mun)": "74",
    "(mah)": "70",
    "(mer)": "71",
    "(mer_2)": "72",
    "(dar)": "94",
    "(qom)": "63",
    "(tel_q)": "04",
    "(yby)": "93",
    "(zarnor)": "02",
    "(pash)": "03",
    "(seg_a)": "01",
}

# The scanner token type each mappable code must produce (the sync check probes
# the scanner and asserts this).
SAFE_ABBREV_TO_TYPE: dict[str, str] = {
    "(atn)": "ATNACH",
    "(zaq_q)": "ZAQEF",
    "(zaq_g)": "ZAQEFGADOL",
    "(rev)": "REVIA",
    "(tip)": "TIFCHA",
    "(yet)": "YETIV",
    "(tev)": "TEVIR",
    "(ger)": "GERESH",
    "(ger_2)": "GERSHAYIM",
    "(paz)": "PAZER",
    "(qar)": "PAZERGADOL",
    "(tel_g)": "TELISHAGEDOLA",
    "(mun)": "MUNACH",
    "(mah)": "MAHPAK",
    "(mer)": "MEREKA",
    "(mer_2)": "MEREKAKEFULA",
    "(dar)": "DARGA",
    "(qom)": "AZLA",
    "(tel_q)": "TELISHAQETANNA",
    "(yby)": "GALGAL",
    "(zarnor)": "ZARQA",
    "(pash)": "PASHTA",
    "(seg_a)": "SEGOLTA",
}

# Accents we refuse to map.  ``(mos)`` is meteg-or-silluq (a vowel-tier mark, not
# a real accent change); the rest are either context-dependent in prose
# (shalshelet's split 65...05) or poetic-only signs that never appear in the
# prose corpus the fix-tester covers.
UNTESTABLE_ABBREVS: frozenset[str] = frozenset(
    {
        "(mos)",  # meteg or silluq -- vowel tier, stripped before diffing
        "(zarshit)",  # zarqa stress-helper / tsinnorit -- lexical pair, code 82
        "(sha)",  # shalshelet -- split 65...05 in prose, fiddly to splice
        "(atn_h)",  # atnaH hafukh -- poetic only
        "(ole)",  # ole -- poetic only
        "(ilu)",  # iluy -- poetic only
        "(dex)",  # dehi -- poetic only
        "(ger_m)",  # geresh muqdam -- poetic only (revia mugrash)
    }
)

# ``(mos)`` is meteg/silluq noise that the fix-tester strips from both sides of an
# accent diff (a meteg difference is not a cantillation-accent fix).
MOS_ABBREV = "(mos)"


def accent_code(abbrev: str) -> str | None:
    """Return the canonical M-C code for a mappable accent abbreviation, else None."""
    return SAFE_ABBREV_TO_CODE.get(abbrev)


def assert_in_sync_with_gg_rules() -> None:
    """Fail fast if the curated table drifts from uni_heb / the scanner.

    1. Every accent abbreviation uni_heb knows is classified exactly once as
       mappable or untestable (so a new accent forces a deliberate choice here).
    2. Every mappable code still scans, in a context-free probe, to the token
       type this module claims -- catching any change to ply_scanner._GG_RULES.
    """
    all_abbrevs = {abbrev for _char, abbrev in uni_heb._HE_AND_NONHE_ACC_PAIRS}
    classified = set(SAFE_ABBREV_TO_CODE) | set(UNTESTABLE_ABBREVS)
    if classified != all_abbrevs:
        missing = all_abbrevs - classified
        extra = classified - all_abbrevs
        raise AssertionError(
            "fix_tester_codes is out of sync with uni_heb accent abbreviations: "
            f"unclassified={sorted(missing)} unknown={sorted(extra)}"
        )
    if set(SAFE_ABBREV_TO_CODE) & set(UNTESTABLE_ABBREVS):
        raise AssertionError(
            "fix_tester_codes: abbreviations both mappable and untestable: "
            f"{sorted(set(SAFE_ABBREV_TO_CODE) & set(UNTESTABLE_ABBREVS))}"
        )
    if set(SAFE_ABBREV_TO_CODE) != set(SAFE_ABBREV_TO_TYPE):
        raise AssertionError(
            "fix_tester_codes: SAFE_ABBREV_TO_CODE and SAFE_ABBREV_TO_TYPE keys differ"
        )

    for abbrev, code in SAFE_ABBREV_TO_CODE.items():
        expected = SAFE_ABBREV_TO_TYPE[abbrev]
        # A context-free probe: a swallowed letter, the code, then a geresh (61)
        # and sof pasuq (00).  The 61 supplies an excluded digit right after the
        # code so the mayela trailing-context (tipeHa before 00/92) cannot fire,
        # pinning 73 to TIFCHA; no 05 is present, so 74 stays MUNACH.
        probe = f"Z{code}Z61Z00"
        types = {tok.type for tok in scan_accents(probe, "zz", 1, 1, HasLegarmeh())}
        if expected not in types:
            raise AssertionError(
                f"fix_tester_codes: code {code} for {abbrev} no longer scans to "
                f"{expected} (got {sorted(types)}); ply_scanner._GG_RULES changed?"
            )
