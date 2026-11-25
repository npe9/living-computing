mpimos_cmd_code:
	module		mpimos_cmd_code
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_cmd_code
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	branch_on_atom		1,3,is_command_2_1
	bucket_entry_a		kl1cmp,is_command_2_4
	bucket_entry_a		listing,is_command_2_5
	bucket_entry_a		save_all,is_command_2_6
is_command_2_4:
	get_atom		2,yes
	proceed
is_command_2_5:
	get_atom		2,yes
	proceed
is_command_2_6:
	get_atom		2,yes
	proceed
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,4,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_7
	table_entry		is_command_2_8
is_command_2_7:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,8,is_command_2_1
	bucket_entry_a		ch_savedir,is_command_2_10
	bucket_entry_a		comp,is_command_2_11
	bucket_entry_a		compile,is_command_2_12
	bucket_entry_a		dload,is_command_2_13
	bucket_entry_a		listing,is_command_2_14
	bucket_entry_a		load,is_command_2_15
	bucket_entry_a		public,is_command_2_16
	bucket_entry_a		save,is_command_2_17
is_command_2_10:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_11:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
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
is_command_2_8:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,is_command_2_1
	bucket_entry_a		comp,is_command_2_19
	bucket_entry_a		public,is_command_2_20
	bucket_entry_a		save,is_command_2_21
is_command_2_19:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_20:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_21:
	read_elements_inc		1,1,4,2
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
is_command_2_29:
	suspend		is_command_2_0
	module_entry		mpimos_cmd_code
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	branch_on_atom		1,3,do_command_2_1
	bucket_entry_a		kl1cmp,do_command_2_4
	bucket_entry_a		listing,do_command_2_5
	bucket_entry_a		save_all,do_command_2_6
do_command_2_4:
	put_func		1,2,getuc
	write_element_variable		1,1,4
	get_list_val_var		2,3,1,1
	put_vector		5,2
	write_element_variable		5,0,3
	write_element_variable		5,1,2
	get_vector_value		1,5
	put_structured_constant		1,'$SCNST_0'
	put_variable		6,5
	b_append_string		1,6,1
	create_goal		5
	set_value		1,2
	set_variable		2,9
	set_marked_variable		3,7
	set_variable		4,6
	set_variable		5,10
	enqueue_goal		5,wait_kl1cmp_5_0
	create_goal		7
	set_value		1,3
	set_variable		2,2
	set_nil		3
	set_variable		4,3
	set_value		5,7
	set_variable		6,8
	set_value		7,10
	enqueue_goal		7,compile_one_file_7_0
	create_goal		7
	set_values_dec		1,9,2
	set_value		3,3
	set_values_dec		4,7,2
	set_variable		6,6
	set_value		7,2
	enqueue_goal		7,kl1cmp_input_window_7_0
	create_goal		2
	put_structured_constant		2,'$SCNST_1'
	put_func		3,3,prompt
	write_element_void		3,1
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	put_list		3
	write_car_atom		3,show
	write_cdr_value		3,2
	set_value		1,3
	set_value		2,1
	enqueue_goal_external		mpimos_window,create,2
	put_values_inc		1,4,2
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_5:
	put_func		1,3,getenv
	write_element_atom		1,1,savedir
	write_element_variable		1,2,6
	put_list_val_var		3,1,5
	put_func		1,2,get_all_modules
	write_element_variable		1,1,7
	put_func		4,2,code
	write_element_value		4,1,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	put_values_inc		1,6,2
	put_value		3,5
	execute		3,listing_action_3_0
do_command_2_6:
	put_func		1,3,getenv
	write_element_atom		1,1,savedir
	write_element_variable		1,2,4
	get_list_val_var		2,5,1,3
	put_values_dec		1,4,2
	execute		2,save_all_action_2_0
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,4,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_7
	table_entry		do_command_2_8
do_command_2_7:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,8,do_command_2_1
	bucket_entry_a		ch_savedir,do_command_2_10
	bucket_entry_a		comp,do_command_2_11
	bucket_entry_a		compile,do_command_2_12
	bucket_entry_a		dload,do_command_2_13
	bucket_entry_a		listing,do_command_2_14
	bucket_entry_a		load,do_command_2_15
	bucket_entry_a		public,do_command_2_16
	bucket_entry_a		save,do_command_2_17
do_command_2_10:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_19
	b_atom_name		4,3
	put_reused_func		1,1,ch_savedir
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_19:
	is_string		4,do_command_2_1
	g_string		4,5,6
	wait_integer		6,8
	collect_vector		1
	put_func		1,3,getenv
	write_element_atom		1,1,savedir
	write_element_variable		1,2,3
	get_list_val_var		2,5,1,1
	put_value		2,4
	execute		3,ch_svdir_action_3_0
do_command_2_11:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_20,do_command_2_1,do_command_2_21,do_command_2_1,do_command_2_22,do_command_2_1
do_command_2_21:
	collect_vector		1
	put_value		3,2
	put_atom		1,comp
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_20:
	test_nil		4,do_command_2_23
	collect_vector		1
	get_nil		2
	proceed
do_command_2_23:
	put_nil		5
	g_diff		4,5
	collect_value		5
	b_atom_name		4,3
	put_reused_func		1,1,comp
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_22:
	g_string		4,5,6
	wait_integer		6,8
	put_reused_func		1,1,getuc
	write_element_variable		1,1,7
	get_list_val_var		2,3,1,6
	put_structured_constant		1,'$SCNST_2'
	put_marked_value		2,1
	put_marked_variable		3,8
	b_append_string		2,3,2
	put_integer		9,65536
	put_atom		10,after_care
	put_func		3,3,delete
	write_element_value		3,1,8
	write_element_void		3,2
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_func		3,4,create
	write_element_value		3,1,5
	write_element_value		3,2,1
	write_element_void		3,3
	put_func		5,3,:
	write_element_atom		5,1,mpimos_directory
	write_element_value		5,2,3
	b_raise		9,10,5
	put_vector		9,2
	write_element_variable		9,0,5
	write_element_variable		9,1,3
	get_vector_value		6,9
	create_goal		5
	set_value		1,3
	set_value		2,1
	set_value		3,8
	set_marked_value		4,2
	set_variable		5,1
	enqueue_goal		5,wait_comp1_5_0
	create_goal		4
	set_values_dec		1,5,2
	set_values_dec		3,2,2
	enqueue_goal		4,compile_one_file_4_0
	create_goal		2
	put_structured_constant		1,'$SCNST_3'
	put_list		2
	write_car_variable		2,3
	write_cdr_value		2,1
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		4,1,2
	set_value		1,4
	set_value		2,8
	enqueue_goal_external		mpimos_utility,string_append,2
	put_value		1,7
	put_value		2,3
	execute_external		mpimos_utility,integer_to_string,2
do_command_2_12:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_24,do_command_2_1,do_command_2_25,do_command_2_1,do_command_2_26,do_command_2_1
do_command_2_25:
	collect_vector		1
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_atom		3,success
	enqueue_goal		3,compile_action_3_0
	put_value		1,4
	put_structured_constant		2,'$SCNST_5'
	execute		3,correct_extention_3_0
do_command_2_24:
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,compile
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_26:
	g_string		4,3,5
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_reused_func		1,1,compile
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_13:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_27,do_command_2_1,do_command_2_28,do_command_2_1,do_command_2_29,do_command_2_1
do_command_2_28:
	collect_vector		1
	put_value		3,2
	put_atom		1,dload
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_27:
	test_nil		4,do_command_2_30
	collect_vector		1
	get_nil		2
	proceed
do_command_2_30:
	put_nil		5
	g_diff		4,5
	collect_value		5
	b_atom_name		4,3
	put_reused_func		1,1,dload
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_29:
	g_string		4,5,6
	wait_integer		6,8
	put_structured_constant		3,'$SCNST_6'
	put_reused_func		1,1,putt
	write_element_marked_value		1,1,4
	put_list_val_val		5,1,3
	put_func		1,2,window
	write_element_value		1,1,5
	get_list_val_var		2,3,1,1
	create_goal		1
	set_variable		1,5
	enqueue_goal		1,wait_status_1_0
	put_void		2
	put_value		3,4
	put_atom		4,debug
	execute		5,load_one_file_5_0
do_command_2_14:
	read_element		1,1,4
	put_reused_func		1,1,get_all_modules
	write_element_variable		1,1,5
	put_func		3,2,code
	write_element_value		3,1,1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	put_values_dec		1,5,2
	execute_external		mpimos_cmd_utl,protect,2
do_command_2_15:
	read_element		1,1,4
	wait		4
	switch_on_type		4,do_command_2_31,do_command_2_1,do_command_2_32,do_command_2_1,do_command_2_33,do_command_2_1
do_command_2_32:
	collect_vector		1
	put_value		3,2
	put_atom		1,load
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_31:
	test_nil		4,do_command_2_34
	collect_vector		1
	get_nil		2
	proceed
do_command_2_34:
	put_nil		5
	g_diff		4,5
	collect_value		5
	b_atom_name		4,3
	put_reused_func		1,1,load
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_33:
	g_string		4,5,6
	wait_integer		6,8
	put_structured_constant		3,'$SCNST_7'
	put_reused_func		1,1,putt
	write_element_marked_value		1,1,4
	put_list_val_val		5,1,3
	put_func		1,2,window
	write_element_value		1,1,5
	get_list_val_var		2,3,1,1
	create_goal		1
	set_variable		1,5
	enqueue_goal		1,wait_status_1_0
	put_void		2
	put_value		3,4
	put_atom		4,nodebug
	execute		5,load_one_file_5_0
do_command_2_16:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_36
	collect_vector		1
	put_value		3,2
	put_atom		1,public
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_36:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_37
	collect_vector		1
	get_nil		2
	proceed
do_command_2_37:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_func		3,4,get_public_predicates
	write_element_value		3,1,4
	write_element_variable		3,2,5
	write_element_variable		3,3,4
	put_reused_func		1,1,code
	write_element_value		1,1,3
	get_list_val_var		2,6,1,3
	put_values_dec		1,5,2
	execute		3,public_action_3_0
do_command_2_17:
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_39
	collect_vector		1
	put_value		3,2
	put_atom		1,save
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_39:
	is_atom		4,do_command_2_1
	collect_vector		1
	put_func		1,3,getenv
	write_element_atom		1,1,savedir
	write_element_variable		1,2,5
	get_list_val_var		2,6,1,3
	put_values_dec		1,5,2
	execute		3,save_action_3_0
do_command_2_8:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,do_command_2_1
	bucket_entry_a		comp,do_command_2_41
	bucket_entry_a		public,do_command_2_42
	bucket_entry_a		save,do_command_2_43
do_command_2_41:
	read_element		1,1,4
	try_me_else		do_command_2_44
	jump_on_non_atom		4,do_command_2_46
	read_element		1,2,5
	b_atom_name		4,3
	put_reused_func		1,1,comp
	write_element_value		1,1,3
	write_element_value		1,2,5
	execute		2,do_command_2_0
do_command_2_46:
	is_string		4,do_command_2_44
	read_element		1,2,5
	string		5
	g_string		4,6,7
	wait_integer		7,8
	g_string		5,6,7
	wait_integer		7,8
	collect_vector		1
	create_goal		1
	set_variable		1,6
	enqueue_goal		1,wait_comp_1_0
	put_value		1,2
	put_values_inc		2,4,3
	execute		4,compile_one_file_4_0
