from __future__ import annotations

from pathlib import Path

from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import xx_data
from py_html import wlc_utils_html

_ITEM_FOI_NON_REVIA = (
    "munax-legarmeh (⅃-leg)\u2026non-revia:"
    " Of the 17 verses whose FOI category starts with"
    " \u201c⅃-leg\u2026non-revia\u201d, 15 are oddballs (they parse to ERROR),"
    " while only 2 — Daniel 3:2 and Ruth 1:2 — are not."
    " Why are those two not oddballs?"
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


# The two verses that escape oddball status do so for two *different* reasons,
# which their parse trees make visible. The munaḥ-legarmeh-not-before-revia mark
# (scanner code 74{TEXT}05) is read as a real LEGARMEH only inside one of
# has_legarmeh's 17 listed passages; elsewhere it degrades to a plain MUNACH with
# the paseq (05) swallowed. The list keys are book *abbreviations* ("Lev 10:6",
# "Dan 3:2"), but the new-format scanner sees *full* booknames — so the only
# listed verse whose name still matches is "Ruth 1:2". That coincidence makes
# Ruth 1:2 parse with a genuine legarmeh_phrase. Daniel 3:2 escapes for an
# unrelated reason: there the degraded munaḥ lands as a grammatical munach-pazer,
# so it parses even *without* the legarmeh reading. (Leviticus 10:6 and 21:10,
# which share Ruth 1:2's shape but lose the legarmeh reading, become oddballs.)
_ITEM_FOI_NON_REVIA_TREES = (
    ("Ruth 1:2 (mark read as legarmeh)", "ru 1:2", "wlc_422_ps_ru_ag.txt"),
    ("Daniel 3:2 (mark read as plain munaḥ)", "da 3:2", "wlc_422_ps_da_ag.txt"),
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
