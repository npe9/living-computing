'Sho-en':
	module		'Sho-en'
	entry		create,8,create_8_0
	entry		create,7,create_7_0
	entry		execute,8,execute_8_0
	entry		execute,7,execute_7_0
	entry		raise,3,raise_3_0
	module_entry		'Sho-en'
	predicate		create,8
create_8_0:
	b_vector		3,3,9
	put_vector		10,3
	write_elements_inc		10,0,1,3
	put_marked_value		1,4
	put_marked_value		2,5
	b_create_shoen		10,9,1,2,6,2,1
	get_value		1,8
	put_value		1,7
	put_values_inc		3,4,2
	execute		4,shoen_4_0
create_8_1:
	suspend		create_8_0
	module_entry		'Sho-en'
	predicate		create,7
create_7_0:
	put_marked_value		8,3
	put_marked_value		9,4
	b_create_shoen		1,2,8,9,5,2,1
	get_value		1,7
	put_value		1,6
	execute		4,shoen_4_0
create_7_1:
	suspend		create_7_0
	module_entry		'Sho-en'
	predicate		shoen,4
shoen_4_0:
	try_me_else		shoen_4_1
	jump_on_non_list		1,shoen_4_3
	read_car		1,5
	jump_on_non_atom		5,shoen_4_5
	hash_on_atom		5,4,shoen_4_1
	bucket_entry_a		abort,shoen_4_6
	bucket_entry_a		remove,shoen_4_7
	bucket_entry_a		start,shoen_4_8
	bucket_entry_a		stop,shoen_4_9
shoen_4_6:
	read_cdr		1,6
	wait		2
	collect_list		1
	b_abort_shoen		2,2
	put_value		1,6
	execute		4,shoen_4_0
shoen_4_7:
	read_cdr		1,6
	wait_nil		6
	wait		2
	collect_list		1
	collect_value		4
	collect_value		3
	b_remove_shoen		2
	proceed
shoen_4_8:
	read_cdr		1,6
	wait		2
	collect_list		1
	b_start_shoen		2,2
	put_value		1,6
	execute		4,shoen_4_0
shoen_4_9:
	read_cdr		1,6
	wait		2
	collect_list		1
	b_stop_shoen		2,2
	put_value		1,6
	execute		4,shoen_4_0
shoen_4_5:
	is_vector		5,shoen_4_1
	jump_on_arity		5,4,shoen_4_1
	table_entry		shoen_4_1
	table_entry		shoen_4_1
	table_entry		shoen_4_10
	table_entry		shoen_4_11
shoen_4_10:
	read_element		5,0,6
	atom		6
	branch_on_atom		6,2,shoen_4_1
	bucket_entry_a		more_reduction,shoen_4_13
	bucket_entry_a		statistics,shoen_4_14
shoen_4_13:
	read_cdr		1,7
	read_element		5,1,8
	wait		2
	collect_list		1
	collect_vector		5
	b_shoen_add_resource		2,8,2
	put_value		1,7
	execute		4,shoen_4_0
shoen_4_14:
	read_cdr		1,7
	read_element		5,1,8
	wait		2
	collect_list		1
	collect_vector		5
	b_shoen_statistics		2,1,2
	put_vector		5,1
	write_element_value		5,0,1
	get_vector_value		8,5
	put_value		1,7
	execute		4,shoen_4_0
shoen_4_11:
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,priority
	read_elements_inc		5,1,7,2
	wait		2
	collect_list		1
	collect_value		4
	collect_value		3
	collect_vector		5
	put_value		1,6
	put_values_inc		3,7,2
	execute		4,shoen_4_0
shoen_4_3:
	check_nil		1,shoen_4_1
	wait		2
	collect_value		4
	collect_value		3
	b_stop_shoen		2,1
	b_abort_shoen		1,1
	b_remove_shoen		1
	proceed
shoen_4_1:
	suspend		shoen_4_0
	module_entry		'Sho-en'
	predicate		execute,8
execute_8_0:
	b_vector		3,3,9
	put_vector		10,3
	write_elements_inc		10,0,1,3
	b_create_shoen		10,9,4,5,6,4,2
	b_merge		3,1
	get_value		1,8
	put_value		1,7
	execute		4,normal_4_0
execute_8_1:
	suspend		execute_8_0
	module_entry		'Sho-en'
	predicate		execute,7
execute_7_0:
	b_create_shoen		1,2,3,4,5,4,2
	b_merge		3,1
	get_value		1,7
	put_value		1,6
	execute		4,normal_4_0
