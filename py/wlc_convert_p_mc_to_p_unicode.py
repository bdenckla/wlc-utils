import py.wlc_uword as wlc_uword
from py.my_utils import dv_dispatch
from py.my_utils import sl_map


def convert_p_mc_to_p_unicode(p_mc):
    """
    Convert "parsed M-C" (parsed Michigan-Claremont) (p_mc)
    to "parsed Unicode" (p_unicode)
    """
    return dv_dispatch(_FN_TABLE_TOP, p_mc)


def _convert_verse(verse):
    return dv_dispatch(_FN_TABLE_VERSE, verse)


def _convert_verse_element(vel):
    if isinstance(vel, str):
        return _FN_TABLE_VERSE_ELEMENT["string"](vel)
    return dv_dispatch(_FN_TABLE_VERSE_ELEMENT, vel)


def _convert_string(word):
    assert isinstance(word, str)
    return wlc_uword.uword(word)


def _convert_kq(ketiv_qere):
    assert isinstance(ketiv_qere, (list, tuple))
    assert len(ketiv_qere) == 2
    ketiv, qere = ketiv_qere
    assert len(ketiv) in (0, 1, 2)
    assert len(qere) in (0, 1, 2)
    return sl_map(_convert_verse_element, ketiv), sl_map(_convert_verse_element, qere)


_FN_TABLE_TOP = {
    "header": lambda x: x,
    "verses": lambda x: sl_map(_convert_verse, x)
}
_FN_TABLE_VERSE = {
    "bcv": lambda x: x,
    "vels": lambda x: sl_map(_convert_verse_element, x)
}
_FN_TABLE_VERSE_ELEMENT = {
    "string": _convert_string,
    "parasep": lambda x: x,
    "word": _convert_string,
    "notes": lambda x: x,
    "kq": _convert_kq,
}
