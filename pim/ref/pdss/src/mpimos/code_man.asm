mpimos_code_manager:
	module		mpimos_code_manager
	entry		create,3,create_3_0
	entry		request,3,request_3_0
	entry		get_command_stream,1,get_command_stream_1_0
	entry		os_get_command_stream,3,os_get_command_stream_3_0
	module_entry		mpimos_code_manager
	predicate		create,3
create_3_0:
	b_merge		4,5
	create_goal		4
	set_value		1,5
	set_values_inc		2,2,2
	set_variable		4,2
	enqueue_goal		4,do_4_0
	create_goal		2
	set_value		1,1
	set_value		2,4
	enqueue_goal		2,do0_2_0
	put_value		1,2
	put_integer		2,32
	execute_external		mpimos_module_pool,create,2
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_code_manager
	predicate		do0,2
do0_2_0:
	try_me_else		do0_2_1
	list		1
	read_car		1,3
	vector		3
	jump_on_arity		3,4,do0_2_1
	table_entry		do0_2_1
	table_entry		do0_2_1
	table_entry		do0_2_4
	table_entry		do0_2_5
do0_2_4:
	read_cdr		1,4
	read_element		3,0,5
	wait_atom		5,get_command_stream
	read_element		3,1,5
	collect_list		1
	put_reused_vector		1,3
	write_element_value		1,0,5
	write_element_variable		1,1,3
	get_vector_value		2,1
	put_values_dec		1,4,2
	execute		2,do0_2_0
do0_2_5:
	read_cdr		1,4
	read_element		3,0,5
	wait_atom		5,get_command_stream
	read_elements_inc		3,1,5,2
	collect_list		1
	collect_vector		3
	put_vector		7,2
	write_element_variable		7,0,3
	write_element_variable		7,1,1
	get_vector_value		2,7
	create_goal		2
	set_value		1,4
	set_value		2,1
	enqueue_goal		2,do0_2_0
	put_value		1,5
	put_value		2,3
	put_value		3,6
	execute		3,valve_3_0
do0_2_1:
	otherwise		do0_2_0
	try_me_else		do0_2_9
	jump_on_non_list_var_var		1,do0_2_11,3,4
	get_reused_list_val_var		2,1,1,3,3
	put_values_dec		1,4,2
	execute		2,do0_2_0
do0_2_11:
	check_nil		1,do0_2_9
	get_nil		2
	proceed
do0_2_9:
	suspend		do0_2_0
	module_entry		mpimos_code_manager
	predicate		do,4
do_4_0:
	try_me_else		do_4_1
	list		1
	read_car		1,5
	vector		5
	jump_on_arity		5,5,do_4_1
	table_entry		do_4_1
	table_entry		do_4_1
	table_entry		do_4_4
	table_entry		do_4_5
	table_entry		do_4_6
do_4_4:
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,get_all_modules
	read_element		5,1,7
	put_reused_func		5,5,modules
	write_element_value		5,1,7
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,6
	put_value		4,5
	execute		4,do_4_0
do_4_5:
	read_element		5,0,6
	atom		6
	hash_on_atom		6,4,do_4_1
	bucket_entry_a		get_public_predicates,do_4_8
	bucket_entry_a		get_unsaved_modules,do_4_9
	bucket_entry_a		remove_module,do_4_10
	bucket_entry_a		save_all,do_4_11
do_4_8:
	read_cdr		1,7
	read_elements_inc		5,1,8,2
	put_reused_func		5,5,get_public_predicates
	write_elements_inc		5,1,8,2
	get_reused_list_val_var		2,1,1,5,5
	put_value		1,7
	put_value		2,5
	execute		4,do_4_0
do_4_9:
	read_cdr		1,7
	read_elements_inc		5,1,8,2
	put_reused_func		5,5,un_saved_modules
	write_elements_inc		5,1,8,2
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,7
	put_value		4,5
	execute		4,do_4_0
