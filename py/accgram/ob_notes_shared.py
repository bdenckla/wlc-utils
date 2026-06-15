"""Cross-book helper constants/functions shared by the ob_notes_* modules."""

from __future__ import annotations


def ambiguous_mark_context_comment(marked_word: str) -> str:
    return (
        "In the LC, inclination does not reliably identify a mark as a merkha, a tipeḥa, or a meteg."
        " Yet, from context, we can usually determine the most likely intended meaning,"
        f" and that is the case here with {marked_word}."
    )


TIP_LIKE_INCL = "The slightly northwest-to-southeast (tipeḥa-like) inclination of the mark in question is, while not irrelevant, hardly definitive."


MISSING_SOF_PASUQ_SUMMARY = (
    "A sof pasuq is missing somewhere in the LC-BHS-WLC pipeline."
)


MISSING_SOF_PASUQ_COMMENT = (
    "Likely the sof pasuq is missing from the start of the pipeline, i.e. from the LC."
)


SOMEWHERE = "Somewhere in the LC-BHS-WLC pipeline, $wlc_focus_desc appears rather than $diff_wlc_mam_desc."


BHS_TRANSCRIBES = "BHS transcribes a $diff_wlc_mam_desc as a $wlc_focus_desc."


ZARQA_WHIM_SUMMARY = "WLC turns a scribal zarqa whim into an outright error."


ZARQA_WHIM = {
    "st-summary": ZARQA_WHIM_SUMMARY,
    "comment": (
        "This is one of twelve items of this type."
        " See nu 20:19 for more discussion of items like this."
    ),
}
