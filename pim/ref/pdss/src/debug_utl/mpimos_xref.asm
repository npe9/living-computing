mpimos_xref:
	module		mpimos_xref
	entry		go,2,go_2_0
	entry		go,3,go_3_0
	entry		go_f,3,go_f_3_0
	entry		go_f,4,go_f_4_0
	module_entry		mpimos_xref
	predicate		go,2
go_2_0:
	create_goal		2
	set_atom		1,success
	set_variable		2,4
	enqueue_goal		2,end_2_0
	create_goal		4
	set_variable		1,3
	set_value		2,4
	set_values_inc		3,1,2
	enqueue_goal		4,start_4_0
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	put_structured_constant		2,'$SCNST_0'
	execute_external		mpimos_window,create,2
go_2_1:
	suspend		go_2_0
	module_entry		mpimos_xref
	predicate		go,3
go_3_0:
	create_goal		2
	set_atom		1,success
	set_variable		2,5
	enqueue_goal		2,end_2_0
	create_goal		4
	set_variable		1,4
	set_value		2,5
	set_values_inc		3,1,2
	enqueue_goal		4,start_4_0
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,4
	put_value		2,3
	execute_external		mpimos_window,create,2
go_3_1:
	suspend		go_3_0
	module_entry		mpimos_xref
	predicate		go_f,3
go_f_3_0:
	create_goal		2
	set_variable		1,7
	set_variable		2,4
	enqueue_goal		2,end_2_0
	create_goal		6
	set_variable		1,5
	set_value		2,4
	set_variable		3,6
	put_func		4,2,close
	write_element_value		4,1,7
	put_list		7
	write_car_value		7,4
	write_cdr_nil		7
	set_value		4,7
	set_values_inc		5,1,2
	enqueue_goal		6,start_f_6_0
	create_goal		3
	set_value		1,6
	set_value		2,3
	set_atom		3,w
	enqueue_goal_external		mpimos_file,create,3
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,5
	put_structured_constant		2,'$SCNST_1'
	execute_external		mpimos_window,create,2
go_f_3_1:
	suspend		go_f_3_0
	module_entry		mpimos_xref
	predicate		go_f,4
go_f_4_0:
	create_goal		2
	set_variable		1,8
	set_variable		2,5
	enqueue_goal		2,end_2_0
	create_goal		6
	set_variable		1,6
	set_value		2,5
	set_variable		3,7
	put_func		5,2,close
	write_element_value		5,1,8
	put_list		8
	write_car_value		8,5
	write_cdr_nil		8
	set_value		4,8
	set_values_inc		5,1,2
	enqueue_goal		6,start_f_6_0
	create_goal		3
	set_value		1,7
	set_value		2,3
	set_atom		3,w
	enqueue_goal_external		mpimos_file,create,3
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,6
	put_value		2,4
	execute_external		mpimos_window,create,2
go_f_4_1:
	suspend		go_f_4_0
	module_entry		mpimos_xref
	predicate		start,4
start_4_0:
	put_func		5,2,flush
	write_element_void		5,1
	put_list_val_var		6,5,9
	put_structured_constant		5,'$SCNST_2'
	put_list_val_val		7,5,6
	put_func		5,2,flush
	write_element_void		5,1
	put_list_val_var		6,5,8
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,6
	create_goal		6
	set_value		1,8
	set_value		2,2
	set_variable		3,11
	set_variable		4,10
	set_variable		5,6
	set_variable		6,8
	enqueue_goal		6,referred_result_6_0
	create_goal		2
	set_variable		1,12
	set_variable		2,2
	enqueue_goal		2,init_module_table_2_0
	create_goal		7
	set_value		1,9
	set_value		2,5
	set_values_dec		3,12,3
	set_value		6,6
	set_variable		7,6
	enqueue_goal_external		mpimos_xref_table,module_table,7
	create_goal		6
	set_value		1,1
	set_value		2,7
	set_values_inc		3,2,2
	set_variable		5,2
	set_atom		6,success
	enqueue_goal		6,loop_6_0
	create_goal		2
	set_variable		1,5
	set_value		2,8
	enqueue_goal		2,output_option_2_0
	put_value		1,4
	put_values_dec		3,6,2
	execute		4,option_4_0
start_4_1:
	suspend		start_4_0
	module_entry		mpimos_xref
	predicate		start_f,6
start_f_6_0:
	put_func		7,2,flush
	write_element_void		7,1
	put_list_val_var		8,7,10
	put_structured_constant		7,'$SCNST_3'
	put_list_val_val		9,7,8
	put_func		7,2,flush
	write_element_void		7,1
	put_list_val_val		8,7,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,8
	create_goal		6
	set_values_inc		1,3,2
	set_variable		3,11
	set_variable		4,8
	set_variable		5,3
	set_variable		6,7
	enqueue_goal		6,referred_result_6_0
	create_goal		2
	set_variable		1,12
	set_variable		2,4
	enqueue_goal		2,init_module_table_2_0
	create_goal		7
	set_value		1,10
	set_value		2,2
	set_values_dec		3,12,2
	set_value		5,8
	set_value		6,3
	set_variable		7,3
	enqueue_goal_external		mpimos_xref_table,module_table,7
	create_goal		6
	set_value		1,1
	set_value		2,9
	set_values_inc		3,4,2
	set_variable		5,2
	set_atom		6,success
	enqueue_goal		6,loop_6_0
	create_goal		2
	set_variable		1,4
	set_value		2,7
	enqueue_goal		2,output_file_option_2_0
	put_value		1,6
	execute		4,option_4_0
start_f_6_1:
	suspend		start_f_6_0
	module_entry		mpimos_xref
	predicate		end,2
end_2_0:
	try_me_else		end_2_1
	wait_atom		1,success
	put_func		1,2,getl
	write_element_void		1,1
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		4,1,3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	get_list_value		2,1
	proceed
end_2_1:
	suspend		end_2_0
	module_entry		mpimos_xref
	predicate		option,4
option_4_0:
	try_me_else		option_4_1
	jump_on_non_atom		1,option_4_3
	branch_on_atom		1,2,option_4_1
	bucket_entry_a		short,option_4_4
	bucket_entry_a		update,option_4_5
option_4_4:
	get_atom		2,short
	get_atom		3,protect
	get_atom		4,check
	proceed
option_4_5:
	get_atom		2,long
	get_atom		3,update
	get_atom		4,check
	proceed
option_4_3:
	check_vector		1,2,option_4_1
	read_element		1,0,5
	atom		5
	branch_on_atom		5,2,option_4_1
	bucket_entry_a		short,option_4_7
	bucket_entry_a		update,option_4_8
option_4_7:
	read_element		1,1,6
	collect_vector		1
	get_atom		2,short
	put_value		1,6
	put_void		2
	execute		4,option_4_0
option_4_8:
	read_element		1,1,6
	collect_vector		1
	get_atom		3,update
	put_value		1,6
	put_void		3
	execute		4,option_4_0
option_4_1:
	otherwise		option_4_0
	get_atom		2,long
	get_atom		3,protect
	get_value		4,1
	proceed
option_4_15:
	suspend		option_4_0
	module_entry		mpimos_xref
	predicate		output_option,2
output_option_2_0:
	try_me_else		output_option_2_1
	jump_on_non_list		1,output_option_2_3
	get_value		2,1
	proceed
output_option_2_3:
	is_atom		1,output_option_2_1
	hash_on_atom		1,11,output_option_2_1
	bucket_entry_a		[],output_option_2_4
	bucket_entry_a		a,output_option_2_5
	bucket_entry_a		all,output_option_2_6
	bucket_entry_a		b,output_option_2_7
	bucket_entry_a		builtin,output_option_2_8
	bucket_entry_a		g,output_option_2_9
	bucket_entry_a		guard,output_option_2_10
	bucket_entry_a		l,output_option_2_11
	bucket_entry_a		list,output_option_2_12
	bucket_entry_a		s,output_option_2_13
	bucket_entry_a		system,output_option_2_14
output_option_2_4:
	get_nil		2
	proceed
output_option_2_5:
	put_structured_constant		1,'$SCNST_5'
	get_value		2,1
	proceed
output_option_2_6:
	put_structured_constant		1,'$SCNST_6'
	get_value		2,1
	proceed
output_option_2_7:
	put_structured_constant		1,'$SCNST_7'
	get_value		2,1
	proceed
output_option_2_8:
	put_structured_constant		1,'$SCNST_8'
	get_value		2,1
	proceed
output_option_2_9:
	put_structured_constant		1,'$SCNST_9'
	get_value		2,1
	proceed
output_option_2_10:
	put_structured_constant		1,'$SCNST_10'
	get_value		2,1
	proceed
output_option_2_11:
	put_structured_constant		1,'$SCNST_11'
	get_value		2,1
	proceed
output_option_2_12:
	put_structured_constant		1,'$SCNST_12'
	get_value		2,1
	proceed
output_option_2_13:
	put_structured_constant		1,'$SCNST_13'
	get_value		2,1
	proceed
output_option_2_14:
	put_structured_constant		1,'$SCNST_14'
	get_value		2,1
	proceed
output_option_2_1:
	otherwise		output_option_2_0
	collect_value		1
	get_atom		2,check
	proceed
output_option_2_18:
	suspend		output_option_2_0
	module_entry		mpimos_xref
	predicate		output_file_option,2
output_file_option_2_0:
	try_me_else		output_file_option_2_1
	jump_on_non_list		1,output_file_option_2_3
	get_value		2,1
	proceed
output_file_option_2_3:
	is_atom		1,output_file_option_2_1
	hash_on_atom		1,9,output_file_option_2_1
	bucket_entry_a		[],output_file_option_2_4
	bucket_entry_a		a,output_file_option_2_5
	bucket_entry_a		all,output_file_option_2_6
	bucket_entry_a		b,output_file_option_2_7
	bucket_entry_a		builtin,output_file_option_2_8
	bucket_entry_a		g,output_file_option_2_9
	bucket_entry_a		guard,output_file_option_2_10
	bucket_entry_a		s,output_file_option_2_11
	bucket_entry_a		system,output_file_option_2_12
output_file_option_2_4:
	get_nil		2
	proceed
output_file_option_2_5:
	put_structured_constant		1,'$SCNST_15'
	get_value		2,1
	proceed
output_file_option_2_6:
	put_structured_constant		1,'$SCNST_16'
	get_value		2,1
	proceed
output_file_option_2_7:
	put_structured_constant		1,'$SCNST_17'
	get_value		2,1
	proceed
output_file_option_2_8:
	put_structured_constant		1,'$SCNST_18'
	get_value		2,1
	proceed
output_file_option_2_9:
	put_structured_constant		1,'$SCNST_19'
	get_value		2,1
	proceed
output_file_option_2_10:
	put_structured_constant		1,'$SCNST_20'
	get_value		2,1
	proceed
output_file_option_2_11:
	put_structured_constant		1,'$SCNST_21'
	get_value		2,1
	proceed
output_file_option_2_12:
	put_structured_constant		1,'$SCNST_22'
	get_value		2,1
	proceed
output_file_option_2_1:
	otherwise		output_file_option_2_0
	collect_value		1
	put_structured_constant		1,'$SCNST_23'
	get_value		2,1
	proceed
output_file_option_2_16:
	suspend		output_file_option_2_0
	module_entry		mpimos_xref
	predicate		loop,6
loop_6_0:
	try_me_else		loop_6_1
	jump_on_non_list_var_var		4,loop_6_3,7,8
	wait		6
	collect_value		6
	put_vector		6,2
	write_element_variable		6,0,10
	write_element_variable		6,1,9
	get_vector_value		3,6
	put_func		3,2,flush
	write_element_variable		3,1,12
	put_reused_list_val_var		4,4,3,11
	put_structured_constant		3,'$SCNST_24'
	put_list_val_val		6,3,4
	put_func		3,2,putt
	write_element_marked_value		3,1,7
	put_list_val_val		4,3,6
	put_structured_constant		3,'$SCNST_25'
	put_list_val_val		6,3,4
	put_structured_constant		3,'$SCNST_26'
	put_list_val_val		4,3,6
	get_list_value		1,4
	put_list		1
	write_car_atom		1,nl
	write_cdr_variable		1,3
	create_goal		6
	set_values_dec		1,3,2
	set_value		3,10
	set_value		4,8
	set_marked_value		5,5
	set_variable		6,2
	enqueue_goal		6,loop_6_0
	create_goal		9
	set_value		1,11
	set_value		2,1
	set_value		3,9
	set_variable		4,1
	set_value		5,7
	set_value		6,5
	set_value		7,2
	set_value		8,12
	set_variable		9,4
	enqueue_goal		9,open_check_9_0
	put_value		2,7
	put_atom		3,r
	execute_external		mpimos_file,create,4
