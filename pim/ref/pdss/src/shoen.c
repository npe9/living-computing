/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
/* PORT: forward declarations */
static int delete_from_and_tree();
static int resource_divide_to_children();
static int divide_resource();
static int shoen_active_unify_with_list();
static int dump_shoen_tree();
static int dump_shoen_tree_sub();


PARENT_RECORD *grand_mother;  /** Root of Shoen Tree **/
CELL *result_of_grand_mother;

int shoen_tree_trace_flag;
#define DumpTree(mesg, sr){\
    if(shoen_tree_trace_flag){\
	PrintCons2F(mesg,\
	    (sr)->status==READY ? 'R' : ((sr)->status==ABORTED ? 'A' : 'S'),\
	    (sr)->id);\
	dump_shoen_tree(grand_mother, 0);\
    }\
}

static int shoen_id_counter;
#define GetShoenid() (shoen_id_counter++)


/*************************************************************************
*   Initialize Shoen Tree.						 *
**************************************************************************

		+---------------+
	    +-->|  Dummy Shoen	|<--+
	    |	+---------------+   |
	    |		|	    |
	    |	+---------------+   |
	    +-->|  Grand Mother |<--+
	    +-->|     Shoen	|<--+
	    |	+---------------+   |
	    |		|	    |
	    |	  +-----------+	    |
	    |	  | Boot Goal |	    |
	    |	  +-----------+	    |
	    |			    |
	    +-----------------------+
*/

initialize_shoen_tree(boot_code)
    OBJ *boot_code;
{
    PARENT_RECORD *grandma, *dummy;
    GOAL_RECORD *boot_goal;
    CELL *c;

    shoen_id_counter = 0;
    GetParentRecord(dummy);
    dummy->number_of_children = 2;
    dummy->parent = NULL;
    dummy->status = READY;
    dummy->reduction_left = -100;
    dummy->reduction_arrowed_max = -1;
    dummy->priority_max = (MAX_PRIORITY<<PRIORITY_SIFT_WIDTH)-1;
    dummy->priority_min = 0;
    AllocUndef(c);
    SetAll(&(dummy->queue), REF, c, MRBOFF);
    AllocUndef(c);
    SetAll(&(dummy->report), REF, c, MRBOFF);

    GetParentRecord(grandma);
    dummy->right_son = grandma;
    dummy->left_son = grandma;
    grandma->status = READY;
    grandma->id = GetShoenid();
    grandma->right_brother = dummy;
    grandma->left_brother = dummy;
    grandma->left_son = grandma;
    grandma->right_son = grandma;
    grandma->parent = dummy;
    grandma->reduction_left = 0x7FFFFFFF;
    grandma->total_of_reduction = 0;
    grandma->number_of_children = 1;
    grandma->reduction_arrowed_max = -100;
    grandma->priority_max = (MAX_PRIORITY<<PRIORITY_SIFT_WIDTH)-1;
    grandma->priority_min = 0;
    grandma->tag = 0xFFFFFFFF;
    AllocUndef(c);
    SetAll(&(grandma->queue), REF, c, MRBOFF);
    AllocUndef(c);
    SetAll(&(grandma->report), REF, c, MRBOFF);
    AllocCell(result_of_grand_mother);
    SetAll(result_of_grand_mother, REF, c, MRBOFF);
    grand_mother = grandma;

    CacheParent(grandma);
    GetGoalRecord(boot_goal, 0);
    boot_goal->argn = 0;
    boot_goal->parent = parent;
    boot_goal->code = boot_code;
    SetGoalPriority(boot_goal, INT, parent->priority_max);
    boot_goal->debug = 0;
    boot_goal->pcode = NULL;
    enqueue_with_priority(boot_goal);
}


/*************************************************************************
*   Create Shoen.							 *
**************************************************************************

Shoen Priority:
  pmin & pmax is priority rate to calculete new priority.
  0 <= pmin+pmax <= PRIORITY_RATE_FULL, pmin >= 0, pmax >= 0.

		   MIN				    Current	  MAX
  Current Shoen:    |==================================|===========|
		    |<------ PRIORITY_RATE_FULL ------>|
		    |<-pmin->|		      |<-pmax->|
      New Shoen:	     |================|
			    MIN		     MAX
*/

