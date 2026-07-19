r"""Generate gh-pages/accgram/printed-decalogue-koren.html -- does the Koren Tanakh follow the
printed or the manuscript Decalogue tradition?  Answer: the printed tradition.

Companion to ``printed_decalogue_simanim_page``: the same question, asked of Koren instead of
Simanim's Tiqqun.  The four cantillation strands of the opening אנכי…מצותי span are derived live
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
shows the p-trad, and where Simanim's Tiqqun does not (an accents-only departure: Simanim's Tiqqun
still follows the p-trad's chanted verse boundaries).  See the conclusion's scope note.

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

from py_html import my_html_for_img as mhi
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
# The companion's appendix cataloguing how the two תחתון strands differ (its heading id there,
# _TAHTON_DETAILS_ID) -- the reference for the Shabbat-commandment accent details this page omits.
_TAHTON_DETAILS_HREF = f"{_PRINTED_DECALOGUE_PAGE}#tahton-details"

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

# Word-highlight boxes on the p. 113 taxton scan, in the scan's own pixel space (viewbox 936x262,
# the rectified grayscale image's natural size). Picked with gen_highlight_picker.py; they mark the
# boundary words of the אנכי…עבדים span the caption discusses.
_P113_BOXES: tuple[mhi.Box, ...] = (
    mhi.Box(x=466, y=112, w=138, h=59),
    mhi.Box(x=796, y=162, w=131, h=69),
)
# Word-highlight boxes on the p. 281 Deuteronomy Shabbat scan, in the scan's own pixel space
# (viewbox 913x186, its natural size). Picked with gen_highlight_picker.py; they mark the three
# signal words the conclusion's scope note names. The middle word wraps the scan's line break
# (וְעַבְדְּךָ ends one line, וַאֲמָתֶךָ starts the next), so it is boxed on its accent-bearing half.
_P281_BOXES: tuple[mhi.Box, ...] = (
    mhi.Box(x=431, y=27, w=189, h=67),
    mhi.Box(x=791, y=92, w=118, h=73),
    mhi.Box(x=389, y=89, w=190, h=70),
)
# Word-highlight boxes on the Koren appendix p. A38 elyon scan, in the scan's own pixel space
# (viewbox 850x472, its natural size). Picked with gen_highlight_picker.py; the three boxes mark,
# in text order, the אנכי…מצותי span's two signal words, עבדים and על־פני, plus מצותי -- the span's
# shared end, marked for orientation, not as a signal (every strand closes a chanted verse there,
# so it distinguishes nothing; the p-trad elyon shown here runs the whole way to it in one verse).
# על־פני wraps the scan's line break (על ends line 2, פני starts line 3), so it is boxed on its פני
# half. This is the direct analog of the Simanim Tiqqun p. 83 elyon
# (printed_decalogue_simanim_page._P83_BOXES), which marks the same three words on its own elyon
# scan (the other Simanim scans, being taxton or m-trad, close a verse earlier and mark only the
# two signal words).
_PA38_BOXES: tuple[mhi.Box, ...] = (
    mhi.Box(x=452, y=77, w=109, h=61),  # עבדים (line 2)
    mhi.Box(x=787, y=136, w=61, h=66),  # על־פני -- its פני, start of line 3
    mhi.Box(x=205, y=381, w=123, h=62),  # מצותי (last line)
)

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
# Koren's p-trad accents on the three Shabbat-commandment signal words (issue #66), named only in
# the conclusion's scope note. The m-trad counterparts (pazer / telisha gedolah / revia) are left
# to the companion page's appendix, not repeated here. _ROM_REVIA is already defined above.
_ROM_GERESH = rmn(pds.ROM_GERESH)
_ROM_ZAQEF_QATAN = rmn(pds.ROM_ZAQEF_QATAN)

# The p-trad Decalogue on Hebrew Wikisource sits in the printed-tradition (נוסח הדפוסים) section of
# the very page these four strands are vendored from -- so its base URL is single-sourced from the
# data's own provenance, and we append only the section anchor here. (Same rule as the Simanim
# page; see its ``_wikisource_ptrad_href``.)
_WIKISOURCE_PTRAD_SECTION = "הטעם התחתון מול הטעם העליון (לפי נוסח הדפוסים)"


def _wikisource_ptrad_href(source: dict) -> str:
    base = source["provenance"]["url"]
    return f"{base}#{_WIKISOURCE_PTRAD_SECTION.replace(' ', '_')}"


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
    " document the claim that Koren follows the p-trad."
    " Along the way it transcribes one of Koren's own notes.",
)


# Every ``alt`` passed here names the strands in ROMANIZED form ("taxton"/"elyon") while the
# figcaption beside it uses Hebrew letters. That is deliberate, not drift: attribute contexts are
# exempt by design (issue #65, finding T1) -- see printed_decalogue_strands' module docstring.
def _figure(
    src: str,
    alt: str,
    caption: object,
    *,
    width: str | None,
    boxes: tuple[mhi.Box, ...] | None = None,
    viewbox: tuple[int, int] | None = None,
) -> object:
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
    # When boxes are given, the <img> is wrapped in a positioned <div> alongside an inline-SVG
    # word-highlight overlay (my_html_for_img.annotated_img). The overlay is a sibling of the
    # img, so the img's dark-mode invert never touches it -- see the .scan-annot rules and the
    # ink-on-white comment in style.css. class="ink-on-white" stays on the img either way.
    if boxes:
        assert viewbox is not None, "boxes require a viewbox=(w, h)"
        img_node = mhi.annotated_img(
            img_attr, boxes, viewbox_w=viewbox[0], viewbox_h=viewbox[1]
        )
    else:
        img_node = H.img(img_attr)
    return H.figure((img_node, H.figcaption(caption)))


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
                f" the p-trad {_TAHTON}. אנכי…עבדים is its own chanted verse — the signal word"
                " עבדים closes it with a",
                *[" ", _ROM_SILLUQ_SOF_PASUQ, "."],
            ),
            width=None,
            boxes=_P113_BOXES,
            viewbox=(936, 262),
        ),
        _figure(
            _PA38_BODY_IMG,
            "Koren appendix p. A38: the Exodus appendix Decalogue in the elyon",
            (
                "The start of Koren's Exodus appendix Decalogue (p. A38), in the p-trad"
                f" {_ELYON}. Both signal words have a",
                *[" ", _ROM_REVIA, " — the p-trad ", _ELYON, "'s pair."],
                " The verse runs on to the highlighted מצותי, the אנכי…מצותי span's shared end.",
            ),
            width=None,
            boxes=_PA38_BOXES,
            viewbox=(850, 472),
        ),
    )


def _intro(source: dict) -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.para(_PARA_1),
        H.para(_PARA_2),
        H.para(
            (
                "Koren follows the p-trad for the Decalogues. In its Exodus"
                " Decalogue, Koren's main Decalogue (p. 113) is the p-trad"
                f" {_TAHTON} and its appendix Decalogue (p. A38) is the p-trad {_ELYON}"
                ". Since no digital Koren exists, I established this by"
                " visually spot-checking Koren against ",
                link("Hebrew Wikisource's p-trad", _wikisource_ptrad_href(source)),
                ". The two scans below show enough of Koren's Exodus Decalogues to"
                ' "diagnose" them both as p-trad.',
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
                        " text in {curly braces} is my editorial addition. That includes the"
                        " expansion of the abbreviation רוו״ה, which I tentatively"
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
                _ELYON,
                " by default — the merged, nine-verse p-trad structure, in which אנכי…עבדים ends"
                " on a ",
                _ROM_REVIA,
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
                " — through עבדים; at the span's other signal word, על־פני, the two part). So"
                " Koren, like Simanim, prints the p-trad structure as the norm and files the"
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
                " most consequential divergence is over the opening span אנכי…מצותי — a"
                " divergence of chanted verse boundaries, which can be read off the accents on"
                " the span's two signal words, עבדים and על־פני. Koren lands on the p-trad side of"
                " that divergence on both strands: the p-trad ",
                _TAHTON,
                " in its Exodus",
                f" main Decalogue (p. 113), and the p-trad {_ELYON} in its appendix Decalogue"
                " (p. A38).",
            )
        ),
        H.para(
            (
                "One scope note: the finding above rests on the אנכי…מצותי span — the most striking"
                " p-trad/m-trad divergence. Koren makes the same p-trad choice at that span in both"
                " of its Decalogues: the Exodus one and the",
                f" Deuteronomy (Vaetḥanan) one, whose {_TAHTON} main Decalogue starts on p. 280"
                " and runs onto"
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
                " finds Simanim's Tiqqun following the m-trad accents at that very commandment"
                " (an accents-only departure — Simanim's Tiqqun still follows the p-trad's"
                " chanted verse boundaries). So Koren happens to be pure p-trad at both"
                " divergence points, where Simanim's Tiqqun is not — and it is exactly that"
                " kind of impurity the Shabbat commandment's own signal words exist to catch,"
                " since an accents-only departure moves no chanted verse boundary and so leaves"
                " עבדים and על־פני reading p-trad throughout. The scan"
                " below is that commandment, with "
                # Single-sourced in pds and shared with the Simanim page's matching scope note;
                # the complementary-jobs doctrine is spelled out at that constant.
                + pds.SHABBAT_SIGNAL_SHORTHAND
                + ". In Koren's p-trad they have, respectively, a ",
                _ROM_GERESH,
                ", a ",
                _ROM_REVIA,
                ", and a ",
                _ROM_ZAQEF_QATAN,
                "; the ",
                link("companion page's appendix", _TAHTON_DETAILS_HREF),
                " has the full details. One boundary on all this: what I have checked in"
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
                f" (p. 281), in the p-trad {_TAHTON}. The three signal words are highlighted.",
            ),
            width=None,
            boxes=_P281_BOXES,
            viewbox=(913, 186),
        ),
    )


def render_body_contents(source: dict) -> tuple[object, ...]:
    return (
        *_intro(source),
        *_pa38_note_section(),
        *_conclusion(),
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
    # readings -- it only needs the source's provenance (the p-trad section URL). We load
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
