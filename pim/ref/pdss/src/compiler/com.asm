kl1cmp_command:
	module		kl1cmp_command
	entry		tsscomp,1,tsscomp_1_0
	entry		tsscomp,0,tsscomp_0_0
	entry		kl1compile,0,kl1compile_0_0
	entry		ghccompile,8,ghccompile_8_0
	entry		message_distributer,7,message_distributer_7_0
	entry		write_string,3,write_string_3_0
	entry		compile_for_pdss,6,compile_for_pdss_6_0
	module_entry		kl1cmp_command
	predicate		kl1b_version,1
kl1b_version_1_0:
	get_atom		1,'**** KL1B Compiler Ver 0.5a (8807xx) ****'
	proceed
kl1b_version_1_1:
	suspend		kl1b_version_1_0
	module_entry		kl1cmp_command
	predicate		kl1compile,0
kl1compile_0_0:
	put_func		1,3,getft
	write_element_variable		1,1,9
	write_element_void		1,2
	put_list_val_var		2,1,8
	put_structured_constant		1,'$SCNST_0'
	put_list_val_val		3,1,2
	put_func		1,3,getft
	write_element_marked_variable		1,1,7
	write_element_void		1,2
	put_list_val_val		2,1,3
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		3,1,2
	put_func		1,3,getft
	write_element_variable		1,1,11
	write_element_void		1,2
	put_list_val_val		2,1,3
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		3,1,2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,3
	put_func		2,2,putt
	write_element_variable		2,1,12
	put_list_val_val		3,2,1
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	b_merge		2,3
	put_func		4,2,getl
	write_element_void		4,1
	put_list		5
	write_car_value		5,4
	write_cdr_nil		5
	put_structured_constant		4,'$SCNST_3'
	put_list_val_val		6,4,5
	put_func		4,2,putt
	write_element_value		4,1,7
	put_list_val_val		5,4,6
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,5
	put_func		5,2,putt
	write_element_variable		5,1,10
	put_list_val_val		6,5,4
	put_structured_constant		4,'$SCNST_4'
	put_list_val_val		5,4,6
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,5
	create_goal		3
	set_variable		1,13
	set_variable		2,14
	set_value		3,10
	enqueue_goal		3,check_error_3_0
	put_integer		5,1024
	b_rltv		5,5
	create_goal		7
	set_variable		1,6
	set_variable		2,16
	set_variable		3,10
	set_value		4,4
	set_atom		5,non_error
	set_value		6,13
	set_variable		7,18
	enqueue_goal_with_priority		7,message_distributer_7_0,5
	put_integer		4,1024
	b_rltv		4,4
	create_goal		2
	put_vector		19,4
	write_element_variable		19,0,15
	write_element_variable		19,1,13
	write_element_variable		19,2,5
	write_element_variable		19,3,17
	set_values_dec		1,19,2
	enqueue_goal_with_priority		2,my_merge_2_0,4
	create_goal		3
	set_value		1,16
	put_func		4,2,close
	write_element_value		4,1,14
	put_list		14
	write_car_value		14,4
	write_cdr_nil		14
	set_value		2,14
	set_variable		3,4
	enqueue_goal_external		kl1cmp_output,output_const_code,3
	create_goal		5
	set_variable		1,16
	set_nil		2
	set_value		3,4
	set_nil		4
	set_variable		5,4
	enqueue_goal_external		kl1cmp_struct,struct_processor,5
	create_goal		1
	set_value		1,3
	enqueue_goal_external		kl1cmp_macro_arg,init_macro_table,1
	create_goal		6
	set_variable		1,14
	set_nil		2
	set_value		3,17
	set_nil		4
	set_value		5,2
	set_value		6,16
	enqueue_goal_external		kl1cmp_macro,generate_macro_expander,6
	put_integer		2,1024
	b_rltv		2,2
	create_goal		5
	set_variable		1,3
	set_nil		2
	set_value		3,15
	set_nil		4
	set_value		5,14
	enqueue_goal_with_priority		5,'$kl1cmp_reader:create_reader/5_5_0',2
	put_integer		2,-1024
	b_rltv		2,2
	create_goal		8
	set_value		1,4
	set_nil		2
	set_value		3,13
	set_nil		4
	set_value		5,5
	set_nil		6
	set_value		7,11
	set_void		8
	enqueue_goal_with_priority		8,ghccompile_8_0,2
	create_goal		1
	set_value		1,12
	enqueue_goal		1,kl1b_version_1_0
	create_goal		5
	set_variable		1,2
	set_value		2,10
	set_value		3,6
	set_value		4,9
	set_atom		5,w
	enqueue_goal		5,file_open_5_0
	create_goal		5
	set_value		1,8
	set_values_inc		2,2,2
	set_value		4,7
	set_atom		5,r
	enqueue_goal		5,file_open_5_0
	put_structured_constant		2,'$SCNST_5'
	execute_external		window,create,2
kl1compile_0_1:
	suspend		kl1compile_0_0
	module_entry		kl1cmp_command
	predicate		check_error,3
check_error_3_0:
	try_me_else		check_error_3_1
	atom		1
	branch_on_atom		1,2,check_error_3_1
	bucket_entry_a		error,check_error_3_3
	bucket_entry_a		non_error,check_error_3_4
check_error_3_3:
	collect_value		2
	get_atom		3,error
	proceed
check_error_3_4:
	get_value		2,3
	proceed
check_error_3_1:
	suspend		check_error_3_0
	module_entry		kl1cmp_command
	predicate		my_merge,2
my_merge_2_0:
	b_merge		3,4
	get_value		3,1
	get_value		4,2
	proceed
my_merge_2_1:
	suspend		my_merge_2_0
	module_entry		kl1cmp_command
	predicate		file_open,5
