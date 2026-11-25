/*************************************************************************
*  PDSS (PIMOS Development Support System)  Version 2.52		 *
*  (C) Copyright 1988,1989,1990,1991,1992.				 *
*  Institute for New Generation Computer Technology (ICOT), Japan.	 *
*  Read "../COPYRIGHT" for detailed information.			 *
*************************************************************************/

#include "pdss.h"

#define NUMBER_OF_DCODE 128
static PREDICATE_ENTRY dcode_table[NUMBER_OF_DCODE];
static PREDICATE_ENTRY *pred_func_hash[PREDICATE_TABLE_SIZE];
static PREDICATE_ENTRY *func_pred_hash[PREDICATE_TABLE_SIZE];

#define DD(func, name, arity){\
    dcode_table[n].pid = intern_atom2(name)|(arity<<16);\
    dcode_table[n].function = func;\
    n++;\
}

initialize_dcode_table()
{
    int m, n;
    MODULE_ENTRY *mod_table;
    n = 0;
    /*** Arithmetic Calculation ***/
    DD(dc_add,			"add",			3);
    DD(dc_subtract,		"subtract",		3);
    DD(dc_multiply,		"multiply",		3);
    DD(dc_divide,		"divide",		3);
    DD(dc_modulo,		"modulo",		3);
    DD(dc_minus,		"minus",		2);
    DD(dc_increment,		"increment",		2);
    DD(dc_decrement,		"decrement",		2);
    DD(dc_abs,			"abs",			2);
    DD(dc_min,			"min",			3);
    DD(dc_max,			"max",			3);
    /*** Logical Calculation ***/
    DD(dc_and,			"and",			3);
    DD(dc_or,			"or",			3);
    DD(dc_exclusive_or,		"exclusive_or",		3);
    DD(dc_complement,		"complement",		2);
    DD(dc_shift_left,		"shift_left",		3);
    DD(dc_shift_right,		"shift_right",		3);
    /*** Vector/String/Atom ***/
    DD(dc_vector,		"vector",		3);
    DD(dc_new_vector,		"new_vector",		2);
    DD(dc_vector_element,	"vector_element",	4);
    DD(dc_set_vector_element,	"set_vector_element",	5);
    DD(dc_string,		"string",		4);
    DD(dc_new_string,		"new_string",		3);
    DD(dc_string_element,	"string_element",	4);
    DD(dc_set_string_element,	"set_string_element",	4);
    DD(dc_substring,		"substring",		5);
    DD(dc_set_substring,	"set_substring",	4);
    DD(dc_append_string,	"append_string",	3);
    DD(dc_string_and,		"string_and",		3);
    DD(dc_string_or,		"string_or",		3);
    DD(dc_string_exclusive_or,	"string_exclusive_or",	3);
    DD(dc_intern_atom,		"intern_atom",		2);
    DD(dc_atom_name,		"atom_name",		2);
    DD(dc_atom_number,		"atom_number",		2);
    /*** Float ***/
    DD(dc_float_add,		"float_add",		3);
    DD(dc_float_subtract,	"float_subtract",	3);
    DD(dc_float_multiply,	"float_multiply",	3);
    DD(dc_float_divide,		"float_divide",		3);
    DD(dc_float_minus,		"float_minus",		2);
    DD(dc_float_abs,		"float_abs",		2);
    DD(dc_float_min,		"float_min",		3);
    DD(dc_float_max,		"float_max",		3);
    DD(dc_float_floor,		"float_floor",		2);
    DD(dc_float_sqrt,		"float_sqrt",		2);
    DD(dc_float_ln,		"float_ln",		2);
    DD(dc_float_log,		"float_log",		2);
    DD(dc_float_exp,		"float_exp",		2);
    DD(dc_float_pow,		"float_pow",		3);
    DD(dc_float_sin,		"float_sin",		2);
    DD(dc_float_cos,		"float_cos",		2);
    DD(dc_float_tan,		"float_tan",		2);
    DD(dc_float_asin,		"float_asin",		2);
    DD(dc_float_acos,		"float_acos",		2);
    DD(dc_float_atan,		"float_atan",		2);
    DD(dc_float_atan2,		"float_atan2",		3);
    DD(dc_float_sinh,		"float_sinh",		2);
    DD(dc_float_cosh,		"float_cosh",		2);
    DD(dc_float_tanh,		"float_tanh",		2);
    DD(dc_float_to_integer,	"float_to_integer",	2);
    DD(dc_integer_to_float,	"integer_to_float",	2);
    /*** Shoen ***/
    DD(dc_create_shoen,		"create_shoen",		7);
    DD(dc_start_shoen,		"start_shoen",		2);
    DD(dc_stop_shoen,		"stop_shoen",		2);
    DD(dc_abort_shoen,		"abort_shoen",		2);
    DD(dc_remove_shoen,		"remove_shoen",		1);
    DD(dc_shoen_statistics,	"shoen_statistics",	3);
    DD(dc_shoen_add_resource,	"shoen_add_resource",	3);
    DD(dc_consume_resource,	"consume_resource",	1);
    /*** Window/File Device ***/
    DD(dc_create_window,	"create_window",	4);
    DD(dc_remove_window,	"remove_window",	2);
    DD(dc_show_window,		"show_window",		3);
    DD(dc_hide_window,		"hide_window",		3);
    DD(dc_remove_file,		"remove_file",		2);
    DD(dc_open_file,		"open_file",		5);
    DD(dc_close_file,		"close_file",		3);
    DD(dc_write_char,		"write_char",		4);
    DD(dc_write_line,		"write_line",		4);
    DD(dc_write_buffer,		"write_buffer",		4);
    DD(dc_write_term,		"write_term",		6);
    DD(dc_read_char,		"read_char",		4);
    DD(dc_read_line,		"read_line",		4);
    DD(dc_read_buffer,		"read_buffer",		5);
    DD(dc_read_token,		"read_token",		5);
    DD(dc_abort_read_command,	"abort_read_command",	3);
    /*** Directory Device ***/
    DD(dc_test_directory,	"test_directory",	2);
    DD(dc_directory_pathname,	"directory_pathname",	3);
    DD(dc_listing_files,	"listing_files",	4);
    DD(dc_delete_files,		"delete_files",		3);
    /*** Timer Device ***/
    DD(dc_on_at,		"on_at",		3);
    DD(dc_on_after,		"on_after",		3);
    /*** Code ***/
    DD(dc_predicate_to_code,	"predicate_to_code",	4);
    DD(dc_code_to_predicate,	"code_to_predicate",	5);
    DD(dc_save_module,		"save_module",		3);
    DD(dc_load_module,		"load_module",		3);
    DD(dc_assemble_module,	"assemble_module",	3);
    DD(dc_remove_module,	"remove_module",	2);
    DD(dc_get_public_predicates,"get_public_predicates",3);
    DD(dc_trace_module,		"trace_module",		3);
    DD(dc_get_module_status,	"get_module_status",	3);
    DD(dc_spy_predicate,	"spy_predicate",	3);
    DD(dc_get_spied_predicates, "get_spied_predicates", 3);
    DD(dc_reset_profile_info,	"reset_profile_info",	2);
    DD(dc_get_profile_info,	"get_profile_info",	3);
    /*** System ***/
    DD(dc_apply,		"apply",		2);
    DD(dc_raise,		"raise",		3);
    DD(dc_rate,			"rate",			2);
    DD(dc_rltv,			"rltv",			2);
    DD(dc_hash,			"hash",			3);
    DD(dc_get_print_image,	"get_print_image",	6);
    DD(dc_get_all_atom_name,	"get_all_atom_name",	1);
    DD(dc_unix,			"unix",			3);
    DD(dc_debug_monitor_stream, "debug_monitor_stream", 3);
    /*** Unification ***/
    DD(dc_unify,		"unify",		2);
    DD(dc_unify_list_list,	"unify_list_list",	2);
    DD(dc_unify_vector_vector,	"unify_vector_vector",	3);
    m = n;
    DD(dc_unify_list_list2,	"unify_list_list",	2);
    DD(dc_unify_vector_vector2, "unify_vector_vector",	3);
    rehash_predicate_table(dcode_table, pred_func_hash, func_pred_hash, n, m);
    enter_module(ATOM_DDD_SYSTEM, 0, 0, &mod_table);
    mod_table->predicate_tbl = dcode_table;
    mod_table->pid_func_hash_tbl = pred_func_hash;
    mod_table->func_pid_hash_tbl = func_pred_hash;
}

dcode_function_to_mod_pred_arity(func, mod, pred, arity)
    int (* func)();
    unsigned int *mod, *pred, *arity;
{
    register PREDICATE_ENTRY *p;
    p = func_pred_hash[HashFuncAddr(func)];
    while(p){
	if(p->function == func){
	    *mod = ATOM_DDD_SYSTEM;
	    *pred = p->pid&0xFFFF;
	    *arity = (p->pid>>16)&0xFFFF;
	    return;
	}
	p = p->p2;
    }
    *mod = ATOM_DDD_SYSTEM;
    *pred = ATOM_DDD_SYSTEM;
    *arity = 0;
}
