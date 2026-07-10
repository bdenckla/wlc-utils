r"""Generate gh-pages/accgram/printed-decalogue-simanim.html -- does Simanim's Tiqqun follow
the printed or the manuscript Decalogue tradition?  Answer: the printed tradition (issue #62).

Companion to ``printed_decalogue_page`` (issue #52, which grammar-checks the printed vs
manuscript Decalogue accentuations).  This page ports two research notes -- formerly issue
#56 comments -- into a versioned, reviewable document:

  * **p. 83** (main-text, *elyon*): Simanim's marginal note on the Exodus (Yitro) Decalogue
    first unit אנכי...עבדים.  Its default (בפנים) elyon reading ends that unit on a *revia*
    (the merged, 9-verse printed structure); "some books" instead give אנכי...עבדים its own
    verse (silluq + *sof pasuq* at עבדים) to keep ten dibrot.
  * **p. 246** (appendix, *taḥton*): the mirror note, contrasting בטעם רגיל (= printed
    taḥton: אנכי...עבדים as its own verse, *sof pasuq* at עבדים) with כתר אר״ץ (= manuscript
    taḥton: pashta...etnaḥta, merged).

What actually establishes the answer is not these notes but Simanim's *body text*: its main
text (p. 83) and appendix Decalogue (p. 246) are compared, by the author, against what Hebrew
Wikisource records as the printed tradition, and they match.  That body text is asserted here,
not reproduced.  The two marginal notes are secondary -- kept for the more-for-fun question of
how aware Simanim is of having made the older, printed-tradition choice.

The two Simanim *transcriptions* are the only hand-set Hebrew, double-checked against the
committed scans.  The shared **four-readings** table is sourced live from the vendored
``in/accgram/printed_decalogue_teamim.json`` (Hebrew Wikisource data) -- each Exodus reading's
first chanted verse is read from the data and the accent on אנכי (first word) and עבדים is
derived from its marks, so the table can never drift from the data.

Editorial / style conventions for the rendered prose (agreed with Ben; keep them when editing):

* **The two chant-strands are named in Hebrew letters -- תחתון / עליון -- NEVER transliterated
  and NEVER translated.**  No "taḥton"/"elyon" and no "upper"/"lower" in the output: the
  upper/lower glosses invite confusion with above-letter vs below-letter accents, which is *not*
  what the names mean, and for a reader who doesn't know the terms no gloss beats a misleading
  one.  The full ``טעם תחתון`` / ``טעם עליון`` appears ONLY at first mention (the intro
  paragraph); everywhere after, drop the טעם -- bare עליון is read as "the [טעם] עליון".  The
  romanized "taḥton"/"elyon" survive only as *internal keys* (``_READING_SPECS`` names,
  ``_STRAND_LETTER``, ``_structure_content`` dispatch); render via the ``_TAHTON`` / ``_ELYON``
  string constants (or ``_render_reading_name()``).  Verbatim quoted source Hebrew (e.g.
  ``בלא טעם עליון``) keeps
  whatever it says.  This is a cross-repo rule (cf. MAM-basics
  ``py/versification_and_cantillation/doc.py``).
* Prefer "**cantillation**" to "accentuation".
* **Accent/mark romanizations are single-sourced as ``_ROM_*`` constants** (pashta, tipeḥa,
  etnaḥta, revia, silluq, sof pasuq, meteg, maqaf, legarmeh, + a few compounds).  They are shared
  by the ``_ACCENT_NAMES`` derivation table, the ``_READING_SPECS`` expected-accent pins, and the
  prose -- so a printed name can't drift from the derived one.  Don't retype these spellings
  inline; ``tests/test_transliterations.py`` guards them tree-wide.  (``_CP_*`` = the codepoint
  constants, distinct from the ``_ROM_*`` word forms.)
* Rendered prose uses the **real Unicode em dash** ``—`` (U+2014), not ASCII ``--`` (``--`` is
  fine in code/comments/docstrings, like this one).
* **Image ``alt`` text keeps romanized names** ("taḥton") on purpose -- don't mix alphabets in
  an alt attribute.

Regenerate with ``main_accgram.py generate-html``; test with
``tests/test_printed_decalogue_simanim.py`` (plus the tree-wide
``tests/test_transliterations.py``).  A running edit log lives in the gitignored
``.novc/pending_simanim_page_edits.md``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import rtms_report
from accgram.almost_errors_html_shared import hbo, link
from accgram.uni_to_marks import is_base_letter
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance

from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "Simanim's Tiqqun follows the printed tradition for the Decalogues"

# _ISSUE_52 = "https://github.com/bdenckla/wlc-utils/issues/52"
# _ISSUE_56 = "https://github.com/bdenckla/wlc-utils/issues/56"
_PRINTED_DECALOGUE_PAGE = "printed-decalogue.html"
_P83_IMG = "img/simanim-decalogue-p83.png"
_P246_IMG = "img/simanim-decalogue-p246.png"

# Codepoints of the two marks we detect by presence (not by the _ACCENT_NAMES table).
_CP_SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
_CP_METEG = "\N{HEBREW POINT METEG}"

# Romanized accent/mark names -- the single spelling used everywhere on this page, so a name
# can neither drift nor be retyped.  Referenced both by _ACCENT_NAMES (the codepoint->name
# derivation table) and by the rendered prose below; the tree-wide transliteration denylist
# (tests/test_transliterations.py) still enforces the spelling of the literals here.  The x-form
# romanizations of the sound ח are written with precomposed h-with-dot-below U+1E25 (ḥ).
_ROM_PASHTA = "pashta"
_ROM_TIPEHA = "tipeḥa"
_ROM_ETNAHTA = "etnaḥta"
_ROM_REVIA = "revia"
_ROM_SILLUQ = "silluq"
_ROM_SOF_PASUQ = "sof pasuq"
_ROM_METEG = "meteg"
_ROM_MAQAF = "maqaf"
_ROM_LEGARMEH = "legarmeh"

# Compound readings that recur verbatim in the prose (U+2026 ellipsis / U+2013 en dash between).
_ROM_PASHTA_ETNAHTA = f"{_ROM_PASHTA}…{_ROM_ETNAHTA}"  # the merged manuscript תחתון
_ROM_TIPEHA_ETNAHTA = f"{_ROM_TIPEHA}–{_ROM_ETNAHTA}"  # the ordinary/printed תחתון opening
_ROM_TIPEHA_SILLUQ = f"{_ROM_TIPEHA}…{_ROM_SILLUQ}"  # the manuscript עליון (standalone verse)
_ROM_SILLUQ_SOF_PASUQ = f"{_ROM_SILLUQ} + {_ROM_SOF_PASUQ}"  # the standalone-verse close

# The accent codepoints that fall on the two boundary words of the first Decalogue unit,
# mapped to the romanizations above.  U+05BD (meteg/silluq) is deliberately absent: it is not a
# cantillation accent, and is resolved to silluq only in verse-final position (see ``_accent_of``
# and CLAUDE.md on meteg-vs-silluq).
_ACCENT_NAMES: dict[str, str] = {
    "\N{HEBREW ACCENT PASHTA}": _ROM_PASHTA,
    "\N{HEBREW ACCENT TIPEHA}": _ROM_TIPEHA,
    "\N{HEBREW ACCENT ETNAHTA}": _ROM_ETNAHTA,
    "\N{HEBREW ACCENT REVIA}": _ROM_REVIA,
}

# The base-letter skeleton of the word עבדים -- the closing word of the first Decalogue unit,
# located within each reading's first chanted verse by matching its consonants (it sits
# mid-verse in the merged readings, verse-finally where אנכי…עבדים is its own verse).
_AVADIM = "עבדים"


def _path(path: str) -> object:
    """A repo path as plain body text (no monospace <code>, whose optical size clashes with
    the surrounding font) that may still line-break after each slash (issue #62)."""
    contents: list[object] = []
    for i, part in enumerate(path.split("/")):
        if i:
            contents += ["/", H.word_break_opportunity()]
        contents.append(part)
    return H.span(tuple(contents))


# The two chant-strands (טעם) are named in Hebrew letters throughout the rendered prose --
# תחתון / עליון -- and are NEITHER transliterated NOR translated.  No "upper"/"lower": those
# English glosses invite confusion with above-letter / below-letter accents, which is not what
# עליון / תחתון mean; per Ben, an English reader is better off not being handed a misleading
# meaning at all.  The romanized forms "taḥton"/"elyon" survive only as internal keys
# (``_READING_SPECS`` names, ``_STRAND_LETTER``, ``_structure_content`` dispatch).  We also
# prefer "cantillation" to "accentuation".  After a strand is first named as its full טעם (e.g.
# "the טעם עליון"), later mentions drop the טעם: bare עליון is understood as "the [טעם] עליון".
# The two strand words are plain Hebrew string constants, substituted directly into the prose
# (including inside f-strings) rather than wrapped in a lang="he" <span>.
_TAHTON = "תחתון"
_ELYON = "עליון"
_STRAND_HEB: dict[str, str] = {"taḥton": _TAHTON, "elyon": _ELYON}


def _render_reading_name(name: str) -> tuple[object, ...]:
    """A reading name like ``"manuscript taḥton"`` rendered with its strand word in Hebrew
    letters: ``("manuscript ", "תחתון")``.  The tradition half stays English."""
    tradition, strand = name.split()
    return (tradition + " ", _STRAND_HEB[strand])


# --------------------------------------------------------------------------- #
# Deriving the four readings live from the vendored data
# --------------------------------------------------------------------------- #
def _base_skeleton(word: str) -> str:
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
        return _ROM_SILLUQ
    raise ValueError(f"no recognized boundary accent on {word!r}")


def _find_word(words: tuple[str, ...], skeleton: str) -> str:
    for word in words:
        if _base_skeleton(word) == skeleton:
            return word
    raise ValueError(f"no word with skeleton {skeleton!r} in {words!r}")


class _Reading:
    """One of the four ways the opening Decalogue unit is accented, resolved from the data."""

    def __init__(self, name: str, vr: pd.VersionResult):
        first = vr.chanted_verses[0]
        self.name = name  # romanized, e.g. "manuscript taxton"
        self.anokhi_word = first.words[0]
        self.avadim_word = _find_word(first.words, _AVADIM)
        self.anokhi_accent = _accent_of(self.anokhi_word)
        self.avadim_accent = _accent_of(self.avadim_word)


# (display name, ex reading, ex data-tradition, expected אנכי, expected עבדים) -- the expected
# accents pin the live derivation so a data change that moved a boundary accent would fail the
# build rather than silently mis-render.  Display extras (MAM strand letter, structure blurb)
# live in the table renderer, keyed by name.
#
# NB: the third element is the DATA lookup key (matched against vr.tradition in _resolve_readings),
# which the source emits as "manuscript"/"printed" -- NOT the "m-trad"/"p-trad" display shorthand.
# Keep it in the source's spelling; only the display name (first element) uses the shorthand.
_READING_SPECS = (
    ("m-trad taḥton", "taxton", "manuscript", _ROM_PASHTA, _ROM_ETNAHTA),
    ("m-trad elyon", "elyon", "manuscript", _ROM_TIPEHA, _ROM_SILLUQ),
    ("p-trad taḥton", "taxton", "printed", _ROM_TIPEHA, _ROM_SILLUQ),
    ("p-trad elyon", "elyon", "printed", _ROM_PASHTA, _ROM_REVIA),
)


def _resolve_readings(results: list[pd.VersionResult]) -> list[_Reading]:
    by_key = {(vr.book, vr.reading, vr.tradition): vr for vr in results}
    readings: list[_Reading] = []
    for name, reading, tradition, exp_anokhi, exp_avadim in _READING_SPECS:
        r = _Reading(name, by_key[("ex", reading, tradition)])
        if (r.anokhi_accent, r.avadim_accent) != (exp_anokhi, exp_avadim):
            raise AssertionError(
                f"{name}: derived ({r.anokhi_accent}, {r.avadim_accent}) from the data, "
                f"expected ({exp_anokhi}, {exp_avadim}) -- the vendored readings drifted"
            )
        readings.append(r)
    return readings


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _display_accent(name: str) -> str:
    return f"{_ROM_SILLUQ} / {_ROM_SOF_PASUQ}" if name == _ROM_SILLUQ else name


def _word_cell(word: str, accent: str) -> object:
    return H.table_datum((hbo(word), H.line_break(), H.small(f"({_display_accent(accent)})")))


_PARA_1 = (
    "Each Decalogue — the one in",
    *[" ", H.bold("Exodus"), " and the one in ", H.bold("Deuteronomy")],
    " — has two strands of cantillation, the",
    *[" ", "טעם תחתון", " and the ", "טעם עליון", "."],
    " Each strand (of the Exodus Decalogue, for example)",
    " varies not only in where it puts chanted verse boundaries,",
    " but also in how many such boundaries there are.",
    " Adding to these complexities, in truth there are",
    *[" ", H.bold("four"), " strands,"],
    " because at the opening commandment the",
    *[" ", H.bold("printed tradition")," (p-trad)"],
    " differs from the",
    *[" ", H.bold("manuscript tradition"), " (m-trad),"],
    f" yielding two different {_ELYON} strands",
    f" and two different {_TAHTON} strands.",
    *[" ", link("The companion page", _PRINTED_DECALOGUE_PAGE)],
    " grammar-checks all p-trad readings; this page serves to document the claim that",
    *[" ", H.bold("Simanim's Tiqqun"), " follows the p-trad."],
    " Along the way, this page transcribes two of Simanim's marginal notes ",
    " — not to document the claim, but to document "
    "how conscious Simanim is of the choice it makes.",
)


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.para(_PARA_1),
        H.para(
            (
                "Simanim's Tiqqun follows the p-trad for the Decalogues. In its ",
                H.bold("Exodus"),
                " (Yitro) Decalogue, Simanim's main text (p. 83) is the p-trad ",
                _ELYON,
                " and its appendix (p. 246) is the p-trad ",
                _TAHTON,
                " — both differing from the m-trad only at this first commandment "
                "(the אנכי…עבדים unit). Since no digital Simanim exists, I established "
                "this by visually spot-checking Simanim against Hebrew Wikisource's "
                "p-trad. I have not reproduced Simanim's body text here — you'll just "
                "have to take it on my word.",
            )
        ),
        H.para(
            (
                "Two of Simanim's marginal notes are transcribed "
                "further down. They are ",
                H.bold("not"),
                " what establishes the finding (the body text is); they are worth reading"
                " to get a sense of how conscious Simanim is of having made their choice "
                "of the p-trad.",
            )
        ),
    )


