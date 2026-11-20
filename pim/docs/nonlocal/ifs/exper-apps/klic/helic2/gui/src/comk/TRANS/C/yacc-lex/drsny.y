/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*  7/20 repair 
**  7/21 repair (atom hyouji bubun no shuusei) 
**  7/27 repair (kata bubun no teisuukata tuika )      
**  8/3  bug repair                                  
**  8/4  repair    bug exist
**       bug repair   hterm ID structure repair  
**       bug(some bubun) repair                       
**       bug(CBR rule Head part ) repair              
**       bug repair 8/19                                
**  8/23 kumikomijutugo taiou                            
**  malloc use version     (9/7)                     
**                         (9/9)                   
**  11/15 bug shuusei               
**  DRS Version                     */
%{
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
%}
%union {
  char string11[512];
  char *string12;
  char *string13;
  char string14[512];
}
%token  <string11> LP RP BBP DIP MP OPOP OP EP ANDP MIP NP KLP KRP BP NL IP
%token  <string11> TRP TLP KName Variable Atom HtermMaker Some Not ZName WK
%token  <string11> Mstring REnd DAR DRR SHMaker BBB DCR CBRAtom CKName
%token  <string11> CBRVariable RGP LGP CBRSHMaker CBRHtermMaker SAtom 
%token  <string11> CBRSAtom CBREP CBRLP CBRRP DG GName GSHMaker GVariable
%token  <string11> GHtermMaker TOP Number NumberDomain CBRNumber 
%token  <string11> CBRNumberDomain LESS GREATER EQUAL NOTEQUAL SAME DIFFERENT
%type   <string12> HTerm PTerm PTermWithoutLimit RBRPTerm CBRPTerm CBRPTermWithoutLimit CBRPTermWithLimit Term kaku AttributeS Builtin CBuiltin
%type   <string12> RuleEx Head Rulek HHTerm RHTerm CHead
%type   <string12> CHHTerm CHTerm Ckaku Attri 
%type   <string13> CRBody GoalList Goal
%type   <string13> RBody Body AbsoluteRule AbsoluteRuleL RBRRule CBRRule
%type   <string14> Predicate Atoms MPredicate NAtom CBRSSAtom
%type   <string14> CPredicate CMPredicate 
%start RuleBase
%%
RuleBase         : DARAbsoluteRuleBase DRRRBRRuleBase DCRCBRRuleBase
                 | GoalData
                 ;
GoalData         : DG
                 | DG GoalList
                 ;
GoalList         : TRP Goal TLP
{
  AllDeleteSNet(&stable);
}
                 | GoalList TRP Goal TLP
{
  AllDeleteSNet(&stable);
}
                 ;
Goal             : Predicate LP kaku RP
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  strToIngiVec(&vtable,invector);
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+
			  sizeof("{\"{{[],},,[],}}")+1);
  strcpy($$,"{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
}
                 | MPredicate LP kaku RP
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+30);
  htmake3(nstring,$3,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+16);
  strcpy($$,"{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  free($3);
  free(newstring);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  kaisuucount1=0;
  hcount1=0;
}
                 | Goal IP Predicate LP kaku RP
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen($3)+strlen($5)+13);
  htmake1($3,$5,newstring);  
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+17);
  strcpy($$,",{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($5);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
}
                 | Goal IP MPredicate LP kaku RP
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1($3,nstring);
  newstring = malloc(strlen($5)+strlen(nstring)+30);
  htmake3(nstring,$5,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+17);
  strcpy($$,",{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(newstring);
  free($5);
  kaisuucount1=0;
  hcount1=0;
}
                 | Predicate LP kaku RP BBP RuleEx
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+14);
  strcpy($$,"{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",");
  strcat($$,$6);
  strcat($$,",");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($6);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
}
                 | MPredicate LP kaku RP BBP RuleEx
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+30);
  htmake3(nstring,$3,string);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen(invector)
			  +strlen(vector)+strlen(hvector)+14);
  strcpy($$,"{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",");
  strcat($$,$6);
  strcat($$,",");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($6);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
}
                 | Goal IP Predicate LP kaku RP BBP RuleEx
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  newstring = malloc(strlen($3)+strlen($5)+13);
  htmake1($3,$5,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen($8)+
			  strlen(invector)+strlen(vector)+strlen(hvector)+15);
  strcpy($$,",{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",");
  strcat($$,$8);
  strcat($$,",");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($5);
  free($8);
  free(newstring);
  kaisuucount1=0;
  hcount1=0;
}
                 | Goal IP MPredicate LP kaku RP BBP RuleEx
{ 
  char *newstring;
  origstring[strlen(origstring)-1]= '"';
  strcat(origstring,",");
  stmake1($3,nstring);
  newstring = malloc(strlen(nstring)+strlen($5)+30);
  htmake3(nstring,$5,newstring);
  strToVec(&vtable,vector);
  strToIngiVec(&vtable,invector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen(origstring)+strlen(newstring)+strlen($8)+
			  strlen(invector)+strlen(vector)+strlen(hvector)+15);
  strcpy($$,",{\"");
  strcat($$,origstring);
  strcat($$,"{{[],");
  strcat($$,newstring);
  strcat($$,"},");
  strcat($$,vector);
  strcat($$,",");
  strcat($$,invector);
  strcat($$,",");
  strcat($$,$8);
  strcat($$,",");
  strcat($$,hvector);
  strcat($$,"}}");
  pri($$,priout);
  memset(origstring,0,STRINGSIZE);
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free(newstring);
  free($5);
  free($8);
  kaisuucount1=0;
  hcount1=0;
}
                 ;
