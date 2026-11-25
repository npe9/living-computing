kl1cmp_register:
	module		kl1cmp_register
	entry		compile_predicate,9,compile_predicate_9_0
	module_entry		kl1cmp_register
	predicate		compile_predicate,9
compile_predicate_9_0:
	create_goal		3
	set_variable		1,11
	set_value		2,2
	set_marked_value		3,8
	enqueue_goal_external		kl1cmp_output,write_code_end,3
	create_goal		8
	set_variable		1,10
	set_value		2,11
	set_values_inc		3,3,3
	set_values_inc		6,7,3
	enqueue_goal		8,compile_predicate_8_0
	create_goal		3
	set_variable		1,2
	set_value		2,10
	set_value		3,8
	enqueue_goal_external		kl1cmp_output,write_label,3
	put_value		3,8
	put_value		4,6
	execute_external		kl1cmp_output,write_code_header,4
compile_predicate_9_1:
	suspend		compile_predicate_9_0
	module_entry		kl1cmp_register
	predicate		compile_predicate,8
compile_predicate_8_0:
	try_me_else		compile_predicate_8_1
	jump_on_non_list_var_var		6,compile_predicate_8_3,9,10
	try_me_else		compile_predicate_8_4
	wait_nil		10
	collect_list		6
	put_value		6,9
	execute		8,compile_last_one_block_8_0
compile_predicate_8_4:
	collect_list		6
	create_goal		8
	set_variable		1,11
	set_value		2,2
	set_variable		3,6
	set_value		4,4
	set_marked_value		5,5
	set_value		6,10
	set_marked_value		7,7
	set_variable		8,10
	enqueue_goal		8,compile_predicate_8_0
	put_value		2,11
	put_value		4,6
	put_value		6,9
	put_value		9,10
	execute		9,compile_one_block_9_0
compile_predicate_8_3:
	check_nil		6,compile_predicate_8_1
	collect_value		8
	collect_value		7
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
compile_predicate_8_1:
	suspend		compile_predicate_8_0
	module_entry		kl1cmp_register
	predicate		compile_last_one_block,8
compile_last_one_block_8_0:
	try_me_else		compile_last_one_block_8_1
	list		6
	read_car		6,9
	atom		9
	branch_on_atom		9,2,compile_last_one_block_8_1
	bucket_entry_a		alternatively,compile_last_one_block_8_4
	bucket_entry_a		otherwise,compile_last_one_block_8_5
compile_last_one_block_8_4:
	read_cdr		6,10
	wait_nil		10
	collect_value		8
	collect_value		7
	collect_value		5
	get_value		1,2
	put_structured_constant		1,'$SCNST_0'
	put_reused_list_val_val		2,6,1,4
	get_list_value		3,2
	proceed
compile_last_one_block_8_5:
	read_cdr		6,10
	wait_nil		10
	collect_value		8
	collect_value		7
	collect_value		5
	get_value		1,2
	put_structured_constant		1,'$SCNST_1'
	put_reused_list_val_val		2,6,1,4
	get_list_value		3,2
	proceed
compile_last_one_block_8_1:
	otherwise		compile_last_one_block_8_0
	try_me_else		compile_last_one_block_8_9
	wait_list_var_var		6,9,10
	wait_nil		10
	collect_list		6
	collect_value		8
	put_value		8,7
	put_integer		6,0
	put_value		7,9
	put_integer		9,0
	put_void		10
	execute		10,compile_and_output_one_clause_10_0
compile_last_one_block_8_9:
	otherwise		compile_last_one_block_8_0
	try_me_else		compile_last_one_block_8_13
	list		6
	read_car		6,9
	atom		9
	branch_on_atom		9,2,compile_last_one_block_8_13
	bucket_entry_a		alternatively,compile_last_one_block_8_16
	bucket_entry_a		otherwise,compile_last_one_block_8_17
compile_last_one_block_8_16:
	read_cdr		6,10
	collect_list		6
	create_goal		8
	set_variable		1,6
	set_values_inc		2,2,4
	set_value		6,10
	set_values_inc		7,7,2
	enqueue_goal		8,compile_last_one_block_8_0
	put_value		2,6
	execute_external		kl1cmp_output,write_alternatively,2
compile_last_one_block_8_17:
	read_cdr		6,10
	collect_list		6
	create_goal		8
	set_variable		1,6
	set_values_inc		2,2,4
	set_value		6,10
	set_marked_value		7,7
	set_value		8,8
	enqueue_goal		8,compile_last_one_block_8_0
	put_values_inc		2,6,2
	execute_external		kl1cmp_output,write_otherwise,3
compile_last_one_block_8_13:
	otherwise		compile_last_one_block_8_0
	try_me_else		compile_last_one_block_8_21
	wait_list_var_var		6,9,10
	collect_list		6
	put_values_inc		11,7,2
	create_goal		8
	set_variable		1,7
	set_value		2,2
	set_variable		3,6
	set_value		4,4
	set_marked_value		5,5
	set_value		6,10
	set_marked_value		7,11
	set_variable		8,10
	enqueue_goal		8,compile_last_one_block_8_0
	put_value		2,7
	put_value		4,6
	put_integer		6,0
	put_value		7,9
	put_values_inc		8,11,2
	execute		10,compile_and_output_one_clause_10_0
