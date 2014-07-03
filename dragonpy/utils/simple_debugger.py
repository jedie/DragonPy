#!/usr/bin/env python
# coding: utf-8

"""
borrowed from http://code.activestate.com/recipes/52215/

usage:

try:
    # ...do something...
except:
    print_exc_plus()
"""

import sys
import traceback

MAX_CHARS = 256

class ColorOut(object):
    """
    Borrowed from Django:
    http://code.djangoproject.com/browser/django/trunk/django/utils/termcolors.py

    >>> c = ColorOut()
    >>> c.supports_colors()
    True
    >>> c.color_support = True
    >>> c.colorize('no color')
    'no color'
    >>> c.colorize('bold', opts=("bold",))
    '\\x1b[1mbold\\x1b[0m'
    >>> c.colorize("colors!", foreground="red", background="blue", opts=("bold", "blink"))
    '\\x1b[31;44;1;5mcolors!\\x1b[0m'
    """
    color_names = ('black', 'red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white')
    foreground_colors = dict([(color_names[x], '3%s' % x) for x in range(8)])
    background_colors = dict([(color_names[x], '4%s' % x) for x in range(8)])
    opt_dict = {'bold': '1', 'underscore': '4', 'blink': '5', 'reverse': '7', 'conceal': '8'}

    def __init__(self):
        self.color_support = self.supports_colors()

    def supports_colors(self):
        if sys.platform in ('win32', 'Pocket PC'):
            return False

        # isatty is not always implemented!
        if hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
            return True
        else:
            return False

    def colorize(self, text, foreground=None, background=None, opts=()):
        """
        Returns your text, enclosed in ANSI graphics codes.
        """
        if not self.color_support:
            return text

        code_list = []

        if foreground:
            code_list.append(self.foreground_colors[foreground])
        if background:
            code_list.append(self.background_colors[background])

        for option in opts:
            code_list.append(self.opt_dict[option])

        if not code_list:
            return text

        return "\x1b[%sm%s\x1b[0m" % (';'.join(code_list), text)
c = ColorOut()


def print_exc_plus():
    """
    Print the usual traceback information, followed by a listing of all the
    local variables in each frame.
    """
    sys.stderr.flush() # for eclipse
    sys.stdout.flush() # for eclipse

    tb = sys.exc_info()[2]
    while True:
        if not tb.tb_next:
            break
        tb = tb.tb_next
    stack = []
    f = tb.tb_frame
    while f:
        stack.append(f)
        f = f.f_back

    txt = traceback.format_exc()
    txt_lines = txt.splitlines()
    first_line = txt_lines.pop(0)
    last_line = txt_lines.pop(-1)
    print c.colorize(first_line, foreground="red")
    for line in txt_lines:
        if line.strip().startswith("File"):
            print line
        else:
            print c.colorize(line, foreground="white", opts=("bold",))
    print c.colorize(last_line, foreground="red")

    print
    print c.colorize(
        "Locals by frame, most recent call first:",
        foreground="blue", opts=("bold",)
    )
    for frame in stack:

        print "\n ***", c.colorize(
            'File "%s", line %i, in %s' % (
                frame.f_code.co_filename,
                frame.f_lineno,
                frame.f_code.co_name,
            ),
            foreground="white",
            opts=("bold", "underscore")
        )

        for key, value in frame.f_locals.items():
            print "%30s = " % c.colorize(key, opts=("bold",)),
            # We have to be careful not to cause a new error in our error
            # printer! Calling str() on an unknown object could cause an
            # error we don't want.
            if isinstance(value, int):
                value = "$%x (decimal: %i)" % (value, value)
            else:
                value = repr(value)

            if len(value) > MAX_CHARS:
                value = "%s..." % value[:MAX_CHARS]

            try:
                print value
            except:
                print "<ERROR WHILE PRINTING VALUE>"
