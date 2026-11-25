kl1cmp_reader:
	module		kl1cmp_reader
	entry		count_variables,3,count_variables_3_0
	entry		create_reader,5,create_reader_5_0
	entry		create_varchk_reader,5,create_varchk_reader_5_0
	entry		functor,3,functor_3_0
	entry		gen_functor,3,gen_functor_3_0
	entry		herrey,3,herrey_3_0
	entry		trans_io_instr,3,trans_io_instr_3_0
	entry		test_reader,0,test_reader_0_0
	entry		convert_integer_to_string,2,convert_integer_to_string_2_0
	entry		convert_integer_to_list,3,convert_integer_to_list_3_0
	entry		convert_list_to_string,3,convert_list_to_string_3_0
	module_entry		kl1cmp_reader
	predicate		test_reader,0
test_reader_0_0:
	b_merge		4,1
	put_vector		5,2
	write_element_variable		5,0,3
	write_element_variable		5,1,2
	get_vector_value		4,5
	create_goal		5
	set_variable		1,6
	set_nil		2
	set_variable		3,5
	set_nil		4
	set_variable		5,4
	enqueue_goal		5,tr_5_0
	create_goal		5
	set_value		1,3
	set_value		2,6
	set_value		3,2
	set_values_dec		4,5,2
	enqueue_goal		5,create_reader_5_0
	create_goal		3
	set_variable		1,3
	put_func		2,2,getl
	write_element_void		2,1
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	set_value		2,4
	set_value		3,1
	enqueue_goal		3,trans_io_instr_3_0
	put_list		1
	write_car_atom		1,clear
	write_cdr_value		1,3
	put_list		2
	write_car_atom		2,show
	write_cdr_value		2,1
	put_value		1,2
	put_structured_constant		2,'$SCNST_0'
	execute_external		window,create,2
test_reader_0_1:
	suspend		test_reader_0_0
	module_entry		kl1cmp_reader
	predicate		trans_io_instr,3
trans_io_instr_3_0:
	try_me_else		trans_io_instr_3_1
	jump_on_non_list		3,trans_io_instr_3_3
	read_car		3,4
	jump_on_non_atom		4,trans_io_instr_3_5
	branch_on_atom		4,3,trans_io_instr_3_1
	bucket_entry_a		nl,trans_io_instr_3_6
	bucket_entry_a		show,trans_io_instr_3_7
	bucket_entry_a		ttynl,trans_io_instr_3_8
trans_io_instr_3_6:
	read_cdr		3,5
	put_reused_list		4,3
	write_car_atom		4,nl
	write_cdr_variable		4,3
	get_list_value		1,4
	put_value		1,3
	put_value		3,5
	execute		3,trans_io_instr_3_0
trans_io_instr_3_7:
	read_cdr		3,5
	put_reused_list		4,3
	write_car_atom		4,show
	write_cdr_variable		4,3
	get_list_value		1,4
	put_value		1,3
	put_value		3,5
	execute		3,trans_io_instr_3_0
trans_io_instr_3_8:
	read_cdr		3,5
	put_reused_list		4,3
	write_car_atom		4,nl
	write_cdr_variable		4,3
	get_list_value		1,4
	put_value		1,3
	put_value		3,5
	execute		3,trans_io_instr_3_0
trans_io_instr_3_5:
	is_vector		4,trans_io_instr_3_1
	jump_on_arity		4,4,trans_io_instr_3_1
	table_entry		trans_io_instr_3_1
	table_entry		trans_io_instr_3_1
	table_entry		trans_io_instr_3_9
	table_entry		trans_io_instr_3_10
trans_io_instr_3_9:
	read_element		4,0,5
	atom		5
	hash_on_atom		5,6,trans_io_instr_3_1
	bucket_entry_a		display,trans_io_instr_3_12
	bucket_entry_a		putc,trans_io_instr_3_13
	bucket_entry_a		puts,trans_io_instr_3_14
	bucket_entry_a		putt,trans_io_instr_3_15
	bucket_entry_a		puttq,trans_io_instr_3_16
	bucket_entry_a		ttyput,trans_io_instr_3_17
trans_io_instr_3_12:
	read_cdr		3,6
	read_element		4,1,7
	put_reused_func		4,4,putt
	write_element_value		4,1,7
	get_reused_list_val_var		1,5,3,4,3
	put_value		1,3
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_13:
	read_cdr		3,6
	read_element		4,1,7
	put_reused_func		4,4,putc
	write_element_value		4,1,7
	get_reused_list_val_var		1,5,3,4,3
	put_value		1,3
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_14:
	read_cdr		3,6
	read_element		4,1,7
	collect_list		3
	collect_vector		4
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,trans_io_instr_3_0
	put_value		2,3
	put_value		3,7
	execute_external		kl1cmp_command,write_string,3
trans_io_instr_3_15:
	read_cdr		3,6
	read_element		4,1,7
	put_reused_func		4,4,putt
	write_element_value		4,1,7
	get_reused_list_val_var		1,5,3,4,3
	put_value		1,3
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_16:
	read_cdr		3,6
	read_element		4,1,7
	put_reused_func		4,4,puttq
	write_element_value		4,1,7
	get_reused_list_val_var		1,5,3,4,3
	put_value		1,3
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_17:
	read_cdr		3,6
	read_element		4,1,7
	put_reused_func		4,4,putc
	write_element_value		4,1,7
	get_reused_list_val_var		1,5,3,4,3
	put_value		1,3
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_10:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,3,trans_io_instr_3_1
	bucket_entry_a		code,trans_io_instr_3_19
	bucket_entry_a		error_message,trans_io_instr_3_20
	bucket_entry_a		warning_message,trans_io_instr_3_21
trans_io_instr_3_19:
	read_cdr		3,6
	read_elements_inc		4,1,7,2
	collect_list		3
	collect_vector		4
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,6
	enqueue_goal		3,trans_io_instr_3_0
	put_value		2,3
	put_values_inc		3,7,2
	execute		4,'C_4_0'
trans_io_instr_3_20:
	read_cdr		3,6
	read_elements_inc		4,1,7,2
	collect_vector		4
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,9
	put_func		4,2,putt
	write_element_value		4,1,8
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_1'
	put_list_val_val		4,3,5
	put_func		3,2,putb
	write_element_value		3,1,7
	put_list_val_val		5,3,4
	get_list_value		1,5
	put_value		1,9
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_21:
	read_cdr		3,6
	read_elements_inc		4,1,7,2
	collect_vector		4
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,9
	put_func		4,2,putt
	write_element_value		4,1,8
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_2'
	put_list_val_val		4,3,5
	put_func		3,2,putb
	write_element_value		3,1,7
	put_list_val_val		5,3,4
	get_list_value		1,5
	put_value		1,9
	put_value		3,6
	execute		3,trans_io_instr_3_0
trans_io_instr_3_3:
	check_nil		3,trans_io_instr_3_1
	get_value		1,2
	proceed
trans_io_instr_3_1:
	otherwise		trans_io_instr_3_0
	try_me_else		trans_io_instr_3_33
	wait_list_var_var		3,4,5
	put_reused_list		3,3
	write_car_atom		3,nl
	write_cdr_variable		3,7
	put_func		6,2,putt
	write_element_value		6,1,4
	put_list_val_val		4,6,3
	put_structured_constant		3,'$SCNST_3'
	put_list_val_val		6,3,4
	get_list_value		1,6
	put_value		1,7
	put_value		3,5
	execute		3,trans_io_instr_3_0
trans_io_instr_3_33:
	suspend		trans_io_instr_3_0
	module_entry		kl1cmp_reader
	predicate		'C',4
'C_4_0':
	get_value		1,3
	get_value		2,4
	proceed
'C_4_1':
	suspend		'C_4_0'
	module_entry		kl1cmp_reader
	predicate		tr,5
tr_5_0:
	put_func		6,3,read_predicate
	write_element_variable		6,1,9
	write_element_variable		6,2,8
	get_list_val_var		5,10,6,7
	put_values_dec		5,9,2
	execute		7,check_end_of_file_7_0
tr_5_1:
	suspend		tr_5_0
	module_entry		kl1cmp_reader
	predicate		check_end_of_file,7
check_end_of_file_7_0:
	try_me_else		check_end_of_file_7_1
	wait_atom		6,end_of_file
	collect_value		5
	get_value		3,4
	get_value		1,2
	get_nil		7
	proceed
check_end_of_file_7_1:
	otherwise		check_end_of_file_7_0
	put_list		8
	write_car_atom		8,nl
	write_cdr_variable		8,10
	put_list		9
	write_car_value		9,6
	write_cdr_nil		9
	put_list_val_val		6,5,9
	put_func		5,2,putt
	write_element_value		5,1,6
	put_list_val_val		6,5,8
	get_list_value		3,6
	put_value		3,10
	put_value		5,7
	execute		5,tr_5_0
check_end_of_file_7_6:
	suspend		check_end_of_file_7_0
	module_entry		kl1cmp_reader
	predicate		name_generator,3
name_generator_3_0:
	try_me_else		name_generator_3_1
	jump_on_non_list_var_var		3,name_generator_3_3,9,4
	wait_vector		9,3
	read_element		9,0,5
	wait_atom		5,new_name
	read_element		9,1,8
	read_element		9,2,5
	wait_vector		8,3
	read_element		8,0,6
	wait_atom		6,/
	read_elements_inc		8,1,6,2
	collect_list		3
	collect_vector		8
	put_variable		3,8
	b_increment		3,3
	create_goal		3
	set_values_dec		1,3,2
	set_value		3,4
	enqueue_goal		3,name_generator_3_0
	put_reused_func		3,9,/
	write_elements_inc		3,1,6,2
	put_value		2,8
	put_value		4,5
	execute		4,make_new_name_4_0
name_generator_3_3:
	check_nil		3,name_generator_3_1
	get_value		1,2
	proceed
name_generator_3_1:
	suspend		name_generator_3_0
	module_entry		kl1cmp_reader
	predicate		make_new_name,4
make_new_name_4_0:
	try_me_else		make_new_name_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,/
	read_elements_inc		3,1,5,2
	collect_vector		3
	put_marked_value		1,1
	get_value		1,2
	b_atom_name		5,2
	put_structured_constant		3,'$SCNST_4'
	b_append_string		3,2,2
	put_structured_constant		3,'$SCNST_5'
	b_append_string		2,3,2
	put_variable		3,5
	b_append_string		2,3,2
	put_structured_constant		3,'$SCNST_6'
	b_append_string		2,3,2
	put_variable		7,3
	b_append_string		2,7,2
	b_intern_atom		2,2
	get_value		2,4
	create_goal		2
	set_value		1,1
	set_value		2,3
	enqueue_goal		2,convert_integer_to_string_2_0
	put_values_dec		1,6,2
	execute		2,convert_integer_to_string_2_0
make_new_name_4_1:
	suspend		make_new_name_4_0
	module_entry		kl1cmp_reader
	predicate		convert_atom_to_list,2
convert_atom_to_list_2_0:
	b_atom_name		1,1
	execute		2,convert_string_to_list_2_0
convert_atom_to_list_2_1:
	suspend		convert_atom_to_list_2_0
	module_entry		kl1cmp_reader
	predicate		convert_integer_to_list,2
convert_integer_to_list_2_0:
	put_value		3,1
	put_value		1,2
	put_nil		2
	execute		3,convert_integer_to_list_3_0
convert_integer_to_list_2_1:
	suspend		convert_integer_to_list_2_0
	module_entry		kl1cmp_reader
	predicate		convert_integer_to_list,3
convert_integer_to_list_3_0:
	try_me_else		convert_integer_to_list_3_1
	integer		3
	try_me_else		convert_integer_to_list_3_3
	put_integer		4,10
	g_less_than		3,4
	put_integer		4,48
	b_add		3,4,3
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
convert_integer_to_list_3_3:
	put_marked_value		4,3
	put_integer		5,10
	b_divide		4,5,4
	put_integer		5,10
	b_modulo		3,5,3
	put_integer		5,48
	b_add		3,5,3
	put_list_val_val		5,3,2
	put_values_dec		2,5,2
	execute		3,convert_integer_to_list_3_0
convert_integer_to_list_3_1:
	suspend		convert_integer_to_list_3_0
	module_entry		kl1cmp_reader
	predicate		convert_string_to_list,2
convert_string_to_list_2_0:
	try_me_else		convert_string_to_list_2_1
	string		1
	put_value		4,1
	g_string		4,3,1
	put_value		1,2
	put_nil		2
	execute		4,convert_one_char_to_list_4_0
convert_string_to_list_2_1:
	suspend		convert_string_to_list_2_0
	module_entry		kl1cmp_reader
	predicate		convert_one_char_to_list,4
convert_one_char_to_list_4_0:
	try_me_else		convert_one_char_to_list_4_1
	integer		3
	test_integer		3,0,convert_one_char_to_list_4_3
	collect_value		4
	get_value		1,2
	proceed
