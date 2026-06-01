from __future__ import annotations

import json
from pathlib import Path

from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import bib_locales as tbn
from py_html import wlc_utils_html
from py_wlc import my_wlc_bcv_str


_ASSESSMENT_KEYS = ("manuscript", "bhs", "wlc", "uxlc", "consensus")


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
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    body_contents = _build_body_contents(enriched_rows)
    write_ctx = wlc_utils_html.WriteCtx(
        title="Goerwitz TMS",
        path=str(html_out_path),
    )
    wlc_utils_html.write_html_to_file(
        body_contents=body_contents,
        write_ctx=write_ctx,
        path_to_style=_path_to_gh_pages_style(html_out_path),
    )


def _build_body_contents(enriched_rows: list[dict[str, object]]) -> tuple[object, ...]:
    sections: list[object] = [
        wlc_utils_html.heading_level_1("Goerwitz Troublemakers (research-tms)"),
        wlc_utils_html.para(f"Rows: {len(enriched_rows)}"),
    ]

    for index, row in enumerate(enriched_rows):
        sections.extend(_render_row_section(row))
        if index + 1 < len(enriched_rows):
            sections.append(wlc_utils_html.horizontal_rule())

    return tuple(sections)


def _render_row_section(row: dict[str, object]) -> tuple[object, ...]:
    ref = _row_ref(row)
    bb, chnu, vrnu, bcv = _parse_ref_to_wlc_bcv(ref)

    section_items: list[object] = [
        wlc_utils_html.heading_level_2(ref),
        _render_ref_links(bb=bb, chnu=chnu, vrnu=vrnu, bcv=bcv, row=row),
        _render_sat_table(row),
    ]
    return tuple(section_items)


def _render_ref_links(
    bb: str,
    chnu: int,
    vrnu: int,
    bcv: str,
    row: dict[str, object],
) -> object:
    mam_url = _mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)
    tanach_us_url = my_wlc_bcv_str.get_tanach_dot_us_url(bcv)

    uxlc_change_node: object
    uxlc_change = _structured_text_value(row, "uxlc_change")
    if isinstance(uxlc_change, str) and uxlc_change.strip():
        uxlc_change_node = wlc_utils_html.anchor(
            "structured_text.uxlc_change",
            {"href": uxlc_change.strip()},
        )
    else:
        uxlc_change_node = "structured_text.uxlc_change: none"

    return wlc_utils_html.para(
        (
            wlc_utils_html.anchor("MAM-with-doc verse", {"href": mam_url}),
            " | ",
            wlc_utils_html.anchor("tanach.us verse", {"href": tanach_us_url}),
            " | ",
            uxlc_change_node,
        )
    )


def _render_sat_table(row: dict[str, object]) -> object:
    verse_text = _wlc_verse_text(row)
    wlc_word = _structured_text_value(row, "wlc_word")
    before_word, woi_placeholder, after_word = _split_wlc_context(
        verse_text=verse_text,
        wlc_word=wlc_word if isinstance(wlc_word, str) else None,
    )

    center_rows = _center_sat_rows(row, woi_placeholder)
    inner_rows: list[object] = [wlc_utils_html.table_row_of_headers(("key", "value"))]
    inner_rows.extend(
        wlc_utils_html.table_row_of_data((label, value)) for label, value in center_rows
    )
    inner_table = wlc_utils_html.table(tuple(inner_rows), {"class": "goerwitz-tms-center"})

    return wlc_utils_html.table(
        (
            wlc_utils_html.table_row_of_headers(("before", "SAT", "after")),
            wlc_utils_html.table_row(
                (
                    wlc_utils_html.table_datum(before_word),
                    wlc_utils_html.table_datum(inner_table),
                    wlc_utils_html.table_datum(after_word),
                )
            ),
        ),
        {"class": "goerwitz-tms-sat"},
    )


