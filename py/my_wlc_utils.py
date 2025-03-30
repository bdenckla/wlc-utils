def velsod_to_veldic(velsod):
    if isinstance(velsod, str):
        return {"word": velsod, "notes": []}
    return velsod


def veldic_to_velsod(veldic):
    # vel as dict always (veldic) to vel as a string or a dict (velsod)
    if is_parasep(veldic):
        return veldic
    wn_dic = veldic
    if not wn_dic["notes"]:
        return wn_dic["word"]
    return wn_dic


def is_parasep(veldic):
    return list(veldic.keys()) == ["parasep"]


def get_parasep(velsod):
    return isinstance(velsod, dict) and velsod.get("parasep")


def get_notes(velsod):
    return isinstance(velsod, dict) and velsod.get("notes")


def get_kq(velsod):
    return isinstance(velsod, dict) and velsod.get("kq")
