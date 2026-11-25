hasher:
	module		hasher
	entry		hash,3,hash_3_0
	module_entry		hasher
	predicate		hash,3
hash_3_0:
	put_integer		4,6
	execute		4,hash0_4_0
hash_3_1:
	suspend		hash_3_0
	module_entry		hasher
	predicate		hash0,4
hash0_4_0:
	try_me_else		hash0_4_1
	wait		1
	switch_on_type		1,hash0_4_2,hash0_4_3,hash0_4_4,hash0_4_5,hash0_4_6,hash0_4_1
hash0_4_4:
	execute		4,hash_list_4_0
hash0_4_2:
	collect_value		4
	b_hash		1,1,4
	get_value		1,2
	get_value		4,3
	proceed
hash0_4_3:
	collect_value		4
	put_marked_value		1,1
	get_value		1,3
	execute		2,hash_int_2_0
hash0_4_5:
	g_vector		1,5
	execute		5,hash_vect_5_0
hash0_4_6:
	g_string		1,5,6
	collect_value		4
	b_hash		1,1,4
	get_value		1,2
	get_value		4,3
	proceed
hash0_4_1:
	otherwise		hash0_4_0
	collect_value		4
	b_hash		1,1,4
	get_value		1,2
	get_value		4,3
	proceed
hash0_4_8:
	suspend		hash0_4_0
	module_entry		hasher
	predicate		hash_int,2
hash_int_2_0:
	try_me_else		hash_int_2_1
	integer		1
	test_integer		1,-2147483648,hash_int_2_3
	get_integer		2,0
	proceed
hash_int_2_3:
	try_me_else		hash_int_2_4
	put_integer		3,0
	g_not_less_than		1,3
	get_value		2,1
	proceed
hash_int_2_4:
	try_me_else		hash_int_2_1
	put_integer		3,-2147483648
	g_less_than		3,1
	b_minus		1,1
	get_value		2,1
	proceed
hash_int_2_1:
	suspend		hash_int_2_0
	module_entry		hasher
	predicate		hash_list,4
hash_list_4_0:
	try_me_else		hash_list_4_1
	wait_list_var_var		1,5,6
	integer		4
	put_integer		7,0
	g_less_than		7,4
	put_reused_list		1,1
	write_car_variable		1,8
	write_cdr_variable		1,7
	get_list_value		3,1
	b_decrement		4,1
	put_value		9,1
	put_variable		1,10
	put_integer		3,536870911
	b_and		1,3,1
	put_marked_variable		3,4
	put_integer		11,2
	b_shift_left		3,11,3
	put_integer		11,536870911
	b_and		3,11,3
	b_add		1,3,1
	put_integer		3,536870911
	b_and		4,3,3
	b_add		1,3,1
	get_value		2,1
	create_goal		4
	set_value		1,6
	set_value		2,4
	set_value		3,7
	set_marked_value		4,9
	enqueue_goal		4,hash0_4_0
	put_value		1,5
	put_value		2,10
	put_values_inc		3,8,2
	execute		4,hash0_4_0
hash_list_4_1:
	try_me_else		hash_list_4_3
	wait_integer		4,0
	get_integer		2,0
	get_value		1,3
	proceed
hash_list_4_3:
	suspend		hash_list_4_0
	module_entry		hasher
	predicate		hash_vect,5
hash_vect_5_0:
	try_me_else		hash_vect_5_1
	integer		4
	test_integer		4,0,hash_vect_5_3
	collect_value		5
	get_integer		2,0
	get_value		1,3
	proceed
hash_vect_5_3:
	put_integer		6,0
	g_less_than		6,4
	integer		5
	put_integer		6,0
	g_less_than		6,5
	put_integer		6,2
	g_divide		5,6,6
	g_decrement		5,7
	put_integer		8,0
	put_variable		10,9
	b_set_vector_element		1,8,1,10,8
	put_variable		11,10
	b_set_vector_element		8,6,6,11,8
	put_variable		12,11
	b_set_vector_element		8,7,7,12,8
	get_value		8,3
	b_decrement		4,3
	put_value		4,3
	create_goal		5
	set_variable		1,3
	set_variable		2,8
	set_variable		3,12
	set_value		4,2
	set_value		5,5
	enqueue_goal		5,wait_hashed_value_5_0
	create_goal		4
	set_value		1,7
	set_values_dec		2,12,2
	set_marked_value		4,4
	enqueue_goal		4,hash0_4_0
	create_goal		4
	set_value		1,6
	set_value		2,8
	set_value		3,10
	set_value		4,4
	enqueue_goal		4,hash0_4_0
	put_value		2,3
	put_value		3,9
	execute		4,hash0_4_0
hash_vect_5_1:
	try_me_else		hash_vect_5_4
	wait_integer		5,0
	collect_value		4
	get_integer		2,0
	get_value		1,3
	proceed
hash_vect_5_4:
	suspend		hash_vect_5_0
	module_entry		hasher
	predicate		wait_hashed_value,5
wait_hashed_value_5_0:
	try_me_else		wait_hashed_value_5_1
	integer		1
	integer		2
	put_integer		6,1
	g_shift_left		2,6,6
	put_integer		7,1073741823
	g_and		6,7,6
	put_integer		7,1073741823
	g_and		2,7,7
	g_add		6,7,6
	integer		3
	put_integer		7,2
	g_shift_left		3,7,7
	put_integer		8,1073741823
	g_and		7,8,7
	put_integer		8,1073741823
	g_and		3,8,8
	g_add		7,8,7
	put_integer		8,1073741823
	g_and		1,8,8
	put_integer		9,1073741823
	g_and		6,9,6
	g_add		8,6,6
	put_integer		8,1073741823
	g_and		6,8,6
	put_integer		8,1073741823
	g_and		7,8,7
	integer		5
	put_integer		8,1073741823
	g_and		5,8,8
	g_add		7,8,7
	put_integer		1,1073741823
	g_and		7,1,1
	b_add		6,1,1
	get_value		4,1
	proceed
wait_hashed_value_5_1:
	suspend		wait_hashed_value_5_0