file_open_5_0:
	create_goal		6
	set_variable		1,7
	set_value		2,2
	set_variable		3,2
	set_variable		4,6
	set_value		5,3
	set_marked_value		6,5
	enqueue_goal		6,status_check_6_0
	create_goal		4
	set_value		1,6
	set_variable		2,6
	set_value		3,5
	set_value		4,2
	enqueue_goal_external		mpimos_file,create,4
	put_value		2,7
	put_value		3,4
	put_value		4,6
	execute		4,convert_name_to_string_4_0
file_open_5_1:
	suspend		file_open_5_0
	module_entry		kl1cmp_command
	predicate		convert_name_to_string,4
convert_name_to_string_4_0:
	try_me_else		convert_name_to_string_4_1
	jump_on_non_atom		3,convert_name_to_string_4_3
	get_value		1,2
	b_atom_name		3,1
	get_value		1,4
	proceed
convert_name_to_string_4_3:
	is_string		3,convert_name_to_string_4_1
	g_string		3,5,6
	get_value		1,2
	get_value		4,3
	proceed
convert_name_to_string_4_4:
	get_value		1,2
	get_value		4,3
	proceed
convert_name_to_string_4_1:
	otherwise		convert_name_to_string_4_0
	put_func		5,2,gett
	write_element_variable		5,1,9
	put_list_val_var		6,5,8
	put_structured_constant		5,'$SCNST_6'
	put_list_val_val		7,5,6
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,7
	put_structured_constant		6,'$SCNST_7'
	put_list_val_val		7,6,5
	put_func		5,2,puttq
	write_element_value		5,1,3
	put_list_val_val		3,5,7
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,3
	get_list_value		1,5
	put_value		1,8
	put_value		3,9
	execute		4,convert_name_to_string_4_0
convert_name_to_string_4_9:
	suspend		convert_name_to_string_4_0
	module_entry		kl1cmp_command
	predicate		status_check,6
status_check_6_0:
	try_me_else		status_check_6_1
	wait_atom		3,success
	collect_value		6
	get_value		1,2
	get_value		4,5
	proceed
status_check_6_1:
	otherwise		status_check_6_0
	collect_value		3
	put_func		3,2,gett
	write_element_variable		3,1,10
	put_list_val_var		7,3,9
	put_structured_constant		3,'$SCNST_8'
	put_list_val_val		8,3,7
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,8
	put_structured_constant		7,'$SCNST_9'
	put_list_val_val		8,7,3
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,8
	get_list_value		1,3
	get_nil		4
	put_value		1,9
	put_value		3,5
	put_value		4,10
	put_value		5,6
	execute		5,file_open_5_0
status_check_6_6:
	suspend		status_check_6_0
	module_entry		kl1cmp_command
	predicate		compile_for_pdss,6
compile_for_pdss_6_0:
	b_merge		7,8
	b_merge		14,9
	put_vector		15,4
	write_element_variable		15,0,10
	write_element_variable		15,1,11
	write_element_variable		15,2,12
	write_element_variable		15,3,13
	get_vector_value		14,15
	create_goal		3
	set_variable		1,15
	set_variable		2,14
	set_value		3,6
	enqueue_goal		3,check_error_3_0
	create_goal		7
	set_value		1,3
	set_variable		2,3
	set_value		3,4
	set_nil		4
	set_atom		5,non_error
	set_value		6,15
	set_value		7,9
	enqueue_goal		7,message_distributer_7_0
	create_goal		3
	set_value		1,3
	put_func		3,2,close
	write_element_value		3,1,14
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	set_value		2,4
	set_variable		3,3
	enqueue_goal_external		kl1cmp_output,output_const_code,3
	create_goal		5
	set_variable		1,6
	set_nil		2
	set_value		3,3
	set_nil		4
	set_variable		5,3
	enqueue_goal_external		kl1cmp_struct,struct_processor,5
	create_goal		1
	set_value		1,8
	enqueue_goal_external		kl1cmp_macro_arg,init_macro_table,1
	create_goal		6
	set_variable		1,4
	set_nil		2
	set_value		3,13
	set_nil		4
	set_values_dec		5,7,2
	enqueue_goal_external		kl1cmp_macro,generate_macro_expander,6
	create_goal		5
	set_value		1,2
	set_nil		2
	set_value		3,12
	set_nil		4
	set_value		5,4
	enqueue_goal_external		kl1cmp_reader,create_reader,5
	put_integer		2,-1024
	b_rltv		2,2
	create_goal		8
	set_value		1,3
	set_nil		2
	set_value		3,11
	set_nil		4
	set_value		5,10
	set_nil		6
	set_value		7,1
	set_value		8,5
	enqueue_goal_with_priority		8,ghccompile_8_0,2
	proceed
compile_for_pdss_6_1:
	suspend		compile_for_pdss_6_0
	module_entry		kl1cmp_command
	predicate		message_distributer,7
message_distributer_7_0:
	try_me_else		message_distributer_7_1
	jump_on_non_list		7,message_distributer_7_3
	read_car		7,8
	jump_on_non_atom		8,message_distributer_7_5
	branch_on_atom		8,2,message_distributer_7_1
	bucket_entry_a		nl,message_distributer_7_6
	bucket_entry_a		ttynl,message_distributer_7_7
message_distributer_7_6:
	read_cdr		7,9
	put_reused_list		8,7
	write_car_atom		8,nl
	write_cdr_variable		8,7
	get_list_value		1,8
	put_value		1,7
	put_value		7,9
	execute		7,message_distributer_7_0
message_distributer_7_7:
	read_cdr		7,9
	put_reused_list		8,7
	write_car_atom		8,nl
	write_cdr_variable		8,7
	get_list_value		3,8
	put_value		3,7
	put_value		7,9
	execute		7,message_distributer_7_0
message_distributer_7_5:
	is_vector		8,message_distributer_7_1
	jump_on_arity		8,4,message_distributer_7_1
	table_entry		message_distributer_7_1
	table_entry		message_distributer_7_1
	table_entry		message_distributer_7_8
	table_entry		message_distributer_7_9
