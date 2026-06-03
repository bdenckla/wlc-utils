from __future__ import annotations

import json
import re
from pathlib import Path

from accgram import research_tms_report_bracket_notes
from accgram import research_tms_report_diff_format
from accgram import research_tms_report_intro
from accgram import research_tms_report_open_issues
from accgram import research_tms_report_subsets
from accgram import research_tms_report_wlc_word_format
from accgram import troublemaker_structured_text_sanity
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import bib_locales as tbn
from py_html import my_html_for_img
from py_html import wlc_utils_html
from py_wlc import my_wlc_bcv_str

_ASSESSMENT_KEYS = ("manuscript", "bhs", "wlc", "uxlc", "mam")
_CONTEXT_HBO_ROW_KEYS = {"wlc_before", "wlc_focus", "wlc_focus.hbo", "wlc_after"}
_GOERWITZ_TMS_WIDTH_CLASS = "goerwitz-tms-width-limited"
_SELF_LINK_SYMBOL = "🔗"
_MAIN_REPORT_TITLE = "Goerwitz TMs"
_MAIN_REPORT_HEADING = "Goerwitz Troublemakers"
_MSP_Y_FLAVOR = "msp-y"
_MSP_N_FLAVOR = "msp-n"
_SAT_A_KEY_MERGE_TARGETS: dict[str, str] = {
    "a.wlc": "wlc_focus",
    "a.uxlc": "diff_wlc_uxlc",
    "a.mam": "diff_wlc_mam",
}
_SAT_ROW_SUPPRESSIONS_BY_REF: dict[str, set[str]] = {
    "1k 16:33": {"diff_wlc_uxlc[1]"},
    "mi 2:7": {"diff_wlc_mam[2]"},
}
_POINTED_HEBREW_SEGMENT_RE = re.compile(r"[\u0590-\u05FF]+")
_HEBREW_POINTING_MARK_RE = re.compile(r"[\u0591-\u05C7]")
_HEBREW_LETTER_RE = re.compile(r"[\u05D0-\u05EA]")
_LC_IMAGE_NAME_RE = re.compile(r"LC-([0-9]+[A-Za-z])-col-([0-9]+)-line-([0-9]+)")

# Internal SAT row shape: (value_cell, middle_description_cell, key_cell).
SatRow = tuple[str, str, str]


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
        wlc_utils_html.anchor("tanach.us verse", {"href": tanach_us_url}),
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
    verse_text = _wlc_verse_text(row)
    wlc_tokens = _wlc_verse_vels(row)
    wlc_focus = _structured_text_value(row, "wlc_focus")
    wlc_focus_str = wlc_focus if isinstance(wlc_focus, str) else None
    wlc_focus_notes = (
        research_tms_report_wlc_word_format.collect_wlc_word_bracket_notes(
            wlc_tokens,
            wlc_focus_str,
            render_sat_value=_render_sat_value,
        )
    )
    before_focus, focus_placeholder, after_focus = _split_wlc_context(
        verse_text=verse_text,
        wlc_focus=wlc_focus_str,
    )

    sat_rows: list[SatRow] = [_sat_row(key="wlc_before", value=before_focus)]
    sat_rows.extend(
        [
            _sat_row(key=label, value=value)
            for label, value in research_tms_report_wlc_word_format.build_wlc_word_rows(
                focus_placeholder,
                wlc_focus_notes,
            )
        ]
    )
    sat_rows.append(_sat_row(key="wlc_after", value=after_focus))

    sat_rows.extend(
        _center_sat_rows(
            row,
        )
    )
    sat_rows = _merge_assessment_rows_into_sat_middle_column(sat_rows)
    sat_rows = _move_assessment_values_to_sat_middle_column(sat_rows)

    table_rows: list[object] = [
        wlc_utils_html.table_row_of_headers(("value", "", "key"))
    ]
    for value, middle_description, key in sat_rows:
        table_rows.append(
            wlc_utils_html.table_row_of_data(
                (
                    research_tms_report_bracket_notes.annotate_bracket_note_tokens(
                        value
                    ),
                    middle_description,
                    key,
                ),
                tdattrs=(_sat_value_cell_attr(key, value), None, None),
            )
        )

    return wlc_utils_html.table(
        tuple(table_rows),
        {"class": "goerwitz-tms-sat"},
    )


