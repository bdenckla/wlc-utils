from __future__ import annotations

import json

from mb_cmn import my_diffs

_PASEQ = "׀"


def diff_wlc_mam(
    wlc422_verse: object,
    mam_simple_verse: object,
) -> list[dict[str, object]] | dict[str, object] | None:
    if not isinstance(wlc422_verse, dict) or not isinstance(mam_simple_verse, dict):
        return None

    wlc_vels = wlc422_verse.get("vels")
    mam_vels = mam_simple_verse.get("vels")
    if not isinstance(wlc_vels, list) or not isinstance(mam_vels, list):
        return None

    wlc_vels = _normalize_paseq_tokenization(wlc_vels)
    mam_vels = _normalize_paseq_tokenization(mam_vels)

    wlc_keys = [_diff_key(token) for token in wlc_vels]
    mam_keys = [_diff_key(token) for token in mam_vels]
    diff_pairs = my_diffs.get(wlc_keys, mam_keys, outa=wlc_vels, outb=mam_vels)
    rendered = [_render_diff_pair(left, right) for left, right in diff_pairs]
    if len(rendered) == 1:
        return rendered[0]
    return rendered


def _normalize_paseq_tokenization(vels: list[object]) -> list[object]:
    out_vels: list[object] = []
    for token in vels:
        if (
            isinstance(token, str)
            and token == _PASEQ
            and out_vels
            and isinstance(out_vels[-1], str)
            and out_vels[-1] != _PASEQ
        ):
            out_vels[-1] = f"{out_vels[-1]}{_PASEQ}"
            continue
        out_vels.append(token)
    return out_vels


def _render_diff_pair(
    left: list[object] | None, right: list[object] | None
) -> dict[str, object]:
    left = [] if left is None else left
    right = [] if right is None else right

    notes = _wlc_notes_only_delta(left, right)
    if notes is not None:
        return {"wlc_adds_notes": notes}

    return {
        "wlc422": _collapse_singleton_list(left),
        "mam_simple": _collapse_singleton_list(right),
    }


def _collapse_singleton_list(tokens: list[object]) -> object:
    if len(tokens) == 1:
        return tokens[0]
    return tokens


def _wlc_notes_only_delta(left: list[object], right: list[object]) -> object | None:
    if len(left) != 1 or len(right) != 1:
        return None

    left_token = left[0]
    right_token = right[0]
    if not isinstance(left_token, dict) or not isinstance(right_token, str):
        return None

    if set(left_token.keys()) != {"word", "notes"}:
        return None

    word = left_token.get("word")
    if not isinstance(word, str) or word != right_token:
        return None

    return left_token.get("notes")


def _diff_key(token: object) -> str:
    if isinstance(token, str):
        return token
    return json.dumps(token, ensure_ascii=False, sort_keys=True)
