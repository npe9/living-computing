pdss_file_device:
	module		pdss_file_device
	entry		files,1,files_1_0
	module_entry		pdss_file_device
	predicate		files,1
files_1_0:
	try_me_else		files_1_1
	put_integer		2,1
	g_device_dup_check		2
	execute		1,files2_1_0
files_1_1:
	suspend		files_1_0
	module_entry		pdss_file_device
	predicate		files2,1
files2_1_0:
	try_me_else		files2_1_1
	jump_on_non_atom		1,files2_1_3
	test_nil		1,files2_1_1
	proceed
files2_1_3:
	is_vector		1,files2_1_1
	jump_on_arity		1,7,files2_1_1
	table_entry		files2_1_1
	table_entry		files2_1_1
	table_entry		files2_1_1
	table_entry		files2_1_1
	table_entry		files2_1_1
	table_entry		files2_1_4
	table_entry		files2_1_5
files2_1_4:
	read_element		1,0,2
	wait_atom		2,directory
	read_elements_inc		1,1,2,4
	string		2
	g_string		2,6,7
	wait_integer		7,8
	collect_vector		1
	put_marked_value		1,2
	b_test_directory		1,6
	create_goal		1
	set_value		1,5
	enqueue_goal		1,files2_1_0
	put_value		1,3
	put_value		3,4
	put_value		4,6
	execute		4,wait_test_directory_4_0
files2_1_5:
	read_element		1,0,2
	wait_atom		2,open
	read_elements_inc		1,1,3,2
	read_element		1,3,2
	read_elements_inc		1,4,5,2
	string		3
	g_string		3,7,8
	wait_integer		8,8
	collect_vector		1
	b_create_file		7,8
	create_goal		1
	set_value		1,6
	enqueue_goal		1,files2_1_0
	put_value		1,2
	put_value		2,8
	put_value		6,7
	execute		6,file_wait_created_6_0
files2_1_1:
	suspend		files2_1_0
	module_entry		pdss_file_device
	predicate		file_wait_created,6
file_wait_created_6_0:
	try_me_else		file_wait_created_6_1
	integer		2
	atom		4
	branch_on_atom		4,3,file_wait_created_6_1
	bucket_entry_a		'fep#append',file_wait_created_6_4
	bucket_entry_a		'fep#read',file_wait_created_6_5
	bucket_entry_a		'fep#write',file_wait_created_6_6
file_wait_created_6_4:
	wait_integer		6,0
	put_marked_value		4,3
	put_integer		6,2
	b_open_file		2,4,6,6,2
	put_values_inc		4,5,2
	execute		5,wfile_wait_open_5_0
file_wait_created_6_5:
	wait_integer		6,0
	put_marked_value		4,3
	put_integer		6,0
	b_open_file		2,4,6,6,2
	put_values_inc		4,5,2
	execute		5,rfile_wait_open_5_0
file_wait_created_6_6:
	wait_integer		6,0
	put_marked_value		4,3
	put_integer		6,1
	b_open_file		2,4,6,6,2
	put_values_inc		4,5,2
	execute		5,wfile_wait_open_5_0
file_wait_created_6_1:
	otherwise		file_wait_created_6_0
	try_me_else		file_wait_created_6_10
	integer		6
	jump_on_integer		6,2,file_wait_created_6_10
	table_entry		file_wait_created_6_12
	table_entry		file_wait_created_6_13
file_wait_created_6_12:
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		5,'fep#abnormal'
	b_remove_file		2,1
	proceed
file_wait_created_6_13:
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		5,'fep#abnormal'
	proceed
file_wait_created_6_10:
	suspend		file_wait_created_6_0
	module_entry		pdss_file_device
	predicate		rfile_wait_open,5
rfile_wait_open_5_0:
	try_me_else		rfile_wait_open_5_1
	integer		5
	jump_on_integer		5,3,rfile_wait_open_5_1
	table_entry		rfile_wait_open_5_3
	table_entry		rfile_wait_open_5_1
	table_entry		rfile_wait_open_5_4
rfile_wait_open_5_3:
	get_atom		4,'fep#normal'
	execute		3,rfile_wait_reset_3_0
rfile_wait_open_5_4:
	collect_value		3
	collect_value		1
	get_atom		4,'fep#abnormal'
	b_remove_file		2,1
	proceed
rfile_wait_open_5_1:
	suspend		rfile_wait_open_5_0
	module_entry		pdss_file_device
	predicate		rfile_wait_reset,3
rfile_wait_reset_3_0:
	try_me_else		rfile_wait_reset_3_1
	jump_on_non_atom		1,rfile_wait_reset_3_3
	test_nil		1,rfile_wait_reset_3_1
	integer		2
	collect_value		3
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
rfile_wait_reset_3_3:
	is_vector		1,rfile_wait_reset_3_1
	jump_on_arity		1,6,rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_4
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_1
	table_entry		rfile_wait_reset_3_5
