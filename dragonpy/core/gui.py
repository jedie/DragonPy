#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import os
import sys
import time

from basic_editor.editor import EditorWindow
from dragonlib.utils.logging_utils import log
from dragonpy.Dragon32 import dragon_charmap
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.utils.humanize import locale_format_number


try:
    # Python 3
    import queue
    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import scrolledtext
except ImportError:
    # Python 2
    import Queue as queue
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext


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

        self.canvas = tkinter.Canvas(root,
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
        for row in range(self.rows + 1):
            for column in range(self.columns + 1):
                x = self.tk_font.width_scaled * row
                y = self.tk_font.height_scaled * column
                image_id = self.canvas.create_image(x, y,
                    image=self.init_img,
                    state="normal",
                    anchor=tkinter.NW  # NW == NorthWest
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


class BaseTkinterGUI(object):
    """
    The complete Tkinter GUI window
    """
    def __init__(self, cfg, display_queue, user_input_queue):
        self.cfg = cfg

        # Queue which contains "write into Display RAM" information
        # for render them in MC6847_TextModeCanvas():
        self.display_queue = display_queue

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        self.burst_count = 100
        self.cpu_after_id = None # Used to call CPU OP burst loop
        self.target_burst_duration = 0.1 # Duration how long should a CPU Op burst loop take

        self.init_statistics() # Called also after reset

        self.root = tkinter.Tk(className="DragonPy")
        self.root.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() * 0.1, self.root.winfo_screenheight() * 0.1
        ))

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        self.status = tkinter.StringVar(value="startup %s...\n" % self.cfg.MACHINE_NAME)
        self.status_widget = tkinter.Label(
            self.root, textvariable=self.status, text="Info:", borderwidth=1)
        self.status_widget.grid(row=1, column=0, columnspan=2)

        self.menubar = tkinter.Menu(self.root)

        filemenu = tkinter.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.exit)
        self.menubar.add_cascade(label="File", menu=filemenu)

        # 6809 menu
        self.cpu_menu = tkinter.Menu(self.menubar, tearoff=0)
        self.cpu_menu.add_command(label="pause", command=self.command_cpu_pause)
        self.cpu_menu.add_command(label="resume", command=self.command_cpu_pause, state=tkinter.DISABLED)
        self.cpu_menu.add_separator()
        self.cpu_menu.add_command(label="soft reset", command=self.command_cpu_soft_reset)
        self.cpu_menu.add_command(label="hard reset", command=self.command_cpu_hard_reset)
        self.menubar.add_cascade(label="6809", menu=self.cpu_menu)

        # help menu
        helpmenu = tkinter.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        self.menubar.add_cascade(label="help", menu=helpmenu)

    def init_statistics(self):
        self.last_op_count = 0
        self.last_cpu_cycles = 0
        self.cpu_cycles_update_interval = 1 # Fequency for update GUI status information
        self.next_cpu_cycle_update = time.time() + self.cpu_cycles_update_interval

    def menu_event_about(self):
        messagebox.showinfo("DragonPy",
            "DragonPy the OpenSource emulator written in python.\n"
            "more info: https://github.com/jedie/DragonPy"
        )

    def menu_event_help(self):
        messagebox.showinfo("Help",
            "Please read the README:"
            "https://github.com/jedie/DragonPy#readme"
        )

    def exit(self):
        log.critical("DragonTkinterGUI.exit()")
        try:
            self.root.destroy()
        except:
            pass

    #-----------------------------------------------------------------------------------------

    def status_paused(self):
        self.status.set("%s paused.\n" % self.cfg.MACHINE_NAME)

    def command_cpu_pause(self):
        if self.cpu_after_id is not None:
            # stop CPU
            self.root.after_cancel(self.cpu_after_id)
            self.cpu_after_id = None
            self.status_paused()
            self.cpu_menu.entryconfig(index=0, state=tkinter.DISABLED)
            self.cpu_menu.entryconfig(index=1, state=tkinter.NORMAL)
        else:
            # restart
            self.cpu_interval(interval=1)
            self.cpu_menu.entryconfig(index=0, state=tkinter.NORMAL)
            self.cpu_menu.entryconfig(index=1, state=tkinter.DISABLED)
            self.init_statistics() # Reset statistics

    def command_cpu_soft_reset(self):
        self.machine.cpu.reset()
        self.init_statistics() # Reset statistics

    def command_cpu_hard_reset(self):
        self.machine.hard_reset()
        self.init_statistics() # Reset statistics

    #-----------------------------------------------------------------------------------------

    def add_user_input(self, txt):
        for char in txt:
            self.user_input_queue.put(char)

    def wait_until_input_queue_empty(self):
        for count in range(1, 10):
            self.cpu_interval()
            if self.user_input_queue.empty():
                log.critical("user_input_queue is empty, after %i burst runs, ok.", count)
                if self.cpu_after_id is None:
                    self.status_paused()
                return
        if self.cpu_after_id is None:
            self.status_paused()
        log.critical("user_input_queue not empty, after %i burst runs!", count)

    def add_user_input_and_wait(self, txt):
        self.add_user_input(txt)
        self.wait_until_input_queue_empty()

    def paste_clipboard(self, event):
        """
        Send the clipboard content as user input to the CPU.
        """
        log.critical("paste clipboard")
        clipboard = self.root.clipboard_get()
        for line in clipboard.splitlines():
            log.critical("paste line: %s", repr(line))
            self.add_user_input(line + "\r")

    def event_key_pressed(self, event):
        char_or_code = event.char or event.keycode
        self.user_input_queue.put(char_or_code)

    def calc_new_count(self, burst_count, current_value, target_value):
        """
        >>> calc_new_count(burst_count=100, current_value=30, target_value=30)
        100
        >>> calc_new_count(burst_count=100, current_value=40, target_value=20)
        75
        >>> calc_new_count(burst_count=100, current_value=20, target_value=40)
        150
        """
        try:
            a = float(burst_count) / float(current_value) * target_value
        except ZeroDivisionError:
            return burst_count * 2
        return int(round((burst_count + a) / 2))

    def cpu_interval(self, interval=None):
