#!/usr/bin/env python
# coding: utf-8

# copy&paste .lst content from e.g.: http://www.asm80.com/
lst = """
0000   5F                     CLRB   ; B is always 0
0001   1F 93                  TFR   B,U   ; clear U
0003                LOOP:
0003   DF 18                  STU   $0018   ; for next NEGA
0005   1F 9A                  TFR   B,CC   ; clear CC
0007   00 18                  NEG   $0018
0009   33 41                  LEAU   1,U   ; inc U
000B   0E 03                  JMP   loop
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
    print line.rstrip()

print "        ])"
