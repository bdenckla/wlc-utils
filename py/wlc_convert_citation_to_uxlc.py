""" Exports get_tanach_dot_us_url, get_uxlc_bkid. """

import py.bib_locales as tbn

_WLC_BKID_TO_STD_BKID = {
    "gn": tbn.BK_GENESIS,
    "ex": tbn.BK_EXODUS,
    "lv": tbn.BK_LEVIT,
    "nu": tbn.BK_NUMBERS,
    "dt": tbn.BK_DEUTER,
    "js": tbn.BK_JOSHUA,
    "ju": tbn.BK_JUDGES,
    "1s": tbn.BK_FST_SAM,
    "2s": tbn.BK_SND_SAM,
    "1k": tbn.BK_FST_KGS,
    "2k": tbn.BK_SND_KGS,
    "is": tbn.BK_ISAIAH,
    "je": tbn.BK_JEREM,
    "ek": tbn.BK_EZEKIEL,
    "ho": tbn.BK_HOSHEA,
    "jl": tbn.BK_JOEL,
    "am": tbn.BK_AMOS,
    "ob": tbn.BK_OVADIAH,
    "jn": tbn.BK_JONAH,
    "mi": tbn.BK_MIKHAH,
    "na": tbn.BK_NAXUM,
    "hb": tbn.BK_XABA,
    "zp": tbn.BK_TSEF,
    "hg": tbn.BK_XAGGAI,
    "zc": tbn.BK_ZEKHAR,
    "ma": tbn.BK_MALAKHI,
    "1c": tbn.BK_FST_CHR,
    "2c": tbn.BK_SND_CHR,
    "ps": tbn.BK_PSALMS,
    "jb": tbn.BK_JOB,
    "pr": tbn.BK_PROV,
    "ru": tbn.BK_RUTH,
    "ca": tbn.BK_SONG,
    "ec": tbn.BK_QOHELET,
    "lm": tbn.BK_LAMENT,
    "es": tbn.BK_ESTHER,
    "da": tbn.BK_DANIEL,
    "er": tbn.BK_EZRA,
    "ne": tbn.BK_NEXEM,
}


def get_std_bcv(wlc_bcv_str):
    """
    Return a bcv triple like ('Genesis', 1, 1) for a WLC bcv string like 'gn1:1'.
    The returned book ID is a standard book ID.
    (bcv: book, chapter, & verse).
    """
    std_bkid = get_std_bkid(wlc_bcv_str)
    cv_pair = get_cv_pair(wlc_bcv_str)
    return std_bkid, *cv_pair


def get_std_bkid(wlc_bcv_str):
    """Return the standard book ID for WLC bcv string (bcv: book, chapter, & verse)"""
    wlc_bkid = wlc_bcv_str[:2]
    return _WLC_BKID_TO_STD_BKID[wlc_bkid]


def get_cv_pair(wlc_bcv_str):
    """Return chapter & verse integer pair for WLC bcv string (bcv: book, chapter, & verse)"""
    wlc_cv_str = _get_cv_str(wlc_bcv_str)
    c_str, v_str = wlc_cv_str.split(":")
    return int(c_str), int(v_str)


def _get_cv_str(wlc_bcv_str):
    wlc_cv_str = wlc_bcv_str[2:]
    return wlc_cv_str
