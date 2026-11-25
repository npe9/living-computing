mpimos_window_device:
	module		mpimos_window_device
	entry		windows,1,windows_1_0
	entry		window_request,3,window_request_3_0
	module_entry		mpimos_window_device
	predicate		windows,1
windows_1_0:
	put_integer		2,65536
	put_atom		3,device_window
	b_raise		2,3,1
	put_integer		1,2
	b_consume_resource		1
	proceed
windows_1_1:
	suspend		windows_1_0
	module_entry		mpimos_window_device
	predicate		window_request,3
window_request_3_0:
	try_me_else		window_request_3_1
	jump_on_non_atom		1,window_request_3_3
	test_nil		1,window_request_3_1
	collect_value		2
	get_nil		3
	put_integer		1,1
	b_consume_resource		1
	proceed
window_request_3_3:
	is_vector		1,window_request_3_1
	jump_on_arity		1,9,window_request_3_1
	table_entry		window_request_3_1
	table_entry		window_request_3_1
	table_entry		window_request_3_1
	table_entry		window_request_3_1
	table_entry		window_request_3_4
	table_entry		window_request_3_5
	table_entry		window_request_3_1
	table_entry		window_request_3_1
	table_entry		window_request_3_6
window_request_3_4:
	read_element		1,0,4
	wait_atom		4,create
	read_elements_inc		1,1,4,3
	get_atom		5,'fep#abnormal'
	create_goal		3
	set_value		1,6
	set_values_inc		2,2,2
	enqueue_goal		3,window_request_3_0
	put_reused_func		3,1,create
	write_element_value		3,1,4
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,unsupported
	execute		3,window_error_3_0
window_request_3_5:
	read_element		1,0,4
	wait_atom		4,create
	read_elements_inc		1,1,4,4
	string		4
	g_string		4,8,9
	wait_integer		9,8
	put_reused_func		1,1,create
	write_element_variable		1,1,10
	write_element_marked_value		1,2,4
	write_element_variable		1,3,9
	write_element_marked_value		1,4,2
	put_func		8,3,:
	write_element_atom		8,1,window_manager
	write_element_value		8,2,1
	get_list_val_var		3,11,8,1
	put_integer		3,10
	b_consume_resource		3
	create_goal		3
	set_value		1,7
	set_values_dec		2,2,2
	enqueue_goal		3,window_request_3_0
	put_value		1,5
	put_value		2,10
	put_value		3,4
	put_value		4,6
	put_value		5,9
	execute		5,window_wait_created_5_0
window_request_3_6:
	read_element		1,0,4
	wait_atom		4,get_max_size
	read_elements_inc		1,1,4,7
	integer		4
	integer		5
	string		6
	g_string		6,4,5
	wait_integer		5,8
	collect_value		6
	collect_vector		1
	get_integer		7,80
	get_integer		8,40
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		3,window_request_3_0
window_request_3_1:
	otherwise		window_request_3_0
	collect_value		2
	put_value		4,1
	get_nil		3
	put_integer		1,1
	b_consume_resource		1
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,4
	execute		3,window_error_3_0
window_request_3_11:
	suspend		window_request_3_0
	module_entry		mpimos_window_device
	predicate		window_wait_created,5
window_wait_created_5_0:
	try_me_else		window_wait_created_5_1
	atom		5
	branch_on_atom		5,2,window_wait_created_5_1
	bucket_entry_a		'fep#abnormal',window_wait_created_5_3
	bucket_entry_a		'fep#normal',window_wait_created_5_4
window_wait_created_5_3:
	collect_value		3
	collect_value		1
	get_atom		4,'fep#abnormal'
	get_nil		2
	proceed
window_wait_created_5_4:
	put_integer		5,1
	b_consume_resource		5
	get_atom		4,'fep#normal'
	put_func		4,2,status
	write_element_value		4,1,3
	put_value		3,4
	execute		3,window_wait_reset_3_0
window_wait_created_5_1:
	suspend		window_wait_created_5_0
	module_entry		mpimos_window_device
	predicate		window_wait_reset,3
