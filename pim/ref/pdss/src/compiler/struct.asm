kl1cmp_struct:
	module		kl1cmp_struct
	entry		struct_processor,5,struct_processor_5_0
	entry		test,0,test_0_0
	entry		calcurate_right_hand,4,calcurate_right_hand_4_0
	module_entry		kl1cmp_struct
	predicate		struct_processor,5
struct_processor_5_0:
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,2
	set_values_inc		4,4,2
	set_nil		6
	set_variable		7,4
	enqueue_goal		7,struct_processor_7_0
	put_value		1,3
	put_value		3,4
	execute		3,struct_header_3_0
struct_processor_5_1:
	suspend		struct_processor_5_0
	module_entry		kl1cmp_struct
	predicate		struct_header,3
struct_header_3_0:
	try_me_else		struct_header_3_1
	jump_on_non_list		2,struct_header_3_3
	put_func		4,2,begin_const_section
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
struct_header_3_3:
	check_nil		2,struct_header_3_1
	collect_value		3
	get_nil		1
	proceed
struct_header_3_1:
	suspend		struct_header_3_0
	module_entry		kl1cmp_struct
	predicate		struct_processor,7
struct_processor_7_0:
	try_me_else		struct_processor_7_1
	jump_on_non_list		5,struct_processor_7_3
	read_car		5,8
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,read_predicate
	read_elements_inc		8,1,10,2
	read_cdr		5,12
	try_me_else		struct_processor_7_6
	wait_nil		6
	put_reused_func		6,8,read_predicate
	write_element_variable		6,1,13
	write_element_variable		6,2,9
	get_reused_list_val_var		1,8,5,6,5
	create_goal		7
	set_value		1,5
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_value		5,12
	set_variable		6,8
	set_value		7,7
	enqueue_goal		7,struct_processor_7_0
	put_value		1,3
	put_value		3,13
	put_values_inc		4,9,3
	put_nil		7
	execute		8,struct_process_8_0
struct_processor_7_6:
	try_me_else		struct_processor_7_1
	put_nil		13
	g_diff		6,13
	collect_value		13
	put_reused_func		8,8,read_predicate
	write_element_variable		8,1,13
	write_element_variable		8,2,9
	get_reused_list_val_var		1,14,5,8,5
	get_value		6,7
	create_goal		5
	set_value		1,5
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_value		5,12
	enqueue_goal		5,struct_processor__5_0
	put_value		1,3
	put_value		3,13
	put_values_inc		4,9,3
	put_void		7
	put_void		8
	execute		8,struct_process_8_0
struct_processor_7_3:
	check_nil		5,struct_processor_7_1
	try_me_else		struct_processor_7_8
	wait_nil		6
	get_value		3,4
	get_value		1,2
	get_atom		7,dummy
	proceed
struct_processor_7_8:
	get_value		3,4
	get_value		1,2
	get_value		7,6
	proceed
struct_processor_7_1:
	suspend		struct_processor_7_0
	module_entry		kl1cmp_struct
	predicate		struct_processor_,5
struct_processor__5_0:
	try_me_else		struct_processor__5_1
	jump_on_non_list_var_var		5,struct_processor__5_3,9,6
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,read_predicate
	read_elements_inc		9,1,7,2
	put_reused_func		9,9,read_predicate
	write_element_variable		9,1,11
	write_element_variable		9,2,10
	get_reused_list_val_var		1,12,5,9,5
	create_goal		5
	set_value		1,5
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_value		5,6
	enqueue_goal		5,struct_processor__5_0
	put_value		1,3
	put_values_dec		3,11,2
	put_values_inc		5,7,2
	put_void		7
	put_void		8
	execute		8,struct_process_8_0
struct_processor__5_3:
	check_nil		5,struct_processor__5_1
	get_value		3,4
	get_value		1,2
	proceed
struct_processor__5_1:
	suspend		struct_processor__5_0
	module_entry		kl1cmp_struct
	predicate		struct_process,8
struct_process_8_0:
	try_me_else		struct_process_8_1
	jump_on_non_atom		4,struct_process_8_3
	test_atom		4,directive,struct_process_8_1
	get_value		1,2
	put_marked_value		3,3
	get_value		3,5
	get_atom		6,directive
	put_value		1,3
	put_values_inc		2,7,2
	execute		3,find_module_declaration_3_0
struct_process_8_3:
	check_vector		4,3,struct_process_8_1
	read_element		4,0,9
	wait_atom		9,/
	read_elements_inc		4,1,9,2
	b_merge		11,12
	put_reused_func		4,4,/
	write_element_marked_value		4,1,9
	write_element_marked_value		4,2,10
	get_vector_value		6,4
	get_value		7,8
	create_goal		5
	set_values_inc		1,1,2
	set_value		3,11
	set_value		4,3
	set_value		5,5
	enqueue_goal		5,convert_clauses_5_0
	put_func		2,3,/
	write_elements_inc		2,1,9,2
	put_value		1,12
	execute		2,label_generator_2_0
struct_process_8_1:
	otherwise		struct_process_8_0
	try_me_else		struct_process_8_9
	atom		4
	get_value		1,2
	get_value		3,5
	get_value		6,4
	get_value		7,8
	proceed
struct_process_8_9:
	suspend		struct_process_8_0
	module_entry		kl1cmp_struct
	predicate		find_module_declaration,3
find_module_declaration_3_0:
	try_me_else		find_module_declaration_3_1
	wait_list_var_var		1,6,4
	wait_vector		6,2
	read_element		6,0,5
	wait_atom		5,:-
	read_element		6,1,7
	wait_vector		7,2
	read_element		7,0,5
	wait_atom		5,module
	read_element		7,1,5
	collect_list		1
	collect_value		2
	collect_value		4
	collect_vector		6
	collect_vector		7
	get_value		5,3
	proceed
find_module_declaration_3_1:
	otherwise		find_module_declaration_3_0
	try_me_else		find_module_declaration_3_5
	jump_on_non_list_var_var		1,find_module_declaration_3_7,4,5
	collect_list		1
	collect_value		4
	put_value		1,5
	execute		3,find_module_declaration_3_0
find_module_declaration_3_7:
	check_nil		1,find_module_declaration_3_5
	get_value		2,3
	proceed
find_module_declaration_3_5:
	suspend		find_module_declaration_3_0
	module_entry		kl1cmp_struct
	predicate		label_generator,2
label_generator_2_0:
	try_me_else		label_generator_2_1
	wait_vector		2,3
	read_element		2,0,3
	wait_atom		3,/
	read_elements_inc		2,1,3,2
	collect_vector		2
	b_atom_name		3,2
	put_structured_constant		3,'$SCNST_0'
	b_append_string		3,2,2
	put_structured_constant		3,'$SCNST_1'
	b_append_string		2,3,2
	put_variable		3,5
	b_append_string		2,3,2
	put_structured_constant		3,'$SCNST_2'
	b_append_string		2,3,2
	create_goal		3
	set_values_inc		1,1,2
	set_integer		3,0
	enqueue_goal		3,label_generator_3_0
	put_values_inc		1,4,2
	execute		2,convert_integer_to_string_2_0
label_generator_2_1:
	suspend		label_generator_2_0
	module_entry		kl1cmp_struct
	predicate		label_generator,3
label_generator_3_0:
	try_me_else		label_generator_3_1
	jump_on_non_list_var_var		1,label_generator_3_3,8,4
	wait_vector		8,2
	read_element		8,0,5
	wait_atom		5,new_label
	read_element		8,1,5
	collect_list		1
	put_marked_value		1,2
	put_variable		6,7
	b_append_string		1,6,1
	put_marked_value		6,3
	b_increment		6,6
	put_reused_func		8,8,'$SCNST'
	write_element_value		8,1,1
	get_vector_value		5,8
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,label_generator_3_0
	put_value		1,3
	put_value		2,7
	execute		2,convert_integer_to_string_2_0
label_generator_3_3:
	check_nil		1,label_generator_3_1
	collect_value		3
	collect_value		2
	proceed
label_generator_3_1:
	suspend		label_generator_3_0
	module_entry		kl1cmp_struct
	predicate		convert_clauses,5
convert_clauses_5_0:
	try_me_else		convert_clauses_5_1
	jump_on_non_list_var_var		4,convert_clauses_5_3,6,7
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,8
	get_vector_value		3,10
	put_reused_list		3,4
	write_car_variable		3,10
	write_cdr_variable		3,4
	get_list_value		5,3
	create_goal		5
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_value		4,7
	set_value		5,4
	enqueue_goal		5,convert_clauses_5_0
	put_value		2,3
	put_value		3,8
	put_value		4,6
	put_value		5,10
	execute		5,convert_one_block_5_0
