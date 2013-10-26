* Load Forth into RAM.
	org $8000
	ldy #$8020
	ldu #$0400
	ldx #$3741
movloop	lda ,y+
	sta ,u+
	leax -1,x
	bne movloop
	jmp $400
	