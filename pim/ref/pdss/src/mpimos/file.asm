mpimos_file:
	module		mpimos_file
	entry		create,3,create_3_0
	entry		create,4,create_4_0
	entry		os_create,7,os_create_7_0
	entry		request,4,request_4_0
	module_entry		mpimos_file
	predicate		create,3
create_3_0:
	put_integer		5,65536
	put_atom		6,file
	put_func		4,4,create
	write_elements_inc		4,1,1,3
	b_raise		5,6,4
	put_integer		1,2
	b_consume_resource		1
	proceed
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_file
	predicate		create,4
create_4_0:
	put_integer		6,65536
	put_atom		7,file
	put_func		5,5,create
	write_elements_inc		5,1,1,4
	b_raise		6,7,5
	put_integer		1,2
	b_consume_resource		1
	proceed
create_4_1:
	suspend		create_4_0
	module_entry		mpimos_file
	predicate		request,4
request_4_0:
	try_me_else		request_4_1
	vector		1
	jump_on_arity		1,6,request_4_1
	table_entry		request_4_1
	table_entry		request_4_1
	table_entry		request_4_1
	table_entry		request_4_1
	table_entry		request_4_3
	table_entry		request_4_4
request_4_3:
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,3
	string		6
	g_string		6,8,9
	wait_integer		9,8
	collect_vector		1
	create_goal		7
	set_value		1,5
	set_marked_value		2,6
	set_value		3,7
	set_variable		4,5
	set_values_inc		5,3,2
	set_atom		7,no_status
	enqueue_goal		7,mode_check_7_0
	put_value		1,2
	put_values_dec		2,6,2
	execute_external		mpimos_utility,pathname,3
request_4_4:
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,4
	string		6
	g_string		6,9,10
	wait_integer		10,8
	collect_vector		1
	create_goal		7
	set_value		1,5
	set_marked_value		2,6
	set_value		3,7
	set_variable		4,5
	set_values_inc		5,3,2
	put_func		1,2,status
	write_element_value		1,1,8
	set_value		7,1
	enqueue_goal		7,mode_check_7_0
	put_value		1,2
	put_values_dec		2,6,2
	execute_external		mpimos_utility,pathname,3
request_4_1:
	otherwise		request_4_0
	try_me_else		request_4_7
	vector		1
	jump_on_arity		1,6,request_4_7
	table_entry		request_4_7
	table_entry		request_4_7
	table_entry		request_4_7
	table_entry		request_4_7
	table_entry		request_4_9
	table_entry		request_4_10
request_4_9:
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,3
	collect_value		3
	collect_value		2
	collect_vector		1
	get_nil		4
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,bad_file_name_type
	put_values_inc		2,5,3
	put_atom		5,no_status
	execute		5,create_error_5_0
request_4_10:
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,4
	collect_value		3
	collect_value		2
	collect_vector		1
	get_nil		4
	put_integer		1,1
	b_consume_resource		1
	put_func		9,2,status
	write_element_value		9,1,8
	put_atom		1,bad_file_name_type
	put_values_inc		2,5,3
	put_value		5,9
	execute		5,create_error_5_0
request_4_7:
	suspend		request_4_0
	module_entry		mpimos_file
	predicate		mode_check,7
mode_check_7_0:
	try_me_else		mode_check_7_1
	atom		3
	branch_on_atom		3,3,mode_check_7_1
	bucket_entry_a		a,mode_check_7_3
	bucket_entry_a		r,mode_check_7_4
	bucket_entry_a		w,mode_check_7_5
mode_check_7_3:
	wait		4
	put_value		10,2
	put_func		2,6,create
	write_element_variable		2,1,9
	write_element_value		2,2,4
	write_element_atom		2,3,'fep#append'
	write_element_variable		2,4,8
	write_element_value		2,5,5
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list		2
	write_car_value		2,3
	write_cdr_nil		2
	get_list_value		6,2
	put_integer		2,11
	b_consume_resource		2
	put_values_inc		2,9,2
	put_atom		4,a
	put_values_dec		5,8,2
	execute		6,create_monitor_6_0
mode_check_7_4:
	wait		4
	put_value		10,2
	put_func		2,6,create
	write_element_variable		2,1,9
	write_element_value		2,2,4
	write_element_atom		2,3,'fep#read'
	write_element_variable		2,4,8
	write_element_value		2,5,5
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list		2
	write_car_value		2,3
	write_cdr_nil		2
	get_list_value		6,2
	put_integer		2,11
	b_consume_resource		2
	put_values_inc		2,9,2
	put_atom		4,r
	put_values_dec		5,8,2
	execute		6,create_monitor_6_0
mode_check_7_5:
	wait		4
	put_value		10,2
	put_func		2,6,create
	write_element_variable		2,1,9
	write_element_value		2,2,4
	write_element_atom		2,3,'fep#write'
	write_element_variable		2,4,8
	write_element_value		2,5,5
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list		2
	write_car_value		2,3
	write_cdr_nil		2
	get_list_value		6,2
	put_integer		2,11
	b_consume_resource		2
	put_values_inc		2,9,2
	put_atom		4,w
	put_values_dec		5,8,2
	execute		6,create_monitor_6_0
mode_check_7_1:
	otherwise		mode_check_7_0
	try_me_else		mode_check_7_8
	atom		3
	put_value		8,3
	collect_value		5
	collect_value		4
	put_value		4,1
	put_value		3,2
	get_nil		6
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,bad_open_mode
	put_value		2,4
	put_values_dec		4,8,2
	execute		5,create_error_5_0
mode_check_7_8:
	otherwise		mode_check_7_0
	collect_value		5
	collect_value		4
	put_value		5,1
	put_value		8,2
	put_value		4,3
	get_nil		6
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,bad_open_mode_type
	put_value		2,5
	put_value		3,8
	put_value		5,7
	execute		5,create_error_5_0
mode_check_7_12:
	suspend		mode_check_7_0
	module_entry		mpimos_file
	predicate		os_create,7
os_create_7_0:
	try_me_else		os_create_7_1
	wait		2
	atom		3
	branch_on_atom		3,3,os_create_7_1
	bucket_entry_a		a,os_create_7_3
	bucket_entry_a		r,os_create_7_4
	bucket_entry_a		w,os_create_7_5
os_create_7_3:
	put_value		8,2
	put_func		2,6,create
	write_element_variable		2,1,10
	write_element_marked_value		2,2,8
	write_element_atom		2,3,'fep#append'
	write_element_variable		2,4,9
	write_element_value		2,5,4
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	get_list_value		5,2
	put_func		6,2,status
	write_element_value		6,1,7
	put_value		2,10
	put_value		3,8
	put_atom		4,a
	put_value		5,9
	execute		6,create_monitor_6_0
os_create_7_4:
	put_value		8,2
	put_func		2,6,create
	write_element_variable		2,1,10
	write_element_marked_value		2,2,8
	write_element_atom		2,3,'fep#read'
	write_element_variable		2,4,9
	write_element_value		2,5,4
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	get_list_value		5,2
	put_func		6,2,status
	write_element_value		6,1,7
	put_value		2,10
	put_value		3,8
	put_atom		4,r
	put_value		5,9
	execute		6,create_monitor_6_0
os_create_7_5:
	put_value		8,2
	put_func		2,6,create
	write_element_variable		2,1,10
	write_element_marked_value		2,2,8
	write_element_atom		2,3,'fep#write'
	write_element_variable		2,4,9
	write_element_value		2,5,4
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	get_list_value		5,2
	put_func		6,2,status
	write_element_value		6,1,7
	put_value		2,10
	put_value		3,8
	put_atom		4,w
	put_value		5,9
	execute		6,create_monitor_6_0
os_create_7_1:
	suspend		os_create_7_0
	module_entry		mpimos_file
	predicate		create_monitor,6
create_monitor_6_0:
	try_me_else		create_monitor_6_1
	wait_atom		4,r
	wait_atom		5,'fep#normal'
	put_integer		4,2
	b_consume_resource		4
	b_merge		5,4
	get_value		5,1
	b_merge		8,1
	put_vector		9,2
	write_element_variable		9,0,5
	write_element_variable		9,1,7
	get_vector_value		8,9
	create_goal		5
	set_value		1,4
	set_value		2,2
	set_value		3,7
	set_variable		4,2
	put_func		4,7,atr
	write_element_value		4,1,3
	write_element_atom		4,2,r
	write_element_integer		4,3,100
	write_element_integer		4,4,100
	write_element_integer		4,5,2048
	write_element_atom		4,6,reading
	set_value		5,4
	enqueue_goal		5,read_mode_5_0
	create_goal		2
	set_value		1,2
	set_value		2,5
	enqueue_goal_external		mpimos_parser,do,2
	create_goal		1
	set_value		1,1
	enqueue_goal_external		mpimos_operator_manipulator,create,1
	put_value		1,6
	execute		1,create_success_1_0
create_monitor_6_1:
	try_me_else		create_monitor_6_3
	atom		5
	branch_on_atom		5,2,create_monitor_6_3
	bucket_entry_a		'fep#abnormal',create_monitor_6_5
	bucket_entry_a		'fep#normal',create_monitor_6_6
create_monitor_6_5:
	put_value		5,1
	get_nil		2
	put_atom		1,cannot_open_file
	put_value		2,5
	put_value		5,6
	execute		5,create_error_5_0
create_monitor_6_6:
	put_atom		7,r
	g_diff		4,7
	put_integer		5,2
	b_consume_resource		5
	b_merge		7,5
	get_value		7,1
	b_merge		7,1
	put_vector		10,2
	write_element_variable		10,0,8
	write_element_variable		10,1,9
	get_vector_value		7,10
	put_integer		7,2048
	put_integer		10,8
	b_new_string		7,7,10
	create_goal		8
	set_value		1,5
	set_value		2,2
	set_value		3,9
	set_variable		4,5
	put_func		2,7,atr
	write_elements_inc		2,1,3,2
	write_element_integer		2,3,100
	write_element_integer		2,4,100
	write_element_integer		2,5,2048
	write_element_atom		2,6,writing
	set_value		5,2
	set_value		6,7
	set_integer		7,2048
	set_integer		8,0
	enqueue_goal		8,write_mode_8_0
	create_goal		2
	put_structured_constant		2,'$SCNST_0'
	put_list_val_val		3,2,5
	put_structured_constant		2,'$SCNST_1'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_2'
	put_list_val_val		3,2,4
	set_value		1,3
	set_value		2,8
	enqueue_goal_external		mpimos_unparser,create,2
	create_goal		1
	set_value		1,1
	enqueue_goal_external		mpimos_operator_manipulator,create,1
	put_value		1,6
	execute		1,create_success_1_0
