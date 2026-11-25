mpimos_utility:
	module		mpimos_utility
	entry		melt,3,melt_3_0
	entry		freeze,2,freeze_2_0
	entry		get_predicate,3,get_predicate_3_0
	entry		write,1,write_1_0
	entry		symbol_append,2,symbol_append_2_0
	entry		string_append,2,string_append_2_0
	entry		symbol_to_string,2,symbol_to_string_2_0
	entry		pathname,3,pathname_3_0
	entry		extend_name,3,extend_name_3_0
	entry		compress,2,compress_2_0
	entry		integer_to_string,2,integer_to_string_2_0
	entry		qsort,2,qsort_2_0
	entry		qsort,3,qsort_3_0
	entry		qsortv,3,qsortv_3_0
	entry		qsortv,4,qsortv_4_0
	entry		report_tokens,3,report_tokens_3_0
	entry		report_tokens,2,report_tokens_2_0
	entry		copy_string_elements,7,copy_string_elements_7_0
	entry		append_string,2,append_string_2_0
	module_entry		mpimos_utility
	predicate		melt,3
melt_3_0:
	try_me_else		melt_3_1
	integer		2
	test_integer		2,0,melt_3_3
	get_value		3,1
	proceed
melt_3_3:
	put_integer		4,0
	g_less_than		4,2
	put_marked_value		4,2
	b_new_vector		4,4
	create_goal		3
	set_integer		1,0
	set_value		2,2
	set_variable		3,6
	enqueue_goal		3,unify_variables_table_entry_3_0
	create_goal		5
	set_value		1,1
	set_value		2,3
	set_variable		3,5
	set_value		4,6
	set_value		5,2
	enqueue_goal		5,melt_term_5_0
	put_integer		1,0
	put_values_inc		3,4,2
	execute		4,set_empty_4_0
melt_3_1:
	suspend		melt_3_0
	module_entry		mpimos_utility
	predicate		set_empty,4
set_empty_4_0:
	try_me_else		set_empty_4_1
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_value		4,3
	proceed
set_empty_4_1:
	try_me_else		set_empty_4_2
	g_diff		1,2
	put_marked_value		5,1
	b_increment		5,5
	put_nil		6
	b_set_vector_element		3,1,1,6,3
	put_value		1,5
	execute		4,set_empty_4_0
set_empty_4_2:
	suspend		set_empty_4_0
	module_entry		mpimos_utility
	predicate		melt_term,5
melt_term_5_0:
	try_me_else		melt_term_5_1
	wait		1
	switch_on_type		1,melt_term_5_2,melt_term_5_3,melt_term_5_4,melt_term_5_5,melt_term_5_6,melt_term_5_7
melt_term_5_4:
	read_car		1,6
	read_cdr		1,7
	put_reused_list		9,1
	write_car_variable		9,8
	write_cdr_variable		9,1
	get_list_value		2,9
	create_goal		5
	set_value		1,7
	set_value		2,1
	set_variable		3,7
	set_value		4,4
	set_marked_value		5,5
	enqueue_goal		5,melt_term_5_0
	put_value		1,6
	put_value		2,8
	put_value		4,7
	execute		5,melt_term_5_0
melt_term_5_2:
	collect_value		5
	get_value		2,1
	get_value		4,3
	proceed
melt_term_5_3:
	collect_value		5
	get_value		2,1
	get_value		4,3
	proceed
melt_term_5_5:
	test_arity		1,3,melt_term_5_1
	read_element		1,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		1,1,6,2
	integer		6
	put_integer		8,0
	g_not_less_than		6,8
	integer		5
	g_less_than		6,5
	string		7
	g_string		7,8,9
	wait_integer		9,8
	collect_value		7
	collect_vector		1
	put_value		1,6
	execute		4,enter_4_0
melt_term_5_6:
	collect_value		5
	get_value		2,1
	get_value		4,3
	proceed
melt_term_5_7:
	is_float		1,melt_term_5_1
	collect_value		5
	get_value		2,1
	get_value		4,3
	proceed
melt_term_5_1:
	otherwise		melt_term_5_0
	try_me_else		melt_term_5_11
	vector		1
	put_value		9,1
	g_vector		9,6
	put_values_inc		10,3,2
	put_value		7,5
	put_value		8,2
	put_marked_value		1,6
	b_new_vector		4,1
	put_integer		1,0
	put_value		2,6
	put_value		3,9
	put_values_inc		5,10,2
	execute		8,melt_args_8_0
melt_term_5_11:
	suspend		melt_term_5_0
	module_entry		mpimos_utility
	predicate		melt_args,8
melt_args_8_0:
	try_me_else		melt_args_8_1
	wait_value		1,2
	collect_value		7
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		8,4
	get_value		6,5
	proceed
melt_args_8_1:
	otherwise		melt_args_8_0
	put_marked_value		9,1
	b_increment		9,9
	put_nil		10
	b_set_vector_element		3,1,3,10,10
	put_variable		12,11
	b_set_vector_element		4,1,1,12,4
	create_goal		8
	set_value		1,9
	set_value		2,2
	set_value		3,10
	set_value		4,4
	set_variable		5,4
	set_value		6,6
	set_marked_value		7,7
	set_value		8,8
	enqueue_goal		8,melt_args_8_0
	put_value		1,3
	put_value		2,11
	put_value		3,5
	put_value		5,7
	execute		5,melt_term_5_0
melt_args_8_3:
	suspend		melt_args_8_0
	module_entry		mpimos_utility
	predicate		enter,4
enter_4_0:
	put_list_val_var		5,2,2
	b_set_vector_element		3,1,1,5,3
	get_value		1,2
	get_value		3,4
	proceed
enter_4_1:
	suspend		enter_4_0
	module_entry		mpimos_utility
	predicate		unify_variables_table_entry,3
unify_variables_table_entry_3_0:
	try_me_else		unify_variables_table_entry_3_1
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	proceed
unify_variables_table_entry_3_1:
	otherwise		unify_variables_table_entry_3_0
	put_marked_value		4,1
	b_increment		4,4
	put_void		5
	b_set_vector_element		3,1,1,5,3
	create_goal		3
	set_value		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,unify_variables_table_entry_3_0
	execute		1,unify_elements_1_0
