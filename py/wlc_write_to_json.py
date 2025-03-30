""" Exports write. """

import py.wlc_read_and_parse as wlc_read_and_parse
import py.wlc_kqparse as wlc_kqparse
import py.wlc_foi_utils as wlc_foi_utils
import py.wlc_smallish_files as wlc_smallish_files
import py.wlc_convert_p_mc_to_p_unicode as mu


def write(tdir, wlc_id):
    parsed = wlc_read_and_parse.read_and_parse(tdir, wlc_id)
    kqparsed = wlc_kqparse.kqparse(parsed)
    wlc_smallish_files.write(tdir, wlc_id, parsed)
    wlc_smallish_files.write(tdir, wlc_id, kqparsed, "-kq")
    wlc_foi_utils.write(tdir, wlc_id, parsed)
    wlc_foi_utils.kqwrite(tdir, wlc_id, kqparsed)
    #
    ukqparsed = mu.convert_p_mc_to_p_unicode(kqparsed)
    wlc_smallish_files.write(tdir, wlc_id, ukqparsed, "-kq-u")
    #
    return parsed