message_distributer_7_8:
	read_element		8,0,9
	atom		9
	hash_on_atom		9,6,message_distributer_7_1
	bucket_entry_a		display,message_distributer_7_11
	bucket_entry_a		putc,message_distributer_7_12
	bucket_entry_a		puts,message_distributer_7_13
	bucket_entry_a		putt,message_distributer_7_14
	bucket_entry_a		puttq,message_distributer_7_15
	bucket_entry_a		ttyput,message_distributer_7_16
message_distributer_7_11:
	read_cdr		7,10
	read_element		8,1,11
	put_reused_func		8,8,putt
	write_element_value		8,1,11
	get_reused_list_val_var		3,9,7,8,7
	put_value		3,7
	put_value		7,10
	execute		7,message_distributer_7_0
message_distributer_7_12:
	read_cdr		7,10
	read_element		8,1,11
	put_reused_func		8,8,putc
	write_element_value		8,1,11
	get_reused_list_val_var		1,9,7,8,7
	put_value		1,7
	put_value		7,10
	execute		7,message_distributer_7_0
message_distributer_7_13:
	read_cdr		7,10
	read_element		8,1,11
	collect_list		7
	collect_vector		8
	create_goal		7
	set_variable		1,7
	set_values_inc		2,2,5
	set_value		7,10
	enqueue_goal		7,message_distributer_7_0
	put_value		2,7
	put_value		3,11
	execute		3,write_string_3_0
message_distributer_7_14:
	read_cdr		7,10
	read_element		8,1,11
	put_reused_func		8,8,putt
	write_element_value		8,1,11
	get_reused_list_val_var		1,9,7,8,7
	put_value		1,7
	put_value		7,10
	execute		7,message_distributer_7_0
message_distributer_7_15:
	read_cdr		7,10
	read_element		8,1,11
	put_reused_func		8,8,puttq
	write_element_value		8,1,11
	get_reused_list_val_var		1,9,7,8,7
	put_value		1,7
	put_value		7,10
	execute		7,message_distributer_7_0
message_distributer_7_16:
	read_cdr		7,10
	read_element		8,1,11
	put_reused_func		8,8,putc
	write_element_value		8,1,11
	get_reused_list_val_var		3,9,7,8,7
	put_value		3,7
	put_value		7,10
	execute		7,message_distributer_7_0
message_distributer_7_9:
	read_element		8,0,9
	atom		9
	branch_on_atom		9,3,message_distributer_7_1
	bucket_entry_a		code,message_distributer_7_18
	bucket_entry_a		error_message,message_distributer_7_19
	bucket_entry_a		warning_message,message_distributer_7_20
message_distributer_7_18:
	read_cdr		7,10
	read_elements_inc		8,1,11,2
	collect_vector		8
	put_func		8,2,flush
	write_element_void		8,1
	put_reused_list_val_var		7,7,8,9
	put_func		8,2,flush
	write_element_void		8,1
	get_list_val_var		3,13,8,8
	create_goal		7
	set_value		1,9
	set_value		2,2
	set_value		3,8
	set_values_inc		4,4,3
	set_value		7,10
	enqueue_goal		7,message_distributer_7_0
	put_value		2,7
	put_values_inc		3,11,2
	execute		4,'C_4_0'
message_distributer_7_19:
	read_cdr		7,10
	read_elements_inc		8,1,11,2
	collect_list		7
	collect_value		5
	collect_vector		8
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,2
	set_value		4,4
	set_atom		5,error
	set_value		6,6
	set_value		7,10
	enqueue_goal		7,message_distributer_7_0
	put_value		1,3
	put_values_inc		3,11,2
	execute		4,error_4_0
message_distributer_7_20:
	read_cdr		7,10
	read_elements_inc		8,1,11,2
	collect_list		7
	collect_vector		8
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,2
	set_values_inc		4,4,3
	set_value		7,10
	enqueue_goal		7,message_distributer_7_0
	put_value		1,3
	put_values_inc		3,11,2
	execute		4,warning_4_0
message_distributer_7_3:
	check_nil		7,message_distributer_7_1
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
message_distributer_7_1:
	otherwise		message_distributer_7_0
	try_me_else		message_distributer_7_32
	wait_list_var_var		7,8,9
	put_reused_list		7,7
	write_car_atom		7,nl
	write_cdr_variable		7,11
	put_func		10,2,putt
	write_element_value		10,1,8
	put_list_val_val		8,10,7
	put_list		7
	write_car_atom		7,nl
	write_cdr_value		7,8
	put_structured_constant		8,'$SCNST_10'
	put_list_val_val		10,8,7
	get_list_value		3,10
	put_value		3,11
	put_value		7,9
	execute		7,message_distributer_7_0
message_distributer_7_32:
	suspend		message_distributer_7_0
	module_entry		kl1cmp_command
	predicate		wait_flushed,9
wait_flushed_9_0:
	try_me_else		wait_flushed_9_1
	wait_atom		7,done
	wait_atom		8,done
	put_value		7,9
	execute		7,message_distributer_7_0
wait_flushed_9_1:
	suspend		wait_flushed_9_0
	module_entry		kl1cmp_command
	predicate		'C',4
'C_4_0':
	get_value		1,3
	get_value		2,4
	proceed
'C_4_1':
	suspend		'C_4_0'
	module_entry		kl1cmp_command
	predicate		write_string,3
write_string_3_0:
	b_intern_atom		3,3
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
write_string_3_1:
	suspend		write_string_3_0
	module_entry		kl1cmp_command
	predicate		write_string,5
