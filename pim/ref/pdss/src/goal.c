/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <varargs.h>
#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "tracer.h"

/** Reqdy Queue **/
READY_QUEUE_BACKET ready_queue_array[MAX_PRIORITY+1];
READY_QUEUE_BACKET *current_queue;
READY_QUEUE_BACKET *highest;
int higher_priority_flag;
#if TWO_WAY_READY_GOAL_POOL
int breadth_first_flag;
int enqueue_special_flag;
int random_enqueue_flag;
unsigned int random_rate;
unsigned int random_seed;
#endif

/** Suspension Stack **/
CELL *SSP;
CELL suspension_stack[SUSPMAX];


/*************************************************************************
*   Initialize Ready Queue.						 *
*************************************************************************/

initialize_priority_queue()
{
    register int i;
    register READY_QUEUE_BACKET *backet;
    for(i = 0; i <= MAX_PRIORITY; i++){
	backet = &ready_queue_array[i];
	backet->head = NULL;
#if TWO_WAY_READY_GOAL_POOL
	backet->tail = NULL;
#endif
	backet->upper = NULL;
	backet->lower = NULL;
	backet->priority = i;
    }
    highest = &ready_queue_array[0];
    higher_priority_flag = NO;
    current_queue = highest;
    priority = 0;
#if TWO_WAY_READY_GOAL_POOL
    breadth_first_flag = option_breadth_first;
    enqueue_special_flag = 0;
    random_enqueue_flag = option_random_enqueue;
    random_rate = option_random_rate;
    random_seed = option_random_seed;
#endif
}


/*************************************************************************
*   Enqueue Goal.  (Current Priority)					 *
*************************************************************************/

enqueue(grec)
    GOAL_RECORD *grec;
{
#if TWO_WAY_READY_GOAL_POOL
    unsigned int rnd();
    if(enqueue_special_flag ? (enqueue_special_flag==2) :
			      (random_enqueue_flag ? (rnd()<random_rate)
						   : breadth_first_flag)){
	SetGoalQueuePt2(grec, NULL);
	if(current_queue->tail == NULL){
	    current_queue->head = grec;
	}else{
	    SetGoalQueuePt2(current_queue->tail, grec);
	}
	current_queue->tail = grec;
    }else{
	SetGoalQueuePt2(grec, current_queue->head);
	if(current_queue->head == NULL) current_queue->tail = grec;
	current_queue->head = grec;
    }
    enqueue_special_flag = 0;
#else
    SetGoalQueuePt2(grec, current_queue->head);
    current_queue->head = grec;
#endif
}

#if TWO_WAY_READY_GOAL_POOL
enqueue_head(grec)
    GOAL_RECORD *grec;
{
    SetGoalQueuePt2(grec, current_queue->head);
    if(current_queue->head == NULL) current_queue->tail = grec;
    current_queue->head = grec;
}

enqueue_tail(grec)
    GOAL_RECORD *grec;
{
    SetGoalQueuePt2(grec, NULL);
    if(current_queue->tail == NULL){
	current_queue->head = grec;
    }else{
	SetGoalQueuePt2(current_queue->tail, grec);
    }
    current_queue->tail = grec;
}
#endif


/*************************************************************************
*   Enqueue Goal.							 *
*************************************************************************/

enqueue_with_priority(grec)
    GOAL_RECORD *grec;
#if TWO_WAY_READY_GOAL_POOL
{
    unsigned int rnd();
    if(enqueue_special_flag ? (enqueue_special_flag==2) :
			      (random_enqueue_flag ? (rnd()<random_rate)
						   : breadth_first_flag)){
	enqueue_tail_with_priority(grec);
    }else{
	enqueue_head_with_priority(grec);
    }
    enqueue_special_flag = 0;
}

enqueue_head_with_priority(grec)
    GOAL_RECORD *grec;
