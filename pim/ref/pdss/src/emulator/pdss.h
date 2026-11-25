/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#define YES  1
#define NO   0
#include <stddef.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef unsigned char OBJ;
typedef unsigned char CHAR;
typedef int	      DCODE;

#ifdef MAIN
#define	EXTERN
#else
#define	EXTERN extern
#endif

#ifdef DEBUG
#define	Debug(X) X
#else
#define	Debug(X)
#endif

#include "config.h"
#include "statistics.h"
#include "cell.h"
#include "record.h"
#include "atom.h"

#define DEFAULT case 0: default


/*************************************************************************
*   Arguments I/O Type of Builtin Predicate.				 *
*************************************************************************/

#define I	      01
#define O	      02
#define II	     011
#define IO	     021
#define OI	     012
#define III	    0111
#define IIO	    0211
#define IOI	    0121
#define IOO	    0221
#define OII	    0112
#define OIO	    0212
#define IIIO	   02111
#define IIOO	   02211
#define IOOO	   02221
#define IIIOO	  022111
#define IIOIO	  021211
#define IIOOO	  022211
#define IOOOO	  022221
#define IIIIOO	 0221111
#define IIIOOO	 0222111
#define IIIIIOO 02211111


/*************************************************************************
*   Public Functions & Variables in "pdss.c".				 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "option.c".				 *
*************************************************************************/

extern unsigned int option_heap_size;
extern unsigned int option_code_size;
extern int	    option_startup_flag;
extern CHAR	    option_startup_file[256];
extern int	    option_load_prompting;
extern int	    option_print_var_mode;
extern int	    option_use_windows;
extern int	    option_alarm_clock_sw;
#if TWO_WAY_READY_GOAL_POOL
extern int	    option_breadth_first;
extern unsigned int option_execute_limit;
extern int	    option_random_enqueue;
extern unsigned int option_random_rate;
extern unsigned int option_random_seed;
#endif
#if INSTRUCTION_TRACE
extern int	    option_instruction_trace;
#endif
#if INSTRUCTION_COUNT
extern int	    option_instruction_count;
#endif


/*************************************************************************
*   Public Functions & Variables in "version.c".			 *
*************************************************************************/

extern CHAR *version;
extern CHAR *makedate;


/*************************************************************************
*   Public Functions & Variables in "emulate.c".			 *
*************************************************************************/

/** Working Registers **/
#define MAXREGS 32
extern CELL regs[MAXREGS];
#define R0 (regs[0])
#define R1 (regs[1])
#define R2 (regs[2])
#define R3 (regs[3])
#define R4 (regs[4])
#define R5 (regs[5])
#define R6 (regs[6])
#define R7 (regs[7])
#define R8 (regs[8])
#define R9 (regs[9])

/** Program Counter, Alternative Clause Pointer, ... **/
extern OBJ *PC;
extern OBJ *ACP;
extern unsigned int number_of_argument;
extern int goal_debug_status;
extern OBJ *current_predicate;	/* pointer to current predicate top */
extern OBJ *current_predicate2;
extern unsigned int priority;
extern unsigned int logical_priority;

/** Shoen **/
extern PARENT_RECORD *parent;
extern int number_of_children;
extern int reduction_left;
#define IsResourceLimit() (reduction_left <= 0)
#if COUNT_DCODE_REDUCTION
#ifdef STATISTICS_REDUCTION
#define CountDcodeReduction() { reduction_left--; STATISTICS_REDUCTION; }
#else
#define CountDcodeReduction() reduction_left--;
#endif
#else
#define CountDcodeReduction()
#endif

/** Interrupt Flags **/
extern int iflag;
  /* bit 1: request gc (heap) */
  /* bit 2: request gc (code) */
  /* bit 5: keyboard data ready */
  /* bit 6: keyboard interrupt	*/
  /* bit 7: alarm clock interrupt */
