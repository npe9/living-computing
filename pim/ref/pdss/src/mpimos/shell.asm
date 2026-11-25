mpimos_command_interpreter:
	module		mpimos_command_interpreter
	entry		create,1,create_1_0
	entry		kl1cmp_create,1,kl1cmp_create_1_0
	entry		initenv,3,initenv_3_0
	entry		apply_goals,1,apply_goals_1_0
	entry		command_analyzer,3,command_analyzer_3_0
	entry		unit,4,unit_4_0
	module_entry		mpimos_command_interpreter
	predicate		create,1
create_1_0:
	b_merge		2,3
	create_goal		5
	set_variable		1,8
	set_marked_variable		2,11
	set_variable		3,6
	set_marked_variable		4,5
	set_value		5,2
	enqueue_goal		5,start_5_0
	create_goal		6
	set_variable		1,2
	set_variable		2,7
	set_variable		3,9
	set_variable		4,4
	set_variable		5,10
	set_value		6,5
	enqueue_goal		6,resource_manager_6_0
	create_goal		3
	set_values_inc		1,2,2
	set_value		3,11
	enqueue_goal		3,initenv_3_0
	put_integer		2,4040
	b_rate		2,2
	create_goal		6
	put_func		3,2,pathname
	write_element_value		3,1,11
	put_list_val_val		11,3,10
	set_value		1,11
	put_structured_constant		3,'$SCNST_0'
	set_value		2,3
	set_void		3
	set_variable		4,3
	set_values_dec		5,9,2
	enqueue_goal_with_priority		6,'$mpimos_directory:os_create/6_6_0',2
	put_integer		2,4040
	b_rate		2,2
	create_goal		3
	set_value		1,4
	set_variable		2,4
	set_value		3,3
	enqueue_goal_with_priority		3,'$mpimos_code_manager:os_get_command_stream/3_3_0',2
	put_integer		2,4040
	b_rate		2,2
	create_goal		6
	put_vector		3,2
	write_elements_dec		3,0,7,2
	put_list		6
	write_car_atom		6,show
	write_cdr_value		6,3
	set_value		1,6
	put_structured_constant		3,'$SCNST_1'
	set_value		2,3
	set_void		3
	set_value		4,5
	set_value		5,1
	set_value		6,4
	enqueue_goal_with_priority		6,'$mpimos_window:os_create/6_6_0',2
	proceed
create_1_1:
	suspend		create_1_0
	module_entry		mpimos_command_interpreter
	predicate		start,5
start_5_0:
	try_me_else		start_5_1
	jump_on_non_atom		1,start_5_3
	test_atom		1,success,start_5_1
	statistics		1,6,7,8,9,10
	put_structured_constant		1,'$SCNST_2'
	put_func		7,3,prompt
	write_element_void		7,1
	write_element_value		7,2,1
	put_list		1
	write_car_value		1,7
	write_cdr_nil		1
	put_list		7
	write_car_atom		7,nl
	write_cdr_value		7,1
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		9,1,7
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		7,1,9
	put_func		1,2,putt
	write_element_value		1,1,8
	put_list_val_val		8,1,7
	put_structured_constant		1,'$SCNST_5'
	put_list_val_val		7,1,8
	put_structured_constant		1,'$SCNST_6'
	put_list_val_val		8,1,7
	put_func		1,2,putt
	write_element_value		1,1,6
	put_list_val_val		6,1,8
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		7,1,6
	put_func		1,2,putl
	write_element_value		1,1,2
	put_list_val_val		2,1,7
	put_structured_constant		1,'$SCNST_8'
	put_list_val_val		6,1,2
	put_structured_constant		1,'$SCNST_9'
	put_list_val_val		2,1,6
	put_structured_constant		1,'$SCNST_10'
	put_list_val_val		6,1,2
	put_structured_constant		1,'$SCNST_11'
	put_list_val_val		2,1,6
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_func		2,2,do
	write_element_value		2,1,1
	get_list_val_var		3,1,2,6
	put_func		1,2,system_stream
	write_element_variable		1,1,8
	get_list_val_var		5,2,1,1
	put_structured_constant		2,'$SCNST_12'
	create_goal		5
	set_value		1,6
	set_value		2,4
	set_value		3,1
	set_marked_value		4,2
	set_variable		5,7
	enqueue_goal		5,startup_file_5_0
	put_nil		1
	put_atom		3,r
	put_void		4
	put_value		5,8
	put_nil		6
	execute_external		mpimos_file,os_create,7
start_5_3:
	check_vector		1,2,start_5_1
	read_element		1,0,6
	wait_atom		6,error
	read_element		1,1,6
	wait_atom		6,cannot_access
	put_structured_constant		6,'$SCNST_13'
	wait		6
	put_console		6
	put_integer		7,1
	g_halt		7
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		6
	collect_vector		1
	proceed
start_5_1:
	suspend		start_5_0
	module_entry		mpimos_command_interpreter
	predicate		startup_file,5
startup_file_5_0:
	try_me_else		startup_file_5_1
	jump_on_non_atom		5,startup_file_5_3
	test_atom		5,success,startup_file_5_1
	put_value		7,2
	put_value		5,3
	put_func		2,2,flush
	write_element_void		2,1
	put_list_val_var		3,2,6
	put_structured_constant		2,'$SCNST_14'
	put_list_val_val		8,2,3
	get_list_value		1,8
	put_func		1,2,take
	write_element_value		1,1,4
	put_integer		2,0
	put_values_inc		3,6,2
	put_integer		6,0
	execute		6,shell_wait_command_6_0
startup_file_5_3:
	check_vector		5,2,startup_file_5_1
	read_element		5,0,6
	wait_atom		6,error
	read_element		5,1,6
	collect_value		6
	collect_value		4
	collect_vector		5
	put_integer		4,0
	execute		4,shell_get_command_4_0
startup_file_5_1:
	suspend		startup_file_5_0
	module_entry		mpimos_command_interpreter
	predicate		kl1cmp_create,1
kl1cmp_create_1_0:
	put_structured_constant		2,'$SCNST_15'
	put_list_val_var		3,2,4
	b_merge		2,5
	get_value		5,4
	create_goal		6
	set_atom		1,kl1cmp
	set_integer		2,0
	set_variable		3,6
	set_marked_variable		4,5
	set_value		5,2
	set_integer		6,0
	enqueue_goal		6,shell_wait_command_6_0
	create_goal		6
	set_variable		1,2
	set_variable		2,7
	set_variable		3,8
	set_variable		4,4
	set_variable		5,9
	set_value		6,5
	enqueue_goal		6,resource_manager_6_0
	create_goal		3
	set_values_inc		1,2,2
	set_variable		3,10
	enqueue_goal		3,initenv_3_0
	put_integer		2,4040
	b_rate		2,2
	create_goal		6
	put_func		3,2,pathname
	write_element_value		3,1,10
	put_list_val_val		10,3,9
	set_value		1,10
	put_structured_constant		3,'$SCNST_16'
	set_value		2,3
	set_void		3
	set_variable		4,3
	set_value		5,8
	set_void		6
	enqueue_goal_with_priority		6,'$mpimos_directory:os_create/6_6_0',2
	put_integer		2,4040
	b_rate		2,2
	create_goal		3
	set_value		1,4
	set_variable		2,4
	set_value		3,3
	enqueue_goal_with_priority		3,'$mpimos_code_manager:os_get_command_stream/3_3_0',2
	put_integer		2,4040
	b_rate		2,2
	create_goal		6
	put_vector		3,2
	write_elements_dec		3,0,7,2
	put_list		6
	write_car_atom		6,show
	write_cdr_value		6,3
	set_value		1,6
	put_structured_constant		3,'$SCNST_17'
	set_value		2,3
	set_void		3
	set_value		4,5
	set_value		5,1
	set_value		6,4
	enqueue_goal_with_priority		6,'$mpimos_window:os_create/6_6_0',2
	proceed
kl1cmp_create_1_1:
	suspend		kl1cmp_create_1_0
	module_entry		mpimos_command_interpreter
	predicate		initenv,3
initenv_3_0:
	b_get_library_directory		4
	put_marked_value		6,4
	put_structured_constant		5,'$SCNST_18'
	b_append_string		6,5,5
	put_structured_constant		6,'$SCNST_19'
	b_append_string		4,6,4
	put_structured_constant		6,'$SCNST_20'
	put_list_val_val		7,6,2
	put_structured_constant		2,'$SCNST_21'
	put_list_val_val		6,2,7
	put_list		2
	write_car_value		2,4
	write_cdr_nil		2
	put_list_val_val		4,5,2
	put_structured_constant		2,'$SCNST_22'
	put_list_val_val		5,2,4
	put_func		2,3,setenv
	write_element_atom		2,1,loaddir
	write_element_value		2,2,5
	put_list_val_val		4,2,6
	put_structured_constant		2,'$SCNST_23'
	put_list_val_val		5,2,4
	put_structured_constant		2,'$SCNST_24'
	put_list_val_val		4,2,5
	put_structured_constant		2,'$SCNST_25'
	put_list_val_val		5,2,4
	put_structured_constant		2,'$SCNST_26'
	put_list_val_val		4,2,5
	put_structured_constant		2,'$SCNST_27'
	put_list_val_val		5,2,4
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		4,2,5
	put_structured_constant		2,'$SCNST_29'
	put_list_val_val		5,2,4
	put_structured_constant		2,'$SCNST_30'
	put_list_val_val		4,2,5
	put_func		2,3,setenv
	write_element_atom		2,1,world
	write_element_value		2,2,3
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
initenv_3_1:
	suspend		initenv_3_0
	module_entry		mpimos_command_interpreter
	predicate		shell_get_command,4
shell_get_command_4_0:
	try_me_else		shell_get_command_4_1
	wait_list_var_var		2,5,6
	collect_list		2
	collect_value		5
	put_value		2,6
	execute		4,shell_get_command_4_0
shell_get_command_4_1:
	put_value		9,2
	put_value		6,4
	put_func		2,3,getft
	write_element_variable		2,1,8
	write_element_variable		2,2,5
	put_list_val_var		4,2,7
	put_list		2
	write_car_atom		2,show
	write_cdr_value		2,4
	get_list_value		1,2
	put_func		1,5,expand
	write_element_value		1,1,8
	write_element_value		1,2,5
	write_element_variable		1,3,8
	write_element_variable		1,4,4
	put_func		2,2,macro_expander
	write_element_value		2,1,1
	get_list_val_var		3,1,2,5
	put_value		1,8
	put_value		2,4
	put_value		3,7
	put_value		4,9
	execute		6,shell_wait_command_6_0
