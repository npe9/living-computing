keyed_sorted_bag:
	module		keyed_sorted_bag
	entry		keyed_sorted_bag,2,keyed_sorted_bag_2_0
	entry		keyed_sorted_set,2,keyed_sorted_set_2_0
	entry		sorted_bag,2,sorted_bag_2_0
	module_entry		keyed_sorted_bag
	predicate		keyed_sorted_bag,2
keyed_sorted_bag_2_0:
	b_merge		4,3
	get_value		4,2
	put_value		2,3
	put_vector		3,0
	execute		3,keyed_sorted_bag_3_0
keyed_sorted_bag_2_1:
	suspend		keyed_sorted_bag_2_0
	module_entry		keyed_sorted_bag
	predicate		keyed_sorted_bag,3
keyed_sorted_bag_3_0:
	try_me_else		keyed_sorted_bag_3_1
	jump_on_non_list		2,keyed_sorted_bag_3_3
	read_car		2,4
	jump_on_non_atom		4,keyed_sorted_bag_3_5
	test_atom		4,clear,keyed_sorted_bag_3_1
	read_cdr		2,5
	collect_list		2
	collect_value		3
	put_value		2,5
	put_vector		3,0
	execute		3,keyed_sorted_bag_3_0
keyed_sorted_bag_3_5:
	is_vector		4,keyed_sorted_bag_3_1
	jump_on_arity		4,6,keyed_sorted_bag_3_1
	table_entry		keyed_sorted_bag_3_1
	table_entry		keyed_sorted_bag_3_1
	table_entry		keyed_sorted_bag_3_6
	table_entry		keyed_sorted_bag_3_7
	table_entry		keyed_sorted_bag_3_8
	table_entry		keyed_sorted_bag_3_9
keyed_sorted_bag_3_6:
	read_element		4,0,5
	atom		5
	hash_on_atom		5,10,keyed_sorted_bag_3_1
	bucket_entry_a		carbon_copy,keyed_sorted_bag_3_11
	bucket_entry_a		count,keyed_sorted_bag_3_12
	bucket_entry_a		data_count,keyed_sorted_bag_3_13
	bucket_entry_a		depth,keyed_sorted_bag_3_14
	bucket_entry_a		do,keyed_sorted_bag_3_15
	bucket_entry_a		empty,keyed_sorted_bag_3_16
	bucket_entry_a		get_all,keyed_sorted_bag_3_17
	bucket_entry_a		get_max_if_any,keyed_sorted_bag_3_18
	bucket_entry_a		get_min_if_any,keyed_sorted_bag_3_19
	bucket_entry_a		possessory_rate,keyed_sorted_bag_3_20
keyed_sorted_bag_3_11:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		5,1
	create_goal		3
	set_marked_value		1,5
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		5,carbon_copy_5_0
keyed_sorted_bag_3_12:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,count_3_0
keyed_sorted_bag_3_13:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,data_count_3_0
keyed_sorted_bag_3_14:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,depth_3_0
keyed_sorted_bag_3_15:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	b_merge		4,2
	get_value		4,7
	create_goal		3
	set_value		1,1
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,2
	put_value		2,6
	put_value		3,4
	execute		3,prepend_3_0
keyed_sorted_bag_3_16:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,empty_3_0
keyed_sorted_bag_3_17:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	put_vector		1,0
	set_value		3,1
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		4,get_all_4_0
keyed_sorted_bag_3_18:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_max_if_any_4_0
keyed_sorted_bag_3_19:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_min_if_any_4_0
keyed_sorted_bag_3_20:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,possessory_rate_3_0
keyed_sorted_bag_3_7:
	read_element		4,0,5
	atom		5
	hash_on_atom		5,6,keyed_sorted_bag_3_1
	bucket_entry_a		carbon_copy,keyed_sorted_bag_3_22
	bucket_entry_a		empty,keyed_sorted_bag_3_23
	bucket_entry_a		get,keyed_sorted_bag_3_24
	bucket_entry_a		get_all,keyed_sorted_bag_3_25
	bucket_entry_a		get_if_any,keyed_sorted_bag_3_26
	bucket_entry_a		put,keyed_sorted_bag_3_27
keyed_sorted_bag_3_22:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,carbon_copy_with_key_5_0
keyed_sorted_bag_3_23:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,empty_5_0
keyed_sorted_bag_3_24:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,get_5_0
keyed_sorted_bag_3_25:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,get_all_with_key_5_0
keyed_sorted_bag_3_26:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,get_if_any_5_0
keyed_sorted_bag_3_27:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,put_5_0
keyed_sorted_bag_3_8:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,keyed_sorted_bag_3_1
	bucket_entry_a		get_and_put,keyed_sorted_bag_3_29
	bucket_entry_a		get_if_any_and_put,keyed_sorted_bag_3_30
keyed_sorted_bag_3_29:
	read_cdr		2,6
	read_elements_inc		4,1,7,3
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,6
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,3
	execute		6,get_and_put_6_0
keyed_sorted_bag_3_30:
	read_cdr		2,6
	read_elements_inc		4,1,7,3
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,6
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,7,3
	execute		6,get_if_any_and_put_6_0
keyed_sorted_bag_3_9:
	read_cdr		2,5
	read_element		4,0,6
	wait_atom		6,get_and_put_if_any
	read_elements_inc		4,1,6,4
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,5
	set_variable		3,10
	enqueue_goal		3,keyed_sorted_bag_3_0
	put_value		2,3
	put_values_inc		3,6,5
	execute		7,get_and_put_if_any_7_0
keyed_sorted_bag_3_3:
	check_nil		2,keyed_sorted_bag_3_1
	collect_value		3
	collect_value		1
	proceed
keyed_sorted_bag_3_1:
	otherwise		keyed_sorted_bag_3_0
	try_me_else		keyed_sorted_bag_3_45
	wait_list_var_var		2,4,5
	collect_list		2
	collect_value		3
	collect_value		5
	collect_value		1
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_0'
	b_raise		2,1,4
	proceed
keyed_sorted_bag_3_45:
	suspend		keyed_sorted_bag_3_0
	module_entry		keyed_sorted_bag
	predicate		prepend,3
prepend_3_0:
	try_me_else		prepend_3_1
	jump_on_non_list_var_var		1,prepend_3_3,4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		3,4
	execute		3,prepend_3_0
prepend_3_3:
	check_nil		1,prepend_3_1
	get_value		2,3
	proceed
prepend_3_1:
	suspend		prepend_3_0
	module_entry		keyed_sorted_bag
	predicate		empty,3
empty_3_0:
	try_me_else		empty_3_1
	wait_vector		1,0
	get_atom		2,yes
	put_vector		1,0
	get_vector_value		3,1
	proceed
empty_3_1:
	otherwise		empty_3_0
	get_atom		2,no
	get_value		1,3
	proceed
empty_3_6:
	suspend		empty_3_0
	module_entry		keyed_sorted_bag
	predicate		empty,5
empty_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,empty_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
empty_5_1:
	suspend		empty_5_0
	module_entry		keyed_sorted_bag
	predicate		empty,2
empty_2_0:
	try_me_else		empty_2_1
	vector		1
	jump_on_arity		1,7,empty_2_1
	table_entry		empty_2_1
	table_entry		empty_2_3
	table_entry		empty_2_4
	table_entry		empty_2_1
	table_entry		empty_2_5
	table_entry		empty_2_1
	table_entry		empty_2_6
empty_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	get_atom		2,yes
	proceed
empty_2_4:
	read_elements_inc		1,0,3,2
	collect_vector		1
	get_atom		2,no
	get_value		3,4
	proceed
empty_2_5:
	read_elements_inc		1,0,3,4
	collect_vector		1
	get_atom		2,no
	put_values_inc		1,3,4
	execute		4,splay_4_0
empty_2_6:
	read_elements_inc		1,0,3,6
	collect_vector		1
	get_atom		2,no
	put_values_inc		1,3,6
	execute		6,splay_6_0
empty_2_1:
	suspend		empty_2_0
	module_entry		keyed_sorted_bag
	predicate		put,5
put_5_0:
	put_value		6,1
	create_goal		3
	set_variable		1,7
	set_variable		2,8
	set_value		3,4
	enqueue_goal		3,put_3_0
	put_value		1,2
	put_value		2,5
	put_values_dec		4,8,2
	execute		6,down_6_0
put_5_1:
	suspend		put_5_0
	module_entry		keyed_sorted_bag
	predicate		put,3
put_3_0:
	try_me_else		put_3_1
	vector		1
	jump_on_arity		1,5,put_3_1
	table_entry		put_3_1
	table_entry		put_3_1
	table_entry		put_3_3
	table_entry		put_3_1
	table_entry		put_3_4
put_3_3:
	read_elements_inc		1,0,4,2
	collect_vector		1
	get_value		4,2
	put_list_val_var		1,3,2
	put_vector		3,5
	write_element_integer		3,0,1
	write_elements_inc		3,1,1,2
	write_element_variable		3,3,1
	write_element_value		3,4,1
	get_vector_value		5,3
	proceed
put_3_4:
	read_elements_inc		1,0,4,2
	read_element		1,2,12
	read_element		1,3,6
	wait_vector		12,5
	read_elements_inc		12,0,7,5
	collect_vector		1
	get_value		5,4
	get_list_val_var		9,1,3,3
	get_list_val_var		11,1,2,2
	b_increment		7,1
	put_reused_vector		4,12
	write_element_value		4,0,1
	write_element_value		4,1,8
	write_element_value		4,2,3
	write_element_value		4,3,10
	write_element_value		4,4,2
	get_vector_value		6,4
	proceed
put_3_1:
	suspend		put_3_0
	module_entry		keyed_sorted_bag
	predicate		get,5
get_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,get_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
get_5_1:
	suspend		get_5_0
	module_entry		keyed_sorted_bag
	predicate		get,2
get_2_0:
	try_me_else		get_2_1
	vector		1
	jump_on_arity		1,7,get_2_1
	table_entry		get_2_1
	table_entry		get_2_3
	table_entry		get_2_4
	table_entry		get_2_1
	table_entry		get_2_5
	table_entry		get_2_1
	table_entry		get_2_6
get_2_3:
	read_element		1,0,3
	collect_vector		1
	put_integer		5,1024
	put_structured_constant		1,'$SCNST_1'
	put_func		4,3,get
	write_elements_dec		4,1,3,2
	b_raise		5,1,4
	proceed
get_2_4:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,5
	read_element		5,0,6
	integer		6
	test_integer		6,1,get_2_10
	try_me_else		get_2_10
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_element		5,1,15
	read_elements_inc		5,2,10,3
	wait_list_var_var		15,13,14
	collect_list		15
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		14
	collect_value		4
	collect_vector		1
	collect_vector		3
	collect_vector		5
	get_value		2,13
	put_values_inc		1,8,2
	put_value		3,7
	execute		3,join_3_0
get_2_10:
	try_me_else		get_2_1
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_element		5,1,15
	read_elements_inc		5,2,10,3
	wait_list_var_var		15,13,14
	put_integer		16,1
	g_less_than		16,6
	collect_value		4
	collect_vector		1
	get_value		2,13
	put_reused_list		1,15
	write_car_variable		1,13
	write_cdr_variable		1,4
	get_list_value		11,1
	b_decrement		6,1
	put_reused_vector		2,5
	write_element_value		2,0,1
	write_element_value		2,1,14
	write_element_value		2,2,10
	write_element_value		2,3,4
	write_element_value		2,4,12
	put_reused_vector		1,3
	write_element_value		1,0,13
	write_element_value		1,1,2
	write_elements_inc		1,2,8,2
	get_vector_value		7,1
	proceed
get_2_5:
	read_elements_inc		1,0,3,2
	wait_vector		4,4
	read_elements_inc		4,0,5,2
	wait_vector		6,5
	read_element		6,0,7
	integer		7
	test_integer		7,1,get_2_14
	try_me_else		get_2_14
	read_elements_inc		1,2,8,2
	read_elements_inc		4,2,10,2
	read_element		6,1,17
	read_elements_inc		6,2,12,3
	wait_list_var_var		17,15,16
	collect_list		17
	collect_value		14
	collect_value		13
	collect_value		12
	collect_value		16
	collect_value		5
	collect_vector		1
	collect_vector		4
	collect_vector		6
	get_value		2,15
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_values_inc		3,8,2
	enqueue_goal		4,stay_4_0
	put_values_inc		1,10,2
	execute		3,join_3_0
get_2_14:
	try_me_else		get_2_1
	read_elements_inc		1,2,8,2
	read_elements_inc		4,2,10,2
	read_element		6,1,17
	read_elements_inc		6,2,12,3
	wait_list_var_var		17,15,16
	put_integer		18,1
	g_less_than		18,7
	collect_value		5
	collect_vector		4
	get_value		2,15
	put_reused_list		2,17
	write_car_variable		2,15
	write_cdr_variable		2,5
	get_list_value		13,2
	b_decrement		7,2
	put_reused_vector		4,6
	write_element_value		4,0,2
	write_element_value		4,1,16
	write_element_value		4,2,12
	write_element_value		4,3,5
	write_element_value		4,4,14
	put_reused_vector		2,1
	write_element_value		2,0,15
	write_element_value		2,1,4
	write_elements_inc		2,2,10,2
	put_value		1,3
	put_values_inc		3,8,2
	execute		4,splay_4_0
get_2_6:
	read_elements_inc		1,0,3,3
	wait_vector		5,4
	read_elements_inc		5,0,6,2
	wait_vector		7,5
	read_element		7,0,8
	integer		8
	test_integer		8,1,get_2_18
	try_me_else		get_2_18
	read_elements_inc		1,3,9,3
	read_elements_inc		5,2,12,2
	read_element		7,1,19
	read_elements_inc		7,2,14,3
	wait_list_var_var		19,17,18
	collect_list		19
	collect_value		16
	collect_value		15
	collect_value		14
	collect_value		18
	collect_value		6
	collect_vector		1
	collect_vector		5
	collect_vector		7
	get_value		2,17
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,3
	set_values_inc		4,9,3
	enqueue_goal		6,splay0_6_0
	put_values_inc		1,12,2
	execute		3,join_3_0
get_2_18:
	try_me_else		get_2_1
	read_elements_inc		1,3,9,3
	read_elements_inc		5,2,12,2
	read_element		7,1,19
	read_elements_inc		7,2,14,3
	wait_list_var_var		19,17,18
	put_integer		20,1
	g_less_than		20,8
	collect_value		6
	collect_vector		1
	get_value		2,17
	put_reused_list		1,19
	write_car_variable		1,17
	write_cdr_variable		1,6
	get_list_value		15,1
	b_decrement		8,1
	put_reused_vector		2,7
	write_element_value		2,0,1
	write_element_value		2,1,18
	write_element_value		2,2,14
	write_element_value		2,3,6
	write_element_value		2,4,16
	put_reused_vector		5,5
	write_element_value		5,0,17
	write_element_value		5,1,2
	write_elements_inc		5,2,12,2
	put_values_inc		1,3,3
	put_values_inc		4,9,3
	execute		6,splay_6_0
get_2_1:
	suspend		get_2_0
	module_entry		keyed_sorted_bag
	predicate		get_all,4
get_all_4_0:
	try_me_else		get_all_4_1
	jump_on_non_atom		4,get_all_4_3
	branch_on_atom		4,2,get_all_4_1
	bucket_entry_a		ascending,get_all_4_4
	bucket_entry_a		descending,get_all_4_5
get_all_4_4:
	execute		3,get_all_3_0
get_all_4_5:
	execute		3,get_all_descending_3_0
get_all_4_3:
	check_vector		4,3,get_all_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	execute		3,get_all_3_0
get_all_4_1:
	suspend		get_all_4_0
	module_entry		keyed_sorted_bag
	predicate		get_all,3
get_all_3_0:
	try_me_else		get_all_3_1
	vector		1
	jump_on_arity		1,5,get_all_3_1
	table_entry		get_all_3_3
	table_entry		get_all_3_1
	table_entry		get_all_3_1
	table_entry		get_all_3_1
	table_entry		get_all_3_4
get_all_3_3:
	get_value		2,3
	proceed
get_all_3_4:
	read_element		1,0,4
	read_element		1,1,13
	read_elements_inc		1,2,5,2
	wait_vector		13,5
	read_element		13,0,7
	read_element		13,1,14
	read_elements_inc		13,2,8,3
	wait_list_var_var		14,11,12
	collect_value		7
	collect_vector		1
	collect_vector		13
	get_nil		8
	get_nil		10
	create_goal		3
	set_value		1,6
	set_variable		2,1
	set_value		3,3
	enqueue_goal		3,get_all_3_0
	create_goal		4
	set_value		1,9
	set_value		2,12
	set_variable		3,6
	set_value		4,1
	enqueue_goal		4,get_elements_4_0
	put_vector		1,2
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_reused_list_val_val		3,14,1,6
	put_value		1,5
	execute		3,get_all_3_0
get_all_3_1:
	suspend		get_all_3_0
	module_entry		keyed_sorted_bag
	predicate		get_all_descending,3
get_all_descending_3_0:
	try_me_else		get_all_descending_3_1
	vector		1
	jump_on_arity		1,5,get_all_descending_3_1
	table_entry		get_all_descending_3_3
	table_entry		get_all_descending_3_1
	table_entry		get_all_descending_3_1
	table_entry		get_all_descending_3_1
	table_entry		get_all_descending_3_4
get_all_descending_3_3:
	get_value		2,3
	proceed
get_all_descending_3_4:
	read_element		1,0,4
	read_element		1,1,13
	read_elements_inc		1,2,5,2
	wait_vector		13,5
	read_element		13,0,7
	read_element		13,1,14
	read_elements_inc		13,2,8,3
	wait_list_var_var		14,11,12
	collect_value		7
	collect_vector		1
	collect_vector		13
	get_nil		8
	get_nil		10
	create_goal		3
	set_value		1,5
	set_variable		2,1
	set_value		3,3
	enqueue_goal		3,get_all_descending_3_0
	create_goal		4
	set_value		1,9
	set_value		2,12
	set_variable		3,5
	set_value		4,1
	enqueue_goal		4,get_elements_4_0
	put_vector		1,2
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_reused_list_val_val		3,14,1,5
	put_value		1,6
	execute		3,get_all_descending_3_0
get_all_descending_3_1:
	suspend		get_all_descending_3_0
	module_entry		keyed_sorted_bag
	predicate		get_elements,4
get_elements_4_0:
	try_me_else		get_elements_4_1
	jump_on_non_list_var_var		1,get_elements_4_3,5,6
	wait_list_var_var		2,7,8
	collect_list		2
	put_vector		2,2
	write_element_value		2,0,5
	write_element_value		2,1,7
	get_reused_list_val_var		3,1,1,2,5
	put_value		1,6
	put_value		2,8
	put_value		3,5
	execute		4,get_elements_4_0
get_elements_4_3:
	check_nil		1,get_elements_4_1
	wait_nil		2
	get_value		3,4
	proceed
get_elements_4_1:
	suspend		get_elements_4_0
	module_entry		keyed_sorted_bag
	predicate		get_all_with_key,5
get_all_with_key_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,get_all_with_key_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
get_all_with_key_5_1:
	suspend		get_all_with_key_5_0
	module_entry		keyed_sorted_bag
	predicate		get_all_with_key,2
get_all_with_key_2_0:
	try_me_else		get_all_with_key_2_1
	vector		1
	jump_on_arity		1,7,get_all_with_key_2_1
	table_entry		get_all_with_key_2_1
	table_entry		get_all_with_key_2_3
	table_entry		get_all_with_key_2_4
	table_entry		get_all_with_key_2_1
	table_entry		get_all_with_key_2_5
	table_entry		get_all_with_key_2_1
	table_entry		get_all_with_key_2_6
get_all_with_key_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	get_nil		2
	proceed
get_all_with_key_2_4:
	read_element		1,0,12
	read_element		1,1,3
	wait_vector		12,4
	read_element		12,0,4
	read_element		12,1,13
	read_elements_inc		12,2,5,2
	wait_vector		13,5
	read_elements_inc		13,0,7,5
	collect_value		11
	collect_value		10
	collect_value		7
	collect_value		4
	collect_vector		1
	collect_vector		12
	collect_vector		13
	get_nil		9
	get_value		2,8
	put_values_inc		1,5,2
	execute		3,join_3_0
get_all_with_key_2_5:
	read_element		1,0,3
	read_element		1,1,14
	read_elements_inc		1,2,4,2
	wait_vector		14,4
	read_element		14,0,6
	read_element		14,1,15
	read_elements_inc		14,2,7,2
	wait_vector		15,5
	read_elements_inc		15,0,9,5
	collect_value		13
	collect_value		12
	collect_value		9
	collect_value		6
	collect_vector		1
	collect_vector		14
	collect_vector		15
	get_nil		11
	get_value		2,10
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_values_inc		3,4,2
	enqueue_goal		4,stay_4_0
	put_values_inc		1,7,2
	execute		3,join_3_0
get_all_with_key_2_6:
	read_elements_inc		1,0,3,2
	read_element		1,2,16
	read_elements_inc		1,3,5,3
	wait_vector		16,4
	read_element		16,0,8
	read_element		16,1,17
	read_elements_inc		16,2,9,2
	wait_vector		17,5
	read_elements_inc		17,0,11,5
	collect_value		15
	collect_value		14
	collect_value		11
	collect_value		8
	collect_vector		1
	collect_vector		16
	collect_vector		17
	get_nil		13
	get_value		2,12
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,3
	set_values_inc		4,5,3
	enqueue_goal		6,splay0_6_0
	put_values_inc		1,9,2
	execute		3,join_3_0
get_all_with_key_2_1:
	suspend		get_all_with_key_2_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put,6
get_and_put_6_0:
	put_value		9,1
	create_goal		4
	set_variable		1,7
	set_variable		2,8
	set_values_inc		3,4,2
	enqueue_goal		4,get_and_put_4_0
	put_value		1,2
	put_value		2,6
	put_values_dec		4,8,2
	put_value		6,9
	execute		6,down_6_0
get_and_put_6_1:
	suspend		get_and_put_6_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put,4
get_and_put_4_0:
	try_me_else		get_and_put_4_1
	vector		1
	jump_on_arity		1,5,get_and_put_4_1
	table_entry		get_and_put_4_1
	table_entry		get_and_put_4_1
	table_entry		get_and_put_4_3
	table_entry		get_and_put_4_1
	table_entry		get_and_put_4_4
get_and_put_4_3:
	read_elements_inc		1,0,5,2
	collect_value		6
	collect_value		5
	collect_vector		1
	put_integer		6,1024
	put_structured_constant		1,'$SCNST_2'
	put_func		5,4,get_and_put
	write_elements_inc		5,1,2,3
	b_raise		6,1,5
	proceed
