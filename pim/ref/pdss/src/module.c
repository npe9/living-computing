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

MODULE_ENTRY  *module_id_table[MODULE_TABLE_SIZE];


/*************************************************************************
*   Module Table.							 *
*************************************************************************/

int lookup_module(id, mod)
    register unsigned int id;	/** Module ID == Module Name Atom **/
    MODULE_ENTRY **mod;
{
    register MODULE_ENTRY *p;
    p = module_id_table[HashModuleID(id)];
    while(p){
	if(p->module_id == id){
	    *mod = p;
	    return(MODMAN_SUCCESS);
	}
	p = p->next;
    }
    return(MODMAN_MODULE_NOT_FOUND);
}

int enter_module(id, addr, size, indp)
    unsigned int id;
    OBJ *addr;
    int size;
    MODULE_ENTRY **indp;
{
    if(lookup_module(id, indp) == MODMAN_SUCCESS){
	if((*indp)->protect == NO){	/** module update **/
	    (*indp)->addr = addr;
	    (*indp)->size = size;
	    PrintCons1F("Module '%s' was updated.\n", atom_name(id));
	    return(MODMAN_SUCCESS);
	}else{
	    Error1F(
	      "\n>>> Module Manager: Module '%s' is protected. Cannot update.",
		    atom_name(id));
	    return(MODMAN_MODULE_PROTECTED);
	}
    }else{				/* undefined */
	MODULE_ENTRY *p1, *p = module_id_table[HashModuleID(id)];;
	p1 = (MODULE_ENTRY *)malloc(sizeof(MODULE_ENTRY));
	if(p1 == NULL){
	    Error(
       "\n>>> Module Manager: Not Enough Memory (malloc failure) -- Aborted.");
	    exit_pdss(1);
	}
	p1->next = p;
	p1->module_id = id;
	p1->addr = addr;
	p1->size = size;
	p1->protect = NO;
	*indp = p1;
	module_id_table[HashModuleID(id)] = p1;
	return(MODMAN_SUCCESS);
    }
}

int remove_module(id)
    register unsigned int id;
{
    register MODULE_ENTRY *p, *befor;
    p = module_id_table[HashModuleID(id)];
    if(p){
	if(p->module_id == id) {
	    if(p->protect == NO){
		module_id_table[HashModuleID(id)] = p->next;
		free(p);
		return(MODMAN_SUCCESS);
	    }else{
		goto error;
	    }
	}
	befor = p;
	p = p->next;
	while(p){
	    if(p->module_id == id){
		if(p->protect == NO){
		    befor->next = p->next;
		    free(p);
		    return(MODMAN_SUCCESS);
		}else{
	      error:
		    Error1F(
	      "\n>>> Module Manager: Module '%s' is protected. Cannot remove.",
			    atom_name(id));
		    return(MODMAN_MODULE_PROTECTED);
		}
	    }
	    befor = p;
	    p = p->next;
	}
    }
    return(MODMAN_MODULE_NOT_FOUND);
}


/*************************************************************************
*   Predicate Table.							 *
*************************************************************************/

OBJ *find_predicate(mod, pid)
    MODULE_ENTRY *mod;
    unsigned int pid;		/** predicate ID **/
{
    register OBJ *addr = mod->addr;

    if(IsNativeCode(addr)){
	register PREDICATE_ENTRY *p;
	register unsigned int x;
	x = HashPredID(pid);
	p = mod->pid_func_hash_tbl[x];
	while(p){
	    if(p->pid == pid){
		return((OBJ *)(p->function));
	    }
	    p = p->p1;
	}
    }else{
	register unsigned int size;
	addr += MODULE_HEADER_LENGTH;  /** entry table addr **/
	addr += ENTRY_TABLE_HASH_FUNC(pid)*TLEN_of_ENTRY_TABLE;
	size = GetUShort(addr+CNUM_of_ENTRY_TABLE);  /** Collision number **/
	addr = GetAddr(addr+OFST_of_ENTRY_TABLE);
	while(size--){
	    if(GetPredID(addr+PRED_of_ENTRY_TABLE) == pid){
		addr = GetAddr(addr+LAB_of_ENTRY_TABLE);
		return(addr);
	    }
	    addr += ELEN_of_ENTRY_TABLE;
	}
    }
    return(NULL);
}


/*************************************************************************
*   Runtime Support Functions for Native Code Module.			 *
*************************************************************************/

