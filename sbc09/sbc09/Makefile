
CC=gcc
CFLAGS= -O1
V09FLAGS= -DUSE_TERMIOS #-DBIG_ENDIAN

all: a09 v09 v09.rom examples 

a09: a09.c
	$(CC) -o a09 $(CFLAGS) a09.c

v09: v09.o engine.o io.o
	$(CC) -o v09 $(CFLAGS) v09.o engine.o io.o

v09.o: v09.c v09.h
	$(CC) -c $(CFLAGS) $(V09FLAGS) v09.c

engine.o: engine.c v09.h
	$(CC) -c $(CFLAGS) $(V09FLAGS) engine.c

io.o: io.c v09.h
	$(CC) -c $(CFLAGS) $(V09FLAGS) io.c

v09.rom: makerom monitor.s 
	./makerom <monitor.s

monitor.s: monitor.asm
	./a09 -s monitor.s -l monitor.lst monitor.asm

makerom: makerom.c
	$(CC) -o makerom makerom.c

examples: test09 bench09 basic bin2dec asmtest 

test09: test09.asm
	./a09 -l test09.lst test09.asm

bench09: bench09.asm
	./a09 -l bench09.lst bench09.asm

basic: basic.asm
	./a09 -l basic.lst basic.asm

bin2dec: bin2dec.asm
	./a09 -l bin2dec.lst bin2dec.asm

asmtest: asmtest.asm
	./a09 -l asmtest.lst asmtest.asm

