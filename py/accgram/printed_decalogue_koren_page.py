r"""Generate gh-pages/accgram/printed-decalogue-koren.html -- does the Koren Tanakh follow the
printed or the manuscript Decalogue tradition?  Answer: the printed tradition.

Companion to ``printed_decalogue_simanim_page``: the same question, asked of Koren instead of
Simanim's Tiqqun.  The four cantillation strands of the opening אנכי…עבדים span are derived live
from the vendored ``in/accgram/printed_decalogue_teamim.json`` by the shared
``printed_decalogue_strands`` module and tabulated on the ``printed-decalogue`` companion page;
this page links to that table rather than duplicating it, and serves only to document Koren's
place in the p-trad camp -- plus one Koren note that shows the same editorial self-awareness the
Simanim page found in Simanim.

What establishes the answer is Koren's *body text*: its Exodus main Decalogue (p. 113) is the
p-trad תחתון and its appendix Decalogue (p. A38) the p-trad עליון, and both are compared, by
the author, against what Hebrew Wikisource records as the printed tradition, and they match.  That
body text is asserted here, not transcribed word-for-word (only shown as scans).
The one *note* is the secondary, more-for-fun material -- kept for how aware Koren is of the older,
printed-tradition choice it makes:

  * **appendix p. A38** (עליון): a note on the merged עליון Decalogue, citing רוו״ה
    (= ר' וולף היידנהיים, R. Wolf Heidenheim), directing that the First Commandment -- through
    מבית עבדים -- be read בטעם התחתון, i.e. as its own chanted verse rather than merged into the
    long opening verse the עליון body prints.  This is the exact mirror of Simanim's p. 83
    side-margin note: the עליון body ends אנכי…עבדים on a revia, and the note flags the
    standalone-verse (ten-commandment) alternative it declines to print.

Editorial / style conventions are shared with the two companion pages and documented on
``printed_decalogue_strands`` (bare-Hebrew strand names תחתון / עליון -- never transliterated or
translated; the single-sourced ``ROM_*`` accent romanizations; the real-em-dash rule).  The thin
``_TAHTON`` / ``_ELYON`` aliases below just limit prose churn; the ``_ROM_*`` ones additionally
wrap each name in the italic ``span.romanized``, so they are HTML nodes rather than strings (see
the comment at that alias block).  As on the Simanim
page: prefer "cantillation" to "accentuation"; keep romanized names ("taḥton") in image ``alt``
text on purpose (attribute contexts are exempt from the Hebrew-letter rule by design -- see the
"Attribute contexts are EXEMPT" bullet in ``printed_decalogue_strands``); and keep the two term
pairs strictly apart.  *main* vs *appendix* = the book's two parts (the running Torah text vs the
Decalogue reprinted in the appendix) -- use "main" ONLY for that pair, worded as "main Decalogue" /
"appendix Decalogue", never "main text"; and *body* (printed text) vs *note* (annotation).  Do not
regress "main" to "running text" here: the Simanim page's docstring is the fuller statement of this
rule.  (Note Koren is a **Tanakh**, not a ḥumash -- the Simanim page glosses this same pair as "the
running ḥumash", which is right for its Torah-only Tiqqun but would be wrong here.)

DRAFT-STAGE FACTS TO VERIFY (see .novc/pending_koren_page_edits.md): the page numbers (113 / A38)
come from the committed scan filenames; and רוו״ה is *tentatively* expanded to Wolf Heidenheim
(likely but unconfirmed, flagged as such in the rendered notation line).

The appendix's separate pagination IS now confirmed (Ben, 2026-07-15), which is why every citation
of it reads "p. A38", never a bare "p. 38": the appendix restarts its own page numbering at 1, so
an unprefixed 38 would read as page 38 of the book's main part and, being lower than the main
Decalogue's own p. 113, would wrongly suggest the appendix sits *before* it.  Keep the A prefix on
appendix citations, and don't "normalize" it away.  (The scan *filenames* keep their original
``Koren-appendix-p-38-...`` spelling -- they are committed assets, and "appendix" already
disambiguates them.)

Koren's Deuteronomy (Vaetxanan) Decalogue *has* now been spot-checked (issue #66), so the claim is
no longer Exodus-scoped: Koren shows the p-trad in both books.  The Deuteronomy check also reaches
a second divergence point the Exodus scans cannot -- the Shabbat commandment -- where Koren again
shows the p-trad, and where Simanim's Tiqqun does not.  See the conclusion's scope note.

Regenerate with ``main_accgram.py generate-html``; test with
``tests/test_printed_decalogue_koren.py`` (plus the tree-wide ``tests/test_transliterations.py``).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import printed_decalogue_strands as pds
from accgram import rtms_report
from accgram.almost_errors_html_shared import link
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance

from py_html import wlc_utils_html as H
from py_html.my_html_span_romanized import rmn

import repo_paths

# Plural "Decalogues" since issue #66: the claim now genuinely covers Exodus and Deuteronomy both,
# so the Simanim page's plural policy (claims about both Decalogues take the plural) applies here
# too. It was singular only while the page was Exodus-scoped.
REPORT_TITLE = "Koren follows the printed tradition for the Decalogues"

_PRINTED_DECALOGUE_PAGE = "printed-decalogue.html"
_SIMANIM_PAGE = "printed-decalogue-simanim.html"
# The four-strands table lives on the companion page (issue #52); cross-references whose link text
# names the table land on its heading anchor there rather than on a local table.
_FOUR_STRANDS_HREF = f"{_PRINTED_DECALOGUE_PAGE}#four-strands"
# Link text that names the page, not the table, gets the page itself: an anchor would drop the
# reader past the companion's own intro, mid-page, which is not what "the companion page" promises.
_COMPANION_PAGE_HREF = _PRINTED_DECALOGUE_PAGE

# Body-text scans: the two Koren Exodus Decalogues whose cantillation establishes the p-trad
# finding -- the תחתון in the main Decalogue (p. 113) and the עליון in the appendix (p. A38).
_P113_BODY_IMG = "img/Koren-p-113-Ex-Dec-p-trad-taxton.png"
_PA38_BODY_IMG = "img/Koren-appendix-p-38-Ex-Dec-p-trad-elyon.png"
# The Deuteronomy (Vaetxanan) תחתון Decalogue starts on p. 280 and runs onto p. 281; this crop is
# its Shabbat commandment, on p. 281. It backs the conclusion's scope note (issue #66): unlike
# Simanim's Tiqqun, Koren shows the p-trad here too.
_P281_DT_BODY_IMG = "img/Koren-p-281-Dt-Dec-Shabbat-p-trad-taxton.png"
# The Koren note (a crop of the appendix p. A38 עליון Decalogue): the רוו״ה footnote transcribed and
# translated below.
_PA38_NOTE_IMG = "img/Koren-appendix-p-38-Ex-Dec-p-trad-elyon-note.png"

# Strand names and accent romanizations are single-sourced in printed_decalogue_strands (see its
# module docstring). These thin local aliases keep the prose below unchanged.
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON
# Each _ROM_* accent name is pre-wrapped ONCE in <span class="romanized"> (italic), so every prose
# site below is styled without a per-site rmn() call -- issue #65, finding C2; the rule and its
# exclusions are documented in printed_decalogue_strands' module docstring. These are HTML nodes,
# not strings: splice them into a contents tuple, never into an f-string.
_ROM_REVIA = rmn(pds.ROM_REVIA)
_ROM_SILLUQ_SOF_PASUQ = rmn(pds.ROM_SILLUQ_SOF_PASUQ)
# The Deuteronomy Shabbat-commandment accents (issue #66), named only in the conclusion's scope
# note and the p. 281 figure caption.
_ROM_GERESH = rmn(pds.ROM_GERESH)
_ROM_ZAQEF_QATAN = rmn(pds.ROM_ZAQEF_QATAN)
_ROM_PAZER = rmn(pds.ROM_PAZER)

# The p-trad Decalogue on Hebrew Wikisource sits in the printed-tradition (נוסח הדפוסים) section of
# the very page these four strands are vendored from -- so its base URL is single-sourced from the
# data's own provenance, and we append only the section anchor here. (Same rule as the Simanim
# page; see its ``_wikisource_ptrad_href``.)
_WIKISOURCE_PTRAD_SECTION = "הטעם התחתון מול הטעם העליון (לפי נוסח הדפוסים)"


def _wikisource_ptrad_href(source: dict) -> str:
    base = source["provenance"]["url"]
    return f"{base}#{_WIKISOURCE_PTRAD_SECTION.replace(' ', '_')}"


def _path(path: str) -> object:
    """A repo path as plain body text (no monospace <code>) that may line-break after each slash."""
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
# links to the companion, which alone states the four strands in full, plus the shared
# pds.MOST_STRIKING sentence (single-sourced there, verbatim on all three pages of the trio).
# Keep it that way: a reader arriving here from the companion should be able to see at a glance
# that nothing new is being said yet.
_PARA_1 = (
    "As ",
    link("the companion page", _COMPANION_PAGE_HREF),
    " explains, each Decalogue has",
    *[" ", H.bold("four"), " strands of cantillation: the"],
    *[" ", H.bold("printed tradition"), " (p-trad)"],
    " and the",
    *[" ", H.bold("manuscript tradition"), " (m-trad)"],
    f" each have their own טעם {_TAHTON} and their own טעם {_ELYON}.",
    " " + pds.MOST_STRIKING,
)

_PARA_2 = (
    "That page lays out those four strands and grammar-checks the p-trad; this page serves only to"
    " document the claim that",
    *[" ", H.bold("Koren"), " follows the p-trad."],
    " Along the way it transcribes one of Koren's own notes.",
)


# Every ``alt`` passed here names the strands in ROMANIZED form ("taxton"/"elyon") while the
# figcaption beside it uses Hebrew letters. That is deliberate, not drift: attribute contexts are
# exempt by design (issue #65, finding T1) -- see printed_decalogue_strands' module docstring.
def _figure(src: str, alt: str, caption: object, *, width: str | None) -> object:
    # No inline style here: gh-pages/style.css already declares `img { max-width: 100% }` and
    # `figure img { height: auto }`, so an inline copy only duplicated the stylesheet and
    # outranked it (issue #65, finding C4b). Don't reintroduce it.
    # class="ink-on-white" opts the scan into the stylesheet's dark-mode CSS inversion. It is
    # unconditional here because every image on this page is a Koren scan -- black ink, white
    # paper. Don't hoist it into a shared img helper: the manuscript photos elsewhere in the
    # tree are ink on parchment and must NOT invert (see the rule's comment in style.css).
    img_attr = {"src": src, "alt": alt, "class": "ink-on-white"}
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


def _body_scans() -> tuple[object, ...]:
    """The two body-text scans that are the finding's actual evidence -- elsewhere the page only
    asserts Koren's body text, here it is shown.  (The captions below name the strands and pages.)
    """
    return (
        _figure(
            _P113_BODY_IMG,
            "Koren p. 113: the Exodus main Decalogue in the p-trad taḥton",
            (
                "The start of Koren's Exodus main Decalogue (p. 113), in"
                f" the p-trad {_TAHTON}. The אנכי…עבדים span is its own chanted verse, closing",
                *[" with a ", _ROM_SILLUQ_SOF_PASUQ, "."],
            ),
            width=None,
        ),
        _figure(
            _PA38_BODY_IMG,
            "Koren appendix p. A38: the Exodus appendix Decalogue in the elyon",
            (
                "The start of Koren's Exodus appendix Decalogue (p. A38), in the p-trad"
                f" {_ELYON}. The אנכי…עבדים span is only the first phrase of a long"
                " verse — עבדים has only a",
                *[" ", _ROM_REVIA, "."],
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
                "Koren follows the p-trad for the Decalogues. In its ",
                H.bold("Exodus"),
                " Decalogue, Koren's main Decalogue (p. 113) is the p-trad"
                f" {_TAHTON} and its appendix Decalogue (p. A38) is the p-trad {_ELYON}"
                ". Since no digital Koren exists, I established this by"
                " visually spot-checking Koren against ",
                link("Hebrew Wikisource's p-trad", _wikisource_ptrad_href(source)),
                ". The two scans below reproduce that body text — Koren's own main and"
                " appendix Decalogues.",
            )
        ),
        *_body_scans(),
    )


# The Koren note, following the scan's own two line breaks. It is unpointed prose (no cantillation),
# so unlike the Simanim transcriptions there is no hand-set pointed verse to check. רוו״ה carries a
# gershayim (U+05F4); the quoted lemma "מבית עבדים" reproduces the note's own straight quotes.
_PA38_NOTE_LINES = (
    'לדעת רוו״ה, יש לקרוא את הדיבר הראשון עד "מבית עבדים"',
    "בטעם התחתון.",
)


def _pa38_note_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Note on the appendix (עליון) Decalogue — Koren p. A38"),
        H.para(
            (
                "A note on the appendix Decalogue, keyed to the opening commandment אנכי…עבדים and"
                " citing רוו״ה.",
            )
        ),
        _figure(
            _PA38_NOTE_IMG,
            "Koren appendix p. A38: note on the elyon Decalogue's אנכי…עבדים span",
            (
                "Koren, appendix p. A38 — the note on the",
                f" {_ELYON} Decalogue, citing רוו״ה.",
            ),
            width=None,
        ),
        H.heading_level_3("Transcription"),
        H.blockquote(
            _lines_with_breaks(_PA38_NOTE_LINES),
            {"dir": "rtl", "lang": "hbo"},
        ),
        H.heading_level_3("Translation"),
        H.blockquote(
            (
                "In the opinion of רוו״ה {R. Wolf Heidenheim}, one should read the First"
                " Commandment (up to “מבית עבדים”) in the ",
                _TAHTON,
                ".",
            )
        ),
        H.para(
            (
                H.small(
                    (
                        H.bold("Notation:"),
                        " text in ",
                        H.bold("{curly braces}"),
                        " is my editorial addition. That includes the expansion of the siglum"
                        " רוו״ה, which I ",
                        H.bold("tentatively"),
                        " read as ר' וולף היידנהיים (R. Wolf Heidenheim) — the grammarian whose"
                        " editions fixed much of the printed dual-cantillation norm, so the"
                        " likeliest referent here, though I have not confirmed the expansion."
                        " The parentheses are likewise an editorial addition; the note itself has"
                        " none.",
                    )
                ),
            )
        ),
        H.para(
            (
                "The note is the mirror of ",
                link("Simanim's p. 83 side-margin note", _SIMANIM_PAGE),
                ". Koren's appendix prints the ",
                H.bold(_ELYON),
                " by default — the merged, nine-verse p-trad structure, in which אנכי…עבדים ends"
                " on a ",
                H.bold(_ROM_REVIA),
                " rather than closing its own verse. The note flags the alternative, on רוו״ה's"
                " authority: read the First Commandment (through מבית עבדים) in the ",
                _TAHTON,
                " — i.e. as its own chanted verse (",
                _ROM_SILLUQ_SOF_PASUQ,
                " at עבדים), which keeps ten distinct commandments. That ",
                _TAHTON,
                " cantillation is one of the ",
                link("four strands on the companion page", _FOUR_STRANDS_HREF),
                " (the p-trad ",
                _TAHTON,
                ", identical on its boundary words to the m-trad ",
                _ELYON,
                "). So Koren, like Simanim, prints the p-trad structure as the norm and files the"
                " standalone-verse alternative under what one authority merely recommends —"
                " aware of the alternative, but not adopting it.",
            )
        ),
    )


def _conclusion() -> tuple[object, ...]:
    return (
        H.heading_level_2("Conclusion", {"id": "koren-conclusion"}),
        H.para(
            (
                "Koren follows the p-trad for the Decalogues, not the m-trad. The two traditions'"
                " most consequential divergence is at the opening commandment אנכי…עבדים, and"
                " Koren lands on the p-trad side of that divergence on both strands: the p-trad ",
                _TAHTON,
                " in its ",
                H.bold("Exodus"),
                f" main Decalogue (p. 113), and the p-trad {_ELYON} in its appendix Decalogue"
                " (p. A38).",
            )
        ),
        H.para(
            (
                "A closing, more-for-fun observation — parallel to the one the ",
                link("Simanim page", _SIMANIM_PAGE),
                " makes, though it lands on a gentler verdict. It is somewhat ",
                H.bold("editorially conservative"),
                " to keep p-trad Decalogues at all — let alone to keep them in both books, as the"
                " scope note below shows Koren does — where more recent Bibles have moved toward"
                f" the m-trad {_ELYON} and m-trad {_TAHTON}. Koren straddles old and new rather"
                " pervasively; the רוו״ה note above is one glimpse of that — it sets Koren's"
                " printed ",
                _ELYON,
                " against the standalone-verse alternative it declines to print.",
            )
        ),
        H.para(
            (
                "One scope note: the finding above rests on the אנכי…עבדים span — the most striking"
                " p-trad/m-trad divergence. Koren makes the same p-trad choice at that span in both"
                " of its Decalogues: the ",
                H.bold("Exodus"),
                " one and the ",
                H.bold("Deuteronomy"),
                f" (Vaetḥanan) one, whose {_TAHTON} main Decalogue starts on p. 280 and runs onto"
                " p. 281. There too אנכי…עבדים is its own chanted verse, closing on עבדים with a",
                *[" ", _ROM_SILLUQ_SOF_PASUQ, "."],
            )
        ),
        H.para(
            (
                "Koren's Deuteronomy also reaches a divergence its Exodus Decalogue cannot: the"
                " Shabbat commandment, where the p-trad and m-trad part again. There too Koren"
                " shows the p-trad — so its p-trad allegiance is unqualified, where the ",
                link("Simanim page", _SIMANIM_PAGE),
                " finds Simanim's Tiqqun following the m-trad at that very commandment. The scan"
                " below is that commandment. One boundary on all this: what I have checked in"
                " Deuteronomy is the ",
                _TAHTON,
                "; I have not chased Koren's Deuteronomy ",
                _ELYON,
                " through its appendix, so the Deuteronomy half of the claim rests on the ",
                _TAHTON,
                " alone.",
            )
        ),
        _figure(
            _P281_DT_BODY_IMG,
            "Koren p. 281: the Shabbat commandment of the Deuteronomy Decalogue, in the p-trad"
            " taḥton",
            (
                "The Shabbat commandment of Koren's Deuteronomy (Vaetḥanan) main Decalogue"
                f" (p. 281), in the p-trad {_TAHTON}. Two of the p-trad's"
                " characteristic choices here: כָל־מְלָאכָ֜ה has a",
                *[" ", _ROM_GERESH, " where the m-trad has a "],
                _ROM_PAZER,
                ", and וְכָל־בְּהֶמְתֶּ֔ךָ has a",
                *[" ", _ROM_ZAQEF_QATAN, " where the m-trad has a "],
                _ROM_REVIA,
                ".",
            ),
            width=None,
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
                " (עשרת הדברות בסיס/טעמים). This page's own content is the Koren note"
                " transcription, hand-set from the committed scans of the Koren Tanakh and"
                " credited to Koren.",
            )
        ),
    )


def render_body_contents(source: dict) -> tuple[object, ...]:
    return (
        *_intro(source),
        *_pa38_note_section(),
        *_conclusion(),
        *_source_section(source),
    )


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue-koren.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=pd.default_source_path())
    parser.add_argument(
        "--html-out", type=Path, default=default_html_out_path(repo_root)
    )


def run(args: argparse.Namespace) -> None:
    # The four-strands table lives on the companion page, so this page never grammar-checks the
    # readings -- it only needs the source's provenance (revision + p-trad section URL). We load
    # the source but skip pd.check_all, a real speedup for solo regeneration.
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
