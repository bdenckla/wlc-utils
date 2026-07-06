"""Enforcement test (cross-repo standardization; MAM-basics #187 / wlc-utils
#49): hand-authored source must standardize the Latin transliteration of
Hebrew het ("h with dot below") on NFC, i.e. the precomposed U+1E25 / U+1E24
forms, never the decomposed "h"/"H" + COMBINING DOT BELOW (U+0323) sequence.
Comments must not use either Unicode form at all -- plain ASCII "x"/"X" is used
instead, since comments don't flow to output.

Scope note: this test deliberately does NOT assert whole-file NFC
(unicodedata.normalize("NFC", text) == text). A blanket NFC pass also reorders
unrelated Hebrew combining marks (shin dot, sin dot, dagesh, rafeh) according to
Unicode canonical combining class, which conflicts with this repo's own
deliberate non-Unicode-standard Hebrew mark order. So this test checks only the
specific h-with-dot-below sequence, which has no such ambiguity: composing
"h"/"H" + U+0323 to U+1E25/U+1E24 is a simple, unambiguous Latin-script
composition.

Adapted from MAM-basics/py/tests/test_h_dot_below_nfc.py:
  - repo root comes from this repo's repo_paths.repo_root() (no mb_cmn/paths);
  - the exclusion set is this repo's generated dirs (out/, gh-pages/) plus the
    external imported-text snapshots under in/ (WLC/UXLC source, release notes,
    manuals) and binaries;
  - comment detection uses Python's tokenize module (real COMMENT tokens) rather
    than a naive line.find("#"). This repo uses "#" as a delimiter inside string
    literals (the "@...#" WLC markup in py_wlc_a_notes/*), so a naive scan would
    false-positive on het that legitimately appears in an output-facing string
    after such a "#". tokenize is stdlib, so this still runs under any interpreter.

Scope excludes:
  - out/, gh-pages/ (generated output, not hand-authored)
  - external/imported source snapshots under in/ (Tanach/UXLC/WLC text, WLC
    release notes and manuals), left as-is for fidelity to source
  - binary files (by extension)
"""
import io
import tokenize
import unicodedata
import unittest
from pathlib import Path

import repo_paths

REPO_ROOT = repo_paths.repo_root()

_COMBINING_DOT_BELOW = chr(0x0323)
_H_WITH_DOT_BELOW = chr(0x1E25)
_H_CAP_WITH_DOT_BELOW = chr(0x1E24)

_BINARY_EXTENSIONS = {
    ".png",
    ".woff2",
    ".svg",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".pdf",
    ".ttf",
    ".otf",
    ".eot",
    ".zip",
    ".gz",
    ".pyc",
    ".exe",
    ".dll",
    ".man",
    ".wts",
    ".md5sum",
}

# Generated output and external imported-text snapshots: excluded from scope.
_EXCLUDE_DIR_PREFIXES = (
    "out/",
    "gh-pages/",
    "in/",
)


def _is_binary(path: Path) -> bool:
    return path.suffix.lower() in _BINARY_EXTENSIONS


def _is_excluded(posix_rel: str) -> bool:
    return any(posix_rel.startswith(prefix) for prefix in _EXCLUDE_DIR_PREFIXES)


def _tracked_files_in_scope():
    import subprocess

    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        encoding="utf-8",
        check=True,
    )
    in_scope = []
    for line in result.stdout.splitlines():
        rel = line.strip()
        if not rel:
            continue
        posix_rel = rel.replace("\\", "/")
        if _is_excluded(posix_rel):
            continue
        full = REPO_ROOT / rel
        if not full.is_file():
            continue
        if _is_binary(full):
            continue
        in_scope.append(posix_rel)
    return in_scope


def _string_has_h_dot_below(s: str) -> bool:
    """True if `s` contains h-with-dot-below specifically (precomposed
    U+1E25/U+1E24, or decomposed "h"/"H" + U+0323) -- NOT just any U+0323,
    since U+0323 also legitimately appears on other base letters."""
    if _H_WITH_DOT_BELOW in s or _H_CAP_WITH_DOT_BELOW in s:
        return True
    for i, ch in enumerate(s):
        if (
            ch in ("h", "H")
            and i + 1 < len(s)
            and s[i + 1] == _COMBINING_DOT_BELOW
        ):
            return True
    return False


