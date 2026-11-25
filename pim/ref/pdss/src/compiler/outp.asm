kl1cmp_output:
	module		kl1cmp_output
	entry		write_code_end,3,write_code_end_3_0
	entry		write_code_header,4,write_code_header_4_0
	entry		write_label,3,write_label_3_0
	entry		erace_or_convert_instruction,8,erace_or_convert_instruction_8_0
	entry		write_vector,3,write_vector_3_0
	entry		write_rkp_information,6,write_rkp_information_6_0
	entry		write_messages,3,write_messages_3_0
	entry		convert_code_for_PDSS,3,convert_code_for_PDSS_3_0
	entry		write_object_code,3,write_object_code_3_0
	entry		write_otherwise,3,write_otherwise_3_0
	entry		write_alternatively,2,write_alternatively_2_0
	entry		output_const_code,3,output_const_code_3_0
	module_entry		kl1cmp_output
	predicate		write_vector,3
write_vector_3_0:
	try_me_else		write_vector_3_1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,/
	read_element		3,1,9
	read_element		3,2,4
	wait_vector		9,3
	read_element		9,0,5
	wait_atom		5,/
	read_elements_inc		9,1,5,2
	put_structured_constant		7,'$SCNST_0'
	get_list_val_var		1,10,7,8
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		7,1,2
	put_reused_func		1,3,/
	write_elements_inc		1,1,5,2
	put_reused_func		3,9,/
	write_element_value		3,1,1
	write_element_value		3,2,4
	put_values_dec		1,8,2
	execute		3,write_vect_3_0
write_vector_3_1:
	otherwise		write_vector_3_0
	try_me_else		write_vector_3_6
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,/
	read_elements_inc		3,1,4,2
	put_structured_constant		6,'$SCNST_2'
	get_list_val_var		1,8,6,7
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		6,1,2
	put_reused_func		1,3,/
	write_elements_inc		1,1,4,2
	put_func		3,3,/
	write_element_value		3,1,1
	write_element_atom		3,2,top
	put_values_dec		1,7,2
	execute		3,write_vect_3_0
write_vector_3_6:
	otherwise		write_vector_3_0
	put_func		4,2,puttq
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
write_vector_3_11:
	suspend		write_vector_3_0
	module_entry		kl1cmp_output
	predicate		write_vect,3
write_vect_3_0:
	try_me_else		write_vect_3_1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,/
	read_elements_inc		3,1,4,2
	put_variable		6,8
	b_intern_atom		6,6
	put_func		7,2,putt
	write_element_value		7,1,6
	put_list_val_val		6,7,2
	get_list_value		1,6
	put_reused_func		1,3,/
	write_elements_inc		1,1,4,2
	put_value		2,8
	execute		2,convert_vector_to_string_2_0
write_vect_3_1:
	suspend		write_vect_3_0
	module_entry		kl1cmp_output
	predicate		convert_vector_to_string,2
convert_vector_to_string_2_0:
	try_me_else		convert_vector_to_string_2_1
	wait		1
	switch_on_type		1,convert_vector_to_string_2_2,convert_vector_to_string_2_3,convert_vector_to_string_2_1,convert_vector_to_string_2_4,convert_vector_to_string_2_1,convert_vector_to_string_2_1
convert_vector_to_string_2_2:
	b_atom_name		1,1
	get_value		1,2
	proceed
convert_vector_to_string_2_3:
	execute		2,convert_integer_to_string_2_0
convert_vector_to_string_2_4:
	test_arity		1,3,convert_vector_to_string_2_1
	read_element		1,0,3
	wait_atom		3,/
	read_elements_inc		1,1,3,2
	collect_vector		1
	create_goal		2
	put_list		1
	write_car_variable		1,7
	write_cdr_nil		1
	put_structured_constant		5,'$SCNST_4'
	put_list_val_val		6,5,1
	put_list		1
	write_car_variable		1,5
	write_cdr_value		1,6
	set_values_inc		1,1,2
	enqueue_goal		2,string_append_2_0
	create_goal		2
	set_value		1,4
	set_value		2,7
	enqueue_goal		2,convert_vector_to_string_2_0
	put_value		1,3
	put_value		2,5
	execute		2,convert_vector_to_string_2_0
convert_vector_to_string_2_1:
	suspend		convert_vector_to_string_2_0
	module_entry		kl1cmp_output
	predicate		string_append,2
string_append_2_0:
	try_me_else		string_append_2_1
	wait_list_var_var		1,3,4
	wait_nil		4
	collect_list		1
	get_value		2,3
	proceed
string_append_2_1:
	otherwise		string_append_2_0
	try_me_else		string_append_2_5
	wait_list_var_var		1,3,4
	collect_list		1
	put_variable		1,5
	b_append_string		3,1,1
	get_value		1,2
	put_values_inc		1,4,2
	execute		2,string_append_2_0
string_append_2_5:
	suspend		string_append_2_0
	module_entry		kl1cmp_output
	predicate		convert_integer_to_string,2
convert_integer_to_string_2_0:
	try_me_else		convert_integer_to_string_2_1
	integer		1
	put_value		4,1
	put_integer		3,10
	g_less_than		4,3
	put_value		3,2
	put_structured_constant		1,'$SCNST_5'
	put_value		2,4
	execute		3,convert_one_integer_to_string_3_0
convert_integer_to_string_2_1:
	otherwise		convert_integer_to_string_2_0
	try_me_else		convert_integer_to_string_2_5
	integer		1
	put_integer		3,10
	g_divide		1,3,3
	put_integer		4,10
	g_modulo		1,4,1
	put_variable		6,4
	put_variable		7,5
	b_append_string		6,7,6
	get_value		6,2
	create_goal		3
	put_structured_constant		2,'$SCNST_6'
	set_values_dec		1,2,2
	set_value		3,5
	enqueue_goal		3,convert_one_integer_to_string_3_0
	put_values_inc		1,3,2
	execute		2,convert_integer_to_string_2_0
convert_integer_to_string_2_5:
	suspend		convert_integer_to_string_2_0
	module_entry		kl1cmp_output
	predicate		convert_one_integer_to_string,3
convert_one_integer_to_string_3_0:
	put_integer		4,1
	b_substring		1,2,4,2,1
	get_value		2,3
	proceed
convert_one_integer_to_string_3_1:
	suspend		convert_one_integer_to_string_3_0
	module_entry		kl1cmp_output
	predicate		erace_or_convert_instruction,8
erace_or_convert_instruction_8_0:
	try_me_else		erace_or_convert_instruction_8_1
	jump_on_non_list_var_var		8,erace_or_convert_instruction_8_3,12,9
	collect_list		8
	put_values_inc		13,2,4
	put_value		11,7
	put_marked_value		2,11
	b_increment		2,2
	create_goal		8
	set_variable		1,3
	set_variable		2,4
	set_variable		3,7
	set_variable		4,8
	set_variable		5,10
	set_value		6,6
	set_value		7,2
	set_value		8,9
	enqueue_goal		8,erace_or_convert_instruction_8_0
	put_value		2,3
	put_value		3,13
	put_value		5,14
	put_value		6,7
	put_value		7,15
	put_value		9,16
	execute		12,erace_or_convert_one_instruction_12_0
erace_or_convert_instruction_8_3:
	check_nil		8,erace_or_convert_instruction_8_1
	collect_value		7
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_value		5,6
	proceed
erace_or_convert_instruction_8_1:
	suspend		erace_or_convert_instruction_8_0
	module_entry		kl1cmp_output
	predicate		erace_or_convert_gc_instruction,12
erace_or_convert_gc_instruction_12_0:
	try_me_else		erace_or_convert_gc_instruction_12_1
	jump_on_non_list_var_var		12,erace_or_convert_gc_instruction_12_3,13,14
	collect_list		12
	put_marked_value		12,11
	b_increment		12,12
	create_goal		12
	set_variable		1,19
	set_value		2,2
	set_variable		3,18
	set_value		4,4
	set_variable		5,17
	set_value		6,6
	set_variable		7,16
	set_value		8,8
	set_variable		9,15
	set_value		10,10
	set_value		11,12
	set_value		12,14
	enqueue_goal		12,erace_or_convert_gc_instruction_12_0
	put_value		2,19
	put_value		4,18
	put_value		6,17
	put_value		8,16
	put_value		10,15
	put_value		12,13
	execute		12,erace_or_convert_one_instruction_12_0
erace_or_convert_gc_instruction_12_3:
	check_nil		12,erace_or_convert_gc_instruction_12_1
	collect_value		11
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_gc_instruction_12_1:
	suspend		erace_or_convert_gc_instruction_12_0
	module_entry		kl1cmp_output
	predicate		erace_or_convert_one_instruction,12
erace_or_convert_one_instruction_12_0:
	try_me_else		erace_or_convert_one_instruction_12_1
	vector		1
	vector		3
	vector		7
	integer		11
	wait_vector		12,2
	read_element		12,0,13
	atom		13
	hash_on_atom		13,4,erace_or_convert_one_instruction_12_1
	bucket_entry_a		float,erace_or_convert_one_instruction_12_8
	bucket_entry_a		integer,erace_or_convert_one_instruction_12_9
	bucket_entry_a		string,erace_or_convert_one_instruction_12_10
	bucket_entry_a		vector,erace_or_convert_one_instruction_12_11
erace_or_convert_one_instruction_12_8:
	read_element		12,1,17
	wait_vector		17,3
	read_element		17,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		17,1,14,2
	integer		14
	g_vector_element		7,14,16
	wait_atom		16,float
	g_vector_element		1,14,16
	g_vector_element		3,14,14
	integer		16
	g_not_less_than		11,16
	integer		14
	g_not_less_than		14,11
	collect_value		15
	collect_vector		12
	collect_vector		17
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_9:
	read_element		12,1,17
	wait_vector		17,3
	read_element		17,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		17,1,14,2
	integer		14
	g_vector_element		7,14,16
	wait_atom		16,integer
	g_vector_element		1,14,16
	g_vector_element		3,14,14
	integer		16
	g_not_less_than		11,16
	integer		14
	g_not_less_than		14,11
	collect_value		15
	collect_vector		12
	collect_vector		17
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_10:
	read_element		12,1,17
	wait_vector		17,3
	read_element		17,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		17,1,14,2
	integer		14
	g_vector_element		7,14,16
	wait_atom		16,string
	g_vector_element		1,14,16
	g_vector_element		3,14,14
	integer		16
	g_not_less_than		11,16
	integer		14
	g_not_less_than		14,11
	collect_value		15
	collect_vector		12
	collect_vector		17
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_11:
	read_element		12,1,17
	wait_vector		17,3
	read_element		17,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		17,1,14,2
	integer		14
	g_vector_element		7,14,16
	wait_atom		16,vector
	g_vector_element		1,14,16
	g_vector_element		3,14,14
	integer		16
	g_not_less_than		11,16
	integer		14
	g_not_less_than		14,11
	collect_value		15
	collect_vector		12
	collect_vector		17
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_1:
	try_me_else		erace_or_convert_one_instruction_12_12
	vector		5
	wait_vector		12,3
	read_element		12,0,13
	atom		13
	hash_on_atom		13,4,erace_or_convert_one_instruction_12_12
	bucket_entry_a		get_list_value,erace_or_convert_one_instruction_12_16
	bucket_entry_a		put_value,erace_or_convert_one_instruction_12_17
	bucket_entry_a		trans_value,erace_or_convert_one_instruction_12_18
	bucket_entry_a		wait_variable,erace_or_convert_one_instruction_12_19
