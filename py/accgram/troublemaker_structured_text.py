from __future__ import annotations

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
        "uxlc_change": {
            "label": "UXLC change 2022.08.31-9",
            "url": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
        },
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
        "uxlc_change": {
            "label": "UXLC change 2022.08.31-23",
            "url": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-23",
        },
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
}
