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
*   b_create_shoen(Rcode,Rargv,Rpmin,Rpmax,Rtag,^Rshoen,^Rreport)	 *
*************************************************************************/

DCODE dc_create_shoen(void)
{
    blt_b_create_shoen(&R0, &R1, &R2, &R3, &R4, &R7, &R8);
    active_unify(&R5, &R7);
    active_unify(&R6, &R8);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_create_shoen(CELL *code, CELL *argv, CELL *pmin, CELL *pmax, CELL *tag, CELL *shoen, CELL *report)
{
    register CELL *x;
    CELL rep;
    x = pmin;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = pmax;
    Dereference(x);
    if(Typeof(x) != INT) goto suspend_or_exception;
    x = tag;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_create_shoen), x, IIIIIOO,
				 code, argv, pmin, pmax, tag, shoen, report);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==pmin ? 3 : (x==pmax ? 4 : 5)),
				   KL1B_B_CREATE_SHOEN, IIIIIOO,
				   code, argv, pmin, pmax, tag, shoen, report);
	}
    }else{
	if(Valueof(pmin) < 0 || Valueof(pmin) > PRIORITY_RATE_FULL){
	    body_builtin_exception(INCORRECT_PRIORITY, 3,
				   KL1B_B_CREATE_SHOEN, IIIIIOO,
				   code, argv, pmin, pmax, tag, shoen, report);
	}else if(Valueof(pmax) < 0 || Valueof(pmax) > PRIORITY_RATE_FULL ||
		 Valueof(pmin)+Valueof(pmax) > PRIORITY_RATE_FULL){
	    body_builtin_exception(INCORRECT_PRIORITY, 4,
				   KL1B_B_CREATE_SHOEN, IIIIIOO,
				   code, argv, pmin, pmax, tag, shoen, report);
/**
	}else if(Valueof(tag) == 0){
	    body_builtin_exception(RANGE_OVERFLOW, 5,
				   KL1B_B_CREATE_SHOEN, IIIIIOO,
				   code, argv, pmin, pmax, tag, shoen, report);
**/
	}else{
	    PARENT_RECORD *p;
	    p = create_shoen(code, argv, Valueof(pmin), Valueof(pmax),
			     Valueof(tag), &rep);
	    SetAll(shoen, SHOEN, p, MRBOFF);
	    *report = rep;
	}
    }
    return 0;
}


/*************************************************************************
*   b_start_shoen(Rshoen,^Rnewshoen)					 *
*************************************************************************/

DCODE dc_start_shoen(void)
{
    blt_b_start_shoen(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_start_shoen(CELL *shoen, CELL *newshoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_start_shoen), x, IO, shoen, newshoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_START_SHOEN, IO, shoen, newshoen);
	}
    }else{
	start_shoen(Shoenof(shoen), SUSP_D);
	*newshoen = *shoen;
    }
    return 0;
}


/*************************************************************************
*   b_stop_shoen(Rshoen,^Rnewshoen)					 *
*************************************************************************/

DCODE dc_stop_shoen(void)
{
    blt_b_stop_shoen(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_stop_shoen(CELL *shoen, CELL *newshoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_stop_shoen), x, IO, shoen, newshoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_STOP_SHOEN, IO, shoen, newshoen);
	}
    }else{
	stop_shoen(Shoenof(shoen), SUSP_D);
	*newshoen = *shoen;
    }
    return 0;
}


/*************************************************************************
*   b_abort_shoen(Rshoen,^Rnewshoen)					 *
*************************************************************************/

DCODE dc_abort_shoen(void)
{
    blt_b_abort_shoen(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_abort_shoen(CELL *shoen, CELL *newshoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_abort_shoen), x, IO, shoen, newshoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_ABORT_SHOEN, IO, shoen, newshoen);
	}
    }else{
	abort_shoen(Shoenof(shoen));
	*newshoen = *shoen;
    }
    return 0;
}