unify_variables_table_entry_3_3:
	suspend		unify_variables_table_entry_3_0
	module_entry		mpimos_utility
	predicate		unify_elements,1
unify_elements_1_0:
	try_me_else		unify_elements_1_1
	wait_list_var_var		1,2,3
	jump_on_non_list_var_var		3,unify_elements_1_4,4,5
	jump_on_non_list		5,unify_elements_1_6
	collect_list		3
	put_marked_value		4,4
	get_value		4,2
	put_reused_list_val_val		1,1,4,5
	execute		1,unify_elements_1_0
unify_elements_1_6:
	check_nil		5,unify_elements_1_1
	collect_list		1
	collect_list		3
	get_value		2,4
	proceed
unify_elements_1_4:
	check_nil		3,unify_elements_1_1
	collect_list		1
	collect_value		2
	proceed
unify_elements_1_1:
	suspend		unify_elements_1_0
	module_entry		mpimos_utility
	predicate		freeze,2
freeze_2_0:
	create_goal		3
	set_variable		1,4
	set_variable		2,3
	set_value		3,2
	enqueue_goal		3,wait_freeze_3_0
	put_value		2,3
	put_integer		3,0
	put_nil		5
	put_void		6
	put_atom		7,di
	put_integer		8,200
	execute		8,freeze_8_0
freeze_2_1:
	suspend		freeze_2_0
	module_entry		mpimos_utility
	predicate		wait_freeze,3
wait_freeze_3_0:
	try_me_else		wait_freeze_3_1
	wait		1
	get_value		3,2
	proceed
wait_freeze_3_1:
	suspend		wait_freeze_3_0
	module_entry		mpimos_utility
	predicate		freeze,8
freeze_8_0:
	try_me_else		freeze_8_1
	integer		8
	try_me_else		freeze_8_3
	put_integer		9,0
	g_not_less_than		8,9
	b_unbound2		1,1
	execute		8,wait_unbound_result_8_0
freeze_8_3:
	collect_value		7
	collect_value		1
	get_atom		2,...
	get_value		4,3
	get_value		6,5
	proceed
freeze_8_1:
	suspend		freeze_8_0
	module_entry		mpimos_utility
	predicate		wait_unbound_result,8
wait_unbound_result_8_0:
	try_me_else		wait_unbound_result_8_1
	vector		1
	jump_on_arity		1,4,wait_unbound_result_8_1
	table_entry		wait_unbound_result_8_1
	table_entry		wait_unbound_result_8_3
	table_entry		wait_unbound_result_8_1
	table_entry		wait_unbound_result_8_4
wait_unbound_result_8_3:
	read_element		1,0,9
	collect_vector		1
	put_value		1,9
	execute		8,unify_8_0
wait_unbound_result_8_4:
	read_elements_inc		1,0,9,3
	collect_value		8
	collect_value		7
	collect_value		11
	collect_value		9
	put_reused_func		7,1,'$VAR'
	write_element_marked_value		7,1,10
	write_element_variable		7,2,1
	get_vector_value		2,7
	create_goal		2
	set_variable		1,7
	set_value		2,1
	enqueue_goal_external		mpimos_unparser,make_variable_name,2
	put_value		1,10
	put_values_inc		2,3,5
	execute		6,get_variable_number_6_0
wait_unbound_result_8_1:
	suspend		wait_unbound_result_8_0
	module_entry		mpimos_utility
	predicate		get_variable_number,6
get_variable_number_6_0:
	try_me_else		get_variable_number_6_1
	jump_on_non_list		4,get_variable_number_6_3
	read_car		4,7
	wait_vector		7,2
	read_elements_inc		7,0,8,2
	read_cdr		4,10
	try_me_else		get_variable_number_6_5
	wait_value		1,8
	collect_value		8
	put_marked_value		9,9
	get_value		9,6
	get_value		3,2
	put_reused_vector		2,7
	write_element_value		2,0,1
	write_element_value		2,1,9
	put_reused_list_val_val		1,4,2,10
	get_list_value		5,1
	proceed
get_variable_number_6_5:
	try_me_else		get_variable_number_6_1
	g_diff		1,8
	put_reused_vector		7,7
	write_elements_inc		7,0,8,2
	get_reused_list_val_var		5,4,4,7,7
	put_value		4,10
	put_value		5,7
	execute		6,get_variable_number_6_0
get_variable_number_6_3:
	check_nil		4,get_variable_number_6_1
	put_marked_value		2,2
	put_marked_value		6,6
	get_value		2,6
	b_increment		2,2
	get_value		3,2
	put_vector		2,2
	write_element_value		2,0,1
	write_element_value		2,1,6
	put_list		1
	write_car_value		1,2
	write_cdr_nil		1
	get_list_value		5,1
	proceed
get_variable_number_6_1:
	suspend		get_variable_number_6_0
	module_entry		mpimos_utility
	predicate		unify,8
unify_8_0:
	try_me_else		unify_8_1
	jump_on_non_list_var_var		1,unify_8_3,9,10
	put_marked_value		11,8
	b_decrement		11,11
	put_integer		12,2
	b_subtract		8,12,8
	put_reused_list		13,1
	write_car_variable		13,12
	write_cdr_variable		13,1
	get_list_value		2,13
	create_goal		8
	set_value		1,10
	set_value		2,1
	set_variable		3,13
	set_value		4,4
	set_variable		5,10
	set_value		6,6
	set_marked_value		7,7
	set_value		8,11
	enqueue_goal		8,freeze_8_0
	put_value		1,9
	put_value		2,12
	put_value		4,13
	put_value		6,10
	execute		8,freeze_8_0
unify_8_3:
	is_vector		1,unify_8_1
	put_value		13,1
	g_vector		13,9
	put_value		12,8
	put_value		14,3
	put_value		8,5
	put_value		15,6
	put_value		10,7
	put_marked_value		1,12
	put_integer		3,2
	b_subtract		1,3,1
	put_value		11,1
	put_marked_value		1,9
	b_new_vector		5,1
	create_goal		5
	set_variable		1,6
	set_value		2,2
	set_variable		3,7
	set_value		4,4
	set_marked_value		5,10
	enqueue_goal		5,unify_variable_5_0
	put_integer		1,0
	put_value		2,9
	put_value		3,13
	put_values_inc		4,5,2
	put_value		6,14
	put_value		9,15
	execute		12,unify_vector_12_0
