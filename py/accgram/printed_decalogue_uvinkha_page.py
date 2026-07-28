r"""Generate gh-pages/accgram/printed-decalogue-uvinkha.html -- the editions cited at ובנך.

A record page, not an argument page.  MAM-basics issue #208 asks whether Hebrew Wikisource's
p-trad עליון is right to have a meteg and a maqaf on ובנך in the Exodus Decalogue's Shabbat
commandment, where Koren's Classic Tanakh and the Simanim Tiqqun each have a munax instead --
the two editions transcribed for issue #69, whose verdicts the trio's satellite pages carry.
A reply in that thread answers it by citing eight printed editions plus Minxat Shai, each by an
archive.org or Al-Hatorah link.  This page holds those links, with a crop of each page where a
crop has been taken, so a reader can check a citation without opening nine scans.

The argument stays in the issue and is deliberately NOT reproduced here: this page states the
disagreement in one paragraph, says how the reply reads the editions, and then does nothing but
cite and show.  Captions are short by design -- name the edition and say what part of the page
the crop is, and let the reader look.  Do not grow them into readings of the marks; the crops are
low-resolution and the issue is where a reading belongs.

Five editions (Hahn, Leeser, MG Warsaw, Letteris, MG Venice) have no crop recorded yet, and the
page says so per edition rather than silently omitting them.  To add one, drop the PNG in
gh-pages/accgram/img/ under the same ``<Edition>-Ex-Dec-Shabbat-uvinkha`` naming and add a
``_Crop`` to that edition's tuple.

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import NamedTuple

from accgram import printed_decalogue_strands as pds
from accgram import rtms_report
from accgram.almost_errors_html_shared import link
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance
from py_html import wlc_utils_html as H
from py_html.my_html_span_romanized import rmn

import repo_paths

PAGE_TITLE = "What printed editions have at ובנך"

_WIDTH_CLASS = "goerwitz-tms-width-limited"

_ISSUE_URL = "https://github.com/bdenckla/MAM-basics/issues/208"
_REPLY_URL = f"{_ISSUE_URL}#issuecomment-5092090523"

# The Wikisource revision adding the note the reply asked for, linked from the closing paragraph.
_NOTE_DIFF_URL = (
    "https://he.wikisource.org/w/index.php"
    "?title=%D7%A9%D7%9E%D7%95%D7%AA_%D7%9B/%D7%98%D7%A2%D7%9E%D7%99%D7%9D"
    "&curid=236217&diff=3027539&oldid=2987656"
)

_HUB_PAGE = "printed-decalogue.html"
_KOREN_PAGE = "printed-decalogue-koren.html"
_SIMANIM_PAGE = "printed-decalogue-simanim.html"

# Strand names in Hebrew letters, single-sourced in pds (see its module docstring).
_TAHTON = pds.TAHTON
_ELYON = pds.ELYON

# Romanized mark names, each pre-wrapped ONCE in <span class="romanized"> (italic), same rule as
# the rest of the printed-Decalogue pages: splice these into a contents tuple, never into an
# f-string, and never retype the spellings inline.
_ROM_MAQAF = rmn(pds.ROM_MAQAF)
_ROM_METEG = rmn(pds.ROM_METEG)
_ROM_MUNAX = rmn(pds.ROM_MUNAX)
_ROM_TELISHA_GEDOLAH = rmn(pds.ROM_TELISHA_GEDOLAH)


class _Crop(NamedTuple):
    """One scan crop: the file in gh-pages/accgram/img/, plus its alt text and caption."""

    file: str
    alt: str
    caption: str


class _Edition(NamedTuple):
    """One cited edition: its name, how the cited item identifies it, the link, and its crops."""

    name: str
    detail: str
    url: str
    crops: tuple[_Crop, ...]


class _Group(NamedTuple):
    """One of the reply's three groups of editions, with the sentence that introduces it.

    ``heading`` is a contents tuple rather than a str so a romanized mark name in it goes
    through the same italic ``rmn`` wrapper as one in the prose -- a heading is prose too.
    """

    heading: tuple[object, ...]
    intro: tuple[object, ...]
    editions: tuple[_Edition, ...]


_MUNAX_ONLY = (
    _Edition(
        "Heidenheim",
        "Torah with Meor Einayim, Rödelheim, 1818–1821",
        "https://archive.org/details/"
        "heidenheim-torah-maor-enayim-rodelheim-1818-1821-images/page/n424/mode/1up",
        (
            _Crop(
                "Heidenheim-Ex-Dec-Shabbat-uvinkha.png",
                "Heidenheim: the Shabbat commandment's line at uvinkha uvitekha",
                "Heidenheim's line at the Shabbat commandment.",
            ),
        ),
    ),
    _Edition(
        "MG Netter",
        "Mikraot Gedolot, Vienna, 1859",
        "https://archive.org/details/"
        "mikraot-gedolot-vienna-1859-full-images/page/n551/mode/1up",
        (
            _Crop(
                "MG-Netter-Ex-Dec-Shabbat-uvinkha-1-of-2.png",
                "MG Netter: the line ending at uvinkha",
                "The line ends at ובנך.",
            ),
            _Crop(
                "MG-Netter-Ex-Dec-Shabbat-uvinkha-2-of-2.png",
                "MG Netter: uvitekha at the start of the next line",
                "ובתך picks up on the next line.",
            ),
        ),
    ),
    _Edition(
        "Ginsburg",
        "Tanakh, 1926, volume 1 (Pentateuch)",
        "https://archive.org/details/ginsburg-tanakh-1926-images/"
        "Ginsburg_Tanakh_1926_V1_Pentateuch_images/page/n121/mode/1up",
        (
            _Crop(
                "Ginsburg-Ex-Dec-Shabbat-uvinkha-1-of-3.png",
                "Ginsburg: the main text at uvinkha uvitekha",
                "Ginsburg's main text at the Shabbat commandment.",
            ),
            _Crop(
                "Ginsburg-Ex-Dec-Shabbat-uvinkha-2-of-3.png",
                "Ginsburg: the two headings of the variant apparatus",
                "The two headings of the variant apparatus on the same page.",
            ),
            _Crop(
                "Ginsburg-Ex-Dec-Shabbat-uvinkha-3-of-3.png",
                "Ginsburg: the apparatus line covering this stretch, in both columns",
                "The apparatus line covering this stretch, in both columns.",
            ),
        ),
    ),
)


_MUNAX_AND_MAQAF = (
    _Edition(
        "Hahn",
        "Biblia Hebraica",
        "https://archive.org/details/bibliahebraicaad00hahn/page/87/mode/1up",
        (),
    ),
    _Edition(
        "Leeser",
        "Tanakh, Jaquett, Philadelphia, 1878",
        "https://archive.org/details/"
        "tanakh-leeser-jaquett-philadelphia-1878-images/page/n153/mode/1up",
        (),
    ),
    _Edition(
        "MG Warsaw",
        "Mikraot Gedolot, Warsaw, 1874–1885",
        "https://archive.org/details/"
        "mikraot-gedolot-warsaw-1874-1885-full-images/page/n451/mode/1up",
        (),
    ),
    _Edition(
        "Letteris",
        "Tanakh",
        "https://archive.org/details/Letteris_Tanakh/page/n127/mode/1up",
        (),
    ),
)


_MINXAT_SHAI_AND_VENICE = (
    _Edition(
        "Minḥat Shai",
        "at Exodus 20:13, in the Al-Hatorah rendering",
        "https://mg.alhatorah.org/Parshan/Minchat_Shai/Shemot/20.13#m7e_he_he_n6",
        (
            _Crop(
                "Minxat-Shai-Ex-Dec-Shabbat-uvinkha-1-of-2.png",
                "Minhat Shai: the two column headings",
                "The two column headings.",
            ),
            _Crop(
                "Minxat-Shai-Ex-Dec-Shabbat-uvinkha-2-of-2.png",
                "Minhat Shai: the two columns' text at uvinkha uvitekha",
                "The two columns' text at the same place.",
            ),
        ),
    ),
    _Edition(
        "MG Venice",
        "the Second Rabbinic Bible, Venice, 1525",
        "https://archive.org/details/"
        "second-rabbinic-bible-venice-1525-color-full-images/page/n182/mode/1up",
        (),
    ),
)


def _groups() -> tuple[_Group, ...]:
    return (
        _Group(
            ("A ", _ROM_MUNAX, " and no ", _ROM_MAQAF),
            (
                "These three have a single accent on ובנך, a ",
                _ROM_MUNAX,
                ". On the reply's reading that means both strands have the ",
                _ROM_MUNAX,
                " there and neither has a ",
                _ROM_MAQAF,
                ". Koren, one of the two editions above, follows Heidenheim. Ginsburg's"
                " apparatus has no entry at this word, which the reply notes as surprising"
                " in an edition meant to document departures from MG Venice.",
            ),
            _MUNAX_ONLY,
        ),
        _Group(
            ("A ", _ROM_MUNAX, " and a ", _ROM_MAQAF),
            (
                "These four have both marks on ובנך, which leaves the ",
                _ROM_MUNAX,
                " to one strand and the ",
                _ROM_MAQAF,
                " to the other — the division Wikisource's pair of strands has.",
            ),
            _MUNAX_AND_MAQAF,
        ),
        _Group(
            ("Minḥat Shai, and MG Venice",),
            (
                "Minḥat Shai distinguishes the two strands at this word: a ",
                _ROM_METEG,
                f" in the {_ELYON}, with the ",
                _ROM_MAQAF,
                " implied, against a ",
                _ROM_MUNAX,
                f" in the {_TAHTON}. In this he follows the reading of MG Venice, and that"
                " reading leaves room for the ",
                _ROM_METEG,
                f" in the {_ELYON}. The reply takes this to decide the question in favour of"
                " Wikisource's present text, while wanting a note alongside it.",
            ),
            _MINXAT_SHAI_AND_VENICE,
        ),
    )


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue-uvinkha.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the ובנך editions page.",
    )


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(PAGE_TITLE),
        H.para(
            (
                "At the Shabbat commandment of the Exodus Decalogue, Hebrew Wikisource's"
                f" printed-tradition {_ELYON} has a ",
                _ROM_METEG,
                " and no accent on ובנך, joined by ",
                _ROM_MAQAF,
                " to ובתך, which has the ",
                _ROM_TELISHA_GEDOLAH,
                ": one chanted word. Koren's Classic Tanakh and the Simanim Tiqqun each have"
                " a ",
                _ROM_MUNAX,
                " on ובנך and no ",
                _ROM_MAQAF,
                ": two chanted words. So the disagreement is an exchange at the last rung of"
                " the accents' own scale — a ",
                _ROM_MAQAF,
                " on one side against a ",
                _ROM_MUNAX,
                " on the other — and since ",
                _ROM_MUNAX,
                " is conjunctive, the disjunctive skeleton is the same either way.",
            )
        ),
        H.para(
            (
                "The question is asked, and argued out, at ",
                link("MAM-basics issue #208", _ISSUE_URL),
                ". This page does not repeat that argument. It records the editions cited"
                " in ",
                link("the reply in that thread", _REPLY_URL),
                ", with a crop of each page where one has been taken, so a citation can be"
                " checked without opening nine scans.",
            )
        ),
        H.para(
            (
                "The reply's premise is that these editions have the Exodus Decalogue with"
                " the marks of both strands together, so that what stands on ובנך in one of"
                " them is evidence about both strands at once. It sorts them accordingly,"
                " and the three sections below follow its sorting.",
            )
        ),
        H.para(
            (
                "The two editions the question started from were transcribed accent by"
                " accent for ",
                link("this repository's printed-Decalogue pages", _HUB_PAGE),
                ", which carry the per-Decalogue verdicts for ",
                link("Koren", _KOREN_PAGE),
                " and for ",
                link("the Simanim Tiqqun", _SIMANIM_PAGE),
                ", and where the scale this page's opening paragraph invokes is stated in"
                " full.",
            )
        ),
    )


def _figure(crop: _Crop) -> object:
    # class="ink-on-white" opts the scan into the stylesheet's dark-mode CSS inversion. Every
    # image on this page is black ink on white paper (printed pages and a screen rendering of
    # one), so it is unconditional here -- unlike the manuscript photos elsewhere in the tree,
    # which are ink on parchment and must NOT invert. See the rule's comment in style.css.
    img_node = H.img(
        {"src": f"img/{crop.file}", "alt": crop.alt, "class": "ink-on-white"}
    )
    return H.figure(
        (
            H.para(img_node, {"class": "goerwitz-tms-image"}),
            H.figcaption(crop.caption, {"class": "goerwitz-tms-image-caption"}),
        ),
        {"class": "goerwitz-tms-figure"},
    )


def _edition_block(edition: _Edition) -> tuple[object, ...]:
    out: list[object] = [
        H.heading_level_3((link(edition.name, edition.url), f" — {edition.detail}"))
    ]
    if edition.crops:
        out.extend(_figure(crop) for crop in edition.crops)
    else:
        out.append(H.para(H.em("No crop recorded yet.")))
    return tuple(out)


def _group_block(group: _Group) -> tuple[object, ...]:
    out: list[object] = [H.heading_level_2(group.heading), H.para(group.intro)]
    for edition in group.editions:
        out.extend(_edition_block(edition))
    return tuple(out)


def _closing() -> tuple[object, ...]:
    return (
        H.heading_level_2("Since then"),
        H.para(
            (
                "The note the reply asked for has been added at Wikisource: see ",
                link("the revision that adds it", _NOTE_DIFF_URL),
                ".",
            )
        ),
    )


def render_body_contents() -> tuple[object, ...]:
    sections: list[object] = [*_intro()]
    for group in _groups():
        sections.extend(_group_block(group))
    sections.extend(_closing())
    return (H.div(tuple(sections), {"class": _WIDTH_CLASS}),)


def run(args: argparse.Namespace) -> None:
    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    H.write_html_to_file(
        body_contents=render_body_contents(),
        write_ctx=H.WriteCtx(
            title=PAGE_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    n_editions = sum(len(group.editions) for group in _groups())
    n_crops = sum(len(ed.crops) for group in _groups() for ed in group.editions)
    print(f"HTML: {html_out} ({n_editions} editions, {n_crops} crops)")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