compile_last_one_block_8_21:
	suspend		compile_last_one_block_8_0
	module_entry		kl1cmp_register
	predicate		compile_and_output_one_clause,10
compile_and_output_one_clause_10_0:
	put_marked_value		11,9
	b_increment		11,11
	get_value		10,11
	create_goal		15
	set_values_inc		1,1,2
	set_variable		3,11
	set_value		4,4
	set_marked_value		5,5
	set_variable		6,12
	set_marked_value		7,6
	set_marked_variable		8,1
	set_variable		9,13
	set_variable		10,2
	set_variable		11,4
	set_marked_value		12,8
	set_value		13,9
	set_marked_variable		14,10
	set_marked_value		15,7
	enqueue_goal		15,output_code_or_retry_15_0
	create_goal		14
	set_variable		1,15
	set_value		2,11
	set_variable		3,11
	set_value		4,12
	set_variable		5,12
	set_value		6,13
	set_variable		7,13
	set_value		8,2
	set_variable		9,2
	set_value		10,4
	set_variable		11,4
	set_void		12
	set_value		13,1
	set_integer		14,0
	enqueue_goal		14,determine_registers_14_0
	create_goal		13
	set_variable		1,14
	set_value		2,15
	set_atom		3,success
	set_value		4,11
	set_variable		5,11
	set_value		6,12
	set_variable		7,12
	set_value		8,13
	set_variable		9,13
	set_value		10,2
	set_variable		11,2
	set_value		12,4
	set_value		13,10
	enqueue_goal		13,register_preference_13_0
	create_goal		9
	set_variable		1,4
	set_value		2,11
	set_variable		3,11
	set_value		4,12
	set_variable		5,12
	set_value		6,13
	set_variable		7,13
	set_values_dec		8,2,2
	enqueue_goal		9,register_predefined_9_0
	create_goal		3
	set_variable		1,2
	set_nil		2
	set_value		3,13
	enqueue_goal_external		kl1cmp_reader,herrey,3
	create_goal		13
	set_value		1,10
	set_nil		2
	set_variable		3,10
	set_value		4,2
	set_variable		5,2
	set_value		6,4
	set_variable		7,4
	set_value		8,11
	set_value		9,5
	set_variable		10,13
	set_value		11,1
	set_variable		12,11
	set_variable		13,5
	enqueue_goal_external		kl1cmp_mrb,mrb_optimization,13
	create_goal		17
	set_value		1,3
	set_values_dec		2,14,2
	set_nil		4
	set_values_inc		5,6,2
	put_func		3,3,/
	write_elements_inc		3,1,8,2
	set_value		7,3
	set_variable		8,3
	set_value		9,2
	set_variable		10,2
	set_value		11,4
	set_variable		12,4
	set_values_dec		13,12,2
	set_value		15,1
	set_value		16,10
	set_value		17,5
	enqueue_goal_external		kl1cmp_compile,compile_one_clause,17
	create_goal		3
	set_value		1,1
	set_nil		2
	set_value		3,4
	enqueue_goal_external		kl1cmp_reader,herrey,3
	create_goal		3
	set_value		1,1
	set_nil		2
	set_value		3,2
	enqueue_goal_external		kl1cmp_reader,herrey,3
	put_nil		2
	execute_external		kl1cmp_reader,herrey,3
compile_and_output_one_clause_10_1:
	suspend		compile_and_output_one_clause_10_0
	module_entry		kl1cmp_register
	predicate		output_code_or_retry,15
output_code_or_retry_15_0:
	try_me_else		output_code_or_retry_15_1
	atom		6
	branch_on_atom		6,2,output_code_or_retry_15_1
	bucket_entry_a		fail,output_code_or_retry_15_3
	bucket_entry_a		success,output_code_or_retry_15_4
output_code_or_retry_15_3:
	wait_integer		7,0
	collect_value		14
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	put_list		6
	write_car_marked_value		6,15
	write_cdr_nil		6
	put_structured_constant		7,'$SCNST_2'
	put_func		8,3,warning_message
	write_elements_dec		8,1,7,2
	get_list_val_var		3,7,8,6
	put_value		3,6
	put_integer		6,1
	put_value		7,15
	put_values_inc		8,12,2
	put_void		10
	execute		10,compile_and_output_one_clause_10_0
output_code_or_retry_15_4:
	collect_value		15
	collect_value		7
	collect_value		5
	get_value		3,4
	create_goal		3
	set_variable		1,3
	set_value		2,2
	put_func		2,3,/
	write_elements_inc		2,1,12,2
	set_value		3,2
	enqueue_goal_external		kl1cmp_output,write_label,3
	create_goal		3
	set_value		1,1
	set_value		2,3
	set_variable		3,1
	enqueue_goal_external		kl1cmp_output,write_object_code,3
	create_goal		3
	set_value		1,1
	set_nil		2
	set_variable		3,1
	enqueue_goal_external		kl1cmp_output,convert_code_for_PDSS,3
	create_goal		8
	set_values_inc		1,9,3
	set_variable		4,3
	set_value		5,1
	set_nil		6
	set_integer		7,0
	set_value		8,14
	enqueue_goal_external		kl1cmp_output,erace_or_convert_instruction,8
	put_value		1,8
	put_nil		2
	execute_external		kl1cmp_reader,herrey,3
