/* 6809 Simulator V09.

   Copyright 1994, L.C. Benschop, Eidnhoven The Netherlands.
   This version of the program is distributed under the terms and conditions
   of the GNU General Public License version 2. See the file COPYING.
   THERE IS NO WARRANTY ON THIS PROGRAM!!!
   
   This program simulates a 6809 processor.
   
   System dependencies: short must be 16 bits.
                        char  must be 8 bits.
                        long must be more than 16 bits.
                        arrays up to 65536 bytes must be supported.
                        machine must be twos complement.
   Most Unix machines will work. For MSODS you need long pointers
   and you may have to malloc() the mem array of 65536 bytes.
                 
   Define BIG_ENDIAN if you have a big-endian machine (680x0 etc)              
   
   Special instructions:                     
   SWI2 writes char to stdout from register B.
   SWI3 reads char from stdout to register B, sets carry at EOF.
               (or when no key available when using term control).
   SWI retains its normal function. 
   CWAI and SYNC stop simulator.
   
*/


#include <stdio.h>
#include <stdlib.h>

#define engine extern

#include "v09.h"

FILE *tracefile;

void do_trace(void)
{
 Word pc=pcreg;
 Byte ir;
 fprintf(tracefile,"pc=%04x ",pc);
 ir=mem[pc++];
 fprintf(tracefile,"i=%02x ",ir);
 if((ir&0xfe)==0x10)
    fprintf(tracefile,"%02x ",mem[pc]);else fprintf(tracefile,"   ");
     fprintf(tracefile,"x=%04x y=%04x u=%04x s=%04x a=%02x b=%02x cc=%02x\n",
                   xreg,yreg,ureg,sreg,*areg,*breg,ccreg);
} 
 
read_image()
{
 FILE *image;
 if((image=fopen("v09.rom","rb"))!=NULL) {
  fread(mem+0x8000,0x8000,1,image);
  fclose(image);
 } else {
    perror("v09, image file");
    exit(2);
 }
}

void usage(void)
{
 fprintf(stderr,"Usage: v09 [-t tracefile [-tl addr] "
                "[-th addr] ]\n[-e escchar] \n");
 exit(1); 
}


#define CHECKARG if(i==argc)usage();else i++;

main(int argc,char *argv[])
{
 Word loadaddr=0x100;
 char *imagename=0;
 int i;
 escchar='\x1d'; 
 tracelo=0;tracehi=0xffff;
 for(i=1;i<argc;i++) {
    if (strcmp(argv[i],"-t")==0) {
     i++;
     if((tracefile=fopen(argv[i],"w"))==NULL) {
         perror("v09, tracefile");
         exit(2);
     }
     tracing=1;attention=1;    
   } else if (strcmp(argv[i],"-tl")==0) {
     i++;
     tracelo=strtol(argv[i],(char**)0,0);
   } else if (strcmp(argv[i],"-th")==0) {
     i++;
     tracehi=strtol(argv[i],(char**)0,0);
   } else if (strcmp(argv[i],"-e")==0) {
     i++;
     escchar=strtol(argv[i],(char**)0,0);
   } else usage();
 }   
 #ifdef MSDOS
 if((mem=farmalloc(65535))==0) { 
   fprintf(stderr,"Not enough memory\n");
   exit(2);
 } 
 #endif
 read_image(); 
 set_term(escchar);
 pcreg=(mem[0xfffe]<<8)+mem[0xffff]; 
 interpr();
}

