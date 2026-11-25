kl1cmp_mtbl:
	module		kl1cmp_mtbl
	entry		generate_macro_table_process,7,generate_macro_table_process_7_0
	entry		make_table,5,make_table_5_0
	module_entry		kl1cmp_mtbl
	predicate		generate_macro_table_process,7
generate_macro_table_process_7_0:
	put_value		9,7
	put_value		11,6
	create_goal		6
	set_variable		1,7
	set_value		2,2
	set_nil		3
	set_value		4,5
	set_variable		5,6
	set_variable		6,8
	enqueue_goal		6,macro_management_process_6_0
	put_value		2,7
	put_nil		5
	put_nil		7
	put_nil		10
	execute		11,read_declaration_11_0
generate_macro_table_process_7_1:
	suspend		generate_macro_table_process_7_0
	module_entry		kl1cmp_mtbl
	predicate		macro_management_process,6
macro_management_process_6_0:
	try_me_else		macro_management_process_6_1
	jump_on_non_list		4,macro_management_process_6_3
	read_car		4,7
	vector		7
	jump_on_arity		7,4,macro_management_process_6_1
	table_entry		macro_management_process_6_1
	table_entry		macro_management_process_6_1
	table_entry		macro_management_process_6_5
	table_entry		macro_management_process_6_6
macro_management_process_6_5:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,7,macro_management_process_6_1
	bucket_entry_a		get_all_args,macro_management_process_6_8
	bucket_entry_a		get_number_of_args,macro_management_process_6_9
	bucket_entry_a		init_tables,macro_management_process_6_10
	bucket_entry_a		new_var_stream,macro_management_process_6_11
	bucket_entry_a		new_variable,macro_management_process_6_12
	bucket_entry_a		replace_local,macro_management_process_6_13
	bucket_entry_a		terminate,macro_management_process_6_14
macro_management_process_6_8:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_vector		7
	put_vector		11,3
	write_element_variable		11,0,8
	write_element_variable		11,1,7
	write_element_variable		11,2,4
	get_vector_value		3,11
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,8
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		5
	set_value		1,7
	set_variable		2,3
	set_nil		3
	set_value		4,6
	set_value		5,1
	enqueue_goal		5,get_arg_5_0
	put_value		1,4
	put_value		2,10
	put_value		4,5
	put_value		5,8
	execute		5,get_arg_5_0
macro_management_process_6_9:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_vector		7
	create_goal		6
	set_values_inc		1,1,3
	set_value		4,9
	set_variable		5,1
	set_variable		6,2
	enqueue_goal		6,macro_management_process_6_0
	create_goal		5
	set_value		1,2
	set_nil		2
	set_variable		3,4
	set_value		4,10
	set_value		5,6
	enqueue_goal		5,count_implicit_args_5_0
	put_nil		2
	put_integer		3,0
	execute		5,count_implicit_args_5_0
macro_management_process_6_10:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_vector		7
	put_vector		11,3
	write_element_variable		11,0,8
	write_element_variable		11,1,7
	write_element_variable		11,2,4
	get_vector_value		3,11
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,8
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		5
	set_value		1,7
	set_variable		2,3
	set_nil		3
	set_value		4,6
	set_value		5,1
	enqueue_goal		5,init_table_5_0
	put_value		1,4
	put_value		2,10
	put_value		4,5
	put_value		5,8
	execute		5,init_table_5_0
macro_management_process_6_11:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_vector		7
	get_nil		3
	put_values_dec		3,10,2
	execute		6,macro_management_process_6_0
macro_management_process_6_12:
	read_cdr		4,9
	read_element		7,1,10
	put_reused_func		7,7,new_variable
	write_element_value		7,1,10
	get_reused_list_val_var		3,8,4,7,4
	put_value		3,4
	put_value		4,9
	execute		6,macro_management_process_6_0
macro_management_process_6_13:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_value		6
	collect_vector		7
	put_value		4,9
	put_value		6,10
	execute		6,macro_management_process_6_0
macro_management_process_6_14:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_vector		7
	put_vector		11,3
	write_element_variable		11,0,8
	write_element_variable		11,1,7
	write_element_variable		11,2,4
	get_vector_value		3,11
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,8
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		5
	set_value		1,7
	set_variable		2,3
	set_nil		3
	set_value		4,6
	set_value		5,1
	enqueue_goal		5,clear_table_5_0
	put_value		1,4
	put_value		2,10
	put_value		4,5
	put_value		5,8
	execute		5,clear_table_5_0
macro_management_process_6_6:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,5,macro_management_process_6_1
	bucket_entry_a		get_new,macro_management_process_6_16
	bucket_entry_a		get_old,macro_management_process_6_17
	bucket_entry_a		get_old_and_new,macro_management_process_6_18
	bucket_entry_a		get_one_arg,macro_management_process_6_19
	bucket_entry_a		get_type,macro_management_process_6_20
macro_management_process_6_16:
	read_cdr		4,9
	read_elements_inc		7,1,10,2
	collect_list		4
	put_reused_vector		12,7
	write_element_variable		12,0,8
	write_element_variable		12,1,7
	write_element_variable		12,2,4
	get_vector_value		3,12
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,3
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		6
	set_values_dec		1,7,2
	set_value		3,1
	set_marked_value		4,10
	set_variable		5,7
	set_value		6,11
	enqueue_goal		6,get_new_6_0
	put_func		6,2,not_found
	write_element_value		6,1,10
	put_values_inc		1,4,2
	put_value		4,10
	put_values_inc		5,6,2
	execute		6,get_new_6_0
macro_management_process_6_17:
	read_cdr		4,9
	read_elements_inc		7,1,10,2
	collect_list		4
	put_reused_vector		12,7
	write_element_variable		12,0,8
	write_element_variable		12,1,7
	write_element_variable		12,2,4
	get_vector_value		3,12
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,3
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		6
	set_values_dec		1,7,2
	set_value		3,1
	set_marked_value		4,10
	set_variable		5,7
	set_value		6,11
	enqueue_goal		6,get_old_6_0
	put_func		6,2,not_found
	write_element_value		6,1,10
	put_values_inc		1,4,2
	put_value		4,10
	put_values_inc		5,6,2
	execute		6,get_old_6_0
macro_management_process_6_18:
	read_cdr		4,9
	read_elements_inc		7,1,10,2
	put_reused_vector		13,7
	write_element_variable		13,0,12
	write_element_variable		13,1,8
	write_element_variable		13,2,7
	get_vector_value		3,13
	create_goal		6
	set_values_inc		1,1,2
	set_value		3,12
	set_value		4,9
	set_variable		5,3
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		6
	set_value		1,8
	set_value		2,6
	set_value		3,1
	set_marked_value		4,10
	set_variable		5,8
	set_value		6,11
	enqueue_goal		6,get_old_and_new_6_0
	put_func		1,2,not_found
	write_element_value		1,1,10
	put_reused_list		6,4
	write_car_value		6,1
	write_cdr_nil		6
	put_value		1,7
	put_value		2,5
	put_value		4,10
	put_value		5,6
	put_value		6,8
	execute		6,get_old_and_new_6_0
