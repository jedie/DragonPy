@echo off

title "%~0"

set python=C:\Python27\python.exe
REM ~ set python=D:\pypy-2.3.1-win32\pypy.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

:loop
    cls
    echo on
    %python% DragonPy_CLI.py --machine=Dragon32
    @echo off
    pause
goto:loop