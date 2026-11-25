mpimos_file_device:
	module		mpimos_file_device
	entry		files,1,files_1_0
	entry		file_request,4,file_request_4_0
	module_entry		mpimos_file_device
	predicate		files,1
files_1_0:
	put_integer		2,65536
	put_atom		3,device_file
	b_raise		2,3,1
	put_integer		1,2
	b_consume_resource		1
	proceed
files_1_1:
	suspend		files_1_0
	module_entry		mpimos_file_device
	predicate		file_request,4
file_request_4_0:
	try_me_else		file_request_4_1
	jump_on_non_atom		1,file_request_4_3
	test_nil		1,file_request_4_1
	collect_value		3
	collect_value		2
	get_nil		4
	put_integer		1,1
	b_consume_resource		1
	proceed
file_request_4_3:
	is_vector		1,file_request_4_1
	jump_on_arity		1,7,file_request_4_1
	table_entry		file_request_4_1
	table_entry		file_request_4_1
	table_entry		file_request_4_1
	table_entry		file_request_4_1
	table_entry		file_request_4_1
	table_entry		file_request_4_4
	table_entry		file_request_4_5
file_request_4_4:
	read_element		1,0,5
	wait_atom		5,directory
	read_elements_inc		1,1,5,4
	string		5
	g_string		5,9,10
	wait_integer		10,8
	put_reused_func		1,1,directory
	write_element_variable		1,1,12
	write_element_variable		1,2,10
	write_element_variable		1,3,11
	write_element_marked_value		1,4,3
	put_func		9,3,:
	write_element_atom		9,1,file_manager
	write_element_value		9,2,1
	get_list_val_var		4,13,9,1
	put_integer		4,10
	b_consume_resource		4
	create_goal		4
	set_value		1,8
	set_marked_value		2,2
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,file_request_4_0
	create_goal		5
	set_value		1,6
	set_value		2,12
	set_marked_value		3,5
	set_value		4,7
	set_value		5,11
	enqueue_goal		5,directory_wait_created_5_0
	put_value		1,2
	put_value		2,5
	put_value		3,10
	execute_external		mpimos_utility,pathname,3
file_request_4_5:
	read_element		1,0,5
	wait_atom		5,open
	read_elements_inc		1,1,5,5
	string		5
	g_string		5,10,11
	wait_integer		11,8
	atom		6
	put_reused_func		1,1,device_create
	write_element_variable		1,1,13
	write_element_variable		1,2,11
	write_element_marked_value		1,3,6
	write_element_variable		1,4,12
	write_element_marked_value		1,5,3
	put_func		10,3,:
	write_element_atom		10,1,file_manager
	write_element_value		10,2,1
	get_list_val_var		4,14,10,1
	put_integer		4,11
	b_consume_resource		4
	create_goal		4
	set_value		1,9
	set_marked_value		2,2
	set_value		3,3
	set_value		4,1
	enqueue_goal		4,file_request_4_0
	create_goal		6
	set_value		1,7
	set_value		2,13
	set_marked_value		3,5
	set_value		4,6
	set_value		5,8
	set_value		6,12
	enqueue_goal		6,file_wait_created_6_0
	put_value		1,2
	put_value		2,5
	put_value		3,11
	execute_external		mpimos_utility,pathname,3
file_request_4_1:
	otherwise		file_request_4_0
	collect_value		3
	collect_value		2
	put_value		3,1
	get_nil		4
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,error
	put_atom		2,illegal_command
	execute		3,file_error_3_0
file_request_4_10:
	suspend		file_request_4_0
	module_entry		mpimos_file_device
	predicate		file_wait_created,6
file_wait_created_6_0:
	try_me_else		file_wait_created_6_1
	wait_atom		4,'fep#read'
	wait_atom		6,'fep#normal'
	put_integer		4,1
	b_consume_resource		4
	get_atom		5,'fep#normal'
	put_func		4,3,status
	write_element_value		4,1,3
	write_element_atom		4,2,'fep#read'
	put_value		3,4
	execute		3,rfile_wait_reset_3_0
file_wait_created_6_1:
	try_me_else		file_wait_created_6_3
	atom		6
	branch_on_atom		6,2,file_wait_created_6_3
	bucket_entry_a		'fep#abnormal',file_wait_created_6_5
	bucket_entry_a		'fep#normal',file_wait_created_6_6
file_wait_created_6_5:
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		5,'fep#abnormal'
	get_nil		2
	proceed
file_wait_created_6_6:
	put_atom		7,'fep#read'
	g_diff		4,7
	get_atom		5,'fep#normal'
	put_func		5,3,status
	write_elements_inc		5,1,3,2
	put_value		3,5
	execute		3,wfile_wait_reset_3_0
file_wait_created_6_3:
	suspend		file_wait_created_6_0
	module_entry		mpimos_file_device
	predicate		rfile_wait_reset,3
rfile_wait_reset_3_0:
	try_me_else		rfile_wait_reset_3_1
	jump_on_non_atom		1,rfile_wait_reset_3_3
	test_nil		1,rfile_wait_reset_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
