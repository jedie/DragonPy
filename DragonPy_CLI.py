#!/usr/bin/env python
# coding: utf-8

"""
    DragonPy - CLI
    ~~~~~~~~~~~~~~

    :created: 2013-2014 by Jens Diemer - www.jensdiemer.de
    :copyleft: 2013-2014 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from dragonpy.DragonPy_CLI import get_cli
from dragonpy.utils.simple_debugger import print_exc_plus

if __name__ == "__main__":
    try:
        cli = get_cli()
        cli.run()
    except SystemExit:
        pass
    except:
        print_exc_plus()
