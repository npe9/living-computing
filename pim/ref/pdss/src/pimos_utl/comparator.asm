comparator:
	module		comparator
	entry		sort,5,sort_5_0
	entry		descending_sort,5,descending_sort_5_0
	entry		sort0,5,sort0_5_0
	module_entry		comparator
	predicate		sort,5
sort_5_0:
	create_goal		6
	set_variable		1,7
	set_variable		2,6
	set_values_inc		3,3,3
	set_variable		6,5
	enqueue_goal		6,wait_sorted_6_0
	put_values_dec		3,7,2
	execute		5,sort0_5_0
sort_5_1:
	suspend		sort_5_0
	module_entry		comparator
	predicate		descending_sort,5
descending_sort_5_0:
	put_value		8,1
	create_goal		6
	set_variable		1,6
	set_variable		2,7
	set_values_inc		3,3,3
	set_variable		6,5
	enqueue_goal		6,wait_sorted_6_0
	put_value		1,2
	put_values_dec		2,8,3
	execute		5,sort0_5_0
descending_sort_5_1:
	suspend		descending_sort_5_0
	module_entry		comparator
	predicate		sort0,5
sort0_5_0:
	create_goal		7
	set_variable		1,6
	set_variable		2,7
	set_values_inc		3,3,3
	set_variable		6,3
	set_variable		7,4
	enqueue_goal		7,do_sort_7_0
	create_goal		3
	set_value		1,2
	set_value		2,7
	set_value		3,4
	enqueue_goal		3,get_type_3_0
	put_value		2,6
	execute		3,get_type_3_0
sort0_5_1:
	suspend		sort0_5_0
	module_entry		comparator
	predicate		wait_sorted,6
wait_sorted_6_0:
	try_me_else		wait_sorted_6_1
	atom		6
	branch_on_atom		6,3,wait_sorted_6_1
	bucket_entry_a		greater,wait_sorted_6_3
	bucket_entry_a		less,wait_sorted_6_4
	bucket_entry_a		same,wait_sorted_6_5
wait_sorted_6_3:
	get_value		3,2
	get_value		4,1
	get_atom		5,yes
	proceed
wait_sorted_6_4:
	get_value		3,1
	get_value		4,2
	get_atom		5,no
	proceed
wait_sorted_6_5:
	get_value		3,1
	get_value		4,2
	get_atom		5,no
	proceed
wait_sorted_6_1:
	suspend		wait_sorted_6_0
	module_entry		comparator
	predicate		get_type,3
get_type_3_0:
	try_me_else		get_type_3_1
	wait		1
	execute		3,get_type1_3_0
get_type_3_1:
	suspend		get_type_3_0
	module_entry		comparator
	predicate		get_type1,3
get_type1_3_0:
	try_me_else		get_type1_3_1
	wait		1
	switch_on_type		1,get_type1_3_2,get_type1_3_3,get_type1_3_4,get_type1_3_5,get_type1_3_6,get_type1_3_7
get_type1_3_4:
	get_value		2,1
	get_integer		3,4
	proceed
get_type1_3_2:
	get_value		2,1
	get_integer		3,2
	proceed
get_type1_3_3:
	get_value		2,1
	get_integer		3,0
	proceed
get_type1_3_5:
	g_vector		1,4
	get_value		2,1
	get_integer		3,5
	proceed
get_type1_3_6:
	g_string		1,4,5
	get_value		2,1
	get_integer		3,3
	proceed
get_type1_3_7:
	is_float		1,get_type1_3_1
	get_value		2,1
	get_integer		3,1
	proceed
get_type1_3_1:
	otherwise		get_type1_3_0
	get_value		2,1
	get_integer		3,8
	proceed
get_type1_3_10:
	suspend		get_type1_3_0
	module_entry		comparator
	predicate		do_sort,7
do_sort_7_0:
	try_me_else		do_sort_7_1
	integer		6
	jump_on_integer		6,2,do_sort_7_1
	table_entry		do_sort_7_3
	table_entry		do_sort_7_4