shell_get_command_4_5:
	suspend		shell_get_command_4_0
	module_entry		mpimos_command_interpreter
	predicate		shell_wait_command,6
shell_wait_command_6_0:
	try_me_else		shell_wait_command_6_1
	wait_list_var_var		4,7,8
	collect_list		4
	collect_value		7
	put_value		4,8
	execute		6,shell_wait_command_6_0
shell_wait_command_6_1:
	try_me_else		shell_wait_command_6_5
	wait_atom		1,end_of_file
	put_integer		1,0
	g_halt		1
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	proceed
shell_wait_command_6_5:
	try_me_else		shell_wait_command_6_7
	put_atom		7,end_of_file
	g_diff		1,7
	put_structured_constant		7,'$SCNST_31'
	put_list_val_var		8,7,7
	put_list		9
	write_car_atom		9,initenv
	write_cdr_value		9,8
	get_list_value		5,9
	put_value		5,7
	execute		6,shell_create_task_6_0
shell_wait_command_6_7:
	suspend		shell_wait_command_6_0
	module_entry		mpimos_command_interpreter
	predicate		shell_create_task,6
shell_create_task_6_0:
	try_me_else		shell_create_task_6_1
	wait_list_var_var		4,7,8
	collect_list		4
	collect_value		7
	put_value		4,8
	execute		6,shell_create_task_6_0
shell_create_task_6_1:
	put_vector		7,2
	write_element_variable		7,0,10
	write_element_variable		7,1,9
	get_vector_value		3,7
	put_vector		3,3
	write_element_variable		3,0,13
	write_element_variable		3,1,12
	write_element_variable		3,2,11
	put_func		7,3,getenv
	write_element_atom		7,1,reduction
	write_element_variable		7,2,14
	put_list_val_val		8,7,3
	put_func		3,2,system_stream
	write_element_variable		3,1,15
	put_list_val_val		7,3,8
	get_list_value		5,7
	put_func		3,2,apply_goals
	write_element_variable		3,1,7
	put_func		5,3,:
	write_element_atom		5,1,mpimos_command_interpreter
	write_element_value		5,2,3
	put_list		3
	write_car_value		3,5
	write_cdr_nil		3
	put_func		5,4,command_analyzer
	write_element_variable		5,1,16
	write_element_variable		5,2,8
	write_element_value		5,3,7
	put_func		7,3,:
	write_element_atom		7,1,mpimos_command_interpreter
	write_element_value		7,2,5
	put_list_val_val		5,7,3
	put_vector		3,1
	write_element_value		3,0,5
	create_goal		11
	set_value		1,14
	set_variable		2,14
	set_variable		3,17
	set_value		4,4
	set_value		5,9
	set_value		6,13
	set_variable		7,7
	set_marked_variable		8,9
	set_variable		9,5
	set_nil		10
	set_atom		11,normal
	enqueue_goal		11,reduction_check_11_0
	put_integer		4,4092
	b_rate		4,4
	create_goal		12
	set_atom		1,mpimos_command_interpreter
	set_atom		2,apply_goals
	set_value		3,3
	set_integer		4,0
	set_integer		5,100
	set_integer		6,-1
	set_value		7,17
	set_values_inc		8,14,2
	set_value		10,10
	set_value		11,12
	set_value		12,9
	enqueue_goal_with_priority		12,'$mpimos_task_monitor:create/12_12_0',4
	create_goal		3
	set_value		1,6
	set_value		2,9
	set_value		3,7
	enqueue_goal		3,new_task_name_3_0
	create_goal		3
	set_values_inc		1,1,2
	set_value		3,16
	enqueue_goal_external		mpimos_utility,melt,3
	put_value		1,5
	put_value		2,8
	put_value		3,11
	execute		3,valve_3_0
shell_create_task_6_5:
	suspend		shell_create_task_6_0
	module_entry		mpimos_command_interpreter
	predicate		reduction_check,11
reduction_check_11_0:
	try_me_else		reduction_check_11_1
	integer		1
	put_integer		12,0
	g_less_than		12,1
	put_integer		12,100000
	g_less_than		1,12
	put_integer		12,10000
	b_multiply		1,12,1
	put_list		12
	write_car_atom		12,start
	write_cdr_variable		12,14
	put_func		13,2,more_reduction
	write_element_value		13,1,1
	put_list_val_val		1,13,12
	get_list_value		3,1
	put_value		1,2
	put_value		2,14
	put_values_inc		3,4,8
	execute		10,shell_with_task_10_0
reduction_check_11_1:
	otherwise		reduction_check_11_0
	put_func		12,2,flush
	write_element_void		12,1
	put_list_val_var		13,12,14
	put_list		12
	write_car_atom		12,nl
	write_cdr_value		12,13
	put_func		13,2,putt
	write_element_value		13,1,1
	put_list_val_val		1,13,12
	put_structured_constant		12,'$SCNST_32'
	put_list_val_val		13,12,1
	put_structured_constant		1,'$SCNST_33'
	put_list_val_val		12,1,13
	get_list_value		5,12
	put_list		1
	write_car_atom		1,start
	write_cdr_variable		1,12
	put_structured_constant		5,'$SCNST_34'
	put_list_val_val		13,5,1
	get_list_value		3,13
	put_value		1,2
	put_value		2,12
	put_value		3,4
	put_value		4,14
	put_values_inc		5,6,6
	execute		10,shell_with_task_10_0
reduction_check_11_5:
	suspend		reduction_check_11_0
	module_entry		mpimos_command_interpreter
	predicate		shell_with_task,10
shell_with_task_10_0:
	try_me_else		shell_with_task_10_1
	list		3
	read_car		3,11
	integer		11
	jump_on_integer		11,3,shell_with_task_10_1
	table_entry		shell_with_task_10_1
	table_entry		shell_with_task_10_4
	table_entry		shell_with_task_10_5
shell_with_task_10_4:
	read_cdr		3,12
	collect_value		10
	get_atom		8,end
	put_structured_constant		8,'$SCNST_35'
	put_func		10,2,statistics
	write_element_variable		10,1,11
	put_reused_list_val_val		3,3,10,8
	put_list		8
	write_car_atom		8,abort
	write_cdr_value		8,3
	get_list_value		2,8
	put_structured_constant		2,'$SCNST_36'
	put_func		3,2,putt
	write_element_value		3,1,11
	put_list_val_val		8,3,2
	put_structured_constant		2,'$SCNST_37'
	put_list_val_val		3,2,8
	put_func		2,2,putb
	write_element_value		2,1,7
	put_list_val_val		7,2,3
	put_structured_constant		2,'$SCNST_38'
	put_list_val_val		3,2,7
	put_func		2,2,do
	write_element_value		2,1,3
	get_list_val_var		4,7,2,3
	put_value		2,12
	put_values_inc		4,5,2
	put_value		6,9
	execute		6,after_care_6_0
shell_with_task_10_5:
	read_cdr		3,12
	put_func		11,2,statistics
	write_element_variable		11,1,14
	get_reused_list_val_var		2,3,3,11,13
	put_func		2,2,flush
	write_element_void		2,1
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_39'
	put_list_val_val		11,3,2
	put_func		2,2,putt
	write_element_value		2,1,14
	put_list_val_val		3,2,11
	put_structured_constant		2,'$SCNST_40'
	put_list_val_val		11,2,3
	put_func		2,2,putb
	write_element_marked_value		2,1,7
	put_list_val_val		3,2,11
	put_structured_constant		2,'$SCNST_41'
	put_list_val_val		11,2,3
	put_func		2,2,do
	write_element_value		2,1,11
	get_list_val_var		4,3,2,11
	put_values_dec		2,13,3
	execute		10,shell_with_task_10_0
shell_with_task_10_1:
	try_me_else		shell_with_task_10_9
	list		1
	read_car		1,11
	jump_on_non_atom		11,shell_with_task_10_12
	branch_on_atom		11,3,shell_with_task_10_9
	bucket_entry_a		aborted,shell_with_task_10_13
	bucket_entry_a		deadlock,shell_with_task_10_14
	bucket_entry_a		succeeded,shell_with_task_10_15
shell_with_task_10_13:
	read_cdr		1,12
	put_value		13,8
	put_values_inc		14,2,2
	put_values_inc		16,5,2
	put_value		8,7
	put_value		18,9
	put_value		11,10
	put_marked_value		13,13
	get_atom		13,end
	put_func		2,2,getl
	write_element_variable		2,1,5
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_structured_constant		2,'$SCNST_42'
	put_list_val_val		3,2,1
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	put_func		2,2,do
	write_element_value		2,1,1
	get_list_val_var		4,1,2,2
	put_value		1,5
	put_value		3,12
	put_values_inc		4,14,4
	put_value		9,13
	put_value		10,18
	execute		11,shell_with_task_2_11_0
shell_with_task_10_14:
	read_cdr		1,12
	put_values_inc		13,2,2
	put_values_inc		15,5,5
	put_value		11,10
	put_func		2,3,prompt
	write_element_void		2,1
	write_element_variable		2,2,5
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_func		2,3,getft
	write_element_variable		2,1,6
	write_element_void		2,2
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_43'
	put_func		2,3,prompt
	write_element_value		2,1,5
	write_element_value		2,2,1
	put_list_val_val		1,2,3
	put_list		2
	write_car_atom		2,show
	write_cdr_value		2,1
	put_func		1,2,do
	write_element_value		1,1,2
	get_list_val_var		4,3,1,2
	put_value		1,6
	put_values_inc		3,12,8
	execute		11,shell_with_task_3_11_0
shell_with_task_10_15:
	read_cdr		1,12
	atom		10
	branch_on_atom		10,2,shell_with_task_10_9
	bucket_entry_a		after_care,shell_with_task_10_17
	bucket_entry_a		normal,shell_with_task_10_18
