"""Apply a MAM-simple fix to a Michigan-Claremont (M-C) verse body, for re-testing.

The fix-tester wants to ask: *if we adopt the MAM-simple value here, does the
oddball clear?*  The scanner reads M-C codes but the fix is a Unicode word-diff
(``diff_wlc_mam``).  This module bridges the two: it locates the single changed
word in the M-C body by index-aligning the body's space/maqaf atoms to the WLC
verse's word tokens, computes which accent the change adds/removes (by name, via
``uni_heb.accent_names``), maps those names to M-C codes
(``fix_tester_codes``), splices the code change into that atom, and returns the
modified body for re-scanning.

An adjacent run of words (a multi-word ``wlc_focus``) is spliced atom by atom.
A one-accent-out / many-accent-in replacement (azla -> pashta x2) is spliced as a
delete-then-insert.  Anything it cannot do mechanically and safely -- a
non-adjacent / mismatched-count multi-word diff, a vowel- or meteg-only change, an
accent whose code is context-dependent, a word/atom misalignment, or a code the
diff claims but the body lacks -- is returned as an ``UntestableFix`` with a
machine-readable reason, never guessed.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from accgram import fix_tester_codes
from mb_cmn import uni_heb

# Atoms are the scanner's space/maqaf-delimited units (TEXT = ``[^ \r\n-]*``).
_ATOM_SPAN_RE = re.compile(r"[^ \t\r\n\-]+")
# Every M-C cantillation code is exactly two adjacent digits.
_CODE_RE = re.compile(r"\d\d")
# A Hebrew consonant (used to tell a real word token from punctuation).
_HEB_LETTER_RE = re.compile(r"[א-ת]")
# An M-C letter (consonant or vowel); ``)`` = alef, ``(`` = ayin, ``$`` = shin,
# ``&`` = sin.  An atom with none of these is pure punctuation/code, not a word.
_MC_LETTER_RE = re.compile(r"[A-Za-z)($&]")
# A ketiv atom is prefixed by a single ``*`` (the qere is ``**``).  The scanner
# swallows the ketiv whole (``\*[^* ...]+``) and rtms_data drops it from the WLC
# word list, so it must not count as a word-atom during index alignment.
_KETIV_RE = re.compile(r"^\*(?!\*)")
# A section marker -- petuhah (``P``), setumah (``S``), or nun-inversum (``N``,
# which carries note ``]8``) -- stands as its own atom in the M-C body, optionally
# trailing note markers like ``]8``.  ``S``/``P`` double as the consonants samekh
# and pe, but a real word bearing them always carries vowels, so a *lone* P/S/N is
# unambiguously a marker.  rtms_data tags it ``sam_pe_inun`` and ``verse_words``
# drops it (no Hebrew consonant), so it must not count as a word-atom during
# alignment either (mirrors wlc_read_and_parse_mdc._distinguish_sam_pe_inun).
_SECTION_MARKER_RE = re.compile(r"^[PSN](?:\].)*$")
_SOFPASUQ_CODE = "00"
# Sof pasuq punctuation (U+05C3); its M-C code is 00.  A MAM value that merely
# adds it is the "missing sof pasuq" fix -- testable by appending 00 to the body.
_SOF_PASUQ = "׃"


@dataclass(frozen=True)
class AppliedFix:
    new_body: str
    word_index: int  # index (in wlc_words) of the first *changed* word
    old_atom: str
    new_atom: str
    removed_accents: tuple[str, ...]  # accent abbreviations, WLC side
    added_accents: tuple[str, ...]  # accent abbreviations, MAM side
    removed_codes: tuple[str, ...]
    added_codes: tuple[str, ...]
    # Pre-formatted transform descriptions for any *additional* changed words in a
    # multi-word (adjacent wlc_focus) splice; empty for the common single-word case.
    extra_transforms: tuple[str, ...] = ()

    def transformation(self) -> str:
        if not self.old_atom and self.added_codes == (_SOFPASUQ_CODE,):
            return "append sof pasuq (00) to body"
        rm = " ".join(self.removed_codes) or "(none)"
        ad = " ".join(self.added_codes) or "(none)"
        base = f'atom "{self.old_atom}" -> "{self.new_atom}" ({rm} -> {ad})'
        if self.extra_transforms:
            return "; ".join((base, *self.extra_transforms))
        return base


@dataclass(frozen=True)
class UntestableFix:
    reason: str  # machine code, see module docstring
    detail: str = ""


def apply_mam_fix(
    body: str,
    wlc_words: list[str],
    diff_entry: object,
) -> AppliedFix | UntestableFix:
    """Splice the MAM value of ``diff_entry`` into ``body``; see module docstring.

    A ``wlc_focus``-expanded entry may carry several *adjacent* words on each side
    (space-joined); the splice then changes each word's atom in place.  The common
    case is a single word.
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
    if len(wlc_tokens) > 1:
        return _apply_multi_word_change(body, wlc_words, wlc_tokens, mam_tokens)
    return _apply_word_change(body, wlc_words, wlc_word, mam_word)