convert_clauses_5_3:
	check_nil		4,convert_clauses_5_1
	get_nil		3
	get_value		1,2
	get_nil		5
	proceed
convert_clauses_5_1:
	suspend		convert_clauses_5_0
	module_entry		kl1cmp_struct
	predicate		convert_one_block,5
convert_one_block_5_0:
	try_me_else		convert_one_block_5_1
	jump_on_non_list		4,convert_one_block_5_3
	read_car		4,6
	jump_on_non_atom		6,convert_one_block_5_5
	branch_on_atom		6,2,convert_one_block_5_1
	bucket_entry_a		alternatively,convert_one_block_5_6
	bucket_entry_a		otherwise,convert_one_block_5_7
convert_one_block_5_6:
	read_cdr		4,7
	put_reused_list		4,4
	write_car_atom		4,alternatively
	write_cdr_variable		4,6
	get_list_value		5,4
	put_values_dec		4,7,2
	execute		5,convert_one_block_5_0
convert_one_block_5_7:
	read_cdr		4,7
	put_reused_list		4,4
	write_car_atom		4,otherwise
	write_cdr_variable		4,6
	get_list_value		5,4
	put_values_dec		4,7,2
	execute		5,convert_one_block_5_0
convert_one_block_5_5:
	check_vector		6,3,convert_one_block_5_1
	read_cdr		4,7
	read_element		6,0,8
	wait_atom		8,:-
	read_element		6,1,8
	read_element		6,2,17
	wait_vector		17,3
	read_element		17,0,9
	wait_atom		9,'|'
	read_elements_inc		17,1,9,2
	put_vector		15,4
	write_element_variable		15,0,14
	write_element_variable		15,1,13
	write_element_variable		15,2,12
	write_element_variable		15,3,11
	get_vector_value		3,15
	put_reused_func		3,6,'|'
	write_element_variable		3,1,16
	write_element_variable		3,2,15
	put_reused_func		6,17,:-
	write_element_variable		6,1,17
	write_element_value		6,2,3
	get_reused_list_val_var		5,4,4,6,3
	create_goal		5
	set_variable		1,5
	set_value		2,2
	set_value		3,14
	set_value		4,7
	set_value		5,3
	enqueue_goal		5,convert_one_block_5_0
	create_goal		6
	set_variable		1,6
	set_value		2,17
	set_variable		3,3
	set_value		4,16
	set_variable		5,2
	set_value		6,15
	enqueue_goal		6,convert_guard_unify_6_0
	create_goal		6
	set_variable		1,4
	set_value		2,5
	set_value		3,13
	set_atom		4,active
	set_value		5,10
	set_value		6,2
	enqueue_goal		6,convert_terms_6_0
	create_goal		6
	set_variable		1,2
	set_value		2,4
	set_value		3,12
	set_atom		4,passive
	set_value		5,9
	set_value		6,3
	enqueue_goal		6,convert_terms_6_0
	put_value		3,11
	put_atom		4,passive
	put_value		5,8
	execute		6,convert_one_term_6_0
convert_one_block_5_3:
	check_nil		4,convert_one_block_5_1
	get_nil		3
	get_value		1,2
	get_nil		5
	proceed
convert_one_block_5_1:
	suspend		convert_one_block_5_0
	module_entry		kl1cmp_struct
	predicate		convert_guard_unify,6
convert_guard_unify_6_0:
	create_goal		7
	set_variable		1,8
	set_values_inc		2,1,2
	set_variable		4,7
	set_values_inc		5,4,3
	enqueue_goal		7,convert_arg_to_list_7_0
	put_value		1,8
	put_nil		2
	put_value		4,7
	put_atom		5,true
	execute		5,extract_struct_unify_5_0
convert_guard_unify_6_1:
	suspend		convert_guard_unify_6_0
	module_entry		kl1cmp_struct
	predicate		extract_struct_unify,5
extract_struct_unify_5_0:
	try_me_else		extract_struct_unify_5_1
	wait_vector		3,3
	read_element		3,0,6
	wait_atom		6,','
	read_elements_inc		3,1,6,2
	collect_vector		3
	create_goal		5
	set_variable		1,3
	set_value		2,2
	set_value		3,7
	set_variable		4,7
	set_value		5,5
	enqueue_goal		5,extract_struct_unify_5_0
	put_value		2,3
	put_value		3,6
	put_value		5,7
	execute		5,extract_struct_unify_5_0
extract_struct_unify_5_1:
	otherwise		extract_struct_unify_5_0
	try_me_else		extract_struct_unify_5_6
	wait_vector		3,3
	read_element		3,0,6
	wait_atom		6,=
	read_element		3,1,7
	try_me_else		extract_struct_unify_5_9
	jump_on_non_list		7,extract_struct_unify_5_11
	read_element		3,2,8
	read_car		7,6
	read_cdr		7,9
	put_reused_list_val_val		7,7,6,9
	put_reused_func		3,3,=
	write_elements_dec		3,1,8,2
	put_list_val_val		6,3,2
	get_list_value		1,6
	get_value		4,5
	proceed
extract_struct_unify_5_11:
	check_vector		7,3,extract_struct_unify_5_9
	read_element		3,2,13
	wait_vector		13,3
	read_element		13,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		13,1,8,2
	read_element		7,0,10
	wait_atom		10,'$VAR'
	read_elements_inc		7,1,10,2
	integer		10
	string		11
	g_string		11,12,14
	wait_integer		14,8
	integer		8
	string		9
	g_string		9,12,14
	wait_integer		14,8
	get_value		1,2
	put_reused_func		1,3,'$VAR'
	write_elements_inc		1,1,8,2
	put_reused_func		2,13,'$VAR'
	write_elements_inc		2,1,10,2
	put_reused_func		3,7,=
	write_elements_dec		3,1,2,2
	put_func		1,3,','
	write_element_value		1,1,3
	write_element_value		1,2,5
	get_vector_value		4,1
	proceed
extract_struct_unify_5_9:
	read_element		3,2,8
	try_me_else		extract_struct_unify_5_6
	wait_list_var_var		8,6,9
	put_reused_list_val_val		8,8,6,9
	put_reused_func		3,3,=
	write_elements_inc		3,1,7,2
	put_list_val_val		6,3,2
	get_list_value		1,6
	get_value		4,5
	proceed
extract_struct_unify_5_6:
	otherwise		extract_struct_unify_5_0
	try_me_else		extract_struct_unify_5_25
	wait_vector		3,3
	read_element		3,0,6
	wait_atom		6,=
	read_element		3,1,7
	vector		7
	test_arity		7,3,extract_struct_unify_5_29
	try_me_else		extract_struct_unify_5_29
	read_element		3,2,8
	read_element		7,0,9
	wait_atom		9,'$VAR'
	read_elements_inc		7,1,9,2
	vector		8
	g_vector		8,11
	integer		9
	string		10
	g_string		10,11,12
	wait_integer		12,8
	put_reused_func		3,3,'$VAR'
	write_elements_inc		3,1,9,2
	put_reused_func		6,7,=
	write_element_value		6,1,3
	write_element_value		6,2,8
	put_list_val_val		3,6,2
	get_list_value		1,3
	get_value		4,5
	proceed
extract_struct_unify_5_29:
	read_element		3,2,8
	try_me_else		extract_struct_unify_5_25
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,'$VAR'
	read_elements_inc		8,1,9,2
	g_vector		7,11
	integer		9
	string		10
	g_string		10,11,12
	wait_integer		12,8
	put_reused_func		3,3,'$VAR'
	write_elements_inc		3,1,9,2
	put_reused_func		6,8,=
	write_element_value		6,1,3
	write_element_value		6,2,7
	put_list_val_val		3,6,2
	get_list_value		1,3
	get_value		4,5
	proceed
extract_struct_unify_5_25:
	otherwise		extract_struct_unify_5_0
	get_value		1,2
	put_func		1,3,','
	write_element_value		1,1,3
	write_element_value		1,2,5
	get_vector_value		4,1
	proceed
extract_struct_unify_5_43:
	suspend		extract_struct_unify_5_0
	module_entry		kl1cmp_struct
	predicate		convert_arg_to_list,7
