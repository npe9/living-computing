mpimos_directory:
	module		mpimos_directory
	entry		create,3,create_3_0
	entry		os_create,6,os_create_6_0
	entry		request,4,request_4_0
	module_entry		mpimos_directory
	predicate		create,3
create_3_0:
	put_integer		5,65536
	put_atom		6,directory
	put_func		4,4,create
	write_elements_inc		4,1,1,3
	b_raise		5,6,4
	put_integer		1,2
	b_consume_resource		1
	proceed
create_3_1:
	suspend		create_3_0
	module_entry		mpimos_directory
	predicate		request,4
request_4_0:
	try_me_else		request_4_1
	wait_vector		1,4
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,3
	string		6
	g_string		6,8,9
	wait_integer		9,8
	collect_vector		1
	create_goal		5
	set_value		1,5
	set_variable		2,5
	set_value		3,7
	set_values_inc		4,3,2
	enqueue_goal		5,wait_directory_5_0
	put_value		1,2
	put_values_dec		2,6,2
	execute_external		mpimos_utility,pathname,3
request_4_1:
	otherwise		request_4_0
	try_me_else		request_4_6
	wait_vector		1,4
	read_element		1,0,5
	wait_atom		5,create
	read_elements_inc		1,1,5,3
	collect_value		3
	collect_value		2
	collect_value		5
	collect_vector		1
	get_nil		4
	put_integer		1,1
	b_consume_resource		1
	put_func		3,2,status
	write_element_value		3,1,7
	put_atom		1,bad_directory_name_type
	put_value		2,6
	execute		3,create_error_3_0
request_4_6:
	suspend		request_4_0
	module_entry		mpimos_directory
	predicate		wait_directory,5
wait_directory_5_0:
	try_me_else		wait_directory_5_1
	wait		2
	put_func		6,5,directory
	write_element_variable		6,1,8
	write_element_value		6,2,2
	write_element_variable		6,3,7
	write_element_value		6,4,4
	put_func		2,3,:
	write_element_atom		2,1,file_manager
	write_element_value		2,2,6
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	get_list_value		5,4
	put_integer		2,10
	b_consume_resource		2
	put_func		5,2,status
	write_element_value		5,1,3
	put_value		2,8
	put_void		3
	put_value		4,7
	execute		5,create_monitor_5_0
wait_directory_5_1:
	suspend		wait_directory_5_0
	module_entry		mpimos_directory
	predicate		os_create,6
os_create_6_0:
	try_me_else		os_create_6_1
	wait		2
	put_value		7,2
	put_func		2,5,directory
	write_element_variable		2,1,9
	write_element_marked_value		2,2,7
	write_element_variable		2,3,8
	write_element_value		2,4,3
	put_func		3,3,:
	write_element_atom		3,1,file_manager
	write_element_value		3,2,2
	put_list_val_val		2,3,5
	get_list_value		4,2
	put_func		5,2,status
	write_element_value		5,1,6
	put_value		2,9
	put_values_inc		3,7,2
	execute		5,create_monitor_5_0
os_create_6_1:
	suspend		os_create_6_0
	module_entry		mpimos_directory
	predicate		create_monitor,5
create_monitor_5_0:
	try_me_else		create_monitor_5_1
	atom		4
	branch_on_atom		4,2,create_monitor_5_1
	bucket_entry_a		'fep#abnormal',create_monitor_5_3
	bucket_entry_a		'fep#normal',create_monitor_5_4
create_monitor_5_3:
	collect_value		1
	get_nil		2
	put_atom		1,cannot_access
	put_value		2,3
	put_value		3,5
	execute		3,create_error_3_0
create_monitor_5_4:
	put_integer		4,2
	b_consume_resource		4
	b_merge		6,4
	get_value		6,1
	put_func		1,3,pathname
	write_element_variable		1,1,7
	write_element_variable		1,2,6
	get_list_val_var		2,8,1,1
	create_goal		5
	set_value		1,4
	set_value		2,1
	put_func		1,2,atr
	write_element_value		1,1,3
	set_value		3,1
	set_values_dec		4,7,2
	enqueue_goal		5,wait_pathname_5_0
	put_value		1,5
	execute		1,create_success_1_0
create_monitor_5_1:
	suspend		create_monitor_5_0
	module_entry		mpimos_directory
	predicate		create_success,1
create_success_1_0:
	try_me_else		create_success_1_1
	wait_vector		1,2
	read_element		1,0,2
	wait_atom		2,status
	read_element		1,1,2
	collect_vector		1
	get_atom		2,success
	proceed
create_success_1_1:
	suspend		create_success_1_0
	module_entry		mpimos_directory
	predicate		create_error,3