class TestHDotBelowNfc(unittest.TestCase):
    """Hand-authored source must use precomposed h-with-dot-below, never the
    decomposed sequence, and must never use either Unicode form in a real
    comment (plain ASCII "x"/"X" instead)."""

    @classmethod
    def setUpClass(cls):
        cls.in_scope_files = _tracked_files_in_scope()
        # Sanity check: the scoping logic should select a non-trivial number of
        # files (catches a badly broken exclusion filter). This repo has ~239
        # in-scope tracked text files, so 100 is a comfortable floor.
        assert len(cls.in_scope_files) > 100, (
            f"Only {len(cls.in_scope_files)} files in scope -- exclusion "
            "filters may be too broad."
        )

    def test_no_decomposed_h_dot_below_in_hand_authored_files(self):
        offenders = []
        for posix_rel in self.in_scope_files:
            full = REPO_ROOT / posix_rel
            text = full.read_text(encoding="utf-8")
            for i, ch in enumerate(text):
                if (
                    ch in ("h", "H")
                    and i + 1 < len(text)
                    and text[i + 1] == _COMBINING_DOT_BELOW
                ):
                    line_no = text.count("\n", 0, i) + 1
                    offenders.append(f"{posix_rel}:{line_no}")
                    break
        self.assertEqual(
            offenders,
            [],
            "Found decomposed h-with-dot-below (h/H + COMBINING DOT BELOW) "
            "in hand-authored files; run the NFC migration or fix by hand: "
            f"{offenders}",
        )

    def test_comments_use_ascii_not_h_dot_below(self):
        """Real Python comments (tokenize COMMENT tokens) must not carry either
        Unicode het form. Uses tokenize, not line.find('#'), because this repo
        embeds '#' inside string literals (the '@...#' WLC markup), where het is
        a legitimate output-facing value, not a comment."""
        offenders = []
        for posix_rel in self.in_scope_files:
            if not posix_rel.endswith(".py"):
                continue
            full = REPO_ROOT / posix_rel
            text = full.read_text(encoding="utf-8")
            try:
                tokens = tokenize.generate_tokens(io.StringIO(text).readline)
                for tok in tokens:
                    if tok.type == tokenize.COMMENT and _string_has_h_dot_below(
                        tok.string
                    ):
                        offenders.append(f"{posix_rel}:{tok.start[0]}")
            except (tokenize.TokenError, IndentationError, SyntaxError):
                # Malformed/partial source: fall back to a naive '#' scan so we
                # never silently skip a file. Rare; keeps coverage conservative.
                for line_no, line in enumerate(text.split("\n"), start=1):
                    hash_idx = line.find("#")
                    if hash_idx != -1 and _string_has_h_dot_below(line[hash_idx:]):
                        offenders.append(f"{posix_rel}:{line_no}")
        self.assertEqual(
            offenders,
            [],
            "Found h-with-dot-below (either Unicode form) in a comment; "
            f"use plain ASCII x/X instead: {offenders}",
        )

    def test_h_dot_below_composition_is_canonically_lossless(self):
        """Spot-check unicodedata agrees h/H + U+0323 composes to
        U+1E25/U+1E24, guarding the core assumption behind this test."""
        self.assertEqual(
            unicodedata.normalize("NFC", "h" + _COMBINING_DOT_BELOW),
            _H_WITH_DOT_BELOW,
        )
        self.assertEqual(
            unicodedata.normalize("NFC", "H" + _COMBINING_DOT_BELOW),
            _H_CAP_WITH_DOT_BELOW,
        )

    def test_detector_flags_decomposed_and_precomposed_h_dot_below(self):
        self.assertTrue(
            _string_has_h_dot_below("guttural / h" + _COMBINING_DOT_BELOW + " slot")
        )
        self.assertTrue(
            _string_has_h_dot_below("guttural / " + _H_WITH_DOT_BELOW + " slot")
        )
        self.assertTrue(
            _string_has_h_dot_below("Capital H" + _COMBINING_DOT_BELOW + "olam")
        )
        self.assertTrue(
            _string_has_h_dot_below("Capital " + _H_CAP_WITH_DOT_BELOW + "olam")
        )

    def test_detector_ignores_dot_below_on_other_base_letters(self):
        # U+0323 legitimately appears on letters other than h/H (e.g. "S" in
        # "Sere", "t" in "qetannah"); that is a different combination and must
        # NOT be flagged.
        self.assertFalse(
            _string_has_h_dot_below("Closed, S" + _COMBINING_DOT_BELOW + "ere-vowelled")
        )
        self.assertFalse(
            _string_has_h_dot_below("shalshelet qet" + _COMBINING_DOT_BELOW + "annah")
        )


if __name__ == "__main__":
    unittest.main()