DARAbsoluteRuleBase :  DAR
                    |  DAR AbsoluteRuleBase
                 ;
DRRRBRRuleBase   : DRR
                 | DRR RBRRuleBase
                 ;
DCRCBRRuleBase   : DCR
                 | DCR CBRRuleBase
                 ;
AbsoluteRuleBase : TRP AbsoluteRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 | AbsoluteRuleBase TRP AbsoluteRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 ;
RBRRuleBase      : TRP RBRRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 | RBRRuleBase TRP RBRRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 ;
CBRRuleBase      : TRP CBRRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 | CBRRuleBase TRP CBRRuleL TLP
{
  AllDeleteSNet(&stable);
}
                 ;
AbsoluteRuleL    : AbsoluteRule
{ 
  pri($1,priout);
  free($1);
  rulechecknumber1=1;
}
                 | AbsoluteRuleL AbsoluteRule
{
  pri(",",priout);
  pri($2,priout);
  free($2);
}
                 ;
RBRRuleL         : RBRRule
{ 
  rulechecknumber2=1;
  if(rulechecknumber1==0){
    pri($1,priout);
    free($1);
  }
  else{
    pri(",",priout);
    pri($1,priout);
    free($1);
  }
}
                 | RBRRuleL RBRRule
{
  pri(",",priout);
  pri($2,priout);
  free($2);
}
                 ;
CBRRuleL         : CBRRule
{
  if(rulechecknumber2==0){
    pri($1,priout);
    free($1);
  }
  else{
    pri(",",priout);
    pri($1,priout);
    free($1);
  }
}
                 | CBRRuleL CBRRule
{
  pri(",",priout);
  pri($2,priout);
  free($2);
}
                 ;
AbsoluteRule     : Atom OPOP Head MP Body BBP RuleEx REnd
{
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(hvector)+strlen($7)+16);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$7);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  free($7);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head MP Body REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($1)+strlen(vector)
			  +strlen(hvector)+16);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[],");
  strcat($$,vector);
  strcat($$,",[],");
  strcat($$,vector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 ;
RBRRule     : Atom OPOP Head MP RBody BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($1)+strlen($5)+strlen(vector)+
		    strlen($7)+strlen(hvector) +16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$7);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  free($7);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head MP RBody REnd
{
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($1)+strlen($5)+strlen(vector)+
    strlen(hvector) + 16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"]");
  strcat(yyval.string13,",");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($1)+strlen($5)+strlen(vector)+
			  strlen(hvector) +16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | Atom OPOP Head REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($1)+strlen($3)+strlen(vector)+
			  strlen(hvector)+16);
  strcpy(yyval.string13,"{'");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,"',{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                |SAtom OPOP Head MP RBody BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($1)+strlen($3)+strlen($5)+strlen(vector)
		    +strlen(hvector)+strlen($7)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$7);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  free($7);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | SAtom OPOP Head MP RBody REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($1)+strlen($3)+strlen($5)+strlen(vector)
		    +strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"]");
  strcat(yyval.string13,",");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  free($5);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | SAtom OPOP Head BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen(vector)+strlen($1)
		    +strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[");
  strcat(yyval.string13,$5);
  strcat(yyval.string13,"],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($5);
  free($3);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | SAtom OPOP Head REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  yyval.string13= malloc(strlen($1)+strlen($3)+strlen(vector)+
			 strlen(hvector)+14);
  strcpy(yyval.string13,"{");
  strcat(yyval.string13,$1);
  strcat(yyval.string13,",{");
  strcat(yyval.string13,$3);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,vector);
  strcat(yyval.string13,",[],");
  strcat(yyval.string13,hvector);
  strcat(yyval.string13,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  free($3);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 ;
CBRRule     : CBRAtom OPOP CHead MP CRBody BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen($7)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +17);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$7);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  free($7);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
          | CBRSAtom OPOP CHead MP CRBody BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($7)+strlen($1)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +15);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$7);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  free($7);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | CBRAtom OPOP CHead MP CRBody REnd
{ 
/*  printf("CBRAtom OPOP CHead MP CRBody REnd%s-%s-%s\n",$1,$3,$5);*/
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+
			  strlen(vector)+strlen(hvector)+strlen(cvector)
			  +17);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | CBRSAtom OPOP CHead MP CRBody REnd
{ 
/*  printf("CBRSAtom OPOP CHead MP CRBody REnd%s-%s-%s\n",$1,$3,$5);*/
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(vector)+strlen(hvector)+strlen(cvector)
			  +15);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,vector);
  strcat($$,",[],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  hcount1=0;
  kaisuucount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | CBRAtom OPOP CHead BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(hvector)+strlen(cvector)+17);
  strcpy($$,"{'");
  strcat($$,$1);
  strcat($$,"',{");
  strcat($$,$3);
  strcat($$,",[],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 | CBRSAtom OPOP CHead BBP RuleEx REnd
{ 
  strToVec(&vtable,vector);
  hstrToVec(&htable,hvector);
  strToVec2(&ctable,cvector);
  yyval.string13 = malloc(strlen($3)+strlen($5)+strlen($1)+strlen(vector)
			  +strlen(hvector)+strlen(cvector)+15);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",[],");
  strcat($$,vector);
  strcat($$,",[");
  strcat($$,$5);
  strcat($$,"],");
  strcat($$,hvector);
  strcat($$,",");
  strcat($$,cvector);
  strcat($$,"}}");
  AllDeleteNet(&vtable);
  AllDeleteHNet(&htable);
  AllDeleteCNet(&ctable);
  free($3);
  free($5);
  kaisuucount1=0;
  hcount1=0;
  bodycount=0;
  printf("Translate: %s\n",$1);
}
                 ;
