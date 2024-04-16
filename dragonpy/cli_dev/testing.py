import rich_click as click
from cli_base.cli_tools.dev_tools import run_coverage, run_tox, run_unittest_cli
from cli_base.cli_tools.subprocess_utils import verbose_check_call
from cli_base.cli_tools.test_utils.snapshot import UpdateTestSnapshotFiles
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE

from dragonpy.cli_dev import PACKAGE_ROOT, cli


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def mypy(verbosity: int):
    """Run Mypy (configured in pyproject.toml)"""
    verbose_check_call('mypy', '.', cwd=PACKAGE_ROOT, verbose=verbosity > 0, exit_on_error=True)


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def update_test_snapshot_files(verbosity: int):
    """
    Update all test snapshot files (by remove and recreate all snapshot files)
    """

    with UpdateTestSnapshotFiles(root_path=PACKAGE_ROOT, verbose=verbosity > 0):
        # Just recreate them by running tests:
        run_unittest_cli(
            extra_env=dict(
                RAISE_SNAPSHOT_ERRORS='0',  # Recreate snapshot files without error
            ),
            verbose=verbosity > 1,
            exit_after_run=False,
        )


@cli.command()  # Dummy command
def test():
    """
    Run unittests
    """
    run_unittest_cli()


@cli.command()  # Dummy command
def coverage():
    """
    Run tests and show coverage report.
    """
    run_coverage()


@cli.command()  # Dummy "tox" command
def tox():
    """
    Run tox
    """
    run_tox()