loop_6_3:
	check_nil		4,loop_6_1
	collect_value		6
	collect_value		5
	get_nil		3
	get_value		1,2
	proceed
loop_6_1:
	suspend		loop_6_0
	module_entry		mpimos_xref
	predicate		open_check,9
open_check_9_0:
	try_me_else		open_check_9_1
	wait_atom		8,done
	jump_on_non_atom		9,open_check_9_4
	test_atom		9,success,open_check_9_1
	b_merge		8,9
	b_merge		11,10
	put_vector		14,2
	write_element_variable		14,0,12
	write_element_variable		14,1,13
	get_vector_value		11,14
	put_vector		15,2
	write_element_variable		15,0,11
	write_element_variable		15,1,14
	get_vector_value		1,15
	create_goal		4
	set_variable		1,1
	set_value		2,2
	set_variable		3,15
	set_variable		4,2
	enqueue_goal_external		mpimos_xref_table,predicate_table,4
	create_goal		12
	set_value		1,14
	set_value		2,1
	set_variable		3,1
	set_nil		4
	set_value		5,15
	set_value		6,3
	set_value		7,6
	set_variable		8,3
	set_values_dec		9,3,2
	set_value		11,5
	set_atom		12,done
	enqueue_goal		12,pre_xref_12_0
	create_goal		1
	set_value		1,9
	enqueue_goal_external		kl1cmp_macro_arg,init_macro_table,1
	create_goal		6
	set_variable		1,2
	set_nil		2
	set_value		3,13
	set_nil		4
	set_value		5,8
	set_value		6,1
	enqueue_goal_external		kl1cmp_macro,generate_macro_expander,6
	create_goal		5
	set_value		1,4
	put_func		1,2,close
	write_element_value		1,1,7
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	set_value		2,3
	set_value		3,12
	set_nil		4
	set_value		5,2
	enqueue_goal_external		kl1cmp_reader,create_reader,5
	put_values_dec		1,11,2
	execute		2,message_distributer_2_0
open_check_9_4:
	check_vector		9,2,open_check_9_1
	read_element		9,0,10
	wait_atom		10,error
	read_element		9,1,8
	collect_value		6
	collect_value		5
	get_nil		3
	put_reused_func		3,9,flush
	write_element_void		3,1
	put_list_val_val		5,3,2
	put_structured_constant		2,'$SCNST_27'
	put_list_val_val		3,2,5
	put_func		2,2,putt
	write_element_marked_value		2,1,8
	put_list_val_val		5,2,3
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		3,2,5
	get_list_value		1,3
	get_nil		4
	put_func		1,2,error
	write_element_value		1,1,8
	get_vector_value		7,1
	proceed
open_check_9_1:
	suspend		open_check_9_0
	module_entry		mpimos_xref
	predicate		message_distributer,2
message_distributer_2_0:
	try_me_else		message_distributer_2_1
	jump_on_non_list		2,message_distributer_2_3
	read_car		2,3
	jump_on_non_atom		3,message_distributer_2_5
	test_atom		3,ttynl,message_distributer_2_1
	read_cdr		2,4
	put_reused_list		3,2
	write_car_atom		3,nl
	write_cdr_variable		3,2
	get_list_value		1,3
	put_value		1,2
	put_value		2,4
	execute		2,message_distributer_2_0
message_distributer_2_5:
	is_vector		3,message_distributer_2_1
	jump_on_arity		3,4,message_distributer_2_1
	table_entry		message_distributer_2_1
	table_entry		message_distributer_2_1
	table_entry		message_distributer_2_6
	table_entry		message_distributer_2_7
message_distributer_2_6:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,message_distributer_2_1
	bucket_entry_a		display,message_distributer_2_9
	bucket_entry_a		ttyput,message_distributer_2_10
message_distributer_2_9:
	read_cdr		2,5
	read_element		3,1,6
	put_reused_func		3,3,putt
	write_element_value		3,1,6
	get_reused_list_val_var		1,4,2,3,2
	put_value		1,2
	put_value		2,5
	execute		2,message_distributer_2_0
message_distributer_2_10:
	read_cdr		2,5
	read_element		3,1,6
	put_reused_func		3,3,putc
	write_element_value		3,1,6
	get_reused_list_val_var		1,4,2,3,2
	put_value		1,2
	put_value		2,5
	execute		2,message_distributer_2_0
message_distributer_2_7:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,message_distributer_2_1
	bucket_entry_a		error_message,message_distributer_2_12
	bucket_entry_a		warning_message,message_distributer_2_13
message_distributer_2_12:
	read_cdr		2,5
	read_elements_inc		3,1,6,2
	collect_list		2
	collect_vector		3
	put_vector		4,2
	write_element_variable		4,0,3
	write_element_variable		4,1,2
	get_vector_value		1,4
	create_goal		2
	set_value		1,3
	set_value		2,5
	enqueue_goal		2,message_distributer_2_0
	put_value		1,2
	put_values_inc		2,6,2
	execute		3,error_3_0
message_distributer_2_13:
	read_cdr		2,5
	read_elements_inc		3,1,6,2
	collect_list		2
	collect_vector		3
	put_vector		4,2
	write_element_variable		4,0,3
	write_element_variable		4,1,2
	get_vector_value		1,4
	create_goal		2
	set_value		1,3
	set_value		2,5
	enqueue_goal		2,message_distributer_2_0
	put_value		1,2
	put_values_inc		2,6,2
	execute		3,warning_3_0
message_distributer_2_3:
	check_nil		2,message_distributer_2_1
	get_nil		1
	proceed
message_distributer_2_1:
	otherwise		message_distributer_2_0
	try_me_else		message_distributer_2_26
	wait_list_var_var		2,3,4
	put_reused_list		2,2
	write_car_atom		2,nl
	write_cdr_variable		2,6
	put_func		5,2,putt
	write_element_value		5,1,3
	put_list_val_val		3,5,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_29'
	put_list_val_val		5,3,2
	get_list_value		1,5
	put_value		1,6
	put_value		2,4
	execute		2,message_distributer_2_0
message_distributer_2_26:
	suspend		message_distributer_2_0
	module_entry		mpimos_xref
	predicate		error,3
error_3_0:
	put_structured_constant		4,'$SCNST_30'
	put_list_val_var		5,4,6
	put_func		4,2,putb
	write_element_value		4,1,2
	put_list_val_val		2,4,5
	put_structured_constant		4,'$SCNST_31'
	put_list_val_val		5,4,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	get_list_value		1,2
	put_value		1,6
	put_value		2,3
	execute		2,output_error_2_0
error_3_1:
	suspend		error_3_0
	module_entry		mpimos_xref
	predicate		warning,3
warning_3_0:
	put_structured_constant		4,'$SCNST_32'
	put_list_val_var		5,4,6
	put_func		4,2,putb
	write_element_value		4,1,2
	put_list_val_val		2,4,5
	put_structured_constant		4,'$SCNST_33'
	put_list_val_val		5,4,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	get_list_value		1,2
	put_value		1,6
	put_value		2,3
	execute		2,output_error_2_0
warning_3_1:
	suspend		warning_3_0
	module_entry		mpimos_xref
	predicate		output_error,2
output_error_2_0:
	try_me_else		output_error_2_1
	jump_on_non_list_var_var		2,output_error_2_3,3,4
	put_func		5,2,puttq
	write_element_value		5,1,3
	get_reused_list_val_var		1,3,2,5,2
	put_value		1,2
	put_value		2,4
	execute		2,output_error_2_0
output_error_2_3:
	check_nil		2,output_error_2_1
	put_nil		2
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	get_list_value		1,3
	proceed
output_error_2_1:
	otherwise		output_error_2_0
	put_nil		4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,4
	put_func		4,2,puttq
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	get_list_value		1,2
	proceed
output_error_2_8:
	suspend		output_error_2_0
	module_entry		mpimos_xref
	predicate		pre_xref,12
pre_xref_12_0:
	try_me_else		pre_xref_12_1
	wait		12
	put_func		12,3,read_predicate
	write_element_variable		12,1,14
	write_element_variable		12,2,13
	get_list_val_var		3,15,12,12
	put_value		3,12
	put_value		12,14
	execute		13,pre_xref0_13_0
pre_xref_12_1:
	suspend		pre_xref_12_0
	module_entry		mpimos_xref
	predicate		pre_xref0,13
pre_xref0_13_0:
	try_me_else		pre_xref0_13_1
	atom		13
	branch_on_atom		13,2,pre_xref0_13_1
	bucket_entry_a		directive,pre_xref0_13_3
	bucket_entry_a		end_of_file,pre_xref0_13_4
pre_xref0_13_3:
	execute		12,pre_xref_directive_12_0
pre_xref0_13_4:
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	collect_value		7
	get_nil		5
	get_nil		6
	get_value		3,4
	put_func		3,2,flush
	write_element_void		3,1
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_structured_constant		3,'$SCNST_34'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
pre_xref0_13_1:
	otherwise		pre_xref0_13_0
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	put_func		8,2,flush
	write_element_void		8,1
	put_list_val_var		9,8,10
	put_list		8
	write_car_atom		8,nl
	write_cdr_value		8,9
	put_structured_constant		9,'$SCNST_35'
	put_list_val_val		11,9,8
	get_list_value		1,11
	put_value		1,10
	put_atom		8,'??module??'
	put_values_inc		9,12,2
	execute		10,xref0_10_0
pre_xref0_13_7:
	suspend		pre_xref0_13_0
	module_entry		mpimos_xref
	predicate		pre_xref_directive,12
pre_xref_directive_12_0:
	try_me_else		pre_xref_directive_12_1
	jump_on_non_list		12,pre_xref_directive_12_3
	read_car		12,13
	wait_vector		13,2
	read_element		13,0,14
	wait_atom		14,:-
	read_element		13,1,15
	wait_vector		15,2
	read_element		15,0,16
	atom		16
	branch_on_atom		16,2,pre_xref_directive_12_1
	bucket_entry_a		module,pre_xref_directive_12_8
	bucket_entry_a		public,pre_xref_directive_12_9
pre_xref_directive_12_8:
	read_cdr		12,17
	read_element		15,1,18
	atom		18
	collect_vector		15
	put_func		14,6,entry
	write_element_marked_value		14,1,18
	write_element_marked_value		14,2,8
	write_elements_inc		14,3,10,2
	write_element_variable		14,5,15
	get_reused_list_val_var		6,10,12,14,11
	put_reused_func		6,13,flush
	write_element_variable		6,1,12
	put_list_val_var		10,6,6
	create_goal		12
	set_value		1,6
	set_values_inc		2,2,4
	set_value		6,11
	set_value		7,7
	set_value		8,18
	set_values_inc		9,8,2
	set_value		11,17
	set_value		12,12
	enqueue_goal		12,pre_xref_module_wait_12_0
	put_value		2,10
	put_value		3,15
	execute		3,wait_module_entry_3_0
pre_xref_directive_12_9:
	read_cdr		12,17
	read_element		15,1,14
	put_reused_vector		18,13
	write_element_variable		18,0,16
	write_element_variable		18,1,13
	get_vector_value		5,18
	put_reused_func		5,15,flush
	write_element_variable		5,1,15
	put_reused_list_val_var		12,12,5,5
	create_goal		13
	set_value		1,5
	set_values_inc		2,2,3
	set_value		5,16
	set_values_inc		6,6,3
	set_variable		9,5
	set_values_inc		10,10,2
	set_value		12,17
	set_value		13,15
	enqueue_goal		13,pre_xref_directive_wait_13_0
	put_values_inc		2,12,2
	put_value		4,9
	put_value		6,14
	execute		6,public_entry_6_0
pre_xref_directive_12_3:
	check_nil		12,pre_xref_directive_12_1
	collect_value		11
	collect_value		10
	collect_value		9
	collect_value		8
	put_func		8,2,flush
	write_element_void		8,1
	put_list_val_var		9,8,10
	put_list		8
	write_car_atom		8,nl
	write_cdr_value		8,9
	put_structured_constant		9,'$SCNST_36'
	put_list_val_val		11,9,8
	get_list_value		1,11
	put_value		1,10
	put_atom		8,'??module??'
	put_atom		9,done
	execute		9,xref_9_0
pre_xref_directive_12_1:
	suspend		pre_xref_directive_12_0
	module_entry		mpimos_xref
	predicate		pre_xref_directive_wait,13
pre_xref_directive_wait_13_0:
	try_me_else		pre_xref_directive_wait_13_1
	wait		13
	execute		12,pre_xref_directive_12_0