convert_arg_to_list_7_0:
	try_me_else		convert_arg_to_list_7_1
	jump_on_non_list		1,convert_arg_to_list_7_3
	read_car		1,8
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,=
	read_elements_inc		8,1,10,2
	read_cdr		1,12
	jump_on_non_atom		2,convert_arg_to_list_7_7
	collect_list		1
	collect_vector		8
	create_goal		7
	set_value		1,12
	set_values_inc		2,2,2
	set_variable		4,8
	set_value		5,5
	set_variable		6,1
	set_value		7,7
	enqueue_goal		7,convert_arg_to_list_7_0
	create_goal		5
	set_marked_value		1,10
	set_marked_value		2,11
	set_value		3,6
	set_value		4,1
	set_atom		5,true
	enqueue_goal		5,convert_arg_to_list_one_part_5_0
	put_values_inc		1,10,2
	put_value		3,4
	put_value		4,8
	put_atom		5,true
	execute		5,convert_arg_to_list_one_part_5_0
convert_arg_to_list_7_7:
	is_vector		2,convert_arg_to_list_7_1
	put_value		13,2
	g_vector		13,2
	collect_list		1
	collect_vector		8
	create_goal		7
	set_value		1,12
	set_variable		2,8
	set_value		3,3
	set_variable		4,1
	set_value		5,5
	set_variable		6,3
	set_value		7,7
	enqueue_goal		7,convert_arg_to_list_7_0
	create_goal		5
	set_marked_value		1,10
	set_marked_value		2,11
	set_value		3,6
	set_value		4,3
	set_atom		5,true
	enqueue_goal		5,convert_arg_to_list_one_part_5_0
	create_goal		5
	set_values_inc		1,10,2
	set_value		3,4
	set_value		4,1
	set_atom		5,true
	enqueue_goal		5,convert_arg_to_list_one_part_5_0
	put_integer		1,0
	put_values_inc		3,10,2
	put_value		5,13
	put_value		6,8
	execute		6,convert_arg_to_list_one_goal_6_0
convert_arg_to_list_7_3:
	check_nil		1,convert_arg_to_list_7_1
	get_value		2,3
	get_value		4,5
	get_value		6,7
	proceed
convert_arg_to_list_7_1:
	suspend		convert_arg_to_list_7_0
	module_entry		kl1cmp_struct
	predicate		convert_arg_to_list_one_part,5
convert_arg_to_list_one_part_5_0:
	try_me_else		convert_arg_to_list_one_part_5_1
	wait_vector		3,3
	read_element		3,0,6
	wait_atom		6,','
	read_elements_inc		3,1,6,2
	collect_vector		3
	create_goal		5
	set_marked_value		1,1
	set_marked_value		2,2
	set_value		3,7
	set_variable		4,7
	set_value		5,5
	enqueue_goal		5,convert_arg_to_list_one_part_5_0
	put_value		3,6
	put_value		5,7
	execute		5,convert_arg_to_list_one_part_5_0
convert_arg_to_list_one_part_5_1:
	otherwise		convert_arg_to_list_one_part_5_0
	try_me_else		convert_arg_to_list_one_part_5_6
	jump_on_non_atom		3,convert_arg_to_list_one_part_5_8
	collect_value		2
	collect_value		1
	put_func		1,3,','
	write_element_value		1,1,3
	write_element_value		1,2,5
	get_vector_value		4,1
	proceed
convert_arg_to_list_one_part_5_8:
	is_vector		3,convert_arg_to_list_one_part_5_6
	put_value		7,3
	g_vector		7,3
	put_values_inc		8,1,2
	put_func		1,3,','
	write_element_variable		1,1,6
	write_element_value		1,2,5
	get_vector_value		4,1
	put_integer		1,0
	put_value		2,3
	put_values_inc		3,8,2
	put_value		5,7
	execute		6,convert_arg_to_list_one_goal_6_0
convert_arg_to_list_one_part_5_6:
	suspend		convert_arg_to_list_one_part_5_0
	module_entry		kl1cmp_struct
	predicate		convert_arg_to_list_one_goal,6
convert_arg_to_list_one_goal_6_0:
	try_me_else		convert_arg_to_list_one_goal_6_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		7,1
	put_variable		9,8
	b_set_vector_element		5,7,5,9,7
	b_increment		1,1
	create_goal		6
	set_values_inc		1,1,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_values_dec		5,7,2
	enqueue_goal		6,convert_arg_to_list_one_goal_6_0
	put_values_inc		1,3,3
	put_value		4,8
	execute		4,convert_one_arg_to_list_4_0
convert_arg_to_list_one_goal_6_1:
	try_me_else		convert_arg_to_list_one_goal_6_3
	wait_value		1,2
	collect_value		4
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,6
	proceed
convert_arg_to_list_one_goal_6_3:
	suspend		convert_arg_to_list_one_goal_6_0
	module_entry		kl1cmp_struct
	predicate		convert_one_arg_to_list,4
convert_one_arg_to_list_4_0:
	try_me_else		convert_one_arg_to_list_4_1
	wait_value		1,3
	collect_value		1
	collect_value		3
	get_value		4,2
	proceed
convert_one_arg_to_list_4_1:
	otherwise		convert_one_arg_to_list_4_0
	try_me_else		convert_one_arg_to_list_4_3
	jump_on_non_list_var_var		3,convert_one_arg_to_list_4_5,5,6
	put_reused_list		8,3
	write_car_variable		8,7
	write_cdr_variable		8,3
	get_list_value		4,8
	create_goal		4
	set_marked_value		1,1
	set_marked_value		2,2
	set_value		3,6
	set_value		4,3
	enqueue_goal		4,convert_one_arg_to_list_4_0
	put_value		3,5
	put_value		4,7
	execute		4,convert_one_arg_to_list_4_0
convert_one_arg_to_list_4_5:
	check_vector		3,3,convert_one_arg_to_list_4_3
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	integer		5
	string		6
	g_string		6,7,8
	wait_integer		8,8
	collect_value		2
	collect_value		1
	put_reused_func		1,3,'$VAR'
	write_elements_inc		1,1,5,2
	get_vector_value		4,1
	proceed
convert_one_arg_to_list_4_3:
	otherwise		convert_one_arg_to_list_4_0
	try_me_else		convert_one_arg_to_list_4_10
	vector		3
	put_value		5,3
	g_vector		5,3
	put_values_inc		7,1,2
	put_value		6,4
	put_integer		1,0
	put_value		2,3
	put_values_inc		3,7,2
	execute		6,convert_one_vect_arg_to_list_6_0
convert_one_arg_to_list_4_10:
	otherwise		convert_one_arg_to_list_4_0
	collect_value		2
	collect_value		1
	get_value		3,4
	proceed
convert_one_arg_to_list_4_14:
	suspend		convert_one_arg_to_list_4_0
	module_entry		kl1cmp_struct
	predicate		convert_one_vect_arg_to_list,6
convert_one_vect_arg_to_list_6_0:
	try_me_else		convert_one_vect_arg_to_list_6_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		7,1
	b_increment		7,7
	put_variable		9,8
	b_set_vector_element		5,1,5,9,1
	create_goal		6
	set_value		1,7
	set_value		2,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_value		5,1
	set_value		6,6
	enqueue_goal		6,convert_one_vect_arg_to_list_6_0
	put_values_inc		1,3,3
	put_value		4,8
	execute		4,convert_one_arg_to_list_4_0
convert_one_vect_arg_to_list_6_1:
	try_me_else		convert_one_vect_arg_to_list_6_3
	wait_value		1,2
	collect_value		4
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,6
	proceed
convert_one_vect_arg_to_list_6_3:
	suspend		convert_one_vect_arg_to_list_6_0
	module_entry		kl1cmp_struct
	predicate		convert_terms,6
convert_terms_6_0:
	try_me_else		convert_terms_6_1
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,','
	read_elements_inc		5,1,7,2
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,9
	get_vector_value		3,11
	put_reused_func		3,5,','
	write_element_variable		3,1,11
	write_element_variable		3,2,5
	get_vector_value		6,3
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_marked_value		4,4
	set_value		5,8
	set_value		6,5
	enqueue_goal		6,convert_terms_6_0
	put_value		2,3
	put_value		3,9
	put_value		5,7
	put_value		6,11
	execute		6,convert_terms_6_0
convert_terms_6_1:
	otherwise		convert_terms_6_0
	execute		6,convert_one_term_6_0
convert_terms_6_6:
	suspend		convert_terms_6_0
	module_entry		kl1cmp_struct
	predicate		convert_one_term,6