rfile_wait_reset_3_3:
	is_vector		1,rfile_wait_reset_3_1
	jump_on_arity		1,6,rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_4
	table_entry		rfile_wait_reset_3_5
	table_entry		rfile_wait_reset_3_6
	table_entry		rfile_wait_reset_3_7
rfile_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	collect_value		3
	put_reused_func		1,1,close
	write_element_variable		1,1,3
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	get_list_value		2,5
	put_integer		1,2
	b_consume_resource		1
	put_values_dec		1,4,2
	execute		2,wait_close_2_0
rfile_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,end_of_file
	read_elements_inc		1,1,4,2
	get_atom		4,'fep#abnormal'
	put_reused_func		4,1,end_of_file
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,5
	execute		4,rfile_not_reset_4_0
rfile_wait_reset_3_6:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,3,rfile_wait_reset_3_1
	bucket_entry_a		next_attention,rfile_wait_reset_3_9
	bucket_entry_a		pathname,rfile_wait_reset_3_10
	bucket_entry_a		putb,rfile_wait_reset_3_11
rfile_wait_reset_3_9:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,next_attention
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,rfile_not_reset_4_0
rfile_wait_reset_3_10:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,pathname
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,rfile_not_reset_4_0
rfile_wait_reset_3_11:
	read_elements_inc		1,1,5,3
	put_value		4,3
	get_atom		6,'fep#abnormal'
	create_goal		3
	set_value		1,7
	set_value		2,2
	set_variable		3,6
	enqueue_goal		3,rfile_wait_reset_3_0
	put_reused_func		3,1,putb
	write_element_value		3,1,5
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,not_write_mode
	put_value		5,6
	execute		5,file_error_5_0
rfile_wait_reset_3_7:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,2,rfile_wait_reset_3_1
	bucket_entry_a		getb,rfile_wait_reset_3_13
	bucket_entry_a		reset,rfile_wait_reset_3_14
rfile_wait_reset_3_13:
	read_elements_inc		1,1,5,4
	get_atom		7,'fep#abnormal'
	put_reused_func		4,1,getb
	write_elements_inc		4,1,5,2
	write_element_void		4,3
	write_element_void		4,4
	put_value		1,8
	execute		4,rfile_not_reset_4_0
rfile_wait_reset_3_14:
	read_elements_inc		1,1,5,4
	collect_value		6
	collect_vector		1
	put_value		6,3
	put_func		1,4,reset
	write_element_variable		1,1,4
	write_element_void		1,2
	write_element_variable		1,3,9
	get_list_val_var		2,10,1,3
	put_integer		1,2
	b_consume_resource		1
	put_value		1,8
	put_value		2,3
	put_value		3,5
	put_values_inc		5,6,2
	put_value		7,9
	execute		7,rfile_wait_status_7_0
rfile_wait_reset_3_1:
	otherwise		rfile_wait_reset_3_0
	collect_value		2
	put_value		5,1
	put_value		4,3
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,5
	put_void		5
	execute		5,file_error_5_0
rfile_wait_reset_3_23:
	suspend		rfile_wait_reset_3_0
	module_entry		mpimos_file_device
	predicate		rfile_not_reset,4
rfile_not_reset_4_0:
	put_value		6,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,5
	enqueue_goal		3,rfile_wait_reset_3_0
	put_atom		1,warning
	put_atom		2,file_not_reset
	put_value		3,4
	put_value		4,6
	execute		5,file_error_5_0
rfile_not_reset_4_1:
	suspend		rfile_not_reset_4_0
	module_entry		mpimos_file_device
	predicate		rfile,5
rfile_5_0:
	try_me_else		rfile_5_1
	wait_atom		3,'fep#abort'
	get_atom		4,'fep#abort'
	put_integer		3,2
	b_consume_resource		3
	put_value		3,5
	execute		3,rfile_wait_reset_3_0
rfile_5_1:
	try_me_else		rfile_5_6
	wait		1
	execute		5,rfile_com_5_0
rfile_5_6:
	suspend		rfile_5_0
	module_entry		mpimos_file_device
	predicate		rfile_com,5
rfile_com_5_0:
	try_me_else		rfile_com_5_1
	jump_on_non_atom		1,rfile_com_5_3
	test_nil		1,rfile_com_5_1
	collect_value		5
	collect_value		4
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
rfile_com_5_3:
	is_vector		1,rfile_com_5_1
	jump_on_arity		1,6,rfile_com_5_1
	table_entry		rfile_com_5_1
	table_entry		rfile_com_5_1
	table_entry		rfile_com_5_4
	table_entry		rfile_com_5_5
	table_entry		rfile_com_5_6
	table_entry		rfile_com_5_7
rfile_com_5_4:
	read_element		1,0,6
	wait_atom		6,close
	read_element		1,1,6
	collect_value		5
	collect_value		4
	collect_value		3
	put_reused_func		1,1,close
	write_element_variable		1,1,3
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	get_list_value		2,4
	put_integer		1,2
	b_consume_resource		1
	put_value		1,6
	put_value		2,3
	execute		2,wait_close_2_0
