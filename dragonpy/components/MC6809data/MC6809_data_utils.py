#!/usr/bin/env python

"""
    6809 instruction set data
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Generate a flat dict

    :copyleft: 2014 by Jens Diemer
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from dragonpy.components.MC6809data.MC6809_op_data import OP_DATA


def get_flat_opdata(OP_DATA):
    flat_opdata = {}
    for instr_data in OP_DATA.values():
        for mnemonic, mnemonic_data in instr_data["mnemonic"].items():
            for op_code, op_data in mnemonic_data["ops"].items():
                op_data["mnemonic"] = mnemonic
                op_data["needs_ea"] = mnemonic_data["needs_ea"]
                for key in ("read_from_memory", "write_to_memory", "register"):
                    op_data[key] = mnemonic_data[key]
                flat_opdata[op_code] = op_data
    return flat_opdata


MC6809OP_DATA_DICT = get_flat_opdata(OP_DATA)

del OP_DATA

if __name__ == '__main__':
    import pprint

    pprint.pprint(MC6809OP_DATA_DICT)