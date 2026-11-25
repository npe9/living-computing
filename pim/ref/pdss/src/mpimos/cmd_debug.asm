mpimos_cmd_debug:
	module		mpimos_cmd_debug
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_cmd_debug
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	hash_on_atom		1,4,is_command_2_1
	bucket_entry_a		backtrace,is_command_2_4
	bucket_entry_a		debug,is_command_2_5
	bucket_entry_a		nobacktrace,is_command_2_6
	bucket_entry_a		nodebug,is_command_2_7
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
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,5,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_8
	table_entry		is_command_2_9
	table_entry		is_command_2_10
is_command_2_8:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,9,is_command_2_1
	bucket_entry_a		nospy,is_command_2_12
	bucket_entry_a		notrace,is_command_2_13
	bucket_entry_a		profile,is_command_2_14
	bucket_entry_a		reset_profile,is_command_2_15
	bucket_entry_a		spy,is_command_2_16
	bucket_entry_a		spying,is_command_2_17
	bucket_entry_a		trace,is_command_2_18
	bucket_entry_a		varchk,is_command_2_19
	bucket_entry_a		xref,is_command_2_20
is_command_2_12:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
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
is_command_2_9:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,is_command_2_1
	bucket_entry_a		profile,is_command_2_22
	bucket_entry_a		spying,is_command_2_23
	bucket_entry_a		varchk,is_command_2_24
	bucket_entry_a		xref,is_command_2_25
is_command_2_22:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_23:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
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
is_command_2_10:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,is_command_2_1
	bucket_entry_a		nospy,is_command_2_27
	bucket_entry_a		spy,is_command_2_28
	bucket_entry_a		varchk,is_command_2_29
	bucket_entry_a		xref,is_command_2_30
is_command_2_27:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_28:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
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
is_command_2_1:
	otherwise		is_command_2_0
	collect_value		1
	get_atom		2,no
	proceed
is_command_2_40:
	suspend		is_command_2_0
	module_entry		mpimos_cmd_debug
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	hash_on_atom		1,4,do_command_2_1
	bucket_entry_a		backtrace,do_command_2_4
	bucket_entry_a		debug,do_command_2_5
	bucket_entry_a		nobacktrace,do_command_2_6
	bucket_entry_a		nodebug,do_command_2_7
do_command_2_4:
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_0'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,initenv
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_1'
	put_list_val_val		4,3,1
	get_list_value		2,4
	put_value		1,5
	execute		1,wait_1_0
do_command_2_5:
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_2'
	put_func		4,3,prompt
	write_element_void		4,1
	write_element_value		4,2,1
	put_list_val_val		1,4,3
	put_func		3,2,window
	write_element_value		3,1,1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	put_list		3
	write_car_atom		3,initenv
	write_cdr_value		3,1
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		4,1,3
	get_list_value		2,4
	put_value		1,5
	execute		1,wait_1_0
do_command_2_6:
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_4'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,initenv
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_5'
	put_list_val_val		4,3,1
	get_list_value		2,4
	put_value		1,5
	execute		1,wait_1_0
do_command_2_7:
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_6'
	put_func		4,3,prompt
	write_element_void		4,1
	write_element_value		4,2,1
	put_list_val_val		1,4,3
	put_func		3,2,window
	write_element_value		3,1,1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	put_list		3
	write_car_atom		3,initenv
	write_cdr_value		3,1
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		4,1,3
	get_list_value		2,4
	put_value		1,5
	execute		1,wait_1_0
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,5,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_8
	table_entry		do_command_2_9
	table_entry		do_command_2_10
do_command_2_8:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,9,do_command_2_1
	bucket_entry_a		nospy,do_command_2_12
	bucket_entry_a		notrace,do_command_2_13
	bucket_entry_a		profile,do_command_2_14
	bucket_entry_a		reset_profile,do_command_2_15
	bucket_entry_a		spy,do_command_2_16
	bucket_entry_a		spying,do_command_2_17
	bucket_entry_a		trace,do_command_2_18
	bucket_entry_a		varchk,do_command_2_19
	bucket_entry_a		xref,do_command_2_20
do_command_2_12:
	read_element		1,1,7
	wait_vector		7,3
	read_element		7,0,4
	wait_atom		4,:
	read_element		7,1,4
	read_element		7,2,8
	wait_vector		8,3
	read_element		8,0,5
	wait_atom		5,/
	read_elements_inc		8,1,5,2
	atom		4
	atom		5
	integer		6
	collect_vector		7
	collect_vector		8
	put_reused_func		1,1,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_8'
	put_list_val_val		7,1,3
	put_func		1,2,window
	write_element_value		1,1,7
	put_list_val_var		3,1,7
	put_func		1,6,spy_predicate
	write_elements_inc		1,1,4,3
	write_element_atom		1,4,off
	write_element_variable		1,5,5
	put_func		4,2,code
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	put_value		1,5
	put_value		2,7
	execute		2,write_status_2_0
do_command_2_13:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_22
	collect_vector		1
	put_value		3,2
	put_atom		1,notrace
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_22:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_23
	collect_vector		1
	get_nil		2
	proceed
do_command_2_23:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_reused_func		1,1,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_9'
	put_list_val_val		5,1,3
	put_func		1,2,window
	write_element_value		1,1,5
	put_list_val_var		3,1,5
	put_func		1,4,trace_module
	write_element_value		1,1,4
	write_element_atom		1,2,off
	write_element_variable		1,3,6
	put_func		4,2,code
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	put_values_dec		1,6,2
	execute		2,write_status_2_0
do_command_2_14:
	read_element		1,1,4
	collect_vector		1
	put_func		1,3,profile
	write_element_value		1,1,4
	write_element_atom		1,2,call
	execute		2,do_command_2_0
do_command_2_15:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_25
	collect_vector		1
	put_value		3,2
	put_atom		1,reset_profile
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_25:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_26
	collect_vector		1
	get_nil		2
	proceed
do_command_2_26:
	put_nil		5
	g_diff		4,5
	collect_value		5
	collect_vector		1
	put_marked_value		1,4
	b_reset_profile_info		1,3
	put_value		1,2
	put_value		2,4
	execute		3,wait_reset_profile_3_0
do_command_2_16:
	read_element		1,1,7
	wait_vector		7,3
	read_element		7,0,4
	wait_atom		4,:
	read_element		7,1,4
	read_element		7,2,8
	wait_vector		8,3
	read_element		8,0,5
	wait_atom		5,/
	read_elements_inc		8,1,5,2
	atom		4
	atom		5
	integer		6
	collect_vector		7
	collect_vector		8
	put_reused_func		1,1,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_10'
	put_list_val_val		7,1,3
	put_func		1,2,window
	write_element_value		1,1,7
	put_list_val_var		3,1,7
	put_func		1,6,spy_predicate
	write_element_marked_value		1,1,4
	write_elements_inc		1,2,5,2
	write_element_atom		1,4,on
	write_element_variable		1,5,6
	put_func		5,2,code
	write_element_value		5,1,1
	put_list_val_val		1,5,3
	get_list_value		2,1
	put_value		1,6
	put_value		2,4
	put_value		3,7
	execute		3,wait_spy_mode_3_0
