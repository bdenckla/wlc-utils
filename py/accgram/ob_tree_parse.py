from __future__ import annotations

from dataclasses import dataclass
from re import Pattern


@dataclass
class TreeLeaf:
    text: str
    has_error: bool


@dataclass
class TreeBranch:
    depth: int
    label: str
    children: list[TreeBranch | TreeLeaf]


@dataclass
class ErrorTree:
    roots: list[TreeBranch]
    has_error_leaf: bool


def parse_verse_tree(
    *,
    verse_lines: list[str],
    node_line_re: Pattern[str],
    error_token_re: Pattern[str],
) -> ErrorTree:
    roots: list[TreeBranch] = []
    stack: list[TreeBranch] = []
    has_error_leaf = False

    for line in verse_lines:
        stripped = line.strip()
        if not stripped:
            continue

        node_match = node_line_re.match(line)
        if node_match is not None:
            depth = int(node_match.group(1))
            label = node_match.group(2).strip()

            while stack and stack[-1].depth >= depth:
                stack.pop()

            branch = TreeBranch(depth=depth, label=label, children=[])
            if stack:
                stack[-1].children.append(branch)
            else:
                roots.append(branch)
            stack.append(branch)
            continue

        if not stack:
            raise ValueError(
                "Leaf line encountered before any branch node: " f"{stripped!r}"
            )

        has_error = error_token_re.search(stripped) is not None
        has_error_leaf = has_error_leaf or has_error
        stack[-1].children.append(TreeLeaf(text=stripped, has_error=has_error))

    return ErrorTree(roots=roots, has_error_leaf=has_error_leaf)


def iter_leaf_texts(tree: ErrorTree) -> list[str]:
    out: list[str] = []

    def _visit_branch(branch: TreeBranch) -> None:
        for child in branch.children:
            if isinstance(child, TreeLeaf):
                out.append(child.text)
            else:
                _visit_branch(child)

    for root in tree.roots:
        _visit_branch(root)
    return out