unify_8_1:
	otherwise		unify_8_0
	collect_value		8
	collect_value		7
	get_value		2,1
	get_value		4,3
	get_value		6,5
	proceed
unify_8_7:
	suspend		unify_8_0
	module_entry		mpimos_utility
	predicate		unify_vector,12
unify_vector_12_0:
	try_me_else		unify_vector_12_1
	integer		1
	integer		2
	integer		12
	g_less_than		1,2
	try_me_else		unify_vector_12_5
	put_integer		13,0
	g_not_less_than		12,13
	put_marked_value		13,1
	put_nil		14
	b_set_vector_element		3,13,3,14,13
	put_variable		14,15
	b_set_vector_element		4,1,4,14,14
	b_increment		1,1
	b_decrement		12,4
	create_goal		12
	set_values_inc		1,1,2
	set_values_inc		3,13,2
	set_value		5,5
	set_variable		6,5
	set_value		7,7
	set_variable		8,7
	set_value		9,9
	set_marked_value		10,10
	set_marked_value		11,11
	set_value		12,4
	enqueue_goal		12,unify_vector_12_0
	put_value		1,3
	put_value		2,15
	put_values_dec		3,6,2
	put_values_dec		5,8,2
	put_values_inc		7,10,2
	execute		8,freeze_8_0
unify_vector_12_5:
	collect_value		11
	put_integer		11,-1
	put_integer		12,1000000
	execute		12,unify_vector_12_0
unify_vector_12_1:
	try_me_else		unify_vector_12_6
	wait_value		1,2
	collect_value		12
	collect_value		11
	collect_value		10
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,4
	get_value		7,6
	get_value		9,8
	proceed
unify_vector_12_6:
	suspend		unify_vector_12_0
	module_entry		mpimos_utility
	predicate		unify_variable,5
unify_variable_5_0:
	try_me_else		unify_variable_5_1
	vector		1
	jump_on_arity		1,4,unify_variable_5_1
	table_entry		unify_variable_5_1
	table_entry		unify_variable_5_1
	table_entry		unify_variable_5_3
	table_entry		unify_variable_5_4
unify_variable_5_3:
	read_element		1,0,6
	wait_atom		6,'$VAR'
	read_element		1,1,7
	integer		7
	atom		5
	branch_on_atom		5,2,unify_variable_5_1
	bucket_entry_a		di,unify_variable_5_8
	bucket_entry_a		no,unify_variable_5_9
unify_variable_5_8:
	put_integer		5,2
	b_new_vector		5,5
	put_integer		6,0
	put_integer		8,1346655059
	b_set_vector_element		5,6,5,8,6
	put_integer		5,1
	put_reused_func		1,1,'$VAR'
	write_element_value		1,1,7
	b_set_vector_element		6,5,1,1,5
	get_value		5,2
	get_value		4,3
	proceed
unify_variable_5_9:
	put_reused_func		1,1,'$VAR'
	write_element_value		1,1,7
	get_vector_value		2,1
	get_value		4,3
	proceed
unify_variable_5_4:
	read_element		1,0,6
	wait_atom		6,'$VAR'
	read_element		1,1,7
	integer		7
	read_element		1,2,8
	string		8
	atom		5
	branch_on_atom		5,2,unify_variable_5_1
	bucket_entry_a		di,unify_variable_5_14
	bucket_entry_a		no,unify_variable_5_15
unify_variable_5_14:
	g_string		8,9,10
	wait_integer		10,8
	put_integer		5,2
	b_new_vector		5,5
	put_integer		6,0
	put_integer		9,1346655059
	b_set_vector_element		5,6,5,9,6
	put_integer		5,1
	put_reused_func		1,1,'$VAR'
	write_elements_inc		1,1,7,2
	b_set_vector_element		6,5,1,1,5
	get_value		5,2
	get_value		4,3
	proceed
unify_variable_5_15:
	g_string		8,9,10
	wait_integer		10,8
	put_reused_func		1,1,'$VAR'
	write_elements_inc		1,1,7,2
	get_vector_value		2,1
	get_value		4,3
	proceed
unify_variable_5_1:
	otherwise		unify_variable_5_0
	collect_value		5
	get_value		2,1
	get_value		4,3
	proceed
unify_variable_5_31:
	suspend		unify_variable_5_0
	module_entry		mpimos_utility
	predicate		get_predicate,3
get_predicate_3_0:
	try_me_else		get_predicate_3_1
	wait_vector		1,3
	read_element		1,0,4
	wait_atom		4,:
	read_elements_inc		1,1,5,2
	jump_on_non_atom		6,get_predicate_3_5
	put_reused_vector		1,1
	write_elements_inc		1,0,5,2
	write_element_integer		1,2,0
	get_vector_value		2,1
	put_vector		1,0
	get_vector_value		3,1
	proceed
get_predicate_3_5:
	is_vector		6,get_predicate_3_1
	g_vector		6,4
	put_value		7,3
	b_decrement		4,3
	put_reused_vector		4,1
	write_element_value		4,0,5
	write_element_variable		4,1,1
	write_element_marked_value		4,2,3
	get_vector_value		2,4
	b_new_vector		4,3
	put_integer		2,0
	put_nil		5
	b_set_vector_element		6,2,2,5,5
	get_value		2,1
	put_integer		1,0
	put_value		2,3
	put_value		3,5
	put_value		5,7
	execute		5,copy_args_5_0
get_predicate_3_1:
	otherwise		get_predicate_3_0
	collect_value		3
	collect_value		2
	put_integer		6,262144
	put_atom		7,warning
	put_structured_constant		2,'$SCNST_0'
	put_func		3,2,putt
	write_element_variable		3,1,5
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_1'
	put_list_val_val		3,2,4
	b_raise		6,7,3
	put_value		2,5
	execute_external		mpimos_utility,freeze,2
get_predicate_3_15:
	suspend		get_predicate_3_0
	module_entry		mpimos_utility
	predicate		copy_args,5
copy_args_5_0:
	try_me_else		copy_args_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	b_increment		6,6
	put_marked_value		7,6
	put_nil		8
	b_set_vector_element		3,7,3,8,7
	b_set_vector_element		4,1,1,3,4
	put_value		1,6
	put_value		3,7
	execute		5,copy_args_5_0