#endif
{
    register CELL *goal_priority_c;
    register unsigned goal_priority;
    register READY_QUEUE_BACKET *queue_pt, *backet;
    goal_priority_c = &(grec->priority);
    Dereference(goal_priority_c);
    if(IsRef(goal_priority_c)){
	SetMrbof(goal_priority_c, MRBON);
	single_wait_suspend(grec, goal_priority_c);
	if(!IsNativeCode(grec->code)) TracePrioritySuspendGoal(grec);
	return;
    }else{
	/* Translate:: logical priority --> phisical priority */
	goal_priority
	    = ((unsigned)(Valueof(goal_priority_c))>>PRIORITY_SIFT_WIDTH);
	backet = &ready_queue_array[goal_priority];
	if(backet->head != NULL){
	    SetGoalQueuePt2(grec, backet->head);
	    backet->head = grec;
	    return;
	}
	/* backet is empty */
	backet->head = grec;
#if TWO_WAY_READY_GOAL_POOL
	backet->tail = grec;
#endif
	SetGoalQueuePt2(grec, NULL);
	if(current_queue == backet) return;
	if(highest->priority < goal_priority){
	    higher_priority_flag = YES;
	    backet->lower = highest;
	    highest->upper = backet;
	    backet->upper = NULL;
	    highest = backet;
	    return;
	}else{			/* highest->priority > goal_priority */
	    queue_pt = highest;
	    do{
		if(queue_pt->lower == NULL){
		    backet->upper = queue_pt;
		    queue_pt->lower = backet;
		    backet->lower = NULL;
		    return;
		}
		queue_pt = queue_pt->lower;
	    } while(queue_pt->priority > goal_priority);
	    backet->upper = queue_pt->upper;
	    queue_pt->upper = backet;
	    backet->lower = queue_pt;
	    backet->upper->lower = backet;
	}
    }
}

#if TWO_WAY_READY_GOAL_POOL
enqueue_tail_with_priority(grec)
    GOAL_RECORD *grec;
{
    register CELL *goal_priority_c;
    register unsigned goal_priority;
    register READY_QUEUE_BACKET *queue_pt, *backet;
    goal_priority_c = &(grec->priority);
    Dereference(goal_priority_c);
    if(IsRef(goal_priority_c)){
	SetMrbof(goal_priority_c, MRBON);
	single_wait_suspend(grec, goal_priority_c);
	if(!IsNativeCode(grec->code)) TracePrioritySuspendGoal(grec);
	return;
    }else{
	/* Translate:: logical priority --> phisical priority */
	goal_priority
	    = ((unsigned)(Valueof(goal_priority_c))>>PRIORITY_SIFT_WIDTH);
	backet = &ready_queue_array[goal_priority];
	if(backet->tail != NULL){
	    SetGoalQueuePt2(grec, NULL);
	    SetGoalQueuePt2(backet->tail, grec);
	    backet->tail = grec;
	    return;
	}
	/* backet is empty */
	backet->head = grec;
	backet->tail = grec;
	SetGoalQueuePt2(grec, NULL);
	if(current_queue == backet) return;
	if(highest->priority < goal_priority){
	    higher_priority_flag = YES;
	    backet->lower = highest;
	    highest->upper = backet;
	    backet->upper = NULL;
	    highest = backet;
	    return;
	}else{			/* highest->priority > goal_priority */
	    queue_pt = highest;
	    do{
		if(queue_pt->lower == NULL){
		    backet->upper = queue_pt;
		    queue_pt->lower = backet;
		    backet->lower = NULL;
		    return;
		}
		queue_pt = queue_pt->lower;
	    } while(queue_pt->priority > goal_priority);
	    backet->upper = queue_pt->upper;
	    queue_pt->upper = backet;
	    backet->lower = queue_pt;
	    backet->upper->lower = backet;
	}
    }
}
#endif


/*************************************************************************
*   Random Number Generator.						 *
*************************************************************************/

#if TWO_WAY_READY_GOAL_POOL
#define RNDX 1048573
#define RNDY 323

static unsigned int rnd()
{
    random_seed = random_seed*RNDX+RNDY;
    return(random_seed%100);
}
#endif


/*************************************************************************
*   Dequeue Goal.							 *
*************************************************************************/

