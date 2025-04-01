""" Exports write. """

import py.wlc_read_and_parse_mdc as rp_mdc
import py.wlc_read_and_parse_uni as rp_uni
import py.wlc_kqparse as kqparse
import py.wlc_foi_utils as foi_utils
import py.wlc_smallish_files as smallish_files
import py.wlc_convert_p_mcd_to_p_uni as mu
import py.release_info as ri


def write(tdir, wlc_id):
    filename = ri.RELEASE_INFO["ri-filenames"][wlc_id]
    format = ri.RELEASE_INFO["ri-formats"][wlc_id]
    read_and_parse_fn = _READ_AND_PARSE_FNS[format]
    parsed = read_and_parse_fn(tdir, wlc_id, filename)
    smallish_files.write(tdir, wlc_id, parsed)
    foi_utils.write(tdir, wlc_id, parsed)
    if format == "fmt-M-C":
        uparsed = mu.convert_p_mcd_to_p_uni(parsed)
        smallish_files.write(tdir, wlc_id, uparsed, "-u")
    skip_kq = format == "fmt-Uni"
    if not skip_kq:
        _write_kq(tdir, wlc_id, parsed)
    return parsed


def _write_kq(tdir, wlc_id, parsed):
    kqparsed = kqparse.kqparse(parsed)
    smallish_files.write(tdir, wlc_id, kqparsed, "-kq")
    foi_utils.kqwrite(tdir, wlc_id, kqparsed)
    if format == "fmt-M-C":
        ukqparsed = mu.convert_p_mcd_to_p_uni(kqparsed)
        smallish_files.write(tdir, wlc_id, ukqparsed, "-kq-u")


_READ_AND_PARSE_FNS = {
    "fmt-M-C": rp_mdc.read_and_parse,
    "fmt-Uni": rp_uni.read_and_parse,
}
