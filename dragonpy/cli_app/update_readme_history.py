import sys

import rich_click as click
from cli_base.cli_tools import git_history
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE, setup_logging
from rich import print  # noqa

from dragonpy.cli_app import cli


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def update_readme_history(verbosity: int):
    """
    Update project history base on git commits/tags in README.md

    Will be exited with 1 if the README.md was updated otherwise with 0.

    Also, callable via e.g.:
        python -m cli_base update-readme-history -v
    """
    setup_logging(verbosity=verbosity)
    updated = git_history.update_readme_history(verbosity=verbosity)
    exit_code = 1 if updated else 0
    if verbosity:
        print(f'{exit_code=}')
    sys.exit(exit_code)
