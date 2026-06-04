from __future__ import annotations

from pathlib import Path

from accgram import research_tms_report_bracket_notes
from accgram import research_tms_report_intro
from accgram import research_tms_report_media
from accgram import research_tms_report_open_issues
from accgram import research_tms_report_sat
from accgram import research_tms_report_subsets
from accgram import research_tms_report_verse
from accgram import research_tms_ref
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import bib_locales as tbn
from py_html import wlc_utils_html
from py_wlc import my_wlc_bcv_str

_GOERWITZ_TMS_WIDTH_CLASS = "goerwitz-tms-width-limited"
_SELF_LINK_SYMBOL = "🔗"
_MAIN_REPORT_TITLE = "Goerwitz TMs"
_MAIN_REPORT_HEADING = "Goerwitz Troublemakers"
_MSP_Y_FLAVOR = "msp-y"
_MSP_N_FLAVOR = "msp-n"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_root / "gh-pages" / "accgram" / "goerwitz-tms.html"


def resolve_html_out_path(args: object, repo_root: Path) -> Path:
    explicit_html_out = getattr(args, "html_out", None)
    if isinstance(explicit_html_out, Path):
        return explicit_html_out

    out_path = getattr(args, "out", None)
    if isinstance(out_path, Path):
        derived_html_out = _derive_html_out_from_out_path(out_path)
        if derived_html_out is not None:
            return derived_html_out

    return default_html_out_path(repo_root)


def write_goerwitz_tms_html_report(
    html_out_path: Path,
    enriched_rows: list[dict[str, object]],
) -> None:
    _write_goerwitz_tms_html_report(
        html_out_path,
        enriched_rows,
        top_contents=research_tms_report_subsets.build_main_subsets_top_contents(
            html_out_path
        ),
        title=_MAIN_REPORT_TITLE,
        heading_level_1_text=_MAIN_REPORT_HEADING,
    )


def write_goerwitz_tms_msp_yes_html_report(
    main_html_out_path: Path,
    enriched_rows: list[dict[str, object]],
) -> None:
    total_count = len(enriched_rows)
    html_out_path = research_tms_report_subsets.missing_sof_pasuq_yes_html_out_path(
        main_html_out_path
    )
    _write_goerwitz_tms_html_report(
        html_out_path,
        research_tms_report_subsets.filter_missing_sof_pasuq_yes_rows(enriched_rows),
        top_contents=research_tms_report_subsets.build_msp_yes_related_pages_top_contents(
            main_html_out_path
        ),
        title=f"{_MAIN_REPORT_TITLE} ({_MSP_Y_FLAVOR})",
        heading_level_1_text=f"{_MAIN_REPORT_HEADING} ({_MSP_Y_FLAVOR})",
        total_count=total_count,
    )


def write_goerwitz_tms_msp_no_html_report(
    main_html_out_path: Path,
    enriched_rows: list[dict[str, object]],
) -> None:
    total_count = len(enriched_rows)
    html_out_path = research_tms_report_subsets.missing_sof_pasuq_no_html_out_path(
        main_html_out_path
    )
    _write_goerwitz_tms_html_report(
        html_out_path,
        research_tms_report_subsets.filter_missing_sof_pasuq_no_rows(enriched_rows),
        top_contents=research_tms_report_subsets.build_msp_no_related_pages_top_contents(
            main_html_out_path
        ),
        title=f"{_MAIN_REPORT_TITLE} ({_MSP_N_FLAVOR})",
        heading_level_1_text=f"{_MAIN_REPORT_HEADING} ({_MSP_N_FLAVOR})",
        total_count=total_count,
    )


def _write_goerwitz_tms_html_report(
    html_out_path: Path,
    enriched_rows: list[dict[str, object]],
    *,
    top_contents: tuple[object, ...],
    title: str,
    heading_level_1_text: str,
    total_count: int | None = None,
) -> None:
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    body_contents = _build_body_contents(
        enriched_rows,
        top_contents=top_contents,
        heading_level_1_text=heading_level_1_text,
        total_count=total_count,
    )
    write_ctx = wlc_utils_html.WriteCtx(
        title=title,
        path=str(html_out_path),
    )
    wlc_utils_html.write_html_to_file(
        body_contents=body_contents,
        write_ctx=write_ctx,
        path_to_style=_path_to_gh_pages_style(html_out_path),
    )


def _build_body_contents(
    enriched_rows: list[dict[str, object]],
    *,
    top_contents: tuple[object, ...],
    heading_level_1_text: str,
    total_count: int | None = None,
) -> tuple[object, ...]:
    row_count = len(enriched_rows)
    sections: list[object] = [
        wlc_utils_html.heading_level_1(heading_level_1_text),
        *top_contents,
    ]
    sections.extend(
        research_tms_report_intro.build_intro_contents(row_count, total_count)
    )
    sections.extend(research_tms_report_open_issues.build_open_issues_section())
    sections.extend(
        research_tms_report_bracket_notes.build_wlc_bracket_notes_section(enriched_rows)
    )

    for index, row in enumerate(enriched_rows):
        sections.extend(_render_row_section(row))
        if index + 1 < len(enriched_rows):
            sections.append(wlc_utils_html.horizontal_rule())

    wrapper = wlc_utils_html.div(
        tuple(sections),
        {"class": _GOERWITZ_TMS_WIDTH_CLASS},
    )
    return (wrapper,)