get_and_put_4_4:
	read_elements_inc		1,0,5,2
	read_element		1,2,14
	read_element		1,3,7
	wait_vector		14,5
	read_element		14,0,8
	read_element		14,1,15
	read_elements_inc		14,2,9,3
	wait_list_var_var		15,12,13
	collect_value		5
	collect_vector		1
	get_value		6,2
	get_value		3,12
	put_reused_list_val_val		1,15,4,13
	put_reused_vector		2,14
	write_element_value		2,0,8
	write_element_value		2,1,1
	write_elements_inc		2,2,9,3
	get_vector_value		7,2
	proceed
get_and_put_4_1:
	suspend		get_and_put_4_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any,5
get_if_any_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,get_if_any_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
get_if_any_5_1:
	suspend		get_if_any_5_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any,2
get_if_any_2_0:
	try_me_else		get_if_any_2_1
	vector		1
	jump_on_arity		1,7,get_if_any_2_1
	table_entry		get_if_any_2_1
	table_entry		get_if_any_2_3
	table_entry		get_if_any_2_4
	table_entry		get_if_any_2_1
	table_entry		get_if_any_2_5
	table_entry		get_if_any_2_1
	table_entry		get_if_any_2_6
get_if_any_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	put_vector		1,0
	get_vector_value		2,1
	proceed
get_if_any_2_4:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,5
	read_element		5,0,6
	integer		6
	test_integer		6,1,get_if_any_2_10
	try_me_else		get_if_any_2_10
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_element		5,1,15
	read_elements_inc		5,2,10,3
	wait_list_var_var		15,13,14
	collect_list		15
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		14
	collect_value		4
	collect_vector		1
	collect_vector		3
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,13
	get_vector_value		2,1
	put_values_inc		1,8,2
	put_value		3,7
	execute		3,join_3_0
get_if_any_2_10:
	try_me_else		get_if_any_2_1
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_element		5,1,15
	read_elements_inc		5,2,10,3
	wait_list_var_var		15,13,14
	put_integer		16,1
	g_less_than		16,6
	collect_value		4
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,13
	get_vector_value		2,1
	put_reused_list		1,15
	write_car_variable		1,13
	write_cdr_variable		1,4
	get_list_value		11,1
	b_decrement		6,1
	put_reused_vector		2,5
	write_element_value		2,0,1
	write_element_value		2,1,14
	write_element_value		2,2,10
	write_element_value		2,3,4
	write_element_value		2,4,12
	put_reused_vector		1,3
	write_element_value		1,0,13
	write_element_value		1,1,2
	write_elements_inc		1,2,8,2
	get_vector_value		7,1
	proceed
get_if_any_2_5:
	read_elements_inc		1,0,3,2
	wait_vector		4,4
	read_elements_inc		4,0,5,2
	wait_vector		6,5
	read_element		6,0,7
	integer		7
	test_integer		7,1,get_if_any_2_14
	try_me_else		get_if_any_2_14
	read_elements_inc		1,2,8,2
	read_elements_inc		4,2,10,2
	read_element		6,1,17
	read_elements_inc		6,2,12,3
	wait_list_var_var		17,15,16
	collect_list		17
	collect_value		14
	collect_value		13
	collect_value		12
	collect_value		16
	collect_value		5
	collect_vector		1
	collect_vector		4
	collect_vector		6
	put_vector		1,1
	write_element_value		1,0,15
	get_vector_value		2,1
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_values_inc		3,8,2
	enqueue_goal		4,stay_4_0
	put_values_inc		1,10,2
	execute		3,join_3_0
get_if_any_2_14:
	try_me_else		get_if_any_2_1
	read_elements_inc		1,2,8,2
	read_elements_inc		4,2,10,2
	read_element		6,1,17
	read_elements_inc		6,2,12,3
	wait_list_var_var		17,15,16
	put_integer		18,1
	g_less_than		18,7
	collect_value		5
	collect_vector		4
	put_vector		4,1
	write_element_value		4,0,15
	get_vector_value		2,4
	put_reused_list		2,17
	write_car_variable		2,15
	write_cdr_variable		2,5
	get_list_value		13,2
	b_decrement		7,2
	put_reused_vector		4,6
	write_element_value		4,0,2
	write_element_value		4,1,16
	write_element_value		4,2,12
	write_element_value		4,3,5
	write_element_value		4,4,14
	put_reused_vector		2,1
	write_element_value		2,0,15
	write_element_value		2,1,4
	write_elements_inc		2,2,10,2
	put_value		1,3
	put_values_inc		3,8,2
	execute		4,splay_4_0
get_if_any_2_6:
	read_elements_inc		1,0,3,3
	wait_vector		5,4
	read_elements_inc		5,0,6,2
	wait_vector		7,5
	read_element		7,0,8
	integer		8
	test_integer		8,1,get_if_any_2_18
	try_me_else		get_if_any_2_18
	read_elements_inc		1,3,9,3
	read_elements_inc		5,2,12,2
	read_element		7,1,19
	read_elements_inc		7,2,14,3
	wait_list_var_var		19,17,18
	collect_list		19
	collect_value		16
	collect_value		15
	collect_value		14
	collect_value		18
	collect_value		6
	collect_vector		1
	collect_vector		5
	collect_vector		7
	put_vector		1,1
	write_element_value		1,0,17
	get_vector_value		2,1
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,3
	set_values_inc		4,9,3
	enqueue_goal		6,splay0_6_0
	put_values_inc		1,12,2
	execute		3,join_3_0
get_if_any_2_18:
	try_me_else		get_if_any_2_1
	read_elements_inc		1,3,9,3
	read_elements_inc		5,2,12,2
	read_element		7,1,19
	read_elements_inc		7,2,14,3
	wait_list_var_var		19,17,18
	put_integer		20,1
	g_less_than		20,8
	collect_value		6
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,17
	get_vector_value		2,1
	put_reused_list		1,19
	write_car_variable		1,17
	write_cdr_variable		1,6
	get_list_value		15,1
	b_decrement		8,1
	put_reused_vector		2,7
	write_element_value		2,0,1
	write_element_value		2,1,18
	write_element_value		2,2,14
	write_element_value		2,3,6
	write_element_value		2,4,16
	put_reused_vector		5,5
	write_element_value		5,0,17
	write_element_value		5,1,2
	write_elements_inc		5,2,12,2
	put_values_inc		1,3,3
	put_values_inc		4,9,3
	execute		6,splay_6_0
get_if_any_2_1:
	suspend		get_if_any_2_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any_and_put,6
get_if_any_and_put_6_0:
	put_value		9,1
	create_goal		4
	set_variable		1,7
	set_variable		2,8
	set_values_inc		3,4,2
	enqueue_goal		4,get_if_any_and_put_4_0
	put_value		1,2
	put_value		2,6
	put_values_dec		4,8,2
	put_value		6,9
	execute		6,down_6_0
get_if_any_and_put_6_1:
	suspend		get_if_any_and_put_6_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any_and_put,4
get_if_any_and_put_4_0:
	try_me_else		get_if_any_and_put_4_1
	vector		1
	jump_on_arity		1,5,get_if_any_and_put_4_1
	table_entry		get_if_any_and_put_4_1
	table_entry		get_if_any_and_put_4_1
	table_entry		get_if_any_and_put_4_3
	table_entry		get_if_any_and_put_4_1
	table_entry		get_if_any_and_put_4_4
get_if_any_and_put_4_3:
	read_elements_inc		1,0,5,2
	collect_vector		1
	get_value		5,2
	put_vector		1,0
	get_vector_value		3,1
	put_list_val_var		1,4,2
	put_vector		3,5
	write_element_integer		3,0,1
	write_elements_inc		3,1,1,2
	write_element_variable		3,3,1
	write_element_value		3,4,1
	get_vector_value		6,3
	proceed
get_if_any_and_put_4_4:
	read_elements_inc		1,0,5,2
	read_element		1,2,14
	read_element		1,3,7
	wait_vector		14,5
	read_element		14,0,8
	read_element		14,1,15
	read_elements_inc		14,2,9,3
	wait_list_var_var		15,12,13
	collect_value		5
	collect_vector		1
	get_value		6,2
	put_vector		1,1
	write_element_value		1,0,12
	get_vector_value		3,1
	put_reused_list_val_val		1,15,4,13
	put_reused_vector		2,14
	write_element_value		2,0,8
	write_element_value		2,1,1
	write_elements_inc		2,2,9,3
	get_vector_value		7,2
	proceed
get_if_any_and_put_4_1:
	suspend		get_if_any_and_put_4_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put_if_any,7
get_and_put_if_any_7_0:
	put_value		9,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,4,3
	enqueue_goal		4,get_and_put_if_any_4_0
	put_value		1,2
	put_value		2,7
	put_values_inc		4,8,2
	execute		5,down_for_get_5_0
get_and_put_if_any_7_1:
	suspend		get_and_put_if_any_7_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put_if_any,4
get_and_put_if_any_4_0:
	try_me_else		get_and_put_if_any_4_1
	vector		1
	jump_on_arity		1,7,get_and_put_if_any_4_1
	table_entry		get_and_put_if_any_4_1
	table_entry		get_and_put_if_any_4_3
	table_entry		get_and_put_if_any_4_4
	table_entry		get_and_put_if_any_4_1
	table_entry		get_and_put_if_any_4_5
	table_entry		get_and_put_if_any_4_1
	table_entry		get_and_put_if_any_4_6
get_and_put_if_any_4_3:
	read_element		1,0,5
	collect_value		5
	put_vector		5,0
	get_vector_value		2,5
	put_reused_vector		1,1
	write_element_value		1,0,3
	get_vector_value		4,1
	proceed
get_and_put_if_any_4_4:
	read_element		1,0,15
	read_element		1,1,5
	wait_vector		15,4
	read_element		15,0,6
	read_element		15,1,16
	read_elements_inc		15,2,7,2
	wait_vector		16,5
	read_element		16,0,9
	read_element		16,1,17
	read_elements_inc		16,2,10,3
	wait_list_var_var		17,13,14
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,13
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		4,1
	put_reused_list_val_val		1,17,3,14
	put_reused_vector		2,16
	write_element_value		2,0,9
	write_element_value		2,1,1
	write_elements_inc		2,2,10,3
	put_reused_vector		1,15
	write_element_value		1,0,6
	write_element_value		1,1,2
	write_elements_inc		1,2,7,2
	get_vector_value		5,1
	proceed
get_and_put_if_any_4_5:
	read_element		1,0,5
	read_element		1,1,17
	read_elements_inc		1,2,6,2
	wait_vector		17,4
	read_element		17,0,8
	read_element		17,1,18
	read_elements_inc		17,2,9,2
	wait_vector		18,5
	read_element		18,0,11
	read_element		18,1,19
	read_elements_inc		18,2,12,3
	wait_list_var_var		19,15,16
	collect_vector		17
	put_vector		17,1
	write_element_value		17,0,15
	get_vector_value		2,17
	put_vector		2,0
	get_vector_value		4,2
	put_reused_list_val_val		2,19,3,16
	put_reused_vector		3,18
	write_element_value		3,0,11
	write_element_value		3,1,2
	write_elements_inc		3,2,12,3
	put_reused_vector		2,1
	write_element_value		2,0,8
	write_element_value		2,1,3
	write_elements_inc		2,2,9,2
	put_value		1,5
	put_values_inc		3,6,2
	execute		4,splay_4_0
get_and_put_if_any_4_6:
	read_elements_inc		1,0,5,2
	read_element		1,2,19
	read_elements_inc		1,3,7,3
	wait_vector		19,4
	read_element		19,0,10
	read_element		19,1,20
	read_elements_inc		19,2,11,2
	wait_vector		20,5
	read_element		20,0,13
	read_element		20,1,21
	read_elements_inc		20,2,14,3
	wait_list_var_var		21,17,18
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,17
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		4,1
	put_reused_list_val_val		1,21,3,18
	put_reused_vector		2,20
	write_element_value		2,0,13
	write_element_value		2,1,1
	write_elements_inc		2,2,14,3
	put_reused_vector		3,19
	write_element_value		3,0,10
	write_element_value		3,1,2
	write_elements_inc		3,2,11,2
	put_values_inc		1,5,2
	put_values_inc		4,7,3
	execute		6,splay_6_0
get_and_put_if_any_4_1:
	suspend		get_and_put_if_any_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy,5
carbon_copy_5_0:
	try_me_else		carbon_copy_5_1
	jump_on_non_atom		5,carbon_copy_5_3
	branch_on_atom		5,2,carbon_copy_5_1
	bucket_entry_a		ascending,carbon_copy_5_4
	bucket_entry_a		descending,carbon_copy_5_5
carbon_copy_5_4:
	execute		4,carbon_copy_4_0
carbon_copy_5_5:
	execute		4,carbon_copy_descending_4_0
carbon_copy_5_3:
	check_vector		5,3,carbon_copy_5_1
	read_elements_inc		5,0,6,3
	atom		6
	atom		7
	integer		8
	collect_vector		5
	execute		4,carbon_copy_4_0
carbon_copy_5_1:
	suspend		carbon_copy_5_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy,4
carbon_copy_4_0:
	try_me_else		carbon_copy_4_1
	vector		1
	jump_on_arity		1,5,carbon_copy_4_1
	table_entry		carbon_copy_4_3
	table_entry		carbon_copy_4_1
	table_entry		carbon_copy_4_1
	table_entry		carbon_copy_4_1
	table_entry		carbon_copy_4_4
carbon_copy_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copy_4_4:
	read_element		1,0,5
	read_element		1,1,14
	read_elements_inc		1,2,6,2
	wait_vector		14,5
	read_element		14,0,8
	read_element		14,1,15
	read_elements_inc		14,2,9,3
	wait_list_var_var		15,12,13
	get_nil		9
	get_nil		11
	put_reused_list		9,15
	write_car_marked_value		9,12
	write_cdr_variable		9,16
	put_reused_vector		11,14
	write_elements_inc		11,0,8,2
	write_element_variable		11,2,15
	write_element_variable		11,3,14
	write_element_variable		11,4,9
	put_reused_vector		17,1
	write_element_marked_value		17,0,5
	write_element_value		17,1,11
	write_element_variable		17,2,8
	write_element_variable		17,3,1
	get_vector_value		4,17
	create_goal		4
	set_value		1,7
	set_variable		2,7
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copy_4_0
	create_goal		8
	set_value		1,10
	set_values_inc		2,13,2
	set_value		4,9
	set_values_dec		5,16,2
	set_variable		7,4
	set_value		8,7
	enqueue_goal		8,carbon_copy_elements_8_0
	put_vector		1,2
	write_element_value		1,0,5
	write_element_value		1,1,12
	put_list_val_val		3,1,4
	put_value		1,6
	put_value		4,8
	execute		4,carbon_copy_4_0
carbon_copy_4_1:
	suspend		carbon_copy_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_descending,4
carbon_copy_descending_4_0:
	try_me_else		carbon_copy_descending_4_1
	vector		1
	jump_on_arity		1,5,carbon_copy_descending_4_1
	table_entry		carbon_copy_descending_4_3
	table_entry		carbon_copy_descending_4_1
	table_entry		carbon_copy_descending_4_1
	table_entry		carbon_copy_descending_4_1
	table_entry		carbon_copy_descending_4_4
carbon_copy_descending_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copy_descending_4_4:
	read_element		1,0,5
	read_element		1,1,14
	read_elements_inc		1,2,6,2
	wait_vector		14,5
	read_element		14,0,8
	read_element		14,1,15
	read_elements_inc		14,2,9,3
	wait_list_var_var		15,12,13
	get_nil		9
	get_nil		11
	put_reused_list		9,15
	write_car_marked_value		9,12
	write_cdr_variable		9,16
	put_reused_vector		11,14
	write_elements_inc		11,0,8,2
	write_element_variable		11,2,15
	write_element_variable		11,3,14
	write_element_variable		11,4,9
	put_reused_vector		17,1
	write_element_marked_value		17,0,5
	write_element_value		17,1,11
	write_element_variable		17,2,8
	write_element_variable		17,3,1
	get_vector_value		4,17
	create_goal		4
	set_value		1,6
	set_variable		2,6
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copy_descending_4_0
	create_goal		8
	set_value		1,10
	set_values_inc		2,13,2
	set_value		4,9
	set_values_dec		5,16,2
	set_variable		7,4
	set_value		8,6
	enqueue_goal		8,carbon_copy_elements_8_0
	put_vector		1,2
	write_element_value		1,0,5
	write_element_value		1,1,12
	put_list_val_val		3,1,4
	put_value		1,7
	put_value		4,8
	execute		4,carbon_copy_descending_4_0
carbon_copy_descending_4_1:
	suspend		carbon_copy_descending_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_elements,8
carbon_copy_elements_8_0:
	try_me_else		carbon_copy_elements_8_1
	jump_on_non_list_var_var		1,carbon_copy_elements_8_3,9,10
	wait_list_var_var		2,11,12
	put_reused_list		1,1
	write_car_marked_value		1,9
	write_cdr_variable		1,13
	get_list_value		3,1
	put_reused_list		1,2
	write_car_marked_value		1,11
	write_cdr_variable		1,14
	get_list_value		5,1
	put_vector		1,2
	write_element_value		1,0,9
	write_element_value		1,1,11
	get_list_val_var		7,2,1,9
	put_value		1,10
	put_values_inc		2,12,2
	put_value		5,14
	put_value		7,9
	execute		8,carbon_copy_elements_8_0
carbon_copy_elements_8_3:
	check_nil		1,carbon_copy_elements_8_1
	wait_nil		2
	get_value		3,4
	get_value		5,6
	get_value		7,8
	proceed
carbon_copy_elements_8_1:
	suspend		carbon_copy_elements_8_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_with_key,5
carbon_copy_with_key_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,carbon_copy_with_key_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
carbon_copy_with_key_5_1:
	suspend		carbon_copy_with_key_5_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_with_key,2
carbon_copy_with_key_2_0:
	try_me_else		carbon_copy_with_key_2_1
	vector		1
	jump_on_arity		1,7,carbon_copy_with_key_2_1
	table_entry		carbon_copy_with_key_2_1
	table_entry		carbon_copy_with_key_2_3
	table_entry		carbon_copy_with_key_2_4
	table_entry		carbon_copy_with_key_2_1
	table_entry		carbon_copy_with_key_2_5
	table_entry		carbon_copy_with_key_2_1
	table_entry		carbon_copy_with_key_2_6
carbon_copy_with_key_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	get_nil		2
	proceed
carbon_copy_with_key_2_4:
	read_element		1,0,12
	read_element		1,1,3
	wait_vector		12,4
	read_element		12,0,4
	read_element		12,1,13
	read_elements_inc		12,2,5,2
	wait_vector		13,5
	read_elements_inc		13,0,7,5
	collect_vector		1
	put_value		14,2
	get_nil		9
	put_reused_vector		1,13
	write_element_value		1,0,7
	write_element_variable		1,1,2
	write_element_variable		1,2,7
	write_elements_inc		1,3,10,2
	put_reused_vector		9,12
	write_element_value		9,0,4
	write_element_value		9,1,1
	write_elements_inc		9,2,5,2
	get_vector_value		3,9
	put_value		1,8
	put_value		3,7
	put_value		4,14
	execute		4,carbon_copy_elements_4_0
carbon_copy_with_key_2_5:
	read_element		1,0,3
	read_element		1,1,14
	read_elements_inc		1,2,4,2
	wait_vector		14,4
	read_element		14,0,6
	read_element		14,1,15
	read_elements_inc		14,2,7,2
	wait_vector		15,5
	read_elements_inc		15,0,9,5
	collect_vector		14
	put_value		14,2
	get_nil		11
	create_goal		4
	set_value		1,3
	put_reused_vector		2,15
	write_element_value		2,0,9
	write_element_variable		2,1,9
	write_element_variable		2,2,3
	write_elements_inc		2,3,12,2
	put_reused_vector		1,1
	write_element_value		1,0,6
	write_element_value		1,1,2
	write_elements_inc		1,2,7,2
	set_value		2,1
	set_values_inc		3,4,2
	enqueue_goal		4,splay_4_0
	put_values_dec		1,10,2
	put_value		4,14
	execute		4,carbon_copy_elements_4_0
carbon_copy_with_key_2_6:
	read_elements_inc		1,0,3,2
	read_element		1,2,16
	read_elements_inc		1,3,5,3
	wait_vector		16,4
	read_element		16,0,8
	read_element		16,1,17
	read_elements_inc		16,2,9,2
	wait_vector		17,5
	read_elements_inc		17,0,11,5
	collect_vector		1
	put_value		18,2
	get_nil		13
	create_goal		6
	set_values_inc		1,3,2
	put_reused_vector		1,17
	write_element_value		1,0,11
	write_element_variable		1,1,2
	write_element_variable		1,2,3
	write_elements_inc		1,3,14,2
	put_reused_vector		4,16
	write_element_value		4,0,8
	write_element_value		4,1,1
	write_elements_inc		4,2,9,2
	set_values_inc		3,4,4
	enqueue_goal		6,splay_6_0
	put_value		1,12
	put_value		4,18
	execute		4,carbon_copy_elements_4_0
carbon_copy_with_key_2_1:
	suspend		carbon_copy_with_key_2_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_elements,4
carbon_copy_elements_4_0:
	try_me_else		carbon_copy_elements_4_1
	jump_on_non_list_var_var		1,carbon_copy_elements_4_3,5,6
	put_reused_list		1,1
	write_car_marked_value		1,5
	write_cdr_variable		1,7
	get_list_value		2,1
	get_list_val_var		4,1,5,5
	put_values_inc		1,6,2
	put_value		4,5
	execute		4,carbon_copy_elements_4_0
carbon_copy_elements_4_3:
	check_nil		1,carbon_copy_elements_4_1
	get_value		2,3
	get_nil		4
	proceed
carbon_copy_elements_4_1:
	suspend		carbon_copy_elements_4_0
	module_entry		keyed_sorted_bag
	predicate		get_max_if_any,4
get_max_if_any_4_0:
	try_me_else		get_max_if_any_4_1
	jump_on_non_atom		4,get_max_if_any_4_3
	branch_on_atom		4,2,get_max_if_any_4_1
	bucket_entry_a		ascending,get_max_if_any_4_4
	bucket_entry_a		descending,get_max_if_any_4_5
get_max_if_any_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_any_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_any_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_any_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_max_if_any_4_3:
	check_vector		4,3,get_max_if_any_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_any_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_any_4_1:
	suspend		get_max_if_any_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_max_if_any,3
do_get_max_if_any_3_0:
	try_me_else		do_get_max_if_any_3_1
	vector		1
	jump_on_arity		1,5,do_get_max_if_any_3_1
	table_entry		do_get_max_if_any_3_3
	table_entry		do_get_max_if_any_3_1
	table_entry		do_get_max_if_any_3_1
	table_entry		do_get_max_if_any_3_1
	table_entry		do_get_max_if_any_3_4
