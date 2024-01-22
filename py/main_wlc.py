""" Exports main """


import my_open
import my_wlc_compare_wlcs

_IO_DIR = '../wlc-utils-io'


def _word1_to_veldics(word1):
    # wn_dic: dict with keys "word" and "notes"
    # veldic: verse element dict (parasep or wn_dic)
    wn_dic1 = {'word': word1, 'notes': []}
    wn_dic2 = _extract_notes(wn_dic1)
    veldic = _distinguish_parasep(wn_dic2)
    veldics = _isolate_atoms(veldic)
    return veldics


def _extract_notes(wn_dic):
    # wn_dic: dict with keys "word" and "notes"
    word = wn_dic['word']
    if len(word) > 2 and word[-2] == ']':
        notes = wn_dic['notes']
        new_notes = [word[-2:], *notes]
        new_wn_dic = {'word': word[:-2], 'notes': new_notes}
        return _extract_notes(new_wn_dic)  # recurse
    return wn_dic


def _distinguish_parasep(wn_dic):
    # wn_dic: dict with keys "word" and "notes"
    word = wn_dic['word']
    if word in ('P', 'S'):
        assert not wn_dic['notes']
        return {'parasep': word}
    return wn_dic

def _is_parasep(veldic):
    return list(veldic.keys()) == ['parasep']


def _isolate_atoms(veldic):
    # wn_dic: dict with keys "word" and "notes"
    if _is_parasep(veldic):
        return [veldic]
    wn_dic = veldic
    word = wn_dic['word']
    pre, sep, post = word.partition('-')
    assert pre != ''
    if post != '':
        assert sep == '-'
        assert pre != ''
        assert '-' not in pre
        pre_plus_sep = pre + sep
        wn_dic_for_pps = {'word': pre_plus_sep, 'notes': []}
        wn_dic_for_post = {'word': post, 'notes': wn_dic['notes']}
        wn_dics_for_post = _isolate_atoms(wn_dic_for_post)  # recurse
        return [wn_dic_for_pps, *wn_dics_for_post]
    assert sep in ('', '-')
    return [wn_dic]


def _veldic_to_velsod(veldic):
    # vel as dict always (veldic) to vel as a string or a dict (velsod)
    if _is_parasep(veldic):
        return veldic
    wn_dic = veldic
    if not wn_dic['notes']:
        return wn_dic['word']
    return wn_dic


def _validate_veldic(veldic):
    if _is_parasep(veldic):
        return
    wn_dic = veldic
    word = wn_dic['word']
    assert ']' not in word
    index_of_dash = word.find('-')
    assert index_of_dash in (-1, len(word) - 1)


def _collect_features_of_interest(io_fois, bcv, veldic):
    if _is_parasep(veldic):
        p_or_s = veldic['parasep']
        parasep_foi = io_fois['parasep_foi']
        parasep_foi[p_or_s] += 1
        return
    wn_dic = veldic
    word = wn_dic['word']
    notes = wn_dic['notes']
    for note in notes:
        counts, cases = _get_counts_and_cases(io_fois, note)
        #
        if note not in counts:
            counts[note] = 0
        counts[note] += 1
        #
        notes_str = ''.join(notes)
        case = {'note': note, 'bcv': bcv, 'word': word, 'notes_str': notes_str}
        cases.append(case)
    return


def _get_counts_and_cases(io_fois, note):
    notes_foi = io_fois['notes_foi']
    counts = notes_foi['counts']
    cases = notes_foi['cases']
    return counts, cases


def _sum_of_lists(lists):
    """ Return the sum of lists. """
    accum = []
    for the_list in lists:
        accum.extend(the_list)
    return accum


def _parse_body_line(io_fois, body_line):
    space_sep_strs = body_line.split(' ')
    bcv = space_sep_strs[0]
    word1s = space_sep_strs[1:]
    list_of_lists_of_veldics = list(map(_word1_to_veldics, word1s))
    veldics = _sum_of_lists(list_of_lists_of_veldics)
    for veldic in veldics:
        _validate_veldic(veldic)
        _collect_features_of_interest(io_fois, bcv, veldic)
    velsods = list(map(_veldic_to_velsod, veldics))
    return {'bcv': bcv, 'vels': velsods}


