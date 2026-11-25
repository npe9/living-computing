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

#define	 GoalList(shoen)	 ((CELL *)((shoen)->number_of_children))
#define	 SetGoalList(shoen, x)	 ((shoen)->number_of_children) = (int)(x)
#define	 NextShoen(shoen)	 ((PARENT_RECORD *)((shoen)->reduction_left))
#define	 SetNextShoen(shoen, x)	 ((shoen)->reduction_left) = (int)(x)

int backtrace_flag;

static PARENT_RECORD *shoen_list_for_deadlock_detection;

static int deadlock_goal_merger_list;
#define DDROOT		 1
#define DDGOAL		 2
#define IsDeadlockGoal() ( deadlock_goal_merger_list&DDGOAL )
#define IsDeadlockRoot() ( deadlock_goal_merger_list&DDROOT )
#define MarkRoot()	 { deadlock_goal_merger_list |= DDROOT; }
#define SetDeadlockGoal(g){\
    (g)->debug = deadlock_goal_merger_list;\
    deadlock_goal_merger_list = ((int)(g))|DDGOAL;\
}
#define SetDeadlockMerger(m){\
    (m)->priority = deadlock_goal_merger_list;\
    deadlock_goal_merger_list = ((int)(m));\
}
#define GetDeadlockGoal(g){\
    g = (GOAL_RECORD *)(deadlock_goal_merger_list&0xFFFFFFFC);\
    deadlock_goal_merger_list = (g)->debug;\
}
#define GetDeadlockMerger(m){\
    m = (MERGER_RECORD *)(deadlock_goal_merger_list&0xFFFFFFFC);\
    deadlock_goal_merger_list = (m)->priority;\
}


/*************************************************************************
*   Detect Deadlock & Report -- Top Level.				 *
*************************************************************************/