do_4_10:
	read_cdr		1,7
	read_elements_inc		5,1,8,2
	put_reused_func		5,5,remove_module
	write_element_marked_value		5,1,8
	write_element_value		5,2,9
	get_reused_list_val_var		2,1,1,5,5
	put_func		1,2,delete
	write_element_value		1,1,8
	get_list_val_var		4,2,1,6
	put_value		1,7
	put_value		2,5
	put_value		4,6
	execute		4,do_4_0
do_4_11:
	read_cdr		1,7
	read_elements_inc		5,1,8,2
	collect_vector		5
	put_func		5,5,save_all
	write_element_value		5,1,2
	write_element_variable		5,2,2
	write_elements_inc		5,3,8,2
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,7
	put_value		4,5
	execute		4,do_4_0
do_4_6:
	read_element		5,0,6
	atom		6
	branch_on_atom		6,3,do_4_1
	bucket_entry_a		auto_load_module,do_4_13
	bucket_entry_a		auto_save_module,do_4_14
	bucket_entry_a		load_module,do_4_15
do_4_13:
	read_cdr		1,7
	read_elements_inc		5,1,8,3
	collect_vector		5
	put_func		5,6,load
	write_elements_inc		5,1,9,2
	write_element_value		5,3,2
	write_element_variable		5,4,2
	write_element_value		5,5,8
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,7
	put_value		4,5
	execute		4,do_4_0
do_4_14:
	read_cdr		1,7
	read_elements_inc		5,1,8,3
	collect_vector		5
	put_func		5,6,save
	write_elements_inc		5,1,9,2
	write_element_value		5,3,2
	write_element_variable		5,4,2
	write_element_value		5,5,8
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,7
	put_value		4,5
	execute		4,do_4_0
do_4_15:
	read_cdr		1,7
	read_elements_inc		5,1,8,3
	put_values_inc		12,3,2
	put_reused_func		3,5,load_module
	write_element_variable		3,1,4
	write_element_marked_value		3,2,9
	write_element_variable		3,3,11
	get_reused_list_val_var		2,1,1,3,3
	put_value		1,7
	put_value		2,3
	put_value		3,8
	put_values_inc		5,9,5
	execute		9,do_wait_load_9_0
do_4_1:
	otherwise		do_4_0
	try_me_else		do_4_23
	jump_on_non_list_var_var		1,do_4_25,5,6
	get_reused_list_val_var		2,1,1,5,5
	put_values_dec		1,6,2
	execute		4,do_4_0
do_4_25:
	check_nil		1,do_4_23
	get_nil		2
	get_nil		3
	get_nil		4
	proceed
do_4_23:
	suspend		do_4_0
	module_entry		mpimos_code_manager
	predicate		do_wait_load,9
do_wait_load_9_0:
	try_me_else		do_wait_load_9_1
	wait_atom		7,success
	collect_value		5
	get_atom		6,success
	put_marked_value		3,3
	get_value		3,4
	put_structured_constant		4,'$SCNST_0'
	put_func		5,3,up_date
	write_elements_inc		5,1,3,2
	get_list_val_var		9,3,5,4
	put_value		3,8
	execute		4,do_4_0
do_wait_load_9_1:
	otherwise		do_wait_load_9_0
	collect_value		5
	collect_value		4
	get_value		6,7
	get_nil		3
	put_values_inc		3,8,2
	execute		4,do_4_0
do_wait_load_9_6:
	suspend		do_wait_load_9_0
	module_entry		mpimos_code_manager
	predicate		valve,3
valve_3_0:
	try_me_else		valve_3_1
	jump_on_non_list_var_var		1,valve_3_3,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,valve_3_0
valve_3_3:
	check_nil		1,valve_3_1
	collect_value		3
	get_nil		2
	proceed
valve_3_1:
	try_me_else		valve_3_4
	wait_atom		3,die
	collect_value		1
	get_nil		2
	proceed
valve_3_4:
	suspend		valve_3_0
	module_entry		mpimos_code_manager
	predicate		get_command_stream,1
