keyed_bag:
	module		keyed_bag
	entry		keyed_bag,3,keyed_bag_3_0
	entry		keyed_set,3,keyed_set_3_0
	module_entry		keyed_bag
	predicate		keyed_bag,3
keyed_bag_3_0:
	try_me_else		keyed_bag_3_1
	integer		3
	put_integer		4,0
	g_less_than		4,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,4
	enqueue_goal		3,wait_table_size_3_0
	put_integer		1,1
	put_values_inc		2,3,2
	execute		3,get_table_size_3_0
keyed_bag_3_1:
	suspend		keyed_bag_3_0
	module_entry		keyed_bag
	predicate		wait_table_size,3
wait_table_size_3_0:
	try_me_else		wait_table_size_3_1
	wait		3
	put_marked_value		4,3
	b_new_vector		6,4
	b_merge		5,4
	get_value		5,2
	b_decrement		3,3
	put_value		2,4
	put_integer		4,0
	put_integer		5,0
	execute		6,keyed_bag_6_0
wait_table_size_3_1:
	suspend		wait_table_size_3_0
	module_entry		keyed_bag
	predicate		get_table_size,3
get_table_size_3_0:
	try_me_else		get_table_size_3_1
	integer		1
	integer		2
	try_me_else		get_table_size_3_4
	g_not_less_than		1,2
	get_value		3,1
	proceed
get_table_size_3_4:
	put_integer		4,1
	b_shift_left		1,4,1
	execute		3,get_table_size_3_0
get_table_size_3_1:
	suspend		get_table_size_3_0
	module_entry		keyed_bag
	predicate		keyed_bag,6
keyed_bag_6_0:
	try_me_else		keyed_bag_6_1
	jump_on_non_list		2,keyed_bag_6_3
	read_car		2,7
	jump_on_non_atom		7,keyed_bag_6_5
	test_atom		7,clear,keyed_bag_6_1
	read_cdr		2,8
	collect_list		2
	collect_value		6
	collect_value		5
	collect_value		4
	put_marked_value		2,3
	b_increment		2,2
	b_new_vector		6,2
	put_value		2,8
	put_integer		4,0
	put_integer		5,0
	execute		6,keyed_bag_6_0
keyed_bag_6_5:
	is_vector		7,keyed_bag_6_1
	jump_on_arity		7,6,keyed_bag_6_1
	table_entry		keyed_bag_6_1
	table_entry		keyed_bag_6_1
	table_entry		keyed_bag_6_6
	table_entry		keyed_bag_6_7
	table_entry		keyed_bag_6_8
	table_entry		keyed_bag_6_9
keyed_bag_6_6:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,7,keyed_bag_6_1
	bucket_entry_a		carbon_copy,keyed_bag_6_11
	bucket_entry_a		copy,keyed_bag_6_12
	bucket_entry_a		do,keyed_bag_6_13
	bucket_entry_a		empty,keyed_bag_6_14
	bucket_entry_a		get_all,keyed_bag_6_15
	bucket_entry_a		get_average_chaining_length,keyed_bag_6_16
	bucket_entry_a		get_load_factor,keyed_bag_6_17
keyed_bag_6_11:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,4
	enqueue_goal		6,keyed_bag_6_0
	put_value		1,3
	put_value		2,6
	put_value		3,4
	put_value		4,10
	execute		4,carbon_copy_4_0
keyed_bag_6_12:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_variable		6,7
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,4
	put_value		6,10
	execute		7,copy_keyed_bag_7_0
keyed_bag_6_13:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	b_merge		7,2
	get_value		7,10
	create_goal		6
	set_value		1,1
	set_variable		2,7
	set_values_inc		3,3,4
	enqueue_goal		6,keyed_bag_6_0
	put_value		1,2
	put_value		2,9
	put_value		3,7
	execute		3,prepend_3_0
keyed_bag_6_14:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_value		3,3
	set_marked_value		4,4
	set_values_inc		5,5,2
	enqueue_goal		6,keyed_bag_6_0
	put_value		1,4
	put_value		2,10
	execute		2,empty_2_0
keyed_bag_6_15:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_value		5
	collect_value		4
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_integer		4,0
	set_integer		5,0
	set_variable		6,4
	enqueue_goal		6,keyed_bag_6_0
	put_value		1,3
	put_value		2,6
	put_value		3,4
	put_value		4,10
	execute		4,get_all_4_0
keyed_bag_6_16:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_value		6,6
	enqueue_goal		6,keyed_bag_6_0
	put_values_dec		1,5,2
	put_value		3,10
	execute		3,get_average_chaining_length_3_0
keyed_bag_6_17:
	read_cdr		2,9
	read_element		7,1,10
	integer		3
	g_increment		3,11
	g_integer_to_float		11,11
	integer		4
	g_integer_to_float		4,12
	g_float_divide		12,11,8
	collect_list		2
	collect_vector		7
	get_value		10,8
	put_value		2,9
	execute		6,keyed_bag_6_0
keyed_bag_6_7:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,6,keyed_bag_6_1
	bucket_entry_a		carbon_copy,keyed_bag_6_19
	bucket_entry_a		empty,keyed_bag_6_20
	bucket_entry_a		get,keyed_bag_6_21
	bucket_entry_a		get_all,keyed_bag_6_22
	bucket_entry_a		get_if_any,keyed_bag_6_23
	bucket_entry_a		put,keyed_bag_6_24
keyed_bag_6_19:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_bag_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,10,2
	put_value		6,7
	execute		6,carbon_copy_6_0
keyed_bag_6_20:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	put_value		8,3
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,8
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,10,2
	put_value		4,8
	put_values_inc		5,6,2
	execute		6,empty_6_0
keyed_bag_6_21:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	b_decrement		5,2
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,7
	set_value		5,2
	set_variable		6,8
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,2
	put_value		4,6
	put_values_inc		5,10,2
	put_atom		9,bag
	execute		9,get_9_0
keyed_bag_6_22:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,8
	set_variable		5,9
	set_variable		6,12
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,2
	put_value		10,12
	execute		10,get_all_10_0
keyed_bag_6_23:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,8
	set_variable		5,9
	set_variable		6,12
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,2
	put_value		10,12
	execute		10,get_if_any_10_0
keyed_bag_6_24:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_variable		3,8
	set_variable		4,9
	set_variable		5,13
	set_variable		6,12
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,2
	put_values_dec		10,13,2
	execute		11,put_11_0
keyed_bag_6_8:
	read_element		7,0,8
	atom		8
	branch_on_atom		8,2,keyed_bag_6_1
	bucket_entry_a		get_and_put,keyed_bag_6_26
	bucket_entry_a		get_if_any_and_put,keyed_bag_6_27
keyed_bag_6_26:
	read_cdr		2,9
	read_elements_inc		7,1,10,3
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_bag_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,10,3
	put_atom		8,bag
	execute		8,get_and_put_8_0
keyed_bag_6_27:
	read_cdr		2,9
	read_elements_inc		7,1,10,3
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_variable		3,9
	set_variable		4,15
	set_variable		5,14
	set_variable		6,13
	enqueue_goal		6,keyed_bag_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,3
	put_values_dec		10,15,3
	execute		12,get_if_any_and_put_12_0
keyed_bag_6_9:
	read_cdr		2,8
	read_element		7,0,9
	wait_atom		9,get_and_put_if_any
	read_elements_inc		7,1,9,4
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,8
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,8
	enqueue_goal		6,keyed_bag_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,9,4
	execute		8,get_and_put_if_any_8_0
keyed_bag_6_3:
	check_nil		2,keyed_bag_6_1
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		1
	proceed
keyed_bag_6_1:
	otherwise		keyed_bag_6_0
	try_me_else		keyed_bag_6_42
	wait_list_var_var		2,7,8
	collect_list		2
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		8
	collect_value		1
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_0'
	b_raise		2,1,7
	proceed
keyed_bag_6_42:
	suspend		keyed_bag_6_0
	module_entry		keyed_bag
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
	module_entry		keyed_bag
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
	module_entry		keyed_bag
	predicate		empty,6
empty_6_0:
	try_me_else		empty_6_1
	wait_atom		1,default
	wait		2
	switch_on_type		2,empty_6_3,empty_6_4,empty_6_1,empty_6_1,empty_6_1,empty_6_5
empty_6_3:
	g_tag_and_value		2,7,8
	integer		4
	g_and		8,4,1
	put_variable		7,4
	b_set_vector_element		5,1,1,7,5
	get_value		5,6
	execute		4,if_empty_4_0
empty_6_4:
	put_integer		7,0
	g_not_less_than		2,7
	integer		4
	g_and		2,4,1
	put_variable		7,4
	b_set_vector_element		5,1,1,7,5
	get_value		5,6
	execute		4,if_empty_4_0
empty_6_5:
	is_float		2,empty_6_1
	put_float		7,0.0
	g_float_not_less_than		2,7
	g_float_to_integer		2,7
	integer		4
	g_and		7,4,1
	put_variable		7,4
	b_set_vector_element		5,1,1,7,5
	get_value		5,6
	execute		4,if_empty_4_0
empty_6_1:
	otherwise		empty_6_0
	try_me_else		empty_6_10
	jump_on_non_atom		1,empty_6_12
	test_atom		1,default,empty_6_10
	create_goal		6
	set_variable		1,8
	set_variable		2,7
	set_values_inc		3,3,4
	enqueue_goal		6,empty_wait_hashed_value_6_0
	put_value		1,2
	put_values_dec		2,8,2
	execute_external		hasher,hash,3