deadlock_check_and_report()
{
    register GOAL_RECORD  *goal, *next, *deadgoals;
    register MERGER_RECORD  *merger, *nextmerger, *deadmergers;
    register PARENT_RECORD  *shoen, *new_shoen;
    register CELL  *cons, *vect, *undef, *args;
    register int  argn, f;

    /** Search deadlocked goals/mergers **/
    deadgoals = NULL;
    for(goal = goal_rec_list_old; goal != NULL; goal = next){
	next = goal->next;
	shoen = goal->parent;
	if(shoen != NULL && IsNotGrecCopied(goal)){
	    if(IsPrecCopied(shoen) && (!IsParentAborted(shoen))){
		/** goal in shoen is deadlocked **/
		goal->debug = 0;
		goal->next = deadgoals;
		deadgoals = goal;
	    }
	}
    }
    deadmergers = NULL;
    for(merger = merger_rec_list_old; merger != NULL; merger = nextmerger){
	nextmerger = merger->next;
	merger->input = NULL;
	if(merger->count != 0){
	    if(IsNotCopied(&(merger->output))){
		shoen = merger->parent;
		if(IsPrecCopied(shoen) && (!IsParentAborted(shoen))){
		    /** merger in shoen is deadlocked **/
		    argn = merger->count;
		    GcAllocNWords(vect, argn+1);
		    merger->input = vect;
		    SetAll(vect, DESC, argn, MRBOFF); vect++;
		    while(--argn >= 0){
			GcAlloc1Word(undef);
			SetAll(undef, UNDEF, MGHOK, MRBOFF);
			SetAll(vect+argn, REF, undef, MRBOFF);
		    }
		    merger->priority = 0;
		    merger->next = deadmergers;
		    deadmergers = merger;
		}
		merger->count = 0;
	    }
	}
    }

    /** Check dependency and search deadlock root **/
    for(goal = deadgoals; goal != NULL; goal = goal->next){
	argn = goal->argn;
	args = goal->args;
	while(argn--){
	    deadlock_mark_goals(args++, goal);
	}
    }
    for(merger = deadmergers; merger != NULL; merger = merger->next){
	deadlock_mark_goals(&(merger->output), NULL);
    }

    /** Make list of deadlocked goals/merger **/
    deadlock_goal_merger_list = -1;
    for(goal = deadgoals, f = -1; goal != NULL; goal = goal->next){
	if(goal->debug == 0){
	    goal->debug = -1;
	    argn = goal->argn;
	    args = goal->args;
	    while(argn--){
		deadlock_link_goals(args++, goal);
	    }
	    SetDeadlockGoal(goal);
	    MarkRoot();
	    f = 0;
	}
    }
    for(merger = deadmergers; merger != NULL; merger = merger->next){
	if(merger->priority == 0){
	    merger->priority = -1;
	    deadlock_link_goals(&(merger->output), NULL);
	    SetDeadlockMerger(merger);
	    MarkRoot();
	    f = 0;
	}
    }
    for(goal = deadgoals; goal != NULL; goal = goal->next){
	if((goal->debug&0xFFFFFFFC) == 0){
	    goal->debug = -1;
	    argn = goal->argn;
	    args = goal->args;
	    while(argn--){
		deadlock_link_goals(args++, goal);
	    }
	    SetDeadlockGoal(goal);
	}
    }
    for(merger = deadmergers; merger != NULL; merger = merger->next){
	if((merger->priority&0xFFFFFFFC) == 0){
	    merger->priority = -1;
	    deadlock_link_goals(&(merger->output), NULL);
	    SetDeadlockMerger(merger);
	}
    }

    /** Make report messages & Print **/
    initialize_print_routine();
    set_print_deadlock(YES);
    set_print_file(stdout);
    shoen_list_for_deadlock_detection = NULL;
    while(deadlock_goal_merger_list != -1){
	if(IsDeadlockGoal()){
	    if(IsDeadlockRoot()){
		f |= DDROOT;
		if(backtrace_flag){
		    printf("*** Next goal is deadlock root!\n");
		}
	    }
	    GetDeadlockGoal(goal);
	    deadlock_report_goal(goal, f);
	}else{
	    if(IsDeadlockRoot()){
		f |= DDROOT;
		if(backtrace_flag){
		    printf("*** Next merger is deadlock root!\n");
		}
	    }
	    GetDeadlockMerger(merger);
	    deadlock_report_merger(merger, f);
	}
	f = 0;
    }
    set_print_deadlock(NO);

    /** Unify to report stream of new shoen **/
    for(shoen = shoen_list_for_deadlock_detection; shoen != NULL;
						   shoen = NextShoen(shoen)){
	new_shoen = shoen->parent;
	new_shoen = search_parent_tag(new_shoen, DEADLOCK_TAG);
	if(new_shoen->parent != NULL && new_shoen->id != 0){
	    GcAlloc2Words(cons);
	    GcAllocNWords2(vect, 5);
	    GcAlloc1Word(undef);
	    SetAll(cons+0, VECTOR, vect, MRBOFF);
	    SetAll(cons+1, REF, undef, MRBOFF);
	    /** vect = deadlock(0, [], List-of-Goals) **/
	    SetAll(vect, DESC, 4, MRBOFF);
	    vect[1] = const_atom_deadlock;
	    SetAll(vect+2, INT, 0, MRBOFF);
	    vect[3] = const_nil;
	    SetAll(vect+4, LIST, GoalList(shoen), MRBOFF);
	    SetAll(undef, UNDEF, NULL, MRBON);
	    GcGetGoalRecord(goal, 2);
	    new_shoen->parent->number_of_children++;
	    goal->parent = new_shoen->parent;
	    goal->code = (OBJ *)dc_unify;
	    goal->argn = 2;
	    goal->args[0] = new_shoen->report;
	    SetAll(&(new_shoen->report), REF, undef, MRBOFF);
	    SetAll(&(goal->args[1]), LIST, cons, MRBOFF);
	    SetGoalPriority(goal, INT, new_shoen->parent->priority_max);
	    goal->debug = NO_TRACE_GOAL;
	    goal->pcode = NULL;
	    enqueue_with_priority(goal);
	}
    }
}


/*************************************************************************
*   Check Dependency and Search Deadlock Root.				 *
*************************************************************************/

