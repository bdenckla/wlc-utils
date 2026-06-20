"""Prose lexical validation: flag stranded stress-helper accents (alphabet errors).

This is a *prose-only* layer that sits on top of the faithful C-port scanner/
grammar (ply_scanner / ply_grammar) and intentionally **diverges from the
goerwitz C oracle**, in the same documented spirit as the MISSING_SOFPASUQ and
tevir/tipexa recoveries: where the C lexer silently swallows a malformed accent,
we surface it as an oddball.

The one helper handled today is accent ``82``.  In the prose accent system, ``82``
is well-formed *only* as the left half of a ``82{TEXT}02`` pair fused onto a single
maqaf/space-delimited atom, where the scanner reads it as one ZARQA token
(ply_scanner ``(?:82{TEXT}02)?02``; TEXT = ``[^ \\r\\n-]*`` keeps the pair inside
one atom).  When there is no ``02`` later in the same atom, the C lexer's
``35|75|95|44|05|82|52 -> None`` rule swallows the ``82`` and the intended accent
simply vanishes -- so whether the verse becomes an oddball is left to downstream
parse luck.  All 12 such prose verses (a stray zarqa mis-encoded before a lamed
ascender) are equally wrong; this layer flags them uniformly.

Prose-only is intentional and burns no bridge: a bare ``82`` is *valid* in the
poetic accent system (tsinnorit, >200 uses), but the genre split already happens
upstream (accgram.prose_filter strips Psalms/Proverbs/poetic-Job before scanning),
so within this prose pipeline a bare ``82`` is unconditionally illegal.  A future
poetic checker is expected to have its own lexer where ``82`` is a first-class
token; this module therefore hard-codes prose semantics with no genre parameter.

The module is self-contained: it re-derives the per-atom 2-digit accent-code stream
straight from the verse body (the Michigan-Claremont transliteration with embedded
2-digit codes), with no dependency on the scanner internals.  It is kept general
enough that other stranded stress-helpers could be added later, but only ``82`` is
wired up now (the siblings ``44``/lone ``24`` and the unknown codes ``11``/``12``
need a separate scholarly call -- see the tracking GitHub issue).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from accgram import accent_marks as am

# Atoms are delimited by spaces and maqaf (``-``), mirroring the scanner's TEXT
# class ``[^ \r\n-]*`` which keeps a fused tsinnorit...zinor pair inside one atom.
_ATOM_SPLIT_RE = re.compile(r"[ \t\r\n\-]+")

# stress-helper mark -> (fusion-partner mark, M-C code label) where the partner must
# follow the helper later in the same atom for the helper to be well-formed.  Only the
# zarqa stress-helper (tsinnorit, U+0598, M-C 82) -- whose partner is the zinor (U+05AE,
# M-C 02) -- is active today.  The label is the original M-C code, kept so the
# ``illegal_mark`` report reads identically to the pre-Phase-2 output.
_STRESS_HELPER_PARTNER: dict[str, tuple[str, str]] = {am.TSINNORIT: (am.ZINOR, "82")}


@dataclass(frozen=True)
class StrandedMark:
    """A stress-helper mark left without its fusion partner in the same atom."""

    code: str  # the stranded helper's M-C code label, e.g. "82"
    atom: str  # the maqaf/space-delimited atom that contains it


def stranded_stress_helpers(body: str) -> list[StrandedMark]:
    """Return every stranded stress-helper in a prose verse body.

    A stress-helper (today only the tsinnorit, M-C ``82``) is *stranded* when its
    fusion partner (the zinor, M-C ``02``) does not occur later in the same maqaf/
    space-delimited atom.  Such a mark is an intrinsic lexical ("alphabet") error
    independent of surrounding context.
    """
    stranded: list[StrandedMark] = []
    for atom in _ATOM_SPLIT_RE.split(body):
        if not atom:
            continue
        for i, ch in enumerate(atom):
            entry = _STRESS_HELPER_PARTNER.get(ch)
            if entry is None:
                continue
            partner, code = entry
            if partner not in atom[i + 1 :]:
                stranded.append(StrandedMark(code=code, atom=atom))
    return stranded
