        ; 6809 Test program.

testnr  equ 128

        org $400
        jmp entry
error  ldx #errmsg
        bsr outs
        lda testnr
        bsr outa
        ldx #newline
        bsr outs
        swi

errmsg fcb "ERROR ",0
newline fcb 13,10,0
outs    ldb ,x+
        beq done1
        jsr 3
        bra outs
done1   rts
outdig  addb # 48
        cmpb # 57
        bls  od2
        addb #7
od2     jsr 3
        rts
outa    tfr a,b
        lsrb
        lsrb
        lsrb
        lsrb
        bsr outdig
        tfr a,b
        andb # 15
        bra outdig
passmsg  fcb "PASSED ",0
good    ldx #passmsg
        jsr outs
        lda testnr
        jsr outa
        ldx #newline
        jsr outs
        inc testnr
        rts

entry   clr testnr
        jsr good          ;test #0, does it print msg?
        andcc #0          ;test #1, conditional (long) branches
        lbvs error        ;         andcc, orcc
        lbcs error
        lbeq error
        lbmi error
        lbls error
        lblt error
        lble error
        lbrn error
        bvs errt1
        bcs errt1
        beq errt1
        bmi errt1
        bls errt1
        blt errt1
        ble errt1
        brn errt1
        lbvc goot1
errt1   jmp error
goot1   lbcc goot2
        jmp error
goot2   lbne goot3
        jmp error
goot3   lbpl goot4
        jmp error
goot4   lbhi goot5
        jmp error
goot5   lbge goot6
        jmp error
goot6   lbgt goot7
        jmp error
goot7   lbra goot8
        jmp error
goot8   bvc goot9
        jmp error
goot9   bcc goot10
        jmp error
goot10  bne goot11
        jmp error
goot11  bpl goot12
        jmp error
goot12  bhi goot13
        jmp error
goot13  bge goot14
        jmp error
goot14  bgt goot15
        jmp error
goot15  bra goot16
        jmp error
goot16  tfr cc,a
        tsta
        lbne error
        andcc #0
        orcc #1
        lbcc error
        lbeq error
        lbvs error
        lbmi error
        orcc #2
        lbvc error
        lbeq error
        lbmi error
        orcc #4
        lbne error
        lbmi error
        orcc #8
        lbpl error
        tfr cc,a
        cmpa #15
        lbne error
        orcc #15
        orcc #240
        tfr cc,a
        inca
        lbne error
        orcc #255
        andcc #$aa
        tfr cc,a
        cmpa #$aa
        lbne error
        jsr good

        lds #$8000       ; test #2: registers and their values, tfr, exg
        lda #$28
        ldb #$7f
        ldu #3417
        ldx #2221
        ldy #16555
        cmpa #$28
        lbne error
        cmpb #$7f
        lbne error
        cmpd #$287f
        lbne error
        cmpx #2221
        lbne error
        cmpy #13
        lbeq error
        cmpy #16555
        lbne error
        cmpu #3417
        lbne error
        cmps #$8000
        lbne error
        exg x,y
        cmpx #16555
        lbne error
        cmpy #2221
        lbne error
        exg x,d
        cmpd #16555
        lbne error
        cmpx #$287f
        lbne error
        cmpy #2221
        lbne error
        exg x,d
        exg a,dp
        tsta
        lbne error
        exg a,dp
        exg a,b
        cmpa #$7f
        lbne error
        cmpb #$28
        lbne error
        tfr b,a
        cmpb #$28
        lbne error
        cmpa #$28
        lbne error
        tfr u,x
        cmpu #3417
        lbne error
        cmpx #3417
        lbne error
        tfr pc,x
