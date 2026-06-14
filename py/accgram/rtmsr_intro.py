from __future__ import annotations

from accgram import rtmsr_bracket_notes
from py_html import wlc_utils_html

_GC_AUTHOR = "Goerwitz, Richard"
_GC_TITLE = (
    "A New Masoretic “Spell Checker” or A Fast, Practical Method For Checking "
    "the Accentual Structure and Integrity Of Tiberian-Pointed Biblical Texts"
)
_GC_BOOK_TITLE = (
    "Studies in Semitic and Afroasiatic Linguistics Presented to Gene B. Gragg"
)
_GC_SERIES = "Studies in Ancient Oriental Civilization 60"
_GC_PAGES = "111-122"
_GC_YEAR = "2007"
_GC_ISBN = "978-1-885923-41-7"
_GC_BOOK_URL = (
    "https://isac.uchicago.edu/research/publications/saoc/"
    "saoc-60-studies-semitic-and-afroasiatic-linguistics-presented-gene-b"
)


def build_intro_contents(
    oddball_count: int,
) -> tuple[object, ...]:
    intro_text = (
        f"This page lists the {oddball_count} WLC 4.22 verses that the Goerwitz accent"
        " grammar checker, run via the PLY port, does not parse cleanly. Use the filter"
        " below to narrow the list."
    )
    oddballs_text = (
        f"These {oddball_count} verses are parsed by the PLY port into a tree"
        " containing the string \u201cERROR\u201d; each oddball section includes its"
        " complete parse tree. Potential causes include"
        " WLC quirks,"
        " BHS quirks,"
        " LC quirks, and"
        " checker quirks."
    )
    msp_text = "The filter sorts each verse into one of four categories:"
    msp_categories = (
        "“missing sof pasuq”",
        "“missing silluq,” where a sof pasuq is present"
        " but the verse-final word has no accent",
        "“zarqa whim,” where WLC turns a scribal zarqa whim into an outright error",
        "“other,” for everything else",
    )
    and_text = (
        "Two further toggles narrow the list, each ANDed with the category:"
        " whether the verse has a UXLC change, and"
        " whether its table displays a WLC bracket-note."
        " Each toggle is three-state: has, doesn’t have, or don’t care"
        " (the default)."
    )
    bracket_notes_text = (
        "We define the bracket-note codes in the ",
        wlc_utils_html.anchor(
            rtmsr_bracket_notes.WLC_BRACKET_NOTES_HEADING,
            {"href": f"#{rtmsr_bracket_notes.WLC_BRACKET_NOTES_ANCHOR_ID}"},
        ),
        " section at the end of this page, but you can also hover over"
        " their use in any verse to see these definitions.",
    )

    return (
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(intro_text),
        wlc_utils_html.para(oddballs_text),
        wlc_utils_html.para(msp_text),
        wlc_utils_html.unordered_list(msp_categories),
        wlc_utils_html.para(and_text),
        wlc_utils_html.para(bracket_notes_text),
    )


def checker_article_citation_contents() -> tuple[object, ...]:
    citation_text = (
        f"{_GC_AUTHOR}. ‹{_GC_TITLE}.›" f" In {_GC_BOOK_TITLE} (pp. {_GC_PAGES}). (",
        wlc_utils_html.anchor(_GC_SERIES, {"href": _GC_BOOK_URL}),
        f"). The Oriental Institute, Chicago, {_GC_YEAR}. ISBN {_GC_ISBN}.",
    )
    return (
        wlc_utils_html.para(
            "The Goerwitz accent grammar checker is described in the following article:"
        ),
        wlc_utils_html.para(citation_text),
    )
