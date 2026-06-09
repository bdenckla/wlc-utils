"""Python port of accutil.c: make_node, add_leaves, print_tree.

Reproduces the display_tree==1 path only.  Node layout mirrors the C `tn`
struct; output format is byte-for-byte identical to the C print_tree().
"""

from __future__ import annotations

from dataclasses import dataclass

INDENT_STRING = "  "


@dataclass
class TN:
    label: str
    left: TN | None = None
    right: TN | None = None
    leaves: str = ""


def make_node(label: str, left: TN, right: TN) -> TN:
    return TN(label=label, left=left, right=right)


def add_leaves(label: str, *leaf_names: str) -> TN:
    """Build a leaf node whose leaves string mirrors C add_leaves().

    Each name gets a trailing space appended, matching the C strcat loop.
    """
    leaves = "".join(name + " " for name in leaf_names)
    return TN(label=label, left=None, right=None, leaves=leaves)


def print_tree(tree: TN | None, indent_level: int = 0) -> str:
    """Return the C print_tree() output as a string.

    Internal node: <indent><level> <label>\\n, then recurse left then right.
    Leaf node: same header line, then <indent+1><leaves>\\n.
    """
    if tree is None:
        return ""
    indent = INDENT_STRING * indent_level
    out: list[str] = [f"{indent}{indent_level} {tree.label}\n"]
    if tree.left is not None:
        out.append(print_tree(tree.left, indent_level + 1))
        out.append(print_tree(tree.right, indent_level + 1))
    else:
        leaf_indent = INDENT_STRING * (indent_level + 1)
        out.append(f"{leaf_indent}{tree.leaves}\n")
    return "".join(out)