convert_one_term_6_0:
	try_me_else		convert_one_term_6_1
	jump_on_non_atom		5,convert_one_term_6_3
	collect_value		4
	get_nil		3
	get_value		1,2
	get_value		5,6
	proceed
convert_one_term_6_3:
	is_vector		5,convert_one_term_6_1
	test_arity		5,3,convert_one_term_6_4
	read_element		5,0,7
	try_me_else		convert_one_term_6_4
	atom		7
	branch_on_atom		7,2,convert_one_term_6_4
	bucket_entry_a		:,convert_one_term_6_6
	bucket_entry_a		@,convert_one_term_6_7
convert_one_term_6_6:
	read_elements_inc		5,1,8,2
	put_reused_func		5,5,:
	write_element_value		5,1,8
	write_element_variable		5,2,7
	get_vector_value		6,5
	put_value		5,9
	put_value		6,7
	execute		6,convert_one_term_6_0
convert_one_term_6_7:
	read_elements_inc		5,1,8,2
	put_reused_func		5,5,@
	write_element_variable		5,1,7
	write_element_value		5,2,9
	get_vector_value		6,5
	put_values_dec		5,8,2
	execute		6,convert_one_term_6_0
convert_one_term_6_4:
	g_vector		5,7
	create_goal		8
	set_values_inc		1,1,3
	set_marked_value		4,4
	set_integer		5,0
	set_marked_value		6,7
	set_variable		7,8
	set_value		8,6
	enqueue_goal		8,make_constant_code_8_0
	put_value		1,4
	put_integer		2,0
	put_value		3,7
	put_value		4,5
	put_value		5,8
	execute		5,convert_args_5_0
convert_one_term_6_1:
	suspend		convert_one_term_6_0
	module_entry		kl1cmp_struct
	predicate		convert_args,5
convert_args_5_0:
	try_me_else		convert_args_5_1
	integer		2
	integer		3
	g_less_than		2,3
	put_marked_value		6,2
	put_variable		8,7
	b_set_vector_element		4,6,4,8,6
	b_increment		2,2
	create_goal		5
	set_marked_value		1,1
	set_values_inc		2,2,2
	set_values_dec		4,6,2
	enqueue_goal		5,convert_args_5_0
	put_integer		2,1
	put_void		3
	put_value		5,7
	execute		5,convert_one_arg_5_0
convert_args_5_1:
	try_me_else		convert_args_5_3
	wait_value		2,3
	collect_value		2
	collect_value		1
	collect_value		3
	get_value		4,5
	proceed
convert_args_5_3:
	suspend		convert_args_5_0
	module_entry		kl1cmp_struct
	predicate		convert_one_arg,5
convert_one_arg_5_0:
	try_me_else		convert_one_arg_5_1
	wait_atom		1,active
	wait_list_var_var		4,6,1
	collect_value		2
	put_variable		2,8
	put_variable		7,9
	b_and		2,7,2
	create_goal		4
	set_values_inc		1,2,2
	put_reused_list		3,4
	write_car_variable		3,7
	write_cdr_variable		3,2
	set_value		3,3
	set_value		4,5
	enqueue_goal		4,check_list_constant_or_not_4_0
	create_goal		5
	set_atom		1,active
	set_integer		2,1
	set_value		3,9
	set_values_inc		4,1,2
	enqueue_goal		5,convert_one_arg_5_0
	put_atom		1,active
	put_integer		2,1
	put_value		3,8
	put_values_inc		4,6,2
	execute		5,convert_one_arg_5_0
convert_one_arg_5_1:
	try_me_else		convert_one_arg_5_3
	wait		4
	switch_on_type		4,convert_one_arg_5_4,convert_one_arg_5_5,convert_one_arg_5_3,convert_one_arg_5_6,convert_one_arg_5_7,convert_one_arg_5_8
convert_one_arg_5_4:
	collect_value		1
	get_value		2,3
	get_value		5,4
	proceed
convert_one_arg_5_5:
	collect_value		1
	get_value		2,3
	get_value		5,4
	proceed
convert_one_arg_5_6:
	test_arity		4,3,convert_one_arg_5_3
	read_element		4,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		4,1,6,2
	integer		6
	string		7
	g_string		7,8,9
	wait_integer		9,8
	collect_value		2
	collect_value		1
	get_integer		3,0
	put_reused_func		1,4,'$VAR'
	write_elements_inc		1,1,6,2
	get_vector_value		5,1
	proceed
convert_one_arg_5_7:
	g_string		4,6,7
	collect_value		1
	get_value		2,3
	put_func		1,4,'$STR'
	write_element_value		1,1,4
	write_elements_inc		1,2,6,2
	get_vector_value		5,1
	proceed
convert_one_arg_5_8:
	is_float		4,convert_one_arg_5_3
	collect_value		1
	get_value		2,3
	get_value		5,4
	proceed
convert_one_arg_5_3:
	otherwise		convert_one_arg_5_0
	try_me_else		convert_one_arg_5_14
	atom		1
	branch_on_atom		1,2,convert_one_arg_5_14
	bucket_entry_a		active,convert_one_arg_5_16
	bucket_entry_a		passive,convert_one_arg_5_17
convert_one_arg_5_16:
	vector		4
	g_vector		4,6
	collect_value		2
	put_value		8,4
	create_goal		5
	set_variable		1,4
	set_value		2,3
	set_marked_value		3,6
	set_variable		4,7
	set_value		5,5
	enqueue_goal		5,check_vect_constant_or_not_5_0
	put_atom		1,active
	put_integer		2,1
	put_value		3,4
	put_integer		4,0
	put_value		5,6
	put_value		6,8
	execute		7,convert_vect_args_7_0
convert_one_arg_5_17:
	jump_on_non_list_var_var		4,convert_one_arg_5_19,6,1
	collect_value		2
	get_integer		3,0
	put_reused_list		3,4
	write_car_variable		3,7
	write_cdr_variable		3,2
	get_list_value		5,3
	create_goal		5
	set_atom		1,passive
	set_integer		2,1
	set_void		3
	set_values_inc		4,1,2
	enqueue_goal		5,convert_one_arg_5_0
	put_atom		1,passive
	put_integer		2,1
	put_void		3
	put_values_inc		4,6,2
	execute		5,convert_one_arg_5_0
convert_one_arg_5_19:
	is_vector		4,convert_one_arg_5_14
	put_value		8,4
	g_vector		8,6
	collect_value		2
	put_value		7,5
	get_integer		3,0
	put_atom		1,passive
	put_integer		2,0
	put_void		3
	put_integer		4,0
	put_value		5,6
	put_value		6,8
	execute		7,convert_vect_args_7_0
convert_one_arg_5_14:
	suspend		convert_one_arg_5_0
	module_entry		kl1cmp_struct
	predicate		convert_vect_args,7
convert_vect_args_7_0:
	try_me_else		convert_vect_args_7_1
	integer		4
	integer		5
	g_less_than		4,5
	put_marked_value		8,4
	put_variable		10,9
	b_set_vector_element		6,8,6,10,8
	b_increment		4,4
	put_variable		11,10
	b_and		2,11,2
	create_goal		7
	set_marked_value		1,1
	set_values_inc		2,2,4
	set_values_dec		6,8,2
	enqueue_goal		7,convert_vect_args_7_0
	put_integer		2,1
	put_value		3,10
	put_value		4,6
	put_value		5,9
	execute		5,convert_one_arg_5_0
convert_vect_args_7_1:
	try_me_else		convert_vect_args_7_3
	wait_value		4,5
	collect_value		4
	collect_value		1
	collect_value		5
	get_value		2,3
	get_value		6,7
	proceed
convert_vect_args_7_3:
	suspend		convert_vect_args_7_0
	module_entry		kl1cmp_struct
	predicate		check_list_constant_or_not,4
check_list_constant_or_not_4_0:
	try_me_else		check_list_constant_or_not_4_1
	integer		1
	jump_on_integer		1,2,check_list_constant_or_not_4_1
	table_entry		check_list_constant_or_not_4_3
	table_entry		check_list_constant_or_not_4_4
check_list_constant_or_not_4_3:
	get_value		4,3
	get_integer		2,0
	proceed
check_list_constant_or_not_4_4:
	wait_list_var_var		3,1,5
	put_func		7,2,'$LIST'
	write_element_variable		7,1,6
	get_vector_value		4,7
	put_reused_list_val_val		3,3,1,5
	get_list_value		6,3
	get_integer		2,1
	proceed