execute_7_1:
	suspend		execute_7_0
	module_entry		'Sho-en'
	predicate		normal,4
normal_4_0:
	try_me_else		normal_4_1
	wait		1
	wait		4
	execute		4,normal_control_4_0
normal_4_1:
	try_me_else		normal_4_5
	wait		2
	wait		4
	execute		4,normal_report_4_0
normal_4_5:
	suspend		normal_4_0
	module_entry		'Sho-en'
	predicate		normal_control,4
normal_control_4_0:
	try_me_else		normal_control_4_1
	jump_on_non_list		1,normal_control_4_3
	read_car		1,5
	jump_on_non_atom		5,normal_control_4_5
	hash_on_atom		5,5,normal_control_4_1
	bucket_entry_a		abort,normal_control_4_6
	bucket_entry_a		allow_resource_report,normal_control_4_7
	bucket_entry_a		start,normal_control_4_8
	bucket_entry_a		statistics,normal_control_4_9
	bucket_entry_a		stop,normal_control_4_10
normal_control_4_6:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,aborted
	write_cdr_variable		1,5
	get_list_value		3,1
	b_abort_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
normal_control_4_7:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,resource_report_allowed
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
normal_control_4_8:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,started
	write_cdr_variable		1,5
	get_list_value		3,1
	b_start_shoen		4,1
	put_integer		3,0
	b_shoen_add_resource		1,3,4
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
normal_control_4_9:
	read_cdr		1,6
	put_vector		5,2
	write_element_variable		5,0,8
	write_element_variable		5,1,7
	put_reused_list		1,1
	write_car_atom		1,statistics_started
	write_cdr_value		1,5
	get_list_value		3,1
	b_shoen_statistics		4,1,3
	create_goal		4
	set_value		1,6
	set_value		2,2
	set_value		3,7
	set_value		4,3
	enqueue_goal		4,normal_4_0
	put_value		2,8
	execute		2,statistics_2_0
normal_control_4_10:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,stopped
	write_cdr_variable		1,5
	get_list_value		3,1
	b_stop_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
normal_control_4_5:
	check_vector		5,2,normal_control_4_1
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,add_resource
	read_element		5,1,7
	collect_vector		5
	put_reused_list		5,1
	write_car_atom		5,resource_added
	write_cdr_variable		5,1
	get_list_value		3,5
	create_goal		4
	set_value		1,6
	set_variable		2,3
	set_value		3,1
	set_variable		4,5
	enqueue_goal		4,normal_4_0
	put_value		1,7
	execute		5,add_resource_5_0
normal_control_4_3:
	check_nil		1,normal_control_4_1
	b_stop_shoen		4,1
	b_abort_shoen		1,1
	b_remove_shoen		1
	put_values_inc		1,2,2
	execute		2,removed_2_0
normal_control_4_1:
	suspend		normal_control_4_0
	module_entry		'Sho-en'
	predicate		normal_report,4
normal_report_4_0:
	try_me_else		normal_report_4_1
	list		2
	read_car		2,5
	try_me_else		normal_report_4_3
	atom		5
	branch_on_atom		5,3,normal_report_4_3
	bucket_entry_a		aborted,normal_report_4_5
	bucket_entry_a		reduction_limit,normal_report_4_6
	bucket_entry_a		succeeded,normal_report_4_7
normal_report_4_5:
	read_cdr		2,6
	put_reused_list		2,2
	write_car_atom		2,terminated
	write_cdr_variable		2,5
	get_list_value		3,2
	put_values_dec		2,6,2
	execute		4,exit_4_0
normal_report_4_6:
	read_cdr		2,6
	put_reused_list		2,2
	write_car_atom		2,resource_low
	write_cdr_variable		2,5
	get_list_value		3,2
	put_values_dec		2,6,2
	execute		4,reported_4_0
normal_report_4_7:
	read_cdr		2,6
	put_reused_list		2,2
	write_car_atom		2,terminated
	write_cdr_variable		2,5
	get_list_value		3,2
	put_values_dec		2,6,2
	execute		4,exit_4_0
normal_report_4_3:
	read_cdr		2,6
	try_me_else		normal_report_4_1
	put_atom		7,reduction_limit
	g_diff		5,7
	put_atom		7,succeeded
	g_diff		5,7
	put_atom		7,aborted
	g_diff		5,7
	collect_list		2
	create_goal		4
	set_value		1,1
	set_value		2,6
	set_variable		3,6
	set_value		4,4
	enqueue_goal		4,normal_4_0
	put_value		1,5
	put_value		2,3
	put_value		3,6
	execute		3,report_handler_3_0
