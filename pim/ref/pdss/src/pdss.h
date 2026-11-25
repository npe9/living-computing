/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#define YES  1
#define NO   0
#define NULL 0

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

extern main();
extern stop_pdss();
extern abort_pdss();
extern exit_pdss();
extern print_instr_counter();
extern timeit();


/*************************************************************************
*   Public Functions & Variables in "option.c".				 *
*************************************************************************/

extern read_option();
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
extern emulate();
extern nop();


/*************************************************************************
*   Public Functions & Variables in "blt_basic.c".			 *
*************************************************************************/

extern blt_b_add();
extern blt_b_subtract();
extern blt_b_multiply();
extern blt_b_divide();
extern blt_b_modulo();
extern blt_b_minus();
extern blt_b_increment();
extern blt_b_decrement();
extern blt_b_abs();
extern blt_b_min();
extern blt_b_max();
extern DCODE dc_add();
extern DCODE dc_subtract();
extern DCODE dc_multiply();
extern DCODE dc_divide();
extern DCODE dc_modulo();
extern DCODE dc_minus();
extern DCODE dc_increment();
extern DCODE dc_decrement();
extern DCODE dc_abs();
extern DCODE dc_min();
extern DCODE dc_max();

extern blt_b_and();
extern blt_b_or();
extern blt_b_exclusive_or();
extern blt_b_complement();
extern blt_b_shift_left();
extern blt_b_shift_right();
extern DCODE dc_and();
extern DCODE dc_or();
extern DCODE dc_exclusive_or();
extern DCODE dc_complement();
extern DCODE dc_shift_left();
extern DCODE dc_shift_right();

extern blt_b_vector();
extern blt_b_new_vector();
extern blt_b_vector_element();
extern blt_b_set_vector_element();
extern DCODE dc_vector();
extern DCODE dc_new_vector();
extern DCODE dc_vector_element();
extern DCODE dc_set_vector_element();

extern blt_b_string();
extern blt_b_new_string();
extern blt_b_string_element();
extern blt_b_set_string_element();
extern blt_b_substring();
extern blt_b_set_substring();
extern blt_b_append_string();
extern blt_b_string_and();
extern blt_b_string_or();
extern blt_b_string_exclusive_or();
extern blt_b_string_complement();
extern DCODE dc_string();
extern DCODE dc_new_string();
extern DCODE dc_string_element();
extern DCODE dc_set_string_element();
extern DCODE dc_substring();
extern DCODE dc_set_substring();
extern DCODE dc_append_string();
extern DCODE dc_string_and();
extern DCODE dc_string_or();
extern DCODE dc_string_exclusive_or();
extern DCODE dc_string_complement();

extern blt_b_new_atom();
extern blt_b_intern_atom();
extern blt_b_atom_name();
extern blt_b_atom_number();
extern DCODE dc_intern_atom();
extern DCODE dc_atom_name();
extern DCODE dc_atom_number();


/*************************************************************************
*   Public Functions & Variables in "blt_float.c".			 *
*************************************************************************/

extern int blt_g_float_add();
extern int blt_g_float_subtract();
extern int blt_g_float_multiply();
extern int blt_g_float_divide();
extern int blt_g_float_minus();
extern int blt_g_float_abs();
extern int blt_g_float_min();
extern int blt_g_float_max();
extern int blt_g_float_floor();
extern int blt_g_float_sqrt();
extern int blt_g_float_ln();
extern int blt_g_float_log();
extern int blt_g_float_exp();
extern int blt_g_float_pow();
extern int blt_g_float_sin();
extern int blt_g_float_cos();
extern int blt_g_float_tan();
extern int blt_g_float_asin();
extern int blt_g_float_acos();
extern int blt_g_float_atan();
extern int blt_g_float_atan2();
extern int blt_g_float_sinh();
extern int blt_g_float_cosh();
extern int blt_g_float_tanh();

extern int blt_g_float_float_to_integer();
extern int blt_g_float_integer_to_float();

extern blt_b_float_add();
extern blt_b_float_subtract();
extern blt_b_float_multiply();
extern blt_b_float_divide();
extern blt_b_float_minus();
extern blt_b_float_abs();
extern blt_b_float_min();
extern blt_b_float_max();
extern blt_b_float_floor();
extern blt_b_float_sqrt();
extern blt_b_float_ln();
extern blt_b_float_log();
extern blt_b_float_exp();
extern blt_b_float_pow();
extern blt_b_float_sin();
extern blt_b_float_cos();
extern blt_b_float_tan();
extern blt_b_float_asin();
extern blt_b_float_acos();
extern blt_b_float_atan();
extern blt_b_float_atan2();
extern blt_b_float_sinh();
extern blt_b_float_cosh();
extern blt_b_float_tanh();

