from __future__ import annotations

from py_html import wlc_utils_html

_GOERWITZ_CITATION_AUTHOR = "Goerwitz, Richard"
_GOERWITZ_CITATION_TITLE = (
    "A New Masoretic \"Spell Checker\" or A Fast, Practical Method For Checking "
    "the Accentual Structure and Integrity Of Tiberian-Pointed Biblical Texts"
)
_GOERWITZ_CITATION_BOOK_TITLE = (
    "Studies in semitic and afroasiatic linguistics presented to Gene B. Gragg"
)
_GOERWITZ_CITATION_SERIES = "Studies in Ancient Oriental Civilization 60"
_GOERWITZ_CITATION_PAGES = "111-122"
_GOERWITZ_CITATION_YEAR = "2007"
_GOERWITZ_CITATION_ISBN = "978-1-885923-41-7"
_GOERWITZ_CITATION_BOOK_URL = (
    "https://isac.uchicago.edu/research/publications/saoc/"
    "saoc-60-studies-semitic-and-afroasiatic-linguistics-presented-gene-b"
)


def build_intro_contents(row_count: int) -> tuple[object, ...]:
    intro_text = (
        f"These {row_count} verses were flagged by the Goerwitz accent grammar checker. "
        "Potential causes include WLC quirks, LC quirks, and checker quirks, so each "
        "entry should be reviewed with context before drawing conclusions."
    )
    citation_text = (
        f"{_GOERWITZ_CITATION_AUTHOR}. \"{_GOERWITZ_CITATION_TITLE}.\" "
        f"In {_GOERWITZ_CITATION_BOOK_TITLE} (pp. {_GOERWITZ_CITATION_PAGES}). "
        f"Ringgold, Chicago, {_GOERWITZ_CITATION_YEAR}. ISBN {_GOERWITZ_CITATION_ISBN}."
    )

    return (
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(intro_text),
        wlc_utils_html.blockquote(
            (
                wlc_utils_html.para(citation_text),
                wlc_utils_html.para(
                    (
                        f"Series: {_GOERWITZ_CITATION_SERIES}",
                        wlc_utils_html.line_break2(),
                        wlc_utils_html.anchor(
                            _GOERWITZ_CITATION_BOOK_URL,
                            {"href": _GOERWITZ_CITATION_BOOK_URL},
                        ),
                    )
                ),
            )
        ),
    )
