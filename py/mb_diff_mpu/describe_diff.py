"""Vendored Hebrew code-point names from MAM-basics describe_diff.py."""

import unicodedata

from mb_cmn import hebrew_accents as ha
from mb_cmn import hebrew_points as hpo
from mb_cmn import hebrew_punctuation as hpu


LETTER_NAMES = {
    "א": "alef",
    "ב": "bet",
    "ג": "gimel",
    "ד": "dalet",
    "ה": "he",
    "ו": "vav",
    "ז": "zayin",
    "ח": "het",
    "ט": "tet",
    "י": "yod",
    "ך": "final-kaf",
    "כ": "kaf",
    "ל": "lamed",
    "ם": "final-mem",
    "מ": "mem",
    "ן": "final-nun",
    "נ": "nun",
    "ס": "samekh",
    "ע": "ayin",
    "ף": "final-pe",
    "פ": "pe",
    "ץ": "final-tsadi",
    "צ": "tsadi",
    "ק": "qof",
    "ר": "resh",
    "ש": "shin",
    "ת": "tav",
}

ACCENT_NAMES = {
    ha.ATN: "etnaḥta",
    ha.SEG_A: "segol-accent",
    ha.SHA: "shalshelet",
    ha.ZAQ_Q: "zaqef-qatan",
    ha.ZAQ_G: "zaqef-gadol",
    ha.TIP: "tipeḥa",
    ha.REV: "revia",
    ha.ZSH_OR_TSIT: "zarqa-sh",
    ha.PASH: "pashta",
    ha.YET: "yetiv",
    ha.TEV: "tevir",
    ha.GER: "geresh",
    ha.GER_M: "geresh-muqdam",
    ha.GER_2: "gershayim",
    ha.QAR: "qarney-para",
    ha.TEL_G: "telisha-gedola",
    ha.PAZ: "pazer",
    ha.ATN_H: "atnaḥ-hafukh",
    ha.MUN: "munaḥ",
    ha.MAH: "mahapakh",
    ha.MER: "merkha",
    ha.MER_2: "merkha-kefula",
    ha.DAR: "darga",
    ha.QOM: "qadma",
    ha.TEL_Q: "telisha-qetana",
    ha.YBY: "yeraḥ-ben-yomo",
    ha.OLE: "ole",
    ha.ILU: "iluy",
    ha.DEX: "deḥi",
    ha.Z_OR_TSOR: "zarqa",
    hpu.MCIRC: "masora-circle",
}

POINT_NAMES = {
    hpo.SHEVA: "shewa",
    hpo.XSEGOL: "ḥataf-segol",
    hpo.XPATAX: "ḥataf-pataḥ",
    hpo.XQAMATS: "ḥataf-qamats",
    hpo.XIRIQ: "ḥiriq",
    hpo.TSERE: "tsere",
    hpo.SEGOL_V: "segol",
    hpo.PATAX: "pataḥ",
    hpo.QAMATS: "qamats",
    hpo.QAMATS_Q: "qamats-qatan",
    hpo.XOLAM: "ḥolam",
    hpo.XOLAM_XFV: "ḥolam-ḥaser-for-vav",
    hpo.QUBUTS: "qubuts",
    hpo.DAGOMOSD: "dagesh",
    hpo.MTGOSLQ: "meteg",
    hpo.RAFE: "rafeh",
    hpo.SHIND: "shin-dot",
    hpo.SIND: "sin-dot",
    hpo.VARIKA: "varika",
}


def letter_name(ch):
    return LETTER_NAMES.get(ch, unicodedata.name(ch, f"U+{ord(ch):04X}"))


def accent_name(ch, poetic=False):
    return ACCENT_NAMES.get(ch, unicodedata.name(ch, f"U+{ord(ch):04X}"))


def mark_name(ch):
    return POINT_NAMES.get(ch, unicodedata.name(ch, f"U+{ord(ch):04X}"))