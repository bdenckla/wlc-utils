"""Pins the by-book ob_notes dataset to the pre-split tm_data+ob_data content.

The merged structured-text dataset was split from the historical tm_data.py/ob_data.py
into per-book ob_notes_* modules. This test asserts the aggregated result is byte-for-byte
equivalent (as evaluated data) to the baseline captured just before the split, and that
every consumer of the data still imports.

BASELINE_SHA256 is the SHA-256 of pprint.pformat(merged, sort_dicts=True, width=100) of
the aggregated ob_notes dataset. The original split baseline was 86 records across 24
books (HEAD 306e15f); it now stands at 91 after the stranded-`82` work added zarqa-whim
notes for the 5 newly-flagged refs (gn 17:20, gn 47:29, ex 36:2, lv 20:2, dt 14:24) and
gn moved into its own ob_notes_gn module. If you intentionally edit the notes, recompute
it with `_canonical_sha256(...)` below.
"""

from __future__ import annotations

import hashlib
import importlib
import pprint

from accgram import ob_notes

BASELINE_SHA256 = "7297ee01dce00745d461a042d04fb419654a4cff22c9d9010097b70b586a2e4d"

# Every module that consumes the structured-text dataset; importing them all is a smoke
# test that the aggregator wiring is intact.
_CONSUMERS = (
    "accgram.research_tao",
    "accgram.ob_report",
    "accgram.rtms_report",
    "accgram.rtms_missing_sof_pasuq_descriptions",
    "accgram.tm_sanity",
)


def _canonical_sha256(data: dict) -> str:
    canon = pprint.pformat(data, sort_dicts=True, width=100)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def test_ob_notes_matches_baseline() -> None:
    data = ob_notes.get_structured_text()
    assert len(data) == 91
    assert _canonical_sha256(data) == BASELINE_SHA256


def test_consumers_import() -> None:
    for name in _CONSUMERS:
        importlib.import_module(name)
