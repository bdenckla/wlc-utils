r"""Detangle WLC's dually-cantillated prose passages into two single-cant streams (#36).

WLC 4.22 carries three prose loci where each word can bear *two* cantillation accents
-- the two readings (תחתון / עליון in the Decalogues, פשוטה / מדרשית in Gen 35:22) merged
into one ``cant-combined``-style stream.  The prose grammar cannot parse two accents per
word, so these verses are excluded from the normal run.  This module *detangles* them:
guided by MAM-simple's already-separated ``cant-alef`` / ``cant-bet`` threads, it splits
WLC's accents into a ``wlc-alef`` and a ``wlc-bet`` stream, each ordinary single
cantillation that the existing prose checker parses.

Throughout, a *chanted verse* is the cantillation unit delimited by a sof pasuq -- which,
in these passages, deliberately does NOT line up with the BHS numbered verse: each
reading carves the text into its own chanted verses that span or subdivide the numbered
verses (the elyon reading chants Exod 20:8-11 as one chanted verse; the taxton reading
makes each its own).  We segment strictly by each strand's own sof pasuq.

Design (all four points verified against the data, see issue #36):

* **Accents come from WLC; MAM is only the oracle** for which accent belongs to which
  thread and where each thread's chanted verses break.  The emitted accent on a word is WLC's
  own codepoint -- so a WLC-specific accent bug still surfaces -- *matched by identity*
  against the accent MAM's thread carries there, never by stored order.
* **Word-division (maqaf / paseq / sof pasuq) comes from each MAM thread**, which is why
  the loader (``mam_simple_verse``) exposes the threads as their own token streams.  WLC's
  one compromise maqaf pattern fits neither thread; the grammar is boundary-sensitive.
* **Alignment is pairwise** (WLC↔alef and WLC↔bet) on the consonant skeleton, so spelling
  / mater / ketiv-qere differences don't derail it.  Because the loader tokenizes paseq
  and ketiv-qere correctly, the would-be maqaf-join divergences (Exod 20:4 / Deut 5:8)
  collapse to clean 1:1 alignment.
* **Charity, two kinds.**  Where WLC genuinely lacks one thread's accent (it wrote only
  the other reading, e.g. a maqaf-join compaction), that one mark is *supplied* from MAM
  and inventoried (``SuppliedMark``) -- a supplied-mark word parses clean and is NOT an
  oddball.  Where WLC instead carries an accent *neither* thread explains (Deut 5:8
  ``תעשה``: a merkha where qadma is due), that is a candidate WLC error: WLC's actual mark
  is emitted (so the grammar reacts) and the discrepancy is flagged (``Anomaly``), never
  silently supplied.

MAM stress-helpers (zarqa/tsinnorit U+0598, and the doubled telisha / segol / pashta
helpers) are never imposed on the WLC streams: ``_emit_word`` drops the tsinnorit and the
second of any doubled accent.

This module is pure computation (no I/O); the driver (``dual_cant_run``) loads the inputs,
writes the trees, and renders the supplied-marks page.
"""

from __future__ import annotations

import difflib
import unicodedata
from dataclasses import dataclass

from accgram import accent_marks as am
from accgram import uni_to_marks
from accgram.prose_ply_grammar import LOCATION_ONLY, parse_tokens
from accgram.prose_scanner import HasLegarmeh, Token, scan_accents
from accgram.tree import TN, tree_to_obj
from cmn.wlc_book_codes import wlc_bb_to_bk39id

_TSINNORIT = am.TSINNORIT
_METEG = am.METEG
_SOF_PASUQ = am.SOF_PASUQ
_PASEQ = am.PASEQ
_SRC_MAQAF = uni_to_marks.MAQAF  # the Unicode maqaf U+05BE in the source words

