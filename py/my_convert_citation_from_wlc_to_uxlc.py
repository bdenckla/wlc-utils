""" Exports get_tanach_dot_us_url, get_uxlc_bkid. """

import my_tanakh_book_names as tbn

_WLC_BKID_TO_STD_BKID = {
    'gn': tbn.BK_GENESIS,
    'ex': tbn.BK_EXODUS,
    'js': tbn.BK_JOSHUA,
    'ju': tbn.BK_JUDGES,
    '1s': tbn.BK_FST_SAM,
    '2s': tbn.BK_SND_SAM,
    '1k': tbn.BK_FST_KGS,
    '2k': tbn.BK_SND_KGS,
    'is': tbn.BK_ISAIAH,
    'je': tbn.BK_JEREM,
    'ek': tbn.BK_EZEKIEL,
    'pr': tbn.BK_PROV,
    'lm': tbn.BK_LAMENT,
    'es': tbn.BK_ESTHER,
    'da': tbn.BK_DANIEL,
    'er': tbn.BK_EZRA,
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
    """ Return the standard book ID for WLC bcv string (bcv: book, chapter, & verse) """
    wlc_bkid = wlc_bcv_str[:2]
    return _WLC_BKID_TO_STD_BKID[wlc_bkid]


def get_cv_pair(wlc_bcv_str):
    """ Return chapter & verse integer pair for WLC bcv string (bcv: book, chapter, & verse) """
    wlc_cv_str = _get_cv_str(wlc_bcv_str)
    c_str, v_str = wlc_cv_str.split(':')
    return int(c_str), int(v_str)


def _get_cv_str(wlc_bcv_str):
    wlc_cv_str = wlc_bcv_str[2:]
    return wlc_cv_str
