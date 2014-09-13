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
from dragonlib.utils import six
xrange = six.moves.xrange

import os
import sys
import time
import logging

from basic_editor.editor import EditorWindow

from dragonpy.Dragon32 import dragon_charmap
from dragonpy.Dragon32.dragon_charmap import get_charmap_dict
from dragonpy.Dragon32.dragon_font import CHARS_DICT, TkFont
from dragonpy.utils.humanize import locale_format_number, get_python_info

log = logging.getLogger(__name__)


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

        foreground, background = dragon_charmap.get_hex_color(dragon_charmap.NORMAL)
        self.canvas = tkinter.Canvas(root,
            width=self.total_width,
            height=self.total_height,
            bd=0, # no border
            highlightthickness=0, # no highlight border
#             bg="#ff0000",
            bg="#%s" % background,
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


class RuntimeCfg(object):
    """
    TODO: Load/save to ~/.DragonPy.ini
    """
    speedlimit = False
    cycles_per_sec = 888625 # cycles/sec
    max_run_time = 0.1

    def __setattr__(self, attr, value):
        log.critical("Set RuntimeCfg %r to: %r" % (attr, value))
        return object.__setattr__(self, attr, value)

    def load(self):
        raise NotImplementedError("TODO!")
    def save(self):
        raise NotImplementedError("TODO!")



class BaseTkinterGUIConfig(object):
    """
    14.318180 Mhz crystal / 16 = 0.894886 MHz CPU frequency * 1000000 = 894886 cycles/sec
    14.218000 Mhz crystal / 16 = 0.888625 MHz CPU frequency * 1000000 = 888625 cycles/sec

    894886 cycles/sec - 888625 cycles/sec = 6261 cycles/sec slower
    14.218000 Mhz crystal = 0.00000113 Sec or 1.12533408356e-06 us cycle time
    """
    def __init__(self, gui, runtime_cfg):
        self.gui = gui
        self.runtime_cfg = runtime_cfg

        self.root = tkinter.Toplevel(self.gui.root)
        self.root.geometry("+%d+%d" % (
            self.gui.root.winfo_rootx() + self.gui.root.winfo_width(),
            self.gui.root.winfo_y() # FIXME: Different on linux.
        ))

        #
        # Speedlimit check button
        #
        # self.check_value_speedlimit = tkinter.BooleanVar( # FIXME: Doesn't work with PyPy ?!?!
        self.check_value_speedlimit = tkinter.IntVar(
            value=self.runtime_cfg.speedlimit
        )
        self.checkbutton_speedlimit = tkinter.Checkbutton(self.root,
            text="speedlimit", variable=self.check_value_speedlimit,
            command=self.command_checkbutton_speedlimit
        )
        self.checkbutton_speedlimit.grid(row=0, column=0)

        #
        # Cycles/sec entry
        #
        self.cycles_per_sec_var = tkinter.IntVar(
            value=self.runtime_cfg.cycles_per_sec
        )
        self.cycles_per_sec_entry = tkinter.Entry(self.root,
            textvariable=self.cycles_per_sec_var,
            width=8, # validate = 'key', validatecommand = vcmd
        )
        self.cycles_per_sec_entry.bind('<KeyRelease>', self.command_cycles_per_sec)
        self.cycles_per_sec_entry.grid(row=0, column=1)

        self.cycles_per_sec_label_var = tkinter.StringVar()
        self.cycles_per_sec_label = tkinter.Label(
            self.root, textvariable=self.cycles_per_sec_label_var
        )
        self.root.after_idle(self.command_cycles_per_sec) # Add Text
        self.cycles_per_sec_label.grid(row=0, column=2)

        #
        # CPU burst max running time - self.runtime_cfg.max_run_time
        #
        self.max_run_time_var = tkinter.DoubleVar(
            value=self.runtime_cfg.max_run_time
        )
        self.max_run_time_entry = tkinter.Entry(self.root,
            textvariable=self.max_run_time_var, width=8,
        )
        self.max_run_time_entry.bind('<KeyRelease>', self.command_max_run_time)
        self.max_run_time_entry.grid(row=2, column=1)
        self.max_run_time_label = tkinter.Label(self.root,
            text="How long should a CPU Op burst loop take (max_run_time)"
        )
        self.max_run_time_label.grid(row=2, column=2, sticky=tkinter.W)

        self.root.update()

    def command_checkbutton_speedlimit(self, event=None):
        self.runtime_cfg.speedlimit = self.check_value_speedlimit.get()

    def command_cycles_per_sec(self, event=None):
        try:
            cycles_per_sec = self.cycles_per_sec_var.get()
        except ValueError:
            self.cycles_per_sec_var.set(self.runtime_cfg.cycles_per_sec)
            return

        self.cycles_per_sec_label_var.set(
            "cycles/sec / 1000000 = %f MHz CPU frequency * 16 = %f Mhz crystal" % (
                cycles_per_sec / 1000000,
                cycles_per_sec / 1000000 * 16,
            )
        )

        self.runtime_cfg.cycles_per_sec = cycles_per_sec

    def command_max_run_time(self, event=None):
        """ CPU burst max running time - self.runtime_cfg.max_run_time """
        try:
            max_run_time = self.max_run_time_var.get()
        except ValueError:
            max_run_time = self.runtime_cfg.max_run_time

        self.runtime_cfg.max_run_time = max_run_time
        self.max_run_time_var.set(self.runtime_cfg.max_run_time)

    def focus(self):
        # see: http://www.python-forum.de/viewtopic.php?f=18&t=34643 (de)
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        self.root.focus_force()
        self.root.lift(aboveThis=self.gui.root)


class BaseTkinterGUI(object):
    """
    The complete Tkinter GUI window
    """
    def __init__(self, cfg, display_queue, user_input_queue):
        self.cfg = cfg
        self.runtime_cfg = RuntimeCfg()

        # Queue which contains "write into Display RAM" information
        # for render them in MC6847_TextModeCanvas():
        self.display_queue = display_queue

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        self.op_delay = 0
        self.burst_op_count = 100
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
        self.status_widget.grid(row=1, column=0)

        self.python_info_label = tkinter.Label(
            self.root, borderwidth=1, text=get_python_info(),
        )
        self.python_info_label.grid(row=2, column=0)

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

        self.config_window = None
        self.menubar.add_command(label="config", command=self.command_config)
        self.root.after(200, self.command_config) # FIXME: Only for developing: Open config on startup!

        # help menu
        helpmenu = tkinter.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        self.menubar.add_cascade(label="help", menu=helpmenu)

    def init_statistics(self):
        self.op_count = 0
        self.last_op_count = 0
        self.last_cpu_cycles = 0
        self.cpu_cycles_update_interval = 1 # Fequency for update GUI status information
        self.next_cpu_cycle_update = time.time() + self.cpu_cycles_update_interval
        self.last_cycles_per_second = sys.maxsize

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

    def close_config(self):
        self.config_window.root.destroy()
        self.config_window = None

    def command_config(self):
        if self.config_window is None:
            self.config_window = BaseTkinterGUIConfig(self, self.runtime_cfg)
            self.config_window.root.protocol("WM_DELETE_WINDOW", self.close_config)
        else:
            self.config_window.focus()

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
        for count in xrange(1, 10):
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

    total_burst_duration = 0
    burst_loops = 0
    cpu_interval_calls = 0
    last_display_queue_qsize = 0
    def cpu_interval(self, interval=None):
        self.cpu_interval_calls += 1

        if self.runtime_cfg.speedlimit:
            # Run CPU not faster than speedlimit
            target_cycles_per_sec = self.runtime_cfg.cycles_per_sec
        else:
            # Run CPU as fast as Python can...
            target_cycles_per_sec = None

        start_time = time.time()
        self.burst_loops += self.machine.cpu.run(
            max_run_time=self.runtime_cfg.max_run_time,
            target_cycles_per_sec=target_cycles_per_sec,
        )
        now = time.time()
        self.total_burst_duration += (now - start_time)

        self.last_display_queue_qsize = (self.last_display_queue_qsize + self.display_queue.qsize()) / 2
        self.process_display_queue()

        if interval is not None:
            if self.machine.cpu.running:
                self.cpu_after_id = self.root.after(interval, self.cpu_interval, interval)
            else:
                log.critical("CPU stopped.")

    last_update = 0
    def update_status_interval(self, interval=500):
        new_cycles = self.machine.cpu.cycles - self.last_cpu_cycles
        duration = time.time() - self.last_update

        cycles_per_sec = new_cycles / duration

        msg = (
            "%s cylces/sec in %i burst loops (~%s burst op count)\n"
            "%i CPU interval calls, display queue qsize: %.2f"
        ) % (
            locale_format_number(cycles_per_sec),
            self.burst_loops,
            locale_format_number(self.machine.cpu.burst_op_count),
            self.cpu_interval_calls,
            self.last_display_queue_qsize
        )

        if self.runtime_cfg.speedlimit:
            msg += (
                "\ncylces/sec diff: %s"
            ) % (
                locale_format_number(
                    abs(self.runtime_cfg.cycles_per_sec - cycles_per_sec)
                ),
            )

        self.status.set(msg)

        self.last_cpu_cycles = self.machine.cpu.cycles
        self.cpu_interval_calls = 0
        self.burst_loops = 0
        self.last_update = time.time()

        self.root.after(interval, self.update_status_interval, interval)

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

        self.update_status_interval(interval=500)

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
        self.display.canvas.grid(row=0, column=0)

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
#         "--log_list",

#         "--verbosity", " 1", # hardcode DEBUG ;)
#         "--verbosity", "10", # DEBUG
#         "--verbosity", "20", # INFO
#         "--verbosity", "30", # WARNING
#         "--verbosity", "40", # ERROR
#         "--verbosity", "50", # CRITICAL/FATAL
        "--verbosity", "99", # nearly all off

#         "--log", "DragonPy.cpu6809,50;dragonpy.Dragon32.MC6821_PIA,40",
#         "--log", "dragonpy.components.cpu6809,50",

        "--machine", "Dragon32", "run",
#        "--machine", "Vectrex", "run",
#        "--max_ops", "1",
#        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()

if __name__ == "__main__":
    test_run()
