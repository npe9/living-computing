mpimos_task_monitor:
	module		mpimos_task_monitor
	entry		create,12,create_12_0
	entry		error_monitor,2,error_monitor_2_0
	entry		error_monitor,3,error_monitor_3_0
	module_entry		mpimos_task_monitor
	predicate		create,12
create_12_0:
	b_merge		13,14
	get_value		14,9
	b_merge		9,14
	get_value		14,10
	create_goal		10
	set_variable		1,10
	set_variable		2,14
	set_values_inc		3,7,2
	set_value		5,13
	set_value		6,9
	set_value		7,11
	set_atom		8,stop
	set_void		9
	set_value		10,12
	enqueue_goal		10,monitor_10_0
	put_integer		7,4096
	b_rate		7,7
	create_goal		8
	set_values_inc		1,1,6
	set_value		7,14
	set_value		8,10
	enqueue_goal_with_priority		8,'$Sho-en:create/8_8_0',7
	proceed
create_12_1:
	suspend		create_12_0
	module_entry		mpimos_task_monitor
	predicate		monitor,10
monitor_10_0:
	try_me_else		monitor_10_1
	list		3
	read_car		3,11
	jump_on_non_atom		11,monitor_10_4
	hash_on_atom		11,4,monitor_10_1
	bucket_entry_a		abort,monitor_10_5
	bucket_entry_a		remove,monitor_10_6
	bucket_entry_a		start,monitor_10_7
	bucket_entry_a		stop,monitor_10_8
monitor_10_5:
	read_cdr		3,12
	collect_value		8
	put_reused_list		8,3
	write_car_atom		8,abort
	write_cdr_variable		8,3
	get_list_value		2,8
	put_value		2,3
	put_value		3,12
	put_atom		8,abort
	execute		10,monitor_10_0
monitor_10_6:
	read_cdr		3,12
	collect_list		3
	collect_value		10
	collect_value		8
	collect_value		12
	collect_value		1
	get_nil		2
	get_atom		9,die
	get_nil		4
	get_nil		5
	get_nil		6
	get_nil		7
	proceed
monitor_10_7:
	read_cdr		3,12
	collect_value		8
	put_reused_list		8,3
	write_car_atom		8,start
	write_cdr_variable		8,3
	get_list_value		2,8
	put_value		2,3
	put_value		3,12
	put_atom		8,active
	execute		10,monitor_10_0
monitor_10_8:
	read_cdr		3,12
	collect_value		8
	put_reused_list		8,3
	write_car_atom		8,stop
	write_cdr_variable		8,3
	get_list_value		2,8
	put_value		2,3
	put_value		3,12
	put_atom		8,stop
	execute		10,monitor_10_0
monitor_10_4:
	is_vector		11,monitor_10_1
	jump_on_arity		11,4,monitor_10_1
	table_entry		monitor_10_1
	table_entry		monitor_10_1
	table_entry		monitor_10_9
	table_entry		monitor_10_10
monitor_10_9:
	read_element		11,0,12
	atom		12
	branch_on_atom		12,2,monitor_10_1
	bucket_entry_a		more_reduction,monitor_10_12
	bucket_entry_a		statistics,monitor_10_13
monitor_10_12:
	read_cdr		3,13
	read_element		11,1,14
	put_reused_func		11,11,more_reduction
	write_element_value		11,1,14
	get_reused_list_val_var		2,12,3,11,3
	put_value		2,3
	put_value		3,13
	execute		10,monitor_10_0
monitor_10_13:
	read_cdr		3,13
	read_element		11,1,14
	put_reused_func		11,11,statistics
	write_element_value		11,1,14
	get_reused_list_val_var		2,12,3,11,3
	put_value		2,3
	put_value		3,13
	execute		10,monitor_10_0
monitor_10_10:
	read_cdr		3,12
	read_element		11,0,13
	wait_atom		13,priority
	read_elements_inc		11,1,13,2
	put_reused_func		11,11,priority
	write_elements_inc		11,1,13,2
	get_reused_list_val_var		2,13,3,11,3
	put_value		2,3
	put_value		3,12
	execute		10,monitor_10_0
monitor_10_1:
	try_me_else		monitor_10_20
	list		1
	read_car		1,11
	jump_on_non_atom		11,monitor_10_23
	branch_on_atom		11,3,monitor_10_20
	bucket_entry_a		aborted,monitor_10_24
	bucket_entry_a		reduction_limit,monitor_10_25
	bucket_entry_a		succeeded,monitor_10_26
monitor_10_24:
	read_cdr		1,12
	put_reused_list		1,1
	write_car_atom		1,aborted
	write_cdr_variable		1,11
	get_list_value		4,1
	put_value		1,12
	put_value		4,11
	execute		10,monitor_10_0
monitor_10_25:
	read_cdr		1,12
	put_func		11,2,reduction_limit
	write_element_variable		11,1,13
	get_reused_list_val_var		4,1,1,11,11
	b_merge		1,4
	put_vector		14,2
	write_element_value		14,0,13
	write_element_value		14,1,3
	get_vector_value		1,14
	put_value		1,12
	put_value		3,4
	put_value		4,11
	execute		10,monitor_10_0
monitor_10_26:
	read_cdr		1,12
	put_reused_list		1,1
	write_car_atom		1,succeeded
	write_cdr_variable		1,11
	get_list_value		4,1
	put_value		1,12
	put_value		4,11
	execute		10,monitor_10_0
monitor_10_23:
	is_vector		11,monitor_10_20
	jump_on_arity		11,9,monitor_10_20
	table_entry		monitor_10_20
	table_entry		monitor_10_20
	table_entry		monitor_10_20
	table_entry		monitor_10_20
	table_entry		monitor_10_27
	table_entry		monitor_10_28
	table_entry		monitor_10_29
	table_entry		monitor_10_30
	table_entry		monitor_10_31
monitor_10_27:
	read_element		11,0,12
	wait_atom		12,deadlock
	read_element		11,1,13
	integer		13
	test_integer		13,0,monitor_10_34
	read_cdr		1,14
	read_elements_inc		11,2,15,2
	collect_value		15
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,17
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,do
	write_element_variable		1,1,15
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_0'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,13
	put_list_val_val		12,11,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,12
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	put_list		11
	write_car_atom		11,stop
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		11
	set_value		1,14
	set_value		2,6
	set_variable		3,6
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	set_variable		11,1
	enqueue_goal		11,wait_flush_11_0
	create_goal		3
	set_value		1,3
	set_value		2,6
	set_value		3,1
	enqueue_goal		3,wait_request_3_0
	create_goal		3
	set_value		1,4
	put_list		1
	write_car_atom		1,deadlock
	write_cdr_value		1,2
	set_value		2,1
	set_value		3,17
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_values_dec		1,16,2
	enqueue_goal		2,put_procedures_list_2_0
	put_integer		1,0
	put_value		2,13
	execute		2,deadlock_table_2_0
monitor_10_34:
	read_cdr		1,14
	read_elements_inc		11,2,15,2
	put_integer		17,0
	g_less_than		17,13
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,21
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,19
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		11,1,12
	put_func		1,2,putb
	write_element_variable		1,1,18
	put_list_val_val		12,1,11
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,12
	put_func		11,2,do
	write_element_variable		11,1,20
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,17
	put_list_val_val		12,11,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,12
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	put_list		11
	write_car_atom		11,stop
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		11
	set_value		1,14
	set_value		2,6
	set_variable		3,6
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	set_variable		11,1
	enqueue_goal		11,wait_flush_11_0
	create_goal		3
	set_value		1,3
	set_value		2,6
	set_value		3,1
	enqueue_goal		3,wait_request_3_0
	create_goal		3
	set_value		1,4
	put_list		1
	write_car_atom		1,deadlock
	write_cdr_value		1,2
	set_value		2,1
	set_value		3,21
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_value		1,16
	set_value		2,20
	enqueue_goal		2,put_procedures_list_2_0
	create_goal		2
	set_value		1,15
	set_value		2,19
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		2
	set_marked_value		1,13
	set_value		2,18
	enqueue_goal		2,occured_table_2_0
	put_value		1,13
	put_value		2,17
	execute		2,deadlock_table_2_0
monitor_10_28:
	read_cdr		1,12
	read_element		11,0,13
	wait_atom		13,raised
	read_elements_inc		11,1,13,4
	collect_list		1
	collect_vector		11
	put_value		1,12
	put_values_inc		11,13,4
	execute		14,request_14_0