create_monitor_6_3:
	suspend		create_monitor_6_0
	module_entry		mpimos_file
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
	module_entry		mpimos_file
	predicate		create_error,5
create_error_5_0:
	try_me_else		create_error_5_1
	jump_on_non_atom		5,create_error_5_3
	test_atom		5,no_status,create_error_5_1
	create_goal		5
	set_value		1,2
	set_void		2
	set_void		3
	set_void		4
	put_func		2,7,atr
	write_element_marked_value		2,1,3
	write_element_marked_value		2,2,4
	write_element_integer		2,3,100
	write_element_integer		2,4,100
	write_element_integer		2,5,2048
	write_element_atom		2,6,closed
	set_value		5,2
	enqueue_goal		5,closed_5_0
	create_goal		4
	set_atom		1,error
	set_variable		2,6
	set_variable		3,7
	put_func		2,2,putb
	write_element_variable		2,1,8
	put_list		5
	write_car_value		5,2
	write_cdr_nil		5
	put_structured_constant		2,'$SCNST_3'
	put_list_val_val		9,2,5
	set_value		4,9
	enqueue_goal		4,raise_error_4_0
	create_goal		2
	set_value		1,1
	set_value		2,8
	enqueue_goal		2,message_2_0
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,3
	put_value		2,6
	execute_external		mpimos_utility,freeze,2
create_error_5_3:
	check_vector		5,2,create_error_5_1
	read_element		5,0,6
	wait_atom		6,status
	read_element		5,1,6
	put_reused_func		5,5,error
	write_element_value		5,1,1
	get_vector_value		6,5
	put_func		5,7,atr
	write_elements_inc		5,1,3,2
	write_element_integer		5,3,100
	write_element_integer		5,4,100
	write_element_integer		5,5,2048
	write_element_atom		5,6,closed
	put_value		1,2
	put_void		2
	put_void		3
	put_void		4
	execute		5,closed_5_0
create_error_5_1:
	suspend		create_error_5_0
	module_entry		mpimos_file
	predicate		read_mode,5
read_mode_5_0:
	try_me_else		read_mode_5_1
	jump_on_non_list		1,read_mode_5_3
	read_car		1,6
	jump_on_non_atom		6,read_mode_5_5
	test_atom		6,nl,read_mode_5_1
	read_cdr		1,7
	collect_list		1
	put_value		1,7
	put_atom		6,nl
	execute		6,read_mode_error_6_0
read_mode_5_5:
	is_vector		6,read_mode_5_1
	jump_on_arity		6,5,read_mode_5_1
	table_entry		read_mode_5_1
	table_entry		read_mode_5_1
	table_entry		read_mode_5_6
	table_entry		read_mode_5_7
	table_entry		read_mode_5_8
read_mode_5_6:
	read_element		6,0,7
	atom		7
	hash_on_atom		7,20,read_mode_5_1
	bucket_entry_a		buffer_length,read_mode_5_10
	bucket_entry_a		change_op_pool,read_mode_5_11
	bucket_entry_a		close,read_mode_5_12
	bucket_entry_a		do,read_mode_5_13
	bucket_entry_a		flush,read_mode_5_14
	bucket_entry_a		getc,read_mode_5_15
	bucket_entry_a		getl,read_mode_5_16
	bucket_entry_a		gett,read_mode_5_17
	bucket_entry_a		print_depth,read_mode_5_18
	bucket_entry_a		print_length,read_mode_5_19
	bucket_entry_a		print_var_mode,read_mode_5_20
	bucket_entry_a		putb,read_mode_5_21
	bucket_entry_a		putc,read_mode_5_22
	bucket_entry_a		putet,read_mode_5_23
	bucket_entry_a		putl,read_mode_5_24
	bucket_entry_a		putt,read_mode_5_25
	bucket_entry_a		puttq,read_mode_5_26
	bucket_entry_a		remove_op,read_mode_5_27
	bucket_entry_a		skip,read_mode_5_28
	bucket_entry_a		tab,read_mode_5_29
read_mode_5_10:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_less_than		10,9
	collect_list		1
	collect_vector		6
	put_integer		1,5
	b_set_vector_element		5,1,1,9,5
	put_value		1,8
	execute		5,read_mode_5_0
read_mode_5_11:
	read_cdr		1,8
	read_element		6,1,9
	collect_vector		6
	put_func		6,3,replace_operator_pool
	write_element_void		6,1
	write_element_value		6,2,9
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	execute		5,read_mode_5_0
read_mode_5_12:
	read_cdr		1,8
	read_element		6,1,9
	put_reused_func		6,6,close
	write_element_variable		6,1,7
	get_reused_list_val_var		2,1,1,6,6
	put_value		1,8
	put_value		2,6
	put_value		6,7
	put_value		7,9
	execute		7,wait_close_7_0
read_mode_5_13:
	read_element		6,1,8
	jump_on_non_list		8,read_mode_5_31
	read_cdr		1,9
	read_car		8,7
	read_cdr		8,10
	collect_list		8
	collect_vector		6
	create_goal		5
	set_variable		1,6
	set_values_inc		2,2,4
	enqueue_goal		5,read_mode_5_0
	put_reused_list_val_val		1,1,7,10
	put_value		2,9
	put_value		3,6
	execute		3,append_3_0
read_mode_5_31:
	check_nil		8,read_mode_5_1
	read_cdr		1,9
	collect_list		1
	collect_vector		6
	put_value		1,9
	execute		5,read_mode_5_0
read_mode_5_14:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	collect_value		9
	put_reused_func		6,6,flush
	write_element_void		6,1
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_15:
	read_cdr		1,8
	read_element		6,1,9
	collect_vector		6
	put_func		6,3,getc
	write_element_variable		6,1,7
	write_element_variable		6,2,10
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,8
	put_value		2,6
	put_value		6,10
	put_value		8,9
	execute		8,unify_char_8_0
read_mode_5_16:
	read_cdr		1,8
	read_element		6,1,9
	collect_vector		6
	put_func		6,3,getl
	write_element_variable		6,1,7
	write_element_variable		6,2,10
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,8
	put_value		2,6
	put_value		6,10
	put_value		8,9
	execute		8,unify_string_8_0
read_mode_5_17:
	read_cdr		1,8
	read_element		6,1,9
	put_func		7,4,gettkn
	write_element_variable		7,1,13
	write_element_variable		7,2,12
	write_element_variable		7,3,11
	get_reused_list_val_var		2,1,1,7,10
	put_integer		1,3
	b_consume_resource		1
	put_reused_func		7,6,gett
	write_element_value		7,1,9
	put_value		1,8
	put_value		2,10
	put_value		6,12
	put_value		8,13
	put_value		9,11
	execute		9,make_term_9_0
read_mode_5_18:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_less_than		10,9
	collect_list		1
	collect_vector		6
	put_integer		1,4
	b_set_vector_element		5,1,1,9,5
	put_value		1,8
	execute		5,read_mode_5_0
read_mode_5_19:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_less_than		10,9
	collect_list		1
	collect_vector		6
	put_integer		1,3
	b_set_vector_element		5,1,1,9,5
	put_value		1,8
	execute		5,read_mode_5_0
read_mode_5_20:
	read_cdr		1,8
	read_element		6,1,9
	atom		9
	collect_list		1
	collect_vector		6
	put_value		1,8
	execute		5,read_mode_5_0
read_mode_5_21:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,putb
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_22:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,putc
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_23:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,putet
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_24:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,putl
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_25:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,putt
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_26:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,puttq
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_27:
	read_cdr		1,8
	read_element		6,1,9
	atom		9
	collect_vector		6
	put_func		6,3,remove_operator
	write_element_value		6,1,9
	write_element_variable		6,2,7
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	put_value		6,7
	execute		6,check_op_6_0
read_mode_5_28:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_not_less_than		9,10
	put_integer		10,255
	g_not_less_than		10,9
	collect_vector		6
	put_func		6,3,getc
	write_element_variable		6,1,7
	write_element_variable		6,2,10
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,8
	put_value		2,6
	put_value		6,10
	put_value		8,9
	execute		8,skip_char_8_0
read_mode_5_29:
	read_cdr		1,8
	read_element		6,1,9
	collect_list		1
	put_reused_func		6,6,tab
	write_element_value		6,1,9
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_7:
	read_element		6,0,7
	atom		7
	hash_on_atom		7,6,read_mode_5_1
	bucket_entry_a		getb,read_mode_5_33
	bucket_entry_a		getft,read_mode_5_34
	bucket_entry_a		gett,read_mode_5_35
	bucket_entry_a		operator,read_mode_5_36
	bucket_entry_a		putb,read_mode_5_37
	bucket_entry_a		replace_op_pool,read_mode_5_38
read_mode_5_33:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	integer		10
	put_integer		11,0
	g_less_than		11,10
	collect_vector		6
	put_func		6,4,getb
	write_element_variable		6,1,7
	write_element_value		6,2,10
	write_element_variable		6,3,10
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,8
	put_value		2,6
	put_value		6,10
	put_value		8,9
	execute		8,unify_string_8_0
read_mode_5_34:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	put_func		7,4,gettkn
	write_element_variable		7,1,14
	write_element_variable		7,2,13
	write_element_variable		7,3,12
	get_reused_list_val_var		2,1,1,7,11
	put_integer		1,3
	b_consume_resource		1
	put_reused_func		7,6,getft
	write_elements_inc		7,1,9,2
	put_value		1,8
	put_value		2,11
	put_value		6,13
	put_value		8,14
	put_value		9,12
	execute		9,make_term_9_0
read_mode_5_35:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	put_func		7,4,gettkn
	write_element_variable		7,1,14
	write_element_variable		7,2,13
	write_element_variable		7,3,12
	get_reused_list_val_var		2,1,1,7,11
	put_integer		1,3
	b_consume_resource		1
	put_reused_func		7,6,gett
	write_elements_inc		7,1,9,2
	put_value		1,8
	put_value		2,11
	put_value		6,13
	put_value		8,14
	put_value		9,12
	execute		9,make_term_9_0