PARENT_RECORD *create_shoen(code, argv, pmin, pmax, tag, report)
    unsigned int pmin, pmax, tag;
    CELL *code, *argv, *report;
{
    PARENT_RECORD *prec;
    GOAL_RECORD *grec;
    CELL *c;
    unsigned int max, min;

    max = logical_priority, 
    min = parent->priority_min;
    GetParentRecord(prec);
    prec->id			= GetShoenid();
    prec->status		= (SUSP_D | RESOURCE_EXHAUSTED);
    prec->number_of_children	= 1;
    prec->reduction_arrowed_max = 0;
    prec->reduction_left	= 0;
    prec->total_of_reduction	= 0;
    prec->priority_min		= min+((max-min)>>PRIORITY_RATE_WIDTH)*pmin;
    prec->priority_max		= max-((max-min)>>PRIORITY_RATE_WIDTH)*pmax;
    prec->tag			= tag;
    prec->parent		= parent;
    number_of_children++;
    DumpTree("*** create shoen [%c%04d] - begin.\n", prec);

    prec->left_brother = parent->right_son;
    parent->right_son = prec;
    prec->right_brother = parent;
    if(parent == prec->left_brother){
	parent->left_son = prec;
    }else{
	prec->left_brother->right_brother = prec;
    }
    prec->left_son = prec;
    prec->right_son = prec;

    AllocUndef(c);
    SetAll(&(prec->queue), REF, c, MRBOFF); 
    AllocUndef(c);
    SetAll(&(prec->report), REF, c, MRBOFF);
    SetAll(report, REF, c, MRBOFF);

    GetGoalRecord(grec, 2);
    SetGoalPriority(grec, INT, prec->priority_max);
    grec->parent = prec;
    grec->code = (OBJ *)dc_apply;
    grec->argn = 2;
    grec->args[0] = *code;
    grec->args[1] = *argv;
    grec->debug = 0;
    grec->pcode = NULL;
    enqueue_with_priority(grec);

    DumpTree("*** create shoen [%c%04d] - end.\n", prec);
    return(prec);
}


/*************************************************************************
*   Start Shoen.							 *
*************************************************************************/

start_shoen(shoen, kind)
    PARENT_RECORD *shoen;
    int kind;
{
    if(IsParentAborted(shoen)) return;
/** DumpTree("*** start shoen [%c%04d] - begin.\n", shoen); **/
    if((shoen->status & (~kind)) == READY && 
       Typeof(Objectof(&(shoen->queue))) == HOOK){
	register GOAL_RECORD *grec, *next;
	grec = Goalof(Objectof(&(shoen->queue)));
	while(Typeof(&(grec->pt)) == HOOK){
	    next = Goalof(&(grec->pt));
	    enqueue_with_priority(grec);
	    grec = next;
	}
	enqueue_with_priority(grec);
	SetTypeof(Objectof(&(shoen->queue)), UNDEF);
    }
    if(!((shoen->status &= ~kind) & SUSP_PD)){
	PARENT_RECORD *son; 
	for(son = shoen->left_son; son != shoen; son = son->right_brother){
	    start_shoen(son, SUSP_P);
	}
    }
/** DumpTree("*** start shoen [%c%04d] - end.\n", shoen); **/
}


/*************************************************************************
*   Stop Shoen.								 *
*************************************************************************/

stop_shoen(shoen, kind)
    PARENT_RECORD *shoen;
    int kind;
{
    PARENT_RECORD *son;	   
/** DumpTree("*** stop shoen [%c%04d] - begin.\n", shoen); **/
    son = shoen->left_son;
    shoen->status |= kind;
    while(son != shoen){
	stop_shoen(son, SUSP_P);
	son = son->right_brother;
    }
/** DumpTree("*** stop shoen [%c%04d] - end.\n", shoen); **/
}


/*************************************************************************
*   Abort Shoen.							 *
*************************************************************************/

abort_shoen(shoen)
    PARENT_RECORD *shoen;
{
    register PARENT_RECORD *prec;
    if(IsParentAborted(shoen)) return;
    DumpTree("*** abort shoen [%c%04d] - begin.\n", shoen);
    shoen->status = ABORTED;
    unify_message_with_parent_report_stream(shoen, &const_atom_aborted);
    if(Typeof(Objectof(&(shoen->queue))) == HOOK){
	register GOAL_RECORD *grec, *next;
	grec = Goalof(Objectof(&(shoen->queue)));
	while(Typeof(&(grec->pt)) == HOOK){
	    next = Goalof(&(grec->pt));
	    FreeGoalRecord(grec, grec->argn);
	    grec = next;
	}
	FreeGoalRecord(grec, grec->argn);
	Typeof(Objectof(&(shoen->queue))) = UNDEF;
    }
    for(prec = shoen->left_son; prec != shoen; prec = prec->right_brother){
	abort_shoen(prec);
    }
    prec = parent;
    DecacheParent();
    shoen->parent->number_of_children -= 1;
    shoen->parent->total_of_reduction += shoen->total_of_reduction;
    shoen->parent->reduction_left += shoen->reduction_left;
    delete_from_and_tree(shoen);
    CacheParent(prec);
    DumpTree("*** abort shoen [%c%04d] - end.\n", shoen);
}

