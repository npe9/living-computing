mpimos_file_device_driver:
	module		mpimos_file_device_driver
	entry		create,7,create_7_0
	entry		device_create,7,device_create_7_0
	module_entry		mpimos_file_device_driver
	predicate		create,7
create_7_0:
	put_func		8,5,reset
	write_element_variable		8,1,10
	write_element_void		8,2
	write_element_void		8,3
	write_element_variable		8,4,9
	get_vector_value		2,8
	put_func		8,3,atr
	write_elements_inc		8,1,6,2
	put_value		2,9
	put_void		6
	put_value		7,10
	execute		8,file_8_0
create_7_1:
	suspend		create_7_0
	module_entry		mpimos_file_device_driver
	predicate		device_create,7
device_create_7_0:
	put_func		8,3,atr
	write_elements_inc		8,1,6,2
	put_void		6
	put_void		7
	execute		8,file_8_0
device_create_7_1:
	suspend		device_create_7_0
	module_entry		mpimos_file_device_driver
	predicate		file,8
file_8_0:
	try_me_else		file_8_1
	wait_atom		6,'fep#abort'
	get_atom		7,'fep#abort'
	put_void		6
	put_void		7
	execute		8,file_8_0
file_8_1:
	try_me_else		file_8_6
	wait_atom		5,die
	collect_value		8
	collect_value		6
	collect_value		1
	get_nil		2
	get_value		3,4
	get_atom		7,'fep#abort'
	proceed
file_8_6:
	try_me_else		file_8_11
	jump_on_non_list		1,file_8_13
	read_car		1,9
	vector		9
	jump_on_arity		9,6,file_8_11
	table_entry		file_8_11
	table_entry		file_8_11
	table_entry		file_8_15
	table_entry		file_8_16
	table_entry		file_8_17
	table_entry		file_8_18
file_8_15:
	read_element		9,0,10
	atom		10
	branch_on_atom		10,3,file_8_11
	bucket_entry_a		close,file_8_20
	bucket_entry_a		do,file_8_21
	bucket_entry_a		end_of_file,file_8_22
file_8_20:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_func		1,9,close
	write_element_value		1,1,12
	get_vector_value		2,1
	put_value		1,11
	put_void		2
	execute		8,file_8_0
file_8_21:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	create_goal		8
	set_variable		1,9
	set_values_inc		2,2,7
	enqueue_goal		8,file_8_0
	put_values_dec		1,12,2
	put_value		3,9
	execute		3,append_3_0
file_8_22:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	put_func		1,3,end_of_file
	write_element_value		1,1,12
	write_element_variable		1,2,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_16:
	read_element		9,0,10
	atom		10
	hash_on_atom		10,6,file_8_11
	bucket_entry_a		getc,file_8_24
	bucket_entry_a		getl,file_8_25
	bucket_entry_a		pathname,file_8_26
	bucket_entry_a		putb,file_8_27
	bucket_entry_a		putc,file_8_28
	bucket_entry_a		putl,file_8_29
file_8_24:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,getc
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_25:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,getl
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_26:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,pathname
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_27:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,putb
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_28:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,putc
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_29:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	put_func		1,4,putl
	write_elements_inc		1,1,12,2
	write_element_variable		1,3,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_17:
	read_element		9,0,10
	atom		10
	branch_on_atom		10,3,file_8_11
	bucket_entry_a		getb,file_8_31
	bucket_entry_a		gettkn,file_8_32
	bucket_entry_a		reset,file_8_33
file_8_31:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	collect_list		1
	collect_vector		9
	put_func		1,5,getb
	write_elements_dec		1,1,13,2
	write_element_value		1,3,14
	write_element_variable		1,4,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_32:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	collect_list		1
	collect_vector		9
	put_func		1,5,gettkn
	write_element_value		1,1,12
	write_elements_dec		1,2,14,2
	write_element_variable		1,4,9
	get_vector_value		2,1
	put_value		1,11
	put_value		2,9
	execute		8,file_8_0
file_8_33:
	read_cdr		1,11
	read_elements_inc		9,1,12,3
	collect_list		1
	collect_value		7
	collect_value		6
	collect_value		13
	collect_vector		9
	put_func		1,5,reset
	write_element_variable		1,1,7
	write_element_void		1,2
	write_element_value		1,3,14
	write_element_variable		1,4,6
	get_vector_value		2,1
	put_value		1,11
	put_value		2,6
	put_value		6,12
	execute		8,file_8_0
file_8_18:
	read_cdr		1,10
	read_element		9,0,11
	wait_atom		11,putt
	read_elements_inc		9,1,11,4
	collect_list		1
	collect_vector		9
	put_func		1,6,putt
	write_elements_inc		1,1,11,4
	write_element_variable		1,5,9
	get_vector_value		2,1
	put_values_dec		1,10,2
	execute		8,file_8_0
file_8_13:
	check_nil		1,file_8_11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_nil		2
	get_value		3,4
	proceed
file_8_11:
	suspend		file_8_0
	module_entry		mpimos_file_device_driver
	predicate		append,3
append_3_0:
	try_me_else		append_3_1
	jump_on_non_list_var_var		1,append_3_3,4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		3,4
	execute		3,append_3_0
append_3_3:
	check_nil		1,append_3_1
	get_value		3,2
	proceed
append_3_1:
	suspend		append_3_0