int dequeue()
{
    register GOAL_RECORD *goal;
  dequeue_loop:
    if(higher_priority_flag){
	higher_priority_flag = NO;
	goal = highest->head;
	priority = highest->priority;
	if(current_queue->head == NULL){ /* current_queue is empty */
	    current_queue->upper->lower = current_queue->lower;
	    if(current_queue->lower != NULL) 
		current_queue->lower->upper = current_queue->upper;
	}
	current_queue = highest;
    }else{			/* highest == current_queue */
	if((goal = highest->head) == NULL){ /* highest is empty */
	    if((highest = highest->lower) == NULL){ /* ready queue empty */
		highest = &ready_queue_array[0];
		current_queue = highest;
		priority = 0;
		return(NO);
	    }
	    priority = highest->priority;
	    goal = highest->head;
	    current_queue = highest;
	}
    }
    highest->head = GoalQueuePt(goal);
#if TWO_WAY_READY_GOAL_POOL
    if(highest->head == NULL) highest->tail = NULL;
#endif
    if(IsParentReady(goal->parent)){ /* executable */
	if(parent != goal->parent){
	    CacheParent2(goal->parent);
	}
	if(reduction_left==0){
	    if(parent->reduction_arrowed_max != 0){
		DecacheParent();
		if(resource_limit(goal->parent, 0)){  /* can't get resource */
		    SetMrbof(&(goal->parent->queue), MRBON);
		    single_wait_suspend(goal, &(goal->parent->queue));
		    goto dequeue_loop;
		}
		CacheParent(goal->parent);
	    }else{
		SetMrbof(&(goal->parent->queue), MRBON);
		single_wait_suspend(goal, &(goal->parent->queue));
		unify_exception_with_parent_report_stream(goal->parent,
						  &const_atom_reduction_limit);
		goal->parent->status |= RESOURCE_EXHAUSTED;
		goto dequeue_loop;
	    }
	}
	CacheGoal(goal);
	FreeGoalRecord(goal, goal->argn);
	return(YES);
    }else if(IsParentAborted(goal->parent)){	/* parent was aborted */
	goal->parent->number_of_children -= 1;
	FreeGoalRecord(goal, goal->argn);
	goto dequeue_loop;
    }else{			/* parent was suspended */
	SetMrbof(&(goal->parent->queue), MRBON);
	single_wait_suspend(goal, &(goal->parent->queue));
	goto dequeue_loop;
    }
}


/*************************************************************************
*   Suspend -- Popup Suspension Stack.					 *
*************************************************************************/

