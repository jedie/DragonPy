@echo off

title "%~0"

set python=C:\Python27\python.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

echo on
%python% -OO DragonPy_CLI.py --machine=CoCo2b run
@pause