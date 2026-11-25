kl1cmp_compile:
	module		kl1cmp_compile
	entry		compile_one_clause,17,compile_one_clause_17_0
	module_entry		kl1cmp_compile
	predicate		compile_one_clause,17
compile_one_clause_17_0:
	put_func		20,3,-
	write_element_variable		20,1,19
	write_element_variable		20,2,18
	get_vector_value		14,20
	create_goal		4
	set_variable		1,14
	set_value		2,9
	set_value		3,11
	set_value		4,13
	enqueue_goal		4,devide_tabs_4_0
	create_goal		11
	set_variable		1,21
	set_value		2,2
	set_variable		3,20
	set_value		4,4
	set_variable		5,11
	set_value		6,14
	set_marked_variable		7,9
	set_value		8,16
	set_variable		9,13
	set_value		10,18
	put_list		2
	write_car_atom		2,commit
	write_cdr_variable		2,4
	set_value		11,2
	enqueue_goal		11,compile_body_11_0
	create_goal		6
	set_variable		1,2
	set_value		2,11
	set_variable		3,11
	set_value		4,19
	set_marked_value		5,15
	set_value		6,9
	enqueue_goal		6,set_guard_arg_ref_count_6_0
	create_goal		3
	set_value		1,15
	set_integer		2,0
	set_value		3,13
	enqueue_goal_external		kl1cmp_reader,herrey,3
	create_goal		3
	set_value		1,15
	set_integer		2,0
	set_value		3,11
	enqueue_goal_external		kl1cmp_reader,herrey,3
	create_goal		5
	set_variable		1,16
	set_value		2,2
	set_marked_variable		3,14
	set_marked_variable		4,11
	set_variable		5,2
	enqueue_goal		5,keep_head_arguments_5_0
	create_goal		12
	set_variable		1,13
	set_value		2,21
	set_value		3,3
	set_value		4,20
	set_variable		5,3
	set_value		6,16
	set_integer		7,1
	set_value		8,9
	set_integer		9,1
	set_value		10,2
	put_list		2
	write_car_atom		2,try_me_else
	write_cdr_variable		2,9
	set_value		11,2
	set_value		12,7
	enqueue_goal		12,compile_guard_12_0
	create_goal		5
	put_func		2,3,-
	write_element_value		2,1,8
	write_element_value		2,2,10
	put_func		7,3,-
	write_element_value		7,1,2
	write_element_value		7,2,12
	set_value		1,7
	set_value		2,3
	set_value		3,14
	set_value		4,11
	set_integer		5,0
	enqueue_goal		5,initiate_head_arguments_5_0
	create_goal		3
	set_value		1,11
	set_void		2
	set_value		3,14
	enqueue_goal_external		kl1cmp_reader,functor,3
	create_goal		3
	set_value		1,15
	set_nil		2
	set_variable		3,2
	enqueue_goal_external		kl1cmp_reader,herrey,3
	create_goal		11
	set_value		1,1
	set_value		2,13
	set_value		3,5
	set_marked_value		4,6
	set_variable		5,3
	set_value		6,15
	set_value		7,11
	set_value		8,9
	set_value		9,4
	set_value		10,2
	set_value		11,17
	enqueue_goal_external		kl1cmp_normalize,normalize,11
	put_value		1,6
	put_integer		2,0
	execute_external		kl1cmp_reader,count_variables,3
compile_one_clause_17_1:
	suspend		compile_one_clause_17_0
	module_entry		kl1cmp_compile
	predicate		devide_tabs,4
devide_tabs_4_0:
	try_me_else		devide_tabs_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,8
	read_element		1,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,-
	read_elements_inc		8,1,6,2
	collect_vector		1
	collect_vector		8
	get_value		6,2
	get_value		7,3
	get_value		5,4
	proceed
devide_tabs_4_1:
	suspend		devide_tabs_4_0
	module_entry		kl1cmp_compile
	predicate		initiate_head_arguments,5
initiate_head_arguments_5_0:
	try_me_else		initiate_head_arguments_5_1
	integer		3
	test_integer		3,0,initiate_head_arguments_5_3
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
initiate_head_arguments_5_3:
	put_integer		6,0
	g_less_than		6,3
	put_marked_value		6,3
	put_marked_variable		8,7
	b_set_vector_element		4,6,6,8,4
	get_value		6,7
	b_decrement		3,6
	create_goal		5
	set_variable		1,8
	set_value		2,2
	set_value		3,6
	set_value		4,4
	set_marked_value		5,5
	enqueue_goal		5,initiate_head_arguments_5_0
	create_goal		4
	set_variable		1,2
	set_values_dec		2,8,2
	set_value		4,3
	enqueue_goal		4,usereg_4_0
	put_value		3,7
	put_value		4,5
	execute		4,newvar_4_0
initiate_head_arguments_5_1:
	suspend		initiate_head_arguments_5_0
	module_entry		kl1cmp_compile
	predicate		'$keep_head_arguments/3_0',5
'$keep_head_arguments/3_0_5_0':
	try_me_else		'$keep_head_arguments/3_0_5_1'
	integer		3
	integer		5
	try_me_else		'$keep_head_arguments/3_0_5_4'
	g_less_than		5,3
	put_value		6,3
	put_value		3,4
	put_value		4,6
	execute		4,refvar_4_0
'$keep_head_arguments/3_0_5_4':
	collect_value		4
	get_value		1,2
	proceed
'$keep_head_arguments/3_0_5_1':
	suspend		'$keep_head_arguments/3_0_5_0'
	module_entry		kl1cmp_compile
	predicate		keep_head_arguments,5
keep_head_arguments_5_0:
	try_me_else		keep_head_arguments_5_1
	integer		3
	test_integer		3,0,keep_head_arguments_5_3
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
keep_head_arguments_5_3:
	put_integer		6,0
	g_less_than		6,3
	put_marked_value		7,3
	put_marked_variable		8,6
	b_set_vector_element		4,7,7,8,4
	get_value		7,6
	b_decrement		3,3
	create_goal		5
	set_variable		1,7
	set_values_inc		2,2,3
	set_marked_value		5,5
	enqueue_goal		5,keep_head_arguments_5_0
	create_goal		5
	set_variable		1,2
	set_value		2,7
	set_values_inc		3,5,2
	set_variable		5,4
	enqueue_goal		5,'$keep_head_arguments/3_0_5_0'
	put_value		3,6
	execute		4,ref_to_table_4_0
keep_head_arguments_5_1:
	suspend		keep_head_arguments_5_0
	module_entry		kl1cmp_compile
	predicate		ref_to_table,4
ref_to_table_4_0:
	try_me_else		ref_to_table_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,10
	read_element		1,2,5
	wait_vector		10,3
	read_element		10,0,6
	wait_atom		6,-
	read_elements_inc		10,1,6,2
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	collect_value		9
	collect_vector		3
	put_marked_value		3,4
	b_set_vector_element		7,8,7,3,3
	get_value		7,4
	put_reused_func		1,1,-
	write_element_value		1,1,6
	write_element_value		1,2,3
	put_reused_func		3,10,-
	write_element_value		3,1,1
	write_element_value		3,2,5
	get_vector_value		2,3
	proceed
ref_to_table_4_1:
	suspend		ref_to_table_4_0
	module_entry		kl1cmp_compile
	predicate		'$set_guard_arg_ref_count/2_1',7
'$set_guard_arg_ref_count/2_1_7_0':
	try_me_else		'$set_guard_arg_ref_count/2_1_7_1'
	integer		5
	integer		7
	try_me_else		'$set_guard_arg_ref_count/2_1_7_4'
	g_less_than		7,5
	get_value		1,2
	put_values_inc		1,3,2
	put_value		3,6
	execute		3,set_pass_tbl_3_0
'$set_guard_arg_ref_count/2_1_7_4':
	collect_value		6
	get_value		3,4
	get_value		1,2
	proceed
'$set_guard_arg_ref_count/2_1_7_1':
	try_me_else		'$set_guard_arg_ref_count/2_1_7_5'
	wait_nil		7
	collect_value		6
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
'$set_guard_arg_ref_count/2_1_7_5':
	suspend		'$set_guard_arg_ref_count/2_1_7_0'
	module_entry		kl1cmp_compile
	predicate		set_guard_arg_ref_count,6