do_sort_7_3:
	wait_integer		7,1
	put_marked_value		6,1
	b_integer_to_float		6,6
	get_value		3,1
	create_goal		3
	set_variable		1,7
	set_atom		2,less
	set_value		3,5
	enqueue_goal		3,wait_compared_real_3_0
	put_value		1,6
	put_void		3
	put_value		5,7
	execute		5,comp_real_5_0
do_sort_7_4:
	wait_integer		7,0
	put_marked_value		6,2
	b_integer_to_float		6,6
	get_value		4,2
	create_goal		3
	set_variable		1,7
	set_atom		2,greater
	set_value		3,5
	enqueue_goal		3,wait_compared_real_3_0
	put_value		2,6
	put_void		4
	put_value		5,7
	execute		5,comp_real_5_0
do_sort_7_1:
	try_me_else		do_sort_7_5
	wait_value		6,7
	collect_value		7
	execute		6,comp_6_0
do_sort_7_5:
	otherwise		do_sort_7_0
	get_value		3,1
	get_value		4,2
	put_values_inc		1,6,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
do_sort_7_8:
	suspend		do_sort_7_0
	module_entry		comparator
	predicate		wait_compared_real,3
wait_compared_real_3_0:
	try_me_else		wait_compared_real_3_1
	wait_atom		1,same
	get_value		3,2
	proceed
wait_compared_real_3_1:
	otherwise		wait_compared_real_3_0
	collect_value		2
	get_value		3,1
	proceed
wait_compared_real_3_6:
	suspend		wait_compared_real_3_0
	module_entry		comparator
	predicate		comp,6
comp_6_0:
	try_me_else		comp_6_1
	vector		1
	vector		2
	wait_integer		6,5
	g_vector		1,7
	g_vector		2,8
	put_values_inc		6,7,2
	execute		7,comp_vect_7_0
comp_6_1:
	try_me_else		comp_6_5
	integer		6
	jump_on_integer		6,9,comp_6_5
	table_entry		comp_6_7
	table_entry		comp_6_8
	table_entry		comp_6_9
	table_entry		comp_6_10
	table_entry		comp_6_11
	table_entry		comp_6_5
	table_entry		comp_6_5
	table_entry		comp_6_5
	table_entry		comp_6_12
comp_6_7:
	execute		5,comp_int_5_0
comp_6_8:
	execute		5,comp_real_5_0
comp_6_9:
	g_tag_and_value		1,6,7
	g_tag_and_value		2,6,8
	get_value		1,3
	get_value		2,4
	put_values_inc		1,7,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
comp_6_10:
	execute		5,comp_str_5_0
comp_6_11:
	execute		5,comp_list_5_0
comp_6_12:
	g_tag_and_value		1,6,7
	g_tag_and_value		2,8,9
	get_value		3,1
	get_value		4,2
	put_value		1,6
	put_values_dec		2,8,2
	put_value		4,9
	execute		5,comp_tag_and_value_5_0
comp_6_5:
	suspend		comp_6_0
	module_entry		comparator
	predicate		comp_int,5
comp_int_5_0:
	try_me_else		comp_int_5_1
	integer		1
	integer		2
	try_me_else		comp_int_5_4
	g_less_than		1,2
	get_value		3,1
	get_value		4,2
	get_atom		5,less
	proceed
comp_int_5_4:
	try_me_else		comp_int_5_5
	g_less_than		2,1
	get_value		3,1
	get_value		4,2
	get_atom		5,greater
	proceed
comp_int_5_5:
	try_me_else		comp_int_5_1
	g_equal		1,2
	get_value		3,1
	get_value		4,2
	get_atom		5,same
	proceed
comp_int_5_1:
	suspend		comp_int_5_0
	module_entry		comparator
	predicate		comp_real,5
comp_real_5_0:
	try_me_else		comp_real_5_1
	float		1
	float		2
	try_me_else		comp_real_5_4
	g_float_less_than		1,2
	get_value		3,1
	get_value		4,2
	get_atom		5,less
	proceed
comp_real_5_4:
	try_me_else		comp_real_5_5
	g_float_less_than		2,1
	get_value		3,1
	get_value		4,2
	get_atom		5,greater
	proceed
