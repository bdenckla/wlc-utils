r"""Transcode a `-kq-u` Unicode WLC verse into the Michigan-Claremont (M-C) accent
*body* the PLY scanners consume (issue #9, Phase 1).

The PLY prose/poetic scanners (`ply_scanner` / `ply_scanner_poetic`) read each verse
as the M-C accent text that follows ``ch:vr `` -- a stream of 2-digit accent codes
interleaved with letters/vowels, with maqaf (``-``) and space word boundaries, paseq
(``05``), sof pasuq (``00``), ketiv ``*``/``**`` markers and ``]N`` note markers.  This
module produces a byte-stream that *scans identically*, sourced from the canonical
``-kq-u`` Unicode verses instead of the retired ``wlc422_ps.txt``.

It is the partial inverse of `wlc_uword.uword`, but only faithful to what the scanner
and `lexical_validation` actually read:

* **Letters** are opaque filler to the scanner (its rules key on the 2-digit codes and
  the word boundaries), so each base consonant becomes a single placeholder consonant
  and vowels/points are dropped -- real reverse-transliteration is unnecessary.
* **Accents** invert the codepoint -> code map.  Five codepoints are conflated in M-C
  (`wlc_uword._ACCENTS`): pashta ``33``/``03``, telisha-qetana ``24``/``04``,
  telisha-gedola ``14``/``44``, gershayim ``12``/``62`` and meteg/silluq ``35``/``75``/
  ``95``.  The positional helper/main split is re-derived (see `_accent_code`); for
  meteg any of ``35``/``75``/``95`` scans identically, so ``75`` is always emitted.
* **Boundaries / punctuation** the scanner lookaheads reference are reproduced exactly:
  maqaf -> ``-``, inter-word gaps -> space, paseq -> ``05``, sof pasuq -> ``00``,
  upper/lower puncta -> ``52``/``53``.
* **Ketiv-qere & notes** reproduce the token stream the M-C source presented: the ketiv
  is emitted as a swallowed ``*<consonants>`` atom, the qere as ``**`` + its pointed
  body, and ``notes`` are appended verbatim (the ``]N`` markers the legarmeh/mayela
  lookaheads key on).

Parity is provable by construction and verified by a zero-diff of the git-tracked
``*_ag.txt`` outputs (issue #9, Phase 1, step 6).
"""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from accgram import rtms_data
from cmn.wlc_book_codes import wlc_bb_to_goerwitz_book_name

# --- codepoint classification -------------------------------------------------

_PLACEHOLDER = "X"  # one per base consonant; opaque scanner filler

_MAQAF = "־"
_PASEQ = "׀"
_SOF_PASUQ = "׃"
_UPPER_DOT = "ׄ"
_LOWER_DOT = "ׅ"
_METEG = "ֽ"

# Each cantillation-accent codepoint -> the canonical (main) M-C 2-digit code.  The
# five conflated codepoints (pashta, telisha-qetana, telisha-gedola, gershayim) get the
# *main* code here; `_accent_code` overrides it with the helper/secondary code where the
# positional rule calls for it.  Meteg (U+05BD) is handled separately (always ``75``).
_ACCENT_MAIN_CODE: dict[str, str] = {
    "֑": "92",  # etnahta            -> atnax
    "֒": "01",  # segol (accent)     -> segolta
    "֓": "65",  # shalshelet
    "֔": "80",  # zaqef qatan
    "֕": "85",  # zaqef gadol
    "֖": "73",  # tipeha
    "֗": "81",  # revia
    "֘": "82",  # zarqa / tsinnorit stress-helper
    "֙": "03",  # pashta             (main; helper = 33)
    "֚": "10",  # yetiv
    "֛": "91",  # tevir
    "֜": "61",  # geresh
    "֝": "11",  # geresh muqdam
    "֞": "62",  # gershayim          (main; secondary = 12)
    "֟": "84",  # qarney para (pazer gadol)
    "֠": "14",  # telisha gedola     (main; helper/secondary = 44)
    "֡": "83",  # pazer
    "֣": "74",  # munah
    "֤": "70",  # mahapakh
    "֥": "71",  # merkha
    "֦": "72",  # merkha kefula
    "֧": "94",  # darga
    "֨": "63",  # qadma (azla)
    "֩": "04",  # telisha qetana     (main; helper = 24)
    "֪": "93",  # yerah ben yomo (galgal)
    "֫": "60",  # ole
    "֬": "64",  # iluy
    "֭": "13",  # dehi
    "֮": "02",  # zinor (zarqa/tsinnor)
}