convert_one_char_to_list_4_3:
	put_integer		5,0
	g_less_than		5,3
	g_decrement		3,5
	string		4
	g_string_element		4,5,3
	put_list_val_val		6,3,2
	put_values_dec		2,6,2
	execute		4,convert_one_char_to_list_4_0
convert_one_char_to_list_4_1:
	suspend		convert_one_char_to_list_4_0
	module_entry		kl1cmp_reader
	predicate		convert_list_to_atom,2
convert_list_to_atom_2_0:
	put_value		4,1
	put_variable		1,3
	b_intern_atom		1,1
	get_value		1,2
	put_integer		1,0
	put_value		2,4
	execute		3,convert_list_to_string_3_0
convert_list_to_atom_2_1:
	suspend		convert_list_to_atom_2_0
	module_entry		kl1cmp_reader
	predicate		len_of_list,2
len_of_list_2_0:
	try_me_else		len_of_list_2_1
	jump_on_non_list_var_var		1,len_of_list_2_3,3,4
	collect_list		1
	collect_value		3
	put_variable		1,3
	b_increment		1,1
	get_value		2,1
	put_values_dec		1,4,2
	execute		2,len_of_list_2_0
len_of_list_2_3:
	check_nil		1,len_of_list_2_1
	get_integer		2,0
	proceed
len_of_list_2_1:
	suspend		len_of_list_2_0
	module_entry		kl1cmp_reader
	predicate		convert_list_to_string,3
convert_list_to_string_3_0:
	put_variable		4,5
	put_integer		6,8
	b_new_string		4,4,6
	create_goal		4
	set_value		1,1
	set_marked_value		2,2
	set_values_dec		3,4,2
	enqueue_goal		4,convert_list_to_string_4_0
	put_value		1,2
	put_value		2,5
	execute		2,len_of_list_2_0
convert_list_to_string_3_1:
	suspend		convert_list_to_string_3_0
	module_entry		kl1cmp_reader
	predicate		convert_list_to_string,4
convert_list_to_string_4_0:
	try_me_else		convert_list_to_string_4_1
	jump_on_non_list_var_var		2,convert_list_to_string_4_3,5,6
	collect_list		2
	put_marked_value		2,1
	b_set_string_element		3,2,5,3
	b_increment		1,1
	put_value		2,6
	execute		4,convert_list_to_string_4_0
convert_list_to_string_4_3:
	check_nil		2,convert_list_to_string_4_1
	collect_value		1
	get_value		3,4
	proceed
convert_list_to_string_4_1:
	suspend		convert_list_to_string_4_0
	module_entry		kl1cmp_reader
	predicate		create_reader,5
create_reader_5_0:
	b_merge		7,6
	put_vector		8,2
	write_element_variable		8,0,10
	write_element_variable		8,1,9
	get_vector_value		7,8
	b_merge		7,8
	create_goal		13
	set_variable		1,12
	set_value		2,2
	set_variable		3,11
	set_value		4,4
	set_value		5,9
	set_variable		6,9
	set_void		7
	set_variable		8,4
	set_void		9
	set_atom		10,normal
	set_value		11,5
	set_variable		12,2
	set_value		13,8
	enqueue_goal		13,reader_13_0
	create_goal		12
	set_value		1,1
	set_value		2,12
	set_value		3,3
	set_values_dec		4,11,2
	set_integer		6,0
	set_value		7,9
	set_integer		8,0
	set_value		9,4
	set_atom		10,normal
	set_value		11,7
	set_value		12,2
	enqueue_goal		12,expanded_read_12_0
	put_integer		1,0
	put_void		2
	put_value		3,6
	execute		3,name_generator_3_0
create_reader_5_1:
	suspend		create_reader_5_0
	module_entry		kl1cmp_reader
	predicate		create_varchk_reader,5
create_varchk_reader_5_0:
	b_merge		7,6
	put_vector		8,2
	write_element_variable		8,0,10
	write_element_variable		8,1,9
	get_vector_value		7,8
	b_merge		7,8
	create_goal		13
	set_variable		1,12
	set_value		2,2
	set_variable		3,11
	set_value		4,4
	set_value		5,9
	set_variable		6,9
	set_void		7
	set_variable		8,4
	set_void		9
	set_atom		10,varchk
	set_value		11,5
	set_variable		12,2
	set_value		13,8
	enqueue_goal		13,reader_13_0
	create_goal		12
	set_value		1,1
	set_value		2,12
	set_value		3,3
	set_values_dec		4,11,2
	set_integer		6,0
	set_value		7,9
	set_integer		8,0
	set_value		9,4
	set_atom		10,varchk
	set_value		11,7
	set_value		12,2
	enqueue_goal		12,expanded_read_12_0
	put_integer		1,0
	put_void		2
	put_value		3,6
	execute		3,name_generator_3_0
create_varchk_reader_5_1:
	suspend		create_varchk_reader_5_0
	module_entry		kl1cmp_reader
	predicate		reader,13
reader_13_0:
	try_me_else		reader_13_1
	wait_list_var_var		11,20,14
	wait_vector		20,3
	read_element		20,0,15
	wait_atom		15,read_predicate
	read_elements_inc		20,1,15,2
	wait_list_var_var		13,21,17
	wait_vector		21,3
	read_element		21,0,18
	wait_atom		18,-
	read_elements_inc		21,1,18,2
	collect_list		13
	collect_vector		20
	collect_vector		21
	put_reused_list		11,11
	write_car_value		11,18
	write_cdr_nil		11
	get_list_value		15,11
	get_value		16,19
	put_value		11,14
	put_value		13,17
	execute		13,reader_13_0
reader_13_1:
	try_me_else		reader_13_5
	wait_list_var_var		11,18,14
	wait_vector		18,3
	read_element		18,0,15
	wait_atom		15,read_predicate
	read_elements_inc		18,1,15,2
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_element		12,1,17
	read_element		12,2,19
	wait_atom		19,end_of_file
	wait_nil		13
	collect_list		11
	collect_vector		12
	get_nil		15
	get_atom		16,end_of_file
	put_reused_func		12,18,-
	write_element_value		12,1,17
	write_element_atom		12,2,end_of_file
	put_value		11,14
	put_nil		13
	execute		13,reader_13_0
reader_13_5:
	otherwise		reader_13_0
	try_me_else		reader_13_9
	jump_on_non_list_var_var		11,reader_13_11,17,14
	wait_vector		17,3
	read_element		17,0,15
	wait_atom		15,read_predicate
	read_elements_inc		17,1,15,2
	wait_nil		13
	collect_list		11
	put_reused_vector		11,17
	write_element_variable		11,0,18
	write_element_variable		11,1,17
	write_element_variable		11,2,13
	get_vector_value		5,11
	b_merge		20,5
	put_vector		21,2
	write_element_variable		21,0,11
	write_element_variable		21,1,19
	get_vector_value		20,21
	create_goal		13
	set_variable		1,22
	set_value		2,2
	set_variable		3,21
	set_value		4,4
	set_value		5,18
	set_variable		6,20
	set_value		7,7
	set_variable		8,18
	set_value		9,9
	set_marked_value		10,10
	set_value		11,14
	set_variable		12,14
	set_value		13,5
	enqueue_goal		13,reader_13_0
	create_goal		16
	set_variable		1,2
	set_value		2,22
	set_variable		3,4
	set_value		4,21
	set_value		5,17
	set_variable		6,7
	set_value		7,20
	set_variable		8,9
	set_value		9,18
	set_value		10,10
	set_value		11,19
	set_value		12,12
	set_variable		13,12
	set_values_inc		14,15,2
	set_value		16,14
	enqueue_goal		16,read_predicate_16_0
	put_value		5,13
	execute		12,expanded_read_12_0
reader_13_11:
	check_nil		11,reader_13_9
	collect_value		13
	collect_value		12
	collect_value		10
	get_nil		5
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	proceed
reader_13_9:
	suspend		reader_13_0
	module_entry		kl1cmp_reader
	predicate		read_predicate,16
read_predicate_16_0:
	try_me_else		read_predicate_16_1
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,17,2
	wait_atom		18,directive
	put_vector		20,2
	write_element_variable		20,0,19
	write_element_variable		20,1,18
	get_vector_value		5,20
	put_vector		21,2
	write_element_variable		21,0,5
	write_element_variable		21,1,20
	get_vector_value		11,21
	put_reused_func		21,12,-
	write_element_variable		21,1,12
	write_element_variable		21,2,11
	get_vector_value		16,21
	create_goal		18
	set_variable		1,22
	set_value		2,2
	set_variable		3,16
	set_value		4,4
	set_value		5,19
	set_variable		6,21
	set_value		7,7
	set_variable		8,19
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	set_variable		12,7
	put_func		2,3,-
	write_element_marked_value		2,1,17
	write_element_atom		2,2,directive
	set_value		13,2
	set_marked_value		14,13
	set_marked_value		15,14
	set_marked_value		16,15
	put_func		4,3,-
	write_element_marked_variable		4,1,5
	write_element_variable		4,2,2
	set_value		17,4
	put_func		4,3,-
	write_elements_dec		4,1,12,2
	set_value		18,4
	enqueue_goal		18,case_dispatch_on_error_18_0
	create_goal		5
	set_variable		1,4
	set_values_inc		2,16,2
	set_value		4,5
	set_value		5,7
	enqueue_goal		5,otherwise_error_check_5_0
	put_func		12,3,-
	write_element_value		12,1,17
	write_element_atom		12,2,directive
	put_func		16,3,-
	write_element_value		16,1,5
	write_element_value		16,2,2
	put_value		2,22
	put_value		5,18
	put_value		7,21
	put_value		9,19
	put_value		11,20
	execute		16,read_predicate_one_block_16_0
read_predicate_16_1:
	otherwise		read_predicate_16_0
	try_me_else		read_predicate_16_6
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,17,2
	put_vector		21,2
	write_element_variable		21,0,20
	write_element_variable		21,1,19
	get_vector_value		5,21
	put_vector		22,2
	write_element_variable		22,0,5
	write_element_variable		22,1,21
	get_vector_value		11,22
	create_goal		16
	set_variable		1,24
	set_value		2,2
	set_variable		3,23
	set_value		4,4
	set_value		5,20
	set_variable		6,22
	set_value		7,7
	set_variable		8,11
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	put_reused_func		5,12,-
	write_element_variable		5,1,4
	write_element_variable		5,2,2
	set_value		12,5
	set_variable		13,20
	set_value		14,14
	set_marked_value		15,15
	set_value		16,16
	enqueue_goal		16,case_dispatch_on_clauses_16_0
	put_func		12,3,-
	write_elements_inc		12,1,17,2
	put_func		16,3,-
	write_element_value		16,1,4
	write_element_value		16,2,2
	put_value		2,24
	put_value		4,23
	put_value		5,19
	put_value		7,22
	put_value		9,11
	put_value		11,21
	put_value		14,20
	execute		16,read_predicate_one_block_16_0
read_predicate_16_6:
	suspend		read_predicate_16_0
	module_entry		kl1cmp_reader
	predicate		case_dispatch_on_clauses,16
case_dispatch_on_clauses_16_0:
	try_me_else		case_dispatch_on_clauses_16_1
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,18,2
	atom		19
	branch_on_atom		19,2,case_dispatch_on_clauses_16_1
	bucket_entry_a		alternatively,case_dispatch_on_clauses_16_5
	bucket_entry_a		otherwise,case_dispatch_on_clauses_16_6
case_dispatch_on_clauses_16_5:
	collect_value		18
	put_vector		19,2
	write_element_variable		19,0,18
	write_element_variable		19,1,17
	get_vector_value		5,19
	put_vector		20,2
	write_element_variable		20,0,5
	write_element_variable		20,1,19
	get_vector_value		11,20
	get_list_val_var		14,20,13,11
	create_goal		16
	set_variable		1,21
	set_value		2,2
	set_variable		3,20
	set_value		4,4
	set_value		5,18
	set_variable		6,14
	set_value		7,7
	set_variable		8,13
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	put_reused_func		2,12,-
	write_element_atom		2,1,alternatively
	write_element_value		2,2,15
	set_value		12,2
	set_variable		13,12
	set_value		14,11
	set_void		15
	set_value		16,16
	enqueue_goal		16,read_predicate_16_0
	put_value		2,21
	put_value		4,20
	put_value		5,17
	put_value		7,14
	put_value		9,13
	put_value		11,19
	execute		12,expanded_read_12_0