def _center_sat_rows(row: dict[str, object], woi_placeholder: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [("wlc_word", woi_placeholder)]

    bracket_notes = _collect_bracket_notes(row)
    if bracket_notes:
        rows.append(("bracket_notes", " | ".join(bracket_notes)))

    rows.extend(_normalize_diff_rows("diff_wlc_uxlc", row.get("diff_wlc_uxlc")))
    rows.extend(_normalize_diff_rows("diff_wlc_mam", row.get("diff_wlc_mam")))

    assessment = _structured_text_value(row, "assessment")
    if isinstance(assessment, dict):
        for key in _ASSESSMENT_KEYS:
            value = assessment.get(key)
            if value is None:
                continue
            rows.append((f"assessment.{key}", _render_sat_value(value)))

    free_form_comment = _structured_text_value(row, "free_form_comment")
    if isinstance(free_form_comment, list):
        for idx, comment in enumerate(free_form_comment, start=1):
            rows.append((f"free_form_comment[{idx}]", _render_sat_value(comment)))
    elif free_form_comment is not None:
        rows.append(("free_form_comment", _render_sat_value(free_form_comment)))

    return rows


def _normalize_diff_rows(label: str, diff_value: object) -> list[tuple[str, str]]:
    entries = _as_nonempty_list(diff_value)
    rows: list[tuple[str, str]] = []
    for idx, entry in enumerate(entries, start=1):
        row_label = label if len(entries) == 1 else f"{label}[{idx}]"
        rows.append((row_label, _render_sat_value(entry)))
    return rows


def _as_nonempty_list(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return [item for item in value if item is not None]
    return [value]


def _collect_bracket_notes(row: dict[str, object]) -> list[str]:
    notes: list[str] = []

    for token in _wlc_verse_vels(row):
        if not isinstance(token, dict):
            continue
        token_notes = token.get("notes")
        if token_notes is None:
            continue
        word = token.get("word")
        rendered_notes = _render_sat_value(token_notes)
        if isinstance(word, str) and word:
            notes.append(f"{word}: {rendered_notes}")
        else:
            notes.append(rendered_notes)

    for diff_label in ("diff_wlc_uxlc", "diff_wlc_mam"):
        for entry in _as_nonempty_list(row.get(diff_label)):
            if not isinstance(entry, dict):
                continue
            for key in ("wlc_adds_notes", "uxlc_adds_note"):
                if key in entry:
                    notes.append(f"{diff_label}.{key}: {_render_sat_value(entry[key])}")

    # Preserve order while dropping duplicates.
    return list(dict.fromkeys(notes))


def _split_wlc_context(verse_text: str, wlc_word: str | None) -> tuple[str, str, str]:
    if not wlc_word:
        return verse_text, "", ""

    match_start = verse_text.find(wlc_word)
    if match_start < 0:
        return verse_text, "", ""

    match_end = match_start + len(wlc_word)
    before_word = verse_text[:match_start].strip()
    after_word = verse_text[match_end:].strip()
    return before_word, wlc_word, after_word


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
        rendered = ", ".join(_render_sat_value(item) for item in value)
        return f"[{rendered}]"

    if isinstance(value, dict):
        parts = [f"{key}: {_render_sat_value(val)}" for key, val in value.items()]
        return "; ".join(parts)

    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        return str(value)


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
    # Reuse the parsing logic from research_troublemakers to avoid drift.
    from accgram import research_troublemakers

    bb, chnu, vrnu = research_troublemakers._parse_ref(ref)
    bcv = research_troublemakers._to_compact_bcv(bb, chnu, vrnu)
    return bb, chnu, vrnu, bcv


def _mam_with_doc_url(bb: str, chnu: int, vrnu: int) -> str:
    bk39id = wlc_bb_to_bk39id(bb)
    osdf = tbn.ordered_short_dash_full_39(bk39id)
    return f"https://bdenckla.github.io/MAM-with-doc/{osdf}.html#c{chnu}v{vrnu}"


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