"""Per-troublemaker structured research notes used by research-tms output."""

from __future__ import annotations


def _non_revia_comment(fp_value: str, extra=()):
    return (
        (
            "This verse probably causes trouble for the Goerwitz accent grammar because "
            f"is has a phrase that is a member of the FOI category “{fp_value}”. "
        ),
        (
            "This verse is one of 5 troublemakers whose FOI category starts "
            "with “⅃-leg...non-revia”. Mysteriously, there are 12 abother such verses that do not cause trouble."
        ),
        (
            " It remains to be investigated whether those other 12,"
            " despite not causing trouble,"
            " are considered ungrammatical,"
            " i.e. report the string “ERROR”."
        ),
        *extra,
    )


def _non_revia_summary(accent: str) -> str:
    return f"The checker probably doesn’t like munax legarmeih serving {accent}."


def _ambiguous_mark_context_comment(marked_word: str) -> str:
    return (
        "In the LC, inclination does not reliably identify a mark as a merkha, a tipexa, or a meteg."
        " Yet, from context, we can usually determine the most likely intended meaning,"
        f" and that is the case here with {marked_word}."
    )


def _je_0910_and_11_comment(adjacent_verse_phrase: str):
    return (
        [
            f"The same word, מבלי, appears in the {adjacent_verse_phrase} with analogous transcription problems."
        ],
        [_ambiguous_mark_context_comment("מבלי")],
        [
            " It is aggressively uncharitable to transcribe the mark on מבלי as tipexa:"
            " tipexa is the least likely of the three possible meanings of this mark."
            " Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably"
            " assume that a maqaf is missing."
        ],
    )


