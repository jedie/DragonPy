"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/sections.htm#sec4_4
        * http://www.burgins.com/m6809.html
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013-2014 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import pprint
import sys

from MC6809_data_raw2 import OP_DATA


class Cell(object):
    def __init__(self, txt):
        self.txt = txt
        self.rowspan = 0
    def html(self):
        if self.rowspan is None:
            return ""
        elif self.rowspan == 1:
            return "<td>%s</td>" % self.txt
        return '<td rowspan="%i">%s</td>' % (self.rowspan, self.txt)

    def __str__(self):
        return "<'%s' rowspan=%s>" % (self.txt, self.rowspan)
    __repr__ = __str__


data = []
no = 0
for instruction, instr_data in sorted(OP_DATA.items()):
    for mnemonic, memoric_data in sorted(instr_data["mnemonic"].items()):
        for op_code, op_data in sorted(memoric_data["ops"].items()):
            no += 1
            data.append(
                (no, instruction, mnemonic, hex(op_code)) + tuple(op_data.values())
            )


# pprint.pprint(data)
# print "-"*79


new_data = []
for row in data:
    new_data.append([Cell(cell) for cell in row])
data = new_data


for colum_no in xrange(len(data[0])):
    old_cell = None
    same_count = 0
    for row in reversed(data) :
        cell = row[colum_no]
        if old_cell is None:
            old_cell = cell
            same_count = 1
        elif cell.txt == old_cell.txt:
            old_cell.rowspan = None
            old_cell = cell
            same_count += 1
        else:
            old_cell.rowspan = same_count
            old_cell = cell
            same_count = 1
    old_cell.rowspan = same_count


print "<table>"
for row in data:
    print "<tr>"
    for cell in row:
        if cell.rowspan is not None:
            print "\t%s" % cell.html()
    print "</tr>"
print "</table>"


print " -- END -- "