macro_management_process_6_19:
	read_cdr		4,9
	read_elements_inc		7,1,10,2
	collect_list		4
	put_reused_vector		12,7
	write_element_variable		12,0,8
	write_element_variable		12,1,7
	write_element_variable		12,2,4
	get_vector_value		3,12
	create_goal		6
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_variable		5,9
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		8
	set_value		1,7
	set_variable		2,3
	set_nil		3
	set_marked_value		4,10
	set_value		5,6
	set_value		6,1
	set_variable		7,8
	set_void		8
	enqueue_goal		8,find_and_get_arg_8_0
	put_func		7,2,not_found
	write_element_value		7,1,10
	put_value		1,4
	put_value		2,11
	put_value		4,10
	put_value		6,9
	execute		8,find_and_get_arg_8_0
macro_management_process_6_20:
	read_cdr		4,9
	read_elements_inc		7,1,10,2
	collect_list		4
	collect_vector		7
	create_goal		6
	set_values_inc		1,1,3
	set_value		4,9
	set_variable		5,2
	set_variable		6,1
	enqueue_goal		6,macro_management_process_6_0
	create_goal		5
	set_value		1,6
	set_value		2,1
	set_marked_value		3,10
	set_variable		4,6
	set_value		5,11
	enqueue_goal		5,find_arg_5_0
	put_func		4,2,not_found
	write_element_value		4,1,10
	put_value		1,5
	put_value		3,10
	put_value		5,6
	execute		5,find_arg_5_0
macro_management_process_6_3:
	check_nil		4,macro_management_process_6_1
	collect_value		6
	collect_value		5
	get_nil		3
	get_value		1,2
	proceed
macro_management_process_6_1:
	suspend		macro_management_process_6_0
	module_entry		kl1cmp_mtbl
	predicate		find_arg,5
find_arg_5_0:
	try_me_else		find_arg_5_1
	jump_on_non_list		1,find_arg_5_3
	read_car		1,6
	vector		6
	read_cdr		1,7
	try_me_else		find_arg_5_5
	put_integer		8,0
	g_vector_element		6,8,8
	g_diff		8,3
	get_reused_list_val_var		2,1,1,6,6
	put_values_dec		1,7,2
	execute		5,find_arg_5_0
find_arg_5_5:
	try_me_else		find_arg_5_1
	put_integer		8,0
	g_vector_element		6,8,8
	wait_value		3,8
	collect_value		4
	put_integer		3,1
	put_marked_value		4,5
	b_set_vector_element		6,3,4,4,3
	get_value		4,5
	put_reused_list_val_val		1,1,3,7
	get_list_value		2,1
	proceed
find_arg_5_3:
	check_nil		1,find_arg_5_1
	collect_value		3
	get_nil		2
	get_value		4,5
	proceed
find_arg_5_1:
	try_me_else		find_arg_5_6
	vector		4
	put_integer		6,0
	g_vector_element		4,6,6
	put_atom		7,not_found
	g_diff		6,7
	collect_value		3
	get_value		1,2
	get_value		4,5
	proceed
find_arg_5_6:
	suspend		find_arg_5_0
	module_entry		kl1cmp_mtbl
	predicate		get_arg,5
get_arg_5_0:
	try_me_else		get_arg_5_1
	jump_on_non_list		4,get_arg_5_3
	read_car		4,6
	vector		6
	jump_on_arity		6,5,get_arg_5_1
	table_entry		get_arg_5_1
	table_entry		get_arg_5_1
	table_entry		get_arg_5_1
	table_entry		get_arg_5_5
	table_entry		get_arg_5_6
get_arg_5_5:
	read_elements_inc		6,0,7,2
	atom		8
	branch_on_atom		8,2,get_arg_5_1
	bucket_entry_a		shared,get_arg_5_8
	bucket_entry_a		stream,get_arg_5_9
get_arg_5_8:
	read_cdr		4,9
	read_element		6,2,10
	put_reused_vector		6,6
	write_element_value		6,0,7
	write_element_atom		6,1,shared
	write_element_marked_value		6,2,10
	get_reused_list_val_var		5,4,4,6,6
	get_list_val_var		2,5,10,4
	put_value		2,4
	put_value		4,9
	put_value		5,6
	execute		5,get_arg_5_0
get_arg_5_9:
	read_cdr		4,9
	read_element		6,2,13
	wait_vector		13,3
	read_element		13,0,10
	wait_atom		10,-
	read_elements_inc		13,1,10,2
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,12
	get_reused_list_val_var		1,4,4,8,8
	put_list_val_val		1,12,10
	put_reused_func		4,6,-
	write_element_value		4,1,1
	write_element_value		4,2,11
	put_reused_vector		1,13
	write_element_value		1,0,7
	write_element_atom		1,1,stream
	write_element_value		1,2,4
	get_list_val_var		5,4,1,6
	get_list_val_var		2,1,12,4
	put_value		1,8
	put_value		2,4
	put_value		4,9
	put_value		5,6
	execute		5,get_arg_5_0
get_arg_5_6:
	read_elements_inc		6,0,7,2
	atom		8
	branch_on_atom		8,2,get_arg_5_1
	bucket_entry_a		oldnew,get_arg_5_11
	bucket_entry_a		string,get_arg_5_12
get_arg_5_11:
	read_cdr		4,9
	read_element		6,2,13
	read_element		6,3,10
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	collect_value		10
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,10
	get_reused_list_val_var		1,4,4,8,8
	put_reused_func		1,13,-
	write_element_value		1,1,10
	write_element_value		1,2,12
	put_reused_vector		4,6
	write_element_value		4,0,7
	write_element_atom		4,1,oldnew
	write_element_value		4,2,1
	write_element_atom		4,3,accessed
	get_list_val_var		5,1,4,6
	put_list_val_var		1,10,4
	put_list_val_val		5,11,1
	get_list_value		2,5
	put_value		1,8
	put_value		2,4
	put_value		4,9
	put_value		5,6
	execute		5,get_arg_5_0