case_dispatch_on_clauses_16_6:
	collect_value		18
	put_vector		19,2
	write_element_variable		19,0,18
	write_element_variable		19,1,17
	get_vector_value		5,19
	put_vector		20,2
	write_element_variable		20,0,5
	write_element_variable		20,1,19
	get_vector_value		11,20
	get_list_val_var		14,20,13,11
	create_goal		16
	set_variable		1,21
	set_value		2,2
	set_variable		3,20
	set_value		4,4
	set_value		5,18
	set_variable		6,14
	set_value		7,7
	set_variable		8,13
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	put_reused_func		2,12,-
	write_element_atom		2,1,otherwise
	write_element_value		2,2,15
	set_value		12,2
	set_variable		13,12
	set_value		14,11
	set_void		15
	set_value		16,16
	enqueue_goal		16,read_predicate_16_0
	put_value		2,21
	put_value		4,20
	put_value		5,17
	put_value		7,14
	put_value		9,13
	put_value		11,19
	execute		12,expanded_read_12_0
case_dispatch_on_clauses_16_1:
	otherwise		case_dispatch_on_clauses_16_0
	try_me_else		case_dispatch_on_clauses_16_15
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,17,2
	collect_value		15
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_list		1
	write_car_value		1,13
	write_cdr_nil		1
	get_list_value		14,1
	put_reused_func		1,12,-
	write_elements_inc		1,1,17,2
	get_vector_value		16,1
	proceed
case_dispatch_on_clauses_16_15:
	suspend		case_dispatch_on_clauses_16_0
	module_entry		kl1cmp_reader
	predicate		otherwise_error_check,5
otherwise_error_check_5_0:
	try_me_else		otherwise_error_check_5_1
	atom		3
	branch_on_atom		3,2,otherwise_error_check_5_1
	bucket_entry_a		alternatively,otherwise_error_check_5_3
	bucket_entry_a		otherwise,otherwise_error_check_5_4
otherwise_error_check_5_3:
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_7'
	put_func		6,3,error_message
	write_elements_dec		6,1,4,2
	put_list_val_val		3,6,2
	get_list_value		1,3
	get_atom		5,error
	proceed
otherwise_error_check_5_4:
	put_list		3
	write_car_value		3,4
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_8'
	put_func		6,3,error_message
	write_elements_dec		6,1,4,2
	put_list_val_val		3,6,2
	get_list_value		1,3
	get_atom		5,error
	proceed
otherwise_error_check_5_1:
	otherwise		otherwise_error_check_5_0
	collect_value		4
	collect_value		3
	get_value		1,2
	get_atom		5,non_error
	proceed
otherwise_error_check_5_7:
	suspend		otherwise_error_check_5_0
	module_entry		kl1cmp_reader
	predicate		case_dispatch_on_error,18
case_dispatch_on_error_18_0:
	try_me_else		case_dispatch_on_error_18_1
	atom		12
	branch_on_atom		12,2,case_dispatch_on_error_18_1
	bucket_entry_a		error,case_dispatch_on_error_18_3
	bucket_entry_a		non_error,case_dispatch_on_error_18_4
case_dispatch_on_error_18_3:
	wait_vector		13,3
	read_element		13,0,19
	wait_atom		19,-
	read_elements_inc		13,1,19,2
	wait_atom		20,directive
	wait_vector		17,3
	read_element		17,0,20
	wait_atom		20,-
	read_elements_inc		17,1,20,2
	wait_vector		18,3
	read_element		18,0,22
	wait_atom		22,-
	read_element		18,1,12
	read_element		18,2,22
	collect_value		21
	collect_value		20
	collect_vector		18
	put_reused_func		13,13,-
	write_element_value		13,1,19
	write_element_atom		13,2,directive
	put_reused_func		17,17,-
	write_element_value		17,1,12
	write_element_value		17,2,22
	put_values_inc		12,13,5
	execute		16,read_predicate_one_block_16_0
case_dispatch_on_error_18_4:
	wait_vector		17,3
	read_element		17,0,19
	wait_atom		19,-
	read_elements_inc		17,1,19,2
	wait_vector		18,3
	read_element		18,0,21
	wait_atom		21,-
	read_element		18,1,12
	read_element		18,2,21
	collect_value		16
	collect_value		15
	collect_value		14
	collect_value		13
	collect_value		10
	collect_vector		17
	collect_vector		18
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	get_value		12,19
	get_value		21,20
	proceed
case_dispatch_on_error_18_1:
	suspend		case_dispatch_on_error_18_0
	module_entry		kl1cmp_reader
	predicate		read_predicate_one_block,16
read_predicate_one_block_16_0:
	try_me_else		read_predicate_one_block_16_1
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,18,2
	try_me_else		read_predicate_one_block_16_4
	wait_atom		19,end_of_file
	collect_value		13
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_list		1
	write_car_marked_value		1,18
	write_cdr_nil		1
	get_list_value		14,1
	get_atom		15,end_of_file
	put_reused_func		1,12,-
	write_element_value		1,1,18
	write_element_atom		1,2,end_of_file
	get_vector_value		16,1
	proceed
read_predicate_one_block_16_4:
	try_me_else		read_predicate_one_block_16_1
	wait_vector		13,3
	read_element		13,0,20
	wait_atom		20,-
	read_elements_inc		13,1,20,2
	wait_value		21,19
	collect_value		19
	collect_vector		13
	put_vector		19,2
	write_element_variable		19,0,17
	write_element_variable		19,1,13
	get_vector_value		5,19
	put_vector		22,2
	write_element_variable		22,0,5
	write_element_variable		22,1,19
	get_vector_value		11,22
	get_list_val_var		14,22,18,11
	create_goal		16
	set_variable		1,22
	set_value		2,2
	set_variable		3,18
	set_value		4,4
	set_value		5,17
	set_variable		6,17
	set_value		7,7
	set_variable		8,14
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	put_reused_func		2,12,-
	write_elements_inc		2,1,20,2
	set_value		12,2
	set_variable		13,12
	set_value		14,11
	set_values_inc		15,15,2
	enqueue_goal		16,read_predicate_one_block_16_0
	put_value		2,22
	put_value		4,18
	put_value		5,13
	put_value		7,17
	put_value		9,14
	put_value		11,19
	execute		12,expanded_read_12_0
read_predicate_one_block_16_1:
	otherwise		read_predicate_one_block_16_0
	try_me_else		read_predicate_one_block_16_18
	wait_vector		12,3
	read_element		12,0,17
	wait_atom		17,-
	read_elements_inc		12,1,17,2
	wait_vector		13,3
	read_element		13,0,19
	wait_atom		19,-
	read_elements_inc		13,1,19,2
	collect_value		10
	collect_vector		13
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	get_value		15,18
	put_reused_func		1,12,-
	write_elements_inc		1,1,19,2
	get_vector_value		16,1
	put_list		1
	write_car_value		1,17
	write_cdr_nil		1
	get_list_value		14,1
	proceed
read_predicate_one_block_16_18:
	suspend		read_predicate_one_block_16_0
	module_entry		kl1cmp_reader
	predicate		expanded_read,12
expanded_read_12_0:
	put_value		13,12
	put_func		12,3,getft
	write_element_variable		12,1,15
	write_element_variable		12,2,14
	get_list_val_var		1,16,12,12
	put_value		1,12
	put_value		12,15
	execute		14,dispatch_on_terms_14_0
expanded_read_12_1:
	suspend		expanded_read_12_0
	module_entry		kl1cmp_reader
	predicate		dispatch_on_terms,14
dispatch_on_terms_14_0:
	try_me_else		dispatch_on_terms_14_1
	atom		10
	branch_on_atom		10,2,dispatch_on_terms_14_1
	bucket_entry_a		normal,dispatch_on_terms_14_3
	bucket_entry_a		varchk,dispatch_on_terms_14_4
dispatch_on_terms_14_3:
	wait_vector		12,3
	read_element		12,0,15
	atom		15
	branch_on_atom		15,2,dispatch_on_terms_14_1
	bucket_entry_a		-->,dispatch_on_terms_14_7
	bucket_entry_a		:-,dispatch_on_terms_14_8
dispatch_on_terms_14_7:
	read_element		12,1,16
	read_element		12,2,20
	wait_vector		20,3
	read_element		20,0,17
	wait_atom		17,'|'
	read_element		20,1,10
	read_element		20,2,17
	get_value		1,2
	put_variable		1,18
	put_marked_value		2,6
	b_add		1,2,1
	put_marked_value		2,8
	b_add		1,2,1
	put_reused_func		2,12,/
	write_element_marked_variable		2,1,19
	write_element_marked_value		2,2,1
	put_reused_func		12,20,'|'
	write_element_variable		12,1,21
	write_element_variable		12,2,20
	put_func		15,3,-->
	write_element_variable		15,1,22
	write_element_value		15,2,12
	put_func		12,3,-
	write_element_value		12,1,15
	write_element_value		12,2,2
	get_vector_value		13,12
	create_goal		5
	set_variable		1,12
	put_func		2,3,'|'
	write_element_marked_value		2,1,10
	write_element_variable		2,2,13
	put_func		15,3,-->
	write_element_marked_value		15,1,16
	write_element_value		15,2,2
	set_value		2,15
	put_func		2,3,'|'
	write_elements_dec		2,1,21,2
	put_func		15,3,-->
	write_element_value		15,1,22
	write_element_value		15,2,2
	set_values_dec		3,15,2
	set_void		5
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,-->
	set_value		5,11
	set_values_inc		6,6,4
	set_value		10,17
	set_value		11,13
	put_func		2,3,+
	write_element_value		2,1,16
	write_element_value		2,2,10
	set_value		12,2
	put_func		2,3,/
	write_element_value		2,1,19
	write_element_value		2,2,1
	set_value		13,2
	set_atom		14,no
	set_value		15,12
	enqueue_goal		15,case_expansion_15_0
	put_value		1,16
	put_values_dec		2,19,2
	execute		3,functor_3_0
dispatch_on_terms_14_8:
	read_element		12,1,16
	read_element		12,2,19
	wait_vector		19,3
	read_element		19,0,17
	wait_atom		17,'|'
	read_element		19,1,10
	read_element		19,2,17
	get_value		1,2
	put_reused_func		1,12,/
	write_element_marked_variable		1,1,18
	write_element_marked_variable		1,2,15
	put_reused_func		2,19,'|'
	write_element_variable		2,1,20
	write_element_variable		2,2,19
	put_func		12,3,:-
	write_element_variable		12,1,21
	write_element_value		12,2,2
	put_func		2,3,-
	write_element_value		2,1,12
	write_element_value		2,2,1
	get_vector_value		13,2
	create_goal		5
	set_variable		1,2
	put_func		1,3,'|'
	write_element_marked_value		1,1,10
	write_element_variable		1,2,12
	put_func		13,3,:-
	write_element_marked_value		13,1,16
	write_element_value		13,2,1
	set_value		2,13
	put_func		1,3,'|'
	write_elements_dec		1,1,20,2
	put_func		13,3,:-
	write_element_value		13,1,21
	write_element_value		13,2,1
	set_values_inc		3,13,2
	set_void		5
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,:-
	set_value		5,11
	set_values_inc		6,6,4
	set_value		10,17
	set_value		11,12
	put_func		1,3,+
	write_element_value		1,1,16
	write_element_value		1,2,10
	set_value		12,1
	put_func		1,3,/
	write_element_value		1,1,18
	write_element_value		1,2,15
	set_value		13,1
	set_atom		14,no
	set_value		15,2
	enqueue_goal		15,case_expansion_15_0
	put_value		1,16
	put_value		2,18
	put_value		3,15
	execute		3,functor_3_0
dispatch_on_terms_14_4:
	wait_vector		12,3
	read_element		12,0,15
	atom		15
	branch_on_atom		15,2,dispatch_on_terms_14_1
	bucket_entry_a		-->,dispatch_on_terms_14_11
	bucket_entry_a		:-,dispatch_on_terms_14_12
dispatch_on_terms_14_11:
	read_element		12,1,16
	read_element		12,2,20
	wait_vector		20,3
	read_element		20,0,17
	wait_atom		17,'|'
	read_element		20,1,10
	read_element		20,2,17
	get_value		1,2
	put_variable		1,18
	put_marked_value		2,6
	b_add		1,2,1
	put_marked_value		2,8
	b_add		1,2,1
	put_reused_func		2,12,/
	write_element_marked_variable		2,1,19
	write_element_marked_value		2,2,1
	put_reused_func		12,20,'|'
	write_element_variable		12,1,21
	write_element_variable		12,2,20
	put_func		15,3,-->
	write_element_variable		15,1,22
	write_element_value		15,2,12
	put_func		12,3,+
	write_element_value		12,1,15
	write_element_variable		12,2,15
	put_func		23,3,-
	write_element_value		23,1,12
	write_element_value		23,2,2
	get_vector_value		13,23
	create_goal		5
	set_variable		1,12
	put_func		2,3,'|'
	write_element_marked_value		2,1,10
	write_element_variable		2,2,13
	put_func		23,3,-->
	write_element_marked_value		23,1,16
	write_element_value		23,2,2
	set_value		2,23
	put_func		2,3,'|'
	write_elements_dec		2,1,21,2
	put_func		20,3,-->
	write_element_value		20,1,22
	write_element_value		20,2,2
	set_value		3,20
	set_values_inc		4,14,2
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,-->
	set_value		5,11
	set_values_inc		6,6,4
	set_value		10,17
	set_value		11,13
	put_func		2,3,+
	write_element_value		2,1,16
	write_element_value		2,2,10
	set_value		12,2
	put_func		2,3,/
	write_element_value		2,1,19
	write_element_value		2,2,1
	set_value		13,2
	set_atom		14,no
	set_value		15,12
	enqueue_goal		15,case_expansion_15_0
	put_value		1,16
	put_values_dec		2,19,2
	execute		3,functor_3_0
