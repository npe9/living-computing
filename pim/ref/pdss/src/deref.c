/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"

#if MRBGC_SWITCH
CELL *dereference(reg)
    CELL *reg;
{
    register CELL *var;
    if(Mrbof(reg) == MRBON){
	var = Objectof(reg);
	while(Typeof(var) == REF){
#if MRBGC_DEREF_TYPE==1
	    if(Mrbof(var) == MRBOFF){
		var = dereference(var);
		break;
	    }
#endif
	    var = Objectof(var);
	}
	if(IsUnbound(var)){
	    SetAll(reg, REF, var, MRBON);
	    return(var);
	}else{
	    SetAll(reg, Typeof(var), Valueof(var), MRBON);
	    return(reg);
	}
    }else{
	var = Objectof(reg);
	while(Typeof(var) == REF){
	    if(Mrbof(var) == MRBON){
		var = Objectof(var);
		while(Typeof(var) == REF){
#if MRBGC_DEREF_TYPE==1
		    if(Mrbof(var) == MRBOFF){
			var = dereference(var);
			break;
		    }
#endif
		    var = Objectof(var);
		}
		if(IsUnbound(var)){
		    SetAll(reg, REF, var, MRBON);
		    return(var);
		}else{
		    SetAll(reg, Typeof(var), Valueof(var), MRBON);
		    return(reg);
		}
	    }else{
		register CELL *w = var;
		var = Objectof(var);
		FreeCell(w);
		mrbgc_statistics_deref();
	    }
	}
	if(IsUnbound(var)){
	    SetAll(reg, REF, var, MRBOFF);
	    return(var);
	}else{
	    *reg = *var;
	    if(Mrbof(var) == MRBOFF){
		FreeCell(var);	
		mrbgc_statistics_deref();
	    }
	    return(reg);
	}
    }
}
#else
CELL *dereference(reg)
    CELL *reg;
{
    register CELL *var = reg;
    do{
	if(Mrbof(var) == MRBON){
	    do{ var = Objectof(var); } while(Typeof(var) == REF);
	    if(IsUnbound(var)){
		SetAll(reg, REF, var, MRBON);
		return(var);
	    }else{
		SetAll(reg, Typeof(var), Valueof(var), MRBON);
		return(reg);
	    }
	}
	var = Objectof(var);
    }while(Typeof(var) == REF);
    if(IsUnbound(var)){
	SetAll(reg, REF, var, MRBOFF);
	return(var);
    }else{
	*reg = *var;
	return(reg);
    }
}
#endif