do_command_2_44:
	read_element		1,2,5
	try_me_else		do_command_2_1
	atom		5
	b_atom_name		5,3
	put_reused_func		1,1,comp
	write_elements_dec		1,1,4,2
	execute		2,do_command_2_0
do_command_2_42:
	read_elements_inc		1,1,4,2
	atom		4
	collect_vector		1
	put_func		1,4,get_public_predicates
	write_element_value		1,1,4
	write_element_variable		1,2,7
	write_element_variable		1,3,6
	put_func		3,2,code
	write_element_value		3,1,1
	get_list_val_var		2,1,3,4
	put_value		1,7
	put_values_inc		2,5,2
	execute		4,return_public_4_0
do_command_2_43:
	read_element		1,1,4
	atom		4
	read_element		1,2,5
	jump_on_non_atom		5,do_command_2_51
	b_atom_name		5,3
	put_reused_func		1,1,save
	write_elements_dec		1,1,4,2
	execute		2,do_command_2_0
do_command_2_51:
	is_string		5,do_command_2_1
	g_string		5,6,7
	wait_integer		7,8
	collect_vector		1
	put_structured_constant		1,'$SCNST_8'
	put_func		3,2,putt
	write_element_marked_value		3,1,5
	put_list_val_val		6,3,1
	put_func		1,2,window
	write_element_value		1,1,6
	get_list_val_var		2,3,1,1
	create_goal		1
	set_variable		1,6
	enqueue_goal		1,wait_status_1_0
	put_values_inc		2,4,3
	execute		4,save_one_file_4_0
do_command_2_1:
	otherwise		do_command_2_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_9'
	put_func		4,2,putt
	write_element_variable		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_10'
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
do_command_2_87:
	suspend		do_command_2_0
	module_entry		mpimos_cmd_code
	predicate		save_action,3
save_action_3_0:
	try_me_else		save_action_3_1
	atom		2
	put_value		4,3
	create_goal		4
	set_variable		1,3
	set_variable		2,6
	set_value		3,2
	set_variable		4,5
	enqueue_goal		4,save_action0_4_0
	put_value		2,6
	execute_external		mpimos_cmd_utl,check_savedir,5
save_action_3_1:
	suspend		save_action_3_0
	module_entry		mpimos_cmd_code
	predicate		save_action0,4
save_action0_4_0:
	try_me_else		save_action0_4_1
	wait_atom		1,success
	wait		2
	put_func		1,2,flush
	write_element_variable		1,1,7
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	put_structured_constant		1,'$SCNST_11'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_marked_value		1,1,3
	put_list_val_val		5,1,6
	put_func		1,2,window
	write_element_value		1,1,5
	put_list_val_var		5,1,6
	put_func		1,4,auto_save_module
	write_elements_inc		1,1,2,2
	write_element_variable		1,3,3
	put_func		2,2,code
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	put_value		1,6
	put_value		2,3
	put_value		3,7
	execute		3,wait_save_3_0
save_action0_4_1:
	otherwise		save_action0_4_0
	collect_value		3
	collect_value		2
	collect_value		1
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
	execute		1,abort_action_1_0
save_action0_4_6:
	suspend		save_action0_4_0
	module_entry		mpimos_cmd_code
	predicate		wait_save,3
wait_save_3_0:
	try_me_else		wait_save_3_1
	wait_atom		2,success
	wait_atom		3,done
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_12'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_1_0
wait_save_3_1:
	otherwise		wait_save_3_0
	try_me_else		wait_save_3_6
	wait		2
	wait_atom		3,done
	put_func		3,2,flush
	write_element_variable		3,1,6
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,4
	put_structured_constant		4,'$SCNST_13'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_marked_value		3,1,2
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_14'
	put_list_val_val		5,3,4
	put_func		3,2,window
	write_element_value		3,1,5
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	get_list_value		1,4
	put_value		1,2
	put_value		2,6
	execute		2,raise_fail_2_0
wait_save_3_6:
	suspend		wait_save_3_0
	module_entry		mpimos_cmd_code
	predicate		wait_status,1
wait_status_1_0:
	try_me_else		wait_status_1_1
	wait_atom		1,success
	proceed
wait_status_1_1:
	otherwise		wait_status_1_0
	collect_value		1
	put_atom		1,done
	execute		1,fail_action_1_0
wait_status_1_6:
	suspend		wait_status_1_0
	module_entry		mpimos_cmd_code
	predicate		load_one_file,5
load_one_file_5_0:
	put_func		6,3,getenv
	write_element_atom		6,1,world
	write_element_variable		6,2,9
	get_list_val_var		1,7,6,8
	put_func		1,2,flush
	write_element_variable		1,1,10
	put_list		6
	write_car_value		6,1
	write_cdr_nil		6
	put_structured_constant		1,'$SCNST_15'
	put_list_val_val		7,1,6
	put_func		1,2,window
	write_element_value		1,1,7
	put_list_val_var		6,1,1
	create_goal		6
	set_value		1,1
	set_marked_value		2,2
	set_values_inc		3,4,2
	set_variable		5,5
	set_value		6,10
	enqueue_goal		6,wait_load_one_file_6_0
	create_goal		4
	put_list		1
	write_car_marked_variable		1,4
	write_cdr_nil		1
	set_value		1,1
	put_func		1,4,load_module
	write_element_value		1,1,2
	write_elements_inc		1,2,4,2
	put_func		2,2,code
	write_element_value		2,1,1
	set_value		2,2
	set_value		3,8
	set_value		4,6
	enqueue_goal_external		mpimos_cmd_utl,wait_send,4
	put_value		1,9
	put_values_inc		2,3,2
	execute_external		mpimos_utility,pathname,3
load_one_file_5_1:
	suspend		load_one_file_5_0
	module_entry		mpimos_cmd_code
	predicate		wait_load_one_file,6
wait_load_one_file_6_0:
	try_me_else		wait_load_one_file_6_1
	atom		3
	branch_on_atom		3,2,wait_load_one_file_6_1
	bucket_entry_a		debug,wait_load_one_file_6_3
	bucket_entry_a		nodebug,wait_load_one_file_6_4
wait_load_one_file_6_3:
	wait_atom		5,success
	wait		6
	collect_value		6
	put_func		3,2,flush
	write_element_variable		3,1,7
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_structured_constant		3,'$SCNST_16'
	put_func		6,3,prompt
	write_element_void		6,1
	write_element_value		6,2,3
	put_list_val_val		3,6,5
	put_func		5,2,window
	write_element_value		5,1,3
	put_list		3
	write_car_value		3,5
	write_cdr_nil		3
	put_list		5
	write_car_atom		5,initenv
	write_cdr_value		5,3
	put_structured_constant		3,'$SCNST_17'
	put_list_val_val		6,3,5
	put_func		3,4,trace_module
	write_element_marked_value		3,1,2
	write_element_atom		3,2,on
	write_element_void		3,3
	put_func		5,2,code
	write_element_value		5,1,3
	put_list_val_val		3,5,6
	put_structured_constant		5,'$SCNST_18'
	put_func		6,2,putt
	write_element_value		6,1,2
	put_list_val_val		2,6,5
	put_structured_constant		5,'$SCNST_19'
	put_list_val_val		6,5,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,6
	put_structured_constant		5,'$SCNST_20'
	put_list_val_val		6,5,2
	put_func		2,2,window
	write_element_value		2,1,6
	put_list_val_val		5,2,3
	get_list_value		1,5
	put_value		1,7
	put_atom		2,success
	put_value		3,4
	execute		3,return_status_3_0
wait_load_one_file_6_4:
	wait_atom		5,success
	wait		6
	collect_value		6
	put_func		3,2,flush
	write_element_variable		3,1,6
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,5
	put_func		5,2,putt
	write_element_value		5,1,2
	put_list_val_val		2,5,3
	put_structured_constant		3,'$SCNST_21'
	put_list_val_val		5,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_structured_constant		3,'$SCNST_22'
	put_list_val_val		5,3,2
	put_func		2,2,window
	write_element_value		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,6
	put_atom		2,success
	put_value		3,4
	execute		3,return_status_3_0
wait_load_one_file_6_1:
	otherwise		wait_load_one_file_6_0
	try_me_else		wait_load_one_file_6_7
	wait		6
	collect_value		3
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,7
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_23'
	put_list_val_val		6,3,2
	put_func		2,2,putt
	write_element_marked_value		2,1,5
	put_list_val_val		3,2,6
	put_structured_constant		2,'$SCNST_24'
	put_list_val_val		6,2,3
	put_func		2,2,window
	write_element_value		2,1,6
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,7
	put_values_dec		2,5,2
	execute		3,return_status_3_0
wait_load_one_file_6_7:
	suspend		wait_load_one_file_6_0
	module_entry		mpimos_cmd_code
	predicate		save_one_file,4
save_one_file_4_0:
	put_func		5,3,getenv
	write_element_atom		5,1,world
	write_element_variable		5,2,8
	get_list_val_var		1,6,5,7
	put_func		1,2,flush
	write_element_variable		1,1,9
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	put_structured_constant		1,'$SCNST_25'
	put_list_val_val		6,1,5
	put_func		1,2,window
	write_element_value		1,1,6
	put_list_val_var		5,1,1
	create_goal		4
	set_value		1,1
	set_value		2,4
	set_variable		3,4
	set_value		4,9
	enqueue_goal		4,wait_save_one_file_4_0
	create_goal		4
	put_list		1
	write_car_marked_variable		1,6
	write_cdr_nil		1
	set_value		1,1
	put_func		1,4,save_module
	write_element_value		1,1,2
	write_element_value		1,2,6
	write_element_value		1,3,4
	put_func		2,2,code
	write_element_value		2,1,1
	set_value		2,2
	set_value		3,7
	set_value		4,5
	enqueue_goal_external		mpimos_cmd_utl,wait_send,4
	create_goal		3
	set_variable		1,4
	put_structured_constant		1,'$SCNST_26'
	set_value		2,1
	set_value		3,6
	enqueue_goal_external		mpimos_utility,extend_name,3
	put_value		1,8
	put_values_inc		2,3,2
	execute_external		mpimos_utility,pathname,3
save_one_file_4_1:
	suspend		save_one_file_4_0
	module_entry		mpimos_cmd_code
	predicate		wait_save_one_file,4
wait_save_one_file_4_0:
	try_me_else		wait_save_one_file_4_1
	wait_atom		3,success
	wait		4
	collect_value		4
	put_value		6,2
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_27'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	put_atom		2,success
	put_value		3,6
	execute		3,return_status_3_0
wait_save_one_file_4_1:
	otherwise		wait_save_one_file_4_0
	try_me_else		wait_save_one_file_4_6
	wait		4
	put_value		7,2
	put_func		2,2,flush
	write_element_variable		2,1,6
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_structured_constant		4,'$SCNST_28'
	put_list_val_val		5,4,2
	put_func		2,2,putt
	write_element_marked_value		2,1,3
	put_list_val_val		4,2,5
	put_structured_constant		2,'$SCNST_29'
	put_list_val_val		5,2,4
	put_func		2,2,window
	write_element_value		2,1,5
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	get_list_value		1,4
	put_value		1,6
	put_value		2,3
	put_value		3,7
	execute		3,return_status_3_0
wait_save_one_file_4_6:
	suspend		wait_save_one_file_4_0
	module_entry		mpimos_cmd_code
	predicate		raise_fail,2
raise_fail_2_0:
	try_me_else		raise_fail_2_1
	wait_atom		2,done
	put_integer		3,131072
	put_structured_constant		2,'$SCNST_30'
	b_raise		3,2,1
	proceed
