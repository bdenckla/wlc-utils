r"""Grammar-check the printed-tradition Decalogue accentuations (issue #52).

Issue #36 grammar-checks the *manuscript* (Tiberian, WLC/MAM) taxton/elyon threads of the
two Decalogues by detangling WLC's dual cantillation.  This module answers the companion
question for the *printed* tradition (דפוסים / Koren / Simanim): fed through the very same
prose grammar checker, are the printed editions' taxton and elyon accentuations grammatical
too, for both Exodus 20 and Deuteronomy 5?

Unlike #36 -- which must *detangle* WLC's two-accents-per-word source -- the printed and
manuscript readings are already single-cantillation, spelled out word-for-word on
he.wikisource ``עשרת הדברות בסיס/טעמים`` (vendored by ``printed_decalogue_fetch.py`` to
``in/accgram/printed_decalogue_teamim.json``).  So this module simply feeds each chanted
verse through the shared pipeline #36 uses -- ``uni_to_marks.verse_to_marks`` -> a leading
``TILDE`` + ``prose_scanner.scan_accents`` -> ``prose_ply_grammar.parse_tokens`` -- and
records clean / ungrammatical per chanted verse.

Both manuscript versions serve as the baseline (MAM's own authoritative text: expected all
clean); the printed versions are the object of study.  That baseline is not taken on trust:
``decalogue_m_trad`` checks all four m-trad strands, word for word and stroke for stroke,
against MAM's own parse of its own text in the sibling repo MAM-parsed's ``plus`` tree, and
they agree exactly (issue #68).  The verdict is stable and stark:

  * **taxton** parses clean in both books and both traditions;
  * **elyon** parses clean in the manuscript, but in the *printed* editions of *both*
    Decalogues exactly one chanted verse is ungrammatical -- the opening verse, where the
    printed tradition merges the first two commandments (אנכי ... through the end of the
    "jealous God" passage) into a single ~51-word verse (nine verses total, vs the
    manuscript's ten).  Its over-long pre-atnax half defeats the prose accent grammar
    (a ``pashta_phrase`` ERROR), where the manuscript -- keeping the two commandments as two
    separate chanted verses -- parses both clean.

Those are the IDEALIZED strands.  ``transcription_parse`` asks the same question of what a
real edition prints, feeding the committed hand transcriptions through ``parse_marks_body``
below -- the same scanner, grammar and status vocabulary, so the two sets of verdicts are
comparable.  Eleven of the twelve transcribed Decalogues match their strand at every chanted
verse; the one that does not is Simanim's Exodus appendix taxton.

Pure computation (no I/O); the driver (``run``) loads the vendored JSON, parses, and writes
``out/accgram/printed-decalogue/_printed_decalogue.json``.  The gh-pages report is rendered
separately by ``printed_decalogue_page``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from accgram import uni_to_marks
from accgram.dual_cant_detangle import _tree_has_error
from accgram.prose_ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.prose_scanner import HasLegarmeh, Token, scan_accents
from accgram.tree import tree_to_obj

import repo_paths

_PASEQ = "\N{HEBREW PUNCTUATION PASEQ}"


def default_source_path() -> Path:
    return repo_paths.in_dir() / "accgram" / "printed_decalogue_teamim.json"


def default_out_path() -> Path:
    return (
        repo_paths.out_dir()
        / "accgram"
        / "printed-decalogue"
        / "_printed_decalogue.json"
    )


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ChantedVerseResult:
    """One chanted verse of one version, fed to the prose grammar."""

    index: int  # 1-based position within the version
    words: tuple[str, ...]  # the vels actually scanned (paseq folded onto its word)
    body: str  # scanner mark body
    tokens: tuple[str, ...]  # token-type stream
    status: str  # clean / ungrammatical / no_parse / location_only
    tree: dict | None


@dataclass(frozen=True)
class VersionResult:
    book: str  # "ex" / "dt"
    reading: str  # "taxton" / "elyon"
    tradition: str  # "manuscript" / "printed"
    section: str  # source wikisource section name
    chanted_verses: tuple[ChantedVerseResult, ...]

    @property
    def ungrammatical(self) -> tuple[ChantedVerseResult, ...]:
        return tuple(cv for cv in self.chanted_verses if cv.status != "clean")


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #
def _to_vels(chanted_verse: str) -> list[str]:
    """Whitespace-split into vels, folding a standalone paseq onto the previous word
    (matching WLC's attached convention and #36's ``_emit_stream``)."""
    vels: list[str] = []
    for tok in chanted_verse.split():
        if tok == _PASEQ and vels:
            vels[-1] = vels[-1] + _PASEQ
        elif tok.startswith(_PASEQ) and vels:
            vels[-1] = vels[-1] + _PASEQ
            rest = tok[len(_PASEQ) :]
            if rest:
                vels.append(rest)
        else:
            vels.append(tok)
    return vels


def parse_marks_body(
    body: str, book: str, index: int, parser, words: tuple[str, ...] = ()
) -> ChantedVerseResult:
    """One scanner mark body -> its grammar verdict.

    Split out from ``_parse_chanted_verse`` so that a source which is NOT pointed Hebrew can
    reach the same pipeline: ``transcription_parse`` builds a mark body straight from a hand
    transcription's accent shorthand, and must run through this exact path -- same scanner,
    same grammar, same status vocabulary -- for its verdicts to be comparable with the
    strands' own.  ``words`` is carried only for the record; nothing keys on it.
    """
    # None of the Decalogue readings is a HasLegarmeh corpus; a fresh per-verse instance is
    # immaterial. Chapter/verse are only for scanner diagnostics, unused on this path.
    tokens = [Token("TILDE", "")] + scan_accents(body, book, 20, 2, HasLegarmeh())
    tree = parse_tokens(parser, tokens)
    if tree is None:
        status, tree_obj = "no_parse", None
    elif tree is LOCATION_ONLY:
        status, tree_obj = "location_only", None
    else:
        status = "ungrammatical" if _tree_has_error(tree) else "clean"
        tree_obj = tree_to_obj(tree)
    return ChantedVerseResult(
        index=index,
        words=words,
        body=body,
        tokens=tuple(t.type for t in tokens),
        status=status,
        tree=tree_obj,
    )


def _parse_chanted_verse(
    text: str, book: str, index: int, parser
) -> ChantedVerseResult:
    vels = _to_vels(text)
    body = uni_to_marks.verse_to_marks({"vels": vels})
    return parse_marks_body(body, book, index, parser, tuple(vels))


def load_source(source_path: Path | None = None) -> dict:
    path = source_path or default_source_path()
    return json.loads(path.read_text(encoding="utf-8"))


def check_all(source: dict, parser=None) -> list[VersionResult]:
    parser = parser or build_parser()
    results: list[VersionResult] = []
    for version in source["versions"]:
        book = version["book"]
        cvs = tuple(
            _parse_chanted_verse(text, book, i, parser)
            for i, text in enumerate(version["chanted_verses"], start=1)
        )
        results.append(
            VersionResult(
                book=book,
                reading=version["reading"],
                tradition=version["tradition"],
                section=version["section"],
                chanted_verses=cvs,
            )
        )
    return results


# --------------------------------------------------------------------------- #
# Driver
# --------------------------------------------------------------------------- #
def _version_obj(vr: VersionResult) -> dict[str, object]:
    return {
        "book": vr.book,
        "reading": vr.reading,
        "tradition": vr.tradition,
        "section": vr.section,
        "chanted_verse_count": len(vr.chanted_verses),
        "ungrammatical_count": len(vr.ungrammatical),
        "chanted_verses": [
            {
                "index": cv.index,
                "words": list(cv.words),
                "marks": cv.body,
                "tokens": list(cv.tokens),
                "status": cv.status,
                "tree": cv.tree,
            }
            for cv in vr.chanted_verses
        ],
    }


def _payload(results: list[VersionResult], source: dict) -> dict[str, object]:
    return {
        "summary": {
            "versions": len(results),
            "chanted_verses": sum(len(vr.chanted_verses) for vr in results),
            "ungrammatical": sum(len(vr.ungrammatical) for vr in results),
        },
        "source_provenance": source.get("provenance", {}),
        "versions": [_version_obj(vr) for vr in results],
    }


def add_args(parser, repo_root: Path) -> None:
    parser.add_argument("--source", type=Path, default=default_source_path())
    parser.add_argument("--out", type=Path, default=default_out_path())


def run(args) -> None:
    import wlc_provenance as provenance

    source = load_source(args.source)
    results = check_all(source)
    payload = provenance.with_json_provenance(_payload(results, source), __file__)

    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")

    s = payload["summary"]
    print(
        f"printed-decalogue: {s['versions']} versions, {s['chanted_verses']} chanted verses, "
        f"{s['ungrammatical']} ungrammatical -> {out_path}"
    )


def main() -> None:
    import argparse

    from cmn.utf8_io import force_utf8_io

    force_utf8_io()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_paths.repo_root())
    run(parser.parse_args())


if __name__ == "__main__":
    main()