# Characters of a thread word that survive into the emitted WLC-stream word: base
# consonants and the word-division / final marks (the spine), plus meteg (the scanner
# swallows it but recovers a verse-final silluq from it).  Accents are handled
# separately (matched/substituted/supplied); points/dagesh/CGJ are dropped.
_KEEP_NON_ACCENT = frozenset((_SRC_MAQAF, _SOF_PASUQ, _PASEQ, _METEG))


@dataclass(frozen=True)
class Passage:
    """One dually-cantillated locus, with its two threads' traditional labels."""

    name: str  # compact, e.g. "gn 35:22" / "ex 20:2-17"
    bb: str
    refs: tuple[tuple[int, int], ...]  # (chnu, vrnu) in source order
    alef_label: str  # cant-alef tradition name (pashut / taxton)
    bet_label: str  # cant-bet tradition name (midrashit / elyon)


PASSAGES: tuple[Passage, ...] = (
    Passage("gn 35:22", "gn", ((35, 22),), "pashut", "midrashit"),
    Passage("ex 20:2-17", "ex", tuple((20, v) for v in range(2, 18)), "taxton", "elyon"),
    Passage("dt 5:6-21", "dt", tuple((5, v) for v in range(6, 22)), "taxton", "elyon"),
)


def all_refs_by_book() -> dict[str, set[tuple[int, int]]]:
    """The refs to load (WLC index + MAM-simple) to cover every passage."""
    out: dict[str, set[tuple[int, int]]] = {}
    for passage in PASSAGES:
        out.setdefault(passage.bb, set()).update(passage.refs)
    return out


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SuppliedMark:
    """A thread accent absent from WLC, supplied from MAM (a clean charity)."""

    bcv: str
    thread: str  # "alef" / "bet"
    thread_label: str  # pashut / taxton / ...
    mam_word: str  # the MAM thread word carrying the supplied accent
    wlc_word: str  # WLC's word, which lacks it
    accent: str  # supplied accent codepoint
    accent_name: str
    reason: str


@dataclass(frozen=True)
class Anomaly:
    """A WLC accent that neither thread explains -- a candidate WLC dual-cant bug."""

    bcv: str
    thread: str
    thread_label: str
    mam_word: str
    wlc_word: str
    expected: str  # accent MAM's thread is due here
    expected_name: str
    found: str  # accent WLC actually wrote
    found_name: str


@dataclass(frozen=True)
class ChantedVerseResult:
    """One detangled chanted verse (sof-pasuq-delimited), fed to the prose grammar."""

    ref: str  # human attribution, e.g. "gn 35:22 [pashut] (chanted verse 1/2)"
    thread: str
    thread_label: str
    bcv_span: tuple[str, str]  # the BHS numbered verse(s) this chanted verse touches
    words: tuple[str, ...]  # emitted (pointed-Hebrew) stream words
    word_bcvs: tuple[str, ...]  # the numbered verse each word falls in (parallel to words)
    body: str  # scanner mark body
    tokens: tuple[str, ...]  # token type stream
    status: str  # clean / oddball / location_only / no_parse
    tree: dict | None


@dataclass(frozen=True)
class ThreadResult:
    thread: str
    thread_label: str
    chanted_verses: tuple[ChantedVerseResult, ...]


@dataclass(frozen=True)
class PassageResult:
    passage: Passage
    threads: tuple[ThreadResult, ThreadResult]  # alef, bet
    supplied_marks: tuple[SuppliedMark, ...]
    anomalies: tuple[Anomaly, ...]


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _skel(word: str) -> str:
    return "".join(c for c in word if "א" <= c <= "ת")


def _accents(word: str) -> list[str]:
    """All cantillation accents in a word (meteg excluded), in order."""
    return [c for c in word if uni_to_marks.is_accent(c)]


def _real_accents_ordered(word: str) -> list[str]:
    """A MAM thread word's genuine accents: dedup (collapse a doubled stress-helper)
    and drop the tsinnorit helper, preserving first-appearance order."""
    out: list[str] = []
    for c in word:
        if uni_to_marks.is_accent(c) and c != _TSINNORIT and c not in out:
            out.append(c)
    return out


