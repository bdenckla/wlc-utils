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


def repo_root() -> Path:
    """Path to this repo's root, anchored to this module's location.

    ``py/repo_paths.py`` -> ``py`` -> repo root.  Anchoring to ``__file__``
    (rather than the cwd) makes this equal to the worktree root even when the
    process is launched from elsewhere.
    """
    return Path(__file__).resolve().parent.parent


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


def mam_simple_dir() -> Path:
    return sibling("MAM-simple") / "json-vtrad-bhs"


def wlc_utils_private_dir() -> Path:
    return sibling("wlc-utils-private")


def mam_basics_dir() -> Path:
    return sibling("MAM-basics")


def uxlc_utils_dir() -> Path:
    return sibling("UXLC-utils")
