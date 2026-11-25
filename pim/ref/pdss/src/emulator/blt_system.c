/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "instr.h"
#include "tracer.h"


/*************************************************************************
*   display_console(Rdata)						 *
*************************************************************************/

int blt_display_console(CELL *x)
{
    SelectWindow(CONSOLE);
    print_term(x, PRINT_LENGTH, PRINT_DEPTH);
    putchar('\n'); Flush();
}


/*************************************************************************
*   put_console(Rdata)							 *
*************************************************************************/

int blt_put_console(CELL *x)
{
    SelectWindow(CONSOLE);
    Dereference(x);
    switch(Typeof(x)){
      case INT:	   putchar(Valueof(x)); break;
      case STRING: print_string(x);	break;
    }
    Flush();
}


/*************************************************************************
*   read_console(^Rdata)						 *
*************************************************************************/

int blt_read_console(CELL *x)
{
    CHAR buffer[16];
    int work;
    ShowWindow(CONSOLE);
    if(read_console("Read Console: ", buffer, 16) < 0){
  exit_by_eof:
	remove_all_windows();
	RemoveWindow(CONSOLE);
	exit_pdss(0);
    }
    while(sscanf(buffer, "%d", &work) != 1){
	if(read_console("           :: ", buffer, 16) < 0) goto exit_by_eof;
    }
    SetAll(x, INT, work, MRBOFF);
}


/*************************************************************************
*   apply(Rcode,Rargv)							 *
*************************************************************************/

DCODE dc_apply(void)
{
    blt_b_apply(&R0, &R1);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_apply(CELL *code, CELL *argv)
{
    register CELL *x, *y;
    register MRB mrb;
    register GOAL_RECORD *grec;
    MODULE_ENTRY *mtbl;
    OBJ *obj;
    unsigned int mod, pred, arity;

    x = code;
    Dereference(x);
    if(Typeof(x) != VECTOR){
	if(Typeof(x) == ATOM && Valueof(x) ==  NIL) return 0;
	goto suspend_or_exception;
    }
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

    x = argv;
    Dereference(x);
    if(Typeof(x) != VECTOR){
  suspend_or_exception:
	if(!IsRef(x)) goto exception;
	GetGoalRecord(grec, 2);
	number_of_children++;
	grec->parent = Ref(parent);
	grec->code = Ref(CodeOfFunction(dc_apply));
	grec->argn = 2;
	grec->args[0] = *code;
	grec->args[1] = *argv;
	SetGoalPriority(grec, INT, logical_priority);
	grec->debug = goal_debug_status;
	grec->pcode = 0;
	single_wait_suspend(grec, x);
	return 0;
    }
    if(VectorLengthof(argv) != arity){
  exception:
	body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==argv ? 2 : 1),
			       KL1B_B_APPLY, II, code, argv);
	return 0;
    }

    if(lookup_module(mod, &mtbl) == MODMAN_MODULE_NOT_FOUND){
	body_goal_exception2(MODULE_NOT_FOUND, code, argv);
	return 0;
    }
    obj = find_predicate(mtbl, (arity<<16)|pred);
    if(obj == NULL){
	body_goal_exception2(PREDICATE_NOT_FOUND, code, argv);
	return 0;
    }
    GetGoalRecord(grec, arity);
    number_of_children++;
    grec->parent = Ref(parent);
    grec->code = Ref(obj);
    grec->argn = arity;
    x = grec->args;
    y = Objectof(argv);
    mrb = Mrbof(argv);
    while(arity--){
	y++;
	Dereference(y);
	if(mrb == MRBON) SetMrbof(y, MRBON);
	*x = *y; x++;
    }
    grec->debug = goal_debug_status;
    grec->pcode = 0;
    SetGoalPriority(grec, INT, logical_priority);
    enqueue(grec);
    if(Mrbof(code) == MRBOFF){
	FreeVector2(Objectof(code), 3);
	mrbgc_statistics_collect_in_builtin(4);
    }
    if(Mrbof(argv) == MRBOFF){
	FreeVector(Objectof(argv), grec->argn);
	mrbgc_statistics_collect_in_builtin(grec->argn+1);
    }
    return 0;
}


/*************************************************************************
*   raise(Rtag,Rkey,Rinfo)						 *
*************************************************************************/

