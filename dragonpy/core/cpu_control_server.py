#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - CPU control http server
    ==================================

    TODO: Use bottle!

    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.

    Based on:
        * ApplyPy by James Tauber (MIT license)
        * XRoar emulator by Ciaran Anscomb (GPL license)
    more info, see README
"""

from __future__ import absolute_import, division, print_function
from dragonlib.utils import six
xrange = six.moves.xrange

try:
    from http.server import BaseHTTPRequestHandler # Python 3
except ImportError:
    from BaseHTTPServer import BaseHTTPRequestHandler # Python 2

import json
import logging
import os
import re
import select
import sys
import threading
import traceback

import logging

log=logging.getLogger(__name__)


class ControlHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server, cpu):
        log.error("ControlHandler %s %s %s", request, client_address, server)
        self.cpu = cpu

        self.get_urls = {
            r"/disassemble/(\s+)/$": self.get_disassemble,
            r"/memory/(\s+)(-(\s+))?/$": self.get_memory,
            r"/memory/(\s+)(-(\s+))?/raw/$": self.get_memory_raw,
            r"/status/$": self.get_status,
            r"/$": self.get_index,
        }

        self.post_urls = {
            r"/memory/(\s+)(-(\s+))?/$": self.post_memory,
            r"/memory/(\s+)(-(\s+))?/raw/$": self.post_memory_raw,
            r"/quit/$": self.post_quit,
            r"/reset/$": self.post_reset,
            r"/debug/$": self.post_debug,
        }

        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def log_message(self, format, *args):
        msg = "%s - - [%s] %s\n" % (
            self.client_address[0], self.log_date_time_string(), format % args
        )
        log.critical(msg)

    def dispatch(self, urls):
        for r, f in list(urls.items()):
            m = re.match(r, self.path)
            if m is not None:
                log.critical("call %s", f.__name__)
                try:
                    f(m)
                except Exception as err:
                    txt = traceback.format_exc()
                    self.response_500("Error call %r: %s" % (f.__name__, err), txt)
                return
        else:
            self.response_404("url %r doesn't match any urls" % self.path)

    def response(self, s, status_code=200):
        log.critical("send %s response", status_code)
        self.send_response(status_code)
        self.send_header("Content-Length", str(len(s)))
        self.end_headers()
        self.wfile.write(s)

    def response_html(self, headline, text=""):
        html = (
            "<!DOCTYPE html><html><body>"
            "<h1>%s</h1>"
            "%s"
            "</body></html>"
        ) % (headline, text)
        self.response(html)

    def response_404(self, txt):
        log.error(txt)
        html = (
            "<!DOCTYPE html><html><body>"
            "<h1>DragonPy - 6809 CPU control server</h1>"
            "<h2>404 - Error:</h2>"
            "<p>%s</p>"
            "</body></html>"
        ) % txt
        self.response(html, status_code=404)

    def response_500(self, err, tb_txt):
        log.error(err, tb_txt)
        html = (
            "<!DOCTYPE html><html><body>"
            "<h1>DragonPy - 6809 CPU control server</h1>"
            "<h2>500 - Error:</h2>"
            "<p>%s</p>"
            "<pre>%s</pre>"
            "</body></html>"
        ) % (err, tb_txt)
        self.response(html, status_code=500)

    def do_GET(self):
        log.critical("do_GET(): %r", self.path)
        self.dispatch(self.get_urls)

    def do_POST(self):
        log.critical("do_POST(): %r", self.path)
        self.dispatch(self.post_urls)

    def get_index(self, m):
        self.response_html(
            headline="DragonPy - 6809 CPU control server",
            text=(
            "<p>Example urls:"
            "<ul>"
            '<li>CPU status:<a href="/status/">/status/</a></li>'
            '<li>6809 interrupt vectors memory dump:'
            '<a href="/memory/fff0-ffff/">/memory/fff0-ffff/</a></li>'
            '</ul>'
            '<form action="/quit/" method="post">'
            '<input type="submit" value="Quit CPU">'
            '</form>'
        ))

    def get_disassemble(self, m):
        addr = int(m.group(1))
        r = []
        n = 20
        while n > 0:
            dis, length = self.disassemble.disasm(addr)
            r.append(dis)
            addr += length
            n -= 1
        self.response(json.dumps(r))

    def get_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        self.response("".join([chr(self.cpu.read_byte(x)) for x in xrange(addr, end + 1)]))

    def get_memory(self, m):
        addr = int(m.group(1), 16)
        e = m.group(3)
        if e is not None:
            end = int(e, 16)
        else:
            end = addr
        self.response(json.dumps(list(map(self.cpu.read_byte, list(range(addr, end + 1))))))

    def get_status(self, m):
        data = {
            "cpu": self.cpu.get_info,
            "cc": self.cpu.cc.get_info,
            "pc": self.cpu.program_counter.get(),
            "cycle_count": self.cpu.cycles,
        }
        log.critical("status dict: %s", repr(data))
        json_string = json.dumps(data)
        self.response(json_string)

    def post_memory(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_memory_raw(self, m):
        addr = int(m.group(1))
        e = m.group(3)
        if e is not None:
            end = int(e)
        else:
            end = addr
        data = self.rfile.read(int(self.headers["Content-Length"]))
        for i, a in enumerate(range(addr, end + 1)):
            self.cpu.write_byte(a, data[i])
        self.response("")

    def post_debug(self, m):
        handler = logging.StreamHandler()
        handler.level = 5
        log.handlers = (handler,)
        log.critical("Activate full debug logging in %s!", __file__)
        self.response("")

    def post_quit(self, m):
        log.critical("Quit CPU from controller server.")
        self.cpu.quit()
        self.response_html(headline="CPU running")

    def post_reset(self, m):
        self.cpu.reset()
        self.response_html(headline="CPU reset")


class ControlHandlerFactory:
    def __init__(self, cpu):
        self.cpu = cpu
    def __call__(self, request, client_address, server):
        return ControlHandler(request, client_address, server, self.cpu)


def control_server_thread(cpu, cfg, control_server):
    # FIXME: Refactor this!
    timeout = 1

    sockets = [control_server]
    rs, _, _ = select.select(sockets, [], [], timeout)
    for s in rs:
        if s is control_server:
            control_server._handle_request_noblock()
        else:
            pass

    if cpu.running:
        threading.Timer(interval=0.5,
            function=control_server_thread,
            args=(cpu, cfg, control_server)
        ).start()
    else:
        log.critical("Quit control server thread, because CPU doesn't run.")

def start_http_control_server(cpu, cfg):
    log.critical("TODO: What's with CPU control server???")
    return

    if not cfg.cfg_dict["use_bus"]:
        log.info("Don't init CPU control server, ok.")
        return None

    control_handler = ControlHandlerFactory(cpu)
    server_address = (cfg.CPU_CONTROL_ADDR, cfg.CPU_CONTROL_PORT)
    try:
        control_server = http.server.HTTPServer(server_address, control_handler)
    except:
        cpu.running = False
        raise
    url = "http://%s:%s" % server_address
    log.error("Start http control server on: %s", url)

    control_server_thread(cpu, cfg, control_server)


def test_run():
    print("test run...")
    import subprocess
    cmd_args = [sys.executable,
        os.path.join("..", "..", "DragonPy_CLI.py"),
#         "--verbosity=5",
#         "--verbosity=10", # DEBUG
#         "--verbosity=20", # INFO
#         "--verbosity=30", # WARNING
#         "--verbosity=40", # ERROR
        "--verbosity=50", # CRITICAL/FATAL
#         "--machine=sbc09",
        "--machine=Simple6809",
#         "--machine=Dragon32",
#         "--machine=Multicomp6809",
#         "--max=100000",
        "--display_cycle",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args).wait()

if __name__ == "__main__":
    test_run()