window_wait_reset_3_0:
	try_me_else		window_wait_reset_3_1
	jump_on_non_atom		1,window_wait_reset_3_3
	test_nil		1,window_wait_reset_3_1
	collect_value		3
	get_nil		2
	put_integer		1,2
	b_consume_resource		1
	proceed
window_wait_reset_3_3:
	is_vector		1,window_wait_reset_3_1
	jump_on_arity		1,8,window_wait_reset_3_1
	table_entry		window_wait_reset_3_1
	table_entry		window_wait_reset_3_1
	table_entry		window_wait_reset_3_4
	table_entry		window_wait_reset_3_5
	table_entry		window_wait_reset_3_6
	table_entry		window_wait_reset_3_7
	table_entry		window_wait_reset_3_1
	table_entry		window_wait_reset_3_8
window_wait_reset_3_4:
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
window_wait_reset_3_5:
	read_element		1,0,4
	atom		4
	hash_on_atom		4,7,window_wait_reset_3_1
	bucket_entry_a		activate,window_wait_reset_3_10
	bucket_entry_a		beep,window_wait_reset_3_11
	bucket_entry_a		clear,window_wait_reset_3_12
	bucket_entry_a		deactivate,window_wait_reset_3_13
	bucket_entry_a		flush,window_wait_reset_3_14
	bucket_entry_a		hide,window_wait_reset_3_15
	bucket_entry_a		show,window_wait_reset_3_16
window_wait_reset_3_10:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,activate
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_11:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,beep
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_12:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,clear
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_13:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,deactivate
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_14:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,flush
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_15:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,hide
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_16:
	read_elements_inc		1,1,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,show
	write_element_void		4,1
	write_element_void		4,2
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_6:
	read_element		1,0,4
	atom		4
	hash_on_atom		4,11,window_wait_reset_3_1
	bucket_entry_a		get_font,window_wait_reset_3_18
	bucket_entry_a		get_title,window_wait_reset_3_19
	bucket_entry_a		getl,window_wait_reset_3_20
	bucket_entry_a		next_attention,window_wait_reset_3_21
	bucket_entry_a		putb,window_wait_reset_3_22
	bucket_entry_a		reshape,window_wait_reset_3_23
	bucket_entry_a		select_buffer,window_wait_reset_3_24
	bucket_entry_a		set_font,window_wait_reset_3_25
	bucket_entry_a		set_position,window_wait_reset_3_26
	bucket_entry_a		set_size,window_wait_reset_3_27
	bucket_entry_a		set_title,window_wait_reset_3_28
window_wait_reset_3_18:
	read_elements_inc		1,1,5,3
	put_value		4,3
	get_atom		6,'fep#abnormal'
	create_goal		3
	set_value		1,7
	set_value		2,2
	set_variable		3,6
	enqueue_goal		3,window_wait_reset_3_0
	put_reused_func		3,1,get_font
	write_element_value		3,1,5
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,unsupported
	put_value		5,6
	execute		5,window_error_5_0
window_wait_reset_3_19:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,get_title
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_20:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,getl
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_21:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,next_attention
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_22:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,putb
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_23:
	read_element		1,1,5
	wait_atom		5,'fep#manipulator'
	read_elements_inc		1,2,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,reshape
	write_element_atom		4,1,'fep#manipulator'
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_24:
	read_elements_inc		1,1,5,3
	put_value		4,3
	get_atom		6,'fep#abnormal'
	create_goal		3
	set_value		1,7
	set_value		2,2
	set_variable		3,6
	enqueue_goal		3,window_wait_reset_3_0
	put_reused_func		3,1,select_buffer
	write_element_value		3,1,5
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,unsupported
	put_value		5,6
	execute		5,window_error_5_0
window_wait_reset_3_25:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,set_font
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_26:
	read_element		1,1,5
	wait_atom		5,'fep#manipulator'
	read_elements_inc		1,2,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,set_position
	write_element_atom		4,1,'fep#manipulator'
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_27:
	read_element		1,1,5
	wait_atom		5,'fep#manipulator'
	read_elements_inc		1,2,5,2
	get_atom		5,'fep#abnormal'
	put_reused_func		4,1,set_size
	write_element_atom		4,1,'fep#manipulator'
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,6
	execute		4,window_not_reset_4_0
