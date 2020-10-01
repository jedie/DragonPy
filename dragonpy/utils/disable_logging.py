#!/usr/bin/env python

"""
    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


import os


if __name__ == "__main__":
    # sourcefile = r"../cpu6809.py"
    sourcefile = r"../DragonPy.py"
    # sourcefile = r"../components/memory.py"
    # sourcefile = r"../cpu_utils/MC6809_registers.py"
    # sourcefile = r"../sbc09/periphery.py"

    sourcefile_bak = sourcefile + ".bak"
    temp_file = sourcefile + ".new"

    in_log = 0

    with open(sourcefile, "r") as infile:
        with open(temp_file, "w") as outfile:
            for line in infile:
                #             print line
                if not line.strip().startswith("#"):
                    if in_log or "log." in line:
                        line = f"#{line}"
                        in_log += line.count("(")
                        in_log -= line.count(")")

                outfile.write(line)

    print(f"{temp_file!r} written.")

    print(f"rename {sourcefile!r} to {sourcefile_bak!r}")
    os.rename(sourcefile, sourcefile_bak)

    print(f"rename {temp_file!r} to {sourcefile!r}")
    os.rename(temp_file, sourcefile)

    print("\n --- END --- ")