DCODE dc_raise(void)
{
    blt_b_raise(&R0, &R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_raise(CELL *tag, CELL *key, CELL *info)
{
    ClearSuspensionStack();
    Dereference(tag);
    if(Typeof(tag) != INT){
	if(IsRef(tag)){
	    PushToSuspensionStack(tag);
	    goto suspend;
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_RAISE, III, tag, key, info);
	    return 0;
	}
    }
    if(Valueof(tag) == 0){
	body_builtin_exception(RANGE_OVERFLOW, 1,
			       KL1B_B_RAISE, III, tag, key, info);
	return 0;
    }
    if(!is_ground(key, MRBOFF, PASSIVE_UNIFY_DEPTH)){
	if(IsSuspensionStackEmpty()){
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 2,
				   KL1B_B_RAISE, III, tag, key, info);
	}else{
	    register GOAL_RECORD *grec;
  suspend:
	    GetGoalRecord(grec, 3);
	    number_of_children++;
	    grec->parent = Ref(parent);
	    grec->code = Ref(CodeOfFunction(dc_raise));
	    grec->argn = 3;
	    grec->args[0] = *tag;
	    grec->args[1] = *key;
	    grec->args[2] = *info;
	    SetGoalPriority(grec, INT, logical_priority);
	    grec->debug = goal_debug_status;
	    grec->pcode = Ref(current_predicate2 ? current_predicate2
					     : current_predicate);
	    popup_suspension_stack(grec);
	}
	return 0;
    }
    pdss_raise(Valueof(tag), key, info);
}


/*************************************************************************
*   merge(^Rin,^Rout)							 *
*************************************************************************/

int blt_b_merge(CELL *in, CELL *out)
{
    register MERGER_RECORD *merger;
    register CELL *mghok, *undef;
    AllocMerger(merger);
    AllocMghok(mghok);
    AllocUndef(undef);
    SetMergerof(mghok, merger);
    SetAll(in, REF, mghok, MRBOFF);
    SetAll(out, REF, undef, MRBOFF);
    SetAll(&(merger->output), REF, undef, MRBOFF);
    merger->count    = 1;
    merger->priority = logical_priority;
    merger->parent   = Ref(parent);
    merger->pcode    = Ref(current_predicate);
    number_of_children++;
}


/*************************************************************************
*   current_node(^Rcurrent,^Rtotal)					 *
*************************************************************************/

int blt_b_current_node(CELL *cp, CELL *tp)
{
    SetAll(cp, INT, 0, MRBOFF);
    SetAll(tp, INT, 1, MRBOFF);
}


/*************************************************************************
*   current_processor(^Rcurrent,^Rx,^Ry)				 *
*************************************************************************/

int blt_b_current_processor(CELL *cp, CELL *sx, CELL *sy)
{
    SetAll(cp, INT, 0, MRBOFF);
    SetAll(sx, INT, 1, MRBOFF);
    SetAll(sy, INT, 1, MRBOFF);
}


/*************************************************************************
*   current_priority(^Rcurrent,^Rmin,^Rmax)				 *
*************************************************************************/

int blt_b_current_priority(CELL *cp, CELL *min, CELL *max)
{
    SetAll(cp, INT, logical_priority, MRBOFF);
    SetAll(min, INT, parent->priority_min, MRBOFF);
    SetAll(max, INT, parent->priority_max, MRBOFF);
}


/*************************************************************************
*   rate(Rin,^Rout)							 *
*************************************************************************/