# Per-reading display extras.  The reading name's strand word renders in Hebrew letters (see
# _render_reading_name); the MAM strand letter and the structure blurbs mix English with the
# odd Hebrew word, wrapped individually.  _STRAND_LETTER's keys are the internal romanized
# reading names (matched against r.name), not display text.
_STRAND_LETTER: dict[str, str] = {"m-trad taḥton": "א", "m-trad elyon": "ב"}


def _structure_content(name: str) -> tuple[object, ...]:
    if name == "m-trad taḥton":
        return ("merges ", "אנכי…פני", " into one verse")
    if name == "m-trad elyon":
        return ("אנכי…עבדים", " its own verse → 10 verses")
    if name == "p-trad taḥton":
        return ("אנכי…עבדים", " its own verse (= m-trad ", _ELYON, ")")
    return ("merges commandments I + II → 9 verses",)


def _reading_label(r: _Reading) -> tuple[object, ...]:
    letter = _STRAND_LETTER.get(r.name)
    base = _render_reading_name(r.name)
    if letter:
        return (*base, " ", H.small(("MAM ", letter)))
    return base


def _four_readings_table(readings: list[_Reading]) -> object:
    header = H.table_row_of_headers(
        ("reading", "אנכי", "עבדים", "structure")
    )
    rows = [header]
    for r in readings:
        rows.append(
            H.table_row(
                (
                    H.table_header(_reading_label(r)),
                    _word_cell(r.anokhi_word, r.anokhi_accent),
                    _word_cell(r.avadim_word, r.avadim_accent),
                    H.table_datum(_structure_content(r.name)),
                )
            )
        )
    return H.table(tuple(rows), {"class": "printed-decalogue-verdict"})


