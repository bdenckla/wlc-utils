"""Guard: no known-undesirable transliteration variant in our Python source.

Two checks run over every ``py/**/*.py`` (excluding the vendored ``mb_*``
packages and ``__pycache__``); any single line may opt out with an inline
``# translit-ok`` pragma (self-documenting, travels with the line, cf.
``# noqa``):

1. ``test_no_undesirable_transliterations`` -- a denylist of spelling variants
   that the #13 standardization retired: ``zinor``->``tsinnor`` (#30),
   ``merka``->``merkha``, ``atnach``->``atnaX`` (X = decomposed h+U+0323),
   ``sinnor``->``tsinnor``, the het-as-plain-``h`` forms, and a few Goerwitz/
   legacy capitalizations.  The het-as-h patterns carry a ``(?![U+0323])``
   lookahead so the *decomposed* good forms (e.g. ``munaX`` written ``muna`` +
   ``h`` + U+0323) never trip them -- the scan reads raw bytes, never NFC.

2. ``test_no_precomposed_chars_tree_wide`` -- folded in from #27: the repo
   standard is the *decomposed* form, so any NFC-only precomposed code point
   (``ch != NFD(ch)``) is flagged, except a tiny documented allowlist.

Legitimate exemptions (external vocabularies / verbatim citations), each tagged
``# translit-ok`` in the source and enumerated in issue #26:

* UXLC external vocab -- the readers that match UXLC's own spellings
  ``etnahta`` / ``etnachta`` / ``zinor`` (``main_uxlc_grammar_test.py``,
  ``main_find_uxlc_accent_changes.py``, ``py_uxlc/my_uxlc_unicode_names.py``).
* Unicode-name citations of ``zinor`` (``accgram/mam_poetic_accents.py``,
  ``accgram/poetic_accent_names.py``).
* Finding-aid citations -- Goerwitz "MEREKA"/"MAHPAK", Yeivin "mehuppak",
  Breuer "mahpakh" (``accgram/poetic_accent_names.py``).

This module is itself excluded from the *denylist* scan: its patterns
necessarily spell out every retired variant.  (It is still covered by the
precomposed-char scan, so its prose avoids precomposed characters.)

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_transliterations.py -v
"""

from __future__ import annotations

import re
import unicodedata

import repo_paths

# Packages vendored from sibling repos -- not ours to normalize.
_VENDORED = {"mb_cmn", "mb_misc", "mb_diff_mpu"}

# Lines bearing this pragma are exempt from the denylist scan.
_PRAGMA = re.compile(r"#\s*translit-ok")

# U+0323 COMBINING DOT BELOW, the decomposed-het marker, kept out of the het-as-h
# matches via negative lookahead.  ``re`` interprets ``̣`` inside the pattern.
_NOT_DOT = r"(?!̣)"

# (compiled pattern, preferred spelling, short label).  Patterns are anchored so the
# good decomposed forms and the genuine Unicode names never match; see the per-row
# notes in issue #26's research comment.
_DENYLIST: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\b[Zz]inor\b"), "tsinnor", "zinor"),
    (re.compile(r"(?<![tT])\b[sS]innor"), "tsinnor(it)", "sinnor"),
    (re.compile(r"\b[mM]unah" + _NOT_DOT), "munaX (h+U+0323)", "munah"),
    (re.compile(r"\b[tT]arha" + _NOT_DOT), "tarXa (h+U+0323)", "tarha"),
    (re.compile(r"\b[aA]tnah" + _NOT_DOT), "atnaX (h+U+0323)", "atnah"),
    (re.compile(r"\b[dD]ehi" + _NOT_DOT), "deXi (h+U+0323)", "dehi"),
    (re.compile(r"\b[yY]erah" + _NOT_DOT), "yeraX (h+U+0323)", "yerah"),
    (re.compile(r"\b[tT]ipeha" + _NOT_DOT), "tipeXa (h+U+0323)", "tipeha"),
    (re.compile(r"\b[mM]unaH\b"), "munaX (h+U+0323)", "munaH"),
    (re.compile(r"\b[tT]ipeHa\b"), "tipeXa (h+U+0323)", "tipeHa"),
    (re.compile(r"\bmehuppak\b"), "mahapakh", "mehuppak"),
    (re.compile(r"\bmahpakh?\b"), "mahapakh", "mahpak(h)"),
    (re.compile(r"\bmereka\b"), "merkha", "mereka"),
    (re.compile(r"\bmerka\b"), "merkha", "merka"),
    (re.compile(r"\b(?:MUNACH|MEREKA|MAHPAK|ATNACH|TIFCHA)\b"), "adopted caps", "legacy CAPS"),
    (re.compile(r"\b(?:ethnakhta|etnahta|etnachta)\b"), "atnaX / ATNAX", "etna*ta"),
    (re.compile(r"\batnach\b"), "atnaX (h+U+0323)", "atnach"),
]