window_wait_reset_3_28:
	read_elements_inc		1,1,5,3
	get_atom		6,'fep#abnormal'
	put_reused_func		4,1,set_title
	write_element_value		4,1,5
	write_element_void		4,2
	write_element_void		4,3
	put_value		1,7
	execute		4,window_not_reset_4_0
window_wait_reset_3_7:
	read_element		1,0,4
	atom		4
	hash_on_atom		4,5,window_wait_reset_3_1
	bucket_entry_a		get_inside_size,window_wait_reset_3_30
	bucket_entry_a		get_position,window_wait_reset_3_31
	bucket_entry_a		reset,window_wait_reset_3_32
	bucket_entry_a		set_inside_size,window_wait_reset_3_33
	bucket_entry_a		set_position,window_wait_reset_3_34
window_wait_reset_3_30:
	read_elements_inc		1,1,5,4
	get_atom		7,'fep#abnormal'
	put_reused_func		4,1,get_inside_size
	write_elements_inc		4,1,5,2
	write_element_void		4,3
	write_element_void		4,4
	put_value		1,8
	execute		4,window_not_reset_4_0
window_wait_reset_3_31:
	read_elements_inc		1,1,5,4
	get_atom		7,'fep#abnormal'
	put_reused_func		4,1,get_position
	write_elements_inc		4,1,5,2
	write_element_void		4,3
	write_element_void		4,4
	put_value		1,8
	execute		4,window_not_reset_4_0
window_wait_reset_3_32:
	read_elements_inc		1,1,5,2
	read_elements_dec		1,3,8,2
	collect_vector		1
	put_value		11,3
	put_func		1,4,reset
	write_element_variable		1,1,4
	write_element_variable		1,2,10
	write_element_variable		1,3,9
	get_list_val_var		2,12,1,3
	put_integer		1,2
	b_consume_resource		1
	put_value		1,7
	put_value		2,3
	put_value		3,5
	put_value		5,6
	put_values_inc		6,10,2
	execute		9,window_wait_status_9_0
window_wait_reset_3_33:
	read_elements_inc		1,1,5,4
	get_atom		7,'fep#abnormal'
	put_reused_func		4,1,set_insize_size
	write_elements_inc		4,1,5,2
	write_element_void		4,3
	write_element_void		4,4
	put_value		1,8
	execute		4,window_not_reset_4_0
window_wait_reset_3_34:
	read_elements_inc		1,1,5,4
	get_atom		7,'fep#abnormal'
	put_reused_func		4,1,set_position
	write_elements_inc		4,1,5,2
	write_element_void		4,3
	write_element_void		4,4
	put_value		1,8
	execute		4,window_not_reset_4_0
window_wait_reset_3_8:
	read_element		1,0,4
	wait_atom		4,reshape
	read_elements_inc		1,1,4,6
	get_atom		8,'fep#abnormal'
	put_reused_func		8,1,reshape
	write_elements_inc		8,1,4,4
	write_element_void		8,5
	write_element_void		8,6
	put_value		1,9
	put_value		4,8
	execute		4,window_not_reset_4_0
window_wait_reset_3_1:
	otherwise		window_wait_reset_3_0
	collect_value		2
	put_value		5,1
	put_value		4,3
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		3,5
	put_void		5
	execute		5,window_error_5_0
window_wait_reset_3_45:
	suspend		window_wait_reset_3_0
	module_entry		mpimos_window_device
	predicate		window_not_reset,4
window_not_reset_4_0:
	put_value		6,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,5
	enqueue_goal		3,window_wait_reset_3_0
	put_atom		1,warning
	put_atom		2,window_not_reset
	put_value		3,4
	put_value		4,6
	execute		5,window_error_5_0
window_not_reset_4_1:
	suspend		window_not_reset_4_0
	module_entry		mpimos_window_device
	predicate		window,7
