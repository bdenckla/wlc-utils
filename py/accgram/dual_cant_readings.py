"""Map each dually-cantillated passage verse to its detangled per-thread readings,
for the goerwitz verse display (issue #36).

For a verse in one of the three dually-cantillated prose loci (Gen 35:22 and the two
Decalogues), the goerwitz report replaces the single combined WLC verse line with one
line per reading (e.g. taḥton + elyon). The elyon reading groups several numbered
verses into one chanted verse, so a reading's span label can differ from the row's own
verse (e.g. the elyon line for dt 5:8 spans dt 5:7–10).

Each reading is a plain dict (``display_label``, ``span_label``, ``words``, and a
``word_bcvs`` list giving each word's numbered verse) so the renderer stays dumb. The
``word_bcvs`` let the renderer gray the words that fall outside the row's own verse: an
elyon reading groups several numbered verses, so on the dt 5:8 row its 5:7 / 5:9 / 5:10
words are de-emphasized, spotlighting the 5:8 part where the oddball lives.
``display_label`` carries the Unicode ḥ (the cant-thread ASCII
label spells ḥet as "x", per the repo transliteration standard).
"""

from __future__ import annotations

import re
from pathlib import Path

from accgram import dual_cant_run

# ḥ as h + COMBINING DOT BELOW (decomposed het), per the repo transliteration standard.
_HET_UNI = "h" + chr(0x0323)
_EN_DASH = chr(0x2013)
_BCV_RE = re.compile(r"(\d+):(\d+)$")


def load_readings_by_bcv(
    wlc422_kq_u_dir: Path, mam_simple_dir: Path
) -> dict[str, list[dict[str, object]]]:
    """Compact-bcv -> ordered per-thread readings (alef/taḥton first, then bet/elyon)."""
    results = dual_cant_run.detangle_results(wlc422_kq_u_dir, mam_simple_dir)
    by_bcv: dict[str, list[dict[str, object]]] = {}
    for passage in results:
        for thread in passage.threads:
            for cv in thread.chanted_verses:
                span = list(cv.bcv_span)
                reading: dict[str, object] = {
                    "display_label": _display_label(thread.thread_label),
                    "span_label": _span_label(span),
                    "words": list(cv.words),
                    "word_bcvs": list(cv.word_bcvs),
                }
                for bcv in _bcvs_in_span(span):
                    by_bcv.setdefault(bcv, []).append(reading)
    return by_bcv


def _display_label(thread_label: str) -> str:
    # The cant-thread ASCII label spells ḥet as "x" (taxton); display uses ḥ.
    return thread_label.replace("x", _HET_UNI)


def _parse_bcv(bcv: str) -> tuple[str, int, int]:
    match = _BCV_RE.search(bcv)
    if match is None:
        raise ValueError(f"Unparseable bcv: {bcv!r}")
    return bcv[: match.start()], int(match.group(1)), int(match.group(2))


def _span_label(span: list[str]) -> str:
    _, ch1, v1 = _parse_bcv(span[0])
    _, ch2, v2 = _parse_bcv(span[-1])
    if (ch1, v1) == (ch2, v2):
        return f"{ch1}:{v1}"
    if ch1 == ch2:
        return f"{ch1}:{v1}{_EN_DASH}{v2}"
    return f"{ch1}:{v1}{_EN_DASH}{ch2}:{v2}"


def _bcvs_in_span(span: list[str]) -> list[str]:
    bb, ch1, v1 = _parse_bcv(span[0])
    _, ch2, v2 = _parse_bcv(span[-1])
    # The dually-cantillated passages never cross a chapter boundary within a chanted
    # verse; if that ever changes, fall back to the endpoints rather than guess verse
    # counts per chapter.
    if ch1 != ch2:
        return [span[0], span[-1]]
    return [f"{bb}{ch1}:{v}" for v in range(v1, v2 + 1)]
