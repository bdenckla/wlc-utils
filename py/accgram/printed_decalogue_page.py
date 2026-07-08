r"""Generate gh-pages/accgram/printed-decalogue.html -- the printed-tradition Decalogue
grammaticality report (issue #52).

Companion to the dual-cantillation work of issue #36 (which grammar-checks the *manuscript*
taxton/elyon threads by detangling WLC): this page reports whether the *printed* editions'
(דפוסים) taxton and elyon accentuations of the two Decalogues parse under the same prose
grammar checker.  It renders live from ``printed_decalogue.check_all`` over the vendored
readings, so it can never drift from the checker's real behaviour.

Run via ``main_accgram.py generate-html``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import printed_decalogue as pd
from accgram import rtms_report
from accgram.almost_errors_html_shared import hbo, link, wrap_hebrew_runs
from cmn.utf8_io import force_utf8_io
import wlc_provenance as provenance

from py_html import wlc_utils_html as H

import repo_paths

REPORT_TITLE = "Are the printed Decalogue cantillations grammatical?"
_WIDTH_CLASS = "goerwitz-narrow"

_ISSUE_36 = "https://github.com/bdenckla/wlc-utils/issues/36"
_ISSUE_52 = "https://github.com/bdenckla/wlc-utils/issues/52"
_GOERWITZ = "goerwitz.html"
_SOURCE_URL = "https://he.wikisource.org/wiki/עשרת_הדברות_בסיס/טעמים"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_paths.gh_pages_dir() / "accgram" / "printed-decalogue.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=pd.default_source_path())
    parser.add_argument("--html-out", type=Path, default=default_html_out_path(repo_root))


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def _by_key(results: list[pd.VersionResult]) -> dict[tuple[str, str, str], pd.VersionResult]:
    return {(vr.book, vr.reading, vr.tradition): vr for vr in results}


def _intro() -> tuple[object, ...]:
    return (
        H.heading_level_1(REPORT_TITLE),
        H.heading_level_2("The question"),
        H.para(
            (
                "The two Decalogues (Exodus 20 and Deuteronomy 5) are each chanted two ways: "
                "the ",
                hbo("טעם תחתון"),
                " (taxton, “lower”) division into ordinary-length verses, and the ",
                hbo("טעם עליון"),
                " (elyon, “upper”) division by commandment, which makes the short "
                "prohibitions (murder, adultery, theft) their own tiny verses and folds long "
                "passages into single long ones. ",
                link("Issue #36", _ISSUE_36),
                " grammar-checked the ",
                H.bold("Tiberian-manuscript"),
                " (WLC / MAM) taxton and elyon threads by detangling WLC’s dual "
                "cantillation. This page (",
                link("issue #52", _ISSUE_52),
                ") asks the companion question for the ",
                H.bold("printed editions"),
                " (",
                hbo("דפוסים"),
                ", also Koren and Simanim): fed through the very same prose grammar checker, "
                "are their taxton and elyon accentuations grammatical too?",
            )
        ),
        H.para(
            (
                "Unlike the manuscript thread, the printed and manuscript readings are already "
                "single cantillation, spelled out word-for-word on the Wikisource base page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                ". Each chanted verse (delimited by its own sof pasuq) is fed through the "
                "shared pipeline — a leading verse-start token, the prose scanner, then the "
                "prose PLY grammar — exactly as issue #36 does. The manuscript versions are "
                "the baseline (MAM’s own authoritative text, expected all clean); the printed "
                "versions are the object of study.",
            )
        ),
    )


def _cell(vr: pd.VersionResult) -> object:
    n = len(vr.chanted_verses)
    bad = vr.ungrammatical
    if not bad:
        return H.table_datum(f"✓ all {n} clean", {"class": "clean"})
    which = ", ".join(f"verse {cv.index}" for cv in bad)
    return H.table_datum(
        f"✗ {len(bad)} of {n} ungrammatical ({which})", {"class": "ungrammatical"}
    )


def _verdict_table(by_key: dict) -> object:
    header = H.table_row_of_headers(("", "Tiberian manuscript", "Printed editions"))
    rows = [header]
    for book in ("ex", "dt"):
        for reading in ("taxton", "elyon"):
            label = f"{pd.BOOK_LABELS[book]} — {pd.READING_LABELS[reading]}"
            rows.append(
                H.table_row(
                    (
                        H.table_header(label),
                        _cell(by_key[(book, reading, "manuscript")]),
                        _cell(by_key[(book, reading, "printed")]),
                    )
                )
            )
    return H.table(tuple(rows), {"class": "printed-decalogue-verdict"})


def _verdict_section(by_key: dict) -> tuple[object, ...]:
    return (
        H.heading_level_2("The verdict"),
        _verdict_table(by_key),
        H.para(
            (
                H.bold("taxton"),
                " is grammatical everywhere — both books, both traditions. The printed "
                "taxton differs from the manuscript only in details that do not touch the "
                "accent grammar (vocalization such as ",
                hbo("תִּרְצַח"),
                " vs ",
                hbo("תִּרְצָח"),
                " at “you shall not murder,” and where a maqaf or ga‘ya falls), and "
                "in one verse boundary: the printed taxton ends its first verse at ",
                hbo("מבית עבדים"),
                " (so it has one more verse than the manuscript, which runs the first two "
                "commandments together). Both parse clean.",
            )
        ),
        H.para(
            (
                H.bold("elyon"),
                " is grammatical in the manuscript but ",
                H.bold("not"),
                " in the printed editions: the printed elyon of ",
                H.bold("each"),
                " Decalogue has exactly one ungrammatical chanted verse — its opening one.",
            )
        ),
    )


def _accent_backbone(cv: pd.ChantedVerseResult) -> str:
    """The disjunctive backbone of a chanted verse: its accent tokens, lower-cased, with the
    non-accent framing tokens dropped."""
    skip = {"TILDE", "SOFPASUQ", "MISSING_SOFPASUQ"}
    return " · ".join(t.lower() for t in cv.tokens if t not in skip)


def _finding_section(by_key: dict) -> tuple[object, ...]:
    ex_printed = by_key[("ex", "elyon", "printed")]
    ex_ms = by_key[("ex", "elyon", "manuscript")]
    offender = ex_printed.ungrammatical[0]
    ms_cmd1, ms_cmd2 = ex_ms.chanted_verses[0], ex_ms.chanted_verses[1]
    return (
        H.heading_level_2("Why the printed elyon fails: the merged first verse"),
        H.para(
            (
                "In the manuscript elyon, the first commandment ",
                hbo("אָנֹכִי … עֲבָדִים"),
                " is its own chanted verse, and “you shall have no other gods …” begins "
                "the next — two separate verses, ",
                H.bold("both of which parse clean"),
                ". The printed editions instead merge the first two commandments into a single "
                "verse (nine chanted verses in all, against the manuscript’s ten). That one "
                "merged verse is what the grammar rejects:",
            )
        ),
        H.blockquote(wrap_hebrew_runs(" ".join(offender.words)), {"lang": "hbo"}),
        H.para(
            (
                "Its accent backbone is ",
                H.code(_accent_backbone(offender)),
                ". The single etnaḥta falls at ",
                hbo("לְשֹׂנְאָי"),
                ", leaving an over-long first half that carries a segolta plus three separate "
                "revia domains (at ",
                hbo("עֲבָדִים"),
                ", ",
                hbo("עַל־פָּנַי"),
                ", and ",
                hbo("לָאָרֶץ"),
                "); the prose grammar cannot build it and returns a ",
                H.code("pashta_phrase"),
                " error — the same failure, at the same structural point, in both Decalogues.",
            )
        ),
        H.para(
            (
                "The cause is the merged ",
                H.bold("structure"),
                ", not sheer length: Deuteronomy’s printed elyon Sabbath verse runs 55 words "
                "and parses clean, while this merged verse (51 words) does not. Keeping the two "
                "commandments as the manuscript’s two separate verses (",
                f"{len(ms_cmd1.words)} and {len(ms_cmd2.words)} words) ",
                "is exactly what lets them parse.",
            )
        ),
        H.para(
            (
                "The manuscript elyon’s own single ungrammatical verse — Deuteronomy 5:8, a "
                "WLC-specific accent bug — is unrelated; it is discussed among the ",
                link("ungrammatical verses", _GOERWITZ),
                ". Here MAM’s manuscript elyon parses clean throughout.",
            )
        ),
    )


def _provenance_section(source: dict) -> tuple[object, ...]:
    prov = source.get("provenance", {})
    oldid = prov.get("oldid")
    ts = prov.get("revision_timestamp", "")
    return (
        H.heading_level_2("Source"),
        H.para(
            (
                "All eight readings (two books × taxton/elyon × manuscript/printed) are "
                "taken from the Wikisource base page ",
                link("עשרת הדברות בסיס/טעמים", _SOURCE_URL),
                f" (revision {oldid}, {ts[:10]}), which every printed-vs-manuscript comparison "
                "table there transcludes. A handful of wiki templates are resolved to plain "
                "pointed text (legarmeh/paseq to a paseq mark, qere for ketiv-qere, paragraph "
                "and pisqa markers dropped); the chanted verses are split at sof pasuq.",
            )
        ),
    )


def render_body_contents(results: list[pd.VersionResult], source: dict) -> tuple[object, ...]:
    by_key = _by_key(results)
    sections: list[object] = [
        *_intro(),
        *_verdict_section(by_key),
        *_finding_section(by_key),
        *_provenance_section(source),
    ]
    wrapper = H.div(tuple(sections), {"class": _WIDTH_CLASS})
    return (wrapper,)


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
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )
    n_bad = sum(len(vr.ungrammatical) for vr in results)
    print(f"HTML: {html_out} ({len(results)} versions, {n_bad} ungrammatical)")


def main() -> None:
    force_utf8_io()
    repo_root = repo_paths.repo_root()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_root)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