do_command_2_17:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_28
	collect_vector		1
	put_value		3,2
	put_atom		1,spying
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_28:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_29
	collect_vector		1
	get_nil		2
	proceed
do_command_2_29:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_func		3,4,get_spied_predicates
	write_element_value		3,1,4
	write_element_variable		3,2,5
	write_element_variable		3,3,4
	put_reused_func		1,1,code
	write_element_value		1,1,3
	get_list_val_var		2,6,1,3
	put_values_inc		1,4,2
	execute		3,wait_spied_pred_3_0
do_command_2_18:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_31
	collect_vector		1
	put_value		3,2
	put_atom		1,trace
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_31:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_32
	collect_vector		1
	get_nil		2
	proceed
do_command_2_32:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_reused_func		1,1,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_11'
	put_list_val_val		5,1,3
	put_func		1,2,window
	write_element_value		1,1,5
	put_list_val_var		3,1,5
	put_func		1,4,trace_module
	write_element_value		1,1,4
	write_element_atom		1,2,on
	write_element_variable		1,3,6
	put_func		4,2,code
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	put_values_dec		1,6,2
	execute		2,wait_debug_mode_2_0
do_command_2_19:
	read_element		1,1,4
	collect_vector		1
	put_func		1,4,varchk
	write_element_value		1,1,4
	write_element_atom		1,2,one
	write_element_atom		1,3,p
	execute		2,do_command_2_0
do_command_2_20:
	read_element		1,1,4
	collect_vector		1
	put_func		1,3,xref
	write_element_value		1,1,4
	write_element_atom		1,2,check
	execute		2,do_command_2_0
do_command_2_9:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,do_command_2_1
	bucket_entry_a		profile,do_command_2_34
	bucket_entry_a		spying,do_command_2_35
	bucket_entry_a		varchk,do_command_2_36
	bucket_entry_a		xref,do_command_2_37
do_command_2_34:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_39
	read_element		1,2,5
	atom		5
	collect_vector		1
	put_func		1,2,getuc
	write_element_variable		1,1,6
	get_list_val_var		2,7,1,3
	put_structured_constant		1,'$SCNST_12'
	put_variable		7,2
	b_append_string		1,7,1
	create_goal		4
	set_variable		1,8
	set_value		2,5
	set_variable		3,5
	set_variable		4,7
	enqueue_goal		4,profile_info_4_0
	create_goal		4
	set_value		1,4
	set_value		2,8
	set_value		3,3
	set_value		4,7
	enqueue_goal		4,correct_module_4_0
	create_goal		2
	put_list		3
	write_car_atom		3,show
	write_cdr_value		3,5
	set_value		1,3
	set_value		2,1
	enqueue_goal_external		mpimos_window,create,2
	put_value		1,6
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_39:
	is_atom		4,do_command_2_1
	read_element		1,2,5
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,profile
	write_element_value		1,1,3
	write_element_value		1,2,5
	execute		2,do_command_2_0
do_command_2_35:
	read_elements_inc		1,1,4,2
	atom		4
	collect_vector		1
	put_func		1,4,get_spied_predicates
	write_element_value		1,1,4
	write_element_variable		1,2,6
	write_element_variable		1,3,4
	put_func		3,2,code
	write_element_value		3,1,1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	put_value		1,4
	put_values_dec		2,6,2
	execute		3,wait_spied_pred1_3_0
do_command_2_36:
	read_elements_inc		1,1,4,2
	collect_vector		1
	put_func		1,4,varchk
	write_elements_inc		1,1,4,2
	write_element_atom		1,3,p
	execute		2,do_command_2_0
do_command_2_37:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_41,do_command_2_1,do_command_2_42,do_command_2_1,do_command_2_43,do_command_2_1
do_command_2_42:
	read_element		1,2,5
	collect_vector		1
	put_func		1,2,getuc
	write_element_variable		1,1,6
	get_list_val_var		2,7,1,3
	put_structured_constant		1,'$SCNST_13'
	put_variable		7,2
	b_append_string		1,7,1
	create_goal		3
	set_variable		1,7
	set_value		2,5
	set_value		3,1
	enqueue_goal_external		mpimos_xref,go,3
	create_goal		4
	set_value		1,4
	set_value		2,7
	set_value		3,3
	set_nil		4
	enqueue_goal		4,correct_files_4_0
	put_value		1,6
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_41:
	read_element		1,2,5
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,xref
	write_element_value		1,1,3
	write_element_value		1,2,5
	execute		2,do_command_2_0
do_command_2_43:
	read_element		1,2,5
	g_string		4,3,6
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,xref
	write_element_value		1,1,3
	write_element_value		1,2,5
	execute		2,do_command_2_0
do_command_2_10:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,do_command_2_1
	bucket_entry_a		nospy,do_command_2_45
	bucket_entry_a		spy,do_command_2_46
	bucket_entry_a		varchk,do_command_2_47
	bucket_entry_a		xref,do_command_2_48
do_command_2_45:
	read_elements_inc		1,1,4,3
	atom		4
	atom		5
	integer		6
	collect_vector		1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_14'
	put_list_val_val		7,1,3
	put_func		1,2,window
	write_element_value		1,1,7
	put_list_val_var		3,1,7
	put_func		1,6,spy_predicate
	write_elements_inc		1,1,4,3
	write_element_atom		1,4,off
	write_element_variable		1,5,5
	put_func		4,2,code
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	put_value		1,5
	put_value		2,7
	execute		2,write_status_2_0
do_command_2_46:
	read_elements_inc		1,1,4,3
	atom		4
	atom		5
	integer		6
	collect_vector		1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_15'
	put_list_val_val		7,1,3
	put_func		1,2,window
	write_element_value		1,1,7
	put_list_val_var		3,1,7
	put_func		1,6,spy_predicate
	write_element_marked_value		1,1,4
	write_elements_inc		1,2,5,2
	write_element_atom		1,4,on
	write_element_variable		1,5,6
	put_func		5,2,code
	write_element_value		5,1,1
	put_list_val_val		1,5,3
	get_list_value		2,1
	put_value		1,6
	put_value		2,4
	put_value		3,7
	execute		3,wait_spy_mode_3_0
do_command_2_47:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_49,do_command_2_1,do_command_2_50,do_command_2_1,do_command_2_51,do_command_2_1
do_command_2_50:
	read_element		1,2,5
	atom		5
	read_element		1,3,6
	atom		6
	collect_vector		1
	put_value		7,2
	put_func		3,3,','
	write_elements_inc		3,1,5,2
	put_atom		1,varchk
	put_value		2,4
	put_value		4,7
	execute_external		mpimos_cmd_utl,apply_action,4
do_command_2_49:
	read_elements_inc		1,2,5,2
	collect_vector		1
	b_atom_name		4,1
	create_goal		4
	set_variable		1,3
	set_values_inc		2,5,2
	set_value		4,2
	enqueue_goal		4,varchk_4_0
	put_structured_constant		2,'$SCNST_16'
	execute_external		mpimos_utility,extend_name,3
do_command_2_51:
	read_elements_inc		1,2,5,2
	g_string		4,3,7
	collect_vector		1
	create_goal		4
	set_variable		1,3
	set_values_inc		2,5,2
	set_value		4,2
	enqueue_goal		4,varchk_4_0
	put_value		1,4
	put_structured_constant		2,'$SCNST_17'
	execute_external		mpimos_utility,extend_name,3
