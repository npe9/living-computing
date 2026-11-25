/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"
#include "memory.h"
#include "io.h"
#include "klb.h"
#include "instr.h"
#include "tracer.h"
/* PORT: forward declarations */
static int do_interrupt();
static int idle();
static int idle2();


CELL regs[MAXREGS];
OBJ *PC;
OBJ *ACP;
unsigned int number_of_argument;
int goal_debug_status;
OBJ *current_predicate;	/* pointer to current predicate top */
OBJ *current_predicate2;
unsigned int priority;
unsigned int logical_priority;
PARENT_RECORD *parent;
int number_of_children;
int reduction_left;
int iflag;
#if TWO_WAY_READY_GOAL_POOL
int execute_limit;
int execute_counter;
#endif
#if INSTRUCTION_TRACE
int instruction_trace_flag;
#endif
#if INSTRUCTION_COUNT
unsigned int instruction_counter;
unsigned int instr__counter[256];
#if INSTRUCTION_BRANCH_COUNT
unsigned int instr__branch_acp[256];
unsigned int instr__branch_lab[256];
#endif
#endif

#define	 DUPLICATE_TABLE_SIZE  8
static int duplicate_table[DUPLICATE_TABLE_SIZE];


/*************************************************************************
*  KL1-B Emulator Top Level Loop -- emulate()				 *
*************************************************************************/

emulate()
{
    register OBJ *PCR;	/** Local Program Counter in emulate() **/
    register GOAL_RECORD *new_grec;
    CELL work;
    int i;

    ResetIflag();
    report_raise_flag = NO;
    shoen_tree_trace_flag = NO;
    backtrace_flag = NO;
#if TWO_WAY_READY_GOAL_POOL
    execute_limit = option_execute_limit;
#endif
#if INSTRUCTION_TRACE
    instruction_trace_flag = option_instruction_trace;
#endif
#if INSTRUCTION_COUNT
    instruction_counter = 0;
    for(i=0; i<256; i++) instr__counter[i]=0;
#if INSTRUCTION_BRANCH_COUNT
    for(i=0; i<256; i++) instr__branch_acp[i]=0;
    for(i=0; i<256; i++) instr__branch_lab[i]=0;
#endif
#endif
    goto proceed_to_next_goal;


/*************************************************************************
*  KL1 Predicate Level Loop						 *
*************************************************************************/

#define CallGc() { DecacheParent(); gc(); }
#define	Idle()	 { if(use_windows) idle(); else if(!idle2()) return; }

suspend_emulated_code_goal:
    DecacheGoal(new_grec, PCR);
    SetGoalPriority(new_grec, INT, logical_priority);
    popup_suspension_stack(new_grec);
    TraceSuspendGoal(new_grec);
    goto proceed_to_next_goal;

suspend_native_code_goal:
    DecacheGoal(new_grec, PC);
    SetGoalPriority(new_grec, INT, logical_priority);
    popup_suspension_stack(new_grec);

proceed_to_next_goal:
    if(InterruptOccurred()) do_interrupt();
    if(!dequeue()) Idle();
    PCR = PC;
#if TWO_WAY_READY_GOAL_POOL
    execute_counter = execute_limit;
#endif
    if(IsNativeCode(PCR)){
	goto next_native_predicate;
    }else{
	TraceDequeueGoal(PCR);
	goto next_emulated_predicate;
    }

swap_native_code_goal:
swap_goal_without_trace:
    DecacheGoal(new_grec, PCR);
    enqueue(new_grec);
    if(InterruptOccurred()) do_interrupt();
    if(!dequeue()) Idle();
    PCR = PC;
#if TWO_WAY_READY_GOAL_POOL
    execute_counter = execute_limit;
#endif
    if(IsNativeCode(PCR)){
	goto next_native_predicate;
    }else{
	TraceDequeueGoal(PCR);
	goto next_emulated_predicate;
    }

execute_next_predicate:
    if(!IsNativeCode(PCR)){
	if(InterruptOccurred() || IsResourceLimit() ||
	   higher_priority_flag){
	    DecacheGoal(new_grec, PCR);
	    TraceSwapGoal(new_grec);
	    enqueue(new_grec);
	    if(InterruptOccurred()) do_interrupt();
	    if(!dequeue()) Idle();
	    PCR = PC;
#if TWO_WAY_READY_GOAL_POOL
	    execute_counter = execute_limit;
#endif
	    if(!IsNativeCode(PCR)){
		TraceDequeueGoal(PCR);
		goto next_emulated_predicate;
	    }
#if TWO_WAY_READY_GOAL_POOL
	}else if(--execute_counter == 0){
	    enqueue_special_flag = 2;
	    DecacheGoal(new_grec, PCR);
	    TraceSwapGoal(new_grec);
	    enqueue(new_grec);
	    if(!dequeue()) Idle();
	    PCR = PC;
	    execute_counter = execute_limit;
	    if(!IsNativeCode(PCR)){
		TraceDequeueGoal(PCR);
		goto next_emulated_predicate;
	    }
#endif
	}else{
	    current_predicate = PCR;
	    TraceExecuteGoal(PCR);
	    goto next_emulated_predicate;
	}
    }else{
	if(InterruptOccurred() || IsResourceLimit() ||
				  higher_priority_flag){
	    DecacheGoal(new_grec, PCR);
	    enqueue(new_grec);
	    if(InterruptOccurred()) do_interrupt();
	    if(!dequeue()) Idle();
	    PCR = PC;
#if TWO_WAY_READY_GOAL_POOL
	    execute_counter = execute_limit;
#endif
	    if(!IsNativeCode(PCR)){
		TraceDequeueGoal(PCR);
		goto next_emulated_predicate;
	    }
	}else{
	    current_predicate = PCR;
	}
    }


/*************************************************************************
*  Execute Native Code Predicate					 *
*************************************************************************/

next_native_predicate:
    switch( (* ((int (*) ())PCR) )() ){	 /** Call(PCR) **/
      case NC_PROCEED:
	if(--number_of_children == 0){
	    terminate_shoen();
	    parent = NULL;
	}
      case NC_SUSPENDED:
	goto proceed_to_next_goal;
      case NC_SUSPEND:	/** Suspension stack is not empty **/
	goto suspend_native_code_goal;
      case NC_SUSPEND_OR_FAIL:
	if(!IsSuspensionStackEmpty()){
	    goto suspend_native_code_goal;
	}
      case NC_FAIL:
	{
	    unsigned int mod, pred, arity;
	    function_to_mod_pred_arity(PC, &mod, &pred, &arity);
	    body_goal_exception(REDUCTION_FAILED, mod, pred, arity, regs);
	    goto proceed_to_next_goal;
	}
      case NC_EXECUTE:
	PCR = PC;
	goto execute_next_predicate;
      case NC_SWAPGOAL:
	goto swap_native_code_goal;
    }


/*************************************************************************
*  Execute Emulated Code Predicate					 *
*************************************************************************/

#if INSTRUCTION_COUNT && INSTRUCTION_BRANCH_COUNT
#define CountBranchACP instr__branch_acp[GetOpCode(PCR)]++
#define CountBranchLAB instr__branch_lab[GetOpCode(PCR)]++
#else
#define CountBranchACP
#define CountBranchLAB
#endif

#define NextInstr(n)	{ PCR += (n); goto next_instruction; }
#define JumpInstr(pc)	{ CountBranchLAB; PCR = (pc); goto next_instruction; }
#define NextAlternative { CountBranchACP; PCR = ACP;  goto next_instruction; }

next_emulated_predicate:
#if TWO_WAY_READY_GOAL_POOL
    if(enqueue_special_flag) goto swap_goal_without_trace;
#endif
    ClearSuspensionStack();


/*************************************************************************
*  KL1-B Instruction Level Loop						 *
*************************************************************************/

next_instruction:
#if INSTRUCTION_TRACE
    if(instruction_trace_flag){
	CHAR buf[256];
	inverse_assemble_one(PCR, code_base, buf);
	PrintCons1F("%s\n", buf);
    }
#endif
#if INSTRUCTION_COUNT
    instruction_counter++;
    instr__counter[GetOpCode(PCR)]++;
#endif
#ifdef STATISTICS_INSTRUCTION
    STATISTICS_INSTRUCTION;
#endif


/*************************************************************************
*  KL1-B Instructions (Standard Code -- 1byte OP Code)			 *
*************************************************************************/

switch(GetOpCode(PCR)){


/*** Control *************************************************************
*  1. true								 *
*  2. fail								 *
*  3. jump(Lab)								 *
*  4. try_me_else(Lab)							 *
*  5. otherwise(Lab)							 *
*  6. suspend(Lab)							 *
*  7. proceed								 *
*  8. execute(Arity,Lab)						 *
*  9. execute_external(Mod,Pred,Arity)					 *
* 10. create_goal(Arity)						 *
* 11. enqueue_goal(Arity,Lab)						 *
* 12. enqueue_goal_with_priority(Arity,Lab,Ai)				 *
* 13. enqueue_goal_external(Mod,Pred,Arity)				 *
*************************************************************************/

case KL1B_TRUE:{
    nop();  /* Used for Break Point */
    NextInstr(LEN_of_NO_ARG);
}

case KL1B_FAIL:{
    NextAlternative;
}

case KL1B_JUMP:{
    CountBranchLAB;
    PCR = GetAddr(PCR+LAB_of_LAB);
    goto next_instruction;
}

case KL1B_TRY_ME_ELSE:{
    ACP = GetAddr(PCR+LAB_of_LAB);
    NextInstr(LEN_of_LAB);
}

case KL1B_OTHERWISE:{
    if(IsSuspensionStackEmpty()){
	NextInstr(LEN_of_LAB);
    }else{
	GetPredicateSuspensionCount(current_predicate)++;
	PCR = GetAddr(PCR+LAB_of_LAB);
	goto suspend_emulated_code_goal;
    }
}

case KL1B_SUSPEND:{
    if(IsSuspensionStackEmpty()){  /* Reduction failed */
	PCR = GetAddr(PCR+LAB_of_LAB);
	TraceFailGoal(PCR);
	body_goal_exception(REDUCTION_FAILED,
		GetModuleName(GetModuleTop(PCR)),
		GetPredicateName(PCR), GetPredicateArity(PCR), regs);
	goto proceed_to_next_goal;
    }else{
	GetPredicateSuspensionCount(current_predicate)++;
	PCR = GetAddr(PCR+LAB_of_LAB);
	goto suspend_emulated_code_goal;
    }
}

case KL1B_PROCEED:{
    reduction_left--;
    GetPredicateReductionCount(current_predicate)++;
#ifdef STATISTICS_REDUCTION
    STATISTICS_REDUCTION;
#endif
    CountBranchLAB;
    if(--number_of_children == 0){
	terminate_shoen();
    }
    goto proceed_to_next_goal;
}

case KL1B_EXECUTE:{
    reduction_left--;
    GetPredicateReductionCount(current_predicate)++;
#ifdef STATISTICS_REDUCTION
    STATISTICS_REDUCTION;
#endif
    CountBranchLAB;
    number_of_argument = GetPredArity(PCR+PARITY_of_PARITY_LAB);
    PCR = GetAddr(PCR+LAB_of_PARITY_LAB);
    goto execute_next_predicate;
}

case KL1B_EXECUTE_EXTERNAL:{
    unsigned int module, pid;
    MODULE_ENTRY *maddr;
    reduction_left--;
    GetPredicateReductionCount(current_predicate)++;
#ifdef STATISTICS_REDUCTION
    STATISTICS_REDUCTION;
#endif
    CountBranchLAB;
    module = GetAtom(PCR+MOD_of_MOD_PRED_PARITY);
    pid = GetPredID(PCR+PRED_of_MOD_PRED_PARITY);
    number_of_argument = GetPredArity(PCR+PARITY_of_MOD_PRED_PARITY);
    if(lookup_module(module, &maddr) == MODMAN_MODULE_NOT_FOUND){
	/** Module isn't defined yet. **/
	number_of_children--;
	body_goal_exception(MODULE_NOT_FOUND,
			    module, pid&0xFFFF, number_of_argument, regs);
	goto proceed_to_next_goal;
    }
    PCR = find_predicate(maddr, pid);
    if(PCR == NULL){
	/** Predicate isn't defined. **/
	number_of_children--;
	body_goal_exception(PREDICATE_NOT_FOUND,
			    module, pid&0xFFFF, number_of_argument, regs);
	goto proceed_to_next_goal;
    }
    goto execute_next_predicate;
}

case KL1B_CREATE_GOAL:{
    register unsigned int arity;
    arity = GetPredArity(PCR+PARITY_of_PARITY);
    GetGoalRecord(new_grec, arity);
    NextInstr(LEN_of_PARITY);
}

case KL1B_ENQUEUE_GOAL:{
    number_of_children++;
    new_grec->parent = parent;
    new_grec->argn = GetPredArity(PCR+PARITY_of_PARITY_LAB);
    new_grec->code = GetAddr(PCR+LAB_of_PARITY_LAB);
    new_grec->pcode = current_predicate2;
    new_grec->debug = goal_debug_status;
    SetGoalPriority(new_grec, INT, logical_priority);
    enqueue(new_grec);
    NextInstr(LEN_of_PARITY_LAB);
}

case KL1B_ENQUEUE_GOAL_WITH_PRIORITY:{
    number_of_children++;
    new_grec->parent = parent;
    new_grec->argn = GetPredArity(PCR+PARITY_of_PARITY_LAB_REG);
    new_grec->code = GetAddr(PCR+LAB_of_PARITY_LAB_REG);
    new_grec->pcode = current_predicate2;
    new_grec->debug = goal_debug_status;
    new_grec->priority = *GetRi(PCR+REG_of_PARITY_LAB_REG);
    enqueue_with_priority(new_grec);
    NextInstr(LEN_of_PARITY_LAB_REG);
}

case KL1B_ENQUEUE_GOAL_EXTERNAL:{
    unsigned int module, pid, arity;
    MODULE_ENTRY *maddr;
    OBJ *code;
    module = GetAtom(PCR+MOD_of_MOD_PRED_PARITY);
    pid = GetPredID(PCR+PRED_of_MOD_PRED_PARITY);
    arity = GetPredArity(PCR+PARITY_of_MOD_PRED_PARITY);
    if(lookup_module(module, &maddr) == MODMAN_MODULE_NOT_FOUND){
	/** Module isn't defined yet. **/
	body_goal_exception(MODULE_NOT_FOUND,
			    module, pid&0xFFFF, arity, new_grec->args);
	FreeGoalRecord(new_grec, arity);
	NextInstr(LEN_of_MOD_PRED_PARITY);
    }
    code = find_predicate(maddr, pid);
    if(code == NULL){
	/** Predicate isn't defined. **/
	body_goal_exception(PREDICATE_NOT_FOUND,
			    module, pid&0xFFFF, arity, new_grec->args);
	FreeGoalRecord(new_grec, arity);
	NextInstr(LEN_of_MOD_PRED_PARITY);
    }
    number_of_children++;
    new_grec->parent = parent;
    new_grec->argn = arity;
    new_grec->code = code;
    new_grec->pcode = current_predicate2;
    new_grec->debug = goal_debug_status;
    SetGoalPriority(new_grec, INT, logical_priority);
    enqueue(new_grec);
    NextInstr(LEN_of_MOD_PRED_PARITY);
}


/*** Wait Bounded Value **************************************************
*  1. wait(Reg)								 *
*************************************************************************/

case KL1B_WAIT:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG);
    Dereference(reg);
    if(IsRef(reg)){
	PushToSuspensionStack(reg);
	NextAlternative;
    }else{
	NextInstr(LEN_of_REG);
    }
}


/*** Check Type **********************************************************
*  1. is_atom(Reg,Lab)							 *
*  2. is_integer(Reg,Lab)						 *
*  3. is_float(Reg,Lab)							 *
*  4. is_list(Reg,Lab)							 *
*  5. is_vector(Reg,Lab)						 *
*  6. is_string(Reg,Lab)						 *
*  7. switch_on_type(Reg,Latom,Lint,Llist,Lvect,Lstr,Lfail)		 *
*************************************************************************/

#define CHECK_TYPE(WTYPE){\
    if(Typeof(GetRi(PCR+REG_of_REG_LAB)) == WTYPE){\
	NextInstr(LEN_of_REG_LAB);\
    }else{\
	JumpInstr(GetAddr(PCR+LAB_of_REG_LAB));\
    }\
}

case KL1B_IS_ATOM:    CHECK_TYPE(ATOM);
case KL1B_IS_INTEGER: CHECK_TYPE(INT);
case KL1B_IS_FLOAT:   CHECK_TYPE(FLOAT);
case KL1B_IS_LIST:    CHECK_TYPE(LIST);
case KL1B_IS_VECTOR:  CHECK_TYPE(VECTOR);
case KL1B_IS_STRING:  CHECK_TYPE(STRING);

case KL1B_SWITCH_ON_TYPE:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_LAB6);
    switch(Typeof(reg)){
      case ATOM:   JumpInstr(GetAddr(PCR+LB1_of_REG_LAB6));
      case INT:	   JumpInstr(GetAddr(PCR+LB2_of_REG_LAB6));
      case LIST:   JumpInstr(GetAddr(PCR+LB3_of_REG_LAB6));
      case VECTOR: JumpInstr(GetAddr(PCR+LB4_of_REG_LAB6));
      case STRING: JumpInstr(GetAddr(PCR+LB5_of_REG_LAB6));
      DEFAULT:	   JumpInstr(GetAddr(PCR+LB6_of_REG_LAB6));
    }
}