def _apply_word_change(
    body: str,
    wlc_words: list[str],
    wlc_word: str,
    mam_word: str,
) -> AppliedFix | UntestableFix:
    # --- which accents the fix removes vs adds (by name) ---
    removed, added = _accent_name_diff(wlc_word, mam_word)
    if not removed and not added:
        # No accent change.  The common "missing sof pasuq" fix adds only the sof
        # pasuq punctuation; test it by appending 00 to the (sof-pasuq-less) body.
        if _SOF_PASUQ in mam_word and _SOF_PASUQ not in wlc_word and "00" not in body:
            # Place 00 right after the last accent code (the verse-final silluq),
            # not at the raw body end and not merely after the last letter: a
            # trailing note-marker like ]1 would fuse (]1 + 00 -> ]100, mis-scanned
            # as YETIV 10), and a silluq code sitting *after* the last consonant
            # would be cut off (00 before it -> the silluq is lost).
            new_body = _insert_after_last_code(body, _SOFPASUQ_CODE)
            return AppliedFix(
                new_body=new_body,
                word_index=len(wlc_words) - 1,
                old_atom="",
                new_atom=_SOFPASUQ_CODE,
                removed_accents=(),
                added_accents=("(sof pasuq)",),
                removed_codes=(),
                added_codes=(_SOFPASUQ_CODE,),
            )
        # A vowel- or meteg-only change cannot reach the grammar (the scanner
        # swallows vowels and meteg), so the speculated fix is grammar-inert.
        return UntestableFix(
            _no_accent_change_reason([wlc_word], [mam_word]),
            "no accent/punctuation difference -- invisible to the grammar",
        )

    # --- locate the changed word, by index, in the M-C body's atoms ---
    occurrences = [i for i, word in enumerate(wlc_words) if word == wlc_word]
    if not occurrences:
        return UntestableFix("alignment_failure", f"WLC word {wlc_word!r} not in vels")
    if len(occurrences) > 1:
        return UntestableFix("ambiguous_word", f"WLC word {wlc_word!r} not unique")
    word_index = occurrences[0]

    atom_spans = _word_atom_spans(body)
    if len(atom_spans) != len(wlc_words):
        return UntestableFix(
            "alignment_failure",
            f"{len(atom_spans)} M-C word-atoms vs {len(wlc_words)} WLC words",
        )

    spliced = _splice_word(atom_spans[word_index], removed, added)
    if isinstance(spliced, UntestableFix):
        return spliced

    new_atom, removed_codes, added_codes = spliced
    target = atom_spans[word_index]
    new_body = body[: target.start()] + new_atom + body[target.end() :]
    return AppliedFix(
        new_body=new_body,
        word_index=word_index,
        old_atom=target.group(),
        new_atom=new_atom,
        removed_accents=tuple(removed),
        added_accents=tuple(added),
        removed_codes=tuple(removed_codes),
        added_codes=tuple(added_codes),
    )