write_string_5_0:
	try_me_else		write_string_5_1
	wait_integer		3,0
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
write_string_5_1:
	otherwise		write_string_5_0
	try_me_else		write_string_5_6
	integer		4
	string		5
	g_string_element		5,4,6
	b_decrement		3,3
	b_increment		4,4
	put_func		7,2,putc
	write_element_value		7,1,6
	get_list_val_var		1,8,7,6
	put_value		1,6
	execute		5,write_string_5_0
write_string_5_6:
	suspend		write_string_5_0
	module_entry		kl1cmp_command
	predicate		ghccompile,8
ghccompile_8_0:
	put_func		9,3,read_predicate
	write_element_variable		9,1,11
	write_element_variable		9,2,10
	get_list_val_var		1,12,9,9
	put_func		1,3,read_predicate
	write_element_variable		1,1,14
	write_element_variable		1,2,13
	get_list_val_var		9,15,1,12
	put_integer		1,1024
	b_rltv		1,1
	create_goal		10
	set_value		1,12
	set_value		2,2
	set_variable		3,9
	set_value		4,4
	set_variable		5,4
	set_value		6,6
	set_value		7,13
	set_marked_value		8,7
	set_value		9,14
	set_variable		10,2
	enqueue_goal_with_priority		10,check_end_of_file_10_0,1
	put_integer		1,1024
	b_rltv		1,1
	create_goal		10
	set_value		1,3
	set_value		2,9
	set_values_dec		3,5,2
	set_values_inc		5,10,2
	set_value		7,7
	set_value		8,2
	set_value		9,8
	set_variable		10,2
	enqueue_goal_with_priority		10,compile_case_on_pred_10_0,1
	put_structured_constant		1,'$SCNST_11'
	execute		2,create_state_2_0
ghccompile_8_1:
	suspend		ghccompile_8_0
	module_entry		kl1cmp_command
	predicate		compile_case_on_pred,10
compile_case_on_pred_10_0:
	try_me_else		compile_case_on_pred_10_1
	wait_atom		5,directive
	collect_value		7
	create_goal		3
	set_variable		1,7
	set_value		2,2
	set_variable		3,2
	enqueue_goal_external		kl1cmp_output,write_messages,3
	create_goal		5
	set_variable		1,5
	set_void		2
	set_atom		3,messages
	set_value		4,2
	set_atom		5,void
	enqueue_goal		5,access_state_5_0
	create_goal		6
	set_value		1,1
	set_value		2,7
	set_variable		3,2
	set_value		4,4
	set_marked_value		5,8
	set_marked_value		6,9
	enqueue_goal_external		kl1cmp_output,write_rkp_information,6
	create_goal		5
	set_variable		1,1
	set_value		2,5
	set_atom		3,external
	set_value		4,9
	set_atom		5,void
	enqueue_goal		5,access_state_5_0
	create_goal		5
	set_variable		1,4
	set_value		2,1
	set_atom		3,module
	set_value		4,8
	set_atom		5,void
	enqueue_goal		5,access_state_5_0
	put_value		1,3
	put_value		3,10
	put_value		5,6
	execute		5,compile_initial_directives_5_0
compile_case_on_pred_10_1:
	otherwise		compile_case_on_pred_10_0
	collect_value		10
	collect_value		7
	collect_value		6
	collect_value		5
	get_value		3,4
	put_structured_constant		3,'$SCNST_12'
	put_list_val_val		4,3,2
	get_list_value		1,4
	get_nil		8
	get_nil		9
	proceed
compile_case_on_pred_10_6:
	suspend		compile_case_on_pred_10_0
	module_entry		kl1cmp_command
	predicate		check_end_of_file,10
check_end_of_file_10_0:
	try_me_else		check_end_of_file_10_1
	wait_atom		7,end_of_file
	collect_value		10
	collect_value		9
	collect_value		8
	get_value		3,4
	get_value		1,2
	put_structured_constant		1,'$SCNST_13'
	put_list_val_val		2,1,6
	get_list_value		5,2
	proceed
check_end_of_file_10_1:
	otherwise		check_end_of_file_10_0
	b_merge		11,12
	b_merge		13,14
	b_merge		15,16
	create_goal		3
	set_values_inc		1,1,2
	set_value		3,16
	enqueue_goal		3,out_to_stream_3_0
	put_integer		1,1024
	b_rltv		1,1
	create_goal		3
	set_values_inc		1,5,2
	set_value		3,14
	enqueue_goal_with_priority		3,out_to_stream_3_0,1
	put_integer		1,1024
	b_rltv		1,1
	create_goal		3
	set_values_inc		1,3,2
	set_value		3,12
	enqueue_goal_with_priority		3,out_to_stream_3_0,1
	put_integer		1,-1024
	b_rltv		1,1
	create_goal		7
	set_value		1,15
	set_value		2,11
	set_value		3,13
	set_values_inc		4,8,2
	set_value		6,7
	set_value		7,10
	enqueue_goal_with_priority		7,read_and_compile_predicate_7_0,1
	proceed
check_end_of_file_10_6:
	suspend		check_end_of_file_10_0
	module_entry		kl1cmp_command
	predicate		high_priority_merge,2
high_priority_merge_2_0:
	b_merge		3,4
	get_value		3,1
	get_value		4,2
	proceed
high_priority_merge_2_1:
	suspend		high_priority_merge_2_0
	module_entry		kl1cmp_command
	predicate		out_to_stream,3
out_to_stream_3_0:
	try_me_else		out_to_stream_3_1
	jump_on_non_list_var_var		3,out_to_stream_3_3,4,5
	get_reused_list_val_var		1,6,3,4,3
	put_value		1,3
	put_value		3,5
	execute		3,out_to_stream_3_0
out_to_stream_3_3:
	check_nil		3,out_to_stream_3_1
	get_value		1,2
	proceed
out_to_stream_3_1:
	suspend		out_to_stream_3_0
	module_entry		kl1cmp_command
	predicate		tsscomp,1
