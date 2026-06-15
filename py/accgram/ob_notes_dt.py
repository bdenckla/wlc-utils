"""Oddball structured research notes — dt."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    MISSING_SOF_PASUQ_COMMENT,
    MISSING_SOF_PASUQ_SUMMARY,
    SOMEWHERE,
    ZARQA_WHIM,
)


BY_REF: dict[str, dict[str, object]] = {
    "dt 9:20": {
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ההֽוא",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 13:15": {
        "st-summary": "The LC has darga where it should have tevir.",
        "wlc_focus": "וחקרת֧",
        "img": "LC-107B-col-3-line-18-dt-13v15.png",
    },
    "dt 25:9": {
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "אחֽיו",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 10:15": {
        "wlc_focus": "הזה׃",
        "st-summary": SOMEWHERE,
    },
    "dt 12:2": {
        "wlc_focus": "רענן׃",
        "st-summary": SOMEWHERE,
    },
    "dt 23:18": {
        "wlc_focus": "ישראל׃",
        "st-summary": SOMEWHERE,
    },
    "dt 24:10": {
        "wlc_focus": "ברעך",
        "st-summary": "The LC has only meteg where meteg-tipeḥa is expected.",
        "img": "LC-113A-col-3-line-27-Dt-24v10.png",
        "comment": (
            [
                "We could also interpret the LC’s mark under the resh as a tipeḥa that comes unexpectedly early in the word."
            ],
            [
                "We could also speculate that what seems to be the long descender of the final kaf"
                " includes a tipeḥa placed too early relative to the kaf."
            ],
            [
                "Yet, just as I have criticized some transcriptions as aggresively uncharitable,"
                " there is no doubt such a thing as a transcription that is too aggressively charitable,"
                " and these suggestions above,"
                " i.e. these ways of saving the word from violating the accent grammar,"
                " may be examples of that."
            ],
            [
                "The most likely explanation is that the LC simply does not have the expected tipeḥa anywhere in the word."
            ]
        ),
    },
    "dt 14:24": {
        "wlc_focus": "תוכ֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-8",
        **ZARQA_WHIM,
    },
    "dt 31:7": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-9",
        **ZARQA_WHIM,
    },
}