# Codepoints emitted verbatim (not via the accent table).
_DIRECT_CODE: dict[str, str] = {
    _PASEQ: "05",
    _SOF_PASUQ: "00",
    _UPPER_DOT: "52",
    _LOWER_DOT: "53",
}

# A conflated accent codepoint -> (helper_or_secondary_code, main_code).
_PASHTA = "֙"
_TELISHA_Q = "֩"
_TELISHA_G = "֠"
_GERSHAYIM = "֞"


def _is_base_letter(ch: str) -> bool:
    return "א" <= ch <= "ת"


def _is_accent(ch: str) -> bool:
    """A real cantillation accent (U+0591..U+05AE) -- meteg (U+05BD) excluded."""
    return "֑" <= ch <= "֮"


# --- word transcoding ---------------------------------------------------------


# M-C *prepositive* codes (yetiv 10, geresh-muqdam 11, garshayim 12, dehi 13,
# telisha-gedola 14): written at the word's start, then relocated by
# `wlc_uword._PREPOS_PATT` to just after the first consonant -- a move that can carry
# them *past* an accent on that first consonant (e.g. a munah), inverting the accent
# order the scanner reads.  We restore the M-C order by emitting these codes at the
# front of the atom's code sequence.  Keyed on the *emitted* code, not the codepoint:
# garshayim 62 and telisha 44 share a codepoint with 12/14 but are NOT prepositive.
_PREPOSITIVE_CODES = {"10", "11", "12", "13", "14"}


def word_to_mc(word: str) -> str:
    """Transcode one Unicode word/atom into its scanner-equivalent M-C string.

    Letters become placeholder consonants, points are dropped, accents become their
    M-C codes (with the conflated helper/main split re-derived), and maqaf / paseq /
    sof pasuq / puncta are emitted verbatim.  Prepositive accents are restored to the
    front of the code sequence (see `_PREPOSITIVE`).
    """
    # Pass 1: assign each character a "letter group" index (incremented on each base
    # consonant) and tally the non-meteg accents per group, plus the totals of the
    # conflated accents that need a positional helper/main split.
    group_of: list[int] = []
    group = 0
    accents_per_group: dict[int, int] = {}
    pashta_total = telq_total = telg_total = 0
    for ch in word:
        if _is_base_letter(ch):
            group += 1
        group_of.append(group)
        if _is_accent(ch):
            accents_per_group[group] = accents_per_group.get(group, 0) + 1
            pashta_total += ch == _PASHTA
            telq_total += ch == _TELISHA_Q
            telg_total += ch == _TELISHA_G

    # Pass 2: build the ordered code sequence (accents/meteg/paseq/sof-pasuq/puncta) and
    # the skeleton of letters/maqaf, marking where codes go.  Prepositive accent codes
    # are pulled to the front of the code sequence.
    skeleton: list[str | None] = []  # str = literal char; None = "a code slot here"
    prepos_codes: list[str] = []
    other_codes: list[str] = []
    pashta_seen = telq_seen = telg_seen = 0
    for i, ch in enumerate(word):
        if _is_base_letter(ch):
            skeleton.append(_PLACEHOLDER)
            continue
        if ch == _MAQAF:
            skeleton.append("-")
            continue
        code: str | None = None
        if ch == _METEG:
            code = "75"
        elif _is_accent(ch):
            clustered = accents_per_group[group_of[i]] >= 2
            if ch == _PASHTA:
                pashta_seen += 1
                code = "33" if pashta_seen < pashta_total else "03"
            elif ch == _TELISHA_Q:
                telq_seen += 1
                code = "24" if telq_seen < telq_total else "04"
            elif ch == _TELISHA_G:
                telg_seen += 1
                # A telisha-gedola sharing its letter with another accent is the
                # swallowed secondary (44); so is the non-first of a separated pair
                # (the 2k 17:24 main+helper).  Otherwise it is the real disjunctive 14.
                code = "44" if clustered or telg_seen > 1 else "14"
            elif ch == _GERSHAYIM:
                # A gershayim sharing its letter with another accent is the swallowed
                # secondary 12 (the gn 5:29 / Zeph 2:15 double-prepositive anomaly).
                code = "12" if clustered else "62"
            else:
                code = _ACCENT_MAIN_CODE[ch]
        elif ch in _DIRECT_CODE:
            code = _DIRECT_CODE[ch]
        if code is None:
            continue  # a point/vowel/dagesh/shin-dot/etc. -> dropped (scanner filler)
        skeleton.append(None)
        if code in _PREPOSITIVE_CODES:
            prepos_codes.append(code)
        else:
            other_codes.append(code)

    codes = iter(prepos_codes + other_codes)
    return "".join(next(codes) if part is None else part for part in skeleton)


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


