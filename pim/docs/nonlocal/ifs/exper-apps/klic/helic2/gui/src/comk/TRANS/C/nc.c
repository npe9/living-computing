/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/**
**
** USAGE :   trans [-g|-r]  InFileName  OutFileName
**
** Option : 
** -g ;    goal translator
** -r ;    rule translator
**    ;    rule translator 
**   
**    7/20  repair 
**    malloc use   version                        */
#include "rgtrans.h"
#include <locale.h>
/*#include <widec.h>*/
#include <stdio.h>
#include <string.h>
#include <stdlib.h>


int kaisuucount1=0;
int kaisuucount2=0;
int hcount1=0;
int bodycount=0;
int goalstate=0;

extern int kaigyounumber;
extern int errorInfo;
extern char *newstring3;
extern FILE *yyin;
extern FILE *priout;

/*  1 つのブロックを確保する。 */


val *AllocNet()
{
  val *p;
  
  p = (val *)calloc(1,sizeof(val));
  if(p == NULL){
    fprintf(stderr,"%s\n","!trans-Memory faise");
    errorInfo = 10;
    exit(1);
  }
  else{
    return(p);
  }
}



ht *AllochNet()
{
  ht *p;
  
  p = (ht *)malloc(sizeof(ht));
  if(p == NULL){
    fprintf(stderr,"%s\n","!trans-Memory faise");
    errorInfo =10;
    exit(1);
  }
  else{
    return(p);
  }
}

st *AllocsNet()
{
  st *p;
  
  p = (st *)malloc(sizeof(st));
  if(p == NULL){
    fprintf(stderr,"%s\n","!trans-Memory faise");
    errorInfo = 10;
    exit(1);
  }
  else{
    return(p);
  }
}

cen *AlloccNet()
{
  cen *p;
  
  p = (cen *)calloc(1,sizeof(cen));
  if(p == NULL){
    fprintf(stderr,"%s\n","!trans-Memory faise");
    errorInfo = 10;
    exit(1);
  }
  else{
    return(p);
  }
}


/*  初期化  */

InitNet(control)
     cont_val *control;
{
  control->top = control->bottom = AllocNet();
 
}


InithNet(control)
     cont_ht *control;
{
  control->htop = control->hbottom = AllochNet();
 
}

InitsNet(control)
     cont_st *control;
{
  control->stop = control->sbottom = AllocsNet();
 
}

InitcNet(control)
     cont_cen *control;
{
  control->ctop = control->cbottom = AlloccNet();
 
}



InsertNet(control ,count,name1,name2)
     cont_val *control ;
     int count;
     char *name1;
     char *name2;
{
  val *ptr;
  
  ptr = control->top;
  control->top = AllocNet();
  control->top->number=count;
  strcpy(control->top->name1,name1);
  strcpy(control->top->name2,name2);
  control->top->next = ptr;
}


/* 要素の探索 */

val *searchNet(control,name)
     cont_val *control;
     char *name;
{
  val *ptr;
  
  ptr = control->top;
  while(ptr != control->bottom){
    if(strcmp(ptr->name1,name) == 0)
      return(ptr);
    ptr=ptr->next;
  }
  return(NULL);
}

ht *searchHNet(control,name)
     cont_ht *control;
     char *name;
{
  ht *ptr;
  
  ptr = control->htop;
  while(ptr != control->hbottom){
    if(strcmp(ptr->hname1,name) == 0)
      return(ptr);
    ptr=ptr->hnext;
  }
  return(NULL);
}

st *searchSNet(control,name)
     cont_st *control;
     char *name;
{
  st *ptr;
  
  ptr = control->stop;
  while(ptr != control->sbottom){
    if(strcmp(ptr->sname1,name) == 0)
      return(ptr);
    ptr=ptr->snext;
  }
  return(NULL);
}

cen *searchCNet(control,name)
     cont_cen *control;
     char *name;
{
  cen *ptr;
  
  ptr = control->ctop;
  while(ptr != control->cbottom){
    if(strcmp(ptr->cname1,name) == 0)
      return(ptr);
    ptr=ptr->cnext;
  }
  return(NULL);
}


