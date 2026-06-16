r"""Hand-written scanner for the POETIC (Three Books) accent system.

The poetic counterpart of accgram.ply_scanner.  Where the prose scanner ports
tnk2acc.l's GG-state table verbatim, there is no poetic flex source, so the rule
table here is built from the Michigan-Claremont accent codes and their *poetic*
(Tabula Accentuum column II) readings, as listed in
``wlc-utils-io/in/wlc420/supplmt.wts``, cross-checked against decoded L verses.

M-C code -> poetic accent (the codes that matter in the Three Books):

  disjunctives
    00            sof pasuq
    75|35|95 /00  silluq (a meteg/silluq immediately before sof pasuq)   II.1
    92            atnah                                                   II.3
    60 (+ yored)  oleh-we-yored: ole sign (above, pre-stress) plus the    II.2
                  yored = merka (71) below the stress; the 71 is consumed
                  into the one OLEH_WEYORED token, not emitted as a servus
    11 (+ 81)     revia mugrash: geresh muqdam (preposed) plus revia; if  II.5
                  the revia dot is omitted because it would fall on the
                  same letter as the geresh muqdam, it is implied
    81            revia (gadol or qatan -- same sign; disambiguated in a   II.4=8
                  second pass: a revia whose next disjunctive is
                  oleh-we-yored is qatan, otherwise gadol)
    13            dehi                                                     II.9
    02            sinnor (no zarqa exists in the poetic system)           II.7
    83            pazer                                                    II.10
    65 + 05       shalshelet gedolah (shalshelet sign + paseq)            II.6
    63|70 + 05    legarmeh: azla legarmeh (63) / mehuppak legarmeh (70),  II.12
                  i.e. a conjunctive followed by paseq, as prose 74+05

  conjunctive servi
    74 munah   71 merka   70 mehuppak   63 azla   64 illuy   73 tarha
    93 galgal (yerah; also the servus of oleh-we-yored and of pazer)

  swallowed (secondary / ga`ya / separators, not structural accents)
    82 sinnorit   65 (without following paseq) shalshelet qetannah
    35|75|95 (not before sof pasuq) meteg   05 (plain) paseq   52|53 puncta

Known gaps (deferred to the validation pass, see the module's tests / notes):
  - "revia mugrash without geresh" (#367): a bare 81 acting as the main verse
    divider when the verse has no atnah is currently scanned as revia (gadol);
    distinguishing it needs verse-level context.
  - oleh-we-yored whose ole is unmarked (only the yored merka is written, when a
    revia precedes -- #363) is not recovered; its yored merka is read as a servus.
  - shalshelet qetannah (the conjunctive, 8 verses) is swallowed, not emitted.

The scanner returns a list of (token_type, leaf_name) pairs ready for
accgram.ply_grammar_poetic.parse_tokens; the verse begins with ('TILDE','') and
ends with ('SOFPASUQ', 'sof pasuq').
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from cmn.wlc_book_codes import wlc_bb_to_bk39id

_TEXT = r"[^ \r\n\-]*"  # within one maqqef/space-delimited word (as in prose)

# Verse-structure line patterns, as in accgram.ply_scanner.scan_book: a verse line
# is "ch:vr <accent codes>"; a lone capitalized word is a chapter/book header we
# skip (the poetic reference is built from the WLC book code, not the header).
_BOOKNAME_RE = re.compile(r"^([1234][ \t]*)?[A-Z][a-z]+[ \t]*$")
_VERSE_RE = re.compile(r"^([1-9][0-9]*):([1-9][0-9]*)[ \t](.*)$")

# Disjunctive token types, for the revia gadol/qatan second-pass lookahead.
_POETIC_DISJUNCTIVES = frozenset(
    {
        "SILLUQ",
        "ATNACH",
        "OLEH_WEYORED",
        "REVIA",
        "REVIA_MUGRASH",
        "REVIA_GADOL",
        "REVIA_QATAN",
        "DEHI",
        "SINNOR",
        "PAZER",
        "LEGARMEH",
        "SHALSHELET_GEDOLAH",
    }
)

# Rule table: (regex anchored at scan position, token type or None to swallow).
# Longest match wins; ties broken by order (mirrors flex / the prose scanner).
_POETIC_GG_RULES: list[tuple[re.Pattern[str], str | None]] = [
    (re.compile(r"00"), "SOFPASUQ"),
    # silluq: meteg/silluq sign (35|75|95) immediately before sof pasuq.
    (re.compile(r"(?:35|75|95)(?=[^ 379\r\n\-?~]*00)"), "SILLUQ"),
    (re.compile(r"92"), "ATNACH"),
    # oleh-we-yored: ole (60) plus its yored merka (71) in the same word; the 71
    # is consumed here so it is not also emitted as a servus.  Bare 60 (yored on
    # the next word, or unmarked) still yields the accent.
    (re.compile(r"60" + _TEXT + r"71"), "OLEH_WEYORED"),
    (re.compile(r"60"), "OLEH_WEYORED"),
    # revia mugrash: geresh muqdam (11) plus revia (81) in the same word; the 81
    # is consumed.  Bare 11 = implied revia (omitted because it would share the
    # geresh muqdam's letter).
    (re.compile(r"11" + _TEXT + r"81"), "REVIA_MUGRASH"),
    (re.compile(r"11"), "REVIA_MUGRASH"),
    (re.compile(r"13"), "DEHI"),
    (re.compile(r"02"), "SINNOR"),
    (re.compile(r"83"), "PAZER"),
    # shalshelet gedolah = shalshelet (65) followed by paseq (05).
    (re.compile(r"65" + _TEXT + r"05"), "SHALSHELET_GEDOLAH"),
    # legarmeh = azla (63) or mehuppak (70) followed by paseq (05).  Must precede
    # the bare AZLA / MAHPAK rules so the longer paseq-terminated match wins.
    (re.compile(r"(?:63|70)" + _TEXT + r"05"), "LEGARMEH"),
    # revia (gadol/qatan) -- reclassified in the second pass.
    (re.compile(r"81"), "REVIA"),
    # conjunctive servi
    (re.compile(r"74"), "MUNACH"),
    (re.compile(r"71"), "MEREKA"),
    (re.compile(r"70"), "MAHPAK"),
    (re.compile(r"63"), "AZLA"),
    (re.compile(r"64"), "ILLUY"),
    (re.compile(r"73"), "TARHA"),
    (re.compile(r"93"), "GALGAL"),
    # swallowed: sinnorit, bare shalshelet (qetannah conjunctive), meteg, paseq,
    # puncta, and any other 2-digit code (prose accents should not occur here).
    (re.compile(r"82|65|35|75|95|05|52|53"), None),
    (re.compile(r"[0-9][0-9]"), None),
    (re.compile(r"\*\*"), None),
    (re.compile(r"\*[^* \r\n\-]+"), None),
    (re.compile(r".", re.DOTALL), None),
]

_LEAF: dict[str, str] = {
    "SOFPASUQ": "sof pasuq",
    "SILLUQ": "silluq",
    "ATNACH": "atnah",
    "OLEH_WEYORED": "oleh we-yored",
    "REVIA_MUGRASH": "revia mugrash",
    "REVIA_GADOL": "revia gadol",
    "REVIA_QATAN": "revia qatan",
    "DEHI": "dehi",
    "SINNOR": "sinnor",
    "PAZER": "pazer",
    "LEGARMEH": "legarmeh",
    "SHALSHELET_GEDOLAH": "shalshelet gedolah",
    "MUNACH": "munah",
    "MEREKA": "merka",
    "MAHPAK": "mehuppak",
    "AZLA": "azla",
    "ILLUY": "illuy",
    "TARHA": "tarha",
    "GALGAL": "galgal",
}


def _reclassify_revia(types: list[str]) -> list[str]:
    """Resolve each generic REVIA (M-C 81, no geresh muqdam) to its role.

    The three revias share signs: revia mugrash carries a geresh muqdam (code 11,
    handled in the rule table); revia gadol and revia qatan are a bare dot, and a
    *bare* revia before silluq is revia mugrash "without the geresh" (Yeivin
    #367).  Disambiguation is by the next disjunctive in the stream:

      - next is OLEH_WEYORED  -> revia qatan (it stands only there, #368);
      - next is SILLUQ        -> revia mugrash without geresh (the last
        disjunctive before silluq; when two revias precede silluq the first is
        gadol and the second mugrash, #391 -- handled automatically since the
        first revia's next disjunctive is the second revia, not silluq);
      - otherwise (next is atnah, oleh, or another revia) -> revia gadol.
    """
    out = list(types)
    for i, t in enumerate(out):
        if t != "REVIA":
            continue
        nxt = next(
            (out[j] for j in range(i + 1, len(out)) if out[j] in _POETIC_DISJUNCTIVES),
            None,
        )
        if nxt == "OLEH_WEYORED":
            out[i] = "REVIA_QATAN"
        elif nxt == "SILLUQ":
            out[i] = "REVIA_MUGRASH"
        else:
            out[i] = "REVIA_GADOL"
    return out


def scan_accents(body: str) -> list[tuple[str, str]]:
    """Scan one poetic verse body (the M-C accent text after ``ch:vr ``).

    Returns (token_type, leaf) pairs, accent tokens followed by SOFPASUQ.  Stops
    after the first 00.  REVIA tokens are reclassified to gadol/qatan afterward.
    """
    raw_types: list[str] = []
    pos = 0
    n = len(body)
    while pos < n:
        best_len = 0
        best_type: str | None = None
        matched = False
        for regex, ttype in _POETIC_GG_RULES:
            m = regex.match(body, pos)
            if m is None:
                continue
            length = m.end() - m.start()
            if length > best_len:
                best_len = length
                best_type = ttype
                matched = True
        assert matched, f"no rule matched at position {pos} in {body!r}"
        if best_type is not None:
            raw_types.append(best_type)
            if best_type == "SOFPASUQ":
                break
        pos += max(best_len, 1)

    resolved = _reclassify_revia(raw_types)
    return [(t, _LEAF[t]) for t in resolved]


@dataclass(frozen=True)
class Verse:
    reference: str
    tokens: list[tuple[str, str]]  # ('TILDE',''), accents..., ('SOFPASUQ',...)
    body: str


def scan_verse(reference: str, body: str) -> Verse:
    """Scan one verse body into a grammar-ready token stream."""
    tokens: list[tuple[str, str]] = [("TILDE", "")]
    tokens += scan_accents(body)
    return Verse(reference=reference, tokens=tokens, body=body)


def scan_book(text: str, bb: str) -> list[Verse]:
    """Scan a whole split_wlc book text into per-verse poetic token streams.

    Mirrors accgram.ply_scanner.scan_book's line walk -- header lines are skipped,
    each ``ch:vr <accents>`` line becomes one Verse via scan_verse -- but the
    reference uses the clean book name (the WLC code's bk39id: "Psalms",
    "Proverbs", "Job") rather than the goerwitz header word, since the poetic
    output has no C oracle to match and the header carries a binary-dodging
    placeholder for Job ("Defeatmatchforjob").
    """
    book = wlc_bb_to_bk39id(bb)
    verses: list[Verse] = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\r\n")
        mv = _VERSE_RE.match(line)
        if mv is not None:
            ch, vs, rest = mv.group(1), mv.group(2), mv.group(3)
            verses.append(scan_verse(f"{book} {ch}:{vs}", rest))
            continue
        # Non-verse lines are book/chapter headers (or blank); ignore them.
        if not line.strip() or _BOOKNAME_RE.match(line):
            continue
    return verses
