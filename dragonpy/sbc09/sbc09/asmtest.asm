	org $400
addr8	equ $80h
addr16	equ $1234

	neg addr8
	com addr8
	lsr addr8
	ror addr8
	asr addr8
	asl addr8
	lsl addr8
	rol addr8
	dec addr8
	inc addr8
	tst addr8
	jmp addr8
	clr addr8

	lbrn addr16
	lbhi addr16
	lbls addr16
	lbhs addr16
	lbcc addr16
	lblo addr16
	lbcs addr16
	lbne addr16
	lbeq addr16
	lbvc addr16
	lbvs addr16
	lbpl addr16
	lbmi addr16
	lbge addr16
	lblt addr16
	lbgt addr16
	lble addr16

	swi2
	cmpd #$4444
	cmpy #$4444
	ldy  #$4444
	cmpd addr8
	cmpy addr8
	ldy addr8
	sty addr8
	cmpd ,x
	cmpy ,x
	ldy ,x
	sty ,x
	cmpd addr16
	cmpy addr16
	ldy addr16
	sty addr16
	lds #$4444
	lds addr8
	sts addr8
	lds ,x
	sts ,x
	lds addr16
	sts addr16
	swi3
	cmpu #$4444
	cmps #$4444
	cmpu addr8
	cmps addr8
	cmpu ,x
	cmps ,x
	cmpu addr16
	cmps addr16

	nop
	sync
	lbra addr16
	lbsr addr16
	daa
	orcc #$ff
	andcc #$00
	sex
	exg a,b
	tfr a,b


labx	bra labx
	brn labx
	bhi labx
	bls labx
	bhs labx
	bcc labx
	blo labx
	bcs labx
	bne labx
	beq labx
	bvc labx
	bvs labx
	bpl labx
	bmi labx
	bge labx
	blt labx
	bgt labx
	ble labx

	leax ,x
	leay ,x
	leas ,x
	leau ,x
	pshs x
	puls x
	pshu x
	pulu x
	rts
	abx
	rti
	cwai #$00
	mul 
	swi

	nega
	coma
	lsra
	rora
	asra
	asla
	lsla
	rola
	deca
	inca
	tsta
	clra

	negb
	comb
	lsrb
	rorb
	asrb
	aslb
	lslb
	rolb
	decb
	incb
	tstb
	clrb

	neg ,x
	com ,x
	lsr ,x
	ror ,x
	asr ,x
	asl ,x
	lsl ,x
	rol ,x
	dec ,x
	inc ,x
	tst ,x
	jmp ,x
	clr ,x

	neg addr16
	com addr16
	lsr addr16
	ror addr16
	asr addr16
	asl addr16
	lsl addr16
	rol addr16
	dec addr16
	inc addr16
	tst addr16
	jmp addr16
	clr addr16

	suba #$22
	cmpa #$22
	sbca #$22
	subd #$4444
	anda #$22
	bita #$22
	lda #$22
	eora #$22
	adca #$22
	ora #$22
	adda #$22
	cmpx #$4444
laby	bsr laby
	ldx #$4444

	suba addr8
	cmpa addr8
	sbca addr8
	subd addr8
	anda addr8
	bita addr8
	lda addr8
	sta addr8
	eora addr8
	adca addr8
	ora addr8
	adda addr8
	cmpx addr8
	jsr addr8
	ldx addr8
	stx addr8

	suba ,x
	cmpa ,x
	sbca ,x
	subd ,x
	anda ,x
	bita ,x
	lda ,x
	sta ,x
	eora ,x
	adca ,x
	ora ,x
	adda ,x
	cmpx ,x
	jsr ,x
	ldx ,x
	stx ,x

	suba addr16
	cmpa addr16
	sbca addr16
	subd addr16
	anda addr16
	bita addr16
	lda addr16
	sta addr16
	eora addr16
	adca addr16
	ora addr16
	adda addr16
	cmpx addr16
	jsr addr16
	ldx addr16
	stx addr16

	subb #$22
	cmpb #$22
	sbcb #$22
	addd #$4444
	andb #$22
	bitb #$22
	ldb #$22
	eorb #$22
	adcb #$22
	orb #$22
	addb #$22
	ldd #$4444
	ldu #$4444

	subb addr8
	cmpb addr8
	sbcb addr8
	addd addr8
	andb addr8
	bitb addr8
	ldb addr8
	stb addr8
	eorb addr8
	adcb addr8
	orb addr8
	addb addr8
	ldd addr8
	std addr8
	ldu addr8
	stu addr8

	subb ,x
	cmpb ,x
	sbcb ,x
	addd ,x
	andb ,x
	bitb ,x
	ldb ,x
	stb ,x
	eorb ,x
	adcb ,x
	orb ,x
	addb ,x
	ldd ,x
	std ,x
	ldu ,x
	stu ,x

	subb addr16
	cmpb addr16
	sbcb addr16
	addd addr16
	andb addr16
	bitb addr16
	ldb addr16
	stb addr16
	eorb addr16
	adcb addr16
	orb addr16
	addb addr16
	ldd addr16
	std addr16
	ldu addr16
	stu addr16

	tfr d,d
	tfr d,x
	tfr d,y
	tfr d,u
	tfr d,s
	tfr d,pc
	tfr a,a
	tfr a,b
	tfr a,cc
	tfr a,dp
	tfr d,d
	tfr x,d
	tfr y,d
	tfr u,d
	tfr s,d
	tfr pc,d
	tfr a,a
	tfr b,a
	tfr cc,a
	tfr dp,a

	pshs pc
	pshs u
	pshu s
	pshs x
	pshs y
	pshs dp
	pshs d
	pshs a,b
	pshs a
	pshs b
	pshs cc
	pshs pc,u,x,y,dp,a,b,cc

	lda 0,x
	lda 1,x
	lda 2,x
	lda 3,x
	lda 4,x
	lda 5,x
	lda 6,x
	lda 7,x
	lda 8,x
	lda 9,x
	lda 10,x
	lda 11,x
	lda 12,x
	lda 13,x
	lda 14,x
	lda 15,x
	lda -16,x
	lda -15,x
	lda -14,x
	lda -13,x
	lda -12,x
	lda -11,x
	lda -10,x
	lda -9,x
	lda -8,x
	lda -7,x
	lda -6,x
	lda -5,x
	lda -4,x
	lda -3,x
	lda -2,x
	lda -1,x
	lda 1,y
	lda -1,y
	lda 1,u
	lda -1,u
	lda 1,s
	lda -1,s
	lda ,x+
	ldd ,x++
	lda ,-x
	ldd ,--x
	lda ,x
	lda b,x
	lda a,x
	lda -128,x
	lda 33,x
	lda 127,x
	lda -129,x
	lda $1234,x
	lda d,x
labz	lda labz,pcr
	lda addr16,pcr
	lda [,x++]
	lda [,--x]
	lda [,x]
	lda [b,x]
	lda [a,x]
	lda [33,x]
	lda [1,x]
	lda [$1234,x]
	lda [d,x]
	lda [labz,pcr]
	lda [addr16,pcr]
	lda [addr16]
	lda ,y+
	lda ,u+
	lda ,s+
	ldy [addr16]
	ldy addr16,pcr

 	