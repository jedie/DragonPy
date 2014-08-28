#!/bin/bash

# https://github.com/jedie/PyDragon32/tree/master/misc#readme

(
    set -x
    #~ python2 DragonPy_CLI.py --machine=Dragon64 run | python ../PyDragon32/misc/filter_xroar_trace.py --display --start-stop=B3D9-ffff | tee Dragon64_test_trace.txt
    #~ python2 DragonPy_CLI.py --machine=Dragon64 run | python ../PyDragon32/misc/filter_xroar_trace.py  --unique | tee Dragon64_test_trace.txt
    #~ python2 DragonPy_CLI.py --machine=Dragon64 run > Dragon64_test_trace.txt
    #~ python2 DragonPy_CLI.py --machine=Dragon64 run | tee Dragon64_test_trace.txt
    python2 DragonPy_CLI.py --machine=Dragon64 run
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