do_get_max_if_any_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_max_if_any_3_4:
	read_elements_inc		1,0,4,2
	wait_vector		5,5
	read_element		5,0,6
	integer		6
	test_integer		6,1,do_get_max_if_any_3_7
	try_me_else		do_get_max_if_any_3_7
	read_elements_inc		1,2,7,2
	read_element		5,1,14
	read_elements_inc		5,2,9,3
	wait_list_var_var		14,12,13
	collect_list		14
	collect_value		8
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		13
	collect_vector		1
	collect_vector		5
	put_vector		1,2
	write_element_value		1,0,4
	write_element_value		1,1,12
	get_vector_value		2,1
	get_value		3,7
	proceed
do_get_max_if_any_3_7:
	try_me_else		do_get_max_if_any_3_1
	read_elements_inc		1,2,7,2
	read_element		5,1,14
	read_elements_inc		5,2,9,3
	wait_list_var_var		14,12,13
	put_integer		15,1
	g_less_than		15,6
	put_vector		15,2
	write_element_value		15,0,4
	write_element_value		15,1,12
	get_vector_value		2,15
	put_reused_list		2,14
	write_car_variable		2,14
	write_cdr_variable		2,12
	get_list_value		10,2
	b_decrement		6,2
	put_reused_vector		4,5
	write_element_value		4,0,2
	write_element_value		4,1,13
	write_element_value		4,2,9
	write_elements_dec		4,3,12,2
	put_reused_vector		1,1
	write_element_value		1,0,14
	write_element_value		1,1,4
	write_elements_inc		1,2,7,2
	get_vector_value		3,1
	proceed
do_get_max_if_any_3_1:
	suspend		do_get_max_if_any_3_0
	module_entry		keyed_sorted_bag
	predicate		get_min_if_any,4
get_min_if_any_4_0:
	try_me_else		get_min_if_any_4_1
	jump_on_non_atom		4,get_min_if_any_4_3
	branch_on_atom		4,2,get_min_if_any_4_1
	bucket_entry_a		ascending,get_min_if_any_4_4
	bucket_entry_a		descending,get_min_if_any_4_5
get_min_if_any_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_any_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_any_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_any_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_min_if_any_4_3:
	check_vector		4,3,get_min_if_any_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_any_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_any_4_1:
	suspend		get_min_if_any_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_min_if_any,3
do_get_min_if_any_3_0:
	try_me_else		do_get_min_if_any_3_1
	vector		1
	jump_on_arity		1,5,do_get_min_if_any_3_1
	table_entry		do_get_min_if_any_3_3
	table_entry		do_get_min_if_any_3_1
	table_entry		do_get_min_if_any_3_1
	table_entry		do_get_min_if_any_3_1
	table_entry		do_get_min_if_any_3_4
do_get_min_if_any_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_min_if_any_3_4:
	read_elements_inc		1,0,4,2
	wait_vector		5,5
	read_element		5,0,6
	integer		6
	test_integer		6,1,do_get_min_if_any_3_7
	try_me_else		do_get_min_if_any_3_7
	read_elements_inc		1,2,7,2
	read_element		5,1,14
	read_elements_inc		5,2,9,3
	wait_list_var_var		14,12,13
	collect_list		14
	collect_value		7
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		13
	collect_vector		1
	collect_vector		5
	put_vector		1,2
	write_element_value		1,0,4
	write_element_value		1,1,12
	get_vector_value		2,1
	get_value		3,8
	proceed
do_get_min_if_any_3_7:
	try_me_else		do_get_min_if_any_3_1
	read_elements_inc		1,2,7,2
	read_element		5,1,14
	read_elements_inc		5,2,9,3
	wait_list_var_var		14,12,13
	put_integer		15,1
	g_less_than		15,6
	put_vector		15,2
	write_element_value		15,0,4
	write_element_value		15,1,12
	get_vector_value		2,15
	put_reused_list		2,14
	write_car_variable		2,14
	write_cdr_variable		2,12
	get_list_value		10,2
	b_decrement		6,2
	put_reused_vector		4,5
	write_element_value		4,0,2
	write_element_value		4,1,13
	write_element_value		4,2,9
	write_elements_dec		4,3,12,2
	put_reused_vector		1,1
	write_element_value		1,0,14
	write_element_value		1,1,4
	write_elements_inc		1,2,7,2
	get_vector_value		3,1
	proceed
do_get_min_if_any_3_1:
	suspend		do_get_min_if_any_3_0
	module_entry		keyed_sorted_bag
	predicate		depth,3
depth_3_0:
	put_value		5,2
	b_merge		2,4
	create_goal		4
	set_values_inc		1,1,2
	set_integer		3,0
	set_value		4,3
	enqueue_goal		4,depth_4_0
	put_value		1,4
	put_integer		2,0
	put_value		3,5
	execute		3,depth_checker_3_0
depth_3_1:
	suspend		depth_3_0
	module_entry		keyed_sorted_bag
	predicate		depth,4
depth_4_0:
	try_me_else		depth_4_1
	vector		1
	jump_on_arity		1,5,depth_4_1
	table_entry		depth_4_3
	table_entry		depth_4_1
	table_entry		depth_4_1
	table_entry		depth_4_1
	table_entry		depth_4_4
depth_4_3:
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	put_vector		1,0
	get_vector_value		4,1
	proceed
depth_4_4:
	read_elements_inc		1,0,5,4
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,6
	write_element_variable		1,3,5
	get_vector_value		4,1
	put_vector		1,2
	write_element_variable		1,0,9
	write_element_variable		1,1,4
	get_vector_value		2,1
	b_increment		3,1
	put_value		3,1
	create_goal		4
	set_value		1,8
	set_value		2,4
	set_marked_value		3,3
	set_value		4,5
	enqueue_goal		4,depth_4_0
	put_value		1,7
	put_value		2,9
	put_value		4,6
	execute		4,depth_4_0
depth_4_1:
	suspend		depth_4_0
	module_entry		keyed_sorted_bag
	predicate		depth_checker,3
depth_checker_3_0:
	try_me_else		depth_checker_3_1
	wait_list_var_var		1,4,5
	integer		2
	integer		4
	g_less_than		2,4
	collect_list		1
	put_values_dec		1,5,2
	execute		3,depth_checker_3_0
depth_checker_3_1:
	otherwise		depth_checker_3_0
	try_me_else		depth_checker_3_5
	jump_on_non_list_var_var		1,depth_checker_3_7,4,5
	collect_list		1
	collect_value		4
	put_value		1,5
	execute		3,depth_checker_3_0
depth_checker_3_7:
	check_nil		1,depth_checker_3_5
	get_value		3,2
	proceed
depth_checker_3_5:
	suspend		depth_checker_3_0
	module_entry		keyed_sorted_bag
	predicate		count,3
count_3_0:
	put_value		5,2
	b_merge		2,4
	create_goal		3
	set_values_inc		1,1,3
	enqueue_goal		3,do_count_3_0
	put_value		1,4
	put_integer		2,0
	put_value		3,5
	execute		3,counter_3_0
count_3_1:
	suspend		count_3_0
	module_entry		keyed_sorted_bag
	predicate		do_count,3
do_count_3_0:
	try_me_else		do_count_3_1
	vector		1
	jump_on_arity		1,5,do_count_3_1
	table_entry		do_count_3_3
	table_entry		do_count_3_1
	table_entry		do_count_3_1
	table_entry		do_count_3_1
	table_entry		do_count_3_4
do_count_3_3:
	get_nil		2
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_count_3_4:
	read_elements_inc		1,0,4,4
	put_list		9
	write_car_integer		9,1
	write_cdr_variable		9,8
	get_list_value		2,9
	put_vector		10,2
	write_element_variable		10,0,2
	write_element_variable		10,1,9
	get_vector_value		8,10
	put_reused_vector		8,1
	write_elements_inc		8,0,4,2
	write_element_variable		8,2,4
	write_element_variable		8,3,1
	get_vector_value		3,8
	create_goal		3
	set_value		1,7
	set_value		2,9
	set_value		3,1
	enqueue_goal		3,do_count_3_0
	put_value		1,6
	put_value		3,4
	execute		3,do_count_3_0
do_count_3_1:
	suspend		do_count_3_0
	module_entry		keyed_sorted_bag
	predicate		counter,3
counter_3_0:
	try_me_else		counter_3_1
	jump_on_non_list_var_var		1,counter_3_3,4,5
	collect_list		1
	b_add		2,4,2
	put_value		1,5
	execute		3,counter_3_0
counter_3_3:
	check_nil		1,counter_3_1
	get_value		3,2
	proceed
counter_3_1:
	suspend		counter_3_0
	module_entry		keyed_sorted_bag
	predicate		data_count,3
data_count_3_0:
	put_value		5,2
	b_merge		2,4
	create_goal		3
	set_values_inc		1,1,3
	enqueue_goal		3,do_data_count_3_0
	put_value		1,4
	put_integer		2,0
	put_value		3,5
	execute		3,counter_3_0
data_count_3_1:
	suspend		data_count_3_0
	module_entry		keyed_sorted_bag
	predicate		do_data_count,3
do_data_count_3_0:
	try_me_else		do_data_count_3_1
	vector		1
	jump_on_arity		1,5,do_data_count_3_1
	table_entry		do_data_count_3_3
	table_entry		do_data_count_3_1
	table_entry		do_data_count_3_1
	table_entry		do_data_count_3_1
	table_entry		do_data_count_3_4
do_data_count_3_3:
	get_nil		2
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_data_count_3_4:
	read_element		1,0,4
	read_element		1,1,15
	read_elements_inc		1,2,5,2
	wait_vector		15,5
	read_elements_inc		15,0,7,5
	put_list		13
	write_car_marked_value		13,7
	write_cdr_variable		13,12
	get_list_value		2,13
	put_vector		2,2
	write_element_variable		2,0,14
	write_element_variable		2,1,13
	get_vector_value		12,2
	put_reused_vector		2,15
	write_elements_inc		2,0,7,5
	put_reused_vector		7,1
	write_element_value		7,0,4
	write_element_value		7,1,2
	write_element_variable		7,2,4
	write_element_variable		7,3,1
	get_vector_value		3,7
	create_goal		3
	set_value		1,6
	set_value		2,13
	set_value		3,1
	enqueue_goal		3,do_data_count_3_0
	put_value		1,5
	put_value		2,14
	put_value		3,4
	execute		3,do_data_count_3_0
do_data_count_3_1:
	suspend		do_data_count_3_0
	module_entry		keyed_sorted_bag
	predicate		possessory_rate,3
possessory_rate_3_0:
	put_variable		4,7
	put_integer		5,100
	b_multiply		4,5,4
	put_integer		5,1
	put_variable		8,6
	b_shift_left		5,8,5
	b_decrement		5,5
	b_divide		4,5,4
	get_value		2,4
	create_goal		3
	set_variable		1,4
	set_value		2,7
	set_value		3,3
	enqueue_goal		3,count_3_0
	put_value		2,6
	put_value		3,4
	execute		3,depth_3_0
possessory_rate_3_1:
	suspend		possessory_rate_3_0
	module_entry		keyed_sorted_bag
	predicate		down,6
down_6_0:
	try_me_else		down_6_1
	jump_on_non_atom		6,down_6_3
	put_vector		10,4
	write_element_variable		10,0,9
	write_element_variable		10,1,8
	write_element_variable		10,2,7
	write_element_variable		10,3,6
	get_vector_value		2,10
	put_vector		2,4
	write_elements_dec		2,0,9,4
	execute		5,down_def_5_0
down_6_3:
	check_vector		6,3,down_6_1
	read_elements_inc		6,0,7,3
	atom		7
	atom		8
	integer		9
	put_vector		14,4
	write_element_variable		14,0,13
	write_element_variable		14,1,12
	write_element_variable		14,2,11
	write_element_variable		14,3,10
	get_vector_value		2,14
	put_vector		2,4
	write_elements_dec		2,0,13,4
	put_reused_vector		6,6
	write_elements_inc		6,0,7,3
	execute		6,down_cod_6_0
down_6_1:
	suspend		down_6_0
	module_entry		keyed_sorted_bag
	predicate		down_def,5
down_def_5_0:
	try_me_else		down_def_5_1
	vector		1
	jump_on_arity		1,5,down_def_5_1
	table_entry		down_def_5_3
	table_entry		down_def_5_1
	table_entry		down_def_5_1
	table_entry		down_def_5_1
	table_entry		down_def_5_4
down_def_5_3:
	wait_vector		2,4
	read_element		2,0,1
	read_elements_inc		2,1,6,3
	collect_vector		2
	get_value		3,4
	put_vector		2,0
	get_vector_value		7,2
	put_vector		2,0
	get_vector_value		8,2
	put_vector		2,2
	write_element_value		2,0,1
	write_element_value		2,1,6
	get_vector_value		5,2
	proceed
down_def_5_4:
	read_element		1,0,6
	try_me_else		down_def_5_5
	wait		6
	switch_on_type		6,down_def_5_6,down_def_5_7,down_def_5_5,down_def_5_5,down_def_5_5,down_def_5_8
down_def_5_6:
	read_elements_inc		1,1,7,3
	atom		3
	g_tag_and_value		6,10,11
	g_tag_and_value		3,12,13
	try_me_else		down_def_5_10
	g_less_than		11,13
	put_reused_vector		10,1
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_value		6,10
	execute		6,down_def_r_6_0
down_def_5_10:
	try_me_else		down_def_5_5
	g_less_than		13,11
	put_reused_vector		10,1
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_value		6,10
	execute		6,down_def_l_6_0
down_def_5_7:
	read_elements_inc		1,1,7,3
	integer		3
	try_me_else		down_def_5_12
	g_less_than		6,3
	put_reused_vector		10,1
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_value		6,10
	execute		6,down_def_r_6_0
down_def_5_12:
	try_me_else		down_def_5_5
	g_less_than		3,6
	put_reused_vector		10,1
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_value		6,10
	execute		6,down_def_l_6_0
down_def_5_8:
	is_float		6,down_def_5_5
	read_elements_inc		1,1,7,3
	float		3
	try_me_else		down_def_5_14
	g_float_less_than		6,3
	put_reused_vector		10,1
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_value		6,10
	execute		6,down_def_r_6_0
down_def_5_14:
	try_me_else		down_def_5_5
	g_float_less_than		3,6
	put_reused_vector		10,1
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_value		6,10
	execute		6,down_def_l_6_0
down_def_5_5:
	read_elements_inc		1,1,7,3
	try_me_else		down_def_5_1
	wait_vector		2,4
	read_elements_inc		2,0,10,4
	wait_value		3,6
	collect_value		6
	collect_vector		2
	put_marked_value		3,3
	get_value		3,4
	get_value		8,12
	get_value		9,13
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_element_value		1,1,10
	write_element_value		1,2,7
	write_element_value		1,3,11
	get_vector_value		5,1
	proceed
down_def_5_1:
	otherwise		down_def_5_0
	try_me_else		down_def_5_35
	wait_vector		1,4
	read_elements_inc		1,0,6,4
	create_goal		6
	put_reused_vector		1,1
	write_element_variable		1,0,10
	write_elements_inc		1,1,7,3
	set_values_inc		1,1,2
	set_variable		3,7
	set_values_inc		4,4,2
	set_variable		6,5
	enqueue_goal		6,wait_def_6_0
	put_value		1,6
	put_value		2,3
	put_value		3,10
	put_value		4,7
	execute_external		comparator,sort,5
down_def_5_35:
	suspend		down_def_5_0
	module_entry		keyed_sorted_bag
	predicate		wait_def,6
wait_def_6_0:
	try_me_else		wait_def_6_1
	wait_vector		1,4
	read_elements_inc		1,0,7,4
	atom		6
	branch_on_atom		6,2,wait_def_6_1
	bucket_entry_a		no,wait_def_6_4
	bucket_entry_a		yes,wait_def_6_5
wait_def_6_4:
	put_reused_vector		6,1
	write_elements_inc		6,0,7,3
	write_element_void		6,3
	put_value		1,10
	execute		6,down_def_r_6_0
wait_def_6_5:
	put_reused_vector		6,1
	write_element_value		6,0,3
	write_element_value		6,1,8
	write_element_void		6,2
	write_element_value		6,3,10
	put_value		1,9
	put_value		3,7
	execute		6,down_def_l_6_0
wait_def_6_1:
	suspend		wait_def_6_0
	module_entry		keyed_sorted_bag
	predicate		down_def_r,6
down_def_r_6_0:
	try_me_else		down_def_r_6_1
	vector		1
	jump_on_arity		1,5,down_def_r_6_1
	table_entry		down_def_r_6_3
	table_entry		down_def_r_6_1
	table_entry		down_def_r_6_1
	table_entry		down_def_r_6_1
	table_entry		down_def_r_6_4
down_def_r_6_3:
	wait_vector		2,4
	read_elements_inc		2,0,7,4
	wait_vector		6,4
	read_element		6,0,1
	read_elements_inc		6,1,11,3
	collect_value		13
	collect_vector		6
	get_value		3,4
	put_structured_constant		3,'$SCNST_3'
	put_reused_vector		2,2
	write_element_value		2,0,1
	write_elements_inc		2,1,11,2
	write_element_value		2,3,3
	get_vector_value		9,2
	put_vector		1,0
	get_vector_value		10,1
	put_vector		1,2
	write_elements_inc		1,0,7,2
	get_vector_value		5,1
	proceed
down_def_r_6_4:
	read_element		1,0,7
	try_me_else		down_def_r_6_5
	wait		7
	switch_on_type		7,down_def_r_6_6,down_def_r_6_7,down_def_r_6_5,down_def_r_6_5,down_def_r_6_5,down_def_r_6_8
down_def_r_6_6:
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	atom		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	g_tag_and_value		7,19,20
	g_tag_and_value		3,21,22
	try_me_else		down_def_r_6_12
	g_less_than		20,22
	collect_value		18
	put_reused_vector		1,1
	write_elements_inc		1,0,15,3
	write_element_value		1,3,9
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		13,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,14
	put_value		1,10
	execute		5,down_def_5_0
down_def_r_6_12:
	try_me_else		down_def_r_6_5
	g_less_than		22,20
	collect_value		18
	put_reused_vector		18,1
	write_elements_inc		18,0,15,3
	write_element_variable		18,3,1
	get_vector_value		13,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,10
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_r_6_7:
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	integer		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	try_me_else		down_def_r_6_16
	g_less_than		7,3
	collect_value		18
	put_reused_vector		1,1
	write_elements_inc		1,0,15,3
	write_element_value		1,3,9
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		13,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,14
	put_value		1,10
	execute		5,down_def_5_0
down_def_r_6_16:
	try_me_else		down_def_r_6_5
	g_less_than		3,7
	collect_value		18
	put_reused_vector		18,1
	write_elements_inc		18,0,15,3
	write_element_variable		18,3,1
	get_vector_value		13,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,10
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_r_6_8:
	is_float		7,down_def_r_6_5
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	float		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	try_me_else		down_def_r_6_20
	g_float_less_than		7,3
	collect_value		18
	put_reused_vector		1,1
	write_elements_inc		1,0,15,3
	write_element_value		1,3,9
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		13,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,14
	put_value		1,10
	execute		5,down_def_5_0
down_def_r_6_20:
	try_me_else		down_def_r_6_5
	g_float_less_than		3,7
	collect_value		18
	put_reused_vector		18,1
	write_elements_inc		18,0,15,3
	write_element_variable		18,3,1
	get_vector_value		13,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,10
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_r_6_5:
	read_elements_inc		1,1,8,3
	try_me_else		down_def_r_6_1
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	wait_value		3,7
	collect_value		18
	collect_value		7
	collect_vector		6
	put_marked_value		3,3
	get_value		3,4
	put_reused_vector		1,1
	write_elements_inc		1,0,15,3
	write_element_value		1,3,9
	get_vector_value		13,1
	get_value		14,10
	put_reused_vector		1,2
	write_element_value		1,0,3
	write_element_value		1,1,11
	write_element_value		1,2,8
	write_element_value		1,3,12
	get_vector_value		5,1
	proceed
down_def_r_6_1:
	otherwise		down_def_r_6_0
	try_me_else		down_def_r_6_59
	wait_vector		1,4
	read_elements_inc		1,0,7,4
	create_goal		7
	put_reused_vector		1,1
	write_element_variable		1,0,11
	write_elements_inc		1,1,8,3
	set_values_inc		1,1,2
	set_variable		3,8
	set_values_inc		4,4,3
	set_variable		7,5
	enqueue_goal		7,wait_def_r2_7_0
	put_value		1,7
	put_value		2,3
	put_value		3,11
	put_value		4,8
	execute_external		comparator,sort,5
down_def_r_6_59:
	suspend		down_def_r_6_0
	module_entry		keyed_sorted_bag
	predicate		wait_def_r2,7
wait_def_r2_7_0:
	try_me_else		wait_def_r2_7_1
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	wait_vector		2,4
	read_elements_inc		2,0,12,4
	wait_vector		6,4
	read_elements_inc		6,0,16,4
	atom		7
	branch_on_atom		7,2,wait_def_r2_7_1
	bucket_entry_a		no,wait_def_r2_7_6
	bucket_entry_a		yes,wait_def_r2_7_7
wait_def_r2_7_6:
	collect_value		19
	put_reused_vector		1,1
	write_elements_inc		1,0,16,3
	write_element_value		1,3,10
	put_reused_vector		2,2
	write_elements_inc		2,0,8,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,12,2
	write_element_value		2,2,1
	write_element_value		2,3,15
	put_value		1,11
	execute		5,down_def_5_0
wait_def_r2_7_7:
	collect_value		19
	put_reused_vector		7,1
	write_elements_inc		7,0,16,3
	write_element_variable		7,3,1
	get_vector_value		14,7
	put_reused_vector		2,2
	write_element_value		2,0,3
	write_element_value		2,1,9
	write_element_variable		2,2,3
	write_element_value		2,3,11
	get_vector_value		15,2
	put_reused_vector		2,6
	write_elements_inc		2,0,12,2
	write_element_value		2,2,1
	write_element_value		2,3,3
	put_value		1,10
	put_value		3,8
	execute		5,down_def_5_0
wait_def_r2_7_1:
	suspend		wait_def_r2_7_0
	module_entry		keyed_sorted_bag
	predicate		down_def_l,6
down_def_l_6_0:
	try_me_else		down_def_l_6_1
	vector		1
	jump_on_arity		1,5,down_def_l_6_1
	table_entry		down_def_l_6_3
	table_entry		down_def_l_6_1
	table_entry		down_def_l_6_1
	table_entry		down_def_l_6_1
	table_entry		down_def_l_6_4
