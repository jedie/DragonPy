# coding: utf-8

"""
    DragonPy - Dragon 32 emulator in Python
    =======================================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

import logging

import six

xrange = six.moves.xrange

from dragonlib.api import Dragon32API
from dragonpy.Dragon32.keyboard_map import get_dragon_keymatrix_pia_result
from dragonpy.Dragon32.mem_info import get_dragon_meminfo
from dragonpy.core.configs import BaseConfig, DRAGON32
from dragonpy.Dragon32.Dragon32_rom import Dragon32Rom


log=logging.getLogger(__name__)


class Dragon32Cfg(BaseConfig):
    """
    see:
     * http://dragon32.info/info/memmap.html
     * http://dragon32.info/info/romref.html
    """
    CONFIG_NAME = DRAGON32
    MACHINE_NAME = "Dragon 32"

    # How does the keyboard polling routine starts with?
    PIA0B_KEYBOARD_START = 0x00

    RAM_START = 0x0000

    # 1KB RAM is not runnable and raise a error
    # 2-8 KB - BASIC Interpreter will be initialized. But every
    #          statement will end with a OM ERROR (Out of Memory)
    # 16 KB - Is usable

#     RAM_END = 0x03FF # 1KB
#     RAM_END = 0x07FF # 2KB # BASIC will always raise a OM ERROR!
#     RAM_END = 0x0FFF # 4KB # BASIC will always raise a OM ERROR!
#     RAM_END = 0x1FFF # 8KB # BASIC will always raise a OM ERROR!
#     RAM_END = 0x3FFF # 16KB # usable
    RAM_END = 0x7FFF # 32KB

    ROM_START = 0x8000
    ROM_END = 0xBFFF
    # ROM size: 0x4000 == 16384 Bytes

    """
    $8000-$bfff - d32.rom - size: $3fff (dez.: 16383) Bytes

    8000-9FFF Extended Color BASIC
    A000-BFFF Color BASIC
    C000-FEFF Program pak memory
    FF00-FFFF I/O, machine configuration, reset vectors
    """
    DEFAULT_ROMS = (
        Dragon32Rom(address=0x8000, max_size=0x4000),
    )

    # for unittests init:
    STARTUP_END_ADDR = 0xbbe5 # scan keyboard

    def __init__(self, cmd_args):
        super(Dragon32Cfg, self).__init__(cmd_args)

        self.machine_api = Dragon32API()

        if self.verbosity and self.verbosity <= logging.ERROR:
            self.mem_info = get_dragon_meminfo()

        self.periphery_class = None# Dragon32Periphery

        self.memory_byte_middlewares = {
            # (start_addr, end_addr): (read_func, write_func)
#             (0x0152, 0x0159): (None, self.keyboard_matrix_state),
#             (0x0115, 0x0119): (self.rnd_seed_read, self.rnd_seed_write),
#             (0x0112, 0x0113): (self.timer_value_read, self.timer_value_write),
        }
        self.memory_word_middlewares = {
            # (0x0019, 0x001F): (None, self.basic_addresses_write),
            # (0x0112, 0x0113): (self.timer_value_read_word, self.timer_value_write_word),
        }

    def keyboard_matrix_state(self, cpu, addr, value):
        log.critical(
            "%04x|      Set keyboard matrix state $%04x to $%02x %s\t\t\t|%s",
            cpu.last_op_address, addr, value, '{0:08b}'.format(value),
            self.mem_info.get_shortest(addr)
        )
        # cpu.memory.ram.print_dump(0x004f, 0x0054)
        return value

    def rnd_seed_read(self, cycles, last_op_address, address, byte):
        log.critical("%04x| read $%02x RND() seed from: $%04x", last_op_address, byte, address)
        return byte

    def rnd_seed_write(self, cycles, last_op_address, address, byte):
        log.critical("%04x| write $%02x RND() seed to: $%04x", last_op_address, byte, address)
        return byte

    def timer_value_read(self, cycles, last_op_address, address, byte):
        log.critical("%04x| read byte $%02x TIMER value from: $%04x", last_op_address, byte, address)
        return byte

    def timer_value_write(self, cycles, last_op_address, address, byte):
        log.critical("%04x| write byte $%02x TIMER value to: $%04x", last_op_address, byte, address)
        return byte

    def timer_value_read_word(self, cycles, last_op_address, address, byte):
        log.critical("%04x| read word $%04x TIMER value from: $%04x", last_op_address, byte, address)
        return byte

    def timer_value_write_word(self, cycles, last_op_address, address, byte):
        log.critical("%04x| write word $%04x TIMER value to: $%04x", last_op_address, byte, address)
        return byte

    def basic_addresses_write(self, cycles, last_op_address, address, word):
#        PROGRAM_START_ADDR = 0x0019
#        VARIABLES_START_ADDR = 0x001B
#        ARRAY_START_ADDR = 0x001D
#        FREE_SPACE_START_ADDR = 0x001F
        log.critical("%04x| write $%04x to $%04x", last_op_address, word, address)
        return word

    def get_initial_RAM(self):
        """
        init the Dragon RAM
        See: http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4444
        """
        mem_FF = [0xff for _ in xrange(4)]
        mem_00 = [0x00 for _ in xrange(4)]

        mem = []
        for _ in xrange(self.RAM_SIZE // 8):
            mem += mem_FF
            mem += mem_00

        return mem

    def pia_keymatrix_result(self, inkey, pia0b):
        return get_dragon_keymatrix_pia_result(inkey, pia0b)

config = Dragon32Cfg


#------------------------------------------------------------------------------


