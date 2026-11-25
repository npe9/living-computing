multiply_keyed_bag:
	module		multiply_keyed_bag
	entry		multiply_keyed_bag,3,multiply_keyed_bag_3_0
	module_entry		multiply_keyed_bag
	predicate		multiply_keyed_bag,3
multiply_keyed_bag_3_0:
	b_merge		5,4
	get_value		5,3
	create_goal		11
	set_value		1,4
	set_variable		2,10
	set_variable		3,9
	set_variable		4,8
	set_variable		5,6
	set_variable		6,7
	set_integer		7,0
	set_marked_variable		8,3
	set_integer		9,0
	set_variable		10,4
	set_variable		11,5
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		6
	set_value		1,1
	set_value		2,3
	set_values_dec		3,10,4
	enqueue_goal		6,init_indexes_6_0
	put_value		1,2
	put_value		2,6
	execute		5,init_datafile_5_0
multiply_keyed_bag_3_1:
	suspend		multiply_keyed_bag_3_0
	module_entry		multiply_keyed_bag
	predicate		init_datafile,5
init_datafile_5_0:
	put_marked_value		6,3
	b_integer_to_float		6,6
	put_marked_value		7,5
	b_float_multiply		6,7,6
	b_float_to_integer		6,6
	b_new_vector		7,3
	get_value		7,2
	create_goal		2
	set_value		1,6
	set_value		2,4
	enqueue_goal		2,get_packing_size_2_0
	put_integer		2,1
	put_float		4,0.5
	execute		5,get_param_5_0
init_datafile_5_1:
	suspend		init_datafile_5_0
	module_entry		multiply_keyed_bag
	predicate		get_param,5
get_param_5_0:
	try_me_else		get_param_5_1
	wait		1
	switch_on_type		1,get_param_5_2,get_param_5_3,get_param_5_4,get_param_5_1,get_param_5_1,get_param_5_1
get_param_5_4:
	read_car		1,6
	wait_vector		6,2
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,get_param_5_1
	bucket_entry_a		packing_ratio,get_param_5_7
	bucket_entry_a		size,get_param_5_8
get_param_5_7:
	read_cdr		1,8
	read_element		6,1,9
	float		9
	put_float		10,0.0
	g_float_less_than		10,9
	put_float		10,1.0
	g_float_not_less_than		10,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,8
	put_value		4,9
	execute		5,get_param_5_0
get_param_5_8:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_less_than		10,9
	collect_list		1
	collect_value		2
	collect_vector		6
	put_values_inc		1,8,2
	execute		5,get_param_5_0
get_param_5_2:
	test_nil		1,get_param_5_1
	get_value		3,2
	get_value		4,5
	proceed
get_param_5_3:
	put_integer		6,0
	g_less_than		6,1
	collect_value		2
	get_value		3,1
	get_value		4,5
	proceed
get_param_5_1:
	otherwise		get_param_5_0
	try_me_else		get_param_5_16
	wait_list_var_var		1,6,7
	collect_list		1
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		7
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_0'
	b_raise		2,1,6
	proceed
get_param_5_16:
	otherwise		get_param_5_0
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_1'
	b_raise		3,2,1
	proceed
get_param_5_20:
	suspend		get_param_5_0
	module_entry		multiply_keyed_bag
	predicate		get_packing_size,2
get_packing_size_2_0:
	try_me_else		get_packing_size_2_1
	integer		1
	test_integer		1,0,get_packing_size_2_3
	get_integer		2,1
	proceed
get_packing_size_2_3:
	put_integer		3,0
	g_less_than		3,1
	get_value		2,1
	proceed
get_packing_size_2_1:
	suspend		get_packing_size_2_0
	module_entry		multiply_keyed_bag
	predicate		init_indexes,6
init_indexes_6_0:
	try_me_else		init_indexes_6_1
	vector		1
	g_vector		1,7
	put_integer		8,0
	g_less_than		8,7
	put_marked_value		6,6
	get_value		6,7
	b_new_vector		7,6
	b_decrement		6,6
	create_goal		8
	set_values_inc		1,1,2
	set_value		3,6
	set_variable		4,1
	set_values_inc		5,3,2
	set_value		7,7
	set_value		8,5
	enqueue_goal		8,init_indexes_8_0
	execute_external		pool,keyed_set,1
init_indexes_6_1:
	otherwise		init_indexes_6_0
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_2'
	b_raise		3,2,1
	proceed
init_indexes_6_5:
	suspend		init_indexes_6_0
	module_entry		multiply_keyed_bag
	predicate		init_indexes,8
init_indexes_8_0:
	try_me_else		init_indexes_8_1
	integer		3
	try_me_else		init_indexes_8_3
	put_integer		9,0
	g_not_less_than		3,9
	put_marked_value		9,3
	put_integer		10,0
	b_set_vector_element		1,9,1,10,9
	put_variable		10,11
	b_set_vector_element		7,3,7,10,10
	b_decrement		3,7
	create_goal		8
	set_value		1,9
	set_marked_value		2,2
	set_value		3,7
	set_variable		4,9
	set_value		5,5
	set_variable		6,7
	set_value		7,10
	set_value		8,8
	enqueue_goal		8,init_indexes_8_0
	put_value		5,9
	put_value		8,11
	execute		8,if_generate_index_8_0
init_indexes_8_3:
	collect_value		2
	collect_value		1
	get_value		4,5
	get_nil		6
	get_value		7,8
	proceed
init_indexes_8_1:
	suspend		init_indexes_8_0
	module_entry		multiply_keyed_bag
	predicate		if_generate_index,8
if_generate_index_8_0:
	try_me_else		if_generate_index_8_1
	jump_on_non_atom		1,if_generate_index_8_3
	collect_value		2
	put_func		2,4,put
	write_element_marked_value		2,1,1
	write_element_value		2,2,3
	write_element_variable		2,3,3
	put_list_val_val		9,2,5
	get_list_value		4,9
	get_integer		8,0
	get_value		6,7
	put_value		2,3
	execute		2,if_succeeded_2_0
if_generate_index_8_3:
	is_vector		1,if_generate_index_8_1
	jump_on_arity		1,4,if_generate_index_8_1
	table_entry		if_generate_index_8_1
	table_entry		if_generate_index_8_1
	table_entry		if_generate_index_8_4
	table_entry		if_generate_index_8_5
if_generate_index_8_4:
	read_elements_inc		1,0,9,2
	atom		9
	collect_vector		1
	put_func		1,4,put
	write_element_marked_value		1,1,9
	write_element_marked_value		1,2,3
	write_element_variable		1,3,11
	put_list_val_val		12,1,5
	get_list_value		4,12
	create_goal		7
	set_value		1,10
	set_value		2,8
	set_nil		3
	set_values_inc		4,2,2
	set_values_inc		6,6,2
	enqueue_goal		7,generate_index_7_0
	put_value		1,9
	put_value		2,11
	execute		2,if_succeeded_2_0
if_generate_index_8_5:
	read_elements_inc		1,0,9,3
	atom		9
	collect_vector		1
	put_func		1,4,put
	write_element_marked_value		1,1,9
	write_element_marked_value		1,2,3
	write_element_variable		1,3,12
	put_list_val_val		13,1,5
	get_list_value		4,13
	create_goal		7
	set_value		1,10
	set_value		2,8
	set_value		3,11
	set_values_inc		4,2,2
	set_values_inc		6,6,2
	enqueue_goal		7,generate_index_7_0
	put_value		1,9
	put_value		2,12
	execute		2,if_succeeded_2_0
if_generate_index_8_1:
	otherwise		if_generate_index_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		3
	collect_value		2
	get_value		4,5
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_3'
	b_raise		3,2,1
	proceed
if_generate_index_8_9:
	suspend		if_generate_index_8_0
	module_entry		multiply_keyed_bag
	predicate		if_succeeded,2
if_succeeded_2_0:
	try_me_else		if_succeeded_2_1
	wait_vector		2,0
	collect_value		1
	proceed
if_succeeded_2_1:
	otherwise		if_succeeded_2_0
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_4'
	b_raise		3,2,1
	proceed
if_succeeded_2_6:
	suspend		if_succeeded_2_0
	module_entry		multiply_keyed_bag
	predicate		generate_index,7
generate_index_7_0:
	try_me_else		generate_index_7_1
	atom		1
	branch_on_atom		1,3,generate_index_7_1
	bucket_entry_a		hashed,generate_index_7_3
	bucket_entry_a		none,generate_index_7_4
	bucket_entry_a		ordered,generate_index_7_5
generate_index_7_3:
	put_value		8,4
	put_list_val_val		1,5,7
	get_list_value		6,1
	put_value		1,3
	put_atom		3,default
	put_atom		4,ascending
	put_value		5,8
	execute		5,hashed_index_5_0
generate_index_7_4:
	collect_value		5
	collect_value		4
	get_value		6,7
	put_value		1,3
	put_atom		3,ascending
	execute		3,no_index_3_0
generate_index_7_5:
	collect_value		4
	put_list_val_val		1,5,7
	get_list_value		6,1
	put_value		1,3
	put_atom		3,ascending
	execute		3,ordered_index_3_0
generate_index_7_1:
	otherwise		generate_index_7_0
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_5'
	b_raise		3,2,1
	proceed
generate_index_7_8:
	suspend		generate_index_7_0
	module_entry		multiply_keyed_bag
	predicate		ordered_index,3
ordered_index_3_0:
	try_me_else		ordered_index_3_1
	jump_on_non_list		1,ordered_index_3_3
	read_car		1,4
	wait_vector		4,2
	read_element		4,0,5
	wait_atom		5,comparator
	read_element		4,1,6
	jump_on_non_atom		6,ordered_index_3_7
	branch_on_atom		6,2,ordered_index_3_1
	bucket_entry_a		ascending,ordered_index_3_8
	bucket_entry_a		descending,ordered_index_3_9
ordered_index_3_8:
	read_cdr		1,7
	collect_list		1
	collect_value		3
	collect_vector		4
	put_value		1,7
	put_atom		3,ascending
	execute		3,ordered_index_3_0
ordered_index_3_9:
	read_cdr		1,7
	collect_list		1
	collect_value		3
	collect_vector		4
	put_value		1,7
	put_atom		3,descending
	execute		3,ordered_index_3_0
ordered_index_3_7:
	check_vector		6,3,ordered_index_3_1
	read_cdr		1,7
	read_elements_inc		6,0,8,3
	atom		8
	atom		9
	integer		10
	collect_list		1
	collect_value		3
	collect_vector		4
	put_reused_vector		3,6
	write_elements_inc		3,0,8,3
	put_value		1,7
	execute		3,ordered_index_3_0
ordered_index_3_3:
	check_nil		1,ordered_index_3_1
	put_func		1,2,ordered
	write_element_variable		1,1,4
	get_vector_value		2,1
	put_values_inc		1,3,2
	execute_external		pool,keyed_sorted_bag,2
ordered_index_3_1:
	otherwise		ordered_index_3_0
	try_me_else		ordered_index_3_24
	wait_list_var_var		1,4,5
	collect_list		1
	collect_value		3
	collect_value		2
	collect_value		5
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_6'
	b_raise		2,1,4
	proceed
ordered_index_3_24:
	otherwise		ordered_index_3_0
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_7'
	b_raise		3,2,1
	proceed
ordered_index_3_28:
	suspend		ordered_index_3_0
	module_entry		multiply_keyed_bag
	predicate		hashed_index,5
hashed_index_5_0:
	try_me_else		hashed_index_5_1
	jump_on_non_list		1,hashed_index_5_3
	read_car		1,6
	wait_vector		6,2
	read_element		6,0,7
	atom		7
	branch_on_atom		7,3,hashed_index_5_1
	bucket_entry_a		comparator,hashed_index_5_6
	bucket_entry_a		hasher,hashed_index_5_7
	bucket_entry_a		index_size,hashed_index_5_8
hashed_index_5_6:
	read_element		6,1,8
	jump_on_non_atom		8,hashed_index_5_10
	branch_on_atom		8,2,hashed_index_5_1
	bucket_entry_a		ascending,hashed_index_5_11
	bucket_entry_a		descending,hashed_index_5_12
hashed_index_5_11:
	read_cdr		1,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,9
	put_atom		4,ascending
	execute		5,hashed_index_5_0
hashed_index_5_12:
	read_cdr		1,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,9
	put_atom		4,descending
	execute		5,hashed_index_5_0
hashed_index_5_10:
	check_vector		8,3,hashed_index_5_1
	read_cdr		1,9
	read_elements_inc		8,0,10,3
	atom		10
	atom		11
	integer		12
	collect_list		1
	collect_value		4
	collect_vector		6
	put_reused_vector		4,8
	write_elements_inc		4,0,10,3
	put_value		1,9
	execute		5,hashed_index_5_0
hashed_index_5_7:
	read_element		6,1,8
	jump_on_non_atom		8,hashed_index_5_14
	test_atom		8,default,hashed_index_5_1
	read_cdr		1,9
	collect_list		1
	collect_value		3
	collect_vector		6
	put_value		1,9
	put_atom		3,default
	execute		5,hashed_index_5_0
hashed_index_5_14:
	check_vector		8,3,hashed_index_5_1
	read_cdr		1,9
	read_elements_inc		8,0,10,3
	atom		10
	atom		11
	integer		12
	collect_list		1
	collect_value		3
	collect_vector		6
	put_reused_vector		3,8
	write_elements_inc		3,0,10,3
	put_value		1,9
	execute		5,hashed_index_5_0
hashed_index_5_8:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	put_integer		10,0
	g_less_than		10,9
	collect_list		1
	collect_value		5
	collect_vector		6
	put_value		1,8
	put_value		5,9
	execute		5,hashed_index_5_0
hashed_index_5_3:
	check_nil		1,hashed_index_5_1
	put_func		1,3,hashed
	write_element_variable		1,1,6
	write_element_value		1,2,4
	get_vector_value		2,1
	put_value		1,3
	put_values_dec		2,6,2
	execute_external		pool,keyed_bag,3
hashed_index_5_1:
	otherwise		hashed_index_5_0
	try_me_else		hashed_index_5_33
	wait_list_var_var		1,6,7
	collect_list		1
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		7
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_8'
	b_raise		2,1,6
	proceed
hashed_index_5_33:
	otherwise		hashed_index_5_0
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_9'
	b_raise		3,2,1
	proceed
hashed_index_5_37:
	suspend		hashed_index_5_0
	module_entry		multiply_keyed_bag
	predicate		no_index,3
no_index_3_0:
	try_me_else		no_index_3_1
	jump_on_non_list		1,no_index_3_3
	read_car		1,4
	wait_vector		4,2
	read_element		4,0,5
	wait_atom		5,comparator
	read_element		4,1,6
	jump_on_non_atom		6,no_index_3_7
	branch_on_atom		6,2,no_index_3_1
	bucket_entry_a		ascending,no_index_3_8
	bucket_entry_a		descending,no_index_3_9
no_index_3_8:
	read_cdr		1,7
	collect_list		1
	collect_value		3
	collect_vector		4
	put_value		1,7
	put_atom		3,ascending
	execute		3,no_index_3_0
no_index_3_9:
	read_cdr		1,7
	collect_list		1
	collect_value		3
	collect_vector		4
	put_value		1,7
	put_atom		3,descending
	execute		3,no_index_3_0
no_index_3_7:
	check_vector		6,3,no_index_3_1
	read_cdr		1,7
	read_elements_inc		6,0,8,3
	atom		8
	atom		9
	integer		10
	collect_list		1
	collect_value		3
	collect_vector		4
	put_reused_vector		3,6
	write_elements_inc		3,0,8,3
	put_value		1,7
	execute		3,no_index_3_0
no_index_3_3:
	check_nil		1,no_index_3_1
	put_func		1,2,none
	write_element_value		1,1,3
	get_vector_value		2,1
	proceed
no_index_3_1:
	otherwise		no_index_3_0
	try_me_else		no_index_3_24
	wait_list_var_var		1,4,5
	collect_list		1
	collect_value		3
	collect_value		2
	collect_value		5
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_10'
	b_raise		2,1,4
	proceed
no_index_3_24:
	otherwise		no_index_3_0
	collect_value		3
	collect_value		2
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_11'
	b_raise		3,2,1
	proceed
no_index_3_28:
	suspend		no_index_3_0
	module_entry		multiply_keyed_bag
	predicate		multiply_keyed_bag,11
multiply_keyed_bag_11_0:
	try_me_else		multiply_keyed_bag_11_1
	jump_on_non_list		1,multiply_keyed_bag_11_3
	read_car		1,12
	jump_on_non_atom		12,multiply_keyed_bag_11_5
	test_atom		12,pack,multiply_keyed_bag_11_1
	read_cdr		1,13
	collect_list		1
	b_subtract		7,9,1
	create_goal		11
	set_value		1,13
	set_value		2,2
	set_marked_value		3,3
	set_variable		4,9
	set_variable		5,7
	set_value		6,6
	set_value		7,1
	set_marked_value		8,8
	set_integer		9,0
	set_values_inc		10,10,2
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,3,2
	put_value		3,9
	put_value		4,5
	put_values_inc		5,7,2
	execute		6,pack_6_0
