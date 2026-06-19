"""Derive the PLY-based oddball set for the generate-goerwitz-html subcommand.

This module classifies oddball verses from the **PLY** port outputs. An oddball
is any verse whose PLY parse tree contains at least one ``ERROR`` leaf. Since
``run-ply-goerwitz`` now processes the full prose corpus (including the 49 verses the C
binary emitted no output for), every such ERROR verse lives in
``out/accgram/ply/`` directly -- there is no separate troublemaker pass.

The resulting ``_oddballs.json`` uses the same schema ``rtms_rows`` parses: one
row per oddball with ``ref``, ``content`` (the verse's pointed-Hebrew text, drawn
from the canonical ``-kq-u`` Unicode source -- issue #9 retired the M-C body as an
input), and ``output_file`` (the ``*_ag.txt`` holding its ERROR tree).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from accgram import oddballs
from accgram import rtms_data
from accgram import rtms_focus_diff_expand
from accgram import rtms_rows
from mb_cmn import provenance

_OUTPUT_FILE_BB_RE = re.compile(r"^wlc_422_ps_([A-Za-z0-9]+)_ag\.txt$")


def _ref_to_tuple(ref: str) -> tuple[str, int, int]:
    bb, rest = ref.split(" ", 1)
    chnu, vrnu = rest.split(":", 1)
    return (bb, int(chnu), int(vrnu))


def write_ply_oddballs(
    ply_dir: Path,
    wlc422_kq_u_dir: Path,
    oddballs_out: Path,
) -> None:
    """(Re)generate the PLY-derived ``_oddballs.json`` from ``out/accgram/ply/``."""
    refs_with_files: list[tuple[str, int, int, str]] = []
    output_paths = sorted(
        p for p in ply_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    for output_path in output_paths:
        match = _OUTPUT_FILE_BB_RE.match(output_path.name)
        if match is None:
            continue
        bb = match.group(1).lower()
        for chnu, vrnu in sorted(oddballs._collect_oddball_refs(output_path)):
            refs_with_files.append((bb, chnu, vrnu, output_path.name))

    wlc_index = rtms_data.load_wlc422_index(wlc422_kq_u_dir)

    oddball_rows: list[dict[str, object]] = [
        {
            "ref": f"{bb} {chnu}:{vrnu}",
            "content": _verse_unicode_text(wlc_index, bb, chnu, vrnu),
            "output_file": output_file,
        }
        for bb, chnu, vrnu, output_file in refs_with_files
    ]
    oddball_rows.sort(key=lambda row: _ref_to_tuple(str(row["ref"])))

    books_with_oddballs = {_ref_to_tuple(str(row["ref"]))[0] for row in oddball_rows}
    oddballs_payload: dict[str, object] = {
        "artifacts_description": "oddball verses with ERROR nodes in PLY *_ag.txt outputs",
        "payload_provenance_note": (
            "These verses are parsed by the PLY port into a tree containing at least "
            "one line with the token ERROR, drawn from out/accgram/ply/. The "
            "output_file field on each row names which book file holds that verse's "
            "ERROR tree."
        ),
        "summary": {
            "oddballs": len(oddball_rows),
            "books_with_oddballs": len(books_with_oddballs),
        },
        "oddballs": oddball_rows,
    }
    oddballs_payload = provenance.with_json_provenance(oddballs_payload, __file__)

    _write_json(oddballs_out, oddballs_payload)


def _verse_unicode_text(
    wlc_index: dict[str, dict[str, object]], bb: str, chnu: int, vrnu: int
) -> str:
    """The verse's normalized pointed-Hebrew text (qere interpolated), or "" if
    the verse is absent from the ``-kq-u`` index."""
    bcv = rtms_rows.to_compact_bcv(bb, chnu, vrnu)
    verse = wlc_index.get(bcv)
    if not isinstance(verse, dict):
        return ""
    prepared = rtms_data.prepare_wlc422_verse_for_render(verse)
    return rtms_focus_diff_expand.normalized_wlc_verse_text_from_payload(prepared)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
