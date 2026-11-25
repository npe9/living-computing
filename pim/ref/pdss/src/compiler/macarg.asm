kl1cmp_macro_arg:
	module		kl1cmp_macro_arg
	entry		init_macro_table,1,init_macro_table_1_0
	entry		read_macro_file,5,read_macro_file_5_0
	entry		macro_arg,6,macro_arg_6_0
	module_entry		kl1cmp_macro_arg
	predicate		init_macro_table,1
init_macro_table_1_0:
	put_marked_variable		2,3
	b_new_vector		2,2
	create_goal		3
	set_values_inc		1,1,3
	enqueue_goal		3,macro_table_manager_3_0
	put_value		1,3
	execute		1,macro_table_size_1_0
init_macro_table_1_1:
	suspend		init_macro_table_1_0
	module_entry		kl1cmp_macro_arg
	predicate		read_macro_file,5
read_macro_file_5_0:
	try_me_else		read_macro_file_5_1
	wait		5
	switch_on_type		5,read_macro_file_5_2,read_macro_file_5_1,read_macro_file_5_1,read_macro_file_5_3,read_macro_file_5_4,read_macro_file_5_1
read_macro_file_5_2:
	b_atom_name		5,5
	b_get_library_directory		6
	put_structured_constant		7,'$SCNST_0'
	b_append_string		6,7,6
	put_marked_value		7,5
	b_append_string		6,7,6
	create_goal		7
	set_values_inc		1,1,4
	set_variable		5,4
	set_value		6,5
	set_variable		7,1
	enqueue_goal		7,check_file_status_7_0
	put_value		2,6
	put_atom		3,r
	execute_external		mpimos_file,create,4
read_macro_file_5_3:
	test_arity		5,3,read_macro_file_5_1
	read_element		5,0,6
	wait_atom		6,','
	read_elements_inc		5,1,6,2
	collect_vector		5
	create_goal		5
	set_variable		1,8
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,7
	enqueue_goal		5,read_macro_file_5_0
	put_value		2,8
	put_values_inc		4,5,2
	execute		5,read_macro_file_5_0
read_macro_file_5_4:
	create_goal		7
	set_values_inc		1,1,4
	set_variable		5,4
	set_marked_value		6,5
	set_variable		7,1
	enqueue_goal		7,check_file_status_7_0
	put_value		2,5
	put_atom		3,r
	execute_external		mpimos_file,create,4
read_macro_file_5_1:
	otherwise		read_macro_file_5_0
	put_value		6,5
	put_structured_constant		5,'$SCNST_1'
	put_void		7
	execute		7,check_file_status_7_0
read_macro_file_5_7:
	suspend		read_macro_file_5_0
	module_entry		kl1cmp_macro_arg
	predicate		macro_table_size,1
macro_table_size_1_0:
	get_integer		1,20
	proceed
macro_table_size_1_1:
	suspend		macro_table_size_1_0
	module_entry		kl1cmp_macro_arg
	predicate		check_file_status,7
check_file_status_7_0:
	try_me_else		check_file_status_7_1
	wait_atom		5,success
	collect_value		6
	put_value		5,7
	put_nil		6
	execute		6,make_macro_table_6_0
check_file_status_7_1:
	otherwise		check_file_status_7_0
	collect_value		5
	get_value		3,4
	put_list		3
	write_car_value		3,6
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_2'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	get_nil		7
	proceed
check_file_status_7_6:
	suspend		check_file_status_7_0
	module_entry		kl1cmp_macro_arg
	predicate		make_macro_table,6
make_macro_table_6_0:
	put_func		7,3,getft
	write_element_variable		7,1,8
	write_element_void		7,2
	get_list_val_var		5,9,7,7
	put_value		5,7
	put_value		7,8
	execute		7,check_declaration_and_add_macro_7_0
make_macro_table_6_1:
	suspend		make_macro_table_6_0
	module_entry		kl1cmp_macro_arg
	predicate		check_declaration_and_add_macro,7
check_declaration_and_add_macro_7_0:
	try_me_else		check_declaration_and_add_macro_7_1
	jump_on_non_atom		7,check_declaration_and_add_macro_7_3
	test_atom		7,end_of_file,check_declaration_and_add_macro_7_1
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
check_declaration_and_add_macro_7_3:
	is_vector		7,check_declaration_and_add_macro_7_1
	jump_on_arity		7,4,check_declaration_and_add_macro_7_1
	table_entry		check_declaration_and_add_macro_7_1
	table_entry		check_declaration_and_add_macro_7_1
	table_entry		check_declaration_and_add_macro_7_4
	table_entry		check_declaration_and_add_macro_7_5