raise_fail_2_1:
	suspend		raise_fail_2_0
	module_entry		mpimos_cmd_code
	predicate		save_all_action,2
save_all_action_2_0:
	put_value		4,2
	create_goal		3
	set_variable		1,3
	set_variable		2,2
	set_variable		3,5
	enqueue_goal		3,save_all_action_wait_dir_3_0
	execute_external		mpimos_cmd_utl,check_savedir,5
save_all_action_2_1:
	suspend		save_all_action_2_0
	module_entry		mpimos_cmd_code
	predicate		save_all_action_wait_dir,3
save_all_action_wait_dir_3_0:
	try_me_else		save_all_action_wait_dir_3_1
	wait_atom		1,success
	put_func		1,3,get_unsaved_modules
	write_element_marked_value		1,1,2
	write_element_variable		1,2,5
	put_func		4,2,code
	write_element_value		4,1,1
	get_list_val_var		3,1,4,4
	put_value		1,2
	put_values_dec		2,5,2
	execute		3,save_all_action_3_0
save_all_action_wait_dir_3_1:
	otherwise		save_all_action_wait_dir_3_0
	collect_value		2
	collect_value		1
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
	execute		1,abort_action_1_0
save_all_action_wait_dir_3_6:
	suspend		save_all_action_wait_dir_3_0
	module_entry		mpimos_cmd_code
	predicate		save_all_action,3
save_all_action_3_0:
	try_me_else		save_all_action_3_1
	wait_nil		2
	collect_value		1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_31'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	proceed
save_all_action_3_1:
	otherwise		save_all_action_3_0
	execute		3,save_all_action0_3_0
save_all_action_3_6:
	suspend		save_all_action_3_0
	module_entry		mpimos_cmd_code
	predicate		save_all_action0,3
save_all_action0_3_0:
	try_me_else		save_all_action0_3_1
	jump_on_non_list_var_var		2,save_all_action0_3_3,4,5
	wait		4
	put_func		6,4,auto_save_module
	write_element_marked_value		6,1,1
	write_element_marked_value		6,2,4
	write_element_variable		6,3,10
	put_func		7,2,code
	write_element_value		7,1,6
	put_reused_list_val_var		2,2,7,9
	put_func		6,2,flush
	write_element_void		6,1
	put_list		7
	write_car_value		7,6
	write_cdr_nil		7
	put_structured_constant		6,'$SCNST_32'
	put_list_val_val		8,6,7
	put_func		6,2,putt
	write_element_value		6,1,4
	put_list_val_val		4,6,8
	put_func		6,2,window
	write_element_value		6,1,4
	put_list_val_val		4,6,2
	get_list_value		3,4
	put_value		2,10
	put_value		3,5
	put_value		4,9
	execute		4,save_all_action00_4_0
save_all_action0_3_3:
	check_nil		2,save_all_action0_3_1
	collect_value		1
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_33'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,wait_1_0
save_all_action0_3_1:
	suspend		save_all_action0_3_0
	module_entry		mpimos_cmd_code
	predicate		save_all_action00,4
save_all_action00_4_0:
	try_me_else		save_all_action00_4_1
	wait_atom		2,success
	put_func		2,2,flush
	write_element_void		2,1
	put_list		5
	write_car_value		5,2
	write_cdr_nil		5
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_structured_constant		5,'$SCNST_34'
	put_list_val_val		6,5,2
	put_func		2,2,window
	write_element_value		2,1,6
	get_list_val_var		4,6,2,5
	put_value		2,3
	put_value		3,5
	execute		3,save_all_action0_3_0
save_all_action00_4_1:
	otherwise		save_all_action00_4_0
	collect_value		3
	collect_value		2
	collect_value		1
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_35'
	put_list_val_val		3,2,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_func		2,2,window
	write_element_value		2,1,1
	put_list		1
	write_car_value		1,2
	write_cdr_nil		1
	get_list_value		4,1
	put_value		1,5
	execute		1,fail_action_1_0
save_all_action00_4_6:
	suspend		save_all_action00_4_0
	module_entry		mpimos_cmd_code
	predicate		listing_action,3
listing_action_3_0:
	try_me_else		listing_action_3_1
	wait_nil		2
	collect_value		1
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_36'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,wait_1_0
listing_action_3_1:
	otherwise		listing_action_3_0
	try_me_else		listing_action_3_6
	wait		1
	put_value		4,3
	create_goal		4
	set_variable		1,3
	set_variable		2,6
	set_value		3,2
	set_variable		4,5
	enqueue_goal		4,listing_action_wait_dir_4_0
	put_value		2,6
	execute_external		mpimos_cmd_utl,check_savedir,5
listing_action_3_6:
	suspend		listing_action_3_0
	module_entry		mpimos_cmd_code
	predicate		listing_action_wait_dir,4
listing_action_wait_dir_4_0:
	try_me_else		listing_action_wait_dir_4_1
	wait_atom		1,success
	string		2
	g_string		2,5,6
	wait_integer		6,8
	put_func		1,3,get_unsaved_modules
	write_element_marked_value		1,1,2
	write_element_variable		1,2,8
	put_func		5,2,code
	write_element_value		5,1,1
	put_list_val_var		1,5,7
	put_structured_constant		5,'$SCNST_37'
	put_func		6,2,putt
	write_element_value		6,1,2
	put_list_val_val		2,6,5
	put_structured_constant		5,'$SCNST_38'
	put_list_val_val		6,5,2
	put_func		2,2,window
	write_element_value		2,1,6
	put_list_val_val		5,2,1
	get_list_value		4,5
	create_goal		4
	set_marked_value		1,3
	set_variable		2,1
	set_variable		3,4
	set_marked_variable		4,2
	enqueue_goal		4,listing_action0_4_0
	create_goal		3
	set_value		1,2
	set_value		2,7
	set_value		3,4
	enqueue_goal		3,display_head_3_0
	create_goal		2
	set_values_dec		1,3,2
	enqueue_goal		2,max_size_2_0
	create_goal		4
	set_value		1,8
	set_variable		2,2
	set_value		3,1
	set_atom		4,off
	enqueue_goal		4,put_all_4_0
	create_goal		4
	set_value		1,3
	set_variable		2,1
	set_value		3,2
	set_atom		4,on
	enqueue_goal		4,put_all_4_0
	execute_external		mpimos_monogyny_list_index,create,1
listing_action_wait_dir_4_1:
	otherwise		listing_action_wait_dir_4_0
	collect_value		2
	collect_value		1
	create_goal		3
	set_marked_value		1,3
	set_variable		2,1
	set_marked_variable		3,2
	enqueue_goal		3,listing_action00_3_0
	create_goal		3
	set_value		1,2
	set_value		2,4
	set_value		3,1
	enqueue_goal		3,display_head_3_0
	put_value		1,3
	execute		2,max_size_2_0
listing_action_wait_dir_4_6:
	suspend		listing_action_wait_dir_4_0
	module_entry		mpimos_cmd_code
	predicate		listing_action0,4
listing_action0_4_0:
	try_me_else		listing_action0_4_1
	jump_on_non_list_var_var		1,listing_action0_4_3,5,6
	wait		5
	put_func		7,4,get_spied_predicates
	write_element_marked_value		7,1,5
	write_element_variable		7,2,10
	write_element_void		7,3
	put_func		8,2,code
	write_element_value		8,1,7
	put_reused_list_val_var		1,1,8,9
	put_func		7,4,get_module_status
	write_element_value		7,1,5
	write_element_variable		7,2,11
	write_element_void		7,3
	put_func		8,2,code
	write_element_value		8,1,7
	put_list_val_val		7,8,1
	get_list_value		3,7
	put_func		1,4,get_at
	write_element_variable		1,1,3
	write_element_value		1,2,5
	write_element_void		1,3
	get_list_val_var		2,7,1,1
	create_goal		4
	set_value		1,6
	set_value		2,1
	set_variable		3,1
	set_marked_value		4,4
	enqueue_goal		4,listing_action0_4_0
	create_goal		7
	set_values_inc		1,4,2
	set_value		3,11
	set_value		4,3
	set_variable		5,2
	set_value		6,9
	set_value		7,1
	enqueue_goal		7,display_line_7_0
	put_value		1,10
	execute		2,count_2_0
listing_action0_4_3:
	check_nil		1,listing_action0_4_1
	integer		4
	try_me_else		listing_action0_4_5
	put_integer		5,12
	g_less_than		4,5
	get_nil		2
	create_goal		1
	set_variable		1,6
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_structured_constant		1,'$SCNST_39'
	put_func		2,2,putb
	write_element_variable		2,1,5
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	set_value		1,1
	set_value		2,3
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
	put_integer		1,45
	put_integer		2,33
	put_value		3,5
	execute		3,line_3_0
listing_action0_4_5:
	try_me_else		listing_action0_4_1
	put_integer		5,11
	g_less_than		5,4
	get_nil		2
	put_integer		1,22
	b_add		4,1,1
	put_value		5,1
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_structured_constant		1,'$SCNST_40'
	put_func		2,2,putb
	write_element_variable		2,1,6
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	set_value		1,1
	set_value		2,3
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
	put_integer		1,45
	put_values_inc		2,5,2
	execute		3,line_3_0
listing_action0_4_1:
	suspend		listing_action0_4_0
	module_entry		mpimos_cmd_code
	predicate		listing_action00,3
listing_action00_3_0:
	try_me_else		listing_action00_3_1
	jump_on_non_list_var_var		1,listing_action00_3_3,4,5
	wait		4
	put_func		6,4,get_spied_predicates
	write_element_marked_value		6,1,4
	write_element_variable		6,2,9
	write_element_void		6,3
	put_func		7,2,code
	write_element_value		7,1,6
	put_reused_list_val_var		1,1,7,8
	put_func		6,4,get_module_status
	write_element_value		6,1,4
	write_element_variable		6,2,10
	write_element_void		6,3
	put_func		7,2,code
	write_element_value		7,1,6
	put_list_val_val		6,7,1
	get_list_value		2,6
	create_goal		3
	set_value		1,5
	set_variable		2,1
	set_marked_value		3,3
	enqueue_goal		3,listing_action00_3_0
	create_goal		7
	set_values_inc		1,3,2
	set_value		3,10
	set_atom		4,?
	set_variable		5,2
	set_value		6,8
	set_value		7,1
	enqueue_goal		7,display_line_7_0
	put_value		1,9
	execute		2,count_2_0
listing_action00_3_3:
	check_nil		1,listing_action00_3_1
	put_value		5,2
	put_value		4,3
	put_nil		1
	put_void		2
	put_value		3,5
	execute		4,listing_action0_4_0
listing_action00_3_1:
	suspend		listing_action00_3_0
	module_entry		mpimos_cmd_code
	predicate		count,2
count_2_0:
	try_me_else		count_2_1
	jump_on_non_list_var_var		1,count_2_3,3,4
	collect_list		1
	collect_value		3
	put_variable		1,3
	b_increment		1,1
	get_value		2,1
	put_values_dec		1,4,2
	execute		2,count_2_0
count_2_3:
	is_atom		1,count_2_1
	branch_on_atom		1,2,count_2_1
	bucket_entry_a		[],count_2_4
	bucket_entry_a		no_information,count_2_5
count_2_4:
	get_integer		2,0
	proceed
count_2_5:
	get_integer		2,-1
	proceed
count_2_1:
	suspend		count_2_0
	module_entry		mpimos_cmd_code
	predicate		max_size,2