tsscomp_1_0:
	b_merge		3,2
	put_vector		4,2
	write_element_variable		4,0,5
	write_element_variable		4,1,6
	get_vector_value		3,4
	put_func		3,3,read_predicate
	write_element_variable		3,1,10
	write_element_variable		3,2,9
	put_list_val_var		4,3,8
	b_merge		13,3
	put_vector		14,3
	write_element_variable		14,0,12
	write_element_variable		14,1,7
	write_element_variable		14,2,11
	get_vector_value		13,14
	create_goal		7
	set_value		1,8
	set_values_dec		2,12,2
	set_value		4,1
	set_values_dec		5,10,2
	set_nil		7
	enqueue_goal		7,read_and_compile_predicate_7_0
	create_goal		2
	put_structured_constant		1,'$SCNST_14'
	set_value		1,1
	set_void		2
	enqueue_goal		2,create_state_2_0
	create_goal		5
	set_value		1,6
	set_nil		2
	set_value		3,7
	set_nil		4
	set_value		5,4
	enqueue_goal_external		kl1cmp_reader,create_reader,5
	create_goal		3
	set_value		1,5
	set_nil		2
	set_value		3,3
	enqueue_goal_external		kl1cmp_reader,trans_io_instr,3
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_15'
	execute_external		window,create,2
tsscomp_1_1:
	suspend		tsscomp_1_0
	module_entry		kl1cmp_command
	predicate		tsscomp,0
tsscomp_0_0:
	put_integer		1,0
	execute		1,tsscomp_1_0
tsscomp_0_1:
	suspend		tsscomp_0_0
	module_entry		kl1cmp_command
	predicate		compile_initial_directives,5
compile_initial_directives_5_0:
	try_me_else		compile_initial_directives_5_1
	jump_on_non_list_var_var		5,compile_initial_directives_5_3,6,7
	collect_list		5
	create_goal		5
	set_variable		1,8
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,7
	enqueue_goal		5,compile_initial_directives_5_0
	put_value		2,8
	put_values_inc		4,5,2
	execute		5,compile_initial_directive_5_0
compile_initial_directives_5_3:
	check_nil		5,compile_initial_directives_5_1
	get_value		3,4
	get_value		1,2
	proceed
compile_initial_directives_5_1:
	suspend		compile_initial_directives_5_0
	module_entry		kl1cmp_command
	predicate		compile_initial_directive,5
compile_initial_directive_5_0:
	try_me_else		compile_initial_directive_5_1
	wait_vector		5,2
	read_element		5,0,6
	wait_atom		6,:-
	read_element		5,1,7
	wait_vector		7,2
	read_element		7,0,8
	atom		8
	branch_on_atom		8,3,compile_initial_directive_5_1
	bucket_entry_a		message,compile_initial_directive_5_6
	bucket_entry_a		module,compile_initial_directive_5_7
	bucket_entry_a		public,compile_initial_directive_5_8
compile_initial_directive_5_6:
	read_element		7,1,6
	collect_vector		5
	collect_vector		7
	get_value		1,2
	put_list_val_var		5,6,6
	put_values_inc		1,3,2
	put_atom		3,messages
	put_value		4,6
	execute		5,access_state_5_0
compile_initial_directive_5_7:
	read_element		7,1,6
	collect_vector		5
	collect_vector		7
	create_goal		4
	set_values_inc		1,1,2
	set_variable		3,5
	set_marked_value		4,6
	enqueue_goal		4,check_module_4_0
	put_values_inc		1,3,2
	put_atom		3,module
	put_values_inc		4,5,2
	execute		5,access_state_5_0
compile_initial_directive_5_8:
	read_element		7,1,6
	collect_vector		5
	collect_vector		7
	get_value		1,2
	create_goal		5
	set_values_inc		1,3,2
	set_atom		3,external
	set_variable		4,2
	set_variable		5,1
	enqueue_goal		5,access_state_5_0
	put_value		3,6
	execute		3,conjunction_to_list_3_0
compile_initial_directive_5_1:
	otherwise		compile_initial_directive_5_0
	get_value		3,4
	put_list		3
	write_car_value		3,5
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_16'
	put_func		5,3,warning_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
compile_initial_directive_5_20:
	suspend		compile_initial_directive_5_0
	module_entry		kl1cmp_command
	predicate		compile_directives,3
compile_directives_3_0:
	try_me_else		compile_directives_3_1
	jump_on_non_list_var_var		3,compile_directives_3_3,6,4
	wait_vector		6,2
	read_element		6,0,5
	wait_atom		5,:-
	read_element		6,1,7
	wait_vector		7,2
	read_element		7,0,5
	wait_atom		5,message
	read_element		7,1,5
	collect_vector		6
	collect_vector		7
	create_goal		3
	set_variable		1,6
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,compile_directives_3_0
	put_reused_list		3,3
	write_car_value		3,5
	write_cdr_nil		3
	put_value		2,6
	execute_external		kl1cmp_output,write_messages,3
compile_directives_3_3:
	check_nil		3,compile_directives_3_1
	get_value		1,2
	proceed
compile_directives_3_1:
	otherwise		compile_directives_3_0
	try_me_else		compile_directives_3_8
	wait_list_var_var		3,4,5
	put_reused_list		3,3
	write_car_value		3,4
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_17'
	put_func		6,3,warning_message
	write_elements_dec		6,1,4,2
	get_list_val_var		1,4,6,3
	put_value		1,3
	put_value		3,5
	execute		3,compile_directives_3_0
compile_directives_3_8:
	suspend		compile_directives_3_0
	module_entry		kl1cmp_command
	predicate		check_module,4
check_module_4_0:
	try_me_else		check_module_4_1
	wait_nil		3
	collect_value		4
	get_value		1,2
	proceed
check_module_4_1:
	try_me_else		check_module_4_3
	put_nil		5
	g_diff		3,5
	collect_value		3
	collect_value		5
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_18'
	put_func		5,3,error_message
	write_elements_dec		5,1,4,2
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
check_module_4_3:
	suspend		check_module_4_0
	module_entry		kl1cmp_command
	predicate		read_and_compile_predicate,7
