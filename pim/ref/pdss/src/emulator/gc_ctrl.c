/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "gc.h"


/*************************************************************************
*   GC Ready Goal Pool.							 *
*************************************************************************/

int gc_ready_queue(void)
{
    register READY_QUEUE_BACKET *p;
    register GOAL_RECORD *old, *new, *next;

    p = highest;
    highest = NULL;
    while(p != NULL){
	old = p->head;
	for(;;){
	    if(old == NULL){
		p->head = NULL;	 /** ready queue is empty **/
#if TWO_WAY_READY_GOAL_POOL
		p->tail = NULL;
#endif
		if(p->upper != NULL) p->upper->lower = p->lower;
		if(p->lower != NULL) p->lower->upper = p->upper;
		goto next_priority;
	    }
	    if(!IsParentAborted(PrecOf(old->parent))){
		GcGetGoalRecord(new, old->argn);
		gc_goal_record(old, new);
		p->head = new;
		old = GoalQueuePt(old);
		break;
	    }
	    old = GoalQueuePt(old);
	}
	for(;;){
	    if(old == NULL){
		SetGoalQueuePt2(new, NULL);
#if TWO_WAY_READY_GOAL_POOL
		p->tail = new;
#endif
		break;
	    }
	    if(!IsParentAborted(PrecOf(old->parent))){
		GcGetGoalRecord(next, old->argn);
		gc_goal_record(old, next);
		SetGoalQueuePt2(new, next);
		new = next;
	    }
	    old = GoalQueuePt(old);
	}
	if(highest == NULL){
	    highest = p;
	}
      next_priority:
	p = p->lower;
    }
    if(highest == NULL){
	highest = &ready_queue_array[0];
    }
    current_queue = highest;
    priority = highest->priority;
    current_queue = highest;
    higher_priority_flag = NO;
}


/*************************************************************************
*   GC Goal Record.							 *
*************************************************************************/

int gc_goal_record(register GOAL_RECORD *old, register GOAL_RECORD *new)
{
    register CELL *oldarg, *newarg;
    register int  argn;

    argn = new->argn = old->argn;
    oldarg = old->args;
    newarg = new->args;
    while(argn--){  /** GC All Arguments (argn = Number of Arguments) **/
	gc_cell(oldarg, newarg);
	oldarg++; newarg++;
    }
    if(IsNotPrecCopied(PrecOf(old->parent))){
	/** 1st Access to Parent Record => Copy Record **/
	{ PARENT_RECORD *gc_r_; GcGetParentRecord(gc_r_); new->parent = Ref(gc_r_); }
	gc_parent_record(PrecOf(old->parent), PrecOf(new->parent));
    }else{
	/** Parent Record is Already Copied **/
	new->parent = Ref(GetCopiedPrec(PrecOf(old->parent)));
    }
    PrecOf(new->parent)->number_of_children2++;
    gc_cell(&(old->priority), &(new->priority));
    if(Typeof(&(new->priority)) == REF)
	SetMrbof(Objectof(&(new->priority)), MRBON);
    new->code = Ref(GcProcedure(CodeOf(old->code)));
    new->pcode = Ref(GcProcedure(CodeOf(old->pcode)));
    new->debug = old->debug;
    SetGrecGCflag(old);
}


/*************************************************************************
*   GC Shoen Record.							 *
*************************************************************************/

