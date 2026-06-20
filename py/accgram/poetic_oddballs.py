"""Poetic oddball report -- the optional Phase 4 analogue of ``generate-goerwitz-html``.

The poetic corpus run (``run-ply-poetic``) parses 99.69% of the Three Books
cleanly; the residual splits into two documented oddball kinds:

  * ``missing_silluq`` -- the 13 verses whose sof pasuq arrives with no silluq
    code, recovered by the grammar into an ERROR-leaf tree (structure preserved,
    the silluq_phrase mark is ``ERROR``).
  * ``no_parse`` -- the 1 hierarchy-violating L anomaly (Job 31:15) for which no
    valid tree exists; emitted as a ``NO_PARSE`` token line by the driver.  (Ps
    17:14's double tsinnor was a second such case until the parser began accepting
    a repeated divider as one; see ply_grammar_poetic.parse_tokens_accepting_repeats
    and gh-pages/accgram/ps17v14-double-tsinnor.html.)

This module re-scans + re-parses the poetic corpus (the same source of truth the
driver writes from), collects every oddball verse, and enriches each with: the
verse's pointed-Hebrew text, the full scanned token sequence, the rendered ERROR
tree or NO_PARSE line, and -- the key review datum for accent oddballs -- the WLC vs
MAM-simple disjunctive sequences (what L's accents say versus what the MAM oracle
reads). It writes a git-tracked ``_oddballs.json`` next to the corpus outputs and
``gh-pages/accgram/poetic.html`` for review.

The HTML deliberately shares the prose ``goerwitz.html`` shell -- the same
``../style.css``, width-limited wrapper, single flat client-side-filterable
verse list (``poetic-filter.js``), per-verse permalinks + Mwd/UXLC links, the
parse tree rendered as an HTML table via ``ob_tree_table``, and the SAT
focus-word table via ``poetic_sat`` (which reuses the prose ``rtmsr_sat``
renderer) -- so the two reports can later be merged into one generator (see
issue #10). It keeps one poetic-only display the prose
page has no analogue for: the WLC-vs-MAM disjunctive compare. The verse-final NO_PARSE cases,
having no valid parse, render a flat best-effort tree (each token a cell, capped
by an ERROR leaf) so they too display through the shared error-tree table.

The mechanically auto-derived WLC-vs-MAM-simple summary is the relevant oracle
for these accent-structure oddballs (the prose UXLC change-text enrichment
targets vowel/consonant text changes, which these do not concern); it -- with
the client-side "MAM compare" filter facet -- now carries the WLC-vs-MAM
disjunctive comparison that an earlier standalone skeleton table showed. On top
of it there is an optional hand-authored annotation layer -- the poetic analogue
of the prose ``ob_notes_*`` modules -- in ``poetic_ob_notes``: a per-oddball
``st-summary`` / ``comment`` plus external links (a tanach.us ``uxlc_note_page``,
a ``github-issue``), shown only for the few cases that warrant it. The SAT
focus-word table is reproduced for missing-silluq verses (whose locus is the
verse-final word); NO_PARSE verses, having no single focus word, omit it.
"""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

from accgram import ob_error_context
from accgram import ob_report
from accgram import ob_tree_table
from accgram import poetic_filter
from accgram import poetic_ob_notes
from accgram import poetic_sat
from accgram import research_tao
from accgram import rtms_data
from accgram import rtms_focus_diff_expand
from accgram import rtms_ref
from accgram import rtms_report
from accgram import rtmsr_media
from accgram import rtmsr_verse
from accgram import uni_to_marks
from accgram.mam_poetic_accents import load_poetic_word_disj
from accgram.mam_simple_verse import default_mam_simple_dir
from accgram.poetic_accent_names import POETIC_DISJUNCTIVES as _POETIC_DISJUNCTIVES
from accgram.ply_grammar_poetic import (
    ParseError,
    build_parser,
    parse_tokens_accepting_repeats,
)
from accgram.ply_scanner_poetic import scan_book
from accgram.poetic_reconcile import reconcile_tokens
from accgram.poetic_oddball_summary import derive_tentative_summary
from accgram.ply_tree import print_tree
from accgram.run_ply_poetic import _has_error_leaf, _no_parse_line
from mb_cmn import provenance
from py_html import wlc_utils_html
from py_wlc import my_wlc_bcv_str

