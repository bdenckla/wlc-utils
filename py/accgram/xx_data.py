def non_revia_summary(accent: str, intro = None) -> str:
    return f"{intro or 'The'} checker probably doesn’t like munaḥ legarmeih serving {accent}."


def non_revia_comment(fp_value: str, extra=()):
    return (
        (
            "This verse probably causes trouble for the Goerwitz accent grammar because "
            f"it has a phrase that is a member of the FOI category “{fp_value}”. "
        ),
        (
            "This verse is one of 5 troublemakers whose FOI category starts "
            "with “⅃-leg...non-revia”. There are 12 other such verses that do not cause trouble."
        ),
        (
            "It remains to be investigated whether all of those other 12,"
            " despite not causing trouble,"
            " are considered ungrammatical,"
            " i.e. report the string “ERROR”. Certainly many of them report “ERROR” (see oddballs)."
        ),
        *extra,
    )