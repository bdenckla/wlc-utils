"""Compare a hand transcription of a printed edition's Decalogue against a vendored strand.

The pages in this family (``printed_decalogue_page`` and its Simanim / Koren satellites) place
real editions among the four IDEALIZED Wikisource strands.  Until now that placement rested on
SIGNAL WORDS -- a handful of accents that identify a strand -- which is enough to settle which
strand an edition follows but says nothing about whether it follows it in every accent.  This
module supports the stronger, accent-by-accent claim, by diffing a hand transcription of the
printed accents against the vendored ``in/accgram/printed_decalogue_teamim.json``.

A transcription is primary observation, read off the printed page (see
``in/accgram/edition_transcriptions/``).  It cannot be derived from anything in the repo, so it
is committed input, not generated output.  What this module adds is that the comparison becomes
mechanical and therefore repeatable: a re-vendoring or an upstream Wikisource revision that
moves an accent fails the test rather than silently invalidating prose on a page.

WHAT COUNTS AS ONE TOKEN (the conventions the transcriptions are written to):

* One token per ACCENT, which is normally one token per chanted word, a maqaf compound being
  one chanted word.  The exception is the compound that bears more than one accent -- its
  atoms each accented, which happens but is rare -- written ``mun-mer``, the dash standing for
  the maqaf itself, and contributing two tokens.  Simanim's Exodus appendix Decalogue has two
  such compounds and they are its most interesting divergences, so this is not hypothetical.
  Contrast ``mun_leg``, where the underscore binds two marks into ONE accent.
* A postpositive or prepositive accent is written TWICE on a word whose stress is not where
  the accent's fixed position puts it -- once at the fixed edge and once on the stressed
  syllable.  That is ONE accent.  ``_accent_tokens`` collapses an immediate repeat of the same
  accent within one word; without this the Exodus elyon alone reports seven phantom
  differences.
* meteg (U+05BD) is dropped: it is not an accent.  Verse-finally the same codepoint is silluq,
  which IS an accent -- emitted, with sof pasuq, as the single token ``silsof``.
* Narrow-sense paseq is not an accent either.  Munax legarmeh is, but the vendored data cannot
  tell the two apart: its own ``resolution_notes`` record that the Wikisource templates
  for legarmeh and for paseq were BOTH folded to U+05C0 at fetch time.  So a munax + U+05C0
  is reported as a PASOLEG position and scored as a plain munax on both sides -- neither
  agreement nor disagreement.  Re-vendoring with the two templates kept distinct would let
  this become a real check; see the issue tracking that.

WHAT A DIFFERENCE MEANS.  Not every difference is a cantillation difference.  Where the two
texts divide words differently -- maqaf vs. space -- the marking usually follows mechanically:
a free-standing word must bear an accent, while a maqaf-joined proclitic normally takes at
most a meteg.  Both confirmed differences in the Exodus elyon are of that kind, and so is one
of the three in the Exodus taxton.  So read a difference list alongside the word it sits on
before calling it an accent difference.

"Normally", though, not "always", and the Exodus taxton is why the weaker word is the right
one.  Simanim prints a munax on the joined לא of לא־יהיה and of לא־תעשה, whose second atoms
carry merkha and qadma -- two accents on one chanted word, where all eight strands have a
meteg.  Those are genuine accent differences, not word-division ones, and an earlier version
of this note asserted they could not occur.  Neither they nor the elyon's pair touch the
disjunctive skeleton or the chanted verse boundaries, which is the claim that has survived
every transcription so far.
"""

from __future__ import annotations

import dataclasses
import difflib
import re
from pathlib import Path

import repo_paths

PASEQ = "\N{HEBREW PUNCTUATION PASEQ}"
SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
MTGOSLQ = "\N{HEBREW POINT METEG}"  # meteg, or silluq when verse-final
MAQAF = "\N{HEBREW PUNCTUATION MAQAF}"