read_mode_5_36:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	atom		9
	put_reused_func		6,6,operator
	write_elements_inc		6,1,9,2
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	execute		5,read_mode_5_0
read_mode_5_37:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	collect_list		1
	put_reused_func		6,6,putb
	write_elements_inc		6,1,9,2
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_38:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	put_reused_func		6,6,replace_operator_pool
	write_elements_inc		6,1,9,2
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	execute		5,read_mode_5_0
read_mode_5_8:
	read_element		6,0,7
	atom		7
	hash_on_atom		7,7,read_mode_5_1
	bucket_entry_a		add_op,read_mode_5_40
	bucket_entry_a		getet,read_mode_5_41
	bucket_entry_a		getft,read_mode_5_42
	bucket_entry_a		putet,read_mode_5_43
	bucket_entry_a		putt,read_mode_5_44
	bucket_entry_a		puttq,read_mode_5_45
	bucket_entry_a		remove_op,read_mode_5_46
read_mode_5_40:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	integer		9
	put_integer		12,1
	g_not_less_than		9,12
	put_integer		12,1200
	g_not_less_than		12,9
	atom		10
	atom		11
	collect_vector		6
	put_func		6,5,add_operator
	write_elements_inc		6,1,9,3
	write_element_variable		6,4,7
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	put_value		6,7
	execute		6,check_op_6_0
read_mode_5_41:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	put_reused_func		6,6,gettkn
	write_element_variable		6,1,14
	write_element_variable		6,2,13
	write_element_variable		6,3,12
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_func		7,4,getet
	write_elements_inc		7,1,9,3
	put_value		1,8
	put_value		2,6
	put_value		6,13
	put_value		8,14
	put_value		9,12
	execute		9,make_term_9_0
read_mode_5_42:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	put_reused_func		6,6,gettkn
	write_element_variable		6,1,14
	write_element_variable		6,2,13
	write_element_variable		6,3,12
	get_reused_list_val_var		2,1,1,6,6
	put_integer		1,3
	b_consume_resource		1
	put_func		7,4,getft
	write_elements_inc		7,1,9,3
	put_value		1,8
	put_value		2,6
	put_value		6,13
	put_value		8,14
	put_value		9,12
	execute		9,make_term_9_0
read_mode_5_43:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	collect_list		1
	put_reused_func		6,6,putet
	write_elements_inc		6,1,9,3
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_44:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	collect_list		1
	put_reused_func		6,6,putt
	write_elements_inc		6,1,9,3
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_45:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	collect_list		1
	put_reused_func		6,6,puttq
	write_elements_inc		6,1,9,3
	put_value		1,8
	execute		6,read_mode_error_6_0
read_mode_5_46:
	read_cdr		1,8
	read_elements_inc		6,1,9,3
	integer		9
	put_integer		12,1
	g_not_less_than		9,12
	put_integer		12,1200
	g_not_less_than		12,9
	atom		10
	atom		11
	collect_vector		6
	put_func		6,5,remove_operator
	write_elements_inc		6,1,9,3
	write_element_variable		6,4,7
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,8
	put_value		3,6
	put_value		6,7
	execute		6,check_op_6_0
read_mode_5_3:
	check_nil		1,read_mode_5_1
	collect_value		5
	get_nil		2
	get_nil		3
	get_nil		4
	proceed
read_mode_5_1:
	otherwise		read_mode_5_0
	try_me_else		read_mode_5_65
	wait_list_var_var		1,6,7
	collect_list		1
	create_goal		5
	set_value		1,7
	set_values_inc		2,2,3
	set_variable		5,7
	enqueue_goal		5,read_mode_5_0
	put_atom		1,warning
	put_atom		2,illegal_command
	put_values_dec		3,6,2
	put_value		5,7
	execute		5,command_error_5_0
read_mode_5_65:
	otherwise		read_mode_5_0
	collect_value		4
	collect_value		3
	collect_value		2
	put_value		3,1
	put_atom		1,error
	put_atom		2,not_command_stream
	put_value		4,5
	put_void		5
	execute		5,command_error_5_0
read_mode_5_69:
	suspend		read_mode_5_0
	module_entry		mpimos_file
	predicate		read_mode_error,6
read_mode_error_6_0:
	create_goal		5
	set_values_inc		1,1,4
	set_variable		5,7
	enqueue_goal		5,read_mode_5_0
	put_atom		1,warning
	put_atom		2,not_write_mode
	put_values_dec		3,6,2
	put_value		5,7
	execute		5,command_error_5_0
read_mode_error_6_1:
	suspend		read_mode_error_6_0
	module_entry		mpimos_file
	predicate		unify_char,8
unify_char_8_0:
	try_me_else		unify_char_8_1
	atom		6
	branch_on_atom		6,3,unify_char_8_1
	bucket_entry_a		'fep#abnormal',unify_char_8_3
	bucket_entry_a		'fep#end_of_file',unify_char_8_4
	bucket_entry_a		'fep#normal',unify_char_8_5
unify_char_8_3:
	collect_value		7
	get_atom		8,end_of_file
	execute		5,read_mode_5_0
unify_char_8_4:
	collect_value		7
	get_atom		8,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
unify_char_8_5:
	integer		7
	get_value		8,7
	execute		5,read_mode_5_0
unify_char_8_1:
	suspend		unify_char_8_0
	module_entry		mpimos_file
	predicate		skip_char,8
skip_char_8_0:
	try_me_else		skip_char_8_1
	atom		6
	branch_on_atom		6,3,skip_char_8_1
	bucket_entry_a		'fep#abnormal',skip_char_8_3
	bucket_entry_a		'fep#end_of_file',skip_char_8_4
	bucket_entry_a		'fep#normal',skip_char_8_5
skip_char_8_3:
	collect_value		8
	collect_value		7
	execute		5,read_mode_5_0
skip_char_8_4:
	collect_value		8
	collect_value		7
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
skip_char_8_5:
	integer		7
	integer		8
	try_me_else		skip_char_8_8
	g_equal		7,8
	execute		5,read_mode_5_0
skip_char_8_8:
	put_func		6,3,getc
	write_element_variable		6,1,7
	write_element_variable		6,2,9
	get_list_val_var		2,10,6,6
	put_integer		2,3
	b_consume_resource		2
	put_value		2,6
	put_value		6,9
	execute		8,skip_char_8_0
skip_char_8_1:
	suspend		skip_char_8_0
	module_entry		mpimos_file
	predicate		unify_string,8
unify_string_8_0:
	try_me_else		unify_string_8_1
	atom		6
	branch_on_atom		6,3,unify_string_8_1
	bucket_entry_a		'fep#abnormal',unify_string_8_3
	bucket_entry_a		'fep#end_of_file',unify_string_8_4
	bucket_entry_a		'fep#normal',unify_string_8_5
unify_string_8_3:
	collect_value		7
	get_atom		8,end_of_file
	execute		5,read_mode_5_0
unify_string_8_4:
	collect_value		7
	get_atom		8,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
unify_string_8_5:
	string		7
	get_value		8,7
	execute		5,read_mode_5_0
unify_string_8_1:
	suspend		unify_string_8_0
	module_entry		mpimos_file
	predicate		make_term,9
make_term_9_0:
	try_me_else		make_term_9_1
	vector		5
	wait_atom		6,'fep#abnormal'
	vector		7
	jump_on_arity		7,5,make_term_9_1
	table_entry		make_term_9_1
	table_entry		make_term_9_1
	table_entry		make_term_9_5
	table_entry		make_term_9_6
	table_entry		make_term_9_7
make_term_9_5:
	read_element		7,0,10
	wait_atom		10,gett
	read_element		7,1,11
	try_me_else		make_term_9_9
	put_integer		12,6
	g_vector_element		5,12,12
	wait_atom		12,read_end
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		11,end_of_file
	execute		5,read_mode_5_0
make_term_9_9:
	try_me_else		make_term_9_1
	put_integer		12,6
	g_vector_element		5,12,12
	wait_atom		12,reading
	collect_value		9
	collect_vector		7
	put_variable		6,9
	b_decrement		6,6
	get_atom		11,end_of_file
	put_integer		7,1
	b_vector_element		5,7,5,7
	create_goal		5
	set_values_inc		1,1,4
	set_value		5,7
	enqueue_goal		5,read_mode_5_0
	create_goal		4
	set_atom		1,eof_in_quote
	set_marked_value		2,8
	set_values_dec		3,6,2
	enqueue_goal		4,display_parse_error_4_0
	put_values_inc		1,8,2
	execute		2,elements_2_0
make_term_9_6:
	read_element		7,0,10
	atom		10
	branch_on_atom		10,2,make_term_9_1
	bucket_entry_a		getft,make_term_9_11
	bucket_entry_a		gett,make_term_9_12
make_term_9_11:
	read_elements_inc		7,1,11,2
	try_me_else		make_term_9_13
	put_integer		13,6
	g_vector_element		5,13,13
	wait_atom		13,read_end
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		11,end_of_file
	get_integer		12,0
	execute		5,read_mode_5_0
make_term_9_13:
	try_me_else		make_term_9_1
	put_integer		13,6
	g_vector_element		5,13,13
	wait_atom		13,reading
	collect_value		9
	collect_vector		7
	put_variable		6,9
	b_decrement		6,6
	get_atom		11,end_of_file
	get_integer		12,0
	put_integer		7,1
	b_vector_element		5,7,5,7
	create_goal		5
	set_values_inc		1,1,4
	set_value		5,7
	enqueue_goal		5,read_mode_5_0
	create_goal		4
	set_atom		1,eof_in_quote
	set_marked_value		2,8
	set_values_dec		3,6,2
	enqueue_goal		4,display_parse_error_4_0
	put_values_inc		1,8,2
	execute		2,elements_2_0
make_term_9_12:
	read_elements_inc		7,1,11,2
	try_me_else		make_term_9_14
	put_integer		13,6
	g_vector_element		5,13,13
	wait_atom		13,read_end
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		11,end_of_file
	get_atom		12,end_of_file
	execute		5,read_mode_5_0
make_term_9_14:
	try_me_else		make_term_9_1
	put_integer		13,6
	g_vector_element		5,13,13
	wait_atom		13,reading
	collect_value		9
	collect_vector		7
	get_value		11,8
	get_atom		12,eof_in_quote
	execute		5,read_mode_5_0
make_term_9_7:
	read_element		7,0,10
	atom		10
	branch_on_atom		10,2,make_term_9_1
	bucket_entry_a		getet,make_term_9_16
	bucket_entry_a		getft,make_term_9_17
make_term_9_16:
	read_elements_inc		7,1,11,3
	try_me_else		make_term_9_18
	put_integer		14,6
	g_vector_element		5,14,14
	wait_atom		14,read_end
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		11,end_of_file
	get_integer		12,0
	get_atom		13,end_of_file
	execute		5,read_mode_5_0
