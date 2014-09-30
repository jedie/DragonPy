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
from dragonpy.Dragon32.keyboard_map import inkey_from_tk_event, add_to_input_queue

xrange = six.moves.xrange

import sys
import time
import logging
import string

try:
    # Python 3
    import queue
    import tkinter
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter import scrolledtext
    from tkinter import font as TkFont
except ImportError:
    # Python 2
    import Queue as queue
    import Tkinter as tkinter
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    import tkFont as TkFont

from basic_editor.editor import EditorWindow
from dragonpy.Dragon32.MC6847 import MC6847_TextModeCanvas
from dragonpy.Dragon32.gui_config import RuntimeCfg, BaseTkinterGUIConfig
from dragonpy.utils.humanize import locale_format_number, get_python_info

log = logging.getLogger(__name__)


class BaseTkinterGUI(object):
    """
    The complete Tkinter GUI window
    """

    def __init__(self, cfg, user_input_queue):
        self.cfg = cfg
        self.runtime_cfg = RuntimeCfg()

        # Queue to send keyboard inputs to CPU Thread:
        self.user_input_queue = user_input_queue

        self.op_delay = 0
        self.burst_op_count = 100
        self.cpu_after_id = None # Used to call CPU OP burst loop
        self.target_burst_duration = 0.1 # Duration how long should a CPU Op burst loop take

        self.init_statistics() # Called also after reset

        self.root = tkinter.Tk(className="DragonPy")
        # self.root.config(font="Helvetica 16 bold italic")

        self.root.geometry("+%d+%d" % (
            self.root.winfo_screenwidth() * 0.1, self.root.winfo_screenheight() * 0.1
        ))

        self.root.bind("<Key>", self.event_key_pressed)
        self.root.bind("<<Paste>>", self.paste_clipboard)

        menu_tk_font = TkFont.Font(
            family='Helvetica',
            # family='clean',
            size=11, weight='normal'
        )

        self.status = tkinter.StringVar(value="startup %s...\n" % self.cfg.MACHINE_NAME)
        self.status_widget = tkinter.Label(
            self.root, textvariable=self.status, text="Info:", borderwidth=1,
            font=menu_tk_font
        )
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
        # FIXME: Only for developing: Open config on startup!
        # self.root.after(200, self.command_config)

        # help menu
        helpmenu = tkinter.Menu(self.menubar, tearoff=0)
        helpmenu.add_command(label="help", command=self.menu_event_help)
        helpmenu.add_command(label="about", command=self.menu_event_about)
        self.menubar.add_cascade(label="help", menu=helpmenu)

        self.auto_shift=True # auto shift all input characters?

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

    # -----------------------------------------------------------------------------------------

    def close_config(self):
        self.config_window.root.destroy()
        self.config_window = None

    def command_config(self):
        if self.config_window is None:
            self.config_window = BaseTkinterGUIConfig(self, self.runtime_cfg)
            self.config_window.root.protocol("WM_DELETE_WINDOW", self.close_config)
        else:
            self.config_window.focus()

    # -----------------------------------------------------------------------------------------

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

    # -----------------------------------------------------------------------------------------

    def add_user_input(self, txt):
        add_to_input_queue(self.user_input_queue, txt)

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
        log.critical("event.char: %-6r event.keycode: %-3r event.keysym: %-11r event.keysym_num: %5r",
                event.char, event.keycode, event.keysym, event.keysym_num
        )
        inkey = inkey_from_tk_event(event, auto_shift=self.auto_shift)
        log.critical("inkey: %r", inkey)
        self.user_input_queue.put(inkey)

    total_burst_duration = 0
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
        self.machine.cpu.run(
            max_run_time=self.runtime_cfg.max_run_time,
            target_cycles_per_sec=target_cycles_per_sec,
        )
        now = time.time()
        self.total_burst_duration += (now - start_time)

        if interval is not None:
            if self.machine.cpu.running:
                self.cpu_after_id = self.root.after(interval, self.cpu_interval, interval)
            else:
                log.critical("CPU stopped.")

    last_update = 0

    def update_status_interval(self, interval=500):
        # Update CPU settings:
        self.machine.cpu.sync_op_count = self.runtime_cfg.sync_op_count
        self.machine.cpu.max_burst_count = self.runtime_cfg.max_burst_count

        new_cycles = self.machine.cpu.cycles - self.last_cpu_cycles
        duration = time.time() - self.last_update

        cycles_per_sec = new_cycles / duration

        msg = (
                  "%s cylces/sec (~%s burst op count)\n"
                  "%i CPU interval calls"
              ) % (
                  locale_format_number(cycles_per_sec),
                  locale_format_number(self.machine.cpu.burst_op_count),
                  self.cpu_interval_calls,
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

    def display_callback(self, cpu_cycles, op_address, address, value):
        """ called via memory write_byte_middleware """
        self.display.write_byte(cpu_cycles, op_address, address, value)
        return value

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
        self.add_user_input_and_wait("\n")

    def command_inject_into_DragonPy(self):
        self.add_user_input_and_wait("'LOAD FROM EDITOR")
        content = self._editor_window.get_content()
        result = self.machine.inject_basic_program(content)
        log.critical("program loaded: %s", result)
        self.add_user_input_and_wait("\n")

    def command_inject_and_run_into_DragonPy(self):
        self.command_inject_into_DragonPy()
        self.add_user_input_and_wait("\n") # FIXME: Sometimes this input will be "ignored"
        self.add_user_input_and_wait("RUN\n")

    # ##########################################################################

    # -------------------------------------------------------------------------------------

    def dump_rnd(self):
        start_addr = 0x0019
        end_addr = 0x0020
        dump, start_addr, end_addr = self.request_comm.request_memory_dump(
            # start_addr=0x0115, end_addr=0x0119 # RND seed
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


class ScrolledTextGUI(BaseTkinterGUI):
    def __init__(self, *args, **kwargs):
        super(ScrolledTextGUI, self).__init__(*args, **kwargs)

        self.root.title("DragonPy - %s" % self.cfg.MACHINE_NAME)

        self.text = scrolledtext.ScrolledText(
            master=self.root, height=30, width=80
        )
        self.text.config(
            background="#ffffff", foreground="#000000",
            highlightthickness=0,
            font=('courier', 11),
        )
        self.text.grid(row=0, column=0, sticky=tkinter.NSEW)

#         self._editor_window = None
#         self.menubar.insert_command(index=3, label="BASIC editor", command=self.open_basic_editor)

        self.root.unbind("<Key>")
        self.text.bind("<Key>", self.event_key_pressed)

        # TODO: self.root.bind("<<Paste>>", self.paste_clipboard) ???

        # display the menu
        self.root.config(menu=self.menubar)
        self.root.update()

    def event_key_pressed(self, event):
        """
        So a "invert shift" for user inputs:
        Convert all lowercase letters to uppercase and vice versa.
        """
        char = event.char
        if not char:
            return

        if char in string.ascii_letters:
            char = invert_shift(char)

        self.user_input_queue.put(char)

        # Don't insert the char in text widget, because it will be echoed
        # back from the machine!
        return "break"

    def display_callback(self, char):
        log.debug("Add to text: %s", repr(char))
        if char == "\x08":
            # Delete last input char
            self.text.delete(tkinter.INSERT + "-1c")
        else:
            # insert the new character:
            self.text.insert(tkinter.END, char)

            # scroll down if needed:
            self.text.see(tkinter.END)

            # Set cursor to the END position:
            self.text.mark_set(tkinter.INSERT, tkinter.END)


def test_run():
    import sys
    import os
    import subprocess

    cmd_args = [
        sys.executable,
        os.path.join("..", "DragonPy_CLI.py"),
        # "--log_list",

        # "--verbosity", " 1", # hardcode DEBUG ;)
        # "--verbosity", "10", # DEBUG
        # "--verbosity", "20", # INFO
        #         "--verbosity", "30", # WARNING
        #         "--verbosity", "40", # ERROR
        #         "--verbosity", "50", # CRITICAL/FATAL
        #         "--verbosity", "99", # nearly all off
        "--verbosity", "100", # all off

        # "--log",
        # "dragonpy.components.cpu6809,40",
        # "dragonpy.Dragon32.MC6821_PIA,50",

        "--machine", "Dragon32", "run",
        #        "--machine", "Vectrex", "run",
        #        "--max_ops", "1",
        #        "--trace",
    ]
    print("Startup CLI with: %s" % " ".join(cmd_args[1:]))
    subprocess.Popen(cmd_args, cwd="..").wait()


if __name__ == "__main__":
    test_run()
