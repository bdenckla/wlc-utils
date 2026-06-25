"""The "Masoretically-blessed oddities" section of the "almost errors" page.

Legitimate masoretic tradition the checker accepts (not charities), where its
only decision is one of representation.  Two exhibits, each backed by live parse
trees from ``almost_errors_trees``:

  * the **telisha gedola + geresh/gershayim** five-word exhibit, whose alternate-
    reading trees show that the checker's choice (keep both, as a telg-then-geresh
    sequence) is the most faithful of several grammatically-clean options; and
  * **Ezekiel 20:31's mahapakh + azla**, the only word in Tanakh with two
    conjunctive accents on one letter, where the verdict table shows the fusion
    is all but forced by the grammar.
"""

from __future__ import annotations

from accgram import almost_errors_trees as aet
from accgram import rtms_report
from accgram import rtmsr_media
from accgram.almost_errors_html_shared import (
    _accents_and_letters,
    _hbo,
    _link,
    _ref_display,
    _ref_short,
    _render_tree,
    _verse_links,
)
from accgram.ply_scanner import HasLegarmeh
from py_html import wlc_utils_html as H
from py_wlc import my_wlc_bcv_str

# The five WLC words carrying BOTH telisha gedola and a geresh-family mark -- the checker
# keeps both, reading them as a telg-then-geresh sequence.  (gn5:29 / zp2:15 same-letter;
# 2k17:13 same-letter with geresh muqdam; lv10:4 / ek48:10 cross-letter, same word.)
_TELG_EXHIBIT_REFS = ("gn5:29", "zp2:15", "2k17:13", "lv10:4", "ek48:10")

# The two verses whose full alternate-reading trees the exhibit draws: one same-letter
# (zp2:15), one cross-letter (lv10:4).  The other three get a verdict-table row only --
# their trees differ in the same place and would only repeat the lesson.
_TELG_TREE_REFS = ("zp2:15", "lv10:4")

_TELG_MODES = (
    ("keep_both", "keep both, as a telisha gedola then geresh sequence (what the checker does)"),
    ("keep_telg", "drop the geresh-family mark, keep the telisha gedola"),
    ("keep_gerstar", "drop the telisha gedola, keep the geresh-family mark"),
)

# The five ways to hand ek20:31's mahapakh + qadma pair to the grammar: the fused token
# the checker actually emits, plus the four alternatives (drop one mark, or keep both as
# a sequence in either order).  Only two parse cleanly: the fused token and the
# qadma-then-mahapakh sequence.
#
# The reason is the *three*-servus context, which is easy to miss.  This pashta (on the
# following word גִּלּוּלֵיכֶם) is served by three conjunctives: a telisha qetanna on the
# preceding word אַתֶּם, then the azla (qadma) and mahapakh that share ek20:31's alef.  Every
# pashta_phrase rule for a telisha-qetanna-headed chain puts AZLA directly after the
# TELISHAQETANNA -- TELISHAQETANNA AZLA MAHAPAKH PASHTA, or its one-token analogue
# TELISHAQETANNA MAHAPAKHAZLA PASHTA -- because the masoretic rule is that a telisha
# qetanna is *always* followed by azla (Yeivin #246).  So here azla is an obligatory
# bridge, not an optional mark:
#   fused          TELISHAQETANNA MAHAPAKHAZLA PASHTA  -> clean
#   seq_azla_mah   TELISHAQETANNA AZLA MAHAPAKH PASHTA -> clean (same reading, two letters)
#   drop_azla      TELISHAQETANNA MAHAPAKH PASHTA      -> no rule (mahapakh can't follow telq)
#   drop_mahapakh  TELISHAQETANNA AZLA PASHTA          -> no rule (azla needs mahapakh/merkha)
#   seq_mah_azla   TELISHAQETANNA MAHAPAKH AZLA PASHTA -> wrong order
# A *bare* MAHAPAKH PASHTA rule does exist (a one-servus pashta), so dropping the azla
# would parse if this pashta stood alone -- but it never does here, because the telisha
# qetanna makes the chain three deep.  The verdict table makes the clean/ERROR split
# visible.
_EK_MODES = (
    ("fused", "fuse into one mahapakh!azla token (what the checker does)"),
    ("drop_azla", "keep the mahapakh, drop the qadma"),
    ("drop_mahapakh", "keep the qadma, drop the mahapakh"),
    ("seq_azla_mah", "keep both, as a qadma then mahapakh sequence"),
    ("seq_mah_azla", "keep both, as a mahapakh then qadma sequence"),
)