output_code_or_retry_15_1:
	otherwise		output_code_or_retry_15_0
	collect_value		14
	collect_value		13
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_value		1,2
	put_list		1
	write_car_value		1,15
	write_cdr_nil		1
	put_structured_constant		2,'$SCNST_3'
	put_func		5,3,error_message
	write_elements_dec		5,1,2,2
	put_list_val_val		1,5,4
	get_list_value		3,1
	proceed
output_code_or_retry_15_7:
	suspend		output_code_or_retry_15_0
	module_entry		kl1cmp_register
	predicate		compile_one_block,9
compile_one_block_9_0:
	try_me_else		compile_one_block_9_1
	list		6
	read_car		6,10
	atom		10
	branch_on_atom		10,2,compile_one_block_9_1
	bucket_entry_a		alternatively,compile_one_block_9_4
	bucket_entry_a		otherwise,compile_one_block_9_5
compile_one_block_9_4:
	read_cdr		6,11
	collect_list		6
	create_goal		9
	set_variable		1,6
	set_values_inc		2,2,4
	set_value		6,11
	set_values_inc		7,7,3
	enqueue_goal		9,compile_one_block_9_0
	put_value		2,6
	execute_external		kl1cmp_output,write_alternatively,2
compile_one_block_9_5:
	read_cdr		6,11
	collect_list		6
	create_goal		9
	set_variable		1,6
	set_values_inc		2,2,4
	set_value		6,11
	set_marked_value		7,7
	set_values_inc		8,8,2
	enqueue_goal		9,compile_one_block_9_0
	put_values_inc		2,6,2
	execute_external		kl1cmp_output,write_otherwise,3
compile_one_block_9_1:
	otherwise		compile_one_block_9_0
	try_me_else		compile_one_block_9_9
	jump_on_non_list_var_var		6,compile_one_block_9_11,10,11
	collect_list		6
	put_values_inc		12,7,2
	create_goal		9
	set_variable		1,7
	set_value		2,2
	set_variable		3,6
	set_value		4,4
	set_marked_value		5,5
	set_value		6,11
	set_marked_value		7,12
	set_variable		8,11
	set_value		9,9
	enqueue_goal		9,compile_one_block_9_0
	put_value		2,7
	put_value		4,6
	put_integer		6,0
	put_value		7,10
	put_values_inc		8,12,2
	put_value		10,11
	execute		10,compile_and_output_one_clause_10_0
compile_one_block_9_11:
	check_nil		6,compile_one_block_9_9
	collect_value		7
	collect_value		5
	get_value		3,4
	get_value		1,2
	get_value		8,9
	proceed
compile_one_block_9_9:
	suspend		compile_one_block_9_0
	module_entry		kl1cmp_register
	predicate		register_predefined,9
register_predefined_9_0:
	try_me_else		register_predefined_9_1
	wait_integer		9,0
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
register_predefined_9_1:
	otherwise		register_predefined_9_0
	try_me_else		register_predefined_9_6
	integer		9
	g_decrement		9,9
	create_goal		9
	set_variable		1,13
	set_value		2,2
	set_variable		3,12
	set_value		4,4
	set_variable		5,11
	set_value		6,6
	set_variable		7,10
	set_value		8,8
	set_marked_value		9,9
	enqueue_goal		9,register_predefined_9_0
	put_value		2,13
	put_value		4,12
	put_value		6,11
	put_value		8,10
	execute		9,init_used_table_9_0
register_predefined_9_6:
	suspend		register_predefined_9_0
	module_entry		kl1cmp_register
	predicate		init_used_table,9
init_used_table_9_0:
	try_me_else		init_used_table_9_1
	vector		5
	integer		9
	try_me_else		init_used_table_9_4
	g_vector_element		5,9,10
	wait_nil		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
init_used_table_9_4:
	try_me_else		init_used_table_9_1
	g_vector_element		5,9,10
	integer		10
	mark_element		5,9
	get_value		5,6
	create_goal		5
	set_values_inc		1,7,2
	set_variable		3,5
	set_variable		4,6
	set_marked_value		5,10
	enqueue_goal		5,use_register_5_0
	create_goal		4
	set_values_inc		1,3,2
	set_marked_value		3,9
	set_value		4,6
	enqueue_goal		4,ref_vector_4_0
	put_value		3,9
	put_value		4,5
	execute		4,ref_vector_4_0
init_used_table_9_1:
	suspend		init_used_table_9_0
	module_entry		kl1cmp_register
	predicate		register_preference,13