def _sat_value_cell_attr(label: str, value: str) -> dict[str, str] | None:
    if label == research_tms_report_wlc_word_format.WLC_FOCUS_NOTES_LABEL:
        return {"style": "text-align: right;"}

    if (
        label in _CONTEXT_HBO_ROW_KEYS
        and research_tms_report_diff_format.contains_hebrew(value)
    ):
        return {"lang": "hbo", "dir": "rtl"}

    if label.startswith(
        "diff_wlc_"
    ) and research_tms_report_diff_format.is_plain_hebrew_string(value):
        return {"lang": "hbo", "dir": "rtl"}

    return None


def _center_sat_rows(
    row: dict[str, object],
) -> list[SatRow]:
    rows: list[SatRow] = []

    rows.extend(
        [
            _sat_row(key=label, value=value)
            for label, value in research_tms_report_diff_format.normalize_diff_rows(
                "diff_wlc_uxlc",
                row.get("diff_wlc_uxlc"),
                row=row,
                rhs_key="uxlc",
                render_sat_value=_render_sat_value,
                structured_text_lookup=_structured_text_value,
            )
        ]
    )
    rows.extend(
        [
            _sat_row(key=label, value=value)
            for label, value in research_tms_report_diff_format.normalize_diff_rows(
                "diff_wlc_mam",
                row.get("diff_wlc_mam"),
                row=row,
                rhs_key="mam_simple",
                render_sat_value=_render_sat_value,
                structured_text_lookup=_structured_text_value,
            )
        ]
    )

    assessment = _structured_text_value(row, "assessment")
    if isinstance(assessment, dict):
        for key in _ASSESSMENT_KEYS:
            value = assessment.get(key)
            if value is None:
                continue
            rows.append(_sat_row(key=f"a.{key}", value=_render_sat_value(value)))

    return _apply_sat_row_suppressions(_row_ref(row), rows)


def _render_comment_paragraphs(row: dict[str, object]) -> tuple[object, ...]:
    comment = _structured_text_value(row, "comment")
    if comment is None:
        return ()
    if not isinstance(comment, (list, tuple)):
        comment = [comment]
    return tuple(_render_comment_paragraph(comment_item) for comment_item in comment)


def _render_image_paragraphs(row: dict[str, object]) -> tuple[object, ...]:
    structured_text = row.get("structured_text")
    if not isinstance(structured_text, dict):
        return ()

    image_paragraphs = list(my_html_for_img.html_for_imgs(structured_text))
    if not image_paragraphs:
        return ()

    img_src_url = structured_text.get("img_src_url")
    if isinstance(img_src_url, str) and img_src_url.strip():
        link_label, location_suffix = _image_source_link_label_and_location_suffix(
            structured_text
        )
        source_contents: list[object] = [
            "Image source: ",
            wlc_utils_html.anchor(
                link_label,
                {"href": img_src_url.strip()},
            ),
        ]
        if location_suffix:
            source_contents.append(location_suffix)
        image_paragraphs.append(wlc_utils_html.para(tuple(source_contents)))

    return tuple(image_paragraphs)


def _image_source_link_label_and_location_suffix(
    structured_text: dict[str, object],
) -> tuple[str, str]:
    img_name = structured_text.get("img")
    if not isinstance(img_name, str):
        return "source", ""

    parsed = _parse_lc_image_name(img_name)
    if parsed is None:
        return "source", ""

    page_id, column, line = parsed
    return page_id, f" column {column} line {line}"


def _parse_lc_image_name(img_name: str) -> tuple[str, int, int] | None:
    match = _LC_IMAGE_NAME_RE.search(img_name)
    if match is None:
        return None

    page_id = match.group(1).upper()
    column = int(match.group(2))
    line = int(match.group(3))
    return page_id, column, line


