import my_uxlc
import my_convert_citation_from_wlc_to_uxlc as w2u
import my_uword
import my_wlc_utils
import my_uni_heb as uh


def compare(parsed_wlc):
    books_dir = '../wlc-utils-io/in/Tanach-26.0--UXLC-1.0--2020-04-01/Books'
    uxlc = my_uxlc.read_all_books(books_dir)
    parsed_wlc_422 = parsed_wlc['wlc420']
    diff_count = 0; max_diff_count = 25
    for wlc_verse in parsed_wlc_422['verses']:
        std_bkid, chnu, vrnu = w2u.get_std_bcv(wlc_verse['bcv'])
        uxlc_verse = uxlc[std_bkid][chnu-1][vrnu-1]
        uxlc_velidx = 0
        for wlc_velsod in wlc_verse['vels']:
            if isinstance(wlc_velsod, dict):
                if my_wlc_utils.is_parasep(wlc_velsod):
                    continue
                wlc_str = wlc_velsod['word']
            else:
                wlc_str = wlc_velsod
            if wlc_str.startswith('*'):
                if wlc_str.startswith('**'):
                    wlc_str = wlc_str.removeprefix('**')
                else:
                    continue
            uxlc_vel = uxlc_verse[uxlc_velidx].replace('/', '').replace(' ', '')
            wlc_str_u = my_uword.uword(wlc_str)
            if wlc_str_u != uxlc_vel:
                wlc_str_u_uh = uh.comma_shunnas(wlc_str_u)
                uxlc_vel_uh = uh.comma_shunnas(uxlc_vel)
                if diff_count <= max_diff_count:
                    print(wlc_verse['bcv'])
                    print(f'w: {wlc_str}')
                    print(f'w: {wlc_str_u_uh}')
                    print(f'u: {uxlc_vel_uh}')
                    diff_count += 1
            uxlc_velidx += 1
