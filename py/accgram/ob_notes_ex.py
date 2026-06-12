"""Oddball structured research notes — ex."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _BHS_TRANSCRIBES,
    _MISSING_SOF_PASUQ_COMMENT,
    _MISSING_SOF_PASUQ_SUMMARY,
    _ZARQA_WHIM,
)


_BAR_INSTEAD_OF_SOF_PASUQ_SUMMARY = "In the place where one would expect a sof pasuq, the LC has a vertical bar somewhat like a paseq or legarmeh."


BY_REF: dict[str, dict[str, object]] = {
    "ex 2:5": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ותקחֽה",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "ex 14:25": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "במצרֽים",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "ex 14:29": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ומשמאלֽם",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "ex 34:6": {
        "st-summary": _BAR_INSTEAD_OF_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ואמֽת׀",
        "img": "LC-052A-col-2-line-1-Ex-34v6.png",
    },
    "ex 4:10": {
        "wlc_focus": "דברך",
        "st-summary": "The LC lacks an accent on this word.",
        "uxlc_change": "https://tanach.us/Changes/2021.10.19%20-%20Changes/2021.10.19%20-%20Changes.xml?2021.08.07-4",
    },
    "ex 6:6": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-2",
        **_ZARQA_WHIM,
    },
    "ex 28:1": {
        "wlc_focus": "את֔ו",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2022.04.01%20-%20Changes/2022.04.01%20-%20Changes.xml?2021.11.28-2",
        "comment": ("This is the example given in Goerwitz’s article."),
    },
    "ex 30:12": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-3",
        **_ZARQA_WHIM,
    },
    "ex 38:12": {
        "wlc_focus": "עמודיה֥ם",
        "st-summary": "The LC has something like a merkha where a munaḥ is expected.",
        "img": "LC-055A-col-1-line-3-Ex-38v12.png",
    },
}