pre_xref_directive_wait_13_1:
	suspend		pre_xref_directive_wait_13_0
	module_entry		mpimos_xref
	predicate		pre_xref_module,11
pre_xref_module_11_0:
	try_me_else		pre_xref_module_11_1
	jump_on_non_list		11,pre_xref_module_11_3
	read_car		11,12
	wait_vector		12,2
	read_element		12,0,13
	wait_atom		13,:-
	read_element		12,1,14
	wait_vector		14,2
	read_element		14,0,15
	atom		15
	branch_on_atom		15,2,pre_xref_module_11_1
	bucket_entry_a		module,pre_xref_module_11_8
	bucket_entry_a		public,pre_xref_module_11_9
pre_xref_module_11_8:
	read_cdr		11,16
	read_element		14,1,17
	atom		17
	put_reused_func		12,12,flush
	write_element_variable		12,1,18
	put_reused_list_val_var		11,11,12,15
	put_structured_constant		12,'$SCNST_37'
	put_list_val_val		13,12,11
	put_reused_func		11,14,putt
	write_element_value		11,1,17
	put_list_val_val		12,11,13
	put_structured_constant		11,'$SCNST_38'
	put_list_val_val		13,11,12
	put_structured_constant		11,'$SCNST_39'
	put_list_val_val		12,11,13
	get_list_value		1,12
	put_value		1,15
	put_value		11,16
	put_value		12,18
	execute		12,pre_xref_module_wait_12_0
pre_xref_module_11_9:
	read_cdr		11,16
	read_element		14,1,13
	put_reused_vector		17,12
	write_element_variable		17,0,15
	write_element_variable		17,1,12
	get_vector_value		5,17
	put_reused_func		5,14,flush
	write_element_variable		5,1,14
	put_reused_list_val_var		11,11,5,5
	create_goal		12
	set_value		1,5
	set_values_inc		2,2,3
	set_value		5,15
	set_values_inc		6,6,4
	set_variable		10,5
	set_value		11,16
	set_value		12,14
	enqueue_goal		12,pre_xref_module_wait_12_0
	put_values_inc		2,11,2
	put_value		4,10
	put_value		6,13
	execute		6,public_entry_6_0
pre_xref_module_11_3:
	check_nil		11,pre_xref_module_11_1
	get_nil		10
	put_func		10,2,flush
	write_element_variable		10,1,12
	put_list_val_var		11,10,10
	create_goal		9
	set_value		1,10
	set_values_inc		2,2,7
	set_value		9,12
	enqueue_goal		9,xref_9_0
	put_value		2,11
	put_value		3,9
	execute		3,wait_public_3_0
pre_xref_module_11_1:
	suspend		pre_xref_module_11_0
	module_entry		mpimos_xref
	predicate		pre_xref_module_wait,12
pre_xref_module_wait_12_0:
	try_me_else		pre_xref_module_wait_12_1
	wait		12
	execute		11,pre_xref_module_11_0
pre_xref_module_wait_12_1:
	suspend		pre_xref_module_wait_12_0
	module_entry		mpimos_xref
	predicate		xref,9
xref_9_0:
	try_me_else		xref_9_1
	wait_atom		9,done
	put_func		9,3,read_predicate
	write_element_variable		9,1,11
	write_element_variable		9,2,10
	get_list_val_var		3,12,9,9
	put_value		3,9
	put_value		9,11
	execute		10,xref0_10_0
xref_9_1:
	suspend		xref_9_0
	module_entry		mpimos_xref
	predicate		xref0,10
xref0_10_0:
	try_me_else		xref0_10_1
	jump_on_non_list_var_var		9,xref0_10_3,14,11
	wait_vector		14,2
	read_element		14,0,12
	wait_atom		12,:-
	read_element		14,1,12
	wait_atom		10,directive
	put_structured_constant		10,'$SCNST_40'
	put_reused_list_val_var		9,9,10,13
	put_reused_func		10,14,putt
	write_element_value		10,1,12
	put_list_val_val		12,10,9
	put_structured_constant		9,'$SCNST_41'
	put_list_val_val		10,9,12
	put_list		9
	write_car_atom		9,nl
	write_cdr_value		9,10
	get_list_value		1,9
	put_value		1,13
	put_value		9,11
	put_atom		10,directive
	execute		10,xref0_10_0
xref0_10_3:
	check_nil		9,xref0_10_1
	wait_atom		10,directive
	put_atom		9,done
	execute		9,xref_9_0
xref0_10_1:
	try_me_else		xref0_10_4
	jump_on_non_atom		10,xref0_10_6
	test_atom		10,end_of_file,xref0_10_4
	collect_value		9
	collect_value		8
	collect_value		7
	get_nil		5
	get_nil		6
	get_value		3,4
	get_value		1,2
	proceed
xref0_10_6:
	check_vector		10,3,xref0_10_4
	read_element		10,0,11
	wait_atom		11,/
	read_elements_inc		10,1,11,2
	put_vector		13,2
	write_element_variable		13,0,15
	write_element_variable		13,1,14
	put_vector		18,2
	write_element_variable		18,0,17
	write_element_variable		18,1,16
	get_vector_value		6,18
	put_func		6,4,entry
	write_element_marked_value		6,1,11
	write_element_marked_value		6,2,12
	write_element_variable		6,3,18
	put_list_val_val		19,6,13
	get_list_value		5,19
	put_func		5,2,flush
	write_element_variable		5,1,13
	put_list_val_var		6,5,5
	create_goal		9
	set_value		1,5
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,15
	set_value		6,17
	set_marked_value		7,7
	set_marked_value		8,8
	set_value		9,13
	enqueue_goal		9,xref_9_0
	create_goal		5
	set_variable		1,4
	set_values_inc		2,6,2
	set_values_inc		4,11,2
	enqueue_goal		5,predicate_info_5_0
	create_goal		12
	set_variable		1,2
	set_values_dec		2,4,2
	set_value		4,5
	set_value		5,14
	set_value		6,16
	set_values_inc		7,7,2
	set_integer		9,1
	set_void		10
	set_value		11,9
	put_reused_func		3,10,/
	write_elements_inc		3,1,11,2
	set_value		12,3
	enqueue_goal		12,xref_predicate_12_0
	put_value		3,18
	execute		3,wait_entry_3_0
xref0_10_4:
	suspend		xref0_10_0
	module_entry		mpimos_xref
	predicate		xref_predicate,12
xref_predicate_12_0:
	try_me_else		xref_predicate_12_1
	wait		11
	switch_on_type		11,xref_predicate_12_2,xref_predicate_12_1,xref_predicate_12_3,xref_predicate_12_4,xref_predicate_12_1,xref_predicate_12_1
xref_predicate_12_3:
	read_car		11,13
	read_cdr		11,14
	collect_list		11
	put_vector		16,2
	write_element_variable		16,0,15
	write_element_variable		16,1,11
	get_vector_value		5,16
	put_vector		17,2
	write_element_variable		17,0,5
	write_element_variable		17,1,16
	get_vector_value		6,17
	create_goal		12
	set_variable		1,17
	set_value		2,2
	set_variable		3,6
	set_value		4,4
	set_value		5,15
	set_value		6,5
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,15
	set_value		10,10
	set_value		11,14
	set_marked_value		12,12
	enqueue_goal		12,xref_predicate_12_0
	put_value		2,17
	put_value		4,6
	put_value		5,11
	put_value		6,16
	put_value		10,15
	put_value		11,13
	execute		12,xref_predicate_12_0
xref_predicate_12_2:
	branch_on_atom		11,3,xref_predicate_12_1
	bucket_entry_a		[],xref_predicate_12_5
	bucket_entry_a		alternatively,xref_predicate_12_6
	bucket_entry_a		otherwise,xref_predicate_12_7
xref_predicate_12_5:
	collect_value		12
	collect_value		8
	collect_value		7
	get_nil		5
	get_nil		6
	get_value		9,10
	get_value		3,4
	get_value		1,2
	proceed
xref_predicate_12_6:
	collect_value		12
	collect_value		8
	collect_value		7
	get_nil		5
	get_nil		6
	get_value		9,10
	get_value		3,4
	get_value		1,2
	proceed
xref_predicate_12_7:
	collect_value		12
	collect_value		8
	collect_value		7
	get_nil		5
	get_nil		6
	get_value		9,10
	get_value		3,4
	get_value		1,2
	proceed
xref_predicate_12_4:
	test_arity		11,3,xref_predicate_12_1
	read_element		11,0,13
	wait_atom		13,:-
	read_element		11,1,13
	read_element		11,2,16
	wait_vector		16,3
	read_element		16,0,14
	wait_atom		14,'|'
	read_elements_inc		16,1,14,2
	collect_value		13
	collect_value		7
	put_vector		17,2
	write_element_variable		17,0,13
	write_element_variable		17,1,7
	get_vector_value		6,17
	get_value		3,4
	put_marked_value		3,9
	b_increment		3,3
	get_value		3,10
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	set_value		4,13
	set_marked_value		5,8
	put_reused_func		2,11,/
	write_element_marked_value		2,1,12
	write_element_value		2,2,9
	set_value		6,2
	set_value		7,15
	enqueue_goal		7,body_check_7_0
	put_reused_func		5,16,/
	write_element_value		5,1,12
	write_element_value		5,2,9
	put_value		2,3
	put_values_inc		3,7,2
	put_value		6,14
	execute		6,guard_check_6_0
xref_predicate_12_1:
	suspend		xref_predicate_12_0
	module_entry		mpimos_xref
	predicate		wait_module_entry,3
wait_module_entry_3_0:
	try_me_else		wait_module_entry_3_1
	wait_vector		3,2
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,wait_module_entry_3_1
	bucket_entry_a		doubly,wait_module_entry_3_4
	bucket_entry_a		success,wait_module_entry_3_5
wait_module_entry_3_4:
	read_element		3,1,5
	put_structured_constant		4,'$SCNST_42'
	put_list_val_val		6,4,2
	put_reused_func		2,3,putt
	write_element_value		2,1,5
	put_list_val_val		3,2,6
	put_structured_constant		2,'$SCNST_43'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
wait_module_entry_3_5:
	read_element		3,1,5
	put_structured_constant		4,'$SCNST_44'
	put_list_val_val		6,4,2
	put_reused_func		2,3,putt
	write_element_value		2,1,5
	put_list_val_val		3,2,6
	put_structured_constant		2,'$SCNST_45'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
wait_module_entry_3_1:
	suspend		wait_module_entry_3_0
	module_entry		mpimos_xref
	predicate		wait_public,3
wait_public_3_0:
	try_me_else		wait_public_3_1
	wait_nil		3
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_structured_constant		2,'$SCNST_46'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
wait_public_3_1:
	try_me_else		wait_public_3_3
	put_nil		4
	g_diff		3,4
	collect_value		4
	put_structured_constant		4,'$SCNST_47'
	get_list_val_var		1,6,4,5
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_structured_constant		2,'$SCNST_48'
	put_list_val_val		4,2,1
	put_values_dec		1,5,2
	execute		3,out_convert_3_0
wait_public_3_3:
	suspend		wait_public_3_0
	module_entry		mpimos_xref
	predicate		wait_entry,3
wait_entry_3_0:
	try_me_else		wait_entry_3_1
	wait_vector		3,3
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,wait_entry_3_1
	bucket_entry_a		doubly,wait_entry_3_4
	bucket_entry_a		none,wait_entry_3_5
wait_entry_3_4:
	read_elements_inc		3,1,5,2
	put_structured_constant		4,'$SCNST_49'
	put_list_val_val		7,4,2
	put_reused_func		2,3,/
	write_elements_inc		2,1,5,2
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,7
	put_structured_constant		3,'$SCNST_50'
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	get_list_value		1,2
	proceed
wait_entry_3_5:
	read_elements_inc		3,1,5,2
	collect_value		6
	collect_value		5
	collect_vector		3
	get_value		1,2
	proceed
wait_entry_3_1:
	otherwise		wait_entry_3_0
	try_me_else		wait_entry_3_11
	wait_vector		3,3
	read_elements_inc		3,0,4,3
	collect_value		4
	put_structured_constant		4,'$SCNST_51'
	put_list_val_val		7,4,2
	put_reused_func		2,3,/
	write_elements_inc		2,1,5,2
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,7
	put_structured_constant		3,'$SCNST_52'
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	get_list_value		1,2
	proceed
wait_entry_3_11:
	suspend		wait_entry_3_0
	module_entry		mpimos_xref
	predicate		predicate_info,5
