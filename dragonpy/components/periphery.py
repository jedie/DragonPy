# encoding:utf8

"""
    DragonPy - Base Periphery
    =========================


    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import time
import sys
import httplib
import threading

try:
    import Tkinter
except Exception, err:
    print "Error importing Tkinter: %s" % err
    Tkinter = None

from dragonpy.utils.logging_utils import log


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

    def reset_vector(self, cpu_cycles, op_address, address):
        return self.cfg.RESET_VECTOR_VALUE

    def new_output_char(self, char):
        self.output_queue.put(char)

    def add_to_input_queue(self, txt):
        log.debug("Add %s to input queue.", repr(txt))
        for char in txt:
            self.user_input_queue.put(char)

    def request_cpu(self, url):
#         log.critical(
        log.debug(
            "request %s:%s%s", self.cfg.CPU_CONTROL_ADDR, self.cfg.CPU_CONTROL_PORT, url
        )
        conn = httplib.HTTPConnection(
            host=self.cfg.CPU_CONTROL_ADDR,
            port=self.cfg.CPU_CONTROL_PORT,
            timeout=1
        )
        try:
            conn.request("POST", url)
            response = conn.getresponse()
        except Exception, err:
            log.critical("Error request %s: %s", url, err)
        else:
            print response.status, response.reason

    def exit(self):
        log.critical("Exit called in periphery.")
        self.running = False
        self.request_cpu(url="/quit/")

    def read_byte(self, cpu_cycles, op_address, address):
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
        if not self.running:
            self.exit()
            return

        log.debug(
            "%04x| Periphery.write_byte $%x to $%x (cpu_cycles: %i)",
            op_address, value, address, cpu_cycles
        )
        try:
            func = self.write_address2func_map[address]
        except KeyError, err:
            msg = "TODO: read byte from $%x" % address
            log.error(msg)
            raise NotImplementedError(msg)
        else:
            log.debug("func: %s", func.__name__)
            func(cpu_cycles, op_address, address, value)

    write_word = write_byte

    def mainloop(self, cpu_process):
        raise NotImplementedError

    def write_acia_status(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError
    def read_acia_status(self, cpu_cycles, op_address, address):
        raise NotImplementedError

    def read_acia_data(self, cpu_cycles, op_address, address):
        raise NotImplementedError
    def write_acia_data(self, cpu_cycles, op_address, address, value):
        raise NotImplementedError



class TkUpdateThread(threading.Thread):
    """
    Wait for CPU/Memory bus write: Redirect write to periphery
    """
    def __init__ (self, periphery, cpu_process):
        super(TkUpdateThread, self).__init__()
        log.critical(" *** TkUpdateThread init *** ")
        self.periphery = periphery
        self.cpu_process = cpu_process
        self.running = True

    def run(self):
        log.critical(" *** TkUpdateThread.run() started. *** ")
        while self.periphery.running and self.cpu_process.is_alive():
            if not self.periphery.output_queue.empty():
                text_buffer = []
                while not self.periphery.output_queue.empty():
                    text_buffer.append(self.periphery.output_queue.get())

                text = "".join(text_buffer)

                # Duplicate output
                sys.stdout.write(text)
                sys.stdout.flush()

                # insert in text field
                self.periphery.text.config(state=Tkinter.NORMAL)
                self.periphery.text.insert("end", text)
                self.periphery.text.see("end")
                self.periphery.text.config(state=Tkinter.DISABLED)

        self.periphery.exit("Exit from TkUpdateThread.")
        log.critical(" *** TkUpdateThread.run() stopped. *** ")


class TkPeripheryBase(PeripheryBase):
    TITLE = "DragonPy - Base Tkinter Periphery"
    GEOMETRY = "+500+300"

    def __init__(self, cfg):
        super(TkPeripheryBase, self).__init__(cfg)
        assert Tkinter is not None, "ERROR: Tkinter can't be used, see import error above!"
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
        self.update_thread = None

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
        log.debug("char %s", repr(char))
        if char:
            char = char.upper()
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
            self.text.config(state=Tkinter.NORMAL)
            # delete last character
            self.text.delete("%s - 1 chars" % Tkinter.INSERT, Tkinter.INSERT)
            self.text.config(state=Tkinter.DISABLED) # FIXME: make textbox "read-only"
            return

        super(TkPeripheryBase, self).write_acia_data(cpu_cycles, op_address, address, value)

    def mainloop(self, cpu_process):
        log.critical("Tk mainloop started.")

        self.update_thread = TkUpdateThread(self, cpu_process)
        self.update_thread.start()

        self.root.mainloop()

        log.critical("Tk mainloop stopped.")