here    cmpx #here
        lbne error
        tfr u,s
        cmps #3417
        lbne error
        lds #$8000
        clra
        tfr b,cc
        tfr cc,a
        cmpa #$28
        lbne error
        jsr good

        lda #128       ;Arithmetic and their status.
        adda #255
        lbcc error
        lbvc error
        lbmi error
        cmpa #127
        lbne error
        lda #0
        adda #255
        lbcs error
        lbvs error
        lbpl error
        cmpa #255
        lbne error
        orcc #1
        lda #255
        adca #0
        lbne error
        lbmi error
        lbcc error
        lda #216
        adda #40




        lbne error
        lda #80
        adda #40
        lbcs error
        lbvs error
        cmpa #120
        lbne error
        orcc #1
        lda #80
        adca #40
        lbcs error
        lbvs error
        cmpa #121
        lbne error
        andcc #254
        ldb #80
        adcb #40
        lbcs error
        lbvs error
        cmpb #120
        lbne error
        ldb #80
        subb #120
        lbcc error
        lbvs error
        cmpb #216
        lbne error
        andcc #254
        lda #140
        sbca #20
        lbvc error
        lbcs error
        cmpa #120
        lbne error
        orcc #1
        lda #140
        sbca #20
        lbvc error
        lbcs error
        cmpa #119
        lbne error
        ldd #40000
        subd #20000
        lbvc error
        lbcs error
        cmpd #20000
        lbne error
        ldd #20000
        subd #40000
        lbvc error
        lbcc error
        cmpd #-20000
        lbne error
        ldd #30000
        addd #-20000
        lbcc error
        lbvs error
        cmpd #10000
        lbne error
        jsr good

        lda #$23      ;Test #4 decimal arithmetic.
        adda #$34
        daa
        lbcs error
        cmpa #$57
        lbne error
        orcc #1
        lda #$19
        adca #$29
        daa
        lbcs error
        cmpa #$49
        lbne error
        lda #$92
        adda #$8
        daa
        lbcc error
        cmpa #$00
        jsr good

        lda #128       ;Test#5  MUL and SEX
        ldb #2
        mul
        lbeq error
        lbcs error
        cmpd #256
        lbne error
        lda #0
        ldb #23
        mul
        lbne error
        lbcs error
        cmpd #0
        lbne error
        lda #10
        ldb #20
        mul
        lbcc error
        cmpd #200
        lbne error
        lda #100
        ldb #49
        mul
        cmpd #4900
        lbne error
        clrb
        sex
        cmpd #0
        lbne error
        ldb #128
        sex
        cmpd #-128
        lbne error
        ldb #50
        sex
        cmpd #50
        lbne error
        jsr good

        lda #$55    ; Test #6 Shifts and rotates.
        asla
        lbcs error
        cmpa #$aa
        lbne error
        asla
        lbcc error
        cmpa #$54
        lbne error
        lda #$0
        andcc #254
        rola
        lbne error
        orcc #1
        rola
        deca
        lbne error
        andcc #254
        rora
        lbne error
        orcc #1
        rora
        cmpa #128
        lbne error
        asra
        cmpa #192
        lbne error
        lsra
        cmpa #96
        lbne error
        ldb # 54
        aslb
        cmpb # 108
        lbne error
        jsr good

        orcc #15          ; Test #7 INC, DEC and NEG
        lda # 33
        inca
        lbeq error
        lbvs error
        lbcc error
        lbmi error
        deca
        lbeq error
        lbvs error
        lbcc error
        lbmi error
        clra
        andcc #254
        deca
        lbcs error
        lbpl error
        inca
        lbne error
        ldb #126
        negb
        lbvs error
        lbcc error
        cmpb #130
        lbne error
        decb
        decb
        negb
        lbvc error
        cmpb #128
        lbne error
        clrb
        negb
        lbcs error
        lbne error
        jsr good

	;test #8 Addessing modes.	
	ldx #testdat+4
	lda ,x
	cmpa #5
        lbne error 
	lda ,x+
	cmpa #5
 	lbne error
	cmpx #testdat+5
	lbne error
	ldd ,x++
	cmpd #6*256+7
	lbne error
	cmpx #testdat+7
	lbne error
	ldx #testdat+4
	lda ,-x
	cmpa #4
	lbne error
	cmpx #testdat+3
	lbne error
	ldd ,--x
	cmpd #2*256+3
	lbne error
        cmpx #testdat+1
	lbne error
	ldx #testdat+4
	lda -2,x
	cmpa #3
	lbne error
	lda 2,x
	cmpa #7
	lbne error
	ldx #td1
	ldd [,x]
	cmpd #3*256+4
	lbne error
	cmpx #td1
	lbne error
	jsr good			
	bra next1
testdat	fcb 1,2,3,4,5,6,7,8,9,10
td1	fdb testdat+2
next1   

        swi
        end 