shell_with_task_10_17:
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		12
	put_structured_constant		7,'$SCNST_44'
	get_reused_list_val_var		4,8,1,7,1
	put_structured_constant		4,'$SCNST_45'
	get_value		2,4
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,shell_get_command_4_0
shell_with_task_10_18:
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		12
	put_structured_constant		7,'$SCNST_46'
	get_reused_list_val_var		4,8,1,7,1
	put_structured_constant		4,'$SCNST_47'
	get_value		2,4
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,shell_get_command_4_0
shell_with_task_10_12:
	is_vector		11,shell_with_task_10_9
	jump_on_arity		11,6,shell_with_task_10_9
	table_entry		shell_with_task_10_9
	table_entry		shell_with_task_10_9
	table_entry		shell_with_task_10_19
	table_entry		shell_with_task_10_9
	table_entry		shell_with_task_10_9
	table_entry		shell_with_task_10_20
shell_with_task_10_19:
	read_element		11,0,12
	atom		12
	branch_on_atom		12,2,shell_with_task_10_9
	bucket_entry_a		after_care,shell_with_task_10_22
	bucket_entry_a		reduction_limit,shell_with_task_10_23
shell_with_task_10_22:
	read_cdr		1,13
	read_element		11,1,14
	collect_vector		11
	put_reused_list_val_val		11,1,14,9
	put_value		1,13
	put_value		9,11
	execute		10,shell_with_task_10_0
shell_with_task_10_23:
	read_cdr		1,13
	read_element		11,1,14
	put_value		15,7
	put_value		16,3
	put_value		7,5
	put_value		17,6
	put_values_inc		18,8,2
	put_value		12,10
	put_func		3,3,prompt
	write_element_void		3,1
	write_element_variable		3,2,6
	put_reused_list		1,1
	write_car_value		1,3
	write_cdr_nil		1
	put_func		3,3,getft
	write_element_variable		3,1,8
	write_element_void		3,2
	put_list_val_val		5,3,1
	put_structured_constant		1,'$SCNST_48'
	put_func		3,3,prompt
	write_element_value		3,1,6
	write_element_value		3,2,1
	put_list_val_val		1,3,5
	put_structured_constant		3,'$SCNST_49'
	put_list_val_val		5,3,1
	put_structured_constant		1,'$SCNST_50'
	put_list_val_val		3,1,5
	put_reused_func		1,11,putt
	write_element_variable		1,1,6
	put_list_val_val		5,1,3
	put_structured_constant		1,'$SCNST_51'
	put_list_val_val		3,1,5
	put_func		1,2,putb
	write_element_marked_value		1,1,15
	put_list_val_val		5,1,3
	put_structured_constant		1,'$SCNST_52'
	put_list_val_val		3,1,5
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_list		3
	write_car_atom		3,show
	write_cdr_value		3,1
	put_func		1,2,do
	write_element_value		1,1,3
	get_list_val_var		4,5,1,3
	put_func		1,2,statistics
	write_element_value		1,1,6
	get_list_val_var		2,4,1,5
	put_value		1,8
	put_value		2,14
	put_value		4,13
	put_value		6,16
	put_value		8,17
	put_value		9,15
	put_values_inc		10,18,2
	execute		12,shell_with_task_1_12_0
shell_with_task_10_20:
	read_element		11,0,12
	wait_atom		12,raised
	read_element		11,1,13
	wait_vector		13,2
	read_element		13,0,14
	wait_atom		14,shell
	read_element		13,1,15
	try_me_else		shell_with_task_10_27
	atom		15
	branch_on_atom		15,2,shell_with_task_10_27
	bucket_entry_a		aborted,shell_with_task_10_29
	bucket_entry_a		fail,shell_with_task_10_30
shell_with_task_10_29:
	read_cdr		1,16
	read_elements_inc		11,2,17,3
	collect_value		19
	collect_value		17
	collect_vector		11
	put_value		12,8
	put_values_inc		14,2,2
	put_value		17,5
	put_value		19,6
	put_value		8,7
	put_value		20,9
	put_value		11,10
	get_nil		18
	put_marked_value		12,12
	get_atom		12,end
	put_reused_func		2,13,getl
	write_element_variable		2,1,5
	put_reused_list		1,1
	write_car_value		1,2
	write_cdr_nil		1
	put_structured_constant		2,'$SCNST_53'
	put_list_val_val		3,2,1
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	put_func		2,2,do
	write_element_value		2,1,1
	get_list_val_var		4,1,2,2
	put_value		1,5
	put_value		3,16
	put_values_inc		4,14,2
	put_value		6,17
	put_value		7,19
	put_value		9,12
	put_value		10,20
	execute		11,shell_with_task_0_11_0
shell_with_task_10_30:
	read_cdr		1,16
	read_elements_inc		11,2,17,3
	collect_list		1
	collect_value		10
	collect_value		7
	collect_value		19
	collect_value		17
	collect_vector		11
	collect_vector		13
	get_nil		18
	get_atom		8,end
	put_structured_constant		1,'$SCNST_54'
	get_value		2,1
	put_value		1,16
	put_values_inc		2,3,4
	put_value		6,9
	execute		6,after_care_6_0
shell_with_task_10_27:
	read_elements_inc		11,2,16,3
	read_cdr		1,19
	try_me_else		shell_with_task_10_9
	put_atom		20,aborted
	g_diff		15,20
	put_atom		20,fail
	g_diff		15,20
	collect_value		18
	collect_value		16
	collect_vector		11
	get_nil		17
	put_reused_func		11,13,flush
	write_element_void		11,1
	put_reused_list		1,1
	write_car_value		1,11
	write_cdr_nil		1
	put_list		11
	write_car_atom		11,nl
	write_cdr_value		11,1
	put_func		1,2,shell
	write_element_value		1,1,15
	put_func		12,2,putt
	write_element_value		12,1,1
	put_list_val_val		1,12,11
	put_structured_constant		11,'$SCNST_55'
	put_list_val_val		12,11,1
	put_func		1,2,do
	write_element_value		1,1,12
	get_list_val_var		4,12,1,11
	put_value		1,19
	put_value		4,11
	execute		10,shell_with_task_10_0
shell_with_task_10_9:
	suspend		shell_with_task_10_0
	module_entry		mpimos_command_interpreter
	predicate		shell_with_task_1,12
shell_with_task_1_12_0:
	try_me_else		shell_with_task_1_12_1
	jump_on_non_atom		1,shell_with_task_1_12_3
	test_atom		1,c,shell_with_task_1_12_1
	put_value		14,3
	get_nil		2
	put_func		1,3,getenv
	write_element_atom		1,1,reduction
	write_element_variable		1,2,2
	get_list_val_var		7,3,1,13
	put_value		1,2
	put_values_inc		2,4,3
	put_values_dec		5,14,2
	put_values_inc		7,8,5
	execute		11,reduction_check_11_0
shell_with_task_1_12_3:
	is_integer		1,shell_with_task_1_12_1
	put_integer		13,1
	g_not_less_than		1,13
	put_value		13,3
	get_nil		2
	put_values_inc		2,4,3
	put_value		5,13
	put_values_inc		6,7,6
	execute		11,reduction_check_11_0
shell_with_task_1_12_1:
	otherwise		shell_with_task_1_12_0
	collect_value		12
	collect_value		1
	get_atom		10,end
	get_nil		2
	put_structured_constant		1,'$SCNST_56'
	put_func		2,2,putb
	write_element_value		2,1,9
	put_list_val_val		9,2,1
	put_structured_constant		1,'$SCNST_57'
	put_list_val_val		2,1,9
	put_func		1,2,do
	write_element_value		1,1,2
	get_list_val_var		3,2,1,9
	put_structured_constant		1,'$SCNST_58'
	get_value		5,1
	put_value		1,4
	put_value		2,6
	put_value		3,9
	put_values_inc		4,7,2
	put_value		6,11
	execute		6,after_care_6_0
shell_with_task_1_12_8:
	suspend		shell_with_task_1_12_0
	module_entry		mpimos_command_interpreter
	predicate		shell_with_task_0,11
shell_with_task_0_11_0:
	try_me_else		shell_with_task_0_11_1
	wait		1
	collect_value		11
	get_atom		9,end
	put_structured_constant		1,'$SCNST_59'
	put_func		9,2,putb
	write_element_value		9,1,8
	put_list_val_val		8,9,1
	put_structured_constant		1,'$SCNST_60'
	put_list_val_val		9,1,8
	put_func		1,2,do
	write_element_value		1,1,9
	get_list_val_var		2,9,1,8
	put_structured_constant		1,'$SCNST_61'
	get_value		4,1
	put_value		1,3
	put_value		2,5
	put_value		3,8
	put_values_inc		4,6,2
	put_value		6,10
	execute		6,after_care_6_0
shell_with_task_0_11_1:
	suspend		shell_with_task_0_11_0
	module_entry		mpimos_command_interpreter
	predicate		shell_with_task_2,11
shell_with_task_2_11_0:
	try_me_else		shell_with_task_2_11_1
	wait		1
	collect_value		11
	get_atom		9,end
	put_structured_constant		1,'$SCNST_62'
	put_func		9,2,putt
	write_element_variable		9,1,12
	put_list_val_val		11,9,1
	put_structured_constant		1,'$SCNST_63'
	put_list_val_val		9,1,11
	put_func		1,2,putb
	write_element_value		1,1,8
	put_list_val_val		8,1,9
	put_structured_constant		1,'$SCNST_64'
	put_list_val_val		9,1,8
	put_func		1,2,do
	write_element_value		1,1,9
	get_list_val_var		2,9,1,8
	put_structured_constant		1,'$SCNST_65'
	put_func		2,2,statistics
	write_element_value		2,1,12
	put_list_val_val		9,2,1
	get_list_value		4,9
	put_value		1,3
	put_value		2,5
	put_value		3,8
	put_values_inc		4,6,2
	put_value		6,10
	execute		6,after_care_6_0
shell_with_task_2_11_1:
	suspend		shell_with_task_2_11_0
	module_entry		mpimos_command_interpreter
	predicate		shell_with_task_3,11
shell_with_task_3_11_0:
	try_me_else		shell_with_task_3_11_1
	wait_atom		1,c
	put_value		12,2
	put_list		1
	write_car_atom		1,start
	write_cdr_variable		1,2
	get_list_value		4,1
	put_value		1,3
	put_value		3,5
	put_value		4,12
	put_values_inc		5,6,6
	execute		10,shell_with_task_10_0