# Codepoint -> the repo's accent spelling (het as X, never h; see accent_marks), so the
# inventory reads like the rest of the accgram pages ("tipexa", "atnax") rather than
# Unicode's "TIPEHA"/"ETNAHTA".  Built from the accent_marks constants (the single source
# of truth); first constant wins for an aliased codepoint.
_ACCENT_SPELLING: dict[str, str] = {}
for _name, _val in vars(am).items():
    if _name.isupper() and isinstance(_val, str) and len(_val) == 1 and uni_to_marks.is_accent(_val):
        _ACCENT_SPELLING.setdefault(_val, _name.lower().replace("_", " "))


def _accent_name(ch: str) -> str:
    spelling = _ACCENT_SPELLING.get(ch)
    if spelling is None:
        try:
            spelling = unicodedata.name(ch).replace("HEBREW ACCENT ", "").lower()
        except ValueError:
            spelling = "?"
    return f"{spelling} (U+{ord(ch):04X})"


@dataclass(frozen=True)
class _Tok:
    bcv: str
    text: str

    @property
    def skel(self) -> str:
        return _skel(self.text)


def _wlc_words(wlc_index: dict[str, dict], passage: Passage) -> list[_Tok]:
    """WLC's accent-bearing words across the passage, in order, tagged by bcv.

    Qere words are taken from a ketiv-qere element (matching the threads, which carry the
    qere); ``sam_pe_inun`` and other non-words are skipped."""
    out: list[_Tok] = []
    for chnu, vrnu in passage.refs:
        bcv = f"{passage.bb}{chnu}:{vrnu}"
        verse = wlc_index.get(bcv)
        if not isinstance(verse, dict):
            continue
        vels = verse.get("vels")
        if not isinstance(vels, list):
            continue
        for vel in vels:
            for word in _wlc_vel_words(vel):
                if _skel(word):
                    out.append(_Tok(bcv, word))
    return out


def _wlc_vel_words(vel: object) -> list[str]:
    if isinstance(vel, str):
        return [vel]
    if isinstance(vel, dict):
        word = vel.get("word")
        if isinstance(word, str):
            return [word]
        kq = vel.get("kq")
        if isinstance(kq, (list, tuple)) and len(kq) == 2 and isinstance(kq[1], list):
            out: list[str] = []
            for qvel in kq[1]:
                if isinstance(qvel, str):
                    out.append(qvel)
                elif isinstance(qvel, dict) and isinstance(qvel.get("word"), str):
                    out.append(qvel["word"])
            return out
    return []


def _thread_tokens(
    mam_by_bcv: dict[str, dict], passage: Passage, vels_key: str
) -> list[_Tok]:
    """One thread's full token stream across the passage (words AND the non-word
    paseq / standalone sof-pasuq tokens), in order, tagged by bcv."""
    out: list[_Tok] = []
    for chnu, vrnu in passage.refs:
        bcv = f"{passage.bb}{chnu}:{vrnu}"
        info = mam_by_bcv.get(bcv)
        if not isinstance(info, dict):
            continue
        verse = info.get("mam_simple_verse")
        if not isinstance(verse, dict):
            continue
        for tok in verse.get(vels_key, []):
            if isinstance(tok, str) and tok:
                out.append(_Tok(bcv, tok))
    return out


# --------------------------------------------------------------------------- #
# Alignment + per-word assignment
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class _Block:
    tag: str
    wlc_idxs: tuple[int, ...]  # indices into the WLC word list
    tok_idxs: tuple[int, ...]  # indices into the thread token list (word tokens only)


def _blocks(wlc: list[_Tok], thread: list[_Tok]) -> list[_Block]:
    """Pairwise skeleton alignment of WLC words to one thread's *word* tokens."""
    word_idxs = [i for i, t in enumerate(thread) if t.skel]
    sm = difflib.SequenceMatcher(
        a=[w.skel for w in wlc],
        b=[thread[i].skel for i in word_idxs],
        autojunk=False,
    )
    out: list[_Block] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        out.append(
            _Block(tag, tuple(range(i1, i2)), tuple(word_idxs[j] for j in range(j1, j2)))
        )
    return out


