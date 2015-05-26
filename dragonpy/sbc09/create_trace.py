
"""
    Hacked script to create a *short* trace
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Create v09 trace simmilar to XRoar one
    and add CC and Memory-Information.

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from functools import partial
import os
import subprocess
import sys
import tempfile
import threading
import time

from MC6809.components.MC6809data.MC6809_data_utils import MC6809OP_DATA_DICT
from dragonpy.utils.humanize import cc_value2txt
from dragonpy.sbc09.mem_info import SBC09MemInfo


def proc_killer(proc, timeout):
    time.sleep(timeout)
    if proc.poll() is None:
        print("kill process after %fsec timeout..." % timeout)
        proc.kill()

def subprocess2(timeout=3, **kwargs):
    print("Start: %s" % " ".join(kwargs["args"]))
    proc = subprocess.Popen(**kwargs)
    threading.Thread(target=partial(proc_killer, proc, timeout)).start()
    return proc


def create_v09_trace(commands, timeout, max_newlines=None):
    trace_file = tempfile.NamedTemporaryFile()

    proc = subprocess2(timeout=timeout,
        args=("./v09", "-t", trace_file.name),
        cwd="sbc09",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    print("Started with timeout: %fsec." % timeout)

    commands = "".join(["%s\n" % cmd for cmd in commands])
    print("Commands: %r" % commands)
    proc.stdin.write(commands)
    proc.stdin.flush()

    print()
    print("Process output:")
    print("-"*79)
    newline_count = 0
    line_buffer = ""
    while proc.poll() is None:
        char = proc.stdout.read(1)
        if char == "\n":
            print(line_buffer)
            newline_count += 1
            if max_newlines is not None and newline_count >= max_newlines:
                print("Aboad process after %i newlines." % newline_count)
                proc.kill()
                break
            line_buffer = ""
    #    elif IS_WIN and char == "\r":
    #        continue
        else:
            line_buffer += char

    print("-"*79)
    print("Process ends and output %i newlines." % newline_count)
    print()

    result = trace_file.read()
    trace_file.close()
    return result


def reformat_v09_trace(raw_trace, max_lines=None):
    """
    reformat v09 trace simmilar to XRoar one
    and add CC and Memory-Information.

    Note:
        v09 traces contains the register info line one trace line later!
        We reoder it as XRoar done: addr+Opcode with resulted registers
    """
    print()
    print("Reformat v09 trace...")
    mem_info = SBC09MemInfo(sys.stderr)

    result = []
    next_update = time.time() + 1
    old_line = None
    for line_no, line in enumerate(raw_trace.splitlines()):
        if max_lines is not None and line_no >= max_lines:
            msg = "max lines %i arraived -> Abort." % max_lines
            print(msg)
            result.append(msg)
            break

        if time.time() > next_update:
            print("reformat %i trace lines..." % line_no)
            next_update = time.time() + 1

        try:
            pc = int(line[3:7], 16)
            op_code = int(line[10:15].strip().replace(" ", ""), 16)
            cc = int(line[57:59], 16)
            a = int(line[46:48], 16)
            b = int(line[51:53], 16)
            x = int(line[18:22], 16)
            y = int(line[25:29], 16)
            u = int(line[32:36], 16)
            s = int(line[39:43], 16)
        except ValueError as err:
            print("Error in line %i: %s" % (line_no, err))
            print("Content on line %i:" % line_no)
            print("-"*79)
            print(repr(line))
            print("-"*79)
            continue

        op_data = MC6809OP_DATA_DICT[op_code]
        mnemonic = op_data["mnemonic"]

        cc_txt = cc_value2txt(cc)
        mem = mem_info.get_shortest(pc)
#        print op_data

        register_line = "cc=%02x a=%02x b=%02x dp=?? x=%04x y=%04x u=%04x s=%04x| %s" % (
            cc, a, b, x, y, u, s, cc_txt
        )
        if old_line is None:
            line = "(init with: %s)" % register_line
        else:
            line = old_line % register_line

        old_line = "%04x| %-11s %-27s %%s | %s" % (
            pc, "%x" % op_code, mnemonic,
            mem
        )

        result.append(line)

    print("Done, %i trace lines converted." % line_no)
#    print raw_trace[:700]
    return result


if __name__ == '__main__':
    commands = [
        "H100+F", # Calculate simple expression in hex with + and -

#        "r", # Register display
#        "ss", # generate Motorola S records

#        "XL400", # Load binary data using X-modem protocol at $400
#        "\x1d" # escape character
#        "ubasic", # load the binary file "basic" at address $400

#        "UE400,20" # Diassemble first 32 bytes of monitor program.

        #"\x1d" # escape character FIXME: Doesn't work :(
        #"x", # exit
    ]

    raw_trace = create_v09_trace(commands,
        timeout=0.1,
        max_newlines=3 # Close process after X newlines
#        max_newlines=None # No limit
    )
#    print raw_trace
    trace = reformat_v09_trace(raw_trace,
#        max_lines=15
        max_lines=None # All lines
    )
#    print "\n".join(trace)

    out_filename = os.path.abspath("../v09_trace.txt")
    with open(out_filename, "w") as f:
        f.write("\n".join(trace))

    print("Trace file %r created." % out_filename)
    print(" --- END --- ")

