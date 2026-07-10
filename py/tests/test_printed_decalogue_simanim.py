"""Issue #62: the Simanim-Decalogue page (printed-decalogue-simanim.html).

The page's four-readings table is derived live from the vendored
``in/accgram/printed_decalogue_teamim.json``: for each Exodus reading it reads the first
chanted verse and derives the accent on אנכי (first word) and עבדים.  These tests pin that
derivation and confirm the page body renders.

Skips if the vendored source JSON is absent (regenerate via printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_printed_decalogue_simanim.py -v
"""

from __future__ import annotations

import pytest

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_simanim_page as sim

import repo_paths


def _results_or_skip() -> list[pd.VersionResult]:
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    return pd.check_all(pd.load_source(src))


def test_four_readings_derive_expected_accents() -> None:
    """אנכי / עבדים accents, derived from the data, match the established four readings.

    ``_resolve_readings`` itself raises if a derived accent diverges from its expected value,
    so this both exercises the derivation and pins the (accent-on-אנכי, accent-on-עבדים) pairs.
    """
    readings = sim._resolve_readings(_results_or_skip())
    got = {r.name: (r.anokhi_accent, r.avadim_accent) for r in readings}
    assert got == {
        "manuscript taḥton": ("pashta", "etnaḥta"),
        "manuscript elyon": ("tipeḥa", "silluq"),
        "printed taḥton": ("tipeḥa", "silluq"),
        "printed elyon": ("pashta", "revia"),
    }


def test_printed_taxton_equals_manuscript_elyon() -> None:
    """The page's headline identity: printed taḥton = manuscript elyon on both boundary words."""
    readings = {r.name: r for r in sim._resolve_readings(_results_or_skip())}
    pt, me = readings["printed taḥton"], readings["manuscript elyon"]
    assert (pt.anokhi_accent, pt.avadim_accent) == (me.anokhi_accent, me.avadim_accent)


def test_avadim_located_within_each_first_verse() -> None:
    """עבדים is found (by consonantal skeleton) in every reading's first chanted verse --
    verse-finally in the standalone readings, mid-verse in the merged ones."""
    readings = sim._resolve_readings(_results_or_skip())
    for r in readings:
        assert sim._base_skeleton(r.avadim_word) == sim._AVADIM


def test_body_renders() -> None:
    """The full page body builds without error and is non-empty."""
    results = _results_or_skip()
    source = pd.load_source(pd.default_source_path())
    body = sim.render_body_contents(results, source)
    assert isinstance(body, tuple) and len(body) > 0


def test_scan_images_committed() -> None:
    """Both Simanim scans are committed locally (the page references them by relative path,
    not the issue CDN)."""
    img_dir = repo_paths.gh_pages_dir() / "accgram" / "img"
    for name in ("simanim-decalogue-p83.png", "simanim-decalogue-p246.png"):
        assert (img_dir / name).is_file(), f"missing committed scan {name}"
