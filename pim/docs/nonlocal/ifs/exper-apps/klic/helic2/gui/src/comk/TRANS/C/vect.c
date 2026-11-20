/*
	(C)1994 Institute for New Generation Computer Technology	
	(Read COPYRIGHT for detailed information.)			
*/

/*  7/20  repair 
**  CBREnv , Env repair  7/21
**  1/10 repair
*/
#include "rgtrans.h"
#include <stdio.h>
#include <string.h>
int answeranswer=0;



kakkoerase(string,newstring)
     char *string;
     char *newstring;
{
  int stnumber;
  *string++;
  stnumber = strlen(string);
  while(stnumber--){
    *newstring = *string ;
    string++;
    newstring++;
  }
}
  


int elementnum(string)
     char *string;
{
  if(string[0] == '['){
    return( elementnum2(string));}
  else{
    return( elementnum1(string));}
}

int elementnum1(string)
     char *string;
{
  int vectorcount2=0,vectnumber=0;
  while(*string != '\0'){
    switch(*string){
    case '{':
      *string++;
      vectorcount2++;
      break;
    case '}':
      *string++;
      vectorcount2--;
      break;
    case '[':
      *string++;
      vectorcount2++;
      break;
    case ']':
      *string++;
      vectorcount2--;
      break;
    case '<':
      *string++;
      vectorcount2++;
      break;
    case '>':
      *string++;
      vectorcount2--;
      break;
    case ',':
      if(vectorcount2 == 1){
	vectnumber++;
	*string++;
      }
      else{
	*string++;
      }
      break;
    default:
      *string++;
      break;
    }
  }
  return(vectnumber+1);
}

int elementnum2(string)
     char *string;
{
  int vectorcount2=0,vectnumber=0;
  while(*string != '\0'){
    switch(*string){
    case '{':
      *string++;
      vectorcount2++;
      break;
    case '}':
      *string++;
      vectorcount2--;
      break;
    case '[':
      *string++;
      vectorcount2++;
      break;
    case ']':
      if(vectorcount2 == 0){
	*string++;
      }
      else{
	*string++;
	vectorcount2--;}
      break;
    case '<':
      *string++;
      vectorcount2++;
      break;
    case '>':
      *string++;
      vectorcount2--;
      break;
    case ',':
      if(vectorcount2 == 1){
	vectnumber++;
	*string++;
      }
      else{
	*string++;
      }
      break;
    default:
      *string++;
      break;
    }
  }
  return(vectnumber+1);
}


int phtermcheck2(string)
     char *string;
{
  char dummy[128];
  switch(string[1]){
  case '{':
    return(2);
    break;
  default:
    vectorE(string,2,3,dummy);
    switch(dummy[0]){
    case '[':
      return(1);
      break;
    default:
      return(2);
      break;
    }
    break;
  }
}

int phtermcheck(string)
     char *string;
{
  switch(string[0]){
  case '[':
    *string++;
    return(phtermcheck2(string));
    break;
  case '{':
    return(phtermcheck2(string));
    break;
  }
}

/*  <A,B> 部分を A,B に分割する。 */

div(news,div1,div2)
     char *news;
     char *div1;
     char *div2;
{
  int breaknumber=0,breakcheck=0;
  while(*news != '\0'){
    switch(breaknumber){
    case 0:
      while(breakcheck != 1){
	switch(*news){
	case '{':
	  breaknumber++;
	  *div1=*news;
	  div1++;
	  news++;
	  break;
	case '}':
	  breaknumber--;
	  *div1=*news;
	  div1++;
	  news++;
	  break;
	case '[':
	  breaknumber++;
	  *div1=*news;
	  div1++;
	  news++;
	  break;
	case ']':
	  breaknumber--;
	  *div1=*news;
	  div1++;
	  news++;
	  break;
	case '<':
	  *news++;
	  break;
	case ',':
	  if(breaknumber == 0){
	    *news++;
	    breakcheck=1;
	    breaknumber++;
	  }
	  else{
	    *div1=*news;
	    div1++;
	    news++;
	  }
	  break;
	default:
	  *div1=*news;
	  div1++;
	  news++;
	  break;
	}
      }
      breakcheck=0;
      break;
    case 1:
      while(breakcheck != 1){
	switch(*news){
	case '>':
	  *news++;
	  breakcheck=1;
	  break;
	default:
	  *div2=*news;
	  div2++;
	  news++;
	  break;
	}
      }
      break;
    }
  }
}


