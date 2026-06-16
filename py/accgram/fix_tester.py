r"""Test whether the suggested fixes in the research-oddballs report actually work.

For every *annotated* prose oddball (one carrying an ob_notes_* note), the
goerwitz.html report suggests a fix -- almost always "adopt the MAM-simple value
instead of the wlc_focus value".  This tool tests that suggestion mechanically:
it splices the MAM value into the verse's Michigan-Claremont body
(``fix_apply``), re-scans + re-parses it (the real ``ply_scanner`` /
``ply_grammar``), and classifies the outcome:

  * CONFIRMED  -- the oddball's ERROR cleared (the verse now parses clean);
  * DENIED     -- the same error remains;
  * CHANGED    -- a *different* error appears;
  * UNTESTABLE -- the fix could not be applied mechanically (vowel-only,
                  multi-word, context-dependent accent, alignment failure, ...).

It then cross-checks the verdict against the note's claim, flagging speculative
claims ("I think the checker wants...") whose mechanical result disagrees, and
writes a standalone text + JSON report under ``out/accgram/fix-tester/``.  It
never edits goerwitz.html or the ob_notes_* prose; a human applies prose edits
from the report.

Depends on ``out/accgram/ply/`` -- run ``run-ply`` first.
"""

from __future__ import annotations

import argparse
import json
import threading
from dataclasses import asdict, dataclass
from pathlib import Path

from accgram import fix_apply
from accgram import fix_claim
from accgram import fix_tester_codes
from accgram import ply_classify
from accgram import research_tao
from accgram import rtms_data
from accgram import rtms_focus_diff_expand
from accgram import rtms_rows
from accgram import lexical_validation
from accgram.ply_grammar import LOCATION_ONLY, build_parser, parse_tokens
from accgram.ply_scanner import HasLegarmeh, Token, scan_accents
from accgram.ply_tree import TN
from accgram.ob_notes import get_structured_text
from mb_cmn import provenance


@dataclass(frozen=True)
class FixTestResult:
    ref: str
    bcv: str
    wlc_focus: str | None
    fix_description: str
    classification: str  # CONFIRMED | DENIED | CHANGED | UNTESTABLE
    untestable_reason: str | None
    transformation: str | None
    before_status: str
    before_labels: tuple[str, ...]
    after_status: str | None
    after_labels: tuple[str, ...]
    before_tokens: tuple[str, ...]
    after_tokens: tuple[str, ...] | None
    speculative: bool
    claimed_outcome: str
    agreement: str  # agree | disagree | n/a
    st_summary: str


@dataclass
class _Eval:
    status: str  # CLEAN | ODDBALL | NO_PARSE | LOCATION_ONLY
    labels: frozenset[str]
    token_types: tuple[str, ...]


_PARSE_TIMEOUT_SECONDS = 8.0


class _ParseGuard:
    """Parse with a wall-clock watchdog so a pathological modified stream cannot
    hang the run.  The fix-tester feeds the grammar synthetic token streams it
    never sees in the corpus; a few can drive PLY's error recovery into an
    internal (not read-driven) loop.  On timeout we abandon the zombie thread
    (daemon) and rebuild the parser so the next verse uses a clean one.
    """

    def __init__(self) -> None:
        self.parser = build_parser()

    def parse(self, tokens):
        box: dict[str, object] = {}

        def work() -> None:
            try:
                box["tree"] = parse_tokens(self.parser, tokens)
            except BaseException as exc:  # noqa: BLE001 - re-raised on the caller thread
                box["exc"] = exc

        thread = threading.Thread(target=work, daemon=True)
        thread.start()
        thread.join(_PARSE_TIMEOUT_SECONDS)
        if thread.is_alive():
            self.parser = build_parser()  # the old parser is held by the zombie
            return "timeout", None
        if "exc" in box:
            raise box["exc"]  # type: ignore[misc]
        return "ok", box.get("tree")


# --- per-verse evaluation (mirrors run_ply.render_book) -----------------------


