mpimos_timer_device:
	module		mpimos_timer_device
	entry		timer,1,timer_1_0
	entry		timer_request,3,timer_request_3_0
	module_entry		mpimos_timer_device
	predicate		timer,1
timer_1_0:
	put_integer		2,65536
	put_atom		3,device_timer
	b_raise		2,3,1
	put_integer		1,2
	b_consume_resource		1
	proceed
timer_1_1:
	suspend		timer_1_0
	module_entry		mpimos_timer_device
	predicate		timer_request,3
timer_request_3_0:
	try_me_else		timer_request_3_1
	jump_on_non_atom		1,timer_request_3_3
	test_nil		1,timer_request_3_1
	collect_value		3
	collect_value		2
	put_integer		1,1
	b_consume_resource		1
	proceed
timer_request_3_3:
	is_vector		1,timer_request_3_1
	jump_on_arity		1,6,timer_request_3_1
	table_entry		timer_request_3_1
	table_entry		timer_request_3_1
	table_entry		timer_request_3_1
	table_entry		timer_request_3_1
	table_entry		timer_request_3_4
	table_entry		timer_request_3_5
timer_request_3_4:
	read_element		1,0,4
	wait_atom		4,get_count
	read_elements_inc		1,1,4,3
	collect_vector		1
	put_func		1,3,get_count
	write_element_variable		1,1,9
	write_element_variable		1,2,8
	put_func		7,3,:
	write_element_atom		7,1,timer_manager
	write_element_value		7,2,1
	get_list_val_var		3,10,7,1
	put_integer		3,9
	b_consume_resource		3
	create_goal		3
	set_value		1,6
	set_values_dec		2,2,2
	enqueue_goal		3,timer_request_3_0
	put_values_inc		1,4,2
	put_values_dec		3,9,2
	execute		4,wait_get_count_4_0
timer_request_3_5:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,2,timer_request_3_1
	bucket_entry_a		on_after,timer_request_3_7
	bucket_entry_a		on_at,timer_request_3_8
timer_request_3_7:
	read_elements_inc		1,1,5,4
	integer		5
	put_integer		9,0
	g_not_less_than		5,9
	put_integer		9,432000000
	g_less_than		5,9
	collect_vector		1
	put_func		1,4,on_after
	write_element_value		1,1,5
	write_element_variable		1,2,9
	write_element_variable		1,3,5
	put_func		4,3,:
	write_element_atom		4,1,timer_manager
	write_element_value		4,2,1
	get_list_val_var		3,10,4,1
	put_integer		3,9
	b_consume_resource		3
	create_goal		3
	set_value		1,8
	set_values_dec		2,2,2
	enqueue_goal		3,timer_request_3_0
	put_values_inc		1,6,2
	put_value		3,9
	put_value		4,5
	execute		4,wait_on_after_4_0
timer_request_3_8:
	read_elements_inc		1,1,5,4
	integer		5
	put_integer		9,0
	g_not_less_than		5,9
	put_integer		9,432000000
	g_less_than		5,9
	collect_vector		1
	put_func		1,4,on_at
	write_element_value		1,1,5
	write_element_variable		1,2,9
	write_element_variable		1,3,5
	put_func		4,3,:
	write_element_atom		4,1,timer_manager
	write_element_value		4,2,1
	get_list_val_var		3,10,4,1
	put_integer		3,9
	b_consume_resource		3
	create_goal		3
	set_value		1,8
	set_values_dec		2,2,2
	enqueue_goal		3,timer_request_3_0
	put_values_inc		1,6,2
	put_value		3,9
	put_value		4,5
	execute		4,wait_on_at_4_0
timer_request_3_1:
	otherwise		timer_request_3_0
	collect_value		2
	put_value		4,1
	get_nil		3
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,4
	execute		3,timer_error_3_0
timer_request_3_15:
	suspend		timer_request_3_0
	module_entry		mpimos_timer_device
	predicate		wait_get_count,4
wait_get_count_4_0:
	try_me_else		wait_get_count_4_1
	wait_atom		4,'fep#normal'
	get_value		1,3
	get_atom		2,'fep#normal'
	proceed
wait_get_count_4_1:
	try_me_else		wait_get_count_4_3
	put_atom		5,'fep#normal'
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_get_count_4_3:
	suspend		wait_get_count_4_0
	module_entry		mpimos_timer_device
	predicate		wait_on_at,4
wait_on_at_4_0:
	try_me_else		wait_on_at_4_1
	wait_atom		4,'fep#normal'
	get_atom		2,'fep#normal'
	put_value		2,3
	execute		2,wait_now_2_0
wait_on_at_4_1:
	try_me_else		wait_on_at_4_3
	put_atom		5,'fep#normal'
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_on_at_4_3:
	suspend		wait_on_at_4_0
	module_entry		mpimos_timer_device
	predicate		wait_on_after,4
wait_on_after_4_0:
	try_me_else		wait_on_after_4_1
	wait_atom		4,'fep#normal'
	get_atom		2,'fep#normal'
	put_value		2,3
	execute		2,wait_now_2_0
wait_on_after_4_1:
	try_me_else		wait_on_after_4_3
	put_atom		5,'fep#normal'
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_on_after_4_3:
	suspend		wait_on_after_4_0
	module_entry		mpimos_timer_device
	predicate		wait_now,2
wait_now_2_0:
	try_me_else		wait_now_2_1
	wait		2
	put_integer		2,1
	b_consume_resource		2
	get_atom		1,'fep#wake_up'
	proceed
wait_now_2_1:
	suspend		wait_now_2_0
	module_entry		mpimos_timer_device
	predicate		timer_error,3
timer_error_3_0:
	create_goal		2
	set_value		1,1
	put_func		1,4,putt
	write_element_variable		1,1,7
	write_element_integer		1,2,10
	write_element_integer		1,3,5
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_structured_constant		1,'$SCNST_0'
	put_list_val_val		5,1,4
	put_func		1,2,putb
	write_element_variable		1,1,6
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		5,1,4
	set_value		2,5
	enqueue_goal		2,raise_error_2_0
	create_goal		2
	set_value		1,3
	set_value		2,7
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,2
	put_value		2,6
	execute		2,message_2_0
timer_error_3_1:
	suspend		timer_error_3_0
	module_entry		mpimos_timer_device
	predicate		raise_error,2
raise_error_2_0:
	put_integer		5,262144
	put_structured_constant		3,'$SCNST_2'
	put_func		4,2,do
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_3'
	put_list_val_val		4,3,2
	b_raise		5,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_2_1:
	suspend		raise_error_2_0
	module_entry		mpimos_timer_device
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	wait_atom		1,illegal_command
	put_structured_constant		1,'$SCNST_4'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	begin_const_section		mpimos_timer_device
'$SCNST_0_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		3,2
	define_integer		1701669236
	define_integer		539959410
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_2':
	define_desc		27,1
	define_integer		46
'$SCNST_2_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_2'
'$SCNST_2_3':
	define_atom		nl
	define_atom		[]
'$SCNST_2_0':
	define_vector		'$SCNST_2_1'
	define_list		'$SCNST_2_3'
'$SCNST_2':
	define_list		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		27,4
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		32
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		11,4
	define_integer		1701604457
	define_integer		543973735
	define_integer		1835888483
	define_integer		6581857
'$SCNST_4':
	define_string		'$SCNST_4_0'