make_term_9_18:
	try_me_else		make_term_9_1
	put_integer		14,6
	g_vector_element		5,14,14
	wait_atom		14,reading
	collect_vector		7
	get_value		11,8
	get_value		12,9
	get_atom		13,eof_in_quote
	execute		5,read_mode_5_0
make_term_9_17:
	read_elements_inc		7,1,11,3
	try_me_else		make_term_9_19
	put_integer		14,6
	g_vector_element		5,14,14
	wait_atom		14,read_end
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		11,end_of_file
	get_integer		12,0
	get_atom		13,end_of_file
	execute		5,read_mode_5_0
make_term_9_19:
	try_me_else		make_term_9_1
	put_integer		14,6
	g_vector_element		5,14,14
	wait_atom		14,reading
	collect_vector		7
	get_value		11,8
	get_value		12,9
	get_atom		13,eof_in_quote
	execute		5,read_mode_5_0
make_term_9_1:
	try_me_else		make_term_9_20
	atom		6
	branch_on_atom		6,2,make_term_9_20
	bucket_entry_a		'fep#end_of_file',make_term_9_22
	bucket_entry_a		'fep#normal',make_term_9_23
make_term_9_22:
	vector		7
	jump_on_arity		7,5,make_term_9_20
	table_entry		make_term_9_20
	table_entry		make_term_9_20
	table_entry		make_term_9_25
	table_entry		make_term_9_26
	table_entry		make_term_9_27
make_term_9_25:
	read_element		7,0,10
	wait_atom		10,gett
	read_element		7,1,6
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		6,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
make_term_9_26:
	read_element		7,0,10
	atom		10
	branch_on_atom		10,2,make_term_9_20
	bucket_entry_a		getft,make_term_9_29
	bucket_entry_a		gett,make_term_9_30
make_term_9_29:
	read_element		7,1,6
	read_element		7,2,11
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		6,end_of_file
	get_integer		11,0
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
make_term_9_30:
	read_element		7,1,6
	read_element		7,2,11
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		6,end_of_file
	get_atom		11,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
make_term_9_27:
	read_element		7,0,10
	atom		10
	branch_on_atom		10,2,make_term_9_20
	bucket_entry_a		getet,make_term_9_32
	bucket_entry_a		getft,make_term_9_33
make_term_9_32:
	read_element		7,1,6
	read_elements_inc		7,2,11,2
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		6,end_of_file
	get_integer		11,0
	get_atom		12,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
make_term_9_33:
	read_element		7,1,6
	read_elements_inc		7,2,11,2
	collect_value		9
	collect_value		8
	collect_vector		7
	get_atom		6,end_of_file
	get_integer		11,0
	get_atom		12,end_of_file
	put_integer		6,6
	put_atom		7,read_end
	b_set_vector_element		5,6,5,7,6
	put_value		5,6
	execute		5,read_mode_5_0
make_term_9_23:
	vector		7
	try_me_else		make_term_9_35
	put_integer		10,0
	g_vector_element		7,10,10
	put_atom		11,getet
	g_diff		10,11
	put_value		10,8
	put_func		6,4,parse
	write_element_marked_value		6,1,10
	write_element_variable		6,2,8
	write_element_variable		6,3,11
	get_list_val_var		4,12,6,6
	put_value		4,6
	put_value		6,11
	execute		10,check_parse_10_0
make_term_9_35:
	try_me_else		make_term_9_20
	put_integer		10,0
	g_vector_element		7,10,10
	wait_atom		10,getet
	put_value		10,8
	put_func		6,4,parse_ex
	write_element_marked_value		6,1,10
	write_element_variable		6,2,8
	write_element_variable		6,3,11
	get_list_val_var		4,12,6,6
	put_value		4,6
	put_value		6,11
	execute		10,check_parse_10_0
make_term_9_20:
	suspend		make_term_9_0
	module_entry		mpimos_file
	predicate		check_parse,10
check_parse_10_0:
	try_me_else		check_parse_10_1
	jump_on_non_atom		6,check_parse_10_3
	test_atom		6,parsed,check_parse_10_1
	vector		7
	jump_on_arity		7,5,check_parse_10_1
	table_entry		check_parse_10_1
	table_entry		check_parse_10_1
	table_entry		check_parse_10_5
	table_entry		check_parse_10_6
	table_entry		check_parse_10_7
check_parse_10_5:
	read_element		7,0,11
	wait_atom		11,gett
	read_element		7,1,12
	integer		9
	test_integer		9,0,check_parse_10_10
	collect_value		10
	collect_vector		7
	get_value		8,12
	execute		5,read_mode_5_0
check_parse_10_10:
	put_integer		13,0
	g_less_than		13,9
	collect_value		10
	collect_vector		7
	create_goal		5
	set_values_inc		1,1,5
	enqueue_goal		5,read_mode_5_0
	put_values_inc		1,8,2
	put_value		3,12
	execute_external		mpimos_utility,melt,3
check_parse_10_6:
	read_element		7,0,11
	atom		11
	branch_on_atom		11,2,check_parse_10_1
	bucket_entry_a		getft,check_parse_10_12
	bucket_entry_a		gett,check_parse_10_13
check_parse_10_12:
	read_element		7,1,6
	read_element		7,2,12
	collect_value		10
	collect_vector		7
	get_value		6,8
	get_value		12,9
	execute		5,read_mode_5_0
check_parse_10_13:
	read_elements_inc		7,1,12,2
	integer		9
	test_integer		9,0,check_parse_10_15
	collect_value		10
	collect_vector		7
	get_value		8,12
	get_atom		13,success
	execute		5,read_mode_5_0
check_parse_10_15:
	put_integer		14,0
	g_less_than		14,9
	collect_value		10
	collect_vector		7
	get_atom		13,success
	create_goal		5
	set_values_inc		1,1,5
	enqueue_goal		5,read_mode_5_0
	put_values_inc		1,8,2
	put_value		3,12
	execute_external		mpimos_utility,melt,3
check_parse_10_7:
	read_element		7,0,11
	atom		11
	branch_on_atom		11,2,check_parse_10_1
	bucket_entry_a		getet,check_parse_10_17
	bucket_entry_a		getft,check_parse_10_18
check_parse_10_17:
	read_element		7,1,6
	read_elements_inc		7,2,12,2
	collect_value		10
	collect_vector		7
	get_value		6,8
	get_value		12,9
	get_atom		13,success
	execute		5,read_mode_5_0
check_parse_10_18:
	read_element		7,1,6
	read_elements_inc		7,2,12,2
	collect_value		10
	collect_vector		7
	get_value		6,8
	get_value		12,9
	get_atom		13,success
	execute		5,read_mode_5_0
check_parse_10_3:
	check_vector		6,3,check_parse_10_1
	read_element		6,0,11
	atom		11
	branch_on_atom		11,3,check_parse_10_1
	bucket_entry_a		ambiguous,check_parse_10_20
	bucket_entry_a		error,check_parse_10_21
	bucket_entry_a		remained,check_parse_10_22
check_parse_10_20:
	read_elements_inc		6,1,12,2
	collect_value		8
	collect_value		13
	collect_vector		6
	put_atom		6,ambiguous
	put_values_inc		8,9,2
	put_value		10,12
	execute		10,parse_error_10_0
check_parse_10_21:
	read_elements_inc		6,1,12,2
	collect_value		8
	collect_value		13
	collect_vector		6
	put_atom		6,syntax_error
	put_values_inc		8,9,2
	put_value		10,12
	execute		10,parse_error_10_0
check_parse_10_22:
	read_elements_inc		6,1,12,2
	collect_value		8
	collect_value		12
	collect_vector		6
	put_variable		6,8
	put_variable		12,11
	b_subtract		6,12,6
	create_goal		10
	set_values_inc		1,1,5
	set_atom		6,syntax_error
	set_value		7,7
	set_value		8,9
	set_marked_value		9,10
	set_value		10,6
	enqueue_goal		10,parse_error_10_0
	create_goal		2
	set_value		1,13
	set_value		2,11
	enqueue_goal		2,elements_2_0
	put_value		1,10
	put_value		2,8
	execute		2,elements_2_0
check_parse_10_1:
	suspend		check_parse_10_0
	module_entry		mpimos_file
	predicate		parse_error,10
parse_error_10_0:
	try_me_else		parse_error_10_1
	vector		7
	jump_on_arity		7,5,parse_error_10_1
	table_entry		parse_error_10_1
	table_entry		parse_error_10_1
	table_entry		parse_error_10_3
	table_entry		parse_error_10_4
	table_entry		parse_error_10_5
parse_error_10_3:
	read_element		7,0,11
	wait_atom		11,gett
	read_element		7,1,11
	collect_value		8
	put_integer		8,1
	b_vector_element		5,8,5,8
	create_goal		5
	put_reused_func		7,7,gett
	write_element_value		7,1,11
	put_list_val_val		11,7,1
	set_value		1,11
	set_values_inc		2,2,3
	set_value		5,8
	enqueue_goal		5,read_mode_5_0
	put_value		1,6
	put_values_inc		2,9,2
	put_value		4,5
	execute		4,display_parse_error_4_0
parse_error_10_4:
	read_element		7,0,11
	atom		11
	branch_on_atom		11,2,parse_error_10_1
	bucket_entry_a		getft,parse_error_10_7
	bucket_entry_a		gett,parse_error_10_8
parse_error_10_7:
	read_elements_inc		7,1,12,2
	collect_value		8
	put_integer		8,1
	b_vector_element		5,8,5,8
	create_goal		5
	put_reused_func		7,7,getft
	write_elements_inc		7,1,12,2
	put_list_val_val		11,7,1
	set_value		1,11
	set_values_inc		2,2,3
	set_value		5,8
	enqueue_goal		5,read_mode_5_0
	put_value		1,6
	put_values_inc		2,9,2
	put_value		4,5
	execute		4,display_parse_error_4_0
parse_error_10_8:
	read_elements_inc		7,1,12,2
	collect_value		8
	collect_vector		7
	get_value		12,9
	put_vector		7,2
	write_element_value		7,0,6
	write_element_value		7,1,10
	get_vector_value		13,7
	execute		5,read_mode_5_0
parse_error_10_5:
	read_element		7,0,11
	atom		11
	branch_on_atom		11,2,parse_error_10_1
	bucket_entry_a		getet,parse_error_10_10
	bucket_entry_a		getft,parse_error_10_11
