"""Check a hand transcription against its vendored strand, before it is committed.

Usage:
    # a transcription still in progress, from the editor's downloaded exports
    .venv/Scripts/python.exe py/accgram/transcription_check.py \
        ~/Downloads/simanim_dt_elyon_p208-transcription.json ... --key dt elyon printed

    # one already committed, taking its strand from the .txt header
    .venv/Scripts/python.exe py/accgram/transcription_check.py --stem simanim_dt_elyon

    # what all eight strands do at one site, located by letter skeleton
    .venv/Scripts/python.exe py/accgram/transcription_check.py --site השבת לקדשו

This is the loop that runs between the transcriber typing a page and the transcription being
committed: resolve what was typed, align it against the strand, and report every difference
WITH the printed page and line it came from, so the page can be re-read at that spot.

THREE THINGS IT REPORTS, AND WHY EACH IS SEPARATE:

* Differences, with the reference word each sits on.  Not every difference is a cantillation
  difference -- where the two texts divide words differently the marking usually follows -- so
  the word is printed alongside and the classification stays a human judgement.
* Chanted verse boundaries, counted on both sides AND checked for difference regions touching
  a silsof.  A bare count would miss one boundary moving while another appeared.
* Vertical strokes.  The vendored data folds legarmeh and narrow-sense paseq onto U+05C0, so
  it can only say WHERE one stands; the transcription says WHICH.  Comparing the placements is
  the part that can be checked today, and it doubles as an alignment check: these are
  independent anchors, so several landing on their exact indices rules out a drifting diff.

An unresolvable abbreviation is held as ``???`` rather than guessed, so the alignment still
runs and the reference's own token at that spot can be shown as CONTEXT for the transcriber's
decision -- never as a substitute for it.  Reading the accents is the transcriber's job; this
tool displays, aligns and reports.

BEWARE the asymmetry this loop has.  It flags only positions where the two already disagree,
so only those get re-read.  A "no divergences" result means no divergence survived a procedure
that never inspects the agreeing majority, and compensating errors are possible in exactly
this material -- see the Exodus elyon's two cancelling divergences in wlc-utils#69.
"""

from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parent.parent)
)  # run directly as a script

sys.stdout.reconfigure(encoding="utf-8")

from accgram import edition_transcription as et  # noqa: E402
from accgram import printed_decalogue as pd  # noqa: E402
from accgram import printed_decalogue_strands as pds  # noqa: E402

MAQAF = "\N{HEBREW PUNCTUATION MAQAF}"
UNRESOLVED = "???"


def _pages_of(record: dict) -> list[dict]:
    """A multi-page audit trail holds one export per page; a single-page one is its own page."""
    return record.get("pages", [record])


def _chunks_with_origin(pages: list[dict]) -> list[tuple[str, str, int]]:
    """(chunk, page label, printed line) in reading order, asides kept in place.

    Two things have to be undone here exactly as ``hebrew_chunks`` undoes them, or the token
    stream silently misaligns: the editor records a multi-accent maqaf compound with a literal
    maqaf between its accents, and when such a compound straddles a printed line break its
    accents arrive on two different lines.  A chunk left ending in a maqaf therefore takes the
    following chunk with it -- and keeps the origin of the line it STARTED on, which is the
    line to go back and re-read.
    """
    out: list[tuple[str, str, int]] = []
    for page in pages:
        label = page.get("stem", "?").split("_")[-1]
        for line in page["lines"]:
            for written in line["text"].split():
                if written.startswith("["):
                    out.append((written, label, line["n"]))
                elif out and out[-1][0].endswith(MAQAF):
                    previous, prev_label, prev_line = out[-1]
                    out[-1] = (previous + written, prev_label, prev_line)
                else:
                    out.append((written, label, line["n"]))
    return out


def _tokens_with_origin(pages: list[dict]) -> tuple[list[str], list[tuple[str, int]]]:
    """Latin tokens in reading order, each with the (page, printed line) it was typed on."""
    tokens: list[str] = []
    origin: list[tuple[str, int]] = []
    for chunk, label, n in _chunks_with_origin(pages):
        if chunk.startswith("["):
            continue  # a bracketed aside carries no accent
        for part in chunk.split(MAQAF):
            # A simple word may bear two accents too (qadma + geresh, the qadma then called
            # metigah), written with the SIMPLE_JOINER rather than a maqaf.  One token per
            # accent either way, so both joiners have to be split on here.
            for accent in part.split(et.SIMPLE_JOINER):
                try:
                    tokens.append(et.hebrew_token(accent))
                except ValueError as exc:
                    print(f"  !! {label} line {n}: {exc}")
                    tokens.append(UNRESOLVED)
                origin.append((label, n))
    return tokens, origin