check_declaration_and_add_macro_7_4:
	read_element		7,0,8
	wait_atom		8,:-
	read_element		7,1,9
	wait_vector		9,2
	read_element		9,0,8
	wait_atom		8,user_macro
	read_element		9,1,8
	collect_value		8
	collect_vector		7
	collect_vector		9
	put_func		7,3,getft
	write_element_variable		7,1,8
	write_element_void		7,2
	get_list_val_var		5,9,7,7
	put_value		5,7
	put_value		7,8
	execute		7,check_declaration_and_add_macro_7_0
check_declaration_and_add_macro_7_5:
	read_element		7,0,8
	wait_atom		8,=>
	read_elements_inc		7,1,8,2
	vector		8
	put_integer		10,0
	g_vector_element		8,10,10
	wait_atom		10,#
	put_integer		12,1
	g_vector_element		8,12,10
	put_integer		13,2
	g_vector_element		8,13,11
	mark_element		8,12
	mark_element		8,13
	collect_value		8
	put_func		8,4,add_one_macro
	write_elements_inc		8,1,10,2
	write_element_value		8,3,9
	get_list_val_var		3,9,8,8
	put_reused_func		3,7,getft
	write_element_variable		3,1,7
	write_element_void		3,2
	get_list_val_var		5,10,3,9
	put_value		3,8
	put_value		5,9
	execute		7,check_declaration_and_add_macro_7_0
check_declaration_and_add_macro_7_1:
	otherwise		check_declaration_and_add_macro_7_0
	put_list		8
	write_car_value		8,7
	write_cdr_nil		8
	put_structured_constant		7,'$SCNST_3'
	put_func		9,3,error_message
	write_elements_inc		9,1,7,2
	get_list_val_var		1,7,9,8
	put_func		1,3,getft
	write_element_variable		1,1,7
	write_element_void		1,2
	get_list_val_var		5,10,1,9
	put_value		1,8
	put_value		5,9
	execute		7,check_declaration_and_add_macro_7_0
check_declaration_and_add_macro_7_10:
	suspend		check_declaration_and_add_macro_7_0
	module_entry		kl1cmp_macro_arg
	predicate		macro_table_manager,3
macro_table_manager_3_0:
	try_me_else		macro_table_manager_3_1
	jump_on_non_list		1,macro_table_manager_3_3
	read_car		1,4
	wait_vector		4,4
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,macro_table_manager_3_1
	bucket_entry_a		add_one_macro,macro_table_manager_3_6
	bucket_entry_a		get_macro_arg,macro_table_manager_3_7
macro_table_manager_3_6:
	read_cdr		1,6
	read_elements_inc		4,1,7,3
	collect_list		1
	collect_vector		4
	put_values_dec		4,3,2
	create_goal		3
	set_value		1,6
	set_variable		2,6
	set_marked_value		3,4
	enqueue_goal		3,macro_table_manager_3_0
	put_values_inc		1,7,3
	execute		6,inkey_to_hash_6_0
macro_table_manager_3_7:
	read_cdr		1,6
	read_elements_inc		4,1,7,3
	collect_list		1
	collect_vector		4
	create_goal		3
	set_value		1,6
	set_variable		2,4
	set_marked_value		3,3
	enqueue_goal		3,macro_table_manager_3_0
	put_value		1,2
	put_value		2,4
	put_values_inc		4,7,3
	execute		6,macro_arg_6_0
macro_table_manager_3_3:
	check_nil		1,macro_table_manager_3_1
	collect_value		3
	collect_value		2
	proceed
macro_table_manager_3_1:
	suspend		macro_table_manager_3_0
	module_entry		kl1cmp_macro_arg
	predicate		inkey_to_hash,6
inkey_to_hash_6_0:
	b_hash		1,1,7
	put_marked_value		8,4
	b_modulo		1,8,1
	put_variable		9,8
	b_set_vector_element		5,1,5,9,1
	get_value		1,6
	put_value		1,7
	put_value		6,8
	execute		6,inkey_to_hash_2_6_0
inkey_to_hash_6_1:
	suspend		inkey_to_hash_6_0
	module_entry		kl1cmp_macro_arg
	predicate		inkey_to_hash_2,6
