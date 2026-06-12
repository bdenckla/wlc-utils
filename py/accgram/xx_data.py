from py_html import wlc_utils_html

# The FOI category shared by Nehemiah 8:7 and Daniel 3:2. Kept here, rather than
# privately in rtmsr_open_issues, so that both the Open Issues section and the
# ne 8:7 oddball comment can link to the very same FOI category page.
FOI_PAZ_CATEGORY_LINK = (
    "⅃-leg...non-revia ((paz)) with 0 intervening",
    "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB((paz))%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB0%C2%ABspace%C2%BBintervening",
)


def foi_paz_category_comment_item():
    """A comment item: intro text with the FOI ((paz)) category link underneath,
    matching how the Open Issues section presents that category."""
    label, href = FOI_PAZ_CATEGORY_LINK
    intro = wlc_utils_html.para(
        "Daniel 3:2 is the only other verse — in MAM at least, perhaps not in WLC —"
        " of this verse’s FOI category:",
        {"class": "goerwitz-tms-comment"},
    )
    link = wlc_utils_html.anchor(label, {"href": href})
    return wlc_utils_html.div((intro, wlc_utils_html.unordered_list((link,))))


def github_issue_comment_item(href):
    """A comment item pointing to a word’s GitHub issue, linked as “GitHub issue”
    just as the same issue is linked above the comment."""
    link = wlc_utils_html.anchor("GitHub issue", {"href": href})
    return wlc_utils_html.para(
        ("See the ", link, " regarding this word."),
        {"class": "goerwitz-tms-comment"},
    )


def non_revia_summary(accent: str, intro=None) -> str:
    return f"{intro or 'The'} checker probably doesn’t like munaḥ legarmeih serving {accent}."


def non_revia_comment(fp_value: str, extra=()):
    return (
        (
            "This verse is probably an oddball (i.e. it reports “ERROR”) because "
            f"it has a phrase that is a member of the FOI category “{fp_value}”. "
        ),
        (
            "This verse is one of 15 oddballs whose FOI category starts "
            "with “⅃-leg...non-revia”. Only 2 such verses — Daniel 3:2 and Ruth 1:2 — are not oddballs."
        ),
        (
            "Of the 17 verses in that category, only those 2 are not oddballs;"
            " all the rest, like this one, report the string “ERROR” (see oddballs)."
        ),
        *extra,
    )
