""" Exports write. """

import my_open
import my_wlc_read_and_parse
import my_wlc_smallish_files


def write(tdir, wlc_id):
    parsed, io_fois = my_wlc_read_and_parse.read_and_parse(tdir, wlc_id)
    my_wlc_smallish_files.write(tdir, wlc_id, parsed)
    _write_fois(tdir, wlc_id, io_fois)
    return parsed


def _write_fois(tdir, wlc_id, fois):
    out_path = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.fois.json'
    my_open.json_dump_to_file_path(fois, out_path)