KIND_MISSING_SILLUQ = "missing_silluq"
KIND_NO_PARSE = "no_parse"

# The prose-report-shaped (row, key) -> value lookup the shared rtmsr_* helpers
# expect; for the poetic page the row is ignored and the value comes from the
# oddball's hand-authored poetic_ob_notes entry (see _structured_text_lookup).
StructuredTextLookup = Callable[[dict[str, object], str], object]


@dataclass(frozen=True)
class PoeticOddball:
    reference: str  # clean book-name form, e.g. "Psalms 31:21"
    bb: str
    kind: str  # KIND_MISSING_SILLUQ | KIND_NO_PARSE
    body: str  # the Unicode mark body (source content after "ch:vr ")
    output_file: str  # the *_ag.txt holding this verse's tree/NO_PARSE line
    token_types: tuple[str, ...]  # full scanned token-type sequence
    wlc_disjunctives: tuple[str, ...]  # WLC disjunctive skeleton (scanner)
    mam_disjunctives: tuple[str, ...] | None  # MAM oracle skeleton (None if absent)
    # MAM per-word (base_consonants, disjunctive_or_None), the word-aligned counterpart
    # of mam_disjunctives used to derive the summary; None if the verse is absent from
    # MAM-simple.  Not written to _oddballs.json (the skeletons are the persisted datum).
    mam_words: tuple[tuple[str, str | None], ...] | None
    tree_text: str  # rendered ERROR tree, or the NO_PARSE line
    # The parse stall locus for a NO_PARSE verse (None for missing-silluq): the
    # offending accent's token type and its 1-based ordinal among the verse's
    # accents, so the report can pinpoint where the parse dead-ended.
    error: ParseError | None
    # WLC 4.22 pointed-Hebrew verse (qere-interpolated + sanitized), for the
    # HTML report's verse paragraph; None if the verse is absent from the index.
    # Not written to _oddballs.json (the disjunctive skeletons are the datum).
    wlc_verse: dict[str, object] | None
    # The build_enriched_row payload (WLC/UXLC/MAM focus-word verses + diffs)
    # feeding the SAT focus-word table; built only for missing-silluq verses with a
    # unique verse-final focus word, None otherwise. Rebuilt at collection time, never
    # persisted to _oddballs.json.
    enriched_row: dict[str, object] | None


def collect_poetic_oddballs(
    mam_simple_dir: Path,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
) -> list[PoeticOddball]:
    """Re-scan + re-parse the poetic corpus and return every oddball verse."""
    mam_words_by_ref = load_poetic_word_disj(mam_simple_dir)
    wlc_index = rtms_data.load_wlc422_index(wlc422_kq_u_dir)
    parser = build_parser()
    book_texts = uni_to_marks.build_book_texts(
        wlc422_kq_u_dir, keep_line_fn=poetic_filter.should_keep_line
    )

    oddballs: list[PoeticOddball] = []
    for bb, text in book_texts.items():
        output_file = f"wlc_422_ps_{bb}_ag.txt"
        for verse in scan_book(text, bb):
            mam_words = mam_words_by_ref.get(verse.reference)
            mam = (
                [d for _cons, d in mam_words if d is not None]
                if mam_words is not None
                else None
            )
            # Apply the legarmeh-vs-paseq and unmarked-oleh corrections before parsing,
            # exactly as run_ply_poetic does, so this report agrees with the driver's
            # trees (and the two resolved NO_PARSE verses no longer surface here).
            tokens = reconcile_tokens(
                verse.reference, verse.body, list(verse.tokens), mam, parser
            )
            tree, error = parse_tokens_accepting_repeats(parser, tokens)
            if tree is None:
                kind = KIND_NO_PARSE
                tree_text = _no_parse_line(tokens, error).rstrip("\n")
            elif _has_error_leaf(tree):
                kind = KIND_MISSING_SILLUQ
                error = None
                tree_text = print_tree(tree, 0).rstrip("\n")
            else:
                continue

            wlc = tuple(t for t, _ in tokens if t in _POETIC_DISJUNCTIVES)
            bcv = f"{bb}{verse.reference.rpartition(' ')[2]}"
            raw_verse = wlc_index.get(bcv)
            wlc_verse = (
                rtms_data.prepare_wlc422_verse_for_render(raw_verse)
                if isinstance(raw_verse, dict)
                else None
            )
            oddballs.append(
                PoeticOddball(
                    reference=verse.reference,
                    bb=bb,
                    kind=kind,
                    body=verse.body,
                    output_file=output_file,
                    token_types=tuple(t for t, _ in tokens),
                    wlc_disjunctives=wlc,
                    mam_disjunctives=tuple(mam) if mam is not None else None,
                    mam_words=tuple(mam_words) if mam_words is not None else None,
                    tree_text=tree_text,
                    error=error,
                    wlc_verse=wlc_verse,
                    enriched_row=None,
                )
            )

    return _attach_enriched_rows(
        oddballs,
        wlc422_kq_u_dir=wlc422_kq_u_dir,
        uxlc_dir=uxlc_dir,
        mam_simple_dir=mam_simple_dir,
    )


