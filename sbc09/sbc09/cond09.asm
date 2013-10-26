* Conditional assembly.

jantje	equ 2

	org $100
	if jantje=1
main	ldx #12
	else
man2	ldx #13
	endif
labx	ldy #25

	include cond09.inc

	ldb #23
        ldu labx,pcr
        ldy laby,pcr
        sex
	mul
laby    sync  
	end