stabletake(control ,string1)
     cont_st *control ;
     char *string1;
/*     char *newstring3;  */
{
  if(searchSNet(control,string1) == NULL){
    fprintf(stderr,"%s","!trans-Illegal htermID error");
/*    fprintf(stderr,"%s",":line ");
    fprintf(stderr,"%d",kaigyounumber+1); */
    fprintf(stderr,"%s"," '");
    fprintf(stderr,"%s",string1);
    fprintf(stderr,"%s\n","'");
    errorInfo = 10;
  }
  else{
    newstring3 = malloc(strlen(searchSNet(control,string1)->sname2)+1);
    strcpy(newstring3,searchSNet(control,string1)->sname2);

  }
   
}

AppendNet0(control,string1,string3)
     cont_val *control;
     char *string1;
     char *string3;
{
  val *ptr;

  if(searchNet(control,string1) == NULL){
    fprintf(stderr,"s\n","error happend");
  }
  else {
    sprintf(string3,"%d",searchNet(control,string1)->number);
  }
}



AppendNet1(control,string1,string2,string3)
     cont_val *control;
     char *string1;
     char *string2;
     char *string3;
{
  val *ptr,*ptr1;
  
  switch(bodycount){
  case 1:
    if(searchNet(control,string1) == NULL){
      kaisuucount1++;
      ptr = control->bottom;
      control->bottom = AllocNet();
      ptr->number=kaisuucount1;
      strcpy(ptr->name1,string1);
      strcpy(ptr->name2,string2);
      strcpy(ptr->name3,"#");
      ptr->next = control->bottom;
      sprintf(string3,"%d",kaisuucount1);
    }
    else {
      ptr1 = searchNet(control,string1);
      if(strcmp(ptr1->name3,"$") == 0){
	strcpy(ptr1->name2,string2);
	strcpy(ptr1->name3,"#");
	sprintf(string3,"%d",ptr1->number);
      }
      else {

/* 960408 oosaki modify & add */
/*   onaji hensuu wo P-Term ni tuketatokini error ni naru */

/*	if(strcmp(string2,"0") == 0){
	  sprintf(string3,"%d",ptr1->number);	
	}
	else{
	  fprintf(stderr,"%s","!trans-Illegal variable difinition");
	  fprintf(stderr,"%s"," '");
	  fprintf(stderr,"%s",string1);
	  fprintf(stderr,"%s\n","'");
	  strcpy(ptr1->name2,string2);
	  strcpy(ptr1->name3,"#");
	  sprintf(string3,"%d",ptr1->number);
	  errorInfo = 10;
	}
*/

	  sprintf(string3,"%d",ptr1->number);	

      }
    }
    break;
  case 0:
    if(searchNet(control,string1) == NULL){
      kaisuucount1++;
      ptr = control->bottom;
      control->bottom = AllocNet();
      ptr->number=kaisuucount1;
      strcpy(ptr->name1,string1);
      strcpy(ptr->name2,string2);
      strcpy(ptr->name3,"$");
      ptr->next = control->bottom;
      sprintf(string3,"%d",kaisuucount1);
    }
    else {
      ptr1 = searchNet(control,string1);
      sprintf(string3,"%d",ptr1->number);
    }
    break;
  }
}

AppendNet2(control,name1,name2)
     cont_val *control;
     char *name1;
     char *name2;
{
  val *ptr;

  kaisuucount1++;
  ptr = control->bottom;
  control->bottom = AllocNet();
  strcpy(ptr->name1,name1);
  strcpy(ptr->name2,name1);
  ptr->next = control->bottom;
  sprintf(name2,"%d",kaisuucount1);
}



