import rich_click as click
from cli_base.cli_tools import code_style
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE
from cli_base.click_defaults import OPTION_ARGS_DEFAULT_TRUE

from dragonpy.cli_dev import PACKAGE_ROOT, cli


@cli.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def fix_code_style(color: bool, verbosity: int):
    """
    Fix code style of all cli_base source code files via darker
    """
    code_style.fix(package_root=PACKAGE_ROOT, darker_color=color, darker_verbose=verbosity > 0)


@cli.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def check_code_style(color: bool, verbosity: int):
    """
    Check code style by calling darker + flake8
    """
    code_style.check(package_root=PACKAGE_ROOT, darker_color=color, darker_verbose=verbosity > 0)
