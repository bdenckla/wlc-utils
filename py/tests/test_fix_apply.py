"""Unit tests for the fix-tester's M-C splice (accgram.fix_apply).

Pin the mechanical behavior of ``apply_mam_fix``: a 1->1 accent swap, an accent
deletion, an insertion placed *after the last letter* (so a trailing note-marker
digit cannot fuse with the new code), the missing-sof-pasuq append, ketiv-atom
exclusion during alignment, and the UNTESTABLE bailouts.  Each splice is also
re-scanned through the real scanner to confirm it tokenizes as intended.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_fix_apply.py -v
"""

from __future__ import annotations

from accgram import fix_apply, fix_tester_codes
from accgram.fix_apply import AppliedFix, UntestableFix, apply_mam_fix
from accgram.ply_scanner import HasLegarmeh, scan_accents


def _types(body: str) -> list[str]:
    return [t.type for t in scan_accents(body, "zz", 1, 1, HasLegarmeh())]


def test_codes_table_in_sync():
    fix_tester_codes.assert_in_sync_with_gg_rules()


def test_swap_munach_to_mereka():
    # 1c 1:53-style: munaH (74) -> merkha (71) on the first word.
    result = apply_mam_fix(
        ")AL.74W.P B.F/(F75M00",
        ["אל֣וף", "בעם"],
        {"wlc422": "אל֣וף", "mam_simple": "אל֥וף"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == ")AL.71W.P B.F/(F75M00"
    assert "MEREKA" in _types(result.new_body)
    assert "MUNACH" not in _types(result.new_body)


def test_delete_accent():
    # je 10:3-style: drop a merkha (71) entirely.
    result = apply_mam_fix(
        "Y:D.71Y X92Z00",
        ["יד֥י", "זה"],
        {"wlc422": "יד֥י", "mam_simple": "ידי"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "Y:D.Y X92Z00"


def test_insert_after_last_letter_not_before_note_digit():
    # ex 4:10-style: a trailing note-marker ]1 must not fuse with an inserted 73.
    result = apply_mam_fix(
        "D.AB.ER/:KF]1 X92Y00",
        ["דברך", "זה"],
        {"wlc422": "דברך", "mam_simple": "דברך֖"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "D.AB.ER/:KF73]1 X92Y00"
    # The 73 must scan as TIFCHA, never as a spurious 17 + 3.
    assert "TIFCHA" in _types(result.new_body)


def test_missing_sof_pasuq_append():
    # A MAM value that only adds the sof pasuq punctuation -> insert 00 after the
    # last accent code (the verse-final silluq 75), so silluq + sof pasuq both scan.
    body = "WA/Y.O71MER )ELOHIY75M"  # no 00: missing sof pasuq; 75 = final silluq
    result = apply_mam_fix(
        body,
        ["ויאמר", "אלהים"],
        {"wlc422": "אלהים", "mam_simple": "אלהים׃"},
    )
    assert isinstance(result, AppliedFix)
    assert result.added_codes == ("00",)
    assert result.new_body == "WA/Y.O71MER )ELOHIY7500M"
    assert _types(result.new_body)[-2:] == ["SILLUQ", "SOFPASUQ"]


def test_ketiv_atom_excluded_from_alignment():
    # The *ketiv atom is swallowed by the scanner and dropped from vels, so it must
    # not count during alignment: 2 word-atoms (qere + last) align to 2 WLC words.
    result = apply_mam_fix(
        "*H/NCYBYM **HA/N.IC74YM ZZ00",
        ["הנציב֣ים", "זז"],
        {"wlc422": "הנציב֣ים", "mam_simple": "הנציב֥ים"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "*H/NCYBYM **HA/N.IC71YM ZZ00"


def test_section_marker_atom_excluded_from_alignment():
    # A lone setumah (S) / petuhah (P) section marker stands as its own M-C atom but
    # is dropped from the WLC word list (tagged sam_pe_inun), so it must not count
    # during alignment: 1 real word-atom aligns to 1 WLC word despite the trailing S.
    result = apply_mam_fix(
        "PE91LI)Y00 S",
        ["פל֛אי"],  # one WLC word; the S marker is not a word
        {"wlc422": "פל֛אי", "mam_simple": "פל֥אי"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "PE71LI)Y00 S"


def test_vowel_only_is_untestable():
    result = apply_mam_fix(
        "B.F71)00",
        ["בא"],
        {"wlc422": "בָא", "mam_simple": "בָּא"},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "vowel_only"


def test_meteg_only_is_untestable():
    # The sole difference is a meteg (U+05BD) -- a vowel-tier mark the grammar never
    # sees, so it is grammar-inert and labeled distinctly from a pure-niqqud diff.
    result = apply_mam_fix(
        "Y:D.71Y X92Z00",
        ["ידי", "זה"],
        {"wlc422": "יד֥י", "mam_simple": "ידֽ֥י"},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "meteg_only"


def test_adjacent_two_word_splice():
    # A wlc_focus spanning two adjacent words: change munaH->merkha on the first and
    # tipeHa->munaH on the second; both atoms are spliced (right-to-left).
    result = apply_mam_fix(
        "X74Y Z73W",
        ["א֣", "ב֖"],
        {"wlc422": "א֣ ב֖", "mam_simple": "א֥ ב֣"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "X71Y Z74W"
    assert result.word_index == 0
    assert result.extra_transforms == ('atom "Z73W" -> "Z74W" (73 -> 74)',)


def test_adjacent_two_word_one_word_is_noop():
    # Second word differs only by a vowel: a no-op for the grammar, first word still
    # splices cleanly.
    result = apply_mam_fix(
        ")AL.74W.P B.F/(F75M00",
        ["אל֣וף", "בעם"],
        {"wlc422": "אל֣וף בעם", "mam_simple": "אל֥וף בעם"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == ")AL.71W.P B.F/(F75M00"
    assert result.extra_transforms == ()


def test_multi_word_unequal_counts_is_untestable():
    result = apply_mam_fix(
        "X74Y Z73W",
        ["א֣", "ב֖"],
        {"wlc422": "א֣ ב֖", "mam_simple": "א֥"},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "multi_word"


def test_synthetic_accent_fix_applies():
    # A synthesized {wlc_focus -> synth_fix} entry (used when MAM == WLC) flows through
    # the same splice machinery: munaH -> merkha.
    result = apply_mam_fix(
        ")AL.74W.P B.F/(F75M00",
        ["אל֣וף", "בעם"],
        {"wlc422": "אל֣וף", "mam_simple": "אל֥וף"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == ")AL.71W.P B.F/(F75M00"


def test_synthetic_segolta_fix_applies():
    # is 45:1-style: the speculated fix is the segol *accent* (segolta, U+0592), not
    # the segol vowel -- a real munaH -> segolta change the grammar sees (74 -> 01).
    result = apply_mam_fix(
        "L:K.74WR$",
        ["לכ֣ורש"],
        {"wlc422": "לכ֣ורש", "mam_simple": "לכ֒ורש"},
    )
    assert isinstance(result, AppliedFix)
    assert result.new_body == "L:K.01WR$"
    assert "SEGOLTA" in _types(result.new_body)


def test_synthetic_vowel_fix_is_inert():
    # A synth_fix that adds only a vowel (segol point, U+05B6) is grammar-inert.
    result = apply_mam_fix(
        "L:K.74WR$",
        ["לכורש"],
        {"wlc422": "לכ֣ורש", "mam_simple": "לכֶ֣ורש"},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "vowel_only"


def test_multi_word_is_untestable():
    result = apply_mam_fix(
        "A92B00",
        ["x"],
        {"wlc422": ["a", "b"], "mam_simple": ["c"]},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "multi_word"


def test_alignment_failure_when_counts_differ():
    result = apply_mam_fix(
        ")AL.74W.P B.F/(F75M00",
        ["אל֣וף"],  # one WLC word vs two M-C atoms
        {"wlc422": "אל֣וף", "mam_simple": "אל֥וף"},
    )
    assert isinstance(result, UntestableFix)
    assert result.reason == "alignment_failure"
