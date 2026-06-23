"""Tests for the poetic (Three Books) scanner.

Pins the decoded token stream of a few real Psalms verses whose Michigan-Claremont
encoding was checked by hand against the M-C accent table (wlc420/supplmt.wts,
column II) and Yeivin ITM #358-374.  These exercise the tricky cases: the
revia-mugrash geresh muqdam (11+81), oleh-we-yored (60 ole + 71 yored merka),
azla/mehuppak legarmeh (63/70 + 05 paseq), the galgal servus of oleh-we-yored
(93), and the revia gadol/qatan/mugrash disambiguation.

Token-type names come from accgram.poetic_accent_names (no re-typed literals).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_scanner_poetic.py -v
"""

from accgram import accent_marks as am
from accgram import poetic_accent_names as pan
from accgram.ply_scanner_poetic import scan_accents
from accgram.ply_grammar_poetic import build_parser, parse_tokens
from accgram.ply_scanner_poetic import scan_verse
from tests.mc_marks import mc_to_marks

# The fixtures are written in the legacy M-C encoding (checked by hand against the
# accent table) and converted to the Phase-2 mark alphabet here (issue #9).


def _types(body):
    return [t for t, _ in scan_accents(mc_to_marks(body))]


def _types_marks(body):
    """Token types for a body already in the Phase-2 mark alphabet (not M-C)."""
    return [t for t, _ in scan_accents(body)]


def test_ps_1_1_revia_mugrash_geresh_muqdam():
    # ... 11L"CI81YM = geresh muqdam (11) + revia (81) -> one revia mugrash.
    body = (
        r')A71$:75R"Y-HF/)I81Y$]c ):A$E70R05 LO71) HFLAK:02 B.A/(:ACA93T '
        r'R:$F60(I71YM W./B:/DE74REK: 13XA+.F)IYM LO71) (FMF92D '
        r'W./B:/MOW$A71B 11L"CI81YM LO74) YF$F75B00'
    )
    types = _types(body)
    assert types[-1] == pan.SOFPASUQ
    assert types[-2] == pan.SILLUQ  # 75 before 00
    assert pan.REVIA_MUGRASH in types  # the 11(+81)
    assert pan.ATNAX in types  # 92
    assert pan.TSINNOR in types  # 02 (no zarqa in poetic)
    assert pan.DEXI in types  # 13


def test_ps_2_2_azla_legarmeh():
    # YI71T:YAC.:B63W.05 = azla (63) + paseq (05) -> azla legarmeh.
    body = (
        r"YI71T:YAC.:B63W.05 MAL:K\"Y-)E81REC W:/ROWZ:NI71YM "
        r"NO75WS:DW.-YF92XAD (AL-11Y:HWFH W:/(AL-M:$IYX/O75W00"
    )
    types = _types(body)
    assert pan.LEGARMEH in types
    # the revia after the legarmeh (81 on )EREC, next disjunctive atnah) is gadol
    assert pan.REVIA_GADOL in types
    assert pan.ATNAX in types


def test_ps_3_3_oleh_weyored_with_galgal_servus():
    # )OM:RI93YM = galgal servus; L:/NA60P:$/I71Y = ole (60) + yored merka (71).
    body = (
        r"RAB.IYM02 )OM:RI93YM L:/NA60P:$/I71Y )\"70YN "
        r"Y:75$W.(F65T/FH L./O64W B\"75/)LOHI64YM SE75LFH00"
    )
    types = _types(body)
    assert pan.OLEH_WEYORED in types
    assert pan.TSINNOR in types  # 02 on RAB.IYM
    # the galgal (93) precedes oleh-we-yored as its servus
    assert types.index(pan.GALGAL) < types.index(pan.OLEH_WEYORED)
    # the yored merka (71) is folded into OLEH_WEYORED, not emitted separately just
    # before it: no MERKHA sits between GALGAL and OLEH_WEYORED
    g, o = types.index(pan.GALGAL), types.index(pan.OLEH_WEYORED)
    assert pan.MERKHA not in types[g + 1 : o]


def test_ps_37_28_revia_gadol_then_dehi_then_atnah():
    # Yeivin's legarmeh-under-revia-gadol example; second half has dehi before atnah.
    body = (
        r"K.I70Y Y:HWF63H05 )O82H\"70B MI$:P.F81+ W:/LO)-YA(:AZO74B "
        r")ET-13X:ASIYDFY/W L:/(OWLF74M NI$:MF92RW. W:/ZE73RA( R:$F(I74YM NIK:RF75T00"
    )
    types = _types(body)
    assert pan.LEGARMEH in types  # 63+05 on YHWH
    assert pan.REVIA_GADOL in types  # 81 on MI$:P.F+ (next disjunctive is atnah)
    assert pan.DEXI in types  # 13
    assert pan.ATNAX in types
    assert types[-2:] == [pan.SILLUQ, pan.SOFPASUQ]


