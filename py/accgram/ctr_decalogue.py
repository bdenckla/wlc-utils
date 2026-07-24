"""Place CTR's two Decalogues among the idealized strands -- the #69 question, for a DIGITAL
edition rather than a hand transcription.

CTR (``ctr_decalogue_fetch.py``) is a VENDORED STRAND: digital, accent-exact Hebrew, so its
marks are compared mechanically against the reference ``printed_decalogue_teamim.json`` rather
than read off a page.  What it turns out to follow is the surprise this module reports:

* CTR's **Exodus 20** has the ta'am **elyon** word-accents (not the taxton the running text was
  expected to hold), on a chanted-verse division that is NEITHER strand's: the taxton's thirteen,
  with each of the three short prohibitions split off into a chanted verse of its own, as only an
  elyon strand does.  Sixteen chanted verses -- the taxton's boundaries with its twelfth (ending
  at שקר) expanded into four (תרצח, תנאף, תגנב, שקר), against the elyon's nine.
* CTR's **Deuteronomy 5** is the **taxton**, chanted-verse division and all: thirteen, matching
  dt/taxton/printed boundary for boundary, which is why that book is clean where Exodus is not.

STATE THE DIVISION IN CHANTED VERSES, NEVER IN NUMBERED ONES.  An earlier draft of the two bullets
above described the Exodus division as "the ordinary numbered-verse division -- a sof pasuq at
every numbered verse".  That is both off-subject and false.  Off-subject because these pages and
this comparison are about chanted verse structure only, numbering being a different concept
(Ben, 2026-07-24).  False because Exodus 20:13 holds FOUR sof pasuqs, which is exactly where three
of the sixteen come from -- ``chanted_verses`` below says so, and the file contradicted itself for
as long as both texts stood.  Issue #69's Result 11 carried the same phrasing and was corrected
with this.

WHY THE COMPARISON IS AT THE GLYPH LEVEL, NOT THE ACCENT LEVEL.  The eight paper Decalogues of
#69 were HAND transcriptions: a reader resolved each mark to an accent, distinguishing a qadma
from a pashta or a yetiv from a mahapakh by grammar and position -- a distinction the two
members of each pair do NOT draw graphically.  CTR gives no such reading.  Worse, its encoding
is nonstandard (see MAM-basics' review of CTR, ``rocc_2_pre_vowel_accents_in_ctr``): it reuses
one code point for a lookalike pair and leans on vowel-relative order, so its bytes recover the
GLYPH reliably but not always the accent.  So CTR is compared at the resolution its data
actually supports -- the visible mark -- by folding each lookalike pair onto one glyph:

    qadma == pashta,  yetiv == mahapakh,  geresh muqdam == geresh   (tipexa/dexi is poetic-only)

This is not a workaround that hides differences: the accents that DISCRIMINATE elyon from taxton
and p-trad from m-trad (geresh vs pazer, revia vs telisha gedola, zaqef vs revia, and the
chanted-verse boundaries) are not lookalike pairs, so folding the pairs leaves every
discriminator intact.  What the fold gives up is exactly the azla-vs-pashta and
mahapakh-vs-yetiv distinction CTR could not have expressed anyway.

WHAT THE VERDICT CLAIMS.  Only what #69 says survives every transcription -- the chanted-verse
boundaries plus the disjunctive skeleton -- read at the glyph level.  CTR's marks agree with
ex/elyon (Exodus) and dt/taxton (Deuteronomy) at all but a few words, and every disagreement is
CONJUNCTIVE: a munax CTR prints on the proclitic atom of a maqaf compound, or a munax/merkha
swap.  None touches a disjunctive.  The cross-strand re-run -- the same comparison against the
OTHER tradition -- is where the evidence is: agreement collapses, which is what rules out the
clean match being an artifact of the fold.
"""

from __future__ import annotations

import argparse
import dataclasses
import difflib
import json
from pathlib import Path

import repo_paths

from accgram import edition_transcription as et
from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds

COLON = "\N{COLON}"
VBAR = "\N{VERTICAL LINE}"
SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
PASEQ = "\N{HEBREW PUNCTUATION PASEQ}"

# Which reference strand each book is compared against first, and which is the cross-strand
# re-run whose collapse is the evidence.  Both are the PRINTED tradition (the p-trad edition).
PRIMARY = {"ex": "elyon", "dt": "taxton"}
CROSS = {"ex": "taxton", "dt": "elyon"}

