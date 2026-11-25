pdss_code_device:
	module		pdss_code_device
	entry		do,1,do_1_0
	module_entry		pdss_code_device
	predicate		do,1
do_1_0:
	put_atom		2,success
	execute		2,do_2_0
do_1_1:
	suspend		do_1_0
	module_entry		pdss_code_device
	predicate		do,2
do_2_0:
	try_me_else		do_2_1
	jump_on_non_list		1,do_2_3
	read_car		1,3
	vector		3
	jump_on_arity		3,7,do_2_1
	table_entry		do_2_1
	table_entry		do_2_1
	table_entry		do_2_1
	table_entry		do_2_5
	table_entry		do_2_6
	table_entry		do_2_1
	table_entry		do_2_7
do_2_5:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,3,do_2_1
	bucket_entry_a		backtrace,do_2_9
	bucket_entry_a		debug,do_2_10
	bucket_entry_a		remove_module,do_2_11
do_2_9:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_marked_value		2,7
	enqueue_goal		2,do_2_0
	put_values_inc		1,6,2
	execute		2,do_backtrace_2_0
do_2_10:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_marked_value		2,7
	enqueue_goal		2,do_2_0
	put_values_inc		1,6,2
	execute		2,do_debug_2_0
do_2_11:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	b_remove_module		6,1
	create_goal		2
	set_value		1,5
	set_marked_value		2,7
	enqueue_goal		2,do_2_0
	put_value		2,7
	execute		2,status_2_0
do_2_6:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,7,do_2_1
	bucket_entry_a		assemble_module,do_2_13
	bucket_entry_a		get_module_status,do_2_14
	bucket_entry_a		get_public_predicates,do_2_15
	bucket_entry_a		get_spied_predicates,do_2_16
	bucket_entry_a		load_module,do_2_17
	bucket_entry_a		save_module,do_2_18
	bucket_entry_a		trace_module,do_2_19
do_2_13:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	put_marked_value		1,7
	b_assemble_module		4,1,9
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_values_inc		1,6,3
	put_value		5,9
	execute		5,wait_assemble_module_5_0
do_2_14:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	b_get_module_status		6,1,2
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	create_goal		2
	set_value		1,2
	set_value		2,8
	enqueue_goal		2,status_2_0
	put_value		2,7
	execute		2,mode_2_0
do_2_15:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	b_get_public_predicates		6,2,1
	get_value		2,7
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_value		2,8
	execute		2,status_2_0
do_2_16:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	b_get_spied_predicates		6,2,1
	get_value		2,7
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_value		2,8
	execute		2,status_2_0
do_2_17:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	put_marked_value		1,7
	b_load_module		4,1,9
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_values_inc		1,6,3
	put_value		5,9
	execute		5,wait_load_module_5_0
do_2_18:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	b_save_module		6,7,1
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_value		2,8
	execute		2,status_2_0
do_2_19:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_marked_value		2,8
	enqueue_goal		2,do_2_0
	put_values_inc		1,6,3
	execute		3,do_trace_module_3_0
do_2_7:
	read_cdr		1,4
	read_element		3,0,5
	wait_atom		5,spy_predicate
	read_elements_inc		3,1,5,5
	wait		2
	collect_list		1
	collect_value		2
	collect_vector		3
	create_goal		2
	set_value		1,4
	set_marked_value		2,9
	enqueue_goal		2,do_2_0
	put_values_inc		1,5,5
	execute		5,do_spy_predicate_5_0
do_2_3:
	check_nil		1,do_2_1
	collect_value		2
	proceed
do_2_1:
	suspend		do_2_0
	module_entry		pdss_code_device
	predicate		wait_assemble_module,5
wait_assemble_module_5_0:
	try_me_else		wait_assemble_module_5_1
	wait_integer		5,7
	collect_value		4
	b_assemble_module		4,2,5
	put_values_inc		2,3,3
	execute		4,wait_assemble_module2_4_0
wait_assemble_module_5_1:
	otherwise		wait_assemble_module_5_0
	collect_value		2
	get_value		1,4
	put_value		1,5
	put_value		2,3
	execute		2,status_2_0
wait_assemble_module_5_6:
	suspend		wait_assemble_module_5_0
	module_entry		pdss_code_device
	predicate		wait_assemble_module2,4
wait_assemble_module2_4_0:
	try_me_else		wait_assemble_module2_4_1
	wait_integer		4,7
	get_value		1,3
	get_atom		2,memory_limit
	proceed
wait_assemble_module2_4_1:
	otherwise		wait_assemble_module2_4_0
	get_value		1,3
	put_value		1,4
	execute		2,status_2_0
wait_assemble_module2_4_6:
	suspend		wait_assemble_module2_4_0
	module_entry		pdss_code_device
	predicate		wait_load_module,5
wait_load_module_5_0:
	try_me_else		wait_load_module_5_1
	wait_integer		5,7
	collect_value		4
	b_load_module		4,2,5
	put_values_inc		2,3,3
	execute		4,wait_load_module2_4_0
wait_load_module_5_1:
	otherwise		wait_load_module_5_0
	collect_value		2
	get_value		1,4
	put_value		1,5
	put_value		2,3
	execute		2,status_2_0
wait_load_module_5_6:
	suspend		wait_load_module_5_0
	module_entry		pdss_code_device
	predicate		wait_load_module2,4
