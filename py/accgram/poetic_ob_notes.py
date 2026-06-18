"""Hand-authored structured research notes for poetic oddballs.

The poetic oddball set is small and closed, and most cases need no hand
annotation: the mechanically auto-derived WLC-vs-MAM-simple summary
(``poetic_oddball_summary.derive_tentative_summary``) is the relevant datum.
This module is the optional prose-style annotation layer for the few oddballs
that warrant more — the poetic analogue of the per-book ``ob_notes_*`` modules
the prose ``goerwitz.html`` report consumes via ``ob_notes.get_structured_text``.

Entries are keyed by the two-letter ``bb`` reference form ("jb 31:15") that
``poetic_oddballs._bb_ref`` produces, and may carry the same fields the prose
report understands. The poetic report currently renders:

  * ``st-summary``      -- a hand-authored summary, shown alongside the
    auto-derived one (labelled to distinguish the two).
  * ``comment``         -- review prose; a string, or a list/tuple of items
    (each item a string or a sequence of inline HTML contents) rendered one
    paragraph apiece (see ``rtmsr_media.render_comment_paragraphs``).
  * ``uxlc_note_page``  -- external tanach.us UXLC note URL, linked next to the
    Mwd/UXLC reference links.
  * ``github-issue``    -- external GitHub issue URL, linked likewise.
"""

from __future__ import annotations

from py_html import wlc_utils_html

_JOB_31_15_NOTE_URL = "https://tanach.us/Notes/Job/Job.31.15.1-t.html"

# Sibling, hand-authored (not generated) page next to poetic.html: an English
# rendering of MAM's four documentation notes on this verse.
_PS_17_14_NOTES_HREF = "ps17v14-mam-doc-notes.html"

# Reuse the goerwitz manuscript-image styling so embedded figures match the
# prose page, but caption them vaguely (just the manuscript) rather than with
# the page/column/line detail the prose LC images carry.
_TMS_FIGURE_CLASS = "goerwitz-tms-figure"
_TMS_IMAGE_CLASS = "goerwitz-tms-image"
_TMS_CAPTION_CLASS = "goerwitz-tms-image-caption"


def _vaguely_captioned_image(img_path: str, caption: str) -> object:
    """A manuscript figure captioned only by manuscript -- no page/line/column."""
    image_para = wlc_utils_html.para(
        wlc_utils_html.img({"src": f"../img/{img_path}"}),
        {"class": _TMS_IMAGE_CLASS},
    )
    caption_el = wlc_utils_html.figcaption(caption, {"class": _TMS_CAPTION_CLASS})
    return wlc_utils_html.figure((image_para, caption_el), {"class": _TMS_FIGURE_CLASS})


BY_REF: dict[str, dict[str, object]] = {
    "ps 17:14": {
        "comment": (
            [
                "This verse is heavily commented upon by MAM (see the ",
                wlc_utils_html.anchor(
                    "translation of those notes", {"href": _PS_17_14_NOTES_HREF}
                ),
                "), but the comments either do not concern cantillation, or "
                "concern cantillation only in ways that would not change "
                "whatever the checker's issue is with the accent grammar of the "
                "verse. (The four notes turn on a secondary merkha plus ga'ya, a "
                "ḥataf, a missing shva, and the placement of the silluq -- none "
                "of which alters the disjunctive skeleton the parser rejects, and "
                "the conjunctive servus chain the grammar does parse is "
                "permissive enough that a secondary conjunctive is absorbed "
                "harmlessly.)",
            ],
            "This verse is not extant in the Aleppo Codex.",
            "Though in the LC the first of the two tsinnor marks is a little "
            "oddly shaped, S1 (Sassoon 1053) clearly shares these two adjacent "
            "tsinnor marks, with no questions of penmanship.",
            "A scan of the disjunctive accent stream of every poetic verse "
            "finds that these two adjacent tsinnor marks are unique in the "
            "Three Books: of the 250 poetic verses carrying at least one "
            "tsinnor, Ps 17:14 is the only one in which two tsinnor occur "
            "consecutively. Both arise from genuine Michigan-Claremont 02 "
            "(tsinnor) codes -- not a swallowed 82 (tsinnorit) -- on adjacent "
            "words: בַּחַיִּים and the qere וּצְפוּנְךָ.",
            _vaguely_captioned_image("LC-Ps-17v14.png", "Leningrad Codex"),
            _vaguely_captioned_image("S1-Ps-17v14.png", "Sassoon 1053 (S1)"),
        ),
    },
    "jb 31:15": {
        "uxlc_note_page": _JOB_31_15_NOTE_URL,
        "st-summary": (
            "On the verse-initial word, WLC transcribes a malformed mark — absent "
            "from MAM (and from BHL) — that the UXLC note page (linked above) flags "
            "with a transcription-uncertainty marker."
        ),
        "comment": (
            [
                "The UXLC ",
                wlc_utils_html.anchor("note for this verse", {"href": _JOB_31_15_NOTE_URL}),
                " describes the mark WLC transcribes here as a geresh muqdam of “a "
                "very odd shape,” a vertical straight line arising from the top front "
                "of the he, and flags it with a transcription-uncertainty “t” marker; "
                "BHL lacks the geresh muqdam entirely.",
            ],
            "In my opinion, to transcribe this mark at all is uncharitable. To "
            "continue to transcribe it with the benefit of the high-resolution color "
            "images now available seems not just uncharitable but aggressively "
            "uncharitable, almost absurd.",
        ),
    },
}


def get_structured_text() -> dict[str, dict[str, object]]:
    return BY_REF