Head             : HHTerm
{ 
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
  bodycount++;
}
                 | Atom OP HHTerm
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  bodycount++;
}
                 ;
CHead            : CHHTerm
{ 
/*  printf("CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
  bodycount++;
}
                 | CBRSAtom OP CHHTerm
{ 
/*  printf("CBRSAtom OP CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  bodycount++;
}
                 | CBRAtom OP CHHTerm
{ 
/*  printf("CBRAtom OP CHHTerm-%s\n",$1);*/
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  bodycount++;
}

                 ;
Body             : HTerm
{ 
  yyval.string13 = malloc(strlen($1)+6);
  strcpy($$,"{[],");
  strcat($$,$1);
  strcat($$,"}");
  free($1);
}
                 | Atom OP HTerm
{ 
  yyval.string13 = malloc(strlen($3)+6);
  strcpy($$,"{[],");
  strcat($$,$3);
  strcat($$,"}");
  free($3);
}
                 | Body IP HTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($3)+7);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$3);
  strcat($$,"}");
  free($1);
  free($3);
}
                 | Body IP Atom OP HTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($5)+7);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$5);
  strcat($$,"}");
  free($1);
  free($5);
}
                 ;
RBody             : RHTerm
{ 
  yyval.string13 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
}
                 | Atom OP RHTerm
{ yyval.string13 =malloc(strlen($3) +1);
  strcpy($$,$3);
  free($3);
}
                 | RBody IP RHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($3)+2);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,$3);
  free($1);
  free($3);
}
                 | RBody IP Atom OP RHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($5) +2);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,$5);
  free($1);
  free($5);
}
                 ;

CRBody           : CBuiltin
{
  yyval.string13 = malloc(strlen($1));
  strcpy($$,$1);
  free($1);
}
                 | CRBody IP CBuiltin
{ 
  yyval.string13 = malloc(strlen($1)+strlen($3)+2);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,$3);
  free($1);
  free($3);
}
                 | CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+8);
  strcpy($$,"{[],");
  strcat($$,$1);
  strcat($$,",0}");
  free($1);
}
                 | CBRAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($3)+8);
  strcpy($$,"{[],");
  strcat($$,$3);
  strcat($$,",0}");
  free($3);
}
                 | CBRSAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($3)+8);
  strcpy($$,"{[],");
  strcat($$,$3);
  strcat($$,",0}");
  free($3);
}
                 | BBB CHTerm
{ 
  yyval.string13 = malloc(strlen($2)+8);
  strcpy($$,"{[],");
  strcat($$,$2);
  strcat($$,",1}");
  free($2);
}
                 | BBB CBRAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($4)+8);
  strcpy($$,"{[],");
  strcat($$,$4);
  strcat($$,",1}");
  free($4);
}
                 | BBB CBRSAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($4)+8);
  strcpy($$,"{[],");
  strcat($$,$4);
  strcat($$,",1}");
  free($4);
}
                 | CRBody IP CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($3)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$3);
  strcat($$,",0}");
  free($1);
  free($3);
}
                 | CRBody IP CBRAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($5)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$5);
  strcat($$,",0}");
  free($1);
  free($5);
}
                 | CRBody IP CBRSAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($5)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$5);
  strcat($$,",0}");
  free($1);
  free($5);
}
                 | CRBody IP BBB CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($4)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$4);
  strcat($$,",1}");
  free($1);
  free($4);
}
                 | CRBody IP BBB CBRAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($6)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$6);
  strcat($$,",1}");
  free($1);
  free($6);
}
                 | CRBody IP BBB CBRSAtom OP CHTerm
{ 
  yyval.string13 = malloc(strlen($1)+strlen($6)+9);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"{[],");
  strcat($$,$6);
  strcat($$,",1}");
  free($1);
  free($6);
}
                 ;
RuleEx           : Rulek
{ 
  yyval.string12 = malloc(strlen($1) +1);
  strcpy($$,$1);
  free($1);
}
                 ;
Rulek            : Variable
{ 
  AppendNet0(&vtable,$1,dum);
  yyval.string12 = malloc(strlen(dum)+1);
  strcpy($$,dum);
}
                 | WK Atom WK
{ 
  yyval.string12 = malloc(strlen($2)+3);
  strcpy($$,"\"");
  strcat($$,$2);
  strcat($$,"\"");
}
                 | Rulek Variable
{ 
/* 
  yyval.string12 = malloc(strlen($1)+strlen(dum)+1);
  strcpy($$,$1);
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);
*/
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen($1)+strlen(dum)+2); 
  strcpy($$,$1);
  strcat($$,",");
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);

}
                 | Rulek WK Atom WK
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

  yyval.string12 = malloc(strlen($1)+strlen($3)+4);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"\"");
  strcat($$,$3);
  strcat($$,"\"");
  free($1);

}
                 | CBRVariable
{ 
  yyval.string12 = malloc(strlen(dum)+1);
  AppendNet0(&vtable,$1,dum);
  strcpy($$,dum);
}
                 | WK CBRAtom WK
{ yyval.string12 = malloc(strlen($2)+3);
  strcpy($$,"\"");
  strcat($$,$2);
  strcat($$,"\"");
}
                 | Rulek CBRVariable
{ 
/*
  yyval.string12 = malloc(strlen($1)+strlen(dum)+1);
  strcpy($$,$1);
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);
*/ 
/* 1996/2/16 modify as following*/

  yyval.string12 = malloc(strlen($1)+strlen(dum)+2);
  strcpy($$,$1);
  strcat($$,",");
  AppendNet0(&vtable,$2,dum);
  strcat($$,dum);
  free($1);

}
                 | Rulek WK CBRAtom WK
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

  yyval.string12 = malloc(strlen($1)+strlen($3)+4);
  strcpy($$,$1);
  strcat($$,",");
  strcat($$,"\"");
  strcat($$,$3);
  strcat($$,"\"");
  free($1);

}
                 ;