rfile_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	integer		2
	collect_value		3
	collect_vector		1
	get_atom		4,'fep#normal'
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
rfile_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,reset
	read_elements_inc		1,1,4,4
	collect_value		5
	collect_vector		1
	put_value		5,2
	put_value		8,3
	get_atom		6,'fep#normal'
	put_value		1,7
	put_values_inc		2,4,2
	put_value		4,8
	execute		4,rfile_4_0
rfile_wait_reset_3_1:
	suspend		rfile_wait_reset_3_0
	module_entry		pdss_file_device
	predicate		rfile,4
rfile_4_0:
	try_me_else		rfile_4_1
	wait_atom		2,'fep#abort'
	put_values_inc		2,3,2
	execute		3,rfile_wait_reset_3_0
rfile_4_1:
	try_me_else		rfile_4_6
	jump_on_non_atom		1,rfile_4_8
	test_nil		1,rfile_4_6
	integer		3
	collect_value		4
	collect_value		2
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
rfile_4_8:
	is_vector		1,rfile_4_6
	jump_on_arity		1,6,rfile_4_6
	table_entry		rfile_4_6
	table_entry		rfile_4_6
	table_entry		rfile_4_9
	table_entry		rfile_4_10
	table_entry		rfile_4_11
	table_entry		rfile_4_12
rfile_4_9:
	read_element		1,0,5
	wait_atom		5,close
	read_element		1,1,5
	integer		3
	collect_value		4
	collect_value		2
	collect_vector		1
	get_atom		5,'fep#normal'
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
rfile_4_10:
	read_element		1,0,5
	wait_atom		5,end_of_file
	read_elements_inc		1,1,5,2
	collect_vector		1
	get_atom		5,'fep#no'
	put_value		1,6
	execute		4,rfile_4_0
rfile_4_11:
	read_element		1,0,5
	atom		5
	hash_on_atom		5,4,rfile_4_6
	bucket_entry_a		getc,rfile_4_14
	bucket_entry_a		getl,rfile_4_15
	bucket_entry_a		next_attention,rfile_4_16
	bucket_entry_a		pathname,rfile_4_17
rfile_4_14:
	read_elements_inc		1,1,6,3
	integer		3
	collect_vector		1
	b_read_char		3,9,10,3
	put_value		1,8
	put_values_inc		5,6,2
	put_values_inc		7,9,2
	execute		8,rfile_wait_char_8_0
rfile_4_15:
	read_elements_inc		1,1,6,3
	integer		3
	collect_vector		1
	b_read_line		3,9,10,3
	put_value		1,8
	put_values_inc		5,6,2
	put_values_inc		7,9,2
	execute		8,rfile_wait_line_8_0
rfile_4_16:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,rfile_4_0
rfile_4_17:
	read_elements_inc		1,1,6,3
	collect_vector		1
	put_marked_value		4,4
	get_value		4,6
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,rfile_4_0
rfile_4_12:
	read_element		1,0,5
	atom		5
	branch_on_atom		5,2,rfile_4_6
	bucket_entry_a		getb,rfile_4_19
	bucket_entry_a		gettkn,rfile_4_20
rfile_4_19:
	read_elements_inc		1,1,6,4
	integer		3
	collect_vector		1
	b_read_buffer		3,6,10,11,3
	put_value		1,9
	put_values_inc		5,7,2
	put_values_inc		7,10,2
	execute		8,rfile_wait_buffer_8_0
rfile_4_20:
	read_elements_inc		1,1,6,4
	integer		3
	collect_vector		1
	b_read_token		3,10,11,12,3
	put_value		1,9
	put_values_inc		5,6,3
	put_values_inc		8,10,3
	execute		10,rfile_wait_token_10_0
rfile_4_6:
	suspend		rfile_4_0
	module_entry		pdss_file_device
	predicate		rfile_wait_char,8
rfile_wait_char_8_0:
	try_me_else		rfile_wait_char_8_1
	wait_atom		2,'fep#abort'
	collect_value		8
	collect_value		7
	collect_value		5
	get_atom		6,'fep#abort'
	put_values_inc		2,3,2
	execute		3,rfile_wait_reset_3_0
rfile_wait_char_8_1:
	try_me_else		rfile_wait_char_8_6
	integer		8
	jump_on_integer		8,4,rfile_wait_char_8_6
	table_entry		rfile_wait_char_8_8
	table_entry		rfile_wait_char_8_6
	table_entry		rfile_wait_char_8_6
	table_entry		rfile_wait_char_8_9
