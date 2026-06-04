from __future__ import annotations

from accgram.research_tms_assessment_materialize import (
    order_assessment_dict,
    should_materialize_missing_assessment_key,
)
from accgram.troublemaker_structured_text_sanity import descriptor_from_hebrew_token

_ASSESSMENT_AUTO_METEG_FALLBACK_BY_KEY = {
    "wlc": "silluq-no_sof_pasuq",
    "uxlc": "silluq-no_sof_pasuq",
    "mam": "silluq-sof_pasuq",
    "manuscript": "meteg-space",
    "bhs": "silluq-no_sof_pasuq",
}

_HEBREW_MAQAF = "\u05be"
_HEBREW_PASEQ = "\u05c0"
_HEBREW_SOF_PASUQ = "\u05c3"
_HEBREW_METEG = "\u05bd"
_HEBREW_ACCENT_START = ord("\u0591")
_HEBREW_ACCENT_END = ord("\u05af")


def materialize_auto_assessment_descriptors(
    *,
    ref: str,
    structured_text: dict[str, object],
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> dict[str, object]:
    assessment = structured_text.get("assessment")
    if not isinstance(assessment, dict):
        return structured_text

    out_assessment = dict(assessment)
    changed = False

    for key, value in assessment.items():
        if not value == "%auto%":
            continue

        if key == "manuscript":
            raise ValueError(
                "structured_text assessment.manuscript must be explicit "
                f"for {ref}; %auto% is not allowed"
            )

        descriptor = _auto_assessment_descriptor_for_key(
            assessment_key=key,
            enriched_row=enriched_row,
            wlc_focus=wlc_focus,
        )
        if not isinstance(descriptor, str) or not descriptor.strip():
            raise ValueError(
                "Could not auto-generate structured_text assessment descriptor "
                f"for {ref}: assessment.{key}"
            )

        out_assessment[key] = descriptor
        changed = True

    # Backward-compatible behavior after removing explicit "%auto%" entries
    # from structured_text data: if an assessment key is absent but its
    # corresponding diff side is present, infer the descriptor implicitly.
    for key in ("wlc", "uxlc", "mam"):
        if key in out_assessment:
            continue
        if not should_materialize_missing_assessment_key(
            assessment_key=key,
            enriched_row=enriched_row,
            wlc_focus=wlc_focus,
            diff_rhs_tokens=_diff_rhs_tokens_for_materialization,
            infer_assessment_descriptor=_infer_assessment_descriptor_for_materialization,
            meteg_fallback_by_key=_ASSESSMENT_AUTO_METEG_FALLBACK_BY_KEY,
        ):
            continue

        descriptor = _auto_assessment_descriptor_for_key(
            assessment_key=key,
            enriched_row=enriched_row,
            wlc_focus=wlc_focus,
        )
        if not isinstance(descriptor, str) or not descriptor.strip():
            continue

        out_assessment[key] = descriptor
        changed = True

    if not changed:
        return structured_text

    out_assessment = order_assessment_dict(out_assessment)

    out_structured_text = dict(structured_text)
    out_structured_text["assessment"] = out_assessment
    return out_structured_text


def try_auto_assessment_descriptor(
    *,
    assessment_key: str,
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> str | None:
    if assessment_key == "manuscript":
        return None

    descriptor = _auto_assessment_descriptor_for_key(
        assessment_key=assessment_key,
        enriched_row=enriched_row,
        wlc_focus=wlc_focus,
    )
    if not isinstance(descriptor, str) or not descriptor.strip():
        return None
    return descriptor


def _auto_assessment_descriptor_for_key(
    *,
    assessment_key: str,
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> str | None:
    meteg_fallback = _ASSESSMENT_AUTO_METEG_FALLBACK_BY_KEY.get(
        assessment_key,
        "silluq-no_sof_pasuq",
    )

    for hebrew_token in _candidate_tokens_for_auto_assessment(
        assessment_key=assessment_key,
        enriched_row=enriched_row,
        wlc_focus=wlc_focus,
    ):
        descriptor = _infer_assessment_descriptor_from_hebrew_token(
            hebrew_token,
            meteg_fallback=meteg_fallback,
        )
        if isinstance(descriptor, str) and descriptor.strip():
            return descriptor

    return None


def _candidate_tokens_for_auto_assessment(
    *,
    assessment_key: str,
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> list[str]:
    tokens: list[str] = []

    if assessment_key in {"wlc", "bhs"}:
        tokens.extend(_diff_rhs_tokens(enriched_row.get("diff_wlc_uxlc"), rhs_key="wlc422"))
        tokens.extend(_diff_rhs_tokens(enriched_row.get("diff_wlc_mam"), rhs_key="wlc422"))
        if isinstance(wlc_focus, str):
            tokens.append(wlc_focus)

    if assessment_key == "uxlc":
        tokens.extend(_diff_rhs_tokens(enriched_row.get("diff_wlc_uxlc"), rhs_key="uxlc"))
        if isinstance(wlc_focus, str):
            tokens.append(wlc_focus)

    if assessment_key == "mam":
        tokens.extend(
            _diff_rhs_tokens(enriched_row.get("diff_wlc_mam"), rhs_key="mam_simple")
        )
        if isinstance(wlc_focus, str):
            tokens.append(wlc_focus)

    return _unique_nonempty_strings(tokens)


def _diff_rhs_tokens_for_materialization(diff_value: object, rhs_key: str) -> list[str]:
    return _diff_rhs_tokens(diff_value, rhs_key=rhs_key)


def _infer_assessment_descriptor_for_materialization(
    hebrew_token: str,
    meteg_fallback: str,
) -> str | None:
    return _infer_assessment_descriptor_from_hebrew_token(
        hebrew_token,
        meteg_fallback=meteg_fallback,
    )


def _diff_rhs_tokens(diff_value: object, *, rhs_key: str) -> list[str]:
    if isinstance(diff_value, list):
        out_tokens: list[str] = []
        for item in diff_value:
            out_tokens.extend(_diff_rhs_tokens(item, rhs_key=rhs_key))
        return out_tokens

    if not isinstance(diff_value, dict):
        return []

    if rhs_key not in diff_value:
        return []

    return _texts_from_token_like_payload(diff_value.get(rhs_key))


def _texts_from_token_like_payload(payload: object) -> list[str]:
    if isinstance(payload, str):
        return [payload]

    if isinstance(payload, list):
        out: list[str] = []
        for item in payload:
            out.extend(_texts_from_token_like_payload(item))
        return out

    if isinstance(payload, dict):
        text = payload.get("text")
        if isinstance(text, str):
            return [text]

        word = payload.get("word")
        if isinstance(word, str):
            return [word]

    return []


def _unique_nonempty_strings(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()

    for value in values:
        collapsed = " ".join(value.split())
        if not collapsed or collapsed in seen:
            continue
        seen.add(collapsed)
        out.append(collapsed)

    return out


def _infer_assessment_descriptor_from_hebrew_token(
    hebrew_token: str,
    *,
    meteg_fallback: str = "silluq-no_sof_pasuq",
) -> str | None:
    token = hebrew_token.strip()
    if not token:
        return None

    # Preserve the existing project convention for this well-known edge case.
    if token == "\u05d3\u05d9":
        return "meteg-space"

    # Silluq heuristics apply only when meteg (U+05BD) is present. A trailing
    # sof pasuq/paseq punctuation mark alone must not override the token's
    # accent descriptor.
    if _HEBREW_METEG in token and _HEBREW_SOF_PASUQ in token:
        return "silluq-sof_pasuq"
    if _HEBREW_METEG in token and _HEBREW_PASEQ in token:
        return "silluq-pasoleg"
    if _HEBREW_METEG in token and _HEBREW_MAQAF in token:
        return "meteg-maqaf"
    if _HEBREW_METEG in token:
        return meteg_fallback

    try:
        descriptor = descriptor_from_hebrew_token(token)
    except (AssertionError, ValueError):
        descriptor = None

    if descriptor == "no_accent":
        return "no accent"
    if descriptor == "maqaf":
        return "meteg-maqaf"
    if isinstance(descriptor, str) and descriptor:
        if _HEBREW_SOF_PASUQ in token:
            return f"{descriptor}-sof_pasuq"
        return descriptor
    # Do not force a maqaf fallback when other accent marks are present but
    # unmapped; in those cases the descriptor is ambiguous for SAT rendering.
    if _HEBREW_MAQAF in token and not any(
        _HEBREW_ACCENT_START <= ord(ch) <= _HEBREW_ACCENT_END for ch in token
    ):
        return "meteg-maqaf"

    return None
