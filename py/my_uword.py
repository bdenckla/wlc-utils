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
_ACCENTS = {
    '00': hpu.SOPA,
    '01': ha.SEG_A,
    '02': ha.ZARQA,
    '03': ha.PASH,
    '04': ha.TEL_Q,
    '05': hpu.PAS,
    '10': ha.YETIV,
    '13': ha.TIP,  # dehi or tipha             II.9
    '11': ha.GER_M,
    '12': ha.GER_2,  # garshayim (preposed)
    '14': ha.TEL_G,  # telisha gedolah
    '24': ha.TEL_Q,  # stress helper to 04 (4 cases)
    '33': ha.PASH,  # stress helper to 03
    '44': ha.TEL_G,  # stress helper to 14
    '52': '\N{HEBREW MARK UPPER DOT}',
    '60': ha.OLE,
    '61': ha.GER,
    '62': ha.GER_2,
    '63': ha.QADMA,
    '64': ha.ILUY,
    '65': ha.SHAL,
    '80': ha.ZAQEF_Q,
    '81': ha.REV,
    '82': ha.ZARQA_SH,  # 2 cases of s.h. use: 2s3:8 & 2c19:2. Also functions as tsinnorit.
    '83': ha.PAZER,
    '84': ha.QARNEY,  # aka pazer gadol
    '85': ha.ZAQEF_G,
    '35': hpo.METEG,  # medial
    '53': '\N{HEBREW MARK LOWER DOT}',
    '70': ha.MAHA,
    '71': ha.MER,
    '72': ha.MER_2,
    '73': ha.TIP,
    '74': ha.MUN,
    '75': hpo.METEG,  # left (normal)
    '91': ha.TEVIR,
    '92': ha.ATN,
    '93': ha.YBY,  # aka galgal
    '94': ha.DARGA,
    '95': hpo.METEG, # right ("early")
}
