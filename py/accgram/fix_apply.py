"""Apply a MAM-simple fix to a WLC verse at the Unicode-word level, for re-testing.

The fix-tester wants to ask: *if we adopt the MAM-simple value here, does the
oddball clear?*  The fix is a Unicode word-diff (``diff_wlc_mam``) and the scanner
reads a Michigan-Claremont (M-C) accent body, so this module bridges the two the
direct way (issue #9, Phase 1): it locates the single changed word in the verse's
``vels`` by index-aligning to the WLC word tokens, substitutes the MAM Unicode word
in place (keeping the surrounding structure -- ketiv-qere wrappers, ``notes``,
section markers), and re-transcodes the modified verse to an M-C body
(``uni_to_mc_body``) for re-scanning.  No accent-name->code bridge is involved; the
transcoder owns the helper/main split and every code emission.

An adjacent run of words (a multi-word ``wlc_focus``) is substituted word by word.
A change the grammar cannot see -- a vowel- or meteg-only edit -- is returned as an
``UntestableFix`` (it would re-transcode to the same body), as is a non-adjacent /
mismatched-count multi-word diff or a word/atom misalignment.  Nothing is guessed.
"""

from __future__ import annotations

import copy
import re
from collections import Counter
from dataclasses import dataclass

from accgram import uni_to_mc_body
from mb_cmn import uni_heb

# A Hebrew consonant (used to tell a real word token from punctuation/markers).
_HEB_LETTER_RE = re.compile(r"[א-ת]")
# Sof pasuq punctuation (U+05C3).  A MAM value that merely adds it is the "missing
# sof pasuq" fix -- grammar-visible (the transcoder emits 00, the scanner terminates).
_SOF_PASUQ = "׃"

# Accent abbreviations as ``uni_heb.accent_names`` returns them.  ``(mos)`` is the
# meteg/silluq glyph (U+05BD); a *medial* meteg difference is invisible to the
# grammar, so it is stripped before diffing.  ``(sil)`` is the synthetic verse-final
# silluq promoted from a ``(mos)`` that lands on a sof-pasuq-bearing word.
_MOS_ABBREV = "(mos)"
_SILLUQ_ABBREV = "(sil)"


@dataclass(frozen=True)
class AppliedFix:
    new_body: str  # the re-transcoded M-C body to re-scan
    word_index: int  # index (in wlc_words) of the first *changed* word
    old_word: str  # the WLC Unicode word (first, for a multi-word focus)
    new_word: str  # the MAM Unicode word it was replaced with
    removed_accents: tuple[str, ...]  # accent abbreviations, WLC side
    added_accents: tuple[str, ...]  # accent abbreviations, MAM side
    # Pre-formatted transform descriptions for any *additional* changed words in a
    # multi-word (adjacent wlc_focus) splice; empty for the common single-word case.
    extra_transforms: tuple[str, ...] = ()

    def transformation(self) -> str:
        rm = " ".join(self.removed_accents) or "(none)"
        ad = " ".join(self.added_accents) or "(none)"
        base = f'word "{self.old_word}" -> "{self.new_word}" ({rm} -> {ad})'
        if self.extra_transforms:
            return "; ".join((base, *self.extra_transforms))
        return base


@dataclass(frozen=True)
class UntestableFix:
    reason: str  # machine code, see module docstring
    detail: str = ""


