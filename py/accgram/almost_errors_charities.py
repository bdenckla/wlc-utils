"""The "Editorial charities" section of the "almost errors" page.

The charities the checker quietly applies: a prose geresh muqdam read as a plain
geresh, and a stray poetic geresh promoted into a revia mugrash (Psalms 124:4).
Pure prose -- no parse trees -- so this module needs only the shared link helpers.
"""

from __future__ import annotations

from accgram.almost_errors_html_shared import _link, _uxlc_change_link
from py_html import wlc_utils_html as H


def _charities_intro() -> tuple[object, ...]:
    return (
        H.heading_level_2("Editorial charities"),
        H.para(
            "Each charity below names what the checker normalizes, the direction, and"
            " why, with a citation. Both reinterpret a mark the manuscript should not"
            " have here — a prose geresh muqdam read as a plain geresh, and a stray"
            " poetic geresh promoted into a revia mugrash."
        ),
    )


def _geresh_muqdam_section() -> tuple[object, ...]:
    return (
        H.heading_level_3("Geresh muqdam → geresh (prose)"),
        H.para(
            (
                "Geresh muqdam (U+059D) is a poetic-only sign. In the 21 prose books"
                " WLC uses it just twice — Lev. 1:3 (alone) and 2 Kings 17:13 —"
                " as a typographic device standing in for"
                " a plain geresh. The checker reads it as a plain geresh, so the prose"
                " grammar (which has no geresh muqdam) sees the geresh it expects."
                " Direction: poetic-looking sign → its prose counterpart. tanach.us"
                " itself made the same correction in both verses — changes ",
                _uxlc_change_link("2020.10.19/2020.09.22-1"),
                " (Lev. 1:3) and ",
                _uxlc_change_link("2020.10.19/2020.09.22-2"),
                " (2 Kings 17:13), each described “Change geresh muqdam to geresh.”",
            )
        ),
        H.para(
            (
                "The two verses differ in what happens next. In Lev. 1:3 the"
                " geresh muqdam stands alone, so the charity is the whole story. In 2"
                " Kings 17:13 the converted geresh then sits on a word that also carries"
                " a telisha gedola — so once the charity has run, what remains is one of"
                " the telisha gedola + geresh oddities below (the only one of those five"
                " whose geresh reaches the checker by way of a charity).",
            )
        ),
    )


def _ps124_section() -> tuple[object, ...]:
    return (
        H.heading_level_3("Plain geresh → revia mugrash (poetic): Psalms 124:4"),
        H.para(
            (
                "A plain geresh in a poetic verse is otherwise a lexical"
                " error: the poetic grammar has no plain geresh. The sole charitable"
                " exception is Psalms 124:4, where a revia and a plain geresh share"
                " one letter. There the"
                " checker reads the pair charitably as a single revia mugrash — the"
                " established poetic compound — by normalizing the two same-letter"
                " marks into order (revia + geresh → geresh + revia) and promoting the"
                " plain geresh to geresh muqdam, so the existing geresh muqdam + revia"
                " → revia mugrash rule consumes both as one token.",
            )
        ),
        H.para(
            (
                "This within-letter order normalization is licit precisely because it"
                " stays within a single letter — we are liberal about mark order on one"
                " letter (questionable penmanship is not our concern) but preserve order"
                " across letters, which is meaningful reading order. See the ",
                _link(
                    "tanach.us Psalms 124:4 note",
                    "https://tanach.us/Notes/Psalms/Psalms.124.4.4-c.html",
                ),
                ".",
            )
        ),
    )
