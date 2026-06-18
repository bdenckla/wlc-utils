"""Auto-derive the tentative WLC-vs-MAM-simple summary for one poetic oddball.

Split out of ``poetic_oddballs`` (which owns the oddball collection + HTML shell);
this module is just the per-verse summary line shown under each oddball.

The summary is computed by aligning the two verses *word-for-word* -- the
consonantal skeleton as the key, via the same ``difflib`` engine ``mb_cmn.my_diffs``
wraps for the prose page -- and reporting each word whose divider differs.  This
replaced an earlier diff of the conjunctive-stripped *disjunctive skeletons*, which
dropped every conjunctive and so conflated a divider that merely shifted to the
neighbouring word into a phantom like-for-like substitution (Ps 68:20 / Pr 30:15:
WLC's legarmeh and MAM's oleh-we-yored sit on different words).  The disjunctive
skeleton remains the persisted datum and the table on the page; only the human-
readable summary uses the word alignment.

The WLC side pairs the wlc422 Unicode consonants (the shared alignment key, grouped
into accent-words) with the M-C scanner's resolved disjunctives; the MAM side comes
from ``mam_poetic_accents.load_poetic_word_disj``.  When the two WLC views cannot be
reconciled 1:1 the summary falls back to the disjunctive-skeleton diff, flagged as
the weaker comparison.
"""

from __future__ import annotations

import difflib
from typing import TYPE_CHECKING

from accgram.mam_poetic_accents import base_consonants
from accgram.poetic_accent_names import POETIC_DISJUNCTIVES as _POETIC_DISJUNCTIVES
from accgram.ply_scanner_poetic import scan_accents
from mb_cmn import hebrew_punctuation as hpunc

if TYPE_CHECKING:
    from accgram.poetic_oddballs import PoeticOddball


def derive_tentative_summary(ob: PoeticOddball) -> str:
    if ob.mam_disjunctives is None:
        return (
            "Not in MAM-simple, so no disjunctive oracle is available "
            "for comparison."
        )
    if ob.wlc_disjunctives == ob.mam_disjunctives:
        return (
            "WLC and MAM-simple read the same disjunctive skeleton, yet the verse "
            "does not parse — the anomaly is structural, not a WLC/MAM divergence."
        )
    clauses = _word_aligned_clauses(ob)
    if clauses is None:
        # Word-level alignment could not be reconciled (e.g. the WLC accent-word and
        # wlc422 consonant-word counts disagree); fall back to the conjunctive-stripped
        # skeleton diff, flagged so the reader knows it is the weaker comparison.
        skeleton = _describe_disjunctive_diff(ob.wlc_disjunctives, ob.mam_disjunctives)
        return (
            "Relative to the MAM-simple oracle (disjunctive skeleton only — words could "
            "not be aligned), " + "; ".join(skeleton) + "."
        )
    if not clauses:
        return (
            "An aligned word-by-word comparison finds the dividers fall on the same "
            "words; the skeleton-level difference is an artifact of segmentation, not a "
            "real divergence in which word each divider sits on."
        )
    return "Word-aligned against MAM-simple, " + "; ".join(clauses) + "."


def _word_aligned_clauses(ob: PoeticOddball) -> list[str] | None:
    """Per-word divider differences between WLC and MAM, or None if unalignable.

    Aligns the two verses *by word* (consonantal skeleton as the key, the same
    ``difflib`` engine ``mb_cmn.my_diffs`` wraps for the prose page) and reports each
    word whose divider differs.  This replaces the old disjunctive-skeleton diff, which
    dropped every conjunctive and so conflated a divider that merely *shifted to the
    neighbouring word* into a phantom like-for-like substitution (see Ps 68:20 / Pr
    30:15: WLC's legarmeh and MAM's oleh-we-yored sit on different words)."""
    if ob.mam_words is None:
        return None
    wlc_words = _wlc_accent_words(ob)
    if wlc_words is None:
        return None
    mam_words = [(cons, (d,) if d else ()) for cons, d in ob.mam_words]

    matcher = difflib.SequenceMatcher(
        a=[cons for cons, _ in wlc_words],
        b=[cons for cons, _ in mam_words],
        autojunk=False,
    )
    clauses: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                cons, wlc_disj = wlc_words[i1 + k]
                _mam_cons, mam_disj = mam_words[j1 + k]
                if wlc_disj != mam_disj:
                    clauses.append(_phrase_word_diff(cons, wlc_disj, mam_disj))
        else:
            clauses.append(
                _phrase_segment_diff(wlc_words[i1:i2], mam_words[j1:j2])
            )
    return clauses


def _wlc_accent_words(ob: PoeticOddball) -> list[tuple[str, tuple[str, ...]]] | None:
    """Per-word ``(base_consonants, disjunctives)`` for the WLC verse, accent-word by
    accent-word: the wlc422 Unicode consonants (the shared alignment key) zipped with
    the M-C scanner's resolved disjunctives.  None if the two cannot be reconciled
    1:1 (different accent-word counts)."""
    cons_words = _wlc_consonant_words(ob.wlc_verse)
    if cons_words is None:
        return None
    disj_words = _wlc_disjunctives_per_word(ob.body)
    if len(cons_words) != len(disj_words):
        return None
    return list(zip(cons_words, disj_words))