def _read_and_parse(wlc_id):
    in_path = f'{_IO_DIR}/in/{wlc_id}/{wlc_id}_ps.txt'
    parsed = {'header': [], 'body': []}
    io_fois = {
        'parasep_foi': {'P': 0, 'S': 0},
        'notes_foi': {
            'counts': {},
            'cases': []
        },
    }
    with open(in_path, encoding='utf-8', newline='') as wlc_in_fp:
        header_or_body = 'header'
        for rawline in wlc_in_fp:
            assert rawline[-1] == '\n'
            line = rawline[:-1]
            if line.startswith('#'):
                assert header_or_body == 'header'
                parsed['header'].append(line)
            else:
                assert header_or_body == 'header'
                parsed_body_line = _parse_body_line(io_fois, line)
                parsed['body'].append(parsed_body_line)
    io_fois['notes_foi'] = _sort_notes_foi(io_fois['notes_foi'])
    return parsed, io_fois


def _sort_notes_foi(notes_foi):
    nfc = notes_foi['counts']
    nfc_sorted = dict(sorted(nfc.items()))
    notes_foi_out = {
        'notes': list(nfc_sorted.keys()),
        'counts': nfc_sorted,
        'cases': notes_foi['cases'],
    }
    return notes_foi_out


def _write_smallish_files(wlc_id, parsed):
    out_path_for_header = f'{_IO_DIR}/out/{wlc_id}/{wlc_id}_ps.0header.json'
    my_open.json_dump_to_file_path(parsed['header'], out_path_for_header)
    sfc = 0  # smallish file count
    bkids_icf = {}  # icf: in current [output] file
    body_els_icf = []  # icf: in current [output] file
    for body_el in parsed['body']:
        bk_of_body_el = _bk_of_body_el(body_el)
        # If we're already bigger than we'd like to be
        # and we're starting a new book ...
        if len(body_els_icf) > 1500 and bk_of_body_el not in bkids_icf:
            _write_smallish_file(wlc_id, sfc, bkids_icf, body_els_icf)
            sfc += 1
            bkids_icf = {}
            body_els_icf = []
        else:
            bkids_icf[bk_of_body_el] = True
            body_els_icf.append(body_el)
    if body_els_icf:
        _write_smallish_file(wlc_id, sfc, bkids_icf, body_els_icf)



def _bk_of_body_el(body_el):
    bcv = body_el['bcv']
    bk_of_body_el = bcv[:2]
    return bk_of_body_el


def _write_smallish_file(wlc_id, sfc, bkids_icf, body_els_icf):
    str_for_bkids = ''.join(bkids_icf)  # e.g. 'exlv'
    str_for_sfc = f'{sfc:02}'  # e.g. '02' (smallish file count)
    str_for_sfc_and_bkids = str_for_sfc + '_' + str_for_bkids
    out_path = f'{_IO_DIR}/out/{wlc_id}/{wlc_id}_ps.1body_{str_for_sfc_and_bkids}.json'
    my_open.json_dump_to_file_path(body_els_icf, out_path)


def _write_fois(wlc_id, fois):
    out_path = f'{_IO_DIR}/out/{wlc_id}/{wlc_id}_ps.fois.json'
    my_open.json_dump_to_file_path(fois, out_path)


def _write_diff(wlc_ids, diff):
    wlc_ida, wlc_idb = wlc_ids
    out_path = f'{_IO_DIR}/out/{wlc_idb}/diff_{wlc_ida}_{wlc_idb}_ps.json'
    my_open.json_dump_to_file_path(diff, out_path)


def _do_one_wlc(wlc_id):
    parsed, io_fois = _read_and_parse(wlc_id)
    _write_smallish_files(wlc_id, parsed)
    _write_fois(wlc_id, io_fois)
    return parsed


def main():
    """ Process WLC 4.20 & WLC 4.22 in various ways. """
    wlc_ids = 'wlc420', 'wlc422'
    parsed = {id: _do_one_wlc(id) for id in wlc_ids}
    diff = my_wlc_compare_wlcs.compare_wlcs(*tuple(parsed.values()))
    _write_diff(wlc_ids, diff)


if __name__ == "__main__":
    main()
