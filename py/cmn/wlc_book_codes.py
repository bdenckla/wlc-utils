from __future__ import annotations

from dataclasses import dataclass
import re

from mb_cmn import bib_locales as tbn


@dataclass(frozen=True)
class WlcBookCodeInfo:
    bk39id: str
    goerwitz_book_name: str | None = None


_GOERWITZ_BOOK_HEADER_RE = re.compile(r"^(?:[1234][ \t]*)?[A-Z][a-z]+[ \t]*$")


# Single source of truth for WLC 4.22 2-char book codes.
_WLC_BB_INFO = {
    "gn": WlcBookCodeInfo(bk39id=tbn.BK_GENESIS),
    "ex": WlcBookCodeInfo(bk39id=tbn.BK_EXODUS),
    "lv": WlcBookCodeInfo(bk39id=tbn.BK_LEVIT),
    "nu": WlcBookCodeInfo(bk39id=tbn.BK_NUMBERS),
    "dt": WlcBookCodeInfo(bk39id=tbn.BK_DEUTER),
    "js": WlcBookCodeInfo(bk39id=tbn.BK_JOSHUA),
    "ju": WlcBookCodeInfo(bk39id=tbn.BK_JUDGES),
    "1s": WlcBookCodeInfo(bk39id=tbn.BK_FST_SAM),
    "2s": WlcBookCodeInfo(bk39id=tbn.BK_SND_SAM),
    "1k": WlcBookCodeInfo(bk39id=tbn.BK_FST_KGS),
    "2k": WlcBookCodeInfo(bk39id=tbn.BK_SND_KGS),
    "is": WlcBookCodeInfo(bk39id=tbn.BK_ISAIAH),
    "je": WlcBookCodeInfo(bk39id=tbn.BK_JEREM),
    "ek": WlcBookCodeInfo(bk39id=tbn.BK_EZEKIEL),
    "ho": WlcBookCodeInfo(bk39id=tbn.BK_HOSHEA),
    "jl": WlcBookCodeInfo(bk39id=tbn.BK_JOEL),
    "am": WlcBookCodeInfo(bk39id=tbn.BK_AMOS),
    "ob": WlcBookCodeInfo(bk39id=tbn.BK_OVADIAH),
    "jn": WlcBookCodeInfo(bk39id=tbn.BK_JONAH),
    "mi": WlcBookCodeInfo(bk39id=tbn.BK_MIKHAH),
    "na": WlcBookCodeInfo(bk39id=tbn.BK_NAXUM),
    "hb": WlcBookCodeInfo(bk39id=tbn.BK_XABA),
    "zp": WlcBookCodeInfo(bk39id=tbn.BK_TSEF),
    "hg": WlcBookCodeInfo(bk39id=tbn.BK_XAGGAI),
    "zc": WlcBookCodeInfo(bk39id=tbn.BK_ZEKHAR),
    "ma": WlcBookCodeInfo(bk39id=tbn.BK_MALAKHI),
    "ps": WlcBookCodeInfo(bk39id=tbn.BK_PSALMS),
    "pr": WlcBookCodeInfo(bk39id=tbn.BK_PROV),
    "jb": WlcBookCodeInfo(bk39id=tbn.BK_JOB, goerwitz_book_name="Defeatmatchforjob"),
    # Above is an attempt to avoid the special treatment of strings starting with "Job"
    # in accents-1.1.4/tnk2acc.c: strncmp (yytext, "Job", 3)
    "ca": WlcBookCodeInfo(bk39id=tbn.BK_SONG, goerwitz_book_name="Song"),
    "ru": WlcBookCodeInfo(bk39id=tbn.BK_RUTH),
    "lm": WlcBookCodeInfo(bk39id=tbn.BK_LAMENT),
    "ec": WlcBookCodeInfo(bk39id=tbn.BK_QOHELET),
    "es": WlcBookCodeInfo(bk39id=tbn.BK_ESTHER),
    "da": WlcBookCodeInfo(bk39id=tbn.BK_DANIEL),
    "er": WlcBookCodeInfo(bk39id=tbn.BK_EZRA),
    "ne": WlcBookCodeInfo(bk39id=tbn.BK_NEXEM),
    "1c": WlcBookCodeInfo(bk39id=tbn.BK_FST_CHR),
    "2c": WlcBookCodeInfo(bk39id=tbn.BK_SND_CHR),
}

_BK39ID_TO_WLC_BB = {info.bk39id: bb for bb, info in _WLC_BB_INFO.items()}


def wlc_bb_to_bk39id(bb: str) -> str:
    info = _WLC_BB_INFO.get(bb)
    if info is None:
        raise ValueError(f"Unknown WLC book code in input: {bb}")
    return info.bk39id


def bk39id_to_wlc_bb(bk39id: str) -> str:
    bb = _BK39ID_TO_WLC_BB.get(bk39id)
    if bb is None:
        raise ValueError(f"Unknown bk39id in input: {bk39id}")
    return bb


def wlc_bb_codes() -> tuple[str, ...]:
    return tuple(_WLC_BB_INFO.keys())


def wlc_bb_to_goerwitz_book_name(bb: str) -> str:
    info = _WLC_BB_INFO.get(bb)
    if info is None:
        raise ValueError(f"Unknown WLC book code in input: {bb}")
    book_name = info.goerwitz_book_name or info.bk39id
    if _GOERWITZ_BOOK_HEADER_RE.match(book_name) is None:
        raise ValueError(
            "Book name does not conform to goerwitz header expectations: "
            f"bb={bb} name={book_name}"
        )
    return book_name