copy_args_5_1:
	try_me_else		copy_args_5_3
	wait		4
	wait_value		1,2
	collect_value		3
	collect_value		1
	get_value		5,4
	proceed
copy_args_5_3:
	suspend		copy_args_5_0
	module_entry		mpimos_utility
	predicate		write,1
write_1_0:
	try_me_else		write_1_1
	jump_on_non_list_var_var		1,write_1_3,2,3
	wait		2
	display_console		2
	collect_list		1
	collect_value		2
	put_value		1,3
	execute		1,write_1_0
write_1_3:
	check_nil		1,write_1_1
	proceed
write_1_1:
	otherwise		write_1_0
	try_me_else		write_1_8
	wait		1
	display_console		1
	collect_value		1
	proceed
write_1_8:
	suspend		write_1_0
	module_entry		mpimos_utility
	predicate		symbol_append,2
symbol_append_2_0:
	b_intern_atom		2,2
	create_goal		2
	set_variable		1,3
	set_value		2,2
	enqueue_goal		2,string_append_2_0
	put_value		2,3
	execute		2,symbol_to_string_2_0
symbol_append_2_1:
	suspend		symbol_append_2_0
	module_entry		mpimos_utility
	predicate		symbol_to_string,2
symbol_to_string_2_0:
	try_me_else		symbol_to_string_2_1
	jump_on_non_list_var_var		1,symbol_to_string_2_3,3,4
	b_atom_name		3,3
	get_reused_list_val_var		2,1,1,3,3
	put_values_dec		1,4,2
	execute		2,symbol_to_string_2_0
symbol_to_string_2_3:
	check_nil		1,symbol_to_string_2_1
	get_nil		2
	proceed
symbol_to_string_2_1:
	suspend		symbol_to_string_2_0
	module_entry		mpimos_utility
	predicate		string_append,2
string_append_2_0:
	put_value		3,2
	put_integer		2,0
	execute		3,string_append_3_0
string_append_2_1:
	suspend		string_append_2_0
	module_entry		mpimos_utility
	predicate		string_append,3
string_append_3_0:
	try_me_else		string_append_3_1
	jump_on_non_list_var_var		1,string_append_3_3,4,5
	wait_integer		2,0
	collect_list		1
	put_values_dec		1,5,2
	execute		3,string_append_3_0
string_append_3_3:
	check_nil		1,string_append_3_1
	get_value		3,2
	proceed
string_append_3_1:
	otherwise		string_append_3_0
	try_me_else		string_append_3_8
	wait_list_var_var		1,4,5
	collect_list		1
	b_append_string		2,4,2
	put_value		1,5
	execute		3,string_append_3_0
string_append_3_8:
	suspend		string_append_3_0
	module_entry		mpimos_utility
	predicate		pathname,3
pathname_3_0:
	try_me_else		pathname_3_1
	string		1
	g_string		1,4,5
	wait_integer		5,8
	create_goal		3
	set_variable		1,4
	set_variable		2,5
	set_value		3,3
	enqueue_goal		3,pathname1_3_0
	create_goal		2
	set_value		1,2
	set_value		2,5
	enqueue_goal		2,compress_2_0
	put_value		2,4
	execute		2,compress_2_0
pathname_3_1:
	otherwise		pathname_3_0
	put_integer		6,262144
	put_atom		7,warning
	put_structured_constant		4,'$SCNST_2'
	put_func		5,2,putt
	write_element_value		5,1,1
	put_list_val_val		1,5,4
	put_structured_constant		4,'$SCNST_3'
	put_list_val_val		5,4,1
	b_raise		6,7,5
	create_goal		3
	put_structured_constant		1,'$SCNST_4'
	set_value		1,1
	set_variable		2,4
	set_value		3,3
	enqueue_goal		3,pathname1_3_0
	put_value		1,2
	put_value		2,4
	execute		2,compress_2_0
pathname_3_5:
	suspend		pathname_3_0
	module_entry		mpimos_utility
	predicate		pathname1,3
pathname1_3_0:
	try_me_else		pathname1_3_1
	string		2
	try_me_else		pathname1_3_3
	put_integer		4,0
	g_string_element		2,4,4
	wait_integer		4,47
	collect_value		1
	get_value		3,2
	proceed
pathname1_3_3:
	try_me_else		pathname1_3_1
	put_integer		4,0
	g_string_element		2,4,4
	wait_integer		4,126
	collect_value		1
	get_value		3,2
	proceed
pathname1_3_1:
	otherwise		pathname1_3_0
	try_me_else		pathname1_3_6
	string		1
	g_string		1,4,5
	wait_integer		5,8
	g_decrement		4,4
	g_string_element		1,4,4
	wait_integer		4,47
	b_append_string		1,2,1
	get_value		1,3
	proceed
pathname1_3_6:
	otherwise		pathname1_3_0
	put_structured_constant		4,'$SCNST_5'
	b_append_string		1,4,1
	b_append_string		1,2,1
	get_value		1,3
	proceed
pathname1_3_10:
	suspend		pathname1_3_0
	module_entry		mpimos_utility
	predicate		extend_name,3
extend_name_3_0:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,extend_3_0
	put_value		2,4
	execute		2,compress_2_0
extend_name_3_1:
	suspend		extend_name_3_0
	module_entry		mpimos_utility
	predicate		extend,3
extend_3_0:
	try_me_else		extend_3_1
	string		1
	g_string		1,4,5
	wait_integer		5,8
	b_decrement		4,4
	execute		4,extend_4_0
extend_3_1:
	suspend		extend_3_0
	module_entry		mpimos_utility
	predicate		extend,4
extend_4_0:
	try_me_else		extend_4_1
	string		1
	integer		4
	try_me_else		extend_4_4
	g_string_element		1,4,5
	wait_integer		5,46
	collect_value		2
	get_value		3,1
	proceed
extend_4_4:
	try_me_else		extend_4_1
	g_string_element		1,4,5
	wait_integer		5,47
	put_structured_constant		4,'$SCNST_6'
	b_append_string		1,4,1
	b_append_string		1,2,1
	get_value		1,3
	proceed
