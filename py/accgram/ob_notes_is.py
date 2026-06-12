"""Oddball structured research notes — is."""

from __future__ import annotations

from accgram.ob_notes_shared import (
    _SOMEWHERE,
)


BY_REF: dict[str, dict[str, object]] = {
    "is 36:2": {
        "st-summary": "The legarmeh fires, but its legarmeh_phrase does not reduce.",
        "wlc_focus": "ירושל֛מה",
        "comment": (
            (
                "This verse’s FOI category is “⅃-leg...non-revia ((tev)) with 2"
                " (qa,da) intervening”. Since has_legarmeh now keys on structured"
                " book refs, the munaḥ-legarmeh-not-before-revia mark is read as a"
                " real legarmeh here, as at all 17 listed passages. But unlike the"
                " other 16, Isaiah 36:2’s legarmeh_phrase still reduces to ERROR"
                " (for a reason independent of the legarmeh reading), so it is the"
                " lone remaining oddball of the category."
            ),
            "This verse also has a munaḥ vs merkha issue that may be significant.",
        ),
    },
    "is 13:7": {
        "wlc_focus": "ימס׃",
        "st-summary": _SOMEWHERE,
    },
    "is 45:1": {
        "wlc_focus": "לכ֣ורש",
        "st-summary": "I think the checker wants לכ֣ורש to have a segol.",
        "comment": "There is a question of whether לכ֣ורש should have a legarmeih; see MAM’s doc-note.",
    },
}
