pdss_window_device:
	module		pdss_window_device
	entry		windows,1,windows_1_0
	module_entry		pdss_window_device
	predicate		windows,1
windows_1_0:
	try_me_else		windows_1_1
	put_integer		2,0
	g_device_dup_check		2
	execute		1,windows2_1_0
windows_1_1:
	suspend		windows_1_0
	module_entry		pdss_window_device
	predicate		windows2,1
windows2_1_0:
	try_me_else		windows2_1_1
	jump_on_non_atom		1,windows2_1_3
	test_nil		1,windows2_1_1
	proceed
windows2_1_3:
	is_vector		1,windows2_1_1
	jump_on_arity		1,9,windows2_1_1
	table_entry		windows2_1_1
	table_entry		windows2_1_1
	table_entry		windows2_1_1
	table_entry		windows2_1_1
	table_entry		windows2_1_4
	table_entry		windows2_1_5
	table_entry		windows2_1_1
	table_entry		windows2_1_1
	table_entry		windows2_1_6
windows2_1_4:
	read_element		1,0,2
	wait_atom		2,create
	read_elements_inc		1,1,2,3
	create_goal		1
	set_marked_value		1,4
	enqueue_goal		1,windows2_1_0
	put_reused_func		1,1,create
	write_elements_inc		1,1,2,3
	execute		1,unsupported_1_0
windows2_1_5:
	read_element		1,0,2
	wait_atom		2,create
	read_element		1,1,4
	read_element		1,2,2
	read_element		1,3,5
	read_element		1,4,3
	string		4
	g_string		4,6,7
	wait_integer		7,8
	collect_vector		1
	put_marked_value		1,4
	b_create_window		1,6,7,8
	create_goal		1
	set_value		1,3
	enqueue_goal		1,windows2_1_0
	put_value		1,2
	put_values_dec		2,8,2
	execute		6,window_wait_created_6_0
windows2_1_6:
	read_element		1,0,2
	wait_atom		2,get_max_size
	read_elements_inc		1,1,2,7
	integer		2
	integer		3
	string		4
	g_string		4,2,3
	wait_integer		3,8
	collect_value		4
	collect_vector		1
	get_integer		5,80
	get_integer		6,40
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		1,windows2_1_0
windows2_1_1:
	suspend		windows2_1_0
	module_entry		pdss_window_device
	predicate		window_wait_created,6
window_wait_created_6_0:
	try_me_else		window_wait_created_6_1
	integer		6
	jump_on_integer		6,2,window_wait_created_6_1
	table_entry		window_wait_created_6_3
	table_entry		window_wait_created_6_4
window_wait_created_6_3:
	get_atom		5,'fep#normal'
	execute		4,window_wait_reset_4_0
window_wait_created_6_4:
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		5,'fep#abnormal'
	proceed
window_wait_created_6_1:
	suspend		window_wait_created_6_0
	module_entry		pdss_window_device
	predicate		window_wait_reset,4
window_wait_reset_4_0:
	try_me_else		window_wait_reset_4_1
	jump_on_non_atom		1,window_wait_reset_4_3
	test_nil		1,window_wait_reset_4_1
	integer		2
	collect_value		4
	collect_value		3
	b_remove_window		2,1
	proceed
window_wait_reset_4_3:
	is_vector		1,window_wait_reset_4_1
	jump_on_arity		1,6,window_wait_reset_4_1
	table_entry		window_wait_reset_4_1
	table_entry		window_wait_reset_4_1
	table_entry		window_wait_reset_4_4
	table_entry		window_wait_reset_4_1
	table_entry		window_wait_reset_4_1
	table_entry		window_wait_reset_4_5
window_wait_reset_4_4:
	read_element		1,0,5
	wait_atom		5,close
	read_element		1,1,5
	integer		2
	collect_value		4
	collect_value		3
	collect_vector		1
	get_atom		5,'fep#normal'
	b_remove_window		2,1
	proceed
