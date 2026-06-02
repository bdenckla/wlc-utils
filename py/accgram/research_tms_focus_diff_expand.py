from __future__ import annotations


def structured_wlc_focus(structured_text: object) -> str | None:
    if not isinstance(structured_text, dict):
        return None

    wlc_focus = structured_text.get("wlc_focus")
    if not isinstance(wlc_focus, str):
        return None

    return wlc_focus.strip() or None


def expand_subset_diff_to_wlc_focus(
    diff_value: object,
    *,
    wlc_focus: str | None,
    rhs_key: str,
) -> object:
    if not wlc_focus:
        return diff_value

    if isinstance(diff_value, dict):
        return _expand_subset_diff_entry_to_wlc_focus(
            diff_value,
            wlc_focus=wlc_focus,
            rhs_key=rhs_key,
        )

    if isinstance(diff_value, list):
        return [
            _expand_subset_diff_entry_to_wlc_focus(
                entry,
                wlc_focus=wlc_focus,
                rhs_key=rhs_key,
            )
            for entry in diff_value
        ]

    return diff_value


def _expand_subset_diff_entry_to_wlc_focus(
    entry: object,
    *,
    wlc_focus: str,
    rhs_key: str,
) -> object:
    if not isinstance(entry, dict):
        return entry

    wlc_side = entry.get("wlc422")
    rhs_side = entry.get(rhs_key)
    if not isinstance(wlc_side, str) or not isinstance(rhs_side, str):
        return entry

    expanded_rhs = _replace_subset_words_in_focus(
        wlc_focus,
        subset_wlc=wlc_side,
        subset_rhs=rhs_side,
    )
    if expanded_rhs is None:
        return entry

    return {
        **entry,
        "wlc422": wlc_focus,
        rhs_key: expanded_rhs,
    }


def _replace_subset_words_in_focus(
    wlc_focus: str,
    *,
    subset_wlc: str,
    subset_rhs: str,
) -> str | None:
    focus_tokens = wlc_focus.split()
    subset_wlc_tokens = subset_wlc.split()
    subset_rhs_tokens = subset_rhs.split()
    if not focus_tokens or not subset_wlc_tokens or not subset_rhs_tokens:
        return None

    match_starts: list[int] = []
    match_len = len(subset_wlc_tokens)
    last_start = len(focus_tokens) - match_len
    for start in range(last_start + 1):
        if focus_tokens[start:start + match_len] == subset_wlc_tokens:
            match_starts.append(start)

    if len(match_starts) != 1:
        return None

    start = match_starts[0]
    end = start + match_len
    expanded_tokens = focus_tokens[:start] + subset_rhs_tokens + focus_tokens[end:]
    return " ".join(expanded_tokens)
