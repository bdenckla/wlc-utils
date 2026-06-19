"""Unit tests for the four trailing-context scanner rules + has_legarmeh.

Stage 1 / Phase D hardening.  These pin the lex *trailing-context* semantics
that PLY's lexer cannot express (silluq, mayela, legarmeh, plus the new-format
chapter lookahead via scan_book) and the stateful `has_legarmeh` counter, so a
regression in any one rule fails here rather than silently across thousands of
verses.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_scanner_lookaheads.py -v
"""

from __future__ import annotations

from accgram.ply_scanner import HasLegarmeh, scan_accents, scan_book


def _types(
    body: str,
    bb: str = "xx",
    chnu: int = 1,
    vrnu: int = 1,
    h: HasLegarmeh | None = None,
) -> list[str]:
    return [t.type for t in scan_accents(body, bb, chnu, vrnu, h or HasLegarmeh())]


# --- silluq (35|75|95 / [^ 379...]* 00) ----------------------------------------
def test_silluq_fires_immediately_before_sof_pasuq():
    # A metheg/silluq code directly (modulo plain text) before 00 is silluq.
    assert _types("75D00") == ["SILLUQ", "SOFPASUQ"]
    assert _types("35F00") == ["SILLUQ", "SOFPASUQ"]
    assert _types("95F00") == ["SILLUQ", "SOFPASUQ"]


def test_silluq_blocked_by_intervening_accent_is_swallowed():
    # 92 (atnax) carries a '9', which the exclusion set [^ 379...] forbids, so
    # the 75 is a medial metheg -> swallowed, and atnax is emitted instead.
    assert _types("7592)00") == ["ATNAX", "SOFPASUQ"]


# --- mayela (73 / <ga`ya-only>* (00|92)) vs plain tipexa -----------------------
def test_mayela_when_73_reaches_sof_pasuq_or_atnax():
    # 73 followed (within the word) only by allowed chars up to 00/92 -> mayela.
    assert _types("73NA00") == ["MAYELA", "SOFPASUQ"]
    assert _types("73NA92Z00") == ["MAYELA", "ATNAX", "SOFPASUQ"]


def test_tipexa_when_a_blocking_accent_intervenes():
    # 81 (revia) carries an '8', a blocking digit, so 73 is plain tipexa.
    assert _types("73NA81C00") == ["TIPEXA", "REVIA", "SOFPASUQ"]


# --- legarmeh (74{TEXT}05 / [^12368]*...81) ------------------------------------
def test_legarmeh_when_munax_paseq_precedes_revia():
    assert _types("74A05B81C00") == ["LEGARMEH", "REVIA", "SOFPASUQ"]


def test_munax_when_paseq_not_before_revia_outside_has_legarmeh_passage():
    # No following revia and an ordinary (non-listed) location -> plain munax.
    assert _types("74A05B70C00", "gn", 1, 1) == ["MUNAX", "MAHAPAKH", "SOFPASUQ"]


# --- has_legarmeh: keyed on structured (bb, ch, vs), so all 17 passages fire ----
# Real Ruth 1:2 body; the maqqef-joined "$:N\"75Y-BFNF74Y/W05" is a munax+paseq
# that does NOT precede revia, so it is legarmeh only because the ref is listed.
_RUTH_1_2 = (
    'W:/$"74M HF/)I74Y$ ):E35LIYME83LEK: W:/$"M04 )I$:T./O63W NF(:FMI61Y '
    'W:/$"71M $:N"75Y-BFNF74Y/W05 MAX:LO70WN W:/KIL:YOWN03 )EP:RFTI80YM '
    'MI/B."71YT LE73XEM Y:HW.DF92H WA/Y.FBO71)W. &:D"Y-MOW)F73B WA/Y.I75H:YW.-$F75M00'
)


def test_has_legarmeh_fires_at_listed_passage_not_elsewhere():
    # The munax+paseq is reinterpreted as legarmeh at any listed passage --
    # ru 1:2 *and*, now that detection is decoupled from header spelling, at a
    # ref like lv 10:6 that the old C abbreviation quirk silently missed.
    assert _types(_RUTH_1_2, "ru", 1, 2).count("LEGARMEH") == 1
    assert _types(_RUTH_1_2, "lv", 10, 6).count("LEGARMEH") == 1
    # ... but the very same body at a non-listed ref stays munax.
    assert _types(_RUTH_1_2, "gn", 1, 1).count("LEGARMEH") == 0


# --- has_legarmeh counter logic (now keyed on structured refs) ------------------
def test_has_legarmeh_1sam_14_47_second_occurrence_only():
    # 1Sam 14:47 has two munax+paseq sequences not before revia; only the
    # second counts as legarmeh.  Now live in the new format (keyed on ("1s",
    # 14, 47), not the dead "1Sam 14:47" abbreviation).
    h = HasLegarmeh()
    assert h("1s", 14, 47) is False
    assert h("1s", 14, 47) is True


def test_has_legarmeh_plain_passage_fires_first_time():
    h = HasLegarmeh()
    assert h("gn", 28, 9) is True


def test_has_legarmeh_old_i_is_monotonic():
    # old_i advances to the matched index, so an earlier passage no longer
    # matches afterwards ("assumes the books are in Jewish order").
    h = HasLegarmeh()
    assert h("ru", 1, 2) is True        # index 13
    assert h("gn", 28, 9) is False      # index 0 < old_i -> never revisited


# --- new-format chapter/verse lookahead (via scan_book) ------------------------
def test_scan_book_builds_reference_and_delimits_verses():
    text = "Genesis\n1:1 71A00\n1:2 81B00\n"
    verses = scan_book(text, "gn")
    assert [v.reference for v in verses] == ["Genesis 1:1", "Genesis 1:2"]
    # Each verse opens with TILDE and closes with SOFPASUQ.
    assert verses[0].tokens[0].type == "TILDE"
    assert verses[0].tokens[-1].type == "SOFPASUQ"
