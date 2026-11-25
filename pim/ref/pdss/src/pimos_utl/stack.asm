stack:
	module		stack
	entry		stack,2,stack_2_0
	module_entry		stack
	predicate		stack,2
stack_2_0:
	put_value		3,2
	b_merge		4,2
	get_value		4,1
	put_value		1,2
	put_nil		2
	execute		3,stack_3_0
stack_2_1:
	suspend		stack_2_0
	module_entry		stack
	predicate		stack,3
stack_3_0:
	try_me_else		stack_3_1
	jump_on_non_list		1,stack_3_3
	read_car		1,4
	wait_vector		4,2
	read_element		4,0,5
	atom		5
	hash_on_atom		5,7,stack_3_1
	bucket_entry_a		carbon_copy,stack_3_6
	bucket_entry_a		do,stack_3_7
	bucket_entry_a		empty,stack_3_8
	bucket_entry_a		get,stack_3_9
	bucket_entry_a		get_all,stack_3_10
	bucket_entry_a		get_if_any,stack_3_11
	bucket_entry_a		put,stack_3_12
stack_3_6:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	create_goal		3
	set_value		1,6
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,stack_3_0
	put_value		1,2
	put_value		2,4
	put_value		3,7
	execute		3,carbon_copy_3_0
stack_3_7:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	b_merge		4,1
	get_value		4,7
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,stack_3_0
	put_value		2,6
	put_value		3,4
	execute		3,prepend_3_0
stack_3_8:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	create_goal		3
	set_value		1,6
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,stack_3_0
	put_value		1,2
	put_value		2,4
	put_value		3,7
	execute		3,empty_3_0
stack_3_9:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	put_value		4,3
	create_goal		3
	set_value		1,6
	set_variable		2,3
	set_marked_value		3,4
	enqueue_goal		3,stack_3_0
	put_values_inc		1,2,2
	put_value		3,7
	execute		4,get_4_0
stack_3_10:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	get_value		7,2
	put_value		1,6
	put_nil		2
	execute		3,stack_3_0
stack_3_11:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	create_goal		3
	set_value		1,6
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,stack_3_0
	put_value		1,2
	put_value		2,4
	put_value		3,7
	execute		3,get_if_any_3_0
stack_3_12:
	read_cdr		1,6
	read_element		4,1,7
	collect_vector		4
	put_reused_list_val_val		4,1,7,2
	put_value		1,6
	put_value		2,4
	execute		3,stack_3_0
stack_3_3:
	check_nil		1,stack_3_1
	collect_value		3
	collect_value		2
	proceed
stack_3_1:
	otherwise		stack_3_0
	try_me_else		stack_3_22
	wait_list_var_var		1,4,5
	collect_list		1
	collect_value		2
	collect_value		5
	put_integer		5,1024
	put_structured_constant		1,'$SCNST_0'
	put_func		2,3,'$PIMOS$'
	write_element_value		2,1,3
	write_element_value		2,2,1
	b_raise		5,2,4
	proceed
stack_3_22:
	suspend		stack_3_0
	module_entry		stack
	predicate		empty,3
empty_3_0:
	try_me_else		empty_3_1
	wait_nil		1
	get_nil		2
	get_atom		3,yes
	proceed
empty_3_1:
	otherwise		empty_3_0
	get_value		2,1
	get_atom		3,no
	proceed
empty_3_6:
	suspend		empty_3_0
	module_entry		stack
	predicate		get,4
get_4_0:
	try_me_else		get_4_1
	jump_on_non_list_var_var		1,get_4_3,5,6
	collect_list		1
	collect_value		4
	get_value		3,5
	get_value		2,6
	proceed
get_4_3:
	check_nil		1,get_4_1
	collect_value		2
	put_integer		5,1024
	put_structured_constant		1,'$SCNST_1'
	put_func		2,3,'$PIMOS$'
	write_element_value		2,1,4
	write_element_value		2,2,1
	put_func		1,2,get
	write_element_value		1,1,3
	b_raise		5,2,1
	proceed
get_4_1:
	suspend		get_4_0
	module_entry		stack
	predicate		get_if_any,3
get_if_any_3_0:
	try_me_else		get_if_any_3_1
	jump_on_non_list_var_var		1,get_if_any_3_3,4,5
	collect_list		1
	put_vector		1,1
	write_element_value		1,0,4
	get_vector_value		3,1
	get_value		2,5
	proceed
get_if_any_3_3:
	check_nil		1,get_if_any_3_1
	put_vector		1,0
	get_vector_value		3,1
	get_nil		2
	proceed
get_if_any_3_1:
	suspend		get_if_any_3_0
	module_entry		stack
	predicate		carbon_copy,3
carbon_copy_3_0:
	try_me_else		carbon_copy_3_1
	jump_on_non_list_var_var		1,carbon_copy_3_3,4,5
	put_reused_list		1,1
	write_car_marked_value		1,4
	write_cdr_variable		1,6
	get_list_value		3,1
	get_list_val_var		2,1,4,3
	put_value		1,5
	put_value		2,3
	put_value		3,6
	execute		3,carbon_copy_3_0
carbon_copy_3_3:
	check_nil		1,carbon_copy_3_1
	get_nil		2
	get_nil		3
	proceed
carbon_copy_3_1:
	suspend		carbon_copy_3_0
	module_entry		stack
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
	begin_const_section		stack
'$SCNST_0_0':
	define_desc		3,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1936942445
	define_integer		1600481121
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		3,8
	define_integer		1701409396
	define_integer		1869897572
	define_integer		1952802655
	define_integer		1852796511
	define_integer		1936291941
	define_integer		1953391988
	define_integer		1701602655
	define_integer		1953391981
'$SCNST_1':
	define_string		'$SCNST_1_0'
