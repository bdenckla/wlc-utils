"""Oddball structured research notes — dt."""

from __future__ import annotations

from accgram.prose_ob_notes_shared import (
    MISSING_SOF_PASUQ_COMMENT,
    MISSING_SOF_PASUQ_SUMMARY,
    SOMEWHERE,
    ZARQA_WHIM,
)


BY_REF: dict[str, dict[str, object]] = {
    "dt 5:8": {
        # Dual-cantillation detangling (issue #36). dt 5:8 is one of the two-reading
        # Decalogue verses excluded from the normal scan. The anomaly is on the ש of
        # תעשה: in the taḥton (lower) reading that ש is due a qadma (MAM's taḥton
        # reading has one), but WLC carries a merkha there, so the detangled taḥton
        # chanted verse does not parse. More charitably, that single WLC mark is best
        # read as the meteg the elyon (upper) reading attests -- MAM's elyon has a meteg
        # on this ש, which the scanner swallows, which is why the elyon parses cleanly --
        # leaving the taḥton simply lacking its due qadma rather than bearing a wrong
        # merkha. Flagged as a candidate dual-cantillation error; whether the mark
        # originates in LC, BHS, BHQ, or is a WLC reading has not been checked -> tbd.
        # Current UXLC carries a pashta on this word (also an error, again not the due
        # qadma); see the linked UXLC note page (its `-t` te'amim note).
        "st-source": "tbd",
        "wlc_focus": "תעש֥ה־",
        "st-summary": (
            "Dual cantillation (Decalogue): in the taḥton (lower) reading the ש of תעשה"
            " is due a qadma, but WLC carries a merkha there — better read as the meteg"
            " the elyon reading attests, leaving the taḥton with no accent on this word"
            " — so the detangled taḥton chanted verse does not parse. (Current UXLC"
            " instead carries a pashta there: also an error, again not the due qadma —"
            " see the UXLC note page.) Flagged as a candidate dual-cantillation error"
            " (source not yet checked against LC/BHS/BHQ); issue #36."
        ),
        "uxlc_note_page": "https://tanach.us/Notes/Deuteronomy/Deuteronomy.5.8.2-t.html",
    },
    "dt 9:20": {
        "st-source": "tbd",
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ההֽוא",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 13:15": {
        "st-source": "lc",
        "st-summary": "The LC has darga where it should have tevir.",
        "wlc_focus": "וחקרת֧",
        "img": "LC-107B-col-3-line-18-dt-13v15.png",
    },
    "dt 25:9": {
        "st-source": "tbd",
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "אחֽיו",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 10:15": {
        "st-source": "tbd",
        "wlc_focus": "הזה׃",
        "st-summary": SOMEWHERE,
    },
    "dt 12:2": {
        "st-source": "tbd",
        "wlc_focus": "רענן׃",
        "st-summary": SOMEWHERE,
    },
    "dt 23:18": {
        "st-source": "tbd",
        "wlc_focus": "ישראל׃",
        "st-summary": SOMEWHERE,
    },
    "dt 24:10": {
        "st-source": "lc",
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
        "st-source": "wlc",
        "wlc_focus": "תוכ֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-8",
        **ZARQA_WHIM,
    },
    "dt 31:7": {
        "st-source": "wlc",
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-9",
        **ZARQA_WHIM,
    },
}
