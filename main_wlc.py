""" Exports main """

import py.wlc_write_to_json as wlc_write_to_json
import py.wlc_compare_with_uxlc as wu
import py.wlc_compare_with_wlc as ww


def _wu_out_path(wlc_id):
    return f"{_TDIR}/out/diff_{wlc_id}_uxlc_ps.json"


def _ww_out_path(ww_diff_ids):
    wlc_ida, wlc_idb = ww_diff_ids
    return f"{_TDIR}/out/diff_{wlc_ida}_{wlc_idb}_ps.json"


def main():
    """Process WLC 4.20 & WLC 4.22 in various ways."""
    wlc_write_to_json.write(_TDIR, "2025-03-21-uni")
    p321mcd = wlc_write_to_json.write(_TDIR, "2025-03-21-mcd")
    p420mcd = wlc_write_to_json.write(_TDIR, "wlc420")
    p422mcd = wlc_write_to_json.write(_TDIR, "wlc422")
    wu.compare(p420mcd, _UXLC_BOOKS_DIR, _wu_out_path)
    ww.compare(p420mcd, p422mcd, _ww_out_path)
    ww.compare(p420mcd, p321mcd, _ww_out_path)


_TDIR = "../wlc-utils-io"
_UXLC_BOOKS_DIR = f"{_TDIR}/in/Tanach-26.0--UXLC-1.0--2020-04-01/Books"


if __name__ == "__main__":
    main()