empty_6_12:
	check_vector		1,3,empty_6_10
	read_elements_inc		1,0,7,3
	atom		7
	atom		8
	integer		9
	put_reused_vector		1,1
	write_elements_inc		1,0,7,3
	put_vector		7,3
	write_element_value		7,0,2
	write_element_variable		7,1,8
	write_element_variable		7,2,2
	b_apply		1,7
	put_value		1,8
	execute		6,empty_wait_hashed_value_6_0
empty_6_10:
	suspend		empty_6_0
	module_entry		keyed_bag
	predicate		empty_wait_hashed_value,6
empty_wait_hashed_value_6_0:
	try_me_else		empty_wait_hashed_value_6_1
	integer		1
	integer		4
	g_and		1,4,1
	put_variable		7,4
	b_set_vector_element		5,1,1,7,5
	get_value		5,6
	execute		4,if_empty_4_0
empty_wait_hashed_value_6_1:
	suspend		empty_wait_hashed_value_6_0
	module_entry		keyed_bag
	predicate		if_empty,4
if_empty_4_0:
	try_me_else		if_empty_4_1
	jump_on_non_integer		1,if_empty_4_3
	test_integer		1,0,if_empty_4_1
	collect_value		2
	get_atom		3,yes
	get_integer		4,0
	proceed
if_empty_4_3:
	check_vector		1,3,if_empty_4_1
	read_elements_inc		1,0,5,3
	wait_value		5,2
	collect_value		2
	get_atom		3,no
	put_reused_vector		1,1
	write_elements_inc		1,0,5,3
	get_vector_value		4,1
	proceed
if_empty_4_1:
	otherwise		if_empty_4_0
	try_me_else		if_empty_4_9
	wait_vector		1,3
	read_elements_inc		1,0,5,3
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,5
	get_vector_value		4,1
	put_value		1,7
	put_value		4,5
	execute		4,if_empty_4_0
if_empty_4_9:
	suspend		if_empty_4_0
	module_entry		keyed_bag
	predicate		put,11
put_11_0:
	try_me_else		put_11_1
	integer		2
	g_increment		2,12
	put_integer		13,1
	g_shift_right		12,13,13
	put_integer		14,2
	g_shift_right		12,14,12
	g_add		13,12,12
	integer		3
	g_less_than		3,12
	put_marked_value		8,8
	get_value		8,2
	b_increment		4,2
	get_value		10,2
	put_value		2,8
	put_values_inc		4,5,3
	put_value		7,9
	put_value		8,11
	execute		8,do_put_8_0
put_11_1:
	otherwise		put_11_0
	collect_value		3
	b_increment		4,3
	get_value		10,3
	create_goal		8
	set_marked_value		1,1
	set_marked_value		2,8
	set_variable		3,12
	set_variable		4,10
	set_values_inc		5,6,2
	set_value		7,9
	set_value		8,11
	enqueue_goal		8,do_put_8_0
	put_value		3,5
	put_value		4,8
	put_value		5,12
	put_value		6,10
	execute		6,rehash_6_0
put_11_5:
	suspend		put_11_0
	module_entry		keyed_bag
	predicate		do_put,8
do_put_8_0:
	try_me_else		do_put_8_1
	wait_atom		1,default
	integer		2
	wait		5
	switch_on_type		5,do_put_8_4,do_put_8_5,do_put_8_1,do_put_8_1,do_put_8_1,do_put_8_6
do_put_8_4:
	g_tag_and_value		5,9,10
	g_and		10,2,1
	put_vector		2,3
	write_elements_inc		2,0,5,2
	write_element_variable		2,2,5
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_value		2,5
	put_value		4,7
	execute		4,get_m_cnt_4_0
do_put_8_5:
	put_integer		9,0
	g_not_less_than		5,9
	g_and		5,2,1
	put_vector		2,3
	write_elements_inc		2,0,5,2
	write_element_variable		2,2,5
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_value		2,5
	put_value		4,7
	execute		4,get_m_cnt_4_0
do_put_8_6:
	is_float		5,do_put_8_1
	put_float		9,0.0
	g_float_not_less_than		5,9
	g_float_to_integer		5,9
	g_and		9,2,1
	put_vector		2,3
	write_elements_inc		2,0,5,2
	write_element_variable		2,2,5
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_value		2,5
	put_value		4,7
	execute		4,get_m_cnt_4_0
do_put_8_1:
	otherwise		do_put_8_0
	try_me_else		do_put_8_12
	jump_on_non_atom		1,do_put_8_14
	test_atom		1,default,do_put_8_12
	create_goal		8
	set_variable		1,9
	set_values_inc		2,2,3
	set_variable		5,3
	set_values_inc		6,6,3
	enqueue_goal		8,put_wait_hashed_value_8_0
	put_value		1,5
	put_value		2,9
	execute_external		hasher,hash,3
do_put_8_14:
	check_vector		1,3,do_put_8_12
	read_elements_inc		1,0,9,3
	atom		9
	atom		10
	integer		11
	put_reused_vector		1,1
	write_elements_inc		1,0,9,3
	put_vector		9,3
	write_element_value		9,0,5
	write_element_variable		9,1,10
	write_element_variable		9,2,5
	b_apply		1,9
	put_value		1,10
	execute		8,put_wait_hashed_value_8_0
do_put_8_12:
	suspend		do_put_8_0
	module_entry		keyed_bag
	predicate		put_wait_hashed_value,8
put_wait_hashed_value_8_0:
	try_me_else		put_wait_hashed_value_8_1
	integer		1
	integer		2
	g_and		1,2,1
	put_vector		2,3
	write_elements_inc		2,0,5,2
	write_element_variable		2,2,5
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_value		2,5
	put_value		4,7
	execute		4,get_m_cnt_4_0
put_wait_hashed_value_8_1:
	suspend		put_wait_hashed_value_8_0
	module_entry		keyed_bag
	predicate		get_m_cnt,4
get_m_cnt_4_0:
	try_me_else		get_m_cnt_4_1
	wait_integer		1,0
	get_integer		2,0
	b_increment		3,1
	get_value		4,1
	proceed
get_m_cnt_4_1:
	otherwise		get_m_cnt_4_0
	get_value		1,2
	get_value		4,3
	proceed
get_m_cnt_4_6:
	suspend		get_m_cnt_4_0
	module_entry		keyed_bag
	predicate		rehash,6
rehash_6_0:
	try_me_else		rehash_6_1
	integer		2
	g_increment		2,7
	put_integer		8,1
	g_shift_left		7,8,7
	put_value		9,5
	put_value		8,6
	put_marked_value		5,7
	b_decrement		5,5
	put_marked_value		4,4
	get_value		4,5
	b_new_vector		7,7
	put_integer		5,0
	put_value		6,9
	execute		8,do_rehash_8_0
rehash_6_1:
	suspend		rehash_6_0
	module_entry		keyed_bag
	predicate		do_rehash,8
do_rehash_8_0:
	try_me_else		do_rehash_8_1
	integer		2
	try_me_else		do_rehash_8_3
	put_integer		9,0
	g_not_less_than		2,9
	put_value		11,1
	put_marked_value		1,2
	put_integer		9,0
	b_set_vector_element		3,1,1,9,3
	b_decrement		2,2
	create_goal		8
	set_marked_value		1,11
	set_values_inc		2,2,2
	set_marked_value		4,4
	set_variable		5,10
	set_value		6,6
	set_variable		7,9
	set_value		8,8
	enqueue_goal		8,do_rehash_8_0
	put_value		2,11
	put_values_inc		3,4,2
	put_value		5,10
	put_value		6,7
	put_value		7,9
	execute		7,rehash_each_entry_7_0
do_rehash_8_3:
	collect_value		4
	collect_value		3
	collect_value		1
	get_value		6,5
	get_value		8,7
	proceed
do_rehash_8_1:
	suspend		do_rehash_8_0
	module_entry		keyed_bag
	predicate		rehash_each_entry,7
rehash_each_entry_7_0:
	try_me_else		rehash_each_entry_7_1
	jump_on_non_integer		1,rehash_each_entry_7_3
	test_integer		1,0,rehash_each_entry_7_1
	collect_value		3
	collect_value		2
	get_value		5,4
	get_value		7,6
	proceed
rehash_each_entry_7_3:
	check_vector		1,3,rehash_each_entry_7_1
	read_element		1,0,8
	wait		8
	switch_on_type		8,rehash_each_entry_7_4,rehash_each_entry_7_5,rehash_each_entry_7_1,rehash_each_entry_7_1,rehash_each_entry_7_1,rehash_each_entry_7_6
rehash_each_entry_7_4:
	read_elements_inc		1,1,9,2
	wait_atom		2,default
	g_tag_and_value		8,11,12
	integer		3
	g_and		12,3,2
	put_reused_vector		1,1
	write_elements_inc		1,0,8,2
	write_element_variable		1,2,8
	b_set_vector_element		6,2,1,1,2
	create_goal		7
	set_value		1,10
	set_atom		2,default
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	set_value		6,2
	set_value		7,7
	enqueue_goal		7,rehash_each_entry_7_0
	put_value		2,8
	put_value		3,4
	put_value		4,6
	execute		4,get_m_cnt_4_0