rfile_wait_char_8_8:
	get_value		5,7
	get_atom		6,'fep#normal'
	execute		4,rfile_4_0
rfile_wait_char_8_9:
	collect_value		7
	get_atom		5,'fep#nil'
	get_atom		6,'fep#end_of_file'
	execute		4,eof2_4_0
rfile_wait_char_8_6:
	suspend		rfile_wait_char_8_0
	module_entry		pdss_file_device
	predicate		rfile_wait_line,8
rfile_wait_line_8_0:
	try_me_else		rfile_wait_line_8_1
	wait_atom		2,'fep#abort'
	collect_value		8
	collect_value		7
	collect_value		5
	get_atom		6,'fep#abort'
	put_values_inc		2,3,2
	execute		3,rfile_wait_reset_3_0
rfile_wait_line_8_1:
	try_me_else		rfile_wait_line_8_6
	string		7
	wait_integer		8,3
	try_me_else		rfile_wait_line_8_9
	g_string		7,9,10
	put_integer		10,1
	g_not_less_than		9,10
	get_value		5,7
	get_atom		6,'fep#normal'
	execute		4,eof_4_0
rfile_wait_line_8_9:
	try_me_else		rfile_wait_line_8_6
	g_string		7,10,9
	wait_integer		10,0
	collect_value		7
	get_atom		5,'fep#nil'
	get_atom		6,'fep#end_of_file'
	execute		4,eof2_4_0
rfile_wait_line_8_6:
	try_me_else		rfile_wait_line_8_10
	wait_integer		8,0
	get_value		5,7
	get_atom		6,'fep#normal'
	execute		4,rfile_4_0
rfile_wait_line_8_10:
	suspend		rfile_wait_line_8_0
	module_entry		pdss_file_device
	predicate		rfile_wait_buffer,8
rfile_wait_buffer_8_0:
	try_me_else		rfile_wait_buffer_8_1
	wait_atom		2,'fep#abort'
	collect_value		8
	collect_value		7
	collect_value		5
	get_atom		6,'fep#abort'
	put_values_inc		2,3,2
	execute		3,rfile_wait_reset_3_0
rfile_wait_buffer_8_1:
	try_me_else		rfile_wait_buffer_8_6
	string		7
	wait_integer		8,3
	try_me_else		rfile_wait_buffer_8_9
	g_string		7,9,10
	put_integer		10,1
	g_not_less_than		9,10
	get_value		5,7
	get_atom		6,'fep#normal'
	execute		4,eof_4_0
rfile_wait_buffer_8_9:
	try_me_else		rfile_wait_buffer_8_6
	g_string		7,10,9
	wait_integer		10,0
	collect_value		7
	get_atom		5,'fep#nil'
	get_atom		6,'fep#end_of_file'
	execute		4,eof2_4_0
rfile_wait_buffer_8_6:
	try_me_else		rfile_wait_buffer_8_10
	wait_integer		8,0
	get_value		5,7
	get_atom		6,'fep#normal'
	execute		4,rfile_4_0
rfile_wait_buffer_8_10:
	suspend		rfile_wait_buffer_8_0
	module_entry		pdss_file_device
	predicate		rfile_wait_token,10
rfile_wait_token_10_0:
	try_me_else		rfile_wait_token_10_1
	wait_atom		2,'fep#abort'
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		6
	collect_value		5
	get_atom		7,'fep#abort'
	put_values_inc		2,3,2
	execute		3,rfile_wait_reset_3_0
rfile_wait_token_10_1:
	try_me_else		rfile_wait_token_10_6
	list		8
	read_car		8,11
	try_me_else		rfile_wait_token_10_8
	wait_atom		11,end
	read_cdr		8,12
	wait_nil		12
	wait_integer		10,3
	collect_list		8
	collect_value		9
	get_atom		5,'fep#nil'
	get_integer		6,0
	get_atom		7,'fep#end_of_file'
	execute		4,eof2_4_0
rfile_wait_token_10_8:
	read_cdr		8,12
	try_me_else		rfile_wait_token_10_6
	list		12
	wait_integer		10,3
	read_car		12,10
	read_cdr		12,13
	put_reused_list_val_val		8,8,10,13
	put_reused_list_val_val		10,12,11,8
	get_list_value		5,10
	get_value		6,9
	get_atom		7,'fep#normal'
	execute		4,eof_4_0
rfile_wait_token_10_6:
	try_me_else		rfile_wait_token_10_11
	integer		10
	jump_on_integer		10,5,rfile_wait_token_10_11
	table_entry		rfile_wait_token_10_13
	table_entry		rfile_wait_token_10_11
	table_entry		rfile_wait_token_10_11
	table_entry		rfile_wait_token_10_11
	table_entry		rfile_wait_token_10_14
