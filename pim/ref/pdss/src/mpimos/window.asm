mpimos_window:
	module		mpimos_window
	entry		create,2,create_2_0
	entry		create,3,create_3_0
	entry		request,7,request_7_0
	entry		os_create,6,os_create_6_0
	module_entry		mpimos_window
	predicate		create,2
create_2_0:
	put_integer		4,65536
	put_atom		5,window
	put_func		3,3,create
	write_elements_inc		3,1,1,2
	b_raise		4,5,3
	put_integer		1,2
	b_consume_resource		1
	proceed
create_2_1:
	suspend		create_2_0
	module_entry		mpimos_window
	predicate		create,3
create_3_0:
	put_integer		5,65536
	put_atom		6,window
	put_func		4,4,create
	write_elements_inc		4,1,1,3
	b_raise		5,6,4
	put_integer		1,2
	b_consume_resource		1
	proceed
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_window
	predicate		request,7
request_7_0:
	try_me_else		request_7_1
	vector		1
	jump_on_arity		1,5,request_7_1
	table_entry		request_7_1
	table_entry		request_7_1
	table_entry		request_7_1
	table_entry		request_7_3
	table_entry		request_7_4
request_7_3:
	read_element		1,0,8
	wait_atom		8,create
	read_elements_inc		1,1,8,2
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_vector		10,2
	write_element_value		10,0,6
	write_element_value		10,1,2
	put_func		2,6,create
	write_element_value		2,1,10
	write_element_marked_value		2,2,9
	write_element_variable		2,3,6
	write_elements_inc		2,4,3,2
	put_reused_func		1,1,:
	write_element_atom		1,1,window_manager
	write_element_value		1,2,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		7,2
	put_integer		1,10
	b_consume_resource		1
	put_value		1,8
	put_value		2,5
	put_value		3,9
	put_atom		4,no_status
	put_value		5,6
	execute		5,create_monitor_5_0
request_7_4:
	read_element		1,0,8
	wait_atom		8,create
	read_elements_inc		1,1,8,3
	string		9
	g_string		9,11,12
	wait_integer		12,8
	collect_vector		1
	put_vector		1,2
	write_element_value		1,0,6
	write_element_value		1,1,2
	put_func		2,6,create
	write_element_value		2,1,1
	write_element_marked_value		2,2,9
	write_element_variable		2,3,6
	write_elements_inc		2,4,3,2
	put_func		1,3,:
	write_element_atom		1,1,window_manager
	write_element_value		1,2,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		7,2
	put_integer		1,10
	b_consume_resource		1
	put_func		4,2,status
	write_element_value		4,1,10
	put_value		1,8
	put_value		2,5
	put_value		3,9
	put_value		5,6
	execute		5,create_monitor_5_0
request_7_1:
	otherwise		request_7_0
	try_me_else		request_7_7
	vector		1
	jump_on_arity		1,5,request_7_7
	table_entry		request_7_7
	table_entry		request_7_7
	table_entry		request_7_7
	table_entry		request_7_9
	table_entry		request_7_10
request_7_9:
	read_element		1,0,8
	wait_atom		8,create
	read_elements_inc		1,1,8,2
	collect_value		6
	collect_value		4
	collect_value		3
	collect_value		2
	collect_vector		1
	get_nil		7
	get_nil		5
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,bad_window_name_type
	put_values_inc		2,8,2
	put_atom		4,no_status
	execute		4,create_error_4_0
request_7_10:
	read_element		1,0,8
	wait_atom		8,create
	read_elements_inc		1,1,8,3
	collect_value		6
	collect_value		4
	collect_value		3
	collect_value		2
	collect_vector		1
	get_nil		7
	get_nil		5
	put_integer		1,1
	b_consume_resource		1
	put_func		4,2,status
	write_element_value		4,1,10
	put_atom		1,bad_window_name_type
	put_values_inc		2,8,2
	execute		4,create_error_4_0
request_7_7:
	suspend		request_7_0
	module_entry		mpimos_window
	predicate		os_create,6
os_create_6_0:
	try_me_else		os_create_6_1
	string		2
	put_value		8,2
	g_string		8,7,9
	wait_integer		9,8
	put_func		2,6,create
	write_element_variable		2,1,9
	write_element_marked_value		2,2,8
	write_element_variable		2,3,7
	write_elements_inc		2,4,3,2
	put_func		3,3,:
	write_element_atom		3,1,window_manager
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	get_list_value		5,2
	put_integer		2,10
	b_consume_resource		2
	put_values_dec		2,9,2
	put_atom		4,no_status
	put_value		5,7
	execute		5,create_monitor_5_0
os_create_6_1:
	suspend		os_create_6_0
	module_entry		mpimos_window
	predicate		create_monitor,5
create_monitor_5_0:
	try_me_else		create_monitor_5_1
	atom		5
	branch_on_atom		5,2,create_monitor_5_1
	bucket_entry_a		'fep#abnormal',create_monitor_5_3
	bucket_entry_a		'fep#normal',create_monitor_5_4
create_monitor_5_3:
	put_value		5,1
	get_nil		2
	put_atom		1,cannot_create_window
	put_value		2,5
	execute		4,create_error_4_0
create_monitor_5_4:
	put_integer		5,2
	b_consume_resource		5
	b_merge		6,5
	get_value		6,1
	b_merge		6,1
	put_vector		10,3
	write_element_variable		10,0,8
	write_element_variable		10,1,9
	write_element_variable		10,2,7
	get_vector_value		6,10
	put_integer		6,512
	put_integer		10,8
	b_new_string		6,6,10
	create_goal		9
	set_value		1,5
	set_value		2,2
	set_value		3,9
	set_variable		4,5
	set_variable		5,9
	put_structured_constant		2,'$SCNST_0'
	put_func		10,6,status
	write_element_integer		10,1,10
	write_element_integer		10,2,10
	write_element_integer		10,3,512
	write_elements_inc		10,4,2,2
	set_value		6,10
	set_value		7,6
	set_integer		8,512
	set_integer		9,0
	enqueue_goal		9,monitor_9_0
	create_goal		1
	set_value		1,4
	enqueue_goal		1,create_success_1_0
	create_goal		2
	put_structured_constant		2,'$SCNST_1'
	put_list_val_val		3,2,9
	put_structured_constant		2,'$SCNST_2'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_3'
	put_list_val_val		3,2,4
	set_value		1,3
	set_value		2,8
	enqueue_goal_external		mpimos_unparser,create,2
	create_goal		2
	set_value		1,5
	set_value		2,7
	enqueue_goal_external		mpimos_parser,do,2
	execute_external		mpimos_operator_manipulator,create,1
create_monitor_5_1:
	suspend		create_monitor_5_0
	module_entry		mpimos_window
	predicate		create_success,1
create_success_1_0:
	try_me_else		create_success_1_1
	jump_on_non_atom		1,create_success_1_3
	test_atom		1,no_status,create_success_1_1
	proceed
create_success_1_3:
	check_vector		1,2,create_success_1_1
	read_element		1,0,2
	wait_atom		2,status
	read_element		1,1,2
	collect_vector		1
	get_atom		2,success
	proceed
create_success_1_1:
	suspend		create_success_1_0
	module_entry		mpimos_window
	predicate		create_error,4
create_error_4_0:
	try_me_else		create_error_4_1
	jump_on_non_atom		4,create_error_4_3
	test_atom		4,no_status,create_error_4_1
	create_goal		9
	set_value		1,2
	set_void		2
	set_void		3
	set_void		4
	set_void		5
	put_structured_constant		2,'$SCNST_4'
	put_func		4,6,status
	write_element_integer		4,1,10
	write_element_integer		4,2,10
	write_element_integer		4,3,512
	write_element_value		4,4,2
	write_element_marked_value		4,5,3
	set_value		6,4
	set_void		7
	set_integer		8,512
	set_integer		9,0
	enqueue_goal		9,closed_9_0
	create_goal		3
	set_atom		1,error
	set_variable		2,5
	put_func		2,2,putb
	write_element_variable		2,1,6
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_structured_constant		2,'$SCNST_5'
	put_list_val_val		7,2,4
	set_value		3,7
	enqueue_goal		3,raise_error_3_0
	create_goal		2
	set_value		1,1
	set_value		2,6
	enqueue_goal		2,message_2_0
	put_value		1,3
	put_value		2,5
	execute_external		mpimos_utility,freeze,2
