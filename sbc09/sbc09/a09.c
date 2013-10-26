/* A09, 6809 Assembler. 
   
   (C) Copyright 1993,1994 L.C. Benschop. 
   This verision of the program is distributed under the terms and conditions 
   of the GNU General Public License version 2. See file the COPYING for details.	
   THERE IS NO WARRANTY ON THIS PROGRAM. 
	
   Generates binary image file from the lowest to
   the highest address with actually assembled data.
   
   Machine dependencies:
                  char is 8 bits.
                  short is 16 bits.
                  integer arithmetic is twos complement.
   
   syntax a09 [-o filename] [-l filename] sourcefile.
                  
   Options
   -o filename name of the output file (default name minus a09 suffix) 
   -s filename name of the s-record output file (default its a binary file)
   -l filename list file name (default no listing)
   
   recognized pseudoops:
    extern public
    macro endm if else endif 
    org equ set setdp
    fcb fcw fdb fcc rmb  
    end include title   
   Not all of these are actually IMPLEMENTED!!!!!! 
    
   v0.1 93/11/03 Initial version.
    
   v0.2 94/03/21 Fixed PC relative addressing bug
       	         Added SET, SETDP, INCLUDE. IF/ELSE/ENDIF
    	         No macros yet, and no separate linkable modules.
    
*/

#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define NLABELS 2048
#define MAXIDLEN 16
#define MAXLISTBYTES 7
#define FNLEN 30
#define LINELEN 128

struct oprecord{char * name; 
                unsigned char cat; 
                unsigned short code;};    

/* Instruction categories:
   0 one byte oprcodes   NOP
   1 two byte opcodes    SWI2
   2 opcodes w. imm byte ANDCC
   3 LEAX etc.
   4 short branches. BGE
   5 long branches 2byte opc LBGE 
   6 long branches 1byte opc LBRA
   7 accumulator instr.      ADDA
   8 double reg instr 1byte opc LDX
   9 double reg instr 2 byte opc LDY
   10 single address instrs NEG
   11 TFR, EXG
   12 push,pull
   13 pseudoops
*/
 
