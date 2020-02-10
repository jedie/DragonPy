#!/usr/bin/env python2

"""
    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

BASIC_TOKENS = {
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
    0x8e: "LET",
    0x8f: "RUN",
    0x90: "RESTORE",
    0x91: "RETURN",
    0x92: "STOP",
    0x93: "POKE",
    0x94: "CONT",
    0x95: "LIST",
    0x96: "CLEAR",
    0x97: "NEW",
    0x98: "DEF",
    0x99: "CLOAD",
    0x9a: "CSAVE",
    0x9b: "OPEN",
    0x9c: "CLOSE",
    0x9d: "LLIST",
    0x9e: "SET",
    0x9f: "RESET",
    0xa0: "CLS",
    0xa1: "MOTOR",
    0xa2: "SOUND",
    0xa3: "AUDIO",
    0xa4: "EXEC",
    0xa5: "SKIPF",
    0xa6: "DELETE",
    0xa7: "EDIT",
    0xa8: "TRON",
    0xa9: "TROFF",
    0xaa: "LINE",
    0xab: "PCLS",
    0xac: "PSET",
    0xad: "PRESET",
    0xae: "SCREEN",
    0xaf: "PCLEAR",
    0xb0: "COLOR",
    0xb1: "CIRCLE",
    0xb2: "PAINT",
    0xb3: "GET",
    0xb4: "PUT",
    0xb5: "DRAW",
    0xb6: "PCOPY",
    0xb7: "PMODE",
    0xb8: "PLAY",
    0xb9: "DLOAD",
    0xba: "RENUM",
    0xbb: "TAB(",
    0xbc: "TO",
    0xbd: "SUB",
    0xbe: "FN",
    0xbf: "THEN",
    0xc0: "NOT",
    0xc1: "STEP",
    0xc2: "OFF",
    0xc3: "+",
    0xc4: "-",
    0xc5: "*",
    0xc6: "/",
    0xc7: "^",
    0xc8: "AND",
    0xc9: "OR",
    0xca: ">",
    0xcb: "=",
    0xcc: "<",
    0xcd: "USING",
}


# Function tokens - all proceeded by 0xff to differentiate from operators
FUNCTION_TOKEN = {
    0x80: "SGN",
    0x81: "INT",
    0x82: "ABS",
    0x83: "POS",
    0x84: "RND",
    0x85: "SQR",
    0x86: "LOG",
    0x87: "EXP",
    0x88: "SIN",
    0x89: "COS",
    0x8a: "TAN",
    0x8b: "ATN",
    0x8c: "PEEK",
    0x8d: "LEN",
    0x8e: "STR$",
    0x8f: "VAL",
    0x90: "ASC",
    0x91: "CHR$",
    0x92: "EOF",
    0x93: "JOYSTK",
    0x94: "FIX",
    0x95: "HEX$",
    0x96: "LEFT$",
    0x97: "RIGHT$",
    0x98: "MID$",
    0x99: "POINT",
    0x9a: "INKEY$",
    0x9b: "MEM",
    0x9c: "VARPTR",
    0x9d: "INSTR",
    0x9e: "TIMER",
    0x9f: "PPOINT",
    0xa0: "STRING$",
    0xa1: "USR",
}



def bytes2codeline(raw_bytes):
    """
    >>> data = (0x87,0x20,0x22,0x48,0x45,0x4c,0x4c,0x4f,0x20,0x57,0x4f,0x52,0x4c,0x44,0x21,0x22)
    >>> bytes2codeline(data)
    'PRINT "HELLO WORLD!"'
    """
    code_line = ""
    func_token = False
    for byte_no in raw_bytes:
        if byte_no == 0xff: # Next byte is a function token
            func_token = True
            continue
        elif func_token == True:
            func_token = False
            try:
                character = FUNCTION_TOKEN[byte_no]
            except KeyError as err:
                print("Error: BASIC function torken for '%s' not found!" % hex(byte_no))
                character = chr(byte_no)
        elif byte_no in BASIC_TOKENS:
            try:
                character = BASIC_TOKENS[byte_no]
            except KeyError as err:
                print("Error: BASIC torken for '%s' not found!" % hex(byte_no))
                character = chr(byte_no)
        else:
            character = chr(byte_no)
#         print byte_no, repr(character)
        code_line += character
    return code_line


if __name__ == "__main__":
    import doctest
    print(doctest.testmod())

    def pprint_formated(d):
        for k, v in sorted(d.items()):
            print('    %s: "%s",' % (hex(k), v.strip()))

    print("BASIC_TOKENS = {")
    pprint_formated(BASIC_TOKENS)
    print("}")

    print("FUNCTION_TOKEN = {")
    pprint_formated(FUNCTION_TOKEN)
    print("}")
