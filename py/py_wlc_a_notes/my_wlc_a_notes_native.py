"""Exports write_native_to_html."""

import py_html.my_html as my_html
import py_html.my_html_for_img as img


def write_to_html(native, record):
    """Write XML (represented as a native Python dict) to an HTML file."""
    rows = list(map(_make_key_value_row, native.items()))
    #
    body_contents = []
    if html_for_i := img.html_for_imgs(record):
        body_contents.extend(html_for_i)
    body_contents.append(my_html.table(rows, {"class": "limited-width"}))
    ucp_n = int(native["n"])
    ucp_n_str_02 = f"{ucp_n:02d}"
    title = f"UXLC change proposal {ucp_n}"
    path = f"ucp/uxlc_change_proposal_{ucp_n_str_02}.html"
    write_ctx = my_html.WriteCtx(title, f"gh-pages/wlc-a-notes/{path}")
    my_html.write_html_to_file(body_contents, write_ctx, "../../")
    return path


def _make_key_value_row(kv_pair):
    key, value = kv_pair
    cell_for_key = my_html.table_datum(key)
    if key in ("reftext", "changetext"):
        attr = {"lang": "hbo", "dir": "rtl"}
    else:
        attr = None
    cell_for_value = my_html.table_datum(value, attr)
    return my_html.table_row([cell_for_key, cell_for_value])
