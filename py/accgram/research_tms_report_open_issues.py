from __future__ import annotations

from py_html import wlc_utils_html

_ITEM_FOI_NON_REVIA = (
    "munax-legarmeh (⅃-leg)\u2026non-revia:"
    " Why do only 5 of the 17 verses whose FOI category starts with"
    " \u201c⅃-leg\u2026non-revia\u201d cause trouble for the checker,"
    " while the other 12 do not?"
)

_ITEM_ZARQA_ON_LAMED = (
    "zarqa on lamed (accent 82 preceding lamed):"
    " WLC encodes 12 such cases with accent 82 placed before the lamed rather than after it."
    " Why does only 1 of these 12 cases cause trouble for the checker?"
)


def build_open_issues_section() -> tuple[object, ...]:
    list_items = (_ITEM_FOI_NON_REVIA, _ITEM_ZARQA_ON_LAMED)
    return (
        wlc_utils_html.heading_level_2("Open Issues"),
        wlc_utils_html.unordered_list(list_items),
    )