set_guard_arg_ref_count_6_0:
	try_me_else		set_guard_arg_ref_count_6_1
	integer		5
	test_integer		5,0,set_guard_arg_ref_count_6_3
	collect_value		6
	get_value		3,4
	get_value		1,2
	proceed
set_guard_arg_ref_count_6_3:
	put_integer		7,0
	g_less_than		7,5
	b_decrement		5,5
	create_goal		6
	set_variable		1,8
	set_value		2,2
	set_variable		3,7
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	enqueue_goal		6,set_guard_arg_ref_count_6_0
	create_goal		7
	set_variable		1,2
	set_value		2,8
	set_value		3,3
	set_values_dec		4,7,3
	set_variable		7,4
	enqueue_goal		7,'$set_guard_arg_ref_count/2_1_7_0'
	put_value		3,5
	execute		4,get_From_PC_4_0
set_guard_arg_ref_count_6_1:
	suspend		set_guard_arg_ref_count_6_0
	module_entry		kl1cmp_compile
	predicate		compile_guard,12
compile_guard_12_0:
	try_me_else		compile_guard_12_1
	jump_on_non_list_var_var		11,compile_guard_12_3,13,14
	collect_list		11
	create_goal		12
	set_variable		1,18
	set_value		2,2
	set_variable		3,17
	set_value		4,4
	set_variable		5,16
	set_value		6,6
	set_variable		7,15
	set_value		8,8
	set_variable		9,11
	set_value		10,10
	set_value		11,14
	set_marked_value		12,12
	enqueue_goal		12,compile_guard_12_0
	put_value		2,18
	put_value		4,17
	put_value		6,16
	put_value		8,15
	put_value		10,11
	put_value		11,13
	execute		12,compile_guard_goal_12_0
compile_guard_12_3:
	check_nil		11,compile_guard_12_1
	collect_value		12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_guard_12_1:
	suspend		compile_guard_12_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_goal,12
compile_guard_goal_12_0:
	try_me_else		compile_guard_goal_12_1
	jump_on_non_atom		11,compile_guard_goal_12_3
	test_atom		11,try_me_else,compile_guard_goal_12_1
	collect_value		9
	put_marked_value		7,7
	get_value		7,10
	get_value		5,6
	get_value		1,2
	put_func		5,2,try_me_else
	write_element_value		5,1,12
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_guard_goal_12_3:
	is_vector		11,compile_guard_goal_12_1
	jump_on_arity		11,4,compile_guard_goal_12_1
	table_entry		compile_guard_goal_12_1
	table_entry		compile_guard_goal_12_1
	table_entry		compile_guard_goal_12_4
	table_entry		compile_guard_goal_12_5
compile_guard_goal_12_4:
	read_element		11,0,13
	atom		13
	hash_on_atom		13,8,compile_guard_goal_12_1
	bucket_entry_a		builtin,compile_guard_goal_12_7
	bucket_entry_a		draw,compile_guard_goal_12_8
	bucket_entry_a		float,compile_guard_goal_12_9
	bucket_entry_a		integer,compile_guard_goal_12_10
	bucket_entry_a		string,compile_guard_goal_12_11
	bucket_entry_a		unify,compile_guard_goal_12_12
	bucket_entry_a		vector,compile_guard_goal_12_13
	bucket_entry_a		wait,compile_guard_goal_12_14
compile_guard_goal_12_7:
	read_element		11,1,14
	jump_on_non_atom		14,compile_guard_goal_12_16
	collect_value		12
	collect_value		9
	put_marked_value		7,7
	get_value		7,10
	get_value		5,6
	get_value		1,2
	put_reused_func		5,11,builtin
	write_element_value		5,1,14
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_guard_goal_12_16:
	is_vector		14,compile_guard_goal_12_1
	test_arity		14,4,compile_guard_goal_12_17
	try_me_else		compile_guard_goal_12_17
	read_element		14,0,15
	wait_atom		15,vector_element
	read_element		14,1,13
	read_elements_inc		14,2,15,2
	collect_value		12
	collect_value		9
	put_marked_value		7,7
	get_value		7,10
	get_value		1,2
	put_marked_variable		1,9
	b_increment		1,1
	create_goal		5
	set_values_inc		1,3,2
	set_values_dec		3,9,2
	put_reused_func		2,14,vector_element
	write_element_marked_value		2,1,13
	write_element_marked_value		2,2,15
	write_element_marked_value		2,3,16
	put_reused_func		3,11,builtin
	write_element_value		3,1,2
	set_value		5,3
	enqueue_goal		5,gen_5_0
	create_goal		6
	set_variable		1,2
	set_value		2,6
	set_value		3,1
	set_void		4
	set_value		5,15
	set_void		6
	enqueue_goal		6,how_do_you_do_6_0
	put_func		6,4,vector_element
	write_element_value		6,1,13
	write_elements_inc		6,2,15,2
	put_value		1,5
	put_value		3,7
	put_value		4,9
	put_integer		5,4
	execute		6,set_life_time_6_0
compile_guard_goal_12_17:
	try_me_else		compile_guard_goal_12_1
	g_vector		14,15
	put_integer		16,0
	g_vector_element		14,16,16
	put_atom		17,vector_element
	g_diff		16,17
	collect_value		12
	collect_value		9
	put_marked_value		7,7
	get_value		7,10
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_variable		3,4
	set_value		4,8
	put_reused_func		1,11,builtin
	write_element_marked_value		1,1,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	put_values_inc		1,5,3
	put_values_dec		5,15,2
	execute		6,set_life_time_6_0
compile_guard_goal_12_8:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_draw_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_foo_6_0
compile_guard_goal_12_9:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_float_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_10:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_integer_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_11:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_string_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_12:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_passive_unify_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_foo_6_0
compile_guard_goal_12_13:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_vector_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_14:
	read_element		11,1,14
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,12
	enqueue_goal		11,compile_guard_wait_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_5:
	read_element		11,0,13
	wait_atom		13,=
	read_elements_inc		11,1,13,2
	collect_vector		11
	create_goal		13
	set_values_inc		1,1,4
	set_variable		5,3
	set_values_inc		6,8,3
	set_variable		9,8
	set_marked_value		10,13
	set_marked_value		11,14
	set_variable		12,1
	set_value		13,12
	enqueue_goal		13,compile_get_valuable_13_0
	create_goal		6
	set_variable		1,2
	set_value		2,6
	set_variable		3,4
	set_value		4,3
	set_value		5,14
	set_value		6,1
	enqueue_goal		6,how_do_you_foo_6_0
	put_value		1,5
	put_value		3,7
	put_value		5,13
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_guard_goal_12_1:
	suspend		compile_guard_goal_12_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_integer,11
compile_guard_integer_11_0:
	try_me_else		compile_guard_integer_11_1
	jump_on_non_integer		9,compile_guard_integer_11_3
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_guard_integer_11_3:
	check_vector		9,3,compile_guard_integer_11_1
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	collect_value		11
	collect_value		7
	put_value		7,5
	create_goal		5
	set_variable		1,5
	set_value		2,4
	set_variable		3,11
	set_value		4,6
	put_reused_func		4,9,'$VAR'
	write_elements_inc		4,1,12,2
	put_func		6,2,integer
	write_element_value		6,1,4
	set_value		5,6
	enqueue_goal		5,gen_5_0
	put_value		4,5
	put_marked_value		5,7
	put_value		6,11
	put_value		9,10
	execute		9,maybe_suspend_forever_9_0
compile_guard_integer_11_1:
	suspend		compile_guard_integer_11_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_float,11
compile_guard_float_11_0:
	try_me_else		compile_guard_float_11_1
	jump_on_non_vector		9,compile_guard_float_11_3
	test_arity		9,3,compile_guard_float_11_1
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	collect_value		11
	collect_value		7
	put_value		7,5
	create_goal		5
	set_variable		1,5
	set_value		2,4
	set_variable		3,11
	set_value		4,6
	put_reused_func		4,9,'$VAR'
	write_elements_inc		4,1,12,2
	put_func		6,2,float
	write_element_value		6,1,4
	set_value		5,6
	enqueue_goal		5,gen_5_0
	put_value		4,5
	put_marked_value		5,7
	put_value		6,11
	put_value		9,10
	execute		9,maybe_suspend_forever_9_0