remove_shoen(shoen)
    PARENT_RECORD *shoen;
{
    return;
}


/*************************************************************************
*   Terminate Shoen.							 *
*************************************************************************/

terminate_shoen()
{
    register PARENT_RECORD *current_shoen, *parent_shoen;
    register CELL *cons, *report;
    CELL list;
    current_shoen = parent;
    DumpTree("*** terminate shoen [%c%04d] - begin.\n", current_shoen);
    DecacheParent();
    parent_shoen = current_shoen->parent;
    report = &(current_shoen->report);
    current_shoen->status = ABORTED;
    delete_from_and_tree(current_shoen);
    parent_shoen->number_of_children -= 1;
    parent_shoen->total_of_reduction += current_shoen->total_of_reduction;
    parent_shoen->reduction_left += current_shoen->reduction_left;
    if(IsResourceExhausted(parent_shoen) ||
       IsChildRequestResource(parent_shoen)){
	resource_limit(parent_shoen, 0);
    }
    AllocCons(cons);
    SetAll(&list, LIST, cons, MRBOFF);
    cons[0] = const_atom_succeeded;
    cons[1] = const_nil;
    CacheParent(parent_shoen);
    shoen_active_unify_with_list(report, &list);
    if(number_of_children == 0){
	terminate_shoen();
    }
    DumpTree("*** terminate shoen [%c%04d] - end.\n", current_shoen);
}

static delete_from_and_tree(shoen)
    PARENT_RECORD *shoen;
{
    if(shoen->parent == shoen->left_brother){
	shoen->left_brother->left_son = shoen->right_brother;
    }else{
	shoen->left_brother->right_brother = shoen->right_brother;
    }
    if(shoen->parent == shoen->right_brother){
	shoen->right_brother->right_son = shoen->left_brother;
    }else{
	shoen->right_brother->left_brother = shoen->left_brother;
    }
}


/*************************************************************************
*   Shoen Statistics.							 *
*************************************************************************/

int shoen_statistics(shoen)
    PARENT_RECORD *shoen;
{
    register PARENT_RECORD *son;
    register int red=0;
    for(son = shoen->left_son; son != shoen; son = son->right_brother){
	red += shoen_statistics(son);
    }
    return(red+shoen->total_of_reduction);
}


/*************************************************************************
*   Add Resource.							 *
*************************************************************************/

shoen_add_resource(shoen, more)
    PARENT_RECORD *shoen;
    int more;
{
    PARENT_RECORD *current_shoen;
    if(IsParentAborted(shoen)) return;
    current_shoen = parent;
    DecacheParent();
    shoen->reduction_arrowed_max += more;
    if(IsResourceExhausted(shoen) || IsChildRequestResource(shoen)){
	if(resource_limit(shoen, 0)){ /* divide failure */
	    unify_exception_with_parent_report_stream(
					  shoen, &const_atom_reduction_limit);
	}else{
	    if(shoen->parent->reduction_left == 0){
		(shoen->parent->reduction_left)++;
	    }
	}
    }
    CacheParent(current_shoen);
}


/*************************************************************************
*   Resource Managiment.						 *
*************************************************************************/

#define UNIT 1000

#define ResetParentStatus(P, FLAG) {\
    (P)->status &= ~(FLAG);\
    if(IsParentReady(P) && Typeof(Objectof(&((P)->queue))) == HOOK){\
	register GOAL_RECORD *grec, *next;\
	grec = Goalof(Objectof(&((P)->queue)));\
	for(;;){\
	    if(Typeof(&(grec->pt)) != HOOK) break;\
	    next = Goalof(&(grec->pt));\
	    enqueue_with_priority(grec);\
	    grec = next;\
	}\
	enqueue_with_priority(grec);\
	SetTypeof(Objectof(&((P)->queue)), UNDEF);\
    }\
}

