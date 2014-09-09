#!/bin/bash

# https://github.com/jedie/PyDragon32/tree/master/misc#readme
#

#PYPY=~/pypy-2.3.1-linux_i686-portable/bin/pypy
PYPY=~/pypy2/bin/pypy

if [ ! -x ${PYPY} ]; then
    (
        echo
        echo ERROR: PyPy executable not found here:
        echo
        echo ${PYPY}
        echo
        echo You can download PyPy here:
        echo
        echo http://pypy.org/download.html
        echo or
        echo https://github.com/squeaky-pl/portable-pypy
        echo
    )
else
(
    set -x
    ${PYPY} -OO DragonPy_CLI.py --verbosity 99 --machine=Dragon64 run
)
fi

echo
read -n1 -p "Start bash? [y,n]" doit
echo
case $doit in
    y|Y)
        bash -i
        exit 0
        ;;
    n|N)
        echo "bye bye"
        ;;
    *)
        echo "input, don't know, bye."
        ;;
esac