parse_error_10_10:
	read_elements_inc		7,1,12,3
	collect_vector		7
	get_value		12,9
	get_value		13,8
	put_vector		7,2
	write_element_value		7,0,6
	write_element_value		7,1,10
	get_vector_value		14,7
	execute		5,read_mode_5_0
parse_error_10_11:
	read_elements_inc		7,1,12,3
	collect_vector		7
	get_value		12,9
	get_value		13,8
	put_vector		7,2
	write_element_value		7,0,6
	write_element_value		7,1,10
	get_vector_value		14,7
	execute		5,read_mode_5_0
parse_error_10_1:
	suspend		parse_error_10_0
	module_entry		mpimos_file
	predicate		display_parse_error,4
display_parse_error_4_0:
	create_goal		4
	set_atom		1,warning
	set_value		2,4
	set_atom		3,r
	put_func		4,2,do
	write_element_variable		4,1,7
	put_list		5
	write_car_value		5,4
	write_cdr_nil		5
	put_structured_constant		4,'$SCNST_4'
	put_list_val_val		6,4,5
	put_func		4,2,putb
	write_element_variable		4,1,8
	put_list_val_val		5,4,6
	put_structured_constant		4,'$SCNST_5'
	put_list_val_val		6,4,5
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,6
	set_value		4,4
	enqueue_goal		4,raise_error_4_0
	create_goal		2
	set_value		1,1
	set_value		2,8
	enqueue_goal		2,message_2_0
	put_values_inc		1,2,2
	put_value		3,7
	execute_external		mpimos_utility,report_tokens,3
display_parse_error_4_1:
	suspend		display_parse_error_4_0
	module_entry		mpimos_file
	predicate		elements,2
elements_2_0:
	put_integer		3,0
	execute		3,elements_3_0
elements_2_1:
	suspend		elements_2_0
	module_entry		mpimos_file
	predicate		elements,3
elements_3_0:
	try_me_else		elements_3_1
	jump_on_non_list_var_var		1,elements_3_3,4,5
	collect_list		1
	collect_value		4
	b_increment		3,1
	put_value		3,1
	put_value		1,5
	execute		3,elements_3_0
elements_3_3:
	check_nil		1,elements_3_1
	get_value		2,3
	proceed
elements_3_1:
	suspend		elements_3_0
	module_entry		mpimos_file
	predicate		write_mode,8
write_mode_8_0:
	try_me_else		write_mode_8_1
	jump_on_non_list		1,write_mode_8_3
	read_car		1,9
	jump_on_non_atom		9,write_mode_8_5
	test_atom		9,nl,write_mode_8_1
	read_cdr		1,10
	collect_list		1
	put_value		1,10
	put_integer		9,10
	execute		9,set_char_9_0
write_mode_8_5:
	is_vector		9,write_mode_8_1
	jump_on_arity		9,5,write_mode_8_1
	table_entry		write_mode_8_1
	table_entry		write_mode_8_1
	table_entry		write_mode_8_6
	table_entry		write_mode_8_7
	table_entry		write_mode_8_8
write_mode_8_6:
	read_element		9,0,10
	atom		10
	hash_on_atom		10,20,write_mode_8_1
	bucket_entry_a		buffer_length,write_mode_8_10
	bucket_entry_a		change_op_pool,write_mode_8_11
	bucket_entry_a		close,write_mode_8_12
	bucket_entry_a		do,write_mode_8_13
	bucket_entry_a		flush,write_mode_8_14
	bucket_entry_a		getc,write_mode_8_15
	bucket_entry_a		getl,write_mode_8_16
	bucket_entry_a		gett,write_mode_8_17
	bucket_entry_a		print_depth,write_mode_8_18
	bucket_entry_a		print_length,write_mode_8_19
	bucket_entry_a		print_var_mode,write_mode_8_20
	bucket_entry_a		putb,write_mode_8_21
	bucket_entry_a		putc,write_mode_8_22
	bucket_entry_a		putet,write_mode_8_23
	bucket_entry_a		putl,write_mode_8_24
	bucket_entry_a		putt,write_mode_8_25
	bucket_entry_a		puttq,write_mode_8_26
	bucket_entry_a		remove_op,write_mode_8_27
	bucket_entry_a		skip,write_mode_8_28
	bucket_entry_a		tab,write_mode_8_29
write_mode_8_10:
	read_cdr		1,11
	read_element		9,1,12
	integer		12
	put_integer		13,0
	g_less_than		13,12
	collect_list		1
	collect_value		7
	collect_vector		9
	put_integer		1,5
	put_marked_value		7,12
	b_set_vector_element		5,1,1,7,5
	put_integer		1,8
	b_new_string		7,12,1
	put_integer		1,0
	b_substring		6,1,8,9,1
	put_value		1,11
	put_value		6,7
	put_value		7,12
	put_integer		8,0
	execute		9,set_string_9_0
write_mode_8_11:
	read_cdr		1,11
	read_element		9,1,12
	collect_vector		9
	put_func		9,3,replace_operator_pool
	write_element_void		9,1
	write_element_value		9,2,12
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	execute		8,write_mode_8_0
write_mode_8_12:
	read_cdr		1,11
	read_element		9,1,12
	collect_value		7
	put_integer		7,0
	b_substring		6,7,8,6,7
	put_reused_func		7,9,close
	write_element_variable		7,1,9
	put_reused_list_val_var		1,1,7,8
	put_func		7,3,putb
	write_element_value		7,1,6
	write_element_void		7,2
	put_list_val_val		6,7,1
	get_list_value		2,6
	put_integer		1,2
	b_consume_resource		1
	put_value		1,11
	put_value		2,8
	put_value		6,9
	put_value		7,12
	execute		7,wait_close_7_0
write_mode_8_13:
	read_element		9,1,11
	jump_on_non_list		11,write_mode_8_31
	read_cdr		1,12
	read_car		11,10
	read_cdr		11,13
	collect_list		11
	collect_vector		9
	create_goal		8
	set_variable		1,9
	set_values_inc		2,2,7
	enqueue_goal		8,write_mode_8_0
	put_reused_list_val_val		1,1,10,13
	put_value		2,12
	put_value		3,9
	execute		3,append_3_0
write_mode_8_31:
	check_nil		11,write_mode_8_1
	read_cdr		1,12
	collect_list		1
	collect_vector		9
	put_value		1,12
	execute		8,write_mode_8_0
write_mode_8_14:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	put_value		10,2
	create_goal		10
	set_value		1,11
	set_variable		2,9
	set_values_inc		3,3,3
	set_variable		6,4
	set_value		7,7
	set_integer		8,0
	set_variable		9,7
	set_value		10,12
	enqueue_goal		10,wait_write_10_0
	put_value		1,6
	put_value		2,8
	put_value		3,10
	put_value		5,9
	put_value		6,7
	execute		6,flush_buffer_6_0
write_mode_8_15:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_func		9,9,getc
	write_element_value		9,1,12
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_16:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_func		9,9,getl
	write_element_value		9,1,12
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_17:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_func		9,9,gett
	write_element_value		9,1,12
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_18:
	read_cdr		1,11
	read_element		9,1,12
	integer		12
	put_integer		13,0
	g_less_than		13,12
	put_reused_func		9,9,print_depth
	write_element_marked_value		9,1,12
	get_reused_list_val_var		4,1,1,9,9
	put_integer		1,4
	b_set_vector_element		5,1,1,12,5
	put_value		1,11
	put_value		4,9
	execute		8,write_mode_8_0
write_mode_8_19:
	read_cdr		1,11
	read_element		9,1,12
	integer		12
	put_integer		13,0
	g_less_than		13,12
	put_reused_func		9,9,print_length
	write_element_marked_value		9,1,12
	get_reused_list_val_var		4,1,1,9,9
	put_integer		1,3
	b_set_vector_element		5,1,1,12,5
	put_value		1,11
	put_value		4,9
	execute		8,write_mode_8_0
write_mode_8_20:
	read_cdr		1,11
	read_element		9,1,12
	atom		12
	put_reused_func		9,9,print_var_mode
	write_element_value		9,1,12
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,11
	put_value		4,9
	execute		8,write_mode_8_0
write_mode_8_21:
	read_cdr		1,11
	read_element		9,1,12
	string		12
	g_string		12,13,14
	wait_integer		14,8
	collect_list		1
	collect_vector		9
	put_value		1,11
	put_value		9,12
	execute		9,set_string_9_0
write_mode_8_22:
	read_cdr		1,11
	read_element		9,1,12
	integer		12
	put_integer		13,0
	g_not_less_than		12,13
	put_integer		13,255
	g_not_less_than		13,12
	collect_list		1
	collect_vector		9
	put_value		1,11
	put_value		9,12
	execute		9,set_char_9_0
write_mode_8_23:
	read_cdr		1,11
	read_element		9,1,12
	wait		12
	collect_vector		9
	put_func		9,3,putet
	write_element_value		9,1,12
	write_element_variable		9,2,10
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,11
	put_value		4,9
	put_value		9,10
	execute		9,set_string_list_9_0
write_mode_8_24:
	read_cdr		1,11
	read_element		9,1,12
	string		12
	g_string		12,13,14
	wait_integer		14,8
	collect_vector		9
	put_reused_list		1,1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_value		9,12
	execute		9,set_string_9_0
write_mode_8_25:
	read_cdr		1,11
	read_element		9,1,12
	wait		12
	collect_vector		9
	put_func		9,3,putt
	write_element_value		9,1,12
	write_element_variable		9,2,10
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,11
	put_value		4,9
	put_value		9,10
	execute		9,set_string_list_9_0
write_mode_8_26:
	read_cdr		1,11
	read_element		9,1,12
	wait		12
	collect_vector		9
	put_func		9,3,puttq
	write_element_value		9,1,12
	write_element_variable		9,2,10
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,11
	put_value		4,9
	put_value		9,10
	execute		9,set_string_list_9_0
write_mode_8_27:
	read_cdr		1,11
	read_element		9,1,12
	atom		12
	collect_vector		9
	put_func		9,3,remove_operator
	write_element_value		9,1,12
	write_element_variable		9,2,10
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	put_value		9,10
	execute		9,check_op_9_0
write_mode_8_28:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_func		9,9,skip
	write_element_value		9,1,12
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_29:
	read_cdr		1,11
	read_element		9,1,12
	integer		12
	put_integer		13,0
	g_not_less_than		12,13
	put_integer		13,1000
	g_less_than		12,13
	collect_list		1
	collect_vector		9
	put_value		1,11
	put_value		9,12
	execute		9,tab_9_0
