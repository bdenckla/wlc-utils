from __future__ import annotations

from collections.abc import Callable

_ASSESSMENT_OUTPUT_KEY_ORDER = ("manuscript", "bhs", "wlc", "uxlc", "mam")


def should_materialize_missing_assessment_key(
    *,
    assessment_key: str,
    enriched_row: dict[str, object],
    wlc_focus: str | None,
    diff_rhs_tokens: Callable[[object, str], list[str]],
    infer_assessment_descriptor: Callable[[str, str], str | None],
    meteg_fallback_by_key: dict[str, str],
) -> bool:
    if assessment_key in {"wlc", "bhs"}:
        return bool(
            diff_rhs_tokens(enriched_row.get("diff_wlc_uxlc"), "wlc422")
            or diff_rhs_tokens(enriched_row.get("diff_wlc_mam"), "wlc422")
        )

    if assessment_key == "uxlc":
        if diff_rhs_tokens(enriched_row.get("diff_wlc_uxlc"), "uxlc"):
            return True

        if not isinstance(wlc_focus, str) or not wlc_focus.strip():
            return False

        focus_descriptor = infer_assessment_descriptor(
            wlc_focus,
            meteg_fallback_by_key.get("uxlc", "silluq-no_sof_pasuq"),
        )
        return focus_descriptor in {"silluq-no_sof_pasuq", "silluq-pasoleg"}

    if assessment_key == "mam":
        return bool(diff_rhs_tokens(enriched_row.get("diff_wlc_mam"), "mam_simple"))

    return False


def order_assessment_dict(
    assessment: dict[str, object],
) -> dict[str, object]:
    ordered: dict[str, object] = {}

    for key in _ASSESSMENT_OUTPUT_KEY_ORDER:
        if key in assessment:
            ordered[key] = assessment[key]

    for key, value in assessment.items():
        if key not in ordered:
            ordered[key] = value

    return ordered