erace_or_convert_one_instruction_12_16:
	read_elements_inc		12,1,18,2
	wait_vector		19,3
	read_element		19,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		19,1,14,2
	wait_vector		18,3
	read_element		18,0,16
	wait_atom		16,'$VAR'
	read_elements_inc		18,1,16,2
	integer		16
	g_vector_element		5,16,16
	integer		14
	g_vector_element		5,14,14
	wait_value		16,14
	collect_value		15
	collect_value		17
	collect_value		11
	collect_vector		12
	collect_vector		18
	collect_vector		19
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_17:
	read_elements_inc		12,1,18,2
	wait_vector		19,3
	read_element		19,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		19,1,14,2
	wait_vector		18,3
	read_element		18,0,16
	wait_atom		16,'$VAR'
	read_elements_inc		18,1,16,2
	integer		16
	g_vector_element		5,16,16
	integer		14
	g_vector_element		5,14,14
	wait_value		16,14
	collect_value		15
	collect_value		17
	collect_value		11
	collect_vector		12
	collect_vector		18
	collect_vector		19
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_18:
	read_elements_inc		12,1,18,2
	wait_vector		19,3
	read_element		19,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		19,1,14,2
	wait_vector		18,3
	read_element		18,0,16
	wait_atom		16,'$VAR'
	read_elements_inc		18,1,16,2
	integer		16
	g_vector_element		5,16,16
	integer		14
	g_vector_element		5,14,14
	wait_value		16,14
	collect_value		15
	collect_value		17
	collect_value		11
	collect_vector		12
	collect_vector		18
	collect_vector		19
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_19:
	read_elements_inc		12,1,19,2
	wait_vector		20,3
	read_element		20,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		20,1,14,2
	wait_vector		19,3
	read_element		19,0,16
	wait_atom		16,'$VAR'
	read_elements_inc		19,1,16,2
	integer		16
	g_vector_element		5,16,18
	integer		14
	g_vector_element		5,14,21
	wait_value		18,21
	collect_value		15
	collect_value		17
	collect_value		11
	collect_vector		12
	collect_vector		19
	collect_vector		20
	get_value		9,10
	get_value		5,6
	get_value		3,4
	get_value		1,2
	put_values_inc		1,7,2
	put_value		3,16
	put_value		4,14
	execute		4,set_type_for_wait_variable_4_0
erace_or_convert_one_instruction_12_12:
	try_me_else		erace_or_convert_one_instruction_12_20
	jump_on_non_atom		12,erace_or_convert_one_instruction_12_22
	test_atom		12,commit,erace_or_convert_one_instruction_12_20
	collect_value		11
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
erace_or_convert_one_instruction_12_22:
	is_vector		12,erace_or_convert_one_instruction_12_20
	jump_on_arity		12,4,erace_or_convert_one_instruction_12_20
	table_entry		erace_or_convert_one_instruction_12_20
	table_entry		erace_or_convert_one_instruction_12_20
	table_entry		erace_or_convert_one_instruction_12_23
	table_entry		erace_or_convert_one_instruction_12_24
erace_or_convert_one_instruction_12_23:
	read_element		12,0,13
	wait_atom		13,'$Gc_code'
	read_element		12,1,13
	collect_vector		12
	put_value		12,13
	execute		12,erace_or_convert_gc_instruction_12_0
erace_or_convert_one_instruction_12_24:
	read_element		12,0,13
	wait_atom		13,get_marked_value
	read_elements_inc		12,1,13,2
	collect_value		11
	get_value		7,8
	get_value		3,4
	get_value		1,2
	create_goal		5
	set_variable		1,2
	set_value		2,6
	set_variable		3,4
	set_value		4,10
	put_reused_func		1,12,get_value
	write_element_marked_value		1,1,13
	write_element_value		1,2,14
	set_value		5,1
	enqueue_goal		5,convert_variable_5_0
	put_func		6,3,put_marked_value
	write_element_value		6,1,13
	write_element_value		6,2,13
	put_value		1,5
	put_value		3,9
	put_value		5,6
	execute		5,convert_variable_5_0
erace_or_convert_one_instruction_12_20:
	otherwise		erace_or_convert_one_instruction_12_0
	try_me_else		erace_or_convert_one_instruction_12_42
	wait_vector		12,3
	read_element		12,0,13
	atom		13
	branch_on_atom		13,2,erace_or_convert_one_instruction_12_42
	bucket_entry_a		trans_value,erace_or_convert_one_instruction_12_45
	bucket_entry_a		wait_variable,erace_or_convert_one_instruction_12_46
erace_or_convert_one_instruction_12_45:
	read_elements_inc		12,1,14,2
	collect_value		11
	get_value		7,8
	get_value		3,4
	get_value		1,2
	put_reused_func		7,12,put_value
	write_elements_inc		7,1,14,2
	put_values_inc		1,5,2
	put_values_inc		3,9,2
	put_value		5,7
	execute		5,convert_variable_5_0
erace_or_convert_one_instruction_12_46:
	read_elements_inc		12,1,14,2
	collect_value		11
	get_value		7,8
	get_value		3,4
	get_value		1,2
	put_reused_func		7,12,put_value
	write_elements_dec		7,1,15,2
	put_values_inc		1,5,2
	put_values_inc		3,9,2
	put_value		5,7
	execute		5,convert_variable_5_0
erace_or_convert_one_instruction_12_42:
	otherwise		erace_or_convert_one_instruction_12_0
	collect_value		11
	get_value		3,4
	get_value		1,2
	create_goal		5
	set_values_inc		1,5,2
	set_values_inc		3,9,2
	set_marked_value		5,12
	enqueue_goal		5,convert_variable_5_0
	put_values_inc		1,7,2
	put_value		3,12
	execute		3,obtain_type_info_3_0
erace_or_convert_one_instruction_12_52:
	suspend		erace_or_convert_one_instruction_12_0
	module_entry		kl1cmp_output
	predicate		set_type_for_wait_variable,4
set_type_for_wait_variable_4_0:
	try_me_else		set_type_for_wait_variable_4_1
	vector		1
	try_me_else		set_type_for_wait_variable_4_3
	integer		3
	try_me_else		set_type_for_wait_variable_4_5
	g_vector_element		1,3,5
	wait_atom		5,integer
	put_value		3,4
	put_atom		4,integer
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_5:
	try_me_else		set_type_for_wait_variable_4_6
	g_vector_element		1,3,5
	wait_atom		5,float
	put_value		3,4
	put_atom		4,float
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_6:
	try_me_else		set_type_for_wait_variable_4_7
	g_vector_element		1,3,5
	wait_atom		5,vector
	put_value		3,4
	put_atom		4,vector
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_7:
	try_me_else		set_type_for_wait_variable_4_3
	g_vector_element		1,3,5
	wait_atom		5,string
	put_value		3,4
	put_atom		4,string
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_3:
	try_me_else		set_type_for_wait_variable_4_1
	integer		4
	try_me_else		set_type_for_wait_variable_4_9
	g_vector_element		1,4,5
	wait_atom		5,integer
	put_atom		4,integer
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_9:
	try_me_else		set_type_for_wait_variable_4_10
	g_vector_element		1,4,5
	wait_atom		5,float
	put_atom		4,float
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_10:
	try_me_else		set_type_for_wait_variable_4_11
	g_vector_element		1,4,5
	wait_atom		5,vector
	put_atom		4,vector
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_11:
	try_me_else		set_type_for_wait_variable_4_1
	g_vector_element		1,4,5
	wait_atom		5,string
	put_atom		4,string
	execute		4,set_vector_element_4_0
set_type_for_wait_variable_4_1:
	otherwise		set_type_for_wait_variable_4_0
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
set_type_for_wait_variable_4_16:
	suspend		set_type_for_wait_variable_4_0
	module_entry		kl1cmp_output
	predicate		obtain_type_info,3
obtain_type_info_3_0:
	try_me_else		obtain_type_info_3_1
	vector		1
	wait_vector		3,3
	read_element		3,0,4
	wait_atom		4,wait_variable
	read_element		3,1,5
	wait_vector		5,3
	read_element		5,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		5,1,7,2
	read_element		3,2,9
	wait_vector		9,3
	read_element		9,0,10
	wait_atom		10,'$VAR'
	read_element		9,1,11
	integer		11
	read_element		9,2,12
	try_me_else		obtain_type_info_3_10
	g_vector_element		1,11,13
	wait_atom		13,integer
	collect_value		12
	collect_value		8
	collect_vector		3
	collect_vector		5
	collect_vector		9
	put_value		3,7
	put_atom		4,integer
	execute		4,set_vector_element_4_0
obtain_type_info_3_10:
	try_me_else		obtain_type_info_3_11
	g_vector_element		1,11,13
	wait_atom		13,float
	collect_value		12
	collect_value		8
	collect_vector		3
	collect_vector		5
	collect_vector		9
	put_value		3,7
	put_atom		4,float
	execute		4,set_vector_element_4_0
obtain_type_info_3_11:
	try_me_else		obtain_type_info_3_12
	g_vector_element		1,11,13
	wait_atom		13,vector
	collect_value		12
	collect_value		8
	collect_vector		3
	collect_vector		5
	collect_vector		9
	put_value		3,7
	put_atom		4,vector
	execute		4,set_vector_element_4_0
obtain_type_info_3_12:
	try_me_else		obtain_type_info_3_13
	g_vector_element		1,11,13
	wait_atom		13,vector
	collect_value		12
	collect_value		8
	collect_vector		3
	collect_vector		5
	collect_vector		9
	put_value		3,7
	put_atom		4,vector
	execute		4,set_vector_element_4_0
obtain_type_info_3_13:
	try_me_else		obtain_type_info_3_1
	g_vector_element		1,11,13
	wait_atom		13,string
	collect_value		12
	collect_value		8
	collect_vector		3
	collect_vector		5
	collect_vector		9
	put_value		3,7
	put_atom		4,string
	execute		4,set_vector_element_4_0
obtain_type_info_3_1:
	try_me_else		obtain_type_info_3_14
	wait_vector		3,2
	read_element		3,0,4
	atom		4
	hash_on_atom		4,5,obtain_type_info_3_14
	bucket_entry_a		builtin,obtain_type_info_3_17
	bucket_entry_a		float,obtain_type_info_3_18
	bucket_entry_a		integer,obtain_type_info_3_19
	bucket_entry_a		string,obtain_type_info_3_20
	bucket_entry_a		vector,obtain_type_info_3_21
obtain_type_info_3_17:
	read_element		3,1,5
	collect_vector		3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,6
	enqueue_goal		3,obtain_builtin_info_3_0
	put_value		1,5
	put_void		2
	put_void		3
	put_void		4
	put_void		5
	put_void		7
	execute_external		kl1cmp_blttbl,builtin,7
obtain_type_info_3_18:
	read_element		3,1,7
	wait_vector		7,3
	read_element		7,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		7,1,5,2
	collect_value		6
	collect_vector		3
	collect_vector		7
	put_value		3,5
	put_atom		4,float
	execute		4,set_vector_element_4_0
obtain_type_info_3_19:
	read_element		3,1,7
	wait_vector		7,3
	read_element		7,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		7,1,5,2
	collect_value		6
	collect_vector		3
	collect_vector		7
	put_value		3,5
	put_atom		4,integer
	execute		4,set_vector_element_4_0
obtain_type_info_3_20:
	read_element		3,1,7
	wait_vector		7,3
	read_element		7,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		7,1,5,2
	collect_value		6
	collect_vector		3
	collect_vector		7
	put_value		3,5
	put_atom		4,string
	execute		4,set_vector_element_4_0
obtain_type_info_3_21:
	read_element		3,1,7
	wait_vector		7,3
	read_element		7,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		7,1,5,2
	collect_value		6
	collect_vector		3
	collect_vector		7
	put_value		3,5
	put_atom		4,vector
	execute		4,set_vector_element_4_0
obtain_type_info_3_14:
	otherwise		obtain_type_info_3_0
	collect_value		3
	get_value		1,2
	proceed
obtain_type_info_3_47:
	suspend		obtain_type_info_3_0
	module_entry		kl1cmp_output
	predicate		obtain_builtin_info,3
obtain_builtin_info_3_0:
	try_me_else		obtain_builtin_info_3_1
	list		3
	read_car		3,4
	wait_vector		4,2
	read_element		4,0,5
	atom		5
	hash_on_atom		5,4,obtain_builtin_info_3_1
	bucket_entry_a		float,obtain_builtin_info_3_5
	bucket_entry_a		integer,obtain_builtin_info_3_6
	bucket_entry_a		string,obtain_builtin_info_3_7
	bucket_entry_a		vector,obtain_builtin_info_3_8