rehash_each_entry_7_5:
	read_elements_inc		1,1,9,2
	wait_atom		2,default
	put_integer		11,0
	g_not_less_than		8,11
	integer		3
	g_and		8,3,2
	put_reused_vector		1,1
	write_elements_inc		1,0,8,2
	write_element_variable		1,2,8
	b_set_vector_element		6,2,1,1,2
	create_goal		7
	set_value		1,10
	set_atom		2,default
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	set_value		6,2
	set_value		7,7
	enqueue_goal		7,rehash_each_entry_7_0
	put_value		2,8
	put_value		3,4
	put_value		4,6
	execute		4,get_m_cnt_4_0
rehash_each_entry_7_6:
	is_float		8,rehash_each_entry_7_1
	read_elements_inc		1,1,9,2
	wait_atom		2,default
	put_float		11,0.0
	g_float_not_less_than		8,11
	g_float_to_integer		8,11
	integer		3
	g_and		11,3,2
	put_reused_vector		1,1
	write_elements_inc		1,0,8,2
	write_element_variable		1,2,8
	b_set_vector_element		6,2,1,1,2
	create_goal		7
	set_value		1,10
	set_atom		2,default
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	set_value		6,2
	set_value		7,7
	enqueue_goal		7,rehash_each_entry_7_0
	put_value		2,8
	put_value		3,4
	put_value		4,6
	execute		4,get_m_cnt_4_0
rehash_each_entry_7_1:
	otherwise		rehash_each_entry_7_0
	try_me_else		rehash_each_entry_7_14
	wait_vector		1,3
	read_elements_inc		1,0,8,3
	jump_on_non_atom		2,rehash_each_entry_7_17
	test_atom		2,default,rehash_each_entry_7_14
	create_goal		8
	put_reused_vector		1,1
	write_element_variable		1,0,11
	write_elements_inc		1,1,9,2
	set_value		1,1
	set_atom		2,default
	set_values_inc		3,3,5
	set_variable		8,2
	enqueue_goal		8,rehash_wait_hashed_value_8_0
	put_value		1,8
	put_value		3,11
	execute_external		hasher,hash,3
rehash_each_entry_7_17:
	check_vector		2,3,rehash_each_entry_7_14
	read_elements_inc		2,0,11,3
	atom		11
	atom		12
	integer		13
	put_reused_vector		1,1
	write_element_marked_value		1,0,11
	write_element_marked_value		1,1,12
	write_element_marked_value		1,2,13
	put_reused_vector		2,2
	write_element_value		2,0,8
	write_element_variable		2,1,8
	write_element_variable		2,2,14
	b_apply		1,2
	put_vector		1,3
	write_element_value		1,0,14
	write_elements_inc		1,1,9,2
	put_vector		2,3
	write_elements_inc		2,0,11,3
	execute		8,rehash_wait_hashed_value_8_0
rehash_each_entry_7_14:
	suspend		rehash_each_entry_7_0
	module_entry		keyed_bag
	predicate		rehash_wait_hashed_value,8
rehash_wait_hashed_value_8_0:
	try_me_else		rehash_wait_hashed_value_8_1
	wait_vector		1,3
	read_elements_inc		1,0,9,3
	integer		8
	integer		3
	g_and		8,3,8
	put_reused_vector		1,1
	write_elements_inc		1,0,9,2
	write_element_variable		1,2,9
	b_set_vector_element		6,8,1,1,6
	create_goal		7
	set_value		1,11
	set_values_inc		2,2,2
	set_variable		4,8
	set_values_inc		5,5,3
	enqueue_goal		7,rehash_each_entry_7_0
	put_value		2,9
	put_value		3,4
	put_value		4,8
	execute		4,get_m_cnt_4_0
rehash_wait_hashed_value_8_1:
	suspend		rehash_wait_hashed_value_8_0
	module_entry		keyed_bag
	predicate		get,9
get_9_0:
	try_me_else		get_9_1
	wait_atom		1,default
	integer		2
	wait		5
	switch_on_type		5,get_9_4,get_9_5,get_9_1,get_9_1,get_9_1,get_9_6
get_9_4:
	g_tag_and_value		5,10,11
	g_and		11,2,1
	put_value		11,3
	put_variable		2,10
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_values_inc		2,5,2
	put_values_inc		4,10,2
	put_value		6,7
	put_atom		7,off
	put_value		8,9
	execute		8,do_get_8_0
get_9_5:
	put_integer		10,0
	g_not_less_than		5,10
	g_and		5,2,1
	put_value		11,3
	put_variable		2,10
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_values_inc		2,5,2
	put_values_inc		4,10,2
	put_value		6,7
	put_atom		7,off
	put_value		8,9
	execute		8,do_get_8_0
get_9_6:
	is_float		5,get_9_1
	put_float		10,0.0
	g_float_not_less_than		5,10
	g_float_to_integer		5,10
	g_and		10,2,1
	put_value		11,3
	put_variable		2,10
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_values_inc		2,5,2
	put_values_inc		4,10,2
	put_value		6,7
	put_atom		7,off
	put_value		8,9
	execute		8,do_get_8_0
get_9_1:
	otherwise		get_9_0
	try_me_else		get_9_12
	jump_on_non_atom		1,get_9_14
	test_atom		1,default,get_9_12
	create_goal		9
	set_variable		1,10
	set_values_inc		2,2,3
	set_variable		5,3
	set_values_inc		6,6,4
	enqueue_goal		9,get_wait_hashed_value_9_0
	put_value		1,5
	put_value		2,10
	execute_external		hasher,hash,3
get_9_14:
	check_vector		1,3,get_9_12
	read_elements_inc		1,0,10,3
	atom		10
	atom		11
	integer		12
	put_reused_vector		1,1
	write_elements_inc		1,0,10,3
	put_vector		10,3
	write_element_value		10,0,5
	write_element_variable		10,1,11
	write_element_variable		10,2,5
	b_apply		1,10
	put_value		1,11
	execute		9,get_wait_hashed_value_9_0
get_9_12:
	suspend		get_9_0
	module_entry		keyed_bag
	predicate		get_wait_hashed_value,9
get_wait_hashed_value_9_0:
	try_me_else		get_wait_hashed_value_9_1
	integer		1
	integer		2
	g_and		1,2,1
	put_value		11,3
	put_variable		2,10
	b_set_vector_element		4,1,1,2,2
	get_value		2,8
	put_values_inc		2,5,2
	put_values_inc		4,10,2
	put_value		6,7
	put_atom		7,off
	put_value		8,9
	execute		8,do_get_8_0
get_wait_hashed_value_9_1:
	suspend		get_wait_hashed_value_9_0
	module_entry		keyed_bag
	predicate		do_get,8
do_get_8_0:
	try_me_else		do_get_8_1
	wait_vector		1,3
	read_elements_inc		1,0,9,3
	wait_value		9,2
	collect_value		8
	collect_value		9
	collect_value		2
	collect_vector		1
	get_value		3,10
	put_value		1,7
	put_value		2,11
	put_values_inc		3,4,3
	execute		5,if_subtract_entry_number_5_0
do_get_8_1:
	otherwise		do_get_8_0
	try_me_else		do_get_8_6
	jump_on_non_integer		1,do_get_8_8
	test_integer		1,0,do_get_8_6
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	put_func		4,3,get
	write_elements_inc		4,1,2,2
	put_value		1,8
	put_value		2,4
	execute		2,raise_error_2_0
do_get_8_8:
	check_vector		1,3,do_get_8_6
	read_elements_inc		1,0,9,3
	collect_value		7
	put_reused_vector		1,1
	write_elements_inc		1,0,9,2
	write_element_variable		1,2,7
	get_vector_value		4,1
	put_value		1,11
	put_value		4,7
	put_atom		7,on
	execute		8,do_get_8_0
do_get_8_6:
	suspend		do_get_8_0
	module_entry		keyed_bag
	predicate		if_subtract_entry_number,5
if_subtract_entry_number_5_0:
	try_me_else		if_subtract_entry_number_5_1
	wait_atom		1,off
	wait_integer		2,0
	get_integer		3,0
	b_decrement		4,1
	get_value		5,1
	proceed
if_subtract_entry_number_5_1:
	otherwise		if_subtract_entry_number_5_0
	collect_value		1
	get_value		3,2
	get_value		5,4
	proceed
if_subtract_entry_number_5_6:
	suspend		if_subtract_entry_number_5_0
	module_entry		keyed_bag
	predicate		raise_error,2
raise_error_2_0:
	try_me_else		raise_error_2_1
	atom		1
	branch_on_atom		1,2,raise_error_2_1
	bucket_entry_a		bag,raise_error_2_3
	bucket_entry_a		set,raise_error_2_4
raise_error_2_3:
	put_integer		3,1024
	put_structured_constant		1,'$SCNST_1'
	b_raise		3,1,2
	proceed
raise_error_2_4:
	put_integer		3,1024
	put_structured_constant		1,'$SCNST_2'
	b_raise		3,1,2
	proceed
raise_error_2_1:
	suspend		raise_error_2_0
	module_entry		keyed_bag
	predicate		get_all,4
