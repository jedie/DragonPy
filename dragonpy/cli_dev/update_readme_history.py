import logging
import sys
from pathlib import Path

from cli_base.cli_tools import git_history
from cli_base.cli_tools.verbosity import setup_logging
from cli_base.tyro_commands import TyroVerbosityArgType
from rich import print  # noqa

from dragonpy.cli_dev import app


logger = logging.getLogger(__name__)


@app.command
def update_readme_history(verbosity: TyroVerbosityArgType):
    """
    Update project history base on git commits/tags in README.md

    Will be exited with 1 if the README.md was updated otherwise with 0.

    Also, callable via e.g.:
        python -m cli_base update-readme-history -v
    """
    setup_logging(verbosity=verbosity)

    logger.debug('%s called. CWD: %s', __name__, Path.cwd())
    updated = git_history.update_readme_history(verbosity=verbosity)
    exit_code = 1 if updated else 0
    if verbosity:
        print(f'{exit_code=}')
    sys.exit(exit_code)