rfile_wait_token_10_13:
	get_value		5,8
	get_value		6,9
	get_atom		7,'fep#normal'
	execute		4,rfile_4_0
rfile_wait_token_10_14:
	get_value		5,8
	get_value		6,9
	get_atom		7,'fep#abnormal'
	execute		4,eof_4_0
rfile_wait_token_10_11:
	suspend		rfile_wait_token_10_0
	module_entry		pdss_file_device
	predicate		eof_wait_reset,3
eof_wait_reset_3_0:
	try_me_else		eof_wait_reset_3_1
	jump_on_non_atom		1,eof_wait_reset_3_3
	test_nil		1,eof_wait_reset_3_1
	integer		2
	collect_value		3
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
eof_wait_reset_3_3:
	is_vector		1,eof_wait_reset_3_1
	jump_on_arity		1,6,eof_wait_reset_3_1
	table_entry		eof_wait_reset_3_1
	table_entry		eof_wait_reset_3_1
	table_entry		eof_wait_reset_3_4
	table_entry		eof_wait_reset_3_1
	table_entry		eof_wait_reset_3_1
	table_entry		eof_wait_reset_3_5
eof_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	integer		2
	collect_value		3
	collect_vector		1
	get_atom		4,'fep#normal'
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
eof_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,reset
	read_elements_inc		1,1,4,4
	collect_value		5
	collect_vector		1
	put_value		5,2
	put_value		8,3
	get_atom		6,'fep#normal'
	put_value		1,7
	put_values_inc		2,4,2
	put_value		4,8
	execute		4,eof_4_0
eof_wait_reset_3_1:
	suspend		eof_wait_reset_3_0
	module_entry		pdss_file_device
	predicate		eof,4
eof_4_0:
	try_me_else		eof_4_1
	wait_atom		2,'fep#abort'
	put_values_inc		2,3,2
	execute		3,eof_wait_reset_3_0
eof_4_1:
	try_me_else		eof_4_6
	jump_on_non_atom		1,eof_4_8
	test_nil		1,eof_4_6
	integer		3
	collect_value		4
	collect_value		2
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
eof_4_8:
	is_vector		1,eof_4_6
	jump_on_arity		1,6,eof_4_6
	table_entry		eof_4_6
	table_entry		eof_4_6
	table_entry		eof_4_9
	table_entry		eof_4_10
	table_entry		eof_4_11
	table_entry		eof_4_12
eof_4_9:
	read_element		1,0,5
	wait_atom		5,close
	read_element		1,1,5
	integer		3
	collect_value		4
	collect_value		2
	collect_vector		1
	get_atom		5,'fep#normal'
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
eof_4_10:
	read_element		1,0,5
	wait_atom		5,end_of_file
	read_elements_inc		1,1,5,2
	collect_vector		1
	get_atom		5,'fep#yes'
	put_value		1,6
	execute		4,eof_4_0
eof_4_11:
	read_element		1,0,5
	atom		5
	hash_on_atom		5,4,eof_4_6
	bucket_entry_a		getc,eof_4_14
	bucket_entry_a		getl,eof_4_15
	bucket_entry_a		next_attention,eof_4_16
	bucket_entry_a		pathname,eof_4_17
eof_4_14:
	read_elements_inc		1,1,6,3
	collect_vector		1
	get_atom		6,'fep#nil'
	get_atom		7,'fep#end_of_file'
	put_value		1,8
	execute		4,eof2_4_0
eof_4_15:
	read_elements_inc		1,1,6,3
	collect_vector		1
	get_atom		6,'fep#nil'
	get_atom		7,'fep#end_of_file'
	put_value		1,8
	execute		4,eof2_4_0
eof_4_16:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,eof_4_0
eof_4_17:
	read_elements_inc		1,1,6,3
	collect_vector		1
	put_marked_value		4,4
	get_value		4,6
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,eof_4_0
eof_4_12:
	read_element		1,0,5
	atom		5
	branch_on_atom		5,2,eof_4_6
	bucket_entry_a		getb,eof_4_19
	bucket_entry_a		gettkn,eof_4_20
eof_4_19:
	read_elements_inc		1,1,6,4
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#nil'
	get_atom		8,'fep#end_of_file'
	put_value		1,9
	execute		4,eof2_4_0
eof_4_20:
	read_elements_inc		1,1,6,4
	collect_vector		1
	get_atom		6,'fep#nil'
	get_integer		7,0
	get_atom		8,'fep#end_of_file'
	put_value		1,9
	execute		4,eof2_4_0
eof_4_6:
	suspend		eof_4_0
	module_entry		pdss_file_device
	predicate		eof2_wait_reset,3
