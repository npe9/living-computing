mpimos_window_device_driver:
	module		mpimos_window_device_driver
	entry		create,7,create_7_0
	entry		device_create,6,device_create_6_0
	module_entry		mpimos_window_device_driver
	predicate		create,7
create_7_0:
	put_func		10,5,reset
	write_element_variable		10,1,8
	write_element_variable		10,2,9
	write_element_void		10,3
	write_element_variable		10,4,11
	get_vector_value		5,10
	b_merge		10,5
	get_value		10,3
	put_func		10,3,status
	write_element_value		10,1,6
	write_element_atom		10,2,normal
	put_value		3,5
	put_value		5,7
	put_value		6,11
	put_void		7
	execute		10,window_10_0
create_7_1:
	suspend		create_7_0
	module_entry		mpimos_window_device_driver
	predicate		device_create,6
device_create_6_0:
	put_value		7,5
	put_func		10,3,status
	write_element_value		10,1,6
	write_element_atom		10,2,device
	put_void		5
	put_value		6,7
	put_void		7
	put_void		8
	put_void		9
	execute		10,window_10_0
device_create_6_1:
	suspend		device_create_6_0
	module_entry		mpimos_window_device_driver
	predicate		window,10
window_10_0:
	try_me_else		window_10_1
	list		1
	read_car		1,11
	vector		11
	jump_on_arity		11,4,window_10_1
	table_entry		window_10_1
	table_entry		window_10_1
	table_entry		window_10_4
	table_entry		window_10_5
window_10_4:
	read_element		11,0,12
	atom		12
	hash_on_atom		12,4,window_10_1
	bucket_entry_a		contents,window_10_7
	bucket_entry_a		count,window_10_8
	bucket_entry_a		switch,window_10_9
	bucket_entry_a		switch_next,window_10_10
window_10_7:
	read_cdr		1,13
	read_element		11,1,14
	put_integer		12,1
	b_vector_element		10,12,10,12
	get_reused_list_val_var		14,1,1,10,10
	put_reused_func		1,11,contents
	write_element_value		1,1,10
	get_list_val_var		2,11,1,10
	put_value		1,13
	put_value		2,10
	put_value		10,12
	execute		10,window_10_0
window_10_8:
	read_cdr		1,13
	read_element		11,1,14
	b_increment		14,12
	put_reused_func		11,11,count
	write_element_value		11,1,12
	get_reused_list_val_var		2,1,1,11,11
	put_value		1,13
	put_value		2,11
	execute		10,window_10_0
window_10_9:
	read_cdr		1,13
	read_element		11,1,14
	collect_list		1
	collect_vector		11
	put_func		1,3,show
	write_element_value		1,1,14
	write_element_variable		1,2,11
	get_vector_value		6,1
	put_value		1,13
	put_value		6,11
	execute		10,window_10_0
window_10_10:
	read_cdr		1,13
	read_element		11,1,14
	put_reused_func		11,11,switch
	write_element_value		11,1,14
	get_reused_list_val_var		2,1,1,11,11
	put_value		1,13
	put_value		2,11
	execute		10,window_10_0
window_10_5:
	read_element		11,0,12
	wait_atom		12,switch
	read_elements_inc		11,1,13,2
	read_cdr		1,15
	vector		10
	try_me_else		window_10_13
	put_integer		16,1
	g_vector_element		10,16,16
	wait_value		13,16
	collect_list		1
	put_reused_func		1,11,show
	write_element_value		1,1,14
	write_element_variable		1,2,11
	get_vector_value		6,1
	put_value		1,15
	put_value		6,11
	execute		10,window_10_0
window_10_13:
	try_me_else		window_10_1
	put_integer		16,1
	g_vector_element		10,16,16
	g_diff		16,13
	put_reused_func		11,11,switch
	write_elements_inc		11,1,13,2
	get_reused_list_val_var		2,1,1,11,11
	put_value		1,15
	put_value		2,11
	execute		10,window_10_0
window_10_1:
	try_me_else		window_10_14
	wait_atom		7,'fep#abort'
	collect_value		9
	collect_value		5
	get_atom		8,'fep#abort'
	put_void		5
	put_void		7
	put_void		8
	put_void		9
	execute		10,window_10_0
window_10_14:
	try_me_else		window_10_16
	wait		9
	vector		10
	try_me_else		window_10_18
	put_integer		11,2
	g_vector_element		10,11,11
	wait_atom		11,normal
	get_atom		8,'fep#abort'
	put_func		13,5,reset
	write_element_variable		13,1,8
	write_element_variable		13,2,12
	write_element_void		13,3
	write_element_variable		13,4,11
	get_vector_value		6,13
	get_list_val_var		5,13,9,6
	put_value		5,6
	put_value		6,11
	put_value		9,12
	execute		10,window_10_0
window_10_18:
	try_me_else		window_10_16
	put_integer		11,2
	g_vector_element		10,11,11
	wait_atom		11,device
	get_value		5,9
	put_void		5
	put_void		9
	execute		10,window_10_0