dispatch_on_terms_14_12:
	read_element		12,1,16
	read_element		12,2,19
	wait_vector		19,3
	read_element		19,0,17
	wait_atom		17,'|'
	read_element		19,1,10
	read_element		19,2,17
	get_value		1,2
	put_reused_func		1,12,/
	write_element_marked_variable		1,1,18
	write_element_marked_variable		1,2,15
	put_reused_func		2,19,'|'
	write_element_variable		2,1,20
	write_element_variable		2,2,19
	put_func		12,3,:-
	write_element_variable		12,1,21
	write_element_value		12,2,2
	put_func		2,3,+
	write_element_value		2,1,12
	write_element_variable		2,2,12
	put_func		22,3,-
	write_elements_dec		22,1,2,2
	get_vector_value		13,22
	create_goal		5
	set_variable		1,2
	put_func		1,3,'|'
	write_element_marked_value		1,1,10
	write_element_variable		1,2,13
	put_func		22,3,:-
	write_element_marked_value		22,1,16
	write_element_value		22,2,1
	set_value		2,22
	put_func		1,3,'|'
	write_elements_dec		1,1,20,2
	put_func		19,3,:-
	write_element_value		19,1,21
	write_element_value		19,2,1
	set_value		3,19
	set_value		4,14
	set_value		5,12
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,:-
	set_value		5,11
	set_values_inc		6,6,4
	set_value		10,17
	set_value		11,13
	put_func		1,3,+
	write_element_value		1,1,16
	write_element_value		1,2,10
	set_value		12,1
	put_func		1,3,/
	write_element_value		1,1,18
	write_element_value		1,2,15
	set_value		13,1
	set_atom		14,no
	set_value		15,2
	enqueue_goal		15,case_expansion_15_0
	put_value		1,16
	put_value		2,18
	put_value		3,15
	execute		3,functor_3_0
dispatch_on_terms_14_1:
	try_me_else		dispatch_on_terms_14_13
	jump_on_non_atom		12,dispatch_on_terms_14_15
	branch_on_atom		12,3,dispatch_on_terms_14_13
	bucket_entry_a		alternatively,dispatch_on_terms_14_16
	bucket_entry_a		end_of_file,dispatch_on_terms_14_17
	bucket_entry_a		otherwise,dispatch_on_terms_14_18
dispatch_on_terms_14_16:
	collect_value		14
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_structured_constant		1,'$SCNST_9'
	get_value		13,1
	proceed
dispatch_on_terms_14_17:
	collect_value		14
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_structured_constant		1,'$SCNST_10'
	get_value		13,1
	proceed
dispatch_on_terms_14_18:
	collect_value		14
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_structured_constant		1,'$SCNST_11'
	get_value		13,1
	proceed
dispatch_on_terms_14_15:
	check_vector		12,2,dispatch_on_terms_14_13
	read_element		12,0,15
	wait_atom		15,:-
	read_element		12,1,15
	collect_value		14
	put_reused_func		12,12,:-
	write_element_value		12,1,15
	execute		13,check_directives_13_0
dispatch_on_terms_14_13:
	otherwise		dispatch_on_terms_14_0
	try_me_else		dispatch_on_terms_14_32
	wait_atom		10,varchk
	wait_vector		12,3
	read_element		12,0,15
	atom		15
	branch_on_atom		15,2,dispatch_on_terms_14_32
	bucket_entry_a		-->,dispatch_on_terms_14_36
	bucket_entry_a		:-,dispatch_on_terms_14_37
dispatch_on_terms_14_36:
	read_element		12,1,10
	read_element		12,2,16
	get_value		1,2
	put_variable		1,17
	put_marked_value		2,6
	b_add		1,2,1
	put_marked_value		2,8
	b_add		1,2,1
	put_reused_func		2,12,/
	write_element_marked_variable		2,1,18
	write_element_marked_value		2,2,1
	put_func		12,3,-->
	write_element_variable		12,1,20
	write_element_variable		12,2,19
	put_func		15,3,+
	write_element_value		15,1,12
	write_element_variable		15,2,12
	put_func		21,3,-
	write_element_value		21,1,15
	write_element_value		21,2,2
	get_vector_value		13,21
	create_goal		5
	set_variable		1,13
	put_func		2,3,'|'
	write_element_atom		2,1,true
	write_element_variable		2,2,15
	put_func		21,3,-->
	write_element_marked_value		21,1,10
	write_element_value		21,2,2
	set_value		2,21
	put_func		2,3,'|'
	write_element_void		2,1
	write_element_value		2,2,19
	put_func		19,3,-->
	write_element_value		19,1,20
	write_element_value		19,2,2
	set_value		3,19
	set_value		4,14
	set_value		5,12
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,-->
	set_value		5,11
	set_values_inc		6,6,4
	set_values_dec		10,16,2
	put_func		2,3,+
	write_element_value		2,1,10
	write_element_atom		2,2,true
	set_value		12,2
	put_func		2,3,/
	write_element_value		2,1,18
	write_element_value		2,2,1
	set_value		13,2
	set_atom		14,no
	set_value		15,13
	enqueue_goal		15,case_expansion_15_0
	put_value		1,10
	put_values_dec		2,18,2
	execute		3,functor_3_0
dispatch_on_terms_14_37:
	read_element		12,1,10
	read_element		12,2,16
	get_value		1,2
	put_reused_func		1,12,/
	write_element_marked_variable		1,1,17
	write_element_marked_variable		1,2,15
	put_func		2,3,:-
	write_element_variable		2,1,19
	write_element_variable		2,2,18
	put_func		12,3,+
	write_element_value		12,1,2
	write_element_variable		12,2,2
	put_func		20,3,-
	write_element_value		20,1,12
	write_element_value		20,2,1
	get_vector_value		13,20
	create_goal		5
	set_variable		1,12
	put_func		1,3,'|'
	write_element_atom		1,1,true
	write_element_variable		1,2,13
	put_func		20,3,:-
	write_element_marked_value		20,1,10
	write_element_value		20,2,1
	set_value		2,20
	put_func		1,3,'|'
	write_element_void		1,1
	write_element_value		1,2,18
	put_func		18,3,:-
	write_element_value		18,1,19
	write_element_value		18,2,1
	set_value		3,18
	set_value		4,14
	set_value		5,2
	enqueue_goal		5,copy_one_clause_5_0
	create_goal		15
	set_values_inc		1,3,3
	set_atom		4,:-
	set_value		5,11
	set_values_inc		6,6,4
	set_value		10,16
	set_value		11,13
	put_func		1,3,+
	write_element_value		1,1,10
	write_element_atom		1,2,true
	set_value		12,1
	put_func		1,3,/
	write_element_value		1,1,17
	write_element_value		1,2,15
	set_value		13,1
	set_atom		14,no
	set_value		15,12
	enqueue_goal		15,case_expansion_15_0
	put_value		1,10
	put_value		2,17
	put_value		3,15
	execute		3,functor_3_0
dispatch_on_terms_14_32:
	otherwise		dispatch_on_terms_14_0
	try_me_else		dispatch_on_terms_14_45
	wait_atom		10,varchk
	jump_on_non_atom		12,dispatch_on_terms_14_48
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_func		1,3,/
	write_element_marked_value		1,1,12
	write_element_integer		1,2,0
	put_func		2,3,+
	write_element_value		2,1,12
	write_element_value		2,2,14
	put_func		3,3,-
	write_elements_dec		3,1,2,2
	get_vector_value		13,3
	proceed
dispatch_on_terms_14_48:
	is_vector		12,dispatch_on_terms_14_45
	put_integer		15,0
	g_vector_element		12,15,15
	atom		15
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_func		1,3,/
	write_element_variable		1,1,4
	write_element_variable		1,2,3
	put_func		2,3,+
	write_element_marked_value		2,1,12
	write_element_value		2,2,14
	put_func		5,3,-
	write_elements_dec		5,1,2,2
	get_vector_value		13,5
	put_value		1,12
	put_value		2,4
	execute		3,functor_3_0
dispatch_on_terms_14_45:
	otherwise		dispatch_on_terms_14_0
	put_vector		17,2
	write_element_variable		17,0,16
	write_element_variable		17,1,15
	get_vector_value		5,17
	put_vector		18,2
	write_element_variable		18,0,5
	write_element_variable		18,1,17
	get_vector_value		11,18
	create_goal		14
	set_variable		1,20
	set_value		2,2
	set_variable		3,19
	set_value		4,4
	set_value		5,16
	set_variable		6,18
	set_value		7,7
	set_variable		8,11
	set_value		9,9
	set_marked_value		10,10
	set_value		11,5
	set_variable		12,16
	set_values_inc		13,13,2
	enqueue_goal		14,dispatch_on_terms_14_0
	put_value		2,20
	put_value		4,19
	put_value		5,15
	put_value		7,18
	put_value		9,11
	put_value		11,17
	put_value		13,16
	execute		13,normalize_clause_13_0
dispatch_on_terms_14_54:
	suspend		dispatch_on_terms_14_0
	module_entry		kl1cmp_reader
	predicate		normalize_clause,13
normalize_clause_13_0:
	try_me_else		normalize_clause_13_1
	wait_vector		12,3
	read_element		12,0,14
	atom		14
	branch_on_atom		14,2,normalize_clause_13_1
	bucket_entry_a		-->,normalize_clause_13_4
	bucket_entry_a		:-,normalize_clause_13_5
normalize_clause_13_4:
	read_elements_inc		12,1,15,2
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_reused_func		1,12,'|'
	write_element_atom		1,1,true
	write_element_value		1,2,16
	put_func		2,3,-->
	write_element_value		2,1,15
	write_element_value		2,2,1
	get_vector_value		13,2
	proceed
normalize_clause_13_5:
	read_elements_inc		12,1,15,2
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_reused_func		1,12,:-
	write_element_marked_value		1,1,15
	write_element_marked_value		1,2,16
	put_structured_constant		2,'$SCNST_12'
	put_func		5,3,warning_message
	write_elements_dec		5,1,2,2
	put_list_val_val		1,5,4
	get_list_value		3,1
	put_func		1,3,'|'
	write_element_atom		1,1,true
	write_element_value		1,2,16
	put_func		2,3,:-
	write_element_value		2,1,15
	write_element_value		2,2,1
	get_vector_value		13,2
	proceed
normalize_clause_13_1:
	otherwise		normalize_clause_13_0
	try_me_else		normalize_clause_13_11
	jump_on_non_atom		12,normalize_clause_13_13
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_structured_constant		1,'$SCNST_13'
	put_func		2,3,warning_message
	write_element_value		2,1,1
	write_element_marked_value		2,2,12
	put_list_val_val		1,2,4
	get_list_value		3,1
	put_structured_constant		1,'$SCNST_14'
	put_func		2,3,:-
	write_element_value		2,1,12
	write_element_value		2,2,1
	get_vector_value		13,2
	proceed
normalize_clause_13_13:
	is_vector		12,normalize_clause_13_11
	put_integer		14,0
	g_vector_element		12,14,14
	atom		14
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		1,2
	put_structured_constant		1,'$SCNST_15'
	put_func		2,3,warning_message
	write_element_value		2,1,1
	write_element_marked_value		2,2,12
	put_list_val_val		1,2,4
	get_list_value		3,1
	put_structured_constant		1,'$SCNST_16'
	put_func		2,3,:-
	write_element_value		2,1,12
	write_element_value		2,2,1
	get_vector_value		13,2
	proceed
normalize_clause_13_11:
	otherwise		normalize_clause_13_0
	put_structured_constant		14,'$SCNST_17'
	put_func		15,3,warning_message
	write_element_value		15,1,14
	write_element_value		15,2,12
	get_list_val_var		3,14,15,12
	put_value		3,12
	put_value		12,13
	execute		12,expanded_read_12_0
normalize_clause_13_17:
	suspend		normalize_clause_13_0
	module_entry		kl1cmp_reader
	predicate		check_directives,13
check_directives_13_0:
	try_me_else		check_directives_13_1
	wait_vector		12,2
	read_element		12,0,14
	wait_atom		14,:-
	read_element		12,1,15
	jump_on_non_atom		15,check_directives_13_5
	test_atom		15,local_implicit,check_directives_13_1
	collect_value		10
	collect_value		8
	collect_vector		12
	get_nil		5
	get_nil		11
	get_integer		9,0
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_structured_constant		1,'$SCNST_18'
	get_value		13,1
	proceed
