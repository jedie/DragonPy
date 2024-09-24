from unittest import TestCase

from cli_base.cli_tools import git_history


class ReadmeHistoryTestCase(TestCase):
    def test_readme_history(self):
        updated = git_history.update_readme_history(verbosity=2)
        self.assertFalse(updated, 'README.md was not updated: Commit changes!')