check_list_constant_or_not_4_1:
	suspend		check_list_constant_or_not_4_0
	module_entry		kl1cmp_struct
	predicate		check_vect_constant_or_not,5
check_vect_constant_or_not_5_0:
	try_me_else		check_vect_constant_or_not_5_1
	integer		1
	jump_on_integer		1,2,check_vect_constant_or_not_5_1
	table_entry		check_vect_constant_or_not_5_3
	table_entry		check_vect_constant_or_not_5_4
check_vect_constant_or_not_5_3:
	collect_value		3
	get_value		5,4
	get_integer		2,0
	proceed
check_vect_constant_or_not_5_4:
	put_func		1,3,'$VECT'
	write_elements_dec		1,1,4,2
	get_vector_value		5,1
	get_integer		2,1
	proceed
check_vect_constant_or_not_5_1:
	suspend		check_vect_constant_or_not_5_0
	module_entry		kl1cmp_struct
	predicate		define_desc,4
define_desc_4_0:
	try_me_else		define_desc_4_1
	string		1
	g_string		1,5,6
	put_value		10,3
	put_integer		3,32
	put_marked_value		7,6
	b_divide		3,7,3
	put_marked_value		7,5
	put_marked_value		8,3
	b_divide		7,8,7
	b_modulo		5,3,5
	put_marked_variable		8,9
	b_new_string		8,8,6
	b_append_string		1,8,1
	create_goal		5
	set_marked_value		1,10
	set_integer		2,0
	set_value		3,3
	set_value		4,1
	set_value		5,4
	enqueue_goal		5,define_int_5_0
	create_goal		3
	set_value		1,6
	set_value		2,9
	set_value		3,2
	enqueue_goal		3,define_type_3_0
	put_value		1,3
	put_value		2,5
	put_value		3,9
	put_value		4,7
	put_value		5,10
	execute		5,not_used_5_0
define_desc_4_1:
	suspend		define_desc_4_0
	module_entry		kl1cmp_struct
	predicate		not_used,5
not_used_5_0:
	try_me_else		not_used_5_1
	wait_integer		2,0
	collect_value		1
	get_integer		3,0
	get_value		5,4
	proceed
not_used_5_1:
	try_me_else		not_used_5_3
	put_integer		6,0
	g_diff		2,6
	b_subtract		1,2,1
	get_value		3,1
	b_increment		4,1
	get_value		5,1
	proceed
not_used_5_3:
	suspend		not_used_5_0
	module_entry		kl1cmp_struct
	predicate		define_type,3
define_type_3_0:
	try_me_else		define_type_3_1
	wait_integer		1,0
	put_integer		1,3
	b_shift_left		2,1,1
	get_value		3,1
	proceed
define_type_3_1:
	otherwise		define_type_3_0
	try_me_else		define_type_3_6
	integer		1
	put_integer		4,4
	g_less_than		1,4
	put_integer		4,1
	b_and		1,4,1
	put_integer		4,7
	b_shift_left		1,4,1
	put_integer		4,3
	b_shift_left		2,4,2
	b_or		1,2,1
	put_integer		2,1
	b_or		1,2,1
	get_value		3,1
	proceed
define_type_3_6:
	otherwise		define_type_3_0
	try_me_else		define_type_3_10
	integer		1
	put_integer		4,8
	g_less_than		1,4
	put_integer		4,3
	b_and		1,4,1
	put_integer		4,6
	b_shift_left		1,4,1
	put_integer		4,3
	b_shift_left		2,4,2
	b_or		1,2,1
	put_integer		2,2
	b_or		1,2,1
	get_value		3,1
	proceed
define_type_3_10:
	otherwise		define_type_3_0
	try_me_else		define_type_3_14
	integer		1
	put_integer		4,16
	g_less_than		1,4
	put_integer		4,7
	b_and		1,4,1
	put_integer		4,5
	b_shift_left		1,4,1
	put_integer		4,3
	b_shift_left		2,4,2
	b_or		1,2,1
	put_integer		2,3
	b_or		1,2,1
	get_value		3,1
	proceed
define_type_3_14:
	otherwise		define_type_3_0
	try_me_else		define_type_3_18
	integer		1
	put_integer		4,32
	g_less_than		1,4
	put_integer		4,15
	b_and		1,4,1
	put_integer		4,4
	b_shift_left		1,4,1
	put_integer		4,3
	b_shift_left		2,4,2
	b_and		1,2,1
	put_integer		2,4
	b_or		1,2,1
	get_value		3,1
	proceed
define_type_3_18:
	otherwise		define_type_3_0
	try_me_else		define_type_3_22
	wait_integer		1,32
	collect_value		2
	get_integer		3,5
	proceed
define_type_3_22:
	suspend		define_type_3_0
	module_entry		kl1cmp_struct
	predicate		convert_integer_to_string,2
convert_integer_to_string_2_0:
	try_me_else		convert_integer_to_string_2_1
	integer		1
	put_integer		3,10
	g_not_less_than		1,3
	put_marked_value		3,1
	put_integer		4,10
	b_modulo		3,4,3
	put_integer		4,10
	b_divide		1,4,1
	put_structured_constant		4,'$SCNST_3'
	put_integer		5,1
	b_substring		4,3,5,3,4
	put_variable		5,4
	b_append_string		5,3,3
	get_value		3,2
	put_value		2,4
	execute		2,convert_integer_to_string_2_0
convert_integer_to_string_2_1:
	otherwise		convert_integer_to_string_2_0
	put_structured_constant		3,'$SCNST_4'
	put_integer		4,1
	b_substring		3,1,4,3,1
	get_value		3,2
	proceed
convert_integer_to_string_2_5:
	suspend		convert_integer_to_string_2_0
	module_entry		kl1cmp_struct
	predicate		define_int,5
define_int_5_0:
	try_me_else		define_int_5_1
	wait_integer		1,0
	collect_value		4
	collect_value		3
	collect_value		2
	get_nil		5
	proceed
define_int_5_1:
	try_me_else		define_int_5_3
	put_integer		6,0
	g_diff		1,6
	b_decrement		1,1
	put_marked_value		6,2
	put_marked_value		7,3
	b_substring		4,6,7,4,6
	put_list		9
	write_car_variable		9,7
	write_cdr_variable		9,8
	get_list_value		5,9
	b_add		2,3,2
	create_goal		5
	set_values_inc		1,1,3
	set_value		4,6
	set_value		5,8
	enqueue_goal		5,define_int_5_0
	put_values_inc		1,3,2
	put_integer		3,0
	put_value		4,7
	execute		4,define_one_word_4_0
define_int_5_3:
	suspend		define_int_5_0
	module_entry		kl1cmp_struct
	predicate		define_one_word,4
define_one_word_4_0:
	try_me_else		define_one_word_4_1
	integer		1
	test_integer		1,0,define_one_word_4_3
	collect_value		2
	get_value		3,4
	proceed
define_one_word_4_3:
	put_integer		5,0
	g_less_than		5,1
	string		2
	g_string		2,5,6
	b_decrement		1,1
	put_marked_value		5,1
	b_string_element		2,5,2,5
	b_shift_left		3,6,3
	b_add		3,2,2
	put_value		3,2
	put_value		2,5
	execute		4,define_one_word_4_0
define_one_word_4_1:
	suspend		define_one_word_4_0
	module_entry		kl1cmp_struct
	predicate		calcurate_right_hand,4
calcurate_right_hand_4_0:
	create_goal		4
	set_variable		1,6
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	enqueue_goal		4,decision_on_flg_4_0
	put_value		2,6
	put_value		4,5
	execute		4,is_integer_4_0
calcurate_right_hand_4_1:
	suspend		calcurate_right_hand_4_0
	module_entry		kl1cmp_struct
	predicate		decision_on_flg,4
decision_on_flg_4_0:
	try_me_else		decision_on_flg_4_1
	integer		1
	jump_on_integer		1,2,decision_on_flg_4_1
	table_entry		decision_on_flg_4_3
	table_entry		decision_on_flg_4_4
decision_on_flg_4_3:
	get_integer		2,0
	get_value		3,4
	proceed
decision_on_flg_4_4:
	get_integer		2,1
	put_values_inc		1,3,2
	execute		2,calcurate_2_0
decision_on_flg_4_1:
	suspend		decision_on_flg_4_0
	module_entry		kl1cmp_struct
	predicate		is_integer,4