shell_with_task_3_11_1:
	otherwise		shell_with_task_3_11_0
	collect_value		11
	collect_value		1
	get_atom		9,end
	put_structured_constant		1,'$SCNST_66'
	put_func		9,2,putt
	write_element_variable		9,1,12
	put_list_val_val		11,9,1
	put_structured_constant		1,'$SCNST_67'
	put_list_val_val		9,1,11
	put_func		1,2,putb
	write_element_value		1,1,8
	put_list_val_val		8,1,9
	put_structured_constant		1,'$SCNST_68'
	put_list_val_val		9,1,8
	put_func		1,2,do
	write_element_value		1,1,9
	get_list_val_var		2,9,1,8
	put_structured_constant		1,'$SCNST_69'
	put_func		2,2,statistics
	write_element_value		2,1,12
	put_list_val_val		9,2,1
	get_list_value		4,9
	put_value		1,3
	put_value		2,5
	put_value		3,8
	put_values_inc		4,6,2
	put_value		6,10
	execute		6,after_care_6_0
shell_with_task_3_11_6:
	suspend		shell_with_task_3_11_0
	module_entry		mpimos_command_interpreter
	predicate		after_care,6
after_care_6_0:
	try_me_else		after_care_6_1
	wait_nil		1
	try_me_else		after_care_6_3
	wait_nil		6
	put_structured_constant		1,'$SCNST_70'
	get_list_val_var		3,6,1,1
	put_values_inc		3,4,2
	execute		4,shell_get_command_4_0
after_care_6_3:
	try_me_else		after_care_6_1
	put_nil		7
	g_diff		6,7
	collect_value		7
	put_vector		1,2
	write_element_variable		1,0,11
	write_element_variable		1,1,10
	put_func		7,2,flush
	write_element_void		7,1
	put_list		8
	write_car_value		8,7
	write_cdr_nil		8
	put_structured_constant		7,'$SCNST_71'
	put_list_val_val		9,7,8
	put_func		7,2,do
	write_element_value		7,1,9
	put_list_val_val		8,7,1
	get_list_value		3,8
	put_vector		1,2
	write_element_variable		1,0,8
	write_element_variable		1,1,7
	put_func		3,2,system_stream
	write_element_variable		3,1,9
	put_list_val_val		12,3,1
	get_list_value		4,12
	create_goal		10
	set_variable		1,4
	set_variable		2,3
	set_value		3,2
	set_value		4,10
	set_value		5,7
	set_value		6,5
	put_structured_constant		1,'$SCNST_72'
	set_value		7,1
	set_void		8
	set_nil		9
	set_atom		10,after_care
	enqueue_goal		10,shell_with_task_10_0
	put_integer		1,4092
	b_rate		1,1
	create_goal		12
	set_atom		1,mpimos_command_interpreter
	set_atom		2,apply_goals
	put_vector		2,1
	write_element_value		2,0,6
	set_value		3,2
	set_integer		4,0
	set_integer		5,100
	set_integer		6,-1
	put_list		2
	write_car_atom		2,start
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_73'
	put_list_val_val		5,3,2
	set_values_dec		7,5,2
	set_value		9,9
	set_value		10,11
	set_value		11,8
	put_structured_constant		2,'$SCNST_74'
	set_value		12,2
	enqueue_goal_with_priority		12,'$mpimos_task_monitor:create/12_12_0',1
	proceed
after_care_6_1:
	otherwise		after_care_6_0
	try_me_else		after_care_6_10
	wait_list_var_var		1,7,8
	collect_list		1
	collect_value		7
	put_value		1,8
	execute		6,after_care_6_0
after_care_6_10:
	suspend		after_care_6_0
	module_entry		mpimos_command_interpreter
	predicate		new_task_name,3
new_task_name_3_0:
	put_marked_value		4,1
	b_increment		4,4
	get_value		3,4
	put_structured_constant		3,'$SCNST_75'
	put_variable		5,4
	b_append_string		3,5,3
	get_value		3,2
	put_value		2,4
	execute_external		mpimos_utility,integer_to_string,2
new_task_name_3_1:
	suspend		new_task_name_3_0
	module_entry		mpimos_command_interpreter
	predicate		unit,4
unit_4_0:
	try_me_else		unit_4_1
	atom		2
	branch_on_atom		2,2,unit_4_1
	bucket_entry_a		fail,unit_4_3
	bucket_entry_a		success,unit_4_4
unit_4_3:
	collect_value		4
	collect_value		1
	get_atom		3,fail
	proceed
unit_4_4:
	put_list		2
	write_car_atom		2,start
	write_cdr_variable		2,6
	put_structured_constant		5,'$SCNST_76'
	put_list_val_val		7,5,2
	create_goal		4
	set_variable		1,8
	set_value		2,6
	set_values_inc		3,3,2
	enqueue_goal		4,unit_monitor_4_0
	put_vector		3,1
	write_element_value		3,0,1
	put_atom		1,mpimos_command_interpreter
	put_atom		2,apply_goals
	put_integer		4,0
	put_integer		5,4
	put_integer		6,131072
	execute_external		'Sho-en',create,8
unit_4_1:
	suspend		unit_4_0
	module_entry		mpimos_command_interpreter
	predicate		unit_monitor,4
unit_monitor_4_0:
	try_me_else		unit_monitor_4_1
	list		1
	read_car		1,5
	jump_on_non_atom		5,unit_monitor_4_4
	branch_on_atom		5,3,unit_monitor_4_1
	bucket_entry_a		aborted,unit_monitor_4_5
	bucket_entry_a		reduction_limit,unit_monitor_4_6
	bucket_entry_a		succeeded,unit_monitor_4_7
unit_monitor_4_5:
	read_cdr		1,6
	collect_value		6
	put_integer		6,131072
	put_structured_constant		5,'$SCNST_77'
	put_void		7
	b_raise		6,5,7
	get_atom		3,fail
	put_structured_constant		3,'$SCNST_78'
	put_func		5,2,statistics
	write_element_value		5,1,4
	put_reused_list_val_val		1,1,5,3
	get_list_value		2,1
	proceed
unit_monitor_4_6:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,start
	write_cdr_variable		1,7
	put_structured_constant		5,'$SCNST_79'
	put_list_val_val		8,5,1
	get_list_value		2,8
	put_values_inc		1,6,2
	execute		4,unit_monitor_4_0
unit_monitor_4_7:
	read_cdr		1,6
	collect_value		6
	get_atom		3,success
	put_structured_constant		3,'$SCNST_80'
	put_func		5,2,statistics
	write_element_value		5,1,4
	put_reused_list_val_val		1,1,5,3
	get_list_value		2,1
	proceed
unit_monitor_4_4:
	check_vector		5,5,unit_monitor_4_1
	read_element		5,0,6
	wait_atom		6,raised
	read_element		5,1,7
	wait_vector		7,2
	read_element		7,0,8
	wait_atom		8,shell
	read_element		7,1,9
	atom		9
	branch_on_atom		9,2,unit_monitor_4_1
	bucket_entry_a		aborted,unit_monitor_4_12
	bucket_entry_a		fail,unit_monitor_4_13
unit_monitor_4_12:
	read_cdr		1,10
	read_elements_inc		5,2,11,3
	collect_value		10
	collect_value		13
	collect_vector		5
	put_integer		6,131072
	put_structured_constant		5,'$SCNST_81'
	b_raise		6,5,11
	get_nil		12
	get_atom		3,fail
	put_structured_constant		3,'$SCNST_82'
	put_reused_func		5,7,statistics
	write_element_value		5,1,4
	put_reused_list_val_val		1,1,5,3
	get_list_value		2,1
	proceed
unit_monitor_4_13:
	read_cdr		1,10
	read_elements_inc		5,2,11,3
	collect_value		10
	collect_value		13
	collect_vector		5
	put_integer		6,131072
	put_structured_constant		5,'$SCNST_83'
	b_raise		6,5,11
	get_nil		12
	get_atom		3,fail
	put_structured_constant		3,'$SCNST_84'
	put_reused_func		5,7,statistics
	write_element_value		5,1,4
	put_reused_list_val_val		1,1,5,3
	get_list_value		2,1
	proceed
unit_monitor_4_1:
	suspend		unit_monitor_4_0
	module_entry		mpimos_command_interpreter
	predicate		apply_goals,1
apply_goals_1_0:
	try_me_else		apply_goals_1_1
	jump_on_non_list_var_var		1,apply_goals_1_3,2,3
	collect_list		1
	create_goal		1
	set_value		1,3
	enqueue_goal		1,apply_goals_1_0
	put_value		1,2
	execute		1,apply_goal_1_0
apply_goals_1_3:
	check_nil		1,apply_goals_1_1
	proceed
apply_goals_1_1:
	suspend		apply_goals_1_0
	module_entry		mpimos_command_interpreter
	predicate		apply_goal,1
apply_goal_1_0:
	put_variable		4,2
	put_variable		5,3
	b_apply		4,5
	execute_external		mpimos_utility,get_predicate,3
apply_goal_1_1:
	suspend		apply_goal_1_0
	module_entry		mpimos_command_interpreter
	predicate		command_analyzer,3
command_analyzer_3_0:
	b_merge		4,5
	get_value		5,2
	b_merge		5,2
	get_value		2,3
	put_values_inc		2,4,2
	execute		3,command_analyzer__3_0
command_analyzer_3_1:
	suspend		command_analyzer_3_0
	module_entry		mpimos_command_interpreter
	predicate		command_analyzer_,3
command_analyzer__3_0:
	try_me_else		command_analyzer__3_1
	wait_vector		1,3
	read_element		1,0,4
	atom		4
	branch_on_atom		4,2,command_analyzer__3_1
	bucket_entry_a		',',command_analyzer__3_4
	bucket_entry_a		;,command_analyzer__3_5
command_analyzer__3_4:
	read_elements_inc		1,1,5,2
	collect_vector		1
	put_vector		7,2
	write_element_variable		7,0,1
	write_element_variable		7,1,4
	get_vector_value		2,7
	put_vector		8,2
	write_element_variable		8,0,2
	write_element_variable		8,1,7
	get_vector_value		3,8
	create_goal		3
	set_value		1,6
	set_values_inc		2,1,2
	enqueue_goal		3,command_analyzer__3_0
	put_values_dec		1,5,2
	put_value		3,7
	execute		3,trans_element_3_0