#define InterruptOccurred() (iflag != 0)
#define ResetIflag()	    (iflag = 0)
#define GcFlag_ON()	    (iflag & 0x06)
#define ResetGcFlag()	    { iflag &= ~0x06; }
#define HeapGcFlag_ON()	    (iflag & 0x02)
#define SetHeapGcFlag()	    { iflag |= 0x02; }
#define CodeGcFlag_ON()	    (iflag & 0x04)
#define SetCodeGcFlag()	    { iflag |= 0x04; }
#define KeyboardFlag_ON()   (iflag & 0x20)
#define SetKeyboardFlag()   { iflag |= 0x20; }
#define KeyIntFlag_ON()	    (iflag & 0x40)
#define SetKeyIntFlag()	    { iflag |= 0x40; }
#define AlarmIntFlag_ON()   (iflag & 0x80)
#define SetAlarmIntFlag()   { iflag |= 0x80; }

#if TWO_WAY_READY_GOAL_POOL
extern int execute_limit;
extern int execute_counter;
#endif

/** Instruction Trace/Counter **/
#if INSTRUCTION_TRACE
extern int instruction_trace_flag;
#endif
#if INSTRUCTION_COUNT
extern unsigned int instruction_counter;
extern unsigned int instr__counter[256];
#if INSTRUCTION_BRANCH_COUNT
extern unsigned int instr__branch_acp[256];
extern unsigned int instr__branch_lab[256];
#endif
#endif

/** Return Value of Native Code **/
#define NC_PROCEED	   0
#define NC_EXECUTE	   1
#define NC_SWAPGOAL	   2
#define NC_SUSPENDED	   3
#define NC_SUSPEND	   4
#define NC_SUSPEND_OR_FAIL 5
#define NC_FAIL		   6

/** Functions **/


/*************************************************************************
*   Public Functions & Variables in "blt_basic.c".			 *
*************************************************************************/







/*************************************************************************
*   Public Functions & Variables in "blt_float.c".			 *
*************************************************************************/







/*************************************************************************
*   Public Functions & Variables in "blt_shoen.c".			 *
*************************************************************************/




/*************************************************************************
*   Public Functions & Variables in "blt_iodev.c".			 *
*************************************************************************/






/*************************************************************************
*   Public Functions & Variables in "blt_code.c".			 *
*************************************************************************/





/*************************************************************************
*   Public Functions & Variables in "blt_system.c".			 *
*************************************************************************/







/*************************************************************************
*   Public Functions in "deref.c" & Dereference Macros.			 *
*************************************************************************/


#define Dereference(Reg){\
    if(Typeof(Reg) == REF){\
	if(!IsUnbound(Objectof(Reg))){\
	    dereference(Reg);\
	}\
    }\
}
#define Dereference2(Reg, Var){\
    Var = Reg;\
    if(Typeof(Var) == REF){\
	if(IsUnbound(Objectof(Var))){\
	    Var = Objectof(Var);\
	}else{\
	    Var = dereference(Reg);\
	}\
    }\
}


/*************************************************************************
*   Public Functions & Variables in "passive.c".			 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "unify.c".				 *
*************************************************************************/

/** Functions for Active Unification **/

/** Make D-Code Goal **/

/** D-Code for Active Unification **/


/*************************************************************************
*   Public Functions & Variables in "goal.c".				 *
*************************************************************************/

/** Physical Priority **/
#define MAX_PRIORITY		  0xFFF	    /* # of ready queue - 1 */
#define PHYSICAL_PRIORITY_WIDTH	  0x0C
#define PRIORITY_SIFT_WIDTH	  (32-PHYSICAL_PRIORITY_WIDTH)
#define SYSTEM_PHYSICAL_PRIORITY  MAX_PRIOTITY

/** Priority Rate **/
#define PRIORITY_RATE_FULL	  0x1000
#define PRIORITY_RATE_WIDTH	  0x0C

/** Ready Queue **/
typedef struct ready_queue_backet{
    unsigned int priority;
    GOAL_RECORD	 *head;
#if TWO_WAY_READY_GOAL_POOL
    GOAL_RECORD	 *tail;
#endif
    struct ready_queue_backet  *upper, *lower;
} READY_QUEUE_BACKET;
extern READY_QUEUE_BACKET ready_queue_array[MAX_PRIORITY+1];
extern READY_QUEUE_BACKET *current_queue;
extern READY_QUEUE_BACKET *highest;
extern int higher_priority_flag;
#if TWO_WAY_READY_GOAL_POOL
extern int breadth_first_flag;
extern int enqueue_special_flag;
extern int random_enqueue_flag;
extern unsigned int random_rate;
extern unsigned int random_seed;
#endif

