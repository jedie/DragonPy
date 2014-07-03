#!/bin/bash

# needs https://pypi.python.org/pypi/coverage
# e.g.:
#   $ sudo apt install python-coverage
# or:
#   $ sudo apt install python-pip
#   $ sudo pip2 install coverage
# etc.

coverage2=/usr/bin/python2-coverage
#coverage2=coverage2

set -x

# delete old results
${coverage2} erase

# run unittests
${coverage2} run --source=dragonpy setup.py test
#~ ${coverage2} run setup.py test -s dragonpy.tests.test_BASIC_simple09


# create coverage html resport files
${coverage2} html

python -m webbrowser -t "htmlcov/index.html"