check_directives_13_5:
	is_vector		15,check_directives_13_1
	jump_on_arity		15,5,check_directives_13_1
	table_entry		check_directives_13_1
	table_entry		check_directives_13_1
	table_entry		check_directives_13_6
	table_entry		check_directives_13_1
	table_entry		check_directives_13_7
check_directives_13_6:
	read_element		15,0,16
	atom		16
	branch_on_atom		16,2,check_directives_13_1
	bucket_entry_a		implicit,check_directives_13_9
	bucket_entry_a		local_implicit,check_directives_13_10
check_directives_13_9:
	read_element		15,1,14
	collect_value		10
	collect_value		6
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		1,2
	put_reused_func		1,12,implicit
	write_element_variable		1,1,6
	put_reused_func		2,15,:-
	write_element_value		2,1,1
	put_func		1,3,-
	write_element_value		1,1,2
	write_element_atom		1,2,directive
	get_vector_value		13,1
	put_values_inc		1,3,2
	put_integer		3,0
	put_value		4,7
	put_value		5,14
	execute		6,count_implicit_args_6_0
check_directives_13_10:
	read_element		15,1,14
	collect_value		10
	collect_value		8
	get_nil		5
	get_nil		11
	get_value		6,7
	get_value		1,2
	put_reused_func		1,12,local_implicit
	write_element_variable		1,1,6
	put_reused_func		2,15,:-
	write_element_value		2,1,1
	put_func		1,3,-
	write_element_value		1,1,2
	write_element_atom		1,2,directive
	get_vector_value		13,1
	put_values_inc		1,3,2
	put_integer		3,0
	put_value		4,9
	put_value		5,14
	execute		6,count_implicit_args_6_0
check_directives_13_7:
	read_element		15,0,16
	wait_atom		16,op
	read_element		15,1,14
	read_elements_inc		15,2,16,2
	collect_vector		12
	put_reused_func		12,15,add_op
	write_element_value		12,1,14
	write_elements_inc		12,2,16,2
	get_list_val_var		1,14,12,12
	put_value		1,12
	put_value		12,13
	execute		12,expanded_read_12_0
check_directives_13_1:
	otherwise		check_directives_13_0
	collect_value		10
	get_nil		5
	get_nil		11
	get_value		8,9
	get_value		6,7
	get_value		3,4
	get_value		1,2
	put_func		1,3,-
	write_element_value		1,1,12
	write_element_atom		1,2,directive
	get_vector_value		13,1
	proceed
check_directives_13_23:
	suspend		check_directives_13_0
	module_entry		kl1cmp_reader
	predicate		count_implicit_args,6
count_implicit_args_6_0:
	try_me_else		count_implicit_args_6_1
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,','
	read_elements_inc		5,1,7,2
	put_reused_func		5,5,','
	write_element_variable		5,1,9
	write_element_variable		5,2,10
	get_vector_value		6,5
	create_goal		6
	set_variable		1,6
	set_value		2,2
	set_variable		3,5
	set_value		4,4
	set_value		5,8
	set_value		6,10
	enqueue_goal		6,count_implicit_args_6_0
	put_value		2,6
	put_value		4,5
	put_value		5,7
	put_value		6,9
	execute		6,increment_implicit_arg_number_6_0
count_implicit_args_6_1:
	otherwise		count_implicit_args_6_0
	execute		6,increment_implicit_arg_number_6_0
count_implicit_args_6_6:
	suspend		count_implicit_args_6_0
	module_entry		kl1cmp_reader
	predicate		increment_implicit_arg_number,6
increment_implicit_arg_number_6_0:
	try_me_else		increment_implicit_arg_number_6_1
	wait_vector		5,3
	read_element		5,0,7
	wait_atom		7,:
	read_elements_inc		5,1,8,2
	atom		9
	hash_on_atom		9,4,increment_implicit_arg_number_6_1
	bucket_entry_a		oldnew,increment_implicit_arg_number_6_5
	bucket_entry_a		shared,increment_implicit_arg_number_6_6
	bucket_entry_a		stream,increment_implicit_arg_number_6_7
	bucket_entry_a		string,increment_implicit_arg_number_6_8
increment_implicit_arg_number_6_5:
	get_value		1,2
	put_integer		1,2
	b_add		3,1,1
	get_value		1,4
	put_reused_func		1,5,:
	write_element_value		1,1,8
	write_element_atom		1,2,oldnew
	get_vector_value		6,1
	proceed
increment_implicit_arg_number_6_6:
	get_value		1,2
	b_increment		3,1
	get_value		1,4
	put_reused_func		1,5,:
	write_element_value		1,1,8
	write_element_atom		1,2,shared
	get_vector_value		6,1
	proceed
increment_implicit_arg_number_6_7:
	get_value		1,2
	b_increment		3,1
	get_value		1,4
	put_reused_func		1,5,:
	write_element_value		1,1,8
	write_element_atom		1,2,stream
	get_vector_value		6,1
	proceed
increment_implicit_arg_number_6_8:
	get_value		1,2
	put_integer		1,2
	b_add		3,1,1
	get_value		1,4
	put_reused_func		1,5,:
	write_element_value		1,1,8
	write_element_atom		1,2,string
	get_vector_value		6,1
	proceed
increment_implicit_arg_number_6_1:
	otherwise		increment_implicit_arg_number_6_0
	get_value		3,4
	put_list		3
	write_car_marked_value		3,5
	write_cdr_nil		3
	put_structured_constant		4,'$SCNST_19'
	put_func		7,3,error_message
	write_elements_dec		7,1,4,2
	put_list_val_val		3,7,2
	get_list_value		1,3
	get_value		5,6
	proceed
increment_implicit_arg_number_6_17:
	suspend		increment_implicit_arg_number_6_0
	module_entry		kl1cmp_reader
	predicate		convert_integer_to_string,2
convert_integer_to_string_2_0:
	put_value		3,1
	create_goal		3
	set_integer		1,0
	set_variable		2,1
	set_value		3,2
	enqueue_goal		3,convert_list_to_string_3_0
	put_nil		2
	execute		3,convert_integer_to_list_3_0
convert_integer_to_string_2_1:
	suspend		convert_integer_to_string_2_0
	module_entry		kl1cmp_reader
	predicate		copy_one_clause,5
copy_one_clause_5_0:
	try_me_else		copy_one_clause_5_1
	atom		1
	branch_on_atom		1,2,copy_one_clause_5_1
	bucket_entry_a		no,copy_one_clause_5_3
	bucket_entry_a		yes,copy_one_clause_5_4
copy_one_clause_5_3:
	wait_vector		2,3
	read_element		2,0,6
	atom		6
	branch_on_atom		6,2,copy_one_clause_5_1
	bucket_entry_a		-->,copy_one_clause_5_7
	bucket_entry_a		:-,copy_one_clause_5_8
copy_one_clause_5_7:
	read_element		2,1,7
	read_element		2,2,12
	wait_vector		12,3
	read_element		12,0,8
	wait_atom		8,'|'
	read_elements_inc		12,1,8,2
	wait_vector		3,3
	read_element		3,0,10
	wait_atom		10,-->
	read_element		3,1,10
	read_element		3,2,13
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,'|'
	read_element		13,1,1
	read_element		13,2,11
	collect_vector		2
	collect_vector		12
	collect_vector		3
	collect_vector		13
	get_value		7,10
	get_value		8,1
	get_value		9,11
	get_value		4,5
	proceed
copy_one_clause_5_8:
	read_element		2,1,7
	read_element		2,2,12
	wait_vector		12,3
	read_element		12,0,8
	wait_atom		8,'|'
	read_elements_inc		12,1,8,2
	wait_vector		3,3
	read_element		3,0,10
	wait_atom		10,:-
	read_element		3,1,10
	read_element		3,2,13
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,'|'
	read_element		13,1,1
	read_element		13,2,11
	collect_vector		2
	collect_vector		12
	collect_vector		3
	collect_vector		13
	get_value		7,10
	get_value		8,1
	get_value		9,11
	get_value		4,5
	proceed
copy_one_clause_5_4:
	collect_value		4
	put_values_inc		1,2,2
	put_value		3,5
	execute		3,copy_one_term_3_0
copy_one_clause_5_1:
	suspend		copy_one_clause_5_0
	module_entry		kl1cmp_reader
	predicate		case_expansion,15
case_expansion_15_0:
	try_me_else		case_expansion_15_1
	vector		10
	jump_on_arity		10,4,case_expansion_15_1
	table_entry		case_expansion_15_1
	table_entry		case_expansion_15_3
	table_entry		case_expansion_15_1
	table_entry		case_expansion_15_4
case_expansion_15_3:
	read_element		10,0,16
	vector		16
	g_vector		16,17
	put_values_inc		18,12,4
	put_reused_vector		10,10
	write_element_variable		10,0,13
	get_vector_value		11,10
	put_integer		10,0
	put_values_dec		11,17,2
	put_values_inc		14,18,4
	execute		17,case_expansion_vector_17_0
case_expansion_15_4:
	read_element		10,0,16
	atom		16
	branch_on_atom		16,3,case_expansion_15_1
	bucket_entry_a		',',case_expansion_15_6
	bucket_entry_a		->,case_expansion_15_7
	bucket_entry_a		;,case_expansion_15_8
case_expansion_15_6:
	read_elements_inc		10,1,17,2
	put_vector		20,2
	write_element_variable		20,0,19
	write_element_variable		20,1,16
	get_vector_value		3,20
	put_vector		21,2
	write_element_variable		21,0,3
	write_element_variable		21,1,20
	get_vector_value		5,21
	put_reused_func		10,10,','
	write_element_variable		10,1,21
	write_element_variable		10,2,5
	get_vector_value		11,10
	create_goal		15
	set_variable		1,22
	set_value		2,2
	set_value		3,19
	set_marked_value		4,4
	set_value		5,3
	set_variable		6,11
	set_value		7,7
	set_variable		8,10
	set_value		9,9
	set_marked_value		10,18
	set_value		11,5
	put_func		2,3,+
	write_element_marked_value		2,1,12
	write_element_marked_value		2,2,17
	set_value		12,2
	set_marked_value		13,13
	set_variable		14,19
	set_value		15,15
	enqueue_goal		15,case_expansion_15_0
	put_func		15,3,+
	write_element_value		15,1,12
	write_element_value		15,2,18
	put_value		2,22
	put_value		3,16
	put_value		5,20
	put_value		7,11
	put_value		9,10
	put_value		10,17
	put_value		11,21
	put_value		12,15
	put_value		15,19
	execute		15,case_expansion_15_0
case_expansion_15_7:
	read_elements_inc		10,1,17,2
	collect_value		14
	get_atom		15,yes
	put_reused_func		10,10,->
	write_elements_inc		10,1,17,2
	execute		13,case_expand_13_0
case_expansion_15_8:
	read_elements_inc		10,1,17,2
	collect_value		14
	get_atom		15,yes
	put_reused_func		10,10,;
	write_elements_inc		10,1,17,2
	execute		13,case_expand_13_0
case_expansion_15_1:
	otherwise		case_expansion_15_0
	collect_value		13
	collect_value		12
	collect_value		4
	get_nil		3
	get_nil		5
	get_value		8,9
	get_value		6,7
	get_value		1,2
	get_value		10,11
	get_value		14,15
	proceed
case_expansion_15_13:
	suspend		case_expansion_15_0
	module_entry		kl1cmp_reader
	predicate		case_expansion_vector,17
case_expansion_vector_17_0:
	try_me_else		case_expansion_vector_17_1
	integer		10
	integer		11
	g_less_than		10,11
	put_vector		20,2
	write_element_variable		20,0,19
	write_element_variable		20,1,18
	get_vector_value		3,20
	put_vector		3,2
	write_element_variable		3,0,21
	write_element_variable		3,1,20
	get_vector_value		5,3
	put_marked_value		3,10
	b_increment		3,3
	put_variable		5,22
	b_set_vector_element		12,10,10,5,5
	create_goal		17
	set_variable		1,24
	set_value		2,2
	set_value		3,19
	set_marked_value		4,4
	set_value		5,21
	set_variable		6,23
	set_value		7,7
	set_variable		8,21
	set_value		9,9
	set_value		10,3
	set_value		11,11
	set_marked_value		12,5
	set_value		13,13
	put_func		2,3,+
	write_element_marked_value		2,1,10
	write_element_marked_value		2,2,14
	set_value		14,2
	set_marked_value		15,15
	set_variable		16,19
	set_value		17,17
	enqueue_goal		17,case_expansion_vector_17_0
	put_func		12,3,+
	write_element_value		12,1,5
	write_element_value		12,2,14
	put_value		2,24
	put_value		3,18
	put_value		5,20
	put_value		7,23
	put_value		9,21
	put_value		11,22
	put_values_inc		13,15,2
	put_value		15,19
	execute		15,case_expansion_15_0
