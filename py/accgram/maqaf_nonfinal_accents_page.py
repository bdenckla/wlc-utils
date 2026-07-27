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
from accgram import rtms_report
from accgram.almost_errors_html_shared import link, wrap_hebrew_runs
from accgram.printed_decalogue_strands import (
    ELYON,
    ROM_ETNAHTA,
    ROM_MAHAPAKH,
    ROM_MERKHA,
    ROM_METEG,
    ROM_MUNAX,
    ROM_QADMA,
    ROM_SILLUQ,
    ROM_TEVIR,
    ROM_TIPEHA,
    ROM_ZAQEF_QATAN,
)
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


# The survey's configuration strings are code identifiers -- they spell ח with an x, as the
# transliteration standard requires of code and of the tracked JSON alike.  Rendered prose takes
# the ROM_* romanizations instead, so the bullet list below cannot print "etnaxta" at a reader.
# Keys are ``maqaf_nonfinal_accents._NAMED_CONFIGURATIONS``' values verbatim; ``_config_label``
# raises on any key not here, so a new configuration cannot reach the page unrendered.
_CONFIG_DISPLAY = {
    "metigah-zaqef (ITM §224)": (
        f"metigah-zaqef: a {ROM_QADMA} before a {ROM_ZAQEF_QATAN} (§224)"
    ),
    "munax-zaqef (ITM §221)": f"a {ROM_MUNAX} before a {ROM_ZAQEF_QATAN} (§221)",
    "mayela before an etnaxta": f"the mayela {ROM_TIPEHA} before an {ROM_ETNAHTA}",
    "mayela before a silluq": f"the mayela {ROM_TIPEHA} before a {ROM_SILLUQ}",
    "secondary merkha in the tipexa's chanted word (ITM §233)": (
        f"a secondary {ROM_MERKHA} in the {ROM_TIPEHA}'s chanted word (§233)"
    ),
    "secondary merkha in the silluq's chanted word (ITM §233)": (
        f"a secondary {ROM_MERKHA} in the {ROM_SILLUQ}'s chanted word (§233)"
    ),
    "secondary merkha in the tevir's chanted word (ITM §§233, 241)": (
        f"a secondary {ROM_MERKHA} in the {ROM_TEVIR}'s chanted word (§§233, 241)"
    ),
    "secondary mahapakh in the tevir's chanted word (ITM §241)": (
        f"a secondary {ROM_MAHAPAKH} in the {ROM_TEVIR}'s chanted word (§241)"
    ),
}

# A route-(a) hit that matches no named configuration: the survey put it there because the mark
# is not where that atom's own accent falls, which rules out the habit without naming a category.
# No em dash inside the label -- the bullets end in " — <count>", and a second one reads as a
# second clause rather than as the count it introduces.
_UNNAMED_LABEL = (
    "no named configuration: the mark is simply not at that atom's own accent position"
)

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


def _is_unnamed(configuration: str | None) -> bool:
    return configuration is None or configuration.startswith("unnamed")


def _secondary_by_configuration(survey: dict, corpus: str, genre: str) -> list:
    """(configuration, count) over route-(a) hits only, commonest first.

    Counting the route rather than filtering the configuration name is what makes the bullet
    list sum to the table's "secondary (inherited)" cell: the unnamed route-(a) case belongs in
    the list, and the undecided ones do not.  Among equal counts the unnamed one sorts last --
    it is the residue of the named ones, so it reads wrongly above any of them.
    """
    counts = Counter(
        o["configuration"]
        for o in _occurrences(survey, corpus, genre)
        if o["route"] == mpa.ROUTE_SECONDARY
    )
    return sorted(counts.items(), key=lambda cn: (-cn[1], _is_unnamed(cn[0]), cn[0]))


def _config_label(configuration: str | None) -> str:
    if configuration in _CONFIG_DISPLAY:
        return _CONFIG_DISPLAY[configuration]
    if _is_unnamed(configuration):
        return _UNNAMED_LABEL
    raise KeyError(f"no rendered label for configuration {configuration!r}")


def _count(n: int) -> str:
    """A small count spelled out, a large one in digits -- for prose, not for table cells."""
    return _SMALL_NUMBERS[n] if n < len(_SMALL_NUMBERS) else f"{n:,}"


