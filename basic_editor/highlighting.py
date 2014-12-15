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

import pygments
from pygments.styles import get_style_by_name

from basic_editor.tkinter_utils import TkTextTag
from dragonlib.dragon32.pygments_lexer import BasicLexer


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

        self.lexer = BasicLexer()

        self.machine_api = editor.machine_api

        self.tags = self.create_tags()
        self.existing_tags = tuple(self.tags.values())

        # TODO: Add a bind callback list
        # see: http://www.python-forum.de/viewtopic.php?f=18&t=35275 (de)
        # self.editor.root.bind("<KeyRelease>", self.update)
        # self.editor.root.bind("<KeyRelease>", self.force_update)

        self.old_pos=None
        self.__update_interval()

    def __update_interval(self):
        """ highlight the current line """
        self.update()
        self.after_id = self.text.after(250, self.__update_interval)


    def force_update(self, event):
        print("force update")
        self.update(event, force=True)

    def update(self, event=None, force=False):
        pos = self.text.index(tkinter.INSERT)
        # print("update %s" % pos)
        if not force and pos == self.old_pos:
            # print("Skip")
            return

        self.recolorize()
        self.old_pos = pos

    # ---------------------------------------------------------------------------------------

    def create_tags(self):
        tags={}

        bold_font = font.Font(self.text, self.text.cget("font"))
        bold_font.configure(weight=font.BOLD)

        italic_font = font.Font(self.text, self.text.cget("font"))
        italic_font.configure(slant=font.ITALIC)

        bold_italic_font = font.Font(self.text, self.text.cget("font"))
        bold_italic_font.configure(weight=font.BOLD, slant=font.ITALIC)

        style = get_style_by_name("default")
        for ttype, ndef in style:
            # print(ttype, ndef)
            tag_font = None
            if ndef["bold"] and ndef["italic"]:
                tag_font = bold_italic_font
            elif ndef["bold"]:
                tag_font = bold_font
            elif ndef["italic"]:
                tag_font = italic_font

            if ndef["color"]:
                foreground = "#%s" % ndef["color"]
            else:
                foreground = None

            tags[ttype]=str(ttype)
            self.text.tag_configure(tags[ttype], foreground=foreground, font=tag_font)
            # self.text.tag_configure(str(ttype), foreground=foreground, font=tag_font)

        return tags

    def recolorize(self):
        # print("recolorize")
        listing = self.text.get("1.0", "end-1c")

        destinations = self.machine_api.renum_tool.get_destinations(listing)

        tokensource = self.lexer.get_tokens(listing)

        start_line=1
        start_index = 0
        end_line=1
        end_index = 0
        for ttype, value in tokensource:
            if "\n" in value:
                end_line += value.count("\n")
                end_index = len(value.rsplit("\n",1)[1])
            else:
                end_index += len(value)

            if value not in (" ", "\n"):
                index1 = "%s.%s" % (start_line, start_index)
                index2 = "%s.%s" % (end_line, end_index)

                for tagname in self.text.tag_names(index1): # FIXME
                    # print("remove %s" % tagname)
                    if tagname not in self.existing_tags: # Don"t remove e.g.: "current line"-tag
                        # print("Skip...")
                        continue
                    self.text.tag_remove(tagname, index1, index2)

                # Mark used line numbers extra:
                if start_index==0 and ttype==pygments.token.Name.Label:
                    if int(value) in destinations:
                        ttype = pygments.token.Name.Tag

                self.text.tag_add(self.tags[ttype], index1, index2)

            start_line = end_line
            start_index = end_index





class TkTextHighlightCurrentLine(BaseExtension):
    after_id = None

    def __init__(self, editor):
        super(TkTextHighlightCurrentLine, self).__init__(editor)

        self.tag_current_line = TkTextTag(self.text,
            background="#e8f2fe"
            # relief="raised", borderwidth=1,
        )

        self.current_line = None
        self.__update_interval()

        # self.editor.root.bind("<KeyRelease>", self.update)

    def update(self, event=None, force=False):
        """ highlight the current line """
        line_no = self.text.index(tkinter.INSERT).split(".")[0]

        # if not force:
            # if line_no == self.current_line:
#                 log.critical("no highlight line needed.")
#                 return

#         log.critical("highlight line: %s" % line_no)
#         self.current_line = line_no

        self.text.tag_remove(self.tag_current_line.id, "1.0", "end")
        self.text.tag_add(self.tag_current_line.id, "%s.0" % line_no, "%s.0+1lines" % line_no)

    def __update_interval(self):
        """ highlight the current line """
        self.update()
        self.after_id = self.text.after(250, self.__update_interval)