do_command_2_48:
	read_element		1,1,4
	try_me_else		do_command_2_53
	wait		4
	switch_on_type		4,do_command_2_54,do_command_2_53,do_command_2_55,do_command_2_53,do_command_2_56,do_command_2_53
do_command_2_55:
	read_elements_inc		1,2,5,2
	string		6
	g_string		6,3,7
	collect_vector		1
	put_func		1,2,getuc
	write_element_variable		1,1,7
	get_list_val_var		2,8,1,3
	put_structured_constant		1,'$SCNST_18'
	put_variable		8,2
	b_append_string		1,8,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,5,2
	set_value		4,1
	enqueue_goal_external		mpimos_xref,go_f,4
	create_goal		4
	set_value		1,4
	set_value		2,8
	set_value		3,3
	set_nil		4
	enqueue_goal		4,correct_files_4_0
	put_value		1,7
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_54:
	read_elements_inc		1,2,5,2
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,xref
	write_element_value		1,1,3
	write_elements_inc		1,2,5,2
	execute		2,do_command_2_0
do_command_2_56:
	read_elements_inc		1,2,5,2
	g_string		4,3,7
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,xref
	write_element_value		1,1,3
	write_elements_inc		1,2,5,2
	execute		2,do_command_2_0
do_command_2_53:
	read_elements_inc		1,2,5,2
	try_me_else		do_command_2_1
	atom		6
	b_atom_name		6,3
	put_reused_func		1,1,xref
	write_elements_inc		1,1,4,2
	write_element_value		1,3,3
	execute		2,do_command_2_0
do_command_2_1:
	otherwise		do_command_2_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_19'
	put_func		4,2,putt
	write_element_variable		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_20'
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
do_command_2_102:
	suspend		do_command_2_0
	module_entry		mpimos_cmd_debug
	predicate		wait_spied_pred,3
wait_spied_pred_3_0:
	try_me_else		wait_spied_pred_3_1
	wait_atom		1,success
	try_me_else		wait_spied_pred_3_3
	wait_nil		2
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_21'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,wait_1_0
wait_spied_pred_3_3:
	try_me_else		wait_spied_pred_3_1
	put_nil		4
	g_diff		2,4
	collect_value		4
	put_values_inc		1,2,2
	execute		2,listing_predicates_2_0
wait_spied_pred_3_1:
	otherwise		wait_spied_pred_3_0
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,6
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_structured_constant		2,'$SCNST_22'
	put_list_val_val		5,2,4
	put_func		2,2,putt
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_structured_constant		2,'$SCNST_23'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,6
	execute		1,fail_action_1_0
wait_spied_pred_3_10:
	suspend		wait_spied_pred_3_0
	module_entry		mpimos_cmd_debug
	predicate		listing_predicates,2
listing_predicates_2_0:
	try_me_else		listing_predicates_2_1
	jump_on_non_list_var_var		1,listing_predicates_2_3,7,3
	wait_vector		7,2
	read_elements_inc		7,0,4,2
	put_structured_constant		6,'$SCNST_24'
	put_reused_func		7,7,putt
	write_element_value		7,1,5
	put_reused_list_val_val		1,1,7,6
	put_structured_constant		5,'$SCNST_25'
	put_list_val_val		6,5,1
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_func		1,2,window
	write_element_value		1,1,4
	get_list_val_var		2,5,1,4
	put_values_inc		1,3,2
	execute		2,listing_predicates_2_0
listing_predicates_2_3:
	check_nil		1,listing_predicates_2_1
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_26'
	put_list_val_val		4,1,3
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,5
	execute		1,wait_1_0
listing_predicates_2_1:
	suspend		listing_predicates_2_0
	module_entry		mpimos_cmd_debug
	predicate		wait_spied_pred1,3
wait_spied_pred1_3_0:
	try_me_else		wait_spied_pred1_3_1
	wait_atom		1,success
	get_value		3,2
	proceed
wait_spied_pred1_3_1:
	otherwise		wait_spied_pred1_3_0
	collect_value		2
	collect_value		1
	get_nil		3
	proceed
wait_spied_pred1_3_6:
	suspend		wait_spied_pred1_3_0
	module_entry		mpimos_cmd_debug
	predicate		wait_spy_mode,3
wait_spy_mode_3_0:
	try_me_else		wait_spy_mode_3_1
	wait_atom		1,success
	put_func		1,4,trace_module
	write_element_value		1,1,2
	write_element_atom		1,2,on
	write_element_void		1,3
	put_func		2,2,code
	write_element_value		2,1,1
	get_list_val_var		3,1,2,2
	put_atom		1,success
	execute		2,wait_debug_mode_2_0
wait_spy_mode_3_1:
	otherwise		wait_spy_mode_3_0
	collect_value		2
	put_value		2,3
	execute		2,wait_debug_mode_2_0
wait_spy_mode_3_6:
	suspend		wait_spy_mode_3_0
	module_entry		mpimos_cmd_debug
	predicate		write_status,2
write_status_2_0:
	try_me_else		write_status_2_1
	wait_atom		1,success
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_27'
	put_list_val_val		4,1,3
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,5
	execute		1,wait_1_0
write_status_2_1:
	otherwise		write_status_2_0
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
	put_func		3,2,window
	write_element_value		3,1,1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	put_value		1,5
	execute		1,wait_1_0
write_status_2_6:
	suspend		write_status_2_0
	module_entry		mpimos_cmd_debug
	predicate		wait_debug_mode,2
wait_debug_mode_2_0:
	try_me_else		wait_debug_mode_2_1
	wait_atom		1,success
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_28'
	put_func		4,3,prompt
	write_element_void		4,1
	write_element_value		4,2,1
	put_list_val_val		1,4,3
	put_structured_constant		3,'$SCNST_29'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,initenv
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_30'
	put_list_val_val		4,3,1
	get_list_value		2,4
	put_value		1,5
	execute		1,wait_1_0
wait_debug_mode_2_1:
	otherwise		wait_debug_mode_2_0
	put_func		3,2,flush
	write_element_variable		3,1,6
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_31'
	put_list_val_val		5,3,4
	put_func		3,2,putt
	write_element_value		3,1,1
	put_list_val_val		1,3,5
	put_structured_constant		3,'$SCNST_32'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,6
	execute		1,fail_action_1_0
wait_debug_mode_2_6:
	suspend		wait_debug_mode_2_0
	module_entry		mpimos_cmd_debug
	predicate		correct_module,4
correct_module_4_0:
	try_me_else		correct_module_4_1
	jump_on_non_list		1,correct_module_4_3
	read_car		1,5
	atom		5
	test_nil		5,correct_module_4_5
	try_me_else		correct_module_4_5
	read_cdr		1,6
	wait_nil		6
	collect_list		1
	get_nil		2
	get_value		3,4
	proceed
correct_module_4_5:
	try_me_else		correct_module_4_1
	read_cdr		1,6
	put_nil		7
	g_diff		5,7
	collect_value		7
	get_reused_list_val_var		2,1,1,5,5
	put_values_dec		1,6,2
	execute		4,correct_module_4_0
