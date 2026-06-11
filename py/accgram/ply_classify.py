"""Derive PLY-based oddball/troublemaker sets for research-tms-and-oddballs.

Unlike the goerwitz analog (``oddballs.write_oddballs_json``), which classifies
verses from the **C** ``accents`` outputs, this module classifies from the **PLY**
port outputs.  The PLY port produces an ``ERROR``-node tree for 47 of the 49
hard-coded "troublemakers" (which the C binary emits no output for), so those 47
behave exactly like the original 51 oddballs and are reclassified as oddballs here.
(Of the 47, 21 are missing-sof-pasuq verses the scanner/grammar flag with a distinct
sof_pasuq_phrase ERROR.)

Resulting sets:
  - **Oddballs (98):** the 51 ``ERROR`` verses in ``out/accgram/ply/`` (tagged
    ``output_dir="ply"``) plus the 47 ``ERROR`` verses in ``out/accgram/ply-tms/``
    (tagged ``output_dir="ply-tms"``).
  - **Troublemakers (2):** ``tms.HARDCODED_REFS`` minus the 47 ply-tms oddballs --
    i.e. the verses that produce no output even under the PLY port.

Both JSONs use the same schema as the goerwitz files so ``rtms_rows`` parses them
unchanged.  Oddball rows carry an extra ``output_dir`` field naming which PLY
output directory holds their ``ERROR`` tree (the two dirs share book filenames).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from accgram import oddballs
from accgram import tms
from mb_cmn import provenance

_OUTPUT_FILE_BB_RE = re.compile(r"^wlc_422_ps_([A-Za-z0-9]+)_ag\.txt$")


def _oddball_rows_for_dir(
    out_dir: Path,
    in_dir: Path,
    output_dir_tag: str,
) -> list[dict[str, object]]:
    """Collect oddball rows for one PLY output dir, content from ``in_dir``."""
    rows: list[dict[str, object]] = []
    output_paths = sorted(
        p for p in out_dir.iterdir() if p.is_file() and p.suffix.lower() == ".txt"
    )
    for output_path in output_paths:
        match = _OUTPUT_FILE_BB_RE.match(output_path.name)
        if match is None:
            continue
        bb = match.group(1).lower()

        input_path = in_dir / f"wlc_422_ps_{bb}.txt"
        input_verses = oddballs._collect_input_verses(input_path)
        oddball_refs = oddballs._collect_oddball_refs(output_path)

        for chnu, vrnu in sorted(oddball_refs):
            rows.append(
                {
                    "ref": f"{bb} {chnu}:{vrnu}",
                    "content": input_verses.get((chnu, vrnu), ""),
                    "output_file": output_path.name,
                    "output_dir": output_dir_tag,
                }
            )
    return rows


def _troublemaker_rows(
    unfiltered_in_dir: Path,
    ply_tms_oddball_refs: set[tuple[str, int, int]],
) -> list[dict[str, object]]:
    """HARDCODED_REFS minus the ply-tms oddballs; content from unfiltered input."""
    remaining = sorted(tms.HARDCODED_REFS - ply_tms_oddball_refs)
    input_verses_by_book: dict[str, dict[tuple[int, int], str]] = {}
    rows: list[dict[str, object]] = []
    for bb, chnu, vrnu in remaining:
        if bb not in input_verses_by_book:
            input_path = unfiltered_in_dir / f"wlc_422_ps_{bb}.txt"
            input_verses_by_book[bb] = oddballs._collect_input_verses(input_path)
        rows.append(
            {
                "ref": f"{bb} {chnu}:{vrnu}",
                "content": input_verses_by_book[bb].get((chnu, vrnu), ""),
            }
        )
    return rows


def _ref_to_tuple(ref: str) -> tuple[str, int, int]:
    bb, rest = ref.split(" ", 1)
    chnu, vrnu = rest.split(":", 1)
    return (bb, int(chnu), int(vrnu))


def write_ply_oddballs_and_troublemakers(
    ply_dir: Path,
    ply_tms_dir: Path,
    psf_in_dir: Path,
    unfiltered_in_dir: Path,
    oddballs_out: Path,
    troubles_out: Path,
) -> None:
    """(Re)generate the PLY-derived ``_oddballs.json`` and ``_troublemakers.json``."""
    ply_rows = _oddball_rows_for_dir(ply_dir, psf_in_dir, "ply")
    ply_tms_rows = _oddball_rows_for_dir(ply_tms_dir, unfiltered_in_dir, "ply-tms")
    oddball_rows = ply_rows + ply_tms_rows
    oddball_rows.sort(key=lambda row: _ref_to_tuple(str(row["ref"])))

    ply_tms_oddball_refs = {_ref_to_tuple(str(row["ref"])) for row in ply_tms_rows}
    troublemaker_rows = _troublemaker_rows(unfiltered_in_dir, ply_tms_oddball_refs)

    books_with_oddballs = {_ref_to_tuple(str(row["ref"]))[0] for row in oddball_rows}
    oddballs_payload: dict[str, object] = {
        "artifacts_description": "oddball verses with ERROR nodes in PLY *_ag.txt outputs",
        "payload_provenance_note": (
            "These verses are parsed by the PLY port into a tree containing at least "
            "one line with the token ERROR. They are drawn from two PLY output "
            "directories: ply/ (the 51 verses the C oracle also flags) and ply-tms/ "
            "(47 verses the C binary emits no output for). The output_dir field on "
            "each row names which directory holds that verse's ERROR tree."
        ),
        "summary": {
            "oddballs": len(oddball_rows),
            "books_with_oddballs": len(books_with_oddballs),
        },
        "oddballs": oddball_rows,
    }
    oddballs_payload = provenance.with_json_provenance(oddballs_payload, __file__)

    books_with_troublemakers = {
        _ref_to_tuple(str(row["ref"]))[0] for row in troublemaker_rows
    }
    troublemakers_payload: dict[str, object] = {
        "artifacts_description": "verses producing no output even under the PLY port",
        "payload_provenance_note": (
            "These verses are hardcoded troublemaker exclusions (tms.HARDCODED_REFS) "
            "that produce no parse tree even under the PLY port, unlike the 47 "
            "siblings reclassified as oddballs."
        ),
        "summary": {
            "troublemakers_excluded": len(troublemaker_rows),
            "books_with_troublemakers": len(books_with_troublemakers),
        },
        "troublemakers": troublemaker_rows,
    }
    troublemakers_payload = provenance.with_json_provenance(
        troublemakers_payload, __file__
    )

    _write_json(oddballs_out, oddballs_payload)
    _write_json(troubles_out, troublemakers_payload)


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")
