# encoding: utf-8

"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    data from:
        * http://www.maddes.net/m6809pm/appendix_a.htm#appA

    :copyleft: 2013 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from pprint import pprint

# http://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup
import sys

soup = BeautifulSoup(open("appendix_a.htm"), "lxml")

soup = soup.find("div")

cpu6809data = {}

char_convert = (
    (u"\u2227", "AND"),
    (u"\u2264", "<="),
    (u"\u2265", "=>"),
    (u"\u2190", "="),
    (u"\u2192", "->"),
    (u"\u2194", "<->"),
    (u"\u2295", "XOR"),
    (u"\u2228", "OR"),
    (u"\xd7", "*"),

)
# ~ for src,dst in char_convert:
    # ~ print src.encode("utf-8"), dst

for table in soup.find_all("table", attrs={"class":"appAa"}):
    # ~ print "-"*79
    # ~ print repr(table.prettify())

    instruction = table.findNext("th").get_text(" ", strip=True)

    # ~ desc = table.find_all("th")[1].contents[0]

    data = {}
    key = None
    for tr in table.findChildren("tr"):
        # ~ print " --------- "
        for td in tr.findChildren("td"):
            # ~ print "++", td
            if "class" in td.attrs and "bold" in td["class"]:
                key = td.contents[0].lower().strip().strip(":")
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
                for src, dst in char_convert:
                    txt = txt.replace(src, dst)

                try:
                    txt = txt.encode("ascii")
                except UnicodeEncodeError, err:
                    print err
                    print instruction, key
                    print repr(txt)
                    sys.exit()

                data[key] = txt
                key = None

    cpu6809data[instruction] = data

pprint(cpu6809data)


print " -- END -- "
