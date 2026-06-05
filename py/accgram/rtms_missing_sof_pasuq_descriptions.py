from __future__ import annotations

from accgram import rtms_focus_diff_expand
from accgram import rtms_generated_descriptions
from accgram.tm_data import get_structured_text

_MISSING_SOF_PASUQ_TOKENS = {
    "silluq-no_sof_pasuq",
    "silluq-pasoleg",
}


def row_is_missing_sof_pasuq_yes(row: dict[str, object]) -> bool:
    ref = row.get("ref")
    structured_text = get_structured_text().get(ref) if isinstance(ref, str) else None
    wlc_focus = rtms_focus_diff_expand.structured_wlc_focus(structured_text)
    for description_key in ("wlc", "uxlc", "mam"):
        description = rtms_generated_descriptions.try_generated_description(
            description_key=description_key,
            enriched_row=row,
            wlc_focus=wlc_focus,
        )
        if description in _MISSING_SOF_PASUQ_TOKENS:
            return True
    return False