/*** Check Value, Arity **************************************************
*  1. test_atom(Reg,Atom,Lab)						 *
*  2. test_nil(Reg,Lab)							 *
*  3. test_integer(Reg,Int,Lab)						 *
*  4. test_float(Reg,Float,Lab)						 *
*  5. test_arity(Reg,Arity,Lab)						 *
*  6. jump_on_integer(Reg,Size,Lab)					 *
*  7. jump_on_arity(Reg,Size,Lab)					 *
*  8. branch_on_atom(Reg,Size,Lab)					 *
*  9. branch_on_integer(Reg,Size,Lab)					 *
* 10. hash_on_atom(Reg,Mask,Lab)					 *
* 11. hash_on_integer(Reg,Mask,Lab)					 *
*************************************************************************/

case KL1B_TEST_ATOM:{
    if(Valueof(GetRi(PCR+REG_of_REG_ATM_LAB))
	   == GetAtom(PCR+ATM_of_REG_ATM_LAB)){
	NextInstr(LEN_of_REG_ATM_LAB);
    }else{
	JumpInstr(GetAddr(PCR+LAB_of_REG_ATM_LAB));
    }
}

case KL1B_TEST_NIL:{
    if(Valueof(GetRi(PCR+REG_of_REG_LAB)) == NIL){
	NextInstr(LEN_of_REG_LAB);
    }else{
	JumpInstr(GetAddr(PCR+LAB_of_REG_LAB));
    }
}

case KL1B_TEST_INTEGER:{
    if(Valueof(GetRi(PCR+REG_of_REG_IT_LAB))
	     == GetInt(PCR+IT_of_REG_IT_LAB)){
	NextInstr(LEN_of_REG_IT_LAB);
    }else{
	JumpInstr(GetAddr(PCR+LAB_of_REG_IT_LAB));
    }
}

case KL1B_TEST_FLOAT:{
    if(Valueof(GetRi(PCR+REG_of_REG_FLOT_LAB))
	     == GetFloat(PCR+FLOT_of_REG_FLOT_LAB)){
	NextInstr(LEN_of_REG_FLOT_LAB);
    }else{
	JumpInstr(GetAddr(PCR+LAB_of_REG_FLOT_LAB));
    }
}

case KL1B_TEST_ARITY:{
    if(VectorLengthof(GetRi(PCR+REG_of_REG_ARITY_LAB))
		== GetArity(PCR+ARITY_of_REG_ARITY_LAB)){
	NextInstr(LEN_of_REG_ARITY_LAB);
    }else{
	JumpInstr(GetAddr(PCR+LAB_of_REG_ARITY_LAB));
    }
}

case KL1B_JUMP_ON_INTEGER:{
    register unsigned int inte;
    inte = Valueof(GetRi(PCR+REG_of_JUMP_ON));
    if(inte < GetUShort(PCR+SIZE_of_JUMP_ON)){
	PCR += inte*ELEN_of_JUMP_ON+TABLE_of_JUMP_ON;
	JumpInstr(GetAddr(PCR+LAB_of_JUMP_ON));
    }else{
	JumpInstr(GetAddr(PCR+FAIL_of_JUMP_ON)); /** Fail Lable **/
    }
}

case KL1B_JUMP_ON_ARITY:{
    register unsigned int arity;
    arity = VectorLengthof(GetRi(PCR+REG_of_JUMP_ON));
    if(arity < GetUShort(PCR+SIZE_of_JUMP_ON)){
	PCR += arity*ELEN_of_JUMP_ON+TABLE_of_JUMP_ON;
	JumpInstr(GetAddr(PCR+LAB_of_JUMP_ON));
    }else{
	JumpInstr(GetAddr(PCR+FAIL_of_JUMP_ON)); /** Fail Lable **/
    }
}

case KL1B_BRANCH_ON_ATOM:{
    register unsigned int atom, size;
    register OBJ *fail;
    atom = Valueof(GetRi(PCR+REG_of_BRANCH_ON_A));
    size = GetUShort(PCR+SIZE_of_BRANCH_ON_A);	/* Table size */
    fail = GetAddr(PCR+FAIL_of_BRANCH_ON_A);	 /* Fail label */
    PCR += TABLE_of_BRANCH_ON_A;
    do{
	if(atom == GetAtom(PCR+ATM_of_BRANCH_ON_A)){
	    JumpInstr(GetAddr(PCR+LAB_of_BRANCH_ON_A));
	}
	PCR += ELEN_of_BRANCH_ON_A;
    }while(--size);
    JumpInstr(fail);
}

case KL1B_BRANCH_ON_INTEGER:{
    register int inte;
    register unsigned int size;
    register OBJ *fail;
    inte = Valueof(GetRi(PCR+REG_of_BRANCH_ON_I));
    size = GetUShort(PCR+SIZE_of_BRANCH_ON_I);	/* Table size */
    fail = GetAddr(PCR+FAIL_of_BRANCH_ON_I);	 /* Fail label */
    PCR += TABLE_of_BRANCH_ON_I;
    do{
	if(inte == GetInt(PCR+IT_of_BRANCH_ON_I)){
	    JumpInstr(GetAddr(PCR+LAB_of_BRANCH_ON_I));
	}
	PCR += ELEN_of_BRANCH_ON_I;
    }while(--size);
    JumpInstr(fail);
}

case KL1B_HASH_ON_ATOM:{
    register unsigned int atom, size;
    register OBJ *fail;
    atom = Valueof(GetRi(PCR+REG_of_HASH_ON_A));
    size = atom & GetUShort(PCR+MASK_of_HASH_ON_A);  /* Mask */
    fail = GetAddr(PCR+FAIL_of_HASH_ON_A);	 /* Fail label */
    PCR += size*TLEN_of_HASH_ON_A+TABLE_of_HASH_ON_A;
    size = GetUShort(PCR+CNUM_of_HASH_ON_A);  /* Collision number */
    PCR = GetAddr(PCR+OFST_of_HASH_ON_A);
    while(size--){
	if(atom == GetAtom(PCR+ATM_of_HASH_ON_A)){
	    JumpInstr(GetAddr(PCR+LAB_of_HASH_ON_A));
	}
	PCR += ELEN_of_HASH_ON_A;
    }
    JumpInstr(fail);
}

case KL1B_HASH_ON_INTEGER:{
    register int inte;
    register unsigned int size;
    register OBJ *fail;
    inte = Valueof(GetRi(PCR+REG_of_HASH_ON_I));
    size = inte & GetUShort(PCR+MASK_of_HASH_ON_I);  /* Mask */
    fail = GetAddr(PCR+FAIL_of_HASH_ON_I);	 /* Fail label */
    PCR += size*TLEN_of_HASH_ON_I+TABLE_of_HASH_ON_I;
    size = GetUShort(PCR+CNUM_of_HASH_ON_I);  /* Collision number */
    PCR = GetAddr(PCR+OFST_of_HASH_ON_I);
    while(size--){
	if(inte == GetInt(PCR+IT_of_HASH_ON_I)){
	    JumpInstr(GetAddr(PCR+LAB_of_HASH_ON_I));
	}
	PCR += ELEN_of_HASH_ON_I;
    }
    JumpInstr(fail);
}


/*** Wait Bounded Value & Check Type (1) *********************************
*  1. atom(Reg)								 *
*  2. integer(Reg)							 *
*  3. float(Reg)							 *
*  4. list(Reg)								 *
*  5. vector(Reg)							 *
*  6. string(Reg)							 *
*************************************************************************/

#define WAIT_AND_CHECK_TYPE1(WTYPE){\
    register CELL *reg;\
    reg = GetRi(PCR+REG_of_REG);\
    if(Typeof(reg) != WTYPE){ /* Optimize, Reg is nearly always bounded */\
	Dereference(reg);\
	if(Typeof(reg) != WTYPE){\
	    if(IsRef(reg)) PushToSuspensionStack(reg);\
	    NextAlternative;\
	}\
    }\
    NextInstr(LEN_of_REG);\
}

case KL1B_ATOM:	   WAIT_AND_CHECK_TYPE1(ATOM);
case KL1B_INTEGER: WAIT_AND_CHECK_TYPE1(INT);
case KL1B_FLOAT:   WAIT_AND_CHECK_TYPE1(FLOAT);
case KL1B_LIST:	   WAIT_AND_CHECK_TYPE1(LIST);
case KL1B_VECTOR:  WAIT_AND_CHECK_TYPE1(VECTOR);
case KL1B_STRING:  WAIT_AND_CHECK_TYPE1(STRING);


/*** Wait Bounded Value & Check Type (2) *********************************
*  1. jump_on_non_atom(Reg,Lab)						 *
*  2. jump_on_non_integer(Reg,Lab)					 *
*  3. jump_on_non_float(Reg,Lab)					 *
*  4. jump_on_non_list(Reg,Lab)						 *
*  5. jump_on_non_vector(Reg,Lab)					 *
*  6. jump_on_non_string(Reg,Lab)					 *
*************************************************************************/

#define WAIT_AND_CHECK_TYPE2(WTYPE){\
    register CELL *reg;\
    reg = GetRi(PCR+REG_of_REG_LAB);\
    if(Typeof(reg) != WTYPE){ /* Optimize, Reg is nearly always bounded */\
	Dereference(reg);\
	if(Typeof(reg) != WTYPE){\
	    if(IsRef(reg)){\
		PushToSuspensionStack(reg);\
		NextAlternative;\
	    }else{\
		JumpInstr(GetAddr(PCR+LAB_of_REG_LAB)); /* Fail Label */\
	    }\
	}\
    }\
    NextInstr(LEN_of_REG_LAB);\
}

case KL1B_JUMP_ON_NON_ATOM:    WAIT_AND_CHECK_TYPE2(ATOM);
case KL1B_JUMP_ON_NON_INTEGER: WAIT_AND_CHECK_TYPE2(INT);
case KL1B_JUMP_ON_NON_FLOAT:   WAIT_AND_CHECK_TYPE2(FLOAT);
case KL1B_JUMP_ON_NON_LIST:    WAIT_AND_CHECK_TYPE2(LIST);
case KL1B_JUMP_ON_NON_VECTOR:  WAIT_AND_CHECK_TYPE2(VECTOR);
case KL1B_JUMP_ON_NON_STRING:  WAIT_AND_CHECK_TYPE2(STRING);


/*** Check Type & Check Value ********************************************
*  1. check_atom(Reg,Atom,Lab)						 *
*  2. check_nil(Reg,Lab)						 *
*  3. check_integer(Reg,Int,Lab)					 *
*  4. check_float(Reg,Float,Lab)					 *
*  5. check_vector(Reg,Arity,Lab)					 *
*************************************************************************/

case KL1B_CHECK_ATOM:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_ATM_LAB);
    if(Typeof(reg) == ATOM &&
       Valueof(reg) == GetAtom(PCR+ATM_of_REG_ATM_LAB)){
	NextInstr(LEN_of_REG_ATM_LAB);
    }
    JumpInstr(GetAddr(PCR+LAB_of_REG_ATM_LAB));
}

case KL1B_CHECK_NIL:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_LAB);
    if(Typeof(reg) == ATOM && Valueof(reg) == NIL){
	NextInstr(LEN_of_REG_LAB);
    }
    JumpInstr(GetAddr(PCR+LAB_of_REG_LAB));
}

case KL1B_CHECK_INTEGER:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_IT_LAB);
    if(Typeof(reg) == INT &&
       Valueof(reg) == GetInt(PCR+IT_of_REG_IT_LAB)){
	NextInstr(LEN_of_REG_IT_LAB);
    }
    JumpInstr(GetAddr(PCR+LAB_of_REG_IT_LAB));
}

case KL1B_CHECK_FLOAT:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_FLOT_LAB);
    if(Typeof(reg) == FLOAT &&
       Valueof(reg) == GetFloat(PCR+FLOT_of_REG_FLOT_LAB)){
	NextInstr(LEN_of_REG_FLOT_LAB);
    }
    JumpInstr(GetAddr(PCR+LAB_of_REG_FLOT_LAB));
}

case KL1B_CHECK_VECTOR:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_ARITY_LAB);
    if(Typeof(reg) == VECTOR &&
       VectorLengthof(reg) == GetArity(PCR+ARITY_of_REG_ARITY_LAB)){
	NextInstr(LEN_of_REG_ARITY_LAB);
    }
    JumpInstr(GetAddr(PCR+LAB_of_REG_ARITY_LAB));
}


/*** Wait Bounded Value & Check Type & Check Value ***********************
*  1. wait_atom(Reg,Atom)						 *
*  2. wait_nil(Reg)							 *
*  3. wait_integer(Reg,Int)						 *
*  4. wait_float(Reg,Float)						 *
*  5. wait_vector(Reg,Arity)						 *
*************************************************************************/

case KL1B_WAIT_ATOM:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_ATM);
    if(Typeof(reg) != ATOM){ /* Optimize, Reg is nearly always bounded */
	Dereference(reg);
	if(Typeof(reg) != ATOM){
	    if(IsRef(reg)) PushToSuspensionStack(reg);
	    NextAlternative;
	}
    }
    if(Valueof(reg) == GetAtom(PCR+ATM_of_REG_ATM)){
	NextInstr(LEN_of_REG_ATM);
    }else{
	NextAlternative;
    }
}

case KL1B_WAIT_NIL:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG);
    if(Typeof(reg) != ATOM){ /* Optimize, Reg is nearly always bounded */
	Dereference(reg);
	if(Typeof(reg) != ATOM){
	    if(IsRef(reg)) PushToSuspensionStack(reg);
	    NextAlternative;
	}
    }
    if(Valueof(reg) == NIL){
	NextInstr(LEN_of_REG);
    }else{
	NextAlternative;
    }
}

case KL1B_WAIT_INTEGER:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_IT);
    if(Typeof(reg) != INT){ /* Optimize, Reg is nearly always bounded */
	Dereference(reg);
	if(Typeof(reg) != INT){
	    if(IsRef(reg)) PushToSuspensionStack(reg);
	    NextAlternative;
	}
    }
    if(Valueof(reg) == GetInt(PCR+IT_of_REG_IT)){
	NextInstr(LEN_of_REG_IT);
    }else{
	NextAlternative;
    }
}

case KL1B_WAIT_FLOAT:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_FLOT);
    if(Typeof(reg) != FLOAT){ /* Optimize, Reg is nearly always bounded */
	Dereference(reg);
	if(Typeof(reg) != FLOAT){
	    if(IsRef(reg)) PushToSuspensionStack(reg);
	    NextAlternative;
	}
    }
    if(Valueof(reg) == GetFloat(PCR+FLOT_of_REG_FLOT)){
	NextInstr(LEN_of_REG_FLOT);
    }else{
	NextAlternative;
    }
}

case KL1B_WAIT_VECTOR:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_ARITY);
    if(Typeof(reg) != VECTOR){ /* Optimize,Reg is nearly always bounded */
	Dereference(reg);
	if(Typeof(reg) != VECTOR){
	    if(IsRef(reg)) PushToSuspensionStack(reg);
	    NextAlternative;
	}
    }
    if(VectorLengthof(reg) == GetArity(PCR+ARITY_of_REG_ARITY)){
	NextInstr(LEN_of_REG_ARITY);
    }else{
	NextAlternative;
    }
}


/*** General Unification (Passive Part) **********************************
*  1. wait_value(Reg1,Reg2)						 *
*************************************************************************/

case KL1B_WAIT_VALUE:{
    register CELL *x, *y;
    register unsigned int len;
    MRB	 mrbx, mrby;
    x = GetRi(PCR+RE1_of_REGS2);
    y = GetRi(PCR+RE2_of_REGS2);
    Dereference(x);
    Dereference(y);
    switch(Typeof(x)){
      case ATOM: case INT: case FLOAT: case NUE: case SHOEN:
	if(Typeof(x) == Typeof(y)){
	    if(Valueof(x) == Valueof(y)) NextInstr(LEN_of_REGS2);
	}else{
	    if(IsRef(y)) PushToSuspensionStack(y);
	}
	NextAlternative;
      case LIST:
	if(Typeof(y) == LIST){
	    mrbx = Mrbof(x); x = Objectof(x);
	    mrby = Mrbof(y); y = Objectof(y);
	    if(passive_unify(x, mrbx, y, mrby, PASSIVE_UNIFY_DEPTH)){
		if(passive_unify(x+1, mrbx, y+1, mrby, PASSIVE_UNIFY_DEPTH)){
		    NextInstr(LEN_of_REGS2);
		}
	    }
	}else{
	    if(IsRef(y)) PushToSuspensionStack(y);
	}
	NextAlternative;
      case VECTOR:
	if(Typeof(y) == VECTOR){
	    len = VectorLengthof(x);
	    if(len == VectorLengthof(y)){
		mrbx = Mrbof(x); x = Objectof(x)+1;
		mrby = Mrbof(y); y = Objectof(y)+1;
		while(len--){
		    if(!passive_unify(x, mrbx, y, mrby, PASSIVE_UNIFY_DEPTH)){
			NextAlternative;
		    }
		    x++; y++;
		}
		NextInstr(LEN_of_REGS2);
	    }
	}else{
	    if(IsRef(y)) PushToSuspensionStack(y);
	}
	NextAlternative;
      case STRING:
	if(Typeof(y) == STRING){
	    len = StringLengthof(x);
	    if(len == StringLengthof(y)){
		x = Objectof(x);
		y = Objectof(y);
		len++;	/* Element Length + Descriptor */
		while(len--){
		    if(Valueof(x) != Valueof(y)) NextAlternative;
		    x++; y++;
		}
		NextInstr(LEN_of_REGS2);
	    }
	}else{
	    if(IsRef(y)) PushToSuspensionStack(y);
	}
	NextAlternative;
      case REF:	 /** --> UNDEF,HOOK,MHOOK,MGHOK **/
	PushToSuspensionStack(x);
	NextAlternative;
      DEFAULT:
	NextAlternative;
    }
}