def _render_row_section(row: dict[str, object]) -> tuple[object, ...]:
    ref = _row_ref(row)
    bb, chnu, vrnu, bcv = _parse_ref_to_wlc_bcv(ref)
    section_anchor_id = _troublemaker_anchor_id(bcv)

    section_items: list[object] = [
        wlc_utils_html.heading_level_2(ref, {"id": section_anchor_id}),
        *_render_ref_links(
            bb=bb,
            chnu=chnu,
            vrnu=vrnu,
            bcv=bcv,
            row=row,
            section_anchor_id=section_anchor_id,
        ),
        _render_wlc_verse_paragraph(row),
        _render_sat_table(row),
        *_render_image_paragraphs(row),
        *_render_comment_paragraphs(row),
    ]
    return tuple(section_items)


def _render_ref_links(
    bb: str,
    chnu: int,
    vrnu: int,
    bcv: str,
    row: dict[str, object],
    section_anchor_id: str,
) -> tuple[object, ...]:
    mam_url = _mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)
    tanach_us_url = my_wlc_bcv_str.get_tanach_dot_us_url(bcv)
    summary = _structured_text_value(row, "st-summary")
    uxlc_change = _structured_text_value(row, "uxlc_change")
    uxlc_note_page = _structured_text_value(row, "uxlc_note_page")

    permalink_summary: list[object] = [
        wlc_utils_html.anchor(
            _SELF_LINK_SYMBOL,
            {
                "href": f"#{section_anchor_id}",
                "title": "Permalink to this section",
                "aria-label": "Permalink to this section",
            },
        ),
    ]
    if isinstance(summary, str) and summary.strip():
        permalink_summary.extend([" ", f"Summary: {summary.strip()}"])

    links: list[object] = [
        wlc_utils_html.anchor("MAM-with-doc verse", {"href": mam_url}),
        " | ",
        wlc_utils_html.anchor("UXLC verse", {"href": tanach_us_url}),
    ]

    if isinstance(uxlc_change, str) and uxlc_change.strip():
        links.extend(
            [
                " | ",
                wlc_utils_html.anchor(
                    "UXLC change",
                    {"href": uxlc_change.strip()},
                ),
            ]
        )

    if isinstance(uxlc_note_page, str) and uxlc_note_page.strip():
        links.extend(
            [
                " | ",
                wlc_utils_html.anchor(
                    "UXLC note page",
                    {"href": uxlc_note_page.strip()},
                ),
            ]
        )

    return (
        wlc_utils_html.para(tuple(permalink_summary)),
        wlc_utils_html.para(tuple(links)),
    )


def _troublemaker_anchor_id(bcv: str) -> str:
    return f"tm{bcv.replace(':', 'v')}"


def _render_sat_table(row: dict[str, object]) -> object:
    return research_tms_report_sat.render_sat_table(
        row,
        row_ref=_row_ref(row),
        structured_text_lookup=_structured_text_value,
        wlc_tokens=research_tms_report_verse.wlc_verse_vels(row),
    )


def _render_comment_paragraphs(row: dict[str, object]) -> tuple[object, ...]:
    return research_tms_report_media.render_comment_paragraphs(
        row,
        structured_text_lookup=_structured_text_value,
    )


def _render_image_paragraphs(row: dict[str, object]) -> tuple[object, ...]:
    return research_tms_report_media.render_image_paragraphs(row)


def _render_wlc_verse_paragraph(row: dict[str, object]) -> object:
    return research_tms_report_verse.render_wlc_verse_paragraph(
        row,
        structured_text_lookup=_structured_text_value,
    )


def _structured_text_value(row: dict[str, object], key: str) -> object:
    structured_text = row.get("structured_text")
    if not isinstance(structured_text, dict):
        return None
    return structured_text.get(key)


def _row_ref(row: dict[str, object]) -> str:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Troublemaker row is missing non-empty string field 'ref'")
    return ref.strip()


def _parse_ref_to_wlc_bcv(ref: str) -> tuple[str, int, int, str]:
    bb, chnu, vrnu = research_tms_ref.parse_ref(ref)
    bcv = research_tms_ref.to_compact_bcv(bb, chnu, vrnu)
    return bb, chnu, vrnu, bcv


def _remap_mam_with_doc_chapter_verse(bb: str, chnu: int, vrnu: int) -> tuple[int, int]:
    # One-time remap: Numbers 25:19 aligns to MAM-with-doc at 26:1.
    if bb == "nu" and chnu == 25 and vrnu == 19:
        return 26, 1
    return chnu, vrnu


def _mam_with_doc_url(bb: str, chnu: int, vrnu: int) -> str:
    bk39id = wlc_bb_to_bk39id(bb)
    osdf = tbn.ordered_short_dash_full_39(bk39id)
    mam_chnu, mam_vrnu = _remap_mam_with_doc_chapter_verse(bb, chnu, vrnu)
    return f"https://bdenckla.github.io/MAM-with-doc/{osdf}.html#c{mam_chnu}v{mam_vrnu}"


def _derive_html_out_from_out_path(out_path: Path) -> Path | None:
    for ancestor in out_path.parents:
        if ancestor.name == "out":
            return ancestor.parent / "gh-pages" / "accgram" / "goerwitz-tms.html"

    parent = out_path.parent
    if parent != out_path:
        return parent / "gh-pages" / "accgram" / "goerwitz-tms.html"

    return None


def _path_to_gh_pages_style(html_out_path: Path) -> str:
    path_parts = list(html_out_path.parent.parts)
    if "gh-pages" not in path_parts:
        return "../"

    gh_pages_index = path_parts.index("gh-pages")
    depth_from_gh_pages = len(path_parts) - gh_pages_index - 1
    if depth_from_gh_pages <= 0:
        return ""

    return "../" * depth_from_gh_pages
