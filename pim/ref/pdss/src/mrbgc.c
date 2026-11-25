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
static int collect_value_sub();
static int detect_deadlock_by_collect_value_sub();
static int is_deadlock_occurred_really();
static int display_deadlock_suspended_goals();
static int display_deadlock_suspended_goal();
static int report_deadlock_suspended_goals();
static int report_deadlock_suspended_goal();
static int report_deadlock_suspended_merger();



/*************************************************************************
*   Collect Value.							 *
*************************************************************************/

#if MRBGC_SWITCH
#if EAGER_DEADLOCK_DETECTION

collect_value(c, d)
    CELL *c;
    int d;
{
    initialize_print_routine();
    collect_value_sub(c, d);
}

static collect_value_sub(c, d)
    CELL *c;
    int d;
{
    int n;
    OBJ *pt = current_predicate;
    switch(Typeof(c)){
      case REF:
	if(Mrbof(c) == MRBON) return;
	c = Objectof(c);
	if(--d >= 0) collect_value_sub(c, d);
	if(Mrbof(c) == MRBOFF && !IsUnbound(c)){
	    FreeCell(c);
	    mrbgc_statistics_collect_value(1);
	}
	return;
      case LIST:
	if(Mrbof(c) == MRBON) return;
	c = Objectof(c);
	if(--d >= 0){
	    collect_value_sub(c, d);
	    collect_value_sub(c+1, d);
	}
	FreeCons(c);
	mrbgc_statistics_collect_value(2);
	return;
      case VECTOR:
	if(Mrbof(c) == MRBON) return;
	n = VectorLengthof(c);
	c = Objectof(c);
	if(--d >= 0){
	    CELL *p = c;
	    int m = n;
	    while(m--){
		collect_value_sub(++p, d);
	    }
	}
	FreeVector(c, n);
	mrbgc_statistics_collect_value(n+1);
	return;
      case STRING:
	if(Mrbof(c) == MRBON) return;
	n = StringLengthof(c);
	c = Objectof(c);
	FreeString(c, n);
	mrbgc_statistics_collect_value(n+1);
	return;
      case UNDEF:
	SetMrbof(c, MRBOFF);
	return;
      case HOOK:
	if(Mrbof(c) == MRBON) return;
	if(!is_deadlock_occurred_really(c)) return;
	PrintCons("\n\
*** Deadlock occurred. [collect(HOOKoo)]\n\
*** A variable which has a goal waiting for instantiation was abandoned.\n");
	if(IsNativeCode(pt)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(pt, &mod, &pred, &arity);
	    PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(pt))),
			atom_name(GetPredicateName(pt)),
			GetPredicateArity(pt));
	}
	display_deadlock_suspended_goals(c);
	report_deadlock_suspended_goals(COLLECT_HOOK, c, pt);
	return;
      case MGHOK:
	if(!is_deadlock_occurred_really(c)) return;
	PrintCons("\n\
*** Deadlock will occur. [collect(MGHOKo)]\n\
*** A merger input variable was abandoned.\n");
	if(IsNativeCode(pt)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(pt, &mod, &pred, &arity);
	    PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(pt))),
			atom_name(GetPredicateName(pt)),
			GetPredicateArity(pt));
	}
	display_deadlock_suspended_goals(c);
	report_deadlock_suspended_goals(COLLECT_MGHK, c, pt);
	return;
      DEFAULT:
	return;
    }
}

#else

collect_value(c, d)
    CELL *c;
    int d;
{
    int n;
    if(Mrbof(c) == MRBON) return;
    switch(Typeof(c)){
      case REF:
	c = Objectof(c);
	if(--d >= 0) collect_value(c, d);
	if(Mrbof(c) == MRBOFF && !IsUnbound(c)){
	    FreeCell(c);
	    mrbgc_statistics_collect_value(1);
	}
	return;
      case LIST:
	c = Objectof(c);
	if(--d >= 0){
	    collect_value(c, d);
	    collect_value(c+1, d);
	}
	FreeCons(c);
	mrbgc_statistics_collect_value(2);
	return;
      case VECTOR:
	n = VectorLengthof(c);
	c = Objectof(c);
	if(--d >= 0){
	    CELL *p = c;
	    int m = n;
	    while(m--){
		collect_value(++p, d);
	    }
	}
	FreeVector(c, n);
	mrbgc_statistics_collect_value(n+1);
	return;
      case STRING:
	n = StringLengthof(c);
	c = Valueof(c);
	FreeString(c, n);
	mrbgc_statistics_collect_value(n+1);
	return;
      DEFAULT:
	return;
    }
}