/*** Read Structure Element **********************************************
*  1. read_car(Rlist,Reg)						 *
*  2. read_cdr(Rlist,Reg)						 *
*  3. read_element(Rvect,Index,Reg)					 *
*************************************************************************/

case KL1B_READ_CAR:{
    register CELL *car, *ptr;
    ptr = GetRi(PCR+RE1_of_REGS2);
    car = Carof(ptr);
    Dereference(car);
    if(Mrbof(ptr) == MRBON) SetMrbof(car, MRBON);
    *GetRi(PCR+RE2_of_REGS2) = *car;
    NextInstr(LEN_of_REGS2);
}

case KL1B_READ_CDR:{
    register CELL *cdr, *ptr;
    ptr = GetRi(PCR+RE1_of_REGS2);
    cdr = Cdrof(ptr);
    Dereference(cdr);
    if(Mrbof(ptr) == MRBON) SetMrbof(cdr, MRBON);
    *GetRi(PCR+RE2_of_REGS2) = *cdr;
    NextInstr(LEN_of_REGS2);
}

case KL1B_READ_ELEMENT:{
    register CELL *elem, *ptr;
    ptr = GetRi(PCR+REG_of_REG_IDX_REG);
    elem = VectorElementof(ptr, GetIndex(PCR+IDX_of_REG_IDX_REG));
    Dereference(elem);
    if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
    *GetRi(PCR+RE2_of_REG_IDX_REG) = *elem;
    NextInstr(LEN_of_REG_IDX_REG);
}


/*** Put Value from Register to Register (Reg1<=Reg2) ********************
*  1. put_value(Reg1,Reg2)						 *
*  2. put_marked_value(Reg1,Reg2)					 *
*************************************************************************/

case KL1B_PUT_VALUE:{
    *GetRi(PCR+RE1_of_REGS2) = *GetRi(PCR+RE2_of_REGS2);
    NextInstr(LEN_of_REGS2);
}

case KL1B_PUT_MARKED_VALUE:{
    register CELL *reg;
    reg = GetRi(PCR+RE2_of_REGS2); SetMrbof(reg, MRBON);
    *GetRi(PCR+RE1_of_REGS2) = *reg;
    NextInstr(LEN_of_REGS2);
}


/*** Set Value from Register to Goal Argument (Arg<=Reg) *****************
*  1. set_value(Arg,Reg)						 *
*  2. set_marked_value(Arg,Reg)						 *
*************************************************************************/

case KL1B_SET_VALUE:{
    *GetGi(PCR+ARG_of_ARG_REG) = *GetRi(PCR+REG_of_ARG_REG);
    NextInstr(LEN_of_ARG_REG);
}

case KL1B_SET_MARKED_VALUE:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_ARG_REG); SetMrbof(reg, MRBON);
    *GetGi(PCR+ARG_of_ARG_REG) = *reg;
    NextInstr(LEN_of_ARG_REG);
}


/*** Write Value from Register to Structure Element **********************
*  1. write_car_value(Rlist,Reg)					 *
*  2. write_cdr_value(Rlist,Reg)					 *
*  3. write_element_value(Rvect,Index,Reg)				 *
*  4. write_car_marked_value(Rlist,Reg)					 *
*  5. write_cdr_marked_value(Rlist,Reg)					 *
*  6. write_element_marked_value(Rvect,Index,Reg)			 *
*************************************************************************/

case KL1B_WRITE_CAR_VALUE:{
    *Carof(GetRi(PCR+RE1_of_REGS2)) = *GetRi(PCR+RE2_of_REGS2);
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_CDR_VALUE:{
    *Cdrof(GetRi(PCR+RE1_of_REGS2)) = *GetRi(PCR+RE2_of_REGS2);
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_ELEMENT_VALUE:{
    *VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG),
		     GetIndex(PCR+IDX_of_REG_IDX_REG))
	= *GetRi(PCR+RE2_of_REG_IDX_REG);
    NextInstr(LEN_of_REG_IDX_REG);
}

case KL1B_WRITE_CAR_MARKED_VALUE:{
    register CELL *reg;
    reg = GetRi(PCR+RE2_of_REGS2); SetMrbof(reg, MRBON);
    *Carof(GetRi(PCR+RE1_of_REGS2)) = *reg;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_CDR_MARKED_VALUE:{
    register CELL *reg;
    reg = GetRi(PCR+RE2_of_REGS2); SetMrbof(reg, MRBON);
    *Cdrof(GetRi(PCR+RE1_of_REGS2)) = *reg;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_ELEMENT_MARKED_VALUE:{
    register CELL *reg;
    reg = GetRi(PCR+RE2_of_REG_IDX_REG); SetMrbof(reg, MRBON);
    *VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG),
		     GetIndex(PCR+IDX_of_REG_IDX_REG)) = *reg;
    NextInstr(LEN_of_REG_IDX_REG);
}


/*** Put Constant to Register ********************************************
*  1. put_atom(Reg,Atom)						 *
*  2. put_nil(Reg)							 *
*  3. put_integer(Reg,Int)						 *
*  4. put_float(Reg,Float)						 *
*  5. put_list(Reg)							 *
*  6. put_reuse_list(Reg,Rlist)						 *
*  7. put_vector(Reg,Arity)						 *
*  8. put_reuse_vector(Reg,Rvect)					 *
*  9. put_structured_constant(Reg,Lab)					 *
*************************************************************************/

case KL1B_PUT_ATOM:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_ATM);
    SetAll(reg, ATOM, GetAtom(PCR+ATM_of_REG_ATM), MRBOFF);
    NextInstr(LEN_of_REG_ATM);
}

case KL1B_PUT_NIL:{
    *GetRi(PCR+REG_of_REG) = const_nil;
    NextInstr(LEN_of_REG);
}

case KL1B_PUT_INTEGER:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_IT);
    SetAll(reg, INT, GetInt(PCR+IT_of_REG_IT), MRBOFF);
    NextInstr(LEN_of_REG_IT);
}

case KL1B_PUT_FLOAT:{
    register CELL *reg;
    reg = GetRi(PCR+REG_of_REG_FLOT);
    SetAll(reg, FLOAT, GetFloat(PCR+FLOT_of_REG_FLOT), MRBOFF);
    NextInstr(LEN_of_REG_FLOT);
}

case KL1B_PUT_LIST:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+REG_of_REG);
    AllocCons(lst);
    SetAll(reg, LIST, lst, MRBOFF);
    NextInstr(LEN_of_REG);
}

case KL1B_PUT_REUSED_LIST:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+RE1_of_REGS2);
    lst = GetRi(PCR+RE2_of_REGS2);
    if(Mrbof(lst) == MRBOFF){
	*reg = *lst;
	mrbgc_statistics_reuse_list();
    }else{
	AllocCons(lst);
	SetAll(reg, LIST, lst, MRBOFF);
	mrbgc_statistics_reuse_list_fail();
    }
    NextInstr(LEN_of_REGS2);
}

case KL1B_PUT_VECTOR:{
    register CELL *reg, *vct;
    register unsigned int arity;
    reg = GetRi(PCR+REG_of_REG_ARITY);
    arity = GetArity(PCR+ARITY_of_REG_ARITY);
    AllocVector(vct, arity);
    SetAll(reg, VECTOR, vct, MRBOFF);
    NextInstr(LEN_of_REG_ARITY);
}

case KL1B_PUT_REUSED_VECTOR:{
    register CELL *reg, *vct;
    register unsigned int arity;
    reg = GetRi(PCR+RE1_of_REGS2);
    vct = GetRi(PCR+RE2_of_REGS2);
    if(Mrbof(vct) == MRBOFF){
	*reg = *vct;
	mrbgc_statistics_reuse_vector(VectorLengthof(vct)+1);
    }else{
	arity = VectorLengthof(vct);
	AllocVector(vct, arity);
	SetAll(reg, VECTOR, vct, MRBOFF);
	mrbgc_statistics_reuse_vector_fail(arity+1);
    }
    NextInstr(LEN_of_REGS2);
}

case KL1B_PUT_STRUCTURED_CONSTANT:{
    *GetRi(PCR+REG_of_REG_LAB) = *((CELL *)GetAddr(PCR+LAB_of_REG_LAB));
    NextInstr(LEN_of_REG_LAB);
}


/*** Set Constant to Goal Argument ***************************************
*  1. set_atom(Arg,Atom)						 *
*  2. set_nil(Arg)							 *
*  3. set_integer(Arg,Int)						 *
*  4. set_float(Arg,Float)						 *
*************************************************************************/

case KL1B_SET_ATOM:{
    register CELL *arg;
    arg = GetGi(PCR+ARG_of_ARG_ATM);
    SetAll(arg, ATOM, GetAtom(PCR+ATM_of_ARG_ATM), MRBOFF);
    NextInstr(LEN_of_ARG_ATM);
}

case KL1B_SET_NIL:{
    *GetGi(PCR+ARG_of_ARG) = const_nil;
    NextInstr(LEN_of_ARG);
}

case KL1B_SET_INTEGER:{
    register CELL *arg;
    arg = GetGi(PCR+ARG_of_ARG_IT);
    SetAll(arg, INT, GetInt(PCR+IT_of_ARG_IT), MRBOFF);
    NextInstr(LEN_of_ARG_IT);
}

case KL1B_SET_FLOAT:{
    register CELL *arg;
    arg = GetGi(PCR+ARG_of_ARG_FLOT);
    SetAll(arg, FLOAT, GetFloat(PCR+FLOT_of_ARG_FLOT), MRBOFF);
    NextInstr(LEN_of_ARG_FLOT);
}


/***  Write Constant to Structure Element ********************************
*  1. write_car_atom(Rlist,Atom)					 *
*  2. write_cdr_atom(Rlist,Atom)					 *
*  3. write_element_atom(Rvect,Index,Atom)				 *
*  4. write_car_nil(Rlist)						 *
*  5. write_cdr_nil(Rlist)						 *
*  6. write_element_nil(Rvect,Index)					 *
*  7. write_car_integer(Rlist,Int)					 *
*  8. write_cdr_integer(Rlist,Int)					 *
*  9. write_element_integer(Rvect,Index,Int)				 *
* 10. write_car_float(Rlist,Float)					 *
* 11. write_cdr_float(Rlist,Float)					 *
* 12. write_element_float(Rvect,Index,Float)				 *
*************************************************************************/

case KL1B_WRITE_CAR_ATOM:{
    register CELL *car;
    car = Carof(GetRi(PCR+REG_of_REG_ATM));
    SetAll(car, ATOM, GetAtom(PCR+ATM_of_REG_ATM), MRBOFF);
    NextInstr(LEN_of_REG_ATM);
}

case KL1B_WRITE_CDR_ATOM:{
    register CELL *cdr;
    cdr = Cdrof(GetRi(PCR+REG_of_REG_ATM));
    SetAll(cdr, ATOM, GetAtom(PCR+ATM_of_REG_ATM), MRBOFF);
    NextInstr(LEN_of_REG_ATM);
}

case KL1B_WRITE_ELEMENT_ATOM:{
    register CELL *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX_ATM),
			   GetIndex(PCR+IDX_of_REG_IDX_ATM));
    SetAll(elem, ATOM, GetAtom(PCR+ATM_of_REG_IDX_ATM), MRBOFF);
    NextInstr(LEN_of_REG_IDX_ATM);
}

case KL1B_WRITE_CAR_NIL:{
    register CELL *car;
    car = Carof(GetRi(PCR+REG_of_REG));
    *car = const_nil;
    NextInstr(LEN_of_REG);
}

case KL1B_WRITE_CDR_NIL:{
    register CELL *cdr;
    cdr = Cdrof(GetRi(PCR+REG_of_REG));
    *cdr = const_nil;
    NextInstr(LEN_of_REG);
}

case KL1B_WRITE_ELEMENT_NIL:{
    register CELL *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX),
			   GetIndex(PCR+IDX_of_REG_IDX)),
    *elem = const_nil;
    NextInstr(LEN_of_REG_IDX);
}

case KL1B_WRITE_CAR_INTEGER:{
    register CELL *car;
    car = Carof(GetRi(PCR+REG_of_REG_IT));
    SetAll(car, INT, GetInt(PCR+IT_of_REG_IT), MRBOFF);
    NextInstr(LEN_of_REG_IT);
}

case KL1B_WRITE_CDR_INTEGER:{
    register CELL *cdr;
    cdr = Cdrof(GetRi(PCR+REG_of_REG_IT));
    SetAll(cdr, INT, GetInt(PCR+IT_of_REG_IT), MRBOFF);
    NextInstr(LEN_of_REG_IT);
}

case KL1B_WRITE_ELEMENT_INTEGER:{
    register CELL *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX_IT),
			   GetIndex(PCR+IDX_of_REG_IDX_REG));
    SetAll(elem, INT, GetInt(PCR+IT_of_REG_IDX_IT), MRBOFF);
    NextInstr(LEN_of_REG_IDX_IT);
}

case KL1B_WRITE_CAR_FLOAT:{
    register CELL *car;
    car = Carof(GetRi(PCR+REG_of_REG_FLOT));
    SetAll(car, FLOAT, GetFloat(PCR+FLOT_of_REG_FLOT), MRBOFF);
    NextInstr(LEN_of_REG_FLOT);
}

case KL1B_WRITE_CDR_FLOAT:{
    register CELL *cdr;
    cdr = Cdrof(GetRi(PCR+REG_of_REG_FLOT));
    SetAll(cdr, FLOAT, GetFloat(PCR+FLOT_of_REG_FLOT), MRBOFF);
    NextInstr(LEN_of_REG_FLOT);
}

case KL1B_WRITE_ELEMENT_FLOAT:{
    register CELL *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX_FLOT),
			   GetIndex(PCR+IDX_of_REG_IDX_REG));
    SetAll(elem, FLOAT, GetFloat(PCR+FLOT_of_REG_IDX_FLOT), MRBOFF);
    NextInstr(LEN_of_REG_IDX_FLOT);
}


/*** Put Variable Register ***********************************************
*  1. put_void(Reg)							 *
*  2. put_variable(Reg1,Reg2)						 *
*  3. put_marked_variable(Reg1,Reg2)					 *
*************************************************************************/

case KL1B_PUT_VOID:{
    register CELL *reg, *undef;
    reg = GetRi(PCR+REG_of_REG);
    AllocVoid(undef);
    SetAll(reg, REF, undef, MRBOFF);
    NextInstr(LEN_of_REG);
}

case KL1B_PUT_VARIABLE:{
    register CELL *reg, *undef;
    reg = GetRi(PCR+RE1_of_REGS2);
    AllocUndef(undef);
    SetAll(reg, REF, undef, MRBOFF);
    *GetRi(PCR+RE2_of_REGS2) = *reg;
    NextInstr(LEN_of_REGS2);
}

case KL1B_PUT_MARKED_VARIABLE:{
    register CELL *reg, *undef;
    reg = GetRi(PCR+RE1_of_REGS2);
    AllocUndef(undef);
    SetAll(reg, REF, undef, MRBON);
    *GetRi(PCR+RE2_of_REGS2) = *reg;
    NextInstr(LEN_of_REGS2);
}


/*** Set Variable to Goal Argument & Register ****************************
*  1. set_void(Arg)							 *
*  2. set_variable(Arg,Reg)						 *
*  3. set_marked_variable(Arg,Reg)					 *
*************************************************************************/

case KL1B_SET_VOID:{
    register CELL *arg, *undef;
    arg = GetGi(PCR+ARG_of_ARG);
    AllocVoid(undef);
    SetAll(arg, REF, undef, MRBOFF);
    NextInstr(LEN_of_ARG);
}

case KL1B_SET_VARIABLE:{
    register CELL *arg, *undef;
    arg = GetGi(PCR+ARG_of_ARG_REG);
    AllocUndef(undef);
    SetAll(arg, REF, undef, MRBOFF);
    *GetRi(PCR+REG_of_ARG_REG) = *arg;
    NextInstr(LEN_of_ARG_REG);
}

case KL1B_SET_MARKED_VARIABLE:{
    register CELL *arg, *undef;
    arg = GetGi(PCR+ARG_of_ARG_REG);
    AllocUndef(undef);
    SetAll(arg, REF, undef, MRBON);
    *GetRi(PCR+REG_of_ARG_REG) = *arg;
    NextInstr(LEN_of_ARG_REG);
}


