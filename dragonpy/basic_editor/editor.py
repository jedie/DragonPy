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

from dragonlib.utils.logging_utils import log


class EditorWindow(object):
    def __init__(self, cfg, parent):
        self.cfg = cfg
        self.parent = parent

        self.root = Tkinter.Toplevel(self.parent)
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
        )

        scollbar.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
        self.text.pack(side=Tkinter.LEFT, fill=Tkinter.Y)

        menubar = Tkinter.Menu(self.root)

        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Tkinter.Menu(menubar, tearoff=0)
#        editmenu.add_command(label="load BASIC program", command=self.load_program)
        menubar.add_cascade(label="edit", menu=editmenu)

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

    def debug_display_tokens(self):
        ascii = self.get_ascii()
        self.listing.ascii_listing2basic_lines(ascii)
        self.listing.debug_listing()
        tkMessageBox.showinfo("TODO", "TODO: debug_display_tokens")

    def get_ascii(self):
        return self.text.get("1.0", Tkinter.END)

    def set_content(self, listing_ascii):
        log.critical("insert listing:")
        for line in listing_ascii:
            line = "%s\n" % line # use os.sep ?!?
            log.critical("\t%s", repr(line))
            self.text.insert(Tkinter.END, line)
        self.text.see(Tkinter.END)


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
    root = Tkinter.Tk()
    editor_window = EditorWindow(cfg, root)

    listing_ascii = (
        "10 CLS",
        "20 FOR I = 0 TO 255:",
        "30 POKE 1024+(I*2),I",
        "40 NEXT I",
        "50 I$ = INKEY$:IF I$="" THEN 50",
    )
    editor_window.set_content(listing_ascii)
    root.mainloop()

if __name__ == "__main__":
    test()
