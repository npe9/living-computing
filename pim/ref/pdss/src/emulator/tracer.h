/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1992.					 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

/*** Trace Status ***/
#define NO_TRACE	      0
#define STEP_TRACE	      1
#define STEP_TO_SPIED_P_OR_G  2
#define STEP_TO_SPIED_P_AND_G 3
#define STEP_TO_SPIED_PRED    4
#define STEP_TO_SPIED_GOAL    5
#define NEXT_SPIED_P_OR_G     6
#define NEXT_SPIED_P_AND_G    7
#define NEXT_SPIED_PRED	      8
#define NEXT_SPIED_GOAL	      9
extern int trace_status;
extern int trace_intr_flag;

/*** Goal Status ***/
#define GATE_MASK 0x1F
#define GATE_CALL 0x01
#define GATE_EXEC 0x41
#define GATE_DEQU 0x81
#define GATE_SUSP 0x02
#define GATE_SPRI 0x82
#define GATE_RESU 0x04
#define GATE_SWAP 0x08
#define GATE_FAIL 0x10

/*** Trace Macros ***/
#define TraceCheck(STATUS)\
    (trace_intr_flag || (trace_status != NO_TRACE && !(STATUS&NO_TRACE_GOAL)))
#define TraceExecuteGoal(PC)\
    if(TraceCheck(goal_debug_status))\
	trace((PC), number_of_argument, regs, GATE_EXEC, NULL, parent)
#define TraceDequeueGoal(PC)\
    if(TraceCheck(goal_debug_status))\
	trace((PC), number_of_argument, regs, GATE_DEQU, NULL, parent)
#define TraceSuspendGoal(GOAL)\
    if(TraceCheck((GOAL)->debug))\
	trace(CodeOf((GOAL)->code), (GOAL)->argn, (GOAL)->args, GATE_SUSP,\
	      (GOAL), PrecOf((GOAL)->parent));
#define TracePrioritySuspendGoal(GOAL)\
    if(TraceCheck((GOAL)->debug))\
	trace(CodeOf((GOAL)->code), (GOAL)->argn, (GOAL)->args, GATE_SPRI,\
	      (GOAL), PrecOf((GOAL)->parent));
#define TraceResumeGoal(GOAL)\
    if(TraceCheck((GOAL)->debug))\
	trace(CodeOf((GOAL)->code), (GOAL)->argn, (GOAL)->args, GATE_RESU,\
	      (GOAL), PrecOf((GOAL)->parent));
#define TraceSwapGoal(GOAL)\
    if(TraceCheck((GOAL)->debug))\
	trace(CodeOf((GOAL)->code), (GOAL)->argn, (GOAL)->args, GATE_SWAP,\
	      (GOAL), PrecOf((GOAL)->parent));
#define TraceFailGoal(PC)\
    if(TraceCheck(goal_debug_status))\
	trace((PC), number_of_argument, regs, GATE_FAIL, NULL, parent)
