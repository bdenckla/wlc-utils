"""Tests for the sibling-repo path resolver (issue #32).

These exercise the resolution precedence and env-var name mapping without
requiring any real sibling directory to exist on disk.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import repo_paths


def test_repo_root_is_module_anchored() -> None:
    # py/repo_paths.py -> py -> repo root; the repo root contains py/.
    assert (repo_paths.repo_root() / "py" / "repo_paths.py").is_file()


def test_default_sibling_is_repo_parent(monkeypatch) -> None:
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    monkeypatch.delenv("WLC_MAM_SIMPLE_DIR", raising=False)
    assert (
        repo_paths.sibling("MAM-simple") == repo_paths.repo_root().parent / "MAM-simple"
    )


def test_default_siblings_root_is_repo_parent(monkeypatch) -> None:
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    assert repo_paths.siblings_root() == repo_paths.repo_root().parent


def test_siblings_root_env_honored(monkeypatch) -> None:
    monkeypatch.setenv("WLC_SIBLINGS_ROOT", "/some/base")
    monkeypatch.delenv("WLC_MAM_SIMPLE_DIR", raising=False)
    assert repo_paths.siblings_root() == Path("/some/base")
    assert repo_paths.sibling("MAM-simple") == Path("/some/base") / "MAM-simple"


def test_per_repo_override_wins_over_siblings_root(monkeypatch) -> None:
    monkeypatch.setenv("WLC_SIBLINGS_ROOT", "/some/base")
    monkeypatch.setenv("WLC_MAM_SIMPLE_DIR", "/elsewhere/mam")
    assert repo_paths.sibling("MAM-simple") == Path("/elsewhere/mam")


def test_per_repo_override_wins_over_default(monkeypatch) -> None:
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    monkeypatch.setenv("WLC_MAM_SIMPLE_DIR", "/elsewhere/mam")
    assert repo_paths.sibling("MAM-simple") == Path("/elsewhere/mam")


def test_env_name_mapping_non_alnum_to_underscore(monkeypatch) -> None:
    # wlc-utils-private -> WLC_WLC_UTILS_PRIVATE_DIR
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    monkeypatch.setenv("WLC_WLC_UTILS_PRIVATE_DIR", "/priv")
    assert repo_paths.sibling("wlc-utils-private") == Path("/priv")
    assert repo_paths.wlc_utils_private_dir() == Path("/priv")


def test_accessor_suffixes(monkeypatch) -> None:
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    for name in (
        "WLC_MAM_SIMPLE_DIR",
        "WLC_MAM_PARSED_DIR",
        "WLC_WLC_UTILS_PRIVATE_DIR",
        "WLC_MAM_BASICS_DIR",
        "WLC_UXLC_UTILS_DIR",
    ):
        monkeypatch.delenv(name, raising=False)
    parent = repo_paths.repo_root().parent
    assert repo_paths.mam_simple_dir() == parent / "MAM-simple" / "json-vtrad-bhs"
    assert repo_paths.mam_parsed_plus_dir() == parent / "MAM-parsed" / "plus"
    assert repo_paths.wlc_utils_private_dir() == parent / "wlc-utils-private"
    assert repo_paths.mam_basics_dir() == parent / "MAM-basics"
    assert repo_paths.uxlc_utils_dir() == parent / "UXLC-utils"


def test_default_matches_legacy_repo_root_parent_formula(monkeypatch) -> None:
    # Byte-identical to the old `repo_root.parent / "MAM-simple" / "json-vtrad-bhs"`.
    monkeypatch.delenv("WLC_SIBLINGS_ROOT", raising=False)
    monkeypatch.delenv("WLC_MAM_SIMPLE_DIR", raising=False)
    legacy = repo_paths.repo_root().parent / "MAM-simple" / "json-vtrad-bhs"
    assert repo_paths.mam_simple_dir() == legacy


def test_require_sibling_returns_a_present_directory() -> None:
    # Any directory that certainly exists; the check is is_dir, not the name.
    root = repo_paths.repo_root()
    assert repo_paths.require_sibling("MAM-parsed", root / "py") == root / "py"


def test_require_sibling_failure_advertises_both_overrides(tmp_path) -> None:
    """The message IS the feature: a missing sibling is a misconfiguration, and the fix has to
    travel with the failure.  A cross-repo check that skipped here would report green having
    verified nothing, so this path must raise -- and raise something actionable."""
    missing = tmp_path / "MAM-parsed" / "plus"
    with pytest.raises(FileNotFoundError) as excinfo:
        repo_paths.require_sibling("MAM-parsed", missing)
    message = str(excinfo.value)
    assert str(missing) in message  # the path actually looked for
    assert "WLC_MAM_PARSED_DIR" in message  # the per-repo override, correctly derived
    assert "WLC_SIBLINGS_ROOT" in message  # the all-siblings override
    assert str(repo_paths.repo_root()) in message  # where a sibling clone belongs


def test_require_mam_parsed_plus_dir_checks_the_resolved_path(
    monkeypatch, tmp_path
) -> None:
    """The accessor checks what it resolves, overrides included -- so pointing the env var at
    a wrong path fails naming that path, not the default one."""
    monkeypatch.setenv("WLC_MAM_PARSED_DIR", str(tmp_path / "nowhere"))
    with pytest.raises(FileNotFoundError, match="nowhere"):
        repo_paths.require_mam_parsed_plus_dir()


def test_data_path_accessors() -> None:
    # The in-repo data-tree accessors (issue #33).
    root = repo_paths.repo_root()
    assert repo_paths.out_dir() == root / "out"
    assert repo_paths.in_dir() == root / "in"
    assert repo_paths.gh_pages_dir() == root / "gh-pages"