down_def_l_6_3:
	wait_vector		2,4
	read_elements_inc		2,0,7,4
	wait_vector		6,4
	read_element		6,0,1
	read_elements_inc		6,1,11,3
	collect_value		12
	collect_vector		6
	get_value		3,4
	put_vector		3,0
	get_vector_value		9,3
	put_structured_constant		3,'$SCNST_4'
	put_reused_vector		2,2
	write_element_value		2,0,1
	write_element_value		2,1,11
	write_element_value		2,2,3
	write_element_value		2,3,13
	get_vector_value		10,2
	put_vector		1,2
	write_elements_inc		1,0,7,2
	get_vector_value		5,1
	proceed
down_def_l_6_4:
	read_element		1,0,7
	try_me_else		down_def_l_6_5
	wait		7
	switch_on_type		7,down_def_l_6_6,down_def_l_6_7,down_def_l_6_5,down_def_l_6_5,down_def_l_6_5,down_def_l_6_8
down_def_l_6_6:
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	atom		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	g_tag_and_value		7,19,20
	g_tag_and_value		3,21,22
	try_me_else		down_def_l_6_12
	g_less_than		20,22
	collect_value		17
	put_reused_vector		17,1
	write_elements_inc		17,0,7,3
	write_element_variable		17,3,1
	get_vector_value		13,17
	put_reused_vector		2,2
	write_elements_inc		2,0,15,2
	write_element_variable		2,2,7
	write_element_value		2,3,18
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,10
	execute		5,down_def_5_0
down_def_l_6_12:
	try_me_else		down_def_l_6_5
	g_less_than		22,20
	collect_value		17
	put_reused_vector		1,1
	write_elements_inc		1,0,15,2
	write_element_value		1,2,10
	write_element_value		1,3,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,1
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,3
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_l_6_7:
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	integer		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	try_me_else		down_def_l_6_16
	g_less_than		7,3
	collect_value		17
	put_reused_vector		17,1
	write_elements_inc		17,0,7,3
	write_element_variable		17,3,1
	get_vector_value		13,17
	put_reused_vector		2,2
	write_elements_inc		2,0,15,2
	write_element_variable		2,2,7
	write_element_value		2,3,18
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,10
	execute		5,down_def_5_0
down_def_l_6_16:
	try_me_else		down_def_l_6_5
	g_less_than		3,7
	collect_value		17
	put_reused_vector		1,1
	write_elements_inc		1,0,15,2
	write_element_value		1,2,10
	write_element_value		1,3,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,1
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,3
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_l_6_8:
	is_float		7,down_def_l_6_5
	read_elements_inc		1,1,8,3
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	float		3
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	try_me_else		down_def_l_6_20
	g_float_less_than		7,3
	collect_value		17
	put_reused_vector		17,1
	write_elements_inc		17,0,7,3
	write_element_variable		17,3,1
	get_vector_value		13,17
	put_reused_vector		2,2
	write_elements_inc		2,0,15,2
	write_element_variable		2,2,7
	write_element_value		2,3,18
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,10
	execute		5,down_def_5_0
down_def_l_6_20:
	try_me_else		down_def_l_6_5
	g_float_less_than		3,7
	collect_value		17
	put_reused_vector		1,1
	write_elements_inc		1,0,15,2
	write_element_value		1,2,10
	write_element_value		1,3,18
	put_reused_vector		2,2
	write_elements_inc		2,0,7,2
	write_element_variable		2,2,7
	write_element_value		2,3,1
	get_vector_value		14,2
	put_reused_vector		2,6
	write_elements_inc		2,0,11,3
	write_element_value		2,3,7
	put_value		1,9
	execute		5,down_def_5_0
down_def_l_6_5:
	read_elements_inc		1,1,8,3
	try_me_else		down_def_l_6_1
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	wait_vector		6,4
	read_elements_inc		6,0,15,4
	wait_value		3,7
	collect_value		17
	collect_value		7
	collect_vector		6
	put_marked_value		3,3
	get_value		3,4
	get_value		13,9
	put_reused_vector		1,1
	write_elements_inc		1,0,15,2
	write_element_value		1,2,10
	write_element_value		1,3,18
	get_vector_value		14,1
	put_reused_vector		1,2
	write_element_value		1,0,3
	write_element_value		1,1,11
	write_element_value		1,2,8
	write_element_value		1,3,12
	get_vector_value		5,1
	proceed
down_def_l_6_1:
	otherwise		down_def_l_6_0
	try_me_else		down_def_l_6_59
	wait_vector		1,4
	read_elements_inc		1,0,7,4
	create_goal		7
	put_reused_vector		1,1
	write_element_variable		1,0,11
	write_elements_inc		1,1,8,3
	set_values_inc		1,1,2
	set_variable		3,8
	set_values_inc		4,4,3
	set_variable		7,5
	enqueue_goal		7,wait_def_l2_7_0
	put_value		1,7
	put_value		2,3
	put_value		3,11
	put_value		4,8
	execute_external		comparator,sort,5
down_def_l_6_59:
	suspend		down_def_l_6_0
	module_entry		keyed_sorted_bag
	predicate		wait_def_l2,7
wait_def_l2_7_0:
	try_me_else		wait_def_l2_7_1
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	wait_vector		2,4
	read_elements_inc		2,0,12,4
	wait_vector		6,4
	read_elements_inc		6,0,16,4
	atom		7
	branch_on_atom		7,2,wait_def_l2_7_1
	bucket_entry_a		no,wait_def_l2_7_6
	bucket_entry_a		yes,wait_def_l2_7_7
wait_def_l2_7_6:
	collect_value		18
	put_reused_vector		7,1
	write_elements_inc		7,0,8,3
	write_element_variable		7,3,1
	get_vector_value		14,7
	put_reused_vector		2,2
	write_elements_inc		2,0,16,2
	write_element_variable		2,2,7
	write_element_value		2,3,19
	get_vector_value		15,2
	put_reused_vector		2,6
	write_elements_inc		2,0,12,2
	write_element_value		2,2,1
	write_element_value		2,3,7
	put_value		1,11
	execute		5,down_def_5_0
wait_def_l2_7_7:
	collect_value		18
	put_reused_vector		1,1
	write_elements_inc		1,0,16,2
	write_element_value		1,2,11
	write_element_value		1,3,19
	put_reused_vector		2,2
	write_element_value		2,0,3
	write_element_value		2,1,9
	write_element_variable		2,2,3
	write_element_value		2,3,1
	get_vector_value		15,2
	put_reused_vector		2,6
	write_elements_inc		2,0,12,3
	write_element_value		2,3,3
	put_value		1,10
	put_value		3,8
	execute		5,down_def_5_0
wait_def_l2_7_1:
	suspend		wait_def_l2_7_0
	module_entry		keyed_sorted_bag
	predicate		down_cod,6
down_cod_6_0:
	try_me_else		down_cod_6_1
	vector		1
	jump_on_arity		1,5,down_cod_6_1
	table_entry		down_cod_6_3
	table_entry		down_cod_6_1
	table_entry		down_cod_6_1
	table_entry		down_cod_6_1
	table_entry		down_cod_6_4
down_cod_6_3:
	wait_vector		2,4
	read_element		2,0,1
	read_elements_inc		2,1,7,3
	collect_value		6
	collect_vector		2
	get_value		3,4
	put_vector		2,0
	get_vector_value		8,2
	put_vector		2,0
	get_vector_value		9,2
	put_vector		2,2
	write_element_value		2,0,1
	write_element_value		2,1,7
	get_vector_value		5,2
	proceed
down_cod_6_4:
	read_elements_inc		1,0,7,4
	wait_vector		2,4
	read_elements_inc		2,0,11,4
	wait_value		7,3
	collect_value		6
	collect_value		3
	collect_vector		2
	put_marked_value		7,7
	get_value		7,4
	get_value		9,13
	get_value		10,14
	put_reused_vector		1,1
	write_element_value		1,0,7
	write_element_value		1,1,11
	write_element_value		1,2,8
	write_element_value		1,3,12
	get_vector_value		5,1
	proceed
down_cod_6_1:
	otherwise		down_cod_6_0
	try_me_else		down_cod_6_7
	wait_vector		1,4
	read_elements_inc		1,0,7,4
	put_marked_value		13,6
	put_vector		11,5
	write_element_value		11,0,7
	write_element_value		11,1,3
	write_element_variable		11,2,12
	write_element_variable		11,3,3
	write_element_variable		11,4,7
	b_apply		13,11
	put_reused_vector		1,1
	write_element_value		1,0,12
	write_elements_inc		1,1,8,3
	execute		7,wait_cod_7_0
down_cod_6_7:
	suspend		down_cod_6_0
	module_entry		keyed_sorted_bag
	predicate		wait_cod,7
wait_cod_7_0:
	try_me_else		wait_cod_7_1
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	atom		7
	branch_on_atom		7,2,wait_cod_7_1
	bucket_entry_a		no,wait_cod_7_4
	bucket_entry_a		yes,wait_cod_7_5
wait_cod_7_4:
	put_reused_vector		7,1
	write_elements_inc		7,0,8,3
	write_element_void		7,3
	put_value		1,11
	execute		7,down_cod_r_7_0
wait_cod_7_5:
	put_reused_vector		7,1
	write_element_value		7,0,3
	write_element_value		7,1,9
	write_element_void		7,2
	write_element_value		7,3,11
	put_value		1,10
	put_value		3,8
	execute		7,down_cod_l_7_0
wait_cod_7_1:
	suspend		wait_cod_7_0
	module_entry		keyed_sorted_bag
	predicate		down_cod_r,7
down_cod_r_7_0:
	try_me_else		down_cod_r_7_1
	vector		1
	jump_on_arity		1,5,down_cod_r_7_1
	table_entry		down_cod_r_7_3
	table_entry		down_cod_r_7_1
	table_entry		down_cod_r_7_1
	table_entry		down_cod_r_7_1
	table_entry		down_cod_r_7_4
down_cod_r_7_3:
	wait_vector		2,4
	read_elements_inc		2,0,8,4
	wait_vector		7,4
	read_element		7,0,1
	read_elements_inc		7,1,12,3
	collect_value		14
	collect_value		6
	collect_vector		7
	get_value		3,4
	put_structured_constant		3,'$SCNST_5'
	put_reused_vector		2,2
	write_element_value		2,0,1
	write_elements_inc		2,1,12,2
	write_element_value		2,3,3
	get_vector_value		10,2
	put_vector		1,0
	get_vector_value		11,1
	put_vector		1,2
	write_elements_inc		1,0,8,2
	get_vector_value		5,1
	proceed
down_cod_r_7_4:
	read_elements_inc		1,0,8,4
	wait_vector		2,4
	read_elements_inc		2,0,12,4
	wait_value		8,3
	wait_vector		7,4
	read_element		7,0,3
	read_elements_inc		7,1,16,3
	collect_value		18
	collect_value		6
	collect_vector		7
	put_marked_value		8,8
	get_value		8,4
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_elements_inc		1,1,16,2
	write_element_value		1,3,10
	get_vector_value		14,1
	get_value		15,11
	put_reused_vector		1,2
	write_element_value		1,0,8
	write_element_value		1,1,12
	write_element_value		1,2,9
	write_element_value		1,3,13
	get_vector_value		5,1
	proceed
down_cod_r_7_1:
	otherwise		down_cod_r_7_0
	try_me_else		down_cod_r_7_7
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	put_marked_value		14,6
	put_vector		12,5
	write_element_value		12,0,8
	write_element_value		12,1,3
	write_element_variable		12,2,13
	write_element_variable		12,3,3
	write_element_variable		12,4,8
	b_apply		14,12
	put_reused_vector		1,1
	write_element_value		1,0,13
	write_elements_inc		1,1,9,3
	execute		8,wait_cod_r2_8_0
down_cod_r_7_7:
	suspend		down_cod_r_7_0
	module_entry		keyed_sorted_bag
	predicate		wait_cod_r2,8
wait_cod_r2_8_0:
	try_me_else		wait_cod_r2_8_1
	wait_vector		1,4
	read_elements_inc		1,0,9,4
	wait_vector		2,4
	read_elements_inc		2,0,13,4
	wait_vector		7,4
	read_elements_inc		7,0,17,4
	atom		8
	branch_on_atom		8,2,wait_cod_r2_8_1
	bucket_entry_a		no,wait_cod_r2_8_6
	bucket_entry_a		yes,wait_cod_r2_8_7
wait_cod_r2_8_6:
	collect_value		20
	put_reused_vector		1,1
	write_elements_inc		1,0,17,3
	write_element_value		1,3,11
	put_reused_vector		2,2
	write_elements_inc		2,0,9,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		15,2
	put_reused_vector		2,7
	write_elements_inc		2,0,13,2
	write_element_value		2,2,1
	write_element_value		2,3,16
	put_value		1,12
	execute		6,down_cod_6_0
wait_cod_r2_8_7:
	collect_value		20
	put_reused_vector		8,1
	write_elements_inc		8,0,17,3
	write_element_variable		8,3,1
	get_vector_value		15,8
	put_reused_vector		2,2
	write_element_value		2,0,3
	write_element_value		2,1,10
	write_element_variable		2,2,3
	write_element_value		2,3,12
	get_vector_value		16,2
	put_reused_vector		2,7
	write_elements_inc		2,0,13,2
	write_element_value		2,2,1
	write_element_value		2,3,3
	put_value		1,11
	put_value		3,9
	execute		6,down_cod_6_0
wait_cod_r2_8_1:
	suspend		wait_cod_r2_8_0
	module_entry		keyed_sorted_bag
	predicate		down_cod_l,7
down_cod_l_7_0:
	try_me_else		down_cod_l_7_1
	vector		1
	jump_on_arity		1,5,down_cod_l_7_1
	table_entry		down_cod_l_7_3
	table_entry		down_cod_l_7_1
	table_entry		down_cod_l_7_1
	table_entry		down_cod_l_7_1
	table_entry		down_cod_l_7_4
down_cod_l_7_3:
	wait_vector		2,4
	read_elements_inc		2,0,8,4
	wait_vector		7,4
	read_element		7,0,1
	read_elements_inc		7,1,12,3
	collect_value		13
	collect_value		6
	collect_vector		7
	get_value		3,4
	put_vector		3,0
	get_vector_value		10,3
	put_structured_constant		3,'$SCNST_6'
	put_reused_vector		2,2
	write_element_value		2,0,1
	write_element_value		2,1,12
	write_element_value		2,2,3
	write_element_value		2,3,14
	get_vector_value		11,2
	put_vector		1,2
	write_elements_inc		1,0,8,2
	get_vector_value		5,1
	proceed
down_cod_l_7_4:
	read_elements_inc		1,0,8,4
	wait_vector		2,4
	read_elements_inc		2,0,12,4
	wait_value		8,3
	wait_vector		7,4
	read_element		7,0,3
	read_elements_inc		7,1,16,3
	collect_value		17
	collect_value		6
	collect_vector		7
	put_marked_value		8,8
	get_value		8,4
	get_value		14,10
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_element_value		1,1,16
	write_element_value		1,2,11
	write_element_value		1,3,18
	get_vector_value		15,1
	put_reused_vector		1,2
	write_element_value		1,0,8
	write_element_value		1,1,12
	write_element_value		1,2,9
	write_element_value		1,3,13
	get_vector_value		5,1
	proceed
down_cod_l_7_1:
	otherwise		down_cod_l_7_0
	try_me_else		down_cod_l_7_7
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	put_marked_value		14,6
	put_vector		12,5
	write_element_value		12,0,8
	write_element_value		12,1,3
	write_element_variable		12,2,13
	write_element_variable		12,3,3
	write_element_variable		12,4,8
	b_apply		14,12
	put_reused_vector		1,1
	write_element_value		1,0,13
	write_elements_inc		1,1,9,3
	execute		8,wait_cod_l2_8_0
down_cod_l_7_7:
	suspend		down_cod_l_7_0
	module_entry		keyed_sorted_bag
	predicate		wait_cod_l2,8
wait_cod_l2_8_0:
	try_me_else		wait_cod_l2_8_1
	wait_vector		1,4
	read_elements_inc		1,0,9,4
	wait_vector		2,4
	read_elements_inc		2,0,13,4
	wait_vector		7,4
	read_elements_inc		7,0,17,4
	atom		8
	branch_on_atom		8,2,wait_cod_l2_8_1
	bucket_entry_a		no,wait_cod_l2_8_6
	bucket_entry_a		yes,wait_cod_l2_8_7
wait_cod_l2_8_6:
	collect_value		19
	put_reused_vector		8,1
	write_elements_inc		8,0,9,3
	write_element_variable		8,3,1
	get_vector_value		15,8
	put_reused_vector		2,2
	write_elements_inc		2,0,17,2
	write_element_variable		2,2,8
	write_element_value		2,3,20
	get_vector_value		16,2
	put_reused_vector		2,7
	write_elements_inc		2,0,13,2
	write_element_value		2,2,1
	write_element_value		2,3,8
	put_value		1,12
	execute		6,down_cod_6_0
wait_cod_l2_8_7:
	collect_value		19
	put_reused_vector		1,1
	write_elements_inc		1,0,17,2
	write_element_value		1,2,12
	write_element_value		1,3,20
	put_reused_vector		2,2
	write_element_value		2,0,3
	write_element_value		2,1,10
	write_element_variable		2,2,3
	write_element_value		2,3,1
	get_vector_value		16,2
	put_reused_vector		2,7
	write_elements_inc		2,0,13,3
	write_element_value		2,3,3
	put_value		1,11
	put_value		3,9
	execute		6,down_cod_6_0
wait_cod_l2_8_1:
	suspend		wait_cod_l2_8_0
	module_entry		keyed_sorted_bag
	predicate		down_for_get,5
down_for_get_5_0:
	try_me_else		down_for_get_5_1
	vector		1
	jump_on_arity		1,5,down_for_get_5_1
	table_entry		down_for_get_5_3
	table_entry		down_for_get_5_1
	table_entry		down_for_get_5_1
	table_entry		down_for_get_5_1
	table_entry		down_for_get_5_4
down_for_get_5_3:
	collect_value		5
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,1
	write_element_value		1,0,3
	get_vector_value		4,1
	proceed
down_for_get_5_4:
	read_element		1,0,6
	try_me_else		down_for_get_5_5
	wait		6
	switch_on_type		6,down_for_get_5_6,down_for_get_5_7,down_for_get_5_5,down_for_get_5_5,down_for_get_5_5,down_for_get_5_8
down_for_get_5_6:
	read_elements_inc		1,1,7,3
	atom		3
	atom		5
	g_tag_and_value		6,10,11
	g_tag_and_value		3,12,13
	try_me_else		down_for_get_5_11
	g_less_than		11,13
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_atom		6,right
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_11:
	try_me_else		down_for_get_5_5
	g_less_than		13,11
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_atom		6,left
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_7:
	read_elements_inc		1,1,7,3
	integer		3
	atom		5
	try_me_else		down_for_get_5_14
	g_less_than		6,3
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_atom		6,right
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_14:
	try_me_else		down_for_get_5_5
	g_less_than		3,6
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_atom		6,left
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_8:
	is_float		6,down_for_get_5_5
	read_elements_inc		1,1,7,3
	float		3
	atom		5
	try_me_else		down_for_get_5_17
	g_float_less_than		6,3
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,3
	write_element_void		10,3
	put_value		1,9
	put_atom		6,right
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_17:
	try_me_else		down_for_get_5_5
	g_float_less_than		3,6
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	put_vector		10,4
	write_elements_inc		10,0,6,2
	write_element_void		10,2
	write_element_value		10,3,9
	put_value		1,8
	put_atom		6,left
	put_value		7,10
	execute		7,downG_7_0
down_for_get_5_5:
	read_elements_inc		1,1,7,3
	try_me_else		down_for_get_5_1
	wait_value		3,6
	collect_value		5
	collect_value		6
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_elements_inc		1,1,7,3
	put_vector		3,2
	write_elements_inc		3,0,1,2
	get_vector_value		4,3
	proceed
down_for_get_5_1:
	otherwise		down_for_get_5_0
	try_me_else		down_for_get_5_38
	wait_vector		1,4
	read_elements_inc		1,0,6,4
	jump_on_non_atom		5,down_for_get_5_41
	put_reused_vector		13,1
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,10
	write_element_variable		13,3,1
	get_vector_value		2,13
	create_goal		6
	put_vector		2,4
	write_element_variable		2,0,13
	write_elements_inc		2,1,7,3
	set_value		1,2
	put_vector		2,4
	write_elements_dec		2,0,12,3
	write_element_value		2,3,1
	set_value		2,2
	set_variable		3,7
	set_values_inc		4,4,2
	set_variable		6,5
	enqueue_goal		6,waitG_6_0
	put_value		1,6
	put_value		2,3
	put_value		3,13
	put_value		4,7
	execute_external		comparator,sort,5
down_for_get_5_41:
	check_vector		5,3,down_for_get_5_38
	read_elements_inc		5,0,10,3
	atom		10
	atom		11
	integer		12
	put_reused_vector		1,1
	write_element_variable		1,0,16
	write_element_variable		1,1,15
	write_element_variable		1,2,14
	write_element_variable		1,3,13
	get_vector_value		2,1
	put_reused_vector		1,5
	write_element_marked_value		1,0,10
	write_element_marked_value		1,1,11
	write_element_marked_value		1,2,12
	put_vector		2,5
	write_element_value		2,0,6
	write_element_value		2,1,3
	write_element_variable		2,2,5
	write_element_variable		2,3,3
	write_element_variable		2,4,6
	b_apply		1,2
	put_vector		1,4
	write_element_value		1,0,5
	write_elements_inc		1,1,7,3
	put_vector		2,4
	write_elements_dec		2,0,16,4
	put_vector		5,3
	write_elements_inc		5,0,10,3
	execute		6,waitG_6_0
down_for_get_5_38:
	suspend		down_for_get_5_0
	module_entry		keyed_sorted_bag
	predicate		waitG,6
waitG_6_0:
	try_me_else		waitG_6_1
	wait_vector		1,4
	read_elements_inc		1,0,7,4
	atom		6
	branch_on_atom		6,2,waitG_6_1
	bucket_entry_a		no,waitG_6_4
	bucket_entry_a		yes,waitG_6_5
waitG_6_4:
	put_reused_vector		11,1
	write_elements_inc		11,0,7,3
	write_element_void		11,3
	put_value		1,10
	put_atom		6,right
	put_value		7,11
	execute		7,downG_7_0
waitG_6_5:
	put_reused_vector		11,1
	write_element_value		11,0,3
	write_element_value		11,1,8
	write_element_void		11,2
	write_element_value		11,3,10
	put_value		1,9
	put_value		3,7
	put_atom		6,left
	put_value		7,11
	execute		7,downG_7_0
