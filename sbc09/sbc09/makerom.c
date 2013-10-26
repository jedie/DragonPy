/* makerom.c 
   Read standard input as S-records and build ROM image file v09.rom
   ROM starts at 0x8000 and is 32K.
*/

#include <stdio.h>
#include <stdlib.h>

static int sum,charindex;
unsigned char mem[0x8000];
char linebuf[130];

hexerr()
{
 fprintf(stderr,"Illegal character in hex number\n");
 exit(1);
}

int gethex()
{
 int c;
 c=linebuf[charindex++];
 if(c<'0')hexerr();
 if(c>'9') if(c<'A')hexerr();else c-=7;
 c-='0';
 return c;
}

int getbyte() 
{
 int b;
 b=gethex();
 b=b*16+gethex();
 sum=(sum+b)&0xff;
 return b;
}

main()
{
 FILE *romfile;
 unsigned int i,length,addr;
 for(i=0;i<0x8000;i++)mem[i]=0xff; /*set unused locations to FF */
 for(;;) {
  if(fgets(linebuf,128,stdin)==NULL)break;
  if(strlen(linebuf))linebuf[strlen(linebuf)]=0;
  if(linebuf[0]=='S'&&linebuf[1]=='1') {
   sum=0;charindex=2;
   length=getbyte();
   if(length<3) {
    fprintf(stderr,"Illegal length in data record\n");
    exit(1);
   }
   addr=getbyte();
   addr=(addr<<8)+getbyte();
   if((long)addr+length-3>0x10000||addr<0x8000) {
    fprintf(stderr,"Address 0x%x out of range\n",addr);
    exit(1);
   }
   for(i=0;i!=length-3;i++)mem[addr-0x8000+i]=getbyte();
   getbyte();
   if(sum!=0xff) {
    fprintf(stderr,"Checksum error\n");
    exit(1);
   }  
  }
 }
 romfile=fopen("v09.rom","wb");
 if(!romfile) {
  fprintf(stderr,"Cannot create file v09.rom\n");
  exit(1);
 }
 fwrite(mem,0x8000,1,romfile);
 fclose(romfile);
 exit(0);
}
