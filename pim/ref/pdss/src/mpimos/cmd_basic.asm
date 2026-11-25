mpimos_cmd_basic:
	module		mpimos_cmd_basic
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_cmd_basic
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	hash_on_atom		1,5,is_command_2_1
	bucket_entry_a		cputime,is_command_2_4
	bucket_entry_a		gc,is_command_2_5
	bucket_entry_a		halt,is_command_2_6
	bucket_entry_a		help,is_command_2_7
	bucket_entry_a		stat,is_command_2_8
is_command_2_4:
	get_atom		2,yes
	proceed
is_command_2_5:
	get_atom		2,yes
	proceed
is_command_2_6:
	get_atom		2,yes
	proceed
is_command_2_7:
	get_atom		2,yes
	proceed
is_command_2_8:
	get_atom		2,yes
	proceed
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,5,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_9
	table_entry		is_command_2_10
	table_entry		is_command_2_11
is_command_2_9:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,10,is_command_2_1
	bucket_entry_a		change_op_pool,is_command_2_13
	bucket_entry_a		cputime,is_command_2_14
	bucket_entry_a		display,is_command_2_15
	bucket_entry_a		gc,is_command_2_16
	bucket_entry_a		help,is_command_2_17
	bucket_entry_a		operator,is_command_2_18
	bucket_entry_a		remove_op,is_command_2_19
	bucket_entry_a		stat,is_command_2_20
	bucket_entry_a		take,is_command_2_21
	bucket_entry_a		window,is_command_2_22
is_command_2_13:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_14:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_15:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_16:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_17:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_18:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_19:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_20:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_21:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_22:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_10:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,is_command_2_1
	bucket_entry_a		apply,is_command_2_24
	bucket_entry_a		display_value,is_command_2_25
	bucket_entry_a		operator,is_command_2_26
	bucket_entry_a		replace_op_pool,is_command_2_27
is_command_2_24:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_25:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_26:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_27:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_11:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,is_command_2_1
	bucket_entry_a		add_op,is_command_2_29
	bucket_entry_a		apply,is_command_2_30
	bucket_entry_a		remove_op,is_command_2_31
is_command_2_29:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_30:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_31:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_1:
	otherwise		is_command_2_0
	collect_value		1
	get_atom		2,no
	proceed
is_command_2_41:
	suspend		is_command_2_0
	module_entry		mpimos_cmd_basic
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	hash_on_atom		1,5,do_command_2_1
	bucket_entry_a		cputime,do_command_2_4
	bucket_entry_a		gc,do_command_2_5
	bucket_entry_a		halt,do_command_2_6
	bucket_entry_a		help,do_command_2_7
	bucket_entry_a		stat,do_command_2_8
do_command_2_4:
	get_cpu_time		1
	put_func		3,2,flush
	write_element_variable		3,1,5
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,4
	put_func		4,2,putt
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	put_structured_constant		3,'$SCNST_0'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,5
	execute		1,wait_1_0
do_command_2_5:
	put_integer		1,0
	g_request_gc		1
	get_nil		2
	proceed
do_command_2_6:
	put_integer		1,0
	g_halt		1
	collect_value		2
	proceed
do_command_2_7:
	put_func		1,3,getenv
	write_element_atom		1,1,modules
	write_element_variable		1,2,5
	get_list_val_var		2,3,1,4
	create_goal		1
	set_variable		1,6
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_structured_constant		1,'$SCNST_1'
	put_list_val_var		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	set_value		1,1
	set_value		2,4
	put_func		1,2,flush
	write_element_value		1,1,6
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_integer		1,1
	put_value		2,5
	execute		3,get_help_menu_3_0
do_command_2_8:
	statistics		1,3,4,5,6,7
	put_marked_value		1,4
	b_subtract		3,1,1
	put_marked_value		3,6
	b_subtract		5,3,3
	create_goal		1
	set_variable		1,8
	enqueue_goal		1,wait_1_0
	put_structured_constant		5,'$SCNST_2'
	put_func		7,2,putt
	write_element_value		7,1,3
	put_list_val_val		3,7,5
	put_structured_constant		5,'$SCNST_3'
	put_list_val_val		7,5,3
	put_structured_constant		3,'$SCNST_4'
	put_list_val_val		5,3,7
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		6,3,5
	put_structured_constant		3,'$SCNST_5'
	put_list_val_val		5,3,6
	put_structured_constant		3,'$SCNST_6'
	put_list_val_val		6,3,5
	put_func		3,2,putt
	write_element_value		3,1,1
	put_list_val_val		1,3,6
	put_structured_constant		3,'$SCNST_7'
	put_list_val_val		5,3,1
	put_structured_constant		1,'$SCNST_8'
	put_list_val_val		3,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,3
	put_structured_constant		1,'$SCNST_9'
	put_list_val_val		3,1,4
	put_func		1,2,window
	write_element_value		1,1,3
	put_func		3,2,flush
	write_element_value		3,1,8
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_func		3,2,window
	write_element_value		3,1,4
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_value		3,4
	execute_external		mpimos_cmd_utl,send_shell,3
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,5,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_9
	table_entry		do_command_2_10
	table_entry		do_command_2_11
do_command_2_9:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,10,do_command_2_1
	bucket_entry_a		change_op_pool,do_command_2_13
	bucket_entry_a		cputime,do_command_2_14
	bucket_entry_a		display,do_command_2_15
	bucket_entry_a		gc,do_command_2_16
	bucket_entry_a		help,do_command_2_17
	bucket_entry_a		operator,do_command_2_18
	bucket_entry_a		remove_op,do_command_2_19
	bucket_entry_a		stat,do_command_2_20
	bucket_entry_a		take,do_command_2_21
	bucket_entry_a		window,do_command_2_22
do_command_2_13:
	read_element		1,1,4
	collect_vector		1
	put_value		5,2
	put_value		1,4
	put_variable		3,2
	put_value		4,5
	execute		4,change_op_pool_4_0
do_command_2_14:
	read_element		1,1,4
	get_cpu_time		3
	collect_vector		1
	get_value		4,3
	get_nil		2
	proceed
do_command_2_15:
	read_element		1,1,4
	create_goal		1
	set_variable		1,5
	enqueue_goal		1,wait_1_0
	put_reused_func		1,1,window
	write_element_value		1,1,4
	put_func		3,2,flush
	write_element_value		3,1,5
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_func		3,2,window
	write_element_value		3,1,4
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_value		3,4
	execute_external		mpimos_cmd_utl,send_shell,3
do_command_2_16:
	read_element		1,1,4
	atom		4
	branch_on_atom		4,2,do_command_2_1
	bucket_entry_a		all,do_command_2_24
	bucket_entry_a		h,do_command_2_25
do_command_2_24:
	put_integer		3,1
	g_request_gc		3
	collect_vector		1
	get_nil		2
	proceed
do_command_2_25:
	put_integer		3,0
	g_request_gc		3
	collect_vector		1
	get_nil		2
	proceed