waitG_6_1:
	suspend		waitG_6_0
	module_entry		keyed_sorted_bag
	predicate		downG,7
downG_7_0:
	try_me_else		downG_7_1
	vector		1
	jump_on_arity		1,5,downG_7_1
	table_entry		downG_7_3
	table_entry		downG_7_1
	table_entry		downG_7_1
	table_entry		downG_7_1
	table_entry		downG_7_4
downG_7_3:
	collect_value		5
	put_value		5,2
	put_vector		1,1
	write_element_value		1,0,3
	get_vector_value		4,1
	put_value		1,6
	put_vector		2,0
	put_value		3,7
	put_value		4,5
	execute		4,stay_4_0
downG_7_4:
	read_element		1,0,8
	try_me_else		downG_7_5
	wait		8
	switch_on_type		8,downG_7_6,downG_7_7,downG_7_5,downG_7_5,downG_7_5,downG_7_8
downG_7_6:
	read_elements_inc		1,1,9,3
	atom		3
	atom		5
	g_tag_and_value		8,12,13
	g_tag_and_value		3,14,15
	try_me_else		downG_7_11
	g_less_than		13,15
	put_reused_vector		12,1
	write_elements_inc		12,0,8,3
	write_element_void		12,3
	put_value		1,11
	put_atom		8,right
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_11:
	try_me_else		downG_7_5
	g_less_than		15,13
	put_reused_vector		12,1
	write_elements_inc		12,0,8,2
	write_element_void		12,2
	write_element_value		12,3,11
	put_value		1,10
	put_atom		8,left
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_7:
	read_elements_inc		1,1,9,3
	integer		3
	atom		5
	try_me_else		downG_7_14
	g_less_than		8,3
	put_reused_vector		12,1
	write_elements_inc		12,0,8,3
	write_element_void		12,3
	put_value		1,11
	put_atom		8,right
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_14:
	try_me_else		downG_7_5
	g_less_than		3,8
	put_reused_vector		12,1
	write_elements_inc		12,0,8,2
	write_element_void		12,2
	write_element_value		12,3,11
	put_value		1,10
	put_atom		8,left
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_8:
	is_float		8,downG_7_5
	read_elements_inc		1,1,9,3
	float		3
	atom		5
	try_me_else		downG_7_17
	g_float_less_than		8,3
	put_reused_vector		12,1
	write_elements_inc		12,0,8,3
	write_element_void		12,3
	put_value		1,11
	put_atom		8,right
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_17:
	try_me_else		downG_7_5
	g_float_less_than		3,8
	put_reused_vector		12,1
	write_elements_inc		12,0,8,2
	write_element_void		12,2
	write_element_value		12,3,11
	put_value		1,10
	put_atom		8,left
	put_value		9,12
	execute		9,downG_again_9_0
downG_7_5:
	read_elements_inc		1,1,9,3
	try_me_else		downG_7_1
	wait_value		3,8
	collect_value		5
	collect_value		8
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_elements_inc		1,1,9,3
	put_vector		3,4
	write_element_value		3,0,6
	write_element_value		3,1,1
	write_element_value		3,2,7
	write_element_value		3,3,2
	get_vector_value		4,3
	proceed
downG_7_1:
	otherwise		downG_7_0
	try_me_else		downG_7_38
	wait_vector		1,4
	read_elements_inc		1,0,8,4
	jump_on_non_atom		5,downG_7_41
	create_goal		8
	put_reused_vector		1,1
	write_element_variable		1,0,12
	write_elements_inc		1,1,9,3
	set_values_inc		1,1,2
	set_variable		3,9
	set_values_inc		4,4,4
	set_variable		8,5
	enqueue_goal		8,waitG_LorR_8_0
	put_value		1,8
	put_value		2,3
	put_value		3,12
	put_value		4,9
	execute_external		comparator,sort,5
downG_7_41:
	check_vector		5,3,downG_7_38
	read_elements_inc		5,0,12,3
	atom		12
	atom		13
	integer		14
	put_reused_vector		5,5
	write_element_marked_value		5,0,12
	write_element_marked_value		5,1,13
	write_element_marked_value		5,2,14
	put_vector		15,5
	write_element_value		15,0,8
	write_element_value		15,1,3
	write_element_variable		15,2,16
	write_element_variable		15,3,3
	write_element_variable		15,4,8
	b_apply		5,15
	put_reused_vector		1,1
	write_element_value		1,0,16
	write_elements_inc		1,1,9,3
	put_vector		5,3
	write_elements_inc		5,0,12,3
	execute		8,waitG_LorR_8_0
downG_7_38:
	suspend		downG_7_0
	module_entry		keyed_sorted_bag
	predicate		waitG_LorR,8
waitG_LorR_8_0:
	try_me_else		waitG_LorR_8_1
	wait_vector		1,4
	read_elements_inc		1,0,9,4
	atom		8
	branch_on_atom		8,2,waitG_LorR_8_1
	bucket_entry_a		no,waitG_LorR_8_4
	bucket_entry_a		yes,waitG_LorR_8_5
waitG_LorR_8_4:
	put_reused_vector		13,1
	write_elements_inc		13,0,9,3
	write_element_void		13,3
	put_value		1,12
	put_atom		8,right
	put_value		9,13
	execute		9,downG_again_9_0
waitG_LorR_8_5:
	put_reused_vector		13,1
	write_element_value		13,0,3
	write_element_value		13,1,10
	write_element_void		13,2
	write_element_value		13,3,12
	put_value		1,11
	put_value		3,9
	put_atom		8,left
	put_value		9,13
	execute		9,downG_again_9_0
waitG_LorR_8_1:
	suspend		waitG_LorR_8_0
	module_entry		keyed_sorted_bag
	predicate		downG_again,9
downG_again_9_0:
	try_me_else		downG_again_9_1
	vector		1
	jump_on_arity		1,5,downG_again_9_1
	table_entry		downG_again_9_3
	table_entry		downG_again_9_1
	table_entry		downG_again_9_1
	table_entry		downG_again_9_1
	table_entry		downG_again_9_4
downG_again_9_3:
	collect_value		5
	put_value		10,2
	put_vector		1,1
	write_element_value		1,0,3
	get_vector_value		4,1
	put_value		1,6
	put_value		2,8
	put_vector		3,0
	put_value		4,7
	put_values_inc		5,9,2
	execute		6,splay0_6_0
downG_again_9_4:
	read_element		1,0,10
	try_me_else		downG_again_9_5
	wait		10
	switch_on_type		10,downG_again_9_6,downG_again_9_7,downG_again_9_5,downG_again_9_5,downG_again_9_5,downG_again_9_8
downG_again_9_6:
	read_elements_inc		1,1,11,3
	atom		3
	atom		5
	g_tag_and_value		10,14,15
	g_tag_and_value		3,16,17
	try_me_else		downG_again_9_11
	g_less_than		15,17
	put_value		15,2
	create_goal		7
	set_value		1,13
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,13
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,right
	put_vector		3,4
	write_elements_inc		3,0,10,3
	write_element_void		3,3
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_elements_dec		3,0,14,2
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_11:
	try_me_else		downG_again_9_5
	g_less_than		17,15
	put_value		15,2
	create_goal		7
	set_value		1,12
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,12
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,left
	put_vector		3,4
	write_elements_inc		3,0,10,2
	write_element_void		3,2
	write_element_value		3,3,13
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_element_value		3,0,14
	write_element_value		3,1,12
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_7:
	read_elements_inc		1,1,11,3
	integer		3
	atom		5
	try_me_else		downG_again_9_14
	g_less_than		10,3
	put_value		15,2
	create_goal		7
	set_value		1,13
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,13
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,right
	put_vector		3,4
	write_elements_inc		3,0,10,3
	write_element_void		3,3
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_elements_dec		3,0,14,2
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_14:
	try_me_else		downG_again_9_5
	g_less_than		3,10
	put_value		15,2
	create_goal		7
	set_value		1,12
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,12
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,left
	put_vector		3,4
	write_elements_inc		3,0,10,2
	write_element_void		3,2
	write_element_value		3,3,13
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_element_value		3,0,14
	write_element_value		3,1,12
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_8:
	is_float		10,downG_again_9_5
	read_elements_inc		1,1,11,3
	float		3
	atom		5
	try_me_else		downG_again_9_17
	g_float_less_than		10,3
	put_value		15,2
	create_goal		7
	set_value		1,13
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,13
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,right
	put_vector		3,4
	write_elements_inc		3,0,10,3
	write_element_void		3,3
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_elements_dec		3,0,14,2
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_17:
	try_me_else		downG_again_9_5
	g_float_less_than		3,10
	put_value		15,2
	create_goal		7
	set_value		1,12
	put_reused_vector		16,1
	write_element_variable		16,0,14
	write_element_variable		16,1,12
	write_element_variable		16,2,2
	write_element_variable		16,3,1
	set_value		2,16
	set_values_inc		3,3,3
	set_atom		6,left
	put_vector		3,4
	write_elements_inc		3,0,10,2
	write_element_void		3,2
	write_element_value		3,3,13
	set_value		7,3
	enqueue_goal		7,downG_7_0
	put_vector		3,4
	write_element_value		3,0,14
	write_element_value		3,1,12
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_5:
	read_elements_inc		1,1,11,3
	try_me_else		downG_again_9_1
	wait_value		3,10
	collect_value		5
	collect_value		10
	put_reused_vector		1,1
	write_element_value		1,0,3
	write_elements_inc		1,1,11,3
	put_vector		3,6
	write_element_value		3,0,6
	write_element_value		3,1,8
	write_element_value		3,2,1
	write_element_value		3,3,7
	write_element_value		3,4,9
	write_element_value		3,5,2
	get_vector_value		4,3
	proceed
downG_again_9_1:
	otherwise		downG_again_9_0
	try_me_else		downG_again_9_38
	wait_vector		1,4
	read_elements_inc		1,0,10,4
	jump_on_non_atom		5,downG_again_9_41
	put_value		15,2
	create_goal		6
	put_reused_vector		1,1
	write_element_variable		1,0,14
	write_elements_inc		1,1,11,3
	set_value		1,1
	put_vector		13,4
	write_element_variable		13,0,12
	write_element_variable		13,1,11
	write_element_variable		13,2,2
	write_element_variable		13,3,1
	set_value		2,13
	set_variable		3,13
	set_values_inc		4,4,2
	set_variable		6,4
	enqueue_goal		6,waitG_6_0
	create_goal		5
	set_value		1,10
	set_value		2,3
	set_values_dec		3,14,2
	set_value		5,4
	enqueue_goal_external		comparator,sort,5
	put_vector		3,4
	write_elements_dec		3,0,12,2
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,15
	execute		6,splay_6_0
downG_again_9_41:
	check_vector		5,3,downG_again_9_38
	read_elements_inc		5,0,14,3
	atom		14
	atom		15
	integer		16
	put_value		18,2
	put_reused_vector		2,5
	write_element_marked_value		2,0,14
	write_element_marked_value		2,1,15
	write_element_marked_value		2,2,16
	put_vector		5,5
	write_element_value		5,0,10
	write_element_value		5,1,3
	write_element_variable		5,2,10
	write_element_variable		5,3,17
	write_element_variable		5,4,3
	b_apply		2,5
	create_goal		6
	put_reused_vector		1,1
	write_elements_inc		1,0,10,4
	set_value		1,1
	put_vector		11,4
	write_element_variable		11,0,10
	write_element_variable		11,1,5
	write_element_variable		11,2,2
	write_element_variable		11,3,1
	set_value		2,11
	set_value		3,17
	set_value		4,4
	put_vector		4,3
	write_elements_inc		4,0,14,3
	set_values_dec		5,4,2
	enqueue_goal		6,waitG_6_0
	put_vector		3,4
	write_element_value		3,0,10
	write_element_value		3,1,5
	write_elements_dec		3,2,2,2
	put_value		1,6
	put_value		2,8
	put_value		4,7
	put_value		5,9
	put_value		6,18
	execute		6,splay_6_0
downG_again_9_38:
	suspend		downG_again_9_0
	module_entry		keyed_sorted_bag
	predicate		stay,4
stay_4_0:
	try_me_else		stay_4_1
	atom		1
	branch_on_atom		1,2,stay_4_1
	bucket_entry_a		left,stay_4_3
	bucket_entry_a		right,stay_4_4
stay_4_3:
	wait_vector		3,4
	read_elements_inc		3,0,5,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,9,3
	collect_value		7
	collect_vector		3
	collect_vector		4
	get_value		1,5
	get_value		9,6
	get_value		10,2
	get_value		11,8
	proceed
stay_4_4:
	wait_vector		3,4
	read_elements_inc		3,0,5,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,9,3
	collect_value		8
	collect_vector		3
	collect_vector		4
	get_value		1,5
	get_value		9,6
	get_value		10,7
	get_value		11,2
	proceed
stay_4_1:
	suspend		stay_4_0
	module_entry		keyed_sorted_bag
	predicate		splay,4
splay_4_0:
	try_me_else		splay_4_1
	atom		1
	branch_on_atom		1,2,splay_4_1
	bucket_entry_a		left,splay_4_3
	bucket_entry_a		right,splay_4_4
splay_4_3:
	wait_vector		2,4
	read_elements_inc		2,0,5,4
	wait_vector		3,4
	read_elements_inc		3,0,9,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,13,3
	collect_value		11
	collect_vector		3
	collect_vector		4
	get_value		1,5
	get_value		13,6
	get_value		14,7
	put_reused_vector		1,2
	write_elements_inc		1,0,9,2
	write_element_value		1,2,8
	write_element_value		1,3,12
	get_vector_value		15,1
	proceed
splay_4_4:
	wait_vector		2,4
	read_elements_inc		2,0,5,4
	wait_vector		3,4
	read_elements_inc		3,0,9,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,13,3
	collect_value		12
	collect_vector		3
	collect_vector		4
	get_value		1,5
	get_value		13,6
	put_reused_vector		1,2
	write_elements_inc		1,0,9,3
	write_element_value		1,3,7
	get_vector_value		14,1
	get_value		15,8
	proceed
splay_4_1:
	suspend		splay_4_0
	module_entry		keyed_sorted_bag
	predicate		splay0,6
splay0_6_0:
	try_me_else		splay0_6_1
	atom		2
	branch_on_atom		2,2,splay0_6_1
	bucket_entry_a		left,splay0_6_3
	bucket_entry_a		right,splay0_6_4
splay0_6_3:
	wait_vector		5,4
	read_element		5,0,2
	read_elements_inc		5,1,7,3
	collect_value		8
	put_reused_vector		5,5
	write_element_value		5,0,2
	write_element_value		5,1,7
	write_element_value		5,2,3
	write_element_value		5,3,9
	put_values_dec		2,5,2
	put_value		4,6
	execute		4,splay_4_0
splay0_6_4:
	wait_vector		5,4
	read_element		5,0,2
	read_elements_inc		5,1,7,3
	collect_value		9
	put_reused_vector		5,5
	write_element_value		5,0,2
	write_elements_inc		5,1,7,2
	write_element_value		5,3,3
	put_values_dec		2,5,2
	put_value		4,6
	execute		4,splay_4_0
splay0_6_1:
	suspend		splay0_6_0
	module_entry		keyed_sorted_bag
	predicate		splay,6
splay_6_0:
	try_me_else		splay_6_1
	atom		1
	branch_on_atom		1,2,splay_6_1
	bucket_entry_a		left,splay_6_3
	bucket_entry_a		right,splay_6_4
splay_6_3:
	atom		2
	branch_on_atom		2,2,splay_6_1
	bucket_entry_a		left,splay_6_6
	bucket_entry_a		right,splay_6_7
splay_6_6:
	wait_vector		3,4
	read_elements_inc		3,0,7,4
	wait_vector		4,4
	read_elements_inc		4,0,11,4
	wait_vector		5,4
	read_elements_inc		5,0,15,4
	wait_vector		6,4
	read_elements_inc		6,0,1,2
	read_elements_inc		6,2,19,2
	collect_value		17
	collect_value		13
	collect_vector		5
	collect_vector		6
	get_value		1,7
	get_value		2,8
	get_value		19,9
	put_reused_vector		1,3
	write_elements_inc		1,0,11,2
	write_element_value		1,2,18
	write_element_value		1,3,14
	put_reused_vector		2,4
	write_elements_inc		2,0,15,2
	write_element_value		2,2,10
	write_element_value		2,3,1
	get_vector_value		20,2
	proceed
splay_6_7:
	wait_vector		3,4
	read_elements_inc		3,0,7,4
	wait_vector		4,4
	read_elements_inc		4,0,11,4
	wait_vector		5,4
	read_elements_inc		5,0,15,4
	wait_vector		6,4
	read_elements_inc		6,0,1,2
	read_elements_inc		6,2,19,2
	collect_value		18
	collect_value		13
	collect_vector		5
	collect_vector		6
	get_value		1,7
	get_value		2,8
	put_reused_vector		1,3
	write_elements_inc		1,0,15,3
	write_element_value		1,3,9
	get_vector_value		19,1
	put_reused_vector		1,4
	write_elements_inc		1,0,11,2
	write_element_value		1,2,10
	write_element_value		1,3,14
	get_vector_value		20,1
	proceed
splay_6_4:
	atom		2
	branch_on_atom		2,2,splay_6_1
	bucket_entry_a		left,splay_6_9
	bucket_entry_a		right,splay_6_10
splay_6_9:
	wait_vector		3,4
	read_elements_inc		3,0,7,4
	wait_vector		4,4
	read_elements_inc		4,0,11,4
	wait_vector		5,4
	read_elements_inc		5,0,15,4
	wait_vector		6,4
	read_elements_inc		6,0,1,2
	read_elements_inc		6,2,19,2
	collect_value		17
	collect_value		14
	collect_vector		5
	collect_vector		6
	get_value		1,7
	get_value		2,8
	put_reused_vector		1,3
	write_elements_inc		1,0,11,3
	write_element_value		1,3,9
	get_vector_value		19,1
	put_reused_vector		1,4
	write_elements_inc		1,0,15,2
	write_element_value		1,2,10
	write_element_value		1,3,18
	get_vector_value		20,1
	proceed
splay_6_10:
	wait_vector		3,4
	read_elements_inc		3,0,7,4
	wait_vector		4,4
	read_elements_inc		4,0,11,4
	wait_vector		5,4
	read_elements_inc		5,0,15,4
	wait_vector		6,4
	read_elements_inc		6,0,1,2
	read_elements_inc		6,2,19,2
	collect_value		18
	collect_value		14
	collect_vector		5
	collect_vector		6
	get_value		1,7
	get_value		2,8
	put_reused_vector		1,3
	write_elements_inc		1,0,11,3
	write_element_value		1,3,17
	put_reused_vector		2,4
	write_elements_inc		2,0,15,2
	write_element_value		2,2,1
	write_element_value		2,3,9
	get_vector_value		19,2
	get_value		20,10
	proceed
splay_6_1:
	suspend		splay_6_0
	module_entry		keyed_sorted_bag
	predicate		join,3
join_3_0:
	try_me_else		join_3_1
	vector		1
	jump_on_arity		1,5,join_3_1
	table_entry		join_3_3
	table_entry		join_3_1
	table_entry		join_3_1
	table_entry		join_3_1
	table_entry		join_3_4
join_3_3:
	vector		2
	jump_on_arity		2,5,join_3_1
	table_entry		join_3_6
	table_entry		join_3_1
	table_entry		join_3_1
	table_entry		join_3_1
	table_entry		join_3_7
join_3_6:
	put_vector		1,0
	get_vector_value		3,1
	proceed
join_3_7:
	read_element		2,0,1
	read_elements_inc		2,1,4,3
	put_reused_vector		2,2
	write_element_value		2,0,1
	write_elements_inc		2,1,4,3
	get_vector_value		3,2
	proceed
join_3_4:
	read_elements_inc		1,0,4,4
	put_reused_vector		10,1
	write_element_variable		10,0,9
	write_element_variable		10,1,8
	write_element_variable		10,2,1
	write_element_value		10,3,2
	get_vector_value		3,10
	put_vector		2,4
	write_elements_dec		2,0,9,2
	write_element_value		2,2,1
	write_element_void		2,3
	put_vector		3,4
	write_elements_inc		3,0,4,3
	write_element_void		3,3
	put_value		1,7
	execute		3,splay_at_max_3_0
join_3_1:
	suspend		join_3_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_max,2
splay_at_max_2_0:
	try_me_else		splay_at_max_2_1
	vector		1
	jump_on_arity		1,5,splay_at_max_2_1
	table_entry		splay_at_max_2_3
	table_entry		splay_at_max_2_1
	table_entry		splay_at_max_2_1
	table_entry		splay_at_max_2_1
	table_entry		splay_at_max_2_4
splay_at_max_2_3:
	put_vector		1,0
	get_vector_value		2,1
	proceed
splay_at_max_2_4:
	read_elements_inc		1,0,3,4
	put_reused_vector		10,1
	write_element_variable		10,0,9
	write_element_variable		10,1,8
	write_element_variable		10,2,7
	write_element_variable		10,3,1
	get_vector_value		2,10
	put_vector		2,4
	write_elements_dec		2,0,9,3
	write_element_value		2,3,1
	put_vector		7,4
	write_elements_inc		7,0,3,3
	write_element_void		7,3
	put_value		1,6
	put_value		3,7
	execute		3,splay_at_max_3_0
splay_at_max_2_1:
	suspend		splay_at_max_2_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_max,3
splay_at_max_3_0:
	try_me_else		splay_at_max_3_1
	vector		1
	jump_on_arity		1,5,splay_at_max_3_1
	table_entry		splay_at_max_3_3
	table_entry		splay_at_max_3_1
	table_entry		splay_at_max_3_1
	table_entry		splay_at_max_3_1
	table_entry		splay_at_max_3_4
splay_at_max_3_3:
	wait_vector		2,4
	read_elements_inc		2,0,4,4
	wait_vector		3,4
	read_element		3,0,1
	read_elements_inc		3,1,8,3
	collect_value		10
	collect_vector		2
	collect_vector		3
	get_value		4,1
	get_value		5,8
	get_value		6,9
	put_vector		1,0
	get_vector_value		7,1
	proceed
splay_at_max_3_4:
	read_elements_inc		1,0,4,4
	put_reused_vector		8,1
	write_elements_inc		8,0,4,3
	write_element_void		8,3
	put_value		1,7
	put_value		4,8
	execute		4,splay_at_max2_4_0
splay_at_max_3_1:
	suspend		splay_at_max_3_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_max2,4
