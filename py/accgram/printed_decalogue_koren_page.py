r"""Generate gh-pages/accgram/printed-decalogue-koren.html -- does the Koren Tanakh follow the
printed or the manuscript Decalogue tradition?  Answer: the printed tradition.

Companion to ``printed_decalogue_simanim_page``: the same question, asked of Koren instead of
Simanim's Tiqqun.  The four cantillation strands of the opening אנכי…עבדים unit are derived live
from the vendored ``in/accgram/printed_decalogue_teamim.json`` by the shared
``printed_decalogue_strands`` module and tabulated on the ``printed-decalogue`` companion page;
this page links to that table rather than duplicating it, and serves only to document Koren's
place in the p-trad camp -- plus one Koren note that shows the same editorial self-awareness the
Simanim page found in Simanim.

What establishes the answer is Koren's *body text*: its Exodus (Yitro) Decalogue is printed twice,
the p-trad תחתון in the running text (p. 113) and the p-trad עליון in an appendix (p. 38), and both
are compared, by the author, against what Hebrew Wikisource records as the printed tradition, and
they match.  That body text is asserted here, not transcribed word-for-word (only shown as scans).
The one *note* is the secondary, more-for-fun material -- kept for how aware Koren is of the older,
printed-tradition choice it makes:

  * **appendix p. 38** (עליון): a note on the merged עליון Decalogue, citing רוו״ה
    (= ר' וולף היידנהיים, R. Wolf Heidenheim), directing that the First Commandment -- through
    מבית עבדים -- be read בטעם התחתון, i.e. as its own chanted verse rather than merged into the
    long opening verse the עליון body prints.  This is the exact mirror of Simanim's p. 83
    side-margin note: the עליון body ends אנכי…עבדים on a revia, and the note flags the
    standalone-verse (ten-commandment) alternative it declines to print.

Editorial / style conventions are shared with the two companion pages and documented on
``printed_decalogue_strands`` (bare-Hebrew strand names תחתון / עליון -- never transliterated or
translated; the single-sourced ``ROM_*`` accent romanizations; the real-em-dash rule).  The thin
``_TAHTON`` / ``_ELYON`` / ``_ROM_*`` aliases below just limit prose churn.  As on the Simanim
page: prefer "cantillation" to "accentuation"; keep romanized names ("taḥton") in image ``alt``
text on purpose (don't mix alphabets in an alt attribute); and keep *running text* (the everyday
Torah text) distinct from *appendix* (the strand reprinted separately), and *body* (printed text)
distinct from *note* (annotation).

DRAFT-STAGE FACTS TO VERIFY (see .novc/pending_koren_page_edits.md): the page numbers (113 / 38)
come from the committed scan filenames; the appendix's separate low pagination is described but not
confirmed; the finding rests on the Exodus Decalogue only (Deuteronomy not checked yet); and
רוו״ה is *tentatively* expanded to Wolf Heidenheim (likely but unconfirmed, flagged as such in the
rendered notation line).

Regenerate with ``main_accgram.py generate-html``; test with
``tests/test_printed_decalogue_koren.py`` (plus the tree-wide ``tests/test_transliterations.py``).
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

import repo_paths

REPORT_TITLE = "Koren follows the printed tradition for the Decalogue"

_PRINTED_DECALOGUE_PAGE = "printed-decalogue.html"
_SIMANIM_PAGE = "printed-decalogue-simanim.html"
# The four-strands table lives on the companion page (issue #52); all cross-references land on its
# heading anchor there rather than on a local table.
_FOUR_STRANDS_HREF = f"{_PRINTED_DECALOGUE_PAGE}#four-strands"

# Body-text scans: the two Koren Decalogues whose cantillation establishes the p-trad finding.
# p. 113 is the Exodus Decalogue in the running text (תחתון); p. 38 is the same Decalogue reprinted
# in the appendix (עליון).
_P113_BODY_IMG = "img/Koren-p-113-Ex-Dec-p-trad-taxton.png"
_P38_BODY_IMG = "img/Koren-appendix-p-38-Ex-Dec-p-trad-elyon.png"
# The Koren note (a crop of the appendix p. 38 עליון Decalogue): the רוו״ה footnote transcribed and
# translated below.
_P38_NOTE_IMG = "img/Koren-appendix-p-38-Ex-Dec-p-trad-elyon-note.png"

# Strand names and accent romanizations are single-sourced in printed_decalogue_strands (see its
# module docstring). These thin local aliases keep the prose below unchanged.
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON
_ROM_REVIA = pds.ROM_REVIA
_ROM_SILLUQ_SOF_PASUQ = pds.ROM_SILLUQ_SOF_PASUQ

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
# The opening span -- from "Roughly speaking" through "only the start of one." -- is duplicated
# verbatim in printed_decalogue_page._intro() and printed_decalogue_simanim_page._PARA_1 (the
# no-HTML shared module pds can't hold rendered prose). If you edit this wording, edit it in all
# three places.
_PARA_1 = (
    "Roughly speaking, each Decalogue",
    " has two strands of cantillation, the טעם תחתון and the טעם עליון.",
    " Why is this only roughly true? Because in detail there are",
    *[" ", H.bold("four"), " strands: the"],
    *[" ", H.bold("printed tradition"), " (p-trad)"],
    " and the",
    *[" ", H.bold("manuscript tradition"), " (m-trad)"],
    " differ in cantillation,",
    f" yielding two different {_ELYON} strands and two different {_TAHTON} strands.",
    " (The p-trad is fading, but still visible in editions like Koren and Simanim.)",
    #
    " The most striking difference between the p-trad and m-trad has to do with whether אנכי…עבדים,",
    " typically identified as the first commandment, is an entire chanted verse or",
    " only the start of one.",
)

_PARA_2 = (
    link("The companion page", _FOUR_STRANDS_HREF),
    " lays out those four strands and grammar-checks the p-trad; this page serves only to"
    " document the claim that",
    *[" ", H.bold("Koren"), " follows the p-trad."],
    " Along the way it transcribes one of Koren's own notes"
    " — not to establish the claim, but to show"
    " how conscious Koren is of the choice it makes.",
)


def _figure(src: str, alt: str, caption: object, *, width: str | None) -> object:
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


def _body_scans() -> tuple[object, ...]:
    """The two body-text scans that establish the finding: Koren's Exodus Decalogue in the running
    text (p-trad תחתון, p. 113) and the same Decalogue reprinted in the appendix (p-trad עליון,
    p. 38).  These are the body text the page otherwise only asserts."""
    return (
        _figure(
            _P113_BODY_IMG,
            "Koren p. 113: the Exodus Decalogue in the running text, in the p-trad taḥton",
            (
                "The start of Koren's Exodus (Yitro) Decalogue in the running text (p. 113), in"
                f" the p-trad {_TAHTON}. The אנכי…עבדים unit is its own chanted verse, closing on"
                " עבדים with a",
                *[" ", _ROM_SILLUQ_SOF_PASUQ, " ("],
                "עֲבָדִֽים׃",
                ").",
            ),
            width=None,
        ),
        _figure(
            _P38_BODY_IMG,
            "Koren appendix p. 38: the Exodus Decalogue in the elyon",
            (
                "The same Decalogue reprinted in Koren's appendix (p. 38), in the p-trad"
                f" {_ELYON}. Here אנכי…עבדים is merged into the long opening verse — it ends on a",
                *[" ", _ROM_REVIA, ","],
                " not on its own verse. A note on this page, citing רוו״ה, points to the",
                f" {_TAHTON} reading of the First Commandment; it is transcribed below.",
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
                "Koren follows the p-trad for the Decalogue. In its ",
                H.bold("Exodus"),
                " (Yitro) Decalogue, Koren runs the p-trad",
                f" {_TAHTON} in the running text (p. 113) and gives the p-trad {_ELYON} in an"
                " appendix (p. 38). Since no digital Koren exists, I established this by"
                " visually spot-checking Koren against ",
                link("Hebrew Wikisource's p-trad", _wikisource_ptrad_href(source)),
                ". The two scans below reproduce that body text — Koren's own running-text and"
                " appendix Decalogues.",
            )
        ),
        *_body_scans(),
    )


# The Koren note, following the scan's own two line breaks. It is unpointed prose (no cantillation),
# so unlike the Simanim transcriptions there is no hand-set pointed verse to check. רוו״ה carries a
# gershayim (U+05F4); the quoted lemma "מבית עבדים" reproduces the note's own straight quotes.
_P38_NOTE_LINES = (
    'לדעת רוו״ה, יש לקרוא את הדיבר הראשון עד "מבית עבדים"',
    "בטעם התחתון.",
)


def _p38_note_section() -> tuple[object, ...]:
    return (
        H.heading_level_2("Note on the appendix (עליון) Decalogue — Koren p. 38"),
        H.para(
            (
                "A note on the appendix Decalogue, keyed to the opening commandment אנכי…עבדים and"
                " citing רוו״ה.",
            )
        ),
        _figure(
            _P38_NOTE_IMG,
            "Koren appendix p. 38: note on the elyon Decalogue’s אנכי…עבדים unit",
            (
                "Koren, appendix p. 38 — the note on the",
                f" {_ELYON} Decalogue, citing רוו״ה.",
            ),
            width=None,
        ),
        H.heading_level_3("Transcription"),
        H.blockquote(
            _lines_with_breaks(_P38_NOTE_LINES),
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
                        " is our editorial addition. That includes the expansion of the siglum"
                        " רוו״ה, which we ",
                        H.bold("tentatively"),
                        " read as ר' וולף היידנהיים (R. Wolf Heidenheim) — the grammarian whose"
                        " editions fixed much of the printed dual-cantillation norm, so the"
                        " likeliest referent here, though we have not confirmed the expansion."
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
                " reading is one of the ",
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
                "Koren follows the p-trad for the Decalogue, not the m-trad. The two traditions'"
                " most consequential divergence is at the opening commandment אנכי…עבדים, and"
                " Koren lands on the p-trad side of that divergence on both strands: the p-trad ",
                _TAHTON,
                " in its ",
                H.bold("Exodus"),
                f" running text (p. 113), and the p-trad {_ELYON} in its appendix (p. 38).",
            )
        ),
        H.para(
            (
                "A closing, more-for-fun observation — the same one the ",
                link("Simanim page", _SIMANIM_PAGE),
                " makes. It is somewhat ",
                H.bold("editorially conservative"),
                " to keep p-trad Decalogues at all, where more recent Bibles have moved toward the"
                f" m-trad {_ELYON} and m-trad {_TAHTON}. Koren straddles old and new rather"
                " pervasively; the רוו״ה note above is one glimpse of that — it sets Koren's"
                " printed ",
                _ELYON,
                " against the standalone-verse alternative it declines to print.",
            )
        ),
        H.para(
            (
                "One scope note: the finding above rests on the אנכי…עבדים unit — the most striking"
                " p-trad/m-trad divergence — in Koren's ",
                H.bold("Exodus"),
                " (Yitro) Decalogue. I have not here checked Koren's ",
                H.bold("Deuteronomy"),
                " (Vaetḥanan) Decalogue, so the claim is made for the Exodus Decalogue"
                " specifically, not asserted for both.",
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
                " (עשרת הדברות בסיס/טעמים). This page's own content is the Koren note"
                " transcription, hand-set from the committed scans of the Koren Tanakh and"
                " credited to Koren.",
            )
        ),
    )


def render_body_contents(source: dict) -> tuple[object, ...]:
    return (
        *_intro(source),
        *_p38_note_section(),
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