get_arg_5_12:
	read_cdr		4,9
	read_element		6,2,13
	read_element		6,3,10
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	collect_value		10
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,10
	get_reused_list_val_var		1,4,4,8,8
	put_reused_func		1,13,-
	write_element_value		1,1,10
	write_element_value		1,2,12
	put_reused_vector		4,6
	write_element_value		4,0,7
	write_element_atom		4,1,string
	write_element_value		4,2,1
	write_element_atom		4,3,accessed
	get_list_val_var		5,1,4,6
	put_list_val_var		1,10,4
	put_list_val_val		5,11,1
	get_list_value		2,5
	put_value		1,8
	put_value		2,4
	put_value		4,9
	put_value		5,6
	execute		5,get_arg_5_0
get_arg_5_3:
	check_nil		4,get_arg_5_1
	get_nil		1
	get_value		2,3
	get_nil		5
	proceed
get_arg_5_1:
	suspend		get_arg_5_0
	module_entry		kl1cmp_mtbl
	predicate		find_and_get_arg,8
find_and_get_arg_8_0:
	try_me_else		find_and_get_arg_8_1
	jump_on_non_list		5,find_and_get_arg_8_3
	read_car		5,9
	vector		9
	read_cdr		5,10
	try_me_else		find_and_get_arg_8_5
	wait_vector		7,2
	read_element		7,0,11
	wait_atom		11,not_found
	read_element		7,1,11
	put_integer		12,0
	g_vector_element		9,12,12
	wait_value		4,12
	put_integer		12,1
	put_reused_func		4,7,not_found
	write_element_marked_value		4,1,11
	b_set_vector_element		9,12,7,4,4
	put_func		9,2,not_found
	write_element_value		9,1,11
	get_vector_value		7,9
	put_integer		7,2
	put_variable		12,9
	b_set_vector_element		4,7,7,12,4
	get_atom		8,found
	put_reused_list_val_val		5,5,4,10
	get_list_value		6,5
	put_func		4,2,not_found
	write_element_value		4,1,11
	put_value		5,7
	put_value		6,9
	execute		6,insert_arg_6_0
find_and_get_arg_8_5:
	try_me_else		find_and_get_arg_8_1
	put_integer		11,0
	g_vector_element		9,11,11
	g_diff		11,4
	get_reused_list_val_var		6,5,5,9,9
	put_values_dec		5,10,2
	execute		8,find_and_get_arg_8_0
find_and_get_arg_8_3:
	check_nil		5,find_and_get_arg_8_1
	collect_value		4
	get_nil		1
	get_value		2,3
	get_nil		6
	get_value		7,8
	proceed
find_and_get_arg_8_1:
	try_me_else		find_and_get_arg_8_7
	vector		7
	put_integer		9,0
	g_vector_element		7,9,9
	put_atom		10,not_found
	g_diff		9,10
	collect_value		4
	get_nil		1
	get_value		2,3
	get_value		5,6
	get_value		7,8
	proceed
find_and_get_arg_8_7:
	suspend		find_and_get_arg_8_0
	module_entry		kl1cmp_mtbl
	predicate		insert_arg,6
insert_arg_6_0:
	try_me_else		insert_arg_6_1
	atom		4
	hash_on_atom		4,4,insert_arg_6_1
	bucket_entry_a		oldnew,insert_arg_6_3
	bucket_entry_a		shared,insert_arg_6_4
	bucket_entry_a		stream,insert_arg_6_5
	bucket_entry_a		string,insert_arg_6_6
insert_arg_6_3:
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,-
	read_element		5,1,4
	read_element		5,2,7
	put_nil		9
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,10
	put_list_val_val		11,8,9
	get_list_value		1,11
	put_list_val_val		1,10,3
	put_list_val_val		3,4,1
	get_list_value		2,3
	put_reused_func		1,5,-
	write_element_value		1,1,10
	write_element_value		1,2,7
	get_vector_value		6,1
	proceed
insert_arg_6_4:
	get_nil		1
	put_list		1
	write_car_marked_value		1,5
	write_cdr_value		1,3
	get_list_value		2,1
	get_value		6,5
	proceed
insert_arg_6_5:
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,-
	read_element		5,1,4
	read_element		5,2,7
	put_nil		9
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,10
	put_list_val_val		11,8,9
	get_list_value		1,11
	put_list_val_val		1,10,3
	get_list_value		2,1
	put_list_val_val		1,10,4
	put_reused_func		2,5,-
	write_element_value		2,1,1
	write_element_value		2,2,7
	get_vector_value		6,2
	proceed
insert_arg_6_6:
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,-
	read_element		5,1,4
	read_element		5,2,7
	put_nil		9
	put_func		8,2,new_variable
	write_element_marked_variable		8,1,10
	put_list_val_val		11,8,9
	get_list_value		1,11
	put_list_val_val		1,10,3
	put_list_val_val		3,4,1
	get_list_value		2,3
	put_reused_func		1,5,-
	write_element_value		1,1,10
	write_element_value		1,2,7
	get_vector_value		6,1
	proceed
insert_arg_6_1:
	suspend		insert_arg_6_0
	module_entry		kl1cmp_mtbl
	predicate		get_old,6
get_old_6_0:
	try_me_else		get_old_6_1
	list		2
	read_car		2,7
	vector		7
	jump_on_arity		7,5,get_old_6_4
	table_entry		get_old_6_4
	table_entry		get_old_6_4
	table_entry		get_old_6_4
	table_entry		get_old_6_5
	table_entry		get_old_6_6
get_old_6_5:
	read_elements_inc		7,0,8,2
	try_me_else		get_old_6_4
	atom		9
	branch_on_atom		9,2,get_old_6_4
	bucket_entry_a		shared,get_old_6_8
	bucket_entry_a		stream,get_old_6_9
get_old_6_8:
	read_cdr		2,10
	read_element		7,2,11
	wait_value		4,8
	collect_value		5
	collect_value		8
	get_nil		1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_atom		1,1,shared
	write_element_marked_value		1,2,11
	put_reused_list_val_val		2,2,1,10
	get_list_value		3,2
	get_value		6,11
	proceed
get_old_6_9:
	read_cdr		2,10
	read_element		7,2,13
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	wait_value		4,8
	collect_value		5
	collect_value		8
	put_nil		8
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,9
	put_reused_list_val_val		2,2,5,8
	get_list_value		1,2
	put_list_val_val		1,9,11
	put_reused_func		2,7,-
	write_element_value		2,1,1
	write_element_value		2,2,12
	put_reused_vector		1,13
	write_element_value		1,0,4
	write_element_atom		1,1,stream
	write_element_value		1,2,2
	put_list_val_val		2,1,10
	get_list_value		3,2
	get_value		6,9
	proceed
get_old_6_6:
	read_elements_inc		7,0,8,2
	try_me_else		get_old_6_4
	atom		9
	branch_on_atom		9,2,get_old_6_4
	bucket_entry_a		oldnew,get_old_6_11
	bucket_entry_a		string,get_old_6_12