max_size_2_0:
	create_goal		3
	set_variable		1,3
	set_integer		2,0
	set_value		3,2
	enqueue_goal		3,max_size_3_0
	put_value		2,3
	execute		2,symbol_to_string_2_0
max_size_2_1:
	suspend		max_size_2_0
	module_entry		mpimos_cmd_code
	predicate		max_size,3
max_size_3_0:
	try_me_else		max_size_3_1
	jump_on_non_list		1,max_size_3_3
	read_car		1,4
	string		4
	read_cdr		1,5
	integer		2
	g_string		4,6,7
	try_me_else		max_size_3_6
	g_not_less_than		6,2
	collect_list		1
	collect_value		4
	put_values_inc		1,5,2
	execute		3,max_size_3_0
max_size_3_6:
	collect_list		1
	collect_value		4
	put_value		1,5
	execute		3,max_size_3_0
max_size_3_3:
	check_nil		1,max_size_3_1
	get_value		3,2
	proceed
max_size_3_1:
	suspend		max_size_3_0
	module_entry		mpimos_cmd_code
	predicate		symbol_to_string,2
symbol_to_string_2_0:
	try_me_else		symbol_to_string_2_1
	jump_on_non_list_var_var		1,symbol_to_string_2_3,3,4
	b_atom_name		3,3
	get_reused_list_val_var		2,1,1,3,3
	put_values_dec		1,4,2
	execute		2,symbol_to_string_2_0
symbol_to_string_2_3:
	check_nil		1,symbol_to_string_2_1
	get_nil		2
	proceed
symbol_to_string_2_1:
	suspend		symbol_to_string_2_0
	module_entry		mpimos_cmd_code
	predicate		display_head,3
display_head_3_0:
	try_me_else		display_head_3_1
	integer		1
	put_integer		4,12
	g_less_than		1,4
	put_structured_constant		1,'$SCNST_41'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
display_head_3_1:
	otherwise		display_head_3_0
	put_integer		4,11
	b_subtract		1,4,1
	put_value		6,1
	create_goal		3
	put_structured_constant		1,'$SCNST_42'
	put_func		4,2,putb
	write_element_variable		4,1,7
	put_list_val_val		5,4,1
	put_structured_constant		1,'$SCNST_43'
	put_list_val_val		4,1,5
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	put_structured_constant		4,'$SCNST_44'
	put_list_val_val		5,4,1
	put_func		1,2,tab
	write_element_marked_value		1,1,6
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_45'
	put_list_val_val		5,1,4
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,5
	put_structured_constant		4,'$SCNST_46'
	put_list_val_val		5,4,1
	put_func		1,2,putb
	write_element_variable		1,1,8
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_47'
	put_list_val_val		5,1,4
	put_func		1,2,window
	write_element_value		1,1,5
	set_values_inc		1,1,3
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	create_goal		3
	set_integer		1,95
	set_value		2,6
	set_value		3,8
	enqueue_goal		3,line_3_0
	put_integer		1,45
	put_values_inc		2,6,2
	execute		3,line_3_0
display_head_3_5:
	suspend		display_head_3_0
	module_entry		mpimos_cmd_code
	predicate		line,3
line_3_0:
	put_value		4,3
	put_marked_value		3,2
	put_integer		5,8
	b_new_string		3,3,5
	execute		4,line0_4_0
line_3_1:
	suspend		line_3_0
	module_entry		mpimos_cmd_code
	predicate		line0,4
line0_4_0:
	try_me_else		line0_4_1
	integer		2
	test_integer		2,0,line0_4_3
	collect_value		1
	get_value		3,4
	proceed
line0_4_3:
	put_integer		5,0
	g_less_than		5,2
	b_decrement		2,2
	put_marked_value		5,2
	put_marked_value		6,1
	b_set_string_element		3,5,6,3
	execute		4,line0_4_0
line0_4_1:
	suspend		line0_4_0
	module_entry		mpimos_cmd_code
	predicate		display_line,7
display_line_7_0:
	b_atom_name		2,2
	b_string		2,2,8,9
	create_goal		8
	set_values_inc		1,1,2
	set_value		3,9
	set_variable		4,1
	set_variable		5,8
	set_variable		6,2
	set_values_inc		7,6,2
	enqueue_goal		8,display_line0_8_0
	create_goal		2
	set_value		1,4
	set_value		2,8
	enqueue_goal		2,flag_2_0
	create_goal		2
	set_value		1,3
	set_value		2,1
	enqueue_goal		2,flag_2_0
	put_value		1,5
	execute_external		mpimos_utility,integer_to_string,2
display_line_7_1:
	suspend		display_line_7_0
	module_entry		mpimos_cmd_code
	predicate		display_line0,8
display_line0_8_0:
	try_me_else		display_line0_8_1
	integer		1
	put_integer		9,12
	g_less_than		1,9
	put_integer		1,13
	b_subtract		1,2,1
	put_structured_constant		2,'$SCNST_48'
	put_func		9,2,putb
	write_element_value		9,1,6
	put_list_val_val		6,9,2
	put_structured_constant		2,'$SCNST_49'
	put_list_val_val		9,2,6
	put_func		2,2,putb
	write_element_value		2,1,5
	put_list_val_val		5,2,9
	put_structured_constant		2,'$SCNST_50'
	put_list_val_val		6,2,5
	put_func		2,2,putb
	write_element_value		2,1,4
	put_list_val_val		4,2,6
	put_func		2,2,tab
	write_element_value		2,1,1
	put_list_val_val		1,2,4
	put_func		2,2,putb
	write_element_value		2,1,3
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_51'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_values_inc		2,7,2
	execute_external		mpimos_cmd_utl,send_shell,3
display_line0_8_1:
	otherwise		display_line0_8_0
	b_subtract		1,2,1
	put_integer		2,2
	b_add		1,2,1
	put_structured_constant		2,'$SCNST_52'
	put_func		9,2,putb
	write_element_value		9,1,6
	put_list_val_val		6,9,2
	put_structured_constant		2,'$SCNST_53'
	put_list_val_val		9,2,6
	put_func		2,2,putb
	write_element_value		2,1,5
	put_list_val_val		5,2,9
	put_structured_constant		2,'$SCNST_54'
	put_list_val_val		6,2,5
	put_func		2,2,putb
	write_element_value		2,1,4
	put_list_val_val		4,2,6
	put_func		2,2,tab
	write_element_value		2,1,1
	put_list_val_val		1,2,4
	put_func		2,2,putb
	write_element_value		2,1,3
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_55'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_values_inc		2,7,2
	execute_external		mpimos_cmd_utl,send_shell,3
display_line0_8_5:
	suspend		display_line0_8_0
	module_entry		mpimos_cmd_code
	predicate		flag,2
flag_2_0:
	try_me_else		flag_2_1
	atom		1
	branch_on_atom		1,3,flag_2_1
	bucket_entry_a		?,flag_2_3
	bucket_entry_a		off,flag_2_4
	bucket_entry_a		on,flag_2_5
flag_2_3:
	put_structured_constant		1,'$SCNST_56'
	get_value		2,1
	proceed
flag_2_4:
	put_structured_constant		1,'$SCNST_57'
	get_value		2,1
	proceed
flag_2_5:
	put_structured_constant		1,'$SCNST_58'
	get_value		2,1
	proceed
flag_2_1:
	suspend		flag_2_0
	module_entry		mpimos_cmd_code
	predicate		put_all,4
put_all_4_0:
	try_me_else		put_all_4_1
	jump_on_non_list_var_var		1,put_all_4_3,5,6
	put_func		7,3,put_at
	write_element_marked_value		7,1,4
	write_element_value		7,2,5
	get_reused_list_val_var		2,1,1,7,5
	put_values_dec		1,6,2
	execute		4,put_all_4_0
put_all_4_3:
	check_nil		1,put_all_4_1
	collect_value		4
	get_value		2,3
	proceed
put_all_4_1:
	suspend		put_all_4_0
	module_entry		mpimos_cmd_code
	predicate		public_action,3
public_action_3_0:
	try_me_else		public_action_3_1
	jump_on_non_list_var_var		1,public_action_3_3,4,5
	wait_atom		2,success
	put_reused_list_val_val		1,1,4,5
	put_value		2,3
	execute		2,display_public_2_0
public_action_3_3:
	check_nil		1,public_action_3_1
	wait_atom		2,success
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_59'
	put_list_val_val		4,2,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,5
	execute		1,wait_1_0
public_action_3_1:
	otherwise		public_action_3_0
	collect_value		1
	put_func		1,2,flush
	write_element_variable		1,1,6
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	put_structured_constant		4,'$SCNST_60'
	put_list_val_val		5,4,1
	put_func		1,2,putt
	write_element_value		1,1,2
	put_list_val_val		2,1,5
	put_structured_constant		1,'$SCNST_61'
	put_list_val_val		4,1,2
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	put_value		1,6
	execute		1,fail_action_1_0
public_action_3_8:
	suspend		public_action_3_0
	module_entry		mpimos_cmd_code
	predicate		display_public,2
display_public_2_0:
	try_me_else		display_public_2_1
	jump_on_non_list_var_var		1,display_public_2_3,3,4
	vector		3
	put_integer		7,0
	g_vector_element		3,7,5
	put_integer		8,1
	g_vector_element		3,8,6
	mark_element		3,7
	mark_element		3,8
	collect_value		3
	put_structured_constant		3,'$SCNST_62'
	put_func		7,2,putt
	write_element_value		7,1,6
	put_reused_list_val_val		1,1,7,3
	put_structured_constant		3,'$SCNST_63'
	put_list_val_val		6,3,1
	put_func		1,2,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	put_func		1,2,window
	write_element_value		1,1,3
	get_list_val_var		2,5,1,3
	put_values_dec		1,4,2
	execute		2,display_public_2_0
display_public_2_3:
	check_nil		1,display_public_2_1
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_structured_constant		3,'$SCNST_64'
	put_list_val_val		4,3,1
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,5
	execute		1,wait_1_0
display_public_2_1:
	suspend		display_public_2_0
	module_entry		mpimos_cmd_code
	predicate		return_public,4
return_public_4_0:
	try_me_else		return_public_4_1
	wait_atom		3,success
	get_nil		4
	execute_external		mpimos_cmd_utl,protect,2
return_public_4_1:
	otherwise		return_public_4_0
	collect_value		2
	collect_value		1
	put_func		1,2,flush
	write_element_variable		1,1,6
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_65'
	put_list_val_val		5,2,1
	put_func		1,2,putt
	write_element_value		1,1,3
	put_list_val_val		2,1,5
	put_structured_constant		1,'$SCNST_66'
	put_list_val_val		3,1,2
	put_func		1,2,window
	write_element_value		1,1,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		4,2
	put_value		1,6
	execute		1,fail_action_1_0
return_public_4_6:
	suspend		return_public_4_0
	module_entry		mpimos_cmd_code
	predicate		abort_action,1
abort_action_1_0:
	try_me_else		abort_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_67'
	put_void		3
	b_raise		2,1,3
	proceed
abort_action_1_1:
	suspend		abort_action_1_0
	module_entry		mpimos_cmd_code
	predicate		fail_action,1
fail_action_1_0:
	try_me_else		fail_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_68'
	put_void		3
	b_raise		2,1,3
	proceed
fail_action_1_1:
	suspend		fail_action_1_0
	module_entry		mpimos_cmd_code
	predicate		append_mess,3