multiply_keyed_bag_11_5:
	is_vector		12,multiply_keyed_bag_11_1
	jump_on_arity		12,7,multiply_keyed_bag_11_1
	table_entry		multiply_keyed_bag_11_1
	table_entry		multiply_keyed_bag_11_1
	table_entry		multiply_keyed_bag_11_6
	table_entry		multiply_keyed_bag_11_7
	table_entry		multiply_keyed_bag_11_8
	table_entry		multiply_keyed_bag_11_9
	table_entry		multiply_keyed_bag_11_10
multiply_keyed_bag_11_6:
	read_element		12,0,13
	atom		13
	hash_on_atom		13,4,multiply_keyed_bag_11_1
	bucket_entry_a		carbon_copy,multiply_keyed_bag_11_12
	bucket_entry_a		empty,multiply_keyed_bag_11_13
	bucket_entry_a		get_all,multiply_keyed_bag_11_14
	bucket_entry_a		put,multiply_keyed_bag_11_15
multiply_keyed_bag_11_12:
	read_cdr		1,14
	read_element		12,1,15
	collect_list		1
	collect_vector		12
	create_goal		11
	set_value		1,14
	set_values_inc		2,2,3
	set_variable		5,4
	set_values_inc		6,6,2
	set_marked_value		8,8
	set_values_inc		9,9,3
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_integer		1,0
	put_value		2,8
	put_value		3,5
	put_value		5,15
	execute		5,carbon_copy_5_0
multiply_keyed_bag_11_13:
	read_cdr		1,14
	read_element		12,1,15
	collect_list		1
	collect_vector		12
	put_marked_value		1,7
	put_marked_value		12,9
	b_subtract		1,12,1
	create_goal		11
	set_value		1,14
	set_values_inc		2,2,10
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		2,15
	execute		2,empty_2_0
multiply_keyed_bag_11_14:
	read_cdr		1,14
	read_element		12,1,15
	collect_list		1
	collect_value		9
	collect_vector		12
	create_goal		11
	set_value		1,14
	set_value		2,2
	set_marked_value		3,3
	set_variable		4,1
	set_variable		5,9
	set_value		6,6
	set_integer		7,0
	set_value		8,8
	set_integer		9,0
	set_values_inc		10,10,2
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		3
	set_values_inc		1,3,2
	set_value		3,1
	enqueue_goal		3,clear_indexes_3_0
	put_integer		1,0
	put_value		2,7
	put_value		3,5
	put_value		4,9
	put_value		5,15
	execute		5,get_all_5_0
multiply_keyed_bag_11_15:
	read_cdr		1,14
	read_element		12,1,15
	collect_list		1
	collect_vector		12
	put_value		17,9
	put_value		12,10
	put_value		18,11
	put_value		16,6
	create_goal		11
	set_value		1,14
	set_value		2,2
	set_marked_value		3,3
	set_variable		4,14
	set_variable		5,6
	set_marked_value		6,16
	set_variable		7,10
	set_variable		8,9
	set_variable		9,11
	set_variable		10,13
	set_marked_value		11,18
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,3,2
	put_value		3,14
	put_values_inc		4,5,3
	put_value		7,10
	put_value		10,17
	put_value		14,18
	put_atom		17,put
	put_void		18
	execute		18,put_18_0
multiply_keyed_bag_11_7:
	read_element		12,0,13
	atom		13
	hash_on_atom		13,9,multiply_keyed_bag_11_1
	bucket_entry_a		carbon_copy,multiply_keyed_bag_11_17
	bucket_entry_a		carbon_copyp,multiply_keyed_bag_11_18
	bucket_entry_a		empty,multiply_keyed_bag_11_19
	bucket_entry_a		get,multiply_keyed_bag_11_20
	bucket_entry_a		get_all,multiply_keyed_bag_11_21
	bucket_entry_a		get_if_any,multiply_keyed_bag_11_22
	bucket_entry_a		getp_all,multiply_keyed_bag_11_23
	bucket_entry_a		max_if_any,multiply_keyed_bag_11_24
	bucket_entry_a		min_if_any,multiply_keyed_bag_11_25
multiply_keyed_bag_11_17:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		13,2
	put_values_inc		17,4,2
	put_values_dec		19,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_value		3,3
	set_variable		4,6
	set_variable		5,12
	set_marked_value		6,20
	set_marked_value		7,19
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,15,2
	put_value		3,13
	put_value		5,17
	put_value		7,18
	put_value		8,12
	put_values_inc		9,19,2
	execute		10,carbon_copy_10_0
multiply_keyed_bag_11_18:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	create_goal		11
	set_value		1,14
	set_variable		2,1
	set_values_inc		3,3,2
	set_variable		5,4
	set_marked_value		6,6
	set_value		7,7
	set_marked_value		8,8
	set_values_inc		9,9,3
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		6
	set_value		1,15
	set_variable		2,7
	set_value		3,16
	set_values_dec		4,2,2
	set_value		6,6
	enqueue_goal		6,get_part_all_6_0
	put_integer		1,0
	put_value		2,8
	put_value		3,5
	put_value		5,7
	execute		5,carbon_copy_5_0
multiply_keyed_bag_11_19:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		13,2
	put_values_inc		17,4,2
	put_values_dec		19,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_value		3,3
	set_variable		4,6
	set_variable		5,12
	set_marked_value		6,20
	set_marked_value		7,19
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,15,2
	put_value		3,13
	put_value		5,17
	put_value		7,18
	put_value		8,12
	put_values_inc		9,19,2
	execute		10,empty_10_0
multiply_keyed_bag_11_20:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		17,2
	put_values_inc		18,4,2
	put_values_inc		20,7,2
	put_value		12,9
	put_value		22,10
	put_value		23,6
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,23
	set_variable		7,10
	set_marked_value		8,21
	set_variable		9,13
	set_marked_value		10,22
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,17
	put_value		5,18
	put_value		7,19
	put_value		9,20
	put_value		11,21
	put_values_inc		14,22,2
	put_atom		17,get
	execute		17,get_17_0
multiply_keyed_bag_11_21:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		17,2
	put_values_inc		18,4,2
	put_values_inc		20,7,2
	put_value		12,9
	put_value		22,10
	put_value		23,6
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,23
	set_variable		7,10
	set_marked_value		8,21
	set_variable		9,13
	set_marked_value		10,22
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,17
	put_value		5,18
	put_value		7,19
	put_value		9,20
	put_value		11,21
	put_values_inc		14,22,2
	execute		16,get_all_16_0
multiply_keyed_bag_11_22:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		17,2
	put_values_inc		18,4,2
	put_values_inc		20,7,2
	put_value		12,9
	put_value		22,10
	put_value		23,6
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,23
	set_variable		7,10
	set_marked_value		8,21
	set_variable		9,13
	set_marked_value		10,22
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,17
	put_value		5,18
	put_value		7,19
	put_value		9,20
	put_value		11,21
	put_values_inc		14,22,2
	execute		16,get_if_any_16_0
multiply_keyed_bag_11_23:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_value		9
	collect_vector		12
	create_goal		11
	set_value		1,14
	set_variable		2,1
	set_marked_value		3,3
	set_variable		4,12
	set_variable		5,9
	set_marked_value		6,6
	set_integer		7,0
	set_value		8,8
	set_integer		9,0
	set_values_inc		10,10,2
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		3
	set_values_inc		1,3,2
	set_value		3,12
	enqueue_goal		3,clear_indexes_3_0
	create_goal		6
	set_value		1,15
	set_variable		2,8
	set_value		3,16
	set_values_dec		4,2,2
	set_value		6,6
	enqueue_goal		6,get_part_all_6_0
	put_integer		1,0
	put_value		2,7
	put_value		3,5
	put_values_dec		4,9,2
	execute		5,get_all_5_0
multiply_keyed_bag_11_24:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		13,7
	put_value		17,2
	put_value		18,6
	create_goal		11
	set_value		1,14
	set_variable		2,12
	set_value		3,3
	set_variable		4,7
	set_variable		5,6
	set_marked_value		6,18
	set_marked_value		7,13
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,15,2
	put_value		3,4
	put_value		4,7
	put_atom		7,get_max_if_any
	put_value		8,13
	put_value		9,17
	put_value		10,12
	put_value		11,18
	execute		11,max_if_any_11_0
multiply_keyed_bag_11_25:
	read_cdr		1,14
	read_elements_inc		12,1,15,2
	collect_list		1
	collect_vector		12
	put_value		13,7
	put_value		17,2
	put_value		18,6
	create_goal		11
	set_value		1,14
	set_variable		2,12
	set_value		3,3
	set_variable		4,7
	set_variable		5,6
	set_marked_value		6,18
	set_marked_value		7,13
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_values_inc		1,15,2
	put_value		3,4
	put_value		4,7
	put_atom		7,get_min_if_any
	put_value		8,13
	put_value		9,17
	put_value		10,12
	put_value		11,18
	execute		11,max_if_any_11_0
multiply_keyed_bag_11_8:
	read_element		12,0,13
	atom		13
	hash_on_atom		13,6,multiply_keyed_bag_11_1
	bucket_entry_a		carbon_copyp,multiply_keyed_bag_11_27
	bucket_entry_a		get_and_put,multiply_keyed_bag_11_28
	bucket_entry_a		get_if_any_and_put,multiply_keyed_bag_11_29
	bucket_entry_a		getp,multiply_keyed_bag_11_30
	bucket_entry_a		getp_all,multiply_keyed_bag_11_31
	bucket_entry_a		getp_if_any,multiply_keyed_bag_11_32
multiply_keyed_bag_11_27:
	read_cdr		1,14
	read_elements_inc		12,1,15,3
	collect_list		1
	collect_vector		12
	put_value		13,2
	put_values_inc		18,4,2
	put_values_dec		20,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,1
	set_value		3,3
	set_variable		4,6
	set_variable		5,12
	set_marked_value		6,21
	set_marked_value		7,20
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		6
	set_value		1,16
	set_variable		2,2
	set_value		3,17
	set_variable		4,4
	set_value		5,1
	set_value		6,21
	enqueue_goal		6,get_part_all_6_0
	put_value		1,15
	put_value		3,13
	put_value		5,18
	put_value		7,19
	put_value		8,12
	put_values_inc		9,20,2
	execute		10,carbon_copy_10_0
multiply_keyed_bag_11_28:
	read_cdr		1,14
	read_elements_inc		12,1,15,3
	collect_list		1
	collect_vector		12
	put_value		13,2
	put_values_inc		18,4,2
	put_values_dec		20,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,12
	set_marked_value		6,21
	set_marked_value		7,20
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,13
	put_value		5,18
	put_value		7,19
	put_value		8,12
	put_values_inc		9,20,2
	put_values_inc		11,16,2
	put_atom		13,get_and_put
	execute		13,get_and_put_13_0
multiply_keyed_bag_11_29:
	read_cdr		1,14
	read_element		12,1,15
	read_elements_inc		12,2,18,2
	collect_list		1
	collect_vector		12
	put_value		21,2
	put_values_inc		22,4,2
	put_values_inc		24,7,2
	put_value		13,9
	put_value		26,10
	put_value		17,11
	put_value		20,6
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,20
	set_variable		7,10
	set_variable		8,12
	set_variable		9,14
	set_variable		10,16
	set_marked_value		11,17
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,21
	put_value		5,22
	put_value		7,23
	put_value		9,24
	put_value		11,25
	put_value		15,26
	execute		20,get_if_any_and_put_20_0
multiply_keyed_bag_11_30:
	read_cdr		1,14
	read_elements_inc		12,1,15,3
	collect_list		1
	collect_vector		12
	put_value		18,2
	put_values_inc		19,4,2
	put_values_inc		21,7,2
	put_value		12,9
	put_value		23,10
	put_value		24,6
	create_goal		11
	set_value		1,14
	set_variable		2,2
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,24
	set_variable		7,10
	set_marked_value		8,22
	set_variable		9,13
	set_marked_value		10,23
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		7
	set_value		1,16
	set_variable		2,1
	set_variable		3,16
	set_value		4,17
	set_variable		5,4
	set_value		6,2
	set_value		7,24
	enqueue_goal		7,get_part_7_0
	put_func		17,2,getp
	write_element_value		17,1,1
	put_value		1,15
	put_value		2,3
	put_value		3,18
	put_value		5,19
	put_value		7,20
	put_value		9,21
	put_value		11,22
	put_values_inc		14,23,2
	execute		17,get_17_0
multiply_keyed_bag_11_31:
	read_cdr		1,14
	read_elements_inc		12,1,15,3
	collect_list		1
	collect_vector		12
	put_value		18,2
	put_values_inc		19,4,2
	put_values_inc		21,7,2
	put_value		12,9
	put_value		23,10
	put_value		24,6
	create_goal		11
	set_value		1,14
	set_variable		2,1
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,24
	set_variable		7,10
	set_marked_value		8,22
	set_variable		9,13
	set_marked_value		10,23
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		6
	set_value		1,16
	set_variable		2,16
	set_value		3,17
	set_variable		4,4
	set_value		5,1
	set_value		6,24
	enqueue_goal		6,get_part_all_6_0
	put_value		1,15
	put_value		2,3
	put_value		3,18
	put_value		5,19
	put_value		7,20
	put_value		9,21
	put_value		11,22
	put_values_inc		14,23,2
	execute		16,get_all_16_0
multiply_keyed_bag_11_32:
	read_cdr		1,14
	read_elements_inc		12,1,15,3
	collect_list		1
	collect_vector		12
	put_value		18,2
	put_values_inc		19,4,2
	put_values_inc		21,7,2
	put_value		12,9
	put_value		23,10
	put_value		24,6
	create_goal		11
	set_value		1,14
	set_variable		2,1
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,8
	set_marked_value		6,24
	set_variable		7,10
	set_marked_value		8,22
	set_variable		9,13
	set_marked_value		10,23
	set_value		11,11
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		6
	set_value		1,16
	set_variable		2,16
	set_value		3,17
	set_variable		4,4
	set_value		5,1
	set_value		6,24
	enqueue_goal		6,get_part_if_any_6_0
	put_value		1,15
	put_value		2,3
	put_value		3,18
	put_value		5,19
	put_value		7,20
	put_value		9,21
	put_value		11,22
	put_values_inc		14,23,2
	execute		16,get_if_any_16_0
multiply_keyed_bag_11_9:
	read_element		12,0,13
	atom		13
	branch_on_atom		13,2,multiply_keyed_bag_11_1
	bucket_entry_a		get_and_put_if_any,multiply_keyed_bag_11_34
	bucket_entry_a		getp_and_put,multiply_keyed_bag_11_35
multiply_keyed_bag_11_34:
	read_cdr		1,14
	read_elements_inc		12,1,15,4
	collect_list		1
	collect_vector		12
	put_value		13,2
	put_values_inc		19,4,2
	put_values_dec		21,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,4
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,12
	set_marked_value		6,22
	set_marked_value		7,21
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	put_value		1,15
	put_value		2,3
	put_value		3,13
	put_value		5,19
	put_value		7,20
	put_value		8,12
	put_values_inc		9,21,2
	put_values_inc		11,16,3
	put_atom		14,get_and_put_if_any
	execute		14,get_and_put_if_any_14_0
multiply_keyed_bag_11_35:
	read_cdr		1,14
	read_elements_inc		12,1,15,4
	collect_list		1
	collect_vector		12
	put_value		19,2
	put_values_inc		20,4,2
	put_values_dec		22,7,2
	create_goal		11
	set_value		1,14
	set_variable		2,2
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,14
	set_marked_value		6,23
	set_marked_value		7,22
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		9
	set_value		1,16
	set_variable		2,1
	set_variable		3,11
	set_variable		4,12
	set_values_inc		5,17,2
	set_variable		7,4
	set_value		8,2
	set_value		9,23
	enqueue_goal		9,get_part_and_put_9_0
	put_func		13,2,getp_and_put
	write_element_value		13,1,1
	put_value		1,15
	put_value		2,3
	put_value		3,19
	put_value		5,20
	put_value		7,21
	put_value		8,14
	put_values_inc		9,22,2
	execute		13,get_and_put_13_0
multiply_keyed_bag_11_10:
	read_cdr		1,13
	read_element		12,0,14
	wait_atom		14,getp_and_put_if_any
	read_elements_inc		12,1,14,5
	collect_list		1
	collect_vector		12
	put_value		19,2
	put_values_inc		20,4,2
	put_values_dec		22,7,2
	create_goal		11
	set_value		1,13
	set_variable		2,1
	set_marked_value		3,3
	set_variable		4,6
	set_variable		5,13
	set_marked_value		6,23
	set_marked_value		7,22
	set_values_inc		8,8,4
	enqueue_goal		11,multiply_keyed_bag_11_0
	create_goal		9
	set_value		1,15
	set_variable		2,11
	set_variable		3,12
	set_values_inc		4,16,3
	set_variable		7,4
	set_value		8,1
	set_value		9,23
	enqueue_goal		9,get_part_and_put_if_any_9_0
	put_value		1,14
	put_value		2,3
	put_value		3,19
	put_value		5,20
	put_value		7,21
	put_value		8,13
	put_values_inc		9,22,2
	put_void		13
	put_atom		14,getp_and_put_if_any
	execute		14,get_and_put_if_any_14_0
multiply_keyed_bag_11_3:
	check_nil		1,multiply_keyed_bag_11_1
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_nil		2
	put_values_inc		1,3,2
	execute		2,terminate_indexes_2_0
