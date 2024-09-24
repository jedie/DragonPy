import sys
from pathlib import Path

import click
from cli_base.cli_tools.dev_tools import run_unittest_cli
from cli_base.cli_tools.subprocess_utils import verbose_check_call
from cli_base.cli_tools.verbosity import OPTION_KWARGS_VERBOSE
from cli_base.run_pip_audit import run_pip_audit
from manageprojects.utilities.publish import publish_package

import dragonpy
from dragonpy.cli_dev import PACKAGE_ROOT, cli


@cli.command()
def install():
    """
    Run pip-sync and install 'cli_base' via pip as editable.
    """
    verbose_check_call('pip-sync', PACKAGE_ROOT / 'requirements.dev.txt')
    verbose_check_call('pip', 'install', '--no-deps', '-e', '.')


@cli.command()
@click.option('-v', '--verbosity', **OPTION_KWARGS_VERBOSE)
def pip_audit(verbosity: int):
    """
    Run pip-audit check against current requirements files
    """
    run_pip_audit(base_path=PACKAGE_ROOT, verbosity=verbosity)


@cli.command()
def update():
    """
    Update "requirements*.txt" dependencies files
    """
    bin_path = Path(sys.executable).parent

    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip')
    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip-tools')

    extra_env = dict(
        CUSTOM_COMPILE_COMMAND='./dev-cli.py update',
    )

    pip_compile_base = [bin_path / 'pip-compile', '--verbose', '--upgrade']

    # Only "prod" dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--output-file',
        'requirements.txt',
        extra_env=extra_env,
    )

    # dependencies + "dev"-optional-dependencies:
    verbose_check_call(
        *pip_compile_base,
        'pyproject.toml',
        '--extra=dev',
        '--output-file',
        'requirements.dev.txt',
        extra_env=extra_env,
    )

    run_pip_audit(base_path=PACKAGE_ROOT)

    # Install new dependencies in current .venv:
    verbose_check_call(bin_path / 'pip-sync', 'requirements.dev.txt')


@cli.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    run_unittest_cli(verbose=False, exit_after_run=False)  # Don't publish a broken state

    publish_package(
        module=dragonpy,
        package_path=PACKAGE_ROOT,
        distribution_name='DragonPyEmulator',
    )
