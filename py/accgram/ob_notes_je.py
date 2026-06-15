"""Oddball structured research notes — je."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    BHS_TRANSCRIBES,
    TIP_LIKE_INCL,
    ambiguous_mark_context_comment,
)


def _je_0910_and_11_comment(adjacent_verse_phrase: str):
    return (
        [
            f"The same word, מבלי, appears in the {adjacent_verse_phrase} with analogous transcription problems."
        ],
        [ambiguous_mark_context_comment("מבלי")],
        [
            " It is aggressively uncharitable to transcribe the mark on מבלי as tipeḥa:"
            " tipeḥa is the least likely of the three possible meanings of this mark."
            " Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably"
            " assume that a maqaf is missing."
        ],
    )


_JE_1003_01 = (
    "As in many other cases we see in this document,"
    " BHS seems to be aggressively uncharitable in its transcription of this somewhat-ambiguous vertical line,"
    " avoiding the most likely intended meaning (here meteg)"
    " in favor of a less likely, indeed “illegal” alternative (here merkha)."
    " In this case the mark even lacks any inclination that would suggest merkha."
)


_JE_1003_02 = (
    "As usual, when we say an accent is “illegal” we mean that it does not conform to the consensus grammar of accents,"
    " given the surrounding accent-context."
    " Thus our degree of certainty that an accent is “illegal”"
    " depends on our degree of certainty about the surrounding accent-context."
    " At times, our degree of certainty about the context is not high,"
    " for example due to ambiguity between merkha and tipeḥa."
    " I don’t think that is the case here, but I thought I would bring up the general point anyway."
)


_JE_1003_03 = "Finally, it should be noted that the mark preceding this word’s yod is assumed to be a spacer."


BY_REF: dict[str, dict[str, object]] = {
    "je 9:10": {
        "st-source": "bhs",
        "st-summary": "BHS transcribes a merkha as a tipeḥa.",
        "wlc_focus": "מבל֖י",
        "uxlc_change": "2023.04.01/2022.12.10-15",
        "comment": _je_0910_and_11_comment("next verse (11)"),
    },
    "je 9:11": {
        "st-source": "bhs",
        "st-summary": "BHS transcribes a merkha as a tipeḥa.",
        "wlc_focus": "מבל֖י",
        "uxlc_change": "2023.04.01/2022.12.10-16",
        "comment": _je_0910_and_11_comment("previous verse (10)"),
    },
    "je 10:3": {
        "st-source": "bhs",
        "st-summary": "BHS transcribes a meteg as a merkha.",
        "wlc_focus": "יד֥י־",
        "img": "LC-251A-col-3-line-11-Je-10v3.png",
        "pending_uxlc_change": "2026.10.19/2026.04.10-8",
        "comment": (
            _JE_1003_01,
            _JE_1003_02,
            _JE_1003_03,
        ),
    },
    "je 31:32": {
        "st-source": "bhs",
        "st-summary": "BHS transcribes a munaḥ as a tipeḥa.",
        "wlc_focus": "מא֖רץ",
        "uxlc_change": "2023.04.01/2022.12.10-41",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "je 48:12": {
        "st-source": "bhs",
        "st-summary": "BHS transcribes a meteg as a tipeḥa.",
        "wlc_focus": "הנ֖ה־",
        "img": "LC-272A-col-3-line-3-Je-48v12.png",
        "comment": (
            "Yet another aggressively uncharitable, overly-literal transcription by BHS."
            + " "
            + TIP_LIKE_INCL
        ),
    },
    "je 49:19": {
        "st-source": "bhs",
        "st-summary": "BHS misses a pashta that is hard to see in the LC.",
        "wlc_focus": "אריצ֨נו",
        "uxlc_change": "2023.04.01/2022.12.10-60",
        "pending_uxlc_change": "2026.10.19/2026.04.10-3",
        "comment": (
            "See the image in the UXLC change to which we link above."
            " BHS transcribes only the pashta stress helper, not the pashta itself."
            " So, understandably, WLC transcribes this mark as a qadma."
        ),
    },
    "je 26:5": {
        "st-source": "bhs",
        "wlc_focus": "דבר֨י",
        "st-summary": "BHS transcribes a syllable as having qadma rather than pashta.",
        "uxlc_change": "2023.04.01/2022.12.10-28",
        "comment": (
            [
                "In BHS, the mark is “late” on the ר, i.e. it is on the left of the ר rather than in its center."
                " If it were really a qadma, we would expect it to be centered on the ר."
            ],
            [
                " Instead, it looks like a stranded pashta stress helper."
                " (Some typography centers a pashta stress helper,"
                " making it indistinguishable from a qadma, but BHS aligns them distinctly.)"
                " I.e. in BHS, the mark looks like a pashta stress helper with no real (end-of-word) pashta to accompany it."
                " (Note that that adding a real pashta to this word would not fix it, since a stress helper on a final syllable makes no sense.)"
            ],
            [
                "So, though above I said “BHS transcribes a syllable as having qadma rather than pashta”,"
                " a more detailed account would be "
                "“BHS transcribes a syllable as having"
                " a stranded pashta stress helper on its first letter rather than a pashta on its last letter,"
                " and WLC transcribes BHS’s stranded stress helper as a qadma.”"
            ],
            [
                "Note that originally WLC had no distinction between a qadma and a pashta stress helper,"
                " using code 63 for both,"
                " but later WLC added a separate code for the pashta stress helper, code 33."
                " So WLC may have had no choice but to transcribe BHS’s stranded stress helper as a qadma,"
                " since it may have had no code for a pashta stress helper at the time."
                " In any case, the serious error is BHS’s transcription, not WLC’s transcription of BHS."
            ],
        ),
    },
    "je 28:2": {
        "st-source": "bhs",
        "wlc_focus": "שב֞רתי",
        "st-summary": BHS_TRANSCRIBES,
        "uxlc_change": "2023.04.01/2022.12.10-35",
    },
    "je 46:4": {
        "st-source": "bhs",
        "wlc_focus": "בכ֥ובע֑ים",
        "st-summary": "BHS transcribes a meteg as a merkha.",
        "img": "LC-271B-col-1-line-5-Je-46v4.png",
        "pending_uxlc_change": "2026.10.19/2026.04.10-9",
    },
    "je 51:9": {
        "st-source": "bhs",
        "wlc_focus": "רפ֣ינו",
        "st-summary": BHS_TRANSCRIBES,
        "pending_uxlc_change": "2026.10.19/2026.04.10-2",
    },
}