/*** Write Variable to Structure Element & Register **********************
*  1. write_car_void(Rlist)						 *
*  2. write_cdr_void(Rlist)						 *
*  3. write_element_void(Rvect,Index)					 *
*  4. write_car_variable(Rlist,Reg)					 *
*  5. write_cdr_variable(Rlist,Reg)					 *
*  6. write_element_variable(Rvect,Index,Reg)				 *
*  7. write_car_marked_variable(Rlist,Reg)				 *
*  8. write_cdr_marked_variable(Rlist,Reg)				 *
*  9. write_element_marked_variable(Rvect,Index,Reg)			 *
*************************************************************************/

case KL1B_WRITE_CAR_VOID:{
    register CELL *undef, *car;
    car = Carof(GetRi(PCR+REG_of_REG));
    AllocVoid(undef);
    SetAll(car, REF, undef, MRBOFF);
    NextInstr(LEN_of_REG);
}

case KL1B_WRITE_CDR_VOID:{
    register CELL *undef, *cdr;
    cdr = Cdrof(GetRi(PCR+REG_of_REG));
    AllocVoid(undef);
    SetAll(cdr, REF, undef, MRBOFF);
    NextInstr(LEN_of_REG);
}

case KL1B_WRITE_ELEMENT_VOID:{
    register CELL *undef, *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX),
			   GetIndex(PCR+IDX_of_REG_IDX));
    AllocVoid(undef);
    SetAll(elem, REF, undef, MRBOFF);
    NextInstr(LEN_of_REG_IDX);
}

case KL1B_WRITE_CAR_VARIABLE:{
    register CELL *undef, *car;
    car = Carof(GetRi(PCR+RE1_of_REGS2));
    AllocUndef(undef);
    SetAll(car, REF, undef, MRBOFF);
    *GetRi(PCR+RE2_of_REGS2) = *car;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_CDR_VARIABLE:{
    register CELL *undef, *cdr;
    cdr = Cdrof(GetRi(PCR+RE1_of_REGS2));
    AllocUndef(undef);
    SetAll(cdr, REF, undef, MRBOFF);
    *GetRi(PCR+RE2_of_REGS2) = *cdr;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_ELEMENT_VARIABLE:{
    register CELL *undef, *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG),
			   GetIndex(PCR+IDX_of_REG_IDX_REG));
    AllocUndef(undef);
    SetAll(elem, REF, undef, MRBOFF);
    *GetRi(PCR+RE2_of_REG_IDX_REG) = *elem;
    NextInstr(LEN_of_REG_IDX_REG);
}

case KL1B_WRITE_CAR_MARKED_VARIABLE:{
    register CELL *undef, *car;
    car = Carof(GetRi(PCR+RE1_of_REGS2));
    AllocUndef(undef);
    SetAll(car, REF, undef, MRBON);
    *GetRi(PCR+RE2_of_REGS2) = *car;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_CDR_MARKED_VARIABLE:{
    register CELL *undef, *cdr;
    cdr = Cdrof(GetRi(PCR+RE1_of_REGS2));
    AllocUndef(undef);
    SetAll(cdr, REF, undef, MRBON);
    *GetRi(PCR+RE2_of_REGS2) = *cdr;
    NextInstr(LEN_of_REGS2);
}

case KL1B_WRITE_ELEMENT_MARKED_VARIABLE:{
    register CELL *undef, *elem;
    elem = VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG),
			   GetIndex(PCR+IDX_of_REG_IDX_REG));
    AllocUndef(undef);
    SetAll(elem, REF, undef, MRBON);
    *GetRi(PCR+RE2_of_REG_IDX_REG) = *elem;
    NextInstr(LEN_of_REG_IDX_REG);
}


/*** Active Unification **************************************************
*  1. get_atom(Reg,Atom)						 *
*  2. get_nil(Reg)							 *
*  3. get_integer(Reg,Int)						 *
*  4. get_float(Reg,Float)						 *
*  5. get_list_value(Reg,Rlist)						 *
*  6. get_vector_value(Reg,Rvect)					 *
*  7. get_value(Reg1,Reg2)						 *
*************************************************************************/

case KL1B_GET_ATOM:{
    register CELL *reg, *var;
    register unsigned int atom;
    reg = GetRi(PCR+REG_of_REG_ATM);
    atom = GetAtom(PCR+ATM_of_REG_ATM);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM:
	if(Valueof(var) == atom) break;
      case INT: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto exception_get_atom;
      case UNDEF:
	SetAll(var, ATOM, atom, Mrbof(reg));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, ATOM, atom, Mrbof(reg));
	break;
      case MGHOK:
	if(atom == NIL){
	    active_unify_stream_nil(var, Mrbof(reg));
	}else{
	    active_unify_stream_atom(var, Mrbof(reg), atom);
	}
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_atom:
	SetAll(&work, ATOM, atom, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
    NextInstr(LEN_of_REG_ATM);
}

case KL1B_GET_NIL:{
    register CELL *reg, *var;
    reg = GetRi(PCR+REG_of_REG);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case ATOM:
	if(Valueof(var) == NIL) break;
      case INT: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto exception_get_nil;
      case UNDEF:
	SetAll(var, ATOM, NIL, Mrbof(reg));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, ATOM, NIL, Mrbof(reg));
	break;
      case MGHOK:
	active_unify_stream_nil(var, Mrbof(reg));
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_nil:
	exception_active_unify_fail(reg, &const_nil);
    }
    NextInstr(LEN_of_REG);
}

case KL1B_GET_INTEGER:{
    register CELL *reg, *var;
    register int inte;
    reg = GetRi(PCR+REG_of_REG_IT);
    inte = GetInt(PCR+IT_of_REG_IT);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case INT:
	if(Valueof(var) == inte) break;
      case ATOM: case FLOAT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto exception_get_integer;
      case UNDEF:
	SetAll(var, INT, inte, Mrbof(reg));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, INT, inte, Mrbof(reg));
	break;
      case MGHOK:
	active_unify_stream_integer(var, Mrbof(reg), inte);
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_integer:
	SetAll(&work, INT, inte, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
    NextInstr(LEN_of_REG_IT);
}

case KL1B_GET_FLOAT:{
    register CELL *reg, *var;
    register int flot;
    reg = GetRi(PCR+REG_of_REG_FLOT);
    flot = GetFloat(PCR+FLOT_of_REG_FLOT);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case FLOAT:
	if(Valueof(var) == flot) break;
      case ATOM: case INT: case LIST: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto exception_get_float;
      case UNDEF:
	SetAll(var, FLOAT, flot, Mrbof(reg));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, FLOAT, flot, Mrbof(reg));
	break;
      case MGHOK:
	active_unify_stream_float(var, Mrbof(reg), flot);
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_float:
	SetAll(&work, FLOAT, flot, MRBOFF);
	exception_active_unify_fail(reg, &work);
    }
    NextInstr(LEN_of_REG_FLOT);
}

case KL1B_GET_LIST_VALUE:{
    register CELL *reg, *var, *list;
    reg = GetRi(PCR+RE1_of_REGS2);
    list = GetRi(PCR+RE2_of_REGS2);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case LIST:
	make_unify_list_list_goal_and_enqueue(var, list);
	break;
      case ATOM: case INT: case FLOAT: case VECTOR: case STRING:
      case NUE: case SHOEN:
	goto exception_get_list;
      case UNDEF:
	SetAll(var, LIST, Objectof(list), Mrbof(reg)|Mrbof(list));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, LIST, Objectof(list), Mrbof(reg)|Mrbof(list));
	break;
      case MGHOK:
	active_unify_stream_list(var, Mrbof(reg), list);
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_list:
	exception_active_unify_fail(reg, list);
    }
    NextInstr(LEN_of_REGS2);
}

case KL1B_GET_VECTOR_VALUE:{
    register CELL *reg, *var, *vct;
    reg = GetRi(PCR+RE1_of_REGS2);
    vct = GetRi(PCR+RE2_of_REGS2);
    Dereference2(reg, var);
    switch(Typeof(var)){
      case VECTOR:
	if(VectorLengthof(var) == VectorLengthof(vct)){
	    make_unify_vector_vector_goal_and_enqueue(var, vct);
	    break;
	}
      case ATOM: case INT: case FLOAT: case LIST: case STRING:
      case NUE: case SHOEN:
	goto exception_get_vector;
      case UNDEF:
	SetAll(var, VECTOR, Objectof(vct), Mrbof(reg)|Mrbof(vct));
	break;
      case HOOK: case MHOOK:
	wakeup_goals(var, VECTOR, Objectof(vct), Mrbof(reg)|Mrbof(vct));
	break;
      case MGHOK:
	active_unify_stream_vector(var, Mrbof(reg), vct);
	break;
      DEFAULT:
	illegal_data_type_in_active_unify(var);
      exception_get_vector:
	exception_active_unify_fail(reg, vct);
    }
    NextInstr(LEN_of_REGS2);
}

case KL1B_GET_VALUE:{
    register CELL *x, *y, *regx, *regy;
    regx = GetRi(PCR+RE1_of_REGS2);
    regy = GetRi(PCR+RE2_of_REGS2);
    Dereference2(regx, x);
    Dereference2(regy, y);
    switch(Typeof(y)){
      case ATOM: case INT: case FLOAT: case SHOEN:
	switch(Typeof(x)){
	  case UNDEF:
	    SetAll(x, Typeof(y), Valueof(y), Mrbof(regx));
	    break;
	  case HOOK: case MHOOK:
	    wakeup_goals(x, Typeof(y), Valueof(y), Mrbof(regx));
	    break;
	  DEFAULT:
	    active_unify(regx, regy);
	    break;
	}
	NextInstr(LEN_of_REGS2);
      case LIST: case VECTOR: case STRING: case NUE:
	switch(Typeof(x)){
	  case UNDEF:
	    SetAll(x, Typeof(y), Objectof(y), Mrbof(regx)|Mrbof(regy));
	    break;
	  case HOOK: case MHOOK:
	    wakeup_goals(x, Typeof(y), Objectof(y), Mrbof(regx)|Mrbof(regy));
	    break;
	  DEFAULT:
	    active_unify(regx, regy);
	    break;
	}
	NextInstr(LEN_of_REGS2);
      case UNDEF:
	switch(Typeof(x)){
	  case ATOM: case INT: case FLOAT: case SHOEN:
	    SetAll(y, Typeof(x), Valueof(x), Mrbof(regy));
	    break;
	  case LIST: case VECTOR: case STRING: case NUE:
	    SetAll(y, Typeof(x), Objectof(x), Mrbof(regx)|Mrbof(regy));
	    break;
	  case UNDEF:
	    if(x != y) SetAll(x, REF, y, Mrbof(regx)|Mrbof(regy));
	    break;
	  case HOOK:
	    DetectDeadlockInUnifyHookUndef(x, Mrbof(regx), y, Mrbof(regy));
	    SetAll(y, REF, x, Mrbof(regx)|Mrbof(regy));
	    break;
	  case MGHOK:
	    DetectDeadlockInUnifyMghokUndef(x, Mrbof(regx), y, Mrbof(regy));
	    SetAll(y, REF, x, Mrbof(regx)|Mrbof(regy));
	    break;
	  case MHOOK:
	    SetAll(y, REF, x, Mrbof(regx)|Mrbof(regy));
	    break;
	  DEFAULT:
	    illegal_data_type_in_active_unify(x);
	    exception_active_unify_fail(regx, regy);
	}
	NextInstr(LEN_of_REGS2);
      case HOOK:
	switch(Typeof(x)){
	  case ATOM: case INT: case FLOAT: case SHOEN:
	    wakeup_goals(y, Typeof(x), Valueof(x), Mrbof(regy));
	    break;
	  case LIST: case VECTOR: case STRING: case NUE:
	    wakeup_goals(y, Typeof(x), Objectof(x), Mrbof(regx)|Mrbof(regy));
	    break;
	  case UNDEF:
	    DetectDeadlockInUnifyHookUndef(y, Mrbof(regy), x, Mrbof(regx));
	    SetAll(x, REF, y, Mrbof(regx)|Mrbof(regy));
	    break;
	  case HOOK:
	    if(x == y) break;
	    DetectDeadlockInUnifyHookHook(y, Mrbof(regy), x, Mrbof(regx));
	  case MHOOK:
	    move_suspension_queue(x, y);
	    SetAll(x, REF, y, Mrbof(regx)|Mrbof(regy));
	    break;
	  case MGHOK:
	    DetectDeadlockInUnifyHookMghok(y, Mrbof(regy), x, Mrbof(regx));
	    active_unify_stream_hook(x, Mrbof(regx), y, Mrbof(regy));
	    break;
	  DEFAULT:
	    illegal_data_type_in_active_unify(x);
	    exception_active_unify_fail(regx, regy);
	}
	NextInstr(LEN_of_REGS2);
      case MHOOK:
	switch(Typeof(x)){
	  case ATOM: case INT: case FLOAT: case SHOEN:
	    wakeup_goals(y, Typeof(x), Valueof(x), Mrbof(regy));
	    break;
	  case LIST: case VECTOR: case STRING: case NUE:
	    wakeup_goals(y, Typeof(x), Objectof(x), Mrbof(regx)|Mrbof(regy));
	    break;
	  case UNDEF:
	    SetAll(x, REF, y, Mrbof(regx)|Mrbof(regy));
	    break;
	  case MHOOK:
	    if(x == y) break;
	  case HOOK:
	    move_suspension_queue(x, y);
	    SetAll(x, REF, y, Mrbof(regx)|Mrbof(regy));
	    break;
	  case MGHOK:
	    active_unify_stream_hook(x, Mrbof(regx), y, Mrbof(regy));
	    break;
	  DEFAULT:
	    illegal_data_type_in_active_unify(x);
	    exception_active_unify_fail(regx, regy);
	}
	NextInstr(LEN_of_REGS2);
      case MGHOK:
	active_unify_with_stream(regx, y, Mrbof(regy));
	NextInstr(LEN_of_REGS2);
      DEFAULT:
	illegal_data_type_in_active_unify(y);
	exception_active_unify_fail(regx, regy);
	NextInstr(LEN_of_REGS2);
    }
}


/*** Merged Instructions *************************************************
*  1. wait_list_var_var(Reg,Rcar,Rcdr)					 *
*  2. jump_on_non_list_var_var(Reg,Lab,Rcar,Rcdr)			 *
*  3. put_func(Rvect,Arity,Atom)					 *
*  4. put_reused_func(Rvect,Roldvect,Atom)				 *
*  5. put_list_val_val(Rlist,Rcar,Rcdr)					 *
*  6. put_reused_list_val_val(Rlist,Roldlist,Rcar,Rcdr)			 *
*  7. put_list_val_var(Rlist,Rcar,Rcdr)					 *
*  8. put_reused_list_val_var(Rlist,Roldlist,Rcar,Rcdr)			 *
*  9. get_list_val_var(Reg,Rlist,Rcar,Rcdr)				 *
* 10. get_reused_list_val_var(Reg,Rlist,Roldlist,Rcar,Rcdr)		 *
* 11. read_elements_inc(Rvect,Index,Reg,Repnum)				 *
* 12. read_elements_dec(Rvect,Index,Reg,Repnum)				 *
* 13. put_values_inc(Rrg,Rfrom,Repnum)					 *
* 14. put_values_dec(Rrg,Rfrom,Repnum)					 *
* 15. set_values_inc(Arg,Rfrom,Repnum)					 *
* 16. set_values_dec(Arg,Rfrom,Repnum)					 *
* 17. write_elements_inc(Rvect,Index,Reg,Repnum)			 *
* 18. write_elements_dec(Rvect,Index,Reg,Repnum)			 *
*************************************************************************/

/**
wait_list_var_var(Reg,Rcar,Rcdr)
 == list(Reg)
  + read_car(Reg,Rcar)
  + read_cdr(Reg,Rcdr)
**/
case KL1B_WAIT_LIST_VAR_VAR:{
    register CELL *elem, *ptr;
    ptr = GetRi(PCR+RE1_of_REGS3);
    if(Typeof(ptr) != LIST){
	Dereference(ptr);
	if(Typeof(ptr) != LIST){
	    if(IsRef(ptr)) PushToSuspensionStack(ptr);
	    NextAlternative;
	}
    }
    elem = Carof(ptr);
    Dereference(elem);
    if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
    *GetRi(PCR+RE2_of_REGS3) = *elem;
    elem++;
    Dereference(elem);
    if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
    *GetRi(PCR+RE3_of_REGS3) = *elem;
    NextInstr(LEN_of_REGS3);
}

/**
jump_on_non_list_var_var(Reg,Lab,Rcar,Rcdr)
 == jump_on_non_list(Reg,Lab)
  + read_car(Reg,Rcar)
  + read_cdr(Reg,Rcdr)
**/
case KL1B_JUMP_ON_NON_LIST_VAR_VAR:{
    register CELL *elem, *ptr;
    ptr = GetRi(PCR+REG_of_REG_LAB_REG_REG);
    if(Typeof(ptr) != LIST){
	Dereference(ptr);
	if(Typeof(ptr) != LIST){
	    if(IsRef(ptr)){
		PushToSuspensionStack(ptr);
		NextAlternative;
	    }else{
		JumpInstr(GetAddr(PCR+LAB_of_REG_LAB_REG_REG));
	    }
	}
    }
    elem = Carof(ptr);
    Dereference(elem);
    if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
    *GetRi(PCR+RE2_of_REG_LAB_REG_REG) = *elem;
    elem++;
    Dereference(elem);
    if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
    *GetRi(PCR+RE3_of_REG_LAB_REG_REG) = *elem;
    NextInstr(LEN_of_REG_LAB_REG_REG);
}

