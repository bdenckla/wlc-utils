from __future__ import annotations

import argparse
from pathlib import Path

from accgram import mam_simple_verse
from accgram import ply_classify
from accgram import rtms_data
from accgram import rtms_focus_diff_expand
from accgram import rtms_output
from accgram import rtms_report
from accgram import rtms_rows
from accgram import tm_changes
from accgram import tm_descriptor
from accgram.ob_notes import get_structured_text
from accgram.tm_sanity import sanity_check_structured_text

import repo_paths


def default_oddballs_in(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "accgram" / "ply" / "_oddballs.json"


def default_ply_dir(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "accgram" / "ply"


def default_wlc422_kq_u_dir(repo_root: Path) -> Path:
    return rtms_data.default_wlc422_kq_u_dir(repo_root)


def default_uxlc_dir(repo_root: Path) -> Path:
    return repo_paths.in_dir() / "UXLC-39"


def default_mam_simple_dir(repo_root: Path) -> Path:
    return mam_simple_verse.default_mam_simple_dir(repo_root)


def default_all_changes_path(repo_root: Path) -> Path:
    return repo_paths.in_dir() / "UXLC-misc" / "all_changes.json"


def default_oddballs_out_path(repo_root: Path) -> Path:
    return repo_paths.out_dir() / "accgram" / "research-oddballs.json"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=default_wlc422_kq_u_dir(repo_root),
        help="Directory containing 1verses_*.json files.",
    )
    parser.add_argument(
        "--uxlc-dir",
        type=Path,
        default=default_uxlc_dir(repo_root),
        help="Directory containing UXLC XML book files.",
    )
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=default_mam_simple_dir(repo_root),
        help="Directory containing MAM-simple json-vtrad-bhs book files.",
    )
    parser.add_argument(
        "--all-changes",
        type=Path,
        default=default_all_changes_path(repo_root),
        help="Path to in/UXLC-misc/all_changes.json for sanity checks.",
    )
    parser.add_argument(
        "--oddballs-in",
        type=Path,
        default=default_oddballs_in(repo_root),
        help="Path to _oddballs.json input (PLY-derived; regenerated each run).",
    )
    parser.add_argument(
        "--ply-dir",
        type=Path,
        default=default_ply_dir(repo_root),
        help="Directory of PLY *_ag.txt outputs for the oddball corpus.",
    )
    parser.add_argument(
        "--oddballs-out",
        type=Path,
        default=default_oddballs_out_path(repo_root),
        help="Output JSON path for enriched oddball research artifact.",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=rtms_report.default_html_out_path(repo_root),
        help="Output HTML path for the goerwitz.html report.",
    )