multiply_keyed_bag_11_1:
	otherwise		multiply_keyed_bag_11_0
	try_me_else		multiply_keyed_bag_11_52
	wait_list_var_var		1,12,13
	collect_list		1
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		13
	get_nil		2
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_12'
	b_raise		2,1,12
	put_values_inc		1,3,2
	execute		2,terminate_indexes_2_0
multiply_keyed_bag_11_52:
	suspend		multiply_keyed_bag_11_0
	module_entry		multiply_keyed_bag
	predicate		terminate_indexes,2
terminate_indexes_2_0:
	try_me_else		terminate_indexes_2_1
	jump_on_non_list_var_var		1,terminate_indexes_2_3,3,4
	collect_list		1
	put_variable		1,5
	b_set_vector_element		2,3,1,1,2
	create_goal		2
	set_value		1,4
	set_value		2,2
	enqueue_goal		2,terminate_indexes_2_0
	put_value		2,5
	put_nil		3
	put_void		4
	execute		4,get_index_stream_4_0
terminate_indexes_2_3:
	check_nil		1,terminate_indexes_2_1
	collect_value		2
	proceed
terminate_indexes_2_1:
	suspend		terminate_indexes_2_0
	module_entry		multiply_keyed_bag
	predicate		empty,2
empty_2_0:
	try_me_else		empty_2_1
	integer		1
	test_integer		1,0,empty_2_3
	get_atom		2,yes
	proceed
empty_2_3:
	put_integer		3,0
	g_less_than		3,1
	get_atom		2,no
	proceed
empty_2_1:
	suspend		empty_2_0
	module_entry		multiply_keyed_bag
	predicate		empty,10
empty_10_0:
	put_value		11,10
	create_goal		4
	set_variable		1,10
	set_variable		2,12
	set_value		3,8
	set_value		4,2
	enqueue_goal		4,if_empty_4_0
	put_void		2
	put_value		8,12
	execute		11,get_data_ids_11_0
empty_10_1:
	suspend		empty_10_0
	module_entry		multiply_keyed_bag
	predicate		if_empty,4
if_empty_4_0:
	try_me_else		if_empty_4_1
	jump_on_non_list		1,if_empty_4_3
	read_car		1,5
	integer		5
	read_cdr		1,6
	vector		2
	try_me_else		if_empty_4_6
	g_vector_element		2,5,7
	vector		7
	g_vector		7,5
	collect_list		1
	collect_value		6
	get_value		2,3
	get_atom		4,no
	proceed
if_empty_4_6:
	try_me_else		if_empty_4_1
	g_vector_element		2,5,7
	wait_integer		7,0
	collect_list		1
	put_value		1,6
	execute		4,if_empty_4_0
if_empty_4_3:
	check_nil		1,if_empty_4_1
	get_value		2,3
	get_atom		4,yes
	proceed
if_empty_4_1:
	suspend		if_empty_4_0
	module_entry		multiply_keyed_bag
	predicate		put,18
put_18_0:
	try_me_else		put_18_1
	integer		6
	vector		15
	g_vector		15,19
	wait_value		19,16
	integer		8
	g_less_than		6,8
	collect_value		18
	collect_value		17
	collect_value		16
	collect_value		14
	collect_value		19
	put_marked_value		14,6
	b_increment		14,14
	get_value		7,14
	get_value		9,8
	get_value		11,10
	get_value		13,12
	put_variable		8,7
	b_set_vector_element		4,6,4,8,8
	get_value		8,5
	put_value		4,15
	put_value		5,7
	execute		6,add_to_indexes_6_0
put_18_1:
	try_me_else		put_18_3
	vector		15
	integer		16
	wait_value		6,8
	g_vector		15,19
	wait_value		19,16
	collect_value		18
	collect_value		17
	collect_value		12
	put_value		8,6
	put_value		6,15
	put_value		12,14
	execute		13,remake_and_put_13_0
put_18_3:
	otherwise		put_18_0
	try_me_else		put_18_10
	atom		17
	branch_on_atom		17,2,put_18_10
	bucket_entry_a		get_if_any_and_put,put_18_12
	bucket_entry_a		put,put_18_13
put_18_12:
	collect_value		18
	collect_value		16
	collect_value		14
	collect_value		1
	get_value		2,3
	get_value		4,5
	get_value		6,7
	get_value		8,9
	get_value		10,11
	get_value		12,13
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_13'
	b_raise		2,1,15
	proceed
put_18_13:
	collect_value		18
	collect_value		16
	collect_value		14
	collect_value		1
	get_value		2,3
	get_value		4,5
	get_value		6,7
	get_value		8,9
	get_value		10,11
	get_value		12,13
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_14'
	b_raise		2,1,15
	proceed
put_18_10:
	suspend		put_18_0
	module_entry		multiply_keyed_bag
	predicate		remake_and_put,13
remake_and_put_13_0:
	put_marked_value		14,8
	b_subtract		14,10,10
	put_integer		14,2
	b_multiply		8,14,14
	put_marked_value		9,9
	get_value		9,14
	put_marked_value		14,10
	b_increment		14,14
	get_value		7,14
	get_integer		11,0
	b_integer_to_float		9,7
	b_float_multiply		7,12,7
	b_float_to_integer		7,7
	get_value		13,7
	b_new_vector		7,9
	put_variable		9,11
	put_variable		13,12
	b_set_vector_element		9,10,9,13,13
	get_value		13,5
	create_goal		6
	set_marked_value		1,1
	set_variable		2,5
	set_value		3,3
	set_value		4,6
	set_value		5,12
	set_value		6,10
	enqueue_goal		6,add_to_indexes_6_0
	create_goal		9
	set_integer		1,0
	set_value		2,8
	set_value		3,1
	set_variable		4,3
	set_values_dec		5,5,2
	set_integer		7,0
	set_value		8,7
	set_value		9,11
	enqueue_goal		9,remake_9_0
	execute		3,clear_indexes_3_0
remake_and_put_13_1:
	suspend		remake_and_put_13_0
	module_entry		multiply_keyed_bag
	predicate		get,17
get_17_0:
	create_goal		15
	set_variable		1,18
	set_value		2,2
	set_values_inc		3,16,2
	set_variable		5,17
	set_value		6,6
	set_variable		7,16
	set_value		8,8
	set_marked_value		9,9
	set_values_inc		10,10,5
	set_variable		15,2
	enqueue_goal		15,do_get_15_0
	put_value		6,17
	put_value		8,16
	put_value		10,18
	put_value		11,15
	execute		11,get_data_ids_11_0
get_17_1:
	suspend		get_17_0
	module_entry		multiply_keyed_bag
	predicate		do_get,15
do_get_15_0:
	try_me_else		do_get_15_1
	jump_on_non_list		1,do_get_15_3
	read_car		1,16
	integer		16
	read_cdr		1,17
	vector		7
	try_me_else		do_get_15_6
	g_vector_element		7,16,18
	vector		18
	g_vector		18,18
	collect_list		1
	collect_value		15
	collect_value		4
	collect_value		17
	put_integer		1,0
	b_set_vector_element		7,16,1,1,7
	get_value		1,3
	put_value		1,14
	put_values_inc		3,12,2
	execute		11,if_pack_11_0
do_get_15_6:
	try_me_else		do_get_15_1
	g_vector_element		7,16,18
	wait_integer		18,0
	collect_list		1
	put_value		1,17
	execute		15,do_get_15_0
do_get_15_3:
	check_nil		1,do_get_15_1
	collect_value		14
	collect_value		13
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		2
	get_value		5,6
	put_value		1,4
	put_value		2,15
	execute		3,raise_message_3_0
do_get_15_1:
	suspend		do_get_15_0
	module_entry		multiply_keyed_bag
	predicate		raise_message,3
raise_message_3_0:
	try_me_else		raise_message_3_1
	jump_on_non_atom		1,raise_message_3_3
	put_integer		6,1024
	put_structured_constant		4,'$SCNST_15'
	put_vector		5,3
	write_elements_inc		5,0,1,3
	b_raise		6,4,5
	proceed
raise_message_3_3:
	check_vector		1,2,raise_message_3_1
	read_elements_inc		1,0,4,2
	wait		5
	collect_vector		1
	put_integer		7,1024
	put_structured_constant		1,'$SCNST_16'
	put_vector		6,4
	write_element_value		6,0,4
	write_element_value		6,1,2
	write_element_value		6,2,5
	write_element_value		6,3,3
	b_raise		7,1,6
	proceed
raise_message_3_1:
	suspend		raise_message_3_0
	module_entry		multiply_keyed_bag
	predicate		if_pack,11
if_pack_11_0:
	try_me_else		if_pack_11_1
	integer		1
	integer		3
	try_me_else		if_pack_11_4
	g_less_than		3,1
	collect_value		11
	collect_value		2
	get_value		5,6
	get_value		7,8
	get_value		10,9
	b_increment		3,1
	get_value		4,1
	proceed
if_pack_11_4:
	b_subtract		9,1,1
	get_value		10,1
	get_integer		4,0
	put_value		1,2
	put_values_inc		2,5,4
	put_value		6,11
	execute		6,pack_6_0
if_pack_11_1:
	suspend		if_pack_11_0
	module_entry		multiply_keyed_bag
	predicate		get_if_any,16
get_if_any_16_0:
	create_goal		13
	set_variable		1,17
	set_value		2,2
	set_value		3,16
	set_value		4,14
	set_variable		5,16
	set_value		6,6
	set_variable		7,14
	set_value		8,8
	set_marked_value		9,9
	set_values_inc		10,10,4
	enqueue_goal		13,do_get_if_any_13_0
	put_void		2
	put_value		6,16
	put_value		8,14
	put_value		10,17
	put_value		11,15
	execute		11,get_data_ids_11_0
get_if_any_16_1:
	suspend		get_if_any_16_0
	module_entry		multiply_keyed_bag
	predicate		do_get_if_any,13
do_get_if_any_13_0:
	try_me_else		do_get_if_any_13_1
	jump_on_non_list		1,do_get_if_any_13_3
	read_car		1,14
	integer		14
	read_cdr		1,15
	vector		7
	try_me_else		do_get_if_any_13_6
	g_vector_element		7,14,16
	vector		16
	g_vector		16,16
	collect_list		1
	collect_value		15
	put_integer		1,0
	b_set_vector_element		7,14,1,1,7
	get_value		1,3
	put_value		1,4
	put_values_inc		3,12,2
	execute		11,if_pack_11_0
do_get_if_any_13_6:
	try_me_else		do_get_if_any_13_1
	g_vector_element		7,14,16
	wait_integer		16,0
	collect_list		1
	put_value		1,15
	execute		13,do_get_if_any_13_0
do_get_if_any_13_3:
	check_nil		1,do_get_if_any_13_1
	collect_value		11
	collect_value		4
	collect_value		2
	put_vector		1,0
	get_vector_value		3,1
	get_value		5,6
	get_value		7,8
	get_value		10,9
	get_value		13,12
	proceed
do_get_if_any_13_1:
	suspend		do_get_if_any_13_0
	module_entry		multiply_keyed_bag
	predicate		max_if_any,11
max_if_any_11_0:
	try_me_else		max_if_any_11_1
	jump_on_non_atom		1,max_if_any_11_3
	put_value		12,1
	collect_value		11
	put_func		1,3,carbon_copy
	write_element_marked_value		1,1,12
	write_element_variable		1,2,11
	put_list_val_val		13,1,10
	get_list_value		9,13
	put_marked_variable		1,9
	put_variable		13,10
	b_set_vector_element		3,1,1,13,3
	get_value		3,4
	create_goal		8
	set_value		1,9
	set_values_dec		2,2,2
	set_value		4,10
	set_values_inc		5,5,4
	enqueue_goal		8,if_ordered_index_8_0
	put_values_inc		1,11,2
	put_value		3,9
	execute		3,get_attr_position_3_0
max_if_any_11_3:
	is_integer		1,max_if_any_11_1
	put_integer		12,0
	g_not_less_than		1,12
	integer		11
	g_less_than		1,11
	get_value		9,10
	put_marked_value		10,1
	put_variable		11,9
	b_set_vector_element		3,10,3,11,10
	get_value		10,4
	put_value		4,9
	execute		8,if_ordered_index_8_0
max_if_any_11_1:
	otherwise		max_if_any_11_0
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	get_value		3,4
	get_value		9,10
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_17'
	b_raise		3,2,1
	proceed
max_if_any_11_7:
	suspend		max_if_any_11_0
	module_entry		multiply_keyed_bag
	predicate		if_ordered_index,8
if_ordered_index_8_0:
	try_me_else		if_ordered_index_8_1
	jump_on_non_integer		3,if_ordered_index_8_3
	test_integer		3,0,if_ordered_index_8_1
	put_values_inc		9,1,2
	put_structured_constant		1,'$SCNST_18'
	get_value		4,1
	b_decrement		8,1
	put_values_inc		2,5,2
	put_values_inc		4,9,2
	put_atom		6,ascending
	execute		7,max_sequential_7_0
if_ordered_index_8_3:
	is_vector		3,if_ordered_index_8_1
	jump_on_arity		3,4,if_ordered_index_8_1
	table_entry		if_ordered_index_8_1
	table_entry		if_ordered_index_8_1
	table_entry		if_ordered_index_8_4
	table_entry		if_ordered_index_8_5
if_ordered_index_8_4:
	read_element		3,0,9
	atom		9
	branch_on_atom		9,2,if_ordered_index_8_1
	bucket_entry_a		none,if_ordered_index_8_7
	bucket_entry_a		ordered,if_ordered_index_8_8
if_ordered_index_8_7:
	read_element		3,1,10
	put_value		9,1
	put_value		11,2
	put_reused_func		1,3,none
	write_element_marked_value		1,1,10
	get_vector_value		4,1
	b_decrement		8,1
	put_values_inc		2,5,2
	put_value		4,9
	put_values_dec		5,11,2
	execute		7,max_sequential_7_0
if_ordered_index_8_8:
	read_element		3,1,10
	collect_value		8
	collect_value		1
	put_reused_vector		1,3
	write_element_marked_value		1,0,7
	write_element_variable		1,1,8
	get_list_val_var		10,9,1,3
	put_func		1,2,ordered
	write_element_variable		1,1,9
	get_vector_value		4,1
	put_value		1,8
	put_value		4,9
	execute		7,max_7_0
if_ordered_index_8_5:
	read_element		3,0,9
	wait_atom		9,hashed
	read_elements_inc		3,1,9,2
	put_values_inc		11,1,2
	put_reused_func		1,3,hashed
	write_element_value		1,1,9
	write_element_marked_value		1,2,10
	get_vector_value		4,1
	b_decrement		8,1
	put_values_inc		2,5,2
	put_values_inc		4,11,2
	put_value		6,10
	execute		7,max_sequential_7_0
if_ordered_index_8_1:
	suspend		if_ordered_index_8_0
	module_entry		multiply_keyed_bag
	predicate		max,7
max_7_0:
	try_me_else		max_7_1
	vector		1
	jump_on_arity		1,3,max_7_1
	table_entry		max_7_3
	table_entry		max_7_1
	table_entry		max_7_4
max_7_3:
	collect_value		7
	put_vector		1,0
	get_vector_value		2,1
	get_value		3,4
	get_value		5,6
	proceed
max_7_4:
	read_elements_inc		1,0,8,2
	integer		9
	vector		5
	try_me_else		max_7_7
	g_vector_element		5,9,10
	vector		10
	g_vector		10,10
	collect_value		7
	collect_vector		1
	put_vector		1,1
	write_element_marked_value		1,0,8
	get_vector_value		2,1
	get_value		5,6
	put_func		1,3,put
	write_elements_inc		1,1,8,2
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
max_7_7:
	try_me_else		max_7_1
	g_vector_element		5,9,10
	wait_integer		10,0
	collect_value		8
	put_reused_vector		1,1
	write_element_marked_value		1,0,7
	write_element_variable		1,1,9
	get_list_val_var		3,10,1,8
	put_value		1,9
	put_value		3,8
	execute		7,max_7_0
max_7_1:
	suspend		max_7_0
	module_entry		multiply_keyed_bag
	predicate		max_sequential,7
max_sequential_7_0:
	put_value		9,4
	create_goal		5
	set_variable		1,4
	set_variable		2,8
	set_values_inc		3,5,3
	enqueue_goal		5,max_sequential_5_0
	put_values_inc		5,8,2
	execute		6,get_and_put_all_6_0
max_sequential_7_1:
	suspend		max_sequential_7_0
	module_entry		multiply_keyed_bag
	predicate		get_and_put_all,6
get_and_put_all_6_0:
	try_me_else		get_and_put_all_6_1
	integer		1
	try_me_else		get_and_put_all_6_3
	put_integer		7,0
	g_not_less_than		1,7
	put_value		9,5
	put_marked_value		5,1
	put_variable		7,8
	b_set_vector_element		2,5,2,7,5
	b_decrement		1,1
	create_goal		6
	set_value		1,1
	set_value		2,5
	set_value		3,3
	set_variable		4,5
	set_variable		5,7
	set_marked_value		6,6
	enqueue_goal		6,get_and_put_all_6_0
	put_value		1,2
	put_value		2,8
	put_value		3,6
	put_value		6,9
	execute		7,if_empty_element_7_0