register_preference_13_0:
	try_me_else		register_preference_13_1
	jump_on_non_list_var_var		13,register_preference_13_3,14,15
	collect_list		13
	create_goal		13
	set_variable		1,20
	set_value		2,2
	set_variable		3,19
	set_value		4,4
	set_variable		5,18
	set_value		6,6
	set_variable		7,17
	set_value		8,8
	set_variable		9,16
	set_value		10,10
	set_variable		11,13
	set_value		12,12
	set_value		13,15
	enqueue_goal		13,register_preference_13_0
	put_value		2,20
	put_value		4,19
	put_value		6,18
	put_value		8,17
	put_value		10,16
	put_values_inc		12,13,2
	execute		13,one_register_pref_13_0
register_preference_13_3:
	check_nil		13,register_preference_13_1
	get_value		11,12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
register_preference_13_1:
	suspend		register_preference_13_0
	module_entry		kl1cmp_register
	predicate		one_register_pref,13
one_register_pref_13_0:
	try_me_else		one_register_pref_13_1
	wait_vector		13,3
	read_element		13,0,14
	atom		14
	branch_on_atom		14,3,one_register_pref_13_1
	bucket_entry_a		put_value,one_register_pref_13_4
	bucket_entry_a		trans_value,one_register_pref_13_5
	bucket_entry_a		wait_variable,one_register_pref_13_6
one_register_pref_13_4:
	read_elements_inc		13,1,19,2
	wait_vector		20,3
	read_element		20,0,15
	wait_atom		15,'$VAR'
	read_elements_inc		20,1,15,2
	wait_vector		19,3
	read_element		19,0,17
	wait_atom		17,'$VAR'
	read_elements_inc		19,1,17,2
	collect_value		16
	collect_value		18
	collect_vector		13
	collect_vector		19
	collect_vector		20
	create_goal		16
	set_values_inc		1,1,8
	set_variable		9,3
	set_values_inc		10,10,3
	set_variable		13,4
	set_variable		14,1
	set_marked_value		15,17
	set_marked_value		16,15
	enqueue_goal		16,allocate_on_same_registers_16_0
	create_goal		4
	set_variable		1,2
	set_value		2,3
	set_value		3,15
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,9
	put_value		3,17
	execute		4,ref_vector_4_0
one_register_pref_13_5:
	read_elements_inc		13,1,19,2
	wait_vector		20,3
	read_element		20,0,15
	wait_atom		15,'$VAR'
	read_elements_inc		20,1,15,2
	wait_vector		19,3
	read_element		19,0,17
	wait_atom		17,'$VAR'
	read_elements_inc		19,1,17,2
	collect_value		16
	collect_value		18
	collect_vector		13
	collect_vector		19
	collect_vector		20
	create_goal		16
	set_values_inc		1,1,8
	set_variable		9,3
	set_values_inc		10,10,3
	set_variable		13,4
	set_variable		14,1
	set_marked_value		15,17
	set_marked_value		16,15
	enqueue_goal		16,allocate_on_same_registers_16_0
	create_goal		4
	set_variable		1,2
	set_value		2,3
	set_value		3,15
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,9
	put_value		3,17
	execute		4,ref_vector_4_0
one_register_pref_13_6:
	read_elements_inc		13,1,19,2
	wait_vector		20,3
	read_element		20,0,15
	wait_atom		15,'$VAR'
	read_elements_inc		20,1,15,2
	wait_vector		19,3
	read_element		19,0,17
	wait_atom		17,'$VAR'
	read_elements_inc		19,1,17,2
	collect_value		16
	collect_value		18
	collect_vector		13
	collect_vector		19
	collect_vector		20
	create_goal		16
	set_values_inc		1,1,8
	set_variable		9,3
	set_values_inc		10,10,3
	set_variable		13,4
	set_variable		14,1
	set_marked_value		15,17
	set_marked_value		16,15
	enqueue_goal		16,allocate_on_same_registers_16_0
	create_goal		4
	set_variable		1,2
	set_value		2,3
	set_value		3,15
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,9
	put_value		3,17
	execute		4,ref_vector_4_0
one_register_pref_13_1:
	otherwise		one_register_pref_13_0
	collect_value		13
	get_value		11,12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
one_register_pref_13_12:
	suspend		one_register_pref_13_0
	module_entry		kl1cmp_register
	predicate		allocate_on_same_registers,16
allocate_on_same_registers_16_0:
	try_me_else		allocate_on_same_registers_16_1
	wait_nil		13
	wait_nil		14
	put_values_inc		13,15,2
	execute		14,one_register_pref_bar_14_0
allocate_on_same_registers_16_1:
	otherwise		allocate_on_same_registers_16_0
	try_me_else		allocate_on_same_registers_16_6
	wait_nil		13
	put_value		17,14
	put_values_inc		13,15,3
	execute		15,one_register_pref_foo_15_0
allocate_on_same_registers_16_6:
	try_me_else		allocate_on_same_registers_16_8
	wait_nil		14
	put_value		17,13
	put_values_dec		13,16,2
	put_value		15,17
	execute		15,one_register_pref_foo_15_0
