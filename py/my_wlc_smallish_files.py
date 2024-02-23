""" Exports write. """

import my_open


def write(tdir, wlc_id, parsed):
    out_path_for_header = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.0header.json'
    my_open.json_dump_to_file_path(parsed['header'], out_path_for_header)
    sfc = 0  # smallish file count
    bkids_icf = {}  # icf: in current [output] file
    verses_icf = []  # icf: in current [output] file
    for verse in parsed['verses']:
        bk_of_verse = _bk_of_verse(verse)
        # If we're already bigger than we'd like to be
        # and we're starting a new book ...
        if len(verses_icf) > 1500 and bk_of_verse not in bkids_icf:
            _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, verses_icf)
            sfc += 1
            bkids_icf = {}
            verses_icf = []
        else:
            bkids_icf[bk_of_verse] = True
            verses_icf.append(verse)
    if verses_icf:
        _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, verses_icf)


def _bk_of_verse(verse):
    return verse['bcv'][:2]


def _write_smallish_file(tdir, wlc_id, sfc, bkids_icf, verses_icf):
    str_for_bkids = ''.join(bkids_icf)  # e.g. 'exlv'
    str_for_sfc = f'{sfc:02}'  # e.g. '02' (smallish file count)
    str_for_sfc_and_bkids = str_for_sfc + '_' + str_for_bkids
    out_path = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.1verses_{str_for_sfc_and_bkids}.json'
    my_open.json_dump_to_file_path(verses_icf, out_path)