AppendhNet1(control,string1,string2,string3)
     cont_ht *control;
     char *string1;
     char *string2;
     char *string3;
{
  char nstring[512];
  ht *ptr,*ptr1;
  
  switch(bodycount){
  case 1:
    if(searchHNet(control,string1) == NULL){
      if(strcmp(string1,string2) == 0){
	strcpy(nstring,"{");
	sprintf(string3,"%d",ptr1->hnumber);
	strcat(nstring,string3);
	strcat(nstring,"}");
	strcpy(string3,nstring);
	fprintf(stderr,"%s","!trans-Illegal htermID difinition");
/*	fprintf(stderr,"%s",":line ");
	fprintf(stderr,"%d",kaigyounumber+1); */
	fprintf(stderr,"%s"," '");
	fprintf(stderr,"%s",string1);
	fprintf(stderr,"%s\n","'");
	errorInfo = 10;
      }
      hcount1++;
      ptr = control->hbottom;
      control->hbottom = AllochNet();
      ptr->hnumber=hcount1;
      ptr->hname1 = malloc(strlen(string1)+1);
      strcpy(ptr->hname1,string1);
      ptr->hname2 = malloc(strlen(string2)+1);
      strcpy(ptr->hname2,string2);
      ptr->hname3 = malloc(8);
      strcpy(ptr->hname3,"#");
      ptr->hnext = control->hbottom;
      strcpy(nstring,"{");
      sprintf(string3,"%d",hcount1);
      strcat(nstring,string3);
      strcat(nstring,"}");
      strcpy(string3,nstring);
    }
    else {
      ptr1 = searchHNet(control,string1);
      if(strcmp(ptr1->hname3,"$") == 0){
	if(strcmp(string1,string2) == 0){
	  strcpy(nstring,"{");
	  sprintf(string3,"%d",ptr1->hnumber);
	  strcat(nstring,string3);
	  strcat(nstring,"}");
	  strcpy(string3,nstring);
	  fprintf(stderr,"%s","!trans-Illegal htermID difinition");
/*	  fprintf(stderr,"%s",":line ");
	  fprintf(stderr,"%d",kaigyounumber+1); */
	  fprintf(stderr,"%s"," '");
	  fprintf(stderr,"%s",string1);
	  fprintf(stderr,"%s\n","'");
	  errorInfo = 10;
	}
	else{
/*	  realloc(ptr1->hname2,strlen(string2)+1); */
	  ptr1->hname2 = malloc(strlen(string2)+1);
	  strcpy(ptr1->hname2,string2);
/*	  realloc(ptr1->hname3,8);    */
	  strcpy(ptr1->hname3,"#");
	  strcpy(nstring,"{");
	  sprintf(string3,"%d",ptr1->hnumber);
	  strcat(nstring,string3);
	  strcat(nstring,"}");
	  strcpy(string3,nstring);
	}
      }
      else {
	if(strcmp(string1,string2) == 0){
	  strcpy(nstring,"{");
	  sprintf(string3,"%d",ptr1->hnumber);
	  strcat(nstring,string3);
	  strcat(nstring,"}");
	  strcpy(string3,nstring);
	}
	else{
	  fprintf(stderr,"%s","!trans-Illegal htermID difinition");
/*	  fprintf(stderr,"%s",":line ");
	  fprintf(stderr,"%d",kaigyounumber+1); */
	  fprintf(stderr,"%s"," '");
	  fprintf(stderr,"%s",string1);
	  fprintf(stderr,"%s\n","'");
/*	  realloc(ptr1->hname2,strlen(string2)+1);  */
	  ptr1->hname2 = malloc(strlen(string2)+1);
	  strcpy(ptr1->hname2,string2);
	  strcpy(ptr1->hname3,"#");
	  strcpy(nstring,"{");
	  sprintf(string3,"%d",ptr1->hnumber);
	  strcat(nstring,string3);
	  strcat(nstring,"}");
	  strcpy(string3,nstring);
	  errorInfo = 10;
	}
      }
    }
    break;
  case 0:
     if(searchHNet(control,string1) == NULL){
       hcount1++;
       ptr = control->hbottom;
       control->hbottom = AllochNet();
       ptr->hnumber=hcount1;
       ptr->hname1 = malloc(strlen(string1)+1);
       strcpy(ptr->hname1,string1);
       ptr->hname2 = malloc(strlen(string2)+1);
       strcpy(ptr->hname2,string2);
       ptr->hname3 = malloc(8);
       strcpy(ptr->hname3,"$");
       ptr->hnext = control->hbottom;
       strcpy(nstring,"{");
       sprintf(string3,"%d",hcount1);
       strcat(nstring,string3);
       strcat(nstring,"}");
       strcpy(string3,nstring);
     }
    else{
	strcpy(nstring,"{");
	sprintf(string3,"%d",searchHNet(control,string1)->hnumber);
	strcat(nstring,string3);
	strcat(nstring,"}");
	strcpy(string3,nstring);
      }
    break;
  }
  
}

