#!/usr/bin/env python
# coding: utf-8

"""
    latex2creole
    ~~~~~~~~~~~~

    Hacked script to convert a LaTeX file into creole markup.

    Note:
        Some hand-editing is needed.

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import sys

sourcefile = r"sbc09/sbc09.tex"
destination = r"sbc09.creole"


HEADLINES = (
    r"\title{",
    r"\chapter{",
    r"\section{",
    r"\subsection{",
)
SKIPS = (
    r"\begin",
    r"\end",
    r"\document",
    r"\maketitle",
    r"\tableofcontents",
    "\\def\\",
)

in_list = 0

def should_skip(line):
    for skip in SKIPS:
        if line.startswith(skip):
            return True


with open(sourcefile, "r") as infile:
    with open(destination, "w") as outfile:
        for line in infile:
            # ~ print line

            line = line.strip()

            if line.startswith(r"\begin{itemize}"):
                in_list += 1
                continue
            if line.startswith(r"\end{itemize}"):
                in_list -= 1
                if in_list == 0:
                    outfile.write("\n")
                continue

            if in_list:
                if line.startswith(r"\item"):
                    line = "\n%s%s" % ("*"*in_list, line[5:])
                outfile.write(line)
                continue

            if line == r"\begin{verbatim}":
                line = "{{{"
            elif line == r"\end{verbatim}":
                line = "}}}"

            if should_skip(line):
                continue

            for no, prefix in enumerate(HEADLINES, 1):
                if line.startswith(prefix):
                    line = line.replace("{\\tt ", "").replace("}", "")
                    line = line.split("{", 1)[1].replace("{", "").replace("}", "")
                    line = "\n%(m)s %(l)s %(m)s\n" % {
                        "m": "="*no,
                        "l": line
                    }
                    break

            if line.startswith(r"\item["):
                item, txt = line[6:].split("]")
                item = item.strip()
                txt = txt.strip()
                line = "** %s **\n%s" % (item, txt)

            if "{\\tt" in line:
                line = line.replace("{\\tt ", "{{{").replace("}", "}}}")
            if "{\\em" in line:
                line = line.replace("{\\em ", "{{{").replace("}", "}}}")

            line = line.replace("\\", "")

            print(line)
            line += "\n"
            outfile.write(line)
