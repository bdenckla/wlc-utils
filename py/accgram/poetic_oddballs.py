"""Poetic oddball report -- the optional Phase 4 analogue of ``research-oddballs``.

The poetic corpus run (``run-ply-poetic``) parses 99.62% of the Three Books
cleanly; the residual splits into two documented oddball kinds:

  * ``missing_silluq`` -- the 13 verses whose sof pasuq arrives with no silluq
    code, recovered by the grammar into an ERROR-leaf tree (structure preserved,
    the silluq_phrase mark is ``ERROR``).
  * ``no_parse`` -- the 4 hierarchy-violating L anomalies for which no valid tree
    exists; emitted as ``NO_PARSE`` token lines by the driver.

This module re-scans + re-parses the poetic corpus (the same source of truth the
driver writes from), collects every oddball verse, and enriches each with: the
M-C source body, the full scanned token sequence, the rendered ERROR tree or
NO_PARSE line, and -- the key review datum for accent oddballs -- the WLC vs
MAM-simple disjunctive sequences (what L's accents say versus what the MAM oracle
reads). It writes a git-tracked ``_oddballs.json`` next to the corpus outputs and
a self-contained ``gh-pages/accgram/poetic.html`` for review.

Unlike the prose ``research_tao`` report, there is no UXLC / changetext / hand-
authored ob_notes machinery here: the poetic oddballs are a closed set of 17
documented structural cases, and the MAM disjunctive comparison is the relevant
oracle (the prose UXLC enrichment targets vowel/consonant text changes, which
these accent-structure oddballs do not concern).
"""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path

from accgram import poetic_filter
from accgram import split_wlc
from accgram.mam_poetic_accents import load_poetic_disjunctives
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram.poetic_accent_names import POETIC_DISJUNCTIVES as _POETIC_DISJUNCTIVES
from accgram.ply_grammar_poetic import build_parser, parse_tokens
from accgram.ply_scanner_poetic import scan_book
from accgram.ply_tree import print_tree
from accgram.run_ply_poetic import _has_error_leaf, _no_parse_line
from mb_cmn import provenance

KIND_MISSING_SILLUQ = "missing_silluq"
KIND_NO_PARSE = "no_parse"


@dataclass(frozen=True)
class PoeticOddball:
    reference: str  # clean book-name form, e.g. "Psalms 31:21"
    bb: str
    kind: str  # KIND_MISSING_SILLUQ | KIND_NO_PARSE
    body: str  # the M-C accent body (source content after "ch:vr ")
    output_file: str  # the *_ag.txt holding this verse's tree/NO_PARSE line
    token_types: tuple[str, ...]  # full scanned token-type sequence
    wlc_disjunctives: tuple[str, ...]  # WLC disjunctive skeleton (scanner)
    mam_disjunctives: tuple[str, ...] | None  # MAM oracle skeleton (None if absent)
    tree_text: str  # rendered ERROR tree, or the NO_PARSE line


def collect_poetic_oddballs(
    input_path: Path, mam_simple_dir: Path
) -> list[PoeticOddball]:
    """Re-scan + re-parse the poetic corpus and return every oddball verse."""
    mam_by_ref = load_poetic_disjunctives(mam_simple_dir)
    parser = build_parser()
    book_texts = split_wlc.split_wlc_to_book_texts(
        input_path, keep_line_fn=poetic_filter.should_keep_line
    )

    oddballs: list[PoeticOddball] = []
    for bb, text in book_texts.items():
        output_file = f"wlc_422_ps_{bb}_ag.txt"
        for verse in scan_book(text, bb):
            tree = parse_tokens(parser, verse.tokens)
            if tree is None:
                kind = KIND_NO_PARSE
                tree_text = _no_parse_line(verse.tokens).rstrip("\n")
            elif _has_error_leaf(tree):
                kind = KIND_MISSING_SILLUQ
                tree_text = print_tree(tree, 0).rstrip("\n")
            else:
                continue

            wlc = tuple(t for t, _ in verse.tokens if t in _POETIC_DISJUNCTIVES)
            mam = mam_by_ref.get(verse.reference)
            oddballs.append(
                PoeticOddball(
                    reference=verse.reference,
                    bb=bb,
                    kind=kind,
                    body=verse.body,
                    output_file=output_file,
                    token_types=tuple(t for t, _ in verse.tokens),
                    wlc_disjunctives=wlc,
                    mam_disjunctives=tuple(mam) if mam is not None else None,
                    tree_text=tree_text,
                )
            )
    return oddballs


