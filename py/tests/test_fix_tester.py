"""Unit tests for the fix-tester's verse-level ``merge_next`` splice.

Every other fix the tester applies is a single-word accent edit inside one
verse's M-C body (see ``test_fix_apply``).  nu 25:19 is the lone exception: MAM
equals WLC word-for-word and the only difference is versification -- BHS strands
a verse number mid-chanted-verse.  The fix is to append the M-C body BHS labels
as the *next* verse and re-parse; the stranded atnach then bisects a complete
verse ending in silluq + sof-pasuq.  See doc/fix-tester-remaining-untestables.md.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_fix_tester.py -v
"""

from __future__ import annotations

from accgram import fix_tester


# The two real M-C bodies (from wlc422_ps.txt).  nu 25:19 ends on an atnach (92)
# plus a ]1 note marker and a P petuhah -- no silluq, no sof-pasuq (00).
_NU_2519 = 'WA/Y:HI73Y )AX:AR"74Y HA/M.AG."PF92H]1 P'
# nu 26:1 ends in silluq (75) + sof-pasuq (00) -- the verse's true second half.
_NU_2601 = (
    'WA/Y.O70)MER Y:HWFH03 )EL-MO$E80H '
    'W:/)E94L )EL:(FZF91R B.EN-)AH:ARO71N HA/K.OH"73N L"/)MO75R00'
)


def test_merge_next_extracted_from_note():
    assert fix_tester._merge_next({"merge_next": "nu 26:1"}) == "nu 26:1"
    assert fix_tester._merge_next({"merge_next": "  nu 26:1  "}) == "nu 26:1"
    assert fix_tester._merge_next({}) is None
    assert fix_tester._merge_next({"merge_next": "   "}) is None
    assert fix_tester._merge_next("not a dict") is None


def test_nu_2519_alone_is_the_oddball():
    # Standalone, the BHS "verse" ends on an atnach with nothing after it, so both
    # the silluq and the sof-pasuq phrases are missing.
    guard = fix_tester._ParseGuard()
    before = fix_tester._evaluate(_NU_2519, "nu", 25, 19, guard)
    assert before.status == "ODDBALL"
    assert before.labels == frozenset({"silluq_phrase", "sof_pasuq_phrase"})
    assert before.token_types[-2:] == ("ATNACH", "MISSING_SOFPASUQ")


def test_merge_next_concatenation_parses_clean():
    # Append nu 26:1: the atnach now bisects a complete verse that ends in
    # silluq + sof-pasuq, and the mid-verse ]1 note / P petuhah are inert.
    guard = fix_tester._ParseGuard()
    before = fix_tester._evaluate(_NU_2519, "nu", 25, 19, guard)
    after = fix_tester._evaluate(f"{_NU_2519} {_NU_2601}", "nu", 25, 19, guard)
    assert after.status == "CLEAN"
    assert not after.labels
    assert "ATNACH" in after.token_types
    assert after.token_types[-2:] == ("SILLUQ", "SOFPASUQ")
    # No spurious token sneaks in where the mid-verse petuhah/note sit.
    assert after.token_types.count("ATNACH") == 1
