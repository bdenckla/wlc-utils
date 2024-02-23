""" Exports write. """

import my_wlc_read_and_parse
import my_wlc_foi_utils
import my_wlc_smallish_files


def write(tdir, wlc_id):
    parsed = my_wlc_read_and_parse.read_and_parse(tdir, wlc_id)
    my_wlc_smallish_files.write(tdir, wlc_id, parsed)
    my_wlc_foi_utils.write(tdir, wlc_id, parsed)
    return parsed