struct oprecord optable[]={
  {"ABX",0,0x3a},{"ADCA",7,0x89},{"ADCB",7,0xc9},
  {"ADDA",7,0x8b},{"ADDB",7,0xcb},{"ADDD",8,0xc3},
  {"ANDA",7,0X84},{"ANDB",7,0xc4},{"ANDCC",2,0x1c},
  {"ASL",10,0x08},{"ASLA",0,0x48},{"ASLB",0,0x58},
  {"ASR",10,0x07},{"ASRA",0,0x47},{"ASRB",0,0x57},
  {"BCC",4,0x24},{"BCS",4,0x25},{"BEQ",4,0x27},
  {"BGE",4,0x2c},{"BGT",4,0x2e},{"BHI",4,0x22},
  {"BHS",4,0x24},{"BITA",7,0x85},{"BITB",7,0xc5},
  {"BLE",4,0x2f},{"BLO",4,0x25},{"BLS",4,0x23},
  {"BLT",4,0x2d},{"BMI",4,0x2b},{"BNE",4,0x26},
  {"BPL",4,0x2a},{"BRA",4,0x20},{"BRN",4,0x21},
  {"BSR",4,0x8d},
  {"BVC",4,0x28},{"BVS",4,0x29},
  {"CLC",1,0x1cfe},{"CLF",1,0x1cbf},{"CLI",1,0x1cef},
  {"CLIF",1,0x1caf},
  {"CLR",10,0x0f},{"CLRA",0,0x4f},{"CLRB",0,0x5f},
  {"CLV",1,0x1cfd},
  {"CMPA",7,0x81},{"CMPB",7,0xc1},{"CMPD",9,0x1083},
  {"CMPS",9,0x118c},{"CMPU",9,0x1183},{"CMPX",8,0x8c},
  {"CMPY",9,0x108c},
  {"COM",10,0x03},{"COMA",0,0x43},{"COMB",0,0x53},
  {"CWAI",2,0x3c},{"DAA",0,0x19},
  {"DEC",10,0x0a},{"DECA",0,0x4a},{"DECB",0,0x5a},
  {"DES",1,0x327f},{"DEU",1,0x335f},{"DEX",1,0x301f},
  {"DEY",1,0x313f},
  {"ELSE",13,1},{"END",13,2},{"ENDIF",13,3},
  {"ENDM",13,4},{"EORA",7,0x88},{"EORB",7,0xc8},
  {"EQU",13,5},{"EXG",11,0x1e},{"EXTERN",13,6},
  {"FCB",13,7},{"FCC",13,8},{"FCW",13,9},
  {"FDB",13,9},{"IF",13,10},
  {"INC",10,0x0c},{"INCA",0,0x4c},{"INCB",0,0x5c},
  {"INCLUDE",13,16},
  {"INS",1,0x3261},{"INU",1,0x3341},{"INX",1,0x3001},
  {"INY",1,0x3121},{"JMP",10,0x0e},{"JSR",8,0x8d},
  {"LBCC",5,0x1024},{"LBCS",5,0x1025},{"LBEQ",5,0x1027},
  {"LBGE",5,0x102c},{"LBGT",5,0x102e},{"LBHI",5,0x1022},
  {"LBHS",5,0x1024},
  {"LBLE",5,0x102f},{"LBLO",5,0x1025},{"LBLS",5,0x1023},
  {"LBLT",5,0x102d},{"LBMI",5,0x102b},{"LBNE",5,0x1026},
  {"LBPL",5,0x102a},{"LBRA",6,0x16},{"LBRN",5,0x1021},
  {"LBSR",6,0x17},
  {"LBVC",5,0x1028},{"LBVS",5,0x1029},
  {"LDA",7,0x86},{"LDB",7,0xc6},{"LDD",8,0xcc},
  {"LDS",9,0x10ce},{"LDU",8,0xce},{"LDX",8,0x8e},
  {"LDY",9,0x108e},{"LEAS",3,0x32},
  {"LEAU",3,0x33},{"LEAX",3,0x30},{"LEAY",3,0x31},
  {"LSL",10,0x08},{"LSLA",0,0x48},{"LSLB",0,0x58},
  {"LSR",10,0x04},{"LSRA",0,0x44},{"LSRB",0,0x54},
  {"MACRO",13,11},{"MUL",0,0x3d},
  {"NEG",10,0x00},{"NEGA",0,0x40},{"NEGB",0,0x50},
  {"NOP",0,0x12},
  {"ORA",7,0x8a},{"ORB",7,0xca},{"ORCC",2,0x1a},
  {"ORG",13,12},
  {"PSHS",12,0x34},{"PSHU",12,0x36},{"PUBLIC",13,13},
  {"PULS",12,0x35},{"PULU",12,0x37},{"RMB",13,0},
  {"ROL",10,0x09},{"ROLA",0,0x49},{"ROLB",0,0x59},
  {"ROR",10,0x06},{"RORA",0,0x46},{"RORB",0,0x56},
  {"RTI",0,0x3b},{"RTS",0,0x39},
  {"SBCA",7,0x82},{"SBCB",7,0xc2},
  {"SEC",1,0x1a01},{"SEF",1,0x1a40},{"SEI",1,0x1a10},
  {"SEIF",1,0x1a50},{"SET",13,15},
  {"SETDP",13,14},{"SEV",1,0x1a02},{"SEX",0,0x1d},
  {"STA",7,0x87},{"STB",7,0xc7},{"STD",8,0xcd},
  {"STS",9,0x10cf},{"STU",8,0xcf},{"STX",8,0x8f},
  {"STY",9,0x108f},
  {"SUBA",7,0x80},{"SUBB",7,0xc0},{"SUBD",8,0x83},
  {"SWI",0,0x3f},{"SWI2",1,0x103f},{"SWI3",1,0x113f},
  {"SYNC",0,0x13},{"TFR",11,0x1f},{"TITLE",13,18},
  {"TST",10,0x0d},{"TSTA",0,0x4d},{"TSTB",0,0x5d},
};

struct symrecord{char name[MAXIDLEN+1];
                 char cat;
                 unsigned short value;
                };
                
int symcounter=0;

/* Symbol categories.
   0 Constant value (from equ).
   1 Variable value (from set)
   2 Address within program module (label).
   3 Variable containing address.
   4 Adress in other program module (extern)
   5 Variable containing external address.
   6 Unresolved address.
   7 Variable containing unresolved address.
   8 Public label.
   9 Macro definition.
  10 Public label (yet undefined).
  11 parameter name.
  12 local label.
  13 empty.
*/
  
struct symrecord symtable[NLABELS];                   
  
struct oprecord * findop(char * nm)
/* Find operation (mnemonic) in table using binary search */
{
 int lo,hi,i,s;
 lo=0;hi=sizeof(optable)/sizeof(optable[0])-1;
 do {
  i=(lo+hi)/2;
  s=strcmp(optable[i].name,nm);
  if(s<0) lo=i+1;
  else if(s>0) hi=i-1;
  else break;
 } while(hi>=lo);     
 if (s) return NULL;
 return optable+i;
}  

struct symrecord * findsym(char * nm)
/* finds symbol table record; inserts if not found 
   uses binary search, maintains sorted table */
{
 int lo,hi,i,j,s;
 lo=0;hi=symcounter-1;
 s=1;i=0;
 while (hi>=lo) {
  i=(lo+hi)/2;
  s=strcmp(symtable[i].name,nm);
  if(s<0) lo=i+1;
  else if(s>0) hi=i-1;
  else break;
 }
 if(s) {
  i=(s<0?i+1:i);
  if(symcounter==NLABELS) {
   fprintf(stderr,"Sorry, no storage for symbols!!!");
   exit(4);
  } 
  for(j=symcounter;j>i;j--) symtable[j]=symtable[j-1];
  symcounter++;
  strcpy(symtable[i].name,nm);
  symtable[i].cat=13;
 }    
 return symtable+i;
}  