predicate_info_5_0:
	try_me_else		predicate_info_5_1
	atom		3
	branch_on_atom		3,2,predicate_info_5_1
	bucket_entry_a		long,predicate_info_5_3
	bucket_entry_a		short,predicate_info_5_4
predicate_info_5_3:
	put_structured_constant		3,'$SCNST_53'
	put_list_val_val		6,3,2
	put_func		2,3,/
	write_elements_inc		2,1,4,2
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,6
	get_list_value		1,2
	proceed
predicate_info_5_4:
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
predicate_info_5_1:
	suspend		predicate_info_5_0
	module_entry		mpimos_xref
	predicate		public_entry,6
public_entry_6_0:
	try_me_else		public_entry_6_1
	wait_vector		6,3
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,public_entry_6_1
	bucket_entry_a		',',public_entry_6_4
	bucket_entry_a		/,public_entry_6_5
public_entry_6_4:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_vector		10,2
	write_element_variable		10,0,7
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,7
	set_variable		4,7
	set_value		5,5
	set_value		6,9
	enqueue_goal		6,public_entry_6_0
	put_value		2,3
	put_value		3,6
	put_values_inc		5,7,2
	execute		6,public_entry_6_0
public_entry_6_5:
	read_elements_inc		6,1,8,2
	atom		8
	integer		9
	put_integer		10,0
	g_not_less_than		9,10
	collect_vector		6
	put_nil		6
	get_value		1,2
	put_func		1,4,call
	write_element_marked_value		1,1,8
	write_element_marked_value		1,2,9
	write_element_atom		1,3,'public declaration'
	put_list_val_val		2,1,6
	get_list_value		3,2
	put_vector		1,2
	write_elements_inc		1,0,8,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
public_entry_6_1:
	otherwise		public_entry_6_0
	get_nil		3
	get_value		4,5
	put_structured_constant		3,'$SCNST_54'
	put_list_val_val		4,3,2
	put_func		2,2,putt
	write_element_value		2,1,6
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_55'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
public_entry_6_11:
	suspend		public_entry_6_0
	module_entry		mpimos_xref
	predicate		guard_check,6
guard_check_6_0:
	try_me_else		guard_check_6_1
	jump_on_non_atom		6,guard_check_6_3
	test_atom		6,true,guard_check_6_1
	collect_value		5
	collect_value		4
	get_nil		3
	get_value		1,2
	proceed
guard_check_6_3:
	check_vector		6,3,guard_check_6_1
	read_element		6,0,7
	atom		7
	hash_on_atom		7,4,guard_check_6_1
	bucket_entry_a		$:=,guard_check_6_5
	bucket_entry_a		',',guard_check_6_6
	bucket_entry_a		:=,guard_check_6_7
	bucket_entry_a		=,guard_check_6_8
guard_check_6_5:
	read_elements_inc		6,1,8,2
	collect_value		8
	get_value		1,2
	put_reused_func		2,6,:
	write_elements_inc		2,1,4,2
	put_value		1,3
	put_atom		3,guard_builtin
	put_value		4,9
	execute		4,float_expression_4_0
guard_check_6_6:
	read_elements_inc		6,1,8,2
	collect_vector		6
	put_vector		10,2
	write_element_variable		10,0,7
	write_element_variable		10,1,6
	get_vector_value		3,10
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,7
	set_marked_value		4,4
	set_marked_value		5,5
	set_value		6,9
	enqueue_goal		6,guard_check_6_0
	put_value		2,3
	put_value		3,6
	put_value		6,8
	execute		6,guard_check_6_0
guard_check_6_7:
	read_elements_inc		6,1,8,2
	collect_value		8
	get_value		1,2
	put_reused_func		2,6,:
	write_elements_inc		2,1,4,2
	put_value		1,3
	put_atom		3,guard_builtin
	put_value		4,9
	execute		4,expression_4_0
guard_check_6_8:
	read_elements_inc		6,1,8,2
	collect_value		9
	collect_value		8
	collect_value		5
	collect_value		4
	collect_vector		6
	get_nil		3
	get_value		1,2
	proceed
guard_check_6_1:
	otherwise		guard_check_6_0
	create_goal		9
	set_values_inc		1,1,5
	set_marked_value		6,6
	set_variable		7,2
	set_variable		8,3
	set_variable		9,7
	enqueue_goal		9,guard_builtin_check_9_0
	put_value		1,6
	put_void		4
	put_void		5
	put_void		6
	execute_external		kl1cmp_blttbl,builtin,7
guard_check_6_16:
	suspend		guard_check_6_0
	module_entry		mpimos_xref
	predicate		guard_builtin_check,9
guard_builtin_check_9_0:
	try_me_else		guard_builtin_check_9_1
	jump_on_non_atom		6,guard_builtin_check_9_3
	put_atom		10,none
	g_diff		9,10
	put_atom		10,relop
	g_diff		9,10
	put_atom		10,float_relop
	g_diff		9,10
	collect_value		9
	collect_value		8
	collect_value		7
	put_nil		7
	get_value		1,2
	put_func		1,3,:
	write_elements_inc		1,1,4,2
	put_func		2,4,guard_builtin
	write_element_value		2,1,6
	write_element_integer		2,2,0
	write_element_value		2,3,1
	put_list_val_val		1,2,7
	get_list_value		3,1
	proceed
guard_builtin_check_9_3:
	is_vector		6,guard_builtin_check_9_1
	put_atom		10,none
	g_diff		9,10
	put_atom		10,relop
	g_diff		9,10
	put_atom		10,float_relop
	g_diff		9,10
	g_vector		6,10
	put_integer		11,2
	g_not_less_than		10,11
	put_integer		12,0
	g_vector_element		6,12,11
	atom		11
	mark_element		6,12
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	put_nil		6
	get_value		1,2
	b_decrement		10,1
	put_func		2,3,:
	write_elements_inc		2,1,4,2
	put_func		4,4,guard_builtin
	write_element_value		4,1,11
	write_elements_inc		4,2,1,2
	put_list_val_val		1,4,6
	get_list_value		3,1
	proceed
guard_builtin_check_9_1:
	try_me_else		guard_builtin_check_9_4
	vector		7
	atom		9
	branch_on_atom		9,2,guard_builtin_check_9_4
	bucket_entry_a		float_relop,guard_builtin_check_9_7
	bucket_entry_a		relop,guard_builtin_check_9_8
guard_builtin_check_9_7:
	g_vector		7,10
	put_integer		11,0
	g_vector_element		7,11,9
	mark_element		7,11
	collect_value		7
	collect_value		6
	get_value		1,2
	b_decrement		10,1
	put_func		2,3,:
	write_element_marked_value		2,1,4
	write_element_marked_value		2,2,5
	put_func		6,4,guard_builtin
	write_element_value		6,1,9
	write_elements_inc		6,2,1,2
	get_list_val_var		3,2,6,1
	put_func		2,3,:
	write_elements_inc		2,1,4,2
	put_atom		3,guard_builtin
	put_value		4,8
	execute		4,float_expression_check_list_4_0
guard_builtin_check_9_8:
	g_vector		7,10
	put_integer		11,0
	g_vector_element		7,11,9
	mark_element		7,11
	collect_value		7
	collect_value		6
	get_value		1,2
	b_decrement		10,1
	put_func		2,3,:
	write_element_marked_value		2,1,4
	write_element_marked_value		2,2,5
	put_func		6,4,guard_builtin
	write_element_value		6,1,9
	write_elements_inc		6,2,1,2
	get_list_val_var		3,2,6,1
	put_func		2,3,:
	write_elements_inc		2,1,4,2
	put_atom		3,guard_builtin
	put_value		4,8
	execute		4,expression_check_list_4_0
guard_builtin_check_9_4:
	try_me_else		guard_builtin_check_9_9
	wait_atom		9,none
	collect_value		8
	collect_value		7
	collect_value		4
	get_nil		3
	put_structured_constant		3,'$SCNST_56'
	put_list_val_val		4,3,2
	put_func		2,2,putt
	write_element_value		2,1,5
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_57'
	put_list_val_val		4,2,3
	put_func		2,2,putt
	write_element_value		2,1,6
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_58'
	put_list_val_val		4,2,3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	get_list_value		1,2
	proceed
guard_builtin_check_9_9:
	suspend		guard_builtin_check_9_0
	module_entry		mpimos_xref
	predicate		body_check,7
body_check_7_0:
	try_me_else		body_check_7_1
	jump_on_non_atom		7,body_check_7_3
	test_atom		7,true,body_check_7_1
	collect_value		6
	collect_value		5
	get_nil		3
	get_nil		4
	get_value		1,2
	proceed
body_check_7_3:
	check_vector		7,3,body_check_7_1
	read_element		7,0,8
	atom		8
	hash_on_atom		8,6,body_check_7_1
	bucket_entry_a		$:=,body_check_7_5
	bucket_entry_a		',',body_check_7_6
	bucket_entry_a		:,body_check_7_7
	bucket_entry_a		:=,body_check_7_8
	bucket_entry_a		=,body_check_7_9
	bucket_entry_a		@,body_check_7_10
body_check_7_5:
	read_elements_inc		7,1,9,2
	collect_value		9
	get_nil		3
	get_value		1,2
	put_reused_func		2,7,:
	write_elements_inc		2,1,5,2
	put_value		1,4
	put_atom		3,body_builtin
	put_value		4,10
	execute		4,float_expression_4_0
body_check_7_6:
	read_elements_inc		7,1,9,2
	collect_vector		7
	put_vector		11,2
	write_element_variable		11,0,8
	write_element_variable		11,1,7
	get_vector_value		3,11
	put_vector		12,2
	write_element_variable		12,0,3
	write_element_variable		12,1,11
	get_vector_value		4,12
	create_goal		7
	set_variable		1,4
	set_value		2,2
	set_value		3,8
	set_value		4,3
	set_marked_value		5,5
	set_marked_value		6,6
	set_value		7,10
	enqueue_goal		7,body_check_7_0
	put_value		2,4
	put_value		3,7
	put_value		4,11
	put_value		7,9
	execute		7,body_check_7_0
body_check_7_7:
	read_element		7,1,9
	read_element		7,2,12
	wait_vector		12,3
	read_element		12,0,10
	wait_atom		10,@
	read_elements_inc		12,1,10,2
	collect_value		11
	collect_vector		12
	put_reused_func		7,7,:
	write_elements_inc		7,1,9,2
	execute		7,body_check_7_0
body_check_7_8:
	read_elements_inc		7,1,9,2
	collect_value		9
	get_nil		3
	get_value		1,2
	put_reused_func		2,7,:
	write_elements_inc		2,1,5,2
	put_value		1,4
	put_atom		3,body_builtin
	put_value		4,10
	execute		4,expression_4_0
body_check_7_9:
	read_elements_inc		7,1,9,2
	collect_value		10
	collect_value		9
	collect_value		6
	collect_value		5
	collect_vector		7
	get_nil		3
	get_nil		4
	get_value		1,2
	proceed
body_check_7_10:
	read_elements_inc		7,1,9,2
	collect_value		10
	collect_vector		7
	put_value		7,9
	execute		7,body_check_7_0
body_check_7_1:
	otherwise		body_check_7_0
	try_me_else		body_check_7_18
	wait_vector		7,3
	read_element		7,0,8
	wait_atom		8,:
	read_element		7,1,9
	atom		9
	read_element		7,2,10
	jump_on_non_atom		10,body_check_7_23
	get_nil		3
	put_nil		3
	get_value		1,2
	put_reused_func		1,7,:
	write_elements_inc		1,1,5,2
	put_func		2,5,call
	write_elements_inc		2,1,9,2
	write_element_integer		2,3,0
	write_element_value		2,4,1
	put_list_val_val		1,2,3
	get_list_value		4,1
	proceed
body_check_7_23:
	is_vector		10,body_check_7_18
	g_vector		10,11
	put_integer		12,2
	g_not_less_than		11,12
	put_integer		13,0
	g_vector_element		10,13,12
	atom		12
	mark_element		10,13
	collect_value		10
	get_nil		3
	put_nil		8
	get_value		1,2
	b_decrement		11,1
	put_reused_func		2,7,:
	write_elements_inc		2,1,5,2
	put_func		3,5,call
	write_element_value		3,1,9
	write_element_value		3,2,12
	write_elements_inc		3,3,1,2
	put_list_val_val		1,3,8
	get_list_value		4,1
	proceed
body_check_7_18:
	otherwise		body_check_7_0
	create_goal		8
	set_values_inc		1,1,6
	set_marked_value		7,7
	set_variable		8,5
	enqueue_goal		8,body_builtin_check_8_0
	put_value		1,7
	put_void		2
	put_void		3
	put_void		4
	execute_external		kl1cmp_blttbl,active_builtin,5