get_command_stream_1_0:
	put_integer		4,65536
	put_atom		5,code_manager
	put_func		2,2,get_command_stream
	write_element_variable		2,1,3
	b_raise		4,5,2
	put_value		2,3
	execute		2,monitor_2_0
get_command_stream_1_1:
	suspend		get_command_stream_1_0
	module_entry		mpimos_code_manager
	predicate		os_get_command_stream,3
os_get_command_stream_3_0:
	put_func		4,2,get_command_stream
	write_element_value		4,1,1
	put_func		1,3,:
	write_element_atom		1,1,code_manager
	write_element_value		1,2,4
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
os_get_command_stream_3_1:
	suspend		os_get_command_stream_3_0
	module_entry		mpimos_code_manager
	predicate		monitor,2
monitor_2_0:
	try_me_else		monitor_2_1
	jump_on_non_list		1,monitor_2_3
	read_car		1,3
	vector		3
	jump_on_arity		3,7,monitor_2_1
	table_entry		monitor_2_1
	table_entry		monitor_2_1
	table_entry		monitor_2_5
	table_entry		monitor_2_6
	table_entry		monitor_2_7
	table_entry		monitor_2_1
	table_entry		monitor_2_8
monitor_2_5:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,3,monitor_2_1
	bucket_entry_a		get_all_modules,monitor_2_10
	bucket_entry_a		get_unsaved_modules,monitor_2_11
	bucket_entry_a		save_all,monitor_2_12
monitor_2_10:
	read_cdr		1,5
	read_element		3,1,6
	put_reused_func		3,3,get_all_modules
	write_element_variable		3,1,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,6
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_11:
	read_cdr		1,5
	read_element		3,1,6
	put_reused_func		3,3,get_unsaved_modules
	write_element_variable		3,1,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,6
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_12:
	read_cdr		1,5
	read_element		3,1,6
	put_reused_func		3,3,save_all
	write_element_variable		3,1,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,6
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_6:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,4,monitor_2_1
	bucket_entry_a		auto_load_module,monitor_2_14
	bucket_entry_a		auto_save_module,monitor_2_15
	bucket_entry_a		get_public_predicates,monitor_2_16
	bucket_entry_a		remove_module,monitor_2_17
monitor_2_14:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	atom		6
	put_reused_func		3,3,auto_load_module
	write_element_value		3,1,6
	write_element_variable		3,2,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_15:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	atom		6
	put_reused_func		3,3,auto_save_module
	write_element_value		3,1,6
	write_element_variable		3,2,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_16:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	atom		6
	put_reused_func		3,3,get_public_predicates
	write_element_value		3,1,6
	write_element_variable		3,2,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_17:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	atom		6
	put_reused_func		3,3,remove_module
	write_element_value		3,1,6
	write_element_variable		3,2,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_7:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,5,monitor_2_1
	bucket_entry_a		get_module_status,monitor_2_19
	bucket_entry_a		get_spied_predicates,monitor_2_20
	bucket_entry_a		load_module,monitor_2_21
	bucket_entry_a		save_module,monitor_2_22
	bucket_entry_a		trace_module,monitor_2_23
monitor_2_19:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	atom		6
	put_reused_func		3,3,get_module_status
	write_element_value		3,1,6
	write_element_variable		3,2,6
	write_element_variable		3,3,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,protect_2_0
	create_goal		2
	set_values_inc		1,6,2
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_20:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	atom		6
	put_reused_func		3,3,get_spied_predicates
	write_element_value		3,1,6
	write_element_variable		3,2,6
	write_element_variable		3,3,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,protect_2_0
	create_goal		2
	set_values_inc		1,6,2
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_21:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	string		7
	g_string		7,9,10
	wait_integer		10,8
	put_reused_func		3,3,load_module
	write_element_variable		3,1,9
	write_element_value		3,2,7
	write_element_variable		3,3,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,protect_2_0
	create_goal		2
	set_value		1,9
	set_value		2,6
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_22:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	atom		6
	string		7
	g_string		7,9,10
	wait_integer		10,8
	put_reused_func		3,3,save_module
	write_elements_inc		3,1,6,2
	write_element_variable		3,3,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_23:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	atom		6
	atom		7
	put_reused_func		3,3,trace_module
	write_elements_inc		3,1,6,2
	write_element_variable		3,3,4
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,protect_2_0
	put_value		1,5
	put_value		2,3
	execute		2,monitor_2_0
