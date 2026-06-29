"""Oddball structured research notes — dt."""

from __future__ import annotations

from accgram.prose_ob_notes_shared import (
    MISSING_SOF_PASUQ_COMMENT,
    MISSING_SOF_PASUQ_SUMMARY,
    SOMEWHERE,
    ZARQA_WHIM,
)


BY_REF: dict[str, dict[str, object]] = {
    "dt 5:8": {
        # Dual-cantillation detangling (issue #36). dt 5:8 is one of the two-reading
        # Decalogue verses excluded from the normal scan. WLC's "tangled" form for
        # תעשה carries only a merkha on the ש; a better LC transcription reads that
        # vertical bar as a meteg (belonging to the elyon) and supplies a qadma
        # (belonging to the taḥton) -- the consensus pointing, under which both the
        # taḥton and elyon chanted verses are grammatical, where the merkha makes both
        # ungrammatical. (MAM's taḥton has the qadma and its elyon has the meteg, which
        # the scanner swallows, which is why MAM's elyon parses cleanly.) The checker supplies
        # the taḥton's qadma (clean, on the supplied-marks page) and emits WLC's actual
        # merkha in the elyon, so only the elyon is a dt 5:8 oddity now. UXLC corrects
        # the merkha to a meteg but supplies a pashta rather than the due qadma; see the
        # linked UXLC note page (its `-t` te'amim note). UXLC has since proposed a pending
        # change (for UXLC 2.6) to change that pashta to the qadma -- exactly the
        # correction this note argues for. Whether the error originates in LC, BHS, or BHQ
        # has not been confirmed -> tbd.
        "st-source": "tbd",
        "wlc_focus": "תעש֥ה־",
        "st-summary": (
            "Dual cantillation (Decalogue): WLC’s “tangled” form for תעשה carries only"
            " a merkha on the ש, but a better LC transcription reads a meteg (elyon)"
            " plus a qadma (taḥton) — the consensus pointing, under which both the"
            " taḥton and elyon chanted verses are grammatical, where the merkha makes"
            " both ungrammatical, so the checker supplies the taḥton its due qadma"
            " (that reading then parses clean) and leaves WLC’s merkha in the elyon,"
            " where only a meteg is due, so the elyon is the oddball. UXLC corrects the"
            " merkha to a meteg but supplies a"
            " pashta rather than the due qadma; a pending UXLC change would correct that"
            " pashta to the qadma."
        ),
        "comment": [
            "WLC represents dual cantillation in manuscript style, which I call a"
            " “tangled” style, where both taḥton and elyon marks appear superimposed"
            " on the same set of letters.",
            "WLC’s tangled form for תעשה has only a merkha. This could be interpreted"
            " as both taḥton and elyon having merkha, or one having merkha and the"
            " other having nothing.",
            "Although the LC is not in great shape here (see the image in the UXLC"
            " note), a better transcription of the"
            " LC here would interpret the vertical bar under ש as meteg rather than"
            " merkha, and would add a qadma over the ש. Admittedly, this is a"
            " transcription somewhat influenced by the fact that this is the consensus"
            " pointing of this word. Not surprisingly, this consensus pointing makes"
            " both the taḥton chanted verse and the elyon chanted verse grammatical, if"
            " the qadma is taken to belong to the taḥton and the meteg is taken to"
            " belong to the elyon.",
            "In contrast, WLC’s actual merkha makes both chanted verses"
            " ungrammatical. The checker adopts the qadma for the taḥton — supplying"
            " it, so that reading parses clean (inventoried on the supplied-marks page) —"
            " but leaves WLC’s actual merkha in the elyon, which is therefore this"
            " oddball.",
            "We do not shy away from transcriptions that, while grounded in manuscript"
            " evidence, use context (consensus and grammar) to supplement manuscript"
            " evidence when the manuscript evidence is ambiguous, for example when the"
            " manuscript image is blurry or the manuscript itself is in bad shape.",
            "UXLC goes most of the way towards correcting WLC here. While UXLC does"
            " correct the merkha to be a meteg, unfortunately UXLC adds a pashta rather"
            " than a qadma.",
            "UXLC has now proposed a pending change (slated for UXLC 2.6) that changes"
            " this pashta over the ש to a qadma — exactly the correction we advocate"
            " here. See the “Pending UXLC change” link above.",
            "This error in WLC probably has its source in BHS and/or BHQ, i.e. this error is"
            " unlikely original to WLC, but we have not confirmed that.",
        ],
        # The detangled focus word תעשה in each reading, across the three transcriptions
        # (issue #36). One per-strand table replaces the old combined focus/diff table:
        # the merkha breaks both readings, but the two readings disagree on what is due
        # (taḥton: a qadma; elyon: no accent, just a meteg), so splitting clarifies that
        # the elyon correction (merkha→meteg) is agreed by MAM and UXLC while only the
        # taḥton correction (qadma vs pashta) is where they part. Keyed by strand_label;
        # each row is (value, desc, source). The WLC value is cross-checked against the
        # detangled stream at render time, so it cannot silently drift.
        "dual_cant_tables": {
            "taxton": [
                {"value": "תעש֥ה", "desc": "merkha (a qadma is due here)", "source": "WLC"},
                {"value": "תעש֨ה", "desc": "qadma", "source": "MAM"},
                {"value": "תעש֙ה", "desc": "pashta (UXLC supplies a pashta, not the due qadma)", "source": "UXLC"},
            ],
            "elyon": [
                {"value": "תעש֥ה־", "desc": "merkha (no accent is due here, only a meteg)", "source": "WLC"},
                {"value": "תעשֽה־", "desc": "meteg", "source": "MAM"},
                {"value": "תעשֽה־", "desc": "meteg", "source": "UXLC"},
            ],
        },
        "pending_uxlc_change": "2026.10.19/2026.04.10-10",
        "uxlc_note_page": "https://tanach.us/Notes/Deuteronomy/Deuteronomy.5.8.2-t.html",
    },
    "dt 9:20": {
        "st-source": "tbd",
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "ההֽוא",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 13:15": {
        "st-source": "lc",
        "st-summary": "The LC has darga where it should have tevir.",
        "wlc_focus": "וחקרת֧",
        "img": "LC-107B-col-3-line-18-dt-13v15.png",
    },
    "dt 25:9": {
        "st-source": "tbd",
        "st-summary": MISSING_SOF_PASUQ_SUMMARY,
        "wlc_focus": "אחֽיו",
        "comment": MISSING_SOF_PASUQ_COMMENT,
        "BHQ": "?",
    },
    "dt 10:15": {
        "st-source": "tbd",
        "wlc_focus": "הזה׃",
        "st-summary": SOMEWHERE,
    },
    "dt 12:2": {
        "st-source": "tbd",
        "wlc_focus": "רענן׃",
        "st-summary": SOMEWHERE,
    },
    "dt 23:18": {
        "st-source": "tbd",
        "wlc_focus": "ישראל׃",
        "st-summary": SOMEWHERE,
    },
    "dt 24:10": {
        "st-source": "lc",
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
    "dt 14:24": {
        "st-source": "wlc",
        "wlc_focus": "תוכ֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-8",
        **ZARQA_WHIM,
    },
    "dt 31:7": {
        "st-source": "wlc",
        "wlc_focus": "ישרא֘ל",
        "uxlc_change": "2021.04.01/2020.12.06-9",
        **ZARQA_WHIM,
    },
}