def _letters_from_end(n: int) -> str:
    return f"{_count(n)} letter{'' if n == 1 else 's'} from the end"


def pin_claims(survey: dict) -> None:
    """Fail the build if the data stops supporting a claim the prose states in words.

    The counts on this page are spliced from the survey, so they cannot drift.  Its
    ARGUMENT cannot be spliced, and every sentence of it rests on a handful of facts that a
    re-vendoring or a corpus bump could quietly overturn.  So they are pinned here, and this
    raises rather than warns -- the same build-fails-on-data-drift behavior
    ``printed_decalogue_strands.resolve_readings`` has, and for the same reason: a warning in
    a generator's output is a warning nobody reads.
    """
    assert (
        _route_count(survey, "mam_simple", "prose", mpa.ROUTE_HABIT) == 0
    ), "MAM is stated to have no bare-habit case in prose"

    # "all but one fall under a named grammatical configuration", under "The prose verses".
    # The count of named ones is spliced; the ONE is not, and it is the sort of thing a
    # re-vendoring moves either way -- to zero (and the sentence understates) or to several
    # (and it is simply false).
    unnamed = [
        c
        for c, _n in _secondary_by_configuration(survey, "mam_simple", "prose")
        if c is None or c.startswith("unnamed")
    ]
    assert (
        len(unnamed) == 1
    ), f"MAM prose: expected one unnamed secondary kind, got {unnamed}"

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
    for o in _occurrences(survey, "mam_simple", "prose"):
        atoms = o["shape"].split("-")
        assert len(atoms) in (2, 3), o
        assert len([a for a in atoms if a != "0"]) == 2, o
        assert all(len(set(a.split("+"))) == 1 for a in atoms), o

    # THE PAGE'S ANSWER, in two claims that only the data can keep true: no compound in MAM's
    # PROSE verses is accented alike twice, and the single one whose non-final atom has a munax
    # is Isaiah 40:7.  Both are stated flatly in the intro and again under "Koren's reading".
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
    mam_munax = [
        o
        for o in _occurrences(survey, "mam_simple", "prose")
        if o["shape"].split("-")[0] == mpa.shape_of([[am.MUNAX]])
    ]
    assert [o["bcv"] for o in mam_munax] == ["is40:7"], mam_munax


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
    return (
        H.heading_level_1(PAGE_TITLE),
        H.para(
            wrap_hebrew_runs(
                "Maqaf marks join two or more atoms into a single chanted word. In the prose"
                " system a chanted word usually has exactly one accent, and only in a small"
                f" minority of cases two. Of the {mam_prose['maqaf_compounds']:,} maqaf"
                f" compounds in the prose verses of MAM, {mam_prose['hits']} ({pct:.2f}%) have"
                " an accent on a non-final atom. In every one of them the two accents sit on"
                " two atoms of the compound and never both on one, the compound itself having"
                " two atoms, or occasionally three. This page counts those cases, sorts them,"
                " and asks what they mean for one printed reading in particular."
            )
        ),
        H.para(
            (
                "The reading is Koren's Deuteronomy ",
                *[link("appendix Decalogue", "printed-decalogue-koren.html"), ", "],
                *wrap_hebrew_runs(
                    "which sets לא־תעשה as a maqaf compound and accents "
                ),
                _emph("both"),
                *wrap_hebrew_runs(
                    f" atoms with a {ROM_MUNAX}, where the strand it otherwise follows in"
                    " every accent sets the two atoms apart as chanted words of their own."
                    " Is there anything in Tanakh like it?"
                ),
            )
        ),
        H.para(
            wrap_hebrew_runs(
                "There is not. No maqaf compound in MAM's prose verses has the same accent on"
                " both atoms, not once. Nearly all of the"
                f" {mam_prose['hits']} prose cases are a single grammatical category, a"
                f" {ROM_QADMA} before a {ROM_ZAQEF_QATAN}; and the one case whose non-final"
                f" atom has a {ROM_MUNAX} — Isaiah 40:7 נבל־ציץ — has a {ROM_ZAQEF_QATAN} as"
                f" the compound's own accent, not a second {ROM_MUNAX}. Nor is any printed"
                " edition known to have Koren's reading before it."
            )
        ),
    )


