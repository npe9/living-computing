kl1cmp_normalize:
	module		kl1cmp_normalize
	entry		normalize,11,normalize_11_0
	entry		variable_generator,3,variable_generator_3_0
	module_entry		kl1cmp_normalize
	predicate		normalize,11
normalize_11_0:
	try_me_else		normalize_11_1
	wait_vector		4,3
	read_element		4,0,12
	wait_atom		12,:-
	read_element		4,1,12
	read_element		4,2,15
	wait_vector		15,3
	read_element		15,0,13
	wait_atom		13,'|'
	read_elements_inc		15,1,13,2
	collect_vector		15
	b_merge		19,15
	put_reused_vector		4,4
	write_element_variable		4,0,16
	write_element_variable		4,1,17
	write_element_variable		4,2,18
	get_vector_value		19,4
	put_integer		4,512
	b_rltv		4,4
	create_goal		3
	set_values_inc		1,5,2
	set_value		3,15
	enqueue_goal_with_priority		3,variable_generator_3_0,4
	create_goal		8
	set_variable		1,5
	set_value		2,2
	set_value		3,18
	set_value		4,9
	set_nil		5
	set_value		6,3
	set_nil		7
	set_variable		8,4
	enqueue_goal		8,normalize_body_8_0
	create_goal		3
	set_variable		1,3
	set_nil		2
	set_variable		3,2
	enqueue_goal		3,unique_3_0
	create_goal		7
	set_value		1,4
	set_nil		2
	set_value		3,2
	set_nil		4
	set_variable		5,2
	set_void		6
	set_value		7,14
	enqueue_goal		7,convert_body_args_7_0
	create_goal		8
	set_variable		1,4
	set_value		2,5
	set_value		3,17
	set_value		4,8
	set_value		5,3
	set_values_inc		6,10,2
	set_variable		8,3
	enqueue_goal		8,normalize_guard_8_0
	create_goal		13
	set_value		1,1
	set_value		2,4
	set_value		3,16
	set_value		4,3
	set_nil		5
	set_value		6,2
	set_nil		7
	set_marked_variable		8,3
	set_integer		9,0
	set_marked_value		10,12
	set_variable		11,1
	set_value		12,7
	set_value		13,13
	enqueue_goal		13,normalize_args_13_0
	create_goal		3
	set_value		1,1
	set_variable		2,2
	set_value		3,3
	enqueue_goal_external		kl1cmp_reader,gen_functor,3
	put_value		1,12
	execute_external		kl1cmp_reader,functor,3
normalize_11_1:
	suspend		normalize_11_0
	module_entry		kl1cmp_normalize
	predicate		unique,3
unique_3_0:
	try_me_else		unique_3_1
	jump_on_non_list_var_var		3,unique_3_3,4,5
	put_reused_list		6,3
	write_car_marked_value		6,4
	write_cdr_variable		6,3
	get_list_value		1,6
	create_goal		3
	set_values_dec		1,3,2
	set_variable		3,1
	enqueue_goal		3,unique_3_0
	put_nil		2
	put_values_inc		3,4,2
	execute		4,unique_4_0
unique_3_3:
	check_nil		3,unique_3_1
	get_value		1,2
	proceed
unique_3_1:
	suspend		unique_3_0
	module_entry		kl1cmp_normalize
	predicate		unique,4
unique_4_0:
	try_me_else		unique_4_1
	list		4
	read_car		4,6
	wait_value		6,3
	read_cdr		4,5
	collect_list		4
	collect_value		6
	put_value		4,5
	execute		4,unique_4_0
unique_4_1:
	otherwise		unique_4_0
	try_me_else		unique_4_5
	jump_on_non_list_var_var		4,unique_4_7,5,6
	get_reused_list_val_var		1,7,4,5,4
	put_value		1,4
	put_value		4,6
	execute		4,unique_4_0
unique_4_7:
	check_nil		4,unique_4_5
	collect_value		3
	get_value		1,2
	proceed
unique_4_5:
	suspend		unique_4_0
	module_entry		kl1cmp_normalize
	predicate		normalize_args,13
normalize_args_13_0:
	try_me_else		normalize_args_13_1
	integer		8
	test_integer		8,0,normalize_args_13_3
	collect_value		10
	collect_value		9
	get_nil		3
	get_value		6,7
	get_value		1,2
	get_value		11,12
	put_values_inc		1,4,2
	put_value		3,13
	execute		3,convert_term_to_list_3_0
normalize_args_13_3:
	put_integer		14,0
	g_less_than		14,8
	put_vector		14,2
	write_element_variable		14,0,19
	write_element_variable		14,1,18
	put_marked_variable		15,16
	put_nil		17
	b_set_vector_element		10,15,10,17,15
	put_marked_variable		17,20
	b_set_vector_element		11,16,11,17,17
	put_func		11,2,new_variable
	write_element_value		11,1,20
	put_list_val_val		21,11,14
	get_list_value		3,21
	b_decrement		8,3
	b_increment		9,8
	get_value		16,8
	put_func		8,3,=
	write_element_marked_value		8,1,10
	write_element_value		8,2,20
	get_list_val_var		4,9,8,8
	create_goal		13
	set_values_inc		1,1,2
	set_value		3,19
	set_value		4,8
	set_value		5,5
	set_variable		6,4
	set_value		7,7
	set_value		8,3
	set_values_dec		9,16,2
	set_value		11,17
	set_values_inc		12,12,2
	enqueue_goal		13,normalize_args_13_0
	put_value		1,18
	put_value		2,6
	put_value		3,4
	put_value		4,10
	put_value		5,20
	execute		5,add_trans_instr_5_0
normalize_args_13_1:
	suspend		normalize_args_13_0
	module_entry		kl1cmp_normalize
	predicate		convert_term_to_list,3
convert_term_to_list_3_0:
	try_me_else		convert_term_to_list_3_1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,','
	read_elements_inc		3,1,4,2
	collect_vector		3
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	enqueue_goal		3,convert_term_to_list_3_0
	put_values_inc		2,3,2
	execute		3,convert_term_to_list_3_0
convert_term_to_list_3_1:
	otherwise		convert_term_to_list_3_0
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
convert_term_to_list_3_6:
	suspend		convert_term_to_list_3_0
	module_entry		kl1cmp_normalize
	predicate		add_trans_instr,5
add_trans_instr_5_0:
	try_me_else		add_trans_instr_5_1
	wait_vector		4,3
	read_element		4,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		4,1,6,2
	integer		6
	string		7
	g_string		7,8,9
	wait_integer		9,8
	collect_value		5
	put_nil		8
	put_func		5,2,new_variable
	write_element_variable		5,1,9
	put_list_val_val		10,5,8
	get_list_value		1,10
	put_reused_func		1,4,'$VAR'
	write_elements_inc		1,1,6,2
	put_vector		4,2
	write_element_value		4,0,1
	write_element_value		4,1,9
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
add_trans_instr_5_1:
	otherwise		add_trans_instr_5_0
	collect_value		5
	collect_value		4
	get_nil		1
	get_value		2,3
	proceed
add_trans_instr_5_6:
	suspend		add_trans_instr_5_0
	module_entry		kl1cmp_normalize
	predicate		convert_body_args,7
convert_body_args_7_0:
	try_me_else		convert_body_args_7_1
	wait_vector		7,3
	read_element		7,0,8
	wait_atom		8,','
	read_elements_inc		7,1,8,2
	collect_vector		7
	create_goal		7
	set_variable		1,11
	set_value		2,2
	set_variable		3,10
	set_value		4,4
	set_variable		5,7
	set_value		6,6
	set_value		7,9
	enqueue_goal		7,convert_body_args_7_0
	put_value		2,11
	put_value		4,10
	put_values_inc		6,7,2
	execute		7,convert_body_args_7_0
convert_body_args_7_1:
	otherwise		convert_body_args_7_0
	put_list		8
	write_car_variable		8,9
	write_cdr_value		8,2
	put_value		2,8
	put_value		8,9
	execute		8,convert_body_args_one_goal_8_0
convert_body_args_7_6:
	suspend		convert_body_args_7_0
	module_entry		kl1cmp_normalize
	predicate		convert_body_args_one_goal,8
convert_body_args_one_goal_8_0:
	try_me_else		convert_body_args_one_goal_8_1
	vector		7
	put_value		10,7
	g_vector		10,7
	put_value		9,8
	put_value		8,10
	execute		9,convert_body_one_goal_9_0
convert_body_args_one_goal_8_1:
	otherwise		convert_body_args_one_goal_8_0
	execute		8,convert_body_one_arg_8_0
convert_body_args_one_goal_8_5:
	suspend		convert_body_args_one_goal_8_0
	module_entry		kl1cmp_normalize
	predicate		convert_body_one_goal,9
convert_body_one_goal_9_0:
	try_me_else		convert_body_one_goal_9_1
	wait_integer		7,0
	get_value		5,6
	get_value		3,4
	get_value		1,2
	get_value		8,9
	proceed
convert_body_one_goal_9_1:
	otherwise		convert_body_one_goal_9_0
	try_me_else		convert_body_one_goal_9_6
	integer		7
	g_decrement		7,7
	put_marked_value		10,7
	put_variable		12,11
	b_set_vector_element		8,10,8,12,10
	create_goal		9
	set_variable		1,14
	set_value		2,2
	set_variable		3,13
	set_value		4,4
	set_variable		5,12
	set_values_inc		6,6,2
	set_values_dec		8,10,2
	enqueue_goal		9,convert_body_one_goal_9_0
	put_value		2,14
	put_value		4,13
	put_value		6,12
	put_value		7,8
	put_value		8,11
	execute		8,convert_body_one_arg_8_0
convert_body_one_goal_9_6:
	suspend		convert_body_one_goal_9_0
	module_entry		kl1cmp_normalize
	predicate		convert_body_one_arg,8
convert_body_one_arg_8_0:
	try_me_else		convert_body_one_arg_8_1
	wait_list_var_var		5,13,9
	wait_vector		13,2
	read_element		13,0,14
	read_element		13,1,10
	wait_vector		14,3
	read_element		14,0,11
	wait_atom		11,'$VAR'
	read_elements_inc		14,1,11,2
	wait_vector		7,3
	read_element		7,0,15
	wait_atom		15,'$VAR'
	read_element		7,1,15
	wait_value		15,11
	read_element		7,2,16
	wait_value		16,12
	collect_value		15
	collect_value		16
	put_marked_value		10,10
	get_value		10,8
	put_reused_func		8,14,'$VAR'
	write_element_marked_value		8,1,11
	write_element_marked_value		8,2,12
	put_reused_vector		13,13
	write_element_value		13,0,8
	write_element_value		13,1,10
	put_reused_list_val_val		5,5,13,9
	get_list_value		6,5
	put_reused_func		5,7,'$VAR'
	write_elements_inc		5,1,11,2
	put_func		6,2,var
	write_element_value		6,1,5
	put_func		5,3,==
	write_element_value		5,1,10
	write_element_value		5,2,6
	put_list_val_val		6,5,2
	get_list_value		1,6
	put_func		1,3,'$VAR'
	write_elements_inc		1,1,11,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,3,=
	write_element_value		1,1,10
	write_element_value		1,2,2
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
convert_body_one_arg_8_1:
	otherwise		convert_body_one_arg_8_0
	try_me_else		convert_body_one_arg_8_5
	jump_on_non_list_var_var		5,convert_body_one_arg_8_7,9,10
	wait_vector		7,3
	read_element		7,0,11
	wait_atom		11,'$VAR'
	read_elements_inc		7,1,11,2
	integer		11
	string		12
	g_string		12,13,14
	wait_integer		14,8
	get_reused_list_val_var		6,5,5,9,9
	put_reused_func		7,7,'$VAR'
	write_elements_inc		7,1,11,2
	put_values_dec		5,10,2
	execute		8,convert_body_one_arg_8_0
convert_body_one_arg_8_7:
	check_nil		5,convert_body_one_arg_8_5
	get_value		3,4
	get_value		1,2
	get_value		7,8
	get_nil		6
	proceed
convert_body_one_arg_8_5:
	try_me_else		convert_body_one_arg_8_8
	wait		7
	switch_on_type		7,convert_body_one_arg_8_9,convert_body_one_arg_8_10,convert_body_one_arg_8_11,convert_body_one_arg_8_12,convert_body_one_arg_8_13,convert_body_one_arg_8_14
convert_body_one_arg_8_11:
	read_car		7,9
	read_cdr		7,10
	put_reused_list		7,7
	write_car_variable		7,11
	write_cdr_variable		7,13
	get_list_value		8,7
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_variable		3,8
	set_value		4,4
	set_variable		5,7
	set_value		6,6
	set_value		7,10
	set_value		8,13
	enqueue_goal		8,convert_body_one_arg_8_0
	put_value		2,12
	put_value		4,8
	put_value		6,7
	put_value		7,9
	put_value		8,11
	execute		8,convert_body_one_arg_8_0
convert_body_one_arg_8_9:
	get_value		3,4
	get_value		1,2
	get_value		5,6
	get_value		8,7
	proceed
convert_body_one_arg_8_10:
	get_value		3,4
	get_value		1,2
	get_value		5,6
	get_value		8,7
	proceed
convert_body_one_arg_8_12:
	put_value		10,7
	g_vector		10,7
	put_value		9,8
	put_value		8,10
	execute		9,convert_body_one_goal_9_0
convert_body_one_arg_8_13:
	get_value		3,4
	get_value		1,2
	get_value		5,6
	get_value		8,7
	proceed
convert_body_one_arg_8_14:
	is_float		7,convert_body_one_arg_8_8
	get_value		3,4
	get_value		1,2
	get_value		5,6
	get_value		8,7
	proceed
convert_body_one_arg_8_8:
	suspend		convert_body_one_arg_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard,8
normalize_guard_8_0:
	try_me_else		normalize_guard_8_1
	jump_on_non_list_var_var		8,normalize_guard_8_3,9,10
	collect_list		8
	put_vector		12,2
	write_element_variable		12,0,11
	write_element_variable		12,1,8
	get_vector_value		3,12
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,11
	set_variable		4,12
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_value		8,10
	enqueue_goal		8,normalize_guard_8_0
	put_value		2,3
	put_value		3,8
	put_value		5,12
	put_value		7,11
	put_value		8,9
	execute		8,normalize_one_guard_8_0
normalize_guard_8_3:
	check_nil		8,normalize_guard_8_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_guard_8_1:
	suspend		normalize_guard_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_one_guard,8
normalize_one_guard_8_0:
	try_me_else		normalize_one_guard_8_1
	jump_on_non_atom		8,normalize_one_guard_8_3
	test_atom		8,true,normalize_one_guard_8_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_one_guard_8_3:
	check_vector		8,3,normalize_one_guard_8_1
	read_element		8,0,9
	atom		9
	branch_on_atom		9,3,normalize_one_guard_8_1
	bucket_entry_a		$:=,normalize_one_guard_8_5
	bucket_entry_a		:=,normalize_one_guard_8_6
	bucket_entry_a		=,normalize_one_guard_8_7
normalize_one_guard_8_5:
	read_elements_inc		8,1,10,2
	collect_vector		8
	put_values_inc		8,10,2
	execute		9,normalize_guard_float_becomes_9_0
normalize_one_guard_8_6:
	read_elements_inc		8,1,10,2
	collect_vector		8
	put_values_inc		8,10,2
	execute		9,normalize_guard_becomes_9_0
normalize_one_guard_8_7:
	read_elements_inc		8,1,10,2
	collect_vector		8
	put_values_inc		8,10,2
	execute		9,normalize_guard_unify_9_0
normalize_one_guard_8_1:
	otherwise		normalize_one_guard_8_0
	try_me_else		normalize_one_guard_8_15
	wait_vector		8,4
	read_element		8,0,9
	wait_atom		9,vector_element
	read_element		8,1,14
	read_elements_inc		8,2,9,2
	wait_vector		14,3
	read_element		14,0,11
	wait_atom		11,'$VAR'
	read_elements_inc		14,1,11,2
	integer		11
	string		12
	g_string		12,13,15
	wait_integer		15,8
	put_reused_vector		8,8
	write_element_void		8,0
	write_element_void		8,1
	write_element_variable		8,2,13
	write_element_void		8,3
	create_goal		12
	set_values_inc		1,1,5
	set_variable		6,2
	set_value		7,7
	set_variable		8,3
	set_marked_value		9,8
	set_variable		10,7
	set_variable		11,5
	set_variable		12,4
	enqueue_goal		12,dispatch_on_builtin_type_12_0
	create_goal		7
	put_reused_func		1,14,'$VAR'
	write_element_marked_value		1,1,11
	write_element_marked_value		1,2,12
	put_func		14,4,vector_element
	write_element_value		14,1,1
	write_element_value		14,2,9
	write_element_marked_value		14,3,10
	set_value		1,14
	set_values_dec		2,8,2
	set_values_dec		4,5,2
	set_void		6
	set_value		7,3
	enqueue_goal_external		kl1cmp_blttbl,builtin,7
	put_func		1,3,'$VAR'
	write_elements_inc		1,1,11,2
	put_func		4,3,element
	write_element_value		4,1,1
	write_element_value		4,2,13
	put_value		1,6
	put_value		3,10
	execute		4,append_attr_4_0
normalize_one_guard_8_15:
	otherwise		normalize_one_guard_8_0
	try_me_else		normalize_one_guard_8_20
	wait_vector		8,4
	read_element		8,0,9
	wait_atom		9,vector_element
	read_elements_inc		8,1,9,3
	vector		9
	g_vector		9,12
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_reused_func		3,8,vector_element
	write_elements_inc		3,1,9,3
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_0'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_one_guard_8_20:
	otherwise		normalize_one_guard_8_0
	try_me_else		normalize_one_guard_8_25
	wait_vector		8,4
	read_element		8,0,9
	wait_atom		9,vector_element
	read_elements_inc		8,1,9,3
	collect_value		11
	collect_value		10
	collect_vector		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_list		3
	write_car_value		3,9
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_1'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_one_guard_8_25:
	otherwise		normalize_one_guard_8_0
	create_goal		12
	set_values_inc		1,1,7
	set_variable		8,7
	set_variable		9,2
	set_variable		10,3
	set_variable		11,4
	set_variable		12,5
	enqueue_goal		12,dispatch_on_builtin_type_12_0
	put_value		1,8
	put_void		6
	execute_external		kl1cmp_blttbl,builtin,7
normalize_one_guard_8_30:
	suspend		normalize_one_guard_8_0
	module_entry		kl1cmp_normalize
	predicate		dispatch_on_builtin_type,12
dispatch_on_builtin_type_12_0:
	try_me_else		dispatch_on_builtin_type_12_1
	atom		8
	hash_on_atom		8,5,dispatch_on_builtin_type_12_1
	bucket_entry_a		builtin,dispatch_on_builtin_type_12_3
	bucket_entry_a		float_relop,dispatch_on_builtin_type_12_4
	bucket_entry_a		none,dispatch_on_builtin_type_12_5
	bucket_entry_a		relop,dispatch_on_builtin_type_12_6
	bucket_entry_a		type_or_wait,dispatch_on_builtin_type_12_7
