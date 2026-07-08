"""Issue #52: grammar-check the printed-tradition Decalogue accentuations.

Feeds the eight vendored Decalogue readings ({Exodus, Deuteronomy} x {taxton, elyon} x
{manuscript, printed}) through the prose grammar and pins the verdict:

  * every taxton chanted verse parses clean, both books and both traditions;
  * the manuscript elyon parses clean in both books (MAM's own authoritative text);
  * the *printed* elyon of *each* Decalogue has exactly one ungrammatical chanted verse --
    its opening verse, where the printed tradition merges the first two commandments into a
    single verse (nine verses total vs the manuscript's ten). That merged verse is far the
    longest of its version.

Skips if the vendored source JSON is absent (regenerate via printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_printed_decalogue.py -v
"""

from __future__ import annotations

import pytest

from accgram import printed_decalogue as pd

_SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"


def _results_or_skip() -> list[pd.VersionResult]:
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    return pd.check_all(pd.load_source(src))


def _by_key(results: list[pd.VersionResult]) -> dict[tuple[str, str, str], pd.VersionResult]:
    return {(vr.book, vr.reading, vr.tradition): vr for vr in results}


def test_eight_versions_present() -> None:
    results = _results_or_skip()
    keys = set(_by_key(results))
    expected = {
        (book, reading, tradition)
        for book in ("ex", "dt")
        for reading in ("taxton", "elyon")
        for tradition in ("manuscript", "printed")
    }
    assert keys == expected


def test_taxton_all_clean() -> None:
    """taxton parses clean in both books and both traditions."""
    results = _results_or_skip()
    for vr in results:
        if vr.reading == "taxton":
            assert vr.ungrammatical == (), f"{vr.book} taxton {vr.tradition} unexpectedly bad"


def test_manuscript_elyon_all_clean() -> None:
    """MAM's own manuscript elyon parses clean in both books."""
    results = _results_or_skip()
    by_key = _by_key(results)
    for book in ("ex", "dt"):
        vr = by_key[(book, "elyon", "manuscript")]
        assert vr.ungrammatical == (), f"{book} elyon manuscript unexpectedly bad"


def test_printed_elyon_one_ungrammatical_merged_first_verse() -> None:
    """The printed elyon of each Decalogue has exactly one ungrammatical chanted verse: its
    opening verse, where the printed tradition merges the first two commandments into one
    (giving nine chanted verses vs the manuscript's ten). Note the failure is NOT mere
    length -- Deuteronomy's 55-word Sabbath elyon verse parses clean, while this merged
    verse (51 words) does not; it is the merged structure, not the size, that defeats the
    grammar."""
    results = _results_or_skip()
    by_key = _by_key(results)
    for book in ("ex", "dt"):
        vr = by_key[(book, "elyon", "printed")]
        bad = vr.ungrammatical
        assert len(bad) == 1, f"{book} printed elyon: expected 1 ungrammatical, got {len(bad)}"
        offender = bad[0]
        assert offender.index == 1, f"{book} printed elyon: offender is not the first verse"
        # The merged verse runs from אנכי (commandment 1) through the end of commandment 2.
        assert offender.words[0].startswith("אָֽנֹכִי")
        assert offender.words[-1].endswith(_SOF_PASUQ)
        # The merge yields nine chanted verses (vs the manuscript's ten).
        assert len(vr.chanted_verses) == 9
        assert by_key[(book, "elyon", "manuscript")].chanted_verses.__len__() == 10


def test_total_ungrammatical_is_two() -> None:
    results = _results_or_skip()
    total = sum(len(vr.ungrammatical) for vr in results)
    assert total == 2
