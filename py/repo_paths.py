"""Resolve this repo's root and its sibling-repo dependencies.

Cross-repo dependencies (MAM-simple, wlc-utils-private, MAM-basics, UXLC-utils)
are by default looked up as siblings of this repo under a common parent
directory.  That convention breaks when the repo is checked out somewhere the
siblings are not co-located -- most notably a git worktree, whose root is nested
under ``.../.claude/worktrees/`` rather than next to the sibling repos.

To make sibling lookups overridable without changing default behavior, two kinds
of environment variable are honored, resolved per dependency in this order:

  1. per-repo ``WLC_<NAME>_DIR`` (NAME = the sibling dir name uppercased with
     each run of non-alphanumeric characters replaced by ``_``); else
  2. ``WLC_SIBLINGS_ROOT`` joined with the sibling name; else
  3. ``repo_root().parent`` joined with the sibling name (the historical default).

With no environment variables set, resolution is byte-identical to the previous
``repo_root.parent / <name>`` behavior.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# This repo's stable logical name -- the top-level segment in generated-artifact
# provenance breadcrumbs, so they read "wlc-utils/..." even when the checkout dir
# is a git worktree (.../.claude/worktrees/agent-xxx) rather than literally
# "wlc-utils".  Supplied to mb_cmn.provenance by the wlc_provenance wrapper.
REPO_NAME = "wlc-utils"


def repo_root() -> Path:
    """Path to this repo's root, anchored to this module's location.

    ``py/repo_paths.py`` -> ``py`` -> repo root.  Anchoring to ``__file__``
    (rather than the cwd) makes this equal to the worktree root even when the
    process is launched from elsewhere.
    """
    return Path(__file__).resolve().parent.parent


def out_dir() -> Path:
    """This repo's generated-output tree (``<repo_root>/out``)."""
    return repo_root() / "out"


def in_dir() -> Path:
    """This repo's committed-input tree (``<repo_root>/in``)."""
    return repo_root() / "in"


def gh_pages_dir() -> Path:
    """This repo's published-HTML tree (``<repo_root>/gh-pages``)."""
    return repo_root() / "gh-pages"


def data_dir() -> Path:
    """This repo's hand-curated data tree (``<repo_root>/data``)."""
    return repo_root() / "data"


def novc_dir() -> Path:
    """This repo's gitignored scratch tree (``<repo_root>/.novc``).

    Named for the ``.gitignore`` entry rather than for what it holds, because what it holds
    is deliberately unclassified: whatever a run wants to write and nobody wants to commit.
    An accessor rather than each caller composing ``repo_root() / ".novc"`` -- four did,
    one of them off its own ``Path(__file__)`` walk -- so the string appears once.
    """
    return repo_root() / ".novc"


def scans_dir() -> Path:
    """Where page renderings from the scan archive are written (``<novc_dir>/scans``).

    NOT the scan archive itself, which is a personal collection outside every repo and is
    resolved by ``accgram.scan_page.SCANS`` off ``WLC_SCANS_DIR``.  These are the
    downscaled, cropped derivatives, which are disposable and can be large.
    """
    return novc_dir() / "scans"


def siblings_root() -> Path:
    """Base directory under which sibling repos are looked up.

    ``WLC_SIBLINGS_ROOT`` if set, else ``repo_root().parent`` (current behavior).
    """
    override = os.environ.get("WLC_SIBLINGS_ROOT")
    if override:
        return Path(override)
    return repo_root().parent


def _env_name(name: str) -> str:
    return "WLC_" + re.sub(r"[^A-Za-z0-9]+", "_", name).upper() + "_DIR"


def sibling(name: str) -> Path:
    """Resolve the path to sibling repo ``name``.

    Precedence: per-repo ``WLC_<NAME>_DIR`` -> ``WLC_SIBLINGS_ROOT/name`` ->
    ``repo_root().parent/name``.
    """
    per_repo = os.environ.get(_env_name(name))
    if per_repo:
        return Path(per_repo)
    return siblings_root() / name


