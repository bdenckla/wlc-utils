"""Small HTML render helpers shared across the "almost errors" page sections.

The lowest presentation layer: verse-reference formatting, UXLC/MAM link
anchors, and the shared error-tree table wrapper.  Imported by the per-section
modules (``almost_errors_charities``, ``almost_errors_oddities``) and the
``almost_errors_html`` coordinator; depends on nothing else in the page.
"""

from __future__ import annotations

from accgram import ob_error_context
from accgram import ob_tree_table
from accgram import rtms_report
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from py_html import wlc_utils_html as H
from py_wlc import my_wlc_bcv_str


def _ref_display(bcv: str) -> str:
    bb = bcv[:2]
    chv = bcv[2:]
    return f"{wlc_bb_to_bk39id(bb)} {chv}"


def _verse_links(bcv: str) -> object:
    bb, chnu, vrnu, _bcv = rtms_report.parse_ref_to_wlc_bcv(f"{bcv[:2]} {bcv[2:]}")
    links = (
        H.anchor("UXLC", {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)}),
        " | ",
        H.anchor("MAM", {"href": rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)}),
    )
    return H.para(links)


def _render_tree(tree_text: str) -> object:
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


def _hbo(text: str) -> object:
    return H.span(text, {"lang": "hbo"})


def _link(text: str, href: str) -> object:
    return H.anchor(text, {"href": href})


def _uxlc_change_link(compact: str) -> object:
    """Anchor to a tanach.us changeset, labelled by its ``changeset-n`` id.

    ``compact`` is the ``release/changeset-n`` form (e.g. ``2020.10.19/2020.09.22-1``)
    the goerwitz page's “UXLC change” links use, expanded by the shared
    ``rtms_report`` helper so the URL form stays single-sourced."""
    changeset_n = compact.partition("/")[2]
    return H.anchor(changeset_n, {"href": rtms_report._expand_uxlc_change_ref(compact)})