window_7_0:
	try_me_else		window_7_1
	wait_atom		3,'fep#abort'
	collect_value		6
	collect_value		5
	get_atom		4,'fep#abort'
	put_integer		3,2
	b_consume_resource		3
	put_value		3,7
	execute		3,window_wait_reset_3_0
window_7_1:
	try_me_else		window_7_3
	wait		6
	put_integer		8,2
	b_consume_resource		8
	get_value		5,6
	put_void		5
	put_void		6
	execute		7,window_7_0
window_7_3:
	try_me_else		window_7_8
	wait		1
	execute		7,window_com_7_0
window_7_8:
	suspend		window_7_0
	module_entry		mpimos_window_device
	predicate		window_com,7
window_com_7_0:
	try_me_else		window_com_7_1
	jump_on_non_atom		1,window_com_7_3
	test_nil		1,window_com_7_1
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	put_integer		1,2
	b_consume_resource		1
	get_nil		2
	proceed
window_com_7_3:
	is_vector		1,window_com_7_1
	jump_on_arity		1,8,window_com_7_1
	table_entry		window_com_7_1
	table_entry		window_com_7_1
	table_entry		window_com_7_4
	table_entry		window_com_7_5
	table_entry		window_com_7_6
	table_entry		window_com_7_7
	table_entry		window_com_7_1
	table_entry		window_com_7_8
window_com_7_4:
	read_element		1,0,8
	wait_atom		8,close
	read_element		1,1,8
	collect_value		7
	collect_value		6
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
	put_value		1,8
	put_value		2,3
	execute		2,wait_close_2_0
window_com_7_5:
	read_element		1,0,8
	atom		8
	hash_on_atom		8,7,window_com_7_1
	bucket_entry_a		activate,window_com_7_10
	bucket_entry_a		beep,window_com_7_11
	bucket_entry_a		clear,window_com_7_12
	bucket_entry_a		deactivate,window_com_7_13
	bucket_entry_a		flush,window_com_7_14
	bucket_entry_a		hide,window_com_7_15
	bucket_entry_a		show,window_com_7_16
window_com_7_10:
	read_elements_inc		1,1,9,2
	collect_vector		1
	put_func		1,2,show
	write_element_variable		1,1,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_11:
	read_elements_inc		1,1,9,2
	put_integer		8,1
	put_integer		11,8
	b_new_string		11,8,11
	put_marked_value		8,11
	put_integer		12,0
	put_integer		13,7
	b_set_string_element		8,12,13,8
	put_reused_func		1,1,putb
	write_element_value		1,1,8
	write_element_value		1,2,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_12:
	read_elements_inc		1,1,9,2
	put_integer		8,1
	put_integer		11,8
	b_new_string		11,8,11
	put_marked_value		8,11
	put_integer		12,0
	put_integer		13,12
	b_set_string_element		8,12,13,8
	put_reused_func		1,1,putb
	write_element_value		1,1,8
	write_element_value		1,2,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_13:
	read_elements_inc		1,1,9,2
	collect_vector		1
	put_func		1,2,hide
	write_element_variable		1,1,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_14:
	read_elements_inc		1,1,9,2
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		7,window_7_0
window_com_7_15:
	read_elements_inc		1,1,9,2
	collect_vector		1
	put_func		1,2,hide
	write_element_variable		1,1,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_16:
	read_elements_inc		1,1,9,2
	collect_vector		1
	put_func		1,2,show
	write_element_variable		1,1,11
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,10
	put_value		2,8
	put_value		8,9
	put_value		9,11
	execute		9,window_wait_status_9_0
window_com_7_6:
	read_element		1,0,8
	atom		8
	hash_on_atom		8,11,window_com_7_1
	bucket_entry_a		get_font,window_com_7_18
	bucket_entry_a		get_title,window_com_7_19
	bucket_entry_a		getl,window_com_7_20
	bucket_entry_a		next_attention,window_com_7_21
	bucket_entry_a		putb,window_com_7_22
	bucket_entry_a		reshape,window_com_7_23
	bucket_entry_a		select_buffer,window_com_7_24
	bucket_entry_a		set_font,window_com_7_25
	bucket_entry_a		set_position,window_com_7_26
	bucket_entry_a		set_size,window_com_7_27
	bucket_entry_a		set_title,window_com_7_28