monitor_10_29:
	read_element		11,0,12
	wait_atom		12,exception
	read_element		11,1,13
	try_me_else		monitor_10_36
	wait_integer		13,17
	read_cdr		1,14
	read_elements_inc		11,2,15,4
	collect_vector		11
	put_reused_list		1,1
	write_car_atom		1,stop
	write_cdr_variable		1,12
	get_list_value		2,1
	put_func		1,3,getenv
	write_element_atom		1,1,auto_load
	write_element_variable		1,2,11
	get_list_val_var		7,2,1,13
	put_value		1,14
	put_value		2,12
	put_value		7,13
	put_values_inc		12,15,4
	execute		15,wait_auto_load_env_15_0
monitor_10_36:
	read_elements_inc		11,2,14,4
	read_cdr		1,18
	try_me_else		monitor_10_20
	put_integer		19,17
	g_diff		13,19
	collect_value		17
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,20
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,19
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,17
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	get_nil		16
	put_list		11
	write_car_atom		11,abort
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		10
	set_value		1,18
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,20
	enqueue_goal		3,wait_flush_3_0
	create_goal		3
	set_values_inc		1,14,2
	set_value		3,19
	enqueue_goal		3,code_to_goal_3_0
	put_value		1,13
	put_value		2,17
	execute		2,code_table_2_0
monitor_10_30:
	read_element		11,0,12
	wait_atom		12,exception
	read_element		11,1,13
	try_me_else		monitor_10_39
	wait_integer		13,10
	read_cdr		1,14
	read_elements_inc		11,2,15,5
	collect_value		19
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,22
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,21
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_5'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putt
	write_element_variable		11,1,20
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_6'
	put_list_val_val		11,1,12
	put_func		1,2,putt
	write_element_variable		1,1,19
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,13
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_8'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	get_nil		18
	put_list		11
	write_car_atom		11,abort
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		10
	set_value		1,14
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,22
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_value		1,17
	set_value		2,21
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		2
	set_value		1,16
	set_value		2,20
	enqueue_goal_external		mpimos_utility,freeze,2
	create_goal		2
	set_value		1,15
	set_value		2,19
	enqueue_goal_external		mpimos_utility,freeze,2
	put_integer		1,10
	put_value		2,13
	execute		2,code_table_2_0
monitor_10_39:
	read_elements_inc		11,2,14,5
	read_cdr		1,19
	try_me_else		monitor_10_20
	put_integer		20,10
	g_diff		13,20
	collect_value		18
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,22
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,21
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_9'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putt
	write_element_variable		11,1,20
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_10'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,18
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_11'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	get_nil		17
	put_list		11
	write_car_atom		11,abort
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		10
	set_value		1,19
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,22
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_value		1,16
	set_value		2,21
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		3
	set_variable		1,1
	set_value		2,15
	set_value		3,20
	enqueue_goal		3,construct_goal_3_0
	create_goal		2
	set_value		1,14
	set_value		2,1
	enqueue_goal_external		mpimos_opcode_table,op,2
	put_value		1,13
	put_value		2,18
	execute		2,code_table_2_0
monitor_10_31:
	read_element		11,0,12
	wait_atom		12,exception
	read_element		11,1,13
	try_me_else		monitor_10_42
	wait_integer		13,8
	read_cdr		1,14
	read_elements_inc		11,2,15,6
	collect_value		20
	collect_value		16
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,22
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,21
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_12'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putt
	write_element_variable		11,1,16
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_13'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putt
	write_element_variable		11,1,20
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_14'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putb
	write_element_variable		11,1,13
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_15'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	get_nil		19
	put_list		11
	write_car_atom		11,abort
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		10
	set_value		1,14
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,22
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_value		1,18
	set_value		2,21
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		2
	set_value		1,17
	set_value		2,20
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		2
	set_values_inc		1,15,2
	enqueue_goal_external		mpimos_utility,freeze,2
	put_integer		1,8
	put_value		2,13
	execute		2,code_table_2_0
monitor_10_42:
	read_elements_inc		11,2,14,6
	read_cdr		1,20
	try_me_else		monitor_10_20
	put_integer		21,8
	g_diff		13,21
	collect_value		19
	collect_vector		11
	put_func		11,2,flush
	write_element_variable		11,1,22
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,putt
	write_element_variable		1,1,21
	put_list_val_val		12,1,11
	put_structured_constant		1,'$SCNST_16'
	put_list_val_val		11,1,12
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,11
	put_func		11,2,putt
	write_element_variable		11,1,19
	put_list_val_val		12,11,1
	put_structured_constant		1,'$SCNST_17'
	put_list_val_val		11,1,12
	put_structured_constant		1,'$SCNST_18'
	put_list_val_val		12,1,11
	put_func		1,2,putt
	write_element_value		1,1,16
	put_list_val_val		11,1,12
	put_structured_constant		1,'$SCNST_19'
	put_list_val_val		12,1,11
	put_func		1,2,putb
	write_element_variable		1,1,16
	put_list_val_val		11,1,12
	put_structured_constant		1,'$SCNST_20'
	put_list_val_val		12,1,11
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,12
	put_func		11,2,do
	write_element_value		11,1,1
	get_list_val_var		6,12,11,1
	get_nil		18
	put_list		11
	write_car_atom		11,abort
	write_cdr_variable		11,6
	get_list_value		2,11
	create_goal		10
	set_value		1,20
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,1
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,2
	set_value		3,22
	enqueue_goal		3,wait_flush_3_0
	create_goal		2
	set_value		1,17
	set_value		2,21
	enqueue_goal		2,code_to_procedure_2_0
	create_goal		3
	set_variable		1,1
	set_value		2,15
	set_value		3,19
	enqueue_goal		3,construct_goal_3_0
	create_goal		2
	set_value		1,14
	set_value		2,1
	enqueue_goal_external		mpimos_opcode_table,op,2
	put_value		1,13
	put_value		2,16
	execute		2,code_table_2_0
monitor_10_20:
	suspend		monitor_10_0
	module_entry		mpimos_task_monitor
	predicate		code_table,2
code_table_2_0:
	try_me_else		code_table_2_1
	integer		1
	jump_on_integer		1,19,code_table_2_1
	table_entry		code_table_2_3
	table_entry		code_table_2_4
	table_entry		code_table_2_1
	table_entry		code_table_2_5
	table_entry		code_table_2_1
	table_entry		code_table_2_6
	table_entry		code_table_2_1
	table_entry		code_table_2_1
	table_entry		code_table_2_7
	table_entry		code_table_2_8
	table_entry		code_table_2_9
	table_entry		code_table_2_1
	table_entry		code_table_2_1
	table_entry		code_table_2_1
	table_entry		code_table_2_1
	table_entry		code_table_2_1
	table_entry		code_table_2_10
	table_entry		code_table_2_11
	table_entry		code_table_2_12
code_table_2_3:
	put_structured_constant		1,'$SCNST_21'
	get_value		2,1
	proceed
code_table_2_4:
	put_structured_constant		1,'$SCNST_22'
	get_value		2,1
	proceed
code_table_2_5:
	put_structured_constant		1,'$SCNST_23'
	get_value		2,1
	proceed
code_table_2_6:
	put_structured_constant		1,'$SCNST_24'
	get_value		2,1
	proceed
code_table_2_7:
	put_structured_constant		1,'$SCNST_25'
	get_value		2,1
	proceed
code_table_2_8:
	put_structured_constant		1,'$SCNST_26'
	get_value		2,1
	proceed
code_table_2_9:
	put_structured_constant		1,'$SCNST_27'
	get_value		2,1
	proceed
code_table_2_10:
	put_structured_constant		1,'$SCNST_28'
	get_value		2,1
	proceed
code_table_2_11:
	put_structured_constant		1,'$SCNST_29'
	get_value		2,1
	proceed
code_table_2_12:
	put_structured_constant		1,'$SCNST_30'
	get_value		2,1
	proceed
code_table_2_1:
	otherwise		code_table_2_0
	collect_value		1
	put_structured_constant		1,'$SCNST_31'
	get_value		2,1
	proceed
code_table_2_15:
	suspend		code_table_2_0
	module_entry		mpimos_task_monitor
	predicate		deadlock_table,2
deadlock_table_2_0:
	try_me_else		deadlock_table_2_1
	integer		1
	jump_on_integer		1,32,deadlock_table_2_1
	table_entry		deadlock_table_2_3
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_4
	table_entry		deadlock_table_2_5
	table_entry		deadlock_table_2_6
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_7
	table_entry		deadlock_table_2_8
	table_entry		deadlock_table_2_9
	table_entry		deadlock_table_2_10
	table_entry		deadlock_table_2_11
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_1
	table_entry		deadlock_table_2_12
	table_entry		deadlock_table_2_13
deadlock_table_2_3:
	put_structured_constant		1,'$SCNST_32'
	get_value		2,1
	proceed
deadlock_table_2_4:
	put_structured_constant		1,'$SCNST_33'
	get_value		2,1
	proceed
deadlock_table_2_5:
	put_structured_constant		1,'$SCNST_34'
	get_value		2,1
	proceed