command_analyzer__3_5:
	read_elements_inc		1,1,5,2
	put_vector		8,2
	write_element_variable		8,0,7
	write_element_variable		8,1,4
	get_vector_value		2,8
	put_func		2,5,unit
	write_element_variable		2,1,8
	write_element_atom		2,2,success
	write_element_variable		2,3,9
	write_element_void		2,4
	put_reused_func		1,1,:
	write_element_atom		1,1,mpimos_command_interpreter
	write_element_value		1,2,2
	get_list_val_var		3,2,1,1
	create_goal		4
	set_values_inc		1,6,2
	set_value		3,9
	set_value		4,1
	enqueue_goal		4,s_command_analyzer_4_0
	put_values_dec		1,5,2
	put_value		3,8
	execute		3,trans_element_3_0
command_analyzer__3_1:
	otherwise		command_analyzer__3_0
	execute		3,trans_element_3_0
command_analyzer__3_11:
	suspend		command_analyzer__3_0
	module_entry		mpimos_command_interpreter
	predicate		s_command_analyzer,4
s_command_analyzer_4_0:
	try_me_else		s_command_analyzer_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,;
	read_elements_inc		1,1,5,2
	put_vector		9,2
	write_element_variable		9,0,8
	write_element_variable		9,1,7
	get_vector_value		2,9
	put_func		2,5,unit
	write_element_variable		2,1,9
	write_element_value		2,2,3
	write_element_variable		2,3,3
	write_element_void		2,4
	put_reused_func		1,1,:
	write_element_atom		1,1,mpimos_command_interpreter
	write_element_value		1,2,2
	get_list_val_var		4,2,1,1
	create_goal		4
	set_value		1,6
	set_value		2,8
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,s_command_analyzer_4_0
	put_value		1,5
	put_value		2,7
	put_value		3,9
	execute		3,trans_element_3_0
s_command_analyzer_4_1:
	otherwise		s_command_analyzer_4_0
	put_func		5,5,unit
	write_element_variable		5,1,6
	write_element_value		5,2,3
	write_element_void		5,3
	write_element_void		5,4
	put_func		3,3,:
	write_element_atom		3,1,mpimos_command_interpreter
	write_element_value		3,2,5
	put_list		5
	write_car_value		5,3
	write_cdr_nil		5
	get_list_value		4,5
	put_value		3,6
	execute		3,trans_element_3_0
s_command_analyzer_4_6:
	suspend		s_command_analyzer_4_0
	module_entry		mpimos_command_interpreter
	predicate		trans_element,3
trans_element_3_0:
	try_me_else		trans_element_3_1
	wait_vector		1,3
	read_element		1,0,4
	wait_atom		4,:
	read_elements_inc		1,1,4,2
	put_reused_func		1,1,:
	write_elements_inc		1,1,4,2
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	get_list_value		3,4
	get_nil		2
	proceed
trans_element_3_1:
	otherwise		trans_element_3_0
	put_value		7,1
	put_func		1,3,getenv
	write_element_atom		1,1,modules
	write_element_marked_variable		1,2,5
	get_list_val_var		2,4,1,1
	create_goal		6
	set_variable		1,4
	set_variable		2,6
	set_marked_value		3,7
	set_value		4,1
	set_value		5,3
	set_value		6,5
	enqueue_goal		6,trans_element1_6_0
	put_list		1
	write_car_atom		1,mpimos_cmd_environment
	write_cdr_value		1,5
	put_values_dec		2,7,2
	execute		4,is_command_4_0
trans_element_3_6:
	suspend		trans_element_3_0
	module_entry		mpimos_command_interpreter
	predicate		trans_element1,6
trans_element1_6_0:
	try_me_else		trans_element1_6_1
	atom		1
	branch_on_atom		1,2,trans_element1_6_1
	bucket_entry_a		abort,trans_element1_6_3
	bucket_entry_a		true,trans_element1_6_4
trans_element1_6_3:
	collect_value		3
	collect_value		2
	get_nil		5
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_func		2,2,putt
	write_element_value		2,1,6
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_85'
	put_list_val_val		2,1,3
	put_structured_constant		1,'$SCNST_86'
	put_list_val_val		3,1,2
	put_func		1,2,window
	write_element_value		1,1,3
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		4,2
	put_value		1,5
	put_atom		2,fail
	execute		2,error_action_2_0
trans_element1_6_4:
	collect_value		6
	put_func		1,3,do_command
	write_elements_inc		1,1,3,2
	put_func		3,3,:
	write_elements_dec		3,1,2,2
	put_list		1
	write_car_value		1,3
	write_cdr_nil		1
	get_list_value		5,1
	proceed
trans_element1_6_1:
	otherwise		trans_element1_6_0
	try_me_else		trans_element1_6_7
	wait_vector		3,3
	read_element		3,0,7
	atom		7
	branch_on_atom		7,2,trans_element1_6_7
	bucket_entry_a		',',trans_element1_6_10
	bucket_entry_a		;,trans_element1_6_11
trans_element1_6_10:
	read_elements_inc		3,1,8,2
	collect_value		6
	collect_value		2
	collect_value		1
	put_reused_func		1,3,','
	write_elements_inc		1,1,8,2
	put_values_inc		2,4,2
	execute		3,command_analyzer_3_0
trans_element1_6_11:
	read_elements_inc		3,1,8,2
	collect_value		6
	collect_value		2
	collect_value		1
	put_reused_func		1,3,;
	write_elements_inc		1,1,8,2
	put_values_inc		2,4,2
	execute		3,command_analyzer_3_0
trans_element1_6_7:
	otherwise		trans_element1_6_0
	collect_value		6
	collect_value		2
	collect_value		1
	get_nil		5
	create_goal		2
	set_variable		1,2
	set_atom		2,fail
	enqueue_goal		2,error_action_2_0
	create_goal		3
	set_variable		1,5
	set_value		2,4
	put_func		1,2,flush
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal		3,unknown_command_3_0
	put_value		1,3
	put_value		2,5
	execute_external		mpimos_utility,freeze,2
trans_element1_6_17:
	suspend		trans_element1_6_0
	module_entry		mpimos_command_interpreter
	predicate		error_action,2
error_action_2_0:
	try_me_else		error_action_2_1
	wait		1
	put_integer		3,131072
	put_func		1,2,shell
	write_element_value		1,1,2
	put_void		2
	b_raise		3,1,2
	proceed
error_action_2_1:
	suspend		error_action_2_0
	module_entry		mpimos_command_interpreter
	predicate		unknown_command,3
unknown_command_3_0:
	try_me_else		unknown_command_3_1
	wait		1
	put_structured_constant		4,'$SCNST_87'
	put_func		5,2,putt
	write_element_value		5,1,1
	put_list_val_val		1,5,4
	put_structured_constant		4,'$SCNST_88'
	put_list_val_val		5,4,1
	put_func		1,2,window
	write_element_value		1,1,5
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
unknown_command_3_1:
	suspend		unknown_command_3_0
	module_entry		mpimos_command_interpreter
	predicate		is_command,4
is_command_4_0:
	try_me_else		is_command_4_1
	jump_on_non_list_var_var		1,is_command_4_3,5,6
	collect_list		1
	put_values_inc		7,2,3
	put_vector		1,3
	write_element_marked_value		1,0,5
	write_element_atom		1,1,is_command
	write_element_integer		1,2,2
	put_vector		2,2
	write_element_marked_value		2,0,7
	write_element_variable		2,1,3
	b_apply		1,2
	put_value		1,3
	put_values_inc		2,6,2
	put_value		4,5
	put_values_inc		5,8,2
	execute		6,is_command0_6_0
is_command_4_3:
	check_nil		1,is_command_4_1
	collect_value		3
	collect_value		2
	get_atom		4,fail
	proceed
is_command_4_1:
	otherwise		is_command_4_0
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		4,abort
	proceed
is_command_4_8:
	suspend		is_command_4_0
	module_entry		mpimos_command_interpreter
	predicate		is_command0,6
is_command0_6_0:
	try_me_else		is_command0_6_1
	atom		1
	branch_on_atom		1,2,is_command0_6_1
	bucket_entry_a		no,is_command0_6_3
	bucket_entry_a		yes,is_command0_6_4
is_command0_6_3:
	collect_value		4
	put_values_inc		1,2,2
	put_values_inc		3,5,2
	execute		4,is_command_4_0
is_command0_6_4:
	collect_value		3
	collect_value		2
	get_value		5,4
	get_atom		6,true
	proceed
is_command0_6_1:
	suspend		is_command0_6_0
	module_entry		mpimos_command_interpreter
	predicate		valve,3
valve_3_0:
	try_me_else		valve_3_1
	wait		1
	collect_value		2
	get_nil		3
	proceed
valve_3_1:
	try_me_else		valve_3_4
	jump_on_non_list_var_var		2,valve_3_6,4,5
	get_reused_list_val_var		3,2,2,4,4
	put_values_dec		2,5,2
	execute		3,valve_3_0
valve_3_6:
	check_nil		2,valve_3_4
	collect_value		1
	get_nil		3
	proceed
valve_3_4:
	suspend		valve_3_0
	module_entry		mpimos_command_interpreter
	predicate		resource_manager,6
resource_manager_6_0:
	create_goal		8
	set_values_inc		1,1,5
	set_variable		6,2
	set_variable		7,1
	set_value		8,6
	enqueue_goal		8,resource_manager0_8_0
	create_goal		1
	set_value		1,2
	enqueue_goal_external		mpimos_macro_expander,create,1
	execute		1,make_table_1_0
resource_manager_6_1:
	suspend		resource_manager_6_0
	module_entry		mpimos_command_interpreter
	predicate		resource_manager0,8
