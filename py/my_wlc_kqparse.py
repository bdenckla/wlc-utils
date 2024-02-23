import my_wlc_utils


def kqparse(parsed):
    kqparsed = {'verses': []}
    ketiv_stack = []
    qere_stack = []
    for verse in parsed['verses']:
        bcv = verse['bcv']
        kqverse = {'bcv': bcv, 'kqvels': []}
        kqparsed['verses'].append(kqverse)
        assert not ketiv_stack
        assert not qere_stack
        for velsod in verse['vels']:
            word = _word(velsod)
            if word and word.startswith('**'):
                qere_stack.append(word)
                continue
            if word and word.startswith('*'):
                ketiv_stack.append(word)
                continue
            _complete(kqverse['kqvels'], ketiv_stack, qere_stack)
            ketiv_stack = []
            qere_stack = []
            kqverse['kqvels'].append(velsod)
        _complete(kqverse['kqvels'], ketiv_stack, qere_stack)
        ketiv_stack = []
        qere_stack = []
    return kqparsed


def _complete(io_kqvels, ketiv_stack, qere_stack):
    if ketiv_stack and qere_stack:
        io_kqvels.append({'kq': (ketiv_stack, qere_stack)})
    else:
        assert not ketiv_stack and not qere_stack



def _word(velsod):
    if isinstance(velsod, str):
        return velsod
    return velsod.get('word')