wait_load_module2_4_0:
	try_me_else		wait_load_module2_4_1
	wait_integer		4,7
	get_value		1,3
	get_atom		2,memory_limit
	proceed
wait_load_module2_4_1:
	otherwise		wait_load_module2_4_0
	get_value		1,3
	put_value		1,4
	execute		2,status_2_0
wait_load_module2_4_6:
	suspend		wait_load_module2_4_0
	module_entry		pdss_code_device
	predicate		do_debug,2
do_debug_2_0:
	try_me_else		do_debug_2_1
	atom		1
	branch_on_atom		1,2,do_debug_2_1
	bucket_entry_a		off,do_debug_2_3
	bucket_entry_a		on,do_debug_2_4
do_debug_2_3:
	put_integer		1,0
	g_set_trace_switch		1
	get_atom		2,success
	proceed
do_debug_2_4:
	put_integer		1,1
	g_set_trace_switch		1
	get_atom		2,success
	proceed
do_debug_2_1:
	otherwise		do_debug_2_0
	collect_value		1
	get_atom		2,undefined_mode
	proceed
do_debug_2_7:
	suspend		do_debug_2_0
	module_entry		pdss_code_device
	predicate		do_backtrace,2
do_backtrace_2_0:
	try_me_else		do_backtrace_2_1
	atom		1
	branch_on_atom		1,2,do_backtrace_2_1
	bucket_entry_a		off,do_backtrace_2_3
	bucket_entry_a		on,do_backtrace_2_4
do_backtrace_2_3:
	put_integer		1,0
	g_set_backtrace_switch		1
	get_atom		2,success
	proceed
do_backtrace_2_4:
	put_integer		1,1
	g_set_backtrace_switch		1
	get_atom		2,success
	proceed
do_backtrace_2_1:
	otherwise		do_backtrace_2_0
	collect_value		1
	get_atom		2,undefined_mode
	proceed
do_backtrace_2_7:
	suspend		do_backtrace_2_0
	module_entry		pdss_code_device
	predicate		do_trace_module,3
do_trace_module_3_0:
	try_me_else		do_trace_module_3_1
	atom		2
	branch_on_atom		2,2,do_trace_module_3_1
	bucket_entry_a		off,do_trace_module_3_3
	bucket_entry_a		on,do_trace_module_3_4
do_trace_module_3_3:
	put_integer		2,0
	b_trace_module		1,2,1
	put_value		2,3
	execute		2,status_2_0
do_trace_module_3_4:
	put_integer		2,1
	b_trace_module		1,2,1
	put_value		2,3
	execute		2,status_2_0
do_trace_module_3_1:
	otherwise		do_trace_module_3_0
	collect_value		2
	collect_value		1
	get_atom		3,undefined_mode
	proceed
do_trace_module_3_7:
	suspend		do_trace_module_3_0
	module_entry		pdss_code_device
	predicate		do_spy_predicate,5
do_spy_predicate_5_0:
	try_me_else		do_spy_predicate_5_1
	atom		4
	branch_on_atom		4,2,do_spy_predicate_5_1
	bucket_entry_a		off,do_spy_predicate_5_3
	bucket_entry_a		on,do_spy_predicate_5_4
do_spy_predicate_5_3:
	put_vector		4,3
	write_elements_inc		4,0,1,3
	put_integer		1,0
	b_spy_predicate		4,1,1
	put_value		2,5
	execute		2,status_2_0
do_spy_predicate_5_4:
	put_vector		4,3
	write_elements_inc		4,0,1,3
	put_integer		1,1
	b_spy_predicate		4,1,1
	put_value		2,5
	execute		2,status_2_0
do_spy_predicate_5_1:
	otherwise		do_spy_predicate_5_0
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		5,undefined_mode
	proceed
do_spy_predicate_5_7:
	suspend		do_spy_predicate_5_0
	module_entry		pdss_code_device
	predicate		status,2
status_2_0:
	try_me_else		status_2_1
	integer		1
	jump_on_integer		1,7,status_2_1
	table_entry		status_2_3
	table_entry		status_2_4
	table_entry		status_2_5
	table_entry		status_2_6
	table_entry		status_2_7
	table_entry		status_2_8
	table_entry		status_2_9
status_2_3:
	get_atom		2,success
	proceed
status_2_4:
	get_atom		2,module_not_found
	proceed
status_2_5:
	get_atom		2,predicate_not_found
	proceed
status_2_6:
	get_atom		2,module_protected
	proceed
status_2_7:
	get_atom		2,native_code_module
	proceed
status_2_8:
	get_atom		2,cannot_open_file
	proceed
status_2_9:
	get_atom		2,load_error
	proceed
status_2_1:
	suspend		status_2_0
	module_entry		pdss_code_device
	predicate		mode,2
mode_2_0:
	try_me_else		mode_2_1
	jump_on_non_atom		1,mode_2_3
	test_nil		1,mode_2_1
	get_nil		2
	proceed
mode_2_3:
	is_integer		1,mode_2_1
	jump_on_integer		1,2,mode_2_1
	table_entry		mode_2_4
	table_entry		mode_2_5
mode_2_4:
	get_atom		2,off
	proceed
mode_2_5:
	get_atom		2,on
	proceed
mode_2_1:
	suspend		mode_2_0