body_check_7_34:
	suspend		body_check_7_0
	module_entry		mpimos_xref
	predicate		body_builtin_check,8
body_builtin_check_8_0:
	try_me_else		body_builtin_check_8_1
	jump_on_non_atom		7,body_builtin_check_8_3
	try_me_else		body_builtin_check_8_4
	wait_atom		8,none
	collect_value		5
	put_nil		5
	get_nil		4
	get_value		1,2
	put_func		1,4,call
	write_element_value		1,1,7
	write_element_integer		1,2,0
	write_element_value		1,3,6
	put_list_val_val		2,1,5
	get_list_value		3,2
	proceed
body_builtin_check_8_4:
	try_me_else		body_builtin_check_8_1
	put_atom		9,none
	g_diff		8,9
	collect_value		8
	get_nil		3
	put_nil		3
	get_value		1,2
	put_func		1,3,:
	write_elements_inc		1,1,5,2
	put_func		2,4,body_builtin
	write_element_value		2,1,7
	write_element_integer		2,2,0
	write_element_value		2,3,1
	put_list_val_val		1,2,3
	get_list_value		4,1
	proceed
body_builtin_check_8_3:
	is_vector		7,body_builtin_check_8_1
	try_me_else		body_builtin_check_8_6
	wait_atom		8,none
	g_vector		7,9
	put_integer		10,2
	g_not_less_than		9,10
	put_integer		11,0
	g_vector_element		7,11,10
	atom		10
	mark_element		7,11
	collect_value		7
	collect_value		5
	put_nil		5
	get_nil		4
	get_value		1,2
	b_decrement		9,1
	put_func		2,4,call
	write_element_value		2,1,10
	write_element_value		2,2,1
	write_element_value		2,3,6
	put_list_val_val		1,2,5
	get_list_value		3,1
	proceed
body_builtin_check_8_6:
	try_me_else		body_builtin_check_8_1
	put_atom		9,none
	g_diff		8,9
	g_vector		7,9
	put_integer		10,2
	g_not_less_than		9,10
	put_integer		11,0
	g_vector_element		7,11,10
	atom		10
	mark_element		7,11
	collect_value		8
	collect_value		7
	get_nil		3
	put_nil		7
	get_value		1,2
	b_decrement		9,1
	put_func		2,3,:
	write_elements_inc		2,1,5,2
	put_func		3,4,body_builtin
	write_element_value		3,1,10
	write_elements_inc		3,2,1,2
	put_list_val_val		1,3,7
	get_list_value		4,1
	proceed
body_builtin_check_8_1:
	otherwise		body_builtin_check_8_0
	try_me_else		body_builtin_check_8_15
	wait_atom		8,none
	collect_value		5
	get_nil		3
	get_nil		4
	put_structured_constant		3,'$SCNST_59'
	put_list_val_val		4,3,2
	put_func		2,2,putt
	write_element_value		2,1,6
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_60'
	put_list_val_val		4,2,3
	put_func		2,2,putt
	write_element_value		2,1,7
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_61'
	put_list_val_val		4,2,3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	get_list_value		1,2
	proceed
body_builtin_check_8_15:
	suspend		body_builtin_check_8_0
	module_entry		mpimos_xref
	predicate		expression,4
expression_4_0:
	try_me_else		expression_4_1
	wait_vector		4,2
	read_element		4,0,5
	wait_atom		5,int
	read_element		4,1,5
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,7
	set_variable		5,6
	enqueue_goal		5,float_expression_check_5_0
	put_reused_func		3,4,int
	write_element_value		3,1,5
	put_void		1
	put_void		2
	put_values_dec		4,7,2
	put_void		6
	execute_external		kl1cmp_blttbl,expression,6
expression_4_1:
	otherwise		expression_4_0
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,6
	set_variable		5,5
	enqueue_goal		5,expression_check_5_0
	put_void		1
	put_void		2
	put_value		3,4
	put_value		4,6
	put_void		6
	execute_external		kl1cmp_blttbl,expression,6
expression_4_6:
	suspend		expression_4_0
	module_entry		mpimos_xref
	predicate		expression_check,5
expression_check_5_0:
	try_me_else		expression_check_5_1
	jump_on_non_atom		4,expression_check_5_3
	test_atom		4,true,expression_check_5_1
	collect_value		5
	collect_value		3
	collect_value		2
	get_nil		1
	proceed
expression_check_5_3:
	is_vector		4,expression_check_5_1
	g_vector		4,6
	put_integer		8,0
	g_vector_element		4,8,7
	mark_element		4,8
	collect_value		4
	b_decrement		6,4
	put_vector		6,4
	write_element_marked_value		6,0,3
	write_element_value		6,1,7
	write_element_value		6,2,4
	write_element_marked_value		6,3,2
	get_list_val_var		1,7,6,4
	put_value		1,4
	put_value		4,5
	execute		4,expression_check_list_4_0
expression_check_5_1:
	suspend		expression_check_5_0
	module_entry		mpimos_xref
	predicate		expression_check_list,4
expression_check_list_4_0:
	try_me_else		expression_check_list_4_1
	jump_on_non_list_var_var		4,expression_check_list_4_3,5,8
	wait_list_var_var		8,6,7
	collect_list		4
	collect_list		8
	collect_value		6
	put_vector		8,2
	write_element_variable		8,0,6
	write_element_variable		8,1,4
	get_vector_value		1,8
	create_goal		4
	set_value		1,6
	set_marked_value		2,2
	set_marked_value		3,3
	set_value		4,7
	enqueue_goal		4,expression_check_list_4_0
	put_value		1,4
	put_value		4,5
	execute		4,expression_4_0
expression_check_list_4_3:
	check_nil		4,expression_check_list_4_1
	collect_value		3
	collect_value		2
	get_nil		1
	proceed
expression_check_list_4_1:
	suspend		expression_check_list_4_0
	module_entry		mpimos_xref
	predicate		float_expression,4
float_expression_4_0:
	try_me_else		float_expression_4_1
	wait_vector		4,2
	read_element		4,0,5
	wait_atom		5,float
	read_element		4,1,5
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,7
	set_variable		5,6
	enqueue_goal		5,expression_check_5_0
	put_reused_func		3,4,float
	write_element_value		3,1,5
	put_void		1
	put_void		2
	put_values_dec		4,7,2
	put_void		6
	execute_external		kl1cmp_blttbl,float_expression,6
float_expression_4_1:
	otherwise		float_expression_4_0
	create_goal		5
	set_values_inc		1,1,3
	set_variable		4,6
	set_variable		5,5
	enqueue_goal		5,float_expression_check_5_0
	put_void		1
	put_void		2
	put_value		3,4
	put_value		4,6
	put_void		6
	execute_external		kl1cmp_blttbl,float_expression,6
float_expression_4_6:
	suspend		float_expression_4_0
	module_entry		mpimos_xref
	predicate		float_expression_check,5
float_expression_check_5_0:
	try_me_else		float_expression_check_5_1
	wait_vector		4,3
	read_element		4,0,6
	wait_atom		6,integer_to_floating_point
	read_elements_inc		4,1,6,2
	collect_value		7
	collect_value		6
	collect_vector		4
	put_vector		4,4
	write_element_marked_value		4,0,3
	write_element_atom		4,1,integer_to_floating_point
	write_element_integer		4,2,2
	write_element_marked_value		4,3,2
	get_list_val_var		1,6,4,4
	put_value		1,4
	put_value		4,5
	execute		4,expression_check_list_4_0
float_expression_check_5_1:
	otherwise		float_expression_check_5_0
	try_me_else		float_expression_check_5_6
	jump_on_non_atom		4,float_expression_check_5_8
	test_atom		4,true,float_expression_check_5_6
	collect_value		5
	collect_value		3
	collect_value		2
	get_nil		1
	proceed
float_expression_check_5_8:
	is_vector		4,float_expression_check_5_6
	g_vector		4,6
	put_integer		8,0
	g_vector_element		4,8,7
	mark_element		4,8
	collect_value		4
	b_decrement		6,4
	put_vector		6,4
	write_element_marked_value		6,0,3
	write_element_value		6,1,7
	write_element_value		6,2,4
	write_element_marked_value		6,3,2
	get_list_val_var		1,7,6,4
	put_value		1,4
	put_value		4,5
	execute		4,float_expression_check_list_4_0
float_expression_check_5_6:
	suspend		float_expression_check_5_0
	module_entry		mpimos_xref
	predicate		float_expression_check_list,4
float_expression_check_list_4_0:
	try_me_else		float_expression_check_list_4_1
	jump_on_non_list_var_var		4,float_expression_check_list_4_3,5,8
	wait_list_var_var		8,6,7
	collect_list		4
	collect_list		8
	collect_value		6
	put_vector		8,2
	write_element_variable		8,0,6
	write_element_variable		8,1,4
	get_vector_value		1,8
	create_goal		4
	set_value		1,6
	set_marked_value		2,2
	set_marked_value		3,3
	set_value		4,7
	enqueue_goal		4,float_expression_check_list_4_0
	put_value		1,4
	put_value		4,5
	execute		4,float_expression_4_0
float_expression_check_list_4_3:
	check_nil		4,float_expression_check_list_4_1
	collect_value		3
	collect_value		2
	get_nil		1
	proceed
float_expression_check_list_4_1:
	suspend		float_expression_check_list_4_0
	module_entry		mpimos_xref
	predicate		referred_result,6
referred_result_6_0:
	try_me_else		referred_result_6_1
	jump_on_non_list		6,referred_result_6_3
	put_values_inc		7,3,3
	put_values_inc		3,6,4
	execute		6,put_referred_6_0
referred_result_6_3:
	check_atom		6,check,referred_result_6_1
	collect_value		5
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
referred_result_6_1:
	otherwise		referred_result_6_0
	b_merge		8,7
	get_value		8,3
	b_merge		8,3
	get_value		8,4
	b_merge		8,4
	get_value		8,5
	create_goal		4
	set_variable		1,5
	set_value		2,2
	set_value		3,4
	set_marked_value		4,6
	enqueue_goal		4,referred_result_body_4_0
	create_goal		4
	set_variable		1,2
	set_value		2,5
	set_value		3,3
	set_value		4,6
	enqueue_goal		4,referred_result_guard_4_0
	create_goal		5
	set_values_inc		1,1,2
	set_variable		3,3
	set_value		4,6
	set_atom		5,done
	enqueue_goal		5,referred_result_list_5_0
	put_value		1,7
	put_integer		2,0
	execute_external		mpimos_utility,qsortv,3
referred_result_6_8:
	suspend		referred_result_6_0
	module_entry		mpimos_xref
	predicate		referred_result_list,5
referred_result_list_5_0:
	try_me_else		referred_result_list_5_1
	jump_on_non_list_var_var		3,referred_result_list_5_3,6,7
	wait		5
	collect_value		5
	put_integer		5,3
	put_variable		8,9
	b_set_vector_element		6,5,5,8,6
	b_merge		10,8
	get_value		10,5
	put_func		5,2,flush
	write_element_variable		5,1,10
	put_reused_list_val_var		3,3,5,5
	create_goal		5
	set_value		1,5
	set_value		2,2
	set_value		3,7
	set_marked_value		4,4
	set_value		5,10
	enqueue_goal		5,referred_result_list_5_0
	create_goal		4
	set_value		1,1
	set_value		2,3
	set_value		3,6
	set_value		4,4
	enqueue_goal		4,referred_result_one_4_0
	put_value		1,8
	put_integer		2,0
	put_value		3,9
	execute_external		mpimos_utility,qsortv,3
referred_result_list_5_3:
	check_nil		3,referred_result_list_5_1
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
referred_result_list_5_1:
	suspend		referred_result_list_5_0
	module_entry		mpimos_xref
	predicate		referred_result_one,4
referred_result_one_4_0:
	try_me_else		referred_result_one_4_1
	vector		3
	put_integer		5,3
	g_vector_element		3,5,5
	wait_nil		5
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
referred_result_one_4_1:
	otherwise		referred_result_one_4_0
	try_me_else		referred_result_one_4_5
	wait_vector		3,5
	read_elements_inc		3,0,5,3
	try_me_else		referred_result_one_4_7
	wait_nil		7
	read_elements_inc		3,3,8,2
	wait_vector		4,4
	read_element		4,0,10
	wait_atom		10,list
	read_elements_inc		4,1,10,3
	string		9
	g_string		9,7,13
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		5
	collect_vector		3
	collect_vector		4
	put_list		3
	write_car_atom		3,nl
	write_cdr_variable		3,7
	put_structured_constant		4,'$SCNST_62'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_63'
	put_list_val_val		5,3,4
	put_structured_constant		3,'$SCNST_64'
	put_list_val_val		4,3,5
	put_func		3,2,putt
	write_element_value		3,1,9
	put_list_val_val		5,3,4
	put_structured_constant		3,'$SCNST_65'
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_66'
	put_list_val_val		5,3,4
	get_list_value		1,5
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_value		1,7
	put_value		2,3
	put_value		3,8
	execute		3,referred_table_3_0
