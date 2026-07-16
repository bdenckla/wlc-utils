"""Issue #62: the Simanim-Decalogue page (printed-decalogue-simanim.html).

The four cantillation strands of the opening אנכי…עבדים span are derived live from the vendored
``in/accgram/printed_decalogue_teamim.json`` by the shared ``printed_decalogue_strands`` module:
for each Exodus reading it reads the first chanted verse and derives the accent on אנכי (first
word) and עבדים.  These tests pin that derivation (which now lives on the strands module, not on
this page) and confirm the Simanim page body renders.

Skips if the vendored source JSON is absent (regenerate via printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_printed_decalogue_simanim.py -v
"""

from __future__ import annotations

import pytest

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_simanim_page as sim
from accgram import printed_decalogue_strands as pds

import repo_paths


def _results_or_skip() -> list[pd.VersionResult]:
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    return pd.check_all(pd.load_source(src))


def test_four_readings_derive_expected_accents() -> None:
    """אנכי / עבדים accents, derived from the data, match the established four readings.

    ``pds.resolve_readings`` itself raises if a derived accent diverges from its expected value,
    so this both exercises the derivation and pins the (accent-on-אנכי, accent-on-עבדים) pairs.
    """
    readings = pds.resolve_readings(_results_or_skip())
    got = {r.name: (r.anokhi_accent, r.avadim_accent) for r in readings}
    assert got == {
        "m-trad taḥton": ("pashta", "etnaḥta"),
        "m-trad elyon": ("tipeḥa", "silluq"),
        "p-trad taḥton": ("tipeḥa", "silluq"),
        "p-trad elyon": ("pashta", "revia"),
    }


def test_printed_taxton_equals_manuscript_elyon() -> None:
    """The page's headline identity: p-trad taḥton = m-trad elyon on both boundary words."""
    readings = {r.name: r for r in pds.resolve_readings(_results_or_skip())}
    pt, me = readings["p-trad taḥton"], readings["m-trad elyon"]
    assert (pt.anokhi_accent, pt.avadim_accent) == (me.anokhi_accent, me.avadim_accent)


def test_avadim_located_within_each_first_verse() -> None:
    """עבדים is found (by consonantal skeleton) in every reading's first chanted verse --
    verse-finally in the standalone readings, mid-verse in the merged ones."""
    readings = pds.resolve_readings(_results_or_skip())
    for r in readings:
        assert pds.base_skeleton(r.avadim_word) == pds.AVADIM


def test_body_renders() -> None:
    """The full Simanim page body builds without error and is non-empty. It no longer needs the
    grammar-check results -- only the source's provenance."""
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    body = sim.render_body_contents(pd.load_source(src))
    assert isinstance(body, tuple) and len(body) > 0


def test_scan_images_committed() -> None:
    """Both Simanim scans are committed locally (the page references them by relative path,
    not the issue CDN)."""
    img_dir = repo_paths.gh_pages_dir() / "accgram" / "img"
    for name in (
        "simanim-decalogue-p-083-sidenote.png",
        "simanim-decalogue-p-246-footnote.png",
    ):
        assert (img_dir / name).is_file(), f"missing committed scan {name}"
