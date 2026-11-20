extern char *malloc(), *realloc();

# line 21 "drsny.y"
#include "rgtrans.h"
#include <stddef.h>
#include <string.h>
#include <stdio.h>


char vector[VECTORSIZE];
char hvector[VECTORSIZE];
char cvector[VECTORSIZE];
char invector[VECTORSIZE];
char string[STRINGSIZE];
char nstring[STRINGSIZE];
char nnstring[STRINGSIZE];
char *newstring3;
char dum[512];
char dummy[512];
char dummy1[512];
char dummy2[512];
extern int kaisuucount1;
extern int hcount1;
extern int bodycount;
extern char origstring[];
extern int attributecount;
int errorInfo=0;
int glovalnumber =0;
int rulechecknumber1=0;
int rulechecknumber2=0;
int kanmachecknumber=0;
extern int kaigyounumber;
FILE *priout;

# line 52 "drsny.y"
typedef union  {
  char string11[512];
  char *string12;
  char *string13;
  char string14[512];
} YYSTYPE;
# define LP 257
# define RP 258
# define BBP 259
# define DIP 260
# define MP 261
# define OPOP 262
# define OP 263
# define EP 264
# define ANDP 265
# define MIP 266
# define NP 267
# define KLP 268
# define KRP 269
# define BP 270
# define NL 271
# define IP 272
# define TRP 273
# define TLP 274
# define KName 275
# define Variable 276
# define Atom 277
# define HtermMaker 278
# define Some 279
# define Not 280
# define ZName 281
# define WK 282
# define Mstring 283
# define REnd 284
# define DAR 285
# define DRR 286
# define SHMaker 287
# define BBB 288
# define DCR 289
# define CBRAtom 290
# define CKName 291
# define CBRVariable 292
# define RGP 293
# define LGP 294
# define CBRSHMaker 295
# define CBRHtermMaker 296
# define SAtom 297
# define CBRSAtom 298
# define CBREP 299
# define CBRLP 300
# define CBRRP 301
# define DG 302
# define GName 303
# define GSHMaker 304
# define GVariable 305
# define GHtermMaker 306
# define TOP 307
# define Number 308
# define NumberDomain 309
# define CBRNumber 310
# define CBRNumberDomain 311
# define LESS 312
# define GREATER 313
# define EQUAL 314
# define NOTEQUAL 315
# define SAME 316
# define DIFFERENT 317
#define yyclearin yychar = -1
#define yyerrok yyerrflag = 0
extern int yychar;
extern int yyerrflag;
#ifndef YYMAXDEPTH
#define YYMAXDEPTH 150
#endif
YYSTYPE yylval, yyval;
# define YYERRCODE 256

# line 2697 "drsny.y"

char string1[512],string2[512],string3[512];

/* mosi <str1,str2> nara str1 wo kaesi
   mosi str nara str wo wo kaesu*/

bunkatu(str,str1)
     char *str,*str1;{
       char str2[512];
       if(str[0]=='<'){
	 divid(str,str1,str2);
       }
       else{
	 strcpy(str1,str);
       }
     }

yyerror(s,t)
     char *s;
     char *t;
{
  fprintf(stderr,"%s",s);
  fprintf(stderr,"%s",":");
  fprintf(stderr,"%s"," ");
  fprintf(stderr,"%s","'");
  fprintf(stderr,"%s",t);
  fprintf(stderr,"%s\n","'");
  errorInfo = 10;
}

pri(string,priout)
     char *string;
     FILE *priout;
{
  fputs(string,priout);
  fputs("\n",priout);
}

/* from structure to Ingi Vector */

strToIngiVec(control,vector)
     cont_val *control;
     char *vector;
{
  val *ptr;
  int size=0;
  char dummy[4];
  memset(vector,0,VECTORSIZE);
  strcpy(vector,"{");
  sprintf(dummy,"%d",kaisuucount1);
  strcat(vector,dummy);
  strcat(vector,",");
  ptr = control -> top;
  while( ptr != control -> bottom){
    strcat(vector,"\"");
    strcat(vector,ptr -> name1);
    strcat(vector,"\"");
    strcat(vector,",");
    ptr = ptr -> next;
  }
  size = strlen(vector);
  vector[size-1] = '}';

}


/* from structure to Vector */

strToVec(control,vector)
     cont_val *control;
     char *vector;
{
  val *ptr;
  int size=0;
  char dummy[4];

  memset(vector,0,VECTORSIZE);
  strcpy(vector,"{");
  sprintf(dummy,"%d",kaisuucount1);
  strcat(vector,dummy);
  strcat(vector,",");
  ptr = control->top;
  while(ptr != control->bottom){
    strcat(vector,ptr->name2);
    strcat(vector,",");
    ptr = ptr->next;
  }
  size = strlen(vector);
  vector[size-1] = '}';
}



hstrToVec(control,vector)
     cont_ht *control;
     char *vector;
{
  ht *ptr;
  int size=0;
  char dummy[4];

  memset(vector,0,VECTORSIZE);
  strcpy(vector,"{");
  sprintf(dummy,"%d",hcount1);
  strcat(vector,dummy);
  strcat(vector,",");
  ptr = control->htop;
  while(ptr != control->hbottom){
    if(strcmp(ptr->hname3,"$") == 0){
      if(strcmp(ptr->hname1,ptr->hname2) == 0){
	fprintf(stderr,"%s","!trans-Illegal htermID difinition");
	fprintf(stderr,"%s",":line ");
	fprintf(stderr,"%d",kaigyounumber+1);
	fprintf(stderr,"%s"," '");
	fprintf(stderr,"%s",ptr->hname1);
	fprintf(stderr,"%s\n","'");
      }
    }
    strcat(vector,ptr->hname2);
    strcat(vector,",");
    ptr = ptr->hnext;
  }
  size = strlen(vector);
  vector[size-1] = '}';
}


strToVec2(control,vector)
     cont_cen *control;
     char *vector;
{
  cen *ptr;
  int size=0;
  char dummy[4];

  memset(vector,0,VECTORSIZE);
  strcpy(vector,"{");
  sprintf(dummy,"%d",kaisuucount1);
  strcat(vector,dummy);
  strcat(vector,",");
  ptr = control->ctop;
  while(ptr != control->cbottom){
    strcat(vector,ptr->cname2);
    strcat(vector,",");
    ptr = ptr->cnext;
  }
  size = strlen(vector);
  vector[size-1] = '}';
}


/* make HTerm */

htmake(string1,string2,newstring)
     char *string1;
     char *string2;
     char *newstring;
{
  char dummy[16];
  
  glovalnumber++;
  sprintf(dummy,"%d",glovalnumber);
  strcpy(newstring,"{{[],");
  strcat(newstring,string1);
  strcat(newstring,"},[");
  strcat(newstring,string2);
  strcat(newstring,"],");
  strcat(newstring,dummy);
  strcat(newstring,"}");
}


htmake1(string1,string2,newstring)  
     char *string1;
     char *string2;
     char *newstring;
{
  strcpy(newstring,"{{[],");
  strcat(newstring,string1);
  strcat(newstring,"},[");
  strcat(newstring,string2);
  strcat(newstring,"],@}");
}

htmake2(string1,string2,newstring)  
     char *string1;
     char *string2;
     char *newstring;
{ strcpy(newstring,"{{-,");
  strcat(newstring,string1);
  strcat(newstring,"},[");
  strcat(newstring,string2);
  strcat(newstring,"],@}");
}

htmake3(string1,string2,nstring)  
     char *string1;
     char *string2;
     char *nstring;
{
  char dummy[16];

  glovalnumber++;
  strcpy(nstring,"{{-,");
  strcat(nstring,string1);
  strcat(nstring,"},[");
  strcat(nstring,string2);
  strcat(nstring,"],");
  sprintf(dummy,"%d",glovalnumber);
  strcat(nstring,dummy);
  strcat(nstring,"}");
}

/* some */

someAtomMake(string1,string)
     char *string1;
     char *string;
{
  char dummy[16];
  int glnumber;
  int chnumber;

  glovalnumber++;
  strcpy(string,"{");
  strcat(string,string1);
  chnumber = glovalnumber ;
  glnumber = evencheck(chnumber);
  sprintf(dummy,"%d",glnumber);
  strcat(string,",");
  strcat(string,dummy);
  strcat(string,",[]}");
}

someAtomMake1(string1,string2,newstring)
     char *string1;
     char *string2;
     char *newstring;
{
  char dummy[16];
  int glnumber;
  int chnumber;

  glovalnumber++;
  chnumber = glovalnumber;
  glnumber = evencheck(chnumber);
  sprintf(dummy,"%d",glnumber);
  strcpy(newstring,"{");
  strcat(newstring,string1);
  strcat(newstring,",");
  strcat(newstring,dummy);
  strcat(newstring,",");
  strcat(newstring,string2);
  strcat(newstring,"}");
}


/*  some fuka */

numbertake(string1,nnstring,nstring)
     char *string1;
     char *nnstring;
     char *nstring;
{
  char cdummy1[16],*rt;
  int iti,icount=0;
  int glnumber;
  int chnumber;

  rt = strstr(string1,nnstring);

  if(rt == NULL)  return(1);
  else {
      iti = rt - string1;
      glovalnumber++;
      chnumber = glovalnumber;
      glnumber = evencheck(chnumber);
      sprintf(cdummy1,"%d",glnumber);
      while(icount != iti){
          *nstring = *string1;
          nstring++;
          string1++;
          icount++;
      }
      strcat(nstring,",");
      strcat(nstring,cdummy1);
      strcat(nstring,",");
      string1++;
      string1++;
      string1++;
      strcat(nstring,string1);
  }
}

/*
stmake2(string1,nstring)
     char *string1;
     char *nstring;
{
  char nstring1[512];
  char *nnstring = ",0,";

  memset(nstring,0,512);
  memset(nstring1,0,512);
  numbertake(string1,nnstring,nstring);
  while(strstr(nstring,nnstring) != NULL){
      numbertake(nstring,nnstring,nstring1);
      strcpy(nstring,nstring1);
  }

}
*/

stmake2(string1,nstring)
     char *string1;
     char *nstring;
{
  char nstring1[512];
  char *nnstring = ",0,";

  memset(nstring,0,512);
  memset(nstring1,0,512);
  switch(string1[0]){
  case '{':
    numbertake(string1,nnstring,nstring);
    while(strstr(nstring,nnstring) != NULL){
      numbertake(nstring,nnstring,nstring1);
      strcpy(nstring,nstring1);
    }
    break;
  case '<':
    numbertake(string1,nnstring,nstring);
    while(strstr(nstring,nnstring) != NULL){
      numbertake(nstring,nnstring,nstring1);
      strcpy(nstring,nstring1);
    }
    break;
  default:
    strcpy(nstring,string1);
    break;
  }
/*
  printf("stmake2 :\n");
  printf(" string1:: %s\n",string1);
  printf(" nstring: %s\n",nstring);
*/
}

/*
{
  strcpy(nstring,string1);
}
*/

stmake1(string1,nstring)
     char *string1;
     char *nstring;


{
  char nstring1[512];
  char *nnstring = ",0,";

  memset(nstring,0,512);
  memset(nstring1,0,512);
  switch(string1[0]){
  case '{':
    numbertake(string1,nnstring,nstring);
    break;
  case '<':
    numbertake(string1,nnstring,nstring);
    break;
  default:
    strcpy(nstring,string1);
    break;
  }
/*
  printf("stmake1 :\n");
  printf(" string1:: %s\n",string1);
  printf(" nstring: %s\n",nstring);
*/
}

/*
{
  strcpy(nstring,string1);
}
*/
/*   Scolem ID fuka   */



scoltake(string1,nnstring,nstring2)
     char *string1;
     char *nnstring;
     char *nstring2;
{
  char cdummy1[16],*rt;
  int iti,icount=0;

  rt = strstr(string1,nnstring);

  if(rt == NULL)  {
    strcpy(nstring2,string1);
  } 
  else {
    iti = rt - string1;
    glovalnumber++;
    sprintf(cdummy1,"%d",glovalnumber);
    while(icount != iti){
      *nstring2 = *string1;
      nstring2++;
      string1++;
      icount++;
    }
    strcat(nstring2,",");
    strcat(nstring2,cdummy1);
    string1++;
    string1++;
    strcat(nstring2,string1);
  }
}



scolmake(string1,newstring)
     char *string1;
     char *newstring;
{
  char *nstring1,*nstring2;
  char *nnstring = ",@";

  nstring2 = malloc(strlen(string1)+32);
  scoltake(string1,nnstring,nstring2);
  if(strstr(nstring2,nnstring) == NULL){
    strcpy(newstring,nstring2);
    free(nstring2);}
  else{
    nstring1 = malloc(strlen(string1)+32);
    while(strstr(nstring2,nnstring) != NULL){
      scoltake(nstring2,nnstring,nstring1);
      strcpy(newstring,nstring1);
      free(nstring1);
      free(nstring2);
    }
  }
/*
  printf("scolmake :\n");
  printf(" string1:: %s\n",string1);
  printf(" newstring: %s\n",newstring);
*/
}

/*   Atom  translator */
makeAtom(string1, string2)
     char *string1;
     char *string2;
{
  strcpy(string1,"{");
  strcat(string1,string2);
  strcat(string1,",0,[]}");
}

makeAtom1(string1, string2,string3)
     char *string1,*string2,*string3;
{
  strcpy(string1,"{");
  strcat(string1,string2);
  strcat(string1,",0,");
  strcat(string1,string3);
  strcat(string1,"}");
}

/*  CBR variable trans */

/*  variable / string2   */

cbrVaSmake(variable,string2,string)
     char *variable;
     char *string2;
     char *string;
{
  char nstring[512];
  someAtomMake(string2,nstring);
  AppendNet1(&vtable,variable,nstring,string);
  AppendCNet1(&ctable,variable,nstring);
}


/* variable / some string2 string3 */

cbrVaSmake3(variable,string2,string3,string)
     char *variable;
     char *string2;
     char *string3;
     char *string;
{
  char nstring[512];
  someAtomMake1(string2,string3,nstring);
  AppendNet1(&vtable,variable,nstring,string);
  AppendCNet1(&ctable,variable,nstring);
}

/* variable / some string2 string3 < string4> */

cbrVaSmake4(variable,string2,string3,string4,string)
     char *variable;
     char *string2;
     char *string3;
     char *string4;
     char *string;
{
  char nstring[512],str[512];

  memset(str,0,512);
  bunkatu(string4,str);

  AppendNet1(&vtable,variable,str,string);
  someAtomMake1(string2,string3,nstring);
  AppendCNet1(&ctable,variable,nstring);
}

/* variable / some string2 string3 < + > */

cbrVaSmake4T(variable,string2,string3,string)
     char *variable;
     char *string2;
     char *string3;
     char *string;
{
  char nstring[512];

  AppendNet1(&vtable,variable,"0",string); /* nstring -> "0" */
  someAtomMake1(string2,string3,nstring);
  AppendCNet1(&ctable,variable,nstring);
}

/* variable / string2  */

cbrVamake(variable,string2,string)
     char *variable;
     char *string2;
     char *string;
{
  char nstring[512];
  makeAtom(nstring,string2);
  AppendNet1(&vtable,variable,nstring,string);
  AppendCNet1(&ctable,variable,nstring);

}

/* variable / string2 < string3> */

cbrVamake2(variable,string2,string3,string)
     char *variable;
     char *string2;
     char *string3;
     char *string;
{
  char nstring[512],str[512];

  memset(str,0,512);
  bunkatu(string3,str);

  AppendNet1(&vtable,variable,str,string);
  makeAtom(nstring,string2);	
  AppendCNet1(&ctable,variable,nstring);
}

/* variable / string2 < + > */

cbrVamakeT(variable,string2,string)
     char *variable;
     char *string2;
     char *string;
{
  char nstring[512];

  AppendNet1(&vtable,variable,"0",string);
  makeAtom(nstring,string2);
  AppendCNet1(&ctable,variable,nstring);

}

