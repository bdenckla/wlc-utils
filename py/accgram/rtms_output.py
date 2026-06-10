from __future__ import annotations

import json
from pathlib import Path

from accgram import ob_report
from accgram import rtms_meteg_witness
from accgram import rtms_ref
from accgram import rtms_report
from accgram import rtmsr_overview
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
    serializable_rows = rtms_meteg_witness.strip_internal_witness_fields_from_rows(
        enriched_rows
    )
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
            "troublemakers": len(serializable_rows),
        },
        "troublemakers": serializable_rows,
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
    enriched_rows: list[dict[str, object]],
    *,
    enriched_oddball_rows: list[dict[str, object]] | None = None,
    base_dir: Path | None = None,
) -> tuple[Path, Path | None]:
    # Present HTML entries in standard reading order (MAM book, chapter, verse),
    # independent of the order they appear in the input/JSON payloads.
    enriched_rows = _rows_in_reading_order(enriched_rows)
    if enriched_oddball_rows:
        enriched_oddball_rows = _rows_in_reading_order(enriched_oddball_rows)

    # Keep this call sequence immediately after JSON write so HTML failures are
    # fail-fast while preserving the JSON write attempt.
    overview_html_out_path = rtmsr_overview.write_goerwitz_overview_html_report(
        html_out_path
    )
    rtms_report.write_goerwitz_tms_html_report(html_out_path, enriched_rows)
    rtms_report.write_goerwitz_tms_msp_yes_html_report(html_out_path, enriched_rows)
    rtms_report.write_goerwitz_tms_msp_no_html_report(html_out_path, enriched_rows)

    oddballs_html_out_path: Path | None = None
    if enriched_oddball_rows and isinstance(base_dir, Path):
        oddballs_html_out_path = ob_report.write_goerwitz_obs_html_report(
            main_html_out_path=html_out_path,
            enriched_oddball_rows=enriched_oddball_rows,
            base_dir=base_dir,
        )

    return overview_html_out_path, oddballs_html_out_path


def print_run_summary(
    *,
    troubles_in_path: Path,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    all_changes_path: Path,
    out_path: Path,
    html_out_path: Path,
    overview_html_out_path: Path,
    enriched_rows_count: int,
    oddballs_in_path: Path | None,
    oddballs_out_path: Path | None,
    oddball_rows_count: int,
    oddballs_html_out_path: Path | None,
) -> None:
    print(f"Input troublemakers: {troubles_in_path}")
    print(f"wlc422-kq-u dir: {wlc422_kq_u_dir}")
    print(f"UXLC dir: {uxlc_dir}")
    print(f"MAM-simple dir: {mam_simple_dir}")
    print(f"All changes: {all_changes_path}")
    print(f"Output: {out_path}")
    print(f"Overview HTML output: {overview_html_out_path}")
    if isinstance(oddballs_out_path, Path):
        print(f"Input oddballs: {oddballs_in_path}")
        print(f"Oddballs output: {oddballs_out_path}")
        print(f"Oddball rows: {oddball_rows_count}")
    if isinstance(oddballs_html_out_path, Path):
        print(f"Oddballs HTML output: {oddballs_html_out_path}")
    print(f"HTML output: {html_out_path}")
    print(f"Rows: {enriched_rows_count}")


def _rows_in_reading_order(
    rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    return sorted(rows, key=_row_reading_order_key)


def _row_reading_order_key(row: dict[str, object]) -> tuple[int, int, int]:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError(
            "Row is missing non-empty string field 'ref' for reading-order sort"
        )
    return rtms_ref.reading_order_key(ref.strip())


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
