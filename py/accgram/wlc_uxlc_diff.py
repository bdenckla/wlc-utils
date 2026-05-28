from __future__ import annotations

import json

from mb_cmn import my_diffs


def diff_wlc_uxlc(
    wlc422_verse: object,
    uxlc_nodes: object,
) -> list[dict[str, object | None]] | None:
    if not isinstance(wlc422_verse, dict) or not isinstance(uxlc_nodes, list):
        return None

    wlc_vels = wlc422_verse.get("vels")
    if not isinstance(wlc_vels, list):
        return None

    wlc_keys = [_diff_key(token) for token in wlc_vels]
    uxlc_keys = [_diff_key(token) for token in uxlc_nodes]
    diff_pairs = my_diffs.get(wlc_keys, uxlc_keys, outa=wlc_vels, outb=uxlc_nodes)
    return [{"wlc422": left, "uxlc": right} for left, right in diff_pairs]


def _diff_key(token: object) -> str:
    if isinstance(token, str):
        return token
    return json.dumps(token, ensure_ascii=False, sort_keys=True)