deadlock_table_2_6:
	put_structured_constant		1,'$SCNST_35'
	get_value		2,1
	proceed
deadlock_table_2_7:
	put_structured_constant		1,'$SCNST_36'
	get_value		2,1
	proceed
deadlock_table_2_8:
	put_structured_constant		1,'$SCNST_37'
	get_value		2,1
	proceed
deadlock_table_2_9:
	put_structured_constant		1,'$SCNST_38'
	get_value		2,1
	proceed
deadlock_table_2_10:
	put_structured_constant		1,'$SCNST_39'
	get_value		2,1
	proceed
deadlock_table_2_11:
	put_structured_constant		1,'$SCNST_40'
	get_value		2,1
	proceed
deadlock_table_2_12:
	put_structured_constant		1,'$SCNST_41'
	get_value		2,1
	proceed
deadlock_table_2_13:
	put_structured_constant		1,'$SCNST_42'
	get_value		2,1
	proceed
deadlock_table_2_1:
	otherwise		deadlock_table_2_0
	collect_value		1
	put_structured_constant		1,'$SCNST_43'
	get_value		2,1
	proceed
deadlock_table_2_16:
	suspend		deadlock_table_2_0
	module_entry		mpimos_task_monitor
	predicate		occured_table,2
occured_table_2_0:
	try_me_else		occured_table_2_1
	integer		1
	jump_on_integer		1,32,occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_3
	table_entry		occured_table_2_4
	table_entry		occured_table_2_5
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_6
	table_entry		occured_table_2_7
	table_entry		occured_table_2_8
	table_entry		occured_table_2_9
	table_entry		occured_table_2_10
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_1
	table_entry		occured_table_2_11
	table_entry		occured_table_2_12
occured_table_2_3:
	put_structured_constant		1,'$SCNST_44'
	get_value		2,1
	proceed
occured_table_2_4:
	put_structured_constant		1,'$SCNST_45'
	get_value		2,1
	proceed
occured_table_2_5:
	put_structured_constant		1,'$SCNST_46'
	get_value		2,1
	proceed
occured_table_2_6:
	put_structured_constant		1,'$SCNST_47'
	get_value		2,1
	proceed
occured_table_2_7:
	put_structured_constant		1,'$SCNST_48'
	get_value		2,1
	proceed
occured_table_2_8:
	put_structured_constant		1,'$SCNST_49'
	get_value		2,1
	proceed
occured_table_2_9:
	put_structured_constant		1,'$SCNST_50'
	get_value		2,1
	proceed
occured_table_2_10:
	put_structured_constant		1,'$SCNST_51'
	get_value		2,1
	proceed
occured_table_2_11:
	put_structured_constant		1,'$SCNST_52'
	get_value		2,1
	proceed
occured_table_2_12:
	put_structured_constant		1,'$SCNST_53'
	get_value		2,1
	proceed
occured_table_2_1:
	suspend		occured_table_2_0
	module_entry		mpimos_task_monitor
	predicate		construct_goal,3
construct_goal_3_0:
	try_me_else		construct_goal_3_1
	atom		1
	vector		2
	try_me_else		construct_goal_3_4
	g_vector		2,4
	wait_integer		4,0
	collect_value		2
	get_value		3,1
	proceed
construct_goal_3_4:
	try_me_else		construct_goal_3_1
	g_vector		2,4
	put_integer		5,0
	g_less_than		5,4
	put_marked_value		5,4
	b_increment		5,5
	b_new_vector		5,5
	put_integer		6,0
	b_set_vector_element		5,6,1,1,5
	create_goal		5
	set_integer		1,0
	set_value		2,4
	set_variable		3,4
	set_value		4,5
	set_value		5,3
	enqueue_goal		5,copy_args_5_0
	put_value		1,2
	put_value		2,4
	execute_external		mpimos_utility,freeze,2
construct_goal_3_1:
	suspend		construct_goal_3_0
	module_entry		mpimos_task_monitor
	predicate		copy_args,5
copy_args_5_0:
	try_me_else		copy_args_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	b_increment		6,6
	put_nil		7
	b_set_vector_element		3,1,1,7,3
	put_marked_value		7,6
	b_set_vector_element		4,7,1,1,4
	put_value		1,6
	execute		5,copy_args_5_0
copy_args_5_1:
	try_me_else		copy_args_5_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,4
	proceed
copy_args_5_3:
	suspend		copy_args_5_0
	module_entry		mpimos_task_monitor
	predicate		code_to_procedure,2
code_to_procedure_2_0:
	try_me_else		code_to_procedure_2_1
	vector		1
	jump_on_arity		1,4,code_to_procedure_2_1
	table_entry		code_to_procedure_2_1
	table_entry		code_to_procedure_2_1
	table_entry		code_to_procedure_2_3
	table_entry		code_to_procedure_2_4
code_to_procedure_2_3:
	read_element		1,0,3
	wait_atom		3,merge
	read_element		1,1,7
	wait_vector		7,3
	read_elements_inc		7,0,3,3
	b_atom_name		3,3
	put_structured_constant		6,'$SCNST_54'
	b_append_string		6,3,3
	b_intern_atom		3,3
	put_reused_func		6,7,/
	write_elements_inc		6,1,4,2
	put_func		4,3,:
	write_element_value		4,1,3
	write_element_value		4,2,6
	put_reused_func		1,1,'merge/2'
	write_element_value		1,1,4
	get_vector_value		2,1
	proceed
code_to_procedure_2_4:
	read_elements_inc		1,0,3,3
	put_reused_func		1,1,/
	write_elements_inc		1,1,4,2
	put_func		4,3,:
	write_element_value		4,1,3
	write_element_value		4,2,1
	get_vector_value		2,4
	proceed
code_to_procedure_2_1:
	suspend		code_to_procedure_2_0
	module_entry		mpimos_task_monitor
	predicate		code_to_goal,3
code_to_goal_3_0:
	try_me_else		code_to_goal_3_1
	wait_vector		1,3
	read_elements_inc		1,0,4,3
	collect_value		6
	put_reused_func		1,1,:
	write_element_value		1,1,4
	write_element_variable		1,2,4
	get_vector_value		3,1
	put_value		1,5
	put_value		3,4
	execute		3,construct_goal_3_0
code_to_goal_3_1:
	suspend		code_to_goal_3_0
	module_entry		mpimos_task_monitor
	predicate		put_procedures_list,2
put_procedures_list_2_0:
	try_me_else		put_procedures_list_2_1
	wait_list_var_var		1,3,4
	put_func		5,2,putt
	write_element_variable		5,1,6
	get_reused_list_val_var		2,7,1,5,1
	create_goal		3
	set_value		1,4
	set_value		2,1
	set_integer		3,4
	enqueue_goal		3,put_procedures_list_3_0
	put_value		1,3
	put_value		2,6
	execute		2,code_to_procedure_2_0
put_procedures_list_2_1:
	suspend		put_procedures_list_2_0
	module_entry		mpimos_task_monitor
	predicate		put_procedures_list,3
put_procedures_list_3_0:
	try_me_else		put_procedures_list_3_1
	jump_on_non_list_var_var		1,put_procedures_list_3_3,4,5
	integer		3
	put_integer		6,0
	g_less_than		6,3
	put_func		6,2,putt
	write_element_variable		6,1,7
	put_reused_list_val_var		1,1,6,8
	put_structured_constant		6,'$SCNST_55'
	put_list_val_val		9,6,1
	get_list_value		2,9
	b_decrement		3,1
	create_goal		3
	set_value		1,5
	set_value		2,8
	set_value		3,1
	enqueue_goal		3,put_procedures_list_3_0
	put_value		1,4
	put_value		2,7
	execute		2,code_to_procedure_2_0
put_procedures_list_3_3:
	check_nil		1,put_procedures_list_3_1
	collect_value		3
	get_nil		2
	proceed
put_procedures_list_3_1:
	try_me_else		put_procedures_list_3_4
	wait_integer		3,0
	put_nil		4
	g_diff		1,4
	collect_value		1
	collect_value		4
	put_structured_constant		1,'$SCNST_56'
	get_value		2,1
	proceed
put_procedures_list_3_4:
	suspend		put_procedures_list_3_0
	module_entry		mpimos_task_monitor
	predicate		wait_auto_load_env,15
wait_auto_load_env_15_0:
	try_me_else		wait_auto_load_env_15_1
	atom		11
	branch_on_atom		11,2,wait_auto_load_env_15_1
	bucket_entry_a		no,wait_auto_load_env_15_3
	bucket_entry_a		yes,wait_auto_load_env_15_4