HHTerm  : Predicate LP kaku RP BP HtermMaker
{ 
  char *newstring;
  newstring = malloc(strlen($1)+strlen($3)+28);
  htmake($1,$3,newstring);
  free($3);
  AppendhNet1(&htable,$6,newstring,string);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | Predicate LP kaku RP BP SHMaker
{ 
  char *newstring,*newstring2;
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring);
  newstring2 = malloc(strlen(newstring)+32);
  scolmake(newstring,newstring2);
  AppendsNet1(&stable,$6,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring2);
  free($3);
  free(newstring);
  free(newstring2);
}
        | MPredicate LP kaku RP
{ 
  char *newstring;
  newstring = malloc(strlen($1)+strlen($3)+12);
  htmake2($1,$3,newstring); 
  free($3);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy($$,newstring);
  free(newstring);
}
        | Predicate LP kaku RP
{ 
  char *newstring;
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring);
  free($3);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy($$,newstring);
  free(newstring);
}
        | error LP kaku RP BP HtermMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  yyerrok;}
        | error LP kaku RP BP SHMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  yyerrok;
}
        | error LP kaku RP
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  yyerrok;
}
        | HtermMaker
{
  AppendhNet1(&htable,$1,$1,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | SHMaker
{ 
  char *newstring;
  stabletake(&stable,$1);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy($$,newstring3);
  free(newstring3);
}
        ;
CHHTerm  : CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker
{ 
  char *newstring,*newstring2;
/*  printf("CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker\n");*/
  newstring = malloc(strlen($1)+strlen($3)+28);
  htmake($1,$3,newstring);
  newstring2 = malloc(strlen($1)+strlen($3)+28);
  predtake(newstring,newstring2);
  AppendhNet1(&htable,$6,newstring2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
  free(newstring);
  free(newstring2);
  free($3);
}
        | CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker
{ char *newstring,*newstring2,*newstring0;
/*  printf("CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker\n");*/
  stmake2($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  newstring2 = malloc(strlen(nstring)+strlen($3)+28);
  newstring0 = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring);
  scolmake(newstring,newstring2);
  predtake(newstring2,newstring0);
  AppendsNet1(&stable,$6,newstring0);
  yyval.string12 = malloc(strlen(newstring0)+1);
  strcpy($$,newstring0);
  free(newstring);
  free(newstring2);
  free(newstring0);
  free($3);
}
        | CMPredicate CBRLP Ckaku CBRRP
{ 
  char *newstring,*newstring2;
/*  printf("CMPredicate CBRLP Ckaku CBRRP\n");*/
  newstring = malloc(strlen($1)+strlen($3)+12);
  htmake2($1,$3,newstring); 
  newstring2 = malloc(strlen($1)+strlen($3)+12);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring2);
  free(newstring);
  free(newstring2);
  free($3);
}
        | CPredicate CBRLP Ckaku CBRRP
{ 
  char *newstring,*newstring2;
/*  printf("CPredicate CBRLP Ckaku CBRRP%s-%s\n",$1,$3);*/
  stmake2($1,nstring);
/*  printf("input: %s\n",$1);
  printf("nstring: %s\n",nstring);*/
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring); 
  newstring2 = malloc(strlen($1)+strlen($3)+28);


  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring2);
  free(newstring);
  free(newstring2);
  free($3);
}
        | error CBRLP Ckaku CBRRP BP CBRHtermMaker
{ 
/*  printf("error CBRLP Ckaku CBRRP BP CBRHtermMaker\n");*/
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | error CBRLP Ckaku CBRRP BP CBRSHMaker
{ 
/*  printf("error CBRLP Ckaku CBRRP BP CBRSHMaker\n");*/
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | error CBRLP Ckaku CBRRP
{ 
/*  printf("error CBRLP Ckaku CBRRP\n");*/
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | CBRHtermMaker
{ 
/*  printf("(CBRHtermMaker)%s\n",$1);*/
  AppendhNet1(&htable,$1,$1,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | CBRSHMaker
{ 
/*  printf("(CBRSHMaker)%s\n",$1);*/
  stabletake(&stable,$1);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy($$,newstring3);
  free(newstring3);
}
         ;
HTerm  : Predicate LP kaku RP BP HtermMaker
{ 
  char *newstring;
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  free($3);
  AppendhNet1(&htable,$6,newstring,string);
  free(newstring);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | Predicate LP kaku RP BP SHMaker
{ 
  char *newstring,*newstring2;
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring);
  free($3);
  newstring2 = malloc(strlen(newstring)+32);
  scolmake(newstring,newstring2);
  free(newstring);
  AppendsNet1(&stable,$6,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring);
  free(newstring2);
}
        | MPredicate LP kaku RP
{ 
  char *newstring;
  newstring = malloc(strlen($1)+strlen($3)+12);
  htmake2($1,$3,newstring);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy($$,newstring);
  free(newstring);
  free($3);
}
        | Predicate LP kaku RP
{ 
  char *newstring;
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  yyval.string12 = malloc(strlen(newstring)+1);
  strcpy($$,newstring);
  free(newstring);
  free($3);
}
        | error LP kaku RP BP HtermMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | error LP kaku RP BP SHMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | error LP kaku RP
{ 
  yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
        | HtermMaker
{ 
  AppendhNet1(&htable,$1,$1,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | SHMaker
{
  stabletake(&stable,$1);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy($$,newstring3);
  free(newstring3);
}
        ;

CHTerm  : CPredicate CBRLP Ckaku CBRRP BP CBRHtermMaker
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  newstring2 = malloc(strlen($1)+strlen($3)+13);
  predtake(newstring,newstring2);
  AppendhNet1(&htable,$6,newstring2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
  free(newstring);
  free(newstring2);
  free($3);
}
        | CPredicate CBRLP Ckaku CBRRP BP CBRSHMaker
{ 
  char *newstring,*newstring2,*newstring0;
  stmake1($1,nstring);
  newstring = malloc(strlen(nstring)+strlen($3)+28);
  htmake(nstring,$3,newstring);
  newstring2 = malloc(strlen(nstring)+strlen($3)+28);
  newstring0 = malloc(strlen(nstring)+strlen($3)+28); /* 1995-9-14 add */
  scolmake(newstring,newstring2);
  predtake(newstring2,newstring0);
  AppendsNet1(&stable,$6,newstring0);
  yyval.string12 = malloc(strlen(newstring0)+1);
  strcpy($$,newstring0);
  free(newstring);
  free(newstring2);
  free(newstring0);
  free($3);
}
        | CMPredicate CBRLP Ckaku CBRRP
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake2($1,$3,newstring);
  newstring2 = malloc(strlen($1)+strlen($3)+13);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring2);
  free(newstring);
  free(newstring2);
  free($3);
}
        | CPredicate CBRLP Ckaku CBRRP
{ 
  char *newstring,*newstring2;
  newstring = malloc(strlen($1)+strlen($3)+13);
  htmake1($1,$3,newstring);
  newstring2 = malloc(strlen($1)+strlen($3)+13);
  predtake(newstring,newstring2);
  yyval.string12 = malloc(strlen(newstring2)+1);
  strcpy($$,newstring2);
  free(newstring);
  free(newstring2);
  free($3);
}
        | error CBRLP Ckaku CBRRP BP CBRHtermMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  free($3);
  yyerrok;}
        | error CBRLP Ckaku CBRRP BP CBRSHMaker
{ 
  yyval.string12 = malloc(strlen($3)+1);
  free($3);
  yyerrok;}
        | error CBRLP Ckaku CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+1);
  free($3);
  yyerrok;}
        | CBRHtermMaker
{ 
  AppendhNet1(&htable,$1,$1,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
        | CBRSHMaker
{ 
  stabletake(&stable,$1);
  yyval.string12 = malloc(strlen(newstring3)+1);
  strcpy($$,newstring3);
  free(newstring3);
}
        ;

MPredicate : MIP Predicate
{ strcpy($$,$2);
}
           ;
CMPredicate : MIP CPredicate
{ strcpy($$,$2);
}
           ;
RHTerm  : HTerm
{ 
  yyval.string12 = malloc(strlen($1)+6);
  strcpy($$,"{[],");
  strcat($$,$1);
  strcat($$,"}");
  free($1);
}
        | Not HTerm
{ 
  yyval.string12 = malloc(strlen($2)+7);
  strcpy($$,"{not,");
  strcat($$,$2);
  strcat($$,"}");
  free($2);
}
        | Builtin
{
  strcpy($$,$1);
}
  ;

Builtin          :  LESS LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+9);
  strcpy($$,"{less,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | GREATER LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+12);
  strcpy($$,"{greater,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | EQUAL LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+10);
  strcpy($$,"{equal,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | NOTEQUAL LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+14);
  strcpy($$,"{not_equal,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | SAME LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+9);
  strcpy($$,"{same,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | DIFFERENT LP PTermWithoutLimit IP PTermWithoutLimit RP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+14);
  strcpy($$,"{different,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
        ;

CBuiltin          :  LESS CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+9);
  strcpy($$,"{less,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | GREATER CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+12);
  strcpy($$,"{greater,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | EQUAL CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+10);
  strcpy($$,"{equal,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | NOTEQUAL CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+14);
  strcpy($$,"{not_equal,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | SAME CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+9);
  strcpy($$,"{same,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
                 | DIFFERENT CBRLP PTermWithoutLimit IP PTermWithoutLimit CBRRP
{ 
  yyval.string12 = malloc(strlen($3)+strlen($5)+14);
  strcpy($$,"{different,");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($3);
  free($5);
}
        ;

kaku      : 
{ yyval.string12 = malloc(8);
  strcpy($$,"");}
          | KName EP Term
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+4);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",");
  strcat($$,$3);
  strcat($$,"}");
  free($3);
}
          | error EP Term
{ yyval.string12 = malloc(strlen($3)+1);
  strcpy($$,$3);
  free($3);
  yyerrok;}
          | kaku IP KName EP Term 
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+strlen($5)+5);
  strcpy($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  strcat($$,"}");
  free($1);
  free($5);
}
          ;
Ckaku     : /* empty */
{ 
  yyval.string12 = malloc(8);
  strcpy($$,"");
}
          | CKName CBREP Term
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+6);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",");
  strcat($$,$3);
  free($3);
  if(bodycount == 0){
    strcat($$,"}");}
  else{
    strcat($$,",0}");}
}
          | error CBREP Term
{ 
  yyval.string12 = malloc(strlen($3) +1);
  strcpy($$,$3);
  free($3);
  yyerrok;
}
          | error CBREP BBB Term
{ 
  yyval.string12 = malloc(strlen($4) +1);
  strcpy($$,$4);
  free($4);
  yyerrok;
}
          | CKName CBREP BBB Term
{ 
  yyval.string12 = malloc(strlen($1)+strlen($4)+6);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",");
  strcat($$,$4);
  strcat($$,",1}");
  free($4);
}
          | Ckaku IP CKName CBREP Term
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+strlen($5)+7);
  strcpy($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$5);
  free($5);
  free($1);
  if(bodycount == 0){
    strcat($$,"}");}
  else{
    strcat($$,",0}");}
}
          | Ckaku IP CKName CBREP BBB Term
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+strlen($6)+7);
  strcpy($$,$1);
  strcat($$,",{");
  strcat($$,$3);
  strcat($$,",");
  strcat($$,$6);
  strcat($$,",1}");
  free($1);
  free($6);
}
          ;
Term      : PTerm
{ 
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
}
          | HTerm
{ 
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
}
          | CHTerm
{ 
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
  free($1);
}
          ;
Predicate : NAtom
{ 
  makeAtom($$,$1);
}
          | Some Atoms
{ 
/*  
  someAtomMake($2,$$);
*/
  yyerror("!trans","Not support some operator");
}
          | NAtom AttributeS   
{
  makeAtom1($$,$1,$2);
}
          | Some NAtom AttributeS   
{
/*
  someAtomMake1($2,$3,$$);
*/
  yyerror("!trans","Not support some operator");
}
          | Variable
{ 
  strcpy(string2,"0");
  AppendNet1(&vtable,$1,string2,string);
  strcpy($$,string);
}
          | Variable DIP NAtom
{ 
  char dummy2[512];
  makeAtom(dummy2,$3);
  AppendNet1(&vtable,$1,dummy2,string);
  strcpy($$,string);
}
          |Variable DIP Some NAtom
{ 
/*
  someAtomMake($4,nstring);
  AppendNet1(&vtable,$1,nstring,string);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
}
          | Variable DIP NAtom AttributeS   
{
  char dummy[512];
  makeAtom1(dummy,$3,$4);
  AppendNet1(&vtable,$1,dummy,string);
  strcpy($$,string);
}
          | Variable DIP Some NAtom AttributeS   
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
}         
          ;
CPredicate : CBRSSAtom
{ 
/*  printf("CBRSSAtom %s\n",$1);*/
  makeAtom(dummy,$1);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  strcat($$,dummy);
  strcat($$,">");
/*  printf("CBRSSAtom %s\n",$$);*/
}
           | Some CBRSSAtom
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
}
           | CBRSSAtom AttributeS
{ 
/*  printf("CBRSSAtom AttributeS %s-%s\n",$1,$2);*/
  makeAtom1(dummy,$1,$2);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  strcat($$,dummy);
  strcat($$,">");
}
           | Some CBRSSAtom AttributeS
{
  yyerror("!trans","Not support some operator");
}
           | CBRVariable
{
  cbrVamake3($1,$$);
}
           | CBRVariable DIP CBRSSAtom
{ 
/*  printf("CBRVariable DIP CBRSSAtom %s-%s\n",$1,$3);*/
  cbrVamake($1,$3,$$);
}
           | CBRVariable DIP Some CBRSSAtom
{ 
/*
  cbrVaSmake($1,$4,$$);
*/
  yyerror("!trans","Not support some operator");
}
           | CBRVariable DIP CBRSSAtom AttributeS
{ 
/*  printf("CBRVariable DIP CBRSSAtom AttributeS %s-%s\n",$3,$4);*/
  cbrVamake4($1,$3,$4,$$);
}
           | CBRVariable DIP Some CBRSSAtom AttributeS
{ 
  yyerror("!trans","Not support some operator");
}
           | CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  char str[512];

  memset(str,0,512);
  bunkatu($3,str);

  makeAtom(dummy,$1);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  strcat($$,str);
  strcat($$,">");
}
           | CBRSSAtom RGP TOP LGP
{ strcpy($$,"<");
  makeAtom(dummy,$1);
  strcat($$,dummy);
  strcat($$,",0>");
}
           | Some CBRSSAtom RGP CBRPTermWithoutLimit LGP
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
}
           | Some CBRSSAtom RGP TOP LGP
{ 
/*
  someAtomMake($2,string);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",0>");
*/
  yyerror("!trans","Not support some operator");
}
           | CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{
  char str[512];

  memset(str,0,512);
  bunkatu($4,str);
  strcpy($$,"<{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"},");
  strcat($$,str);
  strcat($$,">");
}
           | CBRSSAtom AttributeS RGP TOP LGP
{
  strcpy($$,"<{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"},0>");
}
           | Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{
  yyerror("!trans","Not support some operator");
}
           | Some CBRSSAtom AttributeS RGP TOP LGP
{
  yyerror("!trans","Not support some operator");
}
           | CBRVariable DIP CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  cbrVamake2($1,$3,$5,$$);
}
           | CBRVariable DIP CBRSSAtom RGP TOP LGP
{ 
  cbrVamakeT($1,$3,$$);
}
           | CBRVariable DIP Some CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  yyerror("!trans","Not support some operator");
}
           | CBRVariable DIP Some CBRSSAtom RGP TOP LGP
{ 
  yyerror("!trans","Not support some operator");
}
           | CBRVariable DIP CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{ 
  cbrVamake41($1,$3,$4,$6,$$);
}
           | CBRVariable DIP CBRSSAtom AttributeS RGP TOP LGP
{ 
  cbrVamake4T($1,$3,$4,$$);
}
           | CBRVariable DIP Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{ 
  yyerror("!trans","Not support some operator");
}
           | CBRVariable DIP Some CBRSSAtom AttributeS RGP TOP LGP
{ 
  yyerror("!trans","Not support some operator");
}
          ;

