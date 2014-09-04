# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


import string

def invert_shift(chars):
    """
    >>> invert_shift("a")
    'A'
    >>> invert_shift("A")
    'a'

    >>> invert_shift("123 foo 456 BAR #!")
    '123 FOO 456 bar #!'
    """
    result = ""
    for char in chars:
        if char in string.ascii_lowercase:
#             log.critical("auto shift lowercase char %s to UPPERCASE", repr(char))
            char = char.upper()
        elif char in string.ascii_uppercase:
#             log.critical("auto shift UPPERCASE char %s to lowercase", repr(char))
            char = char.lower()
        result += char
    return result


if __name__ == '__main__':
    import doctest
    print(doctest.testmod(
        # verbose=1
    ))
