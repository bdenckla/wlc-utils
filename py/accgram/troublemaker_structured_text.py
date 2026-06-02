from __future__ import annotations


def _foi_non_revia_note(fp_value: str) -> str:
    return (
        'A possible reason why the goerwitz accent grammar check deems this verse "ungrammatical" '
        f'is its phrase that is a member of the FOI category "{fp_value}". '
        'A problem with this theory is this verse is one of only 5 of the 17 whose FOI category starts '
        'with "⅃-leg...non-revia" and the other 12 are not deemed "ungrammatical" by the checker.'
    )


# Per-troublemaker structured research notes used by research-tms output.
STRUCTURED_TEXT_BY_REF: dict[str, dict[str, object]] = {
    "1k 6:2": {
        "wlc_focus": "ועשר֤ים",
        "assessment": {
            "manuscript": "munax",
            "wlc": "mahapakh",
            "uxlc": "munax",
            "consensus": "munax"
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
    },
    "1k 16:33": {
        "wlc_focus": "מכ֨ל",
        "assessment": {
            "manuscript": "no accent",
            "wlc": "qadma on kaf",
            "uxlc": "no accent",
            "consensus": "pashta on lamed",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-23",
    },
    "1k 19:11": {
        "wlc_focus": "הר֨וח",
        "assessment": {
            "wlc": "qadma on resh",
            "uxlc": "qadma on resh",
            "consensus": "pashta stress helper on resh, pashta on xet",
        },
        "uxlc_change": None,
    },
    "1k 20:29": {
        "wlc_focus": "נ֥כח",
        "assessment": {
            "manuscript": "meteg-maqaf",
            "wlc": "merkha-space",
            "uxlc": "meteg-maqaf",
            "consensus": "meteg-maqaf, though merkha-space and no_meteg-maqaf are also attested (see MAM doc-note)",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-32",
        "free_form_comment": [
            "I am not sure what, if anything is 'wrong' about merkha-space."
            " Maybe that is not even what the Goerwitz checker is flaging as wrong."
            " The overall sequence involves merkha kefula; I wonder whether, because it is so rare, we lack a good sense of"
            " the 'legality' of sequences involving it."
            " The sequence in question is darga, merkha kefula, something on נכח (the atom in question), and then tipexa."
        ]
    },
    "1s 6:19": {
        "wlc_focus": "גדולֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "2c 22:12": {
        "wlc_focus": "שנ֖ים",
        "assessment": {
            "manuscript": "etnaxta",
            "wlc": "tipexa",
            "uxlc": "etnaxta",
            "consensus": "etnaxta",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-12",
    },
    "is 36:2": {
        "wlc_focus": "ירושל֛מה",
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening"),
    },
    "je 4:19": {
        "wlc_focus": "אוח֜ילה",
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "je 38:11": {
        "wlc_focus": "את־האנש֜ים",
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "hg 2:12": {
        "wlc_focus": "בשר־ק֜דש",
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2c 26:15": {
        "wlc_focus": "חשבנ֜ות",
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2k 23:36": {
        "wlc_focus": "שנ֨ה",
        "assessment": {
            "manuscript": "pashta on ה",
            "wlc": "qadma on נ",
            "uxlc": "pashta on ה",
            "consensus": "pashta on ה",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.09.01-24",
    },
    "am 1:14": {
        "wlc_focus": "סופֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "am 6:6": {
        "wlc_focus": "יוסֽף",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "am 9:5": {
        "wlc_focus": "מצרֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "da 2:41": {
        "wlc_focus": "ד֥י",
        "assessment": {
            "manuscript": "meteg-space",
            "wlc": "merkha-space",
            "uxlc": "meteg-space",
            "consensus": "meteg-maqaf",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.12-3",
    },
    "dt 9:20": {
        "wlc_focus": "ההֽוא",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "dt 13:15": {
        "wlc_focus": "וחקרת֧",
        "assessment": {
            "wlc": "darga",
            "uxlc": "darga",
            "consensus": "tevir",
        },
    },
    "dt 25:9": {
        "wlc_focus": "אחֽיו",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ek 33:20": {
        "wlc_focus": "ישראֽל",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 2:5": {
        "wlc_focus": "ותקחֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 14:25": {
        "wlc_focus": "במצרֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 14:29": {
        "wlc_focus": "ומשמאלֽם",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ho 4:19": {
        "wlc_focus": "מזבחותֽם",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ho 8:9": {
        "wlc_focus": "אהבֽים",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 18:17": {
        "wlc_focus": "הֽוא",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 19:1": {
        "wlc_focus": "לאמֽר",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 26:7": {
        "wlc_focus": "לחֽרב",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:32": {
        "wlc_focus": "קטֽרת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:40": {
        "wlc_focus": "לחטֽאת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:55": {
        "wlc_focus": "למנחֽה",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:68": {
        "wlc_focus": "קטֽרת",
        "assessment": {
            "wlc": "silluq-no_sof_pasuq",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ec 7:21": {
        "wlc_focus": "אש֥ר",
        "assessment": {
            "manuscript": "tevir",
            "wlc": "merkha",
            "uxlc": "tevir",
            "consensus": "tevir",
        },
        "uxlc_change": "https://tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.xml?2023.09.11-18",
    },
    "ec 9:18": {
        "wlc_focus": "יאב֥ד טוב֥ה",
        "assessment": {
            "manuscript": "[merkha] tipexa",
            "wlc": "[merkha] merkha",
            "uxlc": "[merkha] tipexa",
            "consensus": "[tipexa] merkha",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.10.04-2",
    },
    "ek 11:1": {
        "wlc_focus": "שר֖י",
        "img": "LC-280B-col-3-line-2-Ezek-11v1.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F280B.jpg",
        "free_form_comment": (
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with שרי. "
            "To transcribe the mark on שרי as tipexa is an aggressively uncharitable transcription: "
            "tipexa is the least likely of the three possible meanings of this mark. "
            "Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably "
            "assume that a maqaf is missing."
        ),
    },
    "ek 14:11": {
        "wlc_focus": "וה֥יו ל֣י",
        "img": "LC-282B-col-2-line-3-Ezek-14v11.png",
        "img_src_url": "https://manuscripts.sefaria.org/leningrad-color/BIB_LENCDX_F282B.jpg",
        "free_form_comment": (
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
          "consensus": "silluq-sof_pasuq"
        },
    },
    "je 9:10": {
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-15",
        "free_form_comment": (
            "The same word, מבלי, appears in the next verse (11) with analogous transcription problems."
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with מבלי. "
            "To transcribe the mark on מבלי as tipexa is an aggressively uncharitable transcription: "
            "tipexa is the least likely of the three possible meanings of this mark. "
            "Merkha is by far the most likely. If the mark were meteg, we would have to uncharitably "
            "assume that a maqaf is missing."
        ),
    },
    "je 9:11": {
        "wlc_focus": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-16",
        "free_form_comment": (
            "The same word, מבלי, appears in the previous verse (10) with analogous transcription problems."
            "In the LC it is often difficult to tell whether a mark is a merkha, a tipexa, or meteg "
            "because merkha and tipexa often lack an inclination that would distinguish them from meteg. "
            "Yet, from context, we can usually determine the most likely intended meaning, and that is the case here with מבלי. "
            "To transcribe the mark on מבלי as tipexa is an aggressively uncharitable transcription: "
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
        "wlc_focus": "הנ֖ה־",
    },
    "je 49:19": {
        "wlc_focus": "אריצ֨נו",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-60",
    },
    "ju 13:18": {
        "wlc_focus": "פ֛לאי׃",
    },
    "lm 5:5": {
        "wlc_focus": "הונ֖ח",
    },
    "mi 2:7": {
        "wlc_focus": "דבר֨י",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.12-10",
    },
    "nu 20:19": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-7",
    },
    "nu 25:19": {
        "wlc_focus": "המגפ֑ה",
    },
    "ob 1:1": {
        "wlc_focus": "עליה",
    },
}

