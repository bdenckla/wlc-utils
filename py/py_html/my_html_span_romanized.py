import py_html.my_html as my_html


def rmn(string):
    return my_html.span(string, {"class": "romanized"})