do_command_2_17:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_27
	put_func		3,3,getenv
	write_element_atom		3,1,modules
	write_element_variable		3,2,6
	get_list_val_var		2,7,3,5
	create_goal		1
	set_variable		1,2
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_reused_func		1,1,window
	write_element_variable		1,1,3
	set_value		1,1
	set_value		2,5
	put_func		1,2,flush
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_value		1,4
	put_value		2,6
	execute		3,get_help_message_item_3_0
do_command_2_27:
	is_integer		4,do_command_2_1
	put_func		3,3,getenv
	write_element_atom		3,1,modules
	write_element_variable		3,2,5
	get_list_val_var		2,6,3,3
	create_goal		1
	set_variable		1,2
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_reused_func		1,1,window
	write_element_variable		1,1,6
	set_value		1,1
	set_value		2,3
	put_func		1,2,flush
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_integer		1,1
	put_values_inc		2,4,3
	execute		4,get_help_message_4_0
do_command_2_18:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_29
	collect_vector		1
	put_value		3,2
	put_atom		1,operator
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_29:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_30
	collect_vector		1
	get_nil		2
	proceed
do_command_2_30:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_func		3,3,operator
	write_element_value		3,1,4
	write_element_variable		3,2,5
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_reused_func		1,1,window
	write_element_value		1,1,4
	get_list_val_var		2,3,1,4
	create_goal		1
	set_variable		1,3
	enqueue_goal		1,wait_1_0
	create_goal		2
	set_value		1,5
	set_variable		2,2
	enqueue_goal		2,display_operator_2_0
	put_func		1,2,window
	write_element_value		1,1,2
	put_func		2,2,flush
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_value		2,4
	execute_external		mpimos_cmd_utl,send_shell,3
do_command_2_19:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_32
	collect_vector		1
	put_value		3,2
	put_atom		1,remove_op
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_32:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_33
	collect_vector		1
	get_nil		2
	proceed
do_command_2_33:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_func		3,3,operator
	write_element_marked_value		3,1,4
	write_element_variable		3,2,6
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_reused_func		1,1,window
	write_element_value		1,1,5
	get_list_val_var		2,5,1,3
	put_value		1,6
	put_value		2,4
	execute		3,remove_operator_all_3_0
do_command_2_20:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_35
	collect_vector		1
	put_value		3,2
	put_atom		1,stat
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_35:
	check_nil		4,do_command_2_1
	collect_vector		1
	get_nil		2
	proceed
do_command_2_21:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_36,do_command_2_1,do_command_2_37,do_command_2_1,do_command_2_38,do_command_2_1
do_command_2_37:
	collect_vector		1
	put_value		3,2
	put_atom		1,take
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_36:
	test_nil		4,do_command_2_39
	collect_vector		1
	get_nil		2
	proceed
do_command_2_39:
	put_nil		5
	g_diff		4,5
	collect_value		5
	b_atom_name		4,3
	put_reused_func		1,1,take
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_38:
	g_string		4,5,6
	wait_integer		6,8
	collect_vector		1
	create_goal		3
	set_variable		1,5
	set_variable		2,1
	set_value		3,2
	enqueue_goal		3,take_action_3_0
	put_value		2,4
	put_atom		3,r
	put_value		4,5
	execute_external		mpimos_file,create,4
do_command_2_22:
	read_element		1,1,4
	put_reused_func		1,1,getuc
	write_element_variable		1,1,6
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_structured_constant		1,'$SCNST_10'
	put_variable		2,7
	b_append_string		1,2,1
	create_goal		2
	put_func		2,2,getl
	write_element_void		2,1
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_structured_constant		2,'$SCNST_11'
	put_list_val_val		5,2,3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_func		3,2,do
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,show
	write_cdr_value		2,4
	set_values_dec		1,2,2
	enqueue_goal_external		mpimos_window,create,2
	put_values_inc		1,6,2
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_10:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,do_command_2_1
	bucket_entry_a		apply,do_command_2_41
	bucket_entry_a		display_value,do_command_2_42
	bucket_entry_a		operator,do_command_2_43
	bucket_entry_a		replace_op_pool,do_command_2_44
do_command_2_41:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_46
	read_element		1,2,5
	collect_vector		1
	put_value		3,2
	put_values_inc		1,4,2
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_46:
	check_vector		4,3,do_command_2_1
	read_element		1,2,5
	read_element		4,0,6
	wait_atom		6,:
	read_elements_inc		4,1,6,2
	atom		6
	atom		7
	collect_vector		4
	put_value		3,2
	put_reused_func		1,1,:
	write_elements_inc		1,1,6,2
	put_value		2,5
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_42:
	read_elements_inc		1,1,4,2
	wait		5
	collect_vector		1
	create_goal		3
	set_value		1,4
	set_variable		2,3
	set_value		3,2
	enqueue_goal		3,display_value_action_3_0
	put_value		1,5
	put_value		2,3
	execute_external		mpimos_utility,freeze,2
do_command_2_43:
	read_elements_inc		1,1,4,2
	atom		4
	put_reused_func		1,1,operator
	write_element_value		1,1,4
	write_element_variable		1,2,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_func		1,2,window
	write_element_value		1,1,3
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_values_inc		1,4,2
	execute_external		mpimos_cmd_utl,protect,2
do_command_2_44:
	read_elements_inc		1,1,4,2
	put_reused_func		1,1,replace_op_pool
	write_element_marked_variable		1,1,6
	write_element_value		1,2,6
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_func		1,2,window
	write_element_value		1,1,3
	get_list_val_var		2,3,1,1
	create_goal		4
	set_value		1,5
	set_variable		2,2
	set_values_dec		3,2,2
	enqueue_goal		4,change_op_pool_4_0
	put_value		1,6
	put_value		2,4
	execute_external		mpimos_cmd_utl,protect,2
do_command_2_11:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,do_command_2_1
	bucket_entry_a		add_op,do_command_2_48
	bucket_entry_a		apply,do_command_2_49
	bucket_entry_a		remove_op,do_command_2_50
do_command_2_48:
	read_elements_inc		1,1,4,3
	integer		4
	put_integer		7,1
	g_not_less_than		4,7
	put_integer		7,1200
	g_not_less_than		7,4
	atom		5
	atom		6
	put_reused_func		1,1,add_op
	write_elements_inc		1,1,4,3
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_func		1,2,window
	write_element_value		1,1,3
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	proceed
do_command_2_49:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_52
	read_elements_inc		1,2,5,2
	collect_vector		1
	put_value		7,2
	put_values_inc		1,4,4
	execute_external		mpimos_cmd_utl,apply_action,4
do_command_2_52:
	check_vector		4,3,do_command_2_1
	read_elements_inc		1,2,5,2
	read_element		4,0,7
	wait_atom		7,:
	read_elements_inc		4,1,7,2
	atom		7
	atom		8
	collect_vector		1
	put_value		9,2
	put_reused_func		1,4,:
	write_elements_inc		1,1,7,2
	put_values_dec		2,6,2
	put_value		4,9
	execute_external		mpimos_cmd_utl,apply_action,4
