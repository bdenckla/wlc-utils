from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from accgram import ob_error_context
from accgram import ob_report
from accgram import rtms_missing_sof_pasuq_descriptions
from accgram import rtms_ref
from accgram import rtms_report
from accgram import rtmsr_bracket_notes
from accgram import rtmsr_intro
from accgram import rtmsr_sat
from accgram import rtmsr_subsets
from accgram import rtmsr_verse
from mb_cmn import provenance
from py_html import wlc_utils_html

_REPORT_TITLE = "Goerwitz Run on WLC"
_REPORT_HEADING = "Goerwitz Run on WLC"
_WIDTH_CLASS = "goerwitz-tms-width-limited"
_FILTER_SCRIPT_NAME = "goerwitz-filter.js"

StructuredTextLookup = Callable[[dict[str, object], str], object]


@dataclass
class _Entry:
    """One oddball verse on the page, tagged along the filter dimensions."""

    ref: str
    # "msp" (missing sof pasuq), "msl" (missing silluq), "zwhim" (zarqa whim),
    # or "other"
    category: str
    # Independent boolean dimensions, ANDed with the category filter.
    has_uxlc_change: bool  # the verse has a "UXLC change" link
    has_wlc_note: bool  # the verse's SAT table displays a WLC bracket-note
    anchor_id: str
    structured_text_lookup: StructuredTextLookup
    row: dict[str, object]
    error_tree: ob_error_context.ErrorTree | None


def write_goerwitz_combined_html_report(
    main_html_out_path: Path,
    enriched_oddball_rows: list[dict[str, object]],
    base_dir: Path | None,
) -> Path:
    """Write goerwitz.html: every oddball verse in one flat,
    client-side-filterable list (see goerwitz-filter.js)."""
    html_out_path = rtmsr_subsets.overview_html_out_path(main_html_out_path)
    html_out_path.parent.mkdir(parents=True, exist_ok=True)

    error_trees_by_ref: dict[str, ob_error_context.ErrorTree | None] = {}
    if enriched_oddball_rows and isinstance(base_dir, Path):
        error_trees_by_ref = ob_error_context.collect_error_trees_by_ref(
            enriched_oddball_rows, base_dir
        )

    entries = _build_entries(enriched_oddball_rows, error_trees_by_ref)
    body_contents = _build_body_contents(entries)

    wlc_utils_html.write_html_to_file(
        body_contents=body_contents,
        write_ctx=wlc_utils_html.WriteCtx(
            title=_REPORT_TITLE,
            path=str(html_out_path),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out_path),
    )
    return html_out_path


def _build_entries(
    enriched_oddball_rows: list[dict[str, object]],
    error_trees_by_ref: dict[str, ob_error_context.ErrorTree | None],
) -> list[_Entry]:
    entries: list[_Entry] = []

    for row in enriched_oddball_rows:
        ref = _row_ref(row)
        bcv = ob_report.ref_bcv(ref)
        structured_text = ob_report.structured_text_dict(row)
        entries.append(
            _Entry(
                ref=ref,
                category=_category(row, structured_text),
                has_uxlc_change=_has_uxlc_change(structured_text),
                has_wlc_note=_has_wlc_note(row, ref),
                anchor_id=ob_report.oddball_anchor_id(bcv),
                structured_text_lookup=ob_report.structured_text_value,
                row=row,
                error_tree=error_trees_by_ref.get(ref),
            )
        )

    entries.sort(key=lambda entry: rtms_ref.reading_order_key(entry.ref))
    return entries


def _category(row: dict[str, object], structured_text: object) -> str:
    return rtms_missing_sof_pasuq_descriptions.row_category(
        row, structured_text=structured_text
    )


def _has_uxlc_change(structured_text: object) -> bool:
    # Counts either a landed "UXLC change" or a "Pending UXLC change" link.
    if not isinstance(structured_text, dict):
        return False
    return any(
        isinstance(value := structured_text.get(key), str) and bool(value.strip())
        for key in ("uxlc_change", "pending_uxlc_change")
    )


def _has_wlc_note(row: dict[str, object], ref: str) -> bool:
    # Only bracket notes the verse's SAT table actually displays count, so the
    # flag agrees with the visible "]"-spans (not notes on undisplayed words).
    return rtmsr_sat.row_has_rendered_bracket_note(
        row,
        row_ref=ref,
        structured_text_lookup=ob_report.structured_text_value,
        wlc_tokens=rtmsr_verse.wlc_verse_vels(row),
    )


def _build_body_contents(entries: list[_Entry]) -> tuple[object, ...]:
    counts = _counts(entries)
    all_rows = [entry.row for entry in entries]

    sections: list[object] = [
        wlc_utils_html.heading_level_1(_REPORT_HEADING),
        *rtmsr_intro.build_intro_contents(counts["total"]),
        *rtmsr_intro.checker_article_citation_contents(),
        *rtmsr_bracket_notes.build_wlc_bracket_notes_section(all_rows),
        _build_filter_controls(counts),
    ]

    for index, entry in enumerate(entries):
        sections.append(_render_verse_section(entry, is_first=index == 0))

    wrapper = wlc_utils_html.div(tuple(sections), {"class": _WIDTH_CLASS})
    script = wlc_utils_html.htel_mk("script", {"src": _FILTER_SCRIPT_NAME})
    return (wrapper, script)