rfile_com_5_5:
	read_element		1,0,6
	wait_atom		6,end_of_file
	read_elements_inc		1,1,6,2
	collect_vector		1
	put_func		1,2,end_of_file
	write_element_variable		1,1,9
	get_list_val_var		2,10,1,8
	put_integer		1,2
	b_consume_resource		1
	put_values_inc		1,7,2
	put_value		7,9
	execute		7,rfile_wait_status_7_0
rfile_com_5_6:
	read_element		1,0,6
	atom		6
	branch_on_atom		6,3,rfile_com_5_1
	bucket_entry_a		next_attention,rfile_com_5_9
	bucket_entry_a		pathname,rfile_com_5_10
	bucket_entry_a		putb,rfile_com_5_11
rfile_com_5_9:
	read_elements_inc		1,1,7,3
	collect_value		7
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		5,rfile_5_0
rfile_com_5_10:
	read_elements_inc		1,1,7,3
	collect_vector		1
	put_func		1,3,pathname
	write_element_variable		1,1,11
	write_element_variable		1,2,10
	get_list_val_var		2,12,1,6
	put_integer		1,2
	b_consume_resource		1
	put_value		1,9
	put_value		2,6
	put_values_inc		6,7,2
	put_values_dec		8,11,2
	execute		9,rfile_wait_pathname_9_0
rfile_com_5_11:
	read_elements_inc		1,1,7,3
	get_atom		8,'fep#abnormal'
	create_goal		5
	set_value		1,9
	set_values_inc		2,2,3
	set_variable		5,6
	enqueue_goal		5,rfile_5_0
	put_reused_func		3,1,putb
	write_element_value		3,1,7
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,not_write_mode
	put_values_inc		4,5,2
	execute		5,file_error_5_0
rfile_com_5_7:
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,rfile_com_5_1
	bucket_entry_a		getb,rfile_com_5_13
	bucket_entry_a		reset,rfile_com_5_14
rfile_com_5_13:
	read_elements_inc		1,1,7,4
	integer		7
	put_integer		11,0
	g_less_than		11,7
	collect_vector		1
	put_func		1,4,getb
	write_element_variable		1,1,12
	write_element_value		1,2,7
	write_element_variable		1,3,11
	get_list_val_var		2,7,1,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,6
	put_values_inc		6,8,2
	put_values_dec		8,12,2
	execute		9,rfile_wait_buffer_9_0
rfile_com_5_14:
	read_elements_inc		1,1,7,4
	get_atom		9,'fep#abnormal'
	create_goal		5
	set_value		1,10
	set_values_inc		2,2,3
	set_variable		5,6
	enqueue_goal		5,rfile_5_0
	put_reused_func		3,1,reset
	write_elements_inc		3,1,7,2
	write_element_void		3,3
	write_element_void		3,4
	put_atom		1,warning
	put_atom		2,file_already_reset
	put_values_inc		4,5,2
	execute		5,file_error_5_0
rfile_com_5_1:
	otherwise		rfile_com_5_0
	collect_value		4
	collect_value		3
	collect_value		2
	put_value		2,1
	put_atom		1,illegal_command
	put_value		3,5
	execute		3,file_error_3_0
rfile_com_5_23:
	suspend		rfile_com_5_0
	module_entry		mpimos_file_device
	predicate		rfile_wait_status,7
rfile_wait_status_7_0:
	try_me_else		rfile_wait_status_7_1
	wait		7
	get_value		6,7
	execute		5,rfile_5_0
rfile_wait_status_7_1:
	suspend		rfile_wait_status_7_0
	module_entry		mpimos_file_device
	predicate		rfile_wait_buffer,9
rfile_wait_buffer_9_0:
	try_me_else		rfile_wait_buffer_9_1
	wait_atom		3,'fep#abort'
	get_atom		4,'fep#abort'
	put_integer		3,2
	b_consume_resource		3
	put_values_inc		3,5,5
	execute		7,rfile_wait_aborted_7_0
rfile_wait_buffer_9_1:
	try_me_else		rfile_wait_buffer_9_6
	jump_on_non_atom		8,rfile_wait_buffer_9_8
	test_atom		8,'fep#nil',rfile_wait_buffer_9_6
	wait_atom		9,'fep#end_of_file'
	get_atom		6,'fep#nil'
	get_atom		7,'fep#end_of_file'
	execute		5,rfile_5_0
rfile_wait_buffer_9_8:
	is_string		8,rfile_wait_buffer_9_6
	wait_atom		9,'fep#normal'
	g_string		8,10,11
	wait_integer		11,8
	get_value		6,8
	get_atom		7,'fep#normal'
	execute		5,rfile_5_0
rfile_wait_buffer_9_6:
	try_me_else		rfile_wait_buffer_9_10
	wait_atom		9,'fep#abnormal'
	collect_value		8
	collect_value		6
	get_atom		7,'fep#abnormal'
	execute		5,rfile_5_0
rfile_wait_buffer_9_10:
	suspend		rfile_wait_buffer_9_0
	module_entry		mpimos_file_device
	predicate		rfile_wait_pathname,9
