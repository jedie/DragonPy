#!/usr/bin/env python

import argparse
import sys
import time


class MemoryInfo2Comments:
    def __init__(self, rom_info_file):
        self.mem_info = self._get_rom_info(rom_info_file)

    def eval_addr(self, addr):
        addr = addr.strip("$")
        return int(addr, 16)

    def _get_rom_info(self, rom_info_file):
        sys.stderr.write(
            f"Read ROM Info file: {rom_info_file.name!r}\n"
        )
        rom_info = []
        next_update = time.time() + 0.5
        for line_no, line in enumerate(rom_info_file):
            if time.time() > next_update:
                sys.stderr.write(
                    f"\rRead {line_no:d} lines..."
                )
                sys.stderr.flush()
                next_update = time.time() + 0.5

            try:
                addr_raw, comment = line.split(";", 1)
            except ValueError:
                continue

            try:
                start_addr_raw, end_addr_raw = addr_raw.split("-")
            except ValueError:
                start_addr_raw = addr_raw
                end_addr_raw = None

            start_addr = self.eval_addr(start_addr_raw)
            if end_addr_raw:
                end_addr = self.eval_addr(end_addr_raw)
            else:
                end_addr = start_addr

            rom_info.append(
                (start_addr, end_addr, comment.strip()),
            )
        sys.stderr.write(
            f"ROM Info file: {rom_info_file.name!r} read.\n",
        )
        return rom_info

    def create_comments(self, outfile):
        for start_addr, _end_addr, comment in self.mem_info:
            comment = comment.replace('"', '\\"')
            comment = comment.replace('$', '\\$')
            outfile.write(
                f'\tcomment=0x{start_addr:x},"{comment}" \\\n'
            )
#            outfile.write(
#                '\tlabel="%s",0x%x \\\n' % (comment, start_addr)
#            )


def main(args):
    rom_info = MemoryInfo2Comments(args.infile)
    rom_info.create_comments(args.outfile)


def get_cli_args():
    parser = argparse.ArgumentParser(
        description="create comment statements from rom info for 6809dasm.pl"
    )
    parser.add_argument('infile', nargs='?',
                        type=argparse.FileType('r'), default=sys.stdin,
                        help="ROM Addresses info file or stdin"
                        )
    parser.add_argument('outfile', nargs='?',
                        type=argparse.FileType('w'), default=sys.stdout,
                        help="output file or stdout"
                        )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    #    sys.argv += ["../ROM Addresses/Dragon32.txt"]

    args = get_cli_args()
    main(args)