eof2_wait_reset_3_0:
	try_me_else		eof2_wait_reset_3_1
	jump_on_non_atom		1,eof2_wait_reset_3_3
	test_nil		1,eof2_wait_reset_3_1
	integer		2
	collect_value		3
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
eof2_wait_reset_3_3:
	is_vector		1,eof2_wait_reset_3_1
	jump_on_arity		1,6,eof2_wait_reset_3_1
	table_entry		eof2_wait_reset_3_1
	table_entry		eof2_wait_reset_3_1
	table_entry		eof2_wait_reset_3_4
	table_entry		eof2_wait_reset_3_1
	table_entry		eof2_wait_reset_3_1
	table_entry		eof2_wait_reset_3_5
eof2_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	integer		2
	collect_value		3
	collect_vector		1
	get_atom		4,'fep#normal'
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
eof2_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,reset
	read_elements_inc		1,1,4,4
	collect_value		5
	collect_vector		1
	put_value		5,2
	put_value		8,3
	get_atom		6,'fep#normal'
	put_value		1,7
	put_values_inc		2,4,2
	put_value		4,8
	execute		4,eof2_4_0
eof2_wait_reset_3_1:
	suspend		eof2_wait_reset_3_0
	module_entry		pdss_file_device
	predicate		eof2,4
eof2_4_0:
	try_me_else		eof2_4_1
	wait_atom		2,'fep#abort'
	put_values_inc		2,3,2
	execute		3,eof2_wait_reset_3_0
eof2_4_1:
	try_me_else		eof2_4_6
	jump_on_non_atom		1,eof2_4_8
	test_nil		1,eof2_4_6
	integer		3
	collect_value		4
	collect_value		2
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
eof2_4_8:
	is_vector		1,eof2_4_6
	jump_on_arity		1,6,eof2_4_6
	table_entry		eof2_4_6
	table_entry		eof2_4_6
	table_entry		eof2_4_9
	table_entry		eof2_4_10
	table_entry		eof2_4_11
	table_entry		eof2_4_12
eof2_4_9:
	read_element		1,0,5
	wait_atom		5,close
	read_element		1,1,5
	integer		3
	collect_value		4
	collect_value		2
	collect_vector		1
	get_atom		5,'fep#normal'
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
eof2_4_10:
	read_element		1,0,5
	wait_atom		5,end_of_file
	read_elements_inc		1,1,5,2
	collect_vector		1
	get_atom		5,'fep#yes'
	put_value		1,6
	execute		4,eof2_4_0
eof2_4_11:
	read_element		1,0,5
	atom		5
	hash_on_atom		5,4,eof2_4_6
	bucket_entry_a		getc,eof2_4_14
	bucket_entry_a		getl,eof2_4_15
	bucket_entry_a		next_attention,eof2_4_16
	bucket_entry_a		pathname,eof2_4_17
eof2_4_14:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#abnormal'
	put_value		1,8
	execute		4,eof2_4_0
eof2_4_15:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#abnormal'
	put_value		1,8
	execute		4,eof2_4_0
eof2_4_16:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,eof2_4_0
eof2_4_17:
	read_elements_inc		1,1,6,3
	collect_vector		1
	put_marked_value		4,4
	get_value		4,6
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,eof2_4_0
eof2_4_12:
	read_element		1,0,5
	atom		5
	branch_on_atom		5,2,eof2_4_6
	bucket_entry_a		getb,eof2_4_19
	bucket_entry_a		gettkn,eof2_4_20
eof2_4_19:
	read_elements_inc		1,1,6,4
	collect_value		7
	collect_value		6
	collect_vector		1
	get_atom		8,'fep#abnormal'
	put_value		1,9
	execute		4,eof2_4_0
eof2_4_20:
	read_elements_inc		1,1,6,4
	collect_value		7
	collect_value		6
	collect_vector		1
	get_atom		8,'fep#abnormal'
	put_value		1,9
	execute		4,eof2_4_0
eof2_4_6:
	suspend		eof2_4_0
	module_entry		pdss_file_device
	predicate		wfile_wait_open,5
wfile_wait_open_5_0:
	try_me_else		wfile_wait_open_5_1
	integer		5
	jump_on_integer		5,3,wfile_wait_open_5_1
	table_entry		wfile_wait_open_5_3
	table_entry		wfile_wait_open_5_1
	table_entry		wfile_wait_open_5_4
wfile_wait_open_5_3:
	get_atom		4,'fep#normal'
	execute		3,wfile_wait_reset_3_0
wfile_wait_open_5_4:
	collect_value		3
	collect_value		1
	get_atom		4,'fep#abnormal'
	b_remove_file		2,1
	proceed
wfile_wait_open_5_1:
	suspend		wfile_wait_open_5_0
	module_entry		pdss_file_device
	predicate		wfile_wait_reset,3
