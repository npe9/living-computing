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

gc_ready_queue()
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
	    if(!IsParentAborted(old->parent)){
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
	    if(!IsParentAborted(old->parent)){
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

gc_goal_record(old, new)
    register GOAL_RECORD *old, *new;
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
    if(IsNotPrecCopied(old->parent)){
	/** 1st Access to Parent Record => Copy Record **/
	GcGetParentRecord(new->parent);
	gc_parent_record(old->parent, new->parent);
    }else{
	/** Parent Record is Already Copied **/
	new->parent = GetCopiedPrec(old->parent);
    }
    new->parent->number_of_children2++;
    gc_cell(&(old->priority), &(new->priority));
    if(Typeof(&(new->priority)) == REF)
	SetMrbof(Objectof(&(new->priority)), MRBON);
    new->code = GcProcedure(old->code);
    new->pcode = GcProcedure(old->pcode);
    new->debug = old->debug;
    SetGrecGCflag(old);
}


/*************************************************************************
*   GC Shoen Record.							 *
*************************************************************************/

gc_parent_record(old, new)
    register PARENT_RECORD *old, *new;
{
    register PARENT_RECORD *parent, *old_son, *new_son;

    parent = old->parent;
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

    new->left_son = new;	    /** New SHOEN Have no Child SHOEN **/
    new->right_son = new;
    if(parent == NULL){	    /* Have no Parent => Highest Level of Tree */
	new->parent = NULL;
	new->left_brother = NULL;
	new->right_brother = NULL;
	new->number_of_children2++;
    }else{
	if(IsNotPrecCopied(parent)){
	    /** 1st Access to Parent => Copy Parent Record **/
	    GcGetParentRecord(new->parent);
	    gc_parent_record(parent, new->parent);
	    parent = new->parent;
	}else{
	    /** Parent is Already Copied **/
	    parent = new->parent = GetCopiedPrec(parent);
	}
	if(parent->left_son == parent){	 /** new is 1st Son of Parent **/
	    parent->left_son = new;
	    parent->right_son = new;
	    new->left_brother = parent;
	    new->right_brother = parent;
	}else{	  /** new is not 1st => Insert new into Brothers List **/
	    parent->left_son->left_brother = new;
	    new->right_brother = parent->left_son;
	    new->left_brother = parent;
	    parent->left_son = new;
	}
	parent->number_of_children2++;
    }

    /*** Copy Child SHOEN. 88/07/12 ***/
    old_son = old->left_son;
    while(old_son != old){
	if(IsNotPrecCopied(old_son)){
	    GcGetParentRecord(new_son);
	    gc_parent_record(old_son, new_son);
	}else{
	    new_son = GetCopiedPrec(old_son);
	}
	old_son = old_son->right_brother;
    }

    gc_cell(&(old->queue), &(new->queue));
    if(Typeof(&(new->queue)) == REF)
	SetMrbof(Objectof(&(new->queue)), MRBON);
    gc_cell(&(old->report), &(new->report));
    if(Typeof(&(new->report)) == REF)
	SetMrbof(Objectof(&(new->report)), MRBON);
    old->number_of_children = NULL;	  /** Used by Deadlock Check **/
}


/*************************************************************************
*   GC Suspension Queue.						 *
*************************************************************************/

gc_suspension_queue(oldhook, newhook)
    register CELL *oldhook, *newhook;
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
	    if(IsParentAborted(old.goal->parent)){
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
	    if(IsParentAborted(old.susp->suspended->parent)){
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
	    return;
	  default:
	    Error2F("Not Hook Cell(%02x) in Susp-Queue (AD:%08x)\n",
					   Typeof(oldhook), oldhook);
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return;
	}
    }
  next:
    for(;;){
	switch(Typeof(oldhook)){
	  case HOOK:
	    /** HOOK Point to Suspended Goal Record (Single Wait) **/
	    old.goal = Goalof(oldhook);
	    if(IsParentAborted(old.goal->parent)){
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
	    if(IsParentAborted(old.susp->suspended->parent)){
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
	    return;
	  default:
	    Error2F("Not Hook Cell(%02x) in Susp-Queue (AD:%08x)\n",
					    Typeof(oldhook), oldhook);
	    SetAll(newhook, UNDEF, NULL, MRBOFF);
	    return;
	}
    }
}


/*************************************************************************
*   GC Suspension Record.						 *
*************************************************************************/

gc_suspension_record(old, new)
    register SUSPENSION_RECORD *old, *new;
{
    register SUSPENSION_RECORD *p1, *p2;

    if(IsNotSrecCopied(old)){
	/** 1st Access to Goal Record => Copy Goal Record **/
	GcGetGoalRecord(new->suspended, old->suspended->argn);
	for(p1 = old->other; p1 != old; p1 = p2){
	    p2 = p1->other;
	    SetSrecGCflag(p1, new);
	}
	new->other = new;
	gc_goal_record(old->suspended, new->suspended);
	return;
    }else{
	/** Suspended Goal is Already Copied **/
	new->suspended = GetCopiedSrec(old)->suspended;
	new->other = GetCopiedSrec(old)->other;
	GetCopiedSrec(old)->other = new;
	return;
    }
}


/*************************************************************************
*   GC Window I/O Table.						 *
*************************************************************************/

gc_io_table()
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

gc_timer_table()
{
    CELL *old;

    old = timer_table;
    GcAlloc1Word(timer_table);
    gc_cell(old, timer_table);
}
