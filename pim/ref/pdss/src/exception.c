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
/* PORT: forward declarations */
static int create_goal_and_wait_new_code();



/*************************************************************************
*   Exception Tag Table.						 *
*************************************************************************/

#define SIZE_OF_EXCEPTION_TAG_TABLE 20
static int exception_tag_table[SIZE_OF_EXCEPTION_TAG_TABLE];

initialize_exception_tag_table()
{
    exception_tag_table[ILLEGAL_INPUT_TYPE]   = ILLEGAL_INPUT_TYPE_TAG;
    exception_tag_table[RANGE_OVERFLOW]	      = RANGE_OVERFLOW_TAG;
    exception_tag_table[INTEGER_OVERFLOW]     = INTEGER_OVERFLOW_TAG;
    exception_tag_table[FLOATING_ERROR]	      = FLOATING_ERROR_TAG;
    exception_tag_table[ILLEGAL_MERGER_INPUT] = ILLEGAL_MERGER_INPUT_TAG;
    exception_tag_table[REDUCTION_FAILED]     = REDUCTION_FAILED_TAG;
    exception_tag_table[UNIFY_FAILED]	      = UNIFY_FAILED_TAG;
    exception_tag_table[INCORRECT_PRIORITY]   = INCORRECT_PRIORITY_TAG;
    exception_tag_table[MODULE_NOT_FOUND]     = MODULE_NOT_FOUND_TAG;
    exception_tag_table[PREDICATE_NOT_FOUND]  = PREDICATE_NOT_FOUND_TAG;
}


/*************************************************************************
*   Raise -- User Exception.						 *
*************************************************************************/

raise(tag, type, info)
    unsigned int tag;
    CELL *type, *info;
{
    register CELL *v, *code, *argv;
    CELL mesg;		/** raised(Type,Info,NewCode,NewArgv) **/
    AllocVector2(v, 5);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_raised;
    *v++ = *type;
    *v++ = *info;
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(parent, &mesg, tag);
}


/*************************************************************************
*   Body Goal Exception - Module/Predicate not Found, Reduction Failed.	 *
*************************************************************************/

body_goal_exception(excp_code, mod, pred, argn, args)
    unsigned int excp_code, mod, pred, argn;
    CELL *args;
{
    register int i;
    register CELL *v, *g, *code, *argv;
    CELL mesg;		/** exception(ExpCode,Code,Argv,NewCode,NewArgv) **/
    AllocVector2(v, 6);
    AllocVector2(g, 3);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_exception;
    SetAll(v, INT, excp_code, MRBOFF); v++;
    SetAll(v, VECTOR, g, MRBOFF); v++; g++;
    SetAll(g, ATOM, mod, MRBOFF); g++;
    SetAll(g, ATOM, pred, MRBOFF); g++;
    SetAll(g, INT, argn, MRBOFF);
    AllocVector(g, argn);
    SetAll(v, VECTOR, g, MRBOFF); v++;
    for(i=0; i<argn; i++) *++g = args[i];
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(parent, &mesg,
				       exception_tag_table[excp_code]);
}

body_goal_exception2(excp_code, cd, av)
    CELL *cd, *av;
{
    register int i;
    register CELL *v, *code, *argv;
    CELL mesg;		/** exception(ExpCode,Code,Argv,NewCode,NewArgv) **/
    AllocVector2(v, 6);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_exception;
    SetAll(v, INT, excp_code, MRBOFF); v++;
    *v++ = *cd;
    *v++ = *av;
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(parent, &mesg,
				       exception_tag_table[excp_code]);
}


/*************************************************************************
*   Active Unify Exception.						 *
*************************************************************************/

exception_active_unify_fail(x, y)
    CELL *x, *y;
{
    register CELL *v, *g, *code, *argv;
    CELL mesg;		/** exception(ExcCode,X,Y,UserCode,NewCode,NewArgv) **/
    OBJ *ptop;
    AllocVector2(v, 7);
    AllocVector2(g, 3);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_exception;
    SetAll(v, INT, UNIFY_FAILED, MRBOFF); v++;
    *v++ = *x;
    *v++ = *y;
    SetAll(v, VECTOR, g, MRBOFF); v++; g++;
    ptop = current_predicate2 ? current_predicate2 : current_predicate;
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(g, ATOM, mod, MRBOFF); g++;
	SetAll(g, ATOM, pred, MRBOFF); g++;
	SetAll(g, INT, arity, MRBOFF);
    }else{
	SetAll(g, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF); g++;
	SetAll(g, ATOM, GetPredicateName(ptop), MRBOFF); g++;
	SetAll(g, INT, GetPredicateArity(ptop), MRBOFF);
    }
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(parent, &mesg,
				       exception_tag_table[UNIFY_FAILED]);
}


/*************************************************************************
*   Illegal Merger Input Exception.					 *
*************************************************************************/

