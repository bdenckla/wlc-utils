import my_wlc_utils


def kqparse(parsed):
    for verse in parsed['body']:
        bcv = verse['bcv']
        for velsod in verse['vels']:
            kqvelsod = _kqvelsod(velsod)


def _kqvelsod(velsod):
    veldic = my_wlc_utils.velsod_to_veldic(velsod)
    return my_wlc_utils.veldic_to_velsod(veldic)
