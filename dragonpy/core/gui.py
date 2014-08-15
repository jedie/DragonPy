#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Queue
import Tkinter
import os
import sys
import time
import tkMessageBox

from basic_editor.editor import EditorWindow

from dragonlib.utils.logging_utils import log

from dragonpy.Dragon32 import dragon_charmap
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont


class MC6847_TextModeCanvas(object):
    """
    MC6847 Video Display Generator (VDG) in Alphanumeric Mode.
    This display mode consumes 512 bytes of memory and is a 32 character wide screen with 16 lines.

    Here we only get the "write into Display RAM" information from the CPU-Thread
    from display_queue.

    The Display Tkinter.Canvas() which will be filled with Tkinter.PhotoImage() instances.
    Every displayed character is a Tkinter.PhotoImage()
    """
    def __init__(self, root):
        self.rows = 32
        self.columns = 16

        scale_factor = 2  # scale the complete Display/Characters
        self.tk_font = TkFont(CHARS_DICT, scale_factor)  # to generate PhotoImage()

        self.total_width = self.tk_font.width_scaled * self.rows
        self.total_height = self.tk_font.height_scaled * self.columns

        self.canvas = Tkinter.Canvas(root,
            width=self.total_width,
            height=self.total_height,
            bd=0, # no border
            highlightthickness=0, # no highlight border
            bg="#ff0000",
        )

        # Contains the map from Display RAM value to char/color:
        self.charmap = get_charmap_dict()

        # Cache for the generated Tkinter.PhotoImage() in evry char/color combination:
        self.image_cache = {}

        # Tkinter.PhotoImage() IDs for image replace with canvas.itemconfigure():
        self.images_map = {}

        # Create all charachter images on the display and fill self.images_map:
        self.init_img = self.tk_font.get_char(char="?", color=dragon_charmap.INVERTED)
        for row in xrange(self.rows + 1):
            for column in xrange(self.columns + 1):
                x = self.tk_font.width_scaled * row
                y = self.tk_font.height_scaled * column
                image_id = self.canvas.create_image(x, y,
                    image=self.init_img,
                    state="normal",
                    anchor=Tkinter.NW  # NW == NorthWest
                )
#                 log.critical("Image ID: %s at %i x %i", image_id, x, y)
                self.images_map[(x, y)] = image_id

    def write_byte(self, cpu_cycles, op_address, address, value):
        #         log.critical(
        #             "%04x| *** Display write $%02x ***%s*** %s at $%04x",
        #             op_address, value, repr(char), color, address
        #         )

        try:
            image = self.image_cache[value]
        except KeyError:
            # Generate a Tkinter.PhotoImage() for the requested char/color
            char, color = self.charmap[value]
            image = self.tk_font.get_char(char, color)
            self.image_cache[value] = image

        position = address - 0x400
        column, row = divmod(position, self.rows)
        x = self.tk_font.width_scaled * row
        y = self.tk_font.height_scaled * column

#         log.critical("replace image %s at %i x %i", image, x, y)
        image_id = self.images_map[(x, y)]
        self.canvas.itemconfigure(image_id, image=image)


class DragonTkinterGUI(object):
    """
    The complete Tkinter GUI window
    """
    def __init__(self, cfg, display_queue, user_input_queue, cpu_status_queue, request_comm):
        self.cfg = cfg

        # Queue which contains "write into Display RAM" information
        # for render them in MC6847_TextModeCanvas():
        self.display_queue = display_queue

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        # LifoQueue filles in CPU Thread with CPU-Cycles information:
        self.cpu_status_queue = cpu_status_queue

        self.request_comm = request_comm

        self.last_cpu_cycles = 0
        self.last_cpu_cycle_update = time.time()

        self.root = Tkinter.Tk(className="DragonPy")
        machine_name = self.cfg.MACHINE_NAME
        self.root.title(
            "%s - Text Display 32 columns x 16 rows" % machine_name)

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        self.display = MC6847_TextModeCanvas(self.root)
        self.display.canvas.grid(row=0, column=0, columnspan=2)  # , rowspan=2)

        self.status = Tkinter.StringVar()
        self.status_widget = Tkinter.Label(
            self.root, textvariable=self.status, text="Info:", borderwidth=1)
        self.status_widget.grid(row=1, column=0, columnspan=2)

        menubar = Tkinter.Menu(self.root)

        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Tkinter.Menu(menubar, tearoff=0)
