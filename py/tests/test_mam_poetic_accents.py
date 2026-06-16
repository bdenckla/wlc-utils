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
from accgram.mam_poetic_accents import disjunctives_from_verse_node

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
