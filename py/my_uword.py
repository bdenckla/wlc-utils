import my_hebrew_points as hpo
import my_hebrew_accents as ha
import my_hebrew_punctuation as hpu


def uword(mcword: str):
    return mcword.translate(_TRANSLATION_TABLE)

_TRANSLATION_TABLE = str.maketrans({
    '/': None,
    ')': 'א',
    'B': 'ב',
    'G': 'ג',
    'D': 'ד',
    'H': 'ה',
    'W': 'ו',
    'Z': 'ז',
    'X': 'ח',
    '+': 'ט',
    'Y': 'י',
    'K': 'כ',
    'L': 'ל',
    'M': 'מ',
    'N': 'נ',
    'S': 'ס',
    '(': 'ע',
    'P': 'פ',
    'C': 'צ',
    'Q': 'ק',
    'R': 'ר',
    '#': 'ש',
    '&': 'ש'+hpo.SIND,
    '$': 'ש'+hpo.SHIND,
    'T': 'ת',
    'A': hpo.PATAX,  # ':A': hpo.XPATAX,
    'F': hpo.QAMATS,  # ':F': hpo.XQAMATS,
    'E': hpo.SEGOL_V,  # ':E': hpo.XSEGOL,
    '"': hpo.TSERE,
    'I': hpo.XIRIQ,
    'O': hpo.XOLAM,
    'U': hpo.QUBUTS,
    ':': hpo.SHEVA,
    '.': hpo.DAGESH_OM,
    ',': hpo.RAFE,
    '-': hpu.MAQ,
})