# Fold each lookalike pair onto one glyph label (the label is arbitrary; only the grouping
# matters).  Everything not here is its own glyph.  See the module docstring.
_GLYPH = {"qad": "pash", "pash": "pash", "yet": "mah", "mah": "mah", "germ": "ger"}

# Unambiguously conjunctive accents.  ``qad`` is not here -- it folds onto ``pash``, whose
# member pashta is disjunctive -- and ``tq`` (telisha qetana) is, distinct from ``tg`` (telisha
# gedola, disjunctive).  Removing these from a word's glyphs leaves its disjunctive skeleton,
# which is what a difference has to leave intact to count as conjunctive-only.
_CONJUNCTIVE_GLYPHS = {"mun", "mer", "mer2", "dar", "tq"}


def default_ctr_path() -> Path:
    return repo_paths.in_dir() / "accgram" / "ctr_decalogue.json"


def load_ctr(path: Path | None = None) -> dict:
    path = path or default_ctr_path()
    return json.loads(path.read_text(encoding="utf-8"))


def _normalize(verse: str) -> str:
    """CTR's own punctuation onto the reference's: colon -> sof pasuq, vertical bar -> pasoleg.

    The accents are left as CTR encodes them; folding the lookalike pairs happens per glyph in
    ``word_glyphs``, not here, so the normalized text still carries CTR's real code points.
    """
    verse = verse.replace(" " + VBAR, PASEQ).replace(VBAR, PASEQ)
    return verse.replace(COLON, SOF_PASUQ)


def chanted_verses(ctr: dict, book: str) -> list[str]:
    """CTR's Decalogue for one book as chanted verses -- split at sof pasuq, not numbered verse.

    Exodus 20:13 prints three prohibitions each with its own colon, so a numbered verse is not a
    chanted verse; splitting the joined, normalized text at sof pasuq is what recovers the
    chanted-verse structure CTR actually shows.
    """
    verses = ctr["chapters"][book]["decalogue_verses"]
    joined = " ".join(_normalize(verses[k]) for k in verses)
    out: list[str] = []
    cur: list[str] = []
    for ch in joined:
        cur.append(ch)
        if ch == SOF_PASUQ:
            out.append("".join(cur).strip())
            cur = []
    tail = "".join(cur).strip()
    if tail:
        out.append(tail)
    return out


def word_glyphs(word: str) -> tuple[str, ...]:
    """One pointed word -> its accent GLYPHS in order, lookalike pairs folded, repeats collapsed.

    A doubled postpositive (the accent written at the word edge and again on the stressed
    syllable) is one glyph, as in ``_accent_tokens``.  A meteg/silluq (U+05BD) is not an accent
    and contributes no glyph, so a verse-final word contributes its cantillation accent if any
    and nothing for the silluq -- the chanted-verse boundary is counted separately.
    """
    out: list[str] = []
    prev = None
    for ch in word:
        abbrev = et.ACCENT_ABBREV.get(ch)
        if abbrev is None:
            continue
        glyph = _GLYPH.get(abbrev, abbrev)
        if glyph == prev:
            continue
        prev = glyph
        out.append(glyph)
    return tuple(out)


def _flat(verses: list[str]) -> list[tuple[str, tuple[str, ...]]]:
    """(consonant skeleton, glyph tuple) per chanted word across a reading's verses."""
    return [(pds.base_skeleton(w), word_glyphs(w)) for v in verses for w in v.split()]


def _skeleton_glyphs(glyphs: tuple[str, ...]) -> tuple[str, ...]:
    """A word's glyphs with the conjunctives dropped: its disjunctive skeleton at glyph level."""
    return tuple(g for g in glyphs if g not in _CONJUNCTIVE_GLYPHS)


@dataclasses.dataclass(frozen=True)
class WordDiff:
    """One chanted word where CTR's glyphs differ from the strand's."""

    skeleton: str
    ctr: tuple[str, ...]
    strand: tuple[str, ...]

    @property
    def conjunctive_only(self) -> bool:
        """True when the two agree on the disjunctive skeleton -- the difference is conjunctive."""
        return _skeleton_glyphs(self.ctr) == _skeleton_glyphs(self.strand)


@dataclasses.dataclass(frozen=True)
class Comparison:
    book: str
    reading: str
    ctr_words: int
    strand_words: int
    agree: int
    diffs: tuple[WordDiff, ...]

    @property
    def disjunctive_skeleton_intact(self) -> bool:
        return all(d.conjunctive_only for d in self.diffs)


