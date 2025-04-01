import re
import py.hebrew_points as hpo
import py.hebrew_accents as ha
import py.hebrew_punctuation as hpu
import py.str_defs as sd


def tword(mcword: str):
    stage = mcword.replace(":A", "a").replace(":F", "f").replace(":E", "e")
    stage = re.sub(_XOLAM_PATT1, xolam_replacement1, stage)
    stage = re.sub(_XOLAM_PATT2, xolam_replacement2, stage)
    stage = re.sub(_XOLAM_PATT3, xolam_replacement3, stage)
    stage = re.sub(_EARLY_MTG_PATT, early_mtg_replacement, stage)
    stage = re.sub(_PREPOS_PATT, prepos_replacement, stage)
    stage = re.sub(_FINAL_PATT, final_replacement, stage)
    stage = stage.replace("8111", "1181")
    return stage


def uword(mcword: str):
    return uword_x(_TRANSLATION_TABLE, mcword)


def uword_retaining_slash(mcword: str):
    return uword_x(_TRANSLATION_TABLE_RETAINING_SLASH, mcword)


def uword_x(ttab, mcword: str):
    if mcword in _PASS_THRUS:
        return mcword
    stage = tword(mcword)
    stage = stage.translate(ttab)
    return re.sub(r"\d\d", digits_replacement, stage)


def _sqbrac(guts):
    return f"[{guts}]"


def _sqbrac_not(guts):
    return _sqbrac(f"^{guts}")


def _paren(guts):
    return f"({guts})"


_LETT_GUTS = ")BGDHWZX+YKLMNS(PCQR#&$T"
_LETT_GUTS_NO_VAV = _LETT_GUTS.replace("W", "")
_LETT = _sqbrac(_LETT_GUTS)
_NON_LETT = _sqbrac_not(_LETT_GUTS)
_NON_LETT_STAR = _NON_LETT + "*"
_NON_LETT_STAR_DOLL = _NON_LETT_STAR + "$"

_PREPOS_PATT = "^(10|11|12|13|14)" + _paren(_LETT + _NON_LETT_STAR)


def prepos_replacement(matchobj):
    groups = matchobj.groups()
    return groups[1] + groups[0]


_EARLY_MTG_PATT = '([AFE"I:U])95'


def early_mtg_replacement(matchobj):
    groups = matchobj.groups()
    return "95" + groups[0]


_XOLAM_PATT1 = (
    "O" + _paren(_NON_LETT_STAR) + _paren(_sqbrac(_LETT_GUTS_NO_VAV) + '|W[AFE"I:U]')
)


def xolam_replacement1(matchobj):
    groups = matchobj.groups()
    return "o" + groups[0] + groups[1]


_XOLAM_PATT2 = "O" + _paren(_NON_LETT_STAR) + "W"


def xolam_replacement2(matchobj):
    groups = matchobj.groups()
    return groups[0] + "WO"


_XOLAM_PATT3 = "W" + _paren(_NON_LETT_STAR) + "o"


def xolam_replacement3(matchobj):
    groups = matchobj.groups()
    return "W" + groups[0] + "ḥ"


_FINAL_PATT = r"[KMNPC]" + _NON_LETT_STAR_DOLL


def final_replacement(matchobj):
    nonfinal = matchobj.group()
    return nonfinal.translate(_TRANSLATION_TABLE_FOR_FINAL_FORMS)


def digits_replacement(matchobj):
    digit_pair = matchobj.group()
    return _ACCENTS[digit_pair]


_TRANSLATION_TABLE_FOR_FINAL_FORMS = str.maketrans(
    {
        "K": "k",
        "M": "m",
        "N": "n",
        "P": "p",
        "C": "c",
    }
)
_TRANSLATION_DIC_RETAINING_SLASH = {
    ")": "א",
    "B": "ב",
    "G": "ג",
    "D": "ד",
    "H": "ה",
    "W": "ו",
    "Z": "ז",
    "X": "ח",
    "+": "ט",
    "Y": "י",
    "K": "כ",
    "k": "ך",
    "L": "ל",
    "M": "מ",
    "m": "ם",
    "N": "נ",
    "n": "ן",
    "S": "ס",
    "(": "ע",
    "P": "פ",
    "p": "ף",
    "C": "צ",
    "c": "ץ",
    "Q": "ק",
    "R": "ר",
    "#": "ש",
    "&": "ש" + hpo.SIND,
    "$": "ש" + hpo.SHIND,
    "T": "ת",
    "A": hpo.PATAX,
    "a": hpo.XPATAX,  # a was :A
    "F": hpo.QAMATS,
    "f": hpo.XQAMATS,  # f was :F
    "E": hpo.SEGOL_V,
    "e": hpo.XSEGOL,  # e was :E
    '"': hpo.TSERE,
    "I": hpo.XIRIQ,
    "O": hpo.XOLAM,
    "o": hpo.XOLAM,
    "ḥ": hpo.XOLAM_XFV,
    "U": hpo.QUBUTS,
    ":": hpo.SHEVA,
    ".": hpo.DAGESH_OM,
    ",": hpo.RAFE,
    "-": hpu.MAQ,
}
_TRANSLATION_DIC = {
    "/": None,
    **_TRANSLATION_DIC_RETAINING_SLASH,
}
_ACCENTS = {
    "00": hpu.SOPA,
    "01": ha.SEG_A,
    "02": ha.ZARQA,
    "03": ha.PASH,
    "04": ha.TEL_Q,
    "05": hpu.PAS,
    "10": ha.YETIV,
    "13": ha.DEXI,
    "11": ha.GER_M,
    "12": ha.GER_2,  # garshayim (preposed)
    "14": ha.TEL_G,
    "24": ha.TEL_Q,  # 4 uses as stress-helper to acc04 (24\S+04); 1 use as non-stress-helper
    "33": ha.PASH,  # >3800 uses as stress-helper to acc03 (33\S+03); number of uses as non-stress-helper is unknown (may be 0)
    "44": ha.TEL_G,  # 1 use as stress-helper to acc14 ([^a-z]14\S+44); 3 uses as non-stress-helper
    "52": "\N{HEBREW MARK UPPER DOT}",
    "60": ha.OLE,
    "61": ha.GER,
    "62": ha.GER_2,
    "63": ha.QADMA,
    "64": ha.ILUY,
    "65": ha.SHAL,
    "80": ha.ZAQEF_Q,
    "81": ha.REV,
    "82": ha.ZARQA_SH,  # 2 uses as stress-helper to acc02 (82\S+02); >200 uses as tsinnorit
    "83": ha.PAZER,
    "84": ha.QARNEY,  # aka pazer gadol
    "85": ha.ZAQEF_G,
    "35": sd.ZWJ + hpo.METEG,  # medial
    "53": "\N{HEBREW MARK LOWER DOT}",
    "70": ha.MAHA,
    "71": ha.MER,
    "72": ha.MER_2,
    "73": ha.TIP,
    "74": ha.MUN,
    "75": hpo.METEG,  # left (normal)
    "91": ha.TEVIR,
    "92": ha.ATN,
    "93": ha.YBY,  # aka galgal
    "94": ha.DARGA,
    "95": hpo.METEG,  # right ("early")
}
# uword('A12C34')
# uword('A1234')
_TRANSLATION_TABLE = str.maketrans(_TRANSLATION_DIC)
_TRANSLATION_TABLE_RETAINING_SLASH = str.maketrans(_TRANSLATION_DIC_RETAINING_SLASH)
_PASS_THRUS = {"*kk", "**qq"}
