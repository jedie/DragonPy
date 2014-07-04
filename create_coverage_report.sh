#!/bin/bash

coverage2=$(which coverage2) # e.g.: installed via pip
if [ $? != 0 ]; then
    coverage2=/usr/bin/python2-coverage
fi

if [ ! -x ${coverage2} ]; then
    echo "Error: coverage2 not found!"
    echo "Please install: https://pypi.python.org/pypi/coverage"
    echo "e.g.:"
    echo "  $ sudo apt install python-coverage"
    echo "or:"
    echo "  $ sudo apt install python-pip"
    echo "  $ sudo pip2 install coverage"
    echo "etc."
    read -p ENTER ENTER
    exit 1
fi

set -x

# delete old results
${coverage2} erase

# run unittests
${coverage2} run --source=dragonpy setup.py test
#~ ${coverage2} run setup.py test -s dragonpy.tests.test_BASIC_simple09


# create coverage html resport files
${coverage2} html

python -m webbrowser -t "htmlcov/index.html"