def apply_mam_fix(
    verse: object,
    wlc_words: list[str],
    diff_entry: object,
) -> AppliedFix | UntestableFix:
    """Substitute the MAM value of ``diff_entry`` into ``verse`` and re-transcode.

    ``verse`` is the raw ``-kq-u`` verse (``{vels: [...]}``); ``wlc_words`` is its WLC
    word list (``verse_words`` of the display verse), used to locate the changed
    word(s) by index.  A ``wlc_focus``-expanded entry may carry several *adjacent*
    words on each side (space-joined); the substitution then replaces each word's vel
    in place.  The common case is a single word.
    """
    wlc_word = _diff_side_word(diff_entry, "wlc422")
    mam_word = _diff_side_word(diff_entry, "mam_simple")
    if wlc_word is _MULTI or mam_word is _MULTI:
        return UntestableFix("multi_word", "diff spans more than one word")
    if not isinstance(wlc_word, str) or not isinstance(mam_word, str):
        return UntestableFix("bad_diff_shape", repr(diff_entry))

    wlc_tokens = wlc_word.split()
    mam_tokens = mam_word.split()
    if len(wlc_tokens) != len(mam_tokens):
        return UntestableFix(
            "multi_word",
            f"diff word counts differ ({len(wlc_tokens)} vs {len(mam_tokens)})",
        )
    if not wlc_tokens:
        return UntestableFix("bad_diff_shape", "empty diff word")

    # --- grammar visibility gate (per word) ---
    removed_first: list[str] = []
    added_first: list[str] = []
    extra_transforms: list[str] = []
    any_visible = False
    for offset, (wlc_tok, mam_tok) in enumerate(zip(wlc_tokens, mam_tokens)):
        removed, added = _accent_name_diff(wlc_tok, mam_tok)
        sof_added = _SOF_PASUQ in mam_tok and _SOF_PASUQ not in wlc_tok
        if sof_added:
            added = [*added, "(sof pasuq)"]
        if removed or added:
            any_visible = True
        if offset == 0:
            removed_first, added_first = removed, added
        elif removed or added:
            rm = " ".join(removed) or "(none)"
            ad = " ".join(added) or "(none)"
            extra_transforms.append(f'word "{wlc_tok}" -> "{mam_tok}" ({rm} -> {ad})')
    if not any_visible:
        # A vowel- or (medial) meteg-only change cannot reach the grammar (the
        # scanner swallows vowels and meteg), so the speculated fix is grammar-inert.
        return UntestableFix(
            _no_accent_change_reason(wlc_tokens, mam_tokens),
            "no accent/punctuation difference -- invisible to the grammar",
        )

    # --- locate the changed run, by index, in the WLC word list ---
    span = len(wlc_tokens)
    starts = [
        i
        for i in range(len(wlc_words) - span + 1)
        if wlc_words[i : i + span] == wlc_tokens
    ]
    if not starts:
        return UntestableFix("alignment_failure", f"WLC run {wlc_tokens!r} not in vels")
    if len(starts) > 1:
        return UntestableFix("ambiguous_word", f"WLC run {wlc_tokens!r} not unique")
    start = starts[0]

    # --- substitute the MAM word(s) into a copy of the verse and re-transcode ---
    new_verse = copy.deepcopy(verse)
    setters = _word_unit_setters(new_verse)
    if len(setters) != len(wlc_words):
        return UntestableFix(
            "alignment_failure",
            f"{len(setters)} verse word-units vs {len(wlc_words)} WLC words",
        )
    for offset in range(span):
        setters[start + offset](mam_tokens[offset])
    new_body = uni_to_mc_body.verse_to_mc_body(new_verse)

    return AppliedFix(
        new_body=new_body,
        word_index=start,
        old_word=wlc_tokens[0],
        new_word=mam_tokens[0],
        removed_accents=tuple(removed_first),
        added_accents=tuple(added_first),
        extra_transforms=tuple(extra_transforms),
    )


def verse_words(wlc_verse: object) -> list[str]:
    """Return the WLC verse's word tokens (those carrying a Hebrew consonant)."""
    if not isinstance(wlc_verse, dict):
        return []
    vels = wlc_verse.get("vels")
    if not isinstance(vels, list):
        return []
    words: list[str] = []
    for token in vels:
        text = _token_text(token)
        if text is not None and _HEB_LETTER_RE.search(text):
            words.append(text)
    return words


# --- helpers -----------------------------------------------------------------

_MULTI = object()  # sentinel: a diff side that is a multi-word list