def _vel_to_mc(vel: object) -> tuple[str, bool]:
    """Transcode one verse element to its M-C fragment.

    Returns ``(fragment, joins_left)`` where ``joins_left`` is True when this fragment
    must abut the previous one with no separating space -- i.e. the previous fragment
    ended with a maqaf, so the run is one maqaf-joined accent word.
    """
    if isinstance(vel, str):
        return word_to_mc(vel), False
    if not isinstance(vel, dict):
        return "", False

    sam = vel.get("sam_pe_inun")
    if isinstance(sam, str):
        # Petuhah/setumah/nun-inversum: a lone P/S/N atom; N re-acquires its ``]8`` note
        # (mirrors wlc_read_and_parse_mdc._distinguish_sam_pe_inun).  Scanner swallows it.
        return ("N]8" if sam == "N" else sam), False

    kq = vel.get("kq")
    if kq is not None:
        return _kq_to_mc(kq), False

    word = vel.get("word")
    if isinstance(word, str):
        return word_to_mc(word) + _notes_suffix(vel.get("notes")), False
    return "", False


def _kq_to_mc(kq: object) -> str:
    """Transcode a ketiv-qere element to ``*<ketiv> **<qere>``.

    The scanner swallows the ketiv whole (``\\*[^* \\r\\n-]+``) and the ``**`` of the
    qere, then scans the (pointed) qere normally -- so only the qere carries grammar-
    visible accents.  An implicit-empty side (qere perpetuum / ketiv-only) emits the
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
        return word_to_mc(vel)
    if isinstance(vel, dict):
        word = vel.get("word")
        if isinstance(word, str):
            return word_to_mc(word) + _notes_suffix(vel.get("notes"))
    return ""


def verse_to_mc_body(verse: dict) -> str:
    """Transcode one ``-kq-u`` verse ``{bcv, vels}`` into the scanner-ready M-C body."""
    vels = verse.get("vels")
    if not isinstance(vels, list):
        return ""
    parts: list[str] = []
    prev_ended_maqaf = False
    for vel in vels:
        frag, _join = _vel_to_mc(vel)
        if not frag:
            continue
        if parts and not prev_ended_maqaf:
            parts.append(" ")
        parts.append(frag)
        prev_ended_maqaf = frag.endswith("-")
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
        body = verse_to_mc_body(verse)
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
