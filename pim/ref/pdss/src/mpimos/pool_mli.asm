mpimos_monogyny_list_index:
	module		mpimos_monogyny_list_index
	entry		create,1,create_1_0
	module_entry		mpimos_monogyny_list_index
	predicate		create,1
create_1_0:
	put_variable		3,2
	execute		3,monogyny_list_index_3_0
create_1_1:
	suspend		create_1_0
	module_entry		mpimos_monogyny_list_index
	predicate		monogyny_list_index,3
monogyny_list_index_3_0:
	try_me_else		monogyny_list_index_3_1
	jump_on_non_list_var_var		1,monogyny_list_index_3_3,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_3:
	check_nil		1,monogyny_list_index_3_1
	get_nil		2
	put_void		1
	put_void		2
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_1:
	try_me_else		monogyny_list_index_3_4
	jump_on_non_list		3,monogyny_list_index_3_6
	read_car		3,4
	jump_on_non_atom		4,monogyny_list_index_3_8
	test_atom		4,clear,monogyny_list_index_3_4
	read_cdr		3,5
	collect_list		3
	put_value		3,5
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_8:
	is_vector		4,monogyny_list_index_3_4
	jump_on_arity		4,5,monogyny_list_index_3_4
	table_entry		monogyny_list_index_3_4
	table_entry		monogyny_list_index_3_4
	table_entry		monogyny_list_index_3_9
	table_entry		monogyny_list_index_3_10
	table_entry		monogyny_list_index_3_11
monogyny_list_index_3_9:
	read_cdr		3,5
	read_element		4,0,6
	wait_atom		6,count
	read_element		4,1,6
	collect_list		3
	collect_value		5
	collect_vector		4
	get_integer		6,0
	put_void		3
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_10:
	read_cdr		3,5
	read_element		4,0,6
	wait_atom		6,put_at
	read_elements_inc		4,1,6,2
	collect_list		3
	collect_vector		4
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,2
	enqueue_goal		3,monogyny_list_index_3_0
	put_value		1,5
	put_values_inc		3,6,2
	execute		4,entry_4_0
monogyny_list_index_3_11:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,monogyny_list_index_3_4
	bucket_entry_a		get_at,monogyny_list_index_3_13
	bucket_entry_a		remove_at,monogyny_list_index_3_14
monogyny_list_index_3_13:
	read_cdr		3,6
	read_elements_inc		4,1,7,3
	collect_list		3
	collect_value		8
	collect_value		7
	collect_vector		4
	get_atom		9,fail
	put_value		3,6
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_14:
	read_cdr		3,6
	read_elements_inc		4,1,7,3
	collect_list		3
	collect_value		8
	collect_value		7
	collect_vector		4
	get_atom		9,fail
	put_value		3,6
	execute		3,monogyny_list_index_3_0
monogyny_list_index_3_6:
	check_nil		3,monogyny_list_index_3_4
	collect_value		2
	collect_value		1
	proceed
monogyny_list_index_3_4:
	suspend		monogyny_list_index_3_0
	module_entry		mpimos_monogyny_list_index
	predicate		entry,4
entry_4_0:
	try_me_else		entry_4_1
	jump_on_non_list		1,entry_4_3
	read_car		1,5
	jump_on_non_atom		5,entry_4_5
	test_atom		5,clear,entry_4_1
	read_cdr		1,6
	collect_value		4
	collect_value		3
	put_reused_list		3,1
	write_car_atom		3,clear
	write_cdr_variable		3,1
	get_list_value		2,3
	get_value		6,1
	proceed
entry_4_5:
	is_vector		5,entry_4_1
	jump_on_arity		5,5,entry_4_1
	table_entry		entry_4_1
	table_entry		entry_4_1
	table_entry		entry_4_6
	table_entry		entry_4_7
	table_entry		entry_4_8
entry_4_6:
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,count
	read_element		5,1,7
	put_variable		8,9
	b_increment		8,8
	get_value		7,8
	put_reused_func		5,5,count
	write_element_value		5,1,9
	get_reused_list_val_var		2,1,1,5,5
	put_values_dec		1,6,2
	execute		4,entry_4_0
entry_4_7:
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,put_at
	read_elements_inc		5,1,7,2
	wait_value		8,4
	collect_list		1
	collect_value		3
	collect_value		8
	collect_vector		5
	put_value		1,6
	put_value		3,7
	execute		4,entry_4_0
entry_4_8:
	read_element		5,0,6
	atom		6
	branch_on_atom		6,2,entry_4_1
	bucket_entry_a		get_at,entry_4_10
	bucket_entry_a		remove_at,entry_4_11
entry_4_10:
	read_cdr		1,7
	read_element		5,1,8
	read_element		5,2,10
	wait_value		10,4
	read_element		5,3,9
	collect_list		1
	collect_value		10
	collect_vector		5
	get_atom		9,success
	put_marked_value		3,3
	get_value		3,8
	put_value		1,7
	execute		4,entry_4_0
entry_4_11:
	read_cdr		1,7
	read_element		5,1,8
	read_element		5,2,10
	wait_value		10,4
	read_element		5,3,9
	collect_list		1
	collect_value		4
	collect_value		10
	collect_vector		5
	get_value		8,3
	get_atom		9,success
	get_value		7,2
	proceed
entry_4_3:
	check_nil		1,entry_4_1
	collect_value		4
	collect_value		3
	get_nil		2
	proceed
entry_4_1:
	otherwise		entry_4_0
	try_me_else		entry_4_22
	wait_list_var_var		1,5,6
	get_reused_list_val_var		2,1,1,5,5
	put_values_dec		1,6,2
	execute		4,entry_4_0
entry_4_22:
	suspend		entry_4_0