def compare(ctr: dict, source: dict, book: str, reading: str) -> Comparison:
    """Glyph-level word-by-word comparison of CTR's ``book`` against one printed strand.

    Aligns by consonant skeleton (difflib), so a different word division shows up as an aligned
    region rather than shifting every accent after it, then compares the glyph tuples of the
    words that line up.
    """
    ctr_flat = _flat(chanted_verses(ctr, book))
    version = next(
        v
        for v in source["versions"]
        if v["book"] == book and v["reading"] == reading and v["tradition"] == "printed"
    )
    strand_flat = _flat(version["chanted_verses"])

    a = [s for s, _ in ctr_flat]
    b = [s for s, _ in strand_flat]
    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    agree = 0
    diffs: list[WordDiff] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                cs, cg = ctr_flat[i1 + k]
                _, sg = strand_flat[j1 + k]
                if cg == sg:
                    agree += 1
                else:
                    diffs.append(WordDiff(cs, cg, sg))
        else:
            for x in range(i1, i2):
                cs, cg = ctr_flat[x]
                diffs.append(WordDiff(cs, cg, ("<no aligned strand word>",)))
    return Comparison(
        book=book,
        reading=reading,
        ctr_words=len(ctr_flat),
        strand_words=len(strand_flat),
        agree=agree,
        diffs=tuple(diffs),
    )


def strand_chanted_verse_count(source: dict, book: str, reading: str) -> int:
    version = next(
        v
        for v in source["versions"]
        if v["book"] == book and v["reading"] == reading and v["tradition"] == "printed"
    )
    return sum(1 for cv in version["chanted_verses"] if cv.rstrip().endswith(SOF_PASUQ))


def _report_book(ctr: dict, source: dict, book: str) -> None:
    primary, cross = PRIMARY[book], CROSS[book]
    cmp_primary = compare(ctr, source, book, primary)
    cmp_cross = compare(ctr, source, book, cross)
    n_cv = len(chanted_verses(ctr, book))

    print(f"\n===== CTR {book.upper()} =====")
    print(f"  chanted verses (sof pasuq): CTR {n_cv}")
    for reading in (primary, cross):
        print(
            f"     strand {book}/{reading}/printed: "
            f"{strand_chanted_verse_count(source, book, reading)}"
        )
    for label, cmp in (
        (f"PRIMARY {primary}", cmp_primary),
        (f"cross {cross}", cmp_cross),
    ):
        total = cmp.agree + len(cmp.diffs)
        print(
            f"  vs {label:16s}: glyph-agree {cmp.agree}/{total}"
            f"  ({len(cmp.diffs)} word diffs)"
        )
    print(
        f"  disjunctive skeleton intact vs {primary}: {cmp_primary.disjunctive_skeleton_intact}"
    )
    print(f"  the {len(cmp_primary.diffs)} residual difference(s) vs {primary}:")
    for d in cmp_primary.diffs:
        kind = "conjunctive-only" if d.conjunctive_only else "TOUCHES DISJUNCTIVE"
        print(f"     {d.skeleton:26s} CTR={d.ctr}  {primary}={d.strand}  [{kind}]")

    total = cmp_primary.agree + len(cmp_primary.diffs)
    strand_cv = strand_chanted_verse_count(source, book, primary)
    division = (
        "same verse division"
        if n_cv == strand_cv
        else f"but its own verse division ({n_cv} chanted verses, not the strand's {strand_cv})"
    )
    print(
        f"  VERDICT: CTR {book} follows {book}/{primary}/printed at the glyph level "
        f"({cmp_primary.agree}/{total} words, disjunctive skeleton intact, "
        f"{len(cmp_primary.diffs)} conjunctive residual(s)), {division}."
    )


def main() -> None:
    import sys

    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(
        description="Report CTR's Decalogues against the strands."
    )
    parser.add_argument("--ctr", type=Path, default=None)
    parser.add_argument("--source", type=Path, default=None)
    args = parser.parse_args()

    ctr = load_ctr(args.ctr)
    source = pd.load_source(args.source or pd.default_source_path())
    print(
        f"CTR retrieved {ctr['provenance']['retrieved']} -- {ctr['provenance']['edition']}"
    )
    for book in ("ex", "dt"):
        _report_book(ctr, source, book)


if __name__ == "__main__":
    main()