AppendsNet1(control,string1,string2)
     cont_st *control;
     char *string1;
     char *string2;
{
  st *ptr;

  if(searchSNet(control,string1) == NULL){
    ptr = control->sbottom;
    control->sbottom = AllocsNet();
    ptr->sname1 = malloc(strlen(string1)+1);
    strcpy(ptr->sname1,string1);
    ptr->sname2 = malloc(strlen(string2)+1);
    strcpy(ptr->sname2,string2);
    ptr->snext = control->sbottom;
  }
  else {
  }
}


charToInt(dum,string,control)
     char *dum;
     char *string;
     cont_ht *control;
{
  sprintf(dum,"%d",searchHNet(control,string)->hnumber);
}


AppendCNet(control,name)
     cont_cen *control;
     char *name;
{
  cen *ptr;

  ptr = control->cbottom;
  control->cbottom = AlloccNet();
  ptr->cname3 = malloc(8);
  strcpy(ptr->cname3,"0");
  ptr->cname1 = malloc(strlen(name)+1);
  strcpy(ptr->cname1,name);
  ptr->cname2 = malloc(strlen(name)+1);
  strcpy(ptr->cname2,name);
  ptr->cnext = control->cbottom;
}


AppendCNet1(control,string1,string2)
     cont_cen *control;
     char *string1;
     char *string2;
{
  cen *ptr,*ptr1;
  
  switch(bodycount){
  case 1:
    if(searchCNet(control,string1) == NULL){
      ptr = control->cbottom;
      control->cbottom = AlloccNet();
      ptr->cname1 = malloc(strlen(string1)+1);
      strcpy(ptr->cname1,string1);
      ptr->cname2 = malloc(strlen(string2)+1);
      strcpy(ptr->cname2,string2);
      ptr->cname3 = malloc(8);
      strcpy(ptr->cname3,"#");
      ptr->cnext = control->cbottom;
    }
    else {
      ptr1 = searchCNet(control,string1);
      if(strcmp(ptr1->cname3,"$") == 0){
	ptr1->cname2 = malloc(strlen(string2)+1);
	strcpy(ptr1->cname2,string2);
	strcpy(ptr1->cname3,"#");
      }
    }
    break;
  case 0:
    if(searchCNet(control,string1) == NULL){
      ptr = control->cbottom;
      control->cbottom = AlloccNet();
      ptr->cname1 = malloc(strlen(string1)+1);
      strcpy(ptr->cname1,string1);
      ptr->cname2 = malloc(strlen(string2)+1);
      strcpy(ptr->cname2,string2);
      ptr->cname3 = malloc(8);
      strcpy(ptr->cname3,"$");
      ptr->cnext = control->cbottom;
    }
    break;
  }
}


/*  先頭ノードの削除  */

DeleteNet(control)
     cont_val *control;
{
  if(control->top != control->bottom){
    val *ptr = control->top->next;
    free(control->top);
    control->top = ptr;
  }
}


DeleteHNet(control)
     cont_ht *control;
{
  if(control->htop != control->hbottom){
    ht *ptr = control->htop->hnext;
    free(control->htop);
    control->htop = ptr;
  }
}

/*  全要素の削除  */

AllDeleteNet(control)
     cont_val *control;
{
  val *ptr;
  
  ptr = control->top;
  while(ptr != control->bottom){
    val *ptr2 = ptr->next;
    free(ptr);
    ptr = ptr2;
  }
  control->top = control->bottom;
}



AllDeleteHNet(control)
     cont_ht *control;
{
  ht *ptr;
  
  ptr = control->htop;
  while(ptr != control->hbottom){
    ht *ptr2 = ptr->hnext;
    free(ptr);
    ptr = ptr2;
  }
  control->htop = control->hbottom;
}