case_expansion_vector_17_1:
	try_me_else		case_expansion_vector_17_3
	wait_value		10,11
	collect_value		15
	collect_value		14
	collect_value		10
	collect_value		4
	collect_value		11
	get_nil		3
	get_nil		5
	get_value		8,9
	get_value		6,7
	get_value		1,2
	get_value		12,13
	get_value		16,17
	proceed
case_expansion_vector_17_3:
	suspend		case_expansion_vector_17_0
	module_entry		kl1cmp_reader
	predicate		case_expand,13
case_expand_13_0:
	put_func		14,3,new_name
	write_element_value		14,1,13
	write_element_variable		14,2,15
	get_list_val_var		3,13,14,14
	put_func		3,3,/
	write_element_marked_variable		3,1,16
	write_element_marked_variable		3,2,17
	put_func		13,3,-
	write_element_variable		13,1,18
	write_element_value		13,2,3
	get_list_val_var		5,19,13,3
	create_goal		14
	set_values_inc		1,1,2
	set_value		3,14
	set_marked_value		4,4
	set_value		5,3
	set_marked_value		6,6
	set_value		7,7
	set_marked_value		8,8
	set_value		9,9
	set_value		10,18
	set_nil		11
	set_marked_value		12,10
	set_marked_value		13,11
	put_func		1,3,/
	write_elements_inc		1,1,16,2
	set_value		14,1
	enqueue_goal		14,case_expand_clauses_14_0
	create_goal		5
	set_value		1,4
	set_value		2,6
	set_value		3,8
	set_variable		4,1
	set_value		5,17
	enqueue_goal		5,calcurate_real_arity_5_0
	create_goal		3
	set_value		1,11
	set_value		2,16
	set_value		3,1
	enqueue_goal		3,functor_3_0
	create_goal		2
	put_list_val_var		1,15,3
	set_value		1,1
	set_value		2,11
	enqueue_goal		2,generate_case_head_2_0
	create_goal		3
	set_variable		1,1
	set_variable		2,2
	set_value		3,3
	enqueue_goal		3,intersection_3_0
	create_goal		4
	set_value		1,2
	set_nil		2
	set_value		3,12
	set_nil		4
	enqueue_goal		4,list_variables_4_0
	put_nil		2
	put_value		3,10
	put_nil		4
	execute		4,list_variables_4_0
case_expand_13_1:
	suspend		case_expand_13_0
	module_entry		kl1cmp_reader
	predicate		calcurate_real_arity,5
calcurate_real_arity_5_0:
	try_me_else		calcurate_real_arity_5_1
	atom		1
	branch_on_atom		1,2,calcurate_real_arity_5_1
	bucket_entry_a		-->,calcurate_real_arity_5_3
	bucket_entry_a		:-,calcurate_real_arity_5_4
calcurate_real_arity_5_3:
	b_add		4,2,1
	b_add		1,3,1
	get_value		5,1
	proceed
calcurate_real_arity_5_4:
	collect_value		3
	collect_value		2
	get_value		5,4
	proceed
calcurate_real_arity_5_1:
	suspend		calcurate_real_arity_5_0
	module_entry		kl1cmp_reader
	predicate		generate_case_head,2
generate_case_head_2_0:
	try_me_else		generate_case_head_2_1
	wait_list_var_var		1,3,4
	wait_nil		4
	collect_list		1
	get_value		2,3
	proceed
generate_case_head_2_1:
	otherwise		generate_case_head_2_0
	put_variable		3,4
	b_new_vector		3,3
	create_goal		4
	set_integer		1,0
	set_marked_value		2,1
	set_values_dec		3,3,2
	enqueue_goal		4,copy_list_to_vector_4_0
	put_value		2,4
	execute		2,len_of_list_2_0
generate_case_head_2_5:
	suspend		generate_case_head_2_0
	module_entry		kl1cmp_reader
	predicate		copy_list_to_vector,4
copy_list_to_vector_4_0:
	try_me_else		copy_list_to_vector_4_1
	jump_on_non_list_var_var		2,copy_list_to_vector_4_3,5,6
	collect_list		2
	put_marked_value		2,1
	b_set_vector_element		3,2,2,5,3
	b_increment		1,1
	put_value		2,6
	execute		4,copy_list_to_vector_4_0
copy_list_to_vector_4_3:
	check_nil		2,copy_list_to_vector_4_1
	collect_value		1
	get_value		3,4
	proceed
copy_list_to_vector_4_1:
	suspend		copy_list_to_vector_4_0
	module_entry		kl1cmp_reader
	predicate		copy_list_to_args,4
copy_list_to_args_4_0:
	try_me_else		copy_list_to_args_4_1
	jump_on_non_list_var_var		2,copy_list_to_args_4_3,5,6
	collect_list		2
	put_marked_value		2,1
	b_set_vector_element		3,2,2,5,3
	b_increment		1,1
	put_value		2,6
	execute		4,copy_list_to_args_4_0
copy_list_to_args_4_3:
	check_nil		2,copy_list_to_args_4_1
	collect_value		1
	get_value		3,4
	proceed
copy_list_to_args_4_1:
	suspend		copy_list_to_args_4_0
	module_entry		kl1cmp_reader
	predicate		case_expand_clauses,14
case_expand_clauses_14_0:
	try_me_else		case_expand_clauses_14_1
	jump_on_non_atom		12,case_expand_clauses_14_3
	branch_on_atom		12,2,case_expand_clauses_14_1
	bucket_entry_a		alternatively,case_expand_clauses_14_4
	bucket_entry_a		otherwise,case_expand_clauses_14_5
case_expand_clauses_14_4:
	collect_value		14
	collect_value		13
	collect_value		4
	get_nil		3
	get_nil		5
	get_value		10,11
	get_value		8,9
	get_value		6,7
	put_structured_constant		3,'$SCNST_20'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
case_expand_clauses_14_5:
	collect_value		14
	collect_value		13
	collect_value		4
	get_nil		3
	get_nil		5
	get_value		10,11
	get_value		8,9
	get_value		6,7
	put_structured_constant		3,'$SCNST_21'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
case_expand_clauses_14_3:
	is_vector		12,case_expand_clauses_14_1
	jump_on_arity		12,4,case_expand_clauses_14_1
	table_entry		case_expand_clauses_14_1
	table_entry		case_expand_clauses_14_6
	table_entry		case_expand_clauses_14_1
	table_entry		case_expand_clauses_14_7
case_expand_clauses_14_6:
	read_element		12,0,15
	vector		15
	g_vector		15,16
	collect_vector		12
	create_goal		14
	set_values_inc		1,1,11
	set_variable		12,4
	set_values_inc		13,13,2
	enqueue_goal		14,case_expand_clauses_14_0
	put_integer		1,0
	put_values_dec		2,16,2
	execute		4,convert_case_vector_4_0
case_expand_clauses_14_7:
	read_element		12,0,15
	wait_atom		15,;
	read_element		12,1,16
	atom		16
	branch_on_atom		16,2,case_expand_clauses_14_1
	bucket_entry_a		alternatively,case_expand_clauses_14_10
	bucket_entry_a		otherwise,case_expand_clauses_14_11
case_expand_clauses_14_10:
	read_element		12,2,17
	collect_vector		12
	put_list		15
	write_car_atom		15,alternatively
	write_cdr_variable		15,12
	get_list_value		10,15
	put_value		10,12
	put_value		12,17
	execute		14,case_expand_clauses_14_0
case_expand_clauses_14_11:
	read_element		12,2,17
	collect_vector		12
	put_list		15
	write_car_atom		15,otherwise
	write_cdr_variable		15,12
	get_list_value		10,15
	put_value		10,12
	put_value		12,17
	execute		14,case_expand_clauses_14_0
case_expand_clauses_14_1:
	otherwise		case_expand_clauses_14_0
	try_me_else		case_expand_clauses_14_20
	wait_vector		12,3
	read_element		12,0,15
	wait_atom		15,->
	read_element		12,1,15
	read_element		12,2,18
	wait_vector		18,1
	read_element		18,0,16
	vector		16
	g_vector		16,17
	put_value		19,14
	create_goal		6
	set_values_inc		1,10,2
	set_marked_value		3,4
	set_marked_value		4,13
	set_marked_value		5,15
	put_reused_vector		10,18
	write_element_variable		10,0,18
	set_value		6,10
	enqueue_goal		6,make_term_6_0
	put_reused_func		14,12,+
	write_element_value		14,1,13
	write_element_value		14,2,15
	put_integer		10,0
	put_values_dec		11,17,2
	put_value		13,18
	put_value		15,19
	put_atom		16,no
	put_void		17
	execute		17,case_expansion_vector_17_0
case_expand_clauses_14_20:
	otherwise		case_expand_clauses_14_0
	try_me_else		case_expand_clauses_14_25
	wait_vector		12,3
	read_element		12,0,15
	wait_atom		15,;
	read_element		12,1,18
	read_element		12,2,15
	wait_vector		18,3
	read_element		18,0,16
	wait_atom		16,->
	read_elements_inc		18,1,16,2
	collect_vector		18
	put_vector		20,2
	write_element_variable		20,0,19
	write_element_variable		20,1,18
	get_vector_value		3,20
	put_vector		21,2
	write_element_variable		21,0,3
	write_element_variable		21,1,20
	get_vector_value		5,21
	create_goal		14
	set_variable		1,5
	set_value		2,2
	set_value		3,19
	set_marked_value		4,4
	set_value		5,3
	set_variable		6,21
	set_value		7,7
	set_variable		8,19
	set_value		9,9
	set_variable		10,2
	set_value		11,11
	set_value		12,15
	set_marked_value		13,13
	set_marked_value		14,14
	enqueue_goal		14,case_expand_clauses_14_0
	create_goal		6
	set_value		1,10
	set_value		2,2
	set_value		3,4
	set_value		4,13
	set_marked_value		5,16
	set_variable		6,11
	enqueue_goal		6,make_term_6_0
	put_reused_func		12,12,+
	write_element_value		12,1,13
	write_element_value		12,2,16
	put_value		2,5
	put_value		3,18
	put_value		5,20
	put_value		7,21
	put_value		9,19
	put_value		10,17
	put_value		13,14
	put_atom		14,no
	put_void		15
	execute		15,case_expansion_15_0
case_expand_clauses_14_25:
	otherwise		case_expand_clauses_14_0
	try_me_else		case_expand_clauses_14_30
	wait_vector		12,3
	read_element		12,0,15
	wait_atom		15,->
	read_elements_inc		12,1,15,2
	create_goal		6
	set_values_inc		1,10,2
	set_marked_value		3,4
	set_marked_value		4,13
	set_marked_value		5,15
	set_variable		6,11
	enqueue_goal		6,make_term_6_0
	put_reused_func		12,12,+
	write_element_value		12,1,13
	write_element_value		12,2,15
	put_value		10,16
	put_value		13,14
	put_atom		14,no
	put_void		15
	execute		15,case_expansion_15_0
case_expand_clauses_14_30:
	otherwise		case_expand_clauses_14_0
	try_me_else		case_expand_clauses_14_35
	wait_vector		12,3
	read_element		12,0,15
	wait_atom		15,;
	read_elements_inc		12,1,15,2
	put_structured_constant		17,'$SCNST_22'
	put_reused_func		12,12,error_message
	write_element_value		12,1,17
	write_element_value		12,2,15
	get_list_val_var		1,15,12,12
	put_value		1,12
	put_value		12,16
	execute		14,case_expand_clauses_14_0
case_expand_clauses_14_35:
	otherwise		case_expand_clauses_14_0
	collect_value		14
	collect_value		13
	collect_value		4
	get_nil		3
	get_nil		5
	get_value		10,11
	get_value		8,9
	get_value		6,7
	put_structured_constant		3,'$SCNST_23'
	put_func		4,3,error_message
	write_element_value		4,1,3
	write_element_value		4,2,12
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
case_expand_clauses_14_40:
	suspend		case_expand_clauses_14_0
	module_entry		kl1cmp_reader
	predicate		convert_case_vector,4
convert_case_vector_4_0:
	try_me_else		convert_case_vector_4_1
	wait_integer		1,0
	put_integer		1,0
	put_atom		5,true
	execute		5,convert_case_vector_5_0
convert_case_vector_4_1:
	suspend		convert_case_vector_4_0
	module_entry		kl1cmp_reader
	predicate		convert_case_vector,5
convert_case_vector_5_0:
	try_me_else		convert_case_vector_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	put_nil		7
	b_set_vector_element		3,6,3,7,6
	put_func		9,3,','
	write_element_variable		9,1,7
	write_element_variable		9,2,8
	get_vector_value		4,9
	b_increment		1,1
	create_goal		5
	set_values_inc		1,1,2
	set_value		3,6
	set_value		4,8
	set_value		5,5
	enqueue_goal		5,convert_case_vector_5_0
	put_value		1,3
	put_value		2,7
	execute		2,convert_case_one_term_2_0
