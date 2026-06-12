"""Per-oddball structured research notes used by oddball HTML output."""

from __future__ import annotations

from accgram import xx_data


def get_structured_text() -> dict[str, dict[str, object]]:
    return STRUCTURED_TEXT_BY_REF


_SOMEWHERE = "Somewhere in the LC-BHS-WLC pipeline, $wlc_focus_desc appears rather than $diff_wlc_mam_desc."
_BHS_TRANSCRIBES = "BHS transcribes a $diff_wlc_mam_desc as a $wlc_focus_desc."
_ZARQA_WHIM = {
    "st-summary": "WLC turns a scribal zarqa whim into an outright error.",
    "other-goerwitz-item": "goerwitz.html#obnu20v19",
    "comment": (
        "This is one of seven items of this type."
        " See the “Other Goerwitz item” link regarding another instance (Nu 20:19)."
    ),
}
STRUCTURED_TEXT_BY_REF: dict[str, dict[str, object]] = {
    "gn 28:9": {
        "wlc_focus": "אברה֜ם",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "gn 32:24": {
        "wlc_focus": "לו׃",
        "st-summary": _SOMEWHERE,
        "comment": (
            "There is also a question of ויקח֔ם vs וי֨קח֔ם (metigah) in this verse, but either option is grammatical."
        ),
    },
    "ex 4:10": {
        "wlc_focus": "דברך",
        "st-summary": "The LC lacks an accent on this word.",
        "uxlc_change": "https://tanach.us/Changes/2021.10.19%20-%20Changes/2021.10.19%20-%20Changes.xml?2021.08.07-4",
    },
    "ex 6:6": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-2",
        **_ZARQA_WHIM,
    },
    "ex 28:1": {
        "wlc_focus": "את֔ו",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2022.04.01%20-%20Changes/2022.04.01%20-%20Changes.xml?2021.11.28-2",
        "comment": ("This is the example given in Goerwitz’s article."),
    },
    "ex 30:12": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-3",
        **_ZARQA_WHIM,
    },
    "ex 38:12": {
        "wlc_focus": "עמודיה֥ם",
        "st-summary": "The LC has something like a merkha where a munaḥ is expected.",
        "img": "LC-055A-col-1-line-3-Ex-38v12.png",
    },
    "lv 4:2": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-5",
        **_ZARQA_WHIM,
    },
    "lv 10:6": {
        "wlc_focus": "תפר֙מו֙ ",
        "st-summary": xx_data.non_revia_summary("pashta"),
    },
    "lv 21:10": {
        "wlc_focus": "המשחה֙",
        "st-summary": xx_data.non_revia_summary("pashta"),
    },
    "lv 25:20": {
        "wlc_focus": "נאכ֤֖ל",
        "st-summary": "The LC has a mahapakh in addition to the expected tipeḥa.",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.22-2",
    },
    "lv 26:28": {
        "wlc_focus": "חטאתיכם׃",
        "st-summary": _SOMEWHERE,
    },
    "nu 27:9": {
        "wlc_focus": "לאחיו׃",
        "st-summary": _SOMEWHERE,
    },
    "dt 10:15": {
        "wlc_focus": "הזה׃",
        "st-summary": _SOMEWHERE,
    },
    "dt 12:2": {
        "wlc_focus": "רענן׃",
        "st-summary": _SOMEWHERE,
    },
    "dt 23:18": {
        "wlc_focus": "ישראל׃",
        "st-summary": _SOMEWHERE,
    },
    "dt 24:10": {
        "wlc_focus": "ברעך",
        "st-summary": "The LC has only meteg where meteg-tipeḥa is expected.",
        "img": "LC-113A-col-3-line-27-Dt-24v10.png",
        "comment": (
            [
                "We could also interpret the LC’s mark under the resh as a tipeḥa that comes unexpectedly early in the word."
            ],
            [
                "We could also speculate that what seems to be the long descender of the final kaf"
                " includes a tipeḥa placed too early relative to the kaf."
            ],
            [
                "Yet, just as I have criticized some transcriptions as aggresively uncharitable,"
                " there is no doubt such a thing as a transcription that is too aggressively charitable,"
                " and these suggestions above,"
                " i.e. these ways of saving the word from violating the accent grammar,"
                " may be examples of that."
            ],
            [
                "The most likely explanation is that the LC simply does not have the expected tipeḥa anywhere in the word."
            ]
        ),
    },
    "dt 31:7": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-9",
        **_ZARQA_WHIM,
    },
    "js 4:8": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-10",
        **_ZARQA_WHIM,
    },
    "js 10:30": {
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "https://tanach.us/Changes/2021.04.01%20-%20Changes/2021.04.01%20-%20Changes.xml?2020.12.06-11",
        **_ZARQA_WHIM,
    },
    "js 15:47": {
        "wlc_focus": "עז֥ה",
        "st-summary": "The LC has merkha where tevir is expected.",
        "img": "LC-130B-col-1-line-16-Jo-15v47.png",
    },
    "ju 1:2": {
        "wlc_focus": "וי֣אמר",
        "st-summary": "The LC has munaḥ where a merkha is expected.",
        "img": "LC-136A-col-1-line-7-Ju-1v2.png",
    },
    "ju 11:24": {
        "wlc_focus": "אות֥ו תיר֑ש",
        "st-summary": "BHS transcribes a faded, ambiguous mark as merkha rather than munaḥ.",
        "img": "LC-144A-col-1-line-17-Ju-11v24.png",
        "edited img": "LC-144A-col-1-line-17-Ju-11v24-edited.png",
        "comment": (
            [
                "Ignoring the grammar of accents, the faded remains of the mark in question are slightly more plausibly"
                " interpreted as a munaḥ than a merkha."
                " But the “upright” part of the munaḥ is very faint, if it is even there are all and I am not kidding myself,"
                " seeing what I want to see rather than what is actually there."
            ],
            [
                "Note that a geresh from הוריש on the line below complicates the colliding with the elbow of the proposed munaḥ."
            ],
            [
                "In an image above, I have outlined the proposed munaḥ and the colliding geresh."
            ],
            [
                "One of the most extraordinary things about BHS (continued by BHQ) is that, to my knowledge, it never acknowledges"
                " any uncertainty in its transcription of the LC."
                " Yet of course any transcription of the LC is surely fraught with hundreds of serious uncertainties."
                " Although space constraints are extreme in any single-volume Tanakh like BHS,"
                " really the only responsible thing to do for a word like this is to acknowledge the uncertainty somehow,"
                " and either transcribe no accent at all or use context (grammar) combined with the (faint) evidence"
                " to make a good guess, which in this case would be munaḥ."
            ],
            [
                "To transcribe this word as (illegally) accented with merkha"
                " without any acknowledgment of either illegality or uncertainty is,"
                " to me, bordering on irresponsible."
            ]
        )
    },
    "ju 21:16": {
        "wlc_focus": "ויאמר֨ו",
        "st-summary": "BHS transcribes a syllable as having qadma rather than pashta.",
        "img": "LC-150A-col-1-line-22-Ju-21v16.png",
    },
    "1s 14:3": {
        "wlc_focus": "על֜י",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "1s 14:47": {
        "wlc_focus": "ובאד֜ום",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "2s 6:20": {
        "wlc_focus": "לעינ֨י",
        "st-summary": "BHS transcribes a syllable as having qadma rather than pashta.",
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.30-17",
    },
    "2s 11:11": {
        "wlc_focus": "אדנ֨י",
        "st-summary": "BHS transcribes a syllable as having qadma rather than pashta.",
        "img": "LC-174A-col-1-line-7-2S-11v11.png",
    },
    "2s 13:32": {
        "wlc_focus": "דו֜ד",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "2s 23:9": {
        "wlc_focus": "בפלשתים",
        "st-summary": "BHS does not transcribe a pashta, leaving the word without accent.",
        "uxlc_change": "https://tanach.us/Changes/2021.10.19%20-%20Changes/2021.10.19%20-%20Changes.xml?2021.08.07-3",
    },
    "1k 6:3": {
        "wlc_focus": "עשר֣ים",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2022.12.07%20-%20Changes/2022.12.07%20-%20Changes.xml?2022.08.31-10",
    },
    "1k 8:11": {
        "wlc_focus": "מפנ֥י",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2022.04.01%20-%20Changes/2022.04.01%20-%20Changes.xml?2021.11.21-1",
    },
    "1k 20:25": {
        "wlc_focus": "וס֣וס",
        "st-summary": "The checker may prefer merkha to LC’s munaḥ. Or it may not like either.",
        "img": "LC-200A-col-2-line-19-1K-20v25.png",
        "Aleppo img": "AC-1K-20v25.png",
    },
    "2k 18:17": {
        "wlc_focus": "תרת֥ן",
        "st-summary": (
            "The checker may prefer munaḥ to LC’s merkha. Or it may not like either."
            " " + xx_data.non_revia_summary("geresh", "Also, the")
        ),
        "img": "LC-215A-col-1-line-24-2K-18v17.png",
        "Aleppo img": "AC-2K-18v17.png",
        "Da-at Miqra img": "Da-at-Miqra-2K-18v17.png",
        "comment": (
            [
                "In the LC image, there is some evidence that the merkha was the result of a correction."
                " If it was the result of a correction, that makes it hard to argue that it was a scribal error."
                " If there was a correction here, one wonders if what was originally there was a munaḥ!"
            ],
            [
                "In Da-at Miqra (see image above), Breuer observes that not only the LC (ל)"
                " but also ק (Cairo Codex of The Prophets)"
                " has this merkha."
                " He also observes that the Aleppo Codex (א) and the Second Venice Miqraot Gedolot (ד)"
                " have, instead, a munaḥ."
            ],
        ),
    },
    "is 13:7": {
        "wlc_focus": "ימס׃",
        "st-summary": _SOMEWHERE,
    },
    "is 45:1": {
        "wlc_focus": "לכ֣ורש",
        "st-summary": "I think the checker wants לכ֣ורש to have a segol.",
        "comment": "There is a question of whether לכ֣ורש should have a legarmeih; see MAM’s doc-note.",
    },
    "je 26:5": {
        "wlc_focus": "דבר֨י",
        "st-summary": "BHS transcribes a syllable as having qadma rather than pashta.",
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-28",
        "comment": (
            [
                "In BHS, the mark is “late” on the ר, i.e. it is on the left of the ר rather than in its center."
                " If it were really a qadma, we would expect it to be centered on the ר."
            ],
            [
                " Instead, it looks like a stranded pashta stress helper."
                " (Some typography centers a pashta stress helper,"
                " making it indistinguishable from a qadma, but BHS aligns them distinctly.)"
                " I.e. in BHS, the mark looks like a pashta stress helper with no real (end-of-word) pashta to accompany it."
                " (Note that that adding a real pashta to this word would not fix it, since a stress helper on a final syllable makes no sense.)"
            ],
            [
                "So, though above I said “BHS transcribes a syllable as having qadma rather than pashta”,"
                " a more detailed account would be "
                "“BHS transcribes a syllable as having"
                " a stranded pashta stress helper on its first letter rather than a pashta on its last letter,"
                " and WLC transcribes BHS’s stranded stress helper as a qadma.”"
            ],
            [
                "Note that originally WLC had no distinction between a qadma and a pashta stress helper,"
                " using code 63 for both,"
                " but later WLC added a separate code for the pashta stress helper, code 33."
                " So WLC may have had no choice but to transcribe BHS’s stranded stress helper as a qadma,"
                " since it may have had no code for a pashta stress helper at the time."
                " In any case, the serious error is BHS’s transcription, not WLC’s transcription of BHS."
            ],
        ),
    },
    "je 28:2": {
        "wlc_focus": "שב֞רתי",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2023.04.01%20-%20Changes/2023.04.01%20-%20Changes.xml?2022.12.10-35",
    },
    "je 40:11": {
        "wlc_focus": "ובאד֜ום",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "je 46:4": {
        "wlc_focus": "בכ֥ובע֑ים",
        "st-summary": "BHS transcribes a meteg as a merkha.",
        "img": "LC-271B-col-1-line-5-Je-46v4.png",
    },
    "je 51:9": {
        "wlc_focus": "רפ֣ינו",
        "st-summary": _BHS_TRANSCRIBES,
        "pending_uxlc_change": "https://tanach.us/Changes/2026.10.19%20-%20Changes/2026.10.19%20-%20Changes.xml?2026.04.10-2",
    },
    "ek 9:2": {
        "wlc_focus": "העלי֜ון",
        "st-summary": xx_data.non_revia_summary("geresh"),
    },
    "ho 11:7": {
        "wlc_focus": "ירומם׃",
        "st-summary": _SOMEWHERE,
    },
    "ec 12:14": {
        "wlc_focus": "כ֤י",
        "st-summary": "Defying both BHS and the LC, WLC transcribes a yetiv as a mahapakh.",
        "uxlc_change": "https://tanach.us/Changes/2023.10.19%20-%20Changes/2023.10.19%20-%20Changes.xml?2023.09.11-25",
        "comment": (
            (
                "It is very rare for WLC to diverge from BHS like this, without a bracket note."
                " Perhaps WLC agrees with an older BHS? I have only checked the 1984 and 1997 editions of BHS."
            ),
        ),
    },
    "ne 2:10": {
        "wlc_focus": "ב֥א",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.14-3",
    },
    "ne 8:7": {
        "wlc_focus": "ושר֥בי֣ה׀",
        "st-summary": "WLC transcribes a meteg as a merkha.",
        "github-issue": "https://github.com/bdenckla/MAM-basics/issues/185",
        "img": "LC458B-col-3-line-4-Ne-8v7.png",
        "comment": (
            (
                "In the LC, the disputed mark looks strange."
                " It may be two separate marks, one of which may be unintentional."
                " The upper part of this mark (if we view it as one mark) has a merkha-like inclination"
                " but the lower part does not."
            ),
            xx_data.foi_paz_category_comment_item(),
            (
                "It makes sense to consider ne 8:7 ungrammatical on the basis of its merkha."
                " So, we have a plausible reason"
                " why the checker would accept Daniel 3:2 but not ne 8:7:"
                " ne 8:7 has this merkha and Daniel 3:2 does not."
            ),
            (
                "There is also the general question of how the checker decides between paseq and legarmeih."
                " For all I know, the checker considers one or both of the marks in question"
                " to be paseq rather than legarmeih."
            ),
        ),
    },
    "1c 1:53": {
        "wlc_focus": "אל֣וף",
        "st-summary": "The LC has a munaḥ where a merkha is expected.",
        "img": "LC-328A-col-1-line-27-1C-1v53.png",
    },
    "2c 7:5": {
        "wlc_focus": "ז֣בח הבק֗ר",
        "st-summary": "BHS accents a word with munaḥ rather than segol.",
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-3",
    },
    "2c 8:10": {
        "wlc_focus": "שר֤י",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-4",
    },
    "2c 24:27": {
        "wlc_focus": "י֧ר֞ב",
        "st-summary": "BHS adds a gershayim out of nowhere.",
        "img": "LC-357B-col-2-line-6-2C-24v27.png",
        "comment": "Perhaps the darga was accidentally repeated from the previous word, which legitimately has a darga.",
    },
    "2c 25:1": {
        "wlc_focus": "ועשר֣ים",
        "st-summary": _BHS_TRANSCRIBES,
        "uxlc_change": "https://tanach.us/Changes/2024.04.01%20-%20Changes/2024.04.01%20-%20Changes.xml?2023.09.16-13",
        "comment": (
            "See the UXLC change image. UXLC corrects WLC but places the mahapakh under the yod, an aggresively uncharitable location for it."
        ),
    },
}
