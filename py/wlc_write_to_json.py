""" Exports write. """

import py.wlc_read_and_parse_mdc as rp_mdc
import py.wlc_read_and_parse_uni as rp_uni
import py.wlc_kqparse as kqparse
import py.wlc_foi_utils as foi_utils
import py.wlc_smallish_files as smallish_files
import py.wlc_convert_p_mcd_to_p_uni as mu
import py.wlc_release_info as ri


def write(path_info, wlc_id):
    in_path_fn, sf_out_path_fn, foi_out_path_fn = path_info
    in_file_filename = ri.RELEASE_INFO["ri-filenames"][wlc_id]
    format = ri.RELEASE_INFO["ri-formats"][wlc_id]
    in_path = in_path_fn(wlc_id)
    in_file_path = f"{in_path}/{in_file_filename}"
    read_and_parse_fn = _READ_AND_PARSE_FNS[format]
    parsed = read_and_parse_fn(in_file_path)
    smallish_files.write(sf_out_path_fn(wlc_id, ""), parsed)
    foi_utils.write(foi_out_path_fn, wlc_id, parsed)
    _write_kq(path_info, wlc_id, parsed)
    if ri.encoding_is_mdc(wlc_id):
        uparsed = mu.convert_p_mcd_to_p_uni(parsed)
        smallish_files.write(sf_out_path_fn(wlc_id, "-u"), uparsed)
    return {"id": wlc_id, **parsed}


def _write_kq(path_info, wlc_id, parsed):
    _in_path_fn, sf_out_path_fn, foi_out_path_fn = path_info
    kqparsed = kqparse.kqparse(parsed)
    smallish_files.write(sf_out_path_fn(wlc_id, "-kq"), kqparsed)
    foi_utils.kqwrite(foi_out_path_fn, wlc_id, kqparsed)
    if ri.encoding_is_mdc(wlc_id):
        ukqparsed = mu.convert_p_mcd_to_p_uni(kqparsed)
        smallish_files.write(sf_out_path_fn(wlc_id, "-kq-u"), ukqparsed)


_READ_AND_PARSE_FNS = {
    "fmt-M-C": rp_mdc.read_and_parse,
    "fmt-Uni": rp_uni.read_and_parse,
}
