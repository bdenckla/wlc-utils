from __future__ import annotations

from mb_cmn import hebrew_accents as ha
from mb_cmn import hebrew_points as hpo
from mb_cmn import uni_heb


def _rm_parens_and_underscore(text: str) -> str:
    return text.translate({ord(ch): None for ch in "()_"})


_ACC_ABBREV_BY_CHAR: dict[str, str] = {
    char: _rm_parens_and_underscore(abbrev)
    for char, abbrev in uni_heb._HE_AND_NONHE_ACC_PAIRS
}

_TOKEN_TO_ACC_CHAR: dict[str, str] = {
    "silluq": hpo.MTGOSLQ,
    "atnach": ha.ATN,
    "segolta": ha.SEG_A,
    "zaqef": ha.ZAQ_Q,
    "zaqefgadol": ha.ZAQ_G,
    "tifcha": ha.TIP,
    "revia": ha.REV,
    "pashta": ha.PASH,
    "yetiv": ha.YET,
    "tevir": ha.TEV,
    "geresh": ha.GER,
    "gershayim": ha.GER_2,
    "munach": ha.MUN,
    "mereka": ha.MER,
    "merkha": ha.MER,
    "mahpak": ha.MAH,
    "darga": ha.DAR,
    "azla": ha.QOM,
    "telishagedola": ha.TEL_G,
    "big_telisha": ha.TEL_G,
    "pazer": ha.PAZ,
    "telishaqetanna": ha.TEL_Q,
    "zarqa": ha.Z_OR_TSOR,
}

# Keep vendored mb_cmn mappings untouched; accgram display abbreviations that
# are repo-specific belong here as explicit overrides.
_TOKEN_ABBREV_OVERRIDES: dict[str, str] = {
    "silluq": "slq",
    "zarqa": "zar",
}

_TOKEN_ABBREV: dict[str, str] = {
    token: _ACC_ABBREV_BY_CHAR[accent_char]
    for token, accent_char in _TOKEN_TO_ACC_CHAR.items()
}
_TOKEN_ABBREV.update(_TOKEN_ABBREV_OVERRIDES)
# This appears in parse output but is not a standalone Unicode accent name.
_TOKEN_ABBREV["legarmeh"] = "lgm"


def abbreviate_branch_label(label: str) -> str:
    base_label = label.strip()
    suffix = ""
    if base_label.endswith("_clause"):
        base_label = base_label[: -len("_clause")]
        suffix = "c"
    elif base_label.endswith("_phrase"):
        base_label = base_label[: -len("_phrase")]
        suffix = "p"

    tokens = [token for token in base_label.split("_") if token]
    if tokens and all(token in _TOKEN_ABBREV for token in tokens):
        short_base = "".join(_TOKEN_ABBREV[token] for token in tokens)
    elif tokens:
        short_base = "_".join(_TOKEN_ABBREV.get(token, token) for token in tokens)
    else:
        short_base = base_label

    return f"{short_base}{suffix}"


def abbreviate_leaf_text(text: str) -> str:
    stripped = text.strip()
    if stripped == "ERROR":
        return "ERROR"

    tokens = [token for token in stripped.split() if token]
    if not tokens:
        return stripped

    return " ".join(_TOKEN_ABBREV.get(token, token) for token in tokens)