r"""Extract the ordered POETIC *disjunctive* sequence from MAM-simple verses.

This is the cross-check oracle for the poetic scanner+grammar (Phase 2 of
``doc/PLAN-poetic-accent-grammar.md``).  The WLC poetic scanner
(``accgram.ply_scanner_poetic``) reads Michigan-Claremont accent *codes*; MAM-simple
stores fully-pointed Unicode Hebrew with combining accent marks.  To confirm the
trees' segmentation is correct -- not merely parseable -- we reduce each side to its
ordered list of disjunctive accents (the division points) and diff those.  Servus
(conjunctive) signs are deliberately dropped: MAM and L often choose different
conjunctive *signs* for the same slot (e.g. L codes the oleh-we-yored servus as
galgal/yerah-ben-yomo while MAM writes atnah-hafukh), and Yeivin pins no exact
servus chains, so only the disjunctive skeleton is a meaningful equality check.

Disjunctive markers, MAM Unicode accent -> poetic token (same vocabulary the
scanner emits):

  ETNAHTA (U+0591)        -> ATNAX
  OLE (U+05AB)            -> OLEH_WEYORED  (its yored merka is folded in, as in L)
  GERESH MUQDAM (U+059D)  -> REVIA_MUGRASH (MAM always writes the revia dot too,
                            even where L omits it under the geresh muqdam -- the
                            geresh muqdam alone is the reliable marker)
  REVIA (U+0597) alone    -> REVIA (generic; reclassified gadol/qatan/mugrash by
                            position, exactly as the scanner's second pass)
  DEHI (U+05AD)           -> DEXI
  ZINOR (U+05AE)          -> TSINNOR
  PAZER (U+05A1)          -> PAZER
  SHALSHELET (U+0593)     -> shalshelet gedolah IFF an ``lp-legarmeih`` paseq node
                            follows (otherwise it is the conjunctive shalshelet
                            qetannah, swallowed -- matching the scanner)
  ``lp-legarmeih`` node   -> LEGARMEH when it follows a conjunctive word (azla /
                            mehuppak + paseq); promotes a preceding SHALSHELET to
                            SHALSHELET_GEDOLAH
  SOF PASUQ (U+05C3)      -> SILLUQ (the final word's meteg; verse end)

Other accents (munah, merka, mahpak, qadma/azla, illuy, tipeha/tarha, galgal,
atnah-hafukh, zarqa=tsinnorit, telisha, plain meteg/ga'ya, plain paseq) are servi
or secondary marks and contribute no disjunctive.
"""

from __future__ import annotations

import json
from pathlib import Path

from mb_cmn import hebrew_accents as ha
from mb_misc import osis_book_abbrevs as oba

from accgram import poetic_accent_names as pan
from cmn.wlc_book_codes import wlc_bb_to_bk39id

_SOF_PASUQ = "׃"

# MAM Unicode accent -> intermediate disjunctive marker (REVIA / SHALSHELET stay
# provisional; resolved in the second pass).  Checked in this priority order so
# composite words resolve correctly (geresh muqdam + revia -> mugrash; ole +
# merka -> oleh-we-yored).
_DISJ_PRIORITY: list[tuple[str, str]] = [
    (ha.OLE, pan.OLEH_WEYORED),
    (ha.GER_M, pan.REVIA_MUGRASH),
    (ha.SHA, pan.SHALSHELET),  # provisional: gedolah only if a paseq node follows
    (ha.ATN, pan.ATNAX),
    (ha.DEX, pan.DEXI),
    (ha.Z_OR_TSOR, pan.TSINNOR),
    (ha.PAZ, pan.PAZER),
    (ha.REV, pan.REVIA),  # provisional: reclassified gadol/qatan/mugrash by position
]

# Node types whose subtree carries no cantillated text for our purposes.
_DROP_TYPES = frozenset(
    {
        "good-ending",
        "spi-pe2",
        "spi-pe3",
        "spi-samekh2",
        "spi-samekh3",
        "spi-invnun",
        "implicit-maqaf",
    }
)
_KETIV_TYPES = frozenset({"ketiv", "kq-k", "kq-k-velo-q"})
_QERE_TYPES = frozenset({"qere", "kq-q", "kq-trivial", "kq-q-velo-k"})
_KQ_TYPES = frozenset({"kq", "kq-trivial", "kq-q-velo-k"})

_POETIC_DISJUNCTIVES = pan.POETIC_DISJUNCTIVES


def _word_marker(accents: str) -> str | None:
    """Resolve one word's combining accents to a provisional disjunctive marker."""
    for accent_char, marker in _DISJ_PRIORITY:
        if accent_char in accents:
            return marker
    return None


def _emit_word_events(text: str, events: list[tuple[str, str | None]]) -> None:
    """Append a ('WORD', marker) event per whitespace-delimited word in ``text``.

    The final word of the verse carries SOF PASUQ; its meteg is silluq, so it is
    emitted as a ('SOFPASUQ', None) sentinel that the second pass turns into SILLUQ.
    """
    for word in text.split():
        if _SOF_PASUQ in word:
            events.append(("SOFPASUQ", None))
            continue
        events.append(("WORD", _word_marker(word)))


