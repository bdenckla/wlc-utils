"""Golden test: output contract for ply_tree.print_tree().

Pins the exact byte output for Obadiah 1:2 — the simplest multi-level tree
in the oracle — so any change to indentation, label format, or leaf trailing-
space is caught immediately.

Run:
    .venv/Scripts/python.exe -m pytest py/tests/test_ply_tree_golden.py -v
"""

from accgram.ply_tree import add_leaves, make_node, print_tree


def _ob_1_2_tree():
    """Hand-built tree for Obadiah 1:2 (from oracle wlc_422_ps_ob_ag.txt)."""
    return make_node(
        "silluq_clause",
        make_node(
            "atnax_clause",
            make_node(
                "tipexa_clause",
                add_leaves("tevir_phrase", "merkha", "tevir"),
                add_leaves("tipexa_phrase", "tipexa"),
            ),
            add_leaves("atnax_phrase", "atnax"),
        ),
        make_node(
            "silluq_clause",
            add_leaves("tipexa_phrase", "merkha", "tipexa"),
            add_leaves("silluq_phrase", "silluq"),
        ),
    )


_OB_1_2_EXPECTED_TREE = (
    "0 silluq_clause\n"
    "  1 atnax_clause\n"
    "    2 tipexa_clause\n"
    "      3 tevir_phrase\n"
    "        merkha tevir \n"
    "      3 tipexa_phrase\n"
    "        tipexa \n"
    "    2 atnax_phrase\n"
    "      atnax \n"
    "  1 silluq_clause\n"
    "    2 tipexa_phrase\n"
    "      merkha tipexa \n"
    "    2 silluq_phrase\n"
    "      silluq \n"
)

_OB_1_2_EXPECTED_VERSE = "Obadiah 1:2\n" + _OB_1_2_EXPECTED_TREE


def test_print_tree_ob_1_2():
    """print_tree() output matches the oracle byte-for-byte."""
    got = print_tree(_ob_1_2_tree(), indent_level=0)
    assert got == _OB_1_2_EXPECTED_TREE


def test_verse_output_ob_1_2():
    """Reference line + print_tree() matches the full oracle verse block."""
    ref_line = "Obadiah 1:2"
    verse_output = f"{ref_line}\n" + print_tree(_ob_1_2_tree(), indent_level=0)
    assert verse_output == _OB_1_2_EXPECTED_VERSE


def test_leaf_trailing_space():
    """Each leaf name in add_leaves() gets a trailing space (C strcat loop)."""
    node = add_leaves("test_phrase", "merkha", "tipexa")
    assert node.leaves == "merkha tipexa "


def test_single_leaf_trailing_space():
    """Single-leaf node still gets trailing space."""
    node = add_leaves("silluq_phrase", "silluq")
    assert node.leaves == "silluq "


def test_internal_node_structure():
    """make_node() sets left/right children and has no leaves string."""
    left = add_leaves("a_phrase", "foo")
    right = add_leaves("b_phrase", "bar")
    parent = make_node("ab_clause", left, right)
    assert parent.left is left
    assert parent.right is right
    assert parent.label == "ab_clause"