extend_4_1:
	try_me_else		extend_4_5
	integer		4
	put_integer		5,0
	g_less_than		4,5
	put_structured_constant		4,'$SCNST_7'
	b_append_string		1,4,1
	b_append_string		1,2,1
	get_value		1,3
	proceed
extend_4_5:
	otherwise		extend_4_0
	b_decrement		4,4
	execute		4,extend_4_0
extend_4_11:
	suspend		extend_4_0
	module_entry		mpimos_utility
	predicate		compress,2
compress_2_0:
	put_value		3,2
	put_integer		2,0
	put_integer		4,0
	execute		4,compress_4_0
compress_2_1:
	suspend		compress_2_0
	module_entry		mpimos_utility
	predicate		compress,4
compress_4_0:
	try_me_else		compress_4_1
	string		1
	integer		2
	try_me_else		compress_4_4
	g_string_element		1,2,5
	wait_integer		5,32
	b_increment		2,2
	execute		4,compress_4_0
compress_4_4:
	try_me_else		compress_4_5
	g_string_element		1,2,5
	wait_integer		5,9
	b_increment		2,2
	execute		4,compress_4_0
compress_4_5:
	try_me_else		compress_4_6
	g_string_element		1,2,5
	put_integer		6,32
	g_diff		5,6
	put_integer		6,9
	g_diff		5,6
	put_variable		7,6
	put_marked_value		8,4
	b_set_string_element		7,8,5,5
	get_value		5,3
	b_increment		2,2
	b_increment		4,3
	put_value		4,3
	put_value		3,6
	execute		4,compress_4_0
compress_4_6:
	try_me_else		compress_4_1
	g_string		1,6,5
	wait_value		6,2
	collect_value		1
	put_integer		1,8
	b_new_string		1,4,1
	get_value		1,3
	proceed
compress_4_1:
	suspend		compress_4_0
	module_entry		mpimos_utility
	predicate		integer_to_string,2
integer_to_string_2_0:
	try_me_else		integer_to_string_2_1
	integer		1
	test_integer		1,0,integer_to_string_2_3
	put_structured_constant		1,'$SCNST_8'
	get_value		2,1
	proceed
integer_to_string_2_3:
	try_me_else		integer_to_string_2_4
	put_integer		3,0
	g_less_than		3,1
	create_goal		4
	set_integer		1,1
	set_variable		2,4
	set_variable		3,3
	set_value		4,2
	enqueue_goal		4,element_list_to_string_4_0
	put_value		2,4
	put_integer		4,0
	execute		4,integer_to_element_list_4_0
integer_to_string_2_4:
	try_me_else		integer_to_string_2_1
	put_integer		3,0
	g_less_than		1,3
	b_minus		1,1
	create_goal		4
	set_integer		1,0
	set_variable		2,4
	set_variable		3,3
	set_value		4,2
	enqueue_goal		4,element_list_to_string_4_0
	put_value		2,4
	put_integer		4,0
	execute		4,integer_to_element_list_4_0
integer_to_string_2_1:
	suspend		integer_to_string_2_0
	module_entry		mpimos_utility
	predicate		element_list_to_string,4
element_list_to_string_4_0:
	try_me_else		element_list_to_string_4_1
	integer		1
	jump_on_integer		1,2,element_list_to_string_4_1
	table_entry		element_list_to_string_4_3
	table_entry		element_list_to_string_4_4
element_list_to_string_4_3:
	b_increment		3,1
	put_value		5,1
	put_marked_value		1,5
	put_integer		3,8
	b_new_string		3,1,3
	put_variable		1,6
	put_integer		7,0
	put_integer		8,45
	b_set_string_element		1,7,8,1
	get_value		1,4
	put_value		1,2
	put_value		2,5
	put_value		4,6
	execute		4,element_list_to_string0_4_0
element_list_to_string_4_4:
	put_marked_value		1,3
	put_integer		5,8
	b_new_string		5,1,5
	put_values_inc		1,2,2
	put_value		3,5
	execute		4,element_list_to_string0_4_0
element_list_to_string_4_1:
	suspend		element_list_to_string_4_0
	module_entry		mpimos_utility
	predicate		element_list_to_string0,4
element_list_to_string0_4_0:
	try_me_else		element_list_to_string0_4_1
	jump_on_non_list_var_var		1,element_list_to_string0_4_3,5,6
	collect_list		1
	put_integer		1,48
	b_add		1,5,1
	b_decrement		2,2
	put_marked_value		5,2
	b_set_string_element		3,5,1,3
	put_value		1,6
	execute		4,element_list_to_string0_4_0
element_list_to_string0_4_3:
	check_nil		1,element_list_to_string0_4_1
	collect_value		2
	get_value		3,4
	proceed
element_list_to_string0_4_1:
	suspend		element_list_to_string0_4_0
	module_entry		mpimos_utility
	predicate		integer_to_element_list,4
integer_to_element_list_4_0:
	try_me_else		integer_to_element_list_4_1
	integer		1
	put_integer		5,0
	g_less_than		5,1
	put_marked_value		5,1
	put_integer		6,10
	b_modulo		5,6,5
	get_list_val_var		2,6,5,5
	put_integer		2,10
	b_divide		1,2,1
	b_increment		4,2
	put_value		4,2
	put_value		2,5
	execute		4,integer_to_element_list_4_0
integer_to_element_list_4_1:
	otherwise		integer_to_element_list_4_0
	collect_value		1
	get_nil		2
	get_value		3,4
	proceed
integer_to_element_list_4_5:
	suspend		integer_to_element_list_4_0
	module_entry		mpimos_utility
	predicate		qsort,2
qsort_2_0:
	put_nil		3
	execute		3,qsortn_3_0
qsort_2_1:
	suspend		qsort_2_0
	module_entry		mpimos_utility
	predicate		qsort,3
qsort_3_0:
	try_me_else		qsort_3_1
	atom		3
	branch_on_atom		3,2,qsort_3_1
	bucket_entry_a		normal,qsort_3_3
	bucket_entry_a		reverse,qsort_3_4
qsort_3_3:
	put_nil		3
	execute		3,qsortn_3_0
qsort_3_4:
	put_nil		3
	execute		3,qsortr_3_0
