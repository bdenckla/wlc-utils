""" Exports main """


import my_open
import my_wlc_compare_with_wlc
import my_wlc_write_to_json
import my_wlc_compare_with_uxlc


def _write_wu_diff(tdir, wlc_id, wu_diff):
    out_path = f'{tdir}/out/diff_{wlc_id}_uxlc_ps.json'
    my_open.json_dump_to_file_path(wu_diff, out_path)


def _write_ww_diff(tdir, wlc_ids, ww_diff):
    wlc_ida, wlc_idb = wlc_ids
    out_path = f'{tdir}/out/diff_{wlc_ida}_{wlc_idb}_ps.json'
    my_open.json_dump_to_file_path(ww_diff, out_path)


def main():
    """ Process WLC 4.20 & WLC 4.22 in various ways. """
    wlc_ids = 'wlc420', 'wlc422'
    tdir = '../wlc-utils-io'
    parsed = {id: my_wlc_write_to_json.write(tdir, id) for id in wlc_ids}
    wu_diff = my_wlc_compare_with_uxlc.compare(parsed['wlc420'])
    _write_wu_diff(tdir, 'wlc420', wu_diff)
    ww_diff = my_wlc_compare_with_wlc.compare(*tuple(parsed.values()))
    _write_ww_diff(tdir, wlc_ids, ww_diff)


if __name__ == "__main__":
    main()
