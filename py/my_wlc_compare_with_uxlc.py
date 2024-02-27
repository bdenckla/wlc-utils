import my_uxlc
import my_convert_citation_from_wlc_to_uxlc as w2u
import my_uword
import my_wlc_utils
import my_uni_heb as uh


def compare(parsed_wlc):
    books_dir = '../wlc-utils-io/in/Tanach-26.0--UXLC-1.0--2020-04-01/Books'
    uxlc = my_uxlc.read_all_books(books_dir)
    parsed_wlc_422 = parsed_wlc['wlc420']
    misc = {'diffs': []}
    for wlc_verse in parsed_wlc_422['verses']:
        wlc_bcv = wlc_verse['bcv']
        wlc_comparables = _comparables(wlc_verse)
        uxlc_verse = _uxlc_verse(uxlc, wlc_bcv)
        assert len(wlc_comparables) == len(uxlc_verse)
        misc['wlc_bcv'] = wlc_bcv
        for wlc_str, uxlc_str in zip(wlc_comparables, uxlc_verse):
            _compare(misc, wlc_str, uxlc_str)
    _print_diffs(misc['diffs'])


def _uxlc_verse(uxlc, wlc_bcv):
    std_bkid, chnu, vrnu = w2u.get_std_bcv(wlc_bcv)
    return uxlc[std_bkid][chnu-1][vrnu-1]


def _comparables(wlc_verse):
    comparables = map(_comparable, wlc_verse['vels'])
    return list(filter(None, comparables))


def _comparable(wlc_velsod):
    if isinstance(wlc_velsod, dict):
        if my_wlc_utils.is_parasep(wlc_velsod):
            return None
        return _comparable(wlc_velsod['word'])
    wlc_str = wlc_velsod
    if wlc_str.startswith('*'):
        if wlc_str.startswith('**'):
            return None if wlc_str == '**qq' else wlc_str.removeprefix('**')
        return None
    return wlc_str


def _compare(io_misc, wlc_str, uxlc_str):
    uxlc_str = uxlc_str.replace('/', '').replace(' ', '')
    wlc_str_u = my_uword.uword(wlc_str)
    if wlc_str_u != uxlc_str:
        _record_diff(io_misc, wlc_str, wlc_str_u, uxlc_str)


def _print_diffs(diffs):
    num_diffs_to_print = min(len(diffs), 250)
    for diff in diffs[:num_diffs_to_print]:
        bcv, wlc_str, wlc_str_u, uxlc_vel = diff
        wlc_str_u_uh = uh.comma_shunnas(wlc_str_u)
        uxlc_vel_uh = uh.comma_shunnas(uxlc_vel)
        print(bcv)
        print(f'w: {wlc_str}')
        print(f'w: {wlc_str_u_uh}')
        print(f'u: {uxlc_vel_uh}')


def _record_diff(io_misc, *rest):
    io_misc['diffs'].append((io_misc['wlc_bcv'], *rest))