def _oddball_to_row(ob: PoeticOddball) -> dict[str, object]:
    return {
        "ref": ob.reference,
        "bb": ob.bb,
        "kind": ob.kind,
        "content": ob.body,
        "output_file": ob.output_file,
        "token_types": list(ob.token_types),
        "wlc_disjunctives": list(ob.wlc_disjunctives),
        "mam_disjunctives": (
            list(ob.mam_disjunctives) if ob.mam_disjunctives is not None else None
        ),
        "tree": ob.tree_text,
    }


def build_payload(oddballs: list[PoeticOddball], source_file: str) -> dict[str, object]:
    kinds: dict[str, int] = {}
    for ob in oddballs:
        kinds[ob.kind] = kinds.get(ob.kind, 0) + 1
    payload: dict[str, object] = {
        "artifacts_description": "poetic (Three Books) oddball verses for review",
        "payload_provenance_note": (
            "Each row is a poetic verse the PLY port could not parse cleanly: either "
            "a missing-silluq verse recovered into an ERROR-leaf tree "
            f"('{KIND_MISSING_SILLUQ}') or a hierarchy-violating L anomaly emitted as "
            f"a NO_PARSE line ('{KIND_NO_PARSE}'). wlc_disjunctives is the scanner's "
            "disjunctive skeleton; mam_disjunctives is the MAM-simple oracle's, for "
            "comparison. output_file names the *_ag.txt holding the tree/NO_PARSE line."
        ),
        "summary": {
            "oddballs": len(oddballs),
            "missing_silluq": kinds.get(KIND_MISSING_SILLUQ, 0),
            "no_parse": kinds.get(KIND_NO_PARSE, 0),
        },
        "oddballs": [_oddball_to_row(ob) for ob in oddballs],
    }
    return provenance.with_json_provenance(payload, source_file)


_KIND_LABEL = {
    KIND_MISSING_SILLUQ: "Missing silluq (ERROR-leaf recovery)",
    KIND_NO_PARSE: "NO_PARSE (hierarchy-violating L anomaly)",
}


def _disj_compare_html(ob: PoeticOddball) -> str:
    wlc = " ".join(ob.wlc_disjunctives)
    if ob.mam_disjunctives is None:
        mam = "<em>(not in MAM-simple)</em>"
        agree = ""
    else:
        mam = html.escape(" ".join(ob.mam_disjunctives))
        agree = (
            ' <span class="agree">(agree)</span>'
            if ob.wlc_disjunctives == ob.mam_disjunctives
            else ' <span class="diff">(differ)</span>'
        )
    return (
        f'<div class="disj"><span class="lbl">WLC:</span> {html.escape(wlc)}{agree}</div>'
        f'<div class="disj"><span class="lbl">MAM:</span> {mam}</div>'
    )


