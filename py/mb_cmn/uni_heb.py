"""Hebrew Unicode utilities."""

import re
import unicodedata
from mb_cmn import hebrew_letters as hl
from mb_cmn import hebrew_points as hpo
from mb_cmn import hebrew_punctuation as hpu
from mb_cmn import hebrew_accents as ha
from mb_cmn import str_defs as sd

__all__ = [
    "shunna",
    "accent_names",
    "rm_mtgoslq",
    "he_char_name",
    "join_shunnas",
    "t_shunnas",
    "he_to_ascii_direct",
    "he_ascii_slug",
    "he_ascii_identifier",
]


def shunna(string):
    """
    Return the short name for the Unicode code point in the given (length-1) string,
    if we "know" a short name for it.
    Otherwise give the standard Unicode name.
    """
    if nonhe := _HE_TO_NONHE_DIC.get(string):
        return nonhe
    fullname = unicodedata.name(string)
    fullname_words = fullname.split()
    if len(fullname_words) < 3:
        return fullname
    sfpp = _shorten_fullname_prefix(fullname_words[0], fullname_words[1])
    return sfpp + " " + " ".join(fullname_words[2:])


def legacy_name(string_len_1):
    """Return the legacy human-readable Unicode name for a code point."""
    return _LEGACY_NAME_SHORTS.get(string_len_1) or unicodedata.name(string_len_1)


def accent_names(string):
    """
    Return accent names including "mos" (MTGOSLQ), which might not be an accent,
    since "mos" could be either meteg or silluq.
    """
    return list(filter(None, (_HE_TO_NONHE_ACC_DIC.get(c) for c in string)))


def rm_mtgoslq(string):
    """Remove MTGOSLQ from the given string."""
    return string.replace(hpo.MTGOSLQ, "")


def he_char_name(unicode_str_of_len_1):
    """Return Hebrew character name."""
    return _HE_TO_NONHE_DIC[unicode_str_of_len_1]


def join_shunnas(string, sep=","):
    """
    Join the short unicode names of the chars of a string.
    Join with the given separator, or comma by default.
    """
    return sep.join(t_shunnas(string))


def t_shunnas(string: str):
    """Tuple of short unicode names"""
    assert isinstance(string, str)
    return tuple(map(shunna, string))


def he_to_ascii_direct(string: str):
    """Map Hebrew letters to direct ASCII code (ABGDH VZXEY KLMNO 3PCQR JF)."""
    assert isinstance(string, str)
    return "".join(_HE_TO_DIRECT_ASCII_LETT_DIC.get(ch, ch) for ch in string)


def he_ascii_slug(string: str, digit_prefix=""):
    """Return a lowercase ASCII slug using the direct Hebrew-letter mapping."""
    mapped = he_to_ascii_direct(string).lower().translate(_DROP_HEBREW_ABBREV_MARKS)
    slug = _NON_ALNUM_RE.sub("-", mapped).strip("-")
    if not slug:
        return digit_prefix
    if slug[0].isdigit() and digit_prefix:
        return f"{digit_prefix}-{slug}"
    return slug


def he_ascii_identifier(string: str, digit_prefix="h_"):
    """Return a lowercase ASCII identifier using the direct Hebrew-letter mapping."""
    mapped = he_to_ascii_direct(string).lower().translate(_DROP_HEBREW_ABBREV_MARKS)
    ident = _NON_IDENT_RE.sub("_", mapped).strip("_")
    if not ident:
        return digit_prefix.rstrip("_")
    if ident[0].isdigit():
        return digit_prefix + ident
    return ident


def _mk_he_to_nonhe_dic():
    nonhe_set = set()
    for _he, nonhe in _HE_AND_NONHE_PAIRS:
        assert nonhe not in nonhe_set
        nonhe_set.add(nonhe)
    return dict(_HE_AND_NONHE_PAIRS)


def _shorten_fullname_prefix(word1, word2):
    return _SHORTEN_DIC.get((word1, word2)) or word1 + " " + word2


_SHORTEN_DIC = {
    ("HEBREW", "LETTER"): "HLE",
    ("HEBREW", "POINT"): "HPO",
    ("HEBREW", "ACCENT"): "HAC",
    ("HEBREW", "PUNCTUATION"): "HPU",
    ("HEBREW", "MARK"): "HMA",
}