rfile_wait_pathname_9_0:
	try_me_else		rfile_wait_pathname_9_1
	string		8
	wait_atom		9,'fep#normal'
	g_string		8,10,11
	wait_integer		11,8
	get_value		6,8
	get_atom		7,'fep#normal'
	execute		5,rfile_5_0
rfile_wait_pathname_9_1:
	suspend		rfile_wait_pathname_9_0
	module_entry		mpimos_file_device
	predicate		rfile_wait_aborted,7
rfile_wait_aborted_7_0:
	try_me_else		rfile_wait_aborted_7_1
	string		6
	wait_atom		7,'fep#normal'
	g_string		6,8,9
	wait_integer		9,8
	get_value		4,6
	get_atom		5,'fep#normal'
	execute		3,rfile_wait_reset_3_0
rfile_wait_aborted_7_1:
	try_me_else		rfile_wait_aborted_7_4
	atom		7
	branch_on_atom		7,2,rfile_wait_aborted_7_4
	bucket_entry_a		'fep#abnormal',rfile_wait_aborted_7_6
	bucket_entry_a		'fep#abort',rfile_wait_aborted_7_7
rfile_wait_aborted_7_6:
	collect_value		6
	collect_value		4
	get_atom		5,'fep#abnormal'
	execute		3,rfile_wait_reset_3_0
rfile_wait_aborted_7_7:
	collect_value		6
	collect_value		4
	get_atom		5,'fep#abort'
	execute		3,rfile_wait_reset_3_0
rfile_wait_aborted_7_4:
	suspend		rfile_wait_aborted_7_0
	module_entry		mpimos_file_device
	predicate		wfile_wait_reset,3
wfile_wait_reset_3_0:
	try_me_else		wfile_wait_reset_3_1
	jump_on_non_atom		1,wfile_wait_reset_3_3
	test_nil		1,wfile_wait_reset_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
wfile_wait_reset_3_3:
	is_vector		1,wfile_wait_reset_3_1
	jump_on_arity		1,6,wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_4
	table_entry		wfile_wait_reset_3_5
	table_entry		wfile_wait_reset_3_6
	table_entry		wfile_wait_reset_3_7
wfile_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	collect_value		3
	put_reused_func		1,1,close
	write_element_variable		1,1,3
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	get_list_value		2,5
	put_integer		1,2
	b_consume_resource		1
	put_values_dec		1,4,2
	execute		2,wait_close_2_0
wfile_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,end_of_file
	read_elements_inc		1,1,4,2
	get_atom		4,'fep#abnormal'
	put_reused_func		4,1,end_of_file
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,5
	execute		4,wfile_not_reset_4_0
wfile_wait_reset_3_6:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,3,wfile_wait_reset_3_1
	bucket_entry_a		next_attention,wfile_wait_reset_3_9
	bucket_entry_a		pathname,wfile_wait_reset_3_10
	bucket_entry_a		putb,wfile_wait_reset_3_11
wfile_wait_reset_3_9:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,next_attention
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,wfile_not_reset_4_0
wfile_wait_reset_3_10:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,pathname
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,wfile_not_reset_4_0
wfile_wait_reset_3_11:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,putb
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,wfile_not_reset_4_0
wfile_wait_reset_3_7:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,2,wfile_wait_reset_3_1
	bucket_entry_a		getb,wfile_wait_reset_3_13
	bucket_entry_a		reset,wfile_wait_reset_3_14
wfile_wait_reset_3_13:
	read_elements_inc		1,1,5,4
	put_value		4,3
	get_atom		7,'fep#abnormal'
	create_goal		3
	set_value		1,8
	set_value		2,2
	set_variable		3,7
	enqueue_goal		3,wfile_wait_reset_3_0
	put_reused_func		3,1,getb
	write_elements_inc		3,1,5,2
	write_element_void		3,3
	write_element_void		3,4
	put_atom		1,warning
	put_atom		2,not_read_mode
	put_value		5,7
	execute		5,file_error_5_0
wfile_wait_reset_3_14:
	read_elements_inc		1,1,5,4
	collect_value		6
	collect_vector		1
	put_value		6,3
	put_func		1,4,reset
	write_element_variable		1,1,4
	write_element_void		1,2
	write_element_variable		1,3,9
	get_list_val_var		2,10,1,3
	put_integer		1,2
	b_consume_resource		1
	put_value		1,8
	put_value		2,3
	put_value		3,5
	put_values_inc		5,6,2
	put_value		7,9
	execute		7,wfile_wait_status_7_0
wfile_wait_reset_3_1:
	otherwise		wfile_wait_reset_3_0
	collect_value		2
	put_value		5,1
	put_value		4,3
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,5
	put_void		5
	execute		5,file_error_5_0
wfile_wait_reset_3_23:
	suspend		wfile_wait_reset_3_0
	module_entry		mpimos_file_device
	predicate		wfile_not_reset,4
wfile_not_reset_4_0:
	put_value		6,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,5
	enqueue_goal		3,wfile_wait_reset_3_0
	put_atom		1,warning
	put_atom		2,file_not_reset
	put_value		3,4
	put_value		4,6
	execute		5,file_error_5_0