create_error_4_3:
	check_vector		4,2,create_error_4_1
	read_element		4,0,5
	wait_atom		5,status
	read_element		4,1,5
	put_reused_func		4,4,error
	write_element_value		4,1,1
	get_vector_value		5,4
	put_structured_constant		1,'$SCNST_6'
	put_func		6,6,status
	write_element_integer		6,1,10
	write_element_integer		6,2,10
	write_element_integer		6,3,512
	write_element_value		6,4,1
	write_element_value		6,5,3
	put_value		1,2
	put_void		2
	put_void		3
	put_void		4
	put_void		5
	put_void		7
	put_integer		8,512
	put_integer		9,0
	execute		9,closed_9_0
create_error_4_1:
	suspend		create_error_4_0
	module_entry		mpimos_window
	predicate		monitor,9
monitor_9_0:
	try_me_else		monitor_9_1
	jump_on_non_list		1,monitor_9_3
	read_car		1,10
	jump_on_non_atom		10,monitor_9_5
	hash_on_atom		10,5,monitor_9_1
	bucket_entry_a		beep,monitor_9_6
	bucket_entry_a		clear,monitor_9_7
	bucket_entry_a		hide,monitor_9_8
	bucket_entry_a		nl,monitor_9_9
	bucket_entry_a		show,monitor_9_10
monitor_9_6:
	read_cdr		1,11
	collect_list		1
	put_value		1,11
	put_integer		10,7
	execute		10,set_char_10_0
monitor_9_7:
	read_cdr		1,11
	collect_list		1
	put_value		1,11
	put_integer		10,12
	execute		10,set_char_10_0
monitor_9_8:
	read_cdr		1,11
	put_value		13,2
	put_func		2,2,hide
	write_element_variable		2,1,12
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		11
	set_value		1,11
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_integer		9,0
	set_value		10,12
	set_void		11
	enqueue_goal		11,wait_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,13
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_9:
	read_cdr		1,11
	collect_list		1
	put_value		1,11
	put_integer		10,10
	execute		10,set_char_10_0
monitor_9_10:
	read_cdr		1,11
	put_value		13,2
	put_func		2,2,show
	write_element_variable		2,1,12
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		11
	set_value		1,11
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_integer		9,0
	set_value		10,12
	set_void		11
	enqueue_goal		11,wait_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,13
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_5:
	is_vector		10,monitor_9_1
	jump_on_arity		10,5,monitor_9_1
	table_entry		monitor_9_1
	table_entry		monitor_9_1
	table_entry		monitor_9_11
	table_entry		monitor_9_12
	table_entry		monitor_9_13
monitor_9_11:
	read_element		10,0,11
	atom		11
	hash_on_atom		11,20,monitor_9_1
	bucket_entry_a		buffer_length,monitor_9_15
	bucket_entry_a		change_op_pool,monitor_9_16
	bucket_entry_a		close,monitor_9_17
	bucket_entry_a		do,monitor_9_18
	bucket_entry_a		flush,monitor_9_19
	bucket_entry_a		getc,monitor_9_20
	bucket_entry_a		getl,monitor_9_21
	bucket_entry_a		gett,monitor_9_22
	bucket_entry_a		print_depth,monitor_9_23
	bucket_entry_a		print_length,monitor_9_24
	bucket_entry_a		print_var_mode,monitor_9_25
	bucket_entry_a		putb,monitor_9_26
	bucket_entry_a		putc,monitor_9_27
	bucket_entry_a		putet,monitor_9_28
	bucket_entry_a		putl,monitor_9_29
	bucket_entry_a		putt,monitor_9_30
	bucket_entry_a		puttq,monitor_9_31
	bucket_entry_a		remove_op,monitor_9_32
	bucket_entry_a		skip,monitor_9_33
	bucket_entry_a		tab,monitor_9_34
monitor_9_15:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_less_than		14,13
	collect_list		1
	collect_value		8
	collect_vector		10
	put_integer		1,3
	put_marked_value		8,13
	b_set_vector_element		6,1,1,8,6
	put_integer		1,8
	b_new_string		8,13,1
	put_integer		1,0
	b_substring		7,1,9,10,1
	put_value		1,12
	put_value		7,8
	put_value		8,13
	put_integer		9,0
	execute		10,set_string_10_0
monitor_9_16:
	read_cdr		1,12
	read_element		10,1,13
	collect_vector		10
	put_func		10,3,replace_operator_pool
	write_element_void		10,1
	write_element_value		10,2,13
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	execute		9,monitor_9_0
monitor_9_17:
	read_cdr		1,12
	read_element		10,1,13
	put_value		14,2
	put_reused_func		2,10,close
	write_element_variable		2,1,11
	put_reused_list_val_var		10,1,2,1
	put_integer		2,2
	b_consume_resource		2
	create_goal		11
	set_value		1,12
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_integer		9,0
	set_value		10,11
	set_value		11,13
	enqueue_goal		11,wait_close_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,14
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_18:
	read_element		10,1,12
	jump_on_non_list		12,monitor_9_36
	read_cdr		1,13
	read_car		12,11
	read_cdr		12,14
	collect_list		12
	collect_vector		10
	create_goal		9
	set_variable		1,10
	set_values_inc		2,2,8
	enqueue_goal		9,monitor_9_0
	put_reused_list_val_val		1,1,11,14
	put_value		2,10
	put_value		3,13
	execute		3,do_3_0
monitor_9_36:
	check_nil		12,monitor_9_1
	read_cdr		1,13
	collect_list		1
	collect_vector		10
	put_value		1,13
	execute		9,monitor_9_0
monitor_9_19:
	read_cdr		1,12
	read_element		10,1,13
	collect_list		1
	collect_vector		10
	put_value		11,2
	create_goal		11
	set_value		1,12
	set_variable		2,10
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_integer		9,0
	set_variable		10,6
	set_value		11,13
	enqueue_goal		11,wait_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,11
	put_value		5,10
	execute		6,flush_buffer_6_0
monitor_9_20:
	read_cdr		1,12
	read_element		10,1,13
	collect_vector		10
	put_value		15,2
	put_func		2,3,getc
	write_element_variable		2,1,14
	write_element_variable		2,2,11
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		11
	set_value		1,12
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_values_inc		9,13,2
	set_value		11,11
	enqueue_goal		11,wait_char_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,15
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_21:
	read_cdr		1,12
	read_element		10,1,13
	collect_vector		10
	put_value		15,2
	put_func		2,3,getl
	write_element_variable		2,1,14
	write_element_variable		2,2,11
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		11
	set_value		1,12
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_values_inc		9,13,2
	set_value		11,11
	enqueue_goal		11,wait_line_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,15
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_22:
	read_cdr		1,12
	read_element		10,1,13
	put_value		19,2
	put_integer		2,4
	b_vector_element		6,2,2,6
	put_func		11,4,gettkn
	write_element_variable		11,1,18
	write_element_variable		11,2,17
	write_element_variable		11,3,16
	put_reused_list_val_var		1,1,11,15
	put_func		11,3,putb
	write_element_value		11,1,2
	write_element_void		11,2
	put_list_val_val		14,11,1
	put_integer		1,6
	b_consume_resource		1
	create_goal		12
	set_value		1,12
	set_value		2,15
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	put_reused_func		1,10,gett
	write_element_value		1,1,13
	set_value		9,1
	set_value		10,18
	set_values_inc		11,16,2
	enqueue_goal		12,wait_token_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,19
	put_value		5,14
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_23:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_less_than		14,13
	put_reused_func		10,10,print_depth
	write_element_marked_value		10,1,13
	get_reused_list_val_var		5,1,1,10,10
	put_integer		1,2
	b_set_vector_element		6,1,1,13,6
	put_value		1,12
	put_value		5,10
	execute		9,monitor_9_0
monitor_9_24:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_less_than		14,13
	put_reused_func		10,10,print_length
	write_element_marked_value		10,1,13
	get_reused_list_val_var		5,1,1,10,10
	put_integer		1,1
	b_set_vector_element		6,1,1,13,6
	put_value		1,12
	put_value		5,10
	execute		9,monitor_9_0
monitor_9_25:
	read_cdr		1,12
	read_element		10,1,13
	atom		13
	put_reused_func		10,10,print_var_mode
	write_element_value		10,1,13
	get_reused_list_val_var		5,1,1,10,10
	put_value		1,12
	put_value		5,10
	execute		9,monitor_9_0
monitor_9_26:
	read_cdr		1,12
	read_element		10,1,13
	string		13
	g_string		13,14,15
	wait_integer		15,8
	collect_list		1
	collect_vector		10
	put_value		1,12
	put_value		10,13
	execute		10,set_string_10_0