def _four_readings_section(readings: list[_Reading]) -> tuple[object, ...]:
    return (
        H.heading_level_2("The four readings of אנכי…עבדים"),
        H.para(
            (
                "The m-trad and the p-trad accent the Decalogue's אנכי…עבדים unit ",
                "differently, and the two ",
                "טעמים",
                " are effectively reassigned by one notch at the first commandment. Reading "
                "each Exodus version's first chanted verse straight from the vendored data and "
                "deriving the accent on its first word (",
                "אנכי",
                ") and on ",
                "עבדים",
                ". The accent on ",
                "עבדים",
                " is what decides the structure: a ",
                H.bold(_ROM_SILLUQ_SOF_PASUQ),
                " there ends the verse, so ",
                "אנכי…עבדים",
                " stands as its own verse; an ",
                H.bold(_ROM_ETNAHTA),
                " or ",
                H.bold(_ROM_REVIA),
                " there is mid-verse, folding ",
                "אנכי…עבדים",
                " into a longer verse.",
            )
        ),
        _four_readings_table(readings),
        H.unordered_list(
            (
                (
                    H.bold(("Printed ", _TAHTON, " = m-trad ", _ELYON, ".")),
                    " Once ",
                    "אנכי…עבדים",
                    " is its own verse there is only one grammatical way to accent it — ",
                    _ROM_ETNAHTA,
                    " in the middle, ",
                    _ROM_SILLUQ,
                    " at the end — so both traditions land on the same marks (consonants, "
                    "accents, and accent-boundary marks: ",
                    _ROM_SOF_PASUQ,
                    ", ",
                    _ROM_MAQAF,
                    ", ",
                    _ROM_LEGARMEH,
                    "). They differ only by an immaterial ",
                    _ROM_METEG,
                    ".",
                ),
                (
                    H.bold(("Printed ", _ELYON, " ≠ m-trad ", _ELYON, ".")),
                    " The p-trad ",
                    _ELYON,
                    " puts ",
                    H.bold(_ROM_REVIA),
                    " on ",
                    "עבדים",
                    " and runs the first two commandments together into one verse (→ ",
                    H.bold("9"),
                    " total), where the m-trad ",
                    _ELYON,
                    " closes on ",
                    _ROM_SILLUQ,
                    " (→ ",
                    H.bold("10"),
                    ").",
                ),
                (
                    "The m-trad ",
                    _TAHTON,
                    " does not give ",
                    "אנכי…עבדים",
                    " its own verse either — it runs ",
                    "אנכי…פני",
                    " together (",
                    _ROM_ETNAHTA,
                    " at ",
                    "עבדים",
                    ", ",
                    _ROM_SOF_PASUQ,
                    " at ",
                    "פני",
                    "), a third structure again.",
                ),
            )
        ),
    )


