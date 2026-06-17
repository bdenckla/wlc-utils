r"""Cross-check, per disjunctive, the SERVANT (conjunctive) L and MAM put before it.

The disjunctive cross-check (``xcheck_poetic``) compares only the division *points*
and is silent on servi.  This tool fills that gap: for each poetic disjunctive it
tabulates the servus standing immediately before it in the WLC scanner's token stream
(L) and in MAM-simple (via ``mam_poetic_accents.servi_before_in_words``), then reports
where the two witnesses agree or differ.

It is the second-witness gate for vetting Breuer's servant-ADJACENCY rules before
encoding any of them in the grammar.  It already settled two:

  * deḥi: Breuer Ch 11 §11 says "always [munaḥ]", but L marks merkha in 16/19 cases and
    MAM agrees (munaḥ in 0) -- REFUTED.
  * small revia': Breuer §16 says "[merkha]", and L is 125/125 merkha with MAM agreeing and
    zero servant-type conflicts -- CONFIRMED (encoded, though it then fires on nothing).

Per target it shows: the L adjacent-servant distribution; and, over verses where L and
MAM agree on how many times the target occurs, the per-occurrence agree/disagree count
(plus a verse-count-mismatch tally for verses the two segment differently).  A
"disagreement" is a servant-TYPE difference; a slot where only one witness has a
servant (the other reads a bare/divider word) is counted separately as such.  The run
writes a git-tracked report and prints a one-line-per-target summary.

Servi are read in the scanner's own vocabulary on both sides (mam_poetic_accents
normalizes MAM's signs: qadma->AZLA, tipeha->TARXA, atnah-hafukh->GALGAL), so the
comparison is apples-to-apples.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from accgram import poetic_accent_names as pan
from accgram import poetic_filter
from accgram import split_wlc
from accgram.mam_poetic_accents import load_word_accents, servi_before_in_words
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram.ply_scanner_poetic import scan_book

# The poetic conjunctive servi, in the scanner's vocabulary.
_SERVI = frozenset(
    {pan.MUNAX, pan.MERKHA, pan.MAHAPAKH, pan.AZLA, pan.GALGAL, pan.ILLUY, pan.TARXA}
)

# Disjunctives worth checking -- every concrete poetic divider that can take a servant
# (the provisional generic REVIA is reclassified away before it reaches a token stream).
_DEFAULT_TARGETS: tuple[str, ...] = (
    pan.SILLUQ,
    pan.OLEH_WEYORED,
    pan.ATNAX,
    pan.REVIA_GADOL,
    pan.REVIA_MUGRASH,
    pan.REVIA_QATAN,
    pan.DEXI,
    pan.TSINNOR,
    pan.PAZER,
    pan.LEGARMEH,
    pan.SHALSHELET_GEDOLAH,
)

# Cap on how many per-target disagreements to spell out in the report (they are usually
# few; the count is always exact even when the listing is truncated).
_MAX_LISTED = 60


@dataclass
class TargetReport:
    target: str
    l_dist: Counter  # L adjacent servant (non-None) -> count
    both: int = 0  # occurrences with a servant in BOTH witnesses (length-matched verses)
    agree: int = 0  # ... and the servant type matches
    disagree: int = 0  # ... and it differs (a real servant-type conflict)
    one_sided: int = 0  # only one witness has a servant there (other reads bare/divider)
    len_mismatch: int = 0  # verses where L and MAM disagree on the target's occurrence count
    disagreements: list[tuple[str, str | None, str | None]] = field(default_factory=list)


def _scan_l(input_path: Path) -> dict[str, list[str]]:
    """Map each verse reference -> the scanner's ordered token-type list (L side)."""
    book_texts = split_wlc.split_wlc_to_book_texts(
        input_path, keep_line_fn=poetic_filter.should_keep_line
    )
    out: dict[str, list[str]] = {}
    for bb, text in book_texts.items():
        for verse in scan_book(text, bb):
            out[verse.reference] = [t for t, _ in verse.tokens]
    return out


def _l_servi_before(types: list[str], target: str) -> list[str | None]:
    """Servus before each ``target`` occurrence in an L token-type list (None = bare)."""
    out: list[str | None] = []
    for i, t in enumerate(types):
        if t != target:
            continue
        prev = types[i - 1] if i > 0 else None
        out.append(prev if prev in _SERVI else None)
    return out