_NU_2509_01 = (
    "Compared to MAM, BHS starts chapter 26 “late”."
    " It only starts chapter 26 after the etnaxta of what MAM calls 26:1."
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
_LM_0505_01 = (
    "The consensus pointing of the last two atoms in this verse is הֽוּנַֽח־לָֽנוּ׃."
    " I.e. ignoring vowel marks, the consensus for the atom in question is הֽונֽח־, i.e. two meteg marks and a maqaf."
)
_LM_0505_02 = (
    "Given this consensus, the most charitable transcription of the LC here is that it is missing the maqaf,"
    " leaving הונח with no accent, only two meteg marks."
    " Even ignoring the consensus, i.e. transcribing “blind,” this is the most charitable transcription."
)
_LM_0505_03 = (
    "Nonetheless, BHQ opts to make הונח “locally legal” by giving it an accent."
    " It gives it an accent by transcribing the second mark"
    " as a second tipexa rather than as a meteg. WLC follows BHQ in this, as it explicitly notes with a bracket-Q note."
    " (Hover over the letters of the bracket notes above to decode them.)"
)
_LM_0505_04 = (
    "This makes the word הונח locally legal while rendering the second half of the verse illegal"
    " by giving the silluq segment two words accented with tipexa."
    " (This (short) verse has no etnaxta segment.)"
)
_LM_0505_05 = (
    "It is uncharitable to transcribe this mark as a tipexa."
    " Most likely what happened here is that the scribe forgot to add a maqaf."
    " It is far less likely that the scribe intended to add a second tipexa,"
    " and a second merkha seems equally implausible."
)
_TIP_LIKE_INCL = "The slightly northwest-to-southeast (tipexa-like) inclination of the mark in question is, while not irrelevant, hardly definitive."
_LM_0505_06 = _TIP_LIKE_INCL
_LM_0505_07 = (
    "Side note: there also seems to be some question of whether the נ in הונח should have a dagesh."
    " BHQ claims that manuscripts L34 and Y (in its sigil vocabulary) have this dagesh."
    " Breuer (in Da-at Miqra) claims that Minxat Shai asserts this dagesh."
)
_NU_2019_01 = (
    "This is one of 12 cases involving zarqa on lamed in which WLC made not only poor decisions but also outright errors."
    " I would have expected all 12 cases to cause trouble for the Goerwitz checker, but this one is the only one that does."
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
_JU_1318_01 = (
    "Color images make it clearer that the mark in question is a speck on the LC vellum rather than a tevir dot made of ink."
    " See the image in the UXLC note to which we link above."
)
_JU_1318_02 = (
    "Even if the editors of BHQ Judges (2011) lacked access to color images,"
    " this was an overly-literal, aggressively uncharitable transcription."
    " Even without color, they should have been aware that this could be"
    " a non-ink speck on the LC vellum or a non-intentional ink dot."
    " They should have found one of these possibilities more likely than a verse-final tevir."
    " A verse-final tevir is rather far-fetched."
)
_JU_1318_03 = (
    "Are they attempting to use typography to create a pseudo-photographic image of the LC,"
    " or are they trying to transcribe the LC “meaningfully,”"
    " using some degree of interpretation to determine the most likely intended meaning of each mark?"
    " (Sometimes, as is the case here, the most likely intended meaning of a mark is no meaning at all!)"
)
_JE_1003_01 = (
    "As in many other cases we see in this document,"
    " BHS seems to be aggresively uncharitable in its transcription of this somewhat-ambiguous vertical line,"
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
    " for example due to ambiguity between merkha and tipexa."
    " I don’t think that is the case here, but I thought I would bring up the general point anyway."
)
_JE_1003_03 = "Finally, it should be noted that the mark preceding this word’s yod is assumed to be a spacer."
STRUCTURED_TEXT_BY_REF: dict[str, dict[str, object]] = {
    "1k 6:2": {
        "st-summary": "Defying the LC, BHS has mahapakh rather than munax.",
        "wlc_focus": "ועשר֤ים",
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "1k 16:33": {
        "st-summary": "BHS’s qadma matches neither the LC nor the consensus.",
        "wlc_focus": "מכ֨ל",
        "assessment": {
            "wlc": "qadma on kaf",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-23",
        "comment": (
            "The LC has no visible accent on מכל. See the image in the UXLC change to which we link above."
            " The consensus accents the final syllable with pashta rather than qadma."
        ),
    },
    "1k 19:11": {
        "wlc_focus": "הר֨וח",
        "assessment": {
            "mam": "pashta stress helper on resh-pashta on ḥet",
        },
    },
    "1k 20:29": {
        "wlc_focus": "נ֥כח",
        "assessment": {
            "manuscript": "meteg-maqaf",
            "wlc": "merkha-space",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-32",
        "comment": [
            "I am not sure what, if anything is “wrong” about merkha-space."
            " Indeed see the MAM doc-note for a list of some of the sources that have merkha-space."
            " Maybe that is not even what the Goerwitz checker is flagging as wrong."
            " The overall sequence involves merkha kefula; I wonder whether, because it is so rare, we lack a good sense of"
            " the “legality” of sequences involving it."
            " The sequence in question is darga, merkha kefula, something on נכח (the atom in question), and then tipexa."
        ],
    },
    "1s 6:19": {
        "wlc_focus": "גדולֽה",
    },
    "2c 22:12": {
        "st-summary": "Defying the LC, BHS has tipexa rather than etnaxta.",
        "wlc_focus": "שנ֖ים",
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-12",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "is 36:2": {
        "st-summary": _non_revia_summary("tevir"),
        "wlc_focus": "ירושל֛מה",
        "comment": _non_revia_comment(
            "⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening",
            ["This verse has a munax vs merkha issue that may be significant."]
        ),
    },
    "je 4:19": {
        "st-summary": _non_revia_summary("geresh"),
        "wlc_focus": "אוח֜ילה",
        "comment": _non_revia_comment("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "je 38:11": {
        "st-summary": _non_revia_summary("geresh"),
        "wlc_focus": "את־ האנש֜ים",
        "comment": _non_revia_comment("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "hg 2:12": {
        "st-summary": _non_revia_summary("geresh"),
        "wlc_focus": "בשר־ ק֜דש",
        "BHQ": "?",
        "comment": _non_revia_comment("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2c 26:15": {
        "st-summary": _non_revia_summary("geresh"),
        "wlc_focus": "חשבנ֜ות",
        "comment": _non_revia_comment("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2k 23:36": {
        "st-summary": "Defying the LC, BHS accents a syllable with qadma rather than pashta.",
        "wlc_focus": "שנ֨ה",
        "assessment": {
            "wlc": "qadma on נ",
            "uxlc": "pashta on ה",
            "mam": "pashta on ה",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.09.01-24",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "am 1:14": {
        "wlc_focus": "סופֽה",
        "BHQ": "?",
    },
    "am 6:6": {
        "wlc_focus": "יוסֽף",
        "BHQ": "?",
    },
    "am 9:5": {
        "wlc_focus": "מצרֽים",
        "BHQ": "?",
    },
    "da 2:41": {
        "wlc_focus": "ד֥י",
        "assessment": {
            "manuscript": "meteg-space",
            "wlc": "merkha-space",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.12-3",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "dt 9:20": {
        "wlc_focus": "ההֽוא",
        "BHQ": "?",
    },
    "dt 13:15": {
        "wlc_focus": "וחקרת֧",
        "BHQ": "?",
    },
    "dt 25:9": {
        "wlc_focus": "אחֽיו",
        "BHQ": "?",
    },
    "ek 33:20": {
        "wlc_focus": "ישראֽל",
    },
    "ex 2:5": {
        "wlc_focus": "ותקחֽה",
    },
    "ex 14:25": {
        "wlc_focus": "במצרֽים",
    },
    "ex 14:29": {
        "wlc_focus": "ומשמאלֽם",
    },
    "ho 4:19": {
        "wlc_focus": "מזבחותֽם",
        "BHQ": "?",
    },
    "ho 8:9": {
        "wlc_focus": "אהבֽים",
        "BHQ": "?",
    },
    "lv 18:17": {
        "wlc_focus": "הֽוא",
        "BHQ": "?",
    },
    "lv 19:1": {
        "wlc_focus": "לאמֽר",
        "BHQ": "?",
    },
    "lv 26:7": {
        "wlc_focus": "לחֽרב",
        "BHQ": "?",
    },
    "nu 7:32": {
        "wlc_focus": "קטֽרת",
    },
    "nu 7:40": {
        "wlc_focus": "לחטֽאת",
    },
    "nu 7:55": {
        "wlc_focus": "למנחֽה",
    },
    "nu 7:68": {
        "wlc_focus": "קטֽרת",
    },
    "ec 7:21": {
        "wlc_focus": "אש֥ר",
        "BHQ": "?",
        "assessment": {
            "manuscript": "tevir",
        },
        "uxlc_change": "https://tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.xml?2023.09.11-18",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "ec 9:18": {
        "wlc_focus": "יאב֥ד טוב֥ה",
        "BHQ": "?",
        "assessment": {
            "manuscript": "merkha tipexa",
        },
        "img": "LC-429A-col-1-line-23-Eccl-9v18.png",
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.10.04-2",
    },
    "ek 11:1": {
        "st-summary": "BHS transcribes a merkha as a tipexa.",
        "wlc_focus": "שר֖י",
        "img": "LC-280B-col-3-line-2-Ezek-11v1.png",
        "comment": (
            _ambiguous_mark_context_comment("שרי")
            + " It is aggressively uncharitable to transcribe the mark on שרי as tipexa:"
            + " tipexa is the least likely of the three possible meanings of this mark."
            + " Merkha is by far the most likely. If the mark were meteg, we would have to"
            + " assume that a maqaf is missing."
        ),
    },
    "ek 14:11": {
        "st-summary": "BHS turns a missing maqaf into something worse.",
        "wlc_focus": "וה֥יו ל֣י",
        "img": "LC-282B-col-2-line-3-Ezek-14v11.png",
        "comment": (
            _ambiguous_mark_context_comment("והיו")
            + " The most likely intended meaning of the mark on והיו is meteg, even though that implies that"
            + " a maqaf is missing."
        ),
    },
    "ex 34:6": {
        "wlc_focus": "ואמֽת׀",
    },
    "je 9:10": {
        "st-summary": "BHS transcribes a merkha as a tipexa.",
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-15",
        "comment": _je_0910_and_11_comment("next verse (11)"),
    },
    "je 9:11": {
        "st-summary": "BHS transcribes a merkha as a tipexa.",
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-16",
        "comment": _je_0910_and_11_comment("previous verse (10)"),
    },
    "je 10:3": {
        "st-summary": "BHS transcribes a meteg as a merkha.",
        "wlc_focus": "יד֥י־",
        "img": "LC-251A-col-3-line-11-Je-10v3.png",
        "comment": (
            _JE_1003_01,
            _JE_1003_02,
            _JE_1003_03,
        ),
    },
    "je 31:32": {
        "st-summary": "Defying the LC, BHS has tipexa rather than munax.",
        "wlc_focus": "מא֖רץ",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-41",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "je 48:12": {
        "st-summary": "BHS transcribes a meteg as a tipexa.",
        "wlc_focus": "הנ֖ה־",
        "img": "LC-272A-col-3-line-3-Je-48v12.png",
        "comment": (
            "Yet another aggressively uncharitable, overly-literal transcription by BHS."
            + " "
            + _TIP_LIKE_INCL
        ),
    },
    "je 49:19": {
        "st-summary": "BHS misses a pashta that is hard to see in the LC.",
        "wlc_focus": "אריצ֨נו",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-60",
        "comment": (
            "See the image in the UXLC change to which we link above."
            " BHS transcribes only the pashta stress helper, not the pashta itself."
            " So, understandably, WLC transcribes this mark as a qadma."
        ),
    },
    "ju 13:18": {
        "st-summary": "BHQ transcribes a silluq as a tevir due to a speck.",
        "wlc_focus": "פ֛לאי׃",
        "uxlc_note_page": "https://tanach.us/Notes/Judges/Judges.13.18.10-t.html",
        "comment": (
            _JU_1318_01,
            _JU_1318_02,
            _JU_1318_03,
        ),
    },
    "lm 5:5": {
        "st-summary": "BHQ turns a missing maqaf into something worse.",
        "wlc_focus": "הונ֖ח",
        "assessment": {
            "mam": "meteg-meteg-maqaf",
        },
        "img": "LC-432A-col-3-line-17-Lam-5v5.png",
        "comment": (
            _LM_0505_01,
            _LM_0505_02,
            _LM_0505_03,
            _LM_0505_04,
            _LM_0505_05,
            _LM_0505_06,
            _LM_0505_07,
        ),
    },
    "mi 2:7": {
        "st-summary": "Defying the LC, BHS accents a syllable with qadma rather than pashta.",
        "wlc_focus": "דבר֨י",
        "BHQ": "?",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.12-10",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "nu 20:19": {
        "st-summary": "WLC turns a scribal zarqa whim into an outright error.",
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-7",
        "comment": (
            _NU_2019_01,
            _NU_2019_02,
            _NU_2019_03,
            _NU_2019_04,
            _NU_2019_05,
            _NU_2019_06,
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
    "ob 1:1": {
        "st-summary": "The LC has no visible accent on עליה.",
        "wlc_focus": "עליה",
        "BHQ": "?",
        "uxlc_note_page": "https://tanach.us/Notes/Obadiah/Obadiah.1.1.17-c.html",
        "comment": "See the image in the UXLC note to which we link above.",
    },
}