read_and_compile_predicate_7_0:
	try_me_else		read_and_compile_predicate_7_1
	wait_atom		6,end_of_file
	collect_value		7
	collect_value		5
	collect_value		4
	get_nil		1
	get_nil		2
	put_nil		2
	put_list		1
	write_car_atom		1,ttynl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_19'
	put_list_val_val		4,2,1
	get_list_value		3,4
	proceed
read_and_compile_predicate_7_1:
	otherwise		read_and_compile_predicate_7_0
	put_vector		8,2
	write_element_variable		8,0,10
	write_element_variable		8,1,9
	get_vector_value		1,8
	put_vector		1,2
	write_element_variable		1,0,12
	write_element_variable		1,1,11
	put_vector		8,4
	write_element_variable		8,0,16
	write_element_variable		8,1,15
	write_element_variable		8,2,14
	write_element_variable		8,3,13
	get_vector_value		3,8
	put_func		3,2,flush
	write_element_variable		3,1,19
	put_list_val_var		8,3,18
	put_func		3,3,code
	write_element_variable		3,1,17
	write_element_value		3,2,18
	put_list_val_val		18,3,1
	get_list_value		2,18
	create_goal		7
	set_value		1,10
	set_value		2,12
	set_value		3,16
	set_variable		4,2
	set_variable		5,3
	set_marked_value		6,4
	set_marked_value		7,7
	enqueue_goal		7,compile_directives_or_clause_7_0
	put_integer		1,1024
	b_rltv		1,1
	create_goal		7
	set_value		1,9
	set_value		2,11
	set_value		3,15
	set_value		4,19
	set_marked_value		5,6
	set_values_dec		6,3,2
	enqueue_goal_with_priority		7,wait_compiled_7_0,1
	create_goal		9
	set_value		1,17
	set_value		2,8
	set_value		3,14
	set_nil		4
	set_value		5,4
	set_value		6,7
	set_values_inc		7,5,2
	set_integer		9,1
	enqueue_goal_external		kl1cmp_register,compile_predicate,9
	put_value		1,13
	put_value		2,6
	execute		2,check_overlapped_builtin_2_0
read_and_compile_predicate_7_6:
	suspend		read_and_compile_predicate_7_0
	module_entry		kl1cmp_command
	predicate		compile_directives_or_clause,7
compile_directives_or_clause_7_0:
	try_me_else		compile_directives_or_clause_7_1
	wait_atom		4,directive
	put_func		4,3,code
	write_element_variable		4,1,9
	write_element_variable		4,2,8
	get_list_val_var		2,10,4,4
	put_func		2,3,read_predicate
	write_element_variable		2,1,11
	write_element_variable		2,2,10
	get_list_val_var		1,12,2,2
	create_goal		7
	set_value		1,2
	set_values_dec		2,4,2
	set_value		4,6
	set_values_dec		5,11,2
	set_value		7,7
	enqueue_goal		7,read_and_compile_predicate_7_0
	put_values_dec		1,9,2
	put_value		3,5
	execute		3,compile_directives_3_0
compile_directives_or_clause_7_1:
	otherwise		compile_directives_or_clause_7_0
	put_value		8,4
	put_value		4,6
	put_value		6,8
	execute		7,read_and_compile_predicate_7_0
compile_directives_or_clause_7_6:
	suspend		compile_directives_or_clause_7_0
	module_entry		kl1cmp_command
	predicate		wait_compiled,7
wait_compiled_7_0:
	try_me_else		wait_compiled_7_1
	wait		4
	put_nil		8
	get_nil		2
	put_nil		9
	put_structured_constant		2,'$SCNST_20'
	put_list_val_val		4,2,9
	put_func		2,2,display
	write_element_value		2,1,5
	put_list_val_val		5,2,4
	get_list_value		3,5
	put_func		2,3,read_predicate
	write_elements_inc		2,1,6,2
	put_list_val_val		3,2,8
	get_list_value		1,3
	proceed
wait_compiled_7_1:
	suspend		wait_compiled_7_0
	module_entry		kl1cmp_command
	predicate		error,4
error_4_0:
	put_list		5
	write_car_atom		5,nl
	write_cdr_variable		5,7
	put_func		6,2,putb
	write_element_value		6,1,3
	put_list_val_val		3,6,5
	put_structured_constant		5,'$SCNST_21'
	put_list_val_val		6,5,3
	put_structured_constant		3,'$SCNST_22'
	put_list_val_val		5,3,6
	get_list_value		1,5
	put_value		1,7
	put_value		3,4
	execute		3,output_error_3_0
error_4_1:
	suspend		error_4_0
	module_entry		kl1cmp_command
	predicate		warning,4
warning_4_0:
	put_list		5
	write_car_atom		5,nl
	write_cdr_variable		5,7
	put_func		6,2,putb
	write_element_value		6,1,3
	put_list_val_val		3,6,5
	put_structured_constant		5,'$SCNST_23'
	put_list_val_val		6,5,3
	put_structured_constant		3,'$SCNST_24'
	put_list_val_val		5,3,6
	get_list_value		1,5
	put_value		1,7
	put_value		3,4
	execute		3,output_error_3_0
warning_4_1:
	suspend		warning_4_0
	module_entry		kl1cmp_command
	predicate		output_error,3
output_error_3_0:
	try_me_else		output_error_3_1
	jump_on_non_list_var_var		3,output_error_3_3,4,5
	put_func		6,2,puttq
	write_element_value		6,1,4
	put_reused_list_val_var		3,3,6,6
	put_structured_constant		4,'$SCNST_25'
	put_list_val_val		7,4,3
	get_list_value		1,7
	put_value		1,6
	put_value		3,5
	execute		3,output_error_3_0