static deadlock_mark_goals(c, goal0)
    CELL  *c;
    GOAL_RECORD	 *goal0;
{
    register CELL  *args, *c0;
    register GOAL_RECORD  *goal;
    register SUSPENSION_RECORD	*susp;
    register PARENT_RECORD  *shoen;
    register MERGER_RECORD  *merger;
    register int  argn;

    while(Typeof(c) == REF){
	c = Objectof(c);
	if(Typeof(c) == MGHOK){
	    if(IsCopied(c)) return;
	    merger = Mergerof(c);
	    if(merger->count != 0) return;
	    if(merger->priority != 0) return;
	    shoen = merger->parent;
	    if(IsNotPrecCopied(shoen) || IsParentAborted(shoen)) return;
	    /** merger in shoen is deadlocked **/
	    merger->priority = 1;
	    c = &(merger->output);
	    goal0 = NULL;
	}
    }
    if(Typeof(c) != HOOK && Typeof(c) != MHOOK) return;
    if(IsCopied(c)) return;
    if(goal0){
	c0 = c;
	for(;;){
	    if(Typeof(c0) == HOOK){
		goal = Goalof(c0);
		c0 = &(goal->pt);
	    }else if(Typeof(c0) == MHOOK){
		susp = Suspof(c0);
		goal = susp->suspended;
		c0 = &(susp->forward);
	    }else{
		break;
	    }
	    if(goal == goal0) return;  /** goal is self **/
	}
    }
    for(;;){
	if(Typeof(c) == HOOK){
	    goal = Goalof(c);
	    c = &(goal->pt);
	}else if(Typeof(c) == MHOOK){
	    susp = Suspof(c);
	    goal = susp->suspended;
	    c = &(susp->forward);
	}else{
	    return;
	}
	shoen = goal->parent;
	if(shoen == NULL || IsGrecCopied(goal)) continue;
	if(goal->debug != 0) continue;
	if(IsNotPrecCopied(shoen) || IsParentAborted(shoen)) continue;
	/** goal in shoen is deadlocked **/
	goal->debug = 1;
	argn = goal->argn;
	args = goal->args;
	while(argn--){
	    deadlock_mark_goals(args++, goal);
	}
    }
}


/*************************************************************************
*   Make Deadlocked Goal/Merger List.					 *
*************************************************************************/

static deadlock_link_goals(c, goal0)
    CELL  *c;
    GOAL_RECORD	 *goal0;
{
    register CELL  *args, *c0;
    register GOAL_RECORD  *goal;
    register SUSPENSION_RECORD	*susp;
    register PARENT_RECORD  *shoen;
    register MERGER_RECORD  *merger;
    register int  argn;

    while(Typeof(c) == REF) c = Objectof(c);
    if(Typeof(c) == MGHOK){
	if(IsCopied(c)) return;
	merger = Mergerof(c);
	if(merger->count != 0) return;
	if(merger->priority&0xFFFFFFFC) return;
	shoen = merger->parent;
	if(IsNotPrecCopied(shoen) || IsParentAborted(shoen)) return;
	/** merger in shoen is deadlocked **/
	merger->priority = -1;
	deadlock_link_goals(&(merger->output), NULL);
	SetDeadlockMerger(merger);
	return;
    }
    if(Typeof(c) != HOOK && Typeof(c) != MHOOK) return;
    if(IsCopied(c)) return;
    if(goal0){
	c0 = c;
	for(;;){
	    if(Typeof(c0) == HOOK){
		goal = Goalof(c0);
		c0 = &(goal->pt);
	    }else if(Typeof(c0) == MHOOK){
		susp = Suspof(c0);
		goal = susp->suspended;
		c0 = &(susp->forward);
	    }else{
		break;
	    }
	    if(goal == goal0) return;  /** goal is self **/
	}
    }
    for(;;){
	if(Typeof(c) == HOOK){
	    goal = Goalof(c);
	    c = &(goal->pt);
	}else if(Typeof(c) == MHOOK){
	    susp = Suspof(c);
	    goal = susp->suspended;
	    c = &(susp->forward);
	}else{
	    return;
	}
	shoen = goal->parent;
	if(shoen == NULL || IsGrecCopied(goal)) continue;
	if(goal->debug&0xFFFFFFFC) continue;
	if(IsNotPrecCopied(shoen) || IsParentAborted(shoen)) continue;
	/** goal in shoen is deadlocked **/
	goal->debug = -1;
	argn = goal->argn;
	args = goal->args;
	while(argn--){
	    deadlock_link_goals(args++, goal);
	}
	SetDeadlockGoal(goal);
    }
}