compile_guard_float_11_3:
	is_float		9,compile_guard_float_11_1
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_guard_float_11_1:
	suspend		compile_guard_float_11_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_vector,11
compile_guard_vector_11_0:
	try_me_else		compile_guard_vector_11_1
	wait_vector		9,3
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	collect_value		11
	collect_value		7
	put_value		7,5
	create_goal		5
	set_variable		1,5
	set_value		2,4
	set_variable		3,11
	set_value		4,6
	put_reused_func		4,9,'$VAR'
	write_elements_inc		4,1,12,2
	put_func		6,2,vector
	write_element_value		6,1,4
	set_value		5,6
	enqueue_goal		5,gen_5_0
	put_value		4,5
	put_marked_value		5,7
	put_value		6,11
	put_value		9,10
	execute		9,maybe_suspend_forever_9_0
compile_guard_vector_11_1:
	suspend		compile_guard_vector_11_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_string,11
compile_guard_string_11_0:
	try_me_else		compile_guard_string_11_1
	vector		9
	jump_on_arity		9,4,compile_guard_string_11_1
	table_entry		compile_guard_string_11_1
	table_entry		compile_guard_string_11_1
	table_entry		compile_guard_string_11_3
	table_entry		compile_guard_string_11_4
compile_guard_string_11_3:
	read_element		9,0,12
	wait_atom		12,'$SCNST'
	read_element		9,1,12
	collect_value		11
	collect_value		10
	collect_value		12
	collect_vector		9
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_guard_string_11_4:
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	collect_value		11
	collect_value		7
	put_value		7,5
	create_goal		5
	set_variable		1,5
	set_value		2,4
	set_variable		3,11
	set_value		4,6
	put_reused_func		4,9,'$VAR'
	write_elements_inc		4,1,12,2
	put_func		6,2,string
	write_element_value		6,1,4
	set_value		5,6
	enqueue_goal		5,gen_5_0
	put_value		4,5
	put_marked_value		5,7
	put_value		6,11
	put_value		9,10
	execute		9,maybe_suspend_forever_9_0
compile_guard_string_11_1:
	suspend		compile_guard_string_11_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_wait,11
compile_guard_wait_11_0:
	try_me_else		compile_guard_wait_11_1
	wait_vector		9,3
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	collect_value		11
	collect_value		7
	put_value		7,5
	create_goal		5
	set_variable		1,5
	set_value		2,4
	set_variable		3,11
	set_value		4,6
	put_reused_func		4,9,'$VAR'
	write_elements_inc		4,1,12,2
	put_func		6,2,wait
	write_element_value		6,1,4
	set_value		5,6
	enqueue_goal		5,gen_5_0
	put_value		4,5
	put_marked_value		5,7
	put_value		6,11
	put_value		9,10
	execute		9,maybe_suspend_forever_9_0
compile_guard_wait_11_1:
	otherwise		compile_guard_wait_11_0
	collect_value		11
	collect_value		10
	collect_value		9
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_guard_wait_11_6:
	suspend		compile_guard_wait_11_0
	module_entry		kl1cmp_compile
	predicate		maybe_suspend_forever,9
maybe_suspend_forever_9_0:
	try_me_else		maybe_suspend_forever_9_1
	jump_on_non_atom		9,maybe_suspend_forever_9_3
	test_nil		9,maybe_suspend_forever_9_1
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_structured_constant		3,'$SCNST_0'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
maybe_suspend_forever_9_3:
	is_integer		9,maybe_suspend_forever_9_1
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
maybe_suspend_forever_9_1:
	suspend		maybe_suspend_forever_9_0
	module_entry		kl1cmp_compile
	predicate		compile_get_valuable,13
compile_get_valuable_13_0:
	try_me_else		compile_get_valuable_13_1
	jump_on_non_atom		9,compile_get_valuable_13_3
	test_nil		9,compile_get_valuable_13_1
	collect_value		13
	put_value		13,10
	put_values_inc		9,11,3
	execute		11,compile_get_variable_11_0
compile_get_valuable_13_3:
	is_integer		9,compile_get_valuable_13_1
	put_value		14,10
	put_values_inc		9,11,2
	put_values_dec		11,14,2
	execute		12,compile_get_value_12_0
compile_get_valuable_13_1:
	suspend		compile_get_valuable_13_0
	module_entry		kl1cmp_compile
	predicate		compile_get_variable,11
compile_get_variable_11_0:
	try_me_else		compile_get_variable_11_1
	jump_on_non_atom		9,compile_get_variable_11_3
	test_atom		9,list,compile_get_variable_11_1
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_list		3
	write_car_value		3,11
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_1'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
compile_get_variable_11_3:
	check_vector		9,2,compile_get_variable_11_1
	read_element		9,0,12
	atom		12
	hash_on_atom		12,4,compile_get_variable_11_1
	bucket_entry_a		atomic,compile_get_variable_11_5
	bucket_entry_a		struct,compile_get_variable_11_6
	bucket_entry_a		var,compile_get_variable_11_7
	bucket_entry_a		vector,compile_get_variable_11_8
compile_get_variable_11_5:
	read_element		9,1,13
	collect_value		10
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_constant
	write_element_value		7,1,13
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_variable_11_6:
	read_element		9,1,13
	collect_value		10
	collect_vector		9
	get_value		7,8
	get_value		1,2
	b_intern_atom		1,13
	put_func		7,3,put_structured_constant
	write_element_value		7,1,1
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_variable_11_7:
	read_element		9,1,13
	jump_on_non_atom		10,compile_get_variable_11_10
	test_nil		10,compile_get_variable_11_1
	collect_vector		9
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_func		3,3,=
	write_element_value		3,1,11
	write_element_value		3,2,13
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_2'
	put_func		5,3,warning_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
compile_get_variable_11_10:
	is_integer		10,compile_get_variable_11_1
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_func		7,3,wait_variable
	write_element_value		7,1,11
	write_element_value		7,2,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_variable_11_8:
	read_element		9,1,13
	collect_value		10
	collect_value		13
	collect_vector		9
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_list		3
	write_car_value		3,11
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_3'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
compile_get_variable_11_1:
	otherwise		compile_get_variable_11_0
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_list		3
	write_car_value		3,9
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_4'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
compile_get_variable_11_22:
	suspend		compile_get_variable_11_0
	module_entry		kl1cmp_compile
	predicate		compile_get_value,12
compile_get_value_12_0:
	try_me_else		compile_get_value_12_1
	jump_on_non_atom		9,compile_get_value_12_3
	test_atom		9,list,compile_get_value_12_1
	collect_value		12
	collect_value		10
	collect_value		7
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_func		7,2,wait_list
	write_element_value		7,1,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_value_12_3:
	check_vector		9,2,compile_get_value_12_1
	read_element		9,0,13
	atom		13
	branch_on_atom		13,3,compile_get_value_12_1
	bucket_entry_a		atomic,compile_get_value_12_5
	bucket_entry_a		var,compile_get_value_12_6
	bucket_entry_a		vector,compile_get_value_12_7
compile_get_value_12_5:
	read_element		9,1,14
	collect_value		12
	collect_value		10
	collect_value		7
	collect_vector		9
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_func		7,3,wait_constant
	write_element_value		7,1,14
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_value_12_6:
	read_element		9,1,14
	jump_on_non_atom		10,compile_get_value_12_9
	test_nil		10,compile_get_value_12_1
	collect_value		12
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_func		7,3,wait_variable
	write_element_value		7,1,14
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_value_12_9:
	is_integer		10,compile_get_value_12_1
	collect_value		12
	collect_value		7
	collect_vector		9
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_func		7,3,wait_value
	write_element_value		7,1,11
	write_element_value		7,2,14
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_value_12_7:
	read_element		9,1,14
	collect_value		12
	collect_value		10
	collect_value		7
	collect_vector		9
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_func		7,3,wait_vector
	write_element_value		7,1,11
	write_element_value		7,2,14
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_get_value_12_1:
	suspend		compile_get_value_12_0
	module_entry		kl1cmp_compile
	predicate		compile_passive_unify,11
