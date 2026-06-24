"""Approach A: test whether UXLC accent changes NOT in goerwitz output move from
WLC-4.22-grammatical to UXLC-ungrammatical.

For each grammar-relevant accent change (per uxlc_accent_changes.json) that is NOT
linked to a Goerwitz oddball note and that lies in the PROSE corpus the checker
can evaluate, we:

  1. Transcode the real WLC 4.22 verse to its scanner-ready mark body from the
     canonical `-kq-u` Unicode source (issue #9 retired wlc422_ps.txt).
  2. Locate the changed word (by the citation's word index).
  3. VALIDATE: synthesize the WLC reading of that word from `refuni` (Unicode token
     names -> accent marks) and confirm that scanning the synthesized word
     yields the SAME token stream as scanning the real word.  This certifies,
     per case, that our name->mark synthesis is faithful for this accent content
     (it auto-excludes stress-helper / ordering cases we can't reproduce).
  4. If validated, synthesize the UXLC reading from `changeuni`, splice it into the
     verse body, and re-run the existing scanner+grammar on both the original
     (WLC) and edited (UXLC) verse.  Classify each as grammatical / ungrammatical.

Output: the WLC-vs-UXLC 2x2, plus coverage (how many validated), written to
out/accgram/uxlc_grammar_test.txt.  Console output is ASCII only.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from accgram import accent_marks as am  # noqa: E402
from accgram import rtms_data  # noqa: E402
from accgram import rtms_rows  # noqa: E402
from accgram import uni_to_marks  # noqa: E402
from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens  # noqa: E402
from accgram.ply_scanner import HasLegarmeh, Token, scan_accents  # noqa: E402
from accgram.ply_tree import print_tree  # noqa: E402
from accgram import prose_filter  # noqa: E402
from cmn.wlc_book_codes import bk39id_to_wlc_bb  # noqa: E402
from py_uxlc.my_uxlc_book_abbreviations import expand_citation  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
WLC_KQ_U = REPO.parent / "wlc-utils-io" / "out" / "wlc422-kq-u"
SRC = REPO / "in" / "accgram" / "uxlc_accent_changes.json"
OUT = REPO / "out" / "accgram" / "uxlc_grammar_test.txt"

# Unicode accent NAME (as used in refuni/changeuni) -> its scanner mark (accent_marks).
# These are the prose te'amim; poetic-only accents (atnah-hafukh, etc.) have no prose
# mark and simply will not validate if they appear.
NAME2MARK = {
    "etnachta": am.ATNAX, "etnahta": am.ATNAX,
    "zarqa": am.ZINOR, "zinor": am.ZINOR,
    "pashta": am.PASHTA,
    "yetiv": am.YETIV,
    "tevir": am.TEVIR,
    "geresh": am.GERESH, "geresh-muqdam": am.GERESH_MUQDAM,
    "gereshayim": am.GERSHAYIM, "gershayim": am.GERSHAYIM,
    "telisha-gedola": am.TELISHA_GEDOLA,
    "telisha-qetana": am.TELISHA_QETANA,
    "pazer": am.PAZER,
    "munah": am.MUNAX,
    "mahapakh": am.MAHAPAKH, "makhapakh": am.MAHAPAKH,
    "merkha": am.MERKHA,
    "darga": am.DARGA,
    "qadma": am.QADMA,
    "yerah-ben-yomo": am.YERAX,
    "ole": am.OLE,
    "iluy": am.ILUY,
    "dehi": am.DEXI,
    "revia": am.REVIA,
    "zaqef-qatan": am.ZAQEF_QATAN,
    "zaqef-gadol": am.ZAQEF_GADOL,
    "tipeha": am.TIPEXA,
    "shalshelet": am.SHALSHELET,
}
# Non-accent tokens that still carry meaning for the scanner.
_METEGISH = {"meteg", "silluq"}


def synth_word(uni_tokens: list[str]) -> str | None:
    """Synthesize a scanner-readable mark word from refuni/changeuni token names.

    Consonants -> a filler placeholder (the scanner swallows letters; they only serve
    as non-terminator TEXT).  Vowels/points are dropped.  Accents/meteg/sof-pasuq/
    paseq/maqaf become their marks/delimiters, in order.  Returns None if a token has
    no known prose mark (e.g. a poetic accent) -> case is unsupported.
    """
    out: list[str] = []
    for tok in uni_tokens:
        if tok in NAME2MARK:
            out.append(NAME2MARK[tok])
        elif tok in _METEGISH:
            out.append(am.METEG)
        elif tok == "sof-pasuq":
            out.append(am.SOF_PASUQ)
        elif tok == "paseq":
            out.append(am.PASEQ)
        elif tok == "maqaf":
            out.append(am.MAQAF)
        elif tok == "space":
            # The flanking space of a paseq: paseq attaches to its word with no
            # word-boundary space, so emit nothing (a real space here would spuriously
            # split the maqaf-unit into two words).
            continue
        else:
            # consonant or vowel/point -> a placeholder filler letter.
            out.append(am.LETTER)
    return "".join(out)


def scan_word_tokens(word: str, bb: str, ch: int, vs: int) -> tuple[str, ...]:
    """Scan a single word body to its accent-token TYPE tuple (terminator included)."""
    toks = scan_accents(word, bb, ch, vs, HasLegarmeh())
    return tuple(t.type for t in toks)


def maqaf_units(body: str):
    """Flatten an M-C verse body into maqaf-units (tanach.us word numbering).

    Returns (units, owners): `units[i]` is the i-th maqaf-unit string; `owners[i]`
    is (space_index, maqaf_index_within_space_token) so a unit can be spliced back
    while preserving the maqaf / space structure of the body.
    """
    units: list[str] = []
    owners: list[tuple[int, int]] = []
    for si, sp in enumerate(body.split(" ")):
        for mi, mu in enumerate(sp.split("-")):
            units.append(mu)
            owners.append((si, mi))
    return units, owners


def splice_unit(body: str, owner: tuple[int, int], new_unit: str) -> str:
    """Return `body` with one maqaf-unit replaced, preserving structure."""
    space_tokens = [sp.split("-") for sp in body.split(" ")]
    si, mi = owner
    space_tokens[si][mi] = new_unit
    return " ".join("-".join(parts) for parts in space_tokens)


def is_ungrammatical(parser, body: str, bb: str, ch: int, vs: int) -> bool:
    toks = [Token("TILDE", "")] + scan_accents(body, bb, ch, vs, HasLegarmeh())
    tree = parse_tokens(parser, toks)
    if tree is None:
        # No recovery: a residual gap.  Treat as ungrammatical but flag via caller.
        return True
    if tree is LOCATION_ONLY:
        return True
    return "ERROR" in print_tree(tree, 0)


def _kind(r) -> str:
    """Categorize a change for confidence bucketing.

    - 'remove_terminator': the change drops sof-pasuq (degenerate: necessarily
      errors regardless of accentuation).
    - 'add_accent': adds an accent (coding-sensitive: an added prepositive mark
      could be a stress-helper we code as a main accent).
    - 'substitution': 1:1 accent swap / removal not touching sof-pasuq (robust:
      validated structurally on the WLC side).
    """
    ref = set((r.get("refuni_gen") or r.get("refuni") or "").split())
    chg = set((r.get("changeuni_gen") or r.get("changeuni") or "").split())
    if "sof-pasuq" in ref and "sof-pasuq" not in chg:
        return "remove_terminator"
    acc = lambda s: sum(1 for t in s if t in NAME2MARK)
    if acc((r.get("changeuni_gen") or r.get("changeuni") or "").split()) > acc(
        (r.get("refuni_gen") or r.get("refuni") or "").split()
    ):
        return "add_accent"
    return "substitution"


def _transcoded_bodies(
    keys,
) -> dict[tuple[str, int, int], str]:
    """The scanner-ready mark body for each ``(bb, ch, vs)``, transcoded from the
    canonical ``-kq-u`` Unicode source (issue #9 retired ``wlc422_ps.txt``)."""
    index = rtms_data.load_wlc422_index(WLC_KQ_U)
    bodies: dict[tuple[str, int, int], str] = {}
    for bb, ch, vs in keys:
        verse = index.get(rtms_rows.to_compact_bcv(bb, ch, vs))
        if isinstance(verse, dict):
            bodies[(bb, ch, vs)] = uni_to_marks.verse_to_marks(verse)
    return bodies


def main() -> None:
    data = json.load(open(SRC, encoding="utf-8"))
    out_set = [r for r in data if not r["goerwitz_st_ref"]]

    # Group prose-corpus changes by verse, so a verse with several changes is
    # tested as ONE coherent UXLC reading (not a per-word chimera).
    by_verse: dict[tuple[str, int, int], list[tuple[int, dict]]] = {}
    for r in out_set:
        bk, ch, vs, wd = expand_citation(r["citation"])
        bb = bk39id_to_wlc_bb(bk)
        if not prose_filter.should_keep_line(bb, ch, vs):
            continue
        by_verse.setdefault((bb, ch, vs), []).append((wd, r))

    bodies = _transcoded_bodies(by_verse)
    parser = build_parser()

    stat = Counter()
    grid = Counter()          # (wlc, uxlc) -> n verses (all validated)
    grid_visible = Counter()  # (wlc, uxlc) -> n verses (scanner-visible only)
    cell_by_kind = Counter()  # (kind, wlc, uxlc) over individual changes in solo verses
    broke = []              # verses: WLC-gram -> UXLC-ungram
    fixed = []              # verses: WLC-ungram -> UXLC-gram
    unreliable = []

    for (bb, ch, vs), changes in by_verse.items():
        stat["prose_verses"] += 1
        stat["prose_changes"] += len(changes)
        body = bodies.get((bb, ch, vs))
        if body is None:
            stat["no_body"] += 1
            continue
        units, owners = maqaf_units(body)

        # Validate every change in the verse; apply them all to build UXLC body.
        uxlc_body = body
        ok = True
        for wd, r in changes:
            if not (1 <= wd <= len(units)):
                ok = False
                break
            ref_syn = synth_word((r.get("refuni_gen") or r.get("refuni") or "").split())
            chg_syn = synth_word((r.get("changeuni_gen") or r.get("changeuni") or "").split())
            if ref_syn is None or chg_syn is None:
                ok = False
                break
            if scan_word_tokens(ref_syn, bb, ch, vs) != scan_word_tokens(units[wd - 1], bb, ch, vs):
                ok = False
                break
            uxlc_body = splice_unit(uxlc_body, owners[wd - 1], chg_syn)
        if not ok:
            stat["unreliable_verses"] += 1
            stat["unreliable_changes"] += len(changes)
            unreliable.append(((bb, ch, vs), [r["citation"] for _, r in changes]))
            continue
        stat["validated_verses"] += 1
        stat["validated_changes"] += len(changes)

        # A change is "scanner-visible" only if it alters the accent-token stream;
        # otherwise (meteg reorder, collapsed sub-distinction, ...) the grammar
        # cannot possibly react and the verse is a trivial neutral.
        wlc_stream = tuple(t.type for t in scan_accents(body, bb, ch, vs, HasLegarmeh()))
        uxlc_stream = tuple(t.type for t in scan_accents(uxlc_body, bb, ch, vs, HasLegarmeh()))
        visible = wlc_stream != uxlc_stream
        stat["visible" if visible else "noop"] += 1

        wlc_bad = is_ungrammatical(parser, body, bb, ch, vs)
        uxlc_bad = is_ungrammatical(parser, uxlc_body, bb, ch, vs)
        if visible:
            grid_visible[("WLC-ungram" if wlc_bad else "WLC-gram",
                          "UXLC-ungram" if uxlc_bad else "UXLC-gram")] += 1
        cell = ("WLC-ungram" if wlc_bad else "WLC-gram",
                "UXLC-ungram" if uxlc_bad else "UXLC-gram")
        grid[cell] += 1
        descs = [(r["citation"], r["accent_change_reason"], _kind(r), r["description"][:55])
                 for _, r in changes]
        # Attribute by-kind only for solo-change verses (clean attribution).
        if len(changes) == 1:
            cell_by_kind[(descs[0][2], cell[0], cell[1])] += 1
        if not wlc_bad and uxlc_bad:
            broke.append(((bb, ch, vs), descs))
        elif wlc_bad and not uxlc_bad:
            fixed.append(((bb, ch, vs), descs))

    # ---- report ----
    lines = []
    def p(s=""):
        lines.append(s)
        print(s)

    p("=== Approach A: WLC-4.22 vs UXLC grammaticality (changes NOT in goerwitz output) ===")
    p()
    p(f"prose-corpus verses          : {stat['prose_verses']}  ({stat['prose_changes']} changes)")
    p(f"  validated                  : {stat['validated_verses']} verses ({stat['validated_changes']} changes)")
    p(f"  unreliable (excluded)      : {stat['unreliable_verses']} verses ({stat['unreliable_changes']} changes)")
    p()
    p(f"  of validated: scanner-VISIBLE change {stat['visible']}, no-op {stat['noop']}")
    p()
    p("2x2 over validated VERSES (all):")
    for w in ("WLC-gram", "WLC-ungram"):
        for u in ("UXLC-gram", "UXLC-ungram"):
            p(f"  {w:11s} -> {u:12s}: {grid[(w, u)]}")
    p()
    p("2x2 over scanner-VISIBLE verses (the meaningful denominator):")
    for w in ("WLC-gram", "WLC-ungram"):
        for u in ("UXLC-gram", "UXLC-ungram"):
            p(f"  {w:11s} -> {u:12s}: {grid_visible[(w, u)]}")
    p()
    p(f"HYPOTHESIS cell (WLC-gram -> UXLC-ungram): {len(broke)} verses")
    for ref, descs in sorted(broke):
        for cit, reason, kind, desc in descs:
            p(f"    {cit:16s} [{reason}/{kind}] {desc}")
    if fixed:
        p()
        p(f"WLC-ungram -> UXLC-gram: {len(fixed)} verses")
        for ref, descs in sorted(fixed):
            for cit, reason, kind, desc in descs:
                p(f"    {cit:16s} [{reason}/{kind}] {desc}")
    p()
    p("By-kind breakdown of WLC-gram solo-change verses (confidence buckets):")
    kinds = sorted({k for (k, _, _) in cell_by_kind})
    for k in kinds:
        g = cell_by_kind[(k, "WLC-gram", "UXLC-gram")]
        b = cell_by_kind[(k, "WLC-gram", "UXLC-ungram")]
        p(f"  {k:18s}: -> UXLC-gram {g:3d}   -> UXLC-ungram {b:3d}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nWrote report to {OUT}")


if __name__ == "__main__":
    main()
