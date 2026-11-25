mpimos_timer_manager:
	module		mpimos_timer_manager
	entry		create,3,create_3_0
	module_entry		mpimos_timer_manager
	predicate		create,3
create_3_0:
	execute		3,manager_3_0
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_timer_manager
	predicate		manager,3
manager_3_0:
	try_me_else		manager_3_1
	list		1
	read_car		1,4
	vector		4
	jump_on_arity		4,5,manager_3_1
	table_entry		manager_3_1
	table_entry		manager_3_1
	table_entry		manager_3_1
	table_entry		manager_3_4
	table_entry		manager_3_5
manager_3_4:
	read_cdr		1,5
	read_element		4,0,6
	wait_atom		6,get_count
	read_elements_inc		4,1,6,2
	collect_list		1
	collect_vector		4
	put_func		1,4,get_count
	write_elements_inc		1,1,6,2
	write_element_variable		1,3,4
	get_vector_value		2,1
	put_values_dec		1,5,2
	execute		3,manager_3_0
manager_3_5:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,manager_3_1
	bucket_entry_a		on_after,manager_3_7
	bucket_entry_a		on_at,manager_3_8
manager_3_7:
	read_cdr		1,6
	read_elements_inc		4,1,7,3
	collect_list		1
	collect_vector		4
	put_func		1,5,on_after
	write_elements_inc		1,1,7,3
	write_element_variable		1,4,4
	get_vector_value		2,1
	put_value		1,6
	put_value		2,4
	execute		3,manager_3_0
manager_3_8:
	read_cdr		1,6
	read_elements_inc		4,1,7,3
	collect_list		1
	collect_vector		4
	put_func		1,5,on_at
	write_elements_inc		1,1,7,3
	write_element_variable		1,4,4
	get_vector_value		2,1
	put_value		1,6
	put_value		2,4
	execute		3,manager_3_0
manager_3_1:
	suspend		manager_3_0
