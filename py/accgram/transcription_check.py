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
* Pasoleg positions AND kinds.  The folded ``chanted_verses`` collapses legarmeh and
  narrow-sense paseq onto the same U+05C0 glyph, but ``faithful_chanted_verses`` keeps them
  apart (issue #74), so the reference now says both WHERE a stroke stands and WHICH kind it is
  -- and the transcription's own legarmeh/paseq claim is checked against it, not only against
  glyph shape.  Comparing the placements doubles as an alignment check: these are independent
  anchors, so several landing on their exact indices rules out a drifting diff.  The two sides
  index DIFFERENT token streams, so a transcribed pasoleg is mapped through the diff into
  reference coordinates before any comparison -- an insertion upstream of one would otherwise
  shift it off its reference position and the report would blame the pasoleg.  An edition that
  does not distinguish the two kinds (Koren) prints ``unspecified`` and no kind is compared.

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

UNRESOLVED = "???"


def _pages_of(record: dict) -> list[dict]:
    """A multi-page audit trail holds one export per page; a single-page one is its own page."""
    return record.get("pages", [record])


def _chunks_with_origin(pages: list[dict]) -> list[tuple[str, str, int]]:
    """(chunk, page label, printed line) in reading order, asides kept in place.

    ``rejoin_editor_chunks`` undoes the editor's line breaks -- the ONE implementation of that
    rule, shared with ``hebrew_chunks``, so the two cannot drift apart again -- and a rejoined
    compound keeps the origin of the line it STARTED on, which is the line to go back and
    re-read.
    """
    items = [
        (written, (page.get("stem", "?").split("_")[-1], line["n"]))
        for page in pages
        for line in page["lines"]
        for written in line["text"].split()
    ]
    return [
        (written, label, n) for written, (label, n) in et.rejoin_editor_chunks(items)
    ]


def _tokens_with_origin(pages: list[dict]) -> tuple[list[str], list[tuple[str, int]]]:
    """Latin tokens in reading order, each with the (page, printed line) it was typed on."""
    tokens: list[str] = []
    origin: list[tuple[str, int]] = []
    for chunk, label, n in _chunks_with_origin(pages):
        if chunk.startswith("["):
            continue  # a bracketed aside carries no accent
        # How an editor chunk comes apart is ``editor_accents``'s business, not this module's:
        # a chunk may hold more than one accent, joined by a maqaf or by the SIMPLE_JOINER, and
        # this loop once knew that separately and fell out of step when the latter was added.
        for accent, _ in et.editor_accents(chunk):
            try:
                tokens.append(et.hebrew_token(accent))
            except ValueError as exc:
                print(f"  !! {label} line {n}: {exc}")
                tokens.append(UNRESOLVED)
            origin.append((label, n))
    return tokens, origin


def _pasolegs(pages: list[dict]) -> list[tuple[int, str]]:
    """(transcribed token index, kind) for each pasoleg the transcription records.

    Indices are into the TRANSCRIBED token stream -- map through the diff before comparing
    them with reference positions.  A pasoleg is pinned to the accent that bears it, so a
    compound is walked part by part: a legarmeh on a compound's second atom is at the second
    atom's index, not the compound's first.

    Kind comes from the aside's own vocabulary (``et.aside_kind``), which is where the three
    kinds are defined and where an unrecognized aside raises.  This function used to label
    EVERY bracketed aside "paseq" regardless of what it said, so an edition that prints the
    stroke without distinguishing its kind -- Koren does not -- had no way to be recorded
    without asserting one.
    """
    out: list[tuple[int, str]] = []
    index = 0
    for chunk, _, _ in _chunks_with_origin(pages):
        if chunk.startswith("["):
            # An aside describes the token before it; none exists yet at index 0.
            if index:
                out.append((index - 1, et.aside_kind(chunk)))
            continue
        for offset, (accent, _) in enumerate(et.editor_accents(chunk)):
            if et.UNIT_JOINER in accent:
                out.append((index + offset, "legarmeh"))
        index += len(et.editor_accents(chunk))
    return out


def _opcodes(ref: list[str], got: list[str]) -> list[tuple[str, int, int, int, int]]:
    """The diff between the two NORMALIZED token streams, as difflib opcodes."""
    a = [et._normalize(t) for t in ref]
    b = [et._normalize(t) for t in got]
    return difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes()


def _to_reference(
    j: int, opcodes: list[tuple[str, int, int, int, int]]
) -> tuple[int, bool]:
    """Transcribed token index -> ``(reference index, exact)``.

    The two streams index DIFFERENT sequences, so a transcribed index means nothing against a
    reference position until it is mapped through the diff.  Inside an equal block the mapping
    is exact.  Inside a difference region the token has no reference counterpart at all, so
    the region's own start is returned as the nearest anchor, flagged inexact -- display it as
    context, never as a position that agrees.
    """
    for tag, i1, _, j1, j2 in opcodes:
        if j1 <= j < j2:
            return (i1 + (j - j1), True) if tag == "equal" else (i1, False)
    return 0, False  # unreachable for an index into the diffed stream


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

    opcodes = _opcodes(ref, got)
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
        # An unresolved token sits inside a difference region by construction, so the mapping
        # is inexact; its region's start is still the right place to show context around.
        anchor, _ = _to_reference(j, opcodes)
        print(f"\n-- reference context around unresolved token {j} --")
        for i in range(max(0, anchor - 3), min(len(ref), anchor + 4)):
            print(
                f"    ref[{i:3d}] {ref[i]:8s} {words[i]}{'  <--' if i == anchor else ''}"
            )

    spots = [i for i, w in enumerate(words) if et.PASEQ in w and ref[i] == "mun"]
    marked = _pasolegs(pages)
    mapped = [_to_reference(j, opcodes) for j, _ in marked]
    # The reference kind of each stroke, now that faithful_chanted_verses keeps it (issue #74).
    # Aligned with ``spots`` in reading order, so spot_kind maps a reference index to its kind.
    ref_kinds = et.reference_pasoleg_kinds(source, key)
    spot_kind = dict(zip(spots, ref_kinds))
    print("\n-- pasoleg positions --")
    print(f"  reference positions:              {spots}")
    print(f"  reference kinds:                  {ref_kinds}")
    print(f"  transcribed, mapped to reference: {[i for i, _ in mapped]}")
    agree = [i for i, exact in mapped if exact] == spots and all(x for _, x in mapped)
    print(f"  placements agree: {agree}")
    for (j, kind), (i, exact) in zip(marked, mapped):
        word = words[i] if 0 <= i < len(words) else "?"
        place = f"ref {i}" if exact else f"in a difference region at ref {i}"
        # The transcription asserts a kind; the reference now states one too.  Compare them
        # only where both are definite -- an edition that does not distinguish the two prints
        # "unspecified", and there is nothing to check against the reference's legarmeh/paseq.
        ref_kind = spot_kind.get(i) if exact else None
        if kind == "unspecified" or ref_kind is None:
            verdict = ""
        elif kind == ref_kind:
            verdict = f"  == reference {ref_kind}"
        else:
            verdict = f"  != reference {ref_kind}  <-- KIND MISMATCH"
        print(f"    token {j:3d} -> {place}  {word:16s} {kind}{verdict}")
    matched = {i for i, exact in mapped if exact}
    for i in spots:
        if i not in matched:
            print(
                f"    ref {i:3d} has a pasoleg in the reference only  {words[i]:16s}"
                f" {spot_kind.get(i, '')}"
            )

    # Printed LAST because it is the one thing a clean report does not otherwise say.  A
    # reading supplied from expectation agrees with the reference by construction, so it sits
    # in the agreeing majority this loop never inspects -- "0 difference regions" is exactly
    # the result that hides it, which is why it is reported even when nothing else is wrong.
    unresolved = et.uncertain_readings(pages)
    if unresolved:
        print(f"\n-- {len(unresolved)} reading(s) NOT fully read off the page --")
        for entry in unresolved:
            print(
                f"  {entry['page']} line {entry['line']}: {entry['word']}"
                f" read as {entry['reading']} -- {entry['why']}"
            )


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
