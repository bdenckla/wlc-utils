""" Exports read_and_parse. """

import re
import py.wlc_utils as wlc_utils
import py.hebrew_punctuation as hpu


def read_and_parse(tdir, wlc_id, filename):
    in_path = f"{tdir}/in/{wlc_id}/{filename}"
    parsed = {"header": [], "verses": []}
    with open(in_path, encoding="utf-8", newline="") as wlc_in_fp:
        for rawline in wlc_in_fp:
            line = rawline.rstrip()
            if line.startswith("#"):
                assert not parsed["verses"]
                parsed["header"].append(line)
            else:
                parsed_verse_line = _parse_verse_line(line)
                parsed["verses"].append(parsed_verse_line)
    return parsed


def _parse_verse_line(verse_line):
    verse_line_2 = verse_line.translate(_DROP_DIRECTIONAL_MARKS_AND_SLASH)
    #
    stages = []
    stages.append(re.split(_SPLIT_PATT, verse_line_2))
    stages.append(list(filter(_is_not_space, stages[-1])))
    stages.append(_recapture_maqaf_and_pasoleg(stages[-1]))
    stages.append(_recapture_note(stages[-1]))
    #
    bcv, atoms = stages[-1][0], stages[-1][1:]
    return _parse_atoms(bcv, atoms)


def _parse_atoms(bcv, atoms_4):
    veldics = list(map(_atom_to_veldic, atoms_4))
    velsods = list(map(wlc_utils.veldic_to_velsod, veldics))
    return {"bcv": bcv, "vels": velsods}


def _is_not_space(string):
    return string != " "


def _recapture_maqaf_and_pasoleg(atoms):
    out = []
    for atom in atoms:
        if atom in ("", hpu.MAQ, hpu.PASOLEG):
            # The empty string ("") results from maqaf followed by space.
            # This only happens in 2k23:10:
            # אאא *בני־ **בֶנ־הִנֹּ֑ם
            # (ignore אאא)
            out[-1] += atom
        else:
            out.append(atom)
    return out


def _recapture_note(atoms):
    # A note accidentally joins the next atom if the note follows a maqaf.
    # This only happens in je5:7:
    # אאא *אסלוח[1]־**אֶֽסְלַֽח־[י]לָ֔/ךְ
    # (ignore אאא)
    # (substitute [y] for [י])
    out = []
    for atom in atoms:
        if atom[0] == "[":
            assert atom[2] == "]"
            out[-1] += atom[0:3]
            out.append(atom[3:])
        else:
            out.append(atom)
    return out


_SPMQ = " " + hpu.MAQ
_SPLIT_PATT = f"([{_SPMQ}])"  # "([ab])"
_DROP_DIRECTIONAL_MARKS_AND_SLASH = str.maketrans(
    {
        "\N{RIGHT-TO-LEFT MARK}": "",  # U+200F
        "\N{LEFT-TO-RIGHT ISOLATE}": "",  # U+2066
        "\N{POP DIRECTIONAL ISOLATE}": "",  # U+2069
        "/": "",
    }
)


def _validate_veldic(veldic):
    if wlc_utils.is_sam_pe_inun(veldic):
        return
    wn_dic = veldic
    word = wn_dic["word"]
    assert "[" not in word
    assert "]" not in word


def _atom_to_veldic(word1):
    word2 = _KK_QQ_REMAPS.get(word1) or word1
    stage1 = {"word": word2, "notes": []}
    stage2 = _extract_notes(stage1)
    stage3 = _distinguish_sam_pe_inun(stage2)
    _validate_veldic(stage3)
    return stage3


def _extract_notes(wn_dic):
    # wn_dic: dict with keys "word" and "notes"
    word = wn_dic["word"]
    if match := re.fullmatch(r"(.*)\[(.*)\](.*)", word):
        main, raw_notes, post = match.groups()
        assert post in ("", hpu.MAQ, hpu.PASOLEG)
        new_word = main + post
        notes = _classic_bracketing(raw_notes)
        return {"word": new_word, "notes": notes}
    return wn_dic


def _classic_bracketing(raw_notes):
    return list(map(lambda x: f"]{x}", raw_notes))


def _distinguish_sam_pe_inun(wn_dic):
    # wn_dic: dict with keys "word" and "notes"
    word = wn_dic["word"]
    if word in ("פ", "ס"):
        assert not wn_dic["notes"]
        return {"sam_pe_inun": _SAMPE_REMAP[word]}
    if word == hpu.NUN_HAF:
        assert wn_dic["notes"] == ["]8"]
        return {"sam_pe_inun": "N"}
    return wn_dic


_SAMPE_REMAP = {"פ": "P", "ס": "S"}
_KK_QQ_REMAPS = {"*": "*kk", "**": "**qq"}