def _evaluate(body: str, bb: str, chnu: int, vrnu: int, guard: _ParseGuard) -> _Eval:
    tokens = [Token("TILDE", "")] + scan_accents(body, bb, chnu, vrnu, HasLegarmeh())
    token_types = tuple(tok.type for tok in tokens if tok.type != "TILDE")

    # Prose lexical layer fires first and skips the grammar (as in run_ply).
    stranded = lexical_validation.stranded_stress_helpers(body)
    if stranded:
        labels = frozenset(f"illegal_mark:{mark.code}" for mark in stranded)
        return _Eval("ODDBALL", labels, token_types)

    status, tree = guard.parse(tokens)
    if status == "timeout":
        return _Eval("PARSE_TIMEOUT", frozenset({"PARSE_TIMEOUT"}), token_types)
    if tree is None:
        return _Eval("NO_PARSE", frozenset({"NO_PARSE"}), token_types)
    if tree is LOCATION_ONLY:
        return _Eval("LOCATION_ONLY", frozenset({"LOCATION_ONLY"}), token_types)
    labels = _error_labels(tree)
    if labels:
        return _Eval("ODDBALL", frozenset(labels), token_types)
    return _Eval("CLEAN", frozenset(), token_types)


def _error_labels(tree: TN, out: set[str] | None = None) -> set[str]:
    """Labels of leaf nodes whose leaves contain the ERROR token."""
    out = set() if out is None else out
    if tree.left is None:
        if "ERROR" in tree.leaves:
            out.add(tree.label)
    else:
        _error_labels(tree.left, out)
        if tree.right is not None:
            _error_labels(tree.right, out)
    return out


# --- diff -> single testable change ------------------------------------------


def _single_diff_entry(diff: object) -> object:
    """Return the lone diff dict, or a sentinel: _NO_DIFF / _MULTI_DIFF."""
    if isinstance(diff, dict):
        return diff
    if diff is None:
        return _NO_DIFF
    if isinstance(diff, list):
        entries = [e for e in diff if isinstance(e, dict)]
        if not entries:
            return _NO_DIFF
        if len(entries) == 1:
            return entries[0]
        return _MULTI_DIFF
    return _NO_DIFF


_NO_DIFF = object()
_MULTI_DIFF = object()


def _describe_diff(diff_entry: object) -> str:
    if not isinstance(diff_entry, dict):
        return "(no MAM diff)"
    return f"{_side_repr(diff_entry.get('wlc422'))} -> {_side_repr(diff_entry.get('mam_simple'))}"


