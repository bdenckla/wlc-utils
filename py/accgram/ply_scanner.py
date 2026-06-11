r"""Hand-written scanner: reproduces the GG-state token stream of tnk2acc.l.

Stage 1 / Phase D (full scanner including the four trailing-context rules).
Handles the new-format verse structure (bookname -> chapter -> verse -> accent
scan) and the complete GG-state accent table, including the four lex
*trailing-context* rules that PLY's lexer cannot express:

  - silluq    35|75|95/[^ 379...]*00        (a true silluq is a metheg/silluq
              immediately before sof pasuq)
  - mayela    73/<allowed>*(00|92)          (tifcha variant before atnach/silluq)
  - legarmeh  74{TEXT}05/[^12368]*...81      (munach+paseq before revia)
  - chapter   ^[1-9][0-9]*:/[1-9]            (new-format verse lookahead; handled
              by the line-oriented _VERSE_RE below)

plus the stateful `has_legarmeh` special case (17-passage list + 1Sam 14:47
"second occurrence only" counter), ported verbatim from tnk2acc.l.

Faithfulness notes (flex semantics reproduced):
  - longest match wins; ties are broken by rule order (the order of _GG_RULES
    below mirrors the order of the rules in tnk2acc.l's GG block);
  - lex trailing context (`r/s`) is expressed as a regex lookahead `(?=s)`, so
    only `r` is consumed, exactly as flex consumes only the left part;
  - flex's `{TEXT}` (= `[^ \r\n\-]*`) is greedy and stays within one
    maqqef/space-delimited word; Python `re` greediness reproduces the longest
    match (backtracking to the rightmost terminator).

Quirk reproduced (`has_legarmeh`): in the *new* format the lexer's `location`
holds the **full** bookname ("Genesis 28:9"), while the 17-passage list uses
*abbreviations* ("Gen 28:9").  They therefore never match -- except "Ruth",
whose full name equals its abbreviation.  So across the whole new-format corpus
the only verse where has_legarmeh fires is **Ruth 1:2** (a munach+paseq not
before revia).  Everywhere else 74{TEXT}05-not-before-revia is plain munach.
We port the list verbatim so this falls out naturally and is self-documenting.
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
# the line-oriented new format we can recover chapter/verse directly.  Note the
# chapter rule's trailing context `:/[1-9]` requires a digit after the colon,
# which the explicit `:([1-9][0-9]*)` below reproduces.
_VERSE_RE = re.compile(r"^([1-9][0-9]*):([1-9][0-9]*)[ \t](.*)$")


# --- GG-state accent rules -----------------------------------------------------
# Each entry: (compiled regex anchored at the scan position, token type or None).
# token type None == "swallow" (consume, emit nothing).  The sentinel
# "_LEGARMEH_OR_MUNACH" is resolved at emit time via has_legarmeh(location).
# Trailing context is a lookahead so it is not consumed.  TEXT is [^ \r\n\-]*.
_TEXT = r"[^ \r\n\-]*"

# mayela right context:  73/(([^ 0123468\r\n\-]|\-[^ 0123468]*)*(\][0-9])?)*(00|92)
_MAYELA_LA = r"(?=(?:(?:[^ 0123468\r\n\-]|-[^ 0123468]*)*(?:\][0-9])?)*(?:00|92))"
# legarmeh right context:  74{TEXT}05/[^12368]*(\][0-9])?[^12368]*81
_LEGARMEH_LA = r"(?=[^12368]*(?:\][0-9])?[^12368]*81)"

_GG_RULES: list[tuple[re.Pattern[str], str | None]] = [
    (re.compile(r"00"), "SOFPASUQ"),
    # silluq: 35|75|95 immediately before sof pasuq (00), excluding mayela etc.
    (re.compile(r"(?:35|75|95)(?=[^ 379\r\n\-?~]*00)"), "SILLUQ"),
    (re.compile(r"92"), "ATNACH"),
    (re.compile(r"(?:01" + _TEXT + r")?01"), "SEGOLTA"),
    (re.compile(r"65" + _TEXT + r"05"), "SHALSHELET"),
    (re.compile(r"63[^01234680]*80"), "METHIGAZAQEF"),
    (re.compile(r"80"), "ZAQEF"),
    (re.compile(r"85"), "ZAQEFGADOL"),
    (re.compile(r"81"), "REVIA"),
    # mayela (trailing context): 73 before 00/92 with only ga`ya intervening.
    (re.compile(r"73" + _MAYELA_LA), "MAYELA"),
    (re.compile(r"73"), "TIFCHA"),
    (re.compile(r"(?:82" + _TEXT + r")?02"), "ZARQA"),
    (re.compile(r"(?:33" + _TEXT + r")?03"), "PASHTA"),
    (re.compile(r"10"), "YETIV"),
    (re.compile(r"91"), "TEVIR"),
    (re.compile(r"61"), "GERESH"),
    (re.compile(r"62"), "GERSHAYIM"),
    (re.compile(r"83"), "PAZER"),
    (re.compile(r"84"), "PAZERGADOL"),
    (re.compile(r"14"), "TELISHAGEDOLA"),
    # legarmeh (trailing context): munach+paseq before a subsequent revia.
    (re.compile(r"74" + _TEXT + r"05" + _LEGARMEH_LA), "LEGARMEH"),
    # munach+paseq NOT before revia: legarmeh only inside a has_legarmeh passage.
    (re.compile(r"74" + _TEXT + r"05"), "_LEGARMEH_OR_MUNACH"),
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
    # any other unrecognized 2-digit accent code -> swallowed (GG [0-9][0-9])
    (re.compile(r"[0-9][0-9]"), None),
    # "**" and "*<non-space>+" -> swallowed
    (re.compile(r"\*\*"), None),
    (re.compile(r"\*[^* \r\n\-]+"), None),
    # catch-all: any other single char -> swallowed
    (re.compile(r".", re.DOTALL), None),
]

# leaf-name (yylval.leaf) for each token type, from tnk2acc.l.
_LEAF: dict[str, str] = {
    "SOFPASUQ": "sof pasuq",
    # Synthetic terminator for a verse missing its sof pasuq (never printed: the
    # grammar production discards it and emits a distinct sof_pasuq_phrase ERROR).
    "MISSING_SOFPASUQ": "",
    "SILLUQ": "silluq",
    "ATNACH": "atnach",
    "SEGOLTA": "segolta",
    "SHALSHELET": "shalshelet",
    "METHIGAZAQEF": "methiga-zaqef",
    "ZAQEF": "zaqef",
    "ZAQEFGADOL": "zaqefgadol",
    "REVIA": "revia",
    "MAYELA": "mayela",
    "TIFCHA": "tifcha",
    "ZARQA": "zarqa",
    "PASHTA": "pashta",
    "YETIV": "yetiv",
    "TEVIR": "tevir",
    "GERESH": "geresh",
    "GERSHAYIM": "gershayim",
    "PAZER": "pazer",
    "PAZERGADOL": "pazergadol",
    "TELISHAGEDOLA": "telishagedola",
    "LEGARMEH": "legarmeh",
    "MUNACH": "munach",
    "MAHPAK": "mahpak",
    "MEREKA": "mereka",
    "MEREKAKEFULA": "merekakefula",
    "DARGA": "darga",
    "AZLA": "azla",
    "TELISHAQETANNA": "telishaqetanna",
    "GALGAL": "galgal",
}


class HasLegarmeh:
    """Port of tnk2acc.l::has_legarmeh (the 17-passage list + 1Sam 14:47 rule).

    Stateful: `count` tracks munach+paseq occurrences at 1Sam 14:47 (only the
    second is legarmeh), and `old_i` advances monotonically through the list
    (the C comment: "this old_i stuff assumes the books are in Jewish order").
    One instance per book file reproduces the C `static` per-process reset.
    """

    _PASSAGES = (
        "Gen 28:9", "Lev 10:6", "Lev 21:10",
        "1Sam 14:3", "1Sam 14:47", "2Sam 13:32",
        "2Kgs 18:17", "Isa 36:2", "Jer 4:19",
        "Jer 38:11", "Jer 40:11", "Ezek 9:2",
        "Hag 2:12", "Ruth 1:2", "Dan 3:2",
        "Neh 8:7", "2Chr 26:15",
    )

    def __init__(self) -> None:
        self._count = 0
        self._old_i = 0

    def __call__(self, location: str) -> bool:
        # Mirrors the C short-circuit `(i != 4) || (++count == 2)`: count is
        # bumped only when we land on 1Sam 14:47 (index 4).
        for i in range(self._old_i, len(self._PASSAGES)):
            if location == self._PASSAGES[i]:
                if i != 4 or self._bump_is_second():
                    self._old_i = i
                    return True
        return False

    def _bump_is_second(self) -> bool:
        self._count += 1
        return self._count == 2


def scan_accents(body: str, location: str, has_legarmeh: HasLegarmeh) -> list[Token]:
    """Scan the GG-state accent codes of one verse body into a token list.

    Emits accent tokens followed by a terminating SOFPASUQ.  Mirrors flex:
    at each position pick the longest match; break ties by rule order.  Stops
    after the first 00 (sof pasuq), which in flex returns to the EE state.

    `location` (the verse reference, e.g. "Ruth 1:2") and `has_legarmeh` resolve
    the 74{TEXT}05-not-before-revia rule to LEGARMEH or MUNACH.
    """
    tokens: list[Token] = []
    pos = 0
    n = len(body)
    saw_sofpasuq = False
    # Insertion index for recovering a *verse-final* silluq when the verse turns
    # out to be missing its sof pasuq (see the post-loop block below).  Set when a
    # meteg/silluq code (35|75|95) is swallowed; reset whenever any later accent is
    # emitted, so only a trailing (verse-final) silluq survives.
    pending_silluq: int | None = None
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
        if best_type == "_LEGARMEH_OR_MUNACH":
            best_type = "LEGARMEH" if has_legarmeh(location) else "MUNACH"
        if best_type is not None:
            tokens.append(Token(best_type, _LEAF[best_type]))
            pending_silluq = None
            if best_type == "SOFPASUQ":
                saw_sofpasuq = True
                break
        elif body[pos : pos + 2] in ("35", "75", "95"):
            # A swallowed meteg/silluq code; remember where its SILLUQ token would
            # go if it proves to be the verse-final silluq of a sof-pasuq-less verse.
            pending_silluq = len(tokens)
        pos += advance

    # Extension beyond tnk2acc.l: tolerate a verse missing its sof pasuq (Unicode
    # SOF PASUQ / code 00).  Such a verse loses *both* end-of-verse markers -- with
    # no 00, the trailing silluq's SILLUQ rule (which requires a following 00) does
    # not fire either, so the stream ends with nothing for the grammar to reduce.
    # Recover the verse-final silluq as a real SILLUQ (so the anomaly is attributed
    # to the sof pasuq, not misread as a missing silluq) and append a distinct
    # MISSING_SOFPASUQ terminator that the grammar flags as a sof_pasuq ERROR.
    if not saw_sofpasuq:
        if pending_silluq is not None:
            tokens.insert(pending_silluq, Token("SILLUQ", _LEAF["SILLUQ"]))
        tokens.append(Token("MISSING_SOFPASUQ", _LEAF["MISSING_SOFPASUQ"]))
    return tokens


@dataclass(frozen=True)
class Verse:
    reference: str
    tokens: list[Token]  # TILDE, accent tokens..., SOFPASUQ


def scan_book(text: str) -> list[Verse]:
    """Scan a whole new-format book file into per-verse token streams.

    Each verse is delimited by TILDE (emitted by the chapter rule at the head of
    every verse line) and SOFPASUQ (the 00 accent code).  A single HasLegarmeh
    instance is held for the whole book, reproducing the C `static` state that
    resets per process (the harness runs one process per book file).
    """
    book = ""
    has_legarmeh = HasLegarmeh()
    verses: list[Verse] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r\n")
        mv = _VERSE_RE.match(line)
        if mv is not None:
            ch, vs, rest = mv.group(1), mv.group(2), mv.group(3)
            reference = f"{book} {ch}:{vs}"
            tokens = [Token("TILDE", "")] + scan_accents(rest, reference, has_legarmeh)
            verses.append(Verse(reference=reference, tokens=tokens))
            continue
        if _BOOKNAME_RE.match(line):
            book = line.strip()
    return verses