/* variable */

cbrVamake3(variable,string)
     char *variable;
     char *string;
{
  AppendNet1(&vtable,variable,"0",string);
  AppendCNet1(&ctable,variable,"0");
}

/* variable / string2 string3  */

cbrVamake4(variable,string2,string3,string)
     char *variable;
     char *string2;
     char *string3;
     char *string;
{
  char *newstring;
  newstring = malloc(strlen(string2)+strlen(string3)+6);
  strcpy(newstring,"{");
  strcat(newstring,string2);
  strcat(newstring,",0,");
  strcat(newstring,string3);
  strcat(newstring,"}");
  AppendNet1(&vtable,variable,newstring,string);
  AppendCNet1(&ctable,variable,newstring);
  free(newstring);
}

/* variable / string2  string3 < string4> */

cbrVamake41(variable,string2,string3,string4,string)
     char *variable;
     char *string2;
     char *string3;
     char *string4;
     char *string;
{
  char *newstring,nstring[512],str[512];;

  memset(str,0,512);
  bunkatu(string4,str);

  AppendNet1(&vtable,variable,str,string);
  newstring = malloc(strlen(string2)+strlen(string3)+5);
  strcpy(newstring,"{");
  strcat(newstring,string2);
  strcat(newstring,",0,");
  strcat(newstring,string3);
  strcat(newstring,"}");
  AppendCNet1(&ctable,variable,newstring);
  free(newstring);
}

/* variable / string2 string3 < + > */

cbrVamake4T(variable,string2,string3,string)
     char *variable;
     char *string2;
     char *string3;
     char *string;
{
  char *newstring;

  AppendNet1(&vtable,variable,"0",string); 	/*newstring->"0"*/
  newstring = malloc(strlen(string2)+strlen(string3)+6);
  strcpy(newstring,"{");
  strcat(newstring,string2);
  strcat(newstring,",0,");
  strcat(newstring,string3);
  strcat(newstring,"}");
  AppendCNet1(&ctable,variable,newstring);
  free(newstring);
}

/*  Number  to Term   */

numbermake(number,numterm)
     char *number;
     char *numterm;
{
  strcpy(numterm,"{{");
  strcat(numterm,number);
  strcat(numterm,"},0,[]}");
}


/*  Number Domain to Term   */

numtake(numdomain,number1,number2)
     char *numdomain;
     char *number1;
     char *number2;
{
  int domainchangenum=0;
  while(*numdomain != '\0'){
    switch(*numdomain){
    case '[':
      *numdomain++;
      domainchangenum=1;
      break;
    case ']':
      *numdomain++;
      break;
    case '.':
      *numdomain++;
      domainchangenum++;
      break;
    default:
      switch(domainchangenum){
      case 1:
	*number1 = *numdomain;
	number1++;
	numdomain++;
	break;
      case 3:
	*number2 = *numdomain;
	number2++;
	numdomain++;
	break;
      }
      break;
    }
  }
}


numdomainmake(numdomain,numdoterm)
     char *numdomain;
     char *numdoterm;
{
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  strcpy(numdoterm,"{{{");
  numtake(numdomain,number1,number2);
  strcat(numdoterm,number1);
  strcat(numdoterm,"},{");
  strcat(numdoterm,number2);
  strcat(numdoterm,"}},0,[]}");
}




makenumber(numnum,numstr)
     char *numnum;
     char *numstr;
{
  strcpy(numstr,"{");
  strcat(numstr,numnum);
  strcat(numstr,"}");
}


makeNumdomain(numnum,numstr)
     char *numnum;
     char *numstr;
{
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  numtake(numnum,number1,number2);
  strcpy(numstr,"{{");
  strcat(numstr,number1);
  strcat(numstr,"},{");
  strcat(numstr,number2);
  strcat(numstr,"}}");
}

int evencheck( checknumber)
     int checknumber ;

{
  int dividnumber;
  int glonumber;
  glonumber = checknumber%2 ;
  if(glonumber == 0){
    glonumber = glovalnumber++;
    return(glovalnumber);}
  else{
    return(glovalnumber);
  }
}



int yyexca[] ={
-1, 1,
	0, -1,
	-2, 0,
-1, 46,
	258, 140,
	272, 140,
	-2, 0,
-1, 47,
	258, 140,
	272, 140,
	-2, 0,
-1, 98,
	258, 140,
	272, 140,
	-2, 0,
-1, 99,
	258, 140,
	272, 140,
	-2, 0,
-1, 100,
	258, 140,
	272, 140,
	-2, 0,
-1, 101,
	258, 140,
	272, 140,
	-2, 0,
-1, 102,
	258, 140,
	272, 140,
	-2, 0,
-1, 171,
	257, 154,
	-2, 237,
-1, 172,
	257, 158,
	-2, 196,
-1, 177,
	300, 163,
	-2, 206,
-1, 178,
	300, 167,
	-2, 210,
-1, 200,
	272, 144,
	301, 144,
	-2, 0,
-1, 201,
	272, 144,
	301, 144,
	-2, 0,
-1, 202,
	272, 144,
	301, 144,
	-2, 0,
-1, 229,
	258, 140,
	272, 140,
	-2, 0,
-1, 230,
	258, 140,
	272, 140,
	-2, 0,
-1, 231,
	258, 140,
	272, 140,
	-2, 0,
-1, 245,
	272, 144,
	301, 144,
	-2, 0,
-1, 246,
	272, 144,
	301, 144,
	-2, 0,
-1, 247,
	272, 144,
	301, 144,
	-2, 0,
-1, 248,
	257, 237,
	-2, 193,
-1, 249,
	300, 164,
	-2, 207,
-1, 250,
	257, 156,
	-2, 194,
-1, 257,
	300, 165,
	-2, 208,
-1, 333,
	257, 157,
	-2, 195,
-1, 334,
	300, 166,
	-2, 209,
-1, 336,
	257, 159,
	-2, 197,
-1, 346,
	300, 168,
	-2, 211,
-1, 423,
	257, 161,
	-2, 199,
-1, 424,
	257, 160,
	-2, 198,
-1, 428,
	300, 172,
	-2, 218,
-1, 429,
	300, 173,
	-2, 219,
-1, 430,
	300, 170,
	-2, 213,
-1, 432,
	300, 169,
	-2, 212,
-1, 487,
	300, 174,
	-2, 220,
-1, 488,
	300, 175,
	-2, 221,
-1, 489,
	257, 162,
	-2, 200,
-1, 491,
	300, 176,
	-2, 222,
-1, 492,
	300, 177,
	-2, 223,
-1, 496,
	300, 171,
	-2, 214,
-1, 549,
	300, 180,
	-2, 224,
-1, 550,
	300, 181,
	-2, 225,
-1, 578,
	300, 184,
	-2, 228,
-1, 579,
	300, 185,
	-2, 229,
-1, 582,
	300, 182,
	-2, 226,
-1, 583,
	300, 183,
	-2, 227,
-1, 595,
	300, 186,
	-2, 230,
-1, 596,
	300, 187,
	-2, 231,
	};
# define YYNPROD 246
# define YYLAST 1340
int yyact[]={

   191,   211,   179,   158,   270,   373,   591,   160,     4,   373,
   180,   396,   373,   231,   187,   188,    28,   373,   398,   590,
   589,   173,   128,   129,   245,     5,    24,   397,   588,   179,
   587,   193,   125,   373,   420,    24,    29,   180,   419,   586,
    51,   418,    24,   179,   161,   126,   377,    30,    31,   128,
   129,   180,    26,    28,   373,   256,   245,    24,   370,   281,
    24,   517,   376,   128,   129,   369,   179,    84,   126,   127,
   368,   367,    28,    29,   180,   366,   375,    24,    24,   365,
   247,   145,   125,   372,    30,    31,   128,   129,   246,   202,
   124,   124,    29,   179,   201,   126,   200,   374,   168,   167,
   113,   180,   138,    30,    31,   356,   177,   177,   348,    24,
   181,    57,    24,   128,   129,   551,   179,   174,   174,    58,
   171,   171,   596,   190,   180,   281,   205,   395,   124,   114,
   546,   545,   595,   162,   162,   127,   128,   129,   185,   213,
   544,   543,   213,   594,   192,    57,    24,   194,   125,    24,
   281,   347,   593,    58,   348,   179,   583,   193,   582,   505,
   127,   126,   179,   180,   168,   167,   528,   506,    37,   579,
   180,   249,   581,   125,   578,   128,   129,   124,    87,   128,
   129,   571,   128,   129,   363,   248,   126,   570,    38,   168,
   167,    24,   364,   267,    57,    91,   567,   124,    37,   124,
   124,   263,    58,   566,   128,   129,   550,   295,   192,   124,
   549,   194,   521,   520,   222,   296,   291,   224,    38,   179,
   527,   193,   303,   516,   515,   526,   179,   180,    60,    24,
    49,    37,   523,   522,   180,   315,   317,   492,   243,   128,
   129,   271,    24,    24,   491,   177,   128,   129,   329,   488,
   487,    38,   466,   271,   465,   497,   174,   205,   462,   171,
   346,    49,   188,    28,   260,   186,   336,   461,   189,   355,
   344,    51,   162,   429,   350,   124,   253,   252,   428,   282,
   352,   381,   380,    29,   493,   467,   471,    49,   121,   349,
   254,   298,   255,   455,    30,    31,    49,   387,   127,   147,
   382,    49,   378,   392,   394,   148,   383,   314,   343,   213,
   213,   125,   431,   142,    49,   149,    24,    24,    28,   362,
    85,   386,   179,    27,   126,   433,   335,   123,   122,   290,
   180,    49,   287,    26,    28,   143,    25,   214,    29,   294,
    13,     7,   128,   129,   144,   425,   321,   421,   432,    30,
    31,   254,   424,   255,    29,   426,   258,   437,    49,   322,
   124,   124,   124,   531,   439,    30,    31,   286,   435,   216,
   217,   218,   219,   220,   221,   177,   177,   501,   456,   458,
    28,   391,   353,   204,   481,   338,   174,   174,   236,   171,
   171,   473,   405,   404,   463,   183,   390,   142,   468,   267,
    29,   237,   162,   162,   440,   444,   445,    27,   184,   416,
   417,    30,    31,   263,   482,   371,    81,    26,    28,   143,
    25,    24,    28,    54,   337,   233,   313,   338,   144,    82,
   310,   234,   232,   399,   400,   401,   402,   403,    29,   438,
   498,   235,    29,   494,   124,   490,   541,   124,   124,    30,
    31,   411,   388,    30,    31,   542,    48,   539,   177,   414,
   177,   518,   410,   519,   412,   359,   540,   342,   415,   174,
   472,   174,   171,   413,   171,   157,   532,   389,   341,   524,
   340,   339,   213,   529,   324,   162,   323,   162,   504,    24,
    19,   507,   508,   448,   449,   450,   451,   452,   453,   357,
    27,   311,   409,   124,   124,   547,   253,   252,    83,   552,
    26,    28,   359,    25,   301,   142,   104,    64,   177,    40,
    19,   564,    19,    34,   358,    27,   312,    33,   135,   174,
   134,    29,   171,    78,    20,    26,   393,   143,    25,   214,
   568,   112,    30,    31,    16,   162,   144,   554,   555,    15,
   408,   109,    77,   136,   108,   281,    29,   124,   124,   132,
    95,   131,    94,   580,   104,   127,   177,    30,    31,   592,
   195,   216,   217,   218,   219,   220,   221,   174,   125,    11,
   171,   203,   407,     9,   133,    96,    45,   443,    73,   441,
    45,   126,    44,   162,   168,   167,   104,   442,   514,   513,
   512,   584,   585,   533,   534,   535,   536,   537,   538,   128,
   129,   275,   276,   277,   278,   279,   280,   242,   241,   511,
   510,   240,   239,   509,   480,   479,    26,    28,   250,    25,
   478,   104,   104,   281,   257,   104,   104,   558,   559,   560,
   561,   562,   563,   127,   264,   486,   238,    29,   266,    49,
    28,   477,   476,   299,   475,   225,   125,   485,    30,    31,
   104,   484,   293,   179,   262,   274,   301,   272,   227,   126,
    29,   180,   168,   167,   483,   273,   142,   460,   300,   454,
   226,    30,    31,   128,   129,   326,    27,   128,   129,   275,
   276,   277,   278,   279,   280,   107,    26,   212,   143,    25,
   214,   103,   325,   261,   244,   333,   334,   144,   111,   104,
   106,   110,    90,   105,   557,   104,   556,    29,   503,   502,
   351,   474,   447,   446,   354,   406,   361,   192,    30,    31,
   194,   360,   216,   217,   218,   219,   220,   221,   179,   302,
   193,   228,   199,   164,   198,    97,   180,   209,   197,   208,
   196,   268,   385,   176,    89,   569,    63,    62,   128,   129,
    42,   265,   259,   172,    28,   143,   170,   251,   206,   173,
    52,   328,   327,   182,   144,   565,   156,   179,   577,   178,
   576,   575,   168,   167,    29,   180,   574,   573,   572,   309,
   308,   307,   306,   423,   164,    30,    31,   128,   129,   305,
   304,   231,   230,   430,   176,   169,   229,   102,   101,   434,
   100,    99,   436,    98,   172,    28,   143,   170,    47,   164,
   173,    46,   115,    65,   269,   144,   459,   116,   179,   176,
   178,    50,   210,   168,   167,    29,   180,    32,    14,   172,
    28,   143,   170,     8,   470,   173,    30,    31,   128,   129,
   144,   457,    66,   179,    21,   178,     3,   164,   168,   167,
    29,   180,    12,    55,    18,    35,   166,   176,     6,    36,
     2,    30,    31,   128,   129,    43,    56,   172,    28,   143,
   170,   489,    41,   173,    17,   121,    92,    93,   144,   496,
     1,   179,   499,   178,   500,   127,   168,   167,    29,   180,
    59,    39,   137,   192,    41,    61,   194,    10,   125,    30,
    31,   128,   129,   130,   179,    80,   193,   192,    86,   118,
   194,   126,   180,   146,   123,   122,   215,   117,   179,    61,
   193,   553,    88,   175,   128,   129,   180,   163,   159,   128,
   129,   192,     0,     0,   194,   548,     0,   285,   128,   129,
   150,     0,   179,     0,   193,   192,   120,   120,   194,     0,
   180,     0,     0,    88,     0,     0,   179,   223,   193,   530,
     0,     0,   128,   129,   180,     0,    50,   192,     0,     0,
   194,     0,   192,   525,     0,   194,   128,   129,   179,     0,
   193,     0,     0,   179,     0,   193,   180,     0,     0,     0,
     0,   180,     0,     0,   192,   495,     0,   194,   128,   129,
   469,     0,     0,   128,   129,   179,     0,   193,   192,     0,
     0,   194,     0,   180,     0,     0,   283,   284,     0,   179,
     0,   193,   464,   297,     0,   128,   129,   180,     0,     0,
   192,     0,     0,   194,     0,   192,   427,     0,   194,   128,
   129,   179,     0,   193,     0,     0,   179,     0,   193,   180,
     0,     0,    50,     0,   180,   120,   120,   192,   422,     0,
   194,   128,   129,   384,     0,     0,   128,   129,   179,     0,
   193,   192,     0,   142,   194,     0,   180,   165,     0,     0,
     0,     0,   179,    27,   193,   379,     0,     0,   128,   129,
   180,     0,     0,    26,   316,   143,    25,    76,     0,   345,
    70,     0,   128,   129,   144,   192,     0,   142,   194,     0,
    27,     0,     0,     0,    29,     0,   179,    27,   193,     0,
    26,    28,    71,    25,   180,    30,    31,    26,   139,   143,
    25,    72,     0,   292,    70,     0,   128,   129,   144,   288,
   289,    29,     0,     0,    27,    79,     0,     0,    29,   140,
     0,     0,    30,    31,    26,    67,    71,    25,     0,    30,
    31,    22,     0,     0,     0,    72,     0,   119,   119,     0,
    22,     0,     0,     0,     0,    29,     0,    53,     0,     0,
     0,   141,     0,   330,   331,   332,    30,    31,     0,     0,
     0,     0,    68,    23,     0,    74,   151,   152,   153,   154,
   155,     0,    23,     0,     0,   207,     0,     0,     0,     0,
     0,     0,    68,    68,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,    69,     0,     0,    75,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,    69,    69,     0,    68,     0,     0,
     0,     0,     0,     0,   207,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,   119,   119,     0,    69,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,    53,   318,   319,   320 };