# MAM's documentation note on ek20:31 (from MAM-parsed-plus / MAM-with-doc), the
# witness that ek20:31's double-marking is standard masoretic tradition, not an L
# anomaly.  Quoted (Hebrew) and paraphrased (English) on the page.
_EK2031_MAM_NOTE_HE = (
    "זאת התיבה היחידה בכל המקרא שיש בה שני טעמים מחברים בהברה אחת."
    " הקדמא קודמת למהפך בקריאה, כמו בעוד שש מקומות במקרא (שבהם הקדמא"
    " במקום הראוי לגעיה והמהפך בהברת הטעם), כגון: ויקרא כה,מו; במדבר [כ,א]."
)

# The six places (besides ek20:31) where a qadma sits in a syllable fit for a ga'ya and
# a mahapakh on the stressed syllable -- the pattern the MAM note above invokes.  The note
# names only the first two as examples (and miscites Num 20:1 as "21:1"); the other four
# are flagged ``supplied`` so the page can list them separately as our additions, not the
# note's.  (bb, chnu, vrnu, display, supplied)
_QADMA_GAYA_REFS = (
    ("lv", 25, 46, "Lev. 25:46", False),
    ("nu", 20, 1, "Num. 20:1", False),
    ("ek", 43, 11, "Ezek. 43:11", True),
    ("2c", 35, 25, "2 Chron. 35:25", True),
    ("da", 3, 2, "Dan. 3:2", True),
    ("er", 7, 24, "Ezra 7:24", True),
)


def _qadma_gaya_links(*, supplied: bool) -> tuple[object, ...]:
    """The qadma-as-ga'ya + mahapakh places as a ``; ``-joined run of MAM-with-doc links,
    filtered to either the two the MAM note names as examples (``supplied=False``) or the
    four supplied here (``supplied=True``)."""
    nodes: list[object] = []
    for bb, chnu, vrnu, display, is_supplied in _QADMA_GAYA_REFS:
        if is_supplied != supplied:
            continue
        if nodes:
            nodes.append("; ")
        nodes.append(_link(display, rtms_report.mam_with_doc_url(bb=bb, chnu=chnu, vrnu=vrnu)))
    return tuple(nodes)


def _oddities_intro() -> tuple[object, ...]:
    return (
        H.heading_level_2("Masoretically-blessed oddities (not charities)"),
        H.para(
            "The features below would make a naïve checker blink — two accents sharing"
            " one letter or one word — but"
            " none of them is a quirk of LC, BHS, or WLC to be forgiven. They are"
            " official masoretic tradition, attested in the standard witnesses. The"
            " checker accepts them; its only real decision is one of representation —"
            " whether to keep both marks as a sequence, fuse a pair into one token, or"
            " carry a single mark — and, as the telisha gedola exhibit shows, that"
            " decision is a choice among readings that all parse cleanly."
        ),
    )


