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

import pprint
import sys

from MC6809_data_raw import OP_CATEGORIES, INSTRUCTION_INFO, OP_DATA, ADDRES_MODE_DICT


keys = OP_DATA[0].keys()

import csv
with open('CPU6809_opcodes.csv', 'wb') as csvfile:
    w = csv.writer(csvfile,
        delimiter=';',
        quotechar='|', quoting=csv.QUOTE_MINIMAL
    )

    for op_data in OP_DATA:
        row = []
        for k in keys:
            data = op_data[k]
            if k == "opcode":
                data = hex(data)
            elif k == "addr_mode":
                data = ADDRES_MODE_DICT[data]
            row.append(data)
            
        instr_info_key = op_data["instr_info_key"]
        row.append(
            INSTRUCTION_INFO[instr_info_key].get('operation', "").replace("\n", " ").replace(";", "|")
        )
            
        print row
        w.writerow(row)

print " -- END -- "
