# encoding:utf8

"""
    DragonPy - Base Periphery
    =========================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
import six
xrange = six.moves.xrange

import sys
import threading
import time

try:
    # Python 3
    import queue
    import _thread
#    import http.client
except ImportError:
    # Python 2
    import Queue as queue
    import thread as _thread
#    import httplib

import logging

log = logging.getLogger(__name__)
from dragonpy.utils import pager



try:
    import tkinter # Python 3
except ImportError:
    try:
        import Tkinter as tkinter # Python 2
    except ImportError:
        log.critical("Error importing Tkinter!")
        tkinter = None



class PeripheryBase(object):
    INITAL_INPUT = None # For quick test

    def __init__(self, cfg, cpu, memory, display_queue=None, user_input_queue=None):
        self.cfg = cfg
        self.cpu = cpu
        self.memory = memory
        self.user_input_queue = user_input_queue
        self.display_queue = display_queue # Buffer for output from CPU

        self.running = True
        self.update_time = 0.1
        self.last_cpu_cycle_update = time.time()

        if self.INITAL_INPUT is not None:
            self.add_to_input_queue(self.INITAL_INPUT)

    def add_to_input_queue(self, txt):
        log.debug("Add %s to input queue.", repr(txt))
        for char in txt:
            self.user_input_queue.put(char)

    def exit(self):
        log.critical("Exit called in periphery.")
        self.running = False

    def mainloop(self, cpu):
        cpu.reset()
        max_ops = self.cfg.cfg_dict["max_ops"]
        if max_ops:
            log.critical("Running only %i ops!", max_ops)
            for __ in xrange(max_ops):
                cpu.get_and_call_next_op()
                if not (self.periphery.running and self.cpu.running):
                    break
            log.critical("Quit CPU after given 'max_ops' %i ops.", max_ops)
        else:
            while self.periphery.running and self.cpu.running:
                cpu.get_and_call_next_op()

        cpu.quit()
        self.periphery.exit()

    def add_output(self, text):
        raise NotImplementedError

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError
    def read_acia_status(self, cpu_cycles, op_address, address):
        raise NotImplementedError

    def read_acia_data(self, cpu_cycles, op_address, address):
        raise NotImplementedError
    def write_acia_data(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError


###############################################################################
# TKinter Base ################################################################
###############################################################################


class TkPeripheryBase(PeripheryBase):
    TITLE = "DragonPy - Base Tkinter Periphery"
    GEOMETRY = "+500+300"
    KEYCODE_MAP = {}
    ESC_KEYCODE = "\x03" # What keycode to send, if escape Key pressed?

    def __init__(self, cfg):
        super(TkPeripheryBase, self).__init__(cfg)
        assert tkinter is not None, "ERROR: Tkinter is not available!"
        self.root = tkinter.Tk()

        self.root.title(self.TITLE)
#         self.root.geometry() # '640x480+500+300') # X*Y + x/y-offset
        self.root.geometry(self.GEOMETRY) # Change initial position

        # http://www.tutorialspoint.com/python/tk_text.htm
        self.text = tkinter.Text(
            self.root,
            height=20, width=80,
            state=tkinter.DISABLED # FIXME: make textbox "read-only"
        )
        scollbar = tkinter.Scrollbar(self.root)
        scollbar.config(command=self.text.yview)

        self.text.config(
            background="#08ff08", # nearly green
            foreground="#004100", # nearly black
            font=('courier', 11, 'bold'),
#            yscrollcommand=scollbar.set, # FIXME
        )

        scollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        self.text.pack(side=tkinter.LEFT, fill=tkinter.Y)

        self.root.bind("<Return>", self.event_return)
        self.root.bind("<Escape>", self.from_console_break)
        self.root.bind('<Control-c>', self.copy_to_clipboard)
        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<Destroy>", self.destroy)

        self.root.update()
        self.update_thread = None

    def event_return(self, event):
#        log.critical("ENTER: add \\n")
        self.user_input_queue.put("\n")

    def from_console_break(self, event):
        log.critical("from_console_break(): Add %r to input queue", self.ESC_KEYCODE)
        self.user_input_queue.put(self.ESC_KEYCODE)

    def copy_to_clipboard(self, event):
        log.critical("Copy to clipboard")
        text = self.text.get("1.0", tkinter.END)
        print(text)
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def event_key_pressed(self, event):
        keycode = event.keycode
        char = event.char
        log.critical("keycode %s - char %s", keycode, repr(char))
        if char:
            char = char.upper()
        elif keycode in self.KEYCODE_MAP:
            char = chr(self.KEYCODE_MAP[keycode])
            log.critical("keycode %s translated to: %s", keycode, repr(char))
        else:
            log.critical("Ignore input, doesn't send to CPU.")
            return

        log.debug("Send %s", repr(char))
        self.user_input_queue.put(char)

    def exit(self, msg):
        log.critical(msg)
        self.root.quit()
        super(TkPeripheryBase, self).exit()

    def destroy(self, event=None):
        self.exit("Tk window closed.")

    STATE = 0
    LAST_INPUT = ""
    def write_acia_data(self, cpu_cycles, op_address, address, value):
        log.debug("%04x| (%i) write to ACIA-data value: $%x (dez.: %i) ASCII: %r" % (
            op_address, cpu_cycles, value, value, chr(value)
        ))
        if value == 0x8: # Backspace
            self.text.config(state=tkinter.NORMAL)
            # delete last character
            self.text.delete("%s - 1 chars" % tkinter.INSERT, tkinter.INSERT)
            self.text.config(state=tkinter.DISABLED) # FIXME: make textbox "read-only"
            return

        super(TkPeripheryBase, self).write_acia_data(cpu_cycles, op_address, address, value)

    def _new_output_char(self, char):
        """ insert in text field """
        self.text.config(state=tkinter.NORMAL)
        self.text.insert("end", char)
        self.text.see("end")
        self.text.config(state=tkinter.DISABLED)

    def add_input_interval(self, cpu_process):
        if not cpu_process.is_alive():
            self.exit("CPU process is not alive.")

        while True:
            try:
                char = self.display_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self._new_output_char(char)

        self.root.after(100, self.add_input_interval, cpu_process)

    def mainloop(self, cpu_process):
        log.critical("Tk mainloop started.")
        self.add_input_interval(cpu_process)
        self.root.mainloop()
        log.critical("Tk mainloop stopped.")


###############################################################################
# Console Base ################################################################
###############################################################################


class InputPollThread(threading.Thread):
    def __init__ (self, cpu_process, user_input_queue):
        super(InputPollThread, self).__init__(name="InputThread")
        self.cpu_process = cpu_process
        self.user_input_queue = user_input_queue
        self.check_cpu_interval(cpu_process)

    def check_cpu_interval(self, cpu_process):
        """
        work-a-round for blocking input
        """
        try:
#            log.critical("check_cpu_interval()")
            if not cpu_process.is_alive():
                log.critical("raise SystemExit, because CPU is not alive.")
                _thread.interrupt_main()
                raise SystemExit("Kill pager.getch()")
        except KeyboardInterrupt:
            _thread.interrupt_main()
        else:
            t = threading.Timer(1.0, self.check_cpu_interval, args=[cpu_process])
            t.start()

    def _run(self):
        while self.cpu_process.is_alive():
            char = pager.getch() # Important: It blocks while waiting for a input
            if char == "\n":
                self.user_input_queue.put("\r")

            char = char.upper()
            self.user_input_queue.put(char)

    def run(self):
        log.critical("InputPollThread.run() start")
        try:
            self._run()
        except KeyboardInterrupt:
            _thread.interrupt_main()
        log.critical("InputPollThread.run() ends, because CPU not alive anymore.")


class ConsolePeripheryBase(PeripheryBase):
    def new_output_char(self, char):
        sys.stdout.write(char)
        sys.stdout.flush()

    def mainloop(self, cpu_process):
        log.critical("ConsolePeripheryBase.mainloop() start")
        input_thread = InputPollThread(cpu_process, self.user_input_queue)
        input_thread.deamon = True
        input_thread.start()


###############################################################################
# Unittest Base ###############################################################
###############################################################################


class PeripheryUnittestBase(object):
    def __init__(self, cfg, cpu, memory, display_queue, user_input_queue):
        self.cfg = cfg
        self.cpu = cpu
        self.display_queue = display_queue
        self.user_input_queue = user_input_queue

    def setUp(self):
        self.user_input_queue.queue.clear()
        self.display_queue.queue.clear()
        self.old_columns = None
        self.output_lines = [""] # for unittest run_until_OK()
        self.display_buffer = {} # for striped_output()

    def _new_output_char(self, char):
#        sys.stdout.write(char)
#        sys.stdout.flush()
        self._out_buffer += char
        if char == "\n":
            self.output_lines.append(self._out_buffer)
            self._out_buffer = ""

    def write_acia_data(self, cpu_cycles, op_address, address, value):
        raise
        super(PeripheryUnittestBase, self).write_acia_data(cpu_cycles, op_address, address, value)

        while True:
            try:
                char = self.display_queue.get(block=False)
            except queue.Empty:
                break
            else:
                self._new_output_char(char)