DCODE dc_rate(void)
{
    blt_b_rate(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_rate(CELL *rate, CELL *prio)
{
    Dereference(rate);
    if(Typeof(rate) != INT){
	if(IsRef(rate)){
	    body_builtin_suspend(CodeOfFunction(dc_rate), rate, IO, rate, prio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_RATE, IO, rate, prio);
	}
    }else{
	register int x;
	register unsigned p1, p2;
	x = Valueof(rate);
	if(x >= 0 && x <= PRIORITY_RATE_FULL){
	    p1 = parent->priority_min;
	    p2 = parent->priority_max;
	    p1 = p1+(((p2-p1)>>PRIORITY_RATE_WIDTH)*x)
		+((((p2-p1)&(PRIORITY_RATE_FULL-1))*x)>>PRIORITY_RATE_WIDTH);
	}else{
	    body_builtin_exception(INCORRECT_PRIORITY, 1,
				   KL1B_B_RATE, IO, rate, prio);
	    return 0;
	}
	SetAll(prio, INT, p1, MRBOFF);
    }
}


/*************************************************************************
*   rltv(Rin,^Rout)							 *
*************************************************************************/

DCODE dc_rltv(void)
{
    blt_b_rltv(&R0, &R2);
    active_unify(&R1, &R2);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_rltv(CELL *rate, CELL *prio)
{
    Dereference(rate);
    if(Typeof(rate) != INT){
	if(IsRef(rate)){
	    body_builtin_suspend(CodeOfFunction(dc_rltv), rate, IO, rate, prio);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, 1,
				   KL1B_B_RLTV, IO, rate, prio);
	}
    }else{
	register int x;
	register unsigned p1, p2;
	x = Valueof(rate);
	if(x >= 0 && x <= PRIORITY_RATE_FULL){
	    p1 = logical_priority;
	    p2 = parent->priority_max;
	    p1 = p1+(((p2-p1)>>PRIORITY_RATE_WIDTH)*x)
		+((((p2-p1)&(PRIORITY_RATE_FULL-1))*x)>>PRIORITY_RATE_WIDTH);
	}else if(x < 0 && x >= -PRIORITY_RATE_FULL){
	    x = -x;
	    p1 = logical_priority;
	    p2 = parent->priority_min;
	    p1 = p1-(((p1-p2)>>PRIORITY_RATE_WIDTH)*x)
		-((((p1-p2)&(PRIORITY_RATE_FULL-1))*x)>>PRIORITY_RATE_WIDTH);
	}else{
	    body_builtin_exception(INCORRECT_PRIORITY, 1,
				   KL1B_B_RLTV, IO, rate, prio);
	    return 0;
	}
	SetAll(prio, INT, p1, MRBOFF);
    }
}


/*************************************************************************
*   hash(Rx,^Rhash,^Rnewx)						 *
*************************************************************************/

DCODE dc_hash(void)
{
    blt_b_hash(&R0, &R3, &R4);
    active_unify(&R1, &R3);
    active_unify(&R2, &R4);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_hash(CELL *x, CELL *hv, CELL *newx)
{
    Dereference(x);
    if(IsRef(x)){
	body_builtin_suspend(CodeOfFunction(dc_hash), x, IOO, x, hv, newx);
    }else{
	unsigned int h;
	switch(Typeof(x)){
	  case ATOM:
	  case INT:
	  case FLOAT:
	    h = Valueof(x);
	    break;
	  case LIST:
	    h = -1;
	    break;
	  case VECTOR:
	    h = VectorLengthof(x);
	    break;
	  case STRING:
	    h = StringLengthof(x);
	    if(h != 0){
		h += (unsigned int)Valueof(Objectof(x)+1)
		  + ((unsigned int)Valueof(Objectof(x)+1)>>16)
		  + ((unsigned int)Valueof(Objectof(x)+1)>>24)
		  + ((unsigned int)Valueof(Objectof(x)+h)<<1)
		  + ((unsigned int)Valueof(Objectof(x)+h)>>15)
		  + ((unsigned int)Valueof(Objectof(x)+h)>>23);
	    }
	    break;
	  default:
	    h = 0;
	    break;
	}
	*newx = *x;
	SetAll(hv, INT, h, MRBOFF);
    }
}


/*************************************************************************
*   unbound(Rx,^Rpe,^Raddr,^Rnewx)  ...  old fashion.			 *
*************************************************************************/

int blt_b_unbound(CELL *x, CELL *pe, CELL *addr, CELL *newx)
{
    Dereference(x);
    if(IsRef(x)){
	*newx = *x;
	SetAll(addr, INT, Objectof(x)-heap1, MRBOFF);
	SetAll(pe, INT, 0, MRBOFF);
    }else{
	*newx = *x;
	*addr = const_nil;
	*pe = const_nil;
    }
}


/*************************************************************************
*   unbound(Rx,^Rresult)						 *
*************************************************************************/

int blt_b_unbound2(CELL *x, CELL *result)
{
    register CELL *r;
    Dereference(x);
    if(IsRef(x)){
	AllocVector2(r, 3);
	r[3] = *x;
	SetAll(r+1, INT, 0, MRBOFF);
	SetAll(r+2, INT, Objectof(x)-heap1, MRBOFF);
	SetAll(result, VECTOR, r, MRBOFF);
    }else{
	AllocVector2(r, 1);
	r[1] = *x;
	SetAll(result, VECTOR, r, MRBOFF);
    }
}


/*************************************************************************
*   get_print_image(Rx,Rmode,Rleft,^Rstr,^Rlength,^Rtail)		 *
*************************************************************************/

DCODE dc_get_print_image(void)
{
    blt_b_get_print_image(&R0, &R1, &R2, &R6, &R7, &R8);
    active_unify(&R3, &R6);
    active_unify(&R4, &R7);
    active_unify(&R5, &R8);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_print_image(CELL *atomic, CELL *mode, CELL *left, CELL *string, CELL *len, CELL *tail)
{
    register CELL *x;
    x = atomic;
    Dereference(x);
    if(Typeof(x) != ATOM && Typeof(x) != INT && Typeof(x) != FLOAT &&
       !(Typeof(x) == STRING && (StringTypeof(x)&0xE7) == 0x03)){
	goto suspend_or_exception;
    }
    x = mode;
    Dereference(x);
    if(Typeof(x) != INT){
	goto suspend_or_exception;
    }
    x = left;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_get_print_image), x, IIIOOO,
				 atomic, mode, left, string, len, tail);
	}else{
	    body_builtin_exception(ILLEGAL_INPUT_TYPE,
				   (x==atomic ? 1 : (x==mode ? 2 : 3)),
				   KL1B_B_GET_PRINT_IMAGE,
				   IIIOOO, atomic,mode,left,string,len,tail);
	}
    }else{
	CELL s;
	int l, t;
	if(get_print_image(atomic, Valueof(mode), Valueof(left), &s, &l, &t)
	   == STRUTL_REQUEST_GC){
	    SetHeapGcFlag();
	    body_builtin_swap(CodeOfFunction(dc_get_print_image),
			      IIIOOO, atomic, mode, left, string, len, tail);
	    return 0;
	}
	if(Typeof(atomic) == STRING && Mrbof(atomic) == MRBOFF){
	    FreeString(Objectof(atomic), StringLengthof(atomic));
	    mrbgc_statistics_collect_in_builtin(StringLengthof(atomic)+1);
	}
	*string = s;
	SetAll(len, INT, l, MRBOFF);
	SetAll(tail, INT, t, MRBOFF);
    }
}