FILE *listfile,*objfile;
char listname[FNLEN+1],objname[FNLEN+1],srcname[FNLEN+1],curname[FNLEN+1];
int lineno;

outsymtable()
{
 int i,j=0;
 fprintf(listfile,"\nSYMBOL TABLE");
 for(i=0;i<symcounter;i++) 
 if(symtable[i].cat!=13) {
  if(j%4==0)fprintf(listfile,"\n");
  fprintf(listfile,"%10s %02d %04x",symtable[i].name,symtable[i].cat,
                       symtable[i].value); 
  j++;
 }
 fprintf(listfile,"\n");
} 

struct regrecord{char *name;unsigned char tfr,psh;};
struct regrecord regtable[]=
                 {{"D",0x00,0x06},{"X",0x01,0x10},{"Y",0x02,0x20},
                  {"U",0x03,0x40},{"S",0x04,0x40},{"PC",0x05,0x80},
                  {"A",0x08,0x02},{"B",0x09,0x04},{"CC",0x0a,0x01},
                  {"CCR",0x0a,0x01},{"DP",0x0b,0x08},{"DPR",0x0b,0x08}};

struct regrecord * findreg(char *nm)
{
 int i;
 for(i=0;i<12;i++) {
  if(strcmp(regtable[i].name,nm)==0) return regtable+i;
 }
 return 0;                   
}


char pass;             /* Assembler pass=1 or 2 */
char listing;          /* flag to indicate listing */
char relocatable;      /* flag to indicate relocatable object. */  
char terminate;        /* flag to indicate termination. */ 
char generating;       /* flag to indicate that we generate code */
unsigned short loccounter,oldlc;  /* Location counter */

char inpline[128];     /* Current input line (not expanded)*/
char srcline[128];     /* Current source line */ 
char * srcptr;         /* Pointer to line being parsed */

char unknown;          /* flag to indicate value unknown */
char certain;          /* flag to indicate value is certain at pass 1*/
int error;             /* flags indicating errors in current line. */
int errors;            /* number of errors */
char exprcat;          /* category of expression being parsed, eg. 
                          label or constant, this is important when
                          generating relocatable object code. */

 
char namebuf[MAXIDLEN+1]; 

scanname()
{
 int i=0;
 char c;
 while(1) {
   c=*srcptr++;
   if(c>='a'&&c<='z')c-=32;
   if((c<'0'||c>'9')&&(c<'A'||c>'Z'))break;
   if(i<MAXIDLEN)namebuf[i++]=c;
 }
 namebuf[i]=0;
 srcptr--;  
}

skipspace()
{
 char c;
 do {
  c=*srcptr++;
 } while(c==' '||c=='\t');
 srcptr--;
} 

short scanexpr(int);

short scandecimal()
{
 char c;
 short t=0;
 c=*srcptr++;
 while(isdigit(c)) {
  t=t*10+c-'0';
  c=*srcptr++;
 }
 srcptr--;
 return t;
} 

short scanhex()
{
 short t=0,i=0;
 srcptr++;
 scanname();
 while(namebuf[i]>='0'&&namebuf[i]<='F') {
  t=t*16+namebuf[i]-'0';
  if(namebuf[i]>'9')t-=7;
  i++;
 }  
 if(i==0)error|=1;
 return t;
}

short scanchar()
{
 short t;
 srcptr++;
 t=*srcptr;
 if(t)srcptr++;
 if (*srcptr=='\'')srcptr++;
 return t;
}

short scanbin()
{
 char c;
 short t=0;
 srcptr++;
 c=*srcptr++;
 while(c=='0'||c=='1') {
  t=t*2+c-'0';
  c=*srcptr++;
 }
 srcptr--;
 return t;
}

short scanoct()
{
 char c;
 short t=0;
 srcptr++;
 c=*srcptr++;
 while(c>='0'&&c<='7') {
  t=t*8+c-'0';
  c=*srcptr++;
 }
 srcptr--;
 return t;
}


short scanlabel()
{
 struct symrecord * p;
 scanname();
 p=findsym(namebuf);
 if(p->cat==13) {
   p->cat=6;
   p->value=0;
 }
 if(p->cat==9||p->cat==11)error|=1;
 exprcat=p->cat&14;
 if(exprcat==6||exprcat==10)unknown=1;
 if(((exprcat==2||exprcat==8)
     && (unsigned short)(p->value)>(unsigned short)loccounter)||
     exprcat==4)
   certain=0;
 if(exprcat==8||exprcat==6||exprcat==10)exprcat=2;   
 return p->value;
}
 
/* expression categories...
   all zeros is ordinary constant.
   bit 1 indicates address within module.
   bit 2 indicates external address.
   bit 4 indicates this can't be relocated if it's an address.
   bit 5 indicates address (if any) is negative.
*/ 
 
 
 