convert_case_vector_5_1:
	try_me_else		convert_case_vector_5_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		4,5
	proceed
convert_case_vector_5_3:
	suspend		convert_case_vector_5_0
	module_entry		kl1cmp_reader
	predicate		convert_case_one_term,2
convert_case_one_term_2_0:
	try_me_else		convert_case_one_term_2_1
	wait_vector		1,3
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,convert_case_one_term_2_1
	bucket_entry_a		->,convert_case_one_term_2_4
	bucket_entry_a		;,convert_case_one_term_2_5
convert_case_one_term_2_4:
	read_elements_inc		1,1,4,2
	put_vector		3,1
	write_element_variable		3,0,6
	put_reused_func		1,1,->
	write_elements_dec		1,1,4,2
	get_vector_value		2,1
	put_values_inc		1,5,2
	execute		2,convert_term_to_vector_2_0
convert_case_one_term_2_5:
	read_element		1,1,8
	read_element		1,2,4
	wait_vector		8,3
	read_element		8,0,5
	wait_atom		5,->
	read_elements_inc		8,1,5,2
	put_vector		3,1
	write_element_variable		3,0,7
	put_reused_func		1,1,->
	write_element_value		1,1,5
	write_element_value		1,2,3
	put_reused_func		3,8,;
	write_element_value		3,1,1
	write_element_variable		3,2,1
	get_vector_value		2,3
	create_goal		2
	set_value		1,4
	set_value		2,1
	enqueue_goal		2,convert_case_one_term_2_0
	put_values_inc		1,6,2
	execute		2,convert_term_to_vector_2_0
convert_case_one_term_2_1:
	suspend		convert_case_one_term_2_0
	module_entry		kl1cmp_reader
	predicate		convert_term_to_vector,2
convert_term_to_vector_2_0:
	put_marked_variable		3,5
	b_new_vector		3,3
	create_goal		5
	set_integer		1,0
	set_value		2,5
	set_variable		3,4
	set_values_dec		4,3,2
	enqueue_goal		5,set_elem_5_0
	put_integer		2,0
	put_value		3,5
	execute		4,length_4_0
convert_term_to_vector_2_1:
	suspend		convert_term_to_vector_2_0
	module_entry		kl1cmp_reader
	predicate		length,4
length_4_0:
	try_me_else		length_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,','
	read_elements_inc		1,1,5,2
	put_reused_func		1,1,','
	write_element_value		1,1,5
	write_element_variable		1,2,5
	get_vector_value		4,1
	b_increment		2,1
	put_value		2,1
	put_value		1,6
	put_value		4,5
	execute		4,length_4_0
length_4_1:
	otherwise		length_4_0
	get_value		1,4
	b_increment		2,1
	get_value		3,1
	proceed
length_4_6:
	suspend		length_4_0
	module_entry		kl1cmp_reader
	predicate		set_elem,5
set_elem_5_0:
	try_me_else		set_elem_5_1
	wait_vector		3,3
	read_element		3,0,6
	wait_atom		6,','
	read_elements_inc		3,1,6,2
	collect_vector		3
	put_marked_value		3,1
	b_set_vector_element		4,3,3,6,4
	b_increment		1,1
	put_value		3,7
	execute		5,set_elem_5_0
set_elem_5_1:
	otherwise		set_elem_5_0
	collect_value		2
	b_set_vector_element		4,1,1,3,2
	get_value		2,5
	proceed
set_elem_5_6:
	suspend		set_elem_5_0
	module_entry		kl1cmp_reader
	predicate		make_term,6
make_term_6_0:
	put_list		8
	write_car_variable		8,7
	write_cdr_value		8,2
	get_list_value		1,8
	put_func		1,3,'|'
	write_elements_inc		1,1,5,2
	put_vector		2,3
	write_elements_inc		2,0,3,2
	write_element_value		2,2,1
	put_value		1,2
	put_value		2,7
	put_void		3
	execute		3,copy_one_term_3_0
make_term_6_1:
	suspend		make_term_6_0
	module_entry		kl1cmp_reader
	predicate		list_variables,4
list_variables_4_0:
	try_me_else		list_variables_4_1
	wait		3
	switch_on_type		3,list_variables_4_2,list_variables_4_3,list_variables_4_4,list_variables_4_5,list_variables_4_6,list_variables_4_7
list_variables_4_4:
	read_car		3,5
	read_cdr		3,6
	collect_list		3
	create_goal		4
	set_values_inc		1,1,2
	set_value		3,6
	set_variable		4,1
	enqueue_goal		4,list_variables_4_0
	put_nil		2
	put_value		3,5
	execute		4,list_variables_4_0
list_variables_4_2:
	put_value		3,4
	execute		3,output_list_3_0
list_variables_4_3:
	put_value		3,4
	execute		3,output_list_3_0
list_variables_4_5:
	test_arity		3,3,list_variables_4_1
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	integer		5
	string		6
	g_string		6,7,8
	wait_integer		8,8
	put_reused_func		3,3,'$VAR'
	write_elements_inc		3,1,5,2
	execute		4,find_or_insert_4_0
list_variables_4_6:
	g_string		3,5,6
	collect_value		3
	put_value		3,4
	execute		3,output_list_3_0
list_variables_4_7:
	is_float		3,list_variables_4_1
	put_value		3,4
	execute		3,output_list_3_0
list_variables_4_1:
	otherwise		list_variables_4_0
	create_goal		4
	set_values_inc		1,1,2
	set_variable		3,1
	set_value		4,4
	enqueue_goal		4,list_variables_4_0
	put_nil		2
	execute		3,get_args_to_list_3_0
list_variables_4_11:
	suspend		list_variables_4_0
	module_entry		kl1cmp_reader
	predicate		get_args_to_list,3
get_args_to_list_3_0:
	try_me_else		get_args_to_list_3_1
	vector		3
	put_value		5,3
	g_vector		5,4
	put_integer		3,0
	execute		5,copy_args_to_list_5_0
get_args_to_list_3_1:
	suspend		get_args_to_list_3_0
	module_entry		kl1cmp_reader
	predicate		copy_args_to_list,5
copy_args_to_list_5_0:
	try_me_else		copy_args_to_list_5_1
	g_diff		3,4
	put_marked_value		6,3
	put_nil		7
	b_set_vector_element		5,6,5,7,6
	get_list_val_var		1,7,5,5
	b_increment		3,1
	put_value		3,1
	put_value		1,5
	put_value		5,6
	execute		5,copy_args_to_list_5_0
copy_args_to_list_5_1:
	try_me_else		copy_args_to_list_5_2
	wait_value		3,4
	collect_value		5
	collect_value		3
	collect_value		4
	get_value		1,2
	proceed
copy_args_to_list_5_2:
	suspend		copy_args_to_list_5_0
	module_entry		kl1cmp_reader
	predicate		find_or_insert,4
find_or_insert_4_0:
	try_me_else		find_or_insert_4_1
	jump_on_non_list_var_var		4,find_or_insert_4_3,5,6
	try_me_else		find_or_insert_4_4
	wait_value		3,5
	collect_value		5
	put_reused_list_val_val		4,4,3,6
	put_value		3,4
	execute		3,output_list_3_0
find_or_insert_4_4:
	try_me_else		find_or_insert_4_1
	g_diff		3,5
	get_reused_list_val_var		1,7,4,5,4
	put_value		1,4
	put_value		4,6
	execute		4,find_or_insert_4_0
find_or_insert_4_3:
	check_nil		4,find_or_insert_4_1
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
find_or_insert_4_1:
	suspend		find_or_insert_4_0
	module_entry		kl1cmp_reader
	predicate		output_list,3
output_list_3_0:
	try_me_else		output_list_3_1
	jump_on_non_list_var_var		3,output_list_3_3,4,5
	get_reused_list_val_var		1,6,3,4,3
	put_value		1,3
	put_value		3,5
	execute		3,output_list_3_0
output_list_3_3:
	check_nil		3,output_list_3_1
	get_value		1,2
	proceed
output_list_3_1:
	suspend		output_list_3_0
	module_entry		kl1cmp_reader
	predicate		intersection,3
intersection_3_0:
	try_me_else		intersection_3_1
	jump_on_non_list_var_var		1,intersection_3_3,4,5
	collect_list		1
	create_goal		4
	set_value		1,3
	set_variable		2,3
	set_marked_value		3,2
	set_value		4,4
	enqueue_goal		4,find_and_insert_4_0
	put_value		1,5
	execute		3,intersection_3_0
intersection_3_3:
	check_nil		1,intersection_3_1
	collect_value		2
	get_nil		3
	proceed
intersection_3_1:
	suspend		intersection_3_0
	module_entry		kl1cmp_reader
	predicate		find_and_insert,4
find_and_insert_4_0:
	try_me_else		find_and_insert_4_1
	jump_on_non_list_var_var		3,find_and_insert_4_3,5,6
	try_me_else		find_and_insert_4_4
	wait_value		4,5
	collect_value		6
	collect_value		5
	put_reused_list_val_val		3,3,4,2
	get_list_value		1,3
	proceed
find_and_insert_4_4:
	try_me_else		find_and_insert_4_1
	g_diff		5,4
	collect_list		3
	collect_value		5
	put_value		3,6
	execute		4,find_and_insert_4_0
find_and_insert_4_3:
	check_nil		3,find_and_insert_4_1
	collect_value		4
	get_value		1,2
	proceed
find_and_insert_4_1:
	suspend		find_and_insert_4_0
	module_entry		kl1cmp_reader
	predicate		copy_one_term,3
copy_one_term_3_0:
	put_value		4,1
	create_goal		3
	set_marked_value		1,4
	set_value		2,2
	set_variable		3,2
	enqueue_goal		3,copy_term_3_0
	create_goal		5
	set_marked_variable		1,1
	set_integer		2,0
	set_value		3,3
	set_variable		4,3
	set_value		5,2
	enqueue_goal		5,table_for_copy_5_0
	create_goal		3
	set_variable		1,2
	set_nil		2
	set_value		3,3
	enqueue_goal		3,herrey_3_0
	create_goal		3
	set_value		1,1
	set_integer		2,0
	set_value		3,2
	enqueue_goal		3,count_variables_3_0
	put_nil		2
	put_value		3,4
	put_nil		4
	execute		4,list_variables_4_0
copy_one_term_3_1:
	suspend		copy_one_term_3_0
	module_entry		kl1cmp_reader
	predicate		table_for_copy,5
table_for_copy_5_0:
	try_me_else		table_for_copy_5_1
	jump_on_non_list_var_var		1,table_for_copy_5_3,9,6
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		9,1,7,2
	collect_list		1
	collect_value		8
	put_marked_value		1,7
	put_marked_variable		10,8
	b_set_vector_element		4,1,4,10,1
	get_value		4,8
	create_goal		5
	set_value		1,6
	set_variable		2,4
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	enqueue_goal		5,table_for_copy_5_0
	put_reused_func		3,9,-
	write_element_value		3,1,2
	write_element_value		3,2,4
	put_func		4,3,-
	write_element_value		4,1,1
	write_element_value		4,2,6
	put_values_dec		1,8,2
	execute		4,case_on_vector_element_4_0
table_for_copy_5_3:
	check_nil		1,table_for_copy_5_1
	get_value		2,3
	get_value		4,5
	proceed
table_for_copy_5_1:
	suspend		table_for_copy_5_0
	module_entry		kl1cmp_reader
	predicate		case_on_vector_element,4
case_on_vector_element_4_0:
	try_me_else		case_on_vector_element_4_1
	jump_on_non_atom		1,case_on_vector_element_4_3
	test_nil		1,case_on_vector_element_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,-
	read_elements_inc		3,1,5,2
	wait_vector		4,3
	read_element		4,0,7
	wait_atom		7,-
	read_element		4,1,1
	read_element		4,2,7
	collect_vector		3
	collect_vector		4
	put_marked_value		3,5
	b_increment		3,3
	get_value		6,3
	b_set_vector_element		1,2,1,5,2
	get_value		2,7
	proceed
case_on_vector_element_4_3:
	is_integer		1,case_on_vector_element_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,-
	read_elements_inc		3,1,5,2
	wait_vector		4,3
	read_element		4,0,7
	wait_atom		7,-
	read_elements_inc		4,1,7,2
	collect_value		2
	collect_vector		3
	collect_vector		4
	get_value		5,6
	get_value		7,8
	proceed
case_on_vector_element_4_1:
	suspend		case_on_vector_element_4_0
	module_entry		kl1cmp_reader
	predicate		copy_term,3
