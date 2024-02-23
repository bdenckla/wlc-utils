""" Exports ? """

def init():
    return {
        'parasep_foi': {'P': 0, 'S': 0},
        'notes_foi': {
            'counts': {},
            'cases': []
        },
    }


def sort_notes_foi(notes_foi):
    nfc = notes_foi['counts']
    nfc_sorted = dict(sorted(nfc.items()))
    notes_foi_out = {
        'notes': list(nfc_sorted.keys()),
        'counts': nfc_sorted,
        'cases': notes_foi['cases'],
    }
    return notes_foi_out


def collect_features_of_interest(io_fois, bcv, veldic):
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


def _is_parasep(veldic):
    return list(veldic.keys()) == ['parasep']
