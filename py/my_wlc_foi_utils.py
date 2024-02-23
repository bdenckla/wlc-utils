""" Exports write. """

import my_open
import my_wlc_utils


def write(tdir, wlc_id, parsed):
    #
    io_fois = _init()
    for verse in parsed['verses']:
        bcv = verse['bcv']
        for velsod in verse['vels']:
            _collect(io_fois, bcv, velsod)
    io_fois['notes_foi'] = _sort_notes_foi(io_fois['notes_foi'])
    #
    out_path = f'{tdir}/out/{wlc_id}/{wlc_id}_ps.fois.json'
    my_open.json_dump_to_file_path(io_fois, out_path)


def _init():
    return {
        'parasep_foi': {'P': 0, 'S': 0},
        'notes_foi': {
            'counts': {},
            'cases': []
        },
    }


def _sort_notes_foi(notes_foi):
    nfc = notes_foi['counts']
    nfc_sorted = dict(sorted(nfc.items()))
    notes_foi_out = {
        'notes': list(nfc_sorted.keys()),
        'counts': nfc_sorted,
        'cases': notes_foi['cases'],
    }
    return notes_foi_out


def _collect(io_fois, bcv, velsod):
    veldic = my_wlc_utils.velsod_to_veldic(velsod)
    if my_wlc_utils.is_parasep(veldic):
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