copy_term_3_0:
	try_me_else		copy_term_3_1
	wait		1
	switch_on_type		1,copy_term_3_2,copy_term_3_3,copy_term_3_4,copy_term_3_5,copy_term_3_6,copy_term_3_7
copy_term_3_4:
	read_car		1,4
	read_cdr		1,5
	put_reused_list		7,1
	write_car_variable		7,6
	write_cdr_variable		7,1
	get_list_value		2,7
	create_goal		3
	set_value		1,5
	set_value		2,1
	set_marked_value		3,3
	enqueue_goal		3,copy_term_3_0
	put_value		1,4
	put_value		2,6
	execute		3,copy_term_3_0
copy_term_3_2:
	collect_value		3
	get_value		1,2
	proceed
copy_term_3_3:
	collect_value		3
	get_value		1,2
	proceed
copy_term_3_5:
	test_arity		1,3,copy_term_3_1
	read_element		1,0,4
	wait_atom		4,'$VAR'
	read_elements_inc		1,1,4,2
	integer		4
	string		5
	g_string		5,6,7
	wait_integer		7,8
	vector		3
	g_vector_element		3,4,6
	mark_element		3,4
	collect_value		3
	put_reused_func		1,1,'$VAR'
	write_elements_dec		1,1,6,2
	get_vector_value		2,1
	proceed
copy_term_3_6:
	collect_value		3
	get_value		1,2
	proceed
copy_term_3_7:
	is_float		1,copy_term_3_1
	collect_value		3
	get_value		1,2
	proceed
copy_term_3_1:
	otherwise		copy_term_3_0
	try_me_else		copy_term_3_11
	vector		1
	put_value		6,1
	g_vector		6,1
	put_values_inc		4,2,2
	put_marked_value		2,1
	b_new_vector		3,2
	put_value		2,6
	execute		5,copy_term_args_5_0
copy_term_3_11:
	suspend		copy_term_3_0
	module_entry		kl1cmp_reader
	predicate		copy_term_args,5
copy_term_args_5_0:
	try_me_else		copy_term_args_5_1
	integer		1
	test_integer		1,0,copy_term_args_5_3
	collect_value		5
	collect_value		2
	get_value		3,4
	proceed
copy_term_args_5_3:
	put_integer		6,0
	g_less_than		6,1
	put_marked_variable		6,7
	put_nil		8
	b_set_vector_element		2,6,2,8,6
	put_variable		8,9
	b_set_vector_element		3,7,3,8,8
	b_decrement		1,1
	get_value		7,1
	create_goal		5
	set_values_dec		1,7,2
	set_value		3,8
	set_value		4,4
	set_marked_value		5,5
	enqueue_goal		5,copy_term_args_5_0
	put_value		1,2
	put_value		2,9
	put_value		3,5
	execute		3,copy_term_3_0
copy_term_args_5_1:
	suspend		copy_term_args_5_0
	module_entry		kl1cmp_reader
	predicate		count_variables,3
count_variables_3_0:
	try_me_else		count_variables_3_1
	wait		1
	switch_on_type		1,count_variables_3_2,count_variables_3_3,count_variables_3_4,count_variables_3_5,count_variables_3_6,count_variables_3_7
count_variables_3_4:
	read_car		1,4
	read_cdr		1,5
	collect_list		1
	create_goal		3
	set_value		1,5
	set_variable		2,5
	set_value		3,3
	enqueue_goal		3,count_variables_3_0
	put_value		1,4
	put_value		3,5
	execute		3,count_variables_3_0
count_variables_3_2:
	get_value		2,3
	proceed
count_variables_3_3:
	get_value		2,3
	proceed
count_variables_3_5:
	test_arity		1,3,count_variables_3_1
	read_element		1,0,4
	wait_atom		4,'$VAR'
	read_element		1,1,5
	integer		5
	read_element		1,2,6
	string		6
	integer		2
	try_me_else		count_variables_3_12
	g_not_less_than		5,2
	try_me_else		count_variables_3_1
	g_string		6,7,8
	wait_integer		8,8
	collect_value		6
	collect_vector		1
	b_increment		5,1
	get_value		3,1
	proceed
count_variables_3_12:
	try_me_else		count_variables_3_1
	g_string		6,7,8
	wait_integer		8,8
	collect_value		6
	collect_vector		1
	get_value		2,3
	proceed
count_variables_3_6:
	get_value		2,3
	proceed
count_variables_3_7:
	is_float		1,count_variables_3_1
	get_value		2,3
	proceed
count_variables_3_1:
	otherwise		count_variables_3_0
	try_me_else		count_variables_3_24
	vector		1
	put_value		6,1
	g_vector		6,4
	put_value		7,2
	put_value		5,3
	put_integer		1,0
	put_value		2,4
	put_values_inc		3,6,2
	execute		5,count_variables_args_5_0
count_variables_3_24:
	suspend		count_variables_3_0
	module_entry		kl1cmp_reader
	predicate		count_variables_args,5
count_variables_args_5_0:
	try_me_else		count_variables_args_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	put_void		7
	b_set_vector_element		3,6,3,7,6
	b_increment		1,1
	create_goal		5
	set_values_inc		1,1,2
	set_value		3,6
	set_variable		4,6
	set_value		5,5
	enqueue_goal		5,count_variables_args_5_0
	put_values_inc		1,3,2
	put_value		3,6
	execute		3,count_variables_3_0
count_variables_args_5_1:
	try_me_else		count_variables_args_5_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		4,5
	proceed
count_variables_args_5_3:
	suspend		count_variables_args_5_0
	module_entry		kl1cmp_reader
	predicate		bell,2
bell_2_0:
	put_structured_constant		3,'$SCNST_24'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
bell_2_1:
	suspend		bell_2_0
	module_entry		kl1cmp_reader
	predicate		herrey,3
herrey_3_0:
	try_me_else		herrey_3_1
	wait_integer		2,0
	b_new_vector		1,1
	get_value		1,3
	proceed
herrey_3_1:
	otherwise		herrey_3_0
	put_value		5,2
	put_value		4,3
	put_marked_value		2,1
	b_new_vector		2,2
	put_value		3,5
	execute		4,initialize_vector_4_0
herrey_3_6:
	suspend		herrey_3_0
	module_entry		kl1cmp_reader
	predicate		initialize_vector,4
initialize_vector_4_0:
	try_me_else		initialize_vector_4_1
	wait_integer		1,0
	collect_value		3
	get_value		2,4
	proceed
initialize_vector_4_1:
	otherwise		initialize_vector_4_0
	b_decrement		1,1
	put_marked_value		5,1
	put_marked_value		6,3
	b_set_vector_element		2,5,2,6,5
	put_value		2,5
	execute		4,initialize_vector_4_0
initialize_vector_4_6:
	suspend		initialize_vector_4_0
	module_entry		kl1cmp_reader
	predicate		functor,3
functor_3_0:
	try_me_else		functor_3_1
	wait		1
	switch_on_type		1,functor_3_2,functor_3_1,functor_3_3,functor_3_4,functor_3_1,functor_3_1
functor_3_3:
	read_car		1,4
	read_cdr		1,5
	collect_list		1
	collect_value		5
	collect_value		4
	get_atom		2,'.'
	get_integer		3,2
	proceed
functor_3_2:
	get_value		2,1
	get_integer		3,0
	proceed
functor_3_4:
	g_vector		1,4
	put_integer		6,0
	g_vector_element		1,6,5
	atom		5
	mark_element		1,6
	collect_value		1
	get_value		2,5
	b_decrement		4,1
	get_value		3,1
	proceed
functor_3_1:
	suspend		functor_3_0
	module_entry		kl1cmp_reader
	predicate		gen_functor,3
gen_functor_3_0:
	try_me_else		gen_functor_3_1
	wait_atom		2,'.'
	wait_integer		3,2
	put_list		2
	write_car_void		2
	write_cdr_void		2
	get_list_value		1,2
	proceed
gen_functor_3_1:
	otherwise		gen_functor_3_0
	put_value		4,1
	b_increment		3,1
	put_marked_value		3,1
	b_new_vector		3,3
	put_integer		5,0
	b_set_vector_element		3,5,2,2,3
	put_values_inc		2,3,2
	execute		3,replace_element_with_undef_3_0
gen_functor_3_6:
	suspend		gen_functor_3_0
	module_entry		kl1cmp_reader
	predicate		replace_element_with_undef,3
replace_element_with_undef_3_0:
	try_me_else		replace_element_with_undef_3_1
	integer		1
	test_integer		1,1,replace_element_with_undef_3_3
	get_value		2,3
	proceed
replace_element_with_undef_3_3:
	put_integer		4,1
	g_less_than		4,1
	b_decrement		1,1
	put_marked_value		4,1
	put_void		5
	b_set_vector_element		2,4,2,5,4
	put_value		2,4
	execute		3,replace_element_with_undef_3_0
replace_element_with_undef_3_1:
	suspend		replace_element_with_undef_3_0
	begin_const_section		kl1cmp_reader
'$SCNST_0_0':
	define_desc		19,2
	define_integer		1664183403
	define_integer		28781
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putt
	define_atom		:
'$SCNST_2':
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_3_1':
	define_desc		3,7
	define_integer		1634890867
	define_integer		543516526
	define_integer		542060361
	define_integer		1936942445
	define_integer		543516513
	define_integer		1853189990
	define_integer		540680292
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		27,1
	define_integer		36
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		27,1
	define_integer		47
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_6_0':
	define_desc		27,1
	define_integer		95
'$SCNST_6':
	define_string		'$SCNST_6_0'
'$SCNST_7_0':
	define_desc		19,8
	define_integer		1702128737
	define_integer		1952542322
	define_integer		1818588777
	define_integer		1868963961
	define_integer		543452789
	define_integer		1701999209
	define_integer		1634891111
	define_integer		31084
'$SCNST_7':
	define_string		'$SCNST_7_0'
'$SCNST_8_0':
	define_desc		19,7
	define_integer		1701344367
	define_integer		1936291698
	define_integer		1868963941
	define_integer		543452789
	define_integer		1701999209
	define_integer		1634891111
	define_integer		31084
'$SCNST_8':
	define_string		'$SCNST_8_0'
'$SCNST_9_0':
	define_desc		0,3
	define_atom		-
	define_atom		mri_wins
	define_atom		alternatively
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_10_0':
	define_desc		0,3
	define_atom		-
	define_atom		upmail_wins
	define_atom		end_of_file
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_11_0':
	define_desc		0,3
	define_atom		-
	define_atom		icot_wins
	define_atom		otherwise
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_12_0':
	define_desc		11,7
	define_integer		1835888451
	define_integer		1864397929
	define_integer		1634887024
	define_integer		544370548
	define_integer		544501614
	define_integer		1853189990
	define_integer		3809380
'$SCNST_15':
'$SCNST_13':
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_14_0':
	define_desc		0,3
	define_atom		'|'
	define_atom		true
	define_atom		true
'$SCNST_16':
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_17_0':
	define_desc		27,8
	define_integer		1936287828
	define_integer		1919251488
	define_integer		1936269421
	define_integer		1953459744
	define_integer		827083552
	define_integer		1634493216
	define_integer		543519605
	define_integer		58
'$SCNST_17':
	define_string		'$SCNST_17_0'
'$SCNST_18_1':
	define_desc		0,2
	define_atom		:-
	define_atom		local_implicit
'$SCNST_18_0':
	define_desc		0,3
	define_atom		-
	define_vector		'$SCNST_18_1'
	define_atom		directive
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_19_0':
	define_desc		3,7
	define_integer		1635151433
	define_integer		543451500
	define_integer		1819307369
	define_integer		1953063785
	define_integer		1667589152
	define_integer		1634885996
	define_integer		1852795252
'$SCNST_19':
	define_string		'$SCNST_19_0'
'$SCNST_20_1':
	define_desc		19,8
	define_integer		1702128737
	define_integer		1952542322
	define_integer		1818588777
	define_integer		1868963961
	define_integer		543452789
	define_integer		1701999209
	define_integer		1634497895
	define_integer		31090
'$SCNST_20_0':
	define_desc		0,3
	define_atom		error_message
	define_string		'$SCNST_20_1'
	define_atom		[]
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_1':
	define_desc		19,7
	define_integer		1701344367
	define_integer		1936291698
	define_integer		1868963941
	define_integer		543452789
	define_integer		1701999209
	define_integer		1634497895
	define_integer		31090
'$SCNST_21_0':
	define_desc		0,3
	define_atom		error_message
	define_string		'$SCNST_21_1'
	define_atom		[]
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_0':
	define_desc		27,4
	define_integer		1701604425
	define_integer		543973735
	define_integer		1702060387
	define_integer		46
'$SCNST_23':
'$SCNST_22':
	define_string		'$SCNST_22_0'
'$SCNST_24_0':
	define_desc		0,2
	define_atom		ttyput
	define_integer		7
'$SCNST_24':
	define_vector		'$SCNST_24_0'