function_to_mod_pred_arity(func, mod, pred, arity)
    int (* func)();
    unsigned int *mod, *pred, *arity;
{
    MODULE_ENTRY *m;
    register PREDICATE_ENTRY *p;
    register int i, x;
    for(i=0; i<MODULE_TABLE_SIZE; i++){
	m = module_id_table[i];
	while(m){
	    if((OBJ *)func >= m->addr && (OBJ *)func < m->addr+m->size){
		x = HashFuncAddr(func);
		p = m->func_pid_hash_tbl[x];
		while(p){
		    if(p->function == func){
			*mod = m->module_id;
			*pred = p->pid&0xFFFF;
			*arity = (p->pid>>16)&0xFFFF;
			return;
		    }
		    p = p->p2;
		}
	    }
	    m = m->next;
	}
    }
    dcode_function_to_mod_pred_arity(func, mod, pred, arity);
}

rehash_predicate_table(pt, pft, fpt, pn, ppn)
    PREDICATE_ENTRY *pt, **pft, **fpt;
    int pn, ppn;
{
    register int i, x;
    for(i=0; i<PREDICATE_TABLE_SIZE; i++){
	pft[i] = NULL; fpt[i] = NULL;
    }
    for(i=0; i<pn; i++){
	x = HashFuncAddr(pt[i].function);
	pt[i].p2 = fpt[x];
	fpt[x] = &pt[i];
    }
    for(i=0; i<ppn; i++){
	x = HashPredID(pt[i].pid);
	pt[i].p1 = pft[x];
	pft[x] = &pt[i];
    }
}

renumber_atoms_in_pred_and_const_table(pt, pn, ct, cn, at)
    PREDICATE_ENTRY *pt;
    register CELL *ct;
    register unsigned int pn, cn;
    unsigned short *at;
{
    while(pn--){
	pt->pid = at[pt->pid&0xFFFF]|(pt->pid&0xFFFF0000);
	pt++;
    }
    while(cn--){
	if(Typeof(ct) == ATOM){
	    Valueof(ct) = at[Valueof(ct)];
	}
	ct++;
    }
}


/*************************************************************************
*   Trace Mode / Spy.							 *
*************************************************************************/

int set_module_trace_flag(module, flag)
    unsigned int module;    /** Module Name (Atom)     **/
    int flag;		    /** Debug Flag (YES or NO) **/
{
    MODULE_ENTRY *mte;
    int f;
    if(f = lookup_module(module, &mte)) return(f);
    if(IsNativeCode(mte->addr)) return(MODMAN_NATIVE_CODE_MODULE);
    if(flag){
	GetModuleDebug(mte->addr) |= MODULE_DEBUG_ON;
    }else{
	GetModuleDebug(mte->addr) &= ~MODULE_DEBUG_ON;
    }
    return(MODMAN_SUCCESS);
}

int get_module_trace_flag(module, flag)
    unsigned int module;    /** Module Name (Atom)     **/
    int *flag;		    /** Debug Flag (YES or NO) **/
{
    MODULE_ENTRY *mte;
    int f;
    if(f = lookup_module(module, &mte)) return(f);
    if(IsNativeCode(mte->addr)) return(MODMAN_NATIVE_CODE_MODULE);
    if(GetModuleDebug(mte->addr) == MODULE_DEBUG_ON){
	*flag = YES;
    }else{
	*flag = NO;
    }
    return(MODMAN_SUCCESS);
}