monitor_9_27:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_not_less_than		13,14
	put_integer		14,255
	g_not_less_than		14,13
	collect_list		1
	collect_vector		10
	put_value		1,12
	put_value		10,13
	execute		10,set_char_10_0
monitor_9_28:
	read_cdr		1,12
	read_element		10,1,13
	wait		13
	collect_vector		10
	put_func		10,3,putet
	write_element_value		10,1,13
	write_element_variable		10,2,11
	get_reused_list_val_var		5,1,1,10,10
	put_value		1,12
	put_value		5,10
	put_value		10,11
	execute		10,set_string_list_10_0
monitor_9_29:
	read_cdr		1,12
	read_element		10,1,13
	string		13
	g_string		13,14,15
	wait_integer		15,8
	collect_vector		10
	put_reused_list		1,1
	write_car_atom		1,nl
	write_cdr_value		1,12
	put_value		10,13
	execute		10,set_string_10_0
monitor_9_30:
	read_cdr		1,12
	read_element		10,1,13
	wait		13
	collect_vector		10
	put_func		10,3,putt
	write_element_value		10,1,13
	write_element_variable		10,2,11
	get_reused_list_val_var		5,1,1,10,10
	put_value		1,12
	put_value		5,10
	put_value		10,11
	execute		10,set_string_list_10_0
monitor_9_31:
	read_cdr		1,12
	read_element		10,1,13
	wait		13
	collect_vector		10
	put_func		10,3,puttq
	write_element_value		10,1,13
	write_element_variable		10,2,11
	get_reused_list_val_var		5,1,1,10,10
	put_value		1,12
	put_value		5,10
	put_value		10,11
	execute		10,set_string_list_10_0
monitor_9_32:
	read_cdr		1,12
	read_element		10,1,13
	atom		13
	collect_vector		10
	put_func		10,3,remove_operator
	write_element_marked_value		10,1,13
	write_element_variable		10,2,11
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	put_value		10,11
	put_void		11
	put_void		12
	execute		13,wait_remove_op_13_0
monitor_9_33:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_not_less_than		13,14
	put_integer		14,255
	g_not_less_than		14,13
	collect_vector		10
	put_value		15,2
	put_func		2,3,getc
	write_element_variable		2,1,14
	write_element_variable		2,2,11
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		11
	set_value		1,12
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_values_inc		9,13,2
	set_value		11,11
	enqueue_goal		11,skip_char_11_0
	put_value		1,7
	put_value		2,9
	put_value		3,15
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_34:
	read_cdr		1,12
	read_element		10,1,13
	integer		13
	put_integer		14,0
	g_not_less_than		13,14
	put_integer		14,1000
	g_less_than		13,14
	collect_list		1
	collect_vector		10
	put_value		1,12
	put_value		10,13
	execute		10,tab_10_0
monitor_9_12:
	read_element		10,0,11
	atom		11
	hash_on_atom		11,7,monitor_9_1
	bucket_entry_a		getb,monitor_9_38
	bucket_entry_a		getft,monitor_9_39
	bucket_entry_a		gett,monitor_9_40
	bucket_entry_a		operator,monitor_9_41
	bucket_entry_a		prompt,monitor_9_42
	bucket_entry_a		putb,monitor_9_43
	bucket_entry_a		replace_op_pool,monitor_9_44
monitor_9_38:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	integer		14
	put_integer		15,0
	g_less_than		15,14
	collect_vector		10
	put_value		16,2
	put_func		2,4,getb
	write_element_variable		2,1,15
	write_element_marked_value		2,2,14
	write_element_variable		2,3,11
	put_reused_list_val_var		10,1,2,1
	put_integer		2,3
	b_consume_resource		2
	create_goal		12
	set_value		1,12
	set_value		2,1
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	set_value		9,13
	set_values_dec		10,15,2
	set_value		12,11
	enqueue_goal		12,wait_buffer_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,16
	put_value		5,10
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_39:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	put_value		19,2
	put_integer		2,4
	b_vector_element		6,2,2,6
	put_func		11,4,gettkn
	write_element_variable		11,1,18
	write_element_variable		11,2,17
	write_element_variable		11,3,16
	put_reused_list_val_var		1,1,11,15
	put_reused_func		10,10,putb
	write_element_value		10,1,2
	write_element_void		10,2
	put_list_val_val		11,10,1
	put_integer		1,6
	b_consume_resource		1
	create_goal		12
	set_value		1,12
	set_value		2,15
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	put_func		1,3,getft
	write_elements_inc		1,1,13,2
	set_value		9,1
	set_value		10,18
	set_values_inc		11,16,2
	enqueue_goal		12,wait_token_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,19
	put_value		5,11
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_40:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	put_value		19,2
	put_integer		2,4
	b_vector_element		6,2,2,6
	put_func		11,4,gettkn
	write_element_variable		11,1,18
	write_element_variable		11,2,17
	write_element_variable		11,3,16
	put_reused_list_val_var		1,1,11,15
	put_reused_func		10,10,putb
	write_element_value		10,1,2
	write_element_void		10,2
	put_list_val_val		11,10,1
	put_integer		1,6
	b_consume_resource		1
	create_goal		12
	set_value		1,12
	set_value		2,15
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	put_func		1,3,gett
	write_elements_inc		1,1,13,2
	set_value		9,1
	set_value		10,18
	set_values_inc		11,16,2
	enqueue_goal		12,wait_token_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,19
	put_value		5,11
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_41:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	atom		13
	put_reused_func		10,10,operator
	write_elements_inc		10,1,13,2
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	execute		9,monitor_9_0
monitor_9_42:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	string		14
	g_string		14,15,16
	wait_integer		16,8
	collect_list		1
	collect_vector		10
	put_integer		1,4
	b_set_vector_element		6,1,1,14,6
	get_value		1,13
	put_value		1,12
	execute		9,monitor_9_0
monitor_9_43:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	string		13
	g_string		13,15,16
	wait_integer		16,8
	integer		14
	put_integer		16,0
	g_not_less_than		14,16
	collect_list		1
	collect_vector		10
	create_goal		10
	set_value		1,12
	set_values_inc		2,2,8
	set_variable		10,4
	enqueue_goal		10,set_string_10_0
	put_value		1,13
	put_values_dec		2,15,2
	execute		4,get_buffer_4_0
monitor_9_44:
	read_cdr		1,12
	read_elements_inc		10,1,13,2
	put_reused_func		10,10,replace_operator_pool
	write_elements_inc		10,1,13,2
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	execute		9,monitor_9_0
monitor_9_13:
	read_element		10,0,11
	atom		11
	hash_on_atom		11,7,monitor_9_1
	bucket_entry_a		add_op,monitor_9_46
	bucket_entry_a		getet,monitor_9_47
	bucket_entry_a		getft,monitor_9_48
	bucket_entry_a		putet,monitor_9_49
	bucket_entry_a		putt,monitor_9_50
	bucket_entry_a		puttq,monitor_9_51
	bucket_entry_a		remove_op,monitor_9_52
monitor_9_46:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	integer		13
	put_integer		16,1
	g_not_less_than		13,16
	put_integer		16,1200
	g_not_less_than		16,13
	atom		14
	atom		15
	collect_vector		10
	put_func		10,5,add_operator
	write_element_marked_value		10,1,13
	write_element_marked_value		10,2,14
	write_element_marked_value		10,3,15
	write_element_variable		10,4,11
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	put_value		10,11
	put_values_inc		11,13,3
	execute		13,wait_add_op_13_0