def _figure(src: str, alt: str, caption: str, *, width: str | None) -> object:
    img_attr = {"src": src, "alt": alt}
    img_attr["style"] = "max-width: 100%; height: auto;"
    if width:
        img_attr["width"] = width
    return H.figure((H.img(img_attr), H.figcaption(caption)))


def _lines_with_breaks(lines: tuple[str, ...]) -> tuple[object, ...]:
    """Interleave ``<br>`` between transcription lines (they follow the scan's own breaks)."""
    body: list[object] = []
    for i, line in enumerate(lines):
        if i:
            body.append(H.line_break())
        body.append(line)
    return tuple(body)


# The p. 83 transcription, following the scan's own line breaks (the pointed example verse
# אנכי…עבדים is hand-set Hebrew, checked against the committed scan).
_P83_LINES = (
    "[ב] פסוק ראשון נהגו",
    "לקרותו כשמסיים",
    "ברביע כמובא בפנים,",
    "יש ספרים שנקרא כמו",
    "בטעם תחתון, כיון שע״פ",
    "המסורה צ״ל כאן יו׳ד",
    "דברות, כך: אָֽנֹכִ֖י יְהֹוָ֣ה",
    "אֱלֹהֶ֑יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ",
    "מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֥ית",
    "עֲבָדִֽים׃ [עשרת הדברות",
    "בלא טעם עליון בסוף",
    "החומש].",
)