do_command_2_50:
	read_elements_inc		1,1,4,3
	integer		4
	put_integer		7,1
	g_not_less_than		4,7
	put_integer		7,1200
	g_not_less_than		7,4
	atom		5
	atom		6
	collect_vector		1
	put_func		1,3,operator
	write_element_marked_value		1,1,6
	write_element_variable		1,2,7
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_func		1,2,window
	write_element_value		1,1,3
	get_list_val_var		2,3,1,1
	create_goal		5
	set_variable		1,3
	set_marked_value		2,4
	set_marked_value		3,5
	set_value		4,6
	set_value		5,1
	enqueue_goal		5,remove_operator_5_0
	put_vector		1,2
	write_elements_inc		1,0,4,2
	put_value		2,7
	execute		3,member_3_0
do_command_2_1:
	otherwise		do_command_2_0
	try_me_else		do_command_2_89
	wait_vector		1,2
	read_element		1,0,3
	wait_atom		3,stat
	read_element		1,1,3
	put_reused_vector		5,1
	write_element_variable		5,0,1
	write_element_variable		5,1,4
	get_vector_value		2,5
	create_goal		2
	set_value		1,1
	set_variable		2,5
	enqueue_goal		2,stat_action_2_0
	put_values_inc		1,3,3
	execute_external		mpimos_command_interpreter,command_analyzer,3
do_command_2_89:
	otherwise		do_command_2_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_12'
	put_func		4,2,putt
	write_element_variable		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_13'
	put_list_val_val		4,3,5
	put_func		3,2,window
	write_element_value		3,1,4
	set_values_dec		1,3,2
	put_func		2,2,flush
	write_element_value		2,1,7
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	set_value		3,3
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_value		2,6
	execute_external		mpimos_utility,freeze,2
do_command_2_94:
	suspend		do_command_2_0
	module_entry		mpimos_cmd_basic
	predicate		get_help_menu,3
get_help_menu_3_0:
	try_me_else		get_help_menu_3_1
	jump_on_non_list_var_var		2,get_help_menu_3_3,4,5
	put_vector		6,3
	write_element_marked_value		6,0,4
	write_element_atom		6,1,help
	write_element_integer		6,2,2
	put_func		7,2,item
	write_element_variable		7,1,8
	b_apply		6,7
	put_vector		6,3
	write_element_value		6,0,4
	write_element_atom		6,1,help
	write_element_integer		6,2,2
	put_func		4,2,menu
	write_element_variable		4,1,9
	b_apply		6,4
	b_atom_name		8,4
	b_string		4,4,6,7
	put_integer		6,10
	b_subtract		6,4,4
	put_reused_list		2,2
	write_car_atom		2,nl
	write_cdr_variable		2,10
	put_func		6,2,putb
	write_element_value		6,1,9
	put_list_val_val		8,6,2
	put_structured_constant		2,'$SCNST_14'
	put_list_val_val		6,2,8
	put_func		2,2,tab
	write_element_value		2,1,4
	put_list_val_val		4,2,6
	put_structured_constant		2,'$SCNST_15'
	put_list_val_val		6,2,4
	put_func		2,2,putb
	write_element_value		2,1,7
	put_list_val_val		4,2,6
	put_structured_constant		2,'$SCNST_16'
	put_list_val_val		6,2,4
	put_func		2,2,putt
	write_element_marked_value		2,1,1
	put_list_val_val		4,2,6
	put_structured_constant		2,'$SCNST_17'
	put_list_val_val		6,2,4
	get_list_value		3,6
	b_increment		1,1
	put_value		2,5
	put_value		3,10
	execute		3,get_help_menu_3_0
get_help_menu_3_3:
	check_nil		2,get_help_menu_3_1
	collect_value		1
	put_structured_constant		1,'$SCNST_18'
	get_value		3,1
	proceed
get_help_menu_3_1:
	suspend		get_help_menu_3_0
	module_entry		mpimos_cmd_basic
	predicate		get_help_message,4
get_help_message_4_0:
	try_me_else		get_help_message_4_1
	jump_on_non_list_var_var		3,get_help_message_4_3,5,6
	try_me_else		get_help_message_4_4
	g_diff		2,1
	collect_list		3
	collect_value		5
	b_increment		1,1
	put_value		3,6
	execute		4,get_help_message_4_0
get_help_message_4_4:
	try_me_else		get_help_message_4_1
	wait_value		1,2
	collect_list		3
	collect_value		6
	collect_value		1
	collect_value		2
	put_vector		1,3
	write_element_value		1,0,5
	write_element_atom		1,1,help
	write_element_integer		1,2,2
	put_func		2,2,message
	write_element_variable		2,1,3
	b_apply		1,2
	put_values_inc		1,3,2
	execute		2,display_message_2_0
get_help_message_4_3:
	check_nil		3,get_help_message_4_1
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_19'
	get_value		4,1
	proceed
get_help_message_4_1:
	suspend		get_help_message_4_0
	module_entry		mpimos_cmd_basic
	predicate		get_help_message_item,3
get_help_message_item_3_0:
	try_me_else		get_help_message_item_3_1
	wait_atom		1,all
	put_values_inc		1,2,2
	execute		2,all_help_message_2_0
get_help_message_item_3_1:
	try_me_else		get_help_message_item_3_3
	put_atom		4,all
	g_diff		1,4
	execute		3,get_help_message_item1_3_0
get_help_message_item_3_3:
	suspend		get_help_message_item_3_0
	module_entry		mpimos_cmd_basic
	predicate		get_help_message_item1,3
get_help_message_item1_3_0:
	try_me_else		get_help_message_item1_3_1
	jump_on_non_list_var_var		2,get_help_message_item1_3_3,4,5
	collect_list		2
	put_value		7,3
	put_vector		2,3
	write_element_marked_value		2,0,4
	write_element_atom		2,1,help
	write_element_integer		2,2,2
	put_func		3,2,item
	write_element_variable		3,1,6
	b_apply		2,3
	put_value		2,6
	put_values_inc		3,4,2
	put_value		5,7
	execute		5,wait_help_item_5_0
get_help_message_item1_3_3:
	check_nil		2,get_help_message_item1_3_1
	collect_value		1
	put_structured_constant		1,'$SCNST_20'
	get_value		3,1
	proceed
get_help_message_item1_3_1:
	suspend		get_help_message_item1_3_0
	module_entry		mpimos_cmd_basic
	predicate		wait_help_item,5
wait_help_item_5_0:
	try_me_else		wait_help_item_5_1
	g_diff		1,2
	collect_value		3
	collect_value		2
	put_values_inc		2,4,2
	execute		3,get_help_message_item1_3_0