#        editmenu.add_command(label="load BASIC program", command=self.load_program)
#        editmenu.add_command(label="dump BASIC program", command=self.dump_program)
        editmenu.add_command(label="open", command=self.open_basic_editor)
        menubar.add_cascade(label="BASIC editor", menu=editmenu)

        # help menu
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        menubar.add_cascade(label="help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)
        self.root.update()

        self.editor_content = None
        self._editor_window = None

    def open_basic_editor(self):
        self._editor_window = EditorWindow(self.cfg, self.root, self.request_comm)

    def dump_rnd(self):
        start_addr = 0x0019
        end_addr = 0x0020
        dump, start_addr, end_addr = self.request_comm.request_memory_dump(
#            start_addr=0x0115, end_addr=0x0119 # RND seed
            start_addr, end_addr
        )
        def format_dump(dump, start_addr, end_addr):
            lines = []
            for addr, value in zip(xrange(start_addr, end_addr + 1), dump):
                log.critical("$%04x: $%02x (dez.: %i)", addr, value, value)
                lines.append("$%04x: $%02x (dez.: %i)" % (addr, value, value))
            return lines
        lines = format_dump(dump, start_addr, end_addr)
        tkMessageBox.showinfo("TODO", "dump_program:\n%s" % "\n".join(lines))

    def menu_event_about(self):
        tkMessageBox.showinfo("DragonPy",
            "DragonPy the OpenSource emulator written in python.\n"
            "more info: https://github.com/jedie/DragonPy"
        )

    def menu_event_help(self):
        tkMessageBox.showinfo("Help",
            "Please read the README:"
            "https://github.com/jedie/DragonPy#readme"
        )

    def exit(self):
        log.critical("DragonTkinterGUI.exit()")
        try:
            self.root.destroy()
        except:
            pass
        super(DragonTkinterGUI, self).exit()

    def paste_clipboard(self, event):
        """
        Send the clipboard content as user input to the CPU.
        """
        log.critical("paste clipboard")
        clipboard = self.root.clipboard_get()
        for line in clipboard.splitlines():
            log.critical("paste line: %s", repr(line))
            for char in line:
                self.user_input_queue.put(char)
            self.user_input_queue.put("\r")

    def event_key_pressed(self, event):
        char_or_code = event.char or event.keycode
        self.user_input_queue.put(char_or_code)

    def display_cpu_status_interval(self, interval):
        """
        Update the 'cycles/sec' in the GUI
        """
        try:
            cycles = self.cpu_status_queue.get(block=False)
        except Queue.Empty:
            log.critical("no new cpu_status_queue entry")
            pass
        else:
            new_cycles = cycles - self.last_cpu_cycles
            duration = time.time() - self.last_cpu_cycle_update
            self.last_cpu_cycles = cycles
            self.last_cpu_cycle_update = time.time()
            cycles_per_second = int(new_cycles / duration)

#             msg = "%i cycles/sec - Dragon ~895.000cycles/s (%i cycles in last %0.1fs)" % (
#                 cycles_per_second, new_cycles, duration
#             )
            msg = "%d cycles/sec (Dragon 32 == 895.000cycles/sec)" % cycles_per_second
#             log.critical(msg)
            self.status.set(msg)
            self.root.update()

        self.root.after(interval, self.display_cpu_status_interval, interval)

    def display_queue_interval(self, interval):
        """
        consume all exiting "display RAM write" queue items and render them.
        """
        max_time = time.time() + 0.25
        while True:
            try:
                cpu_cycles, op_address, address, value = self.display_queue.get_nowait()
            except Queue.Empty:
                #                 log.critical("display_queue empty -> exit loop")
                break
#                 log.critical(
#                     "call display.write_byte() (display_queue._qsize(): %i)",
#                     self.display_queue._qsize()
#                 )
            self.display.write_byte(cpu_cycles, op_address, address, value)
            if time.time() > max_time:
                log.critical("Abort display_queue_interval() loop.")
                break
#                 self.root.update()
#                 self.root.after_idle(self.display_queue_interval, interval)
#                 return

#         log.critical(
#             "exit display_queue_interval (display_queue._qsize(): %i)",
#             self.display_queue._qsize()
#         )
        self.root.after(interval, self.display_queue_interval, interval)

    def mainloop(self):
        log.critical("Start display_queue_interval()")
        self.display_queue_interval(interval=50)

        log.critical("Start display_cpu_status_interval()")
        self.display_cpu_status_interval(interval=1000)

        log.critical("Start root.mainloop()")
        self.root.mainloop()
        log.critical("root.mainloop() has quit!")


def test_run_direct():
    import subprocess
    cmd_args = [
        sys.executable,
        #         "/usr/bin/pypy",
        os.path.join("..",
            "Dragon32_test.py"
#             "Dragon64_test.py"
        ),
    ]
    print "Startup CLI with: %s" % " ".join(cmd_args[1:])
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    #     test_run_cli()
    test_run_direct()