# The three joiners, and the distinctions they draw.  ``-`` is a maqaf, binding two ACCENTS
# into one chanted word: ``mun-mer`` is a compound whose atoms are separately accented, rare
# but real, and it contributes two tokens because the reference side emits one per accent.
# ``_`` binds two MARKS into one accent: ``mun_leg`` is munax legarmeh, conceptually a single
# accent that merely happens to be written with a munax and a pasoleg, and it
# contributes one token.  Tight binding reads as tighter than a maqaf, which is the point.
#
# ``+`` is the SIMPLE-word counterpart of ``-``: two accents on one word that is not a maqaf
# compound at all.  ``qad+ger`` is the case in hand -- qadma and geresh on a single word,
# where the qadma is by convention called *metigah* rather than qadma (the same renaming
# applies in the compound case).  Like a maqaf compound it contributes one token per accent,
# because the reference side emits one per accent either way; unlike one, there is no maqaf,
# and collapsing the two notations would lose exactly the word-division fact that every
# difference here has to be read against.
MAQAF_JOINER = "-"
UNIT_JOINER = "_"
SIMPLE_JOINER = "+"

# The two languages a chunk can be written in, and how each spells the joiners that split it
# into one token per accent.  UNIT_JOINER is in neither, which is what keeps ``mun_leg`` whole.
#
# The .txt writes a maqaf compound with MAQAF_JOINER; the line editor records the literal
# maqaf that was typed.  Otherwise the two agree, and both map onto the .txt's spelling, so
# one splitter serves both -- ``_split_on_joiners`` below is the single place that knows a
# chunk can hold more than one accent.  It used to be three places, and when SIMPLE_JOINER
# was added to two of them the third went on rejecting ``qad+ger`` as an unknown abbreviation.
WRITTEN_ACCENT_JOINERS = {MAQAF_JOINER: MAQAF_JOINER, SIMPLE_JOINER: SIMPLE_JOINER}
EDITOR_ACCENT_JOINERS = {MAQAF: MAQAF_JOINER, SIMPLE_JOINER: SIMPLE_JOINER}

# Accent codepoint -> the shorthand the transcriptions use.
ACCENT_ABBREV = {
    "\N{HEBREW ACCENT ETNAHTA}": "etn",
    "\N{HEBREW ACCENT SEGOL}": "seg",  # segolta
    "\N{HEBREW ACCENT ZAQEF QATAN}": "zaq",
    "\N{HEBREW ACCENT ZAQEF GADOL}": "zaqg",
    "\N{HEBREW ACCENT TIPEHA}": "tip",
    "\N{HEBREW ACCENT REVIA}": "rev",
    "\N{HEBREW ACCENT ZARQA}": "zar",  # U+0598
    "\N{HEBREW ACCENT ZINOR}": "zar",  # U+05AE, the same accent as encoded in this data
    "\N{HEBREW ACCENT PASHTA}": "pash",
    "\N{HEBREW ACCENT YETIV}": "yet",
    "\N{HEBREW ACCENT TEVIR}": "tev",
    "\N{HEBREW ACCENT GERESH}": "ger",
    "\N{HEBREW ACCENT GERESH MUQDAM}": "germ",
    "\N{HEBREW ACCENT GERSHAYIM}": "ger2",
    "\N{HEBREW ACCENT TELISHA GEDOLA}": "tg",
    "\N{HEBREW ACCENT PAZER}": "paz",
    "\N{HEBREW ACCENT MUNAH}": "mun",
    "\N{HEBREW ACCENT MAHAPAKH}": "mah",
    "\N{HEBREW ACCENT MERKHA}": "mer",
    "\N{HEBREW ACCENT MERKHA KEFULA}": "mer2",
    "\N{HEBREW ACCENT DARGA}": "dar",
    "\N{HEBREW ACCENT QADMA}": "qad",
    "\N{HEBREW ACCENT TELISHA QETANA}": "tq",
}

# Spellings a transcriber may reasonably write, normalized onto the shorthand above.
_ALIASES = {
    "pashta": "pash",
    "zaqef": "zaq",
    "zarq": "zar",
    "gershayim": "ger2",
    "munax": "mun",  # transcriptions are plain ASCII, so x for the letter xet
    "munaḥ": "mun",
}

# Legarmeh is set aside for now (see the module docstring): both sides collapse to a plain
# munax so that a PASOLEG position is scored as neither agreement nor disagreement.
_LEGARMEH_TOKENS = ("mun_leg", "mun_PASOLEG")