get_all_4_0:
	try_me_else		get_all_4_1
	integer		1
	try_me_else		get_all_4_3
	put_integer		5,0
	g_not_less_than		1,5
	put_marked_value		5,1
	put_integer		6,0
	b_set_vector_element		2,5,2,6,5
	b_decrement		1,1
	create_goal		4
	set_value		1,1
	set_value		2,5
	set_value		3,3
	set_variable		4,3
	enqueue_goal		4,get_all_4_0
	put_value		1,2
	put_value		2,4
	execute		3,get_entry_3_0
get_all_4_3:
	get_value		2,3
	get_nil		4
	proceed
get_all_4_1:
	suspend		get_all_4_0
	module_entry		keyed_bag
	predicate		get_entry,3
get_entry_3_0:
	try_me_else		get_entry_3_1
	jump_on_non_integer		1,get_entry_3_3
	test_integer		1,0,get_entry_3_1
	get_value		2,3
	proceed
get_entry_3_3:
	check_vector		1,3,get_entry_3_1
	read_elements_inc		1,0,4,3
	collect_vector		1
	put_vector		1,2
	write_elements_inc		1,0,4,2
	get_list_val_var		2,5,1,4
	put_value		1,6
	put_value		2,4
	execute		3,get_entry_3_0
get_entry_3_1:
	suspend		get_entry_3_0
	module_entry		keyed_bag
	predicate		get_all,10
get_all_10_0:
	try_me_else		get_all_10_1
	wait_atom		1,default
	integer		2
	wait		6
	switch_on_type		6,get_all_10_4,get_all_10_5,get_all_10_1,get_all_10_1,get_all_10_1,get_all_10_6
get_all_10_4:
	g_tag_and_value		6,11,12
	g_and		12,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,get_entry_with_key_9_0
get_all_10_5:
	put_integer		11,0
	g_not_less_than		6,11
	g_and		6,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,get_entry_with_key_9_0
get_all_10_6:
	is_float		6,get_all_10_1
	put_float		11,0.0
	g_float_not_less_than		6,11
	g_float_to_integer		6,11
	g_and		11,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,get_entry_with_key_9_0
get_all_10_1:
	otherwise		get_all_10_0
	try_me_else		get_all_10_12
	jump_on_non_atom		1,get_all_10_14
	test_atom		1,default,get_all_10_12
	create_goal		10
	set_variable		1,11
	set_values_inc		2,2,4
	set_variable		6,3
	set_values_inc		7,7,4
	enqueue_goal		10,get_all_wait_hashed_value_10_0
	put_value		1,6
	put_value		2,11
	execute_external		hasher,hash,3
get_all_10_14:
	check_vector		1,3,get_all_10_12
	read_elements_inc		1,0,11,3
	atom		11
	atom		12
	integer		13
	put_reused_vector		1,1
	write_elements_inc		1,0,11,3
	put_vector		11,3
	write_element_value		11,0,6
	write_element_variable		11,1,12
	write_element_variable		11,2,6
	b_apply		1,11
	put_value		1,12
	execute		10,get_all_wait_hashed_value_10_0
get_all_10_12:
	suspend		get_all_10_0
	module_entry		keyed_bag
	predicate		get_all_wait_hashed_value,10
get_all_wait_hashed_value_10_0:
	try_me_else		get_all_wait_hashed_value_10_1
	integer		1
	integer		2
	g_and		1,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,get_entry_with_key_9_0
get_all_wait_hashed_value_10_1:
	suspend		get_all_wait_hashed_value_10_0
	module_entry		keyed_bag
	predicate		get_entry_with_key,9
get_entry_with_key_9_0:
	try_me_else		get_entry_with_key_9_1
	wait_vector		1,3
	read_elements_inc		1,0,10,3
	wait_value		10,2
	collect_value		2
	collect_vector		1
	get_list_val_var		3,1,11,11
	b_decrement		7,7
	put_value		1,12
	put_values_inc		2,10,2
	execute		9,get_entry_with_key_9_0
get_entry_with_key_9_1:
	otherwise		get_entry_with_key_9_0
	try_me_else		get_entry_with_key_9_6
	jump_on_non_integer		1,get_entry_with_key_9_8
	test_integer		1,0,get_entry_with_key_9_6
	collect_value		2
	get_nil		3
	get_integer		4,0
	get_value		8,7
	put_value		1,9
	put_values_inc		2,5,2
	execute		3,if_subtract_entry_number_3_0
get_entry_with_key_9_8:
	check_vector		1,3,get_entry_with_key_9_6
	read_elements_inc		1,0,10,3
	collect_value		9
	put_reused_vector		1,1
	write_elements_inc		1,0,10,2
	write_element_variable		1,2,9
	get_vector_value		4,1
	put_value		1,12
	put_value		4,9
	put_atom		9,on
	execute		9,get_entry_with_key_9_0
get_entry_with_key_9_6:
	suspend		get_entry_with_key_9_0
	module_entry		keyed_bag
	predicate		if_subtract_entry_number,3
if_subtract_entry_number_3_0:
	try_me_else		if_subtract_entry_number_3_1
	atom		1
	branch_on_atom		1,2,if_subtract_entry_number_3_1
	bucket_entry_a		off,if_subtract_entry_number_3_3
	bucket_entry_a		on,if_subtract_entry_number_3_4
if_subtract_entry_number_3_3:
	b_decrement		2,1
	get_value		3,1
	proceed
if_subtract_entry_number_3_4:
	get_value		3,2
	proceed
if_subtract_entry_number_3_1:
	suspend		if_subtract_entry_number_3_0
	module_entry		keyed_bag
	predicate		get_and_put,8
get_and_put_8_0:
	try_me_else		get_and_put_8_1
	wait_atom		1,default
	integer		2
	wait		4
	switch_on_type		4,get_and_put_8_4,get_and_put_8_5,get_and_put_8_1,get_and_put_8_1,get_and_put_8_1,get_and_put_8_6
get_and_put_8_4:
	g_tag_and_value		4,9,10
	g_and		10,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,7
	put_values_inc		2,4,3
	put_values_dec		5,9,2
	execute		6,do_get_and_put_6_0
get_and_put_8_5:
	put_integer		9,0
	g_not_less_than		4,9
	g_and		4,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,7
	put_values_inc		2,4,3
	put_values_dec		5,9,2
	execute		6,do_get_and_put_6_0
get_and_put_8_6:
	is_float		4,get_and_put_8_1
	put_float		9,0.0
	g_float_not_less_than		4,9
	g_float_to_integer		4,9
	g_and		9,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,7
	put_values_inc		2,4,3
	put_values_dec		5,9,2
	execute		6,do_get_and_put_6_0
get_and_put_8_1:
	otherwise		get_and_put_8_0
	try_me_else		get_and_put_8_12
	jump_on_non_atom		1,get_and_put_8_14
	test_atom		1,default,get_and_put_8_12
	create_goal		8
	set_variable		1,9
	set_values_inc		2,2,2
	set_variable		4,3
	set_values_inc		5,5,4
	enqueue_goal		8,get_and_put_wait_hashed_value_8_0
	put_value		1,4
	put_value		2,9
	execute_external		hasher,hash,3
get_and_put_8_14:
	check_vector		1,3,get_and_put_8_12
	read_elements_inc		1,0,9,3
	atom		9
	atom		10
	integer		11
	put_reused_vector		1,1
	write_elements_inc		1,0,9,3
	put_vector		9,3
	write_element_value		9,0,4
	write_element_variable		9,1,10
	write_element_variable		9,2,4
	b_apply		1,9
	put_value		1,10
	execute		8,get_and_put_wait_hashed_value_8_0
get_and_put_8_12:
	suspend		get_and_put_8_0
	module_entry		keyed_bag
	predicate		get_and_put_wait_hashed_value,8
get_and_put_wait_hashed_value_8_0:
	try_me_else		get_and_put_wait_hashed_value_8_1
	integer		1
	integer		2
	g_and		1,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,7
	put_values_inc		2,4,3
	put_values_dec		5,9,2
	execute		6,do_get_and_put_6_0
get_and_put_wait_hashed_value_8_1:
	suspend		get_and_put_wait_hashed_value_8_0
	module_entry		keyed_bag
	predicate		do_get_and_put,6
do_get_and_put_6_0:
	try_me_else		do_get_and_put_6_1
	wait_vector		1,3
	read_elements_inc		1,0,7,3
	wait_value		7,2
	collect_value		6
	collect_value		2
	get_value		3,8
	put_reused_vector		1,1
	write_element_value		1,0,7
	write_element_value		1,1,4
	write_element_value		1,2,9
	get_vector_value		5,1
	proceed
do_get_and_put_6_1:
	otherwise		do_get_and_put_6_0
	try_me_else		do_get_and_put_6_6
	jump_on_non_integer		1,do_get_and_put_6_8
	test_integer		1,0,do_get_and_put_6_6
	collect_value		5
	put_func		5,4,get_and_put
	write_elements_inc		5,1,2,3
	put_values_dec		1,6,2
	execute		2,raise_error_2_0
do_get_and_put_6_8:
	check_vector		1,3,do_get_and_put_6_6
	read_elements_inc		1,0,7,3
	put_reused_vector		1,1
	write_elements_inc		1,0,7,2
	write_element_variable		1,2,7
	get_vector_value		5,1
	put_value		1,9
	put_value		5,7
	execute		6,do_get_and_put_6_0
do_get_and_put_6_6:
	suspend		do_get_and_put_6_0
	module_entry		keyed_bag
	predicate		get_if_any,10