append_mess_3_0:
	try_me_else		append_mess_3_1
	jump_on_non_list_var_var		1,append_mess_3_3,4,5
	put_func		6,2,flush
	write_element_void		6,1
	put_reused_list_val_var		1,1,6,6
	put_list_val_val		7,4,1
	get_list_value		3,7
	put_value		1,5
	put_value		3,6
	execute		3,append_mess_3_0
append_mess_3_3:
	check_nil		1,append_mess_3_1
	get_value		2,3
	proceed
append_mess_3_1:
	suspend		append_mess_3_0
	module_entry		mpimos_cmd_code
	predicate		compile_one_file,4
compile_one_file_4_0:
	put_func		5,2,getuc
	write_element_variable		5,1,8
	get_list_val_var		1,6,5,5
	put_structured_constant		1,'$SCNST_69'
	put_variable		6,9
	b_append_string		1,6,1
	create_goal		7
	set_value		1,5
	set_variable		2,10
	put_func		5,2,getl
	write_element_void		5,1
	put_list		6
	write_car_value		6,5
	write_cdr_nil		6
	put_structured_constant		5,'$SCNST_70'
	put_list_val_val		7,5,6
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,7
	set_value		3,5
	set_values_inc		4,2,2
	set_integer		6,3
	set_value		7,4
	enqueue_goal		7,compile_one_file_7_0
	create_goal		2
	put_list		2
	write_car_atom		2,show
	write_cdr_value		2,10
	set_values_dec		1,2,2
	enqueue_goal_external		mpimos_window,create,2
	put_values_inc		1,8,2
	execute_external		mpimos_utility,integer_to_string,2
compile_one_file_4_1:
	suspend		compile_one_file_4_0
	module_entry		mpimos_cmd_code
	predicate		compile_one_file,7
compile_one_file_7_0:
	put_func		8,2,flush
	write_element_variable		8,1,11
	put_list		9
	write_car_value		9,8
	write_cdr_nil		9
	put_structured_constant		8,'$SCNST_71'
	put_list_val_val		10,8,9
	put_func		8,2,putt
	write_element_marked_value		8,1,4
	put_list_val_val		9,8,10
	put_func		8,2,window
	write_element_value		8,1,9
	get_list_val_var		1,9,8,8
	create_goal		10
	set_value		1,8
	set_values_inc		2,2,2
	set_variable		4,8
	set_variable		5,1
	set_values_inc		6,6,2
	set_variable		8,2
	set_value		9,11
	set_marked_variable		10,3
	enqueue_goal		10,compile_wait_in_file_10_0
	create_goal		4
	set_value		1,8
	set_value		2,3
	set_atom		3,r
	set_value		4,2
	enqueue_goal_external		mpimos_file,create,4
	create_goal		3
	set_value		1,5
	put_structured_constant		2,'$SCNST_72'
	set_values_dec		2,2,2
	enqueue_goal_external		mpimos_utility,extend_name,3
	put_value		1,4
	put_structured_constant		2,'$SCNST_73'
	execute_external		mpimos_utility,extend_name,3
compile_one_file_7_1:
	suspend		compile_one_file_7_0
	module_entry		mpimos_cmd_code
	predicate		compile_wait_in_file,10
compile_wait_in_file_10_0:
	try_me_else		compile_wait_in_file_10_1
	jump_on_non_atom		8,compile_wait_in_file_10_3
	test_atom		8,success,compile_wait_in_file_10_1
	wait_atom		9,done
	collect_value		10
	create_goal		9
	set_values_inc		1,1,4
	set_variable		5,1
	set_values_inc		6,6,2
	set_variable		8,4
	set_marked_value		9,5
	enqueue_goal		9,compile_wait_out_file_9_0
	put_value		2,5
	put_atom		3,w
	execute_external		mpimos_file,create,4
compile_wait_in_file_10_3:
	check_vector		8,2,compile_wait_in_file_10_1
	read_element		8,0,11
	wait_atom		11,error
	read_element		8,1,11
	wait_atom		9,done
	collect_value		6
	collect_value		5
	collect_value		3
	put_reused_func		3,8,flush
	write_element_variable		3,1,8
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,5
	put_structured_constant		5,'$SCNST_74'
	put_list_val_val		6,5,3
	put_func		3,2,putt
	write_element_marked_value		3,1,11
	put_list_val_val		5,3,6
	put_structured_constant		3,'$SCNST_75'
	put_list_val_val		6,3,5
	put_func		3,2,putt
	write_element_value		3,1,10
	put_list_val_val		5,3,6
	put_structured_constant		3,'$SCNST_76'
	put_list_val_val		6,3,5
	put_func		3,2,window
	write_element_value		3,1,6
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	get_list_value		1,5
	get_nil		2
	get_nil		4
	put_value		1,8
	put_value		2,11
	put_value		3,7
	execute		3,return_status_3_0
compile_wait_in_file_10_1:
	suspend		compile_wait_in_file_10_0
	module_entry		mpimos_cmd_code
	predicate		compile_wait_out_file,9
compile_wait_out_file_9_0:
	try_me_else		compile_wait_out_file_9_1
	jump_on_non_atom		8,compile_wait_out_file_9_3
	test_atom		8,success,compile_wait_out_file_9_1
	collect_value		9
	put_value		9,2
	create_goal		6
	set_value		1,1
	set_variable		2,8
	set_value		3,3
	set_value		4,7
	set_marked_variable		5,3
	set_variable		6,2
	enqueue_goal		6,wait_compile_one_file_6_0
	create_goal		6
	set_value		1,6
	set_values_inc		2,4,2
	set_variable		4,5
	set_variable		5,4
	set_value		6,3
	enqueue_goal_external		kl1cmp_command,compile_for_pdss,6
	put_func		1,2,flush
	write_element_value		1,1,2
	put_list_val_val		2,1,8
	put_func		1,2,putt
	write_element_value		1,1,3
	put_list_val_val		3,1,2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_func		2,2,putt
	write_element_value		2,1,4
	put_list_val_val		3,2,1
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_value		1,5
	put_value		3,9
	execute		3,append_mess_3_0
compile_wait_out_file_9_3:
	check_vector		8,2,compile_wait_out_file_9_1
	read_element		8,0,10
	wait_atom		10,error
	read_element		8,1,10
	collect_value		6
	collect_value		3
	put_reused_func		3,8,flush
	write_element_variable		3,1,11
	put_list		6
	write_car_value		6,3
	write_cdr_nil		6
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,6
	put_structured_constant		6,'$SCNST_77'
	put_list_val_val		8,6,3
	put_func		3,2,putt
	write_element_marked_value		3,1,10
	put_list_val_val		6,3,8
	put_structured_constant		3,'$SCNST_78'
	put_list_val_val		8,3,6
	put_func		3,2,putt
	write_element_value		3,1,9
	put_list_val_val		6,3,8
	put_structured_constant		3,'$SCNST_79'
	put_list_val_val		8,3,6
	put_func		3,2,window
	write_element_value		3,1,8
	put_list		6
	write_car_value		6,3
	write_cdr_nil		6
	get_list_value		1,6
	get_nil		4
	get_nil		5
	get_nil		2
	put_values_dec		1,11,2
	put_value		3,7
	execute		3,return_status_3_0
compile_wait_out_file_9_1:
	suspend		compile_wait_out_file_9_0
	module_entry		mpimos_cmd_code
	predicate		wait_compile_one_file,6
wait_compile_one_file_6_0:
	try_me_else		wait_compile_one_file_6_1
	wait_atom		5,success
	wait		6
	collect_value		6
	collect_value		3
	put_func		3,2,flush
	write_element_variable		3,1,7
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,5
	put_structured_constant		5,'$SCNST_80'
	put_list_val_val		6,5,3
	put_func		3,2,window
	write_element_value		3,1,6
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	get_list_value		1,5
	get_nil		2
	put_value		1,7
	put_atom		2,success
	put_value		3,4
	execute		3,return_status_3_0
wait_compile_one_file_6_1:
	otherwise		wait_compile_one_file_6_0
	try_me_else		wait_compile_one_file_6_6
	wait		6
	put_func		6,2,flush
	write_element_variable		6,1,9
	put_list		7
	write_car_value		7,6
	write_cdr_nil		7
	put_list		6
	write_car_atom		6,nl
	write_cdr_value		6,7
	put_structured_constant		7,'$SCNST_81'
	put_list_val_val		8,7,6
	put_func		6,2,window
	write_element_value		6,1,8
	put_list		7
	write_car_value		7,6
	write_cdr_nil		7
	get_list_value		1,7
	put_func		1,2,flush
	write_element_variable		1,1,7
	put_list		6
	write_car_value		6,1
	write_cdr_nil		6
	put_func		1,2,do
	write_element_value		1,1,3
	put_list_val_val		3,1,6
	get_list_value		2,3
	create_goal		3
	set_variable		1,3
	set_values_dec		2,5,2
	enqueue_goal		3,return_status_3_0
	put_value		1,9
	put_value		2,7
	execute		3,return_status_3_0
wait_compile_one_file_6_6:
	suspend		wait_compile_one_file_6_0
	module_entry		mpimos_cmd_code
	predicate		return_status,3
return_status_3_0:
	try_me_else		return_status_3_1
	wait		1
	get_value		3,2
	proceed
return_status_3_1:
	suspend		return_status_3_0
	module_entry		mpimos_cmd_code
	predicate		wait_comp,1
wait_comp_1_0:
	try_me_else		wait_comp_1_1
	wait_atom		1,success
	proceed
wait_comp_1_1:
	otherwise		wait_comp_1_0
	collect_value		1
	put_atom		1,done
	execute		1,fail_action_1_0
wait_comp_1_6:
	suspend		wait_comp_1_0
	module_entry		mpimos_cmd_code
	predicate		wait_comp1,5
wait_comp1_5_0:
	try_me_else		wait_comp1_5_1
	wait_atom		5,success
	create_goal		3
	set_values_inc		1,2,2
	set_variable		3,5
	enqueue_goal		3,wait_comp1_load_3_0
	put_void		2
	put_value		3,4
	put_atom		4,nodebug
	execute		5,load_one_file_5_0
wait_comp1_5_1:
	otherwise		wait_comp1_5_0
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	get_nil		1
	put_atom		1,done
	execute		1,fail_action_1_0
wait_comp1_5_6:
	suspend		wait_comp1_5_0
	module_entry		mpimos_cmd_code
	predicate		wait_comp1_load,3
wait_comp1_load_3_0:
	try_me_else		wait_comp1_load_3_1
	wait_atom		3,success
	put_value		4,1
	create_goal		1
	set_variable		1,3
	enqueue_goal		1,wait_1_0
	put_func		1,3,delete
	write_elements_inc		1,1,2,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_value		1,2
	put_value		2,4
	put_void		3
	execute_external		mpimos_directory,create,3
wait_comp1_load_3_1:
	otherwise		wait_comp1_load_3_0
	collect_value		3
	put_value		4,1
	create_goal		1
	set_variable		1,3
	enqueue_goal		1,fail_action_1_0
	put_func		1,3,delete
	write_elements_inc		1,1,2,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_value		1,2
	put_value		2,4
	put_void		3
	execute_external		mpimos_directory,create,3
wait_comp1_load_3_6:
	suspend		wait_comp1_load_3_0
	module_entry		mpimos_cmd_code
	predicate		kl1cmp_input_window,7