window_wait_reset_4_5:
	read_element		1,0,5
	wait_atom		5,reset
	read_elements_inc		1,1,5,4
	collect_vector		1
	put_values_inc		9,2,3
	get_atom		7,'fep#normal'
	put_value		1,8
	put_values_inc		2,5,2
	put_values_inc		4,9,3
	execute		6,window_6_0
window_wait_reset_4_1:
	suspend		window_wait_reset_4_0
	module_entry		pdss_window_device
	predicate		window,6
window_6_0:
	try_me_else		window_6_1
	wait_atom		2,'fep#abort'
	collect_value		3
	put_values_inc		2,4,3
	execute		4,window_wait_reset_4_0
window_6_1:
	try_me_else		window_6_3
	wait_list_var_var		5,7,8
	wait		7
	collect_list		5
	get_value		3,7
	put_void		3
	put_value		5,8
	execute		6,window_6_0
window_6_3:
	try_me_else		window_6_9
	jump_on_non_atom		1,window_6_11
	test_nil		1,window_6_9
	integer		4
	collect_value		6
	collect_value		5
	collect_value		3
	collect_value		2
	b_remove_window		4,1
	proceed
window_6_11:
	is_vector		1,window_6_9
	jump_on_arity		1,8,window_6_9
	table_entry		window_6_9
	table_entry		window_6_9
	table_entry		window_6_12
	table_entry		window_6_13
	table_entry		window_6_14
	table_entry		window_6_15
	table_entry		window_6_16
	table_entry		window_6_17
window_6_12:
	read_element		1,0,7
	wait_atom		7,close
	read_element		1,1,7
	integer		4
	collect_value		6
	collect_value		5
	collect_value		3
	collect_value		2
	collect_vector		1
	get_atom		7,'fep#normal'
	b_remove_window		4,1
	proceed
window_6_13:
	read_element		1,0,7
	atom		7
	hash_on_atom		7,7,window_6_9
	bucket_entry_a		activate,window_6_19
	bucket_entry_a		beep,window_6_20
	bucket_entry_a		clear,window_6_21
	bucket_entry_a		deactivate,window_6_22
	bucket_entry_a		flush,window_6_23
	bucket_entry_a		hide,window_6_24
	bucket_entry_a		show,window_6_25
window_6_19:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	b_show_window		4,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_20:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	put_integer		1,7
	b_write_char		4,1,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_21:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	put_integer		1,12
	b_write_char		4,1,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_22:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	b_hide_window		4,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_23:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		6,window_6_0
window_6_24:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	b_hide_window		4,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_25:
	read_elements_inc		1,1,8,2
	integer		4
	collect_vector		1
	b_show_window		4,10,4
	put_value		1,9
	put_value		7,8
	put_value		8,10
	execute		8,window_wait_status_8_0
window_6_14:
	read_element		1,0,7
	atom		7
	hash_on_atom		7,14,window_6_9
	bucket_entry_a		get_font,window_6_27
	bucket_entry_a		get_title,window_6_28
	bucket_entry_a		getc,window_6_29
	bucket_entry_a		getl,window_6_30
	bucket_entry_a		next_attention,window_6_31
	bucket_entry_a		putb,window_6_32
	bucket_entry_a		putc,window_6_33
	bucket_entry_a		putl,window_6_34
	bucket_entry_a		reshape,window_6_35
	bucket_entry_a		select_buffer,window_6_36
	bucket_entry_a		set_font,window_6_37
	bucket_entry_a		set_position,window_6_38
	bucket_entry_a		set_size,window_6_39
	bucket_entry_a		set_title,window_6_40
window_6_27:
	read_elements_inc		1,1,8,3
	create_goal		6
	set_marked_value		1,10
	set_values_inc		2,2,5
	enqueue_goal		6,window_6_0
	put_reused_func		1,1,get_font
	write_elements_inc		1,1,8,3
	execute		1,unsupported_1_0
