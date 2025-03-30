""" Exports write. """

import py.my_open as my_open
import py.wlc_utils as wlc_utils
import py.wlc_uword as wlc_uword


def write(tdir, wlc_id, parsed):
    io_fois = _init()
    _flexcollect(io_fois, parsed, _collect)
    #
    io_fois["notes_foi"] = _sort_notes_foi(io_fois["notes_foi"])
    #
    _flexdump(io_fois, tdir, wlc_id)


def kqwrite(tdir, wlc_id, kqparsed):
    io_fois = _kqinit()
    _flexcollect(io_fois, kqparsed, _kqcollect)
    _flexdump(io_fois, tdir, wlc_id, "-kq")


def _flexcollect(io_fois, xparsed, xcollect):
    for verse in xparsed["verses"]:
        bcv = verse["bcv"]
        for velsod in verse["vels"]:
            xcollect(io_fois, bcv, velsod)


def _flexdump(fois, tdir, wlc_id, suffix=""):
    out_path = _flexpath(tdir, wlc_id, suffix)
    my_open.json_dump_to_file_path(fois, out_path)


def _flexpath(tdir, wlc_id, suffix=""):
    return f"{tdir}/out/{wlc_id}{suffix}_ps.fois.json"


def _init():
    return {
        "parasep_foi": {"P": 0, "S": 0, "N": 0},
        "notes_foi": {"counts": {}, "cases": []},
    }


def _kqinit():
    return {
        "kq_foi": {
            "counts": {
                "k1q1": 0,
                "k0q1": 0,
                "k1q0": 0,
                "k2q1": 0,
                "k1q2": 0,
                "k2q2": 0,
            },
            "cases": [],
        }
    }


def _sort_notes_foi(notes_foi):
    nfc = notes_foi["counts"]
    nfc_sorted = dict(sorted(nfc.items()))
    notes_foi_out = {
        "notes": list(nfc_sorted.keys()),
        "counts": nfc_sorted,
        "cases": notes_foi["cases"],
    }
    return notes_foi_out


def _collect(io_fois, bcv, velsod):
    if p_or_s := wlc_utils.get_parasep(velsod):
        parasep_foi = io_fois["parasep_foi"]
        parasep_foi[p_or_s] += 1
        return
    if notes := wlc_utils.get_notes(velsod):
        word = velsod["word"]
        counts, cases = _get_counts_and_cases(io_fois["notes_foi"])
        for note in notes:
            #
            if note not in counts:
                counts[note] = 0
            counts[note] += 1
            #
            notes_str = "".join(notes)
            case = {
                "note": note,
                "bcv": bcv,
                "uword": wlc_uword.uword(word),
                "word": word,
                "notes_str": notes_str,
            }
            cases.append(case)


def _kqcollect(io_fois, bcv, velsod):
    if ketiv_and_qere := wlc_utils.get_kq(velsod):
        ketiv_and_qere = velsod["kq"]
        lenk = len(ketiv_and_qere[0])
        lenq = len(ketiv_and_qere[1])
        knqm = f"k{lenk}q{lenq}"
        #
        counts, cases = _get_counts_and_cases(io_fois["kq_foi"])
        #
        counts[knqm] += 1
        if knqm != "k1q1":
            case = {"knqm": knqm, "bcv": bcv, **_k2q2_generic(ketiv_and_qere)}
            cases.append(case)


def _k2q2_generic(ketiv_and_qere):
    out = {"k1": None, "k2": None, "q1": None, "q2": None}
    kkeys = {0: "k1", 1: "k2"}
    for kidx, kvelsod in enumerate(ketiv_and_qere[0]):
        out[kkeys[kidx]] = _word(kvelsod)
    qkeys = {0: "q1", 1: "q2"}
    for qidx, qvelsod in enumerate(ketiv_and_qere[1]):
        out[qkeys[qidx]] = _word(qvelsod)
    return out


def _word(velsod):
    if isinstance(velsod, str):
        return velsod
    return velsod.get("word")


def _get_counts_and_cases(foi):
    return foi["counts"], foi["cases"]