divid(string,div1,div2)
     char *string;
     char *div1;
     char *div2;
{
  char news1[STSIZE],div0[HSTSIZE],ndiv0[HSTSIZE];

  switch(string[0]){
  case '<':
    div(string,div1,div2);
    break;
  default:
    strcpy(div1,string);
    strcpy(div2,"0");
    break;
  }
}


/*  vector から 要素を取り出す。残り要素も返す。  */


toelement(string,stringdummy)
     char *string;
     char *stringdummy;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  while(*string != '\0'){
    switch(vectorcount1){
    case 0:
      while(vectorcount1 != 1){
	switch(*string){
	case ',':
	  if(vectorcount2 == 0){
	    vectorcount1 = 0;
	    string++;
	  }
	  else{
	    string++;
	  }
	  break;
	case '{':
	  vectorcount2++;
	  string++;
	  break;
	case '}':
	  vectorcount2--;
	  string++;
	  break;
	default:
	  string++;
	  break;
	}
      }
      break;
    case 1:
      strcpy(stringdummy,string);
      break;
    }
    return(0);
  }
}

vectorER(string,elementnumber,stringnumber , tstring ,nstring)
     char *string;
     int elementnumber;
     int stringnumber;
     char *tstring;
     char *nstring;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  char stringdummy[STRINGSIZE];

  memset(nstring,0,STRINGSIZE);
  memset(stringdummy,0,STRINGSIZE);
  while(vectorEnumber != elementnumber +1){
    if(vectorEnumber == elementnumber){
      if(elementnumber == stringnumber - 1){
	switch(elementnumber){
	case 0:
	  strcpy(nstring,"{");
	  strcat(nstring,tstring);
	  strcat(nstring,"}");
	  break;
	default:
	  strcat(nstring,tstring);
	  strcat(nstring,"}");
	  break;
	}
      }
      else{
	switch(elementnumber){
	case 0:
	  strcpy(nstring,"{");
	  strcat(nstring,tstring);
	  strcat(nstring,",");
	  toelement(string,stringdummy);
	  strcat(nstring,stringdummy);
	  break;
	default:
	  strcat(nstring,tstring);
	  toelement(string,stringdummy);
	  strcat(nstring,stringdummy);
	  break;
	}
      }
    }
    else{
      switch(vectorEnumber){
      case 0:
	while(vectorcount1 != 1){
	  switch(*string){
	  case ',':
	    if(vectorcount2 == 1){
	      vectorcount1 = 1;
	      *nstring = *string;
	      string++;
	      nstring++;
	    }
	    else{
	      *nstring = *string;
	      string++;
	      nstring++;
	    }
	    break;
	  case '{':
	    *nstring = *string;
	    string++;
	    nstring++;
	    vectorcount2++;
	    break;
	  case '}':
	    *nstring=*string;
	    string++;
	    nstring++;
	    vectorcount2--;
	    break;
	  case '<':
	    *nstring = *string;
	    string++;
	    nstring++;
	    vectorcount2++;
	    break;
	  case '>':
	    *nstring = *string;
	    string++;
	    nstring++;
	    vectorcount2--;
	    break;
	  default:
	    *nstring=*string;
	    nstring++;
	    string++;
	    break;
	  }
	}
	vectorcount1=0;
	vectorcount2=0;
	break;
      default:
	while(vectorcount1 != 1){
	  switch(*string){
	  case ',':
	    if(vectorcount2 == 0){
	      vectorcount1 = 1;
	      *nstring=*string;
	      nstring++;
	      string++;
	    }
	    else{
	      *nstring=*string;
	      nstring++;
	      string++;
	    }
	    break;
	  case '{':
	    *nstring=*string;
	    nstring++;
	    string++;
	    vectorcount2++;
	    break;
	  case '}':
	    *nstring=*string;
	    nstring++;
	    string++;
	    vectorcount2--;
	    break;
	  case '<':
	    *nstring = *string;
	    string++;
	    nstring++;
	    vectorcount2++;
	    break;
	  case '>':
	    *nstring = *string;
	    string++;
	    nstring++;
	    vectorcount2--;
	    break;
	  default:
	    *nstring=*string;
	    nstring++;
	    string++;
	    break;
	  }
	}
	break;
	
      }
    }
    vectorEnumber++;
    
  }
}   
      
  