extern DCODE dc_float_add();
extern DCODE dc_float_subtract();
extern DCODE dc_float_multiply();
extern DCODE dc_float_divide();
extern DCODE dc_float_minus();
extern DCODE dc_float_abs();
extern DCODE dc_float_min();
extern DCODE dc_float_max();
extern DCODE dc_float_floor();
extern DCODE dc_float_sqrt();
extern DCODE dc_float_ln();
extern DCODE dc_float_log();
extern DCODE dc_float_exp();
extern DCODE dc_float_pow();
extern DCODE dc_float_sin();
extern DCODE dc_float_cos();
extern DCODE dc_float_tan();
extern DCODE dc_float_asin();
extern DCODE dc_float_acos();
extern DCODE dc_float_atan();
extern DCODE dc_float_atan2();
extern DCODE dc_float_sinh();
extern DCODE dc_float_cosh();
extern DCODE dc_float_tanh();

extern blt_b_float_to_integer();
extern blt_b_integer_to_float();
extern DCODE dc_float_to_integer();
extern DCODE dc_integer_to_float();


/*************************************************************************
*   Public Functions & Variables in "blt_shoen.c".			 *
*************************************************************************/

extern blt_b_create_shoen();
extern blt_b_start_shoen();
extern blt_b_stop_shoen();
extern blt_b_abort_shoen();
extern blt_b_remove_shoen();
extern blt_b_shoen_statistics();
extern blt_b_shoen_add_resource();
extern blt_b_consume_resource();

extern DCODE dc_create_shoen();
extern DCODE dc_start_shoen();
extern DCODE dc_stop_shoen();
extern DCODE dc_abort_shoen();
extern DCODE dc_remove_shoen();
extern DCODE dc_shoen_statistics();
extern DCODE dc_shoen_add_resource();
extern DCODE dc_consume_resource();


/*************************************************************************
*   Public Functions & Variables in "blt_iodev.c".			 *
*************************************************************************/

extern blt_b_create_window();
extern blt_b_remove_window();
extern blt_b_show_window();
extern blt_b_hide_window();
extern blt_b_create_file();
extern blt_b_remove_file();
extern blt_b_open_file();
extern blt_b_close_file();
extern DCODE dc_create_window();
extern DCODE dc_remove_window();
extern DCODE dc_show_window();
extern DCODE dc_hide_window();
extern DCODE dc_remove_file();
extern DCODE dc_open_file();
extern DCODE dc_close_file();

extern blt_b_write_char();
extern blt_b_write_line();
extern blt_b_write_buffer();
extern blt_b_write_term();
extern blt_b_read_char();
extern blt_b_read_line();
extern blt_b_read_buffer();
extern blt_b_read_token();
extern blt_b_abort_read_command();
extern DCODE dc_write_char();
extern DCODE dc_write_line();
extern DCODE dc_write_buffer();
extern DCODE dc_write_term();
extern DCODE dc_read_char();
extern DCODE dc_read_line();
extern DCODE dc_read_buffer();
extern DCODE dc_read_token();
extern DCODE dc_abort_read_command();

extern blt_b_test_directory();
extern blt_b_directory_pathname();
extern blt_b_listing_files();
extern blt_b_delete_files();
extern DCODE dc_test_directory();
extern DCODE dc_directory_pathname();
extern DCODE dc_listing_files();
extern DCODE dc_delete_files();

extern blt_b_get_time_count();
extern blt_b_on_at();
extern blt_b_on_after();
extern DCODE dc_on_at();
extern DCODE dc_on_after();


/*************************************************************************
*   Public Functions & Variables in "blt_code.c".			 *
*************************************************************************/

extern blt_predicate_to_code();
extern blt_code_to_predicate();
extern DCODE dc_predicate_to_code();
extern DCODE dc_code_to_predicate();

extern blt_b_save_module();
extern blt_b_load_module();
extern blt_b_assemble_module();
extern blt_b_remove_module();
extern DCODE dc_save_module();
extern DCODE dc_load_module();
extern DCODE dc_assemble_module();
extern DCODE dc_remove_module();

