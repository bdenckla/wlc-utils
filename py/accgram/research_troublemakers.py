from __future__ import annotations

import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from accgram.hebrew_verse_sanitize import sanitize_verse_text_payload
from accgram.troublemaker_structured_text import STRUCTURED_TEXT_BY_REF
from accgram.wlc_uxlc_diff import diff_wlc_uxlc
from accgram.wlc_book_codes import wlc_bb_to_bk39id
from mb_cmn import provenance
from py_uxlc import my_uxlc


_TROUBLEMAKER_REF_RE = re.compile(r"^(?P<bb>[0-9a-z]{2})\s+(?P<ch>\d+):(?P<vr>\d+)$")


def default_troubles_in(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "goerwitz" / "_troublemakers.json"


def default_wlc422_kq_u_dir(repo_root: Path) -> Path:
    return repo_root.parent / "wlc-utils-io" / "out" / "wlc422-kq-u"


def default_uxlc_dir(repo_root: Path) -> Path:
    return repo_root / "in" / "UXLC-39"


def default_out_path(repo_root: Path) -> Path:
    return repo_root / "out" / "accgram" / "research-troublemakers.json"


def add_args(parser: argparse.ArgumentParser, repo_root: Path) -> None:
    parser.add_argument(
        "--troubles-in",
        type=Path,
        default=default_troubles_in(repo_root),
        help="Path to _troublemakers.json input.",
    )
    parser.add_argument(
        "--wlc422-kq-u-dir",
        type=Path,
        default=default_wlc422_kq_u_dir(repo_root),
        help="Directory containing 1verses_*.json files.",
    )
    parser.add_argument(
        "--uxlc-dir",
        type=Path,
        default=default_uxlc_dir(repo_root),
        help="Directory containing UXLC XML book files.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=default_out_path(repo_root),
        help="Output JSON path for enriched research artifact.",
    )


def run(args: argparse.Namespace) -> None:
    troubles_payload = _read_json(args.troubles_in)
    troublemakers = troubles_payload.get("troublemakers")
    if not isinstance(troublemakers, list):
        raise ValueError(f"Expected list at troubles payload key 'troublemakers': {args.troubles_in}")

    parsed_rows: list[tuple[dict[str, object], str, str]] = []
    refs_by_book: dict[str, set[tuple[int, int]]] = {}
    for row in troublemakers:
        if not isinstance(row, dict):
            raise ValueError("Troublemaker rows must be JSON objects")
        ref_value = row.get("ref")
        if not isinstance(ref_value, str):
            raise ValueError("Troublemaker row is missing string field 'ref'")
        bb, chnu, vrnu = _parse_ref(ref_value)
        bcv = _to_compact_bcv(bb, chnu, vrnu)
        ref = _to_ref(bb, chnu, vrnu)
        refs_by_book.setdefault(bb, set()).add((chnu, vrnu))
        parsed_rows.append((row, bcv, ref))

    wlc422_by_bcv = _load_wlc422_index(args.wlc422_kq_u_dir)
    uxlc_by_bcv = _load_uxlc_for_refs(args.uxlc_dir, refs_by_book)

    found_wlc422 = 0
    missing_wlc422 = 0
    found_uxlc = 0
    missing_uxlc = 0

    enriched_rows: list[dict[str, object]] = []
    for row, bcv, ref in parsed_rows:
        wlc422_verse = wlc422_by_bcv.get(bcv)
        if wlc422_verse is None:
            missing_wlc422 += 1
        else:
            found_wlc422 += 1
            wlc422_verse = _interpolate_wlc422_kq_qere(wlc422_verse)
            wlc422_verse = sanitize_verse_text_payload(wlc422_verse)
            if isinstance(wlc422_verse, dict):
                wlc422_verse.pop("bcv", None)

        uxlc_info = uxlc_by_bcv.get(bcv)
        if uxlc_info is None:
            missing_uxlc += 1
            uxlc_nodes = None
        else:
            found_uxlc += 1
            uxlc_nodes = uxlc_info["nodes"]
            uxlc_nodes = sanitize_verse_text_payload(uxlc_nodes)

        enriched_row: dict[str, object] = {
            **row,
            "wlc422_kq_u_verse": wlc422_verse,
            "uxlc_verse": uxlc_nodes,
            "diff_wlc_uxlc": diff_wlc_uxlc(wlc422_verse, uxlc_nodes),
        }
        structured_text = STRUCTURED_TEXT_BY_REF.get(ref)
        if structured_text is not None:
            enriched_row["structured_text"] = structured_text
        enriched_rows.append(enriched_row)

    payload: dict[str, object] = {
        "artifacts_description": "enriched troublemaker verse research records",
        "payload_provenance_note": (
            "This artifact augments existing troublemaker rows with linked verse payloads "
            "from wlc422-kq-u and XML-ish UXLC verse nodes."
        ),
        "input": str(args.troubles_in),
        "wlc422_kq_u_dir": str(args.wlc422_kq_u_dir),
        "uxlc_dir": str(args.uxlc_dir),
        "summary": {
            "troublemakers": len(enriched_rows),
            "wlc422_kq_u_found": found_wlc422,
            "wlc422_kq_u_missing": missing_wlc422,
            "uxlc_found": found_uxlc,
            "uxlc_missing": missing_uxlc,
        },
        "troublemakers": enriched_rows,
    }
    payload = provenance.with_json_provenance(payload, __file__)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f_out:
        json.dump(payload, f_out, ensure_ascii=False, indent=2)
        f_out.write("\n")

    print(f"Input troublemakers: {args.troubles_in}")
    print(f"wlc422-kq-u dir: {args.wlc422_kq_u_dir}")
    print(f"UXLC dir: {args.uxlc_dir}")
    print(f"Output: {args.out}")
    print(f"Rows: {len(enriched_rows)}")
    print(f"wlc422-kq-u found/missing: {found_wlc422}/{missing_wlc422}")
    print(f"UXLC found/missing: {found_uxlc}/{missing_uxlc}")


def _read_json(path: Path):
    with path.open("r", encoding="utf-8") as f_in:
        return json.load(f_in)


def _parse_ref(ref: str) -> tuple[str, int, int]:
    match = _TROUBLEMAKER_REF_RE.match(ref.strip())
    if match is None:
        raise ValueError(f"Malformed troublemaker ref: {ref}")
    bb = match.group("bb")
    chnu = int(match.group("ch"))
    vrnu = int(match.group("vr"))
    return bb, chnu, vrnu


def _to_compact_bcv(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb}{chnu}:{vrnu}"


def _to_ref(bb: str, chnu: int, vrnu: int) -> str:
    return f"{bb} {chnu}:{vrnu}"


def _load_wlc422_index(wlc422_kq_u_dir: Path) -> dict[str, dict[str, object]]:
    if not wlc422_kq_u_dir.is_dir():
        raise FileNotFoundError(f"wlc422-kq-u directory not found: {wlc422_kq_u_dir}")

    by_bcv: dict[str, dict[str, object]] = {}
    for in_path in sorted(wlc422_kq_u_dir.glob("1verses_*.json")):
        rows = _read_json(in_path)
        if not isinstance(rows, list):
            raise ValueError(f"Expected list in verses file: {in_path}")
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(f"Expected object rows in verses file: {in_path}")
            bcv = row.get("bcv")
            if not isinstance(bcv, str):
                raise ValueError(f"Expected string 'bcv' in {in_path}")
            if bcv in by_bcv:
                raise ValueError(f"Duplicate bcv across verses files: {bcv}")
            by_bcv[bcv] = row
    return by_bcv


def _interpolate_wlc422_kq_qere(verse_payload: dict[str, object]) -> dict[str, object]:
    vels = verse_payload.get("vels")
    if not isinstance(vels, list):
        return verse_payload

    out_verse: dict[str, object] = dict(verse_payload)
    out_vels: list[object] = []
    for token in vels:
        if not isinstance(token, dict):
            out_vels.append(token)
            continue

        kq = token.get("kq")
        if not isinstance(kq, list) or len(kq) < 2 or not isinstance(kq[1], list):
            out_vels.append(token)
            continue

        # Inline qere tokens directly into vels in place of the kq wrapper.
        out_vels.extend(kq[1])

    out_verse["vels"] = [_strip_sam_pe_inun_token(token) for token in out_vels]
    out_verse["vels"] = [token for token in out_verse["vels"] if token is not None]
    return out_verse


def _strip_sam_pe_inun_token(token: object) -> object | None:
    if not isinstance(token, dict):
        return token
    if set(token.keys()) == {"sam_pe_inun"}:
        return None
    return token


def _load_uxlc_for_refs(
    uxlc_dir: Path,
    refs_by_book: dict[str, set[tuple[int, int]]],
) -> dict[str, dict[str, object]]:
    if not uxlc_dir.is_dir():
        raise FileNotFoundError(f"UXLC directory not found: {uxlc_dir}")

    by_bcv: dict[str, dict[str, object]] = {}
    for bb, ref_pairs in refs_by_book.items():
        bk39id = wlc_bb_to_bk39id(bb)
        xml_basename = my_uxlc._UXLC_BOOK_FILE_NAMES[bk39id]
        xml_name = f"{xml_basename}.xml"
        xml_path = uxlc_dir / xml_name
        if not xml_path.is_file():
            continue

        tree = ET.parse(xml_path)
        root = tree.getroot()
        target_set = set(ref_pairs)

        for chapter in root.iter("c"):
            ch_attr = chapter.attrib.get("n")
            if ch_attr is None:
                continue
            try:
                chnu = int(ch_attr)
            except ValueError:
                continue
            for verse in chapter.iter("v"):
                v_attr = verse.attrib.get("n")
                if v_attr is None:
                    continue
                try:
                    vrnu = int(v_attr)
                except ValueError:
                    continue
                if (chnu, vrnu) not in target_set:
                    continue
                bcv = _to_compact_bcv(bb, chnu, vrnu)
                nodes = [_to_xmlish_verse_child(child) for child in verse]
                by_bcv[bcv] = {
                    "xml_file": xml_name,
                    "nodes": [node for node in nodes if node is not None],
                }
    return by_bcv


def _to_xmlish_verse_child(element: ET.Element) -> dict[str, object] | str | None:
    if element.tag in {"k", "pe", "samekh"}:
        return None

    tag = "w" if element.tag == "q" else element.tag
    node: dict[str, object] = {"tag": tag}

    # Preserve direct text plus tail text after inline children (e.g. <x>...</x>tail).
    # Do not include inline child text here; it is represented separately in children.
    text_parts = [(element.text or "")]
    for child in element:
        text_parts.append(child.tail or "")
    text = "".join(text_parts).strip()
    if text:
        node["text"] = text

    if element.attrib:
        node["attrs"] = dict(element.attrib)

    if tag == "w":
        children = [_to_xmlish_inline(child) for child in element if child.tag in {"s", "x"}]
        if children:
            node["children"] = children

    # Compact the common simple case to keep uxlc_verse readable.
    if set(node.keys()) == {"tag", "text"} and node["tag"] == "w":
        return str(node["text"])

    # Flatten the common word+single-note shape.
    if set(node.keys()) == {"tag", "text", "children"} and node["tag"] == "w":
        children = node["children"]
        if (
            isinstance(children, list)
            and len(children) == 1
            and isinstance(children[0], dict)
            and set(children[0].keys()) == {"tag", "text"}
            and children[0]["tag"] == "x"
        ):
            return {"text": str(node["text"]), "note": str(children[0]["text"])}

    return node


def _to_xmlish_inline(element: ET.Element) -> dict[str, object]:
    node: dict[str, object] = {"tag": element.tag}

    text = "".join(element.itertext()).strip()
    if text:
        node["text"] = text

    if element.attrib:
        node["attrs"] = dict(element.attrib)

    return node
