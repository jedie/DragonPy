#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import Tkinter
import tkMessageBox

from dragonlib.utils.logging_utils import log, format_program_dump


class EditorWindow(object):
    def __init__(self, cfg, parent=None, request_comm=None):
        self.cfg = cfg
        if parent is None:
            self.standalone_run = True
        else:
            self.parent = parent
            self.request_comm = request_comm
            self.standalone_run = False

        self.machine_api = self.cfg.machine_api

        if self.standalone_run:
            self.root = Tkinter.Tk()
        else:
            # As sub window in DragonPy Emulator
            self.root = Tkinter.Toplevel(self.parent)
            self.root.geometry("+%d+%d" % (self.parent.winfo_rootx() + 30,
                self.parent.winfo_rooty() + 40))

        self.root.title("%s - BASIC Editor" % self.cfg.MACHINE_NAME)

        # http://www.tutorialspoint.com/python/tk_text.htm
        self.text = Tkinter.Text(self.root, height=30, width=80)
        scollbar = Tkinter.Scrollbar(self.root)
        scollbar.config(command=self.text.yview)

        self.text.config(
            background="#08ff08", # nearly green
            foreground="#004100", # nearly black
            font=('courier', 11, 'bold'),
#            yscrollcommand=scollbar.set, # FIXME
#            state=Tkinter.DISABLED # FIXME: make textbox "read-only"
        )

        # TODO:
        self.auto_shift = True # use invert shift for letters?
#        self.root.bind("<Key>", self.event_key_pressed)

        scollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.text.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

        menubar = Tkinter.Menu(self.root)

        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.load_file)
        filemenu.add_command(label="Save", command=self.save_file)
        if self.standalone_run:
            filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        if not self.standalone_run: # As sub window in DragonPy Emulator
            editmenu = Tkinter.Menu(menubar, tearoff=0)
            editmenu.add_command(label="load from DragonPy", command=self.load_from_DragonPy)
            editmenu.add_command(label="inject into DragonPy", command=self.inject_into_DragonPy)
            menubar.add_cascade(label="DragonPy", menu=editmenu)

        editmenu = Tkinter.Menu(menubar, tearoff=0)
        editmenu.add_command(label="display tokens", command=self.debug_display_tokens)
        menubar.add_cascade(label="debug", menu=editmenu)

        # help menu
        helpmenu = Tkinter.Menu(menubar, tearoff=0)
#        helpmenu.add_command(label="help", command=self.menu_event_help)
#        helpmenu.add_command(label="about", command=self.menu_event_about)
        menubar.add_cascade(label="help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)
        self.root.update()

#    def event_key_pressed(self, event):
#        keycode = event.keycode
#        char = event.char
#        log.critical("keycode %s - char %s", keycode, repr(char))
#        self.text.config(state=Tkinter.NORMAL)
#        char = invert_shift(char)
#        self.text.insert("end", char)
#        self.text.see("end")
#        self.text.config(state=Tkinter.DISABLED)

    def load_file(self):
        tkMessageBox.showinfo("TODO", "load file")
    def save_file(self):
        tkMessageBox.showinfo("TODO", "save file")

    def load_from_DragonPy(self):
        listing_ascii = self.request_comm.get_basic_program()
        self.set_content(listing_ascii)
        
    def inject_into_DragonPy(self):
        basic_program_ascii = self.get_ascii()
        result = self.request_comm.inject_basic_program(basic_program_ascii)
        log.critical("program loaded: %s", result)

    def debug_display_tokens(self):
        ascii_listing = self.get_ascii()
        program_dump = self.machine_api.ascii_listing2program_dump(ascii_listing)
        msg = format_program_dump(program_dump)
        tkMessageBox.showinfo("Program Dump:", msg)

    def get_ascii(self):
        return self.text.get("1.0", Tkinter.END)

    def set_content(self, listing_ascii):
#        self.text.config(state=Tkinter.NORMAL)
        self.text.delete("1.0", Tkinter.END)
        log.critical("insert listing:")
        for line in listing_ascii:
            line = "%s\n" % line # use os.sep ?!?
            log.critical("\t%s", repr(line))
            self.text.insert(Tkinter.END, line)
#        self.text.config(state=Tkinter.DISABLED)
        self.text.see(Tkinter.END)

    def mainloop(self):
        """ for standalone usage """
        self.root.mainloop()


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

    editor = EditorWindow(cfg)

    listing_ascii = (
        "10 CLS",
        "20 FOR I = 0 TO 255:",
        "30 POKE 1024+(I*2),I",
        "40 NEXT I",
        "50 I$ = INKEY$:IF I$="" THEN 50",
    )
    editor.set_content(listing_ascii)
    editor.mainloop()

if __name__ == "__main__":
    test()