exception_illegal_merger_input(x, strm)
    CELL *x, *strm;
{
    register CELL *v, *g, *code, *argv;
    CELL mesg;	/** exception(ExcCode,X,S,Code,UnifyCode,NewCode,NewArgv) **/
    OBJ *ptop;
    AllocVector2(v, 8);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_exception;
    SetAll(v, INT, ILLEGAL_MERGER_INPUT, MRBOFF); v++;
    *v++ = *x;
    *v++ = *strm;
    AllocVector2(g, 3);
    SetAll(v, VECTOR, g, MRBOFF); v++; g++;
    ptop = Mergerof(Objectof(strm))->pcode;
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(g, ATOM, mod, MRBOFF); g++;
	SetAll(g, ATOM, pred, MRBOFF); g++;
	SetAll(g, INT, arity, MRBOFF);
    }else{
	SetAll(g, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF); g++;
	SetAll(g, ATOM, GetPredicateName(ptop), MRBOFF); g++;
	SetAll(g, INT, GetPredicateArity(ptop), MRBOFF);
    }
    AllocVector2(g, 3);
    SetAll(v, VECTOR, g, MRBOFF); v++; g++;
    ptop = current_predicate2 ? current_predicate2 : current_predicate;
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(g, ATOM, mod, MRBOFF); g++;
	SetAll(g, ATOM, pred, MRBOFF); g++;
	SetAll(g, INT, arity, MRBOFF);
    }else{
	SetAll(g, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF); g++;
	SetAll(g, ATOM, GetPredicateName(ptop), MRBOFF); g++;
	SetAll(g, INT, GetPredicateArity(ptop), MRBOFF);
    }
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(Mergerof(Objectof(strm))->parent, &mesg,
				    exception_tag_table[ILLEGAL_MERGER_INPUT]);
}


/*************************************************************************
*   Body Builtin Exception.						 *
*************************************************************************/

body_builtin_exception(excp_code, where, opcode, argio, pa0, pa1, pa2, pa3, pa4, pa5, pa6, pa7)
    unsigned int excp_code, where, opcode, argio;
    CELL *pa0, *pa1, *pa2, *pa3, *pa4, *pa5, *pa6, *pa7;  /* PORT: was va_alist */
{
    CELL *bltargs[8]; int bltn = 0;  /* PORT */
    register int i;
    register CELL *v, *g, *x, *undef, *code, *argv;
    CELL mesg; /** exception(ExpCode,OP,Argv,UserCode,NewCode,NewArgv) **/
    OBJ *ptop;
    static CELL *ap[MAXREGS];
    for(i=0; (argio>>(i*3))&(I|O); i++);
    if(where) AllocVector2(v, 8) else AllocVector2(v, 7);
    AllocVector(g, i);
    AllocUndef(code);
    AllocUndef(argv);
    SetAll(&mesg, VECTOR, v, MRBOFF); v++;
    *v++ = const_atom_exception;
    SetAll(v, INT, excp_code, MRBOFF); v++;
    SetAll(v, INT, opcode, MRBOFF); v++;
    SetAll(v, VECTOR, g, MRBOFF); v++;
    if(where){ SetAll(v, INT, where, MRBOFF); v++; }
    bltargs[0]=pa0; bltargs[1]=pa1; bltargs[2]=pa2; bltargs[3]=pa3;
    bltargs[4]=pa4; bltargs[5]=pa5; bltargs[6]=pa6; bltargs[7]=pa7;
    for(i=0; argio&(I|O); i++,argio>>=3){
	g++;
	x = bltargs[bltn++];
	if(argio&I){
	    /*** Input Argument ***/
	    *g = *x;
	    ap[i] = NULL;
	}else{
	    /*** Output Argument ***/
	    AllocUndef(undef);
	    SetAll(g, REF, undef, MRBOFF);
	    ap[i] = x;
	}
    }
    while(i--){
	if(ap[i]){
	    *ap[i] = *g;
	}
	g--;
    }
    AllocVector2(g, 3);
    SetAll(v, VECTOR, g, MRBOFF); v++; g++;
    ptop = current_predicate2 ? current_predicate2 : current_predicate;
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(g, ATOM, mod, MRBOFF); g++;
	SetAll(g, ATOM, pred, MRBOFF); g++;
	SetAll(g, INT, arity, MRBOFF);
    }else{
	SetAll(g, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF); g++;
	SetAll(g, ATOM, GetPredicateName(ptop), MRBOFF); g++;
	SetAll(g, INT, GetPredicateArity(ptop), MRBOFF);
    }
    SetAll(v, REF, code, MRBOFF); v++;
    SetAll(v, REF, argv, MRBOFF);
    create_goal_and_wait_new_code(code, argv);
    unify_exception_with_report_stream(parent, &mesg,
				       exception_tag_table[excp_code]);
}


/*************************************************************************
*   Utility.								 *
*************************************************************************/

static create_goal_and_wait_new_code(code, argv)
    CELL *code, *argv;
{
    GOAL_RECORD *grec;
    GetGoalRecord(grec, 2);
    grec->parent = parent;
    grec->code = (OBJ *)dc_apply;
    grec->argn = 2;
    SetAll(&(grec->args[0]), REF, code, MRBOFF);
    SetAll(&(grec->args[1]), REF, argv, MRBOFF);
    SetGoalPriority(grec, INT, logical_priority);
    grec->debug = 0;
    grec->pcode = current_predicate2;
    number_of_children += 1;
    single_wait_suspend(grec, &(grec->args[0]));
}