write_mode_8_7:
	read_element		9,0,10
	atom		10
	hash_on_atom		10,6,write_mode_8_1
	bucket_entry_a		getb,write_mode_8_33
	bucket_entry_a		getft,write_mode_8_34
	bucket_entry_a		gett,write_mode_8_35
	bucket_entry_a		operator,write_mode_8_36
	bucket_entry_a		putb,write_mode_8_37
	bucket_entry_a		replace_op_pool,write_mode_8_38
write_mode_8_33:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	put_reused_func		9,9,getb
	write_elements_inc		9,1,12,2
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_34:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	put_reused_func		9,9,getft
	write_elements_inc		9,1,12,2
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_35:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	put_reused_func		9,9,gett
	write_elements_inc		9,1,12,2
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_36:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	atom		12
	put_reused_func		9,9,operator
	write_elements_inc		9,1,12,2
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	execute		8,write_mode_8_0
write_mode_8_37:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	string		12
	g_string		12,14,15
	wait_integer		15,8
	integer		13
	put_integer		15,0
	g_not_less_than		13,15
	collect_list		1
	collect_vector		9
	create_goal		9
	set_value		1,11
	set_values_inc		2,2,7
	set_variable		9,4
	enqueue_goal		9,set_string_9_0
	put_value		1,12
	put_values_dec		2,14,2
	execute		4,get_buffer_4_0
write_mode_8_38:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	put_reused_func		9,9,replace_operator_pool
	write_elements_inc		9,1,12,2
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	execute		8,write_mode_8_0
write_mode_8_8:
	read_element		9,0,10
	atom		10
	hash_on_atom		10,7,write_mode_8_1
	bucket_entry_a		add_op,write_mode_8_40
	bucket_entry_a		getet,write_mode_8_41
	bucket_entry_a		getft,write_mode_8_42
	bucket_entry_a		putet,write_mode_8_43
	bucket_entry_a		putt,write_mode_8_44
	bucket_entry_a		puttq,write_mode_8_45
	bucket_entry_a		remove_op,write_mode_8_46
write_mode_8_40:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	integer		12
	put_integer		15,1
	g_not_less_than		12,15
	put_integer		15,1200
	g_not_less_than		15,12
	atom		13
	atom		14
	collect_vector		9
	put_func		9,5,add_operator
	write_elements_inc		9,1,12,3
	write_element_variable		9,4,10
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	put_value		9,10
	execute		9,check_op_9_0
write_mode_8_41:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	collect_list		1
	put_reused_func		9,9,getet
	write_elements_inc		9,1,12,3
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_42:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	collect_list		1
	put_reused_func		9,9,getft
	write_elements_inc		9,1,12,3
	put_value		1,11
	execute		9,write_mode_error_9_0
write_mode_8_43:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	wait		12
	integer		13
	put_integer		15,0
	g_less_than		15,13
	integer		14
	put_integer		15,0
	g_less_than		15,14
	collect_vector		9
	put_integer		9,3
	b_vector_element		5,9,5,9
	put_integer		10,4
	b_vector_element		9,10,9,10
	put_func		15,2,print_depth
	write_element_value		15,1,9
	put_reused_list_val_var		1,1,15,15
	put_func		9,2,print_length
	write_element_value		9,1,5
	put_list_val_val		5,9,1
	put_func		1,3,putet
	write_element_value		1,1,12
	write_element_variable		1,2,12
	put_list_val_val		9,1,5
	put_func		1,2,print_depth
	write_element_value		1,1,14
	put_list_val_val		5,1,9
	put_func		1,2,print_length
	write_element_value		1,1,13
	put_list_val_val		9,1,5
	get_list_value		4,9
	put_value		1,11
	put_value		4,15
	put_value		5,10
	put_value		9,12
	execute		9,set_string_list_9_0
write_mode_8_44:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	wait		12
	integer		13
	put_integer		15,0
	g_less_than		15,13
	integer		14
	put_integer		15,0
	g_less_than		15,14
	collect_vector		9
	put_integer		9,3
	b_vector_element		5,9,5,9
	put_integer		10,4
	b_vector_element		9,10,9,10
	put_func		15,2,print_depth
	write_element_value		15,1,9
	put_reused_list_val_var		1,1,15,15
	put_func		9,2,print_length
	write_element_value		9,1,5
	put_list_val_val		5,9,1
	put_func		1,3,putt
	write_element_value		1,1,12
	write_element_variable		1,2,12
	put_list_val_val		9,1,5
	put_func		1,2,print_depth
	write_element_value		1,1,14
	put_list_val_val		5,1,9
	put_func		1,2,print_length
	write_element_value		1,1,13
	put_list_val_val		9,1,5
	get_list_value		4,9
	put_value		1,11
	put_value		4,15
	put_value		5,10
	put_value		9,12
	execute		9,set_string_list_9_0
write_mode_8_45:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	wait		12
	integer		13
	put_integer		15,0
	g_less_than		15,13
	integer		14
	put_integer		15,0
	g_less_than		15,14
	collect_vector		9
	put_integer		9,3
	b_vector_element		5,9,5,9
	put_integer		10,4
	b_vector_element		9,10,9,10
	put_func		15,2,print_depth
	write_element_value		15,1,9
	put_reused_list_val_var		1,1,15,15
	put_func		9,2,print_length
	write_element_value		9,1,5
	put_list_val_val		5,9,1
	put_func		1,3,puttq
	write_element_value		1,1,12
	write_element_variable		1,2,12
	put_list_val_val		9,1,5
	put_func		1,2,print_depth
	write_element_value		1,1,14
	put_list_val_val		5,1,9
	put_func		1,2,print_length
	write_element_value		1,1,13
	put_list_val_val		9,1,5
	get_list_value		4,9
	put_value		1,11
	put_value		4,15
	put_value		5,10
	put_value		9,12
	execute		9,set_string_list_9_0
write_mode_8_46:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	integer		12
	put_integer		15,1
	g_not_less_than		12,15
	put_integer		15,1200
	g_not_less_than		15,12
	atom		13
	atom		14
	collect_vector		9
	put_func		9,5,remove_operator
	write_elements_inc		9,1,12,3
	write_element_variable		9,4,10
	get_reused_list_val_var		3,1,1,9,9
	put_value		1,11
	put_value		3,9
	put_value		9,10
	execute		9,check_op_9_0
write_mode_8_3:
	check_nil		1,write_mode_8_1
	collect_value		7
	put_integer		1,0
	b_substring		6,1,8,1,6
	put_func		6,3,putb
	write_element_value		6,1,1
	write_element_variable		6,2,1
	put_list		7
	write_car_value		7,6
	write_cdr_nil		7
	get_list_value		2,7
	put_integer		2,2
	b_consume_resource		2
	get_nil		3
	get_nil		4
	put_value		2,5
	execute		2,wait_2_0
write_mode_8_1:
	otherwise		write_mode_8_0
	try_me_else		write_mode_8_65
	wait_list_var_var		1,9,10
	collect_list		1
	create_goal		8
	set_value		1,10
	set_values_inc		2,2,3
	set_variable		5,10
	set_values_inc		6,6,3
	enqueue_goal		8,write_mode_8_0
	put_atom		1,warning
	put_atom		2,illegal_command
	put_value		3,9
	put_value		4,5
	put_value		5,10
	execute		5,command_error_5_0
write_mode_8_65:
	otherwise		write_mode_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		4
	collect_value		3
	collect_value		2
	put_value		3,1
	put_atom		1,error
	put_atom		2,not_command_stream
	put_value		4,5
	put_void		5
	execute		5,command_error_5_0
write_mode_8_69:
	suspend		write_mode_8_0
	module_entry		mpimos_file
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
	module_entry		mpimos_file
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
	module_entry		mpimos_file
	predicate		wait_write,10
wait_write_10_0:
	try_me_else		wait_write_10_1
	atom		9
	branch_on_atom		9,2,wait_write_10_1
	bucket_entry_a		'fep#abnormal',wait_write_10_3
	bucket_entry_a		'fep#normal',wait_write_10_4
wait_write_10_3:
	get_atom		10,done
	create_goal		8
	set_values_inc		1,1,4
	set_variable		5,2
	set_values_inc		6,6,3
	enqueue_goal		8,write_mode_8_0
	put_value		1,5
	execute		2,cannot_write_2_0
wait_write_10_4:
	get_atom		10,done
	execute		8,write_mode_8_0
wait_write_10_1:
	suspend		wait_write_10_0
	module_entry		mpimos_file
	predicate		wait,2
wait_2_0:
	try_me_else		wait_2_1
	atom		1
	branch_on_atom		1,2,wait_2_1
	bucket_entry_a		'fep#abnormal',wait_2_3
	bucket_entry_a		'fep#normal',wait_2_4
wait_2_3:
	put_value		1,2
	put_void		2
	execute		2,cannot_write_2_0
wait_2_4:
	collect_value		2
	proceed
wait_2_1:
	suspend		wait_2_0
	module_entry		mpimos_file
	predicate		write_mode_error,9
write_mode_error_9_0:
	create_goal		8
	set_values_inc		1,1,4
	set_variable		5,10
	set_values_inc		6,6,3
	enqueue_goal		8,write_mode_8_0
	put_atom		1,warning
	put_atom		2,not_read_mode
	put_value		3,9
	put_value		4,5
	put_value		5,10
	execute		5,command_error_5_0
write_mode_error_9_1:
	suspend		write_mode_error_9_0
	module_entry		mpimos_file
	predicate		set_char,9
set_char_9_0:
	try_me_else		set_char_9_1
	integer		7
	integer		8
	g_less_than		8,7
	put_marked_value		10,8
	b_set_string_element		6,10,9,6
	b_increment		8,8
	execute		8,write_mode_8_0
set_char_9_1:
	try_me_else		set_char_9_3
	wait_value		7,8
	collect_value		8
	put_value		11,2
	put_variable		2,10
	put_integer		8,0
	b_set_string_element		2,8,9,2
	create_goal		10
	set_value		1,1
	set_variable		2,9
	set_values_inc		3,3,3
	set_value		6,2
	set_marked_value		7,7
	set_integer		8,1
	set_variable		9,8
	set_void		10
	enqueue_goal		10,wait_write_10_0
	put_values_inc		1,6,2
	put_values_dec		3,11,4
	execute		6,flush_buffer_6_0
set_char_9_3:
	suspend		set_char_9_0
	module_entry		mpimos_file
	predicate		tab,9
tab_9_0:
	try_me_else		tab_9_1
	wait_integer		9,0
	execute		8,write_mode_8_0
