/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "instr.h"


/*************************************************************************
*   b_predicate_to_code(Rmodule,Rpred,Raarity,^Rcode)			 *
*************************************************************************/

DCODE dc_predicate_to_code(void)
{
    blt_b_predicate_to_code(&R0, &R1, &R2, &R4);
    active_unify(&R3, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_predicate_to_code(CELL *mod, CELL *pred, CELL *arity, CELL *code)
{
    register CELL *x;
    MODULE_ENTRY *m;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = pred;
    Dereference(x);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = arity;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_predicate_to_code), x,
				 IIIO, mod, pred, arity, code);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==mod ? 1 : (x==pred ? 2 : 3)),
				   KL1B_B_PREDICATE_TO_CODE,
				   IIIO, mod, pred, arity, code);
	}
    }else{
	if(lookup_module(Valueof(mod), &m) == MODMAN_SUCCESS &&
	   find_predicate(m, Valueof(pred)|(Valueof(arity)<<16))){
	    AllocVector2(x, 3);
	    x[1] = *mod;
	    x[2] = *pred;
	    x[3] = *arity;
	    SetAll(code, VECTOR, x, MRBOFF);
	}else{
	    *code = const_nil;
	}
    }
    return 0;
}


/*************************************************************************
*   b_code_to_predicate(Rcode,^Rmodule,^Rpred,^Rarity,^Rinfo)		 *
*************************************************************************/

DCODE dc_code_to_predicate(void)
{
    blt_b_code_to_predicate(&R0, &R5, &R6, &R7, &R8);
    active_unify(&R1, &R5);
    active_unify(&R2, &R6);
    active_unify(&R3, &R7);
    active_unify(&R4, &R8);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_code_to_predicate(CELL *code, CELL *mod, CELL *pred, CELL *arity, CELL *info)
{
    register CELL *x;
    register MRB mrb;
    int flag;
    x = code;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_exception;
    if(VectorLengthof(x) != 3) goto exception;
    mrb = Mrbof(x);
    x = VectorElementof(code, 0);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = VectorElementof(code, 1);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = VectorElementof(code, 2);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_code_to_predicate), x,
				 IOOOO, code, mod, pred, arity, info);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CODE_TO_PREDICATE,
				   IOOOO, code, mod, pred, arity, info);
	}
    }else{
	x = VectorElementof(code, 0);
	switch(get_predicate_spy_flag(Valueof(x+0), Valueof(x+1),
				      Valueof(x+2), &flag)){
	  case MODMAN_MODULE_NOT_FOUND:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CODE_TO_PREDICATE,
				   IOOOO, code, mod, pred, arity, info);
	    break;
	  case MODMAN_NATIVE_CODE_MODULE:
	    /* PORT: the original passed the module-name atom where
	       find_predicate() takes a MODULE_ENTRY pointer, and
	       dereferenced address 1 (test/b_code_e.kl1, check b). */
	    { MODULE_ENTRY *mte;
	    if(lookup_module(Valueof(x+0), &mte) == MODMAN_SUCCESS &&
	       find_predicate(mte, Valueof(x+1)|(Valueof(x+2)<<16))){
		flag = 0;
		goto success;
	    } }
	  case MODMAN_PREDICATE_NOT_FOUND:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CODE_TO_PREDICATE,
				   IOOOO, code, mod, pred, arity, info);
	    break;
	  case MODMAN_SUCCESS:
	  success:
	    SetAll(mod, ATOM, Valueof(x+0), MRBOFF);
	    SetAll(pred, ATOM, Valueof(x+1), MRBOFF);
	    SetAll(arity, INT, Valueof(x+2), MRBOFF);
	    SetAll(info, INT, flag, MRBOFF);
	    break;
	}
    }
    return 0;
}


/*************************************************************************
*   b_save_module(Rmodule,Rfname,^Rstt)					 *
*************************************************************************/

DCODE dc_save_module(void)
{
    blt_b_save_module(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_save_module(CELL *mod, CELL *file, CELL *status)
{
    register CELL *x;
    MODULE_ENTRY *mtbl;
    CHAR buf[256];
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = file;
    Dereference(x);
    if(Typeof(x) != STRING){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_save_module), x, IIO, mod, file, status);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==mod ? 1 : 2),
				   KL1B_B_SAVE_MODULE, IIO, mod, file, status);
	}
    }else{
	if((StringTypeof(file)&0xE7) != 0x03) goto exception;
	convert_to_c_string(file, buf, 250);
	if(Mrbof(file) == MRBOFF){
	    FreeString(Objectof(file), StringLengthof(file));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(file)+1);
	}
	if(lookup_module(Valueof(mod), &mtbl) == MODMAN_MODULE_NOT_FOUND){
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	}
	if(IsNativeCode(mtbl->addr)){
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	}
	if(save_to_sav_file(buf, mtbl) == MODMAN_CANNOT_OPEN_FILE){
	    SetAll(status, INT, MODMAN_CANNOT_OPEN_FILE, MRBOFF);
	    return 0;
	}
	SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
    }
    return 0;
}


