queue:
	module		queue
	entry		queue,1,queue_1_0
	module_entry		queue
	predicate		queue,1
queue_1_0:
	b_merge		3,2
	get_value		3,1
	put_value		1,2
	put_variable		3,2
	put_integer		4,0
	execute		4,queue_4_0
queue_1_1:
	suspend		queue_1_0
	module_entry		queue
	predicate		queue,4
queue_4_0:
	try_me_else		queue_4_1
	jump_on_non_list		1,queue_4_3
	read_car		1,5
	wait_vector		5,2
	read_element		5,0,6
	atom		6
	hash_on_atom		6,7,queue_4_1
	bucket_entry_a		carbon_copy,queue_4_6
	bucket_entry_a		do,queue_4_7
	bucket_entry_a		empty,queue_4_8
	bucket_entry_a		get,queue_4_9
	bucket_entry_a		get_all,queue_4_10
	bucket_entry_a		get_if_any,queue_4_11
	bucket_entry_a		put,queue_4_12
queue_4_6:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_vector		5
	create_goal		4
	set_value		1,7
	set_variable		2,5
	set_value		3,3
	set_marked_value		4,4
	enqueue_goal		4,queue_4_0
	put_value		1,4
	put_value		3,5
	put_value		4,8
	execute		4,carbon_copy_4_0
queue_4_7:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_vector		5
	b_merge		5,1
	get_value		5,8
	create_goal		4
	set_variable		1,5
	set_values_inc		2,2,3
	enqueue_goal		4,queue_4_0
	put_value		2,7
	put_value		3,5
	execute		3,prepend_3_0
queue_4_8:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_vector		5
	create_goal		4
	set_value		1,7
	set_values_inc		2,2,2
	set_marked_value		4,4
	enqueue_goal		4,queue_4_0
	put_value		1,4
	put_value		2,8
	execute		2,empty_2_0
queue_4_9:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_vector		5
	put_value		6,2
	create_goal		4
	set_value		1,7
	set_variable		2,5
	set_value		3,3
	set_variable		4,2
	enqueue_goal		4,queue_4_0
	put_value		1,4
	put_value		3,8
	put_value		4,6
	execute		5,get_5_0
queue_4_10:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_value		4
	collect_vector		5
	get_value		8,2
	get_nil		3
	put_value		1,7
	put_variable		3,2
	put_integer		4,0
	execute		4,queue_4_0
queue_4_11:
	read_cdr		1,7
	read_element		5,1,8
	collect_list		1
	collect_vector		5
	put_value		6,2
	create_goal		4
	set_value		1,7
	set_variable		2,5
	set_value		3,3
	set_variable		4,2
	enqueue_goal		4,queue_4_0
	put_value		1,4
	put_value		3,8
	put_value		4,6
	execute		5,get_if_any_5_0
queue_4_12:
	read_cdr		1,7
	read_element		5,1,8
	collect_vector		5
	get_reused_list_val_var		3,1,1,8,5
	b_increment		4,4
	put_value		1,7
	put_value		3,5
	execute		4,queue_4_0
queue_4_3:
	check_nil		1,queue_4_1
	collect_value		4
	collect_value		3
	collect_value		2
	proceed
queue_4_1:
	otherwise		queue_4_0
	try_me_else		queue_4_22
	wait_list_var_var		1,5,6
	collect_list		1
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		6
	put_integer		2,1024
	put_structured_constant		1,'$SCNST_0'
	b_raise		2,1,5
	proceed
queue_4_22:
	suspend		queue_4_0
	module_entry		queue
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
	module_entry		queue
	predicate		get,5
get_5_0:
	try_me_else		get_5_1
	integer		1
	test_integer		1,0,get_5_3
	collect_value		5
	collect_value		4
	collect_value		2
	put_integer		4,1024
	put_structured_constant		1,'$SCNST_1'
	put_func		2,2,get
	write_element_value		2,1,3
	b_raise		4,1,2
	proceed
get_5_3:
	put_integer		6,0
	g_less_than		6,1
	put_list_val_val		6,3,5
	get_list_value		4,6
	b_decrement		1,1
	get_value		2,1
	proceed
get_5_1:
	suspend		get_5_0
	module_entry		queue
	predicate		get_if_any,5
get_if_any_5_0:
	try_me_else		get_if_any_5_1
	integer		1
	test_integer		1,0,get_if_any_5_3
	put_vector		1,0
	get_vector_value		3,1
	get_integer		2,0
	get_value		5,4
	proceed
get_if_any_5_3:
	put_integer		6,0
	g_less_than		6,1
	put_vector		7,1
	write_element_variable		7,0,6
	get_vector_value		3,7
	put_list_val_val		3,6,5
	get_list_value		4,3
	b_decrement		1,1
	get_value		2,1
	proceed
get_if_any_5_1:
	suspend		get_if_any_5_0
	module_entry		queue
	predicate		carbon_copy,4
carbon_copy_4_0:
	try_me_else		carbon_copy_4_1
	wait_integer		1,0
	get_value		2,3
	get_nil		4
	proceed
carbon_copy_4_1:
	otherwise		carbon_copy_4_0
	try_me_else		carbon_copy_4_6
	wait_list_var_var		2,5,6
	put_reused_list		2,2
	write_car_marked_value		2,5
	write_cdr_variable		2,7
	get_list_value		4,2
	get_list_val_var		3,2,5,4
	b_decrement		1,1
	put_value		2,6
	put_value		3,4
	put_value		4,7
	execute		4,carbon_copy_4_0
carbon_copy_4_6:
	suspend		carbon_copy_4_0
	module_entry		queue
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
	begin_const_section		queue
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
	define_atom		queue
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
	define_atom		queue
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