def render_html(oddballs: list[PoeticOddball]) -> str:
    n_silluq = sum(1 for o in oddballs if o.kind == KIND_MISSING_SILLUQ)
    n_noparse = sum(1 for o in oddballs if o.kind == KIND_NO_PARSE)
    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append('<html lang="en"><head><meta charset="utf-8">')
    parts.append("<title>Poetic accent-grammar oddballs</title>")
    parts.append(
        "<style>"
        "body{font-family:system-ui,sans-serif;margin:2rem;max-width:60rem;color:#222}"
        "h1{font-size:1.5rem}h2{font-size:1.15rem;margin-top:2rem;border-bottom:1px solid #ccc}"
        ".ob{border:1px solid #ddd;border-radius:6px;padding:.8rem 1rem;margin:1rem 0}"
        ".ref{font-weight:600;font-size:1.05rem}"
        ".src{font-family:ui-monospace,monospace;background:#f6f6f6;padding:.3rem .5rem;"
        "border-radius:4px;word-break:break-all;margin:.4rem 0;direction:ltr;unicode-bidi:plaintext}"
        ".disj{font-family:ui-monospace,monospace;font-size:.9rem;margin:.15rem 0}"
        ".lbl{display:inline-block;width:3rem;color:#666}"
        ".agree{color:#178017}.diff{color:#b00}"
        "pre{background:#fafafa;border:1px solid #eee;padding:.5rem;overflow-x:auto;font-size:.85rem}"
        ".meta{color:#666;font-size:.85rem;margin:.3rem 0}"
        "</style></head><body>"
    )
    parts.append("<h1>Poetic (Three Books) accent-grammar oddballs</h1>")
    parts.append(
        f"<p>{len(oddballs)} residual oddball verse(s): "
        f"{n_silluq} missing-silluq (ERROR-leaf), {n_noparse} NO_PARSE. "
        "See <code>doc/PLAN-poetic-accent-grammar.md</code> for the taxonomy.</p>"
    )

    for kind in (KIND_MISSING_SILLUQ, KIND_NO_PARSE):
        group = [o for o in oddballs if o.kind == kind]
        if not group:
            continue
        parts.append(f"<h2>{html.escape(_KIND_LABEL[kind])} &mdash; {len(group)}</h2>")
        for ob in group:
            parts.append('<div class="ob">')
            parts.append(f'<div class="ref">{html.escape(ob.reference)}</div>')
            parts.append(f'<div class="src">{html.escape(ob.body)}</div>')
            parts.append(_disj_compare_html(ob))
            parts.append(
                f'<div class="meta">tokens: {html.escape(" ".join(ob.token_types))}'
                f' &middot; <code>{html.escape(ob.output_file)}</code></div>'
            )
            parts.append(f"<pre>{html.escape(ob.tree_text)}</pre>")
            parts.append("</div>")

    parts.append("</body></html>")
    return "\n".join(parts) + "\n"


def default_input_path(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "in" / "wlc422" / "wlc422_ps.txt"


def default_oddballs_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-poetic" / "_oddballs.json"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_root / "gh-pages" / "accgram" / "poetic.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=default_input_path(repo_root),
        help="Path to source wlc422_ps.txt file.",
    )
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=default_mam_simple_dir(repo_root),
        help="Directory containing MAM-simple json-vtrad-bhs book files.",
    )
    parser.add_argument(
        "--oddballs-out",
        type=Path,
        default=default_oddballs_out_path(repo_root),
        help="Output JSON path for the poetic oddball records.",
    )
    parser.add_argument(
        "--html-out",
        type=Path,
        default=default_html_out_path(repo_root),
        help="Output HTML path for the poetic oddball report.",
    )


def run(args: argparse.Namespace) -> None:
    oddballs = collect_poetic_oddballs(args.input, args.mam_simple_dir)

    payload = build_payload(oddballs, __file__)
    oddballs_out: Path = args.oddballs_out
    oddballs_out.parent.mkdir(parents=True, exist_ok=True)
    with oddballs_out.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    html_out.write_text(render_html(oddballs), encoding="utf-8", newline="\n")

    n_silluq = sum(1 for o in oddballs if o.kind == KIND_MISSING_SILLUQ)
    n_noparse = sum(1 for o in oddballs if o.kind == KIND_NO_PARSE)
    print(
        f"Poetic oddballs: {len(oddballs)} "
        f"({n_silluq} missing-silluq, {n_noparse} NO_PARSE)"
    )
    print(f"JSON: {oddballs_out}")
    print(f"HTML: {html_out}")
