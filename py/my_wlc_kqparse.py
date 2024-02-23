import my_wlc_utils


def kqparse(parsed):
    kqparsed = {'verses': []}
    for verse in parsed['verses']:
        bcv = verse['bcv']
        kqverse = {'bcv': bcv, 'kqvels': []}
        kqparsed['verses'].append(kqverse)
        for velsod in verse['vels']:
            veldic = my_wlc_utils.velsod_to_veldic(velsod)
            kqvelsod = my_wlc_utils.veldic_to_velsod(veldic)
            kqverse['kqvels'].append(kqvelsod)
    return kqparsed