def _side_repr(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(_side_repr(v) for v in value)
    if isinstance(value, dict):
        for key in ("word", "text"):
            inner = value.get(key)
            if isinstance(inner, str):
                return inner
    return repr(value)


# --- one oddball -------------------------------------------------------------


def _test_one(
    *,
    row: dict[str, object],
    bcv: str,
    ref: str,
    structured_text: dict[str, object],
    wlc_focus: str | None,
    source_indexes: tuple[dict, dict, dict],
    args: argparse.Namespace,
    guard: _ParseGuard,
) -> FixTestResult:
    speculative = fix_claim.is_speculative(structured_text)
    claimed = fix_claim.claimed_outcome(structured_text)
    st_summary = _summary_text(structured_text)
    bb, chnu, vrnu = rtms_rows.parse_ref(ref, row_kind="oddball")

    def result(
        classification: str,
        *,
        reason: str | None = None,
        transformation: str | None = None,
        before: _Eval | None = None,
        after: _Eval | None = None,
        fix_description: str = "",
    ) -> FixTestResult:
        agreement = _agreement(claimed, classification)
        return FixTestResult(
            ref=ref,
            bcv=bcv,
            wlc_focus=wlc_focus,
            fix_description=fix_description,
            classification=classification,
            untestable_reason=reason,
            transformation=transformation,
            before_status=before.status if before else "n/a",
            before_labels=tuple(sorted(before.labels)) if before else (),
            after_status=after.status if after else None,
            after_labels=tuple(sorted(after.labels)) if after else (),
            before_tokens=before.token_types if before else (),
            after_tokens=after.token_types if after else None,
            speculative=speculative,
            claimed_outcome=claimed,
            agreement=agreement,
            st_summary=st_summary,
        )

    body = row.get("content")
    if not isinstance(body, str) or not body:
        return result("UNTESTABLE", reason="no_body")

    wlc422_by_bcv, uxlc_by_bcv, mam_simple_by_bcv = source_indexes
    try:
        enriched_row, _ = rtms_data.build_enriched_row(
            row=row,
            bcv=bcv,
            ref=ref,
            wlc422_by_bcv=wlc422_by_bcv,
            uxlc_by_bcv=uxlc_by_bcv,
            mam_simple_by_bcv=mam_simple_by_bcv,
            wlc422_kq_u_dir=args.wlc422_kq_u_dir,
            uxlc_dir=args.uxlc_dir,
            mam_simple_dir=args.mam_simple_dir,
            wlc_focus=wlc_focus,
        )
    except (ValueError, KeyError) as exc:
        return result("UNTESTABLE", reason="enrich_error", fix_description=str(exc))

    diff = enriched_row.get("diff_wlc_mam")
    wlc_words = fix_apply.verse_words(enriched_row.get("wlc422_kq_u_verse"))
    before = _evaluate(body, bb, chnu, vrnu, guard)

    diff_entry = _single_diff_entry(diff)
    if diff_entry is _NO_DIFF:
        return result(
            "UNTESTABLE", reason="no_mam_diff", before=before,
            fix_description="(MAM equals WLC; nothing to adopt)",
        )
    if diff_entry is _MULTI_DIFF:
        return result(
            "UNTESTABLE", reason="multi_diff", before=before,
            fix_description=_describe_diff_list(diff),
        )

    fix_description = _describe_diff(diff_entry)
    applied = fix_apply.apply_mam_fix(body, wlc_words, diff_entry)
    if isinstance(applied, fix_apply.UntestableFix):
        return result(
            "UNTESTABLE",
            reason=applied.reason,
            before=before,
            fix_description=fix_description,
            transformation=applied.detail or None,
        )

    after = _evaluate(applied.new_body, bb, chnu, vrnu, guard)
    if after.status == "PARSE_TIMEOUT":
        return result(
            "UNTESTABLE",
            reason="parse_timeout",
            before=before,
            transformation=applied.transformation(),
            fix_description=fix_description,
        )
    if after.status == "CLEAN":
        classification = "CONFIRMED"
    elif (after.status, after.labels) == (before.status, before.labels):
        classification = "DENIED"
    else:
        classification = "CHANGED"
    return result(
        classification,
        before=before,
        after=after,
        transformation=applied.transformation(),
        fix_description=fix_description,
    )


def _describe_diff_list(diff: object) -> str:
    if isinstance(diff, list):
        return "; ".join(_describe_diff(e) for e in diff if isinstance(e, dict))
    return _describe_diff(diff)


def _summary_text(structured_text: object) -> str:
    if isinstance(structured_text, dict):
        summary = structured_text.get("st-summary")
        if isinstance(summary, str):
            return summary
    return ""


def _agreement(claimed: str, classification: str) -> str:
    if classification == "UNTESTABLE" or claimed == "unclear":
        return "n/a"
    result_fixed = classification == "CONFIRMED"
    if claimed == "expects_fix":
        return "agree" if result_fixed else "disagree"
    if claimed == "rejects_fix":
        return "agree" if not result_fixed else "disagree"
    return "n/a"


# --- run ---------------------------------------------------------------------


def run_tests(args: argparse.Namespace) -> list[FixTestResult]:
    fix_tester_codes.assert_in_sync_with_gg_rules()
    repo_root = _repo_root()

    ply_classify.write_ply_oddballs(
        ply_dir=getattr(args, "ply_dir", None) or research_tao.default_ply_dir(repo_root),
        source_input_path=args.input,
        oddballs_out=args.oddballs_in,
    )

    refs_by_book: dict[str, set[tuple[int, int]]] = {}
    parsed_rows = rtms_rows.parse_oddball_rows(args.oddballs_in, refs_by_book)
    structured_text_by_ref = get_structured_text()

    source_indexes = rtms_data.load_source_indexes(
        wlc422_kq_u_dir=args.wlc422_kq_u_dir,
        uxlc_dir=args.uxlc_dir,
        mam_simple_dir=args.mam_simple_dir,
        refs_by_book=refs_by_book,
    )

    guard = _ParseGuard()
    results: list[FixTestResult] = []
    for row, bcv, ref in parsed_rows:
        structured_text = structured_text_by_ref.get(ref)
        if structured_text is None:
            continue
        wlc_focus = rtms_focus_diff_expand.structured_wlc_focus(structured_text)
        results.append(
            _test_one(
                row=row,
                bcv=bcv,
                ref=ref,
                structured_text=structured_text,
                wlc_focus=wlc_focus,
                source_indexes=source_indexes,
                args=args,
                guard=guard,
            )
        )
    results.sort(key=lambda r: _ref_sort_key(r.ref))
    return results


def _ref_sort_key(ref: str) -> tuple[str, int, int]:
    bb, chnu, vrnu = rtms_rows.parse_ref(ref, row_kind="oddball")
    return (bb, chnu, vrnu)


# --- reports -----------------------------------------------------------------

_SECTIONS = (
    ("CONFIRMED", "MAM fix clears the oddball"),
    ("DENIED", "same error remains after the fix"),
    ("CHANGED", "a different error appears after the fix"),
    ("UNTESTABLE", "fix could not be applied mechanically"),
)


def _summary_counts(results: list[FixTestResult]) -> dict[str, int]:
    counts = {name: 0 for name, _ in _SECTIONS}
    for r in results:
        counts[r.classification] = counts.get(r.classification, 0) + 1
    return counts


def render_text_report(results: list[FixTestResult]) -> str:
    counts = _summary_counts(results)
    specs = [r for r in results if r.speculative]
    spec_conf = sum(1 for r in specs if r.classification == "CONFIRMED")
    spec_denied = sum(1 for r in specs if r.classification in ("DENIED", "CHANGED"))
    spec_untest = sum(1 for r in specs if r.classification == "UNTESTABLE")
    agree = sum(1 for r in results if r.agreement == "agree")
    disagree = sum(1 for r in results if r.agreement == "disagree")

    lines: list[str] = []
    lines.append("# Fix-tester: do MAM-simple values resolve annotated prose oddballs?")
    lines.append("")
    lines.append(
        f"confirmed: {counts['CONFIRMED']}  denied: {counts['DENIED']}  "
        f"changed: {counts['CHANGED']}  untestable: {counts['UNTESTABLE']}  "
        f"({len(results)} annotated oddballs tested)"
    )
    lines.append(
        f"speculations: {len(specs)} total; {spec_conf} confirmed, "
        f"{spec_denied} denied/changed, {spec_untest} untestable"
    )
    lines.append(f"claim-vs-result: {agree} agree, {disagree} disagree")
    lines.append("")

    by_class: dict[str, list[FixTestResult]] = {name: [] for name, _ in _SECTIONS}
    for r in results:
        by_class.setdefault(r.classification, []).append(r)

    for name, blurb in _SECTIONS:
        group = by_class.get(name, [])
        lines.append(f"## {name} -- {blurb}  ({len(group)})")
        for r in group:
            lines.extend(_render_entry(r))
        lines.append("")

    review = [r for r in results if r.speculative and r.agreement == "disagree"]
    lines.append(
        f"## Review queue: speculative claims whose result disagrees  ({len(review)})"
    )
    for r in review:
        lines.append(f"  {r.ref}  [{r.classification}] claim: {r.st_summary!r}")
    lines.append("")

    return "\n".join(lines) + "\n"


def _render_entry(r: FixTestResult) -> list[str]:
    tags = []
    if r.speculative:
        tags.append("speculative")
    if r.claimed_outcome != "unclear":
        tags.append(f"claim: {r.claimed_outcome}")
    if r.agreement != "n/a":
        tags.append(r.agreement.upper())
    tag_str = (" [" + "] [".join(tags) + "]") if tags else ""
    out = [f"  {r.ref}{tag_str}"]
    out.append(f"    fix: {r.fix_description}")
    if r.classification == "UNTESTABLE":
        detail = f" ({r.transformation})" if r.transformation else ""
        out.append(f"    reason: {r.untestable_reason}{detail}")
        return out
    if r.transformation:
        out.append(f"    transform: {r.transformation}")
    out.append(f"    before: {' '.join(r.before_tokens)}  [{_status_label(r.before_status, r.before_labels)}]")
    after_tokens = " ".join(r.after_tokens) if r.after_tokens else ""
    out.append(f"    after:  {after_tokens}  [{_status_label(r.after_status, r.after_labels)}]")
    return out


def _status_label(status: str | None, labels: tuple[str, ...]) -> str:
    if status == "CLEAN":
        return "CLEAN"
    if labels:
        return f"{status}: {', '.join(labels)}"
    return status or "n/a"


def build_json_report(results: list[FixTestResult]) -> dict:
    counts = _summary_counts(results)
    specs = [r for r in results if r.speculative]
    payload = {
        "artifacts_description": (
            "fix-tester verdicts: whether adopting each annotated prose oddball's "
            "MAM-simple value clears its grammar/lexical error"
        ),
        "summary": {
            "tested": len(results),
            **{name.lower(): counts.get(name, 0) for name, _ in _SECTIONS},
            "speculative_total": len(specs),
            "speculative_confirmed": sum(
                1 for r in specs if r.classification == "CONFIRMED"
            ),
            "agree": sum(1 for r in results if r.agreement == "agree"),
            "disagree": sum(1 for r in results if r.agreement == "disagree"),
        },
        "results": [asdict(r) for r in results],
    }
    return provenance.with_json_provenance(payload, __file__)


# --- CLI ---------------------------------------------------------------------


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def default_report_txt_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "fix-tester" / "_fix_tester.txt"


def default_report_json_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "fix-tester" / "_fix_tester.json"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--input",
        type=Path,
        default=research_tao.default_input_path(repo_root),
        help="Path to source wlc422_ps.txt file (oddball verse content).",
    )
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=research_tao.default_wlc422_kq_u_dir(repo_root),
        help="Directory containing 1verses_*.json files.",
    )
    parser.add_argument(
        "--uxlc-dir",
        type=Path,
        default=research_tao.default_uxlc_dir(repo_root),
        help="Directory containing UXLC XML book files.",
    )
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=research_tao.default_mam_simple_dir(repo_root),
        help="Directory containing MAM-simple json-vtrad-bhs book files.",
    )
    parser.add_argument(
        "--oddballs-in",
        type=Path,
        default=research_tao.default_oddballs_in(repo_root),
        help="Path to _oddballs.json (PLY-derived; regenerated each run).",
    )
    parser.add_argument(
        "--ply-dir",
        type=Path,
        default=research_tao.default_ply_dir(repo_root),
        help="Directory of PLY *_ag.txt outputs for the oddball corpus.",
    )
    parser.add_argument(
        "--report-txt",
        type=Path,
        default=default_report_txt_path(repo_root),
        help="Output path for the text fix-tester report.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        default=default_report_json_path(repo_root),
        help="Output path for the JSON fix-tester report.",
    )


def run(args: argparse.Namespace) -> None:
    results = run_tests(args)

    text_path: Path = args.report_txt
    json_path: Path = args.report_json
    text_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.write_text(render_text_report(results), encoding="utf-8", newline="\n")
    with json_path.open("w", encoding="utf-8") as f_out:
        json.dump(build_json_report(results), f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")

    counts = _summary_counts(results)
    print(
        f"Fix-tester: {len(results)} tested; {counts['CONFIRMED']} confirmed, "
        f"{counts['DENIED']} denied, {counts['CHANGED']} changed, "
        f"{counts['UNTESTABLE']} untestable -> {text_path}"
    )
