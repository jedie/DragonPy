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

#include<stdio.h>
#include<stdlib.h>
#include<ctype.h>
#include<signal.h>
#include<sys/time.h>

#include <unistd.h>
#include <fcntl.h>

#ifdef USE_TERMIOS
#include <termios.h>
#endif

#define engine extern
#include "v09.h"

int tflags;
struct termios termsetting;

int xmstat; /* 0= no XMODEM transfer, 1=send, 2=receiver */
unsigned char xmbuf[132];
int xidx;
int acknak;
int rcvdnak;
int blocknum;


FILE *logfile;
FILE *infile;
FILE *xfile;

int char_input(void)
{
 int c,w,sum;
 if(!xmstat) {
  if(infile) {
    c=getc(infile);
    if(c==EOF) {
     fclose(infile);
     infile=0;
     return char_input();
    }
    if(c=='\n')c='\r';
    return c; 
  } else   
  return getchar();
 }else if(xmstat==1) {
  if(xidx) {
   c=xmbuf[xidx++];
   if(xidx==132){xidx=0;rcvdnak=EOF;acknak=6;}
  }else{
   if(acknak==21&&rcvdnak==21||acknak==6&&rcvdnak==6) {
    rcvdnak=0;
    memset(xmbuf,0,132);
    w=fread(xmbuf+3,1,128,xfile);
    if(w) {
      printf("Block %3d transmitted, ",blocknum);   
      xmbuf[0]=1;
      xmbuf[1]=blocknum;
      xmbuf[2]=255-blocknum;
      blocknum=(blocknum+1)&255;
      sum=0;for(w=3;w<131;w++)sum=(sum+xmbuf[w])&255;
      xmbuf[131]=sum;
      acknak=6;
      c=1;
      xidx=1;
    }else {
      printf("EOT transmitted, ");
      acknak=4;
      c=4;
    }    
   }else if (rcvdnak==21) {
    rcvdnak=0;
    printf("Block %3d retransmitted, ",xmbuf[1]);
    c=xmbuf[xidx++];   /*retransmit the same block */
   }
   else c=EOF;
  }
  return c;
 }else{
  if(acknak==4){c=6;acknak=0;fclose(xfile);xfile=0;xmstat=0;}
  else if(acknak) {c=acknak;acknak=0;}else c=EOF;
  if(c==6)printf("ACK\n");
  if(c==21)printf("NAK\n");
  return c;
 }
}

int do_input(a) 
{
 static int c,f=EOF;
 if(a==0) {
  if(f==EOF) f=char_input();
  if(f!=EOF)c=f;
  return 2+(f!=EOF);
 }else if(a==1) { /*data port*/
  if(f==EOF) f=char_input();
  if(f!=EOF){c=f;f=EOF;}
  return c;
 }
}


void do_output(int a,int c)
{
 int i,sum;
 if(a==1) { /* ACIA data port,ignore address */
  if(!xmstat) {
   if(logfile&&c!=127&&(c>=' '||c=='\n'))putc(c,logfile);  
   putchar(c);fflush(stdout);
  }else if (xmstat==1) {
   rcvdnak=c;
   if(c==6&&acknak==4) {fclose(xfile);xfile=0;xmstat=0;}
   if(c==6)printf("ACK\n");
   if(c==21)printf("NAK\n");
   if(c==24){printf("CAN\n");
             fclose(xfile);xmstat=0;xfile=0;
            } 
  }else{
   if(xidx==0&&c==4) {
    acknak=4;
    printf("EOT received, ");
   }
   xmbuf[xidx++]=c;
   if(xidx==132) {
    sum=0;for(i=3;i<131;i++)sum=(sum+xmbuf[i])&255;
    if(xmbuf[0]==1&&xmbuf[1]==255-xmbuf[2]&&sum==xmbuf[131]) acknak=6;
    else acknak=21;
    printf("Block %3d received, ",xmbuf[1]);
    if(blocknum==xmbuf[1]) {
     blocknum=(blocknum+1)&255;
     fwrite(xmbuf+3,1,128,xfile);
    } 
    xidx=0;
   }
  } 
 }
}

void restore_term(void)
{
 tcsetattr(0,TCSAFLUSH,&termsetting);
 fcntl(0,F_SETFL,tflags);
 signal(SIGALRM,SIG_IGN);
}

void do_exit(void)
{
 restore_term();
 exit(0);
}


void do_escape(void)
{
 char s[80];
 restore_term();
 printf("v09>");fgets(s,80,stdin);
 if(s[0])s[strlen(s)-1]=0; 
 switch(toupper(s[0])) {
  case 'L': if(logfile)fclose(logfile);
            logfile=0;
            if(s[1]) {
              logfile=fopen(s+1,"w");
            } 
            break;
  case 'S': if(infile)fclose(infile);
  	    infile=0;
  	    if(s[1]) {
  	       infile=fopen(s+1,"r");
  	    }
  	    break;			
  case 'X': if(!xmstat)do_exit();else {
              xmstat=0;
              fclose(xfile);
              xfile=0;
            }break;
  case 'U': if(xfile)fclose(xfile);
  	    xfile=0;
  	    if(s[1]) {
  	       xfile=fopen(s+1,"rb");
  	    }
  	    if(xfile)xmstat=1;else xmstat=0;
  	    xidx=0;
  	    acknak=21;
  	    rcvdnak=EOF;
  	    blocknum=1;
  	    break; 
  case 'D': if(xfile)fclose(xfile);
  	    xfile=0;
  	    if(s[1]) {
  	       xfile=fopen(s+1,"wb");
  	    }
  	    if(xfile)xmstat=2;else xmstat=0;
  	    xidx=0;
  	    acknak=21;
  	    blocknum=1;
  	    break;
  case 'R': pcreg=(mem[0xfffe]<<8)+mem[0xffff];
 }
 if(!tracing)attention=0;
 escape=0;
 set_term(escchar);
}

void timehandler(int sig)
{
 attention=1;irq=2;signal(SIGALRM,timehandler);
}


void handler(int sig)
{
 escape=1;attention=1;
}
 
void set_term(char c)
{
 struct termios newterm;
 struct itimerval timercontrol;
 signal(SIGQUIT,SIG_IGN);
 signal(SIGTSTP,SIG_IGN);
 signal(SIGINT,handler);
 tcgetattr(0,&termsetting);
 newterm=termsetting;
 newterm.c_iflag=newterm.c_iflag&~INLCR&~ICRNL;
 newterm.c_lflag=newterm.c_lflag&~ECHO&~ICANON;
 newterm.c_cc[VTIME]=0;
 newterm.c_cc[VMIN]=1;
 newterm.c_cc[VINTR]=escchar; 
 tcsetattr(0,TCSAFLUSH,&newterm);
 tflags=fcntl(0,F_GETFL,0);
 fcntl(0,F_SETFL,tflags|O_NDELAY); /* Make input from stdin non-blocking */
 signal(SIGALRM,timehandler);
 timercontrol.it_interval.tv_sec=0;
 timercontrol.it_interval.tv_usec=20000;
 timercontrol.it_value.tv_sec=0;
 timercontrol.it_value.tv_usec=20000;
 setitimer(ITIMER_REAL,&timercontrol,NULL);
}