dispatch_on_builtin_type_12_3:
	put_values_inc		8,9,4
	execute		11,normalize_guard_builtin_11_0
dispatch_on_builtin_type_12_4:
	collect_value		12
	collect_value		11
	put_vector		8,3
	write_element_variable		8,0,13
	write_element_variable		8,1,11
	write_element_variable		8,2,12
	get_vector_value		3,8
	put_list		3
	write_car_variable		3,14
	write_cdr_nil		3
	put_list		8
	write_car_variable		8,15
	write_cdr_value		8,3
	put_list		3
	write_car_variable		3,16
	write_cdr_value		3,8
	put_list		17
	write_car_variable		17,8
	write_cdr_value		17,3
	get_list_value		10,17
	create_goal		8
	set_variable		1,17
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,3
	set_value		7,7
	set_variable		8,10
	enqueue_goal		8,normalize_guard_8_0
	create_goal		11
	set_variable		1,2
	set_value		2,17
	set_value		3,11
	set_variable		4,5
	set_value		5,13
	set_variable		6,7
	set_value		7,3
	set_values_dec		8,15,2
	set_variable		10,11
	put_list		3
	write_car_value		3,9
	write_cdr_nil		3
	set_value		11,3
	enqueue_goal		11,expand_float_expression_11_0
	put_value		3,12
	put_value		9,16
	execute		11,expand_float_expression_11_0
dispatch_on_builtin_type_12_5:
	collect_value		12
	collect_value		11
	collect_value		10
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_list		3
	write_car_value		3,9
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_2'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
dispatch_on_builtin_type_12_6:
	collect_value		12
	collect_value		11
	put_vector		8,3
	write_element_variable		8,0,13
	write_element_variable		8,1,11
	write_element_variable		8,2,12
	get_vector_value		3,8
	put_list		3
	write_car_variable		3,14
	write_cdr_nil		3
	put_list		8
	write_car_variable		8,15
	write_cdr_value		8,3
	put_list		3
	write_car_variable		3,16
	write_cdr_value		3,8
	put_list		17
	write_car_variable		17,8
	write_cdr_value		17,3
	get_list_value		10,17
	create_goal		8
	set_variable		1,17
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,3
	set_value		7,7
	set_variable		8,10
	enqueue_goal		8,normalize_guard_8_0
	create_goal		11
	set_variable		1,2
	set_value		2,17
	set_value		3,11
	set_variable		4,5
	set_value		5,13
	set_variable		6,7
	set_value		7,3
	set_values_dec		8,15,2
	set_variable		10,11
	put_list		3
	write_car_value		3,9
	write_cdr_nil		3
	set_value		11,3
	enqueue_goal		11,expand_expression_11_0
	put_value		3,12
	put_value		9,16
	execute		11,expand_expression_11_0
dispatch_on_builtin_type_12_7:
	collect_value		12
	put_values_inc		8,9,3
	execute		10,normalize_guard_type_or_wait_10_0
dispatch_on_builtin_type_12_1:
	suspend		dispatch_on_builtin_type_12_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_type_or_wait,10
normalize_guard_type_or_wait_10_0:
	put_vector		11,2
	write_element_variable		11,0,13
	write_element_variable		11,1,12
	get_vector_value		3,11
	put_list_val_var		11,8,8
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,13
	set_value		4,8
	set_value		5,5
	set_variable		6,8
	set_value		7,7
	set_value		8,10
	enqueue_goal		8,normalize_builtin_args_8_0
	put_value		2,3
	put_value		3,12
	put_value		5,11
	put_values_inc		7,8,2
	execute		8,normalize_builtin_args_8_0
normalize_guard_type_or_wait_10_1:
	suspend		normalize_guard_type_or_wait_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_unify,9
normalize_guard_unify_9_0:
	try_me_else		normalize_guard_unify_9_1
	wait_vector		8,3
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		12,8,'$VAR'
	write_elements_inc		12,1,10,2
	put_value		8,9
	put_value		9,12
	execute		9,normalize_guard_unify_variable_9_0
normalize_guard_unify_9_1:
	try_me_else		normalize_guard_unify_9_3
	wait_vector		9,3
	read_element		9,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		9,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		9,9,'$VAR'
	write_elements_inc		9,1,10,2
	execute		9,normalize_guard_unify_variable_9_0
normalize_guard_unify_9_3:
	otherwise		normalize_guard_unify_9_0
	try_me_else		normalize_guard_unify_9_10
	jump_on_non_list_var_var		8,normalize_guard_unify_9_12,10,11
	wait_list_var_var		9,12,13
	put_reused_list_val_val		8,8,10,11
	put_reused_list_val_val		9,9,12,13
	execute		9,normalize_guard_unify_list_list_9_0
normalize_guard_unify_9_12:
	is_vector		8,normalize_guard_unify_9_10
	vector		9
	put_value		12,8
	put_value		11,9
	g_vector		12,10
	g_vector		11,9
	put_value		8,10
	put_value		10,12
	execute		11,normalize_guard_unify_vect_vect_11_0
normalize_guard_unify_9_10:
	otherwise		normalize_guard_unify_9_0
	try_me_else		normalize_guard_unify_9_18
	wait_value		8,9
	collect_value		8
	collect_value		9
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_guard_unify_9_18:
	otherwise		normalize_guard_unify_9_0
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,=
	write_elements_inc		3,1,8,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_3'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_guard_unify_9_20:
	suspend		normalize_guard_unify_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_unify_variable,9
normalize_guard_unify_variable_9_0:
	try_me_else		normalize_guard_unify_variable_9_1
	vector		8
	jump_on_arity		8,4,normalize_guard_unify_variable_9_1
	table_entry		normalize_guard_unify_variable_9_1
	table_entry		normalize_guard_unify_variable_9_1
	table_entry		normalize_guard_unify_variable_9_3
	table_entry		normalize_guard_unify_variable_9_4
normalize_guard_unify_variable_9_3:
	read_element		8,0,10
	wait_atom		10,'$SCNST'
	read_element		8,1,10
	string		10
	put_nil		11
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,11
	get_list_value		3,2
	put_func		1,2,var
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_value		2,1,10
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_guard_unify_variable_9_4:
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,'$VAR'
	write_elements_inc		1,1,10,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,3,=
	write_element_value		1,1,9
	write_element_value		1,2,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_guard_unify_variable_9_1:
	otherwise		normalize_guard_unify_variable_9_0
	try_me_else		normalize_guard_unify_variable_9_7
	wait		8
	switch_on_type		8,normalize_guard_unify_variable_9_8,normalize_guard_unify_variable_9_9,normalize_guard_unify_variable_9_10,normalize_guard_unify_variable_9_11,normalize_guard_unify_variable_9_12,normalize_guard_unify_variable_9_13
normalize_guard_unify_variable_9_10:
	read_car		8,10
	read_cdr		8,11
	put_value		14,9
	put_value		15,6
	put_value		9,7
	put_func		6,3,=
	write_element_marked_value		6,1,14
	write_element_atom		6,2,list
	get_reused_list_val_var		4,7,8,6,8
	create_goal		4
	set_variable		1,13
	set_value		2,5
	set_variable		3,6
	set_variable		4,7
	enqueue_goal		4,'C_4_0'
	put_list_val_val		12,10,11
	put_value		4,8
	put_value		5,13
	put_value		8,15
	put_value		10,12
	put_value		11,14
	execute		11,normalize_list_args_11_0
normalize_guard_unify_variable_9_8:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_guard_unify_variable_9_9:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_guard_unify_variable_9_11:
	put_value		12,8
	g_vector		12,10
	put_value		13,9
	put_values_inc		8,6,2
	put_func		6,2,vector
	write_element_marked_value		6,1,10
	put_func		7,3,=
	write_element_marked_value		7,1,13
	write_element_value		7,2,6
	get_list_val_var		4,6,7,11
	create_goal		4
	set_variable		1,14
	set_value		2,5
	set_variable		3,6
	set_variable		4,7
	enqueue_goal		4,'C_4_0'
	put_value		4,11
	put_value		5,14
	put_integer		11,0
	execute		13,normalize_structure_args_13_0
normalize_guard_unify_variable_9_12:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_guard_unify_variable_9_13:
	is_float		8,normalize_guard_unify_variable_9_7
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_guard_unify_variable_9_7:
	suspend		normalize_guard_unify_variable_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_unify_vect_vect,11
normalize_guard_unify_vect_vect_11_0:
	try_me_else		normalize_guard_unify_vect_vect_11_1
	wait_value		8,9
	collect_value		9
	put_value		9,8
	put_integer		8,0
	execute		11,compare_vect_elements_11_0
normalize_guard_unify_vect_vect_11_1:
	otherwise		normalize_guard_unify_vect_vect_11_0
	collect_value		9
	collect_value		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,=
	write_elements_inc		3,1,10,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_4'
	put_func		5,3,warning_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_guard_unify_vect_vect_11_3:
	suspend		normalize_guard_unify_vect_vect_11_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_unify_list_list,9
normalize_guard_unify_list_list_9_0:
	try_me_else		normalize_guard_unify_list_list_9_1
	wait_list_var_var		8,10,11
	wait_list_var_var		9,12,13
	collect_list		8
	collect_list		9
	put_vector		14,2
	write_element_variable		14,0,9
	write_element_variable		14,1,8
	get_vector_value		3,14
	create_goal		9
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,14
	set_value		5,5
	set_variable		6,9
	set_value		7,7
	set_value		8,11
	set_value		9,13
	enqueue_goal		9,normalize_guard_unify_9_0
	put_value		2,3
	put_value		3,8
	put_value		5,14
	put_values_inc		7,9,2
	put_value		9,12
	execute		9,normalize_guard_unify_9_0
normalize_guard_unify_list_list_9_1:
	suspend		normalize_guard_unify_list_list_9_0
	module_entry		kl1cmp_normalize
	predicate		compare_vect_elements,11
compare_vect_elements_11_0:
	try_me_else		compare_vect_elements_11_1
	integer		8
	vector		10
	g_vector_element		10,8,12
	vector		11
	g_vector_element		11,8,13
	wait_value		12,13
	b_increment		8,8
	execute		11,compare_vect_elements_11_0
compare_vect_elements_11_1:
	try_me_else		compare_vect_elements_11_3
	wait_value		8,9
	collect_value		11
	collect_value		10
	collect_value		8
	collect_value		9
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
compare_vect_elements_11_3:
	otherwise		compare_vect_elements_11_0
	put_vector		12,2
	write_element_variable		12,0,15
	write_element_variable		12,1,14
	get_vector_value		3,12
	put_func		3,3,=
	write_element_marked_value		3,1,10
	write_element_marked_value		3,2,11
	put_list		12
	write_car_value		12,3
	write_cdr_nil		12
	put_structured_constant		3,'$SCNST_5'
	put_func		13,3,warning_message
	write_element_value		13,1,3
	write_element_value		13,2,12
	get_list_val_var		1,3,13,13
	put_marked_value		1,8
	b_increment		1,1
	put_void		3
	b_set_vector_element		10,8,3,3,12
	put_void		3
	b_set_vector_element		11,8,3,3,8
	create_goal		11
	set_variable		1,3
	set_value		2,2
	set_value		3,15
	set_variable		4,16
	set_value		5,5
	set_variable		6,15
	set_value		7,7
	set_value		8,1
	set_value		9,9
	set_value		10,12
	set_value		11,8
	enqueue_goal		11,compare_vect_elements_11_0
	put_value		1,13
	put_value		2,3
	put_value		3,14
	put_value		5,16
	put_value		7,15
	put_values_inc		8,10,2
	execute		9,normalize_guard_unify_9_0
compare_vect_elements_11_6:
	suspend		compare_vect_elements_11_0
	module_entry		kl1cmp_normalize
	predicate		normalize_structure_args,13
normalize_structure_args_13_0:
	try_me_else		normalize_structure_args_13_1
	integer		10
	test_integer		10,0,normalize_structure_args_13_3
	collect_value		13
	collect_value		12
	collect_value		11
	get_nil		3
	get_value		8,9
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_structure_args_13_3:
	put_integer		14,0
	g_less_than		14,10
	put_vector		14,2
	write_element_variable		14,0,16
	write_element_variable		14,1,15
	get_vector_value		3,14
	put_marked_value		3,11
	b_increment		3,3
	b_decrement		10,10
	put_nil		14
	b_set_vector_element		12,11,12,14,14
	create_goal		13
	set_variable		1,17
	set_value		2,2
	set_value		3,16
	set_variable		4,16
	set_value		5,5
	set_variable		6,2
	set_value		7,7
	set_variable		8,5
	set_values_inc		9,9,2
	set_value		11,3
	set_value		12,14
	set_marked_value		13,13
	enqueue_goal		13,normalize_structure_args_13_0
	create_goal		11
	set_value		1,1
	set_value		2,17
	set_value		3,15
	set_value		4,4
	set_value		5,16
	set_value		6,6
	set_value		7,2
	set_variable		8,2
	set_value		9,5
	set_value		10,12
	set_variable		11,3
	enqueue_goal		11,normalize_one_arg_11_0
	put_func		4,3,element
	write_element_value		4,1,13
	write_element_value		4,2,11
	put_value		1,8
	execute		4,append_attr_4_0
normalize_structure_args_13_1:
	suspend		normalize_structure_args_13_0
	module_entry		kl1cmp_normalize
	predicate		normalize_list_args,11
normalize_list_args_11_0:
	try_me_else		normalize_list_args_11_1
	wait_list_var_var		10,12,13
	collect_list		10
	put_vector		15,2
	write_element_variable		15,0,14
	write_element_variable		15,1,10
	get_vector_value		3,15
	create_goal		4
	set_variable		1,3
	set_value		2,9
	set_variable		3,16
	put_func		9,3,element
	write_element_marked_value		9,1,11
	write_element_integer		9,2,1
	set_value		4,9
	enqueue_goal		4,append_attr_4_0
	create_goal		4
	set_variable		1,17
	set_value		2,3
	set_variable		3,15
	put_func		3,3,element
	write_element_value		3,1,11
	write_element_integer		3,2,0
	set_value		4,3
	enqueue_goal		4,append_attr_4_0
	create_goal		11
	set_variable		1,3
	set_value		2,2
	set_value		3,14
	set_variable		4,14
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_variable		8,9
	set_value		9,17
	set_value		10,13
	set_value		11,16
	enqueue_goal		11,normalize_one_arg_11_0
	put_value		2,3
	put_value		3,10
	put_value		5,14
	put_value		7,11
	put_value		10,12
	put_value		11,15
	execute		11,normalize_one_arg_11_0
normalize_list_args_11_1:
	suspend		normalize_list_args_11_0
	module_entry		kl1cmp_normalize
	predicate		append_attr,4
append_attr_4_0:
	try_me_else		append_attr_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	integer		5
	string		6
	g_string		6,7,8
	wait_integer		8,8
	collect_value		6
	collect_vector		3
	put_variable		6,3
	b_set_vector_element		1,5,1,6,5
	get_value		5,2
	put_list		2
	write_car_value		2,4
	write_cdr_nil		2
	execute		3,ap_3_0
append_attr_4_1:
	otherwise		append_attr_4_0
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
append_attr_4_6:
	suspend		append_attr_4_0
	module_entry		kl1cmp_normalize
	predicate		ap,3
ap_3_0:
	try_me_else		ap_3_1
	jump_on_non_list_var_var		1,ap_3_3,4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		3,4
	execute		3,ap_3_0
ap_3_3:
	check_nil		1,ap_3_1
	get_value		2,3
	proceed
ap_3_1:
	suspend		ap_3_0
	module_entry		kl1cmp_normalize
	predicate		normalize_one_arg,11
normalize_one_arg_11_0:
	try_me_else		normalize_one_arg_11_1
	vector		10
	jump_on_arity		10,4,normalize_one_arg_11_1
	table_entry		normalize_one_arg_11_1
	table_entry		normalize_one_arg_11_1
	table_entry		normalize_one_arg_11_3
	table_entry		normalize_one_arg_11_4
normalize_one_arg_11_3:
	read_element		10,0,12
	wait_atom		12,'$SCNST'
	read_element		10,1,12
	string		12
	g_string		12,13,14
	put_nil		13
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_reused_func		1,10,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,13
	put_func		1,2,new_variable
	write_element_marked_value		1,1,11
	put_list_val_val		7,1,2
	get_list_value		3,7
	put_func		1,2,var
	write_element_value		1,1,11
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,var
	write_element_value		2,1,6
	put_func		3,2,unify
	write_element_value		3,1,2
	put_list_val_val		2,3,1
	put_func		1,2,struct
	write_element_value		1,1,12
	put_func		3,3,=
	write_element_value		3,1,11
	write_element_value		3,2,1
	put_list_val_val		1,3,2
	get_list_value		4,1
	proceed
normalize_one_arg_11_4:
	read_element		10,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		10,1,12,2
	integer		12
	string		13
	g_string		13,14,15
	wait_integer		15,8
	put_nil		14
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_value		1,1,11
	put_list_val_val		2,1,14
	get_list_value		3,2
	put_reused_func		1,10,'$VAR'
	write_elements_inc		1,1,12,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,3,=
	write_element_value		1,1,11
	write_element_value		1,2,2
	put_list_val_val		2,1,5
	put_func		1,2,var
	write_element_value		1,1,11
	put_func		3,2,unify
	write_element_value		3,1,1
	put_list_val_val		1,3,2
	get_list_value		4,1
	proceed
normalize_one_arg_11_1:
	otherwise		normalize_one_arg_11_0
	try_me_else		normalize_one_arg_11_7
	wait		10
	switch_on_type		10,normalize_one_arg_11_8,normalize_one_arg_11_9,normalize_one_arg_11_7,normalize_one_arg_11_7,normalize_one_arg_11_7,normalize_one_arg_11_10
normalize_one_arg_11_8:
	put_nil		12
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_value		1,1,11
	put_list_val_val		2,1,12
	get_list_value		3,2
	put_func		1,2,atomic
	write_element_value		1,1,10
	put_func		2,3,=
	write_element_value		2,1,11
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,var
	write_element_value		2,1,11
	put_func		3,2,unify
	write_element_value		3,1,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_one_arg_11_9:
	put_nil		12
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_value		1,1,11
	put_list_val_val		2,1,12
	get_list_value		3,2
	put_func		1,2,atomic
	write_element_value		1,1,10
	put_func		2,3,=
	write_element_value		2,1,11
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,var
	write_element_value		2,1,11
	put_func		3,2,unify
	write_element_value		3,1,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_one_arg_11_10:
	is_float		10,normalize_one_arg_11_7
	put_nil		12
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_value		1,1,11
	put_list_val_val		2,1,12
	get_list_value		3,2
	put_func		1,2,atomic
	write_element_value		1,1,10
	put_func		2,3,=
	write_element_value		2,1,11
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,var
	write_element_value		2,1,11
	put_func		3,2,unify
	write_element_value		3,1,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_one_arg_11_7:
	put_func		12,2,new_variable
	write_element_marked_value		12,1,11
	get_list_val_var		3,14,12,13
	put_func		3,2,var
	write_element_value		3,1,11
	put_func		12,2,unify
	write_element_value		12,1,3
	put_list_val_val		3,12,5
	get_list_value		4,3
	put_value		3,13
	put_values_inc		4,6,6
	execute		9,normalize_guard_unify_variable_9_0
