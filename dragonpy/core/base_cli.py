#!/usr/bin/env python2
# coding: utf-8

"""
    base commandline interface
    ==========================

    :created: 2013 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

import argparse
import logging
import os
import sys
from dragonlib.utils.logging_utils import log, setup_logging


def get_log_levels():
    levels = [5, 7] # FIXME
    levels += [level for level in logging._levelNames if isinstance(level, int)]
    return levels

LOG_LEVELS = get_log_levels()


class Base_CLI(object):
    DESCRIPTION = None
    EPOLOG = None
    VERSION = None
    DEFAULT_LOG_FORMATTER = "%(message)s"

    def __init__(self):
        self.logfilename = None

        arg_kwargs = {}
        if self.DESCRIPTION is not None:
            arg_kwargs["description"] = self.DESCRIPTION
        if self.EPOLOG is not None:
            arg_kwargs["epilog"] = self.EPOLOG
        if self.VERSION is not None:
            arg_kwargs["version"] = self.VERSION

        self.parser = argparse.ArgumentParser(**arg_kwargs)

        self.parser.add_argument(
            "--verbosity", type=int, choices=LOG_LEVELS, default=logging.WARNING,
            help=(
                "verbosity level to stdout (lower == more output!)"
                " (default: %s)" % logging.INFO
            )
        )
        self.parser.add_argument(
            "--log_formatter", default=self.DEFAULT_LOG_FORMATTER,
            help=(
                "see: http://docs.python.org/2/library/logging.html#logrecord-attributes"
            )
        )

    def parse_args(self):
        if self.DESCRIPTION is not None:
            print
            print self.DESCRIPTION, self.VERSION
            print "-"*79
            print

        args = self.parser.parse_args()

#         for arg, value in sorted(vars(args).items()):
#             log.debug("argument %s: %r", arg, value)
#             print "argument %s: %r" % (arg, value)

        return args

    def setup_logging(self, args):
        self.verbosity = args.verbosity
        log_formatter = logging.Formatter(
            args.log_formatter or self.DEFAULT_LOG_FORMATTER
        )

        setup_logging(log, self.verbosity, log_formatter=log_formatter)


if __name__ == "__main__":
    import doctest
    print doctest.testmod(
        verbose=False
        # verbose=True
    )
