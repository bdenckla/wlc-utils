from __future__ import annotations

# Per-troublemaker structured research notes used by research-tms output.
STRUCTURED_TEXT_BY_REF: dict[tuple[str, int, int], dict[str, object]] = {
    ("1k", 6, 2): {
        "topic": "wlc-vs-uxlc-reading",
        "summary": (
            "UXLC records this as a textual change; manuscript evidence appears clear "
            "here, and WLC is likely in error. The WLC reading may reflect a BHS-side "
            "error, but that should be confirmed."
        ),
        "references": [
            {
                "label": "UXLC change 2022.08.31-9",
                "url": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-9",
            }
        ],
        "assessment": {
            "manuscript": "clear",
            "wlc": "likely_error",
            "possible_source": "possible_bhs_error",
            "verification": "confirm_bhs",
        },
    }
}