wfile_wait_reset_3_0:
	try_me_else		wfile_wait_reset_3_1
	jump_on_non_atom		1,wfile_wait_reset_3_3
	test_nil		1,wfile_wait_reset_3_1
	integer		2
	collect_value		3
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
wfile_wait_reset_3_3:
	is_vector		1,wfile_wait_reset_3_1
	jump_on_arity		1,6,wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_4
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_1
	table_entry		wfile_wait_reset_3_5
wfile_wait_reset_3_4:
	read_element		1,0,4
	wait_atom		4,close
	read_element		1,1,4
	integer		2
	collect_value		3
	collect_vector		1
	get_atom		4,'fep#normal'
	b_close_file		2,1,2
	b_remove_file		2,1
	proceed
wfile_wait_reset_3_5:
	read_element		1,0,4
	wait_atom		4,reset
	read_elements_inc		1,1,4,4
	collect_value		5
	collect_vector		1
	put_value		5,2
	put_value		8,3
	get_atom		6,'fep#normal'
	put_value		1,7
	put_values_inc		2,4,2
	put_value		4,8
	execute		4,wfile_4_0
wfile_wait_reset_3_1:
	suspend		wfile_wait_reset_3_0
	module_entry		pdss_file_device
	predicate		wfile,4
wfile_4_0:
	try_me_else		wfile_4_1
	wait_atom		2,'fep#abort'
	put_values_inc		2,3,2
	execute		3,wfile_wait_reset_3_0
wfile_4_1:
	try_me_else		wfile_4_6
	jump_on_non_atom		1,wfile_4_8
	test_nil		1,wfile_4_6
	integer		3
	collect_value		4
	collect_value		2
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
wfile_4_8:
	is_vector		1,wfile_4_6
	jump_on_arity		1,7,wfile_4_6
	table_entry		wfile_4_6
	table_entry		wfile_4_6
	table_entry		wfile_4_9
	table_entry		wfile_4_10
	table_entry		wfile_4_11
	table_entry		wfile_4_6
	table_entry		wfile_4_12
wfile_4_9:
	read_element		1,0,5
	wait_atom		5,close
	read_element		1,1,5
	integer		3
	collect_value		4
	collect_value		2
	collect_vector		1
	get_atom		5,'fep#normal'
	b_close_file		3,1,2
	b_remove_file		2,1
	proceed
wfile_4_10:
	read_element		1,0,5
	wait_atom		5,end_of_file
	read_elements_inc		1,1,5,2
	collect_vector		1
	get_atom		5,'fep#yes'
	put_value		1,6
	execute		4,wfile_4_0
wfile_4_11:
	read_element		1,0,5
	atom		5
	hash_on_atom		5,5,wfile_4_6
	bucket_entry_a		next_attention,wfile_4_14
	bucket_entry_a		pathname,wfile_4_15
	bucket_entry_a		putb,wfile_4_16
	bucket_entry_a		putc,wfile_4_17
	bucket_entry_a		putl,wfile_4_18
wfile_4_14:
	read_elements_inc		1,1,6,3
	collect_value		6
	collect_vector		1
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,wfile_4_0
wfile_4_15:
	read_elements_inc		1,1,6,3
	collect_vector		1
	put_marked_value		4,4
	get_value		4,6
	get_atom		7,'fep#normal'
	put_value		1,8
	execute		4,wfile_4_0
wfile_4_16:
	read_elements_inc		1,1,6,3
	integer		3
	string		6
	g_string		6,9,10
	wait_integer		10,8
	collect_vector		1
	b_write_buffer		3,6,6,3
	put_value		1,8
	put_value		5,7
	execute		6,wfile_wait_status_6_0
wfile_4_17:
	read_elements_inc		1,1,6,3
	integer		3
	integer		6
	collect_vector		1
	b_write_char		3,6,6,3
	put_value		1,8
	put_value		5,7
	execute		6,wfile_wait_status_6_0
wfile_4_18:
	read_elements_inc		1,1,6,3
	integer		3
	string		6
	g_string		6,9,10
	wait_integer		10,8
	collect_vector		1
	b_write_line		3,6,6,3
	put_value		1,8
	put_value		5,7
	execute		6,wfile_wait_status_6_0
wfile_4_12:
	read_element		1,0,5
	wait_atom		5,putt
	read_elements_inc		1,1,5,5
	integer		3
	collect_vector		1
	b_write_term		3,5,6,7,6,3
	put_value		1,9
	put_value		5,8
	execute		6,wfile_wait_status_6_0
wfile_4_6:
	suspend		wfile_4_0
	module_entry		pdss_file_device
	predicate		wfile_wait_status,6
