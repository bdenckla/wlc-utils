r"""Detangle WLC's dually-cantillated prose passages into two single-cant streams (#36).

WLC 4.22 carries three prose loci where each word can bear *two* cantillation accents
-- the two readings (תחתון / עליון in the Decalogues, פשוטה / מדרשית in Gen 35:22) merged
into one ``cant-combined``-style stream.  The prose grammar cannot parse two accents per
word, so these verses are excluded from the normal run.  This module *detangles* them:
guided by MAM-simple's already-separated ``cant-alef`` / ``cant-bet`` strands, it splits
WLC's accents into a ``wlc-alef`` and a ``wlc-bet`` stream, each ordinary single
cantillation that the existing prose checker parses.

Throughout, a *chanted verse* is the cantillation unit delimited by a sof pasuq -- which,
in these passages, deliberately does NOT line up with the BHS numbered verse: each
reading carves the text into its own chanted verses that span or subdivide the numbered
verses (the elyon reading chants Exod 20:8-11 as one chanted verse; the taxton reading
makes each its own).  We segment strictly by each strand's own sof pasuq.

Design (all four points verified against the data, see issue #36):

* **Accents come from WLC; MAM is only the oracle** for which accent belongs to which
  strand and where each strand's chanted verses break.  The emitted accent on a word is WLC's
  own codepoint -- so a WLC-specific accent bug still surfaces -- *matched by identity*
  against the accent MAM's strand carries there, never by stored order.
* **Word-division (maqaf / paseq / sof pasuq) comes from each MAM strand**, which is why
  the loader (``mam_simple_verse``) exposes the strands as their own token streams.  WLC's
  one compromise maqaf pattern fits neither strand; the grammar is boundary-sensitive.
* **Alignment is pairwise** (WLC↔alef and WLC↔bet) on the consonant skeleton, so spelling
  / mater / ketiv-qere differences don't derail it.  Because the loader tokenizes paseq
  and ketiv-qere correctly, the would-be maqaf-join divergences (Exod 20:4 / Deut 5:8)
  collapse to clean 1:1 alignment.
* **Charity, two kinds.**  Where WLC genuinely lacks one strand's accent (it wrote only
  the other reading, e.g. a maqaf-join compaction), that one mark is *supplied* from MAM
  and inventoried (``SuppliedMark``) -- a supplied-mark word parses clean and is NOT an
  ungrammatical verse.  Where WLC instead carries an accent *neither* strand explains (Deut 5:8
  ``תעשה``: a merkha where qadma is due), that is a candidate WLC error: WLC's actual mark
  is emitted (so the grammar reacts) and the discrepancy is flagged (``Anomaly``), never
  silently supplied.  Because WLC's single tangled mark serves *both* readings, such a
  rogue accent is routed into both strands -- as the short strand's substitution where it
  is due an accent, and as a *stray* in the strand that is due none (only a meteg).  The
  one Deut 5:8 merkha is thus the taḥton's qadma substitute and the elyon's stray, so it
  surfaces as an ungrammatical verse in *both* readings (two anomalies, one underlying WLC mark).

MAM stress-helpers (zarqa/tsinnorit U+0598, and the doubled telisha / segol / pashta
helpers) are never imposed on the WLC streams: ``_emit_word`` drops the tsinnorit and the
second of any doubled accent.  MAM's metegs are likewise stripped from the emitted
stream (``_strip_nonfinal_meteg``), keeping only the verse-final meteg the scanner reads
as silluq -- the rest are swallowed by the scanner, so dropping them is parse-neutral.

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

# Characters of a strand word that survive into the emitted WLC-stream word: base
# consonants and the word-division / final marks (the spine), plus meteg (kept here so the
# scanner can recover a verse-final silluq from it; the non-final metegs are stripped
# afterwards by ``_strip_nonfinal_meteg``).  Accents are handled separately
# (matched/substituted/supplied); points/dagesh/CGJ are dropped.
_KEEP_NON_ACCENT = frozenset((_SRC_MAQAF, _SOF_PASUQ, _PASEQ, _METEG))


@dataclass(frozen=True)
class Passage:
    """One dually-cantillated locus, with its two strands' traditional labels."""

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
    """A strand accent absent from WLC, supplied from MAM (a clean charity)."""

    bcv: str
    strand: str  # "alef" / "bet"
    strand_label: str  # pashut / taxton / ...
    mam_word: str  # the MAM strand word carrying the supplied accent
    wlc_word: str  # WLC's word, which lacks it
    accent: str  # supplied accent codepoint
    accent_name: str
    reason: str
    source: str = "mam"  # "mam" (MAM only) or "lc" (the LC gives non-definitive support)


