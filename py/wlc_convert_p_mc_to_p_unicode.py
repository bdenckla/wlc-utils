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


_FN_TABLE_TOP = {
    "header": lambda x: x,
    "verses": lambda x: sl_map(_convert_verse, x)
}
_FN_TABLE_VERSE = {
    "bcv": lambda x: x,
    "vels": lambda x: sl_map(_convert_verse_element, x)
}
_FN_TABLE_VERSE_ELEMENT = {
    "string": lambda x: x,
    "parasep": lambda x: x,
    "word": lambda x: x,
    "notes": lambda x: x,
    "kq": lambda x: x,
}