#endif
#else
#if EAGER_DEADLOCK_DETECTION

detect_deadlock_by_collect_value(c, d)
    CELL *c;
    int d;
{
    initialize_print_routine();
    detect_deadlock_by_collect_value_sub(c, d);
}

static detect_deadlock_by_collect_value_sub(c, d)
    CELL *c;
    int d;
{
    int n;
    OBJ *pt = current_predicate;
    for(;;){
	switch(Typeof(c)){
	  case REF:
	    if(Mrbof(c) == MRBON) return;
	    if(--d < 0) return;
	    c = Objectof(c);
	    continue;
	  case LIST:
	    if(Mrbof(c) == MRBON) return;
	    if(--d < 0) return;
	    c = Objectof(c);
	    detect_deadlock_by_collect_value_sub(c++, d);
	    continue;
	  case VECTOR:
	    if(Mrbof(c) == MRBON) return;
	    if(--d < 0) return;
	    c = Objectof(c);
	    n = VectorLengthof(c);
	    while(n--) detect_deadlock_by_collect_value_sub(++c, d);
	    return;
	  case UNDEF:
	    SetMrbof(c, MRBOFF);
	    return;
	  case HOOK:
	    if(Mrbof(c) == MRBON) return;
	    if(!is_deadlock_occurred_really(c)) return;
	    PrintCons("\n\
*** Deadlock occurred. [collect(HOOKoo)]\n\
*** A variable which has a goal waiting for instantiation was abandoned.\n");
	    if(IsNativeCode(pt)){
		unsigned int mod, pred, arity;
		function_to_mod_pred_arity(pt, &mod, &pred, &arity);
		PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			    atom_name(mod), atom_name(pred), arity);
	    }else{
		PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			    atom_name(GetModuleName(GetModuleTop(pt))),
			    atom_name(GetPredicateName(pt)),
			    GetPredicateArity(pt));
	    }
	    display_deadlock_suspended_goals(c);
	    report_deadlock_suspended_goals(COLLECT_HOOK, c, pt);
	    return;
	  case MGHOK:
	    if(!is_deadlock_occurred_really(c)) return;
	    PrintCons("\n\
*** Deadlock will occur. [collect(MGHOKo)]\n\
*** A merger input variable was abandoned.\n");
	    if(IsNativeCode(pt)){
		unsigned int mod, pred, arity;
		function_to_mod_pred_arity(pt, &mod, &pred, &arity);
		PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			    atom_name(mod), atom_name(pred), arity);
	    }else{
		PrintCons3F("*** Collect_value occurred in %s:%s/%d\n",
			    atom_name(GetModuleName(GetModuleTop(pt))),
			    atom_name(GetPredicateName(pt)),
			    GetPredicateArity(pt));
	    }
	    display_deadlock_suspended_goals(c);
	    report_deadlock_suspended_goals(COLLECT_MGHOK, c, pt);
	    return;
	  DEFAULT:
	    return;
	}
    }
}

#endif
#endif


/*************************************************************************
*   Eager Deadlock Detection by Suspend.				 *
*************************************************************************/
#if EAGER_DEADLOCK_DETECTION

detect_deadlock_in_suspension(type, goal, c)
    int type;
    GOAL_RECORD *goal;
    CELL *c;
{
    OBJ *ptop = current_predicate2 ? current_predicate2 : current_predicate;
    initialize_print_routine();
    if(Typeof(c) == UNDEF){
	PrintCons("\n\
*** Deadlock occurred. [suspend(UNDEFoo)]\n\
*** Waiting for instantiation of a void variable.\n");
	display_deadlock_suspended_goal(goal);
	report_deadlock_suspended_goal(type, goal, ptop);
    }else if(Typeof(c) == HOOK){
	PrintCons("\n\
*** Deadlock occurred. [suspend(HOOKoo)]\n\
*** Waiting for instantiation of a variable which never be instantiated.\n");
	display_deadlock_suspended_goal(goal);
	display_deadlock_suspended_goals(c);
	report_deadlock_suspended_goal(type, goal, ptop);
	report_deadlock_suspended_goals(type, c, ptop);
    }else{  /* MGHOK */
	PrintCons("\n\
*** Deadlock occurred. [suspend(MGHOKo)]\n\
*** Waiting for instantiation of a merger input variable.\n");
	display_deadlock_suspended_goal(goal);
	display_deadlock_suspended_goals(c);
	report_deadlock_suspended_goal(type, goal, ptop);
	report_deadlock_suspended_goals(type, c, ptop);
    }
}

#endif

/*************************************************************************
*   Eager Deadlock Detection by Unification.				 *
*************************************************************************/
#if EAGER_DEADLOCK_DETECTION

