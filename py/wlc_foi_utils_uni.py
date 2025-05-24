import re
import pycmn.uni_norm_fragile as unf
import pycmn.hebrew_accents as ha
import pycmn.hebrew_letters as hl
import pycmn.hebrew_points as hpo

def collect_uni(io_fois, wlc_id, bcv, velsod):
    word = _get_word(velsod)
    if word is None:
        return
    fcomps = unf.get_fragile_comps(word)
    dropped, dropped_n = fcomps
    if dropped == dropped_n:
        return
    fragile_foi = io_fois["fragile_foi"]
    pattkey_found = None
    for pattkey, patt in _PATTS:
        if re.search(patt, word):
            assert pattkey_found is None
            pattkey_found = pattkey
    ffrec = _mk_ffrec(bcv, word, fcomps, pattkey_found)
    fragile_foi.append(ffrec)


_PATTS = {
    ("patt-lauy", hl.LAMED + hpo.QAMATS + ha.ATN + hpo.XIRIQ),
}


def _mk_ffrec(bcv, word, fcomps, pattkey):
    dropped, dropped_n = fcomps
    return {
        "bcv": bcv,
        "word": word,
        "dropped": dropped,
        "dropped_n": dropped_n,
        "pattkey": pattkey,
    }


def _get_word(velsod):
    if isinstance(velsod, dict):
        return velsod.get("word")
    assert isinstance(velsod, str)
    return velsod