tab_9_1:
	otherwise		tab_9_0
	try_me_else		tab_9_6
	integer		7
	integer		8
	g_less_than		8,7
	put_marked_value		10,8
	put_integer		11,32
	b_set_string_element		6,10,11,6
	b_increment		8,8
	b_decrement		9,9
	execute		9,tab_9_0
tab_9_6:
	try_me_else		tab_9_8
	wait_value		7,8
	collect_value		8
	put_value		11,2
	create_goal		9
	set_value		1,1
	set_variable		2,10
	set_values_inc		3,3,3
	set_variable		6,4
	set_marked_value		7,7
	set_variable		8,8
	set_value		9,9
	enqueue_goal		9,wait_tab_write_9_0
	put_values_inc		1,6,2
	put_value		3,11
	put_value		5,10
	put_value		6,8
	execute		6,flush_buffer_6_0
tab_9_8:
	suspend		tab_9_0
	module_entry		mpimos_file
	predicate		wait_tab_write,9
wait_tab_write_9_0:
	try_me_else		wait_tab_write_9_1
	atom		8
	branch_on_atom		8,2,wait_tab_write_9_1
	bucket_entry_a		'fep#abnormal',wait_tab_write_9_3
	bucket_entry_a		'fep#normal',wait_tab_write_9_4
wait_tab_write_9_3:
	create_goal		9
	set_values_inc		1,1,4
	set_variable		5,2
	set_values_inc		6,6,2
	set_integer		8,0
	set_value		9,9
	enqueue_goal		9,tab_9_0
	put_value		1,5
	execute		2,cannot_write_2_0
wait_tab_write_9_4:
	put_integer		8,0
	execute		9,tab_9_0
wait_tab_write_9_1:
	suspend		wait_tab_write_9_0
	module_entry		mpimos_file
	predicate		set_string,9
set_string_9_0:
	try_me_else		set_string_9_1
	string		9
	try_me_else		set_string_9_3
	g_string		9,10,11
	wait_integer		10,0
	wait_integer		11,8
	collect_value		9
	execute		8,write_mode_8_0
set_string_9_3:
	try_me_else		set_string_9_1
	g_string		9,10,11
	wait_integer		11,8
	put_integer		11,0
	g_less_than		11,10
	put_marked_value		11,7
	put_marked_value		12,8
	b_subtract		11,12,11
	execute		11,set_string_11_0
set_string_9_1:
	suspend		set_string_9_0
	module_entry		mpimos_file
	predicate		set_string,11
set_string_11_0:
	try_me_else		set_string_11_1
	wait_integer		11,0
	collect_value		8
	put_value		12,2
	create_goal		10
	set_value		1,1
	set_variable		2,11
	set_values_inc		3,3,3
	set_variable		6,4
	set_marked_value		7,7
	set_variable		8,8
	set_values_inc		9,9,2
	enqueue_goal		10,wait_putb_10_0
	put_values_inc		1,6,2
	put_value		3,12
	put_value		5,11
	put_value		6,8
	execute		6,flush_buffer_6_0
set_string_11_1:
	otherwise		set_string_11_0
	try_me_else		set_string_11_6
	integer		10
	integer		11
	try_me_else		set_string_11_9
	g_not_less_than		11,10
	put_marked_value		11,8
	b_set_substring		6,11,9,6
	b_add		8,10,8
	execute		8,write_mode_8_0
set_string_11_9:
	put_value		12,2
	put_integer		2,0
	put_marked_value		13,11
	b_substring		9,2,13,2,9
	b_set_substring		6,8,2,2
	b_subtract		10,11,6
	put_marked_value		8,6
	b_substring		9,11,8,8,9
	create_goal		10
	set_value		1,1
	set_variable		2,10
	set_values_inc		3,3,3
	set_variable		6,4
	set_marked_value		7,7
	set_variable		8,9
	set_value		9,8
	set_value		10,6
	enqueue_goal		10,wait_putb_10_0
	put_value		1,2
	put_value		2,7
	put_value		3,12
	put_values_dec		5,10,2
	execute		6,flush_buffer_6_0
set_string_11_6:
	suspend		set_string_11_0
	module_entry		mpimos_file
	predicate		wait_putb,10
wait_putb_10_0:
	try_me_else		wait_putb_10_1
	atom		8
	branch_on_atom		8,2,wait_putb_10_1
	bucket_entry_a		'fep#abnormal',wait_putb_10_3
	bucket_entry_a		'fep#normal',wait_putb_10_4
wait_putb_10_3:
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,2
	set_value		6,6
	set_marked_value		7,7
	set_integer		8,0
	set_values_inc		9,9,2
	set_value		11,7
	enqueue_goal		11,set_string_11_0
	put_value		1,5
	execute		2,cannot_write_2_0
wait_putb_10_4:
	put_value		11,7
	put_marked_value		7,11
	put_integer		8,0
	execute		11,set_string_11_0
wait_putb_10_1:
	suspend		wait_putb_10_0
	module_entry		mpimos_file
	predicate		set_string_list,9
set_string_list_9_0:
	try_me_else		set_string_list_9_1
	jump_on_non_list		9,set_string_list_9_3
	read_car		9,10
	string		10
	read_cdr		9,11
	try_me_else		set_string_list_9_5
	g_string		10,12,13
	wait_integer		12,0
	wait_integer		13,8
	collect_list		9
	collect_value		10
	put_value		9,11
	execute		9,set_string_list_9_0
set_string_list_9_5:
	try_me_else		set_string_list_9_1
	g_string		10,12,13
	wait_integer		13,8
	put_integer		13,0
	g_less_than		13,12
	collect_list		9
	put_marked_value		9,7
	put_marked_value		13,8
	b_subtract		9,13,9
	put_value		13,9
	put_value		9,11
	put_values_inc		11,12,2
	execute		12,set_string_list_12_0
set_string_list_9_3:
	check_nil		9,set_string_list_9_1
	execute		8,write_mode_8_0
set_string_list_9_1:
	suspend		set_string_list_9_0
	module_entry		mpimos_file
	predicate		set_string_list,12
set_string_list_12_0:
	try_me_else		set_string_list_12_1
	wait_integer		12,0
	collect_value		8
	put_value		13,2
	create_goal		11
	set_value		1,1
	set_variable		2,12
	set_values_inc		3,3,3
	set_variable		6,4
	set_marked_value		7,7
	set_variable		8,8
	set_values_inc		9,9,3
	enqueue_goal		11,wait_list_putb_11_0
	put_values_inc		1,6,2
	put_value		3,13
	put_value		5,12
	put_value		6,8
	execute		6,flush_buffer_6_0
set_string_list_12_1:
	otherwise		set_string_list_12_0
	try_me_else		set_string_list_12_6
	integer		11
	integer		12
	try_me_else		set_string_list_12_9
	g_not_less_than		12,11
	put_marked_value		12,8
	b_set_substring		6,12,10,6
	b_add		8,11,8
	execute		9,set_string_list_9_0
set_string_list_12_9:
	put_value		13,2
	put_integer		2,0
	put_marked_value		14,12
	b_substring		10,2,14,2,10
	b_set_substring		6,8,2,2
	b_subtract		11,12,6
	put_marked_value		8,6
	b_substring		10,12,8,8,10
	create_goal		11
	set_value		1,1
	set_variable		2,11
	set_values_inc		3,3,3
	set_variable		6,4
	set_marked_value		7,7
	set_variable		8,10
	set_values_dec		9,9,2
	set_value		11,6
	enqueue_goal		11,wait_list_putb_11_0
	put_value		1,2
	put_value		2,7
	put_value		3,13
	put_values_dec		5,11,2
	execute		6,flush_buffer_6_0
set_string_list_12_6:
	suspend		set_string_list_12_0
	module_entry		mpimos_file
	predicate		wait_list_putb,11
wait_list_putb_11_0:
	try_me_else		wait_list_putb_11_1
	atom		8
	branch_on_atom		8,2,wait_list_putb_11_1
	bucket_entry_a		'fep#abnormal',wait_list_putb_11_3
	bucket_entry_a		'fep#normal',wait_list_putb_11_4
wait_list_putb_11_3:
	create_goal		12
	set_values_inc		1,1,4
	set_variable		5,2
	set_value		6,6
	set_marked_value		7,7
	set_integer		8,0
	set_values_inc		9,9,3
	set_value		12,7
	enqueue_goal		12,set_string_list_12_0
	put_value		1,5
	execute		2,cannot_write_2_0
wait_list_putb_11_4:
	put_value		12,7
	put_marked_value		7,12
	put_integer		8,0
	execute		12,set_string_list_12_0
wait_list_putb_11_1:
	suspend		wait_list_putb_11_0
	module_entry		mpimos_file
	predicate		wait_close,7
wait_close_7_0:
	try_me_else		wait_close_7_1
	wait_atom		6,'fep#normal'
	get_atom		7,success
	execute		5,closed_5_0
wait_close_7_1:
	suspend		wait_close_7_0
	module_entry		mpimos_file
	predicate		closed,5
closed_5_0:
	try_me_else		closed_5_1
	jump_on_non_list_var_var		1,closed_5_3,6,7
	collect_list		1
	create_goal		5
	set_value		1,7
	set_values_inc		2,2,3
	set_variable		5,7
	enqueue_goal		5,closed_5_0
	put_atom		1,warning
	put_atom		2,file_not_open
	put_values_dec		3,6,2
	put_value		5,7
	execute		5,command_error_5_0
closed_5_3:
	check_nil		1,closed_5_1
	collect_value		5
	get_nil		2
	get_nil		3
	get_nil		4
	proceed
closed_5_1:
	suspend		closed_5_0
	module_entry		mpimos_file
	predicate		check_op,6
check_op_6_0:
	try_me_else		check_op_6_1
	vector		6
	jump_on_arity		6,5,check_op_6_1
	table_entry		check_op_6_1
	table_entry		check_op_6_1
	table_entry		check_op_6_3
	table_entry		check_op_6_1
	table_entry		check_op_6_4
check_op_6_3:
	read_element		6,0,7
	wait_atom		7,not_find
	read_element		6,1,7
	collect_vector		6
	create_goal		5
	set_values_inc		1,1,4
	set_variable		5,6
	enqueue_goal		5,read_mode_5_0
	put_func		3,4,remove_op
	write_element_void		3,1
	write_element_void		3,2
	write_element_value		3,3,7
	put_atom		1,warning
	put_atom		2,operator_not_found
	put_values_inc		4,5,2
	execute		5,command_error_5_0
