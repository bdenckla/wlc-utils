""" Exports read_and_parse. """

import my_wlc_foi_utils as foi_utils


def read_and_parse(tdir, wlc_id):
    in_path = f'{tdir}/in/{wlc_id}/{wlc_id}_ps.txt'
    parsed = {'header': [], 'body': []}
    io_fois = foi_utils.init()
    with open(in_path, encoding='utf-8', newline='') as wlc_in_fp:
        header_or_body = 'header'
        for rawline in wlc_in_fp:
            line = rawline.rstrip()
            if line.startswith('#'):
                assert header_or_body == 'header'
                parsed['header'].append(line)
            else:
                assert header_or_body == 'header'
                parsed_body_line = _parse_body_line(io_fois, line)
                parsed['body'].append(parsed_body_line)
    io_fois['notes_foi'] = foi_utils.sort_notes_foi(io_fois['notes_foi'])
    return parsed, io_fois


def _parse_body_line(io_fois, body_line):
    space_sep_strs = body_line.split(' ')
    bcv = space_sep_strs[0]
    word1s = space_sep_strs[1:]
    list_of_lists_of_veldics = list(map(_word1_to_veldics, word1s))
    veldics = _sum_of_lists(list_of_lists_of_veldics)
    for veldic in veldics:
        _validate_veldic(veldic)
        foi_utils.collect_features_of_interest(io_fois, bcv, veldic)
    velsods = list(map(_veldic_to_velsod, veldics))
    return {'bcv': bcv, 'vels': velsods}


def _sum_of_lists(lists):
    """ Return the sum of lists. """
    accum = []
    for the_list in lists:
        accum.extend(the_list)
    return accum


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