inkey_to_hash_2_6_0:
	try_me_else		inkey_to_hash_2_6_1
	wait_integer		5,0
	put_marked_value		5,4
	b_new_vector		5,5
	b_hash		2,2,7
	b_modulo		2,4,2
	put_vector		4,3
	write_element_value		4,0,1
	write_element_value		4,1,7
	write_element_value		4,2,3
	put_list		1
	write_car_value		1,4
	write_cdr_nil		1
	b_set_vector_element		5,2,1,1,2
	get_value		2,6
	proceed
inkey_to_hash_2_6_1:
	otherwise		inkey_to_hash_2_6_0
	put_value		8,1
	put_value		9,3
	b_hash		2,1,3
	b_modulo		1,4,1
	put_variable		2,7
	b_set_vector_element		5,1,1,2,2
	get_value		2,6
	put_value		2,8
	put_value		4,9
	put_value		5,7
	execute		5,collision_check_5_0
inkey_to_hash_2_6_6:
	suspend		inkey_to_hash_2_6_0
	module_entry		kl1cmp_macro_arg
	predicate		collision_check,5
collision_check_5_0:
	try_me_else		collision_check_5_1
	wait_integer		1,0
	put_vector		1,3
	write_elements_inc		1,0,2,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		5,2
	proceed
collision_check_5_1:
	otherwise		collision_check_5_0
	execute		5,check_old_definitions_5_0
collision_check_5_6:
	suspend		collision_check_5_0
	module_entry		kl1cmp_macro_arg
	predicate		check_old_definitions,5
check_old_definitions_5_0:
	try_me_else		check_old_definitions_5_1
	wait_list_var_var		1,10,6
	wait_vector		10,3
	read_elements_inc		10,0,7,3
	wait_value		7,2
	wait_value		8,3
	collect_value		9
	collect_value		3
	put_reused_vector		2,10
	write_elements_inc		2,0,7,2
	write_element_value		2,2,4
	put_reused_list_val_val		1,1,2,6
	get_list_value		5,1
	proceed
check_old_definitions_5_1:
	otherwise		check_old_definitions_5_0
	try_me_else		check_old_definitions_5_5
	jump_on_non_list_var_var		1,check_old_definitions_5_7,6,7
	get_reused_list_val_var		5,1,1,6,6
	put_value		1,7
	put_value		5,6
	execute		5,check_old_definitions_5_0
check_old_definitions_5_7:
	check_nil		1,check_old_definitions_5_5
	put_vector		1,3
	write_elements_inc		1,0,2,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		5,2
	proceed
check_old_definitions_5_5:
	suspend		check_old_definitions_5_0
	module_entry		kl1cmp_macro_arg
	predicate		ref_hash_element,5
ref_hash_element_5_0:
	try_me_else		ref_hash_element_5_1
	jump_on_non_integer		1,ref_hash_element_5_3
	test_integer		1,0,ref_hash_element_5_1
	try_me_else		ref_hash_element_5_4
	wait_atom		3,none
	put_func		1,2,#
	write_element_value		1,1,4
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_integer		2,0
	proceed
ref_hash_element_5_4:
	try_me_else		ref_hash_element_5_1
	put_atom		6,none
	g_diff		3,6
	put_func		1,3,#
	write_elements_inc		1,1,3,2
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_integer		2,0
	proceed
ref_hash_element_5_3:
	is_vector		1,ref_hash_element_5_1
	g_vector		1,6
	b_hash		4,4,7
	b_modulo		4,6,4
	put_variable		8,6
	b_set_vector_element		1,4,1,8,4
	get_value		4,2
	put_value		2,6
	put_value		4,7
	execute		5,ref_hash_list_5_0
ref_hash_element_5_1:
	suspend		ref_hash_element_5_0
	module_entry		kl1cmp_macro_arg
	predicate		ref_hash_list,5
ref_hash_list_5_0:
	try_me_else		ref_hash_list_5_1
	list		1
	read_car		1,6
	wait_vector		6,3
	read_elements_inc		6,0,7,2
	jump_on_non_atom		8,ref_hash_list_5_5
	read_cdr		1,9
	read_element		6,2,10
	wait_value		3,7
	wait_value		4,8
	atom		4
	put_marked_value		10,10
	get_value		10,5
	put_reused_vector		5,6
	write_elements_inc		5,0,3,2
	write_element_value		5,2,10
	put_reused_list_val_val		1,1,5,9
	get_list_value		2,1
	proceed