allocate_on_same_registers_16_8:
	otherwise		allocate_on_same_registers_16_0
	collect_value		16
	collect_value		15
	collect_value		14
	collect_value		13
	get_value		11,12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
allocate_on_same_registers_16_15:
	suspend		allocate_on_same_registers_16_0
	module_entry		kl1cmp_register
	predicate		one_register_pref_foo,15
one_register_pref_foo_15_0:
	get_value		3,4
	get_value		1,2
	create_goal		12
	set_variable		1,3
	set_value		2,6
	set_variable		3,16
	set_values_inc		4,8,3
	set_marked_variable		7,10
	set_marked_value		8,13
	set_marked_value		9,14
	set_marked_value		10,15
	set_marked_variable		11,6
	set_marked_variable		12,4
	enqueue_goal		12,one_register_pref_foobar_or_not_12_0
	create_goal		6
	set_variable		1,1
	set_value		2,12
	set_value		3,10
	set_marked_variable		4,8
	set_value		5,4
	set_value		6,15
	enqueue_goal		6,decision_on_answer_6_0
	create_goal		6
	set_variable		1,2
	set_value		2,1
	set_value		3,10
	set_value		4,6
	set_marked_variable		5,1
	set_value		6,15
	enqueue_goal		6,decision_on_answer_6_0
	create_goal		7
	set_variable		1,9
	set_value		2,2
	set_value		3,8
	set_value		4,4
	set_value		5,15
	set_variable		6,2
	set_value		7,10
	enqueue_goal		7,register_available_7_0
	create_goal		7
	set_value		1,11
	set_value		2,9
	set_value		3,6
	set_value		4,1
	set_value		5,15
	set_atom		6,yes
	set_value		7,2
	enqueue_goal		7,register_available_7_0
	create_goal		3
	set_value		1,8
	set_variable		2,2
	set_value		3,4
	enqueue_goal		3,return_greater_3_0
	create_goal		3
	set_variable		1,4
	set_value		2,1
	set_value		3,6
	enqueue_goal		3,return_less_3_0
	create_goal		4
	set_variable		1,6
	set_value		2,16
	set_value		3,14
	set_value		4,8
	enqueue_goal		4,ref_vector_4_0
	create_goal		4
	set_values_dec		1,7,2
	set_value		3,13
	set_value		4,2
	enqueue_goal		4,ref_vector_4_0
	create_goal		4
	set_variable		1,2
	set_value		2,3
	set_value		3,14
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,5
	put_value		3,13
	execute		4,ref_vector_4_0
one_register_pref_foo_15_1:
	suspend		one_register_pref_foo_15_0
	module_entry		kl1cmp_register
	predicate		decision_on_answer,6
decision_on_answer_6_0:
	try_me_else		decision_on_answer_6_1
	wait_atom		3,yes
	put_values_inc		3,4,3
	execute		5,use_register_5_0
decision_on_answer_6_1:
	otherwise		decision_on_answer_6_0
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
decision_on_answer_6_6:
	suspend		decision_on_answer_6_0
	module_entry		kl1cmp_register
	predicate		one_register_pref_foobar_or_not,12
one_register_pref_foobar_or_not_12_0:
	try_me_else		one_register_pref_foobar_or_not_12_1
	wait_atom		7,yes
	put_values_inc		7,8,5
	execute		11,one_register_pref_foobar_11_0
one_register_pref_foobar_or_not_12_1:
	otherwise		one_register_pref_foobar_or_not_12_0
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
one_register_pref_foobar_or_not_12_6:
	suspend		one_register_pref_foobar_or_not_12_0
	module_entry		kl1cmp_register
	predicate		one_register_pref_bar,14
one_register_pref_bar_14_0:
	create_goal		11
	set_variable		1,15
	set_value		2,6
	set_variable		3,16
	set_values_inc		4,8,3
	set_marked_value		7,13
	set_marked_value		8,14
	set_variable		9,6
	set_marked_variable		10,8
	set_marked_variable		11,9
	enqueue_goal		11,one_register_pref_foobar_11_0
	create_goal		11
	set_values_inc		1,1,4
	set_values_inc		5,11,2
	set_integer		7,1
	set_variable		8,1
	set_value		9,6
	set_values_inc		10,8,2
	enqueue_goal		11,find_free_register_11_0
	create_goal		1
	set_value		1,1
	enqueue_goal		1,number_of_registers_1_0
	create_goal		3
	set_variable		1,6
	set_variable		2,2
	set_value		3,9
	enqueue_goal		3,return_greater_3_0
	create_goal		3
	set_variable		1,4
	set_variable		2,1
	set_value		3,8
	enqueue_goal		3,return_less_3_0
	create_goal		4
	set_variable		1,3
	set_value		2,16
	set_value		3,14
	set_value		4,6
	enqueue_goal		4,ref_vector_4_0
	create_goal		4
	set_value		1,7
	set_value		2,3
	set_value		3,13
	set_value		4,2
	enqueue_goal		4,ref_vector_4_0
	create_goal		4
	set_variable		1,2
	set_values_dec		2,15,2
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,5
	put_value		3,13
	execute		4,ref_vector_4_0