/*************************************************************************
*   statistics(^Rcpu,^Rhsize,^Rhused,^Rcsize,^Rcused,^Rsystem)		 *
*************************************************************************/

int blt_statistics(CELL *ct, CELL *hs, CELL *hu, CELL *cs, CELL *cu, CELL *sy)
{
    long uspent;
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    uspent = usage.ru_utime.tv_sec*1000
	   + usage.ru_utime.tv_usec/1000;
    SetAll(ct, INT, uspent,	      MRBOFF);
    SetAll(hs, INT, HeapSize(),	      MRBOFF);
    SetAll(hu, INT, HeapUsed(),	      MRBOFF);
    SetAll(cs, INT, CodeSize(),	      MRBOFF);
    SetAll(cu, INT, CodeUsed(),	      MRBOFF);
    SetAll(sy, INT, SystemCodeSize(), MRBOFF);
}


/*************************************************************************
*   get_cpu_time(^Rcpu)							 *
*************************************************************************/

int blt_get_cpu_time(CELL *cpu)
{
    long uspent;
    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);
    uspent = usage.ru_utime.tv_sec*1000
	   + usage.ru_utime.tv_usec/1000;
    SetAll(cpu, INT, uspent, MRBOFF);
}


/*************************************************************************
*   get_current_time(^Ryear,^Rmonth,^Rday,^Rhour,^Rminute,^Rsecond)	 *
*************************************************************************/

