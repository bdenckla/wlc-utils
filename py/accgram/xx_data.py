from py_html import wlc_utils_html

# The FOI category shared by Nehemiah 8:7 and Daniel 3:2. Kept here, rather than
# privately in rtmsr_open_issues, so the Open Issues section can link to the FOI
# category page. (The ne 8:7 oddball comment that once also linked here is gone:
# ne 8:7 no longer parses to ERROR now that has_legarmeh fires for all 17
# passages -- see doc/PLAN-fix-has-legarmeh-booknames.md.)
FOI_PAZ_CATEGORY_LINK = (
    "⅃-leg...non-revia ((paz)) with 0 intervening",
    "https://bdenckla.github.io/MAM-with-doc/foi/foi-pasoleg-1.html#intro-%E2%85%83-leg...non-revia%C2%ABspace%C2%BB((paz))%C2%ABspace%C2%BBwith%C2%ABspace%C2%BB0%C2%ABspace%C2%BBintervening",
)


def github_issue_comment_item(href):
    """A comment item pointing to a word’s GitHub issue, linked as “GitHub issue”
    just as the same issue is linked above the comment."""
    link = wlc_utils_html.anchor("GitHub issue", {"href": href})
    return wlc_utils_html.para(
        ("See the ", link, " regarding this word."),
        {"class": "goerwitz-tms-comment"},
    )
