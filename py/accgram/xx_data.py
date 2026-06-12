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
