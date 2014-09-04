"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import pprint
import sys

from .MC6809_data_raw import INSTRUCTION_INFO, OP_DATA
from MC6809data.MC6809_data_raw import MEM_ACCESS_BYTE, MEM_ACCESS_WORD


keys = list(OP_DATA[0].keys())
keys.insert(3, "opcode_hex")
keys.sort()

FROM_INSTRUCTION_INFO = ['HNZVC', 'instr_desc']


MEM_ACCESS_MAP = {
    MEM_ACCESS_BYTE: "byte",
    MEM_ACCESS_WORD: "word",
}


import csv
with open('CPU6809_opcodes.csv', 'wb') as csvfile:
    w = csv.writer(csvfile,
        delimiter='\t',
        quotechar='|', quoting=csv.QUOTE_MINIMAL
    )

    w.writerow(keys + FROM_INSTRUCTION_INFO)

    for op_data in OP_DATA:
        row = []

        op_data["opcode_hex"] = hex(op_data["opcode"])

        for key in keys:
            data = op_data.get(key, "-")
            if key == "mem_access" and data != "-":
                data = MEM_ACCESS_MAP[data]
                
            if isinstance(data, str):
                data = data.replace("\t", "    ")
            row.append(data)

        instr_info_key = op_data["instr_info_key"]
        instr_info = INSTRUCTION_INFO[instr_info_key]
        for key in FROM_INSTRUCTION_INFO:
            row.append(
                instr_info.get(key, "").replace("\n", " ").replace("\t", "    ")
            )

        print(row)
        w.writerow(row)

print(" -- END -- ")
