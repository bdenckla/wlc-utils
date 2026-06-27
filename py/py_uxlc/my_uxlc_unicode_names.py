"""Exports name, names."""

from cmn import legacy_names


def names(string):
    """
    Return a string with the space-separated the UXLC names
    for the Unicode code points in the given string.
    """
    names_list = list(map(name, string))
    return " ".join(names_list)


def name(string_len_1):
    """Return the UXLC name for the given Unicode code point."""
    my_un = legacy_names.legacy_name(string_len_1)
    # ndb: no dot below.  The search literal is the *decomposed* ḥ (h +
    # U+0323), matching legacy_name's already-decomposed output, so this
    # actually strips the dot.  E.g. etnaḥta becomes just etnahta.  # translit-ok: illustrates UXLC output
    my_un_ndb = my_un.replace("ḥ", "h")
    my_un_ndb_fn = my_un_ndb.split("/")[0]  # first name in a slash seq
    # E.g., meteg/siluq becomes just meteg
    uxlc_un = _UXLC_UNS.get(my_un_ndb_fn) or my_un_ndb_fn
    return uxlc_un


_UXLC_UNS = {
    "zarqa-stress-helper": "zarqa",
    "segol-vowel": "segol",
    "holam-haser-for-vav": "holam-haser",
    "tsinor": "zinor",  # translit-ok: UXLC name
    "rafeh": "rafe",
}
