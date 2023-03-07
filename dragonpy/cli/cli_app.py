import inspect
import locale
import logging
import sys
from pathlib import Path

import rich_click as click
from bx_py_utils.path import assert_is_file
from manageprojects.utilities import code_style
from manageprojects.utilities.publish import publish_package
from manageprojects.utilities.subprocess_utils import verbose_check_call
from manageprojects.utilities.version_info import print_version
from rich import print  # noqa
from rich_click import RichGroup

import dragonpy
from basic_editor.editor import run_basic_editor
from dragonpy import constants
from dragonpy.components.rom import ROMFileError
from dragonpy.constants import VERBOSITY_DEFAULT_VALUE, VERBOSITY_DICT
from dragonpy.core.configs import machine_dict
from dragonpy.core.gui_starter import gui_mainloop


logger = logging.getLogger(__name__)


# use user's preferred locale
# e.g.: for formatting cycles/sec number
locale.setlocale(locale.LC_ALL, '')


PACKAGE_ROOT = Path(dragonpy.__file__).parent.parent
assert_is_file(PACKAGE_ROOT / 'pyproject.toml')

OPTION_ARGS_DEFAULT_TRUE = dict(is_flag=True, show_default=True, default=True)
OPTION_ARGS_DEFAULT_FALSE = dict(is_flag=True, show_default=True, default=False)
ARGUMENT_EXISTING_DIR = dict(
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, path_type=Path)
)
ARGUMENT_NOT_EXISTING_DIR = dict(
    type=click.Path(exists=False, file_okay=False, dir_okay=True, readable=False, writable=True, path_type=Path)
)
ARGUMENT_EXISTING_FILE = dict(
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path)
)


OPTION_KWARGS_VERBOSITY = dict(
    type=click.Choice([str(number) for number in sorted(VERBOSITY_DICT.keys())]),
    default=str(VERBOSITY_DEFAULT_VALUE),
    show_default=True,
    help=", ".join(f'{number}:{text}' for number, text in VERBOSITY_DICT.items()),
)
OPTION_KWARGS_MACHINE = dict(
    type=click.Choice(sorted(machine_dict.keys())),
    default=machine_dict.DEFAULT,
    show_default=True,
    help='Used machine configuration',
)


class ClickGroup(RichGroup):  # FIXME: How to set the "info_name" easier?
    def make_context(self, info_name, *args, **kwargs):
        info_name = './cli.py'
        return super().make_context(info_name, *args, **kwargs)


@click.group(
    cls=ClickGroup,
    epilog=constants.CLI_EPILOG,
)
def cli():
    pass


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def mypy(verbose: bool = True):
    """Run Mypy (configured in pyproject.toml)"""
    verbose_check_call('mypy', '.', cwd=PACKAGE_ROOT, verbose=verbose, exit_on_error=True)


cli.add_command(mypy)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def coverage(verbose: bool = True):
    """
    Run and show coverage.
    """
    verbose_check_call('coverage', 'run', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'combine', '--append', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'report', '--fail-under=30', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'xml', verbose=verbose, exit_on_error=True)
    verbose_check_call('coverage', 'json', verbose=verbose, exit_on_error=True)


cli.add_command(coverage)


@click.command()
def install():
    """
    Run pip-sync and install 'dragonpy' via pip as editable.
    """
    verbose_check_call('pip-sync', PACKAGE_ROOT / 'requirements.dev.txt')
    verbose_check_call('pip', 'install', '-e', '.')


cli.add_command(install)


@click.command()
def safety():
    """
    Run safety check against current requirements files
    """
    verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')


cli.add_command(safety)


@click.command()
def update():
    """
    Update "requirements*.txt" dependencies files
    """
    bin_path = Path(sys.executable).parent

    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip')
    verbose_check_call(bin_path / 'pip', 'install', '-U', 'pip-tools')

    extra_env = dict(
        CUSTOM_COMPILE_COMMAND='./cli.py update',
    )

    pip_compile_base = [
        bin_path / 'pip-compile',
        '--verbose',
        '--allow-unsafe',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--resolver=backtracking',  # https://pip-tools.readthedocs.io/en/latest/#deprecations
        '--upgrade',
        '--generate-hashes',
    ]

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

    verbose_check_call('safety', 'check', '-r', 'requirements.dev.txt')

    # Install new dependencies in current .venv:
    verbose_check_call('pip-sync', 'requirements.dev.txt')


cli.add_command(update)


@click.command()
def publish():
    """
    Build and upload this project to PyPi
    """
    _run_unittest_cli(verbose=False, exit_after_run=False)  # Don't publish a broken state

    publish_package(
        module=dragonpy,
        package_path=PACKAGE_ROOT,
        distribution_name='DragonPyEmulator',
    )


