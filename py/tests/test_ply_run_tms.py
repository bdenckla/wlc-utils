"""Regression test for run-ply-tms: PLY behavior on the 49 troublemaker verses.

The troublemakers (accgram.tms.HARDCODED_REFS) yield no output from the C binary.
This test runs the PLY port on them (from the unfiltered split dir) and pins the
observed bucketing: every troublemaker is accounted for exactly once, the bucket
counts sum to 49, and a few spot-checked verses land where we observed them.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_run_tms.py -v
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from accgram import tms
from accgram.run_ply_tms import (
    CLEAN,
    ERROR_TREE,
    LOCATION_ONLY_BUCKET,
    MISSING_INPUT,
    NO_OUTPUT,
    classify_all,
    default_in_dir,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_IN_DIR = default_in_dir(_REPO_ROOT)

# Observed buckets on the current corpus (see out/accgram/ply-tms/_run_ply_tms.json).
_EXPECTED_COUNTS = {
    CLEAN: 0,
    ERROR_TREE: 26,
    LOCATION_ONLY_BUCKET: 0,
    NO_OUTPUT: 23,
    MISSING_INPUT: 0,
}
# A few representative verses, pinned to their observed bucket.
_SPOT_CHECKS = {
    ("1k", 6, 2): ERROR_TREE,
    ("je", 9, 10): ERROR_TREE,
    ("nu", 20, 19): ERROR_TREE,
    ("ob", 1, 1): NO_OUTPUT,
    ("ex", 34, 6): NO_OUTPUT,
}


@pytest.fixture(scope="module")
def results():
    if not _IN_DIR.is_dir():
        pytest.skip(f"unfiltered split dir not present: {_IN_DIR}")
    return classify_all(_IN_DIR)


def test_every_troublemaker_accounted_for_exactly_once(results):
    refs = [r.ref for r in results]
    assert set(refs) == set(tms.HARDCODED_REFS)
    assert len(refs) == len(set(refs)) == len(tms.HARDCODED_REFS) == 49


def test_bucket_counts(results):
    counts = Counter(r.bucket for r in results)
    assert dict(counts) == {k: v for k, v in _EXPECTED_COUNTS.items() if v}
    assert sum(counts.values()) == 49


def test_error_tree_results_contain_error_leaf(results):
    for r in results:
        if r.bucket == ERROR_TREE:
            assert "ERROR" in r.tree_text, f"{r.ref_str} bucketed error-tree without ERROR leaf"
        elif r.bucket == CLEAN:
            assert r.tree_text and "ERROR" not in r.tree_text
        else:
            assert r.tree_text == ""


@pytest.mark.parametrize(
    "ref,bucket",
    list(_SPOT_CHECKS.items()),
    ids=[tms.format_ref(ref) for ref in _SPOT_CHECKS],
)
def test_spot_checks(results, ref, bucket):
    by_ref = {r.ref: r.bucket for r in results}
    assert by_ref[ref] == bucket