def _attach_enriched_rows(
    oddballs: list[PoeticOddball],
    *,
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
) -> list[PoeticOddball]:
    """Enrich each missing-silluq oddball with the WLC/UXLC/MAM focus-word payload
    the SAT table needs, leaving NO_PARSE verses (no localized focus) untouched."""
    refs_by_book: dict[str, set[tuple[int, int]]] = {}
    for ob in oddballs:
        if ob.kind != KIND_MISSING_SILLUQ:
            continue
        _bb, chnu, vrnu, _bcv = rtms_report.parse_ref_to_wlc_bcv(_bb_ref(ob))
        refs_by_book.setdefault(ob.bb, set()).add((chnu, vrnu))

    wlc422_by_bcv, uxlc_by_bcv, mam_simple_by_bcv = rtms_data.load_source_indexes(
        wlc422_kq_u_dir=wlc422_kq_u_dir,
        uxlc_dir=uxlc_dir,
        mam_simple_dir=mam_simple_dir,
        refs_by_book=refs_by_book,
    )

    return [
        replace(
            ob,
            enriched_row=_enriched_row_for(
                ob,
                wlc422_by_bcv=wlc422_by_bcv,
                uxlc_by_bcv=uxlc_by_bcv,
                mam_simple_by_bcv=mam_simple_by_bcv,
                wlc422_kq_u_dir=wlc422_kq_u_dir,
                uxlc_dir=uxlc_dir,
                mam_simple_dir=mam_simple_dir,
            ),
        )
        for ob in oddballs
    ]


def _enriched_row_for(
    ob: PoeticOddball,
    *,
    wlc422_by_bcv: dict[str, dict[str, object]],
    uxlc_by_bcv: dict[str, dict[str, object]],
    mam_simple_by_bcv: dict[str, dict[str, object]],
    wlc422_kq_u_dir: Path,
    uxlc_dir: Path,
    mam_simple_dir: Path,
) -> dict[str, object] | None:
    """The poetic_sat focus-word payload for ob's SAT table, or None.

    Only missing-silluq verses get one (their locus is the verse-final focus word);
    a missing UXLC/MAM witness or a non-unique focus degrades to None, in which case
    the verse simply renders no SAT table -- the run stays non-fatal."""
    if ob.kind != KIND_MISSING_SILLUQ:
        return None
    wlc_focus = poetic_sat.focus_word(
        final_word=_final_word_focus(ob), wlc_verse=ob.wlc_verse
    )
    if not wlc_focus:
        return None
    bb_ref = _bb_ref(ob)
    _bb, _chnu, _vrnu, bcv = rtms_report.parse_ref_to_wlc_bcv(bb_ref)
    return poetic_sat.build_focus_enriched_row(
        bb_ref=bb_ref,
        bcv=bcv,
        output_file=ob.output_file,
        wlc_focus=wlc_focus,
        wlc422_by_bcv=wlc422_by_bcv,
        uxlc_by_bcv=uxlc_by_bcv,
        mam_simple_by_bcv=mam_simple_by_bcv,
        wlc422_kq_u_dir=wlc422_kq_u_dir,
        uxlc_dir=uxlc_dir,
        mam_simple_dir=mam_simple_dir,
    )