int resource_limit(p, level)
    PARENT_RECORD *p;
    int level;
{
    int max = p->reduction_arrowed_max;
    if(max != 0){  /* Require reduction count of */
	PARENT_RECORD *pp = p->parent;
	if((pp->reduction_left > 0) || (pp->reduction_left < -99)){
	    /** Grandfather can divide **/
	    divide_resource(pp, p);
	    if(IsChildRequestResource(p)){
		if(resource_divide_to_children(p)){
		    return(resource_limit(p, level));
		}
		ResetParentStatus(p, RESOURCE_REQUEST);
	    }
	    if(p->reduction_left > 0){
		ResetParentStatus(p, RESOURCE_EXHAUSTED);
	    }
	    return(NO);		/** Not Resource Limit, Can Continue **/
	}else{
	    /** Grandfather can't divide **/
            if(resource_limit(pp, 1)){
                /** Grand-grandfather can't dived **/
		if(level > 0){
		    p->status |= RESOURCE_REQUEST;
		}else{
		    p->status |= RESOURCE_EXHAUSTED;
		}
		return(YES);	/** Resource Limit Occured **/
	    }else{
		divide_resource(pp, p);
		if(IsChildRequestResource(p)){
		    if(resource_divide_to_children(p)){
			return(resource_limit(p, level));
		    }
		    ResetParentStatus(p, RESOURCE_REQUEST);
		}
		if(p->reduction_left > 0){
		    ResetParentStatus(p, RESOURCE_EXHAUSTED);
		}
		return(NO);	/** Not Resource Limit, Can Continue **/
	    }
	}
    }else{
	/** Resource Limit & Exception Occurred **/
	CELL mesg;
	if(!(IsResourceExhausted(p) || IsChildRequestResource(p))){
	    SetAll(&mesg, ATOM, ATOM_REDUCTION_LIMIT, MRBOFF);
	    unify_exception_with_parent_report_stream(
					      p, &const_atom_reduction_limit);
	}
	if(level > 0){
	    p->status |= RESOURCE_REQUEST;
	}else{
	    p->status |= RESOURCE_EXHAUSTED;
	}
	return(YES);		/** Resource Limit Occured **/
    }
}

static int resource_divide_to_children(p)
    PARENT_RECORD *p;
{
    PARENT_RECORD *prec = p->left_son;
    while((p != prec) && (p->reduction_left > 0)){
	int max = prec->reduction_arrowed_max;
	if((IsResourceExhausted(prec) || IsChildRequestResource(prec)) &&
	   (max != 0)){
	    divide_resource(p, prec);
	    if(IsChildRequestResource(prec)){
		if(resource_divide_to_children(prec)){
		    return(YES);	/** Resource Limit Occured **/
		}
		ResetParentStatus(prec, RESOURCE_REQUEST);
	    }
	    if(prec->reduction_left > 0){
		ResetParentStatus(prec, RESOURCE_EXHAUSTED);
	    }
	}
	prec = prec->right_brother;
    }
    while(prec != p){
	int max = prec->reduction_arrowed_max;
	if((IsResourceExhausted(prec) || IsChildRequestResource(prec)) &&
	   (max != 0)){
	    return(YES);	/** Resource Limit Occured **/
	}
	prec = prec->right_brother;
    }
    return(NO);			/** Not Resource Limit, Can Continue **/
}

static divide_resource(from, to)
    PARENT_RECORD *from, *to;
{
    int max = to->reduction_arrowed_max;
    if(from->reduction_left < -99){
	if(max > 0 && max >= UNIT){
	    to->reduction_arrowed_max -= UNIT;
	    to->reduction_left += UNIT;
	}else if(max > 0 && max < UNIT){
	    to->reduction_arrowed_max = 0;
	    to->reduction_left += max;
	}
    }else{
	if(from->reduction_left > UNIT && (max < 0 || max >= UNIT)){
	    if(max > 0) to->reduction_arrowed_max -= UNIT;
	    from->reduction_left -= UNIT;
	    to->reduction_left += UNIT;
	}else if(max > 0 && max < UNIT && max < from->reduction_left){
	    from->reduction_left -= max;
	    to->reduction_arrowed_max = 0;
	    to->reduction_left += max;
	}else{
	    if(max > 0) to->reduction_arrowed_max -= from->reduction_left;
	    to->reduction_left += from->reduction_left;
	    from->reduction_left = 0;
	}
    }
}


/*************************************************************************
*   Unify Message with Report Stream.					 *
*************************************************************************/

PARENT_RECORD *search_parent_tag(prec, tag)
    PARENT_RECORD *prec;
    unsigned int tag;
{
    while(prec){
	if((prec->tag & tag) != 0) return(prec);
	prec = prec->parent;
    }
    Error1F("Illegal exception tag was occurred: %d\n", tag);
    exit_pdss(1);
}