resource_manager0_8_0:
	try_me_else		resource_manager0_8_1
	list		1
	read_car		1,9
	jump_on_non_atom		9,resource_manager0_8_4
	test_atom		9,initenv,resource_manager0_8_1
	read_cdr		1,10
	put_func		9,3,backtrace
	write_element_marked_variable		9,1,12
	write_element_variable		9,2,14
	put_reused_list_val_var		1,1,9,13
	put_func		9,3,debug
	write_element_marked_variable		9,1,11
	write_element_variable		9,2,15
	put_list_val_val		16,9,1
	get_list_value		4,16
	create_goal		8
	set_value		1,10
	set_variable		2,4
	set_value		3,3
	set_value		4,13
	set_values_inc		5,5,2
	set_variable		7,5
	set_value		8,8
	enqueue_goal		8,resource_manager0_8_0
	create_goal		5
	set_variable		1,9
	set_marked_variable		2,3
	put_structured_constant		1,'$SCNST_89'
	set_value		3,1
	set_variable		4,1
	set_value		5,4
	enqueue_goal		5,check_env_5_0
	create_goal		5
	set_variable		1,6
	set_marked_variable		2,4
	put_structured_constant		8,'$SCNST_90'
	set_value		3,8
	set_variable		4,13
	set_value		5,1
	enqueue_goal		5,check_env_5_0
	create_goal		5
	set_variable		1,8
	set_marked_variable		2,1
	put_structured_constant		10,'$SCNST_91'
	set_value		3,10
	set_variable		4,10
	set_value		5,13
	enqueue_goal		5,check_env_5_0
	create_goal		5
	set_value		1,14
	set_value		2,12
	put_structured_constant		13,'$SCNST_92'
	set_value		3,13
	set_variable		4,13
	set_value		5,10
	enqueue_goal		5,check_env_5_0
	create_goal		5
	set_value		1,15
	set_value		2,11
	put_structured_constant		10,'$SCNST_93'
	set_value		3,10
	set_variable		4,10
	set_value		5,13
	enqueue_goal		5,check_env_5_0
	create_goal		4
	set_value		1,3
	set_value		2,9
	set_variable		3,9
	set_value		4,10
	enqueue_goal		4,set_print_var_mode_4_0
	create_goal		4
	set_value		1,4
	set_value		2,6
	set_variable		3,6
	set_value		4,9
	enqueue_goal		4,set_print_depth_4_0
	create_goal		4
	set_value		1,1
	set_value		2,8
	set_value		3,2
	set_value		4,6
	enqueue_goal		4,set_print_length_4_0
	create_goal		4
	set_atom		1,pvar
	set_value		2,3
	set_variable		3,3
	set_value		4,5
	enqueue_goal		4,getenv_4_0
	create_goal		4
	set_atom		1,pdepth
	set_value		2,4
	set_variable		3,2
	set_value		4,3
	enqueue_goal		4,getenv_4_0
	create_goal		4
	set_atom		1,plength
	set_value		2,1
	set_variable		3,1
	set_value		4,2
	enqueue_goal		4,getenv_4_0
	create_goal		4
	set_atom		1,backtrace
	set_value		2,12
	set_variable		3,4
	set_value		4,1
	enqueue_goal		4,getenv_4_0
	put_atom		1,trace
	put_value		2,11
	put_value		3,7
	execute		4,getenv_4_0
resource_manager0_8_4:
	is_vector		9,resource_manager0_8_1
	jump_on_arity		9,4,resource_manager0_8_1
	table_entry		resource_manager0_8_1
	table_entry		resource_manager0_8_1
	table_entry		resource_manager0_8_5
	table_entry		resource_manager0_8_6
resource_manager0_8_5:
	read_element		9,0,10
	atom		10
	hash_on_atom		10,9,resource_manager0_8_1
	bucket_entry_a		code,resource_manager0_8_8
	bucket_entry_a		directory,resource_manager0_8_9
	bucket_entry_a		getenv,resource_manager0_8_10
	bucket_entry_a		getuc,resource_manager0_8_11
	bucket_entry_a		interrupt,resource_manager0_8_12
	bucket_entry_a		macro_expander,resource_manager0_8_13
	bucket_entry_a		system,resource_manager0_8_14
	bucket_entry_a		system_stream,resource_manager0_8_15
	bucket_entry_a		window,resource_manager0_8_16
resource_manager0_8_8:
	read_cdr		1,11
	read_element		9,1,12
	collect_vector		9
	get_reused_list_val_var		4,1,1,12,9
	put_value		1,11
	put_value		4,9
	execute		8,resource_manager0_8_0
resource_manager0_8_9:
	read_cdr		1,11
	read_element		9,1,12
	put_reused_func		9,9,do
	write_element_value		9,1,12
	get_reused_list_val_var		5,1,1,9,9
	put_value		1,11
	put_value		5,9
	execute		8,resource_manager0_8_0
resource_manager0_8_10:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	create_goal		8
	set_value		1,11
	set_values_inc		2,2,7
	enqueue_goal		8,resource_manager0_8_0
	put_value		1,12
	execute		1,all_env_1_0
resource_manager0_8_11:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	put_marked_value		1,12
	b_increment		1,1
	create_goal		8
	set_value		1,11
	set_variable		2,9
	set_values_inc		3,3,4
	set_variable		7,3
	set_value		8,8
	enqueue_goal		8,resource_manager0_8_0
	create_goal		4
	set_atom		1,ucounter
	set_value		2,1
	set_variable		3,4
	set_value		4,3
	enqueue_goal		4,setenv_4_0
	create_goal		4
	set_variable		1,3
	set_value		2,12
	set_value		3,2
	set_value		4,9
	enqueue_goal		4,check_num_4_0
	put_atom		1,ucounter
	put_value		2,3
	put_value		3,7
	execute		4,getenv_4_0
resource_manager0_8_12:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	collect_vector		9
	put_marked_value		8,8
	get_value		8,12
	put_value		1,11
	execute		8,resource_manager0_8_0
resource_manager0_8_13:
	read_cdr		1,11
	read_element		9,1,12
	collect_vector		9
	get_reused_list_val_var		6,1,1,12,9
	put_value		1,11
	put_value		6,9
	execute		8,resource_manager0_8_0
resource_manager0_8_14:
	read_cdr		1,11
	read_element		9,1,12
	collect_vector		9
	get_reused_list_val_var		3,1,1,12,9
	put_value		1,11
	put_value		3,9
	execute		8,resource_manager0_8_0
resource_manager0_8_15:
	read_cdr		1,11
	read_element		9,1,12
	collect_list		1
	put_reused_vector		1,9
	write_element_value		1,0,12
	write_element_variable		1,1,9
	get_vector_value		3,1
	put_value		1,11
	put_value		3,9
	execute		8,resource_manager0_8_0
resource_manager0_8_16:
	read_cdr		1,11
	read_element		9,1,12
	put_reused_func		9,9,do
	write_element_value		9,1,12
	get_reused_list_val_var		2,1,1,9,9
	put_value		1,11
	put_value		2,9
	execute		8,resource_manager0_8_0
resource_manager0_8_6:
	read_element		9,0,10
	atom		10
	branch_on_atom		10,2,resource_manager0_8_1
	bucket_entry_a		getenv,resource_manager0_8_18
	bucket_entry_a		setenv,resource_manager0_8_19
resource_manager0_8_18:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	create_goal		8
	set_value		1,11
	set_values_inc		2,2,5
	set_variable		7,4
	set_value		8,8
	enqueue_goal		8,resource_manager0_8_0
	put_values_inc		1,12,2
	put_value		3,7
	execute		4,getenv_4_0
resource_manager0_8_19:
	read_cdr		1,11
	read_elements_inc		9,1,12,2
	collect_list		1
	collect_vector		9
	create_goal		8
	set_value		1,11
	set_values_inc		2,2,5
	set_variable		7,4
	set_value		8,8
	enqueue_goal		8,resource_manager0_8_0
	put_values_inc		1,12,2
	put_value		3,7
	execute		4,setenv_4_0
resource_manager0_8_1:
	suspend		resource_manager0_8_0
	module_entry		mpimos_command_interpreter
	predicate		make_table,1
make_table_1_0:
	put_variable		3,2
	b_new_vector		3,3
	get_value		3,1
	put_atom		1,max
	execute		2,env_table_2_0
make_table_1_1:
	suspend		make_table_1_0
	module_entry		mpimos_command_interpreter
	predicate		getenv,4
getenv_4_0:
	put_variable		6,5
	b_vector_element		3,6,3,6
	get_value		3,2
	get_value		6,4
	put_value		2,5
	execute		2,env_table_2_0
getenv_4_1:
	suspend		getenv_4_0
	module_entry		mpimos_command_interpreter
	predicate		setenv,4
setenv_4_0:
	put_variable		6,5
	b_set_vector_element		3,6,2,2,3
	get_value		3,4
	put_value		2,5
	execute		2,env_table_2_0
setenv_4_1:
	suspend		setenv_4_0
	module_entry		mpimos_command_interpreter
	predicate		env_table,2
env_table_2_0:
	try_me_else		env_table_2_1
	atom		1
	hash_on_atom		1,13,env_table_2_1
	bucket_entry_a		auto_load,env_table_2_3
	bucket_entry_a		backtrace,env_table_2_4
	bucket_entry_a		loaddir,env_table_2_5
	bucket_entry_a		max,env_table_2_6
	bucket_entry_a		modules,env_table_2_7
	bucket_entry_a		pdepth,env_table_2_8
	bucket_entry_a		plength,env_table_2_9
	bucket_entry_a		pvar,env_table_2_10
	bucket_entry_a		reduction,env_table_2_11
	bucket_entry_a		savedir,env_table_2_12
	bucket_entry_a		trace,env_table_2_13
	bucket_entry_a		ucounter,env_table_2_14
	bucket_entry_a		world,env_table_2_15
env_table_2_3:
	get_integer		2,8
	proceed
env_table_2_4:
	get_integer		2,2
	proceed
env_table_2_5:
	get_integer		2,7
	proceed
env_table_2_6:
	get_integer		2,12
	proceed
env_table_2_7:
	get_integer		2,3
	proceed
env_table_2_8:
	get_integer		2,10
	proceed
env_table_2_9:
	get_integer		2,9
	proceed
env_table_2_10:
	get_integer		2,11
	proceed
env_table_2_11:
	get_integer		2,4
	proceed
env_table_2_12:
	get_integer		2,6
	proceed
env_table_2_13:
	get_integer		2,1
	proceed
env_table_2_14:
	get_integer		2,5
	proceed
env_table_2_15:
	get_integer		2,0
	proceed
env_table_2_1:
	suspend		env_table_2_0
	module_entry		mpimos_command_interpreter
	predicate		all_env,1
all_env_1_0:
	put_structured_constant		2,'$SCNST_94'
	get_value		1,2
	proceed
all_env_1_1:
	suspend		all_env_1_0
	module_entry		mpimos_command_interpreter
	predicate		check_env,5
check_env_5_0:
	try_me_else		check_env_5_1
	wait_atom		1,success
	collect_value		3
	collect_value		2
	get_value		4,5
	proceed
