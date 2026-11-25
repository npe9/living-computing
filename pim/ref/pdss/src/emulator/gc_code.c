/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "klb.h"
#include "gc.h"


/*************************************************************************
*   GC KL1-B Code Area.							 *
*************************************************************************/

int gc_code_area(void)
{
    register int  i;
    register MODULE_ENTRY  *p;
    for(i = 0; i < MODULE_TABLE_SIZE; i++){
	for(p = module_id_table[i]; p != NULL; p = p->next){
	    if(p->addr != NULL){
		p->addr = gc_code_module(p->addr);
	    }
	}
    }
}


/*************************************************************************
*   GC Predicate.							 *
*************************************************************************/

OBJ *gc_predicate(OBJ *old)
{
    OBJ	 *oldtop;
    if(InUserCode(old)){
	oldtop = GetModuleTop(old);
	return(gc_code_module(oldtop)+(old-oldtop));
    }else{
	return(old);
    }
}


/*************************************************************************
*   GC KL1-B Program Module.						 *
*************************************************************************/

OBJ *gc_code_module(OBJ *old)
{
    register OBJ  *new, *from, *to;
    register OBJ  *module_bottom, *program_bottom;
    register int  code_size, cnst_offs;

    if(InUserCode(old)){
	if(IsNotCodeCopied(old)){
	    code_size = GetModuleSize(old)+MODULE_SIZE_LENGTH;
	    cnst_offs = GetConstantOffset(old);
	    module_bottom = old+code_size;
	    if(cnst_offs == 0){
		program_bottom = module_bottom;
	    }else{
		program_bottom = old+cnst_offs+MODULE_CONSTANT_OFFSET;
	    }
	    from = old;
	    to = new = C; C += code_size;
	    while(from < program_bottom){
		*to++ = *from++;
	    }
	    if(from < module_bottom){
		gc_constant_section(from, to, module_bottom);
	    }
	    SetCodeGCinfo(old, new);
	}else{
	    new = GetNewAddress(old);
	}
	return(new);
    }else{
	return(old);
    }
}


/*************************************************************************
*   GC Structured Constant.						 *
*************************************************************************/

int gc_constant_section(CELL *from, CELL *to, CELL *bottom)
{
    int offs = (int)to-(int)from;
    while(from < bottom){
	switch(Typeof(from)){
	  case ATOM:
	  case INT:
	  case FLOAT:
	  case DESC:
	    *to = *from;
	    break;
	  case LIST:
	  case VECTOR:
	  case STRING:
	  case 0xFF:
	    SetAll(to, Typeof(from), Valueof(from)+offs, MRBON);
	    break;
	}
	from++; to++;
    }
}

CELL *gc_cell_in_constant_section(CELL *old)
{
    CELL *p;
    OBJ *oldtop, *newtop;
    if(InUserCode(old)){
	if(IsNotCodeCopied(old)){
	    p = old;
	    while(Typeof(p) != 0xFF) p--;
	    oldtop = (OBJ *)Valueof(p);
	    newtop = gc_code_module(oldtop);
	    return((CELL *)((int)old+(newtop-oldtop)));
	}else{
	    return((CELL *)Valueof(old));
	}
    }else{
	return(old);
    }
}
