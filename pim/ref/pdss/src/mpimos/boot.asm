mpimos_booter:
	module		mpimos_booter
	entry		start,0,start_0_0
	entry		kl1cmp_start,0,kl1cmp_start_0_0
	entry		process_name_list,2,process_name_list_2_0
	module_entry		mpimos_booter
	predicate		start,0
start_0_0:
	create_goal		4
	set_variable		1,2
	set_variable		2,3
	set_variable		3,4
	set_variable		4,5
	enqueue_goal		4,start_4_0
	put_integer		1,4040
	b_rate		1,1
	create_goal		1
	set_value		1,5
	enqueue_goal_with_priority		1,'$pdss_code_device:do/1_1_0',1
	put_integer		1,4040
	b_rate		1,1
	create_goal		1
	set_value		1,4
	enqueue_goal_with_priority		1,'$pdss_timer_device:timer/1_1_0',1
	put_integer		1,4040
	b_rate		1,1
	create_goal		1
	set_value		1,3
	enqueue_goal_with_priority		1,'$pdss_file_device:files/1_1_0',1
	put_integer		1,4080
	b_rate		1,1
	create_goal		1
	set_value		1,2
	enqueue_goal_with_priority		1,'$pdss_window_device:windows/1_1_0',1
	proceed
start_0_1:
	suspend		start_0_0
	module_entry		mpimos_booter
	predicate		start,4
start_4_0:
	b_merge		6,5
	put_vector		7,5
	write_element_variable		7,0,9
	write_element_variable		7,1,10
	write_element_variable		7,2,11
	write_element_variable		7,3,13
	write_element_variable		7,4,15
	get_vector_value		6,7
	put_integer		6,4040
	b_rate		6,6
	create_goal		2
	set_value		1,5
	put_func		5,2,code_manager
	write_element_variable		5,1,16
	put_list		7
	write_car_value		7,5
	write_cdr_nil		7
	put_func		5,2,timer_manager
	write_element_variable		5,1,14
	put_list_val_val		8,5,7
	put_func		5,2,file_manager
	write_element_variable		5,1,12
	put_list_val_val		7,5,8
	put_func		5,2,window_manager
	write_element_variable		5,1,8
	put_list_val_val		17,5,7
	set_value		2,17
	enqueue_goal_with_priority		2,distributor_2_0,6
	put_integer		5,4040
	b_rate		5,5
	create_goal		3
	set_value		1,16
	set_value		2,4
	set_value		3,15
	enqueue_goal_with_priority		3,'$mpimos_code_manager:create/3_3_0',5
	put_integer		4,4040
	b_rate		4,4
	create_goal		3
	set_value		1,14
	set_value		2,3
	set_value		3,13
	enqueue_goal_with_priority		3,'$mpimos_timer_manager:create/3_3_0',4
	put_integer		3,4040
	b_rate		3,3
	create_goal		3
	set_value		1,12
	set_value		2,2
	set_value		3,11
	enqueue_goal_with_priority		3,'$mpimos_file_manager:create/3_3_0',3
	put_integer		2,4084
	b_rate		2,2
	create_goal		3
	set_value		1,8
	set_value		2,1
	set_value		3,10
	enqueue_goal_with_priority		3,'$mpimos_window_manager:create/3_3_0',2
	put_integer		1,4088
	b_rate		1,1
	create_goal		1
	set_value		1,9
	enqueue_goal_with_priority		1,'$mpimos_command_interpreter:create/1_1_0',1
	proceed
start_4_1:
	suspend		start_4_0
	module_entry		mpimos_booter
	predicate		kl1cmp_start,0
kl1cmp_start_0_0:
	create_goal		3
	set_variable		1,2
	set_variable		2,3
	set_variable		3,4
	enqueue_goal		3,kl1cmp_start_3_0
	put_integer		1,4040
	b_rate		1,1
	create_goal		1
	set_value		1,4
	enqueue_goal_with_priority		1,'$pdss_code_device:do/1_1_0',1
	put_integer		1,4040
	b_rate		1,1
	create_goal		1
	set_value		1,3
	enqueue_goal_with_priority		1,'$pdss_file_device:files/1_1_0',1
	put_integer		1,4080
	b_rate		1,1
	create_goal		1
	set_value		1,2
	enqueue_goal_with_priority		1,'$pdss_window_device:windows/1_1_0',1
	proceed
kl1cmp_start_0_1:
	suspend		kl1cmp_start_0_0
	module_entry		mpimos_booter
	predicate		kl1cmp_start,3