ref_hash_list_5_5:
	is_vector		8,ref_hash_list_5_1
	read_element		6,2,9
	read_cdr		1,10
	vector		4
	wait_value		3,7
	put_integer		11,0
	g_vector_element		8,11,11
	put_integer		12,0
	g_vector_element		4,12,12
	wait_value		11,12
	g_vector		8,11
	g_vector		4,12
	wait_value		12,11
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_marked_value		6,1,8
	write_element_marked_value		6,2,9
	put_reused_list_val_val		1,1,6,10
	get_list_value		2,1
	put_value		1,11
	put_value		2,8
	put_value		3,4
	put_value		4,9
	execute		5,copy_macro_args_5_0
ref_hash_list_5_1:
	otherwise		ref_hash_list_5_0
	try_me_else		ref_hash_list_5_16
	wait		1
	switch_on_type		1,ref_hash_list_5_17,ref_hash_list_5_18,ref_hash_list_5_19,ref_hash_list_5_16,ref_hash_list_5_16,ref_hash_list_5_16
ref_hash_list_5_19:
	read_car		1,6
	read_cdr		1,7
	get_reused_list_val_var		2,1,1,6,6
	put_values_dec		1,7,2
	execute		5,ref_hash_list_5_0
ref_hash_list_5_17:
	test_nil		1,ref_hash_list_5_16
	try_me_else		ref_hash_list_5_20
	wait_atom		3,none
	put_func		1,2,#
	write_element_value		1,1,4
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_nil		2
	proceed
ref_hash_list_5_20:
	try_me_else		ref_hash_list_5_16
	put_atom		6,none
	g_diff		3,6
	put_func		1,3,#
	write_elements_inc		1,1,3,2
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_nil		2
	proceed
ref_hash_list_5_18:
	test_integer		1,0,ref_hash_list_5_16
	try_me_else		ref_hash_list_5_22
	wait_atom		3,none
	put_func		1,2,#
	write_element_value		1,1,4
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_nil		2
	proceed
ref_hash_list_5_22:
	try_me_else		ref_hash_list_5_16
	put_atom		6,none
	g_diff		3,6
	put_func		1,3,#
	write_elements_inc		1,1,3,2
	put_func		3,2,'$NOT_FOUND'
	write_element_value		3,1,1
	get_vector_value		5,3
	get_nil		2
	proceed
ref_hash_list_5_16:
	suspend		ref_hash_list_5_0
	module_entry		kl1cmp_macro_arg
	predicate		copy_macro_args,5
copy_macro_args_5_0:
	try_me_else		copy_macro_args_5_1
	vector		4
	g_vector		4,6
	put_values_inc		7,1,3
	put_marked_value		1,6
	b_new_vector		1,1
	create_goal		7
	set_integer		1,0
	set_value		2,6
	set_variable		3,2
	set_void		4
	set_value		5,4
	set_value		6,1
	set_value		7,5
	enqueue_goal		7,copy_to_new_arg_7_0
	put_value		1,2
	put_nil		2
	put_integer		3,1
	put_values_inc		4,7,3
	execute		6,extract_original_args_6_0
copy_macro_args_5_1:
	suspend		copy_macro_args_5_0
	module_entry		kl1cmp_macro_arg
	predicate		extract_original_args,6
extract_original_args_6_0:
	try_me_else		extract_original_args_6_1
	integer		3
	integer		4
	g_less_than		3,4
	put_marked_value		7,3
	put_nil		8
	b_set_vector_element		5,7,5,8,7
	put_nil		8
	b_set_vector_element		6,3,6,8,8
	put_list_val_var		9,6,6
	put_list_val_val		10,5,9
	get_list_value		1,10
	b_increment		3,1
	put_value		3,1
	put_value		1,6
	put_values_inc		5,7,2
	execute		6,extract_original_args_6_0
extract_original_args_6_1:
	try_me_else		extract_original_args_6_3
	wait_value		3,4
	collect_value		6
	collect_value		5
	collect_value		3
	collect_value		4
	get_value		1,2
	proceed
extract_original_args_6_3:
	suspend		extract_original_args_6_0
	module_entry		kl1cmp_macro_arg
	predicate		copy_to_new_arg,7
copy_to_new_arg_7_0:
	try_me_else		copy_to_new_arg_7_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		8,1
	put_nil		9
	b_set_vector_element		5,8,5,9,8
	b_increment		1,9
	put_variable		11,10
	b_set_vector_element		6,1,1,11,6
	create_goal		7
	set_value		1,9
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_value		5,8
	set_values_inc		6,6,2
	enqueue_goal		7,copy_to_new_arg_7_0
	put_value		1,3
	put_value		3,5
	put_value		4,10
	execute		4,search_new_arg_4_0