one_register_pref_bar_14_1:
	suspend		one_register_pref_bar_14_0
	module_entry		kl1cmp_register
	predicate		one_register_pref_foobar,11
one_register_pref_foobar_11_0:
	create_goal		4
	set_variable		1,12
	set_value		2,6
	set_marked_value		3,8
	set_marked_value		4,9
	enqueue_goal		4,set_vector_4_0
	create_goal		4
	set_value		1,5
	set_value		2,12
	set_marked_value		3,7
	set_value		4,9
	enqueue_goal		4,set_vector_4_0
	create_goal		4
	set_variable		1,5
	set_value		2,4
	set_value		3,8
	set_marked_value		4,11
	enqueue_goal		4,set_vector_4_0
	create_goal		4
	set_value		1,3
	set_value		2,5
	set_value		3,7
	set_value		4,11
	enqueue_goal		4,set_vector_4_0
	create_goal		4
	set_variable		1,3
	set_value		2,2
	set_value		3,8
	set_marked_value		4,10
	enqueue_goal		4,set_vector_4_0
	put_value		2,3
	put_value		3,7
	put_value		4,10
	execute		4,set_vector_4_0
one_register_pref_foobar_11_1:
	suspend		one_register_pref_foobar_11_0
	module_entry		kl1cmp_register
	predicate		return_less,3
return_less_3_0:
	try_me_else		return_less_3_1
	integer		1
	integer		2
	try_me_else		return_less_3_4
	g_less_than		1,2
	get_value		1,3
	proceed
return_less_3_4:
	get_value		2,3
	proceed
return_less_3_1:
	suspend		return_less_3_0
	module_entry		kl1cmp_register
	predicate		return_greater,3
return_greater_3_0:
	try_me_else		return_greater_3_1
	integer		1
	integer		2
	try_me_else		return_greater_3_4
	g_less_than		2,1
	get_value		1,3
	proceed
return_greater_3_4:
	get_value		2,3
	proceed
return_greater_3_1:
	suspend		return_greater_3_0
	module_entry		kl1cmp_register
	predicate		determine_registers,14
determine_registers_14_0:
	try_me_else		determine_registers_14_1
	wait_integer		13,0
	collect_value		14
	get_value		11,12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
determine_registers_14_1:
	otherwise		determine_registers_14_0
	try_me_else		determine_registers_14_6
	vector		9
	integer		14
	g_vector_element		9,14,15
	wait_nil		15
	b_decrement		13,13
	put_marked_value		15,14
	b_increment		15,15
	create_goal		14
	set_variable		1,18
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_variable		5,17
	set_value		6,6
	set_variable		7,16
	set_value		8,8
	set_variable		9,6
	set_value		10,10
	set_variable		11,4
	set_values_inc		12,12,2
	set_value		14,15
	enqueue_goal		14,determine_registers_14_0
	create_goal		15
	set_value		1,1
	set_value		2,18
	set_values_dec		3,3,2
	set_variable		5,2
	set_value		6,17
	set_variable		7,3
	set_value		8,16
	set_value		9,9
	set_value		10,6
	set_value		11,11
	set_value		12,4
	set_variable		13,4
	set_variable		14,1
	set_value		15,14
	enqueue_goal		15,check_void_variable_15_0
	create_goal		4
	set_value		1,7
	set_value		2,3
	set_value		3,14
	set_value		4,1
	enqueue_goal		4,ref_vector_4_0
	put_value		1,5
	put_value		3,14
	execute		4,ref_vector_4_0
determine_registers_14_6:
	otherwise		determine_registers_14_0
	b_decrement		13,13
	b_increment		14,14
	execute		14,determine_registers_14_0
determine_registers_14_12:
	suspend		determine_registers_14_0
	module_entry		kl1cmp_register
	predicate		check_void_variable,15
check_void_variable_15_0:
	try_me_else		check_void_variable_15_1
	wait_value		13,14
	collect_value		13
	collect_value		14
	get_value		11,12
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	put_values_inc		1,9,2
	put_value		3,15
	put_integer		4,0
	execute		4,set_vector_4_0
check_void_variable_15_1:
	otherwise		check_void_variable_15_0
	get_value		7,8
	get_value		5,6
	create_goal		4
	set_values_inc		1,9,2
	set_value		3,15
	set_variable		4,5
	enqueue_goal		4,set_vector_4_0
	create_goal		11
	set_values_inc		1,1,4
	set_values_inc		5,11,2
	set_integer		7,1
	set_variable		8,1
	set_value		9,5
	set_values_inc		10,13,2
	enqueue_goal		11,find_free_register_11_0
	execute		1,number_of_registers_1_0
check_void_variable_15_3:
	suspend		check_void_variable_15_0
	module_entry		kl1cmp_register
	predicate		number_of_registers,1
number_of_registers_1_0:
	get_integer		1,33
	proceed
number_of_registers_1_1:
	suspend		number_of_registers_1_0
	module_entry		kl1cmp_register
	predicate		'$find_free_register/5_0',12
