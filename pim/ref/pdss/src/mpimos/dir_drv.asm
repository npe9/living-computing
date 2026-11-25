mpimos_directory_device_driver:
	module		mpimos_directory_device_driver
	entry		create,6,create_6_0
	module_entry		mpimos_directory_device_driver
	predicate		create,6
create_6_0:
	execute		6,directory_6_0
create_6_1:
	suspend		create_6_0
	module_entry		mpimos_directory_device_driver
	predicate		directory,6
directory_6_0:
	try_me_else		directory_6_1
	wait_atom		5,die
	collect_value		6
	collect_value		1
	get_nil		2
	get_value		3,4
	proceed
directory_6_1:
	try_me_else		directory_6_6
	jump_on_non_list		1,directory_6_8
	read_car		1,7
	vector		7
	jump_on_arity		7,5,directory_6_6
	table_entry		directory_6_6
	table_entry		directory_6_6
	table_entry		directory_6_10
	table_entry		directory_6_11
	table_entry		directory_6_12
directory_6_10:
	read_cdr		1,8
	read_element		7,0,9
	wait_atom		9,expunge
	read_element		7,1,9
	collect_list		1
	collect_vector		7
	put_func		1,3,expunge
	write_element_value		1,1,9
	write_element_variable		1,2,7
	get_vector_value		2,1
	put_values_dec		1,8,2
	execute		6,directory_6_0
directory_6_11:
	read_element		7,0,8
	atom		8
	hash_on_atom		8,4,directory_6_6
	bucket_entry_a		delete,directory_6_14
	bucket_entry_a		pathname,directory_6_15
	bucket_entry_a		purge,directory_6_16
	bucket_entry_a		undelete,directory_6_17
directory_6_14:
	read_cdr		1,9
	read_elements_inc		7,1,10,2
	collect_list		1
	collect_vector		7
	put_func		1,4,delete
	write_elements_inc		1,1,10,2
	write_element_variable		1,3,7
	get_vector_value		2,1
	put_value		1,9
	put_value		2,7
	execute		6,directory_6_0
directory_6_15:
	read_cdr		1,9
	read_elements_inc		7,1,10,2
	collect_list		1
	collect_vector		7
	put_func		1,4,pathname
	write_elements_inc		1,1,10,2
	write_element_variable		1,3,7
	get_vector_value		2,1
	put_value		1,9
	put_value		2,7
	execute		6,directory_6_0
directory_6_16:
	read_cdr		1,9
	read_elements_inc		7,1,10,2
	collect_list		1
	collect_vector		7
	put_func		1,4,purge
	write_elements_inc		1,1,10,2
	write_element_variable		1,3,7
	get_vector_value		2,1
	put_value		1,9
	put_value		2,7
	execute		6,directory_6_0
directory_6_17:
	read_cdr		1,9
	read_elements_inc		7,1,10,2
	collect_list		1
	collect_vector		7
	put_func		1,4,undelete
	write_elements_inc		1,1,10,2
	write_element_variable		1,3,7
	get_vector_value		2,1
	put_value		1,9
	put_value		2,7
	execute		6,directory_6_0
directory_6_12:
	read_element		7,0,8
	atom		8
	branch_on_atom		8,2,directory_6_6
	bucket_entry_a		deleted,directory_6_19
	bucket_entry_a		listing,directory_6_20
directory_6_19:
	read_cdr		1,9
	read_elements_inc		7,1,10,3
	collect_list		1
	collect_vector		7
	put_func		8,5,deleted
	write_element_value		8,1,10
	write_element_variable		8,2,7
	write_element_value		8,3,12
	write_element_variable		8,4,1
	get_vector_value		2,8
	create_goal		6
	set_value		1,9
	set_value		2,1
	set_values_inc		3,3,2
	set_marked_value		5,5
	set_value		6,6
	enqueue_goal		6,directory_6_0
	put_value		1,11
	put_value		2,7
	put_value		3,5
	execute		3,listing_3_0
directory_6_20:
	read_cdr		1,9
	read_elements_inc		7,1,10,3
	collect_list		1
	collect_vector		7
	put_func		8,5,listing
	write_element_value		8,1,10
	write_element_variable		8,2,7
	write_element_value		8,3,12
	write_element_variable		8,4,1
	get_vector_value		2,8
	create_goal		6
	set_value		1,9
	set_value		2,1
	set_values_inc		3,3,2
	set_marked_value		5,5
	set_value		6,6
	enqueue_goal		6,directory_6_0
	put_value		1,11
	put_value		2,7
	put_value		3,5
	execute		3,listing_3_0
directory_6_8:
	check_nil		1,directory_6_6
	collect_value		6
	collect_value		5
	get_nil		2
	get_value		3,4
	proceed
directory_6_6:
	suspend		directory_6_0
	module_entry		mpimos_directory_device_driver
	predicate		listing,3
listing_3_0:
	try_me_else		listing_3_1
	wait_atom		3,die
	collect_value		1
	get_nil		2
	proceed
listing_3_1:
	try_me_else		listing_3_6
	jump_on_non_list_var_var		1,listing_3_8,7,4
	wait_vector		7,3
	read_element		7,0,5
	wait_atom		5,next_file_name
	read_elements_inc		7,1,5,2
	collect_list		1
	collect_vector		7
	put_func		1,4,next_file_name
	write_elements_inc		1,1,5,2
	write_element_variable		1,3,5
	get_vector_value		2,1
	put_values_inc		1,4,2
	execute		3,listing_3_0
listing_3_8:
	check_nil		1,listing_3_6
	collect_value		3
	get_nil		2
	proceed
listing_3_6:
	suspend		listing_3_0