referred_result_one_4_7:
	read_elements_inc		3,3,8,2
	try_me_else		referred_result_one_4_5
	jump_on_non_atom		9,referred_result_one_4_10
	test_nil		9,referred_result_one_4_5
	wait_vector		4,4
	read_elements_inc		4,0,10,2
	wait_atom		11,system
	read_elements_inc		4,2,11,2
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		5
	collect_vector		3
	collect_vector		4
	put_structured_constant		3,'$SCNST_67'
	put_list_val_var		4,3,9
	put_structured_constant		3,'$SCNST_68'
	put_list_val_val		5,3,4
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_69'
	put_list_val_val		5,3,4
	put_structured_constant		3,'$SCNST_70'
	put_list_val_val		4,3,5
	get_list_value		1,4
	put_list		1
	write_car_atom		1,nl
	write_cdr_variable		1,5
	put_structured_constant		3,'$SCNST_71'
	put_list_val_val		4,3,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	create_goal		3
	set_value		1,5
	set_value		2,1
	set_value		3,8
	enqueue_goal		3,referred_table_3_0
	put_value		1,9
	put_value		2,4
	put_value		3,7
	execute		3,out_convert_3_0
referred_result_one_4_10:
	is_string		9,referred_result_one_4_5
	wait_vector		4,4
	read_element		4,0,10
	wait_atom		10,list
	read_elements_inc		4,1,10,3
	g_string		9,13,14
	put_nil		13
	g_diff		7,13
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		5
	collect_value		13
	collect_vector		3
	collect_vector		4
	put_structured_constant		3,'$SCNST_72'
	put_list_val_var		4,3,10
	put_structured_constant		3,'$SCNST_73'
	put_list_val_val		5,3,4
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_74'
	put_list_val_val		5,3,4
	put_structured_constant		3,'$SCNST_75'
	put_list_val_val		4,3,5
	put_func		3,2,putt
	write_element_value		3,1,9
	put_list_val_val		5,3,4
	put_structured_constant		3,'$SCNST_76'
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_77'
	put_list_val_val		5,3,4
	get_list_value		1,5
	put_list		1
	write_car_atom		1,nl
	write_cdr_variable		1,5
	put_structured_constant		3,'$SCNST_78'
	put_list_val_val		4,3,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	create_goal		3
	set_value		1,5
	set_value		2,1
	set_value		3,8
	enqueue_goal		3,referred_table_3_0
	put_value		1,10
	put_value		2,4
	put_value		3,7
	execute		3,out_convert_3_0
referred_result_one_4_5:
	otherwise		referred_result_one_4_0
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
referred_result_one_4_24:
	suspend		referred_result_one_4_0
	module_entry		mpimos_xref
	predicate		referred_table,3
referred_table_3_0:
	try_me_else		referred_table_3_1
	jump_on_non_list_var_var		3,referred_table_3_3,9,4
	wait_vector		9,4
	read_elements_inc		9,0,5,4
	collect_value		5
	collect_vector		9
	put_structured_constant		5,'$SCNST_79'
	put_reused_list_val_var		3,3,5,9
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,3
	put_func		3,3,/
	write_elements_inc		3,1,6,2
	put_func		6,2,putt
	write_element_value		6,1,3
	put_list_val_val		3,6,5
	put_structured_constant		5,'$SCNST_80'
	put_list_val_val		6,5,3
	put_structured_constant		3,'$SCNST_81'
	put_list_val_val		5,3,6
	get_list_value		1,5
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,referred_table_3_0
	put_value		1,9
	put_value		2,3
	put_value		3,8
	execute		3,out_convert_v_3_0
referred_table_3_3:
	check_nil		3,referred_table_3_1
	get_value		1,2
	proceed
referred_table_3_1:
	suspend		referred_table_3_0
	module_entry		mpimos_xref
	predicate		referred_result_guard,4
referred_result_guard_4_0:
	try_me_else		referred_result_guard_4_1
	jump_on_non_list		3,referred_result_guard_4_3
	wait_vector		4,4
	read_elements_inc		4,0,5,4
	wait_atom		8,guard
	collect_value		7
	collect_value		6
	collect_value		5
	collect_vector		4
	put_structured_constant		4,'$SCNST_82'
	put_list_val_var		5,4,6
	put_structured_constant		4,'$SCNST_83'
	put_list_val_val		7,4,5
	get_list_value		1,7
	put_value		1,6
	execute		3,referred_result_builtin_3_0
referred_result_guard_4_3:
	check_nil		3,referred_result_guard_4_1
	collect_value		4
	get_value		1,2
	proceed
referred_result_guard_4_1:
	try_me_else		referred_result_guard_4_5
	wait_vector		4,4
	read_elements_inc		4,0,5,4
	wait_atom		8,no
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		3
	collect_vector		4
	get_value		1,2
	proceed
referred_result_guard_4_5:
	suspend		referred_result_guard_4_0
	module_entry		mpimos_xref
	predicate		referred_result_body,4
referred_result_body_4_0:
	try_me_else		referred_result_body_4_1
	jump_on_non_list		3,referred_result_body_4_3
	wait_vector		4,4
	read_elements_inc		4,0,5,3
	wait_atom		7,builtin
	read_element		4,3,7
	collect_value		7
	collect_value		6
	collect_value		5
	collect_vector		4
	put_structured_constant		4,'$SCNST_84'
	put_list_val_var		5,4,6
	put_structured_constant		4,'$SCNST_85'
	put_list_val_val		7,4,5
	get_list_value		1,7
	put_value		1,6
	execute		3,referred_result_builtin_3_0
referred_result_body_4_3:
	check_nil		3,referred_result_body_4_1
	collect_value		4
	get_value		1,2
	proceed
referred_result_body_4_1:
	try_me_else		referred_result_body_4_5
	wait_vector		4,4
	read_elements_inc		4,0,5,3
	wait_atom		7,no
	read_element		4,3,7
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		3
	collect_vector		4
	get_value		1,2
	proceed
referred_result_body_4_5:
	suspend		referred_result_body_4_0
	module_entry		mpimos_xref
	predicate		referred_result_builtin,3
referred_result_builtin_3_0:
	try_me_else		referred_result_builtin_3_1
	jump_on_non_list_var_var		3,referred_result_builtin_3_3,10,4
	wait_vector		10,3
	read_elements_inc		10,0,5,3
	put_structured_constant		8,'$SCNST_86'
	put_reused_list_val_var		3,3,8,9
	put_list		8
	write_car_atom		8,nl
	write_cdr_value		8,3
	put_reused_func		3,10,/
	write_elements_inc		3,1,5,2
	put_func		5,2,putt
	write_element_value		5,1,3
	put_list_val_val		3,5,8
	put_structured_constant		5,'$SCNST_87'
	put_list_val_val		6,5,3
	put_structured_constant		3,'$SCNST_88'
	put_list_val_val		5,3,6
	get_list_value		1,5
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,referred_result_builtin_3_0
	put_value		1,9
	put_value		2,3
	put_value		3,7
	execute		3,out_convert_v_3_0
referred_result_builtin_3_3:
	check_nil		3,referred_result_builtin_3_1
	get_value		1,2
	proceed
referred_result_builtin_3_1:
	suspend		referred_result_builtin_3_0
	module_entry		mpimos_xref
	predicate		put_referred,6
put_referred_6_0:
	try_me_else		put_referred_6_1
	jump_on_non_list		3,put_referred_6_3
	read_car		3,7
	jump_on_non_atom		7,put_referred_6_5
	read_cdr		3,8
	collect_list		3
	create_goal		6
	set_variable		1,9
	set_value		2,2
	set_value		3,8
	set_variable		4,3
	set_values_inc		5,5,2
	enqueue_goal		6,put_referred_6_0
	create_goal		5
	set_value		1,1
	set_value		2,9
	set_variable		3,5
	set_variable		4,6
	set_marked_value		5,7
	enqueue_goal		5,put_module_result_5_0
	put_value		1,7
	put_value		2,4
	put_value		4,6
	execute		5,get_list_from_table_5_0
put_referred_6_5:
	is_vector		7,put_referred_6_1
	jump_on_arity		7,4,put_referred_6_1
	table_entry		put_referred_6_1
	table_entry		put_referred_6_1
	table_entry		put_referred_6_6
	table_entry		put_referred_6_7
put_referred_6_6:
	read_cdr		3,8
	read_element		7,0,9
	wait_atom		9,guard
	read_element		7,1,11
	wait_vector		11,3
	read_element		11,0,9
	wait_atom		9,/
	read_elements_inc		11,1,9,2
	atom		9
	integer		10
	put_integer		12,0
	g_not_less_than		10,12
	collect_vector		7
	collect_vector		11
	put_structured_constant		7,'$SCNST_89'
	get_reused_list_val_var		1,3,3,7,7
	create_goal		6
	set_variable		1,1
	set_value		2,2
	set_value		3,8
	set_value		4,4
	set_variable		5,3
	set_value		6,6
	enqueue_goal		6,put_referred_6_0
	create_goal		7
	set_value		1,7
	set_value		2,1
	set_variable		3,6
	set_variable		4,4
	set_marked_value		5,9
	set_value		6,10
	put_structured_constant		1,'$SCNST_90'
	set_value		7,1
	enqueue_goal		7,put_one_builtin_7_0
	put_value		1,9
	put_value		2,5
	put_value		5,6
	execute		5,get_list_from_table_5_0
put_referred_6_7:
	read_element		7,0,8
	atom		8
	branch_on_atom		8,2,put_referred_6_1
	bucket_entry_a		/,put_referred_6_9
	bucket_entry_a		:,put_referred_6_10
put_referred_6_9:
	read_cdr		3,9
	read_elements_inc		7,1,10,2
	atom		10
	integer		11
	put_integer		12,0
	g_not_less_than		11,12
	collect_vector		7
	put_structured_constant		7,'$SCNST_91'
	get_reused_list_val_var		1,3,3,7,7
	create_goal		6
	set_variable		1,1
	set_value		2,2
	set_value		3,9
	set_values_inc		4,4,2
	set_variable		6,3
	enqueue_goal		6,put_referred_6_0
	create_goal		7
	set_value		1,7
	set_value		2,1
	set_variable		3,5
	set_variable		4,4
	set_marked_value		5,10
	set_value		6,11
	put_structured_constant		1,'$SCNST_92'
	set_value		7,1
	enqueue_goal		7,put_one_builtin_7_0
	put_value		1,10
	put_value		2,6
	execute		5,get_list_from_table_5_0
put_referred_6_10:
	read_cdr		3,9
	read_element		7,1,10
	read_element		7,2,13
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,/
	read_elements_inc		13,1,11,2
	atom		10
	atom		11
	integer		12
	put_integer		14,0
	g_not_less_than		12,14
	collect_vector		7
	collect_vector		13
	put_structured_constant		7,'$SCNST_93'
	get_reused_list_val_var		1,3,3,7,7
	create_goal		6
	set_variable		1,1
	set_value		2,2
	set_value		3,9
	set_variable		4,3
	set_values_inc		5,5,2
	enqueue_goal		6,put_referred_6_0
	create_goal		7
	set_value		1,7
	set_value		2,1
	set_variable		3,5
	set_variable		4,6
	set_marked_value		5,10
	set_values_inc		6,11,2
	enqueue_goal		7,put_predicate_result_7_0
	put_value		1,10
	put_value		2,4
	put_value		4,6
	execute		5,get_list_from_table_5_0
put_referred_6_3:
	check_nil		3,put_referred_6_1
	collect_value		6
	collect_value		5
	collect_value		4
	get_value		1,2
	proceed
put_referred_6_1:
	otherwise		put_referred_6_0
	try_me_else		put_referred_6_20
	wait_list_var_var		3,7,8
	put_structured_constant		9,'$SCNST_94'
	put_reused_list_val_var		3,3,9,11
	put_structured_constant		9,'$SCNST_95'
	put_list_val_val		10,9,3
	put_func		3,2,putt
	write_element_value		3,1,7
	put_list_val_val		7,3,10
	put_structured_constant		3,'$SCNST_96'
	put_list_val_val		9,3,7
	put_structured_constant		3,'$SCNST_97'
	put_list_val_val		7,3,9
	get_list_value		1,7
	put_value		1,11
	put_value		3,8
	execute		6,put_referred_6_0