def _oddball_to_row(ob: PoeticOddball) -> dict[str, object]:
    return {
        "ref": ob.reference,
        "bb": ob.bb,
        "kind": ob.kind,
        "content": _unicode_text(ob),
        "output_file": ob.output_file,
        "token_types": list(ob.token_types),
        "wlc_disjunctives": list(ob.wlc_disjunctives),
        "mam_disjunctives": (
            list(ob.mam_disjunctives) if ob.mam_disjunctives is not None else None
        ),
        # For a NO_PARSE verse, where the parse dead-ended (the offending accent's
        # token type and its 1-based ordinal among the verse's accents); null for a
        # missing-silluq verse, which has a full ERROR-leaf tree instead.
        "stall": (
            {"accent_index": ob.error.accent_index, "token_type": ob.error.token_type}
            if ob.error is not None
            else None
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
            "comparison. For a NO_PARSE verse, stall names the offending accent (its "
            "1-based ordinal among the verse's accents and its token type) -- where "
            "the LALR(1) parse dead-ended, i.e. every accent before it was consumable "
            "(the stall point, not necessarily the root-cause accent). output_file "
            "names the *_ag.txt holding the tree/NO_PARSE line."
        ),
        "summary": {
            "oddballs": len(oddballs),
            "missing_silluq": kinds.get(KIND_MISSING_SILLUQ, 0),
            "no_parse": kinds.get(KIND_NO_PARSE, 0),
        },
        "oddballs": [_oddball_to_row(ob) for ob in oddballs],
    }
    return provenance.with_json_provenance(payload, source_file)


# The poetic page shares goerwitz.html's stylesheet + width-limited shell and
# the same single flat, client-side-filterable verse list (see
# gh-pages/accgram/poetic-filter.js), so a later merge of the two reports is
# mostly mechanical. It keeps one poetic-only data display the prose page has no
# analogue for: the WLC-vs-MAM disjunctive compare (the relevant oracle for
# accent-structure oddballs). The verse text is shown as pointed Hebrew (issue #9
# retired the Michigan-Claremont body from the reports).
_REPORT_TITLE = "Poetic checker run on WLC"
_REPORT_HEADING = "Poetic checker run on WLC"
_WIDTH_CLASS = "goerwitz-tms-width-limited"
_FILTER_SCRIPT_NAME = "poetic-filter.js"
_SELF_LINK_SYMBOL = "🔗"
# The class every live count span carries, shared with goerwitz-filter.js so the
# poetic filter script reuses the same per-option count machinery.
_COUNT_CLASS = "gf-opt-count"

_KIND_LABEL = {
    KIND_MISSING_SILLUQ: "Missing silluq (ERROR-leaf recovery)",
    KIND_NO_PARSE: "NO_PARSE (hierarchy-violating L anomaly)",
}

# Short labels for the kind filter checkboxes (the headings use _KIND_LABEL).
_KIND_FILTER_LABEL = {
    KIND_MISSING_SILLUQ: "missing silluq",
    KIND_NO_PARSE: "NO_PARSE",
}

# Display labels for the book and MAM-compare filter facets, in filter order.
_BOOK_LABEL = {"ps": "Psalms", "pr": "Proverbs", "jb": "Job"}
_AGREE_LABEL = {
    "agree": "WLC = MAM",
    "differ": "WLC ≠ MAM",
    "na": "not in MAM-simple",
}


def _agree_slug(ob: PoeticOddball) -> str:
    """Filter facet for the WLC-vs-MAM disjunctive compare (see _AGREE_LABEL)."""
    if ob.mam_disjunctives is None:
        return "na"
    return "agree" if ob.wlc_disjunctives == ob.mam_disjunctives else "differ"


def _bb_ref(ob: PoeticOddball) -> str:
    """Rebuild the two-letter bb form ("ps 31:20") the shared rtms_ref/url
    helpers expect from the clean book-name reference ("Psalms 31:20")."""
    _name, _sep, chv = ob.reference.rpartition(" ")
    return f"{ob.bb} {chv}"


def _structured_text_lookup(ob: PoeticOddball) -> StructuredTextLookup:
    """A ``(row, key) -> value`` lookup over this oddball's hand-authored notes.

    Returns the prose-report-shaped callable the shared rtmsr_media/ rtmsr_verse
    helpers expect; ``row`` is ignored (the notes are keyed by the oddball's bb
    reference, not carried on a row). Yields ``None`` for every key when the
    oddball has no hand-authored entry."""
    notes = poetic_ob_notes.get_structured_text().get(_bb_ref(ob))
    notes = notes if isinstance(notes, dict) else {}
    return lambda _row, key: notes.get(key)


