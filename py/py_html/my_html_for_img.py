"""Exports img_html."""

import py_html.wlc_utils_html as wlc_utils_html
import mb_cmn.my_utils as my_utils


def html_for_imgs(record, *, img_para_attr=None):
    """Return HTML for image or images in record."""
    if "img" in record:
        return [html_for_single_img(record["img"], img_para_attr=img_para_attr)]
    if "imgs" in record:
        imgs_items = record["imgs"].items()
        list_of_lists = [
            _html_for_imgs_item(imgs_item, img_para_attr=img_para_attr)
            for imgs_item in imgs_items
        ]
        return my_utils.sum_of_seqs(list_of_lists)
    return []


def html_for_single_img(img_path, *, img_para_attr=None):
    img_element = wlc_utils_html.img({"src": f"../img/{img_path}"})
    return wlc_utils_html.para(img_element, img_para_attr)


def _html_for_imgs_item(imgs_item, *, img_para_attr=None):
    img_label, img_path = imgs_item
    return [
        wlc_utils_html.para(img_label),
        html_for_single_img(img_path, img_para_attr=img_para_attr),
    ]