put_referred_6_20:
	suspend		put_referred_6_0
	module_entry		mpimos_xref
	predicate		put_module_result,5
put_module_result_5_0:
	try_me_else		put_module_result_5_1
	jump_on_non_list_var_var		4,put_module_result_5_3,6,7
	vector		6
	put_integer		8,1
	g_vector_element		6,8,8
	wait_value		5,8
	put_reused_list		4,4
	write_car_marked_value		4,6
	write_cdr_value		4,7
	get_list_value		3,4
	put_integer		3,3
	put_variable		4,7
	b_set_vector_element		6,3,3,4,4
	b_merge		6,5
	get_value		6,3
	create_goal		4
	set_values_inc		1,1,2
	set_value		3,4
	put_structured_constant		1,'$SCNST_98'
	set_value		4,1
	enqueue_goal		4,referred_result_one_4_0
	put_value		1,5
	put_integer		2,0
	put_value		3,7
	execute_external		mpimos_utility,qsortv,3
put_module_result_5_3:
	check_nil		4,put_module_result_5_1
	get_nil		3
	put_structured_constant		3,'$SCNST_99'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_100'
	put_list_val_val		3,2,4
	put_func		2,2,putt
	write_element_value		2,1,5
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_101'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_102'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_module_result_5_1:
	otherwise		put_module_result_5_0
	try_me_else		put_module_result_5_8
	wait_list_var_var		4,6,7
	get_reused_list_val_var		3,8,4,6,4
	put_value		3,4
	put_value		4,7
	execute		5,put_module_result_5_0
put_module_result_5_8:
	suspend		put_module_result_5_0
	module_entry		mpimos_xref
	predicate		put_predicate_result,7
put_predicate_result_7_0:
	try_me_else		put_predicate_result_7_1
	jump_on_non_list		4,put_predicate_result_7_3
	read_car		4,8
	vector		8
	read_cdr		4,9
	try_me_else		put_predicate_result_7_5
	put_integer		11,1
	g_vector_element		8,11,10
	wait_value		5,10
	put_integer		10,3
	g_vector_element		8,10,10
	vector		10
	g_vector		10,10
	put_integer		12,0
	g_less_than		12,10
	mark_element		8,11
	mark_element		8,11
	put_marked_value		11,5
	put_integer		5,3
	put_variable		12,10
	b_set_vector_element		8,5,5,12,8
	put_reused_list_val_val		4,4,8,9
	get_list_value		3,4
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,8
	set_variable		4,4
	set_value		5,11
	set_marked_value		6,6
	set_value		7,7
	enqueue_goal		7,put_one_predicate_7_0
	put_values_dec		1,6,2
	put_value		3,10
	put_value		5,8
	execute		5,get_list_from_table_5_0
put_predicate_result_7_5:
	try_me_else		put_predicate_result_7_1
	put_integer		11,1
	g_vector_element		8,11,10
	wait_value		5,10
	put_integer		10,3
	g_vector_element		8,10,10
	wait_vector		10,0
	mark_element		8,11
	mark_element		8,11
	put_marked_value		5,5
	put_reused_list_val_val		4,4,8,9
	get_list_value		3,4
	put_structured_constant		3,'$SCNST_103'
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_func		3,3,/
	write_elements_inc		3,1,6,2
	put_func		4,3,:
	write_element_value		4,1,5
	write_element_value		4,2,3
	put_func		3,2,putt
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_104'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_105'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_predicate_result_7_3:
	check_nil		4,put_predicate_result_7_1
	get_nil		3
	put_structured_constant		3,'$SCNST_106'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_107'
	put_list_val_val		3,2,4
	put_func		2,3,/
	write_elements_inc		2,1,6,2
	put_func		4,3,:
	write_element_value		4,1,5
	write_element_value		4,2,2
	put_func		2,2,putt
	write_element_value		2,1,4
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_108'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_109'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_predicate_result_7_1:
	otherwise		put_predicate_result_7_0
	try_me_else		put_predicate_result_7_12
	wait_list_var_var		4,8,9
	get_reused_list_val_var		3,10,4,8,4
	put_value		3,4
	put_value		4,9
	execute		7,put_predicate_result_7_0
put_predicate_result_7_12:
	suspend		put_predicate_result_7_0
	module_entry		mpimos_xref
	predicate		put_one_predicate,7
put_one_predicate_7_0:
	try_me_else		put_one_predicate_7_1
	jump_on_non_list_var_var		4,put_one_predicate_7_3,8,9
	vector		8
	put_integer		10,1
	g_vector_element		8,10,11
	wait_value		6,11
	put_integer		11,2
	g_vector_element		8,11,12
	wait_value		7,12
	mark_element		8,10
	mark_element		8,11
	mark_element		8,10
	mark_element		8,11
	put_marked_value		10,6
	put_marked_value		11,7
	put_integer		6,3
	put_marked_variable		12,7
	b_set_vector_element		8,6,8,12,6
	get_value		8,7
	put_reused_list_val_val		4,4,6,9
	get_list_value		3,4
	put_structured_constant		3,'$SCNST_110'
	put_list_val_var		4,3,8
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,4
	put_func		4,3,/
	write_elements_inc		4,1,10,2
	put_func		6,3,:
	write_elements_dec		6,1,5,2
	put_func		4,2,putt
	write_element_value		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_111'
	put_list_val_val		4,3,5
	put_structured_constant		3,'$SCNST_112'
	put_list_val_val		5,3,4
	get_list_value		1,5
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_value		1,8
	put_value		2,3
	put_value		3,7
	execute		3,out_convert_v_3_0
put_one_predicate_7_3:
	check_nil		4,put_one_predicate_7_1
	get_nil		3
	put_structured_constant		3,'$SCNST_113'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_114'
	put_list_val_val		3,2,4
	put_func		2,3,/
	write_elements_inc		2,1,6,2
	put_func		4,3,:
	write_element_value		4,1,5
	write_element_value		4,2,2
	put_func		2,2,putt
	write_element_value		2,1,4
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_115'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_116'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_one_predicate_7_1:
	otherwise		put_one_predicate_7_0
	try_me_else		put_one_predicate_7_8
	wait_list_var_var		4,8,9
	get_reused_list_val_var		3,10,4,8,4
	put_value		3,4
	put_value		4,9
	execute		7,put_one_predicate_7_0
put_one_predicate_7_8:
	suspend		put_one_predicate_7_0
	module_entry		mpimos_xref
	predicate		put_one_builtin,7
put_one_builtin_7_0:
	try_me_else		put_one_builtin_7_1
	jump_on_non_list_var_var		4,put_one_builtin_7_3,12,8
	wait_vector		12,3
	read_elements_inc		12,0,9,3
	wait_value		9,5
	wait_value		10,6
	collect_value		6
	put_reused_vector		5,12
	write_element_marked_value		5,0,9
	write_element_marked_value		5,1,10
	write_element_marked_value		5,2,11
	put_reused_list_val_val		4,4,5,8
	get_list_value		3,4
	put_structured_constant		3,'$SCNST_117'
	put_list_val_var		4,3,6
	put_func		3,2,putl
	write_element_value		3,1,7
	put_list_val_val		5,3,4
	put_func		3,3,/
	write_elements_inc		3,1,9,2
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,5
	put_structured_constant		4,'$SCNST_118'
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_119'
	put_list_val_val		4,3,5
	get_list_value		1,4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_value		1,6
	put_value		2,3
	put_value		3,11
	execute		3,out_convert_v_3_0
put_one_builtin_7_3:
	check_nil		4,put_one_builtin_7_1
	get_nil		3
	create_goal		6
	set_values_inc		1,1,2
	set_variable		3,3
	set_marked_value		4,5
	set_marked_value		5,6
	set_value		6,7
	enqueue_goal		6,put_one_builtin_no_entry_6_0
	put_values_inc		1,5,2
	execute		3,check_builtin_type_3_0
put_one_builtin_7_1:
	otherwise		put_one_builtin_7_0
	try_me_else		put_one_builtin_7_8
	wait_list_var_var		4,8,9
	get_reused_list_val_var		3,10,4,8,4
	put_value		3,4
	put_value		4,9
	execute		7,put_one_builtin_7_0
put_one_builtin_7_8:
	suspend		put_one_builtin_7_0
	module_entry		mpimos_xref
	predicate		put_one_builtin_no_entry,6
put_one_builtin_no_entry_6_0:
	try_me_else		put_one_builtin_no_entry_6_1
	wait_atom		3,none
	put_structured_constant		3,'$SCNST_120'
	put_list_val_val		7,3,2
	put_structured_constant		2,'$SCNST_121'
	put_list_val_val		3,2,7
	put_func		2,2,putb
	write_element_value		2,1,6
	put_list_val_val		6,2,3
	put_func		2,3,/
	write_elements_inc		2,1,4,2
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,6
	put_structured_constant		3,'$SCNST_122'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_123'
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
put_one_builtin_no_entry_6_1:
	try_me_else		put_one_builtin_no_entry_6_3
	put_atom		7,none
	g_diff		3,7
	collect_value		3
	put_structured_constant		3,'$SCNST_124'
	put_list_val_val		7,3,2
	put_func		2,2,putl
	write_element_value		2,1,6
	put_list_val_val		3,2,7
	put_func		2,3,/
	write_elements_inc		2,1,4,2
	put_func		4,2,putt
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_125'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_126'
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
put_one_builtin_no_entry_6_3:
	suspend		put_one_builtin_no_entry_6_0
	module_entry		mpimos_xref
	predicate		check_builtin_type,3
check_builtin_type_3_0:
	try_me_else		check_builtin_type_3_1
	integer		2
	test_integer		2,0,check_builtin_type_3_3
	put_value		5,3
	put_void		2
	put_void		3
	put_void		4
	execute_external		kl1cmp_blttbl,active_builtin,5
check_builtin_type_3_3:
	put_integer		4,0
	g_less_than		4,2
	put_value		5,3
	b_increment		2,2
	b_new_vector		2,2
	put_integer		3,0
	b_set_vector_element		2,3,1,1,2
	put_value		1,2
	put_void		2
	put_void		3
	put_void		4
	execute_external		kl1cmp_blttbl,active_builtin,5
check_builtin_type_3_1:
	suspend		check_builtin_type_3_0
	module_entry		mpimos_xref
	predicate		out_convert,3
out_convert_3_0:
	try_me_else		out_convert_3_1
	jump_on_non_list_var_var		3,out_convert_3_3,8,4
	wait_vector		8,2
	read_elements_inc		8,0,5,2
	put_func		7,3,/
	write_elements_inc		7,1,5,2
	put_reused_func		5,8,putt
	write_element_value		5,1,7
	get_reused_list_val_var		1,6,3,5,3
	put_value		1,3
	put_value		3,4
	execute		3,out_convert1_3_0
out_convert_3_3:
	check_nil		3,out_convert_3_1
	get_value		1,2
	proceed
out_convert_3_1:
	suspend		out_convert_3_0
	module_entry		mpimos_xref
	predicate		out_convert1,3
out_convert1_3_0:
	try_me_else		out_convert1_3_1
	jump_on_non_list_var_var		3,out_convert1_3_3,8,4
	wait_vector		8,2
	read_elements_inc		8,0,5,2
	put_func		7,3,/
	write_elements_inc		7,1,5,2
	put_reused_func		5,8,putt
	write_element_value		5,1,7
	put_reused_list_val_var		3,3,5,6
	put_structured_constant		5,'$SCNST_127'
	put_list_val_val		7,5,3
	get_list_value		1,7
	put_value		1,6
	put_value		3,4
	execute		3,out_convert1_3_0
out_convert1_3_3:
	check_nil		3,out_convert1_3_1
	get_value		1,2
	proceed
out_convert1_3_1:
	suspend		out_convert1_3_0
	module_entry		mpimos_xref
	predicate		out_convert_v,3
out_convert_v_3_0:
	try_me_else		out_convert_v_3_1
	jump_on_non_list_var_var		3,out_convert_v_3_3,4,5
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,7
	put_func		6,2,putt
	write_element_value		6,1,4
	put_list_val_val		4,6,3
	put_structured_constant		3,'$SCNST_128'
	put_list_val_val		6,3,4
	get_list_value		1,6
	put_value		1,7
	put_value		3,5
	execute		3,out_convert_v_3_0
out_convert_v_3_3:
	check_nil		3,out_convert_v_3_1
	get_value		1,2
	proceed
out_convert_v_3_1:
	suspend		out_convert_v_3_0
	module_entry		mpimos_xref
	predicate		get_list_from_table,5
