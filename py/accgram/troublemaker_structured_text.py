from __future__ import annotations


def _foi_non_revia_note(fp_value: str) -> str:
    return (
        'A possible reason why the goerwitz accent grammar check deems this verse "ungrammatical" '
        f'is its phrase that is a member of the FOI category "{fp_value}". '
        'A problem with this theory is this verse is one of only 5 of the 17 whose FOI category starts '
        'with "⅃-leg...non-revia" and the other 12 are not deemed "ungrammatical" by the checker.'
    )


# Per-troublemaker structured research notes used by research-tms output.
STRUCTURED_TEXT_BY_REF: dict[tuple[str, int, int], dict[str, object]] = {
    ("1k", 6, 2): {
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
    ("1k", 16, 33): {
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
    ("1k", 19, 11): {
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
    ("1k", 20, 29): {
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
    ("1s", 6, 19): {
        "wlc_word": "גדולֽה",
        "assessment": {
            "manuscript": "silluq-no_sof_pasuq?",
            "bhs": "silluq-no_sof_pasuq?",
            "wlc": "silluq-no_sof_pasuq (with brac-1 note)",
            "uxlc": "silluq-no_sof_pasuq",
            "consensus": "silluq-sof_pasuq",
        },
    },
    ("2c", 22, 12): {
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
    ("is", 36, 2): {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening"),
    },
    ("je", 4, 19): {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    ("je", 38, 11): {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    ("hg", 2, 12): {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
    ("2c", 26, 15): {
        "free_form_comment": _foi_non_revia_note("⅃-leg...non-revia (ge) with 1 qa intervening"),
    },
}