'$find_free_register/5_0_12_0':
	try_me_else		'$find_free_register/5_0_12_1'
	atom		12
	branch_on_atom		12,2,'$find_free_register/5_0_12_1'
	bucket_entry_a		no,'$find_free_register/5_0_12_3'
	bucket_entry_a		yes,'$find_free_register/5_0_12_4'
'$find_free_register/5_0_12_3':
	b_increment		7,7
	execute		11,find_free_register_11_0
'$find_free_register/5_0_12_4':
	collect_value		8
	get_value		3,4
	get_value		1,2
	put_marked_value		9,9
	get_value		9,7
	put_values_inc		1,5,2
	put_values_inc		3,10,2
	put_value		5,9
	execute		5,use_register_5_0
'$find_free_register/5_0_12_1':
	suspend		'$find_free_register/5_0_12_0'
	module_entry		kl1cmp_register
	predicate		find_free_register,11
find_free_register_11_0:
	try_me_else		find_free_register_11_1
	integer		7
	integer		8
	g_less_than		7,8
	create_goal		12
	set_values_inc		1,1,4
	set_variable		5,2
	set_value		6,6
	set_marked_value		7,7
	set_values_inc		8,8,2
	set_marked_value		10,10
	set_marked_value		11,11
	set_variable		12,8
	enqueue_goal		12,'$find_free_register/5_0_12_0'
	put_value		1,5
	put_values_inc		3,10,2
	put_value		5,7
	put_atom		6,yes
	put_value		7,8
	execute		7,register_available_7_0
find_free_register_11_1:
	try_me_else		find_free_register_11_3
	wait_value		7,8
	collect_value		11
	collect_value		10
	collect_value		7
	collect_value		3
	collect_value		8
	get_value		5,6
	get_atom		4,fail
	get_integer		9,0
	put_structured_constant		3,'$SCNST_4'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
find_free_register_11_3:
	suspend		find_free_register_11_0
	module_entry		kl1cmp_register
	predicate		register_available,7
register_available_7_0:
	try_me_else		register_available_7_1
	wait_value		3,4
	collect_value		5
	collect_value		3
	collect_value		4
	get_value		1,2
	get_value		7,6
	proceed
register_available_7_1:
	otherwise		register_available_7_0
	create_goal		9
	set_variable		1,10
	set_value		2,2
	set_variable		3,9
	set_variable		4,8
	set_marked_value		5,3
	set_values_inc		6,4,4
	enqueue_goal		9,register_available_on_one_pc_9_0
	put_value		2,10
	put_values_dec		4,9,2
	execute		5,rep_vector_5_0
register_available_7_3:
	suspend		register_available_7_0
	module_entry		kl1cmp_register
	predicate		register_available_on_one_pc,9
register_available_on_one_pc_9_0:
	try_me_else		register_available_on_one_pc_9_1
	wait_nil		3
	b_increment		5,3
	get_nil		4
	put_values_inc		4,6,4
	execute		7,register_available_7_0
register_available_on_one_pc_9_1:
	otherwise		register_available_on_one_pc_9_0
	create_goal		8
	set_values_inc		1,1,2
	set_variable		3,10
	set_values_inc		4,5,2
	set_marked_value		6,7
	set_values_inc		7,8,2
	enqueue_goal		8,register_free_or_not_8_0
	put_values_inc		1,3,2
	put_value		3,7
	put_value		4,10
	execute		4,get_one_used_element_4_0
register_available_on_one_pc_9_6:
	suspend		register_available_on_one_pc_9_0
	module_entry		kl1cmp_register
	predicate		register_free_or_not,8
register_free_or_not_8_0:
	try_me_else		register_free_or_not_8_1
	wait_atom		3,no
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	get_value		1,2
	get_atom		8,no
	proceed
register_free_or_not_8_1:
	otherwise		register_free_or_not_8_0
	collect_value		3
	b_increment		4,3
	put_values_inc		4,5,4
	execute		7,register_available_7_0
register_free_or_not_8_6:
	suspend		register_free_or_not_8_0
	module_entry		kl1cmp_register
	predicate		get_one_used_element,4
get_one_used_element_4_0:
	try_me_else		get_one_used_element_4_1
	integer		1
	integer		3
	g_decrement		3,5
	put_integer		6,1
	g_shift_left		6,5,5
	g_and		1,5,5
	put_integer		6,0
	g_not_equal		5,6
	get_atom		4,no
	get_value		1,2
	proceed
get_one_used_element_4_1:
	otherwise		get_one_used_element_4_0
	collect_value		3
	get_atom		4,yes
	get_value		1,2
	proceed
get_one_used_element_4_5:
	suspend		get_one_used_element_4_0
	module_entry		kl1cmp_register
	predicate		use_register,5
use_register_5_0:
	create_goal		6
	set_values_inc		1,1,2
	set_variable		3,1
	set_values_inc		4,3,3
	enqueue_goal		6,use_register_6_0
	execute		1,number_of_registers_1_0
