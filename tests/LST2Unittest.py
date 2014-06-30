#!/usr/bin/env python
# coding: utf-8

# copy&paste .lst content from e.g.: http://www.asm80.com/
lst = """
0100                          .ORG   $100
0100                CRCHH:    EQU   $ED
0100                CRCHL:    EQU   $B8
0100                CRCLH:    EQU   $83
0100                CRCLL:    EQU   $20
0100                CRCINITH:   EQU   $FFFF
0100                CRCINITL:   EQU   $FFFF
0100                BL:
0100   E8 C0                  EORB   ,u+   ; XOR with lowest byte
0102   10 8E 00 08            LDY   #8   ; bit counter
0106                RL:
0106   1E 01                  EXG   d,x
0108                RL1:
0108   44                     LSRA   ; shift CRC right, beginning with high word
0109   56                     RORB
010A   1E 01                  EXG   d,x
010C   46                     RORA   ; low word
010D   56                     RORB
010E   24 12                  BCC   cl
0110                          ; CRC=CRC XOR polynomic
0110   88 83                  EORA   #CRCLH   ; apply CRC polynomic low word
0112   C8 20                  EORB   #CRCLL
0114   1E 01                  EXG   d,x
0116   88 ED                  EORA   #CRCHH   ; apply CRC polynomic high word
0118   C8 B8                  EORB   #CRCHL
011A   31 3F                  LEAY   -1,y   ; bit count down
011C   26 EA                  BNE   rl1
011E   1E 01                  EXG   d,x   ; CRC: restore correct order
0120   27 04                  BEQ   el   ; leave bit loop
0122                CL:
0122   31 3F                  LEAY   -1,y   ; bit count down
0124   26 E0                  BNE   rl   ; bit loop
0126                EL:
0126   11 A3 E4               CMPU   ,s   ; end address reached?
0129   26 D5                  BNE   bl   ; byte loop

"""

"""
        self.cpu_test_run(start=0x2000, end=None, mem=[
            0x10, 0x8e, 0x30, 0x00, #       2000|       LDY $3000
            0xcc, 0x10, 0x00, #             2004|       LDD $1000
            0xed, 0xa4, #                   2007|       STD ,Y
            0x86, 0x55, #                   2009|       LDA $55
            0xA7, 0xb4, #                   200B|       STA ,[Y]
        ])
"""

print "        self.cpu_test_run(start=0x2000, end=None, mem=["
for line in lst.strip().splitlines():
    address = line[:4]

    hex_list = line[7:30]
    lable = ""
    if ":" in hex_list:
        hex_list = hex_list.strip()
        try:
            hex_list, lable = hex_list.strip().rsplit(" ", 1)
        except ValueError:
            lable = hex_list
            hex_list = ""
        else:
            lable = lable.strip()

    hex_list = hex_list.strip().split(" ")
    hex_list = ", ".join(["0x%s" % i for i in hex_list if i])

    code1 = line[30:].strip()
    doc = ""
    if ";" in code1:
        code1, doc = code1.split(";", 1)
        code1 = code1.strip()
        doc = ";%s" % doc

    code2 = ""
    if " " in code1:
        code1, code2 = code1.split(" ", 1)
        code1 = code1.strip()
        code2 = code2.strip()

    if hex_list:
        hex_list += ", #"
    else:
        hex_list += "#"

    line = "            %-30s %s|%10s %-5s %-10s %s" % (
        hex_list, address, lable, code1, code2, doc
    )
#     line = "            %-30s %10s %-5s %-10s %s" % (
#         hex_list, lable, code1, code2, doc
#     )
    print line.rstrip()

print "        ])"
