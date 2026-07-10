r"""Author tool: vendor the eight Decalogue accentuations from he.wikisource (issue #52).

Fetches ``עשרת הדברות בסיס/טעמים`` -- the base page every printed-vs-manuscript
comparison table on Wikisource transcludes -- and writes the resolved, chanted-verse-split
readings to ``in/accgram/printed_decalogue_teamim.json`` for the grammaticality checker
(``printed_decalogue.py``).

The base page spells out, fully accented, all eight versions:

    {שמות, דברים} × {טעם תחתון, טעם עליון} × {(טבריה), (דפוסים)}
    = {Exodus, Deuteronomy} × {taxton (lower), elyon (upper)} × {manuscript, printed}

Only a handful of wiki templates appear inside the accentuation sections; they are
resolved to plain pointed text so the result is scanner-ready:

  * ``{{מ:לגרמיה}}`` / ``{{מ:פסק}}``  -> a paseq (U+05C0), folded onto the preceding word
    (WLC's attached convention; a munax+paseq is then read as legarmeh by the scanner).
  * ``{{מ:קמץ|ד=X|ס=Y}}``            -> the ``ד`` (default) qamats-qatan display form ``X``.
  * ``{{כו"ק|ketiv|qere}}``          -> the qere (the accented form the reading chants).
  * paragraph / pisqa markers ``{{ססס}}`` ``{{סס2}}`` ``{{סס}}`` ``{{פפ}}`` -> dropped
    (they carry no accent; a pisqa be'emtsa pasuq sits *inside* a chanted verse, which is
    delimited only by sof pasuq).

This is a network tool run by hand to refresh the vendored snapshot; the committed JSON
records the source page's revision id and retrieval date for provenance.  Run:

    PYTHONUTF8=1 PYTHONPATH=. ../.venv/Scripts/python.exe accgram/printed_decalogue_fetch.py
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

from cmn.utf8_io import force_utf8_io

import repo_paths

PASEQ = "\N{HEBREW PUNCTUATION PASEQ}"
SOF_PASUQ = "\N{HEBREW PUNCTUATION SOF PASUQ}"

_PAGE_TITLE = "עשרת הדברות בסיס/טעמים"
_USER_AGENT = "wlc-utils/printed-decalogue (issue #52)"

# (book, reading, tradition, wikisource section name).  ``book`` is the WLC 2-char code.
_SECTIONS: tuple[tuple[str, str, str, str], ...] = (
    ("ex", "taxton", "manuscript", "שמות טעם תחתון (טבריה)"),
    ("ex", "elyon", "manuscript", "שמות טעם עליון (טבריה)"),
    ("ex", "taxton", "printed", "שמות טעם תחתון (דפוסים)"),
    ("ex", "elyon", "printed", "שמות טעם עליון (דפוסים)"),
    ("dt", "taxton", "manuscript", "דברים טעם תחתון (טבריה)"),
    ("dt", "elyon", "manuscript", "דברים טעם עליון (טבריה)"),
    ("dt", "taxton", "printed", "דברים טעם תחתון (דפוסים)"),
    ("dt", "elyon", "printed", "דברים טעם עליון (דפוסים)"),
)


def default_out_path() -> Path:
    return repo_paths.in_dir() / "accgram" / "printed_decalogue_teamim.json"


def _fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def fetch_wikitext_and_revision() -> tuple[str, dict[str, object]]:
    quoted = urllib.parse.quote(_PAGE_TITLE)
    wikitext = _fetch(f"https://he.wikisource.org/wiki/{quoted}?action=raw")
    api = (
        "https://he.wikisource.org/w/api.php?action=query&format=json&prop=revisions"
        f"&rvprop=ids|timestamp&titles={quoted}"
    )
    meta = json.loads(_fetch(api))
    page = next(iter(meta["query"]["pages"].values()))
    rev = page["revisions"][0]
    provenance = {
        "source_page": _PAGE_TITLE,
        "url": f"https://he.wikisource.org/wiki/{quoted}",
        "pageid": page.get("pageid"),
        "oldid": rev["revid"],
        "revision_timestamp": rev["timestamp"],
    }
    return wikitext, provenance


def _extract_section(text: str, name: str) -> str:
    start = f"<קטע התחלה={name}/>"
    end = f"<קטע סוף={name}/>"
    i = text.index(start) + len(start)
    j = text.index(end, i)
    return text[i:j]


def _resolve_templates(section: str) -> str:
    section = re.sub(r"<קטע התחלה=[^/]*/>", "", section)
    section = re.sub(r"<קטע סוף=[^/]*/>", "", section)
    section = section.replace("{{מ:לגרמיה}}", PASEQ + " ")
    section = section.replace("{{מ:פסק}}", PASEQ + " ")
    section = re.sub(r"\{\{מ:קמץ\|ד=([^|]*)\|ס=[^}]*\}\}", r"\1", section)
    section = re.sub(r'\{\{כו"ק\|[^|]*\|([^}]*)\}\}', r"\1", section)
    for marker in ("{{ססס}}", "{{סס2}}", "{{סס}}", "{{פפ}}", "{{פ}}"):
        section = section.replace(marker, " ")
    if "{{" in section:
        raise ValueError(f"Unresolved template remains in section: {section[:120]!r}")
    return section


def _segment_chanted_verses(section: str) -> list[str]:
    out: list[str] = []
    cur: list[str] = []
    for ch in section:
        cur.append(ch)
        if ch == SOF_PASUQ:
            out.append("".join(cur))
            cur = []
    tail = "".join(cur).strip()
    if tail:
        out.append(tail)
    return [cv for cv in (re.sub(r"\s+", " ", c).strip() for c in out) if cv]


def build_payload(wikitext: str, provenance: dict[str, object]) -> dict[str, object]:
    versions: list[dict[str, object]] = []
    for book, reading, tradition, name in _SECTIONS:
        chanted_verses = _segment_chanted_verses(_resolve_templates(_extract_section(wikitext, name)))
        versions.append(
            {
                "book": book,
                "reading": reading,
                "tradition": tradition,
                "section": name,
                "chanted_verses": chanted_verses,
            }
        )
    provenance = dict(provenance)
    provenance["resolution_notes"] = (
        "Wiki templates resolved: {{מ:לגרמיה}}/{{מ:פסק}} -> U+05C0 paseq folded onto the "
        "preceding word; {{מ:קמץ|ד=X|ס=Y}} -> X; {{כו\"ק|ketiv|qere}} -> qere; paragraph/"
        "pisqa markers dropped; inner <קטע> tags stripped. Chanted verses split at sof pasuq."
    )
    return {"provenance": provenance, "versions": versions}


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument("--out", type=Path, default=default_out_path())


def run(args: argparse.Namespace) -> None:
    wikitext, provenance = fetch_wikitext_and_revision()
    payload = build_payload(wikitext, provenance)
    out_path: Path = args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
    n_cv = sum(len(v["chanted_verses"]) for v in payload["versions"])
    print(f"printed-decalogue: {len(payload['versions'])} versions, {n_cv} chanted verses "
          f"(oldid {provenance['oldid']}) -> {out_path}")


def main() -> None:
    force_utf8_io()
    parser = argparse.ArgumentParser(description=__doc__)
    add_args(parser, repo_root=repo_paths.repo_root())
    run(parser.parse_args())


if __name__ == "__main__":
    main()