def _what_is_counted() -> tuple[object, ...]:
    # The old version of this section opened by calling the space-delimited unit a chanted word
    # and then argued that splitting on spaces gives chanted words -- assuming the premise and
    # then proving it.  It also taught a shape notation (qad-zaq, 0-mer-sil) that appeared
    # nowhere else on the page, the configuration list below going by Yeivin's category names
    # instead; that paragraph is gone, which also frees "shape" for its ordinary English sense
    # in "Koren's reading".
    return (
        H.heading_level_2("What is counted"),
        H.para(
            "A maqaf joins an atom to the next, and what it makes is one chanted word."
            " The question put to every maqaf compound in the Tanakh is whether an atom"
            " the maqaf joins has an accent of its own, over and above the accent the"
            " compound has on its last atom. A compound counts once however many of its"
            " atoms are accented, and it is counted against every maqaf compound in those"
            " verses, accented on one atom or on two."
        ),
        H.para(
            f"A {ROM_METEG} and a {ROM_SILLUQ} are one and the same sign. That sign counts"
            " here as an accent only on the last chanted word of a verse, where it is a"
            f" {ROM_SILLUQ}; anywhere else it is a {ROM_METEG}, which is not an accent at"
            " all."
        ),
    )


def _corpus_caveat() -> tuple[object, ...]:
    # What is left of "What these three columns are, and are not" once there is one column.  Its
    # WLC and UXLC bullets went with them; so did the paragraph reporting that two of the three
    # Leningrad readings Yeivin cites for this feature are contradicted by the transcription,
    # which was there to stop a reader treating WLC as a second manuscript and has nothing to
    # stop once WLC is off the page.  That observation is issue #82 now, not page text -- and it
    # is sharper there, since UXLC and MAM turn out to contradict him at both verses as well.
    # The MAM bullet is what had to survive: every claim here takes MAM, so the reader is owed a
    # sentence on what MAM is.  A second paragraph justifying the choice of a consensus text was
    # drafted and cut (Ben, 2026-07-27) -- with no comparison left on the page, it defended a
    # decision no reader is in a position to question.
    return (
        H.heading_level_2("Which text this page counts"),
        H.para(
            "Every count on this page is MAM's. MAM is a consensus text rather than a"
            " diplomatic one: not a single manuscript's reading, but the accentuation the"
            " Masoretic tradition converges on. It largely follows Breuer, but it is not one"
            " of Breuer's own editions."
        ),
    )


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
    configs = _secondary_by_configuration(survey, _CORPUS, "prose")
    hits = _n(survey, _CORPUS, "prose", "hits")
    secondary = _route_count(survey, _CORPUS, "prose", mpa.ROUTE_SECONDARY)
    undecided = _route_count(survey, _CORPUS, "prose", mpa.ROUTE_UNDECIDED)
    example = _occurrence(survey, _CORPUS, "prose", "ju7:13")
    return (
        H.heading_level_2("The prose verses"),
        H.para(
            "A mark on a non-final atom is there because the compound is one chanted word,"
            " and a mark belonging to that chanted word as a whole has landed short of its"
            " last atom. The marks that can do this are a closed list, which Yeivin gives"
            f" for the prose system: {ROM_QADMA} before a {ROM_ZAQEF_QATAN} (metigah-zaqef,"
            f" §224), {ROM_MUNAX} before a {ROM_ZAQEF_QATAN} (§221), a secondary"
            f" {ROM_MERKHA} in the chanted word of a {ROM_TIPEHA}, of a {ROM_SILLUQ} or of a"
            f" {ROM_TEVIR} (§§233, 241), a secondary {ROM_MAHAPAKH} in the chanted word of a"
            f" {ROM_TEVIR} (§241), and the mayela {ROM_TIPEHA} before an {ROM_ETNAHTA} or a"
            f" {ROM_SILLUQ}."
        ),
        H.para(
            (
                f"Of MAM's {hits} cases, {secondary} are marks that are not the atom's own"
                " accent — all but one of them under a named category from that list — and"
                f" {_count(undecided)} are undecided, their non-final atom never standing"
                " free elsewhere in the text for its mark's position to be checked."
                " Deciding one is a matter of position, and needs no"
                " phonology: the atom is looked up elsewhere standing free, a chanted word"
                " by itself with an accent of its own, and the letters following the accent"
                " are counted in each. ",
                *wrap_hebrew_runs(
                    f"Judges 7:13 והנה־איש has its {ROM_QADMA}"
                    f" {_letters_from_end(example['oracle']['joined_letters_after_accent'])},"
                    " where among the"
                    f" {_count(example['oracle']['free_occurrences'])} free-standing והנה the"
                    " accent's usual place is"
                    f" {_letters_from_end(example['oracle']['free_letters_after_accent'])} —"
                    " so the mark is not that atom's own accent, and it is the metigah of"
                    " §224."
                ),
            )
        ),
        H.para("The cases, by configuration:"),
        H.unordered_list(
            tuple(f"{_config_label(config)} — {n}" for config, n in configs),
        ),
        H.para(
            "Things are less tidy in a manuscript. Yeivin (§§293, 357) reports that some"
            " manuscripts have a maqaf even after an atom that keeps its own conjunctive,"
            " with no grammatical trigger at all, and names the Leningrad Codex for the"
            " habit. MAM, which is not a manuscript, has no case of it."
        ),
    )