normalize_one_arg_11_11:
	suspend		normalize_one_arg_11_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_becomes,9
normalize_guard_becomes_9_0:
	try_me_else		normalize_guard_becomes_9_1
	jump_on_non_integer		8,normalize_guard_becomes_9_3
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,12
	get_vector_value		3,11
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_variable		4,15
	set_value		5,5
	set_variable		6,14
	set_value		7,7
	set_variable		8,10
	enqueue_goal		8,normalize_guard_8_0
	put_func		2,3,=
	write_element_value		2,1,8
	write_element_variable		2,2,13
	put_list		11
	write_car_value		11,2
	write_cdr_nil		11
	put_value		2,3
	put_value		3,12
	put_value		5,15
	put_value		7,14
	put_value		8,9
	put_value		9,13
	execute		11,expand_expression_11_0
normalize_guard_becomes_9_3:
	check_vector		8,3,normalize_guard_becomes_9_1
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	get_vector_value		3,14
	create_goal		8
	set_variable		1,16
	set_value		2,2
	set_value		3,13
	set_variable		4,15
	set_value		5,5
	set_variable		6,14
	set_value		7,7
	set_variable		8,13
	enqueue_goal		8,normalize_guard_8_0
	put_reused_func		2,8,'$VAR'
	write_elements_inc		2,1,10,2
	put_func		3,3,=
	write_element_value		3,1,2
	write_element_variable		3,2,10
	put_list		11
	write_car_value		11,3
	write_cdr_nil		11
	put_value		2,16
	put_value		3,12
	put_value		5,15
	put_value		7,14
	put_values_inc		8,9,2
	put_value		10,13
	execute		11,expand_expression_11_0
normalize_guard_becomes_9_1:
	otherwise		normalize_guard_becomes_9_0
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,:=
	write_elements_inc		3,1,8,2
	put_structured_constant		4,'$SCNST_6'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_guard_becomes_9_8:
	suspend		normalize_guard_becomes_9_0
	module_entry		kl1cmp_normalize
	predicate		'$expand_expression/4_0',9
'$expand_expression/4_0_9_0':
	try_me_else		'$expand_expression/4_0_9_1'
	wait_atom		9,true
	collect_value		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
'$expand_expression/4_0_9_1':
	otherwise		'$expand_expression/4_0_9_0'
	collect_value		9
	put_nil		9
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_value		1,1,8
	put_list_val_val		2,1,9
	get_list_value		3,2
	proceed
'$expand_expression/4_0_9_6':
	suspend		'$expand_expression/4_0_9_0'
	module_entry		kl1cmp_normalize
	predicate		'$expand_expression/4_1',9
'$expand_expression/4_1_9_0':
	try_me_else		'$expand_expression/4_1_9_1'
	wait_atom		9,true
	collect_value		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
'$expand_expression/4_1_9_1':
	otherwise		'$expand_expression/4_1_9_0'
	collect_value		9
	put_nil		9
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_value		1,1,8
	put_list_val_val		2,1,9
	get_list_value		3,2
	proceed
'$expand_expression/4_1_9_6':
	suspend		'$expand_expression/4_1_9_0'
	module_entry		kl1cmp_normalize
	predicate		expand_expression,11
expand_expression_11_0:
	try_me_else		expand_expression_11_1
	wait		8
	switch_on_type		8,expand_expression_11_2,expand_expression_11_3,expand_expression_11_1,expand_expression_11_4,expand_expression_11_1,expand_expression_11_1
expand_expression_11_2:
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		8,9
	get_value		10,11
	proceed
expand_expression_11_3:
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		8,9
	get_value		10,11
	proceed
expand_expression_11_4:
	jump_on_arity		8,4,expand_expression_11_1
	table_entry		expand_expression_11_1
	table_entry		expand_expression_11_1
	table_entry		expand_expression_11_5
	table_entry		expand_expression_11_6
expand_expression_11_5:
	read_element		8,0,12
	wait_atom		12,int
	read_element		8,1,12
	put_reused_vector		14,8
	write_element_variable		14,0,13
	write_element_variable		14,1,8
	get_vector_value		3,14
	put_list		3
	write_car_marked_variable		3,14
	write_cdr_value		3,11
	create_goal		10
	set_variable		1,15
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_variable		8,5
	set_value		9,10
	set_value		10,3
	enqueue_goal		10,expand_float_expr_10_0
	create_goal		9
	set_variable		1,2
	set_value		2,15
	set_value		3,8
	set_value		4,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_marked_value		8,9
	set_value		9,14
	enqueue_goal		9,'$expand_expression/4_0_9_0'
	put_func		3,2,int
	write_element_value		3,1,12
	put_value		4,14
	put_value		6,9
	execute_external		kl1cmp_blttbl,expression,6
expand_expression_11_6:
	read_element		8,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		8,1,12,2
	integer		12
	string		13
	g_string		13,14,15
	wait_integer		15,8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_reused_func		1,8,'$VAR'
	write_elements_inc		1,1,12,2
	get_vector_value		9,1
	get_value		10,11
	proceed
expand_expression_11_1:
	otherwise		expand_expression_11_0
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	get_vector_value		3,14
	put_list		3
	write_car_marked_variable		3,14
	write_cdr_value		3,11
	create_goal		10
	set_variable		1,15
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_variable		8,5
	set_value		9,10
	set_value		10,3
	enqueue_goal		10,expand_expr_10_0
	create_goal		9
	set_variable		1,2
	set_value		2,15
	set_value		3,12
	set_value		4,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_marked_value		8,9
	set_value		9,14
	enqueue_goal		9,'$expand_expression/4_1_9_0'
	put_value		3,8
	put_value		4,14
	put_value		6,9
	execute_external		kl1cmp_blttbl,expression,6
expand_expression_11_8:
	suspend		expand_expression_11_0
	module_entry		kl1cmp_normalize
	predicate		expand_expr,10
expand_expr_10_0:
	try_me_else		expand_expr_10_1
	jump_on_non_list_var_var		8,expand_expr_10_3,11,14
	wait_list_var_var		14,12,13
	collect_list		8
	collect_list		14
	put_value		15,9
	put_vector		14,2
	write_element_variable		14,0,9
	write_element_variable		14,1,8
	get_vector_value		3,14
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,14
	set_value		5,5
	set_variable		6,9
	set_value		7,7
	set_value		8,13
	set_variable		9,13
	set_value		10,10
	enqueue_goal		10,expand_expr_10_0
	put_value		2,3
	put_value		3,8
	put_value		5,14
	put_value		7,9
	put_values_inc		8,11,2
	put_value		10,15
	put_value		11,13
	execute		11,expand_expression_11_0
expand_expr_10_3:
	check_nil		8,expand_expr_10_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		9,10
	proceed
expand_expr_10_1:
	suspend		expand_expr_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_float_becomes,9
normalize_guard_float_becomes_9_0:
	try_me_else		normalize_guard_float_becomes_9_1
	jump_on_non_integer		8,normalize_guard_float_becomes_9_3
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,12
	get_vector_value		3,11
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_variable		4,15
	set_value		5,5
	set_variable		6,14
	set_value		7,7
	set_variable		8,10
	enqueue_goal		8,normalize_guard_8_0
	put_func		2,3,=
	write_element_value		2,1,8
	write_element_variable		2,2,13
	put_list		11
	write_car_value		11,2
	write_cdr_nil		11
	put_value		2,3
	put_value		3,12
	put_value		5,15
	put_value		7,14
	put_value		8,9
	put_value		9,13
	execute		11,expand_float_expression_11_0
normalize_guard_float_becomes_9_3:
	check_vector		8,3,normalize_guard_float_becomes_9_1
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	get_vector_value		3,14
	create_goal		8
	set_variable		1,16
	set_value		2,2
	set_value		3,13
	set_variable		4,15
	set_value		5,5
	set_variable		6,14
	set_value		7,7
	set_variable		8,13
	enqueue_goal		8,normalize_guard_8_0
	put_reused_func		2,8,'$VAR'
	write_elements_inc		2,1,10,2
	put_func		3,3,=
	write_element_value		3,1,2
	write_element_variable		3,2,10
	put_list		11
	write_car_value		11,3
	write_cdr_nil		11
	put_value		2,16
	put_value		3,12
	put_value		5,15
	put_value		7,14
	put_values_inc		8,9,2
	put_value		10,13
	execute		11,expand_float_expression_11_0
normalize_guard_float_becomes_9_1:
	otherwise		normalize_guard_float_becomes_9_0
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,$:=
	write_elements_inc		3,1,8,2
	put_structured_constant		4,'$SCNST_7'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_guard_float_becomes_9_8:
	suspend		normalize_guard_float_becomes_9_0
	module_entry		kl1cmp_normalize
	predicate		'$expand_float_expression/4_2',9
'$expand_float_expression/4_2_9_0':
	try_me_else		'$expand_float_expression/4_2_9_1'
	wait_atom		9,true
	collect_value		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
'$expand_float_expression/4_2_9_1':
	otherwise		'$expand_float_expression/4_2_9_0'
	collect_value		9
	put_nil		9
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_value		1,1,8
	put_list_val_val		2,1,9
	get_list_value		3,2
	proceed
'$expand_float_expression/4_2_9_6':
	suspend		'$expand_float_expression/4_2_9_0'
	module_entry		kl1cmp_normalize
	predicate		'$expand_float_expression/4_3',9
'$expand_float_expression/4_3_9_0':
	try_me_else		'$expand_float_expression/4_3_9_1'
	wait_atom		9,true
	collect_value		8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
'$expand_float_expression/4_3_9_1':
	otherwise		'$expand_float_expression/4_3_9_0'
	collect_value		9
	put_nil		9
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_value		1,1,8
	put_list_val_val		2,1,9
	get_list_value		3,2
	proceed
'$expand_float_expression/4_3_9_6':
	suspend		'$expand_float_expression/4_3_9_0'
	module_entry		kl1cmp_normalize
	predicate		expand_float_expression,11
expand_float_expression_11_0:
	try_me_else		expand_float_expression_11_1
	jump_on_non_vector		8,expand_float_expression_11_3
	jump_on_arity		8,4,expand_float_expression_11_1
	table_entry		expand_float_expression_11_1
	table_entry		expand_float_expression_11_1
	table_entry		expand_float_expression_11_4
	table_entry		expand_float_expression_11_5
expand_float_expression_11_4:
	read_element		8,0,12
	wait_atom		12,float
	read_element		8,1,12
	put_reused_vector		14,8
	write_element_variable		14,0,13
	write_element_variable		14,1,8
	get_vector_value		3,14
	put_list		3
	write_car_marked_variable		3,14
	write_cdr_value		3,11
	create_goal		10
	set_variable		1,15
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_variable		8,5
	set_value		9,10
	set_value		10,3
	enqueue_goal		10,expand_expr_10_0
	create_goal		9
	set_variable		1,2
	set_value		2,15
	set_value		3,8
	set_value		4,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_marked_value		8,9
	set_value		9,14
	enqueue_goal		9,'$expand_float_expression/4_2_9_0'
	put_func		3,2,float
	write_element_value		3,1,12
	put_value		4,14
	put_value		6,9
	execute_external		kl1cmp_blttbl,float_expression,6
expand_float_expression_11_5:
	read_element		8,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		8,1,12,2
	integer		12
	string		13
	g_string		13,14,15
	wait_integer		15,8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_reused_func		1,8,'$VAR'
	write_elements_inc		1,1,12,2
	get_vector_value		9,1
	get_value		10,11
	proceed
expand_float_expression_11_3:
	is_float		8,expand_float_expression_11_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		8,9
	get_value		10,11
	proceed
expand_float_expression_11_1:
	otherwise		expand_float_expression_11_0
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	get_vector_value		3,14
	put_list		3
	write_car_marked_variable		3,14
	write_cdr_value		3,11
	create_goal		10
	set_variable		1,15
	set_value		2,2
	set_value		3,13
	set_variable		4,13
	set_value		5,5
	set_variable		6,11
	set_value		7,7
	set_variable		8,5
	set_value		9,10
	set_value		10,3
	enqueue_goal		10,expand_float_expr_10_0
	create_goal		9
	set_variable		1,2
	set_value		2,15
	set_value		3,12
	set_value		4,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_marked_value		8,9
	set_value		9,14
	enqueue_goal		9,'$expand_float_expression/4_3_9_0'
	put_value		3,8
	put_value		4,14
	put_value		6,9
	execute_external		kl1cmp_blttbl,float_expression,6
expand_float_expression_11_9:
	suspend		expand_float_expression_11_0
	module_entry		kl1cmp_normalize
	predicate		expand_float_expr,10
expand_float_expr_10_0:
	try_me_else		expand_float_expr_10_1
	jump_on_non_list_var_var		8,expand_float_expr_10_3,11,14
	wait_list_var_var		14,12,13
	collect_list		8
	collect_list		14
	put_value		15,9
	put_vector		14,2
	write_element_variable		14,0,9
	write_element_variable		14,1,8
	get_vector_value		3,14
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,14
	set_value		5,5
	set_variable		6,9
	set_value		7,7
	set_value		8,13
	set_variable		9,13
	set_value		10,10
	enqueue_goal		10,expand_float_expr_10_0
	put_value		2,3
	put_value		3,8
	put_value		5,14
	put_value		7,9
	put_values_inc		8,11,2
	put_value		10,15
	put_value		11,13
	execute		11,expand_float_expression_11_0
expand_float_expr_10_3:
	check_nil		8,expand_float_expr_10_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		9,10
	proceed
expand_float_expr_10_1:
	suspend		expand_float_expr_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_builtin,11
normalize_guard_builtin_11_0:
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	get_vector_value		3,14
	put_func		3,2,builtin
	write_element_value		3,1,8
	put_list_val_var		8,3,14
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_values_inc		3,13,2
	set_value		5,5
	set_variable		6,13
	set_value		7,7
	set_value		8,10
	enqueue_goal		8,normalize_builtin_args_8_0
	create_goal		5
	set_variable		1,2
	set_value		2,3
	set_variable		3,5
	set_value		4,8
	set_value		5,11
	enqueue_goal		5,concatenate_type_check_5_0
	put_value		3,12
	put_value		7,13
	put_value		8,9
	execute		8,normalize_builtin_args_8_0
normalize_guard_builtin_11_1:
	suspend		normalize_guard_builtin_11_0
	module_entry		kl1cmp_normalize
	predicate		concatenate_type_check,5
concatenate_type_check_5_0:
	try_me_else		concatenate_type_check_5_1
	list		5
	read_car		5,6
	wait_vector		6,2
	read_element		6,0,7
	atom		7
	hash_on_atom		7,5,concatenate_type_check_5_1
	bucket_entry_a		float,concatenate_type_check_5_5
	bucket_entry_a		integer,concatenate_type_check_5_6
	bucket_entry_a		string,concatenate_type_check_5_7
	bucket_entry_a		vector,concatenate_type_check_5_8
	bucket_entry_a		wait,concatenate_type_check_5_9
concatenate_type_check_5_5:
	read_element		6,1,8
	jump_on_non_vector		8,concatenate_type_check_5_11
	test_arity		8,3,concatenate_type_check_5_1
	read_cdr		5,9
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		7,8,'$VAR'
	write_elements_inc		7,1,10,2
	put_reused_func		6,6,float
	write_element_value		6,1,7
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_11:
	is_float		8,concatenate_type_check_5_1
	read_cdr		5,9
	put_reused_func		6,6,float
	write_element_value		6,1,8
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_6:
	read_element		6,1,8
	jump_on_non_integer		8,concatenate_type_check_5_13
	read_cdr		5,9
	put_reused_func		6,6,integer
	write_element_value		6,1,8
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_13:
	check_vector		8,3,concatenate_type_check_5_1
	read_cdr		5,9
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		7,8,'$VAR'
	write_elements_inc		7,1,10,2
	put_reused_func		6,6,integer
	write_element_value		6,1,7
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_7:
	read_element		6,1,8
	vector		8
	jump_on_arity		8,4,concatenate_type_check_5_1
	table_entry		concatenate_type_check_5_1
	table_entry		concatenate_type_check_5_1
	table_entry		concatenate_type_check_5_15
	table_entry		concatenate_type_check_5_16
concatenate_type_check_5_15:
	read_cdr		5,9
	read_element		8,0,10
	wait_atom		10,'$SCNST'
	read_element		8,1,7
	put_reused_func		6,6,'$SCNST'
	write_element_value		6,1,7
	put_reused_func		7,8,string
	write_element_value		7,1,6
	get_reused_list_val_var		3,6,5,7,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_16:
	read_cdr		5,9
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		7,8,'$VAR'
	write_elements_inc		7,1,10,2
	put_reused_func		6,6,string
	write_element_value		6,1,7
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,9
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_8:
	read_cdr		5,8
	read_element		6,1,12
	wait_vector		12,3
	read_element		12,0,9
	wait_atom		9,'$VAR'
	read_elements_inc		12,1,9,2
	integer		9
	string		10
	g_string		10,11,13
	wait_integer		13,8
	put_reused_func		7,12,'$VAR'
	write_elements_inc		7,1,9,2
	put_reused_func		6,6,vector
	write_element_value		6,1,7
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_9:
	read_cdr		5,8
	read_element		6,1,11
	wait_vector		11,3
	read_element		11,0,9
	wait_atom		9,'$VAR'
	read_elements_inc		11,1,9,2
	put_reused_func		7,11,'$VAR'
	write_elements_inc		7,1,9,2
	put_reused_func		6,6,wait
	write_element_value		6,1,7
	get_reused_list_val_var		3,7,5,6,5
	put_value		3,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_1:
	otherwise		concatenate_type_check_5_0
	try_me_else		concatenate_type_check_5_33
	jump_on_non_list		5,concatenate_type_check_5_35
	read_car		5,6
	wait_vector		6,2
	read_element		6,0,7
	atom		7
	hash_on_atom		7,5,concatenate_type_check_5_33
	bucket_entry_a		float,concatenate_type_check_5_38
	bucket_entry_a		integer,concatenate_type_check_5_39
	bucket_entry_a		string,concatenate_type_check_5_40
	bucket_entry_a		vector,concatenate_type_check_5_41
	bucket_entry_a		wait,concatenate_type_check_5_42