AllDeleteSNet(control)
     cont_st *control;
{
  st *ptr;
  
  ptr = control->stop;
  while(ptr != control->sbottom){
    st *ptr2 = ptr->snext;
    free(ptr);
    ptr = ptr2;
  }
  control->stop = control->sbottom;
}


AllDeleteCNet(control)
     cont_cen *control;
{
  cen *ptr;
  
  ptr = control->ctop;
  while(ptr != control->cbottom){
    cen *ptr2 = ptr->cnext;
    free(ptr);
    ptr = ptr2;
  }
  control->ctop = control->cbottom;
}


TermNet(control)
     cont_val *control;
{
  free(control->top);
  control->top = control->bottom = NULL;
}

TermHNet(control)
     cont_ht *control;
{
  free(control->htop);
  control->htop = control->hbottom = NULL;
}


PrintNet(control)
     cont_ht *control;
{
  ht *ptr;
  
  ptr = control->htop;
  while(ptr != control->hbottom){
    printf("Data0:%d\n",ptr->hnumber);
    printf("Data1:%s\n",ptr->hname1);
    printf("Data2:%s\n",ptr->hname2);
    ptr = ptr->hnext;
  }
}

PrintCNet(control)
     cont_cen *control;
{
  cen *ptr;
  
  ptr = control->ctop;
  while(ptr != control->cbottom){
    printf("CTableData0:%d\n",ptr->cname1);
    printf("CTableData1:%s\n",ptr->cname2);
    printf("CTableData2:%s\n",ptr->cname3);
    ptr = ptr->cnext;
  }
}


main(argc,argv)
     int argc;
     char *argv[];
{
  switch(argc){
  case 4:
    setlocale(LC_ALL,"");
    switch(argv[1][1]){
      case 'g':    /* -g : goal translator */
	goalstate=1;
	break;
      case 'r':    /* -r : rule translator */
	goalstate=0;
	break;
      default:
	fprintf(stderr,"%s","!trans-Illegal option : '");
	fprintf(stderr,"%s",argv[1]);
	fprintf(stderr,"%s\n","'");
	return(2);
	exit(1);
	break;
      }
    if((yyin = fopen(argv[2],"r"))==NULL){
      fprintf(stderr,"%s\n","!trans-File can't open or don't exist");
      return(2);
      exit(1);
    }
    if((priout = fopen(argv[3],"w")) ==NULL){
      fprintf(stderr,"%s\n","!trans-File can't open or mistake pathname");
      return(2);
      exit(1);
    }
    if(goalstate == 1){
      priout = fopen(argv[3],"a");
      fputs("{",priout);
    }
    else {     
      priout = fopen(argv[3],"a");}
    fputs("[",priout);
    InitNet(&vtable);
    InithNet(&htable);
    InitsNet(&stable);
    InitcNet(&ctable);
    yyparse();
    if(errorInfo == 10){
      return(2);
      exit(1);
    }else {
      fputs("]",priout);
      if(goalstate == 1){
	fputs("}.",priout);}
      else{
	fputs(".",priout);}
      fclose(yyin);
      fclose(priout);
      return(0);
    }
    break;
  case 3:          /*  rule translator */
    setlocale(LC_ALL,"");
    if(argv[1][0] == '-'){
      fprintf(stderr,"%s\n","!trans-Illegal argument number");
    }
    else{
      if((yyin = fopen(argv[1],"r"))==NULL){
	fprintf(stderr,"%s\n","!trans-Input File can't open or don't exist");
	return(2);
	exit(1);
      }
      if((priout = fopen(argv[2],"w"))==NULL){
	fprintf(stderr,"%s\n","!trans-Output File can't open or mistake pathname");
	return(2);
	exit(1);
      }
      priout = fopen(argv[2],"a");
      fputs("[",priout);
      InitNet(&vtable);
      InithNet(&htable);
      InitsNet(&stable);
      InitcNet(&ctable);
      yyparse();
      if(errorInfo==10){
	return(2);
	exit(1);
      }else{
	fputs("].",priout);
	fclose(yyin);
	fclose(priout);
	return(0);
      }
    }
    
    break;
  default:
    fprintf(stderr,"%s\n","!trans-Illegal argument number");
    return(2);
    exit(1);
    break;
  }
}


       

   