window_10_16:
	try_me_else		window_10_34
	wait_atom		4,die
	collect_value		10
	collect_value		9
	collect_value		7
	collect_value		3
	get_value		1,2
	get_nil		5
	get_nil		6
	get_atom		8,'fep#abort'
	proceed
window_10_34:
	try_me_else		window_10_39
	jump_on_non_list		3,window_10_41
	read_car		3,11
	vector		11
	jump_on_arity		11,6,window_10_39
	table_entry		window_10_39
	table_entry		window_10_39
	table_entry		window_10_43
	table_entry		window_10_44
	table_entry		window_10_45
	table_entry		window_10_46
window_10_43:
	read_element		11,0,12
	atom		12
	hash_on_atom		12,4,window_10_39
	bucket_entry_a		close,window_10_48
	bucket_entry_a		do,window_10_49
	bucket_entry_a		hide,window_10_50
	bucket_entry_a		show,window_10_51
window_10_48:
	read_cdr		3,13
	read_element		11,1,14
	collect_list		3
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		4
	collect_value		13
	get_value		1,2
	get_nil		5
	put_reused_func		1,11,close
	write_element_value		1,1,14
	get_vector_value		6,1
	proceed
window_10_49:
	read_cdr		3,13
	read_element		11,1,14
	collect_list		3
	collect_vector		11
	create_goal		10
	set_values_inc		1,1,2
	set_variable		3,3
	set_values_inc		4,4,7
	enqueue_goal		10,window_10_0
	put_values_dec		1,14,2
	execute		3,append_3_0
window_10_50:
	read_cdr		3,13
	read_element		11,1,14
	collect_list		3
	collect_vector		11
	put_func		3,3,hide
	write_element_value		3,1,14
	write_element_variable		3,2,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_51:
	read_cdr		3,13
	read_element		11,1,14
	collect_list		3
	collect_vector		11
	put_func		3,3,show
	write_element_value		3,1,14
	write_element_variable		3,2,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_44:
	read_element		11,0,12
	atom		12
	hash_on_atom		12,6,window_10_39
	bucket_entry_a		getc,window_10_53
	bucket_entry_a		getl,window_10_54
	bucket_entry_a		next_attention,window_10_55
	bucket_entry_a		putb,window_10_56
	bucket_entry_a		putc,window_10_57
	bucket_entry_a		putl,window_10_58
window_10_53:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_vector		11
	put_func		3,4,getc
	write_elements_inc		3,1,14,2
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_54:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_vector		11
	put_func		3,4,getl
	write_elements_inc		3,1,14,2
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_55:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_value		9
	collect_value		5
	collect_vector		11
	put_func		3,4,next_attention
	write_element_variable		3,1,9
	write_element_value		3,2,15
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		5,14
	put_value		6,11
	execute		10,window_10_0
window_10_56:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_vector		11
	put_func		3,4,putb
	write_elements_inc		3,1,14,2
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_57:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_vector		11
	put_func		3,4,putc
	write_elements_inc		3,1,14,2
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_58:
	read_cdr		3,13
	read_elements_inc		11,1,14,2
	collect_list		3
	collect_vector		11
	put_func		3,4,putl
	write_elements_inc		3,1,14,2
	write_element_variable		3,3,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_45:
	read_element		11,0,12
	atom		12
	branch_on_atom		12,3,window_10_39
	bucket_entry_a		getb,window_10_60
	bucket_entry_a		gettkn,window_10_61
	bucket_entry_a		reset,window_10_62
window_10_60:
	read_cdr		3,13
	read_elements_inc		11,1,14,3
	collect_list		3
	collect_vector		11
	put_func		3,5,getb
	write_elements_dec		3,1,15,2
	write_element_value		3,3,16
	write_element_variable		3,4,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_61:
	read_cdr		3,13
	read_elements_inc		11,1,14,3
	collect_list		3
	collect_vector		11
	put_func		3,5,gettkn
	write_element_value		3,1,14
	write_elements_dec		3,2,16,2
	write_element_variable		3,4,11
	get_vector_value		6,3
	put_value		3,13
	put_value		6,11
	execute		10,window_10_0
window_10_62:
	read_cdr		3,13
	read_elements_inc		11,1,14,3
	collect_list		3
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		5
	collect_vector		11
	put_func		3,5,reset
	write_element_variable		3,1,8
	write_element_variable		3,2,9
	write_element_value		3,3,16
	write_element_variable		3,4,7
	get_vector_value		6,3
	put_value		3,13
	put_value		5,15
	put_value		6,7
	put_value		7,14
	execute		10,window_10_0
window_10_46:
	read_cdr		3,12
	read_element		11,0,13
	wait_atom		13,putt
	read_elements_inc		11,1,13,4
	collect_list		3
	collect_vector		11
	put_func		3,6,putt
	write_elements_inc		3,1,13,4
	write_element_variable		3,5,11
	get_vector_value		6,3
	put_value		3,12
	put_value		6,11
	execute		10,window_10_0
window_10_41:
	check_nil		3,window_10_39
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		4
	get_value		1,2
	get_nil		5
	get_nil		6
	proceed
window_10_39:
	suspend		window_10_0
	module_entry		mpimos_window_device_driver
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