concatenate_type_check_5_38:
	read_cdr		5,8
	read_element		6,1,9
	collect_vector		6
	put_reused_list		5,5
	write_car_value		5,9
	write_cdr_nil		5
	put_structured_constant		6,'$SCNST_8'
	put_func		7,3,error_message
	write_elements_dec		7,1,6,2
	get_list_val_var		1,6,7,5
	put_value		1,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_39:
	read_cdr		5,8
	read_element		6,1,9
	collect_vector		6
	put_reused_list		5,5
	write_car_value		5,9
	write_cdr_nil		5
	put_structured_constant		6,'$SCNST_9'
	put_func		7,3,error_message
	write_elements_dec		7,1,6,2
	get_list_val_var		1,6,7,5
	put_value		1,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_40:
	read_cdr		5,8
	read_element		6,1,9
	collect_vector		6
	put_reused_list		5,5
	write_car_value		5,9
	write_cdr_nil		5
	put_structured_constant		6,'$SCNST_10'
	put_func		7,3,error_message
	write_elements_dec		7,1,6,2
	get_list_val_var		1,6,7,5
	put_value		1,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_41:
	read_cdr		5,8
	read_element		6,1,9
	collect_vector		6
	put_reused_list		5,5
	write_car_value		5,9
	write_cdr_nil		5
	put_structured_constant		6,'$SCNST_11'
	put_func		7,3,error_message
	write_elements_dec		7,1,6,2
	get_list_val_var		1,6,7,5
	put_value		1,5
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_42:
	read_cdr		5,8
	read_element		6,1,9
	collect_list		5
	collect_value		9
	collect_vector		6
	put_value		5,8
	execute		5,concatenate_type_check_5_0
concatenate_type_check_5_35:
	check_nil		5,concatenate_type_check_5_33
	get_value		3,4
	get_value		1,2
	proceed
concatenate_type_check_5_33:
	suspend		concatenate_type_check_5_0
	module_entry		kl1cmp_normalize
	predicate		concatenate,5
concatenate_5_0:
	try_me_else		concatenate_5_1
	jump_on_non_list_var_var		5,concatenate_5_3,6,7
	get_reused_list_val_var		3,8,5,6,5
	put_value		3,5
	put_value		5,7
	execute		5,concatenate_5_0
concatenate_5_3:
	check_nil		5,concatenate_5_1
	get_value		3,4
	get_value		1,2
	proceed
concatenate_5_1:
	suspend		concatenate_5_0
	module_entry		kl1cmp_normalize
	predicate		normalize_builtin_args,8
normalize_builtin_args_8_0:
	try_me_else		normalize_builtin_args_8_1
	jump_on_non_list_var_var		8,normalize_builtin_args_8_3,9,12
	wait_list_var_var		12,10,11
	collect_list		12
	put_vector		12,2
	write_element_variable		12,0,15
	write_element_variable		12,1,14
	put_func		13,2,new_variable
	write_element_marked_value		13,1,10
	put_reused_list_val_val		8,8,13,12
	get_list_value		3,8
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,15
	set_variable		4,12
	set_value		5,5
	set_variable		6,8
	set_value		7,7
	set_value		8,11
	enqueue_goal		8,normalize_builtin_args_8_0
	put_value		2,3
	put_value		3,14
	put_value		5,12
	put_values_inc		7,8,3
	execute		9,normalize_guard_unify_9_0
normalize_builtin_args_8_3:
	check_nil		8,normalize_builtin_args_8_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_builtin_args_8_1:
	suspend		normalize_builtin_args_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_not_unify,9
normalize_guard_not_unify_9_0:
	try_me_else		normalize_guard_not_unify_9_1
	wait_vector		8,3
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		12,8,'$VAR'
	write_elements_inc		12,1,10,2
	put_value		8,9
	put_value		9,12
	execute		9,normalize_guard_not_unify_variable_9_0
normalize_guard_not_unify_9_1:
	try_me_else		normalize_guard_not_unify_9_3
	wait_vector		9,3
	read_element		9,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		9,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_reused_func		9,9,'$VAR'
	write_elements_inc		9,1,10,2
	execute		9,normalize_guard_not_unify_variable_9_0
normalize_guard_not_unify_9_3:
	otherwise		normalize_guard_not_unify_9_0
	collect_value		9
	put_value		9,8
	put_marked_value		8,9
	execute		9,normalize_not_unify_atomic_atomic_9_0
normalize_guard_not_unify_9_10:
	suspend		normalize_guard_not_unify_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_guard_not_unify_variable,9
normalize_guard_not_unify_variable_9_0:
	try_me_else		normalize_guard_not_unify_variable_9_1
	vector		8
	jump_on_arity		8,4,normalize_guard_not_unify_variable_9_1
	table_entry		normalize_guard_not_unify_variable_9_1
	table_entry		normalize_guard_not_unify_variable_9_1
	table_entry		normalize_guard_not_unify_variable_9_3
	table_entry		normalize_guard_not_unify_variable_9_4
normalize_guard_not_unify_variable_9_3:
	read_element		8,0,10
	wait_atom		10,'$SCNST'
	read_element		8,1,10
	string		10
	put_nil		11
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,11
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		8,1,2
	get_list_value		3,8
	put_func		1,3,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_marked_value		2,1,10
	put_func		3,3,=
	write_element_value		3,1,7
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,10
	put_list_val_val		3,1,2
	put_func		1,2,var
	write_element_marked_value		1,1,9
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_func		2,2,wait
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_4:
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	put_nil		12
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,12
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		12,1,2
	get_list_value		3,12
	put_reused_func		1,8,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,3,'$VAR'
	write_element_marked_value		2,1,10
	write_element_marked_value		2,2,11
	put_func		3,2,var
	write_element_value		3,1,2
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,3
	put_list_val_val		3,2,1
	put_func		1,3,'$VAR'
	write_elements_inc		1,1,10,2
	put_func		2,2,wait
	write_element_value		2,1,1
	put_list_val_val		1,2,3
	put_func		2,2,var
	write_element_marked_value		2,1,9
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,9
	put_list_val_val		3,1,2
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_1:
	otherwise		normalize_guard_not_unify_variable_9_0
	try_me_else		normalize_guard_not_unify_variable_9_7
	wait		8
	switch_on_type		8,normalize_guard_not_unify_variable_9_8,normalize_guard_not_unify_variable_9_9,normalize_guard_not_unify_variable_9_7,normalize_guard_not_unify_variable_9_7,normalize_guard_not_unify_variable_9_10,normalize_guard_not_unify_variable_9_11
normalize_guard_not_unify_variable_9_8:
	put_nil		10
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,10
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		10,1,2
	get_list_value		3,10
	put_func		1,3,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,atomic
	write_element_marked_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,7
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,8
	put_list_val_val		3,1,2
	put_func		1,2,var
	write_element_marked_value		1,1,9
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_func		2,2,wait
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_9:
	put_nil		10
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,10
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		10,1,2
	get_list_value		3,10
	put_func		1,3,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,atomic
	write_element_marked_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,7
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,8
	put_list_val_val		3,1,2
	put_func		1,2,var
	write_element_marked_value		1,1,9
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_func		2,2,wait
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_10:
	put_nil		10
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,10
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		10,1,2
	get_list_value		3,10
	put_func		1,3,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,atomic
	write_element_marked_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,7
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,8
	put_list_val_val		3,1,2
	put_func		1,2,var
	write_element_marked_value		1,1,9
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_func		2,2,wait
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_11:
	is_float		8,normalize_guard_not_unify_variable_9_7
	put_nil		10
	get_value		6,7
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,10
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,7
	put_list_val_val		10,1,2
	get_list_value		3,10
	put_func		1,3,diff
	write_elements_inc		1,1,6,2
	put_func		2,2,builtin
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,atomic
	write_element_marked_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,7
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	put_func		1,2,wait
	write_element_value		1,1,8
	put_list_val_val		3,1,2
	put_func		1,2,var
	write_element_marked_value		1,1,9
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_func		2,2,wait
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	get_list_value		4,3
	proceed
normalize_guard_not_unify_variable_9_7:
	otherwise		normalize_guard_not_unify_variable_9_0
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,\=
	write_elements_dec		3,1,9,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_12'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_guard_not_unify_variable_9_14:
	suspend		normalize_guard_not_unify_variable_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_not_unify_atomic_atomic,9
normalize_not_unify_atomic_atomic_9_0:
	try_me_else		normalize_not_unify_atomic_atomic_9_1
	wait_value		8,9
	collect_value		9
	get_nil		3
	get_value		6,7
	put_func		3,3,\=
	write_element_marked_value		3,1,8
	write_element_value		3,2,8
	put_list		6
	write_car_value		6,3
	write_cdr_nil		6
	put_structured_constant		3,'$SCNST_13'
	put_func		7,3,warning_message
	write_element_value		7,1,3
	write_element_value		7,2,6
	put_list_val_val		3,7,2
	get_list_value		1,3
	put_structured_constant		1,'$SCNST_14'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_not_unify_atomic_atomic_9_1:
	otherwise		normalize_not_unify_atomic_atomic_9_0
	try_me_else		normalize_not_unify_atomic_atomic_9_3
	atom		8
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_3:
	try_me_else		normalize_not_unify_atomic_atomic_9_5
	atom		9
	put_value		10,8
	put_values_inc		8,9,2
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_5:
	otherwise		normalize_not_unify_atomic_atomic_9_0
	try_me_else		normalize_not_unify_atomic_atomic_9_10
	integer		8
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_10:
	try_me_else		normalize_not_unify_atomic_atomic_9_12
	integer		9
	put_value		10,8
	put_values_inc		8,9,2
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_12:
	otherwise		normalize_not_unify_atomic_atomic_9_0
	try_me_else		normalize_not_unify_atomic_atomic_9_17
	float		8
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_17:
	try_me_else		normalize_not_unify_atomic_atomic_9_19
	float		9
	put_value		10,8
	put_values_inc		8,9,2
	execute		9,normalize_not_unify_success_9_0
normalize_not_unify_atomic_atomic_9_19:
	otherwise		normalize_not_unify_atomic_atomic_9_0
	get_nil		3
	get_value		6,7
	put_func		3,3,\=
	write_elements_inc		3,1,8,2
	put_list		6
	write_car_value		6,3
	write_cdr_nil		6
	put_structured_constant		3,'$SCNST_15'
	put_func		7,3,error_message
	write_element_value		7,1,3
	write_element_value		7,2,6
	put_list_val_val		3,7,2
	get_list_value		1,3
	put_structured_constant		1,'$SCNST_16'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_not_unify_atomic_atomic_9_24:
	suspend		normalize_not_unify_atomic_atomic_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_not_unify_success,9
normalize_not_unify_success_9_0:
	get_nil		3
	get_value		6,7
	get_value		4,5
	put_func		3,3,\=
	write_elements_inc		3,1,8,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_17'
	put_func		5,3,warning_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_not_unify_success_9_1:
	suspend		normalize_not_unify_success_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_unify_structure_arg,9
normalize_unify_structure_arg_9_0:
	try_me_else		normalize_unify_structure_arg_9_1
	vector		8
	jump_on_arity		8,4,normalize_unify_structure_arg_9_1
	table_entry		normalize_unify_structure_arg_9_1
	table_entry		normalize_unify_structure_arg_9_1
	table_entry		normalize_unify_structure_arg_9_3
	table_entry		normalize_unify_structure_arg_9_4
normalize_unify_structure_arg_9_3:
	read_element		8,0,10
	wait_atom		10,'$SCNCT'
	read_element		8,1,10
	string		10
	g_string		10,11,12
	put_nil		11
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,11
	get_list_value		3,2
	put_func		1,2,var
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_value		2,1,10
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_unify_structure_arg_9_4:
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,var
	write_element_value		1,1,9
	put_reused_func		2,8,'$VAR'
	write_elements_inc		2,1,10,2
	put_func		3,3,=
	write_elements_dec		3,1,2,2
	put_list_val_val		1,3,5
	get_list_value		4,1
	proceed
normalize_unify_structure_arg_9_1:
	otherwise		normalize_unify_structure_arg_9_0
	try_me_else		normalize_unify_structure_arg_9_7
	wait		8
	switch_on_type		8,normalize_unify_structure_arg_9_8,normalize_unify_structure_arg_9_9,normalize_unify_structure_arg_9_10,normalize_unify_structure_arg_9_11,normalize_unify_structure_arg_9_7,normalize_unify_structure_arg_9_12
normalize_unify_structure_arg_9_10:
	read_car		8,10
	read_cdr		8,11
	get_value		6,7
	put_reused_list_val_val		6,8,10,11
	put_value		7,9
	execute		7,normalize_body_list_7_0
normalize_unify_structure_arg_9_8:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_unify_structure_arg_9_9:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_unify_structure_arg_9_11:
	g_vector		8,10
	get_value		6,7
	put_values_inc		6,8,3
	execute		8,normalize_body_vector_8_0
normalize_unify_structure_arg_9_12:
	is_float		8,normalize_unify_structure_arg_9_7
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,3,=
	write_element_value		2,1,9
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_unify_structure_arg_9_7:
	suspend		normalize_unify_structure_arg_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body,8
normalize_body_8_0:
	try_me_else		normalize_body_8_1
	integer		6
	jump_on_integer		6,2,normalize_body_8_1
	table_entry		normalize_body_8_3
	table_entry		normalize_body_8_4
normalize_body_8_3:
	put_vector		11,3
	write_element_variable		11,0,10
	write_element_variable		11,1,9
	write_element_variable		11,2,6
	get_vector_value		3,11
	create_goal		6
	set_variable		1,13
	set_value		2,2
	set_value		3,10
	set_variable		4,10
	set_value		5,5
	set_variable		6,3
	enqueue_goal		6,normalize_user_body_6_0
	create_goal		4
	set_variable		1,2
	set_value		2,10
	set_variable		3,11
	set_variable		4,10
	enqueue_goal		4,'C_4_0'
	create_goal		6
	set_variable		1,12
	set_value		2,13
	set_value		3,9
	set_variable		4,5
	set_value		5,2
	set_variable		6,9
	enqueue_goal		6,normalize_body_builtin_6_0
	create_goal		10
	set_variable		1,2
	set_value		2,12
	set_value		3,6
	set_values_dec		4,11,3
	set_nil		7
	set_nil		8
	set_value		9,3
	set_value		10,8
	enqueue_goal		10,classify_body_10_0
	put_values_inc		3,4,2
	put_value		5,7
	execute		5,concatenate_5_0
normalize_body_8_4:
	put_values_inc		6,7,2
	execute		7,normalize_body_one_by_one_7_0
normalize_body_8_1:
	suspend		normalize_body_8_0
	module_entry		kl1cmp_normalize
	predicate		classify_body,10
classify_body_10_0:
	try_me_else		classify_body_10_1
	jump_on_non_list_var_var		10,classify_body_10_3,11,12
	collect_list		10
	put_vector		14,2
	write_element_variable		14,0,13
	write_element_variable		14,1,10
	get_vector_value		3,14
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_value		3,13
	set_variable		4,15
	set_value		5,5
	set_variable		6,14
	set_value		7,7
	set_variable		8,13
	set_value		9,9
	set_value		10,12
	enqueue_goal		10,classify_body_10_0
	put_value		2,3
	put_value		3,10
	put_value		5,15
	put_value		7,14
	put_value		9,13
	put_value		10,11
	execute		10,classify_one_goal_10_0
classify_body_10_3:
	check_nil		10,classify_body_10_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	get_value		8,9
	proceed
classify_body_10_1:
	suspend		classify_body_10_0
	module_entry		kl1cmp_normalize
	predicate		classify_one_goal,10
classify_one_goal_10_0:
	try_me_else		classify_one_goal_10_1
	jump_on_non_atom		10,classify_one_goal_10_3
	test_atom		10,true,classify_one_goal_10_1
	get_nil		3
	get_value		8,9
	get_value		4,5
	get_value		1,2
	put_list		1
	write_car_atom		1,true
	write_cdr_value		1,7
	get_list_value		6,1
	proceed
classify_one_goal_10_3:
	check_vector		10,3,classify_one_goal_10_1
	read_element		10,0,11
	atom		11
	hash_on_atom		11,6,classify_one_goal_10_1
	bucket_entry_a		$:=,classify_one_goal_10_5
	bucket_entry_a		:,classify_one_goal_10_6
	bucket_entry_a		:=,classify_one_goal_10_7
	bucket_entry_a		=,classify_one_goal_10_8
	bucket_entry_a		==,classify_one_goal_10_9
	bucket_entry_a		@,classify_one_goal_10_10
classify_one_goal_10_5:
	read_elements_inc		10,1,12,2
	get_nil		3
	get_value		8,9
	get_value		4,5
	get_value		1,2
	put_reused_func		1,10,$:=
	write_elements_inc		1,1,12,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
classify_one_goal_10_6:
	read_element		10,1,12
	read_element		10,2,16
	wait_vector		16,3
	read_element		16,0,13
	wait_atom		13,@
	read_elements_inc		16,1,13,2
	put_vector		17,2
	write_element_variable		17,0,15
	write_element_variable		17,1,11
	get_vector_value		3,17
	create_goal		3
	set_values_inc		1,8,2
	put_reused_func		3,10,@
	write_element_value		3,1,13
	write_element_variable		3,2,9
	put_reused_func		8,16,:
	write_element_value		8,1,12
	write_element_value		8,2,3
	set_value		3,8
	enqueue_goal		3,stack_3_0
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,15
	set_values_inc		4,4,2
	set_variable		6,8
	enqueue_goal		6,normalize_body_builtin_for_pragma_6_0
	put_value		2,3
	put_value		3,11
	put_values_inc		4,6,2
	put_value		6,14
	put_value		7,9
	put_nil		9
	execute		9,normalize_pragma_9_0
classify_one_goal_10_7:
	read_elements_inc		10,1,12,2
	get_nil		3
	get_value		8,9
	get_value		4,5
	get_value		1,2
	put_reused_func		1,10,:=
	write_elements_inc		1,1,12,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
classify_one_goal_10_8:
	read_elements_inc		10,1,12,2
	get_nil		3
	get_value		8,9
	get_value		4,5
	get_value		1,2
	put_reused_func		1,10,=
	write_elements_inc		1,1,12,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
classify_one_goal_10_9:
	read_elements_inc		10,1,12,2
	get_nil		3
	get_value		8,9
	get_value		4,5
	get_value		1,2
	put_reused_func		1,10,==
	write_elements_inc		1,1,12,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
classify_one_goal_10_10:
	read_elements_inc		10,1,12,2
	put_vector		15,2
	write_element_variable		15,0,14
	write_element_variable		15,1,11
	get_vector_value		3,15
	create_goal		3
	set_values_inc		1,8,2
	put_reused_func		3,10,@
	write_element_value		3,1,12
	write_element_variable		3,2,9
	set_value		3,3
	enqueue_goal		3,stack_3_0
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,14
	set_values_inc		4,4,2
	set_variable		6,8
	enqueue_goal		6,normalize_body_builtin_for_pragma_6_0
	put_value		2,3
	put_value		3,11
	put_values_inc		4,6,2
	put_value		6,13
	put_value		7,9
	put_nil		9
	execute		9,normalize_pragma_9_0
