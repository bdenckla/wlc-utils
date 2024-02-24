""" Exports write. """

import my_open
import my_wlc_utils


def write(tdir, wlc_id, parsed):
    io_fois = _init()
    _flexcollect(io_fois, parsed, _collect)
    #
    io_fois['notes_foi'] = _sort_notes_foi(io_fois['notes_foi'])
    #
    _flexdump(io_fois, tdir, wlc_id)


def kqwrite(tdir, wlc_id, kqparsed):
    io_fois = _kqinit()
    _flexcollect(io_fois, kqparsed, _kqcollect)
    _flexdump(io_fois, tdir, wlc_id, '-kq')


def _flexcollect(io_fois, xparsed, xcollect):
    for verse in xparsed['verses']:
        bcv = verse['bcv']
        for velsod in verse['vels']:
            xcollect(io_fois, bcv, velsod)


def _flexdump(fois, tdir, wlc_id, suffix=''):
    out_path = _flexpath(tdir, wlc_id, '-kq')
    my_open.json_dump_to_file_path(fois, out_path)


def _flexpath(tdir, wlc_id, suffix=''):
    return f'{tdir}/out/{wlc_id}{suffix}/{wlc_id}_ps.fois.json'


def _init():
    return {
        'parasep_foi': {'P': 0, 'S': 0},
        'notes_foi': {
            'counts': {},
            'cases': []
        },
    }


def _kqinit():
    return {
        'kq_foi': {'k1q1': 0, 'k0q1': 0, 'k1q0': 0, 'k2q1': 0, 'k1q2': 0, 'k2q2': 0},
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
    if p_or_s := my_wlc_utils.get_parasep(velsod):
        parasep_foi = io_fois['parasep_foi']
        parasep_foi[p_or_s] += 1
        return
    if notes := my_wlc_utils.get_notes(velsod):
        word = velsod['word']
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


def _kqcollect(io_fois, _bcv, velsod):
    if ketiv_and_qere := my_wlc_utils.get_kq(velsod):
        ketiv_and_qere = velsod['kq']
        lenk = len(ketiv_and_qere[0])
        lenq = len(ketiv_and_qere[1])
        knqm_key = f'k{lenk}q{lenq}'
        io_fois['kq_foi'][knqm_key] += 1


def _get_counts_and_cases(io_fois, note):
    notes_foi = io_fois['notes_foi']
    counts = notes_foi['counts']
    cases = notes_foi['cases']
    return counts, cases