/**
put_func(Rvect,Arity,Atom)
 == put_vector(Rvect,Arity)
  + write_element_atom(Rvect,0,Atom)
**/
case KL1B_PUT_FUNC:{
    register CELL *reg, *vct;
    register unsigned int arity;
    reg = GetRi(PCR+REG_of_REG_ARITY_ATM);
    arity = GetArity(PCR+ARITY_of_REG_ARITY_ATM);
    AllocVector(vct, arity);
    SetAll(reg, VECTOR, vct, MRBOFF); vct++;
    SetAll(vct, ATOM, GetAtom(PCR+ATM_of_REG_ARITY_ATM), MRBOFF);
    NextInstr(LEN_of_REG_ARITY_ATM);
}

/**
put_reused_func(Rvect,Roldvect,Atom)
 == put_reused_vector(Rvect,Roldvect)
  + write_element_atom(Rvect,0,Atom)
**/
case KL1B_PUT_REUSED_FUNC:{
    register CELL *reg, *vct;
    register unsigned int arity;
    reg = GetRi(PCR+REG_of_REG_REG_ATM);
    vct = GetRi(PCR+RE2_of_REG_REG_ATM);
    if(Mrbof(vct) == MRBOFF){
	*reg = *vct;
	mrbgc_statistics_reuse_vector(VectorLengthof(vct)+1);
	vct = VectorElementof(vct, 0);
    }else{
	arity = VectorLengthof(vct);
	AllocVector(vct, arity);
	SetAll(reg, VECTOR, vct, MRBOFF); vct++;
	mrbgc_statistics_reuse_vector_fail(arity+1);
    }
    SetAll(vct, ATOM, GetAtom(PCR+ATM_of_REG_REG_ATM), MRBOFF);
    NextInstr(LEN_of_REG_REG_ATM);
}

/**
put_list_val_val(Rlist,Rcar,Rcdr)
 == put_list(Rlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_value(Rlist,Rcdr)
**/
case KL1B_PUT_LIST_VAL_VAL:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+RE1_of_REGS3);
    AllocCons(lst);
    SetAll(reg, LIST, lst, MRBOFF);
    *lst = *GetRi(PCR+RE2_of_REGS3); lst++;
    *lst = *GetRi(PCR+RE3_of_REGS3);
    NextInstr(LEN_of_REGS3);
}

/**
put_reused_list_val_val(Rlist,Roldlist,Rcar,Rcdr)
 == put_reused_list(Rlist,Roldlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_value(Rlist,Rcdr)
**/
case KL1B_PUT_REUSED_LIST_VAL_VAL:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+RE1_of_REGS4);
    lst = GetRi(PCR+RE2_of_REGS4);
    if(Mrbof(lst) == MRBOFF){
	*reg = *lst;
	mrbgc_statistics_reuse_list();
	lst = Carof(lst);
    }else{
	AllocCons(lst);
	SetAll(reg, LIST, lst, MRBOFF);
	mrbgc_statistics_reuse_list_fail();
    }
    *lst = *GetRi(PCR+RE3_of_REGS4); lst++;
    *lst = *GetRi(PCR+RE4_of_REGS4);
    NextInstr(LEN_of_REGS4);
}

/**
put_list_val_var(Rlist,Rcar,Rcdr)
 == put_list(Rlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_variable(Rlist,Rcdr)
**/
case KL1B_PUT_LIST_VAL_VAR:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+RE1_of_REGS3);
    AllocCons(lst);
    SetAll(reg, LIST, lst, MRBOFF);
    *lst = *GetRi(PCR+RE2_of_REGS3); lst++;
    AllocUndef(reg);
    SetAll(lst, REF, reg, MRBOFF);
    *GetRi(PCR+RE3_of_REGS3) = *lst;
    NextInstr(LEN_of_REGS3);
}

/**
put_reused_list_val_var(Rlist,Roldlist,Rcar,Rcdr)
 == put_reused_list(Rlist,Roldlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_variable(Rlist,Rcdr)
**/
case KL1B_PUT_REUSED_LIST_VAL_VAR:{
    register CELL *reg, *lst;
    reg = GetRi(PCR+RE1_of_REGS4);
    lst = GetRi(PCR+RE2_of_REGS4);
    if(Mrbof(lst) == MRBOFF){
	*reg = *lst;
	mrbgc_statistics_reuse_list();
	lst = Carof(lst);
    }else{
	AllocCons(lst);
	SetAll(reg, LIST, lst, MRBOFF);
	mrbgc_statistics_reuse_list_fail();
    }
    *lst = *GetRi(PCR+RE3_of_REGS4); lst++;
    AllocUndef(reg);
    SetAll(lst, REF, reg, MRBOFF);
    *GetRi(PCR+RE4_of_REGS4) = *lst;
    NextInstr(LEN_of_REGS4);
}

/**
get_list_val_var(Reg,Rlist,Rcar,Rcdr)
 == put_list(Rlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_variable(Rlist,Rcdr)
  + get_list_value(Reg,Rlist)
**/
case KL1B_GET_LIST_VAL_VAR:{
    register CELL *reg, *lst, *undef;
    reg = GetRi(PCR+RE2_of_REGS4);
    AllocCons(lst);
    SetAll(reg, LIST, lst, MRBOFF);
    *lst = *GetRi(PCR+RE3_of_REGS4); lst++;
    AllocUndef(undef);
    SetAll(lst, REF, undef, MRBOFF);
    *GetRi(PCR+RE4_of_REGS4) = *lst;
    active_unify_with_list(GetRi(PCR+RE1_of_REGS4), reg);
    NextInstr(LEN_of_REGS4);
}

/**
get_reused_list_val_var(Reg,Rlist,Roldlist,Rcar,Rcdr)
 == put_reused_list(Rlist,Roldlist)
  + write_car_value(Rlist,Rcar)
  + write_cdr_variable(Rlist,Rcdr)
  + get_list_value(Reg,Rlist)
**/
case KL1B_GET_REUSED_LIST_VAL_VAR:{
    register CELL *reg, *lst, *undef;
    reg = GetRi(PCR+RE2_of_REGS5);
    lst = GetRi(PCR+RE3_of_REGS5);
    if(Mrbof(lst) == MRBOFF){
	*reg = *lst;
	mrbgc_statistics_reuse_list();
	lst = Carof(lst);
    }else{
	AllocCons(lst);
	SetAll(reg, LIST, lst, MRBOFF);
	mrbgc_statistics_reuse_list_fail();
    }
    *lst = *GetRi(PCR+RE4_of_REGS5); lst++;
    AllocUndef(undef);
    SetAll(lst, REF, undef, MRBOFF);
    *GetRi(PCR+RE5_of_REGS5) = *lst;
    active_unify_with_list(GetRi(PCR+RE1_of_REGS5), reg);
    NextInstr(LEN_of_REGS5);
}

/**
read_elements_inc(Rvect,Index,Reg,Repnum)
 == read_element(Rvect,Index,Reg)
  + read_element(Rvect,Index+1,Reg+1)
  +   ...
**/
case KL1B_READ_ELEMENTS_INC:{
    register CELL *elem, *ptr, *reg;
    register unsigned int ctr;
    ptr = GetRi(PCR+REG_of_REG_IDX_REG_REP);
    reg = GetRi(PCR+RE2_of_REG_IDX_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_IDX_REG_REP);
    elem = VectorElementof(ptr, GetIndex(PCR+IDX_of_REG_IDX_REG_REP));
    while(ctr--){
	Dereference(elem);
	if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
	*reg = *elem; reg++; elem++;
    }
    NextInstr(LEN_of_REG_IDX_REG_REP);
}

/**
read_elements_dec(Rvect,Index,Reg,Repnum)
 == read_element(Rvect,Index,Reg)
  + read_element(Rvect,Index+1,Reg-1)
  +   ...
**/
case KL1B_READ_ELEMENTS_DEC:{
    register CELL *elem, *ptr, *reg;
    register unsigned int ctr;
    ptr = GetRi(PCR+REG_of_REG_IDX_REG_REP);
    reg = GetRi(PCR+RE2_of_REG_IDX_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_IDX_REG_REP);
    elem = VectorElementof(ptr, GetIndex(PCR+IDX_of_REG_IDX_REG_REP));
    while(ctr--){
	Dereference(elem);
	if(Mrbof(ptr) == MRBON) SetMrbof(elem, MRBON);
	*reg = *elem; reg--; elem++;
    }
    NextInstr(LEN_of_REG_IDX_REG_REP);
}

/**
put_values_inc(Reg,Rfrom,Repnum)
 == put_value(Reg,Rfrom)
  + put_value(Reg+1,Rfrom+1)
  +   ...
**/
case KL1B_PUT_VALUES_INC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = GetRi(PCR+REG_of_REG_REG_REP);
    fr = GetRi(PCR+RE2_of_REG_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr++;
    }
    NextInstr(LEN_of_REG_REG_REP);
}

/**
put_values_dec(Reg,Rfrom,Repnum)
 == put_value(Reg,Rfrom)
  + put_value(Reg+1,Rfrom-1)
  +   ...
**/
case KL1B_PUT_VALUES_DEC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = GetRi(PCR+REG_of_REG_REG_REP);
    fr = GetRi(PCR+RE2_of_REG_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr--;
    }
    NextInstr(LEN_of_REG_REG_REP);
}

/**
set_values_inc(Reg,Rfrom,Repnum)
 == set_value(Reg,Rfrom)
  + set_value(Reg+1,Rfrom+1)
  +   ...
**/
case KL1B_SET_VALUES_INC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = GetGi(PCR+ARG_of_ARG_REG_REP);
    fr = GetRi(PCR+REG_of_ARG_REG_REP);
    ctr = GetRepnum(PCR+REP_of_ARG_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr++;
    }
    NextInstr(LEN_of_ARG_REG_REP);
}

/**
set_values_dec(Reg,Rfrom,Repnum)
 == set_value(Reg,Rfrom)
  + set_value(Reg+1,Rfrom-1)
  +   ...
**/
case KL1B_SET_VALUES_DEC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = GetGi(PCR+ARG_of_ARG_REG_REP);
    fr = GetRi(PCR+REG_of_ARG_REG_REP);
    ctr = GetRepnum(PCR+REP_of_ARG_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr--;
    }
    NextInstr(LEN_of_ARG_REG_REP);
}

/**
write_elements_inc(Rvect,Index,Reg,Repnum)
 == write_element_value(Rvect,Index,Reg)
  + write_element_value(Rvect,Index+1,Reg+1)
  +   ...
**/
case KL1B_WRITE_ELEMENTS_INC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG_REP),
			 GetIndex(PCR+IDX_of_REG_IDX_REG_REP));
    fr = GetRi(PCR+RE2_of_REG_IDX_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_IDX_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr++;
    }
    NextInstr(LEN_of_REG_IDX_REG_REP);
}

/**
write_elements_dec(Rvect,Index,Reg,Repnum)
 == write_element_value(Rvect,Index,Reg)
  + write_element_value(Rvect,Index+1,Reg-1)
  +   ...
**/
case KL1B_WRITE_ELEMENTS_DEC:{
    register CELL *fr, *to;
    register unsigned int ctr;
    to = VectorElementof(GetRi(PCR+REG_of_REG_IDX_REG_REP),
			 GetIndex(PCR+IDX_of_REG_IDX_REG_REP));
    fr = GetRi(PCR+RE2_of_REG_IDX_REG_REP);
    ctr = GetRepnum(PCR+REP_of_REG_IDX_REG_REP);
    while(ctr--){
	*to = *fr; to++; fr--;
    }
    NextInstr(LEN_of_REG_IDX_REG_REP);
}


/*** MRB Maintenance & GC ************************************************
*  1. collect_value(Reg)						 *
*  2. collect_list(Rlist)						 *
*  3. collect_vector(Rvect)						 *
*************************************************************************/

case KL1B_COLLECT_VALUE:{
    register CELL *reg;
#if MRBGC_SWITCH
    reg = GetRi(PCR+REG_of_REG);
    if(Mrbof(reg) == MRBOFF){
	if(Typeof(reg) != ATOM && Typeof(reg) != INT && Typeof(reg) != FLOAT){
	    collect_value(reg, MRBGC_COLLECT_VALUE_DEPTH);
	}
    }
#else
#if EAGER_DEADLOCK_DETECTION
    reg = GetRi(PCR+REG_of_REG);
    if(Mrbof(reg) == MRBOFF){
	if(Typeof(reg) != ATOM && Typeof(reg) != INT && Typeof(reg) != FLOAT){
	    detect_deadlock_by_collect_value(reg, MRBGC_COLLECT_VALUE_DEPTH);
	}
    }
#endif
#endif
    NextInstr(LEN_of_REG);
}

case KL1B_COLLECT_LIST:{
    register CELL *reg;
#if MRBGC_SWITCH
    reg = GetRi(PCR+REG_of_REG);
    if(Mrbof(reg) == MRBOFF){
	FreeCons(Objectof(reg));
	mrbgc_statistics_collect_list();
    }else{
	mrbgc_statistics_collect_list_fail();
    }
#endif
    NextInstr(LEN_of_REG);
}

case KL1B_COLLECT_VECTOR:{
    register CELL *reg;
#if MRBGC_SWITCH
    reg = GetRi(PCR+REG_of_REG);
    if(Mrbof(reg) == MRBOFF){
	FreeVector(Objectof(reg), VectorLengthof(reg));
	mrbgc_statistics_collect_vector(VectorLengthof(reg)+1);
    }else{
	mrbgc_statistics_collect_vector_fail(VectorLengthof(reg)+1);
    }
#endif
    NextInstr(LEN_of_REG);
}


/*************************************************************************
*   Macros for Builtin Predicate.					 *
*************************************************************************/

#define BLTG1(name){\
    if(name(GetRi(PCR+REG_of_REG))){\
	NextInstr(LEN_of_REG);\
    }else{\
	NextAlternative;\
    }\
}
#define BLTG2(name){\
    if(name(GetRi(PCR+RE1_of_REGS2),\
	    GetRi(PCR+RE2_of_REGS2))){\
	NextInstr(LEN_of_REGS2);\
    }else{\
	NextAlternative;\
    }\
}
#define BLTG3(name){\
    if(name(GetRi(PCR+RE1_of_REGS3),\
	    GetRi(PCR+RE2_of_REGS3),\
	    GetRi(PCR+RE3_of_REGS3))){\
	NextInstr(LEN_of_REGS3);\
    }else{\
	NextAlternative;\
    }\
}

#define BLT1(name){\
    name(GetRi(PCR+REG_of_REG));\
    NextInstr(LEN_of_REG);\
}
#define BLT2(name){\
    name(GetRi(PCR+RE1_of_REGS2),\
	 GetRi(PCR+RE2_of_REGS2));\
    NextInstr(LEN_of_REGS2);\
}
#define BLT3(name){\
    name(GetRi(PCR+RE1_of_REGS3),\
	 GetRi(PCR+RE2_of_REGS3),\
	 GetRi(PCR+RE3_of_REGS3));\
    NextInstr(LEN_of_REGS3);\
}
#define BLT4(name){\
    name(GetRi(PCR+RE1_of_REGS4),\
	 GetRi(PCR+RE2_of_REGS4),\
	 GetRi(PCR+RE3_of_REGS4),\
	 GetRi(PCR+RE4_of_REGS4));\
    NextInstr(LEN_of_REGS4);\
}
#define BLT5(name){\
    name(GetRi(PCR+RE1_of_REGS5),\
	 GetRi(PCR+RE2_of_REGS5),\
	 GetRi(PCR+RE3_of_REGS5),\
	 GetRi(PCR+RE4_of_REGS5),\
	 GetRi(PCR+RE5_of_REGS5));\
    NextInstr(LEN_of_REGS5);\
}
#define BLT6(name){\
    name(GetRi(PCR+RE1_of_REGS6),\
	 GetRi(PCR+RE2_of_REGS6),\
	 GetRi(PCR+RE3_of_REGS6),\
	 GetRi(PCR+RE4_of_REGS6),\
	 GetRi(PCR+RE5_of_REGS6),\
	 GetRi(PCR+RE6_of_REGS6));\
    NextInstr(LEN_of_REGS6);\
}
#define BLT7(name){\
    name(GetRi(PCR+RE1_of_REGS7),\
	 GetRi(PCR+RE2_of_REGS7),\
	 GetRi(PCR+RE3_of_REGS7),\
	 GetRi(PCR+RE4_of_REGS7),\
	 GetRi(PCR+RE5_of_REGS7),\
	 GetRi(PCR+RE6_of_REGS7),\
	 GetRi(PCR+RE7_of_REGS7));\
    NextInstr(LEN_of_REGS7);\
}
#define BLT8(name){\
    name(GetRi(PCR+RE1_of_REGS8),\
	 GetRi(PCR+RE2_of_REGS8),\
	 GetRi(PCR+RE3_of_REGS8),\
	 GetRi(PCR+RE4_of_REGS8),\
	 GetRi(PCR+RE5_of_REGS8),\
	 GetRi(PCR+RE6_of_REGS8),\
	 GetRi(PCR+RE7_of_REGS8),\
	 GetRi(PCR+RE8_of_REGS8));\
    NextInstr(LEN_of_REGS8);\
}


