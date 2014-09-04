#!/usr/bin/env python
# encoding:utf8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    https://pythonhosted.org/pypng/index.html

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function


from dragonpy.Dragon32.DragonFont import png
import sys
import unicodedata


def group(lst, n):
    """
    from https://code.activestate.com/recipes/303060-group-a-list-into-sequential-n-tuples/

    group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]

    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.

    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    """
    return list(zip(*[lst[i::n] for i in range(n)]))


def generate_font(filename, row_count, column_count, characters):
    all_bits = {}
    with open(filename, "rb") as f:
        r = png.Reader(file=f)
        png_data = r.read()

        width, height, data, info = png_data
        print("Size:", width, height)
        print("Info:", info)

        for row_no, row_array in enumerate(data):
            char_offset = divmod(row_no, height / column_count)[0] * row_count
            for pos, bit in enumerate(row_array):
                char_no = divmod(pos, width / row_count)[0] + char_offset
                char = characters[char_no]

                all_bits.setdefault(char, []).append(bit)
#             print "%2s %s" % (
#                 row_no,
#                 "".join([str(i) for i in row_array])
#             )
    return all_bits, width / row_count


BACKGROUND_CHAR = "."
FOREGROUND_CHAR = "X"

def display_dict(all_bits, characters, width):
    """
    padding_top=3, padding_bottom=2
    """
    padding = '        "%s",' % (BACKGROUND_CHAR * width)

    print('BACKGROUND_CHAR = "%s"' % BACKGROUND_CHAR)
    print('FOREGROUND_CHAR = "%s"' % FOREGROUND_CHAR)
    print("CHARS_DICT = {")
    for char in characters:
        name = unicodedata.name(char)
        print('    %s: (# %s' % (repr(char), name))
        print(padding)
        print(padding)
        print(padding)

        bits = all_bits[char]
        for g in group(bits, width):
            line = "".join([str(i) for i in g])
            line = line.replace("0", BACKGROUND_CHAR)
            line = line.replace("1", FOREGROUND_CHAR)
            print('        "%s",' % line)
        print(padding)
        print(padding)
        print('    ),')
    print("}")


if __name__ == "__main__":
    CHARS6847 = (
        ''' !"#$%&'()*+,-./'''
        '''0123456789:;<=>?'''
        '''@ABCDEFGHIJKLMNO'''
        '''PQRSTUVWXYZ[\]''' + "\N{UPWARDS ARROW}\N{LEFTWARDS ARROW}"
        '''`abcdefghijklmno'''
        '''pqrstuvwxyz{|}~§'''
    )
    print(CHARS6847)
    all_bits, width = generate_font(
        "font-6847.png", # From XRoar
        row_count=16, # How many characters per row
        column_count=6, # How many lines of characters
        characters=CHARS6847,
    )

    # see: http://archive.worldofdragon.org/index.php?title=CharMap
    needed_chars = (
        '''@'''
        '''ABCDEFGHIJKLMNOPQRSTUVWXYZ'''
        '''[\]''' + "\N{UPWARDS ARROW}\N{LEFTWARDS ARROW}"
        ''' !"#$%&'()*+,-./'''
        '''0123456789'''
        ''':;<=>?'''
    )
    display_dict(all_bits, needed_chars, width)
    print(" --- END --- ")