short scanfactor()
{
 char c;
 short t;
 skipspace();
 c=*srcptr;
 if(isalpha(c))return scanlabel();
 else if(isdigit(c))return scandecimal();
 else switch(c) {
  case '*' : srcptr++;exprcat|=2;return loccounter;
  case '$' : return scanhex();
  case '%' : return scanbin();
  case '@' : return scanoct();
  case '\'' : return scanchar();
  case '(' : srcptr++;t=scanexpr(0);skipspace();
             if(*srcptr==')')srcptr++;else error|=1;
             return t; 
  case '-' : srcptr++;exprcat^=32;return -scanfactor();
  case '+' : srcptr++;return scanfactor();
  case '!' : srcptr++;exprcat|=16;return !scanfactor();
  case '~' : srcptr++;exprcat|=16;return ~scanfactor();           
 }
 error|=1;
 return 0;
}

#define EXITEVAL {srcptr--;return t;}

#define RESOLVECAT if((oldcat&15)==0)oldcat=0;\
           if((exprcat&15)==0)exprcat=0;\
           if((exprcat==2&&oldcat==34)||(exprcat==34&&oldcat==2)) {\
             exprcat=0;\
             oldcat=0;}\
           exprcat|=oldcat;\
/* resolve such cases as constant added to address or difference between
   two addresses in same module */           
 

short scanexpr(int level) /* This is what you call _recursive_ descent!!!*/
{
 short t,u;
 char oldcat,c;
 exprcat=0;
 if(level==10)return scanfactor();
 t=scanexpr(level+1);
 while(1) {
  skipspace();
  c=*srcptr++; 
  switch(c) {
  case '*':oldcat=exprcat;
           t*=scanexpr(10);
           exprcat|=oldcat|16;
           break;
  case '/':oldcat=exprcat;
           u=scanexpr(10);
           if(u)t/=u;else error|=1;
           exprcat|=oldcat|16;
           break;
  case '%':oldcat=exprcat;
           u=scanexpr(10);
           if(u)t%=u;else error|=1;
           exprcat|=oldcat|16;
           break;
  case '+':if(level==9)EXITEVAL
           oldcat=exprcat;
           t+=scanexpr(9);
           RESOLVECAT
           break;
  case '-':if(level==9)EXITEVAL              
           oldcat=exprcat;
           t-=scanexpr(9);
           exprcat^=32;
           RESOLVECAT
           break;
  case '<':if(*(srcptr)=='<') {
            if(level>=8)EXITEVAL
            srcptr++;
            oldcat=exprcat;
            t<<=scanexpr(8);
            exprcat|=oldcat|16;
            break; 
           } else if(*(srcptr)=='=') {
            if(level>=7)EXITEVAL
            srcptr++;
            oldcat=exprcat;
            t=t<=scanexpr(7);
            exprcat|=oldcat|16;
            break;
           } else {
            if(level>=7)EXITEVAL
            oldcat=exprcat;
            t=t<scanexpr(7);
            exprcat|=oldcat|16;
            break;
           }
  case '>':if(*(srcptr)=='>') {
            if(level>=8)EXITEVAL
            srcptr++;
            oldcat=exprcat;
            t>>=scanexpr(8);
            exprcat|=oldcat|16;
            break; 
           } else if(*(srcptr)=='=') {
            if(level>=7)EXITEVAL
            srcptr++;
            oldcat=exprcat;
            t=t>=scanexpr(7);
            exprcat|=oldcat|16;
            break;
           } else {
            if(level>=7)EXITEVAL
            oldcat=exprcat;
            t=t>scanexpr(7);
            exprcat|=oldcat|16;
            break;
           }
  case '!':if(level>=6||*srcptr!='=')EXITEVAL
           srcptr++;
           oldcat=exprcat;
           t=t!=scanexpr(6);
           exprcat|=oldcat|16;
           break;             
  case '=':if(level>=6)EXITEVAL
           if(*srcptr=='=')srcptr++;
           oldcat=exprcat;
           t=t==scanexpr(6);
           exprcat|=oldcat|16;
           break;
  case '&':if(level>=5)EXITEVAL
           oldcat=exprcat;
           t&=scanexpr(5);
           exprcat|=oldcat|16;
           break;             
  case '^':if(level>=4)EXITEVAL
           oldcat=exprcat;
           t^=scanexpr(4);
           exprcat|=oldcat|16;
           break;
  case '|':if(level>=3)EXITEVAL
           oldcat=exprcat;
           t|=scanexpr(3);
           exprcat|=oldcat|16;                                        
  default: EXITEVAL        
  }
 }
}

char mode; /* addressing mode 0=immediate,1=direct,2=extended,3=postbyte
               4=pcrelative(with postbyte) 5=indirect 6=pcrel&indirect*/
char opsize; /*desired operand size 0=dunno,1=5,2=8,3=16*/
short operand;
unsigned char postbyte;

int dpsetting;


int scanindexreg()
{
 char c;
 c=*srcptr;
 if(islower(c))c-=32;
 switch(c) {
  case 'X':return 1;
  case 'Y':postbyte|=0x20;return 1;
  case 'U':postbyte|=0x40;return 1;
  case 'S':postbyte|=0x60;return 1;
  default: return 0;
 }  
}