get_and_put_all_6_3:
	collect_value		6
	get_value		2,3
	get_nil		4
	get_nil		5
	proceed
get_and_put_all_6_1:
	suspend		get_and_put_all_6_0
	module_entry		multiply_keyed_bag
	predicate		if_empty_element,7
if_empty_element_7_0:
	try_me_else		if_empty_element_7_1
	jump_on_non_integer		1,if_empty_element_7_3
	test_integer		1,0,if_empty_element_7_1
	collect_value		3
	get_integer		2,0
	get_value		4,5
	get_value		6,7
	proceed
if_empty_element_7_3:
	is_vector		1,if_empty_element_7_1
	g_vector		1,8
	put_variable		9,8
	b_set_vector_element		1,3,1,9,3
	get_value		3,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	put_list_val_val		1,8,7
	get_list_value		6,1
	proceed
if_empty_element_7_1:
	suspend		if_empty_element_7_0
	module_entry		multiply_keyed_bag
	predicate		max_sequential,5
max_sequential_5_0:
	try_me_else		max_sequential_5_1
	jump_on_non_list_var_var		1,max_sequential_5_3,6,7
	wait_list_var_var		2,8,9
	collect_list		1
	collect_list		2
	put_value		10,5
	put_value		1,7
	put_value		2,9
	put_value		5,6
	put_value		6,8
	put_value		7,10
	execute		7,max_seq_7_0
max_sequential_5_3:
	check_nil		1,max_sequential_5_1
	wait_nil		2
	collect_value		5
	collect_value		4
	put_vector		1,0
	get_vector_value		3,1
	proceed
max_sequential_5_1:
	suspend		max_sequential_5_0
	module_entry		multiply_keyed_bag
	predicate		max_seq,7
max_seq_7_0:
	try_me_else		max_seq_7_1
	atom		7
	branch_on_atom		7,2,max_seq_7_1
	bucket_entry_a		get_max_if_any,max_seq_7_3
	bucket_entry_a		get_min_if_any,max_seq_7_4
max_seq_7_3:
	execute		6,do_max_seq_6_0
max_seq_7_4:
	execute		6,do_min_seq_6_0
max_seq_7_1:
	suspend		max_seq_7_0
	module_entry		multiply_keyed_bag
	predicate		do_max_seq,6
do_max_seq_6_0:
	try_me_else		do_max_seq_6_1
	jump_on_non_list_var_var		1,do_max_seq_6_3,7,8
	wait_list_var_var		2,9,10
	collect_list		1
	collect_list		2
	put_marked_value		2,4
	put_vector		1,5
	write_element_value		1,0,5
	write_element_value		1,1,7
	write_element_variable		1,2,5
	write_element_variable		1,3,7
	write_element_variable		1,4,11
	b_apply		2,1
	put_value		1,8
	put_value		2,10
	put_value		8,9
	put_value		9,11
	execute		9,wait_compared_max_9_0
do_max_seq_6_3:
	check_nil		1,do_max_seq_6_1
	wait_nil		2
	collect_value		4
	put_marked_value		6,6
	get_value		6,5
	put_vector		1,1
	write_element_value		1,0,6
	get_vector_value		3,1
	proceed
do_max_seq_6_1:
	suspend		do_max_seq_6_0
	module_entry		multiply_keyed_bag
	predicate		wait_compared_max,9
wait_compared_max_9_0:
	try_me_else		wait_compared_max_9_1
	atom		9
	branch_on_atom		9,2,wait_compared_max_9_1
	bucket_entry_a		no,wait_compared_max_9_3
	bucket_entry_a		yes,wait_compared_max_9_4
wait_compared_max_9_3:
	get_value		5,6
	put_values_inc		5,7,2
	execute		6,do_max_seq_6_0
wait_compared_max_9_4:
	get_value		5,8
	put_value		5,7
	execute		6,do_max_seq_6_0
wait_compared_max_9_1:
	suspend		wait_compared_max_9_0
	module_entry		multiply_keyed_bag
	predicate		do_min_seq,6
do_min_seq_6_0:
	try_me_else		do_min_seq_6_1
	jump_on_non_list_var_var		1,do_min_seq_6_3,7,8
	wait_list_var_var		2,9,10
	collect_list		1
	collect_list		2
	put_marked_value		2,4
	put_vector		1,5
	write_element_value		1,0,5
	write_element_value		1,1,7
	write_element_variable		1,2,5
	write_element_variable		1,3,7
	write_element_variable		1,4,11
	b_apply		2,1
	put_value		1,8
	put_value		2,10
	put_value		8,9
	put_value		9,11
	execute		9,wait_compared_min_9_0
do_min_seq_6_3:
	check_nil		1,do_min_seq_6_1
	wait_nil		2
	collect_value		4
	put_marked_value		6,6
	get_value		6,5
	put_vector		1,1
	write_element_value		1,0,6
	get_vector_value		3,1
	proceed
do_min_seq_6_1:
	suspend		do_min_seq_6_0
	module_entry		multiply_keyed_bag
	predicate		wait_compared_min,9
wait_compared_min_9_0:
	try_me_else		wait_compared_min_9_1
	atom		9
	branch_on_atom		9,2,wait_compared_min_9_1
	bucket_entry_a		no,wait_compared_min_9_3
	bucket_entry_a		yes,wait_compared_min_9_4
wait_compared_min_9_3:
	get_value		7,8
	execute		6,do_min_seq_6_0
wait_compared_min_9_4:
	get_value		7,6
	put_value		6,8
	execute		6,do_min_seq_6_0
wait_compared_min_9_1:
	suspend		wait_compared_min_9_0
	module_entry		multiply_keyed_bag
	predicate		get_all,5
get_all_5_0:
	try_me_else		get_all_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	put_integer		7,0
	b_set_vector_element		3,6,3,7,6
	b_increment		1,1
	create_goal		5
	set_values_inc		1,1,2
	set_value		3,6
	set_value		4,4
	set_variable		5,4
	enqueue_goal		5,get_all_5_0
	put_value		1,3
	put_values_dec		2,5,2
	execute		3,if_get_all_3_0
get_all_5_1:
	try_me_else		get_all_5_3
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_value		3,4
	get_nil		5
	proceed
get_all_5_3:
	suspend		get_all_5_0
	module_entry		multiply_keyed_bag
	predicate		if_get_all,3
if_get_all_3_0:
	try_me_else		if_get_all_3_1
	jump_on_non_integer		1,if_get_all_3_3
	test_integer		1,0,if_get_all_3_1
	get_value		2,3
	proceed
if_get_all_3_3:
	is_vector		1,if_get_all_3_1
	g_vector		1,4
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
if_get_all_3_1:
	suspend		if_get_all_3_0
	module_entry		multiply_keyed_bag
	predicate		get_all,16
get_all_16_0:
	try_me_else		get_all_16_1
	wait		1
	switch_on_type		1,get_all_16_2,get_all_16_3,get_all_16_1,get_all_16_4,get_all_16_1,get_all_16_1
get_all_16_2:
	put_value		17,1
	collect_value		15
	collect_value		14
	collect_value		12
	collect_value		11
	collect_value		2
	put_func		1,3,carbon_copy
	write_element_marked_value		1,1,17
	write_element_variable		1,2,2
	put_list_val_val		11,1,4
	get_list_value		3,11
	get_integer		10,0
	get_integer		13,0
	put_marked_variable		1,3
	put_variable		10,4
	b_set_vector_element		5,1,1,10,5
	get_value		5,6
	create_goal		7
	set_value		1,1
	set_value		2,4
	set_values_inc		3,7,3
	set_value		6,3
	set_value		7,16
	enqueue_goal		7,get_all_i_7_0
	put_value		1,2
	put_value		2,17
	execute		3,get_attr_position_3_0
get_all_16_3:
	put_value		17,1
	put_integer		18,0
	g_not_less_than		17,18
	integer		15
	g_less_than		17,15
	collect_value		14
	collect_value		12
	collect_value		11
	collect_value		2
	get_value		3,4
	get_integer		10,0
	get_integer		13,0
	put_marked_value		1,17
	put_variable		3,2
	b_set_vector_element		5,1,1,3,3
	get_value		3,6
	put_values_inc		3,7,3
	put_values_dec		6,17,2
	execute		7,get_all_i_7_0
get_all_16_4:
	g_vector		1,17
	create_goal		13
	set_variable		1,17
	set_value		2,2
	set_value		3,14
	set_value		4,16
	set_variable		5,16
	set_value		6,6
	set_variable		7,14
	set_value		8,8
	set_marked_value		9,9
	set_values_inc		10,10,4
	enqueue_goal		13,do_get_all_13_0
	put_void		2
	put_value		6,16
	put_value		8,14
	put_value		10,17
	put_value		11,15
	execute		11,get_data_ids_11_0
get_all_16_1:
	otherwise		get_all_16_0
	collect_value		16
	collect_value		15
	collect_value		14
	collect_value		11
	collect_value		2
	get_value		3,4
	get_value		5,6
	get_value		7,8
	get_value		10,9
	get_value		13,12
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_19'
	b_raise		3,2,1
	proceed
get_all_16_6:
	suspend		get_all_16_0
	module_entry		multiply_keyed_bag
	predicate		get_all_i,7
get_all_i_7_0:
	try_me_else		get_all_i_7_1
	jump_on_non_integer		1,get_all_i_7_3
	test_integer		1,0,get_all_i_7_1
	put_structured_constant		1,'$SCNST_20'
	get_value		2,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,6,2
	set_atom		4,ascending
	enqueue_goal		4,sort_4_0
	put_integer		1,0
	put_value		2,5
	put_value		5,8
	execute		5,get_all_5_0
get_all_i_7_3:
	is_vector		1,get_all_i_7_1
	jump_on_arity		1,4,get_all_i_7_1
	table_entry		get_all_i_7_1
	table_entry		get_all_i_7_1
	table_entry		get_all_i_7_4
	table_entry		get_all_i_7_5
get_all_i_7_4:
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,get_all_i_7_1
	bucket_entry_a		none,get_all_i_7_7
	bucket_entry_a		ordered,get_all_i_7_8
get_all_i_7_7:
	read_element		1,1,9
	put_reused_func		1,1,none
	write_element_marked_value		1,1,9
	get_vector_value		2,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,6,2
	set_value		4,9
	enqueue_goal		4,sort_4_0
	put_integer		1,0
	put_value		2,5
	put_value		5,8
	execute		5,get_all_5_0
get_all_i_7_8:
	read_element		1,1,9
	collect_value		6
	collect_value		5
	put_reused_func		1,1,ordered
	write_element_variable		1,1,5
	get_vector_value		2,1
	put_func		1,2,get_all
	write_element_variable		1,1,6
	put_list_val_val		2,1,5
	get_list_value		9,2
	create_goal		4
	set_variable		1,2
	set_values_inc		2,3,2
	set_value		4,7
	enqueue_goal		4,do_get_all_i_4_0
	put_value		1,6
	execute		2,get_ids_only_2_0
get_all_i_7_5:
	read_element		1,0,8
	wait_atom		8,hashed
	read_elements_inc		1,1,8,2
	collect_value		6
	collect_value		5
	put_reused_func		1,1,hashed
	write_element_variable		1,1,5
	write_element_value		1,2,9
	get_vector_value		2,1
	put_func		1,2,get_all
	write_element_variable		1,1,6
	put_list_val_val		2,1,5
	get_list_value		8,2
	create_goal		4
	set_variable		1,2
	set_values_inc		2,3,2
	set_value		4,7
	enqueue_goal		4,do_get_all_i_4_0
	put_value		1,6
	execute		2,get_ids_only_2_0
get_all_i_7_1:
	suspend		get_all_i_7_0
	module_entry		multiply_keyed_bag
	predicate		sort,4
sort_4_0:
	create_goal		3
	set_variable		1,5
	set_marked_value		2,2
	set_value		3,3
	enqueue_goal		3,return_datalist_3_0
	create_goal		3
	set_variable		1,3
	set_values_inc		2,4,2
	enqueue_goal_external		sorter,key_sort,3
	execute		3,trans_datalist_3_0
sort_4_1:
	suspend		sort_4_0
	module_entry		multiply_keyed_bag
	predicate		trans_datalist,3
trans_datalist_3_0:
	try_me_else		trans_datalist_3_1
	jump_on_non_list_var_var		1,trans_datalist_3_3,4,5
	put_marked_value		6,2
	put_integer		7,0
	b_set_vector_element		4,6,4,7,6
	put_vector		7,2
	write_element_value		7,0,4
	write_element_value		7,1,6
	get_reused_list_val_var		3,1,1,7,4
	put_value		1,5
	put_value		3,4
	execute		3,trans_datalist_3_0
trans_datalist_3_3:
	check_nil		1,trans_datalist_3_1
	collect_value		2
	get_nil		3
	proceed
trans_datalist_3_1:
	suspend		trans_datalist_3_0
	module_entry		multiply_keyed_bag
	predicate		return_datalist,3
return_datalist_3_0:
	try_me_else		return_datalist_3_1
	jump_on_non_list_var_var		1,return_datalist_3_3,7,4
	wait_vector		7,2
	read_elements_inc		7,0,5,2
	collect_vector		7
	put_marked_value		7,2
	b_set_vector_element		6,7,5,5,6
	get_reused_list_val_var		3,1,1,6,5
	put_value		1,4
	put_value		3,5
	execute		3,return_datalist_3_0
return_datalist_3_3:
	check_nil		1,return_datalist_3_1
	collect_value		2
	get_nil		3
	proceed
return_datalist_3_1:
	suspend		return_datalist_3_0
	module_entry		multiply_keyed_bag
	predicate		get_ids_only,2
get_ids_only_2_0:
	try_me_else		get_ids_only_2_1
	jump_on_non_list_var_var		1,get_ids_only_2_3,6,3
	wait_vector		6,2
	read_elements_inc		6,0,4,2
	collect_value		4
	collect_vector		6
	get_reused_list_val_var		2,1,1,5,4
	put_values_inc		1,3,2
	execute		2,get_ids_only_2_0
get_ids_only_2_3:
	check_nil		1,get_ids_only_2_1
	get_nil		2
	proceed
get_ids_only_2_1:
	suspend		get_ids_only_2_0
	module_entry		multiply_keyed_bag
	predicate		do_get_all_i,4
do_get_all_i_4_0:
	try_me_else		do_get_all_i_4_1
	jump_on_non_list_var_var		1,do_get_all_i_4_3,5,6
	put_integer		7,0
	b_set_vector_element		2,5,2,7,5
	get_reused_list_val_var		4,1,1,2,7
	put_values_dec		1,6,2
	put_value		4,7
	execute		4,do_get_all_i_4_0
do_get_all_i_4_3:
	check_nil		1,do_get_all_i_4_1
	get_value		2,3
	get_nil		4
	proceed
do_get_all_i_4_1:
	suspend		do_get_all_i_4_0
	module_entry		multiply_keyed_bag
	predicate		do_get_all,13
do_get_all_13_0:
	try_me_else		do_get_all_13_1
	jump_on_non_list		1,do_get_all_13_3
	read_car		1,14
	integer		14
	read_cdr		1,15
	vector		7
	try_me_else		do_get_all_13_6
	g_vector_element		7,14,16
	vector		16
	g_vector		16,16
	put_integer		16,0
	b_set_vector_element		7,14,7,16,14
	get_reused_list_val_var		4,1,1,7,7
	b_increment		12,12
	put_value		1,15
	put_value		4,7
	put_value		7,14
	execute		13,do_get_all_13_0
do_get_all_13_6:
	try_me_else		do_get_all_13_1
	g_vector_element		7,14,16
	wait_integer		16,0
	collect_list		1
	put_value		1,15
	execute		13,do_get_all_13_0
do_get_all_13_3:
	check_nil		1,do_get_all_13_1
	get_nil		4
	put_value		1,3
	put_values_inc		3,12,2
	execute		11,if_pack_11_0
do_get_all_13_1:
	suspend		do_get_all_13_0
	module_entry		multiply_keyed_bag
	predicate		carbon_copy,5
carbon_copy_5_0:
	try_me_else		carbon_copy_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	put_variable		8,7
	b_set_vector_element		3,6,3,8,6
	b_increment		1,1
	create_goal		5
	set_values_inc		1,1,2
	set_value		3,6
	set_value		4,4
	set_variable		5,4
	enqueue_goal		5,carbon_copy_5_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,if_carbon_copy_4_0
carbon_copy_5_1:
	try_me_else		carbon_copy_5_3
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_value		3,4
	get_nil		5
	proceed
carbon_copy_5_3:
	suspend		carbon_copy_5_0
	module_entry		multiply_keyed_bag
	predicate		if_carbon_copy,4
if_carbon_copy_4_0:
	try_me_else		if_carbon_copy_4_1
	jump_on_non_integer		1,if_carbon_copy_4_3
	test_integer		1,0,if_carbon_copy_4_1
	get_integer		2,0
	get_value		3,4
	proceed
if_carbon_copy_4_3:
	is_vector		1,if_carbon_copy_4_1
	g_vector		1,5
	put_marked_value		1,1
	get_value		1,2
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
if_carbon_copy_4_1:
	suspend		if_carbon_copy_4_0
	module_entry		multiply_keyed_bag
	predicate		carbon_copy,10