detect_deadlock_in_unification1(x)
    CELL *x;
{
    OBJ *ptop = current_predicate2 ? current_predicate2 : current_predicate;
    if(!is_deadlock_occurred_really(x)) return;
    initialize_print_routine();
    if(Typeof(x) == HOOK){
	PrintCons("\n\
*** Deadlock occurred. [unify(HOOKoo,VOID)]\n\
*** A variable which has a goal waiting for instantiation is unified with\n\
*** a void variable.\n");
	if(IsNativeCode(ptop)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(ptop))),
			atom_name(GetPredicateName(ptop)),
			GetPredicateArity(ptop));
	}
	display_deadlock_suspended_goals(x);
	report_deadlock_suspended_goals(UNIFY_VOID_HOOK, x, ptop);
	return;
    }
    if(Typeof(x) == MGHOK){
	PrintCons("\n\
*** Deadlock will occur. [unify(MGHOKo,VOID)]\n\
*** A merger input variable is unified with a void variable.\n");
	if(IsNativeCode(ptop)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(ptop))),
			atom_name(GetPredicateName(ptop)),
			GetPredicateArity(ptop));
	}
	display_deadlock_suspended_goals(x);
	report_deadlock_suspended_goals(UNIFY_VOID_HOOK, x, ptop);
	return;
    }
}

detect_deadlock_in_unification2(x, y)
    CELL *x, *y;
{
    CELL *z;
    OBJ *ptop = current_predicate2 ? current_predicate2 : current_predicate;
    if(!is_deadlock_occurred_really(x) &&
       !is_deadlock_occurred_really(y)) return;
    initialize_print_routine();
    if(Typeof(x) == HOOK && Typeof(y) == HOOK){
	PrintCons("\n\
*** Deadlock occurred. [unify(HOOKoo,HOOKoo)]\n\
*** Unifying two variables which have goals waiting for instantiation.\n");
	if(IsNativeCode(ptop)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(ptop))),
			atom_name(GetPredicateName(ptop)),
			GetPredicateArity(ptop));
	}
	display_deadlock_suspended_goals(x);
	display_deadlock_suspended_goals(y);
	report_deadlock_suspended_goals(UNIFY_HOOK_HOOK, x, ptop);
	report_deadlock_suspended_goals(UNIFY_HOOK_HOOK, y, ptop);
	return;
    }
    if(Typeof(y) == HOOK) { z=x; x=y; y=z; }
    if(Typeof(x) == HOOK && Typeof(y) == MGHOK){
	PrintCons("\n\
*** Deadlock occurred. [unify(HOOKoo,MGHOKo)]\n\
*** Unifying variable which has a goal waiting for instantiation is unified\n\
*** and a merger input variable.\n");
	if(IsNativeCode(ptop)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(ptop))),
			atom_name(GetPredicateName(ptop)),
			GetPredicateArity(ptop));
	}
	display_deadlock_suspended_goals(x);
	display_deadlock_suspended_goals(y);
	report_deadlock_suspended_goals(UNIFY_HOOK_MGHK, x, ptop);
	report_deadlock_suspended_goals(UNIFY_HOOK_MGHK, y, ptop);
	return;
    }
    if(Typeof(x) == MGHOK && Typeof(y) == MGHOK){
	PrintCons("\n\
*** Deadlock will occur. [unify(MGHOKo,MGHOKo)]\n\
*** Unifying two merger input variables.\n");
	if(IsNativeCode(ptop)){
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(mod), atom_name(pred), arity);
	}else{
	    PrintCons3F("*** Unification occurred in %s:%s/%d\n",
			atom_name(GetModuleName(GetModuleTop(ptop))),
			atom_name(GetPredicateName(ptop)),
			GetPredicateArity(ptop));
	}
	display_deadlock_suspended_goals(x);
	display_deadlock_suspended_goals(y);
	report_deadlock_suspended_goals(UNIFY_MGHK_MGHK, x, ptop);
	report_deadlock_suspended_goals(UNIFY_MGHK_MGHK, y, ptop);
	return;
    }
}

#endif

/*************************************************************************
*   Eager Deadlock Detection -- Subroutines.				 *
*************************************************************************/
#if EAGER_DEADLOCK_DETECTION