set3()
{
 if(mode<3)mode=3;
}

scanspecial()
{
 set3();
 skipspace();
 if(*srcptr=='-') {
  srcptr++;
  if(*srcptr=='-') {
   srcptr++;
   postbyte=0x83;
  } else postbyte=0x82;
  if(!scanindexreg())error|=2;else srcptr++; 
 } else {
  postbyte=0x80;
  if(!scanindexreg())error|=2;else srcptr++;
  if(*srcptr=='+') {
   srcptr++;
   if(*srcptr=='+') {
    srcptr++;
    postbyte+=1;
   }  
  } else postbyte+=4;
 }    
}


scanindexed()
{
 int offs;
 set3();
 postbyte=0;
 if(scanindexreg()) {
   srcptr++;
   if(opsize==0)if(unknown||!certain)opsize=3;
                else if(operand>=-16&&operand<16&&mode==3)opsize=1;
                else if(operand>=-128&&operand<128)opsize=2;
                else opsize=3;
   switch(opsize) {
   case 1:postbyte+=(operand&31);opsize=0;break;
   case 2:postbyte+=0x88;break;
   case 3:postbyte+=0x89;break;
   }                 
 } else { /*pc relative*/
  if(toupper(*srcptr)!='P')error|=2;
  else {
    srcptr++;
    if(toupper(*srcptr)!='C')error|=2;
    else {
     srcptr++;
     if(toupper(*srcptr)=='R')srcptr++;
    } 
  }    
  mode++;postbyte+=0x8c;
  if(opsize==1)opsize=2;    
 }
}

#define RESTORE {srcptr=oldsrcptr;c=*srcptr;goto dodefault;}

scanoperands()
{
 char c,d,*oldsrcptr;
 unknown=0;
 opsize=0;
 certain=1;
 skipspace();
 c=*srcptr;
 mode=0;
 if(c=='[') {
  srcptr++;
  c=*srcptr;
  mode=5;
 }
 switch(c) {
 case 'D': case 'd':
  oldsrcptr=srcptr;
  srcptr++;
  skipspace();
  if(*srcptr!=',')RESTORE else {
     postbyte=0x8b;
     srcptr++;
     if(!scanindexreg())RESTORE else {srcptr++;set3();}
  }
  break;    
 case 'A': case 'a':
  oldsrcptr=srcptr;
  srcptr++;
  skipspace();
  if(*srcptr!=',')RESTORE else {
     postbyte=0x86;
     srcptr++;
     if(!scanindexreg())RESTORE else {srcptr++;set3();}
  } 
  break;
 case 'B': case 'b': 
  oldsrcptr=srcptr; 
  srcptr++;
  skipspace();
  if(*srcptr!=',')RESTORE else {
     postbyte=0x85;
     srcptr++;
     if(!scanindexreg())RESTORE else {srcptr++;set3();}
  }
  break;   
 case ',':
  srcptr++;
  scanspecial();
  break; 
 case '#':
  if(mode==5)error|=2;else mode=0;
  srcptr++;
  operand=scanexpr(0); 
  break;
 case '<':
  srcptr++;
  if(*srcptr=='<') {
   srcptr++;
   opsize=1;
  } else opsize=2;
  goto dodefault;    
 case '>':
  srcptr++;
  opsize=3;
 default: dodefault:
  operand=scanexpr(0);
  skipspace();
  if(*srcptr==',') {
   srcptr++;
   scanindexed();
  } else {
   if(opsize==0) {
    if(unknown||!certain||dpsetting==-1||
         (unsigned short)(operand-dpsetting*256)>=256)
    opsize=3; else opsize=2;
   }  
   if(opsize==1)opsize=2;         
   if(mode==5){
    postbyte=0x8f;
    opsize=3;
   } else mode=opsize-1;
  }   
 }
 if(mode>=5) {
  skipspace();
  postbyte|=0x10;
  if(*srcptr!=']')error|=2;else srcptr++;    
 }
 if(pass==2&&unknown)error|=4; 
}

unsigned char codebuf[128];
int codeptr; /* byte offset within instruction */
int suppress; /* 0=no suppress 1=until ENDIF 2=until ELSE 3=until ENDM */
int ifcount;  /* count of nested IFs within suppressed text */

unsigned char outmode; /* 0 is binary, 1 is s-records */

unsigned short hexaddr;
int hexcount;
unsigned char hexbuffer[16];
unsigned int chksum;

flushhex()
{
 int i;
 if(hexcount){
  fprintf(objfile,"S1%02X%04X",(hexcount+3)&0xff,hexaddr&0xffff);
  for(i=0;i<hexcount;i++)fprintf(objfile,"%02X",hexbuffer[i]);
  chksum+=(hexaddr&0xff)+((hexaddr>>8)&0xff)+hexcount+3;
  fprintf(objfile,"%02X\n",0xff-(chksum&0xff));
  hexaddr+=hexcount;
  hexcount=0;
  chksum=0;
 }
}