correct_module_4_3:
	check_nil		1,correct_module_4_1
	get_nil		2
	get_value		3,4
	proceed
correct_module_4_1:
	otherwise		correct_module_4_0
	try_me_else		correct_module_4_13
	wait_list_var_var		1,5,6
	collect_value		4
	collect_value		2
	collect_value		6
	put_func		2,2,flush
	write_element_variable		2,1,7
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,1
	put_func		1,2,putt
	write_element_variable		1,1,6
	put_list_val_val		4,1,2
	put_structured_constant		1,'$SCNST_33'
	put_list_val_val		2,1,4
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	create_goal		1
	set_value		1,7
	enqueue_goal		1,fail_action_1_0
	put_values_inc		1,5,2
	execute_external		mpimos_utility,freeze,2
correct_module_4_13:
	suspend		correct_module_4_0
	module_entry		mpimos_cmd_debug
	predicate		wait_reset_profile,3
wait_reset_profile_3_0:
	try_me_else		wait_reset_profile_3_1
	wait_integer		3,0
	collect_value		2
	get_nil		1
	proceed
wait_reset_profile_3_1:
	otherwise		wait_reset_profile_3_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_structured_constant		4,'$SCNST_34'
	put_func		5,2,putt
	write_element_value		5,1,2
	put_list_val_val		2,5,4
	put_structured_constant		4,'$SCNST_35'
	put_list_val_val		5,4,2
	put_func		2,2,putt
	write_element_variable		2,1,6
	put_list_val_val		4,2,5
	put_structured_constant		2,'$SCNST_36'
	put_list_val_val		5,2,4
	put_func		2,2,window
	write_element_value		2,1,5
	set_values_dec		1,2,2
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
	put_value		1,3
	put_value		2,6
	execute		2,profile_status_2_0
wait_reset_profile_3_6:
	suspend		wait_reset_profile_3_0
	module_entry		mpimos_cmd_debug
	predicate		profile_info,4
profile_info_4_0:
	try_me_else		profile_info_4_1
	jump_on_non_list_var_var		1,profile_info_4_3,5,6
	collect_list		1
	put_values_inc		9,2,2
	put_value		7,4
	put_marked_value		1,5
	b_get_profile_info		1,3,1
	create_goal		4
	set_value		1,6
	set_marked_value		2,9
	set_variable		3,6
	set_variable		4,8
	enqueue_goal		4,profile_info_4_0
	put_value		2,5
	put_values_inc		4,9,2
	execute		8,wait_get_profile_8_0
profile_info_4_3:
	check_nil		1,profile_info_4_1
	collect_value		2
	put_func		1,2,getl
	write_element_void		1,1
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_structured_constant		1,'$SCNST_37'
	put_list_val_val		5,1,2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,5
	get_list_value		3,1
	put_func		1,2,flush
	write_element_variable		1,1,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		4,2
	put_value		1,3
	execute		1,wait_1_0
profile_info_4_1:
	suspend		profile_info_4_0
	module_entry		mpimos_cmd_debug
	predicate		wait_get_profile,8
wait_get_profile_8_0:
	try_me_else		wait_get_profile_8_1
	wait_integer		1,0
	get_value		7,8
	put_func		1,2,putl
	write_element_marked_variable		1,1,10
	put_list_val_var		7,1,9
	put_structured_constant		1,'$SCNST_38'
	put_list_val_val		8,1,7
	put_func		1,2,tab
	write_element_variable		1,1,11
	put_list_val_val		7,1,8
	put_structured_constant		1,'$SCNST_39'
	put_list_val_val		8,1,7
	put_func		1,2,tab
	write_element_variable		1,1,12
	put_list_val_val		7,1,8
	put_func		1,2,tab
	write_element_variable		1,1,13
	put_list_val_val		8,1,7
	put_structured_constant		1,'$SCNST_40'
	put_list_val_val		7,1,8
	put_func		1,2,putl
	write_element_value		1,1,10
	put_list_val_val		8,1,7
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,8
	put_func		7,2,putt
	write_element_value		7,1,2
	put_list_val_val		2,7,1
	put_structured_constant		1,'$SCNST_41'
	put_list_val_val		7,1,2
	get_list_value		5,7
	put_marked_variable		1,2
	put_marked_variable		7,5
	b_add		1,7,1
	put_marked_variable		8,7
	b_add		1,8,1
	put_integer		8,9
	b_add		1,8,1
	put_value		8,1
	put_integer		1,6
	b_subtract		2,1,1
	get_value		13,1
	put_integer		1,2
	b_subtract		5,1,1
	get_value		12,1
	put_integer		1,2
	b_subtract		7,1,1
	get_value		11,1
	create_goal		12
	set_variable		1,1
	set_value		2,9
	set_value		3,6
	set_value		4,10
	set_integer		5,6
	set_value		6,2
	set_integer		7,4
	set_value		8,5
	set_integer		9,4
	set_value		10,7
	set_integer		11,0
	set_integer		12,0
	enqueue_goal		12,put_profile_info_12_0
	create_goal		3
	set_value		1,3
	set_value		2,1
	set_value		3,4
	enqueue_goal		3,sort_profile_info_3_0
	put_integer		1,45
	put_value		2,8
	put_value		3,10
	execute		3,line_3_0
wait_get_profile_8_1:
	otherwise		wait_get_profile_8_0
	collect_value		4
	collect_value		3
	get_value		5,6
	create_goal		1
	set_variable		1,6
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_42'
	put_func		4,2,putt
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_43'
	put_list_val_val		4,3,2
	put_func		2,2,putt
	write_element_variable		2,1,5
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_44'
	put_list_val_val		4,2,3
	put_func		2,2,window
	write_element_value		2,1,4
	set_value		1,2
	set_value		2,7
	put_func		2,2,flush
	write_element_value		2,1,6
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list_val_val		3,2,8
	set_value		3,3
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_value		2,5
	execute		2,profile_status_2_0
wait_get_profile_8_6:
	suspend		wait_get_profile_8_0
	module_entry		mpimos_cmd_debug
	predicate		sort_profile_info,3
sort_profile_info_3_0:
	try_me_else		sort_profile_info_3_1
	atom		3
	hash_on_atom		3,4,sort_profile_info_3_1
	bucket_entry_a		c,sort_profile_info_3_3
	bucket_entry_a		call,sort_profile_info_3_4
	bucket_entry_a		s,sort_profile_info_3_5
	bucket_entry_a		susp,sort_profile_info_3_6
sort_profile_info_3_3:
	create_goal		4
	set_variable		1,3
	set_integer		2,2
	set_value		3,2
	set_atom		4,reverse
	enqueue_goal_external		mpimos_utility,qsortv,4
	put_integer		2,3
	put_atom		4,reverse
	execute_external		mpimos_utility,qsortv,4
sort_profile_info_3_4:
	create_goal		4
	set_variable		1,3
	set_integer		2,2
	set_value		3,2
	set_atom		4,reverse
	enqueue_goal_external		mpimos_utility,qsortv,4
	put_integer		2,3
	put_atom		4,reverse
	execute_external		mpimos_utility,qsortv,4