popup_suspension_stack(goal)
    GOAL_RECORD *goal;
{
    register CELL *c, *root;
    register SUSPENSION_RECORD *srec, *last;
    register MRB mrb;
    
    c = Objectof(--SSP);
    if(other_var_exist(c)){
	/*** Multiple Wait ***/
	while(same_var_exist(c)) c = Objectof(--SSP);
	root = c;
	last = NULL;
	for(;;){
	    switch(Typeof(c)){
	      case UNDEF:
		GetSuspensionRecord(srec);
		srec->suspended = goal;
		SetSuspRecForward(srec, UNDEF, NIL);
		SetSuspRecBackward(srec, REF, c);
		SetTypeof(c, MHOOK); SetSuspof(c, srec);
		break;
	      case HOOK:
		GetSuspensionRecord(srec);
		srec->suspended = goal;
		SetSuspRecForward(srec, HOOK, Suspof(c));
		SetSuspRecBackward(srec, REF, c);
		SetTypeof(c, MHOOK); SetSuspof(c, srec);
		break;
	      case MHOOK:
		if(Suspof(c)->suspended != goal){
		    GetSuspensionRecord(srec);
		    srec->suspended = goal;
		    SetSuspRecForward(srec, MHOOK, Suspof(c));
		    SetSuspRecBackward(srec, REF, c);
		    SetSuspRecBackward(Suspof(c), MHOOK, srec);
		    SetSuspof(c, srec);
		}
		break;
	      case MGHOK:
		{
		    register CELL *nc;
		    register GOAL_RECORD *grec;
		    GetSuspensionRecord(srec);
		    srec->suspended = goal;
		    AllocMghok(nc);
		    SetMergerof(nc, Mergerof(c));
		    SetTypeof(c, MHOOK); SetSuspof(c, srec);
		    grec = make_unify_goal_for_merger(
				     REF,c,MRBON, REF,nc,MRBOFF, Mergerof(nc));
		    SetSuspRecForward(srec, HOOK, grec);
		    SetSuspRecBackward(srec, REF, c);
		    SetGoalQueuePt(grec, UNDEF, NIL);
		}
		break;
	      default:
		Error("Illegal data type is found in suspension stack.");
		PrintCons2F("TAG : %x, Value : %x", Typeof(c), Valueof(c));
		PrintCons1F("SSP : %x", (SSP - suspension_stack));
		return;
	    }
	    srec->other = last;
	    last = srec;
	    if(--SSP < suspension_stack) break;
	    c = Objectof(SSP);
	    while(same_var_exist(c)) c = Objectof(--SSP);
	}
	Suspof(root)->other = srec;  /* success terminateion */
    }else{
	/**** Single Wait ****/
	mrb = Mrbof(SSP);
	switch(Typeof(c)) {
	  case UNDEF:
	    DetectDeadlockInSuspHook(SUSPEND_VOID, goal, c, mrb);
	    SetGoalQueuePt(goal, UNDEF, NIL);
	    SetTypeof(c, HOOK); SetGoalof(c, goal);
	    SetMrbof(c, mrb);
	    break;
	  case HOOK:
	    DetectDeadlockInSuspHook(SUSPEND_HOOK, goal, c, mrb);
	    SetGoalQueuePt(goal, HOOK, Goalof(c));
	    SetGoalof(c, goal);
	    SetMrbof(c, mrb);
	    break;
	  case MHOOK:
	    SetGoalQueuePt(goal, MHOOK, Suspof(c));
	    SetSuspRecBackward(Suspof(c), HOOK, goal);
	    SetTypeof(c, HOOK); SetGoalof(c, goal);
	    break;
	  case MGHOK:
	    DetectDeadlockInSuspMghok(SUSPEND_MGHK, goal, c, mrb);
	    {
		register CELL *nc;
		register GOAL_RECORD *grec;
		AllocMghok(nc);
		SetMergerof(nc, Mergerof(c));
		SetTypeof(c, HOOK); SetGoalof(c, goal);
		grec = make_unify_goal_for_merger(
				       REF,c,mrb, REF,nc,MRBOFF, Mergerof(nc));
		SetGoalQueuePt(goal, HOOK, grec);
		SetGoalQueuePt(grec, UNDEF, NIL);
	    }
	    SetMrbof(c, mrb);
	    break;
	  default:
	    Error("Illegal data type is found in suspension stack.");
	    PrintCons2F("TAG : %x, Value : %x", Typeof(c), Valueof(c));
	    PrintCons1F("SSP : %x", (SSP - suspension_stack));
	}
    }
}

static int other_var_exist(c)
    register CELL *c;
{
    register CELL *tmp = SSP-1;
    while(tmp >= suspension_stack){
	if(Objectof(tmp--) != c) return(YES);
    }
    return(NO);
}

static int same_var_exist(c)
    register CELL *c;
{
    register CELL *tmp = SSP-1;
    while(tmp >= suspension_stack){
	if(Objectof(tmp--) == c) return(YES);
    }
    return(NO);
}


/*************************************************************************
*   Suspend -- Single Wait.						 *
*************************************************************************/