outhex(unsigned char x) 
{
 if(hexcount==16)flushhex();
 hexbuffer[hexcount++]=x;
 chksum+=x;
}

outbuffer()
{
 int i;
 for(i=0;i<codeptr;i++)
   if(!outmode)fputc(codebuf[i],objfile);else outhex(codebuf[i]);
}

char *errormsg[]={"Error in expression",
                "Illegal addressing mode",
                "Undefined label",
                "Multiple definitions of label",
                "Relative branch out of range",
                "Missing label",
                "","","","","","","","","",
                "Illegal mnemonic"
               };
report()
{
 int i;
 fprintf(stderr,"File %s, line %d:%s\n",curname,lineno,srcline);
 for(i=0;i<16;i++) {
  if(error&1) {
   fprintf(stderr,"%s\n",errormsg[i]);
   if(pass==2&&listing)fprintf(listfile,"**** %s\n",errormsg[i]);
  }
  error>>=1;
 }
 errors++;
} 

outlist()
{
 int i;
 fprintf(listfile,"%04X: ",oldlc);
 for(i=0;i<codeptr&&i<MAXLISTBYTES;i++)
  fprintf(listfile,"%02X",codebuf[i]);
 for(;i<=MAXLISTBYTES;i++)
  fprintf(listfile,"  ");
 fprintf(listfile,"%s\n",srcline); 
}

setlabel(struct symrecord * lp)
{
 if(lp) {
  if(lp->cat!=13&&lp->cat!=6) {
   if(lp->cat!=2||lp->value!=loccounter)
    error|=8;
  } else {
   lp->cat=2;
   lp->value=loccounter;
  } 
 } 
}

putbyte(unsigned char b)
{
 codebuf[codeptr++]=b;
}

putword(unsigned short w)
{
 codebuf[codeptr++]=w>>8;
 codebuf[codeptr++]=w&0x0ff;
}

doaddress() /* assemble the right addressing bytes for an instruction */
{
 int offs;
 switch(mode) {
 case 0: if(opsize==2)putbyte(operand);else putword(operand);break; 
 case 1: putbyte(operand);break;
 case 2: putword(operand);break;
 case 3: case 5: putbyte(postbyte);
    switch(opsize) {
     case 2: putbyte(operand);break;
     case 3: putword(operand); 
    }
    break;
 case 4: case 6: offs=(unsigned short)operand-loccounter-codeptr-2;
                if(offs<-128||offs>=128||opsize==3||unknown||!certain) {
                 if((!unknown)&&opsize==2)error|=16;
                 offs--;
                 opsize=3;
                 postbyte++;
                }
                putbyte(postbyte);
                if(opsize==3)putword(offs); 
                else putbyte(offs);   
 }     
}

onebyte(int co)
{
 putbyte(co);
}

twobyte(int co)
{
 putword(co);
}

oneimm(int co)
{
 scanoperands();
 if(mode>=3)error|=2;
 putbyte(co);
 putbyte(operand);
}

lea(int co)
{
 putbyte(co);
 scanoperands();
 if(mode==0) error|=2;
 if(mode<3) {
   opsize=3;
   postbyte=0x8f;
   mode=3;
 }
 doaddress();
}

sbranch(int co)
{
 int offs;
 scanoperands();
 if(mode!=1&&mode!=2)error|=2;
 offs=(unsigned short)operand-loccounter-2;
 if(!unknown&&(offs<-128||offs>=128))error|=16;
 if(pass==2&&unknown)error|=4;
 putbyte(co);
 putbyte(offs);
}

lbra(int co)
{
 scanoperands();
 if(mode!=1&&mode!=2)error|=2;
 putbyte(co);
 putword(operand-loccounter-3);
}

lbranch(int co)
{
 scanoperands();
 if(mode!=1&&mode!=2)error|=2;
 putword(co);
 putword(operand-loccounter-4);
}

arith(int co)
{
 scanoperands();
 switch(mode) {
 case 0:opsize=2;putbyte(co);break;
 case 1:putbyte(co+0x010);break;
 case 2:putbyte(co+0x030);break;
 default:putbyte(co+0x020);
 }
 doaddress();
}

darith(int co)
{
 scanoperands();
 switch(mode) {
 case 0:opsize=3;putbyte(co);break;
 case 1:putbyte(co+0x010);break;
 case 2:putbyte(co+0x030);break;
 default:putbyte(co+0x020);
 }
 doaddress();
}

d2arith(int co)
{
 scanoperands();
 switch(mode) {
 case 0:opsize=3;putword(co);break;
 case 1:putword(co+0x010);break;
 case 2:putword(co+0x030);break;
 default:putword(co+0x020);
 }
 doaddress();
}

oneaddr(int co)
{
 scanoperands();
 switch(mode) {
 case 0: error|=2;break;
 case 1: putbyte(co);break;
 case 2: putbyte(co+0x70);break;
 default: putbyte(co+0x60);break;
 }
 doaddress();
}

