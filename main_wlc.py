""" Exports main """

import py.my_open as my_open
import py.wlc_compare_with_wlc as wlc_compare_with_wlc
import py.wlc_write_to_json as wlc_write_to_json
import py.wlc_compare_with_uxlc as wlc_compare_with_uxlc


def _write_wu_diff(tdir, wlc_id, wu_diff):
    out_path = f"{tdir}/out/diff_{wlc_id}_uxlc_ps.json"
    my_open.json_dump_to_file_path(wu_diff, out_path)


def _write_ww_diff(tdir, wlc_ids, ww_diff):
    wlc_ida, wlc_idb = wlc_ids
    out_path = f"{tdir}/out/diff_{wlc_ida}_{wlc_idb}_ps.json"
    my_open.json_dump_to_file_path(ww_diff, out_path)


def main():
    """Process WLC 4.20 & WLC 4.22 in various ways."""
    tdir = "../wlc-utils-io"
    wlc_write_to_json.write(tdir, "2025-03-21-uni")
    wlc_write_to_json.write(tdir, "2025-03-21-mcd")
    uni_only = False
    if uni_only:
        return
    wlc_mcd_ids = "wlc420", "wlc422"
    parsed = {id: wlc_write_to_json.write(tdir, id) for id in wlc_mcd_ids}
    wu_diff = wlc_compare_with_uxlc.compare(parsed["wlc420"])
    _write_wu_diff(tdir, "wlc420", wu_diff)
    ww_diff = wlc_compare_with_wlc.compare(parsed["wlc420"], parsed["wlc422"])
    _write_ww_diff(tdir, wlc_mcd_ids, ww_diff)


if __name__ == "__main__":
    main()