comp_real_5_5:
	try_me_else		comp_real_5_1
	g_float_equal		1,2
	get_value		3,1
	get_value		4,2
	get_atom		5,same
	proceed
comp_real_5_1:
	suspend		comp_real_5_0
	module_entry		comparator
	predicate		comp_str,5
comp_str_5_0:
	try_me_else		comp_str_5_1
	wait_value		1,2
	collect_value		2
	put_marked_value		1,1
	get_value		1,3
	get_value		1,4
	get_atom		5,same
	proceed
comp_str_5_1:
	otherwise		comp_str_5_0
	try_me_else		comp_str_5_3
	string		1
	string		2
	g_string		1,7,9
	g_string		2,8,10
	put_integer		6,0
	execute		10,comp_str_10_0
comp_str_5_3:
	suspend		comp_str_5_0
	module_entry		comparator
	predicate		comp_str,10
comp_str_10_0:
	try_me_else		comp_str_10_1
	wait_value		9,10
	collect_value		9
	collect_value		10
	execute		8,comp_str_8_0
comp_str_10_1:
	otherwise		comp_str_10_0
	collect_value		8
	collect_value		7
	collect_value		6
	get_value		3,1
	get_value		4,2
	put_values_inc		1,9,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
comp_str_10_3:
	suspend		comp_str_10_0
	module_entry		comparator
	predicate		comp_str,8
comp_str_8_0:
	try_me_else		comp_str_8_1
	string		1
	string		2
	integer		6
	integer		7
	g_less_than		6,7
	integer		8
	g_less_than		6,8
	g_string_element		1,6,9
	g_string_element		2,6,10
	create_goal		9
	set_values_inc		1,1,8
	set_variable		9,5
	enqueue_goal		9,wait_compared_str_9_0
	put_values_inc		1,9,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
comp_str_8_1:
	otherwise		comp_str_8_0
	try_me_else		comp_str_8_9
	integer		6
	integer		7
	integer		8
	try_me_else		comp_str_8_13
	wait_value		6,7
	g_less_than		6,8
	get_value		3,1
	get_value		4,2
	get_atom		5,less
	proceed
comp_str_8_13:
	try_me_else		comp_str_8_9
	wait_value		6,8
	g_less_than		6,7
	get_value		3,1
	get_value		4,2
	get_atom		5,greater
	proceed
comp_str_8_9:
	try_me_else		comp_str_8_14
	wait_value		6,7
	wait_value		6,8
	collect_value		6
	collect_value		8
	get_value		3,1
	get_value		4,2
	get_atom		5,same
	proceed
comp_str_8_14:
	suspend		comp_str_8_0
	module_entry		comparator
	predicate		wait_compared_str,9
wait_compared_str_9_0:
	try_me_else		wait_compared_str_9_1
	wait_atom		9,same
	b_increment		6,6
	execute		8,comp_str_8_0
wait_compared_str_9_1:
	otherwise		wait_compared_str_9_0
	collect_value		8
	collect_value		7
	collect_value		6
	get_value		3,1
	get_value		4,2
	get_value		5,9
	proceed
wait_compared_str_9_6:
	suspend		wait_compared_str_9_0
	module_entry		comparator
	predicate		comp_list,5
comp_list_5_0:
	try_me_else		comp_list_5_1
	jump_on_non_list_var_var		1,comp_list_5_3,6,7
	jump_on_non_list_var_var		2,comp_list_5_5,8,9
	put_reused_list		10,1
	write_car_variable		10,11
	write_cdr_variable		10,1
	get_list_value		3,10
	put_reused_list		3,2
	write_car_variable		3,10
	write_cdr_variable		3,2
	get_list_value		4,3
	create_goal		6
	set_value		1,7
	set_value		2,9
	set_values_inc		3,1,2
	set_value		5,5
	set_variable		6,5
	enqueue_goal		6,wait_compared_list_6_0
	put_value		1,6
	put_value		2,8
	put_values_dec		3,11,2
	execute		5,sort0_5_0