def _p83_scan_and_transcription() -> object:
    """Scan and transcription side by side, as in the original issue-#56 comment: a two-column
    table with the source scan on the left and the RTL transcription (following the scan's own
    line breaks) on the right."""
    img = H.img(
        {
            "src": _P83_IMG,
            "alt": "Simanim Tiqqun p. 83: marginal note on the Exodus Decalogue’s אנכי…עבדים unit",
            "style": "max-width: 100%; height: auto;",
            "width": "275",
        }
    )
    header = H.table_row_of_headers(("Source scan", "Transcription"))
    body = H.table_row(
        (
            H.table_datum(img, {"style": "vertical-align: top"}),
            H.table_datum(
                _lines_with_breaks(_P83_LINES),
                {"style": "vertical-align: top", "dir": "rtl", "lang": "hbo"},
            ),
        )
    )
    return H.table((header, body), {"class": "simanim-scan-transcription"})


def _p83_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Main-text (עליון) note — Simanim p. 83"),
        H.para(
            (
                "A note in the margin of the Exodus (Yitro) Decalogue, on ",
                "אנכי…עבדים",
                ".",
            )
        ),
        _p83_scan_and_transcription(),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                H.bold("[ב]"),
                " {Regarding} the first verse — it is the custom of some to chant it as ",
                H.bold(("ending on a ", _ROM_REVIA)),
                ", as given in the main text (",
                "בפנים",
                "); {but} there are editions that call for it to be chanted as in the ",
                _TAHTON,
                " {i.e. giving ",
                "אנכי…עבדים",
                " its own verse — see the four readings above}, since by the Masorah there must "
                "be Ten "
                "Commandments here — thus: {",
                "אנכי…עבדים",
                " as its own verse, shown above, with ",
                _ROM_SILLUQ_SOF_PASUQ,
                " at ",
                "עבדים",
                "}. [The Ten Commandments without the ",
                _ELYON,
                " appear at the end of the Ḥumash.]",
            )
        ),
        H.para(
            (
                H.small(
                    (
                        H.bold("Notation:"),
                        " text in ",
                        H.bold("{curly braces}"),
                        " is our editorial addition; ",
                        H.bold("[square brackets]"),
                        " reproduce brackets present in the source itself.",
                    )
                ),
            )
        ),
        H.para(
            (
                "The note is worth reading for what it reveals about Simanim's own stance: its ",
                H.bold("default"),
                " (",
                "בפנים",
                ") ",
                _ELYON,
                " reading ends the אנכי…עבדים unit on a ",
                H.bold(_ROM_REVIA),
                " — the merged, nine-verse p-trad structure — and it files the standalone, "
                "ten-dibrot reading (",
                _ROM_SILLUQ_SOF_PASUQ,
                " at ",
                "עבדים",
                ") under what merely “some books” do. So Simanim treats the p-trad structure "
                "as the norm and the m-trad alternative as the deviation — aware of "
                "the alternative, but not adopting it.",
            )
        ),
    )