_LEGACY_NAME_SHORTS = {
    "\N{SPACE}": "space",
    "\N{COMBINING GRAPHEME JOINER}": "combining-grapheme-joiner",
    "\N{ZERO WIDTH JOINER}": "zero-width-joiner",
    ha.ATN: "etnaḥta",
    "\N{HEBREW ACCENT SEGOL}": "segol-accent",
    "\N{HEBREW ACCENT SHALSHELET}": "shalshelet",
    "\N{HEBREW ACCENT ZAQEF QATAN}": "zaqef-qatan",
    "\N{HEBREW ACCENT ZAQEF GADOL}": "zaqef-gadol",
    ha.TIP: "tipeḥa/tarḥa",
    ha.REV: "revia",
    "\N{HEBREW ACCENT ZARQA}": "zarqa-stress-helper/tsinorit",
    "\N{HEBREW ACCENT PASHTA}": "pashta",
    "\N{HEBREW ACCENT YETIV}": "yetiv",
    "\N{HEBREW ACCENT TEVIR}": "tevir",
    ha.GER: "geresh",
    ha.GER_M: "geresh-muqdam",
    ha.GER_2: "gershayim",
    "\N{HEBREW ACCENT QARNEY PARA}": "qarney-para",
    ha.TEL_G: "telisha-gedola",
    "\N{HEBREW ACCENT PAZER}": "pazer",
    ha.ATN_H: "atnaḥ-hafukh",
    ha.MUN: "munaḥ",
    "\N{HEBREW ACCENT MAHAPAKH}": "mahapakh",
    ha.MER: "merkha/yored",
    "\N{HEBREW ACCENT MERKHA KEFULA}": "merkha-kefula",
    "\N{HEBREW ACCENT DARGA}": "darga",
    "\N{HEBREW ACCENT QADMA}": "qadma",
    "\N{HEBREW ACCENT TELISHA QETANA}": "telisha-qetana",
    ha.YBY: "yeraḥ-ben-yomo",
    ha.OLE: "ole",
    "\N{HEBREW ACCENT ILUY}": "iluy",
    "\N{HEBREW ACCENT DEHI}": "deḥi",
    "\N{HEBREW ACCENT ZINOR}": "tsinor",
    hpo.SHEVA: "sheva",
    hpo.XSEGOL: "ḥataf-segol",
    hpo.XPATAX: "ḥataf-pataḥ",
    hpo.XQAMATS: "ḥataf-qamats",
    hpo.XIRIQ: "ḥiriq",
    hpo.TSERE: "tsere",
    hpo.SEGOL_V: "segol-vowel",
    hpo.PATAX: "pataḥ",
    hpo.QAMATS: "qamats",
    hpo.XOLAM: "ḥolam",
    hpo.XOLAM_XFV: "ḥolam-ḥaser-for-vav",
    hpo.QUBUTS: "qubuts",
    hpo.DAGOMOSD: "dagesh/mapiq/shuruq-dot",
    hpo.MTGOSLQ: "meteg/siluq",
    "\N{HEBREW PUNCTUATION MAQAF}": "maqaf",
    hpo.RAFE: "rafeh",
    "\N{HEBREW PUNCTUATION PASEQ}": "paseq/legarmeih",
    hpo.SHIND: "shin-dot",
    hpo.SIND: "sin-dot",
    "\N{HEBREW PUNCTUATION SOF PASUQ}": "sof-pasuq",
    "\N{HEBREW MARK UPPER DOT}": "upper-dot",
    "\N{HEBREW MARK LOWER DOT}": "lower-dot",
    "\N{HEBREW PUNCTUATION NUN HAFUKHA}": "nun-hafukha",
    hpo.QAMATS_Q: "qamats-qatan",
    hl.ALEF: "alef",
    hl.BET: "bet",
    hl.GIMEL: "gimel",
    hl.DALET: "dalet",
    hl.HE: "he",
    hl.VAV: "vav",
    hl.ZAYIN: "zayin",
    hl.XET: "ḥet",
    hl.TET: "tet",
    hl.YOD: "yod",
    hl.FKAF: "final-kaf",
    hl.KAF: "kaf",
    hl.LAMED: "lamed",
    hl.FMEM: "final-mem",
    hl.MEM: "mem",
    hl.FNUN: "final-nun",
    hl.NUN: "nun",
    hl.SAMEKH: "samekh",
    hl.AYIN: "ayin",
    hl.FPE: "final-pe",
    hl.PE: "pe",
    hl.FTSADI: "final-tsadi",
    hl.TSADI: "tsadi",
    hl.QOF: "qof",
    hl.RESH: "resh",
    hl.SHIN: "shin",
    hl.TAV: "tav",
    hpo.VARIKA: "varika",
}