/*  vector から 要素を取り出す。  */

vectorE1(string,nstring)
     char *string;
     char *nstring;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  *string++;   
  vectorE2(string,nstring);
}


vectorE2(string,nstring)
     char *string;
     char *nstring;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  while(vectorcount1 != 1){
    switch(*string){
    case ',':
      if(vectorcount2 == 0){
	vectorcount1 = 1;
      }
      else{
	*nstring = *string;
	nstring++;
	string++;
      }
      break;
    case '{':
      *nstring = *string;
      nstring++;
      string++;
      vectorcount2++;
      break;
    case '}':
      *nstring = *string;
      nstring++;
      string++;
      vectorcount2--;
      if(vectorcount2 == 0){
	return(1);
      }
      break;
    case '[':
      *nstring = *string;
      nstring++;
      string++;
      vectorcount2++;
      break;
    case ']':
      *nstring = *string;
      nstring++;
      string++;
      if(vectorcount2 == 0){
      }
      else{
	vectorcount2--;}
      break;
    case '<':
      *nstring = *string;
      string++;
      nstring++;
      vectorcount2++;
      break;
    case '>':
      *nstring = *string;
      string++;
      nstring++;
      vectorcount2--;
      break;
    default:
      *nstring = *string;
      nstring++;
      string++;
      break;
    }
  }
  return(0);
}


vectorE3(string,nstring)
     char *string;
     char *nstring;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  while(vectorcount1 != 1){
    switch(*string){
    case ',':
      if(vectorcount2 == 0){
	vectorcount1 = 1;
	return(1);
      }
      else{
	*nstring = *string;
	nstring++;
	string++;
      }
      break;
    case '{':
      *nstring = *string;
      nstring++;
      string++;
      vectorcount2++;
      break;
    case '}':
      if(vectorcount2 == 0){
	vectorcount1 = 1;
	return(1);
      }
      else{
	*nstring = *string;
	nstring++;
	string++;
	vectorcount2--;
      }
      break;
    case '[':
      *nstring = *string;
      nstring++;
      string++;
      vectorcount2++;
      break;
    case ']':
      if(vectorcount2 == 0){
	return(1);
      }
      else{
	*nstring = *string;
	nstring++;
	string++;
	vectorcount2--;
      }
      break;
    case '<':
      *nstring = *string;
      string++;
      nstring++;
      vectorcount2++;
      break;
    case '>':
      *nstring = *string;
      string++;
      nstring++;
      vectorcount2--;
      break;
    default:
      *nstring = *string;
      nstring++;
      string++;
      break;
    }
  }
  return(0);
}


vectorE(string,elementnumber,stringnumber ,nstring)
     char *string;
     int elementnumber;
     int stringnumber;
     char *nstring;
{
  int vectorEnumber=0,vectorcount1=0,vectorcount2=0;
  char stringdummy[STSIZE];
  memset(nstring,0,STSIZE);
  while(vectorEnumber != elementnumber +1){
    if(vectorEnumber == elementnumber){
      if (elementnumber == stringnumber-1){
	vectorE3(string,nstring);
	return(0);
      }
      else{
	switch(elementnumber){
	case 0:
	  vectorE1(string,nstring);
	  return(0);
	  break;
	default:
	  vectorE2(string,nstring);
	  return(0);
	  break;
	}
      }
    }
    else{
      switch(vectorEnumber){
      case 0:
	while(vectorcount1 != 1){
	  switch(*string){
	  case ',':
	    if(vectorcount2 == 1){
	      vectorcount1 = 1;
	      *string++;
	    }
	    else{
	      *string++;
	    }
	    break;
	  case '{':
	    *string++;
	    vectorcount2++;
	    break;
	  case '}':
	    *string++;
	    vectorcount2--;
	    break;
	  case '[':
	    *string++;
	    vectorcount2++;
	    break;
	  case ']':
	    *string++;
	    vectorcount2--;
	    break;
	  case '<':
	    *string++;
	    vectorcount2++;
	    break;
	  case '>':
	    *string++;
	    vectorcount2--;
	    break;
	  default:
	    *string++;
	    break;
	  }
	}
	vectorcount1=0;
	vectorcount2=0;
	vectorEnumber++;
	break;
      default:
	while(vectorcount1 != 1){
	  switch(*string){
	  case ',':
	    if(vectorcount2 == 0){
	      *string++;
	      vectorcount1 = 1;
	    }
	    else{
	      *string++;
	    }
	    break;
	  case '{':
	    *string++;
	    vectorcount2++;
	    break;
	  case '}':
	    *string++;
	    vectorcount2--;
	    break;
	  case '[':
	    *string++;
	    vectorcount2++;
	    break;
	  case ']':
	    *string++;
	    vectorcount2--;
	    break;
	  case '<':
	    *string++;
	    vectorcount2++;
	    break;
	  case '>':
	    *string++;
	    vectorcount2--;
	    break;
	  default:
	    *string++;
	    break;
	  }
	}
	vectorcount1=0;
	vectorcount2=0;
	vectorEnumber++;
	break;

      }
    }
       
  }
}
	    

