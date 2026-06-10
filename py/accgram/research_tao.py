from __future__ import annotations

import argparse
from pathlib import Path

from accgram import ob_data
from accgram import ply_classify
from accgram import rtms_data
from accgram import rtms_focus_diff_expand
from accgram import rtms_output
from accgram import rtms_ref
from accgram import rtms_report
from accgram import rtms_rows
from accgram import tm_changes
from accgram import tm_descriptor
from accgram.mam_simple_verse import default_mam_simple_dir as _default_mam_simple_dir
from accgram.tm_data import get_structured_text
from accgram.tm_sanity import sanity_check_structured_text


def default_troubles_in(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply" / "_troublemakers.json"


def default_oddballs_in(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply" / "_oddballs.json"


def default_ply_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply"


def default_ply_tms_dir(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-tms"


def default_psf_in_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "goerwitz" / "wlc_422_psf"


def default_unfiltered_in_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "goerwitz" / "wlc_422_ps"


def default_wlc422_kq_u_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "wlc422-kq-u"


def default_uxlc_dir(repo_root: Path) -> Path:
    return repo_root / "in" / "UXLC-39"


def default_mam_simple_dir(repo_root: Path) -> Path:
    return _default_mam_simple_dir(repo_root)


def default_all_changes_path(repo_root: Path) -> Path:
    return repo_root.parent / "UXLC-utils" / "out" / "UXLC-misc" / "all_changes.json"


def default_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "research-troublemakers.json"


def default_oddballs_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "research-oddballs.json"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--troubles-in",
        type=Path,
        default=default_troubles_in(repo_root),
        help="Path to _troublemakers.json input.",
    )
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
        help="Path to UXLC-utils out/UXLC-misc/all_changes.json for sanity checks.",
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
        help="Directory of PLY *_ag.txt outputs for the clean+oddball corpus.",
    )
    parser.add_argument(
        "--ply-tms-dir",
        type=Path,
        default=default_ply_tms_dir(repo_root),
        help="Directory of PLY *_ag.txt outputs for the troublemaker corpus.",
    )
    parser.add_argument(
        "--psf-in-dir",
        type=Path,
        default=default_psf_in_dir(repo_root),
        help="Filtered new-format input dir (content for ply/ oddballs).",
    )
    parser.add_argument(
        "--unfiltered-in-dir",
        type=Path,
        default=default_unfiltered_in_dir(repo_root),
        help="Unfiltered new-format input dir (content for ply-tms/ oddballs and troublemakers).",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=default_out_path(repo_root),
        help="Output JSON path for enriched research artifact.",
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
        help="Output HTML path for research-tms-and-oddballs report.",
    )


def run(args: argparse.Namespace) -> None:
    repo_root = Path(__file__).resolve().parent.parent.parent

    all_changes_path = getattr(args, "all_changes", None)
    if not isinstance(all_changes_path, Path):
        all_changes_path = default_all_changes_path(repo_root)

    html_out_path = rtms_report.resolve_html_out_path(args, repo_root)

    oddballs_in_path = getattr(args, "oddballs_in", None)

    # (Re)derive the PLY-based oddball/troublemaker sets from the PLY outputs so
    # the research command never reads out/accgram/goerwitz. The 26 troublemakers
    # PLY parses into ERROR trees are reclassified as oddballs here.
    if isinstance(oddballs_in_path, Path):
        ply_classify.write_ply_oddballs_and_troublemakers(
            ply_dir=getattr(args, "ply_dir", None) or default_ply_dir(repo_root),
            ply_tms_dir=getattr(args, "ply_tms_dir", None)
            or default_ply_tms_dir(repo_root),
            psf_in_dir=getattr(args, "psf_in_dir", None)
            or default_psf_in_dir(repo_root),
            unfiltered_in_dir=getattr(args, "unfiltered_in_dir", None)
            or default_unfiltered_in_dir(repo_root),
            oddballs_out=oddballs_in_path,
            troubles_out=args.troubles_in,
        )

    refs_by_book: dict[str, set[tuple[int, int]]] = {}
    parsed_rows = rtms_rows.parse_troublemaker_rows(args.troubles_in, refs_by_book)

    oddballs_out_path = getattr(args, "oddballs_out", None)
    parsed_oddball_rows: list[tuple[dict[str, object], str, str]] = []
    if isinstance(oddballs_in_path, Path) and isinstance(oddballs_out_path, Path):
        parsed_oddball_rows = rtms_rows.parse_oddball_rows(
            oddballs_in_path,
            refs_by_book,
        )
    elif oddballs_in_path is not None or oddballs_out_path is not None:
        raise ValueError("Expected both oddballs_in and oddballs_out, or neither")

    # Validate notes for every ref displayed with notes: the 23 troublemakers plus
    # the 26 reclassified oddballs, whose notes are still served from tm_data.
    reclassified_refs = [
        ref
        for row, _bcv, ref in parsed_oddball_rows
        if row.get("output_dir") == "ply-tms"
    ]
    sanity_check_structured_text(
        refs=[ref for _row, _bcv, ref in parsed_rows] + reclassified_refs,
        all_changes_path=all_changes_path,
    )
    wlc_focus_by_ref = _wlc_focus_by_ref()
    all_changes_by_url = tm_changes.load_all_changes_by_url(all_changes_path)

    wlc422_by_bcv, uxlc_by_bcv, mam_simple_by_bcv = rtms_data.load_source_indexes(
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        refs_by_book=refs_by_book,
    )

    enriched_rows, diff_wlc_uxlc_for_checks_by_ref = _enrich_troublemaker_rows(
        parsed_rows=parsed_rows,
        wlc_focus_by_ref=wlc_focus_by_ref,
        wlc422_by_bcv=wlc422_by_bcv,
        uxlc_by_bcv=uxlc_by_bcv,
        mam_simple_by_bcv=mam_simple_by_bcv,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
    )

    _validate_structured_text_high_level(
        parsed_rows=parsed_rows,
        wlc_focus_by_ref=wlc_focus_by_ref,
        diff_wlc_uxlc_for_checks_by_ref=diff_wlc_uxlc_for_checks_by_ref,
        all_changes_by_url=all_changes_by_url,
    )

    enriched_oddball_rows = _enrich_rows_without_structured_text(
        parsed_rows=parsed_oddball_rows,
        wlc_focus_by_ref=_ob_wlc_focus_by_ref(),
        wlc422_by_bcv=wlc422_by_bcv,
        uxlc_by_bcv=uxlc_by_bcv,
        mam_simple_by_bcv=mam_simple_by_bcv,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
    )

    rtms_output.write_troublemakers_payload(
        out_path=args.out,
        troubles_in_path=args.troubles_in,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        enriched_rows=enriched_rows,
        source_file=__file__,
    )

    if isinstance(oddballs_out_path, Path) and isinstance(oddballs_in_path, Path):
        rtms_output.write_oddballs_payload(
            oddballs_out_path=oddballs_out_path,
            oddballs_in_path=oddballs_in_path,
            wlc422_kq_u_dir=args.wlc422_kq_u_dir,
            uxlc_dir=args.uxlc_dir,
            mam_simple_dir=args.mam_simple_dir,
            enriched_oddball_rows=enriched_oddball_rows,
            source_file=__file__,
        )

    # Base dir holding the two PLY output subdirs (ply/, ply-tms/); the oddball
    # report appends each row's output_dir to locate its ERROR tree.
    accgram_base_dir = (
        oddballs_in_path.parent.parent if isinstance(oddballs_in_path, Path) else None
    )
    overview_html_out_path, oddballs_html_out_path = rtms_output.write_html_reports(
        html_out_path,
        enriched_rows,
        enriched_oddball_rows=enriched_oddball_rows,
        base_dir=accgram_base_dir,
    )

    rtms_output.print_run_summary(
        troubles_in_path=args.troubles_in,
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        all_changes_path=all_changes_path,
        out_path=args.out,
        html_out_path=html_out_path,
        overview_html_out_path=overview_html_out_path,
        enriched_rows_count=len(enriched_rows),
        oddballs_in_path=(
            oddballs_in_path if isinstance(oddballs_in_path, Path) else None
        ),
        oddballs_out_path=(
            oddballs_out_path if isinstance(oddballs_out_path, Path) else None
        ),
        oddball_rows_count=len(enriched_oddball_rows),
        oddballs_html_out_path=oddballs_html_out_path,
    )


def _enrich_troublemaker_rows(
    *,
    parsed_rows: list[tuple[dict[str, object], str, str]],
    wlc_focus_by_ref: dict[str, str | None],
    wlc422_by_bcv: dict[str, dict[str, object]],
    uxlc_by_bcv: dict[str, dict[str, object]],
    mam_simple_by_bcv: dict[str, dict[str, object]],
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    enriched_rows: list[dict[str, object]] = []
    diff_wlc_uxlc_for_checks_by_ref: dict[str, object] = {}
    for row, bcv, ref in parsed_rows:
        wlc_focus = wlc_focus_by_ref.get(ref)

        enriched_row, diff_wlc_uxlc_for_checks = _build_enriched_row(
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
        diff_wlc_uxlc_for_checks_by_ref[ref] = diff_wlc_uxlc_for_checks
        enriched_rows.append(enriched_row)

    return enriched_rows, diff_wlc_uxlc_for_checks_by_ref


def _wlc_focus_by_ref() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    stext = get_structured_text()
    for ref, structured_text in stext.items():
        out[ref] = _structured_wlc_focus(structured_text)
    return out


def _ob_wlc_focus_by_ref() -> dict[str, str | None]:
    out: dict[str, str | None] = {}
    # Reclassified troublemakers have no ob_data entry; fall back to tm_data so the
    # 26 still get a WLC focus (their notes are served from tm_data).
    for ref, structured_text in get_structured_text().items():
        out[ref] = _structured_wlc_focus(structured_text)
    for ref, structured_text in ob_data.get_structured_text().items():
        out[ref] = _structured_wlc_focus(structured_text)
    return out


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


def _enrich_rows_without_structured_text(
    *,
    parsed_rows: list[tuple[dict[str, object], str, str]],
    wlc_focus_by_ref: dict[str, str | None],
    wlc422_by_bcv: dict[str, dict[str, object]],
    uxlc_by_bcv: dict[str, dict[str, object]],
    mam_simple_by_bcv: dict[str, dict[str, object]],
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
) -> list[dict[str, object]]:
    enriched_rows: list[dict[str, object]] = []
    for row, bcv, ref in parsed_rows:
        enriched_row, _ = _build_enriched_row(
            row=row,
            bcv=bcv,
            ref=ref,
            wlc422_by_bcv=wlc422_by_bcv,
            uxlc_by_bcv=uxlc_by_bcv,
            mam_simple_by_bcv=mam_simple_by_bcv,
            wlc422_kq_u_dir=wlc422_kq_u_dir,
            uxlc_dir=uxlc_dir,
            mam_simple_dir=mam_simple_dir,
            wlc_focus=wlc_focus_by_ref.get(ref),
        )
        enriched_rows.append(enriched_row)
    return enriched_rows


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


# Compatibility wrappers retained for tests and report helpers.
def _read_json(path: Path):
    return rtms_rows.read_json(path)


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


def _normalize_payload_for_diff_ignoring_notes(payload: object) -> object:
    return rtms_data._normalize_payload_for_diff_ignoring_notes(payload)


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


def _validate_unique_wlc_focus_in_wlc_verse(
    *,
    ref: str,
    wlc422_kq_u_verse: object,
    wlc_focus: str | None,
) -> None:
    rtms_focus_diff_expand.validate_unique_focus_occurrence(
        ref=ref,
        wlc422_kq_u_verse=wlc422_kq_u_verse,
        wlc_focus=wlc_focus,
    )


def _parse_ref(ref: str, *, row_kind: str = "troublemaker") -> tuple[str, int, int]:
    return rtms_ref.parse_ref(ref, row_kind=row_kind)


def _to_compact_bcv(bb: str, chnu: int, vrnu: int) -> str:
    return rtms_ref.to_compact_bcv(bb, chnu, vrnu)


def _to_ref(bb: str, chnu: int, vrnu: int) -> str:
    return rtms_ref.to_ref(bb, chnu, vrnu)


def _load_wlc422_index(wlc422_kq_u_dir: Path) -> dict[str, dict[str, object]]:
    return rtms_data._load_wlc422_index(wlc422_kq_u_dir)


def _collapse_wlc_notes_to_string(node: object) -> object:
    return rtms_data._collapse_wlc_notes_to_string(node)


def _interpolate_wlc422_kq_qere(verse_payload: dict[str, object]) -> dict[str, object]:
    return rtms_data._interpolate_wlc422_kq_qere(verse_payload)


def _strip_sam_pe_inun_token(token: object) -> object | None:
    return rtms_data._strip_sam_pe_inun_token(token)


def _load_uxlc_for_refs(
    uxlc_dir: Path,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> dict[str, dict[str, object]]:
    return rtms_data._load_uxlc_for_refs(uxlc_dir, refs_by_book)


def _to_xmlish_verse_child(element):
    return rtms_data._to_xmlish_verse_child(element)


def _to_xmlish_inline(element):
    return rtms_data._to_xmlish_inline(element)