def run(args: argparse.Namespace) -> None:
    repo_root = repo_paths.repo_root()

    all_changes_path = getattr(args, "all_changes", None)
    if not isinstance(all_changes_path, Path):
        all_changes_path = default_all_changes_path(repo_root)

    html_out_path = rtms_report.resolve_html_out_path(args, repo_root)

    oddballs_in_path = args.oddballs_in
    oddballs_out_path = args.oddballs_out
    ply_dir = getattr(args, "ply_dir", None) or default_ply_dir(repo_root)

    # (Re)derive the PLY-based oddball set from out/accgram/ply only. Every ERROR
    # verse -- including the 49 the C binary emitted nothing for -- now lives there.
    ply_classify.write_ply_oddballs(
        ply_dir=ply_dir,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        oddballs_out=oddballs_in_path,
    )

    refs_by_book: dict[str, set[tuple[int, int]]] = {}
    parsed_oddball_rows = rtms_rows.parse_oddball_rows(oddballs_in_path, refs_by_book)

    # Annotated oddballs (those carrying hand-authored ob_notes structured text) get the
    # UXLC/changetext validation the old troublemaker rows used to get; each validation
    # step self-skips on records lacking its field (uxlc_change/assessment). Unannotated
    # oddballs get plain enrichment.
    structured_text_by_ref = get_structured_text()
    rich_refs = [
        ref for _row, _bcv, ref in parsed_oddball_rows if ref in structured_text_by_ref
    ]
    sanity_check_structured_text(
        refs=rich_refs,
        all_changes_path=all_changes_path,
    )

    wlc_focus_by_ref = _ob_wlc_focus_by_ref()
    all_changes_by_url = tm_changes.load_all_changes_by_url(all_changes_path)

    wlc422_by_bcv, uxlc_by_bcv, mam_simple_by_bcv = rtms_data.load_source_indexes(
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        refs_by_book=refs_by_book,
    )

    enriched_oddball_rows: list[dict[str, object]] = []
    diff_wlc_uxlc_for_checks_by_ref: dict[str, object] = {}
    rich_parsed_rows: list[tuple[dict[str, object], str, str]] = []
    for row, bcv, ref in parsed_oddball_rows:
        enriched_row, diff_wlc_uxlc_for_checks = _build_enriched_row(
            row=row,
            bcv=bcv,
            ref=ref,
            wlc422_by_bcv=wlc422_by_bcv,
            uxlc_by_bcv=uxlc_by_bcv,
            mam_simple_by_bcv=mam_simple_by_bcv,
            wlc422_kq_u_dir=args.wlc422_kq_u_dir,
            uxlc_dir=args.uxlc_dir,
            mam_simple_dir=args.mam_simple_dir,
            wlc_focus=wlc_focus_by_ref.get(ref),
        )
        enriched_oddball_rows.append(enriched_row)
        if ref in structured_text_by_ref:
            diff_wlc_uxlc_for_checks_by_ref[ref] = diff_wlc_uxlc_for_checks
            rich_parsed_rows.append((row, bcv, ref))

    _validate_structured_text_high_level(
        parsed_rows=rich_parsed_rows,
        wlc_focus_by_ref=wlc_focus_by_ref,
        diff_wlc_uxlc_for_checks_by_ref=diff_wlc_uxlc_for_checks_by_ref,
        all_changes_by_url=all_changes_by_url,
    )

    rtms_output.write_oddballs_payload(
        oddballs_out_path=oddballs_out_path,
        oddballs_in_path=oddballs_in_path,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        enriched_oddball_rows=enriched_oddball_rows,
        source_file=__file__,
    )

    # The oddball report locates each row's ERROR tree by output_file under ply_dir.
    combined_html_out_path = rtms_output.write_html_reports(
        html_out_path,
        enriched_oddball_rows=enriched_oddball_rows,
        base_dir=ply_dir,
    )

    rtms_output.print_run_summary(
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        all_changes_path=all_changes_path,
        combined_html_out_path=combined_html_out_path,
        oddballs_in_path=oddballs_in_path,
        oddballs_out_path=oddballs_out_path,
        oddball_rows_count=len(enriched_oddball_rows),
    )


def _ob_wlc_focus_by_ref() -> dict[str, str | None]:
    # Every annotated oddball's WLC focus now comes from the single by-book ob_notes set.
    return {
        ref: _structured_wlc_focus(structured_text)
        for ref, structured_text in get_structured_text().items()
    }


def _validate_structured_text_high_level(
    *,
    parsed_rows: list[tuple[dict[str, object], str, str]],
    wlc_focus_by_ref: dict[str, str | None],
    diff_wlc_uxlc_for_checks_by_ref: dict[str, object],
    all_changes_by_url: dict[str, dict[str, object]],
) -> None:
    stext = get_structured_text()
    for _row, _bcv, ref in parsed_rows:
        structured_text = stext.get(ref)
        if structured_text is None:
            continue

        if ref not in diff_wlc_uxlc_for_checks_by_ref:
            raise ValueError(f"Missing diff_wlc_uxlc_for_checks for {ref}")

        diff_wlc_uxlc_for_checks = diff_wlc_uxlc_for_checks_by_ref[ref]
        _validate_structured_text_uxlc_match(
            ref=ref,
            structured_text=structured_text,
            diff_wlc_uxlc_for_checks=diff_wlc_uxlc_for_checks,
            wlc_focus=wlc_focus_by_ref.get(ref),
        )
        _validate_structured_text_changetext_match(
            ref=ref,
            structured_text=structured_text,
            diff_wlc_uxlc_for_checks=diff_wlc_uxlc_for_checks,
            all_changes_by_url=all_changes_by_url,
        )


