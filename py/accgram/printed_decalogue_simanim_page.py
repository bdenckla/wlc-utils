r"""Generate gh-pages/accgram/printed-decalogue-simanim.html -- two marginal notes from
Simanim's Tiqqun that independently witness the printed Decalogue tradition (issue #62).

Companion to ``printed_decalogue_page`` (issue #52, which grammar-checks the printed vs
manuscript Decalogue accentuations).  This page ports two research notes -- formerly issue
#56 comments -- into a versioned, reviewable document:

  * **p. 83** (main-text, *elyon*): Simanim's marginal note on the Exodus (Yitro) Decalogue
    first unit אנכי...עבדים.  Its default (בפנים) elyon reading ends that unit on a *revia*
    (the merged, 9-verse printed structure); "some books" instead give the standalone
    *sof-pasuq* verse to keep ten dibrot.
  * **p. 246** (appendix, *taḥton*): the mirror note, contrasting בטעם רגיל (= printed
    taḥton: standalone, *sof pasuq* at עבדים) with כתר אר״ץ (= manuscript taḥton:
    pashta...etnaḥta, merged).

Together they show Simanim carries the **printed** elyon in its main text and the **printed**
taḥton in its appendix, so the Simanim scans are independent printed-tradition witnesses.

The two Simanim *transcriptions* are the only hand-set Hebrew (they differ from MAM; they are
double-checked against the committed scans).  The shared **four-readings** table is sourced
live from the vendored ``in/accgram/printed_decalogue_teamim.json`` -- each Exodus reading's
first chanted verse is read from the data and the accent on אנכי (first word) and עבדים is
derived from its marks, so the table can never drift from the data.

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import rtms_report
from accgram.almost_errors_html_shared import hbo, link
from accgram.uni_to_marks import is_accent, is_base_letter
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance

from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "Simanim's Tiqqun independently witnesses the printed Decalogue tradition"

_ISSUE_52 = "https://github.com/bdenckla/wlc-utils/issues/52"
_ISSUE_56 = "https://github.com/bdenckla/wlc-utils/issues/56"
_PRINTED_DECALOGUE_PAGE = "printed-decalogue.html"
_P83_IMG = "img/simanim-decalogue-p83.png"
_P246_IMG = "img/simanim-decalogue-p246.png"

_SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"
_METEG = "\N{HEBREW POINT METEG}"

# The accent codepoints that fall on the two boundary words of the first Decalogue unit,
# mapped to the romanizations the issue fixes (etnaxta / tipexa / taxton, spelled in the
# output with the precomposed h-with-dot-below U+1E25).  U+05BD (meteg/silluq) is
# deliberately absent: it is not a cantillation accent, and is resolved to silluq only in
# verse-final position (see ``_accent_of`` and CLAUDE.md on meteg-vs-silluq).
_ACCENT_NAMES: dict[str, str] = {
    "\N{HEBREW ACCENT PASHTA}": "pashta",
    "\N{HEBREW ACCENT TIPEHA}": "tipeḥa",
    "\N{HEBREW ACCENT ETNAHTA}": "etnaḥta",
    "\N{HEBREW ACCENT REVIA}": "revia",
}

# The base-letter skeleton of the word עבדים -- the closing word of the first Decalogue unit,
# located within each reading's first chanted verse by matching its consonants (it sits
# mid-verse in the merged readings, verse-finally in the standalone ones).
_AVADIM = "עבדים"


def _heb(text: str) -> object:
    """Unpointed (consonantal) Hebrew: default font, not the pointed-text font (issue #58)."""
    return H.span(text, {"lang": "he"})


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
    if _SOF_PASUQ in word and _METEG in word:
        return "silluq"
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


# (romanized name, ex reading, ex tradition, expected אנכי, expected עבדים) -- the expected
# accents pin the live derivation so a data change that moved a boundary accent would fail the
# build rather than silently mis-render.  Display extras (MAM strand letter, structure blurb)
# live in the table renderer, keyed by name.
_READING_SPECS = (
    ("manuscript taḥton", "taxton", "manuscript", "pashta", "etnaḥta"),
    ("manuscript elyon", "elyon", "manuscript", "tipeḥa", "silluq"),
    ("printed taḥton", "taxton", "printed", "tipeḥa", "silluq"),
    ("printed elyon", "elyon", "printed", "pashta", "revia"),
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
    return "silluq / sof pasuq" if name == "silluq" else name


def _word_cell(word: str, accent: str) -> object:
    return H.table_datum((hbo(word), H.line_break(), H.small(f"({_display_accent(accent)})")))


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.para(
            (
                "The two Decalogues are each chanted two ways -- the ",
                _heb("טעם תחתון"),
                " (taḥton, ordinary-length verses) and the ",
                _heb("טעם עליון"),
                " (elyon, one verse per commandment) -- and the ",
                H.bold("printed"),
                " editions accent the opening commandment differently from the Tiberian ",
                H.bold("manuscript"),
                ". ",
                link("The companion page", _PRINTED_DECALOGUE_PAGE),
                " (",
                link("issue #52", _ISSUE_52),
                ") grammar-checks all four printed-vs-manuscript readings; this page ports two "
                "marginal notes from ",
                H.bold("Simanim's Tiqqun"),
                " that independently attest which tradition Simanim follows (formerly two "
                "comments on ",
                link("issue #56", _ISSUE_56),
                ").",
            )
        ),
        H.para(
            (
                "The two notes mirror each other. The ",
                H.bold("main-text"),
                " note (p. 83) sits beside the elyon Decalogue and, on its own testimony, "
                "gives the merged nine-verse ",
                H.bold("printed elyon"),
                " as its default; the ",
                H.bold("appendix"),
                " note (p. 246) sits beside the taḥton Decalogue and prints the standalone ",
                H.bold("printed taḥton"),
                ". Each even points at the other. Taken together they show Simanim carrying "
                "the printed tradition on both strands -- so the Simanim scans are independent "
                "printed-tradition witnesses, not merely an echo of MAM's own note.",
            )
        ),
    )


# Per-reading display extras (romanized name is English/LTR; the MAM strand letter and the
# structure blurbs mix English with the odd Hebrew word, wrapped individually).
_STRAND_LETTER: dict[str, str] = {"manuscript taḥton": "א", "manuscript elyon": "ב"}


def _structure_content(name: str) -> tuple[object, ...]:
    if name == "manuscript taḥton":
        return ("merges ", _heb("אנכי…פני"), " into one verse")
    if name == "manuscript elyon":
        return (_heb("אנכי…עבדים"), " standalone → 10 verses")
    if name == "printed taḥton":
        return ("standalone (= manuscript elyon)",)
    return ("merges commandments I + II → 9 verses",)


def _reading_label(r: _Reading) -> tuple[object, ...]:
    letter = _STRAND_LETTER.get(r.name)
    if letter:
        return (r.name, " ", H.small(("MAM ", _heb(letter))))
    return (r.name,)


def _four_readings_table(readings: list[_Reading]) -> object:
    header = H.table_row_of_headers(
        ("reading", _heb("אנכי"), _heb("עבדים"), "structure")
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
                "The manuscript and printed traditions accent the Decalogue's first unit ",
                "differently, and the two ",
                _heb("טעמים"),
                " are effectively reassigned by one notch at the first commandment. Reading "
                "each Exodus version's first chanted verse straight from the vendored data and "
                "deriving the accent on its first word (",
                _heb("אנכי"),
                ") and on ",
                _heb("עבדים"),
                ":",
            )
        ),
        _four_readings_table(readings),
        H.unordered_list(
            (
                (
                    H.bold("Printed taḥton = manuscript elyon."),
                    " Once ",
                    _heb("אנכי…עבדים"),
                    " is a standalone verse there is only one grammatical way to accent it "
                    "-- etnaḥta in the middle, silluq at the end -- so both traditions land on "
                    "the same marks (consonants, accents, and accent-boundary marks: sof "
                    "pasuq, maqaf, legarmeh). They differ only by an immaterial meteg.",
                ),
                (
                    H.bold("Printed elyon ≠ manuscript elyon."),
                    " The printed elyon puts ",
                    H.bold("revia"),
                    " on ",
                    _heb("עבדים"),
                    " and runs the first two commandments together into one verse (→ ",
                    H.bold("9"),
                    " total), where the manuscript elyon closes on silluq (→ ",
                    H.bold("10"),
                    ").",
                ),
                (
                    "The manuscript ",
                    H.bold("taḥton"),
                    " does not give ",
                    _heb("אנכי…עבדים"),
                    " its own verse either -- it runs ",
                    _heb("אנכי…פני"),
                    " together (etnaḥta at ",
                    _heb("עבדים"),
                    ", sof pasuq at ",
                    _heb("פני"),
                    "). So “read it like the taḥton” can only mean the ",
                    H.bold("printed"),
                    " taḥton, not the manuscript one.",
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


def _transcription(lines: tuple[object, ...]) -> object:
    """An RTL blockquote transcription. ``lines`` are already-built inline pieces; a line break
    is inserted between them. Rendered in the pointed-text (hbo) font throughout."""
    body: list[object] = []
    for i, line in enumerate(lines):
        if i:
            body.append(H.line_break())
        body.append(line)
    return H.blockquote(tuple(body), {"dir": "rtl", "lang": "hbo"})


# The p. 83 transcription, following the scan's own line breaks (the pointed example verse
# אנכי…עבדים is MAM-divergent hand-set Hebrew, checked against the committed scan).
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


def _p83_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Main-text (elyon) note — Simanim p. 83"),
        H.para(
            (
                "A note in the margin of the Exodus (Yitro) Decalogue, on ",
                _heb("אנכי…עבדים"),
                ".",
            )
        ),
        _figure(
            _P83_IMG,
            "Simanim Tiqqun p. 83: marginal note on the Exodus Decalogue’s first unit",
            "Simanim Tiqqun, p. 83 — marginal note on אנכי…עבדים.",
            width="300",
        ),
        H.heading_level_3("Transcription"),
        _transcription(tuple(_P83_LINES)),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                H.bold("[ב]"),
                " {Regarding} the first verse — it is the custom of some to chant it as ",
                H.bold("ending on a revia"),
                ", as given in the main text (",
                _heb("בפנים"),
                "); {but} there are editions that call for it to be chanted as in the ",
                H.bold("lower"),
                " (taḥton) accentuation {specifically the ",
                H.bold("printed"),
                " taḥton — see the four readings above}, since by the Masorah there must be Ten "
                "Commandments here — thus: {the standalone verse ",
                _heb("אנכי…עבדים"),
                " shown above, ending on silluq / sof pasuq}. [The Ten Commandments without the "
                "upper accentuation appear at the end of the Ḥumash.]",
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
                "Simanim's ",
                H.bold("default"),
                " (",
                _heb("בפנים"),
                ") elyon reading thus ends the first unit on a ",
                H.bold("revia"),
                " — the merged, nine-verse printed structure — and only “some books” "
                "restore the standalone sof-pasuq verse to keep ten dibrot. On its own "
                "testimony, Simanim follows the ",
                H.bold("printed"),
                " tradition for the Decalogue elyon.",
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
            H.bold("מענה לשון"),
            H.line_break(),
            H.line_break(),
            H.bold(lemma),
            body,
        ),
        {"dir": "rtl", "lang": "hbo"},
    )


def _p246_mapping_table() -> object:
    header = H.table_row_of_headers(
        ("the note's label", _heb("אנכי"), _heb("עבדים"), "= four-readings row")
    )
    ragil = H.table_row(
        (
            H.table_header((_heb("בטעם רגיל"), " ", H.small("(ordinary)"))),
            H.table_datum("tipeḥa"),
            H.table_datum("sof pasuq"),
            H.table_datum("printed taḥton = manuscript elyon"),
        )
    )
    keter = H.table_row(
        (
            H.table_header(_heb("כתר אר״ץ")),
            H.table_datum("pashta"),
            H.table_datum("etnaḥta"),
            H.table_datum(("manuscript taḥton (MAM ", _heb("א"), ")")),
        )
    )
    return H.table((header, ragil, keter), {"class": "printed-decalogue-verdict"})


def _p246_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Appendix (taḥton) note — Simanim p. 246"),
        H.para(
            (
                "The mirror note, from the appendix's taḥton Decalogue (which Simanim heads "
                "only negatively, ",
                _heb("בלא טעם עליון"),
                ", “without the upper accentuation”). It sits under the section "
                "running-head ",
                _heb("מענה לשון"),
                " (maʿaneh lashon, Prov. 16:1 — a generic notes-section title), on the lemma ",
                _heb("אנכי"),
                ".",
            )
        ),
        _figure(
            _P246_IMG,
            "Simanim Tiqqun p. 246: appendix note on the taḥton Decalogue’s first unit",
            "Simanim Tiqqun, p. 246 — appendix note contrasting בטעם רגיל and כתר אר״ץ.",
            width=None,
        ),
        H.heading_level_3("Transcription"),
        _p246_transcription(),
        H.para(
            (
                H.small(
                    (
                        "The bold lemma reproduces the appendix's own body text, asterisk and "
                        "all, except that the note writes the Tetragrammaton as the double-yod ",
                        _heb("יְיָ"),
                        " where the body has ",
                        _heb("יהוה"),
                        ".",
                    )
                ),
            )
        ),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                H.bold("Maʿaneh Lashon."),
                " “",
                _heb("אנכי יי אלהיך"),
                " …” — Such is the version in the ordinary accentuation, which opens with ",
                H.bold("tipeḥa–etnaḥta"),
                " and ends with the verse-final word — at sof pasuq — ",
                _heb("עבדים"),
                "; but in the Keter Aram Tsova it opens with ",
                H.bold("pashta"),
                " and ends with ",
                H.bold("etnaḥta"),
                ", thus: {the merged reading ",
                _heb("אנכי…עבדים"),
                " shown above}. And as regards the “Ten Commandments” in the upper "
                "accentuation within the [main body of the] Ḥumash: …",
            )
        ),
        H.heading_level_3("How it maps onto the four readings"),
        H.para(
            (
                "The note contrasts two accentuations of the first unit, both already in the "
                "table above:",
            )
        ),
        _p246_mapping_table(),
        H.para(
            (
                "So Simanim's appendix, in its own editorial voice, draws the ",
                "printed-vs-manuscript taḥton distinction directly: what it prints and calls "
                "the “ordinary” taḥton is the standalone reading whose marks are the ",
                H.bold("manuscript's elyon"),
                ", while the genuine manuscript taḥton — the merged ",
                "pashta…etnaḥta",
                " reading — it sets aside in the note. Independent, printed-tradition "
                "confirmation that “read it like the taḥton” means the ",
                H.bold("printed"),
                " taḥton, since Simanim itself shows it knows the two taḥtons differ.",
            )
        ),
        H.heading_level_3("Two caveats"),
        H.unordered_list(
            (
                (
                    H.bold("“כתר אר״ץ” here is reconstruction, not autopsy."),
                    " The reading it reports (",
                    "pashta…etnaḥta",
                    ", merged) is the standard manuscript taḥton, so it is substantively right. "
                    "But the Aleppo Codex's Torah survives only from Deut 28:17 onward, so the "
                    "physical Keter contains neither Decalogue; any Keter statement about the "
                    "first commandment rests on reconstruction or pre-1947 testimony.",
                ),
                (
                    H.bold("The colon after "),
                    _heb("עבדים"),
                    H.bold(" is an editorial colon, not a sof pasuq."),
                    " The word is cited bare — vowels only, no silluq, no verse-mark — because "
                    "the note's topic is precisely how it is pointed: ",
                    _heb("עבדים"),
                    " is the shared pivot that takes a sof pasuq under ",
                    _heb("רגיל"),
                    " but an etnaḥta under the Keter reading. (",
                    _heb("בסו״פ"),
                    " = be-sof-pasuq, verse-finally, in the broad sense bundling silluq + sof "
                    "pasuq.)",
                ),
            )
        ),
    )


def _conclusion() -> tuple[object, ...]:
    return (
        H.heading_level_2("Conclusion"),
        H.para(
            (
                "Simanim's Tiqqun carries the ",
                H.bold("printed elyon"),
                " in the main text of its Decalogues and the ",
                H.bold("printed taḥton"),
                " in its appendix. Both marginal notes are independent printed-tradition "
                "witnesses to the standalone silluq reading that the printed tradition itself "
                "labels “taḥton,” which is what lets the ",
                link("issue #52 finding", _PRINTED_DECALOGUE_PAGE),
                " rest on more than MAM's own note alone.",
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
                "The four readings are read live from the vendored MAM data ",
                H.code("in/accgram/printed_decalogue_teamim.json"),
                rev,
                " — each Exodus version's first chanted verse, with the accent on ",
                _heb("אנכי"),
                " and ",
                _heb("עבדים"),
                " derived from its marks. The two Simanim transcriptions are hand-set from the "
                "committed scans (they diverge from MAM). All content is credited to MAM and "
                "the vendored data.",
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