wfile_not_reset_4_1:
	suspend		wfile_not_reset_4_0
	module_entry		mpimos_file_device
	predicate		wfile,5
wfile_5_0:
	try_me_else		wfile_5_1
	wait_atom		3,'fep#abort'
	get_atom		4,'fep#abort'
	put_value		3,5
	execute		3,wfile_wait_reset_3_0
wfile_5_1:
	try_me_else		wfile_5_6
	wait		1
	wait_atom		3,'fep#abort'
	put_void		3
	execute		5,wfile_com_5_0
wfile_5_6:
	suspend		wfile_5_0
	module_entry		mpimos_file_device
	predicate		wfile_com,5
wfile_com_5_0:
	try_me_else		wfile_com_5_1
	jump_on_non_atom		1,wfile_com_5_3
	test_nil		1,wfile_com_5_1
	collect_value		5
	collect_value		4
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
wfile_com_5_3:
	is_vector		1,wfile_com_5_1
	jump_on_arity		1,6,wfile_com_5_1
	table_entry		wfile_com_5_1
	table_entry		wfile_com_5_1
	table_entry		wfile_com_5_4
	table_entry		wfile_com_5_5
	table_entry		wfile_com_5_6
	table_entry		wfile_com_5_7
wfile_com_5_4:
	read_element		1,0,6
	wait_atom		6,close
	read_element		1,1,6
	collect_value		5
	collect_value		4
	collect_value		3
	put_reused_func		1,1,close
	write_element_variable		1,1,3
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	get_list_value		2,4
	put_integer		1,2
	b_consume_resource		1
	put_value		1,6
	put_value		2,3
	execute		2,wait_close_2_0
wfile_com_5_5:
	read_element		1,0,6
	wait_atom		6,end_of_file
	read_elements_inc		1,1,6,2
	collect_vector		1
	put_func		1,2,end_of_file
	write_element_variable		1,1,9
	get_list_val_var		2,10,1,8
	put_integer		1,2
	b_consume_resource		1
	put_values_inc		1,7,2
	put_value		7,9
	execute		7,wfile_wait_status_7_0
wfile_com_5_6:
	read_element		1,0,6
	atom		6
	branch_on_atom		6,3,wfile_com_5_1
	bucket_entry_a		next_attention,wfile_com_5_9
	bucket_entry_a		pathname,wfile_com_5_10
	bucket_entry_a		putb,wfile_com_5_11
wfile_com_5_9:
	read_elements_inc		1,1,7,3
	collect_value		7
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		5,wfile_5_0
wfile_com_5_10:
	read_elements_inc		1,1,7,3
	collect_vector		1
	put_func		1,3,pathname
	write_element_variable		1,1,11
	write_element_variable		1,2,10
	get_list_val_var		2,12,1,6
	put_integer		1,2
	b_consume_resource		1
	put_value		1,9
	put_value		2,6
	put_values_inc		6,7,2
	put_values_dec		8,11,2
	execute		9,wfile_wait_pathname_9_0
wfile_com_5_11:
	read_elements_inc		1,1,7,3
	string		7
	g_string		7,10,11
	wait_integer		11,8
	collect_vector		1
	put_func		1,3,putb
	write_element_value		1,1,7
	write_element_variable		1,2,7
	get_list_val_var		2,10,1,6
	put_integer		1,3
	b_consume_resource		1
	put_value		1,9
	put_value		2,6
	put_value		6,8
	execute		7,wfile_wait_status_7_0
wfile_com_5_7:
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,wfile_com_5_1
	bucket_entry_a		getb,wfile_com_5_13
	bucket_entry_a		reset,wfile_com_5_14
wfile_com_5_13:
	read_elements_inc		1,1,7,4
	get_atom		9,'fep#abnormal'
	create_goal		5
	set_value		1,10
	set_values_inc		2,2,3
	set_variable		5,6
	enqueue_goal		5,wfile_5_0
	put_reused_func		3,1,getb
	write_elements_inc		3,1,7,2
	write_element_void		3,3
	write_element_void		3,4
	put_atom		1,warning
	put_atom		2,not_read_mode
	put_values_inc		4,5,2
	execute		5,file_error_5_0
wfile_com_5_14:
	read_elements_inc		1,1,7,4
	get_atom		9,'fep#abnormal'
	create_goal		5
	set_value		1,10
	set_values_inc		2,2,3
	set_variable		5,6
	enqueue_goal		5,wfile_5_0
	put_reused_func		3,1,reset
	write_elements_inc		3,1,7,2
	write_element_void		3,3
	write_element_void		3,4
	put_atom		1,warning
	put_atom		2,file_already_reset
	put_values_inc		4,5,2
	execute		5,file_error_5_0
wfile_com_5_1:
	otherwise		wfile_com_5_0
	collect_value		4
	collect_value		3
	collect_value		2
	put_value		3,1
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		4,5
	put_void		5
	execute		5,file_error_5_0