/*************************************************************************
*   Detect Deadlock & Report -- Sub Routines.				 *
*************************************************************************/

static deadlock_report_goal(goal, f)
    GOAL_RECORD	 *goal;
    int  f;
{
    register CELL  *func1, *func2, *cons, *goalarg, *vectarg;
    register PARENT_RECORD  *shoen, *new_shoen;
    register int  argn;
    unsigned int  mod, pred, arity;

    if(IsNativeCode(goal->code)){
	function_to_mod_pred_arity(goal->code, &mod, &pred, &arity);
    }else{
	mod = GetModuleName(GetModuleTop(goal->code));
	pred = GetPredicateName(goal->code);
    }
    shoen = goal->parent;
    GcAlloc2Words(cons);
    GcAllocNWords2(func1, 4);
    SetAll(cons, VECTOR, func1, MRBOFF);
    SetAll(func1, DESC, 3, MRBOFF);
    func1[1] = const_atom_colon;
    SetAll(func1+2, ATOM, mod, MRBOFF);
    if((argn = goal->argn) == 0){
	SetAll(func1+3, ATOM, pred, MRBOFF);
    }else{
	GcAllocNWords(func2, argn+2);
	SetAll(func1+3, VECTOR, func2, MRBOFF);
	SetAll(func2, DESC, argn+1, MRBOFF);
	SetAll(func2+1, ATOM, pred, MRBOFF);
	goalarg = goal->args;
	vectarg = func2+2;
	while(argn--){	/** Copy All Arguments (argn = Number of Arguments) **/
	    dead_cp_cell(goalarg, vectarg);
	    goalarg++; vectarg++;
	}
    }
    /** Display term to Console **/
    if(backtrace_flag || (f&DDROOT)){
	PrintCons1F("Deadlock::[%04d]", shoen->id);
	print_term2(cons, PRINT_LENGTH, PRINT_DEPTH);
	PrintCons("\n");
    }
    if(f){
	/** Make Code: {Module,PredName,Arity} **/
	func1[1] = func1[2];
	func1[2] = (goal->argn == 0) ? func1[3] : func2[1];
	SetAll(func1+3, INT, goal->argn, MRBOFF);
	/** Make list of deadlock message **/
	new_shoen = shoen->parent;
	if(new_shoen->parent != NULL  /** not(parent of grand mother) **/
	   && new_shoen->parent->parent != NULL){  /** not(grand mother) **/
	    if(GoalList(shoen) == NULL){
		cons[1] = const_nil;
		SetGoalList(shoen, cons);
		SetNextShoen(shoen, shoen_list_for_deadlock_detection);
		shoen_list_for_deadlock_detection = shoen;
	    }else{
		SetAll(cons+1, LIST, GoalList(shoen), MRBOFF);
		SetGoalList(shoen, cons);
	    }
	}
    }
}

static deadlock_report_merger(merger, f)
    MERGER_RECORD  *merger;
    int  f;
{
    register CELL  *func1, *func2, *cons, *out;
    register PARENT_RECORD  *shoen, *new_shoen;
    unsigned int  mod, pred, arity;

    shoen = merger->parent;
    GcAlloc2Words(cons);
    GcAllocNWords2(func1, 3);
    GcAllocNWords2(func2, 4);
    GcAlloc1Word(out);
    SetAll(func1, DESC, 2, MRBOFF);
    SetAll(func2, DESC, 3, MRBOFF);
    SetAll(cons, VECTOR, func1, MRBOFF);
    func1[1] = const_atom_merge;
    SetAll(func1+2, VECTOR, func2, MRBOFF);
    if(IsNativeCode(merger->pcode)){
	function_to_mod_pred_arity(merger->pcode, &mod, &pred, &arity);
    }else{
	mod = GetModuleName(GetModuleTop(merger->pcode));
	pred = GetPredicateName(merger->pcode);
	arity = GetPredicateArity(merger->pcode);
    }
    SetAll(func2+1, ATOM, mod, MRBOFF);
    SetAll(func2+2, ATOM, pred, MRBOFF);
    SetAll(func2+3, INT, arity, MRBOFF);
    dead_cp_cell(&(merger->output), out);
    /** Display term to Console **/
    SetAll(cons+1, VECTOR, merger->input, MRBOFF);
    if(backtrace_flag || (f&DDROOT)){
	PrintCons1F("Deadlock::[%04d]merge(", shoen->id);
	print_term2(cons+1, PRINT_LENGTH, PRINT_DEPTH);
	PrintCons(",");
	print_term2(out, PRINT_LENGTH, PRINT_DEPTH);
	PrintCons3F(") in %s:%s/%d\n", atom_name(mod), atom_name(pred), arity);
    }
    if(f){
	/** Make list of deadlock message **/
	new_shoen = shoen->parent;
	if(new_shoen->parent != NULL  /** not(parent of grand mother) **/
	   && new_shoen->parent->parent != NULL){  /** not(grand mother) **/
	    if(GoalList(shoen) == NULL){
		cons[1] = const_nil;
		SetGoalList(shoen, cons);
		SetNextShoen(shoen, shoen_list_for_deadlock_detection);
		shoen_list_for_deadlock_detection = shoen;
	    }else{
		SetAll(cons+1, LIST, GoalList(shoen), MRBOFF);
		SetGoalList(shoen, cons);

	    }
	}
    }
}