window_6_28:
	read_elements_inc		1,1,8,3
	collect_vector		1
	put_marked_value		6,6
	get_value		6,8
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		6,window_6_0
window_6_29:
	read_elements_inc		1,1,8,3
	integer		4
	collect_vector		1
	put_marked_value		1,4
	b_read_char		1,11,12,1
	put_value		1,10
	put_values_inc		7,8,2
	put_values_inc		9,11,2
	execute		10,window_wait_char_10_0
window_6_30:
	read_elements_inc		1,1,8,3
	integer		4
	collect_vector		1
	put_marked_value		1,4
	b_read_line		1,11,12,1
	put_value		1,10
	put_values_inc		7,8,2
	put_values_inc		9,11,2
	execute		10,window_wait_line_10_0
window_6_31:
	read_elements_inc		1,1,8,3
	collect_value		3
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	put_value		3,8
	execute		6,window_6_0
window_6_32:
	read_elements_inc		1,1,8,3
	integer		4
	string		8
	g_string		8,11,12
	wait_integer		12,8
	collect_vector		1
	b_write_buffer		4,8,8,4
	put_value		1,10
	put_value		7,9
	execute		8,window_wait_status_8_0
window_6_33:
	read_elements_inc		1,1,8,3
	integer		4
	collect_vector		1
	b_write_char		4,8,8,4
	put_value		1,10
	put_value		7,9
	execute		8,window_wait_status_8_0
window_6_34:
	read_elements_inc		1,1,8,3
	integer		4
	string		8
	g_string		8,11,12
	wait_integer		12,8
	collect_vector		1
	b_write_line		4,8,8,4
	put_value		1,10
	put_value		7,9
	execute		8,window_wait_status_8_0
window_6_35:
	read_element		1,1,8
	wait_atom		8,'fep#manipulator'
	read_elements_inc		1,2,8,2
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		6,window_6_0
window_6_36:
	read_elements_inc		1,1,8,3
	string		8
	g_string		8,11,12
	wait_integer		12,8
	create_goal		6
	set_marked_value		1,10
	set_values_inc		2,2,5
	enqueue_goal		6,window_6_0
	put_reused_func		1,1,select_buffer
	write_elements_inc		1,1,8,3
	execute		1,unsupported_1_0
window_6_37:
	read_elements_inc		1,1,8,3
	string		8
	g_string		8,11,12
	wait_integer		12,8
	collect_value		8
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		6,window_6_0
window_6_38:
	read_element		1,1,8
	wait_atom		8,'fep#manipulator'
	read_elements_inc		1,2,8,2
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		6,window_6_0
window_6_39:
	read_element		1,1,8
	wait_atom		8,'fep#manipulator'
	read_elements_inc		1,2,8,2
	collect_vector		1
	get_atom		8,'fep#normal'
	put_value		1,9
	execute		6,window_6_0
window_6_40:
	read_elements_inc		1,1,8,3
	string		8
	g_string		8,11,12
	wait_integer		12,8
	collect_value		8
	collect_vector		1
	get_atom		9,'fep#normal'
	put_value		1,10
	execute		6,window_6_0
window_6_15:
	read_element		1,0,7
	atom		7
	hash_on_atom		7,6,window_6_9
	bucket_entry_a		get_inside_size,window_6_42
	bucket_entry_a		get_position,window_6_43
	bucket_entry_a		getb,window_6_44
	bucket_entry_a		gettkn,window_6_45
	bucket_entry_a		set_inside_size,window_6_46
	bucket_entry_a		set_position,window_6_47
window_6_42:
	read_elements_inc		1,1,8,4
	collect_vector		1
	get_integer		8,80
	get_integer		9,20
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		6,window_6_0
window_6_43:
	read_elements_inc		1,1,8,4
	collect_vector		1
	get_integer		8,0
	get_integer		9,0
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		6,window_6_0
window_6_44:
	read_elements_inc		1,1,8,4
	integer		4
	collect_vector		1
	put_marked_value		1,4
	b_read_buffer		1,8,12,13,1
	put_value		1,11
	put_values_inc		7,9,2
	put_values_inc		9,12,2
	execute		10,window_wait_buffer_10_0
