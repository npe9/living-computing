#include <stdio.h>
# define U(x) x
# define NLSTATE yyprevious=YYNEWLINE
# define BEGIN yybgin = yysvec + 1 +
# define INITIAL 0
# define YYLERR yysvec
# define YYSTATE (yyestate-yysvec-1)
# define YYOPTIM 1
# define YYLMAX BUFSIZ
#define output(c) putc(c,yyout)
#define input() (((yytchar=yysptr>yysbuf?U(*--yysptr):getc(yyin))==10?(yylineno++,yytchar):yytchar)==EOF?0:yytchar)
#define ECHO fprintf(yyout, "%s",yytext)
# define REJECT { nstr = yyreject(); goto yyfussy;}
int yyleng; extern char yytext[];
extern char *yysptr, yysbuf[];
# define unput(c) {yytchar= (c);if(yytchar=='\n')yylineno--;*yysptr++=yytchar;}
# define yymore() (yymorfg=1)
int yymorfg;
int yytchar;
FILE *yyin = {stdin}, *yyout = {stdout};
extern int yylineno;
struct yysvf { 
	struct yywork *yystoff;
	struct yysvf *yyother;
	int *yystops;};
struct yysvf *yyestate;
extern struct yysvf yysvec[], *yybgin;
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
#include "y_tab.h"
#include "rgtrans.h"
#include <stddef.h>
#include <stdio.h>
extern int kanmachecknumber;
extern int goalstate;
int kaigyounumber=0;
int attributecount=0;
char origstring[STRINGSIZE];
char dummy[64];
# define RBRRULE 2
# define CBRRULE 4
# define GOAL 6
# define YYNEWLINE 10
yylex(){
int nstr; extern int yyprevious;
while((nstr = yylook()) >= 0)
yyfussy: switch(nstr){
case 0:
if(yywrap()) return(0); break;
case 1:
    { 
          if(goalstate == 1){
          strcat(origstring,"(");
          }
          strcpy(yylval.string11,yytext);
          return(LP);}
break;
case 2:
    { 
          if(goalstate == 1){
          strcat(origstring,")");
          }
          strcpy(yylval.string11,yytext);
          return(RP);}
break;
case 3:
    { strcpy(yylval.string11,yytext);
          return(CBRLP);}
break;
case 4:
    { strcpy(yylval.string11,yytext);
          return(CBRRP);}
break;
case 5:
    { 
          strcpy(yylval.string11,yytext);
          return(TRP);}
break;
case 6:
    { 
          if(goalstate == 1){
            strcat(origstring,",");
          }
          strcpy(yylval.string11,yytext);
          return(TLP);}
break;
case 7:
    { 
          if(goalstate == 1){
          strcat(origstring,"/");
          }
          strcpy(yylval.string11,yytext);
          return(DIP);}
break;
case 8:
    { 
          if(goalstate == 1){
          strcat(origstring,":");
          }
          strcpy(yylval.string11,yytext);
          return(OP);}
break;
case 9:
    { 
          if(goalstate == 1){
            strcat(origstring,",");
          }
          strcpy(yylval.string11,yytext);
          return(IP);}
break;
case 10:
    { 
          if(goalstate == 1){
          strcat(origstring,"=");
          }
          strcpy(yylval.string11,yytext);
          return(EP);}
break;
case 11:
    { strcpy(yylval.string11,yytext);
          return(CBREP);}
break;
case 12:
    { 
          if(goalstate == 1){
          strcat(origstring,"-");
          }
          strcpy(yylval.string11,yytext);
          return(MIP);}
break;
case 13:
    { 
          if(goalstate == 1){
          strcat(origstring,"<");
          }
          strcpy(yylval.string11,yytext);
          return(RGP);}
break;
case 14:
    { 
          if(goalstate == 1){
          strcat(origstring,">");
          }
          strcpy(yylval.string11,yytext);
          return(LGP);}
break;
case 15:
    { 
          if(goalstate == 1){
          strcat(origstring,"[");
          }
          strcpy(yylval.string11,yytext);
          return(KLP);}
break;
case 16:
    { 
          if(goalstate == 1){
          strcat(origstring,"]");
          }
          strcpy(yylval.string11,yytext);
          return(KRP);}
break;
case 17:
    { 
          if(goalstate == 1){
          strcat(origstring,"|");
          }
          strcpy(yylval.string11,yytext);
          return(BP);}
break;
case 18:
   { 
          if(goalstate == 1){
          strcat(origstring,"||");
          }
          strcpy(yylval.string11,yytext);
          return(BBP);}
break;
case 19:
   { 
          if(goalstate == 1){
          strcat(origstring,"+");
          }
          strcpy(yylval.string11,yytext);
          return(TOP);}
break;
case 20:
   { strcpy(yylval.string11,yytext);
          return(MP);}
break;
case 21:
   { 
          attributecount++;
          if(goalstate == 1){
          strcat(origstring,"=>");
          }
          strcpy(yylval.string11,yytext);
          return(NP);}
break;
case 22:
   { strcpy(yylval.string11,yytext);
          return(OPOP);}
break;
case 23:
    { strcpy(yylval.string11,yytext);
          return(BBB);}
break;
case 24:
  { 
          if(goalstate == 1){
          strcat(origstring,"agent");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 25:
 { 
          if(goalstate == 1){
          strcat(origstring,"object");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 26:
 { 
          if(goalstate == 1){
          strcat(origstring,"a_object");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 27:
  { 
          if(goalstate == 1){
          strcat(origstring,"cause");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 28:
{
          if(goalstate == 1){
          strcat(origstring,"condition");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 29:
{
          if(goalstate == 1){
          strcat(origstring,"purpose");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 30:
  {
          if(goalstate == 1){
          strcat(origstring,"place");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 31:
 { 
          if(goalstate == 1){
          strcat(origstring,"source");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 32:
   { 
          if(goalstate == 1){
          strcat(origstring,"goal");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 33:
   { 
          if(goalstate == 1){
          strcat(origstring,"time");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 34:
{ 
          if(goalstate == 1){
          strcat(origstring,"time_from");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 35:
  { 
          if(goalstate == 1){
          strcat(origstring,"time_to");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 36:
{ 
          if(goalstate == 1){
          strcat(origstring,"implement");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 37:
 { 
          if(goalstate == 1){
          strcat(origstring,"quantity");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 38:
 { 
          if(goalstate == 1){
          strcat(origstring,"number");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 39:
 { 
          if(goalstate == 1){
          strcat(origstring,"manner");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 40:
 { 
          if(goalstate == 1){
          strcat(origstring,"basis");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
break;
case 41:
  { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 42:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 43:
 { strcpy(yylval.string11,yytext);
            return(CKName);}
break;
case 44:
  { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 45:
{strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 46:
{strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 47:
  {strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 48:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 49:
   { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 50:
   { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 51:
{ strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 52:
  { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 53:
{ strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 54:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 55:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 56:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 57:
 { strcpy(yylval.string11,yytext);
          return(CKName);}
break;
case 58:
   { 
          if(goalstate == 1){
          strcat(origstring,"some");
          }
          strcpy(yylval.string11,yytext);
          return(Some);}
break;
case 59:
  { strcpy(yylval.string11,yytext);
          return(Not);}
break;
case 60:
   { if(goalstate == 1){
          strcat(origstring,"less");
          }
          strcpy(yylval.string11,yytext);
          return(LESS);}
break;
case 61:
{ if(goalstate == 1){
          strcat(origstring,"greater");
          }
          strcpy(yylval.string11,yytext);
          return(GREATER);}
break;
case 62:
  { if(goalstate == 1){
          strcat(origstring,"equal");
          }
          strcpy(yylval.string11,yytext);
          return(EQUAL);}
break;
case 63:
{ if(goalstate == 1){
            strcat(origstring,"not_equal");
            }
            strcpy(yylval.string11,yytext);
            return(NOTEQUAL);}
break;
case 64:
   { if(goalstate == 1){
          strcat(origstring,"same");
          }
          strcpy(yylval.string11,yytext);
          return(SAME);}
break;
case 65:
{ if(goalstate == 1){
            strcat(origstring,"different");
            }
            strcpy(yylval.string11,yytext);
            return(DIFFERENT);}
break;
case 66:
          { if(goalstate == 1){
                              return(DG);
                              }
                              else{
    fprintf(stderr,"%s\n","!trans-Illegal option : please  '-g' ");
      exit(1);
      }
    }
break;
case 67:
 { if(goalstate == 0){
                              return(DAR);
                              }
                              else{
   fprintf(stderr,"%s\n","!trans-Illegal option :  please  '-r' ");      
   exit(1);
      }
    }
break;
case 68:
      { return(DRR);}
break;
case 69:
      { BEGIN CBRRULE ;
                              return(DCR);}
break;
case 70:
  ;
break;
case 71:
  ;
break;
case 72:
   ;
break;
case 73:
  { kaigyounumber++;}
break;
case 74:
{ 
          if(goalstate == 1){
/*
          sprintf(dummy,"%s",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(Number);}
break;
case 75:
 { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%s",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(Variable);}
break;
case 76:
 { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
	  return(Variable);}
break;
case 77:
    { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(HtermMaker);}
break;
case 78:
    { 
          if(goalstate == 1){
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(SHMaker);}
break;
case 79:
  {
                                  strcpy(yylval.string11,yytext);
                                  return(CBRHtermMaker);}
break;
case 80:
  {
                                  strcpy(yylval.string11,yytext);
                                  return(CBRSHMaker);}
break;
case 81:
 { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
/*          printf("AtomAtom %s\n",yytext); */
          return(Atom);}
break;
case 82:
 { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          printf("AtomAtom2 %s\n",yytext);
          return(SAtom);}
break;
case 83:
{
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(NumberDomain);}
break;
case 84:
{
          strcpy(yylval.string11,yytext);
          return(CBRNumber);}
break;
case 85:
 { strcpy(yylval.string11,yytext);
               		     return(CBRVariable);}
break;
case 86:
 { strcpy(yylval.string11,yytext);
               		     return(CBRVariable);}
break;
case 87:
 { 
                                   strcpy(yylval.string11,yytext);
                		          return(CBRAtom);}
break;
case 88:
 { 
                                   strcpy(yylval.string11,yytext);
                                   return(CBRSAtom);}
break;
case 89:
{
          strcpy(yylval.string11,yytext);
          return(CBRNumberDomain);}
break;
case 90:
      {return (REnd);}
break;
case 91:
     { return(WK);}
break;
case 92:
     { kaigyounumber++;}
break;
case -1:
break;
default:
fprintf(yyout,"bad switch yylook %d",nstr);
} return(0); }
/* end of yylex */


int yyvstop[] = {
0,
/* actions for state 8 */
81,
0,
/* actions for state 9 */
71,
0,
/* actions for state 10 */
70,
0,
/* actions for state 11 */
92,
0,
/* actions for state 12 */
70,
71,
0,
/* actions for state 13 */
23,
0,
/* actions for state 14 */
91,
0,
/* actions for state 16 */
81,
0,
/* actions for state 17 */
81,
0,
/* actions for state 19 */
1,
0,
/* actions for state 20 */
2,
0,
/* actions for state 21 */
19,
81,
0,
/* actions for state 22 */
9,
0,
/* actions for state 23 */
12,
0,
/* actions for state 24 */
90,
0,
/* actions for state 25 */
7,
0,
/* actions for state 26 */
74,
81,
0,
/* actions for state 27 */
8,
0,
/* actions for state 28 */
13,
0,
/* actions for state 29 */
10,
0,
/* actions for state 30 */
14,
0,
/* actions for state 32 */
75,
81,
0,
/* actions for state 33 */
15,
0,
/* actions for state 34 */
72,
0,
/* actions for state 35 */
16,
0,
/* actions for state 36 */
76,
81,
0,
/* actions for state 37 */
81,
0,
/* actions for state 38 */
81,
0,
/* actions for state 39 */
81,
0,
/* actions for state 40 */
81,
0,
/* actions for state 41 */
81,
0,
/* actions for state 42 */
81,
0,
/* actions for state 43 */
81,
0,
/* actions for state 44 */
81,
0,
/* actions for state 45 */
81,
0,
/* actions for state 46 */
81,
0,
/* actions for state 47 */
81,
0,
/* actions for state 48 */
81,
0,
/* actions for state 49 */
81,
0,
/* actions for state 50 */
81,
0,
/* actions for state 51 */
81,
0,
/* actions for state 52 */
5,
0,
/* actions for state 53 */
17,
0,
/* actions for state 54 */
6,
0,
/* actions for state 57 */
19,
0,
/* actions for state 59 */
15,
0,
/* actions for state 66 */
87,
0,
/* actions for state 68 */
87,
0,
/* actions for state 69 */
87,
0,
/* actions for state 70 */
87,
0,
/* actions for state 71 */
3,
0,
/* actions for state 72 */
4,
0,
/* actions for state 73 */
19,
87,
0,
/* actions for state 74 */
84,
87,
0,
/* actions for state 75 */
11,
0,
/* actions for state 77 */
85,
87,
0,
/* actions for state 78 */
15,
0,
/* actions for state 79 */
86,
87,
0,
/* actions for state 80 */
87,
0,
/* actions for state 81 */
87,
0,
/* actions for state 82 */
87,
0,
/* actions for state 83 */
87,
0,
/* actions for state 84 */
87,
0,
/* actions for state 85 */
87,
0,
/* actions for state 86 */
87,
0,
/* actions for state 87 */
87,
0,
/* actions for state 88 */
87,
0,
/* actions for state 89 */
87,
0,
/* actions for state 90 */
87,
0,
/* actions for state 91 */
87,
0,
/* actions for state 92 */
87,
0,
/* actions for state 93 */
87,
0,
/* actions for state 94 */
87,
0,
/* actions for state 95 */
78,
0,
/* actions for state 96 */
81,
0,
/* actions for state 98 */
81,
0,
/* actions for state 100 */
22,
0,
/* actions for state 101 */
20,
0,
/* actions for state 102 */
21,
0,
/* actions for state 103 */
77,
0,
/* actions for state 105 */
81,
0,
/* actions for state 106 */
81,
0,
/* actions for state 107 */
81,
0,
/* actions for state 108 */
81,
0,
/* actions for state 109 */
81,
0,
/* actions for state 110 */
81,
0,
/* actions for state 111 */
81,
0,
/* actions for state 112 */
81,
0,
/* actions for state 113 */
81,
0,
/* actions for state 114 */
81,
0,
/* actions for state 115 */
81,
0,
/* actions for state 116 */
81,
0,
/* actions for state 117 */
81,
0,
/* actions for state 118 */
81,
0,
/* actions for state 119 */
81,
0,
/* actions for state 120 */
81,
0,
/* actions for state 121 */
81,
0,
/* actions for state 122 */
81,
0,
/* actions for state 123 */
81,
0,
/* actions for state 124 */
81,
0,
/* actions for state 125 */
81,
0,
/* actions for state 126 */
18,
0,
/* actions for state 135 */
80,
0,
/* actions for state 136 */
87,
0,
/* actions for state 137 */
87,
0,
/* actions for state 138 */
87,
0,
/* actions for state 140 */
79,
0,
/* actions for state 142 */
87,
0,
/* actions for state 143 */
87,
0,
/* actions for state 144 */
87,
0,
/* actions for state 145 */
87,
0,
/* actions for state 146 */
87,
0,
/* actions for state 147 */
87,
0,
/* actions for state 148 */
87,
0,
/* actions for state 149 */
87,
0,
/* actions for state 150 */
87,
0,
/* actions for state 151 */
87,
0,
/* actions for state 152 */
87,
0,
/* actions for state 153 */
87,
0,
/* actions for state 154 */
87,
0,
/* actions for state 155 */
87,
0,
/* actions for state 156 */
87,
0,
/* actions for state 157 */
87,
0,
/* actions for state 158 */
87,
0,
/* actions for state 159 */
87,
0,
/* actions for state 160 */
87,
0,
/* actions for state 161 */
87,
0,
/* actions for state 162 */
87,
0,
/* actions for state 163 */
73,
0,
/* actions for state 164 */
81,
0,
/* actions for state 165 */
82,
0,
/* actions for state 167 */
81,
0,
/* actions for state 168 */
81,
0,
/* actions for state 169 */
81,
0,
/* actions for state 170 */
81,
0,
/* actions for state 171 */
81,
0,
/* actions for state 172 */
81,
0,
/* actions for state 173 */
81,
0,
/* actions for state 174 */
81,
0,
/* actions for state 175 */
81,
0,
/* actions for state 176 */
81,
0,
/* actions for state 177 */
81,
0,
/* actions for state 178 */
81,
0,
/* actions for state 179 */
59,
81,
0,
/* actions for state 180 */
81,
0,
/* actions for state 181 */
81,
0,
/* actions for state 182 */
81,
0,
/* actions for state 183 */
81,
0,
/* actions for state 184 */
81,
0,
/* actions for state 185 */
81,
0,
/* actions for state 186 */
81,
0,
/* actions for state 187 */
81,
0,
/* actions for state 188 */
81,
0,
/* actions for state 194 */
59,
0,
/* actions for state 197 */
87,
0,
/* actions for state 198 */
87,
88,
0,
/* actions for state 199 */
88,
0,
/* actions for state 201 */
87,
0,
/* actions for state 202 */
87,
0,
/* actions for state 203 */
87,
0,
/* actions for state 204 */
87,
0,
/* actions for state 205 */
87,
0,
/* actions for state 206 */
87,
0,
/* actions for state 207 */
87,
0,
/* actions for state 208 */
87,
0,
/* actions for state 209 */
87,
0,
/* actions for state 210 */
87,
0,
/* actions for state 211 */
87,
0,
/* actions for state 212 */
87,
0,
/* actions for state 213 */
59,
87,
0,
/* actions for state 214 */
87,
0,
/* actions for state 215 */
87,
0,
/* actions for state 216 */
87,
0,
/* actions for state 217 */
87,
0,
/* actions for state 218 */
87,
0,
/* actions for state 219 */
87,
0,
/* actions for state 220 */
87,
0,
/* actions for state 221 */
87,
0,
/* actions for state 222 */
87,
0,
/* actions for state 223 */
81,
0,
/* actions for state 225 */
81,
0,
/* actions for state 226 */
81,
0,
/* actions for state 227 */
81,
0,
/* actions for state 228 */
81,
0,
/* actions for state 229 */
81,
0,
/* actions for state 230 */
81,
0,
/* actions for state 231 */
81,
0,
/* actions for state 232 */
32,
81,
0,
/* actions for state 233 */
81,
0,
/* actions for state 234 */
81,
0,
/* actions for state 235 */
60,
81,
0,
/* actions for state 236 */
81,
0,
/* actions for state 237 */
81,
0,
/* actions for state 238 */
81,
0,
/* actions for state 239 */
81,
0,
/* actions for state 240 */
81,
0,
/* actions for state 241 */
81,
0,
/* actions for state 242 */
81,
0,
/* actions for state 243 */
64,
81,
0,
/* actions for state 244 */
58,
81,
0,
/* actions for state 245 */
81,
0,
/* actions for state 246 */
33,
81,
0,
/* actions for state 251 */
60,
0,
/* actions for state 253 */
64,
0,
/* actions for state 254 */
58,
0,
/* actions for state 255 */
87,
0,
/* actions for state 257 */
87,
0,
/* actions for state 258 */
87,
0,
/* actions for state 259 */
87,
0,
/* actions for state 260 */
87,
0,
/* actions for state 261 */
87,
0,
/* actions for state 262 */
87,
0,
/* actions for state 263 */
87,
0,
/* actions for state 264 */
49,
87,
0,
/* actions for state 265 */
87,
0,
/* actions for state 266 */
87,
0,
/* actions for state 267 */
60,
87,
0,
/* actions for state 268 */
87,
0,
/* actions for state 269 */
87,
0,
/* actions for state 270 */
87,
0,
/* actions for state 271 */
87,
0,
/* actions for state 272 */
87,
0,
/* actions for state 273 */
87,
0,
/* actions for state 274 */
87,
0,
/* actions for state 275 */
64,
87,
0,
/* actions for state 276 */
58,
87,
0,
/* actions for state 277 */
87,
0,
/* actions for state 278 */
50,
87,
0,
/* actions for state 279 */
81,
0,
/* actions for state 281 */
81,
0,
/* actions for state 282 */
24,
81,
0,
/* actions for state 283 */
40,
81,
0,
/* actions for state 284 */
27,
81,
0,
/* actions for state 285 */
81,
0,
/* actions for state 286 */
81,
0,
/* actions for state 287 */
62,
81,
0,
/* actions for state 288 */
81,
0,
/* actions for state 289 */
81,
0,
/* actions for state 290 */
81,
0,
/* actions for state 291 */
81,
0,
/* actions for state 292 */
81,
0,
/* actions for state 293 */
81,
0,
/* actions for state 294 */
30,
81,
0,
/* actions for state 295 */
81,
0,
/* actions for state 296 */
81,
0,
/* actions for state 297 */
81,
0,
/* actions for state 298 */
81,
0,
/* actions for state 301 */
62,
0,
/* actions for state 304 */
87,
0,
/* actions for state 306 */
87,
0,
/* actions for state 307 */
41,
87,
0,
/* actions for state 308 */
57,
87,
0,
/* actions for state 309 */
44,
87,
0,
/* actions for state 310 */
87,
0,
/* actions for state 311 */
87,
0,
/* actions for state 312 */
62,
87,
0,
/* actions for state 313 */
87,
0,
/* actions for state 314 */
87,
0,
/* actions for state 315 */
87,
0,
/* actions for state 316 */
87,
0,
/* actions for state 317 */
87,
0,
/* actions for state 318 */
87,
0,
/* actions for state 319 */
47,
87,
0,
/* actions for state 320 */
87,
0,
/* actions for state 321 */
87,
0,
/* actions for state 322 */
87,
0,
/* actions for state 323 */
87,
0,
/* actions for state 324 */
81,
0,
/* actions for state 325 */
83,
0,
/* actions for state 326 */
81,
0,
/* actions for state 327 */
81,
0,
/* actions for state 328 */
81,
0,
/* actions for state 329 */
81,
0,
/* actions for state 330 */
81,
0,
/* actions for state 331 */
39,
81,
0,
/* actions for state 332 */
81,
0,
/* actions for state 333 */
38,
81,
0,
/* actions for state 334 */
25,
81,
0,
/* actions for state 335 */
81,
0,
/* actions for state 336 */
81,
0,
/* actions for state 337 */
31,
81,
0,
/* actions for state 338 */
81,
0,
/* actions for state 339 */
81,
0,
/* actions for state 344 */
87,
0,
/* actions for state 345 */
89,
0,
/* actions for state 346 */
87,
0,
/* actions for state 347 */
87,
0,
/* actions for state 348 */
87,
0,
/* actions for state 349 */
87,
0,
/* actions for state 350 */
87,
0,
/* actions for state 351 */
56,
87,
0,
/* actions for state 352 */
87,
0,
/* actions for state 353 */
55,
87,
0,
/* actions for state 354 */
42,
87,
0,
/* actions for state 355 */
87,
0,
/* actions for state 356 */
87,
0,
/* actions for state 357 */
48,
87,
0,
/* actions for state 358 */
87,
0,
/* actions for state 359 */
87,
0,
/* actions for state 360 */
81,
0,
/* actions for state 361 */
81,
0,
/* actions for state 362 */
81,
0,
/* actions for state 363 */
81,
0,
/* actions for state 364 */
61,
81,
0,
/* actions for state 365 */
81,
0,
/* actions for state 366 */
81,
0,
/* actions for state 367 */
29,
81,
0,
/* actions for state 368 */
81,
0,
/* actions for state 369 */
81,
0,
/* actions for state 370 */
35,
81,
0,
/* actions for state 373 */
61,
0,
/* actions for state 375 */
87,
0,
/* actions for state 376 */
87,
0,
/* actions for state 377 */
87,
0,
/* actions for state 378 */
87,
0,
/* actions for state 379 */
61,
87,
0,
/* actions for state 380 */
87,
0,
/* actions for state 381 */
87,
0,
/* actions for state 382 */
46,
87,
0,
/* actions for state 383 */
87,
0,
/* actions for state 384 */
87,
0,
/* actions for state 385 */
52,
87,
0,
/* actions for state 386 */
81,
0,
/* actions for state 387 */
26,
81,
0,
/* actions for state 388 */
81,
0,
/* actions for state 389 */
81,
0,
/* actions for state 390 */
81,
0,
/* actions for state 391 */
81,
0,
/* actions for state 392 */
37,
81,
0,
/* actions for state 393 */
81,
0,
/* actions for state 397 */
87,
0,
/* actions for state 398 */
43,
87,
0,
/* actions for state 399 */
87,
0,
/* actions for state 400 */
87,
0,
/* actions for state 401 */
87,
0,
/* actions for state 402 */
87,
0,
/* actions for state 403 */
54,
87,
0,
/* actions for state 404 */
87,
0,
/* actions for state 405 */
81,
0,
/* actions for state 406 */
81,
0,
/* actions for state 407 */
81,
0,
/* actions for state 408 */
81,
0,
/* actions for state 409 */
28,
81,
0,
/* actions for state 410 */
65,
81,
0,
/* actions for state 411 */
36,
81,
0,
/* actions for state 412 */
63,
81,
0,
/* actions for state 413 */
34,
81,
0,
/* actions for state 418 */
65,
0,
/* actions for state 419 */
63,
0,
/* actions for state 420 */
87,
0,
/* actions for state 421 */
87,
0,
/* actions for state 422 */
87,
0,
/* actions for state 423 */
87,
0,
/* actions for state 424 */
45,
87,
0,
/* actions for state 425 */
65,
87,
0,
/* actions for state 426 */
53,
87,
0,
/* actions for state 427 */
63,
87,
0,
/* actions for state 428 */
51,
87,
0,
/* actions for state 429 */
81,
0,
/* actions for state 430 */
81,
0,
/* actions for state 431 */
81,
0,
/* actions for state 432 */
81,
0,
/* actions for state 437 */
87,
0,
/* actions for state 438 */
87,
0,
/* actions for state 439 */
87,
0,
/* actions for state 440 */
87,
0,
/* actions for state 441 */
81,
0,
/* actions for state 442 */
81,
0,
/* actions for state 443 */
81,
0,
/* actions for state 444 */
81,
0,
/* actions for state 449 */
87,
0,
/* actions for state 450 */
87,
0,
/* actions for state 451 */
87,
0,
/* actions for state 452 */
87,
0,
/* actions for state 453 */
81,
0,
/* actions for state 454 */
81,
0,
/* actions for state 455 */
81,
0,
/* actions for state 456 */
81,
0,
/* actions for state 461 */
87,
0,
/* actions for state 462 */
87,
0,
/* actions for state 463 */
87,
0,
/* actions for state 464 */
87,
0,
/* actions for state 465 */
81,
0,
/* actions for state 466 */
81,
0,
/* actions for state 467 */
81,
0,
/* actions for state 468 */
66,
0,
/* actions for state 472 */
87,
0,
/* actions for state 473 */
87,
0,
/* actions for state 474 */
87,
0,
/* actions for state 475 */
81,
0,
/* actions for state 476 */
81,
0,
/* actions for state 477 */
81,
0,
/* actions for state 481 */
87,
0,
/* actions for state 482 */
87,
0,
/* actions for state 483 */
87,
0,
/* actions for state 484 */
81,
0,
/* actions for state 485 */
81,
0,
/* actions for state 486 */
81,
0,
/* actions for state 490 */
87,
0,
/* actions for state 491 */
87,
0,
/* actions for state 492 */
87,
0,
/* actions for state 493 */
81,
0,
/* actions for state 494 */
81,
0,
/* actions for state 495 */
81,
0,
/* actions for state 499 */
87,
0,
/* actions for state 500 */
87,
0,
/* actions for state 501 */
87,
0,
/* actions for state 502 */
69,
0,
/* actions for state 503 */
68,
0,
/* actions for state 504 */
81,
0,
/* actions for state 506 */
87,
0,
/* actions for state 507 */
81,
0,
/* actions for state 509 */
87,
0,
/* actions for state 510 */
81,
0,
/* actions for state 512 */
87,
0,
/* actions for state 513 */
81,
0,
/* actions for state 515 */
87,
0,
/* actions for state 516 */
81,
0,
/* actions for state 518 */
87,
0,
/* actions for state 519 */
67,
0,
0};
# define YYTYPE int
struct yywork { YYTYPE verify, advance; } yycrank[] = {
0,0,	0,0,	1,9,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	1,10,	1,11,	1,12,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
97,0,	0,0,	97,164,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	1,13,	1,14,	1,15,	
1,16,	0,0,	1,17,	1,18,	
1,19,	1,20,	1,21,	0,0,	
1,22,	1,23,	1,24,	1,25,	
1,26,	1,27,	29,102,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	1,28,	
0,0,	1,29,	1,30,	1,31,	
28,101,	1,32,	1,33,	30,103,	
34,105,	34,105,	34,105,	34,105,	
34,105,	34,105,	34,105,	34,105,	
34,105,	34,105,	79,142,	79,142,	
79,142,	79,142,	79,142,	79,142,	
79,142,	79,142,	79,142,	79,142,	
105,167,	142,201,	167,225,	201,257,	
1,34,	1,35,	1,36,	0,0,	
1,37,	0,0,	1,38,	1,39,	
1,40,	1,41,	1,42,	1,9,	
1,43,	1,9,	1,44,	1,9,	
1,9,	1,45,	1,46,	1,47,	
1,48,	1,49,	1,50,	1,9,	
1,51,	1,52,	1,9,	1,9,	
1,9,	1,9,	1,9,	1,9,	
1,53,	1,54,	1,55,	2,18,	
1,9,	2,20,	2,21,	54,127,	
2,22,	2,23,	57,128,	2,25,	
2,26,	61,129,	62,130,	63,131,	
64,132,	65,133,	66,134,	128,190,	
129,191,	130,192,	131,193,	2,28,	
132,194,	2,29,	2,30,	2,31,	
133,195,	2,32,	134,196,	135,197,	
66,135,	190,248,	191,249,	192,250,	
193,251,	194,252,	195,253,	196,254,	
197,255,	225,281,	225,281,	225,281,	
225,281,	225,281,	225,281,	225,281,	
225,281,	225,281,	225,281,	248,300,	
249,301,	250,302,	251,303,	253,304,	
2,34,	281,326,	2,36,	300,341,	
301,342,	303,343,	2,38,	2,39,	
2,40,	2,41,	2,42,	2,9,	
2,43,	2,9,	2,44,	2,9,	
2,9,	2,45,	2,46,	2,47,	
2,48,	2,49,	2,50,	2,9,	
2,51,	2,52,	2,9,	2,9,	
2,9,	2,9,	2,9,	2,9,	
2,53,	2,54,	2,55,	3,10,	
3,11,	3,12,	304,344,	56,98,	
306,346,	341,372,	342,373,	343,374,	
69,137,	98,98,	56,0,	344,375,	
56,0,	372,395,	373,396,	69,0,	
98,0,	69,0,	98,164,	375,397,	
396,419,	397,420,	415,434,	3,13,	
3,14,	3,15,	416,435,	417,436,	
3,56,	3,57,	418,437,	434,446,	
435,447,	436,448,	3,58,	3,23,	
3,24,	3,25,	3,26,	56,98,	
437,449,	446,458,	447,459,	448,460,	
69,137,	98,98,	69,137,	449,461,	
458,470,	3,28,	56,98,	3,29,	
3,59,	3,31,	459,471,	69,137,	
98,98,	257,306,	257,306,	257,306,	
257,306,	257,306,	257,306,	257,306,	
257,306,	257,306,	257,306,	56,98,	
460,472,	461,469,	470,479,	471,480,	
69,137,	98,98,	395,415,	472,481,	
479,488,	480,489,	481,490,	488,497,	
489,498,	490,499,	3,60,	3,35,	
3,36,	5,67,	497,503,	498,504,	
499,506,	395,416,	506,509,	3,61,	
3,62,	509,512,	3,63,	512,515,	
515,518,	56,98,	518,520,	3,64,	
0,0,	3,65,	69,137,	98,98,	
395,417,	0,0,	3,66,	0,0,	
0,0,	0,0,	395,418,	0,0,	
0,0,	0,0,	3,53,	3,54,	
3,55,	0,0,	0,0,	5,68,	
0,0,	5,69,	5,70,	5,71,	
5,72,	5,73,	0,0,	5,74,	
5,23,	56,0,	5,25,	5,26,	
5,75,	0,0,	69,67,	98,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	5,28,	0,0,	
5,29,	5,76,	5,31,	0,0,	
5,77,	5,78,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	5,79,	
6,67,	5,36,	0,0,	5,80,	
0,0,	5,81,	5,82,	5,83,	
5,84,	5,85,	5,67,	5,86,	
5,67,	5,87,	5,67,	5,67,	
5,88,	5,89,	5,90,	5,91,	
5,92,	5,93,	5,67,	5,94,	
5,95,	5,67,	5,67,	5,67,	
5,67,	5,67,	5,67,	5,53,	
5,54,	5,55,	6,68,	5,67,	
6,69,	6,70,	6,71,	6,72,	
6,73,	0,0,	6,74,	6,23,	
0,0,	6,25,	6,26,	6,75,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	6,28,	0,0,	6,29,	
6,76,	6,31,	0,0,	6,77,	
6,78,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	6,79,	0,0,	
6,36,	0,0,	6,80,	0,0,	
6,81,	6,82,	6,83,	6,84,	
6,85,	6,67,	6,86,	6,67,	
6,87,	6,67,	6,67,	6,88,	
6,89,	6,90,	6,91,	6,92,	
6,93,	6,67,	6,94,	6,95,	
6,67,	6,67,	6,67,	6,67,	
6,67,	6,67,	6,53,	6,54,	
6,55,	9,9,	6,67,	0,0,	
0,0,	0,0,	0,0,	0,0,	
9,0,	9,0,	9,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
9,0,	9,0,	9,0,	9,0,	
0,0,	9,9,	0,0,	9,0,	
9,0,	9,0,	16,96,	0,0,	
9,0,	9,0,	9,0,	9,0,	
9,9,	16,0,	16,0,	16,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	9,0,	0,0,	
9,0,	9,0,	9,0,	0,0,	
9,0,	9,9,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	16,0,	16,96,	16,0,	
16,96,	0,0,	16,96,	0,0,	
16,96,	16,0,	16,0,	0,0,	
0,0,	16,0,	16,0,	16,0,	
16,0,	16,96,	0,0,	9,0,	
9,0,	9,0,	0,0,	9,9,	
0,0,	0,0,	0,0,	16,0,	
0,0,	0,0,	16,0,	0,0,	
0,0,	0,0,	16,96,	17,97,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	17,0,	17,98,	
17,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	9,0,	
9,0,	9,0,	0,0,	9,9,	
0,0,	0,0,	0,0,	0,0,	
16,0,	16,0,	16,0,	0,0,	
16,96,	0,0,	17,98,	17,98,	
17,98,	17,98,	0,0,	17,97,	
0,0,	17,98,	0,0,	0,0,	
0,0,	0,0,	0,0,	17,98,	
0,0,	0,0,	17,97,	18,0,	
18,0,	18,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
16,0,	0,0,	16,0,	0,0,	
16,96,	0,0,	0,0,	17,97,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	18,0,	
18,0,	18,0,	18,0,	0,0,	
0,0,	0,0,	18,0,	18,0,	
18,0,	0,0,	0,0,	18,0,	
18,0,	18,0,	18,0,	0,0,	
0,0,	0,0,	17,98,	0,0,	
0,0,	17,97,	0,0,	0,0,	
0,0,	18,0,	0,0,	18,0,	
18,0,	18,0,	0,0,	18,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	19,100,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
19,0,	19,0,	19,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	17,9,	0,0,	0,0,	
0,0,	0,0,	18,0,	18,0,	
18,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	18,99,	
19,0,	19,0,	19,0,	19,100,	
0,0,	19,100,	0,0,	19,100,	
19,0,	19,0,	0,0,	0,0,	
19,0,	19,100,	19,0,	19,0,	
19,100,	22,0,	22,0,	22,0,	
0,0,	0,0,	18,0,	18,0,	
18,0,	0,0,	19,0,	0,0,	
19,0,	19,0,	19,0,	0,0,	
0,0,	19,100,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	22,0,	22,0,	22,0,	
22,0,	0,0,	0,0,	0,0,	
22,0,	22,0,	22,0,	0,0,	
0,0,	22,0,	22,0,	22,0,	
22,0,	0,0,	0,0,	0,0,	
19,0,	0,0,	0,0,	19,100,	
0,0,	0,0,	0,0,	22,0,	
0,0,	22,0,	22,0,	22,0,	
0,0,	22,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	27,0,	27,0,	27,0,	
0,0,	0,0,	0,0,	19,0,	
0,0,	19,0,	0,0,	19,100,	
0,0,	0,0,	0,0,	0,0,	
22,0,	22,0,	22,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	27,0,	27,0,	27,0,	
27,0,	0,0,	0,0,	0,0,	
27,0,	27,0,	27,0,	32,104,	
0,0,	27,0,	27,0,	27,0,	
27,0,	27,27,	32,0,	32,0,	
32,0,	0,0,	0,0,	0,0,	
22,0,	22,0,	22,0,	27,0,	
0,0,	27,0,	27,0,	27,0,	
0,0,	27,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	32,0,	32,104,	
32,0,	32,104,	0,0,	32,104,	
0,0,	32,104,	32,0,	32,0,	
0,0,	0,0,	32,0,	32,0,	
32,0,	32,0,	32,104,	0,0,	
27,0,	27,0,	27,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
32,0,	0,0,	0,0,	32,0,	
0,0,	0,0,	0,0,	32,104,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	33,0,	33,0,	
33,0,	0,0,	0,0,	0,0,	
27,0,	27,0,	27,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	32,0,	32,0,	32,0,	
0,0,	32,104,	0,0,	0,0,	
0,0,	0,0,	33,0,	33,0,	
33,0,	33,0,	0,0,	0,0,	
0,0,	33,0,	33,0,	33,0,	
0,0,	0,0,	33,0,	33,0,	
33,0,	33,0,	33,33,	37,0,	
37,0,	37,0,	0,0,	0,0,	
0,0,	32,0,	0,0,	32,0,	
33,0,	32,104,	33,0,	33,0,	
33,0,	0,0,	33,0,	33,33,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	37,0,	
37,0,	37,0,	37,0,	0,0,	
0,0,	0,0,	37,0,	37,0,	
37,0,	0,0,	0,0,	37,0,	
37,0,	37,0,	37,0,	37,37,	
0,0,	33,0,	33,0,	33,0,	
0,0,	33,33,	0,0,	0,0,	
0,0,	37,0,	0,0,	37,0,	
37,0,	37,0,	0,0,	37,0,	
37,37,	0,0,	0,0,	0,0,	
38,9,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	38,0,	
38,0,	38,0,	0,0,	0,0,	
0,0,	33,0,	33,0,	33,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	37,0,	37,0,	
37,0,	0,0,	37,37,	0,0,	
0,0,	0,0,	0,0,	38,0,	
38,0,	38,0,	38,0,	0,0,	
38,9,	0,0,	38,0,	38,0,	
38,0,	0,0,	0,0,	38,0,	
38,0,	38,0,	38,0,	38,9,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	37,0,	37,0,	
37,0,	38,0,	0,0,	38,0,	
38,0,	38,0,	0,0,	38,0,	
38,9,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	38,0,	38,0,	
38,0,	0,0,	38,106,	0,0,	
38,9,	38,9,	38,9,	38,9,	
38,9,	38,9,	38,107,	38,9,	
38,9,	38,9,	38,9,	38,9,	
38,9,	38,9,	38,9,	38,9,	
38,9,	38,9,	38,9,	38,9,	
38,9,	38,9,	38,9,	38,9,	
38,9,	38,9,	38,0,	38,0,	
38,0,	0,0,	38,9,	39,0,	
39,0,	39,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	137,137,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
137,0,	0,0,	137,164,	0,0,	
0,0,	0,0,	0,0,	39,0,	
39,0,	39,0,	39,0,	0,0,	
0,0,	0,0,	39,0,	39,0,	
39,0,	0,0,	0,0,	39,0,	
39,0,	39,0,	39,0,	40,0,	
40,0,	40,0,	0,0,	0,0,	
0,0,	137,137,	0,0,	137,137,	
0,0,	39,0,	0,0,	39,0,	
39,0,	39,0,	0,0,	39,0,	
137,137,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	40,0,	
40,0,	40,0,	40,0,	0,0,	
0,0,	0,0,	40,0,	40,0,	
40,0,	137,137,	0,0,	40,0,	
40,0,	40,0,	40,0,	0,0,	
0,0,	0,0,	39,0,	39,0,	
39,0,	0,0,	0,0,	0,0,	
39,108,	40,0,	0,0,	40,0,	
40,0,	40,0,	0,0,	40,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	137,137,	
0,0,	0,0,	0,0,	41,0,	
41,0,	41,0,	0,0,	0,0,	
0,0,	0,0,	39,0,	39,0,	
39,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	40,0,	40,0,	
40,0,	0,0,	0,0,	0,0,	
40,109,	0,0,	0,0,	41,0,	
41,0,	41,0,	41,0,	137,67,	
0,0,	0,0,	41,0,	41,0,	
41,0,	0,0,	40,110,	41,0,	
41,0,	41,0,	41,0,	42,0,	
42,0,	42,0,	0,0,	0,0,	
0,0,	0,0,	40,0,	40,0,	
40,0,	41,0,	0,0,	41,0,	
41,0,	41,0,	0,0,	41,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	42,0,	
42,0,	42,0,	42,0,	0,0,	
0,0,	0,0,	42,0,	42,0,	
42,0,	0,0,	0,0,	42,0,	
42,0,	42,0,	42,0,	0,0,	
0,0,	0,0,	41,0,	41,0,	
41,0,	0,0,	0,0,	0,0,	
0,0,	42,0,	0,0,	42,0,	
42,0,	42,0,	0,0,	42,0,	
41,111,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	43,0,	43,0,	43,0,	
0,0,	0,0,	41,0,	41,0,	
41,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	42,0,	42,0,	
42,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	43,0,	43,0,	43,0,	
43,0,	0,0,	0,0,	0,0,	
43,0,	43,0,	43,0,	0,0,	
42,112,	43,0,	43,0,	43,0,	
43,0,	44,0,	44,0,	44,0,	
0,0,	0,0,	42,0,	42,0,	
42,0,	0,0,	0,0,	43,0,	
0,0,	43,0,	43,0,	43,0,	
0,0,	43,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	44,0,	44,0,	44,0,	
44,0,	0,0,	0,0,	0,0,	
44,0,	44,0,	44,0,	0,0,	
0,0,	44,0,	44,0,	44,0,	
44,0,	0,0,	0,0,	0,0,	
43,0,	43,0,	43,0,	0,0,	
0,0,	0,0,	0,0,	44,0,	
0,0,	44,0,	44,0,	44,0,	
0,0,	44,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
43,113,	0,0,	0,0,	43,114,	
0,0,	0,0,	0,0,	0,0,	
45,0,	45,0,	45,0,	0,0,	
43,0,	43,0,	43,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
44,0,	44,0,	44,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
45,0,	45,0,	45,0,	45,0,	
0,0,	0,0,	44,115,	45,0,	
45,0,	45,0,	0,0,	0,0,	
45,0,	45,0,	45,0,	45,0,	
0,0,	0,0,	0,0,	0,0,	
44,0,	44,0,	44,0,	0,0,	
0,0,	0,0,	45,0,	0,0,	
45,0,	45,0,	45,0,	0,0,	
45,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	46,0,	46,0,	
46,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	45,0,	
45,0,	45,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	45,116,	46,0,	46,0,	
46,0,	46,0,	0,0,	0,0,	
0,0,	46,0,	46,0,	46,0,	
0,0,	0,0,	46,0,	46,0,	
46,0,	46,0,	47,0,	47,0,	
47,0,	0,0,	0,0,	45,0,	
45,0,	45,0,	0,0,	0,0,	
46,0,	0,0,	46,0,	46,0,	
46,0,	0,0,	46,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	47,0,	47,0,	
47,0,	47,0,	0,0,	0,0,	
0,0,	47,0,	47,0,	47,0,	
0,0,	0,0,	47,0,	47,0,	
47,0,	47,0,	0,0,	0,0,	
0,0,	46,0,	46,0,	46,0,	
0,0,	0,0,	0,0,	46,117,	
47,0,	0,0,	47,0,	47,0,	
47,0,	0,0,	47,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	48,0,	48,0,	
48,0,	0,0,	0,0,	0,0,	
0,0,	46,0,	46,0,	46,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	47,0,	47,0,	47,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	48,0,	48,0,	
48,0,	48,0,	0,0,	0,0,	
0,0,	48,0,	48,0,	48,0,	
0,0,	47,118,	48,0,	48,0,	
48,0,	48,0,	0,0,	47,119,	
49,0,	49,0,	49,0,	0,0,	
0,0,	47,0,	47,0,	47,0,	
48,0,	0,0,	48,0,	48,0,	
48,0,	0,0,	48,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
49,0,	49,0,	49,0,	49,0,	
0,0,	0,0,	0,0,	49,0,	
49,0,	49,0,	0,0,	0,0,	
49,0,	49,0,	49,0,	49,0,	
0,0,	48,0,	48,0,	48,0,	
0,0,	0,0,	0,0,	0,0,	
48,120,	0,0,	49,0,	0,0,	
49,0,	49,0,	49,0,	0,0,	
49,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	48,0,	48,0,	48,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	49,0,	
49,0,	49,0,	0,0,	50,0,	
50,0,	50,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
49,121,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	49,122,	0,0,	50,0,	
50,0,	50,0,	50,0,	49,0,	
49,0,	49,0,	50,0,	50,0,	
50,0,	0,0,	0,0,	50,0,	
50,0,	50,0,	50,0,	51,0,	
51,0,	51,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	50,0,	0,0,	50,0,	
50,0,	50,0,	0,0,	50,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	51,0,	
51,0,	51,0,	51,0,	0,0,	
0,0,	0,0,	51,0,	51,0,	
51,0,	0,0,	0,0,	51,0,	
51,0,	51,0,	51,0,	0,0,	
0,0,	0,0,	50,0,	50,0,	
50,0,	0,0,	0,0,	0,0,	
0,0,	51,0,	0,0,	51,0,	
51,0,	51,0,	0,0,	51,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
50,123,	0,0,	0,0,	0,0,	
0,0,	0,0,	50,0,	50,0,	
50,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	51,0,	51,0,	
51,0,	0,0,	0,0,	0,0,	
51,124,	0,0,	0,0,	0,0,	
0,0,	52,0,	52,0,	52,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	51,125,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	51,0,	51,0,	
51,0,	52,0,	52,0,	52,0,	
52,0,	0,0,	0,0,	0,0,	
52,0,	52,0,	52,0,	0,0,	
67,67,	52,0,	52,0,	52,0,	
52,0,	0,0,	0,0,	67,0,	
67,0,	67,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	52,0,	
0,0,	52,0,	52,0,	52,0,	
0,0,	52,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	67,0,	
67,0,	67,0,	67,0,	0,0,	
67,67,	0,0,	67,67,	67,0,	
67,0,	0,0,	0,0,	67,0,	
67,0,	67,0,	67,0,	67,67,	
52,0,	52,0,	52,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	67,0,	0,0,	67,0,	
67,0,	67,0,	52,126,	67,0,	
67,67,	0,0,	0,0,	0,0,	
68,136,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	68,0,	
68,0,	68,0,	0,0,	0,0,	
52,0,	52,0,	52,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	67,0,	67,0,	
67,0,	0,0,	67,67,	0,0,	
0,0,	0,0,	0,0,	68,0,	
68,136,	68,0,	68,136,	0,0,	
68,136,	0,0,	68,136,	68,0,	
68,0,	0,0,	0,0,	68,0,	
68,0,	68,0,	68,0,	68,136,	
70,0,	70,0,	70,0,	0,0,	
0,0,	0,0,	67,0,	67,0,	
67,0,	68,0,	67,67,	0,0,	
68,0,	0,0,	0,0,	0,0,	
68,136,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
70,0,	70,0,	70,0,	70,0,	
0,0,	0,0,	0,0,	0,0,	
70,0,	70,0,	0,0,	0,0,	
70,0,	70,0,	70,0,	70,0,	
0,0,	0,0,	68,0,	68,0,	
68,0,	0,0,	68,136,	0,0,	
0,0,	0,0,	70,0,	0,0,	
70,0,	70,0,	70,0,	0,0,	
70,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	71,139,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	71,0,	71,0,	71,0,	
0,0,	0,0,	68,0,	0,0,	
68,0,	0,0,	68,136,	0,0,	
0,0,	0,0,	0,0,	70,0,	
70,0,	70,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
70,138,	71,0,	71,0,	71,0,	
71,140,	0,0,	71,139,	0,0,	
71,139,	71,0,	71,0,	0,0,	
0,0,	71,0,	71,140,	71,0,	
71,0,	71,139,	74,0,	74,0,	
74,0,	0,0,	0,0,	70,0,	
70,0,	70,0,	0,0,	71,0,	
0,0,	71,0,	71,0,	71,0,	
0,0,	0,0,	71,139,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	74,0,	74,0,	
74,0,	74,0,	0,0,	0,0,	
0,0,	0,0,	74,0,	74,0,	
0,0,	0,0,	74,0,	74,0,	
74,0,	74,0,	0,0,	0,0,	
0,0,	71,0,	0,0,	0,0,	
71,139,	0,0,	0,0,	0,0,	
74,0,	0,0,	74,0,	74,0,	
74,0,	0,0,	74,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	75,0,	75,0,	
75,0,	0,0,	0,0,	0,0,	
71,0,	0,0,	71,0,	0,0,	
71,139,	0,0,	0,0,	0,0,	
0,0,	74,0,	74,0,	74,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	75,0,	75,0,	
75,0,	75,0,	0,0,	0,0,	
0,0,	0,0,	75,0,	75,0,	
77,141,	0,0,	75,0,	75,0,	
75,0,	75,0,	75,75,	77,0,	
77,0,	77,0,	0,0,	0,0,	
0,0,	74,0,	74,0,	74,0,	
75,0,	0,0,	75,0,	75,0,	
75,0,	0,0,	75,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	77,0,	
77,141,	77,0,	77,141,	0,0,	
77,141,	0,0,	77,141,	77,0,	
77,0,	0,0,	0,0,	77,0,	
77,0,	77,0,	77,0,	77,141,	
0,0,	75,0,	75,0,	75,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	77,0,	0,0,	0,0,	
77,0,	0,0,	0,0,	0,0,	
77,141,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	78,0,	
78,0,	78,0,	0,0,	0,0,	
0,0,	75,0,	75,0,	75,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	77,0,	77,0,	
77,0,	0,0,	77,141,	0,0,	
0,0,	0,0,	0,0,	78,0,	
78,0,	78,0,	78,0,	0,0,	
0,0,	0,0,	0,0,	78,0,	
78,0,	0,0,	0,0,	78,0,	
78,0,	78,0,	78,0,	78,78,	
80,0,	80,0,	80,0,	0,0,	
0,0,	0,0,	77,0,	0,0,	
77,0,	78,0,	77,141,	78,0,	
78,0,	78,0,	0,0,	78,0,	
78,78,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
80,0,	80,0,	80,0,	80,0,	
0,0,	0,0,	0,0,	0,0,	
80,0,	80,0,	0,0,	0,0,	
80,0,	80,0,	80,0,	80,0,	
80,80,	0,0,	78,0,	78,0,	
78,0,	0,0,	78,78,	0,0,	
0,0,	0,0,	80,0,	0,0,	
80,0,	80,0,	80,0,	0,0,	
80,0,	80,80,	0,0,	0,0,	
0,0,	81,67,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
81,0,	81,0,	81,0,	0,0,	
0,0,	0,0,	78,0,	78,0,	
78,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	80,0,	
80,0,	80,0,	0,0,	80,80,	
0,0,	0,0,	0,0,	0,0,	
81,0,	81,0,	81,0,	81,0,	
0,0,	81,67,	0,0,	81,67,	
81,0,	81,0,	0,0,	0,0,	
81,0,	81,0,	81,0,	81,0,	
81,67,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	80,0,	
80,0,	80,0,	81,0,	0,0,	
81,0,	81,0,	81,0,	0,0,	
81,0,	81,67,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	81,0,	
81,0,	81,0,	0,0,	81,143,	
0,0,	81,67,	81,67,	81,67,	
81,67,	81,67,	81,67,	81,144,	
81,67,	81,67,	81,67,	81,67,	
81,67,	81,67,	81,67,	81,67,	
81,67,	81,67,	81,67,	81,67,	
81,67,	81,67,	81,67,	81,67,	
81,67,	81,67,	81,67,	81,0,	
81,0,	81,0,	0,0,	81,67,	
82,0,	82,0,	82,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
82,0,	82,0,	82,0,	82,0,	
0,0,	0,0,	0,0,	0,0,	
82,0,	82,0,	0,0,	0,0,	
82,0,	82,0,	82,0,	82,0,	
83,0,	83,0,	83,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	82,0,	0,0,	
82,0,	82,0,	82,0,	0,0,	
82,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
83,0,	83,0,	83,0,	83,0,	
0,0,	0,0,	0,0,	0,0,	
83,0,	83,0,	0,0,	0,0,	
83,0,	83,0,	83,0,	83,0,	
0,0,	0,0,	0,0,	82,0,	
82,0,	82,0,	0,0,	0,0,	
0,0,	82,145,	83,0,	0,0,	
83,0,	83,0,	83,0,	0,0,	
83,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
84,0,	84,0,	84,0,	0,0,	
0,0,	0,0,	0,0,	82,0,	
82,0,	82,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	83,0,	
83,0,	83,0,	0,0,	0,0,	
0,0,	83,146,	0,0,	0,0,	
84,0,	84,0,	84,0,	84,0,	
0,0,	0,0,	0,0,	0,0,	
84,0,	84,0,	0,0,	83,147,	
84,0,	84,0,	84,0,	84,0,	
85,0,	85,0,	85,0,	0,0,	
0,0,	0,0,	0,0,	83,0,	
83,0,	83,0,	84,0,	0,0,	
84,0,	84,0,	84,0,	0,0,	
84,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
85,0,	85,0,	85,0,	85,0,	
0,0,	0,0,	0,0,	0,0,	
85,0,	85,0,	0,0,	0,0,	
85,0,	85,0,	85,0,	85,0,	
0,0,	0,0,	0,0,	84,0,	
84,0,	84,0,	0,0,	0,0,	
0,0,	0,0,	85,0,	0,0,	
85,0,	85,0,	85,0,	0,0,	
85,0,	84,148,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	86,0,	86,0,	
86,0,	0,0,	0,0,	84,0,	
84,0,	84,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	85,0,	
85,0,	85,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	86,0,	86,0,	
86,0,	86,0,	0,0,	0,0,	
0,0,	0,0,	86,0,	86,0,	
0,0,	85,149,	86,0,	86,0,	
86,0,	86,0,	87,0,	87,0,	
87,0,	0,0,	0,0,	85,0,	
85,0,	85,0,	0,0,	0,0,	
86,0,	0,0,	86,0,	86,0,	
86,0,	0,0,	86,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	87,0,	87,0,	
87,0,	87,0,	0,0,	0,0,	
0,0,	0,0,	87,0,	87,0,	
0,0,	0,0,	87,0,	87,0,	
87,0,	87,0,	0,0,	0,0,	
0,0,	86,0,	86,0,	86,0,	
0,0,	0,0,	0,0,	0,0,	
87,0,	0,0,	87,0,	87,0,	
87,0,	0,0,	87,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	86,150,	0,0,	0,0,	
86,151,	0,0,	0,0,	0,0,	
88,0,	88,0,	88,0,	0,0,	
0,0,	86,0,	86,0,	86,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	87,0,	87,0,	87,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
88,0,	88,0,	88,0,	88,0,	
0,0,	0,0,	0,0,	87,152,	
88,0,	88,0,	0,0,	0,0,	
88,0,	88,0,	88,0,	88,0,	
0,0,	0,0,	89,0,	89,0,	
89,0,	87,0,	87,0,	87,0,	
0,0,	0,0,	88,0,	0,0,	
88,0,	88,0,	88,0,	0,0,	
88,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	89,0,	89,0,	
89,0,	89,0,	0,0,	0,0,	
0,0,	0,0,	89,0,	89,0,	
0,0,	0,0,	89,0,	89,0,	
89,0,	89,0,	0,0,	88,0,	
88,0,	88,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
89,0,	88,153,	89,0,	89,0,	
89,0,	0,0,	89,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	90,0,	90,0,	
90,0,	0,0,	0,0,	88,0,	
88,0,	88,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	89,0,	89,0,	89,0,	
0,0,	0,0,	0,0,	89,154,	
0,0,	0,0,	90,0,	90,0,	
90,0,	90,0,	0,0,	0,0,	
0,0,	0,0,	90,0,	90,0,	
0,0,	0,0,	90,0,	90,0,	
90,0,	90,0,	91,0,	91,0,	
91,0,	0,0,	0,0,	0,0,	
0,0,	89,0,	89,0,	89,0,	
90,0,	0,0,	90,0,	90,0,	
90,0,	0,0,	90,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	91,0,	91,0,	
91,0,	91,0,	0,0,	0,0,	
0,0,	0,0,	91,0,	91,0,	
0,0,	0,0,	91,0,	91,0,	
91,0,	91,0,	0,0,	0,0,	
0,0,	90,0,	90,0,	90,0,	
0,0,	0,0,	0,0,	0,0,	
91,0,	0,0,	91,0,	91,0,	
91,0,	0,0,	91,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	90,155,	0,0,	0,0,	
0,0,	0,0,	0,0,	90,156,	
92,0,	92,0,	92,0,	0,0,	
0,0,	90,0,	90,0,	90,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	91,0,	91,0,	91,0,	
0,0,	0,0,	0,0,	0,0,	
91,157,	0,0,	0,0,	0,0,	
92,0,	92,0,	92,0,	92,0,	
0,0,	0,0,	0,0,	0,0,	
92,0,	92,0,	0,0,	0,0,	
92,0,	92,0,	92,0,	92,0,	
93,0,	93,0,	93,0,	0,0,	
0,0,	91,0,	91,0,	91,0,	
0,0,	0,0,	92,0,	0,0,	
92,0,	92,0,	92,0,	0,0,	
92,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
93,0,	93,0,	93,0,	93,0,	
0,0,	0,0,	0,0,	0,0,	
93,0,	93,0,	0,0,	0,0,	
93,0,	93,0,	93,0,	93,0,	
0,0,	0,0,	0,0,	92,0,	
92,0,	92,0,	0,0,	0,0,	
0,0,	0,0,	93,0,	0,0,	
93,0,	93,0,	93,0,	0,0,	
93,0,	0,0,	0,0,	0,0,	
92,158,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	92,159,	0,0,	0,0,	
0,0,	0,0,	0,0,	92,0,	
92,0,	92,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	93,0,	
93,0,	93,0,	94,0,	94,0,	
94,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	93,160,	94,0,	94,0,	
94,0,	94,0,	0,0,	93,0,	
93,0,	93,0,	94,0,	94,0,	
0,0,	0,0,	94,0,	94,0,	
94,0,	94,0,	95,0,	95,0,	
95,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
94,0,	0,0,	94,0,	94,0,	
94,0,	0,0,	94,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	95,0,	95,0,	
95,0,	95,0,	0,0,	0,0,	
0,0,	0,0,	95,0,	95,0,	
0,0,	0,0,	95,0,	95,0,	
95,0,	95,0,	0,0,	0,0,	
0,0,	94,0,	94,0,	94,0,	
0,0,	0,0,	0,0,	94,161,	
95,0,	0,0,	95,0,	95,0,	
95,0,	0,0,	95,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	94,162,	0,0,	0,0,	
0,0,	0,0,	96,0,	96,0,	
96,0,	0,0,	0,0,	0,0,	
0,0,	94,0,	94,0,	94,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	95,0,	95,0,	95,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	96,0,	0,0,	
96,0,	0,0,	0,0,	95,163,	
0,0,	0,0,	96,0,	96,0,	
0,0,	0,0,	96,0,	96,0,	
96,0,	96,0,	99,0,	99,0,	
99,0,	0,0,	0,0,	0,0,	
0,0,	95,0,	95,0,	95,0,	
96,0,	0,0,	0,0,	96,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	99,0,	99,0,	
99,0,	99,0,	0,0,	0,0,	
0,0,	99,0,	99,0,	99,0,	
0,0,	0,0,	99,0,	99,0,	
99,0,	99,0,	0,0,	0,0,	
0,0,	96,0,	96,0,	96,0,	
0,0,	0,0,	0,0,	0,0,	
99,0,	0,0,	99,0,	99,0,	
99,0,	0,0,	99,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
100,0,	100,0,	100,0,	0,0,	
0,0,	96,0,	0,0,	96,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	99,0,	99,0,	99,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	99,165,	
100,0,	100,0,	100,0,	0,0,	
0,0,	0,0,	0,0,	100,166,	
100,0,	100,0,	0,0,	0,0,	
100,0,	0,0,	100,0,	100,0,	
104,0,	104,0,	104,0,	0,0,	
0,0,	99,0,	99,0,	99,0,	
0,0,	0,0,	100,0,	0,0,	
100,0,	100,0,	100,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
104,0,	0,0,	104,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
104,0,	104,0,	0,0,	0,0,	
104,0,	104,0,	104,0,	104,0,	
0,0,	0,0,	0,0,	0,0,	
100,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	104,0,	0,0,	
0,0,	104,0,	0,0,	106,0,	
106,0,	106,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	100,0,	
0,0,	100,0,	0,0,	106,0,	
106,0,	106,0,	106,0,	104,0,	
104,0,	104,0,	106,0,	106,0,	
106,0,	0,0,	0,0,	106,0,	
106,0,	106,0,	106,0,	107,0,	
107,0,	107,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	106,0,	0,0,	106,0,	
106,0,	106,0,	0,0,	106,0,	
0,0,	0,0,	0,0,	104,0,	
0,0,	104,0,	0,0,	107,0,	
107,0,	107,0,	107,0,	0,0,	
0,0,	0,0,	107,0,	107,0,	
107,0,	0,0,	0,0,	107,0,	
107,0,	107,0,	107,0,	0,0,	
0,0,	0,0,	106,0,	106,0,	
106,0,	0,0,	0,0,	0,0,	
0,0,	107,0,	0,0,	107,0,	
107,0,	107,0,	0,0,	107,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	106,168,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	108,0,	108,0,	108,0,	
0,0,	0,0,	106,0,	106,0,	
106,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	107,0,	107,0,	
107,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
107,169,	108,0,	108,0,	108,0,	
108,0,	0,0,	0,0,	0,0,	
108,0,	108,0,	108,0,	0,0,	
0,0,	108,0,	108,0,	108,0,	
108,0,	109,0,	109,0,	109,0,	
0,0,	0,0,	107,0,	107,0,	
107,0,	0,0,	0,0,	108,0,	
0,0,	108,0,	108,0,	108,0,	
0,0,	108,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	109,0,	109,0,	109,0,	
109,0,	0,0,	0,0,	0,0,	
109,0,	109,0,	109,0,	0,0,	
0,0,	109,0,	109,0,	109,0,	
109,0,	0,0,	0,0,	0,0,	
108,0,	108,0,	108,0,	0,0,	
0,0,	0,0,	0,0,	109,0,	
0,0,	109,0,	109,0,	109,0,	
0,0,	109,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
108,170,	110,0,	110,0,	110,0,	
0,0,	0,0,	0,0,	0,0,	
108,0,	108,0,	108,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
109,0,	109,0,	109,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	110,0,	110,0,	110,0,	
110,0,	0,0,	0,0,	0,0,	
110,0,	110,0,	110,0,	0,0,	
0,0,	110,0,	110,0,	110,0,	
110,0,	0,0,	109,171,	111,0,	
111,0,	111,0,	0,0,	0,0,	
109,0,	109,0,	109,0,	110,0,	
0,0,	110,0,	110,0,	110,0,	
0,0,	110,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	111,0,	
111,0,	111,0,	111,0,	0,0,	
0,0,	0,0,	111,0,	111,0,	
111,0,	0,0,	0,0,	111,0,	
111,0,	111,0,	111,0,	0,0,	
110,0,	110,0,	110,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	111,0,	0,0,	111,0,	
111,0,	111,0,	0,0,	111,0,	
0,0,	0,0,	0,0,	110,172,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
110,0,	110,0,	110,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	111,0,	111,0,	
111,0,	0,0,	112,0,	112,0,	
112,0,	0,0,	0,0,	0,0,	
0,0,	111,173,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	112,0,	112,0,	
112,0,	112,0,	111,0,	111,0,	
111,0,	112,0,	112,0,	112,0,	
0,0,	0,0,	112,0,	112,0,	
112,0,	112,0,	113,0,	113,0,	
113,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
112,0,	0,0,	112,0,	112,0,	
112,0,	0,0,	112,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	113,0,	113,0,	
113,0,	113,0,	0,0,	0,0,	
0,0,	113,0,	113,0,	113,0,	
0,0,	0,0,	113,0,	113,0,	
113,0,	113,0,	0,0,	0,0,	
0,0,	112,0,	112,0,	112,0,	
0,0,	0,0,	0,0,	0,0,	
113,0,	0,0,	113,0,	113,0,	
113,0,	0,0,	113,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	112,174,	
114,0,	114,0,	114,0,	0,0,	
0,0,	112,0,	112,0,	112,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	113,0,	113,0,	113,0,	
0,0,	0,0,	0,0,	113,175,	
0,0,	0,0,	0,0,	0,0,	
114,0,	114,0,	114,0,	114,0,	
0,0,	0,0,	0,0,	114,0,	
114,0,	114,0,	0,0,	0,0,	
114,0,	114,0,	114,0,	114,0,	
0,0,	0,0,	115,0,	115,0,	
115,0,	113,0,	113,0,	113,0,	
0,0,	0,0,	114,0,	0,0,	
114,0,	114,0,	114,0,	0,0,	
114,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	115,0,	115,0,	
115,0,	115,0,	0,0,	0,0,	
0,0,	115,0,	115,0,	115,0,	
0,0,	0,0,	115,0,	115,0,	
115,0,	115,0,	0,0,	114,0,	
114,0,	114,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
115,0,	114,176,	115,0,	115,0,	
115,0,	0,0,	115,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	116,0,	
116,0,	116,0,	0,0,	114,0,	
114,0,	114,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	115,0,	115,0,	115,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	116,0,	
116,0,	116,0,	116,0,	0,0,	
0,0,	0,0,	116,0,	116,0,	
116,0,	0,0,	115,177,	116,0,	
116,0,	116,0,	116,0,	117,0,	
117,0,	117,0,	0,0,	0,0,	
0,0,	115,0,	115,0,	115,0,	
0,0,	116,0,	0,0,	116,0,	
116,0,	116,0,	0,0,	116,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	117,0,	
117,0,	117,0,	117,0,	0,0,	
0,0,	0,0,	117,0,	117,0,	
117,0,	0,0,	0,0,	117,0,	
117,0,	117,0,	117,0,	0,0,	
0,0,	0,0,	116,0,	116,0,	
116,0,	0,0,	0,0,	0,0,	
0,0,	117,0,	0,0,	117,0,	
117,0,	117,0,	0,0,	117,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	116,178,	118,0,	
118,0,	118,0,	0,0,	0,0,	
0,0,	0,0,	116,0,	116,0,	
116,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	117,0,	117,0,	
117,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	118,0,	
118,0,	118,0,	118,0,	0,0,	
0,0,	0,0,	118,0,	118,0,	
118,0,	117,179,	0,0,	118,0,	
118,0,	118,0,	118,0,	119,0,	
119,0,	119,0,	0,0,	0,0,	
0,0,	0,0,	117,0,	117,0,	
117,0,	118,0,	0,0,	118,0,	
118,0,	118,0,	0,0,	118,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	119,0,	
119,0,	119,0,	119,0,	0,0,	
0,0,	0,0,	119,0,	119,0,	
119,0,	0,0,	0,0,	119,0,	
119,0,	119,0,	119,0,	0,0,	
0,0,	0,0,	118,0,	118,0,	
118,0,	0,0,	0,0,	0,0,	
0,0,	119,0,	0,0,	119,0,	
119,0,	119,0,	0,0,	119,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	118,180,	
0,0,	0,0,	120,0,	120,0,	
120,0,	0,0,	118,0,	118,0,	
118,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	119,0,	119,0,	
119,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	120,0,	120,0,	
120,0,	120,0,	0,0,	0,0,	
119,181,	120,0,	120,0,	120,0,	
0,0,	0,0,	120,0,	120,0,	
120,0,	120,0,	121,0,	121,0,	
121,0,	0,0,	119,0,	119,0,	
119,0,	0,0,	0,0,	0,0,	
120,0,	0,0,	120,0,	120,0,	
120,0,	0,0,	120,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	121,0,	121,0,	
121,0,	121,0,	0,0,	0,0,	
0,0,	121,0,	121,0,	121,0,	
0,0,	0,0,	121,0,	121,0,	
121,0,	121,0,	0,0,	0,0,	
0,0,	120,0,	120,0,	120,0,	
0,0,	0,0,	0,0,	0,0,	
121,0,	0,0,	121,0,	121,0,	
121,0,	0,0,	121,0,	0,0,	
120,182,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	122,0,	122,0,	
122,0,	0,0,	0,0,	0,0,	
0,0,	120,0,	120,0,	120,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	121,0,	121,0,	121,0,	
0,0,	0,0,	0,0,	121,183,	
0,0,	0,0,	122,0,	122,0,	
122,0,	122,0,	0,0,	0,0,	
0,0,	122,0,	122,0,	122,0,	
0,0,	0,0,	122,0,	122,0,	
122,0,	122,0,	123,0,	123,0,	
123,0,	0,0,	0,0,	0,0,	
0,0,	121,0,	121,0,	121,0,	
122,0,	0,0,	122,0,	122,0,	
122,0,	0,0,	122,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	123,0,	123,0,	
123,0,	123,0,	0,0,	0,0,	
0,0,	123,0,	123,0,	123,0,	
0,0,	0,0,	123,0,	123,0,	
123,0,	123,0,	0,0,	0,0,	
0,0,	122,0,	122,0,	122,0,	
0,0,	0,0,	0,0,	0,0,	
123,0,	0,0,	123,0,	123,0,	
123,0,	0,0,	123,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
122,184,	0,0,	124,0,	124,0,	
124,0,	0,0,	0,0,	0,0,	
0,0,	122,0,	122,0,	122,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	123,0,	123,0,	123,0,	
0,0,	0,0,	0,0,	123,185,	
0,0,	0,0,	124,0,	124,0,	
124,0,	124,0,	0,0,	0,0,	
0,0,	124,0,	124,0,	124,0,	
0,0,	0,0,	124,0,	124,0,	
124,0,	124,0,	125,0,	125,0,	
125,0,	0,0,	0,0,	0,0,	
0,0,	123,0,	123,0,	123,0,	
124,0,	0,0,	124,0,	124,0,	
124,0,	0,0,	124,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	125,0,	125,0,	
125,0,	125,0,	0,0,	0,0,	
0,0,	125,0,	125,0,	125,0,	
0,0,	0,0,	125,0,	125,0,	
125,0,	125,0,	0,0,	0,0,	
0,0,	124,0,	124,0,	124,0,	
0,0,	0,0,	0,0,	0,0,	
125,0,	0,0,	125,0,	125,0,	
125,0,	0,0,	125,0,	0,0,	
0,0,	0,0,	0,0,	124,186,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	124,0,	124,0,	124,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	125,0,	125,0,	125,0,	
0,0,	126,0,	126,0,	126,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	125,187,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	125,188,	
0,0,	126,0,	126,0,	126,0,	
126,0,	125,0,	125,0,	125,0,	
126,0,	126,0,	126,0,	0,0,	
0,0,	126,0,	126,0,	126,0,	
126,0,	136,0,	136,0,	136,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	126,0,	
0,0,	126,0,	126,0,	126,0,	
0,0,	126,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	136,0,	0,0,	136,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	136,0,	136,0,	0,0,	
0,0,	136,0,	136,0,	136,0,	
136,0,	0,0,	0,0,	0,0,	
126,0,	126,0,	126,0,	0,0,	
0,0,	0,0,	0,0,	136,0,	
0,0,	0,0,	136,0,	138,0,	
138,0,	138,0,	0,0,	0,0,	
0,0,	0,0,	126,189,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
126,0,	126,0,	126,0,	138,0,	
138,0,	138,0,	138,0,	0,0,	
136,0,	136,0,	136,0,	138,0,	
138,0,	0,0,	0,0,	138,0,	
138,0,	138,0,	138,0,	0,0,	
0,0,	139,0,	139,0,	139,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	138,0,	0,0,	138,0,	
138,0,	138,0,	0,0,	138,0,	
0,0,	0,0,	0,0,	0,0,	
136,0,	0,0,	136,0,	0,0,	
0,0,	139,0,	139,0,	139,0,	
0,0,	0,0,	0,0,	0,0,	
139,199,	139,0,	139,0,	0,0,	
0,0,	139,0,	0,0,	139,0,	
139,0,	0,0,	138,0,	138,0,	
138,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	140,140,	139,0,	
138,198,	139,0,	139,0,	139,0,	
0,0,	140,0,	140,0,	140,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	138,0,	138,0,	
138,0,	0,0,	0,0,	0,0,	
0,0,	140,0,	140,0,	140,0,	
0,0,	139,0,	140,140,	0,0,	
140,200,	140,0,	140,0,	0,0,	
0,0,	140,0,	0,0,	140,0,	
140,0,	140,140,	141,0,	141,0,	
141,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	140,0,	
0,0,	140,0,	140,0,	140,0,	
0,0,	0,0,	140,140,	0,0,	
139,0,	0,0,	139,0,	0,0,	
0,0,	0,0,	141,0,	0,0,	
141,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	141,0,	141,0,	
0,0,	0,0,	141,0,	141,0,	
141,0,	141,0,	0,0,	0,0,	
0,0,	140,0,	0,0,	0,0,	
140,140,	0,0,	0,0,	0,0,	
141,0,	0,0,	0,0,	141,0,	
0,0,	143,0,	143,0,	143,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
140,0,	0,0,	140,0,	0,0,	
140,140,	143,0,	143,0,	143,0,	
143,0,	141,0,	141,0,	141,0,	
0,0,	143,0,	143,0,	0,0,	
0,0,	143,0,	143,0,	143,0,	
143,0,	144,0,	144,0,	144,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	143,0,	
0,0,	143,0,	143,0,	143,0,	
0,0,	143,0,	0,0,	0,0,	
0,0,	141,0,	0,0,	141,0,	
0,0,	144,0,	144,0,	144,0,	
144,0,	0,0,	0,0,	0,0,	
0,0,	144,0,	144,0,	0,0,	
0,0,	144,0,	144,0,	144,0,	
144,0,	0,0,	0,0,	0,0,	
143,0,	143,0,	143,0,	0,0,	
0,0,	0,0,	0,0,	144,0,	
0,0,	144,0,	144,0,	144,0,	
0,0,	144,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
143,202,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	145,0,	
145,0,	145,0,	0,0,	0,0,	
143,0,	143,0,	143,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
144,0,	144,0,	144,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	144,203,	145,0,	
145,0,	145,0,	145,0,	0,0,	
0,0,	0,0,	0,0,	145,0,	
145,0,	0,0,	0,0,	145,0,	
145,0,	145,0,	145,0,	146,0,	
146,0,	146,0,	0,0,	0,0,	
144,0,	144,0,	144,0,	0,0,	
0,0,	145,0,	0,0,	145,0,	
145,0,	145,0,	0,0,	145,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	146,0,	
146,0,	146,0,	146,0,	0,0,	
0,0,	0,0,	0,0,	146,0,	
146,0,	0,0,	0,0,	146,0,	
146,0,	146,0,	146,0,	0,0,	
0,0,	0,0,	145,0,	145,0,	
145,0,	0,0,	0,0,	0,0,	
0,0,	146,0,	0,0,	146,0,	
146,0,	146,0,	0,0,	146,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	145,204,	147,0,	
147,0,	147,0,	0,0,	0,0,	
0,0,	0,0,	145,0,	145,0,	
145,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	146,0,	146,0,	
146,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	147,0,	
147,0,	147,0,	147,0,	0,0,	
0,0,	0,0,	0,0,	147,0,	
147,0,	0,0,	0,0,	147,0,	
147,0,	147,0,	147,0,	0,0,	
146,205,	148,0,	148,0,	148,0,	
0,0,	0,0,	146,0,	146,0,	
146,0,	147,0,	0,0,	147,0,	
147,0,	147,0,	0,0,	147,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	148,0,	148,0,	148,0,	
148,0,	0,0,	0,0,	0,0,	
0,0,	148,0,	148,0,	0,0,	
0,0,	148,0,	148,0,	148,0,	
148,0,	0,0,	147,0,	147,0,	
147,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	148,0,	
0,0,	148,0,	148,0,	148,0,	
0,0,	148,0,	0,0,	0,0,	
0,0,	147,206,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	147,0,	147,0,	
147,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
148,0,	148,0,	148,0,	149,0,	
149,0,	149,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	148,207,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	149,0,	
149,0,	149,0,	149,0,	0,0,	
148,0,	148,0,	148,0,	149,0,	
149,0,	0,0,	0,0,	149,0,	
149,0,	149,0,	149,0,	150,0,	
150,0,	150,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	149,0,	0,0,	149,0,	
149,0,	149,0,	0,0,	149,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	150,0,	
150,0,	150,0,	150,0,	0,0,	
0,0,	0,0,	0,0,	150,0,	
150,0,	0,0,	0,0,	150,0,	
150,0,	150,0,	150,0,	0,0,	
0,0,	0,0,	149,0,	149,0,	
149,0,	0,0,	0,0,	0,0,	
0,0,	150,0,	0,0,	150,0,	
150,0,	150,0,	0,0,	150,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
149,208,	151,0,	151,0,	151,0,	
0,0,	0,0,	149,0,	149,0,	
149,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	150,0,	150,0,	
150,0,	0,0,	0,0,	0,0,	
150,209,	0,0,	0,0,	0,0,	
0,0,	151,0,	151,0,	151,0,	
151,0,	0,0,	0,0,	0,0,	
0,0,	151,0,	151,0,	0,0,	
0,0,	151,0,	151,0,	151,0,	
151,0,	0,0,	0,0,	152,0,	
152,0,	152,0,	150,0,	150,0,	
150,0,	0,0,	0,0,	151,0,	
0,0,	151,0,	151,0,	151,0,	
0,0,	151,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	152,0,	
152,0,	152,0,	152,0,	0,0,	
0,0,	0,0,	0,0,	152,0,	
152,0,	0,0,	0,0,	152,0,	
152,0,	152,0,	152,0,	0,0,	
151,0,	151,0,	151,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	152,0,	151,210,	152,0,	
152,0,	152,0,	0,0,	152,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
153,0,	153,0,	153,0,	0,0,	
151,0,	151,0,	151,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	152,0,	152,0,	
152,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
153,0,	153,0,	153,0,	153,0,	
0,0,	0,0,	0,0,	0,0,	
153,0,	153,0,	0,0,	152,211,	
153,0,	153,0,	153,0,	153,0,	
154,0,	154,0,	154,0,	0,0,	
0,0,	0,0,	152,0,	152,0,	
152,0,	0,0,	153,0,	0,0,	
153,0,	153,0,	153,0,	0,0,	
153,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
154,0,	154,0,	154,0,	154,0,	
0,0,	0,0,	0,0,	0,0,	
154,0,	154,0,	0,0,	0,0,	
154,0,	154,0,	154,0,	154,0,	
0,0,	0,0,	0,0,	153,0,	
153,0,	153,0,	0,0,	0,0,	
0,0,	0,0,	154,0,	0,0,	
154,0,	154,0,	154,0,	0,0,	
154,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	153,212,	
155,0,	155,0,	155,0,	0,0,	
0,0,	0,0,	0,0,	153,0,	
153,0,	153,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	154,0,	
154,0,	154,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
155,0,	155,0,	155,0,	155,0,	
0,0,	0,0,	0,0,	0,0,	
155,0,	155,0,	154,213,	0,0,	
155,0,	155,0,	155,0,	155,0,	
156,0,	156,0,	156,0,	0,0,	
0,0,	0,0,	0,0,	154,0,	
154,0,	154,0,	155,0,	0,0,	
155,0,	155,0,	155,0,	0,0,	
155,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
156,0,	156,0,	156,0,	156,0,	
0,0,	0,0,	0,0,	0,0,	
156,0,	156,0,	0,0,	0,0,	
156,0,	156,0,	156,0,	156,0,	
0,0,	0,0,	0,0,	155,0,	
155,0,	155,0,	0,0,	0,0,	
0,0,	0,0,	156,0,	0,0,	
156,0,	156,0,	156,0,	0,0,	
156,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
155,214,	0,0,	157,0,	157,0,	
157,0,	0,0,	0,0,	155,0,	
155,0,	155,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	156,0,	
156,0,	156,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	157,0,	157,0,	
157,0,	157,0,	0,0,	0,0,	
0,0,	156,215,	157,0,	157,0,	
0,0,	0,0,	157,0,	157,0,	
157,0,	157,0,	158,0,	158,0,	
158,0,	0,0,	0,0,	156,0,	
156,0,	156,0,	0,0,	0,0,	
157,0,	0,0,	157,0,	157,0,	
157,0,	0,0,	157,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	158,0,	158,0,	
158,0,	158,0,	0,0,	0,0,	
0,0,	0,0,	158,0,	158,0,	
0,0,	0,0,	158,0,	158,0,	
158,0,	158,0,	0,0,	0,0,	
0,0,	157,0,	157,0,	157,0,	
0,0,	0,0,	0,0,	0,0,	
158,0,	0,0,	158,0,	158,0,	
158,0,	0,0,	158,0,	0,0,	
157,216,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	159,0,	159,0,	
159,0,	0,0,	0,0,	0,0,	
0,0,	157,0,	157,0,	157,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	158,0,	158,0,	158,0,	
0,0,	0,0,	0,0,	158,217,	
0,0,	0,0,	159,0,	159,0,	
159,0,	159,0,	0,0,	0,0,	
0,0,	0,0,	159,0,	159,0,	
0,0,	0,0,	159,0,	159,0,	
159,0,	159,0,	160,0,	160,0,	
160,0,	0,0,	0,0,	0,0,	
0,0,	158,0,	158,0,	158,0,	
159,0,	0,0,	159,0,	159,0,	
159,0,	0,0,	159,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	160,0,	160,0,	
160,0,	160,0,	0,0,	0,0,	
0,0,	0,0,	160,0,	160,0,	
0,0,	0,0,	160,0,	160,0,	
160,0,	160,0,	0,0,	0,0,	
0,0,	159,0,	159,0,	159,0,	
0,0,	0,0,	0,0,	0,0,	
160,0,	0,0,	160,0,	160,0,	
160,0,	0,0,	160,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
159,218,	0,0,	161,0,	161,0,	
161,0,	0,0,	0,0,	0,0,	
0,0,	159,0,	159,0,	159,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	160,0,	160,0,	160,0,	
0,0,	0,0,	0,0,	160,219,	
0,0,	0,0,	161,0,	161,0,	
161,0,	161,0,	0,0,	0,0,	
0,0,	0,0,	161,0,	161,0,	
0,0,	0,0,	161,0,	161,0,	
161,0,	161,0,	162,0,	162,0,	
162,0,	0,0,	0,0,	0,0,	
0,0,	160,0,	160,0,	160,0,	
161,0,	0,0,	161,0,	161,0,	
161,0,	0,0,	161,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	162,0,	162,0,	
162,0,	162,0,	0,0,	0,0,	
0,0,	0,0,	162,0,	162,0,	
0,0,	0,0,	162,0,	162,0,	
162,0,	162,0,	0,0,	0,0,	
0,0,	161,0,	161,0,	161,0,	
0,0,	0,0,	0,0,	0,0,	
162,0,	0,0,	162,0,	162,0,	
162,0,	0,0,	162,0,	0,0,	
0,0,	0,0,	0,0,	161,220,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	161,0,	161,0,	161,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	162,0,	162,0,	162,0,	
163,0,	163,0,	163,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	162,221,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	162,222,	
163,0,	163,0,	163,0,	163,0,	
0,0,	162,0,	162,0,	162,0,	
163,0,	163,0,	0,0,	0,0,	
163,0,	163,0,	163,0,	163,0,	
165,0,	165,0,	165,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	163,0,	0,0,	
163,0,	163,0,	163,0,	0,0,	
163,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
165,0,	165,0,	165,0,	165,0,	
0,0,	0,0,	0,0,	165,0,	
165,0,	165,0,	0,0,	0,0,	
165,0,	165,0,	165,0,	165,0,	
0,0,	0,0,	0,0,	163,0,	
163,0,	163,0,	0,0,	0,0,	
0,0,	0,0,	165,0,	0,0,	
165,0,	165,0,	165,0,	0,0,	
165,0,	0,0,	0,0,	0,0,	
0,0,	163,223,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	166,0,	
166,0,	166,0,	0,0,	163,0,	
163,0,	163,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	165,0,	
165,0,	165,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	165,224,	166,0,	
166,0,	166,0,	0,0,	0,0,	
0,0,	0,0,	166,166,	166,0,	
166,0,	0,0,	0,0,	166,0,	
0,0,	166,0,	166,0,	168,0,	
168,0,	168,0,	0,0,	165,0,	
165,0,	165,0,	0,0,	0,0,	
0,0,	166,0,	0,0,	166,0,	
166,0,	166,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	168,0,	
168,0,	168,0,	168,0,	0,0,	
0,0,	0,0,	168,0,	168,0,	
168,0,	0,0,	0,0,	168,0,	
168,0,	168,0,	168,0,	0,0,	
0,0,	0,0,	0,0,	166,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	168,0,	0,0,	168,0,	
168,0,	168,0,	0,0,	168,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	169,0,	
169,0,	169,0,	0,0,	0,0,	
0,0,	0,0,	166,0,	0,0,	
166,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	168,0,	168,0,	
168,0,	0,0,	0,0,	0,0,	
0,0,	168,226,	0,0,	169,0,	
169,0,	169,0,	169,0,	0,0,	
0,0,	0,0,	169,0,	169,0,	
169,0,	0,0,	0,0,	169,0,	
169,0,	169,0,	169,0,	170,0,	
170,0,	170,0,	0,0,	0,0,	
0,0,	0,0,	168,0,	168,0,	
168,0,	169,0,	0,0,	169,0,	
169,0,	169,0,	0,0,	169,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	170,0,	
170,0,	170,0,	170,0,	0,0,	
0,0,	0,0,	170,0,	170,0,	
170,0,	0,0,	0,0,	170,0,	
170,0,	170,0,	170,0,	0,0,	
0,0,	0,0,	169,0,	169,0,	
169,0,	0,0,	0,0,	0,0,	
0,0,	170,0,	0,0,	170,0,	
170,0,	170,0,	0,0,	170,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	169,227,	0,0,	0,0,	
0,0,	0,0,	0,0,	171,0,	
171,0,	171,0,	0,0,	0,0,	
0,0,	0,0,	169,0,	169,0,	
169,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	170,0,	170,0,	
170,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	171,0,	
171,0,	171,0,	171,0,	0,0,	
170,228,	0,0,	171,0,	171,0,	
171,0,	0,0,	0,0,	171,0,	
171,0,	171,0,	171,0,	172,0,	
172,0,	172,0,	0,0,	0,0,	
0,0,	0,0,	170,0,	170,0,	
170,0,	171,0,	0,0,	171,0,	
171,0,	171,0,	0,0,	171,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	172,0,	
172,0,	172,0,	172,0,	0,0,	
0,0,	0,0,	172,0,	172,0,	
172,0,	0,0,	0,0,	172,0,	
172,0,	172,0,	172,0,	0,0,	
0,0,	0,0,	171,0,	171,0,	
171,0,	0,0,	0,0,	0,0,	
0,0,	172,0,	0,0,	172,0,	
172,0,	172,0,	0,0,	172,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	171,229,	0,0,	
173,0,	173,0,	173,0,	0,0,	
0,0,	0,0,	171,0,	171,0,	
171,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	172,0,	172,0,	
172,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	172,230,	
173,0,	173,0,	173,0,	173,0,	
0,0,	0,0,	0,0,	173,0,	
173,0,	173,0,	0,0,	0,0,	
173,0,	173,0,	173,0,	173,0,	
0,0,	0,0,	0,0,	174,0,	
174,0,	174,0,	172,0,	172,0,	
172,0,	0,0,	173,0,	0,0,	
173,0,	173,0,	173,0,	0,0,	
173,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	174,0,	
174,0,	174,0,	174,0,	0,0,	
0,0,	0,0,	174,0,	174,0,	
174,0,	0,0,	0,0,	174,0,	
174,0,	174,0,	174,0,	173,0,	
173,0,	173,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	174,0,	173,231,	174,0,	
174,0,	174,0,	0,0,	174,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	175,0,	
175,0,	175,0,	0,0,	173,0,	
173,0,	173,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	174,0,	174,0,	
174,0,	0,0,	0,0,	0,0,	
174,232,	0,0,	0,0,	175,0,	
175,0,	175,0,	175,0,	0,0,	
0,0,	0,0,	175,0,	175,0,	
175,0,	0,0,	0,0,	175,0,	
175,0,	175,0,	175,0,	176,0,	
176,0,	176,0,	0,0,	0,0,	
0,0,	0,0,	174,0,	174,0,	
174,0,	175,0,	0,0,	175,0,	
175,0,	175,0,	0,0,	175,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	176,0,	
176,0,	176,0,	176,0,	0,0,	
0,0,	0,0,	176,0,	176,0,	
176,0,	0,0,	0,0,	176,0,	
176,0,	176,0,	176,0,	0,0,	
0,0,	0,0,	175,0,	175,0,	
175,0,	0,0,	0,0,	0,0,	
0,0,	176,0,	0,0,	176,0,	
176,0,	176,0,	0,0,	176,0,	
0,0,	0,0,	0,0,	175,233,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	177,0,	
177,0,	177,0,	0,0,	0,0,	
0,0,	0,0,	175,0,	175,0,	
175,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	176,0,	176,0,	
176,0,	0,0,	0,0,	0,0,	
176,234,	0,0,	0,0,	177,0,	
177,0,	177,0,	177,0,	0,0,	
0,0,	0,0,	177,0,	177,0,	
177,0,	0,0,	0,0,	177,0,	
177,0,	177,0,	177,0,	178,0,	
178,0,	178,0,	0,0,	0,0,	
0,0,	0,0,	176,0,	176,0,	
176,0,	177,0,	0,0,	177,0,	
177,0,	177,0,	0,0,	177,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	178,0,	
178,0,	178,0,	178,0,	0,0,	
0,0,	0,0,	178,0,	178,0,	
178,0,	0,0,	0,0,	178,0,	
178,0,	178,0,	178,0,	0,0,	
0,0,	0,0,	177,0,	177,0,	
177,0,	0,0,	0,0,	0,0,	
0,0,	178,0,	0,0,	178,0,	
178,0,	178,0,	0,0,	178,0,	
0,0,	0,0,	0,0,	177,235,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	179,0,	
179,0,	179,0,	177,0,	177,0,	
177,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	178,0,	178,0,	
178,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	179,0,	
179,0,	179,0,	179,0,	0,0,	
0,0,	0,0,	179,0,	179,0,	
179,0,	0,0,	178,236,	179,0,	
179,0,	179,0,	179,0,	180,0,	
180,0,	180,0,	178,0,	178,0,	
178,0,	0,0,	0,0,	0,0,	
0,0,	179,0,	0,0,	179,0,	
179,0,	179,0,	0,0,	179,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	180,0,	
180,0,	180,0,	180,0,	0,0,	
0,0,	0,0,	180,0,	180,0,	
180,0,	0,0,	0,0,	180,0,	
180,0,	180,0,	180,0,	0,0,	
0,0,	0,0,	179,0,	179,0,	
179,0,	0,0,	0,0,	0,0,	
0,0,	180,0,	0,0,	180,0,	
180,0,	180,0,	0,0,	180,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	179,237,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	179,0,	179,0,	
179,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	180,0,	180,0,	
180,0,	0,0,	180,238,	0,0,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,9,	180,9,	
180,9,	180,9,	180,0,	180,0,	
180,0,	181,0,	181,0,	181,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	181,0,	181,0,	181,0,	
181,0,	0,0,	0,0,	0,0,	
181,0,	181,0,	181,0,	0,0,	
0,0,	181,0,	181,0,	181,0,	
181,0,	0,0,	182,0,	182,0,	
182,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	181,0,	
0,0,	181,0,	181,0,	181,0,	
0,0,	181,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	182,0,	182,0,	
182,0,	182,0,	0,0,	0,0,	
0,0,	182,0,	182,0,	182,0,	
0,0,	0,0,	182,0,	182,0,	
182,0,	182,0,	0,0,	0,0,	
181,0,	181,0,	181,0,	0,0,	
0,0,	0,0,	0,0,	181,239,	
182,0,	0,0,	182,0,	182,0,	
182,0,	0,0,	182,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
183,0,	183,0,	183,0,	0,0,	
181,0,	181,0,	181,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	182,0,	182,0,	182,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	182,240,	
183,0,	183,0,	183,0,	183,0,	
0,0,	0,0,	0,0,	183,0,	
183,0,	183,0,	0,0,	0,0,	
183,0,	183,0,	183,0,	183,0,	
184,0,	184,0,	184,0,	0,0,	
0,0,	182,0,	182,0,	182,0,	
0,0,	0,0,	183,0,	0,0,	
183,0,	183,0,	183,0,	0,0,	
183,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
184,0,	184,0,	184,0,	184,0,	
0,0,	0,0,	0,0,	184,0,	
184,0,	184,0,	0,0,	0,0,	
184,0,	184,0,	184,0,	184,0,	
0,0,	0,0,	0,0,	183,0,	
183,0,	183,0,	0,0,	0,0,	
0,0,	0,0,	184,0,	183,241,	
184,0,	184,0,	184,0,	0,0,	
184,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	185,0,	185,0,	185,0,	
0,0,	0,0,	0,0,	183,0,	
183,0,	183,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	184,0,	
184,0,	184,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	185,0,	185,0,	185,0,	
185,0,	0,0,	0,0,	0,0,	
185,0,	185,0,	185,0,	0,0,	
184,242,	185,0,	185,0,	185,0,	
185,0,	186,0,	186,0,	186,0,	
0,0,	0,0,	0,0,	184,0,	
184,0,	184,0,	0,0,	185,0,	
0,0,	185,0,	185,0,	185,0,	
0,0,	185,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	186,0,	186,0,	186,0,	
186,0,	0,0,	0,0,	0,0,	
186,0,	186,0,	186,0,	0,0,	
0,0,	186,0,	186,0,	186,0,	
186,0,	0,0,	0,0,	0,0,	
185,0,	185,0,	185,0,	0,0,	
0,0,	0,0,	0,0,	186,0,	
0,0,	186,0,	186,0,	186,0,	
0,0,	186,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	185,243,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	187,0,	
187,0,	187,0,	0,0,	0,0,	
185,0,	185,0,	185,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
186,0,	186,0,	186,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	186,244,	187,0,	
187,0,	187,0,	187,0,	0,0,	
0,0,	0,0,	187,0,	187,0,	
187,0,	0,0,	0,0,	187,0,	
187,0,	187,0,	187,0,	0,0,	
0,0,	188,0,	188,0,	188,0,	
186,0,	186,0,	186,0,	0,0,	
0,0,	187,0,	0,0,	187,0,	
187,0,	187,0,	0,0,	187,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	188,0,	188,0,	188,0,	
188,0,	0,0,	0,0,	0,0,	
188,0,	188,0,	188,0,	0,0,	
0,0,	188,0,	188,0,	188,0,	
188,0,	0,0,	187,0,	187,0,	
187,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	188,0,	
187,245,	188,0,	188,0,	188,0,	
0,0,	188,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	187,0,	187,0,	
187,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
188,0,	188,0,	188,0,	0,0,	
189,0,	189,0,	189,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	188,246,	
0,0,	0,0,	0,0,	0,0,	
189,0,	189,0,	189,0,	189,0,	
188,0,	188,0,	188,0,	189,0,	
189,0,	189,0,	0,0,	0,0,	
189,0,	189,0,	189,0,	189,0,	
0,0,	0,0,	198,0,	198,0,	
198,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	189,0,	0,0,	
189,0,	189,0,	189,0,	0,0,	
189,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	198,0,	198,0,	
198,0,	198,0,	0,0,	0,0,	
0,0,	0,0,	198,0,	198,0,	
0,0,	0,0,	198,0,	198,0,	
198,0,	198,0,	0,0,	189,0,	
189,0,	189,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
198,0,	189,247,	198,0,	198,0,	
198,0,	0,0,	198,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	189,0,	
189,0,	189,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	198,0,	198,0,	198,0,	
0,0,	199,0,	199,0,	199,0,	
0,0,	0,0,	0,0,	0,0,	
198,256,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	199,0,	199,0,	199,0,	
0,0,	198,0,	198,0,	198,0,	
199,199,	199,0,	199,0,	200,140,	
0,0,	199,0,	0,0,	199,0,	
199,0,	0,0,	200,0,	200,0,	
200,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	199,0,	
0,0,	199,0,	199,0,	199,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	200,0,	200,0,	
200,0,	0,0,	0,0,	200,140,	
0,0,	200,200,	200,0,	200,0,	
0,0,	0,0,	200,0,	0,0,	
200,0,	200,0,	200,140,	0,0,	
0,0,	199,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
200,0,	0,0,	200,0,	200,0,	
200,0,	0,0,	0,0,	200,140,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	202,0,	202,0,	
202,0,	0,0,	0,0,	0,0,	
199,0,	0,0,	199,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	200,0,	0,0,	
0,0,	200,140,	0,0,	0,0,	
0,0,	0,0,	202,0,	202,0,	
202,0,	202,0,	0,0,	0,0,	
0,0,	0,0,	202,0,	202,0,	
0,0,	0,0,	202,0,	202,0,	
202,0,	202,0,	0,0,	203,0,	
203,0,	203,0,	0,0,	0,0,	
0,0,	200,0,	0,0,	200,0,	
202,0,	200,140,	202,0,	202,0,	
202,0,	0,0,	202,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	203,0,	
203,0,	203,0,	203,0,	0,0,	
0,0,	0,0,	0,0,	203,0,	
203,0,	0,0,	0,0,	203,0,	
203,0,	203,0,	203,0,	0,0,	
0,0,	202,0,	202,0,	202,0,	
0,0,	0,0,	0,0,	0,0,	
202,258,	203,0,	0,0,	203,0,	
203,0,	203,0,	0,0,	203,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	204,0,	
204,0,	204,0,	0,0,	0,0,	
0,0,	202,0,	202,0,	202,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	203,0,	203,0,	
203,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	204,0,	
204,0,	204,0,	204,0,	0,0,	
0,0,	0,0,	0,0,	204,0,	
204,0,	203,259,	0,0,	204,0,	
204,0,	204,0,	204,0,	205,0,	
205,0,	205,0,	0,0,	0,0,	
0,0,	0,0,	203,0,	203,0,	
203,0,	204,0,	0,0,	204,0,	
204,0,	204,0,	0,0,	204,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	205,0,	
205,0,	205,0,	205,0,	0,0,	
0,0,	0,0,	0,0,	205,0,	
205,0,	0,0,	0,0,	205,0,	
205,0,	205,0,	205,0,	0,0,	
0,0,	0,0,	204,0,	204,0,	
204,0,	0,0,	0,0,	0,0,	
0,0,	205,0,	0,0,	205,0,	
205,0,	205,0,	0,0,	205,0,	
204,260,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	206,0,	
206,0,	206,0,	204,0,	204,0,	
204,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	205,0,	205,0,	
205,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	206,0,	
206,0,	206,0,	206,0,	0,0,	
0,0,	0,0,	0,0,	206,0,	
206,0,	0,0,	205,261,	206,0,	
206,0,	206,0,	206,0,	0,0,	
0,0,	0,0,	205,0,	205,0,	
205,0,	0,0,	0,0,	0,0,	
0,0,	206,0,	0,0,	206,0,	
206,0,	206,0,	0,0,	206,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
207,0,	207,0,	207,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	206,0,	206,0,	
206,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	206,262,	
207,0,	207,0,	207,0,	207,0,	
0,0,	0,0,	0,0,	0,0,	
207,0,	207,0,	0,0,	0,0,	
207,0,	207,0,	207,0,	207,0,	
0,0,	0,0,	0,0,	208,0,	
208,0,	208,0,	206,0,	206,0,	
206,0,	0,0,	207,0,	0,0,	
207,0,	207,0,	207,0,	0,0,	
207,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	208,0,	
208,0,	208,0,	208,0,	0,0,	
0,0,	0,0,	0,0,	208,0,	
208,0,	0,0,	0,0,	208,0,	
208,0,	208,0,	208,0,	207,0,	
207,0,	207,0,	209,0,	209,0,	
209,0,	0,0,	0,0,	0,0,	
0,0,	208,0,	207,263,	208,0,	
208,0,	208,0,	0,0,	208,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	209,0,	209,0,	
209,0,	209,0,	0,0,	207,0,	
207,0,	207,0,	209,0,	209,0,	
0,0,	0,0,	209,0,	209,0,	
209,0,	209,0,	208,0,	208,0,	
208,0,	210,0,	210,0,	210,0,	
208,264,	0,0,	0,0,	0,0,	
209,0,	0,0,	209,0,	209,0,	
209,0,	0,0,	209,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	210,0,	210,0,	210,0,	
210,0,	0,0,	208,0,	208,0,	
208,0,	210,0,	210,0,	0,0,	
0,0,	210,0,	210,0,	210,0,	
210,0,	209,0,	209,0,	209,0,	
211,0,	211,0,	211,0,	0,0,	
0,0,	0,0,	0,0,	210,0,	
0,0,	210,0,	210,0,	210,0,	
0,0,	210,0,	209,265,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
211,0,	211,0,	211,0,	211,0,	
0,0,	209,0,	209,0,	209,0,	
211,0,	211,0,	0,0,	0,0,	
211,0,	211,0,	211,0,	211,0,	
210,0,	210,0,	210,0,	212,0,	
212,0,	212,0,	210,266,	0,0,	
0,0,	0,0,	211,0,	0,0,	
211,0,	211,0,	211,0,	0,0,	
211,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	212,0,	
212,0,	212,0,	212,0,	0,0,	
210,0,	210,0,	210,0,	212,0,	
212,0,	0,0,	0,0,	212,0,	
212,0,	212,0,	212,0,	211,0,	
211,0,	211,0,	213,0,	213,0,	
213,0,	0,0,	0,0,	0,0,	
0,0,	212,0,	0,0,	212,0,	
212,0,	212,0,	0,0,	212,0,	
211,267,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	213,0,	213,0,	
213,0,	213,0,	0,0,	211,0,	
211,0,	211,0,	213,0,	213,0,	
0,0,	0,0,	213,0,	213,0,	
213,0,	213,0,	212,0,	212,0,	
212,0,	214,0,	214,0,	214,0,	
0,0,	0,0,	0,0,	0,0,	
213,0,	0,0,	213,0,	213,0,	
213,0,	0,0,	213,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	212,268,	0,0,	
0,0,	214,0,	214,0,	214,0,	
214,0,	0,0,	212,0,	212,0,	
212,0,	214,0,	214,0,	0,0,	
0,0,	214,0,	214,0,	214,0,	
214,0,	213,0,	213,0,	213,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	214,0,	
0,0,	214,0,	214,0,	214,0,	
0,0,	214,0,	0,0,	0,0,	
213,269,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	213,0,	213,0,	213,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
214,0,	214,0,	214,0,	0,0,	
214,270,	0,0,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,67,	214,67,	214,67,	214,67,	
214,0,	214,0,	214,0,	215,0,	
215,0,	215,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	215,0,	
215,0,	215,0,	215,0,	0,0,	
0,0,	0,0,	0,0,	215,0,	
215,0,	0,0,	0,0,	215,0,	
215,0,	215,0,	215,0,	0,0,	
216,0,	216,0,	216,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	215,0,	0,0,	215,0,	
215,0,	215,0,	0,0,	215,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
216,0,	216,0,	216,0,	216,0,	
0,0,	0,0,	0,0,	0,0,	
216,0,	216,0,	0,0,	0,0,	
216,0,	216,0,	216,0,	216,0,	
0,0,	0,0,	215,0,	215,0,	
215,0,	0,0,	0,0,	0,0,	
0,0,	215,271,	216,0,	0,0,	
216,0,	216,0,	216,0,	0,0,	
216,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	217,0,	217,0,	
217,0,	0,0,	215,0,	215,0,	
215,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	216,0,	
216,0,	216,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	216,272,	217,0,	217,0,	
217,0,	217,0,	0,0,	0,0,	
0,0,	0,0,	217,0,	217,0,	
0,0,	0,0,	217,0,	217,0,	
217,0,	217,0,	218,0,	218,0,	
218,0,	0,0,	0,0,	216,0,	
216,0,	216,0,	0,0,	0,0,	
217,0,	0,0,	217,0,	217,0,	
217,0,	0,0,	217,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	218,0,	218,0,	
218,0,	218,0,	0,0,	0,0,	
0,0,	0,0,	218,0,	218,0,	
0,0,	0,0,	218,0,	218,0,	
218,0,	218,0,	0,0,	0,0,	
0,0,	217,0,	217,0,	217,0,	
0,0,	0,0,	0,0,	0,0,	
218,0,	217,273,	218,0,	218,0,	
218,0,	0,0,	218,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	219,0,	
219,0,	219,0,	0,0,	0,0,	
0,0,	217,0,	217,0,	217,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	218,0,	218,0,	218,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	219,0,	
219,0,	219,0,	219,0,	0,0,	
0,0,	0,0,	0,0,	219,0,	
219,0,	0,0,	218,274,	219,0,	
219,0,	219,0,	219,0,	220,0,	
220,0,	220,0,	0,0,	0,0,	
0,0,	218,0,	218,0,	218,0,	
0,0,	219,0,	0,0,	219,0,	
219,0,	219,0,	0,0,	219,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	220,0,	
220,0,	220,0,	220,0,	0,0,	
0,0,	0,0,	0,0,	220,0,	
220,0,	0,0,	0,0,	220,0,	
220,0,	220,0,	220,0,	0,0,	
0,0,	0,0,	219,0,	219,0,	
219,0,	0,0,	0,0,	0,0,	
0,0,	220,0,	0,0,	220,0,	
220,0,	220,0,	0,0,	220,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	219,275,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	221,0,	221,0,	221,0,	
0,0,	0,0,	219,0,	219,0,	
219,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	220,0,	220,0,	
220,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
220,276,	221,0,	221,0,	221,0,	
221,0,	0,0,	0,0,	0,0,	
0,0,	221,0,	221,0,	0,0,	
0,0,	221,0,	221,0,	221,0,	
221,0,	0,0,	0,0,	222,0,	
222,0,	222,0,	220,0,	220,0,	
220,0,	0,0,	0,0,	221,0,	
0,0,	221,0,	221,0,	221,0,	
0,0,	221,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	222,0,	
222,0,	222,0,	222,0,	0,0,	
0,0,	0,0,	0,0,	222,0,	
222,0,	0,0,	0,0,	222,0,	
222,0,	222,0,	222,0,	0,0,	
221,0,	221,0,	221,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	222,0,	221,277,	222,0,	
222,0,	222,0,	0,0,	222,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
221,0,	221,0,	221,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	222,0,	222,0,	
222,0,	223,0,	223,0,	223,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	222,278,	0,0,	0,0,	
0,0,	223,0,	223,0,	223,0,	
223,0,	0,0,	222,0,	222,0,	
222,0,	223,0,	223,0,	0,0,	
0,0,	223,0,	223,0,	223,0,	
223,0,	0,0,	0,0,	224,0,	
224,0,	224,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	223,0,	
0,0,	223,0,	223,0,	223,0,	
0,0,	223,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	224,0,	
224,0,	224,0,	224,0,	0,0,	
0,0,	0,0,	224,0,	224,0,	
224,0,	0,0,	0,0,	224,0,	
224,0,	224,0,	224,0,	0,0,	
223,0,	223,0,	223,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	224,0,	223,279,	224,0,	
224,0,	224,0,	0,0,	224,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	226,0,	
226,0,	226,0,	0,0,	0,0,	
223,0,	223,0,	223,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	224,0,	224,0,	
224,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	226,0,	
226,0,	226,0,	226,0,	0,0,	
224,280,	0,0,	226,0,	226,0,	
226,0,	0,0,	0,0,	226,0,	
226,0,	226,0,	226,0,	227,0,	
227,0,	227,0,	0,0,	0,0,	
0,0,	0,0,	224,0,	224,0,	
224,0,	226,0,	0,0,	226,0,	
226,0,	226,0,	0,0,	226,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	227,0,	
227,0,	227,0,	227,0,	0,0,	
0,0,	0,0,	227,0,	227,0,	
227,0,	0,0,	0,0,	227,0,	
227,0,	227,0,	227,0,	0,0,	
0,0,	0,0,	226,0,	226,0,	
226,0,	0,0,	0,0,	0,0,	
0,0,	227,0,	0,0,	227,0,	
227,0,	227,0,	0,0,	227,0,	
0,0,	226,282,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	228,0,	
228,0,	228,0,	0,0,	0,0,	
0,0,	0,0,	226,0,	226,0,	
226,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	227,0,	227,0,	
227,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	228,0,	
228,0,	228,0,	228,0,	0,0,	
0,0,	0,0,	228,0,	228,0,	
228,0,	0,0,	0,0,	228,0,	
228,0,	228,0,	228,0,	227,283,	
229,0,	229,0,	229,0,	0,0,	
0,0,	0,0,	227,0,	227,0,	
227,0,	228,0,	0,0,	228,0,	
228,0,	228,0,	0,0,	228,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
229,0,	229,0,	229,0,	229,0,	
0,0,	0,0,	0,0,	229,0,	
229,0,	229,0,	0,0,	0,0,	
229,0,	229,0,	229,0,	229,0,	
0,0,	0,0,	228,0,	228,0,	
228,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	229,0,	0,0,	
229,0,	229,0,	229,0,	0,0,	
229,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	228,284,	0,0,	
0,0,	0,0,	230,0,	230,0,	
230,0,	0,0,	228,0,	228,0,	
228,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	229,0,	
229,0,	229,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	229,285,	230,0,	230,0,	
230,0,	230,0,	0,0,	0,0,	
0,0,	230,0,	230,0,	230,0,	
0,0,	0,0,	230,0,	230,0,	
230,0,	230,0,	231,0,	231,0,	
231,0,	0,0,	0,0,	229,0,	
229,0,	229,0,	0,0,	0,0,	
230,0,	0,0,	230,0,	230,0,	
230,0,	0,0,	230,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	231,0,	231,0,	
231,0,	231,0,	0,0,	0,0,	
0,0,	231,0,	231,0,	231,0,	
0,0,	0,0,	231,0,	231,0,	
231,0,	231,0,	0,0,	0,0,	
0,0,	230,0,	230,0,	230,0,	
0,0,	0,0,	0,0,	0,0,	
231,0,	0,0,	231,0,	231,0,	
231,0,	0,0,	231,0,	230,286,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
232,0,	232,0,	232,0,	0,0,	
0,0,	230,0,	230,0,	230,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	231,0,	231,0,	231,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	231,287,	
232,0,	232,0,	232,0,	232,0,	
0,0,	0,0,	0,0,	232,0,	
232,0,	232,0,	0,0,	0,0,	
232,0,	232,0,	232,0,	232,0,	
233,0,	233,0,	233,0,	0,0,	
0,0,	231,0,	231,0,	231,0,	
0,0,	0,0,	232,0,	0,0,	
232,0,	232,0,	232,0,	0,0,	
232,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
233,0,	233,0,	233,0,	233,0,	
0,0,	0,0,	0,0,	233,0,	
233,0,	233,0,	0,0,	0,0,	
233,0,	233,0,	233,0,	233,0,	
0,0,	0,0,	0,0,	232,0,	
232,0,	232,0,	0,0,	0,0,	
0,0,	0,0,	233,0,	0,0,	
233,0,	233,0,	233,0,	0,0,	
233,0,	0,0,	0,0,	0,0,	
232,288,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
234,0,	234,0,	234,0,	0,0,	
0,0,	0,0,	0,0,	232,0,	
232,0,	232,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	233,0,	
233,0,	233,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
234,0,	234,0,	234,0,	234,0,	
0,0,	0,0,	0,0,	234,0,	
234,0,	234,0,	0,0,	0,0,	
234,0,	234,0,	234,0,	234,0,	
235,0,	235,0,	235,0,	0,0,	
0,0,	0,0,	0,0,	233,0,	
233,0,	233,0,	234,0,	0,0,	
234,0,	234,0,	234,0,	0,0,	
234,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
235,0,	235,0,	235,0,	235,0,	
0,0,	0,0,	0,0,	235,0,	
235,0,	235,0,	0,0,	0,0,	
235,0,	235,0,	235,0,	235,0,	
0,0,	0,0,	0,0,	234,0,	
234,0,	234,0,	0,0,	0,0,	
0,0,	0,0,	235,0,	0,0,	
235,0,	235,0,	235,0,	0,0,	
235,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
234,289,	0,0,	236,0,	236,0,	
236,0,	0,0,	0,0,	234,0,	
234,0,	234,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	235,0,	
235,0,	235,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	235,290,	236,0,	236,0,	
236,0,	236,0,	0,0,	0,0,	
0,0,	236,0,	236,0,	236,0,	
0,0,	0,0,	236,0,	236,0,	
236,0,	236,0,	237,0,	237,0,	
237,0,	0,0,	0,0,	235,0,	
235,0,	235,0,	0,0,	0,0,	
236,0,	0,0,	236,0,	236,0,	
236,0,	0,0,	236,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	237,0,	237,0,	
237,0,	237,0,	0,0,	0,0,	
0,0,	237,0,	237,0,	237,0,	
0,0,	0,0,	237,0,	237,0,	
237,0,	237,0,	0,0,	0,0,	
0,0,	236,0,	236,0,	236,0,	
0,0,	0,0,	0,0,	0,0,	
237,0,	0,0,	237,0,	237,0,	
237,0,	0,0,	237,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
238,0,	238,0,	238,0,	0,0,	
0,0,	236,0,	236,0,	236,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	237,0,	237,0,	237,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	237,291,	
238,0,	238,0,	238,0,	238,0,	
0,0,	0,0,	0,0,	238,0,	
238,0,	238,0,	0,0,	0,0,	
238,0,	238,0,	238,0,	238,0,	
0,0,	0,0,	239,0,	239,0,	
239,0,	237,0,	237,0,	237,0,	
0,0,	0,0,	238,0,	0,0,	
238,0,	238,0,	238,0,	0,0,	
238,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	239,0,	239,0,	
239,0,	239,0,	0,0,	0,0,	
0,0,	239,0,	239,0,	239,0,	
0,0,	0,0,	239,0,	239,0,	
239,0,	239,0,	0,0,	238,0,	
238,0,	238,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
239,0,	238,292,	239,0,	239,0,	
239,0,	0,0,	239,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
240,0,	240,0,	240,0,	238,0,	
238,0,	238,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	239,0,	239,0,	239,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	239,293,	
240,0,	240,0,	240,0,	240,0,	
0,0,	0,0,	0,0,	240,0,	
240,0,	240,0,	0,0,	0,0,	
240,0,	240,0,	240,0,	240,0,	
241,0,	241,0,	241,0,	0,0,	
0,0,	239,0,	239,0,	239,0,	
0,0,	0,0,	240,0,	0,0,	
240,0,	240,0,	240,0,	0,0,	
240,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
241,0,	241,0,	241,0,	241,0,	
0,0,	0,0,	0,0,	241,0,	
241,0,	241,0,	0,0,	0,0,	
241,0,	241,0,	241,0,	241,0,	
0,0,	0,0,	0,0,	240,0,	
240,0,	240,0,	0,0,	0,0,	
0,0,	0,0,	241,0,	240,294,	
241,0,	241,0,	241,0,	0,0,	
241,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	242,0,	242,0,	
242,0,	0,0,	0,0,	240,0,	
240,0,	240,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	241,0,	
241,0,	241,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	241,295,	242,0,	242,0,	
242,0,	242,0,	0,0,	0,0,	
0,0,	242,0,	242,0,	242,0,	
0,0,	0,0,	242,0,	242,0,	
242,0,	242,0,	243,0,	243,0,	
243,0,	0,0,	0,0,	241,0,	
241,0,	241,0,	0,0,	0,0,	
242,0,	0,0,	242,0,	242,0,	
242,0,	0,0,	242,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	243,0,	243,0,	
243,0,	243,0,	0,0,	0,0,	
0,0,	243,0,	243,0,	243,0,	
0,0,	0,0,	243,0,	243,0,	
243,0,	243,0,	0,0,	0,0,	
0,0,	242,0,	242,0,	242,0,	
0,0,	0,0,	0,0,	0,0,	
243,0,	0,0,	243,0,	243,0,	
243,0,	0,0,	243,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	242,296,	0,0,	0,0,	
0,0,	0,0,	244,0,	244,0,	
244,0,	0,0,	0,0,	0,0,	
0,0,	242,0,	242,0,	242,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	243,0,	243,0,	243,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	244,0,	244,0,	
244,0,	244,0,	0,0,	0,0,	
0,0,	244,0,	244,0,	244,0,	
0,0,	0,0,	244,0,	244,0,	
244,0,	244,0,	243,297,	245,0,	
245,0,	245,0,	0,0,	0,0,	
0,0,	243,0,	243,0,	243,0,	
244,0,	0,0,	244,0,	244,0,	
244,0,	0,0,	244,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	245,0,	
245,0,	245,0,	245,0,	0,0,	
0,0,	0,0,	245,0,	245,0,	
245,0,	0,0,	0,0,	245,0,	
245,0,	245,0,	245,0,	0,0,	
0,0,	244,0,	244,0,	244,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	245,0,	0,0,	245,0,	
245,0,	245,0,	0,0,	245,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	246,0,	
246,0,	246,0,	0,0,	0,0,	
0,0,	244,0,	244,0,	244,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	245,0,	245,0,	
245,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	246,0,	
246,0,	246,0,	246,0,	0,0,	
0,0,	0,0,	246,0,	246,0,	
246,0,	0,0,	0,0,	246,0,	
246,0,	246,0,	246,0,	247,0,	
247,0,	247,0,	0,0,	0,0,	
0,0,	0,0,	245,0,	245,0,	
245,0,	246,0,	0,0,	246,0,	
246,0,	246,0,	0,0,	246,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	247,0,	
247,0,	247,0,	247,0,	0,0,	
0,0,	0,0,	247,0,	247,0,	
247,0,	0,0,	0,0,	247,0,	
247,0,	247,0,	247,0,	0,0,	
0,0,	0,0,	246,0,	246,0,	
246,0,	0,0,	0,0,	0,0,	
0,0,	247,0,	246,298,	247,0,	
247,0,	247,0,	0,0,	247,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	246,0,	246,0,	
246,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	247,0,	247,0,	
247,0,	0,0,	247,299,	0,0,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,9,	247,9,	
247,9,	247,9,	247,0,	247,0,	
247,0,	256,0,	256,0,	256,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	256,0,	256,0,	256,0,	
256,0,	0,0,	0,0,	0,0,	
0,0,	256,0,	256,0,	0,0,	
0,0,	256,0,	256,0,	256,0,	
256,0,	258,0,	258,0,	258,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	256,0,	
0,0,	256,0,	256,0,	256,0,	
0,0,	256,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	258,0,	258,0,	258,0,	
258,0,	0,0,	0,0,	0,0,	
0,0,	258,0,	258,0,	0,0,	
0,0,	258,0,	258,0,	258,0,	
258,0,	0,0,	0,0,	0,0,	
256,0,	256,0,	256,0,	0,0,	
0,0,	0,0,	0,0,	258,0,	
0,0,	258,0,	258,0,	258,0,	
0,0,	258,0,	256,305,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	259,0,	259,0,	259,0,	
0,0,	0,0,	0,0,	0,0,	
256,0,	256,0,	256,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
258,0,	258,0,	258,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	259,0,	259,0,	259,0,	
259,0,	0,0,	0,0,	258,307,	
0,0,	259,0,	259,0,	0,0,	
0,0,	259,0,	259,0,	259,0,	
259,0,	260,0,	260,0,	260,0,	
0,0,	0,0,	0,0,	0,0,	
258,0,	258,0,	258,0,	259,0,	
0,0,	259,0,	259,0,	259,0,	
0,0,	259,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	260,0,	260,0,	260,0,	
260,0,	0,0,	0,0,	0,0,	
0,0,	260,0,	260,0,	0,0,	
0,0,	260,0,	260,0,	260,0,	
260,0,	0,0,	0,0,	0,0,	
259,0,	259,0,	259,0,	0,0,	
0,0,	0,0,	0,0,	260,0,	
0,0,	260,0,	260,0,	260,0,	
0,0,	260,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	259,308,	0,0,	0,0,	
0,0,	261,0,	261,0,	261,0,	
259,0,	259,0,	259,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
260,0,	260,0,	260,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	261,0,	261,0,	261,0,	
261,0,	0,0,	0,0,	0,0,	
0,0,	261,0,	261,0,	0,0,	
260,309,	261,0,	261,0,	261,0,	
261,0,	0,0,	0,0,	0,0,	
260,0,	260,0,	260,0,	0,0,	
0,0,	0,0,	0,0,	261,0,	
0,0,	261,0,	261,0,	261,0,	
0,0,	261,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	262,0,	
262,0,	262,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
261,0,	261,0,	261,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	261,310,	262,0,	
262,0,	262,0,	262,0,	0,0,	
0,0,	0,0,	0,0,	262,0,	
262,0,	0,0,	0,0,	262,0,	
262,0,	262,0,	262,0,	263,0,	
263,0,	263,0,	0,0,	0,0,	
261,0,	261,0,	261,0,	0,0,	
0,0,	262,0,	0,0,	262,0,	
262,0,	262,0,	0,0,	262,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	263,0,	
263,0,	263,0,	263,0,	0,0,	
0,0,	0,0,	0,0,	263,0,	
263,0,	0,0,	0,0,	263,0,	
263,0,	263,0,	263,0,	0,0,	
0,0,	0,0,	262,0,	262,0,	
262,0,	0,0,	0,0,	0,0,	
0,0,	263,0,	0,0,	263,0,	
263,0,	263,0,	0,0,	263,0,	
262,311,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	264,0,	264,0,	264,0,	
0,0,	0,0,	262,0,	262,0,	
262,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	263,0,	263,0,	
263,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
263,312,	264,0,	264,0,	264,0,	
264,0,	0,0,	0,0,	0,0,	
0,0,	264,0,	264,0,	0,0,	
0,0,	264,0,	264,0,	264,0,	
264,0,	265,0,	265,0,	265,0,	
0,0,	0,0,	263,0,	263,0,	
263,0,	0,0,	0,0,	264,0,	
0,0,	264,0,	264,0,	264,0,	
0,0,	264,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	265,0,	265,0,	265,0,	
265,0,	0,0,	0,0,	0,0,	
0,0,	265,0,	265,0,	0,0,	
0,0,	265,0,	265,0,	265,0,	
265,0,	0,0,	0,0,	0,0,	
264,0,	264,0,	264,0,	0,0,	
0,0,	0,0,	0,0,	265,0,	
0,0,	265,0,	265,0,	265,0,	
0,0,	265,0,	0,0,	0,0,	
0,0,	264,313,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	266,0,	266,0,	266,0,	
0,0,	0,0,	0,0,	0,0,	
264,0,	264,0,	264,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
265,0,	265,0,	265,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	266,0,	266,0,	266,0,	
266,0,	0,0,	0,0,	0,0,	
0,0,	266,0,	266,0,	0,0,	
0,0,	266,0,	266,0,	266,0,	
266,0,	267,0,	267,0,	267,0,	
0,0,	0,0,	0,0,	0,0,	
265,0,	265,0,	265,0,	266,0,	
0,0,	266,0,	266,0,	266,0,	
0,0,	266,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	267,0,	267,0,	267,0,	
267,0,	0,0,	0,0,	0,0,	
0,0,	267,0,	267,0,	0,0,	
0,0,	267,0,	267,0,	267,0,	
267,0,	0,0,	0,0,	0,0,	
266,0,	266,0,	266,0,	0,0,	
0,0,	0,0,	0,0,	267,0,	
0,0,	267,0,	267,0,	267,0,	
0,0,	267,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	266,314,	0,0,	268,0,	
268,0,	268,0,	0,0,	0,0,	
266,0,	266,0,	266,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
267,0,	267,0,	267,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	267,315,	268,0,	
268,0,	268,0,	268,0,	0,0,	
0,0,	0,0,	0,0,	268,0,	
268,0,	0,0,	0,0,	268,0,	
268,0,	268,0,	268,0,	269,0,	
269,0,	269,0,	0,0,	0,0,	
267,0,	267,0,	267,0,	0,0,	
0,0,	268,0,	0,0,	268,0,	
268,0,	268,0,	0,0,	268,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	269,0,	
269,0,	269,0,	269,0,	0,0,	
0,0,	0,0,	0,0,	269,0,	
269,0,	0,0,	0,0,	269,0,	
269,0,	269,0,	269,0,	0,0,	
0,0,	0,0,	268,0,	268,0,	
268,0,	0,0,	0,0,	0,0,	
0,0,	269,0,	0,0,	269,0,	
269,0,	269,0,	0,0,	269,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	270,0,	270,0,	270,0,	
0,0,	0,0,	268,0,	268,0,	
268,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	269,0,	269,0,	
269,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
269,316,	270,0,	270,0,	270,0,	
270,0,	0,0,	0,0,	0,0,	
0,0,	270,0,	270,0,	0,0,	
0,0,	270,0,	270,0,	270,0,	
270,0,	0,0,	0,0,	271,0,	
271,0,	271,0,	269,0,	269,0,	
269,0,	0,0,	0,0,	270,0,	
0,0,	270,0,	270,0,	270,0,	
0,0,	270,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	271,0,	
271,0,	271,0,	271,0,	0,0,	
0,0,	0,0,	0,0,	271,0,	
271,0,	0,0,	0,0,	271,0,	
271,0,	271,0,	271,0,	0,0,	
270,0,	270,0,	270,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	271,0,	270,317,	271,0,	
271,0,	271,0,	0,0,	271,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	272,0,	272,0,	272,0,	
270,0,	270,0,	270,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	271,0,	271,0,	
271,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
271,318,	272,0,	272,0,	272,0,	
272,0,	0,0,	0,0,	0,0,	
0,0,	272,0,	272,0,	0,0,	
0,0,	272,0,	272,0,	272,0,	
272,0,	273,0,	273,0,	273,0,	
0,0,	0,0,	271,0,	271,0,	
271,0,	0,0,	0,0,	272,0,	
0,0,	272,0,	272,0,	272,0,	
0,0,	272,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	273,0,	273,0,	273,0,	
273,0,	0,0,	0,0,	0,0,	
0,0,	273,0,	273,0,	0,0,	
0,0,	273,0,	273,0,	273,0,	
273,0,	0,0,	0,0,	0,0,	
272,0,	272,0,	272,0,	0,0,	
0,0,	0,0,	0,0,	273,0,	
272,319,	273,0,	273,0,	273,0,	
0,0,	273,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	274,0,	
274,0,	274,0,	0,0,	0,0,	
272,0,	272,0,	272,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
273,0,	273,0,	273,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	273,320,	274,0,	
274,0,	274,0,	274,0,	0,0,	
0,0,	0,0,	0,0,	274,0,	
274,0,	0,0,	0,0,	274,0,	
274,0,	274,0,	274,0,	275,0,	
275,0,	275,0,	0,0,	0,0,	
273,0,	273,0,	273,0,	0,0,	
0,0,	274,0,	0,0,	274,0,	
274,0,	274,0,	0,0,	274,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	275,0,	
275,0,	275,0,	275,0,	0,0,	
0,0,	0,0,	0,0,	275,0,	
275,0,	0,0,	0,0,	275,0,	
275,0,	275,0,	275,0,	0,0,	
0,0,	0,0,	274,0,	274,0,	
274,0,	0,0,	0,0,	0,0,	
0,0,	275,0,	0,0,	275,0,	
275,0,	275,0,	0,0,	275,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	274,321,	0,0,	
0,0,	0,0,	0,0,	276,0,	
276,0,	276,0,	0,0,	0,0,	
0,0,	0,0,	274,0,	274,0,	
274,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	275,0,	275,0,	
275,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	276,0,	
276,0,	276,0,	276,0,	0,0,	
0,0,	0,0,	0,0,	276,0,	
276,0,	0,0,	0,0,	276,0,	
276,0,	276,0,	276,0,	275,322,	
277,0,	277,0,	277,0,	0,0,	
0,0,	0,0,	275,0,	275,0,	
275,0,	276,0,	0,0,	276,0,	
276,0,	276,0,	0,0,	276,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
277,0,	277,0,	277,0,	277,0,	
0,0,	0,0,	0,0,	0,0,	
277,0,	277,0,	0,0,	0,0,	
277,0,	277,0,	277,0,	277,0,	
0,0,	0,0,	276,0,	276,0,	
276,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	277,0,	0,0,	
277,0,	277,0,	277,0,	0,0,	
277,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
278,0,	278,0,	278,0,	0,0,	
0,0,	0,0,	276,0,	276,0,	
276,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	277,0,	
277,0,	277,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
278,0,	278,0,	278,0,	278,0,	
0,0,	0,0,	0,0,	0,0,	
278,0,	278,0,	0,0,	0,0,	
278,0,	278,0,	278,0,	278,0,	
279,0,	279,0,	279,0,	0,0,	
0,0,	0,0,	0,0,	277,0,	
277,0,	277,0,	278,0,	0,0,	
278,0,	278,0,	278,0,	0,0,	
278,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
279,0,	279,0,	279,0,	279,0,	
0,0,	0,0,	0,0,	0,0,	
279,0,	279,0,	0,0,	0,0,	
279,0,	279,0,	279,0,	279,0,	
0,0,	0,0,	0,0,	278,0,	
278,0,	278,0,	0,0,	0,0,	
0,0,	0,0,	279,0,	278,323,	
279,0,	279,0,	279,0,	0,0,	
279,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	278,0,	
278,0,	278,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	279,0,	
279,0,	279,0,	0,0,	279,324,	
0,0,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,67,	
279,67,	279,67,	279,67,	279,0,	
279,0,	279,0,	280,0,	280,0,	
280,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	280,0,	280,0,	
280,0,	280,0,	0,0,	0,0,	
0,0,	280,0,	280,0,	280,0,	
0,0,	0,0,	280,0,	280,0,	
280,0,	280,0,	282,0,	282,0,	
282,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
280,0,	0,0,	280,0,	280,0,	
280,0,	0,0,	280,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	282,0,	282,0,	
282,0,	282,0,	0,0,	0,0,	
0,0,	282,0,	282,0,	282,0,	
0,0,	0,0,	282,0,	282,0,	
282,0,	282,0,	0,0,	0,0,	
0,0,	280,0,	280,0,	280,0,	
0,0,	0,0,	0,0,	0,0,	
282,0,	0,0,	282,0,	282,0,	
282,0,	0,0,	282,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
280,325,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
283,0,	283,0,	283,0,	0,0,	
0,0,	280,0,	280,0,	280,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	282,0,	282,0,	282,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	282,327,	
283,0,	283,0,	283,0,	283,0,	
0,0,	0,0,	0,0,	283,0,	
283,0,	283,0,	0,0,	0,0,	
283,0,	283,0,	283,0,	283,0,	
284,0,	284,0,	284,0,	0,0,	
0,0,	282,0,	282,0,	282,0,	
0,0,	0,0,	283,0,	0,0,	
283,0,	283,0,	283,0,	0,0,	
283,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
284,0,	284,0,	284,0,	284,0,	
0,0,	0,0,	0,0,	284,0,	
284,0,	284,0,	0,0,	0,0,	
284,0,	284,0,	284,0,	284,0,	
0,0,	0,0,	0,0,	283,0,	
283,0,	283,0,	0,0,	0,0,	
0,0,	0,0,	284,0,	0,0,	
284,0,	284,0,	284,0,	0,0,	
284,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
285,0,	285,0,	285,0,	0,0,	
0,0,	0,0,	0,0,	283,0,	
283,0,	283,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	284,0,	
284,0,	284,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
285,0,	285,0,	285,0,	285,0,	
0,0,	0,0,	0,0,	285,0,	
285,0,	285,0,	0,0,	0,0,	
285,0,	285,0,	285,0,	285,0,	
286,0,	286,0,	286,0,	0,0,	
0,0,	0,0,	0,0,	284,0,	
284,0,	284,0,	285,0,	0,0,	
285,0,	285,0,	285,0,	0,0,	
285,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
286,0,	286,0,	286,0,	286,0,	
0,0,	0,0,	0,0,	286,0,	
286,0,	286,0,	0,0,	0,0,	
286,0,	286,0,	286,0,	286,0,	
0,0,	0,0,	0,0,	285,0,	
285,0,	285,0,	0,0,	0,0,	
0,0,	0,0,	286,0,	0,0,	
286,0,	286,0,	286,0,	0,0,	
286,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
287,0,	287,0,	287,0,	0,0,	
0,0,	0,0,	0,0,	285,0,	
285,0,	285,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	286,0,	
286,0,	286,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
287,0,	287,0,	287,0,	287,0,	
0,0,	0,0,	0,0,	287,0,	
287,0,	287,0,	0,0,	0,0,	
287,0,	287,0,	287,0,	287,0,	
286,328,	288,0,	288,0,	288,0,	
0,0,	0,0,	0,0,	286,0,	
286,0,	286,0,	287,0,	0,0,	
287,0,	287,0,	287,0,	0,0,	
287,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	288,0,	288,0,	288,0,	
288,0,	0,0,	0,0,	0,0,	
288,0,	288,0,	288,0,	0,0,	
0,0,	288,0,	288,0,	288,0,	
288,0,	0,0,	0,0,	287,0,	
287,0,	287,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	288,0,	
0,0,	288,0,	288,0,	288,0,	
0,0,	288,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	287,329,	0,0,	
0,0,	289,0,	289,0,	289,0,	
0,0,	0,0,	0,0,	287,0,	
287,0,	287,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
288,0,	288,0,	288,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	289,0,	289,0,	289,0,	
289,0,	0,0,	0,0,	0,0,	
289,0,	289,0,	289,0,	0,0,	
0,0,	289,0,	289,0,	289,0,	
289,0,	0,0,	0,0,	290,0,	
290,0,	290,0,	0,0,	0,0,	
288,0,	288,0,	288,0,	289,0,	
0,0,	289,0,	289,0,	289,0,	
0,0,	289,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	290,0,	
290,0,	290,0,	290,0,	0,0,	
0,0,	0,0,	290,0,	290,0,	
290,0,	0,0,	0,0,	290,0,	
290,0,	290,0,	290,0,	0,0,	
289,0,	289,0,	289,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	290,0,	289,330,	290,0,	
290,0,	290,0,	0,0,	290,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
289,0,	289,0,	289,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	290,0,	290,0,	
290,0,	0,0,	291,0,	291,0,	
291,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
290,331,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	291,0,	291,0,	
291,0,	291,0,	290,0,	290,0,	
290,0,	291,0,	291,0,	291,0,	
0,0,	0,0,	291,0,	291,0,	
291,0,	291,0,	292,0,	292,0,	
292,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
291,0,	0,0,	291,0,	291,0,	
291,0,	0,0,	291,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	292,0,	292,0,	
292,0,	292,0,	0,0,	0,0,	
0,0,	292,0,	292,0,	292,0,	
0,0,	0,0,	292,0,	292,0,	
292,0,	292,0,	0,0,	0,0,	
0,0,	291,0,	291,0,	291,0,	
0,0,	0,0,	0,0,	0,0,	
292,0,	0,0,	292,0,	292,0,	
292,0,	0,0,	292,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
291,332,	0,0,	0,0,	0,0,	
293,0,	293,0,	293,0,	0,0,	
0,0,	291,0,	291,0,	291,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	292,0,	292,0,	292,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
293,0,	293,0,	293,0,	293,0,	
0,0,	0,0,	0,0,	293,0,	
293,0,	293,0,	0,0,	292,333,	
293,0,	293,0,	293,0,	293,0,	
294,0,	294,0,	294,0,	0,0,	
0,0,	292,0,	292,0,	292,0,	
0,0,	0,0,	293,0,	0,0,	
293,0,	293,0,	293,0,	0,0,	
293,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
294,0,	294,0,	294,0,	294,0,	
0,0,	0,0,	0,0,	294,0,	
294,0,	294,0,	0,0,	0,0,	
294,0,	294,0,	294,0,	294,0,	
0,0,	0,0,	0,0,	293,0,	
293,0,	293,0,	0,0,	0,0,	
0,0,	0,0,	294,0,	0,0,	
294,0,	294,0,	294,0,	0,0,	
294,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	293,334,	0,0,	
295,0,	295,0,	295,0,	0,0,	
0,0,	0,0,	0,0,	293,0,	
293,0,	293,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	294,0,	
294,0,	294,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
295,0,	295,0,	295,0,	295,0,	
0,0,	0,0,	0,0,	295,0,	
295,0,	295,0,	0,0,	0,0,	
295,0,	295,0,	295,0,	295,0,	
294,335,	296,0,	296,0,	296,0,	
0,0,	0,0,	0,0,	294,0,	
294,0,	294,0,	295,0,	0,0,	
295,0,	295,0,	295,0,	0,0,	
295,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	296,0,	296,0,	296,0,	
296,0,	0,0,	0,0,	0,0,	
296,0,	296,0,	296,0,	0,0,	
0,0,	296,0,	296,0,	296,0,	
296,0,	0,0,	0,0,	295,0,	
295,0,	295,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	296,0,	
0,0,	296,0,	296,0,	296,0,	
0,0,	296,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	295,0,	
295,0,	295,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
296,0,	296,0,	296,0,	0,0,	
297,0,	297,0,	297,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
296,336,	0,0,	0,0,	0,0,	
297,0,	297,0,	297,0,	297,0,	
296,0,	296,0,	296,0,	297,0,	
297,0,	297,0,	0,0,	0,0,	
297,0,	297,0,	297,0,	297,0,	
298,0,	298,0,	298,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	297,0,	0,0,	
297,0,	297,0,	297,0,	0,0,	
297,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
298,0,	298,0,	298,0,	298,0,	
0,0,	0,0,	0,0,	298,0,	
298,0,	298,0,	0,0,	0,0,	
298,0,	298,0,	298,0,	298,0,	
0,0,	0,0,	0,0,	297,0,	
297,0,	297,0,	0,0,	0,0,	
0,0,	0,0,	298,0,	0,0,	
298,0,	298,0,	298,0,	0,0,	
298,0,	297,337,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	299,0,	299,0,	
299,0,	0,0,	0,0,	297,0,	
297,0,	297,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	298,0,	
298,0,	298,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	298,338,	299,0,	299,0,	
299,0,	299,0,	0,0,	0,0,	
0,0,	299,0,	299,0,	299,0,	
0,0,	0,0,	299,0,	299,0,	
299,0,	299,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	298,0,	
298,0,	298,0,	0,0,	0,0,	
299,0,	0,0,	299,0,	299,0,	
299,0,	0,0,	299,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	305,0,	
305,0,	305,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	299,0,	299,0,	299,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
299,339,	0,0,	0,0,	305,0,	
305,0,	305,0,	305,0,	0,0,	
0,0,	0,0,	0,0,	305,0,	
305,0,	0,0,	299,340,	305,0,	
305,0,	305,0,	305,0,	0,0,	
0,0,	299,0,	299,0,	299,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	305,0,	0,0,	305,0,	
305,0,	305,0,	0,0,	305,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	307,0,	
307,0,	307,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	305,0,	305,0,	
305,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	307,0,	
307,0,	307,0,	307,0,	0,0,	
0,0,	0,0,	0,0,	307,0,	
307,0,	305,345,	0,0,	307,0,	
307,0,	307,0,	307,0,	0,0,	
0,0,	308,0,	308,0,	308,0,	
0,0,	0,0,	305,0,	305,0,	
305,0,	307,0,	0,0,	307,0,	
307,0,	307,0,	0,0,	307,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	308,0,	308,0,	308,0,	
308,0,	0,0,	0,0,	0,0,	
0,0,	308,0,	308,0,	0,0,	
0,0,	308,0,	308,0,	308,0,	
308,0,	0,0,	307,0,	307,0,	
307,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	308,0,	
307,347,	308,0,	308,0,	308,0,	
0,0,	308,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	309,0,	309,0,	309,0,	
0,0,	0,0,	307,0,	307,0,	
307,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
308,0,	308,0,	308,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	309,0,	309,0,	309,0,	
309,0,	0,0,	0,0,	0,0,	
0,0,	309,0,	309,0,	0,0,	
0,0,	309,0,	309,0,	309,0,	
309,0,	310,0,	310,0,	310,0,	
0,0,	0,0,	0,0,	0,0,	
308,0,	308,0,	308,0,	309,0,	
0,0,	309,0,	309,0,	309,0,	
0,0,	309,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	310,0,	310,0,	310,0,	
310,0,	0,0,	0,0,	0,0,	
0,0,	310,0,	310,0,	0,0,	
0,0,	310,0,	310,0,	310,0,	
310,0,	0,0,	0,0,	0,0,	
309,0,	309,0,	309,0,	0,0,	
0,0,	0,0,	0,0,	310,0,	
0,0,	310,0,	310,0,	310,0,	
0,0,	310,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	311,0,	311,0,	311,0,	
0,0,	0,0,	0,0,	0,0,	
309,0,	309,0,	309,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
310,0,	310,0,	310,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	311,0,	311,0,	311,0,	
311,0,	0,0,	0,0,	0,0,	
0,0,	311,0,	311,0,	0,0,	
0,0,	311,0,	311,0,	311,0,	
311,0,	312,0,	312,0,	312,0,	
0,0,	0,0,	0,0,	0,0,	
310,0,	310,0,	310,0,	311,0,	
0,0,	311,0,	311,0,	311,0,	
0,0,	311,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	312,0,	312,0,	312,0,	
312,0,	0,0,	0,0,	0,0,	
0,0,	312,0,	312,0,	0,0,	
0,0,	312,0,	312,0,	312,0,	
312,0,	0,0,	0,0,	0,0,	
311,0,	311,0,	311,0,	0,0,	
0,0,	0,0,	0,0,	312,0,	
0,0,	312,0,	312,0,	312,0,	
0,0,	312,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	311,348,	0,0,	0,0,	
313,0,	313,0,	313,0,	0,0,	
311,0,	311,0,	311,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
312,0,	312,0,	312,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
313,0,	313,0,	313,0,	313,0,	
0,0,	0,0,	0,0,	0,0,	
313,0,	313,0,	0,0,	312,349,	
313,0,	313,0,	313,0,	313,0,	
314,0,	314,0,	314,0,	0,0,	
312,0,	312,0,	312,0,	0,0,	
0,0,	0,0,	313,0,	0,0,	
313,0,	313,0,	313,0,	0,0,	
313,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
314,0,	314,0,	314,0,	314,0,	
0,0,	0,0,	0,0,	0,0,	
314,0,	314,0,	0,0,	0,0,	
314,0,	314,0,	314,0,	314,0,	
0,0,	0,0,	0,0,	313,0,	
313,0,	313,0,	0,0,	0,0,	
0,0,	0,0,	314,0,	0,0,	
314,0,	314,0,	314,0,	0,0,	
314,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	315,0,	315,0,	
315,0,	0,0,	0,0,	313,0,	
313,0,	313,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	314,0,	
314,0,	314,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	314,350,	315,0,	315,0,	
315,0,	315,0,	0,0,	0,0,	
0,0,	0,0,	315,0,	315,0,	
0,0,	0,0,	315,0,	315,0,	
315,0,	315,0,	316,0,	316,0,	
316,0,	0,0,	0,0,	314,0,	
314,0,	314,0,	0,0,	0,0,	
315,0,	0,0,	315,0,	315,0,	
315,0,	0,0,	315,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	316,0,	316,0,	
316,0,	316,0,	0,0,	0,0,	
0,0,	0,0,	316,0,	316,0,	
0,0,	0,0,	316,0,	316,0,	
316,0,	316,0,	0,0,	0,0,	
0,0,	315,0,	315,0,	315,0,	
0,0,	0,0,	0,0,	0,0,	
316,0,	0,0,	316,0,	316,0,	
316,0,	0,0,	316,0,	0,0,	
0,0,	0,0,	0,0,	315,351,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	317,0,	317,0,	317,0,	
0,0,	315,0,	315,0,	315,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	316,0,	316,0,	316,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	317,0,	317,0,	317,0,	
317,0,	0,0,	0,0,	0,0,	
0,0,	317,0,	317,0,	0,0,	
316,352,	317,0,	317,0,	317,0,	
317,0,	318,0,	318,0,	318,0,	
0,0,	316,0,	316,0,	316,0,	
0,0,	0,0,	0,0,	317,0,	
0,0,	317,0,	317,0,	317,0,	
0,0,	317,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	318,0,	318,0,	318,0,	
318,0,	0,0,	0,0,	0,0,	
0,0,	318,0,	318,0,	0,0,	
0,0,	318,0,	318,0,	318,0,	
318,0,	0,0,	0,0,	0,0,	
317,0,	317,0,	317,0,	0,0,	
0,0,	0,0,	0,0,	318,0,	
0,0,	318,0,	318,0,	318,0,	
0,0,	318,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	317,353,	0,0,	
0,0,	0,0,	0,0,	0,0,	
319,0,	319,0,	319,0,	0,0,	
317,0,	317,0,	317,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
318,0,	318,0,	318,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
319,0,	319,0,	319,0,	319,0,	
0,0,	0,0,	0,0,	0,0,	
319,0,	319,0,	0,0,	318,354,	
319,0,	319,0,	319,0,	319,0,	
320,0,	320,0,	320,0,	0,0,	
318,0,	318,0,	318,0,	0,0,	
0,0,	0,0,	319,0,	0,0,	
319,0,	319,0,	319,0,	0,0,	
319,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
320,0,	320,0,	320,0,	320,0,	
0,0,	0,0,	0,0,	0,0,	
320,0,	320,0,	0,0,	0,0,	
320,0,	320,0,	320,0,	320,0,	
0,0,	0,0,	0,0,	319,0,	
319,0,	319,0,	0,0,	0,0,	
0,0,	0,0,	320,0,	0,0,	
320,0,	320,0,	320,0,	0,0,	
320,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
319,355,	321,0,	321,0,	321,0,	
0,0,	0,0,	0,0,	319,0,	
319,0,	319,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	320,0,	
320,0,	320,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	321,0,	321,0,	321,0,	
321,0,	0,0,	0,0,	0,0,	
0,0,	321,0,	321,0,	0,0,	
0,0,	321,0,	321,0,	321,0,	
321,0,	322,0,	322,0,	322,0,	
0,0,	0,0,	0,0,	320,0,	
320,0,	320,0,	0,0,	321,0,	
0,0,	321,0,	321,0,	321,0,	
0,0,	321,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	322,0,	322,0,	322,0,	
322,0,	0,0,	0,0,	0,0,	
0,0,	322,0,	322,0,	0,0,	
0,0,	322,0,	322,0,	322,0,	
322,0,	0,0,	0,0,	0,0,	
321,0,	321,0,	321,0,	0,0,	
0,0,	0,0,	0,0,	322,0,	
0,0,	322,0,	322,0,	322,0,	
0,0,	322,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
321,356,	323,0,	323,0,	323,0,	
0,0,	0,0,	0,0,	0,0,	
321,0,	321,0,	321,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
322,0,	322,0,	322,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	323,0,	323,0,	323,0,	
323,0,	0,0,	322,357,	0,0,	
0,0,	323,0,	323,0,	0,0,	
0,0,	323,0,	323,0,	323,0,	
323,0,	0,0,	0,0,	324,0,	
324,0,	324,0,	0,0,	0,0,	
322,0,	322,0,	322,0,	323,0,	
0,0,	323,0,	323,0,	323,0,	
0,0,	323,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	324,0,	
324,0,	324,0,	324,0,	0,0,	
0,0,	0,0,	0,0,	324,0,	
324,0,	0,0,	0,0,	324,0,	
324,0,	324,0,	324,0,	0,0,	
323,0,	323,0,	323,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	324,0,	323,358,	324,0,	
324,0,	324,0,	0,0,	324,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
323,0,	323,0,	323,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	324,0,	324,0,	
324,0,	0,0,	325,0,	325,0,	
325,0,	0,0,	0,0,	0,0,	
0,0,	324,359,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	324,360,	
0,0,	0,0,	325,0,	325,0,	
325,0,	325,0,	324,0,	324,0,	
324,0,	325,0,	325,0,	325,0,	
0,0,	0,0,	325,0,	325,0,	
325,0,	325,0,	0,0,	0,0,	
327,0,	327,0,	327,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
325,0,	0,0,	325,0,	325,0,	
325,0,	0,0,	325,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
327,0,	327,0,	327,0,	327,0,	
0,0,	0,0,	0,0,	327,0,	
327,0,	327,0,	0,0,	0,0,	
327,0,	327,0,	327,0,	327,0,	
0,0,	325,0,	325,0,	325,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	327,0,	325,361,	
327,0,	327,0,	327,0,	0,0,	
327,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
328,0,	328,0,	328,0,	0,0,	
0,0,	325,0,	325,0,	325,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	327,0,	
327,0,	327,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	327,362,	
328,0,	328,0,	328,0,	328,0,	
0,0,	0,0,	0,0,	328,0,	
328,0,	328,0,	0,0,	0,0,	
328,0,	328,0,	328,0,	328,0,	
329,0,	329,0,	329,0,	0,0,	
0,0,	0,0,	0,0,	327,0,	
327,0,	327,0,	328,0,	0,0,	
328,0,	328,0,	328,0,	0,0,	
328,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
329,0,	329,0,	329,0,	329,0,	
0,0,	0,0,	0,0,	329,0,	
329,0,	329,0,	0,0,	0,0,	
329,0,	329,0,	329,0,	329,0,	
0,0,	0,0,	0,0,	328,0,	
328,0,	328,0,	0,0,	0,0,	
0,0,	0,0,	329,0,	0,0,	
329,0,	329,0,	329,0,	0,0,	
329,0,	328,363,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	330,0,	330,0,	
330,0,	0,0,	0,0,	328,0,	
328,0,	328,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	329,0,	
329,0,	329,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	329,364,	330,0,	330,0,	
330,0,	330,0,	0,0,	0,0,	
0,0,	330,0,	330,0,	330,0,	
0,0,	0,0,	330,0,	330,0,	
330,0,	330,0,	331,0,	331,0,	
331,0,	0,0,	0,0,	329,0,	
329,0,	329,0,	0,0,	0,0,	
330,0,	0,0,	330,0,	330,0,	
330,0,	0,0,	330,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	331,0,	331,0,	
331,0,	331,0,	0,0,	0,0,	
0,0,	331,0,	331,0,	331,0,	
0,0,	0,0,	331,0,	331,0,	
331,0,	331,0,	0,0,	0,0,	
0,0,	330,0,	330,0,	330,0,	
0,0,	0,0,	0,0,	0,0,	
331,0,	0,0,	331,0,	331,0,	
331,0,	0,0,	331,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
330,365,	0,0,	0,0,	0,0,	
332,0,	332,0,	332,0,	0,0,	
0,0,	330,0,	330,0,	330,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	331,0,	331,0,	331,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	331,366,	
332,0,	332,0,	332,0,	332,0,	
0,0,	0,0,	0,0,	332,0,	
332,0,	332,0,	0,0,	0,0,	
332,0,	332,0,	332,0,	332,0,	
333,0,	333,0,	333,0,	0,0,	
0,0,	331,0,	331,0,	331,0,	
0,0,	0,0,	332,0,	0,0,	
332,0,	332,0,	332,0,	0,0,	
332,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
333,0,	333,0,	333,0,	333,0,	
0,0,	0,0,	0,0,	333,0,	
333,0,	333,0,	0,0,	0,0,	
333,0,	333,0,	333,0,	333,0,	
0,0,	0,0,	0,0,	332,0,	
332,0,	332,0,	0,0,	0,0,	
0,0,	0,0,	333,0,	0,0,	
333,0,	333,0,	333,0,	0,0,	
333,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
334,0,	334,0,	334,0,	0,0,	
0,0,	0,0,	0,0,	332,0,	
332,0,	332,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	333,0,	
333,0,	333,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
334,0,	334,0,	334,0,	334,0,	
0,0,	0,0,	0,0,	334,0,	
334,0,	334,0,	0,0,	0,0,	
334,0,	334,0,	334,0,	334,0,	
0,0,	333,367,	335,0,	335,0,	
335,0,	0,0,	0,0,	333,0,	
333,0,	333,0,	334,0,	0,0,	
334,0,	334,0,	334,0,	0,0,	
334,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	335,0,	335,0,	
335,0,	335,0,	0,0,	0,0,	
0,0,	335,0,	335,0,	335,0,	
0,0,	0,0,	335,0,	335,0,	
335,0,	335,0,	0,0,	334,0,	
334,0,	334,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
335,0,	0,0,	335,0,	335,0,	
335,0,	0,0,	335,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	336,0,	336,0,	
336,0,	0,0,	0,0,	334,0,	
334,0,	334,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	335,0,	335,0,	335,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	336,0,	336,0,	
336,0,	336,0,	0,0,	0,0,	
0,0,	336,0,	336,0,	336,0,	
0,0,	0,0,	336,0,	336,0,	
336,0,	336,0,	0,0,	0,0,	
337,0,	337,0,	337,0,	0,0,	
0,0,	335,0,	335,0,	335,0,	
336,0,	0,0,	336,0,	336,0,	
336,0,	0,0,	336,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
337,0,	337,0,	337,0,	337,0,	
0,0,	0,0,	0,0,	337,0,	
337,0,	337,0,	0,0,	0,0,	
337,0,	337,0,	337,0,	337,0,	
0,0,	336,0,	336,0,	336,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	337,0,	336,368,	
337,0,	337,0,	337,0,	0,0,	
337,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
338,0,	338,0,	338,0,	0,0,	
0,0,	336,0,	336,0,	336,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	337,0,	
337,0,	337,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
338,0,	338,0,	338,0,	338,0,	
0,0,	0,0,	0,0,	338,0,	
338,0,	338,0,	0,0,	0,0,	
338,0,	338,0,	338,0,	338,0,	
337,369,	339,0,	339,0,	339,0,	
0,0,	0,0,	0,0,	337,0,	
337,0,	337,0,	338,0,	0,0,	
338,0,	338,0,	338,0,	0,0,	
338,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	339,0,	339,0,	339,0,	
339,0,	0,0,	0,0,	0,0,	
339,0,	339,0,	339,0,	0,0,	
0,0,	339,0,	339,0,	339,0,	
339,0,	0,0,	0,0,	338,0,	
338,0,	338,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	339,0,	
0,0,	339,0,	339,0,	339,0,	
0,0,	339,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
340,0,	340,0,	340,0,	338,0,	
338,0,	338,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
339,0,	339,0,	339,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
340,0,	340,0,	340,0,	340,0,	
0,0,	0,0,	0,0,	340,0,	
340,0,	340,0,	0,0,	339,370,	
340,0,	340,0,	340,0,	340,0,	
345,0,	345,0,	345,0,	0,0,	
339,0,	339,0,	339,0,	0,0,	
0,0,	0,0,	340,0,	0,0,	
340,0,	340,0,	340,0,	0,0,	
340,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
345,0,	345,0,	345,0,	345,0,	
0,0,	0,0,	0,0,	0,0,	
345,0,	345,0,	0,0,	0,0,	
345,0,	345,0,	345,0,	345,0,	
0,0,	0,0,	0,0,	340,0,	
340,0,	340,0,	0,0,	0,0,	
0,0,	0,0,	345,0,	0,0,	
345,0,	345,0,	345,0,	0,0,	
345,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	340,371,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	347,0,	347,0,	
347,0,	0,0,	0,0,	340,0,	
340,0,	340,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	345,0,	
345,0,	345,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	345,376,	347,0,	347,0,	
347,0,	347,0,	0,0,	0,0,	
0,0,	0,0,	347,0,	347,0,	
0,0,	0,0,	347,0,	347,0,	
347,0,	347,0,	348,0,	348,0,	
348,0,	0,0,	0,0,	345,0,	
345,0,	345,0,	0,0,	0,0,	
347,0,	0,0,	347,0,	347,0,	
347,0,	0,0,	347,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	348,0,	348,0,	
348,0,	348,0,	0,0,	0,0,	
0,0,	0,0,	348,0,	348,0,	
0,0,	0,0,	348,0,	348,0,	
348,0,	348,0,	0,0,	0,0,	
0,0,	347,0,	347,0,	347,0,	
0,0,	0,0,	0,0,	0,0,	
348,0,	347,377,	348,0,	348,0,	
348,0,	0,0,	348,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	349,0,	349,0,	
349,0,	0,0,	0,0,	0,0,	
0,0,	347,0,	347,0,	347,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	348,0,	348,0,	348,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	349,0,	349,0,	
349,0,	349,0,	0,0,	348,378,	
0,0,	0,0,	349,0,	349,0,	
0,0,	0,0,	349,0,	349,0,	
349,0,	349,0,	0,0,	0,0,	
350,0,	350,0,	350,0,	0,0,	
0,0,	348,0,	348,0,	348,0,	
349,0,	0,0,	349,0,	349,0,	
349,0,	0,0,	349,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
350,0,	350,0,	350,0,	350,0,	
0,0,	0,0,	0,0,	0,0,	
350,0,	350,0,	0,0,	0,0,	
350,0,	350,0,	350,0,	350,0,	
0,0,	349,0,	349,0,	349,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	350,0,	349,379,	
350,0,	350,0,	350,0,	0,0,	
350,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	349,0,	349,0,	349,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	350,0,	
350,0,	350,0,	351,0,	351,0,	
351,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	350,380,	0,0,	
0,0,	0,0,	351,0,	351,0,	
351,0,	351,0,	0,0,	350,0,	
350,0,	350,0,	351,0,	351,0,	
0,0,	0,0,	351,0,	351,0,	
351,0,	351,0,	0,0,	0,0,	
352,0,	352,0,	352,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
351,0,	0,0,	351,0,	351,0,	
351,0,	0,0,	351,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
352,0,	352,0,	352,0,	352,0,	
0,0,	0,0,	0,0,	0,0,	
352,0,	352,0,	0,0,	0,0,	
352,0,	352,0,	352,0,	352,0,	
0,0,	351,0,	351,0,	351,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	352,0,	351,381,	
352,0,	352,0,	352,0,	0,0,	
352,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
353,0,	353,0,	353,0,	0,0,	
0,0,	351,0,	351,0,	351,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	352,0,	
352,0,	352,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
353,0,	353,0,	353,0,	353,0,	
0,0,	0,0,	0,0,	0,0,	
353,0,	353,0,	0,0,	0,0,	
353,0,	353,0,	353,0,	353,0,	
354,0,	354,0,	354,0,	0,0,	
0,0,	0,0,	0,0,	352,0,	
352,0,	352,0,	353,0,	0,0,	
353,0,	353,0,	353,0,	0,0,	
353,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
354,0,	354,0,	354,0,	354,0,	
0,0,	0,0,	0,0,	0,0,	
354,0,	354,0,	0,0,	0,0,	
354,0,	354,0,	354,0,	354,0,	
0,0,	0,0,	0,0,	353,0,	
353,0,	353,0,	0,0,	0,0,	
0,0,	0,0,	354,0,	0,0,	
354,0,	354,0,	354,0,	0,0,	
354,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	353,382,	355,0,	355,0,	
355,0,	0,0,	0,0,	353,0,	
353,0,	353,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	354,0,	
354,0,	354,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	355,0,	355,0,	
355,0,	355,0,	0,0,	0,0,	
0,0,	0,0,	355,0,	355,0,	
0,0,	0,0,	355,0,	355,0,	
355,0,	355,0,	356,0,	356,0,	
356,0,	0,0,	0,0,	354,0,	
354,0,	354,0,	0,0,	0,0,	
355,0,	0,0,	355,0,	355,0,	
355,0,	0,0,	355,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	356,0,	356,0,	
356,0,	356,0,	0,0,	0,0,	
0,0,	0,0,	356,0,	356,0,	
0,0,	0,0,	356,0,	356,0,	
356,0,	356,0,	0,0,	0,0,	
0,0,	355,0,	355,0,	355,0,	
0,0,	0,0,	0,0,	0,0,	
356,0,	0,0,	356,0,	356,0,	
356,0,	0,0,	356,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
357,0,	357,0,	357,0,	0,0,	
0,0,	355,0,	355,0,	355,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	356,0,	356,0,	356,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	356,383,	
357,0,	357,0,	357,0,	357,0,	
0,0,	0,0,	0,0,	0,0,	
357,0,	357,0,	0,0,	0,0,	
357,0,	357,0,	357,0,	357,0,	
358,0,	358,0,	358,0,	0,0,	
0,0,	356,0,	356,0,	356,0,	
0,0,	0,0,	357,0,	0,0,	
357,0,	357,0,	357,0,	0,0,	
357,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
358,0,	358,0,	358,0,	358,0,	
0,0,	0,0,	0,0,	0,0,	
358,0,	358,0,	0,0,	0,0,	
358,0,	358,0,	358,0,	358,0,	
0,0,	0,0,	0,0,	357,0,	
357,0,	357,0,	0,0,	0,0,	
0,0,	0,0,	358,0,	0,0,	
358,0,	358,0,	358,0,	0,0,	
358,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
357,384,	359,0,	359,0,	359,0,	
0,0,	0,0,	0,0,	357,0,	
357,0,	357,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	358,0,	
358,0,	358,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	359,0,	359,0,	359,0,	
359,0,	0,0,	0,0,	0,0,	
0,0,	359,0,	359,0,	0,0,	
0,0,	359,0,	359,0,	359,0,	
359,0,	360,0,	360,0,	360,0,	
0,0,	0,0,	0,0,	358,0,	
358,0,	358,0,	0,0,	359,0,	
0,0,	359,0,	359,0,	359,0,	
0,0,	359,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	360,0,	360,0,	360,0,	
360,0,	0,0,	0,0,	0,0,	
0,0,	360,0,	360,0,	0,0,	
0,0,	360,0,	360,0,	360,0,	
360,0,	0,0,	0,0,	0,0,	
359,0,	359,0,	359,0,	0,0,	
0,0,	0,0,	0,0,	360,0,	
0,0,	360,0,	360,0,	360,0,	
0,0,	360,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	359,385,	
0,0,	361,0,	361,0,	361,0,	
0,0,	0,0,	0,0,	0,0,	
359,0,	359,0,	359,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
360,0,	360,0,	360,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	361,0,	361,0,	361,0,	
361,0,	0,0,	0,0,	0,0,	
361,0,	361,0,	361,0,	0,0,	
360,386,	361,0,	361,0,	361,0,	
361,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
360,0,	360,0,	360,0,	361,0,	
0,0,	361,0,	361,0,	361,0,	
0,0,	361,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
361,0,	361,0,	361,0,	0,0,	
361,387,	0,0,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,9,	361,9,	361,9,	361,9,	
361,0,	361,0,	361,0,	362,0,	
362,0,	362,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	362,0,	
362,0,	362,0,	362,0,	0,0,	
0,0,	0,0,	362,0,	362,0,	
362,0,	0,0,	0,0,	362,0,	
362,0,	362,0,	362,0,	363,0,	
363,0,	363,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	362,0,	0,0,	362,0,	
362,0,	362,0,	0,0,	362,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	363,0,	
363,0,	363,0,	363,0,	0,0,	
0,0,	0,0,	363,0,	363,0,	
363,0,	0,0,	0,0,	363,0,	
363,0,	363,0,	363,0,	0,0,	
0,0,	0,0,	362,0,	362,0,	
362,0,	0,0,	0,0,	0,0,	
0,0,	363,0,	0,0,	363,0,	
363,0,	363,0,	0,0,	363,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	362,388,	
364,0,	364,0,	364,0,	0,0,	
0,0,	0,0,	362,0,	362,0,	
362,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	363,0,	363,0,	
363,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
364,0,	364,0,	364,0,	364,0,	
0,0,	0,0,	0,0,	364,0,	
364,0,	364,0,	363,389,	0,0,	
364,0,	364,0,	364,0,	364,0,	
365,0,	365,0,	365,0,	0,0,	
0,0,	0,0,	363,0,	363,0,	
363,0,	0,0,	364,0,	0,0,	
364,0,	364,0,	364,0,	0,0,	
364,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
365,0,	365,0,	365,0,	365,0,	
0,0,	0,0,	0,0,	365,0,	
365,0,	365,0,	0,0,	0,0,	
365,0,	365,0,	365,0,	365,0,	
0,0,	0,0,	0,0,	364,0,	
364,0,	364,0,	0,0,	0,0,	
0,0,	0,0,	365,0,	0,0,	
365,0,	365,0,	365,0,	0,0,	
365,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	364,390,	0,0,	
0,0,	0,0,	0,0,	0,0,	
366,0,	366,0,	366,0,	0,0,	
0,0,	0,0,	0,0,	364,0,	
364,0,	364,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	365,0,	
365,0,	365,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
366,0,	366,0,	366,0,	366,0,	
0,0,	0,0,	0,0,	366,0,	
366,0,	366,0,	0,0,	0,0,	
366,0,	366,0,	366,0,	366,0,	
367,0,	367,0,	367,0,	0,0,	
0,0,	0,0,	0,0,	365,0,	
365,0,	365,0,	366,0,	0,0,	
366,0,	366,0,	366,0,	0,0,	
366,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
367,0,	367,0,	367,0,	367,0,	
0,0,	0,0,	0,0,	367,0,	
367,0,	367,0,	0,0,	0,0,	
367,0,	367,0,	367,0,	367,0,	
0,0,	0,0,	0,0,	366,0,	
366,0,	366,0,	0,0,	0,0,	
0,0,	0,0,	367,0,	0,0,	
367,0,	367,0,	367,0,	0,0,	
367,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	366,391,	0,0,	
0,0,	0,0,	0,0,	0,0,	
368,0,	368,0,	368,0,	0,0,	
0,0,	0,0,	0,0,	366,0,	
366,0,	366,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	367,0,	
367,0,	367,0,	0,0,	0,0,	
0,0,	367,392,	0,0,	0,0,	
368,0,	368,0,	368,0,	368,0,	
0,0,	0,0,	0,0,	368,0,	
368,0,	368,0,	0,0,	0,0,	
368,0,	368,0,	368,0,	368,0,	
369,0,	369,0,	369,0,	0,0,	
0,0,	0,0,	0,0,	367,0,	
367,0,	367,0,	368,0,	0,0,	
368,0,	368,0,	368,0,	0,0,	
368,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
369,0,	369,0,	369,0,	369,0,	
0,0,	0,0,	0,0,	369,0,	
369,0,	369,0,	0,0,	0,0,	
369,0,	369,0,	369,0,	369,0,	
0,0,	0,0,	0,0,	368,0,	
368,0,	368,0,	0,0,	0,0,	
0,0,	0,0,	369,0,	0,0,	
369,0,	369,0,	369,0,	0,0,	
369,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
370,0,	370,0,	370,0,	0,0,	
0,0,	0,0,	0,0,	368,0,	
368,0,	368,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	369,0,	
369,0,	369,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
370,0,	370,0,	370,0,	370,0,	
0,0,	0,0,	0,0,	370,0,	
370,0,	370,0,	0,0,	0,0,	
370,0,	370,0,	370,0,	370,0,	
371,0,	371,0,	371,0,	0,0,	
0,0,	369,393,	0,0,	369,0,	
369,0,	369,0,	370,0,	0,0,	
370,0,	370,0,	370,0,	0,0,	
370,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
371,0,	371,0,	371,0,	371,0,	
0,0,	0,0,	0,0,	371,0,	
371,0,	371,0,	0,0,	0,0,	
371,0,	371,0,	371,0,	371,0,	
0,0,	0,0,	0,0,	370,0,	
370,0,	370,0,	0,0,	0,0,	
0,0,	0,0,	371,0,	0,0,	
371,0,	371,0,	371,0,	0,0,	
371,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	370,394,	
0,0,	0,0,	0,0,	0,0,	
376,0,	376,0,	376,0,	0,0,	
0,0,	0,0,	0,0,	370,0,	
370,0,	370,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	371,0,	
371,0,	371,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
376,0,	376,0,	376,0,	376,0,	
0,0,	0,0,	0,0,	0,0,	
376,0,	376,0,	0,0,	0,0,	
376,0,	376,0,	376,0,	376,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	371,0,	
371,0,	371,0,	376,0,	0,0,	
376,0,	376,0,	376,0,	0,0,	
376,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	376,0,	
376,0,	376,0,	0,0,	376,398,	
0,0,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,67,	
376,67,	376,67,	376,67,	376,0,	
376,0,	376,0,	377,0,	377,0,	
377,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	377,0,	377,0,	
377,0,	377,0,	0,0,	0,0,	
0,0,	0,0,	377,0,	377,0,	
0,0,	0,0,	377,0,	377,0,	
377,0,	377,0,	378,0,	378,0,	
378,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
377,0,	0,0,	377,0,	377,0,	
377,0,	0,0,	377,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	378,0,	378,0,	
378,0,	378,0,	0,0,	0,0,	
0,0,	0,0,	378,0,	378,0,	
0,0,	0,0,	378,0,	378,0,	
378,0,	378,0,	0,0,	0,0,	
0,0,	377,0,	377,0,	377,0,	
0,0,	0,0,	0,0,	0,0,	
378,0,	0,0,	378,0,	378,0,	
378,0,	0,0,	378,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	377,399,	379,0,	
379,0,	379,0,	0,0,	0,0,	
0,0,	377,0,	377,0,	377,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	378,0,	378,0,	378,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	379,0,	
379,0,	379,0,	379,0,	0,0,	
0,0,	0,0,	0,0,	379,0,	
379,0,	378,400,	0,0,	379,0,	
379,0,	379,0,	379,0,	380,0,	
380,0,	380,0,	0,0,	0,0,	
0,0,	378,0,	378,0,	378,0,	
0,0,	379,0,	0,0,	379,0,	
379,0,	379,0,	0,0,	379,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	380,0,	
380,0,	380,0,	380,0,	0,0,	
0,0,	0,0,	0,0,	380,0,	
380,0,	0,0,	0,0,	380,0,	
380,0,	380,0,	380,0,	0,0,	
0,0,	0,0,	379,0,	379,0,	
379,0,	0,0,	0,0,	0,0,	
0,0,	380,0,	0,0,	380,0,	
380,0,	380,0,	0,0,	380,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	379,401,	0,0,	0,0,	
0,0,	0,0,	0,0,	381,0,	
381,0,	381,0,	0,0,	0,0,	
0,0,	0,0,	379,0,	379,0,	
379,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	380,0,	380,0,	
380,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	381,0,	
381,0,	381,0,	381,0,	0,0,	
0,0,	0,0,	0,0,	381,0,	
381,0,	0,0,	0,0,	381,0,	
381,0,	381,0,	381,0,	382,0,	
382,0,	382,0,	0,0,	0,0,	
0,0,	0,0,	380,0,	380,0,	
380,0,	381,0,	0,0,	381,0,	
381,0,	381,0,	0,0,	381,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	382,0,	
382,0,	382,0,	382,0,	0,0,	
0,0,	0,0,	0,0,	382,0,	
382,0,	0,0,	0,0,	382,0,	
382,0,	382,0,	382,0,	0,0,	
0,0,	0,0,	381,0,	381,0,	
381,0,	0,0,	0,0,	0,0,	
0,0,	382,0,	0,0,	382,0,	
382,0,	382,0,	0,0,	382,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	381,402,	0,0,	0,0,	
0,0,	0,0,	0,0,	383,0,	
383,0,	383,0,	0,0,	0,0,	
0,0,	0,0,	381,0,	381,0,	
381,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	382,0,	382,0,	
382,0,	0,0,	0,0,	0,0,	
382,403,	0,0,	0,0,	383,0,	
383,0,	383,0,	383,0,	0,0,	
0,0,	0,0,	0,0,	383,0,	
383,0,	0,0,	0,0,	383,0,	
383,0,	383,0,	383,0,	384,0,	
384,0,	384,0,	0,0,	0,0,	
0,0,	0,0,	382,0,	382,0,	
382,0,	383,0,	0,0,	383,0,	
383,0,	383,0,	0,0,	383,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	384,0,	
384,0,	384,0,	384,0,	0,0,	
0,0,	0,0,	0,0,	384,0,	
384,0,	0,0,	0,0,	384,0,	
384,0,	384,0,	384,0,	0,0,	
0,0,	0,0,	383,0,	383,0,	
383,0,	0,0,	0,0,	0,0,	
0,0,	384,0,	0,0,	384,0,	
384,0,	384,0,	0,0,	384,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	385,0,	
385,0,	385,0,	0,0,	0,0,	
0,0,	0,0,	383,0,	383,0,	
383,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	384,0,	384,0,	
384,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	385,0,	
385,0,	385,0,	385,0,	0,0,	
0,0,	0,0,	0,0,	385,0,	
385,0,	0,0,	0,0,	385,0,	
385,0,	385,0,	385,0,	386,0,	
386,0,	386,0,	0,0,	0,0,	
384,404,	0,0,	384,0,	384,0,	
384,0,	385,0,	0,0,	385,0,	
385,0,	385,0,	0,0,	385,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	386,0,	
386,0,	386,0,	386,0,	0,0,	
0,0,	0,0,	0,0,	386,0,	
386,0,	0,0,	0,0,	386,0,	
386,0,	386,0,	386,0,	0,0,	
0,0,	0,0,	385,0,	385,0,	
385,0,	0,0,	0,0,	0,0,	
0,0,	386,0,	0,0,	386,0,	
386,0,	386,0,	0,0,	386,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	385,405,	0,0,	
0,0,	0,0,	0,0,	387,0,	
387,0,	387,0,	0,0,	0,0,	
0,0,	0,0,	385,0,	385,0,	
385,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	386,0,	386,0,	
386,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	387,0,	
387,0,	387,0,	387,0,	0,0,	
0,0,	0,0,	387,0,	387,0,	
387,0,	0,0,	0,0,	387,0,	
387,0,	387,0,	387,0,	388,0,	
388,0,	388,0,	0,0,	0,0,	
0,0,	0,0,	386,0,	386,0,	
386,0,	387,0,	0,0,	387,0,	
387,0,	387,0,	0,0,	387,0,	
0,0,	0,0,	387,406,	0,0,	
0,0,	0,0,	0,0,	388,0,	
388,0,	388,0,	388,0,	0,0,	
0,0,	0,0,	388,0,	388,0,	
388,0,	387,407,	0,0,	388,0,	
388,0,	388,0,	388,0,	0,0,	
0,0,	0,0,	387,0,	387,0,	
387,0,	0,0,	0,0,	0,0,	
387,408,	388,0,	0,0,	388,0,	
388,0,	388,0,	387,409,	388,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	389,0,	
389,0,	389,0,	0,0,	0,0,	
0,0,	0,0,	387,0,	387,0,	
387,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	388,0,	388,0,	
388,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	389,0,	
389,0,	389,0,	389,0,	0,0,	
0,0,	0,0,	389,0,	389,0,	
389,0,	0,0,	0,0,	389,0,	
389,0,	389,0,	389,0,	390,0,	
390,0,	390,0,	0,0,	0,0,	
0,0,	0,0,	388,0,	388,0,	
388,0,	389,0,	0,0,	389,0,	
389,0,	389,0,	0,0,	389,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	390,0,	
390,0,	390,0,	390,0,	0,0,	
0,0,	0,0,	390,0,	390,0,	
390,0,	0,0,	0,0,	390,0,	
390,0,	390,0,	390,0,	0,0,	
0,0,	0,0,	389,0,	389,0,	
389,0,	0,0,	0,0,	0,0,	
0,0,	390,0,	0,0,	390,0,	
390,0,	390,0,	0,0,	390,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	389,410,	0,0,	0,0,	
0,0,	0,0,	0,0,	391,0,	
391,0,	391,0,	0,0,	0,0,	
0,0,	0,0,	389,0,	389,0,	
389,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	390,0,	390,0,	
390,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	391,0,	
391,0,	391,0,	391,0,	0,0,	
0,0,	0,0,	391,0,	391,0,	
391,0,	0,0,	0,0,	391,0,	
391,0,	391,0,	391,0,	390,411,	
392,0,	392,0,	392,0,	0,0,	
0,0,	0,0,	390,0,	390,0,	
390,0,	391,0,	0,0,	391,0,	
391,0,	391,0,	0,0,	391,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
392,0,	392,0,	392,0,	392,0,	
0,0,	0,0,	0,0,	392,0,	
392,0,	392,0,	0,0,	0,0,	
392,0,	392,0,	392,0,	392,0,	
0,0,	0,0,	391,0,	391,0,	
391,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	392,0,	0,0,	
392,0,	392,0,	392,0,	0,0,	
392,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	391,412,	
0,0,	0,0,	393,0,	393,0,	
393,0,	0,0,	391,0,	391,0,	
391,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	392,0,	
392,0,	392,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	393,0,	393,0,	
393,0,	393,0,	0,0,	0,0,	
392,413,	393,0,	393,0,	393,0,	
0,0,	0,0,	393,0,	393,0,	
393,0,	393,0,	394,0,	394,0,	
394,0,	0,0,	0,0,	392,0,	
392,0,	392,0,	0,0,	0,0,	
393,0,	0,0,	393,0,	393,0,	
393,0,	0,0,	393,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	394,0,	394,0,	
394,0,	394,0,	0,0,	0,0,	
0,0,	394,0,	394,0,	394,0,	
0,0,	0,0,	394,0,	394,0,	
394,0,	394,0,	0,0,	0,0,	
0,0,	393,0,	393,0,	393,0,	
0,0,	0,0,	0,0,	0,0,	
394,0,	0,0,	394,0,	394,0,	
394,0,	0,0,	394,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
398,0,	398,0,	398,0,	0,0,	
0,0,	393,0,	393,0,	393,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	394,0,	394,0,	394,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
398,0,	398,0,	398,0,	398,0,	
0,0,	0,0,	0,0,	394,414,	
398,0,	398,0,	0,0,	0,0,	
398,0,	398,0,	398,0,	398,0,	
399,0,	399,0,	399,0,	0,0,	
0,0,	394,0,	394,0,	394,0,	
0,0,	0,0,	398,0,	0,0,	
398,0,	398,0,	398,0,	0,0,	
398,0,	0,0,	0,0,	398,421,	
0,0,	0,0,	0,0,	0,0,	
399,0,	399,0,	399,0,	399,0,	
0,0,	0,0,	0,0,	0,0,	
399,0,	399,0,	398,422,	0,0,	
399,0,	399,0,	399,0,	399,0,	
0,0,	0,0,	0,0,	398,0,	
398,0,	398,0,	0,0,	0,0,	
0,0,	398,423,	399,0,	0,0,	
399,0,	399,0,	399,0,	398,424,	
399,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
400,0,	400,0,	400,0,	0,0,	
0,0,	0,0,	0,0,	398,0,	
398,0,	398,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	399,0,	
399,0,	399,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
400,0,	400,0,	400,0,	400,0,	
0,0,	0,0,	0,0,	0,0,	
400,0,	400,0,	0,0,	0,0,	
400,0,	400,0,	400,0,	400,0,	
401,0,	401,0,	401,0,	0,0,	
0,0,	0,0,	0,0,	399,0,	
399,0,	399,0,	400,0,	0,0,	
400,0,	400,0,	400,0,	0,0,	
400,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
401,0,	401,0,	401,0,	401,0,	
0,0,	0,0,	0,0,	0,0,	
401,0,	401,0,	0,0,	0,0,	
401,0,	401,0,	401,0,	401,0,	
0,0,	0,0,	0,0,	400,0,	
400,0,	400,0,	0,0,	0,0,	
0,0,	0,0,	401,0,	0,0,	
401,0,	401,0,	401,0,	0,0,	
401,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	400,425,	0,0,	
0,0,	0,0,	0,0,	0,0,	
402,0,	402,0,	402,0,	0,0,	
0,0,	0,0,	0,0,	400,0,	
400,0,	400,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	401,0,	
401,0,	401,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
402,0,	402,0,	402,0,	402,0,	
0,0,	0,0,	0,0,	0,0,	
402,0,	402,0,	0,0,	0,0,	
402,0,	402,0,	402,0,	402,0,	
401,426,	403,0,	403,0,	403,0,	
0,0,	0,0,	0,0,	401,0,	
401,0,	401,0,	402,0,	0,0,	
402,0,	402,0,	402,0,	0,0,	
402,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	403,0,	403,0,	403,0,	
403,0,	0,0,	0,0,	0,0,	
0,0,	403,0,	403,0,	0,0,	
0,0,	403,0,	403,0,	403,0,	
403,0,	0,0,	0,0,	402,0,	
402,0,	402,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	403,0,	
0,0,	403,0,	403,0,	403,0,	
0,0,	403,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
402,427,	0,0,	404,0,	404,0,	
404,0,	0,0,	0,0,	402,0,	
402,0,	402,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
403,0,	403,0,	403,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	404,0,	404,0,	
404,0,	404,0,	0,0,	0,0,	
0,0,	403,428,	404,0,	404,0,	
0,0,	0,0,	404,0,	404,0,	
404,0,	404,0,	405,0,	405,0,	
405,0,	0,0,	0,0,	0,0,	
403,0,	403,0,	403,0,	0,0,	
404,0,	0,0,	404,0,	404,0,	
404,0,	0,0,	404,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	405,0,	405,0,	
405,0,	405,0,	0,0,	0,0,	
0,0,	0,0,	405,0,	405,0,	
0,0,	0,0,	405,0,	405,0,	
405,0,	405,0,	0,0,	0,0,	
0,0,	404,0,	404,0,	404,0,	
0,0,	0,0,	0,0,	0,0,	
405,0,	0,0,	405,0,	405,0,	
405,0,	0,0,	405,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	406,0,	406,0,	406,0,	
0,0,	404,0,	404,0,	404,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	405,0,	405,0,	405,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	406,0,	406,0,	406,0,	
406,0,	0,0,	0,0,	405,429,	
406,0,	406,0,	406,0,	0,0,	
0,0,	406,0,	406,0,	406,0,	
406,0,	407,0,	407,0,	407,0,	
0,0,	405,0,	405,0,	405,0,	
0,0,	0,0,	0,0,	406,0,	
0,0,	406,0,	406,0,	406,0,	
0,0,	406,0,	0,0,	406,430,	
0,0,	0,0,	0,0,	0,0,	
0,0,	407,0,	407,0,	407,0,	
407,0,	0,0,	0,0,	0,0,	
407,0,	407,0,	407,0,	0,0,	
0,0,	407,0,	407,0,	407,0,	
407,0,	0,0,	0,0,	0,0,	
406,0,	406,0,	406,0,	0,0,	
0,0,	0,0,	0,0,	407,0,	
0,0,	407,0,	407,0,	407,0,	
0,0,	407,0,	0,0,	407,431,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	408,0,	408,0,	408,0,	
0,0,	0,0,	0,0,	0,0,	
406,0,	406,0,	406,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
407,0,	407,0,	407,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	408,0,	408,0,	408,0,	
408,0,	0,0,	0,0,	0,0,	
408,0,	408,0,	408,0,	0,0,	
0,0,	408,0,	408,0,	408,0,	
408,0,	0,0,	409,0,	409,0,	
409,0,	0,0,	0,0,	0,0,	
407,0,	407,0,	407,0,	408,0,	
0,0,	408,0,	408,0,	408,0,	
0,0,	408,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	409,0,	409,0,	
409,0,	409,0,	0,0,	0,0,	
0,0,	409,0,	409,0,	409,0,	
0,0,	0,0,	409,0,	409,0,	
409,0,	409,0,	0,0,	0,0,	
408,0,	408,0,	408,0,	0,0,	
0,0,	0,0,	0,0,	408,432,	
409,0,	0,0,	409,0,	409,0,	
409,0,	0,0,	409,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	410,0,	410,0,	
410,0,	0,0,	0,0,	0,0,	
408,0,	408,0,	408,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	409,0,	409,0,	409,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	410,0,	410,0,	
410,0,	410,0,	0,0,	0,0,	
0,0,	410,0,	410,0,	410,0,	
0,0,	409,433,	410,0,	410,0,	
410,0,	410,0,	411,0,	411,0,	
411,0,	0,0,	0,0,	0,0,	
0,0,	409,0,	409,0,	409,0,	
410,0,	0,0,	410,0,	410,0,	
410,0,	0,0,	410,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	411,0,	411,0,	
411,0,	411,0,	0,0,	0,0,	
0,0,	411,0,	411,0,	411,0,	
0,0,	0,0,	411,0,	411,0,	
411,0,	411,0,	0,0,	0,0,	
0,0,	410,0,	410,0,	410,0,	
0,0,	0,0,	0,0,	0,0,	
411,0,	0,0,	411,0,	411,0,	
411,0,	0,0,	411,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	412,0,	412,0,	
412,0,	0,0,	0,0,	0,0,	
0,0,	410,0,	410,0,	410,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	411,0,	411,0,	411,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	412,0,	412,0,	
412,0,	412,0,	0,0,	0,0,	
0,0,	412,0,	412,0,	412,0,	
0,0,	0,0,	412,0,	412,0,	
412,0,	412,0,	413,0,	413,0,	
413,0,	0,0,	0,0,	0,0,	
0,0,	411,0,	411,0,	411,0,	
412,0,	0,0,	412,0,	412,0,	
412,0,	0,0,	412,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	413,0,	413,0,	
413,0,	413,0,	0,0,	0,0,	
0,0,	413,0,	413,0,	413,0,	
0,0,	0,0,	413,0,	413,0,	
413,0,	413,0,	0,0,	0,0,	
0,0,	412,0,	412,0,	412,0,	
0,0,	0,0,	0,0,	0,0,	
413,0,	0,0,	413,0,	413,0,	
413,0,	0,0,	413,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	414,0,	414,0,	
414,0,	0,0,	0,0,	0,0,	
0,0,	412,0,	412,0,	412,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	413,0,	413,0,	413,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	414,0,	414,0,	
414,0,	414,0,	0,0,	0,0,	
0,0,	414,0,	414,0,	414,0,	
0,0,	0,0,	414,0,	414,0,	
414,0,	414,0,	421,0,	421,0,	
421,0,	0,0,	0,0,	0,0,	
0,0,	413,0,	413,0,	413,0,	
414,0,	0,0,	414,0,	414,0,	
414,0,	0,0,	414,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	421,0,	421,0,	
421,0,	421,0,	0,0,	0,0,	
0,0,	0,0,	421,0,	421,0,	
0,0,	0,0,	421,0,	421,0,	
421,0,	421,0,	0,0,	0,0,	
0,0,	414,0,	414,0,	414,0,	
0,0,	0,0,	0,0,	0,0,	
421,0,	0,0,	421,0,	421,0,	
421,0,	0,0,	421,0,	0,0,	
421,438,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	422,0,	422,0,	
422,0,	0,0,	0,0,	0,0,	
0,0,	414,0,	414,0,	414,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	421,0,	421,0,	421,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	422,0,	422,0,	
422,0,	422,0,	0,0,	0,0,	
0,0,	0,0,	422,0,	422,0,	
0,0,	0,0,	422,0,	422,0,	
422,0,	422,0,	423,0,	423,0,	
423,0,	0,0,	0,0,	0,0,	
0,0,	421,0,	421,0,	421,0,	
422,0,	0,0,	422,0,	422,0,	
422,0,	0,0,	422,0,	0,0,	
422,439,	0,0,	0,0,	0,0,	
0,0,	0,0,	423,0,	423,0,	
423,0,	423,0,	0,0,	0,0,	
0,0,	0,0,	423,0,	423,0,	
0,0,	0,0,	423,0,	423,0,	
423,0,	423,0,	0,0,	0,0,	
0,0,	422,0,	422,0,	422,0,	
0,0,	0,0,	0,0,	0,0,	
423,0,	0,0,	423,0,	423,0,	
423,0,	0,0,	423,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	424,0,	424,0,	
424,0,	0,0,	0,0,	0,0,	
0,0,	422,0,	422,0,	422,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	423,0,	423,0,	423,0,	
0,0,	0,0,	0,0,	0,0,	
423,440,	0,0,	424,0,	424,0,	
424,0,	424,0,	0,0,	0,0,	
0,0,	0,0,	424,0,	424,0,	
0,0,	0,0,	424,0,	424,0,	
424,0,	424,0,	425,0,	425,0,	
425,0,	0,0,	0,0,	0,0,	
0,0,	423,0,	423,0,	423,0,	
424,0,	0,0,	424,0,	424,0,	
424,0,	0,0,	424,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	425,0,	425,0,	
425,0,	425,0,	0,0,	0,0,	
0,0,	0,0,	425,0,	425,0,	
0,0,	0,0,	425,0,	425,0,	
425,0,	425,0,	0,0,	0,0,	
0,0,	424,0,	424,0,	424,0,	
0,0,	0,0,	0,0,	0,0,	
425,0,	0,0,	425,0,	425,0,	
425,0,	0,0,	425,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	424,441,	0,0,	0,0,	
0,0,	0,0,	426,0,	426,0,	
426,0,	0,0,	0,0,	0,0,	
0,0,	424,0,	424,0,	424,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	425,0,	425,0,	425,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	426,0,	426,0,	
426,0,	426,0,	0,0,	0,0,	
0,0,	0,0,	426,0,	426,0,	
0,0,	0,0,	426,0,	426,0,	
426,0,	426,0,	427,0,	427,0,	
427,0,	0,0,	0,0,	0,0,	
0,0,	425,0,	425,0,	425,0,	
426,0,	0,0,	426,0,	426,0,	
426,0,	0,0,	426,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	427,0,	427,0,	
427,0,	427,0,	0,0,	0,0,	
0,0,	0,0,	427,0,	427,0,	
0,0,	0,0,	427,0,	427,0,	
427,0,	427,0,	0,0,	0,0,	
0,0,	426,0,	426,0,	426,0,	
0,0,	0,0,	0,0,	0,0,	
427,0,	0,0,	427,0,	427,0,	
427,0,	0,0,	427,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	428,0,	428,0,	
428,0,	0,0,	0,0,	0,0,	
0,0,	426,0,	426,0,	426,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	427,0,	427,0,	427,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	428,0,	428,0,	
428,0,	428,0,	0,0,	0,0,	
0,0,	0,0,	428,0,	428,0,	
0,0,	0,0,	428,0,	428,0,	
428,0,	428,0,	429,0,	429,0,	
429,0,	0,0,	0,0,	0,0,	
0,0,	427,0,	427,0,	427,0,	
428,0,	0,0,	428,0,	428,0,	
428,0,	0,0,	428,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	429,0,	429,0,	
429,0,	429,0,	0,0,	0,0,	
0,0,	0,0,	429,0,	429,0,	
0,0,	0,0,	429,0,	429,0,	
429,0,	429,0,	0,0,	0,0,	
0,0,	428,0,	428,0,	428,0,	
0,0,	0,0,	0,0,	0,0,	
429,0,	0,0,	429,0,	429,0,	
429,0,	0,0,	429,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	430,0,	430,0,	
430,0,	0,0,	0,0,	0,0,	
0,0,	428,0,	428,0,	428,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	429,0,	429,0,	429,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	430,0,	430,0,	
430,0,	430,0,	0,0,	0,0,	
0,0,	430,0,	430,0,	430,0,	
0,0,	0,0,	430,0,	430,0,	
430,0,	430,0,	431,0,	431,0,	
431,0,	0,0,	0,0,	0,0,	
0,0,	429,0,	429,0,	429,0,	
430,0,	0,0,	430,0,	430,0,	
430,0,	0,0,	430,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	431,0,	431,0,	
431,0,	431,0,	0,0,	0,0,	
0,0,	431,0,	431,0,	431,0,	
430,442,	0,0,	431,0,	431,0,	
431,0,	431,0,	0,0,	0,0,	
0,0,	430,0,	430,0,	430,0,	
0,0,	0,0,	0,0,	0,0,	
431,0,	0,0,	431,0,	431,0,	
431,0,	0,0,	431,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	432,0,	432,0,	
432,0,	0,0,	0,0,	0,0,	
431,443,	430,0,	430,0,	430,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	431,0,	431,0,	431,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	432,0,	432,0,	
432,0,	432,0,	0,0,	0,0,	
0,0,	432,0,	432,0,	432,0,	
0,0,	0,0,	432,0,	432,0,	
432,0,	432,0,	433,0,	433,0,	
433,0,	0,0,	0,0,	0,0,	
0,0,	431,0,	431,0,	431,0,	
432,0,	0,0,	432,0,	432,0,	
432,0,	0,0,	432,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	433,0,	433,0,	
433,0,	433,0,	0,0,	0,0,	
0,0,	433,0,	433,0,	433,0,	
0,0,	0,0,	433,0,	433,0,	
433,0,	433,0,	0,0,	0,0,	
0,0,	432,0,	432,0,	432,0,	
0,0,	0,0,	0,0,	0,0,	
433,0,	0,0,	433,0,	433,0,	
433,0,	0,0,	433,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	432,444,	438,0,	438,0,	
438,0,	0,0,	0,0,	0,0,	
0,0,	432,0,	432,0,	432,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	433,0,	433,0,	433,0,	
0,0,	0,0,	0,0,	433,445,	
0,0,	0,0,	438,0,	438,0,	
438,0,	438,0,	0,0,	0,0,	
0,0,	0,0,	438,0,	438,0,	
0,0,	0,0,	438,0,	438,0,	
438,0,	438,0,	439,0,	439,0,	
439,0,	0,0,	0,0,	0,0,	
0,0,	433,0,	433,0,	433,0,	
438,0,	0,0,	438,0,	438,0,	
438,0,	0,0,	438,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	439,0,	439,0,	
439,0,	439,0,	0,0,	0,0,	
0,0,	0,0,	439,0,	439,0,	
438,450,	0,0,	439,0,	439,0,	
439,0,	439,0,	0,0,	0,0,	
0,0,	438,0,	438,0,	438,0,	
0,0,	0,0,	0,0,	0,0,	
439,0,	0,0,	439,0,	439,0,	
439,0,	0,0,	439,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	440,0,	440,0,	
440,0,	0,0,	0,0,	0,0,	
439,451,	438,0,	438,0,	438,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	439,0,	439,0,	439,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	440,0,	440,0,	
440,0,	440,0,	0,0,	0,0,	
0,0,	0,0,	440,0,	440,0,	
0,0,	0,0,	440,0,	440,0,	
440,0,	440,0,	441,0,	441,0,	
441,0,	0,0,	0,0,	0,0,	
0,0,	439,0,	439,0,	439,0,	
440,0,	0,0,	440,0,	440,0,	
440,0,	0,0,	440,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	441,0,	441,0,	
441,0,	441,0,	0,0,	0,0,	
0,0,	0,0,	441,0,	441,0,	
0,0,	0,0,	441,0,	441,0,	
441,0,	441,0,	0,0,	0,0,	
0,0,	440,0,	440,0,	440,0,	
0,0,	0,0,	0,0,	0,0,	
441,0,	0,0,	441,0,	441,0,	
441,0,	0,0,	441,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	440,452,	442,0,	442,0,	
442,0,	0,0,	0,0,	0,0,	
0,0,	440,0,	440,0,	440,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	441,0,	441,0,	441,0,	
0,0,	0,0,	0,0,	441,453,	
0,0,	0,0,	442,0,	442,0,	
442,0,	442,0,	0,0,	0,0,	
0,0,	442,0,	442,0,	442,0,	
0,0,	0,0,	442,0,	442,0,	
442,0,	442,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	441,0,	441,0,	441,0,	
442,0,	0,0,	442,0,	442,0,	
442,0,	0,0,	442,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	442,0,	442,0,	442,0,	
0,0,	442,454,	0,0,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,9,	442,9,	442,9,	
442,9,	442,0,	442,0,	442,0,	
443,0,	443,0,	443,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
443,0,	443,0,	443,0,	443,0,	
0,0,	0,0,	0,0,	443,0,	
443,0,	443,0,	0,0,	0,0,	
443,0,	443,0,	443,0,	443,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	443,0,	0,0,	
443,0,	443,0,	443,0,	0,0,	
443,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	443,0,	
443,0,	443,0,	0,0,	443,455,	
0,0,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,9,	
443,9,	443,9,	443,9,	443,0,	
443,0,	443,0,	444,0,	444,0,	
444,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	444,0,	444,0,	
444,0,	444,0,	0,0,	0,0,	
0,0,	444,0,	444,0,	444,0,	
0,0,	0,0,	444,0,	444,0,	
444,0,	444,0,	445,0,	445,0,	
445,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
444,0,	0,0,	444,0,	444,0,	
444,0,	0,0,	444,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	445,0,	445,0,	
445,0,	445,0,	0,0,	0,0,	
0,0,	445,0,	445,0,	445,0,	
0,0,	0,0,	445,0,	445,0,	
445,0,	445,0,	0,0,	0,0,	
0,0,	444,0,	444,0,	444,0,	
0,0,	0,0,	0,0,	0,0,	
445,0,	0,0,	445,0,	445,0,	
445,0,	0,0,	445,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	444,456,	0,0,	0,0,	
0,0,	0,0,	0,0,	450,0,	
450,0,	450,0,	0,0,	0,0,	
0,0,	444,0,	444,0,	444,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	445,0,	445,0,	445,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	450,0,	
450,0,	450,0,	450,0,	0,0,	
0,0,	0,0,	445,457,	450,0,	
450,0,	0,0,	0,0,	450,0,	
450,0,	450,0,	450,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	445,0,	445,0,	445,0,	
0,0,	450,0,	0,0,	450,0,	
450,0,	450,0,	0,0,	450,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	450,0,	450,0,	
450,0,	0,0,	450,462,	0,0,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,67,	450,67,	
450,67,	450,67,	450,0,	450,0,	
450,0,	451,0,	451,0,	451,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	451,0,	451,0,	451,0,	
451,0,	0,0,	0,0,	0,0,	
0,0,	451,0,	451,0,	0,0,	
0,0,	451,0,	451,0,	451,0,	
451,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	451,0,	
0,0,	451,0,	451,0,	451,0,	
0,0,	451,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
451,0,	451,0,	451,0,	0,0,	
451,463,	0,0,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,67,	451,67,	451,67,	451,67,	
451,0,	451,0,	451,0,	452,0,	
452,0,	452,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	452,0,	
452,0,	452,0,	452,0,	0,0,	
0,0,	0,0,	0,0,	452,0,	
452,0,	0,0,	0,0,	452,0,	
452,0,	452,0,	452,0,	453,0,	
453,0,	453,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	452,0,	0,0,	452,0,	
452,0,	452,0,	0,0,	452,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	453,0,	
453,0,	453,0,	453,0,	0,0,	
0,0,	0,0,	0,0,	453,0,	
453,0,	0,0,	0,0,	453,0,	
453,0,	453,0,	453,0,	0,0,	
0,0,	0,0,	452,0,	452,0,	
452,0,	0,0,	0,0,	0,0,	
0,0,	453,0,	0,0,	453,0,	
453,0,	453,0,	0,0,	453,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	452,464,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	454,0,	454,0,	454,0,	
0,0,	0,0,	452,0,	452,0,	
452,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	453,0,	453,0,	
453,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	454,0,	454,0,	454,0,	
454,0,	0,0,	0,0,	453,465,	
454,0,	454,0,	454,0,	0,0,	
0,0,	454,0,	454,0,	454,0,	
454,0,	455,0,	455,0,	455,0,	
0,0,	0,0,	453,0,	453,0,	
453,0,	0,0,	0,0,	454,0,	
0,0,	454,0,	454,0,	454,0,	
0,0,	454,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	455,0,	455,0,	455,0,	
455,0,	0,0,	0,0,	0,0,	
455,0,	455,0,	455,0,	0,0,	
0,0,	455,0,	455,0,	455,0,	
455,0,	0,0,	0,0,	0,0,	
454,0,	454,0,	454,0,	0,0,	
0,0,	0,0,	0,0,	455,0,	
0,0,	455,0,	455,0,	455,0,	
0,0,	455,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	454,466,	
0,0,	0,0,	0,0,	0,0,	
456,0,	456,0,	456,0,	0,0,	
454,0,	454,0,	454,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
455,0,	455,0,	455,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
456,0,	456,0,	456,0,	456,0,	
0,0,	0,0,	0,0,	456,0,	
456,0,	456,0,	0,0,	455,467,	
456,0,	456,0,	456,0,	456,0,	
457,0,	457,0,	457,0,	0,0,	
455,0,	455,0,	455,0,	0,0,	
0,0,	0,0,	456,0,	0,0,	
456,0,	456,0,	456,0,	0,0,	
456,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
457,0,	457,0,	457,0,	457,0,	
0,0,	0,0,	0,0,	457,0,	
457,0,	457,0,	0,0,	0,0,	
457,0,	457,0,	457,469,	457,0,	
0,0,	0,0,	0,0,	456,0,	
456,0,	456,0,	0,0,	0,0,	
0,0,	0,0,	457,0,	0,0,	
457,0,	457,0,	457,0,	0,0,	
457,0,	0,0,	0,0,	0,0,	
456,468,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
462,0,	462,0,	462,0,	0,0,	
0,0,	0,0,	0,0,	456,0,	
456,0,	456,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	457,0,	
457,0,	457,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
462,0,	462,0,	462,0,	462,0,	
0,0,	0,0,	0,0,	0,0,	
462,0,	462,0,	0,0,	0,0,	
462,0,	462,0,	462,0,	462,0,	
463,0,	463,0,	463,0,	0,0,	
0,0,	0,0,	0,0,	457,0,	
457,0,	457,0,	462,0,	0,0,	
462,0,	462,0,	462,0,	0,0,	
462,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
463,0,	463,0,	463,0,	463,0,	
0,0,	0,0,	0,0,	0,0,	
463,0,	463,0,	0,0,	0,0,	
463,0,	463,0,	463,0,	463,0,	
0,0,	0,0,	0,0,	462,0,	
462,0,	462,0,	0,0,	0,0,	
0,0,	0,0,	463,0,	0,0,	
463,0,	463,0,	463,0,	0,0,	
463,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	462,473,	0,0,	
0,0,	0,0,	0,0,	464,0,	
464,0,	464,0,	0,0,	462,0,	
462,0,	462,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	463,0,	
463,0,	463,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	464,0,	
464,0,	464,0,	464,0,	0,0,	
0,0,	0,0,	0,0,	464,0,	
464,0,	0,0,	463,474,	464,0,	
464,0,	464,0,	464,0,	465,0,	
465,0,	465,0,	0,0,	463,0,	
463,0,	463,0,	0,0,	0,0,	
0,0,	464,0,	0,0,	464,0,	
464,0,	464,0,	0,0,	464,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	465,0,	
465,0,	465,0,	465,0,	0,0,	
0,0,	0,0,	0,0,	465,0,	
465,0,	0,0,	0,0,	465,0,	
465,0,	465,469,	465,0,	0,0,	
0,0,	0,0,	464,0,	464,0,	
464,0,	0,0,	0,0,	0,0,	
0,0,	465,0,	0,0,	465,0,	
465,0,	465,0,	0,0,	465,0,	
0,0,	0,0,	0,0,	464,475,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	466,0,	
466,0,	466,0,	0,0,	0,0,	
0,0,	0,0,	464,0,	464,0,	
464,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	465,0,	465,0,	
465,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	466,0,	
466,0,	466,0,	466,0,	0,0,	
0,0,	0,0,	466,0,	466,0,	
466,0,	0,0,	0,0,	466,0,	
466,0,	466,0,	466,0,	467,0,	
467,0,	467,0,	0,0,	0,0,	
0,0,	0,0,	465,0,	465,0,	
465,0,	466,0,	0,0,	466,0,	
466,0,	466,0,	0,0,	466,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	467,0,	
467,0,	467,0,	467,0,	0,0,	
0,0,	0,0,	467,0,	467,0,	
467,0,	0,0,	0,0,	467,0,	
467,0,	467,0,	467,0,	0,0,	
0,0,	0,0,	466,0,	466,0,	
466,0,	0,0,	0,0,	0,0,	
0,0,	467,0,	0,0,	467,0,	
467,0,	467,0,	0,0,	467,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
466,476,	0,0,	0,0,	0,0,	
0,0,	0,0,	466,0,	466,0,	
466,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	467,0,	467,0,	
467,0,	0,0,	468,0,	468,0,	
468,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
467,477,	0,0,	468,0,	468,0,	
468,0,	468,0,	467,0,	467,0,	
467,0,	468,0,	468,0,	468,0,	
0,0,	0,0,	468,0,	468,0,	
468,0,	468,0,	473,0,	473,0,	
473,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
468,0,	0,0,	468,0,	468,0,	
468,0,	0,0,	468,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	473,0,	473,0,	
473,0,	473,0,	0,0,	0,0,	
0,0,	0,0,	473,0,	473,0,	
0,0,	0,0,	473,0,	473,0,	
473,0,	473,0,	0,0,	0,0,	
0,0,	468,0,	468,0,	468,0,	
0,0,	0,0,	0,0,	0,0,	
473,0,	0,0,	473,0,	473,0,	
473,0,	0,0,	473,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	468,478,	
0,0,	0,0,	0,0,	0,0,	
0,0,	468,0,	468,0,	468,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	473,0,	473,0,	473,0,	
474,0,	474,0,	474,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	473,482,	
474,0,	474,0,	474,0,	474,0,	
0,0,	473,0,	473,0,	473,0,	
474,0,	474,0,	0,0,	0,0,	
474,0,	474,0,	474,0,	474,0,	
475,0,	475,0,	475,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	474,0,	0,0,	
474,0,	474,0,	474,0,	0,0,	
474,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
475,0,	475,0,	475,0,	475,0,	
0,0,	0,0,	0,0,	0,0,	
475,0,	475,0,	0,0,	0,0,	
475,0,	475,0,	475,0,	475,0,	
0,0,	0,0,	0,0,	474,0,	
474,0,	474,0,	0,0,	0,0,	
0,0,	0,0,	475,0,	0,0,	
475,0,	475,0,	475,0,	0,0,	
475,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	474,483,	0,0,	0,0,	
0,0,	0,0,	0,0,	474,0,	
474,0,	474,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	475,0,	
475,0,	475,0,	0,0,	476,0,	
476,0,	476,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	475,484,	0,0,	476,0,	
476,0,	476,0,	476,0,	475,0,	
475,0,	475,0,	476,0,	476,0,	
476,0,	0,0,	0,0,	476,0,	
476,0,	476,0,	476,0,	477,0,	
477,0,	477,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	476,0,	0,0,	476,0,	
476,0,	476,0,	0,0,	476,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	477,0,	
477,0,	477,0,	477,0,	0,0,	
0,0,	0,0,	477,0,	477,0,	
477,0,	0,0,	0,0,	477,0,	
477,0,	477,0,	477,0,	0,0,	
0,0,	0,0,	476,0,	476,0,	
476,0,	0,0,	0,0,	0,0,	
0,0,	477,0,	0,0,	477,0,	
477,0,	477,0,	0,0,	477,0,	
0,0,	0,0,	0,0,	476,485,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	478,0,	478,0,	478,0,	
0,0,	0,0,	476,0,	476,0,	
476,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	477,0,	477,0,	
477,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	478,0,	478,0,	478,0,	
478,0,	0,0,	0,0,	477,486,	
478,0,	478,0,	478,0,	0,0,	
0,0,	478,0,	478,0,	478,0,	
478,0,	482,0,	482,0,	482,0,	
0,0,	0,0,	477,0,	477,0,	
477,0,	0,0,	0,0,	478,0,	
0,0,	478,0,	478,0,	478,0,	
0,0,	478,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	482,0,	482,0,	482,0,	
482,0,	0,0,	0,0,	0,0,	
0,0,	482,0,	482,0,	0,0,	
0,0,	482,0,	482,0,	482,0,	
482,0,	0,0,	0,0,	0,0,	
478,0,	478,0,	478,0,	0,0,	
0,0,	0,0,	0,0,	482,0,	
0,0,	482,0,	482,0,	482,0,	
0,0,	482,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	478,487,	483,0,	483,0,	
483,0,	0,0,	0,0,	0,0,	
478,0,	478,0,	478,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
482,0,	482,0,	482,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	483,0,	483,0,	
483,0,	483,0,	0,0,	0,0,	
0,0,	482,491,	483,0,	483,0,	
0,0,	0,0,	483,0,	483,0,	
483,0,	483,0,	484,0,	484,0,	
484,0,	0,0,	0,0,	0,0,	
482,0,	482,0,	482,0,	0,0,	
483,0,	0,0,	483,0,	483,0,	
483,0,	0,0,	483,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	484,0,	484,0,	
484,0,	484,0,	0,0,	0,0,	
0,0,	0,0,	484,0,	484,0,	
0,0,	0,0,	484,0,	484,0,	
484,0,	484,0,	0,0,	0,0,	
0,0,	483,0,	483,0,	483,0,	
0,0,	0,0,	0,0,	0,0,	
484,0,	0,0,	484,0,	484,0,	
484,0,	0,0,	484,0,	0,0,	
0,0,	0,0,	483,492,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	485,0,	485,0,	
485,0,	0,0,	0,0,	0,0,	
0,0,	483,0,	483,0,	483,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	484,0,	484,0,	484,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	485,0,	485,0,	
485,0,	485,0,	0,0,	0,0,	
0,0,	485,0,	485,0,	485,0,	
0,0,	0,0,	485,0,	485,0,	
485,0,	485,0,	484,493,	0,0,	
486,0,	486,0,	486,0,	0,0,	
0,0,	484,0,	484,0,	484,0,	
485,0,	0,0,	485,0,	485,0,	
485,0,	0,0,	485,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
486,0,	486,0,	486,0,	486,0,	
0,0,	0,0,	0,0,	486,0,	
486,0,	486,0,	0,0,	0,0,	
486,0,	486,0,	486,0,	486,0,	
0,0,	485,0,	485,0,	485,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	486,0,	485,494,	
486,0,	486,0,	486,0,	0,0,	
486,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	487,0,	487,0,	
487,0,	485,0,	485,0,	485,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	486,0,	
486,0,	486,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	486,495,	487,0,	487,0,	
487,0,	487,0,	0,0,	0,0,	
0,0,	487,0,	487,0,	487,0,	
0,0,	0,0,	487,0,	487,0,	
487,0,	487,0,	0,0,	0,0,	
491,0,	491,0,	491,0,	486,0,	
486,0,	486,0,	0,0,	0,0,	
487,0,	0,0,	487,0,	487,0,	
487,0,	0,0,	487,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
491,0,	491,0,	491,0,	491,0,	
0,0,	0,0,	0,0,	0,0,	
491,0,	491,0,	0,0,	0,0,	
491,0,	491,0,	491,0,	491,0,	
0,0,	487,0,	487,0,	487,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	491,0,	487,496,	
491,0,	491,0,	491,0,	0,0,	
491,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	492,0,	492,0,	
492,0,	487,0,	487,0,	487,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	491,0,	
491,0,	491,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	491,500,	492,0,	492,0,	
492,0,	492,0,	0,0,	0,0,	
0,0,	0,0,	492,0,	492,0,	
0,0,	0,0,	492,0,	492,0,	
492,0,	492,0,	0,0,	0,0,	
493,0,	493,0,	493,0,	491,0,	
491,0,	491,0,	0,0,	0,0,	
492,0,	0,0,	492,0,	492,0,	
492,0,	0,0,	492,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
493,0,	493,0,	493,0,	493,0,	
0,0,	0,0,	0,0,	0,0,	
493,0,	493,0,	0,0,	0,0,	
493,0,	493,0,	493,0,	493,0,	
0,0,	492,0,	492,0,	492,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	493,0,	492,501,	
493,0,	493,0,	493,0,	0,0,	
493,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	494,0,	494,0,	
494,0,	492,0,	492,0,	492,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	493,0,	
493,0,	493,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	493,502,	494,0,	494,0,	
494,0,	494,0,	0,0,	0,0,	
0,0,	494,0,	494,0,	494,0,	
0,0,	0,0,	494,0,	494,0,	
494,503,	494,0,	495,0,	495,0,	
495,0,	0,0,	0,0,	493,0,	
493,0,	493,0,	0,0,	0,0,	
494,0,	0,0,	494,0,	494,0,	
494,0,	0,0,	494,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	495,0,	495,0,	
495,0,	495,0,	0,0,	0,0,	
0,0,	495,0,	495,0,	495,0,	
0,0,	0,0,	495,0,	495,0,	
495,504,	495,0,	0,0,	0,0,	
0,0,	494,0,	494,0,	494,0,	
0,0,	0,0,	0,0,	0,0,	
495,0,	0,0,	495,0,	495,0,	
495,0,	0,0,	495,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	496,0,	496,0,	
496,0,	0,0,	0,0,	0,0,	
0,0,	494,0,	494,0,	494,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	495,0,	495,0,	495,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	496,0,	496,0,	
496,0,	496,0,	0,0,	0,0,	
0,0,	496,0,	496,0,	496,0,	
0,0,	0,0,	496,0,	496,0,	
496,0,	496,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	495,0,	495,0,	495,0,	
496,0,	0,0,	496,0,	496,0,	
496,0,	0,0,	496,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	496,0,	496,0,	496,0,	
0,0,	496,505,	0,0,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,9,	496,9,	496,9,	
496,9,	496,0,	496,0,	496,0,	
500,0,	500,0,	500,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
500,0,	500,0,	500,0,	500,0,	
0,0,	0,0,	0,0,	0,0,	
500,0,	500,0,	0,0,	0,0,	
500,0,	500,0,	500,503,	500,0,	
501,0,	501,0,	501,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	500,0,	0,0,	
500,0,	500,0,	500,0,	0,0,	
500,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
501,0,	501,0,	501,0,	501,0,	
0,0,	0,0,	0,0,	0,0,	
501,0,	501,0,	0,0,	0,0,	
501,0,	501,0,	501,504,	501,0,	
0,0,	0,0,	0,0,	500,0,	
500,0,	500,0,	0,0,	0,0,	
0,0,	0,0,	501,0,	0,0,	
501,0,	501,0,	501,0,	0,0,	
501,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
502,0,	502,0,	502,0,	0,0,	
0,0,	0,0,	0,0,	500,0,	
500,0,	500,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	501,0,	
501,0,	501,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
502,0,	502,0,	502,0,	502,0,	
0,0,	0,0,	0,0,	0,0,	
502,0,	502,0,	0,0,	0,0,	
502,0,	502,0,	502,0,	502,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	501,0,	
501,0,	501,0,	502,0,	0,0,	
502,0,	502,0,	502,0,	0,0,	
502,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	502,0,	
502,0,	502,0,	0,0,	502,507,	
0,0,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,67,	
502,67,	502,67,	502,67,	502,0,	
502,0,	502,0,	505,0,	505,0,	
505,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	505,0,	505,0,	
505,0,	505,0,	0,0,	0,0,	
0,0,	505,0,	505,0,	505,0,	
0,0,	0,0,	505,0,	505,0,	
505,0,	505,0,	507,0,	507,0,	
507,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
505,0,	0,0,	505,0,	505,0,	
505,0,	0,0,	505,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	507,0,	507,0,	
507,0,	507,0,	0,0,	0,0,	
0,0,	0,0,	507,0,	507,0,	
0,0,	0,0,	507,0,	507,0,	
507,0,	507,0,	0,0,	0,0,	
0,0,	505,0,	505,0,	505,0,	
0,0,	0,0,	0,0,	0,0,	
507,0,	0,0,	507,0,	507,0,	
507,0,	0,0,	507,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
505,508,	0,0,	0,0,	0,0,	
0,0,	508,0,	508,0,	508,0,	
0,0,	505,0,	505,0,	505,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	507,0,	507,0,	507,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	508,0,	508,0,	508,0,	
508,0,	0,0,	0,0,	0,0,	
508,0,	508,0,	508,0,	0,0,	
507,510,	508,0,	508,0,	508,0,	
508,0,	510,0,	510,0,	510,0,	
0,0,	507,0,	507,0,	507,0,	
0,0,	0,0,	0,0,	508,0,	
0,0,	508,0,	508,0,	508,0,	
0,0,	508,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	510,0,	510,0,	510,0,	
510,0,	0,0,	0,0,	0,0,	
0,0,	510,0,	510,0,	0,0,	
0,0,	510,0,	510,0,	510,0,	
510,0,	0,0,	0,0,	0,0,	
508,0,	508,0,	508,0,	0,0,	
0,0,	0,0,	0,0,	510,0,	
0,0,	510,0,	510,0,	510,0,	
0,0,	510,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	508,511,	0,0,	
0,0,	0,0,	0,0,	0,0,	
508,0,	508,0,	508,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
510,0,	510,0,	510,0,	0,0,	
511,0,	511,0,	511,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	510,513,	0,0,	
511,0,	511,0,	511,0,	511,0,	
510,0,	510,0,	510,0,	511,0,	
511,0,	511,0,	0,0,	0,0,	
511,0,	511,0,	511,0,	511,0,	
513,0,	513,0,	513,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	511,0,	0,0,	
511,0,	511,0,	511,0,	0,0,	
511,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
513,0,	513,0,	513,0,	513,0,	
0,0,	0,0,	0,0,	0,0,	
513,0,	513,0,	0,0,	0,0,	
513,0,	513,0,	513,0,	513,0,	
0,0,	0,0,	0,0,	511,0,	
511,0,	511,0,	0,0,	0,0,	
0,0,	0,0,	513,0,	0,0,	
513,0,	513,0,	513,0,	0,0,	
513,0,	0,0,	0,0,	0,0,	
511,514,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	514,0,	514,0,	
514,0,	0,0,	0,0,	511,0,	
511,0,	511,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	513,0,	
513,0,	513,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	514,0,	514,0,	
514,0,	514,0,	0,0,	0,0,	
513,516,	514,0,	514,0,	514,0,	
0,0,	0,0,	514,0,	514,0,	
514,0,	514,0,	0,0,	0,0,	
516,0,	516,0,	516,0,	513,0,	
513,0,	513,0,	0,0,	0,0,	
514,0,	0,0,	514,0,	514,0,	
514,0,	0,0,	514,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
516,0,	516,0,	516,0,	516,0,	
0,0,	0,0,	0,0,	0,0,	
516,0,	516,0,	0,0,	0,0,	
516,0,	516,0,	516,0,	516,0,	
0,0,	514,0,	514,0,	514,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	516,0,	514,517,	
516,0,	516,0,	516,0,	0,0,	
516,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	517,0,	517,0,	
517,0,	514,0,	514,0,	514,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	516,0,	
516,0,	516,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	516,519,	517,0,	517,0,	
517,0,	517,0,	0,0,	0,0,	
0,0,	517,0,	517,0,	517,0,	
0,0,	0,0,	517,0,	517,0,	
517,520,	517,0,	519,0,	519,0,	
519,0,	0,0,	0,0,	516,0,	
516,0,	516,0,	0,0,	0,0,	
517,0,	0,0,	517,0,	517,0,	
517,0,	0,0,	517,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	519,0,	519,0,	
519,0,	519,0,	0,0,	0,0,	
0,0,	0,0,	519,0,	519,0,	
0,0,	0,0,	519,0,	519,0,	
519,520,	519,0,	0,0,	0,0,	
0,0,	517,0,	517,0,	517,0,	
0,0,	0,0,	0,0,	0,0,	
519,0,	0,0,	519,0,	519,0,	
519,0,	0,0,	519,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	517,0,	517,0,	517,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	519,0,	519,0,	519,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	0,0,	0,0,	0,0,	
0,0,	519,0,	519,0,	519,0,	
0,0};
struct yysvf yysvec[] = {
0,	0,	0,
yycrank+-1,	0,		0,			/* state 0 */
yycrank+-89,	yysvec+1,	0,			/* state 1 */
yycrank+207,	0,		0,			/* state 2 */
yycrank+0,	yysvec+3,	0,			/* state 3 */
yycrank+-300,	yysvec+1,	0,			/* state 4 */
yycrank+-391,	yysvec+1,	0,			/* state 5 */
yycrank+0,	yysvec+3,	0,			/* state 6 */
yycrank+0,	yysvec+3,	0,			/* state 7 */
yycrank+-516,	0,		yyvstop+1,		/* state 8 */
yycrank+0,	0,		yyvstop+3,		/* state 9 */
yycrank+0,	0,		yyvstop+5,		/* state 10 */
yycrank+0,	0,		yyvstop+7,		/* state 11 */
yycrank+0,	0,		yyvstop+9,		/* state 12 */
yycrank+0,	0,		yyvstop+12,		/* state 13 */
yycrank+0,	0,		yyvstop+14,		/* state 14 */
yycrank+-557,	0,		0,			/* state 15 */
yycrank+-622,	0,		yyvstop+16,		/* state 16 */
yycrank+-663,	yysvec+9,	yyvstop+18,		/* state 17 */
yycrank+-732,	0,		0,			/* state 18 */
yycrank+0,	0,		yyvstop+20,		/* state 19 */
yycrank+0,	0,		yyvstop+22,		/* state 20 */
yycrank+-773,	yysvec+9,	yyvstop+24,		/* state 21 */
yycrank+0,	0,		yyvstop+27,		/* state 22 */
yycrank+0,	0,		yyvstop+29,		/* state 23 */
yycrank+0,	0,		yyvstop+31,		/* state 24 */
yycrank+0,	0,		yyvstop+33,		/* state 25 */
yycrank+-841,	yysvec+9,	yyvstop+35,		/* state 26 */
yycrank+6,	0,		yyvstop+38,		/* state 27 */
yycrank+5,	0,		yyvstop+40,		/* state 28 */
yycrank+5,	0,		yyvstop+42,		/* state 29 */
yycrank+0,	0,		yyvstop+44,		/* state 30 */
yycrank+-882,	0,		0,			/* state 31 */
yycrank+-950,	yysvec+9,	yyvstop+46,		/* state 32 */
yycrank+20,	0,		yyvstop+49,		/* state 33 */
yycrank+0,	0,		yyvstop+51,		/* state 34 */
yycrank+0,	0,		yyvstop+53,		/* state 35 */
yycrank+-991,	yysvec+9,	yyvstop+55,		/* state 36 */
yycrank+-1059,	0,		yyvstop+58,		/* state 37 */
yycrank+-1179,	yysvec+9,	yyvstop+60,		/* state 38 */
yycrank+-1219,	yysvec+9,	yyvstop+62,		/* state 39 */
yycrank+-1287,	yysvec+9,	yyvstop+64,		/* state 40 */
yycrank+-1327,	yysvec+9,	yyvstop+66,		/* state 41 */
yycrank+-1397,	yysvec+9,	yyvstop+68,		/* state 42 */
yycrank+-1437,	yysvec+9,	yyvstop+70,		/* state 43 */
yycrank+-1508,	yysvec+9,	yyvstop+72,		/* state 44 */
yycrank+-1578,	yysvec+9,	yyvstop+74,		/* state 45 */
yycrank+-1618,	yysvec+9,	yyvstop+76,		/* state 46 */
yycrank+-1686,	yysvec+9,	yyvstop+78,		/* state 47 */
yycrank+-1728,	yysvec+9,	yyvstop+80,		/* state 48 */
yycrank+-1815,	yysvec+9,	yyvstop+82,		/* state 49 */
yycrank+-1855,	yysvec+9,	yyvstop+84,		/* state 50 */
yycrank+-1949,	yysvec+9,	yyvstop+86,		/* state 51 */
yycrank+0,	0,		yyvstop+88,		/* state 52 */
yycrank+7,	0,		yyvstop+90,		/* state 53 */
yycrank+0,	0,		yyvstop+92,		/* state 54 */
yycrank+-218,	yysvec+17,	0,			/* state 55 */
yycrank+34,	0,		0,			/* state 56 */
yycrank+0,	0,		yyvstop+94,		/* state 57 */
yycrank+0,	yysvec+30,	0,			/* state 58 */
yycrank+0,	0,		yyvstop+96,		/* state 59 */
yycrank+32,	0,		0,			/* state 60 */
yycrank+25,	0,		0,			/* state 61 */
yycrank+25,	0,		0,			/* state 62 */
yycrank+39,	0,		0,			/* state 63 */
yycrank+30,	0,		0,			/* state 64 */
yycrank+45,	0,		0,			/* state 65 */
yycrank+-1991,	0,		yyvstop+98,		/* state 66 */
yycrank+-2059,	0,		0,			/* state 67 */
yycrank+-223,	yysvec+17,	yyvstop+100,		/* state 68 */
yycrank+-2100,	yysvec+67,	yyvstop+102,		/* state 69 */
yycrank+-2169,	0,		yyvstop+104,		/* state 70 */
yycrank+0,	0,		yyvstop+106,		/* state 71 */
yycrank+0,	0,		yyvstop+108,		/* state 72 */
yycrank+-2210,	yysvec+67,	yyvstop+110,		/* state 73 */
yycrank+-2278,	yysvec+67,	yyvstop+113,		/* state 74 */
yycrank+0,	yysvec+30,	yyvstop+116,		/* state 75 */
yycrank+-2319,	0,		0,			/* state 76 */
yycrank+-2387,	yysvec+67,	yyvstop+118,		/* state 77 */
yycrank+30,	0,		yyvstop+121,		/* state 78 */
yycrank+-2428,	yysvec+67,	yyvstop+123,		/* state 79 */
yycrank+-2496,	0,		yyvstop+126,		/* state 80 */
yycrank+-2616,	yysvec+67,	yyvstop+128,		/* state 81 */
yycrank+-2656,	yysvec+67,	yyvstop+130,		/* state 82 */
yycrank+-2724,	yysvec+67,	yyvstop+132,		/* state 83 */
yycrank+-2764,	yysvec+67,	yyvstop+134,		/* state 84 */
yycrank+-2834,	yysvec+67,	yyvstop+136,		/* state 85 */
yycrank+-2874,	yysvec+67,	yyvstop+138,		/* state 86 */
yycrank+-2944,	yysvec+67,	yyvstop+140,		/* state 87 */
yycrank+-2986,	yysvec+67,	yyvstop+142,		/* state 88 */
yycrank+-3054,	yysvec+67,	yyvstop+144,		/* state 89 */
yycrank+-3094,	yysvec+67,	yyvstop+146,		/* state 90 */
yycrank+-3164,	yysvec+67,	yyvstop+148,		/* state 91 */
yycrank+-3204,	yysvec+67,	yyvstop+150,		/* state 92 */
yycrank+-3290,	yysvec+67,	yyvstop+152,		/* state 93 */
yycrank+-3330,	yysvec+67,	yyvstop+154,		/* state 94 */
yycrank+-3398,	yysvec+16,	yyvstop+156,		/* state 95 */
yycrank+-16,	yysvec+17,	yyvstop+158,		/* state 96 */
yycrank+-224,	yysvec+17,	0,			/* state 97 */
yycrank+-3438,	yysvec+9,	yyvstop+160,		/* state 98 */
yycrank+-3508,	yysvec+19,	0,			/* state 99 */
yycrank+0,	0,		yyvstop+162,		/* state 100 */
yycrank+0,	0,		yyvstop+164,		/* state 101 */
yycrank+0,	0,		yyvstop+166,		/* state 102 */
yycrank+-3548,	yysvec+32,	yyvstop+168,		/* state 103 */
yycrank+42,	yysvec+34,	0,			/* state 104 */
yycrank+-3603,	yysvec+9,	yyvstop+170,		/* state 105 */
yycrank+-3643,	yysvec+9,	yyvstop+172,		/* state 106 */
yycrank+-3713,	yysvec+9,	yyvstop+174,		/* state 107 */
yycrank+-3753,	yysvec+9,	yyvstop+176,		/* state 108 */
yycrank+-3821,	yysvec+9,	yyvstop+178,		/* state 109 */
yycrank+-3863,	yysvec+9,	yyvstop+180,		/* state 110 */
yycrank+-3950,	yysvec+9,	yyvstop+182,		/* state 111 */
yycrank+-3990,	yysvec+9,	yyvstop+184,		/* state 112 */
yycrank+-4060,	yysvec+9,	yyvstop+186,		/* state 113 */
yycrank+-4102,	yysvec+9,	yyvstop+188,		/* state 114 */
yycrank+-4171,	yysvec+9,	yyvstop+190,		/* state 115 */
yycrank+-4211,	yysvec+9,	yyvstop+192,		/* state 116 */
yycrank+-4279,	yysvec+9,	yyvstop+194,		/* state 117 */
yycrank+-4319,	yysvec+9,	yyvstop+196,		/* state 118 */
yycrank+-4390,	yysvec+9,	yyvstop+198,		/* state 119 */
yycrank+-4430,	yysvec+9,	yyvstop+200,		/* state 120 */
yycrank+-4498,	yysvec+9,	yyvstop+202,		/* state 121 */
yycrank+-4538,	yysvec+9,	yyvstop+204,		/* state 122 */
yycrank+-4606,	yysvec+9,	yyvstop+206,		/* state 123 */
yycrank+-4646,	yysvec+9,	yyvstop+208,		/* state 124 */
yycrank+-4733,	yysvec+9,	yyvstop+210,		/* state 125 */
yycrank+0,	0,		yyvstop+212,		/* state 126 */
yycrank+42,	0,		0,			/* state 127 */
yycrank+42,	0,		0,			/* state 128 */
yycrank+28,	0,		0,			/* state 129 */
yycrank+45,	0,		0,			/* state 130 */
yycrank+33,	0,		0,			/* state 131 */
yycrank+36,	0,		0,			/* state 132 */
yycrank+45,	0,		0,			/* state 133 */
yycrank+46,	0,		0,			/* state 134 */
yycrank+-4773,	yysvec+68,	yyvstop+214,		/* state 135 */
yycrank+-1196,	yysvec+17,	yyvstop+216,		/* state 136 */
yycrank+-4827,	yysvec+67,	yyvstop+218,		/* state 137 */
yycrank+-4869,	yysvec+71,	yyvstop+220,		/* state 138 */
yycrank+-4925,	yysvec+71,	0,			/* state 139 */
yycrank+-4966,	yysvec+77,	yyvstop+222,		/* state 140 */
yycrank+43,	yysvec+79,	0,			/* state 141 */
yycrank+-5021,	yysvec+67,	yyvstop+224,		/* state 142 */
yycrank+-5061,	yysvec+67,	yyvstop+226,		/* state 143 */
yycrank+-5131,	yysvec+67,	yyvstop+228,		/* state 144 */
yycrank+-5171,	yysvec+67,	yyvstop+230,		/* state 145 */
yycrank+-5239,	yysvec+67,	yyvstop+232,		/* state 146 */
yycrank+-5281,	yysvec+67,	yyvstop+234,		/* state 147 */
yycrank+-5367,	yysvec+67,	yyvstop+236,		/* state 148 */
yycrank+-5407,	yysvec+67,	yyvstop+238,		/* state 149 */
yycrank+-5477,	yysvec+67,	yyvstop+240,		/* state 150 */
yycrank+-5519,	yysvec+67,	yyvstop+242,		/* state 151 */
yycrank+-5588,	yysvec+67,	yyvstop+244,		/* state 152 */
yycrank+-5628,	yysvec+67,	yyvstop+246,		/* state 153 */
yycrank+-5696,	yysvec+67,	yyvstop+248,		/* state 154 */
yycrank+-5736,	yysvec+67,	yyvstop+250,		/* state 155 */
yycrank+-5806,	yysvec+67,	yyvstop+252,		/* state 156 */
yycrank+-5846,	yysvec+67,	yyvstop+254,		/* state 157 */
yycrank+-5914,	yysvec+67,	yyvstop+256,		/* state 158 */
yycrank+-5954,	yysvec+67,	yyvstop+258,		/* state 159 */
yycrank+-6022,	yysvec+67,	yyvstop+260,		/* state 160 */
yycrank+-6062,	yysvec+67,	yyvstop+262,		/* state 161 */
yycrank+-6148,	yysvec+67,	yyvstop+264,		/* state 162 */
yycrank+0,	0,		yyvstop+266,		/* state 163 */
yycrank+-6188,	yysvec+9,	yyvstop+268,		/* state 164 */
yycrank+-6259,	yysvec+19,	yyvstop+270,		/* state 165 */
yycrank+44,	0,		0,			/* state 166 */
yycrank+-6299,	yysvec+9,	yyvstop+272,		/* state 167 */
yycrank+-6367,	yysvec+9,	yyvstop+274,		/* state 168 */
yycrank+-6407,	yysvec+9,	yyvstop+276,		/* state 169 */
yycrank+-6475,	yysvec+9,	yyvstop+278,		/* state 170 */
yycrank+-6515,	yysvec+9,	yyvstop+280,		/* state 171 */
yycrank+-6584,	yysvec+9,	yyvstop+282,		/* state 172 */
yycrank+-6627,	yysvec+9,	yyvstop+284,		/* state 173 */
yycrank+-6695,	yysvec+9,	yyvstop+286,		/* state 174 */
yycrank+-6735,	yysvec+9,	yyvstop+288,		/* state 175 */
yycrank+-6803,	yysvec+9,	yyvstop+290,		/* state 176 */
yycrank+-6843,	yysvec+9,	yyvstop+292,		/* state 177 */
yycrank+-6915,	yysvec+9,	yyvstop+294,		/* state 178 */
yycrank+-6955,	yysvec+38,	yyvstop+296,		/* state 179 */
yycrank+-7073,	yysvec+9,	yyvstop+299,		/* state 180 */
yycrank+-7114,	yysvec+9,	yyvstop+301,		/* state 181 */
yycrank+-7184,	yysvec+9,	yyvstop+303,		/* state 182 */
yycrank+-7224,	yysvec+9,	yyvstop+305,		/* state 183 */
yycrank+-7293,	yysvec+9,	yyvstop+307,		/* state 184 */
yycrank+-7333,	yysvec+9,	yyvstop+309,		/* state 185 */
yycrank+-7403,	yysvec+9,	yyvstop+311,		/* state 186 */
yycrank+-7445,	yysvec+9,	yyvstop+313,		/* state 187 */
yycrank+-7532,	yysvec+9,	yyvstop+315,		/* state 188 */
yycrank+55,	0,		0,			/* state 189 */
yycrank+56,	0,		0,			/* state 190 */
yycrank+62,	0,		0,			/* state 191 */
yycrank+63,	0,		0,			/* state 192 */
yycrank+46,	0,		0,			/* state 193 */
yycrank+67,	0,		yyvstop+317,		/* state 194 */
yycrank+62,	0,		0,			/* state 195 */
yycrank+63,	0,		0,			/* state 196 */
yycrank+-7574,	yysvec+67,	yyvstop+319,		/* state 197 */
yycrank+-7661,	yysvec+71,	yyvstop+321,		/* state 198 */
yycrank+-7702,	yysvec+71,	yyvstop+324,		/* state 199 */
yycrank+45,	0,		0,			/* state 200 */
yycrank+-7770,	yysvec+67,	yyvstop+326,		/* state 201 */
yycrank+-7811,	yysvec+67,	yyvstop+328,		/* state 202 */
yycrank+-7879,	yysvec+67,	yyvstop+330,		/* state 203 */
yycrank+-7919,	yysvec+67,	yyvstop+332,		/* state 204 */
yycrank+-7991,	yysvec+67,	yyvstop+334,		/* state 205 */
yycrank+-8060,	yysvec+67,	yyvstop+336,		/* state 206 */
yycrank+-8103,	yysvec+67,	yyvstop+338,		/* state 207 */
yycrank+-8146,	yysvec+67,	yyvstop+340,		/* state 208 */
yycrank+-8189,	yysvec+67,	yyvstop+342,		/* state 209 */
yycrank+-8232,	yysvec+67,	yyvstop+344,		/* state 210 */
yycrank+-8275,	yysvec+67,	yyvstop+346,		/* state 211 */
yycrank+-8318,	yysvec+67,	yyvstop+348,		/* state 212 */
yycrank+-8361,	yysvec+81,	yyvstop+350,		/* state 213 */
yycrank+-8479,	yysvec+67,	yyvstop+353,		/* state 214 */
yycrank+-8520,	yysvec+67,	yyvstop+355,		/* state 215 */
yycrank+-8590,	yysvec+67,	yyvstop+357,		/* state 216 */
yycrank+-8630,	yysvec+67,	yyvstop+359,		/* state 217 */
yycrank+-8699,	yysvec+67,	yyvstop+361,		/* state 218 */
yycrank+-8739,	yysvec+67,	yyvstop+363,		/* state 219 */
yycrank+-8809,	yysvec+67,	yyvstop+365,		/* state 220 */
yycrank+-8851,	yysvec+67,	yyvstop+367,		/* state 221 */
yycrank+-8937,	yysvec+67,	yyvstop+369,		/* state 222 */
yycrank+-8979,	yysvec+9,	yyvstop+371,		/* state 223 */
yycrank+117,	0,		0,			/* state 224 */
yycrank+-9047,	yysvec+9,	yyvstop+373,		/* state 225 */
yycrank+-9087,	yysvec+9,	yyvstop+375,		/* state 226 */
yycrank+-9155,	yysvec+9,	yyvstop+377,		/* state 227 */
yycrank+-9196,	yysvec+9,	yyvstop+379,		/* state 228 */
yycrank+-9266,	yysvec+9,	yyvstop+381,		/* state 229 */
yycrank+-9306,	yysvec+9,	yyvstop+383,		/* state 230 */
yycrank+-9376,	yysvec+9,	yyvstop+385,		/* state 231 */
yycrank+-9416,	yysvec+9,	yyvstop+387,		/* state 232 */
yycrank+-9484,	yysvec+9,	yyvstop+390,		/* state 233 */
yycrank+-9524,	yysvec+9,	yyvstop+392,		/* state 234 */
yycrank+-9594,	yysvec+9,	yyvstop+394,		/* state 235 */
yycrank+-9634,	yysvec+9,	yyvstop+397,		/* state 236 */
yycrank+-9704,	yysvec+9,	yyvstop+399,		/* state 237 */
yycrank+-9746,	yysvec+9,	yyvstop+401,		/* state 238 */
yycrank+-9816,	yysvec+9,	yyvstop+403,		/* state 239 */
yycrank+-9856,	yysvec+9,	yyvstop+405,		/* state 240 */
yycrank+-9926,	yysvec+9,	yyvstop+407,		/* state 241 */
yycrank+-9966,	yysvec+9,	yyvstop+409,		/* state 242 */
yycrank+-10034,	yysvec+9,	yyvstop+411,		/* state 243 */
yycrank+-10075,	yysvec+9,	yyvstop+414,		/* state 244 */
yycrank+-10143,	yysvec+9,	yyvstop+417,		/* state 245 */
yycrank+-10183,	yysvec+38,	yyvstop+419,		/* state 246 */
yycrank+70,	0,		0,			/* state 247 */
yycrank+75,	0,		0,			/* state 248 */
yycrank+69,	0,		0,			/* state 249 */
yycrank+62,	0,		0,			/* state 250 */
yycrank+0,	0,		yyvstop+422,		/* state 251 */
yycrank+78,	0,		0,			/* state 252 */
yycrank+0,	0,		yyvstop+424,		/* state 253 */
yycrank+0,	0,		yyvstop+426,		/* state 254 */
yycrank+-10301,	yysvec+67,	yyvstop+428,		/* state 255 */
yycrank+225,	0,		0,			/* state 256 */
yycrank+-10341,	yysvec+67,	yyvstop+430,		/* state 257 */
yycrank+-10409,	yysvec+67,	yyvstop+432,		/* state 258 */
yycrank+-10449,	yysvec+67,	yyvstop+434,		/* state 259 */
yycrank+-10521,	yysvec+67,	yyvstop+436,		/* state 260 */
yycrank+-10591,	yysvec+67,	yyvstop+438,		/* state 261 */
yycrank+-10631,	yysvec+67,	yyvstop+440,		/* state 262 */
yycrank+-10701,	yysvec+67,	yyvstop+442,		/* state 263 */
yycrank+-10741,	yysvec+67,	yyvstop+444,		/* state 264 */
yycrank+-10809,	yysvec+67,	yyvstop+447,		/* state 265 */
yycrank+-10849,	yysvec+67,	yyvstop+449,		/* state 266 */
yycrank+-10919,	yysvec+67,	yyvstop+451,		/* state 267 */
yycrank+-10959,	yysvec+67,	yyvstop+454,		/* state 268 */
yycrank+-11029,	yysvec+67,	yyvstop+456,		/* state 269 */
yycrank+-11071,	yysvec+67,	yyvstop+458,		/* state 270 */
yycrank+-11141,	yysvec+67,	yyvstop+460,		/* state 271 */
yycrank+-11181,	yysvec+67,	yyvstop+462,		/* state 272 */
yycrank+-11251,	yysvec+67,	yyvstop+464,		/* state 273 */
yycrank+-11291,	yysvec+67,	yyvstop+466,		/* state 274 */
yycrank+-11359,	yysvec+67,	yyvstop+468,		/* state 275 */
yycrank+-11400,	yysvec+67,	yyvstop+471,		/* state 276 */
yycrank+-11468,	yysvec+67,	yyvstop+474,		/* state 277 */
yycrank+-11508,	yysvec+81,	yyvstop+476,		/* state 278 */
yycrank+-11626,	yysvec+9,	yyvstop+479,		/* state 279 */
yycrank+88,	yysvec+225,	0,			/* state 280 */
yycrank+-11666,	yysvec+9,	yyvstop+481,		/* state 281 */
yycrank+-11736,	yysvec+9,	yyvstop+483,		/* state 282 */
yycrank+-11776,	yysvec+9,	yyvstop+486,		/* state 283 */
yycrank+-11844,	yysvec+9,	yyvstop+489,		/* state 284 */
yycrank+-11884,	yysvec+9,	yyvstop+492,		/* state 285 */
yycrank+-11952,	yysvec+9,	yyvstop+494,		/* state 286 */
yycrank+-11993,	yysvec+9,	yyvstop+496,		/* state 287 */
yycrank+-12061,	yysvec+9,	yyvstop+499,		/* state 288 */
yycrank+-12103,	yysvec+9,	yyvstop+501,		/* state 289 */
yycrank+-12190,	yysvec+9,	yyvstop+503,		/* state 290 */
yycrank+-12230,	yysvec+9,	yyvstop+505,		/* state 291 */
yycrank+-12300,	yysvec+9,	yyvstop+507,		/* state 292 */
yycrank+-12340,	yysvec+9,	yyvstop+509,		/* state 293 */
yycrank+-12408,	yysvec+9,	yyvstop+511,		/* state 294 */
yycrank+-12449,	yysvec+9,	yyvstop+514,		/* state 295 */
yycrank+-12536,	yysvec+9,	yyvstop+516,		/* state 296 */
yycrank+-12576,	yysvec+9,	yyvstop+518,		/* state 297 */
yycrank+-12646,	yysvec+9,	yyvstop+520,		/* state 298 */
yycrank+73,	0,		0,			/* state 299 */
yycrank+70,	0,		0,			/* state 300 */
yycrank+0,	0,		yyvstop+522,		/* state 301 */
yycrank+84,	0,		0,			/* state 302 */
yycrank+105,	0,		0,			/* state 303 */
yycrank+-12719,	yysvec+67,	yyvstop+524,		/* state 304 */
yycrank+127,	yysvec+257,	0,			/* state 305 */
yycrank+-12787,	yysvec+67,	yyvstop+526,		/* state 306 */
yycrank+-12829,	yysvec+67,	yyvstop+528,		/* state 307 */
yycrank+-12897,	yysvec+67,	yyvstop+531,		/* state 308 */
yycrank+-12937,	yysvec+67,	yyvstop+534,		/* state 309 */
yycrank+-13005,	yysvec+67,	yyvstop+537,		/* state 310 */
yycrank+-13045,	yysvec+67,	yyvstop+539,		/* state 311 */
yycrank+-13116,	yysvec+67,	yyvstop+541,		/* state 312 */
yycrank+-13156,	yysvec+67,	yyvstop+544,		/* state 313 */
yycrank+-13226,	yysvec+67,	yyvstop+546,		/* state 314 */
yycrank+-13266,	yysvec+67,	yyvstop+548,		/* state 315 */
yycrank+-13337,	yysvec+67,	yyvstop+550,		/* state 316 */
yycrank+-13377,	yysvec+67,	yyvstop+552,		/* state 317 */
yycrank+-13448,	yysvec+67,	yyvstop+554,		/* state 318 */
yycrank+-13488,	yysvec+67,	yyvstop+556,		/* state 319 */
yycrank+-13557,	yysvec+67,	yyvstop+559,		/* state 320 */
yycrank+-13597,	yysvec+67,	yyvstop+561,		/* state 321 */
yycrank+-13665,	yysvec+67,	yyvstop+563,		/* state 322 */
yycrank+-13707,	yysvec+67,	yyvstop+565,		/* state 323 */
yycrank+-13794,	yysvec+9,	yyvstop+567,		/* state 324 */
yycrank+0,	0,		yyvstop+569,		/* state 325 */
yycrank+-13836,	yysvec+9,	yyvstop+571,		/* state 326 */
yycrank+-13904,	yysvec+9,	yyvstop+573,		/* state 327 */
yycrank+-13944,	yysvec+9,	yyvstop+575,		/* state 328 */
yycrank+-14014,	yysvec+9,	yyvstop+577,		/* state 329 */
yycrank+-14054,	yysvec+9,	yyvstop+579,		/* state 330 */
yycrank+-14124,	yysvec+9,	yyvstop+581,		/* state 331 */
yycrank+-14164,	yysvec+9,	yyvstop+584,		/* state 332 */
yycrank+-14232,	yysvec+9,	yyvstop+586,		/* state 333 */
yycrank+-14274,	yysvec+9,	yyvstop+589,		/* state 334 */
yycrank+-14342,	yysvec+9,	yyvstop+592,		/* state 335 */
yycrank+-14384,	yysvec+9,	yyvstop+594,		/* state 336 */
yycrank+-14452,	yysvec+9,	yyvstop+596,		/* state 337 */
yycrank+-14493,	yysvec+9,	yyvstop+599,		/* state 338 */
yycrank+-14564,	yysvec+9,	yyvstop+601,		/* state 339 */
yycrank+120,	0,		0,			/* state 340 */
yycrank+121,	0,		0,			/* state 341 */
yycrank+109,	0,		0,			/* state 342 */
yycrank+110,	0,		0,			/* state 343 */
yycrank+-14604,	yysvec+67,	yyvstop+603,		/* state 344 */
yycrank+0,	0,		yyvstop+605,		/* state 345 */
yycrank+-14674,	yysvec+67,	yyvstop+607,		/* state 346 */
yycrank+-14714,	yysvec+67,	yyvstop+609,		/* state 347 */
yycrank+-14782,	yysvec+67,	yyvstop+611,		/* state 348 */
yycrank+-14824,	yysvec+67,	yyvstop+613,		/* state 349 */
yycrank+-14910,	yysvec+67,	yyvstop+615,		/* state 350 */
yycrank+-14952,	yysvec+67,	yyvstop+617,		/* state 351 */
yycrank+-15020,	yysvec+67,	yyvstop+620,		/* state 352 */
yycrank+-15060,	yysvec+67,	yyvstop+622,		/* state 353 */
yycrank+-15130,	yysvec+67,	yyvstop+625,		/* state 354 */
yycrank+-15170,	yysvec+67,	yyvstop+628,		/* state 355 */
yycrank+-15240,	yysvec+67,	yyvstop+630,		/* state 356 */
yycrank+-15280,	yysvec+67,	yyvstop+632,		/* state 357 */
yycrank+-15349,	yysvec+67,	yyvstop+635,		/* state 358 */
yycrank+-15389,	yysvec+67,	yyvstop+637,		/* state 359 */
yycrank+-15457,	yysvec+38,	yyvstop+639,		/* state 360 */
yycrank+-15575,	yysvec+9,	yyvstop+641,		/* state 361 */
yycrank+-15615,	yysvec+9,	yyvstop+643,		/* state 362 */
yycrank+-15684,	yysvec+9,	yyvstop+645,		/* state 363 */
yycrank+-15724,	yysvec+9,	yyvstop+647,		/* state 364 */
yycrank+-15792,	yysvec+9,	yyvstop+650,		/* state 365 */
yycrank+-15832,	yysvec+9,	yyvstop+652,		/* state 366 */
yycrank+-15900,	yysvec+9,	yyvstop+654,		/* state 367 */
yycrank+-15940,	yysvec+9,	yyvstop+657,		/* state 368 */
yycrank+-16008,	yysvec+9,	yyvstop+659,		/* state 369 */
yycrank+-16048,	yysvec+9,	yyvstop+661,		/* state 370 */
yycrank+134,	0,		0,			/* state 371 */
yycrank+120,	0,		0,			/* state 372 */
yycrank+0,	0,		yyvstop+664,		/* state 373 */
yycrank+138,	0,		0,			/* state 374 */
yycrank+-16116,	yysvec+81,	yyvstop+666,		/* state 375 */
yycrank+-16234,	yysvec+67,	yyvstop+668,		/* state 376 */
yycrank+-16274,	yysvec+67,	yyvstop+670,		/* state 377 */
yycrank+-16343,	yysvec+67,	yyvstop+672,		/* state 378 */
yycrank+-16383,	yysvec+67,	yyvstop+674,		/* state 379 */
yycrank+-16451,	yysvec+67,	yyvstop+677,		/* state 380 */
yycrank+-16491,	yysvec+67,	yyvstop+679,		/* state 381 */
yycrank+-16559,	yysvec+67,	yyvstop+681,		/* state 382 */
yycrank+-16599,	yysvec+67,	yyvstop+684,		/* state 383 */
yycrank+-16667,	yysvec+67,	yyvstop+686,		/* state 384 */
yycrank+-16707,	yysvec+67,	yyvstop+688,		/* state 385 */
yycrank+-16775,	yysvec+9,	yyvstop+691,		/* state 386 */
yycrank+-16815,	yysvec+9,	yyvstop+693,		/* state 387 */
yycrank+-16883,	yysvec+9,	yyvstop+696,		/* state 388 */
yycrank+-16923,	yysvec+9,	yyvstop+698,		/* state 389 */
yycrank+-16991,	yysvec+9,	yyvstop+700,		/* state 390 */
yycrank+-17032,	yysvec+9,	yyvstop+702,		/* state 391 */
yycrank+-17102,	yysvec+9,	yyvstop+704,		/* state 392 */
yycrank+-17142,	yysvec+9,	yyvstop+707,		/* state 393 */
yycrank+223,	0,		0,			/* state 394 */
yycrank+120,	0,		0,			/* state 395 */
yycrank+129,	0,		0,			/* state 396 */
yycrank+-17212,	yysvec+67,	yyvstop+709,		/* state 397 */
yycrank+-17252,	yysvec+67,	yyvstop+711,		/* state 398 */
yycrank+-17320,	yysvec+67,	yyvstop+714,		/* state 399 */
yycrank+-17360,	yysvec+67,	yyvstop+716,		/* state 400 */
yycrank+-17428,	yysvec+67,	yyvstop+718,		/* state 401 */
yycrank+-17469,	yysvec+67,	yyvstop+720,		/* state 402 */
yycrank+-17538,	yysvec+67,	yyvstop+722,		/* state 403 */
yycrank+-17578,	yysvec+67,	yyvstop+725,		/* state 404 */
yycrank+-17649,	yysvec+9,	yyvstop+727,		/* state 405 */
yycrank+-17689,	yysvec+9,	yyvstop+729,		/* state 406 */
yycrank+-17757,	yysvec+9,	yyvstop+731,		/* state 407 */
yycrank+-17798,	yysvec+9,	yyvstop+733,		/* state 408 */
yycrank+-17866,	yysvec+9,	yyvstop+735,		/* state 409 */
yycrank+-17906,	yysvec+9,	yyvstop+738,		/* state 410 */
yycrank+-17974,	yysvec+9,	yyvstop+741,		/* state 411 */
yycrank+-18014,	yysvec+9,	yyvstop+744,		/* state 412 */
yycrank+-18082,	yysvec+9,	yyvstop+747,		/* state 413 */
yycrank+172,	0,		0,			/* state 414 */
yycrank+176,	0,		0,			/* state 415 */
yycrank+145,	0,		0,			/* state 416 */
yycrank+135,	0,		0,			/* state 417 */
yycrank+0,	0,		yyvstop+750,		/* state 418 */
yycrank+0,	0,		yyvstop+752,		/* state 419 */
yycrank+-18122,	yysvec+67,	yyvstop+754,		/* state 420 */
yycrank+-18190,	yysvec+67,	yyvstop+756,		/* state 421 */
yycrank+-18230,	yysvec+67,	yyvstop+758,		/* state 422 */
yycrank+-18298,	yysvec+67,	yyvstop+760,		/* state 423 */
yycrank+-18338,	yysvec+67,	yyvstop+762,		/* state 424 */
yycrank+-18406,	yysvec+67,	yyvstop+765,		/* state 425 */
yycrank+-18446,	yysvec+67,	yyvstop+768,		/* state 426 */
yycrank+-18514,	yysvec+67,	yyvstop+771,		/* state 427 */
yycrank+-18554,	yysvec+67,	yyvstop+774,		/* state 428 */
yycrank+-18622,	yysvec+9,	yyvstop+777,		/* state 429 */
yycrank+-18662,	yysvec+9,	yyvstop+779,		/* state 430 */
yycrank+-18730,	yysvec+9,	yyvstop+781,		/* state 431 */
yycrank+-18770,	yysvec+9,	yyvstop+783,		/* state 432 */
yycrank+165,	0,		0,			/* state 433 */
yycrank+166,	0,		0,			/* state 434 */
yycrank+134,	0,		0,			/* state 435 */
yycrank+159,	0,		0,			/* state 436 */
yycrank+-18838,	yysvec+67,	yyvstop+785,		/* state 437 */
yycrank+-18878,	yysvec+67,	yyvstop+787,		/* state 438 */
yycrank+-18946,	yysvec+67,	yyvstop+789,		/* state 439 */
yycrank+-18986,	yysvec+67,	yyvstop+791,		/* state 440 */
yycrank+-19054,	yysvec+38,	yyvstop+793,		/* state 441 */
yycrank+-19172,	yysvec+38,	yyvstop+795,		/* state 442 */
yycrank+-19290,	yysvec+9,	yyvstop+797,		/* state 443 */
yycrank+-19330,	yysvec+9,	yyvstop+799,		/* state 444 */
yycrank+162,	0,		0,			/* state 445 */
yycrank+163,	0,		0,			/* state 446 */
yycrank+148,	0,		0,			/* state 447 */
yycrank+155,	0,		0,			/* state 448 */
yycrank+-19399,	yysvec+81,	yyvstop+801,		/* state 449 */
yycrank+-19517,	yysvec+81,	yyvstop+803,		/* state 450 */
yycrank+-19635,	yysvec+67,	yyvstop+805,		/* state 451 */
yycrank+-19675,	yysvec+67,	yyvstop+807,		/* state 452 */
yycrank+-19745,	yysvec+9,	yyvstop+809,		/* state 453 */
yycrank+-19785,	yysvec+9,	yyvstop+811,		/* state 454 */
yycrank+-19856,	yysvec+9,	yyvstop+813,		/* state 455 */
yycrank+-19896,	yysvec+9,	yyvstop+815,		/* state 456 */
yycrank+150,	0,		0,			/* state 457 */
yycrank+156,	0,		0,			/* state 458 */
yycrank+176,	0,		0,			/* state 459 */
yycrank+239,	0,		0,			/* state 460 */
yycrank+-19964,	yysvec+67,	yyvstop+817,		/* state 461 */
yycrank+-20004,	yysvec+67,	yyvstop+819,		/* state 462 */
yycrank+-20075,	yysvec+67,	yyvstop+821,		/* state 463 */
yycrank+-20115,	yysvec+67,	yyvstop+823,		/* state 464 */
yycrank+-20183,	yysvec+9,	yyvstop+825,		/* state 465 */
yycrank+-20223,	yysvec+9,	yyvstop+827,		/* state 466 */
yycrank+-20310,	yysvec+9,	yyvstop+829,		/* state 467 */
yycrank+0,	0,		yyvstop+831,		/* state 468 */
yycrank+169,	0,		0,			/* state 469 */
yycrank+170,	0,		0,			/* state 470 */
yycrank+174,	0,		0,			/* state 471 */
yycrank+-20350,	yysvec+67,	yyvstop+833,		/* state 472 */
yycrank+-20436,	yysvec+67,	yyvstop+835,		/* state 473 */
yycrank+-20476,	yysvec+67,	yyvstop+837,		/* state 474 */
yycrank+-20563,	yysvec+9,	yyvstop+839,		/* state 475 */
yycrank+-20603,	yysvec+9,	yyvstop+841,		/* state 476 */
yycrank+-20673,	yysvec+9,	yyvstop+843,		/* state 477 */
yycrank+184,	0,		0,			/* state 478 */
yycrank+185,	0,		0,			/* state 479 */
yycrank+178,	0,		0,			/* state 480 */
yycrank+-20713,	yysvec+67,	yyvstop+845,		/* state 481 */
yycrank+-20782,	yysvec+67,	yyvstop+847,		/* state 482 */
yycrank+-20822,	yysvec+67,	yyvstop+849,		/* state 483 */
yycrank+-20890,	yysvec+9,	yyvstop+851,		/* state 484 */
yycrank+-20932,	yysvec+9,	yyvstop+853,		/* state 485 */
yycrank+-21002,	yysvec+9,	yyvstop+855,		/* state 486 */
yycrank+194,	0,		0,			/* state 487 */
yycrank+195,	0,		0,			/* state 488 */
yycrank+196,	0,		0,			/* state 489 */
yycrank+-21044,	yysvec+67,	yyvstop+857,		/* state 490 */
yycrank+-21114,	yysvec+67,	yyvstop+859,		/* state 491 */
yycrank+-21156,	yysvec+67,	yyvstop+861,		/* state 492 */
yycrank+-21226,	yysvec+9,	yyvstop+863,		/* state 493 */
yycrank+-21266,	yysvec+9,	yyvstop+865,		/* state 494 */
yycrank+-21334,	yysvec+38,	yyvstop+867,		/* state 495 */
yycrank+256,	0,		0,			/* state 496 */
yycrank+257,	0,		0,			/* state 497 */
yycrank+209,	0,		0,			/* state 498 */
yycrank+-21452,	yysvec+67,	yyvstop+869,		/* state 499 */
yycrank+-21492,	yysvec+67,	yyvstop+871,		/* state 500 */
yycrank+-21560,	yysvec+81,	yyvstop+873,		/* state 501 */
yycrank+0,	0,		yyvstop+875,		/* state 502 */
yycrank+0,	0,		yyvstop+877,		/* state 503 */
yycrank+-21678,	yysvec+9,	yyvstop+879,		/* state 504 */
yycrank+192,	0,		0,			/* state 505 */
yycrank+-21718,	yysvec+67,	yyvstop+881,		/* state 506 */
yycrank+-21789,	yysvec+9,	yyvstop+883,		/* state 507 */
yycrank+192,	0,		0,			/* state 508 */
yycrank+-21829,	yysvec+67,	yyvstop+885,		/* state 509 */
yycrank+-21916,	yysvec+9,	yyvstop+887,		/* state 510 */
yycrank+203,	0,		0,			/* state 511 */
yycrank+-21956,	yysvec+67,	yyvstop+889,		/* state 512 */
yycrank+-22026,	yysvec+9,	yyvstop+891,		/* state 513 */
yycrank+211,	0,		0,			/* state 514 */
yycrank+-22068,	yysvec+67,	yyvstop+893,		/* state 515 */
yycrank+-22138,	yysvec+9,	yyvstop+895,		/* state 516 */
yycrank+268,	0,		0,			/* state 517 */
yycrank+-22178,	yysvec+67,	yyvstop+897,		/* state 518 */
yycrank+0,	0,		yyvstop+899,		/* state 519 */
0,	0,	0};
struct yywork *yytop = yycrank+22303;
struct yysvf *yybgin = yysvec+1;
char yymatch[] = {
  0,   1,   1,   1,   1,   1,   1,   1, 
  8,   9,  10,   1,   1,   1,   1,   1, 
  1,   1,   1,   1,   1,   1,   1,   1, 
  1,   1,   1,   1,   1,   1,   1,   1, 
 32,  33,  34,  35,   1,  37,   1,  39, 
 34,  34,   1,   1,  34,  45,  34,  34, 
 48,  48,  48,  48,  48,  48,  48,  48, 
 48,  48,  34,   1,  33,  34,  33,   1, 
 35,  65,  65,  65,  65,  65,  65,  65, 
 65,  65,  65,  65,  65,  65,  65,  65, 
 65,  65,  65,  65,  65,  65,  65,  65, 
 65,  65,  65,  45,  92,  45,   1,  95, 
  1,  95,  95,  95,  95,  95,  95,  95, 
 95,  95,  95,  95,  95,  95,  95,  95, 
 95,  95,  95,  95,  95,  95,  95,  95, 
 95,  95,  95,  34,  35,  34,   1, 127, 
0};
char yyextra[] = {
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0,0,0,0,0,0,0,0,
0};
#ifndef lint
static	char ncform_sccsid[] = "@(#)ncform 1.6 88/02/08 SMI"; /* from S5R2 1.2 */
#endif

int yylineno =1;
# define YYU(x) x
# define NLSTATE yyprevious=YYNEWLINE
char yytext[YYLMAX];
struct yysvf *yylstate [YYLMAX], **yylsp, **yyolsp;
char yysbuf[YYLMAX];
char *yysptr = yysbuf;
int *yyfnd;
extern struct yysvf *yyestate;
int yyprevious = YYNEWLINE;
yylook(){
	register struct yysvf *yystate, **lsp;
	register struct yywork *yyt;
	struct yysvf *yyz;
	int yych, yyfirst;
	struct yywork *yyr;
# ifdef LEXDEBUG
	int debug;
# endif
	char *yylastch;
	/* start off machines */
# ifdef LEXDEBUG
	debug = 0;
# endif
	yyfirst=1;
	if (!yymorfg)
		yylastch = yytext;
	else {
		yymorfg=0;
		yylastch = yytext+yyleng;
		}
	for(;;){
		lsp = yylstate;
		yyestate = yystate = yybgin;
		if (yyprevious==YYNEWLINE) yystate++;
		for (;;){
# ifdef LEXDEBUG
			if(debug)fprintf(yyout,"state %d\n",yystate-yysvec-1);
# endif
			yyt = yystate->yystoff;
			if(yyt == yycrank && !yyfirst){  /* may not be any transitions */
				yyz = yystate->yyother;
				if(yyz == 0)break;
				if(yyz->yystoff == yycrank)break;
				}
			*yylastch++ = yych = input();
			yyfirst=0;
		tryagain:
# ifdef LEXDEBUG
			if(debug){
				fprintf(yyout,"char ");
				allprint(yych);
				putchar('\n');
				}
# endif
			yyr = yyt;
			if ( (int)yyt > (int)yycrank){
				yyt = yyr + yych;
				if (yyt <= yytop && yyt->verify+yysvec == yystate){
					if(yyt->advance+yysvec == YYLERR)	/* error transitions */
						{unput(*--yylastch);break;}
					*lsp++ = yystate = yyt->advance+yysvec;
					goto contin;
					}
				}
# ifdef YYOPTIM
			else if((int)yyt < (int)yycrank) {		/* r < yycrank */
				yyt = yyr = yycrank+(yycrank-yyt);
# ifdef LEXDEBUG
				if(debug)fprintf(yyout,"compressed state\n");
# endif
				yyt = yyt + yych;
				if(yyt <= yytop && yyt->verify+yysvec == yystate){
					if(yyt->advance+yysvec == YYLERR)	/* error transitions */
						{unput(*--yylastch);break;}
					*lsp++ = yystate = yyt->advance+yysvec;
					goto contin;
					}
				yyt = yyr + YYU(yymatch[yych]);
# ifdef LEXDEBUG
				if(debug){
					fprintf(yyout,"try fall back character ");
					allprint(YYU(yymatch[yych]));
					putchar('\n');
					}
# endif
				if(yyt <= yytop && yyt->verify+yysvec == yystate){
					if(yyt->advance+yysvec == YYLERR)	/* error transition */
						{unput(*--yylastch);break;}
					*lsp++ = yystate = yyt->advance+yysvec;
					goto contin;
					}
				}
			if ((yystate = yystate->yyother) && (yyt= yystate->yystoff) != yycrank){
# ifdef LEXDEBUG
				if(debug)fprintf(yyout,"fall back to state %d\n",yystate-yysvec-1);
# endif
				goto tryagain;
				}
# endif
			else
				{unput(*--yylastch);break;}
		contin:
# ifdef LEXDEBUG
			if(debug){
				fprintf(yyout,"state %d char ",yystate-yysvec-1);
				allprint(yych);
				putchar('\n');
				}
# endif
			;
			}
# ifdef LEXDEBUG
		if(debug){
			fprintf(yyout,"stopped at %d with ",*(lsp-1)-yysvec-1);
			allprint(yych);
			putchar('\n');
			}
# endif
		while (lsp-- > yylstate){
			*yylastch-- = 0;
			if (*lsp != 0 && (yyfnd= (*lsp)->yystops) && *yyfnd > 0){
				yyolsp = lsp;
				if(yyextra[*yyfnd]){		/* must backup */
					while(yyback((*lsp)->yystops,-*yyfnd) != 1 && lsp > yylstate){
						lsp--;
						unput(*yylastch--);
						}
					}
				yyprevious = YYU(*yylastch);
				yylsp = lsp;
				yyleng = yylastch-yytext+1;
				yytext[yyleng] = 0;
# ifdef LEXDEBUG
				if(debug){
					fprintf(yyout,"\nmatch ");
					sprint(yytext);
					fprintf(yyout," action %d\n",*yyfnd);
					}
# endif
				return(*yyfnd++);
				}
			unput(*yylastch);
			}
		if (yytext[0] == 0  /* && feof(yyin) */)
			{
			yysptr=yysbuf;
			return(0);
			}
		yyprevious = yytext[0] = input();
		if (yyprevious>0)
			output(yyprevious);
		yylastch=yytext;
# ifdef LEXDEBUG
		if(debug)putchar('\n');
# endif
		}
	}
yyback(p, m)
	int *p;
{
if (p==0) return(0);
while (*p)
	{
	if (*p++ == m)
		return(1);
	}
return(0);
}
	/* the following are only used in the lex library */
yyinput(){
	return(input());
	}
yyoutput(c)
  int c; {
	output(c);
	}
yyunput(c)
   int c; {
	unput(c);
	}