def _equal_acc_by_wlc(
    wlc: list[_Tok], thread: list[_Tok], blocks: list[_Block]
) -> dict[int, set[str]]:
    """Map each 1:1-aligned WLC word index to that thread's real accents there.

    Used to look up the *other* thread's accents when deciding supply vs anomaly."""
    out: dict[int, set[str]] = {}
    for block in blocks:
        if block.tag == "equal":
            for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
                out[wi] = set(_real_accents_ordered(thread[ti].text))
    return out


@dataclass(frozen=True)
class _Assign:
    substitutions: dict[str, str]  # mam accent -> wlc accent (anomaly only)
    supplies: tuple[SuppliedMark, ...]
    anomalies: tuple[Anomaly, ...]


_NO_ASSIGN = _Assign({}, (), ())


def _assign_word(
    *,
    wlc_word: str,
    mam_word: str,
    other_real: set[str],
    bcv: str,
    thread: str,
    thread_label: str,
    other_label: str,
) -> _Assign:
    """Decide one equal-aligned word's emitted accents for one thread.

    Match the thread's (deduped, helper-free) accents against WLC's accents by identity.
    A thread accent absent from WLC is either a clean *supply* (WLC carries only the other
    thread's reading here) or, if WLC carries an accent neither thread explains, an
    *anomaly* (emit WLC's mark, flag it)."""
    need = _real_accents_ordered(mam_word)
    have = set(_accents(wlc_word))
    missing = [a for a in need if a not in have]
    if not missing:
        return _NO_ASSIGN

    # WLC accents this word carries that belong to neither thread's reading here.
    leftover = sorted(have - set(need) - other_real, key=ord)

    substitutions: dict[str, str] = {}
    supplies: list[SuppliedMark] = []
    anomalies: list[Anomaly] = []
    for i, accent in enumerate(missing):
        if i < len(leftover):
            found = leftover[i]
            substitutions[accent] = found
            anomalies.append(
                Anomaly(
                    bcv=bcv,
                    thread=thread,
                    thread_label=thread_label,
                    mam_word=mam_word,
                    wlc_word=wlc_word,
                    expected=accent,
                    expected_name=_accent_name(accent),
                    found=found,
                    found_name=_accent_name(found),
                )
            )
        else:
            supplies.append(
                SuppliedMark(
                    bcv=bcv,
                    thread=thread,
                    thread_label=thread_label,
                    mam_word=mam_word,
                    wlc_word=wlc_word,
                    accent=accent,
                    accent_name=_accent_name(accent),
                    reason=_supply_reason(wlc_word, have, other_label),
                )
            )
    return _Assign(substitutions, tuple(supplies), tuple(anomalies))


def _supply_reason(wlc_word: str, wlc_have: set[str], other_label: str) -> str:
    if _SOF_PASUQ in wlc_word:
        return (
            f"WLC ends a chanted verse here in the {other_label} reading (silluq + sof"
            " pasuq), so this reading's continuing accent is supplied from MAM."
        )
    if not wlc_have:
        return (
            "WLC writes no cantillation accent on this word (it is maqaf-joined in the"
            f" {other_label} reading), so the mark is supplied from MAM."
        )
    others = ", ".join(_accent_name(a) for a in sorted(wlc_have, key=ord))
    return (
        f"WLC writes only the {other_label} reading here ({others}), so this thread's"
        " mark is supplied from MAM."
    )