is_integer_4_0:
	try_me_else		is_integer_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	integer		5
	string		6
	g_string		6,7,8
	wait_integer		8,8
	collect_value		1
	get_integer		2,0
	put_reused_func		1,3,'$VAR'
	write_elements_inc		1,1,5,2
	get_vector_value		4,1
	proceed
is_integer_4_1:
	otherwise		is_integer_4_0
	try_me_else		is_integer_4_6
	jump_on_non_integer		3,is_integer_4_8
	get_value		1,2
	get_value		4,3
	proceed
is_integer_4_8:
	check_vector		3,3,is_integer_4_6
	read_elements_inc		3,0,5,3
	integer		6
	integer		7
	get_value		1,2
	put_reused_vector		1,3
	write_elements_inc		1,0,5,3
	get_vector_value		4,1
	proceed
is_integer_4_6:
	otherwise		is_integer_4_0
	try_me_else		is_integer_4_13
	wait_vector		3,3
	read_elements_inc		3,0,5,2
	try_me_else		is_integer_4_15
	integer		6
	read_element		3,2,7
	put_variable		9,8
	b_and		1,9,1
	get_value		1,2
	put_reused_vector		1,3
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,5
	get_vector_value		4,1
	put_integer		1,1
	put_values_dec		2,8,2
	put_value		4,5
	execute		4,calcurate_right_hand_4_0
is_integer_4_15:
	read_element		3,2,7
	try_me_else		is_integer_4_13
	integer		7
	put_variable		9,8
	b_and		1,9,1
	get_value		1,2
	put_reused_vector		1,3
	write_element_value		1,0,5
	write_element_variable		1,1,5
	write_element_value		1,2,7
	get_vector_value		4,1
	put_integer		1,1
	put_value		2,8
	put_values_dec		3,6,2
	execute		4,calcurate_right_hand_4_0
is_integer_4_13:
	otherwise		is_integer_4_0
	try_me_else		is_integer_4_25
	wait_vector		3,3
	read_elements_inc		3,0,5,3
	collect_value		1
	put_variable		1,8
	put_variable		10,9
	b_and		1,10,1
	get_value		1,2
	put_reused_vector		2,3
	write_element_value		2,0,5
	write_element_variable		2,1,5
	write_element_variable		2,2,1
	get_vector_value		4,2
	create_goal		4
	set_integer		1,1
	set_value		2,9
	set_value		3,7
	set_value		4,1
	enqueue_goal		4,calcurate_right_hand_4_0
	put_integer		1,1
	put_value		2,8
	put_values_dec		3,6,2
	execute		4,calcurate_right_hand_4_0
is_integer_4_25:
	otherwise		is_integer_4_0
	collect_value		1
	get_integer		2,0
	get_value		3,4
	proceed
is_integer_4_30:
	suspend		is_integer_4_0
	module_entry		kl1cmp_struct
	predicate		calcurate,2
calcurate_2_0:
	try_me_else		calcurate_2_1
	vector		1
	jump_on_arity		1,4,calcurate_2_1
	table_entry		calcurate_2_1
	table_entry		calcurate_2_1
	table_entry		calcurate_2_3
	table_entry		calcurate_2_4
calcurate_2_3:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,calcurate_2_1
	bucket_entry_a		-,calcurate_2_6
	bucket_entry_a		\,calcurate_2_7
	bucket_entry_a		abs,calcurate_2_8
calcurate_2_6:
	read_element		1,1,4
	integer		4
	collect_vector		1
	b_minus		4,1
	get_value		2,1
	proceed
calcurate_2_7:
	read_element		1,1,4
	integer		4
	collect_vector		1
	b_complement		4,1
	get_value		2,1
	proceed
calcurate_2_8:
	read_element		1,1,4
	integer		4
	try_me_else		calcurate_2_10
	put_integer		5,0
	g_not_less_than		4,5
	collect_vector		1
	get_value		2,4
	proceed
calcurate_2_10:
	collect_vector		1
	b_minus		4,1
	get_value		2,1
	proceed
calcurate_2_4:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,12,calcurate_2_1
	bucket_entry_a		*,calcurate_2_12
	bucket_entry_a		+,calcurate_2_13
	bucket_entry_a		-,calcurate_2_14
	bucket_entry_a		/,calcurate_2_15
	bucket_entry_a		/\,calcurate_2_16
	bucket_entry_a		<<,calcurate_2_17
	bucket_entry_a		>>,calcurate_2_18
	bucket_entry_a		\/,calcurate_2_19
	bucket_entry_a		max,calcurate_2_20
	bucket_entry_a		min,calcurate_2_21
	bucket_entry_a		mod,calcurate_2_22
	bucket_entry_a		xor,calcurate_2_23
calcurate_2_12:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_multiply		4,5,1
	get_value		2,1
	proceed
calcurate_2_13:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_add		4,5,1
	get_value		2,1
	proceed
calcurate_2_14:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_subtract		4,5,1
	get_value		2,1
	proceed
calcurate_2_15:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_divide		4,5,1
	get_value		2,1
	proceed
calcurate_2_16:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_and		4,5,1
	get_value		2,1
	proceed
calcurate_2_17:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_shift_left		4,5,1
	get_value		2,1
	proceed
calcurate_2_18:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_shift_right		4,5,1
	get_value		2,1
	proceed
calcurate_2_19:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_or		4,5,1
	get_value		2,1
	proceed
calcurate_2_20:
	read_element		1,1,4
	integer		4
	read_element		1,2,5
	integer		5
	try_me_else		calcurate_2_26
	g_not_less_than		4,5
	collect_vector		1
	get_value		2,4
	proceed
calcurate_2_26:
	collect_vector		1
	get_value		2,5
	proceed
calcurate_2_21:
	read_element		1,1,4
	integer		4
	read_element		1,2,5
	integer		5
	try_me_else		calcurate_2_29
	g_not_less_than		5,4
	collect_vector		1
	get_value		2,4
	proceed
calcurate_2_29:
	collect_vector		1
	get_value		2,5
	proceed
calcurate_2_22:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_modulo		4,5,1
	get_value		2,1
	proceed
calcurate_2_23:
	read_elements_inc		1,1,4,2
	integer		4
	integer		5
	collect_vector		1
	b_exclusive_or		4,5,1
	get_value		2,1
	proceed
calcurate_2_1:
	otherwise		calcurate_2_0
	get_value		1,2
	proceed
calcurate_2_47:
	suspend		calcurate_2_0
	module_entry		kl1cmp_struct
	predicate		make_constant_code,8
make_constant_code_8_0:
	try_me_else		make_constant_code_8_1
	integer		5
	integer		6
	g_less_than		5,6
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,9
	get_vector_value		3,11
	put_marked_value		3,5
	put_variable		12,11
	b_set_vector_element		7,3,7,12,3
	b_increment		5,5
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,10
	set_marked_value		4,4
	set_values_inc		5,5,2
	set_value		7,3
	set_value		8,8
	enqueue_goal		8,make_constant_code_8_0
	put_value		2,12
	put_value		3,9
	put_value		5,7
	put_value		6,11
	execute		6,check_constant_top_6_0
make_constant_code_8_1:
	try_me_else		make_constant_code_8_3
	wait_value		5,6
	collect_value		5
	collect_value		4
	collect_value		6
	get_nil		3
	get_value		1,2
	get_value		7,8
	proceed
make_constant_code_8_3:
	suspend		make_constant_code_8_0
	module_entry		kl1cmp_struct
	predicate		check_constant_top,6
check_constant_top_6_0:
	try_me_else		check_constant_top_6_1
	wait_atom		4,active
	vector		5
	jump_on_arity		5,4,check_constant_top_6_1
	table_entry		check_constant_top_6_1
	table_entry		check_constant_top_6_1
	table_entry		check_constant_top_6_4
	table_entry		check_constant_top_6_5
check_constant_top_6_4:
	read_element		5,0,7
	wait_atom		7,'$LIST'
	read_element		5,1,8
	wait_list_var_var		8,4,7
	put_reused_func		5,5,new_label
	write_element_marked_variable		5,1,10
	put_reused_list_val_var		8,8,5,9
	put_func		5,2,new_label
	write_element_marked_variable		5,1,11
	put_list_val_val		12,5,8
	get_list_value		3,12
	put_func		3,2,define_list
	write_element_value		3,1,10
	put_list_val_val		5,3,2
	put_list_val_val		2,11,5
	get_value		6,11
	put_list_val_val		5,4,7
	put_value		3,9
	put_value		4,5
	put_value		5,10
	execute		5,construct_constant_code_5_0