def test_unmarked_oleh_recovered_after_galgal():
    # Ps 30:12: L omits the ole (#363), writing only the yored merka (L/I71Y);
    # the galgal servus (93) immediately precedes it, so the bare merka is
    # recovered as oleh-we-yored rather than read as a servus.  MAM-cross-checked.
    body = (
        r"HFPA74K:T.F MIS:P.:D/IY02 L:/MFXO93WL L/I71Y P.IT.A71X:T.F "
        r'&AQ./I92Y WA75/T.:)AZ.:R/"71NIY &IM:XF75H00'
    )
    types = _types(body)
    assert pan.OLEH_WEYORED in types
    # the galgal stays as the oleh-we-yored's servus, directly before it
    g, o = types.index(pan.GALGAL), types.index(pan.OLEH_WEYORED)
    assert o == g + 1
    # the verse now parses (it was a NO_PARSE before the recovery)
    parser = build_parser()
    toks = scan_verse("Psalms 30:12", mc_to_marks(body)).tokens
    assert parse_tokens(parser, toks) is not None


def test_galgal_then_marked_oleh_not_doubly_recovered():
    # When the ole IS marked (60+71), the yored is already folded into
    # OLEH_WEYORED by the rule table, so there is no bare MERKHA after the galgal
    # to misread (Ps 1:1: B.A/(:ACA93T R:$F60(I71YM).
    body = r"B.A/(:ACA93T R:$F60(I71YM W./B:/DE74REK: LO74) YF$F75B00"
    types = _types(body)
    assert types.count(pan.OLEH_WEYORED) == 1
    g, o = types.index(pan.GALGAL), types.index(pan.OLEH_WEYORED)
    assert o == g + 1
    assert pan.MERKHA not in types[g:o]


def test_revia_qatan_before_oleh():
    # A bare revia (81) whose next disjunctive is oleh-we-yored is revia qatan.
    body = r"FOO81 BAR60BAZ71 QUX75X00"
    assert pan.REVIA_QATAN in _types(body)


def test_ps124_4_plain_geresh_charity_to_revia_mugrash():
    # ps124:4: revia (U+0597) + plain geresh (U+059C) on ONE letter -- the only plain
    # geresh in the Three Books.  Read charitably as a single revia mugrash: the geresh
    # is *consumed* into the fused token, not silently swallowed by the catch-all (which
    # would leave a bare revia that only incidentally reclassifies to revia mugrash).
    # Body mirrors the real verse's shape: ... revia+geresh word (with a ]1 note) ...
    # then a meteg-before-sofpasuq silluq.
    body = (
        "X" + am.DEHI + "XX XX" + am.MUNAH + "XX XXX" + am.ATNAX + "XXX "
        "X" + am.REVIA + am.GERESH + "XXX]1 XX" + am.MERKHA + "X "
        "XX-XXX" + am.METEG + "XX" + am.SOF_PASUQ
    )
    types = _types_marks(body)
    assert pan.REVIA_MUGRASH in types
    assert types.count(pan.REVIA_MUGRASH) == 1
    # the geresh is consumed, so no spurious extra disjunctive appears
    assert pan.REVIA not in types and pan.REVIA_GADOL not in types
    assert types[-2:] == [pan.SILLUQ, pan.SOFPASUQ]


def test_revia_then_geresh_only_fuses_same_letter():
    # The charity is same-letter only (adjacency, no X between).  Trailing atnah makes a
    # *bare* revia reclassify to revia GADOL, so fusion (same-letter) vs swallow
    # (cross-letter) is visible in the output: were the trailing disjunctive silluq,
    # the bare revia would reclassify to mugrash too and hide the difference.
    tail = "X XX" + am.ATNAX + "X XX" + am.METEG + am.SOF_PASUQ
    same = _types_marks("X" + am.REVIA + am.GERESH + tail)
    cross = _types_marks("X" + am.REVIA + "X" + am.GERESH + tail)
    assert same.count(pan.REVIA_MUGRASH) == 1  # fused, regardless of what follows
    assert pan.REVIA_GADOL in cross and pan.REVIA_MUGRASH not in cross  # geresh swallowed


def test_these_verses_parse():
    parser = build_parser()
    for body in (
        r')A71$:75R"Y-HF/)I81Y$]c ):A$E70R05 LO71) HFLAK:02 B.A/(:ACA93T '
        r'R:$F60(I71YM W./B:/DE74REK: 13XA+.F)IYM LO71) (FMF92D '
        r'W./B:/MOW$A71B 11L"CI81YM LO74) YF$F75B00',
    ):
        v = scan_verse("test 1:1", mc_to_marks(body))
        assert parse_tokens(parser, v.tokens) is not None
