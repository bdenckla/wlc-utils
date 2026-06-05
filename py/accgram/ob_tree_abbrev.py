from __future__ import annotations

_TOKEN_ABBREV: dict[str, str] = {
    "silluq": "slq",
    "atnach": "atn",
    "zaqef": "zqf",
    "pashta": "psh",
    "revia": "rv",
    "tifcha": "tf",
    "tevir": "tvr",
    "geresh": "gr",
    "munach": "mun",
    "mereka": "mr",
    "mahpak": "mhp",
    "darga": "dar",
    "yetiv": "ytv",
}


def abbreviate_branch_label(depth: int, label: str) -> str:
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

    return f"{depth}-{short_base}{suffix}"


def abbreviate_leaf_text(text: str) -> str:
    stripped = text.strip()
    if stripped == "ERROR":
        return "ERROR"

    tokens = [token for token in stripped.split() if token]
    if not tokens:
        return stripped

    return " ".join(_TOKEN_ABBREV.get(token, token) for token in tokens)