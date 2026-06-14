"""Oddball structured research notes — nu."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _MISSING_SOF_PASUQ_COMMENT,
    _MISSING_SOF_PASUQ_SUMMARY,
    _SOMEWHERE,
    ZARQA_WHIM_SUMMARY,
)


_NU_2509_01 = (
    "Compared to MAM, BHS starts chapter 26 “late”."
    " It only starts chapter 26 after the etnaḥta of what MAM calls 26:1."
    " It labels the first part of what MAM calls 26:1 as 25:19, a verse number that does not exist in MAM."
)


_NU_2509_02 = " In other words, the accent grammar is unexceptional here if we ignore where BHS happens to put its verse labels."


_NU_2509_03 = (
    " MAM is not exceptional in its more cantillation-aware versification here;"
    " above I might have said “many editions” instead of “MAM” but I wanted to be specific."
)


_NU_2509_04 = (
    " As to where BHS got this versification, I suspect it is not original to BHS."
    " This versification’s rather extraordinary mid-chanted-verse verse number does correspond to"
    " a rather extraordinary mid-chanted-verse parashah petuxah break."
    " So, while this verse number is not at the boundary of a chanted verse,"
    " it is at a boundary deemed quite significant in the layout of both cantillated and letter-only Hebrew texts."
)


_NU_2019_01 = (
    "This is one of 12 cases involving zarqa on lamed in which WLC made not only poor decisions but also outright errors."
    " All 12 cases are flagged as oddballs (report “ERROR”), treated uniformly as the lexical (“alphabet”) errors they are,"
    " independent of surrounding context."
)


_NU_2019_02 = (
    "WLC’s first poor decision was to attempt to encode a meaningless scribal whim:"
    " the placement of a zarqa before the lamed ascender rather than after it."
    " See the image in the UXLC change to which we link above."
)


_NU_2019_03 = (
    "WLC’s second poor decision was to characterize this as the correction of a typesetting error in BHS/BHQ."
    " While I am as great a critic of BHS/BHQ as anyone, this is unfair."
    " The treatment of these words in BHS/BHQ is almost certainly an editorial decision,"
    " not an oddly-systematic set of typesetting errors."
)


_NU_2019_04 = (
    "WLC’s third poor decision was to encode this by further overloading the meaning of accent 82,"
    " which is already used as tsinnorit and, rarely, as a stress-helper to accent 02 (zarqa/tsinnor)."
)


_NU_2019_05 = (
    "Finally, WLC greatly compounded these poor decisions by making an outright error in implementation:"
    " the 82 codes are consistently placed preceding rather than following the L (lamed) in question,"
    " in one case by even more than one letter too far back."
)


_NU_2019_06 = (
    "They are consistently placed in a location that would be more appropriate for a tsinnorit or a zarqa stress helper,"
    " namely, on the first letter of the syllable ending in lamed, rather than on the lamed itself."
)


_NU_2019_07 = (
    "This is one of twelve oddballs of this same type,"
    " in which WLC turned a scribal zarqa whim into an outright error."
)


BY_REF: dict[str, dict[str, object]] = {
    "nu 7:32": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "קטֽרת",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "nu 7:40": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "לחטֽאת",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "nu 7:55": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "למנחֽה",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "nu 7:68": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "קטֽרת",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "nu 20:19": {
        "st-summary": ZARQA_WHIM_SUMMARY,
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-7",
        "comment": (
            _NU_2019_01,
            _NU_2019_02,
            _NU_2019_03,
            _NU_2019_04,
            _NU_2019_05,
            _NU_2019_06,
            _NU_2019_07,
        ),
    },
    "nu 25:19": {
        "st-summary": "BHS puts a verse number in the middle of a chanted verse.",
        "wlc_focus": "המגפ֑ה",
        "comment": (
            _NU_2509_01,
            _NU_2509_02,
            _NU_2509_03,
            _NU_2509_04,
        ),
    },
    "nu 27:9": {
        "wlc_focus": "לאחיו׃",
        "st-summary": _SOMEWHERE,
    },
}