def collect(
    input_path: Path, mam_simple_dir: Path, targets: tuple[str, ...]
) -> list[TargetReport]:
    """Build a TargetReport per target over the poetic corpus (one MAM walk)."""
    l_by_ref = _scan_l(input_path)
    mam_words = load_word_accents(mam_simple_dir)

    reports: list[TargetReport] = []
    for target in targets:
        rep = TargetReport(target=target, l_dist=Counter())
        for ref, types in l_by_ref.items():
            l_seq = _l_servi_before(types, target)
            for servus in l_seq:
                if servus is not None:
                    rep.l_dist[servus] += 1
            words = mam_words.get(ref)
            if words is None:
                continue
            m_seq = servi_before_in_words(words, target)
            if len(l_seq) != len(m_seq):
                rep.len_mismatch += 1
                continue
            for l_servus, m_servus in zip(l_seq, m_seq):
                if l_servus is None and m_servus is None:
                    continue
                if l_servus is None or m_servus is None:
                    rep.one_sided += 1
                    continue
                rep.both += 1
                if l_servus == m_servus:
                    rep.agree += 1
                else:
                    rep.disagree += 1
                    rep.disagreements.append((ref, l_servus, m_servus))
        reports.append(rep)
    return reports


def _verdict(rep: TargetReport) -> str:
    if not rep.l_dist:
        return "no servant-bearing occurrences in L"
    uniform = len(rep.l_dist) == 1
    if rep.disagree == 0:
        kind = "UNIFORM" if uniform else "varied"
        return (
            f"{kind} in L; no servant-type conflict with MAM "
            "(rule candidate -- may flag nothing if L is already uniform)"
        )
    return f"{rep.disagree} servant-type conflict(s) with MAM -- investigate"


def render_report(reports: list[TargetReport]) -> str:
    lines: list[str] = ["# Poetic servant-adjacency cross-check: WLC scanner vs MAM-simple", ""]
    for rep in reports:
        dist = ", ".join(f"{k}:{v}" for k, v in rep.l_dist.most_common()) or "(none)"
        lines.append(f"## {rep.target}")
        lines.append(f"  L adjacent servant: {dist}")
        lines.append(
            f"  vs MAM (length-matched verses): both-served {rep.both} "
            f"(agree {rep.agree}, type-conflict {rep.disagree}); "
            f"one-sided {rep.one_sided}; verse-count-mismatch {rep.len_mismatch}"
        )
        lines.append(f"  verdict: {_verdict(rep)}")
        if rep.disagreements:
            lines.append("  servant-type conflicts (ref: L -> MAM):")
            for ref, l_servus, m_servus in rep.disagreements[:_MAX_LISTED]:
                lines.append(f"    {ref}: {l_servus} -> {m_servus}")
            if len(rep.disagreements) > _MAX_LISTED:
                lines.append(f"    ... and {len(rep.disagreements) - _MAX_LISTED} more")
        lines.append("")
    return "\n".join(lines) + "\n"


def default_input_path(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "in" / "wlc422" / "wlc422_ps.txt"


def default_report_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-poetic" / "_servi_xcheck.txt"


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
        "--report",
        type=Path,
        default=default_report_path(repo_root),
        help="Output path for the servant cross-check report.",
    )
    parser.add_argument(
        "--target",
        nargs="*",
        choices=_DEFAULT_TARGETS,
        default=list(_DEFAULT_TARGETS),
        metavar="DISJUNCTIVE",
        help="Disjunctive token name(s) to check (default: all). e.g. --target DEXI TSINNOR",
    )


def run(args: argparse.Namespace) -> None:
    reports = collect(args.input, args.mam_simple_dir, tuple(args.target))
    report_text = render_report(reports)

    report_path: Path = args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_text, encoding="utf-8", newline="\n")

    for rep in reports:
        dist = ", ".join(f"{k}:{v}" for k, v in rep.l_dist.most_common()) or "(none)"
        print(
            f"{rep.target}: L[{dist}]; MAM agree {rep.agree}, "
            f"type-conflict {rep.disagree}, one-sided {rep.one_sided}, "
            f"len-mismatch {rep.len_mismatch}"
        )
    print(f"-> {report_path}")