def render_body_contents(oddballs: list[PoeticOddball]) -> tuple[object, ...]:
    counts = _counts(oddballs)
    ordered = sorted(
        oddballs, key=lambda ob: rtms_ref.reading_order_key(_bb_ref(ob))
    )

    sections: list[object] = [
        *_build_intro(oddballs),
        _build_filter_controls(counts),
    ]
    for index, ob in enumerate(ordered):
        sections.append(_render_oddball_section(ob, is_first=index == 0))

    wrapper = wlc_utils_html.div(tuple(sections), {"class": _WIDTH_CLASS})
    script = wlc_utils_html.htel_mk("script", {"src": _FILTER_SCRIPT_NAME})
    return (wrapper, script)


def _build_intro(oddballs: list[PoeticOddball]) -> tuple[object, ...]:
    n_silluq = sum(1 for o in oddballs if o.kind == KIND_MISSING_SILLUQ)
    n_noparse = sum(1 for o in oddballs if o.kind == KIND_NO_PARSE)
    return (
        wlc_utils_html.heading_level_1(_REPORT_HEADING),
        wlc_utils_html.heading_level_2("Introduction"),
        wlc_utils_html.para(
            f"This page lists the {len(oddballs)} poetic (Three Books) WLC 4.22 "
            f"verses the PLY accent grammar cannot parse cleanly "
            f"({n_silluq} missing-silluq, {n_noparse} NO_PARSE). Use the filter "
            "below to narrow the list."
        ),
        wlc_utils_html.para("Each verse falls into one of two documented kinds:"),
        wlc_utils_html.unordered_list(
            (
                "“missing silluq,” where the sof pasuq arrives with no silluq, "
                "recovered into an ERROR-leaf tree (structure preserved).",
                "“NO_PARSE,” a hierarchy-violating L anomaly for which no valid "
                "tree exists; the offending accent (where the parse dead-ended) is "
                "marked “← stalled here” in its tree and named in the meta line.",
            )
        ),
        wlc_utils_html.para(
            (
                "Each verse shows its pointed-Hebrew text (the verse-final word "
                "highlighted for missing-silluq cases) and — for missing-silluq "
                "verses — a SAT focus-word "
                "table comparing the WLC focus word against its UXLC and MAM-simple "
                "readings. The "
                "per-verse summary is mechanically auto-derived — but from a "
                "word-by-word alignment of the two verses, not from the "
                "conjunctive-stripped skeletons above, so a divider that merely "
                "sits on a different word is reported as such rather than as a "
                "phantom substitution. It is labelled tentative — not a hand-vetted "
                "attribution. See ",
                wlc_utils_html.code("doc/PLAN-poetic-accent-grammar.md"),
                " for the full taxonomy.",
            )
        ),
    )


def _render_oddball_section(ob: PoeticOddball, *, is_first: bool) -> object:
    bb, chnu, vrnu, bcv = rtms_report.parse_ref_to_wlc_bcv(_bb_ref(ob))
    anchor_id = ob_report.oddball_anchor_id(bcv)

    items: list[object] = []
    # The separating rule lives inside the section (omitted on the first one) so
    # it hides with its verse when the filter removes it -- as in goerwitz.html.
    if not is_first:
        items.append(wlc_utils_html.horizontal_rule())
    items.append(wlc_utils_html.heading_level_2(ob.reference, {"id": anchor_id}))
    items.extend(_render_ref_links(ob, bb=bb, chnu=chnu, vrnu=vrnu, bcv=bcv, anchor_id=anchor_id))
    items.append(_render_summary(ob))
    hebrew_verse = _render_hebrew_verse(ob)
    if hebrew_verse is not None:
        items.append(hebrew_verse)
    items.append(
        wlc_utils_html.para(
            wlc_utils_html.span(_unicode_text(ob), {"lang": "hbo"}),
            {"class": "poetic-src"},
        )
    )
    sat_table = poetic_sat.render_table(ob.enriched_row, row_ref=_bb_ref(ob))
    if sat_table is not None:
        items.append(sat_table)
    items.append(_render_meta(ob))
    items.append(_render_tree(ob))
    items.extend(
        rtmsr_media.render_comment_paragraphs(
            {}, structured_text_lookup=_structured_text_lookup(ob)
        )
    )

    return wlc_utils_html.htel_mk(
        "section",
        {
            "class": "goerwitz-verse",
            "data-kind": ob.kind,
            "data-book": ob.bb,
            "data-agree": _agree_slug(ob),
        },
        tuple(items),
    )