def _scan_targets():
    py_root = repo_paths.repo_root() / "py"
    for path in py_root.rglob("*.py"):
        parts = set(path.relative_to(py_root).parts)
        if parts & _VENDORED or "__pycache__" in parts:
            continue
        yield py_root, path


def test_no_undesirable_transliterations() -> None:
    import pathlib

    this_file = pathlib.Path(__file__).resolve()
    offenders: list[str] = []
    for py_root, path in _scan_targets():
        if path.resolve() == this_file:  # the denylist necessarily names every variant
            continue
        rel = path.relative_to(py_root).as_posix()
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if _PRAGMA.search(line):
                continue
            for pattern, preferred, label in _DENYLIST:
                if pattern.search(line):
                    offenders.append(f"{rel}:{lineno}  {label} -> {preferred}")
    assert not offenders, (
        "Undesirable transliteration variants (use the preferred form, or add a"
        " `# translit-ok` pragma if the line legitimately cites an external"
        " vocabulary / Unicode name):\n  " + "\n  ".join(offenders)
    )


# --- precomposed-character guard (folded in from #27) -------------------------

# (relative-posix-path, code point) pairs exempt from the precomposed guard, each
# justified below.  ``None`` path means "allowed in any file".
#   * U+2260 NOT EQUAL TO -- a display glyph ("WLC != MAM"); NFD makes it "=" +
#     U+0338, so the predicate flags it, but there is no decomposed letter to
#     prefer -- it is intentionally precomposed.
#   * U+1E25 in wlc_uword.py -- a private single-codepoint sentinel used as a
#     ``str.maketrans`` key, which must be length 1 (a decomposed h+U+0323 would
#     raise ValueError at import).  See the note at ``_XOLAM_REPL3`` there.
_ALLOW_PRECOMPOSED = {
    (None, 0x2260),
    ("py_wlc_json_and_unicode/wlc_uword.py", 0x1E25),
}


def _is_allowed_precomposed(rel_posix: str, code_point: int) -> bool:
    return (None, code_point) in _ALLOW_PRECOMPOSED or (
        rel_posix,
        code_point,
    ) in _ALLOW_PRECOMPOSED


def test_no_precomposed_chars_tree_wide() -> None:
    offenders: list[str] = []
    for py_root, path in _scan_targets():
        rel = path.relative_to(py_root).as_posix()
        text = path.read_text(encoding="utf-8")
        for code_point in sorted({ord(ch) for ch in text}):
            ch = chr(code_point)
            if ch == unicodedata.normalize("NFD", ch):
                continue
            if _is_allowed_precomposed(rel, code_point):
                continue
            name = unicodedata.name(ch, "?")
            offenders.append(f"{rel}: U+{code_point:04X} {name}")
    assert not offenders, (
        "Use decomposed forms (e.g. het as h+U+0323), not precomposed:\n  "
        + "\n  ".join(offenders)
    )
