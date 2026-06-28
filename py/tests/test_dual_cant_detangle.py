"""Stage-2 of issue #36: the dual-cantillation detangler.

Drives all three loci (Gen 35:22 + the two Decalogues) through the detangler and the
*existing* prose grammar.  The corpus-backed assertions skip when the WLC 4.22 kq-u
corpus or MAM-simple is absent.

The fixed expectations come from the verified survey (``.novc/novc_dualcant_survey.py``):

  * exactly 4 supplied marks (clean charities) and 1 anomaly (a candidate WLC bug);
  * Gen 35:22 detangles into pashut = 2 chanted verses, midrashit = 1, all parsing;
  * supplied-mark words parse clean (the charity is what lets them parse);
  * the dt 5:8 anomaly surfaces as an attributed oddball, not a crash.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_dual_cant_detangle.py -v
"""

from __future__ import annotations

import pytest

from accgram import accent_marks as am
from accgram import dual_cant_detangle as dcd
from accgram import prose_filter
from accgram import rtms_data
from accgram import supplied_marks
from accgram.mam_simple_verse import load_mam_simple_for_refs
from accgram.prose_ply_grammar import build_parser

import repo_paths


def _detangle_or_skip() -> list[dcd.PassageResult]:
    kq_u_dir = rtms_data.default_wlc422_kq_u_dir(repo_paths.repo_root())
    mam_dir = repo_paths.mam_simple_dir()
    if not kq_u_dir.is_dir():
        pytest.skip(f"WLC 4.22 kq-u corpus not present at {kq_u_dir}")
    if not mam_dir.is_dir():
        pytest.skip(f"MAM-simple not present at {mam_dir}")
    wlc_index = rtms_data.load_wlc422_index(kq_u_dir)
    mam = load_mam_simple_for_refs(mam_dir, dcd.all_refs_by_book(), include_threads=True)
    return dcd.detangle_all(wlc_index, mam, build_parser())


def _all_chanted_verses(results: list[dcd.PassageResult]) -> list[dcd.ChantedVerseResult]:
    return [cv for pr in results for tr in pr.threads for cv in tr.chanted_verses]


def test_gen3522_splits_into_two_and_one_chanted_verse_all_parsing() -> None:
    results = _detangle_or_skip()
    gen = next(pr for pr in results if pr.passage.bb == "gn")
    alef, bet = gen.threads
    assert alef.thread_label == "pashut" and bet.thread_label == "midrashit"
    assert len(alef.chanted_verses) == 2
    assert len(bet.chanted_verses) == 1
    assert all(cv.status == "clean" for cv in alef.chanted_verses + bet.chanted_verses)


def test_supplied_marks_are_exactly_the_four_clean_supplies() -> None:
    results = _detangle_or_skip()
    supplies = [s for pr in results for s in pr.supplied_marks]
    keyed = {(s.bcv, s.thread, s.accent) for s in supplies}  # one row per supply
    assert len(supplies) == 4
    assert keyed == {
        ("ex20:3", "alef", am.MERKHA),
        ("dt5:17", "alef", am.TIPEXA),
        ("dt5:6", "bet", am.TIPEXA),
        ("dt5:6", "bet", am.ATNAX),
    }


def test_single_anomaly_is_dt58_alef_and_is_a_candidate_wlc_bug() -> None:
    results = _detangle_or_skip()
    anomalies = [a for pr in results for a in pr.anomalies]
    assert len(anomalies) == 1
    anomaly = anomalies[0]
    assert (anomaly.bcv, anomaly.thread) == ("dt5:8", "alef")
    assert anomaly.expected == am.QADMA  # MAM is due a qadma
    assert anomaly.found == am.MERKHA  # WLC wrote a merkha instead


def test_supplied_mark_words_parse_clean() -> None:
    # The supply is precisely what lets the chanted verse parse: a supplied-mark word's
    # chanted verse must be clean and NOT an oddball (the issue's reporting requirement).
    results = _detangle_or_skip()
    supply_bcvs = {(s.bcv, s.thread) for pr in results for s in pr.supplied_marks}
    for pr in results:
        for tr in pr.threads:
            for cv in tr.chanted_verses:
                for bcv in {b for b in cv.bcv_span}:
                    if (bcv, tr.thread) in supply_bcvs:
                        assert cv.status == "clean", f"{cv.ref} -> {cv.status}"