obtain_builtin_info_3_5:
	read_cdr		3,6
	read_element		4,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		9,1,7,2
	collect_list		3
	collect_value		8
	collect_vector		4
	collect_vector		9
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,obtain_builtin_info_3_0
	put_value		2,3
	put_value		3,7
	put_atom		4,float
	execute		4,set_vector_element_4_0
obtain_builtin_info_3_6:
	read_cdr		3,6
	read_element		4,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		9,1,7,2
	collect_list		3
	collect_value		8
	collect_vector		4
	collect_vector		9
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,obtain_builtin_info_3_0
	put_value		2,3
	put_value		3,7
	put_atom		4,integer
	execute		4,set_vector_element_4_0
obtain_builtin_info_3_7:
	read_cdr		3,6
	read_element		4,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		9,1,7,2
	collect_list		3
	collect_value		8
	collect_vector		4
	collect_vector		9
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,obtain_builtin_info_3_0
	put_value		2,3
	put_value		3,7
	put_atom		4,string
	execute		4,set_vector_element_4_0
obtain_builtin_info_3_8:
	read_cdr		3,6
	read_element		4,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		9,1,7,2
	collect_list		3
	collect_value		8
	collect_vector		4
	collect_vector		9
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,obtain_builtin_info_3_0
	put_value		2,3
	put_value		3,7
	put_atom		4,vector
	execute		4,set_vector_element_4_0
obtain_builtin_info_3_1:
	otherwise		obtain_builtin_info_3_0
	try_me_else		obtain_builtin_info_3_15
	jump_on_non_list_var_var		3,obtain_builtin_info_3_17,4,5
	collect_list		3
	collect_value		4
	put_value		3,5
	execute		3,obtain_builtin_info_3_0
obtain_builtin_info_3_17:
	check_nil		3,obtain_builtin_info_3_15
	get_value		1,2
	proceed
obtain_builtin_info_3_15:
	suspend		obtain_builtin_info_3_0
	module_entry		kl1cmp_output
	predicate		convert_variable,5
convert_variable_5_0:
	try_me_else		convert_variable_5_1
	wait		5
	switch_on_type		5,convert_variable_5_2,convert_variable_5_3,convert_variable_5_1,convert_variable_5_4,convert_variable_5_1,convert_variable_5_5
convert_variable_5_2:
	get_value		1,2
	put_list_val_val		1,5,4
	get_list_value		3,1
	proceed
convert_variable_5_3:
	get_value		1,2
	put_list_val_val		1,5,4
	get_list_value		3,1
	proceed
convert_variable_5_4:
	test_arity		5,2,convert_variable_5_1
	read_element		5,0,6
	wait_atom		6,builtin
	read_element		5,1,6
	collect_vector		5
	put_value		5,6
	execute		5,convert_variable_5_0
convert_variable_5_5:
	is_float		5,convert_variable_5_1
	get_value		1,2
	put_list_val_val		1,5,4
	get_list_value		3,1
	proceed
convert_variable_5_1:
	otherwise		convert_variable_5_0
	try_me_else		convert_variable_5_9
	vector		5
	put_value		6,5
	g_vector		6,5
	execute		6,convert_args_6_0
convert_variable_5_9:
	suspend		convert_variable_5_0
	module_entry		kl1cmp_output
	predicate		convert_args,6
convert_args_6_0:
	try_me_else		convert_args_6_1
	wait_integer		5,0
	get_value		1,2
	put_list_val_val		1,6,4
	get_list_value		3,1
	proceed
convert_args_6_1:
	b_decrement		5,5
	put_marked_value		7,5
	put_variable		9,8
	b_set_vector_element		6,7,6,9,7
	create_goal		6
	set_variable		1,10
	set_value		2,2
	set_variable		3,9
	set_values_inc		4,4,2
	set_value		6,7
	enqueue_goal		6,convert_args_6_0
	put_value		2,10
	put_value		4,9
	put_value		5,6
	put_value		6,8
	execute		6,convert_one_arg_6_0
convert_args_6_3:
	suspend		convert_args_6_0
	module_entry		kl1cmp_output
	predicate		convert_one_arg,6
convert_one_arg_6_0:
	try_me_else		convert_one_arg_6_1
	wait		5
	switch_on_type		5,convert_one_arg_6_2,convert_one_arg_6_3,convert_one_arg_6_1,convert_one_arg_6_4,convert_one_arg_6_1,convert_one_arg_6_5
convert_one_arg_6_2:
	get_value		3,4
	get_value		1,2
	get_value		6,5
	proceed
convert_one_arg_6_3:
	get_value		3,4
	get_value		1,2
	get_value		6,5
	proceed
convert_one_arg_6_4:
	test_arity		5,3,convert_one_arg_6_1
	read_element		5,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		5,1,7,2
	collect_value		8
	collect_vector		5
	get_value		3,4
	put_values_dec		3,7,2
	execute		4,ref_vector_element_4_0
convert_one_arg_6_5:
	is_float		5,convert_one_arg_6_1
	get_value		3,4
	get_value		1,2
	get_value		6,5
	proceed
convert_one_arg_6_1:
	otherwise		convert_one_arg_6_0
	get_value		3,4
	get_value		1,2
	get_value		5,6
	proceed
convert_one_arg_6_9:
	suspend		convert_one_arg_6_0
	module_entry		kl1cmp_output
	predicate		write_object_code,3
write_object_code_3_0:
	try_me_else		write_object_code_3_1
	jump_on_non_list_var_var		3,write_object_code_3_3,4,5
	collect_list		3
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	enqueue_goal		3,write_object_code_3_0
	put_values_inc		2,3,2
	execute		3,write_one_object_code_3_0
write_object_code_3_3:
	check_nil		3,write_object_code_3_1
	get_value		1,2
	proceed
write_object_code_3_1:
	suspend		write_object_code_3_0
	module_entry		kl1cmp_output
	predicate		write_one_object_code,3
write_one_object_code_3_0:
	try_me_else		write_one_object_code_3_1
	wait		3
	switch_on_type		3,write_one_object_code_3_2,write_one_object_code_3_3,write_one_object_code_3_1,write_one_object_code_3_4,write_one_object_code_3_1,write_one_object_code_3_5
write_one_object_code_3_2:
	test_nil		3,write_one_object_code_3_6
	get_value		1,2
	proceed
write_one_object_code_3_6:
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_7'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
write_one_object_code_3_3:
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_8'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
write_one_object_code_3_4:
	g_vector		3,4
	put_integer		5,0
	put_nil		6
	b_set_vector_element		3,5,3,6,5
	b_decrement		4,4
	put_structured_constant		6,'$SCNST_9'
	put_list_val_var		7,6,8
	put_func		6,2,putt
	write_element_value		6,1,3
	put_list_val_val		3,6,7
	put_structured_constant		6,'$SCNST_10'
	put_list_val_val		7,6,3
	get_list_value		1,7
	put_value		1,8
	put_value		3,4
	put_integer		4,1
	execute		5,write_args_5_0
write_one_object_code_3_5:
	is_float		3,write_one_object_code_3_1
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_11'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
write_one_object_code_3_1:
	suspend		write_one_object_code_3_0
	module_entry		kl1cmp_output
	predicate		write_args,5
write_args_5_0:
	try_me_else		write_args_5_1
	wait_integer		3,1
	put_nil		3
	b_set_vector_element		5,4,3,3,4
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_value		2,4
	execute		3,write_one_arg_3_0
write_args_5_1:
	otherwise		write_args_5_0
	put_marked_value		6,4
	put_nil		7
	b_set_vector_element		5,6,5,7,6
	b_decrement		3,3
	b_increment		4,4
	put_structured_constant		7,'$SCNST_12'
	put_list_val_var		8,7,7
	create_goal		5
	set_value		1,7
	set_values_inc		2,2,3
	set_value		5,6
	enqueue_goal		5,write_args_5_0
	put_value		2,8
	put_value		3,5
	execute		3,write_one_arg_3_0
write_args_5_6:
	suspend		write_args_5_0
	module_entry		kl1cmp_output
	predicate		write_one_arg,3
write_one_arg_3_0:
	try_me_else		write_one_arg_3_1
	wait		3
	switch_on_type		3,write_one_arg_3_2,write_one_arg_3_3,write_one_arg_3_1,write_one_arg_3_1,write_one_arg_3_1,write_one_arg_3_4
write_one_arg_3_2:
	branch_on_atom		3,2,write_one_arg_3_5
	bucket_entry_a		'!',write_one_arg_3_6
	bucket_entry_a		'|',write_one_arg_3_7
write_one_arg_3_6:
	put_structured_constant		3,'$SCNST_13'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
write_one_arg_3_7:
	put_structured_constant		3,'$SCNST_14'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
write_one_arg_3_5:
	put_atom		4,'|'
	g_diff		3,4
	put_atom		4,'!'
	g_diff		3,4
	put_func		4,2,puttq
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
write_one_arg_3_3:
	put_func		4,2,puttq
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
write_one_arg_3_4:
	is_float		3,write_one_arg_3_1
	put_func		4,2,puttq
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
write_one_arg_3_1:
	otherwise		write_one_arg_3_0
	execute		3,write_vector_3_0
write_one_arg_3_10:
	suspend		write_one_arg_3_0
	module_entry		kl1cmp_output
	predicate		write_otherwise,3
write_otherwise_3_0:
	put_structured_constant		4,'$SCNST_15'
	put_list_val_var		5,4,7
	put_structured_constant		4,'$SCNST_16'
	put_list_val_val		6,4,5
	put_structured_constant		4,'$SCNST_17'
	put_list_val_val		5,4,6
	get_list_value		1,5
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_value		1,7
	put_value		2,4
	execute		3,write_vector_3_0
write_otherwise_3_1:
	suspend		write_otherwise_3_0
	module_entry		kl1cmp_output
	predicate		write_alternatively,2
write_alternatively_2_0:
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_structured_constant		2,'$SCNST_18'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_19'
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
write_alternatively_2_1:
	suspend		write_alternatively_2_0
	module_entry		kl1cmp_output
	predicate		convert_code_for_PDSS,3
convert_code_for_PDSS_3_0:
	create_goal		5
	set_variable		1,4
	set_value		2,2
	put_structured_constant		2,'$SCNST_20'
	set_value		3,2
	set_void		4
	set_value		5,3
	enqueue_goal		5,convert_code_for_PDSS_5_0
	put_value		2,4
	execute		2,optimize_2_0
convert_code_for_PDSS_3_1:
	suspend		convert_code_for_PDSS_3_0
	module_entry		kl1cmp_output
	predicate		convert_code_for_PDSS,5
convert_code_for_PDSS_5_0:
	try_me_else		convert_code_for_PDSS_5_1
	jump_on_non_list_var_var		5,convert_code_for_PDSS_5_3,6,7
	collect_list		5
	create_goal		5
	set_variable		1,8
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,7
	enqueue_goal		5,convert_code_for_PDSS_5_0
	put_value		2,8
	put_values_inc		4,5,2
	execute		5,tbl_5_0
convert_code_for_PDSS_5_3:
	check_nil		5,convert_code_for_PDSS_5_1
	get_value		3,4
	get_value		1,2
	proceed
convert_code_for_PDSS_5_1:
	suspend		convert_code_for_PDSS_5_0
	module_entry		kl1cmp_output
	predicate		write_label,3
write_label_3_0:
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_structured_constant		2,'$SCNST_21'
	put_list_val_val		5,2,4
	put_value		2,5
	execute		3,write_vector_3_0
write_label_3_1:
	suspend		write_label_3_0
	module_entry		kl1cmp_output
	predicate		write_code_header,4
write_code_header_4_0:
	try_me_else		write_code_header_4_1
	jump_on_non_atom		3,write_code_header_4_3
	test_nil		3,write_code_header_4_1
	collect_value		4
	get_value		1,2
	proceed