normal_report_4_1:
	suspend		normal_report_4_0
	module_entry		'Sho-en'
	predicate		reported,4
reported_4_0:
	try_me_else		reported_4_1
	wait		1
	wait		4
	execute		4,reported_control_4_0
reported_4_1:
	try_me_else		reported_4_5
	wait		2
	wait		4
	execute		4,reported_report_4_0
reported_4_5:
	suspend		reported_4_0
	module_entry		'Sho-en'
	predicate		reported_control,4
reported_control_4_0:
	try_me_else		reported_control_4_1
	jump_on_non_list		1,reported_control_4_3
	read_car		1,5
	jump_on_non_atom		5,reported_control_4_5
	hash_on_atom		5,5,reported_control_4_1
	bucket_entry_a		abort,reported_control_4_6
	bucket_entry_a		allow_resource_report,reported_control_4_7
	bucket_entry_a		start,reported_control_4_8
	bucket_entry_a		statistics,reported_control_4_9
	bucket_entry_a		stop,reported_control_4_10
reported_control_4_6:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,aborted
	write_cdr_variable		1,5
	get_list_value		3,1
	b_abort_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_4_0
reported_control_4_7:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,resource_report_allowed
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
reported_control_4_8:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,started
	write_cdr_variable		1,5
	get_list_value		3,1
	b_start_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_4_0
reported_control_4_9:
	read_cdr		1,6
	put_vector		5,2
	write_element_variable		5,0,8
	write_element_variable		5,1,7
	put_reused_list		1,1
	write_car_atom		1,statistics_started
	write_cdr_value		1,5
	get_list_value		3,1
	b_shoen_statistics		4,1,3
	create_goal		4
	set_value		1,6
	set_value		2,2
	set_value		3,7
	set_value		4,3
	enqueue_goal		4,reported_4_0
	put_value		2,8
	execute		2,statistics_2_0
reported_control_4_10:
	read_cdr		1,6
	put_reused_list		1,1
	write_car_atom		1,stopped
	write_cdr_variable		1,5
	get_list_value		3,1
	b_stop_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_4_0
reported_control_4_5:
	check_vector		5,2,reported_control_4_1
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,add_resource
	read_element		5,1,7
	collect_vector		5
	put_reused_list		5,1
	write_car_atom		5,resource_added
	write_cdr_variable		5,1
	get_list_value		3,5
	create_goal		4
	set_value		1,6
	set_variable		2,3
	set_value		3,1
	set_variable		4,5
	enqueue_goal		4,reported_4_0
	put_value		1,7
	execute		5,add_resource_5_0
reported_control_4_3:
	check_nil		1,reported_control_4_1
	b_stop_shoen		4,1
	b_abort_shoen		1,1
	b_remove_shoen		1
	put_values_inc		1,2,2
	execute		2,removed_reported_2_0
reported_control_4_1:
	suspend		reported_control_4_0
	module_entry		'Sho-en'
	predicate		reported_report,4
reported_report_4_0:
	try_me_else		reported_report_4_1
	list		2
	read_car		2,5
	try_me_else		reported_report_4_3
	atom		5
	branch_on_atom		5,3,reported_report_4_3
	bucket_entry_a		aborted,reported_report_4_5
	bucket_entry_a		reduction_limit,reported_report_4_6
	bucket_entry_a		succeeded,reported_report_4_7
reported_report_4_5:
	read_cdr		2,6
	put_reused_list		2,2
	write_car_atom		2,terminated
	write_cdr_variable		2,5
	get_list_value		3,2
	put_values_dec		2,6,2
	execute		4,exit_4_0
reported_report_4_6:
	read_cdr		2,6
	collect_list		2
	put_value		2,6
	execute		4,reported_low_4_0
reported_report_4_7:
	read_cdr		2,6
	put_reused_list		2,2
	write_car_atom		2,terminated
	write_cdr_variable		2,5
	get_list_value		3,2
	put_values_dec		2,6,2
	execute		4,exit_4_0
reported_report_4_3:
	read_cdr		2,6
	try_me_else		reported_report_4_1
	put_atom		7,reduction_limit
	g_diff		5,7
	put_atom		7,succeeded
	g_diff		5,7
	put_atom		7,aborted
	g_diff		5,7
	collect_list		2
	create_goal		4
	set_value		1,1
	set_value		2,6
	set_variable		3,6
	set_value		4,4
	enqueue_goal		4,reported_4_0
	put_value		1,5
	put_value		2,3
	put_value		3,6
	execute		3,report_handler_3_0
