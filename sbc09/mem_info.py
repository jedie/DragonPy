
import logging

from utils.memory_info import BaseMemoryInfo

log = logging.getLogger(__name__)

class SBC09MemInfo(BaseMemoryInfo):
    MEM_INFO = (
        # TODO: generated from "monitor.lst"

        (0xfff2, 0xfff2, 'SWI3'),
        (0xfff4, 0xfff4, 'SWI2'),
        (0xfff6, 0xfff6, 'FIRQ'),
        (0xfff8, 0xfff8, 'IRQ'),
        (0xfffa, 0xfffa, 'SWI'),
        (0xfffc, 0xfffc, 'NMI'),
        (0xfffe, 0xfffe, 'RESET'),

        # manually inserted:

        # Memory map of SBC
        (0x0, 0x40, "Zero page variables reserved by monitor and O.S."),
        (0x40, 0xFF , "Zero page portion for user programs."),
        (0x100, 0x17F , "Xmodem buffer 0, terminal input buffer"),
        (0x180, 0x1FF , "Xmodem buffer 1, terminal output buffer"),
        (0x200, 0x27F , "Terminal input line"),
        (0x280, 0x2FF , "Variables reserved by monitor and O.S."),
        (0x300, 0x400 , "System stack"),
        (0x400, 0x7FFF , "RAM for user programs and data"),
        (0x8000, 0xDFFF , "PROM for user programs"),
        (0xE000, 0xE1FF , "I/O addresses"),
        (0xE200, 0xE3FF , "Reserved"),
        (0xE400, 0xFFFF , "Monitor ROM"),

        (0xe000, 0xe000, "Control/status port of ACIA"),
        (0xe001, 0xe001, "Data port of ACIA"),
    )


def print_out(txt):
    print txt


def get_sbc09_meminfo():
    return SBC09MemInfo(log.debug)


if __name__ == "__main__":
    mem_info = SBC09MemInfo(print_out)

    mem_info(0xe000) # SERIAL INTERFACE
