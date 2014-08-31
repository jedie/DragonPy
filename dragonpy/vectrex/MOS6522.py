# encoding:utf8

"""
    DragonPy
    ========

    :created: 2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""


from dragonlib.utils.logging_utils import log


class MOS6522VIA(object):
    """
    MOS Technology 6522 Versatile Interface Adapter (VIA)

    https://en.wikipedia.org/wiki/MOS_Technology_6522

    $D000 - $D7FF 6522 interface adapter
    $D800 - $DFFF 6522 / RAM ?!?
    """
    def __init__(self, cfg, memory):
        self.cfg = cfg
        self.memory = memory

        self.memory.add_read_byte_callback(
            callback_func=self.read_byte,
            start_addr=0xd000,
            end_addr=0xdfff
        )

        self.memory.add_write_byte_callback(
            callback_func=self.write_byte,
            start_addr=0xd000,
            end_addr=0xdfff
        )

    def read_byte(self, cpu_cycles, op_address, address):
        log.error("%04x| TODO: 6522 read byte from $%04x - Send 0x00 back", op_address, address)
        return 0x00

    def write_byte(self, cpu_cycles, op_address, address, value):
        log.error("%04x| TODO: 6522 write $%02x to $%04x", op_address, value, address)
