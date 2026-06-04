"""Per-troublemaker structured research notes used by research-tms output."""

from __future__ import annotations


def _foi_non_revia_note(fp_value: str) -> str:
    return (
        'A possible reason why the Goerwitz accent grammar check deems this verse "ungrammatical" '
        f'is its phrase that is a member of the FOI category "{fp_value}". '
        "A problem with this theory is this verse is one of only 5 of the 17 whose FOI category starts "
        'with "⅃-leg...non-revia" and the other 12 are not deemed "ungrammatical" by the checker.'
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
    " It is far less likely that the scribe intended to add a second tipexa, "
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

STRUCTURED_TEXT_BY_REF: dict[str, dict[str, object]] = {
    "1k 6:2": {
        "wlc_focus": "ועשר֤ים",
        "assessment": {
            "manuscript": "munax",
            "wlc": "mahapakh",
            "uxlc": "munax",
            "mam": "munax",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
    },
    "1k 16:33": {
        "wlc_focus": "מכ֨ל",
        "assessment": {
            "manuscript": "no accent",
            "wlc": "qadma on kaf",
            "uxlc": "no accent",
            "mam": "pashta on lamed",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-23",
    },
    "1k 19:11": {
        "wlc_focus": "הר֨וח",
        "assessment": {
            "wlc": "qadma on resh",
            "mam": "pashta stress helper on resh, pashta on xet",
        },
    },
    "1k 20:29": {
        "wlc_focus": "נ֥כח",
        "assessment": {
            "manuscript": "meteg-maqaf",
            "wlc": "merkha-space",
            "uxlc": "meteg-maqaf",
            "mam": "meteg-maqaf",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-32",
        "comment": [
            "I am not sure what, if anything is 'wrong' about merkha-space."
            " Indeed see the MAM doc-note for a list of some of the sources that have merkha-space."
            " Maybe that is not even what the Goerwitz checker is flagging as wrong."
            " The overall sequence involves merkha kefula; I wonder whether, because it is so rare, we lack a good sense of"
            " the 'legality' of sequences involving it."
            " The sequence in question is darga, merkha kefula, something on נכח (the atom in question), and then tipexa."
        ],
    },
    "1s 6:19": {
        "wlc_focus": "גדולֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "2c 22:12": {
        "wlc_focus": "שנ֖ים",
        "assessment": {
            "manuscript": "etnaxta",
            "wlc": "tipexa",
            "uxlc": "etnaxta",
            "mam": "etnaxta",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-12",
    },
    "is 36:2": {
        "st-summary": "The Goerwitz checker likely does not like munax legarmeih serving tevir.",
        "wlc_focus": "ירושל֛מה",
        "comment": _foi_non_revia_note(
            "⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening"
        ),
    },
    "je 4:19": {
        "st-summary": "The Goerwitz checker likely does not like munax legarmeih serving geresh.",
        "wlc_focus": "אוח֜ילה",
        "comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "je 38:11": {
        "st-summary": "The Goerwitz checker likely does not like munax legarmeih serving geresh.",
        "wlc_focus": "את־האנש֜ים",
        "comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "hg 2:12": {
        "st-summary": "The Goerwitz checker likely does not like munax legarmeih serving geresh.",
        "wlc_focus": "בשר־ק֜דש",
        "comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2c 26:15": {
        "st-summary": "The Goerwitz checker likely does not like munax legarmeih serving geresh.",
        "wlc_focus": "חשבנ֜ות",
        "comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2k 23:36": {
        "wlc_focus": "שנ֨ה",
        "assessment": {
            "manuscript": "pashta on ה",
            "wlc": "qadma on נ",
            "uxlc": "pashta on ה",
            "mam": "pashta on ה",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.09.01-24",
    },
    "am 1:14": {
        "wlc_focus": "סופֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "am 6:6": {
        "wlc_focus": "יוסֽף",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "am 9:5": {
        "wlc_focus": "מצרֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "da 2:41": {
        "wlc_focus": "ד֥י",
        "assessment": {
            "manuscript": "meteg-space",
            "wlc": "merkha-space",
            "uxlc": "meteg-space",
            "mam": "meteg-maqaf",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.12-3",
    },
    "dt 9:20": {
        "wlc_focus": "ההֽוא",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "dt 13:15": {
        "wlc_focus": "וחקרת֧",
        "assessment": {
            "wlc": "darga",
            "uxlc": "darga",
            "mam": "tevir",
        },
    },
    "dt 25:9": {
        "wlc_focus": "אחֽיו",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ek 33:20": {
        "wlc_focus": "ישראֽל",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ex 2:5": {
        "wlc_focus": "ותקחֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ex 14:25": {
        "wlc_focus": "במצרֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ex 14:29": {
        "wlc_focus": "ומשמאלֽם",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ho 4:19": {
        "wlc_focus": "מזבחותֽם",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ho 8:9": {
        "wlc_focus": "אהבֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "lv 18:17": {
        "wlc_focus": "הֽוא",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "lv 19:1": {
        "wlc_focus": "לאמֽר",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "lv 26:7": {
        "wlc_focus": "לחֽרב",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "nu 7:32": {
        "wlc_focus": "קטֽרת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "nu 7:40": {
        "wlc_focus": "לחטֽאת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "nu 7:55": {
        "wlc_focus": "למנחֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "nu 7:68": {
        "wlc_focus": "קטֽרת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "mam": "silluq-sof_pasuq",
        },
    },
    "ec 7:21": {
        "wlc_focus": "אש֥ר",
        "assessment": {
            "manuscript": "tevir",
            "wlc": "merkha",
            "uxlc": "tevir",
            "mam": "tevir",
        },
        "uxlc_change": "https://tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.xml?2023.09.11-18",
    },
    "ec 9:18": {
        "wlc_focus": "יאב֥ד טוב֥ה",
        "assessment": {
            "manuscript": "merkha tipexa",
            "wlc": "merkha merkha",
            "uxlc": "merkha tipexa",
            "mam": "tipexa merkha",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.10.04-2",
    },
    "ek 11:1": {
        "wlc_focus": "שר֖י",
        "img": "LC-280B-col-3-line-2-Ezek-11v1.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F280B.jpg",
        "comment": (
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with שרי. "
            "It is aggressively uncharitable to transcribe the mark on שרי as tipexa: "
            "tipexa is the least likely of the three possible meanings of this mark. "
            "Merkha is by far the most likely. If the mark were meteg, we would have to "
            "assume that a maqaf is missing."
        ),
    },
    "ek 14:11": {
        "wlc_focus": "וה֥יו ל֣י",
        "img": "LC-282B-col-2-line-3-Ezek-14v11.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F282B.jpg",
        "comment": (
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with והיו. "
            "The most likely intended meaning of the mark on והיו is meteg, even though that implies that "
            "a maqaf is missing."
        ),
    },
    "ex 34:6": {
        "wlc_focus": "ואמֽת׀",
        "assessment": {
            "wlc": "silluq-pasoleg",
            "uxlc": "silluq-pasoleg",
            "mam": "silluq-sof_pasuq",
        },
    },
    "je 9:10": {
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-15",
        "comment": (
            "The same word, מבלי, appears in the next verse (11) with analogous transcription problems."
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with מבלי. "
            "It is aggressively uncharitable to transcribe the mark on מבלי as tipexa: "
            "tipexa is the least likely of the three possible meanings of this mark. "
            "Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably "
            "assume that a maqaf is missing."
        ),
    },
    "je 9:11": {
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-16",
        "comment": (
            "The same word, מבלי, appears in the previous verse (10) with analogous transcription problems."
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with מבלי. "
            "It is aggressively uncharitable to transcribe the mark on מבלי as tipexa: "
            "tipexa is the least likely of the three possible meanings of this mark. "
            "Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably "
            "assume that a maqaf is missing."
        ),
    },
    "je 10:3": {
        "wlc_focus": "יד֥י־",
    },
    "je 31:32": {
        "wlc_focus": "מא֖רץ",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-41",
    },
    "je 48:12": {
        "st-summary": "BHS transcribes a meteg as a tipexa.",
        "wlc_focus": "הנ֖ה־",
        "img": "LC-272A-col-3-line-3-Je-48v12.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F272A.jpg",
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
            "See the image in the UXLC note to which we link above."
            " BHS transcribes only the pashta stress helper, not the pashta itself."
            " So, understandably, WLC transcribes this mark as a qadma."
        ),
    },
    "ju 13:18": {
        "st-summary": "BHQ transcribes a silluq as a tevir due to a speck on the LC vellum.",
        "wlc_focus": "פ֛לאי׃",
        "uxlc_note_page": "https://tanach.us/Notes/Judges/Judges.13.18.10-t.html",
        "comment": (
            _JU_1318_01,
            _JU_1318_02,
            _JU_1318_03,
        ),
    },
    "lm 5:5": {
        "st-summary": "LC’s missing maqaf causes BHQ to make things worse.",
        "wlc_focus": "הונ֖ח",
        "img": "LC-432A-col-3-line-17-Lam-5v5.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F432A.jpg",
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
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.12-10",
        "comment": ("See the image in the UXLC change to which we link above."),
    },
    "nu 20:19": {
        "st-summary": "WLC turns a scribal zarqa whim into something far worse.",
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
        "st-summary": "LC has no visible accent on עליה.",
        "wlc_focus": "עליה",
        "uxlc_note_page": "https://tanach.us/Notes/Obadiah/Obadiah.1.1.17-c.html",
        "comment": ("See the image in the UXLC note to which we link above."),
    },
}
