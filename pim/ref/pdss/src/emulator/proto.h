/* Prototypes of PDSS's external functions, generated once by
   tools/mkproto.py from the definitions (then maintained by hand). */


/* assemble.c */
extern int ChkAndPutRAddr(int raddr, OBJ *pc);
extern CHAR *scan_name(CHAR **s);
extern int assemble(FILE *file, MODULE_ENTRY **module);
extern int make_entry_table(OBJ **pcp, FILE *file);

/* atom.c */
extern CHAR *atom_name(unsigned int atom);
extern unsigned int new_atom(void);
extern unsigned int intern_atom(CHAR *name);
extern unsigned int intern_atom2(CHAR *name);
extern int initialize_atom_table(void);

/* blt_basic.c */
extern DCODE dc_add(void);
extern int blt_b_add(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_subtract(void);
extern int blt_b_subtract(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_multiply(void);
extern int blt_b_multiply(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_divide(void);
extern int blt_b_divide(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_modulo(void);
extern int blt_b_modulo(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_minus(void);
extern int blt_b_minus(CELL *in1, CELL *out);
extern DCODE dc_increment(void);
extern int blt_b_increment(CELL *in1, CELL *out);
extern DCODE dc_decrement(void);
extern int blt_b_decrement(CELL *in1, CELL *out);
extern DCODE dc_abs(void);
extern int blt_b_abs(CELL *in1, CELL *out);
extern DCODE dc_min(void);
extern int blt_b_min(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_max(void);
extern int blt_b_max(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_and(void);
extern int blt_b_and(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_or(void);
extern int blt_b_or(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_exclusive_or(void);
extern int blt_b_exclusive_or(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_complement(void);
extern int blt_b_complement(CELL *in1, CELL *out);
extern DCODE dc_shift_left(void);
extern int blt_b_shift_left(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_shift_right(void);
extern int blt_b_shift_right(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_vector(void);
extern int blt_b_vector(CELL *vect, CELL *size, CELL *newvect);
extern DCODE dc_new_vector(void);
extern int blt_b_new_vector(CELL *vect, CELL *size);
extern DCODE dc_vector_element(void);
extern int blt_b_vector_element(CELL *vect, CELL *pos, CELL *elem, CELL *newvect);
extern DCODE dc_set_vector_element(void);
extern int blt_b_set_vector_element(CELL *vect, CELL *pos, CELL *oldelem, CELL *elem, CELL *newvect);
extern DCODE dc_string(void);
extern int blt_b_string(CELL *str, CELL *len, CELL *width, CELL *newstr);
extern DCODE dc_new_string(void);
extern int blt_b_new_string(CELL *str, CELL *len, CELL *width);
extern DCODE dc_string_element(void);
extern int blt_b_string_element(CELL *str, CELL *pos, CELL *elem, CELL *newstr);
extern DCODE dc_set_string_element(void);
extern int blt_b_set_string_element(CELL *str, CELL *pos, CELL *elem, CELL *newstr);
extern DCODE dc_substring(void);
extern int blt_b_substring(CELL *str, CELL *pos, CELL *len, CELL *substr, CELL *newstr);
extern DCODE dc_set_substring(void);
extern int blt_b_set_substring(CELL *str, CELL *pos, CELL *substr, CELL *newstr);
extern DCODE dc_append_string(void);
extern int blt_b_append_string(CELL *str1, CELL *str2, CELL *newstr);
extern DCODE dc_string_and(void);
extern int blt_b_string_and(CELL *str1, CELL *str2, CELL *newstr, CELL *newstr2);
extern DCODE dc_string_or(void);
extern int blt_b_string_or(CELL *str1, CELL *str2, CELL *newstr, CELL *newstr2);
extern DCODE dc_string_exclusive_or(void);
extern int blt_b_string_exclusive_or(CELL *str1, CELL *str2, CELL *newstr, CELL *newstr2);
extern DCODE dc_string_complement(void);
extern int blt_b_string_complement(CELL *str, CELL *newstr);
extern int blt_b_new_atom(CELL *atom);
extern DCODE dc_intern_atom(void);
extern int blt_b_intern_atom(CELL *atom, CELL *name);
extern DCODE dc_atom_name(void);
extern int blt_b_atom_name(CELL *atom, CELL *name);
extern DCODE dc_atom_number(void);
extern int blt_b_atom_number(CELL *atom, CELL *number);

/* blt_code.c */
extern DCODE dc_predicate_to_code(void);
extern int blt_b_predicate_to_code(CELL *mod, CELL *pred, CELL *arity, CELL *code);
extern DCODE dc_code_to_predicate(void);
extern int blt_b_code_to_predicate(CELL *code, CELL *mod, CELL *pred, CELL *arity, CELL *info);
extern DCODE dc_save_module(void);
extern int blt_b_save_module(CELL *mod, CELL *file, CELL *status);
extern DCODE dc_load_module(void);
extern int blt_b_load_module(CELL *mod, CELL *file, CELL *status);
extern DCODE dc_assemble_module(void);
extern int blt_b_assemble_module(CELL *mod, CELL *file, CELL *status);
extern DCODE dc_remove_module(void);
extern int blt_b_remove_module(CELL *mod, CELL *status);
extern DCODE dc_get_public_predicates(void);
extern int blt_b_get_public_predicates(CELL *mod, CELL *list, CELL *status);
extern DCODE dc_trace_module(void);
extern int blt_b_trace_module(CELL *mod, CELL *flag, CELL *status);
extern DCODE dc_get_module_status(void);
extern int blt_b_get_module_status(CELL *mod, CELL *flag, CELL *status);
extern DCODE dc_spy_predicate(void);
extern int blt_b_spy_predicate(CELL *code, CELL *flag, CELL *status);
extern DCODE dc_get_spied_predicates(void);
extern int blt_b_get_spied_predicates(CELL *mod, CELL *list, CELL *status);
extern DCODE dc_reset_profile_info(void);
extern int blt_b_reset_profile_info(CELL *mod, CELL *status);
extern DCODE dc_get_profile_info(void);
extern int blt_b_get_profile_info(CELL *mod, CELL *list, CELL *status);

/* blt_float.c */
extern int blt_g_float_add(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_subtract(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_multiply(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_divide(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_minus(CELL *in, CELL *out);
extern int blt_g_float_abs(CELL *in, CELL *out);
extern int blt_g_float_min(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_max(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_floor(CELL *in, CELL *out);
extern int blt_g_float_sqrt(CELL *in, CELL *out);
extern int blt_g_float_ln(CELL *in, CELL *out);
extern int blt_g_float_log(CELL *in, CELL *out);
extern int blt_g_float_exp(CELL *in, CELL *out);
extern int blt_g_float_pow(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_sin(CELL *in, CELL *out);
extern int blt_g_float_cos(CELL *in, CELL *out);
extern int blt_g_float_tan(CELL *in, CELL *out);
extern int blt_g_float_asin(CELL *in, CELL *out);
extern int blt_g_float_acos(CELL *in, CELL *out);
extern int blt_g_float_atan(CELL *in, CELL *out);
extern int blt_g_float_atan2(CELL *in1, CELL *in2, CELL *out);
extern int blt_g_float_sinh(CELL *in, CELL *out);
extern int blt_g_float_cosh(CELL *in, CELL *out);
extern int blt_g_float_tanh(CELL *in, CELL *out);
extern int blt_g_float_to_integer(CELL *in, CELL *out);
extern int blt_g_integer_to_float(CELL *in, CELL *out);
extern DCODE dc_float_add(void);
extern int blt_b_float_add(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_subtract(void);
extern int blt_b_float_subtract(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_multiply(void);
extern int blt_b_float_multiply(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_divide(void);
extern int blt_b_float_divide(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_minus(void);
extern int blt_b_float_minus(register CELL *in, CELL *out);
extern DCODE dc_float_abs(void);
extern int blt_b_float_abs(register CELL *in, CELL *out);
extern DCODE dc_float_min(void);
extern int blt_b_float_min(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_max(void);
extern int blt_b_float_max(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_floor(void);
extern int blt_b_float_floor(register CELL *in, CELL *out);
extern DCODE dc_float_sqrt(void);
extern int blt_b_float_sqrt(register CELL *in, CELL *out);
extern DCODE dc_float_ln(void);
extern int blt_b_float_ln(register CELL *in, CELL *out);
extern DCODE dc_float_log(void);
extern int blt_b_float_log(register CELL *in, CELL *out);
extern DCODE dc_float_exp(void);
extern int blt_b_float_exp(register CELL *in, CELL *out);
extern DCODE dc_float_pow(void);
extern int blt_b_float_pow(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_sin(void);
extern int blt_b_float_sin(register CELL *in, CELL *out);
extern DCODE dc_float_cos(void);
extern int blt_b_float_cos(register CELL *in, CELL *out);
extern DCODE dc_float_tan(void);
extern int blt_b_float_tan(register CELL *in, CELL *out);
extern DCODE dc_float_asin(void);
extern int blt_b_float_asin(register CELL *in, CELL *out);
extern DCODE dc_float_acos(void);
extern int blt_b_float_acos(register CELL *in, CELL *out);
extern DCODE dc_float_atan(void);
extern int blt_b_float_atan(register CELL *in, CELL *out);
extern DCODE dc_float_atan2(void);
extern int blt_b_float_atan2(CELL *in1, CELL *in2, CELL *out);
extern DCODE dc_float_sinh(void);
extern int blt_b_float_sinh(register CELL *in, CELL *out);
extern DCODE dc_float_cosh(void);
extern int blt_b_float_cosh(register CELL *in, CELL *out);
extern DCODE dc_float_tanh(void);
extern int blt_b_float_tanh(register CELL *in, CELL *out);
extern DCODE dc_float_to_integer(void);
extern int blt_b_float_to_integer(register CELL *in, CELL *out);
extern DCODE dc_integer_to_float(void);
extern int blt_b_integer_to_float(register CELL *in, CELL *out);

/* blt_iodev.c */
extern DCODE dc_create_window(void);
extern int blt_b_create_window(CELL *name, CELL *status, CELL *intrup, CELL *ioid);
extern DCODE dc_remove_window(void);
extern int blt_b_remove_window(CELL *ioid, CELL *status);
extern DCODE dc_show_window(void);
extern int blt_b_show_window(CELL *ioid, CELL *status, CELL *newio);
extern DCODE dc_hide_window(void);
extern int blt_b_hide_window(CELL *ioid, CELL *status, CELL *newio);
extern int blt_b_create_file(CELL *status, CELL *ioid);
extern DCODE dc_remove_file(void);
extern int blt_b_remove_file(CELL *ioid, CELL *status);
extern DCODE dc_open_file(void);
extern int blt_b_open_file(CELL *ioid, CELL *name, CELL *mode, CELL *status, CELL *newio);
extern DCODE dc_close_file(void);
extern int blt_b_close_file(CELL *ioid, CELL *status, CELL *newio);
extern DCODE dc_write_char(void);
extern int blt_b_write_char(CELL *ioid, CELL *chr, CELL *status, CELL *newio);
extern DCODE dc_write_line(void);
extern int blt_b_write_line(CELL *ioid, CELL *line, CELL *status, CELL *newio);
extern DCODE dc_write_buffer(void);
extern int blt_b_write_buffer(CELL *ioid, CELL *buffer, CELL *status, CELL *newio);
extern DCODE dc_write_term(void);
extern int blt_b_write_term(CELL *ioid, CELL *term, CELL *len, CELL *dep, CELL *status, CELL *newio);
extern DCODE dc_read_char(void);
extern int blt_b_read_char(CELL *ioid, CELL *chr, CELL *status, CELL *newio);
extern DCODE dc_read_line(void);
extern int blt_b_read_line(CELL *ioid, CELL *line, CELL *status, CELL *newio);
extern DCODE dc_read_buffer(void);
extern int blt_b_read_buffer(CELL *ioid, CELL *len, CELL *buffer, CELL *status, CELL *newio);
extern DCODE dc_read_token(void);
extern int blt_b_read_token(CELL *ioid, CELL *token, CELL *varnum, CELL *status, CELL *newio);
extern DCODE dc_abort_read_command(void);
extern int blt_b_abort_read_command(CELL *ioid, CELL *status, CELL *newio);
extern DCODE dc_test_directory(void);
extern int blt_b_test_directory(CELL *name, CELL *status);
extern DCODE dc_directory_pathname(void);
extern int blt_b_directory_pathname(CELL *name, CELL *exname, CELL *status);
extern DCODE dc_listing_files(void);
extern int blt_b_listing_files(CELL *name, CELL *wild, CELL *list, CELL *status);
extern DCODE dc_delete_files(void);
extern int blt_b_delete_files(CELL *name, CELL *wild, CELL *status);
extern int blt_b_get_time_count(CELL *time, CELL *status);
extern DCODE dc_on_at(void);
extern int blt_b_on_at(CELL *time, CELL *done, CELL *status);
extern DCODE dc_on_after(void);
extern int blt_b_on_after(CELL *time, CELL *done, CELL *status);

/* blt_shoen.c */
extern DCODE dc_create_shoen(void);
extern int blt_b_create_shoen(CELL *code, CELL *argv, CELL *pmin, CELL *pmax, CELL *tag, CELL *shoen, CELL *report);
extern DCODE dc_start_shoen(void);
extern int blt_b_start_shoen(CELL *shoen, CELL *newshoen);
extern DCODE dc_stop_shoen(void);
extern int blt_b_stop_shoen(CELL *shoen, CELL *newshoen);
extern DCODE dc_abort_shoen(void);
extern int blt_b_abort_shoen(CELL *shoen, CELL *newshoen);
extern DCODE dc_remove_shoen(void);
extern int blt_b_remove_shoen(CELL *shoen);
extern DCODE dc_shoen_statistics(void);
extern int blt_b_shoen_statistics(CELL *shoen, CELL *red, CELL *newshoen);
extern DCODE dc_shoen_add_resource(void);
extern int blt_b_shoen_add_resource(CELL *shoen, CELL *red, CELL *newshoen);
extern DCODE dc_consume_resource(void);
extern int blt_b_consume_resource(CELL *red);

/* blt_system.c */
extern int blt_display_console(CELL *x);
extern int blt_put_console(CELL *x);
extern int blt_read_console(CELL *x);
extern DCODE dc_apply(void);
extern int blt_b_apply(CELL *code, CELL *argv);
extern DCODE dc_raise(void);
extern int blt_b_raise(CELL *tag, CELL *key, CELL *info);
extern int blt_b_merge(CELL *in, CELL *out);
extern int blt_b_current_node(CELL *cp, CELL *tp);
extern int blt_b_current_processor(CELL *cp, CELL *sx, CELL *sy);
extern int blt_b_current_priority(CELL *cp, CELL *min, CELL *max);
extern DCODE dc_rate(void);
extern int blt_b_rate(CELL *rate, CELL *prio);
extern DCODE dc_rltv(void);
extern int blt_b_rltv(CELL *rate, CELL *prio);
extern DCODE dc_hash(void);
extern int blt_b_hash(CELL *x, CELL *hv, CELL *newx);
extern int blt_b_unbound(CELL *x, CELL *pe, CELL *addr, CELL *newx);
extern int blt_b_unbound2(CELL *x, CELL *result);
extern DCODE dc_get_print_image(void);
extern int blt_b_get_print_image(CELL *atomic, CELL *mode, CELL *left, CELL *string, CELL *len, CELL *tail);
extern int blt_statistics(CELL *ct, CELL *hs, CELL *hu, CELL *cs, CELL *cu, CELL *sy);
extern int blt_get_cpu_time(CELL *cpu);
extern int blt_get_current_time(CELL *year, CELL *month, CELL *day, CELL *hour, CELL *minute, CELL *second);
extern int blt_g_tag_and_value(CELL *data, CELL *tag, CELL *value);
extern int blt_g_register_tag_and_value(CELL *data, CELL *tag, CELL *value);
extern int blt_g_word(CELL *addr, CELL *tag, CELL *value);
extern int blt_g_set_tag_and_value(CELL *data, CELL *tag, CELL *value);
extern int blt_g_halt(CELL *code);
extern int blt_g_request_gc(CELL *flag);
extern int blt_g_set_scheduling_switch(CELL *flag);
extern int blt_g_set_trace_switch(CELL *flag);
extern int blt_g_set_backtrace_switch(CELL *flag);
extern DCODE dc_get_all_atom_name(void);
extern int blt_b_get_all_atom_name(CELL *list);
extern DCODE dc_unix(void);
extern int blt_b_unix(CELL *command, CELL *flag, CELL *status);
extern int blt_b_get_library_directory(CELL *name);

/* dcode.c */
extern int initialize_dcode_table(void);
extern int dcode_function_to_mod_pred_arity(OBJ *code, unsigned int *mod, unsigned int *pred, unsigned int *arity);

/* deref.c */
extern CELL *dereference(CELL *reg);

/* emulate.c */
extern int emulate(void);
extern int nop(void);

/* exception.c */
extern int initialize_exception_tag_table(void);
extern int pdss_raise(unsigned int tag, CELL *type, CELL *info);
extern int body_goal_exception(unsigned int excp_code, unsigned int mod, unsigned int pred, unsigned int argn, CELL *args);
extern int body_goal_exception2(int excp_code, CELL *cd, CELL *av);
extern int exception_active_unify_fail(CELL *x, CELL *y);
extern int exception_illegal_merger_input(CELL *x, CELL *strm);
extern int body_builtin_exception(unsigned int excp_code, unsigned int where, unsigned int opcode, unsigned int argio, ...);

/* float.c */
extern int initialize_float_calculator(void);
extern int float_equal(int32_t *x, int32_t *y);
extern int float_not_equal(int32_t *x, int32_t *y);
extern int float_less_than(int32_t *x, int32_t *y);
extern int float_not_less_than(int32_t *x, int32_t *y);
extern int float_add(int32_t *x, int32_t *y, int32_t *z);
extern int float_subtract(int32_t *x, int32_t *y, int32_t *z);
extern int float_multiply(int32_t *x, int32_t *y, int32_t *z);
extern int float_divide(int32_t *x, int32_t *y, int32_t *z);
extern int float_minus(int32_t *x, int32_t *z);
extern int float_abs(int32_t *x, int32_t *z);
extern int float_min(int32_t *x, int32_t *y, int32_t *z);
extern int float_max(int32_t *x, int32_t *y, int32_t *z);
extern int float_floor(int32_t *x, int32_t *z);
extern int float_sqrt(int32_t *x, int32_t *z);
extern int float_ln(int32_t *x, int32_t *z);
extern int float_log(int32_t *x, int32_t *z);
extern int float_exp(int32_t *x, int32_t *z);
extern int float_pow(int32_t *x, int32_t *y, int32_t *z);
extern int float_sin(int32_t *x, int32_t *z);
extern int float_cos(int32_t *x, int32_t *z);
extern int float_tan(int32_t *x, int32_t *z);
extern int float_asin(int32_t *x, int32_t *z);
extern int float_acos(int32_t *x, int32_t *z);
extern int float_atan(int32_t *x, int32_t *z);
extern int float_atan2(int32_t *x, int32_t *y, int32_t *z);
extern int float_sinh(int32_t *x, int32_t *z);
extern int float_cosh(int32_t *x, int32_t *z);
extern int float_tanh(int32_t *x, int32_t *z);
extern int float_to_integer(int32_t *x, int32_t *y);
extern int integer_to_float(int32_t *x, int32_t *y);
extern CHAR *float_to_string(int32_t *x);
extern int string_to_float(register CHAR *s, int32_t *z);

/* gc.c */
extern int gc(void);
extern int display_memory_statistics(int f);

/* gc_cell.c */
extern int gc_cell(register CELL *old, register CELL *new);

/* gc_code.c */
extern int gc_code_area(void);
extern OBJ *gc_predicate(OBJ *old);
extern OBJ *gc_code_module(OBJ *old);
extern int gc_constant_section(CELL *from, CELL *to, CELL *bottom);
extern CELL *gc_cell_in_constant_section(CELL *old);

/* gc_ctrl.c */
extern int gc_ready_queue(void);
extern int gc_goal_record(register GOAL_RECORD *old, register GOAL_RECORD *new);
extern int gc_parent_record(register PARENT_RECORD *old, register PARENT_RECORD *new);
extern int gc_suspension_queue(register CELL *oldhook, register CELL *newhook);
extern int gc_suspension_record(register SUSPENSION_RECORD *old, register SUSPENSION_RECORD *new);
extern int gc_io_table(void);
extern int gc_timer_table(void);

/* gc_dead.c */
extern int deadlock_check_and_report(void);
extern int terminate_shoen_by_gc(void);

/* goal.c */
extern int enqueue_with_priority(GOAL_RECORD *grec);
extern int enqueue_head_with_priority(GOAL_RECORD *grec);
extern int initialize_priority_queue(void);
extern int enqueue(GOAL_RECORD *grec);
extern int enqueue_head(GOAL_RECORD *grec);
extern int enqueue_tail(GOAL_RECORD *grec);
extern int enqueue_tail_with_priority(GOAL_RECORD *grec);
extern int dequeue(void);
extern int popup_suspension_stack(GOAL_RECORD *goal);
extern int single_wait_suspend(GOAL_RECORD *goal, CELL *ref);
extern int body_builtin_suspend(OBJ *code, CELL *waitref, unsigned int argio, ...);
extern int body_builtin_swap(OBJ *code, unsigned int argio, ...);
extern int wakeup_goals_v(CELL *cc, int type, int32_t value, MRB mrb);
/* MODERN: callers pass an integer or a pointer as the new value (cell.h SetAll). */
#define wakeup_goals(CC, T, V, M) wakeup_goals_v((CC), (T), CellValue(V), (M))
extern int move_suspension_queue(register CELL *from, register CELL *to);

/* instr.c */
extern int initialize_instruction_table(void);

/* invassm.c */
extern int inverse_assemble_one(OBJ *p, OBJ *top, CHAR *s);

/* io.c */
extern int initialize_io(void);
extern int io_ctrl_when_exit(void);
extern int io_ctrl_when_stop(void);
extern int io_ctrl_when_resume(void);
extern int read_console(CHAR *prompt, CHAR *line, int n);
extern int getc_window(register IO_BACKET *it);
extern int ungetc_window(register int chr, register IO_BACKET *it);
extern int request_keyboard(register IO_BACKET *it);
extern int request_console(void);
extern int do_keyboard_interrupt(void);
extern int is_there_goal_waiting_for_keyboard_input(void);
extern int is_there_goal_waiting_for_keyboard_interrupt(void);

/* iosub.c */
extern int create_window(CELL *name, CELL *intr, int *ioid);
extern int remove_window(int ioid);
extern int remove_all_windows(void);
extern int show_window(int ioid);
extern int hide_window(int ioid);
extern int create_file(int *ioid);
extern int open_file(int ioid, CELL *name, int mode);
extern int close_file(int ioid);
extern int remove_file(int ioid);
extern int write_char(int ioid, int chr);
extern int write_line(int ioid, CELL *line);
extern int write_buffer(int ioid, CELL *buf);
extern int write_term(int ioid, CELL *term, int len, int dep);
extern int abort_read_command(int ioid);
extern int read_char(int ioid, int *chr);
extern int read_line(int ioid, CELL *line);
extern int read_buffer(int ioid, int max, CELL *buf);
extern int read_token(int ioid, register CELL *head, CELL *tail, int *vars);

/* memory.c */
extern int initialize_heap(unsigned int size);
extern int switch_heap(void);
extern CELL *alloc_cells_to_free_list(register unsigned int size, register unsigned int num);
extern int mrbgc_statistics_collect_vector(int n);
extern int mrbgc_statistics_collect_vector_fail(int n);
extern int mrbgc_statistics_collect_value(int n);
extern int mrbgc_statistics_collect_in_builtin(int n);
extern int mrbgc_statistics_reuse_vector(int n);
extern int mrbgc_statistics_reuse_vector_fail(int n);
extern int mrbgc_statistics_reuse_in_builtin(int n);
extern int alloc_suspension_record(register unsigned int num);
extern int alloc_goal_record8(register unsigned int num);
extern int alloc_goal_record16(register unsigned int num);
extern int alloc_goal_record32(register unsigned int num);
extern int alloc_parent_record(register unsigned int num);
extern unsigned int count_suspension_record_in_free_list(void);
extern unsigned int count_goal_record8_in_free_list(void);
extern unsigned int count_goal_record16_in_free_list(void);
extern unsigned int count_goal_record32_in_free_list(void);
extern unsigned int count_parent_record_in_free_list(void);
extern int initialize_code(unsigned int size);
extern int initialize_code2(void);
extern int switch_code(void);
extern unsigned char *t1_alloc(unsigned int size);
extern int t1_free(void);
extern unsigned char *t2_alloc(unsigned int size);
extern int t2_free(void);
extern unsigned char *t3_alloc(unsigned int size);
extern int t3_free(void);
extern unsigned char *t4_alloc(unsigned int size);
extern int t4_free(void);

/* module.c */
extern int lookup_module(register unsigned int id, MODULE_ENTRY **mod);
extern int enter_module(unsigned int id, OBJ *addr, int size, MODULE_ENTRY **indp);
extern int remove_module(register unsigned int id);
extern OBJ *find_predicate(MODULE_ENTRY *mod, unsigned int pid);
extern int function_to_mod_pred_arity(OBJ *code, unsigned int *mod, unsigned int *pred, unsigned int *arity);
extern int rehash_predicate_table(PREDICATE_ENTRY *pt, PREDICATE_ENTRY **pft, PREDICATE_ENTRY **fpt, int pn, int ppn);
extern int renumber_atoms_in_pred_and_const_table(PREDICATE_ENTRY *pt, register unsigned int pn, register CELL *ct, register unsigned int cn, unsigned short *at);
extern int set_module_trace_flag(unsigned int module, int flag);
extern int get_module_trace_flag(unsigned int module, int *flag);
extern int set_predicate_spy_flag(unsigned int module, unsigned int predicate, int arity, int flag);
extern int get_predicate_spy_flag(unsigned int module, unsigned int predicate, int arity, int *flag);
extern int get_public_predicates(unsigned int module, CELL *predicates);
extern int get_spied_predicates(unsigned int module, CELL *predicates);
extern int reset_module_profile_info(unsigned int module);
extern int get_module_profile_info(int module, register CELL *info);
extern int load_from_sav_or_asm_file(CHAR *name, MODULE_ENTRY **mod_table);
extern int load_from_asm_file(CHAR *name, MODULE_ENTRY **mod_table);
extern int save_to_sav_file(CHAR *name, MODULE_ENTRY *mod_table);

/* mrbgc.c */
extern int collect_value(CELL *c, int d);
extern int detect_deadlock_by_collect_value(CELL *c, int d);
extern int detect_deadlock_in_suspension(int type, GOAL_RECORD *goal, CELL *c);
extern int detect_deadlock_in_unification1(CELL *x);
extern int detect_deadlock_in_unification2(CELL *x, CELL *y);

/* native.c */
extern int load_and_link_native_code_module(CHAR *fname, MODULE_ENTRY **mod_table);

/* option.c */
extern int read_option(int argc, CHAR **argv);

/* passive.c */
extern int passive_unify(register CELL *x, MRB mrbx, register CELL *y, MRB mrby, int depth);
extern int is_ground(register CELL *x, MRB mrb, int depth);

/* path.c */
extern CHAR *expand_path_name(CHAR *name, CHAR *buffer);

/* pdss.c */
extern int stop_pdss(void);
extern int abort_pdss(int sig);
extern int exit_pdss(int code);
extern int print_instr_counter(void);
extern int timeit(int (* routine)());

/* pdssinv.c */
extern int invasm_module(OBJ *cp);
extern OBJ *invasm_predicate(OBJ *cp, OBJ *top);
extern int invasm_constant(CELL *p, CELL *bottom, CELL *top);

/* print.c */
extern int initialize_print_routine(void);
extern int set_print_file(FILE *ff);
extern int set_print_var_mode(int mode);
extern int get_print_var_mode(void);
extern int set_print_deadlock(int f);
extern int print_term(CELL *cc, int len, int depth);
extern int print_term2(CELL *cc, int len, int depth);
extern int fprint_term(FILE *ff, CELL *cc, int len, int depth);
extern int print_string(CELL *c);
extern int fprint_string(register FILE *f, register CELL *c);
extern CELL *lookup_var(CHAR *name);

/* saveload.c */
extern int save_module(FILE *file, MODULE_ENTRY *module);
extern int load_module(FILE *fp, MODULE_ENTRY **module);

/* shoen.c */
extern int initialize_shoen_tree(OBJ *boot_code);
extern PARENT_RECORD *create_shoen(CELL *code, CELL *argv, unsigned int pmin, unsigned int pmax, unsigned int tag, CELL *report);
extern int start_shoen(PARENT_RECORD *shoen, int kind);
extern int stop_shoen(PARENT_RECORD *shoen, int kind);
extern int abort_shoen(PARENT_RECORD *shoen);
extern int remove_shoen(PARENT_RECORD *shoen);
extern int terminate_shoen(void);
extern int shoen_statistics(PARENT_RECORD *shoen);
extern int shoen_add_resource(PARENT_RECORD *shoen, int more);
extern int resource_limit(PARENT_RECORD *p, int level);
extern PARENT_RECORD *search_parent_tag(PARENT_RECORD *prec, unsigned int tag);
extern int unify_exception_with_report_stream(PARENT_RECORD *prec, CELL *mesg, unsigned int tag);
extern int unify_exception_with_parent_report_stream(PARENT_RECORD *prec, CELL *mesg);
extern int unify_message_with_parent_report_stream(PARENT_RECORD *prec, CELL *mesg);
extern int inspect_shoen_tree(void);

/* string.c */
extern int get_string_type(CELL *string, int *length, int *width);
extern int new_string(int length, int width, CELL *string);
extern int copy_string(CELL *string, CELL *newstr);
extern int get_string_element(CELL *string, int position, int *element);
extern int set_string_element(CELL *string, int position, int element);
extern int get_substring(CELL *string, int position, int length, CELL *substr);
extern int set_substring(CELL *string, int position, CELL *substr);
extern int append_string(CELL *string1, CELL *string2, CELL *newstr);
extern int string_and(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2);
extern int string_or(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2);
extern int string_exclusive_or(CELL *string1, CELL *string2, CELL *newstr, CELL *newstr2);
extern int string_complement(CELL *string, CELL *newstr);
extern int atom_to_string(unsigned int atom, CELL *string);
extern int string_to_atom(CELL *string, unsigned int *atom);
extern int get_print_image(CELL *atomic, int mode, int left, CELL *string, int *sleng, int *tail);
extern CELL *convert_to_kl1_string(register CHAR *string);
extern CELL *convert_to_kl1_string2(register CHAR *string, register int len);
extern CHAR *convert_to_c_string(CELL *string, CHAR *buffer, int maxlen);

/* timer.c */
extern int initialize_timer(void);
extern int timer_wakeup_goal(void);
extern int is_there_goal_waiting_for_timer(void);
extern int set_timer_on_after(int count, CELL *var);
extern int set_timer_on_at(int count, CELL *var);
extern int get_time_count(void);

/* tracer.c */
extern int initialize_tracer(void);
extern int set_trace_status(int status);
extern int trace_call_switch(int status);
extern int trace_susp_switch(int status);
extern int trace_resu_switch(int status);
extern int trace_fail_switch(int status);
extern int trace_swap_switch(int status);
extern int trace_interrupt(void);
extern int trace(OBJ *code, int an, CELL *as, int mode, GOAL_RECORD *grec, PARENT_RECORD *prec);
extern DCODE dc_debug_monitor_stream(void);
extern int blt_b_debug_monitor_stream(CELL *x, CELL *name, CELL *count);
extern int write_goal_record(GOAL_RECORD *goal);
extern int write_goal(OBJ *code, int an, CELL *as, PARENT_RECORD *prec, int pl, int pd);
extern int display_suspended_goals(CELL *mmm);

/* unify.c */
extern GOAL_RECORD *make_unify_goal_for_merger(TYPE type1, CELL *val1, MRB mrb1, TYPE type2, CELL *val2, MRB mrb2, MERGER_RECORD *merger);
extern int active_unify(CELL *regX, CELL *regY);
extern int active_unify_with_atom(CELL *reg, unsigned int atom);
extern int active_unify_with_nil(CELL *reg);
extern int active_unify_with_integer(CELL *reg, int inte);
extern int active_unify_with_float(CELL *reg, int flot);
extern int active_unify_with_list(CELL *reg, CELL *list);
extern int active_unify_with_vector(CELL *reg, CELL *vct);
extern int active_unify_with_string(CELL *reg, register CELL *str);
extern int active_unify_with_nue(CELL *reg, CELL *nue);
extern int active_unify_with_shoen(CELL *reg, PARENT_RECORD *shoen);
extern int active_unify_with_undef(CELL *reg, CELL *undef, MRB mrb);
extern int active_unify_with_hook(CELL *reg, CELL *hook, MRB mrb);
extern int active_unify_with_mhook(CELL *reg, CELL *mhook, MRB mrb);
extern int active_unify_with_stream(CELL *reg, CELL *stream, MRB mrb);
extern int active_unify_stream_atom(CELL *strm, MRB mrb, int atom);
extern int active_unify_stream_nil(CELL *strm, MRB mrb);
extern int active_unify_stream_integer(CELL *strm, MRB mrb, int inte);
extern int active_unify_stream_float(CELL *strm, MRB mrb, int flot);
extern int active_unify_stream_list(CELL *strm, MRB mrb, CELL *list);
extern int active_unify_stream_vector(CELL *strm, MRB mrb, CELL *vct);
extern int active_unify_stream_string(CELL *strm, MRB mrb, CELL *str);
extern int active_unify_stream_nue(CELL *strm, MRB mrb, CELL *nue);
extern int active_unify_stream_shoen(CELL *strm, MRB mrb, PARENT_RECORD *shoen);
extern int active_unify_stream_hook(CELL *strm, MRB mrbst, CELL *hook, MRB mrbhk);
extern int active_unify_stream_stream(CELL *st1, CELL *st2);
extern int make_unify_list_list_goal_and_enqueue(CELL *x, CELL *y);
extern int make_unify_vector_vector_goal_and_enqueue(CELL *x, CELL *y);
extern DCODE dc_unify(void);
extern DCODE dc_unify_list_list(void);
extern DCODE dc_unify_list_list2(void);
extern DCODE dc_unify_vector_vector(void);
extern DCODE dc_unify_vector_vector2(void);
extern int illegal_data_type_in_active_unify(CELL *x);
