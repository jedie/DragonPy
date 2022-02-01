#!/usr/bin/env python3

"""
    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import os
import socket
import subprocess
import sys
import threading
import time


GDB_IP = "127.0.0.1"
GDB_PORT = 65520


def start_xroar(xroar_args, cwd):
    """
    http://www.6809.org.uk/xroar/doc/xroar.shtml#Debugging
    """
    args = ["xroar", "-gdb",
            "-gdb-ip", GDB_IP,
            "-gdb-port", str(GDB_PORT),
            ]
    args += xroar_args

    sys.stderr.write(f"Start Xroar in {cwd!r} with: '{' '.join([str(i) for i in args])}'\n")
    xroar_process = subprocess.Popen(args=args, cwd=cwd)
    return xroar_process


class XroarGDB:
    """
    https://github.com/jedie/XRoar/blob/master/src/gdb.c
    """

    def __init__(self):
        sys.stderr.write(f"Connect to {GDB_IP}:{GDB_PORT} ...")
        self.s = socket.socket(
            family=socket.AF_INET,
            #             family=socket.AF_UNSPEC,
            type=socket.SOCK_STREAM,
            proto=0
        )
        self.s.connect((GDB_IP, GDB_PORT))
        sys.stderr.write("connected.\n")

        self.running = True
        self.print_recv_interval()

    def send(self, txt):
        sys.stderr.write(f"Send {txt!r} ...")
        self.s.sendall(txt)
        sys.stderr.write("done.\n")

    def print_recv_interval(self):
        print(f"recv: {repr(self.s.recv(1024))}")
        if self.running:
            t = threading.Timer(0.5, self.print_recv_interval)
            t.deamon = True
            t.start()


if __name__ == '__main__':
    xroar_process = start_xroar(
        xroar_args=[
            "-keymap", "de",
            "-kbd-translate"
        ],
        cwd=os.path.expanduser("~/xroar")
    )
    time.sleep(2)

    try:
        xroar_gdb = XroarGDB()
        xroar_gdb.send("g")
        time.sleep(1)
        xroar_gdb.send("p")
        time.sleep(1)
        xroar_gdb.send("g")
        time.sleep(1)
    finally:
        print("tear down")
        try:
            xroar_gdb.running = False
            xroar_gdb.s.close()
        except BaseException:
            pass

    time.sleep(1)
    print(" --- END --- ")