def _p246_transcription() -> object:
    lemma = "אָֽנֹכִ֖י* יְיָ֣ אֱלֹהֶ֑יךָ"
    body = (
        " וגו׳ כך היא הגרסה בטעם רגיל שפותח בטפחה אתנחתא ומסיים תיבת בסו״פ עֲבָדִים: "
        "ובכתר אר״ץ פותח בפשטא ומסיים באתנחתא, כך: אָֽנֹכִי֙ יְהֹוָ֣ה אֱלֹהֶ֔יךָ אֲשֶׁ֧ר "
        "הֽוֹצֵאתִ֛יךָ מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֣ית עֲבָדִ֑ים. ולגבי “עשרת הדברות” "
        "בטעם עליון בתוך החומש:"
    )
    return H.blockquote(
        (
            H.span_c(lemma, "simanim-lemma"),
            body,
        ),
        {"dir": "rtl", "lang": "hbo"},
    )


def _p246_mapping_table() -> object:
    header = H.table_row_of_headers(
        ("the note's label", "אנכי", "עבדים", "= four-readings row")
    )
    ragil = H.table_row(
        (
            H.table_header(("בטעם רגיל", " ", H.small("(ordinary)"))),
            H.table_datum(_ROM_TIPEHA),
            H.table_datum(_ROM_SOF_PASUQ),
            H.table_datum(("printed ", _TAHTON, " = m-trad ", _ELYON)),
        )
    )
    keter = H.table_row(
        (
            H.table_header("כתר אר״ץ"),
            H.table_datum(_ROM_PASHTA),
            H.table_datum(_ROM_ETNAHTA),
            H.table_datum(("m-trad ", _TAHTON, " (MAM ", "א", ")")),
        )
    )
    return H.table((header, ragil, keter), {"class": "printed-decalogue-verdict"})