#        log.critical("enter cpu interval")
        start_time = time.time()

        self.machine.run_cpu(self.burst_count)

        now = time.time()
        burst_duration = now - start_time

        # Calculate the burst_count new, to hit self.target_burst_duration
        self.burst_count = self.calc_new_count(self.burst_count,
            current_value=burst_duration,
            target_value=self.target_burst_duration,
        )
#        log.critical("burst duration: %.3f sec. - new burst count: %i Ops", burst_duration, burst_count)

        if now > self.next_cpu_cycle_update:

            duration = now - self.next_cpu_cycle_update + self.cpu_cycles_update_interval
            self.next_cpu_cycle_update = now + self.cpu_cycles_update_interval

            new_cycles = self.machine.cpu.cycles - self.last_cpu_cycles
            self.last_cpu_cycles = self.machine.cpu.cycles
            cycles_per_second = int(new_cycles / duration)

            new_ops = self.machine.op_count - self.last_op_count
            self.last_op_count = self.machine.op_count
            ops_per_second = int(new_ops / duration)

            msg = (
                "%s cycles/sec (Dragon 32 == 895.000cycles/sec)"
                "\n%s ops/sec - burst duration: %.3f sec. - burst count: %s Ops"
            ) % (
                locale_format_number(cycles_per_second),
                locale_format_number(ops_per_second),
                burst_duration, locale_format_number(self.burst_count)
            )
            self.status.set(msg)

        self.process_display_queue()

        if interval is not None:
            if self.machine.cpu.running:
    #            log.critical("queue cpu interval")
    #            self.root.after_idle(self.cpu_interval, machine, burst_count, interval)
                self.cpu_after_id = self.root.after(interval, self.cpu_interval, interval)
            else:
                log.critical("CPU stopped.")

    def process_display_queue(self):
        """
        consume all exiting "display RAM write" queue items and render them.
        """
#        log.critical("start process_display_queue()")
        while True:
            try:
                cpu_cycles, op_address, address, value = self.display_queue.get_nowait()
            except queue.Empty:
#                log.critical("display_queue empty -> exit loop")
                return
#                log.critical(
#                    "call display.write_byte() (display_queue._qsize(): %i)",
#                    self.display_queue._qsize()
#                )
            self.display.write_byte(cpu_cycles, op_address, address, value)

    def mainloop(self, machine):
        self.machine = machine

        self.cpu_interval(interval=1)

        log.critical("Start root.mainloop()")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.exit()
        log.critical("root.mainloop() has quit!")


class DragonTkinterGUI(BaseTkinterGUI):
    """
    The complete Tkinter GUI window
    """
    def __init__(self, *args, **kwargs):
        super(DragonTkinterGUI, self).__init__(*args, **kwargs)

        machine_name = self.cfg.MACHINE_NAME
        self.root.title(
            "%s - Text Display 32 columns x 16 rows" % machine_name)

        self.display = MC6847_TextModeCanvas(self.root)
        self.display.canvas.grid(row=0, column=0, columnspan=2)  # , rowspan=2)

        self._editor_window = None

        self.menubar.insert_command(index=3, label="BASIC editor", command=self.open_basic_editor)

        # display the menu
        self.root.config(menu=self.menubar)
        self.root.update()

    #-------------------------------------------------------------------------------------

    def close_basic_editor(self):
        if messagebox.askokcancel("Quit", "Do you really wish to close the Editor?"):
            self._editor_window.root.destroy()
            self._editor_window = None

    def open_basic_editor(self):
        if self._editor_window is None:
            self._editor_window = EditorWindow(self.cfg, self)
            self._editor_window.root.protocol("WM_DELETE_WINDOW", self.close_basic_editor)

            # insert menu to editor window
            editmenu = tkinter.Menu(self._editor_window.menubar, tearoff=0)
            editmenu.add_command(label="load from DragonPy", command=self.command_load_from_DragonPy)
            editmenu.add_command(label="inject into DragonPy", command=self.command_inject_into_DragonPy)
            editmenu.add_command(label="inject + RUN into DragonPy", command=self.command_inject_and_run_into_DragonPy)
            self._editor_window.menubar.insert_cascade(index=2, label="DragonPy", menu=editmenu)

        self._editor_window.focus_text()

    def command_load_from_DragonPy(self):
        self.add_user_input_and_wait("'SAVE TO EDITOR")
        listing_ascii = self.machine.get_basic_program()
        self._editor_window.set_content(listing_ascii)
        self.add_user_input_and_wait("\r")

    def command_inject_into_DragonPy(self):
        self.add_user_input_and_wait("'LOAD FROM EDITOR")
        content = self._editor_window.get_content()
        result = self.machine.inject_basic_program(content)
        log.critical("program loaded: %s", result)
        self.add_user_input_and_wait("\r")

    def command_inject_and_run_into_DragonPy(self):
        self.command_inject_into_DragonPy()
        self.add_user_input_and_wait("\r") # FIXME: Sometimes this input will be "ignored"
        self.add_user_input_and_wait("RUN\r")

    ###########################################################################

    #-------------------------------------------------------------------------------------

    def dump_rnd(self):
        start_addr = 0x0019
        end_addr = 0x0020
        dump, start_addr, end_addr = self.request_comm.request_memory_dump(
#            start_addr=0x0115, end_addr=0x0119 # RND seed
            start_addr, end_addr
        )
        def format_dump(dump, start_addr, end_addr):
            lines = []
            for addr, value in zip(range(start_addr, end_addr + 1), dump):
                log.critical("$%04x: $%02x (dez.: %i)", addr, value, value)
                lines.append("$%04x: $%02x (dez.: %i)" % (addr, value, value))
            return lines
        lines = format_dump(dump, start_addr, end_addr)
        messagebox.showinfo("TODO", "dump_program:\n%s" % "\n".join(lines))



#------------------------------------------------------------------------------


def test_run():
    import sys
    import os
    import subprocess
    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
#        "--verbosity", "5",
        "--machine", "Dragon32", "run",
#        "--machine", "Vectrex", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()