/** Suspension Stack **/
#define SUSPMAX 1000
extern CELL *SSP;
extern CELL suspension_stack[SUSPMAX];
#define ClearSuspensionStack()	   SSP = suspension_stack
#define IsSuspensionStackEmpty()   (SSP == suspension_stack)
#define PushToSuspensionStack(reg) *SSP++ = *(reg)
#define PushToSuspensionStack2(reg, mrb){\
    SetAll(SSP, Typeof(reg), Valueof(reg), Mrbof(reg)|(mrb));\
    SSP++;\
}

/** Functions for Ready Queue **/
#if TWO_WAY_READY_GOAL_POOL
#else
#define enqueue_head(grec) enqueue(grec)
#define enqueue_tail(grec) enqueue(grec)
#endif
#if !TWO_WAY_READY_GOAL_POOL
#define enqueue_with_priority_head(grec) enqueue_with_priority(grec)
#define enqueue_with_priority_tail(grec) enqueue_with_priority(grec)
#endif

/** Functions for Suspension **/


/*************************************************************************
*   Public Functions & Variables in "shoen.c".				 *
*************************************************************************/

/** Variables **/
extern PARENT_RECORD *grand_mother;
extern CELL *result_of_grand_mother;
extern int report_raise_flag;
extern int shoen_tree_trace_flag;

/** Functions for Shoen Control **/

/** Functions for Shoen Report Stream **/

/** Functions for Shoen Tree Trace **/


/*************************************************************************
*   Public Functions & Variables in "exception.c".			 *
*************************************************************************/

/** Exception Code **/
#define ILLEGAL_INPUT_TYPE	0
#define RANGE_OVERFLOW		1
#define INTEGER_OVERFLOW	3
#define FLOATING_ERROR		5
#define ILLEGAL_MERGER_INPUT	8
#define REDUCTION_FAILED	9
#define UNIFY_FAILED	       10
#define INCORRECT_PRIORITY     16
#define MODULE_NOT_FOUND       17
#define PREDICATE_NOT_FOUND    18

/** Exception Tag **/
#define DEADLOCK_TAG		 0x00100000
#define ILLEGAL_INPUT_TYPE_TAG	 0x00200000
#define RANGE_OVERFLOW_TAG	 0x00400000
#define INTEGER_OVERFLOW_TAG	 0x00800000
#define FLOATING_ERROR_TAG	 0x01000000
#define ILLEGAL_MERGER_INPUT_TAG 0x04000000
#define REDUCTION_FAILED_TAG	 0x08000000
#define UNIFY_FAILED_TAG	 0x10000000
#define INCORRECT_PRIORITY_TAG	 0x20000000
#define MODULE_NOT_FOUND_TAG	 0x40000000
#define PREDICATE_NOT_FOUND_TAG	 0x80000000

/** Functions **/


/*************************************************************************
*   Public Functions & Variables in "atom.c".				 *
*************************************************************************/

extern unsigned int gensym_count1;
extern unsigned int gensym_count2;


/*************************************************************************
*   Public Functions & Variables in "memory.c".				 *
*************************************************************************/

/** Functions for Heap Area **/

/** Functions for Code Area **/

/** Functions for Temporary Area **/


/*************************************************************************
*   Public Functions & Variables in "module.c".				 *
*************************************************************************/

#define MODULE_TABLE_SIZE    64
#define PREDICATE_TABLE_SIZE 16	 /** Cannot Change **/
#define HashModuleID(id) ((id) & (MODULE_TABLE_SIZE-1))
#define HashPredID(id)	 (((id)+(id>>16)) & (PREDICATE_TABLE_SIZE-1))
#define HashFuncAddr(fa) ((((int)(fa))>>2) & (PREDICATE_TABLE_SIZE-1))