vectorcheck(string)
     char *string;
{
  int kcount=0;
  while(*string != '\0'){
    switch(*string){
    case '{':
      kcount++;
      string++;
      break;
    default:
      string++;
      break;
    }
  }
  switch(kcount){
  case 1:
    answeranswer = 0;
    break;
  case 0:
    answeranswer = 1;
    break;
  default:
    answeranswer = 2;
    break;
  }
}


predtake2(string,nstring)
     char *string;
     char *nstring;
{


  char div1[STSIZE],div2[STSIZE],dummy[128];
  memset(div1,0,STSIZE);
  memset(div2,0,STSIZE);
  divid(string,div1,div2);
  AppendCNet(&ctable,div1);
  AppendNet2(&vtable,div2,nstring);
/*
  printf("string %s\n",string);
  printf("div1 %s\n",div1);
  printf("div2 %s\n",div2);
  printf("nstring %s\n",nstring);
*/

/* oosaki modify 850825*/
/*
  char div1[STSIZE],div2[STSIZE],dummy[128];
  memset(div1,0,STSIZE);
  memset(div2,0,STSIZE);
  divid(string,div1,div2);

  if(strcmp(div1,div2)==0){
    strcpy(nstring,div1);
  }
  else {
    AppendCNet(&ctable,div1);
    AppendNet2(&vtable,div2,nstring);    
  }
  printf("string %s\n",string);
  printf("div1 %s(%d)\n",div1,strlen(div1));
  printf("div2 %s(%d)\n",div2,strlen(div2));
  printf("nstring %s\n",nstring);
*/
}

predtake3sub(elementnumberstring,nstring)
     char *elementnumberstring;
     char *nstring;
{
  char nelementnumberstring[STSIZE];
  memset(nelementnumberstring,0,STSIZE);
  memset(nstring,0,STSIZE);
  switch(answeranswer){
  case 1:
    strcat(nstring,elementnumberstring);
    break;
  default:
    predtake(elementnumberstring,nelementnumberstring);
    strcat(nstring,nelementnumberstring);
    break;
  }
}

predtake3(elementnumberstring,nstring)
     char *elementnumberstring;
     char *nstring;
{
  switch(*elementnumberstring){
  case '[':
/*    elementnumberstring++;    */
    predtake3sub(elementnumberstring,nstring);
    break;
  default:
    predtake3sub(elementnumberstring,nstring);
    break;
  }
}