wait_auto_load_env_15_3:
	collect_value		15
	put_func		11,2,flush
	write_element_variable		11,1,19
	put_list		15
	write_car_value		15,11
	write_cdr_nil		15
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,15
	put_func		15,2,putt
	write_element_variable		15,1,18
	put_list_val_val		16,15,11
	put_structured_constant		11,'$SCNST_57'
	put_list_val_val		15,11,16
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,15
	put_func		15,2,putb
	write_element_variable		15,1,17
	put_list_val_val		16,15,11
	put_structured_constant		11,'$SCNST_58'
	put_list_val_val		15,11,16
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,15
	put_func		15,2,do
	write_element_value		15,1,11
	get_list_val_var		6,16,15,11
	get_nil		14
	put_list		14
	write_car_atom		14,abort
	write_cdr_variable		14,6
	get_list_value		2,14
	create_goal		10
	set_value		1,1
	set_value		2,6
	set_value		3,3
	set_variable		4,1
	set_value		5,5
	set_value		6,11
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_value		1,4
	set_value		2,1
	set_value		3,19
	enqueue_goal		3,wait_flush_3_0
	create_goal		3
	set_values_inc		1,12,2
	set_value		3,18
	enqueue_goal		3,code_to_goal_3_0
	put_integer		1,17
	put_value		2,17
	execute		2,code_table_2_0
wait_auto_load_env_15_4:
	wait_vector		12,3
	read_element		12,0,11
	read_elements_inc		12,1,16,2
	put_func		18,2,get_all_modules
	write_element_variable		18,1,19
	put_reused_func		12,12,:
	write_element_atom		12,1,code_manager
	write_element_value		12,2,18
	get_list_val_var		5,18,12,12
	create_goal		15
	set_values_inc		1,1,4
	set_value		5,12
	set_values_inc		6,6,5
	set_variable		11,3
	put_vector		1,3
	write_element_marked_value		1,0,11
	write_elements_inc		1,1,16,2
	set_value		12,1
	set_values_inc		13,13,3
	enqueue_goal		15,wait_loaded_status_15_0
	put_value		1,19
	put_value		2,11
	execute		3,member_3_0
wait_auto_load_env_15_1:
	otherwise		wait_auto_load_env_15_0
	collect_value		15
	collect_value		13
	collect_value		12
	put_func		12,2,flush
	write_element_variable		12,1,15
	put_list		13
	write_car_value		13,12
	write_cdr_nil		13
	put_list		12
	write_car_atom		12,nl
	write_cdr_value		12,13
	put_func		13,2,putt
	write_element_value		13,1,11
	put_list_val_val		11,13,12
	put_structured_constant		12,'$SCNST_59'
	put_list_val_val		13,12,11
	put_structured_constant		11,'$SCNST_60'
	put_list_val_val		12,11,13
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,12
	put_func		12,2,do
	write_element_value		12,1,11
	get_list_val_var		6,13,12,11
	get_nil		14
	put_list		12
	write_car_atom		12,abort
	write_cdr_variable		12,6
	get_list_value		2,12
	create_goal		10
	set_value		1,1
	set_value		2,6
	set_value		3,3
	set_variable		4,2
	set_value		5,5
	set_value		6,11
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	put_value		1,4
	put_value		3,15
	execute		3,wait_flush_3_0
wait_auto_load_env_15_7:
	suspend		wait_auto_load_env_15_0
	module_entry		mpimos_task_monitor
	predicate		wait_loaded_status,15
wait_loaded_status_15_0:
	try_me_else		wait_loaded_status_15_1
	atom		11
	branch_on_atom		11,2,wait_loaded_status_15_1
	bucket_entry_a		no,wait_loaded_status_15_3
	bucket_entry_a		yes,wait_loaded_status_15_4
wait_loaded_status_15_3:
	wait_vector		12,3
	read_element		12,0,11
	read_elements_inc		12,1,16,2
	put_func		18,2,flush
	write_element_variable		18,1,21
	put_list		19
	write_car_value		19,18
	write_cdr_nil		19
	put_structured_constant		18,'$SCNST_61'
	put_list_val_val		20,18,19
	put_func		18,2,putt
	write_element_marked_value		18,1,11
	put_list_val_val		19,18,20
	put_func		18,2,do
	write_element_value		18,1,19
	get_list_val_var		6,19,18,18
	put_reused_vector		6,12
	write_element_value		6,0,11
	write_elements_inc		6,1,16,2
	get_vector_value		14,6
	get_value		15,13
	put_func		6,3,getenv
	write_element_atom		6,1,loaddir
	write_element_variable		6,2,12
	get_list_val_var		7,13,6,6
	create_goal		12
	set_value		1,1
	set_variable		2,7
	set_values_inc		3,3,3
	set_value		6,18
	set_value		7,6
	set_values_inc		8,8,5
	enqueue_goal		12,auto_load_12_0
	put_value		1,2
	put_value		2,7
	put_value		3,21
	execute		3,wait_flush_3_0
wait_loaded_status_15_4:
	get_value		14,12
	get_value		15,13
	put_list		12
	write_car_atom		12,start
	write_cdr_variable		12,11
	get_list_value		2,12
	put_value		2,11
	execute		10,monitor_10_0
wait_loaded_status_15_1:
	suspend		wait_loaded_status_15_0
	module_entry		mpimos_task_monitor
	predicate		auto_load,12
auto_load_12_0:
	try_me_else		auto_load_12_1
	jump_on_non_list_var_var		12,auto_load_12_3,13,14
	string		13
	g_string		13,15,16
	put_func		15,4,auto_load_module
	write_element_variable		15,1,17
	write_element_marked_value		15,2,11
	write_element_variable		15,3,18
	put_func		16,3,:
	write_element_atom		16,1,code_manager
	write_element_value		16,2,15
	get_reused_list_val_var		5,15,12,16,12
	create_goal		13
	set_values_inc		1,1,4
	set_value		5,12
	set_value		6,6
	set_variable		7,5
	set_values_inc		8,8,4
	set_value		12,14
	set_value		13,18
	enqueue_goal		13,wait_auto_load_13_0
	put_value		1,13
	put_value		2,17
	put_void		3
	put_value		4,7
	execute_external		mpimos_cmd_utl,os_check_loaddir,5
auto_load_12_3:
	check_nil		12,auto_load_12_1
	collect_value		11
	collect_value		8
	put_func		8,2,flush
	write_element_marked_variable		8,1,13
	put_list		11
	write_car_value		11,8
	write_cdr_nil		11
	put_structured_constant		8,'$SCNST_62'
	put_list_val_val		12,8,11
	put_func		8,2,do
	write_element_value		8,1,12
	get_list_val_var		6,11,8,8
	create_goal		10
	set_value		1,1
	set_variable		2,1
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	set_values_dec		6,8,2
	set_atom		8,abort
	set_values_inc		9,9,2
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_values_dec		1,4,2
	set_value		3,13
	enqueue_goal		3,wait_flush_3_0
	put_list		3
	write_car_atom		3,abort
	write_cdr_value		3,1
	put_values_inc		1,2,2
	put_value		3,13
	execute		3,wait_flush_3_0
auto_load_12_1:
	otherwise		auto_load_12_0
	collect_value		11
	collect_value		8
	put_func		8,2,flush
	write_element_marked_variable		8,1,13
	put_list		11
	write_car_value		11,8
	write_cdr_nil		11
	put_list		8
	write_car_atom		8,nl
	write_cdr_value		8,11
	put_func		11,2,putt
	write_element_value		11,1,12
	put_list_val_val		12,11,8
	put_structured_constant		8,'$SCNST_63'
	put_list_val_val		11,8,12
	put_structured_constant		8,'$SCNST_64'
	put_list_val_val		12,8,11
	put_list		8
	write_car_atom		8,nl
	write_cdr_value		8,12
	put_func		11,2,do
	write_element_value		11,1,8
	get_list_val_var		6,12,11,8
	create_goal		10
	set_value		1,1
	set_variable		2,1
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	set_values_dec		6,8,2
	set_atom		8,abort
	set_values_inc		9,9,2
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_values_dec		1,4,2
	set_value		3,13
	enqueue_goal		3,wait_flush_3_0
	put_list		3
	write_car_atom		3,abort
	write_cdr_value		3,1
	put_values_inc		1,2,2
	put_value		3,13
	execute		3,wait_flush_3_0
auto_load_12_8:
	suspend		auto_load_12_0
	module_entry		mpimos_task_monitor
	predicate		wait_auto_load,13
wait_auto_load_13_0:
	try_me_else		wait_auto_load_13_1
	atom		13
	branch_on_atom		13,3,wait_auto_load_13_1
	bucket_entry_a		memory_limit,wait_auto_load_13_3
	bucket_entry_a		success,wait_auto_load_13_4
	bucket_entry_a		this_module_not_saved,wait_auto_load_13_5
