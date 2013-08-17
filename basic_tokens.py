#!/usr/bin/env python2

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

BASIC_TOKENS = {
    128: " FOR ", # 0x80
    129: " GO ", # 0x81
    130: " REM ", # 0x82
    131: "'", # 0x83
    132: " ELSE ", # 0x84
    133: " IF ", # 0x85
    134: " DATA ", # 0x86
    135: " PRINT ", # 0x87
    136: " ON ", # 0x88
    137: " INPUT ", # 0x89
    138: " END ", # 0x8a
    139: " NEXT ", # 0x8b
    140: " DIM ", # 0x8c
    141: " READ ", # 0x8d
    142: " LET ", # 0x8e
    143: " RUN ", # 0x8f
    144: " RESTORE ", # 0x90
    145: " RETURN ", # 0x91
    146: " STOP ", # 0x92
    147: " POKE ", # 0x93
    148: " CONT ", # 0x94
    149: " LIST ", # 0x95
    150: " CLEAR ", # 0x96
    151: " NEW ", # 0x97
    152: " DEF ", # 0x98
    153: " CLOAD ", # 0x99
    154: " CSAVE ", # 0x9a
    155: " OPEN ", # 0x9b
    156: " CLOSE ", # 0x9c
    157: " LLIST ", # 0x9d
    158: " SET ", # 0x9e
    159: " RESET ", # 0x9f
    160: " CLS ", # 0xa0
    161: " MOTOR ", # 0xa1
    162: " SOUND ", # 0xa2
    163: " AUDIO ", # 0xa3
    164: " EXEC ", # 0xa4
    165: " SKIPF ", # 0xa5
    166: " DELETE ", # 0xa6
    167: " EDIT ", # 0xa7
    168: " TRON ", # 0xa8
    169: " TROFF ", # 0xa9
    170: " LINE ", # 0xaa
    171: " PCLS ", # 0xab
    172: " PSET ", # 0xac
    173: " PRESET ", # 0xad
    174: " SCREEN ", # 0xae
    175: " PCLEAR ", # 0xaf
    176: " COLOR ", # 0xb0
    177: " CIRCLE ", # 0xb1
    178: " PAINT ", # 0xb2
    179: " GET ", # 0xb3
    180: " PUT ", # 0xb4
    181: " DRAW ", # 0xb5
    182: " PCOPY ", # 0xb6
    183: " PMODE ", # 0xb7
    184: " PLAY ", # 0xb8
    185: " DLOAD ", # 0xb9
    186: " RENUM ", # 0xba
    187: " TAB(", # 0xbb
    188: " TO ", # 0xbc
    189: " SUB ", # 0xbd
    190: " FN ", # 0xbe
    191: " THEN ", # 0xbf
    192: " NOT ", # 0xc0
    193: " STEP ", # 0xc1
    194: " OFF ", # 0xc2
    195: "+", # 0xc3
    196: "-", # 0xc4
    197: "*", # 0xc5
    198: "/", # 0xc6
    199: "^", # 0xc7
    200: " AND ", # 0xc8
    201: " OR ", # 0xc9
    202: ">", # 0xca
    203: "=", # 0xcb
    204: "<", # 0xcc
    205: " USING ", # 0xcd
}
# for k, v in sorted(BASIC_TOKENS.items()):
#     print '%i: "%s", # %s' % (k, v.strip(), hex(k))
# sys.exit()