wfile_wait_status_6_0:
	try_me_else		wfile_wait_status_6_1
	wait_integer		6,0
	get_atom		5,'fep#normal'
	execute		4,wfile_4_0
wfile_wait_status_6_1:
	suspend		wfile_wait_status_6_0
	module_entry		pdss_file_device
	predicate		wait_test_directory,4
wait_test_directory_4_0:
	try_me_else		wait_test_directory_4_1
	integer		4
	jump_on_integer		4,3,wait_test_directory_4_1
	table_entry		wait_test_directory_4_3
	table_entry		wait_test_directory_4_1
	table_entry		wait_test_directory_4_4
wait_test_directory_4_3:
	b_directory_pathname		2,2,4
	execute		4,wait_pathname_4_0
wait_test_directory_4_4:
	collect_value		2
	collect_value		1
	get_atom		3,'fep#abnormal'
	proceed
wait_test_directory_4_1:
	suspend		wait_test_directory_4_0
	module_entry		pdss_file_device
	predicate		wait_pathname,4
wait_pathname_4_0:
	try_me_else		wait_pathname_4_1
	integer		4
	jump_on_integer		4,3,wait_pathname_4_1
	table_entry		wait_pathname_4_3
	table_entry		wait_pathname_4_1
	table_entry		wait_pathname_4_4
wait_pathname_4_3:
	get_atom		3,'fep#normal'
	execute		2,directory_2_0
wait_pathname_4_4:
	collect_value		2
	collect_value		1
	get_atom		3,'fep#abnormal'
	proceed
wait_pathname_4_1:
	suspend		wait_pathname_4_0
	module_entry		pdss_file_device
	predicate		directory,2
directory_2_0:
	try_me_else		directory_2_1
	jump_on_non_atom		1,directory_2_3
	test_nil		1,directory_2_1
	collect_value		2
	proceed
directory_2_3:
	is_vector		1,directory_2_1
	jump_on_arity		1,6,directory_2_1
	table_entry		directory_2_1
	table_entry		directory_2_1
	table_entry		directory_2_1
	table_entry		directory_2_4
	table_entry		directory_2_5
	table_entry		directory_2_6
directory_2_4:
	read_element		1,0,3
	wait_atom		3,expunge
	read_elements_inc		1,1,3,2
	collect_vector		1
	get_atom		3,'fep#normal'
	put_value		1,4
	execute		2,directory_2_0
directory_2_5:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,directory_2_1
	bucket_entry_a		delete,directory_2_8
	bucket_entry_a		pathname,directory_2_9
	bucket_entry_a		purge,directory_2_10
	bucket_entry_a		undelete,directory_2_11
directory_2_8:
	read_elements_inc		1,1,4,3
	string		4
	g_string		4,7,8
	wait_integer		8,8
	collect_vector		1
	put_marked_value		1,2
	b_delete_files		1,4,3
	create_goal		2
	set_value		1,6
	set_value		2,2
	enqueue_goal		2,directory_2_0
	put_value		1,5
	put_value		2,3
	execute		2,wait_delete_2_0
directory_2_9:
	read_elements_inc		1,1,4,3
	collect_vector		1
	put_marked_value		2,2
	get_value		2,4
	get_atom		5,'fep#normal'
	put_value		1,6
	execute		2,directory_2_0
directory_2_10:
	read_elements_inc		1,1,4,3
	string		4
	g_string		4,7,8
	wait_integer		8,8
	collect_value		4
	collect_vector		1
	get_atom		5,'fep#normal'
	put_value		1,6
	execute		2,directory_2_0
directory_2_11:
	read_elements_inc		1,1,4,3
	string		4
	g_string		4,7,8
	wait_integer		8,8
	collect_value		4
	collect_vector		1
	get_atom		5,'fep#normal'
	put_value		1,6
	execute		2,directory_2_0
directory_2_6:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,directory_2_1
	bucket_entry_a		deleted,directory_2_13
	bucket_entry_a		listing,directory_2_14
directory_2_13:
	read_elements_inc		1,1,4,4
	string		4
	g_string		4,8,9
	wait_integer		9,8
	collect_value		4
	collect_vector		1
	get_atom		6,'fep#normal'
	create_goal		2
	set_value		1,7
	set_value		2,2
	enqueue_goal		2,directory_2_0
	put_value		1,5
	execute		1,listing_done1_1_0
directory_2_14:
	read_elements_inc		1,1,4,4
	string		4
	g_string		4,8,9
	wait_integer		9,8
	collect_vector		1
	put_marked_value		1,2
	put_marked_value		3,4
	b_listing_files		1,3,8,9
	create_goal		2
	set_value		1,7
	set_value		2,2
	enqueue_goal		2,directory_2_0
	put_value		1,2
	put_values_inc		2,4,2
	put_value		4,8
	put_value		5,6
	put_value		6,9
	execute		6,wait_listing_6_0