sort_profile_info_3_5:
	create_goal		4
	set_variable		1,3
	set_integer		2,3
	set_value		3,2
	set_atom		4,reverse
	enqueue_goal_external		mpimos_utility,qsortv,4
	put_integer		2,2
	put_atom		4,reverse
	execute_external		mpimos_utility,qsortv,4
sort_profile_info_3_6:
	create_goal		4
	set_variable		1,3
	set_integer		2,3
	set_value		3,2
	set_atom		4,reverse
	enqueue_goal_external		mpimos_utility,qsortv,4
	put_integer		2,2
	put_atom		4,reverse
	execute_external		mpimos_utility,qsortv,4
sort_profile_info_3_1:
	otherwise		sort_profile_info_3_0
	collect_value		3
	get_value		2,1
	proceed
sort_profile_info_3_9:
	suspend		sort_profile_info_3_0
	module_entry		mpimos_cmd_debug
	predicate		put_profile_info,12
put_profile_info_12_0:
	try_me_else		put_profile_info_12_1
	jump_on_non_list_var_var		1,put_profile_info_12_3,18,13
	wait_vector		18,4
	read_elements_inc		18,0,14,4
	collect_vector		18
	put_structured_constant		18,'$SCNST_45'
	put_reused_list_val_var		1,1,18,20
	put_func		18,2,putt
	write_element_marked_value		18,1,17
	put_list_val_val		19,18,1
	put_func		1,2,tab
	write_element_variable		1,1,21
	put_list_val_val		18,1,19
	put_func		1,2,putt
	write_element_marked_value		1,1,16
	put_list_val_val		19,1,18
	put_func		1,2,tab
	write_element_variable		1,1,22
	put_list_val_val		18,1,19
	put_func		1,2,tab
	write_element_variable		1,1,23
	put_list_val_val		19,1,18
	put_func		1,2,putt
	write_element_marked_value		1,1,15
	put_list_val_val		18,1,19
	put_structured_constant		1,'$SCNST_46'
	put_list_val_val		19,1,18
	put_func		1,2,putb
	write_element_variable		1,1,24
	put_list_val_val		18,1,19
	put_structured_constant		1,'$SCNST_47'
	put_list_val_val		19,1,18
	get_list_value		2,19
	b_atom_name		14,1
	b_string		1,1,2,14
	get_value		14,24
	put_marked_value		2,6
	put_marked_value		14,1
	b_subtract		2,14,2
	put_variable		18,14
	b_subtract		2,18,2
	put_integer		18,2
	b_add		2,18,2
	get_value		23,2
	put_marked_value		2,8
	put_variable		19,18
	b_subtract		2,19,2
	put_integer		19,2
	b_add		2,19,2
	get_value		22,2
	put_marked_value		2,10
	put_variable		22,19
	b_subtract		2,22,2
	put_integer		22,2
	b_add		2,22,2
	get_value		21,2
	b_max		5,1,1
	b_add		11,16,2
	b_add		12,17,5
	create_goal		12
	set_value		1,13
	set_value		2,20
	set_values_inc		3,3,2
	set_value		5,1
	set_values_inc		6,6,5
	set_value		11,2
	set_value		12,5
	enqueue_goal		12,put_profile_info_12_0
	create_goal		2
	set_value		1,17
	set_value		2,19
	enqueue_goal		2,width_2_0
	create_goal		2
	set_value		1,16
	set_value		2,18
	enqueue_goal		2,width_2_0
	put_values_dec		1,15,2
	execute		2,width_2_0
put_profile_info_12_3:
	check_nil		1,put_profile_info_12_1
	put_func		1,2,flush
	write_element_void		1,1
	put_list_val_val		13,1,3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,13
	put_func		3,2,putl
	write_element_marked_value		3,1,4
	put_list_val_val		13,3,1
	put_structured_constant		1,'$SCNST_48'
	put_list_val_val		3,1,13
	put_func		1,2,putt
	write_element_marked_value		1,1,12
	put_list_val_val		13,1,3
	put_func		1,2,tab
	write_element_variable		1,1,14
	put_list_val_val		3,1,13
	put_func		1,2,putt
	write_element_marked_value		1,1,11
	put_list_val_val		13,1,3
	put_func		1,2,tab
	write_element_variable		1,1,15
	put_list_val_val		3,1,13
	put_func		1,2,tab
	write_element_variable		1,1,16
	put_list_val_val		13,1,3
	put_structured_constant		1,'$SCNST_49'
	put_list_val_val		3,1,13
	put_structured_constant		1,'$SCNST_50'
	put_list_val_val		13,1,3
	put_func		1,2,putl
	write_element_value		1,1,4
	put_list_val_val		3,1,13
	get_list_value		2,3
	put_marked_value		6,6
	get_value		6,16
	put_marked_value		1,8
	put_marked_variable		3,2
	b_subtract		1,3,1
	put_integer		3,2
	b_add		1,3,1
	get_value		15,1
	put_marked_value		1,10
	put_marked_variable		4,3
	b_subtract		1,4,1
	put_integer		4,2
	b_add		1,4,1
	get_value		14,1
	put_integer		1,3
	b_max		1,5,1
	get_value		1,6
	b_max		2,7,1
	get_value		1,8
	b_max		3,9,1
	get_value		1,10
	create_goal		2
	set_value		1,12
	set_value		2,3
	enqueue_goal		2,width_2_0
	put_value		1,11
	execute		2,width_2_0
put_profile_info_12_1:
	suspend		put_profile_info_12_0
	module_entry		mpimos_cmd_debug
	predicate		line,3
line_3_0:
	put_value		6,1
	put_value		5,3
	put_marked_value		1,2
	put_integer		3,8
	b_new_string		4,1,3
	put_integer		1,0
	put_value		3,6
	execute		5,line_5_0
line_3_1:
	suspend		line_3_0
	module_entry		mpimos_cmd_debug
	predicate		line,5
line_5_0:
	try_me_else		line_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	put_marked_value		7,3
	b_set_string_element		4,6,7,4
	b_increment		1,1
	execute		5,line_5_0
line_5_1:
	try_me_else		line_5_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,4
	proceed
line_5_3:
	suspend		line_5_0
	module_entry		mpimos_cmd_debug
	predicate		width,2
width_2_0:
	put_value		3,2
	put_integer		2,1
	execute		3,width_3_0
width_2_1:
	suspend		width_2_0
	module_entry		mpimos_cmd_debug
	predicate		width,3
width_3_0:
	try_me_else		width_3_1
	integer		1
	put_integer		4,10
	g_divide		1,4,4
	try_me_else		width_3_3
	put_integer		5,0
	g_less_than		5,4
	put_integer		4,10
	b_divide		1,4,1
	b_increment		2,2
	execute		3,width_3_0
width_3_3:
	try_me_else		width_3_1
	put_integer		5,0
	g_equal		4,5
	get_value		3,2
	proceed
width_3_1:
	suspend		width_3_0
	module_entry		mpimos_cmd_debug
	predicate		profile_status,2
profile_status_2_0:
	try_me_else		profile_status_2_1
	integer		1
	jump_on_integer		1,5,profile_status_2_1
	table_entry		profile_status_2_1
	table_entry		profile_status_2_3
	table_entry		profile_status_2_1
	table_entry		profile_status_2_1
	table_entry		profile_status_2_4