write_code_header_4_3:
	check_vector		3,3,write_code_header_4_1
	read_element		3,0,5
	wait_atom		5,/
	read_elements_inc		3,1,5,2
	collect_vector		3
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	put_func		2,2,puttq
	write_element_value		2,1,6
	put_list_val_val		6,2,3
	put_structured_constant		2,'$SCNST_22'
	put_list_val_val		3,2,6
	put_func		2,2,puttq
	write_element_value		2,1,5
	put_list_val_val		5,2,3
	put_structured_constant		2,'$SCNST_23'
	put_list_val_val		3,2,5
	put_structured_constant		2,'$SCNST_24'
	put_list_val_val		5,2,3
	put_structured_constant		2,'$SCNST_25'
	put_list_val_val		3,2,5
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_func		3,2,puttq
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_26'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_27'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
write_code_header_4_1:
	suspend		write_code_header_4_0
	module_entry		kl1cmp_output
	predicate		write_code_end,3
write_code_end_3_0:
	put_structured_constant		4,'$SCNST_29'
	put_list_val_var		5,4,7
	put_structured_constant		4,'$SCNST_30'
	put_list_val_val		6,4,5
	put_structured_constant		4,'$SCNST_31'
	put_list_val_val		5,4,6
	put_structured_constant		4,'$SCNST_32'
	put_list_val_val		6,4,5
	get_list_value		1,6
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_value		1,7
	put_value		2,4
	execute		3,write_vector_3_0
write_code_end_3_1:
	suspend		write_code_end_3_0
	module_entry		kl1cmp_output
	predicate		write_rkp_information,6
write_rkp_information_6_0:
	put_list		7
	write_car_atom		7,nl
	write_cdr_variable		7,11
	put_func		8,2,puttq
	write_element_marked_variable		8,1,10
	put_list_val_val		9,8,7
	put_structured_constant		7,'$SCNST_33'
	put_list_val_val		8,7,9
	put_structured_constant		7,'$SCNST_34'
	put_list_val_val		9,7,8
	put_structured_constant		7,'$SCNST_35'
	put_list_val_val		8,7,9
	put_list		7
	write_car_atom		7,nl
	write_cdr_value		7,8
	put_structured_constant		8,'$SCNST_36'
	put_list_val_val		9,8,7
	put_func		7,2,puttq
	write_element_value		7,1,10
	put_list_val_val		8,7,9
	create_goal		5
	set_value		1,11
	set_value		2,2
	set_variable		3,7
	set_value		4,4
	set_value		5,6
	enqueue_goal		5,write_public_5_0
	put_value		2,8
	put_value		4,7
	put_value		6,10
	execute		6,write_module_6_0
write_rkp_information_6_1:
	suspend		write_rkp_information_6_0
	module_entry		kl1cmp_output
	predicate		write_public,5
write_public_5_0:
	try_me_else		write_public_5_1
	jump_on_non_list_var_var		5,write_public_5_3,12,6
	wait_vector		12,3
	read_element		12,0,7
	wait_atom		7,/
	read_elements_inc		12,1,7,2
	put_structured_constant		9,'$SCNST_37'
	put_reused_list_val_var		5,5,9,11
	put_func		9,2,puttq
	write_element_marked_value		9,1,8
	put_list_val_val		10,9,5
	put_structured_constant		5,'$SCNST_38'
	put_list_val_val		9,5,10
	put_func		5,2,puttq
	write_element_marked_value		5,1,7
	put_list_val_val		10,5,9
	put_structured_constant		5,'$SCNST_39'
	put_list_val_val		9,5,10
	put_structured_constant		5,'$SCNST_40'
	put_list_val_val		10,5,9
	put_structured_constant		5,'$SCNST_41'
	put_list_val_val		9,5,10
	get_list_value		1,9
	put_list		5
	write_car_atom		5,nl
	write_cdr_variable		5,1
	create_goal		5
	set_values_inc		1,1,4
	set_value		5,6
	enqueue_goal		5,write_public_5_0
	put_reused_func		3,12,/
	write_elements_inc		3,1,7,2
	put_value		1,11
	put_value		2,5
	execute		3,write_vector_3_0
write_public_5_3:
	check_nil		5,write_public_5_1
	get_value		3,4
	get_value		1,2
	proceed
write_public_5_1:
	otherwise		write_public_5_0
	try_me_else		write_public_5_8
	wait_list_var_var		5,6,7
	put_reused_list		5,5
	write_car_value		5,6
	write_cdr_nil		5
	put_structured_constant		6,'$SCNST_42'
	put_func		8,3,error_message
	write_elements_dec		8,1,6,2
	get_list_val_var		3,6,8,5
	put_value		3,5
	put_value		5,7
	execute		5,write_public_5_0
write_public_5_8:
	suspend		write_public_5_0
	module_entry		kl1cmp_output
	predicate		write_module,6
write_module_6_0:
	try_me_else		write_module_6_1
	wait_nil		5
	get_value		1,2
	get_nil		6
	put_structured_constant		1,'$SCNST_43'
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
write_module_6_1:
	otherwise		write_module_6_0
	get_value		3,4
	get_value		1,2
	get_value		5,6
	proceed
write_module_6_6:
	suspend		write_module_6_0
	module_entry		kl1cmp_output
	predicate		write_messages,3
write_messages_3_0:
	try_me_else		write_messages_3_1
	jump_on_non_list_var_var		3,write_messages_3_3,4,5
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,7
	put_func		6,2,putt
	write_element_value		6,1,4
	put_list_val_val		4,6,3
	put_structured_constant		3,'$SCNST_44'
	put_list_val_val		6,3,4
	put_structured_constant		3,'$SCNST_45'
	put_list_val_val		4,3,6
	put_structured_constant		3,'$SCNST_46'
	put_list_val_val		6,3,4
	get_list_value		1,6
	put_value		1,7
	put_value		3,5
	execute		3,write_messages_3_0
write_messages_3_3:
	check_nil		3,write_messages_3_1
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,2
	get_list_value		1,3
	proceed
write_messages_3_1:
	suspend		write_messages_3_0
	module_entry		kl1cmp_output
	predicate		'$tbl/1_0',4
'$tbl/1_0_4_0':
	try_me_else		'$tbl/1_0_4_1'
	wait_vector		3,3
	read_element		3,0,5
	atom		5
	branch_on_atom		5,2,'$tbl/1_0_4_1'
	bucket_entry_a		list,'$tbl/1_0_4_4'
	bucket_entry_a		vector,'$tbl/1_0_4_5'
'$tbl/1_0_4_4':
	read_elements_inc		3,1,6,2
	atom		7
	branch_on_atom		7,2,'$tbl/1_0_4_1'
	bucket_entry_a		car,'$tbl/1_0_4_7'
	bucket_entry_a		cdr,'$tbl/1_0_4_8'
'$tbl/1_0_4_7':
	put_reused_func		3,3,list
	write_element_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	get_value		1,2
	proceed
'$tbl/1_0_4_8':
	put_reused_func		3,3,list
	write_element_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	get_value		1,2
	proceed
'$tbl/1_0_4_5':
	read_elements_inc		3,1,6,2
	put_reused_func		5,3,vector
	write_element_value		5,1,6
	write_element_variable		5,2,3
	get_vector_value		4,5
	get_value		1,2
	b_increment		7,1
	get_value		3,1
	proceed
'$tbl/1_0_4_1':
	suspend		'$tbl/1_0_4_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_1',5
'$tbl/1_1_5_0':
	try_me_else		'$tbl/1_1_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_1_5_1'
	bucket_entry_a		list,'$tbl/1_1_5_4'
	bucket_entry_a		vector,'$tbl/1_1_5_5'
'$tbl/1_1_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_1_5_1'
	bucket_entry_a		car,'$tbl/1_1_5_7'
	bucket_entry_a		cdr,'$tbl/1_1_5_8'
'$tbl/1_1_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,read_car
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_1_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,read_cdr
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_1_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,read_element
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_1_5_1':
	suspend		'$tbl/1_1_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_2',5
'$tbl/1_2_5_0':
	try_me_else		'$tbl/1_2_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_2_5_1'
	bucket_entry_a		list,'$tbl/1_2_5_4'
	bucket_entry_a		vector,'$tbl/1_2_5_5'
'$tbl/1_2_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_2_5_1'
	bucket_entry_a		car,'$tbl/1_2_5_7'
	bucket_entry_a		cdr,'$tbl/1_2_5_8'
'$tbl/1_2_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_value
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_2_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_value
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_2_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_value
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_2_5_1':
	suspend		'$tbl/1_2_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_3',5
'$tbl/1_3_5_0':
	try_me_else		'$tbl/1_3_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_3_5_1'
	bucket_entry_a		list,'$tbl/1_3_5_4'
	bucket_entry_a		vector,'$tbl/1_3_5_5'
'$tbl/1_3_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_3_5_1'
	bucket_entry_a		car,'$tbl/1_3_5_7'
	bucket_entry_a		cdr,'$tbl/1_3_5_8'
'$tbl/1_3_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_marked_value
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_3_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_marked_value
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_3_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_marked_value
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_3_5_1':
	suspend		'$tbl/1_3_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_4',4
'$tbl/1_4_4_0':
	try_me_else		'$tbl/1_4_4_1'
	wait_vector		3,3
	read_element		3,0,5
	atom		5
	branch_on_atom		5,2,'$tbl/1_4_4_1'
	bucket_entry_a		list,'$tbl/1_4_4_4'
	bucket_entry_a		vector,'$tbl/1_4_4_5'
'$tbl/1_4_4_4':
	read_elements_inc		3,1,6,2
	atom		7
	branch_on_atom		7,2,'$tbl/1_4_4_1'
	bucket_entry_a		car,'$tbl/1_4_4_7'
	bucket_entry_a		cdr,'$tbl/1_4_4_8'
'$tbl/1_4_4_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,2,write_car_nil
	write_element_value		3,1,6
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_4_4_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,2,write_cdr_nil
	write_element_value		3,1,6
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_4_4_5':
	read_elements_inc		3,1,6,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,6
	write_element_variable		3,2,5
	get_vector_value		4,3
	put_func		3,3,write_element_nil
	write_element_value		3,1,6
	write_element_marked_value		3,2,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		7,1
	get_value		5,1
	proceed
'$tbl/1_4_4_1':
	suspend		'$tbl/1_4_4_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_5',5
'$tbl/1_5_5_0':
	try_me_else		'$tbl/1_5_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_5_5_1'
	bucket_entry_a		list,'$tbl/1_5_5_4'
	bucket_entry_a		vector,'$tbl/1_5_5_5'
'$tbl/1_5_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_5_5_1'
	bucket_entry_a		car,'$tbl/1_5_5_7'
	bucket_entry_a		cdr,'$tbl/1_5_5_8'
'$tbl/1_5_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_atom
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_5_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_atom
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_5_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_atom
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_5_5_1':
	suspend		'$tbl/1_5_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_6',5
'$tbl/1_6_5_0':
	try_me_else		'$tbl/1_6_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_6_5_1'
	bucket_entry_a		list,'$tbl/1_6_5_4'
	bucket_entry_a		vector,'$tbl/1_6_5_5'
'$tbl/1_6_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_6_5_1'
	bucket_entry_a		car,'$tbl/1_6_5_7'
	bucket_entry_a		cdr,'$tbl/1_6_5_8'
'$tbl/1_6_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_integer
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_6_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_integer
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_6_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_integer
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_6_5_1':
	suspend		'$tbl/1_6_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_7',5
'$tbl/1_7_5_0':
	try_me_else		'$tbl/1_7_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_7_5_1'
	bucket_entry_a		list,'$tbl/1_7_5_4'
	bucket_entry_a		vector,'$tbl/1_7_5_5'
'$tbl/1_7_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_7_5_1'
	bucket_entry_a		car,'$tbl/1_7_5_7'
	bucket_entry_a		cdr,'$tbl/1_7_5_8'
'$tbl/1_7_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_float
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_7_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_float
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_7_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_float
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_7_5_1':
	suspend		'$tbl/1_7_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_8',4