reported_report_4_1:
	suspend		reported_report_4_0
	module_entry		'Sho-en'
	predicate		reported_low,4
reported_low_4_0:
	try_me_else		reported_low_4_1
	jump_on_non_list		1,reported_low_4_3
	read_car		1,5
	jump_on_non_atom		5,reported_low_4_5
	hash_on_atom		5,5,reported_low_4_1
	bucket_entry_a		abort,reported_low_4_6
	bucket_entry_a		allow_resource_report,reported_low_4_7
	bucket_entry_a		start,reported_low_4_8
	bucket_entry_a		statistics,reported_low_4_9
	bucket_entry_a		stop,reported_low_4_10
reported_low_4_6:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,aborted
	write_cdr_variable		1,5
	get_list_value		3,1
	b_abort_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_low_4_0
reported_low_4_7:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,resource_low
	write_cdr_variable		1,5
	put_list		7
	write_car_atom		7,resource_report_allowed
	write_cdr_value		7,1
	get_list_value		3,7
	put_value		1,6
	put_value		3,5
	execute		4,normal_4_0
reported_low_4_8:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,started
	write_cdr_variable		1,5
	get_list_value		3,1
	b_start_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_low_4_0
reported_low_4_9:
	read_cdr		1,6
	wait		4
	put_vector		5,2
	write_element_variable		5,0,8
	write_element_variable		5,1,7
	put_reused_list		1,1
	write_car_atom		1,statistics_started
	write_cdr_value		1,5
	get_list_value		3,1
	b_shoen_statistics		4,1,3
	create_goal		4
	set_value		1,6
	set_value		2,2
	set_value		3,8
	set_value		4,3
	enqueue_goal		4,reported_low_4_0
	put_value		2,7
	execute		2,statistics_2_0
reported_low_4_10:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,stopped
	write_cdr_variable		1,5
	get_list_value		3,1
	b_stop_shoen		4,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_low_4_0
reported_low_4_5:
	check_vector		5,2,reported_low_4_1
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,add_resource
	read_element		5,1,7
	wait		4
	collect_vector		5
	put_reused_list		1,1
	write_car_atom		1,resource_added
	write_cdr_variable		1,5
	get_list_value		3,1
	b_shoen_add_resource		4,7,4
	put_value		1,6
	put_value		3,5
	execute		4,reported_4_0
reported_low_4_3:
	check_nil		1,reported_low_4_1
	wait		4
	b_stop_shoen		4,1
	b_abort_shoen		1,1
	b_remove_shoen		1
	put_values_inc		1,2,2
	execute		2,removed_2_0
reported_low_4_1:
	suspend		reported_low_4_0
	module_entry		'Sho-en'
	predicate		exit,4
exit_4_0:
	try_me_else		exit_4_1
	jump_on_non_list		1,exit_4_3
	read_car		1,5
	jump_on_non_atom		5,exit_4_5
	hash_on_atom		5,5,exit_4_1
	bucket_entry_a		abort,exit_4_6
	bucket_entry_a		allow_resource_report,exit_4_7
	bucket_entry_a		start,exit_4_8
	bucket_entry_a		statistics,exit_4_9
	bucket_entry_a		stop,exit_4_10
exit_4_6:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,aborted
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,exit_4_0
exit_4_7:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,resource_report_allowed
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,exit_4_0
exit_4_8:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,started
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,exit_4_0
exit_4_9:
	read_cdr		1,6
	wait		4
	put_vector		5,2
	write_element_variable		5,0,8
	write_element_variable		5,1,7
	put_reused_list		1,1
	write_car_atom		1,statistics_started
	write_cdr_value		1,5
	get_list_value		3,1
	b_shoen_statistics		4,1,3
	create_goal		4
	set_value		1,6
	set_value		2,2
	set_value		3,7
	set_value		4,3
	enqueue_goal		4,exit_4_0
	put_value		2,8
	execute		2,statistics_2_0
exit_4_10:
	read_cdr		1,6
	wait		4
	put_reused_list		1,1
	write_car_atom		1,stopped
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,exit_4_0
exit_4_5:
	check_vector		5,2,exit_4_1
	read_cdr		1,6
	read_element		5,0,7
	wait_atom		7,add_resource
	read_element		5,1,7
	wait		4
	collect_value		7
	collect_vector		5
	put_reused_list		1,1
	write_car_atom		1,resource_added
	write_cdr_variable		1,5
	get_list_value		3,1
	put_value		1,6
	put_value		3,5
	execute		4,exit_4_0