cli.add_command(publish)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def fix_code_style(color: bool = True, verbose: bool = False):
    """
    Fix code style of all dragonpy source code files via darker
    """
    code_style.fix(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(fix_code_style)


@click.command()
@click.option('--color/--no-color', **OPTION_ARGS_DEFAULT_TRUE)
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
def check_code_style(color: bool = True, verbose: bool = False):
    """
    Check code style by calling darker + flake8
    """
    code_style.check(package_root=PACKAGE_ROOT, color=color, verbose=verbose)


cli.add_command(check_code_style)


@click.command()
def update_test_snapshot_files():
    """
    Update all test snapshot files (by remove and recreate all snapshot files)
    """

    def iter_snapshot_files():
        yield from PACKAGE_ROOT.rglob('*.snapshot.*')

    removed_file_count = 0
    for item in iter_snapshot_files():
        item.unlink()
        removed_file_count += 1
    print(f'{removed_file_count} test snapshot files removed... run tests...')

    # Just recreate them by running tests:
    _run_unittest_cli(
        extra_env=dict(
            RAISE_SNAPSHOT_ERRORS='0',  # Recreate snapshot files without error
        ),
        verbose=False,
        exit_after_run=False,
    )

    new_files = len(list(iter_snapshot_files()))
    print(f'{new_files} test snapshot files created, ok.\n')


cli.add_command(update_test_snapshot_files)


def _run_unittest_cli(extra_env=None, verbose=True, exit_after_run=True):
    """
    Call the origin unittest CLI and pass all args to it.
    """
    if extra_env is None:
        extra_env = dict()

    extra_env.update(
        dict(
            PYTHONUNBUFFERED='1',
            PYTHONWARNINGS='always',
        )
    )

    args = sys.argv[2:]
    if not args:
        if verbose:
            args = ('--verbose', '--locals', '--buffer')
        else:
            args = ('--locals', '--buffer')

    verbose_check_call(
        sys.executable,
        '-m',
        'unittest',
        *args,
        timeout=15 * 60,
        extra_env=extra_env,
    )
    if exit_after_run:
        sys.exit(0)


@click.command()  # Dummy command
def test():
    """
    Run unittests
    """
    _run_unittest_cli()


cli.add_command(test)


def _run_tox():
    verbose_check_call(sys.executable, '-m', 'tox', *sys.argv[2:])
    sys.exit(0)


@click.command()  # Dummy "tox" command
def tox():
    """
    Run tox
    """
    _run_tox()


cli.add_command(tox)


@click.command()
def version():
    """Print version and exit"""
    # Pseudo command, because the version always printed on every CLI call ;)
    sys.exit(0)


cli.add_command(version)


@click.command()
def gui():
    """Start the DragonPy tkinter starter GUI"""
    gui_mainloop(confirm_exit=False)


cli.add_command(gui)


@click.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSITY)
@click.option('--trace/--no-trace', **OPTION_ARGS_DEFAULT_FALSE, help='Create trace lines')
@click.option(
    '--max-ops',
    type=int,
    default=None,
    show_default=True,
    help='If given: Stop CPU after given cycles else: run forever',
)
@click.option('--machine', **OPTION_KWARGS_MACHINE)
def run(machine: str, trace: bool, max_ops: int | None, verbosity: str):
    """Run a machine emulation"""
    machine_run_func, MachineConfigClass = machine_dict[machine]
    print(f'Use machine func: {machine_run_func.__name__}')
    cfg_dict = {
        'verbosity': int(verbosity),
        'trace': trace,
        'max_ops': max_ops,
    }
    print(cfg_dict)
    machine_run_func(cfg_dict)


cli.add_command(run)


@click.command()
@click.option('--verbosity', **OPTION_KWARGS_VERBOSITY)
@click.option('--machine', **OPTION_KWARGS_MACHINE)
def editor(machine: str, verbosity: str):
    """
    Run only the BASIC editor
    """
    machine_run_func, MachineConfigClass = machine_dict[machine]
    cfg_dict = {
        'verbosity': int(verbosity),
        'trace': False,
        'max_ops': None,
    }
    machine_cfg = MachineConfigClass(cfg_dict)
    run_basic_editor(machine_cfg)


cli.add_command(editor)


@click.command()
@click.option('--verbose/--no-verbose', **OPTION_ARGS_DEFAULT_FALSE)
@click.option(
    '--machines',
    '-m',
    multiple=True,
    type=click.Choice(sorted(machine_dict.keys())),
    default=None,
    help='Download ROM only for given machine(s). Leave empty to download all known ROMs',
)
def download_roms(machines: tuple[str] | None, verbose: bool = True):
    """
    Download/Test only ROM files
    """
    if not machines:
        machines = sorted(machine_dict.keys())
    print(f'Download ROMs for {machines}')
    success = 0
    for machine_name in machines:
        machine_run_func, machine_cfg = machine_dict[machine_name]
        print(f'Download / test ROM for {machine_name}:')

        for rom in machine_cfg.DEFAULT_ROMS:
            print(f"\tROM file: {rom.FILENAME}")
            try:
                content = rom.get_data()
            except ROMFileError as err:
                print(f'[red]{err}')
                continue

            size = len(content)
            print(f"\tfile size is ${size:04x} (dez.: {size:d}) Bytes\n")
            success += 1

    print(f'{success} ROMs succeed.')


cli.add_command(download_roms)


@click.command()
def log_list():
    """
    List all exiting loggers and exit.
    """
    print("A list of all loggers:")
    for log_name in sorted(logging.Logger.manager.loggerDict):
        print(f"\t{log_name}")


cli.add_command(log_list)


def main():
    print_version(dragonpy)
    print(
        inspect.cleandoc(
            """
            ********************************************************
            * DragonPy is a Open source (GPL v3 or later) emulator *
            * for the 30 years old homecomputer Dragon 32          *
            * and Tandy TRS-80 Color Computer (CoCo)...            *
            ********************************************************
            * Homepage: https://github.com/jedie/DragonPy          *
            ********************************************************
        """
        )
    )

    if len(sys.argv) >= 2:
        # Check if we just pass a command call
        command = sys.argv[1]
        if command == 'test':
            _run_unittest_cli()
        elif command == 'tox':
            _run_tox()

    # Execute Click CLI:
    cli.name = './cli.py'
    cli()