use_register_5_1:
	suspend		use_register_5_0
	module_entry		kl1cmp_register
	predicate		use_register,6
use_register_6_0:
	try_me_else		use_register_6_1
	wait_value		4,5
	collect_value		6
	collect_value		4
	collect_value		3
	collect_value		5
	get_value		1,2
	proceed
use_register_6_1:
	otherwise		use_register_6_0
	put_values_dec		9,4,2
	put_values_inc		7,5,2
	put_marked_value		3,9
	put_variable		5,4
	b_set_vector_element		1,3,3,5,1
	put_values_dec		5,10,2
	execute		8,allocate_used_table_element_8_0
use_register_6_3:
	suspend		use_register_6_0
	module_entry		kl1cmp_register
	predicate		allocate_used_table_element,8
allocate_used_table_element_8_0:
	try_me_else		allocate_used_table_element_8_1
	wait_nil		3
	b_increment		6,3
	create_goal		6
	set_values_inc		1,1,2
	set_marked_value		3,5
	set_value		4,3
	set_value		5,7
	set_marked_value		6,8
	enqueue_goal		6,use_register_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,8
	set_value		3,4
	enqueue_goal		3,reserve_register_3_0
	put_value		1,5
	execute		2,new_used_table_element_2_0
allocate_used_table_element_8_1:
	otherwise		allocate_used_table_element_8_0
	b_increment		6,6
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,5,3
	set_marked_value		6,8
	enqueue_goal		6,use_register_6_0
	put_value		1,3
	put_value		2,8
	put_value		3,4
	execute		3,reserve_register_3_0
allocate_used_table_element_8_6:
	suspend		allocate_used_table_element_8_0
	module_entry		kl1cmp_register
	predicate		reserve_register,3
reserve_register_3_0:
	try_me_else		reserve_register_3_1
	integer		2
	put_integer		4,32
	g_less_than		4,2
	get_value		1,3
	proceed
reserve_register_3_1:
	otherwise		reserve_register_3_0
	try_me_else		reserve_register_3_5
	wait_integer		2,0
	get_value		1,3
	proceed
reserve_register_3_5:
	b_decrement		2,2
	put_integer		4,1
	b_shift_left		4,2,2
	b_or		1,2,1
	get_value		3,1
	proceed
reserve_register_3_7:
	suspend		reserve_register_3_0
	module_entry		kl1cmp_register
	predicate		new_used_table_element,2
new_used_table_element_2_0:
	collect_value		1
	get_integer		2,0
	proceed
new_used_table_element_2_1:
	suspend		new_used_table_element_2_0
	module_entry		kl1cmp_register
	predicate		ref_vector,4
ref_vector_4_0:
	put_marked_value		5,4
	b_set_vector_element		1,3,1,5,3
	get_value		1,4
	get_value		3,2
	proceed
ref_vector_4_1:
	suspend		ref_vector_4_0
	module_entry		kl1cmp_register
	predicate		set_vector,4
set_vector_4_0:
	b_set_vector_element		1,3,1,4,3
	get_value		3,2
	proceed
set_vector_4_1:
	suspend		set_vector_4_0
	module_entry		kl1cmp_register
	predicate		rep_vector,5
rep_vector_5_0:
	b_set_vector_element		1,3,1,5,3
	get_value		1,4
	get_value		3,2
	proceed
rep_vector_5_1:
	suspend		rep_vector_5_0
	module_entry		kl1cmp_register
	predicate		equal,2
equal_2_0:
	get_value		1,2
	proceed
equal_2_1:
	suspend		equal_2_0
	begin_const_section		kl1cmp_register
'$SCNST_0_1':
	define_desc		19,10
	define_integer		1919248468
	define_integer		1936269413
	define_integer		544173600
	define_integer		1969319011
	define_integer		1629513075
	define_integer		1919251558
	define_integer		1953259808
	define_integer		1634628197
	define_integer		1702259060
	define_integer		31084
'$SCNST_0_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_0_1'
	define_atom		[]
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		19,9
	define_integer		1919248468
	define_integer		1936269413
	define_integer		544173600
	define_integer		1635085411
	define_integer		1629513075
	define_integer		1919251558
	define_integer		1752461088
	define_integer		1769435749
	define_integer		25971
'$SCNST_1_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_1_1'
	define_atom		[]
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		11,7
	define_integer		544830036
	define_integer		1663070068
	define_integer		1768975727
	define_integer		1864394092
	define_integer		543515502
	define_integer		1701998445
	define_integer		2112032
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		27,9
	define_integer		1970499145
	define_integer		1667851878
	define_integer		1953391977
	define_integer		1734701600
	define_integer		1702130537
	define_integer		1679830642
	define_integer		1952803941
	define_integer		975201381
	define_integer		32
'$SCNST_3':
	define_string		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		11,8
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1869488229
	define_integer		1869505824
	define_integer		543713141
	define_integer		1768383858
	define_integer		1919251571
	define_integer		3809395
'$SCNST_4_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_4_1'
	define_atom		[]
'$SCNST_4':
	define_vector		'$SCNST_4_0'
