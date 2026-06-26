"""Guard: no NFC-only precomposed character may appear in our Python source.

The repo standard for transliteration is the *decomposed* form -- e.g. ``ḥ`` is
written as ``h`` + U+0323 (combining dot below), never the precomposed U+1E25.
This keeps a single normalization variant tree-wide so lookups, diffs, and
display never silently disagree on which code point a glyph is.

A character is precomposed iff NFD changes it (``ch != NFD(ch)``).  This walks
every ``*.py`` under ``py/`` (excluding the vendored ``mb_*`` packages, whose
normalization is the upstream repo's concern) and flags any such character,
except a tiny, deliberately documented allowlist:

* **U+2260 NOT EQUAL TO (≠)** -- a display glyph (``"WLC ≠ MAM"``); its NFD is
  ``=`` + U+0338, so the predicate flags it, but there is no decomposed letter
  to prefer -- it is intentionally precomposed.
* **U+1E25 in ``wlc_uword.py``** -- a private single-codepoint *sentinel* used as
  a ``str.maketrans`` key, which must be length 1 (a decomposed h+U+0323 would
  raise ``ValueError`` at import).  See the note at ``_XOLAM_REPL3`` there.

Issue #26 will fold this into a shared ``test_transliterations.py`` later.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_no_precomposed_chars.py -v
"""

from __future__ import annotations

import unicodedata

import repo_paths

# Packages vendored from sibling repos -- not ours to normalize.
_VENDORED = {"mb_cmn", "mb_misc", "mb_diff_mpu"}

# (relative-posix-path, code point) pairs exempt from the guard, each justified
# in this module's docstring.  ``None`` path means "allowed in any file".
_ALLOW = {
    (None, 0x2260),                                       # ≠  display glyph
    ("py_wlc_json_and_unicode/wlc_uword.py", 0x1E25),     # ḥ  maketrans sentinel
}


def _is_allowed(rel_posix: str, code_point: int) -> bool:
    return (None, code_point) in _ALLOW or (rel_posix, code_point) in _ALLOW


def test_no_precomposed_chars_tree_wide() -> None:
    py_root = repo_paths.repo_root() / "py"
    offenders: list[str] = []
    for path in py_root.rglob("*.py"):
        parts = set(path.relative_to(py_root).parts)
        if parts & _VENDORED or "__pycache__" in parts:
            continue
        rel = path.relative_to(py_root).as_posix()
        text = path.read_text(encoding="utf-8")
        for code_point in sorted({ord(ch) for ch in text}):
            ch = chr(code_point)
            if ch == unicodedata.normalize("NFD", ch):
                continue
            if _is_allowed(rel, code_point):
                continue
            name = unicodedata.name(ch, "?")
            offenders.append(f"{rel}: U+{code_point:04X} {name}")
    assert not offenders, (
        "Use decomposed forms (e.g. ḥ as h+U+0323), not precomposed:\n  "
        + "\n  ".join(offenders)
    )
