# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    informations from:
    http://sourceforge.net/p/toolshed/code/ci/default/tree/cocoroms/bas.asm

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


COCO_BASIC_TOKENS = {
    0x80: "FOR",
    0x81: "GO",
    0x82: "REM",
    0x83: "'",
    0x84: "ELSE",
    0x85: "IF",
    0x86: "DATA",
    0x87: "PRINT",
    0x88: "ON",
    0x89: "INPUT",
    0x8a: "END",
    0x8b: "NEXT",
    0x8c: "DIM",
    0x8d: "READ",
    0x8e: "RUN",
    0x8f: "RESTORE",
    0x90: "RETURN",
    0x91: "STOP",
    0x92: "POKE",
    0x93: "CONT",
    0x94: "LIST",
    0x95: "CLEAR",
    0x96: "NEW",
    0x97: "CLOAD",
    0x98: "CSAVE",
    0x99: "OPEN",
    0x9a: "CLOSE",
    0x9b: "LLIST",
    0x9c: "SET",
    0x9d: "RESET",
    0x9e: "CLS",
    0x9f: "MOTOR",
    0xa0: "SOUND",
    0xa1: "AUDIO",
    0xa2: "EXEC",
    0xa3: "SKIPF",
    0xa4: "TAB(",
    0xa5: "TO",
    0xa6: "SUB",
    0xa7: "THEN",
    0xa8: "NOT",
    0xa9: "STEP",
    0xaa: "OFF",
    0xab: "+",
    0xac: "-",
    0xad: "*",
    0xae: "/",
    0xaf: "^",
    0xb0: "AND",
    0xb1: "OR",
    0xb2: ">",
    0xb3: "=",
    0xb4: "<",

    # Function tokens - all proceeded by 0xff to differentiate from operators

    0xff81: "INT",
    0xff82: "ABS",
    0xff83: "USR",
    0xff84: "RND",
    0xff85: "SIN",
    0xff86: "PEEK",
    0xff87: "LEN",
    0xff88: "STR$",
    0xff89: "VAL",
    0xff8a: "ASC",
    0xff8b: "CHR$",
    0xff8c: "EOF",
    0xff8d: "JOYSTK",
    0xff8e: "LEFT$",
    0xff8f: "RIGHT$",
    0xff90: "MID$",
    0xff91: "POINT",
    0xff92: "INKEY$",
    0xff93: "MEM",
}


if __name__ == '__main__':
    from dragonlib.dragon32.basic_tokens import DRAGON32_BASIC_TOKENS

    values = range(0x80, 0x100) + range(0x8000, 0x10000)

    # Generate Wiki Table for:
    # http://archive.worldofdragon.org/index.php?title=Tokens

    print """
{| class="wikitable" style="font-family: monospace; background-color:#ffffcc;" cellpadding="10"
|-
! value
! Dragon
token
! CoCo
token
"""
    for value in values:
        coco_statement = COCO_BASIC_TOKENS.get(value, "")
        dragon_statement = DRAGON32_BASIC_TOKENS.get(value, "")

        if coco_statement == "" and dragon_statement == "":
            continue

        if value > 0xff:
            value = "$%04x" % value
        else:
            value = "$%02x" % value

        print "|-"
        print "| %s" % value
        print "| %s" % dragon_statement
        print "| %s" % coco_statement
    print "|-"
    print "|}"
