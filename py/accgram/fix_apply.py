"""Apply a MAM-simple fix to a Michigan-Claremont (M-C) verse body, for re-testing.

The fix-tester wants to ask: *if we adopt the MAM-simple value here, does the
oddball clear?*  The scanner reads M-C codes but the fix is a Unicode word-diff
(``diff_wlc_mam``).  This module bridges the two: it locates the single changed
word in the M-C body by index-aligning the body's space/maqaf atoms to the WLC
verse's word tokens, computes which accent the change adds/removes (by name, via
``uni_heb.accent_names``), maps those names to M-C codes
(``fix_tester_codes``), splices the code change into that atom, and returns the
modified body for re-scanning.

Anything it cannot do mechanically and safely -- a multi-word or multi-accent
diff, a vowel-only change, an accent whose code is context-dependent, a
word/atom misalignment, or a code the diff claims but the body lacks -- is
returned as an ``UntestableFix`` with a machine-readable reason, never guessed.
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
_SOFPASUQ_CODE = "00"
# Sof pasuq punctuation (U+05C3); its M-C code is 00.  A MAM value that merely
# adds it is the "missing sof pasuq" fix -- testable by appending 00 to the body.
_SOF_PASUQ = "׃"


@dataclass(frozen=True)
class AppliedFix:
    new_body: str
    word_index: int
    old_atom: str
    new_atom: str
    removed_accents: tuple[str, ...]  # accent abbreviations, WLC side
    added_accents: tuple[str, ...]  # accent abbreviations, MAM side
    removed_codes: tuple[str, ...]
    added_codes: tuple[str, ...]

    def transformation(self) -> str:
        if not self.old_atom and self.added_codes == (_SOFPASUQ_CODE,):
            return "append sof pasuq (00) to body"
        rm = " ".join(self.removed_codes) or "(none)"
        ad = " ".join(self.added_codes) or "(none)"
        return f'atom "{self.old_atom}" -> "{self.new_atom}" ({rm} -> {ad})'


@dataclass(frozen=True)
class UntestableFix:
    reason: str  # machine code, see module docstring
    detail: str = ""


def apply_mam_fix(
    body: str,
    wlc_words: list[str],
    diff_entry: object,
) -> AppliedFix | UntestableFix:
    """Splice the MAM value of ``diff_entry`` into ``body``; see module docstring."""
    wlc_word = _diff_side_word(diff_entry, "wlc422")
    mam_word = _diff_side_word(diff_entry, "mam_simple")
    if wlc_word is _MULTI or mam_word is _MULTI:
        return UntestableFix("multi_word", "diff spans more than one word")
    if not isinstance(wlc_word, str) or not isinstance(mam_word, str):
        return UntestableFix("bad_diff_shape", repr(diff_entry))

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
        return UntestableFix("vowel_only", "no accent-name difference (vowel/meteg)")

    # --- locate the changed word, by index, in the M-C body's atoms ---
    occurrences = [i for i, word in enumerate(wlc_words) if word == wlc_word]
    if not occurrences:
        return UntestableFix("alignment_failure", f"WLC word {wlc_word!r} not in vels")
    if len(occurrences) > 1:
        return UntestableFix("ambiguous_word", f"WLC word {wlc_word!r} not unique")
    word_index = occurrences[0]

    atom_spans = [
        m
        for m in _ATOM_SPAN_RE.finditer(body)
        if _MC_LETTER_RE.search(m.group()) and not _KETIV_RE.match(m.group())
    ]
    if len(atom_spans) != len(wlc_words):
        return UntestableFix(
            "alignment_failure",
            f"{len(atom_spans)} M-C word-atoms vs {len(wlc_words)} WLC words",
        )
    target = atom_spans[word_index]
    atom_text = target.group()

    removed_codes, bad = _codes_for(removed)
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
    if new_atom == _MULTI_SPLICE:
        return UntestableFix(
            "multi_accent",
            f"unsupported multi-accent splice {removed_codes} -> {added_codes}",
        )

    new_body = body[: target.start()] + new_atom + body[target.end() :]
    return AppliedFix(
        new_body=new_body,
        word_index=word_index,
        old_atom=atom_text,
        new_atom=new_atom,
        removed_accents=tuple(removed),
        added_accents=tuple(added),
        removed_codes=tuple(removed_codes),
        added_codes=tuple(added_codes),
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
_MULTI_SPLICE = "\x00multi"  # sentinel: an unsupported multi-accent splice


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
    del wlc_accs[fix_tester_codes.MOS_ABBREV]
    del mam_accs[fix_tester_codes.MOS_ABBREV]
    removed = list((wlc_accs - mam_accs).elements())
    added = list((mam_accs - wlc_accs).elements())
    return removed, added


def _codes_for(abbrevs: list[str]) -> tuple[list[str], str | None]:
    codes: list[str] = []
    for abbrev in abbrevs:
        code = fix_tester_codes.accent_code(abbrev)
        if code is None:
            return [], abbrev
        codes.append(code)
    return codes, None


def _splice(atom: str, removed_codes: list[str], added_codes: list[str]) -> str | None:
    """Return the atom with the accent codes changed, or None / _MULTI_SPLICE.

    Handles the three safe shapes: 1->1 swap, delete-only, insert-only.  Anything
    else returns the _MULTI_SPLICE sentinel (caller marks it UNTESTABLE).
    """
    if len(removed_codes) == 1 and len(added_codes) == 1:
        return _replace_first_code(atom, removed_codes[0], added_codes[0])
    if removed_codes and not added_codes:
        out = atom
        for code in removed_codes:
            out = _replace_first_code(out, code, "")
            if out is None:
                return None
        return out
    if added_codes and not removed_codes:
        return _insert_codes(atom, added_codes)
    return _MULTI_SPLICE


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
