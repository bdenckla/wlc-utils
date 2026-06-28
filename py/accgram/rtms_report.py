from __future__ import annotations

from pathlib import Path
from collections.abc import Callable

from accgram import rtmsr_media
from accgram import rtmsr_sat
from accgram import rtmsr_verse
from accgram import rtms_ref
from accgram.prose_ob_notes import get_structured_text
from cmn.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import bib_locales as tbn
from py_html import wlc_utils_html
from py_wlc import my_wlc_bcv_str

import repo_paths

_SELF_LINK_SYMBOL = "🔗"

StructuredTextLookup = Callable[[dict[str, object], str], object]


def expand_uxlc_change_ref(compact: object) -> object:
    """Expand a compact UXLC change ref to its full tanach.us URL.

    Compact form "2026.10.19/2026.04.10-7" (release/changeset-n) becomes
    "https://tanach.us/Changes/2026.10.19%20-%20Changes/2026.10.19%20-%20Changes.xml?2026.04.10-7".
    Non-strings and values that already look like URLs are returned unchanged.
    """
    if not isinstance(compact, str):
        return compact
    ref = compact.strip()
    if not ref or ref.startswith("http"):
        return compact
    release, sep, changeset_n = ref.partition("/")
    if not sep:
        return compact
    folder = f"{release}%20-%20Changes"
    return f"https://tanach.us/Changes/{folder}/{folder}.xml?{changeset_n}"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "goerwitz.html"


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


def path_to_gh_pages_style(html_out_path: Path) -> str:
    return _path_to_gh_pages_style(html_out_path)


def render_row_section_with_anchor_id(
    row: dict[str, object],
    *,
    section_anchor_id: str,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    return _render_row_section_with_anchor_id(
        row,
        section_anchor_id=section_anchor_id,
        structured_text_lookup=structured_text_lookup,
    )


def _render_row_section_with_anchor_id(
    row: dict[str, object],
    *,
    section_anchor_id: str,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    ref = _row_ref(row)
    bb, chnu, vrnu, bcv = parse_ref_to_wlc_bcv(ref)

    section_items: list[object] = [
        wlc_utils_html.heading_level_2(ref, {"id": section_anchor_id}),
        *_render_ref_links(
            bb=bb,
            chnu=chnu,
            vrnu=vrnu,
            bcv=bcv,
            row=row,
            section_anchor_id=section_anchor_id,
            structured_text_lookup=structured_text_lookup,
        ),
        *_render_verse_paragraphs(row, structured_text_lookup=structured_text_lookup),
        _render_sat_table(row, structured_text_lookup=structured_text_lookup),
        *_render_image_paragraphs(row, structured_text_lookup=structured_text_lookup),
        *_render_comment_paragraphs(
            row,
            structured_text_lookup=structured_text_lookup,
        ),
    ]
    return tuple(section_items)


def _render_ref_links(
    bb: str,
    chnu: int,
    vrnu: int,
    bcv: str,
    row: dict[str, object],
    section_anchor_id: str,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    mam_url = _mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)
    tanach_us_url = my_wlc_bcv_str.get_tanach_dot_us_url(bcv)
    summary = structured_text_lookup(row, "st-summary")
    uxlc_change = expand_uxlc_change_ref(structured_text_lookup(row, "uxlc_change"))
    pending_uxlc_change = expand_uxlc_change_ref(
        structured_text_lookup(row, "pending_uxlc_change")
    )
    uxlc_note_page = structured_text_lookup(row, "uxlc_note_page")
    github_issue = structured_text_lookup(row, "github-issue")

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
        wlc_utils_html.anchor("Mwd", {"href": mam_url}),
        " | ",
        wlc_utils_html.anchor("UXLC", {"href": tanach_us_url}),
    ]

    for label, url in [
        ("UXLC change", uxlc_change),
        ("Pending UXLC change", pending_uxlc_change),
        ("UXLC note page", uxlc_note_page),
        ("GitHub issue", github_issue),
    ]:
        if isinstance(url, str) and url.strip():
            links.extend([" | ", wlc_utils_html.anchor(label, {"href": url.strip()})])

    return (
        wlc_utils_html.para(tuple(permalink_summary)),
        wlc_utils_html.para(tuple(links)),
    )


def _render_sat_table(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> object:
    return rtmsr_sat.render_sat_table(
        row,
        row_ref=_row_ref(row),
        structured_text_lookup=structured_text_lookup,
        wlc_tokens=rtmsr_verse.wlc_verse_vels(row),
    )


def _render_comment_paragraphs(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    return rtmsr_media.render_comment_paragraphs(
        row,
        structured_text_lookup=structured_text_lookup,
    )


def _render_image_paragraphs(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    return rtmsr_media.render_image_paragraphs(
        row,
        structured_text_lookup=structured_text_lookup,
    )


def _render_verse_paragraphs(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    # Dually-cantillated verses (issue #36) show one labelled line per reading
    # (e.g. taḥton + elyon) in place of the single combined WLC verse line.
    readings = row.get("dual_cant_readings")
    if isinstance(readings, list) and readings:
        return rtmsr_verse.render_dual_cant_reading_paragraphs(readings)
    return (_render_wlc_verse_paragraph(row, structured_text_lookup=structured_text_lookup),)


def _render_wlc_verse_paragraph(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> object:
    return rtmsr_verse.render_wlc_verse_paragraph(
        row,
        structured_text_lookup=structured_text_lookup,
    )


def structured_text_value(row: dict[str, object], key: str) -> object:
    ref = _row_ref(row)
    structured_text = get_structured_text().get(ref)
    if not isinstance(structured_text, dict):
        return None
    return structured_text.get(key)


def _row_ref(row: dict[str, object]) -> str:
    ref = row.get("ref")
    if not isinstance(ref, str) or not ref.strip():
        raise ValueError("Troublemaker row is missing non-empty string field 'ref'")
    return ref.strip()


def parse_ref_to_wlc_bcv(ref: str) -> tuple[str, int, int, str]:
    bb, chnu, vrnu = rtms_ref.parse_ref(ref)
    bcv = rtms_ref.to_compact_bcv(bb, chnu, vrnu)
    return bb, chnu, vrnu, bcv


def mam_with_doc_url(*, bb: str, chnu: int, vrnu: int) -> str:
    """Public MAM-with-doc verse URL, shared with the poetic oddball report."""
    return _mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)


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
            return ancestor.parent / "gh-pages" / "accgram" / "goerwitz.html"

    parent = out_path.parent
    if parent != out_path:
        return parent / "gh-pages" / "accgram" / "goerwitz.html"

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