def _render_verse_section(entry: _Entry, *, is_first: bool) -> object:
    inner = list(
        rtms_report.render_row_section_with_anchor_id(
            entry.row,
            section_anchor_id=entry.anchor_id,
            structured_text_lookup=entry.structured_text_lookup,
        )
    )
    inner.extend(
        ob_report.render_error_context_section(
            entry.row, error_tree=entry.error_tree
        )
    )

    items: list[object] = []
    # The separating rule lives inside the section (omitted on the first one) so it
    # hides with its verse when the filter removes it.
    if not is_first:
        items.append(wlc_utils_html.horizontal_rule())
    items.extend(inner)

    return wlc_utils_html.htel_mk(
        "section",
        {
            "class": "goerwitz-verse",
            "data-category": entry.category,
            "data-uchange": _flag_attr(entry.has_uxlc_change),
            "data-wnote": _flag_attr(entry.has_wlc_note),
        },
        tuple(items),
    )


def _flag_attr(value: bool) -> str:
    return "1" if value else "0"


def _build_filter_controls(counts: dict[str, int]) -> object:
    total = counts["total"]
    category_fieldset = _fieldset(
        "Category",
        (
            _checkbox(
                "gf-category", "msp", f"missing sof pasuq ({counts['msp']})"
            ),
            _checkbox("gf-category", "msl", f"missing silluq ({counts['msl']})"),
            _checkbox("gf-category", "zwhim", f"zarqa whim ({counts['zwhim']})"),
            _checkbox("gf-category", "other", f"other ({counts['other']})"),
        ),
    )
    uchange_fieldset = _tristate_fieldset(
        "UXLC change", "gf-uchange", counts["uchange_has"], total
    )
    wnote_fieldset = _tristate_fieldset(
        "WLC bracket-note", "gf-wnote", counts["wnote_has"], total
    )
    count_para = wlc_utils_html.para("", {"class": "gf-count"})
    return wlc_utils_html.div(
        (category_fieldset, uchange_fieldset, wnote_fieldset, count_para),
        {"class": "goerwitz-filter"},
    )


def _fieldset(legend_text: str, labels: tuple[object, ...]) -> object:
    legend = wlc_utils_html.htel_mk("legend", None, legend_text)
    return wlc_utils_html.htel_mk("fieldset", None, (legend, *labels))


def _tristate_fieldset(
    legend_text: str, group_name: str, has_count: int, total: int
) -> object:
    """A has / doesn't-have / don't-care radio group, ANDed with the category
    filter. Defaults to "don't care" so the page opens unfiltered on this axis.

    The "has"/"doesn't have" counts are wrapped in spans the filter script
    recomputes live, restricting to the verses passing the other filters (see
    goerwitz-filter.js). The numbers written here are the no-JS fallback."""
    return _fieldset(
        legend_text,
        (
            _radio_with_count(
                group_name, "yes", "has", has_count, f"{group_name}-has-count"
            ),
            _radio_with_count(
                group_name,
                "no",
                "doesn't have",
                total - has_count,
                f"{group_name}-no-count",
            ),
            _radio(group_name, "any", "don't care", checked=True),
        ),
    )


def _checkbox(css_class: str, value: str, label_text: str) -> object:
    input_el = wlc_utils_html.htel_mk_inline_nc(
        "input",
        {
            "type": "checkbox",
            "class": css_class,
            "value": value,
            "checked": "checked",
        },
    )
    return wlc_utils_html.htel_mk_inline("label", None, (input_el, f" {label_text}"))


def _radio(
    group_name: str, value: str, label_text: str, *, checked: bool
) -> object:
    input_el = _radio_input(group_name, value, checked=checked)
    return wlc_utils_html.htel_mk_inline("label", None, (input_el, f" {label_text}"))


def _radio_with_count(
    group_name: str, value: str, prefix_text: str, count: int, count_class: str
) -> object:
    """A radio whose label ends in a "(N)" count the filter script keeps live."""
    input_el = _radio_input(group_name, value, checked=False)
    count_span = wlc_utils_html.span_c(str(count), count_class)
    return wlc_utils_html.htel_mk_inline(
        "label", None, (input_el, f" {prefix_text} (", count_span, ")")
    )


def _radio_input(group_name: str, value: str, *, checked: bool) -> object:
    attrs: dict[str, str] = {
        "type": "radio",
        "class": group_name,
        "name": group_name,
        "value": value,
    }
    if checked:
        attrs["checked"] = "checked"
    return wlc_utils_html.htel_mk_inline_nc("input", attrs)


def _counts(entries: list[_Entry]) -> dict[str, int]:
    counts = {
        "msp": 0,
        "msl": 0,
        "zwhim": 0,
        "other": 0,
        "uchange_has": 0,
        "wnote_has": 0,
        "total": len(entries),
    }
    for entry in entries:
        counts[entry.category] += 1
        if entry.has_uxlc_change:
            counts["uchange_has"] += 1
        if entry.has_wlc_note:
            counts["wnote_has"] += 1
    return counts


def _row_ref(row: dict[str, object]) -> str:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Row is missing non-empty string field 'ref'")
    return ref.strip()