def _p246_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Appendix (תחתון) note — Simanim p. 246"),
        H.para(
            (
                "The mirror note, from the appendix's ",
                _TAHTON,
                " Decalogue (which Simanim heads only negatively, ",
                "בלא טעם עליון",
                " — lacking the ",
                _ELYON,
                "), on the lemma ",
                "אנכי",
                ".",
            )
        ),
        _figure(
            _P246_IMG,
            "Simanim Tiqqun p. 246: appendix note on the taḥton Decalogue’s אנכי…עבדים unit",
            "Simanim Tiqqun, p. 246 — appendix note contrasting בטעם רגיל and כתר אר״ץ.",
            width=None,
        ),
        H.heading_level_3("Transcription"),
        _p246_transcription(),
        H.para(
            (
                H.small(
                    (
                        "The lemma is shown in blue rather than boldface — bold renders many "
                        "Hebrew fonts' diacritics hard to read, so we substitute colour for the "
                        "source's own emphasis. It reproduces the appendix's own body text, "
                        "asterisk and all, except that the note writes the Tetragrammaton as the "
                        "double-yod ",
                        hbo("יְיָ"),
                        " where the body has ",
                        "יהוה",
                        ".",
                    )
                ),
            )
        ),
        H.para(
            (
                H.small(
                    (
                        "It isn't clear whether the mark after ",
                        "עבדים",
                        " in the transcription is a ",
                        _ROM_SOF_PASUQ,
                        " or a colon; we read it as a colon.",
                    )
                ),
            )
        ),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                "“",
                "אנכי יי אלהיך",
                " …” — Such is the version in the ordinary cantillation, which opens with ",
                H.bold(_ROM_TIPEHA_ETNAHTA),
                " and ends with the verse-final word — at ",
                _ROM_SOF_PASUQ,
                " — ",
                "עבדים",
                "; but in the Keter Aram Tsova it opens with ",
                H.bold(_ROM_PASHTA),
                " and ends with ",
                H.bold(_ROM_ETNAHTA),
                ", thus: {the merged reading ",
                "אנכי…עבדים",
                " shown above}. And as regards the “Ten Commandments” in the ",
                _ELYON,
                " within the [main body of the] Ḥumash: …",
            )
        ),
        H.para(
            (
                H.small(
                    (
                        "On Simanim's citing the ",
                        "כתר אר״ץ",
                        " (Aleppo Codex) here — what that citation can and cannot mean — see ",
                        link("the note below", "#simanim-aleppo-codex"),
                        ".",
                    )
                ),
            )
        ),
        H.heading_level_3("How it maps onto the four readings"),
        H.para(
            (
                "The note contrasts two cantillations of the אנכי…עבדים unit, both already in the "
                "table above:",
            )
        ),
        _p246_mapping_table(),
        H.para(
            (
                "So the note has Simanim, in its own editorial voice, distinguishing two ",
                _TAHTON,
                " cantillations of the אנכי…עבדים unit: what it prints and calls the "
                "“ordinary” (",
                "רגיל",
                ") ",
                _TAHTON,
                " — ",
                "עבדים",
                " carrying ",
                _ROM_SILLUQ_SOF_PASUQ,
                ", ",
                "אנכי…עבדים",
                " as its own verse, its marks identical to the m-trad ",
                _ELYON,
                " — versus the Keter's merged ",
                _ROM_PASHTA_ETNAHTA,
                ", the genuine m-trad ",
                _TAHTON,
                ", which it sets aside. Simanim thus knows the two differ and knowingly prints "
                "the newer one — another glimpse of the same self-awareness as the p. 83 note.",
            )
        ),
    )


def _conclusion() -> tuple[object, ...]:
    return (
        H.heading_level_2("Conclusion", {"id": "simanim-conclusion"}),
        H.para(
            (
                "Simanim's Tiqqun follows the p-trad for the Decalogues, not the m-trad. "
                "The two traditions diverge only at the opening commandment ",
                "אנכי…עבדים",
                ", and Simanim lands on the p-trad side of that divergence on both strands: "
                "the p-trad ",
                _ELYON,
                " in its ",
                H.bold("Exodus"),
                " main text (p. 83), and the p-trad ",
                _TAHTON,
                " in its appendix (p. 246).",
            )
        ),
        H.para(
            (
                "A closing, more-for-fun observation. I find it somewhat ",
                H.bold("editorially inconsistent"),
                " that Simanim — otherwise a modern Tiqqun (from Feldheim) — keeps "
                "p-trad Decalogues, where more recent Bibles have moved toward the "
                "m-trad ",
                _ELYON,
                " and m-trad ",
                _TAHTON,
                ". The two marginal notes above suggest "
                "Simanim was at least half-aware of the tension: each sets its p-trad reading "
                "against the standalone-verse / Keter alternative it declines to follow. "
                "(Straddling old and new is less surprising in a house like Koren, which does it "
                "more pervasively; Simanim's is a milder case.)",
            )
        ),
        H.para(
            (
                "One scope note: I examined only Simanim's ",
                H.bold("Exodus"),
                " (Yitro) Decalogue. The אנכי…עבדים unit ",
                " is textually identical in the ",
                H.bold("Deuteronomy"),
                " (Vaetḥanan) Decalogue, so the same choice between the two cantillations would "
                "apply — but "
                "that Simanim accents its Deuteronomy Decalogue the same way is my assumption, "
                "not something I checked.",
            )
        ),
    )