monitor_9_47:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	put_value		20,2
	put_integer		2,4
	b_vector_element		6,2,2,6
	put_reused_func		10,10,gettkn
	write_element_variable		10,1,19
	write_element_variable		10,2,18
	write_element_variable		10,3,17
	put_reused_list_val_var		1,1,10,16
	put_func		10,3,putb
	write_element_value		10,1,2
	write_element_void		10,2
	put_list_val_val		11,10,1
	put_integer		1,6
	b_consume_resource		1
	create_goal		12
	set_value		1,12
	set_value		2,16
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	put_func		1,4,getet
	write_elements_inc		1,1,13,3
	set_value		9,1
	set_value		10,19
	set_values_inc		11,17,2
	enqueue_goal		12,wait_token_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,20
	put_value		5,11
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_48:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	put_value		20,2
	put_integer		2,4
	b_vector_element		6,2,2,6
	put_reused_func		10,10,gettkn
	write_element_variable		10,1,19
	write_element_variable		10,2,18
	write_element_variable		10,3,17
	put_reused_list_val_var		1,1,10,16
	put_func		10,3,putb
	write_element_value		10,1,2
	write_element_void		10,2
	put_list_val_val		11,10,1
	put_integer		1,6
	b_consume_resource		1
	create_goal		12
	set_value		1,12
	set_value		2,16
	set_values_inc		3,3,4
	set_variable		7,4
	set_value		8,8
	put_func		1,4,getft
	write_elements_inc		1,1,13,3
	set_value		9,1
	set_value		10,19
	set_values_inc		11,17,2
	enqueue_goal		12,wait_token_12_0
	put_value		1,7
	put_value		2,9
	put_value		3,20
	put_value		5,11
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_49:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	wait		13
	integer		14
	put_integer		16,0
	g_less_than		16,14
	integer		15
	put_integer		16,0
	g_less_than		16,15
	collect_vector		10
	put_integer		10,1
	b_vector_element		6,10,6,10
	put_integer		11,2
	b_vector_element		10,11,10,11
	put_func		16,2,print_depth
	write_element_value		16,1,10
	put_reused_list_val_var		1,1,16,16
	put_func		10,2,print_length
	write_element_value		10,1,6
	put_list_val_val		6,10,1
	put_func		1,3,putet
	write_element_value		1,1,13
	write_element_variable		1,2,13
	put_list_val_val		10,1,6
	put_func		1,2,print_depth
	write_element_value		1,1,15
	put_list_val_val		6,1,10
	put_func		1,2,print_length
	write_element_value		1,1,14
	put_list_val_val		10,1,6
	get_list_value		5,10
	put_value		1,12
	put_value		5,16
	put_value		6,11
	put_value		10,13
	execute		10,set_string_list_10_0
monitor_9_50:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	wait		13
	integer		14
	put_integer		16,0
	g_less_than		16,14
	integer		15
	put_integer		16,0
	g_less_than		16,15
	collect_vector		10
	put_integer		10,1
	b_vector_element		6,10,6,10
	put_integer		11,2
	b_vector_element		10,11,10,11
	put_func		16,2,print_depth
	write_element_value		16,1,10
	put_reused_list_val_var		1,1,16,16
	put_func		10,2,print_length
	write_element_value		10,1,6
	put_list_val_val		6,10,1
	put_func		1,3,putt
	write_element_value		1,1,13
	write_element_variable		1,2,13
	put_list_val_val		10,1,6
	put_func		1,2,print_depth
	write_element_value		1,1,15
	put_list_val_val		6,1,10
	put_func		1,2,print_length
	write_element_value		1,1,14
	put_list_val_val		10,1,6
	get_list_value		5,10
	put_value		1,12
	put_value		5,16
	put_value		6,11
	put_value		10,13
	execute		10,set_string_list_10_0
monitor_9_51:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	wait		13
	integer		14
	put_integer		16,0
	g_less_than		16,14
	integer		15
	put_integer		16,0
	g_less_than		16,15
	collect_vector		10
	put_integer		10,1
	b_vector_element		6,10,6,10
	put_integer		11,2
	b_vector_element		10,11,10,11
	put_func		16,2,print_depth
	write_element_value		16,1,10
	put_reused_list_val_var		1,1,16,16
	put_func		10,2,print_length
	write_element_value		10,1,6
	put_list_val_val		6,10,1
	put_func		1,3,puttq
	write_element_value		1,1,13
	write_element_variable		1,2,13
	put_list_val_val		10,1,6
	put_func		1,2,print_depth
	write_element_value		1,1,15
	put_list_val_val		6,1,10
	put_func		1,2,print_length
	write_element_value		1,1,14
	put_list_val_val		10,1,6
	get_list_value		5,10
	put_value		1,12
	put_value		5,16
	put_value		6,11
	put_value		10,13
	execute		10,set_string_list_10_0
monitor_9_52:
	read_cdr		1,12
	read_elements_inc		10,1,13,3
	integer		13
	put_integer		16,1
	g_not_less_than		13,16
	put_integer		16,1200
	g_not_less_than		16,13
	atom		14
	atom		15
	collect_vector		10
	put_func		10,5,remove_operator
	write_element_marked_value		10,1,13
	write_element_marked_value		10,2,14
	write_element_marked_value		10,3,15
	write_element_variable		10,4,11
	get_reused_list_val_var		3,1,1,10,10
	put_value		1,12
	put_value		3,10
	put_value		10,11
	put_values_inc		11,13,3
	execute		13,wait_remove_op_13_0
monitor_9_3:
	check_nil		1,monitor_9_1
	collect_value		8
	collect_value		6
	put_value		8,2
	put_func		1,2,close
	write_element_variable		1,1,2
	put_list		6
	write_car_value		6,1
	write_cdr_nil		6
	put_integer		1,2
	b_consume_resource		1
	get_nil		3
	get_nil		4
	get_nil		5
	create_goal		1
	set_value		1,2
	enqueue_goal		1,wait_1_0
	put_value		1,7
	put_values_dec		2,9,2
	put_void		4
	put_value		5,6
	put_void		6
	execute		6,flush_buffer_6_0
monitor_9_1:
	otherwise		monitor_9_0
	try_me_else		monitor_9_70
	wait_list_var_var		1,10,11
	collect_list		1
	create_goal		9
	set_value		1,11
	set_values_inc		2,2,4
	set_variable		6,5
	set_values_inc		7,7,3
	enqueue_goal		9,monitor_9_0
	put_atom		1,warning
	put_atom		2,illegal_command
	put_value		3,10
	put_value		4,6
	execute		5,command_error_5_0
monitor_9_70:
	otherwise		monitor_9_0
	put_value		10,1
	create_goal		9
	set_marked_value		1,10
	set_values_inc		2,2,4
	set_variable		6,5
	set_values_inc		7,7,3
	enqueue_goal		9,monitor_9_0
	put_atom		1,error
	put_atom		2,not_command_stream
	put_value		3,10
	put_value		4,6
	execute		5,command_error_5_0
monitor_9_74:
	suspend		monitor_9_0
	module_entry		mpimos_window
	predicate		closed,9
closed_9_0:
	try_me_else		closed_9_1
	jump_on_non_list_var_var		1,closed_9_3,10,11
	collect_list		1
	create_goal		9
	set_value		1,11
	set_values_inc		2,2,4
	set_variable		6,5
	set_values_inc		7,7,3
	enqueue_goal		9,closed_9_0
	put_atom		1,warning
	put_atom		2,window_not_open
	put_value		3,10
	put_value		4,6
	execute		5,command_error_5_0
closed_9_3:
	check_nil		1,closed_9_1
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	get_nil		2
	get_nil		3
	get_nil		4
	get_nil		5
	proceed
closed_9_1:
	suspend		closed_9_0
	module_entry		mpimos_window
	predicate		wait_close,11
wait_close_11_0:
	try_me_else		wait_close_11_1
	wait_atom		10,'fep#normal'
	get_atom		11,success
	execute		9,closed_9_0
wait_close_11_1:
	suspend		wait_close_11_0
	module_entry		mpimos_window
	predicate		flush_buffer,6
flush_buffer_6_0:
	try_me_else		flush_buffer_6_1
	integer		2
	test_integer		2,0,flush_buffer_6_3
	get_value		4,1
	get_value		5,3
	get_atom		6,'fep#normal'
	proceed
flush_buffer_6_3:
	put_integer		7,0
	g_less_than		7,2
	put_integer		7,0
	b_substring		1,7,2,1,2
	get_value		2,4
	put_func		2,3,putb
	write_element_value		2,1,1
	write_element_value		2,2,6
	put_list_val_val		1,2,5
	get_list_value		3,1
	put_integer		1,3
	b_consume_resource		1
	proceed
flush_buffer_6_1:
	suspend		flush_buffer_6_0
	module_entry		mpimos_window
	predicate		get_buffer,4
get_buffer_4_0:
	try_me_else		get_buffer_4_1
	integer		2
	integer		3
	try_me_else		get_buffer_4_4
	g_less_than		3,2
	put_integer		2,0
	b_substring		1,2,3,2,1
	get_value		2,4
	proceed
get_buffer_4_4:
	get_value		4,1
	proceed
get_buffer_4_1:
	suspend		get_buffer_4_0
	module_entry		mpimos_window
	predicate		wait,11
wait_11_0:
	try_me_else		wait_11_1
	wait_atom		10,'fep#normal'
	get_atom		11,done
	execute		9,monitor_9_0