# What is typed into the line editor (transcription_editor.py), onto the Latin shorthand the
# .txt is written in.  Transcribing from a Hebrew page in Latin means translating every mark
# in your head while also holding your place on the line, so the editor takes Hebrew and the
# mapping happens here instead.
#
# The rule is ANY UNIQUE PREFIX of the accent's Hebrew name: זר is zarqa, פז is pazer, סג is
# segolta, and the full name always works.  So there is no code to memorize, and no need to
# agree a spelling in advance for an accent a page has not yet produced -- which the earlier
# fixed table did require, and which was the reason six accents were deliberately missing
# from it.  A prefix matching more than one name is an error naming the candidates, not a
# guess: adding zaqef gadol later turns a bare זק from unambiguous into rejected, which is
# the safe direction.
#
# Bare זקף is zaqef QATAN by name, not by convention -- the unqualified accent's name simply
# is זקף, so an exact match wins over any longer name that extends it.  The same rule keeps
# מרכא off מרכא כפולה and גרש off גרשיים.
HEBREW_NAMES = {
    "אתנחתא": "etn",
    "סגולתא": "seg",
    "זקף": "zaq",
    "טפחא": "tip",
    "רביע": "rev",
    "זרקא": "zar",
    "פשטא": "pash",
    "יתיב": "yet",
    "תביר": "tev",
    "גרש": "ger",
    "גרשיים": "ger2",
    "תלישא גדולה": "tg",
    "פזר": "paz",
    "מונח": "mun",
    "מהפך": "mah",
    "מרכא": "mer",
    "דרגא": "dar",
    "קדמא": "qad",
    "תלישא קטנה": "tq",
    "סילוק": "silsof",
}

# Spellings the prefix rule cannot reach, and that the Exodus taxton was already transcribed
# in.  תג/תק take a letter from each word of a two-word name, which is not a prefix of it at
# all; גר prefixes גרש and גרשיים alike, so it would be rejected as ambiguous even though
# geresh is the unmarked member of that pair and is what גר has always meant here.
HEBREW_SHORTHAND = {
    "תג": "tg",
    "תק": "tq",
    "גר": "ger",
}

# Written after UNIT_JOINER, binding a second mark into the accent named before it.  Kept
# apart from the accent names so that a bare לג cannot resolve to a token on its own.
HEBREW_MODIFIERS = {
    "לגרמיה": "leg",
}


def _resolve_name(
    written: str, names: dict[str, str], shorthand: dict[str, str]
) -> str:
    """One thing typed into the editor -> its Latin shorthand, by exact name or unique prefix.

    Exact matches -- a name, or an agreed shorthand -- are taken before any prefix search, so
    that a name which merely extends another (גרשיים over גרש, זקף גדול over זקף) cannot make
    the shorter one ambiguous.
    """
    if written in shorthand:
        return shorthand[written]
    if written in names:
        return names[written]
    matches = sorted(name for name in names if name.startswith(written))
    if not matches:
        raise ValueError(f"unknown Hebrew accent abbreviation {written!r}")
    if len(matches) > 1:
        raise ValueError(f"ambiguous Hebrew accent abbreviation {written!r}: {matches}")
    return names[matches[0]]


def hebrew_token(written: str) -> str:
    """One thing typed into the editor -> the Latin shorthand, ``mun_leg`` included."""
    head, joiner, tail = written.partition(UNIT_JOINER)
    accent = _resolve_name(head, HEBREW_NAMES, HEBREW_SHORTHAND)
    if not joiner:
        return accent
    return accent + UNIT_JOINER + _resolve_name(tail, HEBREW_MODIFIERS, {})


def transcriptions_dir() -> Path:
    """Committed hand transcriptions, one file per edition-Decalogue.

    Filenames are ``<edition>_<book>_<reading>``: the same Decalogue exists in more than one
    edition, so the edition has to be in the stem for the stems to stay distinct.
    """
    return repo_paths.in_dir() / "accgram" / "edition_transcriptions"


@dataclasses.dataclass(frozen=True)
class Transcription:
    """One hand-transcribed Decalogue: its header fields and its accent tokens."""

    path: Path
    header: dict[str, str]
    tokens: tuple[str, ...]

    @property
    def key(self) -> tuple[str, str, str]:
        """The ``(book, reading, tradition)`` triple naming the strand to compare against."""
        return (self.header["book"], self.header["reading"], self.header["tradition"])

    @property
    def label(self) -> str:
        edition = self.header.get("edition", "?")
        pages = self.header.get("pages", "?")
        return f"{edition} {'/'.join(self.key)} (pp. {pages})"


