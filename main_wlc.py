""" Exports main """

import py.wlc_write_to_json as wlc_write_to_json
import py.wlc_compare_mdc_with_uxlc as mx
import py.wlc_compare_mdc_with_mdc as mm
import py.wlc_compare_uni_with_uni as uu


def _mx_out_path(wlc_id):
    return f"{_TDIR}/out/diff_mx_{wlc_id}_uxlc.json"


def _mm_out_path(ww_diff_ids):
    wlc_ida, wlc_idb = ww_diff_ids
    return f"{_TDIR}/out/diff_mm_{wlc_ida}_{wlc_idb}.json"


def _uu_out_path(ww_diff_ids):
    wlc_ida, wlc_idb = ww_diff_ids
    return f"{_TDIR}/out/diff_uu_{wlc_ida}_{wlc_idb}.json"


def _out_path(wlc_id, suffix):
    return f"{_TDIR}/out/{wlc_id}{suffix}"


def _in_path(wlc_id):
    return f"{_TDIR}/in/{wlc_id}"


def main():
    """Process WLC 4.20 & WLC 4.22 in various ways."""
    path_info = _in_path, _out_path
    p321uni = wlc_write_to_json.write(path_info, "2025-03-21-uni")
    p321mcd, p321mcdu = wlc_write_to_json.write(path_info, "2025-03-21-mcd")
    # p420mcd, _u = wlc_write_to_json.write(path_info, "wlc420")
    # p422mcd, _u = wlc_write_to_json.write(path_info, "wlc422")
    uu.compare(p321mcdu, p321uni, _uu_out_path)
    # mx.compare(p420mcd, _UXLC_BOOKS_DIR, _mx_out_path)
    # mm.compare(p420mcd, p422mcd, _mm_out_path)
    # mm.compare(p420mcd, p321mcd, _mm_out_path)


_TDIR = "../wlc-utils-io"
_UXLC_BOOKS_DIR = f"{_TDIR}/in/Tanach-26.0--UXLC-1.0--2020-04-01/Books"


if __name__ == "__main__":
    main()
