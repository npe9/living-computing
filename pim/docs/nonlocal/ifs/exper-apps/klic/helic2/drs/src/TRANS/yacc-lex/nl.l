/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

%{
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
%}
%a 15000
%p 5000
%o 25000
%n 1000
%start RBRRULE CBRRULE GOAL
%%
<INITIAL>"("     { 
          if(goalstate == 1){
          strcat(origstring,"(");
          }
          strcpy(yylval.string11,yytext);
          return(LP);}
<INITIAL>")"     { 
          if(goalstate == 1){
          strcat(origstring,")");
          }
          strcpy(yylval.string11,yytext);
          return(RP);}
<CBRRULE>"("     { strcpy(yylval.string11,yytext);
          return(CBRLP);}
<CBRRULE>")"     { strcpy(yylval.string11,yytext);
          return(CBRRP);}
"{"     { 
          strcpy(yylval.string11,yytext);
          return(TRP);}
"}"     { 
          if(goalstate == 1){
            strcat(origstring,",");
          }
          strcpy(yylval.string11,yytext);
          return(TLP);}
"/"     { 
          if(goalstate == 1){
          strcat(origstring,"/");
          }
          strcpy(yylval.string11,yytext);
          return(DIP);}
":"     { 
          if(goalstate == 1){
          strcat(origstring,":");
          }
          strcpy(yylval.string11,yytext);
          return(OP);}
","     { 
          if(goalstate == 1){
            strcat(origstring,",");
          }
          strcpy(yylval.string11,yytext);
          return(IP);}
<INITIAL>"="     { 
          if(goalstate == 1){
          strcat(origstring,"=");
          }
          strcpy(yylval.string11,yytext);
          return(EP);}
<CBRRULE>"="     { strcpy(yylval.string11,yytext);
          return(CBREP);}
"-"     { 
          if(goalstate == 1){
          strcat(origstring,"-");
          }
          strcpy(yylval.string11,yytext);
          return(MIP);}
"<"     { 
          if(goalstate == 1){
          strcat(origstring,"<");
          }
          strcpy(yylval.string11,yytext);
          return(RGP);}
">"     { 
          if(goalstate == 1){
          strcat(origstring,">");
          }
          strcpy(yylval.string11,yytext);
          return(LGP);}
"["     { 
          if(goalstate == 1){
          strcat(origstring,"[");
          }
          strcpy(yylval.string11,yytext);
          return(KLP);}
"]"     { 
          if(goalstate == 1){
          strcat(origstring,"]");
          }
          strcpy(yylval.string11,yytext);
          return(KRP);}
"|"     { 
          if(goalstate == 1){
          strcat(origstring,"|");
          }
          strcpy(yylval.string11,yytext);
          return(BP);}
"||"    { 
          if(goalstate == 1){
          strcat(origstring,"||");
          }
          strcpy(yylval.string11,yytext);
          return(BBP);}
"+"    { 
          if(goalstate == 1){
          strcat(origstring,"+");
          }
          strcpy(yylval.string11,yytext);
          return(TOP);}
"<-"    { strcpy(yylval.string11,yytext);
          return(MP);}
"=>"    { 
          attributecount++;
          if(goalstate == 1){
          strcat(origstring,"=>");
          }
          strcpy(yylval.string11,yytext);
          return(NP);}
"::"    { strcpy(yylval.string11,yytext);
          return(OPOP);}
"!"     { strcpy(yylval.string11,yytext);
          return(BBB);}