@dataclass(frozen=True)
class Anomaly:
    """A WLC accent that neither strand explains -- a candidate WLC dual-cant bug."""

    bcv: str
    strand: str
    strand_label: str
    mam_word: str
    wlc_word: str
    expected: str  # accent MAM's strand is due here
    expected_name: str
    found: str  # accent WLC actually wrote
    found_name: str


@dataclass(frozen=True)
class DivisionChange:
    """A word-division mark (maqaf or sof pasuq) a reading adds or erases relative to WLC's
    single tangled form.

    Each reading takes its word-division from its MAM strand, so against WLC's one compromise
    division it both adds marks (where this reading divides and WLC did not) and erases them
    (where WLC divided for the other reading).  Narrow-sense paseq is not part of the accent
    grammar and is not tracked; a legarmeh's paseq is always WLC's own (see the page), so no
    accent-bearing division mark beyond maqaf and sof pasuq changes here."""

    bcv: str
    strand: str  # "alef" / "bet"
    strand_label: str  # pashut / taxton / ...
    mark: str  # "maqaf" / "sof pasuq"
    delta: str  # "added" (strand has, WLC lacks) / "erased" (WLC has, strand lacks)
    wlc_word: str  # the aligned WLC word
    mam_word: str  # the aligned MAM strand word


@dataclass(frozen=True)
class ChantedVerseResult:
    """One detangled chanted verse (sof-pasuq-delimited), fed to the prose grammar."""

    ref: str  # human attribution, e.g. "gn 35:22 [pashut] (chanted verse 1/2)"
    strand: str
    strand_label: str
    bcv_span: tuple[str, str]  # the BHS numbered verse(s) this chanted verse touches
    words: tuple[str, ...]  # emitted (pointed-Hebrew) stream words
    word_bcvs: tuple[str, ...]  # the numbered verse each word falls in (parallel to words)
    body: str  # scanner mark body
    tokens: tuple[str, ...]  # token type stream
    status: str  # clean / ungrammatical / location_only / no_parse
    tree: dict | None
    word_leaf_counts: tuple[int, ...]  # parse-tree leaves each word contributes (parallel
    # to words); lets the renderer gray a chanted verse's out-of-focus numbered verses by
    # column.  Exact in error-free spans; an ERROR may absorb tokens, but only within the
    # focus verse, so the leading/trailing flanks the renderer grays stay exact.


@dataclass(frozen=True)
class StrandResult:
    strand: str
    strand_label: str
    chanted_verses: tuple[ChantedVerseResult, ...]


@dataclass(frozen=True)
class PassageResult:
    passage: Passage
    strands: tuple[StrandResult, StrandResult]  # alef, bet
    supplied_marks: tuple[SuppliedMark, ...]
    anomalies: tuple[Anomaly, ...]
    division_changes: tuple[DivisionChange, ...] = ()


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _skel(word: str) -> str:
    return "".join(c for c in word if "א" <= c <= "ת")


def _accents(word: str) -> list[str]:
    """All cantillation accents in a word (meteg excluded), in order."""
    return [c for c in word if uni_to_marks.is_accent(c)]