kl1cmp_start_3_0:
	b_merge		5,4
	put_vector		6,4
	write_element_variable		6,0,8
	write_element_variable		6,1,9
	write_element_variable		6,2,10
	write_element_variable		6,3,12
	get_vector_value		5,6
	put_integer		5,4040
	b_rate		5,5
	create_goal		2
	set_value		1,4
	put_func		4,2,code_manager
	write_element_variable		4,1,13
	put_list		6
	write_car_value		6,4
	write_cdr_nil		6
	put_func		4,2,file_manager
	write_element_variable		4,1,11
	put_list_val_val		7,4,6
	put_func		4,2,window_manager
	write_element_variable		4,1,6
	put_list_val_val		14,4,7
	set_value		2,14
	enqueue_goal_with_priority		2,distributor_2_0,5
	put_integer		4,4040
	b_rate		4,4
	create_goal		3
	set_value		1,13
	set_value		2,3
	set_value		3,12
	enqueue_goal_with_priority		3,'$mpimos_code_manager:create/3_3_0',4
	put_integer		3,4040
	b_rate		3,3
	create_goal		3
	set_value		1,11
	set_value		2,2
	set_value		3,10
	enqueue_goal_with_priority		3,'$mpimos_file_manager:create/3_3_0',3
	put_integer		2,4084
	b_rate		2,2
	create_goal		3
	set_value		1,6
	set_value		2,1
	set_value		3,9
	enqueue_goal_with_priority		3,'$mpimos_window_manager:create/3_3_0',2
	put_integer		1,4088
	b_rate		1,1
	create_goal		1
	set_value		1,8
	enqueue_goal_with_priority		1,'$mpimos_command_interpreter:kl1cmp_create/1_1_0',1
	proceed
kl1cmp_start_3_1:
	suspend		kl1cmp_start_3_0
	module_entry		mpimos_booter
	predicate		distributor,2
distributor_2_0:
	try_me_else		distributor_2_1
	wait_list_var_var		1,6,3
	wait_vector		6,3
	read_element		6,0,4
	wait_atom		4,:
	read_elements_inc		6,1,4,2
	collect_list		1
	collect_vector		6
	create_goal		2
	set_value		1,3
	set_variable		2,6
	enqueue_goal		2,distributor_2_0
	put_value		1,2
	put_values_inc		2,4,3
	execute		4,send_4_0
distributor_2_1:
	otherwise		distributor_2_0
	try_me_else		distributor_2_5
	jump_on_non_list_var_var		1,distributor_2_7,3,4
	collect_list		1
	put_integer		5,1
	put_atom		6,'ERROR'
	put_func		1,2,illegal_format
	write_element_value		1,1,3
	b_raise		5,6,1
	put_value		1,4
	execute		2,distributor_2_0
distributor_2_7:
	check_nil		1,distributor_2_5
	collect_value		2
	put_integer		1,1
	put_atom		2,'ERROR'
	put_atom		3,system_stream_closed
	b_raise		1,2,3
	proceed
distributor_2_5:
	suspend		distributor_2_0
	module_entry		mpimos_booter
	predicate		send,4
send_4_0:
	create_goal		6
	set_variable		1,7
	set_marked_value		2,2
	set_value		3,3
	set_variable		4,6
	set_variable		5,5
	set_value		6,4
	enqueue_goal		6,send_request_6_0
	put_values_dec		3,7,2
	execute		5,find_5_0
send_4_1:
	suspend		send_4_0
	module_entry		mpimos_booter
	predicate		find,5
find_5_0:
	try_me_else		find_5_1
	wait_list_var_var		1,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	wait_value		7,2
	collect_list		1
	collect_value		7
	collect_value		2
	collect_vector		9
	get_value		4,8
	get_atom		3,success
	get_value		5,6
	proceed
find_5_1:
	otherwise		find_5_0
	try_me_else		find_5_5
	jump_on_non_list_var_var		1,find_5_7,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	put_reused_vector		9,9
	write_elements_inc		9,0,7,2
	get_reused_list_val_var		5,1,1,9,7
	put_value		1,6
	put_value		5,7
	execute		5,find_5_0
find_5_7:
	check_nil		1,find_5_5
	collect_value		4
	collect_value		2
	get_nil		5
	get_atom		3,failure
	proceed
find_5_5:
	suspend		find_5_0
	module_entry		mpimos_booter
	predicate		send_request,6