_HE_AND_NONHE_LETT_PAIRS = (
    (hl.ALEF, "α"),  # Greek alpha
    (hl.BET, "b"),
    (hl.GIMEL, "g"),
    (hl.DALET, "d"),
    (hl.HE, "h"),
    (hl.VAV, "v"),
    (hl.ZAYIN, "z"),
    (hl.XET, "x"),
    (hl.TET, "θ"),  # See note on θ (theta)
    (hl.YOD, "y"),
    (hl.FKAF, "k."),
    (hl.KAF, "k"),
    (hl.LAMED, "l"),
    (hl.FMEM, "m."),
    (hl.MEM, "m"),
    (hl.FNUN, "n."),
    (hl.NUN, "n"),
    (hl.SAMEKH, "σ"),  # Greek sigma
    (hl.AYIN, "3"),  # as in Arabizi
    (hl.FPE, "p."),
    (hl.PE, "p"),
    (hl.FTSADI, "c."),  # as in "C" in Michigan-Claremont
    (hl.TSADI, "c"),
    (hl.QOF, "q"),
    (hl.RESH, "r"),
    (hl.SHIN, "$"),  # as in Michigan-Claremont
    (hl.TAV, "τ"),  # Greek tau
)
_HE_AND_DIRECT_ASCII_LETT_PAIRS = (
    # Derived from author.py comment:
    # אבגדה וזחטי כלמנס עפצקר שת
    # ABGDH VZXEY KLMNO 3PCQR JF
    (hl.ALEF, "a"),
    (hl.BET, "b"),
    (hl.GIMEL, "g"),
    (hl.DALET, "d"),
    (hl.HE, "h"),
    (hl.VAV, "v"),
    (hl.ZAYIN, "z"),
    (hl.XET, "x"),
    (hl.TET, "e"),  # tet/tav is e/f
    (hl.YOD, "y"),
    (hl.FKAF, "k"),
    (hl.KAF, "k"),
    (hl.LAMED, "l"),
    (hl.FMEM, "m"),
    (hl.MEM, "m"),
    (hl.FNUN, "n"),
    (hl.NUN, "n"),
    (hl.SAMEKH, "o"),  # samekh/shin is o/j
    (hl.AYIN, "3"),  # as in Arabizi
    (hl.FPE, "p"),
    (hl.PE, "p"),
    (hl.FTSADI, "c"),
    (hl.TSADI, "c"),  # Michigan-Claremont
    (hl.QOF, "q"),
    (hl.RESH, "r"),
    (hl.SHIN, "j"),  # samekh/shin is o/j
    (hl.TAV, "f"),  # tet/tav is e/f
)
_HE_AND_NONHE_POINT_PAIRS = (
    (hpo.VARIKA, "varika"),
    (hpo.DAGOMOSD, "·"),
    (hpo.RAFE, "‾"),  # r̄ was another candidate
    (hpo.SHIND, "·sh"),
    (hpo.SIND, "·si"),
    (hpo.SHEVA, ":"),  # ambiguous, could be na or nax
    (hpo.XSEGOL, ":∵"),  # ∵ aka BECAUSE
    (hpo.XPATAX, ":_"),
    (hpo.XQAMATS, ":a"),
    (hpo.XIRIQ, "i"),
    (hpo.TSERE, "‥"),
    (hpo.SEGOL_V, "∵"),  # ∵ aka BECAUSE
    (hpo.PATAX, "_"),
    (hpo.QAMATS, "a"),  # ambiguous, could be gadol or qatan
    (hpo.QAMATS_Q, "oa"),
    (hpo.XOLAM_XFV, "xxfv"),
    (hpo.XOLAM, "o"),
    (hpo.QUBUTS, "u"),
)
_HE_AND_NONHE_ACC_PAIRS = (
    # These first three are the only ones not of the form (ha.X, "(x)")
    (ha.Z_OR_TSOR, "(zarnor)"),
    # Above is zarqa or tsinnor; see: Note on zinor
    (ha.ZSH_OR_TSIT, "(zarshit)"),
    # Above is zarqa stress helper or tsinnorit; see: Note on zinor
    (hpo.MTGOSLQ, "(mos)"),
    # Above is meteg or silluq; here we consider it an accent not a point
    # The ones below are all of the form (ha.X, "(x)")
    (ha.ATN, "(atn)"),
    (ha.SEG_A, "(seg_a)"),
    (ha.SHA, "(sha)"),
    (ha.ZAQ_Q, "(zaq_q)"),
    (ha.ZAQ_G, "(zaq_g)"),
    (ha.TIP, "(tip)"),
    (ha.REV, "(rev)"),
    (ha.PASH, "(pash)"),
    (ha.YET, "(yet)"),
    (ha.TEV, "(tev)"),
    (ha.GER, "(ger)"),
    (ha.GER_M, "(ger_m)"),
    (ha.GER_2, "(ger_2)"),
    (ha.QAR, "(qar)"),
    (ha.TEL_G, "(tel_g)"),
    (ha.PAZ, "(paz)"),
    (ha.ATN_H, "(atn_h)"),
    (ha.MUN, "(mun)"),
    (ha.MAH, "(mah)"),
    (ha.MER, "(mer)"),
    (ha.MER_2, "(mer_2)"),
    (ha.DAR, "(dar)"),
    (ha.QOM, "(qom)"),  # qadma or metigah
    (ha.TEL_Q, "(tel_q)"),
    (ha.YBY, "(yby)"),
    (ha.OLE, "(ole)"),
    (ha.ILU, "(ilu)"),
    (ha.DEX, "(dex)"),
)
_HE_AND_NONHE_PUNC_PAIRS = (
    (hpu.MAQ, "-"),
    (hpu.PASOLEG, "|"),
    (hpu.SOPA, "(sopa)"),  # sof pasuq
    (hpu.MCIRC, "ḿ"),  # U+1E3F: LATIN SMALL LETTER M WITH ACUTE
)
_MISC_UNI_NAME_SHORTENINGS = ((sd.CGJ, "CGJ"),)
_HE_AND_NONHE_PAIRS = (
    _MISC_UNI_NAME_SHORTENINGS
    + _HE_AND_NONHE_LETT_PAIRS
    + _HE_AND_NONHE_POINT_PAIRS
    + _HE_AND_NONHE_PUNC_PAIRS
    + _HE_AND_NONHE_ACC_PAIRS
)
_HE_TO_NONHE_DIC = _mk_he_to_nonhe_dic()
_HE_TO_NONHE_ACC_DIC = dict(_HE_AND_NONHE_ACC_PAIRS)
_HE_TO_DIRECT_ASCII_LETT_DIC = dict(_HE_AND_DIRECT_ASCII_LETT_PAIRS)
_NON_ALNUM_RE = re.compile(r"[^0-9a-z]+")
_NON_IDENT_RE = re.compile(r"[^0-9a-z_]+")
_DROP_HEBREW_ABBREV_MARKS = str.maketrans("", "", "׳״")

#######################################
# Note on θ (theta)
#
# Is θ (theta) a bad choice for tet since θ is IPA for tav?
# Relatedly, there is a (mostly historic) transliteration of tav
# as "th". A notable example is the English word "Sabbath"!
# We chose theta for tet because its name reminded us of tet.
# Similarly we chose tau for tav because of its name reminded us of tav.
#######################################
# Note on zinor
#
# Really the accent called ZINOR in Unicode
# should be called TSINOR or TSINOR/ZARQA.
# So its name is not great, but not terrible.
#
# More messed up is this related situation:
# Really the accent called ZARQA in Unicode
# should be called TSINORIT or TSINORIT/ZARQA STRESS HELPER.