output_error_3_3:
	check_nil		3,output_error_3_1
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	get_list_value		1,3
	proceed
output_error_3_1:
	otherwise		output_error_3_0
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_func		2,2,puttq
	write_element_value		2,1,3
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_26'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
output_error_3_8:
	suspend		output_error_3_0
	module_entry		kl1cmp_command
	predicate		create_state,2
create_state_2_0:
	get_value		1,2
	proceed
create_state_2_1:
	suspend		create_state_2_0
	module_entry		kl1cmp_command
	predicate		access_state,5
access_state_5_0:
	try_me_else		access_state_5_1
	jump_on_non_list		1,access_state_5_3
	read_car		1,6
	wait_vector		6,3
	read_element		6,0,7
	wait_atom		7,=
	read_elements_inc		6,1,8,2
	read_cdr		1,10
	try_me_else		access_state_5_6
	wait_value		3,8
	collect_value		8
	get_value		9,4
	put_reused_func		4,6,=
	write_element_value		4,1,3
	write_element_value		4,2,5
	put_reused_list_val_val		1,1,4,10
	get_list_value		2,1
	proceed
access_state_5_6:
	try_me_else		access_state_5_1
	g_diff		3,8
	put_reused_func		6,6,=
	write_elements_inc		6,1,8,2
	get_reused_list_val_var		2,1,1,6,6
	put_value		1,10
	put_value		2,6
	execute		5,access_state_5_0
access_state_5_3:
	check_nil		1,access_state_5_1
	put_func		1,3,=
	write_element_value		1,1,3
	write_element_marked_value		1,2,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	get_value		5,4
	proceed
access_state_5_1:
	suspend		access_state_5_0
	module_entry		kl1cmp_command
	predicate		conjunction_to_list,3
conjunction_to_list_3_0:
	try_me_else		conjunction_to_list_3_1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,','
	read_elements_inc		3,1,4,2
	collect_vector		3
	get_list_val_var		1,6,4,3
	put_value		1,3
	put_value		3,5
	execute		3,conjunction_to_list_3_0
conjunction_to_list_3_1:
	otherwise		conjunction_to_list_3_0
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
conjunction_to_list_3_6:
	suspend		conjunction_to_list_3_0
	module_entry		kl1cmp_command
	predicate		check_overlapped_builtin,2
check_overlapped_builtin_2_0:
	try_me_else		check_overlapped_builtin_2_1
	wait_vector		2,3
	read_element		2,0,3
	wait_atom		3,/
	read_elements_inc		2,1,3,2
	collect_vector		2
	put_marked_value		2,4
	b_increment		2,2
	b_new_vector		2,2
	put_integer		5,0
	put_marked_value		6,3
	b_set_vector_element		2,5,2,6,5
	create_goal		4
	set_value		1,1
	set_variable		2,6
	set_values_inc		3,3,2
	enqueue_goal		4,check_overlapped_builtin_type_4_0
	put_value		1,5
	put_void		2
	put_void		3
	put_void		4
	put_value		5,6
	execute_external		kl1cmp_blttbl,active_builtin,5
check_overlapped_builtin_2_1:
	suspend		check_overlapped_builtin_2_0
	module_entry		kl1cmp_command
	predicate		check_overlapped_builtin_type,4
check_overlapped_builtin_type_4_0:
	try_me_else		check_overlapped_builtin_type_4_1
	atom		2
	branch_on_atom		2,2,check_overlapped_builtin_type_4_1
	bucket_entry_a		builtin,check_overlapped_builtin_type_4_3
	bucket_entry_a		none,check_overlapped_builtin_type_4_4
check_overlapped_builtin_type_4_3:
	put_nil		5
	put_func		2,3,/
	write_elements_inc		2,1,3,2
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_structured_constant		2,'$SCNST_27'
	put_func		4,3,warning_message
	write_elements_inc		4,1,2,2
	put_list_val_val		2,4,5
	get_list_value		1,2
	proceed
check_overlapped_builtin_type_4_4:
	atom		3
	branch_on_atom		3,2,check_overlapped_builtin_type_4_1
	bucket_entry_a		merge,check_overlapped_builtin_type_4_6
	bucket_entry_a		merge_in,check_overlapped_builtin_type_4_7
check_overlapped_builtin_type_4_6:
	wait_integer		4,3
	put_nil		3
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
check_overlapped_builtin_type_4_7:
	wait_integer		4,3
	put_nil		3
	put_structured_constant		2,'$SCNST_29'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
check_overlapped_builtin_type_4_1:
	otherwise		check_overlapped_builtin_type_4_0
	try_me_else		check_overlapped_builtin_type_4_11
	wait_atom		2,none
	collect_value		4
	collect_value		3
	get_nil		1
	proceed
check_overlapped_builtin_type_4_11:
	suspend		check_overlapped_builtin_type_4_0
	module_entry		kl1cmp_command
	predicate		'$kl1cmp_reader:create_reader/5',5
'$kl1cmp_reader:create_reader/5_5_0':
	execute_external		kl1cmp_reader,create_reader,5
'$kl1cmp_reader:create_reader/5_5_1':
	suspend		'$kl1cmp_reader:create_reader/5_5_0'
	begin_const_section		kl1cmp_command
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putt
	define_atom		'Output File    : '
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putt
	define_atom		'Input File     : '
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putt
	define_atom		'Optimize lavel : '
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putt
	define_atom		' is compiled.'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putt
	define_atom		'Status is '
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		19,2
	define_integer		1664183403
	define_integer		28781
