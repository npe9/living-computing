/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"


/*************************************************************************
*   General Unification.  X=Y.						 *
*************************************************************************/

int passive_unify(register CELL *x, MRB mrbx, register CELL *y, MRB mrby, int depth)
    /** Used for Eager Deadlock Detection **/
{
    register int len;
  loop:
    Dereference(x);
    Dereference(y);
    switch(Typeof(x)){
      case ATOM: case INT: case FLOAT: case NUE: case SHOEN:
	if(Typeof(x) == Typeof(y)){
	    return(Valueof(x) == Valueof(y));
	}else{
	    if(IsRef(y)) PushToSuspensionStack2(y, mrby);
	    return(NO);
	}
      case LIST:
	if(Typeof(y) == LIST){
	    if(--depth < 0) return(NO);
	    mrbx |= Mrbof(x); x = Objectof(x);
	    mrby |= Mrbof(y); y = Objectof(y);
	    if(!passive_unify(x, mrbx, y, mrby, depth)) return(NO);
	    x++; y++;
	    goto loop;
	}else{
	    if(IsRef(y)) PushToSuspensionStack2(y, mrby);
	    return(NO);
	}
      case VECTOR:
	if(Typeof(y) == VECTOR){
	    len = VectorLengthof(x);
	    if(len == VectorLengthof(y) && --depth >= 0){
		mrbx |= Mrbof(x); x = Objectof(x)+1;
		mrby |= Mrbof(y); y = Objectof(y)+1;
		while(--len >= 0){
		    if(!passive_unify(x, mrbx, y, mrby, depth)) return(NO);
		    x++; y++;
		}
		return(YES);
	    }else{
		return(NO);
	    }
	}else{
	    if(IsRef(y)) PushToSuspensionStack2(y, mrby);
	    return(NO);
	}
      case STRING:
	if(Typeof(y) == STRING){
	    len = StringLengthof(x);
	    if(len == StringLengthof(y)){
		x = Objectof(x);
		y = Objectof(y);
		while(len-- >= 0){
		    if(Valueof(x) != Valueof(y)) return(NO);
		    x++; y++;
		}
		return(YES);
	    }else{
		return(NO);
	    }
	}else{
	    if(IsRef(y)) PushToSuspensionStack2(y, mrby);
	    return(NO);
	}
      case REF:	 /** --> UNDEF,HOOK,MHOOK,MGHOK **/
	PushToSuspensionStack2(x, mrbx);
	return(NO);
      DEFAULT:
	return(NO);
    }
}


/*************************************************************************
*   Ground Check.							 *
*************************************************************************/

int is_ground(register CELL *x, MRB mrb, int depth)
    /** Used for Eager Deadlock Detection **/
{
    register int len;
  loop:
    Dereference(x);
    switch(Typeof(x)){
      case ATOM: case INT: case FLOAT: case STRING: case NUE: case SHOEN:
	return(YES);
      case LIST:
	if(--depth < 0) return(NO);
	mrb |= Mrbof(x); x = Objectof(x);
	if(!is_ground(x, mrb, depth)) return(NO);
	x++;
	goto loop;
      case VECTOR:
	if(--depth < 0) return(NO);
	len = VectorLengthof(x);
	mrb |= Mrbof(x); x = Objectof(x)+1;
	while(--len >= 0){
	    if(!is_ground(x, mrb, depth)) return(NO);
	    x++;
	}
	return(YES);
      case REF:	 /** --> UNDEF,HOOK,MHOOK,MGHOK **/
	PushToSuspensionStack2(x, mrb);
	return(NO);
      DEFAULT:
	return(NO);
    }
}