def _assign_pooled(
    *, mam_word: str, pool: list[str], bcv: str, thread: str, thread_label: str
) -> _Assign:
    """Fallback for a non-equal alignment block (maqaf-join etc.): match a thread word's
    accents against the block's pooled WLC accents by identity.  No genuine divergence
    block survives the loader's paseq/ketiv-qere tokenization in the three loci, so this
    is defensive; a thread accent with no pooled match is recorded as a supply."""
    need = _real_accents_ordered(mam_word)
    supplies: list[SuppliedMark] = []
    for accent in need:
        if accent in pool:
            pool.remove(accent)
        else:
            supplies.append(
                SuppliedMark(
                    bcv=bcv,
                    thread=thread,
                    thread_label=thread_label,
                    mam_word=mam_word,
                    wlc_word="",
                    accent=accent,
                    accent_name=_accent_name(accent),
                    reason=(
                        "WLC tokenizes this span differently (word-division taken from"
                        " MAM); the mark is supplied from MAM."
                    ),
                )
            )
    return _Assign({}, tuple(supplies), ())


# --------------------------------------------------------------------------- #
# Emission + segmentation + parsing
# --------------------------------------------------------------------------- #
def _emit_word(text: str, substitutions: dict[str, str]) -> str:
    """Build one WLC-stream word on the MAM thread word's spine.

    Keep base letters and the spine marks (maqaf / paseq / sof pasuq / meteg); drop the
    tsinnorit stress-helper and the second of any doubled accent (a stress-helper); apply
    anomaly substitutions (MAM accent -> WLC's actual accent); drop points/dagesh/CGJ."""
    out: list[str] = []
    seen: set[str] = set()
    for ch in text:
        if uni_to_marks.is_accent(ch):
            if ch == _TSINNORIT or ch in seen:
                continue
            seen.add(ch)
            out.append(substitutions.get(ch, ch))
        elif uni_to_marks.is_base_letter(ch) or ch in _KEEP_NON_ACCENT:
            out.append(ch)
    return "".join(out)


def _emit_stream(thread: list[_Tok], assigns: dict[int, _Assign]) -> list[_Tok]:
    """Emit the thread's stream as pointed-Hebrew vels, folding each non-word token
    (paseq / standalone sof pasuq) onto the previous word (WLC's attached convention)."""
    vels: list[_Tok] = []
    for i, tok in enumerate(thread):
        if tok.skel:
            sub = assigns.get(i, _NO_ASSIGN).substitutions
            vels.append(_Tok(tok.bcv, _emit_word(tok.text, sub)))
        else:
            attach = _emit_word(tok.text, {})
            if vels and attach:
                vels[-1] = _Tok(vels[-1].bcv, vels[-1].text + attach)
            elif attach:
                vels.append(_Tok(tok.bcv, attach))
    return vels


def _segment(vels: list[_Tok]) -> list[list[_Tok]]:
    """Split the stream into chanted verses at every sof pasuq the strand carries."""
    chanted_verses: list[list[_Tok]] = []
    cur: list[_Tok] = []
    for vel in vels:
        cur.append(vel)
        if _SOF_PASUQ in vel.text:
            chanted_verses.append(cur)
            cur = []
    if cur:
        chanted_verses.append(cur)
    return chanted_verses


def _tree_has_error(tree: TN | None) -> bool:
    if tree is None:
        return False
    if tree.left is not None:
        return _tree_has_error(tree.left) or _tree_has_error(tree.right)
    return "ERROR" in tree.leaves


def _bcv_span_ref(cv: list[_Tok], label: str, ordinal: str) -> str:
    bcvs = [v.bcv for v in cv]
    first, last = bcvs[0], bcvs[-1]
    where = first if first == last else f"{first}–{last.split(':')[-1]}"
    return f"{where} [{label}]{ordinal}"


