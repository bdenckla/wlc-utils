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


# NOTE: Ps 17:14 (the unique double tsinnor) once had an entry here, but the
# checker now accepts that verse (ply_grammar_poetic.parse_tokens_accepting_repeats
# collapses the repeated divider), so it no longer surfaces as a poetic oddball and
# this layer can no longer render notes for it.  Its manuscript / MAM / Breuer
# discussion, plus the LC and S1 images, now live on the hand-authored page
# gh-pages/accgram/ps17v14-double-tsinnor.html.
BY_REF: dict[str, dict[str, object]] = {
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
