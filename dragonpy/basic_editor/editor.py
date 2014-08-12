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

from dragonpy.utils.logging_utils import log

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