'$tbl/1_8_4_0':
	try_me_else		'$tbl/1_8_4_1'
	wait_vector		3,3
	read_element		3,0,5
	atom		5
	branch_on_atom		5,2,'$tbl/1_8_4_1'
	bucket_entry_a		list,'$tbl/1_8_4_4'
	bucket_entry_a		vector,'$tbl/1_8_4_5'
'$tbl/1_8_4_4':
	read_elements_inc		3,1,6,2
	atom		7
	branch_on_atom		7,2,'$tbl/1_8_4_1'
	bucket_entry_a		car,'$tbl/1_8_4_7'
	bucket_entry_a		cdr,'$tbl/1_8_4_8'
'$tbl/1_8_4_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,2,write_car_void
	write_element_value		3,1,6
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_8_4_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,6
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,2,write_cdr_void
	write_element_value		3,1,6
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_8_4_5':
	read_elements_inc		3,1,6,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,6
	write_element_variable		3,2,5
	get_vector_value		4,3
	put_func		3,3,write_element_void
	write_element_value		3,1,6
	write_element_marked_value		3,2,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		7,1
	get_value		5,1
	proceed
'$tbl/1_8_4_1':
	suspend		'$tbl/1_8_4_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_9',5
'$tbl/1_9_5_0':
	try_me_else		'$tbl/1_9_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_9_5_1'
	bucket_entry_a		list,'$tbl/1_9_5_4'
	bucket_entry_a		vector,'$tbl/1_9_5_5'
'$tbl/1_9_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_9_5_1'
	bucket_entry_a		car,'$tbl/1_9_5_7'
	bucket_entry_a		cdr,'$tbl/1_9_5_8'
'$tbl/1_9_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_variable
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_9_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_variable
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_9_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_variable
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_9_5_1':
	suspend		'$tbl/1_9_5_0'
	module_entry		kl1cmp_output
	predicate		'$tbl/1_10',5
'$tbl/1_10_5_0':
	try_me_else		'$tbl/1_10_5_1'
	wait_vector		3,3
	read_element		3,0,6
	atom		6
	branch_on_atom		6,2,'$tbl/1_10_5_1'
	bucket_entry_a		list,'$tbl/1_10_5_4'
	bucket_entry_a		vector,'$tbl/1_10_5_5'
'$tbl/1_10_5_4':
	read_elements_inc		3,1,7,2
	atom		8
	branch_on_atom		8,2,'$tbl/1_10_5_1'
	bucket_entry_a		car,'$tbl/1_10_5_7'
	bucket_entry_a		cdr,'$tbl/1_10_5_8'
'$tbl/1_10_5_7':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_car_marked_variable
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_10_5_8':
	put_reused_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,cdr
	get_vector_value		4,3
	put_func		3,3,write_cdr_marked_variable
	write_element_value		3,1,7
	write_element_value		3,2,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
'$tbl/1_10_5_5':
	read_elements_inc		3,1,7,2
	put_reused_func		3,3,vector
	write_element_marked_value		3,1,7
	write_element_variable		3,2,6
	get_vector_value		4,3
	put_func		3,4,write_element_marked_variable
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	write_element_value		3,3,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	b_increment		8,1
	get_value		6,1
	proceed
'$tbl/1_10_5_1':
	suspend		'$tbl/1_10_5_0'
	module_entry		kl1cmp_output
	predicate		tbl,5
tbl_5_0:
	try_me_else		tbl_5_1
	jump_on_non_atom		5,tbl_5_3
	test_atom		5,collect_stack,tbl_5_1
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_3:
	is_vector		5,tbl_5_1
	jump_on_arity		5,5,tbl_5_1
	table_entry		tbl_5_1
	table_entry		tbl_5_1
	table_entry		tbl_5_4
	table_entry		tbl_5_5
	table_entry		tbl_5_6
tbl_5_4:
	read_element		5,0,6
	atom		6
	hash_on_atom		6,17,tbl_5_1
	bucket_entry_a		create_goal,tbl_5_8
	bucket_entry_a		device_dup_check,tbl_5_9
	bucket_entry_a		enqueue_goal,tbl_5_10
	bucket_entry_a		execute,tbl_5_11
	bucket_entry_a		halt,tbl_5_12
	bucket_entry_a		put_list,tbl_5_13
	bucket_entry_a		read_variable,tbl_5_14
	bucket_entry_a		request_gc,tbl_5_15
	bucket_entry_a		set_backtrace_switch,tbl_5_16
	bucket_entry_a		set_scheduling_switch,tbl_5_17
	bucket_entry_a		set_trace_switch,tbl_5_18
	bucket_entry_a		wait_list,tbl_5_19
	bucket_entry_a		write_constant,tbl_5_20
	bucket_entry_a		write_marked_value,tbl_5_21
	bucket_entry_a		write_marked_variable,tbl_5_22
	bucket_entry_a		write_value,tbl_5_23
	bucket_entry_a		write_variable,tbl_5_24
tbl_5_8:
	read_element		5,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,/
	read_elements_inc		9,1,7,2
	collect_value		7
	collect_vector		9
	get_value		3,4
	put_reused_func		3,5,create_goal
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_9:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_device_dup_check
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_10:
	read_element		5,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,/
	read_elements_inc		9,1,7,2
	collect_vector		5
	get_value		3,4
	put_reused_func		3,9,/
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	put_func		4,3,enqueue_goal
	write_element_value		4,1,8
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
tbl_5_11:
	read_element		5,1,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,/
	read_elements_inc		9,1,7,2
	collect_vector		5
	get_value		3,4
	put_reused_func		3,9,/
	write_element_value		3,1,7
	write_element_marked_value		3,2,8
	put_func		4,3,execute
	write_element_value		4,1,8
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
tbl_5_12:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_halt
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_13:
	read_element		5,1,7
	collect_value		3
	put_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,car
	get_vector_value		4,3
	put_reused_func		3,5,put_list
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_14:
	read_element		5,1,7
	integer		7
	test_integer		7,0,tbl_5_26
	collect_vector		5
	execute		4,'$tbl/1_0_4_0'
tbl_5_26:
	put_integer		8,0
	g_less_than		8,7
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_1_5_0'
tbl_5_15:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_request_gc
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_16:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_set_backtrace_switch
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_17:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_set_scheduling_switch
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_18:
	read_element		5,1,7
	get_value		3,4
	put_reused_func		3,5,g_set_trace_switch
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_19:
	read_element		5,1,7
	collect_value		3
	put_func		3,3,list
	write_element_marked_value		3,1,7
	write_element_atom		3,2,car
	get_vector_value		4,3
	put_reused_func		3,5,list
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_20:
	read_element		5,1,7
	wait		7
	switch_on_type		7,tbl_5_27,tbl_5_28,tbl_5_1,tbl_5_1,tbl_5_1,tbl_5_29
tbl_5_27:
	test_nil		7,tbl_5_30
	collect_vector		5
	execute		4,'$tbl/1_4_4_0'
tbl_5_30:
	put_nil		8
	g_diff		7,8
	collect_value		8
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_5_5_0'
tbl_5_28:
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_6_5_0'
tbl_5_29:
	is_float		7,tbl_5_1
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_7_5_0'
tbl_5_21:
	read_element		5,1,7
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_3_5_0'
tbl_5_22:
	read_element		5,1,7
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_10_5_0'
tbl_5_23:
	read_element		5,1,7
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_2_5_0'
tbl_5_24:
	read_element		5,1,7
	integer		7
	test_integer		7,0,tbl_5_32
	collect_vector		5
	execute		4,'$tbl/1_8_4_0'
tbl_5_32:
	put_integer		8,0
	g_less_than		8,7
	collect_vector		5
	put_value		5,7
	execute		5,'$tbl/1_9_5_0'
tbl_5_5:
	read_element		5,0,6
	atom		6
	hash_on_atom		6,58,tbl_5_1
	bucket_entry_a		abs,tbl_5_34
	bucket_entry_a		complement,tbl_5_35
	bucket_entry_a		create_ext,tbl_5_36
	bucket_entry_a		create_to_node,tbl_5_37
	bucket_entry_a		create_to_processor,tbl_5_38
	bucket_entry_a		create_with_priority,tbl_5_39
	bucket_entry_a		decrement,tbl_5_40
	bucket_entry_a		diff,tbl_5_41
	bucket_entry_a		enqueue_ext,tbl_5_42
	bucket_entry_a		enqueue_to_node,tbl_5_43
	bucket_entry_a		enqueue_to_processor,tbl_5_44
	bucket_entry_a		enqueue_with_priority,tbl_5_45
	bucket_entry_a		equal,tbl_5_46
	bucket_entry_a		execute_ext,tbl_5_47
	bucket_entry_a		floating_point_abs,tbl_5_48
	bucket_entry_a		floating_point_acos,tbl_5_49
	bucket_entry_a		floating_point_asin,tbl_5_50
	bucket_entry_a		floating_point_atan,tbl_5_51
	bucket_entry_a		floating_point_cos,tbl_5_52
	bucket_entry_a		floating_point_cosh,tbl_5_53
	bucket_entry_a		floating_point_equal,tbl_5_54
	bucket_entry_a		floating_point_exp,tbl_5_55
	bucket_entry_a		floating_point_floor,tbl_5_56
	bucket_entry_a		floating_point_less_than,tbl_5_57
	bucket_entry_a		floating_point_ln,tbl_5_58
	bucket_entry_a		floating_point_log,tbl_5_59
	bucket_entry_a		floating_point_minus,tbl_5_60
	bucket_entry_a		floating_point_not_equal,tbl_5_61
	bucket_entry_a		floating_point_not_less_than,tbl_5_62
	bucket_entry_a		floating_point_sin,tbl_5_63
	bucket_entry_a		floating_point_sinh,tbl_5_64
	bucket_entry_a		floating_point_sqrt,tbl_5_65
	bucket_entry_a		floating_point_tan,tbl_5_66
	bucket_entry_a		floating_point_tanh,tbl_5_67
	bucket_entry_a		floating_point_to_integer,tbl_5_68
	bucket_entry_a		get_constant,tbl_5_69
	bucket_entry_a		get_list_value,tbl_5_70
	bucket_entry_a		get_vector_value,tbl_5_71
	bucket_entry_a		increment,tbl_5_72
	bucket_entry_a		integer_to_floating_point,tbl_5_73
	bucket_entry_a		less_than,tbl_5_74
	bucket_entry_a		minus,tbl_5_75
	bucket_entry_a		not_equal,tbl_5_76
	bucket_entry_a		not_less_than,tbl_5_77
	bucket_entry_a		put_constant,tbl_5_78
	bucket_entry_a		put_marked_value,tbl_5_79
	bucket_entry_a		put_structured_constant,tbl_5_80
	bucket_entry_a		put_value,tbl_5_81
	bucket_entry_a		put_variable,tbl_5_82
	bucket_entry_a		put_vector,tbl_5_83
	bucket_entry_a		set_constant,tbl_5_84
	bucket_entry_a		set_marked_value,tbl_5_85
	bucket_entry_a		set_marked_variable,tbl_5_86
	bucket_entry_a		set_value,tbl_5_87
	bucket_entry_a		set_variable,tbl_5_88
	bucket_entry_a		vector,tbl_5_89
	bucket_entry_a		wait_constant,tbl_5_90
	bucket_entry_a		wait_vector,tbl_5_91