window_com_7_18:
	read_elements_inc		1,1,9,3
	get_atom		10,'fep#abnormal'
	create_goal		7
	set_value		1,11
	set_values_inc		2,2,5
	set_variable		7,5
	enqueue_goal		7,window_7_0
	put_reused_func		3,1,get_font
	write_element_value		3,1,9
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,unsupported
	put_value		4,7
	execute		5,window_error_5_0
window_com_7_19:
	read_elements_inc		1,1,9,3
	collect_vector		1
	put_integer		1,1
	b_vector_element		7,1,1,7
	get_value		1,9
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		7,window_7_0
window_com_7_20:
	read_elements_inc		1,1,9,3
	collect_vector		1
	put_func		1,3,getl
	write_element_variable		1,1,13
	write_element_variable		1,2,12
	get_list_val_var		2,14,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,11
	put_value		2,8
	put_values_inc		8,9,2
	put_values_dec		10,13,2
	execute		11,window_wait_line_11_0
window_com_7_21:
	read_elements_inc		1,1,9,3
	collect_value		6
	collect_value		5
	collect_vector		1
	put_func		1,3,next_attention
	write_element_variable		1,1,6
	write_element_variable		1,2,12
	get_list_val_var		2,8,1,5
	put_integer		1,2
	b_consume_resource		1
	put_value		1,11
	put_value		2,5
	put_value		5,9
	put_value		8,10
	put_value		9,12
	execute		9,window_wait_status_9_0
window_com_7_22:
	read_elements_inc		1,1,9,3
	collect_vector		1
	put_func		1,3,putb
	write_element_value		1,1,9
	write_element_variable		1,2,9
	get_list_val_var		2,12,1,8
	put_integer		1,3
	b_consume_resource		1
	put_value		1,11
	put_value		2,8
	put_value		8,10
	execute		9,window_wait_status_9_0
window_com_7_23:
	read_element		1,1,9
	wait_atom		9,'fep#manipulator'
	read_elements_inc		1,2,9,2
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		7,window_7_0
window_com_7_24:
	read_elements_inc		1,1,9,3
	string		9
	g_string		9,12,13
	wait_integer		13,8
	get_atom		10,'fep#abnormal'
	create_goal		7
	set_value		1,11
	set_values_inc		2,2,5
	set_variable		7,5
	enqueue_goal		7,window_7_0
	put_reused_func		3,1,select_buffer
	write_element_value		3,1,9
	write_element_void		3,2
	write_element_void		3,3
	put_atom		1,warning
	put_atom		2,unsupported
	put_value		4,7
	execute		5,window_error_5_0
window_com_7_25:
	read_elements_inc		1,1,9,3
	string		9
	g_string		9,12,13
	wait_integer		13,8
	collect_value		9
	collect_vector		1
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		7,window_7_0
window_com_7_26:
	read_element		1,1,9
	wait_atom		9,'fep#manipulator'
	read_elements_inc		1,2,9,2
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		7,window_7_0
window_com_7_27:
	read_element		1,1,9
	wait_atom		9,'fep#manipulator'
	read_elements_inc		1,2,9,2
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		7,window_7_0
window_com_7_28:
	read_elements_inc		1,1,9,3
	string		9
	g_string		9,12,13
	wait_integer		13,8
	collect_value		9
	collect_vector		1
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		7,window_7_0
window_com_7_7:
	read_element		1,0,8
	atom		8
	hash_on_atom		8,5,window_com_7_1
	bucket_entry_a		get_inside_size,window_com_7_30
	bucket_entry_a		get_position,window_com_7_31
	bucket_entry_a		reset,window_com_7_32
	bucket_entry_a		set_inside_size,window_com_7_33
	bucket_entry_a		set_position,window_com_7_34
window_com_7_30:
	read_elements_inc		1,1,9,4
	collect_vector		1
	get_integer		9,80
	get_integer		10,20
	get_atom		11,'fep#normal'
	put_value		1,12
	execute		7,window_7_0