int blt_get_current_time(CELL *year, CELL *month, CELL *day, CELL *hour, CELL *minute, CELL *second)
{
    time_t clock;
    struct tm *tm;
    time(&clock);
    tm = localtime(&clock);
    SetAll(year,   INT, tm->tm_year+1900, MRBOFF);
    SetAll(month,  INT, tm->tm_mon+1,	  MRBOFF);
    SetAll(day,	   INT, tm->tm_mday,	  MRBOFF);
    SetAll(hour,   INT, tm->tm_hour,	  MRBOFF);
    SetAll(minute, INT, tm->tm_min,	  MRBOFF);
    SetAll(second, INT, tm->tm_sec,	  MRBOFF);
}


/*************************************************************************
*   tag_and_value(Rdata,^Rtag,^Rvalue)					 *
*************************************************************************/

int blt_g_tag_and_value(CELL *data, CELL *tag, CELL *value)
{
    int t, v;
    Dereference(data);
    if(IsRef(data)){
	PushToSuspensionStack(data);
	return(NO);
    }
    t = Typeof(data);
    v = Valueof(data);
    SetAll(tag  ,INT,t,MRBOFF);
    SetAll(value,INT,v,MRBOFF);
    return(YES);
}


/*************************************************************************
*   register_tag_and_value(Rdata,^Rtag,^Rvalue)				 *
*************************************************************************/

int blt_g_register_tag_and_value(CELL *data, CELL *tag, CELL *value)
{
    int t, v;
    t = Typeof(data);
    v = Valueof(data);
    SetAll(tag  ,INT,t,MRBOFF);
    SetAll(value,INT,v,MRBOFF);
    return(YES);
}


/*************************************************************************
*   word(Raddress,^Rtag,^Rvalue)					 *
*************************************************************************/

int blt_g_word(CELL *addr, CELL *tag, CELL *value)
{
    int t, v;
    Dereference(addr);
    if(Typeof(addr) != INT){
	if(IsRef(addr)) PushToSuspensionStack(addr);
	return(NO);
    }
    addr = Objectof(addr);
    t = Typeof(addr);
    v = Valueof(addr);
    SetAll(tag  ,INT,t,MRBOFF);
    SetAll(value,INT,v,MRBOFF);
    return(YES);
}


/*************************************************************************
*   set_tag_and_value(^Rdata,Rtag,Rvalue)				 *
*************************************************************************/

int blt_g_set_tag_and_value(CELL *data, CELL *tag, CELL *value)
{
    int t, v;
    t = Valueof(tag);
    v = Valueof(value);
    SetAll(data,t,v,MRBOFF);
    return(YES);
}


/*************************************************************************
*   halt(Rexitcode)							 *
*************************************************************************/

int blt_g_halt(CELL *code)
{
    Dereference(code);
    if(Typeof(code) == INT){
	remove_all_windows();
	RemoveWindow(CONSOLE);
	exit_pdss(Valueof(code));
    }
    if(IsRef(code)) PushToSuspensionStack(code);
    return(NO);
}


/*************************************************************************
*   request_gc(Rflag)							 *
*************************************************************************/

int blt_g_request_gc(CELL *flag)
{
    Dereference(flag);
    if(Typeof(flag) != INT){
	if(IsRef(flag)) PushToSuspensionStack(flag);
	return(NO);
    }
    if(Valueof(flag)&1){
	SetCodeGcFlag();
    }else{
	SetHeapGcFlag();
    }
    return(YES);
}


/*************************************************************************
*   set_scheduling_switch(Rflag)					 *
*************************************************************************/

int blt_g_set_scheduling_switch(CELL *flag)
{
    Dereference(flag);
    if(Typeof(flag) != INT){
	if(IsRef(flag)) PushToSuspensionStack(flag);
	return(NO);
    }
    if(Valueof(flag)&1){
	breadth_first_flag = YES;
	option_execute_limit = 100;
    }else{
	breadth_first_flag = NO;
	option_execute_limit = 0;
    }
    return(YES);
}


/*************************************************************************
*   set_trace_switch(Rflag)						 *
*************************************************************************/

int blt_g_set_trace_switch(CELL *flag)
{
    Dereference(flag);
    if(Typeof(flag) != INT){
	if(IsRef(flag)) PushToSuspensionStack(flag);
	return(NO);
    }
    if(Valueof(flag)&1){
	set_trace_status(STEP_TRACE);
    }else{
	set_trace_status(NO_TRACE);
    }
    return(YES);
}


