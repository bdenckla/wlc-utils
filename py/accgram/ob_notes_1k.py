"""Oddball structured research notes — 1k."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _BHS_TRANSCRIBES,
)


BY_REF: dict[str, dict[str, object]] = {
    "1k 6:2": {
        "st-summary": "BHS transcribes a munaḥ as a mahapakh.",
        "wlc_focus": "ועשר֤ים",
        "uxlc_change": "2022.12.07/2022.08.31-9",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "1k 16:33": {
        "st-summary": "BHS’s qadma matches neither the LC nor the consensus.",
        "wlc_focus": "מכ֨ל",
        "uxlc_change": "2022.12.07/2022.08.31-23",
        "comment": (
            "The LC has no visible accent on מכל. See the image in the UXLC change to which we link above."
            " The consensus accents the final syllable with pashta rather than qadma."
        ),
    },
    "1k 19:11": {
        "st-summary": "The LC is missing a pashta.",
        "wlc_focus": "הר֨וח",
        "img": "LC-199A-col-3-line-21-1K-19v11.png",
        "comment": "Arguably, WLC and UXLC should code the mark on the resh as a pashta rather than a qadma.",
    },
    "1k 20:29": {
        "st-summary": "BHS transcribes a meteg as a merkha and ignores a maqaf.",
        "wlc_focus": "נ֥כח",
        "uxlc_change": "2022.12.07/2022.08.31-32",
        "comment": (
            ("See the image in the UXLC change to which we link above."),
            (
                "Aside: I am not sure what, if anything, is grammatically “wrong” about a merkha here."
                " Indeed see the MAM doc-note for a list of some of the sources that have merkha."
                " Maybe this merkha is not even what the Goerwitz checker is flagging as wrong."
                " The overall sequence involves merkha kefula;"
                " I wonder whether, because it is so rare, we lack a good sense of"
                " the “legality” of sequences involving it."
                " The sequence in question is"
                " darga, merkha kefula, something on נכח (the atom in question), and then tipeḥa."
            ),
        ),
    },
    "1k 6:3": {
        "wlc_focus": "עשר֣ים",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "2022.12.07/2022.08.31-10",
    },
    "1k 8:11": {
        "wlc_focus": "מפנ֥י",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "2022.04.01/2021.11.21-1",
    },
    "1k 20:25": {
        "wlc_focus": "וס֣וס",
        "st-summary": "The checker may prefer merkha to LC’s munaḥ. Or it may not like either.",
        "img": "LC-200A-col-2-line-19-1K-20v25.png",
        "Aleppo img": "AC-1K-20v25.png",
    },
}