'$SCNST_15':
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		11,4
	define_integer		1970302537
	define_integer		1852776564
	define_integer		1830839651
	define_integer		6648431
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		3,7
	define_integer		1847620457
	define_integer		1629516911
	define_integer		2003790956
	define_integer		1629512805
	define_integer		1768300659
	define_integer		1847616876
	define_integer		778399073
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		11,4
	define_integer		1970302537
	define_integer		1850679412
	define_integer		1293968739
	define_integer		6648431
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_9_1':
	define_desc		19,6
	define_integer		661545283
	define_integer		1701257332
	define_integer		1768300660
	define_integer		1931502956
	define_integer		1634038388
	define_integer		11885
'$SCNST_9_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_9_1'
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_10_1':
	define_desc		27,7
	define_integer		1634890835
	define_integer		543516526
	define_integer		542060361
	define_integer		1835888483
	define_integer		543452769
	define_integer		1853189990
	define_integer		100
'$SCNST_10_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_10_1'
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_1':
	define_desc		0,3
	define_atom		=
	define_atom		module
	define_atom		[]
'$SCNST_11_3':
	define_desc		0,3
	define_atom		=
	define_atom		external
	define_atom		[]
'$SCNST_11_5':
	define_desc		0,3
	define_atom		=
	define_atom		messages
	define_atom		[]
'$SCNST_11_4':
	define_vector		'$SCNST_11_5'
	define_atom		[]
'$SCNST_11_2':
	define_vector		'$SCNST_11_3'
	define_list		'$SCNST_11_4'
'$SCNST_11_0':
	define_vector		'$SCNST_11_1'
	define_list		'$SCNST_11_2'
'$SCNST_14':
'$SCNST_11':
	define_list		'$SCNST_11_0'
'$SCNST_12_1':
	define_desc		3,7
	define_integer		1226862414
	define_integer		1769236846
	define_integer		1679846497
	define_integer		1667592809
	define_integer		1702259060
	define_integer		1868963955
	define_integer		543452789
'$SCNST_12_0':
	define_desc		0,3
	define_atom		error_message
	define_string		'$SCNST_12_1'
	define_atom		[]
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		19,5
	define_integer		1881173870
	define_integer		1768187250
	define_integer		1702125923
	define_integer		1970234912
	define_integer		25710
'$SCNST_13_0':
	define_desc		0,3
	define_atom		error_message
	define_string		'$SCNST_13_1'
	define_atom		[]
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_16_0':
	define_desc		3,9
	define_integer		1936287828
	define_integer		1919509536
	define_integer		1769235301
	define_integer		1763730806
	define_integer		1869488243
	define_integer		1818304628
	define_integer		1702326124
	define_integer		1701322852
	define_integer		539911538
'$SCNST_16':
	define_string		'$SCNST_16_0'
'$SCNST_17_0':
	define_desc		11,9
	define_integer		1936287828
	define_integer		1919509536
	define_integer		1769235301
	define_integer		1763730806
	define_integer		1869488243
	define_integer		1818304628
	define_integer		1702326124
	define_integer		1701322852
	define_integer		3040626
'$SCNST_17':
	define_string		'$SCNST_17_0'
'$SCNST_18_0':
	define_desc		11,8
	define_integer		1819309380
	define_integer		1952539497
	define_integer		1869422693
	define_integer		1701606756
	define_integer		1701868320
	define_integer		1768319331
	define_integer		1769234787
	define_integer		2125423
'$SCNST_18':
	define_string		'$SCNST_18_0'
'$SCNST_19_0':
	define_desc		0,2
	define_atom		display
	define_atom		'END.'
'$SCNST_19':
	define_vector		'$SCNST_19_0'
'$SCNST_20_0':
	define_desc		0,2
	define_atom		display
	define_atom		','
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		0,2
	define_atom		putt
	define_atom		:
'$SCNST_23':
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_1':
	define_desc		27,2
	define_integer		1869771333
	define_integer		114
'$SCNST_22_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_22_1'
'$SCNST_22':
	define_vector		'$SCNST_22_0'
'$SCNST_24_1':
	define_desc		11,2
	define_integer		1852989783
	define_integer		6778473
'$SCNST_24_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_24_1'
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_25_0':
	define_desc		0,2
	define_atom		putc
	define_integer		9
'$SCNST_26':
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_27_0':
	define_desc		3,12
	define_integer		1936287828
	define_integer		1701998624
	define_integer		1633904996
	define_integer		1864394100
	define_integer		1819436406
	define_integer		1701867617
	define_integer		1769414756
	define_integer		1646291060
	define_integer		1953261941
	define_integer		1881173609
	define_integer		1768187250
	define_integer		1702125923
'$SCNST_27':
	define_string		'$SCNST_27_0'
'$SCNST_28_1':
	define_desc		3,11
	define_integer		1936287828
	define_integer		1701998624
	define_integer		1633904996
	define_integer		1864394100
	define_integer		1819436406
	define_integer		1701867617
	define_integer		1769414756
	define_integer		1646291060
	define_integer		1953261941
	define_integer		1830841961
	define_integer		1869767521
'$SCNST_28_3':
	define_desc		0,3
	define_atom		/
	define_atom		merge
	define_integer		3
'$SCNST_28_2':
	define_vector		'$SCNST_28_3'
	define_atom		[]
'$SCNST_28_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_28_1'
	define_list		'$SCNST_28_2'
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_29_1':
	define_desc		3,11
	define_integer		1936287828
	define_integer		1701998624
	define_integer		1633904996
	define_integer		1864394100
	define_integer		1819436406
	define_integer		1701867617
	define_integer		1769414756
	define_integer		1646291060
	define_integer		1953261941
	define_integer		1830841961
	define_integer		1869767521
'$SCNST_29_3':
	define_desc		0,3
	define_atom		/
	define_atom		merge_in
	define_integer		3
'$SCNST_29_2':
	define_vector		'$SCNST_29_3'
	define_atom		[]
'$SCNST_29_0':
	define_desc		0,3
	define_atom		warning_message
	define_string		'$SCNST_29_1'
	define_list		'$SCNST_29_2'
'$SCNST_29':
	define_vector		'$SCNST_29_0'