window_6_45:
	read_elements_inc		1,1,8,4
	integer		4
	collect_vector		1
	put_marked_value		1,4
	b_read_token		1,12,13,14,1
	put_value		1,11
	put_values_inc		7,8,3
	put_values_inc		10,12,3
	execute		12,window_wait_token_12_0
window_6_46:
	read_elements_inc		1,1,8,4
	integer		8
	integer		9
	collect_vector		1
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		6,window_6_0
window_6_47:
	read_elements_inc		1,1,8,4
	integer		8
	integer		9
	collect_vector		1
	get_atom		10,'fep#normal'
	put_value		1,11
	execute		6,window_6_0
window_6_16:
	read_element		1,0,7
	wait_atom		7,putt
	read_elements_inc		1,1,7,5
	integer		4
	collect_vector		1
	b_write_term		4,7,8,9,8,4
	put_value		1,11
	put_value		7,10
	execute		8,window_wait_status_8_0
window_6_17:
	read_element		1,0,7
	wait_atom		7,reshape
	read_elements_inc		1,1,7,6
	integer		7
	integer		8
	integer		9
	integer		10
	collect_vector		1
	get_atom		11,'fep#normal'
	put_value		1,12
	execute		6,window_6_0
window_6_9:
	suspend		window_6_0
	module_entry		pdss_window_device
	predicate		window_wait_status,8
window_wait_status_8_0:
	try_me_else		window_wait_status_8_1
	wait_integer		8,0
	get_atom		7,'fep#normal'
	execute		6,window_6_0
window_wait_status_8_1:
	try_me_else		window_wait_status_8_3
	put_integer		9,0
	g_diff		8,9
	collect_value		8
	get_atom		7,'fep#abnormal'
	execute		6,window_6_0
window_wait_status_8_3:
	suspend		window_wait_status_8_0
	module_entry		pdss_window_device
	predicate		window_wait_char,10
window_wait_char_10_0:
	try_me_else		window_wait_char_10_1
	wait_atom		2,'fep#abort'
	collect_value		10
	collect_value		9
	collect_value		7
	collect_value		3
	b_abort_read_command		4,2,3
	get_atom		8,'fep#abort'
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,window_wait_reset_4_0
window_wait_char_10_1:
	try_me_else		window_wait_char_10_3
	wait_list_var_var		5,11,12
	wait		11
	collect_list		5
	get_value		3,11
	put_void		3
	put_value		5,12
	execute		10,window_wait_char_10_0
window_wait_char_10_3:
	try_me_else		window_wait_char_10_9
	integer		10
	jump_on_integer		10,4,window_wait_char_10_9
	table_entry		window_wait_char_10_11
	table_entry		window_wait_char_10_9
	table_entry		window_wait_char_10_9
	table_entry		window_wait_char_10_12
window_wait_char_10_11:
	get_value		7,9
	get_atom		8,'fep#normal'
	execute		6,window_6_0
window_wait_char_10_12:
	collect_value		9
	collect_value		7
	get_atom		8,'fep#end_of_file'
	execute		6,window_6_0
window_wait_char_10_9:
	suspend		window_wait_char_10_0
	module_entry		pdss_window_device
	predicate		window_wait_line,10
window_wait_line_10_0:
	try_me_else		window_wait_line_10_1
	wait_atom		2,'fep#abort'
	collect_value		10
	collect_value		9
	collect_value		7
	collect_value		3
	b_abort_read_command		4,2,3
	get_atom		8,'fep#abort'
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,window_wait_reset_4_0
window_wait_line_10_1:
	try_me_else		window_wait_line_10_3
	wait_list_var_var		5,11,12
	wait		11
	collect_list		5
	get_value		3,11
	put_void		3
	put_value		5,12
	execute		10,window_wait_line_10_0