wait_11_1:
	suspend		wait_11_0
	module_entry		mpimos_window
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait_atom		1,'fep#normal'
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_window
	predicate		wait_char,11
wait_char_11_0:
	try_me_else		wait_char_11_1
	integer		10
	wait_atom		11,'fep#normal'
	get_value		9,10
	put_integer		9,0
	execute		9,monitor_9_0
wait_char_11_1:
	try_me_else		wait_char_11_3
	atom		11
	branch_on_atom		11,2,wait_char_11_3
	bucket_entry_a		'fep#abort',wait_char_11_5
	bucket_entry_a		'fep#end_of_file',wait_char_11_6
wait_char_11_5:
	collect_value		10
	put_integer		10,14
	b_consume_resource		10
	put_func		10,2,getc
	write_element_value		10,1,9
	put_list_val_val		9,10,1
	put_value		1,9
	put_integer		9,0
	execute		9,monitor_9_0
wait_char_11_6:
	collect_value		10
	get_atom		9,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_char_11_3:
	suspend		wait_char_11_0
	module_entry		mpimos_window
	predicate		skip_char,11
skip_char_11_0:
	try_me_else		skip_char_11_1
	integer		9
	integer		10
	wait_atom		11,'fep#normal'
	try_me_else		skip_char_11_5
	g_equal		10,9
	put_integer		9,0
	execute		9,monitor_9_0
skip_char_11_5:
	put_func		10,3,getc
	write_element_variable		10,1,12
	write_element_variable		10,2,11
	get_list_val_var		2,13,10,10
	put_integer		2,3
	b_consume_resource		2
	put_value		2,10
	put_value		10,12
	execute		11,skip_char_11_0
skip_char_11_1:
	try_me_else		skip_char_11_6
	atom		11
	branch_on_atom		11,2,skip_char_11_6
	bucket_entry_a		'fep#abort',skip_char_11_8
	bucket_entry_a		'fep#end_of_file',skip_char_11_9
skip_char_11_8:
	collect_value		10
	put_integer		10,14
	b_consume_resource		10
	put_func		10,2,skip
	write_element_value		10,1,9
	put_list_val_val		9,10,1
	put_value		1,9
	put_integer		9,0
	execute		9,monitor_9_0
skip_char_11_9:
	collect_value		10
	collect_value		9
	put_integer		9,0
	execute		9,monitor_9_0
skip_char_11_6:
	suspend		skip_char_11_0
	module_entry		mpimos_window
	predicate		wait_line,11
wait_line_11_0:
	try_me_else		wait_line_11_1
	string		10
	wait_atom		11,'fep#normal'
	g_string		10,12,13
	wait_integer		13,8
	get_value		9,10
	put_integer		9,0
	execute		9,monitor_9_0
wait_line_11_1:
	try_me_else		wait_line_11_4
	atom		11
	branch_on_atom		11,2,wait_line_11_4
	bucket_entry_a		'fep#abort',wait_line_11_6
	bucket_entry_a		'fep#end_of_file',wait_line_11_7
wait_line_11_6:
	collect_value		10
	put_integer		10,14
	b_consume_resource		10
	put_func		10,2,getl
	write_element_value		10,1,9
	put_list_val_val		9,10,1
	put_value		1,9
	put_integer		9,0
	execute		9,monitor_9_0
wait_line_11_7:
	collect_value		10
	get_atom		9,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_line_11_4:
	suspend		wait_line_11_0
	module_entry		mpimos_window
	predicate		wait_buffer,12
wait_buffer_12_0:
	try_me_else		wait_buffer_12_1
	string		10
	wait_atom		12,'fep#normal'
	g_string		10,13,14
	wait_integer		14,8
	collect_value		11
	get_value		9,10
	put_integer		9,0
	execute		9,monitor_9_0
wait_buffer_12_1:
	try_me_else		wait_buffer_12_4
	atom		12
	branch_on_atom		12,2,wait_buffer_12_4
	bucket_entry_a		'fep#abort',wait_buffer_12_6
	bucket_entry_a		'fep#end_of_file',wait_buffer_12_7
wait_buffer_12_6:
	collect_value		10
	put_integer		10,14
	b_consume_resource		10
	put_func		10,3,getb
	write_element_value		10,1,9
	write_element_value		10,2,11
	put_list_val_val		9,10,1
	put_value		1,9
	put_integer		9,0
	execute		9,monitor_9_0
wait_buffer_12_7:
	collect_value		11
	collect_value		10
	get_atom		9,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_buffer_12_4:
	suspend		wait_buffer_12_0
	module_entry		mpimos_window
	predicate		wait_token,12
wait_token_12_0:
	try_me_else		wait_token_12_1
	vector		9
	jump_on_arity		9,5,wait_token_12_3
	table_entry		wait_token_12_3
	table_entry		wait_token_12_3
	table_entry		wait_token_12_4
	table_entry		wait_token_12_5
	table_entry		wait_token_12_6
wait_token_12_4:
	try_me_else		wait_token_12_3
	read_element		9,0,13
	wait_atom		13,gett
	read_element		9,1,13
	wait_atom		12,'fep#end_of_file'
	collect_value		11
	collect_value		10
	collect_vector		9
	get_atom		13,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_5:
	read_element		9,0,13
	try_me_else		wait_token_12_3
	atom		13
	branch_on_atom		13,2,wait_token_12_3
	bucket_entry_a		getft,wait_token_12_8
	bucket_entry_a		gett,wait_token_12_9
wait_token_12_8:
	read_elements_inc		9,1,14,2
	wait_atom		12,'fep#end_of_file'
	collect_value		11
	collect_value		10
	collect_vector		9
	get_atom		14,end_of_file
	get_integer		15,0
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_9:
	read_elements_inc		9,1,14,2
	wait_atom		12,'fep#end_of_file'
	collect_value		11
	collect_value		10
	collect_vector		9
	get_atom		14,end_of_file
	get_atom		15,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_6:
	read_element		9,0,13
	try_me_else		wait_token_12_3
	atom		13
	branch_on_atom		13,2,wait_token_12_3
	bucket_entry_a		getet,wait_token_12_11
	bucket_entry_a		getft,wait_token_12_12
wait_token_12_11:
	read_elements_inc		9,1,14,3
	wait_atom		12,'fep#end_of_file'
	collect_value		11
	collect_value		10
	collect_vector		9
	get_atom		14,end_of_file
	get_integer		15,0
	get_atom		16,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_12:
	read_elements_inc		9,1,14,3
	wait_atom		12,'fep#end_of_file'
	collect_value		11
	collect_value		10
	collect_vector		9
	get_atom		14,end_of_file
	get_integer		15,0
	get_atom		16,end_of_file
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_3:
	try_me_else		wait_token_12_1
	wait_atom		12,'fep#normal'
	try_me_else		wait_token_12_14
	put_integer		13,0
	g_vector_element		9,13,13
	put_atom		14,getet
	g_diff		13,14
	put_func		12,4,parse
	write_element_marked_value		12,1,10
	write_element_variable		12,2,14
	write_element_variable		12,3,13
	get_list_val_var		4,15,12,12
	put_value		4,12
	put_value		12,14
	execute		13,wait_parse_13_0
wait_token_12_14:
	try_me_else		wait_token_12_1
	put_integer		13,0
	g_vector_element		9,13,13
	wait_atom		13,getet
	put_func		12,4,parse_ex
	write_element_marked_value		12,1,10
	write_element_variable		12,2,14
	write_element_variable		12,3,13
	get_list_val_var		4,15,12,12
	put_value		4,12
	put_value		12,14
	execute		13,wait_parse_13_0
wait_token_12_1:
	try_me_else		wait_token_12_15
	wait_atom		12,'fep#abort'
	collect_value		11
	collect_value		10
	put_integer		10,14
	b_consume_resource		10
	put_list_val_val		10,9,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,10
	put_integer		9,0
	execute		9,monitor_9_0
wait_token_12_15:
	suspend		wait_token_12_0
	module_entry		mpimos_window
	predicate		wait_parse,13
wait_parse_13_0:
	try_me_else		wait_parse_13_1
	vector		9
	jump_on_arity		9,5,wait_parse_13_1
	table_entry		wait_parse_13_1
	table_entry		wait_parse_13_1
	table_entry		wait_parse_13_3
	table_entry		wait_parse_13_4
	table_entry		wait_parse_13_5
