""" Exports write. """

import my_open


def write(tdir, wlc_id, parsed):
    out_path_for_header = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.0header.json'
    my_open.json_dump_to_file_path(parsed['header'], out_path_for_header)
    sfc = 0  # smallish file count
    bkids_icf = {}  # icf: in current [output] file
    body_els_icf = []  # icf: in current [output] file
    for body_el in parsed['body']:
        bk_of_body_el = _bk_of_body_el(body_el)
        # If we're already bigger than we'd like to be
        # and we're starting a new book ...
        if len(body_els_icf) > 1500 and bk_of_body_el not in bkids_icf:
            _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, body_els_icf)
            sfc += 1
            bkids_icf = {}
            body_els_icf = []
        else:
            bkids_icf[bk_of_body_el] = True
            body_els_icf.append(body_el)
    if body_els_icf:
        _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, body_els_icf)


def _bk_of_body_el(body_el):
    bcv = body_el['bcv']
    bk_of_body_el = bcv[:2]
    return bk_of_body_el


def _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, body_els_icf):
    str_for_bkids = ''.join(bkids_icf)  # e.g. 'exlv'
    str_for_sfc = f'{sfc:02}'  # e.g. '02' (smallish file count)
    str_for_sfc_and_bkids = str_for_sfc + '_' + str_for_bkids
    out_path = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.1body_{str_for_sfc_and_bkids}.json'
    my_open.json_dump_to_file_path(body_els_icf, out_path)