qsort_3_1:
	suspend		qsort_3_0
	module_entry		mpimos_utility
	predicate		qsortn,3
qsortn_3_0:
	try_me_else		qsortn_3_1
	jump_on_non_list_var_var		1,qsortn_3_3,4,5
	create_goal		3
	set_variable		1,6
	set_variable		2,7
	set_value		3,3
	enqueue_goal		3,qsortn_3_0
	create_goal		3
	set_variable		1,3
	set_value		2,2
	put_reused_list		1,1
	write_car_marked_value		1,4
	write_cdr_value		1,7
	set_value		3,1
	enqueue_goal		3,qsortn_3_0
	put_values_dec		1,5,2
	put_value		4,6
	execute		4,part_4_0
qsortn_3_3:
	check_nil		1,qsortn_3_1
	get_value		2,3
	proceed
qsortn_3_1:
	suspend		qsortn_3_0
	module_entry		mpimos_utility
	predicate		qsortr,3
qsortr_3_0:
	try_me_else		qsortr_3_1
	jump_on_non_list_var_var		1,qsortr_3_3,4,5
	create_goal		3
	set_variable		1,7
	set_variable		2,8
	set_value		3,3
	enqueue_goal		3,qsortr_3_0
	create_goal		3
	set_variable		1,6
	set_value		2,2
	put_reused_list		1,1
	write_car_marked_value		1,4
	write_cdr_value		1,8
	set_value		3,1
	enqueue_goal		3,qsortr_3_0
	put_values_dec		1,5,2
	put_values_dec		3,7,2
	execute		4,part_4_0
qsortr_3_3:
	check_nil		1,qsortr_3_1
	get_value		2,3
	proceed
qsortr_3_1:
	suspend		qsortr_3_0
	module_entry		mpimos_utility
	predicate		part,4
part_4_0:
	try_me_else		part_4_1
	jump_on_non_list		1,part_4_3
	read_car		1,5
	integer		5
	read_cdr		1,6
	integer		2
	try_me_else		part_4_6
	g_less_than		2,5
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,6
	put_value		4,5
	execute		4,part_4_0
part_4_6:
	get_reused_list_val_var		3,1,1,5,5
	put_value		1,6
	put_value		3,5
	execute		4,part_4_0
part_4_3:
	check_nil		1,part_4_1
	collect_value		2
	get_nil		3
	get_nil		4
	proceed
part_4_1:
	suspend		part_4_0
	module_entry		mpimos_utility
	predicate		qsortv,3
qsortv_3_0:
	put_nil		4
	execute		4,qsortvn_4_0
qsortv_3_1:
	suspend		qsortv_3_0
	module_entry		mpimos_utility
	predicate		qsortv,4
qsortv_4_0:
	try_me_else		qsortv_4_1
	atom		4
	branch_on_atom		4,2,qsortv_4_1
	bucket_entry_a		normal,qsortv_4_3
	bucket_entry_a		reverse,qsortv_4_4
qsortv_4_3:
	put_nil		4
	execute		4,qsortvn_4_0
qsortv_4_4:
	put_nil		4
	execute		4,qsortvr_4_0
qsortv_4_1:
	suspend		qsortv_4_0
	module_entry		mpimos_utility
	predicate		qsortvn,4
qsortvn_4_0:
	try_me_else		qsortvn_4_1
	jump_on_non_list_var_var		1,qsortvn_4_3,5,6
	put_value		8,2
	create_goal		4
	set_variable		1,7
	set_marked_value		2,8
	set_variable		3,2
	set_value		4,4
	enqueue_goal		4,qsortvn_4_0
	create_goal		4
	set_variable		1,4
	set_value		2,8
	set_value		3,3
	put_reused_list		1,1
	write_car_marked_value		1,5
	write_cdr_value		1,2
	set_value		4,1
	enqueue_goal		4,qsortvn_4_0
	put_values_dec		1,6,2
	put_value		3,8
	put_value		5,7
	execute		5,partv_5_0
qsortvn_4_3:
	check_nil		1,qsortvn_4_1
	collect_value		2
	get_value		3,4
	proceed
qsortvn_4_1:
	suspend		qsortvn_4_0
	module_entry		mpimos_utility
	predicate		qsortvr,4
qsortvr_4_0:
	try_me_else		qsortvr_4_1
	jump_on_non_list_var_var		1,qsortvr_4_3,5,6
	put_value		9,2
	create_goal		4
	set_variable		1,8
	set_marked_value		2,9
	set_variable		3,2
	set_value		4,4
	enqueue_goal		4,qsortvr_4_0
	create_goal		4
	set_variable		1,7
	set_value		2,9
	set_value		3,3
	put_reused_list		1,1
	write_car_marked_value		1,5
	write_cdr_value		1,2
	set_value		4,1
	enqueue_goal		4,qsortvr_4_0
	put_values_dec		1,6,2
	put_values_dec		3,9,3
	execute		5,partv_5_0
qsortvr_4_3:
	check_nil		1,qsortvr_4_1
	collect_value		2
	get_value		3,4
	proceed
qsortvr_4_1:
	suspend		qsortvr_4_0
	module_entry		mpimos_utility
	predicate		partv,5
partv_5_0:
	try_me_else		partv_5_1
	jump_on_non_list		1,partv_5_3
	read_car		1,6
	vector		6
	read_cdr		1,7
	vector		2
	integer		3
	try_me_else		partv_5_7
	g_vector_element		6,3,8
	g_vector_element		2,3,9
	integer		9
	integer		8
	g_less_than		9,8
	get_reused_list_val_var		5,1,1,6,6
	put_value		1,7
	put_value		5,6
	execute		5,partv_5_0
partv_5_7:
	try_me_else		partv_5_1
	g_vector_element		6,3,8
	g_vector_element		2,3,9
	integer		9
	integer		8
	g_not_less_than		9,8
	get_reused_list_val_var		4,1,1,6,6
	put_value		1,7
	put_value		4,6
	execute		5,partv_5_0
partv_5_3:
	check_nil		1,partv_5_1
	collect_value		3
	collect_value		2
	get_nil		4
	get_nil		5
	proceed
partv_5_1:
	suspend		partv_5_0
	module_entry		mpimos_utility
	predicate		report_tokens,3