wait_help_item_5_1:
	try_me_else		wait_help_item_5_2
	wait_value		1,2
	collect_value		4
	collect_value		1
	collect_value		2
	put_vector		1,3
	write_element_value		1,0,3
	write_element_atom		1,1,help
	write_element_integer		1,2,2
	put_func		2,2,message
	write_element_variable		2,1,3
	b_apply		1,2
	put_value		1,3
	put_value		2,5
	execute		2,display_message_2_0
wait_help_item_5_2:
	suspend		wait_help_item_5_0
	module_entry		mpimos_cmd_basic
	predicate		all_help_message,2
all_help_message_2_0:
	try_me_else		all_help_message_2_1
	wait_list_var_var		1,3,4
	put_vector		5,3
	write_element_value		5,0,3
	write_element_atom		5,1,help
	write_element_integer		5,2,2
	put_func		3,2,message
	write_element_variable		3,1,6
	b_apply		5,3
	put_func		3,2,do
	write_element_variable		3,1,5
	get_reused_list_val_var		2,7,1,3,1
	create_goal		2
	set_value		1,4
	set_value		2,1
	enqueue_goal		2,all_help_message1_2_0
	put_values_dec		1,6,2
	execute		2,display_message_2_0
all_help_message_2_1:
	suspend		all_help_message_2_0
	module_entry		mpimos_cmd_basic
	predicate		all_help_message1,2
all_help_message1_2_0:
	try_me_else		all_help_message1_2_1
	jump_on_non_list_var_var		1,all_help_message1_2_3,3,4
	put_vector		5,3
	write_element_value		5,0,3
	write_element_atom		5,1,help
	write_element_integer		5,2,2
	put_func		3,2,message
	write_element_variable		3,1,6
	b_apply		5,3
	put_func		3,2,do
	write_element_variable		3,1,5
	put_reused_list_val_var		1,1,3,3
	put_list		7
	write_car_atom		7,nl
	write_cdr_value		7,1
	get_list_value		2,7
	create_goal		2
	set_values_dec		1,4,2
	enqueue_goal		2,all_help_message1_2_0
	put_values_dec		1,6,2
	execute		2,display_message_2_0
all_help_message1_2_3:
	check_nil		1,all_help_message1_2_1
	get_nil		2
	proceed
all_help_message1_2_1:
	suspend		all_help_message1_2_0
	module_entry		mpimos_cmd_basic
	predicate		display_message,2
display_message_2_0:
	try_me_else		display_message_2_1
	jump_on_non_list_var_var		1,display_message_2_3,3,4
	wait		3
	put_func		5,2,putl
	write_element_value		5,1,3
	put_reused_list_val_var		1,1,5,5
	put_structured_constant		3,'$SCNST_21'
	put_list_val_val		6,3,1
	get_list_value		2,6
	put_values_inc		1,4,2
	execute		2,display_message_2_0
display_message_2_3:
	check_nil		1,display_message_2_1
	get_nil		2
	proceed
display_message_2_1:
	suspend		display_message_2_0
	module_entry		mpimos_cmd_basic
	predicate		display_value_action,3
display_value_action_3_0:
	try_me_else		display_value_action_3_1
	jump_on_non_list		1,display_value_action_3_3
	read_car		1,4
	jump_on_non_vector		4,display_value_action_3_5
	test_arity		4,2,display_value_action_3_1
	read_cdr		1,5
	read_element		4,0,6
	wait_atom		6,error
	read_element		4,1,6
	collect_value		2
	collect_value		5
	put_reused_func		2,4,flush
	write_element_variable		2,1,7
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,1
	put_func		1,2,putt
	write_element_variable		1,1,5
	put_list_val_val		4,1,2
	put_structured_constant		1,'$SCNST_22'
	put_list_val_val		2,1,4
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	create_goal		2
	set_value		1,7
	set_atom		2,aborted
	enqueue_goal		2,error_action_2_0
	put_values_dec		1,6,2
	execute_external		mpimos_utility,freeze,2
display_value_action_3_5:
	is_string		4,display_value_action_3_1
	read_cdr		1,5
	wait_list_var_var		2,6,7
	g_string		4,8,9
	wait_integer		9,8
	wait		6
	create_goal		3
	set_value		1,5
	set_value		2,7
	set_variable		3,8
	enqueue_goal		3,display_value_action_3_0
	put_structured_constant		5,'$SCNST_23'
	put_func		7,2,putt
	write_element_value		7,1,6
	put_reused_list_val_val		1,1,7,5
	put_structured_constant		5,'$SCNST_24'
	put_reused_list_val_val		2,2,5,1
	put_func		1,2,putb
	write_element_value		1,1,4
	put_list_val_val		4,1,2
	put_func		1,2,window
	write_element_value		1,1,4
	put_value		2,3
	put_value		3,8
	execute_external		mpimos_cmd_utl,send_shell,3
display_value_action_3_3:
	check_nil		1,display_value_action_3_1
	wait_nil		2
	put_func		1,2,flush
	write_element_variable		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,4
	execute		1,wait_1_0
display_value_action_3_1:
	suspend		display_value_action_3_0
	module_entry		mpimos_cmd_basic
	predicate		stat_action,2
stat_action_2_0:
	try_me_else		stat_action_2_1
	wait		2
	put_value		10,1
	put_variable		1,6
	put_integer		3,0
	b_vector_element		1,3,1,3
	put_variable		3,8
	put_variable		4,7
	b_subtract		3,4,3
	create_goal		1
	set_variable		1,9
	enqueue_goal_external		mpimos_command_interpreter,apply_goals,1
	put_structured_constant		4,'$SCNST_25'
	put_func		5,2,putt
	write_element_value		5,1,3
	put_list_val_val		3,5,4
	put_structured_constant		4,'$SCNST_26'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,1
	put_list_val_val		1,3,5
	put_structured_constant		3,'$SCNST_27'
	put_list_val_val		4,3,1
	put_func		1,2,display
	write_element_value		1,1,4
	put_func		3,2,cputime
	write_element_value		3,1,8
	put_func		4,3,;
	write_element_value		4,1,3
	write_element_value		4,2,1
	put_func		1,5,unit
	write_element_value		1,1,2
	write_element_atom		1,2,success
	write_element_void		1,3
	write_element_value		1,4,6
	put_func		2,3,:
	write_element_atom		2,1,mpimos_command_interpreter
	write_element_value		2,2,1
	put_func		1,3,;
	write_element_value		1,1,2
	write_element_value		1,2,4
	put_func		2,2,cputime
	write_element_value		2,1,7
	put_func		3,3,;
	write_elements_dec		3,1,2,2
	put_value		1,3
	put_values_dec		2,10,2
	execute_external		mpimos_command_interpreter,command_analyzer,3
stat_action_2_1:
	suspend		stat_action_2_0
	module_entry		mpimos_cmd_basic
	predicate		take_action,3