wait_auto_load_13_3:
	collect_value		12
	collect_value		11
	collect_value		8
	put_func		8,2,flush
	write_element_marked_variable		8,1,13
	put_list		11
	write_car_value		11,8
	write_cdr_nil		11
	put_structured_constant		8,'$SCNST_65'
	put_list_val_val		12,8,11
	put_func		8,2,do
	write_element_value		8,1,12
	get_list_val_var		6,11,8,8
	create_goal		10
	set_value		1,1
	set_variable		2,1
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	set_values_dec		6,8,2
	set_atom		8,abort
	set_values_inc		9,9,2
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_values_dec		1,4,2
	set_value		3,13
	enqueue_goal		3,wait_flush_3_0
	put_list		3
	write_car_atom		3,abort
	write_cdr_value		3,1
	put_values_inc		1,2,2
	put_value		3,13
	execute		3,wait_flush_3_0
wait_auto_load_13_4:
	collect_value		12
	collect_value		11
	collect_value		8
	put_func		8,2,flush
	write_element_marked_variable		8,1,13
	put_list		11
	write_car_value		11,8
	write_cdr_nil		11
	put_structured_constant		8,'$SCNST_66'
	put_list_val_val		12,8,11
	put_func		8,2,do
	write_element_value		8,1,12
	get_list_val_var		6,11,8,8
	create_goal		10
	set_value		1,1
	set_variable		2,1
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	set_values_dec		6,8,2
	set_atom		8,active
	set_values_inc		9,9,2
	enqueue_goal		10,monitor_10_0
	create_goal		3
	set_values_dec		1,4,2
	set_value		3,13
	enqueue_goal		3,wait_flush_3_0
	put_list		3
	write_car_atom		3,start
	write_cdr_value		3,1
	put_values_inc		1,2,2
	put_value		3,13
	execute		3,wait_flush_3_0
wait_auto_load_13_5:
	execute		12,auto_load_12_0
wait_auto_load_13_1:
	suspend		wait_auto_load_13_0
	module_entry		mpimos_task_monitor
	predicate		member,3
member_3_0:
	try_me_else		member_3_1
	jump_on_non_list_var_var		1,member_3_3,4,5
	try_me_else		member_3_4
	g_diff		2,4
	collect_list		1
	collect_value		4
	put_value		1,5
	execute		3,member_3_0
member_3_4:
	try_me_else		member_3_1
	wait_value		2,4
	collect_list		1
	collect_value		2
	collect_value		5
	collect_value		4
	get_atom		3,yes
	proceed
member_3_3:
	check_nil		1,member_3_1
	collect_value		2
	get_atom		3,no
	proceed
member_3_1:
	suspend		member_3_0
	module_entry		mpimos_task_monitor
	predicate		request,14
request_14_0:
	try_me_else		request_14_1
	jump_on_non_atom		11,request_14_3
	hash_on_atom		11,10,request_14_1
	bucket_entry_a		after_care,request_14_4
	bucket_entry_a		code_manager,request_14_5
	bucket_entry_a		device_file,request_14_6
	bucket_entry_a		device_timer,request_14_7
	bucket_entry_a		device_window,request_14_8
	bucket_entry_a		directory,request_14_9
	bucket_entry_a		error,request_14_10
	bucket_entry_a		file,request_14_11
	bucket_entry_a		warning,request_14_12
	bucket_entry_a		window,request_14_13
request_14_4:
	collect_value		14
	get_nil		13
	put_func		11,2,after_care
	write_element_value		11,1,12
	get_list_val_var		4,12,11,11
	put_value		4,11
	execute		10,monitor_10_0
request_14_5:
	put_structured_constant		11,'$SCNST_67'
	get_value		13,11
	put_vector		13,3
	write_element_value		13,0,12
	write_element_marked_value		13,1,9
	write_element_variable		13,2,11
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_values_inc		6,6,5
	enqueue_goal		10,monitor_10_0
	put_values_inc		1,11,2
	put_value		3,9
	execute		3,valve_3_0
request_14_6:
	put_func		11,3,getenv
	write_element_atom		11,1,world
	write_element_variable		11,2,15
	get_list_val_var		7,16,11,11
	put_structured_constant		7,'$SCNST_68'
	get_value		13,7
	put_vector		13,4
	write_element_value		13,0,12
	write_element_value		13,1,15
	write_element_marked_value		13,2,9
	write_element_variable		13,3,7
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_values_inc		8,8,3
	enqueue_goal		10,monitor_10_0
	put_value		1,7
	put_value		2,12
	put_value		3,9
	execute		3,valve_3_0
request_14_7:
	put_structured_constant		11,'$SCNST_69'
	get_value		13,11
	put_vector		13,3
	write_element_value		13,0,12
	write_element_marked_value		13,1,9
	write_element_variable		13,2,11
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_values_inc		6,6,5
	enqueue_goal		10,monitor_10_0
	put_values_inc		1,11,2
	put_value		3,9
	execute		3,valve_3_0
request_14_8:
	put_structured_constant		11,'$SCNST_70'
	get_value		13,11
	put_vector		13,3
	write_element_value		13,0,12
	write_element_marked_value		13,1,9
	write_element_variable		13,2,11
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_values_inc		6,6,5
	enqueue_goal		10,monitor_10_0
	put_values_inc		1,11,2
	put_value		3,9
	execute		3,valve_3_0
request_14_9:
	put_func		11,3,getenv
	write_element_atom		11,1,world
	write_element_variable		11,2,15
	get_list_val_var		7,16,11,11
	put_structured_constant		7,'$SCNST_71'
	get_value		13,7
	put_vector		13,4
	write_element_value		13,0,12
	write_element_value		13,1,15
	write_element_marked_value		13,2,9
	write_element_variable		13,3,7
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_values_inc		8,8,3
	enqueue_goal		10,monitor_10_0
	put_value		1,7
	put_value		2,12
	put_value		3,9
	execute		3,valve_3_0
request_14_10:
	put_structured_constant		11,'$SCNST_72'
	get_value		13,11
	put_vector		13,3
	write_element_value		13,0,12
	write_element_variable		13,1,11
	write_element_marked_value		13,2,9
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		6,14
	b_merge		14,6
	put_vector		15,2
	write_element_value		15,0,3
	write_element_variable		15,1,3
	get_vector_value		14,15
	create_goal		10
	set_values_inc		1,1,2
	set_value		3,6
	set_values_inc		4,4,2
	set_value		6,13
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	put_values_inc		1,11,2
	put_value		4,9
	execute		4,valve_4_0
request_14_11:
	put_func		11,3,getenv
	write_element_atom		11,1,world
	write_element_variable		11,2,15
	get_list_val_var		7,16,11,11
	put_structured_constant		7,'$SCNST_73'
	get_value		13,7
	put_vector		13,4
	write_element_value		13,0,12
	write_element_value		13,1,15
	write_element_marked_value		13,2,9
	write_element_variable		13,3,7
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		5,14
	create_goal		10
	set_values_inc		1,1,4
	set_value		5,13
	set_value		6,6
	set_value		7,11
	set_values_inc		8,8,3
	enqueue_goal		10,monitor_10_0
	put_value		1,7
	put_value		2,12
	put_value		3,9
	execute		3,valve_3_0
request_14_12:
	put_structured_constant		11,'$SCNST_74'
	get_value		13,11
	put_vector		13,2
	write_element_value		13,0,12
	write_element_variable		13,1,11
	get_vector_value		14,13
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		6,14
	create_goal		10
	set_values_inc		1,1,5
	set_value		6,13
	set_values_inc		7,7,2
	set_marked_value		9,9
	set_value		10,10
	enqueue_goal		10,monitor_10_0
	put_values_inc		1,11,2
	put_value		3,9
	execute		3,valve_3_0
request_14_13:
	put_structured_constant		11,'$SCNST_75'
	get_value		13,11
	put_vector		17,7
	write_element_value		17,0,12
	write_element_variable		17,1,16
	write_element_marked_value		17,2,9
	write_element_variable		17,3,15
	write_element_variable		17,4,13
	write_element_variable		17,5,12
	write_element_variable		17,6,11
	get_vector_value		14,17
	put_vector		18,2
	write_element_variable		18,0,14
	write_element_variable		18,1,17
	get_vector_value		5,18
	b_merge		18,5
	put_vector		19,2
	write_element_value		19,0,3
	write_element_variable		19,1,3
	get_vector_value		18,19
	create_goal		10
	set_values_inc		1,1,2
	set_values_dec		3,5,2
	set_value		5,17
	set_values_inc		6,6,5
	enqueue_goal		10,monitor_10_0
	put_integer		1,4088
	b_rate		1,1
	create_goal		4
	set_value		1,15
	set_value		2,3
	set_value		3,16
	set_value		4,9
	enqueue_goal_with_priority		4,interrupt_handler_4_0,1
	create_goal		3
	set_values_dec		1,13,2
	set_value		3,9
	enqueue_goal		3,valve_3_0
	put_value		1,11
	put_value		2,14
	put_value		3,9
	execute		3,valve_3_0
