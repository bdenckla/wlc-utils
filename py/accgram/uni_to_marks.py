r"""Extract the Unicode **mark sequence** the PLY scanners consume (issue #9, Phase 2).

The PLY prose/poetic scanners (`ply_scanner` / `ply_scanner_poetic`) read each verse
as a stream of single-character *marks* -- one Unicode codepoint per cantillation
accent (plus meteg/paseq/sof-pasuq/puncta), placeholder ``X`` per base consonant, and
maqaf (``-``) / space word boundaries -- as defined in `accent_marks`.  This module
produces that mark body straight from the canonical ``-kq-u`` Unicode verses.

It is the partial inverse of `wlc_uword.uword`, but only faithful to what the scanner
and `lexical_validation` actually read:

* **Letters** are opaque filler (the rules key on the marks and the word boundaries),
  so each base consonant becomes a single ``LETTER`` placeholder and vowels/points are
  dropped -- real reverse-transliteration is unnecessary.
* **Accents** pass through as their own codepoint.  The five M-C codepoint conflations
  no longer need distinct codes: pashta and telisha-qetana keep both their stress-helper
  and their main occurrence (the scanner merges an adjacent same-accent run into one
  token), and the swallowed secondaries -- a telisha-gedola or gershayim that shares its
  base letter with another accent, or a repeated telisha-gedola -- are dropped here
  (`word_to_marks`).
* **Prepositive accents** (yetiv, geresh-muqdam, dehi, telisha-gedola) are relocated to
  the front of the word's mark sequence, undoing `wlc_uword._PREPOS_PATT`'s move past an
  accent on the first consonant, so the scanner reads the accents in M-C order.
* **Boundaries / punctuation** are reproduced exactly: maqaf -> ``-``, inter-word gaps
  -> space, paseq / sof pasuq / puncta as their own codepoints.
* **Ketiv-qere & notes** reproduce the token stream the M-C source presented: the ketiv
  is a swallowed ``*<consonants>`` atom, the qere ``**`` + its pointed body, and
  ``notes`` are appended verbatim (the ``]N`` markers the legarmeh/mayela lookaheads
  key on).

Parity with the Phase-1 outputs is verified by a zero-diff of the git-tracked
``*_ag.txt`` outputs (issue #9, Phase 2).
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from accgram import accent_marks as am
from accgram import rtms_data
from cmn.wlc_book_codes import wlc_bb_to_goerwitz_book_name

# --- codepoint classification -------------------------------------------------

_MAQAF = "־"  # U+05BE; emitted as the boundary mark ``-``

# Cantillation-accent codepoints other than the conflated/positional ones pass
# straight through as their own mark.  Meteg, paseq, sof-pasuq and the puncta are
# kept too (their codepoints are already their marks).
_KEPT_NON_ACCENT = frozenset(
    (am.METEG, am.PASEQ, am.SOF_PASUQ, am.UPPER_DOT, am.LOWER_DOT)
)

# Prepositive accents: written at the word's start but relocated by
# `wlc_uword._PREPOS_PATT` to just after the first consonant -- a move that can carry
# them past an accent on that first consonant, inverting the accent order the scanner
# reads.  We restore M-C order by emitting them at the front of the word's marks.
# (Gershayim 12 and the secondary telisha-gedola 44 are *also* prepositive in M-C but
# are swallowed secondaries dropped below, so only these four reach the front.)
_PREPOSITIVE_MARKS = frozenset(
    (am.YETIV, am.GERESH_MUQDAM, am.DEHI, am.TELISHA_GEDOLA)
)


def _is_base_letter(ch: str) -> bool:
    return "א" <= ch <= "ת"


def _is_accent(ch: str) -> bool:
    """A real cantillation accent (U+0591..U+05AE) -- meteg (U+05BD) excluded."""
    return "֑" <= ch <= "֮"


# --- word transcoding ---------------------------------------------------------


def word_to_marks(word: str) -> str:
    """Transcode one Unicode word/atom into its scanner-ready mark string.

    Letters become ``X`` placeholders, points are dropped, accents pass through as
    their codepoints (swallowed-secondary telisha-gedola / gershayim dropped), and
    maqaf / paseq / sof pasuq / puncta are emitted verbatim.  Prepositive accents are
    restored to the front of the mark sequence (see `_PREPOSITIVE_MARKS`).
    """
    # Pass 1: assign each character a "letter group" index (incremented on each base
    # consonant) and tally the non-meteg accents per group, so the cluster test below
    # can tell whether an accent shares its base letter with another accent.
    group_of: list[int] = []
    group = 0
    accents_per_group: dict[int, int] = {}
    for ch in word:
        if _is_base_letter(ch):
            group += 1
        group_of.append(group)
        if _is_accent(ch):
            accents_per_group[group] = accents_per_group.get(group, 0) + 1

    # Pass 2: build the ordered mark sequence and the skeleton of letters/maqaf,
    # marking where marks go.  Prepositive accent marks are pulled to the front.
    skeleton: list[str | None] = []  # str = literal char; None = "a mark slot here"
    prepos_marks: list[str] = []
    other_marks: list[str] = []
    telg_seen = 0
    for i, ch in enumerate(word):
        if _is_base_letter(ch):
            skeleton.append(am.LETTER)
            continue
        if ch == _MAQAF:
            skeleton.append(am.MAQAF)
            continue
        mark: str | None = None
        if _is_accent(ch):
            clustered = accents_per_group[group_of[i]] >= 2
            if ch == am.TELISHA_GEDOLA:
                telg_seen += 1
                # A telisha-gedola sharing its letter with another accent, or the
                # non-first of a repeated pair, is the swallowed secondary (M-C 44).
                if clustered or telg_seen > 1:
                    continue
                mark = am.TELISHA_GEDOLA
            elif ch == am.GERSHAYIM and clustered:
                # A gershayim sharing its letter with another accent is the swallowed
                # secondary (M-C 12, the gn 5:29 / Zeph 2:15 double-prepositive anomaly).
                continue
            else:
                mark = ch  # the accent codepoint is its own mark
        elif ch in _KEPT_NON_ACCENT:
            mark = ch
        if mark is None:
            continue  # a point/vowel/dagesh/shin-dot/etc. -> dropped (scanner filler)
        skeleton.append(None)
        if mark in _PREPOSITIVE_MARKS:
            prepos_marks.append(mark)
        else:
            other_marks.append(mark)

    marks = iter(prepos_marks + other_marks)
    return "".join(next(marks) if part is None else part for part in skeleton)


def _notes_suffix(notes: object) -> str:
    """The ``]N`` markers appended after a word, verbatim (legarmeh/mayela lookaheads
    key on ``]<digit>``).

    The kq-u loader collapses a ``notes`` list into one string
    (`rtms_data._collapse_wlc_notes_to_string`), so accept either form.
    """
    if isinstance(notes, str):
        return notes
    if isinstance(notes, list):
        return "".join(n for n in notes if isinstance(n, str))
    return ""


def _vel_to_marks(vel: object) -> str:
    """Transcode one verse element to its mark fragment."""
    if isinstance(vel, str):
        return word_to_marks(vel)
    if not isinstance(vel, dict):
        return ""

    sam = vel.get("sam_pe_inun")
    if isinstance(sam, str):
        # Petuhah/setumah/nun-inversum: a lone P/S/N atom; N re-acquires its ``]8`` note
        # (mirrors wlc_read_and_parse_mdc._distinguish_sam_pe_inun).  Scanner swallows it.
        return "N]8" if sam == "N" else sam

    kq = vel.get("kq")
    if kq is not None:
        return _kq_to_marks(kq)

    word = vel.get("word")
    if isinstance(word, str):
        return word_to_marks(word) + _notes_suffix(vel.get("notes"))
    return ""


def _kq_to_marks(kq: object) -> str:
    """Transcode a ketiv-qere element to ``*<ketiv> **<qere>``.

    The scanner swallows the ketiv whole (``\\*[^* \\r\\n-]+``) and the ``**`` of the
    qere, then scans the (pointed) qere normally -- so only the qere carries grammar-
    visible marks.  An implicit-empty side (qere perpetuum / ketiv-only) emits the
    ``*kk`` / ``**qq`` placeholder the M-C source used, both swallowed.
    """
    ketiv, qere = kq if isinstance(kq, (list, tuple)) and len(kq) == 2 else ([], [])
    ketiv_words = [w for w in (_kq_word(v) for v in ketiv) if w]
    qere_words = [w for w in (_kq_word(v) for v in qere) if w]
    ketiv_part = "*" + "-".join(ketiv_words) if ketiv_words else "*kk"
    qere_part = "**" + "-".join(qere_words) if qere_words else "**qq"
    return f"{ketiv_part} {qere_part}"


def _kq_word(vel: object) -> str:
    if isinstance(vel, str):
        return word_to_marks(vel)
    if isinstance(vel, dict):
        word = vel.get("word")
        if isinstance(word, str):
            return word_to_marks(word) + _notes_suffix(vel.get("notes"))
    return ""


def verse_to_marks(verse: dict) -> str:
    """Transcode one ``-kq-u`` verse ``{bcv, vels}`` into the scanner-ready mark body."""
    vels = verse.get("vels")
    if not isinstance(vels, list):
        return ""
    parts: list[str] = []
    prev_ended_maqaf = False
    for vel in vels:
        frag = _vel_to_marks(vel)
        if not frag:
            continue
        if parts and not prev_ended_maqaf:
            parts.append(" ")
        parts.append(frag)
        prev_ended_maqaf = frag.endswith(am.MAQAF)
    return "".join(parts)


# --- book-text builder (drop-in for split_wlc.split_wlc_to_book_texts) ---------


def build_book_texts(
    wlc422_kq_u_dir: Path,
    keep_line_fn=None,
) -> "OrderedDict[str, str]":
    """Per-book scanner-ready text from the ``-kq-u`` JSON, mirroring the shape
    `split_wlc.split_wlc_to_book_texts` returned from ``wlc422_ps.txt``.

    Each value is a goerwitz book-name header line followed by normalized
    ``ch:vr <body>`` lines (the 2-char WLC book code dropped), in source order.
    ``keep_line_fn(bb, chnu, vrnu)`` (the genre filter) may exclude verses.
    """
    index = rtms_data.load_wlc422_index(wlc422_kq_u_dir)

    per_book: OrderedDict[str, list[str]] = OrderedDict()
    for bcv, verse in index.items():
        bb, chnu, vrnu = _split_bcv(bcv)
        if keep_line_fn is not None and not keep_line_fn(bb, chnu, vrnu):
            continue
        body = verse_to_marks(verse)
        per_book.setdefault(bb, []).append(f"{chnu}:{vrnu} {body}")

    book_texts: OrderedDict[str, str] = OrderedDict()
    for bb, lines in per_book.items():
        header = wlc_bb_to_goerwitz_book_name(bb)
        book_texts[bb] = "".join([f"{header}\n", *(f"{ln}\n" for ln in lines)])
    return book_texts


def _split_bcv(bcv: str) -> tuple[str, int, int]:
    """``gn1:1`` -> ``("gn", 1, 1)``."""
    bb = bcv[:2]
    chv = bcv[2:]
    ch, _colon, vr = chv.partition(":")
    return bb, int(ch), int(vr)