take_action_3_0:
	try_me_else		take_action_3_1
	jump_on_non_atom		1,take_action_3_3
	test_atom		1,success,take_action_3_1
	put_value		5,3
	put_func		1,3,getft
	write_element_variable		1,1,6
	write_element_variable		1,2,3
	get_list_val_var		2,7,1,4
	put_atom		1,success
	put_value		2,6
	execute		5,take_action0_5_0
take_action_3_3:
	check_vector		1,2,take_action_3_1
	read_element		1,0,4
	wait_atom		4,error
	read_element		1,1,4
	wait_atom		4,cannot_open_file
	get_nil		2
	put_reused_func		1,1,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,fail_action_1_0
take_action_3_1:
	suspend		take_action_3_0
	module_entry		mpimos_cmd_basic
	predicate		take_action0,5
take_action0_5_0:
	try_me_else		take_action0_5_1
	wait_atom		2,end_of_file
	collect_value		3
	collect_value		1
	get_nil		4
	get_nil		5
	proceed
take_action0_5_1:
	otherwise		take_action0_5_0
	try_me_else		take_action0_5_6
	wait		1
	put_vector		1,2
	write_element_variable		1,0,8
	write_element_variable		1,1,7
	put_func		6,5,expand
	write_elements_inc		6,1,2,2
	write_element_variable		6,3,10
	write_element_variable		6,4,9
	put_func		2,2,macro_expander
	write_element_value		2,1,6
	put_list_val_val		3,2,1
	get_list_value		5,3
	put_func		1,3,getft
	write_element_variable		1,1,5
	write_element_variable		1,2,3
	get_list_val_var		4,2,1,1
	create_goal		5
	set_variable		1,2
	set_value		2,5
	set_value		3,3
	set_value		4,1
	set_value		5,7
	enqueue_goal		5,take_action0_5_0
	create_goal		4
	set_variable		1,1
	set_atom		2,success
	set_value		3,2
	set_void		4
	enqueue_goal_external		mpimos_command_interpreter,unit,4
	create_goal		3
	set_variable		1,3
	set_value		2,8
	set_value		3,1
	enqueue_goal_external		mpimos_command_interpreter,command_analyzer,3
	put_values_dec		1,10,2
	execute_external		mpimos_utility,melt,3
take_action0_5_6:
	suspend		take_action0_5_0
	module_entry		mpimos_cmd_basic
	predicate		fail_action,1
fail_action_1_0:
	try_me_else		fail_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_29'
	put_void		3
	b_raise		2,1,3
	proceed
fail_action_1_1:
	suspend		fail_action_1_0
	module_entry		mpimos_cmd_basic
	predicate		remove_operator,5
remove_operator_5_0:
	try_me_else		remove_operator_5_1
	atom		1
	branch_on_atom		1,2,remove_operator_5_1
	bucket_entry_a		false,remove_operator_5_3
	bucket_entry_a		true,remove_operator_5_4
remove_operator_5_3:
	collect_value		4
	collect_value		3
	collect_value		2
	put_func		1,2,flush
	write_element_variable		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_structured_constant		1,'$SCNST_30'
	put_list_val_val		3,1,2
	put_func		1,2,window
	write_element_value		1,1,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		5,2
	put_value		1,4
	execute		1,wait_1_0
remove_operator_5_4:
	put_func		1,4,remove_op
	write_elements_inc		1,1,2,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		5,2
	proceed
remove_operator_5_1:
	suspend		remove_operator_5_0
	module_entry		mpimos_cmd_basic
	predicate		remove_operator_all,3
remove_operator_all_3_0:
	try_me_else		remove_operator_all_3_1
	jump_on_non_list		1,remove_operator_all_3_3
	put_func		1,2,remove_op
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	proceed
remove_operator_all_3_3:
	check_nil		1,remove_operator_all_3_1
	collect_value		2
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_structured_constant		1,'$SCNST_31'
	put_list_val_val		4,1,2
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,wait_1_0
remove_operator_all_3_1:
	suspend		remove_operator_all_3_0
	module_entry		mpimos_cmd_basic
	predicate		member,3
member_3_0:
	try_me_else		member_3_1
	jump_on_non_list_var_var		2,member_3_3,4,5
	try_me_else		member_3_4
	g_diff		1,4
	collect_list		2
	collect_value		4
	put_value		2,5
	execute		3,member_3_0
member_3_4:
	try_me_else		member_3_1
	wait_value		1,4
	collect_list		2
	collect_value		5
	collect_value		1
	collect_value		4
	get_atom		3,true
	proceed
member_3_3:
	check_nil		2,member_3_1
	collect_value		1
	get_atom		3,false
	proceed
member_3_1:
	suspend		member_3_0
	module_entry		mpimos_cmd_basic
	predicate		display_operator,2
display_operator_2_0:
	try_me_else		display_operator_2_1
	jump_on_non_list_var_var		1,display_operator_2_3,8,3
	wait_vector		8,2
	read_elements_inc		8,0,4,2
	put_structured_constant		6,'$SCNST_32'
	put_reused_list_val_var		1,1,6,7
	put_reused_func		6,8,putt
	write_element_value		6,1,5
	put_list_val_val		5,6,1
	put_structured_constant		1,'$SCNST_33'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_structured_constant		1,'$SCNST_34'
	put_list_val_val		5,1,4
	get_list_value		2,5
	put_value		1,3
	put_value		2,7
	execute		2,display_operator1_2_0
display_operator_2_3:
	check_nil		1,display_operator_2_1
	put_structured_constant		1,'$SCNST_35'
	get_value		2,1
	proceed
display_operator_2_1:
	suspend		display_operator_2_0
	module_entry		mpimos_cmd_basic
	predicate		display_operator1,2
display_operator1_2_0:
	try_me_else		display_operator1_2_1
	jump_on_non_list_var_var		1,display_operator1_2_3,8,3
	wait_vector		8,2
	read_elements_inc		8,0,4,2
	put_structured_constant		6,'$SCNST_36'
	put_reused_list_val_var		1,1,6,7
	put_reused_func		6,8,putt
	write_element_value		6,1,5
	put_list_val_val		5,6,1
	put_structured_constant		1,'$SCNST_37'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_structured_constant		1,'$SCNST_38'
	put_list_val_val		5,1,4
	get_list_value		2,5
	put_value		1,3
	put_value		2,7
	execute		2,display_operator1_2_0
display_operator1_2_3:
	check_nil		1,display_operator1_2_1
	put_structured_constant		1,'$SCNST_39'
	get_value		2,1
	proceed
display_operator1_2_1:
	suspend		display_operator1_2_0
	module_entry		mpimos_cmd_basic
	predicate		change_op_pool,4
change_op_pool_4_0:
	try_me_else		change_op_pool_4_1
	jump_on_non_list_var_var		1,change_op_pool_4_3,8,5
	wait_vector		8,2
	read_elements_inc		8,0,6,2
	atom		6
	put_reused_vector		8,8
	write_element_value		8,0,6
	write_element_variable		8,1,6
	get_reused_list_val_var		3,1,1,8,8
	put_value		1,5
	put_value		3,8
	put_value		5,7
	execute		6,check_op_defs_6_0