def _telg_section(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    items: list[object] = [
        H.heading_level_3("telisha gedola + geresh/gershayim (five words)"),
        H.para(
            "Five WLC words carry both a telisha gedola and a geresh-family companion"
            " (a plain geresh or gershayim — or, in 2 Kings 17:13, a geresh that the"
            " geresh muqdam charity above produced). This double-marking is not a quirk"
            " to forgive: it is official masoretic tradition, attested in the standard"
            " witnesses. The checker keeps both marks. The grammar — which constrains what"
            " sequences of accents are well-formed — admits a telisha gedola alongside a"
            " geresh (the pairing occurs about 165 times across separate words, so it parses"
            " cleanly). In three of the words the two marks sit on one base letter (Genesis"
            " 5:29, Zephaniah 2:15, and 2 Kings 17:13); there the same-letter pair is"
            " whitelisted — the prose analogue of the poetic deḥi + munaḥ entry, a"
            " legitimate same-letter pair kept as a sequence rather than fused — instead of"
            " being flagged. The other two words (Leviticus 10:4, Ezekiel 48:10) carry their"
            " two marks on two letters, so no same-letter question arises."
        ),
        H.para(
            "Keeping both is a choice, not a forced move: each verse also parses cleanly"
            " if either mark is dropped instead. We keep both simply because that is the"
            " reading that preserves everything the manuscript wrote — dropping either mark"
            " would discard a real masoretic accent. The checker happens to present the two"
            " accents telisha gedola first, then geresh, but nothing rides on that order: it"
            " is an artifact of how the marks are written, not a statement about which is"
            " chanted first, and the grammar accepts the reverse order just as readily —"
            " across the corpus a big telisha freely precedes or follows a geresh. The table"
            " below shows, for each word, the real WLC form (both marks, post-charity)"
            " alongside the two single-mark forms those alternate readings would use; whether"
            " the two marks share a letter is noted in the last column."
        ),
        _telg_forms_table(index),
        H.para(
            "So the choice is not forced by grammaticality — all three readings parse"
            " cleanly — but only keeping both preserves both accents the manuscript wrote."
            " The two verses below show the checker's actual parse tree (one same-letter"
            " case, one cross-letter)."
        ),
    ]
    for bcv in _TELG_TREE_REFS:
        items.append(H.htel_mk("h4", None, _ref_display(bcv)))
        items.append(_verse_links(bcv))
        items.append(_render_tree(aet._telg_tree_text(bcv, "keep_both", index, parser, has_legarmeh)))
    items.append(
        H.para(
            (
                "A note on the trees above: the same-letter words (here Zephaniah 2:15)"
                " appear exactly like the cross-letter ones — the two accents are kept"
                " distinct, a telisha gedola followed by a geresh, never merged into a"
                " single unit, whether or not they share a letter. That is the contrast"
                " with Ezekiel 20:31 below, whose two accents do merge.",
            )
        )
    )
    return tuple(items)


def _telg_forms_table(index) -> object:
    """One row per telg-exhibit word: the real WLC word (both marks, post-charity), the two
    single-mark Hebrew forms the alternate (drop-one) readings would use, and whether the
    two marks share a base letter.  No parse verdict: every reading parses cleanly, as the
    trees below show, so the forms themselves are the point."""
    header = H.table_row_of_headers(
        ("verse", "word", "telg", "gerstar", "same letter?")
    )
    rows: list[object] = [header]
    # The reference and the same-letter flag are LTR; the three word forms are RTL Hebrew.
    tdattrs = (None, *(({"dir": "rtl"},) * 3), None)
    for bcv in _TELG_EXHIBIT_REFS:
        forms = aet._telg_word_forms(aet._telg_gerstar_word(index[bcv]))
        keep_telg = _accents_and_letters(forms.keep_telg)
        keep_gerstar = _accents_and_letters(forms.keep_gerstar)
        rows.append(
            H.table_row_of_data(
                (
                    H.anchor(
                        _ref_short(bcv),
                        {"href": my_wlc_bcv_str.get_tanach_dot_us_url(bcv)},
                    ),
                    _hbo(forms.word),
                    _hbo(keep_telg),
                    _hbo(keep_gerstar),
                    "yes" if forms.same_letter else "no",
                ),
                tdattrs,
            )
        )
    return H.table(tuple(rows), {"class": "limited-width"})


def _ek_verdict_table(index, parser, has_legarmeh: HasLegarmeh) -> object:
    """One row per ek20:31 reading (``_EK_MODES``): the reading and its parse verdict."""
    rows: list[object] = [H.table_row_of_headers(("reading", "verdict"))]
    for mode, label in _EK_MODES:
        verdict = aet._ek_verdict_for(mode, index, parser, has_legarmeh)
        rows.append(H.table_row_of_data((label, verdict)))
    return H.table(tuple(rows), {"class": "limited-width"})


def _ek2031_section(index, parser, has_legarmeh: HasLegarmeh) -> tuple[object, ...]:
    tree_text = aet._prose_verse_tree_text("ek20:31", index, parser, has_legarmeh)
    return (
        H.heading_level_3("Mahapakh + azla (Ezekiel 20:31)"),
        _verse_links("ek20:31"),
        H.para(
            (
                "In Ezekiel 20:31, ",
                _hbo("נִטְמְאִ֤֨ים"),
                " carries both a mahapakh and a qadma on its"
                " alef. It is the only word in"
                " Tanakh with two conjunctive accents on one letter. The"
                " checker accepts it outright: the scanner fuses the pair into one ",
                H.code("mahapakh!azla"),
                " token, which the grammar parses as an ordinary accent. As with the"
                " telisha gedola words, both marks survive; only the representation"
                " differs. The telisha gedola and its geresh are two disjunctives, which"
                " the grammar admits as a two-accent sequence, so the checker keeps them as"
                " a sequence; the mahapakh and qadma are two conjunctives sharing one"
                " letter, which the scanner instead fuses into a single token. Either way"
                " both marks survive — the difference is sequence versus fused token. The"
                " two conjunctives do have a reading order — qadma before mahapakh, as the"
                " MAM note below stresses — but the fused token does not try to encode it.",
            )
        ),
        H.para(
            (
                "That this double accent is intentional in the LC is"
                " supported by the word’s masorah qetannah note,"
                " ל̇ בטע̇" # we purposely don't format this as hbo because Taamey D doesn't support "combining dot above" well
                " (“[this is the] one [word in all Tanakh that appears] with [these]"
                " accents [arranged like this]”):",
            )
        ),
        *rtmsr_media.render_image_paragraphs(
            {"img": "LC-286A-col-3-line-21-Ezek-20v31.png"},
            structured_text_lookup=lambda row, key: row.get(key),
        ),
        H.para(
            (
                "MAM has this double accent,"
                " and has a documentation note citing support for it from"
                " three standard witnesses (Aleppo, Leningrad, Cairo) and their masorot."
                " MAM also cites Yeivin 28.1 p. 232."
                " MAM spells out why this double accent is puzzling yet standard:",
            )
        ),
        H.blockquote(_EK2031_MAM_NOTE_HE, {"dir": "rtl"}),
        H.blockquote(
            (
                "This is the only word in all of Tanakh with two conjunctive accents on one letter;"
                " the qadma precedes the mahapakh in chanting,"
                " as in six other places where [(on a single word)]"
                " a qadma occupies a syllable fit for a ga‘ya"
                " and a mahapakh occupies the stressed syllable, for example: ",
                *_qadma_gaya_links(supplied=False),
                ".",
            )
        ),
        H.para(
            (
                "The note names only those two as examples — and writes"
                " “Num. 21:1” where it means Num. 20:1. The other four verses alluded to"
                " above are as follows, making six total: ",
                *_qadma_gaya_links(supplied=True),
                ". See the full note on the ",
                _link(
                    "MAM-with-doc Ezekiel page",
                    "https://bdenckla.github.io/MAM-with-doc/C3-Ezekiel.html#c20v31",
                ),
                ". Because the witnesses agree, this double accent is whitelisted"
                " rather than treated an error.",
            )
        ),
        H.para(
            (
                "The instructive contrast is Lev. 25:20, the ",
                H.bold("only other"),
                " prose word with two accents on one letter (a mahapakh and a tipeḥa)."
                " There the witnesses do ",
                H.bold("not"),
                " agree — MAM keeps only the tipeḥa and WLC tags the word anomalous —"
                " so it may well be an error in the LC, and the checker flags it (as a"
                " lexical error). Same surface shape, opposite verdict, decided by the"
                " witnesses. Its full treatment is on the ",
                _link("Goerwitz page", "goerwitz.html#oblv25v20"),
                ". The poetic ",
                H.code("merkha!azla"),
                " of Psalms 56:10 is the same story on the poetic side: the double accent in the LC has no"
                " support from other manuscripts, so it, like Lev. 25:20, is flagged as an error.",
            )
        ),
        H.para(
            (
                "How forced is the fusion? Unlike the telisha gedola readings above — where"
                " every alternative parses cleanly and the choice is one of faithfulness —"
                " here the grammar all but dictates it. The table below runs the verse through"
                " the real checker under each of the five ways to present the pair: the"
                " fused token, dropping either mark, and keeping both as a sequence in"
                " either order. Only two parse: the fused ",
                H.code("mahapakh!azla"),
                " token and the qadma-then-mahapakh sequence — and those coincide,"
                " because the same pashta phrase rule that accepts the fused cluster also"
                " accepts the cross-letter ",
                H.code("azla mahapakh"),
                " pair, in exactly the reading order the MAM note describes (qadma before"
                " mahapakh).",
            )
        ),
        H.para(
            (
                "Why the other three readings fail is worth spelling out, because it is"
                " not merely that “a word needs an accent.” The pashta here is served by"
                " three conjunctives: a telisha qetanna on the preceding word ",
                _hbo("אַתֶּם"),
                ", then the qadma and mahapakh sharing this word’s alef. Once a"
                " telisha qetanna heads the chain, the grammar admits only ",
                H.code("telisha-qetanna azla mahapakh pashta"),
                " (or its one-token analogue ",
                H.code("telisha-qetanna mahapakh!azla pashta"),
                ") — the azla is obligatory, because the masoretic rule (Yeivin §246) is"
                " that a telisha qetanna is always followed by azla. So ",
                H.bold("keep the mahapakh, drop the qadma"),
                " leaves a telisha qetanna directly before a bare mahapakh — a sequence"
                " the tradition never produces and the grammar has no rule for — and the"
                " parse falls into error recovery (verdict ERROR, not even a clean"
                " non-parse). Dropping the mahapakh instead leaves an azla with nothing"
                " between it and the pashta, also unruled (azla must be followed by"
                " mahapakh or merkha); and the mahapakh-then-qadma order is simply"
                " backwards. A bare ",
                H.code("mahapakh pashta"),
                " is a perfectly legal one-servus pashta elsewhere, so dropping the qadma"
                " would parse if this pashta stood alone — but it does not, because the"
                " telisha qetanna makes the chain three deep.",
            )
        ),
        _ek_verdict_table(index, parser, has_legarmeh),
        H.para(
            "The checker’s parse tree for the verse, with the fused token shown as"
            " mahapakh!azla:"
        ),
        _render_tree(tree_text),
    )
