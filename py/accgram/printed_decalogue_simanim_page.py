r"""Generate gh-pages/accgram/printed-decalogue-simanim.html -- does Simanim's Tiqqun follow
the printed or the manuscript Decalogue tradition?  Answer: the printed tradition (issue #62).

Companion to ``printed_decalogue_page`` (issue #52, which grammar-checks the printed vs
manuscript Decalogue accentuations and lays out the four cantillation strands).  This page ports
two research notes -- formerly issue #56 comments -- into a versioned, reviewable document:

  * **p. 83** (main Decalogue, *elyon*): Simanim's side-margin note on the Exodus (Yitro)
    Decalogue first unit אנכי...עבדים.  Its default (בפנים) elyon reading ends that unit on a
    *revia* (the merged, 9-verse printed structure); "some books" instead give אנכי...עבדים its
    own verse (silluq + *sof pasuq* at עבדים) to keep ten distinct commandments.
  * **p. 246** (appendix, *taḥton*): the mirror footnote, contrasting בטעם רגיל (= printed
    taḥton: אנכי...עבדים as its own verse, *sof pasuq* at עבדים) with כתר אר״ץ (= manuscript
    taḥton: pashta...etnaḥta, merged).

What actually establishes the answer is not these notes but Simanim's *body text*: its main
Decalogue (p. 83) and appendix Decalogue (p. 246) are compared, by the author, against what Hebrew
Wikisource records as the printed tradition, and they match.  That body text is asserted here,
not reproduced.  The two notes are secondary -- kept for the more-for-fun question of
how aware Simanim is of having made the older, printed-tradition choice.

The four cantillation strands of the opening אנכי...עבדים unit are derived live from the vendored
``in/accgram/printed_decalogue_teamim.json`` by the shared ``printed_decalogue_strands`` module
and tabulated on the companion page; this page links to that table rather than duplicating it.
The two Simanim *transcriptions* are the only hand-set Hebrew, double-checked against the
committed scans.

Editorial / style conventions shared with the companion page -- bare-Hebrew strand names
תחתון / עליון (never transliterated or translated), the single-sourced ``ROM_*`` accent
romanizations, and the real-em-dash rule -- are documented on ``printed_decalogue_strands`` and
imported from it (the thin ``_TAHTON`` / ``_ELYON`` aliases below just limit prose churn; the
``_ROM_*`` ones additionally wrap each name in the italic ``span.romanized``, so they are HTML
nodes rather than strings -- see the comment at that alias block).  The conventions specific to
THIS page (keep them when editing):

* Prefer "**cantillation**" to "accentuation".
* **Three term pairs, kept strictly apart** (a recurring inconsistency -- don't regress):
  *main* vs *appendix* = the book's two parts (the running ḥumash vs the Decalogue reprinted at
  the back); *body* vs *note* = running text vs annotation; and the two notes differ by
  placement.  Use "main" ONLY for main-vs-appendix -- pair it as "main Decalogue" /
  "appendix Decalogue", never "main text" -- and "body" ONLY for body-vs-note (so the p. 83
  note's ``בפנים`` renders as "the body", NOT "the main text").  The **p. 83** note sits in the
  **side margin** ("side-margin note"); the **p. 246** note sits in the **bottom margin**, keyed
  by an asterisk -- it is a **footnote**, so never call it a "marginal note".  For the pair, say
  "notes" (never "marginal notes").
* **Image ``alt`` text keeps romanized names** ("taḥton") on purpose -- attribute contexts are
  exempt from the Hebrew-letter rule by design; see the "Attribute contexts are EXEMPT" bullet in
  ``printed_decalogue_strands``' module docstring for the full rule and why.

Regenerate with ``main_accgram.py generate-html``; test with
``tests/test_printed_decalogue_simanim.py`` (plus the tree-wide
``tests/test_transliterations.py``).  A running edit log lives in the gitignored
``.novc/pending_simanim_page_edits.md``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds
from accgram import rtms_report
from accgram.almost_errors_html_shared import hbo, link
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance

from py_html import wlc_utils_html as H
from py_html.my_html_span_romanized import rmn

import repo_paths

REPORT_TITLE = "Simanim's Tiqqun follows the printed tradition for the Decalogues"

# _ISSUE_52 = "https://github.com/bdenckla/wlc-utils/issues/52"
# _ISSUE_56 = "https://github.com/bdenckla/wlc-utils/issues/56"
_PRINTED_DECALOGUE_PAGE = "printed-decalogue.html"
# The four-strands table now lives on the companion page (issue #52); all cross-references land
# on its heading anchor there rather than on a local table.
_FOUR_STRANDS_HREF = f"{_PRINTED_DECALOGUE_PAGE}#four-strands"
_P83_IMG = "img/simanim-decalogue-p-083-sidenote.png"
_P246_IMG = "img/simanim-decalogue-p-246-footnote.png"
# Body-text scans (issue #62): the actual Simanim Decalogues whose cantillation establishes the
# p-trad finding -- distinct from the two note scans above.  p. 83 is the main Decalogue in the
# elyon; p. 246 is the appendix Decalogue in the taxton.
_P83_BODY_IMG = "img/Simanim-Tiqqun-p-083-Ex-Dec-elyon.png"
_P246_BODY_IMG = "img/Simanim-Tiqqun-p-246-Ex-Dec-p-trad-taxton.png"
# Simanim *Tanakh* (Feldheim), a different edition from the Tiqqun (issue #62 scope note): both
# its Exodus Decalogue strands are m-trad, unlike the Tiqqun's p-trad -- the running-text taxton
# (p. 119) and the elyon in the Torah section's appendix (p. 350).
_TANAKH_EX_TAHTON_IMG = "img/Feldheim-Tanakh-p-0119-Ex-Dec-start-m-trad-taxton.png"
_TANAKH_EX_ELYON_IMG = "img/Simanim-Tanakh-p-350-Ex-Dec-elyon-m-trad.png"

# Strand names and accent romanizations are single-sourced in printed_decalogue_strands (see its
# module docstring). These thin local aliases keep the prose below unchanged after the move.
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON
# Each _ROM_* accent name is pre-wrapped ONCE in <span class="romanized"> (italic), so every prose
# site below is styled without a per-site rmn() call -- issue #65, finding C2; the rule and its
# exclusions are documented in printed_decalogue_strands' module docstring. These are HTML nodes,
# not strings: splice them into a contents tuple, never into an f-string.
_ROM_PASHTA = rmn(pds.ROM_PASHTA)
_ROM_TIPEHA = rmn(pds.ROM_TIPEHA)
_ROM_ETNAHTA = rmn(pds.ROM_ETNAHTA)
_ROM_REVIA = rmn(pds.ROM_REVIA)
_ROM_SOF_PASUQ = rmn(pds.ROM_SOF_PASUQ)
_ROM_PASHTA_ETNAHTA = rmn(pds.ROM_PASHTA_ETNAHTA)
_ROM_TIPEHA_ETNAHTA = rmn(pds.ROM_TIPEHA_ETNAHTA)
_ROM_TIPEHA_SILLUQ = rmn(pds.ROM_TIPEHA_SILLUQ)
_ROM_SILLUQ_SOF_PASUQ = rmn(pds.ROM_SILLUQ_SOF_PASUQ)

# The p-trad Decalogue on Hebrew Wikisource sits in the printed-tradition (נוסח הדפוסים) section
# of the very page these four strands are vendored from -- so its base URL is single-sourced from
# the data's own provenance (see _source_section), and we append only the section anchor here.
# That Exodus section holds BOTH p-trad strands (תחתון and עליון), which is exactly what the
# spot-check compares against.  Wikisource forms a heading's anchor id by replacing spaces with
# underscores (parentheses kept literally); the Deuteronomy copy of this heading gets a "_2"
# suffix, so the bare (suffix-less) id is the Exodus one we want.
_WIKISOURCE_PTRAD_SECTION = "הטעם התחתון מול הטעם העליון (לפי נוסח הדפוסים)"


def _wikisource_ptrad_href(source: dict) -> str:
    base = source["provenance"]["url"]
    return f"{base}#{_WIKISOURCE_PTRAD_SECTION.replace(' ', '_')}"


def _path(path: str) -> object:
    """A repo path as plain body text (no monospace <code>, whose optical size clashes with
    the surrounding font) that may still line-break after each slash (issue #62)."""
    contents: list[object] = []
    for i, part in enumerate(path.split("/")):
        if i:
            contents += ["/", H.word_break_opportunity()]
        contents.append(part)
    return H.span(tuple(contents))


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
# This page used to open with the companion page's whole four-strands intro paragraph, duplicated
# verbatim (issue #65, finding V5). It now opens with ONE sentence that cues the reiteration and
# links to the companion, which alone states the four strands in full. Keep it to one sentence: a
# reader arriving here from the companion should be able to see at a glance that nothing new is
# being said yet.
_PARA_1 = (
    "As ",
    link("the companion page", _FOUR_STRANDS_HREF),
    " explains, each Decalogue has not two strands of cantillation but",
    *[" ", H.bold("four"), ": the"],
    *[" ", H.bold("printed tradition"), " (p-trad)"],
    " and the",
    *[" ", H.bold("manuscript tradition"), " (m-trad)"],
    f" each have their own טעם {_TAHTON} and their own טעם {_ELYON}, differing most strikingly over"
    " whether אנכי…עבדים, typically identified as the first commandment, is an entire chanted"
    " verse or only the start of one.",
)

# The continuation is this page's own second paragraph (the companion page's differs).
_PARA_2 = (
    "That page lays out those four strands and grammar-checks the p-trad; this page serves only to"
    " document the claim that",
    *[" ", H.bold("Simanim's Tiqqun"), " follows the p-trad."],
    " Along the way it transcribes two of Simanim's notes"
    " — not to establish the claim, but to show"
    " how conscious Simanim is of the choice it makes.",
)


def _body_scans() -> tuple[object, ...]:
    """The two body-text scans that establish the finding (issue #62): Simanim's main Decalogue in
    the p-trad עליון (p. 83) and its appendix Decalogue in the p-trad תחתון (p. 246). These are the
    body text the page used to only assert; showing them is what replaces the old apology.
    """
    return (
        _figure(
            _P83_BODY_IMG,
            "Simanim Tiqqun p. 83: the Exodus main Decalogue in the elyon",
            (
                "The (massive) verse that starts Simanim's main Decalogue (p. 83), headed",
                *[" ", H.bdi(' "עשרת הדברות" בטעם עליון'), "."],
                " The אנכי…עבדים unit ends on a",
                *[" ", _ROM_REVIA, "."],
                H.line_break(),
                H.small(
                    (
                        "The horizontal brown bar marks a removed page break — two page-scans"
                        " joined into a single column.",
                    )
                ),
            ),
            width=None,
        ),
        _figure(
            _P246_BODY_IMG,
            "Simanim Tiqqun p. 246: the Exodus appendix Decalogue in the taḥton",
            (
                f"The (short) two verses that start Simanim's appendix Decalogue (p. 246), headed עשרת הדברות דיתרו בלא טעם עליון."
                " (Heading not shown in this image though.)"
                " The אנכי…עבדים unit ends on a",
                *[" ", _ROM_SILLUQ_SOF_PASUQ, "."],
                " The asterisk is a callout to the footnote transcribed below.",
            ),
            width=None,
        ),
    )


def _intro(source: dict) -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.para(_PARA_1),
        H.para(_PARA_2),
        H.para(
            (
                "Simanim's Tiqqun follows the p-trad for the Decalogues. In its ",
                H.bold("Exodus"),
                " (Yitro) Decalogue, Simanim's main Decalogue (p. 83) is the p-trad"
                f" {_ELYON} and its appendix Decalogue (p. 246) is the p-trad {_TAHTON}"
                ". Since no digital Simanim exists, I established this by"
                " visually spot-checking Simanim against ",
                link("Hebrew Wikisource's p-trad", _wikisource_ptrad_href(source)),
                ". The two scans below reproduce that body text — Simanim's own main and"
                " appendix Decalogues.",
            )
        ),
        *_body_scans(),
    )