change_op_pool_4_3:
	check_nil		1,change_op_pool_4_1
	get_nil		3
	put_func		1,2,change_op_pool
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		4,2
	proceed
change_op_pool_4_1:
	otherwise		change_op_pool_4_0
	collect_value		3
	collect_value		2
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		2,'$SCNST_40'
	put_func		3,2,putt
	write_element_variable		3,1,6
	put_list_val_val		5,3,2
	put_structured_constant		2,'$SCNST_41'
	put_list_val_val		3,2,5
	put_func		2,2,window
	write_element_value		2,1,3
	set_value		1,2
	set_value		2,4
	put_func		2,2,flush
	write_element_value		2,1,7
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	set_value		3,3
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_value		2,6
	execute_external		mpimos_utility,freeze,2
change_op_pool_4_8:
	suspend		change_op_pool_4_0
	module_entry		mpimos_cmd_basic
	predicate		check_op_defs,6
check_op_defs_6_0:
	try_me_else		check_op_defs_6_1
	jump_on_non_list_var_var		5,check_op_defs_6_3,10,7
	wait_vector		10,2
	read_elements_inc		10,0,8,2
	integer		8
	put_integer		11,1
	g_not_less_than		8,11
	put_integer		11,1200
	g_not_less_than		11,8
	atom		9
	put_reused_vector		10,10
	write_elements_inc		10,0,8,2
	get_reused_list_val_var		6,5,5,10,8
	put_values_inc		5,7,2
	execute		6,check_op_defs_6_0
check_op_defs_6_3:
	check_nil		5,check_op_defs_6_1
	get_nil		6
	execute		4,change_op_pool_4_0
check_op_defs_6_1:
	otherwise		check_op_defs_6_0
	collect_value		6
	collect_value		3
	collect_value		2
	collect_value		1
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		1,'$SCNST_42'
	put_func		2,2,putt
	write_element_variable		2,1,6
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_43'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	set_value		1,1
	set_value		2,4
	put_func		1,2,flush
	write_element_value		1,1,7
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_values_inc		1,5,2
	execute_external		mpimos_utility,freeze,2
check_op_defs_6_8:
	suspend		check_op_defs_6_0
	module_entry		mpimos_cmd_basic
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait		1
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_cmd_basic
	predicate		error_action,2
error_action_2_0:
	try_me_else		error_action_2_1
	wait		1
	wait		2
	put_integer		3,131072
	put_func		1,2,shell
	write_element_value		1,1,2
	put_void		2
	b_raise		3,1,2
	proceed
error_action_2_1:
	suspend		error_action_2_0
	module_entry		mpimos_cmd_basic
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,basic
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_44'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_45'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_cmd_basic
'$SCNST_0_1':
	define_desc		19,3
	define_integer		1953853539
	define_integer		543518057
	define_integer		8253
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		19,8
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1886152040
	define_integer		1852140832
	define_integer		11893
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_2':
	define_desc		11,2
	define_integer		1954112032
	define_integer		3044197
'$SCNST_2_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_2_2'
'$SCNST_2_0':
	define_vector		'$SCNST_2_1'
	define_atom		[]
'$SCNST_2':
	define_list		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		19,5
	define_integer		1701147206
	define_integer		1685013280
	define_integer		1769152613
	define_integer		1763730810
	define_integer		8307
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		11,2
	define_integer		1954112032
	define_integer		3044197
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		19,5
	define_integer		1684370261
	define_integer		1685013280
	define_integer		1769152613
	define_integer		1763730810
	define_integer		8307
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		11,2
	define_integer		1919907616
	define_integer		3044196
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_6_1'
'$SCNST_8':
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		19,5
	define_integer		1701147206
	define_integer		1634027552
	define_integer		1769152624
	define_integer		1763730810
	define_integer		8307
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_9_1':
	define_desc		19,5
	define_integer		1684370261
	define_integer		1634027552
	define_integer		1769152624
	define_integer		1763730810
	define_integer		8307
'$SCNST_9_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_9_1'
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_10_0':
	define_desc		19,2
	define_integer		1145981271
	define_integer		22351
'$SCNST_10':
	define_string		'$SCNST_10_0'
'$SCNST_11_1':
	define_desc		3,5
	define_integer		1701736260
	define_integer		1887007784
	define_integer		1851859045
	define_integer		1701519481
	define_integer		1059072377
'$SCNST_11_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_11_1'
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_12_0':
	define_atom		nl
	define_atom		[]
'$SCNST_42':
'$SCNST_40':
'$SCNST_23':
'$SCNST_12':
	define_list		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		19,7
	define_integer		1969713729
	define_integer		1953391981
	define_integer		1869771333
	define_integer		1701060722
	define_integer		1952671092
	define_integer		1763730533
	define_integer		8302
'$SCNST_13_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_13_1'
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		3,1
	define_integer		539831597
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_1':
	define_desc		27,1
	define_integer		41
'$SCNST_15_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_16_1':
	define_desc		11,2
	define_integer		1701325865
	define_integer		2650220
'$SCNST_16_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_16_1'
'$SCNST_16':
	define_vector		'$SCNST_16_0'
'$SCNST_17_1':
	define_desc		3,2
	define_integer		1746935840
	define_integer		678456421
'$SCNST_17_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_17_1'
'$SCNST_17':
	define_vector		'$SCNST_17_0'
'$SCNST_18_2':
	define_desc		11,14
	define_integer		1746935840
	define_integer		678456421
	define_integer		694971489
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1881156909
	define_integer		1953393010
	define_integer		1819042080
	define_integer		1818585120
	define_integer		1701650544
	define_integer		1734439795
	define_integer		3044197
'$SCNST_18_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_18_2'
'$SCNST_18_0':
	define_vector		'$SCNST_18_1'
	define_atom		[]
'$SCNST_18':
	define_list		'$SCNST_18_0'
'$SCNST_19_2':
	define_desc		19,6
	define_integer		1701604425
	define_integer		543973735
	define_integer		1886152040
	define_integer		1836412448
	define_integer		544367970
	define_integer		8481
'$SCNST_19_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_19_2'
'$SCNST_19_0':
	define_vector		'$SCNST_19_1'
	define_atom		[]
'$SCNST_19':
	define_list		'$SCNST_19_0'
'$SCNST_20_2':
	define_desc		3,5
	define_integer		1701604425
	define_integer		543973735
	define_integer		1886152040
	define_integer		1702127904
	define_integer		555819117
'$SCNST_20_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_20_2'
'$SCNST_20_0':
	define_vector		'$SCNST_20_1'
	define_atom		[]
'$SCNST_20':
	define_list		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		0,2
	define_atom		tab
	define_integer		3
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_1':
	define_desc		11,5
	define_integer		1701604425
	define_integer		543973735
	define_integer		1836216166
	define_integer		975205473
	define_integer		2112058