typedef struct predicate_table {	/* for native code */
    unsigned int pid;
    DCODE	 (* function)(void);
    struct predicate_table *p1, *p2;
} PREDICATE_ENTRY;

typedef struct module_entry{
    struct module_entry	 *next;
    unsigned  module_id;
    OBJ	 *addr;
    int	 size;
    PREDICATE_ENTRY *predicate_tbl;
    PREDICATE_ENTRY **pid_func_hash_tbl;
    PREDICATE_ENTRY **func_pid_hash_tbl;
    int	 protect;
} MODULE_ENTRY;
extern MODULE_ENTRY  *module_id_table[MODULE_TABLE_SIZE];

/** Return Code **/
#define MODMAN_SUCCESS		   0
#define MODMAN_MODULE_NOT_FOUND	   1
#define MODMAN_PREDICATE_NOT_FOUND 2
#define MODMAN_MODULE_PROTECTED	   3
#define MODMAN_NATIVE_CODE_MODULE  4
#define MODMAN_CANNOT_OPEN_FILE	   5
#define MODMAN_LOAD_ERROR	   6
#define MODMAN_REQUEST_GC	   7
#define MODMAN_MEMORY_LIMIT	   8

/** Functions to Access Module/Predicate Table **/

/** Functions to Set/Reset Module Debug Flag **/

/** Functions to Load Module **/


/*************************************************************************
*   Public Functions & Variables in "dcode.c".				 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "float.c".				 *
*************************************************************************/







/*************************************************************************
*   Public Functions & Variables in "string.c".				 *
*************************************************************************/

/** Return Code **/
#define STRUTL_SUCCESS	     0
#define STRUTL_BAD_WIDTH     1
#define STRUTL_BAD_LENGTH    2
#define STRUTL_BAD_POSITION  3
#define STRUTL_BAD_TYPE	     4
#define STRUTL_REQUEST_GC    5



/*************************************************************************
*   Public Functions & Variables in "gc.c".				 *
*************************************************************************/

extern int gc_counter;
extern int gc_panic_flag;


/*************************************************************************
*   Public Functions & Variables in "gc_ctrl.c".			 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "gc_cell.c".			 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "gc_code.c".			 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "gc_dead.c".			 *
*************************************************************************/

extern int backtrace_flag;


/*************************************************************************
*   Public Functions & Variables in "mrbgc.c".				 *
*************************************************************************/

#if EAGER_DEADLOCK_DETECTION
#define SUSPEND_VOID	10
#define SUSPEND_HOOK	11
#define SUSPEND_MGHK	12
#define UNIFY_VOID_HOOK 20
#define UNIFY_VOID_MGHK 21
#define UNIFY_HOOK_HOOK 22
#define UNIFY_HOOK_MGHK 23
#define UNIFY_MGHK_MGHK 24
#define COLLECT_HOOK	30
#define COLLECT_MGHK	31
#endif

#if EAGER_DEADLOCK_DETECTION
#define DetectDeadlockInUnifyHookUndef(var1, mrb1, var2, mrb2)\
    if(Mrbof(var1) == MRBOFF && mrb1 == MRBOFF &&\
       Mrbof(var2) == MRBOFF && mrb2 == MRBOFF){\
	detect_deadlock_in_unification1(var1);\
    }
#define DetectDeadlockInUnifyMghokUndef(var1, mrb1, var2, mrb2)\
    if(				mrb1 == MRBOFF &&\
       Mrbof(var2) == MRBOFF && mrb2 == MRBOFF){\
	detect_deadlock_in_unification1(var1);\
    }
#define DetectDeadlockInUnifyHookHook(var1, mrb1, var2, mrb2)\
    if(Mrbof(var1) == MRBOFF && mrb1 == MRBOFF &&\
       Mrbof(var2) == MRBOFF && mrb2 == MRBOFF){\
	detect_deadlock_in_unification2(var1, var2);\
    }