check_constant_top_6_5:
	read_element		5,0,7
	wait_atom		7,'$VECT'
	read_elements_inc		5,1,7,2
	vector		7
	g_vector		7,9
	wait_value		9,8
	collect_value		8
	collect_value		9
	collect_vector		5
	put_func		4,2,new_label
	write_element_marked_variable		4,1,9
	put_list_val_var		5,4,8
	put_func		4,2,new_label
	write_element_marked_variable		4,1,10
	put_list_val_val		11,4,5
	get_list_value		3,11
	put_func		3,2,define_vector
	write_element_value		3,1,9
	put_list_val_val		4,3,2
	put_list_val_val		2,10,4
	get_value		6,10
	put_values_dec		3,8,2
	put_value		5,9
	execute		5,construct_constant_code_5_0
check_constant_top_6_1:
	try_me_else		check_constant_top_6_6
	wait		5
	switch_on_type		5,check_constant_top_6_7,check_constant_top_6_8,check_constant_top_6_6,check_constant_top_6_9,check_constant_top_6_6,check_constant_top_6_10
check_constant_top_6_7:
	collect_value		4
	get_nil		3
	get_value		1,2
	get_value		5,6
	proceed
check_constant_top_6_8:
	collect_value		4
	get_nil		3
	get_value		1,2
	get_value		5,6
	proceed
check_constant_top_6_9:
	jump_on_arity		5,5,check_constant_top_6_6
	table_entry		check_constant_top_6_6
	table_entry		check_constant_top_6_6
	table_entry		check_constant_top_6_6
	table_entry		check_constant_top_6_11
	table_entry		check_constant_top_6_12
check_constant_top_6_11:
	read_element		5,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		5,1,7,2
	integer		7
	string		8
	g_string		8,9,10
	wait_integer		10,8
	collect_value		4
	get_nil		3
	get_value		1,2
	put_reused_func		1,5,'$VAR'
	write_elements_inc		1,1,7,2
	get_vector_value		6,1
	proceed
check_constant_top_6_12:
	read_element		5,0,7
	wait_atom		7,'$STR'
	read_elements_inc		5,1,7,3
	string		7
	g_string		7,10,11
	collect_value		9
	collect_value		8
	collect_value		4
	collect_vector		5
	put_nil		8
	put_func		4,2,new_label
	write_element_marked_variable		4,1,9
	put_list_val_val		5,4,8
	put_func		4,2,new_label
	write_element_marked_variable		4,1,8
	put_list_val_val		10,4,5
	get_list_value		3,10
	put_func		3,3,define_desc
	write_element_variable		3,1,10
	write_element_variable		3,2,5
	put_list_val_var		4,3,11
	put_list_val_val		3,9,4
	get_list_value		1,3
	put_func		1,2,define_string
	write_element_value		1,1,9
	put_list_val_val		3,1,2
	put_list_val_val		1,8,3
	get_value		6,8
	create_goal		3
	set_value		1,11
	set_value		2,1
	set_variable		3,4
	enqueue_goal		3,make_define_int_3_0
	put_value		1,7
	put_value		2,10
	put_value		3,5
	execute		4,define_desc_4_0
check_constant_top_6_10:
	is_float		5,check_constant_top_6_6
	collect_value		4
	get_nil		3
	get_value		1,2
	get_value		5,6
	proceed
check_constant_top_6_6:
	otherwise		check_constant_top_6_0
	try_me_else		check_constant_top_6_18
	jump_on_non_list_var_var		5,check_constant_top_6_20,7,8
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,9
	get_vector_value		3,11
	put_reused_list		3,5
	write_car_variable		3,11
	write_cdr_variable		3,5
	get_list_value		6,3
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,10
	set_marked_value		4,4
	set_value		5,8
	set_value		6,5
	enqueue_goal		6,check_constant_top_6_0
	put_value		2,3
	put_value		3,9
	put_value		5,7
	put_value		6,11
	execute		6,check_constant_top_6_0
check_constant_top_6_20:
	is_vector		5,check_constant_top_6_18
	put_value		9,5
	g_vector		9,7
	put_value		8,6
	put_integer		5,0
	put_value		6,7
	put_value		7,9
	execute		8,check_constant_top_vect_8_0
check_constant_top_6_18:
	suspend		check_constant_top_6_0
	module_entry		kl1cmp_struct
	predicate		check_constant_top_vect,8
check_constant_top_vect_8_0:
	try_me_else		check_constant_top_vect_8_1
	integer		5
	integer		6
	g_less_than		5,6
	put_vector		11,2
	write_element_variable		11,0,10
	write_element_variable		11,1,9
	get_vector_value		3,11
	put_marked_value		3,5
	put_variable		12,11
	b_set_vector_element		7,3,7,12,3
	b_increment		5,5
	create_goal		8
	set_variable		1,12
	set_value		2,2
	set_value		3,10
	set_marked_value		4,4
	set_values_inc		5,5,2
	set_value		7,3
	set_value		8,8
	enqueue_goal		8,check_constant_top_vect_8_0
	put_value		2,12
	put_value		3,9
	put_value		5,7
	put_value		6,11
	execute		6,check_constant_top_6_0
check_constant_top_vect_8_1:
	try_me_else		check_constant_top_vect_8_3
	wait_value		5,6
	collect_value		5
	collect_value		4
	collect_value		6
	get_nil		3
	get_value		1,2
	get_value		7,8
	proceed
check_constant_top_vect_8_3:
	suspend		check_constant_top_vect_8_0
	module_entry		kl1cmp_struct
	predicate		make_define_int,3
make_define_int_3_0:
	try_me_else		make_define_int_3_1
	jump_on_non_list_var_var		3,make_define_int_3_3,4,5
	put_func		6,2,define_integer
	write_element_value		6,1,4
	get_reused_list_val_var		1,4,3,6,3
	put_value		1,3
	put_value		3,5
	execute		3,make_define_int_3_0
make_define_int_3_3:
	check_nil		3,make_define_int_3_1
	get_value		1,2
	proceed
make_define_int_3_1:
	suspend		make_define_int_3_0
	module_entry		kl1cmp_struct
	predicate		construct_constant_code,5
construct_constant_code_5_0:
	try_me_else		construct_constant_code_5_1
	wait		4
	switch_on_type		4,construct_constant_code_5_1,construct_constant_code_5_1,construct_constant_code_5_2,construct_constant_code_5_3,construct_constant_code_5_4,construct_constant_code_5_1
construct_constant_code_5_2:
	read_car		4,6
	read_cdr		4,7
	put_vector		8,2
	write_element_variable		8,0,11
	write_element_variable		8,1,10
	put_func		9,2,new_label
	write_element_variable		9,1,12
	put_reused_list_val_val		4,4,9,8
	put_func		8,2,new_label
	write_element_variable		8,1,9
	put_list_val_val		13,8,4
	get_list_value		3,13
	put_list		3
	write_car_variable		3,8
	write_cdr_value		3,2
	put_list		2
	write_car_variable		2,4
	write_cdr_value		2,3
	put_list_val_val		3,5,2
	create_goal		6
	set_variable		1,2
	set_value		2,3
	set_value		3,11
	set_value		4,6
	set_value		5,9
	set_value		6,4
	enqueue_goal		6,construct_constant_code_element_6_0
	put_value		3,10
	put_value		4,7
	put_value		5,12
	put_value		6,8
	execute		6,construct_constant_code_element_6_0
construct_constant_code_5_3:
	put_value		8,4
	g_vector		8,7
	put_func		4,3,define_desc
	write_element_integer		4,1,0
	write_element_marked_value		4,2,7
	put_list_val_var		6,4,9
	put_list_val_val		4,5,6
	create_goal		4
	set_value		1,9
	set_value		2,2
	set_variable		3,6
	set_variable		4,5
	enqueue_goal		4,'C_4_0'
	put_value		2,4
	put_value		4,6
	put_integer		6,0
	execute		8,construct_constant_code_element_8_0
construct_constant_code_5_4:
	g_string		4,6,7
	get_nil		3
	put_func		3,3,define_desc
	write_element_variable		3,1,8
	write_element_variable		3,2,7
	put_list_val_var		6,3,3
	put_list_val_val		9,5,6
	get_list_value		1,9
	create_goal		3
	set_values_dec		1,3,2
	set_variable		3,5
	enqueue_goal		3,make_define_int_3_0
	put_value		1,4
	put_values_dec		2,8,2
	put_value		4,5
	execute		4,define_desc_4_0
