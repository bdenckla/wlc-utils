import re
import pycmn.hebrew_points as hpo
import pycmn.hebrew_accents as ha
import pycmn.hebrew_punctuation as hpu
import pycmn.str_defs as sd


def tword(mcword: str):
    stage = mcword.replace(":A", "a").replace(":F", "f").replace(":E", "e")
    stage = re.sub(_XOLAM_PATT1, _xolam_replacement1, stage)
    stage = re.sub(_XOLAM_PATT2, _xolam_replacement2, stage)
    stage = re.sub(_XOLAM_PATT3, _xolam_replacement3, stage)
    stage = re.sub(_EARLY_MTG_PATT, _early_mtg_replacement, stage)
    stage = re.sub(_PREPOS_PATT, _prepos_replacement, stage)
    stage = re.sub(_FINAL_PATT, _final_replacement, stage)
    stage = re.sub(_LAOY_PATT, _laoy_replacement, stage)
    stage = stage.replace("81" + "11", "11" + "81")  # rev-ger_m becomes ger_m-rev
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
    return re.sub(r"\d\d", _digits_replacement, stage)


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
_PREPOS_PATT = r"^(\*\*|)(10|11|12|13|14)" + _paren(_LETT + _NON_LETT_STAR)
_EARLY_MTG_PATT = '([afeAFE"I:U])95'
_XOLAM_PATT1 = (
    "O" + _paren(_NON_LETT_STAR) + _paren(_sqbrac(_LETT_GUTS_NO_VAV) + '|W[AFE"I:U]')
)
_XOLAM_PATT2 = "O" + _paren(_NON_LETT_STAR) + "W"
_XOLAM_PATT3 = "W" + _paren(_NON_LETT_STAR) + "o"
_FINAL_PATT = r"[KMNPC]" + _NON_LETT_STAR_DOLL


def _prepos_replacement(matchobj):
    dsoe, prepos, lpzmnl = matchobj.groups()
    # dsoe: ds or empty (ds: double-star, i.e. **, i.e. qere marker)
    # prepos: the two-digit prepositive accent code
    # lpzmnl: letter plus zmnl (zmnl: zero or more non-letters)
    return dsoe + lpzmnl + prepos


def _early_mtg_replacement(matchobj):
    groups = matchobj.groups()
    return "95" + groups[0]


def _xolam_replacement1(matchobj):
    groups = matchobj.groups()
    return "o" + groups[0] + groups[1]


def _xolam_replacement2(matchobj):
    groups = matchobj.groups()
    return groups[0] + "WO"


def _xolam_replacement3(matchobj):
    groups = matchobj.groups()
    return "W" + groups[0] + "ḥ"


def _final_replacement(matchobj):
    nonfinal = matchobj.group()
    return nonfinal.translate(_TRANSLATION_TABLE_FOR_FINAL_FORMS)


def _laoy_replacement(matchobj):
    gra, gro, gry = matchobj.groups()
    return "L" + gra + gry + gro


def _digits_replacement(matchobj):
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
    ".": hpo.DAGOMOSD,
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
    "02": ha.Z_OR_TSOR,
    "03": ha.PASH,
    "04": ha.TEL_Q,
    "05": hpu.PASOLEG,
    "10": ha.YET,
    "11": ha.GER_M,
    "12": ha.GER_2,  # garshayim (preposed)
    "13": ha.DEX,
    "14": ha.TEL_G,
    "24": ha.TEL_Q,  # 4 uses as stress-helper to acc04 (24\S+04); 1 use as non-stress-helper
    "33": ha.PASH,  # >3800 uses as stress-helper to acc03 (33\S+03); number of uses as non-stress-helper is unknown (may be 0)
    "35": sd.ZWJ + hpo.MTGOSLQ,  # medial
    "44": ha.TEL_G,  # 1 use as stress-helper to acc14 ([^a-z]14\S+44); 3 uses as non-stress-helper
    "52": hpu.UPDOT,
    "53": hpu.LODOT,
    "60": ha.OLE,
    "61": ha.GER,
    "62": ha.GER_2,
    "63": ha.QOM,
    "64": ha.ILU,
    "65": ha.SHA,
    "80": ha.ZAQ_Q,
    "81": ha.REV,
    "82": ha.ZSH_OR_TSIT,  # 2 uses as stress-helper to acc02 (82\S+02); >200 uses as tsinnorit
    "83": ha.PAZ,
    "84": ha.QAR,  # aka pazer gadol
    "85": ha.ZAQ_G,
    "70": ha.MAH,
    "71": ha.MER,
    "72": ha.MER_2,
    "73": ha.TIP,
    "74": ha.MUN,
    "75": hpo.MTGOSLQ,  # left (normal)
    "91": ha.TEV,
    "92": ha.ATN,
    "93": ha.YBY,  # aka galgal
    "94": ha.DAR,
    "95": hpo.MTGOSLQ,  # right ("early")
}
# uword('A12C34')
# uword('A1234')
_TRANSLATION_TABLE = str.maketrans(_TRANSLATION_DIC)
_TRANSLATION_TABLE_RETAINING_SLASH = str.maketrans(_TRANSLATION_DIC_RETAINING_SLASH)
_PASS_THRUS = {"*kk", "**qq"}
_OVER_ACCENTS = [a for a in _ACCENTS.keys() if _ACCENTS[a] in ha.UNI_OVER_ACCENTS]
_OVER_ACCENTS.append("75")  # XXX Normal meteg is treated like an over-accent, i.e. like O in LAYO!
_OVER_ACCENTS_PATT = _paren("|".join(_OVER_ACCENTS))
_LAOY_PATT = r"L([AF])" + _OVER_ACCENTS_PATT + "([I:])"