int set_predicate_spy_flag(module, predicate, arity, flag)
    unsigned int module;     /** Module Name (Atom)    **/
    unsigned int predicate;  /** Predicate Name (Atom) **/
    int arity;		     /** Arity (Int), Arity<0 -> Each Arity **/
    int flag;		     /** Spy Flag (YES or NO)  **/
{
    MODULE_ENTRY  *mte;
    OBJ	 *p, *bottom;
    unsigned int predicate0, table_size, code_size;
    int arity0, cnst_offs, f;

    if(f = lookup_module(module, &mte)) return(f);
    p = mte->addr;
    if(IsNativeCode(p)) return(MODMAN_NATIVE_CODE_MODULE);
    code_size = GetModuleSize(p);
    cnst_offs = GetConstantOffset(p);
    table_size = GetEntryTableSize(p);
    if(cnst_offs == 0){
	bottom = p+code_size+MODULE_SIZE_LENGTH;
    }else{
	bottom = p+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    p += table_size+MODULE_HEADER_LENGTH;
    if(arity >= 0){
	while(p+PREDICATE_HEADER_LENGTH < bottom){
	    code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	    predicate0 = GetPredicateName(p+PREDICATE_HEADER_LENGTH);
	    arity0 = GetPredicateArity(p+PREDICATE_HEADER_LENGTH);
	    if(predicate == predicate0 && arity == arity0){
		if(flag){
		    GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
			|= PREDICATE_SPY_ON;
		}else{
		    GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
			&= ~PREDICATE_SPY_ON;
		}
		return(MODMAN_SUCCESS);
	    }
	    p += code_size+PREDICATE_SIZE_LENGTH;
	}
	return(MODMAN_PREDICATE_NOT_FOUND);
    }else{
	f = MODMAN_PREDICATE_NOT_FOUND;
	while(p+PREDICATE_HEADER_LENGTH < bottom){
	    code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	    predicate0 = GetPredicateName(p+PREDICATE_HEADER_LENGTH);
	    if(predicate == predicate0){
		if(flag){
		    GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
			|= PREDICATE_SPY_ON;
		}else{
		    GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
			&= ~PREDICATE_SPY_ON;
		}
		f = MODMAN_SUCCESS;
	    }
	    p += code_size+PREDICATE_SIZE_LENGTH;
	}
	return(f);
    }
}

int get_predicate_spy_flag(module, predicate, arity, flag)
    unsigned int module;     /** Module Name (Atom)    **/
    unsigned int predicate;  /** Predicate Name (Atom) **/
    int arity;		     /** Arity (Int)	       **/
    int *flag;		     /** Spy Flag (YES or NO)  **/
{
    MODULE_ENTRY  *mte;
    OBJ	 *p, *bottom;
    unsigned int predicate0, table_size, code_size;
    int arity0, cnst_offs, f;

    if(f = lookup_module(module, &mte)) return(f);
    p = mte->addr;
    if(IsNativeCode(p)) return(MODMAN_NATIVE_CODE_MODULE);
    code_size = GetModuleSize(p);
    cnst_offs = GetConstantOffset(p);
    table_size = GetEntryTableSize(p);
    if(cnst_offs == 0){
	bottom = p+code_size+MODULE_SIZE_LENGTH;
    }else{
	bottom = p+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    p += table_size+MODULE_HEADER_LENGTH;
    while(p+PREDICATE_HEADER_LENGTH < bottom){
	code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	predicate0 = GetPredicateName(p+PREDICATE_HEADER_LENGTH);
	arity0 = GetPredicateArity(p+PREDICATE_HEADER_LENGTH);
	if(predicate == predicate0 && arity == arity0){
	    if(GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
	       & PREDICATE_SPY_ON){
		*flag = YES;
	    }else{
		*flag = NO;
	    }
	    return(MODMAN_SUCCESS);
	}
	p += code_size+PREDICATE_SIZE_LENGTH;
    }
    return(MODMAN_PREDICATE_NOT_FOUND);
}


/*************************************************************************
*   Get Predicate List.							 *
*************************************************************************/

int get_public_predicates(module, predicates)
    unsigned int module;  /** Module Name (Atom)   **/
    CELL *predicates;	  /** Predicates Name List **/
{
    MODULE_ENTRY *mte;
    register CELL *cdr, *cons, *pred;
    int f;

    if(f = lookup_module(module, &mte)) return(f);
    cdr = predicates;
    if(IsNativeCode(mte->addr)){
	register PREDICATE_ENTRY *p;
	register unsigned int x;
	for(x=0; x<PREDICATE_TABLE_SIZE; x++){
	    for(p=mte->pid_func_hash_tbl[x]; p!=NULL; p=p->p1){
		if(GcFlag_ON()) return(MODMAN_REQUEST_GC); 
		AllocCons(cons);
		AllocVector2(pred, 2);
		SetAll(cdr, LIST, cons, MRBOFF);
		SetAll(cons, VECTOR, pred, MRBOFF); pred++;
		SetAll(pred, ATOM, p->pid&0xFFFF, MRBOFF); pred++;
		SetAll(pred, INT, p->pid>>16, MRBOFF);
		cdr = cons+1;
	    }
	}
    }else{
	register OBJ *p;
	unsigned int predicate, arity, table_size;
	p = mte->addr;
	table_size = GetNumberOfEntry(p);
	if(HeapRest() < table_size*5){
	    SetHeapGcFlag();
	    return(MODMAN_REQUEST_GC); 
	}
	p += MODULE_HEADER_LENGTH+ENTRY_TABLE_HASH_TABLE_SIZE;
	while(table_size--) {
	    predicate = GetInt(p)&0xFFFF;
	    arity = (GetInt(p)>>16)&0xFF;
	    p+=ELEN_of_ENTRY_TABLE;
	    AllocCons(cons);
	    AllocVector2(pred, 2);
	    SetAll(cdr, LIST, cons, MRBOFF);
	    SetAll(cons, VECTOR, pred, MRBOFF); pred++;
	    SetAll(pred, ATOM, predicate, MRBOFF); pred++;
	    SetAll(pred, INT, arity, MRBOFF);
	    cdr = cons+1;
	}
    }
    SetAll(cdr, ATOM, NIL, MRBOFF);
    return(MODMAN_SUCCESS);
}

int get_spied_predicates(module, predicates)
    unsigned int module;  /** Module Name (Atom)   **/
    CELL *predicates;	  /** Predicates Name List **/
{
    MODULE_ENTRY *mte;
    register CELL *cdr, *cons, *pred;
    register OBJ *p, *bottom;
    unsigned int predicate, arity, table_size, code_size;
    int cnst_offs, f;

    if(f = lookup_module(module, &mte)) return(f);
    p = mte->addr;
    if(IsNativeCode(p)) return(MODMAN_NATIVE_CODE_MODULE);
    code_size = GetModuleSize(p);
    cnst_offs = GetConstantOffset(p);
    table_size = GetEntryTableSize(p);
    if(cnst_offs == 0){
	bottom = p+code_size+MODULE_SIZE_LENGTH;
    }else{
	bottom = p+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    p += table_size+MODULE_HEADER_LENGTH;
    cdr = predicates;
    while(p+PREDICATE_HEADER_LENGTH < bottom) {
	code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	predicate = GetPredicateName(p+PREDICATE_HEADER_LENGTH);
	arity = GetPredicateArity(p+PREDICATE_HEADER_LENGTH);
	if(GetPredicateDebug(p+PREDICATE_HEADER_LENGTH)
	   ==PREDICATE_SPY_ON){
	    if(GcFlag_ON()) return(MODMAN_REQUEST_GC); 
	    AllocCons(cons);
	    AllocVector2(pred, 2);
	    SetAll(cdr, LIST, cons, MRBOFF);
	    SetAll(cons, VECTOR, pred, MRBOFF); pred++;
	    SetAll(pred, ATOM, predicate, MRBOFF); pred++;
	    SetAll(pred, INT, arity, MRBOFF);
	    cdr = cons+1;
	}
	p += code_size+PREDICATE_SIZE_LENGTH;
    }
    SetAll(cdr, ATOM, NIL, MRBOFF);
    return(MODMAN_SUCCESS);
}


/*************************************************************************
*   Profile.								 *
*************************************************************************/

int reset_module_profile_info(module)
    unsigned int module;
{
    MODULE_ENTRY *mte;
    OBJ *p, *bottom;
    unsigned int table_size, code_size;
    int cnst_offs, f;

    if(f = lookup_module(module, &mte)) return(f);
    p = mte->addr;
    if(IsNativeCode(p)) return(MODMAN_NATIVE_CODE_MODULE);
    code_size = GetModuleSize(p);
    cnst_offs = GetConstantOffset(p);
    table_size = GetEntryTableSize(p);
    if(cnst_offs == 0){
	bottom = p+code_size+MODULE_SIZE_LENGTH;
    }else{
	bottom = p+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    p += table_size+MODULE_HEADER_LENGTH;
    while(p+PREDICATE_HEADER_LENGTH < bottom) {
	code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	GetPredicateReductionCount(p+PREDICATE_HEADER_LENGTH) = 0;
	GetPredicateSuspensionCount(p+PREDICATE_HEADER_LENGTH) = 0;
	p += code_size+PREDICATE_SIZE_LENGTH;
    }
    return(MODMAN_SUCCESS);
}

int get_module_profile_info(module, info)
    int module;
    register CELL *info;
{
    MODULE_ENTRY *mte;
    register CELL *cons, *vect;
    register OBJ *p, *bottom;
    unsigned int predicate, arity, redc, susc, table_size, code_size;
    int cnst_offs, f;

    if(f = lookup_module(module, &mte)) return(f);
    p = mte->addr;
    if(IsNativeCode(p)) return(MODMAN_NATIVE_CODE_MODULE);
    code_size = GetModuleSize(p);
    cnst_offs = GetConstantOffset(p);
    table_size = GetEntryTableSize(p);
    if(cnst_offs == 0){
	bottom = p+code_size+MODULE_SIZE_LENGTH;
    }else{
	bottom = p+cnst_offs+MODULE_CONSTANT_OFFSET;
    }
    p += table_size+MODULE_HEADER_LENGTH;
    while(p+PREDICATE_HEADER_LENGTH < bottom) {
	if(GcFlag_ON()) return(MODMAN_REQUEST_GC); 
	code_size = GetPredicateSize(p+PREDICATE_HEADER_LENGTH);
	predicate = GetPredicateName(p+PREDICATE_HEADER_LENGTH);
	arity = GetPredicateArity(p+PREDICATE_HEADER_LENGTH);
	redc = GetPredicateReductionCount(p+PREDICATE_HEADER_LENGTH);
	susc = GetPredicateSuspensionCount(p+PREDICATE_HEADER_LENGTH);
	/** Make  {PredName,Arity,ReductionCount,SuspensionCount} **/
	AllocCons(cons);
	AllocVector2(vect, 4);
	SetAll(info, LIST, cons, MRBOFF);
	SetAll(cons, VECTOR, vect, MRBOFF); vect++;
	SetAll(vect, ATOM, predicate, MRBOFF); vect++;
	SetAll(vect, INT, arity, MRBOFF); vect++;
	SetAll(vect, INT, redc, MRBOFF); vect++;
	SetAll(vect, INT, susc, MRBOFF);
	info = cons+1;
	p += code_size+PREDICATE_SIZE_LENGTH;
    }
    SetAll(info, ATOM, NIL, MRBOFF);
    return(MODMAN_SUCCESS);
}


/*************************************************************************
*   Load / Save.							 *
*************************************************************************/

int load_from_sav_or_asm_file(name, mod_table)
    CHAR *name;
    MODULE_ENTRY **mod_table;
{
    int len;
    CHAR fname[256];

    len = strlen(name);
    if(strcmp(&name[len-2], ".o") == 0){
	switch(load_and_link_native_code_module(name, mod_table)){
	  case NLOAD_SUCCESS:
	    return(MODMAN_SUCCESS);
	  case NLOAD_CANNOT_OPEN_FILE:
/*	    Error1F("\n>>> Module Manager: Can't Open File \"%s\".", name); */
	    return(MODMAN_LOAD_ERROR);
	  case NLOAD_LINK_ERROR:
	    Error1F("\n>>> Module Manager: Can't Link File \"%s\".", name);
	    return(MODMAN_LOAD_ERROR);
	  case NLOAD_MEMORY_LIMIT:
     Error("\n>>> Module Manager: Can't Get Memory Segument for Native Code.");
	    return(MODMAN_LOAD_ERROR);
	  case NLOAD_MODULE_PROTECTED:
	Error("\n>>> Module Manager: Module is Protected. Can't Link Module.");
	    return(MODMAN_MODULE_PROTECTED);
	}
    }else if(strcmp(&name[len-4], ".sav") == 0){
	switch(load_sav_file(name, mod_table)){
	  case LOAD_SUCCESS:
	    return(MODMAN_SUCCESS);
	  case LOAD_NOT_SAV_FILE:
	  case LOAD_BAD_VERSION:
	  case LOAD_ERROR:
	    return(MODMAN_LOAD_ERROR);
	  case LOAD_MODULE_PROTECTED:
	    return(MODMAN_MODULE_PROTECTED);
	  case LOAD_REQUEST_GC:
	    return(MODMAN_REQUEST_GC);
	  default:
/*	    Error1F("\n>>> Module Manager: Can't Open File \"%s\".", name); */
	    return(MODMAN_CANNOT_OPEN_FILE);
	}
    }else if(strcmp(&name[len-4], ".asm") == 0){
	switch(load_asm_file(name, mod_table)){
	  case ASSEMBLE_SUCCESS:
	    return(MODMAN_SUCCESS);
	  case ASSEMBLE_ERROR:
	    return(MODMAN_LOAD_ERROR);
	  case ASSEMBLE_MODULE_PROTECTED:
	    return(MODMAN_MODULE_PROTECTED);
	  case ASSEMBLE_REQUEST_GC:
	    return(MODMAN_REQUEST_GC);
	  default:
/*	    Error1F("\n>>> Module Manager: Can't Open File \"%s\".", name); */
	    return(MODMAN_CANNOT_OPEN_FILE);
	}
    }else{
	sprintf(fname, "%s.sav", name);
	switch(load_sav_file(fname, mod_table)){
	  case LOAD_SUCCESS:
	    return(MODMAN_SUCCESS);
	  case LOAD_ERROR:
	    return(MODMAN_LOAD_ERROR);
	  case LOAD_MODULE_PROTECTED:
	    return(MODMAN_MODULE_PROTECTED);
	  case LOAD_REQUEST_GC:
	    return(MODMAN_REQUEST_GC);
	}
	sprintf(fname, "%s.asm", name);
	switch(load_asm_file(fname, mod_table)){
	  case ASSEMBLE_SUCCESS:
	    return(MODMAN_SUCCESS);
	  case ASSEMBLE_ERROR:
	    return(MODMAN_LOAD_ERROR);
	  case ASSEMBLE_MODULE_PROTECTED:
	    return(MODMAN_MODULE_PROTECTED);
	  case ASSEMBLE_REQUEST_GC:
	    return(MODMAN_REQUEST_GC);
	  default:
/*	    Error1F("\n>>> Module Manager: Can't Open File \"%s\".", fname); */
	    return(MODMAN_CANNOT_OPEN_FILE);
	}
    }
}

int load_from_asm_file(name, mod_table)
    CHAR *name;
    MODULE_ENTRY **mod_table;
{
    int len;
    CHAR fname[256];

    len = strlen(name);
    if(strcmp(&name[len-4], ".asm") != 0){
	sprintf(fname, "%s.asm", name);
	name = fname;
    }
    switch(load_asm_file(name, mod_table)){
      case ASSEMBLE_SUCCESS:
	return(MODMAN_SUCCESS);
      case ASSEMBLE_ERROR:
	return(MODMAN_LOAD_ERROR);
      case ASSEMBLE_MODULE_PROTECTED:
	return(MODMAN_MODULE_PROTECTED);
      case ASSEMBLE_REQUEST_GC:
	return(MODMAN_REQUEST_GC);
      default:
/*	Error1F("\n>>> Module Manager: Can't Open File \"%s\".", name); */
	return(MODMAN_CANNOT_OPEN_FILE);
    }
}

static load_sav_file(fname, mod_table)
    CHAR *fname;
    MODULE_ENTRY **mod_table;
{
    int status;
    FILE *fp;
    CHAR name[256], *expand_path_name();
    if(expand_path_name(fname, name) == NULL) return(-1);
    if((fp = fopen(name, "r")) == NULL) return(-1);
    status = load_module(fp, mod_table);
    fclose(fp);
    return(status);
}

static load_asm_file(fname, mod_table)
    CHAR *fname;
    MODULE_ENTRY **mod_table;
{
    int status;
    FILE *fp;
    CHAR name[256], *expand_path_name();
    if(expand_path_name(fname, name) == NULL) return(-1);
    if((fp = fopen(name, "r")) == NULL) return(-1);
    status = assemble(fp, mod_table);
    fclose(fp);
    return(status);
}

int save_to_sav_file(name, mod_table)
    CHAR *name;
    MODULE_ENTRY *mod_table;
{
    int len;
    CHAR fname[256];

    len = strlen(name);
    if(strcmp(&name[len-4], ".sav") != 0){
	sprintf(fname, "%s.sav", name);
	name = fname;
    }
    switch(save_sav_file(name, mod_table)){
      case 0:
	return(MODMAN_SUCCESS);
      default:
	Error1F("\n>>> Module Manager: Can't Write Open File \"%s\".", name);
	return(MODMAN_CANNOT_OPEN_FILE);
    }
}

static save_sav_file(fname, mod_table)
    CHAR *fname;
    MODULE_ENTRY *mod_table;
{
    FILE *fp;
    CHAR name[256], *expand_path_name();
    if(expand_path_name(fname, name) == NULL) return(-1);
    if((fp = fopen(name, "w")) == NULL) return(-1);
    save_module(fp, mod_table);
    fclose(fp);
    return(0);
}