def _wlc_consonant_words(wlc_verse: object) -> list[str] | None:
    """Group the wlc422 ``vels`` into accent-words and return each one's consonants.

    A maqaf-terminated token joins the next sub-word into one accent-word (matching the
    M-C scanner's whitespace-delimited words); punctuation-only tokens (paseq) drop
    out.  None if the verse carries no ``vels``."""
    if not isinstance(wlc_verse, dict):
        return None
    vels = wlc_verse.get("vels")
    if not isinstance(vels, list):
        return None
    words: list[str] = []
    current = ""
    for token in vels:
        text = _token_text(token)  # a vel may be a {"word", "notes"} dict, not a str
        if not text:
            continue
        cons = base_consonants(text)
        if not cons:  # punctuation-only token (paseq, etc.)
            continue
        current += cons
        if hpunc.MAQ in text:  # maqaf joins this to the next sub-word
            continue
        words.append(current)
        current = ""
    if current:
        words.append(current)
    return words


def _wlc_disjunctives_per_word(body: str) -> list[tuple[str, ...]]:
    """The M-C scanner's resolved disjunctives, partitioned per accent-word.

    The scanner runs verse-level passes (unmarked-ole recovery, revia
    reclassification) that need cross-word context, so we keep the whole-verse
    resolved stream and slice it by each word's own token count (the passes relabel
    tokens but never change their count)."""
    resolved = [t for t, _leaf in scan_accents(body)]
    words: list[tuple[str, ...]] = []
    pos = 0
    for mc_word in body.split():
        count = len(scan_accents(mc_word))
        segment = resolved[pos : pos + count]
        pos += count
        words.append(tuple(t for t in segment if t in _POETIC_DISJUNCTIVES))
    return words


def _phrase_word_diff(
    cons: str, wlc_disj: tuple[str, ...], mam_disj: tuple[str, ...]
) -> str:
    return (
        f"on {cons}, WLC reads {_disj_phrase(wlc_disj)} "
        f"where MAM reads {_disj_phrase(mam_disj)}"
    )


def _phrase_segment_diff(
    wlc_seg: list[tuple[str, tuple[str, ...]]],
    mam_seg: list[tuple[str, tuple[str, ...]]],
) -> str:
    """Phrase an insert/delete/replace block: the two witnesses segment the stretch
    differently (e.g. Pr 30:15 WLC ``הב`` vs MAM ``ה ב``), so the dividers there are
    not word-comparable."""
    wlc_part = _phrase_word_list(wlc_seg)
    mam_part = _phrase_word_list(mam_seg)
    if not wlc_seg:
        return f"MAM has {mam_part} with no aligned WLC word"
    if not mam_seg:
        return f"WLC has {wlc_part} with no aligned MAM word"
    return f"WLC segments this stretch as {wlc_part} where MAM has {mam_part}"


def _phrase_word_list(seg: list[tuple[str, tuple[str, ...]]]) -> str:
    return ", ".join(
        cons + (f" [{_humanize_disjunctives(disj)}]" if disj else "")
        for cons, disj in seg
    )


def _disj_phrase(disj: tuple[str, ...]) -> str:
    return _humanize_disjunctives(disj) if disj else "no divider (a conjunctive)"


def _describe_disjunctive_diff(
    wlc: tuple[str, ...], mam: tuple[str, ...]
) -> list[str]:
    """Phrase each edit between the WLC and MAM disjunctive skeletons from WLC's
    side (MAM is the oracle), e.g. "WLC omits silluq that MAM reads".  Fallback only
    (see _word_aligned_clauses); the disjunctive-only skeleton drops conjunctives and
    so cannot tell which word each divider sits on."""
    matcher = difflib.SequenceMatcher(a=wlc, b=mam, autojunk=False)
    clauses: list[str] = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        wlc_part = _humanize_disjunctives(wlc[i1:i2])
        mam_part = _humanize_disjunctives(mam[j1:j2])
        if tag == "delete":
            clauses.append(f"WLC has an extra {wlc_part} not in MAM")
        elif tag == "insert":
            clauses.append(f"WLC omits {mam_part} that MAM reads")
        else:  # replace
            clauses.append(f"WLC reads {wlc_part} where MAM reads {mam_part}")
    return clauses


def _humanize_disjunctives(tokens: tuple[str, ...]) -> str:
    return ", ".join(token.lower().replace("_", " ") for token in tokens)


def _token_text(token: object) -> str:
    """The base text of a wlc422 ``vels`` token, which may be a str or a
    ``{"word", "notes"}`` dict (as several accgram modules each define privately)."""
    if isinstance(token, str):
        return token
    if isinstance(token, dict):
        for key in ("word", "text"):
            value = token.get(key)
            if isinstance(value, str):
                return value
    return ""
