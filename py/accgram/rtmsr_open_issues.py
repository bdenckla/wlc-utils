from __future__ import annotations

from pathlib import Path

from py_html import wlc_utils_html

_ITEM_ZARQA_ON_LAMED = (
    "zarqa on lamed (accent 82 preceding lamed):"
    " WLC encodes 12 such cases with accent 82 placed before the lamed rather than after it."
    " Why are only 7 of these 12 cases oddballs?"
)


def build_open_issues_section(base_dir: Path | None = None) -> tuple[object, ...]:
    list_items = (_ITEM_ZARQA_ON_LAMED,)
    return (
        wlc_utils_html.heading_level_2("Open Issues"),
        wlc_utils_html.unordered_list(list_items),
    )