report_tokens_3_0:
	put_value		5,2
	put_value		4,3
	put_integer		2,0
	put_value		3,5
	execute		4,report_tokens_4_0
report_tokens_3_1:
	suspend		report_tokens_3_0
	module_entry		mpimos_utility
	predicate		report_tokens,4
report_tokens_4_0:
	try_me_else		report_tokens_4_1
	wait_list_var_var		1,5,6
	integer		2
	integer		3
	g_less_than		2,3
	collect_list		1
	b_increment		2,1
	create_goal		4
	set_value		1,6
	set_value		2,1
	set_value		3,3
	set_variable		4,3
	enqueue_goal		4,report_tokens_4_0
	put_values_dec		1,5,2
	execute		3,report_one_3_0
report_tokens_4_1:
	try_me_else		report_tokens_4_3
	wait_value		2,3
	collect_value		2
	collect_value		3
	put_structured_constant		2,'$SCNST_9'
	put_list_val_var		3,2,2
	put_list		5
	write_car_atom		5,nl
	write_cdr_value		5,3
	get_list_value		4,5
	execute		2,report_remains_2_0
report_tokens_4_3:
	suspend		report_tokens_4_0
	module_entry		mpimos_utility
	predicate		report_remains,2
report_remains_2_0:
	try_me_else		report_remains_2_1
	jump_on_non_list_var_var		1,report_remains_2_3,3,4
	collect_list		1
	create_goal		2
	set_value		1,4
	set_variable		2,4
	enqueue_goal		2,report_remains_2_0
	put_value		1,3
	put_value		3,4
	execute		3,report_one_3_0
report_remains_2_3:
	check_nil		1,report_remains_2_1
	put_structured_constant		1,'$SCNST_10'
	get_value		2,1
	proceed
report_remains_2_1:
	suspend		report_remains_2_0
	module_entry		mpimos_utility
	predicate		report_tokens,2
report_tokens_2_0:
	try_me_else		report_tokens_2_1
	jump_on_non_list_var_var		1,report_tokens_2_3,3,4
	collect_list		1
	create_goal		2
	set_value		1,4
	set_variable		2,4
	enqueue_goal		2,report_tokens_2_0
	put_value		1,3
	put_value		3,4
	execute		3,report_one_3_0
report_tokens_2_3:
	check_nil		1,report_tokens_2_1
	put_structured_constant		1,'$SCNST_11'
	get_value		2,1
	proceed
report_tokens_2_1:
	suspend		report_tokens_2_0
	module_entry		mpimos_utility
	predicate		report_one,3
report_one_3_0:
	try_me_else		report_one_3_1
	jump_on_non_atom		1,report_one_3_3
	test_atom		1,end,report_one_3_1
	get_value		2,3
	proceed
report_one_3_3:
	is_vector		1,report_one_3_1
	jump_on_arity		1,4,report_one_3_1
	table_entry		report_one_3_1
	table_entry		report_one_3_1
	table_entry		report_one_3_4
	table_entry		report_one_3_5
report_one_3_4:
	read_element		1,0,4
	atom		4
	hash_on_atom		4,7,report_one_3_1
	bucket_entry_a		atom,report_one_3_7
	bucket_entry_a		float,report_one_3_8
	bucket_entry_a		illegal,report_one_3_9
	bucket_entry_a		integer,report_one_3_10
	bucket_entry_a		open,report_one_3_11
	bucket_entry_a		sign,report_one_3_12
	bucket_entry_a		string,report_one_3_13
report_one_3_7:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_12'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_8:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_13'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_9:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_14'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putb
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_10:
	read_element		1,1,5
	integer		5
	try_me_else		report_one_3_15
	put_integer		6,0
	g_not_less_than		5,6
	put_structured_constant		4,'$SCNST_15'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_15:
	collect_vector		1
	put_structured_constant		1,'$SCNST_16'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
report_one_3_11:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_17'
	put_list_val_val		6,4,3
	put_structured_constant		3,'$SCNST_18'
	put_list_val_val		4,3,6
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,4
	get_list_value		2,3
	proceed
report_one_3_12:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_19'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_13:
	read_element		1,1,5
	put_structured_constant		4,'$SCNST_20'
	put_list_val_val		6,4,3
	put_reused_func		1,1,putt
	write_element_value		1,1,5
	put_list_val_val		3,1,6
	get_list_value		2,3
	proceed
report_one_3_5:
	read_element		1,0,4
	wait_atom		4,'$VAR'
	read_elements_inc		1,1,4,2
	collect_value		4
	collect_vector		1
	put_structured_constant		1,'$SCNST_21'
	put_list_val_val		4,1,3
	put_func		1,2,putb
	write_element_value		1,1,5
	put_list_val_val		3,1,4
	get_list_value		2,3
	proceed
report_one_3_1:
	otherwise		report_one_3_0
	put_structured_constant		4,'$SCNST_22'
	put_list_val_val		5,4,3
	put_func		3,2,putt
	write_element_value		3,1,1
	put_list_val_val		1,3,5
	get_list_value		2,1
	proceed
report_one_3_25:
	suspend		report_one_3_0
	module_entry		mpimos_utility
	predicate		copy_string_elements,7
copy_string_elements_7_0:
	try_me_else		copy_string_elements_7_1
	string		1
	integer		2
	put_integer		8,0
	g_not_less_than		2,8
	integer		5
	put_integer		8,0
	g_not_less_than		5,8
	integer		3
	put_integer		8,0
	g_not_less_than		3,8
	g_string		1,8,9
	string		4
	g_string		4,10,11
	wait_value		11,9
	put_value		11,6
	put_value		9,7
	put_value		6,8
	put_values_inc		7,10,2
	execute		9,copy_string_elements1_9_0
copy_string_elements_7_1:
	suspend		copy_string_elements_7_0
	module_entry		mpimos_utility
	predicate		copy_string_elements1,9
copy_string_elements1_9_0:
	try_me_else		copy_string_elements1_9_1
	wait_integer		3,0
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	get_value		8,1
	get_value		9,4
	proceed