directory_2_1:
	suspend		directory_2_0
	module_entry		pdss_file_device
	predicate		wait_listing,6
wait_listing_6_0:
	try_me_else		wait_listing_6_1
	integer		6
	jump_on_integer		6,7,wait_listing_6_1
	table_entry		wait_listing_6_3
	table_entry		wait_listing_6_1
	table_entry		wait_listing_6_4
	table_entry		wait_listing_6_1
	table_entry		wait_listing_6_1
	table_entry		wait_listing_6_1
	table_entry		wait_listing_6_5
wait_listing_6_3:
	collect_value		2
	collect_value		1
	get_atom		5,'fep#normal'
	put_values_inc		1,3,2
	execute		2,listing_one_file_2_0
wait_listing_6_4:
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		5,'fep#abnormal'
	proceed
wait_listing_6_5:
	collect_value		4
	b_listing_files		1,2,2,4
	put_value		1,3
	put_value		3,5
	execute		4,wait_listing1_4_0
wait_listing_6_1:
	suspend		wait_listing_6_0
	module_entry		pdss_file_device
	predicate		wait_listing1,4
wait_listing1_4_0:
	try_me_else		wait_listing1_4_1
	wait_integer		4,0
	get_atom		3,'fep#normal'
	execute		2,listing_one_file_2_0
wait_listing1_4_1:
	try_me_else		wait_listing1_4_3
	put_integer		5,0
	g_diff		4,5
	collect_value		4
	collect_value		2
	collect_value		1
	get_atom		3,'fep#abnormal'
	proceed
wait_listing1_4_3:
	suspend		wait_listing1_4_0
	module_entry		pdss_file_device
	predicate		listing_one_file,2
listing_one_file_2_0:
	try_me_else		listing_one_file_2_1
	jump_on_non_atom		1,listing_one_file_2_3
	test_nil		1,listing_one_file_2_1
	collect_value		2
	proceed
listing_one_file_2_3:
	check_vector		1,4,listing_one_file_2_1
	read_element		1,0,3
	wait_atom		3,next_file_name
	read_elements_inc		1,1,4,3
	jump_on_non_list_var_var		2,listing_one_file_2_6,7,8
	collect_list		2
	collect_vector		1
	get_value		4,7
	get_atom		5,'fep#normal'
	put_value		1,6
	put_value		2,8
	execute		2,listing_one_file_2_0
listing_one_file_2_6:
	check_nil		2,listing_one_file_2_1
	collect_vector		1
	get_atom		4,'fep#nil'
	get_atom		5,'fep#end_of_file'
	put_value		1,6
	execute		1,listing_done2_1_0
listing_one_file_2_1:
	suspend		listing_one_file_2_0
	module_entry		pdss_file_device
	predicate		listing_done1,1
listing_done1_1_0:
	try_me_else		listing_done1_1_1
	jump_on_non_atom		1,listing_done1_1_3
	test_nil		1,listing_done1_1_1
	proceed
listing_done1_1_3:
	check_vector		1,4,listing_done1_1_1
	read_element		1,0,2
	wait_atom		2,next_file_name
	read_elements_inc		1,1,2,3
	collect_vector		1
	get_atom		2,'fep#nil'
	get_atom		3,'fep#end_of_file'
	put_value		1,4
	execute		1,listing_done2_1_0
listing_done1_1_1:
	suspend		listing_done1_1_0
	module_entry		pdss_file_device
	predicate		listing_done2,1
listing_done2_1_0:
	try_me_else		listing_done2_1_1
	jump_on_non_atom		1,listing_done2_1_3
	test_nil		1,listing_done2_1_1
	proceed
listing_done2_1_3:
	check_vector		1,4,listing_done2_1_1
	read_element		1,0,2
	wait_atom		2,next_file_name
	read_elements_inc		1,1,2,3
	collect_value		2
	collect_vector		1
	get_atom		3,'fep#abnormal'
	put_value		1,4
	execute		1,listing_done2_1_0
listing_done2_1_1:
	suspend		listing_done2_1_0
	module_entry		pdss_file_device
	predicate		wait_delete,2
wait_delete_2_0:
	try_me_else		wait_delete_2_1
	integer		2
	jump_on_integer		2,3,wait_delete_2_1
	table_entry		wait_delete_2_3
	table_entry		wait_delete_2_1
	table_entry		wait_delete_2_4
wait_delete_2_3:
	get_atom		1,'fep#normal'
	proceed
wait_delete_2_4:
	get_atom		1,'fep#abnormal'
	proceed
wait_delete_2_1:
	suspend		wait_delete_2_0