# Every ``alt`` passed here names the strands in ROMANIZED form ("taxton"/"elyon") while the
# figcaption beside it uses Hebrew letters. That is deliberate, not drift: attribute contexts are
# exempt by design (issue #65, finding T1) -- see printed_decalogue_strands' module docstring.
def _figure(src: str, alt: str, caption: object, *, width: str | None) -> object:
    # No inline style here: gh-pages/style.css already declares `img { max-width: 100% }` and
    # `figure img { height: auto }`, so an inline copy only duplicated the stylesheet and
    # outranked it (issue #65, finding C4b). Don't reintroduce it.
    img_attr = {"src": src, "alt": alt}
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


# The standalone-verse (ten-commandment) cantillation the p. 83 note gives after "כך:" -- the same
# pointed אנכי…עבדים of _P83_LINES above, run together as one verse (silluq + sof pasuq at עבדים),
# quoted in the translation below so it shows the real text rather than describing it.
_P83_STANDALONE_VERSE = (
    "אָֽנֹכִ֖י יְהֹוָ֣ה אֱלֹהֶ֑יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ"
    " מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֥ית עֲבָדִֽים׃"
)


def _p83_scan_and_transcription() -> object:
    """Scan and transcription side by side, as in the original issue-#56 comment: a two-column
    table with the source scan on the left and the RTL transcription (following the scan's own
    line breaks) on the right."""
    # As in _figure: no inline style, since gh-pages/style.css's `img { max-width: 100% }` already
    # covers it (issue #65, finding C4b). This img sits in a table cell rather than a <figure>, so
    # it never picked up `figure img { height: auto }` -- but height:auto is the CSS initial value
    # for a replaced element anyway, so the inline copy bought nothing here either.
    img = H.img(
        {
            "src": _P83_IMG,
            "alt": "Simanim Tiqqun p. 83: side-margin note on the Exodus Decalogue's אנכי…עבדים unit",
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
        H.heading_level_2("Margin note on the main (עליון) Decalogue — Simanim p. 83"),
        H.para(
            (
                "A note in the side margin of the Exodus (Yitro) Decalogue, on אנכי…עבדים.",
            )
        ),
        _p83_scan_and_transcription(),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                H.bold("[{Verse 20:}2]"),
                " {Regarding} the first {pseudo-?} verse — it is the custom of some to chant it as ",
                H.bold(("ending on a ", _ROM_REVIA)),
                ", as given in the body; {but} there are editions that call for it"
                " to be chanted as in the ",
                _TAHTON,
                " since by the Masorah there must be Ten Commandments here — thus:",
                H.line_break(),
                hbo(_P83_STANDALONE_VERSE),
                H.line_break(),
                "[The Ten Commandments without the ",
                f"{_ELYON} cantillation "
                "{can be found}"
                " at the end of the ḥumash.]",
            )
        ),
        H.para(
            (
                H.small(
                    (
                        H.bold("Notation:"),
                        *[
                            " text in ",
                            H.bold("{curly braces}"),
                            " is my editorial addition; ",
                        ],
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
                f" {_ELYON} ends the אנכי…עבדים unit on a ",
                H.bold(_ROM_REVIA),
                " — the nine-verse p-trad structure — and it files the standalone,"
                " ten-verse cantillation (",
                _ROM_SILLUQ_SOF_PASUQ,
                " at עבדים) under what merely “some books” do. So Simanim treats the p-trad"
                " structure as the norm and the m-trad alternative as the deviation — aware of the"
                " alternative, but not adopting it.",
            )
        ),
    )


# The merged (Keter / m-trad תחתון) cantillation the p. 246 note gives after "כך:" -- אנכי…עבדים
# run together as one verse, closing mid-verse rather than on a sof pasuq, quoted both in the
# transcription below and, factored out, in the translation so each shows the real text.
_P246_MERGED_VERSE = (
    "אָֽנֹכִי֙ יְהֹוָ֣ה אֱלֹהֶ֔יךָ אֲשֶׁ֧ר הֽוֹצֵאתִ֛יךָ"
    " מֵאֶ֥רֶץ מִצְרַ֖יִם מִבֵּ֣ית עֲבָדִ֑ים"
)


# The lemma the p. 246 footnote is keyed to -- its opening words, set off in the source's own
# emphasis (rendered blue here; the asterisk keys the footnote, and יי is the note's double-yod
# Tetragrammaton). Shared by the transcription and the translation so both show the same pointed,
# blue lemma.
_P246_LEMMA = "אָֽנֹכִ֖י* יְיָ֣ אֱלֹהֶ֑יךָ"

# The ordinary (רגיל / p-trad תחתון) sof-pasuq form of עבדים as the p. 246 note points it, shared
# by the transcription and the translation.
_P246_AVADIM_RAGIL = "עֲבָדִים"


def _p246_transcription() -> object:
    body = (
        f" וגו׳ כך היא הגרסה בטעם רגיל שפותח בטפחה אתנחתא ומסיים תיבת בסו״פ {_P246_AVADIM_RAGIL}: "
        f"ובכתר אר״ץ פותח בפשטא ומסיים באתנחתא, כך: {_P246_MERGED_VERSE}. ולגבי "
        '"עשרת הדברות"'
        " בטעם עליון בתוך החומש:"
    )
    return H.blockquote(
        (
            H.span_c(_P246_LEMMA, "simanim-lemma"),
            body,
        ),
        {"dir": "rtl", "lang": "hbo"},
    )


def _p246_mapping_table() -> object:
    # עבדים…אנכי columns in Hebrew reading order (right-to-left): עבדים sits left of אנכי.
    # The last column links each label to the four-strands table on the companion page.
    header = H.table_row_of_headers(
        ("the note's label", "עבדים", "אנכי", "= strand (companion page)")
    )
    ragil = H.table_row(
        (
            H.table_header(("בטעם רגיל", " ", H.small("(ordinary)"))),
            # This strand gives אנכי…עבדים its own chanted verse (pds.STRUCTURE pins that
            # verse's end at עבדים), so עבדים IS verse-final here and its U+05BD really is
            # silluq, not a meteg. Name the accent and the punctuation both, as the rest of
            # the page-set does -- "sof pasuq" alone named neither the accent nor the strand.
            H.table_datum(_ROM_SILLUQ_SOF_PASUQ),
            H.table_datum(_ROM_TIPEHA),
            H.table_datum(
                link(("p-trad ", _TAHTON, " = m-trad ", _ELYON), _FOUR_STRANDS_HREF)
            ),
        )
    )
    keter = H.table_row(
        (
            H.table_header("כתר אר״ץ"),
            H.table_datum(_ROM_ETNAHTA),
            H.table_datum(_ROM_PASHTA),
            H.table_datum(link(("m-trad ", _TAHTON), _FOUR_STRANDS_HREF)),
        )
    )
    # Its own class, not the companion page's "printed-decalogue-verdict": this table maps the
    # note's labels onto strands, it renders no grammaticality verdict, and it never used that
    # class's td.clean / td.ungrammatical rules (issue #65, finding C4d).
    return H.table(
        (header, ragil, keter), {"class": "printed-decalogue-strand-mapping"}
    )


def _p246_section() -> tuple[object, ...]:
    return (
        H.heading_level_2(
            "Footnote on the appendix (תחתון) Decalogue — Simanim p. 246"
        ),
        H.para(
            (
                f"The mirror footnote, from the appendix's {_TAHTON} Decalogue (which Simanim"
                f" heads only negatively, בלא טעם עליון — lacking the {_ELYON}), on the lemma"
                " אנכי.",
            )
        ),
        _figure(
            _P246_IMG,
            "Simanim Tiqqun p. 246: appendix footnote on the taḥton Decalogue's אנכי…עבדים unit",
            # The blue vertical bars are deliberately a different colour AND orientation from
            # the brown horizontal page-break bar (see the p. 83 elyon figure above): the two
            # mark opposite operations — a horizontal brown bar marks a page break we *removed*
            # (two scans joined), whereas these mark line breaks we *added* to a single wide
            # line. That contrast is the reason for the distinct styling, but it's mechanical
            # detail; the caption states only what each bar means, not why they look different.
            (
                "Simanim Tiqqun, p. 246 — appendix footnote contrasting בטעם רגיל and כתר אר״ץ.",
                H.line_break(),
                H.small(
                    (
                        "The vertical blue bars mark line breaks I added — after אתנחתא and after"
                        " עבדים — to narrow the inconveniently wide original.",
                    )
                ),
            ),
            width=None,
        ),
        H.heading_level_3("Transcription"),
        _p246_transcription(),
        H.para(
            (
                H.small(
                    (
                        "The lemma is shown in blue rather than boldface — bold renders many"
                        " Hebrew fonts' diacritics hard to read, so I substitute colour for the"
                        " source's own emphasis. It reproduces the appendix's own body text,"
                        " asterisk and all, except that the note writes the Tetragrammaton as the"
                        " double-yod (יי) abbreviation where the body has the full יהוה.",
                    )
                ),
            )
        ),
        H.para(
            (
                H.small(
                    (
                        "It isn't clear whether the mark after עבדים in the transcription is a ",
                        _ROM_SOF_PASUQ,
                        " or a colon; I read it as a colon.",
                    )
                ),
            )
        ),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                H.span_c(hbo(_P246_LEMMA), "simanim-lemma"),
                " Such is the version in the ordinary cantillation, which"
                " opens with ",
                H.bold(_ROM_TIPEHA_ETNAHTA),
                " and ends with the ",
                _ROM_SOF_PASUQ,
                " word ",
                hbo(_P246_AVADIM_RAGIL),
                "; but in the Keter Aram Tsova it opens with ",
                H.bold(_ROM_PASHTA),
                " and ends with ",
                H.bold(_ROM_ETNAHTA),
                ", thus: ",
                hbo(_P246_MERGED_VERSE),
                ". And as regards the “Ten" " Commandments” in the ",
                f"{_ELYON} within the ḥumash: " "{see the main part of the ḥumash?}",
            )
        ),
        H.para(
            (
                H.small(
                    (
                        "On Simanim's citing the כתר אר״ץ (Aleppo Codex) here — what that citation"
                        " can and cannot mean — see ",
                        link("the note below", "#simanim-aleppo-codex"),
                        ".",
                    )
                ),
            )
        ),
        H.heading_level_3("How it maps onto the four strands"),
        H.para(
            (
                "The note contrasts two cantillations of the אנכי…עבדים unit, both in the ",
                link("four-strands table on the companion page", _FOUR_STRANDS_HREF),
                ":",
            )
        ),
        _p246_mapping_table(),
        H.para(
            (
                f"So the note has Simanim, in its own editorial voice, distinguishing two"
                f" {_TAHTON} cantillations of the אנכי…עבדים unit: what it prints and calls the"
                f" “ordinary” (רגיל) {_TAHTON} — עבדים with ",
                _ROM_SILLUQ_SOF_PASUQ,
                f", אנכי…עבדים as its own verse, its marks identical to the m-trad {_ELYON} —"
                " versus the Keter's ",
                _ROM_PASHTA_ETNAHTA,
                f", the genuine m-trad {_TAHTON}, which it sets aside. Simanim thus knows the two"
                " differ and knowingly prints the newer one — another glimpse of the same"
                " self-awareness as the p. 83 margin note.",
            )
        ),
    )


