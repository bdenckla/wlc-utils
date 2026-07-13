r"""Shared computation for the two printed-Decalogue pages: the four cantillation strands
of the Exodus Decalogue's opening אנכי...עבדים unit, resolved live from the vendored data.

This module is pure computation -- no HTML, no display/editorial vocabulary in its *return
values* -- so both companion pages can depend on it without either depending on the other:

  * ``printed_decalogue_page`` (issue #52) grammar-checks the printed vs manuscript Decalogue
    accentuations and now also lays out the four strands as a styled range table.
  * ``printed_decalogue_simanim_page`` (issue #62) documents Simanim's Tiqqun as an independent
    printed-tradition witness and links back to the four-strands table on the main page.

Each of the four Exodus readings (m-trad / p-trad x taḥton / elyon) is read from
``in/accgram/printed_decalogue_teamim.json`` (Hebrew Wikisource data): its first chanted verse
is pulled from the data, and the accent on אנכי (first word) and עבדים is derived from the marks,
so the strands can never drift from the data.  ``resolve_readings`` pins each derivation against
``READING_SPECS`` / ``STRUCTURE`` and raises ``AssertionError`` on any divergence -- this
build-fails-on-data-drift behavior fires at page-1 generation and in the tests, and must never be
softened to a warning.

Editorial / style conventions for the rendered prose on BOTH pages (agreed with Ben; keep them
when editing either page):

* **The two chant-strands are named in Hebrew letters -- תחתון / עליון -- NEVER transliterated
  and NEVER translated.**  No "taḥton"/"elyon" and no "upper"/"lower" in the output: the
  upper/lower glosses invite confusion with above-letter vs below-letter accents, which is *not*
  what the names mean, and for a reader who doesn't know the terms no gloss beats a misleading
  one.  The full ``טעם תחתון`` / ``טעם עליון`` appears ONLY at first mention; everywhere after,
  drop the טעם -- bare עליון is read as "the [טעם] עליון".  The romanized "taḥton"/"elyon" survive
  only as *internal keys* (``READING_SPECS`` / ``STRUCTURE`` names) and inside ``title`` / ``alt``
  attributes; render via the ``TAHTON`` / ``ELYON`` string constants (or ``render_reading_name``).
  Verbatim quoted source Hebrew (e.g. ``בלא טעם עליון``) keeps whatever it says.  This is a
  cross-repo rule (cf. MAM-basics ``py/versification_and_cantillation/doc.py``).
* Prefer "**cantillation**" to "accentuation".
* **Accent/mark romanizations are single-sourced as ``ROM_*`` constants** (pashta, tipeḥa,
  etnaḥta, revia, silluq, sof pasuq, meteg, maqaf, legarmeh, + a few compounds).  They are shared
  by the ``_ACCENT_NAMES`` derivation table, the ``READING_SPECS`` expected-accent pins, and the
  prose of both pages -- so a printed name can't drift from the derived one.  Don't retype these
  spellings inline; ``tests/test_transliterations.py`` guards them tree-wide.  (``_CP_*`` = the
  codepoint constants, distinct from the ``ROM_*`` word forms.)
* Rendered prose uses the **real Unicode em dash** ``—`` (U+2014), not ASCII ``--`` (``--`` is
  fine in code/comments/docstrings, like this one).
* **Image ``alt`` text keeps romanized names** ("taḥton") on purpose -- don't mix alphabets in
  an alt attribute.

Tested by ``tests/test_printed_decalogue_simanim.py`` and ``tests/test_printed_decalogue_page.py``
(plus the tree-wide ``tests/test_transliterations.py``).
"""

from __future__ import annotations

from accgram import printed_decalogue as pd
from accgram.uni_to_marks import is_base_letter

# Codepoints of the two marks we detect by presence (not by the _ACCENT_NAMES table).
_CP_SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
_CP_METEG = "\N{HEBREW POINT METEG}"