classify_one_goal_10_1:
	otherwise		classify_one_goal_10_0
	get_nil		3
	get_value		4,5
	get_value		1,2
	create_goal		6
	set_values_inc		1,6,4
	set_variable		5,5
	set_marked_value		6,10
	enqueue_goal		6,classify_one_goal_on_type_6_0
	put_value		1,10
	put_void		2
	put_void		3
	put_void		4
	execute_external		kl1cmp_blttbl,active_builtin,5
classify_one_goal_10_18:
	suspend		classify_one_goal_10_0
	module_entry		kl1cmp_normalize
	predicate		stack,3
stack_3_0:
	put_list_val_val		4,3,1
	get_list_value		2,4
	proceed
stack_3_1:
	suspend		stack_3_0
	module_entry		kl1cmp_normalize
	predicate		classify_one_goal_on_type,6
classify_one_goal_on_type_6_0:
	try_me_else		classify_one_goal_on_type_6_1
	atom		5
	branch_on_atom		5,2,classify_one_goal_on_type_6_1
	bucket_entry_a		builtin,classify_one_goal_on_type_6_3
	bucket_entry_a		none,classify_one_goal_on_type_6_4
classify_one_goal_on_type_6_3:
	put_list_val_val		5,6,2
	get_list_value		1,5
	get_value		3,4
	proceed
classify_one_goal_on_type_6_4:
	get_value		1,2
	put_list_val_val		1,6,3
	get_list_value		4,1
	proceed
classify_one_goal_on_type_6_1:
	suspend		classify_one_goal_on_type_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_builtin,6
normalize_body_builtin_6_0:
	try_me_else		normalize_body_builtin_6_1
	jump_on_non_list_var_var		6,normalize_body_builtin_6_3,7,8
	collect_list		6
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,9
	set_value		5,5
	set_value		6,8
	enqueue_goal		6,normalize_body_builtin_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,9
	put_value		6,7
	execute		6,normalize_one_body_builtin_6_0
normalize_body_builtin_6_3:
	check_nil		6,normalize_body_builtin_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_body_builtin_6_1:
	suspend		normalize_body_builtin_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_one_body_builtin,6
normalize_one_body_builtin_6_0:
	try_me_else		normalize_one_body_builtin_6_1
	jump_on_non_atom		6,normalize_one_body_builtin_6_3
	test_atom		6,true,normalize_one_body_builtin_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_one_body_builtin_6_3:
	check_vector		6,3,normalize_one_body_builtin_6_1
	read_element		6,0,7
	atom		7
	hash_on_atom		7,4,normalize_one_body_builtin_6_1
	bucket_entry_a		$:=,normalize_one_body_builtin_6_5
	bucket_entry_a		:=,normalize_one_body_builtin_6_6
	bucket_entry_a		=,normalize_one_body_builtin_6_7
	bucket_entry_a		==,normalize_one_body_builtin_6_8
normalize_one_body_builtin_6_5:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_values_inc		6,8,2
	execute		7,normalize_body_float_becomes_7_0
normalize_one_body_builtin_6_6:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_values_inc		6,8,2
	execute		7,normalize_body_becomes_7_0
normalize_one_body_builtin_6_7:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_values_inc		6,8,2
	execute		7,normalize_body_unify_7_0
normalize_one_body_builtin_6_8:
	read_elements_inc		6,1,8,2
	get_nil		3
	get_value		1,2
	put_reused_func		1,6,==
	write_elements_inc		1,1,8,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_one_body_builtin_6_1:
	otherwise		normalize_one_body_builtin_6_0
	put_vector		7,2
	write_element_variable		7,0,9
	write_element_variable		7,1,8
	get_vector_value		3,7
	put_func		3,2,blt
	write_element_variable		3,1,10
	put_list_val_var		7,3,11
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_value		4,11
	set_value		5,5
	set_variable		6,5
	enqueue_goal		6,normalize_body_args_6_0
	create_goal		6
	set_value		1,1
	set_value		2,3
	set_value		3,8
	set_value		4,4
	set_value		5,7
	set_variable		6,3
	enqueue_goal		6,normalize_body_args_6_0
	put_value		1,6
	put_value		2,10
	put_value		4,5
	put_void		5
	execute_external		kl1cmp_blttbl,active_builtin,5
normalize_one_body_builtin_6_16:
	suspend		normalize_one_body_builtin_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_builtin_for_pragma,6
normalize_body_builtin_for_pragma_6_0:
	try_me_else		normalize_body_builtin_for_pragma_6_1
	jump_on_non_list_var_var		6,normalize_body_builtin_for_pragma_6_3,7,8
	collect_list		6
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,9
	set_value		5,5
	set_value		6,8
	enqueue_goal		6,normalize_body_builtin_for_pragma_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,9
	put_value		6,7
	execute		6,normalize_one_body_builtin_6_0
normalize_body_builtin_for_pragma_6_3:
	check_nil		6,normalize_body_builtin_for_pragma_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_body_builtin_for_pragma_6_1:
	suspend		normalize_body_builtin_for_pragma_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_becomes,7
normalize_body_becomes_7_0:
	try_me_else		normalize_body_becomes_7_1
	jump_on_non_integer		6,normalize_body_becomes_7_3
	put_value		9,6
	put_vector		10,2
	write_element_variable		10,0,8
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,8
	set_variable		4,10
	set_value		5,5
	set_variable		6,8
	enqueue_goal		6,normalize_body_builtin_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,10
	put_value		6,7
	put_value		7,9
	put_nil		9
	execute		9,expand_body_expression_9_0
normalize_body_becomes_7_3:
	check_vector		6,3,normalize_body_becomes_7_1
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_vector		12,2
	write_element_variable		12,0,10
	write_element_variable		12,1,11
	get_vector_value		3,12
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_variable		4,13
	set_value		5,5
	set_variable		6,12
	enqueue_goal		6,normalize_body_builtin_6_0
	put_reused_func		10,6,'$VAR'
	write_elements_inc		10,1,8,2
	put_value		2,3
	put_value		3,11
	put_value		5,13
	put_value		6,7
	put_value		7,10
	put_value		8,12
	put_nil		9
	execute		9,expand_body_expression_9_0
normalize_body_becomes_7_1:
	otherwise		normalize_body_becomes_7_0
	get_nil		3
	get_value		4,5
	put_func		3,3,:=
	write_elements_inc		3,1,6,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_18'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_body_becomes_7_8:
	suspend		normalize_body_becomes_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_flot_becomes,7
normalize_body_flot_becomes_7_0:
	try_me_else		normalize_body_flot_becomes_7_1
	jump_on_non_integer		6,normalize_body_flot_becomes_7_3
	put_value		9,6
	put_vector		10,2
	write_element_variable		10,0,8
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,8
	set_variable		4,10
	set_value		5,5
	set_variable		6,8
	enqueue_goal		6,normalize_body_builtin_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,10
	put_value		6,7
	put_value		7,9
	put_nil		9
	execute		9,expand_body_float_expression_9_0
normalize_body_flot_becomes_7_3:
	check_vector		6,3,normalize_body_flot_becomes_7_1
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_vector		12,2
	write_element_variable		12,0,10
	write_element_variable		12,1,11
	get_vector_value		3,12
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_variable		4,13
	set_value		5,5
	set_variable		6,12
	enqueue_goal		6,normalize_body_builtin_6_0
	put_reused_func		10,6,'$VAR'
	write_elements_inc		10,1,8,2
	put_value		2,3
	put_value		3,11
	put_value		5,13
	put_value		6,7
	put_value		7,10
	put_value		8,12
	put_nil		9
	execute		9,expand_body_float_expression_9_0
normalize_body_flot_becomes_7_1:
	otherwise		normalize_body_flot_becomes_7_0
	suspend		normalize_body_flot_becomes_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_float_becomes,7
normalize_body_float_becomes_7_0:
	get_nil		3
	get_value		4,5
	put_func		3,3,$:=
	write_elements_inc		3,1,6,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_19'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_body_float_becomes_7_1:
	suspend		normalize_body_float_becomes_7_0
	module_entry		kl1cmp_normalize
	predicate		expand_body_expression,9
expand_body_expression_9_0:
	try_me_else		expand_body_expression_9_1
	jump_on_non_integer		6,expand_body_expression_9_3
	get_nil		3
	get_value		4,5
	get_value		1,2
	put_func		1,3,=
	write_elements_dec		1,1,7,2
	put_list_val_val		2,1,9
	get_list_value		8,2
	proceed
expand_body_expression_9_3:
	is_vector		6,expand_body_expression_9_1
	jump_on_arity		6,4,expand_body_expression_9_1
	table_entry		expand_body_expression_9_1
	table_entry		expand_body_expression_9_1
	table_entry		expand_body_expression_9_4
	table_entry		expand_body_expression_9_5
expand_body_expression_9_4:
	read_element		6,0,10
	wait_atom		10,int
	read_element		6,1,10
	put_reused_func		6,6,new_variable
	write_element_marked_variable		6,1,11
	get_list_val_var		3,12,6,6
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,6
	set_values_inc		4,4,2
	set_variable		6,5
	set_value		7,8
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,11
	put_list_val_val		3,2,9
	put_list		2
	write_car_variable		2,4
	write_cdr_value		2,3
	set_value		8,2
	enqueue_goal		8,expand_body_float_expr_8_0
	put_value		2,12
	put_value		3,10
	put_value		6,11
	execute_external		kl1cmp_blttbl,expression,6
expand_body_expression_9_5:
	read_element		6,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		6,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	get_nil		3
	get_value		4,5
	get_value		1,2
	put_reused_func		1,6,'$VAR'
	write_elements_inc		1,1,10,2
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,9
	get_list_value		8,1
	proceed
expand_body_expression_9_1:
	otherwise		expand_body_expression_9_0
	put_func		10,2,new_variable
	write_element_marked_variable		10,1,11
	get_list_val_var		3,12,10,10
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,10
	set_values_inc		4,4,2
	set_variable		6,5
	set_value		7,8
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,11
	put_list_val_val		3,2,9
	put_list		2
	write_car_variable		2,4
	write_cdr_value		2,3
	set_value		8,2
	enqueue_goal		8,expand_body_expr_8_0
	put_value		2,12
	put_value		3,6
	put_value		6,11
	execute_external		kl1cmp_blttbl,expression,6
expand_body_expression_9_9:
	suspend		expand_body_expression_9_0
	module_entry		kl1cmp_normalize
	predicate		expand_body_expr,8
expand_body_expr_8_0:
	try_me_else		expand_body_expr_8_1
	jump_on_non_list_var_var		6,expand_body_expr_8_3,9,12
	wait_list_var_var		12,10,11
	collect_list		12
	put_value		15,7
	put_vector		7,2
	write_element_variable		7,0,14
	write_element_variable		7,1,13
	put_func		12,2,new_variable
	write_element_marked_value		12,1,10
	put_reused_list_val_val		6,6,12,7
	get_list_value		3,6
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,14
	set_variable		4,6
	set_value		5,5
	set_value		6,11
	set_variable		7,11
	set_value		8,8
	enqueue_goal		8,expand_body_expr_8_0
	put_value		2,3
	put_value		3,13
	put_value		5,6
	put_values_inc		6,9,2
	put_value		8,15
	put_value		9,11
	execute		9,expand_body_expression_9_0
expand_body_expr_8_3:
	check_nil		6,expand_body_expr_8_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	get_value		7,8
	proceed
expand_body_expr_8_1:
	suspend		expand_body_expr_8_0
	module_entry		kl1cmp_normalize
	predicate		expand_body_float_expression,9
expand_body_float_expression_9_0:
	try_me_else		expand_body_float_expression_9_1
	jump_on_non_vector		6,expand_body_float_expression_9_3
	jump_on_arity		6,4,expand_body_float_expression_9_1
	table_entry		expand_body_float_expression_9_1
	table_entry		expand_body_float_expression_9_1
	table_entry		expand_body_float_expression_9_4
	table_entry		expand_body_float_expression_9_5
expand_body_float_expression_9_4:
	read_element		6,0,10
	wait_atom		10,float
	read_element		6,1,10
	put_reused_func		6,6,new_variable
	write_element_marked_variable		6,1,11
	get_list_val_var		3,12,6,6
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,6
	set_values_inc		4,4,2
	set_variable		6,5
	set_value		7,8
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,11
	put_list_val_val		3,2,9
	put_list		2
	write_car_variable		2,4
	write_cdr_value		2,3
	set_value		8,2
	enqueue_goal		8,expand_body_expr_8_0
	put_func		3,2,float
	write_element_value		3,1,10
	put_value		2,12
	put_value		6,11
	execute_external		kl1cmp_blttbl,float_expression,6
expand_body_float_expression_9_5:
	read_element		6,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		6,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	get_nil		3
	get_value		4,5
	get_value		1,2
	put_reused_func		1,6,'$VAR'
	write_elements_inc		1,1,10,2
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,9
	get_list_value		8,1
	proceed
expand_body_float_expression_9_3:
	is_float		6,expand_body_float_expression_9_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	put_func		1,3,=
	write_elements_dec		1,1,7,2
	put_list_val_val		2,1,9
	get_list_value		8,2
	proceed
expand_body_float_expression_9_1:
	otherwise		expand_body_float_expression_9_0
	put_func		10,2,new_variable
	write_element_marked_variable		10,1,11
	get_list_val_var		3,12,10,10
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,10
	set_values_inc		4,4,2
	set_variable		6,5
	set_value		7,8
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,11
	put_list_val_val		3,2,9
	put_list		2
	write_car_variable		2,4
	write_cdr_value		2,3
	set_value		8,2
	enqueue_goal		8,expand_body_float_expr_8_0
	put_value		2,12
	put_value		3,6
	put_value		6,11
	execute_external		kl1cmp_blttbl,float_expression,6
expand_body_float_expression_9_9:
	suspend		expand_body_float_expression_9_0
	module_entry		kl1cmp_normalize
	predicate		expand_body_float_expr,8
expand_body_float_expr_8_0:
	try_me_else		expand_body_float_expr_8_1
	jump_on_non_list_var_var		6,expand_body_float_expr_8_3,9,12
	wait_list_var_var		12,10,11
	collect_list		12
	put_value		15,7
	put_vector		7,2
	write_element_variable		7,0,14
	write_element_variable		7,1,13
	put_func		12,2,new_variable
	write_element_marked_value		12,1,10
	put_reused_list_val_val		6,6,12,7
	get_list_value		3,6
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,14
	set_variable		4,6
	set_value		5,5
	set_value		6,11
	set_variable		7,11
	set_value		8,8
	enqueue_goal		8,expand_body_float_expr_8_0
	put_value		2,3
	put_value		3,13
	put_value		5,6
	put_values_inc		6,9,2
	put_value		8,15
	put_value		9,11
	execute		9,expand_body_float_expression_9_0
expand_body_float_expr_8_3:
	check_nil		6,expand_body_float_expr_8_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	get_value		7,8
	proceed
expand_body_float_expr_8_1:
	suspend		expand_body_float_expr_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_pragma,9
normalize_pragma_9_0:
	put_vector		12,2
	write_element_variable		12,0,11
	write_element_variable		12,1,10
	get_vector_value		3,12
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_value		3,11
	set_variable		4,13
	set_value		5,5
	set_variable		6,12
	set_variable		7,11
	set_values_inc		8,7,3
	enqueue_goal		10,classify_pragma_10_0
	put_value		2,3
	put_value		3,10
	put_value		5,13
	put_values_dec		7,12,2
	execute		8,take_apart_priority_and_alloc_8_0
normalize_pragma_9_1:
	suspend		normalize_pragma_9_0
	module_entry		kl1cmp_normalize
	predicate		take_apart_priority_and_alloc,8
take_apart_priority_and_alloc_8_0:
	try_me_else		take_apart_priority_and_alloc_8_1
	vector		6
	jump_on_arity		6,4,take_apart_priority_and_alloc_8_1
	table_entry		take_apart_priority_and_alloc_8_1
	table_entry		take_apart_priority_and_alloc_8_1
	table_entry		take_apart_priority_and_alloc_8_3
	table_entry		take_apart_priority_and_alloc_8_4
take_apart_priority_and_alloc_8_3:
	read_element		6,0,9
	atom		9
	branch_on_atom		9,2,take_apart_priority_and_alloc_8_1
	bucket_entry_a		node,take_apart_priority_and_alloc_8_6
	bucket_entry_a		processor,take_apart_priority_and_alloc_8_7
take_apart_priority_and_alloc_8_6:
	read_element		6,1,10
	get_nil		3
	get_value		4,5
	get_value		1,2
	get_nil		7
	put_reused_func		1,6,node
	write_element_value		1,1,10
	get_vector_value		8,1
	proceed
take_apart_priority_and_alloc_8_7:
	read_element		6,1,10
	get_nil		3
	get_value		4,5
	get_value		1,2
	get_nil		7
	put_reused_func		1,6,processor
	write_element_value		1,1,10
	get_vector_value		8,1
	proceed
take_apart_priority_and_alloc_8_4:
	read_element		6,0,9
	wait_atom		9,priority
	read_elements_inc		6,1,9,2
	get_nil		3
	get_value		4,5
	get_value		1,2
	put_reused_func		1,6,priority
	write_elements_inc		1,1,9,2
	get_vector_value		7,1
	get_nil		8
	proceed
take_apart_priority_and_alloc_8_1:
	otherwise		take_apart_priority_and_alloc_8_0
	get_nil		3
	get_value		4,5
	get_nil		7
	get_nil		8
	put_structured_constant		3,'$SCNST_20'
	put_func		4,3,error_message
	write_element_value		4,1,3
	write_element_value		4,2,6
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
take_apart_priority_and_alloc_8_12:
	suspend		take_apart_priority_and_alloc_8_0
	module_entry		kl1cmp_normalize
	predicate		classify_pragma,10
classify_pragma_10_0:
	try_me_else		classify_pragma_10_1
	jump_on_non_atom		6,classify_pragma_10_3
	test_nil		6,classify_pragma_10_1
	wait_vector		7,2
	read_element		7,0,11
	atom		11
	branch_on_atom		11,2,classify_pragma_10_1
	bucket_entry_a		node,classify_pragma_10_6
	bucket_entry_a		processor,classify_pragma_10_7
classify_pragma_10_6:
	read_element		7,1,6
	put_nil		11
	get_value		4,5
	get_value		1,2
	put_reused_func		1,7,new_variable
	write_element_marked_variable		1,1,2
	put_list_val_val		4,1,11
	get_list_value		3,4
	put_func		1,2,node
	write_element_value		1,1,2
	get_vector_value		8,1
	put_func		1,3,=
	write_element_value		1,1,2
	write_element_value		1,2,6
	put_list_val_val		2,1,10
	get_list_value		9,2
	proceed