@dataclasses.dataclass(frozen=True)
class Difference:
    """One region where transcription and reference disagree.

    ``word`` is the reference word the region starts on -- the thing to look at before
    calling the difference an accent difference rather than a word-division one.
    """

    kind: str  # difflib opcode: "replace", "delete", "insert"
    ref_index: int
    reference: tuple[str, ...]
    transcribed: tuple[str, ...]
    word: str

    def describe(self) -> str:
        ref = " ".join(self.reference) or "(nothing)"
        got = " ".join(self.transcribed) or "(nothing)"
        return f"at token {self.ref_index} ({self.word}): reference {ref} / transcribed {got}"


def _normalize(token: str) -> str:
    token = _ALIASES.get(token, token)
    return "mun" if token in _LEGARMEH_TOKENS else token


def _split_on_joiners(chunk: str, joiners: dict[str, str]) -> list[tuple[str, str]]:
    """Split a chunk into ``(part, the WRITTEN joiner before it)``, in order.

    The first part's joiner is ``""``.  ``joiners`` maps each joiner as the chunk spells it
    onto the way the .txt spells it, so a caller that only wants the parts can drop the second
    element and one that has to rebuild the .txt spelling has it to hand.
    """
    out: list[tuple[str, str]] = []
    part = ""
    joiner = ""
    for ch in chunk:
        if ch in joiners:
            out.append((part, joiner))
            part, joiner = "", joiners[ch]
        else:
            part += ch
    out.append((part, joiner))
    return out


def written_accents(chunk: str) -> list[str]:
    """One chunk as the .txt writes it -> its per-accent parts."""
    return [part for part, _ in _split_on_joiners(chunk, WRITTEN_ACCENT_JOINERS)]


def editor_accents(chunk: str) -> list[tuple[str, str]]:
    """One chunk as the line editor records it -> ``(Hebrew accent, .txt joiner before it)``.

    The one place that knows how an editor chunk holding more than one accent comes apart.
    ``transcription_check`` needs the parts alone, to resolve each with its own printed-line
    origin and to count how many tokens a chunk contributes; ``_hebrew_chunk`` needs the
    joiners too, to write the .txt.  Both take them from here.
    """
    return _split_on_joiners(chunk, EDITOR_ACCENT_JOINERS)


def expand_chunk(chunk: str) -> list[str]:
    """One written chunk -> the token(s) it stands for.

    Almost always one.  A word bearing more than one accent is the exception -- a maqaf
    compound (``mun-mer``) or a simple word (``qad+ger``) -- and it contributes one token per
    accent either way.  Splitting on the ACCENT joiners alone is what makes ``mun_leg`` stay
    whole here.
    """
    return [_normalize(part) for part in written_accents(chunk)]


def rejoin_editor_chunks(items: list[tuple[str, object]]) -> list[tuple[str, object]]:
    """Rejoin maqaf compounds the editor's line breaks split, asides kept in place.

    ``items`` are ``(written, payload)`` pairs in reading order -- the payload is whatever the
    caller needs carried along, a printed-line origin or nothing at all.  The editor records a
    multi-accent maqaf compound with a literal maqaf between its accents; when such a compound
    straddles a printed line break its accents arrive on two different lines, so a chunk left
    ending in a maqaf takes the following chunk with it, and keeps the payload of the piece it
    STARTED on -- that is the line to go back and re-read.

    A bracketed aside carries no accent, so it passes through untouched and never takes part
    in the rejoining: a compound continues across an intervening aside.  This is the ONE
    implementation of the rejoin -- ``hebrew_chunks`` here and ``transcription_check`` both
    call it, after the two drifted apart on exactly the aside case while each had its own.
    """
    out: list[tuple[str, object]] = []
    last_real = -1  # index into ``out`` of the last non-aside chunk
    for written, payload in items:
        if written.startswith("["):
            out.append((written, payload))
        elif last_real >= 0 and out[last_real][0].endswith(MAQAF):
            joined, kept = out[last_real]
            out[last_real] = (joined + written, kept)
        else:
            out.append((written, payload))
            last_real = len(out) - 1
    return out


