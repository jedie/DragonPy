# encoding:utf8

"""
    DragonPy - Base Periphery
    =========================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import time
import logging
import sys
import httplib

try:
    import Tkinter
except Exception, err:
    print "Error importing Tkinter: %s" % err
    Tkinter = None


log = logging.getLogger("DragonPy.components.Periphery")


class PeripheryBase(object):
    INITAL_INPUT = None # For quick test

    def __init__(self, cfg):
        self.cfg = cfg
        self.running = True

        self.user_input_queue = Queue.Queue() # Buffer for input to send back to the CPU
        self.output_queue = Queue.Queue() # Buffer with content from the CPU to display

        self.update_time = 0.1
        self.last_update = time.time()

        # Set by subclass
        self.read_address2func_map = None
        self.write_address2func_map = None

        if self.INITAL_INPUT is not None:
            self.add_to_input_queue(self.INITAL_INPUT)

    def add_to_input_queue(self, txt):
        for char in txt:
            self.user_input_queue.put(char)

    def request_cpu(self, url):
#         log.critical(
        log.error(
            "request %s:%s%s", self.cfg.CPU_CONTROL_ADDR, self.cfg.CPU_CONTROL_PORT, url
        )
        conn = httplib.HTTPConnection(
            host=self.cfg.CPU_CONTROL_ADDR,
            port=self.cfg.CPU_CONTROL_PORT,
            timeout=1
        )
        conn.request("POST", url)
        try:
            response = conn.getresponse()
        except Exception, err:
            log.critical("Error request %s: %s", url, err)
        else:
            print response.status, response.reason

        log.error("FIXME: request_cpu in %s", __file__)

    def exit(self):
        self.running = False

        # FIXME: It doesn't work to request that CPU shutdown:
        #        will get timeouts
        self.request_cpu(url="/quit/")

        time.sleep(1) # Wait that CPU quit
        sys.exit(0)

    def activate_full_debug_logging(self):
        handler = logging.StreamHandler()
        handler.level = 5
        log.handlers = (handler,)
        log.critical("Activate full debug logging in %s!", __file__)
        self.request_cpu(url="/debug/")

    def read_byte(self, cpu_cycles, op_address, address):
        if not self.running:
            log.critical("Periphery.read_byte, but not running anymore.")
            return 0x0

#        log.debug(
#            "%04x| Periphery.read_byte from $%x (cpu_cycles: %i)",
#            op_address, address, cpu_cycles
#        )
        try:
            func = self.read_address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
#            log.debug("func: %s", func.__name__)
            byte = func(cpu_cycles, op_address, address)
#            log.debug("\tsend byte $%x back" % byte)
            return byte
    read_word = read_byte

    def write_byte(self, cpu_cycles, op_address, address, value):
#        log.debug(
#            "%04x| Periphery.write_byte $%x to $%x (cpu_cycles: %i)",
#            op_address, value, address, cpu_cycles
#        )
        try:
            func = self.write_address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
#            log.debug("func: %s", func.__name__)
            func(cpu_cycles, op_address, address, value)

    write_word = write_byte

    last_cycles_update = time.time()
    last_cycles = 0
    def update(self, cpu_cycles):
#         sys.stdout.write("u")
#         sys.stdout.flush()
        if self.cfg.display_cycle:
            duration = time.time() - self.last_cycles_update
            if duration >= 1:
                count = cpu_cycles - self.last_cycles
                log.critical("%.2f cycles/sec. (current cycle: %i)", float(count / duration), cpu_cycles)
                self.last_cycles = cpu_cycles
                self.last_cycles_update = time.time()

    def cycle(self, cpu_cycles, op_address):
#         sys.stdout.write("c")
#         sys.stdout.flush()
        if time.time() - self.last_update > self.update_time:
            self.last_update = time.time()
            self.update(cpu_cycles)
            return self.running # send pack if CPU quit

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError
    def read_acia_status(self, cpu_cycles, op_address, address):
        raise NotImplementedError

    def read_acia_data(self, cpu_cycles, op_address, address):
        raise NotImplementedError
    def write_acia_data(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError


class TkPeripheryBase(PeripheryBase):
    TITLE = "DragonPy - Base Tkinter Periphery"
    GEOMETRY = "+500+300"

    def __init__(self, cfg):
        super(TkPeripheryBase, self).__init__(cfg)
        self.root = Tkinter.Tk()
        self.root.title(self.TITLE)
#         self.root.geometry() # '640x480+500+300') # X*Y + x/y-offset
        self.root.geometry(self.GEOMETRY) # Change initial position

        # http://www.tutorialspoint.com/python/tk_text.htm
        self.text = Tkinter.Text(
            self.root,
            height=20, width=80,
            state=Tkinter.DISABLED # FIXME: make textbox "read-only"
        )
        scollbar = Tkinter.Scrollbar(self.root)
        scollbar.config(command=self.text.yview)

        self.text.config(
            background="#08ff08", # nearly green
            foreground="#004100", # nearly black
            font=('courier', 11, 'bold'),
            yscrollcommand=scollbar.set,
        )

        scollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.text.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

        self.root.bind("<Return>", self.event_return)
        self.root.bind("<Escape>", self.from_console_break)
        self.root.bind('<Control-c>', self.copy_to_clipboard)
        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<Destroy>", self.destroy)

        self.root.update()

    def event_return(self, event):
#        log.critical("ENTER: add \\n")
        self.user_input_queue.put("\n")

    def from_console_break(self, event):
#        log.critical("BREAK: add 0x03")
        # dc61 81 03              LA3C2     CMPA #3             BREAK KEY?
        self.user_input_queue.put("\x03")

    def copy_to_clipboard(self, event):
        log.critical("Copy to clipboard")
        text = self.text.get("1.0", Tkinter.END)
        print text
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def event_key_pressed(self, event):
        log.critical("keycode %s", repr(event.keycode))
        char = event.char
        log.error("char %s", repr(char))
        if char:
            char = char.upper()
            log.error("Send %s", repr(char))
            self.user_input_queue.put(char)

    def destroy(self, event=None):
        """
        FIXME: How destroy the CPU process?
        """
        log.critical("Tk window closed.")
        self.root.destroy()
        self.exit()

    STATE = 0
    LAST_INPUT = ""
    def write_acia_data(self, cpu_cycles, op_address, address, value):
#        log.error("%04x| (%i) write to ACIA-data value: $%x (dez.: %i) ASCII: %r" % (
#            op_address, cpu_cycles, value, value, chr(value)
#        ))
        if value == 0x8: # Backspace
            self.text.config(state=Tkinter.NORMAL)
            # delete last character
            self.text.delete("%s - 1 chars" % Tkinter.INSERT, Tkinter.INSERT)
            self.text.config(state=Tkinter.DISABLED) # FIXME: make textbox "read-only"
            return

        super(TkPeripheryBase, self).write_acia_data(cpu_cycles, op_address, address, value)

    def update(self, cpu_cycles):
        if not self.output_queue.empty():
            text_buffer = []
            while not self.output_queue.empty():
                text_buffer.append(self.output_queue.get())

            text = "".join(text_buffer)

            # Duplicate output
            sys.stdout.write(text)
            sys.stdout.flush()

            # insert in text field
            self.text.config(state=Tkinter.NORMAL)
            self.text.insert("end", text)
            self.text.see("end")
            self.text.config(state=Tkinter.DISABLED)

        self.root.update()
        return super(TkPeripheryBase, self).update(cpu_cycles)
