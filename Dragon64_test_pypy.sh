#!/bin/bash

# https://github.com/jedie/PyDragon32/tree/master/misc#readme
# https://github.com/squeaky-pl/portable-pypy

(
    set -x
    #~ python2 Dragon64_test.py | python ../PyDragon32/misc/filter_xroar_trace.py --display --start-stop=B3D9-ffff | tee Dragon64_test_trace.txt
    #~ python2 Dragon64_test.py | python ../PyDragon32/misc/filter_xroar_trace.py  --unique | tee Dragon64_test_trace.txt
    #~ python2 Dragon64_test.py > Dragon64_test_trace.txt
    #~ python2 Dragon64_test.py | tee Dragon64_test_trace.txt
    ~/pypy-2.3.1-linux_x86_64-portable/bin/pypy Dragon64_test.py
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