wait_parse_13_3:
	read_element		9,0,14
	wait_atom		14,gett
	read_element		9,1,15
	integer		11
	test_integer		11,0,wait_parse_13_8
	try_me_else		wait_parse_13_8
	wait_atom		13,parsed
	collect_value		10
	collect_vector		9
	get_value		15,12
	put_integer		9,0
	execute		9,monitor_9_0
wait_parse_13_8:
	try_me_else		wait_parse_13_1
	wait_atom		13,parsed
	put_integer		16,0
	g_less_than		16,11
	collect_value		10
	collect_vector		9
	create_goal		9
	set_values_inc		1,1,8
	set_integer		9,0
	enqueue_goal		9,monitor_9_0
	put_values_dec		1,12,2
	put_value		3,15
	execute_external		mpimos_utility,melt,3
wait_parse_13_4:
	read_element		9,0,14
	atom		14
	branch_on_atom		14,2,wait_parse_13_1
	bucket_entry_a		getft,wait_parse_13_10
	bucket_entry_a		gett,wait_parse_13_11
wait_parse_13_10:
	read_elements_inc		9,1,15,2
	wait_atom		13,parsed
	collect_value		10
	collect_vector		9
	get_value		15,12
	get_value		16,11
	put_integer		9,0
	execute		9,monitor_9_0
wait_parse_13_11:
	read_elements_inc		9,1,15,2
	integer		11
	test_integer		11,0,wait_parse_13_13
	try_me_else		wait_parse_13_13
	wait_atom		13,parsed
	collect_value		10
	collect_vector		9
	get_value		15,12
	get_atom		16,success
	put_integer		9,0
	execute		9,monitor_9_0
wait_parse_13_13:
	try_me_else		wait_parse_13_1
	wait_atom		13,parsed
	put_integer		17,0
	g_less_than		17,11
	collect_value		10
	collect_vector		9
	get_atom		16,success
	create_goal		9
	set_values_inc		1,1,8
	set_integer		9,0
	enqueue_goal		9,monitor_9_0
	put_values_dec		1,12,2
	put_value		3,15
	execute_external		mpimos_utility,melt,3
wait_parse_13_5:
	read_element		9,0,14
	atom		14
	branch_on_atom		14,2,wait_parse_13_1
	bucket_entry_a		getet,wait_parse_13_15
	bucket_entry_a		getft,wait_parse_13_16
wait_parse_13_15:
	read_elements_inc		9,1,15,3
	wait_atom		13,parsed
	collect_value		10
	collect_vector		9
	get_value		15,12
	get_value		16,11
	get_atom		17,success
	put_integer		9,0
	execute		9,monitor_9_0
wait_parse_13_16:
	read_elements_inc		9,1,15,3
	wait_atom		13,parsed
	collect_value		10
	collect_vector		9
	get_value		15,12
	get_value		16,11
	get_atom		17,success
	put_integer		9,0
	execute		9,monitor_9_0
wait_parse_13_1:
	try_me_else		wait_parse_13_17
	wait_vector		13,3
	read_element		13,0,14
	atom		14
	branch_on_atom		14,3,wait_parse_13_17
	bucket_entry_a		ambiguous,wait_parse_13_20
	bucket_entry_a		error,wait_parse_13_21
	bucket_entry_a		remained,wait_parse_13_22
wait_parse_13_20:
	read_elements_inc		13,1,15,2
	collect_value		16
	collect_value		12
	collect_vector		13
	put_values_inc		12,10,2
	put_atom		10,ambiguous
	put_value		11,15
	execute		13,parse_error_13_0
wait_parse_13_21:
	read_elements_inc		13,1,15,2
	collect_value		16
	collect_value		12
	collect_vector		13
	put_values_inc		12,10,2
	put_atom		10,syntax_error
	put_value		11,15
	execute		13,parse_error_13_0
wait_parse_13_22:
	read_elements_inc		13,1,15,2
	collect_value		15
	collect_value		12
	collect_vector		13
	put_variable		12,13
	put_variable		15,14
	b_subtract		12,15,12
	create_goal		13
	set_values_inc		1,1,9
	set_atom		10,syntax_error
	set_value		11,12
	set_marked_value		12,10
	set_value		13,11
	enqueue_goal		13,parse_error_13_0
	create_goal		2
	set_value		1,16
	set_value		2,14
	enqueue_goal		2,length_2_0
	put_value		1,10
	put_value		2,13
	execute		2,length_2_0
wait_parse_13_17:
	suspend		wait_parse_13_0
	module_entry		mpimos_window
	predicate		parse_error,13
parse_error_13_0:
	try_me_else		parse_error_13_1
	vector		9
	jump_on_arity		9,5,parse_error_13_1
	table_entry		parse_error_13_1
	table_entry		parse_error_13_1
	table_entry		parse_error_13_3
	table_entry		parse_error_13_4
	table_entry		parse_error_13_5
parse_error_13_3:
	read_element		9,0,14
	wait_atom		14,gett
	read_element		9,1,14
	collect_value		13
	put_list		13
	write_car_atom		13,nl
	write_cdr_variable		13,18
	put_structured_constant		15,'$SCNST_7'
	put_list_val_val		16,15,13
	put_reused_func		9,9,putb
	write_element_variable		9,1,17
	put_list_val_val		13,9,16
	put_structured_constant		9,'$SCNST_8'
	put_list_val_val		15,9,13
	create_goal		9
	put_func		9,2,gett
	write_element_value		9,1,14
	put_list_val_val		13,9,1
	put_func		1,2,do
	write_element_value		1,1,15
	put_list_val_val		9,1,13
	set_value		1,9
	set_values_inc		2,2,7
	set_integer		9,0
	enqueue_goal		9,monitor_9_0
	create_goal		3
	set_values_dec		1,12,2
	set_value		3,18
	enqueue_goal_external		mpimos_utility,report_tokens,3
	put_value		1,10
	put_value		2,17
	execute		2,message_2_0
parse_error_13_4:
	read_element		9,0,14
	atom		14
	branch_on_atom		14,2,parse_error_13_1
	bucket_entry_a		getft,parse_error_13_7
	bucket_entry_a		gett,parse_error_13_8
parse_error_13_7:
	read_elements_inc		9,1,15,2
	collect_value		13
	put_list		13
	write_car_atom		13,nl
	write_cdr_variable		13,19
	put_structured_constant		14,'$SCNST_9'
	put_list_val_val		17,14,13
	put_func		13,2,putb
	write_element_variable		13,1,18
	put_list_val_val		14,13,17
	put_structured_constant		13,'$SCNST_10'
	put_list_val_val		17,13,14
	create_goal		9
	put_reused_func		9,9,getft
	write_elements_inc		9,1,15,2
	put_list_val_val		13,9,1
	put_func		1,2,do
	write_element_value		1,1,17
	put_list_val_val		9,1,13
	set_value		1,9
	set_values_inc		2,2,7
	set_integer		9,0
	enqueue_goal		9,monitor_9_0
	create_goal		3
	set_values_dec		1,12,2
	set_value		3,19
	enqueue_goal_external		mpimos_utility,report_tokens,3
	put_value		1,10
	put_value		2,18
	execute		2,message_2_0
parse_error_13_8:
	read_elements_inc		9,1,15,2
	collect_value		13
	collect_vector		9
	get_value		15,12
	put_vector		9,2
	write_elements_inc		9,0,10,2
	get_vector_value		16,9
	put_integer		9,0
	execute		9,monitor_9_0
parse_error_13_5:
	read_element		9,0,14
	atom		14
	branch_on_atom		14,2,parse_error_13_1
	bucket_entry_a		getet,parse_error_13_10
	bucket_entry_a		getft,parse_error_13_11
parse_error_13_10:
	read_elements_inc		9,1,15,3
	collect_vector		9
	get_value		15,12
	get_value		16,13
	put_vector		9,2
	write_elements_inc		9,0,10,2
	get_vector_value		17,9
	put_integer		9,0
	execute		9,monitor_9_0
parse_error_13_11:
	read_elements_inc		9,1,15,3
	collect_vector		9
	get_value		15,12
	get_value		16,13
	put_vector		9,2
	write_elements_inc		9,0,10,2
	get_vector_value		17,9
	put_integer		9,0
	execute		9,monitor_9_0
parse_error_13_1:
	suspend		parse_error_13_0
	module_entry		mpimos_window
	predicate		set_char,10
set_char_10_0:
	try_me_else		set_char_10_1
	integer		8
	integer		9
	g_less_than		9,8
	put_marked_value		11,9
	b_set_string_element		7,11,10,7
	b_increment		9,9
	execute		9,monitor_9_0