exit_4_3:
	check_nil		1,exit_4_1
	wait		4
	collect_value		2
	get_nil		3
	b_remove_shoen		4
	proceed
exit_4_1:
	suspend		exit_4_0
	module_entry		'Sho-en'
	predicate		removed,2
removed_2_0:
	try_me_else		removed_2_1
	list		1
	read_car		1,3
	try_me_else		removed_2_3
	atom		3
	branch_on_atom		3,3,removed_2_3
	bucket_entry_a		aborted,removed_2_5
	bucket_entry_a		reduction_limit,removed_2_6
	bucket_entry_a		succeeded,removed_2_7
removed_2_5:
	read_cdr		1,4
	collect_list		1
	collect_value		4
	put_structured_constant		1,'$SCNST_0'
	get_value		2,1
	proceed
removed_2_6:
	read_cdr		1,4
	put_reused_list		1,1
	write_car_atom		1,resource_low
	write_cdr_variable		1,3
	get_list_value		2,1
	put_values_dec		1,4,2
	execute		2,removed_reported_2_0
removed_2_7:
	read_cdr		1,4
	collect_list		1
	collect_value		4
	put_structured_constant		1,'$SCNST_1'
	get_value		2,1
	proceed
removed_2_3:
	read_cdr		1,4
	try_me_else		removed_2_1
	put_atom		5,reduction_limit
	g_diff		3,5
	put_atom		5,succeeded
	g_diff		3,5
	put_atom		5,aborted
	g_diff		3,5
	collect_list		1
	create_goal		2
	set_value		1,4
	set_variable		2,4
	enqueue_goal		2,removed_2_0
	put_value		1,3
	put_value		3,4
	execute		3,report_handler_3_0
removed_2_1:
	suspend		removed_2_0
	module_entry		'Sho-en'
	predicate		removed_reported,2
removed_reported_2_0:
	try_me_else		removed_reported_2_1
	list		1
	read_car		1,3
	try_me_else		removed_reported_2_3
	atom		3
	branch_on_atom		3,3,removed_reported_2_3
	bucket_entry_a		aborted,removed_reported_2_5
	bucket_entry_a		reduction_limit,removed_reported_2_6
	bucket_entry_a		succeeded,removed_reported_2_7
removed_reported_2_5:
	read_cdr		1,4
	collect_list		1
	collect_value		4
	put_structured_constant		1,'$SCNST_2'
	get_value		2,1
	proceed
removed_reported_2_6:
	read_cdr		1,4
	collect_list		1
	put_value		1,4
	execute		2,removed_reported_2_0
removed_reported_2_7:
	read_cdr		1,4
	collect_list		1
	collect_value		4
	put_structured_constant		1,'$SCNST_3'
	get_value		2,1
	proceed
removed_reported_2_3:
	read_cdr		1,4
	try_me_else		removed_reported_2_1
	put_atom		5,reduction_limit
	g_diff		3,5
	put_atom		5,succeeded
	g_diff		3,5
	put_atom		5,aborted
	g_diff		3,5
	collect_list		1
	create_goal		2
	set_value		1,4
	set_variable		2,4
	enqueue_goal		2,removed_reported_2_0
	put_value		1,3
	put_value		3,4
	execute		3,report_handler_3_0
removed_reported_2_1:
	suspend		removed_reported_2_0
	module_entry		'Sho-en'
	predicate		report_handler,3
report_handler_3_0:
	try_me_else		report_handler_3_1
	vector		1
	jump_on_arity		1,9,report_handler_3_1
	table_entry		report_handler_3_1
	table_entry		report_handler_3_1
	table_entry		report_handler_3_1
	table_entry		report_handler_3_1
	table_entry		report_handler_3_3
	table_entry		report_handler_3_4
	table_entry		report_handler_3_5
	table_entry		report_handler_3_6
	table_entry		report_handler_3_7
