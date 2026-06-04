from __future__ import annotations

import re
from collections.abc import Callable

from py_html import my_html_for_img
from py_html import wlc_utils_html

_GOERWITZ_TMS_IMAGE_CLASS = "goerwitz-tms-image"
_GOERWITZ_TMS_FIGURE_CLASS = "goerwitz-tms-figure"
_GOERWITZ_TMS_IMAGE_CAPTION_CLASS = "goerwitz-tms-image-caption"

_POINTED_HEBREW_SEGMENT_RE = re.compile(r"[\u0590-\u05FF]+")
_HEBREW_POINTING_MARK_RE = re.compile(r"[\u0591-\u05C7]")
_HEBREW_LETTER_RE = re.compile(r"[\u05D0-\u05EA]")
_LC_IMAGE_NAME_RE = re.compile(r"LC-([0-9]+[A-Za-z])-col-([0-9]+)-line-([0-9]+)")

StructuredTextLookup = Callable[[dict[str, object], str], object]


def render_comment_paragraphs(
    row: dict[str, object],
    *,
    structured_text_lookup: StructuredTextLookup,
) -> tuple[object, ...]:
    comment = structured_text_lookup(row, "comment")
    if comment is None:
        return ()
    if not isinstance(comment, (list, tuple)):
        comment = [comment]
    return tuple(_render_comment_paragraph(comment_item) for comment_item in comment)


def render_image_paragraphs(row: dict[str, object]) -> tuple[object, ...]:
    structured_text = row.get("structured_text")
    if not isinstance(structured_text, dict):
        return ()

    image_paragraphs = list(
        my_html_for_img.html_for_imgs(
            structured_text,
            img_para_attr={"class": _GOERWITZ_TMS_IMAGE_CLASS},
        )
    )
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
        source_caption = wlc_utils_html.figcaption(
            tuple(source_contents),
            {"class": _GOERWITZ_TMS_IMAGE_CAPTION_CLASS},
        )
        image_paragraphs[-1] = wlc_utils_html.figure(
            (image_paragraphs[-1], source_caption),
            {"class": _GOERWITZ_TMS_FIGURE_CLASS},
        )

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