wfile_com_5_23:
	suspend		wfile_com_5_0
	module_entry		mpimos_file_device
	predicate		wfile_wait_status,7
wfile_wait_status_7_0:
	try_me_else		wfile_wait_status_7_1
	wait		7
	get_value		6,7
	execute		5,wfile_5_0
wfile_wait_status_7_1:
	suspend		wfile_wait_status_7_0
	module_entry		mpimos_file_device
	predicate		wfile_wait_pathname,9
wfile_wait_pathname_9_0:
	try_me_else		wfile_wait_pathname_9_1
	string		8
	wait_atom		9,'fep#normal'
	g_string		8,10,11
	wait_integer		11,8
	get_value		6,8
	get_atom		7,'fep#normal'
	execute		5,wfile_5_0
wfile_wait_pathname_9_1:
	suspend		wfile_wait_pathname_9_0
	module_entry		mpimos_file_device
	predicate		directory_wait_created,5
directory_wait_created_5_0:
	try_me_else		directory_wait_created_5_1
	atom		5
	branch_on_atom		5,2,directory_wait_created_5_1
	bucket_entry_a		'fep#abnormal',directory_wait_created_5_3
	bucket_entry_a		'fep#normal',directory_wait_created_5_4
directory_wait_created_5_3:
	collect_value		3
	collect_value		1
	get_atom		4,'fep#abnormal'
	get_nil		2
	proceed
directory_wait_created_5_4:
	put_integer		5,1
	b_consume_resource		5
	get_atom		4,'fep#normal'
	put_func		4,2,status
	write_element_value		4,1,3
	put_value		3,4
	execute		3,directory_3_0
directory_wait_created_5_1:
	suspend		directory_wait_created_5_0
	module_entry		mpimos_file_device
	predicate		directory,3
directory_3_0:
	try_me_else		directory_3_1
	jump_on_non_atom		1,directory_3_3
	test_nil		1,directory_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
directory_3_3:
	is_vector		1,directory_3_1
	jump_on_arity		1,6,directory_3_1
	table_entry		directory_3_1
	table_entry		directory_3_1
	table_entry		directory_3_1
	table_entry		directory_3_4
	table_entry		directory_3_5
	table_entry		directory_3_6
directory_3_4:
	read_element		1,0,4
	wait_atom		4,expunge
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_atom		4,'fep#normal'
	put_value		1,5
	execute		3,directory_3_0
directory_3_5:
	read_element		1,0,4
	atom		4
	hash_on_atom		4,4,directory_3_1
	bucket_entry_a		delete,directory_3_8
	bucket_entry_a		pathname,directory_3_9
	bucket_entry_a		purge,directory_3_10
	bucket_entry_a		undelete,directory_3_11
directory_3_8:
	read_elements_inc		1,1,5,3
	string		5
	g_string		5,8,9
	wait_integer		9,8
	collect_vector		1
	put_func		1,3,delete
	write_element_value		1,1,5
	write_element_variable		1,2,5
	get_list_val_var		2,8,1,4
	put_integer		1,3
	b_consume_resource		1
	put_value		1,7
	put_value		2,4
	put_value		4,6
	execute		5,directory_wait_delete_5_0
directory_3_9:
	read_elements_inc		1,1,5,3
	collect_vector		1
	put_func		1,3,pathname
	write_element_variable		1,1,9
	write_element_variable		1,2,8
	get_list_val_var		2,10,1,4
	put_integer		1,2
	b_consume_resource		1
	put_value		1,7
	put_value		2,4
	put_values_inc		4,5,2
	put_values_dec		6,9,2
	execute		7,directory_wait_pathname_7_0
directory_3_10:
	read_elements_inc		1,1,5,3
	string		5
	g_string		5,8,9
	wait_integer		9,8
	collect_value		5
	collect_vector		1
	get_atom		6,'fep#normal'
	put_value		1,7
	execute		3,directory_3_0
directory_3_11:
	read_elements_inc		1,1,5,3
	string		5
	g_string		5,8,9
	wait_integer		9,8
	collect_value		5
	collect_vector		1
	get_atom		6,'fep#normal'
	put_value		1,7
	execute		3,directory_3_0
directory_3_6:
	read_element		1,0,4
	atom		4
	branch_on_atom		4,2,directory_3_1
	bucket_entry_a		deleted,directory_3_13
	bucket_entry_a		listing,directory_3_14
directory_3_13:
	read_elements_inc		1,1,5,4
	string		5
	g_string		5,9,10
	wait_integer		10,8
	collect_vector		1
	put_func		1,4,deleted
	write_element_value		1,1,5
	write_element_variable		1,2,10
	write_element_variable		1,3,9
	get_list_val_var		2,5,1,4
	put_integer		1,2
	b_consume_resource		1
	put_value		1,8
	put_value		2,4
	put_values_inc		4,6,2
	put_values_dec		6,10,2
	execute		7,directory_wait_listing_7_0
