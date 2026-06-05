from __future__ import annotations

import re

_TROUBLEMAKER_REF_RE = re.compile(r"^(?P<bb>[0-9a-z]{2})\s+(?P<ch>\d+):(?P<vr>\d+)$")


def parse_ref(ref: str, *, row_kind: str = "troublemaker") -> tuple[str, int, int]:
    match = _TROUBLEMAKER_REF_RE.match(ref.strip())
    if match is None:
        raise ValueError(f"Malformed {row_kind} ref: {ref}")
    bb = match.group("bb")
    chnu = int(match.group("ch"))
    vrnu = int(match.group("vr"))
    return bb, chnu, vrnu


def to_compact_bcv(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb}{chnu}:{vrnu}"


def to_ref(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb} {chnu}:{vrnu}"