set_char_10_1:
	try_me_else		set_char_10_3
	wait_value		8,9
	collect_value		9
	put_value		12,2
	put_variable		2,11
	put_integer		9,0
	b_set_string_element		2,9,10,2
	create_goal		11
	set_value		1,1
	set_variable		2,9
	set_values_inc		3,3,4
	set_value		7,2
	set_marked_value		8,8
	set_integer		9,1
	set_variable		10,6
	set_void		11
	enqueue_goal		11,wait_11_0
	put_values_inc		1,7,2
	put_values_dec		3,12,2
	put_value		5,9
	execute		6,flush_buffer_6_0
set_char_10_3:
	suspend		set_char_10_0
	module_entry		mpimos_window
	predicate		tab,10
tab_10_0:
	try_me_else		tab_10_1
	wait_integer		10,0
	execute		9,monitor_9_0
tab_10_1:
	otherwise		tab_10_0
	try_me_else		tab_10_6
	integer		8
	integer		9
	g_less_than		9,8
	put_marked_value		11,9
	put_integer		12,32
	b_set_string_element		7,11,12,7
	b_increment		9,9
	b_decrement		10,10
	execute		10,tab_10_0
tab_10_6:
	try_me_else		tab_10_8
	wait_value		8,9
	collect_value		9
	put_value		11,2
	create_goal		10
	set_value		1,1
	set_variable		2,9
	set_values_inc		3,3,4
	set_variable		7,4
	set_marked_value		8,8
	set_variable		9,6
	set_value		10,10
	enqueue_goal		10,wait_tab_write_10_0
	put_values_inc		1,7,2
	put_value		3,11
	put_value		5,9
	execute		6,flush_buffer_6_0
tab_10_8:
	suspend		tab_10_0
	module_entry		mpimos_window
	predicate		wait_tab_write,10
wait_tab_write_10_0:
	try_me_else		wait_tab_write_10_1
	wait_atom		9,'fep#normal'
	put_integer		9,0
	execute		10,tab_10_0
wait_tab_write_10_1:
	suspend		wait_tab_write_10_0
	module_entry		mpimos_window
	predicate		set_string,10
set_string_10_0:
	try_me_else		set_string_10_1
	string		10
	try_me_else		set_string_10_3
	g_string		10,11,12
	wait_integer		11,0
	wait_integer		12,8
	collect_value		10
	execute		9,monitor_9_0
set_string_10_3:
	try_me_else		set_string_10_1
	g_string		10,11,12
	wait_integer		12,8
	put_integer		12,0
	g_less_than		12,11
	put_marked_value		12,8
	put_marked_value		13,9
	b_subtract		12,13,12
	execute		12,set_string_12_0
set_string_10_1:
	suspend		set_string_10_0
	module_entry		mpimos_window
	predicate		set_string,12
set_string_12_0:
	try_me_else		set_string_12_1
	wait_integer		12,0
	collect_value		9
	put_value		12,2
	create_goal		11
	set_value		1,1
	set_variable		2,9
	set_values_inc		3,3,4
	set_variable		7,4
	set_marked_value		8,8
	set_variable		9,6
	set_values_inc		10,10,2
	enqueue_goal		11,wait_putb_11_0
	put_values_inc		1,7,2
	put_value		3,12
	put_value		5,9
	execute		6,flush_buffer_6_0
set_string_12_1:
	otherwise		set_string_12_0
	try_me_else		set_string_12_6
	integer		11
	integer		12
	try_me_else		set_string_12_9
	g_not_less_than		12,11
	put_marked_value		12,9
	b_set_substring		7,12,10,7
	b_add		9,11,9
	execute		9,monitor_9_0
set_string_12_9:
	put_value		13,2
	put_integer		2,0
	put_marked_value		14,12
	b_substring		10,2,14,2,10
	b_set_substring		7,9,2,2
	b_subtract		11,12,7
	put_marked_value		9,7
	b_substring		10,12,9,9,10
	create_goal		11
	set_value		1,1
	set_variable		2,10
	set_values_inc		3,3,4
	set_variable		7,4
	set_marked_value		8,8
	set_variable		9,6
	set_value		10,9
	set_value		11,7
	enqueue_goal		11,wait_putb_11_0
	put_value		1,2
	put_value		2,8
	put_value		3,13
	put_value		5,10
	execute		6,flush_buffer_6_0
set_string_12_6:
	suspend		set_string_12_0
	module_entry		mpimos_window
	predicate		wait_putb,11
wait_putb_11_0:
	try_me_else		wait_putb_11_1
	wait_atom		9,'fep#normal'
	put_value		12,8
	put_marked_value		8,12
	put_integer		9,0
	execute		12,set_string_12_0
wait_putb_11_1:
	suspend		wait_putb_11_0
	module_entry		mpimos_window
	predicate		set_string_list,10
set_string_list_10_0:
	try_me_else		set_string_list_10_1
	jump_on_non_list		10,set_string_list_10_3
	read_car		10,11
	string		11
	read_cdr		10,12
	try_me_else		set_string_list_10_5
	g_string		11,13,14
	wait_integer		13,0
	wait_integer		14,8
	collect_list		10
	collect_value		11
	put_value		10,12
	execute		10,set_string_list_10_0
set_string_list_10_5:
	try_me_else		set_string_list_10_1
	g_string		11,13,14
	wait_integer		14,8
	put_integer		14,0
	g_less_than		14,13
	collect_list		10
	put_marked_value		10,8
	put_marked_value		14,9
	b_subtract		10,14,10
	put_value		14,10
	put_value		10,12
	put_values_inc		12,13,2
	execute		13,set_string_list_13_0
set_string_list_10_3:
	check_nil		10,set_string_list_10_1
	execute		9,monitor_9_0
set_string_list_10_1:
	suspend		set_string_list_10_0
	module_entry		mpimos_window
	predicate		set_string_list,13
set_string_list_13_0:
	try_me_else		set_string_list_13_1
	wait_integer		13,0
	collect_value		9
	put_value		13,2
	create_goal		12
	set_value		1,1
	set_variable		2,9
	set_values_inc		3,3,4
	set_variable		7,4
	set_marked_value		8,8
	set_variable		9,6
	set_values_inc		10,10,3
	enqueue_goal		12,wait_list_putb_12_0
	put_values_inc		1,7,2
	put_value		3,13
	put_value		5,9
	execute		6,flush_buffer_6_0
set_string_list_13_1:
	otherwise		set_string_list_13_0
	try_me_else		set_string_list_13_6
	integer		12
	integer		13
	try_me_else		set_string_list_13_9
	g_not_less_than		13,12
	put_marked_value		13,9
	b_set_substring		7,13,11,7
	b_add		9,12,9
	execute		10,set_string_list_10_0
set_string_list_13_9:
	put_value		14,2
	put_integer		2,0
	put_marked_value		15,13
	b_substring		11,2,15,2,11
	b_set_substring		7,9,2,2
	b_subtract		12,13,7
	put_marked_value		9,7
	b_substring		11,13,9,9,11
	create_goal		12
	set_value		1,1
	set_variable		2,11
	set_values_inc		3,3,4
	set_variable		7,4
	set_marked_value		8,8
	set_variable		9,6
	set_values_dec		10,10,2
	set_value		12,7
	enqueue_goal		12,wait_list_putb_12_0
	put_value		1,2
	put_value		2,8
	put_value		3,14
	put_value		5,11
	execute		6,flush_buffer_6_0
set_string_list_13_6:
	suspend		set_string_list_13_0
	module_entry		mpimos_window
	predicate		wait_list_putb,12
wait_list_putb_12_0:
	try_me_else		wait_list_putb_12_1
	wait_atom		9,'fep#normal'
	put_value		13,8
	put_marked_value		8,13
	put_integer		9,0
	execute		13,set_string_list_13_0
wait_list_putb_12_1:
	suspend		wait_list_putb_12_0
	module_entry		mpimos_window
	predicate		wait_add_op,13
wait_add_op_13_0:
	try_me_else		wait_add_op_13_1
	atom		10
	branch_on_atom		10,2,wait_add_op_13_1
	bucket_entry_a		already_exist,wait_add_op_13_3
	bucket_entry_a		success,wait_add_op_13_4
wait_add_op_13_3:
	collect_value		13
	collect_value		12
	collect_value		11
	execute		9,monitor_9_0
wait_add_op_13_4:
	collect_value		13
	collect_value		12
	collect_value		11
	execute		9,monitor_9_0
