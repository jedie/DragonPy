@echo off

title "%~0"

REM ~ set python=C:\pypy-2.3.1-win32\pypy.exe
set python=C:\pypy-2.4.0-win32\pypy.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

cd..

:loop
    echo on
    %python% -OO DragonPy_CLI.py benchmark --loops 100
    @echo off
    pause
goto:loop