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

* One token per chanted word.  A maqaf compound is one chanted word, hence one token.
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
texts divide words differently -- maqaf vs. space -- the conjunctive/meteg marking follows
mechanically, because a maqaf-joined proclitic cannot bear an accent while a free-standing
word must.  Both confirmed Simanim/Wikisource differences in the Exodus elyon are of exactly
this kind, and neither touches the disjunctive skeleton or the chanted verse boundaries.  So
read a difference list alongside the word it sits on before calling it an accent difference.
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
_LEGARMEH_TOKENS = ("mun-leg", "mun-PASOLEG")


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
            tokens.append(_normalize(chunk))
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
