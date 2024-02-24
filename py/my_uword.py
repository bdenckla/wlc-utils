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
    '03': ha.PASH,  # pashta, azla legarmeh   I.10a,II.12
    '04': ha.TEL_Q,
    '05': hpu.PAS,
    '10': ha.YETIV,
    '13': ha.TIP,  # dehi or tipha             II.9
    '11': ha.GER_M,
    '12': ha.GER_2,  # garshajim (preposed)        -
    '14': ha.TEL_G,  # telisha magnum             I.17
    '24': ha.TEL_Q,  # telisha parvum (med)         -
    '33': ha.PASH,  # (with 03, left of letter)   I.10(b)
    '44': ha.TEL_G,  # telisha magnum (med)         -
    '52': '\N{HEBREW MARK UPPER DOT}',  # puncta extraordinaria        -
    '60': ha.OLE,  # ole or mahpakatum         (II.2)
    '61': ha.GER,  # geresh or teres             I.13
    '62': ha.GER_2,  # garshajim                   I.14
    '63': ha.QADMA,  # azla, azla or qadma      I.24,II.19
    '64': ha.ILUY,  # illuj                      II.15
    '65': ha.SHAL,  # shalshelet (magn,parv)    I.4,II.6+20
    '80': ha.ZAQEF_Q,  # zaqep parvum                I.5
    '81': ha.REV,  # rebia (magnum=parvum)     I.7,II.4=8
    '82': ha.ZARQA_SH,  # sinnorit                   II.21
    '83': ha.PAZER,  # pazer                    I.15,II.10
    '84': ha.QARNEY,  # pazer mag. or qarne para    I.16
    '85': ha.ZAQEF_G,  # zaqep magnum                I.6
    '35': hpo.METEG,  # meteg (med)                  -
    '53': '\N{HEBREW MARK LOWER DOT}',  # puncta extraordinaria         -
    '70': ha.MAHA,  # mahpak or mehuppak       I.20,II.11+18
    '71': ha.MER,  # mereka                    I.21,II.14
    '72': ha.MER_2,  # mereka kepulah (duplex)      I.22
    '73': ha.TIP,  # tipha, tarha               I.8,II.16
    '74': ha.MUN,  # munah                  I.18-19,II.13
    '75': hpo.METEG,  # silluq [meteg (left)]      I.1,II.1
    '91': ha.TEVIR,  # tebir                        I.12
    '92': ha.ATN,  # atnah                      I.2,II.3
    '93': ha.YBY,  # galgal or jerah           I.26,II.17
    '94': ha.DARGA,  # darga                        I.23
    '95': hpo.METEG,  # meteg (right) [cf 35,75]      -
}

#'00': ';',  # --- sop pasuq [end of verse]
#'01': '.:---',  # segolta                     I.3
#      02  )--- zarqa, sinnor             I.9,II.7
#      03  \--- pashta, azla legarmeh   I.10a,II.12
#      04  &--- telisha parvum              I.25
#      05  |--- paseq [separator]          "Nota"
#       - |-,-- legarmeh (74 + 05)          I.18

# At START (to right) of word and BELOW
#      10   ---< yetib (yetiv)              I.11
#      13   ---\ dehi or tipha             II.9

# At START (to right) of word and ABOVE
#      11   ---/ (81 + ) mugrash           II.5
#      12   ---" garshajim (preposed)        -
#      14   ---% telisha magnum             I.17

# ABOVE word
#      24  -&-- telisha parvum (med)         -
#      33  --\- (with 03, left of letter)   I.10(b)
#      44  -%-- telisha magnum (med)         -
#      52  --.- puncta extraordinaria        -
#      60  --<- ole or mahpakatum         (II.2)
#      61  -/-- geresh or teres             I.13
#      62  -"-- garshajim                   I.14
#      63  -\-- azla, azla or qadma      I.24,II.19
#      64  -,-- illuj                      II.15
#      65  -#-- shalshelet (magn,parv)    I.4,II.6+20
#      80  -:-- zaqep parvum                I.5
#      81  -.-- rebia (magnum=parvum)     I.7,II.4=8
#      82  --)- sinnorit                   II.21
#      83  -+-- pazer                    I.15,II.10
#'84': '-&%--',  # pazer mag. or qarne para    I.16
#'85': '-|:--',  # zaqep magnum                I.6

# BELOW word
#'35': '-F|:--',  # meteg (med)                  -
#      53  --.- puncta extraordinaria         -
#      70  -<-- mahpak or mehuppak       I.20,II.11+18
#      71  -/-- mereka                    I.21,II.14
#'72': '-//--',  # mereka kepulah (duplex)      I.22
#      73  -\-- tipha, tarha               I.8,II.16
#       - --\-- majela [= 73]                I.27
#      74  -,-- munah                  I.18-19,II.13
#      75  -|-- silluq [meteg (left)]      I.1,II.1
#'91': '-./--',  # tebir                        I.12
#      92  -^-- atnah                      I.2,II.3
#      93  -v-- galgal or jerah           I.26,II.17
#      94  -s-- darga                        I.23
#      95  -|-- meteg (right) [cf 35,75]      -