'$SCNST_22_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_22_1'
'$SCNST_22':
	define_vector		'$SCNST_22_0'
'$SCNST_24_1':
	define_desc		11,1
	define_integer		2112800
'$SCNST_24_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_24_1'
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_25_2':
	define_desc		19,2
	define_integer		1702063392
	define_integer		11875
'$SCNST_25_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_25_2'
'$SCNST_25_0':
	define_vector		'$SCNST_25_1'
	define_atom		[]
'$SCNST_25':
	define_list		'$SCNST_25_0'
'$SCNST_26_1':
	define_desc		11,4
	define_integer		1684369952
	define_integer		1769235317
	define_integer		544435823
	define_integer		2125417
'$SCNST_26_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_26_1'
'$SCNST_26':
	define_vector		'$SCNST_26_0'
'$SCNST_27_1':
	define_desc		27,3
	define_integer		1635020628
	define_integer		1718558828
	define_integer		32
'$SCNST_27_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_27_1'
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_28_1':
	define_desc		3,11
	define_integer		1869771333
	define_integer		1635000434
	define_integer		825189739
	define_integer		1836016416
	define_integer		1684955501
	define_integer		976894496
	define_integer		1176517178
	define_integer		543517801
	define_integer		544501614
	define_integer		1853189990
	define_integer		555819108
'$SCNST_28_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_28_1'
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_29_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_29':
	define_vector		'$SCNST_29_0'
'$SCNST_30_1':
	define_desc		19,3
	define_integer		1701080661
	define_integer		1701734758
	define_integer		11876
'$SCNST_30_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_30_1'
'$SCNST_31':
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_32_0':
	define_desc		0,2
	define_atom		putc
	define_integer		125
'$SCNST_36':
'$SCNST_32':
	define_vector		'$SCNST_32_0'
'$SCNST_33_0':
	define_desc		0,2
	define_atom		putc
	define_integer		44
'$SCNST_37':
'$SCNST_33':
	define_vector		'$SCNST_33_0'
'$SCNST_34_1':
	define_desc		19,4
	define_integer		1768318276
	define_integer		1769236846
	define_integer		1025535599
	define_integer		31520
'$SCNST_34_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_34_1'
'$SCNST_34':
	define_vector		'$SCNST_34_0'
'$SCNST_35_2':
	define_desc		19,3
	define_integer		1701080661
	define_integer		1701734758
	define_integer		11876
'$SCNST_35_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_35_2'
'$SCNST_35_0':
	define_vector		'$SCNST_35_1'
	define_atom		[]
'$SCNST_35':
	define_list		'$SCNST_35_0'
'$SCNST_38_1':
	define_desc		11,1
	define_integer		8069164
'$SCNST_38_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_38_1'
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_39_2':
	define_desc		27,1
	define_integer		46
'$SCNST_39_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_39_2'
'$SCNST_39_0':
	define_vector		'$SCNST_39_1'
	define_atom		[]
'$SCNST_39':
	define_list		'$SCNST_39_0'
'$SCNST_41_1':
	define_desc		3,9
	define_integer		1701604425
	define_integer		543973735
	define_integer		1836216134
	define_integer		1763734625
	define_integer		1884233838
	define_integer		1952543333
	define_integer		1344303727
	define_integer		543977327
	define_integer		540686906
'$SCNST_41_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_1'
'$SCNST_41':
	define_vector		'$SCNST_41_0'
'$SCNST_43_1':
	define_desc		19,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1836216134
	define_integer		1763734625
	define_integer		1884233838
	define_integer		1952543333
	define_integer		1142977135
	define_integer		1852401253
	define_integer		1869182057
	define_integer		976887918
	define_integer		8250
'$SCNST_43_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_43_1'
'$SCNST_43':
	define_vector		'$SCNST_43_0'
'$SCNST_44_0':
	define_desc		3,9
	define_integer		1701536116
	define_integer		1886413100
	define_integer		1730967916
	define_integer		1885547619
	define_integer		1835627637
	define_integer		1953705061
	define_integer		1747743841
	define_integer		745827425
	define_integer		778269797
'$SCNST_44':
	define_string		'$SCNST_44_0'
'$SCNST_45_1':
	define_desc		11,9
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1769169250
	define_integer		1868767331
	define_integer		1851878765
	define_integer		3044196
'$SCNST_45_3':
	define_desc		11,13
	define_integer		1969516365
	define_integer		1195009388
	define_integer		543973743
	define_integer		538976288
	define_integer		757080096
	define_integer		1226845485
	define_integer		1802466926
	define_integer		1752440933
	define_integer		1869029477
	define_integer		1293970529
	define_integer		1819632751
	define_integer		1866938981
	define_integer		3042401
'$SCNST_45_5':
	define_desc		3,11
	define_integer		1701536116
	define_integer		1279870504
	define_integer		538978629
	define_integer		538976288
	define_integer		757080096
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1663067508
	define_integer		1634561391
	define_integer		1176527982
	define_integer		776293449
'$SCNST_45_7':
	define_desc		19,17
	define_integer		1819308129
	define_integer		1329801337
	define_integer		1312902477
	define_integer		1380002884
	define_integer		539579207
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1948280180
	define_integer		1931502952
	define_integer		543518049
	define_integer		1296912195
	define_integer		541347393
	define_integer		1752459639
	define_integer		1869504800
	define_integer		1919248500
	define_integer		1196572960
	define_integer		11859
'$SCNST_45_9':
	define_desc		27,12
	define_integer		538993511
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1142959405
	define_integer		1634148463
	define_integer		1734435442
	define_integer		1868767333
	define_integer		1667591276
	define_integer		1852795252
	define_integer		46
'$SCNST_45_11':
	define_desc		19,15
	define_integer		1747477351
	define_integer		538976297
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1142959405
	define_integer		1634148463
	define_integer		1734435442
	define_integer		1868767333
	define_integer		1667591276
	define_integer		1852795252
	define_integer		543584032
	define_integer		1885431144
	define_integer		1701994784
	define_integer		11873
'$SCNST_45_13':
	define_desc		27,17
	define_integer		1630036839
	define_integer		539585644
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1142959405
	define_integer		1634148463
	define_integer		1734435442
	define_integer		1868767333
	define_integer		1667591276
	define_integer		1852795252
	define_integer		543584032
	define_integer		1885431144
	define_integer		1663051296
	define_integer		543515759
	define_integer		1634038369
	define_integer		46
'$SCNST_45_15':
	define_desc		27,10
	define_integer		1953853539
	define_integer		543518057
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1970299680
	define_integer		1701669236
	define_integer		46
'$SCNST_45_17':
	define_desc		11,11
	define_integer		1953853539
	define_integer		677735785
	define_integer		1162692948
	define_integer		538976297
	define_integer		757080096
	define_integer		1193291053
	define_integer		1663071333
	define_integer		1769239920
	define_integer		1948280173
	define_integer		1230250095
	define_integer		3032397