def _render_comment_paragraph(comment: object) -> object:
    return wlc_utils_html.para(
        _comment_contents_with_hbo_spans(comment),
        {"class": "goerwitz-tms-comment"},
    )


def _comment_contents_with_hbo_spans(comment: object) -> object:
    if not isinstance(comment, str):
        return comment

    return _wrap_pointed_hebrew_substrings(comment)


def _wrap_pointed_hebrew_substrings(text: str) -> object:
    pieces: list[object] = []
    cursor = 0
    wrapped_any = False

    for match in _POINTED_HEBREW_SEGMENT_RE.finditer(text):
        start, end = match.span()
        if start > cursor:
            pieces.append(text[cursor:start])

        segment = match.group(0)
        if _is_pointed_hebrew_segment(segment):
            pieces.append(wlc_utils_html.span(segment, {"lang": "hbo"}))
            wrapped_any = True
        else:
            pieces.append(segment)

        cursor = end

    if cursor < len(text):
        pieces.append(text[cursor:])

    if not wrapped_any:
        return text
    if len(pieces) == 1:
        return pieces[0]
    return tuple(pieces)


def _is_pointed_hebrew_segment(text: str) -> bool:
    return bool(
        _HEBREW_LETTER_RE.search(text) and _HEBREW_POINTING_MARK_RE.search(text)
    )


def _apply_sat_row_suppressions(ref: str, rows: list[SatRow]) -> list[SatRow]:
    suppressed_labels = _SAT_ROW_SUPPRESSIONS_BY_REF.get(ref)
    if not suppressed_labels:
        return rows

    return [
        sat_row for sat_row in rows if _sat_row_key(sat_row) not in suppressed_labels
    ]


def _sat_row(*, key: str, value: str, middle_description: str = "") -> SatRow:
    return (value, middle_description, key)


def _sat_row_key(row: SatRow) -> str:
    return row[2]


def _move_assessment_values_to_sat_middle_column(rows: list[SatRow]) -> list[SatRow]:
    moved_rows: list[SatRow] = []
    for value, middle_description, key in rows:
        if key.startswith("a.") and value:
            moved_rows.append(
                _sat_row(
                    key=key,
                    value="",
                    middle_description=middle_description or value,
                )
            )
        else:
            moved_rows.append((value, middle_description, key))

    return moved_rows


def _sat_merge_target_key_for_assessment_key(key: str) -> str | None:
    return _SAT_A_KEY_MERGE_TARGETS.get(key)


def _sat_row_matches_merge_target(*, row_key: str, merge_target_base_key: str) -> bool:
    # Phase 1 scope: match either base key or base key.hbo.
    return row_key == merge_target_base_key or row_key == f"{merge_target_base_key}.hbo"


def _merge_assessment_rows_into_sat_middle_column(rows: list[SatRow]) -> list[SatRow]:
    merged_rows = list(rows)
    consumed_indices: set[int] = set()

    for row_idx, sat_row in enumerate(rows):
        row_key = _sat_row_key(sat_row)
        merge_target_base_key = _sat_merge_target_key_for_assessment_key(row_key)
        if merge_target_base_key is None:
            continue

        target_idx = _find_sat_merge_target_row_index(
            merged_rows,
            merge_target_base_key=merge_target_base_key,
        )
        if target_idx is None:
            continue

        assessment_value, _assessment_middle, _assessment_key = sat_row
        target_value, _target_middle, target_key = merged_rows[target_idx]

        if (
            _sat_assessment_value_describes_target_value(
                assessment_value=assessment_value,
                target_value=target_value,
            )
            is not True
        ):
            continue

        merged_rows[target_idx] = _sat_row(
            key=target_key,
            value=target_value,
            middle_description=assessment_value,
        )
        consumed_indices.add(row_idx)

    if not consumed_indices:
        return merged_rows

    return [
        sat_row
        for idx, sat_row in enumerate(merged_rows)
        if idx not in consumed_indices
    ]