tbl_5_34:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_abs
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_92:
	get_value		3,4
	put_reused_func		3,5,g_abs
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_35:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_complement
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_36:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	collect_value		8
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,2,create_goal
	write_element_value		3,1,9
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_37:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	collect_value		8
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,2,create_goal
	write_element_value		3,1,9
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_38:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	collect_value		8
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,2,create_goal
	write_element_value		3,1,9
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_39:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	collect_value		8
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,2,create_goal
	write_element_value		3,1,9
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_40:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_decrement
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_41:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_diff
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_42:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,4,enqueue_goal_external
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_43:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	get_value		3,4
	put_reused_func		3,5,/
	write_element_value		3,1,8
	write_element_marked_value		3,2,9
	put_reused_func		4,10,enqueue_goal
	write_element_value		4,1,9
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
tbl_5_44:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_value		7
	get_value		3,4
	put_reused_func		3,5,/
	write_element_value		3,1,8
	write_element_marked_value		3,2,9
	put_reused_func		4,10,enqueue_goal
	write_element_value		4,1,9
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
tbl_5_45:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_vector		10
	get_value		3,4
	put_reused_func		3,5,/
	write_element_value		3,1,8
	write_element_marked_value		3,2,9
	put_func		4,4,enqueue_goal_with_priority
	write_element_value		4,1,9
	write_element_value		4,2,3
	write_element_value		4,3,7
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
tbl_5_46:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_equal
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_47:
	read_element		5,1,10
	read_element		5,2,7
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,/
	read_elements_inc		10,1,8,2
	collect_vector		5
	collect_vector		10
	get_value		3,4
	put_func		3,4,execute_external
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_48:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_abs
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_49:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_acos
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_50:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_asin
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_51:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_atan
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_52:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_cos
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_53:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_cosh
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_54:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_equal
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_55:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_exp
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_56:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_floor
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_57:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_less_than
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_58:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_ln
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_59:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_log
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_60:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_minus
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_61:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_not_equal
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_62:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_not_less_than
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_63:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_sin
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_64:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_sinh
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_65:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_sqrt
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_66:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_tan
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_67:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_tanh
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_68:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_float_to_integer
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_69:
	read_element		5,1,7
	wait		7
	switch_on_type		7,tbl_5_93,tbl_5_94,tbl_5_1,tbl_5_1,tbl_5_1,tbl_5_95
tbl_5_93:
	test_nil		7,tbl_5_96
	read_element		5,2,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,get_nil
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_96:
	read_element		5,2,8
	put_nil		9
	g_diff		7,9
	collect_value		9
	get_value		3,4
	put_reused_func		3,5,get_atom
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_94:
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,get_integer
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_95:
	is_float		7,tbl_5_1
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,get_float
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_70:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,get_list_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_71:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,get_vector_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_72:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_increment
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_73:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_integer_to_float
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_74:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_less_than
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_75:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_minus
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_76:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_not_equal
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_77:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_not_less_than
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_78:
	read_element		5,1,7
	try_me_else		tbl_5_97
	wait		7
	switch_on_type		7,tbl_5_98,tbl_5_99,tbl_5_97,tbl_5_97,tbl_5_97,tbl_5_100
tbl_5_98:
	test_nil		7,tbl_5_101
	try_me_else		tbl_5_101
	read_element		5,2,8
	integer		8
	put_integer		9,0
	g_less_than		9,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,put_nil
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_101:
	try_me_else		tbl_5_97
	read_element		5,2,8
	integer		8
	put_integer		9,0
	g_less_than		9,8
	put_nil		9
	g_diff		7,9
	collect_value		9
	get_value		3,4
	put_reused_func		3,5,put_atom
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_99:
	read_element		5,2,8
	integer		8
	put_integer		9,0
	g_less_than		9,8
	get_value		3,4
	put_reused_func		3,5,put_integer
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_100:
	is_float		7,tbl_5_97
	read_element		5,2,8
	integer		8
	put_integer		9,0
	g_less_than		9,8
	get_value		3,4
	put_reused_func		3,5,put_float
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_97:
	read_element		5,2,8
	try_me_else		tbl_5_1
	wait_integer		8,0
	collect_value		7
	collect_vector		5
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_79:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,put_marked_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_80:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,put_structured_constant
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_81:
	read_element		5,1,7
	try_me_else		tbl_5_103
	integer		7
	test_integer		7,0,tbl_5_105
	read_element		5,2,8
	collect_value		8
	collect_vector		5
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_105:
	read_element		5,2,8
	put_integer		9,0
	g_less_than		9,7
	integer		8
	put_integer		9,0
	g_less_than		9,8
	get_value		3,4
	put_reused_func		3,5,put_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_103:
	read_element		5,2,8
	try_me_else		tbl_5_1
	wait_integer		8,0
	collect_value		7
	collect_vector		5
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_82:
	read_element		5,1,7
	integer		7
	test_integer		7,0,tbl_5_108
	read_element		5,2,8
	try_me_else		tbl_5_108
	integer		8
	test_integer		8,0,tbl_5_110
	collect_vector		5
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_110:
	put_integer		9,0
	g_less_than		9,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,put_void
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_108:
	try_me_else		tbl_5_1
	read_element		5,2,8
	wait_integer		8,0
	put_integer		8,0
	g_less_than		8,7
	collect_vector		5
	get_value		3,4
	put_func		3,2,put_void
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_83:
	read_elements_inc		5,1,7,2
	collect_value		3
	put_reused_func		3,5,vector
	write_element_marked_value		3,1,7
	write_element_integer		3,2,0
	get_vector_value		4,3
	put_func		3,3,put_vector
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_84:
	read_element		5,1,7
	wait		7
	switch_on_type		7,tbl_5_111,tbl_5_112,tbl_5_1,tbl_5_1,tbl_5_1,tbl_5_113
tbl_5_111:
	test_nil		7,tbl_5_114
	read_element		5,2,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,set_nil
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_114:
	read_element		5,2,8
	put_nil		9
	g_diff		7,9
	collect_value		9
	get_value		3,4
	put_reused_func		3,5,set_atom
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_112:
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,set_integer
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_113:
	is_float		7,tbl_5_1
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,set_float
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_85:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,set_marked_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_86:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,set_marked_variable
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_87:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,set_value
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_88:
	read_element		5,1,7
	try_me_else		tbl_5_115
	integer		7
	test_integer		7,0,tbl_5_117
	read_element		5,2,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,set_void
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_117:
	read_element		5,2,8
	put_integer		9,0
	g_less_than		9,7
	integer		8
	put_integer		9,0
	g_less_than		9,8
	get_value		3,4
	put_reused_func		3,5,set_variable
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_115:
	read_element		5,2,8
	try_me_else		tbl_5_1
	wait_integer		8,0
	collect_vector		5
	get_value		3,4
	put_func		3,2,put_void
	write_element_value		3,1,7
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_89:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,g_vector
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_90:
	read_element		5,1,7
	wait		7
	switch_on_type		7,tbl_5_119,tbl_5_120,tbl_5_1,tbl_5_1,tbl_5_1,tbl_5_121
tbl_5_119:
	test_nil		7,tbl_5_122
	read_element		5,2,8
	collect_vector		5
	get_value		3,4
	put_func		3,2,wait_nil
	write_element_value		3,1,8
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_122:
	read_element		5,2,8
	put_nil		9
	g_diff		7,9
	collect_value		9
	get_value		3,4
	put_reused_func		3,5,wait_atom
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_120:
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,wait_integer
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_121:
	is_float		7,tbl_5_1
	read_element		5,2,8
	get_value		3,4
	put_reused_func		3,5,wait_float
	write_elements_dec		3,1,8,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_91:
	read_elements_inc		5,1,7,2
	collect_value		3
	put_reused_func		3,5,vector
	write_element_marked_value		3,1,7
	write_element_integer		3,2,0
	get_vector_value		4,3
	put_func		3,3,wait_vector
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_6:
	read_element		5,0,6
	atom		6
	hash_on_atom		6,29,tbl_5_1
	bucket_entry_a		add,tbl_5_124
	bucket_entry_a		and,tbl_5_125
	bucket_entry_a		create_ext_with_priority,tbl_5_126
	bucket_entry_a		divide,tbl_5_127
	bucket_entry_a		exclusive_or,tbl_5_128
	bucket_entry_a		floating_point_add,tbl_5_129
	bucket_entry_a		floating_point_atan,tbl_5_130
	bucket_entry_a		floating_point_divide,tbl_5_131
	bucket_entry_a		floating_point_max,tbl_5_132
	bucket_entry_a		floating_point_min,tbl_5_133
	bucket_entry_a		floating_point_multiply,tbl_5_134
	bucket_entry_a		floating_point_pow,tbl_5_135
	bucket_entry_a		floating_point_subtract,tbl_5_136
	bucket_entry_a		mark_element,tbl_5_137
	bucket_entry_a		max,tbl_5_138
	bucket_entry_a		min,tbl_5_139
	bucket_entry_a		modulo,tbl_5_140
	bucket_entry_a		multiply,tbl_5_141
	bucket_entry_a		or,tbl_5_142
	bucket_entry_a		register_tag_and_value,tbl_5_143
	bucket_entry_a		set_tag_and_value,tbl_5_144
	bucket_entry_a		shift_left,tbl_5_145
	bucket_entry_a		shift_right,tbl_5_146
	bucket_entry_a		string,tbl_5_147
	bucket_entry_a		string_element,tbl_5_148
	bucket_entry_a		subtract,tbl_5_149
	bucket_entry_a		tag_and_value,tbl_5_150
	bucket_entry_a		vector_element,tbl_5_151
	bucket_entry_a		word,tbl_5_152
tbl_5_124:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_add
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_125:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_and
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_126:
	read_element		5,1,11
	read_elements_inc		5,2,7,2
	wait_vector		11,3
	read_element		11,0,9
	wait_atom		9,/
	read_elements_inc		11,1,9,2
	collect_value		8
	collect_value		7
	collect_value		10
	collect_value		9
	collect_vector		5
	collect_vector		11
	get_value		3,4
	get_value		1,2
	proceed
tbl_5_127:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_divide
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_128:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_exclusive_or
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_129:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_add
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_130:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_atan2
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_131:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_divide
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_132:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_max
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_133:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_min
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_134:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_multiply
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_135:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_pow
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_136:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_float_subtract
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_137:
	read_elements_inc		5,1,7,3
	collect_vector		5
	get_value		3,4
	put_func		3,3,put_marked_value
	write_element_marked_value		3,1,9
	write_element_value		3,2,9
	put_list_val_val		4,3,2
	put_func		2,3,mark_element
	write_elements_inc		2,1,7,2
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
tbl_5_138:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_max
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_153:
	get_value		3,4
	put_reused_func		3,5,g_max
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_139:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_min
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_154:
	get_value		3,4
	put_reused_func		3,5,g_min
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_140:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_modulo
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_141:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_multiply
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_142:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_or
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_143:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_register_tag_and_value
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_144:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_set_tag_and_value
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_145:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_shift_left
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_146:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_shift_right
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_147:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_string
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_148:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_string_element
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_149:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_subtract
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_150:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_tag_and_value
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_151:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_vector_element
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_152:
	read_elements_inc		5,1,7,3
	get_value		3,4
	put_reused_func		3,5,g_word
	write_elements_inc		3,1,7,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
tbl_5_1:
	otherwise		tbl_5_0
	get_value		3,4
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
tbl_5_210:
	suspend		tbl_5_0
	module_entry		kl1cmp_output
	predicate		set_vector_element,4
set_vector_element_4_0:
	b_set_vector_element		1,3,1,4,3
	get_value		3,2
	proceed
set_vector_element_4_1:
	suspend		set_vector_element_4_0
	module_entry		kl1cmp_output
	predicate		ref_vector_element,4
ref_vector_element_4_0:
	put_marked_value		5,4
	b_set_vector_element		1,3,1,5,3
	get_value		1,4
	get_value		3,2
	proceed
ref_vector_element_4_1:
	suspend		ref_vector_element_4_0
	module_entry		kl1cmp_output
	predicate		output_const_code,3
output_const_code_3_0:
	put_func		4,2,flush
	write_element_void		4,1
	put_list_val_var		5,4,4
	put_list		6
	write_car_atom		6,nl
	write_cdr_value		6,5
	get_list_value		1,6
	put_value		1,4
	execute		3,output_const_code__3_0
output_const_code_3_1:
	suspend		output_const_code_3_0
	module_entry		kl1cmp_output
	predicate		output_const_code_,3