construct_constant_code_5_1:
	suspend		construct_constant_code_5_0
	module_entry		kl1cmp_struct
	predicate		'C',4
'C_4_0':
	get_value		1,3
	get_value		2,4
	proceed
'C_4_1':
	suspend		'C_4_0'
	module_entry		kl1cmp_struct
	predicate		construct_constant_code_element,8
construct_constant_code_element_8_0:
	try_me_else		construct_constant_code_element_8_1
	integer		6
	integer		7
	g_less_than		6,7
	put_vector		9,2
	write_element_variable		9,0,13
	write_element_variable		9,1,12
	put_marked_value		10,6
	put_nil		11
	b_set_vector_element		8,10,8,11,10
	b_increment		6,6
	put_func		11,2,new_label
	write_element_variable		11,1,14
	put_list_val_val		15,11,9
	get_list_value		3,15
	put_list		3
	write_car_variable		3,9
	write_cdr_variable		3,11
	get_list_value		4,3
	create_goal		8
	set_variable		1,3
	set_value		2,2
	set_value		3,13
	set_value		4,11
	set_values_inc		5,5,3
	set_value		8,10
	enqueue_goal		8,construct_constant_code_element_8_0
	put_value		2,3
	put_value		3,12
	put_value		4,8
	put_value		5,14
	put_value		6,9
	execute		6,construct_constant_code_element_6_0
construct_constant_code_element_8_1:
	try_me_else		construct_constant_code_element_8_3
	wait_value		6,7
	collect_value		8
	collect_value		6
	collect_value		7
	get_nil		3
	get_value		4,5
	get_value		1,2
	proceed
construct_constant_code_element_8_3:
	suspend		construct_constant_code_element_8_0
	module_entry		kl1cmp_struct
	predicate		construct_constant_code_element,6
construct_constant_code_element_6_0:
	try_me_else		construct_constant_code_element_6_1
	wait		4
	switch_on_type		4,construct_constant_code_element_6_2,construct_constant_code_element_6_3,construct_constant_code_element_6_1,construct_constant_code_element_6_4,construct_constant_code_element_6_1,construct_constant_code_element_6_5
construct_constant_code_element_6_2:
	collect_value		5
	get_nil		3
	get_value		1,2
	put_func		1,2,define_atom
	write_element_value		1,1,4
	get_vector_value		6,1
	proceed
construct_constant_code_element_6_3:
	collect_value		5
	get_nil		3
	get_value		1,2
	put_func		1,2,define_integer
	write_element_value		1,1,4
	get_vector_value		6,1
	proceed
construct_constant_code_element_6_4:
	jump_on_arity		4,5,construct_constant_code_element_6_1
	table_entry		construct_constant_code_element_6_1
	table_entry		construct_constant_code_element_6_1
	table_entry		construct_constant_code_element_6_6
	table_entry		construct_constant_code_element_6_7
	table_entry		construct_constant_code_element_6_8
construct_constant_code_element_6_6:
	read_element		4,0,7
	wait_atom		7,'$LIST'
	read_element		4,1,9
	wait_list_var_var		9,7,8
	put_reused_func		4,4,define_list
	write_element_marked_value		4,1,5
	get_vector_value		6,4
	put_reused_list_val_val		4,9,7,8
	execute		5,construct_constant_code_5_0
construct_constant_code_element_6_7:
	read_element		4,0,7
	wait_atom		7,'$VECT'
	read_elements_inc		4,1,7,2
	vector		7
	g_vector		7,9
	wait_value		9,8
	collect_value		8
	collect_value		9
	collect_vector		4
	put_func		4,2,define_vector
	write_element_marked_value		4,1,5
	get_vector_value		6,4
	put_value		4,7
	execute		5,construct_constant_code_5_0
construct_constant_code_element_6_8:
	read_element		4,0,7
	wait_atom		7,'$STR'
	read_elements_inc		4,1,7,3
	string		7
	g_string		7,10,11
	wait_value		10,8
	wait_value		11,9
	collect_value		9
	collect_value		8
	collect_value		10
	collect_value		11
	collect_vector		4
	put_func		4,2,define_string
	write_element_marked_value		4,1,5
	get_vector_value		6,4
	put_value		4,7
	execute		5,construct_constant_code_5_0
construct_constant_code_element_6_5:
	is_float		4,construct_constant_code_element_6_1
	collect_value		5
	get_nil		3
	get_value		1,2
	put_func		1,2,define_float
	write_element_value		1,1,4
	get_vector_value		6,1
	proceed
construct_constant_code_element_6_1:
	suspend		construct_constant_code_element_6_0
	module_entry		kl1cmp_struct
	predicate		test,0
test_0_0:
	b_merge		2,1
	put_vector		6,3
	write_element_variable		6,0,3
	write_element_variable		6,1,4
	write_element_variable		6,2,5
	get_vector_value		2,6
	create_goal		3
	set_variable		1,2
	set_nil		2
	set_value		3,1
	enqueue_goal		3,out_to_stream_3_0
	create_goal		4
	set_value		1,3
	set_nil		2
	set_variable		3,1
	set_nil		4
	enqueue_goal		4,compiler_4_0
	create_goal		5
	set_variable		1,3
	set_nil		2
	set_value		3,5
	set_nil		4
	set_value		5,1
	enqueue_goal		5,struct_processor_5_0
	create_goal		5
	set_variable		1,1
	set_nil		2
	set_value		3,4
	set_nil		4
	set_value		5,3
	enqueue_goal_external		kl1cmp_reader,create_reader,5
	create_goal		2
	put_list		3
	write_car_atom		3,show
	write_cdr_value		3,2
	set_value		1,3
	put_structured_constant		2,'$SCNST_5'
	set_value		2,2
	enqueue_goal_external		window,create,2
	put_structured_constant		2,'$SCNST_6'
	put_atom		3,r
	execute_external		mpimos_file,create,3
test_0_1:
	suspend		test_0_0
	module_entry		kl1cmp_struct
	predicate		compiler,4
compiler_4_0:
	put_func		5,3,read_predicate
	write_element_variable		5,1,6
	write_element_variable		5,2,7
	get_list_val_var		3,8,5,5
	put_value		3,5
	put_value		5,7
	execute		6,check_clause_6_0
compiler_4_1:
	suspend		compiler_4_0
	module_entry		kl1cmp_struct
	predicate		check_clause,6
check_clause_6_0:
	try_me_else		check_clause_6_1
	wait_atom		5,end_of_file
	get_value		3,4
	get_value		1,2
	get_atom		6,end_of_file
	proceed
check_clause_6_1:
	otherwise		check_clause_6_0
	collect_value		5
	put_list		5
	write_car_atom		5,nl
	write_cdr_variable		5,7
	put_list_val_val		8,6,5
	get_list_value		1,8
	put_func		1,3,read_predicate
	write_element_variable		1,1,6
	write_element_variable		1,2,5
	get_list_val_var		3,9,1,8
	put_value		1,7
	put_value		3,8
	execute		6,check_clause_6_0
check_clause_6_6:
	suspend		check_clause_6_0
	module_entry		kl1cmp_struct
	predicate		out_to_stream,3
out_to_stream_3_0:
	try_me_else		out_to_stream_3_1
	wait_list_var_var		3,4,5
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,8
	put_func		6,2,flush
	write_element_void		6,1
	put_list_val_val		7,6,3
	put_func		3,2,putt
	write_element_value		3,1,4
	put_list_val_val		4,3,7
	get_list_value		1,4
	put_value		1,8
	put_value		3,5
	execute		3,out_to_stream_3_0
out_to_stream_3_1:
	otherwise		out_to_stream_3_0
	try_me_else		out_to_stream_3_5
	wait_nil		3
	put_func		3,2,getl
	write_element_void		3,1
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
out_to_stream_3_5:
	suspend		out_to_stream_3_0
	begin_const_section		kl1cmp_struct
'$SCNST_0_0':
	define_desc		19,2
	define_integer		1313035044
	define_integer		21587
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		27,1
	define_integer		95
'$SCNST_2':
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_3_0':
	define_desc		19,3
	define_integer		858927408
	define_integer		926299444
	define_integer		14648
'$SCNST_4':
'$SCNST_3':
	define_string		'$SCNST_3_0'
'$SCNST_5_0':
	define_desc		3,1
	define_integer		1953719668
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_6_0':
	define_desc		3,2
	define_integer		1953719668
	define_integer		829188910
'$SCNST_6':
	define_string		'$SCNST_6_0'