int report_raise_flag = NO;

#define ExceptionMesg(mesg, id) {\
    if(report_raise_flag || id == 0){\
	PrintCons(">> ");\
	print_term(mesg, PRINT_LENGTH, PRINT_DEPTH);\
	printf(" in shoen#%d.\n", id);\
    }\
}

unify_exception_with_report_stream(prec, mesg, tag)
    PARENT_RECORD *prec;
    CELL *mesg;
    unsigned int tag;
{
    PARENT_RECORD *current_parent;
    register CELL *cons, *undef;
    CELL report, list;
    ExceptionMesg(mesg, prec->id);
    if(parent->id != 0){
	current_parent = parent;
	DecacheParent();
	prec = search_parent_tag(prec, tag);
	CacheParent(prec->parent);
	report = prec->report;
	AllocUndef(undef);
	AllocCons(cons);
	cons[0] = *mesg;
	SetAll(cons+1, REF, undef, MRBOFF);
	SetAll(&(prec->report), REF, undef, MRBOFF);
	SetAll(&list, LIST, cons, MRBOFF);
	shoen_active_unify_with_list(&report, &list);
	CacheParent2(current_parent);
    }
}

unify_exception_with_parent_report_stream(prec, mesg)
    PARENT_RECORD *prec;
    CELL *mesg;
{
    PARENT_RECORD *current_parent;
    register CELL *cons, *undef;
    CELL report, list;
    ExceptionMesg(mesg, prec->id);
    if(prec->id != 0){
	current_parent = parent;
	CacheParent2(prec->parent);
	report = prec->report;
	AllocUndef(undef);
	AllocCons(cons);
	cons[0] = *mesg;
	SetAll(cons+1, REF, undef, MRBOFF);
	SetAll(&(prec->report), REF, undef, MRBOFF);
	SetAll(&list, LIST, cons, MRBOFF);
	shoen_active_unify_with_list(&report, &list);
	CacheParent2(current_parent);
    }
}

unify_message_with_parent_report_stream(prec, mesg)
    PARENT_RECORD *prec;
    CELL *mesg;
{
    PARENT_RECORD *current_parent;
    register CELL *cons, *undef;
    CELL report, list;
    current_parent = parent;
    CacheParent2(prec->parent);
    report = prec->report;
    AllocUndef(undef);
    AllocCons(cons);
    cons[0] = *mesg;
    SetAll(cons+1, REF, undef, MRBOFF);
    SetAll(&(prec->report), REF, undef, MRBOFF);
    SetAll(&list, LIST, cons, MRBOFF);
    shoen_active_unify_with_list(&report, &list);
    CacheParent2(current_parent);
}

static shoen_active_unify_with_list(report, list)
    CELL *report, *list;
{
    OBJ	 *current_predicate_save;
    OBJ	 *current_predicate_save2;
    current_predicate_save = current_predicate;
    current_predicate_save2 = current_predicate2;
    current_predicate = NULL;
    current_predicate2 = NULL;
    active_unify_with_list(report, list);
    current_predicate = current_predicate_save;
    current_predicate2 = current_predicate_save2;
}


/*************************************************************************
*   Dump Shoen Tree for Debug.						 *
*************************************************************************/

inspect_shoen_tree()
{
    PrintCons("Shoen tree:\n");
    dump_shoen_tree(grand_mother, 0);
}

static dump_shoen_tree(root, level)
    PARENT_RECORD *root;
    int level;
{
    PARENT_RECORD *prec=root->left_son;
    printf("%c%04d",
	   root->status==READY ? 'R' : (root->status==ABORTED ? 'A' : 'S'),
	   root->id);
    if(prec!=root){
	if(root->left_son==root->right_son){
	    printf("--");
	}else{
	    printf("-+");
	}
	dump_shoen_tree(prec, level+1);
	prec = prec->right_brother;
	while(prec!=root){
	    dump_shoen_tree_sub(root, level);
	    printf(" +");
	    dump_shoen_tree(prec, level+1);
	    prec = prec->right_brother;
	}
    }else{
	printf("\n");
    }
}

static dump_shoen_tree_sub(prec, level)
    PARENT_RECORD *prec;
    int level;
{
    if(level>0){
	dump_shoen_tree_sub(prec->parent, level-1);
	if(prec==prec->parent->right_son){
	    printf("       ");
	}else{
	    printf(" |     ");
	}
    }else{
	printf("     ");
    }
}