window_com_7_31:
	read_elements_inc		1,1,9,4
	collect_vector		1
	get_integer		9,0
	get_integer		10,0
	get_atom		11,'fep#normal'
	put_value		1,12
	execute		7,window_7_0
window_com_7_32:
	read_elements_inc		1,1,9,4
	get_atom		11,'fep#abnormal'
	create_goal		7
	set_value		1,12
	set_values_inc		2,2,5
	set_variable		7,5
	enqueue_goal		7,window_7_0
	put_reused_func		3,1,reset
	write_elements_inc		3,1,9,2
	write_element_void		3,3
	write_element_void		3,4
	put_atom		1,warning
	put_atom		2,window_already_reset
	put_value		4,7
	execute		5,window_error_5_0
window_com_7_33:
	read_elements_inc		1,1,9,4
	integer		9
	integer		10
	collect_vector		1
	get_atom		11,'fep#normal'
	put_value		1,12
	execute		7,window_7_0
window_com_7_34:
	read_elements_inc		1,1,9,4
	integer		9
	integer		10
	collect_vector		1
	get_atom		11,'fep#normal'
	put_value		1,12
	execute		7,window_7_0
window_com_7_8:
	read_element		1,0,8
	wait_atom		8,reshape
	read_elements_inc		1,1,8,6
	integer		8
	integer		9
	integer		10
	integer		11
	collect_vector		1
	get_atom		12,'fep#normal'
	put_value		1,13
	execute		7,window_7_0
window_com_7_1:
	otherwise		window_com_7_0
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	put_value		3,1
	put_atom		1,error
	put_atom		2,illegal_command
	put_value		4,7
	put_void		5
	execute		5,window_error_5_0
window_com_7_45:
	suspend		window_com_7_0
	module_entry		mpimos_window_device
	predicate		window_wait_status,9
window_wait_status_9_0:
	try_me_else		window_wait_status_9_1
	wait		9
	get_atom		8,'fep#normal'
	execute		7,window_7_0
window_wait_status_9_1:
	suspend		window_wait_status_9_0
	module_entry		mpimos_window_device
	predicate		window_wait_line,11
window_wait_line_11_0:
	try_me_else		window_wait_line_11_1
	wait_atom		3,'fep#abort'
	collect_value		6
	collect_value		5
	get_atom		4,'fep#abort'
	put_integer		3,2
	b_consume_resource		3
	put_values_inc		3,7,5
	execute		7,window_wait_aborted_7_0
window_wait_line_11_1:
	try_me_else		window_wait_line_11_3
	wait		6
	put_integer		12,2
	b_consume_resource		12
	get_value		5,6
	put_void		5
	put_void		6
	execute		11,window_wait_line_11_0
window_wait_line_11_3:
	try_me_else		window_wait_line_11_8
	string		10
	wait_atom		11,'fep#normal'
	g_string		10,12,13
	wait_integer		13,8
	get_value		8,10
	get_atom		9,'fep#normal'
	execute		7,window_7_0
window_wait_line_11_8:
	try_me_else		window_wait_line_11_11
	wait_atom		11,'fep#abnormal'
	collect_value		10
	collect_value		8
	get_atom		9,'fep#abnormal'
	execute		7,window_7_0
window_wait_line_11_11:
	suspend		window_wait_line_11_0
	module_entry		mpimos_window_device
	predicate		window_wait_aborted,7
window_wait_aborted_7_0:
	try_me_else		window_wait_aborted_7_1
	string		6
	wait_atom		7,'fep#normal'
	g_string		6,8,9
	wait_integer		9,8
	get_value		4,6
	get_atom		5,'fep#normal'
	execute		3,window_wait_reset_3_0
window_wait_aborted_7_1:
	try_me_else		window_wait_aborted_7_4
	atom		7
	branch_on_atom		7,2,window_wait_aborted_7_4
	bucket_entry_a		'fep#abnormal',window_wait_aborted_7_6
	bucket_entry_a		'fep#abort',window_wait_aborted_7_7
window_wait_aborted_7_6:
	collect_value		6
	collect_value		4
	get_atom		5,'fep#abnormal'
	execute		3,window_wait_reset_3_0
