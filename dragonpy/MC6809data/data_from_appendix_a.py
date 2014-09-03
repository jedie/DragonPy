# encoding: utf-8

"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function, unicode_literals


import pprint
import os
import sys
import urllib.request, urllib.error, urllib.parse

# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup


filename = "appendix_a.htm"

if os.path.isfile(filename):
    print("use cached file %s" % filename)
else:
    print("get and save cache file %s" % filename)
    response = urllib.request.urlopen("http://www.maddes.net/m6809pm/%s" % filename)
    html = response.read()
    with open(filename, "wb") as f:
        f.write(html)


soup = BeautifulSoup(open(filename),
    # ~ "lxml",
    "html.parser",
    # ~ from_encoding="utf-8"
)

soup = soup.find("div")

cpu6809data = {}

char_convert = (
    ("\u2227", "AND"),
    ("\u2264", "<="),
    ("\u2265", "=>"),
    ("\u2190", "="),
    ("\u2192", "->"),
    ("\u2194", "<->"),
    ("\u2295", "XOR"),
    ("\u2228", "OR"),
    ("\xd7", "*"),

)
# ~ for src,dst in char_convert:
    # ~ print src.encode("utf-8"), dst

instr_convert = (
    (" (8-Bit)", "8"),
    (" (16-Bit)", "16"),
)

USE_SOURCE_FORM = {
    "AND": "ANDCC",
    "OR": "ORCC",
}

class Tee(object):
    def __init__(self, filepath, origin_out):
        self.filepath = filepath
        self.origin_out = origin_out
        self.f = file(filepath, "w")

    def write(self, *args):
        txt = " ".join(args)
        self.origin_out.write(txt)
        self.f.write(txt)

    def close(self):
        self.f.close()

sys.stdout = Tee("appendix_a.py", sys.stdout)


print('"""%s"""' % __doc__)
print()
for table in soup.find_all("table", attrs={"class":"appAa"}):

    instruction = table.findNext("th").get_text(" ", strip=True)
    instruction = instruction.encode("ascii")
    for src, dst in instr_convert:
        instruction = instruction.replace(src, dst)

    data = {}
    key = None
    for tr in table.findChildren("tr"):
        # ~ print " --------- "
        for td in tr.findChildren("td"):
            # ~ print "++", td
            if "class" in td.attrs and "bold" in td["class"]:
                key = td.contents[0].lower().strip().rstrip("s:")
                # ~ print "key:", key
                continue

            sub_table = td.find("table")
            if sub_table:
                # ~ print sub_table
                txt = []
                for row in sub_table.findChildren(['th', 'tr']):
                    txt.append(row.get_text(" ", strip=True))
                txt = "\n".join(txt)
            else:
                txt = td.get_text(" ", strip=True)

            if key:
                key = key.encode("ascii")
                for src, dst in char_convert:
                    txt = txt.replace(src, dst)

                try:
                    txt = txt.encode("ascii")
                except UnicodeEncodeError as err:
                    print(err)
                    print(instruction, key)
                    print(repr(txt))
                    sys.exit()

                data[key] = txt
                key = None

    for key, other in list(USE_SOURCE_FORM.items()):
        if instruction == key:
            if other in data["source form"]:
                instruction = other
                break

    if instruction in cpu6809data:
        print("%s exists more then one time!")
        print("new:")
        pprint.pprint(data)
        print("old:")
        pprint.pprint(cpu6809data[instruction])
        raise AssertionError
    cpu6809data[instruction] = data

print("INSTRUCTION_INFO = ", pprint.pformat(cpu6809data))
