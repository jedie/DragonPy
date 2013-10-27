
"""
    Hacked script to create a *short* trace
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    commandline output e.g.:

$ python create_trace.py
Welcome to BUGGY version 1.0
r
X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00
P=0400 NEG   $00
r
X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00
P=0400 NEG   $00
r
X=0000 Y=0000 U=0000 S=0400 A=00 B=00 D=00 C=00
P=0400 NEG   $00
x
Unknown command
"""

import time
import subprocess

cmd_args = [
    "./v09", "-t", "../v09trace.txt"
]
p=subprocess.Popen(cmd_args,
    cwd="sbc09",
    stdin=subprocess.PIPE,
    #~ stdout=subprocess.PIPE
)
p.stdin.write(
    "r\n" # Register display
    "r\n" # Register display
    "r\n" # Register display

    # FIXME: Doesn't work:
    "\x1d" # escape character
    "x\n" # exit
)
p.stdin.flush()

# work-a-round:
time.sleep(1)
p.kill()