monitor_2_8:
	read_cdr		1,4
	read_element		3,0,5
	wait_atom		5,spy_predicate
	read_elements_inc		3,1,5,5
	atom		5
	atom		6
	integer		7
	atom		8
	put_reused_func		3,3,spy_predicate
	write_elements_inc		3,1,5,4
	write_element_variable		3,5,5
	get_reused_list_val_var		2,1,1,3,3
	create_goal		2
	set_value		1,5
	set_value		2,9
	enqueue_goal		2,protect_2_0
	put_values_dec		1,4,2
	execute		2,monitor_2_0
monitor_2_3:
	check_nil		1,monitor_2_1
	get_nil		2
	proceed
monitor_2_1:
	suspend		monitor_2_0
	module_entry		mpimos_code_manager
	predicate		protect,2
protect_2_0:
	try_me_else		protect_2_1
	wait		1
	switch_on_type		1,protect_2_2,protect_2_3,protect_2_4,protect_2_5,protect_2_6,protect_2_1
protect_2_4:
	read_car		1,3
	read_cdr		1,4
	put_reused_list		6,1
	write_car_variable		6,5
	write_cdr_variable		6,1
	get_list_value		2,6
	create_goal		2
	set_value		1,4
	set_value		2,1
	enqueue_goal		2,protect_2_0
	put_value		1,3
	put_value		2,5
	execute		2,protect_2_0
protect_2_2:
	get_value		2,1
	proceed
protect_2_3:
	get_value		2,1
	proceed
protect_2_5:
	g_vector		1,3
	put_marked_value		4,3
	b_new_vector		4,4
	b_decrement		3,3
	put_value		5,3
	put_values_inc		3,4,2
	execute		4,protect_vector_4_0
protect_2_6:
	g_string		1,3,4
	get_value		2,1
	proceed
protect_2_1:
	suspend		protect_2_0
	module_entry		mpimos_code_manager
	predicate		protect_vector,4
protect_vector_4_0:
	try_me_else		protect_vector_4_1
	vector		1
	integer		4
	g_vector_element		1,4,5
	mark_element		1,4
	put_marked_value		6,4
	put_variable		8,7
	b_set_vector_element		3,6,3,8,6
	b_decrement		4,3
	create_goal		4
	set_values_inc		1,1,2
	set_value		3,6
	set_value		4,3
	enqueue_goal		4,protect_vector_4_0
	put_marked_value		1,5
	put_value		2,7
	execute		2,protect_2_0
protect_vector_4_1:
	try_me_else		protect_vector_4_4
	integer		4
	put_integer		5,0
	g_less_than		4,5
	collect_value		1
	get_value		2,3
	proceed
protect_vector_4_4:
	suspend		protect_vector_4_0
	module_entry		mpimos_code_manager
	predicate		request,3
request_3_0:
	try_me_else		request_3_1
	wait_vector		1,2
	read_element		1,0,4
	wait_atom		4,get_command_stream
	read_element		1,1,4
	collect_vector		1
	put_func		1,3,get_command_stream
	write_element_value		1,1,4
	write_element_value		1,2,2
	put_func		2,3,:
	write_element_atom		2,1,code_manager
	write_element_value		2,2,1
	put_list		1
	write_car_value		1,2
	write_cdr_nil		1
	get_list_value		3,1
	proceed
request_3_1:
	suspend		request_3_0
	begin_const_section		mpimos_code_manager
'$SCNST_0_1':
	define_atom		[]
	define_atom		[]
'$SCNST_0_0':
	define_atom		yes
	define_list		'$SCNST_0_1'
'$SCNST_0':
	define_list		'$SCNST_0_0'