def require_sibling(name: str, path: Path) -> Path:
    """Return ``path``, or raise saying both ways to point this repo at ``name``.

    A MISSING SIBLING IS A MISCONFIGURATION, NOT A REASON TO CHECK LESS.  Nothing runs the
    test suite without the siblings present -- the only CI here is the Pages deploy, which
    runs no tests -- so a cross-repo check that quietly skips on an absent sibling reports
    green having verified nothing, and does it in the same channel this suite uses for
    SEMANTIC skips ("this page diverges from its Wikisource strand; the control needs an
    agreeing page").  Fail instead, and make the failure carry its own fix: the overrides
    documented
    in this module's docstring are the answer, and a bare ``FileNotFoundError`` from deep in
    a loader does not mention them.

    ``path`` is passed in rather than recomputed because a sibling accessor usually wants a
    subtree of the clone (``MAM-parsed/plus``), and the message should name the path actually
    looked for while the override it advertises is keyed to the clone.
    """
    if path.is_dir():
        return path
    # Name the siblings root the lookup actually searches, NOT repo_root(): in
    # the worktree case this module exists for, repo_root() is the worktree
    # root, and "clone beside that" is precisely the wrong advice.
    raise FileNotFoundError(
        f"sibling repo {name} not found: no directory at {path}.\n"
        f"Clone {name} under the siblings root, {siblings_root()}, or point at it"
        f" explicitly:\n"
        f"  {_env_name(name)}=<path to the {name} clone>\n"
        f"  WLC_SIBLINGS_ROOT=<directory holding all the sibling clones>"
    )


def mam_simple_dir() -> Path:
    """MAM-simple's ``json-vtrad-bhs`` subtree: one JSON per book, verse-element streams."""
    return sibling("MAM-simple") / "json-vtrad-bhs"


def require_mam_simple_dir() -> Path:
    """``mam_simple_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("MAM-simple", mam_simple_dir())


def mam_simple_vtrad_mam_dir() -> Path:
    """MAM-simple's ``json-vtrad-mam``: the same text in MAM's native versification.

    ``mam_simple_dir`` above is the BHS versification, which is what this repo's surveys read
    because they are keyed to WLC's refs.  A cross-check against another MAM-derived text numbers
    its verses MAM's way, so it wants this flavour and no remap table.  MAM-simple ships three --
    BHS, Sefaria and MAM native -- and picking the wrong one is what makes versification look like
    a difference between two texts rather than between two numberings of one.
    """
    return sibling("MAM-simple") / "json-vtrad-mam"


def require_mam_simple_vtrad_mam_dir() -> Path:
    """``mam_simple_vtrad_mam_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("MAM-simple", mam_simple_vtrad_mam_dir())


def mam_parsed_plus_dir() -> Path:
    """MAM-parsed's ``plus`` subtree: one JSON per book24, minirow cells C/D/E."""
    return sibling("MAM-parsed") / "plus"


def require_mam_parsed_plus_dir() -> Path:
    """``mam_parsed_plus_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("MAM-parsed", mam_parsed_plus_dir())


def wlc_utils_private_dir() -> Path:
    return sibling("wlc-utils-private")


def mam_basics_dir() -> Path:
    return sibling("MAM-basics")


def require_mam_basics_dir() -> Path:
    """``mam_basics_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("MAM-basics", mam_basics_dir())


def al_hatorah_phonetic_dir() -> Path:
    """al-hatorah's ``io/a01-phonetic-std-set``: Phonetic MAM, one JSON per book.

    Each chanted word has a ``jta`` field whose ``!`` immediately precedes the stressed
    syllable, which is what makes this an independent oracle for ``accgram.final_stress``.  The
    engine behind it is al-hatorah's ``py/aht_phon``, which cannot be imported here -- issue #48
    calls consuming these outputs its second path, and this is that path.
    """
    return sibling("al-hatorah") / "io" / "a01-phonetic-std-set"


def require_al_hatorah_phonetic_dir() -> Path:
    """``al_hatorah_phonetic_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("al-hatorah", al_hatorah_phonetic_dir())


def uxlc_utils_dir() -> Path:
    return sibling("UXLC-utils")


def require_uxlc_utils_dir() -> Path:
    """``uxlc_utils_dir``, checked -- see ``require_sibling`` for why this is not a skip."""
    return require_sibling("UXLC-utils", uxlc_utils_dir())
