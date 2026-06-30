"""Small HTML render helpers shared across the "almost errors" page sections.

The lowest presentation layer: verse-reference formatting, UXLC/MAM link
anchors, and the shared error-tree table wrapper.  Imported by the per-section
modules (``almost_errors_charities``, ``almost_errors_oddities``) and the
``almost_errors_html`` coordinator; depends on nothing else in the page.
"""

from __future__ import annotations

import re

from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import rtms_report
from accgram.uni_to_marks import is_accent, is_base_letter
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import bib_locales as bl
from py_html import wlc_utils_html as H
from py_wlc import my_wlc_bcv_str


def ref_display(bcv: str) -> str:
    bb = bcv[:2]
    chv = bcv[2:]
    return f"{wlc_bb_to_bk39id(bb)} {chv}"


def ref_short(bcv: str) -> str:
    """Compact ``G5:29``-style reference (short book name, no space) for a ``gn5:29`` bcv."""
    chnu, vrnu = (int(part) for part in bcv[2:].split(":"))
    return bl.short_bcv((wlc_bb_to_bk39id(bcv[:2]), chnu, vrnu))


def accents_and_letters(word: str) -> str:
    """Reduce a pointed Hebrew word to just its base letters and accents, dropping vowels,
    dagesh, and other points.  Used for the alternate-form columns, which illustrate accent
    placement, not vocalization."""
    return "".join(ch for ch in word if is_base_letter(ch) or is_accent(ch))


def verse_links(bcv: str) -> object:
    bb, chnu, vrnu, _bcv = rtms_report.parse_ref_to_wlc_bcv(f"{bcv[:2]} {bcv[2:]}")
    links = (
        H.anchor("UXLC", {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)}),
        " | ",
        H.anchor("MAM", {"href": rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)}),
    )
    return H.para(links)


def render_tree(tree_text: str) -> object:
    tree = ob_error_context.parse_tree_from_text(tree_text)
    if tree is not None:
        return H.div(
            (ob_tree_table.render_error_tree_table(tree),),
            {"class": "goerwitz-obs-tree-wrap"},
        )
    return H.div(
        (H.htel_mk_inline("pre", None, tree_text),),
        {"class": "goerwitz-obs-tree-wrap"},
    )


def hbo(text: str) -> object:
    return H.span(text, {"lang": "hbo"})


# A run of Hebrew-block characters -- letters, points, accents, and the maqaf / sof pasuq
# that join or end an accent-word.  Covers both bare consonantal skeletons and fully-pointed
# words, so the whole word stays in one hbo span rather than being split at its marks.
_HEBREW_RUN_RE = re.compile(r"[֐-׿]+")


def wrap_hebrew_runs(text: str) -> tuple[object, ...]:
    """Split ``text`` into a flat (string | hbo-span) sequence, wrapping each Hebrew run.

    Wrapping the Hebrew words in ``lang="hbo"`` spans gives them the Hebrew font and
    (via the stylesheet) keeps them upright -- Hebrew is never italicized."""
    pieces: list[object] = []
    cursor = 0
    for match in _HEBREW_RUN_RE.finditer(text):
        start, end = match.span()
        if start > cursor:
            pieces.append(text[cursor:start])
        pieces.append(hbo(match.group(0)))
        cursor = end
    if cursor < len(text):
        pieces.append(text[cursor:])
    return tuple(pieces)


def link(text: str, href: str) -> object:
    return H.anchor(text, {"href": href})


def uxlc_change_link(compact: str) -> object:
    """Anchor to a tanach.us changeset, labelled by its ``changeset-n`` id.

    ``compact`` is the ``release/changeset-n`` form (e.g. ``2020.10.19/2020.09.22-1``)
    the goerwitz page's “UXLC change” links use, expanded by the shared
    ``rtms_report`` helper so the URL form stays single-sourced."""
    changeset_n = compact.partition("/")[2]
    return H.anchor(changeset_n, {"href": rtms_report.expand_uxlc_change_ref(compact)})