kl1cmp_input_window_7_0:
	put_func		8,3,getft
	write_element_variable		8,1,12
	write_element_void		8,2
	put_list_val_var		9,8,13
	put_structured_constant		8,'$SCNST_82'
	put_list_val_val		10,8,9
	put_func		8,3,getft
	write_element_variable		8,1,11
	write_element_void		8,2
	put_list_val_val		9,8,10
	put_structured_constant		8,'$SCNST_83'
	put_list_val_val		10,8,9
	put_func		8,3,getft
	write_element_value		8,1,2
	write_element_void		8,2
	put_list_val_val		2,8,10
	put_structured_constant		8,'$SCNST_84'
	put_list_val_val		9,8,2
	put_func		2,3,getft
	write_element_marked_value		2,1,1
	write_element_void		2,2
	put_list_val_val		8,2,9
	put_structured_constant		2,'$SCNST_85'
	put_list_val_val		9,2,8
	get_list_value		6,9
	b_atom_name		11,2
	get_value		2,3
	b_atom_name		12,2
	get_value		2,4
	put_value		2,5
	put_value		3,13
	put_value		4,7
	execute		4,kl1cmp_input_window1_4_0
kl1cmp_input_window_7_1:
	suspend		kl1cmp_input_window_7_0
	module_entry		mpimos_cmd_code
	predicate		kl1cmp_input_window1,4
kl1cmp_input_window1_4_0:
	try_me_else		kl1cmp_input_window1_4_1
	atom		1
	branch_on_atom		1,2,kl1cmp_input_window1_4_1
	bucket_entry_a		no,kl1cmp_input_window1_4_3
	bucket_entry_a		yes,kl1cmp_input_window1_4_4
kl1cmp_input_window1_4_3:
	collect_value		2
	get_value		3,4
	proceed
kl1cmp_input_window1_4_4:
	put_func		1,3,getft
	write_element_variable		1,1,6
	write_element_void		1,2
	put_list_val_val		5,1,4
	put_structured_constant		1,'$SCNST_86'
	put_list_val_val		4,1,5
	get_list_value		3,4
	b_atom_name		6,1
	get_value		1,2
	proceed
kl1cmp_input_window1_4_1:
	suspend		kl1cmp_input_window1_4_0
	module_entry		mpimos_cmd_code
	predicate		wait_kl1cmp,5
wait_kl1cmp_5_0:
	try_me_else		wait_kl1cmp_5_1
	atom		2
	branch_on_atom		2,2,wait_kl1cmp_5_1
	bucket_entry_a		no,wait_kl1cmp_5_3
	bucket_entry_a		yes,wait_kl1cmp_5_4
wait_kl1cmp_5_3:
	wait_atom		5,success
	collect_value		4
	collect_value		3
	get_nil		1
	put_integer		1,0
	execute		1,halt_1_0
wait_kl1cmp_5_4:
	wait_atom		5,success
	put_vector		5,2
	write_element_variable		5,0,6
	write_element_variable		5,1,2
	get_vector_value		1,5
	create_goal		4
	set_value		1,2
	set_value		2,4
	set_variable		3,2
	set_variable		4,5
	enqueue_goal		4,wait_kl1cmp_load_4_0
	put_value		1,6
	put_atom		4,nodebug
	execute		5,load_one_file_5_0
wait_kl1cmp_5_1:
	otherwise		wait_kl1cmp_5_0
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	get_nil		1
	put_integer		1,1
	execute		1,halt_1_0
wait_kl1cmp_5_7:
	suspend		wait_kl1cmp_5_0
	module_entry		mpimos_cmd_code
	predicate		wait_kl1cmp_load,4
wait_kl1cmp_load_4_0:
	try_me_else		wait_kl1cmp_load_4_1
	wait_atom		4,success
	put_value		5,2
	create_goal		1
	set_variable		1,4
	enqueue_goal		1,wait_kl1cmp_save_1_0
	put_value		2,3
	put_value		3,5
	execute		4,save_one_file_4_0
wait_kl1cmp_load_4_1:
	otherwise		wait_kl1cmp_load_4_0
	collect_value		4
	collect_value		3
	collect_value		2
	get_nil		1
	put_integer		1,1
	execute		1,halt_1_0
wait_kl1cmp_load_4_6:
	suspend		wait_kl1cmp_load_4_0
	module_entry		mpimos_cmd_code
	predicate		wait_kl1cmp_save,1
wait_kl1cmp_save_1_0:
	try_me_else		wait_kl1cmp_save_1_1
	wait_atom		1,success
	put_integer		1,0
	execute		1,halt_1_0
wait_kl1cmp_save_1_1:
	otherwise		wait_kl1cmp_save_1_0
	collect_value		1
	put_integer		1,1
	execute		1,halt_1_0
wait_kl1cmp_save_1_6:
	suspend		wait_kl1cmp_save_1_0
	module_entry		mpimos_cmd_code
	predicate		halt,1
halt_1_0:
	try_me_else		halt_1_1
	g_halt		1
	collect_value		1
	proceed
halt_1_1:
	suspend		halt_1_0
	module_entry		mpimos_cmd_code
	predicate		compile_action,3
compile_action_3_0:
	try_me_else		compile_action_3_1
	jump_on_non_list_var_var		1,compile_action_3_3,4,5
	wait		3
	collect_list		1
	put_vector		7,2
	write_element_variable		7,0,1
	write_element_variable		7,1,6
	get_vector_value		2,7
	create_goal		5
	set_values_inc		1,5,2
	set_marked_value		3,4
	set_variable		4,5
	set_value		5,3
	enqueue_goal		5,wait_compile_5_0
	put_value		2,4
	put_values_inc		3,4,2
	execute		4,compile_one_file_4_0
compile_action_3_3:
	check_nil		1,compile_action_3_1
	wait_atom		3,success
	get_nil		2
	proceed
compile_action_3_1:
	otherwise		compile_action_3_0
	try_me_else		compile_action_3_8
	wait_nil		1
	collect_value		3
	get_nil		2
	put_atom		1,done
	execute		1,fail_action_1_0
compile_action_3_8:
	suspend		compile_action_3_0
	module_entry		mpimos_cmd_code
	predicate		wait_compile,5
wait_compile_5_0:
	try_me_else		wait_compile_5_1
	wait_atom		4,success
	put_vector		7,2
	write_element_variable		7,0,6
	write_element_variable		7,1,4
	get_vector_value		2,7
	create_goal		6
	set_value		1,1
	set_value		2,4
	set_marked_value		3,3
	set_variable		4,2
	set_variable		5,1
	set_value		6,5
	enqueue_goal		6,wait_compile_load_6_0
	create_goal		5
	set_value		1,6
	set_value		2,2
	set_variable		3,4
	set_atom		4,nodebug
	set_value		5,1
	enqueue_goal		5,load_one_file_5_0
	put_value		1,3
	put_structured_constant		2,'$SCNST_87'
	put_value		3,4
	execute_external		mpimos_utility,extend_name,3
wait_compile_5_1:
	otherwise		wait_compile_5_0
	collect_value		5
	collect_value		3
	put_value		3,4
	execute		3,compile_action_3_0
wait_compile_5_6:
	suspend		wait_compile_5_0
	module_entry		mpimos_cmd_code
	predicate		wait_compile_load,6
wait_compile_load_6_0:
	try_me_else		wait_compile_load_6_1
	wait_atom		5,success
	collect_value		6
	put_vector		7,2
	write_element_variable		7,0,6
	write_element_variable		7,1,5
	get_vector_value		2,7
	create_goal		3
	set_value		1,1
	set_value		2,5
	set_variable		3,5
	enqueue_goal		3,compile_action_3_0
	put_value		1,6
	put_value		2,4
	put_value		4,5
	execute		4,save_one_file_4_0
wait_compile_load_6_1:
	otherwise		wait_compile_load_6_0
	collect_value		6
	collect_value		4
	collect_value		3
	put_value		3,5
	execute		3,compile_action_3_0
wait_compile_load_6_6:
	suspend		wait_compile_load_6_0
	module_entry		mpimos_cmd_code
	predicate		correct_extention,3
correct_extention_3_0:
	try_me_else		correct_extention_3_1
	jump_on_non_list		1,correct_extention_3_3
	read_car		1,4
	jump_on_non_atom		4,correct_extention_3_5
	test_nil		4,correct_extention_3_6
	try_me_else		correct_extention_3_6
	read_cdr		1,5
	wait_nil		5
	collect_list		1
	collect_value		2
	get_nil		3
	proceed
correct_extention_3_6:
	try_me_else		correct_extention_3_1
	read_cdr		1,5
	put_nil		6
	g_diff		4,6
	collect_value		6
	b_atom_name		4,4
	put_reused_list		7,1
	write_car_variable		7,1
	write_cdr_variable		7,6
	get_list_value		3,7
	create_goal		3
	set_value		1,5
	set_marked_value		2,2
	set_value		3,6
	enqueue_goal		3,correct_extention_3_0
	create_goal		3
	set_variable		1,3
	set_values_dec		2,2,2
	enqueue_goal		3,delete_extention_one_3_0
	put_values_dec		1,4,2
	execute_external		mpimos_utility,compress,2
correct_extention_3_5:
	is_string		4,correct_extention_3_1
	read_cdr		1,5
	g_string		4,6,7
	put_reused_list		7,1
	write_car_variable		7,1
	write_cdr_variable		7,6
	get_list_value		3,7
	create_goal		3
	set_value		1,5
	set_marked_value		2,2
	set_value		3,6
	enqueue_goal		3,correct_extention_3_0
	create_goal		3
	set_variable		1,3
	set_values_dec		2,2,2
	enqueue_goal		3,delete_extention_one_3_0
	put_values_dec		1,4,2
	execute_external		mpimos_utility,compress,2
correct_extention_3_3:
	check_nil		1,correct_extention_3_1
	collect_value		2
	get_nil		3
	proceed
correct_extention_3_1:
	suspend		correct_extention_3_0
	module_entry		mpimos_cmd_code
	predicate		delete_extention_one,3
delete_extention_one_3_0:
	try_me_else		delete_extention_one_3_1
	string		1
	string		2
	g_string		1,4,5
	g_string		2,6,7
	try_me_else		delete_extention_one_3_4
	g_less_than		6,4
	put_value		8,2
	put_value		5,3
	put_marked_value		2,6
	b_subtract		4,2,2
	put_marked_value		3,2
	b_substring		1,3,6,4,1
	put_value		3,8
	execute		5,delete_extention_one_1_5_0
delete_extention_one_3_4:
	collect_value		2
	get_value		3,1
	proceed
delete_extention_one_3_1:
	suspend		delete_extention_one_3_0
	module_entry		mpimos_cmd_code
	predicate		delete_extention_one_1,5
delete_extention_one_1_5_0:
	try_me_else		delete_extention_one_1_5_1
	g_diff		3,4
	collect_value		4
	collect_value		3
	collect_value		2
	get_value		5,1
	proceed
delete_extention_one_1_5_1:
	try_me_else		delete_extention_one_1_5_2
	wait_value		3,4
	collect_value		3
	collect_value		4
	put_integer		3,0
	b_substring		1,3,2,2,1
	get_value		2,5
	proceed
delete_extention_one_1_5_2:
	suspend		delete_extention_one_1_5_0
	module_entry		mpimos_cmd_code
	predicate		ch_svdir_action,3
ch_svdir_action_3_0:
	try_me_else		ch_svdir_action_3_1
	string		3
	g_string		3,4,5
	wait_integer		5,8
	create_goal		3
	set_value		1,1
	set_variable		2,4
	set_variable		3,1
	enqueue_goal		3,ch_svdir_action0_3_0
	create_goal		3
	set_value		1,4
	set_variable		2,4
	set_value		3,1
	enqueue_goal_external		mpimos_directory,create,3
	put_value		1,3
	put_value		3,4
	execute_external		mpimos_utility,pathname,3