/*** Guard Builtin - Diff ************************************************
*  1. g_diff(Reg1,Reg2)							 *
*************************************************************************/

case KL1B_G_DIFF:{
    register CELL *SSPsave;
    SSPsave = SSP;
    if(!passive_unify(GetRi(PCR+RE1_of_REGS2), MRBOFF,
		      GetRi(PCR+RE2_of_REGS2), MRBOFF, PASSIVE_UNIFY_DEPTH)){
	if(SSP == SSPsave){
	    NextInstr(LEN_of_REGS2);
	}
    }
    NextAlternative;
}


/*** Guard Builtin - Comparison ******************************************
*  1. g_equal(Rin1,Rin2)						 *
*  2. g_not_equal(Rin1,Rin2)						 *
*  3. g_less_than(Rin1,Rin2)						 *
*  4. g_not_less_than(Rin1,Rin2)					 *
*************************************************************************/

#define COMPARE_INT(OP){\
    if(Valueof(GetRi(PCR+RE1_of_REGS2)) OP Valueof(GetRi(PCR+RE2_of_REGS2))){\
	NextInstr(LEN_of_REGS2);\
    }else{\
	NextAlternative;\
    }\
}

case KL1B_G_EQUAL:	   COMPARE_INT(==);
case KL1B_G_NOT_EQUAL:	   COMPARE_INT(!=);
case KL1B_G_LESS_THAN:	   COMPARE_INT(<);
case KL1B_G_NOT_LESS_THAN: COMPARE_INT(>=);


/*** Guard Builtin - Calculation *****************************************
*  1. g_add(Rin1,Rin2,Rout)						 *
*  2. g_subtract(Rin1,Rin2,Rout)					 *
*  3. g_multiply(Rin1,Rin2,Rout)					 *
*  4. g_divide(Rin1,Rin2,Rout)						 *
*  5. g_modulo(Rin1,Rin2,Rout)						 *
*  6. g_minus(Rin,Rout)							 *
*  7. g_increment(Rin,Rout)						 *
*  8. g_decrement(Rin,Rout)						 *
*  9. g_abs(Rin,Rout)							 *
* 10. g_min(Rin1,Rin2,Rout)						 *
* 11. g_max(Rin1,Rin2,Rout)						 *
* 12. g_and(Rin1,Rin2,Rout)						 *
* 13. g_or(Rin1,Rin2,Rout)						 *
* 14. g_exclusive_or(Rin1,Rin2,Rout)					 *
* 15. g_complement(Rin,Rout)						 *
* 16. g_shift_left(Rin1,Rin2,Rout)					 *
* 17. g_shift_right(Rin1,Rin2,Rout)					 *
*************************************************************************/

case KL1B_G_ADD:{
    register CELL *out;
#if IGNORE_INTEGER_OVERFLOW
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
	   	    +Valueof(GetRi(PCR+RE2_of_REGS3)) , MRBOFF);
#else
    double x;
    x = (double)Valueof(GetRi(PCR+RE1_of_REGS3))
       +(double)Valueof(GetRi(PCR+RE2_of_REGS3));
    if(IntOverflow(x)) NextAlternative;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, (int)x, MRBOFF);
#endif
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_SUBTRACT:{
    register CELL *out;
#if IGNORE_INTEGER_OVERFLOW
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
	   	    -Valueof(GetRi(PCR+RE2_of_REGS3)) , MRBOFF);
#else
    double x;
    x = (double)Valueof(GetRi(PCR+RE1_of_REGS3))
       -(double)Valueof(GetRi(PCR+RE2_of_REGS3));
    if(IntOverflow(x)) NextAlternative;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, (int)x, MRBOFF);
#endif
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_MULTIPLY:{
    register CELL *out;
#if IGNORE_INTEGER_OVERFLOW
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
	   	    *Valueof(GetRi(PCR+RE2_of_REGS3)) , MRBOFF);
#else
    double x;
    x = (double)Valueof(GetRi(PCR+RE1_of_REGS3))
       *(double)Valueof(GetRi(PCR+RE2_of_REGS3));
    if(IntOverflow(x)) NextAlternative;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, (int)x, MRBOFF);