/*************************************************************************
*   b_load_module(^Rmodule,Rfname,^Rstt)				 *
*************************************************************************/

DCODE dc_load_module(void)
{
    blt_b_load_module(&R3, &R1, &R4);
    active_unify(&R0, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_load_module(CELL *mod, CELL *file, CELL *status)
{
    register CELL *x;
    MODULE_ENTRY *mtbl;
    CHAR buf[256];
    x = file;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_load_module), x, OIO, mod, file, status);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_LOAD_MODULE, OIO, mod, file, status);
	}
    }else{
	if((StringTypeof(file)&0xE7) != 0x03) goto exception;
	convert_to_c_string(file, buf, 250);
	if(Mrbof(file) == MRBOFF){
	    FreeString(Objectof(file), StringLengthof(file));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(file)+1);
	}
	switch(load_from_sav_or_asm_file(buf, &mtbl)){
	  case MODMAN_CANNOT_OPEN_FILE:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_CANNOT_OPEN_FILE, MRBOFF);
	    return 0;
	  case MODMAN_LOAD_ERROR:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_LOAD_ERROR, MRBOFF);
	    return 0;
	  case MODMAN_MODULE_PROTECTED:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_MODULE_PROTECTED, MRBOFF);
	    return 0;
	  case MODMAN_REQUEST_GC:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_REQUEST_GC, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(mod, ATOM, mtbl->module_id, MRBOFF);
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_assemble_module(^Rmodule,Rfname,^Rstt)				 *
*************************************************************************/

