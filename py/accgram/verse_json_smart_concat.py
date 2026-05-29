from __future__ import annotations

_MAQAF = "־"


def smart_concatenate_wlc422_verse(verse_payload: dict[str, object]) -> dict[str, object]:
    vels = verse_payload.get("vels")
    if not isinstance(vels, list):
        return verse_payload

    out_verse = dict(verse_payload)
    out_verse["vels"] = smart_concatenate_string_runs(vels)
    return out_verse


def smart_concatenate_row_for_json(row: dict[str, object]) -> dict[str, object]:
    out_row = dict(row)

    wlc422_verse = out_row.get("wlc422_kq_u_verse")
    if isinstance(wlc422_verse, dict):
        out_row["wlc422_kq_u_verse"] = smart_concatenate_wlc422_verse(wlc422_verse)

    uxlc_verse = out_row.get("uxlc_verse")
    if isinstance(uxlc_verse, list):
        out_row["uxlc_verse"] = smart_concatenate_string_runs(uxlc_verse)

    return out_row


def smart_concatenate_string_runs(nodes: list[object]) -> list[object]:
    out_nodes: list[object] = []
    previous_input_string: str | None = None

    for node in nodes:
        if isinstance(node, str) and out_nodes and isinstance(out_nodes[-1], str):
            assert previous_input_string is not None
            assert " " not in previous_input_string, (
                f"Expected no spaces before concatenation: {previous_input_string!r}"
            )
            assert " " not in node, f"Expected no spaces before concatenation: {node!r}"

            prev = out_nodes[-1]
            sep = "" if prev.endswith(_MAQAF) else " "
            out_nodes[-1] = f"{prev}{sep}{node}"
            previous_input_string = node
            continue

        out_nodes.append(node)
        previous_input_string = node if isinstance(node, str) else None

    return out_nodes