int yypact[]={

  -277, -1000,    55, -1000,   310,   306,    51,   276,   271,   213,
   261,   234, -1000,   254,   250,  -109,   213,   245, -1000,   498,
   234,   318,   564,   561,   381,  -205,   510,   350, -1000, -1000,
 -1000, -1000,   150,  -179,  -109,   -46, -1000,   495,   494,   243,
 -1000, -1000,   888,   314, -1000,   234,   277,   277, -1000,   139,
 -1000,   381,    41, -1000,  -179,   -96, -1000,   492,   450,   -79,
 -1000, -1000,   888,   888, -1000,   301, -1000,   482,   556,   554,
   553, -1000, -1000, -1000,   551,   550,   443,   449,   446,   437,
   282,   444,   441, -1000,   381,  -205,  -145, -1000, -1000,   629,
   629, -1000,   300,   269,   861,    23, -1000,   854,   277,   277,
   277,   277,   277,   517,   200,   601,   601,   514,   118, -1000,
   -14,   -71, -1000,   381, -1000,   489, -1000,   481,   479,  -204,
  -206,  -211, -1000, -1000,    90,  -288,   508,  -247, -1000, -1000,
   488,   420,    23, -1000,   420,    23, -1000,   396, -1000,   478,
   549,   545,   544, -1000, -1000,   148,   149, -1000,   111, -1000,
 -1000,   388,   364,   363,   360,   359,    23,   440, -1000, -1000,
 -1000, -1000, -1000, -1000,  -244,  -212,  -220, -1000, -1000, -1000,
   373,   381,   507,     0, -1000, -1000,  -224,    63,   502, -1000,
 -1000, -1000,    23,   436,   397, -1000,  -205,   381,   501,   230,
 -1000,   381,  -288,   491,    61, -1000,   377,    23,    32,    32,
    76,    76,    76,    36,   836,    46,   -64, -1000,   377,    23,
   394, -1000,   476, -1000,   141, -1000,   543,   542,   535,   534,
   533,   532,   146,   242,   142,    23, -1000,   827,   141,   277,
   277,   277, -1000, -1000,    69, -1000,   204,   202,   432, -1000,
   415,   513,   512, -1000,   601,    76,    76,    76,   381,    33,
 -1000,   145,   199,   198,   196,   185,   373,    15,   802,  -128,
 -1000,   -14,   -71,   381, -1000,   103, -1000,   381,  -174,   240,
 -1000, -1000,   468,   463,  -106,  -221,  -225,  -229,  -230,  -235,
  -242,  -276,   131, -1000, -1000,  -218,  -202,  -223,  -239,  -255,
   788,   -12,   -13,     7,   766,    28,  -288,   193,   112,    23,
 -1000,   259,    57, -1000,  -261,  -261,  -261,  -261,  -261,  -261,
 -1000,    23, -1000, -1000,   108, -1000,   462, -1000,   324,   292,
   244,   180,   169, -1000, -1000,   186,   181,    23,    23, -1000,
  -260,  -263,  -267, -1000,     7,   761,   381,  -205,    68, -1000,
 -1000, -1000, -1000,   739,   -16,   -21,    19,  -288,    35, -1000,
 -1000, -1000,   381,  -205, -1000,   381,  -288,    23, -1000,   299,
  -197,  -197, -1000,   460,   459,  -261,  -261,  -261,  -261,  -261,
  -261, -1000,   409,     2,   563,   538, -1000,   407,   -27,   -36,
 -1000, -1000,   725,   -40,   -42,    -8,   703,    -7,    23, -1000,
 -1000,   107, -1000,   458, -1000,   382, -1000, -1000,   373,   380,
   379,   358,   353,   352,   100, -1000,   141,   404, -1000,   391,
 -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000,   387,   375,
 -1000,   -44,   -45, -1000,   381,   163,   -50,   -57, -1000, -1000,
    -9,   698,   -38,   158, -1000,   381, -1000,   381,    93, -1000,
 -1000,   456,   455,  -131, -1000, -1000,  -197,  -197,   351,   348,
   347,   328,   327,   326,   -72,  -238, -1000,   601, -1000,   601,
   -83, -1000, -1000,   -61,   -62, -1000, -1000,   676,   -69,   -74,
  -127,   662,    79, -1000,    57,  -261,  -261,  -261,  -261,  -261,
  -261, -1000, -1000,   179,   168,  -155,  -165, -1000, -1000, -1000,
 -1000, -1000, -1000,   638,   -84,   -88,  -178,   624, -1000, -1000,
 -1000, -1000,  -197,  -197, -1000,   453,   451, -1000, -1000,  -261,
  -261,  -261,  -261,  -261,  -261, -1000, -1000,   487, -1000, -1000,
 -1000, -1000, -1000, -1000,   -91,   -98, -1000, -1000,   448,  -107,
  -113, -1000, -1000,   530,   529,   528,   523,   522,   520, -1000,
 -1000, -1000, -1000, -1000, -1000, -1000, -1000,  -120,  -125, -1000,
 -1000,  -135,  -136,  -138, -1000, -1000,  -197,  -197,  -262,  -271,
  -273,  -281,  -282,  -295, -1000,   601, -1000, -1000,  -142,  -151,
 -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000,
  -162,  -172, -1000, -1000, -1000, -1000, -1000, -1000, -1000, -1000,
 -1000, -1000, -1000, -1000, -1000, -1000, -1000 };
int yypgo[]={

     0,     7,   938,   127,    27,   937,    11,   933,     3,  1107,
   456,   926,     4,    81,   823,   923,   852,     1,   822,   827,
    44,   947,   915,   824,   907,   854,   832,   902,   864,   884,
   869,   876,  1159,   805,  1191,    14,     0,  1087,   866,   890,
   870,   868,   862,   856,   843,   838,   837,   865,   863 };
int yyr1[]={

     0,    39,    39,    43,    43,    24,    24,    25,    25,    25,
    25,    25,    25,    25,    25,    40,    40,    41,    41,    42,
    42,    44,    44,    45,    45,    46,    46,    29,    29,    47,
    47,    48,    48,    28,    28,    28,    28,    30,    30,    30,
    30,    30,    30,    30,    30,    31,    31,    31,    31,    31,
    31,    14,    14,    18,    18,    18,    27,    27,    27,    27,
    26,    26,    26,    26,    23,    23,    23,    23,    23,    23,
    23,    23,    23,    23,    23,    23,    23,    23,    13,    15,
    15,    15,    15,    15,    15,    15,    15,    16,    16,    16,
    16,    16,    16,    16,    16,    16,    19,    19,    19,    19,
    19,    19,    19,    19,    19,     1,     1,     1,     1,     1,
     1,     1,     1,     1,    20,    20,    20,    20,    20,    20,
    20,    20,    20,    34,    38,    17,    17,    17,    11,    11,
    11,    11,    11,    11,    12,    12,    12,    12,    12,    12,
     9,     9,     9,     9,    21,    21,    21,    21,    21,    21,
    21,     8,     8,     8,    32,    32,    32,    32,    32,    32,
    32,    32,    32,    37,    37,    37,    37,    37,    37,    37,
    37,    37,    37,    37,    37,    37,    37,    37,    37,    37,
    37,    37,    37,    37,    37,    37,    37,    37,     2,     2,
     3,     3,     4,     4,     4,     4,     4,     4,     4,     4,
     4,     4,     4,     4,     5,     5,     6,     6,     6,     6,
     6,     6,     6,     6,     6,     6,     6,     6,     7,     7,
     7,     7,     7,     7,     7,     7,     7,     7,     7,     7,
     7,     7,    22,    22,    22,    22,    10,    33,    35,    35,
    35,    35,    36,    36,    36,    36 };
int yyr2[]={

     0,     6,     2,     2,     4,     7,     9,     9,     9,    13,
    13,    13,    13,    17,    17,     2,     4,     2,     4,     2,
     4,     7,     9,     7,     9,     7,     9,     3,     5,     3,
     5,     3,     5,    17,    13,    13,     9,    17,    13,    13,
     9,    17,    13,    13,     9,    17,    17,    13,    13,    13,
    13,     3,     7,     3,     7,     7,     3,     7,     7,    11,
     3,     7,     7,    11,     3,     7,     3,     7,     7,     5,
     9,     9,     7,    11,    11,     9,    13,    13,     3,     3,
     7,     5,     9,     3,     7,     5,     9,    13,    13,     9,
     9,    13,    13,     9,     3,     3,    13,    13,     9,     9,
    13,    13,     9,     3,     3,    13,    13,     9,     9,    13,
    13,     9,     3,     3,    13,    13,     9,     9,    13,    13,
     9,     3,     3,     5,     5,     3,     5,     3,    13,    13,
    13,    13,    13,    13,    13,    13,    13,    13,    13,    13,
     1,     7,     7,    11,     1,     7,     7,     9,     9,    11,
    13,     3,     3,     3,     3,     5,     5,     7,     3,     7,
     9,     9,    11,     3,     5,     5,     7,     3,     7,     9,
     9,    11,     9,     9,    11,    11,    11,    11,    13,    13,
    13,    13,    15,    15,    15,    15,    17,    17,     2,     2,
     3,     2,     3,     5,     5,     7,     3,     7,     9,     9,
    11,     7,     7,    11,     2,     2,     3,     5,     5,     7,
     3,     7,     9,     9,    11,     7,     7,    11,     9,     9,
    11,    11,    11,    11,    13,    13,    15,    15,    15,    15,
    17,    17,     7,    11,     7,    11,     7,     3,     3,     3,
     3,     3,     3,     3,     3,     3 };
int yychk[]={

 -1000,   -39,   -40,   -43,   285,   302,   -41,   286,   -44,   273,
   -24,   273,   -42,   289,   -45,   273,   273,   -29,   -28,   277,
   273,   -25,   -32,   -34,   -35,   279,   276,   266,   277,   297,
   308,   309,   -46,   273,   273,   -47,   -30,   277,   297,   -29,
   274,   -28,   262,   -25,   274,   272,   257,   257,   -10,   268,
   -33,   -35,   260,   -32,   273,   -48,   -31,   290,   298,   -47,
   274,   -30,   262,   262,   274,   -14,   -16,   277,   -32,   -34,
   256,   278,   287,   274,   -32,   -34,    -9,   275,   256,    -9,
   -22,   277,   290,   -10,   -35,   279,   -48,   274,   -31,   262,
   262,   274,   -14,   -14,   261,   259,   284,   263,   257,   257,
   257,   257,   257,   258,   272,   264,   264,   258,   272,   269,
   267,   267,   -10,   -35,   274,   -18,   -19,   298,   290,   -37,
   -38,   256,   296,   295,   -36,   279,   292,   266,   310,   311,
   -18,   261,   259,   284,   261,   259,   284,   -27,    -1,   277,
   -32,   -34,   256,   278,   287,   -13,   -15,   276,   282,   292,
   -16,    -9,    -9,    -9,    -9,    -9,   259,   275,    -8,    -2,
    -1,   -20,    -4,    -5,   256,   -37,   -38,   296,   295,   -33,
   279,   -35,   276,   282,    -6,    -7,   266,   -36,   292,   290,
   298,    -8,   259,   277,   290,    -4,   279,   -35,   276,   282,
    -6,   -36,   279,   292,   282,   -10,   261,   259,   263,   263,
   300,   300,   300,   -10,   293,   -36,   260,   -37,   261,   259,
   -26,   -17,   277,    -1,   280,   -11,   312,   313,   314,   315,
   316,   317,   -13,   -26,   -13,   259,   284,   272,   263,   257,
   257,   257,   284,   276,   282,   292,   277,   290,   258,   258,
   258,   258,   258,   -13,   264,   300,   300,   300,   -35,   -36,
   -10,   260,   277,   276,   290,   292,   279,   -10,   293,   260,
   -13,   267,   267,   -35,   -10,   260,   -10,   -36,   260,   -23,
   -12,   -20,   290,   298,   288,   312,   313,   314,   315,   316,
   317,   256,   -13,   -19,   -19,   -21,   291,   256,   -21,   -21,
   293,    -6,   307,   -10,   293,   -36,   279,   -23,   -13,   259,
   284,   272,   263,    -1,   257,   257,   257,   257,   257,   257,
   284,   259,   284,   284,   -13,    -1,   277,    -1,    -9,    -9,
    -9,   277,   290,   282,   282,   270,   270,   259,   259,    -8,
   -21,   -21,   -21,   -10,   -10,   293,   -35,   279,   282,   282,
   282,   282,   282,   293,    -6,   307,   -36,   279,   282,    -4,
    -6,   -10,   -35,   279,   -10,   -36,   279,   259,   284,   272,
   263,   263,   -20,   290,   298,   300,   300,   300,   300,   300,
   300,   284,   301,   272,   299,   299,   301,   301,    -6,   307,
   294,   294,   293,    -6,   307,   -10,   293,   -36,   259,   284,
   284,   -13,   -17,   277,   -17,    -3,    -6,    -4,   279,    -3,
    -3,    -3,    -3,    -3,   -13,   284,   263,   258,   258,   258,
   282,   282,   278,   287,   278,   287,   -13,   -13,   301,   301,
   301,    -6,   307,   -10,   -35,   277,    -6,   307,   294,   294,
   -10,   293,   -36,   290,   -10,   -35,   -10,   -36,   -13,   -12,
   -20,   290,   298,   288,   -20,   -20,   263,   263,    -3,    -3,
    -3,    -3,    -3,    -3,   270,   291,    -8,   288,    -8,   288,
   270,   294,   294,    -6,   307,   294,   294,   293,    -6,   307,
   -10,   293,   -13,   284,   263,   272,   272,   272,   272,   272,
   272,   284,    -1,   270,   270,   270,   270,   294,   294,   -10,
   282,   294,   294,   293,    -6,   307,   -10,   293,   282,   -10,
   -10,   284,   263,   263,   -20,   290,   298,   -20,   -20,   272,
   272,   272,   272,   272,   272,   296,   295,   299,    -8,    -8,
   296,   295,   294,   294,    -6,   307,   294,   294,   293,    -6,
   307,   284,   -17,    -3,    -3,    -3,    -3,    -3,    -3,   278,
   287,   278,   287,   296,   295,   296,   295,    -6,   307,   294,
   294,   293,    -6,   307,   -20,   -20,   263,   263,    -3,    -3,
    -3,    -3,    -3,    -3,    -8,   288,   294,   294,    -6,   307,
   294,   294,   258,   258,   258,   258,   258,   258,   294,   294,
    -6,   307,   294,   294,   -20,   -20,   301,   301,   301,   301,
   301,   301,    -8,   294,   294,   294,   294 };
