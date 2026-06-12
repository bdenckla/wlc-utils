"""Oddball structured research notes — lv."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _MISSING_SOF_PASUQ_COMMENT,
    _MISSING_SOF_PASUQ_SUMMARY,
    _SOMEWHERE,
    _ZARQA_WHIM,
)


BY_REF: dict[str, dict[str, object]] = {
    "lv 18:17": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "הֽוא",
        "BHQ": "?",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "lv 19:1": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "לאמֽר",
        "BHQ": "?",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "lv 26:7": {
        "st-summary": _MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "לחֽרב",
        "BHQ": "?",
        "comment": _MISSING_SOF_PASUQ_COMMENT,
    },
    "lv 4:2": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-5",
        **_ZARQA_WHIM,
    },
    "lv 25:20": {
        "wlc_focus": "נאכ֤֖ל",
        "st-summary": "The LC has a mahapakh in addition to the expected tipeḥa.",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.22-2",
    },
    "lv 26:28": {
        "wlc_focus": "חטאתיכם׃",
        "st-summary": _SOMEWHERE,
    },
}