get_old_6_11:
	read_cdr		2,10
	read_element		7,2,14
	read_element		7,3,11
	wait_vector		14,3
	read_element		14,0,12
	wait_atom		12,-
	read_elements_inc		14,1,12,2
	wait_value		4,8
	collect_value		5
	collect_value		8
	get_nil		1
	put_reused_func		1,14,-
	write_element_marked_value		1,1,12
	write_element_value		1,2,13
	put_reused_vector		5,7
	write_element_value		5,0,4
	write_element_atom		5,1,oldnew
	write_element_value		5,2,1
	write_element_value		5,3,11
	put_reused_list_val_val		1,2,5,10
	get_list_value		3,1
	get_value		6,12
	proceed
get_old_6_12:
	read_cdr		2,10
	read_element		7,2,14
	read_element		7,3,11
	wait_vector		14,3
	read_element		14,0,12
	wait_atom		12,-
	read_elements_inc		14,1,12,2
	wait_value		4,8
	collect_value		5
	collect_value		8
	get_nil		1
	put_reused_func		1,14,-
	write_element_marked_value		1,1,12
	write_element_value		1,2,13
	put_reused_vector		5,7
	write_element_value		5,0,4
	write_element_atom		5,1,string
	write_element_value		5,2,1
	write_element_value		5,3,11
	put_reused_list_val_val		1,2,5,10
	get_list_value		3,1
	get_value		6,12
	proceed
get_old_6_4:
	read_cdr		2,8
	try_me_else		get_old_6_1
	wait_vector		5,2
	read_element		5,0,9
	wait_atom		9,not_found
	read_element		5,1,9
	put_integer		10,0
	g_vector_element		7,10,10
	g_diff		10,4
	get_reused_list_val_var		3,2,2,7,7
	put_reused_func		5,5,not_found
	write_element_value		5,1,9
	put_values_dec		2,8,2
	execute		6,get_old_6_0
get_old_6_1:
	otherwise		get_old_6_0
	try_me_else		get_old_6_24
	jump_on_non_list_var_var		2,get_old_6_26,7,8
	wait_vector		5,2
	read_element		5,0,9
	wait_atom		9,not_found
	read_element		5,1,9
	wait_value		9,4
	collect_value		9
	get_reused_list_val_var		3,2,2,7,7
	put_reused_func		5,5,not_found
	write_element_marked_value		5,1,4
	put_values_dec		2,8,2
	execute		6,get_old_6_0
get_old_6_26:
	check_nil		2,get_old_6_24
	collect_value		4
	get_nil		1
	get_nil		3
	get_value		5,6
	proceed
get_old_6_24:
	try_me_else		get_old_6_27
	vector		5
	put_integer		7,0
	g_vector_element		5,7,7
	put_atom		8,not_found
	g_diff		7,8
	collect_value		4
	get_nil		1
	get_value		2,3
	get_value		5,6
	proceed
get_old_6_27:
	suspend		get_old_6_0
	module_entry		kl1cmp_mtbl
	predicate		get_new,6
get_new_6_0:
	try_me_else		get_new_6_1
	list		2
	read_car		2,7
	vector		7
	jump_on_arity		7,5,get_new_6_1
	table_entry		get_new_6_1
	table_entry		get_new_6_1
	table_entry		get_new_6_1
	table_entry		get_new_6_4
	table_entry		get_new_6_5
get_new_6_4:
	read_elements_inc		7,0,8,2
	atom		9
	branch_on_atom		9,2,get_new_6_1
	bucket_entry_a		shared,get_new_6_7
	bucket_entry_a		stream,get_new_6_8
get_new_6_7:
	read_cdr		2,10
	read_element		7,2,11
	wait_value		4,8
	collect_value		5
	collect_value		11
	collect_value		8
	put_nil		8
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,9
	put_reused_list_val_val		2,2,5,8
	get_list_value		1,2
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_atom		1,1,shared
	write_element_value		1,2,9
	put_list_val_val		2,1,10
	get_list_value		3,2
	get_value		6,9
	proceed
get_new_6_8:
	read_cdr		2,10
	read_element		7,2,13
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	wait_value		4,8
	collect_value		5
	collect_value		8
	put_nil		8
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,9
	put_reused_list_val_val		2,2,5,8
	get_list_value		1,2
	put_list_val_val		1,9,11
	put_reused_func		2,7,-
	write_element_value		2,1,1
	write_element_value		2,2,12
	put_reused_vector		1,13
	write_element_value		1,0,4
	write_element_atom		1,1,stream
	write_element_value		1,2,2
	put_list_val_val		2,1,10
	get_list_value		3,2
	get_value		6,9
	proceed
get_new_6_5:
	read_elements_inc		7,0,8,2
	atom		9
	branch_on_atom		9,2,get_new_6_1
	bucket_entry_a		oldnew,get_new_6_10
	bucket_entry_a		string,get_new_6_11
get_new_6_10:
	read_cdr		2,10
	read_element		7,2,14
	read_element		7,3,11
	wait_vector		14,3
	read_element		14,0,12
	wait_atom		12,-
	read_elements_inc		14,1,12,2
	wait_value		4,8
	collect_value		5
	collect_value		12
	collect_value		8
	put_nil		8
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,9
	put_reused_list_val_val		2,2,5,8
	get_list_value		1,2
	put_reused_func		1,14,-
	write_element_value		1,1,9
	write_element_value		1,2,13
	put_reused_vector		2,7
	write_element_value		2,0,4
	write_element_atom		2,1,oldnew
	write_element_value		2,2,1
	write_element_value		2,3,11
	put_list_val_val		1,2,10
	get_list_value		3,1
	get_value		6,9
	proceed
get_new_6_11:
	read_cdr		2,10
	read_element		7,2,14
	read_element		7,3,11
	wait_vector		14,3
	read_element		14,0,12
	wait_atom		12,-
	read_elements_inc		14,1,12,2
	wait_value		4,8
	collect_value		5
	collect_value		12
	collect_value		8
	put_nil		8
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,9
	put_reused_list_val_val		2,2,5,8
	get_list_value		1,2
	put_reused_func		1,14,-
	write_element_value		1,1,9
	write_element_value		1,2,13
	put_reused_vector		2,7
	write_element_value		2,0,4
	write_element_atom		2,1,string
	write_element_value		2,2,1
	write_element_value		2,3,11
	put_list_val_val		1,2,10
	get_list_value		3,1
	get_value		6,9
	proceed
get_new_6_1:
	otherwise		get_new_6_0
	try_me_else		get_new_6_19
	jump_on_non_list_var_var		2,get_new_6_21,7,8
	get_reused_list_val_var		3,2,2,7,7
	put_values_dec		2,8,2
	execute		6,get_new_6_0
