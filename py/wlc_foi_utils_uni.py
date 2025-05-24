import re
import pycmn.uni_norm_fragile as unf
import pycmn.hebrew_accents as ha
import pycmn.hebrew_letters as hl
import pycmn.hebrew_points as hpo


def ff_init():
    fragile_foi = {
        "ff-counts": {},
        "ff-cases": [],
    }
    fragile_foi["ff-counts"]["misc"] = 0
    for pattkey, _patt in _PATTS:
        fragile_foi["ff-counts"][pattkey] = 0
    return fragile_foi


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
    fragile_foi["ff-cases"].append(ffrec)
    count_key = "misc" if pattkey_found is None else pattkey_found
    fragile_foi["ff-counts"][count_key] += 1


_QAMATS_OR_PATAX = f"[{hpo.QAMATS+hpo.PATAX}]"
_UNDER_ACCENTS_STR = "".join(ha.UNI_UNDER_ACCENTS)
_OVER_ACCENTS_STR = "".join(ha.UNI_OVER_ACCENTS)
_UNDER_ACCENT_PATT = f"[{_UNDER_ACCENTS_STR}]"
_OVER_ACCENT_PATT = f"[{_OVER_ACCENTS_STR}]"
_XIRIQ_OR_SHEVA = f"[{hpo.XIRIQ+hpo.SHEVA}]"
_LAUY_PATT = hl.LAMED + _QAMATS_OR_PATAX + _UNDER_ACCENT_PATT + _XIRIQ_OR_SHEVA
_LAYO_PATT = hl.LAMED + _QAMATS_OR_PATAX + _XIRIQ_OR_SHEVA + _OVER_ACCENT_PATT
_LAXY_PATT = hl.LAMED + _QAMATS_OR_PATAX + _XIRIQ_OR_SHEVA + hl.FMEM
_PATTS = {
    ("patt-lauy", _LAUY_PATT),
    ("patt-layo", _LAYO_PATT),
    ("patt-laxy", _LAXY_PATT),
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