create_error_3_0:
	try_me_else		create_error_3_1
	wait_vector		3,2
	read_element		3,0,4
	wait_atom		4,status
	read_element		3,1,4
	collect_value		2
	put_reused_func		2,3,error
	write_element_value		2,1,1
	get_vector_value		4,2
	proceed
create_error_3_1:
	suspend		create_error_3_0
	module_entry		mpimos_directory
	predicate		monitor,3
monitor_3_0:
	try_me_else		monitor_3_1
	jump_on_non_list		1,monitor_3_3
	read_car		1,4
	vector		4
	jump_on_arity		4,6,monitor_3_1
	table_entry		monitor_3_1
	table_entry		monitor_3_1
	table_entry		monitor_3_5
	table_entry		monitor_3_6
	table_entry		monitor_3_7
	table_entry		monitor_3_8
monitor_3_5:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,monitor_3_1
	bucket_entry_a		do,monitor_3_10
	bucket_entry_a		pathname,monitor_3_11
monitor_3_10:
	read_element		4,1,6
	jump_on_non_list		6,monitor_3_13
	read_cdr		1,7
	read_car		6,5
	read_cdr		6,8
	collect_list		6
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,monitor_3_0
	put_reused_list_val_val		1,1,5,8
	put_value		2,7
	put_value		3,4
	execute		3,append_3_0
monitor_3_13:
	check_nil		6,monitor_3_1
	read_cdr		1,7
	collect_list		1
	collect_vector		4
	put_value		1,7
	execute		3,monitor_3_0
monitor_3_11:
	read_cdr		1,6
	read_element		4,1,7
	collect_list		1
	collect_vector		4
	put_integer		1,1
	b_vector_element		3,1,1,3
	get_value		1,7
	put_value		1,6
	execute		3,monitor_3_0
monitor_3_6:
	read_cdr		1,5
	read_element		4,0,6
	wait_atom		6,delete
	read_elements_inc		4,1,6,2
	string		6
	g_string		6,8,9
	wait_integer		9,8
	put_reused_func		4,4,delete
	write_element_value		4,1,6
	write_element_variable		4,2,6
	get_reused_list_val_var		2,1,1,4,4
	put_integer		1,3
	b_consume_resource		1
	put_values_dec		1,5,2
	put_values_inc		4,6,2
	execute		5,delete_5_0
monitor_3_7:
	read_cdr		1,5
	read_element		4,0,6
	wait_atom		6,listing
	read_elements_inc		4,1,6,3
	string		6
	g_string		6,9,10
	wait_integer		10,8
	put_reused_func		4,4,listing
	write_element_value		4,1,6
	write_element_variable		4,2,9
	write_element_variable		4,3,6
	get_reused_list_val_var		2,1,1,4,4
	put_integer		1,3
	b_consume_resource		1
	put_values_dec		1,5,2
	put_value		4,9
	put_value		5,7
	put_value		7,8
	execute		7,listing_7_0
monitor_3_8:
	read_cdr		1,5
	read_element		4,0,6
	wait_atom		6,open
	read_elements_inc		4,1,6,4
	collect_list		1
	collect_vector		4
	put_integer		1,1
	b_vector_element		3,1,1,3
	create_goal		5
	set_value		1,5
	set_values_inc		2,2,2
	set_variable		4,2
	set_value		5,9
	enqueue_goal		5,open_5_0
	create_goal		4
	set_value		1,6
	set_variable		2,3
	set_value		3,8
	set_value		4,2
	enqueue_goal_external		mpimos_file,create,4
	put_value		2,7
	execute_external		mpimos_utility,pathname,3
monitor_3_3:
	check_nil		1,monitor_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
monitor_3_1:
	otherwise		monitor_3_0
	try_me_else		monitor_3_26
	wait_list_var_var		1,4,5
	collect_list		1
	put_value		6,3
	create_goal		3
	set_value		1,5
	set_value		2,2
	set_variable		3,5
	enqueue_goal		3,monitor_3_0
	put_atom		1,warning
	put_atom		2,illegal_command
	put_value		3,4
	put_value		4,6
	execute		5,command_error_5_0
monitor_3_26:
	suspend		monitor_3_0
	module_entry		mpimos_directory
	predicate		wait_pathname,5
wait_pathname_5_0:
	try_me_else		wait_pathname_5_1
	string		4
	wait_atom		5,'fep#normal'
	g_string		4,6,7
	wait_integer		7,8
	collect_value		3
	put_func		3,2,atr
	write_element_value		3,1,4
	execute		3,monitor_3_0
wait_pathname_5_1:
	suspend		wait_pathname_5_0
	module_entry		mpimos_directory
	predicate		listing,7
listing_7_0:
	try_me_else		listing_7_1
	atom		6
	branch_on_atom		6,2,listing_7_1
	bucket_entry_a		'fep#abnormal',listing_7_3
	bucket_entry_a		'fep#normal',listing_7_4
