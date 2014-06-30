#!/usr/bin/env python
# coding: utf-8

# copy&paste .lst content from e.g.: http://www.asm80.com/
lst = """
0100                          .ORG   $100
0100                          ; sample parameters on stack ...
0100   CC 00 00               LDD   #$0000   ; dividend low word
0103   36 06                  PSHU   d
0105   CC 58 00               LDD   #$5800   ; dividend high word
0108   36 06                  PSHU   d
010A   CC 30 00               LDD   #$3000   ; divisor
010D   36 06                  PSHU   d
010F   EC 42        USLASH:   LDD   2,u
0111   AE 44                  LDX   4,u
0113   AF 42                  STX   2,u
0115   ED 44                  STD   4,u
0117   68 43                  ASL   3,u   ; initial shift of L word
0119   69 42                  ROL   2,u
011B   8E 00 10               LDX   #$10
011E   69 45        USL1:     ROL   5,u   ; shift H word
0120   69 44                  ROL   4,u
0122   EC 44                  LDD   4,u
0124   A3 C4                  SUBD   ,u   ; does divisor fit?
0126   1C FE                  ANDCC   #$FE   ; clc - clear carry flag
0128   2B 04                  BMI   USL2
012A   ED 44                  STD   4,u   ; fits -> quotient = 1
012C   1A 01                  ORCC   #$01   ; sec - Set Carry flag
012E   69 43        USL2:     ROL   3,u   ; L word/quotient
0130   69 42                  ROL   2,u
0132   30 1F                  LEAX   -1,x
0134   26 E8                  BNE   USL1
0136   33 42                  LEAU   2,u
0138   AE C4                  LDX   ,u   ; quotient
013A   EC 42                  LDD   2,u   ; remainder
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

#    line = "            %-30s %s|%10s %-5s %-10s %s" % (
#        hex_list, address, lable, code1, code2, doc
#    )
    line = "            %-30s %10s %-5s %-10s %s" % (
        hex_list, lable, code1, code2, doc
    )
    print line.rstrip()

print "        ])"