carbon_copy_10_0:
	try_me_else		carbon_copy_10_1
	jump_on_non_atom		1,carbon_copy_10_3
	put_value		11,1
	collect_value		10
	put_func		1,3,carbon_copy
	write_element_marked_value		1,1,11
	write_element_variable		1,2,10
	put_list_val_val		12,1,4
	get_list_value		3,12
	put_marked_variable		1,3
	put_variable		12,4
	b_set_vector_element		5,1,1,12,5
	get_value		5,6
	create_goal		7
	set_value		1,1
	set_value		2,4
	set_values_inc		3,7,3
	set_values_dec		6,3,2
	enqueue_goal		7,carbon_copy_i_7_0
	put_values_inc		1,10,2
	execute		3,get_attr_position_3_0
carbon_copy_10_3:
	is_integer		1,carbon_copy_10_1
	put_value		11,1
	put_integer		12,0
	g_not_less_than		11,12
	integer		10
	g_less_than		11,10
	put_value		10,2
	get_value		3,4
	put_marked_value		1,11
	put_variable		3,2
	b_set_vector_element		5,1,1,3,3
	get_value		3,6
	put_values_inc		3,7,3
	put_values_dec		6,11,2
	execute		7,carbon_copy_i_7_0
carbon_copy_10_1:
	otherwise		carbon_copy_10_0
	put_value		11,10
	create_goal		4
	set_variable		1,10
	set_variable		2,12
	set_value		3,8
	set_value		4,2
	enqueue_goal		4,do_carbon_copy_4_0
	put_void		2
	put_value		8,12
	execute		11,get_data_ids_11_0
carbon_copy_10_7:
	suspend		carbon_copy_10_0
	module_entry		multiply_keyed_bag
	predicate		carbon_copy_i,7
carbon_copy_i_7_0:
	try_me_else		carbon_copy_i_7_1
	jump_on_non_integer		1,carbon_copy_i_7_3
	test_integer		1,0,carbon_copy_i_7_1
	put_structured_constant		1,'$SCNST_21'
	get_value		2,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,6,2
	set_atom		4,ascending
	enqueue_goal		4,sort_4_0
	put_integer		1,0
	put_value		2,5
	put_value		5,8
	execute		5,carbon_copy_5_0
carbon_copy_i_7_3:
	is_vector		1,carbon_copy_i_7_1
	jump_on_arity		1,4,carbon_copy_i_7_1
	table_entry		carbon_copy_i_7_1
	table_entry		carbon_copy_i_7_1
	table_entry		carbon_copy_i_7_4
	table_entry		carbon_copy_i_7_5
carbon_copy_i_7_4:
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,carbon_copy_i_7_1
	bucket_entry_a		none,carbon_copy_i_7_7
	bucket_entry_a		ordered,carbon_copy_i_7_8
carbon_copy_i_7_7:
	read_element		1,1,9
	collect_vector		1
	put_structured_constant		1,'$SCNST_22'
	get_value		2,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,6,2
	set_value		4,9
	enqueue_goal		4,sort_4_0
	put_integer		1,0
	put_value		2,5
	put_value		5,8
	execute		5,carbon_copy_5_0
carbon_copy_i_7_8:
	read_element		1,1,9
	collect_value		6
	collect_value		5
	put_reused_func		1,1,ordered
	write_element_variable		1,1,5
	get_vector_value		2,1
	put_func		1,2,carbon_copy
	write_element_variable		1,1,6
	put_list_val_val		2,1,5
	get_list_value		9,2
	create_goal		4
	set_variable		1,2
	set_values_inc		2,3,2
	set_value		4,7
	enqueue_goal		4,do_carbon_copy_i_4_0
	put_value		1,6
	execute		2,get_ids_only_2_0
carbon_copy_i_7_5:
	read_element		1,0,8
	wait_atom		8,hashed
	read_elements_inc		1,1,8,2
	collect_value		6
	collect_value		5
	put_reused_func		1,1,hashed
	write_element_variable		1,1,5
	write_element_value		1,2,9
	get_vector_value		2,1
	put_func		1,2,carbon_copy
	write_element_variable		1,1,6
	put_list_val_val		2,1,5
	get_list_value		8,2
	create_goal		4
	set_variable		1,2
	set_values_inc		2,3,2
	set_value		4,7
	enqueue_goal		4,do_carbon_copy_i_4_0
	put_value		1,6
	execute		2,get_ids_only_2_0
carbon_copy_i_7_1:
	suspend		carbon_copy_i_7_0
	module_entry		multiply_keyed_bag
	predicate		do_carbon_copy_i,4
do_carbon_copy_i_4_0:
	try_me_else		do_carbon_copy_i_4_1
	jump_on_non_list_var_var		1,do_carbon_copy_i_4_3,5,6
	put_marked_variable		8,7
	b_set_vector_element		2,5,5,8,2
	get_value		5,7
	get_reused_list_val_var		4,1,1,7,5
	put_value		1,6
	put_value		4,5
	execute		4,do_carbon_copy_i_4_0
do_carbon_copy_i_4_3:
	check_nil		1,do_carbon_copy_i_4_1
	get_value		2,3
	get_nil		4
	proceed
do_carbon_copy_i_4_1:
	suspend		do_carbon_copy_i_4_0
	module_entry		multiply_keyed_bag
	predicate		do_carbon_copy,4
do_carbon_copy_4_0:
	try_me_else		do_carbon_copy_4_1
	jump_on_non_list		1,do_carbon_copy_4_3
	read_car		1,5
	integer		5
	read_cdr		1,6
	vector		2
	try_me_else		do_carbon_copy_4_6
	g_vector_element		2,5,7
	vector		7
	g_vector		7,8
	mark_element		2,5
	put_marked_value		8,7
	b_set_vector_element		2,5,5,8,2
	get_value		5,7
	get_reused_list_val_var		4,1,1,7,5
	put_value		1,6
	put_value		4,5
	execute		4,do_carbon_copy_4_0
do_carbon_copy_4_6:
	try_me_else		do_carbon_copy_4_1
	g_vector_element		2,5,7
	wait_integer		7,0
	collect_list		1
	put_value		1,6
	execute		4,do_carbon_copy_4_0
do_carbon_copy_4_3:
	check_nil		1,do_carbon_copy_4_1
	get_value		2,3
	get_nil		4
	proceed
do_carbon_copy_4_1:
	suspend		do_carbon_copy_4_0
	module_entry		multiply_keyed_bag
	predicate		get_and_put,13
get_and_put_13_0:
	put_value		14,10
	create_goal		11
	set_variable		1,10
	set_value		2,2
	set_values_inc		3,11,2
	set_variable		5,12
	set_value		6,6
	set_variable		7,11
	set_value		8,8
	set_marked_value		9,14
	set_value		10,13
	set_variable		11,2
	enqueue_goal		11,do_get_and_put_11_0
	put_value		6,12
	put_value		8,11
	put_value		11,14
	execute		11,get_data_ids_11_0
get_and_put_13_1:
	suspend		get_and_put_13_0
	module_entry		multiply_keyed_bag
	predicate		do_get_and_put,11
do_get_and_put_11_0:
	try_me_else		do_get_and_put_11_1
	jump_on_non_list		1,do_get_and_put_11_3
	read_car		1,12
	integer		12
	read_cdr		1,13
	vector		7
	try_me_else		do_get_and_put_11_6
	g_vector_element		7,12,14
	vector		14
	g_vector		14,14
	collect_list		1
	collect_value		13
	put_values_inc		14,3,2
	put_marked_value		1,12
	put_variable		3,13
	b_set_vector_element		7,1,4,3,1
	get_value		1,8
	put_value		1,2
	put_values_inc		2,5,2
	put_values_inc		5,14,2
	put_values_dec		7,13,2
	execute		11,modify_indexes_11_0
do_get_and_put_11_6:
	try_me_else		do_get_and_put_11_1
	g_vector_element		7,12,14
	wait_integer		14,0
	collect_list		1
	put_value		1,13
	execute		11,do_get_and_put_11_0
do_get_and_put_11_3:
	check_nil		1,do_get_and_put_11_1
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		2
	get_value		5,6
	put_values_inc		1,10,2
	execute		4,raise_message_4_0
do_get_and_put_11_1:
	suspend		do_get_and_put_11_0
	module_entry		multiply_keyed_bag
	predicate		raise_message,4
raise_message_4_0:
	try_me_else		raise_message_4_1
	jump_on_non_atom		1,raise_message_4_3
	put_integer		7,1024
	put_structured_constant		5,'$SCNST_23'
	put_vector		6,4
	write_elements_inc		6,0,1,4
	b_raise		7,5,6
	proceed
raise_message_4_3:
	check_vector		1,2,raise_message_4_1
	read_elements_inc		1,0,5,2
	wait		6
	collect_vector		1
	put_integer		8,1024
	put_structured_constant		1,'$SCNST_24'
	put_vector		7,5
	write_element_value		7,0,5
	write_element_value		7,1,2
	write_element_value		7,2,6
	write_elements_inc		7,3,3,2
	b_raise		8,1,7
	proceed
raise_message_4_1:
	suspend		raise_message_4_0
	module_entry		multiply_keyed_bag
	predicate		get_if_any_and_put,20
get_if_any_and_put_20_0:
	create_goal		20
	set_variable		1,21
	set_value		2,2
	set_values_inc		3,18,2
	set_variable		5,19
	set_value		6,6
	set_variable		7,18
	set_value		8,8
	set_marked_value		9,9
	set_values_inc		10,10,8
	set_marked_value		18,20
	set_atom		19,get_if_any_and_put
	set_variable		20,2
	enqueue_goal		20,do_get_if_any_and_put_20_0
	put_value		6,19
	put_value		8,18
	put_values_dec		10,21,2
	execute		11,get_data_ids_11_0
get_if_any_and_put_20_1:
	suspend		get_if_any_and_put_20_0
	module_entry		multiply_keyed_bag
	predicate		do_get_if_any_and_put,20
do_get_if_any_and_put_20_0:
	try_me_else		do_get_if_any_and_put_20_1
	jump_on_non_list		1,do_get_if_any_and_put_20_3
	read_car		1,21
	integer		21
	read_cdr		1,22
	vector		7
	try_me_else		do_get_if_any_and_put_20_6
	g_vector_element		7,21,23
	vector		23
	g_vector		23,23
	collect_list		1
	collect_value		17
	collect_value		22
	put_value		17,3
	put_value		22,4
	get_value		10,9
	get_value		12,11
	get_value		14,13
	get_value		16,15
	put_marked_value		1,21
	put_variable		3,9
	b_set_vector_element		7,1,4,3,1
	get_value		1,8
	put_value		1,2
	put_values_inc		2,5,2
	put_value		5,17
	put_value		6,22
	put_value		7,9
	put_value		8,21
	put_values_inc		9,18,3
	execute		11,modify_indexes_11_0
do_get_if_any_and_put_20_6:
	try_me_else		do_get_if_any_and_put_20_1
	g_vector_element		7,21,23
	wait_integer		23,0
	collect_list		1
	put_value		1,22
	execute		20,do_get_if_any_and_put_20_0
do_get_if_any_and_put_20_3:
	check_nil		1,do_get_if_any_and_put_20_1
	put_value		21,4
	put_vector		1,0
	get_vector_value		3,1
	put_value		1,2
	put_values_inc		2,5,13
	put_value		15,21
	put_values_inc		16,18,3
	execute		18,put_18_0
do_get_if_any_and_put_20_1:
	suspend		do_get_if_any_and_put_20_0
	module_entry		multiply_keyed_bag
	predicate		get_and_put_if_any,14
get_and_put_if_any_14_0:
	put_value		15,10
	create_goal		12
	set_variable		1,10
	set_value		2,2
	set_values_inc		3,11,2
	set_variable		5,12
	set_value		6,6
	set_variable		7,11
	set_value		8,8
	set_value		9,13
	set_marked_value		10,15
	set_value		11,14
	set_variable		12,2
	enqueue_goal		12,do_get_and_put_if_any_12_0
	put_value		6,12
	put_value		8,11
	put_value		11,15
	execute		11,get_data_ids_11_0
get_and_put_if_any_14_1:
	suspend		get_and_put_if_any_14_0
	module_entry		multiply_keyed_bag
	predicate		do_get_and_put_if_any,12
do_get_and_put_if_any_12_0:
	try_me_else		do_get_and_put_if_any_12_1
	jump_on_non_list		1,do_get_and_put_if_any_12_3
	read_car		1,13
	integer		13
	read_cdr		1,14
	vector		7
	try_me_else		do_get_and_put_if_any_12_6
	g_vector_element		7,13,15
	vector		15
	g_vector		15,15
	collect_list		1
	collect_value		14
	put_values_inc		14,3,2
	put_vector		1,0
	get_vector_value		9,1
	put_marked_value		1,13
	put_variable		3,9
	b_set_vector_element		7,1,4,3,1
	get_value		1,8
	put_value		1,2
	put_values_inc		2,5,2
	put_values_inc		5,14,2
	put_value		7,9
	put_value		8,13
	put_values_inc		9,10,3
	execute		11,modify_indexes_11_0
do_get_and_put_if_any_12_6:
	try_me_else		do_get_and_put_if_any_12_1
	g_vector_element		7,13,15
	wait_integer		15,0
	collect_list		1
	put_value		1,14
	execute		12,do_get_and_put_if_any_12_0
do_get_and_put_if_any_12_3:
	check_nil		1,do_get_and_put_if_any_12_1
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		2
	put_vector		1,0
	get_vector_value		3,1
	get_value		4,9
	get_value		5,6
	get_value		7,8
	proceed
do_get_and_put_if_any_12_1:
	suspend		do_get_and_put_if_any_12_0
	module_entry		multiply_keyed_bag
	predicate		get_data_ids,11
get_data_ids_11_0:
	try_me_else		get_data_ids_11_1
	vector		1
	jump_on_arity		1,4,get_data_ids_11_1
	table_entry		get_data_ids_11_1
	table_entry		get_data_ids_11_1
	table_entry		get_data_ids_11_3
	table_entry		get_data_ids_11_4
get_data_ids_11_3:
	read_element		1,0,12
	atom		12
	branch_on_atom		12,2,get_data_ids_11_1
	bucket_entry_a		\,get_data_ids_11_6
	bucket_entry_a		not,get_data_ids_11_7
get_data_ids_11_6:
	read_element		1,1,13
	put_reused_func		1,1,\
	write_element_variable		1,1,12
	get_vector_value		2,1
	create_goal		3
	set_variable		1,14
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	put_values_dec		1,13,2
	put_value		10,14
	execute		11,get_data_ids_11_0
get_data_ids_11_7:
	read_element		1,1,13
	put_reused_func		1,1,not
	write_element_variable		1,1,12
	get_vector_value		2,1
	create_goal		3
	set_variable		1,14
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	put_values_dec		1,13,2
	put_value		10,14
	execute		11,get_data_ids_11_0
get_data_ids_11_4:
	read_element		1,0,12
	atom		12
	hash_on_atom		12,8,get_data_ids_11_1
	bucket_entry_a		/\,get_data_ids_11_9
	bucket_entry_a		=,get_data_ids_11_10
	bucket_entry_a		\/,get_data_ids_11_11
	bucket_entry_a		\=,get_data_ids_11_12
	bucket_entry_a		and,get_data_ids_11_13
	bucket_entry_a		equal,get_data_ids_11_14
	bucket_entry_a		not_equal,get_data_ids_11_15
	bucket_entry_a		or,get_data_ids_11_16
get_data_ids_11_9:
	read_elements_inc		1,1,13,2
	put_reused_func		15,1,/\
	write_element_variable		15,1,12
	write_element_variable		15,2,1
	get_vector_value		2,15
	create_goal		3
	set_variable		1,15
	set_variable		2,2
	set_value		3,10
	enqueue_goal		3,do_and_3_0
	create_goal		11
	set_value		1,14
	set_value		2,1
	set_variable		3,16
	set_value		4,4
	set_variable		5,14
	set_value		6,6
	set_variable		7,10
	set_value		8,8
	set_marked_value		9,9
	set_value		10,2
	set_marked_value		11,11
	enqueue_goal		11,get_data_ids_11_0
	put_values_dec		1,13,2
	put_value		4,16
	put_value		6,14
	put_value		8,10
	put_value		10,15
	execute		11,get_data_ids_11_0
get_data_ids_11_10:
	read_element		1,1,13
	jump_on_non_atom		13,get_data_ids_11_18
	read_element		1,2,14
	collect_value		11
	put_reused_func		1,1,=
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	put_func		1,3,carbon_copy
	write_element_value		1,1,13
	write_element_variable		1,2,2
	put_list_val_val		11,1,4
	get_list_value		3,11
	create_goal		8
	set_variable		1,3
	set_value		2,14
	set_values_inc		3,9,2
	set_values_inc		5,5,4
	enqueue_goal		8,get_ids_8_0
	put_value		1,2
	put_value		2,13
	execute		3,get_attr_position_3_0
get_data_ids_11_18:
	is_integer		13,get_data_ids_11_1
	read_element		1,2,14
	put_integer		15,0
	g_not_less_than		13,15
	integer		11
	g_less_than		13,11
	put_reused_func		1,1,=
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	get_value		3,4
	put_values_inc		1,13,2
	put_values_inc		3,9,2
	execute		8,get_ids_8_0