/*************************************************************************
*   Copy CELL in Deadlocked Goal.					 *
*************************************************************************/

static dead_cp_cell(old, new)
    register CELL  *old, *new;
{
    register CELL  *work, *next;
    CELL  wcell;
    int	 leng, len2;

    for(;;){
	switch(Typeof(old)){
	  case ATOM:
	    SetAll(new, ATOM, Valueof(old), MRBOFF);
	    return;
	  case INT:
	    SetAll(new, INT, Valueof(old), MRBOFF);
	    return;
	  case FLOAT:
	    SetAll(new, FLOAT, Valueof(old), MRBOFF);
	    return;
	  case REF:
	    work = Objectof(old);
	    switch(Typeof(work)){
	      case UNDEF:
	      case HOOK:
	      case MHOOK:
		/** REF->UNBOUND No.1 **/
		/** OLD-UNBOUND := Pointer to NEW-REF, MRB=OFF **/
		SetOldNewPointer1(work, new);
		GcAlloc1Word(next);
		SetAll(new, REF, next, MRBOFF);
		SetAll(next, UNDEF, NULL, MRBOFF);
		return;
	      case MGHOK:
		/** REF->MHOOK No.1 **/
		/** OLD-MHOOK := Pointer to NEW-REF, MRB=OFF **/
		wcell = *work;
		SetOldNewPointer1(work, new);
		dead_cp_stream_merger(Mergerof(&wcell), new);
		return;
	      case COPIED:
		next = Objectof(work); /* REF No.1 in new heap */
		switch(Typeof(Objectof(next))){
		  case UNDEF:
		  case MHOOK:
		    if(Mrbof(work) == MRBOFF){
			/** REF->UNDEF/MHOOK No.2 **/
			/** OLD-UNDEF := Pointer to NEW-REF, MRB=ON **/
			MarkOldNewPointer(work);
			next = Objectof(next);
			SetAll(new, REF, next, MRBOFF);
			SetMrbof(next, MRBON);
			return;
		    }else{
			/** REF->UNDEF No.3 **/
			SetMrbof(next, MRBON); /** Mark REF No.1 **/
			next = Objectof(next);
			SetAll(new, REF, next, MRBON);
			return;
		    }
		  case HOOK:
		    if(Mrbof(work) == MRBOFF){
			/** REF->HOOK No.2 **/
			/** OLD-HOOK := Pointer to NEW-REF, MRB=ON **/
			MarkOldNewPointer(work);
			next = Objectof(next);
			SetAll(new, REF, next, MRBOFF);
			return;
		    }else{
			/** REF->HOOK No.3 **/
			SetMrbof(next, MRBON); /** Mark REF No.1 **/
			next = Objectof(next);
			SetAll(new, REF, next, MRBON);
			SetMrbof(next, MRBON);
			return;
		    }
		  case MGHOK:
		    if(Mrbof(work) == MRBOFF){
			/** REF->MGHOK No.2 **/
			/** OLD-MGHOK := Pointer to NEW-REF, MRB=ON **/
			MarkOldNewPointer(work);
			SetMrbof(next, MRBON);  /** Mark REF No.1 **/
			next = Objectof(next);
			SetAll(new, REF, next, MRBON);
			SetMrbof(next, MRBON);
			return;
		    }else{
			/** REF->MGOOK No.3 **/
			next = Objectof(next);
			SetAll(new, REF, next, MRBON);
			return;
		    }
		}
	      DEFAULT:
		old = work;  /** Dereference **/
		continue;    /** TRO: dead_cp_cell(old, new) **/
	    }
	  case LIST:
	    work = Objectof(old);
	    if(IsConstInCode(work)){
		if(IsConstInNativeCode(work)){
		    /** Structure Constant in Native Code **/
		    SetAll(new, LIST, work, MRBON);
		}else{
		    /** Structure Constant in Code Area **/
		    SetAll(new, LIST, GcConstInCode(work), MRBON);
		}
		return;
	    }
	    if(IsNotCopied(work)){
		/** LIST No.1 **/
		/** OLD-CAR := Pointer to NEW-REF, MRB=OFF **/
		wcell = work[0];  /** CAR **/
		SetOldNewPointer1(work, new);
		GcAlloc2Words(next);
		SetAll(new, LIST, next, MRBOFF);
		dead_cp_cell(&wcell, &next[0]);	 /** GC CAR **/
		old = &work[1];	    /** GC CDR **/
		new = &next[1];	    /** TRO: dead_cp_cell(old, new) **/
		continue;
	    }
	    if(Mrbof(work) == MRBOFF){
		/** LIST No.2 **/
		/** OLD-CAR := Pointer to NEW-CONS, MRB=ON **/
		next = Objectof(work);
		SetMrbof(next, MRBON);	/** Mark LIST No.1 **/
		next = Objectof(next);
		SetOldNewPointer2(work,next);
		SetAll(new, LIST, next, MRBON);
		return;
	    }else{
		/** LIST No.3 **/
		next = Objectof(work);
		SetAll(new, LIST, next, MRBON);
		return;
	    }
	  case VECTOR:
	    work = Objectof(old);
	    if(IsConstInCode(work)){
		if(IsConstInNativeCode(work)){
		    /** Structure Constant in Native Code **/
		    SetAll(new, VECTOR, work, MRBON);
		}else{
		    /** Structure Constant in Code Area **/
		    SetAll(new, VECTOR, GcConstInCode(work), MRBON);
		}
		return;
	    }
	    if(IsNotCopied(work)){
		/** VECTOR No.1 **/
		/** OLD-DESC := Pointer to NEW-REF, MRB=OFF **/
		leng = Valueof(work)&0xFFFFFF;
		SetOldNewPointer1(work, new);
		GcAllocNWords(next, leng+1);
		SetAll(new, VECTOR, next, MRBOFF);
		SetAll(next, DESC, leng, MRBOFF);
		while(leng--){
		    work++; next++;
		    dead_cp_cell(work, next);
		}
		return;
	    }
	    if(Mrbof(work) == MRBOFF){
		/** VECTOR No.2 **/
		/** OLD-DESC := Pointer to NEW-VECTOR-BODY, MRB=ON **/
		next = Objectof(work);
		SetMrbof(next, MRBON);	/** Mark VECTOR No.1 **/
		next = Objectof(next);
		SetOldNewPointer2(work, next);
		SetAll(new, VECTOR, next, MRBON);
		return;
	    }else{
		/** VECTOR No.3 **/
		next = Objectof(work);
		SetAll(new, VECTOR, next, MRBON);
		return;
	    }
	  case STRING:
	    work = Objectof(old);
	    if(IsConstInCode(work)){
		if(IsConstInNativeCode(work)){
		    /** Structure Constant in Native Code **/
		    SetAll(new, STRING, work, MRBON);
		}else{
		    /** Structure Constant in Code Area **/
		    SetAll(new, STRING, GcConstInCode(work), MRBON);
		}
		return;
	    }
	    if(IsNotCopied(work)){
		/** STRING No.1 **/
		/** OLD-DESC := Pointer to NEW-REF, MRB=OFF **/
		leng = Valueof(work);
		SetOldNewPointer1(work, new);
		GcAllocNWords(next, (leng&0xFFFFFF)+1);
		SetAll(new, STRING, next, MRBOFF);
		SetAll(next, DESC, leng, MRBOFF);
		leng &= 0xFFFFFF;
		while(leng--){
		    next++; work++;
		    *next = *work;
		}
		return;
	    }
	    if(Mrbof(work) == MRBOFF){
		/** STRING No.2 **/
		/** OLD-DESC := Pointer to NEW-STRING-BODY, MRB=ON **/
		next = Objectof(work);
		SetMrbof(next, MRBON);	/** Mark STRING No.1 **/
		next = Objectof(next);
		SetOldNewPointer2(work, next);
		SetAll(new, STRING, next, MRBON);
		return;
	    }else{
		/** STRING No.3 **/
		next = Objectof(work);
		SetAll(new, STRING, next, MRBON);
		return;
	    }
	  case NUE:
	    work = Objectof(old);
	    if(IsNotCopied(work)){
		/** NUE No.1 **/
		leng = Valueof(work)&0xFFFFFF;
		len2 = (Valueof(work)>>24)&0xFF;
		SetOldNewPointer1(work, new);
		GcAllocNWords(next, leng+1);
		SetAll(new, NUE, next, MRBOFF);
		SetAll(next, DESC, (len2<<24)|leng, MRBOFF);
		leng -= len2;
		while(len2--){
		    work++; next++;
		    dead_cp_cell(work, next);
		}
		while(leng--){
		    next++; work++;
		    *next = *work;
		}
		return;
	    }
	    if(Mrbof(work) == MRBOFF){
		/** NUE No.2 **/
		next = Objectof(work);
		SetMrbof(next, MRBON);	/** Mark NUE No.1 **/
		next = Objectof(next);
		SetOldNewPointer2(work, next);
		SetAll(new, NUE, next, MRBON);
		return;
	    }else{
		/** NUE No.3 **/
		next = Objectof(work);
		SetAll(new, NUE, next, MRBON);
		return;
	    }
	  case SHOEN:
	    /** SHOEN -> '$SHOEN'(Shoen-ID) **/
	    GcAllocNWords2(next, 3);
	    SetAll(new, VECTOR, next, MRBOFF);
	    SetAll(next, DESC, 2, MRBOFF);
	    next[1] = const_atom_d_shoen;
	    SetAll(next+2, INT, Shoenof(old)->id, MRBOFF);
	    return;
	  DEFAULT:
	    Error2F("Unknown Data Type (%02x  AD:%08x)\n", Typeof(old), old);
	    new = old;
	    return;
	}
    }
}