wait_add_op_13_1:
	suspend		wait_add_op_13_0
	module_entry		mpimos_window
	predicate		wait_remove_op,13
wait_remove_op_13_0:
	try_me_else		wait_remove_op_13_1
	jump_on_non_atom		10,wait_remove_op_13_3
	test_atom		10,success,wait_remove_op_13_1
	collect_value		13
	collect_value		12
	collect_value		11
	execute		9,monitor_9_0
wait_remove_op_13_3:
	is_vector		10,wait_remove_op_13_1
	jump_on_arity		10,5,wait_remove_op_13_1
	table_entry		wait_remove_op_13_1
	table_entry		wait_remove_op_13_1
	table_entry		wait_remove_op_13_4
	table_entry		wait_remove_op_13_1
	table_entry		wait_remove_op_13_5
wait_remove_op_13_4:
	read_element		10,0,14
	wait_atom		14,not_find
	read_element		10,1,14
	collect_value		12
	collect_value		11
	collect_value		14
	create_goal		9
	set_values_inc		1,1,5
	set_variable		6,5
	set_values_inc		7,7,3
	enqueue_goal		9,monitor_9_0
	put_reused_func		3,10,remove_op
	write_element_value		3,1,13
	put_atom		1,warning
	put_atom		2,operator_not_found
	put_value		4,6
	execute		5,command_error_5_0
wait_remove_op_13_5:
	read_element		10,0,14
	wait_atom		14,not_find
	read_elements_inc		10,1,14,3
	collect_value		16
	collect_value		15
	collect_value		14
	create_goal		9
	set_values_inc		1,1,5
	set_variable		6,5
	set_values_inc		7,7,3
	enqueue_goal		9,monitor_9_0
	put_reused_func		3,10,remove_op
	write_elements_inc		3,1,11,3
	put_atom		1,warning
	put_atom		2,operator_not_found
	put_value		4,6
	execute		5,command_error_5_0
wait_remove_op_13_1:
	suspend		wait_remove_op_13_0
	module_entry		mpimos_window
	predicate		do,3
do_3_0:
	try_me_else		do_3_1
	jump_on_non_list_var_var		1,do_3_3,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,do_3_0
do_3_3:
	check_nil		1,do_3_1
	get_value		2,3
	proceed
do_3_1:
	suspend		do_3_0
	module_entry		mpimos_window
	predicate		length,2
length_2_0:
	put_integer		3,0
	execute		3,length_3_0
length_2_1:
	suspend		length_2_0
	module_entry		mpimos_window
	predicate		length,3
length_3_0:
	try_me_else		length_3_1
	jump_on_non_list_var_var		1,length_3_3,4,5
	collect_list		1
	collect_value		4
	b_increment		3,1
	put_value		3,1
	put_value		1,5
	execute		3,length_3_0
length_3_3:
	check_nil		1,length_3_1
	get_value		2,3
	proceed
length_3_1:
	suspend		length_3_0
	module_entry		mpimos_window
	predicate		command_error,5
command_error_5_0:
	put_integer		6,5
	b_vector_element		4,6,4,6
	get_value		6,5
	create_goal		3
	set_value		1,1
	set_value		2,4
	put_func		1,2,putt
	write_element_variable		1,1,7
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_structured_constant		1,'$SCNST_11'
	put_list_val_val		5,1,4
	put_func		1,2,putb
	write_element_variable		1,1,6
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_12'
	put_list_val_val		5,1,4
	set_value		3,5
	enqueue_goal		3,raise_error_3_0
	create_goal		2
	set_value		1,3
	set_value		2,7
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,2
	put_value		2,6
	execute		2,message_2_0
command_error_5_1:
	suspend		command_error_5_0
	module_entry		mpimos_window
	predicate		raise_error,3
raise_error_3_0:
	put_integer		6,262144
	put_structured_constant		4,'$SCNST_13'
	put_func		5,2,do
	write_element_value		5,1,3
	put_list_val_val		3,5,4
	put_structured_constant		4,'$SCNST_14'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,5
	put_structured_constant		3,'$SCNST_15'
	put_list_val_val		4,3,2
	b_raise		6,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_3_1:
	suspend		raise_error_3_0
	module_entry		mpimos_window
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	atom		1
	hash_on_atom		1,8,message_2_1
	bucket_entry_a		ambiguous,message_2_3
	bucket_entry_a		bad_window_name_type,message_2_4
	bucket_entry_a		cannot_create_window,message_2_5
	bucket_entry_a		illegal_command,message_2_6
	bucket_entry_a		not_command_stream,message_2_7
	bucket_entry_a		operator_not_found,message_2_8
	bucket_entry_a		syntax_error,message_2_9
	bucket_entry_a		window_not_open,message_2_10
message_2_3:
	put_structured_constant		1,'$SCNST_16'
	get_value		2,1
	proceed
message_2_4:
	put_structured_constant		1,'$SCNST_17'
	get_value		2,1
	proceed
message_2_5:
	put_structured_constant		1,'$SCNST_18'
	get_value		2,1
	proceed
message_2_6:
	put_structured_constant		1,'$SCNST_19'
	get_value		2,1
	proceed
message_2_7:
	put_structured_constant		1,'$SCNST_20'
	get_value		2,1
	proceed
message_2_8:
	put_structured_constant		1,'$SCNST_21'
	get_value		2,1
	proceed
message_2_9:
	put_structured_constant		1,'$SCNST_22'
	get_value		2,1
	proceed
message_2_10:
	put_structured_constant		1,'$SCNST_23'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	begin_const_section		mpimos_window
'$SCNST_0_0':
	define_desc		11,1
	define_integer		2108735
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		print_var_mode
	define_atom		na
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		0,2
	define_atom		print_depth
	define_integer		10
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		0,2
	define_atom		print_length
	define_integer		10
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		11,1
	define_integer		2108730
'$SCNST_6':
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		11,1
	define_integer		2109216
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_12':
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_7_1':
	define_desc		27,2
	define_integer		707406368
	define_integer		42
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_7_1'
'$SCNST_9':
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		27,2
	define_integer		707406378
	define_integer		32
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_10':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_11_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_11_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_11_1'
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_13_2':
	define_desc		27,1
	define_integer		46
'$SCNST_13_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_13_2'
'$SCNST_13_3':
	define_atom		nl
	define_atom		[]
'$SCNST_13_0':
	define_vector		'$SCNST_13_1'
	define_list		'$SCNST_13_3'
'$SCNST_13':
	define_list		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		27,1
	define_integer		41
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_1':
	define_desc		27,6
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		1852405536
	define_integer		544698212
	define_integer		40
'$SCNST_15_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_16_0':
	define_desc		3,5
	define_integer		1768058177
	define_integer		1970238823
	define_integer		2017796211
	define_integer		1936028272
	define_integer		1852795251
'$SCNST_16':
	define_string		'$SCNST_16_0'
'$SCNST_17_0':
	define_desc		27,7
	define_integer		1684957559
	define_integer		1847621487
	define_integer		543518049
	define_integer		1847620457
	define_integer		1931506799
	define_integer		1852404340
	define_integer		103
'$SCNST_17':
	define_string		'$SCNST_17_0'
'$SCNST_18_0':
	define_desc		3,5
	define_integer		1852727651
	define_integer		1663071343
	define_integer		1952540018
	define_integer		1769414757
	define_integer		2003788910
'$SCNST_18':
	define_string		'$SCNST_18_0'
'$SCNST_19_0':
	define_desc		11,4
	define_integer		1701604457
	define_integer		543973735
	define_integer		1835888483
	define_integer		6581857
'$SCNST_19':
	define_string		'$SCNST_19_0'
'$SCNST_20_0':
	define_desc		19,7
	define_integer		1835888483
	define_integer		761556577
	define_integer		1701999731
	define_integer		1763732833
	define_integer		1869488243
	define_integer		1768693876
	define_integer		29811
'$SCNST_20':
	define_string		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		19,6
	define_integer		1852727651
	define_integer		1914729583
	define_integer		1987013989
	define_integer		1886330981
	define_integer		1952543333
	define_integer		29295
'$SCNST_21':
	define_string		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		3,3
	define_integer		1953397075
	define_integer		1159755873
	define_integer		1919906418
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_23_0':
	define_desc		19,5
	define_integer		1684957559
	define_integer		1763735407
	define_integer		1869488243
	define_integer		1886330996
	define_integer		28261
'$SCNST_23':
	define_string		'$SCNST_23_0'
