"""The Koren-Decalogue page (printed-decalogue-koren.html).

Companion to ``test_printed_decalogue_simanim``. The four-strands derivation itself is pinned by
that test and by ``printed_decalogue_strands``; here we only confirm the Koren page body renders
and that its scans are committed.

Skips if the vendored source JSON is absent (regenerate via printed_decalogue_fetch.py).

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_printed_decalogue_koren.py -v
"""

from __future__ import annotations

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_koren_page as kor
from accgram import transcription_parse as tp
from accgram import transcription_verdict_column as tvc

import pytest

import repo_paths


def test_body_renders() -> None:
    """The full Koren page body builds without error and is non-empty.

    Like the Simanim page it needs the grammar-check results, for the verdict table's last column
    (issue #52): each cell is the checker's verdict for one transcription against its strand's, so
    a row naming a stem with no committed transcription fails here, on the lookup.
    """
    src = pd.default_source_path()
    if not src.is_file():
        pytest.skip(f"vendored printed-Decalogue source not present at {src}")
    source = pd.load_source(src)
    verdicts = tvc.by_stem(tp.check_all(pd.check_all(source)))
    body = kor.render_body_contents(source, verdicts)
    assert isinstance(body, tuple) and len(body) > 0


def test_scan_images_committed() -> None:
    """The four Koren scans are committed locally (the page references them by relative path)."""
    img_dir = repo_paths.gh_pages_dir() / "accgram" / "img"
    for name in (
        "Koren-p-113-Ex-Dec-p-trad-taxton.png",
        "Koren-appendix-p-38-Ex-Dec-p-trad-elyon.png",
        "Koren-appendix-p-38-Ex-Dec-p-trad-elyon-note.png",
        # The Deuteronomy Shabbat commandment (issue #66), backing the conclusion's scope note.
        "Koren-p-281-Dt-Dec-Shabbat-p-trad-taxton.png",
    ):
        assert (img_dir / name).is_file(), f"missing committed scan {name}"