get_new_6_21:
	check_nil		2,get_new_6_19
	collect_value		4
	get_nil		1
	get_value		5,6
	get_nil		3
	proceed
get_new_6_19:
	suspend		get_new_6_0
	module_entry		kl1cmp_mtbl
	predicate		clear_table,5
clear_table_5_0:
	try_me_else		clear_table_5_1
	jump_on_non_list		4,clear_table_5_3
	read_car		4,6
	vector		6
	jump_on_arity		6,5,clear_table_5_1
	table_entry		clear_table_5_1
	table_entry		clear_table_5_1
	table_entry		clear_table_5_1
	table_entry		clear_table_5_5
	table_entry		clear_table_5_6
clear_table_5_5:
	read_elements_inc		6,0,7,2
	atom		8
	branch_on_atom		8,2,clear_table_5_1
	bucket_entry_a		shared,clear_table_5_8
	bucket_entry_a		stream,clear_table_5_9
clear_table_5_8:
	read_cdr		4,9
	read_element		6,2,10
	collect_value		10
	collect_vector		6
	put_vector		6,2
	write_element_value		6,0,7
	write_element_atom		6,1,shared
	get_reused_list_val_var		5,4,4,6,6
	put_value		4,9
	put_value		5,6
	execute		5,clear_table_5_0
clear_table_5_9:
	read_cdr		4,9
	read_element		6,2,12
	wait_vector		12,3
	read_element		12,0,10
	wait_atom		10,-
	read_elements_inc		12,1,10,2
	collect_vector		12
	put_func		8,2,new_variable
	write_element_marked_value		8,1,11
	get_reused_list_val_var		1,4,4,8,8
	put_reused_func		1,6,=
	write_element_value		1,1,11
	write_element_variable		1,2,4
	get_list_val_var		2,11,1,6
	put_vector		1,2
	write_element_value		1,0,7
	write_element_atom		1,1,stream
	get_list_val_var		5,2,1,1
	create_goal		5
	set_value		1,8
	set_value		2,6
	set_value		3,3
	set_value		4,9
	set_value		5,1
	enqueue_goal		5,clear_table_5_0
	put_value		1,10
	put_value		2,4
	execute		2,convert_list_to_vector_2_0
clear_table_5_6:
	read_elements_inc		6,0,7,2
	atom		8
	branch_on_atom		8,2,clear_table_5_1
	bucket_entry_a		oldnew,clear_table_5_11
	bucket_entry_a		string,clear_table_5_12
clear_table_5_11:
	read_cdr		4,9
	read_element		6,2,13
	read_element		6,3,10
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	collect_vector		6
	collect_vector		13
	put_vector		13,2
	write_element_variable		13,0,8
	write_element_variable		13,1,6
	get_vector_value		1,13
	put_vector		1,2
	write_element_value		1,0,7
	write_element_atom		1,1,oldnew
	get_reused_list_val_var		5,4,4,1,1
	create_goal		5
	set_value		1,8
	set_variable		2,4
	set_value		3,3
	set_value		4,9
	set_value		5,1
	enqueue_goal		5,clear_table_5_0
	put_value		1,6
	put_value		3,4
	put_values_inc		4,10,3
	execute		6,check_accessed_flg_6_0
clear_table_5_12:
	read_cdr		4,9
	read_element		6,2,13
	read_element		6,3,10
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,-
	read_elements_inc		13,1,11,2
	collect_vector		6
	collect_vector		13
	put_vector		13,2
	write_element_variable		13,0,8
	write_element_variable		13,1,6
	get_vector_value		1,13
	put_vector		1,2
	write_element_value		1,0,7
	write_element_atom		1,1,string
	get_reused_list_val_var		5,4,4,1,1
	create_goal		5
	set_value		1,8
	set_variable		2,4
	set_value		3,3
	set_value		4,9
	set_value		5,1
	enqueue_goal		5,clear_table_5_0
	put_value		1,6
	put_value		3,4
	put_values_inc		4,10,3
	execute		6,check_accessed_flg_6_0
clear_table_5_3:
	check_nil		4,clear_table_5_1
	get_nil		1
	get_value		2,3
	get_nil		5
	proceed
clear_table_5_1:
	suspend		clear_table_5_0
	module_entry		kl1cmp_mtbl
	predicate		check_accessed_flg,6
check_accessed_flg_6_0:
	try_me_else		check_accessed_flg_6_1
	atom		4
	branch_on_atom		4,2,check_accessed_flg_6_1
	bucket_entry_a		accessed,check_accessed_flg_6_3
	bucket_entry_a		not_accessed,check_accessed_flg_6_4
check_accessed_flg_6_3:
	get_nil		1
	get_value		2,3
	get_value		5,6
	proceed
check_accessed_flg_6_4:
	put_nil		7
	put_func		4,2,new_variable
	write_element_marked_value		4,1,6
	put_list_val_val		8,4,7
	get_list_value		1,8
	put_func		1,3,=
	write_elements_inc		1,1,5,2
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
check_accessed_flg_6_1:
	suspend		check_accessed_flg_6_0
	module_entry		kl1cmp_mtbl
	predicate		init_table,5
init_table_5_0:
	try_me_else		init_table_5_1
	jump_on_non_list		4,init_table_5_3
	read_car		4,6
	wait_vector		6,2
	read_elements_inc		6,0,7,2
	atom		8
	hash_on_atom		8,4,init_table_5_1
	bucket_entry_a		oldnew,init_table_5_6
	bucket_entry_a		shared,init_table_5_7
	bucket_entry_a		stream,init_table_5_8
	bucket_entry_a		string,init_table_5_9
init_table_5_6:
	read_cdr		4,9
	put_reused_func		6,6,new_variable
	write_element_marked_variable		6,1,8
	get_reused_list_val_var		1,4,4,6,6
	put_func		1,3,-
	write_element_value		1,1,8
	write_element_variable		1,2,10
	put_vector		4,4
	write_element_value		4,0,7
	write_element_atom		4,1,oldnew
	write_element_value		4,2,1
	write_element_atom		4,3,not_accessed
	get_list_val_var		5,1,4,7
	put_list_val_var		1,10,4
	put_list_val_val		5,8,1
	get_list_value		2,5
	put_value		1,6
	put_value		2,4
	put_value		4,9
	put_value		5,7
	execute		5,init_table_5_0
init_table_5_7:
	read_cdr		4,9
	put_reused_func		6,6,new_variable
	write_element_marked_variable		6,1,8
	get_reused_list_val_var		1,10,4,6,4
	put_vector		1,3
	write_element_value		1,0,7
	write_element_atom		1,1,shared
	write_element_value		1,2,8
	get_list_val_var		5,7,1,6
	get_list_val_var		2,1,8,5
	put_values_inc		1,4,2
	put_value		4,9
	put_value		5,6
	execute		5,init_table_5_0
