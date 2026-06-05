from __future__ import annotations

import json
from pathlib import Path

from mb_cmn import bib_locales as tbn
from mb_cmn import hebrew_punctuation as hpunc
from mb_misc import osis_book_abbrevs as oba

from cmn.wlc_book_codes import wlc_bb_to_bk39id


def default_mam_simple_dir(repo_root: Path) -> Path:
    return repo_root.parent / "MAM-simple" / "json-vtrad-bhs"


def load_mam_simple_for_refs(
    mam_simple_dir: Path,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> dict[str, dict[str, object]]:
    if not mam_simple_dir.is_dir():
        raise FileNotFoundError(f"MAM-simple directory not found: {mam_simple_dir}")

    by_bcv: dict[str, dict[str, object]] = {}
    for bb, ref_pairs in refs_by_book.items():
        bk39id = wlc_bb_to_bk39id(bb)
        json_path = _mam_simple_json_path(mam_simple_dir, bk39id)
        if json_path is None:
            continue

        root = _read_json(json_path)
        if not isinstance(root, dict):
            raise ValueError(f"Expected root object in MAM-simple file: {json_path}")

        target_set = set(ref_pairs)
        for verse_node in _iter_dict_nodes(root):
            if verse_node.get("type") != "verse":
                continue

            osis_id = verse_node.get("osisID")
            osis_prefix = oba.BOOK_ABBREVS.get(bk39id)
            if (
                not isinstance(osis_id, str)
                or osis_prefix is None
                or not osis_id.startswith(f"{osis_prefix}.")
            ):
                continue

            chnu, vrnu = _parse_osis_id(osis_id)
            if (chnu, vrnu) not in target_set:
                continue

            bcv = f"{bb}{chnu}:{vrnu}"
            by_bcv[bcv] = {
                "mam_simple_json_file": json_path.name,
                "mam_simple_verse": _normalize_mam_simple_verse(verse_node),
            }

    return by_bcv


def _mam_simple_json_path(mam_simple_dir: Path, bk39id: str) -> Path | None:
    candidate_names = [_mam_simple_json_file_for_bk39id(bk39id), f"{bk39id}.json"]
    for candidate_name in candidate_names:
        candidate_path = mam_simple_dir / candidate_name
        if candidate_path.is_file():
            return candidate_path
    return None


def _mam_simple_json_file_for_bk39id(bk39id: str) -> str:
    bk24id = tbn.bk24id(bk39id)
    bk39ids = tbn.bk39ids_of_bk24(bk24id)
    if not bk39ids:
        return f"{bk39id}.json"

    first_prefix = oba.BOOK_ABBREVS.get(bk39ids[0])
    last_prefix = oba.BOOK_ABBREVS.get(bk39ids[-1])
    if first_prefix is None or last_prefix is None:
        return f"{bk39id}.json"

    if len(bk39ids) == 1:
        return f"{first_prefix}.json"
    return f"{first_prefix}-{last_prefix}.json"


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f_in:
        return json.load(f_in)


def _iter_dict_nodes(value: object):
    if isinstance(value, dict):
        yield value
        contents = value.get("contents")
        if isinstance(contents, list):
            for child in contents:
                yield from _iter_dict_nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_dict_nodes(child)


def _parse_osis_id(osis_id: str) -> tuple[int, int]:
    parts = osis_id.split(".")
    if len(parts) != 3:
        raise ValueError(f"Malformed MAM-simple osisID: {osis_id}")

    try:
        chnu = int(parts[1])
        vrnu = int(parts[2])
    except ValueError as exc:
        raise ValueError(f"Malformed MAM-simple osisID: {osis_id}") from exc

    return chnu, vrnu


def _normalize_mam_simple_verse(verse_node: dict[str, object]) -> dict[str, object]:
    vels = _normalize_mam_simple_node(verse_node)
    return {"vels": vels}


def _normalize_mam_simple_node(node: object) -> list[object]:
    if not isinstance(node, dict):
        return []

    node_type = node.get("type")
    if isinstance(node_type, str):
        if node_type in {
            "spi-pe2",
            "spi-pe3",
            "spi-samekh2",
            "spi-samekh3",
            "spi-invnun",
        }:
            return []
        if node_type in {"lp-paseq", "lp-legarmeih"}:
            return [hpunc.PASOLEG]
        if node_type == "implicit-maqaf":
            return [hpunc.MAQ]
        if node_type in {"kq", "kq-trivial", "kq-q-velo-k"}:
            return _normalize_mam_simple_kq_qere(node)
        if node_type in {"kq-k", "ketiv", "kq-k-velo-q"}:
            return []

    contents = node.get("contents")
    if isinstance(contents, list):
        out_tokens: list[object] = []
        for child in contents:
            out_tokens.extend(_normalize_mam_simple_node(child))
        return out_tokens

    text = node.get("text")
    if isinstance(text, str):
        return _split_mam_simple_text(text)

    return []


def _normalize_mam_simple_kq_qere(node: dict[str, object]) -> list[object]:
    contents = node.get("contents")
    if not isinstance(contents, list):
        text = node.get("text")
        if isinstance(text, str):
            return _split_mam_simple_text(text)
        return []

    qere_nodes = [
        child for child in contents if isinstance(child, dict) and _is_qere_node(child)
    ]
    if qere_nodes:
        out_tokens: list[object] = []
        for qere_node in qere_nodes:
            out_tokens.extend(_normalize_mam_simple_node(qere_node))
        return out_tokens

    out_tokens: list[object] = []
    for child in contents:
        if isinstance(child, dict) and _is_ketiv_node(child):
            continue
        out_tokens.extend(_normalize_mam_simple_node(child))
    return out_tokens


def _is_qere_node(node: dict[str, object]) -> bool:
    node_type = node.get("type")
    return isinstance(node_type, str) and node_type in {
        "qere",
        "kq-q",
        "kq-trivial",
        "kq-q-velo-k",
    }


def _is_ketiv_node(node: dict[str, object]) -> bool:
    node_type = node.get("type")
    return isinstance(node_type, str) and node_type in {"ketiv", "kq-k", "kq-k-velo-q"}


def _split_mam_simple_text(text: str) -> list[object]:
    out_tokens: list[object] = []
    current = []
    for ch in text:
        if ch == " ":
            if current:
                out_tokens.append("".join(current))
                current = []
            continue

        current.append(ch)
        if ch == hpunc.MAQ:
            out_tokens.append("".join(current))
            current = []

    if current:
        out_tokens.append("".join(current))

    return out_tokens
