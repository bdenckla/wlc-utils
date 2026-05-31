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
        "wlc_word": "ועשר֤ים",
        "assessment": {
            "manuscript": "munax",
            "bhs": "mahapakh?",
            "wlc": "mahapakh",
            "uxlc": "munax",
            "consensus": "munax"
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
    },
    "1k 16:33": {
        "wlc_word": "מכ֨ל",
        "assessment": {
            "manuscript": "no accent",
            "bhs": "qadma on kaf?",
            "wlc": "qadma on kaf",
            "uxlc": "no accent",
            "consensus": "pashta on lamed",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-23",
    },
    "1k 19:11": {
        "wlc_word": "הר֨וח",
        "assessment": {
            "manuscript": "?",
            "bhs": "qadma on resh?",
            "wlc": "qadma on resh (with brac-1 note)",
            "uxlc": "qadma on resh",
            "consensus": "optional pashta stress helper on resh, required pashta on xet",
        },
        "uxlc_change": None,
    },
    "1k 20:29": {
        "wlc_word": "נ֥כח",
        "assessment": {
            "manuscript": "meteg-maqaf",
            "bhs": "merkha-space?",
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
        "wlc_word": "גדולֽה",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "2c 22:12": {
        "wlc_word": "שנ֖ים",
        "assessment": {
            "manuscript": "etnaxta",
            "bhs": "tipexa?",
            "wlc": "tipexa",
            "uxlc": "etnaxta",
            "consensus": "etnaxta",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-12",
    },
    "is 36:2": {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening"),
    },
    "je 4:19": {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "je 38:11": {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "hg 2:12": {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2c 26:15": {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    "2k 23:36": {
        "wlc_word": "שנ֨ה",
        "assessment": {
            "manuscript": "pashta on ה?",
            "bhs": "qadma on נ?",
            "wlc": "qadma on נ",
            "uxlc": "pashta on ה",
            "consensus": "pashta on ה",
        },
    },
    "am 1:14": {
        "wlc_word": "סופֽה",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "am 6:6": {
        "wlc_word": "יוסֽף",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "am 9:5": {
        "wlc_word": "מצרֽים",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "da 2:41": {
        "wlc_word": "ד֥י",
        "assessment": {
            "manuscript": "meteg-no_maqaf",
            "bhs": "merkha-space?",
            "wlc": "merkha-space",
            "uxlc": "meteg-space",
            "consensus": "meteg-maqaf",
        },
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.12-3",
    },
    "dt 9:20": {
        "wlc_word": "ההֽוא",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "dt 13:15": {
        "wlc_word": "וחקרת֧",
        "assessment": {
            "manuscript": "darga?",
            "bhs": "darga?",
            "wlc": "darga (with brac-U note)",
            "uxlc": "darga",
            "consensus": "tevir",
        },
    },
    "dt 25:9": {
        "wlc_word": "אחֽיו",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ek 33:20": {
        "wlc_word": "ישראֽל",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-p note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 2:5": {
        "wlc_word": "ותקחֽה",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 14:25": {
        "wlc_word": "במצרֽים",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ex 14:29": {
        "wlc_word": "ומשמאלֽם",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ho 4:19": {
        "wlc_word": "מזבחותֽם",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ho 8:9": {
        "wlc_word": "אהבֽים",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-Q, brac-n, and brac-p notes)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 18:17": {
        "wlc_word": "הֽוא",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 19:1": {
        "wlc_word": "לאמֽר",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "lv 26:7": {
        "wlc_word": "לחֽרב",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:32": {
        "wlc_word": "קטֽרת",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:40": {
        "wlc_word": "לחטֽאת",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:55": {
        "wlc_word": "למנחֽה",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "nu 7:68": {
        "wlc_word": "קטֽרת",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    "ec 7:21": {
        "wlc_word": "אש֥ר",
        "assessment": {
            "manuscript": "tevir",
            "bhs": "merkha?",
            "wlc": "merkha",
            "uxlc": "tevir",
            "consensus": "tevir",
        },
        "uxlc_change": "https://tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.xml?2023.09.11-18",
    },
    "ec 9:18": {
        "wlc_word": "טוב֥ה",
        "assessment": {
            "manuscript": "[merkha] tipexa",
            "bhs": "[merkha] merkha?",
            "wlc": "[merkha] merkha",
            "uxlc": "[merkha] tipexa",
            "consensus": "[tipexa] merkha",
        },
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.10.04-2",
    },
    "ek 11:1": {
        "wlc_word": "שר֖י",
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
        "wlc_word": "וה֥יו [ל֣י]",
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
        "wlc_word": "ואמֽת׀",
        "assessment": {
          "manuscript": "silluq-vertical_line?",
          "bhs": "silluq-vertical_line?",
          "wlc": "silluq-pasoleg (with brac-c, brac-n, and brac-p notes)",
          "uxlc": "silluq-pasoleg",
          "consensus": "silluq-sof_pasuq"
        },
    },
    "je 9:10": {
        "wlc_word": "מבל֖י",
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.10.04-2",
        "free_form_comment": (
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
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "je 10:3": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "je 31:32": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "je 48:12": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "je 49:19": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "ju 13:18": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "lm 5:5": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "mi 2:7": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "nu 20:19": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "nu 25:19": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
    "ob 1:1": {
        "TODO_placeholder": "FILL_STRUCTURED_TEXT",
    },
}