single_wait_suspend(goal, ref)
    GOAL_RECORD *goal;
    CELL *ref;
{
    register CELL *var;
    register MRB mrb;
    mrb = Mrbof(ref);
    var = Objectof(ref);
    switch(Typeof(var)){
      case UNDEF:
	DetectDeadlockInSuspHook(SUSPEND_VOID, goal, var, mrb);
	SetGoalQueuePt(goal, UNDEF, NIL);
	SetTypeof(var, HOOK); SetGoalof(var, goal);
	SetMrbof(var, mrb);
	break;
      case HOOK:
	DetectDeadlockInSuspHook(SUSPEND_HOOK, goal, var, mrb);
	SetGoalQueuePt(goal, HOOK, Goalof(var));
	SetGoalof(var, goal);
	SetMrbof(var, mrb);
	break;
      case MHOOK:
	SetGoalQueuePt(goal, MHOOK, Suspof(var));
	SetSuspRecBackward(Suspof(var), HOOK, goal);
	SetTypeof(var, HOOK); SetGoalof(var, goal);
	break;
      case MGHOK:
	DetectDeadlockInSuspMghok(SUSPEND_MGHK, goal, var, mrb);
	{
	    register CELL *nvar;
	    register GOAL_RECORD *grec;
	    AllocMghok(nvar);
	    SetMergerof(nvar, Mergerof(var));
	    SetTypeof(var, HOOK); SetGoalof(var, goal);
	    grec = make_unify_goal_for_merger(
				 REF,var,mrb, REF,nvar,MRBOFF, Mergerof(nvar));
	    SetGoalQueuePt(goal, HOOK, grec);
	    SetGoalQueuePt(grec, UNDEF, NIL);
	}
	SetMrbof(var, mrb);
	break;
      default:
	Error("Illegal data type is found in single_wait_suspend().");
	PrintCons2F("Tag : %x, Value : %x", Typeof(var), Valueof(var));
    }
}


/*************************************************************************
*   Suspend -- Body Builtin Suspend.					 *
*************************************************************************/

