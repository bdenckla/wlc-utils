from __future__ import annotations

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
    troublemaker_count: int,
    oddball_count: int,
) -> tuple[object, ...]:
    total = troublemaker_count + oddball_count
    intro_text = (
        f"This page lists the {total} WLC 4.22 verses that the Goerwitz accent grammar"
        " checker, run via the PLY port, does not parse cleanly. Use the filters below"
        " to narrow the list along two dimensions."
    )
    troublemakers_text = (
        f"Troublemakers ({troublemaker_count} verses) produce no output even under the"
        " PLY port. Potential causes of this trouble include WLC quirks, LC quirks, and"
        " checker quirks."
    )
    oddballs_text = (
        f"Oddballs ({oddball_count} verses) are parsed by the PLY port into a tree"
        " containing the string \u201cERROR\u201d; each oddball section includes its"
        " complete parse tree."
    )
    msp_text = (
        "The second dimension is whether a sof pasuq is missing somewhere in the"
        " LC-BHS-WLC pipeline (msp-y) or not (msp-n)."
    )

    return (
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(intro_text),
        wlc_utils_html.para(troublemakers_text),
        wlc_utils_html.para(oddballs_text),
        wlc_utils_html.para(msp_text),
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