predtakeSub(string,stringnumber,nstring)
     char *string;
     int stringnumber;
     char *nstring;
{
  int elementnumber=0;
  char elementnumberstring[STSIZE];
  char nnstring1[STSIZE];
  char nnstring2[STSIZE];
  
  memset(elementnumberstring,0,STSIZE);
  memset(nnstring1,0,STSIZE);
  memset(nnstring2,0,STSIZE);
  for(elementnumber=0 ; elementnumber < stringnumber ;elementnumber++){
    switch(stringnumber){
    case 1:
      strcat(nstring,string);
      break;
    default:
      if(elementnumber == stringnumber-1){
	vectorE(string,elementnumber,stringnumber,elementnumberstring);
	if(strcmp(elementnumberstring,"[]") == 0){
	  strcat(nstring,"[]}");
	}
	else{
	  switch(elementnumberstring[0]){
	  case '[':
/*	    strcpy(nnstring1,"[");   */
	    vectorcheck(elementnumberstring);
	    predtake3(elementnumberstring,nnstring2);
	    if(nnstring2[0] == '['){
	      strcat(nnstring1,nnstring2);}
	    else{
	      strcpy(nnstring1,"[");
	      strcat(nnstring1,nnstring2);
	      strcat(nnstring1,"]");  
	    }
/*	    strcat(nnstring1,"}");    */
	    strcat(nstring,nnstring1);
	    memset(nnstring1,0,STSIZE);
	    memset(nnstring2,0,STSIZE);
	    break;
	  default:
	    vectorcheck(elementnumberstring);
	    predtake3(elementnumberstring,nnstring1);
	    strcat(nstring,nnstring1);
	    if(string[0] == '['){
	    }
	    else{
	      strcat(nstring,"}");}
	    memset(nnstring1,0,STSIZE);
	    break;
	  }
	}
      }
      else {
	switch(elementnumber){
	case 0:
	  vectorE(string,elementnumber,stringnumber,elementnumberstring);
	  if(string[0] == '{'){ 
	    strcpy(nnstring1,"{"); }
	  if(strcmp(elementnumberstring,"[]") == 0){
	    strcat(nnstring1,"[],");
	    strcpy(nstring,nnstring1);
	  }
	  else{
	    vectorcheck(elementnumberstring);
	    predtake3(elementnumberstring,nnstring2);
	    strcat(nnstring1,nnstring2);
	    strcpy(nstring,nnstring1);
	    memset(nnstring1,0,STSIZE);
	    memset(nnstring2,0,STSIZE);
	    strcat(nstring,",");
	  }
	  break;
	default:
	  vectorE(string,elementnumber,stringnumber,elementnumberstring);
	  if(strcmp(elementnumberstring,"[]") == 0){
	    strcat(nstring,"[],");
	  }
	  else{
	    switch(elementnumberstring[0]){
	    case '[':
/*	      strcpy(nnstring1,"[");         */
	      vectorcheck(elementnumberstring);
	      predtake3(elementnumberstring,nnstring2);
	      if(nnstring2[0] == '['){
		strcat(nnstring1,nnstring2);}
	      else{
		strcpy(nnstring1,"[");
		strcat(nnstring1,nnstring2);
		strcat(nnstring1,"]");}        
	      strcat(nnstring1,",");
	      strcat(nstring,nnstring1);
	      memset(nnstring1,0,STSIZE);
	      memset(nnstring2,0,STSIZE);
	      break;
	    default:
	      vectorcheck(elementnumberstring);
	      predtake3(elementnumberstring,nnstring2);
	      strcat(nstring,nnstring2);
	      strcat(nstring,",");
	      memset(nnstring2,0,STSIZE);
	      break;
	    }
	  }
	  break;
	}
      }
      break;
    }
  }
}
    
  

predtake(string,nstring)
     char *string;
     char *nstring;
{
  int stringnumber=0;
  char elementnumberstring[STSIZE];
  char nnstring[STSIZE];
  char newstring[STSIZE];
  
  memset(newstring,0,STSIZE);
  memset(nnstring,0,STSIZE);
  memset(elementnumberstring,0,STSIZE);
  if(string[0] == '<'){
    predtake2(string,elementnumberstring);
    strcat(nstring,elementnumberstring);
  }
  else{
    stringnumber = elementnum(string);
    switch(stringnumber){
    case 3:
      switch(phtermcheck(string)){
      case 2:
	predtakeSub(string,stringnumber,nstring);
	break;
      case 1:
	predtake2(string,elementnumberstring);
	strcat(nstring,elementnumberstring);
	break;
      }
      break;
    case 1:
      if(string[0] == '['){
	strcpy(nstring,"[");
	kakkoerase(string,newstring);
	predtake(newstring,nnstring);
	strcat(nstring,nnstring);
	strcat(nstring,"]");}
      else{
	predtakeSub(string,stringnumber,nstring);}
      break;
    default:
      predtakeSub(string,stringnumber,nstring);
      break;
    }
  }
}

