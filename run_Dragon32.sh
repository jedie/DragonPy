#!/bin/bash

# https://github.com/jedie/DragonPy

source ../../bin/activate

(
    set -x
    python -OO DragonPy_CLI.py --verbosity 99 --machine=Dragon32 run
)
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