compile_passive_unify_11_0:
	try_me_else		compile_passive_unify_11_1
	wait_vector		9,2
	read_element		9,0,12
	atom		12
	branch_on_atom		12,2,compile_passive_unify_11_1
	bucket_entry_a		atomic,compile_passive_unify_11_4
	bucket_entry_a		var,compile_passive_unify_11_5
compile_passive_unify_11_4:
	read_element		9,1,13
	collect_value		11
	collect_value		10
	collect_value		7
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_reused_func		7,9,read_constant
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_passive_unify_11_5:
	read_element		9,1,13
	jump_on_non_atom		10,compile_passive_unify_11_7
	test_nil		10,compile_passive_unify_11_1
	collect_value		11
	get_value		7,8
	get_value		1,2
	put_reused_func		7,9,read_variable
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_passive_unify_11_7:
	is_integer		10,compile_passive_unify_11_1
	collect_value		11
	collect_value		7
	put_marked_value		5,5
	get_value		5,8
	get_value		1,2
	put_reused_func		7,9,read_value
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_passive_unify_11_1:
	suspend		compile_passive_unify_11_0
	module_entry		kl1cmp_compile
	predicate		compile_guard_draw,11
compile_guard_draw_11_0:
	try_me_else		compile_guard_draw_11_1
	wait_vector		9,2
	read_element		9,0,12
	atom		12
	branch_on_atom		12,2,compile_guard_draw_11_1
	bucket_entry_a		atomic,compile_guard_draw_11_4
	bucket_entry_a		var,compile_guard_draw_11_5
compile_guard_draw_11_4:
	read_element		9,1,13
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		1,2
	put_reused_func		7,9,write_constant
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_guard_draw_11_5:
	read_element		9,1,13
	try_me_else		compile_guard_draw_11_6
	wait_nil		10
	collect_value		11
	get_value		7,8
	get_value		1,2
	put_reused_func		7,9,write_variable
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_guard_draw_11_6:
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		1,2
	put_reused_func		7,9,write_value
	write_element_value		7,1,13
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_guard_draw_11_1:
	suspend		compile_guard_draw_11_0
	module_entry		kl1cmp_compile
	predicate		set_life_time,6
set_life_time_6_0:
	try_me_else		set_life_time_6_1
	integer		5
	test_integer		5,0,set_life_time_6_3
	collect_value		6
	get_value		3,4
	get_value		1,2
	proceed
set_life_time_6_3:
	put_integer		7,0
	g_less_than		7,5
	put_marked_variable		7,8
	put_nil		9
	b_set_vector_element		6,7,6,9,7
	b_decrement		5,5
	get_value		8,5
	create_goal		6
	set_variable		1,9
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_values_dec		5,8,2
	enqueue_goal		6,set_life_time_6_0
	put_value		2,9
	put_values_inc		4,5,2
	put_void		6
	execute		6,how_do_you_do_6_0
set_life_time_6_1:
	suspend		set_life_time_6_0
	module_entry		kl1cmp_compile
	predicate		compile_body,11
compile_body_11_0:
	try_me_else		compile_body_11_1
	jump_on_non_list_var_var		11,compile_body_11_3,12,13
	collect_list		11
	create_goal		11
	set_variable		1,17
	set_value		2,2
	set_variable		3,16
	set_value		4,4
	set_variable		5,15
	set_value		6,6
	set_variable		7,14
	set_value		8,8
	set_variable		9,11
	set_value		10,10
	set_value		11,13
	enqueue_goal		11,compile_body_11_0
	put_value		2,17
	put_value		4,16
	put_value		6,15
	put_value		8,14
	put_values_inc		10,11,2
	execute		11,compile_body_goal_11_0
compile_body_11_3:
	check_nil		11,compile_body_11_1
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_body_11_1:
	suspend		compile_body_11_0
	module_entry		kl1cmp_compile
	predicate		compile_body_goal,11
compile_body_goal_11_0:
	try_me_else		compile_body_goal_11_1
	jump_on_non_atom		11,compile_body_goal_11_3
	branch_on_atom		11,2,compile_body_goal_11_1
	bucket_entry_a		commit,compile_body_goal_11_4
	bucket_entry_a		proceed,compile_body_goal_11_5
compile_body_goal_11_4:
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	put_atom		5,commit
	execute		5,gen_5_0
compile_body_goal_11_5:
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	put_atom		5,proceed
	execute		5,gen_5_0
compile_body_goal_11_3:
	is_vector		11,compile_body_goal_11_1
	jump_on_arity		11,4,compile_body_goal_11_1
	table_entry		compile_body_goal_11_1
	table_entry		compile_body_goal_11_1
	table_entry		compile_body_goal_11_6
	table_entry		compile_body_goal_11_7
compile_body_goal_11_6:
	read_element		11,0,12
	atom		12
	hash_on_atom		12,5,compile_body_goal_11_1
	bucket_entry_a		blt,compile_body_goal_11_9
	bucket_entry_a		create_goal,compile_body_goal_11_10
	bucket_entry_a		draw,compile_body_goal_11_11
	bucket_entry_a		enqueue_goal,compile_body_goal_11_12
	bucket_entry_a		execute,compile_body_goal_11_13
compile_body_goal_11_9:
	read_element		11,1,13
	jump_on_non_atom		13,compile_body_goal_11_15
	collect_vector		11
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
compile_body_goal_11_15:
	is_vector		13,compile_body_goal_11_1
	g_vector		13,12
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_variable		3,4
	set_value		4,8
	put_reused_func		1,11,builtin
	write_element_marked_value		1,1,13
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		4
	set_values_inc		1,9,2
	set_marked_value		3,12
	set_value		4,13
	enqueue_goal		4,set_mrb_body_ref_4_0
	put_values_inc		1,5,3
	put_values_inc		5,12,2
	execute		6,set_life_time_6_0
compile_body_goal_11_10:
	read_element		11,1,13
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_reused_func		5,11,create_goal
	write_element_value		5,1,13
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_body_goal_11_11:
	read_element		11,1,13
	collect_vector		11
	create_goal		10
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,13
	set_variable		10,8
	enqueue_goal		10,compile_active_draw_10_0
	put_values_inc		1,5,3
	put_value		5,13
	put_value		6,8
	execute		6,how_do_you_foo_6_0
compile_body_goal_11_12:
	read_element		11,1,13
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_reused_func		5,11,enqueue_goal
	write_element_value		5,1,13
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_body_goal_11_13:
	read_element		11,1,13
	get_value		9,10
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_variable		3,4
	set_value		4,8
	put_func		1,3,/
	write_element_variable		1,1,2
	write_element_marked_variable		1,2,3
	put_reused_func		8,11,execute
	write_element_value		8,1,1
	set_value		5,8
	enqueue_goal		5,gen_5_0
	create_goal		6
	set_values_inc		1,5,3
	set_values_dec		4,4,2
	set_marked_value		6,13
	enqueue_goal		6,register_body_arguments_6_0
	put_value		1,13
	execute_external		kl1cmp_reader,functor,3
compile_body_goal_11_7:
	read_element		11,0,12
	atom		12
	hash_on_atom		12,14,compile_body_goal_11_1
	bucket_entry_a		$:=,compile_body_goal_11_17
	bucket_entry_a		:=,compile_body_goal_11_18
	bucket_entry_a		<=,compile_body_goal_11_19
	bucket_entry_a		=,compile_body_goal_11_20
	bucket_entry_a		==,compile_body_goal_11_21
	bucket_entry_a		create_ext,compile_body_goal_11_22
	bucket_entry_a		create_to_node,compile_body_goal_11_23
	bucket_entry_a		create_to_processor,compile_body_goal_11_24
	bucket_entry_a		create_with_priority,compile_body_goal_11_25
	bucket_entry_a		enqueue_ext,compile_body_goal_11_26
	bucket_entry_a		enqueue_to_node,compile_body_goal_11_27
	bucket_entry_a		enqueue_to_processor,compile_body_goal_11_28
	bucket_entry_a		enqueue_with_priority,compile_body_goal_11_29
	bucket_entry_a		execute_ext,compile_body_goal_11_30
compile_body_goal_11_17:
	read_elements_inc		11,1,13,2
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,13
	enqueue_goal		11,compile_set_arg_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_foo_6_0