ch_svdir_action_3_1:
	otherwise		ch_svdir_action_3_0
	put_func		4,2,flush
	write_element_void		4,1
	put_list		5
	write_car_value		5,4
	write_cdr_nil		5
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,5
	put_func		5,2,putt
	write_element_value		5,1,3
	put_list_val_val		3,5,4
	put_structured_constant		4,'$SCNST_88'
	put_list_val_val		5,4,3
	put_func		3,2,window
	write_element_value		3,1,5
	get_list_val_var		1,4,3,3
	create_goal		3
	set_value		1,3
	set_variable		2,3
	set_variable		3,1
	enqueue_goal		3,ch_svdir_action0_3_0
	create_goal		3
	set_value		1,3
	set_variable		2,3
	set_value		3,1
	enqueue_goal_external		mpimos_directory,create,3
	put_structured_constant		1,'$SCNST_89'
	execute_external		mpimos_utility,pathname,3
ch_svdir_action_3_5:
	suspend		ch_svdir_action_3_0
	module_entry		mpimos_cmd_code
	predicate		ch_svdir_action0,3
ch_svdir_action0_3_0:
	try_me_else		ch_svdir_action0_3_1
	jump_on_non_atom		3,ch_svdir_action0_3_3
	test_atom		3,success,ch_svdir_action0_3_1
	put_value		6,1
	put_func		1,2,pathname
	write_element_marked_variable		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	create_goal		1
	set_variable		1,5
	enqueue_goal		1,wait_1_0
	put_structured_constant		1,'$SCNST_90'
	put_func		2,2,putb
	write_element_value		2,1,4
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_91'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_func		2,3,setenv
	write_element_atom		2,1,savedir
	write_element_value		2,2,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,flush
	write_element_value		2,1,5
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_func		2,2,window
	write_element_value		2,1,4
	put_list_val_val		4,2,3
	put_value		2,6
	put_value		3,4
	execute_external		mpimos_cmd_utl,send_shell,3
ch_svdir_action0_3_3:
	check_vector		3,2,ch_svdir_action0_3_1
	read_element		3,0,4
	wait_atom		4,error
	read_element		3,1,4
	collect_value		4
	get_nil		2
	put_reused_func		2,3,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_92'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,fail_action_1_0
ch_svdir_action0_3_1:
	suspend		ch_svdir_action0_3_0
	module_entry		mpimos_cmd_code
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait		1
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_cmd_code
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,code
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_93'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_94'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_cmd_code
'$SCNST_0_0':
	define_desc		3,2
	define_integer		1347243843
	define_integer		1380273225
'$SCNST_69':
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		11,1
	define_integer		2112032
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		27,2
	define_integer		1886221359
	define_integer		47
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		3,1
	define_integer		1836278062
'$SCNST_3_0':
	define_string		'$SCNST_3_1'
	define_atom		[]
'$SCNST_3':
	define_list		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		3,3
	define_integer		1936942192
	define_integer		611347811
	define_integer		606348324
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		3,1
	define_integer		829188910
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_6_2':
	define_desc		11,1
	define_integer		2112032
'$SCNST_6_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_6_2'
'$SCNST_6_0':
	define_vector		'$SCNST_6_1'
	define_atom		[]
'$SCNST_8':
'$SCNST_7':
'$SCNST_6':
	define_list		'$SCNST_6_0'
'$SCNST_9_0':
	define_atom		nl
	define_atom		[]
'$SCNST_90':
'$SCNST_52':
'$SCNST_48':
'$SCNST_40':
'$SCNST_39':
'$SCNST_37':
'$SCNST_18':
'$SCNST_9':
	define_list		'$SCNST_9_0'
'$SCNST_10_1':
	define_desc		19,7
	define_integer		1969713729
	define_integer		1953391981
	define_integer		1869771333
	define_integer		1701060722
	define_integer		1952671092
	define_integer		1763730533
	define_integer		8302
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_1':
	define_desc		19,4
	define_integer		1394620960
	define_integer		1852405345
	define_integer		774774887
	define_integer		8238
'$SCNST_11_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_11_1'
'$SCNST_32':
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_12_1':
	define_desc		3,1
	define_integer		1701736292
'$SCNST_12_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_12_1'
'$SCNST_80':
'$SCNST_34':
'$SCNST_27':
'$SCNST_22':
'$SCNST_20':
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		27,1
	define_integer		62
'$SCNST_13_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_13_1'
'$SCNST_77':
'$SCNST_74':
'$SCNST_65':
'$SCNST_60':
'$SCNST_28':
'$SCNST_23':
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		11,2
	define_integer		1869771333
	define_integer		3940466
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_14_1'
'$SCNST_66':
'$SCNST_61':
'$SCNST_29':
'$SCNST_24':
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_1':
	define_desc		3,3
	define_integer		1684107084
	define_integer		543649385
	define_integer		539897390
'$SCNST_15_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_16_0':
	define_desc		19,3
	define_integer		1650811995
	define_integer		1063085941
	define_integer		8237
'$SCNST_16':
	define_string		'$SCNST_16_0'
'$SCNST_17_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		trace
	define_atom		on
'$SCNST_17':
	define_vector		'$SCNST_17_0'
'$SCNST_19_1':
	define_desc		19,4
	define_integer		1969516365
	define_integer		1847616876
	define_integer		543518049
	define_integer		8250
'$SCNST_19_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_19_1'
'$SCNST_21':
'$SCNST_19':
	define_vector		'$SCNST_19_0'
'$SCNST_25_1':
	define_desc		11,3
	define_integer		1769365843
	define_integer		773875566
	define_integer		2108974
'$SCNST_25_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_25_1'
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_26_0':
	define_desc		11,1
	define_integer		7758195
'$SCNST_26':
	define_string		'$SCNST_26_0'
'$SCNST_30_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_68':
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_31_1':
	define_desc		27,7
	define_integer		543976513
	define_integer		1969516397
	define_integer		544433516
	define_integer		543519329
	define_integer		1702257011
	define_integer		555819108
	define_integer		32
'$SCNST_31_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_31_1'
'$SCNST_31':
	define_vector		'$SCNST_31_0'
'$SCNST_33_1':
	define_desc		11,4
	define_integer		1702257011
	define_integer		1819042143
	define_integer		1684956448
	define_integer		3040357
'$SCNST_33_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_33_1'
'$SCNST_33':
	define_vector		'$SCNST_33_0'
'$SCNST_35_1':
	define_desc		11,7
	define_integer		1869771333
	define_integer		1634934898
	define_integer		1633641846
	define_integer		808414316
	define_integer		1836016416
	define_integer		1684955501
	define_integer		2171168
'$SCNST_35_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_35_1'
'$SCNST_35':
	define_vector		'$SCNST_35_0'
'$SCNST_36_1':
	define_desc		11,2
	define_integer		1953525061
	define_integer		2109049
'$SCNST_36_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_36_1'
'$SCNST_36':
	define_vector		'$SCNST_36_0'
'$SCNST_38_1':
	define_desc		19,3
	define_integer		1702257011
	define_integer		544368996
	define_integer		8253
'$SCNST_38_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_38_1'
'$SCNST_91':
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_41_3':
	define_desc		27,9
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		95
'$SCNST_41_2':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_3'
'$SCNST_41_7':
	define_desc		27,9
	define_integer		1685015840
	define_integer		1600482421
	define_integer		1701667150
	define_integer		1918115872
	define_integer		543515489
	define_integer		1986089760
	define_integer		538993765
	define_integer		1350135891
	define_integer		78
'$SCNST_41_6':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_7'
'$SCNST_41_11':
	define_desc		27,9
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		45
'$SCNST_41_10':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_11'
'$SCNST_41_12':
	define_atom		nl
	define_atom		[]
'$SCNST_41_9':
	define_vector		'$SCNST_41_10'
	define_list		'$SCNST_41_12'
'$SCNST_41_8':
	define_atom		nl
	define_list		'$SCNST_41_9'
'$SCNST_41_5':
	define_vector		'$SCNST_41_6'
	define_list		'$SCNST_41_8'
'$SCNST_41_4':
	define_atom		nl
	define_list		'$SCNST_41_5'
'$SCNST_41_1':
	define_vector		'$SCNST_41_2'
	define_list		'$SCNST_41_4'
'$SCNST_41_0':
	define_desc		0,2
	define_atom		window
	define_list		'$SCNST_41_1'
'$SCNST_41':
	define_vector		'$SCNST_41_0'
'$SCNST_42_2':
	define_desc		27,6
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		45
'$SCNST_42_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_42_2'
'$SCNST_42_3':
	define_atom		nl
	define_atom		[]
'$SCNST_42_0':
	define_vector		'$SCNST_42_1'
	define_list		'$SCNST_42_3'
'$SCNST_42':
	define_list		'$SCNST_42_0'
'$SCNST_43_1':
	define_desc		3,3
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
'$SCNST_43_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_43_1'
'$SCNST_43':
	define_vector		'$SCNST_43_0'
'$SCNST_44_1':
	define_desc		27,6
	define_integer		1918115872
	define_integer		543515489
	define_integer		1986089760
	define_integer		538993765
	define_integer		1350135891
	define_integer		78
'$SCNST_44_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_44_1'
'$SCNST_44':
	define_vector		'$SCNST_44_0'
'$SCNST_45_1':
	define_desc		3,3
	define_integer		1685015840
	define_integer		1600482421
	define_integer		1701667150
'$SCNST_45_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_45_1'
'$SCNST_45':
	define_vector		'$SCNST_45_0'
'$SCNST_46_1':
	define_desc		27,6
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
	define_integer		95
'$SCNST_46_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_46_1'
'$SCNST_46':
	define_vector		'$SCNST_46_0'
'$SCNST_47_1':
	define_desc		3,3
	define_integer		1600085855
	define_integer		1600085855
	define_integer		1600085855
'$SCNST_47_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_47_1'
'$SCNST_47':
	define_vector		'$SCNST_47_0'
'$SCNST_49_0':
	define_desc		0,2
	define_atom		tab
	define_integer		6
'$SCNST_54':
'$SCNST_53':
'$SCNST_50':
'$SCNST_49':
	define_vector		'$SCNST_49_0'
'$SCNST_51_1':
	define_desc		27,1
	define_integer		32
'$SCNST_51_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_51_1'
'$SCNST_55':
'$SCNST_51':
	define_vector		'$SCNST_51_0'
'$SCNST_56_0':
	define_desc		27,1
	define_integer		63
'$SCNST_56':
	define_string		'$SCNST_56_0'
'$SCNST_57_0':
	define_desc		27,1
	define_integer		32
'$SCNST_57':
	define_string		'$SCNST_57_0'
'$SCNST_58_0':
	define_desc		27,1
	define_integer		42
'$SCNST_58':
	define_string		'$SCNST_58_0'
'$SCNST_59_1':
	define_desc		27,11
	define_integer		1852534357
	define_integer		544110447
	define_integer		1818391920
	define_integer		1881170793
	define_integer		1768187250
	define_integer		1702125923
	define_integer		1852383347
	define_integer		1768453152
	define_integer		1869422707
	define_integer		1701606756
	define_integer		46
'$SCNST_59_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_59_1'
'$SCNST_59':
	define_vector		'$SCNST_59_0'
'$SCNST_62_2':
	define_desc		19,1
	define_integer		8236