def _parse_chanted_verse(
    passage: Passage,
    cv: list[_Tok],
    thread: str,
    label: str,
    ordinal: str,
    parser,
) -> ChantedVerseResult:
    body = uni_to_marks.verse_to_marks({"vels": [v.text for v in cv]})
    # None of the three loci is a HasLegarmeh passage, so a fresh per-verse instance is
    # immaterial; pass the strand's first numbered verse for the (unused-here) ref.
    first_bcv = cv[0].bcv
    chv = first_bcv[len(passage.bb):]
    chnu = int(chv.split(":")[0])
    vrnu = int(chv.split(":")[1])
    tokens = [Token("TILDE", "")] + scan_accents(
        body, passage.bb, chnu, vrnu, HasLegarmeh()
    )
    tree = parse_tokens(parser, tokens)
    if tree is None:
        status, tree_obj = "no_parse", None
    elif tree is LOCATION_ONLY:
        status, tree_obj = "location_only", None
    else:
        status = "oddball" if _tree_has_error(tree) else "clean"
        tree_obj = tree_to_obj(tree)
    return ChantedVerseResult(
        ref=_bcv_span_ref(cv, label, ordinal),
        thread=thread,
        thread_label=label,
        bcv_span=(cv[0].bcv, cv[-1].bcv),
        words=tuple(v.text for v in cv),
        word_bcvs=tuple(v.bcv for v in cv),
        body=body,
        tokens=tuple(t.type for t in tokens),
        status=status,
        tree=tree_obj,
    )


# --------------------------------------------------------------------------- #
# Driver entry points
# --------------------------------------------------------------------------- #
def _process_thread(
    passage: Passage,
    thread: str,
    label: str,
    other_label: str,
    wlc: list[_Tok],
    thread_toks: list[_Tok],
    blocks: list[_Block],
    other_acc: dict[int, set[str]],
    parser,
) -> tuple[ThreadResult, list[SuppliedMark], list[Anomaly]]:
    assigns: dict[int, _Assign] = {}
    supplies: list[SuppliedMark] = []
    anomalies: list[Anomaly] = []
    for block in blocks:
        if block.tag == "equal":
            for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
                res = _assign_word(
                    wlc_word=wlc[wi].text,
                    mam_word=thread_toks[ti].text,
                    other_real=other_acc.get(wi, set()),
                    bcv=thread_toks[ti].bcv,
                    thread=thread,
                    thread_label=label,
                    other_label=other_label,
                )
                assigns[ti] = res
                supplies.extend(res.supplies)
                anomalies.extend(res.anomalies)
        elif block.tok_idxs:
            pool = [a for wi in block.wlc_idxs for a in _accents(wlc[wi].text)]
            for ti in block.tok_idxs:
                res = _assign_pooled(
                    mam_word=thread_toks[ti].text,
                    pool=pool,
                    bcv=thread_toks[ti].bcv,
                    thread=thread,
                    thread_label=label,
                )
                assigns[ti] = res
                supplies.extend(res.supplies)

    vels = _emit_stream(thread_toks, assigns)
    chanted_verses = _segment(vels)
    n = len(chanted_verses)
    results: list[ChantedVerseResult] = []
    for idx, cv in enumerate(chanted_verses, start=1):
        ordinal = f" (chanted verse {idx}/{n})" if n > 1 else ""
        results.append(_parse_chanted_verse(passage, cv, thread, label, ordinal, parser))
    return (
        ThreadResult(thread=thread, thread_label=label, chanted_verses=tuple(results)),
        supplies,
        anomalies,
    )


def detangle_passage(
    passage: Passage,
    wlc_index: dict[str, dict],
    mam_by_bcv: dict[str, dict],
    parser,
) -> PassageResult:
    wlc = _wlc_words(wlc_index, passage)
    alef = _thread_tokens(mam_by_bcv, passage, "vels_cant_alef")
    bet = _thread_tokens(mam_by_bcv, passage, "vels_cant_bet")

    alef_blocks = _blocks(wlc, alef)
    bet_blocks = _blocks(wlc, bet)
    alef_acc = _equal_acc_by_wlc(wlc, alef, alef_blocks)
    bet_acc = _equal_acc_by_wlc(wlc, bet, bet_blocks)

    alef_result, alef_sup, alef_anom = _process_thread(
        passage, "alef", passage.alef_label, passage.bet_label,
        wlc, alef, alef_blocks, bet_acc, parser,
    )
    bet_result, bet_sup, bet_anom = _process_thread(
        passage, "bet", passage.bet_label, passage.alef_label,
        wlc, bet, bet_blocks, alef_acc, parser,
    )
    return PassageResult(
        passage=passage,
        threads=(alef_result, bet_result),
        supplied_marks=tuple(alef_sup + bet_sup),
        anomalies=tuple(alef_anom + bet_anom),
    )