def _real_accents_ordered(word: str) -> list[str]:
    """A MAM strand word's genuine accents: dedup (collapse a doubled stress-helper)
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


def _no_accent_due_name(mam_word: str) -> str:
    """The ``expected`` description for a stray anomaly: this strand is due no cantillation
    accent here (it carries only a meteg, where MAM's word has one)."""
    if _METEG in mam_word:
        return "no cantillation accent (only a meteg is due)"
    return "no cantillation accent"


@dataclass(frozen=True)
class _Tok:
    bcv: str
    text: str

    @property
    def skel(self) -> str:
        return _skel(self.text)


def _wlc_words(wlc_index: dict[str, dict], passage: Passage) -> list[_Tok]:
    """WLC's accent-bearing words across the passage, in order, tagged by bcv.

    Qere words are taken from a ketiv-qere element (matching the strands, which carry the
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


def _strand_tokens(
    mam_by_bcv: dict[str, dict], passage: Passage, vels_key: str
) -> list[_Tok]:
    """One strand's full token stream across the passage (words AND the non-word
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
    tok_idxs: tuple[int, ...]  # indices into the strand token list (word tokens only)


def _blocks(wlc: list[_Tok], strand: list[_Tok]) -> list[_Block]:
    """Pairwise skeleton alignment of WLC words to one strand's *word* tokens."""
    word_idxs = [i for i, t in enumerate(strand) if t.skel]
    sm = difflib.SequenceMatcher(
        a=[w.skel for w in wlc],
        b=[strand[i].skel for i in word_idxs],
        autojunk=False,
    )
    out: list[_Block] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        out.append(
            _Block(tag, tuple(range(i1, i2)), tuple(word_idxs[j] for j in range(j1, j2)))
        )
    return out


def _equal_acc_by_wlc(
    wlc: list[_Tok], strand: list[_Tok], blocks: list[_Block]
) -> dict[int, set[str]]:
    """Map each 1:1-aligned WLC word index to that strand's real accents there.

    Used to look up the *other* strand's accents when deciding supply vs anomaly."""
    out: dict[int, set[str]] = {}
    for block in blocks:
        if block.tag == "equal":
            for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
                out[wi] = set(_real_accents_ordered(strand[ti].text))
    return out


# Word-division marks that ARE accent-relevant (the inventory tracks these); narrow-sense
# paseq is not part of the accent grammar, so it is deliberately excluded.
_DIVISION_MARKS: tuple[tuple[str, str], ...] = (
    (_SRC_MAQAF, "maqaf"),
    (_SOF_PASUQ, "sof pasuq"),
)


def _trailing_division(word: str) -> set[str]:
    """The maqaf / sof pasuq a word itself carries."""
    return {ch for ch, _ in _DIVISION_MARKS if ch in word}


def _strand_division_after(strand: list[_Tok], i: int) -> set[str]:
    """The division marks the strand carries after word-token ``i``: trailing marks on the
    word plus any immediately following non-word tokens (a standalone sof pasuq)."""
    marks = _trailing_division(strand[i].text)
    j = i + 1
    while j < len(strand) and not strand[j].skel:
        marks |= _trailing_division(strand[j].text)
        j += 1
    return marks


def _division_changes(
    wlc: list[_Tok],
    strand_toks: list[_Tok],
    blocks: list[_Block],
    strand: str,
    label: str,
) -> list[DivisionChange]:
    """The maqaf / sof-pasuq marks this strand adds or erases vs WLC's tangled division.

    Compares each 1:1-aligned WLC word's trailing division against the strand's at the same
    position (the strand's word-division is MAM's).  ``added`` = the strand divides where WLC
    did not; ``erased`` = WLC divided for the other reading and this strand does not."""
    changes: list[DivisionChange] = []
    for block in blocks:
        if block.tag != "equal":
            continue
        for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
            wlc_marks = _trailing_division(wlc[wi].text)
            strand_marks = _strand_division_after(strand_toks, ti)
            for ch, name in _DIVISION_MARKS:
                in_wlc, in_strand = ch in wlc_marks, ch in strand_marks
                if in_strand and not in_wlc:
                    delta = "added"
                elif in_wlc and not in_strand:
                    delta = "erased"
                else:
                    continue
                changes.append(
                    DivisionChange(
                        bcv=strand_toks[ti].bcv,
                        strand=strand,
                        strand_label=label,
                        mark=name,
                        delta=delta,
                        wlc_word=wlc[wi].text,
                        mam_word=strand_toks[ti].text,
                    )
                )
    return changes


def _equal_meteg_by_wlc(
    wlc: list[_Tok], strand: list[_Tok], blocks: list[_Block]
) -> dict[int, bool]:
    """Map each 1:1-aligned WLC word index to whether that strand's word carries a *medial*
    meteg (U+05BD not before a sof pasuq, i.e. not a verse-final silluq).

    A medial meteg is a transcription-ambiguous mark -- it ``half-includes`` as an accent,
    and WLC may have written a real accent (merkha/tipexa) where it is due, or vice versa.
    So the strand whose mark here is a sole meteg is the ambiguous slot that absorbs WLC's
    actual mark; the other strand's distinct accent is the omitted one, supplied from MAM."""
    out: dict[int, bool] = {}
    for block in blocks:
        if block.tag == "equal":
            for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
                w = strand[ti].text
                out[wi] = _METEG in w and _SOF_PASUQ not in w
    return out


@dataclass(frozen=True)
class _Assign:
    substitutions: dict[str, str]  # mam accent -> wlc accent (anomaly only)
    supplies: tuple[SuppliedMark, ...]
    anomalies: tuple[Anomaly, ...]
    strays: tuple[str, ...] = ()  # WLC accents this strand has no slot for, emitted anyway


_NO_ASSIGN = _Assign({}, (), ())


def _assign_word(
    *,
    wlc_word: str,
    mam_word: str,
    other_real: set[str],
    other_meteg: bool,
    bcv: str,
    strand: str,
    strand_label: str,
    other_label: str,
) -> _Assign:
    """Decide one equal-aligned word's emitted accents for one strand.

    Match the strand's (deduped, helper-free) accents against WLC's accents by identity.
    A strand accent absent from WLC is either a clean *supply* (WLC carries only the other
    strand's reading here) or, if WLC carries an accent neither strand explains, an
    *anomaly* (emit WLC's mark, flag it).

    A WLC accent belonging to *neither* strand (a true leftover) is the candidate WLC bug,
    homed in the strand whose mark here is a sole (medial) meteg -- the transcription-
    ambiguous slot that absorbs WLC's actual mark.  When the OTHER strand is that meteg slot
    (``other_meteg`` and it is due no real accent), the leftover is ceded to it, and this
    strand instead *supplies* its own omitted accent (clean, with some manuscript support).
    When THIS strand is the meteg slot, the leftover has no real-accent slot here yet WLC
    wrote it, so this reading must confront the rogue mark: it is emitted as a *stray* (the
    grammar reacts) and flagged as a no-accent-due anomaly.  dt 5:8's merkha thus *supplies*
    the omitted qadma in the taxton (clean) AND is the elyon's *stray* (ungrammatical) -- one WLC
    mark, charitably read in the taxton and flagged in the elyon."""
    need = _real_accents_ordered(mam_word)
    have = set(_accents(wlc_word))
    missing = [a for a in need if a not in have]

    # WLC accents this word carries that belong to neither strand's reading here.
    leftover = sorted(have - set(need) - other_real, key=ord)

    # A leftover that belongs to the OTHER strand's sole-meteg slot is ceded to it (that
    # strand emits it as its stray); this strand then supplies its own omitted accent, which
    # has some manuscript support -- WLC wrote the other reading's mark, not this reading's.
    ceded = tuple(leftover) if (other_meteg and not other_real and leftover) else ()
    if ceded:
        leftover = []

    substitutions: dict[str, str] = {}
    supplies: list[SuppliedMark] = []
    anomalies: list[Anomaly] = []
    used_leftover: set[str] = set()
    for i, accent in enumerate(missing):
        if i < len(leftover):
            found = leftover[i]
            used_leftover.add(found)
            substitutions[accent] = found
            anomalies.append(
                Anomaly(
                    bcv=bcv,
                    strand=strand,
                    strand_label=strand_label,
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
                    strand=strand,
                    strand_label=strand_label,
                    mam_word=mam_word,
                    wlc_word=wlc_word,
                    accent=accent,
                    accent_name=_accent_name(accent),
                    reason=_supply_reason(wlc_word, have, other_label, ceded=ceded),
                    source="lc" if ceded else "mam",
                )
            )

    # A leftover WLC accent this strand has no slot for becomes a *stray* only when the
    # OTHER strand is itself short an accent here -- i.e. the leftover is the rogue mark
    # WLC wrote *instead of* the proper pointing, which the other strand absorbs as a
    # substitution.  (A leftover where neither strand is missing anything is a benign extra
    # mark -- a meteg the strands don't track -- and is dropped, as before.)  Emit such a
    # stray so this reading is confronted with the rogue mark too, and flag it as a
    # no-accent-due anomaly.
    other_short = bool(other_real - have)
    strays = tuple(a for a in leftover if a not in used_leftover) if other_short else ()
    for accent in strays:
        anomalies.append(
            Anomaly(
                bcv=bcv,
                strand=strand,
                strand_label=strand_label,
                mam_word=mam_word,
                wlc_word=wlc_word,
                expected="",
                expected_name=_no_accent_due_name(mam_word),
                found=accent,
                found_name=_accent_name(accent),
            )
        )

    if not missing and not strays:
        return _NO_ASSIGN
    return _Assign(substitutions, tuple(supplies), tuple(anomalies), strays)


def _supply_reason(
    wlc_word: str, wlc_have: set[str], other_label: str, *, ceded: tuple[str, ...] = ()
) -> str:
    if ceded:
        names = ", ".join(_accent_name(a) for a in ceded)
        return (
            f"WLC writes a {names} here that belongs to the {other_label} reading (where it"
            " mis-transcribes a meteg); this reading's own accent is omitted by WLC and"
            " supplied from MAM."
        )
    if _SOF_PASUQ in wlc_word:
        return (
            f"WLC ends a chanted verse here in the {other_label} reading (silluq + sof"
            " pasuq), so this reading's continuing accent is supplied from MAM."
        )
    if not wlc_have:
        form = "maqaf-joined, carrying a meteg" if _METEG in wlc_word else "maqaf-joined"
        return (
            f"WLC writes only the {other_label} reading here ({form}, with no cantillation"
            " accent of its own), so this reading's mark is supplied from MAM."
        )
    others = ", ".join(_accent_name(a) for a in sorted(wlc_have, key=ord))
    return (
        f"WLC writes only the {other_label} reading here ({others}), so this strand's"
        " mark is supplied from MAM."
    )


def _assign_pooled(
    *, mam_word: str, pool: list[str], bcv: str, strand: str, strand_label: str
) -> _Assign:
    """Fallback for a non-equal alignment block (maqaf-join etc.): match a strand word's
    accents against the block's pooled WLC accents by identity.  No genuine divergence
    block survives the loader's paseq/ketiv-qere tokenization in the three loci, so this
    is defensive; a strand accent with no pooled match is recorded as a supply."""
    need = _real_accents_ordered(mam_word)
    supplies: list[SuppliedMark] = []
    for accent in need:
        if accent in pool:
            pool.remove(accent)
        else:
            supplies.append(
                SuppliedMark(
                    bcv=bcv,
                    strand=strand,
                    strand_label=strand_label,
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
def _emit_word(text: str, substitutions: dict[str, str], strays: tuple[str, ...] = ()) -> str:
    """Build one WLC-stream word on the MAM strand word's spine.

    Keep base letters and the spine marks (maqaf / paseq / sof pasuq / meteg); drop the
    tsinnorit stress-helper and the second of any doubled accent (a stress-helper); apply
    anomaly substitutions (MAM accent -> WLC's actual accent); drop points/dagesh/CGJ.

    Any ``strays`` (WLC accents this strand has no slot for) are spliced in at the strand
    word's stress: right after its meteg if it has one (the stress marker, e.g. dt
    5:8 elyon's meteg on the ש), else after the last base letter.  Their letter position is
    immaterial to the grammar (one accent per word -> one token) but matters to the verse
    line, so we place them where WLC's mark would sit."""
    out: list[str] = []
    seen: set[str] = set()
    last_letter_idx = -1
    meteg_idx = -1
    for ch in text:
        if uni_to_marks.is_accent(ch):
            if ch == _TSINNORIT or ch in seen:
                continue
            seen.add(ch)
            out.append(substitutions.get(ch, ch))
        elif uni_to_marks.is_base_letter(ch) or ch in _KEEP_NON_ACCENT:
            out.append(ch)
            if uni_to_marks.is_base_letter(ch):
                last_letter_idx = len(out) - 1
            elif ch == _METEG:
                meteg_idx = len(out) - 1
    insert_at = (meteg_idx if meteg_idx >= 0 else last_letter_idx) + 1
    if strays and insert_at >= 1:
        out[insert_at:insert_at] = list(strays)
    return "".join(out)


def _emit_stream(strand: list[_Tok], assigns: dict[int, _Assign]) -> list[_Tok]:
    """Emit the strand's stream as pointed-Hebrew vels, folding each non-word token
    (paseq / standalone sof pasuq) onto the previous word (WLC's attached convention)."""
    vels: list[_Tok] = []
    for i, tok in enumerate(strand):
        if tok.skel:
            assign = assigns.get(i, _NO_ASSIGN)
            vels.append(
                _Tok(tok.bcv, _emit_word(tok.text, assign.substitutions, assign.strays))
            )
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


def _strip_nonfinal_meteg(chanted_verse: list[_Tok]) -> list[_Tok]:
    """Drop metegs from a chanted verse, keeping only the verse-final silluq.

    The scanner swallows every meteg except the one adjacent to the sof pasuq, which it
    promotes to SILLUQ; that meteg lives in the chanted verse's last word (the sof-pasuq
    bearer).  Stripping the others is therefore parse-neutral, and it keeps WLC's emitted
    strand from carrying MAM's metegs -- marks that are not WLC's own here and bear
    on no accent grammar (e.g. dt 5:8's elyon תעשה, where MAM's swallowed meteg would
    otherwise mask WLC's actual merkha)."""
    if len(chanted_verse) <= 1:
        return chanted_verse
    return [
        vel if i == len(chanted_verse) - 1 else _Tok(vel.bcv, vel.text.replace(_METEG, ""))
        for i, vel in enumerate(chanted_verse)
    ]


def _tree_has_error(tree: TN | None) -> bool:
    if tree is None:
        return False
    if tree.left is not None:
        return _tree_has_error(tree.left) or _tree_has_error(tree.right)
    return "ERROR" in tree.leaves


_NON_LEAF_TOKENS = frozenset(("TILDE", "SOFPASUQ", "MISSING_SOFPASUQ"))


def _word_leaf_counts(
    words: list[_Tok], bb: str, chnu: int, vrnu: int
) -> tuple[int, ...]:
    """How many parse-tree leaves each word contributes, by re-scanning the word alone.

    Each scanner accent token (including a verse-final silluq) is one leaf; the sof-pasuq
    terminator is not.  We count tokens *the scanner emits* -- not raw accent codepoints,
    which include marks the scanner swallows -- and a single-word divider context only
    renames a token (munax vs legarmeh), never changes the count.  (A parse ERROR can fold
    several tokens into one leaf, but only inside the offending verse, so these per-word
    counts stay exact in the error-free flanks the renderer actually grays.)"""
    out: list[int] = []
    for tok in words:
        word_body = uni_to_marks.verse_to_marks({"vels": [tok.text]})
        word_tokens = scan_accents(word_body, bb, chnu, vrnu, HasLegarmeh())
        out.append(sum(1 for t in word_tokens if t.type not in _NON_LEAF_TOKENS))
    return tuple(out)


def _bcv_span_ref(cv: list[_Tok], label: str, ordinal: str) -> str:
    bcvs = [v.bcv for v in cv]
    first, last = bcvs[0], bcvs[-1]
    where = first if first == last else f"{first}–{last.split(':')[-1]}"
    return f"{where} [{label}]{ordinal}"


def _parse_chanted_verse(
    passage: Passage,
    cv: list[_Tok],
    strand: str,
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
        status = "error" if _tree_has_error(tree) else "clean"
        tree_obj = tree_to_obj(tree)
    return ChantedVerseResult(
        ref=_bcv_span_ref(cv, label, ordinal),
        strand=strand,
        strand_label=label,
        bcv_span=(cv[0].bcv, cv[-1].bcv),
        words=tuple(v.text for v in cv),
        word_bcvs=tuple(v.bcv for v in cv),
        body=body,
        tokens=tuple(t.type for t in tokens),
        status=status,
        tree=tree_obj,
        word_leaf_counts=_word_leaf_counts(cv, passage.bb, chnu, vrnu),
    )


# --------------------------------------------------------------------------- #
# Driver entry points
# --------------------------------------------------------------------------- #
def _process_strand(
    passage: Passage,
    strand: str,
    label: str,
    other_label: str,
    wlc: list[_Tok],
    strand_toks: list[_Tok],
    blocks: list[_Block],
    other_acc: dict[int, set[str]],
    other_meteg: dict[int, bool],
    parser,
) -> tuple[StrandResult, list[SuppliedMark], list[Anomaly]]:
    assigns: dict[int, _Assign] = {}
    supplies: list[SuppliedMark] = []
    anomalies: list[Anomaly] = []
    for block in blocks:
        if block.tag == "equal":
            for wi, ti in zip(block.wlc_idxs, block.tok_idxs):
                res = _assign_word(
                    wlc_word=wlc[wi].text,
                    mam_word=strand_toks[ti].text,
                    other_real=other_acc.get(wi, set()),
                    other_meteg=other_meteg.get(wi, False),
                    bcv=strand_toks[ti].bcv,
                    strand=strand,
                    strand_label=label,
                    other_label=other_label,
                )
                assigns[ti] = res
                supplies.extend(res.supplies)
                anomalies.extend(res.anomalies)
        elif block.tok_idxs:
            pool = [a for wi in block.wlc_idxs for a in _accents(wlc[wi].text)]
            for ti in block.tok_idxs:
                res = _assign_pooled(
                    mam_word=strand_toks[ti].text,
                    pool=pool,
                    bcv=strand_toks[ti].bcv,
                    strand=strand,
                    strand_label=label,
                )
                assigns[ti] = res
                supplies.extend(res.supplies)

    vels = _emit_stream(strand_toks, assigns)
    chanted_verses = [_strip_nonfinal_meteg(cv) for cv in _segment(vels)]
    n = len(chanted_verses)
    results: list[ChantedVerseResult] = []
    for idx, cv in enumerate(chanted_verses, start=1):
        ordinal = f" (chanted verse {idx}/{n})" if n > 1 else ""
        results.append(_parse_chanted_verse(passage, cv, strand, label, ordinal, parser))
    return (
        StrandResult(strand=strand, strand_label=label, chanted_verses=tuple(results)),
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
    alef = _strand_tokens(mam_by_bcv, passage, "vels_cant_alef")
    bet = _strand_tokens(mam_by_bcv, passage, "vels_cant_bet")

    alef_blocks = _blocks(wlc, alef)
    bet_blocks = _blocks(wlc, bet)
    alef_acc = _equal_acc_by_wlc(wlc, alef, alef_blocks)
    bet_acc = _equal_acc_by_wlc(wlc, bet, bet_blocks)
    alef_meteg = _equal_meteg_by_wlc(wlc, alef, alef_blocks)
    bet_meteg = _equal_meteg_by_wlc(wlc, bet, bet_blocks)

    alef_result, alef_sup, alef_anom = _process_strand(
        passage, "alef", passage.alef_label, passage.bet_label,
        wlc, alef, alef_blocks, bet_acc, bet_meteg, parser,
    )
    bet_result, bet_sup, bet_anom = _process_strand(
        passage, "bet", passage.bet_label, passage.alef_label,
        wlc, bet, bet_blocks, alef_acc, alef_meteg, parser,
    )
    division_changes = tuple(
        _division_changes(wlc, alef, alef_blocks, "alef", passage.alef_label)
        + _division_changes(wlc, bet, bet_blocks, "bet", passage.bet_label)
    )
    return PassageResult(
        passage=passage,
        strands=(alef_result, bet_result),
        supplied_marks=tuple(alef_sup + bet_sup),
        anomalies=tuple(alef_anom + bet_anom),
        division_changes=division_changes,
    )


def detangle_all(
    wlc_index: dict[str, dict], mam_by_bcv: dict[str, dict], parser
) -> list[PassageResult]:
    return [detangle_passage(p, wlc_index, mam_by_bcv, parser) for p in PASSAGES]


# --------------------------------------------------------------------------- #
# Folding detangled oddities into the (numbered-verse-keyed) prose ungrammatical-verse reports
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


def chanted_verse_to_prose_record(
    cv: ChantedVerseResult, bb: str, key_bcv: str | None = None
) -> dict[str, object]:
    """Shape one detangled chanted verse as a prose ``*_ag.json`` record.

    The prose ungrammatical pipeline is keyed by the BHS numbered verse (``bcv``) and looks the
    parse tree up by that key.  ``key_bcv`` sets that key; it defaults to the chanted verse's
    first numbered verse, but a multi-verse reading is keyed at the verse where its rogue
    mark lives (e.g. the elyon dt 5:7-10 ungrammatical is keyed dt 5:8, where WLC's stray sits), so
    the note and goerwitz row land on that verse.  The strand and the full chanted-verse span
    are kept in ``dual_cant_*`` fields for provenance (the goerwitz row re-derives its visible
    ref from the bcv); the ``dual_cant`` flag marks the record so a re-run replaces it."""
    bcv = key_bcv or cv.bcv_span[0]
    chnu, vrnu = bcv[len(bb):].split(":")
    return {
        "ref": f"{wlc_bb_to_bk39id(bb)} {chnu}:{vrnu}",
        "bcv": bcv,
        "dual_cant": True,
        "dual_cant_strand": cv.strand,
        "dual_cant_strand_label": cv.strand_label,
        "dual_cant_ref": cv.ref,
        "input": {
            "unicode": _join_for_display(cv.words),
            "marks": cv.body,
            "tokens": list(cv.tokens),
        },
        "status": cv.status,
        "tree": cv.tree,
    }


def folded_ungrammatical_records(
    bb: str, wlc_index: dict[str, dict], mam_by_bcv: dict[str, dict], parser
) -> list[dict[str, object]]:
    """The detangled *oddity* records for one book, to fold into its prose output.

    Only non-clean chanted verses (a genuine WLC dual-cant bug -> ungrammatical / no_parse /
    location_only) are folded; clean and supplied-mark chanted verses are not ungrammatical.
    A supplied-mark chanted verse parses clean, so it never appears here (the issue's
    reporting requirement).

    A rogue WLC mark can spoil more than one reading (dt 5:8's merkha breaks the elyon; the
    taxton is rescued by supplying its omitted qadma).  Such a mark is a single phenomenon
    and gets one numbered-verse row, keyed at the verse where the mark lives (its anomaly's
    verse, e.g. dt 5:8) rather than the reading's first verse (the elyon groups dt 5:7-10).
    A later strand's non-clean chanted verse whose anomalies were all already folded from an
    earlier strand is skipped (shown inside that one row as the second reading, its tree
    riding along on ``dual_cant_readings``)."""
    passage = passage_for_book(bb)
    if passage is None:
        return []
    result = detangle_passage(passage, wlc_index, mam_by_bcv, parser)
    anomaly_bcvs = {a.bcv for a in result.anomalies}
    records: list[dict[str, object]] = []
    seen: dict[str, str] = {}
    folded_anomaly_bcvs: set[str] = set()
    for strand in result.strands:
        for cv in strand.chanted_verses:
            if cv.status == "clean":
                continue
            cv_anomaly_bcvs = anomaly_bcvs & set(cv.word_bcvs)
            if cv_anomaly_bcvs and cv_anomaly_bcvs <= folded_anomaly_bcvs:
                continue
            # Key the row at the verse where the rogue mark lives (its anomaly's verse), not
            # the chanted verse's first verse: an elyon reading groups several verses
            # (dt 5:7-10), but its ungrammatical belongs to dt 5:8, where WLC's stray mark sits.
            key_bcv = min(cv_anomaly_bcvs) if cv_anomaly_bcvs else None
            record = chanted_verse_to_prose_record(cv, bb, key_bcv)
            bcv = str(record["bcv"])
            if bcv in seen:
                raise ValueError(
                    f"Two folded dual-cant oddities share bcv {bcv} ({seen[bcv]} and "
                    f"{cv.ref}); the numbered-verse-keyed prose ungrammatical pipeline cannot "
                    "represent both -- revisit the fold-in attribution."
                )
            seen[bcv] = cv.ref
            records.append(record)
            folded_anomaly_bcvs |= cv_anomaly_bcvs
    return records