PTerm     : RBRPTerm
          | CBRPTerm
          ;

PTermWithoutLimit : CBRPTermWithoutLimit
{
  char str[512];

  memset(str,0,512);
  bunkatu($1,str);
  strcpy($$,str);
}
          | RBRPTerm
          ;

RBRPTerm  : Atoms
{ 
  yyval.string12 = malloc(strlen($1)+1);
  strcpy($$,$1);
}
          | Some NAtom
{ 
/*
  someAtomMake($2,dummy);
  yyval.string12 = malloc(strlen(dummy)+1);
  strcpy(yyval.string12,dummy);
*/
  yyerror("!trans","Not support some operator");

}
          | NAtom AttributeS
{ 
  yyval.string12 = malloc(strlen($1)+strlen($2)+6);
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"}");
  free($2);
}
          | Some NAtom AttributeS
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
}
          | Variable
{ 
  strcpy(string2,"0");
  AppendNet1(&vtable,$1,string2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          | Variable DIP NAtom
{ 
  char dummy2[512];
  makeAtom(dummy2,$3);
  AppendNet1(&vtable,$1,dummy2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          | Variable DIP Some NAtom        
{ 
  yyerror("!trans","Not support some operator");
}
          | Variable DIP NAtom AttributeS
{ 
  char *newstring;
  newstring = malloc(strlen($3)+strlen($4)+6);
  strcpy(newstring,"{");
  strcat(newstring,$3);
  strcat(newstring,",0,");
  strcat(newstring,$4);
  strcat(newstring,"}");
  AppendNet1(&vtable,$1,newstring,string);
  free(newstring);
  free($4);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          |Variable DIP Some NAtom AttributeS
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
}
          | WK Atom WK
{ 
  yyval.string12 = malloc(strlen($2)+10);
  strcpy($$,"{\"");
  strcat($$,$2);
  strcat($$,"\",0,[]}");
}
         | WK Variable WK
{
  yyval.string12 = malloc(strlen($2)+10);
  strcpy($$,"{\"");
  strcat($$,$2);
  strcat($$,"\",0,[]}");
}
          | Variable DIP WK Atom WK
{ 
  char dummy2[512];
  strcpy(dummy2,"{\"");
  strcat(dummy2,$4);
  strcat(dummy2,"\",0,[]}");
  AppendNet1(&vtable,$1,dummy2,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          ;

CBRPTerm  : CBRPTermWithoutLimit
          | CBRPTermWithLimit
          ;

CBRPTermWithoutLimit : CBRSSAtom
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
  makeAtom(dummy,$1);
  yyval.string12 = malloc(strlen(dummy)+strlen(dummy)+4);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  strcat($$,dummy);
  strcat($$,">");
}
          | Some CBRSSAtom    
{
  yyerror("!trans","Not support some operator");
}
          | CBRSSAtom AttributeS
{ 
  yyval.string12 = malloc(strlen($1)+strlen($1)+
			  strlen($2)+strlen($2)+14);
  strcpy($$,"<{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"},{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"}>");
  free($2);
}
          | Some CBRSSAtom AttributeS 
{
  yyerror("!trans","Not support some operator");
}
          | CBRVariable
{ 
  cbrVamake3($1,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          | CBRVariable DIP CBRSSAtom
{ 
  cbrVamake($1,$3,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          |CBRVariable DIP Some CBRSSAtom
{ 
/*
  cbrVaSmake($1,$4,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
}
          | CBRVariable DIP CBRSSAtom AttributeS
{ 
  cbrVamake4($1,$3,$4,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($4);
  strcpy($$,string);
}
          | CBRVariable DIP Some CBRSSAtom AttributeS
{ 
/*
  cbrVaSmake3($1,$4,$5,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
}
          | WK CBRAtom WK
{ 
  yyval.string12 = malloc(strlen($2)+10);
  strcpy($$,"{\"");
  strcat($$,$2);
  strcat($$,"\",0,[]}");
}
         | WK CBRVariable WK
{
  yyval.string12 = malloc(strlen($2)+10);
  strcpy($$,"{\"");
  strcat($$,$2);
  strcat($$,"\",0,[]}");
}
          | CBRVariable DIP WK CBRAtom WK
{ 
  char dummy2[512];
  strcpy(dummy2,"{\"");
  strcat(dummy2,$4);
  strcat(dummy2,"\",0,[]}");
  AppendNet1(&vtable,$1,dummy2,string);
  AppendCNet1(&ctable,$1,dummy2);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
	  ;

CBRPTermWithLimit : CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  char str[512];

  memset(str,0,512);
  bunkatu($3,str);

  makeAtom(dummy,$1);
  yyval.string12 = malloc(strlen(dummy)+strlen(str)+4);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",");
  strcat($$,str);
  strcat($$,">");
}
           | CBRSSAtom RGP TOP LGP
{ 
  makeAtom(dummy,$1);
  yyval.string12 = malloc(strlen(dummy)+5);
  strcpy($$,"<");
  strcat($$,dummy);
  strcat($$,",0>");
}
           | Some CBRSSAtom RGP CBRPTermWithoutLimit LGP
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
}
           | Some CBRSSAtom RGP TOP LGP
{ 
/*  someAtomMake($2,string);
  yyval.string12 = malloc(strlen(string)+5);
  strcpy($$,"<");
  strcat($$,string);
  strcat($$,",0>");
*/
  yyerror("!trans","Not support some operator");
}
          | CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{ 
  char str[512];

  memset(str,0,512);
  bunkatu($4,str);

  yyval.string12 = malloc(strlen($1)+strlen($2)+strlen(str)+9);
  strcpy($$,"<{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"},");
  strcat($$,str);
  strcat($$,">");
  free($2);
}
          | CBRSSAtom AttributeS RGP TOP LGP
{ 
  yyval.string12 = malloc(strlen($1)+strlen($2)+10);
  strcpy($$,"<{");
  strcat($$,$1);
  strcat($$,",0,");
  strcat($$,$2);
  strcat($$,"},0>");
  free($2);
}
         |CBRVariable DIP CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  cbrVamake2($1,$3,$5,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
          | CBRVariable DIP CBRSSAtom RGP TOP LGP
{ 
  cbrVamakeT($1,$3,string);
  yyval.string12 = malloc(strlen(string)+1);
  strcpy($$,string);
}
         |CBRVariable DIP Some CBRSSAtom RGP CBRPTermWithoutLimit LGP
{ 
  yyerror("!trans","Not support some operator");
}
         |CBRVariable DIP Some CBRSSAtom RGP TOP LGP
{ 
  yyerror("!trans","Not support some operator");
}
          | CBRVariable DIP CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{ 
  cbrVamake41($1,$3,$4,$6,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($4);
  strcpy($$,string);
}
          | CBRVariable DIP CBRSSAtom AttributeS RGP TOP LGP
{ 
  cbrVamake4T($1,$3,$4,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($4);
  strcpy($$,string);
}
          | CBRVariable DIP Some CBRSSAtom AttributeS RGP CBRPTermWithoutLimit LGP
{ 
/*
  cbrVaSmake4($1,$4,$5,$7,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
}
          | CBRVariable DIP Some CBRSSAtom AttributeS RGP TOP LGP
{ 
/*
  cbrVaSmake4T($1,$4,$5,string);
  yyval.string12 = malloc(strlen(string)+1);
  free($5);
  strcpy($$,string);
*/
  yyerror("!trans","Not support some operator");
}
           ;

Attri    : Atom NP RBRPTerm
{ 
  yyval.string12 = malloc(strlen($1)+strlen($3)+6);
  strcpy($$,"{\"");
  strcat($$,$1);
  strcat($$,"\",");
  strcat($$,$3);
  strcat($$,"}");
  free($3);
}
         | Attri IP Atom NP RBRPTerm
{ 
  yyval.string12 = malloc(strlen($3)+strlen($1)+strlen($5)+7);
  strcpy($$,$1);
  strcat($$,",{\"");
  strcat($$,$3);
  strcat($$,"\",");
  strcat($$,$5);
  strcat($$,"}");
  free($1);
  free($5);
}
         | CBRAtom NP CBRPTermWithoutLimit
{ 
  char str[512];

  memset(str,0,512);
  bunkatu($3,str);
  yyval.string12 = malloc(strlen($1)+strlen(str)+8);

  strcpy($$,"{\"");
  strcat($$,$1);
  strcat($$,"\",");
  strcat($$,str);
  strcat($$,"}");
  free($3);
}

         | Attri IP CBRAtom NP CBRPTermWithoutLimit
{ 
  char str[512];

  memset(str,0,512);
  bunkatu($5,str);

  yyval.string12 = malloc(strlen($1)+strlen($3)+strlen(str)+9);
  strcpy($$,$1);
  strcat($$,",{\"");
  strcat($$,$3);
  strcat($$,"\",");
  strcat($$,str);
  strcat($$,"}");
  free($1);
  free($5);

}
          ;

AttributeS : KLP Attri KRP
{ 
  yyval.string12 = malloc(strlen($2)+3);
  strcpy($$,"[");
  strcat($$,$2);
  strcat($$,"]");
  free($2);
}
          ;
Atoms     : NAtom
{ 
  makeAtom($$,$1);
}

          ;
NAtom     : Atom
{ 
  strcpy($$,"'");
  strcat($$,$1);
  strcat($$,"'");
}
          | SAtom
{ 
  strcpy($$,$1);
}
          | Number
{ 
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,"}");
}
          | NumberDomain
{ 
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  numtake($1,number1,number2);
  strcpy($$,"{{");
  strcat($$,number1);
  strcat($$,"},{");
  strcat($$,number2);
  strcat($$,"}}");
}
          ;
CBRSSAtom : CBRAtom
{ 
  strcpy($$,"'");
  strcat($$,$1);
  strcat($$,"'");
}
         |  CBRSAtom
{ 
  strcpy($$,$1);
}
          | CBRNumber
{ 
  strcpy($$,"{");
  strcat($$,$1);
  strcat($$,"}");
}
          | CBRNumberDomain
{ 
  char number1[512],number2[512];
  memset(number1,0,512);
  memset(number2,0,512);
  numtake($1,number1,number2);
  strcpy($$,"{{");
  strcat($$,number1);
  strcat($$,"},{");
  strcat($$,number2);
  strcat($$,"}}");
}
         ;
%%
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