copy_to_new_arg_7_1:
	try_me_else		copy_to_new_arg_7_3
	wait_value		1,2
	collect_value		5
	collect_value		1
	collect_value		2
	get_value		6,7
	get_value		3,4
	proceed
copy_to_new_arg_7_3:
	suspend		copy_to_new_arg_7_0
	module_entry		kl1cmp_macro_arg
	predicate		search_new_arg,4
search_new_arg_4_0:
	try_me_else		search_new_arg_4_1
	wait		3
	switch_on_type		3,search_new_arg_4_2,search_new_arg_4_3,search_new_arg_4_4,search_new_arg_4_5,search_new_arg_4_6,search_new_arg_4_7
search_new_arg_4_4:
	read_car		3,5
	read_cdr		3,6
	put_reused_list		3,3
	write_car_variable		3,7
	write_cdr_variable		3,8
	get_list_value		4,3
	create_goal		4
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	set_value		4,8
	enqueue_goal		4,search_new_arg_4_0
	put_value		2,3
	put_value		3,5
	put_value		4,7
	execute		4,search_new_arg_4_0
search_new_arg_4_2:
	get_value		4,3
	get_value		1,2
	proceed
search_new_arg_4_3:
	get_value		4,3
	get_value		1,2
	proceed
search_new_arg_4_5:
	test_arity		3,3,search_new_arg_4_1
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	integer		5
	string		6
	g_string		6,7,8
	wait_integer		8,8
	collect_value		6
	collect_vector		3
	put_value		3,5
	execute		4,search_new_undef_arg_4_0
search_new_arg_4_6:
	get_value		4,3
	get_value		1,2
	proceed
search_new_arg_4_7:
	is_float		3,search_new_arg_4_1
	get_value		4,3
	get_value		1,2
	proceed
search_new_arg_4_1:
	otherwise		search_new_arg_4_0
	try_me_else		search_new_arg_4_11
	vector		3
	put_value		5,3
	g_vector		5,3
	put_values_inc		8,1,2
	put_value		7,4
	put_marked_value		1,3
	b_new_vector		6,1
	put_integer		1,0
	put_value		2,3
	put_values_inc		3,8,2
	execute		7,copy_to_new_arg_7_0
search_new_arg_4_11:
	suspend		search_new_arg_4_0
	module_entry		kl1cmp_macro_arg
	predicate		search_new_undef_arg,4
search_new_undef_arg_4_0:
	try_me_else		search_new_undef_arg_4_1
	wait_list_var_var		1,10,11
	wait_list_var_var		11,5,6
	wait_vector		10,3
	read_element		10,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		10,1,7,2
	integer		7
	integer		3
	g_not_equal		7,3
	put_reused_list_val_var		1,1,5,9
	put_reused_func		5,10,'$VAR'
	write_elements_inc		5,1,7,2
	put_reused_list_val_val		7,11,5,1
	get_list_value		2,7
	put_value		1,6
	put_value		2,9
	execute		4,search_new_undef_arg_4_0
search_new_undef_arg_4_1:
	otherwise		search_new_undef_arg_4_0
	try_me_else		search_new_undef_arg_4_5
	jump_on_non_list_var_var		1,search_new_undef_arg_4_7,5,8
	wait_list_var_var		8,6,7
	collect_value		3
	put_marked_value		6,6
	get_value		6,4
	put_reused_list_val_val		1,1,6,7
	put_reused_list_val_val		3,8,5,1
	get_list_value		2,3
	proceed
search_new_undef_arg_4_7:
	check_nil		1,search_new_undef_arg_4_5
	collect_value		3
	get_nil		4
	get_nil		2
	proceed
search_new_undef_arg_4_5:
	suspend		search_new_undef_arg_4_0
	module_entry		kl1cmp_macro_arg
	predicate		macro_arg,6
macro_arg_6_0:
	put_integer		7,0
	execute		7,macro_arg_7_0
macro_arg_6_1:
	suspend		macro_arg_6_0
	module_entry		kl1cmp_macro_arg
	predicate		macro_arg,7
macro_arg_7_0:
	try_me_else		macro_arg_7_1
	jump_on_non_atom		4,macro_arg_7_3
	hash_on_atom		4,7,macro_arg_7_1
	bucket_entry_a		ascii,macro_arg_7_4
	bucket_entry_a		c,macro_arg_7_5
	bucket_entry_a		code,macro_arg_7_6
	bucket_entry_a		key,macro_arg_7_7
	bucket_entry_a		module,macro_arg_7_8
	bucket_entry_a		none,macro_arg_7_9
	bucket_entry_a		string,macro_arg_7_10
