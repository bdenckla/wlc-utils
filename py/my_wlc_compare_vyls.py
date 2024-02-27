""" Exports compare_vyls """

import my_uword


def compare_vyls(io_diff, bcv, vyla, vylb):
    """ Compare vyla and vylb, putting result in io_diff """
    typa = _vyltype(vyla)
    typb = _vyltype(vylb)
    if typa != typb:
        io_diff['type changes'].append({
            'bcv': bcv,
                **_vyla_to_cells(vyla),
                **_vylb_to_cells(vylb),
        })
    if typa == typb == _VYLTYPE_WN:
        if vyla['notes'] != vylb['notes']:
            _record_notes_diff(io_diff, bcv, vyla, vylb)
        worda_ns = vyla['word'].replace('/', '')
        wordb_ns = vylb['word'].replace('/', '')
        if worda_ns != wordb_ns:
            _record_word_diff(io_diff, bcv, vyla, vylb)


def _record_word_diff(io_diff, bcv, vyla, vylb):
    _new_field(vyla, vylb, 'cnotes', 'notes', lambda x : ''.join(x))
    _new_field(vyla, vylb, 'uword', 'word', my_uword.uword)
    if vyla['notes'] == vylb['notes']:
        word_diff_type = 'word changed but notes did not'
    else:
        word_diff_type = 'word changed and notes changed'
    io_diff['word differences'].append({
        'bcv': bcv,
        'word_diff_type': word_diff_type,
        'ab_word': _newline_sep(vyla, vylb, 'word'),
        'ab_uword': _newline_sep(vyla, vylb, 'uword'),
        'ab_notes': _newline_sep(vyla, vylb, 'cnotes'),
    })


def _new_field(dica, dicb, newkey, oldkey, fun):
    dica[newkey] = fun(dica[oldkey])
    dicb[newkey] = fun(dicb[oldkey])


def _newline_sep(dica, dicb, key):
    return dica[key] + '\n' + dicb[key]


def _record_notes_diff(io_diff, bcv, vyla, vylb):
    notesa = ''.join(vyla['notes'])
    notesb = ''.join(vylb['notes'])
    notes_change = ' → '.join((notesa or '∅', notesb or '∅'))
    worda_ns = vyla['word'].replace('/', '')
    wordb_ns = vylb['word'].replace('/', '')
    if worda_ns == wordb_ns:
        notes_diff_type = 'notes changed but word did not'
    else:
        notes_diff_type = 'notes changed and word changed'
    io_diff['notes differences'].append({
        'bcv': bcv,
        'notes_diff_type': notes_diff_type,
        'a_word': vyla['word'],
        'a_notes': notesa,
        'b_word': vylb['word'],
        'b_notes': notesb,
        'notes_change': notes_change,
        'notes_change_category': _NC_CATEGORIES[notes_change],
        **_set_differences(vyla['notes'], vylb['notes'])
    })


_NC_CATEGORIES = {
    # Below are categories of note changes on unchanged words.
    # nc: named category, i.e. not "other" (misc.)
    '∅ → ]1': 'nc + ]1',
    '∅ → ]1]P': 'nc + ]1',
    '∅ → ]c]p': 'nc + ]p',
    '∅ → ]e': 'nc + ]e',
    '∅ → ]p': 'nc + ]p',
    '∅ → ]Q]n]p': 'nc + ]p',
    '∅ → ]U': 'nc + ]U',
    '∅ → ]w': 'nc + ]w',
    ']1 → ∅': 'other ]1 → ∅',
    ']1 → ]C]U': 'nc .*]1.* → .*]U.*',
    ']1 → ]s': 'nc ]1 → ]s or ]U → ]S]s',
    ']1 → ]S]s': 'other ]1 → ]S]s',
    ']1 → ]U': 'nc .*]1.* → .*]U.*',
    ']1]a → ]U]a': 'nc .*]1.* → .*]U.*',
    ']c → ∅': 'other ]c → ∅',
    ']c → ]C]c': 'other ]c → ]C]c',
    ']c → ]C]P]c': 'other ]c → ]C]P]c',
    ']c]p → ]C]P]c]p': 'other ]c]p → ]C]P]c]p',
    ']k → ]Q]k': 'other ]k → ]Q]k',
    ']p → ]n]p': 'other ]p → ]n]p',
    ']q → ]Q]n]q': 'other ]q → ]Q]n]q',
    ']q → ]Q]q': 'other ]q → ]Q]q',
    ']Q]c → ]Q]c]e': 'nc + ]e',
    ']U → ]S]s': 'nc ]1 → ]s or ]U → ]S]s',
    ']v → ∅': 'other ]v → ∅',
    ']v → ]Q]v': 'other ]v → ]Q]v',
    #
    # Below are categories of note changes that appear only on changed words.
    '∅ → ]c': 'other ∅ → ]c',
    '∅ → ]C]c': 'other ∅ → ]C]c',
    '∅ → ]P]p': 'other ∅ → ]P]p',
    '∅ → ]Q]c': 'other ∅ → ]Q]c',
    '∅ → ]Q]c]n': 'other ∅ → ]Q]c]n',
    '∅ → ]Q]n]v': 'other ∅ → ]Q]n]v',
    '∅ → ]v': 'other ∅ → ]v',
    ']1 → ]Q]p': 'other ]1 → ]Q]p',
    ']1 → ]Q]U]v': 'other ]1 → ]Q]U]v',
    ']n]p → ∅': 'other ]n]p → ∅',
    ']p → ∅': 'other ]p → ∅',
    ']p → ]1': 'other ]p → ]1',
    ']P]p]v → ]Q]n]v': 'other ]P]p]v → ]Q]n]v',
}


def _set_differences(notesa, notesb):
    seta = set(notesa)
    setb = set(notesb)
    b_minus_a = setb - seta
    a_minus_b = seta - setb
    bma_sorted_list = sorted(list(b_minus_a))
    amb_sorted_list = sorted(list(a_minus_b))
    bma_str = ''.join(bma_sorted_list)
    amb_str = ''.join(amb_sorted_list)
    return {'b-a': bma_str, 'a-b': amb_str}


def _vyla_to_cells(vyla):
    return _vyl_to_cells(vyla, 'vela_type', 'vela_0', 'vela_1')


def _vylb_to_cells(vylb):
    return _vyl_to_cells(vylb, 'velb_type', 'velb_0', 'velb_1')


def _vyl_to_cells(vyl, typlbl, lbl0, lbl1):
    vyltype = _vyltype(vyl)
    if vyltype == _VYLTYPE_WN:
        datacells = vyl['word'], ''.join(vyl['notes'])
    elif vyltype == _VYLTYPE_PS:
        datacells = vyl['parasep'], ''
    elif vyltype == _VYLTYPE_NONE:
        datacells = '', ''
    else:
        assert False
    return {typlbl: vyltype, lbl0: datacells[0], lbl1: datacells[1]}



_VYLTYPE_NONE = 'vyltype-∅'
_VYLTYPE_WN = 'vyltype-wn'
_VYLTYPE_PS = 'vyltype-parasep'


def _vyltype(vyl):
    if vyl is None:
        return _VYLTYPE_NONE
    assert isinstance(vyl, dict)
    keys = tuple(vyl.keys())
    if keys == ('word', 'notes'):
        return _VYLTYPE_WN
    if keys == ('parasep',):
        return _VYLTYPE_PS
    assert False