def _apply_multi_word_change(
    body: str,
    wlc_words: list[str],
    wlc_tokens: list[str],
    mam_tokens: list[str],
) -> AppliedFix | UntestableFix:
    """Splice an adjacent run of words (a multi-word ``wlc_focus``) atom by atom."""
    span = len(wlc_tokens)
    starts = [
        i
        for i in range(len(wlc_words) - span + 1)
        if wlc_words[i : i + span] == wlc_tokens
    ]
    if not starts:
        return UntestableFix(
            "alignment_failure", f"multi-word run {wlc_tokens!r} not in vels"
        )
    if len(starts) > 1:
        return UntestableFix(
            "ambiguous_word", f"multi-word run {wlc_tokens!r} not unique"
        )
    start = starts[0]

    atom_spans = _word_atom_spans(body)
    if len(atom_spans) != len(wlc_words):
        return UntestableFix(
            "alignment_failure",
            f"{len(atom_spans)} M-C word-atoms vs {len(wlc_words)} WLC words",
        )

    # (word_index, span, new_atom, removed, added, removed_codes, added_codes)
    changes: list[tuple[int, object, str, list[str], list[str], list[str], list[str]]] = []
    for offset in range(span):
        removed, added = _accent_name_diff(wlc_tokens[offset], mam_tokens[offset])
        if not removed and not added:
            continue  # vowel/meteg-only on this word: a no-op for the grammar
        target = atom_spans[start + offset]
        spliced = _splice_word(target, removed, added)
        if isinstance(spliced, UntestableFix):
            return spliced
        new_atom, removed_codes, added_codes = spliced
        changes.append(
            (start + offset, target, new_atom, removed, added, removed_codes, added_codes)
        )

    if not changes:
        return UntestableFix(
            _no_accent_change_reason(wlc_tokens, mam_tokens),
            "no accent/punctuation difference -- invisible to the grammar",
        )

    # Apply right-to-left so earlier splices do not shift later atom offsets.
    new_body = body
    for _idx, target, new_atom, *_rest in sorted(
        changes, key=lambda c: c[1].start(), reverse=True
    ):
        new_body = new_body[: target.start()] + new_atom + new_body[target.end() :]

    first_index, first_target, first_atom, removed, added, removed_codes, added_codes = (
        changes[0]
    )
    extra_transforms = tuple(
        f'atom "{t.group()}" -> "{na}" '
        f'({" ".join(rc) or "(none)"} -> {" ".join(ac) or "(none)"})'
        for (_i, t, na, _rm, _ad, rc, ac) in changes[1:]
    )
    return AppliedFix(
        new_body=new_body,
        word_index=first_index,
        old_atom=first_target.group(),
        new_atom=first_atom,
        removed_accents=tuple(removed),
        added_accents=tuple(added),
        removed_codes=tuple(removed_codes),
        added_codes=tuple(added_codes),
        extra_transforms=extra_transforms,
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
    wlc_accs = Counter(uni_heb.accent_names(wlc_word))
    mam_accs = Counter(uni_heb.accent_names(mam_word))
    # ``(mos)`` is the meteg/silluq glyph (U+05BD); strip it from the cantillation
    # diff -- a meteg difference is invisible to the grammar.
    del wlc_accs[fix_tester_codes.MOS_ABBREV]
    mam_mos = mam_accs.pop(fix_tester_codes.MOS_ABBREV, 0)
    removed = list((wlc_accs - mam_accs).elements())
    added = list((mam_accs - wlc_accs).elements())
    # Verse-final silluq: when MAM trades a real WLC accent for a ``(mos)`` on a
    # sof-pasuq-bearing word, that ``(mos)`` is the verse-final silluq -- a real,
    # grammar-visible accent (code 35), not meteg.  Promote it so the splice swaps
    # accent->silluq instead of silently dropping the silluq (which would leave the
    # word accent-less and still failing silluq_phrase -- a false DENIED, e.g.
    # ju 13:18).  A ``(mos)`` merely *added* (nothing removed) stays an inert meteg,
    # as in the meteg_only cases.
    if mam_mos and removed and not added and _SOF_PASUQ in mam_word:
        added.append(fix_tester_codes.SILLUQ_ABBREV)
    return removed, added


def _word_atom_spans(body: str) -> list[re.Match[str]]:
    """The M-C body's word-bearing atoms (a Hebrew letter, not a ketiv ``*atom``
    and not a lone P/S/N section marker), index-aligned 1:1 with the WLC verse's
    word tokens."""
    return [
        m
        for m in _ATOM_SPAN_RE.finditer(body)
        if _MC_LETTER_RE.search(m.group())
        and not _KETIV_RE.match(m.group())
        and not _SECTION_MARKER_RE.match(m.group())
    ]


def _splice_word(
    target: re.Match[str], removed: list[str], added: list[str]
) -> tuple[str, list[str], list[str]] | UntestableFix:
    """Map accent names -> M-C codes and splice them into ``target``'s atom text."""
    atom_text = target.group()
    # The removed side may resolve delete-only accents (e.g. a stranded zarshit /
    # 82) that have no standalone token type and so cannot be added.
    removed_codes, bad = _codes_for(removed, for_removal=True)
    if bad is not None:
        return UntestableFix("ambiguous_accent", f"unmappable accent {bad}")
    added_codes, bad = _codes_for(added)
    if bad is not None:
        return UntestableFix("ambiguous_accent", f"unmappable accent {bad}")

    new_atom = _splice(atom_text, removed_codes, added_codes)
    if new_atom is None:
        return UntestableFix(
            "code_not_found",
            f"codes {removed_codes} not all in atom {atom_text!r}",
        )
    return new_atom, removed_codes, added_codes


def _no_accent_change_reason(wlc_tokens: list[str], mam_tokens: list[str]) -> str:
    """Distinguish a meteg/silluq-only change from a pure niqqud change; both are
    invisible to the grammar, but the label tells which mark moved."""
    wlc_mos = sum(
        Counter(uni_heb.accent_names(w))[fix_tester_codes.MOS_ABBREV] for w in wlc_tokens
    )
    mam_mos = sum(
        Counter(uni_heb.accent_names(w))[fix_tester_codes.MOS_ABBREV] for w in mam_tokens
    )
    return "meteg_only" if wlc_mos != mam_mos else "vowel_only"


def _codes_for(
    abbrevs: list[str], for_removal: bool = False
) -> tuple[list[str], str | None]:
    lookup = (
        fix_tester_codes.removal_code if for_removal else fix_tester_codes.accent_code
    )
    codes: list[str] = []
    for abbrev in abbrevs:
        code = lookup(abbrev)
        if code is None:
            return [], abbrev
        codes.append(code)
    return codes, None


def _splice(atom: str, removed_codes: list[str], added_codes: list[str]) -> str | None:
    """Return the atom with the accent codes changed, or None if a removed code is
    absent from the atom.

    Handles four shapes: a 1->1 swap (in place, preserving the code's offset -- so
    e.g. an in-place zarshit 82->02 or verse-final silluq 91->35 stays put), and
    the general delete-then-insert that covers delete-only, insert-only, and the
    1->many replacement (azla -> pashta x2, 1k 19:11 / je 49:19).  In the general
    path the added codes land after the last M-C letter, exactly as the insert-only
    case always has: the offset among letters is irrelevant to tokenization, and a
    postpositive accent (pashta) belongs on the final consonant anyway.
    """
    if len(removed_codes) == 1 and len(added_codes) == 1:
        return _replace_first_code(atom, removed_codes[0], added_codes[0])
    out = atom
    for code in removed_codes:
        out = _replace_first_code(out, code, "")
        if out is None:
            return None
    if added_codes:
        out = _insert_codes(out, added_codes)
    return out


def _replace_first_code(atom: str, old_code: str, new_code: str) -> str | None:
    for m in _CODE_RE.finditer(atom):
        if m.group() == old_code:
            return atom[: m.start()] + new_code + atom[m.end() :]
    return None


def _insert_codes(atom: str, codes: list[str]) -> str:
    return _insert_after_last_letter(atom, "".join(codes))


def _insert_after_last_letter(text: str, ins: str) -> str:
    # Insert right after the last M-C letter (the stress-bearing consonant), not
    # at the very end: trailing note-markers like ``]1`` carry stray digits that
    # would fuse with an end-appended code into a spurious 2-digit code.  The
    # exact letter offset among earlier letters is irrelevant to tokenization.
    last_letter = None
    for m in _MC_LETTER_RE.finditer(text):
        last_letter = m
    insert_at = last_letter.end() if last_letter is not None else len(text)
    return text[:insert_at] + ins + text[insert_at:]


def _insert_after_last_code(text: str, ins: str) -> str:
    # Insert right after the last 2-digit accent code (the verse-final silluq for
    # a sof-pasuq append), so the silluq still scans and the inserted 00 does not
    # fuse with note-marker digits.  Falls back to after the last letter.
    last_code = None
    for m in _CODE_RE.finditer(text):
        last_code = m
    if last_code is not None:
        return text[: last_code.end()] + ins + text[last_code.end() :]
    return _insert_after_last_letter(text, ins)