tfrexg(int co)
{
 struct regrecord * p;
 putbyte(co);
 skipspace();
 scanname();
 if((p=findreg(namebuf))==0)error|=2;
 else postbyte=(p->tfr)<<4;
 skipspace();
 if(*srcptr==',')srcptr++;else error|=2;
 skipspace();
 scanname();
 if((p=findreg(namebuf))==0)error|=2;
 else postbyte|=p->tfr;
 putbyte(postbyte);
}

pshpul(int co)
{
 struct regrecord *p;
 putbyte(co);
 postbyte=0;
 do {
  if(*srcptr==',')srcptr++;
  skipspace();
  scanname(); 
  if((p=findreg(namebuf))==0)error|=2;
  else postbyte|=p->psh; 
  skipspace();
 }while (*srcptr==',');
 putbyte(postbyte);
}

pseudoop(int co,struct symrecord * lp)
{
 int i;
 char c;
 char fname[FNLEN+1];
 switch(co) {
 case 0:/* RMB */
        setlabel(lp);
        operand=scanexpr(0);
        if(unknown)error|=4;
        loccounter+=operand;
        if(generating&&pass==2) {
           if(!outmode)for(i=0;i<operand;i++)fputc(0,objfile);
           else flushhex();  
        }   
        hexaddr=loccounter;
        break;  
 case 5:/* EQU */
        operand=scanexpr(0);
        if(!lp)error|=32;
        else {
         if(lp->cat==13||lp->cat==6||
            (lp->value==(unsigned short)operand&&pass==2)) {
          if(exprcat==2)lp->cat=2;
          else lp->cat=0;
          lp->value=operand;
         } else error|=8;
        }
        break;
 case 7:/* FCB */
        setlabel(lp);
        generating=1;
        do {
        if(*srcptr==',')srcptr++;
        skipspace();
        if(*srcptr=='\"') {
         srcptr++;
         while(*srcptr!='\"'&&*srcptr)
          putbyte(*srcptr++);
         if(*srcptr=='\"')srcptr++; 
        } else {
          putbyte(scanexpr(0)); 
          if(unknown&&pass==2)error|=4;
        }  
        skipspace();
        } while(*srcptr==',');
        break; 
 case 8:/* FCC */
        setlabel(lp);
        skipspace();
        c=*srcptr++;
        while(*srcptr!=c&&*srcptr)
         putbyte(*srcptr++);
        if(*srcptr==c)srcptr++;
        break;
 case 9:/* FDB */
        setlabel(lp);
        generating=1;
        do {
         if(*srcptr==',')srcptr++;
         skipspace();
         putword(scanexpr(0));
         if(unknown&&pass==2)error|=4; 
         skipspace();     
        } while(*srcptr==',');
        break;
 case 1: /* ELSE */
        suppress=1;
        break;
 case 10: /* IF */
        operand=scanexpr(0);
        if(unknown)error|=4;
        if(!operand)suppress=2;
        break;                
 case 12: /* ORG */
         operand=scanexpr(0);
         if(unknown)error|=4;
         if(generating&&pass==2) {
           for(i=0;i<(unsigned short)operand-loccounter;i++)
                if(!outmode)fputc(0,objfile);else flushhex();
         }             
         loccounter=operand;
         hexaddr=loccounter;
         break;
  case 14: /* SETDP */
         operand=scanexpr(0);
         if(unknown)error|=4;
         if(!(operand&255))operand=(unsigned short)operand>>8;
         if((unsigned)operand>255)operand=-1;
         dpsetting=operand;              
         break;
  case 15: /* SET */
        operand=scanexpr(0);
        if(!lp)error|=32;
        else {
         if(lp->cat&1||lp->cat==6) {
          if(exprcat==2)lp->cat=3;
          else lp->cat=1;
          lp->value=operand;
         } else error|=8;
        }
        break;
   case 2: /* END */
   	terminate=1;
   	break;     
   case 16: /* INCLUDE */     
        skipspace();
        if(*srcptr=='"')srcptr++;
        for(i=0;i<FNLEN;i++) {
          if(*srcptr==0||*srcptr=='"')break;
          fname[i]=*srcptr++;
        }
        fname[i]=0;
        processfile(fname);
        codeptr=0;
        srcline[0]=0;
        break; 
 }
}


