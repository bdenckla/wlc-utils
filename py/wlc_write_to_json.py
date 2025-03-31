""" Exports write. """

import py.wlc_read_and_parse_mdc as rp_mdc
import py.wlc_read_and_parse_mdc as rp_uni
import py.wlc_kqparse as kqparse
import py.wlc_foi_utils as foi_utils
import py.wlc_smallish_files as smallish_files
import py.wlc_convert_p_mcd_to_p_uni as mu


def write(tdir, wlc_id):
    parsed, _kqparsed = _write(tdir, wlc_id)
    return parsed


def write_uni(tdir, wlc_id):
    _parsed, kqparsed = _write(tdir, wlc_id)
    ukqparsed = mu.convert_p_mc_to_p_unicode(kqparsed)
    smallish_files.write(tdir, wlc_id, ukqparsed, "-kq-u")


def _write(tdir, wlc_id):
    filename = _FILENAMES[wlc_id]
    read_and_parse_fn = _READ_AND_PARSE_FNS[wlc_id]
    parsed = read_and_parse_fn(tdir, wlc_id, filename)
    kqparsed = kqparse.kqparse(parsed)
    smallish_files.write(tdir, wlc_id, parsed)
    smallish_files.write(tdir, wlc_id, kqparsed, "-kq")
    foi_utils.write(tdir, wlc_id, parsed)
    foi_utils.kqwrite(tdir, wlc_id, kqparsed)
    return parsed, kqparsed


_FILENAMES = {
    "wlc420": "wlc420_ps.txt",
    "wlc422": "wlc422_ps.txt",
    "WLCU-2025-03-21": "wlcubs420.txt"
}
_FORMATS = {
    "wlc420": "fmt-M-C",
    "wlc422": "fmt-M-C",
    "WLCU-2025-03-21": "fmt-Uni"
}
_READ_AND_PARSE_FNS = {
    "fmt-M-C": rp_mdc.read_and_parse,
    "fmt-Uni": rp_uni.read_and_parse,
}
