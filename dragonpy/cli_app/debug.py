from __future__ import annotations

import logging

from rich import print  # noqa

from dragonpy.cli_app import cli


@cli.command()
def log_list():
    """
    List all exiting loggers and exit.
    """
    print("A list of all loggers:")
    for log_name in sorted(logging.Logger.manager.loggerDict):
        print(f"\t{log_name}")
