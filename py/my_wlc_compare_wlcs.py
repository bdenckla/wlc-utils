""" Exports compare_wlcs """

import my_wlc_utils
import my_wlc_compare_vyls


def compare_wlcs(wlca, wlcb):
    """ Compare wlca with wlcb (e.g. WLC 4.20 with WLC 4.22) """
    return _compare_wlc_verse_lists(wlca['verses'], wlcb['verses'])


def _compare_verse_element(io_diff, bcv, vela, velb):
    vyla = my_wlc_utils.velsod_to_veldic(vela)
    vylb = my_wlc_utils.velsod_to_veldic(velb)
    return my_wlc_compare_vyls.compare_vyls(io_diff, bcv, vyla, vylb)


def _compare_verse(io_diff, bcv, velsa, velsb):
    velsa_comparable = velsa
    if len(velsa_comparable) != len(velsb):
        diff_len_record = bcv, len(velsa_comparable), len(velsb)
        io_diff['verses_of_different_length'].append(diff_len_record)
    if bcv == 'gn14:17':
        part1part2 = _split_gn1417_word_9(velsa[8])
        velsa_comparable = [
            *velsa[:8],
            *part1part2,
            *velsa[9:]
        ]
        side_a_edit_record = {
            'bcv': bcv,
            'edit type': 'split word',
            'original word': velsa[8],
            'split word': part1part2
        }
        io_diff['side_a_edits'].append(side_a_edit_record)
    if bcv == 'da2:39':
        velsa_comparable = [
            *velsa[:4],
            None,
            *velsa[4:]
        ]
        side_a_edit_record = {
            'bcv': bcv,
            'edit type': 'added null word',
            'word before null word': velsa[3],
            'word after null word': velsa[4]}
        io_diff['side_a_edits'].append(side_a_edit_record)
    assert len(velsa_comparable) == len(velsb)
    for vel_ab in zip(velsa_comparable, velsb):
        _compare_verse_element(io_diff, bcv, *vel_ab)


def _split_gn1417_word_9(word_9):
    assert word_9['word'] == 'K.:DFRLF(O80MER'
    part1 = word_9['word'][:6]
    part2 = word_9['word'][6:]
    part1 = part1 + '→'
    part2 = '←' + part2
    return part1, {'word': part2, 'notes': word_9['notes']}


def _compare_wlc_verse_lists(verse_list_a, verse_list_b):
    io_diff = {
        'verses_of_different_length': [],
        'side_a_edits': [],
        'type changes': [],
        'notes differences': [],
        'word differences': [],
    }
    assert len(verse_list_a) == len(verse_list_b)
    for verse_ab in zip(verse_list_a, verse_list_b):
        verse_a, verse_b = verse_ab
        assert verse_a['bcv'] == verse_b['bcv']
        _compare_verse(
            io_diff, verse_a['bcv'], verse_a['vels'], verse_b['vels'])
    return io_diff
