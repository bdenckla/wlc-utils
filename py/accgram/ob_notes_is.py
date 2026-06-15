"""Oddball structured research notes — is."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    SOMEWHERE,
)
from py_html import wlc_utils_html


_FOI_CATEGORY_NAME = "⅃-leg...non-revia ((tev)) with 2 (qa,da) intervening"

_FOI_CATEGORY_URL = (
    "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html"
    "#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB((tev))%C2%ABspace%C2%BB"
    "with%C2%ABspace%C2%BB2%C2%ABspace%C2%BB(qa,da)%C2%ABspace%C2%BBintervening"
)


BY_REF: dict[str, dict[str, object]] = {
    "is 36:2": {
        "st-summary": "The checker does not like munaḥ serving munaḥ legarmeh.",
        "wlc_focus": "וישל֣ח",
        "comment": [
            (
                "This verse is the sole member of the FOI category “",
                wlc_utils_html.anchor(
                    _FOI_CATEGORY_NAME, {"href": _FOI_CATEGORY_URL}
                ),
                "”.",
            ),
        ],
    },
    "is 13:7": {
        "wlc_focus": "ימס׃",
        "st-summary": SOMEWHERE,
    },
    "is 45:1": {
        "wlc_focus": "לכ֣ורש",
        "st-summary": "I think the checker wants לכ֣ורש to have a segol.",
        "comment": "There is a question of whether לכ֣ורש should have a legarmeh; see MAM’s doc-note.",
    },
}
