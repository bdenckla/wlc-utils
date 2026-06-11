"""Regression test for ply_classify: the PLY-based oddball/troublemaker split.

Pins the 99/1 reclassification: 51 original oddballs (ERROR in out/accgram/ply/)
plus 48 troublemakers PLY parses into ERROR trees (out/accgram/ply-tms/) become the
99 oddballs; the remaining 1 hardcoded troublemaker (no output even under PLY)
stays a troublemaker.  The 48 include 21 missing-sof-pasuq verses the scanner/grammar
now flag with a distinct sof_pasuq_phrase ERROR.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_classify.py -v
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from accgram import ply_classify
from accgram import research_tao
from accgram import tms

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PLY_DIR = research_tao.default_ply_dir(_REPO_ROOT)
_PLY_TMS_DIR = research_tao.default_ply_tms_dir(_REPO_ROOT)
_PSF_IN_DIR = research_tao.default_psf_in_dir(_REPO_ROOT)
_UNFILTERED_IN_DIR = research_tao.default_unfiltered_in_dir(_REPO_ROOT)
_GOERWITZ_ODDBALLS = _REPO_ROOT / "out" / "accgram" / "goerwitz" / "_oddballs.json"

# The 48 troublemakers PLY parses into ERROR trees (reclassified as oddballs).
# The first 27 are the original error-tree reclassifications; the remaining 21 are
# missing-sof-pasuq verses now flagged with a distinct sof_pasuq_phrase ERROR.
# ob 1:1 is an error-tree reclassification: a tevir illegally before silluq,
# recovered by the tevir_tifcha_clause error production.
_RECLASSIFIED_48 = {
    "1k 6:2", "1k 16:33", "1k 19:11", "1k 20:29", "2c 22:12", "2c 26:15",
    "2k 23:36", "da 2:41", "dt 13:15", "ec 7:21", "ec 9:18", "ek 11:1",
    "ek 14:11", "hg 2:12", "is 36:2", "je 4:19", "je 9:10", "je 9:11",
    "je 10:3", "je 31:32", "je 38:11", "je 48:12", "je 49:19", "lm 5:5",
    "mi 2:7", "nu 20:19", "ob 1:1",
    # missing sof pasuq (silluq-no_sof_pasuq / silluq-pasoleg):
    "1s 6:19", "am 1:14", "am 6:6", "am 9:5", "dt 9:20", "dt 25:9",
    "ek 33:20", "ex 2:5", "ex 14:25", "ex 14:29", "ex 34:6", "ho 4:19",
    "ho 8:9", "lv 18:17", "lv 19:1", "lv 26:7", "nu 7:32", "nu 7:40",
    "nu 7:55", "nu 7:68", "nu 25:19",
}
# The 1 verse that produces no output even under PLY (stays a troublemaker); it
# has a sof pasuq and fails for unrelated structural reasons.
_TROUBLEMAKERS_1 = {
    "ju 13:18",
}


def _refs(payload: dict, key: str) -> list[str]:
    return [row["ref"] for row in payload[key]]


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    for path in (_PLY_DIR, _PLY_TMS_DIR, _PSF_IN_DIR, _UNFILTERED_IN_DIR):
        if not path.is_dir():
            pytest.skip(f"required input dir not present: {path}")
    out_dir = tmp_path_factory.mktemp("ply_classify")
    oddballs_out = out_dir / "_oddballs.json"
    troubles_out = out_dir / "_troublemakers.json"
    ply_classify.write_ply_oddballs_and_troublemakers(
        ply_dir=_PLY_DIR,
        ply_tms_dir=_PLY_TMS_DIR,
        psf_in_dir=_PSF_IN_DIR,
        unfiltered_in_dir=_UNFILTERED_IN_DIR,
        oddballs_out=oddballs_out,
        troubles_out=troubles_out,
    )
    return (
        json.loads(oddballs_out.read_text(encoding="utf-8")),
        json.loads(troubles_out.read_text(encoding="utf-8")),
    )


def test_counts(generated):
    oddballs, troubles = generated
    assert len(oddballs["oddballs"]) == 99
    assert len(troubles["troublemakers"]) == 1
    # Cross-check: 99 + 1 == original 51 + 49 == 100.
    assert len(oddballs["oddballs"]) + len(troubles["troublemakers"]) == 100
    assert len(troubles["troublemakers"]) == len(tms.HARDCODED_REFS) - 48


def test_oddballs_are_goerwitz_51_union_reclassified_48(generated):
    oddballs, _ = generated
    oddball_refs = set(_refs(oddballs, "oddballs"))
    assert len(oddball_refs) == 99

    goerwitz_51 = set(_refs(json.loads(_GOERWITZ_ODDBALLS.read_text("utf-8")), "oddballs"))
    assert len(goerwitz_51) == 51
    assert oddball_refs == goerwitz_51 | _RECLASSIFIED_48


def test_troublemakers_are_the_1(generated):
    _, troubles = generated
    assert set(_refs(troubles, "troublemakers")) == _TROUBLEMAKERS_1


def test_ply_tms_oddballs_tagged_and_have_content(generated):
    oddballs, _ = generated
    ply_tms_rows = [r for r in oddballs["oddballs"] if r.get("output_dir") == "ply-tms"]
    assert {r["ref"] for r in ply_tms_rows} == _RECLASSIFIED_48
    for row in ply_tms_rows:
        assert row["content"], f"reclassified oddball {row['ref']} has empty content"
        assert row["output_file"].startswith("wlc_422_ps_")
