"""Exports img_html."""

import py_html.wlc_utils_html as wlc_utils_html
import mb_cmn.my_utils as my_utils

# Default location of images relative to the page being generated.  Pages that sit
# one level below their sub-folder root (e.g. gh-pages/420422/full-record/*, the
# wlc-a-notes pages) resolve this to their own sub-folder's img/ dir and so keep the
# default.  Pages that sit directly in their sub-folder (the accgram pages) pass
# img_base="img/" so they reference their own accgram/img/ dir rather than escaping
# up to the top-level gh-pages/img/.
_DEFAULT_IMG_BASE = "../img/"


def html_for_imgs(record, *, img_para_attr=None, img_base=_DEFAULT_IMG_BASE):
    """Return HTML for image or images in record."""
    if "img" in record:
        return [
            html_for_single_img(
                record["img"], img_para_attr=img_para_attr, img_base=img_base
            )
        ]
    if "imgs" in record:
        imgs_items = record["imgs"].items()
        list_of_lists = [
            _html_for_imgs_item(
                imgs_item, img_para_attr=img_para_attr, img_base=img_base
            )
            for imgs_item in imgs_items
        ]
        return my_utils.sum_of_seqs(list_of_lists)
    return []


def html_for_single_img(img_path, *, img_para_attr=None, img_base=_DEFAULT_IMG_BASE):
    img_element = wlc_utils_html.img({"src": f"{img_base}{img_path}"})
    return wlc_utils_html.para(img_element, img_para_attr)


def _html_for_imgs_item(imgs_item, *, img_para_attr=None, img_base=_DEFAULT_IMG_BASE):
    img_label, img_path = imgs_item
    return [
        wlc_utils_html.para(img_label),
        html_for_single_img(img_path, img_para_attr=img_para_attr, img_base=img_base),
    ]