#endif
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_DIVIDE:{
    register CELL *out;
    register int v1, v2;
    v1 = Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = Valueof(GetRi(PCR+RE2_of_REGS3));
    out = GetRi(PCR+RE3_of_REGS3);
    if(v2 == 0) NextAlternative;	/* Illegal Input */
    if(v1 == 0x80000000 && v2 == -1){
#if IGNORE_INTEGER_OVERFLOW
	SetAll(out, INT, 0x80000000, MRBOFF);
#else
	NextAlternative;
#endif
    }else{
	SetAll(out, INT, v1/v2, MRBOFF);
    }
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_MODULO:{
    register CELL *out;
    register int v1, v2;
    v1 = Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = Valueof(GetRi(PCR+RE2_of_REGS3));
    out = GetRi(PCR+RE3_of_REGS3);
    if(v2 == 0) NextAlternative;	/* Illegal Input */
    if(v1 == 0x80000000 && v2 == -1){
	SetAll(out, INT, 0, MRBOFF);
    }else{
	SetAll(out, INT, v1%v2, MRBOFF);
    }
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_MINUS:{
    register CELL *out;
    register int v;
    v = Valueof(GetRi(PCR+RE1_of_REGS2));
    out = GetRi(PCR+RE2_of_REGS2);
#if !IGNORE_INTEGER_OVERFLOW
    if(v == 0x80000000) NextAlternative;
#endif
    SetAll(out, INT, -v, MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_INCREMENT:{
    register CELL *out;
    register int v;
    v = Valueof(GetRi(PCR+RE1_of_REGS2));
    out = GetRi(PCR+RE2_of_REGS2);
#if !IGNORE_INTEGER_OVERFLOW
    if(v == 0x7FFFFFFF) NextAlternative;
#endif
    SetAll(out, INT, v+1, MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_DECREMENT:{
    register CELL *out;
    register int v;
    v = Valueof(GetRi(PCR+RE1_of_REGS2));
    out = GetRi(PCR+RE2_of_REGS2);
#if !IGNORE_INTEGER_OVERFLOW
    if(v == 0x80000000) NextAlternative;
#endif
    SetAll(out, INT, v-1, MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_ABS:{
    register CELL *out;
    register int v;
    v = Valueof(GetRi(PCR+RE1_of_REGS2));
    out = GetRi(PCR+RE2_of_REGS2);
#if !IGNORE_INTEGER_OVERFLOW
    if(v == 0x80000000) NextAlternative;
#endif
    SetAll(out, INT, (v<0)?(-v):v, MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_MIN:{
    register CELL *out;
    register int v1, v2;
    v1 = Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = Valueof(GetRi(PCR+RE2_of_REGS3));
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, v1<v2?v1:v2, MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_MAX:{
    register CELL *out;
    register int v1, v2;
    v1 = Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = Valueof(GetRi(PCR+RE2_of_REGS3));
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, v1>v2?v1:v2, MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_AND:{
    register CELL *out;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
		    &Valueof(GetRi(PCR+RE2_of_REGS3)), MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_OR:{
    register CELL *out;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
		    |Valueof(GetRi(PCR+RE2_of_REGS3)), MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_EXCLUSIVE_OR:{
    register CELL *out;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, Valueof(GetRi(PCR+RE1_of_REGS3))
		    ^Valueof(GetRi(PCR+RE2_of_REGS3)), MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_COMPLEMENT:{
    register CELL *out;
    out = GetRi(PCR+RE2_of_REGS2);
    SetAll(out, INT, ~Valueof(GetRi(PCR+RE1_of_REGS2)), MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_SHIFT_LEFT:{
    register CELL *out;
    register unsigned int v1, v2;
    v1 = (unsigned int)Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = (unsigned int)Valueof(GetRi(PCR+RE2_of_REGS3));
    if(v2 > 31) NextAlternative;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, v1<<v2, MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_SHIFT_RIGHT:{
    register CELL *out;
    register unsigned int v1, v2;
    v1 = (unsigned int)Valueof(GetRi(PCR+RE1_of_REGS3));
    v2 = (unsigned int)Valueof(GetRi(PCR+RE2_of_REGS3));
    if(v2 > 31) NextAlternative;
    out = GetRi(PCR+RE3_of_REGS3);
    SetAll(out, INT, v1>>v2, MRBOFF);
    NextInstr(LEN_of_REGS3);
}


/***  Builtin - Vector **********************************************
*  1. g_vector(Rvect,Rsize)						 *
*  2. g_vector_element(Rvect,Rindex,Relem)				 *
*  3. mark_element(Rvect,Rindex)					 *
*************************************************************************/

case KL1B_G_VECTOR:{
    register CELL *vct, *size;
    vct = GetRi(PCR+RE1_of_REGS2);
    size = GetRi(PCR+RE2_of_REGS2);
    SetAll(size, INT, VectorLengthof(vct), MRBOFF);
    NextInstr(LEN_of_REGS2);
}

case KL1B_G_VECTOR_ELEMENT:{
    register CELL *vct, *elem;
    register unsigned int index;
    vct = GetRi(PCR+RE1_of_REGS3);
    index = Valueof(GetRi(PCR+RE2_of_REGS3));
    if(index < (unsigned int)VectorLengthof(vct)){
	elem = VectorElementof(vct, index);
	Dereference(elem);
	if(Mrbof(vct) == MRBON) SetMrbof(elem, MRBON);
	*GetRi(PCR+RE3_of_REGS3) = *elem;
	NextInstr(LEN_of_REGS3);
    }else{
	NextAlternative;
    }
}

case KL1B_MARK_ELEMENT:{
    register CELL *elem;
    elem = VectorElementof(GetRi(PCR+RE1_of_REGS2),
			   Valueof(GetRi(PCR+RE2_of_REGS2)));
    SetMrbof(elem, MRBON);
    NextInstr(LEN_of_REGS2);
}


/*** Guard Builtin - String **********************************************
*  1. g_string(Rstr,Rlength,Rwidth)					 *
*  2. g_string_element(Rstr,Rindex,Relem)				 *
*************************************************************************/

case KL1B_G_STRING:{
    register CELL *reg;
    register unsigned int type, width, leng, rest;
    reg = GetRi(PCR+RE1_of_REGS3);
    leng = StringLengthof(reg);
    type = StringTypeof(reg);
    width = (1<<(type&7))+(type>>(8-(type&7)));
    rest = (type&(0xFF>>(type&7)))>>3;
    reg = GetRi(PCR+RE2_of_REGS3);
    SetAll(reg, INT, leng*(32/width)-rest, MRBOFF);
    reg = GetRi(PCR+RE3_of_REGS3);
    SetAll(reg, INT, width, MRBOFF);
    NextInstr(LEN_of_REGS3);
}

case KL1B_G_STRING_ELEMENT:{
    register CELL *str, *out;
    register unsigned int index;
    int element;
    str = GetRi(PCR+RE1_of_REGS3);
    index = Valueof(GetRi(PCR+RE2_of_REGS3));
    out = GetRi(PCR+RE3_of_REGS3);
    if(get_string_element(str, index, &element) == STRUTL_SUCCESS){
	SetAll(out, INT, element, MRBOFF);
	NextInstr(LEN_of_REGS3);
    }else{
	NextAlternative;
    }
}


/*** Body Builtin - Calculation ******************************************
*  1. b_add(Rin1,Rin2,Rout)						 *
*  2. b_subtract(Rin1,Rin2,Rout)					 *
*  3. b_multiply(Rin1,Rin2,Rout)					 *
*  4. b_divide(Rin1,Rin2,Rout)						 *
*  5. b_modulo(Rin1,Rin2,Rout)						 *
*  6. b_minus(Rin,Rout)							 *
*  7. b_increment(Rin,Rout)						 *
*  8. b_decrement(Rin,Rout)						 *
*  9. b_abs(Rin,Rout)							 *
* 10. b_min(Rin1,Rin2,Rout)						 *
* 11. b_max(Rin1,Rin2,Rout)						 *
* 12. b_and(Rin1,Rin2,Rout)						 *
* 13. b_or(Rin1,Rin2,Rout)						 *
* 14. b_exclusive_or(Rin1,Rin2,Rout)					 *
* 15. b_complement(Rin,Rout)						 *
* 16. b_shift_left(Rin1,Rin2,Rout)					 *
* 17. b_shift_right(Rin1,Rin2,Rout)					 *
*************************************************************************/

case KL1B_B_ADD:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
#if IGNORE_INTEGER_OVERFLOW
	SetAll(out, INT, Valueof(in1)+Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
#else
	double x;
	x = (double)Valueof(in1)+(double)Valueof(in2);
	if(!IntOverflow(x)){
	    SetAll(out, INT, (int)x, MRBOFF);
	    NextInstr(LEN_of_REGS3);
	}
#endif
    }
    blt_b_add(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_SUBTRACT:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
#if IGNORE_INTEGER_OVERFLOW
	SetAll(out, INT, Valueof(in1)-Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
#else
	double x;
	x = (double)Valueof(in1)-(double)Valueof(in2);
	if(!IntOverflow(x)){
	    SetAll(out, INT, (int)x, MRBOFF);
	    NextInstr(LEN_of_REGS3);
	}
#endif
    }
    blt_b_subtract(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_MULTIPLY:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
#if IGNORE_INTEGER_OVERFLOW
	SetAll(out, INT, Valueof(in1)*Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
#else
	double x;
	x = (double)Valueof(in1)*(double)Valueof(in2);
	if(!IntOverflow(x)){
	    SetAll(out, INT, (int)x, MRBOFF);
	    NextInstr(LEN_of_REGS3);
	}
#endif
    }
    blt_b_multiply(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_DIVIDE:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT && Valueof(in2) != 0 &&
       !(Valueof(in1) == 0x80000000 && Valueof(in2) == -1)){
	SetAll(out, INT, Valueof(in1)/Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_divide(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_MODULO:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT && Valueof(in2) != 0 &&
       !(Valueof(in1) == 0x80000000 && Valueof(in2) == -1)){
	SetAll(out, INT, Valueof(in1)%Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_modulo(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_MINUS:{
    register CELL *in, *out;
    in	= GetRi(PCR+RE1_of_REGS2);
    out = GetRi(PCR+RE2_of_REGS2);
    if(Typeof(in) == INT && Valueof(in) != 0x80000000){
	SetAll(out, INT, -Valueof(in), MRBOFF);
	NextInstr(LEN_of_REGS2);
    }
    blt_b_minus(in, out);
    NextInstr(LEN_of_REGS2);
}

case KL1B_B_INCREMENT:{
    register CELL *in, *out;
    in	= GetRi(PCR+RE1_of_REGS2);
    out = GetRi(PCR+RE2_of_REGS2);
    if(Typeof(in) == INT && Valueof(in) != 0x7FFFFFFF){
	SetAll(out, INT, Valueof(in)+1, MRBOFF);
	NextInstr(LEN_of_REGS2);
    }
    blt_b_increment(in, out);
    NextInstr(LEN_of_REGS2);
}

case KL1B_B_DECREMENT:{
    register CELL *in, *out;
    in	= GetRi(PCR+RE1_of_REGS2);
    out = GetRi(PCR+RE2_of_REGS2);
    if(Typeof(in) == INT && Valueof(in) != 0x80000000){
	SetAll(out, INT, Valueof(in)-1, MRBOFF);
	NextInstr(LEN_of_REGS2);
    }
    blt_b_decrement(in, out);
    NextInstr(LEN_of_REGS2);
}

case KL1B_B_ABS:{
    register CELL *in, *out;
    in	= GetRi(PCR+RE1_of_REGS2);
    out = GetRi(PCR+RE2_of_REGS2);
    if(Typeof(in) == INT && Valueof(in) != 0x80000000){
	SetAll(out, INT, Valueof(in)<0?(-Valueof(in)):Valueof(in), MRBOFF);
	NextInstr(LEN_of_REGS2);
    }
    blt_b_abs(in, out);
    NextInstr(LEN_of_REGS2);
}

case KL1B_B_MIN:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
	SetAll(out, INT, Valueof(in1)<Valueof(in2)?Valueof(in1)
						  :Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_min(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_MAX:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
	SetAll(out, INT, Valueof(in1)>Valueof(in2)?Valueof(in1)
						  :Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_max(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_AND:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
	SetAll(out, INT, Valueof(in1)&Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_and(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_OR:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
	SetAll(out, INT, Valueof(in1)|Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_or(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_EXCLUSIVE_OR:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT){
	SetAll(out, INT, Valueof(in1)^Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_exclusive_or(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_COMPLEMENT:{
    register CELL *in, *out;
    in	= GetRi(PCR+RE1_of_REGS2);
    out = GetRi(PCR+RE2_of_REGS2);
    if(Typeof(in) == INT){
	SetAll(out, INT, ~Valueof(in), MRBOFF);
	NextInstr(LEN_of_REGS2);
    }
    blt_b_complement(in, out);
    NextInstr(LEN_of_REGS2);
}

case KL1B_B_SHIFT_LEFT:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT &&
       (unsigned int)Valueof(in2) <= 31){
	SetAll(out, INT, (unsigned int)Valueof(in1)
		       <<(unsigned int)Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_shift_left(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}

case KL1B_B_SHIFT_RIGHT:{
    register CELL *in1, *in2, *out;
    in1 = GetRi(PCR+RE1_of_REGS3);
    in2 = GetRi(PCR+RE2_of_REGS3);
    out = GetRi(PCR+RE3_of_REGS3);
    if(Typeof(in1) == INT && Typeof(in2) == INT &&
       (unsigned int)Valueof(in2) <= 31){
	SetAll(out, INT, (unsigned int)Valueof(in1)
		       >>(unsigned int)Valueof(in2), MRBOFF);
	NextInstr(LEN_of_REGS3);
    }
    blt_b_shift_right(in1, in2, out);
    NextInstr(LEN_of_REGS3);
}


/*** Body Builtin - Vector ***********************************************
*  1. b_vector(Rvect,Rsize,Rnewvect)					 *
*  2. b_new_vector(Rvect,Rsize)						 *
*  3. b_vector_element(Rvect,Rindex,Relem,Rnewvect)			 *
*  4. b_set_vector_element(Rvect,Rindex,Roldelem,Relem,Rnewvect)	 *
*************************************************************************/

case KL1B_B_VECTOR:		BLT3(blt_b_vector);
case KL1B_B_NEW_VECTOR:		BLT2(blt_b_new_vector);
case KL1B_B_VECTOR_ELEMENT:	BLT4(blt_b_vector_element);
case KL1B_B_SET_VECTOR_ELEMENT: BLT5(blt_b_set_vector_element);


/*** Body Builtin - String ***********************************************
*  1. b_string(Rstr,Rlength,Rwidth,Rnewstr)				 *
*  2. b_new_string(Rstr,Rlength,Rwidth)					 *
*  3. b_string_element(Rstr,Rindex,Relem,Rnewstr)			 *
*  4. b_set_string_element(Rstr,Rindex,Relem,Rnewstr)			 *
*  5. b_substring(Rstr,Rindex,Rlength,Rsubs,Rnewstr)			 *
*  6. b_set_substring(Rstr,Rindex,Rsubs,Rnewstr)			 *
*  7. b_append_string(Rstr1,Rstr2,Rnewstr)				 *
*************************************************************************/

case KL1B_B_STRING:		BLT4(blt_b_string);
case KL1B_B_NEW_STRING:		BLT3(blt_b_new_string);
case KL1B_B_STRING_ELEMENT:	BLT4(blt_b_string_element);
case KL1B_B_SET_STRING_ELEMENT: BLT4(blt_b_set_string_element);
case KL1B_B_SUBSTRING:		BLT5(blt_b_substring);
case KL1B_B_SET_SUBSTRING:	BLT4(blt_b_set_substring);
case KL1B_B_APPEND_STRING:	BLT3(blt_b_append_string);


/*** Body Builtin - Atom *************************************************
*  1. b_new_atom(Ratom)							 *
*  2. b_intern_atom(Ratom,Rstr)						 *
*  3. b_atom_name(Ratom,Rstr)						 *
*  4. b_atom_number(Ratom,Rnumber)					 *
*************************************************************************/

case KL1B_B_NEW_ATOM:	 BLT1(blt_b_new_atom);
case KL1B_B_INTERN_ATOM: BLT2(blt_b_intern_atom);
case KL1B_B_ATOM_NAME:	 BLT2(blt_b_atom_name);
case KL1B_B_ATOM_NUMBER: BLT2(blt_b_atom_number);


/*** Body Builtin - Code *************************************************
*  1. b_predicate_to_code(Rmodule,Rpred,Raarity,Rcode)			 *
*  2. b_code_to_predicate(Rcode,Rmodule,Rpred,Rarity,Rinfo)		 *
*************************************************************************/

case KL1B_B_PREDICATE_TO_CODE: BLT4(blt_b_predicate_to_code);
case KL1B_B_CODE_TO_PREDICATE: BLT5(blt_b_code_to_predicate);


/*** Guard Builtin - Console I/O *****************************************
*  1. display_console(Rdata)						 *
*  2. put_console(Rdata)						 *
*  3. read_console(Rdata)						 *
*************************************************************************/

case KL1B_DISPLAY_CONSOLE: BLT1(blt_display_console);
case KL1B_PUT_CONSOLE:	   BLT1(blt_put_console);
case KL1B_READ_CONSOLE:	   BLT1(blt_read_console);


/*** Body Builtin - Special **********************************************
*  1. b_apply(Rcode,Rargv)						 *
*  2. b_raise(Rtag,Rkey,Rinfo)						 *
*  3. b_merge(Rin,Rout)							 *
*  +. b_current_node(Rcurrent,Rtotal)					 *
*  4. b_current_processor(Rcurrent,Rx,Ry)				 *
*  5. b_current_priority(Rcurrent,Rmin,Rmax)				 *
*  6. b_rate(Rin,Rout)							 *
*  7. b_rltv(Rin,Rout)							 *
*  8. b_hash(Rx,Rhash,Rnewx)						 *
*  -. b_unbound(Rx,Rpe,Raddr,Rnewx)  ...  old fashion.			 *
*  9. b_unbound(Rx,Rresult)						 *
* 10. b_get_print_image(Rx,Rmode,Rleft,Rstr,Rlength,Rtail)		 *
*************************************************************************/

case KL1B_B_APPLY:	       BLT2(blt_b_apply);
case KL1B_B_RAISE:	       BLT3(blt_b_raise);
case KL1B_B_MERGE:	       BLT2(blt_b_merge);
case KL1B_B_CURRENT_NODE:      BLT2(blt_b_current_node);
case KL1B_B_CURRENT_PROCESSOR: BLT3(blt_b_current_processor);
case KL1B_B_CURRENT_PRIORITY:  BLT3(blt_b_current_priority);
case KL1B_B_RATE:	       BLT2(blt_b_rate);
case KL1B_B_RLTV:	       BLT2(blt_b_rltv);
case KL1B_B_HASH:	       BLT3(blt_b_hash);
case KL1B_B_UNBOUND:	       BLT4(blt_b_unbound);
case KL1B_B_UNBOUND2:	       BLT2(blt_b_unbound2);
case KL1B_B_GET_PRINT_IMAGE:   BLT6(blt_b_get_print_image);


/*************************************************************************
*  Unknown Instruction or 2byte OP Code					 *
*************************************************************************/

case SPECIAL_FUNCTION_SHIFT:
    PCR++;
    break;
DEFAULT:
    Error("Unknown opcode occurred.");
    PrintCons2F("   0x%x: 0x%x\n", PCR, GetOpCode(PCR));
    exit_pdss(1);
}


/*************************************************************************
*  KL1-B Instructions (Extended Code -- 2byte OP Code)			 *
*************************************************************************/

#if INSTRUCTION_COUNT && INSTRUCTION_BRANCH_COUNT
#undef	CountBranchACP
#define CountBranchACP instr__branch_acp[SPECIAL_FUNCTION_SHIFT]++
#undef	CountBranchLAB
#define CountBranchLAB instr__branch_lab[SPECIAL_FUNCTION_SHIFT]++
#endif

switch(0x100|GetOpCode(PCR)){


/*************************************************************************
*   Macros for Builtin Predicate.					 *
*************************************************************************/

#undef	BLTG1
#define BLTG1(name){\
    if(name(GetRi(PCR+REG_of_REG))){\
	NextInstr(LEN_of_2B_REG);\
    }else{\
	NextAlternative;\
    }\
}
#undef	BLTG2
#define BLTG2(name){\
    if(name(GetRi(PCR+RE1_of_REGS2),\
	    GetRi(PCR+RE2_of_REGS2))){\
	NextInstr(LEN_of_2B_REGS2);\
    }else{\
	NextAlternative;\
    }\
}
#undef	BLTG3
#define BLTG3(name){\
    if(name(GetRi(PCR+RE1_of_REGS3),\
	    GetRi(PCR+RE2_of_REGS3),\
	    GetRi(PCR+RE3_of_REGS3))){\
	NextInstr(LEN_of_2B_REGS3);\
    }else{\
	NextAlternative;\
    }\
}

#undef	BLT1
#define BLT1(name){\
    name(GetRi(PCR+REG_of_REG));\
    NextInstr(LEN_of_2B_REG);\
}
#undef	BLT2
#define BLT2(name){\
    name(GetRi(PCR+RE1_of_REGS2),\
	 GetRi(PCR+RE2_of_REGS2));\
    NextInstr(LEN_of_2B_REGS2);\
}
#undef	BLT3
#define BLT3(name){\
    name(GetRi(PCR+RE1_of_REGS3),\
	 GetRi(PCR+RE2_of_REGS3),\
	 GetRi(PCR+RE3_of_REGS3));\
    NextInstr(LEN_of_2B_REGS3);\
}
#undef	BLT4
#define BLT4(name){\
    name(GetRi(PCR+RE1_of_REGS4),\
	 GetRi(PCR+RE2_of_REGS4),\
	 GetRi(PCR+RE3_of_REGS4),\
	 GetRi(PCR+RE4_of_REGS4));\
    NextInstr(LEN_of_2B_REGS4);\
}
#undef	BLT5
#define BLT5(name){\
    name(GetRi(PCR+RE1_of_REGS5),\
	 GetRi(PCR+RE2_of_REGS5),\
	 GetRi(PCR+RE3_of_REGS5),\
	 GetRi(PCR+RE4_of_REGS5),\
	 GetRi(PCR+RE5_of_REGS5));\
    NextInstr(LEN_of_2B_REGS5);\
}
#undef	BLT6
#define BLT6(name){\
    name(GetRi(PCR+RE1_of_REGS6),\
	 GetRi(PCR+RE2_of_REGS6),\
	 GetRi(PCR+RE3_of_REGS6),\
	 GetRi(PCR+RE4_of_REGS6),\
	 GetRi(PCR+RE5_of_REGS6),\
	 GetRi(PCR+RE6_of_REGS6));\
    NextInstr(LEN_of_2B_REGS6);\
}
#undef	BLT7
#define BLT7(name){\
    name(GetRi(PCR+RE1_of_REGS7),\
	 GetRi(PCR+RE2_of_REGS7),\
	 GetRi(PCR+RE3_of_REGS7),\
	 GetRi(PCR+RE4_of_REGS7),\
	 GetRi(PCR+RE5_of_REGS7),\
	 GetRi(PCR+RE6_of_REGS7),\
	 GetRi(PCR+RE7_of_REGS7));\
    NextInstr(LEN_of_2B_REGS7);\
}
#undef	BLT8
#define BLT8(name){\
    name(GetRi(PCR+RE1_of_REGS8),\
	 GetRi(PCR+RE2_of_REGS8),\
	 GetRi(PCR+RE3_of_REGS8),\
	 GetRi(PCR+RE4_of_REGS8),\
	 GetRi(PCR+RE5_of_REGS8),\
	 GetRi(PCR+RE6_of_REGS8),\
	 GetRi(PCR+RE7_of_REGS8),\
	 GetRi(PCR+RE8_of_REGS8));\
    NextInstr(LEN_of_2B_REGS8);\
}


/*** Guard Builtin - Compare Floating Point ******************************
*  1. g_float_equal(Rin1,Rin2)						 *
*  2. g_float_not_equal(Rin1,Rin2)					 *
*  3. g_float_less_than(Rin1,Rin2)					 *
*  4. g_float_not_less_than(Rin1,Rin2)					 *
*************************************************************************/

#define COMPARE_FLOAT(FUNC){\
    if(FUNC(&Valueof(GetRi(PCR+RE1_of_REGS2)),\
	    &Valueof(GetRi(PCR+RE2_of_REGS2)))){\
	NextInstr(LEN_of_2B_REGS2);\
    }else{\
	NextAlternative;\
    }\
}

case KL1B_G_FLOAT_EQUAL:	 COMPARE_FLOAT(float_equal);
case KL1B_G_FLOAT_NOT_EQUAL:	 COMPARE_FLOAT(float_not_equal);
case KL1B_G_FLOAT_LESS_THAN:	 COMPARE_FLOAT(float_less_than);
case KL1B_G_FLOAT_NOT_LESS_THAN: COMPARE_FLOAT(float_not_less_than);


/*** Guard Builtin - Calculate Floating Point ****************************
*  1. g_float_add(Rin1,Rin2,Rout)					 *
*  2. g_float_subtract(Rin1,Rin2,Rout)					 *
*  3. g_float_multiply(Rin1,Rin2,Rout)					 *
*  4. g_float_divide(Rin1,Rin2,Rout)					 *
*  5. g_float_minus(Rin,Rout)						 *
*  6. g_float_abs(Rin,Rout)						 *
*  7. g_float_min(Rin1,Rin2,Rout)					 *
*  8. g_float_max(Rin1,Rin2,Rout)					 *
*  9. g_float_floor(Rin,Rout)						 *
* 10. g_float_sqrt(Rin,Rout)						 *
* 11. g_float_ln(Rin,Rout)						 *
* 12. g_float_log(Rin,Rout)						 *
* 13. g_float_exp(Rin,Rout)						 *
* 14. g_float_pow(Rin1,Rin2,Rout)					 *
* 15. g_float_sin(Rin,Rout)						 *
* 16. g_float_cos(Rin,Rout)						 *
* 17. g_float_tan(Rin,Rout)						 *
* 18. g_float_asin(Rin,Rout)						 *
* 19. g_float_acos(Rin,Rout)						 *
* 20. g_float_atan(Rin,Rout)						 *
* 21. g_float_atan2(Rin1,Rin2,Rout)					 *
* 22. g_float_sinh(Rin,Rout)						 *
* 23. g_float_cosh(Rin,Rout)						 *
* 24. g_float_tanh(Rin,Rout)						 *
*************************************************************************/

case KL1B_G_FLOAT_ADD:	    BLTG3(blt_g_float_add);
case KL1B_G_FLOAT_SUBTRACT: BLTG3(blt_g_float_subtract);
case KL1B_G_FLOAT_MULTIPLY: BLTG3(blt_g_float_multiply);
case KL1B_G_FLOAT_DIVIDE:   BLTG3(blt_g_float_divide);
case KL1B_G_FLOAT_MINUS:    BLTG2(blt_g_float_minus);
case KL1B_G_FLOAT_ABS:	    BLTG2(blt_g_float_abs);
case KL1B_G_FLOAT_MIN:	    BLTG3(blt_g_float_min);
case KL1B_G_FLOAT_MAX:	    BLTG3(blt_g_float_max);
case KL1B_G_FLOAT_FLOOR:    BLTG2(blt_g_float_floor);
case KL1B_G_FLOAT_SQRT:	    BLTG2(blt_g_float_sqrt);
case KL1B_G_FLOAT_LN:	    BLTG2(blt_g_float_ln);
case KL1B_G_FLOAT_LOG:	    BLTG2(blt_g_float_log);
case KL1B_G_FLOAT_EXP:	    BLTG2(blt_g_float_exp);
case KL1B_G_FLOAT_POW:	    BLTG3(blt_g_float_pow);
case KL1B_G_FLOAT_SIN:	    BLTG2(blt_g_float_sin);
case KL1B_G_FLOAT_COS:	    BLTG2(blt_g_float_cos);
case KL1B_G_FLOAT_TAN:	    BLTG2(blt_g_float_tan);
case KL1B_G_FLOAT_ASIN:	    BLTG2(blt_g_float_asin);
case KL1B_G_FLOAT_ACOS:	    BLTG2(blt_g_float_acos);
case KL1B_G_FLOAT_ATAN:	    BLTG2(blt_g_float_atan);
case KL1B_G_FLOAT_ATAN2:    BLTG3(blt_g_float_atan2);
case KL1B_G_FLOAT_SINH:	    BLTG2(blt_g_float_sinh);
case KL1B_G_FLOAT_COSH:	    BLTG2(blt_g_float_cosh);
case KL1B_G_FLOAT_TANH:	    BLTG2(blt_g_float_tanh);


/*** Guard Builtin - Convert Floating Point <-> Integer ******************
*  1. g_float_to_integer(Rin,Rout)					 *
*  2. g_integer_to_float(Rin,Rout)					 *
*************************************************************************/

case KL1B_G_FLOAT_TO_INTEGER: BLTG2(blt_g_float_to_integer);
case KL1B_G_INTEGER_TO_FLOAT: BLTG2(blt_g_integer_to_float);


/*** Body Builtin - Calculate Floating Point *****************************
*  1. b_float_add(Rin1,Rin2,Rout)					 *
*  2. b_float_subtract(Rin1,Rin2,Rout)					 *
*  3. b_float_multiply(Rin1,Rin2,Rout)					 *
*  4. b_float_divide(Rin1,Rin2,Rout)					 *
*  5. b_float_minus(Rin,Rout)						 *
*  6. b_float_abs(Rin,Rout)						 *
*  7. b_float_min(Rin1,Rin2,Rout)					 *
*  8. b_float_max(Rin1,Rin2,Rout)					 *
*  9. b_float_floor(Rin,Rout)						 *
* 10. b_float_sqrt(Rin,Rout)						 *
* 11. b_float_ln(Rin,Rout)						 *
* 12. b_float_log(Rin,Rout)						 *
* 13. b_float_exp(Rin,Rout)						 *
* 14. b_float_pow(Rin1,Rin2,Rout)					 *
* 15. b_float_sin(Rin,Rout)						 *
* 16. b_float_cos(Rin,Rout)						 *
* 17. b_float_tan(Rin,Rout)						 *
* 18. b_float_asin(Rin,Rout)						 *
* 19. b_float_acos(Rin,Rout)						 *
* 20. b_float_atan(Rin,Rout)						 *
* 21. b_float_atan2(Rin1,Rin2,Rout)					 *
* 22. b_float_sinh(Rin,Rout)						 *
* 23. b_float_cosh(Rin,Rout)						 *
* 24. b_float_tanh(Rin,Rout)						 *
*************************************************************************/

case KL1B_B_FLOAT_ADD:	    BLT3(blt_b_float_add);
case KL1B_B_FLOAT_SUBTRACT: BLT3(blt_b_float_subtract);
case KL1B_B_FLOAT_MULTIPLY: BLT3(blt_b_float_multiply);
case KL1B_B_FLOAT_DIVIDE:   BLT3(blt_b_float_divide);
case KL1B_B_FLOAT_MINUS:    BLT2(blt_b_float_minus);
case KL1B_B_FLOAT_ABS:	    BLT2(blt_b_float_abs);
case KL1B_B_FLOAT_MIN:	    BLT3(blt_b_float_min);
case KL1B_B_FLOAT_MAX:	    BLT3(blt_b_float_max);
case KL1B_B_FLOAT_FLOOR:    BLT2(blt_b_float_floor);
case KL1B_B_FLOAT_SQRT:	    BLT2(blt_b_float_sqrt);
case KL1B_B_FLOAT_LN:	    BLT2(blt_b_float_ln);
case KL1B_B_FLOAT_LOG:	    BLT2(blt_b_float_log);
case KL1B_B_FLOAT_EXP:	    BLT2(blt_b_float_exp);
case KL1B_B_FLOAT_POW:	    BLT3(blt_b_float_pow);
case KL1B_B_FLOAT_SIN:	    BLT2(blt_b_float_sin);
case KL1B_B_FLOAT_COS:	    BLT2(blt_b_float_cos);
case KL1B_B_FLOAT_TAN:	    BLT2(blt_b_float_tan);
case KL1B_B_FLOAT_ASIN:	    BLT2(blt_b_float_asin);
case KL1B_B_FLOAT_ACOS:	    BLT2(blt_b_float_acos);
case KL1B_B_FLOAT_ATAN:	    BLT2(blt_b_float_atan);
case KL1B_B_FLOAT_ATAN2:    BLT3(blt_b_float_atan2);
case KL1B_B_FLOAT_SINH:	    BLT2(blt_b_float_sinh);
case KL1B_B_FLOAT_COSH:	    BLT2(blt_b_float_cosh);
case KL1B_B_FLOAT_TANH:	    BLT2(blt_b_float_tanh);


/*** Body Builtin - Convert Floating Point <-> Integer *******************
*  1. b_float_to_integer(Rin,Rout)					 *
*  2. b_integer_to_float(Rin,Rout)					 *
*************************************************************************/

case KL1B_B_FLOAT_TO_INTEGER: BLT2(blt_b_float_to_integer);
case KL1B_B_INTEGER_TO_FLOAT: BLT2(blt_b_integer_to_float);


/*** Body Builtin - Shoen Control ****************************************
*  1. b_create_shoen(Rcode,Rargv,Rpmin,Rpmax,Rtag,Rshoen,Rreport)	 *
*  2. b_start_shoen(Rshoen,Rnewshoen)					 *
*  3. b_stop_shoen(Rshoen,Rnewshoen)					 *
*  4. b_abort_shoen(Rshoen,Rnewshoen)					 *
*  5. b_remove_shoen(Rshoen)						 *
*  6. b_shoen_statistics(Rshoen,Rreduction,Rnewshoen)			 *
*  7. b_shoen_add_resource(Rshoen,Rreduction,Rnewshoen)			 *
*  8. b_consume_resource(Rreduction)					 *
*************************************************************************/

case KL1B_B_CREATE_SHOEN:	BLT7(blt_b_create_shoen);
case KL1B_B_START_SHOEN:	BLT2(blt_b_start_shoen);
case KL1B_B_STOP_SHOEN:		BLT2(blt_b_stop_shoen);
case KL1B_B_ABORT_SHOEN:	BLT2(blt_b_abort_shoen);
case KL1B_B_REMOVE_SHOEN:	BLT1(blt_b_remove_shoen);
case KL1B_B_SHOEN_STATISTICS:	BLT3(blt_b_shoen_statistics);
case KL1B_B_SHOEN_ADD_RESOURCE: BLT3(blt_b_shoen_add_resource);
case KL1B_B_CONSUME_RESOURCE:	BLT1(blt_b_consume_resource);


/*** Body Builtin - File, Window I/O *************************************
*  1. b_create_window(Rname,Rstt,Rinterrupt,Rio)			 *
*  2. b_remove_window(Rio,Rstt)						 *
*  3. b_show_window(Rio,Rstt,Rnewio)					 *
*  4. b_hide_window(Rio,Rstt,Rnewio)					 *
*  5. b_create_file(Rstt,Rio)						 *
*  6. b_remove_file(Rio,Rstt)						 *
*  7. b_open_file(Rio,Rname,Rmode,Rstt,Rnewio)				 *
*  8. b_close_file(Rio,Rstt,Rnewio)					 *
*  9. b_write_char(Rio,Rchar,Rstt,Rnewio)				 *
* 10. b_write_line(Rio,Rline,Rstt,Rnewio)				 *
* 11. b_write_buffer(Rio,Rbuffer,Rstt,Rnewio)				 *
* 12. b_write_term(Rio,Rterm,Rlength,Rdepth,Rstt,Rnewio)		 *
* 13. b_read_char(Rio,Rchar,Rstt,Rnewio)				 *
* 14. b_read_line(Rio,Rline,Rstt,Rnewio)				 *
* 15. b_read_buffer(Rio,Rlength,Rbuffer,Rstt,Rnewio)			 *
* 16. b_read_token(Rio,Rtoken,Rvarnum,Rstt,Rnewio)			 *
* 17. b_abort_read_command(Rio,Rstt,Rnewio)				 *
*************************************************************************/

case KL1B_B_CREATE_WINDOW:	BLT4(blt_b_create_window);
case KL1B_B_REMOVE_WINDOW:	BLT2(blt_b_remove_window);
case KL1B_B_SHOW_WINDOW:	BLT3(blt_b_show_window);
case KL1B_B_HIDE_WINDOW:	BLT3(blt_b_hide_window);
case KL1B_B_CREATE_FILE:	BLT2(blt_b_create_file);
case KL1B_B_REMOVE_FILE:	BLT2(blt_b_remove_file);
case KL1B_B_OPEN_FILE:		BLT5(blt_b_open_file);
case KL1B_B_CLOSE_FILE:		BLT3(blt_b_close_file);
case KL1B_B_WRITE_CHAR:		BLT4(blt_b_write_char);
case KL1B_B_WRITE_LINE:		BLT4(blt_b_write_line);
case KL1B_B_WRITE_BUFFER:	BLT4(blt_b_write_buffer);
case KL1B_B_WRITE_TERM:		BLT6(blt_b_write_term);
case KL1B_B_READ_CHAR:		BLT4(blt_b_read_char);
case KL1B_B_READ_LINE:		BLT4(blt_b_read_line);
case KL1B_B_READ_BUFFER:	BLT5(blt_b_read_buffer);
case KL1B_B_READ_TOKEN:		BLT5(blt_b_read_token);
case KL1B_B_ABORT_READ_COMMAND: BLT3(blt_b_abort_read_command);


/*** Body Builtin - Directory ********************************************
*  1. b_test_directory(Rname,Rstt)					 *
*  2. b_directory_pathname(Rname,Rexname,Rstt)				 *
*  3. b_listing_files(Rname,Rwild,Rlist,Rstt)				 *
*  4. b_delete_files(Rname,Rwild,Rstt)					 *
*************************************************************************/

case KL1B_B_TEST_DIRECTORY:	BLT2(blt_b_test_directory);
case KL1B_B_DIRECTORY_PATHNAME: BLT3(blt_b_directory_pathname);
case KL1B_B_LISTING_FILES:	BLT4(blt_b_listing_files);
case KL1B_B_DELETE_FILES:	BLT3(blt_b_delete_files);


/*** Body Builtin - Timer ************************************************
*  1. b_get_time_count(Rtime,Rstt)					 *
*  2. b_on_at(Rtime,Rdone,Rstt)						 *
*  3. b_on_after(Rtime,Rdone,Rstt)					 *
*************************************************************************/

case KL1B_B_GET_TIME_COUNT: BLT2(blt_b_get_time_count);
case KL1B_B_ON_AT:	    BLT3(blt_b_on_at);
case KL1B_B_ON_AFTER:	    BLT3(blt_b_on_after);


/*** Body Builtin - Code *************************************************
*  1. b_save_module(Rmodule,Rfname,Rstt)				 *
*  2. b_load_module(Rmodule,Rfname,Rstt)				 *
*  3. b_assemble_module(Rmodule,Rfname,Rstt)				 *
*  4. b_remove_module(Rmodule,Rstt)					 *
*  5. b_get_public_predicates(Rmodule,Rlist,Rstt)			 *
*  6. b_trace_module(Rmodule,Rflag,Rstt)				 *
*  7. b_get_module_status(Rmodule,Rflag,Rstt)				 *
*  8. b_spy_predicate(Rcode,Rflag,Rstt)					 *
*  9. b_get_spied_predicates(Rmodule,Rlist,Rstt)			 *
* 10. b_reset_profile_info(Rmodule,Rstt)				 *
* 11. b_get_profile_info(Rmodule,Rlist,Rstt)				 *
*************************************************************************/

case KL1B_B_SAVE_MODULE:	   BLT3(blt_b_save_module);
case KL1B_B_LOAD_MODULE:	   BLT3(blt_b_load_module);
case KL1B_B_ASSEMBLE_MODULE:	   BLT3(blt_b_assemble_module);
case KL1B_B_REMOVE_MODULE:	   BLT2(blt_b_remove_module);
case KL1B_B_GET_PUBLIC_PREDICATES: BLT3(blt_b_get_public_predicates);
case KL1B_B_TRACE_MODULE:	   BLT3(blt_b_trace_module);
case KL1B_B_GET_MODULE_STATUS:	   BLT3(blt_b_get_module_status);
case KL1B_B_SPY_PREDICATE:	   BLT3(blt_b_spy_predicate);
case KL1B_B_GET_SPIED_PREDICATES:  BLT3(blt_b_get_spied_predicates);
case KL1B_B_RESET_PROFILE_INFO:	   BLT2(blt_b_reset_profile_info);
case KL1B_B_GET_PROFILE_INFO:	   BLT3(blt_b_get_profile_info);


/*** Guard Builtin - Emulator Control, Debug *****************************
*  1. statistics(Rcpu,Rheapsize,Rheapused,Rcodesize,Rcodeused,Rsystem)	 *
*  2. get_cpu_time(Rcpu)						 *
*  3. get_current_time(Ryear,Rmonth,Rday,Rhour,Rminute,Rsecond)		 *
*  -. g_tag_and_value(Reg,Rtag,Rvalue)					 *
*  -. g_register_tag_and_value(Reg,Rtag,Rvalue)				 *
*  -. g_word(Raddr,Rtag,Rvalue)						 *
*  -. g_set_tag_and_value(Reg,Rtag,Rvalue)				 *
*  4. g_halt(Rexitcode)							 *
*  5. g_request_gc(Rflag)						 *
*  6. g_set_scheduling_switch(Rflag)					 *
*  7. g_set_trace_switch(Rflag)						 *
*  8. g_set_backtrace_switch(Rflag)					 *
*  9. g_device_dup_check(Rnumber)					 *
* 10. b_get_all_atom_name(Rlist)					 *
* 11. b_unix(Rcommand,Rflag,Rstatus)					 *
* 12. b_debug_monitor_stream(Rstream,Rname,Rcounter)			 *
* 13. b_get_library_directory(Rname)					 *
*************************************************************************/

case KL1B_STATISTICS:		    BLT6(blt_statistics);
case KL1B_GET_CPU_TIME:		    BLT1(blt_get_cpu_time);
case KL1B_GET_CURRENT_TIME:	    BLT6(blt_get_current_time);
case KL1B_G_TAG_AND_VALUE:	    BLTG3(blt_g_tag_and_value);
case KL1B_G_REGISTER_TAG_AND_VALUE: BLTG3(blt_g_register_tag_and_value);
case KL1B_G_WORD:		    BLTG3(blt_g_word);
case KL1B_G_SET_TAG_AND_VALUE:	    BLTG3(blt_g_set_tag_and_value);
case KL1B_G_HALT:		    BLTG1(blt_g_halt);
case KL1B_G_REQUEST_GC:		    BLTG1(blt_g_request_gc);
case KL1B_G_SET_SCHEDULING_SWITCH:  BLTG1(blt_g_set_scheduling_switch);
case KL1B_G_SET_TRACE_SWITCH:	    BLTG1(blt_g_set_trace_switch);
case KL1B_G_SET_BACKTRACE_SWITCH:   BLTG1(blt_g_set_backtrace_switch);

case KL1B_G_DEVICE_DUP_CHECK:{
    register CELL *reg;
    register unsigned int x;
    reg = GetRi(PCR+REG_of_REG);
    Dereference(reg);
    if(Typeof(reg) != INT){
	if(IsRef(reg)) PushToSuspensionStack(reg);
	NextAlternative;
    }
    x = Valueof(reg);
    if(x < DUPLICATE_TABLE_SIZE && !duplicate_table[x]){
	duplicate_table[x] = YES;
    }else{
	NextAlternative;
    }
    NextInstr(LEN_of_2B_REG);
}

case KL1B_B_GET_ALL_ATOM_NAME:	   BLT1(blt_b_get_all_atom_name);
case KL1B_B_DEBUG_MONITOR_STREAM:  BLT3(blt_b_debug_monitor_stream);
case KL1B_B_UNIX:		   BLT3(blt_b_unix);
case KL1B_B_GET_LIBRARY_DIRECTORY: BLT1(blt_b_get_library_directory);


/*** Body Builtin - String II ********************************************
*  1. b_string_and(Rin1,Rin2,Rout,Rout2)				 *
*  2. b_string_or(Rin1,Rin2,Rout,Rout2)					 *
*  3. b_string_exclusive_or(Rin1,Rin2,Rout,Rout2)			 *
*  2. b_string_complement(Rin,Rout)					 *
*************************************************************************/

case KL1B_B_STRING_AND:		 BLT4(blt_b_string_and);
case KL1B_B_STRING_OR:		 BLT4(blt_b_string_or);
case KL1B_B_STRING_EXCLUSIVE_OR: BLT4(blt_b_string_exclusive_or);
case KL1B_B_STRING_COMPLEMENT:	 BLT2(blt_b_string_complement);


/*************************************************************************
*  Unknown Instruction							 *
*************************************************************************/

DEFAULT:
    Error("Unknown opcode occurred.");
    PrintCons2F("   0x%x: 0x%x\n", PCR-1, 0x100|GetOpCode(PCR));
    exit_pdss(1);
}
}


/*************************************************************************
*  Subroutines								 *
*************************************************************************/

nop()
{
    return;
}

static do_interrupt()
{
    if(GcFlag_ON()) CallGc();
    if(KeyboardFlag_ON() || KeyIntFlag_ON()) do_keyboard_interrupt();
    if(AlarmIntFlag_ON()) timer_wakeup_goal();
    ResetIflag();
}

static idle()
{
    SpecialFunctionToWindow(1);	 /* Idle start. */
    if(!is_there_goal_waiting_for_timer() &&
       !is_there_goal_waiting_for_keyboard_input()) SetHeapGcFlag();
  loop:
    do_interrupt();
    if(!dequeue()){
	while(!InterruptOccurred()) pause();
	goto loop;
    }
#if TWO_WAY_READY_GOAL_POOL
    execute_counter = execute_limit;
#endif
    SpecialFunctionToWindow(0);	 /* Idle end */
}

static idle2()
{
    PrintCons("Idle start...\n");
    if(!is_there_goal_waiting_for_timer() &&
       !is_there_goal_waiting_for_keyboard_input()) SetHeapGcFlag();
  loop:
    do_interrupt();
    if(!dequeue()){
	if(is_there_goal_waiting_for_timer() ||
	   is_there_goal_waiting_for_keyboard_input() ||
	   is_there_goal_waiting_for_keyboard_interrupt()){
	    while(!InterruptOccurred()) pause();
	    goto loop;
	}
	return(NO);
    }
#if TWO_WAY_READY_GOAL_POOL
    execute_counter = execute_limit;
#endif
    PrintCons("Idle end.\n");
    return(YES);
}
