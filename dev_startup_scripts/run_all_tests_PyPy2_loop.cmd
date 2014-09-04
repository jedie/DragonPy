@echo off

title "%~0"

set python=C:\pypy-2.3.1-win32\pypy.exe
if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

cd ..

:loop
    echo on
    cls
    REM ~ %python% setup.py test
    %python% -m unittest discover
    @echo off
    pause
goto:loop