get_data_ids_11_11:
	read_elements_inc		1,1,13,2
	put_reused_func		15,1,\/
	write_element_variable		15,1,12
	write_element_variable		15,2,1
	get_vector_value		2,15
	create_goal		3
	set_variable		1,15
	set_variable		2,2
	set_value		3,10
	enqueue_goal		3,do_or_3_0
	create_goal		11
	set_value		1,14
	set_value		2,1
	set_variable		3,16
	set_value		4,4
	set_variable		5,14
	set_value		6,6
	set_variable		7,10
	set_value		8,8
	set_marked_value		9,9
	set_value		10,2
	set_marked_value		11,11
	enqueue_goal		11,get_data_ids_11_0
	put_values_dec		1,13,2
	put_value		4,16
	put_value		6,14
	put_value		8,10
	put_value		10,15
	execute		11,get_data_ids_11_0
get_data_ids_11_12:
	read_element		1,1,13
	jump_on_non_atom		13,get_data_ids_11_20
	read_element		1,2,14
	collect_value		11
	put_reused_func		1,1,\=
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	put_func		1,3,carbon_copy
	write_element_value		1,1,13
	write_element_variable		1,2,2
	put_list_val_val		11,1,4
	get_list_value		3,11
	create_goal		3
	set_variable		1,1
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	create_goal		8
	set_variable		1,3
	set_value		2,14
	set_value		3,9
	set_value		4,1
	set_values_inc		5,5,4
	enqueue_goal		8,get_ids_8_0
	put_value		1,2
	put_value		2,13
	execute		3,get_attr_position_3_0
get_data_ids_11_20:
	is_integer		13,get_data_ids_11_1
	read_element		1,2,14
	put_integer		15,0
	g_not_less_than		13,15
	integer		11
	g_less_than		13,11
	put_reused_func		1,1,\=
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	get_value		3,4
	create_goal		3
	set_variable		1,4
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	put_values_inc		1,13,2
	put_value		3,9
	execute		8,get_ids_8_0
get_data_ids_11_13:
	read_elements_inc		1,1,13,2
	put_reused_func		15,1,and
	write_element_variable		15,1,12
	write_element_variable		15,2,1
	get_vector_value		2,15
	create_goal		3
	set_variable		1,15
	set_variable		2,2
	set_value		3,10
	enqueue_goal		3,do_and_3_0
	create_goal		11
	set_value		1,14
	set_value		2,1
	set_variable		3,16
	set_value		4,4
	set_variable		5,14
	set_value		6,6
	set_variable		7,10
	set_value		8,8
	set_marked_value		9,9
	set_value		10,2
	set_marked_value		11,11
	enqueue_goal		11,get_data_ids_11_0
	put_values_dec		1,13,2
	put_value		4,16
	put_value		6,14
	put_value		8,10
	put_value		10,15
	execute		11,get_data_ids_11_0
get_data_ids_11_14:
	read_element		1,1,13
	jump_on_non_atom		13,get_data_ids_11_22
	read_element		1,2,14
	collect_value		11
	put_reused_func		1,1,equal
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	put_func		1,3,carbon_copy
	write_element_value		1,1,13
	write_element_variable		1,2,2
	put_list_val_val		11,1,4
	get_list_value		3,11
	create_goal		8
	set_variable		1,3
	set_value		2,14
	set_values_inc		3,9,2
	set_values_inc		5,5,4
	enqueue_goal		8,get_ids_8_0
	put_value		1,2
	put_value		2,13
	execute		3,get_attr_position_3_0
get_data_ids_11_22:
	is_integer		13,get_data_ids_11_1
	read_element		1,2,14
	put_integer		15,0
	g_not_less_than		13,15
	integer		11
	g_less_than		13,11
	put_reused_func		1,1,equal
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	get_value		3,4
	put_values_inc		1,13,2
	put_values_inc		3,9,2
	execute		8,get_ids_8_0
get_data_ids_11_15:
	read_element		1,1,13
	jump_on_non_atom		13,get_data_ids_11_24
	read_element		1,2,14
	collect_value		11
	put_reused_func		1,1,not_equal
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	put_func		1,3,carbon_copy
	write_element_value		1,1,13
	write_element_variable		1,2,2
	put_list_val_val		11,1,4
	get_list_value		3,11
	create_goal		3
	set_variable		1,1
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	create_goal		8
	set_variable		1,3
	set_value		2,14
	set_value		3,9
	set_value		4,1
	set_values_inc		5,5,4
	enqueue_goal		8,get_ids_8_0
	put_value		1,2
	put_value		2,13
	execute		3,get_attr_position_3_0
get_data_ids_11_24:
	is_integer		13,get_data_ids_11_1
	read_element		1,2,14
	put_integer		15,0
	g_not_less_than		13,15
	integer		11
	g_less_than		13,11
	put_reused_func		1,1,not_equal
	write_element_marked_value		1,1,13
	write_element_marked_value		1,2,14
	get_vector_value		2,1
	get_value		3,4
	create_goal		3
	set_variable		1,4
	set_value		2,10
	set_marked_value		3,9
	enqueue_goal		3,do_not_3_0
	put_values_inc		1,13,2
	put_value		3,9
	execute		8,get_ids_8_0
get_data_ids_11_16:
	read_elements_inc		1,1,13,2
	put_reused_func		15,1,or
	write_element_variable		15,1,12
	write_element_variable		15,2,1
	get_vector_value		2,15
	create_goal		3
	set_variable		1,15
	set_variable		2,2
	set_value		3,10
	enqueue_goal		3,do_or_3_0
	create_goal		11
	set_value		1,14
	set_value		2,1
	set_variable		3,16
	set_value		4,4
	set_variable		5,14
	set_value		6,6
	set_variable		7,10
	set_value		8,8
	set_marked_value		9,9
	set_value		10,2
	set_marked_value		11,11
	enqueue_goal		11,get_data_ids_11_0
	put_values_dec		1,13,2
	put_value		4,16
	put_value		6,14
	put_value		8,10
	put_value		10,15
	execute		11,get_data_ids_11_0
get_data_ids_11_1:
	otherwise		get_data_ids_11_0
	collect_value		11
	collect_value		9
	put_marked_value		1,1
	get_value		1,2
	get_value		3,4
	get_value		5,6
	get_value		7,8
	get_nil		10
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_25'
	b_raise		3,2,1
	proceed
get_data_ids_11_43:
	suspend		get_data_ids_11_0
	module_entry		multiply_keyed_bag
	predicate		get_attr_position,3
get_attr_position_3_0:
	try_me_else		get_attr_position_3_1
	jump_on_non_list_var_var		1,get_attr_position_3_3,4,5
	wait_nil		5
	collect_list		1
	collect_value		2
	get_value		3,4
	proceed
get_attr_position_3_3:
	check_nil		1,get_attr_position_3_1
	get_integer		3,0
	put_integer		3,1024
	put_structured_constant		1,'$SCNST_26'
	b_raise		3,1,2
	proceed
get_attr_position_3_1:
	suspend		get_attr_position_3_0
	module_entry		multiply_keyed_bag
	predicate		get_ids,8
get_ids_8_0:
	put_marked_value		10,1
	put_variable		11,9
	b_set_vector_element		5,10,5,11,10
	get_value		10,6
	put_value		6,9
	execute		8,do_get_ids_8_0
get_ids_8_1:
	suspend		get_ids_8_0
	module_entry		multiply_keyed_bag
	predicate		do_get_ids,8
do_get_ids_8_0:
	try_me_else		do_get_ids_8_1
	jump_on_non_integer		5,do_get_ids_8_3
	test_integer		5,0,do_get_ids_8_1
	get_integer		6,0
	put_integer		5,0
	put_values_inc		6,7,2
	execute		7,sequential_search_7_0
do_get_ids_8_3:
	is_vector		5,do_get_ids_8_1
	jump_on_arity		5,4,do_get_ids_8_1
	table_entry		do_get_ids_8_1
	table_entry		do_get_ids_8_1
	table_entry		do_get_ids_8_4
	table_entry		do_get_ids_8_5
do_get_ids_8_4:
	read_element		5,0,9
	atom		9
	branch_on_atom		9,2,do_get_ids_8_1
	bucket_entry_a		none,do_get_ids_8_7
	bucket_entry_a		ordered,do_get_ids_8_8
do_get_ids_8_7:
	read_element		5,1,10
	put_reused_func		5,5,none
	write_element_value		5,1,10
	get_vector_value		6,5
	put_integer		5,0
	put_values_inc		6,7,2
	execute		7,sequential_search_7_0
do_get_ids_8_8:
	read_element		5,1,10
	collect_value		3
	collect_value		1
	put_reused_func		1,5,ordered
	write_element_variable		1,1,3
	get_vector_value		6,1
	get_value		7,8
	put_func		1,3,carbon_copy
	write_element_value		1,1,2
	write_element_value		1,2,4
	put_list_val_val		2,1,3
	get_list_value		10,2
	proceed
do_get_ids_8_5:
	read_element		5,0,9
	wait_atom		9,hashed
	read_elements_inc		5,1,9,2
	collect_value		3
	collect_value		1
	put_reused_func		1,5,hashed
	write_element_variable		1,1,3
	write_element_value		1,2,10
	get_vector_value		6,1
	get_value		7,8
	put_func		1,3,carbon_copy
	write_element_value		1,1,2
	write_element_value		1,2,4
	put_list_val_val		2,1,3
	get_list_value		9,2
	proceed
do_get_ids_8_1:
	suspend		do_get_ids_8_0
	module_entry		multiply_keyed_bag
	predicate		sequential_search,7
sequential_search_7_0:
	try_me_else		sequential_search_7_1
	integer		3
	integer		5
	g_less_than		5,3
	put_value		8,5
	put_value		11,2
	put_value		5,4
	put_value		12,1
	put_marked_value		1,8
	put_variable		2,9
	b_set_vector_element		6,1,1,2,2
	b_increment		8,4
	create_goal		7
	set_marked_value		1,12
	set_variable		2,10
	set_value		3,3
	set_variable		4,6
	set_value		5,4
	set_value		6,2
	set_value		7,7
	enqueue_goal		7,sequential_search_7_0
	put_value		2,9
	put_values_dec		3,11,2
	put_value		7,8
	put_value		8,12
	execute		8,if_same_key_8_0
sequential_search_7_1:
	try_me_else		sequential_search_7_3
	wait_value		3,5
	collect_value		3
	collect_value		2
	collect_value		1
	collect_value		5
	get_nil		4
	get_value		6,7
	proceed
sequential_search_7_3:
	suspend		sequential_search_7_0
	module_entry		multiply_keyed_bag
	predicate		if_same_key,8
if_same_key_8_0:
	try_me_else		if_same_key_8_1
	jump_on_non_integer		1,if_same_key_8_3
	test_integer		1,0,if_same_key_8_1
	collect_value		8
	collect_value		7
	get_integer		2,0
	get_value		3,4
	get_value		5,6
	proceed
if_same_key_8_3:
	is_vector		1,if_same_key_8_1
	g_vector		1,9
	put_variable		10,9
	b_set_vector_element		1,8,1,10,8
	get_value		8,2
	put_value		2,9
	execute		7,check_if_same_key_7_0
if_same_key_8_1:
	suspend		if_same_key_8_0
	module_entry		multiply_keyed_bag
	predicate		check_if_same_key,7
check_if_same_key_7_0:
	try_me_else		check_if_same_key_7_1
	wait_value		1,3
	collect_value		3
	put_marked_value		1,1
	get_value		1,2
	get_value		1,4
	put_list_val_val		1,7,6
	get_list_value		5,1
	proceed
check_if_same_key_7_1:
	otherwise		check_if_same_key_7_0
	collect_value		7
	get_value		1,2
	get_value		3,4
	get_value		5,6
	proceed
check_if_same_key_7_3:
	suspend		check_if_same_key_7_0
	module_entry		multiply_keyed_bag
	predicate		do_and,3
do_and_3_0:
	create_goal		3
	set_variable		1,4
	set_variable		2,5
	set_value		3,3
	enqueue_goal		3,do_do_and_3_0
	create_goal		2
	set_value		1,2
	set_value		2,5
	enqueue_goal_external		sorter,sort,2
	put_value		2,4
	execute_external		sorter,sort,2
do_and_3_1:
	suspend		do_and_3_0
	module_entry		multiply_keyed_bag
	predicate		do_do_and,3
do_do_and_3_0:
	try_me_else		do_do_and_3_1
	jump_on_non_list		1,do_do_and_3_3
	read_car		1,4
	try_me_else		do_do_and_3_4
	integer		4
	read_cdr		1,5
	list		2
	read_car		2,6
	integer		6
	read_cdr		2,7
	try_me_else		do_do_and_3_8
	g_less_than		4,6
	collect_list		1
	collect_list		2
	put_value		1,5
	put_value		2,7
	put_value		4,6
	execute		4,get_away_x_4_0
do_do_and_3_8:
	try_me_else		do_do_and_3_4
	g_less_than		6,4
	collect_list		1
	collect_list		2
	put_value		1,5
	put_value		2,7
	execute		4,get_away_y_4_0
do_do_and_3_4:
	read_cdr		1,5
	try_me_else		do_do_and_3_1
	wait_list_var_var		2,6,7
	wait_value		6,4
	collect_list		2
	collect_value		4
	get_reused_list_val_var		3,1,1,6,4
	put_value		1,5
	put_value		2,7
	put_value		3,4
	execute		3,do_do_and_3_0
do_do_and_3_3:
	check_nil		1,do_do_and_3_1
	collect_value		2
	get_nil		3
	proceed
do_do_and_3_1:
	try_me_else		do_do_and_3_10
	wait_nil		2
	collect_value		1
	get_nil		3
	proceed
do_do_and_3_10:
	suspend		do_do_and_3_0
	module_entry		multiply_keyed_bag
	predicate		get_away_x,4
get_away_x_4_0:
	try_me_else		get_away_x_4_1
	jump_on_non_list		1,get_away_x_4_3
	read_car		1,5
	try_me_else		get_away_x_4_4
	integer		5
	read_cdr		1,6
	integer		4
	try_me_else		get_away_x_4_7
	g_less_than		5,4
	collect_list		1
	put_value		1,6
	execute		4,get_away_x_4_0
get_away_x_4_7:
	try_me_else		get_away_x_4_4
	g_less_than		4,5
	collect_list		1
	put_value		1,6
	put_value		4,5
	execute		4,get_away_y_4_0
get_away_x_4_4:
	read_cdr		1,6
	try_me_else		get_away_x_4_1
	wait_value		4,5
	collect_value		5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,6
	put_value		3,4
	execute		3,do_do_and_3_0
get_away_x_4_3:
	check_nil		1,get_away_x_4_1
	collect_value		4
	collect_value		2
	get_nil		3
	proceed
get_away_x_4_1:
	suspend		get_away_x_4_0
	module_entry		multiply_keyed_bag
	predicate		get_away_y,4
get_away_y_4_0:
	try_me_else		get_away_y_4_1
	jump_on_non_list		2,get_away_y_4_3
	read_car		2,5
	try_me_else		get_away_y_4_4
	integer		5
	read_cdr		2,6
	integer		4
	try_me_else		get_away_y_4_7
	g_less_than		5,4
	collect_list		2
	put_value		2,6
	execute		4,get_away_y_4_0
get_away_y_4_7:
	try_me_else		get_away_y_4_4
	g_less_than		4,5
	collect_list		2
	put_value		2,6
	put_value		4,5
	execute		4,get_away_x_4_0
get_away_y_4_4:
	read_cdr		2,6
	try_me_else		get_away_y_4_1
	wait_value		4,5
	collect_value		5
	get_reused_list_val_var		3,2,2,4,4
	put_value		2,6
	put_value		3,4
	execute		3,do_do_and_3_0
get_away_y_4_3:
	check_nil		2,get_away_y_4_1
	collect_value		4
	collect_value		1
	get_nil		3
	proceed
get_away_y_4_1:
	suspend		get_away_y_4_0
	module_entry		multiply_keyed_bag
	predicate		do_or,3
do_or_3_0:
	create_goal		3
	set_variable		1,4
	set_variable		2,5
	set_value		3,3
	enqueue_goal		3,do_do_or_3_0
	create_goal		2
	set_value		1,2
	set_value		2,5
	enqueue_goal_external		sorter,sort,2
	put_value		2,4
	execute_external		sorter,sort,2
do_or_3_1:
	suspend		do_or_3_0
	module_entry		multiply_keyed_bag
	predicate		do_do_or,3
do_do_or_3_0:
	try_me_else		do_do_or_3_1
	jump_on_non_list		1,do_do_or_3_3
	read_car		1,4
	try_me_else		do_do_or_3_4
	integer		4
	read_cdr		1,5
	list		2
	read_car		2,6
	integer		6
	read_cdr		2,7
	try_me_else		do_do_or_3_8
	g_less_than		4,6
	collect_list		2
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		2,7
	put_value		3,4
	put_value		4,6
	execute		4,consume_x_4_0
do_do_or_3_8:
	try_me_else		do_do_or_3_4
	g_less_than		6,4
	collect_list		2
	get_reused_list_val_var		3,1,1,6,6
	put_value		1,5
	put_values_dec		2,7,2
	execute		4,consume_y_4_0
