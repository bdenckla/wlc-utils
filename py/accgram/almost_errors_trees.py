"""Tree-generation / "real computing" for the "almost errors" page.

The compute layer behind ``almost_errors_html``: mode-aware ``word_to_marks``
swaps, scan/parse, and the clean/ERROR/NO_PARSE verdicts that drive the
alternate-reading parse trees.  These functions take ``bcv``/``mode`` parameters
and have **zero HTML dependency** -- they only scan and parse the real grammar,
so the page can never drift from the checker's actual behaviour.

All swaps of ``uni_to_marks.word_to_marks`` (and the scanner's fuse rule) are
scoped to a context manager and restored on exit (read-only: no module is left
mutated permanently).
"""

from __future__ import annotations

import contextlib

from accgram import accent_marks as am
from accgram import lexical_validation
from accgram import ply_scanner
from accgram import run_ply
from accgram import uni_to_marks
from accgram.ply_grammar import LOCATION_ONLY, parse_tokens
from accgram.ply_scanner import HasLegarmeh, Token, scan_accents
from accgram.ply_tree import print_tree
from accgram.uni_to_marks import (
    _KEPT_NON_ACCENT,
    _MAQAF,
    _PREPOSITIVE_MARKS,
    _is_accent,
    _is_base_letter,
)

# The geresh family (plain geresh U+059C, gershayim U+059D's plain sibling, and the
# geresh muqdam U+059D promoted/demoted form) the telisha gedola companion-drop concerns.
_GG = frozenset((am.GERESH, am.GERSHAYIM))


# --------------------------------------------------------------------------- #
# Tree generation
# --------------------------------------------------------------------------- #
def _build_word_variant(word: str, mode: str) -> str:
    """``uni_to_marks.word_to_marks``, but for a word carrying BOTH a telisha gedola
    and a geresh-family mark, apply ``mode`` (chosen / keep_gerstar / keep_both).

    A faithful copy of the Plan B prototype: it rebuilds the mark skeleton, dropping
    the telg or the geresh-family companion per ``mode`` (or neither, for keep_both),
    scoped to words holding *both*; every other word is transcoded normally.
    """
    has_telg = am.TELISHA_GEDOLA in word
    has_gerstar = any((am.GERESH if c == am.GERESH_MUQDAM else c) in _GG for c in word)
    both = has_telg and has_gerstar
    skeleton: list[str | None] = []
    prepos: list[str] = []
    other: list[str] = []
    telg_seen = 0
    for ch in word:
        if _is_base_letter(ch):
            skeleton.append(am.LETTER)
            continue
        if ch == _MAQAF:
            skeleton.append(am.MAQAF)
            continue
        mark: str | None = None
        if _is_accent(ch):
            if ch == am.TELISHA_GEDOLA:
                telg_seen += 1
                if telg_seen > 1:
                    continue
                if both and mode == "keep_gerstar":
                    continue  # drop the telg
                mark = am.TELISHA_GEDOLA
            else:
                as_geresh = am.GERESH if ch == am.GERESH_MUQDAM else ch
                if as_geresh in _GG:
                    if both and mode == "chosen":
                        continue  # drop the geresh-family companion (current behaviour)
                    mark = as_geresh
                else:
                    mark = ch
        elif ch in _KEPT_NON_ACCENT:
            mark = ch
        if mark is None:
            continue
        skeleton.append(None)
        (prepos if mark in _PREPOSITIVE_MARKS else other).append(mark)
    marks = iter(prepos + other)
    return "".join(next(marks) if p is None else p for p in skeleton)


@contextlib.contextmanager
def _word_to_marks_mode(mode: str):
    """Temporarily swap ``uni_to_marks.word_to_marks`` for the mode-aware variant,
    restoring the original on exit (read-only: the module is never left mutated)."""
    original = uni_to_marks.word_to_marks
    uni_to_marks.word_to_marks = lambda w: _build_word_variant(w, mode)
    try:
        yield
    finally:
        uni_to_marks.word_to_marks = original


def _scan_and_parse(bcv: str, body: str, parser, has_legarmeh: HasLegarmeh):
    bb = bcv[:2]
    chnu, vrnu = (int(part) for part in bcv[2:].split(":"))
    tokens = [Token("TILDE", "")] + scan_accents(body, bb, chnu, vrnu, has_legarmeh)
    return parse_tokens(parser, tokens)


def _tree_text(tree) -> str:
    if tree in (None, LOCATION_ONLY):
        return "NO_PARSE"
    return print_tree(tree, 0).rstrip("\n")


def _telg_verdict(tree) -> str:
    if tree in (None, LOCATION_ONLY):
        return "NO_PARSE"
    return "ERROR" if "ERROR" in print_tree(tree) else "clean"


