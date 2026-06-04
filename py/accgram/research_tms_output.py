from __future__ import annotations

import json
from pathlib import Path

from accgram import research_tms_report
from accgram.verse_json_smart_concat import smart_concatenate_row_for_json
from mb_cmn import provenance


def write_troublemakers_payload(
    *,
    out_path: Path,
    troubles_in_path: Path,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    enriched_rows: list[dict[str, object]],
    source_file: str,
) -> None:
    payload: dict[str, object] = {
        "artifacts_description": "enriched troublemaker verse research records",
        "payload_provenance_note": (
            "This artifact augments existing troublemaker rows with linked verse payloads "
            "from wlc422-kq-u, XML-ish UXLC verse nodes, and normalized MAM-simple verses."
        ),
        "input": str(troubles_in_path),
        "wlc422_kq_u_dir": str(wlc422_kq_u_dir),
        "uxlc_dir": str(uxlc_dir),
        "mam_simple_dir": str(mam_simple_dir),
        "summary": {
            "troublemakers": len(enriched_rows),
        },
        # Keep diff computation on original tokenized structures, then prettify
        # verse display fields only at serialization time.
        "troublemakers": [smart_concatenate_row_for_json(row) for row in enriched_rows],
    }
    payload = provenance.with_json_provenance(payload, source_file)
    _write_json(out_path, payload)


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
            "oddballs": len(enriched_oddball_rows),
        },
        # Keep diff computation on original tokenized structures, then prettify
        # verse display fields only at serialization time.
        "oddballs": [
            smart_concatenate_row_for_json(row) for row in enriched_oddball_rows
        ],
    }
    oddballs_payload = provenance.with_json_provenance(oddballs_payload, source_file)
    _write_json(oddballs_out_path, oddballs_payload)


def write_html_reports(
    html_out_path: Path,
    enriched_rows: list[dict[str, object]],
) -> None:
    # Keep this call sequence immediately after JSON write so HTML failures are
    # fail-fast while preserving the JSON write attempt.
    research_tms_report.write_goerwitz_tms_html_report(html_out_path, enriched_rows)
    research_tms_report.write_goerwitz_tms_msp_yes_html_report(
        html_out_path, enriched_rows
    )
    research_tms_report.write_goerwitz_tms_msp_no_html_report(
        html_out_path, enriched_rows
    )


def print_run_summary(
    *,
    troubles_in_path: Path,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    all_changes_path: Path,
    out_path: Path,
    html_out_path: Path,
    enriched_rows_count: int,
    oddballs_in_path: Path | None,
    oddballs_out_path: Path | None,
    oddball_rows_count: int,
) -> None:
    print(f"Input troublemakers: {troubles_in_path}")
    print(f"wlc422-kq-u dir: {wlc422_kq_u_dir}")
    print(f"UXLC dir: {uxlc_dir}")
    print(f"MAM-simple dir: {mam_simple_dir}")
    print(f"All changes: {all_changes_path}")
    print(f"Output: {out_path}")
    if isinstance(oddballs_out_path, Path):
        print(f"Input oddballs: {oddballs_in_path}")
        print(f"Oddballs output: {oddballs_out_path}")
        print(f"Oddball rows: {oddball_rows_count}")
    print(f"HTML output: {html_out_path}")
    print(f"Rows: {enriched_rows_count}")


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
