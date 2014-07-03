* Convert 32-bits binary number to decimal.
	org $400
	
main	lds #$8000
	ldx #num1
	jsr prtdec
	ldx #num2
	jsr prtdec
	ldx #num3
	jsr prtdec
	ldx #num4
	jsr prtdec
	ldx #num5
	jsr prtdec
	ldx #num6
	jsr prtdec
	swi


* Print double number (including leading zeros)  pointed to by X. 
* Number at that location is destroyed by the process.
prtdec	jsr bin2bcd	;Convert to bcd
        ldx #bcdbuf	;Traverse 5-byte buffer.
	ldb #5
	stb temp
pdloop	lda ,x+	        
        tfr a,b		
	lsrb
	lsrb
	lsrb
	lsrb		;Extract higher digit from bcd byte.
 	addb #'0
	jsr outch
	tfr a,b
	andb #15	;Extract lower digit.
	addb #'0
	jsr outch
	dec temp
	bne pdloop
	ldb #13		;output newline.
	jsr outch
	ldb #10
	jsr outch
	rts

* Convert 4-byte number pointed to by X to 5-byte (10 digit) bcd.
bin2bcd ldu #bcdbuf
	ldb #5
bbclr	clr ,u+		;Clear the 5-byte bcd buffer.
	decb
	bne bbclr
        ldb #4		;traverse 4 bytes of bin number 
	stb temp
bbloop	ldb #8		;and 8 bits of each byte. (msb to lsb)
	stb temp2
bbl1	rol ,x		;Extract next bit from binary number.
	ldb #5
        ldu #bcdbuf+5
bbl2	lda ,-u		;multiply bcd number by 2 and add extracted bit
	adca ,u		;into it. 
	daa
	sta ,u
	decb
	bne bbl2
	dec temp2
	bne bbl1
	leax 1,x
	dec temp
	bne bbloop
	rts

* Output character B 
outch	jsr 3
	rts

bcdbuf	rmb 5
temp	rmb 1
temp2 	rmb 1

num1	fdb -1,-1       ; should be 4294967295
num2	fdb 0,0         ; should be 0000000000
num3	fdb 32768,0     ; should be 2147483648
num4	fdb $3b9A,$c9ff ; should be 0999999999
num5    fdb $3b9a,$ca00 ; should be 1000000000
num6	fdb 0,5501	; should be 0000005501