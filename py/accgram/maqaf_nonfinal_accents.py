r"""Survey: accents on the NON-FINAL atom of a maqaf compound, across the whole Tanakh.

An accent on a non-final atom of a maqaf compound is the phenomenon behind ``koren_dt_elyon``'s
``mun-mun`` on לא־תעשה and SimTiq's two munax-on-לא (see ``edition_transcription``).  This module
measures it mechanically so the printed-Decalogue pages' claims about how rare it is rest on a
count that can be regenerated, rather than on prose that has to be re-derived every time someone
asks.

Pure computation and a JSON writer -- no HTML.  ``maqaf_nonfinal_accents_page`` renders it, and
runs this to write the JSON, so the page's numbers can never drift from the data.

THE CRITERION is mechanical: within one whitespace-delimited chanted word, is there an accent both
before and after a maqaf?  A maqaf compound has no space in it, so splitting on whitespace really
does give chanted words, and splitting those on maqaf gives their atoms -- the two units this
module counts, and the two the question is about.  A U+05BD counts as an accent only on the
verse's last chanted word, where it is silluq (see CLAUDE.md on meteg-vs-silluq).  Read off the
Unicode verses and NOT off ``uni_to_marks``' mark bodies: ``word_to_marks`` front-loads prepositive
accents to the front of the whole COMPOUND, which would move an atom-2 telisha gedolah onto atom 1
and manufacture hits.
Prose and poetic are routed by ``prose_filter`` / ``poetic_filter`` and counted separately, since
the two systems differ here and a merged count would say nothing about either.

THE TWO ROUTES.  A single bucket of "compounds with two accents" hides the distinction that
matters, so every hit is sorted into one of two routes:

* **(a) A secondary accent the compound inherits.**  Yeivin's own term, and his prose inventory
  is a CLOSED LIST of configurations -- which accent sits on the non-final atom and which the
  compound has: metigah-zaqef (ITM §224), munax-zaqef (§221), a secondary merkha in the chanted word of a
  tipexa (§233) or of a tevir (§§233/241), and the mayela tipexa before an etnaxta or a silluq.
  ``_NAMED_CONFIGURATIONS`` is that list.
* **(b) A maqaf written after an atom that keeps its own conjunctive.**  ITM §293: a manuscript
  habit with no grammatical trigger, "most common where the word has penultimate stress", and L
  -- WLC's own base -- is named for it (§21, §293).

POSITION IS EVIDENCE, NOT THE CRITERION.  Whether a non-final atom's accent sits where that atom's
own accent sits is answered exactly, with no phonology, by an in-corpus oracle: the same spelling
standing FREE elsewhere in the same corpus -- an atom that is a whole chanted word by itself, so
it has its own accent (``build_oracle``).  Key each atom by its letters and points with accents
stripped, and compare base letters after the accent.

* A **no** is decisive.  Nu 9:17 ואחרי־כן has its munax three letters from the end where 21 free
  ואחרי put theirs one from the end, so it cannot be that atom's own accent.
* A **yes is not decisive**, which is the trap.  A secondary accent can land on the atom's own
  stress anyway: MAM's שלף־חרב matches all six free שלף, because nasog axor has retracted the
  stress before חרב, and it is still §233's secondary merkha.  So the CONFIGURATION decides the
  route and the oracle corroborates -- never the other way round.

Two refinements the oracle needs, both of which silently inverted verdicts before they were made:
the free side takes the LAST IMPOSITIVE accent, because a secondary accent always precedes the
main one and taking the first reads a restored secondary as the atom's own position; and
postpositive/prepositive accents are skipped entirely, since their position is a fact about the
chanted word's edge rather than about any atom's stress.

§293's further claim -- that the habit correlates with penultimate stress -- is NOT tested here.
That needs a real stress model; ``../al-hatorah/py/aht_phon/stress.py`` is the prior art.

WHAT THE SURVEY IS A SURVEY OF, which bounds every number it produces.  ``out/wlc422-kq-u`` is the
Westminster transcription of L.  ``in/UXLC-39`` is NOT a second manuscript -- its own header
records that it was produced from WLC 4.20 by WLC2XML -- so it is the same transcription plus
Kimball's corrections, and agreement between the two is not corroboration by a second hand.
MAM-simple is a CONSENSUS text rather than a diplomatic one -- no single manuscript's reading.
It largely follows Breuer, but it is not one of Breuer's own editions (Horev; and the Jerusalem
Crown, which he advised on).  There is therefore no second manuscript here at all: the
counts measure L as Westminster reads it, and what an edition does with it.  ``CORPUS_KIND``
records that so the page cannot state a corpus's standing wrongly.

THE GRAY MAQAF IS THE POETIC HALF OF THE ANSWER, and it is a second measure rather than more of
the first.  The scan above finds a compound by its WRITTEN maqaf, and in poetic verses the maqaf
after a secondary mark is customarily not written -- so the poetic count is a floor by
construction and no tightening of the scan can raise it.  MAM's own answer to that is the gray
maqaf (מקף אפור), its mark for a maqaf the manuscript leaves unwritten where the chanted word
needs one; ``gray_maqaf_survey`` counts it.  The doctrine is Breuer, Chapter 9 §§18-36, set out in
MAM's Wikisource introduction (authored at ``../MAM-basics/py/author_misc/
he_ws_intro_to_mam_gray_maqaf_*.mediawiki``), and the mark is preserved only in MAM-parsed-plus:
MAM-simple drops it, so this one count reads a different corpus from every other count here.
Two kinds are separated, because only one of them answers this page's question: an oleh with its
yored, and a tsinnorit with its partner, are ONE accent written across two atoms.

Run via ``main_accgram.py generate-html-maqaf-nonfinal-accents``.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

from accgram import accent_marks as am
from accgram import poetic_filter, prose_filter, rtms_data
from cmn.wlc_book_codes import wlc_bb_codes
from mb_cmn.hebrew_punctuation import NU_GMAQ
from mb_cmn.str_defs import DOUB_VERT_LINE
from mb_diff_mpu.mpplus_flatten import flatten_ep_for_diff

import repo_paths
import wlc_provenance as provenance

MAQAF = "\N{HEBREW PUNCTUATION MAQAF}"
METEG = "\N{HEBREW POINT METEG}"
PASEQ = "\N{HEBREW PUNCTUATION PASEQ}"
SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
NUN_HAFUKHA = "\N{HEBREW PUNCTUATION NUN HAFUKHA}"

# The pseudo-mark for a verse-final U+05BD.  Not an accent codepoint, so it needs its own token
# in the shape strings and in the configuration table.
SILLUQ = "silluq"

# Marks stripped when keying an atom for the free-standing oracle: two spellings of one atom must
# key alike whether or not one of them has punctuation.
_STRIPPED_FOR_KEY = frozenset((METEG, PASEQ, SOF_PASUQ, NUN_HAFUKHA))

# Accents written at a fixed EDGE of the chanted word rather than on its stress.  Their position
# says nothing about where an atom's own accent falls, so the oracle ignores them.
_NOT_IMPOSITIVE = frozenset(
    (
        am.PASHTA,
        am.TELISHA_QETANA,
        am.SEGOLTA,
        am.TSINNOR,
        am.TSINNORIT,
        am.YETIV,
        am.DEXI,
        am.TELISHA_GEDOLA,
        am.GERESH_MUQDAM,
    )
)

# Route (a): Yeivin's closed prose list, keyed by (accent on the non-final atom, accent the
# compound has).  Membership is a fact about the configuration, not about the mark's position -- see the
# module docstring on why position cannot be the criterion.
_NAMED_CONFIGURATIONS: dict[tuple[str, str], str] = {
    (am.QADMA, am.ZAQEF_QATAN): "metigah-zaqef (ITM §224)",
    (am.MUNAX, am.ZAQEF_QATAN): "munax-zaqef (ITM §221)",
    (am.TIPEXA, am.ATNAX): "mayela before an etnaxta",
    (am.TIPEXA, SILLUQ): "mayela before a silluq",
    (am.MERKHA, am.TIPEXA): "secondary merkha in the tipexa's chanted word (ITM §233)",
    (am.MERKHA, SILLUQ): "secondary merkha in the silluq's chanted word (ITM §233)",
    (
        am.MERKHA,
        am.TEVIR,
    ): "secondary merkha in the tevir's chanted word (ITM §§233, 241)",
    (
        am.MAHAPAKH,
        am.TEVIR,
    ): "secondary mahapakh in the tevir's chanted word (ITM §241)",
}

ROUTE_SECONDARY = "a: a secondary accent the compound inherits"
ROUTE_HABIT = "b: a maqaf after an atom that keeps its own conjunctive (ITM §293)"
ROUTE_UNDECIDED = "?: undecided -- the non-final atom never stands free"
# The poetic corpus is deliberately left unrouted; see ``classify``.
ROUTE_NOT_ATTEMPTED = "(not attempted -- the route split is prose doctrine)"

# Each corpus's standing, which the page must state and must not overstate.
CORPUS_KIND = {
    "wlc422": "diplomatic: the Westminster transcription of the Leningrad Codex",
    "uxlc": "produced from WLC 4.20 by WLC2XML -- the same transcription, corrected",
    "mam_simple": "consensus, not diplomatic; largely follows Breuer, but not an edition of his",
}

_ACCENT_SHORTHAND = {
    am.ATNAX: "etn",
    am.SEGOLTA: "seg",
    am.SHALSHELET: "shal",
    am.ZAQEF_QATAN: "zaq",
    am.ZAQEF_GADOL: "zaqg",
    am.TIPEXA: "tip",
    am.REVIA: "rev",
    am.TSINNORIT: "tsit",
    am.PASHTA: "pash",
    am.YETIV: "yet",
    am.TEVIR: "tev",
    am.GERESH: "ger",
    am.GERESH_MUQDAM: "germ",
    am.GERSHAYIM: "ger2",
    am.QARNEY_PARA: "qar",
    am.TELISHA_GEDOLA: "telg",
    am.PAZER: "paz",
    am.MUNAX: "mun",
    am.MAHAPAKH: "mah",
    am.MERKHA: "mer",
    am.MERKHA_KEFULA: "mer2",
    am.DARGA: "dar",
    am.QADMA: "qad",
    am.TELISHA_QETANA: "telq",
    am.YERAX: "yby",
    am.OLE: "ole",
    am.ILUY: "ilu",
    am.DEXI: "dex",
    am.TSINNOR: "tsor",
    SILLUQ: "sil",
}


# --- low-level predicates -----------------------------------------------------


def is_accent(ch: str) -> bool:
    """An accent (U+0591..U+05AE); U+05BD (meteg/silluq) excluded."""
    return "֑" <= ch <= "֮"


def is_base_letter(ch: str) -> bool:
    return "א" <= ch <= "ת"


# --- reading the three corpora into {bcv: [chanted word, ...]} ----------------


def _join_on_maqaf(atoms: list[str]) -> list[str]:
    """Fold a flat atom list into CHANTED WORDS, an atom ending in a maqaf continuing into
    the next.

    Mirrors ``uni_to_marks.verse_to_marks``' boundary logic, which is what makes a maqaf
    compound one chanted word here as it is there.  Every ``words``-named local and every
    ``[word, ...]`` value in this module is a list of chanted words in this sense; the
    identifiers keep the shorter name, as the #81 sweep left the repo's others.
    """
    words: list[str] = []
    pending = ""
    for atom in atoms:
        pending += atom
        if not pending.endswith(MAQAF):
            words.append(pending)
            pending = ""
    if pending:
        words.append(pending)
    return words


def wlc_words(kq_u_dir: Path) -> dict[str, list[str]]:
    index = rtms_data.load_wlc422_index(kq_u_dir)
    return {
        bcv: _join_on_maqaf(
            [a for vel in (verse.get("vels") or []) for a in _wlc_vel_atoms(vel)]
        )
        for bcv, verse in index.items()
    }


def _wlc_vel_atoms(vel: object) -> list[str]:
    """The pointed atoms of one verse element; the ketiv is dropped, the qere kept.

    A ketiv is unpointed and never accented, so it can only add spurious unaccented atoms;
    the qere is the side that has the marks the scanners read.
    """
    if isinstance(vel, str):
        return [vel]
    if not isinstance(vel, dict):
        return []
    if isinstance(vel.get("sam_pe_inun"), str):
        return []
    kq = vel.get("kq")
    if kq is not None:
        _ketiv, qere = (
            kq if isinstance(kq, (list, tuple)) and len(kq) == 2 else ([], [])
        )
        return [a for sub in qere for a in _wlc_vel_atoms(sub)]
    word = vel.get("word")
    return [word] if isinstance(word, str) else []


def mam_words(refs_by_book: dict[str, set[tuple[int, int]]]) -> dict[str, list[str]]:
    from accgram import mam_simple_verse

    loaded = mam_simple_verse.load_mam_simple_for_refs(
        repo_paths.require_mam_simple_dir(), refs_by_book
    )
    return {
        bcv: _join_on_maqaf(
            [v for v in payload["mam_simple_verse"]["vels"] if isinstance(v, str)]
        )
        for bcv, payload in loaded.items()
    }


# UXLC ships one XML per book under its own English filename; map those onto the WLC 2-char
# book codes the genre filters and the bcv keys use.
_UXLC_FILE_TO_BB = dict(
    zip(
        (
            "Genesis Exodus Leviticus Numbers Deuteronomy Joshua Judges Samuel_1 Samuel_2"
            " Kings_1 Kings_2 Isaiah Jeremiah Ezekiel Hosea Joel Amos Obadiah Jonah Micah"
            " Nahum Habakkuk Zephaniah Haggai Zechariah Malachi Psalms Proverbs Job"
            " Song_of_Songs Ruth Lamentations Ecclesiastes Esther Daniel Ezra Nehemiah"
            " Chronicles_1 Chronicles_2"
        ).split(),
        wlc_bb_codes(),
    )
)


def uxlc_words(uxlc_dir: Path) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for path in sorted(uxlc_dir.glob("*.xml")):
        bb = _UXLC_FILE_TO_BB.get(path.stem)
        if bb is None:
            raise ValueError(f"unmapped UXLC book file: {path.name}")
        for chapter in ET.parse(path).getroot().iter("c"):
            chnu = int(chapter.get("n"))
            for verse in chapter.iter("v"):
                vrnu = int(verse.get("n"))
                atoms = [_uxlc_text(el) for el in verse if el.tag in ("w", "q")]
                out[f"{bb}{chnu}:{vrnu}"] = _join_on_maqaf(atoms)
    return out


def _uxlc_text(el) -> str:
    """The Hebrew of one UXLC ``<w>``/``<q>``, with ``<x>`` note markers dropped.

    An ``<x>`` holds a Latin note letter, not text; left in, it lands mid-word and splits an
    atom that has no business being split.
    """
    parts = [el.text or ""]
    for child in el:
        if child.tag != "x":
            parts.append(_uxlc_text(child))
        parts.append(child.tail or "")
    return "".join(parts)


def split_bcv(bcv: str) -> tuple[str, int, int]:
    bb = bcv[:2]
    chnu, _colon, vrnu = bcv[2:].partition(":")
    return bb, int(chnu), int(vrnu)


# --- the scan -----------------------------------------------------------------


def atom_accents(word: str, verse_final: bool) -> list[list[str]]:
    """Accents per atom of one chanted word, silluq included when it is the verse's last.

    Elsewhere a U+05BD is an ordinary meteg and is dropped: it is not an accent, and counting
    it would turn every non-final atom that has ITM §337's ga'ya into a false hit.
    """
    atoms = word.split(MAQAF)
    per_atom = [[c for c in atom if is_accent(c)] for atom in atoms]
    if verse_final and METEG in atoms[-1]:
        per_atom[-1].append(SILLUQ)
    return per_atom


def shape_of(per_atom: list[list[str]]) -> str:
    """``mun-mun``, ``qad-zaq``, ``0-mer-sil`` -- one field per atom, ``0`` for an unaccented
    one, the dash standing for the maqaf, as in the edition transcriptions' own notation.
    """
    return "-".join(
        "+".join(_ACCENT_SHORTHAND.get(a, a) for a in atom) or "0" for atom in per_atom
    )


def scan(words_by_bcv: dict[str, list[str]], keep) -> tuple[list[dict], int, int]:
    """(hits, verses scanned, maqaf compounds seen) for one corpus and one genre filter."""
    hits: list[dict] = []
    n_verses = n_compounds = 0
    for bcv, words in words_by_bcv.items():
        if not keep(*split_bcv(bcv)):
            continue
        n_verses += 1
        last = len(words) - 1
        for i, word in enumerate(words):
            if MAQAF not in word:
                continue
            n_compounds += 1
            per_atom = atom_accents(word, i == last)
            if not any(per_atom[:-1]):
                continue
            hits.append({"bcv": bcv, "word": word, "atoms": per_atom})
    return hits, n_verses, n_compounds


# --- the free-standing oracle -------------------------------------------------


def oracle_key(atom: str) -> str:
    """The atom's letters and points, accents and punctuation stripped, so a joined and a
    free occurrence of one atom key alike."""
    return "".join(c for c in atom if not is_accent(c) and c not in _STRIPPED_FOR_KEY)


def letters_after_accent(atom: str, *, main_only: bool = False) -> int | None:
    """Base letters strictly after the letter that has the accent; None if there is no accent.

    ``main_only`` takes the last IMPOSITIVE accent, which is the atom's own: a secondary
    accent always precedes the main one, so taking the first would read a restored secondary
    as the atom's own position -- which is exactly what MAM's שלף does.  Without it, take the
    sole accent, which is all a non-final atom ever has.
    """
    letters_before: list[int] = []
    seen = 0
    for ch in atom:
        if is_base_letter(ch):
            seen += 1
        elif is_accent(ch) and not (main_only and ch in _NOT_IMPOSITIVE):
            letters_before.append(seen)
    if not letters_before:
        return None
    return seen - (letters_before[-1] if main_only else letters_before[0])


def build_oracle(words_by_bcv: dict[str, list[str]], keep) -> dict[str, Counter]:
    """key -> Counter of letters-after-accent, over atoms standing FREE -- that is, over
    chanted words of one atom, which therefore have that atom's own accent.

    Verse-final ones are excluded along with the joined: there the U+05BD is a silluq that
    this counter does not see, so such an atom would look unaccented or mis-positioned.
    """
    oracle: dict[str, Counter] = defaultdict(Counter)
    for bcv, words in words_by_bcv.items():
        if not keep(*split_bcv(bcv)):
            continue
        last = len(words) - 1
        for i, word in enumerate(words):
            if MAQAF in word or i == last:
                continue
            n = letters_after_accent(word, main_only=True)
            if n is not None:
                oracle[oracle_key(word)][n] += 1
    return oracle


# --- classification -----------------------------------------------------------


def _accented_nonfinal_atom(hit: dict) -> str:
    return next(
        a for a in hit["word"].split(MAQAF)[:-1] if any(is_accent(c) for c in a)
    )


def _single(accents: list[str]) -> str | None:
    return accents[0] if len(accents) == 1 else None


def classify(hit: dict, oracle: dict[str, Counter], *, routed: bool) -> dict:
    """Route, configuration and oracle evidence for one hit.

    The returned record is what lands in the tracked JSON, so its keys are read by people, not
    only by code: ``word`` is the whole CHANTED WORD (the maqaf compound, joined atoms and all),
    ``shape`` its per-atom accents, and the oracle fields count base letters, not syllables.
    The key keeps the short name, as #81 left the repo's other ``word``-named identifiers.

    ``routed`` is false for the poetic corpus, where the route split is NOT attempted: both
    halves of it are prose doctrine.  ``_NAMED_CONFIGURATIONS`` is Yeivin's PROSE inventory,
    and the poetic counterpart is a different list (his §372 tsinnorit -- ITM spells it with
    an s, this repo with ts; Breuer's Chapter 9 §§23-26 secondary mahapakh/merkha, the span he
    cites for it himself in §27, checkable in ``../breuer-cos/md-export-of-docx/C09-S021.md``),
    which is not encoded here.  Running the prose list
    over poetic verses would label a poetic secondary as unnamed and read it as §293's habit,
    which is why the poetic side reports shapes and counts only.
    """
    per_atom = hit["atoms"]
    atom = _accented_nonfinal_atom(hit)
    joined = letters_after_accent(atom)
    free = oracle.get(oracle_key(atom))
    free_usual = free.most_common(1)[0][0] if free else None
    evidence = {
        "joined_letters_after_accent": joined,
        "free_letters_after_accent": free_usual,
        "free_occurrences": sum(free.values()) if free else 0,
    }

    if not routed:
        route, named = ROUTE_NOT_ATTEMPTED, None
    else:
        nonfinal_accent = _single([a for atom_ in per_atom[:-1] for a in atom_])
        compound_accent = _single(per_atom[-1])
        named = _NAMED_CONFIGURATIONS.get((nonfinal_accent, compound_accent))
        if named is not None:
            route = ROUTE_SECONDARY
        elif free_usual is None:
            route = ROUTE_UNDECIDED
        elif joined != free_usual:
            route, named = (
                ROUTE_SECONDARY,
                "unnamed -- not at the atom's own accent position",
            )
        else:
            route, named = ROUTE_HABIT, "unnamed"

    return {
        "bcv": hit["bcv"],
        "word": hit["word"],
        "shape": shape_of(per_atom),
        "route": route,
        "configuration": named,
        "oracle": evidence,
    }


# --- MAM's gray maqaf ---------------------------------------------------------

# MAM-parsed-plus' three poetic books, keyed by the book code ``bcv`` uses.  There is no prose
# file to read: the gray maqaf occurs in poetic verses only, which the survey checks rather than
# assumes -- ``gray_maqaf_survey`` raises if a prose-cantillated verse of Job carries one.
_GRAY_MAQAF_BOOKS = (
    ("ps", "D1-Psalms.json"),
    ("pr", "D2-Proverbs.json"),
    ("jb", "D3-Job.json"),
)

# An oleh with its yored, and a tsinnorit with its partner mahapakh or merkha, are ONE accent
# written across two atoms rather than two accents on one chanted word.  A gray maqaf joining such
# a pair says nothing about the question this page asks, so the two kinds are counted apart and
# the prose quotes the kind that answers it.
_ONE_ACCENT_ACROSS_TWO_ATOMS = frozenset((am.OLE, am.TSINNORIT))

GRAY_KIND_SPREAD = "one accent written across the two atoms (an oleh-we-yored, or a tsinnorit and its partner)"
GRAY_KIND_SECOND = "a second accent on the joined atom"

# Where a chanted word ends in the flattened MAM-parsed-plus text.  A space is the ordinary
# boundary; ``flatten_ep_for_diff`` renders מ:פסק as ``DOUB_VERT_LINE`` and legarmeh as a PASEQ
# with no space around either, so a whitespace split alone would run Ps 5:5's רשע and אתה
# together into one chanted word and manufacture an accent for the atom after a gray maqaf.
_CHANTED_WORD_END = frozenset((" ", PASEQ, DOUB_VERT_LINE, SOF_PASUQ))


def _around_gray_maqaf(text: str, idx: int) -> tuple[str, str, bool]:
    """The atom a gray maqaf joins, the rest of the chanted word, and whether that is verse-final.

    ``idx`` indexes the ``NU_GMAQ`` sentinel in a flattened verse.  The far side is the REST of
    the chanted word rather than one atom, because the atom immediately after a gray maqaf need
    not be the one with the accent: Ps 5:5 לא~אל־חפץ joins לא to a compound whose accent is on
    its second atom, so an atom-to-atom reading would report the compound's own accent missing.
    Verse-finality comes back because a verse-final U+05BD is the silluq, and Ps 18:20's בי has
    nothing else -- the same rule ``atom_accents`` applies, and applied by it below.
    """
    before = text[:idx].replace(NU_GMAQ, " ")
    end = idx + 1
    while end < len(text) and text[end] not in _CHANTED_WORD_END:
        end += 1
    verse_final = end < len(text) and text[end] == SOF_PASUQ
    return before.split()[-1].split(MAQAF)[-1], text[idx + 1 : end], verse_final


def _gray_maqaf_hits(plus_dir: Path) -> list[dict]:
    """Every מ:מקף אפור in MAM-parsed-plus, with the atoms it joins and their accents."""
    hits: list[dict] = []
    for bb, filename in _GRAY_MAQAF_BOOKS:
        with (plus_dir / filename).open(encoding="utf-8") as f_in:
            chapters = json.load(f_in)["book39s"][0]["chapters"]
        for chnu, chapter in chapters.items():
            for vrnu, verse in chapter.items():
                text = flatten_ep_for_diff(verse[2])
                idx = text.find(NU_GMAQ)
                while idx >= 0:
                    joined, rest, verse_final = _around_gray_maqaf(text, idx)
                    word = joined + MAQAF + rest.replace(NU_GMAQ, MAQAF)
                    per_atom = atom_accents(word, verse_final)
                    kind = (
                        GRAY_KIND_SPREAD
                        if set(per_atom[0]) & _ONE_ACCENT_ACROSS_TWO_ATOMS
                        else GRAY_KIND_SECOND
                    )
                    hits.append(
                        {
                            "bcv": f"{bb}{int(chnu)}:{int(vrnu)}",
                            "joined_atom": joined,
                            "rest_of_chanted_word": rest,
                            "shape": shape_of(per_atom),
                            "kind": kind,
                        }
                    )
                    idx = text.find(NU_GMAQ, idx + 1)
    return hits


def gray_maqaf_survey() -> dict:
    """MAM's gray maqafs: the compounds its poetic verses join without a written maqaf.

    Not a fourth corpus beside the three above -- a second MEASURE, of the part of the poetic
    phenomenon the maqaf scan cannot reach.  See the module docstring on why it has to be, and
    on why it alone reads MAM-parsed-plus.
    """
    hits = _gray_maqaf_hits(repo_paths.require_mam_parsed_plus_dir())
    # The claims the prose rests on, pinned where the data is rather than in the page: that the
    # mark is confined to poetic verses, so it can be described as belonging to that system; that
    # the joined atom always has exactly one accent, which is what makes it worth a gray maqaf at
    # all; and that another accent always falls later in the same chanted word, without which
    # "two marks in one chanted word" -- the whole reason the count is worth quoting -- would be
    # false of some of them.  The atom right after the gray maqaf is NOT pinned: Ps 5:5 is a real
    # case where it has no accent and the compound's accent is one atom further on.
    for hit in hits:
        bb, chnu, vrnu = split_bcv(hit["bcv"])
        assert poetic_filter.should_keep_line(bb, chnu, vrnu), hit
        fields = hit["shape"].split("-")
        assert fields[0] != "0" and "+" not in fields[0], hit
        assert any(field != "0" for field in fields[1:]), hit
    return {
        "what": (
            "MAM's מקף אפור: a maqaf the manuscript leaves unwritten where the chanted word"
            " needs one. The doctrine is Breuer, Chapter 9 §§18-36, set out in MAM's Wikisource"
            " introduction; the two atoms are one chanted word, and the joined one is often"
            " pointed as though the maqaf were there."
        ),
        "source": (
            "MAM-parsed-plus (the מ:מקף אפור template), NOT the MAM-simple this survey's"
            " corpora read: MAM-simple drops the mark."
        ),
        "total": len(hits),
        "by_book": dict(Counter(h["bcv"][:2] for h in hits).most_common()),
        "by_kind": dict(Counter(h["kind"] for h in hits).most_common()),
        "by_shape": dict(Counter(h["shape"] for h in hits).most_common()),
        "occurrences": sorted(hits, key=lambda h: (h["kind"], h["shape"], h["bcv"])),
    }


# --- the survey ---------------------------------------------------------------


def _genre_survey(words_by_bcv, keep, oracle, *, routed: bool) -> dict:
    hits, n_verses, n_compounds = scan(words_by_bcv, keep)
    classified = [classify(h, oracle, routed=routed) for h in hits]
    return {
        "verses": n_verses,
        "maqaf_compounds": n_compounds,
        "hits": len(classified),
        "by_route": dict(Counter(c["route"] for c in classified).most_common()),
        "by_configuration": dict(
            Counter(c["configuration"] for c in classified).most_common()
        ),
        "by_shape": dict(Counter(c["shape"] for c in classified).most_common()),
        "occurrences": sorted(
            classified, key=lambda c: (c["route"], c["shape"], c["bcv"])
        ),
    }


def build_survey() -> dict:
    """The whole survey: three corpora x two genres, every hit classified."""
    wlc = wlc_words(repo_paths.out_dir() / "wlc422-kq-u")
    refs: dict[str, set[tuple[int, int]]] = defaultdict(set)
    for bcv in wlc:
        bb, chnu, vrnu = split_bcv(bcv)
        refs[bb].add((chnu, vrnu))

    corpora = {
        "wlc422": wlc,
        "uxlc": uxlc_words(repo_paths.in_dir() / "UXLC-39"),
        "mam_simple": mam_words(dict(refs)),
    }
    genres = (("prose", prose_filter, True), ("poetic", poetic_filter, False))

    survey: dict[str, object] = {
        "criterion": (
            "Within one whitespace-delimited chanted word, an accent both before and after a"
            " maqaf -- that is, on an atom the maqaf joins to the next as well as on the atom"
            " that has the compound's own accent. A U+05BD counts as an accent only on the"
            " verse's last chanted word, where it is silluq."
        ),
        "poetic_caveat": (
            "The poetic counts under ``corpora`` are a FLOOR and are not comparable with the"
            " prose ones. Breuer (Chapter 9 §§27, 37) records that in the Three Books the maqaf"
            " after a secondary mahapakh, merkha or tsinnorit is customarily omitted in writing"
            " while the atom still counts as joined -- so most of the poetic phenomenon is"
            " invisible to a maqaf scan by construction. His own 'few cases where the hyphen is"
            " not omitted' bear this out from the other side: Job 6:10 and Prov 25:20 are"
            " written WITHOUT a maqaf in WLC and UXLC, and with one only in MAM. ``gray_maqaf``"
            " is the measure of what the scan misses; take the two together, and neither alone."
            " The routes are not attempted here either; see ``classify``."
        ),
        "gray_maqaf": gray_maqaf_survey(),
        "corpora": {},
    }
    for name, words_by_bcv in corpora.items():
        per_genre = {}
        for genre, module, routed in genres:
            keep = module.should_keep_line
            oracle = build_oracle(words_by_bcv, keep)
            per_genre[genre] = _genre_survey(words_by_bcv, keep, oracle, routed=routed)
        survey["corpora"][name] = {"kind": CORPUS_KIND[name], **per_genre}
    return survey


def default_json_out_path() -> Path:
    return repo_paths.out_dir() / "accgram" / "maqaf-nonfinal-accents.json"


def write_json(survey: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = provenance.with_json_provenance(survey, __file__)
    # ``newline="\n"`` as dual_cant_run does: the repo's line-ending policy is LF in the
    # workdir as well as in git (.gitattributes, issue #50), and Python would otherwise
    # translate to CRLF on Windows and leave every regeneration looking like a whole-file diff.
    with path.open("w", encoding="utf-8", newline="\n") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=1)
        f_out.write("\n")