def _koren_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Koren's reading"),
        H.para(
            (
                "Every one of those cases pairs two ",
                _emph("different"),
                " accents: the compound's own accent, and a secondary mark of a kind that"
                " can precede it. Koren's two are the same accent twice, and no chanted"
                " word in MAM is accented that way — so there is no category the reading"
                " could be said to be following, and nothing in MAM it could be said to be"
                " repeating.",
            )
        ),
        H.para(
            wrap_hebrew_runs(
                f"The Decalogue's own Exodus 20:10 לא־תעשה has a {ROM_MUNAX} on each atom, but"
                " that is the two strands tangled together rather than either one of them:"
                f" untangled, MAM's טעם {ELYON} has no maqaf, and לא and תעשה are two chanted"
                f" words, each with a {ROM_MUNAX} of its own — the very two atoms Koren has as"
                " one maqaf compound."
            )
        ),
        H.heading_level_3("The nearest thing in a printed edition"),
        H.para(
            (
                *wrap_hebrew_runs(
                    "None of the printed editions transcribed for these pages has the shape"
                    " either. The nearest is the "
                ),
                link("Simanim Tiqqun", "printed-decalogue-simanim.html"),
                *wrap_hebrew_runs(
                    f"'s {ROM_MUNAX} on the joined לא of לא־יהיה and of לא־תעשה — the same"
                    " phenomenon, a non-final atom keeping its accent, one step short of the"
                    " same shape, and in this very passage."
                ),
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
            "The poetic system is a different matter, and different enough that the same"
            " count would not mean the same thing there. It puts two marks on one chanted"
            " word readily and systematically (Breuer, Chapter 9 §§20–26), where the prose"
            " system does so rarely and only within the closed list above. And many of its"
            " maqafs are not written at all: Breuer (§§27, 37) records that in poetic verses"
            " the maqaf after a secondary mark is customarily left unwritten while the atom"
            " still counts as joined, so a survey that finds compounds by looking for a"
            f" written maqaf reaches only part of what is there. MAM's poetic verses have"
            f" {hits} cases by that measure, and MAM has the other part of the measure too:"
            f" it supplies {_gray(survey)} gray maqafs, its own mark for a maqaf the"
            " manuscript leaves unwritten where the chanted word needs one. Of those,"
            f" {_gray(survey, mpa.GRAY_KIND_SECOND)} join an atom that has an accent"
            " alongside the compound's own; the other"
            f" {_gray(survey, mpa.GRAY_KIND_SPREAD)} have one accent written across the two"
            " atoms. Neither figure belongs beside the prose one."
        ),
    )


def render_body_contents(survey: dict) -> tuple[object, ...]:
    pin_claims(survey)
    sections: list[object] = [
        *_intro(survey),
        *_what_is_counted(),
        *_corpus_caveat(),
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