check_env_5_1:
	otherwise		check_env_5_0
	collect_value		1
	put_func		1,2,flush
	write_element_void		1,1
	put_list_val_val		6,1,5
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,6
	put_func		5,2,putt
	write_element_value		5,1,2
	put_list_val_val		2,5,1
	put_structured_constant		1,'$SCNST_95'
	put_list_val_val		5,1,2
	put_func		1,2,putb
	write_element_value		1,1,3
	put_list_val_val		2,1,5
	put_structured_constant		1,'$SCNST_96'
	put_list_val_val		3,1,2
	get_list_value		4,3
	proceed
check_env_5_6:
	suspend		check_env_5_0
	module_entry		mpimos_command_interpreter
	predicate		check_num,4
check_num_4_0:
	try_me_else		check_num_4_1
	integer		1
	get_value		2,1
	get_value		3,4
	proceed
check_num_4_1:
	otherwise		check_num_4_0
	get_cpu_time		5
	put_value		6,1
	put_values_inc		7,3,2
	get_value		2,5
	put_atom		1,fail
	put_value		2,6
	put_structured_constant		3,'$SCNST_97'
	put_values_inc		4,7,2
	execute		5,check_env_5_0
check_num_4_5:
	suspend		check_num_4_0
	module_entry		mpimos_command_interpreter
	predicate		set_print_length,4
set_print_length_4_0:
	try_me_else		set_print_length_4_1
	integer		1
	put_integer		5,1
	g_not_less_than		1,5
	put_func		5,2,print_length
	write_element_value		5,1,1
	put_list_val_val		1,5,4
	get_list_value		3,1
	get_atom		2,success
	proceed
set_print_length_4_1:
	otherwise		set_print_length_4_0
	collect_value		1
	get_value		3,4
	get_atom		2,fail
	proceed
set_print_length_4_5:
	suspend		set_print_length_4_0
	module_entry		mpimos_command_interpreter
	predicate		set_print_depth,4
set_print_depth_4_0:
	try_me_else		set_print_depth_4_1
	integer		1
	put_integer		5,1
	g_not_less_than		1,5
	put_func		5,2,print_depth
	write_element_value		5,1,1
	put_list_val_val		1,5,4
	get_list_value		3,1
	get_atom		2,success
	proceed
set_print_depth_4_1:
	otherwise		set_print_depth_4_0
	collect_value		1
	get_value		3,4
	get_atom		2,fail
	proceed
set_print_depth_4_5:
	suspend		set_print_depth_4_0
	module_entry		mpimos_command_interpreter
	predicate		set_print_var_mode,4
set_print_var_mode_4_0:
	try_me_else		set_print_var_mode_4_1
	atom		1
	branch_on_atom		1,2,set_print_var_mode_4_1
	bucket_entry_a		na,set_print_var_mode_4_3
	bucket_entry_a		nu,set_print_var_mode_4_4
set_print_var_mode_4_3:
	put_structured_constant		1,'$SCNST_98'
	put_list_val_val		5,1,4
	get_list_value		3,5
	get_atom		2,success
	proceed
set_print_var_mode_4_4:
	put_structured_constant		1,'$SCNST_99'
	put_list_val_val		5,1,4
	get_list_value		3,5
	get_atom		2,success
	proceed
set_print_var_mode_4_1:
	otherwise		set_print_var_mode_4_0
	collect_value		1
	get_value		3,4
	get_atom		2,fail
	proceed
set_print_var_mode_4_7:
	suspend		set_print_var_mode_4_0
	module_entry		mpimos_command_interpreter
	predicate		'$mpimos_window:os_create/6',6
'$mpimos_window:os_create/6_6_0':
	execute_external		mpimos_window,os_create,6
'$mpimos_window:os_create/6_6_1':
	suspend		'$mpimos_window:os_create/6_6_0'
	module_entry		mpimos_command_interpreter
	predicate		'$mpimos_code_manager:os_get_command_stream/3',3
'$mpimos_code_manager:os_get_command_stream/3_3_0':
	execute_external		mpimos_code_manager,os_get_command_stream,3
'$mpimos_code_manager:os_get_command_stream/3_3_1':
	suspend		'$mpimos_code_manager:os_get_command_stream/3_3_0'
	module_entry		mpimos_command_interpreter
	predicate		'$mpimos_directory:os_create/6',6
'$mpimos_directory:os_create/6_6_0':
	execute_external		mpimos_directory,os_create,6
'$mpimos_directory:os_create/6_6_1':
	suspend		'$mpimos_directory:os_create/6_6_0'
	module_entry		mpimos_command_interpreter
	predicate		'$mpimos_task_monitor:create/12',12
'$mpimos_task_monitor:create/12_12_0':
	execute_external		mpimos_task_monitor,create,12
'$mpimos_task_monitor:create/12_12_1':
	suspend		'$mpimos_task_monitor:create/12_12_0'
	begin_const_section		mpimos_command_interpreter
'$SCNST_0_0':
	define_desc		27,1
	define_integer		46
'$SCNST_16':
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		27,2
	define_integer		1279608915
	define_integer		76
'$SCNST_17':
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		27,2
	define_integer		759111804
	define_integer		32
'$SCNST_2':
	define_string		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		11,11
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		707406378
	define_integer		2763306
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_3_1'
'$SCNST_11':
'$SCNST_9':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		19,2
	define_integer		1954112032
	define_integer		29541
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		11,5
	define_integer		1635020628
	define_integer		1868767340
	define_integer		1931502948
	define_integer		543521385
	define_integer		2126697
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		19,2
	define_integer		1919907616
	define_integer		29540
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		11,5
	define_integer		1635020628
	define_integer		1701322860
	define_integer		1931505761
	define_integer		543521385
	define_integer		2126697
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		27,3
	define_integer		1819438935
	define_integer		1936269412
	define_integer		32
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_10_1':
	define_desc		11,11
	define_integer		707406378
	define_integer		1667845408
	define_integer		1344302962
	define_integer		1397706057
	define_integer		1702242336
	define_integer		1869181810
	define_integer		775037038
	define_integer		706750773
	define_integer		707406378
	define_integer		707406378
	define_integer		2763306
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_12_0':
	define_desc		27,3
	define_integer		1882075006
	define_integer		1920168804
	define_integer		99
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_13_0':
	define_desc		11,8
	define_integer		661545283
	define_integer		1667309684
	define_integer		1936942435
	define_integer		1717920800
	define_integer		1953264993
	define_integer		1919509536
	define_integer		1869898597
	define_integer		3045746
'$SCNST_13':
	define_string		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		19,7
	define_integer		1918989395
	define_integer		544241012
	define_integer		1701603686
	define_integer		1702389024
	define_integer		1769239907
	define_integer		773875566
	define_integer		11822
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_2':
	define_atom		mpimos_cmd_environment
	define_atom		[]
'$SCNST_15_1':
	define_atom		mpimos_cmd_code
	define_list		'$SCNST_15_2'
'$SCNST_15_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		modules
	define_list		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_18_0':
	define_desc		19,3
	define_integer		1650811951
	define_integer		1969186677
	define_integer		27764
'$SCNST_18':
	define_string		'$SCNST_18_0'
'$SCNST_19_0':
	define_desc		19,3
	define_integer		1835626543
	define_integer		1969189743
	define_integer		27764
'$SCNST_19':
	define_string		'$SCNST_19_0'
'$SCNST_20_6':
	define_atom		mpimos_cmd_environment
	define_atom		[]
'$SCNST_20_5':
	define_atom		mpimos_cmd_debug
	define_list		'$SCNST_20_6'
'$SCNST_20_4':
	define_atom		mpimos_cmd_directory
	define_list		'$SCNST_20_5'
'$SCNST_20_3':
	define_atom		mpimos_cmd_code
	define_list		'$SCNST_20_4'
'$SCNST_20_2':
	define_atom		mpimos_cmd_basic
	define_list		'$SCNST_20_3'
'$SCNST_20_1':
	define_atom		mpimos_builtin_predicate
	define_list		'$SCNST_20_2'
'$SCNST_20_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		modules
	define_list		'$SCNST_20_1'
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		auto_load
	define_atom		yes
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		11,3
	define_integer		1345204094
	define_integer		1934840644
	define_integer		6649441
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_23_1':
	define_desc		11,3
	define_integer		1345204094
	define_integer		1934840644
	define_integer		6649441
'$SCNST_23_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		savedir
	define_string		'$SCNST_23_1'
'$SCNST_23':
	define_vector		'$SCNST_23_0'
'$SCNST_24_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		pvar
	define_atom		nu
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_25_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		pdepth
	define_integer		5
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_26_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		plength
	define_integer		20
'$SCNST_26':
	define_vector		'$SCNST_26_0'
'$SCNST_27_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		ucounter
	define_integer		0
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_28_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		reduction
	define_integer		10000
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_29_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		backtrace
	define_atom		on
'$SCNST_29':
	define_vector		'$SCNST_29_0'
'$SCNST_30_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		trace
	define_atom		off
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_31_0':
	define_desc		0,3
	define_atom		setenv
	define_atom		ucounter
	define_integer		1
'$SCNST_31':
	define_vector		'$SCNST_31_0'
'$SCNST_32_1':
	define_desc		3,3
	define_integer		1969513842
	define_integer		1869182051
	define_integer		540876910
'$SCNST_32_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_32_1'
'$SCNST_32':
	define_vector		'$SCNST_32_0'
'$SCNST_33_1':
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
'$SCNST_33_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_33_1'
'$SCNST_96':
'$SCNST_33':
	define_vector		'$SCNST_33_0'
'$SCNST_34_0':
	define_desc		0,2
	define_atom		more_reduction
	define_integer		10000
'$SCNST_73':
'$SCNST_34':
	define_vector		'$SCNST_34_0'
'$SCNST_35_0':
	define_atom		remove
	define_atom		[]
'$SCNST_84':
'$SCNST_82':
'$SCNST_80':
'$SCNST_78':
'$SCNST_54':
'$SCNST_47':
'$SCNST_45':
'$SCNST_35':
	define_list		'$SCNST_35_0'
'$SCNST_36_2':
	define_desc		11,4
	define_integer		1935767328
	define_integer		1868718368
	define_integer		1684370546
	define_integer		2171168
'$SCNST_36_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_36_2'
'$SCNST_36_3':
	define_atom		nl
	define_atom		[]
'$SCNST_36_0':
	define_vector		'$SCNST_36_1'
	define_list		'$SCNST_36_3'
'$SCNST_36':
	define_list		'$SCNST_36_0'
