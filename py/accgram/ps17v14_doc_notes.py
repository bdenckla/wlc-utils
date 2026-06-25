"""Generate gh-pages/accgram/ps17v14-mam-doc-notes.html -- an English rendering of
MAM's four documentation notes on Psalms 17:14 (one per word).

Formerly hand-authored; now generated so it shares the look and feel of the other
accgram pages.  The page body is replayed byte-exactly from the committed htel
JSON ``ps17v14_mam_doc_notes_body.json`` (parsed from the original) through the
shared shell in ``ps17v14_replay``.  It is the Psalms 17:14 sibling of
telg-doc-notes.html, and is linked from ps17v14-double-tsinnor.html.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from accgram import ps17v14_replay

_OUT_NAME = "ps17v14-mam-doc-notes.html"
_JSON_NAME = "ps17v14_mam_doc_notes_body.json"


def default_html_out_path(repo_root: Path) -> Path:
    return repo_root / "gh-pages" / "accgram" / _OUT_NAME


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    ps17v14_replay.add_html_out_arg(parser, default_html_out_path(repo_root))


def run(args: argparse.Namespace) -> None:
    ps17v14_replay.write_replayed(args.html_out, _JSON_NAME, __file__)


def main() -> None:
    ps17v14_replay.main_for(
        json_name=_JSON_NAME,
        out_name=_OUT_NAME,
        generator_file=__file__,
        description=__doc__,
    )


if __name__ == "__main__":
    main()