'$SCNST_45_19':
	define_desc		27,12
	define_integer		1952543859
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1635021600
	define_integer		1864394100
	define_integer		1701650534
	define_integer		2037542765
	define_integer		46
'$SCNST_45_21':
	define_desc		27,19
	define_integer		1952543859
	define_integer		1297040168
	define_integer		1145979213
	define_integer		538976297
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1297040160
	define_integer		1145979213
	define_integer		1702389024
	define_integer		1769239907
	define_integer		1948282479
	define_integer		543518057
	define_integer		543452769
	define_integer		1969513842
	define_integer		1869182051
	define_integer		1970151534
	define_integer		1919246957
	define_integer		46
'$SCNST_45_23':
	define_desc		27,17
	define_integer		1684957559
	define_integer		1395160943
	define_integer		1095062100
	define_integer		538978637
	define_integer		757080096
	define_integer		1126182189
	define_integer		1952540018
	define_integer		1230446693
	define_integer		1464812622
	define_integer		1684955424
	define_integer		1852142368
	define_integer		1868767332
	define_integer		1851878765
	define_integer		1948283748
	define_integer		1414733935
	define_integer		1296123218
	define_integer		46
'$SCNST_45_25':
	define_desc		3,13
	define_integer		1600414817
	define_integer		1344827503
	define_integer		742606162
	define_integer		1328306516
	define_integer		757082448
	define_integer		1092627757
	define_integer		1864393828
	define_integer		1634887024
	define_integer		544370548
	define_integer		1931505524
	define_integer		1819043176
	define_integer		1852405549
	define_integer		779579236
'$SCNST_45_27':
	define_desc		27,15
	define_integer		1869440370
	define_integer		1868522870
	define_integer		1380984944
	define_integer		1412186949
	define_integer		1347365977
	define_integer		1377840425
	define_integer		1987013989
	define_integer		1886330981
	define_integer		1952543333
	define_integer		1713402479
	define_integer		544042866
	define_integer		1818585203
	define_integer		1769418092
	define_integer		2003788910
	define_integer		46
'$SCNST_45_29':
	define_desc		27,15
	define_integer		1869440370
	define_integer		1868522870
	define_integer		1347364976
	define_integer		538976297
	define_integer		757080096
	define_integer		1377840429
	define_integer		1987013989
	define_integer		1886330981
	define_integer		1952543333
	define_integer		1713402479
	define_integer		544042866
	define_integer		1818585203
	define_integer		1769418092
	define_integer		2003788910
	define_integer		46
'$SCNST_45_31':
	define_desc		11,14
	define_integer		1919250543
	define_integer		1919906913
	define_integer		693129000
	define_integer		538976288
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1701867296
	define_integer		1869898098
	define_integer		1701060722
	define_integer		1768843622
	define_integer		1852795252
	define_integer		543584032
	define_integer		3035215
'$SCNST_45_33':
	define_desc		27,16
	define_integer		1919250543
	define_integer		1919906913
	define_integer		743460648
	define_integer		1279673668
	define_integer		757080105
	define_integer		1193291053
	define_integer		1864397925
	define_integer		1634887024
	define_integer		544370548
	define_integer		1768318308
	define_integer		1769236846
	define_integer		1864396399
	define_integer		1347362918
	define_integer		544175136
	define_integer		1279673668
	define_integer		46
'$SCNST_45_35':
	define_desc		3,6
	define_integer		1819305330
	define_integer		1600480097
	define_integer		1885302895
	define_integer		678195055
	define_integer		742673487
	define_integer		693585230
'$SCNST_45_37':
	define_desc		3,14
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1377840429
	define_integer		1634496613
	define_integer		1864394083
	define_integer		1634887024
	define_integer		544370548
	define_integer		1819242352
	define_integer		1145851680
	define_integer		544175136
	define_integer		777471310
'$SCNST_45_39':
	define_desc		11,13
	define_integer		1851877475
	define_integer		1868522855
	define_integer		1869635440
	define_integer		1311272047
	define_integer		757684037
	define_integer		1126182189
	define_integer		1735287144
	define_integer		1886330981
	define_integer		1952543333
	define_integer		1881174639
	define_integer		543977327
	define_integer		1310748532
	define_integer		3036997
'$SCNST_45_41':
	define_desc		3,10
	define_integer		1953259880
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1159736621
	define_integer		544500088
	define_integer		1397965904
	define_integer		1937339168
	define_integer		778921332
'$SCNST_45_40':
	define_string		'$SCNST_45_41'
	define_atom		[]
'$SCNST_45_38':
	define_string		'$SCNST_45_39'
	define_list		'$SCNST_45_40'
'$SCNST_45_36':
	define_string		'$SCNST_45_37'
	define_list		'$SCNST_45_38'
'$SCNST_45_34':
	define_string		'$SCNST_45_35'
	define_list		'$SCNST_45_36'
'$SCNST_45_32':
	define_string		'$SCNST_45_33'
	define_list		'$SCNST_45_34'
'$SCNST_45_30':
	define_string		'$SCNST_45_31'
	define_list		'$SCNST_45_32'
'$SCNST_45_28':
	define_string		'$SCNST_45_29'
	define_list		'$SCNST_45_30'
'$SCNST_45_26':
	define_string		'$SCNST_45_27'
	define_list		'$SCNST_45_28'
'$SCNST_45_24':
	define_string		'$SCNST_45_25'
	define_list		'$SCNST_45_26'
'$SCNST_45_22':
	define_string		'$SCNST_45_23'
	define_list		'$SCNST_45_24'
'$SCNST_45_20':
	define_string		'$SCNST_45_21'
	define_list		'$SCNST_45_22'
'$SCNST_45_18':
	define_string		'$SCNST_45_19'
	define_list		'$SCNST_45_20'
'$SCNST_45_16':
	define_string		'$SCNST_45_17'
	define_list		'$SCNST_45_18'
'$SCNST_45_14':
	define_string		'$SCNST_45_15'
	define_list		'$SCNST_45_16'
'$SCNST_45_12':
	define_string		'$SCNST_45_13'
	define_list		'$SCNST_45_14'
'$SCNST_45_10':
	define_string		'$SCNST_45_11'
	define_list		'$SCNST_45_12'
'$SCNST_45_8':
	define_string		'$SCNST_45_9'
	define_list		'$SCNST_45_10'
'$SCNST_45_6':
	define_string		'$SCNST_45_7'
	define_list		'$SCNST_45_8'
'$SCNST_45_4':
	define_string		'$SCNST_45_5'
	define_list		'$SCNST_45_6'
'$SCNST_45_2':
	define_string		'$SCNST_45_3'
	define_list		'$SCNST_45_4'
'$SCNST_45_0':
	define_string		'$SCNST_45_1'
	define_list		'$SCNST_45_2'
'$SCNST_45':
	define_list		'$SCNST_45_0'