def hebrew_chunks(lines: list[str]) -> list[str]:
    """Latin shorthand for the Hebrew abbreviations typed into the line editor.

    ``lines`` are the editor's per-line strings, in page order.  Returns one chunk per chanted
    word, written the way the .txt writes it: a multi-accent maqaf compound keeps its dash and
    ``mun_leg`` keeps its underscore.  Normalization -- folding legarmeh onto a plain munax --
    is deliberately NOT done here.  It belongs to the comparison, not to the transcription,
    and doing it here would make the .txt this produces claim less than what was observed.

    ``rejoin_editor_chunks`` undoes the editor's line breaks first; the asides it keeps in
    place are dropped here, exactly as ``load_transcription`` drops them from the .txt.
    ``[פסק]``, marking where a narrow-sense paseq stands, is the one in use: worth recording
    on the page it was read from, but not an accent and so not a token on either side of the
    comparison.
    """
    items = [(chunk, None) for line in lines for chunk in line.split()]
    return [
        _hebrew_chunk(written)
        for written, _ in rejoin_editor_chunks(items)
        if not written.startswith("[")
    ]


def _hebrew_chunk(chunk: str) -> str:
    """One editor chunk -> the way the .txt writes it, both accent joiners preserved.

    The editor records a maqaf compound with a literal maqaf between its accents, and a
    multi-accent simple word with the ``+`` that is typed.  ``editor_accents`` maps each onto
    its own written joiner, so the .txt keeps saying which of the two was seen on the page.
    """
    return "".join(
        joiner + hebrew_token(accent) for accent, joiner in editor_accents(chunk)
    )


def _accent_tokens(verses: list[str]) -> tuple[list[str], list[str], list[str]]:
    """(tokens, words, pasoleg_words) for a vendored strand's chanted verses.

    ``words[k]`` is the chanted word token ``k`` sits on, so a caller can see whether a
    difference is really about the word division rather than about an accent.
    """
    tokens: list[str] = []
    words: list[str] = []
    pasoleg: list[str] = []
    for verse in verses:
        verse_words = verse.split()
        for word in verse_words:
            previous = None
            for i, ch in enumerate(word):
                abbrev = ACCENT_ABBREV.get(ch)
                if abbrev is None:
                    continue
                if abbrev == previous:
                    continue  # doubled postpositive/prepositive: one accent, one token
                previous = abbrev
                if abbrev == "mun" and word[i + 1 :].endswith(PASEQ):
                    pasoleg.append(word)
                tokens.append(abbrev)
                words.append(word)
        if verse.rstrip().endswith(SOF_PASUQ):
            tokens.append("silsof")
            words.append(verse_words[-1] if verse_words else "")
    return tokens, words, pasoleg


def reference_tokens(source: dict, key: tuple[str, str, str]):
    """The reference accent tokens for one ``(book, reading, tradition)`` strand."""
    book, reading, tradition = key
    version = next(
        v
        for v in source["versions"]
        if v["book"] == book and v["reading"] == reading and v["tradition"] == tradition
    )
    return _accent_tokens(version["chanted_verses"])


def load_transcription(path: Path) -> Transcription:
    """Parse a transcription file: ``#`` comments, ``key: value`` header, then tokens."""
    header: dict[str, str] = {}
    tokens: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" in stripped and not stripped.startswith("["):
            field, _, value = stripped.partition(":")
            if " " not in field.strip():
                header[field.strip()] = value.strip()
                continue
        for chunk in re.findall(r"\[[^\]]*\]|\S+", stripped):
            if chunk.startswith("["):
                continue  # a bracketed aside such as "[page break]" carries no accent
            tokens.extend(expand_chunk(chunk))
    missing = {"book", "reading", "tradition"} - set(header)
    if missing:
        raise ValueError(f"{path}: transcription header missing {sorted(missing)}")
    return Transcription(path=path, header=header, tokens=tuple(tokens))


def load_all_transcriptions() -> list[Transcription]:
    """Every committed transcription, sorted by filename."""
    return [load_transcription(p) for p in sorted(transcriptions_dir().glob("*.txt"))]


def compare(source: dict, transcription: Transcription) -> list[Difference]:
    """Every region where ``transcription`` disagrees with its vendored strand."""
    ref, words, _ = reference_tokens(source, transcription.key)
    got = [_normalize(t) for t in transcription.tokens]
    matcher = difflib.SequenceMatcher(a=ref, b=got, autojunk=False)
    out: list[Difference] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        out.append(
            Difference(
                kind=tag,
                ref_index=i1,
                reference=tuple(ref[i1:i2]),
                transcribed=tuple(got[j1:j2]),
                word=words[min(i1, len(words) - 1)] if words else "",
            )
        )
    return out