extern blt_b_get_public_predicates();
extern blt_b_trace_module();
extern blt_b_get_module_status();
extern blt_b_spy_predicate();
extern blt_b_get_spied_predicates();
extern blt_b_reset_profile_info();
extern blt_b_get_profile_info();
extern DCODE dc_get_public_predicates();
extern DCODE dc_trace_module();
extern DCODE dc_get_module_status();
extern DCODE dc_spy_predicate();
extern DCODE dc_get_spied_predicates();
extern DCODE dc_reset_profile_info();
extern DCODE dc_get_profile_info();


/*************************************************************************
*   Public Functions & Variables in "blt_system.c".			 *
*************************************************************************/

extern blt_display_console();
extern blt_put_console();
extern blt_read_console();

extern blt_b_apply();
extern blt_b_raise();
extern blt_b_merge();
extern blt_b_current_processor();
extern blt_b_current_priority();
extern blt_b_rltv();
extern blt_b_hash();
extern blt_b_unbound();
extern blt_b_unbound2();
extern blt_b_get_print_image();
extern DCODE dc_apply();
extern DCODE dc_raise();
extern DCODE dc_rate();
extern DCODE dc_rltv();
extern DCODE dc_hash();
extern DCODE dc_get_print_image();

extern blt_statistics();
extern blt_get_cpu_time();
extern blt_get_current_time();

extern int blt_g_halt();
extern int blt_g_request_gc();
extern int blt_g_set_scheduling_switch();
extern int blt_g_set_trace_switch();
extern int blt_g_set_backtrace_switch();

extern blt_b_get_all_atom_name();
extern blt_b_unix();
extern blt_b_get_library_directory();
extern DCODE dc_get_all_atom_name();
extern DCODE dc_unix();


/*************************************************************************
*   Public Functions in "deref.c" & Dereference Macros.			 *
*************************************************************************/

extern CELL *dereference();

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

extern int passive_unify();
extern int is_ground();


/*************************************************************************
*   Public Functions & Variables in "unify.c".				 *
*************************************************************************/

/** Functions for Active Unification **/
extern active_unify();
extern active_unify_with_atom();
extern active_unify_with_nil();
extern active_unify_with_integer();
extern active_unify_with_float();
extern active_unify_with_list();
extern active_unify_with_vector();
extern active_unify_with_string();
extern active_unify_with_nue();
extern active_unify_with_shoen();
extern active_unify_with_undef();
extern active_unify_with_hook();
extern active_unify_with_mhook();
extern active_unify_with_stream();
extern active_unify_stream_atom();
extern active_unify_stream_nil();
extern active_unify_stream_integer();
extern active_unify_stream_float();
extern active_unify_stream_list();
extern active_unify_stream_vector();
extern active_unify_stream_string();
extern active_unify_stream_nue();
extern active_unify_stream_shoen();
extern active_unify_stream_hook();
extern active_unify_stream_stream();

/** Make D-Code Goal **/
extern GOAL_RECORD *make_unify_goal_for_merger();
extern make_unify_list_list_goal_and_enqueue();
extern make_unify_vector_vector_goal_and_enqueue();

/** D-Code for Active Unification **/
extern DCODE dc_unify();
extern DCODE dc_unify_list_list();
extern DCODE dc_unify_list_list2();
extern DCODE dc_unify_vector_vector();
extern DCODE dc_unify_vector_vector2();


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
extern initialize_priority_queue();
extern enqueue();
#if TWO_WAY_READY_GOAL_POOL
extern enqueue_head();
extern enqueue_tail();
#else
#define enqueue_head(grec) enqueue(grec)
#define enqueue_tail(grec) enqueue(grec)
#endif
extern enqueue_with_priority();
#if TWO_WAY_READY_GOAL_POOL
extern enqueue_with_priority_head();
extern enqueue_with_priority_tail();
#else
#define enqueue_with_priority_head(grec) enqueue_with_priority(grec)
#define enqueue_with_priority_tail(grec) enqueue_with_priority(grec)
#endif
extern int dequeue();

/** Functions for Suspension **/
extern popup_suspension_stack();
extern single_wait_suspend();
extern body_builtin_suspend();
extern body_builtin_swap();
extern wakeup_goals();
extern move_suspension_queue();