listing_7_3:
	get_nil		5
	get_nil		4
	put_integer		4,1
	b_consume_resource		4
	put_structured_constant		4,'$SCNST_0'
	get_value		7,4
	execute		3,monitor_3_0
listing_7_4:
	put_value		8,7
	put_func		6,3,next_file_name
	write_element_variable		6,1,9
	write_element_variable		6,2,7
	get_list_val_var		4,10,6,6
	put_integer		4,2
	b_consume_resource		4
	put_value		4,6
	put_value		6,9
	execute		8,make_list_8_0
listing_7_1:
	suspend		listing_7_0
	module_entry		mpimos_directory
	predicate		make_list,8
make_list_8_0:
	try_me_else		make_list_8_1
	atom		7
	branch_on_atom		7,2,make_list_8_1
	bucket_entry_a		'fep#end_of_file',make_list_8_3
	bucket_entry_a		'fep#normal',make_list_8_4
make_list_8_3:
	collect_value		6
	get_nil		5
	get_nil		4
	put_integer		4,2
	b_consume_resource		4
	get_atom		8,success
	execute		3,monitor_3_0
make_list_8_4:
	get_list_val_var		5,7,6,9
	put_func		5,3,next_file_name
	write_element_variable		5,1,6
	write_element_variable		5,2,7
	get_list_val_var		4,10,5,5
	put_integer		4,2
	b_consume_resource		4
	put_value		4,5
	put_value		5,9
	execute		8,make_list_8_0
make_list_8_1:
	suspend		make_list_8_0
	module_entry		mpimos_directory
	predicate		delete,5
delete_5_0:
	try_me_else		delete_5_1
	atom		4
	branch_on_atom		4,2,delete_5_1
	bucket_entry_a		'fep#abnormal',delete_5_3
	bucket_entry_a		'fep#normal',delete_5_4
delete_5_3:
	put_structured_constant		4,'$SCNST_1'
	get_value		5,4
	execute		3,monitor_3_0
delete_5_4:
	get_atom		5,success
	execute		3,monitor_3_0
delete_5_1:
	suspend		delete_5_0
	module_entry		mpimos_directory
	predicate		open,5
open_5_0:
	try_me_else		open_5_1
	wait		4
	get_value		5,4
	execute		3,monitor_3_0
open_5_1:
	suspend		open_5_0
	module_entry		mpimos_directory
	predicate		command_error,5
command_error_5_0:
	put_integer		6,1
	b_vector_element		4,6,4,6
	get_value		6,5
	create_goal		3
	set_value		1,1
	set_value		2,4
	put_func		1,2,putt
	write_element_variable		1,1,6
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		5,1,4
	put_func		1,2,putb
	write_element_variable		1,1,7
	put_list_val_val		4,1,5
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		5,1,4
	set_value		3,5
	enqueue_goal		3,raise_error_3_0
	create_goal		2
	set_value		1,2
	set_value		2,7
	enqueue_goal		2,message_2_0
	put_value		1,3
	put_value		2,6
	execute_external		mpimos_utility,freeze,2
command_error_5_1:
	suspend		command_error_5_0
	module_entry		mpimos_directory
	predicate		raise_error,3
raise_error_3_0:
	put_integer		6,262144
	put_structured_constant		4,'$SCNST_4'
	put_func		5,2,do
	write_element_value		5,1,3
	put_list_val_val		3,5,4
	put_structured_constant		4,'$SCNST_5'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,5
	put_structured_constant		3,'$SCNST_6'
	put_list_val_val		4,3,2
	b_raise		6,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_3_1:
	suspend		raise_error_3_0
	module_entry		mpimos_directory
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	wait_atom		1,illegal_command
	put_structured_constant		1,'$SCNST_7'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	module_entry		mpimos_directory
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
	get_value		2,3
	proceed
append_3_1:
	suspend		append_3_0
	begin_const_section		mpimos_directory
'$SCNST_0_0':
	define_desc		0,2
	define_atom		error
	define_atom		cannot_listing
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		error
	define_atom		cannot_delete
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		11,1
	define_integer		2109216
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_2':
	define_desc		27,1
	define_integer		46
'$SCNST_4_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_2'
'$SCNST_4_3':
	define_atom		nl
	define_atom		[]
'$SCNST_4_0':
	define_vector		'$SCNST_4_1'
	define_list		'$SCNST_4_3'
'$SCNST_4':
	define_list		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		27,1
	define_integer		41
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		3,6
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		1919509536
	define_integer		1869898597
	define_integer		673216882
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_0':
	define_desc		11,4
	define_integer		1701604457
	define_integer		543973735
	define_integer		1835888483
	define_integer		6581857
'$SCNST_7':
	define_string		'$SCNST_7_0'