report_handler_3_3:
	read_element		1,0,4
	wait_atom		4,deadlock
	read_elements_inc		1,1,4,3
	put_reused_vector		1,1
	write_element_integer		1,0,0
	write_elements_dec		1,1,5,2
	write_element_value		1,3,6
	put_func		4,3,deadlock
	write_element_integer		4,1,11
	write_element_value		4,2,1
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
report_handler_3_4:
	read_element		1,0,4
	wait_atom		4,raised
	read_elements_inc		1,1,4,4
	put_vector		8,3
	write_element_integer		8,0,0
	write_elements_inc		8,1,4,2
	put_reused_func		1,1,exception
	write_element_integer		1,1,12
	write_element_value		1,2,8
	write_elements_inc		1,3,6,2
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
report_handler_3_5:
	read_element		1,0,4
	wait_atom		4,exception
	read_elements_inc		1,1,4,5
	collect_vector		1
	put_vector		1,3
	write_element_integer		1,0,0
	write_elements_inc		1,1,5,2
	put_func		5,5,exception
	write_element_value		5,1,4
	write_element_value		5,2,1
	write_elements_inc		5,3,7,2
	put_list_val_val		1,5,3
	get_list_value		2,1
	proceed
report_handler_3_6:
	read_element		1,0,4
	wait_atom		4,exception
	read_element		1,1,5
	try_me_else		report_handler_3_9
	wait_integer		5,10
	read_elements_inc		1,2,6,5
	collect_value		8
	collect_vector		1
	put_vector		1,3
	write_element_integer		1,0,0
	write_elements_inc		1,1,6,2
	put_func		4,5,exception
	write_element_integer		4,1,10
	write_element_value		4,2,1
	write_elements_inc		4,3,9,2
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
report_handler_3_9:
	read_elements_inc		1,2,6,5
	try_me_else		report_handler_3_1
	put_integer		11,10
	g_diff		5,11
	collect_vector		1
	put_vector		1,4
	write_element_integer		1,0,0
	write_element_value		1,1,8
	write_elements_inc		1,2,6,2
	put_func		4,5,exception
	write_element_value		4,1,5
	write_element_value		4,2,1
	write_elements_inc		4,3,9,2
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
report_handler_3_7:
	read_element		1,0,4
	wait_atom		4,exception
	read_element		1,1,5
	try_me_else		report_handler_3_12
	wait_integer		5,8
	read_elements_inc		1,2,6,6
	collect_value		9
	collect_vector		1
	put_vector		1,5
	write_element_integer		1,0,0
	write_element_value		1,1,8
	write_element_integer		1,2,246
	write_elements_inc		1,3,6,2
	put_func		4,5,exception
	write_element_integer		4,1,8
	write_element_value		4,2,1
	write_elements_inc		4,3,10,2
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
report_handler_3_12:
	read_elements_inc		1,2,6,6
	try_me_else		report_handler_3_1
	put_integer		12,8
	g_diff		5,12
	collect_vector		1
	put_vector		1,5
	write_element_integer		1,0,0
	write_element_value		1,1,9
	write_element_value		1,2,6
	write_elements_dec		1,3,8,2
	put_func		4,5,exception
	write_element_value		4,1,5
	write_element_value		4,2,1
	write_elements_inc		4,3,10,2
	put_list_val_val		1,4,3
	get_list_value		2,1
	proceed
report_handler_3_1:
	suspend		report_handler_3_0
	module_entry		'Sho-en'
	predicate		add_resource,5
add_resource_5_0:
	try_me_else		add_resource_5_1
	list		2
	read_car		2,6
	try_me_else		add_resource_5_3
	wait_atom		6,reduction_limit
	read_cdr		2,7
	collect_list		2
	put_value		2,7
	execute		5,add_resource_5_0
add_resource_5_3:
	read_cdr		2,7
	try_me_else		add_resource_5_1
	put_atom		8,reduction_limit
	g_diff		6,8
	get_reused_list_val_var		3,2,2,6,6
	put_values_dec		2,7,2
	execute		5,add_resource_5_0
add_resource_5_1:
	get_value		2,3
	b_shoen_add_resource		4,1,1
	get_value		1,5
	proceed
add_resource_5_10:
	suspend		add_resource_5_0
	module_entry		'Sho-en'
	predicate		statistics,2
statistics_2_0:
	try_me_else		statistics_2_1
	wait		1
	put_vector		3,1
	write_element_value		3,0,1
	put_func		1,2,statistics
	write_element_value		1,1,3
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	proceed
statistics_2_1:
	suspend		statistics_2_0
	module_entry		'Sho-en'
	predicate		raise,3
raise_3_0:
	b_raise		1,2,3
	proceed
raise_3_1:
	suspend		raise_3_0
	begin_const_section		'Sho-en'
'$SCNST_0_0':
	define_atom		terminated
	define_atom		[]
'$SCNST_3':
'$SCNST_2':
'$SCNST_1':
'$SCNST_0':
	define_list		'$SCNST_0_0'