copy_string_elements1_9_1:
	otherwise		copy_string_elements1_9_0
	try_me_else		copy_string_elements1_9_6
	integer		2
	integer		6
	g_less_than		2,6
	integer		5
	integer		7
	g_less_than		5,7
	integer		3
	g_add		3,2,10
	g_not_less_than		6,10
	put_value		10,1
	put_value		11,4
	put_value		1,3
	put_values_dec		3,6,2
	put_value		5,7
	put_values_inc		6,10,2
	execute		9,copy_string_elements2_9_0
copy_string_elements1_9_6:
	suspend		copy_string_elements1_9_0
	module_entry		mpimos_utility
	predicate		copy_string_elements2,9
copy_string_elements2_9_0:
	try_me_else		copy_string_elements2_9_1
	wait_integer		1,0
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		2
	get_value		8,6
	get_value		9,7
	proceed
copy_string_elements2_9_1:
	otherwise		copy_string_elements2_9_0
	try_me_else		copy_string_elements2_9_6
	wait_value		4,5
	collect_value		4
	collect_value		1
	collect_value		5
	get_value		9,7
	put_values_inc		1,2,2
	put_value		3,6
	put_value		4,8
	execute		4,copy_zero_4_0
copy_string_elements2_9_6:
	otherwise		copy_string_elements2_9_0
	try_me_else		copy_string_elements2_9_8
	integer		4
	string		7
	g_string_element		7,4,10
	put_marked_value		11,2
	b_set_string_element		6,11,10,6
	b_decrement		1,1
	b_increment		2,2
	b_increment		4,4
	execute		9,copy_string_elements2_9_0
copy_string_elements2_9_8:
	suspend		copy_string_elements2_9_0
	module_entry		mpimos_utility
	predicate		copy_zero,4
copy_zero_4_0:
	try_me_else		copy_zero_4_1
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_value		4,3
	proceed
copy_zero_4_1:
	otherwise		copy_zero_4_0
	put_marked_value		5,1
	put_integer		6,0
	b_set_string_element		3,5,6,3
	b_increment		1,1
	execute		4,copy_zero_4_0
copy_zero_4_3:
	suspend		copy_zero_4_0
	module_entry		mpimos_utility
	predicate		append_string,2
append_string_2_0:
	try_me_else		append_string_2_1
	jump_on_non_list_var_var		1,append_string_2_3,3,4
	string		3
	g_string		3,5,6
	put_value		8,2
	put_variable		2,7
	put_marked_value		5,6
	b_new_string		5,2,5
	put_reused_list_val_val		1,1,3,4
	put_integer		2,0
	put_values_inc		3,5,4
	execute		6,append_string_6_0
append_string_2_3:
	check_nil		1,append_string_2_1
	put_structured_constant		1,'$SCNST_23'
	get_value		2,1
	proceed
append_string_2_1:
	suspend		append_string_2_0
	module_entry		mpimos_utility
	predicate		append_string,6
append_string_6_0:
	try_me_else		append_string_6_1
	jump_on_non_list_var_var		1,append_string_6_3,7,8
	string		7
	g_string		7,9,10
	wait_value		10,4
	collect_list		1
	collect_value		10
	put_marked_value		1,2
	put_marked_value		10,9
	b_add		1,10,1
	create_goal		6
	set_value		1,8
	set_value		2,1
	set_variable		3,8
	set_values_inc		4,4,3
	enqueue_goal		6,append_string_6_0
	put_value		1,3
	put_value		3,9
	put_value		4,7
	put_integer		5,0
	put_value		6,8
	put_void		7
	execute		7,copy_string_elements_7_0
append_string_6_3:
	check_nil		1,append_string_6_1
	collect_value		4
	get_value		5,2
	get_value		6,3
	proceed
append_string_6_1:
	suspend		append_string_6_0
	begin_const_section		mpimos_utility
'$SCNST_0_2':
	define_desc		19,1
	define_integer		11817
'$SCNST_0_1':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_2'
'$SCNST_0_3':
	define_atom		nl
	define_atom		[]
'$SCNST_0_0':
	define_vector		'$SCNST_0_1'
	define_list		'$SCNST_0_3'
'$SCNST_0':
	define_list		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		27,6
	define_integer		1701604457
	define_integer		543973735
	define_integer		1818324839
	define_integer		1919903264
	define_integer		544498029
	define_integer		40
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_atom		nl
	define_atom		[]
'$SCNST_2':
	define_list		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		27,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1768710518
	define_integer		1701601889
	define_integer		976894496
	define_integer		1919907616
	define_integer		1025533036
	define_integer		32
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		27,1
	define_integer		46
'$SCNST_7':
'$SCNST_6':
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		27,1
	define_integer		47
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_8_0':
	define_desc		27,1
	define_integer		48
'$SCNST_8':
	define_string		'$SCNST_8_0'
'$SCNST_9_1':
	define_desc		3,3
	define_integer		539634218
	define_integer		1701995880
	define_integer		707406368
'$SCNST_9_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_9_1'
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_10_1':
	define_desc		0,2
	define_atom		putc
	define_integer		46
'$SCNST_10_2':
	define_atom		nl
	define_atom		[]
'$SCNST_10_0':
	define_vector		'$SCNST_10_1'
	define_list		'$SCNST_10_2'
'$SCNST_10':
	define_list		'$SCNST_10_0'
'$SCNST_11_3':
	define_desc		3,3
	define_integer		539634218
	define_integer		1701995880
	define_integer		707406368
'$SCNST_11_2':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_11_3'
'$SCNST_11_1':
	define_vector		'$SCNST_11_2'
	define_atom		[]
'$SCNST_11_0':
	define_atom		nl
	define_list		'$SCNST_11_1'
'$SCNST_11':
	define_list		'$SCNST_11_0'
'$SCNST_12_0':
	define_desc		0,2
	define_atom		putc
	define_integer		32
'$SCNST_22':
'$SCNST_21':
'$SCNST_20':
'$SCNST_19':
'$SCNST_17':
'$SCNST_15':
'$SCNST_14':
'$SCNST_13':
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_16_1':
	define_desc		11,3
	define_integer		926167346
	define_integer		909326388
	define_integer		2111540
'$SCNST_16_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_16_1'
'$SCNST_16':
	define_vector		'$SCNST_16_0'
'$SCNST_18_0':
	define_desc		0,2
	define_atom		putc
	define_integer		40
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_23_0':
	define_desc		3,0
'$SCNST_23':
	define_string		'$SCNST_23_0'