def _validate_structured_text_uxlc_match(
    *,
    ref: str,
    structured_text: dict[str, object],
    diff_wlc_uxlc_for_checks: object,
    wlc_focus: str | None,
) -> None:
    assessment = structured_text.get("assessment")
    assessment_uxlc = assessment.get("uxlc") if isinstance(assessment, dict) else None
    if not isinstance(assessment_uxlc, str):
        return

    diff_wlc_uxlc_for_assessment = _expand_subset_diff_to_wlc_focus(
        diff_wlc_uxlc_for_checks,
        wlc_focus=wlc_focus,
        rhs_key="uxlc",
    )
    matches_converted_diff = tm_descriptor.assessment_uxlc_matches_converted_diff_uxlc(
        assessment_uxlc=assessment_uxlc,
        diff_wlc_uxlc=diff_wlc_uxlc_for_assessment,
    )
    if matches_converted_diff is False:
        raise ValueError(
            "structured_text assessment.uxlc mismatches converted diff_wlc_uxlc.uxlc "
            f"for {ref}: assessment.uxlc={assessment_uxlc} "
            f"diff_wlc_uxlc={diff_wlc_uxlc_for_assessment}"
        )


def _validate_structured_text_changetext_match(
    *,
    ref: str,
    structured_text: dict[str, object],
    diff_wlc_uxlc_for_checks: object,
    all_changes_by_url: dict[str, dict[str, object]],
) -> None:
    uxlc_change = structured_text.get("uxlc_change")
    if uxlc_change is None:
        return
    assert isinstance(
        uxlc_change, str
    ), f"structured_text.uxlc_change must be a string URL for {ref}"

    canonical_url = tm_changes.canonicalize_uxlc_change_url(uxlc_change)
    if canonical_url is None:
        raise ValueError(
            f"Malformed structured_text.uxlc_change URL for {ref}: {uxlc_change}"
        )

    change_row = all_changes_by_url.get(canonical_url)
    if change_row is None:
        raise ValueError(
            "structured_text.uxlc_change not found in all_changes.json "
            f"for {ref}: {uxlc_change}"
        )

    changetext = change_row.get("changetext")
    if not isinstance(changetext, str):
        raise ValueError(
            f"all_changes.json row is missing string changetext for URL {canonical_url}"
        )

    matches_changetext = tm_descriptor.diff_uxlc_matches_changetext(
        diff_wlc_uxlc=diff_wlc_uxlc_for_checks,
        changetext=changetext,
    )
    if matches_changetext is False:
        raise ValueError(
            "diff_wlc_uxlc.uxlc mismatches all_changes changetext after sanitization "
            f"for {ref}: changetext={changetext} "
            f"diff_wlc_uxlc={diff_wlc_uxlc_for_checks}"
        )


def _build_enriched_row(
    *,
    row: dict[str, object],
    bcv: str,
    ref: str,
    wlc422_by_bcv: dict[str, dict[str, object]],
    uxlc_by_bcv: dict[str, dict[str, object]],
    mam_simple_by_bcv: dict[str, dict[str, object]],
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
    wlc_focus: str | None,
) -> tuple[dict[str, object], object]:
    return rtms_data.build_enriched_row(
        row=row,
        bcv=bcv,
        ref=ref,
        wlc422_by_bcv=wlc422_by_bcv,
        uxlc_by_bcv=uxlc_by_bcv,
        mam_simple_by_bcv=mam_simple_by_bcv,
        wlc422_kq_u_dir=wlc422_kq_u_dir,
        uxlc_dir=uxlc_dir,
        mam_simple_dir=mam_simple_dir,
        wlc_focus=wlc_focus,
    )


def _structured_wlc_focus(structured_text: object) -> str | None:
    return rtms_focus_diff_expand.structured_wlc_focus(structured_text)


def _expand_subset_diff_to_wlc_focus(
    diff_value: object,
    *,
    wlc_focus: str | None,
    rhs_key: str,
) -> object:
    return rtms_focus_diff_expand.expand_subset_diff_to_wlc_focus(
        diff_value,
        wlc_focus=wlc_focus,
        rhs_key=rhs_key,
    )