compile_body_goal_11_18:
	read_elements_inc		11,1,13,2
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,4
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_value		11,13
	enqueue_goal		11,compile_set_arg_11_0
	put_values_inc		1,5,3
	put_value		5,14
	put_value		6,8
	execute		6,how_do_you_foo_6_0
compile_body_goal_11_19:
	read_elements_inc		11,1,13,2
	collect_vector		11
	create_goal		11
	set_values_inc		1,1,4
	set_variable		5,1
	set_values_inc		6,8,3
	set_marked_value		9,14
	set_variable		10,8
	set_marked_value		11,13
	enqueue_goal		11,compile_struct_11_0
	create_goal		6
	set_variable		1,2
	set_value		2,6
	set_variable		3,4
	set_value		4,1
	set_value		5,14
	set_void		6
	enqueue_goal		6,how_do_you_foo_6_0
	put_value		1,5
	put_value		3,7
	put_value		5,13
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_body_goal_11_20:
	read_elements_inc		11,1,13,2
	collect_vector		11
	create_goal		12
	set_values_inc		1,1,4
	set_variable		5,3
	set_value		6,8
	set_variable		7,2
	set_value		8,10
	set_marked_value		9,14
	set_variable		10,1
	set_marked_value		11,13
	set_variable		12,8
	enqueue_goal		12,compile_put_valuable_12_0
	create_goal		3
	set_value		1,9
	set_value		2,2
	set_value		3,13
	enqueue_goal		3,mrb_body_ref_3_0
	create_goal		6
	set_variable		1,2
	set_value		2,6
	set_variable		3,4
	set_value		4,3
	set_value		5,14
	set_value		6,1
	enqueue_goal		6,how_do_you_foo_6_0
	put_value		1,5
	put_value		3,7
	put_value		5,13
	put_value		6,8
	execute		6,how_do_you_do_6_0
compile_body_goal_11_21:
	read_element		11,1,13
	read_element		11,2,15
	wait_vector		15,2
	read_element		15,0,14
	wait_atom		14,var
	read_element		15,1,14
	collect_value		13
	collect_vector		11
	collect_vector		15
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	put_values_inc		1,9,2
	put_value		3,14
	execute		3,mrb_body_ref_3_0
compile_body_goal_11_22:
	read_elements_inc		11,1,13,2
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_reused_func		5,11,create_ext
	write_elements_inc		5,1,13,2
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_body_goal_11_23:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,create_to_node
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_24:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,create_to_processor
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_25:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,create_with_priority
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_26:
	read_elements_inc		11,1,13,2
	get_value		9,10
	get_value		5,6
	get_value		1,2
	put_reused_func		5,11,enqueue_ext
	write_elements_inc		5,1,13,2
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	execute		5,gen_5_0
compile_body_goal_11_27:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,enqueue_to_node
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_28:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,enqueue_to_processor
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_29:
	read_elements_inc		11,1,13,2
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_marked_value		3,7
	set_value		4,8
	put_reused_func		1,11,enqueue_with_priority
	write_element_value		1,1,13
	write_element_marked_value		1,2,14
	set_value		5,1
	enqueue_goal		5,gen_5_0
	create_goal		3
	set_values_inc		1,9,2
	set_value		3,14
	enqueue_goal		3,mrb_body_ref_3_0
	put_values_inc		1,5,2
	put_value		3,14
	put_value		4,7
	execute		4,refvar_4_0
compile_body_goal_11_30:
	read_elements_inc		11,1,13,2
	get_value		9,10
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_variable		3,4
	set_value		4,8
	put_reused_func		1,11,/
	write_element_variable		1,1,2
	write_element_marked_variable		1,2,3
	put_func		8,3,execute_ext
	write_element_value		8,1,1
	write_element_value		8,2,14
	set_value		5,8
	enqueue_goal		5,gen_5_0
	create_goal		6
	set_values_inc		1,5,3
	set_values_dec		4,4,2
	set_marked_value		6,13
	enqueue_goal		6,register_body_arguments_6_0
	put_value		1,13
	execute_external		kl1cmp_reader,functor,3
compile_body_goal_11_1:
	suspend		compile_body_goal_11_0
	module_entry		kl1cmp_compile
	predicate		'$compile_put_valuable/4_2',12
'$compile_put_valuable/4_2_12_0':
	try_me_else		'$compile_put_valuable/4_2_12_1'
	jump_on_non_atom		10,'$compile_put_valuable/4_2_12_3'
	test_nil		10,'$compile_put_valuable/4_2_12_1'
	jump_on_non_atom		12,'$compile_put_valuable/4_2_12_5'
	test_nil		12,'$compile_put_valuable/4_2_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_variable
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_2_12_5':
	is_integer		12,'$compile_put_valuable/4_2_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_value
	write_element_value		7,1,11
	write_element_value		7,2,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_2_12_3':
	is_integer		10,'$compile_put_valuable/4_2_12_1'
	jump_on_non_atom		12,'$compile_put_valuable/4_2_12_7'
	test_nil		12,'$compile_put_valuable/4_2_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_value
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_2_12_7':
	is_integer		12,'$compile_put_valuable/4_2_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,get_value
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_2_12_1':
	suspend		'$compile_put_valuable/4_2_12_0'
	module_entry		kl1cmp_compile
	predicate		register_body_arguments,6
register_body_arguments_6_0:
	try_me_else		register_body_arguments_6_1
	integer		5
	test_integer		5,0,register_body_arguments_6_3
	collect_value		6
	get_value		3,4
	get_value		1,2
	proceed
register_body_arguments_6_3:
	put_integer		7,0
	g_less_than		7,5
	put_value		9,3
	put_marked_value		3,5
	put_nil		7
	b_set_vector_element		6,3,3,7,6
	b_decrement		5,7
	create_goal		6
	set_variable		1,8
	set_value		2,2
	set_marked_value		3,9
	set_value		4,4
	set_values_dec		5,7,2
	enqueue_goal		6,register_body_arguments_6_0
	create_goal		4
	set_variable		1,2
	set_value		2,8
	set_marked_value		3,3
	set_value		4,5
	enqueue_goal		4,usereg_4_0
	put_value		4,9
	execute		4,refvar_4_0
register_body_arguments_6_1:
	suspend		register_body_arguments_6_0
	module_entry		kl1cmp_compile
	predicate		'$compile_put_valuable/4_3',11
'$compile_put_valuable/4_3_11_0':
	try_me_else		'$compile_put_valuable/4_3_11_1'
	jump_on_non_atom		11,'$compile_put_valuable/4_3_11_3'
	test_nil		11,'$compile_put_valuable/4_3_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_constant
	write_elements_inc		7,1,9,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_3_11_3':
	is_integer		11,'$compile_put_valuable/4_3_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,get_constant
	write_elements_inc		7,1,9,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_3_11_1':
	suspend		'$compile_put_valuable/4_3_11_0'
	module_entry		kl1cmp_compile
	predicate		'$compile_put_valuable/4_4',11
'$compile_put_valuable/4_4_11_0':
	try_me_else		'$compile_put_valuable/4_4_11_1'
	jump_on_non_atom		11,'$compile_put_valuable/4_4_11_3'
	test_nil		11,'$compile_put_valuable/4_4_11_1'
	get_value		7,8
	get_value		1,2
	b_intern_atom		1,9
	put_func		7,3,put_structured_constant
	write_element_value		7,1,1
	write_element_value		7,2,10
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_4_11_3':
	is_integer		11,'$compile_put_valuable/4_4_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,get_constant
	write_elements_inc		7,1,9,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_4_11_1':
	suspend		'$compile_put_valuable/4_4_11_0'
	module_entry		kl1cmp_compile
	predicate		'$compile_put_valuable/4_5',10
'$compile_put_valuable/4_5_10_0':
	try_me_else		'$compile_put_valuable/4_5_10_1'
	jump_on_non_atom		10,'$compile_put_valuable/4_5_10_3'
	test_nil		10,'$compile_put_valuable/4_5_10_1'
	get_value		7,8
	get_value		1,2
	put_func		7,2,put_list
	write_element_value		7,1,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_5_10_3':
	is_integer		10,'$compile_put_valuable/4_5_10_1'
	get_value		7,8
	get_value		1,2
	put_func		7,2,get_list
	write_element_value		7,1,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_5_10_1':
	suspend		'$compile_put_valuable/4_5_10_0'
	module_entry		kl1cmp_compile
	predicate		'$compile_put_valuable/4_6',11