output_const_code__3_0:
	try_me_else		output_const_code__3_1
	wait_list_var_var		3,8,4
	wait_vector		8,2
	read_element		8,0,5
	wait_atom		5,'$SCNST'
	read_element		8,1,5
	string		5
	g_string		5,6,7
	collect_vector		8
	put_structured_constant		7,'$SCNST_47'
	get_reused_list_val_var		1,3,3,7,8
	put_list		1
	write_car_atom		1,nl
	write_cdr_variable		1,9
	put_structured_constant		3,'$SCNST_48'
	put_list_val_val		7,3,1
	put_structured_constant		1,'$SCNST_49'
	put_list_val_val		3,1,7
	create_goal		3
	set_value		1,9
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,output_const_code__3_0
	put_value		1,8
	put_value		2,3
	put_integer		3,0
	put_value		4,6
	execute		5,write_string_5_0
output_const_code__3_1:
	otherwise		output_const_code__3_0
	try_me_else		output_const_code__3_5
	jump_on_non_list_var_var		3,output_const_code__3_7,4,5
	vector		4
	g_vector		4,6
	put_integer		7,0
	put_nil		8
	b_set_vector_element		4,7,4,8,7
	put_structured_constant		8,'$SCNST_50'
	put_reused_list_val_var		3,3,8,9
	put_func		8,2,putt
	write_element_value		8,1,4
	put_list_val_val		4,8,3
	put_structured_constant		3,'$SCNST_51'
	put_list_val_val		8,3,4
	get_list_value		1,8
	b_decrement		6,1
	put_value		4,1
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	enqueue_goal		3,output_const_code__3_0
	put_value		1,9
	put_value		2,3
	put_integer		3,1
	put_value		5,7
	execute		5,output_const_arg_5_0
output_const_code__3_7:
	check_nil		3,output_const_code__3_5
	get_value		1,2
	proceed
output_const_code__3_5:
	suspend		output_const_code__3_0
	module_entry		kl1cmp_output
	predicate		write_string,5
write_string_5_0:
	try_me_else		write_string_5_1
	integer		3
	integer		4
	g_less_than		3,4
	string		5
	g_string_element		5,3,6
	put_func		7,2,putc
	write_element_value		7,1,6
	get_list_val_var		1,8,7,6
	b_increment		3,3
	put_value		1,6
	execute		5,write_string_5_0
write_string_5_1:
	try_me_else		write_string_5_3
	wait_value		3,4
	collect_value		5
	collect_value		3
	collect_value		4
	get_value		1,2
	proceed
write_string_5_3:
	suspend		write_string_5_0
	module_entry		kl1cmp_output
	predicate		output_const_arg,5
output_const_arg_5_0:
	try_me_else		output_const_arg_5_1
	integer		3
	integer		4
	g_less_than		3,4
	put_marked_value		6,3
	put_nil		7
	b_set_vector_element		5,6,5,7,6
	put_structured_constant		7,'$SCNST_52'
	put_list_val_var		8,7,7
	b_increment		3,3
	create_goal		5
	set_value		1,7
	set_values_inc		2,2,3
	set_value		5,6
	enqueue_goal		5,output_const_arg_5_0
	put_value		2,8
	put_value		3,5
	execute		3,output_one_arg_3_0
output_const_arg_5_1:
	try_me_else		output_const_arg_5_3
	wait_value		3,4
	collect_value		4
	put_nil		4
	b_set_vector_element		5,3,3,4,4
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,2
	put_value		2,4
	execute		3,output_one_arg_3_0
output_const_arg_5_3:
	suspend		output_const_arg_5_0
	module_entry		kl1cmp_output
	predicate		output_one_arg,3
output_one_arg_3_0:
	try_me_else		output_one_arg_3_1
	wait_vector		3,2
	read_element		3,0,4
	wait_atom		4,'$SCNST'
	read_element		3,1,5
	string		5
	g_string		5,4,6
	collect_vector		3
	put_structured_constant		3,'$SCNST_53'
	get_list_val_var		1,7,3,6
	put_structured_constant		1,'$SCNST_54'
	put_list_val_val		3,1,2
	put_value		1,6
	put_value		2,3
	put_integer		3,0
	execute		5,write_string_5_0
output_one_arg_3_1:
	otherwise		output_one_arg_3_0
	put_func		4,2,puttq
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
output_one_arg_3_6:
	suspend		output_one_arg_3_0
	module_entry		kl1cmp_output
	predicate		'$optimize/1_11',5
'$optimize/1_11_5_0':
	try_me_else		'$optimize/1_11_5_1'
	wait_list_var_var		5,8,6
	wait_vector		8,3
	read_element		8,0,7
	wait_atom		7,get_list_value
	read_element		8,1,7
	read_element		8,2,9
	wait_value		9,2
	collect_value		9
	collect_vector		8
	put_func		8,5,get_list_val_var
	write_element_value		8,1,7
	write_elements_inc		8,2,2,3
	get_reused_list_val_var		1,3,5,8,2
	put_value		1,2
	put_value		2,6
	execute		2,optimize_2_0
'$optimize/1_11_5_1':
	otherwise		'$optimize/1_11_5_0'
	put_func		6,4,put_list_val_var
	write_elements_inc		6,1,2,3
	get_list_val_var		1,3,6,2
	put_value		1,2
	put_value		2,5
	execute		2,optimize_2_0
'$optimize/1_11_5_5':
	suspend		'$optimize/1_11_5_0'
	module_entry		kl1cmp_output
	predicate		optimize,2
optimize_2_0:
	try_me_else		optimize_2_1
	jump_on_non_list		2,optimize_2_3
	read_car		2,3
	vector		3
	jump_on_arity		3,6,optimize_2_1
	table_entry		optimize_2_1
	table_entry		optimize_2_1
	table_entry		optimize_2_5
	table_entry		optimize_2_6
	table_entry		optimize_2_7
	table_entry		optimize_2_8
optimize_2_5:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,optimize_2_1
	bucket_entry_a		list,optimize_2_10
	bucket_entry_a		put_list,optimize_2_11
optimize_2_10:
	read_cdr		2,9
	wait_list_var_var		9,10,11
	wait_list_var_var		11,12,5
	wait_vector		12,3
	read_element		12,0,6
	wait_atom		6,read_cdr
	read_elements_inc		12,1,6,2
	wait_vector		10,3
	read_element		10,0,8
	wait_atom		8,read_car
	read_element		10,1,13
	wait_value		13,6
	read_element		10,2,8
	read_element		3,1,14
	wait_value		14,6
	collect_list		9
	collect_list		11
	collect_value		13
	collect_value		14
	collect_vector		10
	collect_vector		12
	collect_vector		3
	put_func		3,4,wait_list_var_var
	write_element_value		3,1,6
	write_elements_dec		3,2,8,2
	get_reused_list_val_var		1,4,2,3,2
	put_value		1,2
	put_value		2,5
	execute		2,optimize_2_0
optimize_2_11:
	read_element		3,1,5
	read_cdr		2,6
	list		6
	read_car		6,7
	wait_vector		7,3
	read_element		7,0,8
	wait_atom		8,write_car_value
	read_elements_inc		7,1,9,2
	read_cdr		6,11
	list		11
	read_car		11,12
	wait_vector		12,3
	read_element		12,0,13
	atom		13
	branch_on_atom		13,2,optimize_2_1
	bucket_entry_a		write_cdr_value,optimize_2_18
	bucket_entry_a		write_cdr_variable,optimize_2_19
optimize_2_18:
	wait_value		5,9
	read_cdr		11,14
	read_element		12,1,15
	wait_value		15,5
	read_element		12,2,4
	collect_list		6
	collect_list		11
	collect_value		15
	collect_vector		3
	collect_vector		7
	collect_vector		12
	put_func		3,4,put_list_val_val
	write_element_value		3,1,5
	write_element_value		3,2,10
	write_element_value		3,3,4
	get_reused_list_val_var		1,4,2,3,2
	put_value		1,2
	put_value		2,14
	execute		2,optimize_2_0
optimize_2_19:
	wait_value		5,9
	read_cdr		11,14
	read_element		12,1,15
	wait_value		15,5
	read_element		12,2,4
	collect_list		2
	collect_list		6
	collect_list		11
	collect_value		15
	collect_vector		3
	collect_vector		7
	collect_vector		12
	put_value		2,5
	put_value		3,10
	put_value		5,14
	execute		5,'$optimize/1_11_5_0'
optimize_2_6:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,3,optimize_2_1
	bucket_entry_a		put_value,optimize_2_21
	bucket_entry_a		put_vector,optimize_2_22
	bucket_entry_a		set_value,optimize_2_23
optimize_2_21:
	read_element		3,1,5
	integer		5
	read_element		3,2,6
	integer		6
	read_cdr		2,7
	list		7
	read_car		7,8
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,put_value
	read_element		8,1,10
	integer		10
	read_element		8,2,11
	integer		11
	read_cdr		7,12
	g_increment		5,13
	g_equal		10,13
	try_me_else		optimize_2_31
	g_increment		6,14
	wait_value		14,11
	collect_list		7
	collect_vector		3
	collect_vector		8
	put_func		3,4,put_values_inc
	write_elements_inc		3,1,5,2
	write_element_integer		3,3,2
	put_reused_list_val_val		2,2,3,12
	execute		2,optimize_2_0
optimize_2_31:
	try_me_else		optimize_2_1
	g_decrement		6,14
	wait_value		14,11
	collect_list		7
	collect_vector		3
	collect_vector		8
	put_func		3,4,put_values_dec
	write_elements_inc		3,1,5,2
	write_element_integer		3,3,2
	put_reused_list_val_val		2,2,3,12
	execute		2,optimize_2_0
optimize_2_22:
	read_cdr		2,9
	wait_list_var_var		9,10,5
	wait_vector		10,4
	read_element		10,0,6
	wait_atom		6,write_element_atom
	read_elements_inc		10,1,6,2
	wait_integer		7,0
	read_element		10,3,7
	read_element		3,1,11
	wait_value		11,6
	read_element		3,2,8
	collect_list		9
	collect_value		11
	collect_vector		3
	put_reused_func		3,10,put_func
	write_element_value		3,1,6
	write_elements_dec		3,2,8,2
	get_reused_list_val_var		1,4,2,3,2
	put_value		1,2
	put_value		2,5
	execute		2,optimize_2_0
optimize_2_23:
	read_element		3,1,5
	integer		5
	read_element		3,2,6
	integer		6
	read_cdr		2,7
	list		7
	read_car		7,8
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,set_value
	read_element		8,1,10
	integer		10
	read_element		8,2,11
	integer		11
	read_cdr		7,12
	g_increment		5,13
	g_equal		10,13
	try_me_else		optimize_2_39
	g_increment		6,14
	wait_value		14,11
	collect_list		7
	collect_vector		3
	collect_vector		8
	put_func		3,4,set_values_inc
	write_elements_inc		3,1,5,2
	write_element_integer		3,3,2
	put_reused_list_val_val		2,2,3,12
	execute		2,optimize_2_0
optimize_2_39:
	try_me_else		optimize_2_1
	g_decrement		6,14
	wait_value		14,11
	collect_list		7
	collect_vector		3
	collect_vector		8
	put_func		3,4,set_values_dec
	write_elements_inc		3,1,5,2
	write_element_integer		3,3,2
	put_reused_list_val_val		2,2,3,12
	execute		2,optimize_2_0
optimize_2_7:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,6,optimize_2_1
	bucket_entry_a		put_values_dec,optimize_2_41
	bucket_entry_a		put_values_inc,optimize_2_42
	bucket_entry_a		read_element,optimize_2_43
	bucket_entry_a		set_values_dec,optimize_2_44
	bucket_entry_a		set_values_inc,optimize_2_45
	bucket_entry_a		write_element_value,optimize_2_46