#define DetectDeadlockInUnifyHookMghok(var1, mrb1, var2, mrb2)\
    if(Mrbof(var1) == MRBOFF && mrb1 == MRBOFF &&\
				mrb2 == MRBOFF){\
	detect_deadlock_in_unification2(var1, var2);\
    }
#define DetectDeadlockInUnifyMghokMghok(var1, mrb1, var2, mrb2)\
    if(mrb1 == MRBOFF && mrb2 == MRBOFF){\
	detect_deadlock_in_unification2(var1, var2);\
    }
#define DetectDeadlockInSuspHook(type, goal, var, mrb)\
    if(Mrbof(var) == MRBOFF && mrb == MRBOFF){\
	detect_deadlock_in_suspension(type, goal, var);\
    }
#define DetectDeadlockInSuspMghok(type, goal, var, mrb)\
    if(mrb == MRBOFF){\
	detect_deadlock_in_suspension(type, goal, var);\
    }
#else
#define DetectDeadlockInUnifyHookUndef(var1, mrb1, var2, mrb2)
#define DetectDeadlockInUnifyMghokUndef(var1, mrb1, var2, mrb2)
#define DetectDeadlockInUnifyHookHook(var1, mrb1, var2, mrb2)
#define DetectDeadlockInUnifyHookMghok(var1, mrb1, var2, mrb2)
#define DetectDeadlockInUnifyMghokMghok(var1, mrb1, var2, mrb2)
#define DetectDeadlockInSuspHook(type, goal, var, mrb)
#define DetectDeadlockInSuspMghok(type, goal, var, mrb)
#endif

#if MRBGC_SWITCH
#else
#if EAGER_DEADLOCK_DETECTION
#endif
#endif

#if EAGER_DEADLOCK_DETECTION
#endif


/*************************************************************************
*   Public Functions & Variables in "instr.c".				 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "invassm.c".			 *
*************************************************************************/

#if INSTRUCTION_TRACE
#endif


/*************************************************************************
*   Public Functions & Variables in "assemble.c".			 *
*************************************************************************/

#define ASSEMBLE_SUCCESS	  0
#define ASSEMBLE_ERROR		  1
#define ASSEMBLE_MODULE_PROTECTED 2
#define ASSEMBLE_REQUEST_GC	  3


/*************************************************************************
*   Public Functions & Variables in "saveload.c".			 *
*************************************************************************/

#define LOAD_SUCCESS	      0
#define LOAD_NOT_SAV_FILE     1
#define LOAD_BAD_VERSION      2
#define LOAD_ERROR	      3
#define LOAD_MODULE_PROTECTED 4
#define LOAD_REQUEST_GC	      5


/*************************************************************************
*   Public Functions & Variables in "native.c".				 *
*************************************************************************/

#define NLOAD_SUCCESS	       0
#define NLOAD_CANNOT_OPEN_FILE 1
#define NLOAD_LINK_ERROR       2
#define NLOAD_MODULE_PROTECTED 3
#define NLOAD_MEMORY_LIMIT     4


/*************************************************************************
*   Public Functions & Variables in "tracer.c".				 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "print.c".				 *
*************************************************************************/

#define PRINT_VAR_MODE_ABC 0
#define PRINT_VAR_MODE_ADR 1


/*************************************************************************
*   Public Functions & Variables in "io.c".				 *
*************************************************************************/



/*************************************************************************
*   Public Functions & Variables in "iosub.c".				 *
*************************************************************************/

#define IOSUB_SUCCESS	       0
#define IOSUB_IO_TABLE_FULL    1
#define IOSUB_CANNOT_OPEN_FILE 2
#define IOSUB_END_OF_FILE      3
#define IOSUB_EOF_IN_QUOTE     4
#define IOSUB_CONTINUE	       5
#define IOSUB_REQUEST_GC       6



/*************************************************************************
*   Public Functions & Variables in "timer.c".				 *
*************************************************************************/

extern CELL *timer_table;


/*************************************************************************
*   Public Functions & Variables in "path.c".				 *
*************************************************************************/


/*************************************************************************
*   Prototypes of every external function.				 *
*************************************************************************/

typedef struct io_backet IO_BACKET;
#include "proto.h"