/*************************************************************************
*   b_remove_shoen(Rshoen)						 *
*************************************************************************/

DCODE dc_remove_shoen(void)
{
    blt_b_remove_shoen(&R0);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_remove_shoen(CELL *shoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_remove_shoen), x, I, shoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_REMOVE_SHOEN, I, shoen);
	}
    }else{
	remove_shoen(Shoenof(shoen));
    }
    return 0;
}


/*************************************************************************
*   b_shoen_statistics(Rshoen,^Rreduction,^Rnewshoen)			 *
*************************************************************************/

DCODE dc_shoen_statistics(void)
{
    blt_b_shoen_statistics(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_shoen_statistics(CELL *shoen, CELL *red, CELL *newshoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_shoen_statistics), x,
				 IOO, shoen, red, newshoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_SHOEN_STATISTICS,
				   IOO, shoen, red, newshoen);
	}
    }else{
	int s;
	s = shoen_statistics(Shoenof(shoen));
	*newshoen = *shoen;
	SetAll(red, INT, s, MRBOFF);
    }
    return 0;
}


/*************************************************************************
*   b_shoen_add_resource(Rshoen,Rreduction,^Rnewshoen)			 *
*************************************************************************/

DCODE dc_shoen_add_resource(void)
{
    blt_b_shoen_add_resource(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_shoen_add_resource(CELL *shoen, CELL *red, CELL *newshoen)
{
    register CELL *x;
    x = shoen;
    Dereference(x);
    if(Typeof(x) != SHOEN) goto suspend_or_exception;
    x = red;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_shoen_add_resource), x,
				 IIO, shoen, red, newshoen);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==shoen ? 1 : 2),
				   KL1B_B_SHOEN_ADD_RESOURCE,
				   IIO, shoen, red, newshoen);
	}
    }else{
	if(Valueof(red) < 0){
	    body_builtin_exception(RANGE_OVERFLOW, 2,
				   KL1B_B_SHOEN_ADD_RESOURCE,
				   IIO, shoen, red, newshoen);
	}else{
	    shoen_add_resource(Shoenof(shoen), Valueof(red));
	    *newshoen = *shoen;
	}
    }
    return 0;
}


/*************************************************************************
*   b_consume_resource(Rreduction)					 *
*************************************************************************/

DCODE dc_consume_resource(void)
{
    blt_b_consume_resource(&R0);
    reduction_left--;
#ifdef STATISTICS_REDUCTION
    STATISTICS_REDUCTION;
#endif
    return(NC_PROCEED);
}

int blt_b_consume_resource(CELL *red)
{
    register CELL *x;
    int reduction;
    x = red;
    Dereference(x);
    if(Typeof(x) != INT){
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_consume_resource), x, I, red);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_CONSUME_RESOURCE, I, red);
	}
    }else{
	reduction = Valueof(red);
	if(reduction < 0){
	    body_builtin_exception(RANGE_OVERFLOW, 1,
				   KL1B_B_CONSUME_RESOURCE, I, red);
	}else{
	    if(reduction < reduction_left){
		reduction_left -= reduction;
	    }else{
		register GOAL_RECORD *grec;
		reduction -= reduction_left-1+1;
		reduction_left = 1;
		GetGoalRecord(grec, 1);
		number_of_children++;
		grec->parent = Ref(parent);
		grec->code = Ref(CodeOfFunction(dc_consume_resource));
		grec->argn = 1;
		SetAll(&(grec->args[0]), INT, reduction, MRBOFF);
		SetGoalPriority(grec, INT, MAX_PRIORITY<<PRIORITY_SIFT_WIDTH);
		SetGoalPriority(grec, INT, logical_priority);
		grec->pcode = Ref(current_predicate2 ? current_predicate2
						 : current_predicate);
		grec->debug = NO_TRACE_GOAL;
		enqueue(grec);
	    }
	}
    }
    return 0;
}