comp_list_5_5:
	check_nil		2,comp_list_5_1
	put_reused_list_val_val		1,1,6,7
	get_list_value		3,1
	get_nil		4
	get_atom		5,greater
	proceed
comp_list_5_3:
	check_nil		1,comp_list_5_1
	jump_on_non_list_var_var		2,comp_list_5_7,1,6
	get_nil		3
	put_reused_list_val_val		2,2,1,6
	get_list_value		4,2
	get_atom		5,less
	proceed
comp_list_5_7:
	check_nil		2,comp_list_5_1
	get_nil		3
	get_nil		4
	get_atom		5,same
	proceed
comp_list_5_1:
	otherwise		comp_list_5_0
	execute		5,sort0_5_0
comp_list_5_19:
	suspend		comp_list_5_0
	module_entry		comparator
	predicate		wait_compared_list,6
wait_compared_list_6_0:
	try_me_else		wait_compared_list_6_1
	wait_atom		6,same
	execute		5,comp_list_5_0
wait_compared_list_6_1:
	otherwise		wait_compared_list_6_0
	get_value		3,1
	get_value		4,2
	get_value		5,6
	proceed
wait_compared_list_6_6:
	suspend		wait_compared_list_6_0
	module_entry		comparator
	predicate		comp_vect,7
comp_vect_7_0:
	try_me_else		comp_vect_7_1
	wait_value		6,7
	collect_value		7
	put_value		7,6
	put_integer		6,0
	execute		7,comp_e_7_0
comp_vect_7_1:
	otherwise		comp_vect_7_0
	get_value		3,1
	get_value		4,2
	put_values_inc		1,6,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
comp_vect_7_3:
	suspend		comp_vect_7_0
	module_entry		comparator
	predicate		comp_e,7
comp_e_7_0:
	try_me_else		comp_e_7_1
	integer		6
	integer		7
	g_less_than		6,7
	put_marked_value		8,6
	put_variable		9,10
	b_set_vector_element		1,8,1,9,8
	put_variable		9,11
	b_set_vector_element		2,6,2,9,9
	create_goal		8
	set_values_inc		1,8,2
	set_values_inc		3,3,5
	set_variable		8,5
	enqueue_goal		8,wait_compared_vect_8_0
	put_values_inc		3,10,2
	execute		5,sort0_5_0
comp_e_7_1:
	try_me_else		comp_e_7_3
	wait_value		6,7
	collect_value		6
	collect_value		7
	get_value		3,1
	get_value		4,2
	get_atom		5,same
	proceed
comp_e_7_3:
	suspend		comp_e_7_0
	module_entry		comparator
	predicate		wait_compared_vect,8
wait_compared_vect_8_0:
	try_me_else		wait_compared_vect_8_1
	wait_atom		8,same
	b_increment		6,6
	execute		7,comp_e_7_0
wait_compared_vect_8_1:
	otherwise		wait_compared_vect_8_0
	collect_value		7
	collect_value		6
	get_value		3,1
	get_value		4,2
	get_value		5,8
	proceed
wait_compared_vect_8_6:
	suspend		wait_compared_vect_8_0
	module_entry		comparator
	predicate		comp_tag_and_value,5
comp_tag_and_value_5_0:
	create_goal		4
	set_variable		1,6
	set_values_inc		2,3,3
	enqueue_goal		4,wait_compared_tag_4_0
	put_void		3
	put_void		4
	put_value		5,6
	execute		5,comp_int_5_0
comp_tag_and_value_5_1:
	suspend		comp_tag_and_value_5_0
	module_entry		comparator
	predicate		wait_compared_tag,4
wait_compared_tag_4_0:
	try_me_else		wait_compared_tag_4_1
	wait_atom		1,same
	put_value		5,4
	put_values_inc		1,2,2
	put_void		3
	put_void		4
	execute		5,comp_int_5_0
wait_compared_tag_4_1:
	otherwise		wait_compared_tag_4_0
	collect_value		3
	collect_value		2
	get_value		4,1
	proceed
wait_compared_tag_4_6:
	suspend		wait_compared_tag_4_0