request_14_3:
	is_vector		11,request_14_1
	jump_on_arity		11,4,request_14_1
	table_entry		request_14_1
	table_entry		request_14_1
	table_entry		request_14_14
	table_entry		request_14_15
request_14_14:
	read_element		11,0,15
	wait_atom		15,shell
	read_element		11,1,15
	atom		15
	put_reused_func		11,11,shell
	write_element_value		11,1,15
	put_func		15,5,raised
	write_elements_inc		15,1,11,4
	get_list_val_var		4,12,15,11
	put_value		4,11
	execute		10,monitor_10_0
request_14_15:
	read_element		11,0,15
	wait_atom		15,'$PIMOS$'
	read_elements_inc		11,1,15,2
	put_structured_constant		17,'$SCNST_76'
	get_value		13,17
	put_reused_vector		11,11
	write_elements_inc		11,0,15,2
	write_element_value		11,2,12
	get_vector_value		14,11
	execute		10,monitor_10_0
request_14_1:
	otherwise		request_14_0
	collect_value		14
	collect_value		12
	get_nil		13
	put_func		12,2,flush
	write_element_variable		12,1,14
	put_list		13
	write_car_value		13,12
	write_cdr_nil		13
	put_list		12
	write_car_atom		12,nl
	write_cdr_value		12,13
	put_func		13,2,putt
	write_element_value		13,1,11
	put_list_val_val		11,13,12
	put_structured_constant		12,'$SCNST_77'
	put_list_val_val		13,12,11
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,13
	put_func		12,2,do
	write_element_value		12,1,11
	get_list_val_var		6,13,12,11
	create_goal		10
	set_values_inc		1,1,3
	set_variable		4,2
	set_value		5,5
	set_value		6,11
	set_values_inc		7,7,4
	enqueue_goal		10,monitor_10_0
	put_value		1,4
	put_value		3,14
	execute		3,wait_flush_3_0
request_14_19:
	suspend		request_14_0
	module_entry		mpimos_task_monitor
	predicate		valve,3
valve_3_0:
	try_me_else		valve_3_1
	jump_on_non_list_var_var		1,valve_3_3,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,valve_3_0
valve_3_3:
	check_nil		1,valve_3_1
	collect_value		3
	get_nil		2
	proceed
valve_3_1:
	try_me_else		valve_3_4
	wait_atom		3,die
	collect_value		1
	get_nil		2
	proceed
valve_3_4:
	suspend		valve_3_0
	module_entry		mpimos_task_monitor
	predicate		valve,4
valve_4_0:
	try_me_else		valve_4_1
	jump_on_non_list_var_var		1,valve_4_3,5,6
	get_reused_list_val_var		2,1,1,5,5
	put_values_dec		1,6,2
	execute		4,valve_4_0
valve_4_3:
	check_nil		1,valve_4_1
	collect_value		4
	get_nil		2
	put_structured_constant		1,'$SCNST_78'
	get_value		3,1
	proceed
valve_4_1:
	try_me_else		valve_4_4
	wait_atom		4,die
	collect_value		1
	get_nil		2
	get_nil		3
	proceed
valve_4_4:
	suspend		valve_4_0
	module_entry		mpimos_task_monitor
	predicate		interrupt_handler,4
interrupt_handler_4_0:
	try_me_else		interrupt_handler_4_1
	jump_on_non_list		1,interrupt_handler_4_3
	read_car		1,5
	integer		5
	jump_on_integer		5,3,interrupt_handler_4_1
	table_entry		interrupt_handler_4_1
	table_entry		interrupt_handler_4_5
	table_entry		interrupt_handler_4_6
interrupt_handler_4_5:
	read_cdr		1,6
	collect_list		1
	collect_value		4
	collect_value		6
	put_structured_constant		1,'$SCNST_79'
	get_value		2,1
	get_nil		3
	proceed
interrupt_handler_4_6:
	read_cdr		1,6
	put_func		5,2,statistics
	write_element_variable		5,1,7
	get_reused_list_val_var		2,1,1,5,8
	put_integer		1,0
	b_vector_element		7,1,1,2
	put_integer		2,1
	put_integer		5,8
	b_new_string		2,2,5
	put_integer		5,0
	put_integer		7,10
	b_set_string_element		2,5,7,2
	put_func		5,3,putb
	write_element_value		5,1,2
	write_element_void		5,2
	put_list		2
	write_car_value		2,5
	write_cdr_nil		2
	put_structured_constant		5,'$SCNST_80'
	put_func		7,3,putb
	write_element_value		7,1,5
	write_element_void		7,2
	put_list_val_val		5,7,2
	put_func		2,3,putb
	write_element_variable		2,1,9
	write_element_void		2,2
	put_list_val_val		7,2,5
	put_structured_constant		2,'$SCNST_81'
	put_func		5,3,putb
	write_element_value		5,1,2
	write_element_void		5,2
	put_list_val_val		2,5,7
	put_func		5,2,do
	write_element_value		5,1,2
	get_list_val_var		3,7,5,2
	create_goal		4
	set_value		1,6
	set_value		2,8
	set_value		3,2
	set_value		4,4
	enqueue_goal		4,interrupt_handler_4_0
	put_value		2,9
	execute_external		mpimos_utility,integer_to_string,2
interrupt_handler_4_3:
	check_nil		1,interrupt_handler_4_1
	collect_value		4
	get_nil		2
	get_nil		3
	proceed
interrupt_handler_4_1:
	try_me_else		interrupt_handler_4_7
	wait_atom		4,die
	collect_value		1
	get_nil		2
	get_nil		3
	proceed
interrupt_handler_4_7:
	suspend		interrupt_handler_4_0
	module_entry		mpimos_task_monitor
	predicate		error_monitor,2
error_monitor_2_0:
	create_goal		3
	set_variable		1,4
	set_value		2,2
	set_variable		3,2
	enqueue_goal		3,wait_done_3_0
	put_atom		3,done
	execute		4,error_monitor_4_0
error_monitor_2_1:
	suspend		error_monitor_2_0
	module_entry		mpimos_task_monitor
	predicate		error_monitor,3
error_monitor_3_0:
	create_goal		1
	set_value		1,3
	enqueue_goal		1,dummy_1_0
	create_goal		3
	set_variable		1,4
	set_value		2,2
	set_variable		3,2
	enqueue_goal		3,wait_done_3_0
	put_atom		3,done
	execute		4,error_monitor_4_0
error_monitor_3_1:
	suspend		error_monitor_3_0
	module_entry		mpimos_task_monitor
	predicate		dummy,1
dummy_1_0:
	try_me_else		dummy_1_1
	wait		1
	proceed
dummy_1_1:
	suspend		dummy_1_0
	module_entry		mpimos_task_monitor
	predicate		error_monitor,4
error_monitor_4_0:
	try_me_else		error_monitor_4_1
	wait		1
	switch_on_type		1,error_monitor_4_2,error_monitor_4_3,error_monitor_4_4,error_monitor_4_5,error_monitor_4_6,error_monitor_4_7
error_monitor_4_4:
	read_car		1,5
	read_cdr		1,6
	put_reused_list		8,1
	write_car_variable		8,7
	write_cdr_variable		8,1
	get_list_value		2,8
	create_goal		4
	set_value		1,6
	set_value		2,1
	set_variable		3,6
	set_value		4,4
	enqueue_goal		4,error_monitor_4_0
	put_value		1,5
	put_value		2,7
	put_value		4,6
	execute		4,error_monitor_4_0
error_monitor_4_2:
	get_value		2,1
	get_value		3,4
	proceed
error_monitor_4_3:
	get_value		2,1
	get_value		3,4
	proceed
error_monitor_4_5:
	test_arity		1,2,error_monitor_4_8
	try_me_else		error_monitor_4_8
	read_element		1,0,5
	wait_atom		5,flush
	read_element		1,1,5
	put_reused_func		6,1,flush
	write_element_variable		6,1,1
	get_vector_value		2,6
	get_value		3,4
	put_value		2,5
	execute		2,wait_flush_status_2_0
error_monitor_4_8:
	put_value		8,1
	g_vector		8,5
	put_value		9,2
	put_values_inc		6,3,2
	put_marked_value		1,5
	b_new_vector		4,1
	put_integer		1,0
	put_value		2,5
	put_value		3,8
	put_value		5,9
	execute		7,unify_vector_7_0
error_monitor_4_6:
	get_value		2,1
	get_value		3,4
	proceed
