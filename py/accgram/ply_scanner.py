"""Hand-written scanner: reproduces the GG-state token stream of tnk2acc.l.

Stage 1 / Phase B (walking skeleton).  This is the *minimal* scanner: it
handles the new-format verse structure (bookname -> chapter -> verse -> accent
scan) and the GG-state accent codes that the Obadiah corpus exercises, plus the
one trailing-context rule a verse cannot terminate without (silluq).

Deferred to Phase D (the four trailing-context rules + has_legarmeh state):
  - mayela        (73/<lookahead>(00|92))   -> here 73 is always TIFCHA
  - legarmeh      (74{TEXT}05/<lookahead>81) and the has_legarmeh 17-passage
                  list                       -> here 74 is always MUNACH
  - shalshelet/methiga-zaqef/segolta/zarqa   -> codes absent from Obadiah
The silluq lookahead *is* implemented because, without it, a metheg/silluq code
(35|75|95) is swallowed and the verse has no silluq_phrase to reduce.

Faithfulness notes (flex semantics reproduced):
  - longest match wins; ties are broken by rule order (the order below mirrors
    the order of the rules in tnk2acc.l's GG block);
  - lex trailing context (`r/s`) is expressed as a regex lookahead `(?=s)`, so
    only `r` is consumed, exactly as flex consumes only the left part.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    """A grammar token: PLY token type plus the leaf-name string (yylval.leaf)."""

    type: str
    leaf: str


# --- verse-structure line patterns (new format), from tnk2acc.l ----------------
# Bookname at the head of a chapter: ^([1234][ \t]*)?[A-Z][a-z]+[ \t]*$
_BOOKNAME_RE = re.compile(r"^([1234][ \t]*)?[A-Z][a-z]+[ \t]*$")
# A verse line: chapter ':' verse ' ' accent-codes.  The flex lexer splits this
# across the EE (chapter, returns TILDE) and FF (verse number) start states; in
# the line-oriented new format we can recover chapter/verse directly.
_VERSE_RE = re.compile(r"^([1-9][0-9]*):([1-9][0-9]*)[ \t](.*)$")


# --- GG-state accent rules -----------------------------------------------------
# Each entry: (compiled regex anchored at the scan position, token type or None).
# token type None == "swallow" (consume, emit nothing).  Trailing context is a
# lookahead so it is not consumed.  TEXT in tnk2acc.l is [^ \r\n\-]*.
_TEXT = r"[^ \r\n\-]*"

_GG_RULES: list[tuple[re.Pattern[str], str | None]] = [
    (re.compile(r"00"), "SOFPASUQ"),
    # silluq: 35|75|95 immediately before sof pasuq (00), excluding mayela etc.
    (re.compile(r"(?:35|75|95)(?=[^ 379\r\n\-?~]*00)"), "SILLUQ"),
    (re.compile(r"92"), "ATNACH"),
    (re.compile(r"80"), "ZAQEF"),
    (re.compile(r"85"), "ZAQEFGADOL"),
    (re.compile(r"81"), "REVIA"),
    # mayela deferred (Phase D): 73 is TIFCHA here.
    (re.compile(r"73"), "TIFCHA"),
    (re.compile(r"(?:33" + _TEXT + r")?03"), "PASHTA"),
    (re.compile(r"10"), "YETIV"),
    (re.compile(r"91"), "TEVIR"),
    (re.compile(r"61"), "GERESH"),
    (re.compile(r"62"), "GERSHAYIM"),
    (re.compile(r"83"), "PAZER"),
    (re.compile(r"84"), "PAZERGADOL"),
    (re.compile(r"14"), "TELISHAGEDOLA"),
    # legarmeh deferred (Phase D): 74 is MUNACH here.
    (re.compile(r"74"), "MUNACH"),
    (re.compile(r"70"), "MAHPAK"),
    (re.compile(r"71"), "MEREKA"),
    (re.compile(r"72"), "MEREKAKEFULA"),
    (re.compile(r"94"), "DARGA"),
    (re.compile(r"63"), "AZLA"),
    (re.compile(r"24" + _TEXT + r"04"), "TELISHAQETANNA"),
    (re.compile(r"04|24"), "TELISHAQETANNA"),
    (re.compile(r"93"), "GALGAL"),
    # leftover schwa/medial telisha/paseq/tsinnorit/puncta -> swallowed
    (re.compile(r"35|75|95|44|05|82|52"), None),
    # "**" and "*<non-space>+" -> swallowed
    (re.compile(r"\*\*"), None),
    (re.compile(r"\*[^* \r\n\-]+"), None),
    # catch-all: any other single char -> swallowed
    (re.compile(r".", re.DOTALL), None),
]

# leaf-name (yylval.leaf) for each token type, from tnk2acc.l.
_LEAF: dict[str, str] = {
    "SOFPASUQ": "sof pasuq",
    "SILLUQ": "silluq",
    "ATNACH": "atnach",
    "ZAQEF": "zaqef",
    "ZAQEFGADOL": "zaqefgadol",
    "REVIA": "revia",
    "TIFCHA": "tifcha",
    "PASHTA": "pashta",
    "YETIV": "yetiv",
    "TEVIR": "tevir",
    "GERESH": "geresh",
    "GERSHAYIM": "gershayim",
    "PAZER": "pazer",
    "PAZERGADOL": "pazergadol",
    "TELISHAGEDOLA": "telishagedola",
    "MUNACH": "munach",
    "MAHPAK": "mahpak",
    "MEREKA": "mereka",
    "MEREKAKEFULA": "merekakefula",
    "DARGA": "darga",
    "AZLA": "azla",
    "TELISHAQETANNA": "telishaqetanna",
    "GALGAL": "galgal",
}


def scan_accents(body: str) -> list[Token]:
    """Scan the GG-state accent codes of one verse body into a token list.

    Emits accent tokens followed by a terminating SOFPASUQ.  Mirrors flex:
    at each position pick the longest match; break ties by rule order.  Stops
    after the first 00 (sof pasuq), which in flex returns to the EE state.
    """
    tokens: list[Token] = []
    pos = 0
    n = len(body)
    while pos < n:
        best_len = 0
        best_type: str | None = None
        best_is_rule = False
        for regex, ttype in _GG_RULES:
            m = regex.match(body, pos)
            if m is None:
                continue
            length = m.end() - m.start()
            if length > best_len:
                best_len = length
                best_type = ttype
                best_is_rule = True
        # The catch-all `.` guarantees best_is_rule is always True for pos < n.
        assert best_is_rule, f"no rule matched at position {pos} in {body!r}"
        advance = max(best_len, 1)
        if best_type is not None:
            tokens.append(Token(best_type, _LEAF[best_type]))
            if best_type == "SOFPASUQ":
                break
        pos += advance
    return tokens


@dataclass(frozen=True)
class Verse:
    reference: str
    tokens: list[Token]  # TILDE, accent tokens..., SOFPASUQ


def scan_book(text: str) -> list[Verse]:
    """Scan a whole new-format book file into per-verse token streams.

    Each verse is delimited by TILDE (emitted by the chapter rule at the head of
    every verse line) and SOFPASUQ (the 00 accent code).
    """
    book = ""
    verses: list[Verse] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r\n")
        mv = _VERSE_RE.match(line)
        if mv is not None:
            ch, vs, rest = mv.group(1), mv.group(2), mv.group(3)
            reference = f"{book} {ch}:{vs}"
            tokens = [Token("TILDE", "")] + scan_accents(rest)
            verses.append(Verse(reference=reference, tokens=tokens))
            continue
        if _BOOKNAME_RE.match(line):
            book = line.strip()
    return verses