get_if_any_10_0:
	try_me_else		get_if_any_10_1
	wait_atom		1,default
	integer		2
	wait		6
	switch_on_type		6,get_if_any_10_4,get_if_any_10_5,get_if_any_10_1,get_if_any_10_1,get_if_any_10_1,get_if_any_10_6
get_if_any_10_4:
	g_tag_and_value		6,11,12
	g_and		12,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,do_get_if_any_9_0
get_if_any_10_5:
	put_integer		11,0
	g_not_less_than		6,11
	g_and		6,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,do_get_if_any_9_0
get_if_any_10_6:
	is_float		6,get_if_any_10_1
	put_float		11,0.0
	g_float_not_less_than		6,11
	g_float_to_integer		6,11
	g_and		11,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,do_get_if_any_9_0
get_if_any_10_1:
	otherwise		get_if_any_10_0
	try_me_else		get_if_any_10_12
	jump_on_non_atom		1,get_if_any_10_14
	test_atom		1,default,get_if_any_10_12
	create_goal		10
	set_variable		1,11
	set_values_inc		2,2,4
	set_variable		6,3
	set_values_inc		7,7,4
	enqueue_goal		10,get_if_any_wait_hashed_value_10_0
	put_value		1,6
	put_value		2,11
	execute_external		hasher,hash,3
get_if_any_10_14:
	check_vector		1,3,get_if_any_10_12
	read_elements_inc		1,0,11,3
	atom		11
	atom		12
	integer		13
	put_reused_vector		1,1
	write_elements_inc		1,0,11,3
	put_vector		11,3
	write_element_value		11,0,6
	write_element_variable		11,1,12
	write_element_variable		11,2,6
	b_apply		1,11
	put_value		1,12
	execute		10,get_if_any_wait_hashed_value_10_0
get_if_any_10_12:
	suspend		get_if_any_10_0
	module_entry		keyed_bag
	predicate		get_if_any_wait_hashed_value,10
get_if_any_wait_hashed_value_10_0:
	try_me_else		get_if_any_wait_hashed_value_10_1
	integer		1
	integer		2
	g_and		1,2,1
	put_values_inc		11,3,2
	put_variable		2,4
	b_set_vector_element		5,1,1,2,2
	get_value		2,10
	put_values_inc		2,6,2
	put_value		5,11
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_atom		9,off
	execute		9,do_get_if_any_9_0
get_if_any_wait_hashed_value_10_1:
	suspend		get_if_any_wait_hashed_value_10_0
	module_entry		keyed_bag
	predicate		do_get_if_any,9
do_get_if_any_9_0:
	try_me_else		do_get_if_any_9_1
	wait_vector		1,3
	read_elements_inc		1,0,10,3
	wait_value		10,2
	collect_value		10
	collect_value		2
	collect_vector		1
	put_vector		1,1
	write_element_value		1,0,11
	get_vector_value		3,1
	b_decrement		7,1
	get_value		8,1
	put_value		1,9
	put_value		2,12
	put_values_inc		3,4,3
	execute		5,if_subtract_entry_number_5_0
do_get_if_any_9_1:
	otherwise		do_get_if_any_9_0
	try_me_else		do_get_if_any_9_6
	jump_on_non_integer		1,do_get_if_any_9_8
	test_integer		1,0,do_get_if_any_9_6
	collect_value		9
	collect_value		2
	put_vector		1,0
	get_vector_value		3,1
	get_integer		4,0
	get_value		6,5
	get_value		8,7
	proceed
do_get_if_any_9_8:
	check_vector		1,3,do_get_if_any_9_6
	read_elements_inc		1,0,10,3
	collect_value		9
	put_reused_vector		1,1
	write_elements_inc		1,0,10,2
	write_element_variable		1,2,9
	get_vector_value		4,1
	put_value		1,12
	put_value		4,9
	put_atom		9,on
	execute		9,do_get_if_any_9_0
do_get_if_any_9_6:
	suspend		do_get_if_any_9_0
	module_entry		keyed_bag
	predicate		get_if_any_and_put,12
get_if_any_and_put_12_0:
	create_goal		7
	set_marked_value		1,1
	set_marked_value		2,2
	set_variable		3,13
	set_values_inc		4,9,2
	set_value		6,12
	set_variable		7,9
	enqueue_goal		7,if_rehash_7_0
	put_value		10,11
	put_value		11,13
	execute		11,do_get_if_any_and_put_11_0
get_if_any_and_put_12_1:
	suspend		get_if_any_and_put_12_0
	module_entry		keyed_bag
	predicate		do_get_if_any_and_put,11
do_get_if_any_and_put_11_0:
	try_me_else		do_get_if_any_and_put_11_1
	wait_atom		1,defualt
	integer		2
	wait		6
	switch_on_type		6,do_get_if_any_and_put_11_4,do_get_if_any_and_put_11_5,do_get_if_any_and_put_11_1,do_get_if_any_and_put_11_1,do_get_if_any_and_put_11_1,do_get_if_any_and_put_11_6
do_get_if_any_and_put_11_4:
	g_tag_and_value		6,12,13
	g_and		13,2,1
	put_values_inc		13,3,2
	put_variable		2,12
	b_set_vector_element		5,1,1,2,2
	get_value		2,11
	put_values_inc		2,6,3
	put_values_inc		5,12,2
	put_value		7,9
	put_value		8,14
	put_value		9,10
	put_atom		10,off
	execute		10,do_get_if_any_and_put1_10_0
do_get_if_any_and_put_11_5:
	put_integer		12,0
	g_not_less_than		6,12
	g_and		6,2,1
	put_values_inc		13,3,2
	put_variable		2,12
	b_set_vector_element		5,1,1,2,2
	get_value		2,11
	put_values_inc		2,6,3
	put_values_inc		5,12,2
	put_value		7,9
	put_value		8,14
	put_value		9,10
	put_atom		10,off
	execute		10,do_get_if_any_and_put1_10_0
do_get_if_any_and_put_11_6:
	is_float		6,do_get_if_any_and_put_11_1
	put_float		12,0.0
	g_float_not_less_than		6,12
	g_float_to_integer		6,12
	g_and		12,2,1
	put_values_inc		13,3,2
	put_variable		2,12
	b_set_vector_element		5,1,1,2,2
	get_value		2,11
	put_values_inc		2,6,3
	put_values_inc		5,12,2
	put_value		7,9
	put_value		8,14
	put_value		9,10
	put_atom		10,off
	execute		10,do_get_if_any_and_put1_10_0
do_get_if_any_and_put_11_1:
	otherwise		do_get_if_any_and_put_11_0
	try_me_else		do_get_if_any_and_put_11_12
	jump_on_non_atom		1,do_get_if_any_and_put_11_14
	test_atom		1,default,do_get_if_any_and_put_11_12
	create_goal		11
	set_variable		1,12
	set_values_inc		2,2,4
	set_variable		6,3
	set_values_inc		7,7,5
	enqueue_goal		11,do_get_if_wait_hashed_value_11_0
	put_value		1,6
	put_value		2,12
	execute_external		hasher,hash,3
do_get_if_any_and_put_11_14:
	check_vector		1,3,do_get_if_any_and_put_11_12
	read_elements_inc		1,0,12,3
	atom		12
	atom		13
	integer		14
	put_reused_vector		1,1
	write_elements_inc		1,0,12,3
	put_vector		12,3
	write_element_value		12,0,6
	write_element_variable		12,1,13
	write_element_variable		12,2,6
	b_apply		1,12
	put_value		1,13
	execute		11,do_get_if_wait_hashed_value_11_0
do_get_if_any_and_put_11_12:
	suspend		do_get_if_any_and_put_11_0
	module_entry		keyed_bag
	predicate		do_get_if_wait_hashed_value,11
do_get_if_wait_hashed_value_11_0:
	try_me_else		do_get_if_wait_hashed_value_11_1
	integer		1
	integer		2
	g_and		1,2,1
	put_values_inc		13,3,2
	put_variable		2,12
	b_set_vector_element		5,1,1,2,2
	get_value		2,11
	put_values_inc		2,6,3
	put_values_inc		5,12,2
	put_value		7,9
	put_value		8,14
	put_value		9,10
	put_atom		10,off
	execute		10,do_get_if_any_and_put1_10_0
do_get_if_wait_hashed_value_11_1:
	suspend		do_get_if_wait_hashed_value_11_0
	module_entry		keyed_bag
	predicate		do_get_if_any_and_put1,10
do_get_if_any_and_put1_10_0:
	try_me_else		do_get_if_any_and_put1_10_1
	wait_vector		1,3
	read_elements_inc		1,0,11,3
	wait_value		11,2
	collect_value		10
	collect_value		2
	put_vector		2,1
	write_element_value		2,0,12
	get_vector_value		3,2
	put_reused_vector		1,1
	write_element_value		1,0,11
	write_element_value		1,1,4
	write_element_value		1,2,13
	get_vector_value		5,1
	get_value		7,6
	get_value		9,8
	proceed
do_get_if_any_and_put1_10_1:
	otherwise		do_get_if_any_and_put1_10_0
	try_me_else		do_get_if_any_and_put1_10_6
	jump_on_non_integer		1,do_get_if_any_and_put1_10_8
	test_integer		1,0,do_get_if_any_and_put1_10_6
	put_vector		1,0
	get_vector_value		3,1
	put_vector		1,3
	write_element_value		1,0,2
	write_element_value		1,1,4
	write_element_integer		1,2,0
	get_vector_value		5,1
	b_increment		8,1
	get_value		9,1
	put_value		1,10
	put_values_inc		2,6,2
	execute		3,if_add_entry_number_3_0
