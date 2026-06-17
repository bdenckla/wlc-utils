"""Tests for the MAM-simple poetic disjunctive extractor (Phase 2 cross-check).

These pin the disjunctive sequence ``mam_poetic_accents`` extracts from a few
hand-built MAM-simple verse nodes, exercising the tricky encodings: oleh-we-yored
(ole + yored merka), revia mugrash (geresh muqdam + revia), legarmeh vs shalshelet
gedolah (both ``lp-legarmeih`` paseq nodes, told apart by the preceding sign), the
generic-revia reclassification, and bare shalshelet (qetannah, swallowed).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_mam_poetic_accents.py -v
"""

from mb_cmn import hebrew_accents as ha

from accgram import poetic_accent_names as pan
from accgram.mam_poetic_accents import (
    disjunctives_from_verse_node,
    servi_before_from_verse_node,
    word_accents_from_verse_node,
)

# Combining-accent helpers; the consonant carrier is irrelevant to extraction.
B = "ב"  # an arbitrary base letter (bet)
SOF = "׃"


def _text(*accents: str) -> dict:
    return {"type": "text", "text": "".join(B + a for a in accents)}


def _verse(*nodes: dict) -> dict:
    return {"type": "verse", "osisID": "Ps.1.1", "contents": list(nodes)}


def test_oleh_weyored_and_atnah_and_silluq():
    # ole(+yored merka) -> oleh-we-yored; etnahta -> atnach; final word -> silluq.
    node = _verse(
        {"type": "text", "text": B + ha.OLE + B + ha.MER},  # one word: ole + yored
        {"type": "text", "text": B + ha.ATN},
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node) == [
        pan.OLEH_WEYORED,
        pan.ATNAX,
        pan.SILLUQ,
    ]


def test_revia_mugrash_geresh_muqdam():
    node = _verse(
        {"type": "text", "text": B + ha.GER_M + B + ha.REV},  # mugrash on one word
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node) == [pan.REVIA_MUGRASH, pan.SILLUQ]


def test_generic_revia_reclassified_gadol_before_atnah():
    node = _verse(
        _text(ha.REV),
        _text(ha.ATN),
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node) == [
        pan.REVIA_GADOL,
        pan.ATNAX,
        pan.SILLUQ,
    ]


def test_generic_revia_before_oleh_is_qatan():
    node = _verse(
        _text(ha.REV),
        {"type": "text", "text": B + ha.OLE + B + ha.MER},
        {"type": "text", "text": B + ha.ATN},
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node)[:2] == [pan.REVIA_QATAN, pan.OLEH_WEYORED]


def test_legarmeh_is_conjunctive_plus_paseq_node():
    # mahpak word + lp-legarmeih paseq node -> legarmeh (not a bare conjunctive).
    node = _verse(
        _text(ha.MAH),
        {"type": "lp-legarmeih"},
        _text(ha.ATN),
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node) == [
        pan.LEGARMEH,
        pan.ATNAX,
        pan.SILLUQ,
    ]


def test_shalshelet_gedolah_vs_qetannah():
    # shalshelet + lp-legarmeih -> gedolah (disjunctive); bare shalshelet -> swallow.
    gedolah = _verse(
        _text(ha.SHA),
        {"type": "lp-legarmeih"},
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(gedolah) == [pan.SHALSHELET_GEDOLAH, pan.SILLUQ]

    qetannah = _verse(
        _text(ha.SHA),  # no paseq node -> conjunctive, swallowed
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(qetannah) == [pan.SILLUQ]


def test_ketiv_skipped_qere_read():
    # The qere half supplies the accent; the ketiv half is ignored.
    node = _verse(
        {
            "type": "kq",
            "contents": [
                {"type": "kq-k", "text": B + B},
                {"type": "kq-q", "text": B + ha.ATN},
            ],
        },
        {"type": "text", "text": B + ha.MER + SOF},
    )
    assert disjunctives_from_verse_node(node) == [pan.ATNAX, pan.SILLUQ]


# --- servant (conjunctive) extraction: servi_before / word_accents ---------------

def _silluq_word() -> dict:
    return {"type": "text", "text": B + ha.MER + SOF}


def test_word_accents_pairs_disjunctive_and_servus():
    # merka(servus) | dehi(divider) | silluq -- exactly one column non-None per word.
    node = _verse(_text(ha.MER), _text(ha.DEX), _silluq_word())
    assert word_accents_from_verse_node(node) == [
        (None, pan.MERKHA),
        (pan.DEXI, None),
        (pan.SILLUQ, None),
    ]


def test_servi_before_dehi_merka_and_munah():
    # The servant immediately before dehi is read in the L scanner's vocabulary.
    merka = _verse(_text(ha.MER), _text(ha.DEX), _silluq_word())
    assert servi_before_from_verse_node(merka, pan.DEXI) == [pan.MERKHA]

    munah = _verse(_text(ha.MUN), _text(ha.DEX), _silluq_word())
    assert servi_before_from_verse_node(munah, pan.DEXI) == [pan.MUNAX]


def test_servi_before_is_none_when_target_is_bare():
    # Verse-initial dehi (no preceding word) and dehi preceded by a divider both
    # count as servant-less -> None.
    initial = _verse(_text(ha.DEX), _text(ha.MUN), _silluq_word())
    assert servi_before_from_verse_node(initial, pan.DEXI) == [None]

    after_divider = _verse(_text(ha.ATN), _text(ha.DEX), _silluq_word())
    assert servi_before_from_verse_node(after_divider, pan.DEXI) == [None]


def test_servi_before_normalizes_atnah_hafukh_to_galgal():
    # MAM writes the oleh-we-yored servus as atnah-hafukh (U+05A2); L codes it galgal.
    # The extractor normalizes it so the same slot matches across witnesses.
    node = _verse(
        _text(ha.ATN_H),
        {"type": "text", "text": B + ha.OLE + B + ha.MER},  # oleh-we-yored word
        _text(ha.ATN),
        _silluq_word(),
    )
    assert servi_before_from_verse_node(node, pan.OLEH_WEYORED) == [pan.GALGAL]
