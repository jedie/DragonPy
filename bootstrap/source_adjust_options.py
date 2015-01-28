# coding: utf-8

# imports not really needed and just for the editor warning ;)
import sys
from boot_dragonpy import INST_TYPES


def adjust_options(options, args):
    # Note: old optparse modul is used :(
    # --- CUT here ---
    if options.install_type == None:
        sys.stderr.write("\n\nERROR:\nYou must add --install_type option (See README) !\n")
        sys.stderr.write("Available types: %s\n\n" % ", ".join(INST_TYPES))
        sys.exit(-1)

    sys.stdout.write("\nInstall type: %r\n" % options.install_type)