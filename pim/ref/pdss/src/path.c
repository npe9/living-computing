/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <pwd.h>
#include "pdss.h"
#include "io.h"

extern struct passwd *getpwent();
extern struct passwd *getpwuid();
extern struct passwd *getpwnam();
extern CHAR *getwd();
extern CHAR *getenv();
extern CHAR *mktemp();

CHAR *expand_path_name(name, buffer)
    CHAR  *name, *buffer;
{
    register struct passwd  *pw;
    register CHAR  *p;

    if(*name == '~'){
	name++;
	if(*name == 0 || *name == '/'){
	    if((p = getenv("HOME")) == NULL){
		Error("Can't get home directory.");
		return(NULL);
	    }
	    sprintf(buffer, "%s%s", p, name);
	}else{
	    p = name;
	    while(*p && *p != '/') p++;
	    if(*p){
		*p = 0;
		if((pw = getpwnam(name)) == NULL){
		    Error1F("Unknown user \"%s\".", name);
		    return(NULL);
		}
		*p++ = '/';
		sprintf(buffer, "%s/%s", pw->pw_dir, p);
	    }else{
		if((pw = getpwnam(name)) == NULL){
		    Error1F("Unknown user \"%s\".", name);
		    return(NULL);
		}
		sprintf(buffer, "%s", pw->pw_dir);
	    }
	}
    }else{
	sprintf(buffer, "%s", name);
    }
    p = buffer;
    while(*p){
	if(p[0]=='$' && p[1]=='$' && p[2]=='$' && p[3]=='$' && p[4]=='$'){
	    int x = getpid();
	    *p++ = '0'+(x/10000)%10;
	    *p++ = '0'+(x/1000)%10;
	    *p++ = '0'+(x/100)%10;
	    *p++ = '0'+(x/10)%10;
	    *p++ = '0'+x%10;
	}else{
	    p++;
	}
    }
    return(buffer);
}