def _verticals(pages: list[dict]) -> list[tuple[int, str]]:
    """(token index, kind) for each vertical stroke the transcription distinguishes."""
    out: list[tuple[int, str]] = []
    index = 0
    for chunk, _, _ in _chunks_with_origin(pages):
        if chunk.startswith("["):
            out.append((index - 1, "paseq"))  # an aside describes the token before it
            continue
        if et.UNIT_JOINER in chunk:
            out.append((index, "legarmeh"))
        index += len(chunk.split(MAQAF))
    return out


def report(pages: list[dict], key: tuple[str, str, str]) -> None:
    source = pd.load_source(pd.default_source_path())
    ref, words, _ = et.reference_tokens(source, key)
    got, origin = _tokens_with_origin(pages)

    print(f"\nstrand {'/'.join(key)}")
    print(f"  reference {len(ref)} tokens / transcribed {len(got)} tokens")
    print(
        f"  chanted verses: reference {ref.count('silsof')}"
        f" / transcribed {got.count('silsof')}"
    )

    a = [et._normalize(t) for t in ref]
    b = [et._normalize(t) for t in got]
    opcodes = difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()
    differences = [op for op in opcodes if op[0] != "equal"]
    print(f"\n-- {len(differences)} difference region(s) --")
    for tag, i1, i2, j1, j2 in differences:
        where = origin[j1] if j1 < len(origin) else ("?", 0)
        word = words[min(i1, len(words) - 1)] if words else ""
        print(
            f"  {tag.upper():8s} ref[{i1}:{i2}]={ref[i1:i2]} got={got[j1:j2]}"
            f"  at {word}  ({where[0]} line {where[1]})"
        )
        if "silsof" in ref[i1:i2] + got[j1:j2]:
            print("           ^^ TOUCHES A CHANTED VERSE BOUNDARY")

    for j, token in enumerate(got):
        if token != UNRESOLVED:
            continue
        print(f"\n-- reference context around unresolved token {j} --")
        for i in range(max(0, j - 3), min(len(ref), j + 4)):
            print(f"    ref[{i:3d}] {ref[i]:8s} {words[i]}{'  <--' if i == j else ''}")

    spots = [i for i, w in enumerate(words) if et.PASEQ in w and ref[i] == "mun"]
    marked = _verticals(pages)
    print("\n-- vertical strokes --")
    print(f"  reference positions:   {spots}")
    print(f"  transcribed positions: {[i for i, _ in marked]}")
    print(f"  placements agree: {[i for i, _ in marked] == spots}")
    for i, kind in marked:
        word = words[i] if 0 <= i < len(words) else "?"
        print(f"    token {i:3d}  {word:16s} {kind}")


def site_report(skeleton: str, next_skeleton: str) -> None:
    """What each of the eight strands does at one site, located by letter skeleton.

    Located by the skeleton of the word AND of the word after it, never by a bare prefix:
    Deuteronomy's tenth commandment opens ולא where Exodus's opens לא, and a filter that
    misses that silently turns an eight-strand answer into a four-strand one.  The hit count
    is printed per strand so a filter that matched too few is visible rather than assumed.
    """
    source = pd.load_source(pd.default_source_path())
    print(f"\n=== {skeleton} followed by {next_skeleton} ===")
    for version in source["versions"]:
        key = (version["book"], version["reading"], version["tradition"])
        hits = []
        for verse in version["chanted_verses"]:
            verse_words = verse.split()
            for i, word in enumerate(verse_words):
                if pds.base_skeleton(word) != skeleton:
                    continue
                after = verse_words[i + 1] if i + 1 < len(verse_words) else ""
                if pds.base_skeleton(after) != next_skeleton:
                    continue
                marks: list[str] = []
                for ch in word:
                    abbrev = et.ACCENT_ABBREV.get(ch)
                    if abbrev is not None and abbrev != (marks[-1] if marks else None):
                        marks.append(abbrev)
                paseq = " +PASEQ" if et.PASEQ in word else ""
                hits.append(f"{word} -> {'+'.join(marks) or '(none)'}{paseq}")
        print(f"  {'/'.join(key):28s} {len(hits)} hit(s): {', '.join(hits)}")


def main() -> None:
    args = sys.argv[1:]
    if "--site" in args:
        i = args.index("--site")
        site_report(args[i + 1], args[i + 2])
        return
    if "--stem" in args:
        stem = args[args.index("--stem") + 1]
        transcription = et.load_transcription(et.transcriptions_dir() / f"{stem}.txt")
        record = json.loads(
            (et.transcriptions_dir() / f"{stem}.json").read_text(encoding="utf-8")
        )
        report(_pages_of(record), transcription.key)
        return
    key_at = args.index("--key")
    key = (args[key_at + 1], args[key_at + 2], args[key_at + 3])
    pages = []
    for path in args[:key_at]:
        pages.extend(_pages_of(json.loads(Path(path).read_text(encoding="utf-8"))))
    report(pages, key)


if __name__ == "__main__":
    main()
