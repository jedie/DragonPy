from cmd2 import CommandResult
from cmd2_ext_test import ExternalTestMixin
from dev_shell.tests.fixtures import CmdAppBaseTestCase

from dragonpy.dev_shell import DevShellApp, get_devshell_app_kwargs


class DevShellAppTester(ExternalTestMixin, DevShellApp):
    pass


class DevShellAppBaseTestCase(CmdAppBaseTestCase):
    """
    Base class for dev-shell tests
    """

    def get_app_instance(self):
        # Init the test app with the same kwargs as the real app
        # see: dev_shell.cmd2app.devshell_cmdloop()
        app = DevShellAppTester(**get_devshell_app_kwargs())
        return app


class DragonPyDevShellTestCase(DevShellAppBaseTestCase):
    def test_help_raw(self):
        out = self.app.app_cmd('help')

        assert isinstance(out, CommandResult)
        stdout = out.stdout
        assert 'Documented commands' in stdout
        assert 'gui' in stdout
        assert 'download_roms' in stdout
        assert 'run' in stdout
        assert 'editor' in stdout
        assert 'log_list' in stdout

    def test_help_via_execute(self):
        stdout, stderr = self.execute('help')
        assert stderr == ''
        assert 'Documented commands' in stdout
        assert 'gui' in stdout
        assert 'download_roms' in stdout
        assert 'run' in stdout
        assert 'editor' in stdout
        assert 'log_list' in stdout

    def test_help_run(self):
        stdout, stderr = self.execute('help run')
        assert stderr == ''
        assert 'Usage: run [-h]' in stdout
        assert '--machine ' in stdout
        assert ' --max-ops MAX_OPS ' in stdout
        assert 'CoCo2b, Dragon32, Dragon64' in stdout

    def test_download_roms(self):
        stdout, stderr = self.execute('download_roms')
        print(stdout)
        print(stderr)
        assert stderr == ''
        assert 'Download 7 platform roms...\n' in stdout
        assert '\n9 ROMs succeed.\n' in stdout