macro_arg_7_4:
	jump_on_non_atom		5,macro_arg_7_12
	collect_value		7
	collect_value		3
	get_value		1,2
	b_atom_name		5,1
	put_integer		2,0
	b_string_element		1,2,2,1
	get_value		2,6
	proceed
macro_arg_7_12:
	is_string		5,macro_arg_7_1
	g_string		5,4,8
	collect_value		7
	collect_value		3
	get_value		1,2
	get_value		6,5
	proceed
macro_arg_7_5:
	string		5
	g_string		5,9,8
	wait_integer		9,1
	collect_value		7
	collect_value		3
	get_value		1,2
	put_integer		1,0
	b_string_element		5,1,2,1
	get_value		2,6
	proceed
macro_arg_7_6:
	wait_vector		5,3
	read_element		5,0,8
	wait_atom		8,:
	read_element		5,1,8
	read_element		5,2,10
	wait_vector		10,3
	read_element		10,0,9
	wait_atom		9,/
	read_element		10,1,4
	read_element		10,2,9
	collect_value		7
	collect_value		3
	collect_vector		10
	get_value		1,2
	put_reused_vector		1,5
	write_element_value		1,0,8
	write_element_value		1,1,4
	write_element_value		1,2,9
	get_vector_value		6,1
	proceed
macro_arg_7_7:
	atom		5
	branch_on_atom		5,2,macro_arg_7_1
	bucket_entry_a		cr,macro_arg_7_14
	bucket_entry_a		lf,macro_arg_7_15
macro_arg_7_14:
	collect_value		7
	collect_value		3
	get_value		1,2
	get_integer		6,13
	proceed
macro_arg_7_15:
	collect_value		7
	collect_value		3
	get_value		1,2
	get_integer		6,10
	proceed
macro_arg_7_8:
	collect_value		7
	collect_value		3
	get_value		1,2
	get_value		6,5
	proceed
macro_arg_7_9:
	string		5
	g_string		5,9,8
	wait_integer		9,1
	collect_value		7
	collect_value		3
	get_value		1,2
	put_integer		1,0
	b_string_element		5,1,2,1
	get_value		2,6
	proceed
macro_arg_7_10:
	string		5
	collect_value		7
	collect_value		3
	get_value		1,2
	get_value		5,6
	proceed
macro_arg_7_3:
	is_integer		4,macro_arg_7_1
	string		5
	g_string		5,8,9
	collect_value		7
	collect_value		3
	get_value		1,2
	put_values_inc		1,4,3
	put_value		4,8
	execute		4,convert_string_to_integer_4_0
macro_arg_7_1:
	otherwise		macro_arg_7_0
	b_hash		4,4,8
	put_marked_value		9,3
	b_modulo		4,9,4
	put_variable		9,10
	put_variable		11,12
	b_set_vector_element		9,4,4,11,9
	create_goal		6
	set_variable		1,11
	set_values_inc		2,2,2
	set_value		4,6
	set_variable		5,2
	set_value		6,7
	enqueue_goal		6,macro_arg_result_6_0
	create_goal		5
	set_value		1,4
	set_value		2,12
	set_value		3,8
	set_value		4,5
	set_value		5,2
	enqueue_goal		5,ref_hash_element_5_0
	put_values_dec		2,11,3
	execute		4,'C_4_0'
macro_arg_7_22:
	suspend		macro_arg_7_0
	module_entry		kl1cmp_macro_arg
	predicate		macro_arg_result,6
macro_arg_result_6_0:
	try_me_else		macro_arg_result_6_1
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,#
	read_elements_inc		5,1,7,2
	integer		6
	put_integer		9,100
	g_less_than		6,9
	collect_vector		5
	put_value		10,4
	b_increment		6,4
	put_value		9,4
	put_values_inc		4,7,2
	put_values_dec		6,10,2
	execute		7,macro_arg_7_0
macro_arg_result_6_1:
	otherwise		macro_arg_result_6_0
	collect_value		6
	collect_value		3
	get_value		1,2
	get_value		4,5
	proceed
macro_arg_result_6_6:
	suspend		macro_arg_result_6_0
	module_entry		kl1cmp_macro_arg
	predicate		'C',4
'C_4_0':
	get_value		1,3
	get_value		2,4
	proceed