def _conclusion() -> tuple[object, ...]:
    return (
        H.heading_level_2("Conclusion", {"id": "simanim-conclusion"}),
        H.para(
            (
                "Simanim's Tiqqun follows the p-trad for the Decalogues, not the m-trad. The two"
                " traditions' most consequential divergence is at the opening commandment"
                " אנכי…עבדים, and Simanim lands"
                f" on the p-trad side of that divergence on both strands: the p-trad {_ELYON} in"
                " its ",
                H.bold("Exodus"),
                f" main Decalogue (p. 83), and the p-trad {_TAHTON} in its appendix Decalogue"
                " (p. 246).",
            )
        ),
        H.para(
            (
                "A closing, more-for-fun observation. I find it somewhat ",
                H.bold("editorially inconsistent"),
                " that Simanim — otherwise a modern Tiqqun (from Feldheim) — keeps p-trad"
                f" Decalogues, where more recent Bibles have moved toward the m-trad {_ELYON} and"
                f" m-trad {_TAHTON}. The two notes above suggest Simanim was at least half-aware"
                " of the tension: each sets its p-trad cantillation against the standalone-verse"
                " / Keter alternative it declines to follow. (Straddling old and new is less"
                " surprising in a house like Koren, which does it more pervasively; Simanim's is"
                " a milder case.)",
            )
        ),
        # Ben provides an image of Simanim's Deuteronomy appendix taxton Decalogue (p. 247),
        # img/Simanim-Tiqqun-p247-Deut-Dec-m-trad-taxton-Shabbat.png, showing that its Shabbat
        # commandment follows the m-trad rather than the p-trad cantillation. That image is
        # deliberately NOT linked from this HTML (the Deuteronomy text is not reproduced here);
        # it is committed only as the private evidence behind this scope note's Shabbat caveat.
        H.para(
            (
                "One scope note: the finding above rests on the אנכי…עבדים unit — the most striking"
                " p-trad/m-trad divergence. Simanim makes the same p-trad choice at that unit in"
                " both of its Decalogues: the ",
                H.bold("Exodus"),
                " (Yitro) one and the ",
                H.bold("Deuteronomy"),
                f" (Vaetḥanan) one, whose {_ELYON} main Decalogue starts on p. 208. One caveat:"
                " in the"
                f" Deuteronomy {_TAHTON} (appendix, p. 247), the p-trad and m-trad also diverge at"
                " the Shabbat commandment, but there Simanim follows the m-trad, not the p-trad —"
                " so its p-trad allegiance, firm at אנכי…עבדים across both Decalogues, is not"
                " absolute.",
            )
        ),
        H.para(
            (
                "Another scope note: everything above concerns Simanim's ",
                H.bold("Tiqqun"),
                ". The separately published Simanim ",
                H.bold("Tanakh"),
                " (Feldheim) does not agree with it: the Tanakh follows the ",
                H.bold("m-trad"),
                f", not the p-trad, on both strands. Where the Tiqqun is p-trad, the Tanakh's"
                f" Exodus Decalogue is the m-trad {_TAHTON} in its running text (p. 119) and the"
                f" m-trad {_ELYON} in the appendix to the Torah section (p. 350) — both shown"
                f" below. Its Deuteronomy Decalogue is likewise m-trad on both strands — the"
                f" {_TAHTON} in the running text (starting p. 297) and the {_ELYON} in that same"
                f" appendix, where Deuteronomy agrees with Exodus, as one would expect (neither"
                " Deuteronomy image shown). So the two Simanim editions genuinely diverge — one"
                " should not assume they agree.",
            )
        ),
        _figure(
            _TANAKH_EX_TAHTON_IMG,
            "Simanim Tanakh p. 119: the Exodus Decalogue in running text, in the m-trad taḥton",
            (
                "Simanim Tanakh, p. 119 — the start of the Exodus Decalogue in running text, in"
                f" the m-trad {_TAHTON} cantillation.",
            ),
            width=None,
        ),
        _figure(
            _TANAKH_EX_ELYON_IMG,
            "Simanim Tanakh p. 350: the Exodus Decalogue in the appendix to the Torah section, in the m-trad elyon",
            (
                "Simanim Tanakh, p. 350 — the Exodus Decalogue in the appendix to the Torah"
                f" section, in the m-trad {_ELYON} cantillation.",
            ),
            width=None,
        ),
        H.para(
            (
                "The two editions also swap which strand goes in the running text and which in an"
                " appendix, as one would expect from their different purposes: the Tiqqun runs the"
                f" {_ELYON} in its main text and appends the {_TAHTON}, whereas the Tanakh does the"
                f" reverse — the everyday {_TAHTON} in the running text and the {_ELYON} in an"
                " appendix. And because this is a Tanakh, not a Torah-only Tiqqun, that appendix"
                " sits at the end of the Torah section — mid-volume, before the Prophets — not at"
                " the back of the book.",
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
                "The companion page's ",
                link("four-strands table", _FOUR_STRANDS_HREF),
                " is read live from the vendored Hebrew Wikisource data ",
                _path("in/accgram/printed_decalogue_teamim.json"),
                rev,
                " (עשרת הדברות בסיס/טעמים). This page's own content is the two Simanim"
                " transcriptions, hand-set from the committed scans of Simanim's Tiqqun and"
                " credited to Simanim.",
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
                "The p. 246 note cites the כתר אר״ץ (Keter Aram Tsova, the Aleppo Codex) for the"
                " ",
                _ROM_PASHTA_ETNAHTA,
                " cantillation. Two things are worth keeping straight about that citation.",
            )
        ),
        H.unordered_list(
            (
                (
                    H.bold(
                        "It names one of the Codex's two Decalogue cantillations, not"
                        " “the” cantillation."
                    ),
                    " The ",
                    _ROM_PASHTA_ETNAHTA,
                    f" cantillation is the m-trad {_TAHTON} — one strand. Like the Tiberian"
                    " manuscripts generally, the Aleppo Codex's Decalogue has ",
                    H.bold("both"),
                    f" cantillations; the {_ELYON} is the other (אנכי…עבדים as its own verse, ",
                    _ROM_TIPEHA_SILLUQ,
                    f"). Citing the {_TAHTON} strand alone does not mean the Codex has only one.",
                ),
                (
                    H.bold("And it is a reconstruction, not an autopsy."),
                    " The Aleppo Codex's Torah survives only from Deut 28:17 onward, so the"
                    " physical Codex contains neither Decalogue; any statement about how “the"
                    " Keter” points אנכי…עבדים rests on reconstruction or pre-1947 testimony."
                    " Simanim, in a passing reference, has no room to say so — but strictly it"
                    " should read “one of the two cantillations reconstructed for the Aleppo Codex"
                    " is …”.",
                ),
            )
        ),
    )


def render_body_contents(source: dict) -> tuple[object, ...]:
    return (
        *_intro(source),
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
    parser.add_argument(
        "--html-out", type=Path, default=default_html_out_path(repo_root)
    )


def run(args: argparse.Namespace) -> None:
    # The four-strands table lives on the companion page now, so this page never grammar-checks
    # the readings -- it only needs the source's provenance (revision + p-trad section URL). We
    # load the source but skip pd.check_all, a real speedup for solo regeneration.
    source = pd.load_source(args.source)

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(source),
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