error_monitor_4_7:
	is_float		1,error_monitor_4_1
	get_value		2,1
	get_value		3,4
	proceed
error_monitor_4_1:
	suspend		error_monitor_4_0
	module_entry		mpimos_task_monitor
	predicate		wait_flush_status,2
wait_flush_status_2_0:
	try_me_else		wait_flush_status_2_1
	wait_atom		1,done
	get_atom		2,done
	proceed
wait_flush_status_2_1:
	suspend		wait_flush_status_2_0
	module_entry		mpimos_task_monitor
	predicate		wait_done,3
wait_done_3_0:
	try_me_else		wait_done_3_1
	wait		1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_func		1,2,do
	write_element_value		1,1,3
	put_list_val_val		3,1,4
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	get_list_value		2,1
	proceed
wait_done_3_1:
	suspend		wait_done_3_0
	module_entry		mpimos_task_monitor
	predicate		unify_vector,7
unify_vector_7_0:
	try_me_else		unify_vector_7_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		8,1
	b_vector_element		3,8,3,8
	put_variable		9,10
	b_set_vector_element		4,1,4,9,9
	b_increment		1,1
	create_goal		7
	set_values_inc		1,1,2
	set_values_inc		3,8,2
	set_value		5,5
	set_variable		6,4
	set_value		7,7
	enqueue_goal		7,unify_vector_7_0
	put_value		1,3
	put_value		2,10
	put_value		3,6
	execute		4,error_monitor_4_0
unify_vector_7_1:
	try_me_else		unify_vector_7_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,4
	get_value		6,7
	proceed
unify_vector_7_3:
	suspend		unify_vector_7_0
	module_entry		mpimos_task_monitor
	predicate		wait_flush,3
wait_flush_3_0:
	try_me_else		wait_flush_3_1
	wait_atom		3,done
	get_value		1,2
	proceed
wait_flush_3_1:
	suspend		wait_flush_3_0
	module_entry		mpimos_task_monitor
	predicate		wait_flush,11
wait_flush_11_0:
	try_me_else		wait_flush_11_1
	wait_list_var_var		3,12,13
	collect_value		11
	put_reused_list_val_val		3,3,12,13
	execute		10,monitor_10_0
wait_flush_11_1:
	try_me_else		wait_flush_11_5
	wait		11
	execute		10,monitor_10_0
wait_flush_11_5:
	suspend		wait_flush_11_0
	module_entry		mpimos_task_monitor
	predicate		wait_request,3
wait_request_3_0:
	try_me_else		wait_request_3_1
	wait		1
	get_value		1,2
	get_atom		3,done
	proceed
wait_request_3_1:
	suspend		wait_request_3_0
	module_entry		mpimos_task_monitor
	predicate		'$Sho-en:create/8',8
'$Sho-en:create/8_8_0':
	execute_external		'Sho-en',create,8
'$Sho-en:create/8_8_1':
	suspend		'$Sho-en:create/8_8_0'
	begin_const_section		mpimos_task_monitor
'$SCNST_0_1':
	define_desc		3,2
	define_integer		1818324807
	define_integer		540680307
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_2':
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		19,2
	define_integer		544106784
	define_integer		8250
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_3_1':
	define_desc		3,3
	define_integer		1818324807
	define_integer		538976288
	define_integer		540680224
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_57':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		3,3
	define_integer		1701017669
	define_integer		1869182064
	define_integer		540680302
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_58':
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		19,4
	define_integer		1969447759
	define_integer		1684370034
	define_integer		544106784
	define_integer		8250
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_16':
'$SCNST_9':
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		11,1
	define_integer		2112800
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		19,4
	define_integer		1818324807
	define_integer		538976288
	define_integer		538976288
	define_integer		8250
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_7_1'
'$SCNST_17':
'$SCNST_10':
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		19,4
	define_integer		1701017669
	define_integer		1869182064
	define_integer		538976366
	define_integer		8250
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_20':
'$SCNST_11':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_12_1':
	define_desc		11,4
	define_integer		1718185557
	define_integer		543450473
	define_integer		538996329
	define_integer		2112032
'$SCNST_12_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_12_1'
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		11,4
	define_integer		1701604425
	define_integer		543973735
	define_integer		1635017028
	define_integer		2112032
'$SCNST_13_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_13_1'
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		11,4
	define_integer		1735550317
	define_integer		540159845
	define_integer		538996329
	define_integer		2112032
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_1':
	define_desc		11,4
	define_integer		1701017669
	define_integer		1869182064
	define_integer		538976366
	define_integer		2112032
'$SCNST_15_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_18_1':
	define_desc		27,1
	define_integer		41
'$SCNST_18_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_18_1'
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_19_1':
	define_desc		19,2
	define_integer		1916872736
	define_integer		8295
'$SCNST_19_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_19_1'
'$SCNST_19':
	define_vector		'$SCNST_19_0'
'$SCNST_21_0':
	define_desc		27,4
	define_integer		1701604425
	define_integer		543973735
	define_integer		1970302537
	define_integer		116
'$SCNST_21':
	define_string		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		19,4
	define_integer		1735287122
	define_integer		1984897125
	define_integer		1818653285
	define_integer		30575
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_23_0':
	define_desc		3,4
	define_integer		1702129225
	define_integer		544367975
	define_integer		1919252047
	define_integer		2003790950
'$SCNST_23':
	define_string		'$SCNST_23_0'
'$SCNST_24_0':
	define_desc		3,5
	define_integer		1634692166
	define_integer		1735289204
	define_integer		1768902688
	define_integer		1159754862
	define_integer		1919906418
'$SCNST_24':
	define_string		'$SCNST_24_0'
'$SCNST_25_0':
	define_desc		3,5
	define_integer		1701604425
	define_integer		543973735
	define_integer		1735550285
	define_integer		1226863205
	define_integer		1953853550
'$SCNST_25':
	define_string		'$SCNST_25_0'
'$SCNST_26_0':
	define_desc		3,4
	define_integer		1969513810
	define_integer		1869182051
	define_integer		1631985774
	define_integer		1684368489
'$SCNST_26':
	define_string		'$SCNST_26_0'
'$SCNST_27_0':
	define_desc		19,5
	define_integer		1718185557
	define_integer		1952539497
	define_integer		544108393
	define_integer		1818845510
	define_integer		25701
'$SCNST_27':
	define_string		'$SCNST_27_0'
'$SCNST_28_0':
	define_desc		19,5
	define_integer		1868787273
	define_integer		1667592818
	define_integer		1917853812
	define_integer		1769107305
	define_integer		31092
'$SCNST_28':
	define_string		'$SCNST_28_0'
'$SCNST_29_0':
	define_desc		3,4
	define_integer		1969516365
	define_integer		1310745964
	define_integer		1176532079
	define_integer		1684960623
'$SCNST_29':
	define_string		'$SCNST_29_0'
'$SCNST_30_0':
	define_desc		11,5
	define_integer		1684370000
	define_integer		1952539497
	define_integer		1867391077
	define_integer		1866866804
	define_integer		6581877
'$SCNST_30':
	define_string		'$SCNST_30_0'
'$SCNST_31_0':
	define_desc		3,8
	define_integer		541015871
	define_integer		1701080693
	define_integer		1701734758
	define_integer		2019893348
	define_integer		1953523043
	define_integer		544108393
	define_integer		1701080931
	define_integer		1061109536
'$SCNST_31':
	define_string		'$SCNST_31_0'
'$SCNST_32_0':
	define_desc		27,9
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		1646796900
	define_integer		1818697849
	define_integer		1818321519
	define_integer		692274976
	define_integer		46
'$SCNST_32':
	define_string		'$SCNST_32_0'
'$SCNST_33_0':
	define_desc		27,10
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1684631414
	define_integer		1970479143
	define_integer		1852141683
	define_integer		694445412
	define_integer		46
'$SCNST_33':
	define_string		'$SCNST_33_0'
'$SCNST_34_0':
	define_desc		3,10
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1953063287
	define_integer		661089897
	define_integer		1937077024
	define_integer		1684956528
	define_integer		774464613
'$SCNST_34':
	define_string		'$SCNST_34_0'
'$SCNST_35_0':
	define_desc		27,12
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1735550317
	define_integer		1764586085
	define_integer		1953853550
	define_integer		1970479143
	define_integer		1852141683
	define_integer		694445412
	define_integer		46
'$SCNST_35':
	define_string		'$SCNST_35_0'
'$SCNST_36_0':
	define_desc		11,10
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1953063287
	define_integer		661089897
	define_integer		656424224
	define_integer		1684631414
	define_integer		3025191
'$SCNST_36':
	define_string		'$SCNST_36_0'