static dead_cp_stream_merger(oldmg, newref)
    register MERGER_RECORD *oldmg;
    CELL *newref;
{
    register CELL *new, *v;
    CELL wcell;
    register int i;
    if(oldmg->input){
	v = oldmg->input;
	for(i=1; i<=Valueof(v); i++){
	    if(Mrbof(Objectof(v+i)) == MRBOFF){
		new = Objectof(v+i);
		SetMrbof(new, MRBON);
		SetAll(newref, REF, new, MRBOFF);
		break;
	    }
	}
    }else{
	GcAlloc1Word(new);
	SetAll(newref, REF, new, MRBOFF);
	if(oldmg->count != 0){
	    SetAll(new, MGHOK, Mergerof(&(oldmg->output)), MRBON);
	}else{
	    SetAll(new, UNDEF, UNDEF, MRBOFF);
	}
    }
}


/*************************************************************************
*   Terminate Shoen by GC.						 *
*************************************************************************/

terminate_shoen_by_gc()
{
    PARENT_RECORD  *prec, *next;
    for(prec = grand_mother->left_son; prec != grand_mother; prec = next){
	next = prec->right_brother;
	terminate_shoen_without_child(prec);
    }
}

static terminate_shoen_without_child(prec)
    PARENT_RECORD  *prec;
{
    if(prec->number_of_children2 == 0){
	if(prec->status != ABORTED){
	    CacheParent(prec);
	    PrintCons("Shoen is terminated by deadlock!\n");
	    terminate_shoen();
	}
    }else{
	PARENT_RECORD  *son, *next;
	for(son = prec->left_son; son != prec; son = next){
	    next = son->right_brother;
	    terminate_shoen_without_child(son);
	}
    }
}