profile_status_2_3:
	get_atom		2,module_not_found
	proceed
profile_status_2_4:
	get_atom		2,native_code_module
	proceed
profile_status_2_1:
	suspend		profile_status_2_0
	module_entry		mpimos_cmd_debug
	predicate		varchk,4
varchk_4_0:
	put_func		5,2,getuc
	write_element_variable		5,1,6
	put_list		7
	write_car_value		7,5
	write_cdr_nil		7
	get_list_value		4,7
	put_structured_constant		4,'$SCNST_51'
	put_variable		7,5
	b_append_string		4,7,4
	create_goal		4
	set_value		1,1
	set_value		2,4
	set_values_inc		3,2,2
	enqueue_goal		4,varchk_go_4_0
	put_values_dec		1,6,2
	execute_external		mpimos_utility,integer_to_string,2
varchk_4_1:
	suspend		varchk_4_0
	module_entry		mpimos_cmd_debug
	predicate		varchk_go,4
varchk_go_4_0:
	try_me_else		varchk_go_4_1
	atom		4
	branch_on_atom		4,2,varchk_go_4_1
	bucket_entry_a		s,varchk_go_4_3
	bucket_entry_a		short,varchk_go_4_4
varchk_go_4_3:
	execute_external		mpimos_varchk,go,3
varchk_go_4_4:
	execute_external		mpimos_varchk,go,3
varchk_go_4_1:
	otherwise		varchk_go_4_0
	collect_value		4
	execute_external		mpimos_varchk,go_p,3
varchk_go_4_7:
	suspend		varchk_go_4_0
	module_entry		mpimos_cmd_debug
	predicate		correct_files,4
correct_files_4_0:
	try_me_else		correct_files_4_1
	jump_on_non_list		1,correct_files_4_3
	read_car		1,5
	jump_on_non_atom		5,correct_files_4_5
	test_nil		5,correct_files_4_6
	try_me_else		correct_files_4_6
	read_cdr		1,6
	wait_nil		6
	collect_list		1
	get_nil		2
	get_value		3,4
	proceed
correct_files_4_6:
	try_me_else		correct_files_4_1
	read_cdr		1,6
	put_nil		7
	g_diff		5,7
	collect_value		7
	b_atom_name		5,5
	put_reused_list		8,1
	write_car_variable		8,7
	write_cdr_variable		8,1
	get_list_value		2,8
	create_goal		4
	set_value		1,6
	set_value		2,1
	set_values_inc		3,3,2
	enqueue_goal		4,correct_files_4_0
	put_value		1,5
	put_structured_constant		2,'$SCNST_52'
	put_value		3,7
	execute_external		mpimos_utility,extend_name,3
correct_files_4_5:
	is_string		5,correct_files_4_1
	read_cdr		1,6
	g_string		5,7,8
	put_reused_list		8,1
	write_car_variable		8,7
	write_cdr_variable		8,1
	get_list_value		2,8
	create_goal		4
	set_value		1,6
	set_value		2,1
	set_values_inc		3,3,2
	enqueue_goal		4,correct_files_4_0
	put_value		1,5
	put_structured_constant		2,'$SCNST_53'
	put_value		3,7
	execute_external		mpimos_utility,extend_name,3
correct_files_4_3:
	check_nil		1,correct_files_4_1
	get_nil		2
	get_value		3,4
	proceed
correct_files_4_1:
	otherwise		correct_files_4_0
	try_me_else		correct_files_4_16
	wait_list_var_var		1,5,6
	collect_value		4
	collect_value		2
	collect_value		6
	put_func		2,2,flush
	write_element_variable		2,1,7
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,1
	put_func		1,2,putt
	write_element_variable		1,1,6
	put_list_val_val		4,1,2
	put_structured_constant		1,'$SCNST_54'
	put_list_val_val		2,1,4
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	create_goal		1
	set_value		1,7
	enqueue_goal		1,fail_action_1_0
	put_values_inc		1,5,2
	execute_external		mpimos_utility,freeze,2
correct_files_4_16:
	suspend		correct_files_4_0
	module_entry		mpimos_cmd_debug
	predicate		fail_action,1
fail_action_1_0:
	try_me_else		fail_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_55'
	put_void		3
	b_raise		2,1,3
	proceed
fail_action_1_1:
	suspend		fail_action_1_0
	module_entry		mpimos_cmd_debug
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait		1
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_cmd_debug
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,debug
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_56'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_57'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_cmd_debug
'$SCNST_0_1':
	define_desc		3,4
	define_integer		1953785171
	define_integer		543649385
	define_integer		539897390
	define_integer		1701736292
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		backtrace
	define_atom		on
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		19,3
	define_integer		1650811995
	define_integer		1063085941
	define_integer		8237
'$SCNST_28':
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		trace
	define_atom		on
'$SCNST_30':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		19,5
	define_integer		1702061394
	define_integer		1852404852
	define_integer		774774887
	define_integer		1868832814
	define_integer		25966
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		backtrace
	define_atom		off
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_0':
	define_desc		27,2
	define_integer		759111804
	define_integer		32
'$SCNST_6':
	define_string		'$SCNST_6_0'
'$SCNST_7_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		trace
	define_atom		off
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		19,4
	define_integer		1702061394
	define_integer		1852404852
	define_integer		774774887
	define_integer		8238
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_14':
'$SCNST_9':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_10_1':
	define_desc		3,3
	define_integer		1953785171
	define_integer		543649385
	define_integer		539897390
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_10_1'
'$SCNST_15':
'$SCNST_11':
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_12_0':
	define_desc		11,2
	define_integer		1718579824
	define_integer		6646889
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_13_0':
	define_desc		3,1
	define_integer		1717924472
'$SCNST_18':
'$SCNST_13':
	define_string		'$SCNST_13_0'
'$SCNST_16_0':
	define_desc		11,1
	define_integer		3239019
'$SCNST_53':
'$SCNST_52':
'$SCNST_17':
'$SCNST_16':
	define_string		'$SCNST_16_0'
'$SCNST_19_0':
	define_atom		nl
	define_atom		[]
'$SCNST_42':
'$SCNST_34':
'$SCNST_19':
	define_list		'$SCNST_19_0'
'$SCNST_20_1':
	define_desc		19,7
	define_integer		1969713729
	define_integer		1953391981
	define_integer		1869771333
	define_integer		1701060722
	define_integer		1952671092
	define_integer		1763730533
	define_integer		8302
'$SCNST_20_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_20_1'
'$SCNST_54':
'$SCNST_33':
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_1':
	define_desc		19,2
	define_integer		1953525061
	define_integer		11897
'$SCNST_21_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_21_1'
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_1':
	define_desc		27,1
	define_integer		62
'$SCNST_22_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_22_1'
'$SCNST_31':
'$SCNST_22':
	define_vector		'$SCNST_22_0'
'$SCNST_23_1':
	define_desc		3,2
	define_integer		1869771333
	define_integer		1008738418
'$SCNST_23_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_23_1'
'$SCNST_23':
	define_vector		'$SCNST_23_0'
