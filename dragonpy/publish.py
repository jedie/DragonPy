from pathlib import Path

import poetry_publish
import poetry_publish.publish
from creole.setup_utils import update_rst_readme
from poetry_publish.utils.subprocess_utils import verbose_check_call

import dragonpy


PACKAGE_ROOT = Path(dragonpy.__file__).parent.parent


def update_readme():
    return update_rst_readme(
        package_root=PACKAGE_ROOT,
        filename='README.creole'
    )


def publish():
    """
        Publish 'poetry-publish' to PyPi
        Call this via:
            $ poetry run publish
    """
    verbose_check_call('make', 'fix-code-style')  # don't publish if code style wrong

    poetry_publish.publish.poetry_publish(
        package_root=PACKAGE_ROOT,
        version=dragonpy.__version__,
        creole_readme=True  # don't publish if README.rst is not up-to-date
    )