def detangle_all(
    wlc_index: dict[str, dict], mam_by_bcv: dict[str, dict], parser
) -> list[PassageResult]:
    return [detangle_passage(p, wlc_index, mam_by_bcv, parser) for p in PASSAGES]


# --------------------------------------------------------------------------- #
# Folding detangled oddities into the (numbered-verse-keyed) prose oddball reports
# --------------------------------------------------------------------------- #
_PASSAGE_BY_BOOK: dict[str, Passage] = {p.bb: p for p in PASSAGES}


def passage_for_book(bb: str) -> Passage | None:
    return _PASSAGE_BY_BOOK.get(bb)


def _join_for_display(words: tuple[str, ...]) -> str:
    """Join chanted-verse words for display: a space between words, except none after a
    maqaf (the joined word already carries it)."""
    out = ""
    for word in words:
        if out and not out.endswith(_SRC_MAQAF):
            out += " "
        out += word
    return out


def chanted_verse_to_prose_record(cv: ChantedVerseResult, bb: str) -> dict[str, object]:
    """Shape one detangled chanted verse as a prose ``*_ag.json`` record.

    The prose oddball pipeline is keyed by the BHS numbered verse (``bcv``) and looks the
    parse tree up by that key, so a chanted verse is attributed to its first numbered
    verse.  The thread and the full chanted-verse span are kept in ``dual_cant_*`` fields
    for provenance (the goerwitz row re-derives its visible ref from the bcv); the
    ``dual_cant`` flag marks the record so a re-run can replace it idempotently."""
    first_bcv = cv.bcv_span[0]
    chnu, vrnu = first_bcv[len(bb):].split(":")
    return {
        "ref": f"{wlc_bb_to_bk39id(bb)} {chnu}:{vrnu}",
        "bcv": first_bcv,
        "dual_cant": True,
        "dual_cant_thread": cv.thread,
        "dual_cant_thread_label": cv.thread_label,
        "dual_cant_ref": cv.ref,
        "input": {
            "unicode": _join_for_display(cv.words),
            "marks": cv.body,
            "tokens": list(cv.tokens),
        },
        "status": cv.status,
        "tree": cv.tree,
    }


def folded_oddball_records(
    bb: str, wlc_index: dict[str, dict], mam_by_bcv: dict[str, dict], parser
) -> list[dict[str, object]]:
    """The detangled *oddity* records for one book, to fold into its prose output.

    Only non-clean chanted verses (a genuine WLC dual-cant bug -> oddball / no_parse /
    location_only) are folded; clean and supplied-mark chanted verses are not oddballs.
    A supplied-mark chanted verse parses clean, so it never appears here (the issue's
    reporting requirement)."""
    passage = passage_for_book(bb)
    if passage is None:
        return []
    result = detangle_passage(passage, wlc_index, mam_by_bcv, parser)
    records: list[dict[str, object]] = []
    seen: dict[str, str] = {}
    for thread in result.threads:
        for cv in thread.chanted_verses:
            if cv.status == "clean":
                continue
            record = chanted_verse_to_prose_record(cv, bb)
            bcv = str(record["bcv"])
            if bcv in seen:
                raise ValueError(
                    f"Two folded dual-cant oddities share bcv {bcv} ({seen[bcv]} and "
                    f"{cv.ref}); the numbered-verse-keyed prose oddball pipeline cannot "
                    "represent both -- revisit the fold-in attribution."
                )
            seen[bcv] = cv.ref
            records.append(record)
    return records
