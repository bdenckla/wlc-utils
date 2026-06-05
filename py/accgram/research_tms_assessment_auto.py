from __future__ import annotations

from accgram import research_tms_meteg_witness
from accgram.research_tms_assessment_materialize import (
    order_assessment_dict,
    should_materialize_missing_assessment_key,
)
from accgram.research_tms_token_like import texts_from_token_like_payload
from accgram.troublemaker_structured_text_sanity import descriptor_from_hebrew_token

_ASSESSMENT_AUTO_METEG_FALLBACK_BY_KEY = {
    "wlc": "silluq-no_sof_pasuq",
    "uxlc": "silluq-no_sof_pasuq",
    "mam": "silluq-sof_pasuq",
    "manuscript": "silluq-no_sof_pasuq",
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
    structured_text: dict[str, object],
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> dict[str, object]:
    assessment = structured_text.get("assessment", {})
    assert isinstance(assessment, dict)

    out_assessment = dict(assessment)
    changed = False

    # If an assessment key is absent but its corresponding diff side is
    # present, infer the descriptor implicitly.
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

    for hebrew_token, witness_token in _candidate_tokens_for_auto_assessment(
        assessment_key=assessment_key,
        enriched_row=enriched_row,
        wlc_focus=wlc_focus,
    ):
        descriptor = _infer_assessment_descriptor_from_hebrew_token(
            hebrew_token,
            meteg_fallback=meteg_fallback,
            witness_hebrew_token=witness_token,
        )
        if isinstance(descriptor, str) and descriptor.strip():
            return descriptor

    return None


def _candidate_tokens_for_auto_assessment(
    *,
    assessment_key: str,
    enriched_row: dict[str, object],
    wlc_focus: str | None,
) -> list[tuple[str, str | None]]:
    candidates: list[tuple[str, str | None]] = []

    wlc_witness_payload = research_tms_meteg_witness.witness_payload_for_side(
        enriched_row,
        side_key="wlc422",
    )

    if assessment_key in {"wlc", "bhs"}:
        candidates.extend(
            _candidate_tokens_from_diff_side(
                diff_value=enriched_row.get("diff_wlc_uxlc"),
                rhs_key="wlc422",
                source_witness_payload=wlc_witness_payload,
            )
        )
        candidates.extend(
            _candidate_tokens_from_diff_side(
                diff_value=enriched_row.get("diff_wlc_mam"),
                rhs_key="wlc422",
                source_witness_payload=wlc_witness_payload,
            )
        )
        if isinstance(wlc_focus, str):
            candidates.append(
                _candidate_with_optional_witness(
                    hebrew_token=wlc_focus,
                    source_witness_payload=wlc_witness_payload,
                )
            )

    if assessment_key == "uxlc":
        uxlc_witness_payload = research_tms_meteg_witness.witness_payload_for_side(
            enriched_row,
            side_key="uxlc",
        )
        candidates.extend(
            _candidate_tokens_from_diff_side(
                diff_value=enriched_row.get("diff_wlc_uxlc"),
                rhs_key="uxlc",
                source_witness_payload=uxlc_witness_payload,
            )
        )
        if isinstance(wlc_focus, str):
            candidates.append(
                _candidate_with_optional_witness(
                    hebrew_token=wlc_focus,
                    source_witness_payload=wlc_witness_payload,
                )
            )

    if assessment_key == "mam":
        mam_witness_payload = research_tms_meteg_witness.witness_payload_for_side(
            enriched_row,
            side_key="mam_simple",
        )
        candidates.extend(
            _candidate_tokens_from_diff_side(
                diff_value=enriched_row.get("diff_wlc_mam"),
                rhs_key="mam_simple",
                source_witness_payload=mam_witness_payload,
            )
        )
        if isinstance(wlc_focus, str):
            candidates.append(
                _candidate_with_optional_witness(
                    hebrew_token=wlc_focus,
                    source_witness_payload=wlc_witness_payload,
                )
            )

    return _unique_candidate_tokens(candidates)


def _candidate_tokens_from_diff_side(
    *,
    diff_value: object,
    rhs_key: str,
    source_witness_payload: object,
) -> list[tuple[str, str | None]]:
    return [
        _candidate_with_optional_witness(
            hebrew_token=token,
            source_witness_payload=source_witness_payload,
        )
        for token in _diff_rhs_tokens(diff_value, rhs_key=rhs_key)
    ]


def _candidate_with_optional_witness(
    *,
    hebrew_token: str,
    source_witness_payload: object,
) -> tuple[str, str | None]:
    collapsed_token = " ".join(hebrew_token.split())
    if not collapsed_token:
        return "", None

    witness_token: str | None = None
    if source_witness_payload is not None:
        witness_token = research_tms_meteg_witness.match_unique_witness_token(
            sanitized_token=collapsed_token,
            source_witness_payload=source_witness_payload,
        )
    return collapsed_token, witness_token


def _unique_candidate_tokens(
    values: list[tuple[str, str | None]],
) -> list[tuple[str, str | None]]:
    out: list[tuple[str, str | None]] = []
    seen_idx_by_token: dict[str, int] = {}

    for token, witness in values:
        collapsed_token = " ".join(token.split())
        if not collapsed_token:
            continue

        collapsed_witness = None
        if isinstance(witness, str):
            maybe_witness = " ".join(witness.split())
            if maybe_witness:
                collapsed_witness = maybe_witness

        existing_idx = seen_idx_by_token.get(collapsed_token)
        if existing_idx is None:
            seen_idx_by_token[collapsed_token] = len(out)
            out.append((collapsed_token, collapsed_witness))
            continue

        existing_token, existing_witness = out[existing_idx]
        merged_witness = _merge_candidate_witness(existing_witness, collapsed_witness)
        out[existing_idx] = (existing_token, merged_witness)

    return out


def _merge_candidate_witness(
    existing_witness: str | None,
    incoming_witness: str | None,
) -> str | None:
    if existing_witness is None:
        return incoming_witness
    if incoming_witness is None:
        return existing_witness
    if existing_witness == incoming_witness:
        return existing_witness
    return None


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
    return texts_from_token_like_payload(payload)


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
    witness_hebrew_token: str | None = None,
) -> str | None:
    token = hebrew_token.strip()
    if not token:
        return None

    # Silluq heuristics apply only when meteg (U+05BD) is present. A trailing
    # sof pasuq/paseq punctuation mark alone must not override the token's
    # accent descriptor.
    if _HEBREW_METEG in token and _HEBREW_SOF_PASUQ in token:
        return "silluq-sof_pasuq"
    if _HEBREW_METEG in token and _HEBREW_PASEQ in token:
        return "silluq-pasoleg"
    if _HEBREW_METEG in token and _HEBREW_MAQAF in token:
        return "maqaf"
    if _HEBREW_METEG in token:
        return meteg_fallback

    try:
        descriptor = descriptor_from_hebrew_token(token)
    except (AssertionError, ValueError):
        descriptor = None

    if descriptor == "no_accent":
        normalized_descriptor = "no_accent"
        return _apply_witness_to_normalized_descriptor(
            normalized_descriptor=normalized_descriptor,
            witness_hebrew_token=witness_hebrew_token,
        )
    if descriptor == "maqaf":
        normalized_descriptor = "maqaf"
        return _apply_witness_to_normalized_descriptor(
            normalized_descriptor=normalized_descriptor,
            witness_hebrew_token=witness_hebrew_token,
        )
    if isinstance(descriptor, str) and descriptor:
        if _HEBREW_SOF_PASUQ in token:
            return f"{descriptor}-sof_pasuq"
        return descriptor
    # Do not force a maqaf fallback when other accent marks are present but
    # unmapped; in those cases the descriptor is ambiguous for SAT rendering.
    if _HEBREW_MAQAF in token and not any(
        _HEBREW_ACCENT_START <= ord(ch) <= _HEBREW_ACCENT_END for ch in token
    ):
        return _apply_witness_to_normalized_descriptor(
            normalized_descriptor="maqaf",
            witness_hebrew_token=witness_hebrew_token,
        )

    return None


def _apply_witness_to_normalized_descriptor(
    *,
    normalized_descriptor: str,
    witness_hebrew_token: str | None,
) -> str:
    if normalized_descriptor not in {"no_accent", "maqaf"}:
        return normalized_descriptor

    if not isinstance(witness_hebrew_token, str):
        return normalized_descriptor

    witness_token = witness_hebrew_token.strip()
    if not witness_token or not research_tms_meteg_witness.token_has_meteg(
        witness_token
    ):
        return normalized_descriptor

    if research_tms_meteg_witness.token_has_maqaf(witness_token):
        return "meteg-maqaf"
    return "meteg-space"