int yydef[]={

     0,    -2,     0,     2,    15,     3,     0,    17,    16,     0,
     4,     0,     1,    19,    18,     0,     0,     0,    27,     0,
     0,     0,     0,     0,   154,     0,   158,     0,   238,   239,
   240,   241,    20,     0,     0,     0,    29,     0,     0,     0,
    21,    28,     0,     0,     5,     0,    -2,    -2,   156,     0,
   155,   237,     0,   123,     0,     0,    31,     0,     0,     0,
    23,    30,     0,     0,    22,     0,    51,   238,     0,     0,
     0,    94,    95,     6,     0,     0,     0,     0,     0,     0,
     0,     0,     0,   157,   159,     0,     0,    25,    32,     0,
     0,    24,     0,     0,     0,     0,    36,     0,    -2,    -2,
    -2,    -2,    -2,     7,     0,     0,     0,     8,     0,   236,
     0,     0,   161,   160,    26,     0,    53,   243,   242,     0,
     0,     0,   103,   104,   163,     0,   167,     0,   244,   245,
     0,     0,     0,    40,     0,     0,    44,     0,    56,   238,
     0,     0,     0,   112,   113,     0,    78,    79,     0,    83,
    52,     0,     0,     0,     0,     0,     0,     0,   141,   151,
   152,   153,   188,   189,     0,     0,     0,   121,   122,   192,
     0,    -2,    -2,     0,   204,   205,     0,    -2,    -2,   242,
   243,   142,     0,     0,     0,   232,     0,   237,   196,     0,
   234,   206,     0,   210,     0,   162,     0,     0,     0,     0,
    -2,    -2,    -2,   165,     0,   164,     0,   124,     0,     0,
     0,    60,   238,   125,     0,   127,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,    34,     0,     0,    -2,
    -2,    -2,    35,    81,     0,    85,     0,     0,    90,    89,
    93,     9,    10,    11,     0,    -2,    -2,    -2,    -2,    -2,
    -2,     0,     0,     0,     0,     0,     0,    -2,     0,     0,
    12,     0,     0,   193,   194,     0,   208,   207,     0,     0,
    64,    66,   242,   243,     0,     0,     0,     0,     0,     0,
     0,     0,     0,    54,    55,     0,     0,     0,     0,     0,
     0,     0,     0,   166,     0,   168,     0,     0,     0,     0,
    38,     0,     0,   126,     0,     0,     0,     0,     0,     0,
    39,     0,    42,    43,     0,    58,   238,    57,     0,     0,
     0,     0,     0,    80,    84,     0,     0,     0,     0,   143,
     0,     0,     0,    -2,    -2,     0,    -2,     0,     0,   201,
   202,   215,   216,     0,     0,     0,    -2,     0,     0,   233,
   235,   195,   197,     0,   209,   211,     0,     0,    47,     0,
     0,     0,    69,   242,   243,     0,     0,     0,     0,     0,
     0,    49,    99,     0,     0,     0,    98,   102,     0,     0,
   172,   173,     0,     0,     0,   170,     0,   169,     0,    48,
    50,     0,    62,   238,    61,     0,   190,   191,     0,     0,
     0,     0,     0,     0,     0,    33,     0,   108,   107,   111,
    82,    86,    87,    88,    91,    92,    13,    14,   120,   117,
   116,     0,     0,    -2,    -2,     0,     0,     0,    -2,    -2,
    -2,     0,    -2,     0,   199,   198,   213,   212,     0,    65,
    72,   242,   243,     0,    67,    68,     0,     0,     0,     0,
     0,     0,     0,     0,     0,     0,   145,     0,   146,     0,
     0,   176,   177,     0,     0,   174,   175,     0,     0,     0,
   171,     0,     0,    37,     0,     0,     0,     0,     0,     0,
     0,    41,    59,     0,     0,     0,     0,    -2,    -2,    -2,
   203,    -2,    -2,     0,     0,     0,    -2,     0,   217,   200,
   214,    45,     0,     0,    75,   242,   243,    70,    71,     0,
     0,     0,     0,     0,     0,    96,    97,     0,   148,   147,
   100,   101,   178,   179,     0,     0,   180,   181,     0,     0,
     0,    46,    63,     0,     0,     0,     0,     0,     0,   105,
   106,   109,   110,   118,   119,   114,   115,     0,     0,    -2,
    -2,     0,     0,     0,    73,    74,     0,     0,     0,     0,
     0,     0,     0,     0,   149,     0,   184,   185,     0,     0,
   182,   183,   128,   129,   130,   131,   132,   133,    -2,    -2,
     0,     0,    -2,    -2,    76,    77,   134,   135,   136,   137,
   138,   139,   150,   186,   187,    -2,    -2 };
typedef struct { char *t_name; int t_val; } yytoktype;
#ifndef YYDEBUG
#	define YYDEBUG	0	/* don't allow debugging */
#endif

#if YYDEBUG

yytoktype yytoks[] =
{
	"LP",	257,
	"RP",	258,
	"BBP",	259,
	"DIP",	260,
	"MP",	261,
	"OPOP",	262,
	"OP",	263,
	"EP",	264,
	"ANDP",	265,
	"MIP",	266,
	"NP",	267,
	"KLP",	268,
	"KRP",	269,
	"BP",	270,
	"NL",	271,
	"IP",	272,
	"TRP",	273,
	"TLP",	274,
	"KName",	275,
	"Variable",	276,
	"Atom",	277,
	"HtermMaker",	278,
	"Some",	279,
	"Not",	280,
	"ZName",	281,
	"WK",	282,
	"Mstring",	283,
	"REnd",	284,
	"DAR",	285,
	"DRR",	286,
	"SHMaker",	287,
	"BBB",	288,
	"DCR",	289,
	"CBRAtom",	290,
	"CKName",	291,
	"CBRVariable",	292,
	"RGP",	293,
	"LGP",	294,
	"CBRSHMaker",	295,
	"CBRHtermMaker",	296,
	"SAtom",	297,
	"CBRSAtom",	298,
	"CBREP",	299,
	"CBRLP",	300,
	"CBRRP",	301,
	"DG",	302,
	"GName",	303,
	"GSHMaker",	304,
	"GVariable",	305,
	"GHtermMaker",	306,
	"TOP",	307,
	"Number",	308,
	"NumberDomain",	309,
	"CBRNumber",	310,
	"CBRNumberDomain",	311,
	"LESS",	312,
	"GREATER",	313,
	"EQUAL",	314,
	"NOTEQUAL",	315,
	"SAME",	316,
	"DIFFERENT",	317,
	"-unknown-",	-1	/* ends search */
};

char * yyreds[] =
{
	"-no such reduction-",
	"RuleBase : DARAbsoluteRuleBase DRRRBRRuleBase DCRCBRRuleBase",
	"RuleBase : GoalData",
	"GoalData : DG",
	"GoalData : DG GoalList",
	"GoalList : TRP Goal TLP",
	"GoalList : GoalList TRP Goal TLP",
	"Goal : Predicate LP kaku RP",
	"Goal : MPredicate LP kaku RP",
	"Goal : Goal IP Predicate LP kaku RP",
	"Goal : Goal IP MPredicate LP kaku RP",
	"Goal : Predicate LP kaku RP BBP RuleEx",
	"Goal : MPredicate LP kaku RP BBP RuleEx",
	"Goal : Goal IP Predicate LP kaku RP BBP RuleEx",
	"Goal : Goal IP MPredicate LP kaku RP BBP RuleEx",
	"DARAbsoluteRuleBase : DAR",
	"DARAbsoluteRuleBase : DAR AbsoluteRuleBase",
	"DRRRBRRuleBase : DRR",
	"DRRRBRRuleBase : DRR RBRRuleBase",
	"DCRCBRRuleBase : DCR",
	"DCRCBRRuleBase : DCR CBRRuleBase",
	"AbsoluteRuleBase : TRP AbsoluteRuleL TLP",
	"AbsoluteRuleBase : AbsoluteRuleBase TRP AbsoluteRuleL TLP",
	"RBRRuleBase : TRP RBRRuleL TLP",
	"RBRRuleBase : RBRRuleBase TRP RBRRuleL TLP",
	"CBRRuleBase : TRP CBRRuleL TLP",
	"CBRRuleBase : CBRRuleBase TRP CBRRuleL TLP",
	"AbsoluteRuleL : AbsoluteRule",
	"AbsoluteRuleL : AbsoluteRuleL AbsoluteRule",
	"RBRRuleL : RBRRule",
	"RBRRuleL : RBRRuleL RBRRule",
	"CBRRuleL : CBRRule",
	"CBRRuleL : CBRRuleL CBRRule",
	"AbsoluteRule : Atom OPOP Head MP Body BBP RuleEx REnd",
	"AbsoluteRule : Atom OPOP Head MP Body REnd",
	"AbsoluteRule : Atom OPOP Head BBP RuleEx REnd",
	"AbsoluteRule : Atom OPOP Head REnd",
	"RBRRule : Atom OPOP Head MP RBody BBP RuleEx REnd",
	"RBRRule : Atom OPOP Head MP RBody REnd",
	"RBRRule : Atom OPOP Head BBP RuleEx REnd",
	"RBRRule : Atom OPOP Head REnd",
	"RBRRule : SAtom OPOP Head MP RBody BBP RuleEx REnd",
	"RBRRule : SAtom OPOP Head MP RBody REnd",
	"RBRRule : SAtom OPOP Head BBP RuleEx REnd",
	"RBRRule : SAtom OPOP Head REnd",
	"CBRRule : CBRAtom OPOP CHead MP CRBody BBP RuleEx REnd",
	"CBRRule : CBRSAtom OPOP CHead MP CRBody BBP RuleEx REnd",
	"CBRRule : CBRAtom OPOP CHead MP CRBody REnd",
	"CBRRule : CBRSAtom OPOP CHead MP CRBody REnd",
	"CBRRule : CBRAtom OPOP CHead BBP RuleEx REnd",
	"CBRRule : CBRSAtom OPOP CHead BBP RuleEx REnd",
	"Head : HHTerm",
	"Head : Atom OP HHTerm",
	"CHead : CHHTerm",
	"CHead : CBRSAtom OP CHHTerm",
	"CHead : CBRAtom OP CHHTerm",
	"Body : HTerm",
	"Body : Atom OP HTerm",
	"Body : Body IP HTerm",
	"Body : Body IP Atom OP HTerm",
	"RBody : RHTerm",
	"RBody : Atom OP RHTerm",
	"RBody : RBody IP RHTerm",
	"RBody : RBody IP Atom OP RHTerm",
	"CRBody : CBuiltin",
	"CRBody : CRBody IP CBuiltin",
	"CRBody : CHTerm",
	"CRBody : CBRAtom OP CHTerm",
	"CRBody : CBRSAtom OP CHTerm",
	"CRBody : BBB CHTerm",
	"CRBody : BBB CBRAtom OP CHTerm",
	"CRBody : BBB CBRSAtom OP CHTerm",
	"CRBody : CRBody IP CHTerm",
	"CRBody : CRBody IP CBRAtom OP CHTerm",
	"CRBody : CRBody IP CBRSAtom OP CHTerm",
	"CRBody : CRBody IP BBB CHTerm",
	"CRBody : CRBody IP BBB CBRAtom OP CHTerm",
	"CRBody : CRBody IP BBB CBRSAtom OP CHTerm",
	"RuleEx : Rulek",
	"Rulek : Variable",
	"Rulek : WK Atom WK",
	"Rulek : Rulek Variable",
	"Rulek : Rulek WK Atom WK",
	"Rulek : CBRVariable",
	"Rulek : WK CBRAtom WK",
	"Rulek : Rulek CBRVariable",
	"Rulek : Rulek WK CBRAtom WK",
	"HHTerm : Predicate LP kaku RP BP HtermMaker",
	"HHTerm : Predicate LP kaku RP BP SHMaker",
	"HHTerm : MPredicate LP kaku RP",
	"HHTerm : Predicate LP kaku RP",
	"HHTerm : error LP kaku RP BP HtermMaker",
	"HHTerm : error LP kaku RP BP SHMaker",
	"HHTerm : error LP kaku RP",
	"HHTerm : HtermMaker",
	"HHTerm : SHMaker",
	"CHHTerm : CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker",
	"CHHTerm : CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker",
	"CHHTerm : CMPredicate CBRLP Ckaku CBRRP",
	"CHHTerm : CPredicate CBRLP Ckaku CBRRP",
	"CHHTerm : error CBRLP Ckaku CBRRP BP CBRHtermMaker",
	"CHHTerm : error CBRLP Ckaku CBRRP BP CBRSHMaker",
	"CHHTerm : error CBRLP Ckaku CBRRP",
	"CHHTerm : CBRHtermMaker",
	"CHHTerm : CBRSHMaker",
	"HTerm : Predicate LP kaku RP BP HtermMaker",
	"HTerm : Predicate LP kaku RP BP SHMaker",
	"HTerm : MPredicate LP kaku RP",
	"HTerm : Predicate LP kaku RP",
	"HTerm : error LP kaku RP BP HtermMaker",
	"HTerm : error LP kaku RP BP SHMaker",
	"HTerm : error LP kaku RP",
	"HTerm : HtermMaker",
	"HTerm : SHMaker",
	"CHTerm : CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker",
	"CHTerm : CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker",
	"CHTerm : CMPredicate CBRLP Ckaku CBRRP",
	"CHTerm : CPredicate CBRLP Ckaku CBRRP",
	"CHTerm : error CBRLP Ckaku CBRRP BP CBRHtermMaker",
	"CHTerm : error CBRLP Ckaku CBRRP BP CBRSHMaker",
	"CHTerm : error CBRLP Ckaku CBRRP",
	"CHTerm : CBRHtermMaker",
	"CHTerm : CBRSHMaker",
	"MPredicate : MIP Predicate",
	"CMPredicate : MIP CPredicate",
	"RHTerm : HTerm",
	"RHTerm : Not HTerm",
	"RHTerm : Builtin",
	"Builtin : LESS LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"Builtin : GREATER LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"Builtin : EQUAL LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"Builtin : NOTEQUAL LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"Builtin : SAME LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"Builtin : DIFFERENT LP PTermWithoutLimit IP PTermWithoutLimit RP",
	"CBuiltin : LESS CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"CBuiltin : GREATER CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"CBuiltin : EQUAL CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"CBuiltin : NOTEQUAL CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"CBuiltin : SAME CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"CBuiltin : DIFFERENT CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP",
	"kaku : /* empty */",
	"kaku : KName EP Term",
	"kaku : error EP Term",
	"kaku : kaku IP KName EP Term",
	"Ckaku : /* empty */",
	"Ckaku : CKName CBREP Term",
	"Ckaku : error CBREP Term",
	"Ckaku : error CBREP BBB Term",
	"Ckaku : CKName CBREP BBB Term",
	"Ckaku : Ckaku IP CKName CBREP Term",
	"Ckaku : Ckaku IP CKName CBREP BBB Term",
	"Term : PTerm",
	"Term : HTerm",
	"Term : CHTerm",
	"Predicate : NAtom",
	"Predicate : Some Atoms",
	"Predicate : NAtom AttributeS",
	"Predicate : Some NAtom AttributeS",
	"Predicate : Variable",
	"Predicate : Variable DIP NAtom",
	"Predicate : Variable DIP Some NAtom",
	"Predicate : Variable DIP NAtom AttributeS",
	"Predicate : Variable DIP Some NAtom AttributeS",
	"CPredicate : CBRSSAtom",
	"CPredicate : Some CBRSSAtom",
	"CPredicate : CBRSSAtom AttributeS",
	"CPredicate : Some CBRSSAtom AttributeS",
	"CPredicate : CBRVariable",
	"CPredicate : CBRVariable DIP CBRSSAtom",
	"CPredicate : CBRVariable DIP Some CBRSSAtom",
	"CPredicate : CBRVariable DIP CBRSSAtom AttributeS",
	"CPredicate : CBRVariable DIP Some CBRSSAtom AttributeS",
	"CPredicate : CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRSSAtom RGP TOP LGP",
	"CPredicate : Some CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CPredicate : Some CBRSSAtom RGP TOP LGP",
	"CPredicate : CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRSSAtom AttributeS RGP TOP LGP",
	"CPredicate : Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CPredicate : Some CBRSSAtom AttributeS RGP TOP LGP",
	"CPredicate : CBRVariable DIP CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRVariable DIP CBRSSAtom RGP TOP LGP",
	"CPredicate : CBRVariable DIP Some CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRVariable DIP Some CBRSSAtom RGP TOP LGP",
	"CPredicate : CBRVariable DIP CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRVariable DIP CBRSSAtom AttributeS RGP TOP LGP",
	"CPredicate : CBRVariable DIP Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CPredicate : CBRVariable DIP Some CBRSSAtom AttributeS RGP TOP LGP",
	"PTerm : RBRPTerm",
	"PTerm : CBRPTerm",
	"PTermWithoutLimit : CBRPTermWithoutLimit",
	"PTermWithoutLimit : RBRPTerm",
	"RBRPTerm : Atoms",
	"RBRPTerm : Some NAtom",
	"RBRPTerm : NAtom AttributeS",
	"RBRPTerm : Some NAtom AttributeS",
	"RBRPTerm : Variable",
	"RBRPTerm : Variable DIP NAtom",
	"RBRPTerm : Variable DIP Some NAtom",
	"RBRPTerm : Variable DIP NAtom AttributeS",
	"RBRPTerm : Variable DIP Some NAtom AttributeS",
	"RBRPTerm : WK Atom WK",
	"RBRPTerm : WK Variable WK",
	"RBRPTerm : Variable DIP WK Atom WK",
	"CBRPTerm : CBRPTermWithoutLimit",
	"CBRPTerm : CBRPTermWithLimit",
	"CBRPTermWithoutLimit : CBRSSAtom",
	"CBRPTermWithoutLimit : Some CBRSSAtom",
	"CBRPTermWithoutLimit : CBRSSAtom AttributeS",
	"CBRPTermWithoutLimit : Some CBRSSAtom AttributeS",
	"CBRPTermWithoutLimit : CBRVariable",
	"CBRPTermWithoutLimit : CBRVariable DIP CBRSSAtom",
	"CBRPTermWithoutLimit : CBRVariable DIP Some CBRSSAtom",
	"CBRPTermWithoutLimit : CBRVariable DIP CBRSSAtom AttributeS",
	"CBRPTermWithoutLimit : CBRVariable DIP Some CBRSSAtom AttributeS",
	"CBRPTermWithoutLimit : WK CBRAtom WK",
	"CBRPTermWithoutLimit : WK CBRVariable WK",
	"CBRPTermWithoutLimit : CBRVariable DIP WK CBRAtom WK",
	"CBRPTermWithLimit : CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRSSAtom RGP TOP LGP",
	"CBRPTermWithLimit : Some CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : Some CBRSSAtom RGP TOP LGP",
	"CBRPTermWithLimit : CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRSSAtom AttributeS RGP TOP LGP",
	"CBRPTermWithLimit : CBRVariable DIP CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRVariable DIP CBRSSAtom RGP TOP LGP",
	"CBRPTermWithLimit : CBRVariable DIP Some CBRSSAtom RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRVariable DIP Some CBRSSAtom RGP TOP LGP",
	"CBRPTermWithLimit : CBRVariable DIP CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRVariable DIP CBRSSAtom AttributeS RGP TOP LGP",
	"CBRPTermWithLimit : CBRVariable DIP Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP",
	"CBRPTermWithLimit : CBRVariable DIP Some CBRSSAtom AttributeS RGP TOP LGP",
	"Attri : Atom NP RBRPTerm",
	"Attri : Attri IP Atom NP RBRPTerm",
	"Attri : CBRAtom NP CBRPTermWithoutLimit",
	"Attri : Attri IP CBRAtom NP CBRPTermWithoutLimit",
	"AttributeS : KLP Attri KRP",
	"Atoms : NAtom",
	"NAtom : Atom",
	"NAtom : SAtom",
	"NAtom : Number",
	"NAtom : NumberDomain",
	"CBRSSAtom : CBRAtom",
	"CBRSSAtom : CBRSAtom",
	"CBRSSAtom : CBRNumber",
	"CBRSSAtom : CBRNumberDomain",
};
#endif /* YYDEBUG */
#line 1 "urlbycpr"
#ifndef lint
static	char yaccpar_sccsid[] = "@(#)yaccpar	1.9 91/12/11 Copyr 1989 Sun Micro; JLE";
/* from SunOS4.0.3 @(#)yaccpar 1.6 88/02/08 SMI"; *//* from UCB 4.1 83/02/01 */
#endif