<INITIAL>agent   { 
          if(goalstate == 1){
          strcat(origstring,"agent");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>object  { 
          if(goalstate == 1){
          strcat(origstring,"object");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>a_object  { 
          if(goalstate == 1){
          strcat(origstring,"a_object");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>cause   { 
          if(goalstate == 1){
          strcat(origstring,"cause");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>condition {
          if(goalstate == 1){
          strcat(origstring,"condition");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>purpose {
          if(goalstate == 1){
          strcat(origstring,"purpose");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>place   {
          if(goalstate == 1){
          strcat(origstring,"place");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>source  { 
          if(goalstate == 1){
          strcat(origstring,"source");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>goal    { 
          if(goalstate == 1){
          strcat(origstring,"goal");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>time    { 
          if(goalstate == 1){
          strcat(origstring,"time");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>time_from { 
          if(goalstate == 1){
          strcat(origstring,"time_from");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>time_to   { 
          if(goalstate == 1){
          strcat(origstring,"time_to");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>implement { 
          if(goalstate == 1){
          strcat(origstring,"implement");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>quantity  { 
          if(goalstate == 1){
          strcat(origstring,"quantity");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>number  { 
          if(goalstate == 1){
          strcat(origstring,"number");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>manner  { 
          if(goalstate == 1){
          strcat(origstring,"manner");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<INITIAL>basis  { 
          if(goalstate == 1){
          strcat(origstring,"basis");
          }
          strcpy(yylval.string11,yytext);
          return(KName);}
<CBRRULE>agent   { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>object  { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>a_object  { strcpy(yylval.string11,yytext);
            return(CKName);}
<CBRRULE>cause   { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>condition {strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>purpose {strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>place   {strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>source  { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>goal    { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>time    { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>time_from { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>time_to   { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>implement { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>quantity  { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>number  { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>manner  { strcpy(yylval.string11,yytext);
          return(CKName);}
<CBRRULE>basis  { strcpy(yylval.string11,yytext);
          return(CKName);}
some    { 
          if(goalstate == 1){
          strcat(origstring,"some");
          }
          strcpy(yylval.string11,yytext);
          return(Some);}
not   { strcpy(yylval.string11,yytext);
          return(Not);}
less    { if(goalstate == 1){
          strcat(origstring,"less");
          }
          strcpy(yylval.string11,yytext);
          return(LESS);}
greater { if(goalstate == 1){
          strcat(origstring,"greater");
          }
          strcpy(yylval.string11,yytext);
          return(GREATER);}
equal   { if(goalstate == 1){
          strcat(origstring,"equal");
          }
          strcpy(yylval.string11,yytext);
          return(EQUAL);}
not_equal { if(goalstate == 1){
            strcat(origstring,"not_equal");
            }
            strcpy(yylval.string11,yytext);
            return(NOTEQUAL);}
same    { if(goalstate == 1){
          strcat(origstring,"same");
          }
          strcpy(yylval.string11,yytext);
          return(SAME);}
different { if(goalstate == 1){
            strcat(origstring,"different");
            }
            strcpy(yylval.string11,yytext);
            return(DIFFERENT);}
"&"define_goal"."           { if(goalstate == 1){
                              return(DG);
                              }
                              else{
    fprintf(stderr,"%s\n","!trans-Illegal option : please  '-g' ");
      exit(1);
      }
    }
"&"define_absolute_rule"."  { if(goalstate == 0){
                              return(DAR);
                              }
                              else{
   fprintf(stderr,"%s\n","!trans-Illegal option :  please  '-r' ");      
   exit(1);
      }
    }
"&"define_RBR_rule"."       { return(DRR);}
"&"define_CBR_rule"."       { BEGIN CBRRULE ;
                              return(DCR);}
[ \t]   ;
[ \b]   ;
[\\]    ;
[%][^\b\177\n]+[\n]   { kaigyounumber++;}
<INITIAL>[0-9]+ { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%s",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(Number);}
<INITIAL>[A-Z][a-zA-Z0-9_]*  { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%s",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(Variable);}
<INITIAL>"_"[a-zA-Z0-9_]*  { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
	  return(Variable);}
<INITIAL>"@"[^(){}\-/:,=.\[\]\" \t\n\b\40\\]+     { 
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(HtermMaker);}
<INITIAL>"#"[^(){}\-/:,=.\[\]\" \t\n\b\\]+     { 
          if(goalstate == 1){
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(SHMaker);}
<CBRRULE>"@"[^(){}\-/:,=.\[\]\" \t\n\b\40\\]+   {
                                  strcpy(yylval.string11,yytext);
                                  return(CBRHtermMaker);}
<CBRRULE>"#"[^(){}\-/:,=.\[\]\" \t\n\b\40\\]+   {
                                  strcpy(yylval.string11,yytext);
                                  return(CBRSHMaker);}
<INITIAL>[^@#!()=,{}\'\-|/:<>.\[\]\" \t\n\b\40\\]+  { 
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
<INITIAL>\'[^!()=,{}\/:<>.\"\n\t\b\40\\]+\'  { 
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
<INITIAL>"["[0-9]+".."[0-9]+"]" {
          if(goalstate == 1){
/*
          sprintf(dummy,"%ws",yytext);
          strcat(origstring,dummy);
*/
          strcat(origstring,yytext);
          }
          strcpy(yylval.string11,yytext);
          return(NumberDomain);}
<CBRRULE>[0-9]+ {
          strcpy(yylval.string11,yytext);
          return(CBRNumber);}
<CBRRULE>[A-Z][a-zA-Z0-9_]*  { strcpy(yylval.string11,yytext);
               		     return(CBRVariable);}
<CBRRULE>"_"[a-zA-Z0-9_]*  { strcpy(yylval.string11,yytext);
               		     return(CBRVariable);}
<CBRRULE>[^@#!()=,{}\-|/:<>.\[\]\" \t\n\b\40\\]+  { 
                                   strcpy(yylval.string11,yytext);
                		          return(CBRAtom);}
<CBRRULE>\'[^!()=,{}\/:<>.\"\t\n\b\40\\]+\'  { 
                                   strcpy(yylval.string11,yytext);
                                   return(CBRSAtom);}
<CBRRULE>"["[0-9]+".."[0-9]+"]" {
          strcpy(yylval.string11,yytext);
          return(CBRNumberDomain);}
\.       {return (REnd);}
\"      { return(WK);}
\n      { kaigyounumber++;}
%%