splay_at_max2_4_0:
	try_me_else		splay_at_max2_4_1
	vector		1
	jump_on_arity		1,5,splay_at_max2_4_1
	table_entry		splay_at_max2_4_3
	table_entry		splay_at_max2_4_1
	table_entry		splay_at_max2_4_1
	table_entry		splay_at_max2_4_1
	table_entry		splay_at_max2_4_4
splay_at_max2_4_3:
	wait_vector		2,4
	read_elements_inc		2,0,5,4
	wait_vector		3,4
	read_elements_inc		3,0,9,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,13,3
	collect_value		15
	collect_value		12
	collect_vector		3
	collect_vector		4
	get_value		5,1
	get_value		6,13
	put_reused_vector		1,2
	write_elements_inc		1,0,9,3
	write_element_value		1,3,14
	get_vector_value		7,1
	put_vector		1,0
	get_vector_value		8,1
	proceed
splay_at_max2_4_4:
	read_elements_inc		1,0,5,4
	wait_vector		2,4
	read_elements_inc		2,0,9,4
	wait_vector		3,4
	read_elements_inc		3,0,13,4
	wait_vector		4,4
	read_elements_inc		4,0,17,4
	collect_value		20
	collect_value		16
	put_reused_vector		1,1
	write_elements_inc		1,0,13,3
	write_element_value		1,3,19
	put_reused_vector		2,2
	write_elements_inc		2,0,17,2
	write_element_value		2,2,1
	write_element_variable		2,3,1
	get_vector_value		11,2
	put_reused_vector		2,3
	write_elements_inc		2,0,9,2
	write_element_value		2,2,1
	write_element_value		2,3,12
	put_reused_vector		3,4
	write_elements_inc		3,0,5,3
	write_element_void		3,3
	put_value		1,8
	execute		3,splay_at_max_3_0
splay_at_max2_4_1:
	suspend		splay_at_max2_4_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_min,2
splay_at_min_2_0:
	try_me_else		splay_at_min_2_1
	vector		1
	jump_on_arity		1,5,splay_at_min_2_1
	table_entry		splay_at_min_2_3
	table_entry		splay_at_min_2_1
	table_entry		splay_at_min_2_1
	table_entry		splay_at_min_2_1
	table_entry		splay_at_min_2_4
splay_at_min_2_3:
	put_vector		1,0
	get_vector_value		2,1
	proceed
splay_at_min_2_4:
	read_elements_inc		1,0,3,4
	put_reused_vector		10,1
	write_element_variable		10,0,9
	write_element_variable		10,1,8
	write_element_variable		10,2,7
	write_element_variable		10,3,1
	get_vector_value		2,10
	put_vector		2,4
	write_elements_dec		2,0,9,3
	write_element_value		2,3,1
	put_vector		7,4
	write_elements_inc		7,0,3,2
	write_element_void		7,2
	write_element_value		7,3,6
	put_value		1,5
	put_value		3,7
	execute		3,splay_at_min_3_0
splay_at_min_2_1:
	suspend		splay_at_min_2_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_min,3
splay_at_min_3_0:
	try_me_else		splay_at_min_3_1
	vector		1
	jump_on_arity		1,5,splay_at_min_3_1
	table_entry		splay_at_min_3_3
	table_entry		splay_at_min_3_1
	table_entry		splay_at_min_3_1
	table_entry		splay_at_min_3_1
	table_entry		splay_at_min_3_4
splay_at_min_3_3:
	wait_vector		2,4
	read_elements_inc		2,0,4,4
	wait_vector		3,4
	read_element		3,0,1
	read_elements_inc		3,1,8,3
	collect_value		9
	collect_vector		2
	collect_vector		3
	get_value		4,1
	get_value		5,8
	put_vector		1,0
	get_vector_value		6,1
	get_value		7,10
	proceed
splay_at_min_3_4:
	read_elements_inc		1,0,4,4
	put_reused_vector		8,1
	write_elements_inc		8,0,4,2
	write_element_void		8,2
	write_element_value		8,3,7
	put_value		1,6
	put_value		4,8
	execute		4,splay_at_min2_4_0
splay_at_min_3_1:
	suspend		splay_at_min_3_0
	module_entry		keyed_sorted_bag
	predicate		splay_at_min2,4
splay_at_min2_4_0:
	try_me_else		splay_at_min2_4_1
	vector		1
	jump_on_arity		1,5,splay_at_min2_4_1
	table_entry		splay_at_min2_4_3
	table_entry		splay_at_min2_4_1
	table_entry		splay_at_min2_4_1
	table_entry		splay_at_min2_4_1
	table_entry		splay_at_min2_4_4
splay_at_min2_4_3:
	wait_vector		2,4
	read_elements_inc		2,0,5,4
	wait_vector		3,4
	read_elements_inc		3,0,9,4
	wait_vector		4,4
	read_element		4,0,1
	read_elements_inc		4,1,13,3
	collect_value		14
	collect_value		11
	collect_vector		3
	collect_vector		4
	get_value		5,1
	get_value		6,13
	put_vector		1,0
	get_vector_value		7,1
	put_reused_vector		1,2
	write_elements_inc		1,0,9,2
	write_element_value		1,2,15
	write_element_value		1,3,12
	get_vector_value		8,1
	proceed
splay_at_min2_4_4:
	read_elements_inc		1,0,5,4
	wait_vector		2,4
	read_elements_inc		2,0,9,4
	wait_vector		3,4
	read_elements_inc		3,0,13,4
	wait_vector		4,4
	read_elements_inc		4,0,17,4
	collect_value		19
	collect_value		15
	put_reused_vector		1,1
	write_elements_inc		1,0,13,2
	write_element_value		1,2,20
	write_element_value		1,3,16
	put_reused_vector		2,2
	write_elements_inc		2,0,17,2
	write_element_variable		2,2,13
	write_element_value		2,3,1
	get_vector_value		12,2
	put_reused_vector		2,3
	write_elements_inc		2,0,9,3
	write_element_value		2,3,13
	put_reused_vector		3,4
	write_elements_inc		3,0,5,2
	write_element_void		3,2
	write_element_value		3,3,8
	put_value		1,7
	execute		3,splay_at_min_3_0
splay_at_min2_4_1:
	suspend		splay_at_min2_4_0
	module_entry		keyed_sorted_bag
	predicate		keyed_sorted_set,2
keyed_sorted_set_2_0:
	b_merge		4,3
	get_value		4,2
	put_value		2,3
	put_vector		3,0
	execute		3,keyed_sorted_set_3_0
keyed_sorted_set_2_1:
	suspend		keyed_sorted_set_2_0
	module_entry		keyed_sorted_bag
	predicate		keyed_sorted_set,3
keyed_sorted_set_3_0:
	try_me_else		keyed_sorted_set_3_1
	jump_on_non_list		2,keyed_sorted_set_3_3
	read_car		2,4
	vector		4
	jump_on_arity		4,6,keyed_sorted_set_3_1
	table_entry		keyed_sorted_set_3_1
	table_entry		keyed_sorted_set_3_1
	table_entry		keyed_sorted_set_3_5
	table_entry		keyed_sorted_set_3_6
	table_entry		keyed_sorted_set_3_7
	table_entry		keyed_sorted_set_3_8
keyed_sorted_set_3_5:
	read_element		4,0,5
	atom		5
	hash_on_atom		5,10,keyed_sorted_set_3_1
	bucket_entry_a		carbon_copy,keyed_sorted_set_3_10
	bucket_entry_a		count,keyed_sorted_set_3_11
	bucket_entry_a		data_count,keyed_sorted_set_3_12
	bucket_entry_a		depth,keyed_sorted_set_3_13
	bucket_entry_a		do,keyed_sorted_set_3_14
	bucket_entry_a		empty,keyed_sorted_set_3_15
	bucket_entry_a		get_all,keyed_sorted_set_3_16
	bucket_entry_a		get_max_if_any,keyed_sorted_set_3_17
	bucket_entry_a		get_min_if_any,keyed_sorted_set_3_18
	bucket_entry_a		possessory_rate,keyed_sorted_set_3_19
keyed_sorted_set_3_10:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		5,1
	create_goal		3
	set_marked_value		1,5
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		5,carbon_copyS_5_0
keyed_sorted_set_3_11:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,count_3_0
keyed_sorted_set_3_12:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,count_3_0
keyed_sorted_set_3_13:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,depth_3_0
keyed_sorted_set_3_14:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	b_merge		4,2
	get_value		4,7
	create_goal		3
	set_value		1,1
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,2
	put_value		2,6
	put_value		3,4
	execute		3,prepend_3_0
keyed_sorted_set_3_15:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,empty_3_0
keyed_sorted_set_3_16:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	put_vector		1,0
	set_value		3,1
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		4,get_allS_4_0
keyed_sorted_set_3_17:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_max_if_anyS_4_0
keyed_sorted_set_3_18:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_min_if_anyS_4_0
keyed_sorted_set_3_19:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,possessory_rate_3_0
keyed_sorted_set_3_6:
	read_element		4,0,5
	atom		5
	hash_on_atom		5,5,keyed_sorted_set_3_1
	bucket_entry_a		carbon_copy,keyed_sorted_set_3_21
	bucket_entry_a		empty,keyed_sorted_set_3_22
	bucket_entry_a		get,keyed_sorted_set_3_23
	bucket_entry_a		get_all,keyed_sorted_set_3_24
	bucket_entry_a		get_if_any,keyed_sorted_set_3_25
keyed_sorted_set_3_21:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,carbon_copy_with_keyS_5_0
keyed_sorted_set_3_22:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,empty_5_0
keyed_sorted_set_3_23:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,getS_5_0
keyed_sorted_set_3_24:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,get_all_with_keyS_5_0
keyed_sorted_set_3_25:
	read_cdr		2,6
	read_elements_inc		4,1,7,2
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		5,get_if_anyS_5_0
keyed_sorted_set_3_7:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,3,keyed_sorted_set_3_1
	bucket_entry_a		get_and_put,keyed_sorted_set_3_27
	bucket_entry_a		get_if_any_and_put,keyed_sorted_set_3_28
	bucket_entry_a		put,keyed_sorted_set_3_29
keyed_sorted_set_3_27:
	read_cdr		2,6
	read_elements_inc		4,1,7,3
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,6
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,3
	execute		6,get_and_putS_6_0
keyed_sorted_set_3_28:
	read_cdr		2,6
	read_elements_inc		4,1,7,3
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,6
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,3
	execute		6,get_if_any_and_putS_6_0
keyed_sorted_set_3_29:
	read_cdr		2,6
	read_elements_inc		4,1,7,3
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,6
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,7,3
	execute		6,putS_6_0
keyed_sorted_set_3_8:
	read_cdr		2,5
	read_element		4,0,6
	wait_atom		6,get_and_put_if_any
	read_elements_inc		4,1,6,4
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,5
	set_variable		3,10
	enqueue_goal		3,keyed_sorted_set_3_0
	put_value		2,3
	put_values_inc		3,6,5
	execute		7,get_and_put_if_anyS_7_0
keyed_sorted_set_3_3:
	check_nil		2,keyed_sorted_set_3_1
	collect_value		3
	collect_value		1
	proceed
keyed_sorted_set_3_1:
	otherwise		keyed_sorted_set_3_0
	try_me_else		keyed_sorted_set_3_42
	wait_list_var_var		2,4,5
	collect_list		2
	collect_value		3
	collect_value		5
	collect_value		1
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_7'
	b_raise		2,1,4
	proceed
keyed_sorted_set_3_42:
	suspend		keyed_sorted_set_3_0
	module_entry		keyed_sorted_bag
	predicate		putS,6
putS_6_0:
	put_value		9,1
	create_goal		4
	set_variable		1,7
	set_variable		2,8
	set_values_inc		3,4,2
	enqueue_goal		4,putS_4_0
	put_value		1,2
	put_value		2,6
	put_values_dec		4,8,2
	put_value		6,9
	execute		6,down_6_0
putS_6_1:
	suspend		putS_6_0
	module_entry		keyed_sorted_bag
	predicate		putS,4
putS_4_0:
	try_me_else		putS_4_1
	vector		1
	jump_on_arity		1,5,putS_4_1
	table_entry		putS_4_1
	table_entry		putS_4_1
	table_entry		putS_4_3
	table_entry		putS_4_1
	table_entry		putS_4_4
putS_4_3:
	read_elements_inc		1,0,5,2
	collect_vector		1
	get_value		5,2
	get_value		6,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
putS_4_4:
	read_elements_inc		1,0,5,4
	collect_value		2
	collect_vector		1
	get_value		6,5
	get_value		8,3
	put_vector		1,1
	write_element_value		1,0,7
	get_vector_value		4,1
	proceed
putS_4_1:
	suspend		putS_4_0
	module_entry		keyed_sorted_bag
	predicate		getS,5
getS_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,getS_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
getS_5_1:
	suspend		getS_5_0
	module_entry		keyed_sorted_bag
	predicate		getS,2
getS_2_0:
	try_me_else		getS_2_1
	vector		1
	jump_on_arity		1,7,getS_2_1
	table_entry		getS_2_1
	table_entry		getS_2_3
	table_entry		getS_2_4
	table_entry		getS_2_1
	table_entry		getS_2_5
	table_entry		getS_2_1
	table_entry		getS_2_6
getS_2_3:
	read_element		1,0,3
	collect_vector		1
	put_integer		5,1024
	put_structured_constant		1,'$SCNST_8'
	put_func		4,3,get
	write_elements_dec		4,1,3,2
	b_raise		5,1,4
	proceed
getS_2_4:
	read_element		1,0,8
	read_element		1,1,3
	wait_vector		8,4
	read_elements_inc		8,0,4,4
	collect_value		4
	collect_vector		1
	collect_vector		8
	get_value		2,5
	put_values_inc		1,6,2
	execute		3,join_3_0
getS_2_5:
	read_element		1,0,3
	read_element		1,1,10
	read_elements_inc		1,2,4,2
	wait_vector		10,4
	read_elements_inc		10,0,6,4
	collect_value		6
	collect_vector		1
	collect_vector		10
	get_value		2,7
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_values_inc		3,4,2
	enqueue_goal		4,stay_4_0
	put_values_inc		1,8,2
	execute		3,join_3_0
getS_2_6:
	read_elements_inc		1,0,3,2
	read_element		1,2,12
	read_elements_inc		1,3,5,3
	wait_vector		12,4
	read_elements_inc		12,0,8,4
	collect_value		8
	collect_vector		1
	collect_vector		12
	get_value		2,9
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,3
	set_values_inc		4,5,3
	enqueue_goal		6,splay0_6_0
	put_values_inc		1,10,2
	execute		3,join_3_0
getS_2_1:
	suspend		getS_2_0
	module_entry		keyed_sorted_bag
	predicate		get_allS,4
get_allS_4_0:
	try_me_else		get_allS_4_1
	jump_on_non_atom		4,get_allS_4_3
	branch_on_atom		4,2,get_allS_4_1
	bucket_entry_a		ascending,get_allS_4_4
	bucket_entry_a		descending,get_allS_4_5
get_allS_4_4:
	execute		3,get_allS_3_0
get_allS_4_5:
	execute		3,get_allS_descending_3_0
get_allS_4_3:
	check_vector		4,3,get_allS_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	execute		3,get_allS_3_0
get_allS_4_1:
	suspend		get_allS_4_0
	module_entry		keyed_sorted_bag
	predicate		get_allS,3
get_allS_3_0:
	try_me_else		get_allS_3_1
	vector		1
	jump_on_arity		1,5,get_allS_3_1
	table_entry		get_allS_3_3
	table_entry		get_allS_3_1
	table_entry		get_allS_3_1
	table_entry		get_allS_3_1
	table_entry		get_allS_3_4
get_allS_3_3:
	get_value		2,3
	proceed
get_allS_3_4:
	read_elements_inc		1,0,4,4
	collect_vector		1
	create_goal		3
	set_value		1,7
	set_variable		2,7
	set_value		3,3
	enqueue_goal		3,get_allS_3_0
	put_vector		1,2
	write_elements_inc		1,0,4,2
	put_list_val_val		3,1,7
	put_value		1,6
	execute		3,get_allS_3_0
get_allS_3_1:
	suspend		get_allS_3_0
	module_entry		keyed_sorted_bag
	predicate		get_allS_descending,3
get_allS_descending_3_0:
	try_me_else		get_allS_descending_3_1
	vector		1
	jump_on_arity		1,5,get_allS_descending_3_1
	table_entry		get_allS_descending_3_3
	table_entry		get_allS_descending_3_1
	table_entry		get_allS_descending_3_1
	table_entry		get_allS_descending_3_1
	table_entry		get_allS_descending_3_4
get_allS_descending_3_3:
	get_value		2,3
	proceed
get_allS_descending_3_4:
	read_elements_inc		1,0,4,4
	collect_vector		1
	create_goal		3
	set_value		1,6
	set_variable		2,6
	set_value		3,3
	enqueue_goal		3,get_allS_descending_3_0
	put_vector		1,2
	write_elements_inc		1,0,4,2
	put_list_val_val		3,1,6
	put_value		1,7
	execute		3,get_allS_descending_3_0
get_allS_descending_3_1:
	suspend		get_allS_descending_3_0
	module_entry		keyed_sorted_bag
	predicate		get_all_with_keyS,5
get_all_with_keyS_5_0:
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,get_all_with_keyS_2_0
	put_value		4,6
	execute		5,get_if_anyS_5_0
get_all_with_keyS_5_1:
	suspend		get_all_with_keyS_5_0
	module_entry		keyed_sorted_bag
	predicate		get_all_with_keyS,2
get_all_with_keyS_2_0:
	try_me_else		get_all_with_keyS_2_1
	vector		1
	jump_on_arity		1,2,get_all_with_keyS_2_1
	table_entry		get_all_with_keyS_2_3
	table_entry		get_all_with_keyS_2_4
get_all_with_keyS_2_3:
	get_nil		2
	proceed
get_all_with_keyS_2_4:
	read_element		1,0,3
	collect_vector		1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	proceed
get_all_with_keyS_2_1:
	suspend		get_all_with_keyS_2_0
	module_entry		keyed_sorted_bag
	predicate		get_and_putS,6
get_and_putS_6_0:
	put_value		9,1
	create_goal		4
	set_variable		1,7
	set_variable		2,8
	set_values_inc		3,4,2
	enqueue_goal		4,get_and_putS_4_0
	put_value		1,2
	put_value		2,6
	put_values_dec		4,8,2
	put_value		6,9
	execute		6,down_6_0
get_and_putS_6_1:
	suspend		get_and_putS_6_0
	module_entry		keyed_sorted_bag
	predicate		get_and_putS,4
get_and_putS_4_0:
	try_me_else		get_and_putS_4_1
	vector		1
	jump_on_arity		1,5,get_and_putS_4_1
	table_entry		get_and_putS_4_1
	table_entry		get_and_putS_4_1
	table_entry		get_and_putS_4_3
	table_entry		get_and_putS_4_1
	table_entry		get_and_putS_4_4
get_and_putS_4_3:
	read_elements_inc		1,0,5,2
	collect_value		6
	collect_value		5
	collect_vector		1
	put_integer		6,1024
	put_structured_constant		1,'$SCNST_9'
	put_func		5,4,get_and_put
	write_elements_inc		5,1,2,3
	b_raise		6,1,5
	proceed
get_and_putS_4_4:
	read_elements_inc		1,0,5,4
	collect_value		5
	collect_vector		1
	get_value		6,2
	get_value		3,7
	get_value		8,4
	proceed
get_and_putS_4_1:
	suspend		get_and_putS_4_0
	module_entry		keyed_sorted_bag
	predicate		get_if_anyS,5
get_if_anyS_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,get_if_anyS_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
get_if_anyS_5_1:
	suspend		get_if_anyS_5_0
	module_entry		keyed_sorted_bag
	predicate		get_if_anyS,2
get_if_anyS_2_0:
	try_me_else		get_if_anyS_2_1
	vector		1
	jump_on_arity		1,7,get_if_anyS_2_1
	table_entry		get_if_anyS_2_1
	table_entry		get_if_anyS_2_3
	table_entry		get_if_anyS_2_4
	table_entry		get_if_anyS_2_1
	table_entry		get_if_anyS_2_5
	table_entry		get_if_anyS_2_1
	table_entry		get_if_anyS_2_6
get_if_anyS_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	put_vector		1,0
	get_vector_value		2,1
	proceed
get_if_anyS_2_4:
	read_element		1,0,8
	read_element		1,1,3
	wait_vector		8,4
	read_elements_inc		8,0,4,4
	collect_value		4
	collect_vector		1
	collect_vector		8
	put_vector		1,1
	write_element_value		1,0,5
	get_vector_value		2,1
	put_values_inc		1,6,2
	execute		3,join_3_0
get_if_anyS_2_5:
	read_element		1,0,3
	read_element		1,1,10
	read_elements_inc		1,2,4,2
	wait_vector		10,4
	read_elements_inc		10,0,6,4
	collect_value		6
	collect_vector		1
	collect_vector		10
	put_vector		1,1
	write_element_value		1,0,7
	get_vector_value		2,1
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_values_inc		3,4,2
	enqueue_goal		4,stay_4_0
	put_values_inc		1,8,2
	execute		3,join_3_0
get_if_anyS_2_6:
	read_elements_inc		1,0,3,2
	read_element		1,2,12
	read_elements_inc		1,3,5,3
	wait_vector		12,4
	read_elements_inc		12,0,8,4
	collect_value		8
	collect_vector		1
	collect_vector		12
	put_vector		1,1
	write_element_value		1,0,9
	get_vector_value		2,1
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,3
	set_values_inc		4,5,3
	enqueue_goal		6,splay0_6_0
	put_values_inc		1,10,2
	execute		3,join_3_0
get_if_anyS_2_1:
	suspend		get_if_anyS_2_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any_and_putS,6
get_if_any_and_putS_6_0:
	put_value		9,1
	create_goal		4
	set_variable		1,7
	set_variable		2,8
	set_values_inc		3,4,2
	enqueue_goal		4,get_if_any_and_putS_4_0
	put_value		1,2
	put_value		2,6
	put_values_dec		4,8,2
	put_value		6,9
	execute		6,down_6_0
get_if_any_and_putS_6_1:
	suspend		get_if_any_and_putS_6_0
	module_entry		keyed_sorted_bag
	predicate		get_if_any_and_putS,4
get_if_any_and_putS_4_0:
	try_me_else		get_if_any_and_putS_4_1
	vector		1
	jump_on_arity		1,5,get_if_any_and_putS_4_1
	table_entry		get_if_any_and_putS_4_1
	table_entry		get_if_any_and_putS_4_1
	table_entry		get_if_any_and_putS_4_3
	table_entry		get_if_any_and_putS_4_1
	table_entry		get_if_any_and_putS_4_4