def _source_section(source: dict) -> tuple[object, ...]:
    prov = source.get("provenance", {})
    oldid = prov.get("oldid")
    ts = prov.get("revision_timestamp", "")
    rev = f" (revision {oldid}, {ts[:10]})" if oldid else ""
    return (
        H.heading_level_2("Source"),
        H.para(
            (
                "The four readings are read live from the vendored Hebrew Wikisource data ",
                _path("in/accgram/printed_decalogue_teamim.json"),
                rev,
                " — each Exodus version's first chanted verse, with the accent on ",
                "אנכי",
                " and ",
                "עבדים",
                " derived from its marks. The two Simanim transcriptions are hand-set from the "
                "committed scans of Simanim's Tiqqun. The four-readings data is credited to "
                "Hebrew Wikisource (",
                "עשרת הדברות בסיס/טעמים",
                "); the transcriptions and scans, to Simanim.",
            )
        ),
    )


def _aleppo_codex_section() -> tuple[object, ...]:
    return (
        H.heading_level_2(
            "On Simanim's citation of the Aleppo Codex", {"id": "simanim-aleppo-codex"}
        ),
        H.para(
            (
                "The p. 246 note cites the ",
                "כתר אר״ץ",
                " (Keter Aram Tsova, the Aleppo Codex) for the merged ",
                _ROM_PASHTA_ETNAHTA,
                " reading. Two things are worth keeping straight about that citation.",
            )
        ),
        H.unordered_list(
            (
                (
                    H.bold(
                        "It names one of the Codex's two Decalogue cantillations, not "
                        "“the” reading."
                    ),
                    " The merged ",
                    _ROM_PASHTA_ETNAHTA,
                    " reading is the m-trad ",
                    _TAHTON,
                    " — one strand. Like the Tiberian manuscripts generally, the Aleppo "
                    "Codex's Decalogue carries ",
                    H.bold("both"),
                    " cantillations; the ",
                    _ELYON,
                    " is the other (",
                    "אנכי…עבדים",
                    " as its own verse, ",
                    _ROM_TIPEHA_SILLUQ,
                    "). Citing the ",
                    _TAHTON,
                    " reading alone does not mean the Codex has only one.",
                ),
                (
                    H.bold("And it is a reconstruction, not an autopsy."),
                    " The Aleppo Codex's Torah survives only from Deut 28:17 onward, so the "
                    "physical Codex contains neither Decalogue; any statement about how "
                    "“the Keter” points ",
                    "אנכי…עבדים",
                    " rests on reconstruction or pre-1947 testimony. Simanim, in a passing "
                    "reference, has no room to say so — but strictly it should read “one of the "
                    "two cantillations reconstructed for the Aleppo Codex is …”.",
                ),
            )
        ),
    )


def render_body_contents(results: list[pd.VersionResult], source: dict) -> tuple[object, ...]:
    readings = _resolve_readings(results)
    return (
        *_intro(),
        *_four_readings_section(readings),
        *_p83_section(),
        *_p246_section(),
        *_conclusion(),
        *_aleppo_codex_section(),
        *_source_section(source),
    )


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue-simanim.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=pd.default_source_path())
    parser.add_argument("--html-out", type=Path, default=default_html_out_path(repo_root))


def run(args: argparse.Namespace) -> None:
    source = pd.load_source(args.source)
    results = pd.check_all(source)

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(results, source),
        write_ctx=H.WriteCtx(
            title=REPORT_TITLE,
            path=str(html_out),
            centered=True,
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    print(f"HTML: {html_out}")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