DCODE dc_assemble_module(void)
{
    blt_b_assemble_module(&R3, &R1, &R4);
    active_unify(&R0, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_assemble_module(CELL *mod, CELL *file, CELL *status)
{
    register CELL *x;
    MODULE_ENTRY *mtbl;
    CHAR buf[256];
    x = file;
    Dereference(x);
    if(Typeof(x) != STRING){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_assemble_module), x, OIO, mod,file,status);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_ASSEMBLE_MODULE,OIO,mod,file,status);
	}
    }else{
	if((StringTypeof(file)&0xE7) != 0x03) goto exception;
	convert_to_c_string(file, buf, 250);
	if(Mrbof(file) == MRBOFF){
	    FreeString(Objectof(file), StringLengthof(file));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(file)+1);
	}
	switch(load_from_asm_file(buf, &mtbl)){
	  case MODMAN_CANNOT_OPEN_FILE:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_CANNOT_OPEN_FILE, MRBOFF);
	    return 0;
	  case MODMAN_LOAD_ERROR:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_LOAD_ERROR, MRBOFF);
	    return 0;
	  case MODMAN_MODULE_PROTECTED:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_MODULE_PROTECTED, MRBOFF);
	    return 0;
	  case MODMAN_REQUEST_GC:
	    *mod = const_nil;
	    SetAll(status, INT, MODMAN_REQUEST_GC, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(mod, ATOM, mtbl->module_id, MRBOFF);
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_remove_module(Rmodule,^Rstt)					 *
*************************************************************************/

DCODE dc_remove_module(void)
{
    blt_b_remove_module(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_remove_module(CELL *mod, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_remove_module), x, IO, mod, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_REMOVE_MODULE, IO, mod, status);
	}
    }else{
	switch(remove_module(Valueof(mod))){
	  case MODMAN_MODULE_NOT_FOUND:
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_MODULE_PROTECTED:
	    SetAll(status, INT, MODMAN_MODULE_PROTECTED, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_get_public_predicates(Rmodule,^Rlist,^Rstt)			 *
*************************************************************************/

DCODE dc_get_public_predicates(void)
{
    blt_b_get_public_predicates(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_public_predicates(CELL *mod, CELL *list, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_get_public_predicates), x,
				 IOO, mod, list, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_GET_PUBLIC_PREDICATES,
				   IOO, mod, list, status);
	}
    }else{
	CELL new;
	switch(get_public_predicates(Valueof(mod), &new)){
	  case MODMAN_REQUEST_GC:
	    SetCodeGcFlag();
	    body_builtin_swap(CodeOfFunction(dc_get_public_predicates),
			      IOO, mod, list, status);
	    return 0;
	  case MODMAN_MODULE_NOT_FOUND:
	    *list = const_nil;
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    *list = new;
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_trace_module(Rmodule,Rflag,^Rstt)					 *
*************************************************************************/

DCODE dc_trace_module(void)
{
    blt_b_trace_module(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_trace_module(CELL *mod, CELL *flag, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    x = flag;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_trace_module), x, IIO, mod, flag, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==mod ? 1 : 2),
				   KL1B_B_TRACE_MODULE, IIO, mod,flag,status);
	}
    }else{
	switch(set_module_trace_flag(Valueof(mod), Valueof(flag))){
	  case MODMAN_MODULE_NOT_FOUND:
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_get_module_status(Rmodule,^Rflag,^Rstt)				 *
*************************************************************************/

DCODE dc_get_module_status(void)
{
    blt_b_get_module_status(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_module_status(CELL *mod, CELL *flag, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_get_module_status), x,
				 IOO, mod, flag, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_GET_MODULE_STATUS,
				   IOO, mod, flag, status);
	}
    }else{
	int f;
	switch(get_module_trace_flag(Valueof(mod), &f)){
	  case MODMAN_MODULE_NOT_FOUND:
	    SetAll(flag, ATOM, NIL, MRBOFF);
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    SetAll(flag, ATOM, NIL, MRBOFF);
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(flag, INT, f, MRBOFF);
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_spy_predicate(Rcode,Rflag,^Rstt)					 *
*************************************************************************/

DCODE dc_spy_predicate(void)
{
    blt_b_spy_predicate(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_spy_predicate(CELL *code, CELL *flag, CELL *status)
{
    register CELL *x;
    register MRB mrb;
    unsigned int mod, pred;
    int arity;

    x = code;
    Dereference(x);
    if(Typeof(x) != VECTOR) goto suspend_or_exception;
    if(VectorLengthof(x) != 3) goto exception;
    mrb = Mrbof(x);
    x = VectorElementof(code, 0);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    mod = Valueof(x);
    x = VectorElementof(code, 1);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != ATOM) goto suspend_or_exception;
    pred = Valueof(x);
    x = VectorElementof(code, 2);
    Dereference(x);
    if(mrb == MRBON) SetMrbof(x, MRBON);
    if(Typeof(x) != INT) goto suspend_or_exception;
    arity = Valueof(x);
    x = flag;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_spy_predicate), x, IIO, code, flag, status);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==flag ? 2 : 1),
				   KL1B_B_SPY_PREDICATE, IIO,code,flag,status);
	}
    }else{
	switch(set_predicate_spy_flag(mod, pred, arity, Valueof(flag))){
	  case MODMAN_MODULE_NOT_FOUND:
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_PREDICATE_NOT_FOUND:
	    SetAll(status, INT, MODMAN_PREDICATE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_get_spied_predicates(Rmodule,^Rlist,^Rstt)			 *
*************************************************************************/

DCODE dc_get_spied_predicates(void)
{
    blt_b_get_spied_predicates(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_spied_predicates(CELL *mod, CELL *list, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_get_spied_predicates), x,
				 IOO, mod, list, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_GET_SPIED_PREDICATES,
				   IOO, mod, list, status);
	}
    }else{
	CELL new;
	switch(get_spied_predicates(Valueof(mod), &new)){
	  case MODMAN_REQUEST_GC:
	    SetCodeGcFlag();
	    body_builtin_swap(CodeOfFunction(dc_get_spied_predicates),
			      IOO, mod, list, status);
	    return 0;
	  case MODMAN_MODULE_NOT_FOUND:
	    *list = const_nil;
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    *list = const_nil;
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    *list = new;
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_reset_profile_info(Rmodule,^Rstt)					 *
*************************************************************************/

DCODE dc_reset_profile_info(void)
{
    blt_b_reset_profile_info(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_reset_profile_info(CELL *mod, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_reset_profile_info), x, IO, mod, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_RESET_PROFILE_INFO, IO, mod, status);
	}
    }else{
	switch(reset_module_profile_info(Valueof(mod))){
	  case MODMAN_MODULE_NOT_FOUND:
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}


/*************************************************************************
*   b_get_profile_info(Rmodule,^Rlist,^Rstt)				 *
*************************************************************************/

DCODE dc_get_profile_info(void)
{
    blt_b_get_profile_info(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_profile_info(CELL *mod, CELL *list, CELL *status)
{
    register CELL *x;
    x = mod;
    Dereference(x);
    if(Typeof(x) != ATOM){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_get_profile_info), x,
				 IOO, mod, list, status);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_GET_PROFILE_INFO,
				   IOO, mod, list, status);
	}
    }else{
	CELL new;
	switch(get_module_profile_info(Valueof(mod), &new)){
	  case MODMAN_REQUEST_GC:
	    SetCodeGcFlag();
	    body_builtin_swap(CodeOfFunction(dc_get_profile_info), IOO, mod, list, status);
	    return 0;
	  case MODMAN_MODULE_NOT_FOUND:
	    *list = const_nil;
	    SetAll(status, INT, MODMAN_MODULE_NOT_FOUND, MRBOFF);
	    return 0;
	  case MODMAN_NATIVE_CODE_MODULE:
	    *list = const_nil;
	    SetAll(status, INT, MODMAN_NATIVE_CODE_MODULE, MRBOFF);
	    return 0;
	  case MODMAN_SUCCESS:
	    *list = new;
	    SetAll(status, INT, MODMAN_SUCCESS, MRBOFF);
	    return 0;
	}
    }
    return 0;
}
