from __future__ import annotations

from pathlib import Path

from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import xx_data
from py_html import wlc_utils_html

_ITEM_FOI_NON_REVIA = (
    "munax-legarmeh (⅃-leg)\u2026non-revia:"
    " All 17 verses whose FOI category starts with"
    " “⅃-leg…non-revia” now parse with a genuine legarmeh: the"
    " munaḥ-legarmeh-not-before-revia mark (scanner code 74{TEXT}05) is read"
    " as a real legarmeh at each of has_legarmeh’s 17 listed passages."
    " (Previously the goerwitz C binary keyed that list on book abbreviations"
    " — “Lev 10:6”, “Dan 3:2” — that do not match the new-format full"
    " booknames the scanner emits, so legarmeh fired for Ruth 1:2 alone and"
    " the other 16 mis-parsed.) Of the 17, only Isaiah 36:2 is still an"
    " oddball — and not because of the legarmeh reading, which now succeeds,"
    " but because its legarmeh_phrase reduces to ERROR for an unrelated"
    " prose-grammar reason. Why does Isaiah 36:2’s legarmeh_phrase fail to"
    " reduce?"
)

_FOI_NON_REVIA_CATEGORY_LINKS = (
    xx_data.FOI_PAZ_CATEGORY_LINK,
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
    " Why are only 7 of these 12 cases oddballs?"
)


# Now that has_legarmeh keys on structured book refs, the munaḥ-legarmeh-not-
# before-revia mark (scanner code 74{TEXT}05) is read as a real LEGARMEH at all
# 17 listed passages, so 16 of them parse cleanly with a legarmeh_phrase. These
# two trees make visible why one verse, Isaiah 36:2, still does not. In Daniel
# 3:2 the legarmeh heads a well-formed legarmeh_phrase and the verse parses; in
# Isaiah 36:2 the very same legarmeh reading fires, but its legarmeh_phrase
# reduces to ERROR for an independent prose-grammar reason — so Isaiah 36:2 is
# the lone remaining oddball of the 17.
_ITEM_FOI_NON_REVIA_TREES = (
    ("Daniel 3:2 (legarmeh fires; legarmeh_phrase reduces)", "da 3:2", "wlc_422_ps_da_ag.txt"),
    ("Isaiah 36:2 (legarmeh fires; legarmeh_phrase reduces to ERROR)", "is 36:2", "wlc_422_ps_is_ag.txt"),
)


def _build_foi_non_revia_trees(base_dir: Path | None) -> tuple[object, ...]:
    if base_dir is None:
        return ()
    figures: list[object] = []
    for caption, ref, output_file in _ITEM_FOI_NON_REVIA_TREES:
        tree = ob_error_context.collect_tree_for_ref(
            ref=ref, output_file=output_file, base_dir=base_dir
        )
        if tree is None:
            continue
        figures.append(
            wlc_utils_html.figure(
                (
                    wlc_utils_html.figcaption(caption),
                    wlc_utils_html.div(
                        (ob_tree_table.render_error_tree_table(tree),),
                        {"class": "goerwitz-obs-tree-wrap"},
                    ),
                )
            )
        )
    return tuple(figures)


def _build_foi_non_revia_item(base_dir: Path | None) -> tuple[object, ...]:
    category_links = tuple(
        wlc_utils_html.anchor(label, {"href": href})
        for label, href in _FOI_NON_REVIA_CATEGORY_LINKS
    )
    return (
        _ITEM_FOI_NON_REVIA,
        wlc_utils_html.unordered_list(category_links),
        *_build_foi_non_revia_trees(base_dir),
    )


def build_open_issues_section(base_dir: Path | None = None) -> tuple[object, ...]:
    list_items = (_build_foi_non_revia_item(base_dir), _ITEM_ZARQA_ON_LAMED)
    return (
        wlc_utils_html.heading_level_2("Open Issues"),
        wlc_utils_html.unordered_list(list_items),
    )