'$compile_put_valuable/4_6_11_0':
	try_me_else		'$compile_put_valuable/4_6_11_1'
	jump_on_non_atom		11,'$compile_put_valuable/4_6_11_3'
	test_nil		11,'$compile_put_valuable/4_6_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_vector
	write_elements_dec		7,1,10,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_6_11_3':
	is_integer		11,'$compile_put_valuable/4_6_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,get_vector
	write_elements_dec		7,1,10,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_put_valuable/4_6_11_1':
	suspend		'$compile_put_valuable/4_6_11_0'
	module_entry		kl1cmp_compile
	predicate		'$compile_trans_valuable/4_7',12
'$compile_trans_valuable/4_7_12_0':
	try_me_else		'$compile_trans_valuable/4_7_12_1'
	jump_on_non_atom		10,'$compile_trans_valuable/4_7_12_3'
	test_nil		10,'$compile_trans_valuable/4_7_12_1'
	jump_on_non_atom		12,'$compile_trans_valuable/4_7_12_5'
	test_nil		12,'$compile_trans_valuable/4_7_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,put_variable
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_trans_valuable/4_7_12_5':
	is_integer		12,'$compile_trans_valuable/4_7_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,trans_value
	write_element_value		7,1,11
	write_element_value		7,2,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_trans_valuable/4_7_12_3':
	is_integer		10,'$compile_trans_valuable/4_7_12_1'
	jump_on_non_atom		12,'$compile_trans_valuable/4_7_12_7'
	test_nil		12,'$compile_trans_valuable/4_7_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,trans_value
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_trans_valuable/4_7_12_7':
	is_integer		12,'$compile_trans_valuable/4_7_12_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,get_value
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_trans_valuable/4_7_12_1':
	suspend		'$compile_trans_valuable/4_7_12_0'
	module_entry		kl1cmp_compile
	predicate		compile_put_valuable,12
compile_put_valuable_12_0:
	try_me_else		compile_put_valuable_12_1
	jump_on_non_atom		9,compile_put_valuable_12_3
	test_atom		9,list,compile_put_valuable_12_1
	collect_value		10
	put_values_inc		9,11,2
	execute		10,'$compile_put_valuable/4_5_10_0'
compile_put_valuable_12_3:
	check_vector		9,2,compile_put_valuable_12_1
	read_element		9,0,13
	atom		13
	hash_on_atom		13,4,compile_put_valuable_12_1
	bucket_entry_a		atomic,compile_put_valuable_12_5
	bucket_entry_a		struct,compile_put_valuable_12_6
	bucket_entry_a		var,compile_put_valuable_12_7
	bucket_entry_a		vector,compile_put_valuable_12_8
compile_put_valuable_12_5:
	read_element		9,1,14
	collect_value		10
	collect_vector		9
	put_value		9,14
	put_values_inc		10,11,2
	execute		11,'$compile_put_valuable/4_3_11_0'
compile_put_valuable_12_6:
	read_element		9,1,14
	collect_value		10
	collect_vector		9
	put_value		9,14
	put_values_inc		10,11,2
	execute		11,'$compile_put_valuable/4_4_11_0'
compile_put_valuable_12_7:
	read_element		9,1,14
	collect_vector		9
	create_goal		12
	set_values_inc		1,1,6
	set_variable		7,2
	set_value		8,8
	set_marked_value		9,14
	set_values_inc		10,10,3
	enqueue_goal		12,'$compile_put_valuable/4_2_12_0'
	put_value		1,7
	put_value		3,14
	execute		3,mrb_body_ref_3_0
compile_put_valuable_12_8:
	read_element		9,1,14
	collect_value		10
	collect_vector		9
	put_value		9,14
	put_values_inc		10,11,2
	execute		11,'$compile_put_valuable/4_6_11_0'
compile_put_valuable_12_1:
	suspend		compile_put_valuable_12_0
	module_entry		kl1cmp_compile
	predicate		'$compile_active_draw/2_8',10
'$compile_active_draw/2_8_10_0':
	try_me_else		'$compile_active_draw/2_8_10_1'
	jump_on_non_atom		10,'$compile_active_draw/2_8_10_3'
	test_nil		10,'$compile_active_draw/2_8_10_1'
	get_value		7,8
	get_value		1,2
	put_func		7,2,write_variable
	write_element_value		7,1,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_active_draw/2_8_10_3':
	is_integer		10,'$compile_active_draw/2_8_10_1'
	get_value		7,8
	get_value		1,2
	put_func		7,2,write_value
	write_element_value		7,1,9
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_active_draw/2_8_10_1':
	suspend		'$compile_active_draw/2_8_10_0'
	module_entry		kl1cmp_compile
	predicate		compile_trans_valuable,12
compile_trans_valuable_12_0:
	try_me_else		compile_trans_valuable_12_1
	wait_vector		9,2
	read_element		9,0,13
	wait_atom		13,var
	read_element		9,1,13
	collect_vector		9
	create_goal		12
	set_values_inc		1,1,6
	set_variable		7,2
	set_value		8,8
	set_marked_value		9,13
	set_values_inc		10,10,3
	enqueue_goal		12,'$compile_trans_valuable/4_7_12_0'
	put_value		1,7
	put_value		3,13
	execute		3,mrb_body_ref_3_0
compile_trans_valuable_12_1:
	suspend		compile_trans_valuable_12_0
	module_entry		kl1cmp_compile
	predicate		'$compile_set_arg/3_9',11
'$compile_set_arg/3_9_11_0':
	try_me_else		'$compile_set_arg/3_9_11_1'
	jump_on_non_atom		10,'$compile_set_arg/3_9_11_3'
	test_nil		10,'$compile_set_arg/3_9_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,set_variable
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_set_arg/3_9_11_3':
	is_integer		10,'$compile_set_arg/3_9_11_1'
	get_value		7,8
	get_value		1,2
	put_func		7,3,set_value
	write_element_value		7,1,9
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_set_arg/3_9_11_1':
	suspend		'$compile_set_arg/3_9_11_0'
	module_entry		kl1cmp_compile
	predicate		compile_active_draw,10
compile_active_draw_10_0:
	try_me_else		compile_active_draw_10_1
	wait_vector		9,2
	read_element		9,0,11
	atom		11
	branch_on_atom		11,2,compile_active_draw_10_1
	bucket_entry_a		atomic,compile_active_draw_10_4
	bucket_entry_a		var,compile_active_draw_10_5
compile_active_draw_10_4:
	read_element		9,1,12
	collect_value		10
	get_value		7,8
	get_value		1,2
	put_reused_func		7,9,write_constant
	write_element_value		7,1,12
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_active_draw_10_5:
	read_element		9,1,12
	collect_vector		9
	create_goal		10
	set_values_inc		1,1,6
	set_variable		7,2
	set_value		8,8
	set_marked_value		9,12
	set_value		10,10
	enqueue_goal		10,'$compile_active_draw/2_8_10_0'
	put_value		1,7
	put_value		3,12
	execute		3,mrb_body_ref_3_0
compile_active_draw_10_1:
	suspend		compile_active_draw_10_0
	module_entry		kl1cmp_compile
	predicate		'$compile_struct/3_10',12
'$compile_struct/3_10_12_0':
	try_me_else		'$compile_struct/3_10_12_1'
	wait_vector		9,2
	read_element		9,0,13
	atom		13
	branch_on_atom		13,2,'$compile_struct/3_10_12_1'
	bucket_entry_a		list,'$compile_struct/3_10_12_4'
	bucket_entry_a		vector,'$compile_struct/3_10_12_5'
