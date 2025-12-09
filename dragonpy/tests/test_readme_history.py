from unittest import TestCase

from cli_base.cli_tools.git_history import update_readme_history


class ReadmeHistoryTestCase(TestCase):
    def test_readme_history(self):
        update_readme_history(raise_update_error=True)