optimize_2_41:
	read_cdr		2,12
	wait_list_var_var		12,13,5
	wait_vector		13,3
	read_element		13,0,6
	wait_atom		6,put_value
	read_elements_inc		13,1,6,2
	read_elements_inc		3,1,8,3
	integer		8
	integer		10
	g_add		8,10,11
	integer		6
	g_equal		6,11
	integer		9
	g_subtract		9,10,6
	wait_value		6,7
	collect_list		12
	collect_value		7
	collect_value		6
	collect_vector		13
	b_increment		10,4
	put_reused_func		3,3,put_values_dec
	write_elements_inc		3,1,8,2
	write_element_value		3,3,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_42:
	read_cdr		2,12
	wait_list_var_var		12,13,5
	wait_vector		13,3
	read_element		13,0,6
	wait_atom		6,put_value
	read_elements_inc		13,1,6,2
	read_elements_inc		3,1,8,3
	integer		8
	integer		10
	g_add		8,10,11
	integer		6
	g_equal		6,11
	integer		9
	g_add		9,10,6
	wait_value		6,7
	collect_list		12
	collect_value		7
	collect_value		6
	collect_vector		13
	b_increment		10,4
	put_reused_func		3,3,put_values_inc
	write_elements_inc		3,1,8,2
	write_element_value		3,3,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_43:
	read_elements_inc		3,1,5,2
	integer		6
	read_element		3,3,7
	integer		7
	read_cdr		2,8
	list		8
	read_car		8,9
	wait_vector		9,4
	read_element		9,0,10
	wait_atom		10,read_element
	read_elements_inc		9,1,11,2
	integer		12
	read_element		9,3,13
	integer		13
	read_cdr		8,14
	g_increment		6,15
	g_equal		12,15
	try_me_else		optimize_2_54
	wait_value		5,11
	g_increment		7,16
	wait_value		16,13
	collect_list		8
	collect_vector		3
	collect_vector		9
	put_func		3,5,read_elements_inc
	write_elements_inc		3,1,5,3
	write_element_integer		3,4,2
	put_reused_list_val_val		2,2,3,14
	execute		2,optimize_2_0
optimize_2_54:
	try_me_else		optimize_2_1
	wait_value		5,11
	g_decrement		7,16
	wait_value		16,13
	collect_list		8
	collect_vector		3
	collect_vector		9
	put_func		3,5,read_elements_dec
	write_elements_inc		3,1,5,3
	write_element_integer		3,4,2
	put_reused_list_val_val		2,2,3,14
	execute		2,optimize_2_0
optimize_2_44:
	read_cdr		2,12
	wait_list_var_var		12,13,5
	wait_vector		13,3
	read_element		13,0,6
	wait_atom		6,set_value
	read_elements_inc		13,1,6,2
	read_elements_inc		3,1,8,3
	integer		8
	integer		10
	g_add		8,10,11
	integer		6
	g_equal		6,11
	integer		9
	g_subtract		9,10,6
	wait_value		6,7
	collect_list		12
	collect_value		7
	collect_value		6
	collect_vector		13
	b_increment		10,4
	put_reused_func		3,3,set_values_dec
	write_elements_inc		3,1,8,2
	write_element_value		3,3,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_45:
	read_cdr		2,12
	wait_list_var_var		12,13,5
	wait_vector		13,3
	read_element		13,0,6
	wait_atom		6,set_value
	read_elements_inc		13,1,6,2
	read_elements_inc		3,1,8,3
	integer		8
	integer		10
	g_add		8,10,11
	integer		6
	g_equal		6,11
	integer		9
	g_add		9,10,6
	wait_value		6,7
	collect_list		12
	collect_value		7
	collect_value		6
	collect_vector		13
	b_increment		10,4
	put_reused_func		3,3,set_values_inc
	write_elements_inc		3,1,8,2
	write_element_value		3,3,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_46:
	read_elements_inc		3,1,5,2
	integer		6
	read_element		3,3,7
	integer		7
	read_cdr		2,8
	list		8
	read_car		8,9
	wait_vector		9,4
	read_element		9,0,10
	wait_atom		10,write_element_value
	read_elements_inc		9,1,11,2
	integer		12
	read_element		9,3,13
	integer		13
	read_cdr		8,14
	g_increment		6,15
	g_equal		12,15
	try_me_else		optimize_2_62
	wait_value		5,11
	g_increment		7,16
	wait_value		16,13
	collect_list		8
	collect_vector		3
	collect_vector		9
	put_func		3,5,write_elements_inc
	write_elements_inc		3,1,5,3
	write_element_integer		3,4,2
	put_reused_list_val_val		2,2,3,14
	execute		2,optimize_2_0
optimize_2_62:
	try_me_else		optimize_2_1
	wait_value		5,11
	g_decrement		7,16
	wait_value		16,13
	collect_list		8
	collect_vector		3
	collect_vector		9
	put_func		3,5,write_elements_dec
	write_elements_inc		3,1,5,3
	write_element_integer		3,4,2
	put_reused_list_val_val		2,2,3,14
	execute		2,optimize_2_0
optimize_2_8:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,4,optimize_2_1
	bucket_entry_a		read_elements_dec,optimize_2_64
	bucket_entry_a		read_elements_inc,optimize_2_65
	bucket_entry_a		write_elements_dec,optimize_2_66
	bucket_entry_a		write_elements_inc,optimize_2_67
optimize_2_64:
	read_cdr		2,13
	wait_list_var_var		13,14,5
	wait_vector		14,4
	read_element		14,0,6
	wait_atom		6,read_element
	read_elements_inc		14,1,6,3
	read_element		3,1,15
	wait_value		15,6
	read_elements_inc		3,2,9,3
	integer		9
	integer		11
	g_add		9,11,12
	integer		7
	g_equal		7,12
	integer		10
	g_subtract		10,11,7
	wait_value		7,8
	collect_list		13
	collect_value		8
	collect_value		15
	collect_value		7
	collect_vector		14
	b_increment		11,4
	put_reused_func		3,3,read_elements_dec
	write_element_value		3,1,6
	write_elements_inc		3,2,9,2
	write_element_value		3,4,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_65:
	read_cdr		2,13
	wait_list_var_var		13,14,5
	wait_vector		14,4
	read_element		14,0,6
	wait_atom		6,read_element
	read_elements_inc		14,1,6,3
	read_element		3,1,15
	wait_value		15,6
	read_elements_inc		3,2,9,3
	integer		9
	integer		11
	g_add		9,11,12
	integer		7
	g_equal		7,12
	integer		10
	g_add		10,11,7
	wait_value		7,8
	collect_list		13
	collect_value		8
	collect_value		15
	collect_value		7
	collect_vector		14
	b_increment		11,4
	put_reused_func		3,3,read_elements_inc
	write_element_value		3,1,6
	write_elements_inc		3,2,9,2
	write_element_value		3,4,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_66:
	read_cdr		2,13
	wait_list_var_var		13,14,5
	wait_vector		14,4
	read_element		14,0,6
	wait_atom		6,write_element_value
	read_elements_inc		14,1,6,3
	read_element		3,1,15
	wait_value		15,6
	read_elements_inc		3,2,9,3
	integer		9
	integer		11
	g_add		9,11,12
	integer		7
	g_equal		7,12
	integer		10
	g_subtract		10,11,7
	wait_value		7,8
	collect_list		13
	collect_value		8
	collect_value		15
	collect_value		7
	collect_vector		14
	b_increment		11,4
	put_reused_func		3,3,write_elements_dec
	write_element_value		3,1,6
	write_elements_inc		3,2,9,2
	write_element_value		3,4,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_67:
	read_cdr		2,13
	wait_list_var_var		13,14,5
	wait_vector		14,4
	read_element		14,0,6
	wait_atom		6,write_element_value
	read_elements_inc		14,1,6,3
	read_element		3,1,15
	wait_value		15,6
	read_elements_inc		3,2,9,3
	integer		9
	integer		11
	g_add		9,11,12
	integer		7
	g_equal		7,12
	integer		10
	g_add		10,11,7
	wait_value		7,8
	collect_list		13
	collect_value		8
	collect_value		15
	collect_value		7
	collect_vector		14
	b_increment		11,4
	put_reused_func		3,3,write_elements_inc
	write_element_value		3,1,6
	write_elements_inc		3,2,9,2
	write_element_value		3,4,4
	put_reused_list_val_val		2,2,3,5
	execute		2,optimize_2_0
optimize_2_3:
	check_nil		2,optimize_2_1
	get_nil		1
	proceed
optimize_2_1:
	otherwise		optimize_2_0
	try_me_else		optimize_2_151
	wait_list_var_var		2,3,4
	get_reused_list_val_var		1,5,2,3,2
	put_value		1,2
	put_value		2,4
	execute		2,optimize_2_0
optimize_2_151:
	suspend		optimize_2_0
	begin_const_section		kl1cmp_output
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putc
	define_integer		39
'$SCNST_54':
'$SCNST_53':
'$SCNST_49':
'$SCNST_47':
'$SCNST_3':
'$SCNST_2':
'$SCNST_1':
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_4_0':
	define_desc		27,1
	define_integer		95
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		19,3
	define_integer		858927408
	define_integer		926299444
	define_integer		14648
'$SCNST_6':
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putc
	define_integer		9
'$SCNST_51':
'$SCNST_50':
'$SCNST_46':
'$SCNST_44':
'$SCNST_41':
'$SCNST_39':
'$SCNST_35':
'$SCNST_33':
'$SCNST_32':
'$SCNST_30':
'$SCNST_29':
'$SCNST_28':
'$SCNST_26':
'$SCNST_25':
'$SCNST_23':
'$SCNST_19':
'$SCNST_17':
'$SCNST_15':
'$SCNST_11':
'$SCNST_10':
'$SCNST_9':
'$SCNST_8':
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_12_0':
	define_desc		0,2
	define_atom		putt
	define_atom		','
'$SCNST_52':
'$SCNST_38':
'$SCNST_37':
'$SCNST_22':
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		11,1
	define_integer		2564391
'$SCNST_13_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_13_1'
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_1':
	define_desc		11,1
	define_integer		2587687
'$SCNST_14_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_16_0':
	define_desc		0,2
	define_atom		putt
	define_atom		otherwise
'$SCNST_16':
	define_vector		'$SCNST_16_0'
'$SCNST_18_0':
	define_desc		0,2
	define_atom		putt
	define_atom		read_eagerly
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_20_0':
	define_desc		0,3
	define_atom		list
	define_integer		0
	define_atom		car
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_0':
	define_desc		0,2
	define_atom		putt
	define_atom		:
'$SCNST_48':
'$SCNST_36':
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_24_0':
	define_desc		0,2
	define_atom		putt
	define_atom		predicate
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_27_0':
	define_desc		0,2
	define_atom		putt
	define_atom		module_entry
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_31_0':
	define_desc		0,2
	define_atom		putt
	define_atom		suspend
'$SCNST_31':
	define_vector		'$SCNST_31_0'
'$SCNST_34_1':
	define_desc		19,2
	define_integer		1969516397
	define_integer		25964
'$SCNST_34_0':
	define_desc		0,2
	define_atom		puts
	define_string		'$SCNST_34_1'
'$SCNST_34':
	define_vector		'$SCNST_34_0'
'$SCNST_40_0':
	define_desc		0,2
	define_atom		putt
	define_atom		entry
'$SCNST_40':
	define_vector		'$SCNST_40_0'
'$SCNST_42_0':
	define_desc		3,9
	define_integer		1635151433
	define_integer		543451500
	define_integer		1818391920
	define_integer		1679844201
	define_integer		1634493285
	define_integer		1769234802
	define_integer		539913839
	define_integer		1869506377
	define_integer		778331506
'$SCNST_42':
	define_string		'$SCNST_42_0'
'$SCNST_43_1':
	define_desc		11,6
	define_integer		1830842190
	define_integer		1819632751
	define_integer		1936269413
	define_integer		1701868320
	define_integer		1768319331
	define_integer		3040357
'$SCNST_43_0':
	define_desc		0,3
	define_atom		error_message
	define_string		'$SCNST_43_1'
	define_atom		[]
'$SCNST_43':
	define_vector		'$SCNST_43_0'
'$SCNST_45_0':
	define_desc		0,2
	define_atom		putt
	define_atom		message
'$SCNST_45':
	define_vector		'$SCNST_45_0'
