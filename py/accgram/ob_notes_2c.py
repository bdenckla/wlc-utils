"""Oddball structured research notes — 2c."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _BHS_TRANSCRIBES,
)


BY_REF: dict[str, dict[str, object]] = {
    "2c 22:12": {
        "st-summary": "BHS transcribes an etnaḥta as a tipeḥa.",
        "wlc_focus": "שנ֖ים",
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-12",
        "comment": "See the image in the UXLC change to which we link above.",
    },
    "2c 7:5": {
        "wlc_focus": "ז֣בח הבק֗ר",
        "st-summary": "BHS accents a word with munaḥ rather than segol.",
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-3",
        "comment": (
            "MAM has munaḥ segol whereas the LC has segol revia."
        )
    },
    "2c 8:10": {
        "wlc_focus": "שר֤י",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-4",
    },
    "2c 24:27": {
        "wlc_focus": "י֧ר֞ב",
        "st-summary": "BHS adds a gershayim out of nowhere.",
        "img": "LC-357B-col-2-line-6-2C-24v27.png",
        "pending_uxlc_change": "https://tanach.us/Changes/2026.10.19%20-%20Changes/2026.10.19%20-%20Changes.xml?2026.04.10-6",
        "comment": "Perhaps the darga was accidentally repeated from the previous word, which legitimately has a darga.",
    },
    "2c 25:1": {
        "wlc_focus": "ועשר֣ים",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-13",
        "comment": (
            "See the UXLC change image. UXLC corrects WLC but places the mahapakh under the yod, an aggresively uncharitable location for it."
        ),
    },
}