def _render_ref_links(
    ob: PoeticOddball,
    *,
    bb: str,
    chnu: int,
    vrnu: int,
    bcv: str,
    anchor_id: str,
) -> tuple[object, ...]:
    lookup = _structured_text_lookup(ob)
    permalink = wlc_utils_html.anchor(
        _SELF_LINK_SYMBOL,
        {
            "href": f"#{anchor_id}",
            "title": "Permalink to this section",
            "aria-label": "Permalink to this section",
        },
    )
    perma_contents: list[object] = [permalink, f" Kind: {_KIND_LABEL[ob.kind]}."]
    summary = lookup({}, "st-summary")
    if isinstance(summary, str) and summary.strip():
        perma_contents.append(f" Summary: {summary.strip()}")
    perma_para = wlc_utils_html.para(tuple(perma_contents))

    links: list[object] = [
        wlc_utils_html.anchor(
            "Mwd", {"href": rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)}
        ),
        " | ",
        wlc_utils_html.anchor("UXLC", {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)}),
    ]
    for label, key in (("UXLC note page", "uxlc_note_page"), ("GitHub issue", "github-issue")):
        url = lookup({}, key)
        if isinstance(url, str) and url.strip():
            links.extend((" | ", wlc_utils_html.anchor(label, {"href": url.strip()})))
    links_para = wlc_utils_html.para(tuple(links))
    return (perma_para, links_para)


def _render_summary(ob: PoeticOddball) -> object:
    """A tentative, mechanically auto-derived summary (NOT hand-authored).

    It is computed by aligning the WLC and MAM-simple verses word-for-word (the
    consonantal skeleton as the key) and reporting each word whose divider differs;
    it is labelled tentative/auto-derived so a reader knows not to treat it as a
    vetted attribution. Earlier this diffed the conjunctive-stripped disjunctive
    skeletons, which conflated a divider that shifted to the neighbouring word into a
    phantom substitution (Ps 68:20 / Pr 30:15); word alignment fixes that. This is the
    poetic analogue of the prose page's hand-authored st-summary / the
    SAT-descriptor-derived summary (rtmsr_sat.derive_summary_from_sat_descriptors).
    """
    return wlc_utils_html.para(
        (
            wlc_utils_html.span_c(
                "Auto-derived summary (tentative): ", "poetic-auto-summary-label"
            ),
            *_wrap_hebrew_runs(derive_tentative_summary(ob)),
        ),
        {"class": "poetic-auto-summary"},
    )


# A run of Hebrew letters (alef..tav, final forms) plus the maqaf that joins them
# into one accent-word -- the Hebrew words the auto-derived summary embeds.
_HEBREW_RUN_RE = re.compile(r"[־א-ת]+")


def _wrap_hebrew_runs(text: str) -> tuple[object, ...]:
    """Split ``text`` into a flat (string | hbo-span) sequence, wrapping each Hebrew run.

    The summary is shown in an italic paragraph; wrapping its Hebrew words in
    ``lang="hbo"`` spans gives them the Hebrew font and (via the stylesheet) keeps them
    upright -- Hebrew is never italicized."""
    pieces: list[object] = []
    cursor = 0
    for match in _HEBREW_RUN_RE.finditer(text):
        start, end = match.span()
        if start > cursor:
            pieces.append(text[cursor:start])
        pieces.append(wlc_utils_html.span(match.group(0), {"lang": "hbo"}))
        cursor = end
    if cursor < len(text):
        pieces.append(text[cursor:])
    return tuple(pieces)


def _render_hebrew_verse(ob: PoeticOddball) -> object | None:
    """Pointed-Hebrew (RTL) verse paragraph via the shared goerwitz renderer.

    For a missing-silluq verse the locus is the verse-final word (the word that
    arrives with no silluq), so highlight it; NO_PARSE is not localized to one
    word, so render the plain verse. A non-unique/absent focus degrades to no
    highlight (the renderer falls back gracefully)."""
    if not isinstance(ob.wlc_verse, dict):
        return None
    focus = _final_word_focus(ob) if ob.kind == KIND_MISSING_SILLUQ else None
    row = {"wlc422_kq_u_verse": ob.wlc_verse, "wlc_focus": focus}
    return rtmsr_verse.render_wlc_verse_paragraph(
        row, structured_text_lookup=lambda r, key: r.get(key)
    )


