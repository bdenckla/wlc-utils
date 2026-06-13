"""Aggregated oddball structured research notes, organized by book.

The former tm_data/ob_data split is retired; every annotated oddball lives in a
per-book ob_notes_* module (small books collected in ob_notes_misc).
"""

from __future__ import annotations

from accgram import ob_notes_gn
from accgram import ob_notes_ex
from accgram import ob_notes_lv
from accgram import ob_notes_nu
from accgram import ob_notes_dt
from accgram import ob_notes_ju
from accgram import ob_notes_1k
from accgram import ob_notes_is
from accgram import ob_notes_je
from accgram import ob_notes_ek
from accgram import ob_notes_ho
from accgram import ob_notes_am
from accgram import ob_notes_ec
from accgram import ob_notes_2c
from accgram import ob_notes_js
from accgram import ob_notes_2s
from accgram import ob_notes_misc


def get_structured_text() -> dict[str, dict[str, object]]:
    return STRUCTURED_TEXT_BY_REF


STRUCTURED_TEXT_BY_REF: dict[str, dict[str, object]] = {
    **ob_notes_gn.BY_REF,
    **ob_notes_ex.BY_REF,
    **ob_notes_lv.BY_REF,
    **ob_notes_nu.BY_REF,
    **ob_notes_dt.BY_REF,
    **ob_notes_ju.BY_REF,
    **ob_notes_1k.BY_REF,
    **ob_notes_is.BY_REF,
    **ob_notes_je.BY_REF,
    **ob_notes_ek.BY_REF,
    **ob_notes_ho.BY_REF,
    **ob_notes_am.BY_REF,
    **ob_notes_ec.BY_REF,
    **ob_notes_2c.BY_REF,
    **ob_notes_js.BY_REF,
    **ob_notes_2s.BY_REF,
    **ob_notes_misc.BY_REF,
}
