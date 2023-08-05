import subprocess
from unittest import TestCase

from bx_py_utils.path import assert_is_file
from manageprojects.test_utils.click_cli_utils import subprocess_cli
from manageprojects.test_utils.project_setup import check_editor_config, get_py_max_line_length
from manageprojects.utilities import code_style
from packaging.version import Version

from dragonpy import __version__
from dragonpy.cli.cli_app import PACKAGE_ROOT


class ProjectSetupTestCase(TestCase):
    def test_version(self):
        self.assertIsNotNone(__version__)

        version = Version(__version__)  # Will raise InvalidVersion() if wrong formatted
        self.assertEqual(str(version), __version__)

        cli_bin = PACKAGE_ROOT / 'cli.py'
        assert_is_file(cli_bin)

        output = subprocess.check_output([cli_bin, 'version'], text=True)
        self.assertIn(f'dragonpy v{__version__}', output)

        dev_cli_bin = PACKAGE_ROOT / 'dev-cli.py'
        assert_is_file(dev_cli_bin)

        output = subprocess.check_output([dev_cli_bin, 'version'], text=True)
        self.assertIn(f'dragonpy v{__version__}', output)

    def test_code_style(self):
        dev_cli_bin = PACKAGE_ROOT / 'dev-cli.py'
        assert_is_file(dev_cli_bin)

        try:
            output = subprocess_cli(
                cli_bin=dev_cli_bin,
                args=('check-code-style',),
                exit_on_error=False,
            )
        except subprocess.CalledProcessError as err:
            self.assertIn('.venv/bin/darker', err.stdout)  # darker was called?
        else:
            if 'Code style: OK' in output:
                self.assertIn('.venv/bin/darker', output)  # darker was called?
                return  # Nothing to fix -> OK

        # Try to "auto" fix code style:

        try:
            output = subprocess_cli(
                cli_bin=dev_cli_bin,
                args=('fix-code-style',),
                exit_on_error=False,
            )
        except subprocess.CalledProcessError as err:
            output = err.stdout

        self.assertIn('.venv/bin/darker', output)  # darker was called?

        # Check again and display the output:

        try:
            code_style.check(package_root=PACKAGE_ROOT)
        except SystemExit as err:
            self.assertEqual(err.code, 0, 'Code style error, see output above!')

    def test_check_editor_config(self):
        check_editor_config(package_root=PACKAGE_ROOT)

        max_line_length = get_py_max_line_length(package_root=PACKAGE_ROOT)
        self.assertEqual(max_line_length, 119)