'$compile_struct/3_10_12_4':
	read_element		9,1,14
	jump_on_non_atom		10,'$compile_struct/3_10_12_7'
	test_nil		10,'$compile_struct/3_10_12_1'
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_marked_value		12,12
	get_value		12,14
	put_func		7,3,put_value
	write_elements_dec		7,1,12,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_struct/3_10_12_7':
	is_integer		10,'$compile_struct/3_10_12_1'
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_marked_value		12,12
	get_value		12,14
	put_func		7,3,get_list_value
	write_elements_dec		7,1,12,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_struct/3_10_12_5':
	read_element		9,1,14
	jump_on_non_atom		10,'$compile_struct/3_10_12_9'
	test_nil		10,'$compile_struct/3_10_12_1'
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_marked_value		12,12
	get_value		12,14
	put_func		7,3,put_value
	write_elements_dec		7,1,12,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_struct/3_10_12_9':
	is_integer		10,'$compile_struct/3_10_12_1'
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_marked_value		12,12
	get_value		12,14
	put_func		7,3,get_vector_value
	write_elements_dec		7,1,12,2
	put_values_inc		1,3,5
	execute		5,gen_5_0
'$compile_struct/3_10_12_1':
	suspend		'$compile_struct/3_10_12_0'
	module_entry		kl1cmp_compile
	predicate		compile_set_arg,11
compile_set_arg_11_0:
	try_me_else		compile_set_arg_11_1
	wait_vector		9,2
	read_element		9,0,12
	atom		12
	branch_on_atom		12,2,compile_set_arg_11_1
	bucket_entry_a		atomic,compile_set_arg_11_4
	bucket_entry_a		var,compile_set_arg_11_5
compile_set_arg_11_4:
	read_element		9,1,13
	collect_value		10
	collect_vector		9
	get_value		7,8
	get_value		1,2
	put_func		7,3,set_constant
	write_element_value		7,1,13
	write_element_value		7,2,11
	put_values_inc		1,3,5
	execute		5,gen_5_0
compile_set_arg_11_5:
	read_element		9,1,13
	collect_vector		9
	create_goal		11
	set_values_inc		1,1,6
	set_variable		7,2
	set_value		8,8
	set_marked_value		9,13
	set_values_inc		10,10,2
	enqueue_goal		11,'$compile_set_arg/3_9_11_0'
	put_value		1,7
	put_value		3,13
	execute		3,mrb_body_ref_3_0
compile_set_arg_11_1:
	suspend		compile_set_arg_11_0
	module_entry		kl1cmp_compile
	predicate		compile_struct,11
compile_struct_11_0:
	create_goal		12
	set_values_inc		1,1,6
	set_variable		7,1
	set_values_inc		8,8,3
	set_marked_value		11,11
	set_variable		12,3
	enqueue_goal		12,'$compile_struct/3_10_12_0'
	create_goal		3
	set_variable		1,2
	set_value		2,1
	set_value		3,11
	enqueue_goal		3,mrb_body_ref_3_0
	put_value		1,7
	execute		3,mrb_body_ref_3_0
compile_struct_11_1:
	suspend		compile_struct_11_0
	module_entry		kl1cmp_compile
	predicate		newvar,4
newvar_4_0:
	try_me_else		newvar_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,10
	read_element		1,2,5
	wait_vector		10,3
	read_element		10,0,6
	wait_atom		6,-
	read_elements_inc		10,1,6,2
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	collect_value		9
	collect_vector		3
	put_reused_func		1,1,-
	write_element_variable		1,1,9
	write_element_variable		1,2,3
	put_reused_func		10,10,-
	write_element_value		10,1,1
	write_element_value		10,2,5
	get_vector_value		2,10
	put_marked_value		1,8
	put_marked_value		2,4
	b_set_vector_element		6,1,1,2,2
	get_value		2,9
	b_set_vector_element		7,8,1,4,2
	get_value		2,3
	proceed
newvar_4_1:
	suspend		newvar_4_0
	module_entry		kl1cmp_compile
	predicate		refvar,4
refvar_4_0:
	try_me_else		refvar_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,10
	read_element		1,2,5
	wait_vector		10,3
	read_element		10,0,6
	wait_atom		6,-
	read_elements_inc		10,1,6,2
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	collect_value		9
	collect_vector		3
	put_reused_func		1,1,-
	write_element_value		1,1,6
	write_element_variable		1,2,3
	put_reused_func		6,10,-
	write_element_value		6,1,1
	write_element_value		6,2,5
	get_vector_value		2,6
	b_set_vector_element		7,8,1,4,2
	get_value		2,3
	proceed
refvar_4_1:
	otherwise		refvar_4_0
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
refvar_4_6:
	suspend		refvar_4_0
	module_entry		kl1cmp_compile
	predicate		usereg,4
usereg_4_0:
	try_me_else		usereg_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,10
	read_element		1,2,5
	wait_vector		10,3
	read_element		10,0,6
	wait_atom		6,-
	read_elements_inc		10,1,6,2
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	collect_value		9
	collect_vector		3
	put_reused_func		1,1,-
	write_elements_inc		1,1,6,2
	put_reused_func		6,10,-
	write_element_value		6,1,1
	write_element_variable		6,2,3
	get_vector_value		2,6
	b_set_vector_element		5,8,1,4,2
	get_value		2,3
	proceed
usereg_4_1:
	otherwise		usereg_4_0
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
usereg_4_6:
	suspend		usereg_4_0
	module_entry		kl1cmp_compile
	predicate		get_From_PC,4
get_From_PC_4_0:
	try_me_else		get_From_PC_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,8
	read_element		1,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,-
	read_elements_inc		8,1,6,2
	put_marked_value		9,4
	b_set_vector_element		6,3,6,9,3
	get_value		6,4
	put_reused_func		1,1,-
	write_element_value		1,1,3
	write_element_value		1,2,7
	put_reused_func		3,8,-
	write_element_value		3,1,1
	write_element_value		3,2,5
	get_vector_value		2,3
	proceed
get_From_PC_4_1:
	suspend		get_From_PC_4_0
	module_entry		kl1cmp_compile
	predicate		set_From_PC,4
set_From_PC_4_0:
	try_me_else		set_From_PC_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,8
	read_element		1,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,-
	read_elements_inc		8,1,6,2
	b_set_vector_element		6,3,3,4,4
	put_reused_func		1,1,-
	write_element_value		1,1,4
	write_element_value		1,2,7
	put_reused_func		3,8,-
	write_element_value		3,1,1
	write_element_value		3,2,5
	get_vector_value		2,3
	proceed
set_From_PC_4_1:
	suspend		set_From_PC_4_0
	module_entry		kl1cmp_compile
	predicate		get_To_PC,4
get_To_PC_4_0:
	try_me_else		get_To_PC_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,8
	read_element		1,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,-
	read_elements_inc		8,1,6,2
	put_marked_value		9,4
	b_set_vector_element		7,3,7,9,3
	get_value		7,4
	put_reused_func		1,1,-
	write_element_value		1,1,6
	write_element_value		1,2,3
	put_reused_func		3,8,-
	write_element_value		3,1,1
	write_element_value		3,2,5
	get_vector_value		2,3
	proceed
get_To_PC_4_1:
	suspend		get_To_PC_4_0
	module_entry		kl1cmp_compile
	predicate		set_To_PC,4
set_To_PC_4_0:
	try_me_else		set_To_PC_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_element		1,1,8
	read_element		1,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,-
	read_elements_inc		8,1,6,2
	b_set_vector_element		7,3,3,4,4
	put_reused_func		1,1,-
	write_element_value		1,1,6
	write_element_value		1,2,4
	put_reused_func		3,8,-
	write_element_value		3,1,1
	write_element_value		3,2,5
	get_vector_value		2,3
	proceed
set_To_PC_4_1:
	suspend		set_To_PC_4_0
	module_entry		kl1cmp_compile
	predicate		'$how_do_you_do/2_11',6
'$how_do_you_do/2_11_6_0':
	try_me_else		'$how_do_you_do/2_11_6_1'
	jump_on_non_atom		6,'$how_do_you_do/2_11_6_3'
	test_nil		6,'$how_do_you_do/2_11_6_1'
	put_value		6,3
	put_marked_value		6,6
	get_value		6,4
	put_values_inc		3,5,2
	execute		4,set_From_PC_4_0
'$how_do_you_do/2_11_6_3':
	is_integer		6,'$how_do_you_do/2_11_6_1'
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
'$how_do_you_do/2_11_6_1':
	suspend		'$how_do_you_do/2_11_6_0'
	module_entry		kl1cmp_compile
	predicate		set_pass_tbl,3
set_pass_tbl_3_0:
	put_integer		4,1
	b_set_vector_element		1,3,1,4,3
	get_value		3,2
	proceed