do_get_if_any_and_put1_10_8:
	check_vector		1,3,do_get_if_any_and_put1_10_6
	read_elements_inc		1,0,11,3
	collect_value		10
	put_reused_vector		1,1
	write_elements_inc		1,0,11,2
	write_element_variable		1,2,10
	get_vector_value		5,1
	put_value		1,13
	put_value		5,10
	put_atom		10,on
	execute		10,do_get_if_any_and_put1_10_0
do_get_if_any_and_put1_10_6:
	suspend		do_get_if_any_and_put1_10_0
	module_entry		keyed_bag
	predicate		if_add_entry_number,3
if_add_entry_number_3_0:
	try_me_else		if_add_entry_number_3_1
	atom		1
	branch_on_atom		1,2,if_add_entry_number_3_1
	bucket_entry_a		off,if_add_entry_number_3_3
	bucket_entry_a		on,if_add_entry_number_3_4
if_add_entry_number_3_3:
	b_increment		2,1
	get_value		3,1
	proceed
if_add_entry_number_3_4:
	get_value		3,2
	proceed
if_add_entry_number_3_1:
	suspend		if_add_entry_number_3_0
	module_entry		keyed_bag
	predicate		if_rehash,7
if_rehash_7_0:
	try_me_else		if_rehash_7_1
	integer		2
	g_increment		2,8
	put_integer		9,1
	g_shift_right		8,9,9
	put_integer		10,2
	g_shift_right		8,10,8
	g_add		9,8,8
	integer		7
	g_less_than		7,8
	collect_value		1
	get_value		4,2
	get_value		6,3
	get_value		5,7
	proceed
if_rehash_7_1:
	otherwise		if_rehash_7_0
	collect_value		7
	execute		6,rehash_6_0
if_rehash_7_5:
	suspend		if_rehash_7_0
	module_entry		keyed_bag
	predicate		get_and_put_if_any,8
get_and_put_if_any_8_0:
	try_me_else		get_and_put_if_any_8_1
	wait_atom		1,default
	integer		2
	wait		4
	switch_on_type		4,get_and_put_if_any_8_4,get_and_put_if_any_8_5,get_and_put_if_any_8_1,get_and_put_if_any_8_1,get_and_put_if_any_8_1,get_and_put_if_any_8_6
get_and_put_if_any_8_4:
	g_tag_and_value		4,9,10
	g_and		10,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,8
	put_values_inc		2,4,4
	put_value		6,9
	execute		6,do_get_and_put_if_any_6_0
get_and_put_if_any_8_5:
	put_integer		9,0
	g_not_less_than		4,9
	g_and		4,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,8
	put_values_inc		2,4,4
	put_value		6,9
	execute		6,do_get_and_put_if_any_6_0
get_and_put_if_any_8_6:
	is_float		4,get_and_put_if_any_8_1
	put_float		9,0.0
	g_float_not_less_than		4,9
	g_float_to_integer		4,9
	g_and		9,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,8
	put_values_inc		2,4,4
	put_value		6,9
	execute		6,do_get_and_put_if_any_6_0
get_and_put_if_any_8_1:
	otherwise		get_and_put_if_any_8_0
	try_me_else		get_and_put_if_any_8_12
	jump_on_non_atom		1,get_and_put_if_any_8_14
	test_atom		1,default,get_and_put_if_any_8_12
	create_goal		8
	set_variable		1,9
	set_values_inc		2,2,2
	set_variable		4,3
	set_values_inc		5,5,4
	enqueue_goal		8,get_and_put_if_wait_hashed_value_8_0
	put_value		1,4
	put_value		2,9
	execute_external		hasher,hash,3
get_and_put_if_any_8_14:
	check_vector		1,3,get_and_put_if_any_8_12
	read_elements_inc		1,0,9,3
	atom		9
	atom		10
	integer		11
	put_reused_vector		1,1
	write_elements_inc		1,0,9,3
	put_vector		9,3
	write_element_value		9,0,4
	write_element_variable		9,1,10
	write_element_variable		9,2,4
	b_apply		1,9
	put_value		1,10
	execute		8,get_and_put_if_wait_hashed_value_8_0
get_and_put_if_any_8_12:
	suspend		get_and_put_if_any_8_0
	module_entry		keyed_bag
	predicate		get_and_put_if_wait_hashed_value,8
get_and_put_if_wait_hashed_value_8_0:
	try_me_else		get_and_put_if_wait_hashed_value_8_1
	integer		1
	integer		2
	g_and		1,2,1
	put_variable		2,9
	b_set_vector_element		3,1,1,2,2
	get_value		2,8
	put_values_inc		2,4,4
	put_value		6,9
	execute		6,do_get_and_put_if_any_6_0
get_and_put_if_wait_hashed_value_8_1:
	suspend		get_and_put_if_wait_hashed_value_8_0
	module_entry		keyed_bag
	predicate		do_get_and_put_if_any,6
do_get_and_put_if_any_6_0:
	try_me_else		do_get_and_put_if_any_6_1
	wait_vector		1,3
	read_elements_inc		1,0,7,3
	wait_value		7,2
	collect_value		2
	put_vector		2,1
	write_element_value		2,0,8
	get_vector_value		3,2
	put_reused_vector		1,1
	write_element_value		1,0,7
	write_element_value		1,1,4
	write_element_value		1,2,9
	get_vector_value		6,1
	put_vector		1,0
	get_vector_value		5,1
	proceed
do_get_and_put_if_any_6_1:
	otherwise		do_get_and_put_if_any_6_0
	try_me_else		do_get_and_put_if_any_6_6
	jump_on_non_integer		1,do_get_and_put_if_any_6_8
	test_integer		1,0,do_get_and_put_if_any_6_6
	collect_value		2
	put_vector		1,0
	get_vector_value		3,1
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		5,1
	get_integer		6,0
	proceed
do_get_and_put_if_any_6_8:
	check_vector		1,3,do_get_and_put_if_any_6_6
	read_elements_inc		1,0,7,3
	put_reused_vector		1,1
	write_elements_inc		1,0,7,2
	write_element_variable		1,2,7
	get_vector_value		6,1
	put_value		1,9
	put_value		6,7
	execute		6,do_get_and_put_if_any_6_0
do_get_and_put_if_any_6_6:
	suspend		do_get_and_put_if_any_6_0
	module_entry		keyed_bag
	predicate		carbon_copy,4
carbon_copy_4_0:
	try_me_else		carbon_copy_4_1
	integer		1
	try_me_else		carbon_copy_4_3
	put_integer		5,0
	g_not_less_than		1,5
	put_marked_value		5,1
	put_variable		7,6
	b_set_vector_element		2,5,2,7,5
	b_decrement		1,1
	create_goal		4
	set_value		1,1
	set_value		2,5
	set_value		3,3
	set_variable		4,5
	enqueue_goal		4,carbon_copy_4_0
	put_value		1,2
	put_value		2,6
	put_values_inc		3,4,2
	execute		4,carbon_copy_entry_4_0
carbon_copy_4_3:
	get_value		2,3
	get_nil		4
	proceed
carbon_copy_4_1:
	suspend		carbon_copy_4_0
	module_entry		keyed_bag
	predicate		carbon_copy_entry,4
carbon_copy_entry_4_0:
	try_me_else		carbon_copy_entry_4_1
	jump_on_non_integer		1,carbon_copy_entry_4_3
	test_integer		1,0,carbon_copy_entry_4_1
	get_integer		2,0
	get_value		3,4
	proceed
carbon_copy_entry_4_3:
	check_vector		1,3,carbon_copy_entry_4_1
	read_elements_inc		1,0,5,3
	put_vector		8,2
	write_element_marked_value		8,0,5
	write_element_marked_value		8,1,6
	get_list_val_var		3,9,8,8
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,3
	get_vector_value		2,1
	put_value		1,7
	put_value		2,3
	put_value		3,8
	execute		4,carbon_copy_entry_4_0
carbon_copy_entry_4_1:
	suspend		carbon_copy_entry_4_0
	module_entry		keyed_bag
	predicate		carbon_copy,6
carbon_copy_6_0:
	try_me_else		carbon_copy_6_1
	wait_atom		1,default
	integer		2
	wait		4
	switch_on_type		4,carbon_copy_6_4,carbon_copy_6_5,carbon_copy_6_1,carbon_copy_6_1,carbon_copy_6_1,carbon_copy_6_6
carbon_copy_6_4:
	g_tag_and_value		4,7,8
	g_and		8,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_6_5:
	put_integer		7,0
	g_not_less_than		4,7
	g_and		4,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_6_6:
	is_float		4,carbon_copy_6_1
	put_float		7,0.0
	g_float_not_less_than		4,7
	g_float_to_integer		4,7
	g_and		7,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_6_1:
	otherwise		carbon_copy_6_0
	try_me_else		carbon_copy_6_12
	jump_on_non_atom		1,carbon_copy_6_14
	test_atom		1,default,carbon_copy_6_12
	create_goal		6
	set_variable		1,7
	set_values_inc		2,2,2
	set_variable		4,3
	set_values_inc		5,5,2
	enqueue_goal		6,carbon_copy_wait_hashed_value_6_0
	put_value		1,4
	put_value		2,7
	execute_external		hasher,hash,3