int gc_parent_record(register PARENT_RECORD *old, register PARENT_RECORD *new)
{
    register PARENT_RECORD *parent, *old_son, *new_son;

    parent = PrecOf(old->parent);
    SetPrecGCflag(old, new);  /* old->parent Point New-Heap => old is Copied */
    new->status		       = old->status;
    new->number_of_children    = old->number_of_children;
    new->number_of_children2   = 0;
    new->reduction_arrowed_max = old->reduction_arrowed_max;
    new->reduction_left	       = old->reduction_left;
    new->total_of_reduction    = old->total_of_reduction;
    new->id		       = old->id;
    new->priority_max	       = old->priority_max;
    new->priority_min	       = old->priority_min;
    new->tag		       = old->tag;

    new->left_son = Ref(new);	    /** New SHOEN Have no Child SHOEN **/
    new->right_son = Ref(new);
    if(parent == NULL){	    /* Have no Parent => Highest Level of Tree */
	new->parent = 0;
	new->left_brother = 0;
	new->right_brother = 0;
	new->number_of_children2++;
    }else{
	if(IsNotPrecCopied(parent)){
	    /** 1st Access to Parent => Copy Parent Record **/
	    { PARENT_RECORD *gc_r_; GcGetParentRecord(gc_r_); new->parent = Ref(gc_r_); }
	    gc_parent_record(parent, PrecOf(new->parent));
	    parent = PrecOf(new->parent);
	}else{
	    /** Parent is Already Copied **/
	    parent = GetCopiedPrec(parent); new->parent = Ref(parent);
	}
	if(PrecOf(parent->left_son) == parent){	 /** new is 1st Son of Parent **/
	    parent->left_son = Ref(new);
	    parent->right_son = Ref(new);
	    new->left_brother = Ref(parent);
	    new->right_brother = Ref(parent);
	}else{	  /** new is not 1st => Insert new into Brothers List **/
	    PrecOf(parent->left_son)->left_brother = Ref(new);
	    new->right_brother = parent->left_son;
	    new->left_brother = Ref(parent);
	    parent->left_son = Ref(new);
	}
	parent->number_of_children2++;
    }

    /*** Copy Child SHOEN. 88/07/12 ***/
    old_son = PrecOf(old->left_son);
    while(old_son != old){
	if(IsNotPrecCopied(old_son)){
	    GcGetParentRecord(new_son);
	    gc_parent_record(old_son, new_son);
	}else{
	    new_son = GetCopiedPrec(old_son);
	}
	old_son = PrecOf(old_son->right_brother);
    }

    gc_cell(&(old->queue), &(new->queue));
    if(Typeof(&(new->queue)) == REF)
	SetMrbof(Objectof(&(new->queue)), MRBON);
    gc_cell(&(old->report), &(new->report));
    if(Typeof(&(new->report)) == REF)
	SetMrbof(Objectof(&(new->report)), MRBON);
    old->number_of_children = 0;	  /** Used by Deadlock Check **/
}


/*************************************************************************
*   GC Suspension Queue.						 *
*************************************************************************/