def _telg_tree_text(bcv: str, mode: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    """Tree text for one telg-exhibit verse under one alternate reading ``mode``."""
    with _word_to_marks_mode(mode):
        body = uni_to_marks.verse_to_marks(index[bcv])
    return _tree_text(_scan_and_parse(bcv, body, parser, has_legarmeh))


def _telg_verdict_for(bcv: str, mode: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    with _word_to_marks_mode(mode):
        body = uni_to_marks.verse_to_marks(index[bcv])
    return _telg_verdict(_scan_and_parse(bcv, body, parser, has_legarmeh))


def _prose_verse_tree_text(bcv: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    """The checker's *live* tree text for a prose verse, exactly as run_ply renders it.

    Reuses the run_ply lexical layer (so lv25:20 reads as its ``illegal_mark`` tree,
    grammar skipped) and the same illegal-mark label, so the page can never drift from
    the corpus output."""
    verse = index[bcv]
    body = uni_to_marks.verse_to_marks(verse)
    stranded = lexical_validation.stranded_stress_helpers(
        body
    ) + lexical_validation.illegal_same_letter_pairs(body)
    if stranded:
        words = run_ply._stranded_unicode_words(stranded, verse)
        return print_tree(run_ply._illegal_mark_tree(stranded, words), 0).rstrip("\n")
    return _tree_text(_scan_and_parse(bcv, body, parser, has_legarmeh))


def _ek2031_word_variant(word: str, mode: str, base) -> str:
    """``uni_to_marks.word_to_marks``, but for ek20:31's ``נִטְמְאִ֤֨ים`` (the one word
    carrying BOTH a mahapakh and a qadma on a single letter) apply ``mode`` -- one of the
    four alternatives to the fused reading (drop one mark, or keep both as a sequence in
    either order).  ``base`` is the real (pre-swap) ``word_to_marks``, used unchanged for
    ``fused`` and for every word not carrying both marks.

    For ``fused`` (and any non-matching word) the scanner fuses the pair as it normally
    would.  The two ``seq_*`` modes only set the mark *order*; ``seq_mah_azla`` still
    scans as the fused token unless the caller also suppresses the fuse rule (see
    ``_no_mahapakh_azla_fuse``)."""
    both = am.MAHAPAKH in word and am.QADMA in word
    if mode == "fused" or not both:
        return base(word)
    skeleton: list[str | None] = []
    prepos: list[str] = []
    other: list[str] = []
    for ch in word:
        if _is_base_letter(ch):
            skeleton.append(am.LETTER)
            continue
        if ch == _MAQAF:
            skeleton.append(am.MAQAF)
            continue
        mark: str | None = None
        if ch == am.MAHAPAKH:
            if mode == "drop_mahapakh":
                continue
            mark = am.MAHAPAKH
        elif ch == am.QADMA:
            if mode == "drop_azla":
                continue
            mark = am.QADMA
        elif _is_accent(ch):
            mark = ch
        elif ch in _KEPT_NON_ACCENT:
            mark = ch
        if mark is None:
            continue
        skeleton.append(None)
        (prepos if mark in _PREPOSITIVE_MARKS else other).append(mark)
    if mode in ("seq_azla_mah", "seq_mah_azla"):
        mah_i, qad_i = other.index(am.MAHAPAKH), other.index(am.QADMA)
        want_qadma_first = mode == "seq_azla_mah"
        if (qad_i < mah_i) != want_qadma_first:
            other[mah_i], other[qad_i] = other[qad_i], other[mah_i]
    marks = iter(prepos + other)
    return "".join(next(marks) if p is None else p for p in skeleton)


@contextlib.contextmanager
def _ek_word_to_marks_mode(mode: str):
    """Temporarily swap ``uni_to_marks.word_to_marks`` for the ek20:31 variant, restoring
    the original on exit (read-only: the module is never left mutated)."""
    original = uni_to_marks.word_to_marks
    uni_to_marks.word_to_marks = lambda w: _ek2031_word_variant(w, mode, original)
    try:
        yield
    finally:
        uni_to_marks.word_to_marks = original


@contextlib.contextmanager
def _no_mahapakh_azla_fuse():
    """Temporarily drop the scanner's ``MAHAPAKHAZLA`` fuse rule so a mahapakh-then-qadma
    adjacency scans as two tokens (``MAHAPAKH AZLA``) instead of re-fusing -- the only way
    to observe the ``seq_mah_azla`` reading as a genuine sequence.  Restored on exit."""
    original = ply_scanner._GG_RULES
    ply_scanner._GG_RULES = [r for r in original if r[1] != "MAHAPAKHAZLA"]
    try:
        yield
    finally:
        ply_scanner._GG_RULES = original


def _ek_verdict_for(mode: str, index, parser, has_legarmeh: HasLegarmeh) -> str:
    """``clean`` / ``ERROR`` / ``NO_PARSE`` for ek20:31 under one ``_EK_MODES`` reading."""
    with contextlib.ExitStack() as stack:
        stack.enter_context(_ek_word_to_marks_mode(mode))
        if mode == "seq_mah_azla":
            stack.enter_context(_no_mahapakh_azla_fuse())
        body = uni_to_marks.verse_to_marks(index["ek20:31"])
        return _telg_verdict(_scan_and_parse("ek20:31", body, parser, has_legarmeh))


def _telg_gerstar_word(verse: object) -> str | None:
    for word in run_ply._verse_display_words(verse):
        has_telg = am.TELISHA_GEDOLA in word
        has_gerstar = any((am.GERESH if c == am.GERESH_MUQDAM else c) in _GG for c in word)
        if has_telg and has_gerstar:
            return word
    return None