directory_3_14:
	read_elements_inc		1,1,5,4
	string		5
	g_string		5,9,10
	wait_integer		10,8
	collect_vector		1
	put_func		1,4,listing
	write_element_value		1,1,5
	write_element_variable		1,2,10
	write_element_variable		1,3,9
	get_list_val_var		2,5,1,4
	put_integer		1,3
	b_consume_resource		1
	put_value		1,8
	put_value		2,4
	put_values_inc		4,6,2
	put_values_dec		6,10,2
	execute		7,directory_wait_listing_7_0
directory_3_1:
	otherwise		directory_3_0
	collect_value		2
	put_value		5,1
	put_value		4,3
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,5
	put_void		5
	execute		5,directory_error_5_0
directory_3_23:
	suspend		directory_3_0
	module_entry		mpimos_file_device
	predicate		directory_wait_pathname,7
directory_wait_pathname_7_0:
	try_me_else		directory_wait_pathname_7_1
	string		6
	wait_atom		7,'fep#normal'
	g_string		6,8,9
	wait_integer		9,8
	get_value		4,6
	get_atom		5,'fep#normal'
	execute		3,directory_3_0
directory_wait_pathname_7_1:
	suspend		directory_wait_pathname_7_0
	module_entry		mpimos_file_device
	predicate		directory_wait_listing,7
directory_wait_listing_7_0:
	try_me_else		directory_wait_listing_7_1
	wait		7
	get_value		5,7
	create_goal		3
	set_values_inc		1,1,2
	set_marked_value		3,3
	enqueue_goal		3,directory_3_0
	put_value		1,4
	put_value		2,6
	execute		3,listing_3_0
directory_wait_listing_7_1:
	suspend		directory_wait_listing_7_0
	module_entry		mpimos_file_device
	predicate		listing,3
listing_3_0:
	try_me_else		listing_3_1
	jump_on_non_atom		1,listing_3_3
	test_nil		1,listing_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
listing_3_3:
	check_vector		1,4,listing_3_1
	read_element		1,0,4
	wait_atom		4,next_file_name
	read_elements_inc		1,1,4,3
	collect_vector		1
	put_func		1,3,next_file_name
	write_element_variable		1,1,9
	write_element_variable		1,2,7
	get_list_val_var		2,10,1,8
	put_integer		1,2
	b_consume_resource		1
	put_value		1,6
	put_value		2,8
	put_value		6,9
	execute		7,listing_wait_name_7_0
listing_3_1:
	otherwise		listing_3_0
	collect_value		2
	put_value		5,1
	put_value		4,3
	put_atom		1,error
	put_atom		2,illegal_listing
	put_value		3,5
	put_void		5
	execute		5,directory_error_5_0
listing_3_9:
	suspend		listing_3_0
	module_entry		mpimos_file_device
	predicate		listing_wait_name,7
listing_wait_name_7_0:
	try_me_else		listing_wait_name_7_1
	jump_on_non_atom		6,listing_wait_name_7_3
	test_atom		6,'fep#nil',listing_wait_name_7_1
	wait_atom		7,'fep#end_of_file'
	get_atom		4,'fep#nil'
	get_atom		5,'fep#end_of_file'
	execute		3,listing_3_0
listing_wait_name_7_3:
	is_string		6,listing_wait_name_7_1
	wait_atom		7,'fep#normal'
	g_string		6,8,9
	wait_integer		9,8
	get_value		4,6
	get_atom		5,'fep#normal'
	execute		3,listing_3_0
listing_wait_name_7_1:
	try_me_else		listing_wait_name_7_5
	wait_atom		7,'fep#abnormal'
	collect_value		6
	collect_value		4
	get_atom		5,'fep#abnormal'
	execute		3,listing_3_0
listing_wait_name_7_5:
	suspend		listing_wait_name_7_0
	module_entry		mpimos_file_device
	predicate		directory_wait_delete,5
directory_wait_delete_5_0:
	try_me_else		directory_wait_delete_5_1
	wait		5
	get_value		4,5
	execute		3,directory_3_0
directory_wait_delete_5_1:
	suspend		directory_wait_delete_5_0
	module_entry		mpimos_file_device
	predicate		wait_close,2
wait_close_2_0:
	try_me_else		wait_close_2_1
	wait_atom		2,'fep#normal'
	get_atom		1,'fep#normal'
	proceed
wait_close_2_1:
	suspend		wait_close_2_0
	module_entry		mpimos_file_device
	predicate		file_error,3
file_error_3_0:
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
file_error_3_1:
	suspend		file_error_3_0
	module_entry		mpimos_file_device
	predicate		file_error,5
file_error_5_0:
	put_integer		6,1
	b_vector_element		4,6,4,6
	put_integer		7,2
	b_vector_element		6,7,6,7
	get_value		7,5
	create_goal		2
	set_value		1,1
	put_func		1,4,putt
	write_element_variable		1,1,9
	write_element_integer		1,2,10
	write_element_integer		1,3,5
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		7,1,5
	put_func		1,2,putb
	write_element_variable		1,1,8
	put_list_val_val		5,1,7
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		7,1,5
	put_func		1,2,putt
	write_element_value		1,1,6
	put_list_val_val		5,1,7
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_structured_constant		1,'$SCNST_5'
	put_list_val_val		5,1,4
	set_value		2,5
	enqueue_goal		2,raise_error_2_0
	create_goal		2
	set_value		1,3
	set_value		2,9
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,2
	put_value		2,8
	execute		2,message_2_0