def test_dt58_anomaly_surfaces_as_attributed_oddball_not_crash() -> None:
    results = _detangle_or_skip()
    dt = next(pr for pr in results if pr.passage.bb == "dt")
    taxton = next(tr for tr in dt.threads if tr.thread == "alef")
    dt58 = [cv for cv in taxton.chanted_verses if cv.bcv_span[0] == "dt5:8"]
    assert dt58 and dt58[0].status == "oddball"
    assert dt58[0].tree is not None  # a real (ERROR-bearing) tree, not a None crash


def test_every_chanted_verse_parses_or_is_attributed_only_dt58_is_an_oddity() -> None:
    results = _detangle_or_skip()
    cvs = _all_chanted_verses(results)
    bad = [cv.ref for cv in cvs if cv.status not in ("clean", "oddball")]
    assert not bad, f"unexpected no_parse/location_only: {bad}"
    oddballs = [cv.bcv_span[0] for cv in cvs if cv.status == "oddball"]
    assert oddballs == ["dt5:8"]


# --------------------------------------------------------------------------- #
# Stage 3: routing (prose_filter) and fold-in / supplied-marks surfaces.
# --------------------------------------------------------------------------- #
def _mam_with_threads_or_skip() -> dict[str, dict]:
    mam_dir = repo_paths.mam_simple_dir()
    if not mam_dir.is_dir():
        pytest.skip(f"MAM-simple not present at {mam_dir}")
    return load_mam_simple_for_refs(
        mam_dir, dcd.all_refs_by_book(), include_threads=True
    )


def _range_verses() -> list[tuple[str, int, int]]:
    out: list[tuple[str, int, int]] = []
    for bb, chnu, start, end in prose_filter._BHS_RANGE_EXCLUSIONS:
        out.extend((bb, chnu, vr) for vr in range(start, end + 1))
    return out


def test_prose_filter_single_cant_exceptions_match_mam_and_routing() -> None:
    # The hardcoded "un-exclude these 9" set must equal exactly the in-range verses MAM
    # marks single-cantillation (no cant-all-three) -- so it can't silently drift.
    mam = _mam_with_threads_or_skip()
    derived_single_cant = set()
    for bb, chnu, vrnu in _range_verses():
        verse = mam[f"{bb}{chnu}:{vrnu}"]["mam_simple_verse"]
        if verse["vels_cant_alef"] == verse["vels_cant_bet"]:
            derived_single_cant.add((bb, chnu, vrnu))
    assert derived_single_cant == set(prose_filter._BHS_SINGLE_CANT_IN_RANGE)

    # Routing: the 9 single-cant verses go to the normal prose path; the 24 dual
    # verses (gn 35:22 + the rest of the ranges) stay excluded.
    for bb, chnu, vrnu in prose_filter._BHS_SINGLE_CANT_IN_RANGE:
        assert prose_filter.should_keep_line(bb, chnu, vrnu) is True
    dual_in_range = [v for v in _range_verses() if v not in derived_single_cant]
    for bb, chnu, vrnu in dual_in_range:
        assert prose_filter.should_keep_line(bb, chnu, vrnu) is False
    assert prose_filter.should_keep_line("gn", 35, 22) is False


def test_fold_in_yields_one_dt58_oddball_record() -> None:
    kq_u_dir = rtms_data.default_wlc422_kq_u_dir(repo_paths.repo_root())
    if not kq_u_dir.is_dir():
        pytest.skip("WLC 4.22 kq-u corpus not present")
    wlc_index = rtms_data.load_wlc422_index(kq_u_dir)
    mam = _mam_with_threads_or_skip()
    parser = build_parser()

    # Genesis 35:22 and the Exodus Decalogue fold in nothing (no oddities).
    assert dcd.folded_oddball_records("gn", wlc_index, mam, parser) == []
    assert dcd.folded_oddball_records("ex", wlc_index, mam, parser) == []
    # Deuteronomy folds in exactly the dt 5:8 taxton oddity, keyed by its numbered verse.
    dt = dcd.folded_oddball_records("dt", wlc_index, mam, parser)
    assert len(dt) == 1
    assert dt[0]["bcv"] == "dt5:8"
    assert dt[0]["status"] == "oddball"
    assert dt[0]["dual_cant"] is True
    assert dt[0]["ref"].endswith("5:8")  # so the oddball collector reads (5, 8)


def test_supplied_marks_page_renders_all_four() -> None:
    results = _detangle_or_skip()
    supplies = [s for pr in results for s in pr.supplied_marks]
    body = supplied_marks.render_body_contents(supplies)
    # One <table> with a header row + 4 data rows.
    from py_html import wlc_utils_html as H

    html = H.el_to_str_no_wbr(body[0])
    assert html.count("<tr") == 5


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