'$SCNST_24_2':
	define_desc		19,1
	define_integer		8236
'$SCNST_24_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_24_2'
'$SCNST_24_0':
	define_vector		'$SCNST_24_1'
	define_atom		[]
'$SCNST_24':
	define_list		'$SCNST_24_0'
'$SCNST_25_1':
	define_desc		27,1
	define_integer		47
'$SCNST_25_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_25_1'
'$SCNST_46':
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_26_1':
	define_desc		3,1
	define_integer		776228421
'$SCNST_26_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_26_1'
'$SCNST_26':
	define_vector		'$SCNST_26_0'
'$SCNST_27_1':
	define_desc		3,1
	define_integer		1701736292
'$SCNST_27_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_27_1'
'$SCNST_29':
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_32_1':
	define_desc		11,2
	define_integer		1869771333
	define_integer		3940466
'$SCNST_32_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_32_1'
'$SCNST_44':
'$SCNST_36':
'$SCNST_32':
	define_vector		'$SCNST_32_0'
'$SCNST_35_1':
	define_desc		19,1
	define_integer		8254
'$SCNST_35_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_35_1'
'$SCNST_43':
'$SCNST_35':
	define_vector		'$SCNST_35_0'
'$SCNST_37_1':
	define_desc		27,2
	define_integer		1162760004
	define_integer		46
'$SCNST_37_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_37_1'
'$SCNST_37':
	define_vector		'$SCNST_37_0'
'$SCNST_38_1':
	define_desc		3,1
	define_integer		1886614867
'$SCNST_38_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_38_1'
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_39_1':
	define_desc		3,1
	define_integer		1819042115
'$SCNST_39_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_39_1'
'$SCNST_39':
	define_vector		'$SCNST_39_0'
'$SCNST_40_1':
	define_desc		19,3
	define_integer		1701990432
	define_integer		1633904996
	define_integer		25972
'$SCNST_40_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_40_1'
'$SCNST_40':
	define_vector		'$SCNST_40_0'
'$SCNST_41_1':
	define_desc		19,3
	define_integer		1685015840
	define_integer		543517813
	define_integer		8250
'$SCNST_41_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_1'
'$SCNST_41':
	define_vector		'$SCNST_41_0'
'$SCNST_45_1':
	define_desc		27,1
	define_integer		32
'$SCNST_45_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_45_1'
'$SCNST_48':
'$SCNST_45':
	define_vector		'$SCNST_45_0'
'$SCNST_47_0':
	define_desc		0,2
	define_atom		tab
	define_integer		1
'$SCNST_50':
'$SCNST_47':
	define_vector		'$SCNST_47_0'
'$SCNST_49_1':
	define_desc		11,1
	define_integer		7173459
'$SCNST_49_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_49_1'
'$SCNST_49':
	define_vector		'$SCNST_49_0'
'$SCNST_51_0':
	define_desc		19,2
	define_integer		1668440438
	define_integer		27496
'$SCNST_51':
	define_string		'$SCNST_51_0'
'$SCNST_55_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_55':
	define_vector		'$SCNST_55_0'
'$SCNST_56_0':
	define_desc		3,5
	define_integer		1667330676
	define_integer		1701063781
	define_integer		744977762
	define_integer		746156147
	define_integer		778269797
'$SCNST_56':
	define_string		'$SCNST_56_0'
'$SCNST_57_1':
	define_desc		11,9
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1969382756
	define_integer		1868767335
	define_integer		1851878765
	define_integer		3044196
'$SCNST_57_3':
	define_desc		3,12
	define_integer		1667330676
	define_integer		1330456677
	define_integer		1162630468
	define_integer		538976297
	define_integer		757080096
	define_integer		1394617645
	define_integer		1948284005
	define_integer		1701011826
	define_integer		1685024032
	define_integer		1718558821
	define_integer		1146047776
	define_integer		776293461
'$SCNST_57_5':
	define_desc		19,13
	define_integer		1920233326
	define_integer		677733217
	define_integer		1430540109
	define_integer		539575628
	define_integer		757080096
	define_integer		1377840429
	define_integer		1952805733
	define_integer		1634890784
	define_integer		1830839651
	define_integer		543515759
	define_integer		1293969007
	define_integer		1280656463
	define_integer		11845
'$SCNST_57_7':
	define_desc		19,11
	define_integer		1801675106
	define_integer		1667330676
	define_integer		538976357
	define_integer		538976288
	define_integer		757080096
	define_integer		1394617645
	define_integer		1646294117
	define_integer		1953194849
	define_integer		1701011826
	define_integer		1685024032
	define_integer		11877
'$SCNST_57_9':
	define_desc		3,11
	define_integer		1633841006
	define_integer		1920232291
	define_integer		543515489
	define_integer		538976288
	define_integer		757080096
	define_integer		1377840429
	define_integer		1952805733
	define_integer		1667326496
	define_integer		1634890859
	define_integer		1830839651
	define_integer		778396783
'$SCNST_57_11':
	define_desc		19,10
	define_integer		1969382756
	define_integer		538976359
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1394617645
	define_integer		1679848549
	define_integer		1735746149
	define_integer		1685024032
	define_integer		11877
'$SCNST_57_13':
	define_desc		3,10
	define_integer		1701080942
	define_integer		543651170
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1377840429
	define_integer		1952805733
	define_integer		1650811936
	define_integer		1830840181
	define_integer		778396783
'$SCNST_57_15':
	define_desc		11,14
	define_integer		1769566323
	define_integer		1294493550
	define_integer		1280656463
	define_integer		538978629
	define_integer		757080096
	define_integer		1277177133
	define_integer		544502633
	define_integer		1701408883
	define_integer		1919950948
	define_integer		1667851365
	define_integer		1936028769
	define_integer		544106784
	define_integer		1430540109
	define_integer		3032396
'$SCNST_57_17':
	define_desc		27,16
	define_integer		1769566323
	define_integer		1294493550
	define_integer		1280656463
	define_integer		1280322629
	define_integer		757080105
	define_integer		1277177133
	define_integer		544502633
	define_integer		1701408883
	define_integer		1919950948
	define_integer		1667851365
	define_integer		1936028769
	define_integer		544106784
	define_integer		1430540109
	define_integer		1948271948
	define_integer		1280319599
	define_integer		46
'$SCNST_57_19':
	define_desc		3,15
	define_integer		679047283
	define_integer		1430540109
	define_integer		1345078604
	define_integer		1229210962
	define_integer		1163149635
	define_integer		1230127404
	define_integer		740907348
	define_integer		2037412640
	define_integer		1146047784
	define_integer		977620053
	define_integer		1145393744
	define_integer		1413563209
	define_integer		1380003653
	define_integer		693720137
	define_integer		757935392
'$SCNST_57_21':
	define_desc		19,16
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		1394614304
	define_integer		1931506789
	define_integer		1830844784
	define_integer		543515759
	define_integer		1293969007
	define_integer		1280656463
	define_integer		1380989509
	define_integer		1128875077
	define_integer		793072705
	define_integer		1414091329
	define_integer		11865
