@echo off

title "%~0"

set python=C:\Python27\python.exe
set coverage2=C:\Python27\Scripts\coverage.exe

if NOT exist %python% (
    echo Error: '%python%' doesn't exists?!?
    pause
    exit 1
)

if NOT exist %coverage2% (
    echo Error: '%coverage2%' doesn't exists!
    echo Please install: https://pypi.python.org/pypi/coverage
    echo e.g.:
    echo C:\Python27>python.exe get-pip.py
    echo C:\Python27\Scripts>pip.exe install coverage
    pause
    exit 1
)

echo on

REM delete old results
%coverage2% erase

REM run unittests
%coverage2% run --source=dragonpy setup.py test
REM ~ %coverage2% run setup.py test -s dragonpy.tests.test_BASIC_simple09


REM create coverage html resport files
%coverage2% html

%python% -m webbrowser -t "htmlcov/index.html"

@pause