# Romanized accent/mark names -- the single spelling used everywhere on both pages, so a name
# can neither drift nor be retyped.  Referenced both by _ACCENT_NAMES (the codepoint->name
# derivation table) and by the rendered prose of both pages; the tree-wide transliteration
# denylist (tests/test_transliterations.py) still enforces the spelling of the literals here.
# The x-form romanizations of the sound ח are written with precomposed h-with-dot-below U+1E25.
ROM_PASHTA = "pashta"
ROM_TIPEHA = "tipeḥa"
ROM_ETNAHTA = "etnaḥta"
ROM_REVIA = "revia"
ROM_SILLUQ = "silluq"
ROM_SOF_PASUQ = "sof pasuq"
ROM_METEG = "meteg"
ROM_MAQAF = "maqaf"
ROM_LEGARMEH = "legarmeh"

# Compound readings that recur verbatim in the prose (U+2026 ellipsis / U+2013 en dash between).
ROM_PASHTA_ETNAHTA = f"{ROM_PASHTA}…{ROM_ETNAHTA}"  # the merged manuscript תחתון
ROM_TIPEHA_ETNAHTA = f"{ROM_TIPEHA}–{ROM_ETNAHTA}"  # the ordinary/printed תחתון opening
ROM_TIPEHA_SILLUQ = (
    f"{ROM_TIPEHA}…{ROM_SILLUQ}"  # the manuscript עליון (standalone verse)
)
ROM_SILLUQ_SOF_PASUQ = f"{ROM_SILLUQ} + {ROM_SOF_PASUQ}"  # the standalone-verse close

# The accent codepoints that fall on the two boundary words of the first Decalogue unit,
# mapped to the romanizations above.  U+05BD (meteg/silluq) is deliberately absent: it is not a
# cantillation accent, and is resolved to silluq only in verse-final position (see ``_accent_of``
# and CLAUDE.md on meteg-vs-silluq).
_ACCENT_NAMES: dict[str, str] = {
    "\N{HEBREW ACCENT PASHTA}": ROM_PASHTA,
    "\N{HEBREW ACCENT TIPEHA}": ROM_TIPEHA,
    "\N{HEBREW ACCENT ETNAHTA}": ROM_ETNAHTA,
    "\N{HEBREW ACCENT REVIA}": ROM_REVIA,
}

# The base-letter skeleton of the word עבדים -- the closing word of the first Decalogue unit,
# located within each reading's first chanted verse by matching its consonants (it sits
# mid-verse in the merged readings, verse-finally where אנכי…עבדים is its own verse).
AVADIM = "עבדים"


# The two chant-strands (טעם) are named in Hebrew letters throughout the rendered prose --
# תחתון / עליון -- and are NEITHER transliterated NOR translated (see the module docstring).
# The romanized forms "taxton"/"elyon" survive only as internal keys (``READING_SPECS`` /
# ``STRUCTURE`` names).  The two strand words are plain Hebrew string constants, substituted
# directly into the prose (including inside f-strings) rather than wrapped in a lang="he" <span>.
TAHTON = "תחתון"
ELYON = "עליון"
_STRAND_HEB: dict[str, str] = {"taḥton": TAHTON, "elyon": ELYON}


def render_reading_name(name: str) -> tuple[object, ...]:
    """A reading name like ``"m-trad taḥton"`` rendered with its strand word in Hebrew
    letters: ``("m-trad ", "תחתון")``.  The tradition half stays English."""
    tradition, strand = name.split()
    return (tradition + " ", _STRAND_HEB[strand])


# --------------------------------------------------------------------------- #
# Deriving the four readings live from the vendored data
# --------------------------------------------------------------------------- #
def base_skeleton(word: str) -> str:
    return "".join(ch for ch in word if is_base_letter(ch))


def _accent_of(word: str) -> str:
    """The cantillation accent on one pointed word, as a romanized name derived from its marks.

    A word carries at most one of the boundary accents we care about.  U+05BD is not a
    cantillation accent, but the same glyph functions as *silluq* on the verse-final word
    (the one carrying *sof pasuq*); so a sof-pasuq word whose only accent-like mark is U+05BD
    is reported as silluq.  Never called on a non-verse-final U+05BD (that is an ordinary
    meteg -- see CLAUDE.md)."""
    for ch in word:
        name = _ACCENT_NAMES.get(ch)
        if name is not None:
            return name
    if _CP_SOF_PASUQ in word and _CP_METEG in word:
        return ROM_SILLUQ
    raise ValueError(f"no recognized boundary accent on {word!r}")