'C_4_1':
	suspend		'C_4_0'
	module_entry		kl1cmp_macro_arg
	predicate		convert_string_to_integer,4
convert_string_to_integer_4_0:
	try_me_else		convert_string_to_integer_4_1
	integer		1
	hash_on_integer		1,5,convert_string_to_integer_4_1
	bucket_entry_i		2,convert_string_to_integer_4_3
	bucket_entry_i		4,convert_string_to_integer_4_4
	bucket_entry_i		8,convert_string_to_integer_4_5
	bucket_entry_i		16,convert_string_to_integer_4_6
	bucket_entry_i		32,convert_string_to_integer_4_7
convert_string_to_integer_4_3:
	put_value		1,4
	put_integer		4,2
	put_integer		5,1
	put_integer		6,1
	execute		6,shift_convert_6_0
convert_string_to_integer_4_4:
	put_value		1,4
	put_integer		4,4
	put_integer		5,2
	put_integer		6,3
	execute		6,shift_convert_6_0
convert_string_to_integer_4_5:
	put_value		1,4
	put_integer		4,8
	put_integer		5,3
	put_integer		6,7
	execute		6,shift_convert_6_0
convert_string_to_integer_4_6:
	put_value		1,4
	put_integer		4,16
	put_integer		5,4
	put_integer		6,15
	execute		6,shift_convert_6_0
convert_string_to_integer_4_7:
	put_value		1,4
	put_integer		4,32
	put_integer		5,5
	put_integer		6,31
	execute		6,shift_convert_6_0
convert_string_to_integer_4_1:
	otherwise		convert_string_to_integer_4_0
	put_value		5,2
	put_value		7,1
	put_value		6,3
	put_integer		1,0
	put_values_inc		2,4,2
	put_value		4,7
	put_integer		5,0
	execute		6,convert_string_to_integer_6_0
convert_string_to_integer_4_10:
	suspend		convert_string_to_integer_4_0
	module_entry		kl1cmp_macro_arg
	predicate		shift_convert,6
shift_convert_6_0:
	try_me_else		shift_convert_6_1
	integer		1
	test_integer		1,0,shift_convert_6_3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		2
	get_integer		3,0
	proceed
shift_convert_6_3:
	put_integer		7,0
	g_less_than		7,1
	integer		5
	g_decrement		5,7
	put_integer		8,32
	g_add		8,7,7
	g_divide		7,5,7
	g_not_less_than		7,1
	put_marked_value		7,2
	put_integer		8,0
	b_string_element		7,8,7,8
	create_goal		7
	set_values_inc		1,1,6
	set_variable		7,2
	enqueue_goal		7,check_first_7_0
	put_value		1,7
	execute		2,convert_one_element_to_integer_2_0
shift_convert_6_1:
	otherwise		shift_convert_6_0
	collect_value		6
	collect_value		5
	collect_value		1
	put_func		1,3,#
	write_element_value		1,1,4
	write_element_value		1,2,2
	put_func		2,2,'$NOT_FOUND'
	write_element_value		2,1,1
	get_vector_value		3,2
	proceed
shift_convert_6_7:
	suspend		shift_convert_6_0
	module_entry		kl1cmp_macro_arg
	predicate		check_first,7
check_first_7_0:
	try_me_else		check_first_7_1
	integer		6
	integer		7
	g_not_less_than		6,7
	put_value		6,1
	put_values_inc		8,2,2
	put_integer		1,1
	put_value		2,6
	put_value		3,8
	put_value		6,7
	put_value		7,9
	execute		7,shift_conv_7_0
check_first_7_1:
	otherwise		check_first_7_0
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	put_func		1,3,#
	write_element_value		1,1,4
	write_element_value		1,2,2
	put_func		2,2,'$NOT_FOUND'
	write_element_value		2,1,1
	get_vector_value		3,2
	proceed
check_first_7_5:
	suspend		check_first_7_0
	module_entry		kl1cmp_macro_arg
	predicate		shift_conv,7
shift_conv_7_0:
	try_me_else		shift_conv_7_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		8,1
	b_string_element		3,8,3,8
	create_goal		8
	set_values_inc		1,1,2
	set_value		3,8
	set_values_inc		4,4,4
	set_variable		8,2
	enqueue_goal		8,check_shift_conv_8_0
	put_value		1,3
	execute		2,convert_one_element_to_integer_2_0
shift_conv_7_1:
	try_me_else		shift_conv_7_3
	wait_value		1,2
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		7,6
	proceed
