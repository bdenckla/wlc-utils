import my_wlc_utils


def kqparse(parsed):
    kqparsed = {'header': parsed['header'], 'verses': []}
    stacks = _STACKS_INIT
    for verse in parsed['verses']:
        bcv = verse['bcv']
        kqverse = {'bcv': bcv, 'vels': []}
        kqparsed['verses'].append(kqverse)
        assert _stacks_are_clear(stacks)
        for velsod in verse['vels']:
            word = _word(velsod)
            if word and word.startswith('**'):
                _stacks_push(stacks, 'qere', velsod)
                continue
            if word and word.startswith('*'):
                if _stacks_has_qere(stacks):
                    _stacks_transfer(kqverse['vels'], stacks)
                _stacks_push(stacks, 'ketiv', velsod)
                continue
            _stacks_transfer(kqverse['vels'], stacks)
            kqverse['vels'].append(velsod)
        _stacks_transfer(kqverse['vels'], stacks)
    return kqparsed


_STACKS_INIT = {'ketiv': [], 'qere': []}


def _stacks_clear(io_stacks):
    io_stacks['ketiv'] = []
    io_stacks['qere'] = []


def _stacks_are_clear(stacks):
    return not stacks['ketiv'] and not stacks['qere']


def _stacks_has_qere(stacks):
    return stacks['qere']


def _stacks_push(io_stacks, k_or_q, val):
    io_stacks[k_or_q].append(val)


def _stacks_transfer(io_kqvels, io_stacks):
    ketiv_stack = io_stacks['ketiv']
    qere_stack = io_stacks['qere']
    if ketiv_stack and qere_stack:
        io_kqvels.append({'kq': (ketiv_stack, qere_stack)})
        _stacks_clear(io_stacks)
    else:
        assert _stacks_are_clear(io_stacks)


def _word(velsod):
    if isinstance(velsod, str):
        return velsod
    return velsod.get('word')
