r"""Generate gh-pages/accgram/maqaf-nonfinal-accents.html, and the JSON behind it.

The rendered account of ``maqaf_nonfinal_accents``' survey, narrowed to one question: how often a
non-final atom of a compound has an accent of its own in MAM, and what that means for
``koren_dt_elyon``'s ``mun-mun`` on לא־תעשה.  Every number on the page is spliced from the survey
this run computes, and the same run writes ``out/accgram/maqaf-nonfinal-accents.json``, so page
and data cannot drift.

The survey is wider than the page: three corpora, both genres, and a route (a)/(b) split telling
an inherited secondary accent from a maqaf written after an atom that keeps its own conjunctive.
The page rendered all of that until 2026-07-27 and now renders MAM's prose alone -- see issue #83
for what was cut and why, and #82 for the Yeivin citations that must be settled before the
route-(b) material is rendered anywhere again.

Rendered-prose conventions are ``printed_decalogue_strands``' module docstring; the romanizations
come from its ``ROM_*`` constants and are never retyped here.

Run via ``main_accgram.py generate-html-maqaf-nonfinal-accents``.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from accgram import accent_marks as am
from accgram import maqaf_nonfinal_accents as mpa
from accgram import printed_decalogue as pd
from accgram import rtms_report
from accgram.almost_errors_html_shared import (
    accents_and_letters,
    hbo,
    link,
    wrap_hebrew_runs,
)
from accgram.printed_decalogue_strands import (
    ELYON,
    ROM_DARGA,
    ROM_ETNAHTA,
    ROM_GERESH,
    ROM_GERSHAYIM,
    ROM_MAHAPAKH,
    ROM_MERKHA,
    ROM_METEG,
    ROM_MUNAX,
    ROM_PASHTA,
    ROM_PAZER,
    ROM_QADMA,
    ROM_REVIA,
    ROM_SILLUQ,
    ROM_TELISHA_GEDOLAH,
    ROM_TEVIR,
    ROM_TIPEHA,
    ROM_ZAQEF_QATAN,
    TAHTON,
)
from accgram.uni_to_marks import is_base_letter
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import wlc_utils_html as H

import repo_paths

# "Non-final atom of a compound", not "proclitic" and not "maqaf-joined atom".  "Proclitic"  # prose-ok: names the rejected term
# asserted a grammatical role the scan never checks -- route (b) is precisely an atom that keeps
# its own conjunctive, so it is proclitic by position only.  And a lone atom is never "maqaf-joined"  # prose-ok: names the rejected term
# full stop: it is joined TO the next one, or else the two of them are joined to each other.
# Naming the atom by its POSITION in the compound says what the scan measures and nothing more,
# and it matches the module basenames.  A title is short on space and there is no other kind of
# compound here, so "maqaf" is dropped from "maqaf compound" in this one place; the body says it
# in full.  (#81's sweep settled "atom" as a reader-facing term, which is what lets it stand bare.)
PAGE_TITLE = "Accents on a Non-Final Atom of a Compound"
_WIDTH_CLASS = "goerwitz-tms-width-limited"

# The one text this page counts.  It used to count three, WLC and UXLC beside MAM, and carry a
# section warning that those two were not two independent readings -- UXLC being WLC 4.20 with
# Kimball's corrections, so a column agreeing with its neighbor was one hand agreeing with itself.
# Ben, 2026-07-27: "Ditch WLC and UXLC; I don't think I ever asked for that scope.  MAM='The
# Tanakh', for the purposes of this document."  A claim about what the accentuation DOES wants a
# consensus text anyway, which is what the caveat section had been working around rather than
# acting on.  The survey behind the page still computes all three, so the tracked JSON is
# unchanged and the other two remain a query away.
_CORPUS = "mam_simple"


# Accent names for the shorthand the survey's shapes are written in -- ``qad-zaq``, ``mer-sil``.
# The shapes are code identifiers and spell ח with an x, as the transliteration standard requires
# of code and of the tracked JSON alike; rendered prose takes the ROM_* romanizations instead.
# ``_pair_of`` raises on a shorthand not here, so a corpus bump that produces a new pair fails
# the build rather than printing a code identifier at a reader.
_ACCENT_DISPLAY = {
    "qad": ROM_QADMA,
    "zaq": ROM_ZAQEF_QATAN,
    "tip": ROM_TIPEHA,
    "etn": ROM_ETNAHTA,
    "mer": ROM_MERKHA,
    "sil": ROM_SILLUQ,
    "mah": ROM_MAHAPAKH,
    "pash": ROM_PASHTA,
    "mun": ROM_MUNAX,
    "tev": ROM_TEVIR,
    # Reached only by the simple side, which since 2026-07-28 covers every pair that occurs on
    # a chanted word of MAM's prose verses rather than only the eight the compound side has.
    "ger": ROM_GERESH,
    "dar": ROM_DARGA,
    "rev": ROM_REVIA,
    "paz": ROM_PAZER,
}

# GONE with the classification (Ben, 2026-07-28): _CONFIG_DISPLAY, which rendered Yeivin's
# category names, and the two labels for the rows that held the cases the categories could not
# name or could not reach.  The unnamed one read "no named configuration: the mark is simply not
# at that atom's own accent position" -- "too long for a cell, and anyway I have no idea what
# [it means], and it features your favorite, usually meaningless word: own".  Both faults are
# moot now: with the rows gone there is no cell, and a table of observed pairs has nothing to
# say about where an accent would otherwise have fallen.
#
# The naming rules those labels carried are worth keeping even though the labels are not:
#   * "the mayela", never "the mayela tipexa" -- mayela IS the name for what would otherwise be
#     a tipexa there, so the pair reads as a kind of tipexa.  Mayela is to tipexa as metigah is
#     to qadma, and nobody writes "metigah qadma".
#   * No "secondary" in a rendered label: unexplained, the page never saying what a secondary
#     accent is, and arguably unwarranted, Yeivin calling every mark on his list secondary where
#     Breuer (CoS ch. 9 §§21-23) reserves the word for pairs that cannot stand in that order
#     across two separate words.  Naming the two marks asserts neither view, which is the point.

# Where an accent has a name of its own in the position the pair puts it in, the row uses that
# name.  A tipexa in the chanted word of an etnaxta or of a silluq is the MAYELA; a qadma in the
# chanted word of a zaqef qatan is the METIGAH.  Ben's own analogy -- mayela is to tipexa as
# metigah is to qadma -- and he asked the same question of both rows in turn: "what happened to
# the terminology of mayela?", then the same of metigah.  The intro still glosses metigah-zaqef
# as a qadma before a zaqef qatan, which is what tells a reader which mark the row means.
_PAIR_FIRST_NAME = {
    ("tip", "etn"): "mayela",
    ("tip", "sil"): "mayela",
    ("qad", "zaq"): "metigah",
}

# A cell holding a number is right-justified, so the digits line up on the units column.  The
# rule is in gh-pages/style.css; the class goes on the count column's header too, or the heading
# sits over nothing.
_NUMERIC_CELL = {"class": "numeric"}

_SMALL_NUMBERS = (
    "no",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
)


# Route (b) is the RESIDUE left when no named configuration fits, so nothing in the classifier
# guarantees its mark is the conjunctive the route is named for.  The page used to disclose that
# in the bullet, with a ``_HABIT_MARKS`` tuple and a ``pin_claims`` assertion keeping the
# disclosure honest -- but every counterexample was WLC's or UXLC's (WLC's Jeremiah 48:12, UXLC's
# Jeremiah 48:12 and Ezekiel 16:37, a tipexa on the non-final atom in each), and MAM has no
# route-(b) hit at all.  With those two corpora off the page there is nothing left to disclose,
# so the sentence, the tuple and the assertion all went (2026-07-27).  Should a corpus bump ever
# give MAM a route-(b) hit, the disclosure has to come back with it.
#
# The half-sentence that had led into the disclosure -- "it is named for what it mostly holds
# rather than for what it is sifted by" -- went too, on the same reasoning: with route (b) empty
# on the page, it was a methodological remark about a bucket the reader cannot see into.


def _emph(text: str) -> object:
    """Emphasis in running prose, rendered bold -- see ``em.emphasis`` in the stylesheet.

    Replaces the ALL-CAPS emphasis these pages used to carry.  Italic is not available for it:
    ``span.romanized`` has that for accent names.
    """
    return H.em(text, {"class": "emphasis"})


def _n(survey: dict, corpus: str, genre: str, field: str) -> int:
    return survey["corpora"][corpus][genre][field]


def _gray(survey: dict, kind: str | None = None) -> int:
    """The gray-maqaf total, or the count of one of its two kinds."""
    gray = survey["gray_maqaf"]
    return gray["total"] if kind is None else gray["by_kind"][kind]


def _route_count(survey: dict, corpus: str, genre: str, route: str) -> int:
    return survey["corpora"][corpus][genre]["by_route"].get(route, 0)


def _occurrences(survey: dict, corpus: str, genre: str) -> list[dict]:
    return survey["corpora"][corpus][genre]["occurrences"]


def _occurrence(survey: dict, corpus: str, genre: str, bcv: str) -> dict:
    """The single occurrence record a sentence names, or a build failure.

    The two worked examples splice their oracle counts out of these records, so a corpus bump
    that drops the verse -- or that splits it in two -- must stop the build rather than leave
    a sentence standing beside a number that no longer describes it.
    """
    found = [o for o in _occurrences(survey, corpus, genre) if o["bcv"] == bcv]
    if len(found) != 1:
        raise AssertionError(
            f"{corpus}/{genre} {bcv}: expected exactly one occurrence, found {len(found)}"
        )
    return found[0]


def _pair_of(shape: str) -> tuple[str, str]:
    """The two accents a shape holds, as romanized names, non-final atom's first.

    A shape is one field per atom -- ``qad-zaq``, ``0-mer-sil`` -- and every hit has exactly
    two accented atoms, which ``pin_claims`` also asserts.  A field of repeats is one accent
    written twice (MAM's Ezekiel 16:12 נֶ֙זֶם֙ has ``pash+pash``), so it collapses to one name.
    """
    accented = []
    for atom in shape.split("-"):
        if atom == "0":
            continue
        marks = set(atom.split("+"))
        assert len(marks) == 1, f"more than one accent on an atom of {shape}"
        accented.append(marks.pop())
    assert len(accented) == 2, f"not two accented atoms in {shape}"
    first, second = accented
    return first, second


def _pair_table(genre: dict, occurrences: list, hits: int) -> object:
    """The accent pairs that occur on a chanted word of MAM's prose verses, with an example
    of each on a compound and on a simple chanted word.

    Rows are what the data holds, not a list from anywhere: the page reports the pairs that
    occur and no longer says which of Yeivin's categories each case falls under (Ben,
    2026-07-28).  Every compound hit lands in exactly one row, which the total asserts.

    THE SIMPLE COLUMN COVERS EVERY PAIR, since 2026-07-28.  It used to be restricted to the
    eight pairs the compound side has, because two marks on a chanted word are not always two
    accents and this scan has no accent tokenization to tell them apart.  ``simple_exclusion``
    now does tell them apart, mechanically and in the survey rather than here, so the column
    can be honest and complete at once: what it leaves out is counted, and the note under the
    table says what and how much.  Ben's rule for the widening: leave out the pairs that are
    not meaningful -- a stress helper is not a second accent -- and disclose the exclusions.

    ONLY the column headings are ``th``.  The pair column is data, so it is ``td``: a ``th``
    there is bold and centered by browser default, which is what Ben asked about -- a bold
    centered first column claims the pair names are headings for their counts, and they are
    not.  Its rows are also then striped like any other data row.

    THE HEADINGS ARE ABBREVIATED, with the full wording on hover (Ben, 2026-07-28: "Use
    shorter headings ... because they are making the columns too wide").  Five columns of
    prose headings pushed the counts apart; "Compound" and "Simple" are the words the page
    body uses anyway.
    """
    simple_by_pair = genre["simple_by_pair"]
    simple_examples = genre["simple_example_by_pair"]
    counts = Counter(_pair_of(o["shape"]) for o in occurrences)
    compound_examples: dict[tuple[str, str], str] = {}
    for occurrence in occurrences:
        compound_examples.setdefault(_pair_of(occurrence["shape"]), occurrence["word"])
    pairs = set(counts) | {
        (pair.split("-")[0], pair.split("-")[1]) for pair in simple_by_pair
    }
    rows = [
        H.table_row(
            (
                H.table_header("Accent pair"),
                H.table_header(
                    H.abbr("Compound", "On a compound chanted word"), _NUMERIC_CELL
                ),
                H.table_header(
                    H.abbr("Example", "An example of the pair on a compound")
                ),
                H.table_header(
                    H.abbr("Simple", "On a simple chanted word"), _NUMERIC_CELL
                ),
                H.table_header(
                    H.abbr("Example", "An example of the pair on a simple chanted word")
                ),
            )
        )
    ]

    # Pairs sharing a first accent stay together rather than scattering by count (Ben,
    # 2026-07-28, of the two mayela rows: "these should be listed together instead of strictly
    # ordering by # of occurrences").  Groups run commonest-group-first, rows within a group
    # commonest-first.  The count that orders them is the ROW TOTAL, compound and simple
    # together: with the simple column widened to every pair, ordering by the compound column
    # alone would put the commonest pair on a chanted word -- munax before zaqef qatan, 960 of
    # them -- near the bottom, on the strength of its single compound.
    def total_of(pair: tuple[str, str]) -> int:
        return counts.get(pair, 0) + simple_by_pair.get("-".join(pair), 0)

    group_max = Counter()
    for pair in pairs:
        group_max[pair[0]] = max(group_max[pair[0]], total_of(pair))
    compound_total = simple_total = 0
    for pair in sorted(
        pairs,
        key=lambda p: (-group_max[p[0]], p[0], -total_of(p), p[1]),
    ):
        first, second = pair
        compound = counts.get(pair, 0)
        simple = simple_by_pair.get("-".join(pair), 0)
        compound_total += compound
        simple_total += simple
        first_name = _PAIR_FIRST_NAME.get(pair, _ACCENT_DISPLAY[first])
        rows.append(
            H.table_row_of_data(
                (
                    f"{first_name} before {_ACCENT_DISPLAY[second]}",
                    str(compound),
                    _example_cell(compound_examples.get(pair), pair),
                    str(simple),
                    _example_cell(simple_examples.get("-".join(pair)), pair),
                ),
                (None, _NUMERIC_CELL, None, _NUMERIC_CELL, None),
            )
        )
    assert (
        compound_total == hits
    ), f"table rows sum to {compound_total}, not the {hits} hits"
    rows.append(
        H.table_row_of_data(
            ("Total", str(hits), "", str(simple_total), ""),
            (None, _NUMERIC_CELL, None, _NUMERIC_CELL, None),
        )
    )
    return H.table(tuple(rows), {"class": "centered-table accent-pair-table"})


def _example_cell(chanted_word: str | None, pair: tuple[str, str]) -> object:
    """One example form for a table cell, or an empty cell where the pair does not occur.

    Letters and accents only, as everywhere on these pages, and lifted from the survey rather
    than retyped.  The maqaf ``accents_and_letters`` drops is put back, so a compound example
    reads as the one chanted word it is.

    ONE U+05BD SURVIVES IN THE SILLUQ ROWS, and none anywhere else.  ``accents_and_letters``
    drops the codepoint, rightly: it is not an accent, and in any other row it would be a meteg
    the pair says nothing about.  But in a row whose second accent IS the silluq, dropping it
    leaves an example showing one mark where the row promises two -- which is what the first
    pass of this table did.  The one kept is the LAST in the chanted word, which is the silluq;
    an earlier one is an ordinary meteg, and ש֥לֽף־חֽרב showed both until this narrowed.  Same
    rule ``atom_accents`` applies, and the pair is what says the rule applies at all.
    """
    if not chanted_word:
        return ""
    silluq_at = (
        chanted_word.rfind(mpa.METEG) if _ACCENT_DISPLAY[pair[1]] == ROM_SILLUQ else -1
    )
    kept = "".join(
        ch
        for i, ch in enumerate(chanted_word)
        if is_base_letter(ch)
        or mpa.is_accent(ch)
        or i == silluq_at
        or ch == "\N{HEBREW PUNCTUATION MAQAF}"
    )
    return hbo(kept)


def _exclusion_note(genre: dict) -> object:
    """The one exclusion from the simple column worth telling a reader about, with its figures
    spliced.

    Ben, 2026-07-28, asking for the widened column: "perhaps put a sort of footnote (not
    literally a footnote) listing these exclusions, for transparency".  So it is an ordinary
    paragraph under the table, in the page's own voice, naming the marks rather than the
    survey's reason strings, and each count comes out of the survey.

    THE STRESS-HELPER EXCLUSION IS NOT MENTIONED, though ``simple_exclusion`` applies it and
    the survey counts it.  A first pass opened this paragraph with it -- so many words in which
    the two marks are a stress helper and the accent it helps, one accent written twice.  Ben:
    that is "a deep implementation detail that should not be mentioned.  No one would think,
    'oh how would you deal with zarqa stress helpers? were there none in MAM, or just not
    included in this table?  Of course they are not included in this table, that is obvious and
    therefore you don't have to make a methodological note'."  A reader takes a stress helper
    for granted; what they would not take for granted is two marks on ONE letter, which is why
    that one keeps its sentence.  (He also rejected the naming: the pair is conceptually a
    zarqa stress helper before a zarqa, the ``tsinnorit``/``tsinnor`` names being Unicode's
    misnaming rather than the accents'.)

    The total the paragraph used to open with went with the stress-helper sentence.  It was
    every simple chanted word with two different marks, so quoting it would leave a reader to
    subtract, find a remainder this paragraph does not explain, and go looking for the very
    detail Ben cut.
    """
    one_letter = genre["simple_excluded"][mpa.SIMPLE_EXCL_ONE_LETTER]
    telisha = one_letter["ger-telg"] + one_letter["ger2-telg"]
    mahapakh = one_letter["mah-qad"]
    return H.para(
        f"Two marks are not always two accents. The simple column above leaves out"
        f" {_count(telisha + mahapakh)} chanted words whose two marks sit on one letter:"
        f" {_count(telisha)} of them a {ROM_GERESH} or {ROM_GERSHAYIM} with a"
        f" {ROM_TELISHA_GEDOLAH}, and {_count(mahapakh)} a {ROM_MAHAPAKH} with a {ROM_QADMA}."
    )


def _count(n: int) -> str:
    """A small count spelled out, a large one in digits -- for prose, not for table cells."""
    return _SMALL_NUMBERS[n] if n < len(_SMALL_NUMBERS) else f"{n:,}"


# GONE with the classification: _case_parts and _case_table, which listed the four cases the
# categories could not name or reach, verse by verse.  With the rows themselves gone there is
# nothing to list.  They are the only thing that ever needed a book name out of a bcv, so the
# leading-numeral fix for mb_cmn's "2Samuel" went with them.


def _specimen(text: str) -> object:
    """A pointed Hebrew form on a line of its own.

    Ben, 2026-07-28: "why would you only describe in words what can be shown in Unicode?"
    The two forms the intro contrasts differ in one mark, and a reader who can see them
    side by side needs no sentence telling them so."""
    return H.para(hbo(text), {"class": "hebrew-specimen"})


# The letters of the two atoms, used only to find them.  Bare letters, no marks -- the marks
# are exactly what must not be retyped here.
_LO_LETTERS = "לא"
_TAASE_LETTERS = "תעשה"
# What follows the Sabbath commandment's לא־תעשה, and tells it from the one at Deuteronomy 5:8.
_KOL_MELAKHA_LETTERS = "כלמלאכה"


def _letters(chanted_word: str) -> str:
    return "".join(ch for ch in chanted_word if is_base_letter(ch))


def lo_taase_atoms() -> tuple[str, str]:
    """ws/dt/elyon/printed's לא and תעשה, lifted from the vendored strand and never retyped.

    An accent typed by hand into a page module is a claim with no oracle behind it, and this
    one is the page's whole subject.  The strand has the two atoms as two chanted words in the
    Sabbath commandment (Deuteronomy 5:14); Koren's Deuteronomy appendix page has the same two
    atoms as one maqaf compound, and the maqaf is the whole of the difference, so ``_intro``
    builds Koren's form by joining these two with a maqaf and the strand's by a space.

    Letters and accents only -- ``accents_and_letters`` drops the vowels, which these pages do
    not show: the vowels are not what the two forms differ in, and an accentuation discussion
    prints the accents.  (Ben, 2026-07-28, on a first pass that kept them: "we almost never use
    vowels in such discussions.")

    The strand's other תעשה (Deuteronomy 5:8) is already joined to לך, so it is not a two-atom
    pair and does not match; the assertion below is what keeps that true."""
    version = next(
        v
        for v in pd.load_source()["versions"]
        if (v["book"], v["reading"], v["tradition"]) == ("dt", "elyon", "printed")
    )
    pairs = []
    for chanted_verse in version["chanted_verses"]:
        words = chanted_verse.split()
        for first, second in zip(words, words[1:]):
            if (_letters(first), _letters(second)) == (_LO_LETTERS, _TAASE_LETTERS):
                pairs.append((accents_and_letters(first), accents_and_letters(second)))
    assert len(pairs) == 1, f"ws/dt/elyon/printed לא + תעשה pairs: {pairs}"
    return pairs[0]


def lo_taase_taxton_compound() -> str:
    """ws/dt/taxton/printed's לא־תעשה at the Sabbath commandment, lifted and never retyped.

    The p-trad תחתון has the two atoms as a maqaf compound at the same commandment where the
    עליון has them as two chanted words, which is the whole reason the intro can raise a
    carry-over.  Same rule as ``lo_taase_atoms``: the marks ARE the claim, so they come from
    the vendored strand, letters and accents only, with the maqaf put back between the atoms
    that ``accents_and_letters`` drops it from.

    The strand has TWO לא־תעשה compounds, this one and Deuteronomy 5:8; they are told apart by
    what follows, כל־מלאכה here and לך at 5:8.  Both assertions below fail the build rather than
    put the wrong compound on the page.

    The intro shows this compound and says nothing about its marks, so the shape assertion is
    all there is to keep the contrast honest: the specimen makes its point only while the
    compound has a single accent, a qadma on its final atom, against Koren's two.  A
    re-vendoring that moved either mark fails here instead of putting a specimen on the page
    that no longer contrasts with anything.
    """
    version = next(
        v
        for v in pd.load_source()["versions"]
        if (v["book"], v["reading"], v["tradition"]) == ("dt", "taxton", "printed")
    )
    hits = []
    for chanted_verse in version["chanted_verses"]:
        words = chanted_verse.split()
        for word, following in zip(words, words[1:]):
            atoms = word.split("\N{HEBREW PUNCTUATION MAQAF}")
            if [_letters(a) for a in atoms] != [_LO_LETTERS, _TAASE_LETTERS]:
                continue
            if _letters(following) == _KOL_MELAKHA_LETTERS:
                hits.append(word)
    assert len(hits) == 1, f"ws/dt/taxton/printed לא־תעשה before כל־מלאכה: {hits}"
    shape = mpa.shape_of(mpa.atom_accents(hits[0], verse_final=False))
    assert shape == f"0-{mpa.shape_of([[am.QADMA]])}", shape
    return "\N{HEBREW PUNCTUATION MAQAF}".join(
        accents_and_letters(a) for a in hits[0].split("\N{HEBREW PUNCTUATION MAQAF}")
    )


# The second atom of each of the two compounds the Simanim Tiqqun accents on both atoms, used
# only to find them; and the accent each of those atoms has, which is what makes the two
# compounds different cases and is the thing the prose must not leave unsaid.
_SIMTIQ_LO_COMPOUNDS = (("יהיה", am.MERKHA), ("תעשה", am.QADMA))


def simtiq_lo_compounds() -> tuple[str, str]:
    """The Simanim Tiqqun's לא־יהיה and לא־תעשה, built from ws/ex/taxton/printed.

    THIS ONE FORM IS CONSTRUCTED rather than lifted whole, and the construction is the page's
    own claim about the edition, so it is worth stating exactly.  A hand transcription records
    the printed ACCENTS and nothing else (``edition_transcription``), so there is no Unicode
    anywhere in the repo for what the Simanim Tiqqun's page has; what there is, is the strand
    it is compared against and a transcription that differs from it in one mark per compound --
    a munaḥ on the joined לא where the strand has a meteg.  So the strand's compound is read,
    the meteg is replaced by that munaḥ where it stands, and everything else -- the letters, the
    accent on the second atom -- is the strand's.

    The assertions are what keep the construction honest, and each would fail the build rather
    than put a form on the page that the transcription does not say: the first atom is לא with a
    meteg and no accent, and the second atom's sole accent is the one ``_SIMTIQ_LO_COMPOUNDS``
    names.  Letters and accents only, as everywhere on these pages, with the maqaf put back.
    """
    version = next(
        v
        for v in pd.load_source()["versions"]
        if (v["book"], v["reading"], v["tradition"]) == ("ex", "taxton", "printed")
    )
    out = []
    for second_letters, second_accent in _SIMTIQ_LO_COMPOUNDS:
        found = set()
        for chanted_verse in version["chanted_verses"]:
            for word in chanted_verse.split():
                atoms = word.split("\N{HEBREW PUNCTUATION MAQAF}")
                if [_letters(a) for a in atoms] != [_LO_LETTERS, second_letters]:
                    continue
                found.add(word)
        assert len(found) == 1, f"ws/ex/taxton/printed לא־{second_letters}: {found}"
        atoms = found.pop().split("\N{HEBREW PUNCTUATION MAQAF}")
        assert mpa.METEG in atoms[0], atoms
        assert not [c for c in atoms[0] if mpa.is_accent(c)], atoms
        assert [c for c in atoms[1] if mpa.is_accent(c)] == [second_accent], atoms
        joined = accents_and_letters(atoms[0].replace(mpa.METEG, am.MUNAX))
        out.append(
            f"{joined}\N{HEBREW PUNCTUATION MAQAF}{accents_and_letters(atoms[1])}"
        )
    return out[0], out[1]


def pin_claims(survey: dict) -> None:
    """Fail the build if the data stops supporting a claim the prose states in words.

    The counts on this page are spliced from the survey, so they cannot drift.  Its
    ARGUMENT cannot be spliced, and every sentence of it rests on a handful of facts that a
    re-vendoring or a corpus bump could quietly overturn.  So they are pinned here, and this
    raises rather than warns -- the same build-fails-on-data-drift behavior
    ``printed_decalogue_strands.resolve_readings`` has, and for the same reason: a warning in
    a generator's output is a warning nobody reads.
    """
    # GONE with the classification (2026-07-28): two assertions that pinned sentences the page
    # no longer makes -- that MAM's prose has no bare-habit (route (b)) case, and that exactly
    # one route-(a) case falls under no named configuration.  Both were about which of Yeivin's
    # categories a case belongs to, and the page now reports the pairs that occur without
    # placing any case in a category.  The survey still computes the routes; nothing on the page
    # depends on them, so nothing here defends them.

    # The oleh-we-yored assertions that stood here went with the poetic section's detail (#83).
    # They defended a sentence counting how many poetic hits were one oleh-we-yored spread across
    # a compound rather than two accents; the section now says only that the poetic system is a
    # different matter, and pins nothing beyond the spliced hit count.

    # The intro speaks for MAM, and says of EVERY hit there that its two accents sit on two
    # atoms and never both on one, the compound having two atoms or occasionally three.  None
    # of that is spliced, so all of it is pinned: one four-atom hit, one atom carrying a stacked
    # pair, or one hit with a single accent would leave those words quietly wrong -- and each of
    # those does occur elsewhere in the survey (WLC's Joshua 20:4 has the single accent, the
    # poetic corpus has revia mugrash), so none is a hypothetical.  A field of REPEATS is the one
    # thing allowed: MAM's Ezekiel 16:12 נֶ֙זֶם֙ has ``pash+pash``, one accent written twice.
    #
    # The same loop is what pins "but never more than two" (Ben's wording, 2026-07-28), since
    # exactly two accented atoms and no stacked pair is what "never more than two" amounts to
    # here.  MIND THE SCOPE: the survey scans maqaf compounds, so the pin covers compounds only.
    # A chanted word that is a lone atom is never scanned, and the sentence speaks for those too.
    for o in _occurrences(survey, "mam_simple", "prose"):
        atoms = o["shape"].split("-")
        assert len(atoms) in (2, 3), o
        assert len([a for a in atoms if a != "0"]) == 2, o
        assert all(len(set(a.split("+"))) == 1 for a in atoms), o

    # THE PAGE'S ANSWER, the one claim about the data that only the data can keep true: no
    # compound in MAM's PROSE verses is accented alike twice.  That is the intro's flat answer
    # to whether anything in Tanakh looks like Koren's compound.
    #
    # Two assertions about Isaiah 40:7 stood beside it -- that it is the single compound whose
    # non-final atom has a munax, and that it pairs that munax with a zaqef qatan.  They
    # defended the "Koren's compound" section's sentences, which went with the section (Ben,
    # 2026-07-28).  The verse is still on the page, as the compound example in the table's
    # munax-before-zaqef-qatan row, but it is spliced there rather than named in prose, so the
    # table's own row is what it now depends on.
    #
    # Prose only, deliberately.  The intro used to say "not in poetic ones" too, and the poetic
    # verses do bear it out -- but only among compounds whose maqaf is WRITTEN, and Breuer has
    # the poetic maqaf after a secondary mark customarily left unwritten.  A compound accented
    # alike twice with an unwritten maqaf is invisible to this scan, so the claim could not be
    # made flatly there.  Ben, 2026-07-27: drop the clause rather than qualify it, this page
    # being about the prose system.  Pinning the poetic half anyway would re-assert in code a
    # claim the page had to withdraw in prose.
    same = [
        o
        for o in _occurrences(survey, "mam_simple", "prose")
        if len({a for a in o["shape"].split("-") if a != "0"}) == 1
    ]
    assert (
        not same
    ), f"MAM prose is stated to have no compound accented alike twice: {same}"


def _intro(survey: dict) -> tuple[object, ...]:
    # The headline frequency is MAM's, not WLC's.  A claim about what the accentuation DOES
    # wants a consensus text; WLC is one manuscript as one transcription reads it, and its
    # blemishes are visible in this very count (Joshua 20:4 זקני־העיר, whose compound has its
    # only accent on the non-final atom because the mark on העיר is a mid-verse meteg).  WLC and
    # UXLC keep their table columns, which are about the texts themselves; what they no longer do
    # is answer the page's question.  Ben, 2026-07-26: "let's leave WLC (and indeed the LC) out of
    # this" -- so the two WLC compounds with a munax on each atom (2 Chr 1:11, 1 Chr 27:14), and
    # the paragraphs that read them as Koren's nearest precedent, are gone rather than demoted.
    mam_prose = survey["corpora"]["mam_simple"]["prose"]
    pct = 100.0 * mam_prose["hits"] / mam_prose["maqaf_compounds"]
    lo, taase = lo_taase_atoms()
    # The metigah-zaqef count, spliced rather than hedged as "nearly all" (Ben, 2026-07-28:
    # "why be coy, why not just say the number").  Counted the same way the pair table counts,
    # so the sentence and the table's top row cannot disagree.
    metigah = sum(
        1
        for o in _occurrences(survey, _CORPUS, "prose")
        if _pair_of(o["shape"]) == ("qad", "zaq")
    )
    return (
        H.heading_level_1(PAGE_TITLE),
        H.para(
            wrap_hebrew_runs(
                "Maqaf marks join two or more atoms into a single chanted word. In the prose"
                " system a chanted word usually has exactly one accent. In a small minority of"
                " cases, a chanted word has two accents, but never more than two. Of the"
                f" {mam_prose['maqaf_compounds']:,} maqaf"
                f" compounds in the prose verses of MAM, {mam_prose['hits']} ({pct:.2f}%) have"
                " an accent on a non-final atom. In every one of them the two accents sit on"
                " two atoms of the compound and never both on one, the compound itself having"
                " two atoms, or occasionally three. This page counts those cases, sorts them,"
                " and asks what they mean for the chanted word"
            )
        ),
        _specimen(f"{lo}\N{HEBREW PUNCTUATION MAQAF}{taase}"),
        H.para(
            (
                "in Koren's Deuteronomy ",
                link("appendix Decalogue", "printed-decalogue-koren.html"),
                *wrap_hebrew_runs(
                    f" (the {ELYON}) — a maqaf compound with a {ROM_MUNAX} on "
                ),
                _emph("both"),
                *wrap_hebrew_runs(
                    " of its atoms. The Wikisource strand Koren otherwise follows in every"
                    " accent has"
                ),
            )
        ),
        _specimen(f"{lo} {taase}"),
        H.para(
            wrap_hebrew_runs(
                f"instead: two chanted words, each with a {ROM_MUNAX} of its own."
            )
        ),
        # WHERE THE MAQAF DOES LIVE, added at Ben's request 2026-07-28.  ONE SENTENCE AND THE
        # SPECIMEN, in his own words: a first pass spread the same suggestion over two
        # paragraphs, naming the strand, the compositor and what the page could not settle, and
        # was "way too belabored regarding speculation about the source of the error".  The
        # specimen carries what those sentences said -- one accent, and it is not Koren's pair.
        #
        # "the p-trad תחתון", not a bare "the תחתון" and not "Koren's own תחתון pages".  The two
        # תחתון strands part at exactly this compound -- the m-trad one has the two atoms
        # separate, as the עליון does -- so a bare "the תחתון" would be false of one of them.
        # Naming the strand fixes that without the possessive: a page is not accented, a chanted
        # word is, and "own" is a word Ben has struck from this repo's prose more than once.
        #
        # IT COMES BEFORE THE QUESTION, not after the answer (Ben, 2026-07-28).  The cheap
        # explanation is disposed of first, and the question is then asked of a maqaf taken
        # seriously -- which is what the rest of the page does.  Put after the answer, it read as
        # an afterthought undercutting the count it followed.
        H.para(
            wrap_hebrew_runs(
                "The odd maqaf in Koren might simply be accidentally carried over from the"
                f" p-trad {TAHTON}:"
            )
        ),
        _specimen(lo_taase_taxton_compound()),
        H.para(
            wrap_hebrew_runs(
                "But if we take the maqaf seriously, is there anything in Tanakh like Koren's"
                f" two-{ROM_MUNAX} compound?"
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "There is not. No maqaf compound in MAM's prose verses has the same accent on"
                f" both atoms, not once. Of the {mam_prose['hits']} prose cases, {metigah} are"
                " a single grammatical category, metigah-zaqef: a"
                f" {ROM_QADMA} before a {ROM_ZAQEF_QATAN}."
            )
        ),
    )


# GONE: "What is counted", whittled to one sentence over two days and then cut outright (Ben,
# 2026-07-28: "I question the value of this whole, small section").  What that last sentence
# said -- the question is whether a compound has an accent other than the one on its last atom
# -- the intro already says, in the same words, as the thing the page counts.  A section that
# restates the intro is not a definition, it is an echo.
#
# What went before it, each cut for a reason worth keeping:
#   * A paragraph calling the space-delimited unit a chanted word and then arguing that
#     splitting on spaces gives chanted words -- assuming the premise and proving it.  It also
#     taught a shape notation (qad-zaq, 0-mer-sil) used nowhere else on the page.
#   * A paragraph saying a meteg and a silluq are one sign and that it counts as an accent only
#     verse-finally.  "Useless internal implementation explanation.  Also, super obvious.
#     Basically saying: I'm not an idiot."  The rule lives in atom_accents' docstring, where a
#     reader of the code needs it and a reader of the page does not.
#   * A sentence saying a compound counts once however many of its atoms are accented, and is
#     counted against every maqaf compound in those verses.  "Nitty-gritty details of counting
#     at a level of detail not of concern to my model of who the reader is."  It lives in
#     ``scan``.
# Every rule they stated still governs the count; none of them was ever page text's job.


# GONE: "Which text this page counts", the last remnant of a section that once compared three
# corpora (Ben, 2026-07-28).  Its final paragraph told the reader that MAM is a consensus text
# rather than a diplomatic one and is not one of Breuer's editions -- true, and every word of it
# an answer to something that happened in the drafting rather than to anything on the page.  Ben:
# "I had to explain all that to you because you kept saying wacky stuff about MAM being a Breuer
# edition, and initially framing this whole page against WLC, but that's dirty laundry/internal
# history the reader doesn't need to know about.  Elsewhere it is clear that MAM is the
# reference."  The rule it stands for: a paragraph that exists because a discussion went a
# certain way is internal history, not page text, however accurate it is.  The corpus is named
# where the counts are, which is where a reader meets it.


def _prose_section(survey: dict) -> tuple[object, ...]:
    # This section absorbed two that used to precede it, "Two routes, and why they must be
    # counted apart" and "How a hit is assigned to a route" (Ben, 2026-07-27: keep the page to
    # one weird thing in Koren and whether it ever happens in MAM, "with at most one passing
    # remark about things being more complicated in L, as Yeivin points out").  Both were built
    # around route (b), the maqaf written after an atom that keeps its own conjunctive -- a
    # habit of a particular naqdan, which MAM, not being a manuscript, has no instance of.  The
    # material they carried is issue #83, which links to #82.
    #
    # What survives of them here: the closed-list sentence, because "Koren's shape is not in the
    # list" is only worth saying of a list that is closed; the passing L remark; and ONE worked
    # example.  The example is kept against a page that would otherwise assert its category
    # names and never show one being decided -- Judges 7:13, because metigah-zaqef is the
    # category the overwhelming majority of the hits fall into.  Judges 8:10 שלף־חרב went with
    # the section: it made the subtler point that a mark AT the atom's own stress can still be
    # secondary, which needs the route machinery to be worth making.
    #
    # "usual place", not "all N": the survey records only the MODE of letters-after-accent per
    # atom, so the mode is the whole of what a spliced number can defend.  The unanimity that in
    # fact holds here is not in the JSON, and prose must not claim more than the build re-derives.
    #
    # The one-row table went too.  Its two surviving columns restated the intro's own sentence,
    # and the other three were route counts.
    genre = survey["corpora"][_CORPUS]["prose"]
    hits = _n(survey, _CORPUS, "prose", "hits")
    occurrences = _occurrences(survey, _CORPUS, "prose")
    return (
        H.heading_level_2("The prose verses"),
        # THE OPENING SENTENCE, rewritten 2026-07-28.  It used to read "A mark on a non-final
        # atom is there because the compound is one chanted word, and a mark belonging to that
        # chanted word as a whole has landed short of its last atom" -- Ben: "one of the least
        # comprehensible things you've ever written, while of course sounding erudite and
        # certain."  Three faults, kept here so none of them comes back:
        #   * The "because" ran backwards.  Being one chanted word is why a compound normally
        #     has exactly ONE accent -- the reason these cases are rare (233 of 36,786), not the
        #     reason the mark is there.
        #   * "landed short of its last atom" pictured a mark that missed.  A secondary accent
        #     has its own position, in front of the main accent; nothing aimed at the last atom
        #     and fell short.  Transformative framing of exactly the banned kind.
        #   * It asserted of all 233 what holds of the 230 routed ones; the three undecided are
        #     undecided precisely because this cannot be checked for them.
        # What replaces it is the point MAQAF_IS_THE_LAST_RUNG stands for: these marks are not a
        # phenomenon of compounds.  The list is Yeivin's list of accents that can come first of
        # two on an ordinary word, which is why Koren's two identical accents are not on it.
        # JUST THE PAIRS THAT OCCUR (Ben, 2026-07-28).  The table used to be Yeivin's closed
        # list, with each case placed in one of his categories, plus two rows for the cases the
        # placement could not name or could not reach.  All of that machinery exists to answer
        # a question this page does not need: whether the maqaf is optional -- a manuscript
        # joining two atoms that each keep their own accent -- or whether the pair is one only
        # a single chanted word can carry.  Ben: "this is an interesting research question, and
        # gets to the more restricted definition of secondary that I think Breuer uses, but can
        # we just avoid the whole thing and say these are the pairs that are known to occur?"
        # So the rows are now observed pairs, every case lands in one, and the undecided and
        # unnamed rows and their four-case table are gone with the question they belonged to.
        #
        # Gone with them (same day, same reason -- "I'm really trying to narrow the scope of
        # this document, and get out alive"): a closing paragraph reporting Yeivin §§293, 357 on
        # manuscripts that have a maqaf after an atom keeping its own conjunctive, and MAM
        # having no case of it.  That paragraph WAS the optional-maqaf question, stated as an
        # aside; with the classification gone the page can no longer support its "no case of
        # it", which was a route count.  Issue #83 holds the material.
        H.para(
            "Two accents can appear on a chanted word, whether it is compound or simple."
            " These are the pairs that occur, in the prose verses of MAM, with an example"
            " of each:"
        ),
        _pair_table(genre, occurrences, hits),
        _exclusion_note(genre),
        # Yeivin in one sentence after the table, not a column in it (Ben, 2026-07-28: "no need
        # to put Yeivin section numbers in the table, just mention most of these pairs are
        # covered in Yeivin ITM sections blah").  "Most", not all: the two pairs ending in a
        # pashta are on no list of his.  §§210 and 216 are the two mayela sections, which the
        # survey's own configuration names never carried; the other four are the ones
        # ``_NAMED_CONFIGURATIONS`` cites.
        # "Several", not "Most" (2026-07-28).  It read "Most of these pairs" while the table's
        # rows were the eight the compound side has, seven of which those sections cover.  With
        # the simple column widened to every pair the rows are eighteen, and the same sections
        # cover seven of them -- most of the CASES still, the pairs they cover being the common
        # ones, but no longer most of the pairs, which is what the sentence said.
        H.para(
            (
                "Several of these pairs are covered in Yeivin's ",
                _itm(),
                " §§210, 216, 221, 224, 233 and 241.",
            )
        ),
    )


# The two books this page cites, each written short with the full title on hover (Ben,
# 2026-07-28: "'Breuer, Chapter 9' doesn't say what breuer book ... use CoS and ITM
# respectively, and make these hover-reveal the full title").  Single-sourced here, so the two
# sections cannot come to cite them differently.
_ITM_TITLE = "Introduction to the Tiberian Masorah"
_COS_TITLE = "The Cantillation of Scripture"


def _itm() -> object:
    return H.abbr("ITM", _ITM_TITLE)


def _cos() -> object:
    return H.abbr("CoS", _COS_TITLE)


def _koren_section() -> tuple[object, ...]:
    # GONE (Ben, 2026-07-28): the whole "Koren's compound" opening -- that every case in the
    # table pairs two DIFFERENT accents where Koren's two are the same accent twice, and then
    # Isaiah 40:7 as the one case sharing one of Koren's two.  With it went ``isaiah_munax_
    # compound`` and the two pin_claims assertions that defended those sentences; the table now
    # shows Isaiah 40:7 itself, in the munax-before-zaqef-qatan row's compound example.
    #
    # GONE with them (Ben, 2026-07-28: "don't even get into the accents on a tangled
    # presentation"): a paragraph reporting that MAM's Exodus 20:10 לא־תעשה has a munax on each
    # atom, and then taking it back -- that being the two strands tangled together in one
    # printing rather than either strand, which untangled has no maqaf there.
    #
    # What survives is the printed-edition comparison, promoted from an h3 to a section of its
    # own now that the heading above it is gone.  It NAMES BOTH ACCENTS AND SHOWS THEM (Ben,
    # 2026-07-28: "don't be coy, show me the actual accents. you are being REALLY coy here, not
    # even describing in prose what the non-munax accent is"): the two compounds differ from
    # each other in the second accent, which is the whole reason there are two of them.
    lo_yihye, lo_taase = simtiq_lo_compounds()
    return (
        H.heading_level_2("The nearest thing in a printed edition"),
        H.para(
            (
                *wrap_hebrew_runs(
                    "None of the printed editions transcribed for these pages has Koren's"
                    " shape either. The nearest is the "
                ),
                link("Simanim Tiqqun", "printed-decalogue-simanim.html"),
                *wrap_hebrew_runs(
                    f"'s {ROM_MUNAX} on the joined לא of two compounds, where every strand has"
                    f" a {ROM_METEG}:"
                ),
            )
        ),
        _specimen(lo_yihye),
        _specimen(lo_taase),
        H.para(
            wrap_hebrew_runs(
                f"The second accent is a {ROM_MERKHA} in the first of those and a {ROM_QADMA}"
                f" in the second, so neither is Koren's {ROM_MUNAX} twice — but each is the"
                " same phenomenon, a non-final atom with an accent, one step short of the same"
                " shape, and in this very passage."
            )
        ),
    )


def _poetic_section(survey: dict) -> tuple[object, ...]:
    # Cut to one paragraph (Ben, 2026-07-27: "roughly speaking just say things are different in
    # the poetic system, without getting into details").  The page is about the prose system,
    # and this section is here only so a reader is not left wondering what happens in the other
    # one.  Gone with the details: the table, Breuer's short list of poetic verses where the
    # maqaf IS written (Job 6:10, Proverbs 25:20), the oleh-we-yored overshoot with Psalms 70:6,
    # and the note that the route split was never run over poetic verses -- the last of which
    # went with the routes themselves.  All of it is issue #83.
    #
    # The two facts that survive are the two that make the count meaningless here rather than
    # merely different, so neither is a detail: the unwritten maqaf (which puts most of the
    # phenomenon out of the scan's reach) and the poetic system's readiness to accent one
    # chanted word twice (which is the asymmetry a prose-trained reader would get wrong).
    #
    # The gray maqaf closes the first of those with a figure instead of a hedge (2026-07-27):
    # the sentence used to call the poetic count "a floor" and stop, which told a reader the
    # number was wrong without telling them by how much.  It stays inside the one paragraph #83
    # cut this section down to, and it names no accent -- spelling out what the 47 are would
    # want oleh-we-yored and tsinnorit in prose, which is the detail that was cut.
    hits = _n(survey, _CORPUS, "poetic", "hits")
    return (
        H.heading_level_2("The poetic verses"),
        H.para(
            (
                "The poetic system is a different matter, and different enough that the same"
                " count would not mean the same thing there. It puts two marks on one chanted"
                " word readily and systematically (Breuer, ",
                _cos(),
                " ch. 9 §§20–26), where the prose system does so rarely, and in the few pairs"
                " above. And many of its maqafs are not written at all: Breuer (§§27, 37)"
                " records that in poetic verses the maqaf after a secondary mark is customarily"
                " left unwritten while the atom still counts as joined, so a survey that finds"
                " compounds by looking for a written maqaf reaches only part of what is there."
                f" MAM's poetic verses have {hits} cases by that measure, and MAM has the other"
                f" part of the measure too: it supplies {_gray(survey)} gray maqafs, its mark"
                " for a maqaf the manuscript leaves unwritten where the chanted word needs one."
                f" Of those, {_gray(survey, mpa.GRAY_KIND_SECOND)} join an atom that has an"
                " accent alongside the compound's accent; the other"
                f" {_gray(survey, mpa.GRAY_KIND_SPREAD)} have one accent written across the"
                " two atoms. Neither figure belongs beside the prose one.",
            )
        ),
    )


def render_body_contents(survey: dict) -> tuple[object, ...]:
    pin_claims(survey)
    sections: list[object] = [
        *_intro(survey),
        *_prose_section(survey),
        *_koren_section(),
        *_poetic_section(survey),
    ]
    return (H.div(tuple(sections), {"class": _WIDTH_CLASS}),)


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "maqaf-nonfinal-accents.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the maqaf-nonfinal-accents page.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=mpa.default_json_out_path(),
        help="Output JSON path for the survey behind the page.",
    )


def run(args: argparse.Namespace) -> None:
    survey = mpa.build_survey()
    mpa.write_json(survey, args.json_out)

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(survey),
        write_ctx=H.WriteCtx(
            title=PAGE_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    prose_hits = _n(survey, _CORPUS, "prose", "hits")
    print(f"JSON: {args.json_out}")
    print(f"HTML: {html_out} (MAM prose hits: {prose_hits})")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
