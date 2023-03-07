## Dragon/CoCO emulator written in Python

DragonPy is a Open source (GPL v3 or later) emulator for the old (1981) homecomputer `Dragon 32` and `Tandy TRS-80 Color Computer` (CoCo)...

The [MC6809](https://github.com/6809/MC6809) project is used to emulate the 6809 CPU.

[![tests](https://github.com/jedie/DragonPy/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/jedie/DragonPy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/github/jedie/dragonpy/branch/main/graph/badge.svg)](https://app.codecov.io/github/jedie/dragonpy)
[![dragonpy @ PyPi](https://img.shields.io/pypi/v/DragonPyEmulator?label=dragonpy%20%40%20PyPi)](https://pypi.org/project/DragonPyEmulator/)
[![Python Versions](https://img.shields.io/pypi/pyversions/DragonPyEmulator)](https://github.com/jedie/DragonPy/blob/main/pyproject.toml)
[![License GPL-3.0-or-later](https://img.shields.io/pypi/l/DragonPyEmulator)](https://github.com/jedie/DragonPy/blob/main/LICENSE)


Dragon 32 with CPython 3 under Linux:

![screenshot Dragon 32](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20150820_DragonPy_Dragon32_CPython3_Linux_01.png "screenshot Dragon 32")

Tandy TRS-80 Color Computer 2b with CPython 2 under Windows:

![screenshot CoCo under Windows](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20150820_DragonPy_CoCo2b_CPython2_Win_01.png "screenshot CoCo under Windows")

(Note: Python 2 support was removed)

DragonPy is written in Python.
It's platform independent and runs with Python and PyPy under Linux/Windows/OSX/...
It's tested with Python 3.x, PyPy

DragonPy will not be a second XRoar written in Python.
This project is primarily to lean and understand.

Future goals are:


* Implement a integrated development environment for BASIC programs

A full featured Dragon / CoCo emulator is [XRoar](http://www.6809.org.uk/dragon/xroar.shtml).

### Current state

The Dragon 32 / 64 and CoCo ROMs works in Text mode.
Also the "single board computer" ROMs sbc09, Simple6809 and Multicomp6809 works well.

There is a rudimentary BASIC editor with save/load BASIC programm listings direct into RAM.

Looks like this:

![old screenshot BASIC Editor](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140820_DragonPy_BASIC_Editor_01.png "old screenshot BASIC Editor")
(older version of the editor)

#### Vectrex

The [Vectrex (Wikipedia)](https://en.wikipedia.org/wiki/Vectrex) is a vector display-based video game console.
The Hardware are _only_ the 6809 CPU, a 6522 Versatile Interface Adapter and the AY-3-8912 sound chip.

Current state is completely not usable. The 6522 is only a dummy implementation.
It makes only sense to display some trace lines, e.g.:
```
.../DragonPy$ poetry run DragonPy --verbosity 0 --machine=Vectrex run --trace --max_ops=1
```

### BASIC Editor

Use "BASIC editor / open" in the main menu to open the editor.

You can load/save ASCII .bas files from you local drive or just type a BASIC listing ;)
With "inject into DragonPy" you send the current listing from the Editor to the Emulator and with "load from DragonPy" back from emulator to editor.
Note: The is currently no "warning" that un-saved content will be "overwritten" and there is no "auto-backup" ;)

The "renumbering" tool can be found in the editor window under "tools"

You can also run the BASIC Editor without the Emulator:
```
.../DragonPy$ make editor
# or:
.../DragonPy$ poetry run DragonPy editor
```

A rudimentary BASIC source code highlighting is available and looks like this:

![screenshot BASIC Editor](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140826_DragonPy_BASIC_Editor_01.png "screenshot BASIC Editor")

Special feature: The Line number that are used in GOTO, SOGUB etc. are extra marked on the left side.

## installation

IMPORTANT: The **PyPi package** name is **DragonPyEmulator** and [not only "DragonPy"](https://github.com/jpanganiban/dragonpy/issues/3)!!!
```
pip install DragonPyEmulator
```

### from source

```bash
~$ git clone https://github.com/jedie/DragonPy.git
~$ cd DragonPy/
~/DragonPy$ ./cli.py --help
```

The output of `./cli.py --help` looks like:

[comment]: <> (✂✂✂ auto generated main help start ✂✂✂)
```
Usage: ./cli.py [OPTIONS] COMMAND [ARGS]...

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --help      Show this message and exit.                                                          │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────────────────────────╮
│ check-code-style            Check code style by calling darker + flake8                          │
│ coverage                    Run and show coverage.                                               │
│ download-roms               Download/Test only ROM files                                         │
│ editor                      Run only the BASIC editor                                            │
│ fix-code-style              Fix code style of all dragonpy source code files via darker          │
│ gui                         Start the DragonPy tkinter starter GUI                               │
│ install                     Run pip-sync and install 'dragonpy' via pip as editable.             │
│ log-list                    List all exiting loggers and exit.                                   │
│ mypy                        Run Mypy (configured in pyproject.toml)                              │
│ publish                     Build and upload this project to PyPi                                │
│ run                         Run a machine emulation                                              │
│ safety                      Run safety check against current requirements files                  │
│ test                        Run unittests                                                        │
│ tox                         Run tox                                                              │
│ update                      Update "requirements*.txt" dependencies files                        │
│ update-test-snapshot-files  Update all test snapshot files (by remove and recreate all snapshot  │
│                             files)                                                               │
│ version                     Print version and exit                                               │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated main help end ✂✂✂)


The output of `./cli.py run --help` looks like:

[comment]: <> (✂✂✂ auto generated run help start ✂✂✂)
```
Usage: ./cli.py run [OPTIONS]

 Run a machine emulation

╭─ Options ────────────────────────────────────────────────────────────────────────────────────────╮
│ --verbosity           [1|10|20|30|40|50|99|100]            1:hardcode DEBUG ;), 10:DEBUG,        │
│                                                            20:INFO, 30:WARNING, 40:ERROR,        │
│                                                            50:CRITICAL/FATAL, 99:nearly all off, │
│                                                            100:all off                           │
│                                                            [default: 100]                        │
│ --trace/--no-trace                                         Create trace lines                    │
│                                                            [default: no-trace]                   │
│ --max-ops             INTEGER                              If given: Stop CPU after given cycles │
│                                                            else: run forever                     │
│ --machine             [CoCo2b|Dragon32|Dragon64|Multicomp  Used machine configuration            │
│                       6809|Simple6809|Vectrex|sbc09]       [default: Dragon32]                   │
│ --help                                                     Show this message and exit.           │
╰──────────────────────────────────────────────────────────────────────────────────────────────────╯
```
[comment]: <> (✂✂✂ auto generated run help end ✂✂✂)

Usage e.g.:
```bash
~/DragonPy$ ./cli.py run
~/DragonPy$ ./cli.py editor
```

## ROMs

All needed ROM files, will be **downloaded automatically**.

The files will be downloaded from:

| Machine        | download url |
|----------------|--------------|
| Dragon 32 + 64 | [http://archive.worldofdragon.org/archive/index.php?dir=Software/Dragon/Dragon%20Data%20Ltd/Dragon%20Firmware/](http://archive.worldofdragon.org/archive/index.php?dir=Software/Dragon/Dragon%20Data%20Ltd/Dragon%20Firmware/) |
| CoCo 2b        | [http://www.roust-it.dk/coco/roms/](http://www.roust-it.dk/coco/roms/)                                                                                                                                                         |
| Multicomp      | [http://searle.x10host.com/Multicomp/index.html](http://searle.x10host.com/Multicomp/index.html)                                                                                                                               |
| Simple6809     | [http://searle.x10host.com/6809/Simple6809.html](http://searle.x10host.com/6809/Simple6809.html)                                                                                                                               |

`sbc09` and `Vectrex` ROMs are included.

All ROM files and download will be checked by `SHA1` value, before use.


## run tests

e.g.:

```bash
~/DragonPy$ ./devshell.py pytest
```
or
```bash
~/DragonPy$ ./devshell.py tox
```

## more screenshots

"sbc09" ROM in Tkinter window:

![screenshot sbc09](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/DragonPy_sbc09_01.png "screenshot sbc09")

"Simple6809" ROM in Tkinter window:

![screenshot simple6809](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/Simple6809_TK_04.PNG "screenshot simple6809")

### Dragon Keyboard

The keyboard mapping is stored into [dragonpy/Dragon32/keyboard_map.py](https://github.com/jedie/DragonPy/blob/main/dragonpy/Dragon32/keyboard_map.py).

Some notes:

* "CLEAR" is mapped to "Home" / "Pos 1" key
* "BREAK" is mapped to "Escape" button
* "LEFT" is mapped to left cursor key and to normal backspace, too.

A "auto shift" mode is implemented. So normal lowercase letters would be automaticly converted to uppercase letters.

#### paste clipboard

It is possible to paste the content of the clipboard as user input in the machine.
Just copy (Ctrl-C) the follow content:
```
10 CLS
20 FOR I = 0 TO 255:
30 POKE 1024+(I*2),I
40 NEXT I
50 I$ = INKEY$:IF I$="" THEN 50
```

Focus the DragonPy window and use Ctrl-V to paste the content.

Looks like:

![raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_Listing.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_Listing.png "https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_Listing.png")

Then just **RUN** and then it looks like this:

![raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_CharMap.png](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_CharMap.png "https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/20140805_DragonPy_Dragon32_CharMap.png")

### DragonPy schematic
```
        Main Thread                                     Sub Thread
       (Tkinter GUI)
    +------------------+                         +---------------------+
    |                  |                         |                     |
    | +-------------+  |  CPU cycles/sec queue   |                     |
    | |            <------------------------------------+6809 CPU      |
    | |             |  |                         |       +     ^       |
    | |     GUI     |  |                         |       |     |       |
    | |             |  | Display RAM write queue |    +--v-----+--+    |
    | |  .--------------------------------------------+   Memory  |    |
    | |  |          |  |                         |    +--+-----^--+    |
    | |  |          |  |                         |       |     |       |
    | |  |          |  |                         | +-----v-----+-----+ |
    | |  |          |  |                         | |    Periphery    | |
    | |  |          |  |     Keyboard queue      | |   MC6883 SAM    | |
    | |  |          +--------------------------------->MC6821 PIA    | |
    | |  |          |  |                         | |                 | |
    | +--+-----^----+  |                         | |                 | |
    |    |     |       |                         | +-----------------+ |
    |    |     |       |                         |                     |
    | +--v-----+----+  |                         |                     |
    | |             |  |                         |                     |
    | |   Display   |  |                         |                     |
    | |             |  |                         |                     |
    | +-------------+  |                         |                     |
    +------------------+                         +---------------------+

```

### performance

The current implementation is not really optimized.

With CPython there is round about 490.000 CPU cycles/sec. in console version.
This is half as fast as the real Hardware.

With PyPy round about 6.900.000 - 8.000.000 CPU cycles/sec.
In other words with PyPy it's 8 times faster as the real Hardware.

e.g. The Dragon 32 6809 machine with a 14.31818 MHz crystal runs with:
0,895MHz (14,31818Mhz/16=0,895MHz) in other words: 895.000 CPU-cycles/sec.

## TODO:


* implement more Dragon 32 periphery
* missing 6809 unittests after coverage run:
  * `MUL`
  * `BVS`

## PyDragon32

Some `Python`/`BASIC tools`/`scripts` around `Dragon32/64` / `CoCo` homecomputer.

All script are copyleft 2013-2020 by Jens Diemer and license unter GNU GPL v3 or above, see LICENSE for more details.

### Python scripts:


* PyDC - Convert dragon 32 Cassetts WAV files into plain text:
  * [github.com/jedie/DragonPy/tree/master/PyDC](https://github.com/jedie/DragonPy/tree/master/PyDC)
* Filter Xroar traces:
  * [github.com/jedie/DragonPy/tree/master/misc](https://github.com/jedie/DragonPy/tree/master/misc)

### BASIC programms:


* Simple memory HEX viewer:
  * [github.com/jedie/DragonPy/tree/master/BASIC/HexViewer](https://github.com/jedie/DragonPy/tree/master/BASIC/HexViewer)


* Test CC Registers:
  * [github.com/jedie/DragonPy/tree/master/BASIC/TestCC_Registers](https://github.com/jedie/DragonPy/tree/master/BASIC/TestCC_Registers)

#### Input/Output Tests

[/BASIC/InputOutput/keyboard.bas](https://github.com/jedie/DragonPy/tree/master/BASIC/InputOutput/keyboard.bas)
Display memory Locations $0152 - $0159 (Keyboard matrix state table)

Example screenshow with the "Y" key is pressed down. You see that this is saved in $0153:

![KeyBoard Screenshot 01](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/keyboard01.png "KeyBoard Screenshot 01")

Example with "U" is hold down:

![KeyBoard Screenshot 02](https://raw.githubusercontent.com/jedie/jedie.github.io/master/screenshots/DragonPy/keyboard02.png "KeyBoard Screenshot 02")

## Links


* Grant Searle's Multicomp FPGA project:
  * Homepage: [http://searle.x10host.com/Multicomp/](http://searle.x10host.com/Multicomp/)
  * own [dragonpy/Multicomp6809/README](https://github.com/jedie/DragonPy/tree/master/dragonpy/Multicomp6809#readme)
* Lennart Benschop 6809 Single Board Computer:
  * Homepage: [http://lennartb.home.xs4all.nl/m6809.html](http://lennartb.home.xs4all.nl/m6809.html)
  * own [dragonpy/sbc09/README](https://github.com/jedie/DragonPy/tree/master/dragonpy/sbc09#readme)
* Grant Searle's Simple 6809 design:
  * Homepage: [http://searle.x10host.com/6809/Simple6809.html](http://searle.x10host.com/6809/Simple6809.html)
  * own [dragonpy/Simple6809/README](https://github.com/jedie/DragonPy/tree/master/dragonpy/Simple6809#readme)

Some links:


* [http://www.burgins.com/m6809.html](http://www.burgins.com/m6809.html)
* [http://www.maddes.net/m6809pm/](http://www.maddes.net/m6809pm/) - Programming Manual for the 6809 microprocessor from Motorola Inc. (now Freescale)
* [http://www.6809.org.uk/dragon/hardware.shtml](http://www.6809.org.uk/dragon/hardware.shtml)
* [http://dragondata.worldofdragon.org/Publications/inside-dragon.htm](http://dragondata.worldofdragon.org/Publications/inside-dragon.htm)
* [http://koti.mbnet.fi/~atjs/mc6809/](http://koti.mbnet.fi/~atjs/mc6809/) - 6809 Emulation Page

Source codes:


* [github.com/naughton/mc6809/blob/master/mc6809.ts](https://github.com/naughton/mc6809/blob/master/mc6809.ts)
* [github.com/maly/6809js/blob/master/6809.js](https://github.com/maly/6809js/blob/master/6809.js)
* [http://mamedev.org/source/src/mess/drivers/dragon.c.html](http://mamedev.org/source/src/mess/drivers/dragon.c.html)
* [http://mamedev.org/source/src/mess/machine/dragon.c.html](http://mamedev.org/source/src/mess/machine/dragon.c.html)
* [http://mamedev.org/source/src/emu/cpu/m6809/m6809.c.html](http://mamedev.org/source/src/emu/cpu/m6809/m6809.c.html)
* [github.com/kjetilhoem/hatchling-32/blob/master/hatchling-32/src/no/k/m6809/InstructionSet.scala](https://github.com/kjetilhoem/hatchling-32/blob/master/hatchling-32/src/no/k/m6809/InstructionSet.scala)

Dragon 32 resources:


* Forum: [http://archive.worldofdragon.org/phpBB3/index.php](http://archive.worldofdragon.org/phpBB3/index.php)
* Wiki: [http://archive.worldofdragon.org/index.php?title=Main_Page](http://archive.worldofdragon.org/index.php?title=Main_Page)

## Credits

Some code based on:

### ApplePy

An `Apple ][` emulator in Python

* Author: James Tauber
* [github.com/jtauber/applepy](https://github.com/jtauber/applepy)
* License: MIT

### XRoar

A really cool Dragon / CoCo emulator

* Author: Ciaran Anscomb
* [http://www.6809.org.uk/xroar/](http://www.6809.org.uk/xroar/)
* License: GNU GPL v2

### included Python modules:

#### python-pager

Page output and find dimensions of console.

* Author: Anatoly Techtonik
* License: Public Domain
* Homepage: [bitbucket.org/techtonik/python-pager/](https://bitbucket.org/techtonik/python-pager/)
* Stored here: [/dragonpy/utils/pager.py](https://github.com/jedie/DragonPy/blob/main/dragonpy/utils/pager.py)

#### srecutils.py

Motorola S-Record utilities

* Author: Gabriel Tremblay
* License: GNU GPL v2
* Homepage: [github.com/gabtremblay/pysrec](https://github.com/gabtremblay/pysrec)
* Stored here: [/dragonpy/utils/srecord_utils.py](https://github.com/jedie/DragonPy/blob/main/dragonpy/utils/srecord_utils.py)

### requirements

#### dragonlib

Dragon/CoCO Python Library

* Author: Jens Diemer
* [pypi.org/project/DragonLib/](https://pypi.org/project/DragonLib/)
* [github.com/6809/dragonlib](https://github.com/6809/dragonlib)
* License: GNU GPL v3

#### MC6809

Implementation of the MC6809 CPU in Python

* Author: Jens Diemer
* [pypi.org/project/MC6809](https://pypi.org/project/MC6809)
* [github.com/6809/MC6809](https://github.com/6809/MC6809)
* License: GNU GPL v3

#### pygments

generic syntax highlighter

* Author: Georg Brandl
* [pypi.org/project/Pygments](https://pypi.org/project/Pygments)
* [http://pygments.org/](http://pygments.org/)
* License: BSD License

## History


* [*dev*](https://github.com/jedie/DragonPy/compare/v0.7.0...master):
  * Replace Creole README with markdown.
  * tbc
* [01.10.2020 - v0.7.0](https://github.com/jedie/DragonPy/compare/v0.6.0...v0.7.0):
  * Modernize project testing, CI pipeline, usw poetry etc.
  * Many Code updates
  * Remove Python v2 fallback code parts
  * Update ROM Download Links
  * Bugfix "--max_ops" cli options
* [19.06.2018 - v0.6.0](https://github.com/jedie/DragonPy/compare/v0.5.3...v0.6.0):
  * Update to new MC6809 API
  * reimplementing Simple6809, contributed by [Claudemir Todo Bom](https://github.com/ctodobom)
  * TODO: Fix speedlimit
  * Fix `No module named 'nose'` on normal PyPi installation
* [24.08.2015 - v0.5.3](https://github.com/jedie/DragonPy/compare/v0.5.2...v0.5.3):
  * Bugfix for "freeze" after "speed limit" was activated
* [20.08.2015 - v0.5.2](https://github.com/jedie/DragonPy/compare/v0.5.1...v0.5.2):
  * Add run 'MC6809 benchmark' button to 'starter GUI'
  * bugfix 'file not found' in 'starter GUI'
  * change the GUI a little bit
* [19.08.2015 - v0.5.1](https://github.com/jedie/DragonPy/compare/v0.5.0...v0.5.1):
  * Add a "starter GUI"
  * Add work-a-round for tkinter usage with virtualenv under windows, see: [virtualenv issues #93](https://github.com/pypa/virtualenv/issues/93)
  * bugfix e.g.: keyboard input in "sbc09" emulation
  * use nose to run unittests
* [18.08.2015 - v0.5.0](https://github.com/jedie/DragonPy/compare/v0.4.0...v0.5.0):
  * ROM files will be downloaded on-the-fly (`.sh` scripts are removed. So it's easier to use under Windows)
* [26.05.2015 - v0.4.0](https://github.com/jedie/DragonPy/compare/v0.3.2...v0.4.0):
  * The MC6809 code is out sourced to: [github.com/6809/MC6809](https://github.com/6809/MC6809)
* [15.12.2014 - v0.3.2](https://github.com/jedie/DragonPy/compare/v0.3.1...v0.3.2):
  * Use [Pygments](http://pygments.org/) syntax highlighter in BASIC editor
* [08.10.2014 - v0.3.1](https://github.com/jedie/DragonPy/compare/v0.3.0...v0.3.1):
  * Release as v0.3.1
  * 30.09.2014 - Enhance the BASIC editor
  * 29.09.2014 - Merge [PyDragon32](https://github.com/jedie/PyDragon32) project
* [25.09.2014 - v0.3.0](https://github.com/jedie/DragonPy/compare/v0.2.0...v0.3.0):
  * [Change Display Queue to a simple Callback](https://github.com/jedie/DragonPy/commit/f396551df730b509498d1b884cdda8f7075737c4)
  * Reimplement [Multicomp 6809](https://github.com/jedie/DragonPy/commit/f3bfbdb2ae9906d8e051436173225c3fa8de1373) and [SBC09](https://github.com/jedie/DragonPy/commit/61c26911379d2b7ea6d07a8b479ab14c5d5a7154)
  * Many code refactoring and cleanup
* [14.09.2014 - v0.2.0](https://github.com/jedie/DragonPy/compare/v0.1.0...v0.2.0):
  * Add a speedlimit, config dialog and IRQ: [Forum post 11780](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&p=11780#p11780)
* [05.09.2014 - v0.1.0](https://github.com/jedie/DragonPy/compare/8fe24e5...v0.1.0):
  * Implement pause/resume, hard-/soft-reset 6809 in GUI and improve a little the GUI/Editor stuff
  * see also: [Forum post 11719](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&p=11719#p11719).
* 27.08.2014 - Run CoCo with Extended Color Basic v1.1, bugfix transfer BASIC Listing with [8fe24e5...697d39e](https://github.com/jedie/DragonPy/compare/8fe24e5...697d39e) see: [Forum post 11696](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=90#p11696).
* 20.08.2014 - rudimenary BASIC IDE works with [7e0f16630...ce12148](https://github.com/jedie/DragonPy/compare/7e0f16630...ce12148), see also: [Forum post 11645](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=8&t=4439#p11645).
* 05.08.2014 - Start to support CoCo, too with [0df724b](https://github.com/jedie/DragonPy/commit/0df724b3ee9d87088b524c3623040a41e9772eb4), see also: [Forum post 11573](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=80#p11573).
* 04.08.2014 - Use the origin Pixel-Font with Tkinter GUI, see: [Forum post 4909](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4909) and [Forum post 11570](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=80#p11570).
* 27.07.2014 - Copyrigth info from Dragon 64 ROM is alive with [543275b](https://github.com/jedie/DragonPy/commit/543275b1b90824b64b67dcd003cc5ab54296fc15), see: [Forum post 11524](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=80#p11524).
* 29.06.2014 - First "HELLO WORLD" works, see: [Forum post 11283](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=70#p11283).
* 27.10.2013 - "sbc09" ROM works wuite well almist, see: [Forum post 9752](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=60#p9752).
* 16.10.2013 - See copyright info from "Simple6809" ROM with [25a97b6](https://github.com/jedie/DragonPy/tree/25a97b66d8567ba7c3a5b646e4a807b816a0e376) see also: [Forum post 9654](http://archive.worldofdragon.org/phpBB3/viewtopic.php?f=5&t=4308&start=50#p9654).
* 10.09.2013 - Start to implement the 6809 CPU with [591d2ed](https://github.com/jedie/DragonPy/commit/591d2ed2b6f1a5f913c14e56e1e37f5870510b0d)
* 28.08.2013 - Fork "Apple ][ Emulator" written in Python: [github.com/jtauber/applepy](https://github.com/jtauber/applepy) to [github.com/jedie/DragonPy](https://github.com/jedie/DragonPy)

## Links:

| Forum  | [http://forum.pylucid.org/](http://forum.pylucid.org/)                                   |
| IRC    | [#pylucid on freenode.net](http://www.pylucid.org/permalink/304/irc-channel)             |
| Jabber | pylucid@conference.jabber.org                                                            |
| PyPi   | [pypi.org/project/DragonPyEmulator/](https://pypi.org/project/DragonPyEmulator/) |
| Github | [github.com/jedie/DragonPy](https://github.com/jedie/DragonPy)                   |

## donation


* Send [Bitcoins](http://www.bitcoin.org/) to [1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F](https://blockexplorer.com/address/1823RZ5Md1Q2X5aSXRC5LRPcYdveCiVX6F)
