"""Run this repo's test suite.

Examples:
    .venv/Scripts/python.exe py/main_test.py
    .venv/Scripts/python.exe py/main_test.py -k printed_decalogue -x
    .venv/Scripts/python.exe py/main_test.py py/tests/test_transliterations.py -q

With no arguments this runs everything under ``py/tests``.  Whatever arguments are
given go straight through to pytest, so its own options (``-k``, ``-x``, ``-q``,
``--lf``, ...) work unchanged; naming a file or directory replaces the default target
rather than adding to it.  Use the venv's own interpreter -- the system Python has
neither pytest nor PLY.

WHY THIS FILE EXISTS, AND WHY A BARE ``pytest`` FAILS TO COLLECT

``.venv/Scripts/pytest.exe py/tests`` does not collect: every test imports
``accgram.*``, ``repo_paths`` or ``cmn.utf8_io``, and collection dies on the first of
them with ``ModuleNotFoundError``.  That is the designed state, not a defect to repair.
Import path here is decided by how a program is entered: CPython puts a script's own
directory at ``sys.path[0]``, so running ``py/main_<x>.py`` -- this file included --
puts ``py/`` on the path, and the in-process ``pytest.main()`` call below inherits it.
Nothing is added by hand anywhere.

So do not "fix" that collection failure by reintroducing a path shim.  A root
``conftest.py`` (which this file replaced), a ``pythonpath`` setting in ``pytest.ini``,
a ``.pth`` file, an exported ``PYTHONPATH``, a ``sitecustomize.py`` -- all the same
mistake in different spellings, and the count of them in this repo is zero, not one.
Run the tests through this entry point instead.

WHY THIS ONE WRAPS pytest WHERE MAM-basics' AND holman-ketiv-qere's RUN unittest

Those two repos' ``py/main_test.py`` is a ``TEST_MODULE_SPECS`` tuple plus a ``unittest``
loader, and the standard came from them, so the difference is deliberate rather than
drift.  Matching their shape here would have meant rewriting 299 module-level ``def
test_`` functions across 33 files (this suite has exactly one ``unittest.TestCase``),
plus the ``@parametrize`` sites, the fixtures, the ``pytest.raises`` calls and the two
SEMANTIC ``pytest.skip`` sites -- on a suite whose worth is that it passes.  What the
standard actually forbids is path configuration, which this file has none of either way.

And a hand-maintained registry has a failure mode this has not: an unlisted test file
does not skip, it reports nothing at all.  Both repos using that pattern were found with
unregistered files on 2026-07-30.  pytest discovers files itself, so there is no registry
to fall out of sync here.  Revisit only if cross-repo uniformity comes to outweigh that.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from cmn.utf8_io import force_utf8_io

import repo_paths


def _default_target() -> str:
    """The whole suite, absolute, so the command does not depend on the cwd."""
    return str(repo_paths.repo_root() / "py" / "tests")


def main(argv: list[str] | None = None) -> int:
    """Run pytest over ``argv`` (default ``sys.argv[1:]``) and return its exit code."""
    args = list(sys.argv[1:] if argv is None else argv)
    # Supply the default target only when nothing given already names one.  An option's
    # value -- the expression after -k, say -- is not an existing path, so `-k <expr>`
    # still selects from the whole suite rather than from nothing.
    if not any(Path(arg).exists() for arg in args):
        args.append(_default_target())
    return int(pytest.main(args))


if __name__ == "__main__":
    force_utf8_io()
    sys.exit(main())
