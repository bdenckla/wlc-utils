from __future__ import annotations

from dataclasses import dataclass

from accgram import ob_tree_abbrev
from accgram import ob_tree_parse
from py_html import wlc_utils_html


@dataclass
class _Cell:
    start_col: int
    colspan: int
    text: str
    class_name: str | None = None


def render_error_tree_table(tree: ob_tree_parse.ErrorTree) -> object:
    if not tree.roots:
        raise ValueError("Cannot render an empty parse tree")

    spans_by_branch: dict[int, int] = {}
    for root in tree.roots:
        _compute_leaf_span(root, spans_by_branch)

    total_cols = sum(spans_by_branch[id(root)] for root in tree.roots)
    if total_cols <= 0:
        raise ValueError("Parse tree has no terminal leaves")

    rows_by_index: dict[int, list[_Cell]] = {}
    max_row_index = 0

    current_col = 0
    for root in tree.roots:
        root_max_row = _emit_branch_cells(
            branch=root,
            start_col=current_col,
            spans_by_branch=spans_by_branch,
            rows_by_index=rows_by_index,
        )
        max_row_index = max(max_row_index, root_max_row)
        current_col += spans_by_branch[id(root)]

    table_rows: list[object] = []
    for row_index in range(max_row_index + 1):
        row_cells = sorted(rows_by_index.get(row_index, []), key=lambda cell: cell.start_col)
        table_rows.append(
            _render_row(
                row_cells=row_cells,
                total_cols=total_cols,
            )
        )

    return wlc_utils_html.table(
        tuple(table_rows),
        {"class": "goerwitz-obs-error-table"},
    )


def _compute_leaf_span(
    branch: ob_tree_parse.TreeBranch,
    spans_by_branch: dict[int, int],
) -> int:
    span = 0
    for child in branch.children:
        if isinstance(child, ob_tree_parse.TreeLeaf):
            span += 1
        else:
            span += _compute_leaf_span(child, spans_by_branch)

    if span <= 0:
        raise ValueError(f"Branch has no leaves: depth={branch.depth}, label={branch.label!r}")

    spans_by_branch[id(branch)] = span
    return span


def _emit_branch_cells(
    *,
    branch: ob_tree_parse.TreeBranch,
    start_col: int,
    spans_by_branch: dict[int, int],
    rows_by_index: dict[int, list[_Cell]],
) -> int:
    branch_span = spans_by_branch[id(branch)]
    _append_cell(
        rows_by_index,
        row_index=branch.depth,
        cell=_Cell(
            start_col=start_col,
            colspan=branch_span,
            text=ob_tree_abbrev.abbreviate_branch_label(branch.depth, branch.label),
        ),
    )

    max_row_index = branch.depth
    child_col = start_col
    for child in branch.children:
        if isinstance(child, ob_tree_parse.TreeLeaf):
            leaf_row_index = branch.depth + 1
            _append_cell(
                rows_by_index,
                row_index=leaf_row_index,
                cell=_Cell(
                    start_col=child_col,
                    colspan=1,
                    text=ob_tree_abbrev.abbreviate_leaf_text(child.text),
                    class_name="goerwitz-obs-error-cell" if child.has_error else None,
                ),
            )
            max_row_index = max(max_row_index, leaf_row_index)
            child_col += 1
            continue

        child_max_row = _emit_branch_cells(
            branch=child,
            start_col=child_col,
            spans_by_branch=spans_by_branch,
            rows_by_index=rows_by_index,
        )
        max_row_index = max(max_row_index, child_max_row)
        child_col += spans_by_branch[id(child)]

    return max_row_index


def _append_cell(
    rows_by_index: dict[int, list[_Cell]],
    *,
    row_index: int,
    cell: _Cell,
) -> None:
    rows_by_index.setdefault(row_index, []).append(cell)


def _render_row(*, row_cells: list[_Cell], total_cols: int) -> object:
    td_cells: list[object] = []
    cursor = 0
    for cell in row_cells:
        if cell.start_col > cursor:
            td_cells.append(
                wlc_utils_html.table_datum(
                    "",
                    {"colspan": str(cell.start_col - cursor)},
                )
            )
            cursor = cell.start_col

        attrs: dict[str, str] = {}
        if cell.colspan > 1:
            attrs["colspan"] = str(cell.colspan)
        if cell.class_name is not None:
            attrs["class"] = cell.class_name

        td_cells.append(wlc_utils_html.table_datum(cell.text, attrs or None))
        cursor += cell.colspan

    if cursor < total_cols:
        td_cells.append(
            wlc_utils_html.table_datum(
                "",
                {"colspan": str(total_cols - cursor)},
            )
        )

    return wlc_utils_html.table_row(tuple(td_cells))