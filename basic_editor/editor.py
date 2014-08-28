#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import ScrolledText
import Tkinter
import string
import tkFileDialog
import tkMessageBox

from dragonlib.utils.auto_shift import invert_shift
from dragonlib.utils.logging_utils import log, pformat_program_dump


class EditorWindow(object):
    def __init__(self, cfg, gui=None):
        self.cfg = cfg
        if gui is None:
            self.standalone_run = True
        else:
            self.gui=gui
            self.standalone_run = False

        self.machine_api = self.cfg.machine_api

        if self.standalone_run:
            self.root = Tkinter.Tk()
        else:
            # As sub window in DragonPy Emulator
            self.root = Tkinter.Toplevel(self.gui.root)
            self.root.geometry("+%d+%d" % (self.gui.root.winfo_rootx() + 30,
                self.gui.root.winfo_rooty() + 40))

        self.root.title("%s - BASIC Editor" % self.cfg.MACHINE_NAME)

        self.text = ScrolledText.ScrolledText(
            master=self.root, height=30, width=80
        )
        self.text.config(
            background="#08ff08", # nearly green
            foreground="#004100", # nearly black
            highlightthickness=0,
            font=('courier', 11, 'bold'),
#            yscrollcommand=scollbar.set, # FIXME
#            state=Tkinter.DISABLED # FIXME: make textbox "read-only"
        )

        #self.auto_shift = True # use invert shift for letters?
        self.root.bind("<Key>", self.event_key_pressed)

        self.text.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

        menubar = Tkinter.Menu(self.root)

        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.command_load_file)
        filemenu.add_command(label="Save", command=self.command_save_file)
        if self.standalone_run:
            filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        if not self.standalone_run: # As sub window in DragonPy Emulator
            editmenu = Tkinter.Menu(menubar, tearoff=0)
            editmenu.add_command(label="load from DragonPy", command=self.command_load_from_DragonPy)
            editmenu.add_command(label="inject into DragonPy", command=self.command_inject_into_DragonPy)
            editmenu.add_command(label="inject + RUN into DragonPy", command=self.command_inject_and_run_into_DragonPy)
            menubar.add_cascade(label="DragonPy", menu=editmenu)

        editmenu = Tkinter.Menu(menubar, tearoff=0)
        editmenu.add_command(label="renum", command=self.renumber_listing)
        editmenu.add_command(label="display tokens", command=self.debug_display_tokens)
        menubar.add_cascade(label="tools", menu=editmenu)

        # help menu
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
#        helpmenu.add_command(label="help", command=self.menu_event_help)
#        helpmenu.add_command(label="about", command=self.menu_event_about)
        menubar.add_cascade(label="help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)
        self.root.update()

    def event_key_pressed(self, event):
        """
        So a "invert shift" for user inputs:
        Convert all lowercase letters to uppercase and vice versa.
        """
        char = event.char
        if not char or char not in string.letters:
            # ignore all non letter inputs
            return
        
        converted_char = invert_shift(char)
        log.debug("convert keycode %s - char %s to %s", event.keycode, repr(char), converted_char)
        self.text.delete("insert-1c") # Delete last input char
        self.text.insert(Tkinter.INSERT, converted_char) # Insert converted char
        return "break"

    def command_load_file(self):
        infile = tkFileDialog.askopenfile(parent=self.root, mode="r", title="Select a BASIC file to load")
        if infile is not None:
            content = infile.read()
            infile.close()
            content = content.strip()
            listing_ascii = content.splitlines()
            self.set_content(listing_ascii)

    def command_save_file(self):
        outfile = tkFileDialog.asksaveasfile(parent=self.root, mode="w")
        if outfile is not None:
            content = self.get_content()
            outfile.write(content)
            outfile.close()

    ###########################################################################
    # For DragonPy Emulator:

    def command_load_from_DragonPy(self):
        self.gui.add_user_input_and_wait("'SAVE TO EDITOR")
        listing_ascii = self.gui.request_comm.get_basic_program()
        self.set_content(listing_ascii)
        self.gui.add_user_input_and_wait("\r")

    def command_inject_into_DragonPy(self):
        self.gui.add_user_input_and_wait("'LOAD FROM EDITOR")
        content = self.get_content()
        result = self.gui.request_comm.inject_basic_program(content)
        log.critical("program loaded: %s", result)
        self.gui.add_user_input_and_wait("\r")

    def command_inject_and_run_into_DragonPy(self):
        self.command_inject_into_DragonPy()
        self.gui.add_user_input_and_wait("\r") # FIXME: Sometimes this input will be "ignored"
        self.gui.add_user_input_and_wait("RUN\r")

    ###########################################################################

    def debug_display_tokens(self):
        content = self.get_content()
        program_dump = self.machine_api.ascii_listing2program_dump(content)
        msg = pformat_program_dump(program_dump)
        tkMessageBox.showinfo("Program Dump:", msg, parent=self.root)

    def renumber_listing(self):
        content = self.get_content()
        content = self.machine_api.renum_ascii_listing(content)
        self.set_content(content)

    def get_content(self):
        content = self.text.get("1.0", Tkinter.END)
        content = content.strip()
        return content

    def set_content(self, listing_ascii):
#        self.text.config(state=Tkinter.NORMAL)
        self.text.delete("1.0", Tkinter.END)
        log.critical("insert listing:")
        if isinstance(listing_ascii, basestring):
            listing_ascii = listing_ascii.splitlines()

        for line in listing_ascii:
            line = "%s\n" % line # use os.sep ?!?
            log.critical("\t%s", repr(line))
            self.text.insert(Tkinter.END, line)
#        self.text.config(state=Tkinter.DISABLED)
        self.text.mark_set(Tkinter.INSERT, '1.0') # Set cursor at start
        self.text.focus()

    def mainloop(self):
        """ for standalone usage """
        self.root.mainloop()


def run_basic_editor(cfg, default_content=None):
    editor = EditorWindow(cfg)
    if default_content is not None:
        editor.set_content(default_content)
    editor.mainloop()


def test():
    CFG_DICT = {
        "verbosity": None,
        "display_cycle": False,
        "trace": None,
        "max_ops": None,
        "bus_socket_host": None,
        "bus_socket_port": None,
        "ram": None,
        "rom": None,
        "use_bus": False,
    }
    from dragonpy.Dragon32.config import Dragon32Cfg
    cfg = Dragon32Cfg(CFG_DICT)
    listing_ascii = (
        "10 CLS\n"
        "20 FOR I = 0 TO 255:\n"
        "30 POKE 1024+(I*2),I\n"
        "40 NEXT I\n"
        "50 I$ = INKEY$:IF I$="" THEN 50\n"
    )
    run_basic_editor(cfg, default_content=listing_ascii)


if __name__ == "__main__":
    test()
