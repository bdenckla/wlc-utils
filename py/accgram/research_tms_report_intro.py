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


def build_intro_contents(row_count: int) -> tuple[object, ...]:
    intro_text = (
        f"These {row_count} verses caused trouble for the Goerwitz accent grammar checker."
        " Potential causes of this trouble include WLC quirks, LC quirks, and checker quirks."
        " The checker is described in the following article:"
    )
    citation_text = (
        f"{_GC_AUTHOR}. ‹{_GC_TITLE}.›" f" In {_GC_BOOK_TITLE} (pp. {_GC_PAGES}). (",
        wlc_utils_html.anchor(_GC_SERIES, {"href": _GC_BOOK_URL}),
        f"). The Oriental Institute, Chicago, {_GC_YEAR}. ISBN {_GC_ISBN}.",
    )

    return (
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(intro_text),
        wlc_utils_html.para(citation_text),
    )
