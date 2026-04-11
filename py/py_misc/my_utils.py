"""Compatibility wrapper for pycmn.my_utils."""

from pycmn.my_utils import *


def init(dic, key, val):
    """Backward-compatible alias for init_at_key."""
    init_at_key(dic, key, val)


def maybe_init(dic, key, val):
    """Backward-compatible alias for maybe_init_at_key."""
    maybe_init_at_key(dic, key, val)


def ll_map(fun, the_list):
    """Backward-compatible list-in, list-out map."""
    assert isinstance(the_list, list)
    return sl_map(fun, the_list)


def tt_map(fun, the_tuple):
    """Backward-compatible tuple-in, tuple-out map."""
    assert isinstance(the_tuple, tuple)
    return st_map(fun, the_tuple)


def sum_of_lists(lists):
    """Backward-compatible alias for flattening a sequence of lists."""
    return sum_of_seqs(lists)