'$SCNST_37_1':
	define_desc		27,1
	define_integer		47
'$SCNST_37_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_37_1'
'$SCNST_67':
'$SCNST_63':
'$SCNST_37':
	define_vector		'$SCNST_37_0'
'$SCNST_38_1':
	define_desc		27,2
	define_integer		1802723668
	define_integer		32
'$SCNST_38_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_38_1'
'$SCNST_68':
'$SCNST_64':
'$SCNST_60':
'$SCNST_57':
'$SCNST_52':
'$SCNST_41':
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_39_1':
	define_desc		11,5
	define_integer		1684369952
	define_integer		1769235317
	define_integer		544435823
	define_integer		1713401715
	define_integer		3043937
'$SCNST_39_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_39_1'
'$SCNST_39':
	define_vector		'$SCNST_39_0'
'$SCNST_40_1':
	define_desc		19,1
	define_integer		8250
'$SCNST_40_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_40_1'
'$SCNST_40':
	define_vector		'$SCNST_40_0'
'$SCNST_42_1':
	define_desc		11,7
	define_integer		1919902273
	define_integer		677668212
	define_integer		1701869940
	define_integer		1413829152
	define_integer		542003797
	define_integer		695821675
	define_integer		2113312
'$SCNST_42_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_42_1'
'$SCNST_53':
'$SCNST_42':
	define_vector		'$SCNST_42_0'
'$SCNST_43_0':
	define_desc		11,7
	define_integer		1953394499
	define_integer		1702194793
	define_integer		544370464
	define_integer		1919902273
	define_integer		1663574132
	define_integer		539582767
	define_integer		2108735
'$SCNST_48':
'$SCNST_43':
	define_string		'$SCNST_43_0'
'$SCNST_44_3':
	define_desc		19,2
	define_integer		1701736292
	define_integer		8238
'$SCNST_44_2':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_44_3'
'$SCNST_44_7':
	define_desc		11,1
	define_integer		3043182
'$SCNST_44_6':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_44_7'
'$SCNST_44_5':
	define_vector		'$SCNST_44_6'
	define_atom		[]
'$SCNST_44_4':
	define_atom		nl
	define_list		'$SCNST_44_5'
'$SCNST_44_1':
	define_vector		'$SCNST_44_2'
	define_list		'$SCNST_44_4'
'$SCNST_44_0':
	define_desc		0,2
	define_atom		do
	define_list		'$SCNST_44_1'
'$SCNST_44':
	define_vector		'$SCNST_44_0'
'$SCNST_46_4':
	define_desc		3,1
	define_integer		779314553
'$SCNST_46_3':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_46_4'
'$SCNST_46_2':
	define_vector		'$SCNST_46_3'
	define_atom		[]
'$SCNST_46_1':
	define_atom		nl
	define_list		'$SCNST_46_2'
'$SCNST_46_0':
	define_desc		0,2
	define_atom		do
	define_list		'$SCNST_46_1'
'$SCNST_46':
	define_vector		'$SCNST_46_0'
'$SCNST_49_1':
	define_desc		19,9
	define_integer		1936287828
	define_integer		1935766560
	define_integer		1701978219
	define_integer		1701340001
	define_integer		1701978212
	define_integer		1952675172
	define_integer		544108393
	define_integer		1768778092
	define_integer		11892
'$SCNST_49_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_49_1'
'$SCNST_49':
	define_vector		'$SCNST_49_0'
'$SCNST_50_1':
	define_desc		11,5
	define_integer		1684369952
	define_integer		1769235317
	define_integer		544435823
	define_integer		1713401715
	define_integer		3043937
'$SCNST_50_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_50_1'
'$SCNST_50':
	define_vector		'$SCNST_50_0'
'$SCNST_51_1':
	define_desc		27,2
	define_integer		1935767328
	define_integer		32
'$SCNST_51_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_51_1'
'$SCNST_51':
	define_vector		'$SCNST_51_0'
'$SCNST_55_1':
	define_desc		11,6
	define_integer		1701080661
	define_integer		1701734758
	define_integer		1634869348
	define_integer		543519593
	define_integer		1701869940
	define_integer		2112032
'$SCNST_55_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_55_1'
'$SCNST_55':
	define_vector		'$SCNST_55_0'
'$SCNST_56_2':
	define_desc		11,4
	define_integer		1935767328
	define_integer		1868718368
	define_integer		1684370546
	define_integer		2171168
'$SCNST_56_1':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_56_2'
'$SCNST_56_0':
	define_vector		'$SCNST_56_1'
	define_atom		[]
'$SCNST_66':
'$SCNST_62':
'$SCNST_59':
'$SCNST_56':
	define_list		'$SCNST_56_0'
'$SCNST_58_1':
	define_atom		remove
	define_atom		[]
'$SCNST_58_0':
	define_atom		abort
	define_list		'$SCNST_58_1'
'$SCNST_69':
'$SCNST_65':
'$SCNST_61':
'$SCNST_58':
	define_list		'$SCNST_58_0'
'$SCNST_70_4':
	define_desc		11,1
	define_integer		3043182
'$SCNST_70_3':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_70_4'
'$SCNST_70_2':
	define_vector		'$SCNST_70_3'
	define_atom		[]
'$SCNST_70_1':
	define_atom		nl
	define_list		'$SCNST_70_2'
'$SCNST_70_0':
	define_desc		0,2
	define_atom		do
	define_list		'$SCNST_70_1'
'$SCNST_70':
	define_vector		'$SCNST_70_0'
'$SCNST_71_1':
	define_desc		19,5
	define_integer		540818492
	define_integer		1702127201
	define_integer		1633886322
	define_integer		1042310514
	define_integer		15934
'$SCNST_71_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_71_1'
'$SCNST_71':
	define_vector		'$SCNST_71_0'
'$SCNST_72_0':
	define_desc		19,3
	define_integer		1702127169
	define_integer		1633902450
	define_integer		25970
'$SCNST_74':
'$SCNST_72':
	define_string		'$SCNST_72_0'
'$SCNST_75_0':
	define_desc		27,2
	define_integer		1802723700
	define_integer		95
'$SCNST_75':
	define_string		'$SCNST_75_0'
'$SCNST_76_0':
	define_desc		0,2
	define_atom		more_reduction
	define_integer		1000000
'$SCNST_79':
'$SCNST_76':
	define_vector		'$SCNST_76_0'
'$SCNST_77_0':
	define_desc		0,2
	define_atom		shell
	define_atom		aborted
'$SCNST_81':
'$SCNST_77':
	define_vector		'$SCNST_77_0'
'$SCNST_83_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_83':
	define_vector		'$SCNST_83_0'
'$SCNST_85_1':
	define_desc		19,4
	define_integer		1869429820
	define_integer		1701606756
	define_integer		540950131
	define_integer		8253
'$SCNST_85_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_85_1'
'$SCNST_85':
	define_vector		'$SCNST_85_0'
'$SCNST_86_1':
	define_desc		11,10
	define_integer		1769369157
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		544434464
	define_integer		1701604457
	define_integer		543973735
	define_integer		1701869940
	define_integer		2171168
'$SCNST_86_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_86_1'
'$SCNST_86':
	define_vector		'$SCNST_86_0'
'$SCNST_87_0':
	define_atom		nl
	define_atom		[]
'$SCNST_87':
	define_list		'$SCNST_87_0'
'$SCNST_88_1':
	define_desc		3,5
	define_integer		1852534357
	define_integer		544110447
	define_integer		1835888483
	define_integer		543452769
	define_integer		540686906
'$SCNST_88_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_88_1'
'$SCNST_88':
	define_vector		'$SCNST_88_0'
'$SCNST_89_0':
	define_desc		3,1
	define_integer		1918989936
'$SCNST_89':
	define_string		'$SCNST_89_0'
'$SCNST_90_0':
	define_desc		19,2
	define_integer		1885693040
	define_integer		26740
'$SCNST_90':
	define_string		'$SCNST_90_0'
'$SCNST_91_0':
	define_desc		11,2
	define_integer		1852140656
	define_integer		6845543
'$SCNST_91':
	define_string		'$SCNST_91_0'
'$SCNST_92_0':
	define_desc		27,3
	define_integer		1801675106
	define_integer		1667330676
	define_integer		101
'$SCNST_92':
	define_string		'$SCNST_92_0'
'$SCNST_93_0':
	define_desc		27,2
	define_integer		1667330676
	define_integer		101
'$SCNST_93':
	define_string		'$SCNST_93_0'
'$SCNST_94_11':
	define_atom		pvar
	define_atom		[]
'$SCNST_94_10':
	define_atom		pdepth
	define_list		'$SCNST_94_11'
'$SCNST_94_9':
	define_atom		plength
	define_list		'$SCNST_94_10'
'$SCNST_94_8':
	define_atom		auto_load
	define_list		'$SCNST_94_9'
'$SCNST_94_7':
	define_atom		loaddir
	define_list		'$SCNST_94_8'
'$SCNST_94_6':
	define_atom		savedir
	define_list		'$SCNST_94_7'
'$SCNST_94_5':
	define_atom		ucounter
	define_list		'$SCNST_94_6'
'$SCNST_94_4':
	define_atom		reduction
	define_list		'$SCNST_94_5'
'$SCNST_94_3':
	define_atom		modules
	define_list		'$SCNST_94_4'
'$SCNST_94_2':
	define_atom		backtrace
	define_list		'$SCNST_94_3'
'$SCNST_94_1':
	define_atom		trace
	define_list		'$SCNST_94_2'
'$SCNST_94_0':
	define_atom		world
	define_list		'$SCNST_94_1'
'$SCNST_94':
	define_list		'$SCNST_94_0'
'$SCNST_95_1':
	define_desc		11,1
	define_integer		2112800
'$SCNST_95_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_95_1'
'$SCNST_95':
	define_vector		'$SCNST_95_0'
'$SCNST_97_0':
	define_desc		3,2
	define_integer		1970234229
	define_integer		1919251566
'$SCNST_97':
	define_string		'$SCNST_97_0'
'$SCNST_98_0':
	define_desc		0,2
	define_atom		print_var_mode
	define_atom		na
'$SCNST_98':
	define_vector		'$SCNST_98_0'
'$SCNST_99_0':
	define_desc		0,2
	define_atom		print_var_mode
	define_atom		nu
'$SCNST_99':
	define_vector		'$SCNST_99_0'