def _token_text(token: object) -> str | None:
    if isinstance(token, str):
        return token
    if isinstance(token, dict):
        for key in ("word", "text"):
            value = token.get(key)
            if isinstance(value, str):
                return value
    return None


def _diff_side_word(diff_entry: object, key: str) -> object:
    if not isinstance(diff_entry, dict):
        return None
    value = diff_entry.get(key)
    if isinstance(value, list):
        if len(value) != 1:
            return _MULTI
        value = value[0]
    return _token_text(value)


def _accent_name_diff(wlc_word: str, mam_word: str) -> tuple[list[str], list[str]]:
    """The cantillation accents the fix removes vs adds, by abbreviation.

    Used only as the grammar-visibility gate and for the human-readable transform
    description; the actual fix is the whole-word substitution.  A *medial* meteg
    (``(mos)``) is stripped from both sides (invisible to the grammar), but a
    ``(mos)`` that *replaces* a real accent on a sof-pasuq-bearing word -- or is added
    to a sof-pasuq word that carried no silluq -- is the verse-final silluq, a real
    grammar-visible accent, so it is promoted to ``(sil)``.
    """
    wlc_accs = Counter(uni_heb.accent_names(wlc_word))
    mam_accs = Counter(uni_heb.accent_names(mam_word))
    wlc_mos = wlc_accs.pop(_MOS_ABBREV, 0)
    mam_mos = mam_accs.pop(_MOS_ABBREV, 0)
    removed = list((wlc_accs - mam_accs).elements())
    added = list((mam_accs - wlc_accs).elements())
    if (
        mam_mos
        and not added
        and _SOF_PASUQ in mam_word
        and (removed or wlc_mos == 0)
    ):
        added.append(_SILLUQ_ABBREV)
    return removed, added


def _no_accent_change_reason(wlc_tokens: list[str], mam_tokens: list[str]) -> str:
    """Distinguish a meteg/silluq-only change from a pure niqqud change; both are
    invisible to the grammar, but the label tells which mark moved."""
    wlc_mos = sum(
        Counter(uni_heb.accent_names(w))[_MOS_ABBREV] for w in wlc_tokens
    )
    mam_mos = sum(
        Counter(uni_heb.accent_names(w))[_MOS_ABBREV] for w in mam_tokens
    )
    return "meteg_only" if wlc_mos != mam_mos else "vowel_only"


def _word_unit_setters(verse: object):
    """Setters for each word-bearing unit in ``verse['vels']``, in WLC word order.

    Each setter replaces one word's Unicode text in place (preserving any ``notes``
    and the ketiv-qere wrapper), so the list is 1:1 with ``verse_words`` of the
    display verse: maqaf-joined sub-words are separate vels (hence separate units),
    ketiv-qere descends into the qere side, and lone section markers contribute none.
    """
    setters: list = []
    vels = verse.get("vels") if isinstance(verse, dict) else None
    if not isinstance(vels, list):
        return setters
    _collect_unit_setters(vels, setters)
    return setters


def _collect_unit_setters(container: list, setters: list) -> None:
    """Append a setter for every word-bearing unit reachable from ``container`` (a
    vels list, or a qere list inside a ketiv-qere wrapper), in order."""
    for index, vel in enumerate(container):
        if isinstance(vel, str):
            if _HEB_LETTER_RE.search(vel):
                setters.append(
                    lambda new_word, c=container, i=index: c.__setitem__(i, new_word)
                )
            continue
        if not isinstance(vel, dict):
            continue
        kq = vel.get("kq")
        if isinstance(kq, (list, tuple)) and len(kq) == 2 and isinstance(kq[1], list):
            _collect_unit_setters(kq[1], setters)
            continue
        word = vel.get("word")
        if isinstance(word, str) and _HEB_LETTER_RE.search(word):
            setters.append(
                lambda new_word, d=vel: d.__setitem__("word", new_word)
            )