def _find_word(words: tuple[str, ...], skeleton: str) -> str:
    for word in words:
        if base_skeleton(word) == skeleton:
            return word
    raise ValueError(f"no word with skeleton {skeleton!r} in {words!r}")


class Reading:
    """One of the four ways the opening Decalogue unit is accented, resolved from the data."""

    def __init__(self, name: str, vr: pd.VersionResult):
        first = vr.chanted_verses[0]
        self.name = name  # romanized, e.g. "m-trad taxton"
        # The whole first chanted verse's word tuple, so page 1's range cells can read
        # first / mid (עבדים) / last words directly off the data.
        self.first_verse_words = first.words
        self.anokhi_word = first.words[0]
        self.avadim_word = _find_word(first.words, AVADIM)
        self.anokhi_accent = _accent_of(self.anokhi_word)
        self.avadim_accent = _accent_of(self.avadim_word)
        # How many chanted verses this strand splits the Exodus Decalogue into, and the
        # consonantal skeleton of its first chanted verse's last word (its span endpoint).
        self.n_verses = len(vr.chanted_verses)
        self.first_verse_end = base_skeleton(first.words[-1])


# (display name, ex reading, ex data-tradition, expected אנכי, expected עבדים) -- the expected
# accents pin the live derivation so a data change that moved a boundary accent would fail the
# build rather than silently mis-render.  The first verse's span + verse count are pinned
# separately in STRUCTURE; display extras live in the table renderers, keyed by name.
#
# NB: the third element is the DATA lookup key (matched against vr.tradition in resolve_readings),
# which the source emits as "manuscript"/"printed" -- NOT the "m-trad"/"p-trad" display shorthand.
# Keep it in the source's spelling; only the display name (first element) uses the shorthand.
READING_SPECS = (
    ("m-trad taḥton", "taxton", "manuscript", ROM_PASHTA, ROM_ETNAHTA),
    ("m-trad elyon", "elyon", "manuscript", ROM_TIPEHA, ROM_SILLUQ),
    ("p-trad taḥton", "taxton", "printed", ROM_TIPEHA, ROM_SILLUQ),
    ("p-trad elyon", "elyon", "printed", ROM_PASHTA, ROM_REVIA),
)

# Per-strand opening structure: (first-verse span as short right-to-left notation, the
# consonantal skeleton of that first verse's last word, the number of chanted verses the
# strand divides the Exodus Decalogue into).  ``end_skel`` and ``n_verses`` are pinned
# against the vendored data in resolve_readings so a moved boundary fails the build rather
# than silently mislabelling.  (span endpoints from the data: אנכי…על־פני / …עבדים / …מצותי.)
STRUCTURE: dict[str, tuple[str, str, int]] = {
    "m-trad taḥton": ("אנכי…פני", "עלפני", 12),
    "m-trad elyon": ("אנכי…עבדים", "עבדים", 10),
    "p-trad taḥton": ("אנכי…עבדים", "עבדים", 13),
    "p-trad elyon": ("אנכי…מצותי", "מצותי", 9),
}


def resolve_readings(results: list[pd.VersionResult]) -> list[Reading]:
    by_key = {(vr.book, vr.reading, vr.tradition): vr for vr in results}
    readings: list[Reading] = []
    for name, reading, tradition, exp_anokhi, exp_avadim in READING_SPECS:
        r = Reading(name, by_key[("ex", reading, tradition)])
        if (r.anokhi_accent, r.avadim_accent) != (exp_anokhi, exp_avadim):
            raise AssertionError(
                f"{name}: derived ({r.anokhi_accent}, {r.avadim_accent}) from the data, "
                f"expected ({exp_anokhi}, {exp_avadim}) -- the vendored readings drifted"
            )
        _, end_skel, n_verses = STRUCTURE[name]
        if (r.first_verse_end, r.n_verses) != (end_skel, n_verses):
            raise AssertionError(
                f"{name}: derived first-verse end {r.first_verse_end!r} / {r.n_verses} verses "
                f"from the data, expected {end_skel!r} / {n_verses} -- the vendored readings drifted"
            )
        readings.append(r)
    return readings