set_pass_tbl_3_1:
	suspend		set_pass_tbl_3_0
	module_entry		kl1cmp_compile
	predicate		how_do_you_do,6
how_do_you_do_6_0:
	try_me_else		how_do_you_do_6_1
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		5,1,7,2
	collect_value		8
	collect_vector		5
	create_goal		4
	set_variable		1,5
	set_value		2,2
	set_marked_value		3,7
	set_marked_value		4,4
	enqueue_goal		4,set_To_PC_4_0
	create_goal		6
	set_variable		1,2
	set_value		2,5
	set_values_inc		3,3,2
	set_value		5,7
	set_marked_value		6,6
	enqueue_goal		6,'$how_do_you_do/2_11_6_0'
	put_values_dec		3,7,2
	execute		4,get_From_PC_4_0
how_do_you_do_6_1:
	otherwise		how_do_you_do_6_0
	collect_value		5
	get_value		3,4
	get_value		1,2
	get_nil		6
	proceed
how_do_you_do_6_6:
	suspend		how_do_you_do_6_0
	module_entry		kl1cmp_compile
	predicate		how_do_you_foo,6
how_do_you_foo_6_0:
	try_me_else		how_do_you_foo_6_1
	wait_vector		5,2
	read_element		5,0,7
	atom		7
	branch_on_atom		7,3,how_do_you_foo_6_1
	bucket_entry_a		list,how_do_you_foo_6_4
	bucket_entry_a		var,how_do_you_foo_6_5
	bucket_entry_a		vector,how_do_you_foo_6_6
how_do_you_foo_6_4:
	read_element		5,1,8
	collect_vector		5
	put_value		5,8
	execute		6,how_do_you_do_6_0
how_do_you_foo_6_5:
	read_element		5,1,8
	collect_vector		5
	put_value		5,8
	execute		6,how_do_you_do_6_0
how_do_you_foo_6_6:
	read_element		5,1,8
	collect_vector		5
	put_value		5,8
	execute		6,how_do_you_do_6_0
how_do_you_foo_6_1:
	otherwise		how_do_you_foo_6_0
	collect_value		5
	get_value		3,4
	get_value		1,2
	get_nil		6
	proceed
how_do_you_foo_6_12:
	suspend		how_do_you_foo_6_0
	module_entry		kl1cmp_compile
	predicate		gen,5
gen_5_0:
	put_list_val_val		6,5,2
	get_list_value		1,6
	b_increment		3,1
	get_value		1,4
	proceed
gen_5_1:
	suspend		gen_5_0
	module_entry		kl1cmp_compile
	predicate		set_mrb_body_ref,4
set_mrb_body_ref_4_0:
	try_me_else		set_mrb_body_ref_4_1
	integer		3
	test_integer		3,0,set_mrb_body_ref_4_3
	collect_value		4
	get_value		1,2
	proceed
set_mrb_body_ref_4_3:
	put_integer		5,0
	g_less_than		5,3
	put_marked_variable		5,6
	put_nil		7
	b_set_vector_element		4,5,4,7,5
	b_decrement		3,3
	get_value		6,3
	create_goal		4
	set_variable		1,3
	set_value		2,2
	set_values_dec		3,6,2
	enqueue_goal		4,set_mrb_body_ref_4_0
	put_values_inc		2,3,2
	execute		3,set_mrb_body_ref00_3_0
set_mrb_body_ref_4_1:
	suspend		set_mrb_body_ref_4_0
	module_entry		kl1cmp_compile
	predicate		set_mrb_body_ref00,3
set_mrb_body_ref00_3_0:
	try_me_else		set_mrb_body_ref00_3_1
	wait		3
	switch_on_type		3,set_mrb_body_ref00_3_2,set_mrb_body_ref00_3_3,set_mrb_body_ref00_3_4,set_mrb_body_ref00_3_5,set_mrb_body_ref00_3_6,set_mrb_body_ref00_3_7
set_mrb_body_ref00_3_4:
	get_value		1,2
	proceed
set_mrb_body_ref00_3_2:
	get_value		1,2
	proceed
set_mrb_body_ref00_3_3:
	get_value		1,2
	proceed
set_mrb_body_ref00_3_5:
	test_arity		3,3,set_mrb_body_ref00_3_1
	read_element		3,0,4
	wait_atom		4,'$VAR'
	read_elements_inc		3,1,4,2
	put_reused_func		3,3,'$VAR'
	write_elements_inc		3,1,4,2
	execute		3,mrb_body_ref_3_0
set_mrb_body_ref00_3_6:
	get_value		1,2
	proceed
set_mrb_body_ref00_3_7:
	is_float		3,set_mrb_body_ref00_3_1
	get_value		1,2
	proceed
set_mrb_body_ref00_3_1:
	otherwise		set_mrb_body_ref00_3_0
	try_me_else		set_mrb_body_ref00_3_11
	vector		3
	put_value		4,3
	g_vector		4,3
	b_decrement		3,3
	execute		4,set_mrb_body_ref_4_0
set_mrb_body_ref00_3_11:
	suspend		set_mrb_body_ref00_3_0
	module_entry		kl1cmp_compile
	predicate		mrb_body_ref,3
mrb_body_ref_3_0:
	try_me_else		mrb_body_ref_3_1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,'$VAR'
	read_elements_inc		3,1,4,2
	collect_value		5
	collect_vector		3
	put_value		3,4
	execute		3,increment_bref_3_0
mrb_body_ref_3_1:
	otherwise		mrb_body_ref_3_0
	collect_value		3
	get_value		1,2
	proceed
mrb_body_ref_3_6:
	suspend		mrb_body_ref_3_0
	module_entry		kl1cmp_compile
	predicate		increment_bref,3
increment_bref_3_0:
	put_variable		5,4
	b_set_vector_element		1,3,1,5,3
	get_value		3,2
	b_increment		1,1
	get_value		1,4
	proceed
increment_bref_3_1:
	suspend		increment_bref_3_0
	begin_const_section		kl1cmp_compile
'$SCNST_0_1':
	define_desc		3,8
	define_integer		543516756
	define_integer		1969319011
	define_integer		1998611827
	define_integer		543976553
	define_integer		1886614899
	define_integer		543452773
	define_integer		1701998438
	define_integer		779249014
'$SCNST_0_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_0_1'
	define_atom		[]
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		27,17
	define_integer		1819310149
	define_integer		1953063785
	define_integer		1936288800
	define_integer		1936269428
	define_integer		1953459744
	define_integer		1886218528
	define_integer		1701668204
	define_integer		1684370542
	define_integer		544106784
	define_integer		1918989671
	define_integer		1969365092
	define_integer		1769237609
	define_integer		1852383342
	define_integer		544503152
	define_integer		1969713761
	define_integer		1953391981
	define_integer		46
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		19,16
	define_integer		1769103702
	define_integer		1701601889
	define_integer		544175136
	define_integer		1769103734
	define_integer		1701601889
	define_integer		1768846624
	define_integer		1633904998
	define_integer		1852795252
	define_integer		544434464
	define_integer		544501614
	define_integer		1819307369
	define_integer		1852140901
	define_integer		543450484
	define_integer		1730178665
	define_integer		1685217653
	define_integer		11891
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		11,17
	define_integer		1819310149
	define_integer		1953063785
	define_integer		1667593760
	define_integer		544370548
	define_integer		1847620457
	define_integer		1763734639
	define_integer		1701605485
	define_integer		1953391981
	define_integer		1763730533
	define_integer		1969692782
	define_integer		543453793
	define_integer		1818850658
	define_integer		544106868
	define_integer		1970302569
	define_integer		1918967924
	define_integer		1701672295
	define_integer		3044462
'$SCNST_3':
	define_string		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		27,15
	define_integer		1818453316
	define_integer		1684369001
	define_integer		1953784096
	define_integer		1953525093
	define_integer		544175136
	define_integer		1718185589
	define_integer		1769414777
	define_integer		1629513844
	define_integer		1853169774
	define_integer		1953066601
	define_integer		1768710505
	define_integer		543450490
	define_integer		1769103734
	define_integer		1701601889
	define_integer		46
'$SCNST_4':
	define_string		'$SCNST_4_0'