shift_conv_7_3:
	suspend		shift_conv_7_0
	module_entry		kl1cmp_macro_arg
	predicate		check_shift_conv,8
check_shift_conv_8_0:
	try_me_else		check_shift_conv_8_1
	integer		4
	integer		8
	g_less_than		8,4
	put_marked_value		9,5
	b_shift_left		6,9,6
	b_or		6,8,6
	b_increment		1,1
	execute		7,shift_conv_7_0
check_shift_conv_8_1:
	otherwise		check_shift_conv_8_0
	collect_value		8
	collect_value		6
	collect_value		5
	collect_value		2
	collect_value		1
	put_func		1,3,#
	write_elements_dec		1,1,4,2
	put_func		2,2,'$NOT_FOUND'
	write_element_value		2,1,1
	get_vector_value		7,2
	proceed
check_shift_conv_8_5:
	suspend		check_shift_conv_8_0
	module_entry		kl1cmp_macro_arg
	predicate		convert_string_to_integer,6
convert_string_to_integer_6_0:
	try_me_else		convert_string_to_integer_6_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		7,1
	b_string_element		3,7,3,7
	create_goal		7
	set_values_inc		1,1,2
	set_value		3,7
	set_values_inc		4,4,3
	set_variable		7,2
	enqueue_goal		7,check_convert_7_0
	put_value		1,3
	execute		2,convert_one_element_to_integer_2_0
convert_string_to_integer_6_1:
	try_me_else		convert_string_to_integer_6_3
	wait_value		1,2
	collect_value		4
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		6,5
	proceed
convert_string_to_integer_6_3:
	suspend		convert_string_to_integer_6_0
	module_entry		kl1cmp_macro_arg
	predicate		check_convert,7
check_convert_7_0:
	try_me_else		check_convert_7_1
	integer		4
	integer		7
	g_less_than		7,4
	integer		5
	g_multiply		5,4,8
	g_add		8,7,5
	b_increment		1,1
	execute		6,convert_string_to_integer_6_0
check_convert_7_1:
	otherwise		check_convert_7_0
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	put_func		1,3,#
	write_elements_dec		1,1,4,2
	put_func		2,2,'$NOT_FOUND'
	write_element_value		2,1,1
	get_vector_value		6,2
	proceed
check_convert_7_5:
	suspend		check_convert_7_0
	module_entry		kl1cmp_macro_arg
	predicate		convert_one_element_to_integer,2
convert_one_element_to_integer_2_0:
	try_me_else		convert_one_element_to_integer_2_1
	integer		1
	try_me_else		convert_one_element_to_integer_2_3
	put_integer		3,48
	g_not_less_than		1,3
	put_integer		3,57
	g_not_less_than		3,1
	put_integer		3,48
	b_subtract		1,3,1
	get_value		2,1
	proceed
convert_one_element_to_integer_2_3:
	try_me_else		convert_one_element_to_integer_2_4
	put_integer		3,97
	g_not_less_than		1,3
	put_integer		3,122
	g_not_less_than		3,1
	put_integer		3,97
	b_subtract		1,3,1
	put_integer		3,10
	b_add		1,3,1
	get_value		2,1
	proceed
convert_one_element_to_integer_2_4:
	try_me_else		convert_one_element_to_integer_2_1
	put_integer		3,65
	g_not_less_than		1,3
	put_integer		3,90
	g_not_less_than		3,1
	put_integer		3,65
	b_subtract		1,3,1
	put_integer		3,10
	b_add		1,3,1
	get_value		2,1
	proceed
convert_one_element_to_integer_2_1:
	otherwise		convert_one_element_to_integer_2_0
	collect_value		1
	get_atom		2,'$NOT_FOUND'
	proceed
convert_one_element_to_integer_2_9:
	suspend		convert_one_element_to_integer_2_0
	begin_const_section		kl1cmp_macro_arg
'$SCNST_0_0':
	define_desc		11,2
	define_integer		1667329327
	define_integer		3108722
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		error
	define_atom		cannot_open_file
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		19,6
	define_integer		661545283
	define_integer		1886330996
	define_integer		1293971045
	define_integer		1869767521
	define_integer		1818838560
	define_integer		8293
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		19,7
	define_integer		1635151433
	define_integer		543451500
	define_integer		1919115629
	define_integer		1701060719
	define_integer		1918987363
	define_integer		1869182049
	define_integer		8302
'$SCNST_3':
	define_string		'$SCNST_3_0'