static int is_deadlock_occurred_really(c)
    CELL *c;
{
    if(Typeof(c) == MGHOK){
	MERGER_RECORD *mg;
	mg = Mergerof(c);
	if(!IsParentAborted(mg->parent)) return(YES);
    }else{
	GOAL_RECORD *hgr;
	SUSPENSION_RECORD *sr;
	for(;;){
	    if(Typeof(c) == HOOK){
		hgr = Goalof(c);
		if(!IsParentAborted(hgr->parent)) return(YES);
		c = &(hgr->pt);
	    }else if(Typeof(c) == MHOOK){
		sr = Suspof(c);
		c = &(sr->forward);
	    }else{
		break;
	    }
	}
    }
    return(NO);
}

static display_deadlock_suspended_goals(c)
    CELL *c;
{
    if(Typeof(c) == MGHOK){
	MERGER_RECORD *mg;
	CELL tmp;
	for(;;){
	    mg = Mergerof(c);
	    if(IsParentAborted(mg->parent)) return;
	    SetAll(&tmp, REF, c, MRBOFF);
	    PrintCons1F("[%04d]merge(", mg->parent->id);
	    print_term2(&tmp, 10, 10);
	    PrintCons(",");
	    print_term2(&(mg->output), 10, 10);
	    if(IsNativeCode(mg->pcode)){
		unsigned int mod, pred, arity;
		function_to_mod_pred_arity(mg->pcode, &mod, &pred, &arity);
		PrintCons3F(") in %s:%s/%d\n",
			    atom_name(mod), atom_name(pred), arity);
	    }else{
		PrintCons3F(") in %s:%s/%d\n",
			    atom_name(GetModuleName(GetModuleTop(mg->pcode))),
			    atom_name(GetPredicateName(mg->pcode)),
			    GetPredicateArity(mg->pcode));
	    }
	    Dereference2(&(mg->output), c);
	    if(Typeof(c) != MGHOK) break;
	}
	if(Typeof(c) != HOOK) return;
	if(!is_deadlock_occurred_really(c)) return;
    }
    {
	GOAL_RECORD *hgr;
	SUSPENSION_RECORD *sr;
	for(;;){
	    if(Typeof(c) == HOOK){
		hgr = Goalof(c);
		if(!IsParentAborted(hgr->parent)){
		    display_deadlock_suspended_goal(hgr);
		}
		c = &(hgr->pt);
	    }else if(Typeof(c) == MHOOK){
		sr = Suspof(c);
		c = &(sr->forward);
	    }else{
		break;
	    }
	}
    }
}

static display_deadlock_suspended_goal(goal)
    GOAL_RECORD *goal;
{
    write_goal_record(goal);
}

static report_deadlock_suspended_goals(type, c, ptop)
    int type;
    CELL *c;
    OBJ *ptop;
{
    if(Typeof(c) == MGHOK){
	MERGER_RECORD *mg;
	for(;;){
	    mg = Mergerof(c);
	    if(IsParentAborted(mg->parent)) return;
	    report_deadlock_suspended_merger(type, mg, ptop);
	    Dereference2(&(mg->output), c);
	    if(Typeof(c) != MGHOK) break;
	}
	if(Typeof(c) != HOOK) return;
	if(!is_deadlock_occurred_really(c)) return;
    }
    {
	GOAL_RECORD *hgr;
	SUSPENSION_RECORD *sr;
	for(;;){
	    if(Typeof(c) == HOOK){
		hgr = Goalof(c);
		if(!IsParentAborted(hgr->parent))
		    report_deadlock_suspended_goal(type, hgr, ptop);
		c = &(hgr->pt);
	    }else if(Typeof(c) == MHOOK){
		sr = Suspof(c);
		c = &(sr->forward);
	    }else{
		break;
	    }
	}
    }
}

