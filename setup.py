#!/usr/bin/env python
# coding: utf-8

"""
    distutils setup
    ~~~~~~~~~~~~~~~

    :copyleft: 2014-2015 by the DragonPy team, see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""

from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages

import os
import sys
import subprocess
import shutil

from dragonpy import __version__, DISTRIBUTION_NAME, DIST_GROUP, ENTRY_POINT

PACKAGE_ROOT = os.path.dirname(os.path.abspath(__file__))


# convert creole to ReSt on-the-fly, see also:
# https://code.google.com/p/python-creole/wiki/UseInSetup
try:
    from creole.setup_utils import get_long_description
except ImportError as err:
    if "check" in sys.argv or "register" in sys.argv or "sdist" in sys.argv or "--long-description" in sys.argv:
        raise ImportError("%s - Please install python-creole >= v0.8 -  e.g.: pip install python-creole" % err)
    long_description = None
else:
    long_description = get_long_description(PACKAGE_ROOT)


if "publish" in sys.argv:
    """
    'publish' helper for setup.py

    Build and upload to PyPi, if...
        ... __version__ doesn't contains "dev"
        ... we are on git 'master' branch
        ... git repository is 'clean' (no changed files)

    Upload with "twine", git tag the current version and git push --tag

    The cli arguments will be pass to 'twine'. So this is possible:
     * Display 'twine' help page...: ./setup.py publish --help
     * use testpypi................: ./setup.py publish --repository=test

    TODO: Look at: https://github.com/zestsoftware/zest.releaser

    Source: https://github.com/jedie/python-code-snippets/blob/master/CodeSnippets/setup_publish.py
    copyleft 2015-2017 Jens Diemer - GNU GPL v2+
    """
    if sys.version_info[0] == 2:
        input = raw_input

    import_error = False
    try:
        # Test if wheel is installed, otherwise the user will only see:
        #   error: invalid command 'bdist_wheel'
        import wheel
    except ImportError as err:
        print("\nError: %s" % err)
        print("\nMaybe https://pypi.org/project/wheel is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install wheel")
        import_error = True

    try:
        import twine
    except ImportError as err:
        print("\nError: %s" % err)
        print("\nMaybe https://pypi.org/project/twine is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install twine")
        import_error = True

    if import_error:
        sys.exit(-1)

    def verbose_check_output(*args):
        """ 'verbose' version of subprocess.check_output() """
        call_info = "Call: %r" % " ".join(args)
        try:
            output = subprocess.check_output(args, universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as err:
            print("\n***ERROR:")
            print(err.output)
            raise
        return call_info, output

    def verbose_check_call(*args):
        """ 'verbose' version of subprocess.check_call() """
        print("\tCall: %r\n" % " ".join(args))
        subprocess.check_call(args, universal_newlines=True)

    def confirm(txt):
        print("\n%s" % txt)
        if input("\nPublish anyhow? (Y/N)").lower() not in ("y", "j"):
            print("Bye.")
            sys.exit(-1)

    if "dev" in __version__:
        confirm("WARNING: Version contains 'dev': v%s\n" % __version__)

    print("\nCheck if we are on 'master' branch:")
    call_info, output = verbose_check_output("git", "branch", "--no-color")
    print("\t%s" % call_info)
    if "* master" in output:
        print("OK")
    else:
        confirm("\nNOTE: It seems you are not on 'master':\n%s" % output)

    print("\ncheck if if git repro is clean:")
    call_info, output = verbose_check_output("git", "status", "--porcelain")
    print("\t%s" % call_info)
    if output == "":
        print("OK")
    else:
        print("\n *** ERROR: git repro not clean:")
        print(output)
        sys.exit(-1)

    print("\nRun './setup.py check':")
    call_info, output = verbose_check_output("./setup.py", "check")
    if "warning" in output:
        print(output)
        confirm("Warning found!")
    else:
        print("OK")

    print("\ncheck if pull is needed")
    verbose_check_call("git", "fetch", "--all")
    call_info, output = verbose_check_output("git", "log", "HEAD..origin/master", "--oneline")
    print("\t%s" % call_info)
    if output == "":
        print("OK")
    else:
        print("\n *** ERROR: git repro is not up-to-date:")
        print(output)
        sys.exit(-1)
    verbose_check_call("git", "push")

    print("\nCleanup old builds:")
    def rmtree(path):
        path = os.path.abspath(path)
        if os.path.isdir(path):
            print("\tremove tree:", path)
            shutil.rmtree(path)
    rmtree("./dist")
    rmtree("./build")

    print("\nbuild but don't upload...")
    log_filename="build.log"
    with open(log_filename, "a") as log:
        call_info, output = verbose_check_output(
            sys.executable or "python",
            "setup.py", "sdist", "bdist_wheel", "bdist_egg"
        )
        print("\t%s" % call_info)
        log.write(call_info)
        log.write(output)
    print("Build output is in log file: %r" % log_filename)

    git_tag="v%s" % __version__

    print("\ncheck git tag")
    call_info, output = verbose_check_output("git", "log", "HEAD..origin/master", "--oneline")
    if git_tag in output:
        print("\n *** ERROR: git tag %r already exists!" % git_tag)
        print(output)
        sys.exit(-1)
    else:
        print("OK")

    print("\nUpload with twine:")
    twine_args = sys.argv[1:]
    twine_args.remove("publish")
    twine_args.insert(1, "dist/*")
    print("\ttwine upload command args: %r" % " ".join(twine_args))
    from twine.commands.upload import main as twine_upload
    twine_upload(twine_args)

    print("\ngit tag version")
    verbose_check_call("git", "tag", git_tag)

    print("\ngit push tag to server")
    verbose_check_call("git", "push", "--tags")

    sys.exit(0)


if "test" in sys.argv or "nosetests" in sys.argv:
    """
    nose is a optional dependency, so test import.
    Otherwise the user get only the error:
        error: invalid command 'nosetests'
    """
    try:
        import nose
    except ImportError as err:
        print("\nError: Can't import 'nose': %s" % err)
        print("\nMaybe 'nose' is not installed or virtualenv not activated?!?")
        print("e.g.:")
        print("    ~/your/env/$ source bin/activate")
        print("    ~/your/env/$ pip install nose")
        print("    ~/your/env/$ ./setup.py nosetests\n")
        sys.exit(-1)
    else:
        if "test" in sys.argv:
            print("\nPlease use 'nosetests' instead of 'test' to cover all tests!\n")
            print("e.g.:")
            print("     $ ./setup.py nosetests\n")
            sys.exit(-1)


setup(
    name=DISTRIBUTION_NAME,
    # PyPi package is: "DragonPyEmulator" and not "DragonPy"
    # because of name conflict with https://github.com/jpanganiban/dragonpy :(
    # see:https://github.com/jpanganiban/dragonpy/issues/3

    version=__version__,
    py_modules=["DragonPy"],
    provides=["DragonPy"],
    install_requires=[
        "dragonlib>=0.1.7",
        "MC6809>=0.5.0",
        "pygments",
        "click",
        "six",
    ],
    tests_require=[
        "nose", # https://pypi.python.org/pypi/nose
    ],
    # https://pythonhosted.org/setuptools/setuptools.html#automatic-script-creation
    entry_points={
        # Here we use constants, because of usage in "starter GUI", too.
        # DIST_GROUP = "console_scripts"
        # ENTRY_POINT = "DragonPy"
        DIST_GROUP: ["%s = dragonpy.core.cli:main" % ENTRY_POINT],
        # e.g.:
        #   "console_scripts": ["DragonPy = dragonpy.core.cli:main"],
    },
    author="Jens Diemer",
    author_email="DragonPy@jensdiemer.de",
    description="Emulator for 6809 CPU based system like Dragon 32 / CoCo written in Python...",
    keywords="Emulator 6809 Dragon CoCo Vectrex tkinter pypy",
    long_description=long_description,
    url="https://github.com/jedie/DragonPy",
    license="GPL v3+",
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: System :: Emulators",
        "Topic :: Software Development :: Assemblers",
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