body_builtin_suspend(code, waitref, argio, va_alist)
    OBJ *code;
    unsigned int argio;
    CELL *waitref;
    va_dcl
{
    va_list bltargs;
    register int i;
    register CELL *x, *y, *undef;
    register GOAL_RECORD *grec;
    static CELL *ap[MAXREGS];
    GetGoalRecord(grec, 8);  /** Number of Builtin Argument <= 8 **/
    y = grec->args;
    va_start(bltargs);
    for(i=0; argio&(I|O); i++,argio>>=3){
	x = va_arg(bltargs, CELL *);
	if(argio&I){
	    /*** Input Argument ***/
	    *y = *x;
	    ap[i] = NULL;
	}else{
	    /*** Output Argument ***/
	    AllocUndef(undef);
	    SetAll(y, REF, undef, MRBOFF);
	    ap[i] = x;
	}
	y++;
    }
    va_end(bltargs);
    grec->argn = i;
    grec->parent = parent;
    grec->code = code;
    SetGoalPriority(grec, INT, logical_priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = current_predicate2 ? current_predicate2 : current_predicate;
    number_of_children += 1;
    single_wait_suspend(grec, waitref);
    while(i--){
	y--;
	if(ap[i]){
	    *ap[i] = *y;
	}
    }
}


/*************************************************************************
*   Swap Goal -- Body Builtin Swap.					 *
*************************************************************************/

body_builtin_swap(code, argio, va_alist)
    OBJ *code;
    unsigned int argio;
    va_dcl
{
    va_list bltargs;
    register int i;
    register CELL *x, *y, *undef;
    register GOAL_RECORD *grec;
    static CELL *ap[MAXREGS];
    GetGoalRecord(grec, 8);  /** Number of Builtin Argument <= 8 **/
    y = grec->args;
    va_start(bltargs);
    for(i=0; argio&(I|O); i++,argio>>=3){
	x = va_arg(bltargs, CELL *);
	if(argio&I){
	    /*** Input Argument ***/
	    *y = *x;
	    ap[i] = NULL;
	}else{
	    /*** Output Argument ***/
	    AllocUndef(undef);
	    SetAll(y, REF, undef, MRBOFF);
	    ap[i] = x;
	}
	y++;
    }
    va_end(bltargs);
    grec->argn = i;
    while(i--){
	y--;
	if(ap[i]){
	    *ap[i] = *y;
	}
    }
    grec->parent = parent;
    grec->code = code;
    SetGoalPriority(grec, INT, logical_priority);
    grec->debug = NO_TRACE_GOAL;
    grec->pcode = current_predicate2;
    number_of_children += 1;
    enqueue(grec);
}


/*************************************************************************
*   Resume -- Wakeup Goal.						 *
*************************************************************************/

wakeup_goals(cc, type, value, mrb)
    CELL *cc, *value;
    int type;
    MRB mrb;
{
    register SUSPENSION_RECORD *srec;
    register GOAL_RECORD *grec;
    CELL *c;
    CELL tmpc;
    
    tmpc = *cc;
    c = &tmpc;
    SetAll(cc, type, value, mrb);
    do{
	if(Typeof(c) == HOOK){	/* case of single waiting */
	    grec = Goalof(c);
	    if(!IsNativeCode(grec->code)) TraceResumeGoal(grec);
	    tmpc = grec->pt; c = &tmpc;
	    enqueue_with_priority(grec);
	}else{			/* case of multiple waiting or read message */
	    SUSPENSION_RECORD *other;			   /* hooked */
	    srec = Suspof(c);
	    grec = srec->suspended;
	    if(!IsNativeCode(grec->code)) TraceResumeGoal(grec);
	    enqueue_with_priority(grec);
	    other = srec->other;
	    while(other != srec){
		SUSPENSION_RECORD *gomi_srec = other;
		CELL *forw = &(other->forward);
		if(Typeof(&(other->backward)) == REF){ /* to var cell */
		    CELL *back;
		    back = Objectof(&(other->backward));
		    SetTypeof(back, Typeof(forw));
		    SetValueof(back, Valueof(forw));
		}else if(Typeof(&(other->backward)) == HOOK){ /* HOOK */
		    GOAL_RECORD *back;
		    back = Goalof(&(other->backward));
		    SetGoalQueuePt(back, Typeof(forw), Suspof(forw));
		}else{		     /* MHOOK : point to susp. record */
		    SUSPENSION_RECORD *back;
		    back = Suspof(&(other->backward));
		    SetSuspRecForward(back, Typeof(forw), Suspof(forw));
		}
		if(Typeof(forw) == MHOOK){
		    SetSuspRecBackward(Suspof(forw),
				       Typeof(&(other->backward)),
				       Suspof(&(other->backward)));
		}
		other = other->other;
		FreeSuspensionRecord(gomi_srec);
	    }
	    tmpc = srec->forward;
	    FreeSuspensionRecord(srec);
	    c = &tmpc;
	}
    } while(Typeof(c) != UNDEF);  /* UNDEF: end of suspension queue */
}


/*************************************************************************
*   Merge Suspension Queue.						 *
*************************************************************************/

move_suspension_queue(from, to)
    register CELL *from, *to;
{
    register CELL *tmp_cell;
    register GOAL_RECORD *tmp_grec;
    register SUSPENSION_RECORD *tmp_srec;
    Mrbof(to) = MRBON;
    tmp_cell = to;
  move_susp_loop_grec:
    switch(Typeof(tmp_cell)){
      case HOOK:
	tmp_cell = &((tmp_grec=Goalof(tmp_cell))->pt);
	goto move_susp_loop_grec;
      case MHOOK:
	tmp_cell = &((tmp_srec=Suspof(tmp_cell))->forward);
	goto move_susp_loop_srec;
      default:			/* NULL pointer */
	SetGoalQueuePt(tmp_grec, Typeof(from), Suspof(from));
	if(Typeof(from) == MHOOK){
	    SetSuspRecBackward(Suspof(from), HOOK, tmp_grec);
	}
	return;
    }
  move_susp_loop_srec:
    switch(Typeof(tmp_cell)){
      case HOOK:
	tmp_cell = &((tmp_grec=Goalof(tmp_cell))->pt);
	goto move_susp_loop_grec;
      case MHOOK:
	tmp_cell = &((tmp_srec=Suspof(tmp_cell))->forward);
	goto move_susp_loop_srec;
      default:			/* NULL pointer */
	SetSuspRecForward(tmp_srec, Typeof(from), Suspof(from));
	if(Typeof(from) == MHOOK){
	    SetSuspRecBackward(Suspof(from), MHOOK, tmp_srec);
	}
	return;
    }
}
