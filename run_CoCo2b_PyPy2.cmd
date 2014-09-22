@echo off

title "%~0"

set pypy=C:\pypy-2.3.1-win32\pypy.exe
if NOT exist %pypy% (
    echo Error: '%pypy%' doesn't exists?!?
    pause
    exit 1
)

echo on
%pypy% -OO DragonPy_CLI.py --machine=CoCo2b run
@pause