send_request_6_0:
	try_me_else		send_request_6_1
	wait_atom		1,success
	get_list_val_var		4,1,3,3
	put_vector		1,2
	write_elements_inc		1,0,2,2
	put_list_val_val		2,1,5
	get_list_value		6,2
	proceed
send_request_6_1:
	otherwise		send_request_6_0
	collect_value		4
	collect_value		1
	get_value		6,5
	put_integer		4,1
	put_atom		5,'ERROR'
	put_func		1,3,illegal_os_request
	write_elements_inc		1,1,2,2
	b_raise		4,5,1
	proceed
send_request_6_6:
	suspend		send_request_6_0
	module_entry		mpimos_booter
	predicate		process_name_list,2
process_name_list_2_0:
	try_me_else		process_name_list_2_1
	atom		1
	hash_on_atom		1,5,process_name_list_2_1
	bucket_entry_a		code_manager,process_name_list_2_3
	bucket_entry_a		file_manager,process_name_list_2_4
	bucket_entry_a		shell,process_name_list_2_5
	bucket_entry_a		timer_manager,process_name_list_2_6
	bucket_entry_a		window_manager,process_name_list_2_7
process_name_list_2_3:
	get_atom		2,success
	proceed
process_name_list_2_4:
	get_atom		2,success
	proceed
process_name_list_2_5:
	get_atom		2,success
	proceed
process_name_list_2_6:
	get_atom		2,success
	proceed
process_name_list_2_7:
	get_atom		2,success
	proceed
process_name_list_2_1:
	otherwise		process_name_list_2_0
	collect_value		1
	get_atom		2,failure
	proceed
process_name_list_2_10:
	suspend		process_name_list_2_0
	module_entry		mpimos_booter
	predicate		'$pdss_window_device:windows/1',1
'$pdss_window_device:windows/1_1_0':
	execute_external		pdss_window_device,windows,1
'$pdss_window_device:windows/1_1_1':
	suspend		'$pdss_window_device:windows/1_1_0'
	module_entry		mpimos_booter
	predicate		'$pdss_file_device:files/1',1
'$pdss_file_device:files/1_1_0':
	execute_external		pdss_file_device,files,1
'$pdss_file_device:files/1_1_1':
	suspend		'$pdss_file_device:files/1_1_0'
	module_entry		mpimos_booter
	predicate		'$pdss_timer_device:timer/1',1
'$pdss_timer_device:timer/1_1_0':
	execute_external		pdss_timer_device,timer,1
'$pdss_timer_device:timer/1_1_1':
	suspend		'$pdss_timer_device:timer/1_1_0'
	module_entry		mpimos_booter
	predicate		'$pdss_code_device:do/1',1
'$pdss_code_device:do/1_1_0':
	execute_external		pdss_code_device,do,1
'$pdss_code_device:do/1_1_1':
	suspend		'$pdss_code_device:do/1_1_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_command_interpreter:create/1',1
'$mpimos_command_interpreter:create/1_1_0':
	execute_external		mpimos_command_interpreter,create,1
'$mpimos_command_interpreter:create/1_1_1':
	suspend		'$mpimos_command_interpreter:create/1_1_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_window_manager:create/3',3
'$mpimos_window_manager:create/3_3_0':
	execute_external		mpimos_window_manager,create,3
'$mpimos_window_manager:create/3_3_1':
	suspend		'$mpimos_window_manager:create/3_3_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_file_manager:create/3',3
'$mpimos_file_manager:create/3_3_0':
	execute_external		mpimos_file_manager,create,3
'$mpimos_file_manager:create/3_3_1':
	suspend		'$mpimos_file_manager:create/3_3_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_timer_manager:create/3',3
'$mpimos_timer_manager:create/3_3_0':
	execute_external		mpimos_timer_manager,create,3
'$mpimos_timer_manager:create/3_3_1':
	suspend		'$mpimos_timer_manager:create/3_3_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_code_manager:create/3',3
'$mpimos_code_manager:create/3_3_0':
	execute_external		mpimos_code_manager,create,3
'$mpimos_code_manager:create/3_3_1':
	suspend		'$mpimos_code_manager:create/3_3_0'
	module_entry		mpimos_booter
	predicate		'$mpimos_command_interpreter:kl1cmp_create/1',1
'$mpimos_command_interpreter:kl1cmp_create/1_1_0':
	execute_external		mpimos_command_interpreter,kl1cmp_create,1
'$mpimos_command_interpreter:kl1cmp_create/1_1_1':
	suspend		'$mpimos_command_interpreter:kl1cmp_create/1_1_0'