def _unicode_text(ob: PoeticOddball) -> str:
    """The verse's normalized pointed-Hebrew text (qere interpolated), from the
    ``-kq-u`` verse; "" if the verse is absent from the index.  Issue #9 replaced the
    Michigan-Claremont source body with this in the report display and ``content``."""
    return rtms_focus_diff_expand.normalized_wlc_verse_text_from_payload(ob.wlc_verse)


def _final_word_focus(ob: PoeticOddball) -> str | None:
    vels = ob.wlc_verse.get("vels") if isinstance(ob.wlc_verse, dict) else None
    if not isinstance(vels, list) or not vels:
        return None
    return _token_text(vels[-1]) or None


def _token_text(token: object) -> str:
    if isinstance(token, str):
        return token
    if isinstance(token, dict):
        for key in ("word", "text"):
            value = token.get(key)
            if isinstance(value, str):
                return value
    return ""


def _render_meta(ob: PoeticOddball) -> object:
    contents: list[object] = [f"tokens: {' '.join(ob.token_types)} · "]
    if ob.error is not None:
        n_accents = sum(
            1 for t in ob.token_types if t not in ("TILDE", "SOFPASUQ")
        )
        contents.append(
            f"parser stalled at accent {ob.error.accent_index}/{n_accents} "
            f"({ob.error.token_type}) · "
        )
    contents.append(wlc_utils_html.code(ob.output_file))
    return wlc_utils_html.para(tuple(contents), {"class": "poetic-meta"})


def _render_tree(ob: PoeticOddball) -> object:
    # missing_silluq carries a real ERROR-leaf tree; NO_PARSE has no valid tree, so
    # synthesize a flat best-effort one (each token a cell, capped by an ERROR leaf)
    # -- both render through the shared error-tree table.
    tree_text = (
        ob.tree_text
        if ob.kind == KIND_MISSING_SILLUQ
        else _no_parse_tree_text(
            ob.token_types,
            stall_index=ob.error.accent_index if ob.error is not None else None,
        )
    )
    tree = ob_error_context.parse_error_tree_from_text(tree_text)
    if tree is not None:
        return wlc_utils_html.div(
            (ob_tree_table.render_error_tree_table(tree),),
            {"class": "goerwitz-obs-tree-wrap"},
        )
    # Last-resort fallback: show the raw tree/NO_PARSE line verbatim.
    return wlc_utils_html.div(
        (wlc_utils_html.htel_mk_inline("pre", None, ob.tree_text),),
        {"class": "goerwitz-obs-tree-wrap"},
    )


def _no_parse_tree_text(
    token_types: tuple[str, ...], stall_index: int | None = None
) -> str:
    """A flat best-effort "tree" for a NO_PARSE verse, in print_tree text form.

    No valid parse exists, so this is not a real tree: a single ``no_parse`` branch
    whose leaves are the accent token types (the TILDE/SOFPASUQ structural bookends
    dropped, as in run_ply_poetic._no_parse_line), capped by an ``ERROR`` leaf. Fed
    through the shared error-tree table it puts each token in its own cell and
    highlights the ERROR cell -- more legible than the bare NO_PARSE token line, and
    visually consistent with the missing-silluq ERROR trees.

    When ``stall_index`` (the offending accent's 1-based ordinal, from ParseError) is
    given, that leaf is annotated ``← stalled here`` so the tree pinpoints where the
    parse dead-ended."""
    accents = [t for t in token_types if t not in ("TILDE", "SOFPASUQ")]
    leaves = list(accents)
    if stall_index is not None and 1 <= stall_index <= len(leaves):
        leaves[stall_index - 1] = f"{leaves[stall_index - 1]} ← stalled here"
    leaf_lines = "".join(f"  {leaf}\n" for leaf in leaves)
    return f"0 no_parse\n{leaf_lines}  ERROR\n"