'$SCNST_37_0':
	define_desc		19,12
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1818851104
	define_integer		1668227180
	define_integer		544372067
	define_integer		1701652264
	define_integer		1919248242
	define_integer		1886284077
	define_integer		539456629
	define_integer		1982275645
	define_integer		660892015
	define_integer		11817
'$SCNST_37':
	define_string		'$SCNST_37_0'
'$SCNST_38_0':
	define_desc		19,11
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1953063287
	define_integer		661089897
	define_integer		656424224
	define_integer		1953063287
	define_integer		661089897
	define_integer		11817
'$SCNST_38':
	define_string		'$SCNST_38_0'
'$SCNST_39_0':
	define_desc		11,12
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1953063287
	define_integer		661089897
	define_integer		656424224
	define_integer		1735550317
	define_integer		1764586085
	define_integer		1953853550
	define_integer		3025191
'$SCNST_39':
	define_string		'$SCNST_39_0'
'$SCNST_40_0':
	define_desc		19,14
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1818851104
	define_integer		1668227180
	define_integer		544372067
	define_integer		1701652264
	define_integer		1919248242
	define_integer		1886284077
	define_integer		539456629
	define_integer		1831280701
	define_integer		1701278309
	define_integer		1852386674
	define_integer		661943664
	define_integer		11817
'$SCNST_40':
	define_string		'$SCNST_40_0'
'$SCNST_41_0':
	define_desc		3,11
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1952801824
	define_integer		1702126437
	define_integer		656941156
	define_integer		1953063287
	define_integer		661089897
	define_integer		1935767328
	define_integer		1819239200
	define_integer		1952671084
	define_integer		774464613
'$SCNST_41':
	define_string		'$SCNST_41_0'
'$SCNST_42_0':
	define_desc		11,13
	define_integer		1684104516
	define_integer		1801678700
	define_integer		1818851104
	define_integer		1668227180
	define_integer		544372067
	define_integer		1701652264
	define_integer		1919248242
	define_integer		1886284077
	define_integer		539456629
	define_integer		544432503
	define_integer		1819045731
	define_integer		1702126437
	define_integer		3025252
'$SCNST_42':
	define_string		'$SCNST_42_0'
'$SCNST_43_0':
	define_desc		11,8
	define_integer		541015871
	define_integer		1701080693
	define_integer		1701734758
	define_integer		1701060708
	define_integer		1869374561
	define_integer		1948281699
	define_integer		543518841
	define_integer		4144959
'$SCNST_43':
	define_string		'$SCNST_43_0'
'$SCNST_44_0':
	define_desc		27,3
	define_integer		1886614867
	define_integer		1701080677
	define_integer		100
'$SCNST_46':
'$SCNST_45':
'$SCNST_44':
	define_string		'$SCNST_44_0'
'$SCNST_47_0':
	define_desc		11,2
	define_integer		1718185557
	define_integer		6579561
'$SCNST_51':
'$SCNST_50':
'$SCNST_49':
'$SCNST_48':
'$SCNST_47':
	define_string		'$SCNST_47_0'
'$SCNST_52_0':
	define_desc		27,3
	define_integer		1819045699
	define_integer		1702126437
	define_integer		100
'$SCNST_52':
	define_string		'$SCNST_52_0'
'$SCNST_53_0':
	define_desc		19,3
	define_integer		1819045699
	define_integer		1702126437
	define_integer		11876
'$SCNST_53':
	define_string		'$SCNST_53_0'
'$SCNST_54_0':
	define_desc		11,1
	define_integer		2125417
'$SCNST_54':
	define_string		'$SCNST_54_0'
'$SCNST_55_1':
	define_desc		19,1
	define_integer		8236
'$SCNST_55_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_55_1'
'$SCNST_55':
	define_vector		'$SCNST_55_0'
'$SCNST_56_2':
	define_desc		27,2
	define_integer		774774828
	define_integer		46
'$SCNST_56_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_56_2'
'$SCNST_56_0':
	define_vector		'$SCNST_56_1'
	define_atom		[]
'$SCNST_56':
	define_list		'$SCNST_56_0'
'$SCNST_59_1':
	define_desc		3,3
	define_integer		1869903201
	define_integer		1634692191
	define_integer		540876900
'$SCNST_59_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_59_1'
'$SCNST_59':
	define_vector		'$SCNST_59_0'
'$SCNST_60_1':
	define_desc		27,9
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		32
'$SCNST_60_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_60_1'
'$SCNST_64':
'$SCNST_60':
	define_vector		'$SCNST_60_0'
'$SCNST_61_1':
	define_desc		3,5
	define_integer		1092631072
	define_integer		544175221
	define_integer		1684107116
	define_integer		543649385
	define_integer		539897390
'$SCNST_61_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_61_1'
'$SCNST_61':
	define_vector		'$SCNST_61_0'
'$SCNST_62_1':
	define_desc		3,8
	define_integer		1869771333
	define_integer		1950097522
	define_integer		544434536
	define_integer		1969516397
	define_integer		1763730796
	define_integer		1869488243
	define_integer		1634934900
	define_integer		1046766966
'$SCNST_62_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_62_1'
'$SCNST_62':
	define_vector		'$SCNST_62_0'
'$SCNST_63_1':
	define_desc		19,3
	define_integer		1684107116
	define_integer		544368996
	define_integer		8253
'$SCNST_63_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_63_1'
'$SCNST_63':
	define_vector		'$SCNST_63_0'
'$SCNST_65_1':
	define_desc		3,5
	define_integer		1869771333
	define_integer		1832657010
	define_integer		1919905125
	define_integer		1768693881
	define_integer		1047816557
'$SCNST_65_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_65_1'
'$SCNST_65':
	define_vector		'$SCNST_65_0'
'$SCNST_66_1':
	define_desc		3,1
	define_integer		1701736292
'$SCNST_66_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_66_1'
'$SCNST_66':
	define_vector		'$SCNST_66_0'
'$SCNST_67_0':
	define_desc		0,3
	define_atom		mpimos_code_manager
	define_atom		request
	define_integer		3
'$SCNST_67':
	define_vector		'$SCNST_67_0'
'$SCNST_68_0':
	define_desc		0,3
	define_atom		mpimos_file_device
	define_atom		file_request
	define_integer		4
'$SCNST_68':
	define_vector		'$SCNST_68_0'
'$SCNST_69_0':
	define_desc		0,3
	define_atom		mpimos_timer_device
	define_atom		timer_request
	define_integer		3
'$SCNST_69':
	define_vector		'$SCNST_69_0'
'$SCNST_70_0':
	define_desc		0,3
	define_atom		mpimos_window_device
	define_atom		window_request
	define_integer		3
'$SCNST_70':
	define_vector		'$SCNST_70_0'
'$SCNST_71_0':
	define_desc		0,3
	define_atom		mpimos_directory
	define_atom		request
	define_integer		4
'$SCNST_71':
	define_vector		'$SCNST_71_0'
'$SCNST_72_0':
	define_desc		0,3
	define_atom		mpimos_task_monitor
	define_atom		error_monitor
	define_integer		3
'$SCNST_72':
	define_vector		'$SCNST_72_0'
'$SCNST_73_0':
	define_desc		0,3
	define_atom		mpimos_file
	define_atom		request
	define_integer		4
'$SCNST_73':
	define_vector		'$SCNST_73_0'
'$SCNST_74_0':
	define_desc		0,3
	define_atom		mpimos_task_monitor
	define_atom		error_monitor
	define_integer		2
'$SCNST_74':
	define_vector		'$SCNST_74_0'
'$SCNST_75_0':
	define_desc		0,3
	define_atom		mpimos_window
	define_atom		request
	define_integer		7
'$SCNST_75':
	define_vector		'$SCNST_75_0'
'$SCNST_76_0':
	define_desc		0,3
	define_atom		pimos_utility_error
	define_atom		error
	define_integer		3
'$SCNST_76':
	define_vector		'$SCNST_76_0'
'$SCNST_77_1':
	define_desc		11,6
	define_integer		1701080661
	define_integer		1701734758
	define_integer		1634869348
	define_integer		543519593
	define_integer		1701869940
	define_integer		2112032
'$SCNST_77_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_77_1'
'$SCNST_77':
	define_vector		'$SCNST_77_0'
'$SCNST_78_0':
	define_atom		abort
	define_atom		[]
'$SCNST_79':
'$SCNST_78':
	define_list		'$SCNST_78_0'
'$SCNST_80_0':
	define_desc		3,5
	define_integer		1701978237
	define_integer		1952675172
	define_integer		1936617321
	define_integer		544174880
	define_integer		779247974
'$SCNST_80':
	define_string		'$SCNST_80_0'
'$SCNST_81_0':
	define_desc		19,3
	define_integer		1920103747
	define_integer		980708965
	define_integer		31520
'$SCNST_81':
	define_string		'$SCNST_81_0'
