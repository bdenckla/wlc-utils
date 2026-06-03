from __future__ import annotations

from py_html import wlc_utils_html

_ITEM_FOI_NON_REVIA = (
    "munax-legarmeh (⅃-leg)\u2026non-revia:"
    " Why do only 5 of the 17 verses whose FOI category starts with"
    " \u201c⅃-leg\u2026non-revia\u201d cause trouble for the checker,"
    " while the other 12 do not?"
)

_FOI_NON_REVIA_CATEGORY_LINKS = (
    (
        "⅃-leg...non-revia ((paz)) with 0 intervening",
        "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB((paz))%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB0%C2%ABspace%C2%BBintervening",
    ),
    (
        "⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening",
        "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB((tev))%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB2%C2%ABspace%C2%BB(qa,da)%C2%ABspace%C2%BBintervening",
    ),
    (
        "⅃-leg...non-revia (ge) with 1 qa intervening",
        "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB(ge)%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB1%C2%ABspace%C2%BBqa%C2%ABspace%C2%BBintervening",
    ),
    (
        "⅃-leg...non-revia (p) with 1 (mah) intervening",
        "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB(p)%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB1%C2%ABspace%C2%BB(mah)%C2%ABspace%C2%BBintervening",
    ),
)

_ITEM_ZARQA_ON_LAMED = (
    "zarqa on lamed (accent 82 preceding lamed):"
    " WLC encodes 12 such cases with accent 82 placed before the lamed rather than after it."
    " Why does only 1 of these 12 cases cause trouble for the checker?"
)


def _build_foi_non_revia_item() -> tuple[object, ...]:
    category_links = tuple(
        wlc_utils_html.anchor(label, {"href": href})
        for label, href in _FOI_NON_REVIA_CATEGORY_LINKS
    )
    return (_ITEM_FOI_NON_REVIA, wlc_utils_html.unordered_list(category_links))


def build_open_issues_section() -> tuple[object, ...]:
    list_items = (_build_foi_non_revia_item(), _ITEM_ZARQA_ON_LAMED)
    return (
        wlc_utils_html.heading_level_2("Open Issues"),
        wlc_utils_html.unordered_list(list_items),
    )