/*************************************************************************
*   set_backtrace_switch(Rflag)						 *
*************************************************************************/

int blt_g_set_backtrace_switch(CELL *flag)
{
    Dereference(flag);
    if(Typeof(flag) != INT){
	if(IsRef(flag)) PushToSuspensionStack(flag);
	return(NO);
    }
    if(Valueof(flag)&1){
	backtrace_flag = YES;
    }else{
	backtrace_flag = NO;
    }
    return(YES);
}


/*************************************************************************
*   get_all_atom_name(^Rlist)						 *
*************************************************************************/

DCODE dc_get_all_atom_name(void)
{
    blt_b_get_all_atom_name(&R0);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_get_all_atom_name(CELL *list)
{
    register CELL *cons, *vect, *p;
    register unsigned int atom;
    CELL root;
    p = &root;
    for(atom = 0; atom < gensym_count1; atom++){
	AllocVector2(vect, 2);
	SetAll(vect+1, ATOM, atom, MRBOFF);
	if(atom_to_string(atom, vect+2) == STRUTL_REQUEST_GC){
	    SetHeapGcFlag();
	    body_builtin_swap(CodeOfFunction(dc_get_all_atom_name), O, list);
	    return 0;
	}
	AllocCons(cons);
	SetAll(p, LIST, cons, MRBOFF);
	SetAll(cons, VECTOR, vect, MRBOFF);
	p = cons+1;
    }
    *p = const_nil;
    *list = root;
}


/*************************************************************************
*   unix(Rcommand,Rflag,^Rstatus)					 *
*************************************************************************/

DCODE dc_unix(void)
{
    blt_b_unix(&R0, &R1, &R3);
    active_unify(&R2, &R3);
    CountDcodeReduction();
    return(NC_PROCEED);
}

int blt_b_unix(CELL *command, CELL *flag, CELL *status)
{
    register CELL *x;
    register int len, id;
    register CHAR *p;
    CHAR buffer[1024];
    x = command;
    Dereference(x);
    if(Typeof(x) != STRING) goto suspend_or_exception;
    x = flag;
    Dereference(x);
    if(Typeof(x) != INT){
  suspend_or_exception:
	if(IsRef(x)){
	    body_builtin_suspend(CodeOfFunction(dc_unix), x, IIO, command, flag, status);
	}else{
  exception:
	    body_builtin_exception(ILLEGAL_INPUT_TYPE, (x==command ? 1 : 2),
				   KL1B_B_UNIX, IIO, command, flag, status);
	}
	return 0;
    }
    if(convert_to_c_string(command, buffer, 960) == NULL){
	goto exception;
    }
    id = getpid();
    p = buffer;
    while(*p){
	if(p[0]=='$' && p[1]=='$' && p[2]=='$' && p[3]=='$' && p[4]=='$'){
	    *p++ = '0'+(id/10000)%10;
	    *p++ = '0'+(id/1000)%10;
	    *p++ = '0'+(id/100)%10;
	    *p++ = '0'+(id/10)%10;
	    *p++ = '0'+id%10;
	}else{
	    p++;
	}
    }
    len = p-buffer;
    switch(Valueof(flag)&3){
      case 0:
	sprintf(&buffer[len],
		" > /dev/null 2> /dev/null < /dev/null");
	break;
      case 1:
	sprintf(&buffer[len],
		" > /dev/null 2> /dev/null < /tmp/pdssI%05d", id);
	break;
      case 2:
	sprintf(&buffer[len],
		" > /tmp/pdssO%05d 2> /dev/null < /dev/null", id);
	break;
      case 3:
	sprintf(&buffer[len],
		" > /tmp/pdssO%05d 2> /dev/null < /tmp/pdssI%05d", id, id);
	break;
    }
    SetAll(status, INT, system(buffer), MRBOFF);
}


/*************************************************************************
*   b_get_library_directory(^Rname)					 *
*************************************************************************/

int blt_b_get_library_directory(CELL *name)
{
    SetAll(name, STRING, convert_to_kl1_string(PDSS_LIBDIR), MRBOFF);
}