carbon_copy_6_14:
	check_vector		1,3,carbon_copy_6_12
	read_elements_inc		1,0,7,3
	atom		7
	atom		8
	integer		9
	put_reused_vector		1,1
	write_elements_inc		1,0,7,3
	put_vector		7,3
	write_element_value		7,0,4
	write_element_variable		7,1,8
	write_element_variable		7,2,4
	b_apply		1,7
	put_value		1,8
	execute		6,carbon_copy_wait_hashed_value_6_0
carbon_copy_6_12:
	suspend		carbon_copy_6_0
	module_entry		keyed_bag
	predicate		carbon_copy_wait_hashed_value,6
carbon_copy_wait_hashed_value_6_0:
	try_me_else		carbon_copy_wait_hashed_value_6_1
	integer		1
	integer		2
	g_and		1,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_wait_hashed_value_6_1:
	suspend		carbon_copy_wait_hashed_value_6_0
	module_entry		keyed_bag
	predicate		carbon_copy_entry_with_key,4
carbon_copy_entry_with_key_4_0:
	try_me_else		carbon_copy_entry_with_key_4_1
	wait_vector		1,3
	read_elements_inc		1,0,5,3
	wait_value		5,2
	collect_value		2
	put_list		2
	write_car_marked_value		2,6
	write_cdr_variable		2,8
	get_list_value		3,2
	put_reused_vector		1,1
	write_element_marked_value		1,0,5
	write_element_value		1,1,6
	write_element_variable		1,2,6
	get_vector_value		4,1
	put_value		1,7
	put_value		2,5
	put_value		3,8
	put_value		4,6
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_entry_with_key_4_1:
	otherwise		carbon_copy_entry_with_key_4_0
	try_me_else		carbon_copy_entry_with_key_4_6
	jump_on_non_integer		1,carbon_copy_entry_with_key_4_8
	test_integer		1,0,carbon_copy_entry_with_key_4_6
	collect_value		2
	get_nil		3
	get_integer		4,0
	proceed
carbon_copy_entry_with_key_4_8:
	check_vector		1,3,carbon_copy_entry_with_key_4_6
	read_elements_inc		1,0,5,3
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,5
	get_vector_value		4,1
	put_value		1,7
	put_value		4,5
	execute		4,carbon_copy_entry_with_key_4_0
carbon_copy_entry_with_key_4_6:
	suspend		carbon_copy_entry_with_key_4_0
	module_entry		keyed_bag
	predicate		get_average_chaining_length,3
get_average_chaining_length_3_0:
	try_me_else		get_average_chaining_length_3_1
	integer		1
	g_integer_to_float		1,4
	integer		2
	g_integer_to_float		2,5
	g_float_divide		4,5,1
	get_value		3,1
	proceed
get_average_chaining_length_3_1:
	try_me_else		get_average_chaining_length_3_3
	wait_integer		2,0
	collect_value		1
	get_float		3,0.0
	proceed
get_average_chaining_length_3_3:
	suspend		get_average_chaining_length_3_0
	module_entry		keyed_bag
	predicate		copy_keyed_bag,7
copy_keyed_bag_7_0:
	b_merge		9,8
	get_value		9,6
	create_goal		6
	set_value		1,1
	set_value		2,8
	set_marked_value		3,2
	set_values_inc		4,3,2
	set_variable		6,4
	enqueue_goal		6,keyed_bag_6_0
	put_value		1,2
	put_value		2,5
	put_value		3,7
	execute		4,do_copy_4_0
copy_keyed_bag_7_1:
	suspend		copy_keyed_bag_7_0
	module_entry		keyed_bag
	predicate		copy_keyed_set,7
copy_keyed_set_7_0:
	b_merge		9,8
	get_value		9,6
	create_goal		6
	set_value		1,1
	set_value		2,8
	set_marked_value		3,2
	set_values_inc		4,3,2
	set_variable		6,4
	enqueue_goal		6,keyed_set_6_0
	put_value		1,2
	put_value		2,5
	put_value		3,7
	execute		4,do_copy_4_0
copy_keyed_set_7_1:
	suspend		copy_keyed_set_7_0
	module_entry		keyed_bag
	predicate		do_copy,4
do_copy_4_0:
	put_value		5,4
	put_marked_value		4,1
	b_increment		4,4
	b_new_vector		4,4
	execute		5,do_copy_5_0
do_copy_4_1:
	suspend		do_copy_4_0
	module_entry		keyed_bag
	predicate		do_copy,5
do_copy_5_0:
	try_me_else		do_copy_5_1
	integer		1
	try_me_else		do_copy_5_3
	put_integer		6,0
	g_not_less_than		1,6
	put_marked_value		6,1
	put_variable		7,8
	b_set_vector_element		2,6,2,7,6
	put_variable		7,9
	b_set_vector_element		4,1,4,7,7
	b_decrement		1,1
	create_goal		5
	set_value		1,1
	set_value		2,6
	set_value		3,3
	set_value		4,7
	set_value		5,5
	enqueue_goal		5,do_copy_5_0
	put_value		1,2
	put_values_inc		2,8,2
	execute		3,copy_entry_3_0
do_copy_5_3:
	get_value		2,3
	get_value		4,5
	proceed
do_copy_5_1:
	suspend		do_copy_5_0
	module_entry		keyed_bag
	predicate		copy_entry,3
copy_entry_3_0:
	try_me_else		copy_entry_3_1
	jump_on_non_integer		1,copy_entry_3_3
	test_integer		1,0,copy_entry_3_1
	get_integer		2,0
	get_integer		3,0
	proceed
copy_entry_3_3:
	check_vector		1,3,copy_entry_3_1
	read_elements_inc		1,0,4,3
	put_reused_vector		1,1
	write_element_marked_value		1,0,4
	write_element_marked_value		1,1,5
	write_element_variable		1,2,7
	get_vector_value		2,1
	put_vector		1,3
	write_elements_inc		1,0,4,2
	write_element_variable		1,2,4
	get_vector_value		3,1
	put_values_inc		1,6,2
	put_value		3,4
	execute		3,copy_entry_3_0
copy_entry_3_1:
	suspend		copy_entry_3_0
	module_entry		keyed_bag
	predicate		keyed_set,3
keyed_set_3_0:
	try_me_else		keyed_set_3_1
	integer		3
	put_integer		4,0
	g_less_than		4,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,4
	enqueue_goal		3,wait_table_size_set_3_0
	put_integer		1,1
	put_values_inc		2,3,2
	execute		3,get_table_size_3_0
keyed_set_3_1:
	suspend		keyed_set_3_0
	module_entry		keyed_bag
	predicate		wait_table_size_set,3
wait_table_size_set_3_0:
	try_me_else		wait_table_size_set_3_1
	wait		3
	put_marked_value		4,3
	b_new_vector		6,4
	b_merge		5,4
	get_value		5,2
	b_decrement		3,3
	put_value		2,4
	put_integer		4,0
	put_integer		5,0
	execute		6,keyed_set_6_0
wait_table_size_set_3_1:
	suspend		wait_table_size_set_3_0
	module_entry		keyed_bag
	predicate		keyed_set,6
keyed_set_6_0:
	try_me_else		keyed_set_6_1
	jump_on_non_list		2,keyed_set_6_3
	read_car		2,7
	vector		7
	jump_on_arity		7,6,keyed_set_6_1
	table_entry		keyed_set_6_1
	table_entry		keyed_set_6_1
	table_entry		keyed_set_6_5
	table_entry		keyed_set_6_6
	table_entry		keyed_set_6_7
	table_entry		keyed_set_6_8
keyed_set_6_5:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,7,keyed_set_6_1
	bucket_entry_a		carbon_copy,keyed_set_6_10
	bucket_entry_a		copy,keyed_set_6_11
	bucket_entry_a		do,keyed_set_6_12
	bucket_entry_a		empty,keyed_set_6_13
	bucket_entry_a		get_all,keyed_set_6_14
	bucket_entry_a		get_average_chaining_length,keyed_set_6_15
	bucket_entry_a		get_load_factor,keyed_set_6_16
keyed_set_6_10:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,4
	enqueue_goal		6,keyed_set_6_0
	put_value		1,3
	put_value		2,6
	put_value		3,4
	put_value		4,10
	execute		4,carbon_copy_4_0
keyed_set_6_11:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_variable		6,7
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,4
	put_value		6,10
	execute		7,copy_keyed_set_7_0
keyed_set_6_12:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	b_merge		7,2
	get_value		7,10
	create_goal		6
	set_value		1,1
	set_variable		2,7
	set_values_inc		3,3,4
	enqueue_goal		6,keyed_set_6_0
	put_value		1,2
	put_value		2,9
	put_value		3,7
	execute		3,prepend_3_0
keyed_set_6_13:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_value		3,3
	set_marked_value		4,4
	set_values_inc		5,5,2
	enqueue_goal		6,keyed_set_6_0
	put_value		1,4
	put_value		2,10
	execute		2,empty_2_0
keyed_set_6_14:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_value		5
	collect_value		4
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_integer		4,0
	set_integer		5,0
	set_variable		6,4
	enqueue_goal		6,keyed_set_6_0
	put_value		1,3
	put_value		2,6
	put_value		3,4
	put_value		4,10
	execute		4,get_all_4_0