check_op_6_4:
	read_element		6,0,7
	wait_atom		7,not_find
	read_elements_inc		6,1,7,3
	create_goal		5
	set_values_inc		1,1,4
	set_variable		5,10
	enqueue_goal		5,read_mode_5_0
	put_reused_func		3,6,remove_op
	write_elements_inc		3,1,7,3
	put_atom		1,warning
	put_atom		2,operator_not_found
	put_value		4,5
	put_value		5,10
	execute		5,command_error_5_0
check_op_6_1:
	otherwise		check_op_6_0
	collect_value		6
	execute		5,read_mode_5_0
check_op_6_7:
	suspend		check_op_6_0
	module_entry		mpimos_file
	predicate		check_op,9
check_op_9_0:
	try_me_else		check_op_9_1
	wait_vector		9,4
	read_element		9,0,10
	wait_atom		10,not_find
	read_elements_inc		9,1,10,3
	create_goal		8
	set_values_inc		1,1,4
	set_variable		5,13
	set_values_inc		6,6,3
	enqueue_goal		8,write_mode_8_0
	put_reused_func		3,9,remove_op
	write_elements_inc		3,1,10,3
	put_atom		1,warning
	put_atom		2,operator_not_found
	put_value		4,5
	put_value		5,13
	execute		5,command_error_5_0
check_op_9_1:
	otherwise		check_op_9_0
	collect_value		9
	execute		8,write_mode_8_0
check_op_9_6:
	suspend		check_op_9_0
	module_entry		mpimos_file
	predicate		command_error,5
command_error_5_0:
	put_integer		6,1
	b_vector_element		4,6,4,6
	put_integer		7,2
	b_vector_element		6,7,6,7
	get_value		7,5
	create_goal		4
	set_value		1,1
	set_value		2,4
	set_value		3,6
	put_func		1,2,putt
	write_element_variable		1,1,7
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_structured_constant		1,'$SCNST_6'
	put_list_val_val		5,1,4
	put_func		1,2,putb
	write_element_variable		1,1,6
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		5,1,4
	set_value		4,5
	enqueue_goal		4,raise_error_4_0
	create_goal		2
	set_value		1,3
	set_value		2,7
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,2
	put_value		2,6
	execute		2,message_2_0
command_error_5_1:
	suspend		command_error_5_0
	module_entry		mpimos_file
	predicate		cannot_write,2
cannot_write_2_0:
	put_integer		3,1
	b_vector_element		1,3,3,1
	put_integer		4,2
	b_vector_element		1,4,4,1
	get_value		1,2
	put_atom		1,warning
	put_values_inc		2,3,2
	put_structured_constant		4,'$SCNST_8'
	execute		4,raise_error_4_0
cannot_write_2_1:
	suspend		cannot_write_2_0
	module_entry		mpimos_file
	predicate		raise_error,4
raise_error_4_0:
	put_integer		7,262144
	put_structured_constant		5,'$SCNST_9'
	put_func		6,2,do
	write_element_value		6,1,4
	put_list_val_val		4,6,5
	put_structured_constant		5,'$SCNST_10'
	put_list_val_val		6,5,4
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,6
	put_structured_constant		4,'$SCNST_11'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,5
	put_structured_constant		3,'$SCNST_12'
	put_list_val_val		4,3,2
	b_raise		7,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_4_1:
	suspend		raise_error_4_0
	module_entry		mpimos_file
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	atom		1
	hash_on_atom		1,13,message_2_1
	bucket_entry_a		ambiguous,message_2_3
	bucket_entry_a		bad_file_name_type,message_2_4
	bucket_entry_a		bad_open_mode,message_2_5
	bucket_entry_a		bad_open_mode_type,message_2_6
	bucket_entry_a		cannot_open_file,message_2_7
	bucket_entry_a		eof_in_quote,message_2_8
	bucket_entry_a		file_not_open,message_2_9
	bucket_entry_a		illegal_command,message_2_10
	bucket_entry_a		not_command_stream,message_2_11
	bucket_entry_a		not_read_mode,message_2_12
	bucket_entry_a		not_write_mode,message_2_13
	bucket_entry_a		operator_not_found,message_2_14
	bucket_entry_a		syntax_error,message_2_15
message_2_3:
	put_structured_constant		1,'$SCNST_13'
	get_value		2,1
	proceed
message_2_4:
	put_structured_constant		1,'$SCNST_14'
	get_value		2,1
	proceed
message_2_5:
	put_structured_constant		1,'$SCNST_15'
	get_value		2,1
	proceed
message_2_6:
	put_structured_constant		1,'$SCNST_16'
	get_value		2,1
	proceed
message_2_7:
	put_structured_constant		1,'$SCNST_17'
	get_value		2,1
	proceed
message_2_8:
	put_structured_constant		1,'$SCNST_18'
	get_value		2,1
	proceed
message_2_9:
	put_structured_constant		1,'$SCNST_19'
	get_value		2,1
	proceed
message_2_10:
	put_structured_constant		1,'$SCNST_20'
	get_value		2,1
	proceed
message_2_11:
	put_structured_constant		1,'$SCNST_21'
	get_value		2,1
	proceed
message_2_12:
	put_structured_constant		1,'$SCNST_22'
	get_value		2,1
	proceed
message_2_13:
	put_structured_constant		1,'$SCNST_23'
	get_value		2,1
	proceed
message_2_14:
	put_structured_constant		1,'$SCNST_24'
	get_value		2,1
	proceed
message_2_15:
	put_structured_constant		1,'$SCNST_25'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	module_entry		mpimos_file
	predicate		append,3
append_3_0:
	try_me_else		append_3_1
	jump_on_non_list_var_var		1,append_3_3,4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		3,4
	execute		3,append_3_0
append_3_3:
	check_nil		1,append_3_1
	get_value		2,3
	proceed
append_3_1:
	suspend		append_3_0
	begin_const_section		mpimos_file
'$SCNST_0_0':
	define_desc		0,2
	define_atom		print_var_mode
	define_atom		na
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		print_depth
	define_integer		100
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		0,2
	define_atom		print_length
	define_integer		100
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		11,1
	define_integer		2109216
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_7':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		27,2
	define_integer		707406368
	define_integer		42
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		27,2
	define_integer		707406378
	define_integer		32
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_8_2':
	define_desc		19,9
	define_integer		1663056416
	define_integer		1869508193
	define_integer		1920409716
	define_integer		543519849
	define_integer		544370534
	define_integer		1852534389
	define_integer		544110447
	define_integer		1935762802
	define_integer		28271
'$SCNST_8_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_2'
'$SCNST_8_0':
	define_vector		'$SCNST_8_1'
	define_atom		[]
'$SCNST_8':
	define_list		'$SCNST_8_0'
'$SCNST_9_2':
	define_desc		27,1
	define_integer		46
'$SCNST_9_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_9_2'
'$SCNST_9_0':
	define_vector		'$SCNST_9_1'
	define_atom		[]
'$SCNST_9':
	define_list		'$SCNST_9_0'
'$SCNST_10_1':
	define_desc		27,1
	define_integer		41
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_1':
	define_desc		27,1
	define_integer		44
'$SCNST_11_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_11_1'
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_12_1':
	define_desc		11,5
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		1818846752
	define_integer		2629733
'$SCNST_12_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_12_1'
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_0':
	define_desc		3,5
	define_integer		1768058177
	define_integer		1970238823
	define_integer		2017796211
	define_integer		1936028272
	define_integer		1852795251
'$SCNST_13':
	define_string		'$SCNST_13_0'
'$SCNST_14_0':
	define_desc		11,6
	define_integer		1701603686
	define_integer		1835101741
	define_integer		1936269413
	define_integer		1953459744
	define_integer		1920234272
	define_integer		6778473
'$SCNST_14':
	define_string		'$SCNST_14_0'
'$SCNST_15_0':
	define_desc		3,6
	define_integer		1852141679
	define_integer		1685024045
	define_integer		1936269413
	define_integer		1953459744
	define_integer		745700128
	define_integer		2103520375
'$SCNST_15':
	define_string		'$SCNST_15_0'
'$SCNST_16_0':
	define_desc		27,6
	define_integer		1852141679
	define_integer		1685024045
	define_integer		1936269413
	define_integer		1953459744
	define_integer		1869898016
	define_integer		109
'$SCNST_16':
	define_string		'$SCNST_16_0'
'$SCNST_17_0':
	define_desc		3,4
	define_integer		1852727651
	define_integer		1864397935
	define_integer		544105840
	define_integer		1701603686
'$SCNST_17':
	define_string		'$SCNST_17_0'
'$SCNST_18_0':
	define_desc		3,5
	define_integer		761556581
	define_integer		1714251375
	define_integer		543517801
	define_integer		1897950825
	define_integer		1702129525
'$SCNST_18':
	define_string		'$SCNST_18_0'
'$SCNST_19_0':
	define_desc		3,4
	define_integer		1701603686
	define_integer		544434464
	define_integer		544501614
	define_integer		1852141679
'$SCNST_19':
	define_string		'$SCNST_19_0'
'$SCNST_20_0':
	define_desc		11,4
	define_integer		1701604457
	define_integer		543973735
	define_integer		1835888483
	define_integer		6581857
'$SCNST_20':
	define_string		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		19,7
	define_integer		1835888483
	define_integer		761556577
	define_integer		1701999731
	define_integer		1763732833
	define_integer		1869488243
	define_integer		1768693876
	define_integer		29811
'$SCNST_21':
	define_string		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		11,7
	define_integer		1970302569
	define_integer		1868770676
	define_integer		1851878765
	define_integer		1852383332
	define_integer		1769109280
	define_integer		1830839668
	define_integer		6644847
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_23_0':
	define_desc		11,7
	define_integer		1886680431
	define_integer		1663923317
	define_integer		1634561391
	define_integer		1763730542
	define_integer		1701978222
	define_integer		1830839393
	define_integer		6644847
'$SCNST_23':
	define_string		'$SCNST_23_0'
'$SCNST_24_0':
	define_desc		19,6
	define_integer		1852727651
	define_integer		1914729583
	define_integer		1987013989
	define_integer		1886330981
	define_integer		1952543333
	define_integer		29295
'$SCNST_24':
	define_string		'$SCNST_24_0'
'$SCNST_25_0':
	define_desc		3,3
	define_integer		1953397075
	define_integer		1159755873
	define_integer		1919906418
'$SCNST_25':
	define_string		'$SCNST_25_0'