'$SCNST_62_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_62_2'
'$SCNST_62_0':
	define_vector		'$SCNST_62_1'
	define_atom		[]
'$SCNST_62':
	define_list		'$SCNST_62_0'
'$SCNST_63_1':
	define_desc		27,1
	define_integer		47
'$SCNST_63_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_63_1'
'$SCNST_63':
	define_vector		'$SCNST_63_0'
'$SCNST_64_1':
	define_desc		3,1
	define_integer		776228421
'$SCNST_64_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_64_1'
'$SCNST_64':
	define_vector		'$SCNST_64_0'
'$SCNST_67_0':
	define_desc		0,2
	define_atom		shell
	define_atom		aborted
'$SCNST_67':
	define_vector		'$SCNST_67_0'
'$SCNST_70_1':
	define_desc		3,4
	define_integer		1887007784
	define_integer		1851859045
	define_integer		1701519481
	define_integer		1059072377
'$SCNST_70_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_70_1'
'$SCNST_70':
	define_vector		'$SCNST_70_0'
'$SCNST_71_1':
	define_desc		27,5
	define_integer		1126185504
	define_integer		1768975727
	define_integer		1735289196
	define_integer		774778400
	define_integer		32
'$SCNST_71_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_71_1'
'$SCNST_71':
	define_vector		'$SCNST_71_0'
'$SCNST_72_0':
	define_desc		11,1
	define_integer		7172961
'$SCNST_87':
'$SCNST_72':
	define_string		'$SCNST_72_0'
'$SCNST_73_0':
	define_desc		11,1
	define_integer		3239019
'$SCNST_73':
	define_string		'$SCNST_73_0'
'$SCNST_75_1':
	define_desc		19,1
	define_integer		15392
'$SCNST_75_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_75_1'
'$SCNST_78':
'$SCNST_75':
	define_vector		'$SCNST_75_0'
'$SCNST_76_1':
	define_desc		19,2
	define_integer		1869771333
	define_integer		8306
'$SCNST_76_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_76_1'
'$SCNST_79':
'$SCNST_76':
	define_vector		'$SCNST_76_0'
'$SCNST_81_1':
	define_desc		27,6
	define_integer		1869771333
	define_integer		1664884850
	define_integer		1768975727
	define_integer		1700750700
	define_integer		1919906418
	define_integer		62
'$SCNST_81_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_81_1'
'$SCNST_81':
	define_vector		'$SCNST_81_0'
'$SCNST_82_1':
	define_desc		3,2
	define_integer		541938497
	define_integer		1701603654
'$SCNST_82_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_82_1'
'$SCNST_82':
	define_vector		'$SCNST_82_0'
'$SCNST_83_1':
	define_desc		3,2
	define_integer		540101707
	define_integer		1701603654
'$SCNST_83_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_83_1'
'$SCNST_83':
	define_vector		'$SCNST_83_0'
'$SCNST_84_1':
	define_desc		3,2
	define_integer		1769238607
	define_integer		1702521197
'$SCNST_84_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_84_1'
'$SCNST_84':
	define_vector		'$SCNST_84_0'
'$SCNST_85_1':
	define_desc		3,2
	define_integer		1702064961
	define_integer		1701601901
'$SCNST_85_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_85_1'
'$SCNST_85':
	define_vector		'$SCNST_85_0'
'$SCNST_86_1':
	define_desc		3,2
	define_integer		542523731
	define_integer		1701603654
'$SCNST_86_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_86_1'
'$SCNST_86':
	define_vector		'$SCNST_86_0'
'$SCNST_88_1':
	define_desc		11,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		1986097952
	define_integer		1919509605
	define_integer		2112800
'$SCNST_88_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_88_1'
'$SCNST_88':
	define_vector		'$SCNST_88_0'
'$SCNST_89_0':
	define_desc		11,3
	define_integer		1345204094
	define_integer		1934840644
	define_integer		6649441
'$SCNST_89':
	define_string		'$SCNST_89_0'
'$SCNST_92_1':
	define_desc		3,9
	define_integer		1869771333
	define_integer		1664884850
	define_integer		1869508193
	define_integer		1667309684
	define_integer		1936942435
	define_integer		1768453152
	define_integer		1768169587
	define_integer		1952671090
	define_integer		1048146543
'$SCNST_92_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_92_1'
'$SCNST_92':
	define_vector		'$SCNST_92_0'
'$SCNST_93_0':
	define_desc		19,9
	define_integer		1886220131
	define_integer		1651863596
	define_integer		744712556
	define_integer		1684107116
	define_integer		1986097964
	define_integer		1768696933
	define_integer		1852404851
	define_integer		1952787559
	define_integer		11875
'$SCNST_93':
	define_string		'$SCNST_93_0'
'$SCNST_94_1':
	define_desc		19,9
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1701080931
	define_integer		1836016416
	define_integer		1684955501
	define_integer		11891
'$SCNST_94_3':
	define_desc		11,16
	define_integer		1886220131
	define_integer		1279870504
	define_integer		538978629
	define_integer		538976288
	define_integer		757080096
	define_integer		1126182189
	define_integer		1768975727
	define_integer		1176528236
	define_integer		541412425
	define_integer		543452769
	define_integer		1684107116
	define_integer		544106784
	define_integer		544108398
	define_integer		1667330676
	define_integer		1869422693
	define_integer		3040612
'$SCNST_94_5':
	define_desc		27,14
	define_integer		1886220131
	define_integer		1279870504
	define_integer		1178676293
	define_integer		692407369
	define_integer		757080096
	define_integer		1126182189
	define_integer		1768975727
	define_integer		1176528236
	define_integer		541412425
	define_integer		543452769
	define_integer		1886680431
	define_integer		1092646005
	define_integer		1162627398
	define_integer		46
'$SCNST_94_7':
	define_desc		11,13
	define_integer		1886220131
	define_integer		677735529
	define_integer		1162627398
	define_integer		538976297
	define_integer		757080096
	define_integer		1126182189
	define_integer		1768975727
	define_integer		1176528236
	define_integer		541412425
	define_integer		543452769
	define_integer		1684107116
	define_integer		1634934828
	define_integer		3040630
'$SCNST_94_9':
	define_desc		19,12
	define_integer		1818391920
	define_integer		1294492521
	define_integer		1280656463
	define_integer		538978629
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1651863584
	define_integer		543385964
	define_integer		1293969007
	define_integer		1280656463
	define_integer		11845
'$SCNST_94_11':
	define_desc		19,13
	define_integer		1818391920
	define_integer		1294492521
	define_integer		1280656463
	define_integer		1280322629
	define_integer		757080105
	define_integer		1193291053
	define_integer		1881175141
	define_integer		1768710773
	define_integer		1718558819
	define_integer		1146047776
	define_integer		541412437
	define_integer		1344302964
	define_integer		11852
'$SCNST_94_13':
	define_desc		11,13
	define_integer		1684107116
	define_integer		1279870504
	define_integer		538978629
	define_integer		538976288
	define_integer		757080096
	define_integer		1277177133
	define_integer		543449455
	define_integer		1162627398
	define_integer		544106784
	define_integer		544108398
	define_integer		1667330676
	define_integer		1869422693
	define_integer		3040612
'$SCNST_94_15':
	define_desc		11,12
	define_integer		1634692196
	define_integer		1229334628
	define_integer		539575628
	define_integer		538976288
	define_integer		757080096
	define_integer		1277177133
	define_integer		543449455
	define_integer		1162627398
	define_integer		544106784
	define_integer		1667330676
	define_integer		1869422693
	define_integer		3040612
'$SCNST_94_17':
	define_desc		19,15
	define_integer		1935632483
	define_integer		1684371041
	define_integer		1143501417
	define_integer		1128616521
	define_integer		1498566484
	define_integer		1126182185
	define_integer		1735287144
	define_integer		1634934885
	define_integer		1679844726
	define_integer		1667592809
	define_integer		2037542772
	define_integer		544175136
	define_integer		1163020612
	define_integer		1380930627
	define_integer		11865
'$SCNST_94_19':
	define_desc		11,12
	define_integer		1702257011
	define_integer		1146047784
	define_integer		692407381
	define_integer		538976288
	define_integer		757080096
	define_integer		1394617645
	define_integer		543520353
	define_integer		543516788
	define_integer		1701080931
	define_integer		543584032
	define_integer		1430540109
	define_integer		3032396
'$SCNST_94_21':
	define_desc		11,14
	define_integer		1702257011
	define_integer		1146047784
	define_integer		742739029
	define_integer		1162627398
	define_integer		757080105
	define_integer		1394617645
	define_integer		543520353
	define_integer		543516788
	define_integer		1701080931
	define_integer		543584032
	define_integer		1430540109
	define_integer		1948271948
	define_integer		1229332591
	define_integer		3032396
'$SCNST_94_23':
	define_desc		3,14
	define_integer		1702257011
	define_integer		1819042143
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1394617645
	define_integer		543520353
	define_integer		543976545
	define_integer		543516788
	define_integer		1684107116
	define_integer		1830839397
	define_integer		1819632751
	define_integer		1663071077
	define_integer		778396783
'$SCNST_94_25':
	define_desc		3,15
	define_integer		1953720684
	define_integer		543649385
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1277177133
	define_integer		544502633
	define_integer		543976545
	define_integer		1684107116
	define_integer		1830839397
	define_integer		1819632751
	define_integer		1763734373
	define_integer		1919903342
	define_integer		1769234797
	define_integer		779316847
'$SCNST_94_27':
	define_desc		3,14
	define_integer		1953720684
	define_integer		677867113
	define_integer		1430540109
	define_integer		539575628
	define_integer		757080096
	define_integer		1193291053
	define_integer		1629516901
	define_integer		1814064236
	define_integer		1701077359
	define_integer		1869422692
	define_integer		1701606756
	define_integer		1869881459
	define_integer		1146047776
	define_integer		776293461
'$SCNST_94_26':
	define_string		'$SCNST_94_27'
	define_atom		[]
'$SCNST_94_24':
	define_string		'$SCNST_94_25'
	define_list		'$SCNST_94_26'
'$SCNST_94_22':
	define_string		'$SCNST_94_23'
	define_list		'$SCNST_94_24'
'$SCNST_94_20':
	define_string		'$SCNST_94_21'
	define_list		'$SCNST_94_22'
'$SCNST_94_18':
	define_string		'$SCNST_94_19'
	define_list		'$SCNST_94_20'
'$SCNST_94_16':
	define_string		'$SCNST_94_17'
	define_list		'$SCNST_94_18'
'$SCNST_94_14':
	define_string		'$SCNST_94_15'
	define_list		'$SCNST_94_16'
'$SCNST_94_12':
	define_string		'$SCNST_94_13'
	define_list		'$SCNST_94_14'
'$SCNST_94_10':
	define_string		'$SCNST_94_11'
	define_list		'$SCNST_94_12'
'$SCNST_94_8':
	define_string		'$SCNST_94_9'
	define_list		'$SCNST_94_10'
'$SCNST_94_6':
	define_string		'$SCNST_94_7'
	define_list		'$SCNST_94_8'
'$SCNST_94_4':
	define_string		'$SCNST_94_5'
	define_list		'$SCNST_94_6'
'$SCNST_94_2':
	define_string		'$SCNST_94_3'
	define_list		'$SCNST_94_4'
'$SCNST_94_0':
	define_string		'$SCNST_94_1'
	define_list		'$SCNST_94_2'
'$SCNST_94':
	define_list		'$SCNST_94_0'