/*************************************************************************
*   Public Functions & Variables in "shoen.c".				 *
*************************************************************************/

/** Variables **/
extern PARENT_RECORD *grand_mother;
extern CELL *result_of_grand_mother;
extern int report_raise_flag;
extern int shoen_tree_trace_flag;

/** Functions for Shoen Control **/
extern initialize_shoen_tree();
extern PARENT_RECORD *create_shoen();
extern start_shoen();
extern stop_shoen();
extern abort_shoen();
extern remove_shoen();
extern terminate_shoen();
extern int shoen_statistics();
extern shoen_add_resource();
extern int resource_limit();

/** Functions for Shoen Report Stream **/
extern PARENT_RECORD *search_parent_tag();
extern unify_exception_with_report_stream();
extern unify_exception_with_parent_report_stream();
extern unify_message_with_parent_report_stream();

/** Functions for Shoen Tree Trace **/
extern inspect_shoen_tree();


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
extern initialize_exception_tag_table();
extern raise();
extern body_goal_exception();
extern body_goal_exception2();
extern exception_active_unify_fail();
extern exception_illegal_merger_input();


/*************************************************************************
*   Public Functions & Variables in "atom.c".				 *
*************************************************************************/

extern initialize_atom_table();
extern CHAR *atom_name();
extern unsigned int new_atom();
extern unsigned int intern_atom();
extern unsigned int intern_atom2();
extern unsigned int gensym_count1;
extern unsigned int gensym_count2;


/*************************************************************************
*   Public Functions & Variables in "memory.c".				 *
*************************************************************************/

/** Functions for Heap Area **/
extern initialize_heap();
extern switch_heap();

/** Functions for Code Area **/
extern initialize_code();
extern initialize_code2();
extern switch_code();

/** Functions for Temporary Area **/
extern unsigned char *t1_alloc();
extern t1_free();
extern unsigned char *t2_alloc();
extern t2_free();
extern unsigned char *t3_alloc();
extern t3_free();
extern unsigned char *t4_alloc();
extern t4_free();


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
    int		 (* function)();
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
extern int lookup_module();
extern int enter_module();
extern int remove_module();
extern OBJ *find_predicate();
extern function_to_mod_pred_arity();

/** Functions to Set/Reset Module Debug Flag **/
extern int set_module_trace_flag();
extern int get_module_trace_flag();
extern int set_predicate_spy_flag();
extern int get_predicate_spy_flag();
extern int get_public_predicates();
extern int get_spied_predicates();
extern int reset_module_profile_info();
extern int get_module_profile_info();

/** Functions to Load Module **/
extern int load_from_sav_or_asm_file();
extern int load_from_asm_file();
extern int save_to_sav_file();


/*************************************************************************
*   Public Functions & Variables in "dcode.c".				 *
*************************************************************************/

extern initialize_dcode_table();
extern dcode_function_to_mod_pred_arity();


/*************************************************************************
*   Public Functions & Variables in "float.c".				 *
*************************************************************************/

extern initialize_float_calculator();

extern int float_equal();
extern int float_not_equal();
extern int float_less_than();
extern int float_not_less_than();

extern int float_add();
extern int float_subtract();
extern int float_multiply();
extern int float_divide();
extern	   float_minus();
extern	   float_abs();
extern	   float_min();
extern	   float_max();
extern int float_floor();
extern int float_sqrt();
extern int float_ln();
extern int float_log();
extern int float_exp();
extern int float_pow();
extern int float_sin();
extern int float_cos();
extern int float_tan();
extern int float_asin();
extern int float_acos();
extern int float_atan();
extern int float_atan2();
extern int float_sinh();
extern int float_cosh();
extern int float_tanh();

extern int float_to_integer();
extern	   integer_to_float();

extern CHAR *float_to_string();
extern int string_to_float();


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

extern int get_string_type();
extern int new_string();
extern int copy_string();
extern int get_string_element();
extern int set_string_element();
extern int get_substring();
extern int set_substring();
extern int append_string();
extern int string_and();
extern int string_or();
extern int string_exclusive_or();
extern int string_complement();
extern int atom_to_string();
extern int string_to_atom();
extern int get_print_image();
extern CELL *convert_to_kl1_string();
extern CELL *convert_to_kl1_string2();
extern CHAR *convert_to_c_string();


/*************************************************************************
*   Public Functions & Variables in "gc.c".				 *
*************************************************************************/

