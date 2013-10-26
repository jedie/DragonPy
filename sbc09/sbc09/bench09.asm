	;6809 Benchmark program.

	org $400

	lds #$8000	

	ldb #'a'
	jsr outc	
	ldd $2b
	std $80	;Save old timer value.
	
	ldy #0
loop	ldx #data
	lda #(enddata-data)
	clrb	
loop2:	addb ,x+
	deca
	bne loop2
	cmpb #210
	lbne error		
        leay -1,y
	bne loop

        ldb #'b'
	jsr outc
	ldd $2b
	subd $80 ;Hold timer difference in D.
	jmp realexit 

error	ldb #'e'
	jsr outc
	jmp realexit

outc	jsr 3
	rts

realexit swi

data 	fcb 1,2,3,4,5,6,7,8,9,10
	fcb 11,12,13,14,15,16,17,18,19,20
enddata
  
	end