/*
** Skeleton parser driver for yacc output
*/

/*
** yacc user known macros and defines
*/
#define YYERROR		goto yyerrlab
#define YYACCEPT	{ free(yys); free(yyv); return(0); }
#define YYABORT		{ free(yys); free(yyv); return(1); }
#define YYBACKUP( newtoken, newvalue )\
{\
	if ( yychar >= 0 || ( yyr2[ yytmp ] >> 1 ) != 1 )\
	{\
		yyerror( "syntax error - cannot backup" );\
		goto yyerrlab;\
	}\
	yychar = newtoken;\
	yystate = *yyps;\
	yylval = newvalue;\
	goto yynewstate;\
}
#define YYRECOVERING()	(!!yyerrflag)
#ifndef YYDEBUG
#	define YYDEBUG	1	/* make debugging available */
#endif

/*
** user known globals
*/
int yydebug;			/* set to 1 to get debugging */

/*
** driver internal defines
*/
#define YYFLAG		(-1000)

/*
** static variables used by the parser
*/
static YYSTYPE *yyv;			/* value stack */
static int *yys;			/* state stack */

static YYSTYPE *yypv;			/* top of value stack */
static int *yyps;			/* top of state stack */

static int yystate;			/* current state */
static int yytmp;			/* extra var (lasts between blocks) */

int yynerrs;			/* number of errors */

int yyerrflag;			/* error recovery flag */
int yychar;			/* current input token number */


/*
** yyparse - return 0 if worked, 1 if syntax error not recovered from
*/
int
yyparse()
{
	register YYSTYPE *yypvt;	/* top of value stack for $vars */
	unsigned yymaxdepth = YYMAXDEPTH;

	/*
	** Initialize externals - yyparse may be called more than once
	*/
	yyv = (YYSTYPE*)malloc(yymaxdepth*sizeof(YYSTYPE));
	yys = (int*)malloc(yymaxdepth*sizeof(int));
	if (!yyv || !yys)
	{
		yyerror( "out of memory" );
		return(1);
	}
	yypv = &yyv[-1];
	yyps = &yys[-1];
	yystate = 0;
	yytmp = 0;
	yynerrs = 0;
	yyerrflag = 0;
	yychar = -1;

	goto yystack;
	{
		register YYSTYPE *yy_pv;	/* top of value stack */
		register int *yy_ps;		/* top of state stack */
		register int yy_state;		/* current state */
		register int  yy_n;		/* internal state number info */

		/*
		** get globals into registers.
		** branch to here only if YYBACKUP was called.
		*/
	yynewstate:
		yy_pv = yypv;
		yy_ps = yyps;
		yy_state = yystate;
		goto yy_newstate;

		/*
		** get globals into registers.
		** either we just started, or we just finished a reduction
		*/
	yystack:
		yy_pv = yypv;
		yy_ps = yyps;
		yy_state = yystate;

		/*
		** top of for (;;) loop while no reductions done
		*/
	yy_stack:
		/*
		** put a state and value onto the stacks
		*/
#if YYDEBUG
		/*
		** if debugging, look up token value in list of value vs.
		** name pairs.  0 and negative (-1) are special values.
		** Note: linear search is used since time is not a real
		** consideration while debugging.
		*/
		if ( yydebug )
		{
			register int yy_i;

			(void)printf( "State %d, token ", yy_state );
			if ( yychar == 0 )
				(void)printf( "end-of-file\n" );
			else if ( yychar < 0 )
				(void)printf( "-none-\n" );
			else
			{
				for ( yy_i = 0; yytoks[yy_i].t_val >= 0;
					yy_i++ )
				{
					if ( yytoks[yy_i].t_val == yychar )
						break;
				}
				(void)printf( "%s\n", yytoks[yy_i].t_name );
			}
		}
#endif /* YYDEBUG */
		if ( ++yy_ps >= &yys[ yymaxdepth ] )	/* room on stack? */
		{
			/*
			** reallocate and recover.  Note that pointers
			** have to be reset, or bad things will happen
			*/
			int yyps_index = (yy_ps - yys);
			int yypv_index = (yy_pv - yyv);
			int yypvt_index = (yypvt - yyv);
			yymaxdepth += YYMAXDEPTH;
			yyv = (YYSTYPE*)realloc((char*)yyv,
				yymaxdepth * sizeof(YYSTYPE));
			yys = (int*)realloc((char*)yys,
				yymaxdepth * sizeof(int));
			if (!yyv || !yys)
			{
				yyerror( "yacc stack overflow" );
				return(1);
			}
			yy_ps = yys + yyps_index;
			yy_pv = yyv + yypv_index;
			yypvt = yyv + yypvt_index;
		}
		*yy_ps = yy_state;
		*++yy_pv = yyval;

		/*
		** we have a new state - find out what to do
		*/
	yy_newstate:
		if ( ( yy_n = yypact[ yy_state ] ) <= YYFLAG )
			goto yydefault;		/* simple state */
#if YYDEBUG
		/*
		** if debugging, need to mark whether new token grabbed
		*/
		yytmp = yychar < 0;
#endif
# ifdef YYEUCCCOUNT
		if ( ( yychar < 0 ) && ( ( yychar = yyeuclex() ) < 0 ) )
# else
		if ( ( yychar < 0 ) && ( ( yychar = yylex() ) < 0 ) )
# endif
			yychar = 0;		/* reached EOF */
#if YYDEBUG
		if ( yydebug && yytmp )
		{
			register int yy_i;

			(void)printf( "Received token " );
			if ( yychar == 0 )
				(void)printf( "end-of-file\n" );
			else if ( yychar < 0 )
				(void)printf( "-none-\n" );
			else
			{
				for ( yy_i = 0; yytoks[yy_i].t_val >= 0;
					yy_i++ )
				{
					if ( yytoks[yy_i].t_val == yychar )
						break;
				}
				(void)printf( "%s\n", yytoks[yy_i].t_name );
			}
		}
#endif /* YYDEBUG */
		if ( ( ( yy_n += yychar ) < 0 ) || ( yy_n >= YYLAST ) )
			goto yydefault;
		if ( yychk[ yy_n = yyact[ yy_n ] ] == yychar )	/*valid shift*/
		{
			yychar = -1;
			yyval = yylval;
			yy_state = yy_n;
			if ( yyerrflag > 0 )
				yyerrflag--;
			goto yy_stack;
		}

	yydefault:
		if ( ( yy_n = yydef[ yy_state ] ) == -2 )
		{
#if YYDEBUG
			yytmp = yychar < 0;
#endif
# ifdef YYEUCCCOUNT
			if ( ( yychar < 0 ) && ( ( yychar = yyeuclex() ) < 0 ) )
# else
			if ( ( yychar < 0 ) && ( ( yychar = yylex() ) < 0 ) )
# endif
				yychar = 0;		/* reached EOF */
#if YYDEBUG
			if ( yydebug && yytmp )
			{
				register int yy_i;

				(void)printf( "Received token " );
				if ( yychar == 0 )
					(void)printf( "end-of-file\n" );
				else if ( yychar < 0 )
					(void)printf( "-none-\n" );
				else
				{
					for ( yy_i = 0;
						yytoks[yy_i].t_val >= 0;
						yy_i++ )
					{
						if ( yytoks[yy_i].t_val
							== yychar )
						{
							break;
						}
					}
					(void)printf( "%s\n", yytoks[yy_i].t_name );
				}
			}
#endif /* YYDEBUG */
			/*
			** look through exception table
			*/
			{
				register int *yyxi = yyexca;

				while ( ( *yyxi != -1 ) ||
					( yyxi[1] != yy_state ) )
				{
					yyxi += 2;
				}
				while ( ( *(yyxi += 2) >= 0 ) &&
					( *yyxi != yychar ) )
					;
				if ( ( yy_n = yyxi[1] ) < 0 )
					YYACCEPT;
			}
		}

		/*
		** check for syntax error
		*/
		if ( yy_n == 0 )	/* have an error */
		{
			/* no worry about speed here! */
			switch ( yyerrflag )
			{
			case 0:		/* new error */
				yyerror( "!trans-illegal syntax",yylval );
				goto skip_init;
			yyerrlab:
				/*
				** get globals into registers.
				** we have a user generated syntax type error
				*/
				yy_pv = yypv;
				yy_ps = yyps;
				yy_state = yystate;
				yynerrs++;
			skip_init:
			case 1:
			case 2:		/* incompletely recovered error */
					/* try again... */
				yyerrflag = 3;
				/*
				** find state where "error" is a legal
				** shift action
				*/
				while ( yy_ps >= yys )
				{
					yy_n = yypact[ *yy_ps ] + YYERRCODE;
					if ( yy_n >= 0 && yy_n < YYLAST &&
						yychk[yyact[yy_n]] == YYERRCODE)					{
						/*
						** simulate shift of "error"
						*/
						yy_state = yyact[ yy_n ];
						goto yy_stack;
					}
					/*
					** current state has no shift on
					** "error", pop stack
					*/
#if YYDEBUG
#	define _POP_ "Error recovery pops state %d, uncovers state %d\n"
					if ( yydebug )
						(void)printf( _POP_, *yy_ps,
							yy_ps[-1] );
#	undef _POP_
#endif
					yy_ps--;
					yy_pv--;
				}
				/*
				** there is no state on stack with "error" as
				** a valid shift.  give up.
				*/
				YYABORT;
			case 3:		/* no shift yet; eat a token */
#if YYDEBUG
				/*
				** if debugging, look up token in list of
				** pairs.  0 and negative shouldn't occur,
				** but since timing doesn't matter when
				** debugging, it doesn't hurt to leave the
				** tests here.
				*/
				if ( yydebug )
				{
					register int yy_i;

					(void)printf( "Error recovery discards " );
					if ( yychar == 0 )
						(void)printf( "token end-of-file\n" );
					else if ( yychar < 0 )
						(void)printf( "token -none-\n" );
					else
					{
						for ( yy_i = 0;
							yytoks[yy_i].t_val >= 0;
							yy_i++ )
						{
							if ( yytoks[yy_i].t_val
								== yychar )
							{
								break;
							}
						}
						(void)printf( "token %s\n",
							yytoks[yy_i].t_name );
					}
				}
#endif /* YYDEBUG */
				if ( yychar == 0 )	/* reached EOF. quit */
					YYABORT;
				yychar = -1;
				goto yy_newstate;
			}
		}/* end if ( yy_n == 0 ) */
		/*
		** reduction by production yy_n
		** put stack tops, etc. so things right after switch
		*/
#if YYDEBUG
		/*
		** if debugging, print the string that is the user's
		** specification of the reduction which is just about
		** to be done.
		*/
		if ( yydebug )
			(void)printf( "Reduce by (%d) \"%s\"\n",
				yy_n, yyreds[ yy_n ] );
#endif
		yytmp = yy_n;			/* value to switch over */
		yypvt = yy_pv;			/* $vars top of value stack */
		/*
		** Look in goto table for next state
		** Sorry about using yy_state here as temporary
		** register variable, but why not, if it works...
		** If yyr2[ yy_n ] doesn't have the low order bit
		** set, then there is no action to be done for
		** this reduction.  So, no saving & unsaving of
		** registers done.  The only difference between the
		** code just after the if and the body of the if is
		** the goto yy_stack in the body.  This way the test
		** can be made before the choice of what to do is needed.
		*/
		{
			/* length of production doubled with extra bit */
			register int yy_len = yyr2[ yy_n ];

			if ( !( yy_len & 01 ) )
			{
				yy_len >>= 1;
				yyval = ( yy_pv -= yy_len )[1];	/* $$ = $1 */
				yy_state = yypgo[ yy_n = yyr1[ yy_n ] ] +
					*( yy_ps -= yy_len ) + 1;
				if ( yy_state >= YYLAST ||
					yychk[ yy_state =
					yyact[ yy_state ] ] != -yy_n )
				{
					yy_state = yyact[ yypgo[ yy_n ] ];
				}
				goto yy_stack;
			}
			yy_len >>= 1;
			yyval = ( yy_pv -= yy_len )[1];	/* $$ = $1 */
			yy_state = yypgo[ yy_n = yyr1[ yy_n ] ] +
				*( yy_ps -= yy_len ) + 1;
			if ( yy_state >= YYLAST ||
				yychk[ yy_state = yyact[ yy_state ] ] != -yy_n )
			{
				yy_state = yyact[ yypgo[ yy_n ] ];
			}
		}
					/* save until reenter driver code */
		yystate = yy_state;
		yyps = yy_ps;
		yypv = yy_pv;
	}
	/*
	** code supplied by user is placed in this switch
	*/
	switch( yytmp )
	{
		
case 5:
# line 81 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 6:
# line 85 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 7:
# line 90 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  htmake1(yypvt[-3].string14,yypvt[-1].string12,newstring);
  strToIngiVec(&vtable,invector);
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+
			  sizeof("{\"{{[],},,[],}}")+1);
  strcpy(yyval.string13,"{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
} break;
case 8:
# line 123 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1(yypvt[-3].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-1].string12)+30);
  htmake3(nstring,yypvt[-1].string12,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+16);
  strcpy(yyval.string13,"{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  free(yypvt[-1].string12);
  free(newstring);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  kaisuucount1=0;
  hcount1=0;
} break;
case 9:
# line 156 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  htmake1(yypvt[-3].string14,yypvt[-1].string12,newstring);  
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+17);
  strcpy(yyval.string13,",{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
} break;
case 10:
# line 188 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1(yypvt[-3].string14,nstring);
  newstring = malloc(strlen(yypvt[-1].string12)+strlen(nstring)+30);
  htmake3(nstring,yypvt[-1].string12,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+17);
  strcpy(yyval.string13,",{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(newstring);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
} break;
case 11:
# line 221 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+13);
  htmake1(yypvt[-5].string14,yypvt[-3].string12,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+14);
  strcpy(yyval.string13,"{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-0].string12);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
} break;
case 12:
# line 256 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+30);
  htmake3(nstring,yypvt[-3].string12,string);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+14);
  strcpy(yyval.string13,"{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-0].string12);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
} break;
case 13:
# line 292 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+13);
  htmake1(yypvt[-5].string14,yypvt[-3].string12,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(yypvt[-0].string12)+
			  strlen(invector)+strlen(vector)+strlen(hvector)+15);
  strcpy(yyval.string13,",{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-0].string12);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
} break;
case 14:
# line 327 "drsny.y"
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+30);
  htmake3(nstring,yypvt[-3].string12,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(yypvt[-0].string12)+
			  strlen(invector)+strlen(vector)+strlen(hvector)+15);
  strcpy(yyval.string13,",{\"");
  strcat(yyval.string13,origstring);
  strcat(yyval.string13,"{{[],");
  strcat(yyval.string13,newstring);
  strcat(yyval.string13,"},");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,invector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  pri(yyval.string13,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(newstring);
  free(yypvt[-3].string12);
  free(yypvt[-0].string12);
  kaisuucount1=0;
  hcount1=0;
} break;
case 21:
# line 373 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 22:
# line 377 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 23:
# line 382 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 24:
# line 386 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 25:
# line 391 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 26:
# line 395 "drsny.y"
{
  AllDeleteSNet(&stable);
} break;
case 27:
# line 400 "drsny.y"
{ 
  pri(yypvt[-0].string13,priout);
  free(yypvt[-0].string13);
  rulechecknumber1=1;
} break;
case 28:
# line 406 "drsny.y"
{
  pri(",",priout);
  pri(yypvt[-0].string13,priout);
  free(yypvt[-0].string13);
} break;
case 29:
# line 413 "drsny.y"
{ 
  rulechecknumber2=1;
  if(rulechecknumber1==0){
    pri(yypvt[-0].string13,priout);
    free(yypvt[-0].string13);
  }
  else{
    pri(",",priout);
    pri(yypvt[-0].string13,priout);
    free(yypvt[-0].string13);
  }
} break;
case 30:
# line 426 "drsny.y"
{
  pri(",",priout);
  pri(yypvt[-0].string13,priout);
  free(yypvt[-0].string13);
} break;
case 31:
# line 433 "drsny.y"
{
  if(rulechecknumber2==0){
    pri(yypvt[-0].string13,priout);
    free(yypvt[-0].string13);
  }
  else{
    pri(",",priout);
    pri(yypvt[-0].string13,priout);
    free(yypvt[-0].string13);
  }
} break;
case 32:
# line 445 "drsny.y"
{
  pri(",",priout);
  pri(yypvt[-0].string13,priout);
  free(yypvt[-0].string13);
} break;
case 33:
# line 452 "drsny.y"
{
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-5].string12)+strlen(yypvt[-3].string13)+strlen(yypvt[-7].string11)+strlen(vector)
			  +strlen(hvector)+strlen(yypvt[-1].string12)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-7].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-5].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-5].string12);
  free(yypvt[-3].string13);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-7].string11);
} break;
case 34:
# line 481 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string13)+strlen(yypvt[-5].string11)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string13);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 35:
# line 507 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+strlen(yypvt[-5].string11)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 36:
# line 533 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-1].string12)+strlen(yypvt[-3].string11)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-3].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-3].string11);
} break;
case 37:
# line 557 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-5].string12)+strlen(yypvt[-7].string11)+strlen(yypvt[-3].string13)+strlen(vector)+
		    strlen(yypvt[-1].string12)+strlen(hvector) +16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-7].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-5].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-5].string12);
  free(yypvt[-3].string13);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-7].string11);
} break;
case 38:
# line 586 "drsny.y"
{
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-5].string11)+strlen(yypvt[-1].string13)+strlen(vector)+
    strlen(hvector) + 16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string13);
  strcat(yyval.string13,"]");
  strcat(yyval.string13,",");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string13);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 39:
# line 613 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-5].string11)+strlen(yypvt[-1].string12)+strlen(vector)+
			  strlen(hvector) +16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 40:
# line 639 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string11)+strlen(yypvt[-1].string12)+strlen(vector)+
			  strlen(hvector)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-3].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-3].string11);
} break;
case 41:
# line 662 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-7].string11)+strlen(yypvt[-5].string12)+strlen(yypvt[-3].string13)+strlen(vector)
		    +strlen(hvector)+strlen(yypvt[-1].string12)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-7].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-5].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-5].string12);
  free(yypvt[-3].string13);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-7].string11);
} break;
case 42:
# line 691 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-5].string11)+strlen(yypvt[-3].string12)+strlen(yypvt[-1].string13)+strlen(vector)
		    +strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string13);
  strcat(yyval.string13,"]");
  strcat(yyval.string13,",");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string13);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 43:
# line 718 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+strlen(vector)+strlen(yypvt[-5].string11)
		    +strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  free(yypvt[-3].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 44:
# line 744 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13= malloc(strlen(yypvt[-3].string11)+strlen(yypvt[-1].string12)+strlen(vector)+
			 strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-3].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-3].string11);
} break;
case 45:
# line 768 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-5].string12)+strlen(yypvt[-3].string13)+strlen(yypvt[-7].string11)+strlen(yypvt[-1].string12)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +17);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-7].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-5].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-5].string12);
  free(yypvt[-3].string13);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-7].string11);
} break;
case 46:
# line 802 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-5].string12)+strlen(yypvt[-3].string13)+strlen(yypvt[-1].string12)+strlen(yypvt[-7].string11)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +15);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-7].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-5].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-5].string12);
  free(yypvt[-3].string13);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-7].string11);
} break;
case 47:
# line 836 "drsny.y"
{ 
/*  printf("CBRAtom OPOP CHead MP CRBody REnd%s-%s-%s\n",$1,$3,$5);*/
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string13)+strlen(yypvt[-5].string11)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +17);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string13);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 48:
# line 868 "drsny.y"
{ 
/*  printf("CBRSAtom OPOP CHead MP CRBody REnd%s-%s-%s\n",$1,$3,$5);*/
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string13)+strlen(yypvt[-5].string11)+strlen(vector)
			  +strlen(vector)+strlen(hvector)+strlen(cvector)
			  +15);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string13);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string13);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 49:
# line 900 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+strlen(yypvt[-5].string11)+strlen(vector)
			  +strlen(hvector)+strlen(cvector)+17);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 50:
# line 930 "drsny.y"
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+strlen(yypvt[-5].string11)+strlen(vector)
			  +strlen(hvector)+strlen(cvector)+15);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,yypvt[-5].string11);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,yypvt[-3].string12);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,yypvt[-1].string12);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,",");
  strcat(yyval.string13,cvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",yypvt[-5].string11);
} break;
case 51:
# line 961 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  bodycount++;
} break;
case 52:
# line 968 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  bodycount++;
} break;
case 53:
# line 976 "drsny.y"
{ 
/*  printf("CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  bodycount++;
} break;
case 54:
# line 984 "drsny.y"
{ 
/*  printf("CBRSAtom OP CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  bodycount++;
} break;
case 55:
# line 992 "drsny.y"
{ 
/*  printf("CBRAtom OP CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  bodycount++;
} break;
case 56:
# line 1002 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,"}");
  free(yypvt[-0].string12);
} break;
case 57:
# line 1010 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,"}");
  free(yypvt[-0].string12);
} break;
case 58:
# line 1018 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-2].string13)+strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string13,yypvt[-2].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,"}");
  free(yypvt[-2].string13);
  free(yypvt[-0].string12);
} break;
case 59:
# line 1029 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-4].string13)+strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string13,yypvt[-4].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,"}");
  free(yypvt[-4].string13);
  free(yypvt[-0].string12);
} break;
case 60:
# line 1041 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string13,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 61:
# line 1047 "drsny.y"
{ yyval.string13 =malloc(strlen(yypvt[-0].string12) +1);
  strcpy(yyval.string13,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 62:
# line 1052 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-2].string13)+strlen(yypvt[-0].string12)+2);
  strcpy(yyval.string13,yypvt[-2].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  free(yypvt[-2].string13);
  free(yypvt[-0].string12);
} break;
case 63:
# line 1061 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-4].string13)+strlen(yypvt[-0].string12) +2);
  strcpy(yyval.string13,yypvt[-4].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  free(yypvt[-4].string13);
  free(yypvt[-0].string12);
} break;
case 64:
# line 1072 "drsny.y"
{
  yyval.string13 = malloc(strlen(yypvt[-0].string12));
  strcpy(yyval.string13,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 65:
# line 1078 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-2].string13)+strlen(yypvt[-0].string12)+2);
  strcpy(yyval.string13,yypvt[-2].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,yypvt[-0].string12);
  free(yypvt[-2].string13);
  free(yypvt[-0].string12);
} break;
case 66:
# line 1087 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-0].string12);
} break;
case 67:
# line 1095 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-0].string12);
} break;
case 68:
# line 1103 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-0].string12);
} break;
case 69:
# line 1111 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-0].string12);
} break;
case 70:
# line 1119 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-0].string12);
} break;
case 71:
# line 1127 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-0].string12)+8);
  strcpy(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-0].string12);
} break;
case 72:
# line 1135 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-2].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-2].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-2].string13);
  free(yypvt[-0].string12);
} break;
case 73:
# line 1146 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-4].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-4].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-4].string13);
  free(yypvt[-0].string12);
} break;
case 74:
# line 1157 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-4].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-4].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",0}");
  free(yypvt[-4].string13);
  free(yypvt[-0].string12);
} break;
case 75:
# line 1168 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-3].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-3].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-3].string13);
  free(yypvt[-0].string12);
} break;
case 76:
# line 1179 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-5].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-5].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-5].string13);
  free(yypvt[-0].string12);
} break;
case 77:
# line 1190 "drsny.y"
{ 
  yyval.string13 = malloc(strlen(yypvt[-5].string13)+strlen(yypvt[-0].string12)+9);
  strcpy(yyval.string13,yypvt[-5].string13);
  strcat(yyval.string13,",");
  strcat(yyval.string13,"{[],");
  strcat(yyval.string13,yypvt[-0].string12);
  strcat(yyval.string13,",1}");
  free(yypvt[-5].string13);
  free(yypvt[-0].string12);
} break;
case 78:
# line 1202 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12) +1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 79:
# line 1209 "drsny.y"
{ 
  AppendNet0(&vtable,yypvt[-0].string11,dum);
  yyval.string12 = malloc(strlen(dum)+1);
  strcpy(yyval.string12,dum);
} break;
case 80:
# line 1215 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string11)+3);
  strcpy(yyval.string12,"\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\"");
} break;
case 81:
# line 1222 "drsny.y"
{ 
/* 
  yyval.string12 = malloc(strlen($1)+strlen(dum)+1);
  strcpy($$,$1);
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);
*/
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen(yypvt[-1].string12)+strlen(dum)+2); 
  strcpy(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,",");
  AppendNet0(&vtable,yypvt[-0].string11,dum);
  strcat(yyval.string12,dum);
  free(yypvt[-1].string12);

} break;
case 82:
# line 1241 "drsny.y"
{ 
/*
  yyval.string12 = malloc(strlen($1)+strlen($3)+3);
  strcpy($$,$1);
  strcat($$,"\"");
  strcat($$,$3);
  strcat($$,"\"");
  free($1);
*/ 
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string11)+4);
  strcpy(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,"\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\"");
  free(yypvt[-3].string12);

} break;
case 83:
# line 1262 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(dum)+1);
  AppendNet0(&vtable,yypvt[-0].string11,dum);
  strcpy(yyval.string12,dum);
} break;
case 84:
# line 1268 "drsny.y"
{ yyval.string12 = malloc(strlen(yypvt[-1].string11)+3);
  strcpy(yyval.string12,"\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\"");
} break;
case 85:
# line 1274 "drsny.y"
{ 
/*
  yyval.string12 = malloc(strlen($1)+strlen(dum)+1);
  strcpy($$,$1);
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);
*/ 
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen(yypvt[-1].string12)+strlen(dum)+2);
  strcpy(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,",");
  AppendNet0(&vtable,yypvt[-0].string11,dum);
  strcat(yyval.string12,dum);
  free(yypvt[-1].string12);

} break;
case 86:
# line 1293 "drsny.y"
{ 
/*
  yyval.string12 = malloc(strlen($1)+strlen($3)+3);
  strcpy($$,$1);
  strcat($$,"\"");
  strcat($$,$3);
  strcat($$,"\"");
  free($1);
*/ 
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string11)+4);
  strcpy(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,"\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\"");
  free(yypvt[-3].string12);

} break;
case 87:
# line 1315 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+28);
  htmake(yypvt[-5].string14,yypvt[-3].string12,newstring);
  free(yypvt[-3].string12);
  AppendhNet1(&htable,yypvt[-0].string11,newstring,string);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 88:
# line 1326 "drsny.y"
{ 
  char *newstring,*newstring2;
  stmake1(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  htmake(nstring,yypvt[-3].string12,newstring);
  newstring2 = malloc(strlen(newstring)+32);
  scolmake(newstring,newstring2);
  AppendsNet1(&stable,yypvt[-0].string11,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring2);
  free(yypvt[-3].string12);
  free(newstring);
  free(newstring2);
} break;
case 89:
# line 1341 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+12);
  htmake2(yypvt[-3].string14,yypvt[-1].string12,newstring); 
  free(yypvt[-1].string12);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy(yyval.string12,newstring);
  free(newstring);
} break;
case 90:
# line 1351 "drsny.y"
{ 
  char *newstring;
  stmake1(yypvt[-3].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-1].string12)+28);
  htmake(nstring,yypvt[-1].string12,newstring);
  free(yypvt[-1].string12);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy(yyval.string12,newstring);
  free(newstring);
} break;
case 91:
# line 1362 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  yyerrok;} break;
case 92:
# line 1367 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  yyerrok;
} break;
case 93:
# line 1373 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string12)+1);
  strcpy(yyval.string12,yypvt[-1].string12);
  yyerrok;
} break;
case 94:
# line 1379 "drsny.y"
{
  AppendhNet1(&htable,yypvt[-0].string11,yypvt[-0].string11,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 95:
# line 1385 "drsny.y"
{ 
  char *newstring;
  stabletake(&stable,yypvt[-0].string11);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy(yyval.string12,newstring3);
  free(newstring3);
} break;
case 96:
# line 1394 "drsny.y"
{ 
  char *newstring,*newstring2;
/*  printf("CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker\n");*/
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+28);
  htmake(yypvt[-5].string14,yypvt[-3].string12,newstring);
  newstring2 = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+28);
  predtake(newstring,newstring2);
  AppendhNet1(&htable,yypvt[-0].string11,newstring2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
  free(newstring);
  free(newstring2);
  free(yypvt[-3].string12);
} break;
case 97:
# line 1409 "drsny.y"
{ char *newstring,*newstring2,*newstring0;
/*  printf("CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker\n");*/
  stmake2(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  newstring2 = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  newstring0 = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  htmake(nstring,yypvt[-3].string12,newstring);
  scolmake(newstring,newstring2);
  predtake(newstring2,newstring0);
  AppendsNet1(&stable,yypvt[-0].string11,newstring0);
  yyval.string12 = malloc(strlen(newstring0)+1);
  strcpy(yyval.string12,newstring0);
  free(newstring);
  free(newstring2);
  free(newstring0);
  free(yypvt[-3].string12);
} break;
case 98:
# line 1427 "drsny.y"
{ 
  char *newstring,*newstring2;
/*  printf("CMPredicate CBRLP Ckaku CBRRP\n");*/
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+12);
  htmake2(yypvt[-3].string14,yypvt[-1].string12,newstring); 
  newstring2 = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+12);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring2);
  free(newstring);
  free(newstring2);
  free(yypvt[-1].string12);
} break;
case 99:
# line 1441 "drsny.y"
{ 
  char *newstring,*newstring2;
/*  printf("CPredicate CBRLP Ckaku CBRRP%s-%s\n",$1,$3);*/
  stmake2(yypvt[-3].string14,nstring);
/*  printf("input: %s\n",$1);
  printf("nstring: %s\n",nstring);*/
  newstring = malloc(strlen(nstring)+strlen(yypvt[-1].string12)+28);
  htmake(nstring,yypvt[-1].string12,newstring); 
  newstring2 = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+28);


  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring2);
  free(newstring);
  free(newstring2);
  free(yypvt[-1].string12);
} break;
case 100:
# line 1460 "drsny.y"
{ 
/*  printf("error CBRLP Ckaku CBRRP BP CBRHtermMaker\n");*/
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 101:
# line 1467 "drsny.y"
{ 
/*  printf("error CBRLP Ckaku CBRRP BP CBRSHMaker\n");*/
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 102:
# line 1474 "drsny.y"
{ 
/*  printf("error CBRLP Ckaku CBRRP\n");*/
  yyval.string12 = malloc(strlen(yypvt[-1].string12)+1);
  strcpy(yyval.string12,yypvt[-1].string12);
  free(yypvt[-1].string12);
  yyerrok;} break;
case 103:
# line 1481 "drsny.y"
{ 
/*  printf("(CBRHtermMaker)%s\n",$1);*/
  AppendhNet1(&htable,yypvt[-0].string11,yypvt[-0].string11,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 104:
# line 1488 "drsny.y"
{ 
/*  printf("(CBRSHMaker)%s\n",$1);*/
  stabletake(&stable,yypvt[-0].string11);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy(yyval.string12,newstring3);
  free(newstring3);
} break;
case 105:
# line 1497 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+13);
  htmake1(yypvt[-5].string14,yypvt[-3].string12,newstring);
  free(yypvt[-3].string12);
  AppendhNet1(&htable,yypvt[-0].string11,newstring,string);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 106:
# line 1508 "drsny.y"
{ 
  char *newstring,*newstring2;
  stmake1(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  htmake(nstring,yypvt[-3].string12,newstring);
  free(yypvt[-3].string12);
  newstring2 = malloc(strlen(newstring)+32);
  scolmake(newstring,newstring2);
  free(newstring);
  AppendsNet1(&stable,yypvt[-0].string11,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring);
  free(newstring2);
} break;
case 107:
# line 1523 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+12);
  htmake2(yypvt[-3].string14,yypvt[-1].string12,newstring);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy(yyval.string12,newstring);
  free(newstring);
  free(yypvt[-1].string12);
} break;
case 108:
# line 1533 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  htmake1(yypvt[-3].string14,yypvt[-1].string12,newstring);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy(yyval.string12,newstring);
  free(newstring);
  free(yypvt[-1].string12);
} break;
case 109:
# line 1543 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 110:
# line 1549 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  strcpy(yyval.string12,yypvt[-3].string12);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 111:
# line 1555 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string12)+1);
  strcpy(yyval.string12,yypvt[-1].string12);
  free(yypvt[-1].string12);
  yyerrok;} break;
case 112:
# line 1561 "drsny.y"
{ 
  AppendhNet1(&htable,yypvt[-0].string11,yypvt[-0].string11,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 113:
# line 1567 "drsny.y"
{
  stabletake(&stable,yypvt[-0].string11);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy(yyval.string12,newstring3);
  free(newstring3);
} break;
case 114:
# line 1576 "drsny.y"
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+13);
  htmake1(yypvt[-5].string14,yypvt[-3].string12,newstring);
  newstring2 = malloc(strlen(yypvt[-5].string14)+strlen(yypvt[-3].string12)+13);
  predtake(newstring,newstring2);
  AppendhNet1(&htable,yypvt[-0].string11,newstring2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
  free(newstring);
  free(newstring2);
  free(yypvt[-3].string12);
} break;
case 115:
# line 1590 "drsny.y"
{ 
  char *newstring,*newstring2,*newstring0;
  stmake1(yypvt[-5].string14,nstring);
  newstring = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  htmake(nstring,yypvt[-3].string12,newstring);
  newstring2 = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28);
  newstring0 = malloc(strlen(nstring)+strlen(yypvt[-3].string12)+28); /* 1995-9-14 add */
  scolmake(newstring,newstring2);
  predtake(newstring2,newstring0);
  AppendsNet1(&stable,yypvt[-0].string11,newstring0);
  yyval.string12 = malloc(strlen(newstring0)+1);
  strcpy(yyval.string12,newstring0);
  free(newstring);
  free(newstring2);
  free(newstring0);
  free(yypvt[-3].string12);
} break;
case 116:
# line 1608 "drsny.y"
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  htmake2(yypvt[-3].string14,yypvt[-1].string12,newstring);
  newstring2 = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring2);
  free(newstring);
  free(newstring2);
  free(yypvt[-1].string12);
} break;
case 117:
# line 1621 "drsny.y"
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  htmake1(yypvt[-3].string14,yypvt[-1].string12,newstring);
  newstring2 = malloc(strlen(yypvt[-3].string14)+strlen(yypvt[-1].string12)+13);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy(yyval.string12,newstring2);
  free(newstring);
  free(newstring2);
  free(yypvt[-1].string12);
} break;
case 118:
# line 1634 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 119:
# line 1639 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+1);
  free(yypvt[-3].string12);
  yyerrok;} break;
case 120:
# line 1644 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string12)+1);
  free(yypvt[-1].string12);
  yyerrok;} break;
case 121:
# line 1649 "drsny.y"
{ 
  AppendhNet1(&htable,yypvt[-0].string11,yypvt[-0].string11,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 122:
# line 1655 "drsny.y"
{ 
  stabletake(&stable,yypvt[-0].string11);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy(yyval.string12,newstring3);
  free(newstring3);
} break;
case 123:
# line 1664 "drsny.y"
{ strcpy(yyval.string14,yypvt[-0].string14);
} break;
case 124:
# line 1668 "drsny.y"
{ strcpy(yyval.string14,yypvt[-0].string14);
} break;
case 125:
# line 1672 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string12,"{[],");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 126:
# line 1680 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string12,"{not,");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 127:
# line 1688 "drsny.y"
{
  strcpy(yyval.string12,yypvt[-0].string12);
} break;
case 128:
# line 1694 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+9);
  strcpy(yyval.string12,"{less,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 129:
# line 1705 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+12);
  strcpy(yyval.string12,"{greater,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 130:
# line 1716 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+10);
  strcpy(yyval.string12,"{equal,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 131:
# line 1727 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+14);
  strcpy(yyval.string12,"{not_equal,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 132:
# line 1738 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+9);
  strcpy(yyval.string12,"{same,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 133:
# line 1749 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+14);
  strcpy(yyval.string12,"{different,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 134:
# line 1762 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+9);
  strcpy(yyval.string12,"{less,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 135:
# line 1773 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+12);
  strcpy(yyval.string12,"{greater,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 136:
# line 1784 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+10);
  strcpy(yyval.string12,"{equal,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 137:
# line 1795 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+14);
  strcpy(yyval.string12,"{not_equal,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 138:
# line 1806 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+9);
  strcpy(yyval.string12,"{same,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 139:
# line 1817 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string12)+strlen(yypvt[-1].string12)+14);
  strcpy(yyval.string12,"{different,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-3].string12);
  free(yypvt[-1].string12);
} break;
case 140:
# line 1830 "drsny.y"
{ yyval.string12 = malloc(8);
  strcpy(yyval.string12,"");} break;
case 141:
# line 1833 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-2].string11)+strlen(yypvt[-0].string12)+4);
  strcpy(yyval.string12,"{");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 142:
# line 1843 "drsny.y"
{ yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  yyerrok;} break;
case 143:
# line 1848 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-4].string12)+strlen(yypvt[-2].string11)+strlen(yypvt[-0].string12)+5);
  strcpy(yyval.string12,yypvt[-4].string12);
  strcat(yyval.string12,",{");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-4].string12);
  free(yypvt[-0].string12);
} break;
case 144:
# line 1861 "drsny.y"
{ 
  yyval.string12 = malloc(8);
  strcpy(yyval.string12,"");
} break;
case 145:
# line 1866 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-2].string11)+strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string12,"{");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  if(bodycount == 0){
    strcat(yyval.string12,"}");}
  else{
    strcat(yyval.string12,",0}");}
} break;
case 146:
# line 1879 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12) +1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  yyerrok;
} break;
case 147:
# line 1886 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12) +1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  yyerrok;
} break;
case 148:
# line 1893 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-3].string11)+strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string12,"{");
  strcat(yyval.string12,yypvt[-3].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,",1}");
  free(yypvt[-0].string12);
} break;
case 149:
# line 1903 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-4].string12)+strlen(yypvt[-2].string11)+strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string12,yypvt[-4].string12);
  strcat(yyval.string12,",{");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
  free(yypvt[-4].string12);
  if(bodycount == 0){
    strcat(yyval.string12,"}");}
  else{
    strcat(yyval.string12,",0}");}
} break;
case 150:
# line 1918 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-5].string12)+strlen(yypvt[-3].string11)+strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string12,yypvt[-5].string12);
  strcat(yyval.string12,",{");
  strcat(yyval.string12,yypvt[-3].string11);
  strcat(yyval.string12,",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,",1}");
  free(yypvt[-5].string12);
  free(yypvt[-0].string12);
} break;
case 151:
# line 1931 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 152:
# line 1937 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 153:
# line 1943 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string12)+1);
  strcpy(yyval.string12,yypvt[-0].string12);
  free(yypvt[-0].string12);
} break;
case 154:
# line 1950 "drsny.y"
{ 
  makeAtom(yyval.string14,yypvt[-0].string14);
} break;
case 155:
# line 1954 "drsny.y"
{ 
/*  
  someAtomMake($2,$$);
*/
  yyerror("!trans","Not support some operator");
} break;
case 156:
# line 1961 "drsny.y"
{
  makeAtom1(yyval.string14,yypvt[-1].string14,yypvt[-0].string12);
} break;
case 157:
# line 1965 "drsny.y"
{
/*
  someAtomMake1($2,$3,$$);
*/
  yyerror("!trans","Not support some operator");
} break;
case 158:
# line 1972 "drsny.y"
{ 
  strcpy(string2,"0");
  AppendNet1(&vtable,yypvt[-0].string11,string2,string);
  strcpy(yyval.string14,string);
} break;
case 159:
# line 1978 "drsny.y"
{ 
  char dummy2[512];
  makeAtom(dummy2,yypvt[-0].string14);
  AppendNet1(&vtable,yypvt[-2].string11,dummy2,string);
  strcpy(yyval.string14,string);
} break;
case 160:
# line 1985 "drsny.y"
{ 
/*
  someAtomMake($4,nstring);
  AppendNet1(&vtable,$1,nstring,string);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 161:
# line 1994 "drsny.y"
{
  char dummy[512];
  makeAtom1(dummy,yypvt[-1].string14,yypvt[-0].string12);
  AppendNet1(&vtable,yypvt[-3].string11,dummy,string);
  strcpy(yyval.string14,string);
} break;
case 162:
# line 2001 "drsny.y"
{
/*
  char *newstring,string[512];
  newstring = malloc(strlen($4)+strlen($5)+21);
  someAtomMake1($4,$5,newstring);
  AppendNet1(&vtable,$1,newstring,string);
  free($5);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 163:
# line 2016 "drsny.y"
{ 
/*  printf("CBRSSAtom %s\n",$1);*/
  makeAtom(dummy,yypvt[-0].string14);
  strcpy(yyval.string14,"<");
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,",");
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,">");
/*  printf("CBRSSAtom %s\n",$$);*/
} break;
case 164:
# line 2027 "drsny.y"
{ 
/*
  someAtomMake($2,dummy);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  makeAtom(dummy,$2);
  strcat($$,dummy);
  strcat($$,">");
*/
  yyerror("!trans","Not support some operator");
} break;
case 165:
# line 2040 "drsny.y"
{ 
/*  printf("CBRSSAtom AttributeS %s-%s\n",$1,$2);*/
  makeAtom1(dummy,yypvt[-1].string14,yypvt[-0].string12);
  strcpy(yyval.string14,"<");
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,",");
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,">");
} break;
case 166:
# line 2050 "drsny.y"
{
  yyerror("!trans","Not support some operator");
} break;
case 167:
# line 2054 "drsny.y"
{
  cbrVamake3(yypvt[-0].string11,yyval.string14);
} break;
case 168:
# line 2058 "drsny.y"
{ 
/*  printf("CBRVariable DIP CBRSSAtom %s-%s\n",$1,$3);*/
  cbrVamake(yypvt[-2].string11,yypvt[-0].string14,yyval.string14);
} break;
case 169:
# line 2063 "drsny.y"
{ 
/*
  cbrVaSmake($1,$4,$$);
*/
  yyerror("!trans","Not support some operator");
} break;
case 170:
# line 2070 "drsny.y"
{ 
/*  printf("CBRVariable DIP CBRSSAtom AttributeS %s-%s\n",$3,$4);*/
  cbrVamake4(yypvt[-3].string11,yypvt[-1].string14,yypvt[-0].string12,yyval.string14);
} break;
case 171:
# line 2075 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 172:
# line 2079 "drsny.y"
{ 
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-1].string12,str);

  makeAtom(dummy,yypvt[-3].string14);
  strcpy(yyval.string14,"<");
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,",");
  strcat(yyval.string14,str);
  strcat(yyval.string14,">");
} break;
case 173:
# line 2093 "drsny.y"
{ strcpy(yyval.string14,"<");
  makeAtom(dummy,yypvt[-3].string14);
  strcat(yyval.string14,dummy);
  strcat(yyval.string14,",0>");
} break;
case 174:
# line 2099 "drsny.y"
{ 
/*
  char str[512];
  someAtomMake($2,string);
  memset(str,0,512);
  bunkatu($4,str);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",");
  strcat($$,str);
  strcat($$,">");
*/
  yyerror("!trans","Not support some operator");
} break;
case 175:
# line 2114 "drsny.y"
{ 
/*
  someAtomMake($2,string);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",0>");
*/
  yyerror("!trans","Not support some operator");
} break;
case 176:
# line 2124 "drsny.y"
{
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-1].string12,str);
  strcpy(yyval.string14,"<{");
  strcat(yyval.string14,yypvt[-4].string14);
  strcat(yyval.string14,",0,");
  strcat(yyval.string14,yypvt[-3].string12);
  strcat(yyval.string14,"},");
  strcat(yyval.string14,str);
  strcat(yyval.string14,">");
} break;
case 177:
# line 2138 "drsny.y"
{
  strcpy(yyval.string14,"<{");
  strcat(yyval.string14,yypvt[-4].string14);
  strcat(yyval.string14,",0,");
  strcat(yyval.string14,yypvt[-3].string12);
  strcat(yyval.string14,"},0>");
} break;
case 178:
# line 2146 "drsny.y"
{
  yyerror("!trans","Not support some operator");
} break;
case 179:
# line 2150 "drsny.y"
{
  yyerror("!trans","Not support some operator");
} break;
case 180:
# line 2154 "drsny.y"
{ 
  cbrVamake2(yypvt[-5].string11,yypvt[-3].string14,yypvt[-1].string12,yyval.string14);
} break;
case 181:
# line 2158 "drsny.y"
{ 
  cbrVamakeT(yypvt[-5].string11,yypvt[-3].string14,yyval.string14);
} break;
case 182:
# line 2162 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 183:
# line 2166 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 184:
# line 2170 "drsny.y"
{ 
  cbrVamake41(yypvt[-6].string11,yypvt[-4].string14,yypvt[-3].string12,yypvt[-1].string12,yyval.string14);
} break;
case 185:
# line 2174 "drsny.y"
{ 
  cbrVamake4T(yypvt[-6].string11,yypvt[-4].string14,yypvt[-3].string12,yyval.string14);
} break;
case 186:
# line 2178 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 187:
# line 2182 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 190:
# line 2192 "drsny.y"
{
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-0].string12,str);
  strcpy(yyval.string12,str);
} break;
case 192:
# line 2203 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-0].string14)+1);
  strcpy(yyval.string12,yypvt[-0].string14);
} break;
case 193:
# line 2208 "drsny.y"
{ 
/*
  someAtomMake($2,dummy);
  yyval.string12 = malloc(strlen(dummy)+1);
  strcpy(yyval.string12,dummy);
*/
  yyerror("!trans","Not support some operator");

} break;
case 194:
# line 2218 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string14)+strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string12,"{");
  strcat(yyval.string12,yypvt[-1].string14);
  strcat(yyval.string12,",0,");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 195:
# line 2228 "drsny.y"
{ 
/*
  char *newstring;
  newstring = malloc(strlen($2)+strlen($3)+21);
  someAtomMake1($2,$3,newstring);
  yyval.string12 = malloc(strlen(newstring)+3);
  strcpy($$,"{");
  strcat($$,newstring);
  strcat($$,"}");
  free($3);
  free(newstring);
*/
  yyerror("!trans","Not support some operator");
} break;
case 196:
# line 2243 "drsny.y"
{ 
  strcpy(string2,"0");
  AppendNet1(&vtable,yypvt[-0].string11,string2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 197:
# line 2250 "drsny.y"
{ 
  char dummy2[512];
  makeAtom(dummy2,yypvt[-0].string14);
  AppendNet1(&vtable,yypvt[-2].string11,dummy2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 198:
# line 2258 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 199:
# line 2262 "drsny.y"
{ 
  char *newstring;
  newstring = malloc(strlen(yypvt[-1].string14)+strlen(yypvt[-0].string12)+6);
  strcpy(newstring,"{");
  strcat(newstring,yypvt[-1].string14);
  strcat(newstring,",0,");
  strcat(newstring,yypvt[-0].string12);
  strcat(newstring,"}");
  AppendNet1(&vtable,yypvt[-3].string11,newstring,string);
  free(newstring);
  free(yypvt[-0].string12);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 200:
# line 2277 "drsny.y"
{ 
/*
  char *newstring,string[512];
  newstring = malloc(strlen($4)+strlen($5)+21);
  someAtomMake1($4,$5,newstring);
  AppendNet1(&vtable,$1,newstring,string);
  free($5);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 201:
# line 2291 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string11)+10);
  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\",0,[]}");
} break;
case 202:
# line 2298 "drsny.y"
{
  yyval.string12 = malloc(strlen(yypvt[-1].string11)+10);
  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\",0,[]}");
} break;
case 203:
# line 2305 "drsny.y"
{ 
  char dummy2[512];
  strcpy(dummy2,"{\"");
  strcat(dummy2,yypvt[-1].string11);
  strcat(dummy2,"\",0,[]}");
  AppendNet1(&vtable,yypvt[-4].string11,dummy2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 206:
# line 2321 "drsny.y"
{ 

/*oosaki modify*/
/*
  makeAtom(dummy,$1);
  yyval.string12 = malloc(strlen(dummy)+strlen(dummy)+4);
  if(attributecount == 0){
    strcpy($$,"<");
    strcat($$,dummy);
    strcat($$,",");
    strcat($$,dummy);
    strcat($$,">");}
  else{
    strcpy($$,dummy);
  }
*/
  makeAtom(dummy,yypvt[-0].string14);
  yyval.string12 = malloc(strlen(dummy)+strlen(dummy)+4);
  strcpy(yyval.string12,"<");
  strcat(yyval.string12,dummy);
  strcat(yyval.string12,",");
  strcat(yyval.string12,dummy);
  strcat(yyval.string12,">");
} break;
case 207:
# line 2346 "drsny.y"
{
  yyerror("!trans","Not support some operator");
} break;
case 208:
# line 2350 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string14)+strlen(yypvt[-1].string14)+
			  strlen(yypvt[-0].string12)+strlen(yypvt[-0].string12)+14);
  strcpy(yyval.string12,"<{");
  strcat(yyval.string12,yypvt[-1].string14);
  strcat(yyval.string12,",0,");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"},{");
  strcat(yyval.string12,yypvt[-1].string14);
  strcat(yyval.string12,",0,");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}>");
  free(yypvt[-0].string12);
} break;
case 209:
# line 2365 "drsny.y"
{
  yyerror("!trans","Not support some operator");
} break;
case 210:
# line 2369 "drsny.y"
{ 
  cbrVamake3(yypvt[-0].string11,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 211:
# line 2375 "drsny.y"
{ 
  cbrVamake(yypvt[-2].string11,yypvt[-0].string14,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 212:
# line 2381 "drsny.y"
{ 
/*
  cbrVaSmake($1,$4,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 213:
# line 2390 "drsny.y"
{ 
  cbrVamake4(yypvt[-3].string11,yypvt[-1].string14,yypvt[-0].string12,string);
  yyval.string12 = malloc(strlen(string)+1);
  free(yypvt[-0].string12);
  strcpy(yyval.string12,string);
} break;
case 214:
# line 2397 "drsny.y"
{ 
/*
  cbrVaSmake3($1,$4,$5,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 215:
# line 2407 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string11)+10);
  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\",0,[]}");
} break;
case 216:
# line 2414 "drsny.y"
{
  yyval.string12 = malloc(strlen(yypvt[-1].string11)+10);
  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-1].string11);
  strcat(yyval.string12,"\",0,[]}");
} break;
case 217:
# line 2421 "drsny.y"
{ 
  char dummy2[512];
  strcpy(dummy2,"{\"");
  strcat(dummy2,yypvt[-1].string11);
  strcat(dummy2,"\",0,[]}");
  AppendNet1(&vtable,yypvt[-4].string11,dummy2,string);
  AppendCNet1(&ctable,yypvt[-4].string11,dummy2);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 218:
# line 2434 "drsny.y"
{ 
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-1].string12,str);

  makeAtom(dummy,yypvt[-3].string14);
  yyval.string12 = malloc(strlen(dummy)+strlen(str)+4);
  strcpy(yyval.string12,"<");
  strcat(yyval.string12,dummy);
  strcat(yyval.string12,",");
  strcat(yyval.string12,str);
  strcat(yyval.string12,">");
} break;
case 219:
# line 2449 "drsny.y"
{ 
  makeAtom(dummy,yypvt[-3].string14);
  yyval.string12 = malloc(strlen(dummy)+5);
  strcpy(yyval.string12,"<");
  strcat(yyval.string12,dummy);
  strcat(yyval.string12,",0>");
} break;
case 220:
# line 2457 "drsny.y"
{ 
/*
  char str[512];

  memset(str,0,512);
  bunkatu($4,str);
  someAtomMake($2,string);
  yyval.string12 = malloc(strlen(string)+strlen(str)+4);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",");
  strcat($$,str);
  strcat($$,">");
*/
  yyerror("!trans","Not support some operator");
} break;
case 221:
# line 2474 "drsny.y"
{ 
/*  someAtomMake($2,string);
  yyval.string12 = malloc(strlen(string)+5);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",0>");
*/
  yyerror("!trans","Not support some operator");
} break;
case 222:
# line 2484 "drsny.y"
{ 
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-1].string12,str);

  yyval.string12 = malloc(strlen(yypvt[-4].string14)+strlen(yypvt[-3].string12)+strlen(str)+9);
  strcpy(yyval.string12,"<{");
  strcat(yyval.string12,yypvt[-4].string14);
  strcat(yyval.string12,",0,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,"},");
  strcat(yyval.string12,str);
  strcat(yyval.string12,">");
  free(yypvt[-3].string12);
} break;
case 223:
# line 2501 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-4].string14)+strlen(yypvt[-3].string12)+10);
  strcpy(yyval.string12,"<{");
  strcat(yyval.string12,yypvt[-4].string14);
  strcat(yyval.string12,",0,");
  strcat(yyval.string12,yypvt[-3].string12);
  strcat(yyval.string12,"},0>");
  free(yypvt[-3].string12);
} break;
case 224:
# line 2511 "drsny.y"
{ 
  cbrVamake2(yypvt[-5].string11,yypvt[-3].string14,yypvt[-1].string12,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 225:
# line 2517 "drsny.y"
{ 
  cbrVamakeT(yypvt[-5].string11,yypvt[-3].string14,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy(yyval.string12,string);
} break;
case 226:
# line 2523 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 227:
# line 2527 "drsny.y"
{ 
  yyerror("!trans","Not support some operator");
} break;
case 228:
# line 2531 "drsny.y"
{ 
  cbrVamake41(yypvt[-6].string11,yypvt[-4].string14,yypvt[-3].string12,yypvt[-1].string12,string);
  yyval.string12 = malloc(strlen(string)+1);
  free(yypvt[-3].string12);
  strcpy(yyval.string12,string);
} break;
case 229:
# line 2538 "drsny.y"
{ 
  cbrVamake4T(yypvt[-6].string11,yypvt[-4].string14,yypvt[-3].string12,string);
  yyval.string12 = malloc(strlen(string)+1);
  free(yypvt[-3].string12);
  strcpy(yyval.string12,string);
} break;
case 230:
# line 2545 "drsny.y"
{ 
/*
  cbrVaSmake4($1,$4,$5,$7,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 231:
# line 2555 "drsny.y"
{ 
/*
  cbrVaSmake4T($1,$4,$5,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
} break;
case 232:
# line 2567 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-2].string11)+strlen(yypvt[-0].string12)+6);
  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,"\",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 233:
# line 2577 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-2].string11)+strlen(yypvt[-4].string12)+strlen(yypvt[-0].string12)+7);
  strcpy(yyval.string12,yypvt[-4].string12);
  strcat(yyval.string12,",{\"");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,"\",");
  strcat(yyval.string12,yypvt[-0].string12);
  strcat(yyval.string12,"}");
  free(yypvt[-4].string12);
  free(yypvt[-0].string12);
} break;
case 234:
# line 2589 "drsny.y"
{ 
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-0].string12,str);
  yyval.string12 = malloc(strlen(yypvt[-2].string11)+strlen(str)+8);

  strcpy(yyval.string12,"{\"");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,"\",");
  strcat(yyval.string12,str);
  strcat(yyval.string12,"}");
  free(yypvt[-0].string12);
} break;
case 235:
# line 2605 "drsny.y"
{ 
  char str[512];

  memset(str,0,512);
  bunkatu(yypvt[-0].string12,str);

  yyval.string12 = malloc(strlen(yypvt[-4].string12)+strlen(yypvt[-2].string11)+strlen(str)+9);
  strcpy(yyval.string12,yypvt[-4].string12);
  strcat(yyval.string12,",{\"");
  strcat(yyval.string12,yypvt[-2].string11);
  strcat(yyval.string12,"\",");
  strcat(yyval.string12,str);
  strcat(yyval.string12,"}");
  free(yypvt[-4].string12);
  free(yypvt[-0].string12);

} break;
case 236:
# line 2625 "drsny.y"
{ 
  yyval.string12 = malloc(strlen(yypvt[-1].string12)+3);
  strcpy(yyval.string12,"[");
  strcat(yyval.string12,yypvt[-1].string12);
  strcat(yyval.string12,"]");
  free(yypvt[-1].string12);
} break;
case 237:
# line 2634 "drsny.y"
{ 
  makeAtom(yyval.string14,yypvt[-0].string14);
} break;
case 238:
# line 2640 "drsny.y"
{ 
  strcpy(yyval.string14,"'");
  strcat(yyval.string14,yypvt[-0].string11);
  strcat(yyval.string14,"'");
} break;
case 239:
# line 2646 "drsny.y"
{ 
  strcpy(yyval.string14,yypvt[-0].string11);
} break;
case 240:
# line 2650 "drsny.y"
{ 
  strcpy(yyval.string14,"{");
  strcat(yyval.string14,yypvt[-0].string11);
  strcat(yyval.string14,"}");
} break;
case 241:
# line 2656 "drsny.y"
{ 
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  numtake(yypvt[-0].string11,number1,number2);
  strcpy(yyval.string14,"{{");
  strcat(yyval.string14,number1);
  strcat(yyval.string14,"},{");
  strcat(yyval.string14,number2);
  strcat(yyval.string14,"}}");
} break;
case 242:
# line 2669 "drsny.y"
{ 
  strcpy(yyval.string14,"'");
  strcat(yyval.string14,yypvt[-0].string11);
  strcat(yyval.string14,"'");
} break;
case 243:
# line 2675 "drsny.y"
{ 
  strcpy(yyval.string14,yypvt[-0].string11);
} break;
case 244:
# line 2679 "drsny.y"
{ 
  strcpy(yyval.string14,"{");
  strcat(yyval.string14,yypvt[-0].string11);
  strcat(yyval.string14,"}");
} break;
case 245:
# line 2685 "drsny.y"
{ 
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  numtake(yypvt[-0].string11,number1,number2);
  strcpy(yyval.string14,"{{");
  strcat(yyval.string14,number1);
  strcat(yyval.string14,"},{");
  strcat(yyval.string14,number2);
  strcat(yyval.string14,"}}");
} break;
	}
	goto yystack;		/* reset registers in driver code */
}

# ifdef YYEUCCCOUNT
yyeuclex()
{
    unsigned short c;
    int i;
 
    c = yylex();
    if( c < 256 ) return(c);
    for(i=0;i<YYEUCCCOUNT;i++)
        if( c == yyeucctable[i].name )
            return( yyeucctable[i].val );
    return(c);
}
# endif
 