do_do_or_3_4:
	read_cdr		1,5
	try_me_else		do_do_or_3_1
	wait_list_var_var		2,6,7
	wait_value		6,4
	collect_list		2
	collect_value		4
	get_reused_list_val_var		3,1,1,6,4
	put_value		1,5
	put_value		2,7
	put_value		3,4
	execute		3,do_do_or_3_0
do_do_or_3_3:
	check_nil		1,do_do_or_3_1
	get_value		2,3
	proceed
do_do_or_3_1:
	try_me_else		do_do_or_3_10
	wait_nil		2
	get_value		1,3
	proceed
do_do_or_3_10:
	suspend		do_do_or_3_0
	module_entry		multiply_keyed_bag
	predicate		consume_x,4
consume_x_4_0:
	try_me_else		consume_x_4_1
	jump_on_non_list		1,consume_x_4_3
	read_car		1,5
	try_me_else		consume_x_4_4
	integer		5
	read_cdr		1,6
	integer		4
	try_me_else		consume_x_4_7
	g_less_than		5,4
	get_reused_list_val_var		3,1,1,5,5
	put_value		1,6
	put_value		3,5
	execute		4,consume_x_4_0
consume_x_4_7:
	try_me_else		consume_x_4_4
	g_less_than		4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,6
	put_values_inc		3,4,2
	execute		4,consume_y_4_0
consume_x_4_4:
	read_cdr		1,6
	try_me_else		consume_x_4_1
	wait_value		4,5
	collect_value		5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,6
	put_value		3,4
	execute		3,do_do_or_3_0
consume_x_4_3:
	check_nil		1,consume_x_4_1
	put_list_val_val		1,4,2
	get_list_value		3,1
	proceed
consume_x_4_1:
	suspend		consume_x_4_0
	module_entry		multiply_keyed_bag
	predicate		consume_y,4
consume_y_4_0:
	try_me_else		consume_y_4_1
	jump_on_non_list		2,consume_y_4_3
	read_car		2,5
	try_me_else		consume_y_4_4
	integer		5
	read_cdr		2,6
	integer		4
	try_me_else		consume_y_4_7
	g_less_than		5,4
	get_reused_list_val_var		3,2,2,5,5
	put_values_dec		2,6,2
	execute		4,consume_y_4_0
consume_y_4_7:
	try_me_else		consume_y_4_4
	g_less_than		4,5
	get_reused_list_val_var		3,2,2,4,4
	put_value		2,6
	put_values_inc		3,4,2
	execute		4,consume_x_4_0
consume_y_4_4:
	read_cdr		2,6
	try_me_else		consume_y_4_1
	wait_value		4,5
	collect_value		5
	get_reused_list_val_var		3,2,2,4,4
	put_value		2,6
	put_value		3,4
	execute		3,do_do_or_3_0
consume_y_4_3:
	check_nil		2,consume_y_4_1
	put_list_val_val		2,4,1
	get_list_value		3,2
	proceed
consume_y_4_1:
	suspend		consume_y_4_0
	module_entry		multiply_keyed_bag
	predicate		do_not,3
do_not_3_0:
	create_goal		4
	set_variable		1,4
	set_values_inc		2,2,2
	set_integer		4,0
	enqueue_goal		4,do_do_not_4_0
	put_value		2,4
	execute_external		sorter,sort,2
do_not_3_1:
	suspend		do_not_3_0
	module_entry		multiply_keyed_bag
	predicate		do_do_not,4
do_do_not_4_0:
	try_me_else		do_do_not_4_1
	jump_on_non_list		1,do_do_not_4_3
	read_car		1,5
	try_me_else		do_do_not_4_4
	integer		5
	read_cdr		1,6
	integer		4
	g_less_than		4,5
	put_reused_list		1,1
	write_car_marked_value		1,4
	write_cdr_variable		1,7
	get_list_value		2,1
	b_increment		4,4
	put_list_val_val		1,5,6
	put_value		2,7
	execute		4,do_do_not_4_0
do_do_not_4_4:
	read_cdr		1,6
	try_me_else		do_do_not_4_1
	wait_value		4,5
	collect_list		1
	collect_value		5
	b_increment		4,4
	put_value		1,6
	execute		4,do_do_not_4_0
do_do_not_4_3:
	check_nil		1,do_do_not_4_1
	put_value		1,4
	execute		3,append_rest_3_0
do_do_not_4_1:
	suspend		do_do_not_4_0
	module_entry		multiply_keyed_bag
	predicate		append_rest,3
append_rest_3_0:
	try_me_else		append_rest_3_1
	integer		1
	integer		3
	g_less_than		1,3
	put_list		5
	write_car_marked_value		5,1
	write_cdr_variable		5,4
	get_list_value		2,5
	b_increment		1,1
	put_value		2,4
	execute		3,append_rest_3_0
append_rest_3_1:
	try_me_else		append_rest_3_3
	wait_value		1,3
	collect_value		1
	collect_value		3
	get_nil		2
	proceed
append_rest_3_3:
	suspend		append_rest_3_0
	module_entry		multiply_keyed_bag
	predicate		add_to_indexes,6
add_to_indexes_6_0:
	try_me_else		add_to_indexes_6_1
	jump_on_non_list_var_var		1,add_to_indexes_6_3,7,8
	put_marked_value		9,7
	put_variable		10,11
	b_set_vector_element		2,9,2,10,9
	b_vector_element		4,7,4,7
	put_func		10,3,put
	write_element_value		10,1,4
	write_element_marked_value		10,2,6
	put_reused_list_val_var		4,1,10,10
	create_goal		6
	set_values_inc		1,8,2
	set_value		3,3
	set_value		4,7
	set_values_inc		5,5,2
	enqueue_goal		6,add_to_indexes_6_0
	put_value		1,2
	put_value		2,11
	put_value		3,4
	put_value		4,10
	execute		4,get_index_stream_4_0
add_to_indexes_6_3:
	check_nil		1,add_to_indexes_6_1
	collect_value		6
	get_value		2,3
	get_value		4,5
	proceed
add_to_indexes_6_1:
	suspend		add_to_indexes_6_0
	module_entry		multiply_keyed_bag
	predicate		get_index_stream,4
get_index_stream_4_0:
	try_me_else		get_index_stream_4_1
	vector		1
	jump_on_arity		1,4,get_index_stream_4_1
	table_entry		get_index_stream_4_1
	table_entry		get_index_stream_4_1
	table_entry		get_index_stream_4_3
	table_entry		get_index_stream_4_4
get_index_stream_4_3:
	read_element		1,0,5
	wait_atom		5,ordered
	read_element		1,1,5
	get_value		3,5
	put_reused_func		1,1,ordered
	write_element_value		1,1,4
	get_vector_value		2,1
	proceed
get_index_stream_4_4:
	read_element		1,0,5
	wait_atom		5,hashed
	read_elements_inc		1,1,5,2
	get_value		3,5
	put_reused_func		1,1,hashed
	write_element_value		1,1,4
	write_element_value		1,2,6
	get_vector_value		2,1
	proceed
get_index_stream_4_1:
	suspend		get_index_stream_4_0
	module_entry		multiply_keyed_bag
	predicate		modify_indexes,11
modify_indexes_11_0:
	create_goal		7
	set_marked_value		1,1
	set_variable		2,12
	set_values_inc		3,6,2
	set_values_inc		5,9,3
	enqueue_goal		7,unify_new_keyes_7_0
	put_value		6,8
	put_value		7,12
	execute		7,modify_indexes_7_0
modify_indexes_11_1:
	suspend		modify_indexes_11_0
	module_entry		multiply_keyed_bag
	predicate		modify_indexes,7
modify_indexes_7_0:
	try_me_else		modify_indexes_7_1
	jump_on_non_list_var_var		1,modify_indexes_7_3,8,9
	put_marked_value		10,8
	put_variable		11,13
	b_set_vector_element		2,10,2,11,10
	b_vector_element		4,8,4,8
	put_func		11,3,get_all
	write_element_marked_value		11,1,4
	write_element_variable		11,2,14
	put_reused_list_val_var		12,1,11,1
	put_list		16
	write_car_variable		16,11
	write_cdr_variable		16,15
	get_list_value		7,16
	create_goal		7
	set_values_inc		1,9,2
	set_value		3,3
	set_value		4,8
	set_value		5,5
	set_marked_value		6,6
	set_value		7,15
	enqueue_goal		7,modify_indexes_7_0
	create_goal		6
	set_value		1,14
	set_value		2,6
	set_value		3,1
	set_variable		4,5
	set_value		5,4
	set_value		6,11
	enqueue_goal		6,modify_index_6_0
	put_value		1,2
	put_values_dec		2,13,2
	put_value		4,5
	execute		4,get_index_stream_4_0
modify_indexes_7_3:
	check_nil		1,modify_indexes_7_1
	collect_value		6
	get_value		2,3
	get_value		4,5
	get_nil		7
	proceed
modify_indexes_7_1:
	suspend		modify_indexes_7_0
	module_entry		multiply_keyed_bag
	predicate		unify_new_keyes,7
unify_new_keyes_7_0:
	try_me_else		unify_new_keyes_7_1
	vector		3
	integer		5
	g_vector		3,8
	wait_value		8,5
	collect_value		7
	collect_value		6
	execute		4,unify_new_keyes_4_0
unify_new_keyes_7_1:
	otherwise		unify_new_keyes_7_0
	try_me_else		unify_new_keyes_7_7
	atom		6
	branch_on_atom		6,3,unify_new_keyes_7_7
	bucket_entry_a		get_and_put,unify_new_keyes_7_9
	bucket_entry_a		get_and_put_if_any,unify_new_keyes_7_10
	bucket_entry_a		get_if_any_and_put,unify_new_keyes_7_11
unify_new_keyes_7_9:
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		4,0
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_27'
	b_raise		2,1,3
	proceed
unify_new_keyes_7_10:
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		4,0
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_28'
	b_raise		2,1,3
	proceed
unify_new_keyes_7_11:
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		4,0
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_29'
	b_raise		2,1,3
	proceed
unify_new_keyes_7_7:
	suspend		unify_new_keyes_7_0
	module_entry		multiply_keyed_bag
	predicate		unify_new_keyes,4
unify_new_keyes_4_0:
	try_me_else		unify_new_keyes_4_1
	jump_on_non_list_var_var		1,unify_new_keyes_4_3,5,6
	wait_list_var_var		2,7,8
	collect_list		1
	collect_list		2
	b_vector_element		3,5,1,3
	get_value		7,1
	put_value		1,6
	put_value		2,8
	execute		4,unify_new_keyes_4_0
unify_new_keyes_4_3:
	check_nil		1,unify_new_keyes_4_1
	wait_nil		2
	get_value		3,4
	proceed
unify_new_keyes_4_1:
	suspend		unify_new_keyes_4_0
	module_entry		multiply_keyed_bag
	predicate		modify_indexes,8
modify_indexes_8_0:
	try_me_else		modify_indexes_8_1
	jump_on_non_list_var_var		1,modify_indexes_8_3,9,10
	put_marked_value		11,9
	put_variable		12,15
	b_set_vector_element		2,11,2,12,11
	b_vector_element		4,9,4,12
	b_vector_element		6,9,6,9
	put_func		13,3,get_all
	write_element_marked_value		13,1,4
	write_element_variable		13,2,16
	put_reused_list_val_var		14,1,13,1
	create_goal		8
	set_values_inc		1,10,2
	set_value		3,3
	set_value		4,12
	set_value		5,5
	set_value		6,9
	set_value		7,7
	set_marked_value		8,8
	enqueue_goal		8,modify_indexes_8_0
	create_goal		6
	set_value		1,16
	set_value		2,8
	set_value		3,1
	set_variable		4,5
	set_value		5,4
	set_value		6,6
	enqueue_goal		6,modify_index_6_0
	put_value		1,2
	put_values_dec		2,15,2
	put_value		4,5
	execute		4,get_index_stream_4_0
modify_indexes_8_3:
	check_nil		1,modify_indexes_8_1
	collect_value		8
	get_value		2,3
	get_value		4,5
	get_value		6,7
	proceed
modify_indexes_8_1:
	suspend		modify_indexes_8_0
	module_entry		multiply_keyed_bag
	predicate		modify_index,6
modify_index_6_0:
	try_me_else		modify_index_6_1
	list		1
	read_car		1,7
	try_me_else		modify_index_6_3
	integer		7
	read_cdr		1,8
	integer		2
	g_not_equal		7,2
	put_func		9,3,put
	write_element_marked_value		9,1,5
	write_element_value		9,2,7
	get_reused_list_val_var		3,1,1,9,7
	put_value		1,8
	put_value		3,7
	execute		6,modify_index_6_0
modify_index_6_3:
	read_cdr		1,8
	try_me_else		modify_index_6_1
	wait_value		2,7
	collect_value		7
	put_func		7,3,put
	write_element_value		7,1,6
	write_element_value		7,2,2
	get_reused_list_val_var		3,1,1,7,6
	put_value		1,8
	put_values_inc		2,5,2
	execute		4,return_ids_4_0
modify_index_6_1:
	suspend		modify_index_6_0
	module_entry		multiply_keyed_bag
	predicate		return_ids,4
return_ids_4_0:
	try_me_else		return_ids_4_1
	jump_on_non_list_var_var		1,return_ids_4_3,5,6
	put_func		7,3,put
	write_element_marked_value		7,1,2
	write_element_value		7,2,5
	get_reused_list_val_var		3,1,1,7,5
	put_value		1,6
	put_value		3,5
	execute		4,return_ids_4_0
return_ids_4_3:
	check_nil		1,return_ids_4_1
	collect_value		2
	get_value		3,4
	proceed
return_ids_4_1:
	suspend		return_ids_4_0
	module_entry		multiply_keyed_bag
	predicate		remake,9
remake_9_0:
	try_me_else		remake_9_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		10,1
	put_integer		11,0
	b_set_vector_element		6,10,6,11,10
	b_increment		1,1
	create_goal		9
	set_values_inc		1,1,2
	set_marked_value		3,3
	set_variable		4,12
	set_value		5,5
	set_value		6,10
	set_variable		7,11
	set_variable		8,10
	set_value		9,9
	enqueue_goal		9,remake_9_0
	put_values_inc		1,3,2
	put_value		3,12
	put_values_inc		4,6,2
	put_value		6,11
	put_value		7,8
	put_value		8,10
	execute		8,if_move_element_8_0
remake_9_1:
	try_me_else		remake_9_3
	wait_value		1,2
	collect_value		7
	collect_value		6
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		4,5
	get_value		8,9
	proceed
remake_9_3:
	suspend		remake_9_0
	module_entry		multiply_keyed_bag
	predicate		if_move_element,8
if_move_element_8_0:
	try_me_else		if_move_element_8_1
	jump_on_non_integer		4,if_move_element_8_3
	test_integer		4,0,if_move_element_8_1
	collect_value		1
	get_value		2,3
	get_value		6,5
	get_value		7,8
	proceed
if_move_element_8_3:
	is_vector		4,if_move_element_8_1
	g_vector		4,9
	put_value		9,5
	put_marked_value		5,9
	put_variable		11,10
	b_set_vector_element		7,5,5,11,7
	get_value		7,8
	b_increment		9,5
	get_value		6,5
	put_values_dec		5,10,2
	execute		6,add_to_indexes_6_0
if_move_element_8_1:
	suspend		if_move_element_8_0
	module_entry		multiply_keyed_bag
	predicate		clear_indexes,3
clear_indexes_3_0:
	try_me_else		clear_indexes_3_1
	jump_on_non_list_var_var		1,clear_indexes_3_3,4,5
	put_variable		6,7
	b_set_vector_element		2,4,2,6,4
	put_reused_list		6,1
	write_car_atom		6,clear
	write_cdr_variable		6,8
	create_goal		3
	set_values_dec		1,5,3
	enqueue_goal		3,clear_indexes_3_0
	put_value		1,2
	put_values_dec		2,7,2
	put_value		4,8
	execute		4,get_index_stream_4_0
clear_indexes_3_3:
	check_nil		1,clear_indexes_3_1
	get_value		2,3
	proceed
clear_indexes_3_1:
	suspend		clear_indexes_3_0
	module_entry		multiply_keyed_bag
	predicate		pack,6
pack_6_0:
	b_decrement		6,6
	create_goal		7
	set_marked_value		1,1
	set_variable		2,7
	set_values_inc		3,3,3
	set_integer		6,0
	set_value		7,6
	enqueue_goal		7,do_pack_7_0
	put_value		3,7
	execute		3,clear_indexes_3_0
pack_6_1:
	suspend		pack_6_0
	module_entry		multiply_keyed_bag
	predicate		do_pack,7
do_pack_7_0:
	try_me_else		do_pack_7_1
	integer		6
	integer		7
	try_me_else		do_pack_7_4
	g_less_than		6,7
	execute		7,find_space_7_0
do_pack_7_4:
	collect_value		1
	get_value		2,3
	get_value		4,5
	proceed
do_pack_7_1:
	suspend		do_pack_7_0
	module_entry		multiply_keyed_bag
	predicate		find_space,7
find_space_7_0:
	try_me_else		find_space_7_1
	vector		4
	integer		6
	g_vector_element		4,6,8
	wait_integer		8,0
	execute		7,find_element_7_0