def _walk(node: object, events: list[tuple[str, str | None]]) -> None:
    """In-order DFS collecting WORD / LP_LEG / LP_PASEQ / SOFPASUQ events.

    ``lp-legarmeih`` and ``lp-paseq`` are sibling structural nodes that sit between
    text runs; pre-order traversal preserves their position relative to the words.
    Ketiv halves of a qere/ketiv pair are skipped (the qere is what is read).
    """
    if not isinstance(node, dict):
        return
    node_type = node.get("type")
    if isinstance(node_type, str):
        if node_type == "lp-legarmeih":
            events.append(("LP_LEG", None))
            return
        if node_type == "lp-paseq":
            events.append(("LP_PASEQ", None))
            return
        if node_type in _KETIV_TYPES:
            return
        if node_type in _DROP_TYPES:
            return
        if node_type in _KQ_TYPES:
            _walk_kq(node, events)
            return

    contents = node.get("contents")
    if isinstance(contents, list):
        for child in contents:
            _walk(child, events)
        return

    text = node.get("text")
    if isinstance(text, str):
        _emit_word_events(text, events)


def _walk_kq(node: dict, events: list[tuple[str, str | None]]) -> None:
    """Walk a ketiv/qere node, reading only its qere half (the accented reading)."""
    contents = node.get("contents")
    if not isinstance(contents, list):
        text = node.get("text")
        if isinstance(text, str):
            _emit_word_events(text, events)
        return

    qere_children = [
        child
        for child in contents
        if isinstance(child, dict) and child.get("type") in _QERE_TYPES
    ]
    chosen = qere_children if qere_children else [
        child
        for child in contents
        if not (isinstance(child, dict) and child.get("type") in _KETIV_TYPES)
    ]
    for child in chosen:
        _walk(child, events)


def _reclassify_revia(disjunctives: list[str]) -> list[str]:
    """Resolve each generic REVIA to gadol/qatan/mugrash by the next disjunctive.

    Identical rule to ``ply_scanner_poetic._reclassify_revia`` (which scans the next
    disjunctive in the full token stream); here the list already contains only
    disjunctives, so the "next disjunctive" is simply the next element.
    """
    out = list(disjunctives)
    for i, marker in enumerate(out):
        if marker != pan.REVIA:
            continue
        nxt = next((out[j] for j in range(i + 1, len(out))), None)
        if nxt == pan.OLEH_WEYORED:
            out[i] = pan.REVIA_QATAN
        elif nxt == pan.SILLUQ:
            out[i] = pan.REVIA_MUGRASH
        else:
            out[i] = pan.REVIA_GADOL
    return out


def disjunctives_from_verse_node(verse_node: dict) -> list[str]:
    """Return the ordered poetic disjunctive sequence for one MAM-simple verse."""
    events: list[tuple[str, str | None]] = []
    _walk(verse_node, events)

    markers: list[str | None] = []
    last_word_index: int | None = None
    for kind, marker in events:
        if kind == "WORD":
            markers.append(marker)
            last_word_index = len(markers) - 1
        elif kind == "SOFPASUQ":
            markers.append(pan.SILLUQ)
            last_word_index = len(markers) - 1
        elif kind == "LP_LEG":
            # The preceding word is legarmeh (conjunctive + paseq) or, if it carried
            # shalshelet, shalshelet gedolah.
            if last_word_index is None:
                continue
            prev = markers[last_word_index]
            if prev == pan.SHALSHELET:
                markers[last_word_index] = pan.SHALSHELET_GEDOLAH
            elif prev is None:
                markers[last_word_index] = pan.LEGARMEH
            # else: an lp-legarmeih after a real disjunctive -- leave it alone.
        elif kind == "LP_PASEQ":
            # A plain paseq promotes a preceding shalshelet to gedolah too, but does
            # not by itself create a legarmeh.
            if last_word_index is not None and markers[last_word_index] == pan.SHALSHELET:
                markers[last_word_index] = pan.SHALSHELET_GEDOLAH

    # Bare shalshelet (no paseq) is the conjunctive qetannah -> swallow.
    disjunctives = [
        m for m in markers if m is not None and m != pan.SHALSHELET
    ]
    return _reclassify_revia(disjunctives)


def _mam_json_path(mam_simple_dir: Path, bk39id: str) -> Path | None:
    prefix = oba.BOOK_ABBREVS.get(bk39id)
    if prefix is None:
        return None
    candidate = mam_simple_dir / f"{prefix}.json"
    return candidate if candidate.is_file() else None


def _iter_verse_nodes(value: object):
    if isinstance(value, dict):
        if value.get("type") == "verse":
            yield value
            return
        contents = value.get("contents")
        if isinstance(contents, list):
            for child in contents:
                yield from _iter_verse_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_verse_nodes(child)


def load_poetic_disjunctives(
    mam_simple_dir: Path,
    books: tuple[str, ...] = ("ps", "pr", "jb"),
) -> dict[str, list[str]]:
    """Map ``"<book> <ch>:<vs>"`` -> MAM disjunctive sequence for the poetic books.

    The reference string matches ``ply_scanner_poetic``'s (e.g. ``"Psalms 1:1"``).
    """
    if not mam_simple_dir.is_dir():
        raise FileNotFoundError(f"MAM-simple directory not found: {mam_simple_dir}")

    by_ref: dict[str, list[str]] = {}
    for bb in books:
        bk39id = wlc_bb_to_bk39id(bb)
        json_path = _mam_json_path(mam_simple_dir, bk39id)
        if json_path is None:
            continue
        prefix = oba.BOOK_ABBREVS[bk39id]
        with json_path.open("r", encoding="utf-8") as f_in:
            root = json.load(f_in)
        for verse_node in _iter_verse_nodes(root):
            osis_id = verse_node.get("osisID")
            if not isinstance(osis_id, str) or not osis_id.startswith(f"{prefix}."):
                continue
            parts = osis_id.split(".")
            if len(parts) != 3:
                continue
            ref = f"{bk39id} {parts[1]}:{parts[2]}"
            by_ref[ref] = disjunctives_from_verse_node(verse_node)
    return by_ref