init_table_5_8:
	read_cdr		4,9
	collect_vector		6
	put_func		6,3,-
	write_element_nil		6,1
	write_element_variable		6,2,10
	put_vector		8,3
	write_element_value		8,0,7
	write_element_atom		8,1,stream
	write_element_value		8,2,6
	get_reused_list_val_var		5,4,4,8,6
	get_list_val_var		2,5,10,4
	put_value		2,4
	put_value		4,9
	put_value		5,6
	execute		5,init_table_5_0
init_table_5_9:
	read_cdr		4,9
	put_reused_func		6,6,new_variable
	write_element_marked_variable		6,1,8
	get_reused_list_val_var		1,4,4,6,6
	put_func		1,3,-
	write_element_value		1,1,8
	write_element_variable		1,2,10
	put_vector		4,4
	write_element_value		4,0,7
	write_element_atom		4,1,string
	write_element_value		4,2,1
	write_element_atom		4,3,not_accessed
	get_list_val_var		5,1,4,7
	put_list_val_var		1,10,4
	put_list_val_val		5,8,1
	get_list_value		2,5
	put_value		1,6
	put_value		2,4
	put_value		4,9
	put_value		5,7
	execute		5,init_table_5_0
init_table_5_3:
	check_nil		4,init_table_5_1
	get_nil		1
	get_value		2,3
	get_nil		5
	proceed
init_table_5_1:
	suspend		init_table_5_0
	module_entry		kl1cmp_mtbl
	predicate		count_implicit_args,5
count_implicit_args_5_0:
	try_me_else		count_implicit_args_5_1
	jump_on_non_list		5,count_implicit_args_5_3
	read_car		5,6
	vector		6
	read_cdr		5,7
	try_me_else		count_implicit_args_5_5
	put_integer		8,1
	g_vector_element		6,8,8
	wait_atom		8,oldnew
	get_reused_list_val_var		1,8,5,6,5
	put_integer		1,2
	b_add		3,1,3
	put_value		1,5
	put_value		5,7
	execute		5,count_implicit_args_5_0
count_implicit_args_5_5:
	try_me_else		count_implicit_args_5_6
	put_integer		8,1
	g_vector_element		6,8,8
	wait_atom		8,stream
	get_reused_list_val_var		1,8,5,6,5
	b_increment		3,3
	put_value		1,5
	put_value		5,7
	execute		5,count_implicit_args_5_0
count_implicit_args_5_6:
	try_me_else		count_implicit_args_5_7
	put_integer		8,1
	g_vector_element		6,8,8
	wait_atom		8,string
	get_reused_list_val_var		1,8,5,6,5
	put_integer		1,2
	b_add		3,1,3
	put_value		1,5
	put_value		5,7
	execute		5,count_implicit_args_5_0
count_implicit_args_5_7:
	try_me_else		count_implicit_args_5_1
	put_integer		8,1
	g_vector_element		6,8,8
	wait_atom		8,shared
	get_reused_list_val_var		1,8,5,6,5
	b_increment		3,3
	put_value		1,5
	put_value		5,7
	execute		5,count_implicit_args_5_0
count_implicit_args_5_3:
	check_nil		5,count_implicit_args_5_1
	get_value		3,4
	get_value		1,2
	proceed
count_implicit_args_5_1:
	suspend		count_implicit_args_5_0
	module_entry		kl1cmp_mtbl
	predicate		get_old_and_new,6
get_old_and_new_6_0:
	try_me_else		get_old_and_new_6_1
	list		2
	read_car		2,7
	vector		7
	jump_on_arity		7,5,get_old_and_new_6_1
	table_entry		get_old_and_new_6_1
	table_entry		get_old_and_new_6_1
	table_entry		get_old_and_new_6_1
	table_entry		get_old_and_new_6_4
	table_entry		get_old_and_new_6_5
get_old_and_new_6_4:
	read_cdr		2,8
	read_element		7,0,11
	wait_value		11,4
	read_element		7,1,9
	wait_atom		9,stream
	read_element		7,2,12
	wait_vector		12,3
	read_element		12,0,9
	wait_atom		9,-
	read_elements_inc		12,1,9,2
	collect_value		5
	collect_value		11
	put_nil		11
	put_func		5,2,new_variable
	write_element_marked_value		5,1,10
	put_reused_list_val_val		2,2,5,11
	get_list_value		1,2
	get_list_val_var		6,1,10,2
	put_reused_func		1,7,-
	write_element_value		1,1,9
	write_element_value		1,2,2
	put_reused_vector		2,12
	write_element_value		2,0,4
	write_element_atom		2,1,stream
	write_element_value		2,2,1
	put_list_val_val		1,2,8
	get_list_value		3,1
	proceed
get_old_and_new_6_5:
	read_cdr		2,8
	read_element		7,0,12
	wait_value		12,4
	read_element		7,1,9
	wait_atom		9,oldnew
	read_element		7,2,14
	read_element		7,3,9
	wait_vector		14,3
	read_element		14,0,10
	wait_atom		10,-
	read_elements_inc		14,1,10,2
	collect_value		5
	collect_value		12
	put_nil		12
	put_func		5,2,new_variable
	write_element_marked_variable		5,1,13
	put_reused_list_val_val		2,2,5,12
	get_list_value		1,2
	put_list_val_val		1,10,13
	get_list_value		6,1
	put_reused_func		1,14,-
	write_element_value		1,1,13
	write_element_value		1,2,11
	put_reused_vector		2,7
	write_element_value		2,0,4
	write_element_atom		2,1,oldnew
	write_element_value		2,2,1
	write_element_value		2,3,9
	put_list_val_val		1,2,8
	get_list_value		3,1
	proceed
get_old_and_new_6_1:
	otherwise		get_old_and_new_6_0
	try_me_else		get_old_and_new_6_9
	wait_list_var_var		2,7,8
	wait_list_var_var		5,11,9
	wait_vector		11,2
	read_element		11,0,10
	wait_atom		10,not_found
	read_element		11,1,12
	wait_value		12,4
	vector		7
	put_integer		10,0
	g_vector_element		7,10,10
	g_diff		10,4
	collect_value		9
	collect_value		12
	get_reused_list_val_var		3,2,2,7,7
	put_reused_func		2,11,not_found
	write_element_marked_value		2,1,4
	put_reused_list		5,5
	write_car_value		5,2
	write_cdr_nil		5
	put_values_dec		2,8,2
	execute		6,get_old_and_new_6_0
get_old_and_new_6_9:
	otherwise		get_old_and_new_6_0
	collect_value		4
	get_nil		1
	get_value		5,6
	get_value		2,3
	proceed
