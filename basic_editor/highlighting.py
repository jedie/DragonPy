# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    Some code borrowed from Python IDLE

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function
from six.moves import xrange

try:
    # python 3
    import tkinter
    from tkinter import font
except ImportError:
    # Python 2
    import Tkinter as tkinter
    import tkFont as font


from basic_editor.editor_base import BaseExtension
from dragonlib.core import basic_parser


class TkTextHighlighting(BaseExtension):
    """
    code based on idlelib.ColorDelegator.ColorDelegator
    """
    after_id = None
    TAG_LINE_NUMBER = "lineno"
    TAG_JUMP_ADDESS = "jump"
    def __init__(self, editor):
        super(TkTextHighlighting, self).__init__(editor)

        self.machine_api = editor.machine_api

        bold_font = font.Font(self.text, self.text.cget("font"))
        bold_font.configure(weight="bold")
        self.text.tag_configure("bold", font=bold_font)

        self.tagdefs = {
            self.TAG_LINE_NUMBER: {"foreground": "#333333", "background":"#f4f4f4"},
            self.TAG_JUMP_ADDESS: {"foreground":"#0000aa", "background":"#f4f4f4", "font":bold_font},

            basic_parser.CODE_TYPE_CODE: {"foreground":"#222222", "font":bold_font},
            basic_parser.CODE_TYPE_DATA: {"foreground":"#ddaaff", "font":bold_font},
            basic_parser.CODE_TYPE_STRING: {"foreground":"#0000ff"},# , "font":bold_font},
            basic_parser.CODE_TYPE_COMMENT: {"foreground":"#00aa00"},
        }
        for tag, args in list(self.tagdefs.items()):
            self.text.tag_configure(tag, **args)

#         self.notify_range("1.0", "end")

        self.old_pos = None
        self.__update_interval()

    def update(self, force=False):
        pos = self.text.index(tkinter.INSERT)

        if not force:
            if pos == self.old_pos:
#                 log.critical("No recolorize needed.")
                return

        self.recolorize()
        self.old_pos = pos

    def __update_interval(self):
        """ highlight the current line_no """
        self.update()
        self.after_id = self.text.after(10, self.__update_interval)

#     def notify_range(self, index1, index2=None):
#         self.text.tag_add("TODO", index1, index2)

    def colorize(self, part_type, start, end):
#         print "colorize", part_type, start, end
        self.text.tag_add(part_type, start, end)

    def recolorize(self):
        self.removecolors()

        listing = self.editor.get_content()
        destinations = self.machine_api.renum_tool.get_destinations(listing)

        line_max = self.text.index(tkinter.END).split('.')[0]
        line_max = int(line_max)
        for line_no in xrange(line_max):
            line_content = self.text.get("%s.0" % line_no, "%s.0+1lines" % line_no)
#             print "line:", repr(line_content)
            if not line_content.strip():
                continue

            parsed_lines = self.machine_api.parse_ascii_listing(line_content)
            try:
                code_line_no, code_objects = list(parsed_lines.items())[0]
            except IndexError:
                continue
#             print "parsed line:", code_line_no, code_objects

            index = len(str(code_line_no) + " ")

            if code_line_no in destinations:
                # The current line number is used as a jump address
                part_type = self.TAG_JUMP_ADDESS
            else:
                part_type = self.TAG_LINE_NUMBER
            self.colorize(part_type,
                start="%s.0" % line_no,
                end="%s.%s" % (line_no, index)
            )

            for code_object in code_objects:
                end = index + len(code_object.content)
                self.colorize(code_object.PART_TYPE,
                     start="%s.%s" % (line_no, index),
                     end="%s.%s" % (line_no, end),
                )
                index = end

#             print

#         line, column = self.text.index(Tkinter.INSERT).split('.')
#         print "recolorize lines %s" % line

    def removecolors(self):
        for tag in self.tagdefs:
            self.text.tag_remove(tag, "1.0", "end")