window_wait_aborted_7_7:
	collect_value		6
	collect_value		4
	get_atom		5,'fep#abort'
	execute		3,window_wait_reset_3_0
window_wait_aborted_7_4:
	suspend		window_wait_aborted_7_0
	module_entry		mpimos_window_device
	predicate		wait_close,2
wait_close_2_0:
	try_me_else		wait_close_2_1
	wait_atom		2,'fep#normal'
	get_atom		1,'fep#normal'
	proceed
wait_close_2_1:
	suspend		wait_close_2_0
	module_entry		mpimos_window_device
	predicate		window_error,3
window_error_3_0:
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
window_error_3_1:
	suspend		window_error_3_0
	module_entry		mpimos_window_device
	predicate		window_error,5
window_error_5_0:
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
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		6,1,5
	put_func		1,2,putb
	write_element_variable		1,1,7
	put_list_val_val		5,1,6
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		6,1,5
	put_func		1,2,putt
	write_element_value		1,1,4
	put_list_val_val		4,1,6
	put_structured_constant		1,'$SCNST_4'
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
window_error_5_1:
	suspend		window_error_5_0
	module_entry		mpimos_window_device
	predicate		raise_error,2
raise_error_2_0:
	put_integer		5,262144
	put_structured_constant		3,'$SCNST_5'
	put_func		4,2,do
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_6'
	put_list_val_val		4,3,2
	b_raise		5,1,4
	put_integer		1,5
	b_consume_resource		1
	proceed
raise_error_2_1:
	suspend		raise_error_2_0
	module_entry		mpimos_window_device
	predicate		message,2
message_2_0:
	try_me_else		message_2_1
	atom		1
	hash_on_atom		1,4,message_2_1
	bucket_entry_a		illegal_command,message_2_3
	bucket_entry_a		unsupported,message_2_4
	bucket_entry_a		window_already_reset,message_2_5
	bucket_entry_a		window_not_reset,message_2_6
message_2_3:
	put_structured_constant		1,'$SCNST_7'
	get_value		2,1
	proceed
message_2_4:
	put_structured_constant		1,'$SCNST_8'
	get_value		2,1
	proceed
message_2_5:
	put_structured_constant		1,'$SCNST_9'
	get_value		2,1
	proceed
message_2_6:
	put_structured_constant		1,'$SCNST_10'
	get_value		2,1
	proceed
message_2_1:
	suspend		message_2_0
	begin_const_section		mpimos_window_device
'$SCNST_0_1':
	define_desc		11,1
	define_integer		2112032
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_2':
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		27,3
	define_integer		1684957559
	define_integer		790656879
	define_integer		32
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_3_1':
	define_desc		3,1
	define_integer		539959337
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		3,2
	define_integer		1684957559
	define_integer		673216367
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_2':
	define_desc		27,1
	define_integer		46
'$SCNST_5_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_2'
'$SCNST_5_3':
	define_atom		nl
	define_atom		[]
'$SCNST_5_0':
	define_vector		'$SCNST_5_1'
	define_list		'$SCNST_5_3'
'$SCNST_5':
	define_list		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		27,4
	define_integer		540950078
	define_integer		1869771365
	define_integer		1852383346
	define_integer		32
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
'$SCNST_8_0':
	define_desc		11,7
	define_integer		1970499189
	define_integer		1919905904
	define_integer		543450484
	define_integer		1835888483
	define_integer		543452769
	define_integer		1344305506
	define_integer		5460804
'$SCNST_8':
	define_string		'$SCNST_8_0'
'$SCNST_9_0':
	define_desc		11,6
	define_integer		1684957559
	define_integer		1763735407
	define_integer		1818304627
	define_integer		1684104562
	define_integer		1701978233
	define_integer		7628147
'$SCNST_9':
	define_string		'$SCNST_9_0'
'$SCNST_10_0':
	define_desc		11,5
	define_integer		1684957559
	define_integer		1763735407
	define_integer		1869488243
	define_integer		1701978228
	define_integer		7628147
'$SCNST_10':
	define_string		'$SCNST_10_0'