classify_pragma_10_7:
	read_element		7,1,6
	put_nil		11
	get_value		4,5
	get_value		1,2
	put_reused_func		1,7,new_variable
	write_element_marked_variable		1,1,2
	put_list_val_val		4,1,11
	get_list_value		3,4
	put_func		1,2,processor
	write_element_value		1,1,2
	get_vector_value		8,1
	put_func		1,3,=
	write_element_value		1,1,2
	write_element_value		1,2,6
	put_list_val_val		2,1,10
	get_list_value		9,2
	proceed
classify_pragma_10_3:
	check_vector		6,3,classify_pragma_10_1
	read_element		6,0,11
	wait_atom		11,priority
	read_element		6,1,12
	atom		12
	branch_on_atom		12,2,classify_pragma_10_1
	bucket_entry_a		$,classify_pragma_10_10
	bucket_entry_a		*,classify_pragma_10_11
classify_pragma_10_10:
	read_element		6,2,13
	wait_nil		7
	put_nil		7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,2
	put_list_val_val		4,1,7
	get_list_value		3,4
	put_func		1,2,priority
	write_element_value		1,1,2
	get_vector_value		8,1
	put_reused_func		1,6,'RLTV'
	write_element_value		1,1,13
	write_element_value		1,2,2
	put_list_val_val		2,1,10
	get_list_value		9,2
	proceed
classify_pragma_10_11:
	read_element		6,2,13
	wait_nil		7
	put_nil		7
	get_value		4,5
	get_value		1,2
	put_func		1,2,new_variable
	write_element_marked_variable		1,1,2
	put_list_val_val		4,1,7
	get_list_value		3,4
	put_func		1,2,priority
	write_element_value		1,1,2
	get_vector_value		8,1
	put_reused_func		1,6,'RATE'
	write_element_value		1,1,13
	write_element_value		1,2,2
	put_list_val_val		2,1,10
	get_list_value		9,2
	proceed
classify_pragma_10_1:
	otherwise		classify_pragma_10_0
	collect_value		7
	get_nil		3
	get_value		4,5
	get_nil		8
	get_value		9,10
	put_structured_constant		3,'$SCNST_21'
	put_func		4,3,error_message
	write_element_value		4,1,3
	write_element_value		4,2,6
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
classify_pragma_10_26:
	suspend		classify_pragma_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_user_body,6
normalize_user_body_6_0:
	try_me_else		normalize_user_body_6_1
	jump_on_non_list_var_var		6,normalize_user_body_6_3,7,8
	wait_nil		8
	collect_list		6
	put_value		6,7
	execute		6,normalize_last_body_goal_6_0
normalize_user_body_6_3:
	check_nil		6,normalize_user_body_6_1
	get_nil		3
	get_value		1,2
	put_list		1
	write_car_atom		1,proceed
	write_cdr_value		1,5
	get_list_value		4,1
	proceed
normalize_user_body_6_1:
	otherwise		normalize_user_body_6_0
	try_me_else		normalize_user_body_6_8
	wait_list_var_var		6,7,8
	collect_list		6
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,9
	set_value		5,5
	set_value		6,8
	enqueue_goal		6,normalize_user_body_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,9
	put_value		6,7
	execute		6,normalize_body_goal_6_0
normalize_user_body_6_8:
	suspend		normalize_user_body_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_last_body_goal,6
normalize_last_body_goal_6_0:
	try_me_else		normalize_last_body_goal_6_1
	wait_vector		6,3
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,normalize_last_body_goal_6_1
	bucket_entry_a		:,normalize_last_body_goal_6_4
	bucket_entry_a		@,normalize_last_body_goal_6_5
normalize_last_body_goal_6_4:
	read_elements_inc		6,1,8,2
	try_me_else		normalize_last_body_goal_6_6
	wait_vector		9,3
	read_element		9,0,10
	wait_atom		10,@
	read_element		9,1,7
	read_element		9,2,10
	collect_vector		9
	create_goal		9
	set_values_inc		1,1,5
	put_reused_func		1,6,@
	write_element_variable		1,1,2
	write_element_value		1,2,10
	set_value		6,1
	set_value		7,8
	set_variable		8,3
	set_variable		9,1
	enqueue_goal		9,normalize_execute_external_call_9_0
	create_goal		3
	set_marked_value		1,7
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,7
	execute		2,pack_body_goal_2_0
normalize_last_body_goal_6_6:
	collect_vector		6
	create_goal		9
	set_values_inc		1,1,5
	set_variable		6,2
	set_value		7,8
	set_variable		8,3
	set_variable		9,1
	enqueue_goal		9,normalize_execute_external_call_9_0
	create_goal		3
	set_marked_value		1,9
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,9
	execute		2,pack_body_goal_2_0
normalize_last_body_goal_6_5:
	read_elements_inc		6,1,8,2
	put_list		7
	write_car_atom		7,proceed
	write_cdr_value		7,5
	create_goal		8
	set_values_inc		1,1,4
	set_value		5,7
	put_reused_func		1,6,@
	write_element_variable		1,1,2
	write_element_value		1,2,9
	set_value		6,1
	set_variable		7,3
	set_variable		8,1
	enqueue_goal		8,normalize_with_pragma_8_0
	create_goal		3
	set_marked_value		1,8
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,8
	execute		2,pack_body_goal_2_0
normalize_last_body_goal_6_1:
	otherwise		normalize_last_body_goal_6_0
	put_vector		7,2
	write_element_variable		7,0,9
	write_element_variable		7,1,8
	get_vector_value		3,7
	put_func		3,2,execute
	write_element_variable		3,1,10
	put_list_val_val		7,3,5
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,2
	set_value		5,7
	set_variable		6,5
	enqueue_goal		6,normalize_body_goal_args_6_0
	create_goal		11
	set_value		1,1
	set_value		2,3
	set_value		3,8
	set_value		4,4
	set_value		5,2
	set_marked_variable		6,1
	set_integer		7,1
	set_variable		8,2
	set_variable		9,3
	set_value		10,10
	set_value		11,5
	enqueue_goal		11,extract_args_11_0
	create_goal		3
	set_value		1,3
	set_variable		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,gen_functor,3
	create_goal		3
	set_marked_value		1,6
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,6
	execute		2,pack_body_goal_2_0
normalize_last_body_goal_6_16:
	suspend		normalize_last_body_goal_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_execute_external_call,9
normalize_execute_external_call_9_0:
	try_me_else		normalize_execute_external_call_9_1
	wait_vector		6,3
	read_element		6,0,10
	wait_atom		10,@
	read_elements_inc		6,1,10,2
	put_list		12
	write_car_atom		12,proceed
	write_cdr_value		12,5
	put_reused_func		6,6,@
	write_elements_inc		6,1,10,2
	put_value		5,12
	execute		9,normalize_external_call_9_0
normalize_execute_external_call_9_1:
	otherwise		normalize_execute_external_call_9_0
	put_vector		12,2
	write_element_variable		12,0,11
	write_element_variable		12,1,10
	get_vector_value		3,12
	put_func		3,3,execute_ext
	write_element_variable		3,1,12
	write_element_value		3,2,7
	put_list_val_val		7,3,5
	create_goal		6
	set_variable		1,5
	set_value		2,2
	set_value		3,11
	set_variable		4,3
	set_value		5,7
	set_variable		6,2
	enqueue_goal		6,normalize_body_goal_args_6_0
	create_goal		11
	set_value		1,1
	set_value		2,5
	set_value		3,10
	set_values_dec		4,4,2
	set_marked_value		6,9
	set_integer		7,1
	set_value		8,6
	set_variable		9,1
	set_value		10,12
	set_value		11,2
	enqueue_goal		11,extract_args_11_0
	put_values_inc		2,8,2
	execute_external		kl1cmp_reader,gen_functor,3
normalize_execute_external_call_9_6:
	suspend		normalize_execute_external_call_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_with_pragma,8
normalize_with_pragma_8_0:
	try_me_else		normalize_with_pragma_8_1
	wait_vector		6,3
	read_element		6,0,9
	wait_atom		9,@
	read_elements_inc		6,1,9,2
	put_vector		13,2
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	get_vector_value		3,13
	put_list		3
	write_car_variable		3,13
	write_cdr_value		3,5
	create_goal		7
	set_variable		1,14
	set_value		2,2
	set_value		3,12
	set_variable		4,5
	set_value		5,3
	set_variable		6,2
	set_marked_value		7,9
	enqueue_goal		7,extract_and_normalize_fork_args_7_0
	create_goal		3
	set_value		1,9
	set_void		2
	set_value		3,2
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_reused_func		9,6,/
	write_elements_inc		9,1,7,2
	put_value		2,14
	put_value		3,11
	put_values_dec		6,10,2
	put_value		8,13
	execute		8,normalize_with_priority_or_alloc_8_0
normalize_with_pragma_8_1:
	suspend		normalize_with_pragma_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_with_priority_or_alloc,8
normalize_with_priority_or_alloc_8_0:
	try_me_else		normalize_with_priority_or_alloc_8_1
	wait_vector		6,2
	read_element		6,0,9
	atom		9
	branch_on_atom		9,3,normalize_with_priority_or_alloc_8_1
	bucket_entry_a		node,normalize_with_priority_or_alloc_8_4
	bucket_entry_a		priority,normalize_with_priority_or_alloc_8_5
	bucket_entry_a		processor,normalize_with_priority_or_alloc_8_6
normalize_with_priority_or_alloc_8_4:
	read_element		6,1,10
	collect_vector		6
	get_nil		3
	get_value		1,2
	put_func		1,3,enqueue_to_node
	write_element_marked_value		1,1,7
	write_element_marked_value		1,2,10
	get_vector_value		8,1
	put_func		1,3,create_to_node
	write_element_value		1,1,7
	write_element_value		1,2,10
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_with_priority_or_alloc_8_5:
	read_element		6,1,10
	collect_vector		6
	get_nil		3
	get_value		1,2
	put_func		1,3,enqueue_with_priority
	write_element_marked_value		1,1,7
	write_element_marked_value		1,2,10
	get_vector_value		8,1
	put_func		1,3,create_with_priority
	write_element_value		1,1,7
	write_element_value		1,2,10
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_with_priority_or_alloc_8_6:
	read_element		6,1,10
	collect_vector		6
	get_nil		3
	get_value		1,2
	put_func		1,3,enqueue_to_processor
	write_element_marked_value		1,1,7
	write_element_marked_value		1,2,10
	get_vector_value		8,1
	put_func		1,3,create_to_processor
	write_element_value		1,1,7
	write_element_value		1,2,10
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_with_priority_or_alloc_8_1:
	suspend		normalize_with_priority_or_alloc_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_goal,6
normalize_body_goal_6_0:
	try_me_else		normalize_body_goal_6_1
	wait_vector		6,3
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,normalize_body_goal_6_1
	bucket_entry_a		:,normalize_body_goal_6_4
	bucket_entry_a		@,normalize_body_goal_6_5
normalize_body_goal_6_4:
	read_elements_inc		6,1,8,2
	collect_vector		6
	create_goal		9
	set_values_inc		1,1,5
	set_variable		6,2
	set_value		7,8
	set_variable		8,3
	set_variable		9,1
	enqueue_goal		9,normalize_external_call_9_0
	create_goal		3
	set_marked_value		1,9
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,9
	execute		2,pack_body_goal_2_0
normalize_body_goal_6_5:
	read_elements_inc		6,1,8,2
	create_goal		8
	set_values_inc		1,1,5
	put_reused_func		1,6,@
	write_element_variable		1,1,2
	write_element_value		1,2,9
	set_value		6,1
	set_variable		7,3
	set_variable		8,1
	enqueue_goal		8,normalize_with_pragma_8_0
	create_goal		3
	set_marked_value		1,8
	set_value		2,3
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,8
	execute		2,pack_body_goal_2_0
normalize_body_goal_6_1:
	otherwise		normalize_body_goal_6_0
	put_func		7,3,/
	write_element_marked_variable		7,1,10
	write_element_marked_variable		7,2,9
	put_func		8,2,create_goal
	write_element_value		8,1,7
	get_list_val_var		4,7,8,8
	put_func		4,3,/
	write_elements_dec		4,1,10,2
	put_func		7,2,enqueue_goal
	write_element_value		7,1,4
	put_list_val_val		4,7,5
	create_goal		7
	set_values_inc		1,1,3
	set_value		4,8
	set_value		5,4
	set_variable		6,1
	set_marked_variable		7,2
	enqueue_goal		7,extract_and_normalize_fork_args_7_0
	create_goal		3
	set_value		1,2
	set_void		2
	set_value		3,1
	enqueue_goal_external		kl1cmp_reader,functor,3
	create_goal		3
	set_marked_value		1,6
	set_values_dec		2,10,2
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,6
	execute		2,pack_body_goal_2_0
normalize_body_goal_6_11:
	suspend		normalize_body_goal_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_external_call,9
normalize_external_call_9_0:
	try_me_else		normalize_external_call_9_1
	wait_vector		6,3
	read_element		6,0,10
	wait_atom		10,@
	read_elements_inc		6,1,10,2
	put_integer		12,1
	put_nil		13
	b_set_vector_element		11,12,11,13,12
	put_reused_func		6,6,/
	write_element_marked_value		6,1,8
	write_element_marked_value		6,2,9
	put_func		12,4,create_ext_with_priority
	write_element_value		12,1,6
	write_element_marked_value		12,2,11
	write_element_marked_value		12,3,7
	get_list_val_var		4,6,12,12
	put_func		4,3,/
	write_elements_inc		4,1,8,2
	put_func		6,4,enqueue_ext_with_priority
	write_element_value		6,1,4
	write_element_value		6,2,11
	write_element_value		6,3,7
	put_list_val_val		4,6,5
	create_goal		7
	set_values_inc		1,1,3
	set_value		4,12
	set_value		5,4
	set_variable		6,3
	set_marked_value		7,10
	enqueue_goal		7,extract_and_normalize_fork_args_7_0
	put_value		1,10
	put_void		2
	execute_external		kl1cmp_reader,functor,3
normalize_external_call_9_1:
	otherwise		normalize_external_call_9_0
	put_func		10,3,/
	write_element_marked_value		10,1,8
	write_element_marked_value		10,2,9
	put_func		11,3,create_ext
	write_element_value		11,1,10
	write_element_marked_value		11,2,7
	get_list_val_var		4,12,11,10
	put_func		4,3,/
	write_elements_inc		4,1,8,2
	put_func		8,3,enqueue_ext
	write_element_value		8,1,4
	write_element_value		8,2,7
	put_list_val_val		4,8,5
	create_goal		7
	set_values_inc		1,1,3
	set_value		4,10
	set_value		5,4
	set_variable		6,3
	set_marked_value		7,6
	enqueue_goal		7,extract_and_normalize_fork_args_7_0
	put_value		1,6
	put_void		2
	execute_external		kl1cmp_reader,functor,3
normalize_external_call_9_6:
	suspend		normalize_external_call_9_0
	module_entry		kl1cmp_normalize
	predicate		extract_args,11
extract_args_11_0:
	try_me_else		extract_args_11_1
	integer		6
	test_integer		6,0,extract_args_11_3
	collect_value		8
	collect_value		7
	get_nil		3
	get_value		4,5
	get_value		1,2
	get_value		9,10
	get_nil		11
	proceed
extract_args_11_3:
	put_integer		12,0
	g_less_than		12,6
	put_marked_value		12,7
	put_nil		13
	b_set_vector_element		8,12,8,13,12
	put_marked_variable		13,14
	b_set_vector_element		9,7,9,13,13
	put_list_val_var		9,14,15
	put_list_val_val		16,8,9
	get_list_value		11,16
	put_func		8,2,new_variable
	write_element_value		8,1,14
	get_list_val_var		3,9,8,8
	b_decrement		6,3
	put_value		6,3
	b_increment		7,3
	put_value		7,3
	put_value		3,8
	put_values_inc		8,12,2
	put_value		11,15
	execute		11,extract_args_11_0
extract_args_11_1:
	try_me_else		extract_args_11_4
	wait_list_var_var		8,12,13
	collect_value		9
	collect_value		7
	collect_value		6
	put_nil		6
	get_value		4,5
	get_value		1,2
	put_reused_list		1,8
	write_car_marked_variable		1,5
	write_cdr_marked_variable		1,4
	get_list_value		10,1
	put_list		1
	write_car_value		1,4
	write_cdr_nil		1
	put_list_val_val		2,13,1
	put_list_val_val		1,5,2
	put_list_val_val		2,12,1
	get_list_value		11,2
	put_func		1,2,new_variable
	write_element_value		1,1,4
	put_list_val_val		2,1,6
	put_func		1,2,new_variable
	write_element_value		1,1,5
	put_list_val_val		4,1,2
	get_list_value		3,4
	proceed
extract_args_11_4:
	suspend		extract_args_11_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_args,6
normalize_body_args_6_0:
	try_me_else		normalize_body_args_6_1
	jump_on_non_list_var_var		6,normalize_body_args_6_3,7,10
	wait_list_var_var		10,8,9
	collect_list		10
	put_vector		10,2
	write_element_variable		10,0,13
	write_element_variable		10,1,12
	put_func		11,2,new_variable
	write_element_marked_value		11,1,8
	put_reused_list_val_val		6,6,11,10
	get_list_value		3,6
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,13
	set_variable		4,6
	set_value		5,5
	set_value		6,9
	enqueue_goal		6,normalize_body_args_6_0
	put_value		2,3
	put_value		3,12
	put_values_inc		5,6,3
	execute		7,normalize_body_unify_variable_7_0
normalize_body_args_6_3:
	check_nil		6,normalize_body_args_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_body_args_6_1:
	suspend		normalize_body_args_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_goal_args,6
normalize_body_goal_args_6_0:
	try_me_else		normalize_body_goal_args_6_1
	jump_on_non_list_var_var		6,normalize_body_goal_args_6_3,7,10
	wait_list_var_var		10,8,9
	collect_list		6
	collect_list		10
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,6
	get_vector_value		3,11
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_variable		4,10
	set_value		5,5
	set_value		6,9
	enqueue_goal		6,normalize_body_goal_args_6_0
	put_value		2,3
	put_value		3,6
	put_value		5,10
	put_values_inc		6,7,2
	execute		7,normalize_body_goal_unify_variable_7_0
normalize_body_goal_args_6_3:
	check_nil		6,normalize_body_goal_args_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_body_goal_args_6_1:
	suspend		normalize_body_goal_args_6_0
	module_entry		kl1cmp_normalize
	predicate		extract_and_normalize_fork_args,7
extract_and_normalize_fork_args_7_0:
	create_goal		10
	set_variable		1,9
	set_values_inc		2,2,2
	set_variable		4,8
	set_value		5,5
	set_variable		6,5
	set_nil		7
	set_value		8,6
	set_integer		9,1
	set_value		10,7
	enqueue_goal		10,extract_and_normalize_fork_args_10_0
	put_value		2,9
	put_value		3,4
	put_value		4,8
	execute		5,concatenate_5_0