'$SCNST_57_23':
	define_desc		3,16
	define_integer		1886613358
	define_integer		1330456697
	define_integer		1162630468
	define_integer		1163022380
	define_integer		1094928708
	define_integer		1093420372
	define_integer		1498696018
	define_integer		1847602217
	define_integer		2037412719
	define_integer		1146047784
	define_integer		977620053
	define_integer		1145393744
	define_integer		1413563209
	define_integer		1380003653
	define_integer		693720137
	define_integer		757935392
'$SCNST_57_25':
	define_desc		3,16
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		1377837088
	define_integer		1952805733
	define_integer		2037412640
	define_integer		1685024032
	define_integer		1718558821
	define_integer		1146047776
	define_integer		977620053
	define_integer		1145393744
	define_integer		1413563209
	define_integer		1380003653
	define_integer		777606217
'$SCNST_57_27':
	define_desc		3,12
	define_integer		1668440438
	define_integer		1177054056
	define_integer		692407369
	define_integer		538976288
	define_integer		757080096
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1981834612
	define_integer		1634300513
	define_integer		543517794
	define_integer		1667590243
	define_integer		779249003
'$SCNST_57_29':
	define_desc		19,15
	define_integer		1668440438
	define_integer		1177054056
	define_integer		742739017
	define_integer		1162104653
	define_integer		757080105
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1981834612
	define_integer		1634300513
	define_integer		543517794
	define_integer		1667590243
	define_integer		544367979
	define_integer		1752459639
	define_integer		1146047776
	define_integer		11845
'$SCNST_57_31':
	define_desc		19,7
	define_integer		1668440438
	define_integer		1177054056
	define_integer		742739017
	define_integer		1162104653
	define_integer		1380927020
	define_integer		757082445
	define_integer		11565
'$SCNST_57_33':
	define_desc		27,17
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		1159733280
	define_integer		1969448312
	define_integer		1981834612
	define_integer		1634300513
	define_integer		543517794
	define_integer		1667590243
	define_integer		544367979
	define_integer		1752459639
	define_integer		1146047776
	define_integer		539369541
	define_integer		1297239878
	define_integer		46
'$SCNST_57_35':
	define_desc		11,12
	define_integer		1717924472
	define_integer		1279870504
	define_integer		538978629
	define_integer		538976288
	define_integer		757080096
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1663067508
	define_integer		1936945010
	define_integer		1717924384
	define_integer		1852142181
	define_integer		3040611
'$SCNST_57_37':
	define_desc		27,15
	define_integer		1717924472
	define_integer		1279870504
	define_integer		1330457669
	define_integer		539575620
	define_integer		757080096
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1663067508
	define_integer		1936945010
	define_integer		1717924384
	define_integer		1852142181
	define_integer		1998611811
	define_integer		543716457
	define_integer		1162104653
	define_integer		46
'$SCNST_57_39':
	define_desc		19,16
	define_integer		1717924472
	define_integer		1279870504
	define_integer		1330457669
	define_integer		1328301380
	define_integer		692474965
	define_integer		1159736621
	define_integer		1969448312
	define_integer		1663067508
	define_integer		1936945010
	define_integer		1717924384
	define_integer		1852142181
	define_integer		673211747
	define_integer		1953720684
	define_integer		544175136
	define_integer		1179931983
	define_integer		11817
'$SCNST_57_41':
	define_desc		3,14
	define_integer		1718579824
	define_integer		677735529
	define_integer		1430540109
	define_integer		539575628
	define_integer		757080096
	define_integer		1277177133
	define_integer		544502633
	define_integer		1684370032
	define_integer		1952539497
	define_integer		1919950949
	define_integer		1818846831
	define_integer		1852383333
	define_integer		1146047776
	define_integer		776293461
'$SCNST_57_43':
	define_desc		19,17
	define_integer		1718579824
	define_integer		677735529
	define_integer		1430540109
	define_integer		1294746956
	define_integer		692405327
	define_integer		1277177133
	define_integer		544502633
	define_integer		1684370032
	define_integer		1952539497
	define_integer		1919950949
	define_integer		1818846831
	define_integer		1852383333
	define_integer		1146047776
	define_integer		541412437
	define_integer		1752459639
	define_integer		1146047776
	define_integer		11845
'$SCNST_57_45':
	define_desc		27,15
	define_integer		1702061426
	define_integer		1919967092
	define_integer		1818846831
	define_integer		1330456677
	define_integer		1162630468
	define_integer		1377840425
	define_integer		1952805733
	define_integer		1701998624
	define_integer		1633904996
	define_integer		1881171316
	define_integer		1768320882
	define_integer		1763730796
	define_integer		1330454638
	define_integer		1162630468
	define_integer		46
'$SCNST_57_44':
	define_string		'$SCNST_57_45'
	define_atom		[]
'$SCNST_57_42':
	define_string		'$SCNST_57_43'
	define_list		'$SCNST_57_44'
'$SCNST_57_40':
	define_string		'$SCNST_57_41'
	define_list		'$SCNST_57_42'
'$SCNST_57_38':
	define_string		'$SCNST_57_39'
	define_list		'$SCNST_57_40'
'$SCNST_57_36':
	define_string		'$SCNST_57_37'
	define_list		'$SCNST_57_38'
'$SCNST_57_34':
	define_string		'$SCNST_57_35'
	define_list		'$SCNST_57_36'
'$SCNST_57_32':
	define_string		'$SCNST_57_33'
	define_list		'$SCNST_57_34'
'$SCNST_57_30':
	define_string		'$SCNST_57_31'
	define_list		'$SCNST_57_32'
'$SCNST_57_28':
	define_string		'$SCNST_57_29'
	define_list		'$SCNST_57_30'
'$SCNST_57_26':
	define_string		'$SCNST_57_27'
	define_list		'$SCNST_57_28'
'$SCNST_57_24':
	define_string		'$SCNST_57_25'
	define_list		'$SCNST_57_26'
'$SCNST_57_22':
	define_string		'$SCNST_57_23'
	define_list		'$SCNST_57_24'
'$SCNST_57_20':
	define_string		'$SCNST_57_21'
	define_list		'$SCNST_57_22'
'$SCNST_57_18':
	define_string		'$SCNST_57_19'
	define_list		'$SCNST_57_20'
'$SCNST_57_16':
	define_string		'$SCNST_57_17'
	define_list		'$SCNST_57_18'
'$SCNST_57_14':
	define_string		'$SCNST_57_15'
	define_list		'$SCNST_57_16'
'$SCNST_57_12':
	define_string		'$SCNST_57_13'
	define_list		'$SCNST_57_14'
'$SCNST_57_10':
	define_string		'$SCNST_57_11'
	define_list		'$SCNST_57_12'
'$SCNST_57_8':
	define_string		'$SCNST_57_9'
	define_list		'$SCNST_57_10'
'$SCNST_57_6':
	define_string		'$SCNST_57_7'
	define_list		'$SCNST_57_8'
'$SCNST_57_4':
	define_string		'$SCNST_57_5'
	define_list		'$SCNST_57_6'
'$SCNST_57_2':
	define_string		'$SCNST_57_3'
	define_list		'$SCNST_57_4'
'$SCNST_57_0':
	define_string		'$SCNST_57_1'
	define_list		'$SCNST_57_2'
'$SCNST_57':
	define_list		'$SCNST_57_0'