get_if_any_and_putS_4_3:
	read_elements_inc		1,0,5,2
	collect_vector		1
	get_value		5,2
	put_vector		1,0
	get_vector_value		3,1
	get_value		6,4
	proceed
get_if_any_and_putS_4_4:
	read_elements_inc		1,0,5,4
	collect_value		5
	collect_vector		1
	get_value		6,2
	put_vector		1,1
	write_element_value		1,0,7
	get_vector_value		3,1
	get_value		8,4
	proceed
get_if_any_and_putS_4_1:
	suspend		get_if_any_and_putS_4_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put_if_anyS,7
get_and_put_if_anyS_7_0:
	put_value		9,1
	create_goal		4
	set_variable		1,8
	set_values_inc		2,4,3
	enqueue_goal		4,get_and_put_if_anyS_4_0
	put_value		1,2
	put_value		2,7
	put_values_inc		4,8,2
	execute		5,down_for_get_5_0
get_and_put_if_anyS_7_1:
	suspend		get_and_put_if_anyS_7_0
	module_entry		keyed_sorted_bag
	predicate		get_and_put_if_anyS,4
get_and_put_if_anyS_4_0:
	try_me_else		get_and_put_if_anyS_4_1
	vector		1
	jump_on_arity		1,7,get_and_put_if_anyS_4_1
	table_entry		get_and_put_if_anyS_4_1
	table_entry		get_and_put_if_anyS_4_3
	table_entry		get_and_put_if_anyS_4_4
	table_entry		get_and_put_if_anyS_4_1
	table_entry		get_and_put_if_anyS_4_5
	table_entry		get_and_put_if_anyS_4_1
	table_entry		get_and_put_if_anyS_4_6
get_and_put_if_anyS_4_3:
	read_element		1,0,5
	collect_value		5
	put_vector		5,0
	get_vector_value		2,5
	put_reused_vector		1,1
	write_element_value		1,0,3
	get_vector_value		4,1
	proceed
get_and_put_if_anyS_4_4:
	read_element		1,0,10
	read_element		1,1,5
	wait_vector		10,4
	read_elements_inc		10,0,6,4
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,7
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		4,1
	put_reused_vector		1,10
	write_element_value		1,0,6
	write_element_value		1,1,3
	write_elements_inc		1,2,8,2
	get_vector_value		5,1
	proceed
get_and_put_if_anyS_4_5:
	read_element		1,0,5
	read_element		1,1,12
	read_elements_inc		1,2,6,2
	wait_vector		12,4
	read_elements_inc		12,0,8,4
	collect_vector		12
	put_vector		12,1
	write_element_value		12,0,9
	get_vector_value		2,12
	put_vector		2,0
	get_vector_value		4,2
	put_reused_vector		2,1
	write_element_value		2,0,8
	write_element_value		2,1,3
	write_elements_inc		2,2,10,2
	put_value		1,5
	put_values_inc		3,6,2
	execute		4,splay_4_0
get_and_put_if_anyS_4_6:
	read_elements_inc		1,0,5,2
	read_element		1,2,14
	read_elements_inc		1,3,7,3
	wait_vector		14,4
	read_elements_inc		14,0,10,4
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,11
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		4,1
	put_reused_vector		4,14
	write_element_value		4,0,10
	write_element_value		4,1,3
	write_elements_inc		4,2,12,2
	put_values_inc		1,5,2
	put_value		3,4
	put_values_inc		4,7,3
	execute		6,splay_6_0
get_and_put_if_anyS_4_1:
	suspend		get_and_put_if_anyS_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copyS,5
carbon_copyS_5_0:
	try_me_else		carbon_copyS_5_1
	jump_on_non_atom		5,carbon_copyS_5_3
	branch_on_atom		5,2,carbon_copyS_5_1
	bucket_entry_a		ascending,carbon_copyS_5_4
	bucket_entry_a		descending,carbon_copyS_5_5
carbon_copyS_5_4:
	execute		4,carbon_copyS_4_0
carbon_copyS_5_5:
	execute		4,carbon_copyS_descending_4_0
carbon_copyS_5_3:
	check_vector		5,3,carbon_copyS_5_1
	read_elements_inc		5,0,6,3
	atom		6
	atom		7
	integer		8
	collect_vector		5
	execute		4,carbon_copyS_4_0
carbon_copyS_5_1:
	suspend		carbon_copyS_5_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copyS,4
carbon_copyS_4_0:
	try_me_else		carbon_copyS_4_1
	vector		1
	jump_on_arity		1,5,carbon_copyS_4_1
	table_entry		carbon_copyS_4_3
	table_entry		carbon_copyS_4_1
	table_entry		carbon_copyS_4_1
	table_entry		carbon_copyS_4_1
	table_entry		carbon_copyS_4_4
carbon_copyS_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copyS_4_4:
	read_elements_inc		1,0,5,4
	put_reused_vector		10,1
	write_element_marked_value		10,0,5
	write_element_marked_value		10,1,6
	write_element_variable		10,2,9
	write_element_variable		10,3,1
	get_vector_value		4,10
	create_goal		4
	set_value		1,8
	set_variable		2,4
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copyS_4_0
	put_vector		1,2
	write_elements_inc		1,0,5,2
	put_list_val_val		3,1,4
	put_value		1,7
	put_value		4,9
	execute		4,carbon_copyS_4_0
carbon_copyS_4_1:
	suspend		carbon_copyS_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copyS_descending,4
carbon_copyS_descending_4_0:
	try_me_else		carbon_copyS_descending_4_1
	vector		1
	jump_on_arity		1,5,carbon_copyS_descending_4_1
	table_entry		carbon_copyS_descending_4_3
	table_entry		carbon_copyS_descending_4_1
	table_entry		carbon_copyS_descending_4_1
	table_entry		carbon_copyS_descending_4_1
	table_entry		carbon_copyS_descending_4_4
carbon_copyS_descending_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copyS_descending_4_4:
	read_elements_inc		1,0,5,4
	put_reused_vector		10,1
	write_element_marked_value		10,0,5
	write_element_marked_value		10,1,6
	write_element_variable		10,2,9
	write_element_variable		10,3,1
	get_vector_value		4,10
	create_goal		4
	set_value		1,7
	set_variable		2,4
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copyS_descending_4_0
	put_vector		1,2
	write_elements_inc		1,0,5,2
	put_list_val_val		3,1,4
	put_value		1,8
	put_value		4,9
	execute		4,carbon_copyS_descending_4_0
carbon_copyS_descending_4_1:
	suspend		carbon_copyS_descending_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_with_keyS,5
carbon_copy_with_keyS_5_0:
	put_value		7,1
	create_goal		2
	set_variable		1,6
	set_value		2,4
	enqueue_goal		2,carbon_copy_with_keyS_2_0
	put_value		1,2
	put_value		2,5
	put_values_inc		4,6,2
	execute		5,down_for_get_5_0
carbon_copy_with_keyS_5_1:
	suspend		carbon_copy_with_keyS_5_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_with_keyS,2
carbon_copy_with_keyS_2_0:
	try_me_else		carbon_copy_with_keyS_2_1
	vector		1
	jump_on_arity		1,7,carbon_copy_with_keyS_2_1
	table_entry		carbon_copy_with_keyS_2_1
	table_entry		carbon_copy_with_keyS_2_3
	table_entry		carbon_copy_with_keyS_2_4
	table_entry		carbon_copy_with_keyS_2_1
	table_entry		carbon_copy_with_keyS_2_5
	table_entry		carbon_copy_with_keyS_2_1
	table_entry		carbon_copy_with_keyS_2_6
carbon_copy_with_keyS_2_3:
	read_element		1,0,3
	collect_value		3
	collect_vector		1
	get_nil		2
	proceed
carbon_copy_with_keyS_2_4:
	read_element		1,0,8
	read_element		1,1,3
	wait_vector		8,4
	read_elements_inc		8,0,4,4
	collect_vector		1
	put_list		1
	write_car_marked_value		1,5
	write_cdr_nil		1
	get_list_value		2,1
	put_reused_vector		1,8
	write_elements_inc		1,0,4,4
	get_vector_value		3,1
	proceed
carbon_copy_with_keyS_2_5:
	read_element		1,0,3
	read_element		1,1,10
	read_elements_inc		1,2,4,2
	wait_vector		10,4
	read_elements_inc		10,0,6,4
	collect_vector		10
	put_list		10
	write_car_marked_value		10,7
	write_cdr_nil		10
	get_list_value		2,10
	put_reused_vector		2,1
	write_elements_inc		2,0,6,4
	put_value		1,3
	put_values_inc		3,4,2
	execute		4,splay_4_0
carbon_copy_with_keyS_2_6:
	read_elements_inc		1,0,3,2
	read_element		1,2,12
	read_elements_inc		1,3,5,3
	wait_vector		12,4
	read_elements_inc		12,0,8,4
	collect_vector		1
	put_list		1
	write_car_marked_value		1,9
	write_cdr_nil		1
	get_list_value		2,1
	put_reused_vector		12,12
	write_elements_inc		12,0,8,4
	put_values_inc		1,3,2
	put_value		3,12
	put_values_inc		4,5,3
	execute		6,splay_6_0
carbon_copy_with_keyS_2_1:
	suspend		carbon_copy_with_keyS_2_0
	module_entry		keyed_sorted_bag
	predicate		get_max_if_anyS,4
get_max_if_anyS_4_0:
	try_me_else		get_max_if_anyS_4_1
	jump_on_non_atom		4,get_max_if_anyS_4_3
	branch_on_atom		4,2,get_max_if_anyS_4_1
	bucket_entry_a		ascending,get_max_if_anyS_4_4
	bucket_entry_a		descending,get_max_if_anyS_4_5
get_max_if_anyS_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_anyS_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_max_if_anyS_4_3:
	check_vector		4,3,get_max_if_anyS_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_anyS_4_1:
	suspend		get_max_if_anyS_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_max_if_anyS,3
do_get_max_if_anyS_3_0:
	try_me_else		do_get_max_if_anyS_3_1
	vector		1
	jump_on_arity		1,5,do_get_max_if_anyS_3_1
	table_entry		do_get_max_if_anyS_3_3
	table_entry		do_get_max_if_anyS_3_1
	table_entry		do_get_max_if_anyS_3_1
	table_entry		do_get_max_if_anyS_3_1
	table_entry		do_get_max_if_anyS_3_4
do_get_max_if_anyS_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_max_if_anyS_3_4:
	read_elements_inc		1,0,4,4
	collect_value		7
	collect_vector		1
	put_vector		1,2
	write_elements_inc		1,0,4,2
	get_vector_value		2,1
	get_value		3,6
	proceed
do_get_max_if_anyS_3_1:
	suspend		do_get_max_if_anyS_3_0
	module_entry		keyed_sorted_bag
	predicate		get_min_if_anyS,4
get_min_if_anyS_4_0:
	try_me_else		get_min_if_anyS_4_1
	jump_on_non_atom		4,get_min_if_anyS_4_3
	branch_on_atom		4,2,get_min_if_anyS_4_1
	bucket_entry_a		ascending,get_min_if_anyS_4_4
	bucket_entry_a		descending,get_min_if_anyS_4_5
get_min_if_anyS_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_anyS_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_min_if_anyS_4_3:
	check_vector		4,3,get_min_if_anyS_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anyS_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_anyS_4_1:
	suspend		get_min_if_anyS_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_min_if_anyS,3
do_get_min_if_anyS_3_0:
	try_me_else		do_get_min_if_anyS_3_1
	vector		1
	jump_on_arity		1,5,do_get_min_if_anyS_3_1
	table_entry		do_get_min_if_anyS_3_3
	table_entry		do_get_min_if_anyS_3_1
	table_entry		do_get_min_if_anyS_3_1
	table_entry		do_get_min_if_anyS_3_1
	table_entry		do_get_min_if_anyS_3_4
do_get_min_if_anyS_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_min_if_anyS_3_4:
	read_elements_inc		1,0,4,4
	collect_value		6
	collect_vector		1
	put_vector		1,2
	write_elements_inc		1,0,4,2
	get_vector_value		2,1
	get_value		3,7
	proceed
do_get_min_if_anyS_3_1:
	suspend		do_get_min_if_anyS_3_0
	module_entry		keyed_sorted_bag
	predicate		sorted_bag,2
sorted_bag_2_0:
	b_merge		4,3
	get_value		4,2
	put_value		2,3
	put_vector		3,0
	execute		3,sorted_bag_3_0
sorted_bag_2_1:
	suspend		sorted_bag_2_0
	module_entry		keyed_sorted_bag
	predicate		sorted_bag,3
sorted_bag_3_0:
	try_me_else		sorted_bag_3_1
	jump_on_non_list		2,sorted_bag_3_3
	read_car		2,4
	wait_vector		4,2
	read_element		4,0,5
	atom		5
	hash_on_atom		5,13,sorted_bag_3_1
	bucket_entry_a		carbon_copy,sorted_bag_3_6
	bucket_entry_a		count,sorted_bag_3_7
	bucket_entry_a		data_count,sorted_bag_3_8
	bucket_entry_a		depth,sorted_bag_3_9
	bucket_entry_a		do,sorted_bag_3_10
	bucket_entry_a		empty,sorted_bag_3_11
	bucket_entry_a		get,sorted_bag_3_12
	bucket_entry_a		get_all,sorted_bag_3_13
	bucket_entry_a		get_if_any,sorted_bag_3_14
	bucket_entry_a		get_max_if_any,sorted_bag_3_15
	bucket_entry_a		get_min_if_any,sorted_bag_3_16
	bucket_entry_a		possessory_rate,sorted_bag_3_17
	bucket_entry_a		put,sorted_bag_3_18
sorted_bag_3_6:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		5,1
	create_goal		3
	set_marked_value		1,5
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		5,carbon_copySB_5_0
sorted_bag_3_7:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,count_3_0
sorted_bag_3_8:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,data_countSB_3_0
sorted_bag_3_9:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,depth_3_0
sorted_bag_3_10:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	b_merge		4,2
	get_value		4,7
	create_goal		3
	set_value		1,1
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,2
	put_value		2,6
	put_value		3,4
	execute		3,prepend_3_0
sorted_bag_3_11:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,empty_3_0
sorted_bag_3_12:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,getSB_3_0
sorted_bag_3_13:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	put_vector		1,0
	set_value		3,1
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_nil		3
	execute		4,get_allSB_4_0
sorted_bag_3_14:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,get_if_anySB_3_0
sorted_bag_3_15:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_max_if_anySB_4_0
sorted_bag_3_16:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,6
	set_variable		3,5
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,5
	execute		4,get_min_if_anySB_4_0
sorted_bag_3_17:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		1,3
	put_value		2,7
	put_value		3,4
	execute		3,possessory_rate_3_0
sorted_bag_3_18:
	read_cdr		2,6
	read_element		4,1,7
	collect_list		2
	collect_vector		4
	create_goal		3
	set_marked_value		1,1
	set_value		2,6
	set_variable		3,4
	enqueue_goal		3,sorted_bag_3_0
	put_value		2,3
	put_value		3,7
	execute		4,putSB_4_0
sorted_bag_3_3:
	check_nil		2,sorted_bag_3_1
	collect_value		3
	collect_value		1
	proceed
sorted_bag_3_1:
	otherwise		sorted_bag_3_0
	try_me_else		sorted_bag_3_28
	wait_list_var_var		2,4,5
	collect_list		2
	collect_value		3
	collect_value		5
	collect_value		1
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_10'
	b_raise		2,1,4
	proceed
sorted_bag_3_28:
	suspend		sorted_bag_3_0
	module_entry		keyed_sorted_bag
	predicate		putSB,4
putSB_4_0:
	put_value		6,1
	create_goal		2
	set_variable		1,5
	set_variable		2,7
	enqueue_goal		2,putSB_2_0
	put_value		1,2
	put_value		2,4
	put_value		4,7
	execute		6,down_6_0
putSB_4_1:
	suspend		putSB_4_0
	module_entry		keyed_sorted_bag
	predicate		putSB,2
putSB_2_0:
	try_me_else		putSB_2_1
	vector		1
	jump_on_arity		1,5,putSB_2_1
	table_entry		putSB_2_1
	table_entry		putSB_2_1
	table_entry		putSB_2_3
	table_entry		putSB_2_1
	table_entry		putSB_2_4
putSB_2_3:
	read_elements_inc		1,0,3,2
	collect_vector		1
	get_value		3,2
	put_vector		2,3
	write_element_integer		2,0,0
	write_element_variable		2,1,1
	write_element_value		2,2,1
	get_vector_value		4,2
	proceed
putSB_2_4:
	read_elements_inc		1,0,3,2
	read_element		1,2,9
	read_element		1,3,5
	wait_vector		9,3
	read_elements_inc		9,0,6,3
	collect_vector		1
	get_value		4,3
	get_list_val_var		8,1,2,2
	b_increment		6,1
	put_reused_vector		3,9
	write_element_value		3,0,1
	write_element_value		3,1,7
	write_element_value		3,2,2
	get_vector_value		5,3
	proceed
putSB_2_1:
	suspend		putSB_2_0
	module_entry		keyed_sorted_bag
	predicate		getSB,3
getSB_3_0:
	create_goal		2
	set_variable		1,4
	set_value		2,2
	enqueue_goal		2,getSB_2_0
	put_values_inc		2,3,2
	execute		3,down_for_getSB_3_0
getSB_3_1:
	suspend		getSB_3_0
	module_entry		keyed_sorted_bag
	predicate		getSB,2
getSB_2_0:
	try_me_else		getSB_2_1
	vector		1
	jump_on_arity		1,5,getSB_2_1
	table_entry		getSB_2_3
	table_entry		getSB_2_1
	table_entry		getSB_2_4
	table_entry		getSB_2_5
	table_entry		getSB_2_6
getSB_2_3:
	put_integer		4,1024
	put_structured_constant		1,'$SCNST_11'
	put_func		3,2,get
	write_element_value		3,1,2
	b_raise		4,1,3
	proceed
getSB_2_4:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,getSB_2_10
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_elements_inc		5,1,10,2
	collect_value		8
	collect_value		11
	collect_value		10
	collect_vector		1
	collect_vector		3
	collect_vector		5
	get_value		2,4
	get_value		7,9
	proceed
getSB_2_10:
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_elements_inc		5,1,10,2
	put_integer		12,0
	g_less_than		12,6
	collect_vector		1
	get_value		2,4
	put_list		1
	write_car_variable		1,12
	write_cdr_variable		1,4
	get_list_value		10,1
	b_decrement		6,1
	put_reused_vector		2,5
	write_element_value		2,0,1
	write_element_value		2,1,4
	write_element_value		2,2,11
	put_reused_vector		1,3
	write_element_value		1,0,12
	write_element_value		1,1,2
	write_elements_inc		1,2,8,2
	get_vector_value		7,1
	proceed
getSB_2_5:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,getSB_2_14
	read_elements_inc		1,1,7,2
	read_elements_inc		3,2,9,2
	read_elements_inc		5,1,11,2
	collect_value		9
	collect_value		12
	collect_value		11
	collect_vector		1
	collect_vector		3
	collect_vector		5
	get_value		2,4
	put_atom		1,left
	put_value		2,10
	put_values_inc		3,7,2
	execute		4,stay_4_0
getSB_2_14:
	read_elements_inc		1,1,7,2
	read_elements_inc		3,2,9,2
	read_elements_inc		5,1,11,2
	put_integer		13,0
	g_less_than		13,6
	collect_vector		5
	get_value		2,4
	put_list		2
	write_car_variable		2,5
	write_cdr_variable		2,4
	get_list_value		11,2
	b_decrement		6,2
	put_reused_vector		1,1
	write_element_value		1,0,2
	write_element_value		1,1,4
	write_element_value		1,2,12
	put_reused_vector		2,3
	write_element_value		2,0,5
	write_element_value		2,1,1
	write_elements_inc		2,2,9,2
	put_atom		1,left
	put_values_inc		3,7,2
	execute		4,splay_4_0
getSB_2_6:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,getSB_2_18
	read_elements_inc		1,1,7,3
	read_elements_inc		3,2,10,2
	read_elements_inc		5,1,12,2
	collect_value		10
	collect_value		13
	collect_value		12
	collect_vector		1
	collect_vector		3
	collect_vector		5
	get_value		2,4
	put_atom		1,left
	put_atom		2,left
	put_value		3,11
	put_values_inc		4,7,3
	execute		6,splay0_6_0
getSB_2_18:
	read_elements_inc		1,1,7,3
	read_elements_inc		3,2,10,2
	read_elements_inc		5,1,12,2
	put_integer		14,0
	g_less_than		14,6
	collect_vector		3
	get_value		2,4
	put_list		2
	write_car_variable		2,14
	write_cdr_variable		2,4
	get_list_value		12,2
	b_decrement		6,2
	put_reused_vector		3,5
	write_element_value		3,0,2
	write_element_value		3,1,4
	write_element_value		3,2,13
	put_reused_vector		4,1
	write_element_value		4,0,14
	write_element_value		4,1,3
	write_elements_inc		4,2,10,2
	put_atom		1,left
	put_atom		2,left
	put_value		3,4
	put_values_inc		4,7,3
	execute		6,splay_6_0
getSB_2_1:
	suspend		getSB_2_0
	module_entry		keyed_sorted_bag
	predicate		get_allSB,4
get_allSB_4_0:
	try_me_else		get_allSB_4_1
	jump_on_non_atom		4,get_allSB_4_3
	branch_on_atom		4,2,get_allSB_4_1
	bucket_entry_a		ascending,get_allSB_4_4
	bucket_entry_a		descending,get_allSB_4_5
get_allSB_4_4:
	execute		3,get_allSB_3_0
get_allSB_4_5:
	execute		3,get_allSB_descending_3_0
get_allSB_4_3:
	check_vector		4,3,get_allSB_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	execute		3,get_allSB_3_0
get_allSB_4_1:
	suspend		get_allSB_4_0
	module_entry		keyed_sorted_bag
	predicate		get_allSB,3
get_allSB_3_0:
	try_me_else		get_allSB_3_1
	vector		1
	jump_on_arity		1,5,get_allSB_3_1
	table_entry		get_allSB_3_3
	table_entry		get_allSB_3_1
	table_entry		get_allSB_3_1
	table_entry		get_allSB_3_1
	table_entry		get_allSB_3_4
get_allSB_3_3:
	get_value		2,3
	proceed
get_allSB_3_4:
	read_element		1,0,4
	read_element		1,1,10
	read_elements_inc		1,2,5,2
	wait_vector		10,3
	read_elements_inc		10,0,7,3
	collect_value		7
	collect_vector		1
	collect_vector		10
	get_nil		9
	create_goal		3
	set_value		1,6
	set_variable		2,6
	set_value		3,3
	enqueue_goal		3,get_allSB_3_0
	create_goal		3
	set_value		1,8
	set_variable		2,1
	set_value		3,6
	enqueue_goal		3,get_elementsSB_3_0
	put_list_val_val		3,4,1
	put_value		1,5
	execute		3,get_allSB_3_0