find_space_7_1:
	otherwise		find_space_7_0
	b_increment		6,6
	execute		7,do_pack_7_0
find_space_7_7:
	suspend		find_space_7_0
	module_entry		multiply_keyed_bag
	predicate		find_element,7
find_element_7_0:
	try_me_else		find_element_7_1
	integer		6
	integer		7
	try_me_else		find_element_7_4
	g_less_than		6,7
	execute		7,do_find_element_7_0
find_element_7_4:
	collect_value		1
	get_value		2,3
	get_value		4,5
	proceed
find_element_7_1:
	suspend		find_element_7_0
	module_entry		multiply_keyed_bag
	predicate		do_find_element,7
do_find_element_7_0:
	try_me_else		do_find_element_7_1
	vector		4
	integer		7
	g_vector_element		4,7,8
	wait_integer		8,0
	b_decrement		7,7
	execute		7,find_element_7_0
do_find_element_7_1:
	otherwise		do_find_element_7_0
	put_marked_value		8,7
	put_integer		9,0
	b_set_vector_element		4,8,4,9,8
	put_marked_value		9,6
	put_variable		11,10
	b_set_vector_element		8,9,8,11,9
	b_increment		6,8
	b_decrement		7,7
	create_goal		7
	set_marked_value		1,1
	set_variable		2,11
	set_value		3,3
	set_value		4,9
	set_value		5,5
	set_values_dec		6,8,2
	enqueue_goal		7,do_pack_7_0
	put_value		3,11
	put_value		5,10
	execute		6,add_to_indexes_6_0
do_find_element_7_7:
	suspend		do_find_element_7_0
	module_entry		multiply_keyed_bag
	predicate		get_part,7
get_part_7_0:
	put_variable		8,10
	b_new_vector		8,8
	create_goal		6
	set_variable		1,9
	set_void		2
	set_value		3,3
	set_value		4,8
	set_value		5,4
	set_integer		6,0
	enqueue_goal		6,part_6_0
	put_values_dec		3,10,2
	execute		7,get_format_7_0
get_part_7_1:
	suspend		get_part_7_0
	module_entry		multiply_keyed_bag
	predicate		part,6
part_6_0:
	try_me_else		part_6_1
	jump_on_non_list_var_var		1,part_6_3,7,8
	put_marked_value		9,7
	put_integer		10,0
	b_set_vector_element		3,9,3,10,9
	put_marked_value		10,6
	b_set_vector_element		4,10,3,3,4
	get_reused_list_val_var		2,1,1,7,3
	b_increment		6,6
	put_value		1,8
	put_value		2,3
	put_value		3,9
	execute		6,part_6_0
part_6_3:
	check_nil		1,part_6_1
	collect_value		6
	collect_value		3
	get_nil		2
	get_value		4,5
	proceed
part_6_1:
	suspend		part_6_0
	module_entry		multiply_keyed_bag
	predicate		get_part_if_any,6
get_part_if_any_6_0:
	put_values_inc		8,4,2
	put_value		7,6
	create_goal		5
	set_variable		1,4
	set_values_inc		2,2,2
	set_marked_value		4,7
	set_variable		5,3
	enqueue_goal		5,do_get_part_if_any_5_0
	put_void		2
	put_values_inc		5,8,2
	execute		7,get_format_7_0
get_part_if_any_6_1:
	suspend		get_part_if_any_6_0
	module_entry		multiply_keyed_bag
	predicate		do_get_part_if_any,5
do_get_part_if_any_5_0:
	try_me_else		do_get_part_if_any_5_1
	vector		2
	test_arity		2,0,do_get_part_if_any_5_3
	collect_value		5
	collect_value		4
	collect_value		1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_part_if_any_5_3:
	integer		4
	put_value		6,2
	g_vector		6,7
	wait_value		7,4
	put_value		7,3
	b_new_vector		4,5
	put_void		2
	put_value		3,6
	put_value		5,7
	put_integer		6,0
	execute		6,part_6_0
do_get_part_if_any_5_1:
	suspend		do_get_part_if_any_5_0
	module_entry		multiply_keyed_bag
	predicate		get_part_all,6
get_part_all_6_0:
	put_values_inc		8,4,2
	put_value		7,6
	create_goal		4
	set_variable		1,4
	set_values_inc		2,2,2
	set_variable		4,3
	enqueue_goal		4,get_part_all_4_0
	put_void		2
	put_values_inc		5,8,2
	execute		7,get_format_7_0
get_part_all_6_1:
	suspend		get_part_all_6_0
	module_entry		multiply_keyed_bag
	predicate		get_part_all,4
get_part_all_4_0:
	try_me_else		get_part_all_4_1
	jump_on_non_list_var_var		2,get_part_all_4_3,5,6
	put_marked_value		7,4
	b_new_vector		7,7
	put_reused_list		2,2
	write_car_variable		2,8
	write_cdr_variable		2,9
	get_list_value		3,2
	create_goal		4
	set_variable		1,2
	set_value		2,6
	set_value		3,9
	set_value		4,4
	enqueue_goal		4,get_part_all_4_0
	put_value		3,5
	put_values_inc		4,7,2
	put_integer		6,0
	execute		6,part_6_0
get_part_all_4_3:
	check_nil		2,get_part_all_4_1
	collect_value		4
	collect_value		1
	get_nil		3
	proceed
get_part_all_4_1:
	suspend		get_part_all_4_0
	module_entry		multiply_keyed_bag
	predicate		get_part_and_put,9
get_part_and_put_9_0:
	put_marked_variable		10,11
	b_new_vector		10,10
	create_goal		4
	set_variable		1,12
	set_value		2,6
	set_value		3,11
	set_atom		4,getp_and_put
	enqueue_goal		4,unify_part_4_0
	create_goal		7
	set_variable		1,6
	set_values_inc		2,3,2
	set_value		4,10
	set_value		5,5
	set_value		6,12
	set_integer		7,0
	enqueue_goal		7,get_part_and_put1_7_0
	put_value		3,11
	put_values_inc		4,6,4
	execute		7,get_format_7_0
get_part_and_put_9_1:
	suspend		get_part_and_put_9_0
	module_entry		multiply_keyed_bag
	predicate		get_part_and_put1,7
get_part_and_put1_7_0:
	try_me_else		get_part_and_put1_7_1
	jump_on_non_list_var_var		1,get_part_and_put1_7_3,8,9
	put_variable		11,10
	b_set_vector_element		2,8,2,11,8
	put_marked_value		11,7
	b_set_vector_element		4,11,2,2,4
	get_reused_list_val_var		6,1,1,10,10
	b_increment		7,7
	put_values_dec		1,9,2
	put_value		6,10
	execute		7,get_part_and_put1_7_0
get_part_and_put1_7_3:
	check_nil		1,get_part_and_put1_7_1
	collect_value		7
	get_value		2,3
	get_value		4,5
	get_nil		6
	proceed
get_part_and_put1_7_1:
	suspend		get_part_and_put1_7_0
	module_entry		multiply_keyed_bag
	predicate		unify_part,4
unify_part_4_0:
	try_me_else		unify_part_4_1
	vector		2
	integer		3
	g_vector		2,5
	wait_value		5,3
	collect_value		4
	put_integer		3,0
	execute		3,do_unify_part_3_0
unify_part_4_1:
	otherwise		unify_part_4_0
	try_me_else		unify_part_4_7
	atom		4
	branch_on_atom		4,2,unify_part_4_7
	bucket_entry_a		getp_and_put,unify_part_4_9
	bucket_entry_a		getp_and_put_if_any,unify_part_4_10
unify_part_4_9:
	collect_value		3
	collect_value		1
	put_integer		3,1024
	put_structured_constant		1,'$SCNST_30'
	b_raise		3,1,2
	proceed
unify_part_4_10:
	collect_value		3
	collect_value		1
	put_integer		3,1024
	put_structured_constant		1,'$SCNST_31'
	b_raise		3,1,2
	proceed
unify_part_4_7:
	suspend		unify_part_4_0
	module_entry		multiply_keyed_bag
	predicate		do_unify_part,3
do_unify_part_3_0:
	try_me_else		do_unify_part_3_1
	jump_on_non_list_var_var		1,do_unify_part_3_3,4,5
	collect_list		1
	put_marked_value		1,3
	put_integer		6,0
	b_set_vector_element		2,1,1,6,2
	get_value		1,4
	b_increment		3,3
	put_value		1,5
	execute		3,do_unify_part_3_0
do_unify_part_3_3:
	check_nil		1,do_unify_part_3_1
	collect_value		3
	collect_value		2
	proceed
do_unify_part_3_1:
	suspend		do_unify_part_3_0
	module_entry		multiply_keyed_bag
	predicate		get_part_and_put_if_any,9
get_part_and_put_if_any_9_0:
	create_goal		8
	set_variable		1,10
	set_values_inc		2,2,5
	set_marked_value		7,9
	set_variable		8,3
	enqueue_goal		8,get_part_and_put_if_any1_8_0
	put_void		2
	put_value		4,10
	put_values_inc		5,7,3
	execute		7,get_format_7_0
get_part_and_put_if_any_9_1:
	suspend		get_part_and_put_if_any_9_0
	module_entry		multiply_keyed_bag
	predicate		get_part_and_put_if_any1,8
get_part_and_put_if_any1_8_0:
	try_me_else		get_part_and_put_if_any1_8_1
	vector		2
	test_arity		2,0,get_part_and_put_if_any1_8_3
	collect_value		8
	collect_value		7
	collect_value		3
	collect_value		1
	put_vector		1,0
	get_vector_value		4,1
	get_value		5,6
	proceed
get_part_and_put_if_any1_8_3:
	integer		7
	g_vector		2,9
	wait_value		9,7
	put_value		7,4
	put_marked_value		4,8
	b_new_vector		4,4
	put_vector		9,0
	get_vector_value		6,9
	create_goal		4
	set_variable		1,6
	set_value		2,5
	set_value		3,8
	set_atom		4,getp_and_put_if_any
	enqueue_goal		4,unify_part_4_0
	put_value		5,7
	put_integer		7,0
	execute		7,get_part_and_put1_7_0
get_part_and_put_if_any1_8_1:
	suspend		get_part_and_put_if_any1_8_0
	module_entry		multiply_keyed_bag
	predicate		get_format,7
get_format_7_0:
	try_me_else		get_format_7_1
	vector		1
	g_vector		1,8
	put_integer		9,0
	g_less_than		9,8
	put_marked_value		3,3
	get_value		3,8
	put_integer		8,0
	execute		8,get_format_8_0
get_format_7_1:
	otherwise		get_format_7_0
	collect_value		7
	put_marked_value		1,1
	get_value		1,2
	get_integer		3,0
	get_nil		4
	get_value		5,6
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_32'
	b_raise		3,2,1
	proceed
get_format_7_5:
	suspend		get_format_7_0
	module_entry		multiply_keyed_bag
	predicate		get_format,8
get_format_8_0:
	try_me_else		get_format_8_1
	integer		3
	integer		8
	g_less_than		8,3
	put_marked_value		10,8
	put_marked_variable		11,9
	b_set_vector_element		1,10,10,11,1
	get_value		10,9
	b_increment		8,8
	create_goal		8
	set_values_inc		1,1,3
	set_variable		4,3
	set_variable		5,10
	set_value		6,6
	set_marked_value		7,7
	set_value		8,8
	enqueue_goal		8,get_format_8_0
	put_value		1,9
	put_value		2,4
	put_value		4,7
	put_value		6,10
	execute		6,if_correct_6_0
get_format_8_1:
	try_me_else		get_format_8_3
	wait_value		3,8
	collect_value		3
	collect_value		7
	collect_value		8
	get_value		1,2
	get_nil		4
	get_value		5,6
	proceed
get_format_8_3:
	suspend		get_format_8_0
	module_entry		multiply_keyed_bag
	predicate		if_correct,6
if_correct_6_0:
	try_me_else		if_correct_6_1
	jump_on_non_atom		1,if_correct_6_3
	collect_value		4
	put_func		4,3,carbon_copy
	write_element_marked_value		4,1,1
	write_element_variable		4,2,7
	put_list_val_val		8,4,6
	get_list_value		5,8
	put_value		4,7
	execute		4,if_if_correct_4_0
if_correct_6_3:
	is_integer		1,if_correct_6_1
	put_integer		7,0
	g_not_less_than		1,7
	integer		4
	g_less_than		1,4
	get_value		5,6
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
if_correct_6_1:
	otherwise		if_correct_6_0
	collect_value		4
	collect_value		3
	collect_value		2
	get_value		5,6
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_33'
	b_raise		3,2,1
	proceed
if_correct_6_7:
	suspend		if_correct_6_0
	module_entry		multiply_keyed_bag
	predicate		if_if_correct,4
if_if_correct_4_0:
	try_me_else		if_if_correct_4_1
	jump_on_non_list_var_var		4,if_if_correct_4_3,5,6
	wait_nil		6
	collect_value		1
	put_reused_list_val_val		1,4,5,3
	get_list_value		2,1
	proceed
if_if_correct_4_3:
	check_nil		4,if_if_correct_4_1
	get_value		2,3
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_34'
	b_raise		3,2,1
	proceed
if_if_correct_4_1:
	suspend		if_if_correct_4_0
	begin_const_section		multiply_keyed_bag
'$SCNST_0_1':
	define_desc		3,7
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1953066601
	define_integer		1769234793
	define_integer		1885302383
	define_integer		1835102817
	define_integer		1919251557
'$SCNST_0_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_0_1'
'$SCNST_1':
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_2_1':
	define_desc		11,5
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		7627117
'$SCNST_2_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		19,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1920234593
	define_integer		1953849961
	define_integer		1634623333
	define_integer		25965
'$SCNST_3_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_3_1'
'$SCNST_34':
'$SCNST_33':
'$SCNST_26':
'$SCNST_19':
'$SCNST_17':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		27,8
	define_integer		1651863396
	define_integer		1683978604
	define_integer		1852401253
	define_integer		1633641573
	define_integer		1769108596
	define_integer		1702131042
	define_integer		1835101791
	define_integer		101
'$SCNST_4_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		19,5
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1701080681
	define_integer		2037669752
	define_integer		25968
'$SCNST_5_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		19,12
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1953066601
	define_integer		1769234793
	define_integer		1885302383
	define_integer		1835102817
	define_integer		1919251557
	define_integer		1919903327
	define_integer		1685221215
	define_integer		1684370021
	define_integer		1684957535
	define_integer		30821
'$SCNST_6_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_6_1'
'$SCNST_7':
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_8_1':
	define_desc		27,12
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1953066601
	define_integer		1769234793
	define_integer		1885302383
	define_integer		1835102817
	define_integer		1919251557
	define_integer		1919903327
	define_integer		1935763551
	define_integer		1600415080
	define_integer		1701080681
	define_integer		120
'$SCNST_8_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_8_1'
'$SCNST_9':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_10_1':
	define_desc		27,11
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1953066601
	define_integer		1769234793
	define_integer		1885302383
	define_integer		1835102817
	define_integer		1919251557
	define_integer		1919903327
	define_integer		1601138271
	define_integer		1701080681
	define_integer		120
'$SCNST_10_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_10_1'
'$SCNST_11':
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_12_1':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_12_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_12_1'
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		27,11
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1730178665
	define_integer		1767863397
	define_integer		1851875174
	define_integer		1851875193
	define_integer		1970298724
	define_integer		116
'$SCNST_13_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_13_1'
'$SCNST_29':
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		19,7
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1881173609
	define_integer		29813
'$SCNST_14_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_1':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_15_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_15_1'
'$SCNST_24':
'$SCNST_23':
'$SCNST_16':
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_18_0':
	define_desc		0,2
	define_atom		none
	define_atom		ascending
'$SCNST_22':
'$SCNST_21':
'$SCNST_20':
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_25_1':
	define_desc		27,5
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1684959075
	define_integer		1869182057
	define_integer		110
'$SCNST_25_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_25_1'
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_27_1':
	define_desc		19,9
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1730178665
	define_integer		1633645669
	define_integer		1885299822
	define_integer		29813
'$SCNST_27_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_27_1'
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_28_1':
	define_desc		27,11
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1730178665
	define_integer		1633645669
	define_integer		1885299822
	define_integer		1767863413
	define_integer		1851875174
	define_integer		121
'$SCNST_28_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_28_1'
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_30_1':
	define_desc		11,9
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1730178665
	define_integer		1601205349
	define_integer		1600417377
	define_integer		7632240
'$SCNST_30_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_30_1'
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_31_1':
	define_desc		19,11
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1919903327
	define_integer		544498029
	define_integer		1730178665
	define_integer		1601205349
	define_integer		1600417377
	define_integer		1601467760
	define_integer		1633642089
	define_integer		31086
'$SCNST_31_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_31_1'
'$SCNST_31':
	define_vector		'$SCNST_31_0'
'$SCNST_32_1':
	define_desc		3,9
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1836216166
	define_integer		1717531745
	define_integer		1885303407
	define_integer		1769239137
	define_integer		1918856289
	define_integer		1919247973
	define_integer		1701015141
'$SCNST_32_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		multiply_keyed_bag
	define_string		'$SCNST_32_1'
'$SCNST_32':
	define_vector		'$SCNST_32_0'