window_wait_line_10_3:
	try_me_else		window_wait_line_10_9
	integer		10
	jump_on_integer		10,4,window_wait_line_10_9
	table_entry		window_wait_line_10_11
	table_entry		window_wait_line_10_9
	table_entry		window_wait_line_10_9
	table_entry		window_wait_line_10_12
window_wait_line_10_11:
	get_value		7,9
	get_atom		8,'fep#normal'
	execute		6,window_6_0
window_wait_line_10_12:
	collect_value		9
	collect_value		7
	get_atom		8,'fep#end_of_file'
	execute		6,window_6_0
window_wait_line_10_9:
	suspend		window_wait_line_10_0
	module_entry		pdss_window_device
	predicate		window_wait_buffer,10
window_wait_buffer_10_0:
	try_me_else		window_wait_buffer_10_1
	wait_atom		2,'fep#abort'
	collect_value		10
	collect_value		9
	collect_value		7
	collect_value		3
	b_abort_read_command		4,2,3
	get_atom		8,'fep#abort'
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,window_wait_reset_4_0
window_wait_buffer_10_1:
	try_me_else		window_wait_buffer_10_3
	wait_list_var_var		5,11,12
	wait		11
	collect_list		5
	get_value		3,11
	put_void		3
	put_value		5,12
	execute		10,window_wait_buffer_10_0
window_wait_buffer_10_3:
	try_me_else		window_wait_buffer_10_9
	integer		10
	jump_on_integer		10,4,window_wait_buffer_10_9
	table_entry		window_wait_buffer_10_11
	table_entry		window_wait_buffer_10_9
	table_entry		window_wait_buffer_10_9
	table_entry		window_wait_buffer_10_12
window_wait_buffer_10_11:
	get_value		7,9
	get_atom		8,'fep#normal'
	execute		6,window_6_0
window_wait_buffer_10_12:
	collect_value		9
	collect_value		7
	get_atom		8,'fep#abnormal'
	execute		6,window_6_0
window_wait_buffer_10_9:
	suspend		window_wait_buffer_10_0
	module_entry		pdss_window_device
	predicate		window_wait_token,12
window_wait_token_12_0:
	try_me_else		window_wait_token_12_1
	wait_atom		2,'fep#abort'
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		8
	collect_value		7
	collect_value		3
	b_abort_read_command		4,2,3
	get_atom		9,'fep#abort'
	put_value		2,3
	put_values_inc		3,5,2
	execute		4,window_wait_reset_4_0
window_wait_token_12_1:
	try_me_else		window_wait_token_12_3
	wait_list_var_var		5,13,14
	wait		13
	collect_list		5
	get_value		3,13
	put_void		3
	put_value		5,14
	execute		12,window_wait_token_12_0
window_wait_token_12_3:
	try_me_else		window_wait_token_12_9
	integer		12
	jump_on_integer		12,5,window_wait_token_12_9
	table_entry		window_wait_token_12_11
	table_entry		window_wait_token_12_9
	table_entry		window_wait_token_12_9
	table_entry		window_wait_token_12_12
	table_entry		window_wait_token_12_13
window_wait_token_12_11:
	get_value		7,10
	get_value		8,11
	get_atom		9,'fep#normal'
	execute		6,window_6_0
window_wait_token_12_12:
	collect_value		11
	collect_value		10
	collect_value		8
	collect_value		7
	get_atom		9,'fep#end_of_file'
	execute		6,window_6_0
window_wait_token_12_13:
	collect_value		11
	collect_value		10
	collect_value		8
	collect_value		7
	get_atom		9,'fep#end_of_file'
	execute		6,window_6_0
window_wait_token_12_9:
	suspend		window_wait_token_12_0
	module_entry		pdss_window_device
	predicate		unsupported,1
unsupported_1_0:
	put_integer		3,1
	put_atom		4,'ERROR'
	put_func		2,2,unsupported_command
	write_element_value		2,1,1
	b_raise		3,4,2
	proceed
unsupported_1_1:
	suspend		unsupported_1_0
