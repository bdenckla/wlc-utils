"""Guard: ``issue_edit.replace_once`` refuses the two anchor failures that lose edits.

The module exists so an issue edit is always derived from the body just fetched, rather than
from a scratch snapshot of unknown age.  ``replace_once`` is the part that has to be right: a
bare ``str.replace`` matching nothing returns the string unchanged, so a stale anchor -- exactly
what a concurrent edit produces -- would push a no-op and report success.  These tests pin that
both zero matches and several matches raise, and that the one good case rewrites in place.

No network: ``replace_once`` is pure, which is why the safety check lives in it and not in the
``gh`` wrappers around it.

BLESSED EXAMPLE-BASED BAND (issue #88).  Every test here pins a hand-picked string, which
``doc/agent-planning-principles.md`` otherwise forbids.  Kept, because ``replace_once`` has no
oracle to differ against and no decidable tree-wide property to sweep for: what it must refuse
is three concrete situations, and naming them concretely is the only way to check that it still
refuses them.  ``outgoing_path``'s literal ``issue-69-outgoing.md`` rides along on the same
ticket -- the spelling is what a reader greps the scratch directory for, so it is the contract
and not an internal name.
"""

from __future__ import annotations

import pytest

import issue_edit


def test_a_single_match_is_rewritten() -> None:
    body = "## Why\n\n- [ ] transcribe Koren\n\n## Notes\n"
    got = issue_edit.replace_once(
        body, "- [ ] transcribe Koren", "- [x] transcribe Koren"
    )
    assert got == "## Why\n\n- [x] transcribe Koren\n\n## Notes\n"


def test_a_stale_anchor_raises_rather_than_silently_doing_nothing() -> None:
    """The concurrent-edit case: the text moved, so the edit must not be reported as applied."""
    with pytest.raises(issue_edit.IssueEditError, match="no match"):
        issue_edit.replace_once(
            "the body as it now reads", "the body as it read an hour ago", "x"
        )


def test_an_ambiguous_anchor_raises_rather_than_picking_one() -> None:
    """Which of several identical anchors gets rewritten would be accidental, so refuse."""
    with pytest.raises(issue_edit.IssueEditError, match="2 matches"):
        issue_edit.replace_once("- [ ] done\n- [ ] done\n", "- [ ] done", "- [x] done")


def test_the_outgoing_path_is_fixed_per_issue() -> None:
    """One overwritten path per issue: an accumulating byproduct is the failure being cured."""
    assert issue_edit.outgoing_path(69) == issue_edit.outgoing_path(69)
    assert issue_edit.outgoing_path(69) != issue_edit.outgoing_path(70)
    assert issue_edit.outgoing_path(69).name == "issue-69-outgoing.md"


def test_hebrew_survives_the_round_trip_to_the_outgoing_file(
    tmp_path, monkeypatch
) -> None:
    """Hebrew must reach the file as UTF-8; a lone surrogate here once pushed an empty body."""
    monkeypatch.setattr(issue_edit, "_OUT_DIR", tmp_path)
    body = "the לא of לא תרצח, taken as *merkha* — p. 114\n"
    path = issue_edit.write_and_edit(70, body, dry_run=True)
    assert path.read_text(encoding="utf-8") == body