keyed_set_6_15:
	read_cdr		2,9
	read_element		7,1,10
	collect_list		2
	collect_vector		7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_value		6,6
	enqueue_goal		6,keyed_set_6_0
	put_values_dec		1,5,2
	put_value		3,10
	execute		3,get_average_chaining_length_3_0
keyed_set_6_16:
	read_cdr		2,9
	read_element		7,1,10
	integer		3
	g_increment		3,11
	g_integer_to_float		11,11
	integer		4
	g_integer_to_float		4,12
	g_float_divide		12,11,8
	collect_list		2
	collect_vector		7
	get_value		10,8
	put_value		2,9
	execute		6,keyed_set_6_0
keyed_set_6_6:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,5,keyed_set_6_1
	bucket_entry_a		carbon_copy,keyed_set_6_18
	bucket_entry_a		empty,keyed_set_6_19
	bucket_entry_a		get,keyed_set_6_20
	bucket_entry_a		get_all,keyed_set_6_21
	bucket_entry_a		get_if_any,keyed_set_6_22
keyed_set_6_18:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_set_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,10,2
	put_value		6,7
	execute		6,carbon_copy_at_most_one_6_0
keyed_set_6_19:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	put_value		8,3
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,8
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,10,2
	put_value		4,8
	put_values_inc		5,6,2
	execute		6,empty_6_0
keyed_set_6_20:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	b_decrement		5,2
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,7
	set_value		5,2
	set_variable		6,8
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,2
	put_value		4,6
	put_values_inc		5,10,2
	put_atom		9,set
	execute		9,get_9_0
keyed_set_6_21:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,8
	set_variable		5,9
	set_variable		6,12
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,2
	put_value		10,12
	execute		10,get_at_most_one_10_0
keyed_set_6_22:
	read_cdr		2,9
	read_elements_inc		7,1,10,2
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_variable		4,8
	set_variable		5,9
	set_variable		6,12
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,2
	put_value		10,12
	execute		10,get_if_any_10_0
keyed_set_6_7:
	read_element		7,0,8
	atom		8
	branch_on_atom		8,3,keyed_set_6_1
	bucket_entry_a		get_and_put,keyed_set_6_24
	bucket_entry_a		get_if_any_and_put,keyed_set_6_25
	bucket_entry_a		put,keyed_set_6_26
keyed_set_6_24:
	read_cdr		2,9
	read_elements_inc		7,1,10,3
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,7
	enqueue_goal		6,keyed_set_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,10,3
	put_atom		8,set
	execute		8,get_and_put_8_0
keyed_set_6_25:
	read_cdr		2,9
	read_elements_inc		7,1,10,3
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_variable		3,9
	set_variable		4,15
	set_variable		5,14
	set_variable		6,13
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,4
	put_values_inc		6,10,3
	put_values_dec		10,15,3
	execute		12,get_if_any_and_put_12_0
keyed_set_6_26:
	read_cdr		2,9
	read_elements_inc		7,1,10,3
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,9
	set_variable		3,9
	set_variable		4,15
	set_variable		5,14
	set_variable		6,13
	enqueue_goal		6,keyed_set_6_0
	put_values_inc		2,3,4
	put_value		6,10
	put_values_dec		7,12,2
	put_values_dec		10,15,3
	execute		12,get_if_any_and_put_12_0
keyed_set_6_8:
	read_cdr		2,8
	read_element		7,0,9
	wait_atom		9,get_and_put_if_any
	read_elements_inc		7,1,9,4
	collect_list		2
	collect_vector		7
	create_goal		6
	set_marked_value		1,1
	set_value		2,8
	set_marked_value		3,3
	set_values_inc		4,4,2
	set_variable		6,8
	enqueue_goal		6,keyed_set_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		4,9,4
	execute		8,get_and_put_if_any_8_0
keyed_set_6_3:
	check_nil		2,keyed_set_6_1
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		1
	proceed
keyed_set_6_1:
	otherwise		keyed_set_6_0
	try_me_else		keyed_set_6_39
	wait_list_var_var		2,7,8
	collect_list		2
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		8
	collect_value		1
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_3'
	b_raise		2,1,7
	proceed
keyed_set_6_39:
	suspend		keyed_set_6_0
	module_entry		keyed_bag
	predicate		get_at_most_one,10
get_at_most_one_10_0:
	create_goal		2
	set_variable		1,11
	set_value		2,7
	enqueue_goal		2,get_at_most_one_2_0
	put_value		7,11
	execute		10,get_if_any_10_0
get_at_most_one_10_1:
	suspend		get_at_most_one_10_0
	module_entry		keyed_bag
	predicate		get_at_most_one,2
get_at_most_one_2_0:
	try_me_else		get_at_most_one_2_1
	vector		1
	jump_on_arity		1,2,get_at_most_one_2_1
	table_entry		get_at_most_one_2_3
	table_entry		get_at_most_one_2_4
get_at_most_one_2_3:
	get_nil		2
	proceed
get_at_most_one_2_4:
	read_element		1,0,3
	collect_vector		1
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		2,1
	proceed
get_at_most_one_2_1:
	suspend		get_at_most_one_2_0
	module_entry		keyed_bag
	predicate		carbon_copy_at_most_one,6
carbon_copy_at_most_one_6_0:
	try_me_else		carbon_copy_at_most_one_6_1
	wait_atom		1,default
	integer		2
	wait		4
	switch_on_type		4,carbon_copy_at_most_one_6_4,carbon_copy_at_most_one_6_5,carbon_copy_at_most_one_6_1,carbon_copy_at_most_one_6_1,carbon_copy_at_most_one_6_1,carbon_copy_at_most_one_6_6
carbon_copy_at_most_one_6_4:
	g_tag_and_value		4,7,8
	g_and		8,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_if_any_4_0
carbon_copy_at_most_one_6_5:
	put_integer		7,0
	g_not_less_than		4,7
	g_and		4,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_if_any_4_0
carbon_copy_at_most_one_6_6:
	is_float		4,carbon_copy_at_most_one_6_1
	put_float		7,0.0
	g_float_not_less_than		4,7
	g_float_to_integer		4,7
	g_and		7,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_if_any_4_0
carbon_copy_at_most_one_6_1:
	otherwise		carbon_copy_at_most_one_6_0
	try_me_else		carbon_copy_at_most_one_6_12
	jump_on_non_atom		1,carbon_copy_at_most_one_6_14
	test_atom		1,default,carbon_copy_at_most_one_6_12
	create_goal		6
	set_variable		1,7
	set_values_inc		2,2,2
	set_variable		4,3
	set_values_inc		5,5,2
	enqueue_goal		6,carbon_copy_one_wait_hashed_value_6_0
	put_value		1,4
	put_value		2,7
	execute_external		hasher,hash,3
carbon_copy_at_most_one_6_14:
	check_vector		1,3,carbon_copy_at_most_one_6_12
	read_elements_inc		1,0,7,3
	atom		7
	atom		8
	integer		9
	put_reused_vector		1,1
	write_elements_inc		1,0,7,3
	put_vector		7,3
	write_element_value		7,0,4
	write_element_variable		7,1,8
	write_element_variable		7,2,4
	b_apply		1,7
	put_value		1,8
	execute		6,carbon_copy_one_wait_hashed_value_6_0
carbon_copy_at_most_one_6_12:
	suspend		carbon_copy_at_most_one_6_0
	module_entry		keyed_bag
	predicate		carbon_copy_one_wait_hashed_value,6
carbon_copy_one_wait_hashed_value_6_0:
	try_me_else		carbon_copy_one_wait_hashed_value_6_1
	integer		1
	integer		2
	g_and		1,2,1
	put_variable		2,7
	b_set_vector_element		3,1,1,2,2
	get_value		2,6
	put_values_inc		2,4,2
	put_value		4,7
	execute		4,carbon_copy_if_any_4_0
carbon_copy_one_wait_hashed_value_6_1:
	suspend		carbon_copy_one_wait_hashed_value_6_0
	module_entry		keyed_bag
	predicate		carbon_copy_if_any,4
carbon_copy_if_any_4_0:
	try_me_else		carbon_copy_if_any_4_1
	wait_vector		1,3
	read_elements_inc		1,0,5,3
	wait_value		5,2
	collect_value		2
	put_list		2
	write_car_marked_value		2,6
	write_cdr_nil		2
	get_list_value		3,2
	put_reused_vector		1,1
	write_elements_inc		1,0,5,3
	get_vector_value		4,1
	proceed
carbon_copy_if_any_4_1:
	otherwise		carbon_copy_if_any_4_0
	try_me_else		carbon_copy_if_any_4_6
	jump_on_non_integer		1,carbon_copy_if_any_4_8
	test_integer		1,0,carbon_copy_if_any_4_6
	collect_value		2
	get_nil		3
	get_integer		4,0
	proceed
carbon_copy_if_any_4_8:
	check_vector		1,3,carbon_copy_if_any_4_6
	read_elements_inc		1,0,5,3
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_variable		1,2,5
	get_vector_value		4,1
	put_value		1,7
	put_value		4,5
	execute		4,carbon_copy_if_any_4_0
carbon_copy_if_any_4_6:
	suspend		carbon_copy_if_any_4_0
	begin_const_section		keyed_bag
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
	define_atom		keyed_bag
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
	define_atom		keyed_bag
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_2_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_set
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_3_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		keyed_set
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