int gc_suspension_queue(register CELL *oldhook, register CELL *newhook)
{
    register CELL *backhook;
    union {
	GOAL_RECORD *goal;
	SUSPENSION_RECORD *susp;
    } old, new;

    for(;;){
	switch(Typeof(oldhook)){
	  case HOOK:
	    /** HOOK Point to Suspended Goal Record (Single Wait) **/
	    old.goal = Goalof(oldhook);
	    if(IsParentAborted(PrecOf(old.goal->parent))){
		oldhook = &(old.goal->pt);
		continue;
	    }
	    GcGetGoalRecord(new.goal, old.goal->argn);
	    SetAll(newhook, HOOK, new.goal, MRBOFF);
	    gc_goal_record(old.goal, new.goal);
	    backhook = newhook;
	    oldhook = &(old.goal->pt);
	    newhook = &(new.goal->pt);
	    goto next;
	  case MHOOK:
	    /** MHOOK Point to Suspension Record (Multiple Wait) **/
	    old.susp = Suspof(oldhook);
	    if(IsParentAborted(PrecOf(GrecOf(old.susp->suspended)->parent))){
		oldhook = &(old.susp->forward);
		continue;
	    }
	    GcGetSuspensionRecord(new.susp);
	    SetAll(newhook, MHOOK, new.susp, MRBOFF);
	    gc_suspension_record(old.susp, new.susp);
	    SetAll(&(new.susp->backward), REF, newhook, MRBOFF);
	    backhook = newhook;
	    oldhook = &(old.susp->forward);
	    newhook = &(new.susp->forward);
	    goto next;
	  case UNDEF:
	    /** UNDEF => End of Qeueu **/
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return 0;
	  default:
	    Error2F("Not Hook Cell(%02x) in Susp-Queue (AD:%08x)\n",
					   Typeof(oldhook), oldhook);
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return 0;
	}
    }
  next:
    for(;;){
	switch(Typeof(oldhook)){
	  case HOOK:
	    /** HOOK Point to Suspended Goal Record (Single Wait) **/
	    old.goal = Goalof(oldhook);
	    if(IsParentAborted(PrecOf(old.goal->parent))){
		oldhook = &(old.goal->pt);
		continue;
	    }
	    GcGetGoalRecord(new.goal, old.goal->argn);
	    SetAll(newhook, HOOK, new.goal, MRBOFF);
	    gc_goal_record(old.goal, new.goal);
	    backhook = newhook;
	    oldhook = &(old.goal->pt);
	    newhook = &(new.goal->pt);
	    break;
	  case MHOOK:
	    /** MHOOK Point to Suspension Record (Multiple Wait) **/
	    old.susp = Suspof(oldhook);
	    if(IsParentAborted(PrecOf(GrecOf(old.susp->suspended)->parent))){
		oldhook = &(old.susp->forward);
		continue;
	    }
	    GcGetSuspensionRecord(new.susp);
	    SetAll(newhook, MHOOK, new.susp, MRBOFF);
	    gc_suspension_record(old.susp, new.susp);
	    new.susp->backward = *backhook;
	    backhook = newhook;
	    oldhook = &(old.susp->forward);
	    newhook = &(new.susp->forward);
	    break;
	  case UNDEF:
	    /** UNDEF => End of Qeueu **/
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return 0;
	  default:
	    Error2F("Not Hook Cell(%02x) in Susp-Queue (AD:%08x)\n",
					    Typeof(oldhook), oldhook);
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return 0;
	}
    }
}


/*************************************************************************
*   GC Suspension Record.						 *
*************************************************************************/

int gc_suspension_record(register SUSPENSION_RECORD *old, register SUSPENSION_RECORD *new)
{
    register SUSPENSION_RECORD *p1, *p2;

    if(IsNotSrecCopied(old)){
	/** 1st Access to Goal Record => Copy Goal Record **/
	{ GOAL_RECORD *gc_g_; GcGetGoalRecord(gc_g_, GrecOf(old->suspended)->argn); new->suspended = Ref(gc_g_); }
	for(p1 = SrecOf(old->other); p1 != old; p1 = p2){
	    p2 = SrecOf(p1->other);
	    SetSrecGCflag(p1, new);
	}
	new->other = Ref(new);
	gc_goal_record(GrecOf(old->suspended), GrecOf(new->suspended));
	return 0;
    }else{
	/** Suspended Goal is Already Copied **/
	new->suspended = GetCopiedSrec(old)->suspended;
	new->other = GetCopiedSrec(old)->other;
	GetCopiedSrec(old)->other = Ref(new);
	return 0;
    }
}


/*************************************************************************
*   GC Window I/O Table.						 *
*************************************************************************/

int gc_io_table(void)
{
    CELL *old;
    int	 i;

    for(i = 1; i < MAX_OF_WINDOW; i++){
	if(io_table[i].status&IO_ACTIVE){
	    old = io_table[i].inp_hook;
	    GcAlloc1Word(io_table[i].inp_hook);
	    gc_cell(old, io_table[i].inp_hook);
	    SetMrbof(Objectof(io_table[i].inp_hook), MRBON);
	    old = io_table[i].int_hook;
	    GcAlloc1Word(io_table[i].int_hook);
	    gc_cell(old, io_table[i].int_hook);
	    SetMrbof(Objectof(io_table[i].int_hook), MRBON);
	}
    }
}


/*************************************************************************
*   GC Timer Table.							 *
*************************************************************************/

int gc_timer_table(void)
{
    CELL *old;

    old = timer_table;
    GcAlloc1Word(timer_table);
    gc_cell(old, timer_table);
}