extern gc();
extern display_memory_statistics();
extern int gc_counter;
extern int gc_panic_flag;


/*************************************************************************
*   Public Functions & Variables in "gc_ctrl.c".			 *
*************************************************************************/

extern gc_ready_queue();
extern gc_goal_record();
extern gc_parent_record();
extern gc_suspension_queue();
extern gc_suspension_record();
extern gc_io_table();
extern gc_timer_table();


/*************************************************************************
*   Public Functions & Variables in "gc_cell.c".			 *
*************************************************************************/

extern gc_cell();


/*************************************************************************
*   Public Functions & Variables in "gc_code.c".			 *
*************************************************************************/

extern gc_code_area();
extern OBJ *gc_predicate();
extern OBJ *gc_code_module();
extern gc_constant_section();
extern CELL *gc_cell_in_constant_section();


/*************************************************************************
*   Public Functions & Variables in "gc_dead.c".			 *
*************************************************************************/

extern deadlock_check_and_report();
extern terminate_shoen_by_gc();
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
extern collect_value();
#else
#if EAGER_DEADLOCK_DETECTION
extern detect_deadlock_by_collect_value();
#endif
#endif

#if EAGER_DEADLOCK_DETECTION
extern detect_deadlock_in_suspension();
extern detect_deadlock_in_unification1();
extern detect_deadlock_in_unification2();
#endif


/*************************************************************************
*   Public Functions & Variables in "instr.c".				 *
*************************************************************************/

extern initialize_instruction_table();


/*************************************************************************
*   Public Functions & Variables in "invassm.c".			 *
*************************************************************************/

#if INSTRUCTION_TRACE
extern inverse_assemble_one();
#endif


/*************************************************************************
*   Public Functions & Variables in "assemble.c".			 *
*************************************************************************/

extern int assemble();
#define ASSEMBLE_SUCCESS	  0
#define ASSEMBLE_ERROR		  1
#define ASSEMBLE_MODULE_PROTECTED 2
#define ASSEMBLE_REQUEST_GC	  3


/*************************************************************************
*   Public Functions & Variables in "saveload.c".			 *
*************************************************************************/

extern save_module();
extern int load_module();
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
int load_and_link_native_code_module();


/*************************************************************************
*   Public Functions & Variables in "tracer.c".				 *
*************************************************************************/

extern initialize_tracer();
extern write_goal_record();
extern write_goal();
extern int display_suspended_goals();
extern DCODE dc_debug_monitor_stream();
extern klb_b_debug_monitor_stream();


/*************************************************************************
*   Public Functions & Variables in "print.c".				 *
*************************************************************************/

extern initialize_print_routine();
extern set_print_file();
extern set_print_var_mode();
extern int get_print_var_mode();
#define PRINT_VAR_MODE_ABC 0
#define PRINT_VAR_MODE_ADR 1
extern set_print_deadlock();
extern print_term();
extern print_term2();
extern fprint_term();
extern print_string();
extern fprint_string();
extern CELL *lookup_var();


/*************************************************************************
*   Public Functions & Variables in "io.c".				 *
*************************************************************************/

extern initialize_io();
extern io_ctrl_when_exit();
extern io_ctrl_when_stop();
extern io_ctrl_when_resume();
extern int read_console();
extern int getc_window();
extern ungetc_window();
extern int request_keyboard();
extern request_console();
extern do_keyboard_interrupt();
extern int is_there_goal_waiting_for_keyboard_input();
extern int is_there_goal_waiting_for_keyboard_interrupt();


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

extern int create_window();
extern int remove_window();
extern int remove_all_windows();
extern int show_window();
extern int hide_window();
extern int create_file();
extern int open_file();
extern int close_file();
extern int remove_file();
extern int write_char();
extern int write_line();
extern int write_buffer();
extern int write_term();
extern int abort_read_command();
extern int read_char();
extern int read_line();
extern int read_buffer();
extern int read_token();


/*************************************************************************
*   Public Functions & Variables in "timer.c".				 *
*************************************************************************/

extern CELL *timer_table;
extern initialize_timer();
extern timer_wakeup_goal();
extern set_timer_on_after();
extern set_timer_on_at();
extern int get_time_count();
extern int is_there_goal_waiting_for_timer();


/*************************************************************************
*   Public Functions & Variables in "path.c".				 *
*************************************************************************/

extern CHAR *expand_path_name();
