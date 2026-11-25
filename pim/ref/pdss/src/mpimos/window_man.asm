mpimos_window_manager:
	module		mpimos_window_manager
	entry		create,3,create_3_0
	module_entry		mpimos_window_manager
	predicate		create,3
create_3_0:
	put_value		4,2
	put_values_inc		2,3,2
	put_variable		5,4
	execute		5,manager_5_0
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_window_manager
	predicate		manager,5
manager_5_0:
	try_me_else		manager_5_1
	list		1
	read_car		1,6
	jump_on_non_atom		6,manager_5_4
	test_atom		6,switch,manager_5_1
	read_cdr		1,7
	put_func		6,2,switch_next
	write_element_variable		6,1,8
	get_reused_list_val_var		5,1,1,6,6
	put_value		1,7
	put_value		5,6
	put_value		6,8
	execute		6,wait_switch_6_0
manager_5_4:
	is_vector		6,manager_5_1
	jump_on_arity		6,7,manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_5
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_6
	table_entry		manager_5_7
manager_5_5:
	read_element		6,0,7
	atom		7
	branch_on_atom		7,3,manager_5_1
	bucket_entry_a		contents,manager_5_9
	bucket_entry_a		count,manager_5_10
	bucket_entry_a		switch,manager_5_11
manager_5_9:
	read_cdr		1,8
	read_element		6,1,9
	put_reused_func		6,6,contents
	write_element_value		6,1,9
	get_reused_list_val_var		5,1,1,6,6
	put_structured_constant		1,'$SCNST_0'
	get_list_val_var		4,7,1,5
	put_value		1,8
	put_values_inc		4,5,2
	execute		5,manager_5_0
manager_5_10:
	read_cdr		1,8
	read_element		6,1,9
	put_structured_constant		7,'$SCNST_1'
	get_reused_list_val_var		5,1,1,7,7
	put_reused_func		1,6,count
	write_element_value		1,1,9
	get_list_val_var		4,6,1,5
	put_value		1,8
	put_value		4,5
	put_value		5,7
	execute		5,manager_5_0
manager_5_11:
	read_cdr		1,8
	read_element		6,1,9
	collect_vector		6
	put_func		6,3,switch
	write_element_value		6,1,9
	write_element_variable		6,2,7
	get_reused_list_val_var		5,1,1,6,6
	put_value		1,8
	put_values_inc		5,6,2
	execute		6,wait_switch_6_0
manager_5_6:
	read_cdr		1,7
	read_element		6,0,8
	wait_atom		8,create
	read_elements_inc		6,1,8,4
	collect_list		1
	put_reused_func		1,6,create
	write_element_marked_value		1,1,9
	write_element_variable		1,2,12
	write_element_marked_value		1,3,10
	write_element_variable		1,4,6
	get_vector_value		3,1
	put_value		1,7
	put_value		3,6
	put_values_inc		6,8,2
	put_values_dec		8,11,2
	put_value		10,12
	put_atom		11,device
	execute		11,wait_create_11_0
manager_5_7:
	read_cdr		1,7
	read_element		6,0,8
	wait_atom		8,create
	read_elements_inc		6,1,8,5
	collect_list		1
	collect_vector		6
	put_func		1,5,create
	write_element_marked_value		1,1,9
	write_element_variable		1,2,14
	write_element_marked_value		1,3,10
	write_element_variable		1,4,6
	get_vector_value		3,1
	put_func		13,2,normal
	write_element_value		13,1,12
	put_value		1,7
	put_value		3,6
	put_values_inc		6,8,2
	put_values_dec		8,11,2
	put_values_dec		10,14,2
	execute		11,wait_create_11_0
manager_5_1:
	suspend		manager_5_0
	module_entry		mpimos_window_manager
	predicate		wait_create,11
wait_create_11_0:
	try_me_else		wait_create_11_1
	wait_atom		9,'fep#normal'
	jump_on_non_atom		11,wait_create_11_4
	test_atom		11,device,wait_create_11_1
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,2
	set_value		5,5
	enqueue_goal		5,manager_5_0
	put_value		1,4
	put_value		3,6
	put_value		4,8
	put_value		5,10
	put_value		6,7
	execute_external		mpimos_window_device_driver,device_create,6
wait_create_11_4:
	check_vector		11,2,wait_create_11_1
	read_element		11,0,12
	wait_atom		12,normal
	read_element		11,1,9
	collect_vector		11
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,2
	set_value		5,5
	enqueue_goal		5,manager_5_0
	put_value		1,4
	put_value		3,6
	put_value		4,8
	put_value		5,10
	put_value		6,7
	put_value		7,9
	execute_external		mpimos_window_device_driver,create,7
wait_create_11_1:
	try_me_else		wait_create_11_5
	put_atom		12,'fep#normal'
	g_diff		9,12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	execute		5,manager_5_0
wait_create_11_5:
	suspend		wait_create_11_0
	module_entry		mpimos_window_manager
	predicate		wait_switch,6
wait_switch_6_0:
	try_me_else		wait_switch_6_1
	list		4
	read_car		4,7
	vector		7
	jump_on_arity		7,4,wait_switch_6_1
	table_entry		wait_switch_6_1
	table_entry		wait_switch_6_1
	table_entry		wait_switch_6_4
	table_entry		wait_switch_6_5
wait_switch_6_4:
	read_element		7,0,8
	atom		8
	branch_on_atom		8,2,wait_switch_6_1
	bucket_entry_a		switch,wait_switch_6_7
	bucket_entry_a		switch_next,wait_switch_6_8
wait_switch_6_7:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_value		6
	collect_value		10
	collect_vector		7
	put_value		4,9
	execute		5,manager_5_0
wait_switch_6_8:
	read_cdr		4,9
	read_element		7,1,10
	collect_list		4
	collect_value		6
	collect_value		10
	collect_vector		7
	put_value		4,9
	execute		5,manager_5_0
wait_switch_6_5:
	read_cdr		4,8
	read_element		7,0,9
	wait_atom		9,switch
	read_elements_inc		7,1,9,2
	collect_list		4
	collect_value		6
	collect_value		10
	collect_value		9
	collect_vector		7
	put_value		4,8
	execute		5,manager_5_0
wait_switch_6_1:
	try_me_else		wait_switch_6_9
	wait_atom		6,success
	execute		5,manager_5_0
wait_switch_6_9:
	suspend		wait_switch_6_0
	begin_const_section		mpimos_window_manager
'$SCNST_0_2':
	define_desc		11,2
	define_integer		1397641027
	define_integer		4541519
'$SCNST_0_1':
	define_string		'$SCNST_0_2'
	define_atom		[]
'$SCNST_0_0':
	define_desc		0,2
	define_atom		contents
	define_list		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		count
	define_integer		1
'$SCNST_1':
	define_vector		'$SCNST_1_0'