def _build_filter_controls(counts: dict[str, int]) -> object:
    kind_fieldset = _fieldset(
        "Oddball kind",
        tuple(
            _checkbox("pf-kind", slug, label, counts[f"kind_{slug}"])
            for slug, label in _KIND_FILTER_LABEL.items()
        ),
    )
    book_fieldset = _fieldset(
        "Book",
        tuple(
            _checkbox("pf-book", slug, label, counts[f"book_{slug}"])
            for slug, label in _BOOK_LABEL.items()
        ),
    )
    agree_fieldset = _fieldset(
        "MAM compare",
        tuple(
            _checkbox("pf-agree", slug, label, counts[f"agree_{slug}"])
            for slug, label in _AGREE_LABEL.items()
        ),
    )
    count_para = wlc_utils_html.para("", {"class": "pf-count"})
    return wlc_utils_html.div(
        (kind_fieldset, book_fieldset, agree_fieldset, count_para),
        {"class": "goerwitz-filter"},
    )


def _fieldset(legend_text: str, labels: tuple[object, ...]) -> object:
    legend = wlc_utils_html.htel_mk("legend", None, legend_text)
    return wlc_utils_html.htel_mk("fieldset", None, (legend, *labels))


def _checkbox(css_class: str, value: str, label_text: str, count: int) -> object:
    input_el = wlc_utils_html.htel_mk_inline_nc(
        "input",
        {
            "type": "checkbox",
            "class": css_class,
            "value": value,
            "checked": "checked",
        },
    )
    return wlc_utils_html.htel_mk_inline(
        "label", None, (input_el, f" {label_text}", _count_span(count))
    )


def _count_span(count: int) -> object:
    # A zero count renders empty (no "(0)"); the filter script keeps it live.
    return wlc_utils_html.span_c(f" ({count})" if count else "", _COUNT_CLASS)


def _counts(oddballs: list[PoeticOddball]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for slug in _KIND_FILTER_LABEL:
        counts[f"kind_{slug}"] = 0
    for slug in _BOOK_LABEL:
        counts[f"book_{slug}"] = 0
    for slug in _AGREE_LABEL:
        counts[f"agree_{slug}"] = 0
    for ob in oddballs:
        counts[f"kind_{ob.kind}"] += 1
        counts[f"book_{ob.bb}"] += 1
        counts[f"agree_{_agree_slug(ob)}"] += 1
    return counts


def default_oddballs_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "ply-poetic" / "_oddballs.json"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_root / "gh-pages" / "accgram" / "poetic.html"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--mam-simple-dir",
        type=Path,
        default=default_mam_simple_dir(repo_root),
        help="Directory containing MAM-simple json-vtrad-bhs book files.",
    )
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=rtms_data.default_wlc422_kq_u_dir(repo_root),
        help="Directory of WLC 4.22 ketiv/qere Unicode 1verses_*.json files "
        "(for pointed-Hebrew verse rendering).",
    )
    parser.add_argument(
        "--uxlc-dir",
        type=Path,
        default=research_tao.default_uxlc_dir(repo_root),
        help="Directory of UXLC-39 book XML files (for the SAT focus-word table).",
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
    oddballs = collect_poetic_oddballs(
        args.mam_simple_dir, args.wlc422_kq_u_dir, args.uxlc_dir
    )

    payload = build_payload(oddballs, __file__)
    oddballs_out: Path = args.oddballs_out
    oddballs_out.parent.mkdir(parents=True, exist_ok=True)
    with oddballs_out.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")

    html_out: Path = args.html_out
    html_out.parent.mkdir(parents=True, exist_ok=True)
    wlc_utils_html.write_html_to_file(
        body_contents=render_body_contents(oddballs),
        write_ctx=wlc_utils_html.WriteCtx(
            title=_REPORT_TITLE,
            path=str(html_out),
            html_comment=provenance.generated_html_comment(__file__),
        ),
        path_to_style=rtms_report.path_to_gh_pages_style(html_out),
    )

    n_silluq = sum(1 for o in oddballs if o.kind == KIND_MISSING_SILLUQ)
    n_noparse = sum(1 for o in oddballs if o.kind == KIND_NO_PARSE)
    print(
        f"Poetic oddballs: {len(oddballs)} "
        f"({n_silluq} missing-silluq, {n_noparse} NO_PARSE)"
    )
    print(f"JSON: {oddballs_out}")
    print(f"HTML: {html_out}")
