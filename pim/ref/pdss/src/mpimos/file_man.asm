mpimos_file_manager:
	module		mpimos_file_manager
	entry		create,3,create_3_0
	module_entry		mpimos_file_manager
	predicate		create,3
create_3_0:
	put_variable		5,4
	execute		5,manager_5_0
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_file_manager
	predicate		manager,5
manager_5_0:
	try_me_else		manager_5_1
	list		1
	read_car		1,6
	vector		6
	jump_on_arity		6,7,manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_1
	table_entry		manager_5_4
	table_entry		manager_5_5
manager_5_4:
	read_cdr		1,7
	read_element		6,0,8
	wait_atom		8,directory
	read_elements_inc		6,1,8,4
	collect_list		1
	put_reused_func		1,6,directory
	write_element_marked_value		1,1,9
	write_element_variable		1,2,12
	write_element_marked_value		1,3,10
	write_element_variable		1,4,6
	get_vector_value		2,1
	put_values_dec		1,7,2
	put_value		6,8
	put_value		7,12
	put_value		8,9
	put_value		9,11
	execute		10,create_directory_10_0
manager_5_5:
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,manager_5_1
	bucket_entry_a		create,manager_5_7
	bucket_entry_a		device_create,manager_5_8
manager_5_7:
	read_cdr		1,8
	read_elements_inc		6,1,9,5
	collect_list		1
	put_reused_func		1,6,open
	write_element_marked_value		1,1,10
	write_element_marked_value		1,2,11
	write_element_variable		1,3,7
	write_element_marked_value		1,4,12
	write_element_variable		1,5,6
	get_vector_value		2,1
	put_value		1,8
	put_value		2,6
	put_value		6,9
	put_values_inc		8,10,2
	put_values_dec		10,13,2
	put_atom		12,normal
	execute		12,create_file_12_0
manager_5_8:
	read_cdr		1,8
	read_elements_inc		6,1,9,5
	collect_list		1
	put_reused_func		1,6,open
	write_element_marked_value		1,1,10
	write_element_marked_value		1,2,11
	write_element_variable		1,3,7
	write_element_marked_value		1,4,12
	write_element_variable		1,5,6
	get_vector_value		2,1
	put_value		1,8
	put_value		2,6
	put_value		6,9
	put_values_inc		8,10,2
	put_values_dec		10,13,2
	put_atom		12,device
	execute		12,create_file_12_0
manager_5_1:
	suspend		manager_5_0
	module_entry		mpimos_file_manager
	predicate		create_file,12
create_file_12_0:
	try_me_else		create_file_12_1
	wait_atom		11,'fep#normal'
	atom		12
	branch_on_atom		12,2,create_file_12_1
	bucket_entry_a		device,create_file_12_4
	bucket_entry_a		normal,create_file_12_5
create_file_12_4:
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,11
	set_value		5,5
	enqueue_goal		5,manager_5_0
	put_values_inc		1,6,2
	put_value		3,4
	put_values_dec		4,11,2
	put_values_inc		6,8,2
	execute_external		mpimos_file_device_driver,device_create,7
create_file_12_5:
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,11
	set_value		5,5
	enqueue_goal		5,manager_5_0
	put_values_inc		1,6,2
	put_value		3,4
	put_values_dec		4,11,2
	put_values_inc		6,8,2
	execute_external		mpimos_file_device_driver,create,7
create_file_12_1:
	try_me_else		create_file_12_6
	put_atom		13,'fep#normal'
	g_diff		11,13
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		6
	get_nil		7
	execute		5,manager_5_0
create_file_12_6:
	suspend		create_file_12_0
	module_entry		mpimos_file_manager
	predicate		create_directory,10
create_directory_10_0:
	try_me_else		create_directory_10_1
	wait_atom		10,'fep#normal'
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,10
	set_value		5,5
	enqueue_goal		5,manager_5_0
	put_values_inc		1,6,2
	put_value		3,4
	put_values_dec		4,10,3
	execute_external		mpimos_directory_device_driver,create,6
create_directory_10_1:
	try_me_else		create_directory_10_3
	put_atom		11,'fep#normal'
	g_diff		10,11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		6
	get_nil		7
	execute		5,manager_5_0
create_directory_10_3:
	suspend		create_directory_10_0