extract_and_normalize_fork_args_7_1:
	suspend		extract_and_normalize_fork_args_7_0
	module_entry		kl1cmp_normalize
	predicate		extract_and_normalize_fork_args,10
extract_and_normalize_fork_args_10_0:
	try_me_else		extract_and_normalize_fork_args_10_1
	integer		8
	test_integer		8,0,extract_and_normalize_fork_args_10_3
	collect_value		10
	collect_value		9
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
extract_and_normalize_fork_args_10_3:
	put_integer		11,0
	g_less_than		11,8
	put_vector		11,2
	write_element_variable		11,0,14
	write_element_variable		11,1,13
	get_vector_value		3,11
	put_marked_value		3,9
	put_nil		11
	b_set_vector_element		10,3,10,11,3
	put_func		11,3,:=
	write_element_value		11,1,9
	write_element_variable		11,2,15
	put_list_val_var		12,11,11
	b_decrement		8,8
	b_increment		9,9
	create_goal		10
	set_variable		1,16
	set_value		2,2
	set_value		3,14
	set_value		4,11
	set_value		5,5
	set_variable		6,11
	set_values_inc		7,7,3
	set_value		10,3
	enqueue_goal		10,extract_and_normalize_fork_args_10_0
	put_value		2,16
	put_value		3,13
	put_value		5,12
	put_values_dec		7,11,2
	put_value		9,15
	execute		9,normalize_argument_put_9_0
extract_and_normalize_fork_args_10_1:
	try_me_else		extract_and_normalize_fork_args_10_4
	wait_list_var_var		10,11,12
	collect_value		9
	collect_value		8
	put_vector		8,2
	write_element_variable		8,0,14
	write_element_variable		8,1,13
	get_vector_value		3,8
	put_func		3,3,:=
	write_element_marked_value		3,1,12
	write_element_variable		3,2,15
	put_reused_list_val_val		8,10,3,5
	put_func		3,3,:=
	write_element_marked_value		3,1,11
	write_element_variable		3,2,9
	put_list_val_val		5,3,8
	create_goal		9
	set_variable		1,3
	set_value		2,2
	set_value		3,14
	set_variable		4,10
	set_value		5,5
	set_variable		6,8
	set_value		7,7
	set_value		8,12
	set_value		9,15
	enqueue_goal		9,normalize_argument_put_9_0
	put_value		2,3
	put_value		3,13
	put_value		5,10
	put_value		7,8
	put_value		8,11
	execute		9,normalize_argument_put_9_0
extract_and_normalize_fork_args_10_4:
	suspend		extract_and_normalize_fork_args_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_argument_put,9
normalize_argument_put_9_0:
	try_me_else		normalize_argument_put_9_1
	wait		8
	switch_on_type		8,normalize_argument_put_9_2,normalize_argument_put_9_3,normalize_argument_put_9_1,normalize_argument_put_9_4,normalize_argument_put_9_1,normalize_argument_put_9_5
normalize_argument_put_9_2:
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	get_vector_value		9,1
	proceed
normalize_argument_put_9_3:
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	get_vector_value		9,1
	proceed
normalize_argument_put_9_4:
	jump_on_arity		8,4,normalize_argument_put_9_1
	table_entry		normalize_argument_put_9_1
	table_entry		normalize_argument_put_9_1
	table_entry		normalize_argument_put_9_6
	table_entry		normalize_argument_put_9_7
normalize_argument_put_9_6:
	read_element		8,0,10
	wait_atom		10,'$SCNST'
	read_element		8,1,10
	string		10
	g_string		10,11,12
	put_nil		11
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,var
	write_element_marked_variable		1,1,6
	get_vector_value		9,1
	put_func		1,2,new_variable
	write_element_value		1,1,6
	put_list_val_val		2,1,11
	get_list_value		3,2
	put_func		1,2,struct
	write_element_value		1,1,10
	put_func		2,3,=
	write_element_value		2,1,6
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_argument_put_9_7:
	read_element		8,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		8,1,10,2
	integer		10
	string		11
	g_string		11,12,13
	wait_integer		13,8
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_reused_func		1,8,'$VAR'
	write_elements_inc		1,1,10,2
	put_func		2,2,var
	write_element_value		2,1,1
	get_vector_value		9,2
	proceed
normalize_argument_put_9_5:
	is_float		8,normalize_argument_put_9_1
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	get_vector_value		9,1
	proceed
normalize_argument_put_9_1:
	otherwise		normalize_argument_put_9_0
	try_me_else		normalize_argument_put_9_10
	jump_on_non_list_var_var		8,normalize_argument_put_9_12,10,11
	get_value		4,5
	put_func		4,2,var
	write_element_marked_variable		4,1,12
	get_vector_value		9,4
	put_func		4,2,new_variable
	write_element_value		4,1,12
	get_reused_list_val_var		3,5,8,4,4
	put_list_val_val		8,10,11
	put_value		3,4
	put_values_inc		4,6,3
	put_value		7,12
	execute		7,normalize_body_list_7_0
normalize_argument_put_9_12:
	is_vector		8,normalize_argument_put_9_10
	g_vector		8,10
	get_value		4,5
	put_func		4,2,var
	write_element_marked_variable		4,1,11
	get_vector_value		9,4
	put_func		4,2,new_variable
	write_element_value		4,1,11
	get_list_val_var		3,5,4,4
	put_value		3,4
	put_values_inc		4,6,3
	put_values_dec		7,11,2
	execute		8,normalize_body_vector_8_0
normalize_argument_put_9_10:
	suspend		normalize_argument_put_9_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_unify,7
normalize_body_unify_7_0:
	try_me_else		normalize_body_unify_7_1
	wait_vector		6,3
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_reused_func		10,6,'$VAR'
	write_elements_inc		10,1,8,2
	put_value		6,7
	put_value		7,10
	execute		7,normalize_body_unify_variable_7_0
normalize_body_unify_7_1:
	try_me_else		normalize_body_unify_7_3
	wait_vector		7,3
	read_element		7,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		7,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_reused_func		7,7,'$VAR'
	write_elements_inc		7,1,8,2
	execute		7,normalize_body_unify_variable_7_0
normalize_body_unify_7_3:
	otherwise		normalize_body_unify_7_0
	get_nil		3
	get_value		4,5
	put_func		3,3,=
	write_elements_inc		3,1,6,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_22'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_body_unify_7_10:
	suspend		normalize_body_unify_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_unify_variable,7
normalize_body_unify_variable_7_0:
	try_me_else		normalize_body_unify_variable_7_1
	wait		6
	switch_on_type		6,normalize_body_unify_variable_7_2,normalize_body_unify_variable_7_3,normalize_body_unify_variable_7_1,normalize_body_unify_variable_7_4,normalize_body_unify_variable_7_1,normalize_body_unify_variable_7_5
normalize_body_unify_variable_7_2:
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_unify_variable_7_3:
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_unify_variable_7_4:
	jump_on_arity		6,4,normalize_body_unify_variable_7_1
	table_entry		normalize_body_unify_variable_7_1
	table_entry		normalize_body_unify_variable_7_1
	table_entry		normalize_body_unify_variable_7_6
	table_entry		normalize_body_unify_variable_7_7
normalize_body_unify_variable_7_6:
	read_element		6,0,8
	wait_atom		8,'$SCNST'
	read_element		6,1,8
	string		8
	g_string		8,9,10
	put_nil		9
	get_value		1,2
	put_reused_func		1,6,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,9
	get_list_value		3,2
	put_func		1,2,var
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_body_unify_variable_7_7:
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	get_nil		3
	get_value		1,2
	put_reused_func		1,6,'$VAR'
	write_elements_inc		1,1,8,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,3,=
	write_element_value		1,1,7
	write_element_value		1,2,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_body_unify_variable_7_5:
	is_float		6,normalize_body_unify_variable_7_1
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_unify_variable_7_1:
	otherwise		normalize_body_unify_variable_7_0
	try_me_else		normalize_body_unify_variable_7_10
	jump_on_non_list_var_var		6,normalize_body_unify_variable_7_12,8,9
	put_func		10,2,new_variable
	write_element_marked_variable		10,1,11
	get_reused_list_val_var		3,6,6,10,10
	put_func		3,2,list
	write_element_value		3,1,11
	put_func		6,3,<=
	write_element_value		6,1,7
	write_element_value		6,2,3
	put_list_val_val		7,6,5
	put_list_val_val		6,8,9
	put_value		3,10
	put_value		5,7
	put_value		7,11
	execute		7,normalize_body_list_7_0
normalize_body_unify_variable_7_12:
	is_vector		6,normalize_body_unify_variable_7_10
	g_vector		6,8
	put_func		9,2,new_variable
	write_element_marked_variable		9,1,11
	get_list_val_var		3,12,9,10
	put_func		3,2,vector
	write_element_value		3,1,11
	put_func		9,3,<=
	write_element_value		9,1,7
	write_element_value		9,2,3
	put_list_val_val		7,9,5
	put_value		3,10
	put_value		5,7
	put_value		7,11
	execute		8,normalize_body_vector_8_0
normalize_body_unify_variable_7_10:
	suspend		normalize_body_unify_variable_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_vector,8
normalize_body_vector_8_0:
	put_func		9,2,vector
	write_element_marked_value		9,1,8
	put_func		10,3,=
	write_element_value		10,1,7
	write_element_value		10,2,9
	put_list_val_var		7,10,9
	create_goal		10
	set_values_inc		1,1,3
	set_value		4,9
	set_value		5,5
	set_variable		6,3
	set_variable		7,5
	set_value		8,8
	set_integer		9,0
	set_value		10,6
	enqueue_goal		10,normalize_body_structure_args_10_0
	put_value		1,4
	put_value		2,7
	put_value		4,5
	execute		4,'C_4_0'
normalize_body_vector_8_1:
	suspend		normalize_body_vector_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_list,7
normalize_body_list_7_0:
	put_func		8,3,=
	write_element_value		8,1,7
	write_element_atom		8,2,list
	put_list_val_var		7,8,8
	create_goal		8
	set_values_inc		1,1,3
	set_value		4,8
	set_value		5,5
	set_variable		6,1
	set_variable		7,2
	set_value		8,6
	enqueue_goal		8,normalize_body_list_args_8_0
	put_value		3,4
	put_value		4,7
	execute		4,'C_4_0'
normalize_body_list_7_1:
	suspend		normalize_body_list_7_0
	module_entry		kl1cmp_normalize
	predicate		'C',4
'C_4_0':
	get_value		1,3
	get_value		2,4
	proceed
'C_4_1':
	suspend		'C_4_0'
	module_entry		kl1cmp_normalize
	predicate		normalize_body_structure_args,10
normalize_body_structure_args_10_0:
	try_me_else		normalize_body_structure_args_10_1
	integer		8
	test_integer		8,0,normalize_body_structure_args_10_3
	collect_value		10
	collect_value		9
	get_nil		3
	get_value		6,7
	get_value		4,5
	get_value		1,2
	proceed
normalize_body_structure_args_10_3:
	put_integer		11,0
	g_less_than		11,8
	put_vector		13,2
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	get_vector_value		3,13
	b_decrement		8,3
	put_marked_value		8,9
	b_increment		8,8
	put_nil		13
	b_set_vector_element		10,9,9,13,10
	create_goal		10
	set_variable		1,14
	set_value		2,2
	set_value		3,12
	set_variable		4,13
	set_value		5,5
	set_variable		6,12
	set_value		7,7
	set_value		8,3
	set_value		9,8
	set_value		10,10
	enqueue_goal		10,normalize_body_structure_args_10_0
	put_value		2,14
	put_value		3,11
	put_value		5,13
	put_value		7,12
	put_value		8,9
	execute		8,normalize_body_one_arg_8_0
normalize_body_structure_args_10_1:
	suspend		normalize_body_structure_args_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_list_args,8
normalize_body_list_args_8_0:
	try_me_else		normalize_body_list_args_8_1
	wait_list_var_var		8,9,10
	collect_list		8
	put_vector		12,2
	write_element_variable		12,0,11
	write_element_variable		12,1,8
	get_vector_value		3,12
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,11
	set_variable		4,11
	set_value		5,5
	set_variable		6,3
	set_variable		7,2
	set_value		8,10
	enqueue_goal		8,normalize_body_one_arg_8_0
	create_goal		8
	set_value		1,1
	set_value		2,12
	set_value		3,8
	set_value		4,4
	set_value		5,11
	set_value		6,2
	set_variable		7,4
	set_value		8,9
	enqueue_goal		8,normalize_body_one_arg_8_0
	put_values_inc		1,6,2
	execute		4,'C_4_0'
normalize_body_list_args_8_1:
	suspend		normalize_body_list_args_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_one_arg,8
normalize_body_one_arg_8_0:
	try_me_else		normalize_body_one_arg_8_1
	vector		8
	jump_on_arity		8,4,normalize_body_one_arg_8_1
	table_entry		normalize_body_one_arg_8_1
	table_entry		normalize_body_one_arg_8_1
	table_entry		normalize_body_one_arg_8_3
	table_entry		normalize_body_one_arg_8_4
normalize_body_one_arg_8_3:
	read_element		8,0,9
	wait_atom		9,'$SCNST'
	read_element		8,1,9
	string		9
	put_nil		10
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,10
	get_list_value		3,2
	put_func		1,2,var
	write_element_value		1,1,6
	put_func		2,2,draw
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_value		2,1,9
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_body_one_arg_8_4:
	read_element		8,0,9
	wait_atom		9,'$VAR'
	read_elements_inc		8,1,9,2
	integer		9
	string		10
	g_string		10,11,12
	wait_integer		12,8
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_reused_func		1,8,'$VAR'
	write_elements_inc		1,1,9,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,2,draw
	write_element_value		1,1,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_body_one_arg_8_1:
	otherwise		normalize_body_one_arg_8_0
	try_me_else		normalize_body_one_arg_8_7
	wait		8
	switch_on_type		8,normalize_body_one_arg_8_8,normalize_body_one_arg_8_9,normalize_body_one_arg_8_10,normalize_body_one_arg_8_11,normalize_body_one_arg_8_7,normalize_body_one_arg_8_12
normalize_body_one_arg_8_10:
	read_car		8,9
	read_cdr		8,10
	put_func		11,2,new_variable
	write_element_marked_variable		11,1,12
	get_reused_list_val_var		3,8,8,11,11
	put_func		3,2,var
	write_element_value		3,1,12
	put_func		8,2,draw
	write_element_value		8,1,3
	put_list_val_val		3,8,5
	get_list_value		4,3
	put_list_val_val		8,9,10
	put_value		3,11
	put_values_inc		4,6,3
	put_value		7,12
	execute		7,normalize_body_list_7_0
normalize_body_one_arg_8_8:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,2,draw
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_one_arg_8_9:
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,2,draw
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_one_arg_8_11:
	g_vector		8,9
	put_func		10,2,new_variable
	write_element_marked_variable		10,1,12
	get_list_val_var		3,13,10,11
	put_func		3,2,var
	write_element_value		3,1,12
	put_func		10,2,draw
	write_element_value		10,1,3
	put_list_val_val		3,10,5
	get_list_value		4,3
	put_value		3,11
	put_values_inc		4,6,3
	put_value		7,12
	put_value		8,9
	execute		8,normalize_body_vector_8_0
normalize_body_one_arg_8_12:
	is_float		8,normalize_body_one_arg_8_7
	get_nil		3
	get_value		6,7
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,8
	put_func		2,2,draw
	write_element_value		2,1,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_one_arg_8_7:
	suspend		normalize_body_one_arg_8_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_goal_unify,7
normalize_body_goal_unify_7_0:
	try_me_else		normalize_body_goal_unify_7_1
	wait_vector		6,3
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_reused_func		10,6,'$VAR'
	write_elements_inc		10,1,8,2
	put_value		6,7
	put_value		7,10
	execute		7,normalize_body_goal_unify_variable_7_0
normalize_body_goal_unify_7_1:
	try_me_else		normalize_body_goal_unify_7_3
	wait_vector		7,3
	read_element		7,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		7,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	put_reused_func		7,7,'$VAR'
	write_elements_inc		7,1,8,2
	execute		7,normalize_body_goal_unify_variable_7_0
normalize_body_goal_unify_7_3:
	otherwise		normalize_body_goal_unify_7_0
	get_nil		3
	get_value		4,5
	put_func		3,3,=
	write_elements_inc		3,1,6,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_23'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
normalize_body_goal_unify_7_10:
	suspend		normalize_body_goal_unify_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_goal_unify_variable,7
normalize_body_goal_unify_variable_7_0:
	try_me_else		normalize_body_goal_unify_variable_7_1
	wait		6
	switch_on_type		6,normalize_body_goal_unify_variable_7_2,normalize_body_goal_unify_variable_7_3,normalize_body_goal_unify_variable_7_1,normalize_body_goal_unify_variable_7_4,normalize_body_goal_unify_variable_7_1,normalize_body_goal_unify_variable_7_5
normalize_body_goal_unify_variable_7_2:
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_goal_unify_variable_7_3:
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_goal_unify_variable_7_4:
	jump_on_arity		6,4,normalize_body_goal_unify_variable_7_1
	table_entry		normalize_body_goal_unify_variable_7_1
	table_entry		normalize_body_goal_unify_variable_7_1
	table_entry		normalize_body_goal_unify_variable_7_6
	table_entry		normalize_body_goal_unify_variable_7_7
normalize_body_goal_unify_variable_7_6:
	read_element		6,0,8
	wait_atom		8,'$SCNST'
	read_element		6,1,8
	string		8
	put_nil		9
	get_value		1,2
	put_reused_func		1,6,new_variable
	write_element_marked_variable		1,1,6
	put_list_val_val		2,1,9
	get_list_value		3,2
	put_func		1,2,var
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	put_func		2,2,struct
	write_element_value		2,1,8
	put_func		3,3,=
	write_element_value		3,1,6
	write_element_value		3,2,2
	put_list_val_val		2,3,1
	get_list_value		4,2
	proceed
normalize_body_goal_unify_variable_7_7:
	read_element		6,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		6,1,8,2
	integer		8
	string		9
	g_string		9,10,11
	wait_integer		11,8
	get_nil		3
	get_value		1,2
	put_reused_func		1,6,'$VAR'
	write_elements_inc		1,1,8,2
	put_func		2,2,var
	write_element_value		2,1,1
	put_func		1,3,=
	write_element_value		1,1,7
	write_element_value		1,2,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
normalize_body_goal_unify_variable_7_5:
	is_float		6,normalize_body_goal_unify_variable_7_1
	get_nil		3
	get_value		1,2
	put_func		1,2,atomic
	write_element_value		1,1,6
	put_func		2,3,=
	write_element_value		2,1,7
	write_element_value		2,2,1
	put_list_val_val		1,2,5
	get_list_value		4,1
	proceed
normalize_body_goal_unify_variable_7_1:
	otherwise		normalize_body_goal_unify_variable_7_0
	try_me_else		normalize_body_goal_unify_variable_7_10
	jump_on_non_list_var_var		6,normalize_body_goal_unify_variable_7_12,8,9
	put_reused_list_val_val		6,6,8,9
	execute		7,normalize_body_list_7_0