get_old_and_new_6_13:
	suspend		get_old_and_new_6_0
	module_entry		kl1cmp_mtbl
	predicate		read_declaration,11
read_declaration_11_0:
	try_me_else		read_declaration_11_1
	wait_nil		5
	wait_list_var_var		11,13,12
	wait_vector		13,2
	read_element		13,0,14
	wait_atom		14,:-
	read_element		13,1,14
	wait_vector		14,2
	read_element		14,0,15
	wait_atom		15,implicit
	read_element		14,1,5
	collect_list		11
	collect_vector		13
	collect_vector		14
	create_goal		11
	set_variable		1,11
	set_values_inc		2,2,3
	set_variable		5,3
	set_values_inc		6,6,5
	set_value		11,12
	enqueue_goal		11,read_declaration_11_0
	create_goal		5
	set_variable		1,2
	set_value		2,11
	set_value		3,3
	set_nil		4
	set_variable		5,3
	enqueue_goal		5,check_table_5_0
	put_nil		4
	execute		5,make_table_5_0
read_declaration_11_1:
	try_me_else		read_declaration_11_3
	jump_on_non_list		11,read_declaration_11_5
	read_car		11,12
	wait_vector		12,2
	read_element		12,0,13
	wait_atom		13,:-
	read_element		12,1,14
	wait_vector		14,2
	read_element		14,0,15
	atom		15
	hash_on_atom		15,4,read_declaration_11_3
	bucket_entry_a		local_implicit,read_declaration_11_10
	bucket_entry_a		module,read_declaration_11_11
	bucket_entry_a		public,read_declaration_11_12
	bucket_entry_a		with_macro,read_declaration_11_13
read_declaration_11_10:
	read_cdr		11,16
	read_element		14,1,13
	collect_list		11
	collect_value		7
	collect_vector		12
	collect_vector		14
	create_goal		11
	set_variable		1,7
	set_values_inc		2,2,5
	set_variable		7,3
	set_values_inc		8,8,3
	set_value		11,16
	enqueue_goal		11,read_declaration_11_0
	create_goal		5
	set_variable		1,2
	set_value		2,7
	set_value		3,3
	set_nil		4
	set_variable		5,3
	enqueue_goal		5,check_table_5_0
	put_nil		4
	put_value		5,13
	execute		5,make_table_5_0
read_declaration_11_11:
	read_cdr		11,16
	read_element		14,1,13
	put_reused_func		12,12,module
	write_element_value		12,1,13
	put_reused_func		13,14,:-
	write_element_value		13,1,12
	get_reused_list_val_var		9,12,11,13,11
	put_value		9,11
	put_value		11,16
	execute		11,read_declaration_11_0
read_declaration_11_12:
	read_cdr		11,16
	read_element		14,1,13
	put_reused_func		12,12,public
	write_element_value		12,1,13
	put_reused_func		13,14,:-
	write_element_value		13,1,12
	get_reused_list_val_var		9,12,11,13,11
	put_value		9,11
	put_value		11,16
	execute		11,read_declaration_11_0
read_declaration_11_13:
	read_cdr		11,16
	read_element		14,1,13
	collect_list		11
	collect_vector		12
	collect_vector		14
	create_goal		11
	set_variable		1,12
	set_value		2,2
	set_variable		3,11
	set_values_inc		4,4,7
	set_value		11,16
	enqueue_goal		11,read_declaration_11_0
	put_value		2,12
	put_value		4,11
	put_value		5,13
	execute_external		kl1cmp_macro_arg,read_macro_file,5
read_declaration_11_5:
	check_nil		11,read_declaration_11_3
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
read_declaration_11_3:
	otherwise		read_declaration_11_0
	try_me_else		read_declaration_11_31
	wait_list_var_var		11,14,12
	wait_vector		14,2
	read_element		14,0,13
	wait_atom		13,:-
	read_element		14,1,15
	wait_vector		15,2
	read_element		15,0,13
	wait_atom		13,implicit
	read_element		15,1,13
	put_reused_func		14,14,implicit
	write_element_value		14,1,13
	put_reused_func		13,15,:-
	write_element_value		13,1,14
	put_reused_list		11,11
	write_car_value		11,13
	write_cdr_nil		11
	put_structured_constant		13,'$SCNST_0'
	put_func		14,3,error_message
	write_element_value		14,1,13
	write_element_value		14,2,11
	get_list_val_var		1,13,14,11
	put_value		1,11
	put_value		11,12
	execute		11,read_declaration_11_0
read_declaration_11_31:
	suspend		read_declaration_11_0
	module_entry		kl1cmp_mtbl
	predicate		make_table,5
make_table_5_0:
	try_me_else		make_table_5_1
	wait_vector		5,3
	read_element		5,0,6
	atom		6
	branch_on_atom		6,2,make_table_5_1
	bucket_entry_a		',',make_table_5_4
	bucket_entry_a		:,make_table_5_5
make_table_5_4:
	read_elements_inc		5,1,7,2
	collect_vector		5
	create_goal		5
	set_variable		1,6
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,8
	enqueue_goal		5,make_table_5_0
	put_value		2,6
	put_value		4,5
	put_value		5,7
	execute		5,make_table_5_0
make_table_5_5:
	read_elements_inc		5,1,7,2
	collect_vector		5
	put_values_dec		5,8,2
	execute		6,check_type_6_0
make_table_5_1:
	otherwise		make_table_5_0
	get_value		3,4
	put_list		3
	write_car_value		3,5
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_1'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
make_table_5_11:
	suspend		make_table_5_0
	module_entry		kl1cmp_mtbl
	predicate		check_type,6
check_type_6_0:
	try_me_else		check_type_6_1
	atom		5
	hash_on_atom		5,4,check_type_6_1
	bucket_entry_a		oldnew,check_type_6_3
	bucket_entry_a		shared,check_type_6_4
	bucket_entry_a		stream,check_type_6_5
	bucket_entry_a		string,check_type_6_6
check_type_6_3:
	get_value		1,2
	put_vector		1,2
	write_element_value		1,0,6
	write_element_atom		1,1,oldnew
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
check_type_6_4:
	get_value		1,2
	put_vector		1,2
	write_element_value		1,0,6
	write_element_atom		1,1,shared
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
check_type_6_5:
	get_value		1,2
	put_vector		1,2
	write_element_value		1,0,6
	write_element_atom		1,1,stream
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
check_type_6_6:
	get_value		1,2
	put_vector		1,2
	write_element_value		1,0,6
	write_element_atom		1,1,string
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
check_type_6_1:
	otherwise		check_type_6_0
	get_value		3,4
	put_func		3,3,:
	write_elements_dec		3,1,6,2
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_structured_constant		3,'$SCNST_2'
	put_func		5,3,error_message
	write_elements_inc		5,1,3,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
