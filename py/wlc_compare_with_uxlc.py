import py.my_uxlc as my_uxlc
import py.my_convert_citation_from_wlc_to_uxlc as w2u
import py.my_uword as my_uword
import py.wlc_utils as wlc_utils
import py.my_uni_heb as uh
import unicodedata


def compare(parsed_wlc_42x):
    books_dir = "../wlc-utils-io/in/Tanach-26.0--UXLC-1.0--2020-04-01/Books"
    uxlc = my_uxlc.read_all_books(books_dir)
    misc = {"diffs": []}
    for wlc_verse in parsed_wlc_42x["verses"]:
        wlc_bcv = wlc_verse["bcv"]
        wlc_comparables = _comparables(wlc_verse)
        uxlc_verse = _uxlc_verse(uxlc, wlc_bcv)
        assert len(wlc_comparables) == len(uxlc_verse)
        misc["wlc_bcv"] = wlc_bcv
        for wlc_str, uxlc_str in zip(wlc_comparables, uxlc_verse):
            _compare(misc, wlc_str, uxlc_str)
    return _for_json(misc["diffs"])


def _uxlc_verse(uxlc, wlc_bcv):
    std_bkid, chnu, vrnu = w2u.get_std_bcv(wlc_bcv)
    return uxlc[std_bkid][chnu - 1][vrnu - 1]


def _comparables(wlc_verse):
    comparables = map(_comparable, wlc_verse["vels"])
    return list(filter(None, comparables))


def _comparable(wlc_velsod):
    if isinstance(wlc_velsod, dict):
        if wlc_utils.is_parasep(wlc_velsod):
            return None
        return _comparable(wlc_velsod["word"])
    wlc_str = wlc_velsod
    if wlc_str.startswith("*"):
        if wlc_str.startswith("**"):
            return None if wlc_str == "**qq" else wlc_str.removeprefix("**")
        return None
    return wlc_str


def _compare(io_misc, wlc_str, uxlc_str):
    wlc_str_u = my_uword.uword(wlc_str)
    uxlc_str = uxlc_str.replace("/", "").replace(" ", "")
    wlc_str_u_n = unicodedata.normalize("NFC", wlc_str_u)
    uxlc_str_n = unicodedata.normalize("NFC", uxlc_str)
    if wlc_str_u_n != uxlc_str_n:
        _record_diff(io_misc, wlc_str, wlc_str_u, uxlc_str)


def _for_json(diffs):
    num_diffs_for_json = min(len(diffs), 2500)
    return list(map(_for_json_single, diffs[:num_diffs_for_json]))


def _for_json_single(diff):
    return diff


def _record_diff(io_misc, wlc_str, wlc_str_u, uxlc_str):
    diff = {
        "bcv": io_misc["wlc_bcv"],
        "wlc_str": wlc_str,
        "wlc_str_t": my_uword.tword(wlc_str),
        "wu": uh.comma_shunnas(wlc_str_u) + "\n" + uh.comma_shunnas(uxlc_str),
    }
    io_misc["diffs"].append(diff)