static report_deadlock_suspended_goal(type, grec, ptop)
    int type;
    GOAL_RECORD *grec;
    OBJ *ptop;
{
    CELL *info, *v1, *v2, *ls, *cons, *undef;
    GOAL_RECORD *goal;
    PARENT_RECORD *shoen;

    AllocVector2(v1, 3);
    if(IsNativeCode(grec->code)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(grec->code, &mod, &pred, &arity);
	SetAll(v1+1, ATOM, mod, MRBOFF);
	SetAll(v1+2, ATOM, pred, MRBOFF);
    }else{
	SetAll(v1+1, ATOM, GetModuleName(GetModuleTop(grec->code)), MRBOFF);
	SetAll(v1+2, ATOM, GetPredicateName(grec->code), MRBOFF);
    }
    SetAll(v1+3, INT, grec->argn, MRBOFF);

    AllocCons(ls);
    SetAll(ls+0, VECTOR, v1, MRBOFF);
    SetAll(ls+1, ATOM, NIL, MRBOFF);

    AllocVector2(v2, 3);
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(v2+1, ATOM, mod, MRBOFF);
	SetAll(v2+2, ATOM, pred, MRBOFF);
	SetAll(v2+3, INT, arity, MRBOFF);
    }else{
	SetAll(v2+1, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF);
	SetAll(v2+2, ATOM, GetPredicateName(ptop), MRBOFF);
	SetAll(v2+3, INT, GetPredicateArity(ptop), MRBOFF);
    }

    AllocVector2(info, 4);
    info[1] = const_atom_deadlock;
    SetAll(info+2, INT, type, MRBOFF);
    SetAll(info+3, VECTOR, v2, MRBOFF);
    SetAll(info+4, LIST, ls, MRBOFF);

    shoen = search_parent_tag(grec->parent, DEADLOCK_TAG);
    if(shoen->parent != NULL){
	AllocCons(cons);
	AllocUndef(undef);
	SetAll(cons+0, VECTOR, info, MRBOFF);
	SetAll(cons+1, REF, undef, MRBOFF);
	GetGoalRecord(goal, 2);
	shoen->parent->number_of_children++;
	goal->parent = shoen->parent;
	goal->code = (OBJ *)dc_unify;
	goal->argn = 2;
	goal->args[0] = shoen->report;
	SetAll(&(shoen->report), REF, undef, MRBOFF);
	SetAll(&(goal->args[1]), LIST, cons, MRBOFF);
	SetGoalPriority(goal, INT, shoen->parent->priority_max);
	goal->debug = NO_TRACE_GOAL;
	goal->pcode = NULL;
	enqueue_with_priority(goal);
    }
}

static report_deadlock_suspended_merger(type, mg, ptop)
    int type;
    MERGER_RECORD *mg;
    OBJ *ptop;
{
    CELL *info, *v1, *v2, *ls, *cons, *undef;
    GOAL_RECORD *goal;
    PARENT_RECORD *shoen;

    AllocVector2(v1, 2);
    AllocVector2(v2, 3);
    v1[1] = const_atom_merge;
    SetAll(v1+2, VECTOR, v2, MRBOFF);
    if(IsNativeCode(mg->pcode)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(v2+1, ATOM, mod, MRBOFF);
	SetAll(v2+2, ATOM, pred, MRBOFF);
	SetAll(v2+3, INT, arity, MRBOFF);
    }else{
	SetAll(v2+1, ATOM, GetModuleName(GetModuleTop(mg->pcode)), MRBOFF);
	SetAll(v2+2, ATOM, GetPredicateName(mg->pcode), MRBOFF);
	SetAll(v2+3, INT, GetPredicateArity(mg->pcode), MRBOFF);
    }
    AllocCons(ls);
    SetAll(ls+0, VECTOR, v1, MRBOFF);
    SetAll(ls+1, ATOM, NIL, MRBOFF);

    AllocVector2(v2, 3);
    if(IsNativeCode(ptop)){
	unsigned int mod, pred, arity;
	function_to_mod_pred_arity(ptop, &mod, &pred, &arity);
	SetAll(v2+1, ATOM, mod, MRBOFF);
	SetAll(v2+2, ATOM, pred, MRBOFF);
	SetAll(v2+3, INT, arity, MRBOFF);
    }else{
	SetAll(v2+1, ATOM, GetModuleName(GetModuleTop(ptop)), MRBOFF);
	SetAll(v2+2, ATOM, GetPredicateName(ptop), MRBOFF);
	SetAll(v2+3, INT, GetPredicateArity(ptop), MRBOFF);
    }

    AllocVector2(info, 4);
    info[1] = const_atom_deadlock;
    SetAll(info+2, INT, type, MRBOFF);
    SetAll(info+3, VECTOR, v2, MRBOFF);
    SetAll(info+4, LIST, ls, MRBOFF);

    shoen = search_parent_tag(mg->parent, DEADLOCK_TAG);
    if(shoen->parent != NULL){
	AllocCons(cons);
	AllocUndef(undef);
	SetAll(cons+0, VECTOR, info, MRBOFF);
	SetAll(cons+1, REF, undef, MRBOFF);
	GetGoalRecord(goal, 2);
	shoen->parent->number_of_children++;
	goal->parent = shoen->parent;
	goal->code = (OBJ *)dc_unify;
	goal->argn = 2;
	goal->args[0] = shoen->report;
	SetAll(&(shoen->report), REF, undef, MRBOFF);
	SetAll(&(goal->args[1]), LIST, cons, MRBOFF);
	SetGoalPriority(goal, INT, shoen->parent->priority_max);
	goal->debug = NO_TRACE_GOAL;
	goal->pcode = NULL;
	enqueue_with_priority(goal);
    }
}

#endif