check_type_6_9:
	suspend		check_type_6_0
	module_entry		kl1cmp_mtbl
	predicate		check_table,5
check_table_5_0:
	try_me_else		check_table_5_1
	jump_on_non_list_var_var		5,check_table_5_3,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	put_reused_vector		9,9
	write_element_marked_value		9,0,7
	write_element_value		9,1,8
	get_reused_list_val_var		3,5,5,9,8
	create_goal		5
	set_variable		1,5
	set_value		2,2
	set_value		3,8
	set_value		4,4
	set_variable		5,3
	enqueue_goal		5,check_table_5_0
	put_value		2,5
	put_nil		4
	put_value		5,7
	execute		6,check_table_6_0
check_table_5_3:
	check_nil		5,check_table_5_1
	get_value		3,4
	get_value		1,2
	proceed
check_table_5_1:
	suspend		check_table_5_0
	module_entry		kl1cmp_mtbl
	predicate		check_table,6
check_table_6_0:
	try_me_else		check_table_6_1
	wait_list_var_var		6,9,7
	wait_vector		9,2
	read_element		9,0,10
	wait_value		10,5
	read_element		9,1,8
	collect_value		10
	collect_vector		9
	put_func		9,3,:
	write_element_marked_value		9,1,5
	write_element_value		9,2,8
	put_reused_list		6,6
	write_car_value		6,9
	write_cdr_nil		6
	put_structured_constant		8,'$SCNST_3'
	put_func		9,3,error_message
	write_element_value		9,1,8
	write_element_value		9,2,6
	get_list_val_var		1,8,9,6
	put_value		1,6
	put_value		6,7
	execute		6,check_table_6_0
check_table_6_1:
	otherwise		check_table_6_0
	try_me_else		check_table_6_5
	jump_on_non_list_var_var		6,check_table_6_7,10,7
	wait_vector		10,2
	read_elements_inc		10,0,8,2
	put_reused_vector		10,10
	write_elements_inc		10,0,8,2
	get_reused_list_val_var		3,8,6,10,6
	put_value		3,6
	put_value		6,7
	execute		6,check_table_6_0
check_table_6_7:
	check_nil		6,check_table_6_5
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
check_table_6_5:
	suspend		check_table_6_0
	module_entry		kl1cmp_mtbl
	predicate		convert_list_to_vector,2
convert_list_to_vector_2_0:
	try_me_else		convert_list_to_vector_2_1
	jump_on_non_list_var_var		1,convert_list_to_vector_2_3,3,4
	create_goal		4
	set_variable		1,7
	set_variable		2,6
	set_integer		3,0
	set_value		4,2
	enqueue_goal		4,check_length_and_copy_elements_4_0
	put_reused_list_val_val		5,1,3,4
	put_integer		1,0
	put_value		2,7
	put_values_inc		3,5,2
	put_nil		5
	execute		5,len_5_0
convert_list_to_vector_2_3:
	check_nil		1,convert_list_to_vector_2_1
	get_nil		2
	proceed
convert_list_to_vector_2_1:
	suspend		convert_list_to_vector_2_0
	module_entry		kl1cmp_mtbl
	predicate		len,5
len_5_0:
	try_me_else		len_5_1
	jump_on_non_list_var_var		3,len_5_3,6,7
	b_increment		1,1
	get_reused_list_val_var		4,3,3,6,6
	put_values_dec		3,7,2
	execute		5,len_5_0
len_5_3:
	check_nil		3,len_5_1
	get_value		1,2
	get_value		4,5
	proceed
len_5_1:
	suspend		len_5_0
	module_entry		kl1cmp_mtbl
	predicate		check_length_and_copy_elements,4
check_length_and_copy_elements_4_0:
	try_me_else		check_length_and_copy_elements_4_1
	integer		1
	jump_on_integer		1,2,check_length_and_copy_elements_4_1
	table_entry		check_length_and_copy_elements_4_3
	table_entry		check_length_and_copy_elements_4_4
check_length_and_copy_elements_4_3:
	wait_nil		2
	collect_value		3
	get_nil		4
	proceed
check_length_and_copy_elements_4_4:
	wait_list_var_var		2,5,6
	wait_nil		6
	collect_list		2
	collect_value		3
	get_value		4,5
	proceed
check_length_and_copy_elements_4_1:
	otherwise		check_length_and_copy_elements_4_0
	try_me_else		check_length_and_copy_elements_4_7
	wait_integer		3,0
	b_new_vector		3,1
	put_value		1,2
	put_integer		2,0
	execute		4,copy_elements_4_0
check_length_and_copy_elements_4_7:
	suspend		check_length_and_copy_elements_4_0
	module_entry		kl1cmp_mtbl
	predicate		copy_elements,4
copy_elements_4_0:
	try_me_else		copy_elements_4_1
	jump_on_non_list_var_var		1,copy_elements_4_3,5,6
	collect_list		1
	put_marked_value		1,2
	b_set_vector_element		3,1,1,5,3
	b_increment		2,1
	put_value		2,1
	put_value		1,6
	execute		4,copy_elements_4_0
copy_elements_4_3:
	check_nil		1,copy_elements_4_1
	collect_value		2
	get_value		3,4
	proceed
copy_elements_4_1:
	suspend		copy_elements_4_0
	begin_const_section		kl1cmp_mtbl
'$SCNST_0_0':
	define_desc		27,12
	define_integer		1651470919
	define_integer		1763732577
	define_integer		1768714349
	define_integer		544500067
	define_integer		1818453348
	define_integer		1767993953
	define_integer		544108404
	define_integer		1853189990
	define_integer		1919492196
	define_integer		1969710450
	define_integer		2037145970
	define_integer		46
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		27,8
	define_integer		1635151433
	define_integer		543451500
	define_integer		1819307369
	define_integer		1953063785
	define_integer		1667589152
	define_integer		1634885996
	define_integer		1852795252
	define_integer		32
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		19,12
	define_integer		1635151433
	define_integer		543451500
	define_integer		1701869940
	define_integer		1667589152
	define_integer		1634885996
	define_integer		1852795252
	define_integer		543584032
	define_integer		1819307369
	define_integer		1953063785
	define_integer		1735549216
	define_integer		1852140917
	define_integer		8308
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		27,10
	define_integer		1819309380
	define_integer		1952539497
	define_integer		1763730533
	define_integer		1768714349
	define_integer		544500067
	define_integer		1969713761
	define_integer		1953391981
	define_integer		1732845614
	define_integer		1701998446
	define_integer		100
'$SCNST_3':
	define_string		'$SCNST_3_0'