normalize_body_goal_unify_variable_7_12:
	is_vector		6,normalize_body_goal_unify_variable_7_10
	g_vector		6,8
	execute		8,normalize_body_vector_8_0
normalize_body_goal_unify_variable_7_10:
	suspend		normalize_body_goal_unify_variable_7_0
	module_entry		kl1cmp_normalize
	predicate		max_goal_slots,1
max_goal_slots_1_0:
	get_integer		1,32
	proceed
max_goal_slots_1_1:
	suspend		max_goal_slots_1_0
	module_entry		kl1cmp_normalize
	predicate		pack_body_goal,2
pack_body_goal_2_0:
	create_goal		4
	set_variable		1,4
	set_variable		2,3
	set_marked_value		3,1
	set_value		4,2
	enqueue_goal		4,pack_body_goal_4_0
	create_goal		3
	set_value		1,1
	set_void		2
	set_value		3,4
	enqueue_goal_external		kl1cmp_reader,functor,3
	put_value		1,3
	execute		1,max_goal_slots_1_0
pack_body_goal_2_1:
	suspend		pack_body_goal_2_0
	module_entry		kl1cmp_normalize
	predicate		pack_body_goal,4
pack_body_goal_4_0:
	try_me_else		pack_body_goal_4_1
	integer		1
	integer		2
	g_less_than		1,2
	get_value		3,4
	proceed
pack_body_goal_4_1:
	otherwise		pack_body_goal_4_0
	put_marked_value		5,2
	b_increment		5,5
	b_decrement		2,6
	b_subtract		1,6,1
	put_marked_value		6,1
	b_new_vector		6,6
	b_new_vector		5,5
	put_variable		7,8
	put_variable		10,9
	b_set_vector_element		7,2,7,10,10
	get_value		10,4
	create_goal		6
	set_integer		1,0
	set_values_dec		2,2,2
	set_variable		4,4
	set_value		5,6
	set_value		6,9
	enqueue_goal		6,copy_args_to_vect_6_0
	put_integer		1,0
	put_value		6,8
	execute		6,copy_args_of_goal_6_0
pack_body_goal_4_5:
	suspend		pack_body_goal_4_0
	module_entry		kl1cmp_normalize
	predicate		copy_args_of_goal,6
copy_args_of_goal_6_0:
	try_me_else		copy_args_of_goal_6_1
	wait_integer		2,0
	collect_value		1
	get_value		3,4
	get_value		5,6
	proceed
copy_args_of_goal_6_1:
	otherwise		copy_args_of_goal_6_0
	put_marked_value		7,1
	put_nil		8
	b_set_vector_element		3,7,3,8,7
	b_set_vector_element		5,1,3,3,5
	b_increment		1,1
	b_decrement		2,2
	put_value		3,7
	execute		6,copy_args_of_goal_6_0
copy_args_of_goal_6_6:
	suspend		copy_args_of_goal_6_0
	module_entry		kl1cmp_normalize
	predicate		copy_args_to_vect,6
copy_args_to_vect_6_0:
	try_me_else		copy_args_to_vect_6_1
	wait_value		1,3
	collect_value		4
	collect_value		1
	collect_value		2
	collect_value		3
	get_value		5,6
	proceed
copy_args_to_vect_6_1:
	otherwise		copy_args_to_vect_6_0
	put_marked_value		7,2
	b_increment		7,7
	put_marked_value		8,1
	b_increment		8,8
	put_marked_value		9,4
	put_nil		10
	b_set_vector_element		9,2,2,10,9
	b_set_vector_element		5,1,1,2,5
	put_values_dec		1,8,2
	execute		6,copy_args_to_vect_6_0
copy_args_to_vect_6_3:
	suspend		copy_args_to_vect_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_body_one_by_one,7
normalize_body_one_by_one_7_0:
	try_me_else		normalize_body_one_by_one_7_1
	wait_nil		6
	wait_list_var_var		7,6,8
	collect_list		7
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,7
	get_vector_value		3,10
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,9
	set_value		5,5
	set_nil		6
	set_value		7,8
	enqueue_goal		7,normalize_body_one_by_one_7_0
	put_value		2,3
	put_value		3,7
	put_value		5,9
	execute		6,normalize_both_body_6_0
normalize_body_one_by_one_7_1:
	otherwise		normalize_body_one_by_one_7_0
	try_me_else		normalize_body_one_by_one_7_6
	wait_nil		6
	put_value		6,7
	execute		6,normalize_last_both_body_6_0
normalize_body_one_by_one_7_6:
	otherwise		normalize_body_one_by_one_7_0
	create_goal		7
	set_variable		1,9
	set_values_inc		2,2,2
	set_variable		4,8
	set_value		5,5
	set_nil		6
	set_value		7,7
	enqueue_goal		7,normalize_body_one_by_one_7_0
	put_value		2,9
	put_value		3,4
	put_value		4,8
	put_value		5,6
	execute		5,concatenate_5_0
normalize_body_one_by_one_7_11:
	suspend		normalize_body_one_by_one_7_0
	module_entry		kl1cmp_normalize
	predicate		normalize_both_body,6
normalize_both_body_6_0:
	try_me_else		normalize_both_body_6_1
	jump_on_non_atom		6,normalize_both_body_6_3
	test_atom		6,true,normalize_both_body_6_1
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
normalize_both_body_6_3:
	check_vector		6,3,normalize_both_body_6_1
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,normalize_both_body_6_1
	bucket_entry_a		:=,normalize_both_body_6_5
	bucket_entry_a		=,normalize_both_body_6_6
normalize_both_body_6_5:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_values_inc		6,8,2
	execute		7,normalize_body_becomes_7_0
normalize_both_body_6_6:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_values_inc		6,8,2
	execute		7,normalize_body_unify_7_0
normalize_both_body_6_1:
	otherwise		normalize_both_body_6_0
	create_goal		10
	set_values_inc		1,1,5
	set_variable		6,5
	set_marked_value		7,6
	set_variable		8,2
	set_variable		9,3
	set_variable		10,4
	enqueue_goal		10,normalize_on_type_10_0
	put_value		1,6
	execute_external		kl1cmp_blttbl,active_builtin,5
normalize_both_body_6_14:
	suspend		normalize_both_body_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_on_type,10
normalize_on_type_10_0:
	try_me_else		normalize_on_type_10_1
	atom		6
	branch_on_atom		6,2,normalize_on_type_10_1
	bucket_entry_a		builtin,normalize_on_type_10_3
	bucket_entry_a		none,normalize_on_type_10_4
normalize_on_type_10_3:
	collect_value		7
	put_vector		6,2
	write_element_variable		6,0,11
	write_element_variable		6,1,7
	get_vector_value		3,6
	put_func		3,2,blt
	write_element_value		3,1,8
	put_list_val_var		6,3,8
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,11
	set_value		4,8
	set_value		5,5
	set_value		6,10
	enqueue_goal		6,normalize_body_args_6_0
	put_value		2,3
	put_value		3,7
	put_value		5,6
	put_value		6,9
	execute		6,normalize_body_args_6_0
normalize_on_type_10_4:
	collect_value		10
	collect_value		9
	collect_value		8
	put_value		6,7
	execute		6,normalize_body_goal_6_0
normalize_on_type_10_1:
	suspend		normalize_on_type_10_0
	module_entry		kl1cmp_normalize
	predicate		normalize_last_both_body,6
normalize_last_both_body_6_0:
	try_me_else		normalize_last_both_body_6_1
	jump_on_non_atom		6,normalize_last_both_body_6_3
	test_atom		6,true,normalize_last_both_body_6_1
	get_nil		3
	get_value		1,2
	put_list		1
	write_car_atom		1,proceed
	write_cdr_value		1,5
	get_list_value		4,1
	proceed
normalize_last_both_body_6_3:
	check_vector		6,3,normalize_last_both_body_6_1
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,normalize_last_both_body_6_1
	bucket_entry_a		:=,normalize_last_both_body_6_5
	bucket_entry_a		=,normalize_last_both_body_6_6
normalize_last_both_body_6_5:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_list		6
	write_car_atom		6,proceed
	write_cdr_value		6,5
	put_value		5,6
	put_values_inc		6,8,2
	execute		7,normalize_body_becomes_7_0
normalize_last_both_body_6_6:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_list		6
	write_car_atom		6,proceed
	write_cdr_value		6,5
	put_value		5,6
	put_values_inc		6,8,2
	execute		7,normalize_body_unify_7_0
normalize_last_both_body_6_1:
	otherwise		normalize_last_both_body_6_0
	create_goal		10
	set_values_inc		1,1,5
	set_variable		6,5
	set_marked_value		7,6
	set_variable		8,2
	set_variable		9,3
	set_variable		10,4
	enqueue_goal		10,normalize_last_on_type_10_0
	put_value		1,6
	execute_external		kl1cmp_blttbl,active_builtin,5
normalize_last_both_body_6_14:
	suspend		normalize_last_both_body_6_0
	module_entry		kl1cmp_normalize
	predicate		normalize_last_on_type,10
normalize_last_on_type_10_0:
	try_me_else		normalize_last_on_type_10_1
	atom		6
	branch_on_atom		6,2,normalize_last_on_type_10_1
	bucket_entry_a		builtin,normalize_last_on_type_10_3
	bucket_entry_a		none,normalize_last_on_type_10_4
normalize_last_on_type_10_3:
	collect_value		7
	put_vector		6,2
	write_element_variable		6,0,11
	write_element_variable		6,1,7
	get_vector_value		3,6
	put_func		3,2,blt
	write_element_value		3,1,8
	put_list_val_var		6,3,8
	put_list		3
	write_car_atom		3,proceed
	write_cdr_value		3,5
	create_goal		6
	set_variable		1,5
	set_value		2,2
	set_value		3,11
	set_value		4,8
	set_value		5,3
	set_value		6,10
	enqueue_goal		6,normalize_body_args_6_0
	put_value		2,5
	put_value		3,7
	put_value		5,6
	put_value		6,9
	execute		6,normalize_body_args_6_0
normalize_last_on_type_10_4:
	collect_value		10
	collect_value		9
	collect_value		8
	put_value		6,7
	execute		6,normalize_last_body_goal_6_0
normalize_last_on_type_10_1:
	suspend		normalize_last_on_type_10_0
	module_entry		kl1cmp_normalize
	predicate		variable_generator,3
variable_generator_3_0:
	try_me_else		variable_generator_3_1
	jump_on_non_list_var_var		3,variable_generator_3_3,6,4
	wait_vector		6,2
	read_element		6,0,5
	wait_atom		5,new_variable
	read_element		6,1,5
	collect_list		3
	collect_vector		6
	put_func		3,3,'$VAR'
	write_element_marked_value		3,1,1
	write_element_variable		3,2,6
	get_vector_value		5,3
	b_increment		1,3
	put_structured_constant		5,'$SCNST_24'
	put_variable		8,7
	b_append_string		5,8,5
	get_value		5,6
	create_goal		3
	set_values_dec		1,3,2
	set_value		3,4
	enqueue_goal		3,variable_generator_3_0
	put_value		2,7
	execute		2,convert_integer_to_string_2_0
variable_generator_3_3:
	check_nil		3,variable_generator_3_1
	get_value		1,2
	proceed
variable_generator_3_1:
	suspend		variable_generator_3_0
	module_entry		kl1cmp_normalize
	predicate		convert_integer_to_string,2
convert_integer_to_string_2_0:
	try_me_else		convert_integer_to_string_2_1
	integer		1
	put_integer		3,10
	g_less_than		1,3
	put_structured_constant		3,'$SCNST_25'
	put_integer		4,1
	b_substring		3,1,4,3,1
	get_value		3,2
	proceed
convert_integer_to_string_2_1:
	otherwise		convert_integer_to_string_2_0
	put_marked_value		3,1
	put_integer		4,10
	b_modulo		3,4,3
	put_integer		4,10
	b_divide		1,4,1
	put_structured_constant		4,'$SCNST_26'
	put_integer		5,1
	b_substring		4,3,5,3,4
	put_variable		5,4
	b_append_string		5,3,3
	get_value		3,2
	put_value		2,4
	execute		2,convert_integer_to_string_2_0
convert_integer_to_string_2_5:
	suspend		convert_integer_to_string_2_0
	begin_const_section		kl1cmp_normalize
'$SCNST_0_0':
	define_desc		27,11
	define_integer		661545283
	define_integer		1919098996
	define_integer		1702125925
	define_integer		1920234272
	define_integer		1970561909
	define_integer		1763730802
	define_integer		1752440942
	define_integer		1969692773
	define_integer		543453793
	define_integer		1953653104
	define_integer		46
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		3,17
	define_integer		543516756
	define_integer		1936877926
	define_integer		1635131508
	define_integer		1650551154
	define_integer		1864394092
	define_integer		1702240358
	define_integer		1919906915
	define_integer		1701602655
	define_integer		1953391981
	define_integer		1937075488
	define_integer		1700929652
	define_integer		1444962592
	define_integer		1634300513
	define_integer		543517794
	define_integer		1629516399
	define_integer		1667585568
	define_integer		544370548
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		11,7
	define_integer		1818324807
	define_integer		1953459744
	define_integer		1819042080
	define_integer		1684371311
	define_integer		544106784
	define_integer		1918989671
	define_integer		3809380
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		11,8
	define_integer		1918989639
	define_integer		1869029476
	define_integer		1847618657
	define_integer		2032170095
	define_integer		1763734629
	define_integer		1701605485
	define_integer		1953391981
	define_integer		3040357
'$SCNST_3':
	define_string		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		27,8
	define_integer		1936287828
	define_integer		1635084064
	define_integer		1965057138
	define_integer		1768319342
	define_integer		1769234787
	define_integer		1713401455
	define_integer		1936484705
	define_integer		46
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		27,11
	define_integer		1936287828
	define_integer		1635084064
	define_integer		1965057138
	define_integer		1768319342
	define_integer		1769234787
	define_integer		1713401455
	define_integer		1936484705
	define_integer		544370464
	define_integer		1886614899
	define_integer		1935961701
	define_integer		46
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_6_0':
	define_desc		27,9
	define_integer		1952867660
	define_integer		1851877408
	define_integer		1769152612
	define_integer		1763730788
	define_integer		1027219566
	define_integer		544434464
	define_integer		1701604457
	define_integer		543973735
	define_integer		58
'$SCNST_18':
'$SCNST_6':
	define_string		'$SCNST_6_0'
'$SCNST_7_0':
	define_desc		19,9
	define_integer		1952867660
	define_integer		1851877408
	define_integer		1769152612
	define_integer		1763730788
	define_integer		975446126
	define_integer		1936269373
	define_integer		1819044128
	define_integer		1818322789
	define_integer		14880
'$SCNST_19':
'$SCNST_7':
	define_string		'$SCNST_7_0'
'$SCNST_8_0':
	define_desc		27,13
	define_integer		1635151433
	define_integer		543451500
	define_integer		1701869940
	define_integer		1735549216
	define_integer		543584032
	define_integer		1752457581
	define_integer		1952542053
	define_integer		1818321769
	define_integer		1769300512
	define_integer		1852404844
	define_integer		1732845614
	define_integer		1701998446
	define_integer		100
'$SCNST_9':
'$SCNST_8':
	define_string		'$SCNST_8_0'
'$SCNST_10_0':
	define_desc		11,11
	define_integer		1635151433
	define_integer		543451500
	define_integer		1701869940
	define_integer		1735549216
	define_integer		543584032
	define_integer		1769108595
	define_integer		1646290798
	define_integer		1953261941
	define_integer		539913833
	define_integer		1869506377
	define_integer		6579570
'$SCNST_10':
	define_string		'$SCNST_10_0'
'$SCNST_11_0':
	define_desc		11,11
	define_integer		1635151433
	define_integer		543451500
	define_integer		1701869940
	define_integer		1735549216
	define_integer		543584032
	define_integer		1952671094
	define_integer		1646293615
	define_integer		1953261941
	define_integer		539913833
	define_integer		1869506377
	define_integer		6579570
'$SCNST_11':
	define_string		'$SCNST_11_0'
'$SCNST_12_0':
	define_desc		3,10
	define_integer		543516756
	define_integer		1969713761
	define_integer		1953391981
	define_integer		1718558835
	define_integer		1768453152
	define_integer		1768169587
	define_integer		1763731046
	define_integer		1869488243
	define_integer		1635131508
	define_integer		979659116
'$SCNST_15':
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_13_0':
	define_desc		3,13
	define_integer		1936287828
	define_integer		1953459744
	define_integer		1768846624
	define_integer		1701734758
	define_integer		1701716068
	define_integer		544367990
	define_integer		1667462515
	define_integer		779318117
	define_integer		1885696544
	define_integer		1702060396
	define_integer		1769414756
	define_integer		1713399924
	define_integer		980183393
'$SCNST_13':
	define_string		'$SCNST_13_0'
'$SCNST_14_0':
	define_desc		0,2
	define_atom		builtin
	define_atom		fail
'$SCNST_16':
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_17_0':
	define_desc		19,8
	define_integer		1936287828
	define_integer		1718182944
	define_integer		1701716070
	define_integer		544367990
	define_integer		1818845542
	define_integer		1732845614
	define_integer		1701998446
	define_integer		14948
'$SCNST_17':
	define_string		'$SCNST_17_0'
'$SCNST_20_0':
	define_desc		11,8
	define_integer		1869771333
	define_integer		1852383346
	define_integer		1634889760
	define_integer		543255911
	define_integer		1667592307
	define_integer		1768318569
	define_integer		1769234787
	define_integer		3829359
'$SCNST_20':
	define_string		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		3,10
	define_integer		1869771333
	define_integer		1668227186
	define_integer		1701999971
	define_integer		1852383332
	define_integer		1769107488
	define_integer		1953067631
	define_integer		1886593145
	define_integer		1718182757
	define_integer		1952539497
	define_integer		980316009
'$SCNST_21':
	define_string		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		11,8
	define_integer		2036625218
	define_integer		1634690848
	define_integer		1869488236
	define_integer		1702436980
	define_integer		1835606132
	define_integer		1835363440
	define_integer		1702129253
	define_integer		3809380
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_23_0':
	define_desc		19,8
	define_integer		2036625218
	define_integer		1634690848
	define_integer		1869488236
	define_integer		1702436980
	define_integer		1835606132
	define_integer		1835363440
	define_integer		1702129253
	define_integer		11876
'$SCNST_23':
	define_string		'$SCNST_23_0'
'$SCNST_24_0':
	define_desc		19,2
	define_integer		1450075463
	define_integer		29281
'$SCNST_24':
	define_string		'$SCNST_24_0'
'$SCNST_25_0':
	define_desc		19,3
	define_integer		858927408
	define_integer		926299444
	define_integer		14648
'$SCNST_26':
'$SCNST_25':
	define_string		'$SCNST_25_0'