get_list_from_table_5_0:
	b_hash		1,1,6
	put_integer		6,16
	b_modulo		1,6,1
	b_set_vector_element		2,1,1,5,2
	get_value		1,4
	get_value		2,3
	proceed
get_list_from_table_5_1:
	suspend		get_list_from_table_5_0
	module_entry		mpimos_xref
	predicate		init_module_table,2
init_module_table_2_0:
	execute_external		mpimos_xref_table,init_module_table,2
init_module_table_2_1:
	suspend		init_module_table_2_0
	begin_const_section		mpimos_xref
'$SCNST_0_0':
	define_desc		3,1
	define_integer		1717924472
'$SCNST_1':
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_2_1':
	define_desc		27,12
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		2021161080
	define_integer		120
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_2_1'
'$SCNST_3':
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_4_1':
	define_desc		27,2
	define_integer		1162760004
	define_integer		46
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		0,4
	define_atom		list
	define_atom		system
	define_atom		builtin
	define_atom		guard
'$SCNST_98':
'$SCNST_16':
'$SCNST_15':
'$SCNST_6':
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_7_0':
	define_desc		0,4
	define_atom		no
	define_atom		no
	define_atom		builtin
	define_atom		no
'$SCNST_18':
'$SCNST_17':
'$SCNST_8':
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_9_0':
	define_desc		0,4
	define_atom		no
	define_atom		no
	define_atom		no
	define_atom		guard
'$SCNST_20':
'$SCNST_19':
'$SCNST_10':
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_11_0':
	define_desc		0,4
	define_atom		list
	define_atom		no
	define_atom		no
	define_atom		no
'$SCNST_23':
'$SCNST_12':
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_13_0':
	define_desc		0,4
	define_atom		no
	define_atom		system
	define_atom		no
	define_atom		no
'$SCNST_22':
'$SCNST_21':
'$SCNST_14':
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_24_1':
	define_desc		27,1
	define_integer		46
'$SCNST_24_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_24_1'
'$SCNST_78':
'$SCNST_75':
'$SCNST_73':
'$SCNST_71':
'$SCNST_68':
'$SCNST_64':
'$SCNST_62':
'$SCNST_59':
'$SCNST_56':
'$SCNST_54':
'$SCNST_51':
'$SCNST_49':
'$SCNST_48':
'$SCNST_44':
'$SCNST_42':
'$SCNST_40':
'$SCNST_37':
'$SCNST_27':
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_25_1':
	define_desc		3,3
	define_integer		1701603654
	define_integer		1835093536
	define_integer		540680293
'$SCNST_25_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_25_1'
'$SCNST_76':
'$SCNST_65':
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_26_1':
	define_desc		27,12
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
	define_integer		707406378
	define_integer		42
'$SCNST_26_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_26_1'
'$SCNST_26':
	define_vector		'$SCNST_26_0'
'$SCNST_28_1':
	define_desc		27,4
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		32
'$SCNST_28_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_28_1'
'$SCNST_31':
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_29_1':
	define_desc		27,7
	define_integer		1634890835
	define_integer		543516526
	define_integer		542060361
	define_integer		1835888483
	define_integer		543452769
	define_integer		1853189990
	define_integer		100
'$SCNST_29_0':
	define_desc		0,2
	define_atom		putt
	define_string		'$SCNST_29_1'
'$SCNST_29':
	define_vector		'$SCNST_29_0'
'$SCNST_30_1':
	define_desc		27,2
	define_integer		976894496
	define_integer		32
'$SCNST_30_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_30_1'
'$SCNST_32':
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_33_1':
	define_desc		19,4
	define_integer		540950078
	define_integer		1852989783
	define_integer		543649385
	define_integer		8255
'$SCNST_33_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_33_1'
'$SCNST_33':
	define_vector		'$SCNST_33_0'
'$SCNST_34_1':
	define_desc		27,10
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1685024032
	define_integer		543517813
	define_integer		1847620457
	define_integer		1931506799
	define_integer		1768121712
	define_integer		1684367718
	define_integer		46
'$SCNST_34_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_34_1'
'$SCNST_36':
'$SCNST_35':
'$SCNST_34':
	define_vector		'$SCNST_34_0'
'$SCNST_38_1':
	define_desc		19,3
	define_integer		1830825274
	define_integer		1819632751
	define_integer		8293
'$SCNST_38_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_38_1'
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_39_1':
	define_desc		19,13
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1685024032
	define_integer		543517813
	define_integer		1818453348
	define_integer		1952543329
	define_integer		544108393
	define_integer		1679848297
	define_integer		1768714357
	define_integer		1702125923
	define_integer		976887908
	define_integer		8250
'$SCNST_39_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_39_1'
'$SCNST_39':
	define_vector		'$SCNST_39_0'
'$SCNST_41_1':
	define_desc		3,10
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1819044128
	define_integer		1818322789
	define_integer		1667589152
	define_integer		1634885996
	define_integer		1852795252
	define_integer		976894496
	define_integer		539834912
'$SCNST_41_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_41_1'
'$SCNST_41':
	define_vector		'$SCNST_41_0'
'$SCNST_43_1':
	define_desc		11,10
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1970234400
	define_integer		544828514
	define_integer		1768318308
	define_integer		543450478
	define_integer		1969516397
	define_integer		975201644
	define_integer		2112058
'$SCNST_43_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_43_1'
'$SCNST_43':
	define_vector		'$SCNST_43_0'
'$SCNST_45_1':
	define_desc		27,3
	define_integer		1969516365
	define_integer		975201644
	define_integer		32
'$SCNST_45_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_45_1'
'$SCNST_74':
'$SCNST_69':
'$SCNST_63':
'$SCNST_45':
	define_vector		'$SCNST_45_0'
'$SCNST_46_1':
	define_desc		3,9
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		544173600
	define_integer		1818391920
	define_integer		1679844201
	define_integer		1634493285
	define_integer		1769234802
	define_integer		539913839
'$SCNST_46_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_46_1'
'$SCNST_46':
	define_vector		'$SCNST_46_0'
'$SCNST_47_1':
	define_desc		27,3
	define_integer		1818391888
	define_integer		975201129
	define_integer		32
'$SCNST_47_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_47_1'
'$SCNST_72':
'$SCNST_67':
'$SCNST_47':
	define_vector		'$SCNST_47_0'
'$SCNST_50_1':
	define_desc		3,8
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1970234400
	define_integer		544828514
	define_integer		1768318308
	define_integer		543450478
	define_integer		540686906
'$SCNST_50_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_50_1'
'$SCNST_50':
	define_vector		'$SCNST_50_0'
'$SCNST_52_1':
	define_desc		11,12
	define_integer		540950078
	define_integer		1852989783
	define_integer		543649385
	define_integer		1986994239
	define_integer		1634497125
	define_integer		1684369520
	define_integer		1769300512
	define_integer		1852404844
	define_integer		1701998624
	define_integer		1633904996
	define_integer		975201652
	define_integer		2112058
'$SCNST_52_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_52_1'
'$SCNST_52':
	define_vector		'$SCNST_52_0'
'$SCNST_53_1':
	define_desc		19,1
	define_integer		8236
'$SCNST_53_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_53_1'
'$SCNST_127':
'$SCNST_53':
	define_vector		'$SCNST_53_0'
'$SCNST_55_1':
	define_desc		3,11
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1819044128
	define_integer		1818322789
	define_integer		1651863584
	define_integer		543385964
	define_integer		1818453348
	define_integer		1952543329
	define_integer		544108393
	define_integer		540686906
'$SCNST_55_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_55_1'
'$SCNST_55':
	define_vector		'$SCNST_55_0'
'$SCNST_57_1':
	define_desc		3,1
	define_integer		544106784
'$SCNST_57_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_57_1'
'$SCNST_60':
'$SCNST_57':
	define_vector		'$SCNST_57_0'
'$SCNST_58_1':
	define_desc		3,11
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1635084064
	define_integer		1730176114
	define_integer		543973743
	define_integer		544501614
	define_integer		1819307369
	define_integer		1852140901
	define_integer		543450484
	define_integer		540686906
'$SCNST_58_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_58_1'
'$SCNST_58':
	define_vector		'$SCNST_58_0'
'$SCNST_61_1':
	define_desc		11,9
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1819044128
	define_integer		1818322789
	define_integer		1685021216
	define_integer		1869029497
	define_integer		975203425
	define_integer		2112058
'$SCNST_61_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_61_1'
'$SCNST_61':
	define_vector		'$SCNST_61_0'
'$SCNST_66_1':
	define_desc		27,12
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		1027423549
	define_integer		61
'$SCNST_66_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_66_1'
'$SCNST_93':
'$SCNST_91':
'$SCNST_89':
'$SCNST_85':
'$SCNST_83':
'$SCNST_77':
'$SCNST_70':
'$SCNST_66':
	define_vector		'$SCNST_66_0'
'$SCNST_79_1':
	define_desc		3,9
	define_integer		757935403
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
	define_integer		757935405
'$SCNST_79_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_79_1'
'$SCNST_126':
'$SCNST_124':
'$SCNST_119':
'$SCNST_117':
'$SCNST_112':
'$SCNST_110':
'$SCNST_105':
'$SCNST_103':
'$SCNST_88':
'$SCNST_86':
'$SCNST_81':
'$SCNST_79':
	define_vector		'$SCNST_79_0'
'$SCNST_80_1':
	define_desc		11,1
	define_integer		2105468
'$SCNST_80_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_80_1'
'$SCNST_125':
'$SCNST_122':
'$SCNST_118':
'$SCNST_115':
'$SCNST_111':
'$SCNST_108':
'$SCNST_104':
'$SCNST_101':
'$SCNST_96':
'$SCNST_87':
'$SCNST_80':
	define_vector		'$SCNST_80_0'
'$SCNST_82_1':
	define_desc		27,7
	define_integer		1918989639
	define_integer		1969365092
	define_integer		1769237609
	define_integer		1919950958
	define_integer		1667851365
	define_integer		1936028769
	define_integer		46
'$SCNST_82_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_82_1'
'$SCNST_82':
	define_vector		'$SCNST_82_0'
'$SCNST_84_1':
	define_desc		3,6
	define_integer		2036625218
	define_integer		1769300512
	define_integer		1852404844
	define_integer		1701998624
	define_integer		1633904996
	define_integer		779314548
'$SCNST_84_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_84_1'
'$SCNST_84':
	define_vector		'$SCNST_84_0'
'$SCNST_90_0':
	define_desc		3,2
	define_integer		1967597600
	define_integer		694448737
'$SCNST_90':
	define_string		'$SCNST_90_0'
'$SCNST_92_0':
	define_desc		3,0
'$SCNST_92':
	define_string		'$SCNST_92_0'
'$SCNST_94_1':
	define_desc		3,9
	define_integer		2122219051
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
	define_integer		2122219134
'$SCNST_94_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_94_1'
'$SCNST_123':
'$SCNST_120':
'$SCNST_116':
'$SCNST_113':
'$SCNST_109':
'$SCNST_106':
'$SCNST_102':
'$SCNST_99':
'$SCNST_97':
'$SCNST_94':
	define_vector		'$SCNST_94_0'
'$SCNST_95_1':
	define_desc		3,5
	define_integer		976894496
	define_integer		1819044128
	define_integer		1818322789
	define_integer		1919903264
	define_integer		779379053
'$SCNST_95_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_95_1'
'$SCNST_95':
	define_vector		'$SCNST_95_0'
'$SCNST_100_1':
	define_desc		19,6
	define_integer		976894496
	define_integer		1684960544
	define_integer		1852401253
	define_integer		1830839397
	define_integer		1819632751
	define_integer		11877
'$SCNST_100_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_100_1'
'$SCNST_107':
'$SCNST_100':
	define_vector		'$SCNST_100_0'
'$SCNST_114_1':
	define_desc		27,7
	define_integer		976894496
	define_integer		1684960544
	define_integer		1852401253
	define_integer		1881171045
	define_integer		1768187250
	define_integer		1702125923
	define_integer		46
'$SCNST_114_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_114_1'
'$SCNST_114':
	define_vector		'$SCNST_114_0'
'$SCNST_121_1':
	define_desc		11,7
	define_integer		976894496
	define_integer		1953459744
	define_integer		1769300512
	define_integer		1852404844
	define_integer		1701998624
	define_integer		1633904996
	define_integer		3040628
'$SCNST_121_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_121_1'
'$SCNST_121':
	define_vector		'$SCNST_121_0'
'$SCNST_128_0':
	define_desc		0,2
	define_atom		tab
	define_integer		4
'$SCNST_128':
	define_vector		'$SCNST_128_0'