processline()
{
 struct symrecord * lp;
 struct oprecord * op;
 int co;
 char c;
 srcptr=srcline;
 oldlc=loccounter;
 error=0;
 unknown=0;certain=1;
 lp=0;
 codeptr=0;
 if(isalnum(*srcptr)) {
  scanname();lp=findsym(namebuf);
  if(*srcptr==':') srcptr++;
 } 
 skipspace();
 if(isalnum(*srcptr)) {
  scanname(); 
  op=findop(namebuf);  
  if(op) {
   if(op->cat!=13){
     setlabel(lp);
     generating=1;
   }
   co=op->code;
   switch(op->cat) {
   case 0:onebyte(co);break;
   case 1:twobyte(co);break;
   case 2:oneimm(co);break;
   case 3:lea(co);break;
   case 4:sbranch(co);break;
   case 5:lbranch(co);break;
   case 6:lbra(co);break;
   case 7:arith(co);break;
   case 8:darith(co);break;
   case 9:d2arith(co);break;
   case 10:oneaddr(co);break;
   case 11:tfrexg(co);break;
   case 12:pshpul(co);break;
   case 13:pseudoop(co,lp);
   }
   c=*srcptr;
   if(c!=' '&&*(srcptr-1)!=' '&&c!=0&&c!=';')error|=2; 
  }
  else error|=0x8000;
 }else setlabel(lp);
 if(pass==2) {
  outbuffer();
  if(listing)outlist();
 }
 if(error)report();
 loccounter+=codeptr;
}

suppressline()
{
 struct oprecord * op;
 srcptr=srcline;
 oldlc=loccounter;
 codeptr=0;
 if(isalnum(*srcptr)) {
  scanname();
  if(*srcptr==':')srcptr++;
 }
 skipspace();
 scanname();op=findop(namebuf);
 if(op && op->cat==13) {
  if(op->code==10) ifcount++;
  else if(op->code==3) {
   if(ifcount>0)ifcount--;else if(suppress==1|suppress==2)suppress=0;
  } else if(op->code==1) {
   if(ifcount==0 && suppress==2)suppress=0;
  }
 }  
 if(pass==2&&listing)outlist();
}

usage(char*nm)
{
  fprintf(stderr,"Usage: %s [-o objname] [-l listname] srcname\n",nm);
  exit(2);
}
 

getoptions(int c,char*v[])
{
 int i=0;
 if(c==1)usage(v[0]); 
 if(strcmp(v[1],"-o")==0) {
   if(c<4)usage(v[0]);
   strcpy(objname,v[2]);
   i+=2;
 }
 if(strcmp(v[i+1],"-s")==0) {
   if(c<4+i)usage(v[0]);
   strcpy(objname,v[i+2]);
   outmode=1;
   i+=2;
 }
 if(strcmp(v[i+1],"-l")==0) {
   if(c<4+i)usage(v[0]);
   strcpy(listname,v[2+i]);
   i+=2;
 }
 strcpy(srcname,v[1+i]);
 if(objname[0]==0) {
  for(i=0;i<=FNLEN;i++) {
   if(srcname[i]=='.')break;
   if(srcname[i]==0){strcpy(objname+i,".b");break;}
    objname[i]=srcname[i];
  }
 }
 listing=listname[0]!=0;       
}

expandline() 
{
 int i=0,j=0,k,j1;
 for(i=0;i<128&&j<128;i++)
 {
  if(inpline[i]=='\n') {
    srcline[j]=0;break;
  }
  if(inpline[i]=='\t') {
    j1=j;
    for(k=0;k<8-j1%8 && j<128;k++)srcline[j++]=' ';
  }else srcline[j++]=inpline[i];     
 }
 srcline[127]=0;
}


processfile(char *name)
{
 char oldname[FNLEN+1];
 int oldno;
 FILE *srcfile;
 strcpy(oldname,curname);
 strcpy(curname,name);
 oldno=lineno;
 lineno=0;
 if((srcfile=fopen(name,"r"))==0) {
  fprintf(stderr,"Cannot open source file %s\n",name);
  exit(4);
 }
 while(!terminate&&fgets(inpline,128,srcfile)) {
   expandline();
   lineno++;
   srcptr=srcline;
   if(suppress)suppressline(); else processline();
 }
 fclose(srcfile);
 if(suppress) {
   fprintf(stderr,"improperly nested IF statements in %s",curname);
   errors++;
   suppress=0;
 }
 lineno=oldno;
 strcpy(curname,oldname); 
}

main(int argc,char *argv[])
{
 char c;
 getoptions(argc,argv);
 pass=1;
 errors=0;
 generating=0;
 terminate=0;
 processfile(srcname);
 if(errors) {
  fprintf(stderr,"%d Pass 1 Errors, Continue?",errors);
  c=getchar();
  if(c=='n'||c=='N') exit(3);
 } 
 pass=2;
 loccounter=0;
 errors=0;
 generating=0;
 terminate=0;
 if(listing&&((listfile=fopen(listname,"w"))==0)) {
  fprintf(stderr,"Cannot open list file"); 
  exit(4);
 }
 if((objfile=fopen(objname,outmode?"w":"wb"))==0) {
  fprintf(stderr,"Cannot write object file\n");
  exit(4);
 }
 processfile(srcname);
 fprintf(stderr,"%d Pass 2 errors.\n",errors);
 if(listing) {
  fprintf(listfile,"%d Pass 2 errors.\n",errors);
  outsymtable();
  fclose(listfile);
 }
 if(outmode){
  flushhex();
  fprintf(objfile,"S9030000FC\n");
 } 
 fclose(objfile); 
}
     