file_error_5_1:
	suspend		file_error_5_0
	module_entry		mpimos_file_device
	predicate		directory_error,5
directory_error_5_0:
	put_integer		6,1
	b_vector_element		4,6,4,6
	get_value		6,5
	create_goal		2
	set_value		1,1
	put_func		1,4,putt
	write_element_variable		1,1,8
	write_element_integer		1,2,10
	write_element_integer		1,3,5
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	put_structured_constant		1,'$SCNST_6'
	put_list_val_val		6,1,5
	put_func		1,2,putb
	write_element_variable		1,1,7
	put_list_val_val		5,1,6
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_structured_constant		1,'$SCNST_8'
	put_list_val_val		5,1,4
	set_value		2,5
	enqueue_goal		2,raise_error_2_0
	create_goal		2
	set_value		1,3
	set_value		2,8
	enqueue_goal_external		mpimos_utility,freeze,2
	put_value		1,2
	put_value		2,7
	execute		2,message_2_0
directory_error_5_1:
	suspend		directory_error_5_0
	module_entry		mpimos_file_device
	predicate		raise_error,2
raise_error_2_0:
	put_integer		5,262144
	put_structured_constant		3,'$SCNST_9'
	put_func		4,2,do
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_10'
	put_list_val_val		4,3,2
	b_raise		5,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_2_1:
	suspend		raise_error_2_0
	module_entry		mpimos_file_device
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	atom		1
	hash_on_atom		1,6,message_2_1
	bucket_entry_a		file_already_reset,message_2_3
	bucket_entry_a		file_not_reset,message_2_4
	bucket_entry_a		illegal_command,message_2_5
	bucket_entry_a		illegal_listing,message_2_6
	bucket_entry_a		not_read_mode,message_2_7
	bucket_entry_a		not_write_mode,message_2_8
message_2_3:
	put_structured_constant		1,'$SCNST_11'
	get_value		2,1
	proceed
message_2_4:
	put_structured_constant		1,'$SCNST_12'
	get_value		2,1
	proceed
message_2_5:
	put_structured_constant		1,'$SCNST_13'
	get_value		2,1
	proceed
message_2_6:
	put_structured_constant		1,'$SCNST_14'
	get_value		2,1
	proceed
message_2_7:
	put_structured_constant		1,'$SCNST_15'
	get_value		2,1
	proceed
message_2_8:
	put_structured_constant		1,'$SCNST_16'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	begin_const_section		mpimos_file_device
'$SCNST_0_1':
	define_desc		11,1
	define_integer		2109216
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		11,2
	define_integer		1701603686
	define_integer		2112032
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_6':
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		3,1
	define_integer		539959337
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_7':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		27,1
	define_integer		44
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		19,2
	define_integer		1701603686
	define_integer		10272
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_8_1':
	define_desc		11,3
	define_integer		1701996900
	define_integer		1919906915
	define_integer		2629753
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_9_2':
	define_desc		27,1
	define_integer		46
'$SCNST_9_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_9_2'
'$SCNST_9_3':
	define_atom		nl
	define_atom		[]
'$SCNST_9_0':
	define_vector		'$SCNST_9_1'
	define_list		'$SCNST_9_3'
'$SCNST_9':
	define_list		'$SCNST_9_0'
'$SCNST_10_1':
	define_desc		27,4
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		32
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_0':
	define_desc		27,6
	define_integer		1701603686
	define_integer		544434464
	define_integer		1701997665
	define_integer		544826465
	define_integer		1702061426
	define_integer		116
'$SCNST_11':
	define_string		'$SCNST_11_0'
'$SCNST_12_0':
	define_desc		27,5
	define_integer		1701603686
	define_integer		544434464
	define_integer		544501614
	define_integer		1702061426
	define_integer		116
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_13_0':
	define_desc		11,4
	define_integer		1701604457
	define_integer		543973735
	define_integer		1835888483
	define_integer		6581857
'$SCNST_13':
	define_string		'$SCNST_13_0'
'$SCNST_14_0':
	define_desc		11,6
	define_integer		1701604457
	define_integer		543973735
	define_integer		1953720684
	define_integer		543649385
	define_integer		1835888483
	define_integer		6581857
'$SCNST_14':
	define_string		'$SCNST_14_0'
'$SCNST_15_0':
	define_desc		27,6
	define_integer		1701603686
	define_integer		544434464
	define_integer		544501614
	define_integer		1684104562
	define_integer		1685024032
	define_integer		101
'$SCNST_15':
	define_string		'$SCNST_15_0'
'$SCNST_16_0':
	define_desc		19,6
	define_integer		1701603686
	define_integer		544434464
	define_integer		544501614
	define_integer		1953067639
	define_integer		1869422693
	define_integer		25956
'$SCNST_16':
	define_string		'$SCNST_16_0'
