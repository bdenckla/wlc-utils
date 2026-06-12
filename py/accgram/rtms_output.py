from __future__ import annotations

import json
from pathlib import Path

from accgram import rtms_meteg_witness
from accgram import rtmsr_overview
from mb_cmn import provenance


def write_oddballs_payload(
    *,
    oddballs_out_path: Path,
    oddballs_in_path: Path,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    enriched_oddball_rows: list[dict[str, object]],
    source_file: str,
) -> None:
    serializable_rows = rtms_meteg_witness.strip_internal_witness_fields_from_rows(
        enriched_oddball_rows
    )
    oddballs_payload: dict[str, object] = {
        "artifacts_description": "enriched oddball verse research records",
        "payload_provenance_note": (
            "This artifact augments existing oddball rows with linked verse payloads "
            "from wlc422-kq-u, XML-ish UXLC verse nodes, and normalized MAM-simple verses."
        ),
        "input": str(oddballs_in_path),
        "wlc422_kq_u_dir": str(wlc422_kq_u_dir),
        "uxlc_dir": str(uxlc_dir),
        "mam_simple_dir": str(mam_simple_dir),
        "summary": {
            "oddballs": len(serializable_rows),
        },
        "oddballs": serializable_rows,
    }
    oddballs_payload = provenance.with_json_provenance(oddballs_payload, source_file)
    _write_json(oddballs_out_path, oddballs_payload)


def write_html_reports(
    html_out_path: Path,
    *,
    enriched_oddball_rows: list[dict[str, object]],
    base_dir: Path | None = None,
) -> Path:
    # The page (rtmsr_overview) sorts its rows into reading order itself, so no
    # per-list sort is needed here.
    return rtmsr_overview.write_goerwitz_combined_html_report(
        html_out_path,
        enriched_oddball_rows,
        base_dir,
    )


def print_run_summary(
    *,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    all_changes_path: Path,
    combined_html_out_path: Path,
    oddballs_in_path: Path,
    oddballs_out_path: Path,
    oddball_rows_count: int,
) -> None:
    print(f"wlc422-kq-u dir: {wlc422_kq_u_dir}")
    print(f"UXLC dir: {uxlc_dir}")
    print(f"MAM-simple dir: {mam_simple_dir}")
    print(f"All changes: {all_changes_path}")
    print(f"Input oddballs: {oddballs_in_path}")
    print(f"Oddballs output: {oddballs_out_path}")
    print(f"Oddball rows: {oddball_rows_count}")
    print(f"Combined HTML output: {combined_html_out_path}")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