get_allSB_3_1:
	suspend		get_allSB_3_0
	module_entry		keyed_sorted_bag
	predicate		get_allSB_descending,3
get_allSB_descending_3_0:
	try_me_else		get_allSB_descending_3_1
	vector		1
	jump_on_arity		1,5,get_allSB_descending_3_1
	table_entry		get_allSB_descending_3_3
	table_entry		get_allSB_descending_3_1
	table_entry		get_allSB_descending_3_1
	table_entry		get_allSB_descending_3_1
	table_entry		get_allSB_descending_3_4
get_allSB_descending_3_3:
	get_value		2,3
	proceed
get_allSB_descending_3_4:
	read_element		1,0,4
	read_element		1,1,10
	read_elements_inc		1,2,5,2
	wait_vector		10,3
	read_elements_inc		10,0,7,3
	collect_value		7
	collect_vector		1
	collect_vector		10
	get_nil		9
	create_goal		3
	set_value		1,5
	set_variable		2,5
	set_value		3,3
	enqueue_goal		3,get_allSB_descending_3_0
	create_goal		3
	set_value		1,8
	set_variable		2,1
	set_value		3,5
	enqueue_goal		3,get_elementsSB_3_0
	put_list_val_val		3,4,1
	put_value		1,6
	execute		3,get_allSB_descending_3_0
get_allSB_descending_3_1:
	suspend		get_allSB_descending_3_0
	module_entry		keyed_sorted_bag
	predicate		get_elementsSB,3
get_elementsSB_3_0:
	try_me_else		get_elementsSB_3_1
	jump_on_non_list_var_var		1,get_elementsSB_3_3,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,get_elementsSB_3_0
get_elementsSB_3_3:
	check_nil		1,get_elementsSB_3_1
	get_value		2,3
	proceed
get_elementsSB_3_1:
	suspend		get_elementsSB_3_0
	module_entry		keyed_sorted_bag
	predicate		get_if_anySB,3
get_if_anySB_3_0:
	create_goal		2
	set_variable		1,4
	set_value		2,2
	enqueue_goal		2,get_if_anySB_2_0
	put_values_inc		2,3,2
	execute		3,down_for_getSB_3_0
get_if_anySB_3_1:
	suspend		get_if_anySB_3_0
	module_entry		keyed_sorted_bag
	predicate		get_if_anySB,2
get_if_anySB_2_0:
	try_me_else		get_if_anySB_2_1
	vector		1
	jump_on_arity		1,5,get_if_anySB_2_1
	table_entry		get_if_anySB_2_3
	table_entry		get_if_anySB_2_1
	table_entry		get_if_anySB_2_4
	table_entry		get_if_anySB_2_5
	table_entry		get_if_anySB_2_6
get_if_anySB_2_3:
	put_vector		1,0
	get_vector_value		2,1
	proceed
get_if_anySB_2_4:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,get_if_anySB_2_10
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_elements_inc		5,1,10,2
	collect_value		8
	collect_value		11
	collect_value		10
	collect_vector		1
	collect_vector		3
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	get_value		7,9
	proceed
get_if_anySB_2_10:
	read_element		1,1,7
	read_elements_inc		3,2,8,2
	read_elements_inc		5,1,10,2
	put_integer		12,0
	g_less_than		12,6
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	put_list		1
	write_car_variable		1,12
	write_cdr_variable		1,4
	get_list_value		10,1
	b_decrement		6,1
	put_reused_vector		2,5
	write_element_value		2,0,1
	write_element_value		2,1,4
	write_element_value		2,2,11
	put_reused_vector		1,3
	write_element_value		1,0,12
	write_element_value		1,1,2
	write_elements_inc		1,2,8,2
	get_vector_value		7,1
	proceed
get_if_anySB_2_5:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,get_if_anySB_2_14
	read_elements_inc		1,1,7,2
	read_elements_inc		3,2,9,2
	read_elements_inc		5,1,11,2
	collect_value		9
	collect_value		12
	collect_value		11
	collect_vector		1
	collect_vector		3
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	put_atom		1,left
	put_value		2,10
	put_values_inc		3,7,2
	execute		4,stay_4_0
get_if_anySB_2_14:
	read_elements_inc		1,1,7,2
	read_elements_inc		3,2,9,2
	read_elements_inc		5,1,11,2
	put_integer		13,0
	g_less_than		13,6
	collect_vector		5
	put_vector		5,1
	write_element_value		5,0,4
	get_vector_value		2,5
	put_list		2
	write_car_variable		2,5
	write_cdr_variable		2,4
	get_list_value		11,2
	b_decrement		6,2
	put_reused_vector		1,1
	write_element_value		1,0,2
	write_element_value		1,1,4
	write_element_value		1,2,12
	put_reused_vector		2,3
	write_element_value		2,0,5
	write_element_value		2,1,1
	write_elements_inc		2,2,9,2
	put_atom		1,left
	put_values_inc		3,7,2
	execute		4,splay_4_0
get_if_anySB_2_6:
	read_element		1,0,3
	wait_vector		3,4
	read_elements_inc		3,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,get_if_anySB_2_18
	read_elements_inc		1,1,7,3
	read_elements_inc		3,2,10,2
	read_elements_inc		5,1,12,2
	collect_value		10
	collect_value		13
	collect_value		12
	collect_vector		1
	collect_vector		3
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	put_atom		1,left
	put_atom		2,left
	put_value		3,11
	put_values_inc		4,7,3
	execute		6,splay0_6_0
get_if_anySB_2_18:
	read_elements_inc		1,1,7,3
	read_elements_inc		3,2,10,2
	read_elements_inc		5,1,12,2
	put_integer		14,0
	g_less_than		14,6
	collect_vector		3
	put_vector		3,1
	write_element_value		3,0,4
	get_vector_value		2,3
	put_list		2
	write_car_variable		2,14
	write_cdr_variable		2,4
	get_list_value		12,2
	b_decrement		6,2
	put_reused_vector		3,5
	write_element_value		3,0,2
	write_element_value		3,1,4
	write_element_value		3,2,13
	put_reused_vector		4,1
	write_element_value		4,0,14
	write_element_value		4,1,3
	write_elements_inc		4,2,10,2
	put_atom		1,left
	put_atom		2,left
	put_value		3,4
	put_values_inc		4,7,3
	execute		6,splay_6_0
get_if_anySB_2_1:
	suspend		get_if_anySB_2_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copySB,5
carbon_copySB_5_0:
	try_me_else		carbon_copySB_5_1
	jump_on_non_atom		5,carbon_copySB_5_3
	branch_on_atom		5,2,carbon_copySB_5_1
	bucket_entry_a		ascending,carbon_copySB_5_4
	bucket_entry_a		descending,carbon_copySB_5_5
carbon_copySB_5_4:
	execute		4,carbon_copySB_4_0
carbon_copySB_5_5:
	execute		4,carbon_copySB_descending_4_0
carbon_copySB_5_3:
	check_vector		5,3,carbon_copySB_5_1
	read_elements_inc		5,0,6,3
	atom		6
	atom		7
	integer		8
	collect_vector		5
	execute		4,carbon_copySB_4_0
carbon_copySB_5_1:
	suspend		carbon_copySB_5_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copySB,4
carbon_copySB_4_0:
	try_me_else		carbon_copySB_4_1
	vector		1
	jump_on_arity		1,5,carbon_copySB_4_1
	table_entry		carbon_copySB_4_3
	table_entry		carbon_copySB_4_1
	table_entry		carbon_copySB_4_1
	table_entry		carbon_copySB_4_1
	table_entry		carbon_copySB_4_4
carbon_copySB_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copySB_4_4:
	read_element		1,0,5
	read_element		1,1,11
	read_elements_inc		1,2,6,2
	wait_vector		11,3
	read_elements_inc		11,0,8,3
	get_nil		10
	put_reused_vector		10,11
	write_element_value		10,0,8
	write_element_variable		10,1,12
	write_element_variable		10,2,11
	put_reused_vector		13,1
	write_element_marked_value		13,0,5
	write_element_value		13,1,10
	write_element_variable		13,2,8
	write_element_variable		13,3,1
	get_vector_value		4,13
	create_goal		4
	set_value		1,7
	set_variable		2,4
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copySB_4_0
	create_goal		5
	set_value		1,9
	set_values_dec		2,12,2
	set_variable		4,1
	set_value		5,4
	enqueue_goal		5,carbon_copy_elementsSB_5_0
	put_list_val_val		3,5,1
	put_value		1,6
	put_value		4,8
	execute		4,carbon_copySB_4_0
carbon_copySB_4_1:
	suspend		carbon_copySB_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copySB_descending,4
carbon_copySB_descending_4_0:
	try_me_else		carbon_copySB_descending_4_1
	vector		1
	jump_on_arity		1,5,carbon_copySB_descending_4_1
	table_entry		carbon_copySB_descending_4_3
	table_entry		carbon_copySB_descending_4_1
	table_entry		carbon_copySB_descending_4_1
	table_entry		carbon_copySB_descending_4_1
	table_entry		carbon_copySB_descending_4_4
carbon_copySB_descending_4_3:
	get_value		2,3
	put_vector		1,0
	get_vector_value		4,1
	proceed
carbon_copySB_descending_4_4:
	read_element		1,0,5
	read_element		1,1,11
	read_elements_inc		1,2,6,2
	wait_vector		11,3
	read_elements_inc		11,0,8,3
	get_nil		10
	put_reused_vector		10,11
	write_element_value		10,0,8
	write_element_variable		10,1,12
	write_element_variable		10,2,11
	put_reused_vector		13,1
	write_element_marked_value		13,0,5
	write_element_value		13,1,10
	write_element_variable		13,2,8
	write_element_variable		13,3,1
	get_vector_value		4,13
	create_goal		4
	set_value		1,6
	set_variable		2,4
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,carbon_copySB_descending_4_0
	create_goal		5
	set_value		1,9
	set_values_dec		2,12,2
	set_variable		4,1
	set_value		5,4
	enqueue_goal		5,carbon_copy_elementsSB_5_0
	put_list_val_val		3,5,1
	put_value		1,7
	put_value		4,8
	execute		4,carbon_copySB_descending_4_0
carbon_copySB_descending_4_1:
	suspend		carbon_copySB_descending_4_0
	module_entry		keyed_sorted_bag
	predicate		carbon_copy_elementsSB,5
carbon_copy_elementsSB_5_0:
	try_me_else		carbon_copy_elementsSB_5_1
	jump_on_non_list_var_var		1,carbon_copy_elementsSB_5_3,6,7
	put_reused_list		1,1
	write_car_marked_value		1,6
	write_cdr_variable		1,8
	get_list_value		2,1
	get_list_val_var		4,1,6,6
	put_values_inc		1,7,2
	put_value		4,6
	execute		5,carbon_copy_elementsSB_5_0
carbon_copy_elementsSB_5_3:
	check_nil		1,carbon_copy_elementsSB_5_1
	get_value		2,3
	get_value		4,5
	proceed
carbon_copy_elementsSB_5_1:
	suspend		carbon_copy_elementsSB_5_0
	module_entry		keyed_sorted_bag
	predicate		get_max_if_anySB,4
get_max_if_anySB_4_0:
	try_me_else		get_max_if_anySB_4_1
	jump_on_non_atom		4,get_max_if_anySB_4_3
	branch_on_atom		4,2,get_max_if_anySB_4_1
	bucket_entry_a		ascending,get_max_if_anySB_4_4
	bucket_entry_a		descending,get_max_if_anySB_4_5
get_max_if_anySB_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_anySB_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_max_if_anySB_4_3:
	check_vector		4,3,get_max_if_anySB_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_max_if_anySB_4_1:
	suspend		get_max_if_anySB_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_max_if_anySB,3
do_get_max_if_anySB_3_0:
	try_me_else		do_get_max_if_anySB_3_1
	vector		1
	jump_on_arity		1,5,do_get_max_if_anySB_3_1
	table_entry		do_get_max_if_anySB_3_3
	table_entry		do_get_max_if_anySB_3_1
	table_entry		do_get_max_if_anySB_3_1
	table_entry		do_get_max_if_anySB_3_1
	table_entry		do_get_max_if_anySB_3_4
do_get_max_if_anySB_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_max_if_anySB_3_4:
	read_elements_inc		1,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,do_get_max_if_anySB_3_7
	read_elements_inc		1,2,7,2
	read_elements_inc		5,1,9,2
	collect_value		8
	collect_value		10
	collect_value		9
	collect_vector		1
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	get_value		3,7
	proceed
do_get_max_if_anySB_3_7:
	read_elements_inc		1,2,7,2
	read_elements_inc		5,1,9,2
	put_integer		11,0
	g_less_than		11,6
	put_vector		11,1
	write_element_value		11,0,4
	get_vector_value		2,11
	put_list		2
	write_car_variable		2,12
	write_cdr_variable		2,11
	get_list_value		9,2
	b_decrement		6,2
	put_reused_vector		4,5
	write_element_value		4,0,2
	write_elements_dec		4,1,11,2
	put_reused_vector		1,1
	write_element_value		1,0,12
	write_element_value		1,1,4
	write_elements_inc		1,2,7,2
	get_vector_value		3,1
	proceed
do_get_max_if_anySB_3_1:
	suspend		do_get_max_if_anySB_3_0
	module_entry		keyed_sorted_bag
	predicate		get_min_if_anySB,4
get_min_if_anySB_4_0:
	try_me_else		get_min_if_anySB_4_1
	jump_on_non_atom		4,get_min_if_anySB_4_3
	branch_on_atom		4,2,get_min_if_anySB_4_1
	bucket_entry_a		ascending,get_min_if_anySB_4_4
	bucket_entry_a		descending,get_min_if_anySB_4_5
get_min_if_anySB_4_4:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_anySB_4_5:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_max_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_max_2_0
get_min_if_anySB_4_3:
	check_vector		4,3,get_min_if_anySB_4_1
	read_elements_inc		4,0,5,3
	atom		5
	atom		6
	integer		7
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,do_get_min_if_anySB_3_0
	put_value		2,4
	execute		2,splay_at_min_2_0
get_min_if_anySB_4_1:
	suspend		get_min_if_anySB_4_0
	module_entry		keyed_sorted_bag
	predicate		do_get_min_if_anySB,3
do_get_min_if_anySB_3_0:
	try_me_else		do_get_min_if_anySB_3_1
	vector		1
	jump_on_arity		1,5,do_get_min_if_anySB_3_1
	table_entry		do_get_min_if_anySB_3_3
	table_entry		do_get_min_if_anySB_3_1
	table_entry		do_get_min_if_anySB_3_1
	table_entry		do_get_min_if_anySB_3_1
	table_entry		do_get_min_if_anySB_3_4
do_get_min_if_anySB_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_get_min_if_anySB_3_4:
	read_elements_inc		1,0,4,2
	wait_vector		5,3
	read_element		5,0,6
	integer		6
	test_integer		6,0,do_get_min_if_anySB_3_7
	read_elements_inc		1,2,7,2
	read_elements_inc		5,1,9,2
	collect_value		7
	collect_value		10
	collect_value		9
	collect_vector		1
	collect_vector		5
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		2,1
	get_value		3,8
	proceed
do_get_min_if_anySB_3_7:
	read_elements_inc		1,2,7,2
	read_elements_inc		5,1,9,2
	put_integer		11,0
	g_less_than		11,6
	put_vector		11,1
	write_element_value		11,0,4
	get_vector_value		2,11
	put_list		2
	write_car_variable		2,12
	write_cdr_variable		2,11
	get_list_value		9,2
	b_decrement		6,2
	put_reused_vector		4,5
	write_element_value		4,0,2
	write_elements_dec		4,1,11,2
	put_reused_vector		1,1
	write_element_value		1,0,12
	write_element_value		1,1,4
	write_elements_inc		1,2,7,2
	get_vector_value		3,1
	proceed
do_get_min_if_anySB_3_1:
	suspend		do_get_min_if_anySB_3_0
	module_entry		keyed_sorted_bag
	predicate		data_countSB,3
data_countSB_3_0:
	put_value		5,2
	b_merge		2,4
	create_goal		3
	set_values_inc		1,1,3
	enqueue_goal		3,do_data_countSB_3_0
	put_value		1,4
	put_integer		2,0
	put_value		3,5
	execute		3,counter_3_0
data_countSB_3_1:
	suspend		data_countSB_3_0
	module_entry		keyed_sorted_bag
	predicate		do_data_countSB,3
do_data_countSB_3_0:
	try_me_else		do_data_countSB_3_1
	vector		1
	jump_on_arity		1,5,do_data_countSB_3_1
	table_entry		do_data_countSB_3_3
	table_entry		do_data_countSB_3_1
	table_entry		do_data_countSB_3_1
	table_entry		do_data_countSB_3_1
	table_entry		do_data_countSB_3_4
do_data_countSB_3_3:
	get_nil		2
	put_vector		1,0
	get_vector_value		3,1
	proceed
do_data_countSB_3_4:
	read_element		1,0,4
	read_element		1,1,13
	read_elements_inc		1,2,5,2
	wait_vector		13,3
	read_elements_inc		13,0,7,3
	put_marked_value		10,7
	b_increment		10,10
	get_list_val_var		2,11,10,10
	put_vector		2,2
	write_element_variable		2,0,12
	write_element_variable		2,1,11
	get_vector_value		10,2
	put_reused_vector		2,13
	write_elements_inc		2,0,7,3
	put_reused_vector		7,1
	write_element_value		7,0,4
	write_element_value		7,1,2
	write_element_variable		7,2,4
	write_element_variable		7,3,1
	get_vector_value		3,7
	create_goal		3
	set_value		1,6
	set_value		2,11
	set_value		3,1
	enqueue_goal		3,do_data_countSB_3_0
	put_value		1,5
	put_value		2,12
	put_value		3,4
	execute		3,do_data_countSB_3_0
do_data_countSB_3_1:
	suspend		do_data_countSB_3_0
	module_entry		keyed_sorted_bag
	predicate		down_for_getSB,3
down_for_getSB_3_0:
	try_me_else		down_for_getSB_3_1
	vector		1
	jump_on_arity		1,5,down_for_getSB_3_1
	table_entry		down_for_getSB_3_3
	table_entry		down_for_getSB_3_1
	table_entry		down_for_getSB_3_1
	table_entry		down_for_getSB_3_1
	table_entry		down_for_getSB_3_4
down_for_getSB_3_3:
	put_vector		1,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
down_for_getSB_3_4:
	read_elements_inc		1,0,4,2
	read_elements_dec		1,2,7,2
	wait_vector		7,0
	put_structured_constant		7,'$SCNST_12'
	put_reused_vector		1,1
	write_elements_inc		1,0,4,2
	write_elements_dec		1,2,7,2
	put_vector		4,2
	write_elements_inc		4,0,1,2
	get_vector_value		3,4
	proceed
down_for_getSB_3_1:
	otherwise		down_for_getSB_3_0
	try_me_else		down_for_getSB_3_7
	wait_vector		1,4
	read_elements_inc		1,0,4,4
	put_reused_vector		8,1
	write_elements_inc		8,0,4,2
	write_element_void		8,2
	write_element_value		8,3,7
	put_value		1,6
	put_value		4,8
	execute		4,downGSB_4_0
down_for_getSB_3_7:
	suspend		down_for_getSB_3_0
	module_entry		keyed_sorted_bag
	predicate		downGSB,4
downGSB_4_0:
	try_me_else		downGSB_4_1
	wait_vector		1,4
	read_elements_inc		1,0,5,2
	read_elements_dec		1,2,8,2
	wait_vector		8,0
	put_structured_constant		8,'$SCNST_13'
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_elements_dec		1,2,8,2
	put_vector		5,3
	write_element_value		5,0,1
	write_element_value		5,1,4
	write_element_value		5,2,2
	get_vector_value		3,5
	proceed
downGSB_4_1:
	otherwise		downGSB_4_0
	try_me_else		downGSB_4_6
	wait_vector		1,4
	read_elements_inc		1,0,5,4
	put_reused_vector		9,1
	write_elements_inc		9,0,5,2
	write_element_void		9,2
	write_element_value		9,3,8
	put_value		1,7
	put_value		5,9
	execute		5,downG_againSB_5_0
downGSB_4_6:
	suspend		downGSB_4_0
	module_entry		keyed_sorted_bag
	predicate		downG_againSB,5
downG_againSB_5_0:
	try_me_else		downG_againSB_5_1
	wait_vector		1,4
	read_elements_inc		1,0,6,2
	read_elements_dec		1,2,9,2
	wait_vector		9,0
	put_structured_constant		9,'$SCNST_14'
	put_reused_vector		1,1
	write_elements_inc		1,0,6,2
	write_elements_dec		1,2,9,2
	put_vector		6,4
	write_element_value		6,0,1
	write_elements_inc		6,1,4,2
	write_element_value		6,3,2
	get_vector_value		3,6
	proceed
downG_againSB_5_1:
	otherwise		downG_againSB_5_0
	try_me_else		downG_againSB_5_6
	wait_vector		1,4
	read_elements_inc		1,0,6,4
	put_value		11,2
	create_goal		4
	set_value		1,8
	put_reused_vector		12,1
	write_element_variable		12,0,10
	write_element_variable		12,1,8
	write_element_variable		12,2,2
	write_element_variable		12,3,1
	set_value		2,12
	set_value		3,3
	put_vector		3,4
	write_elements_inc		3,0,6,2
	write_element_void		3,2
	write_element_value		3,3,9
	set_value		4,3
	enqueue_goal		4,downGSB_4_0
	put_vector		3,4
	write_element_value		3,0,10
	write_element_value		3,1,8
	write_elements_dec		3,2,2,2
	put_atom		1,left
	put_atom		2,left
	put_value		6,11
	execute		6,splay_6_0
downG_againSB_5_6:
	suspend		downG_againSB_5_0
	begin_const_section		keyed_sorted_bag
'$SCNST_0_1':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_0_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_sorted_bag
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_1_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_sorted_bag
	define_string		'$SCNST_1_1'
'$SCNST_2':
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_3_0':
	define_desc		0,0
'$SCNST_14':
'$SCNST_13':
'$SCNST_12':
'$SCNST_6':
'$SCNST_5':
'$SCNST_4':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_7_1':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_7_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_sorted_set
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_8_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_sorted_set
	define_string		'$SCNST_8_1'
'$SCNST_9':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_10_1':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_10_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		sorted_bag
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_1':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_11_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		sorted_bag
	define_string		'$SCNST_11_1'
'$SCNST_11':
	define_vector		'$SCNST_11_0'
