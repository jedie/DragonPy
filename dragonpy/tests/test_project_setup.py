import subprocess
from unittest import TestCase

from bx_py_utils.path import assert_is_file
from manageprojects.test_utils.project_setup import check_editor_config, get_py_max_line_length
from cli_base.cli_tools.code_style import assert_code_style
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
        return_code = assert_code_style(package_root=PACKAGE_ROOT)
        self.assertEqual(return_code, 0, 'Code style error, see output above!')

    def test_check_editor_config(self):
        check_editor_config(package_root=PACKAGE_ROOT)

        max_line_length = get_py_max_line_length(package_root=PACKAGE_ROOT)
        self.assertEqual(max_line_length, 119)
