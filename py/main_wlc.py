""" Exports main """


import my_open
import my_wlc_compare_wlcs
import my_wlc_write_to_json


def _write_diff(tdir, wlc_ids, diff):
    wlc_ida, wlc_idb = wlc_ids
    out_path = f'{tdir}/out/{wlc_idb}/diff_{wlc_ida}_{wlc_idb}_ps.json'
    my_open.json_dump_to_file_path(diff, out_path)


def main():
    """ Process WLC 4.20 & WLC 4.22 in various ways. """
    wlc_ids = 'wlc420', 'wlc422'
    tdir = '../wlc-utils-io'
    parsed = {id: my_wlc_write_to_json.write(tdir, id) for id in wlc_ids}
    diff = my_wlc_compare_wlcs.compare_wlcs(*tuple(parsed.values()))
    _write_diff(tdir, wlc_ids, diff)


if __name__ == "__main__":
    main()