def _find_sat_merge_target_row_index(
    rows: list[SatRow], *, merge_target_base_key: str
) -> int | None:
    preferred_keys = (f"{merge_target_base_key}.hbo", merge_target_base_key)

    for preferred_key in preferred_keys:
        for idx, sat_row in enumerate(rows):
            if _sat_row_key(sat_row) == preferred_key:
                return idx

    return None


def _sat_assessment_value_describes_target_value(
    *, assessment_value: str, target_value: str
) -> bool | None:
    assessment_text = assessment_value.strip()
    target_text = target_value.strip()
    if not assessment_text or not target_text:
        return None

    if not research_tms_report_diff_format.is_plain_hebrew_string(target_text):
        return None

    try:
        return troublemaker_structured_text_sanity.assessment_descriptor_matches_hebrew_token(
            assessment_descriptor=assessment_text,
            hebrew_token=target_text,
        )
    except (AssertionError, ValueError):
        # Descriptor inference failures are indeterminate for SAT merge purposes.
        return None


def _split_wlc_context(verse_text: str, wlc_focus: str | None) -> tuple[str, str, str]:
    if not wlc_focus:
        return verse_text, "", ""

    match_start = verse_text.find(wlc_focus)
    if match_start < 0:
        return verse_text, "", ""

    match_end = match_start + len(wlc_focus)
    before_focus = verse_text[:match_start].strip()
    after_focus = verse_text[match_end:].strip()
    return before_focus, wlc_focus, after_focus


def _wlc_verse_text(row: dict[str, object]) -> str:
    tokens = _wlc_verse_vels(row)
    text_parts = [_token_text(token) for token in tokens]
    compact = " ".join(part for part in text_parts if part)
    return " ".join(compact.split())


def _wlc_verse_vels(row: dict[str, object]) -> list[object]:
    wlc_verse = row.get("wlc422_kq_u_verse")
    if not isinstance(wlc_verse, dict):
        return []
    vels = wlc_verse.get("vels")
    if not isinstance(vels, list):
        return []
    return vels


def _token_text(token: object) -> str:
    if isinstance(token, str):
        return token

    if isinstance(token, dict):
        word = token.get("word")
        if isinstance(word, str):
            return word

        text = token.get("text")
        if isinstance(text, str):
            return text

    return _render_sat_value(token)


def _render_sat_value(value: object) -> str:
    if isinstance(value, str):
        return value

    if value is None:
        return ""

    if isinstance(value, list):
        rendered_items = [_render_sat_value(item) for item in value if item is not None]
        rendered_items = [item for item in rendered_items if item]
        if not rendered_items:
            return "[]"
        return f"[{' | '.join(rendered_items)}]"

    if isinstance(value, dict):
        token_like = _render_token_like_dict(value)
        if token_like is not None:
            return token_like

        parts = []
        for key, val in value.items():
            rendered = _render_sat_value(val)
            parts.append(f"{key}: {rendered}" if rendered else str(key))
        return "; ".join(parts)

    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value)


def _render_token_like_dict(value: dict[str, object]) -> str | None:
    token_text: str | None = None
    if isinstance(value.get("word"), str):
        token_text = str(value["word"])
    elif isinstance(value.get("text"), str):
        token_text = str(value["text"])

    if token_text is None:
        return None

    note_key: str | None = None
    if "notes" in value:
        note_key = "notes"
    elif "note" in value:
        note_key = "note"

    out = token_text
    if note_key is not None:
        note_text = _render_sat_value(value.get(note_key))
        if note_text:
            out = f"{out} ({note_key}: {note_text})"

    extras: list[str] = []
    for key, val in value.items():
        if key in {"word", "text", "notes", "note"}:
            continue
        rendered = _render_sat_value(val)
        extras.append(f"{key}: {rendered}" if rendered else str(key))

    if extras:
        out = f"{out} ({'; '.join(extras)})"

    return out


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
    # Reuse the parsing logic from research_tms to avoid drift.
    from accgram import research_tms

    bb, chnu, vrnu = research_tms._parse_ref(ref)
    bcv = research_tms._to_compact_bcv(bb, chnu, vrnu)
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
