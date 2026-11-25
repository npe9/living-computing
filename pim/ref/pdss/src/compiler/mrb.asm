kl1cmp_mrb:
	module		kl1cmp_mrb
	entry		mrb_optimization,13,mrb_optimization_13_0
	entry		compile_for_pdss,6,compile_for_pdss_6_0
	module_entry		kl1cmp_mrb
	predicate		mrb_optimization,13
mrb_optimization_13_0:
	try_me_else		mrb_optimization_13_1
	integer		9
	jump_on_integer		9,4,mrb_optimization_13_1
	table_entry		mrb_optimization_13_3
	table_entry		mrb_optimization_13_4
	table_entry		mrb_optimization_13_5
	table_entry		mrb_optimization_13_6
mrb_optimization_13_3:
	collect_value		13
	collect_value		12
	collect_value		11
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_void		3
	put_nil		4
	put_value		5,10
	put_nil		6
	execute		6,merge_read_variable_6_0
mrb_optimization_13_4:
	collect_value		13
	collect_value		11
	collect_value		3
	put_value		13,12
	put_value		16,10
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_variable		3,11
	set_value		4,4
	set_variable		5,10
	set_value		6,6
	set_variable		7,9
	set_value		8,8
	set_variable		9,17
	set_variable		10,14
	enqueue_goal		10,mrb_body_code_10_0
	create_goal		6
	set_value		1,1
	set_value		2,3
	set_void		3
	set_nil		4
	set_variable		5,1
	set_nil		6
	enqueue_goal		6,merge_read_variable_6_0
	put_nil		2
	put_integer		3,1
	put_value		4,11
	put_value		6,10
	put_value		8,9
	put_void		9
	put_void		10
	put_void		11
	put_nil		12
	put_nil		15
	execute		17,mrb_passive_code_17_0
mrb_optimization_13_5:
	collect_value		13
	collect_value		11
	collect_value		3
	put_value		13,12
	put_value		16,10
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_marked_variable		3,10
	set_value		4,4
	set_variable		5,9
	set_value		6,6
	set_variable		7,4
	set_value		8,8
	put_func		2,2,'$Gc_code'
	write_element_variable		2,1,6
	put_list_val_var		8,2,17
	set_value		9,8
	set_variable		10,14
	enqueue_goal		10,mrb_body_code_10_0
	create_goal		3
	set_value		1,6
	set_nil		2
	set_variable		3,2
	enqueue_goal		3,unique_3_0
	create_goal		7
	set_variable		1,8
	set_value		2,4
	set_value		3,10
	set_value		4,2
	set_nil		5
	set_variable		6,2
	set_atom		7,no
	enqueue_goal		7,mrb_update_optimal_code_7_0
	create_goal		6
	set_value		1,1
	set_values_dec		2,3,2
	set_nil		4
	set_variable		5,1
	set_variable		6,11
	enqueue_goal		6,merge_read_variable_6_0
	put_nil		2
	put_integer		3,1
	put_value		4,10
	put_value		6,9
	put_void		9
	put_void		10
	put_nil		12
	put_nil		15
	execute		17,mrb_passive_code_17_0
mrb_optimization_13_6:
	collect_value		11
	collect_value		3
	put_value		18,12
	put_value		15,13
	put_value		16,10
	create_goal		10
	set_variable		1,3
	set_value		2,2
	set_marked_variable		3,11
	set_value		4,4
	set_variable		5,10
	set_value		6,6
	set_variable		7,4
	set_value		8,8
	put_func		2,2,'$Gc_code'
	write_element_variable		2,1,6
	put_list_val_var		8,2,17
	set_value		9,8
	set_variable		10,14
	enqueue_goal		10,mrb_body_code_10_0
	create_goal		3
	set_value		1,6
	set_nil		2
	set_variable		3,2
	enqueue_goal		3,unique_3_0
	create_goal		7
	set_variable		1,8
	set_value		2,4
	set_value		3,11
	set_value		4,2
	set_nil		5
	set_variable		6,2
	set_atom		7,no
	enqueue_goal		7,mrb_update_optimal_code_7_0
	create_goal		6
	set_value		1,1
	set_values_dec		2,3,2
	set_nil		4
	set_variable		5,1
	set_variable		6,9
	enqueue_goal		6,merge_read_variable_6_0
	put_nil		2
	put_integer		3,1
	put_value		4,11
	put_value		6,10
	put_variable		11,10
	put_nil		12
	put_value		13,18
	execute		17,mrb_passive_code_17_0
mrb_optimization_13_1:
	suspend		mrb_optimization_13_0
	module_entry		kl1cmp_mrb
	predicate		copy_element_of_list,3
copy_element_of_list_3_0:
	try_me_else		copy_element_of_list_3_1
	jump_on_non_list_var_var		3,copy_element_of_list_3_3,4,5
	get_reused_list_val_var		1,6,3,4,3
	put_value		1,3
	put_value		3,5
	execute		3,copy_element_of_list_3_0
copy_element_of_list_3_3:
	check_nil		3,copy_element_of_list_3_1
	get_value		1,2
	proceed
copy_element_of_list_3_1:
	suspend		copy_element_of_list_3_0
	module_entry		kl1cmp_mrb
	predicate		mrb_passive_code,17
mrb_passive_code_17_0:
	try_me_else		mrb_passive_code_17_1
	list		16
	read_car		16,18
	try_me_else		mrb_passive_code_17_3
	wait_atom		18,commit
	read_cdr		16,19
	collect_list		16
	collect_value		15
	get_value		13,14
	get_value		11,12
	get_value		9,10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	get_value		19,17
	proceed
mrb_passive_code_17_3:
	read_cdr		16,19
	try_me_else		mrb_passive_code_17_1
	put_atom		20,commit
	g_diff		18,20
	collect_list		16
	create_goal		17
	set_variable		1,26
	set_value		2,2
	set_variable		3,25
	set_value		4,4
	set_variable		5,24
	set_value		6,6
	set_variable		7,23
	set_value		8,8
	set_variable		9,22
	set_value		10,10
	set_variable		11,21
	set_value		12,12
	set_variable		13,20
	set_value		14,14
	set_variable		15,16
	set_value		16,19
	set_value		17,17
	enqueue_goal		17,mrb_passive_code_17_0
	put_value		2,26
	put_value		4,25
	put_value		6,24
	put_value		8,23
	put_value		10,22
	put_value		12,21
	put_value		14,20
	put_value		17,18
	execute		17,mrb_one_passive_code_17_0
mrb_passive_code_17_1:
	suspend		mrb_passive_code_17_0
	module_entry		kl1cmp_mrb
	predicate		mrb_one_passive_code,17
mrb_one_passive_code_17_0:
	try_me_else		mrb_one_passive_code_17_1
	vector		17
	jump_on_arity		17,4,mrb_one_passive_code_17_1
	table_entry		mrb_one_passive_code_17_1
	table_entry		mrb_one_passive_code_17_1
	table_entry		mrb_one_passive_code_17_3
	table_entry		mrb_one_passive_code_17_4
mrb_one_passive_code_17_3:
	read_element		17,0,18
	atom		18
	branch_on_atom		18,2,mrb_one_passive_code_17_1
	bucket_entry_a		read_variable,mrb_one_passive_code_17_6
	bucket_entry_a		wait_list,mrb_one_passive_code_17_7
mrb_one_passive_code_17_6:
	read_element		17,1,19
	get_value		11,12
	get_value		7,8
	get_value		5,6
	b_increment		3,3
	get_value		3,4
	put_reused_func		3,17,read_variable
	write_element_marked_value		3,1,19
	put_list_val_val		4,3,2
	get_list_value		1,4
	put_values_inc		1,9,2
	put_values_inc		3,13,4
	put_value		7,19
	execute		7,manage_vector_element_7_0
mrb_one_passive_code_17_7:
	read_element		17,1,19
	get_value		15,16
	get_value		9,10
	get_value		7,8
	get_value		5,6
	put_reused_func		5,17,wait_list
	write_element_marked_value		5,1,19
	get_list_val_var		1,6,5,5
	b_increment		3,1
	get_value		1,4
	create_goal		6
	set_value		1,5
	set_value		2,2
	set_values_inc		3,11,2
	set_variable		5,4
	put_func		1,2,collect_list
	write_element_value		1,1,19
	set_value		6,1
	enqueue_goal		6,is_not_refed_in_body_6_0
	put_values_inc		1,13,2
	put_value		3,19
	execute		4,body_ref_check_4_0
mrb_one_passive_code_17_4:
	read_element		17,0,18
	atom		18
	branch_on_atom		18,3,mrb_one_passive_code_17_1
	bucket_entry_a		wait_value,mrb_one_passive_code_17_9
	bucket_entry_a		wait_variable,mrb_one_passive_code_17_10
	bucket_entry_a		wait_vector,mrb_one_passive_code_17_11
mrb_one_passive_code_17_9:
	read_elements_inc		17,1,19,2
	get_value		5,6
	put_list		5
	write_car_atom		5,collect_stack
	write_cdr_value		5,12
	put_marked_value		6,3
	b_increment		6,6
	get_value		6,4
	put_reused_func		4,17,wait_value
	write_element_marked_value		4,1,19
	write_element_marked_value		4,2,20
	put_list_val_val		6,4,2
	create_goal		7
	set_values_inc		1,9,2
	set_variable		3,10
	set_values_inc		4,14,3
	set_value		7,19
	enqueue_goal		7,manage_vector_element_7_0
	create_goal		8
	set_variable		1,9
	set_value		2,6
	set_variable		3,4
	set_value		4,5
	set_variable		5,2
	set_value		6,3
	set_variable		7,6
	put_func		5,2,collect_value
	write_element_value		5,1,19
	set_value		8,5
	enqueue_goal		8,is_not_refed_in_body_and_last_8_0
	create_goal		4
	set_variable		1,5
	set_value		2,10
	set_value		3,19
	set_value		4,2
	enqueue_goal		4,body_ref_check_4_0
	create_goal		4
	set_variable		1,2
	set_value		2,8
	set_value		3,19
	set_value		4,6
	enqueue_goal		4,latest_occurrence_4_0
	create_goal		8
	set_value		1,1
	set_value		2,9
	set_value		3,11
	set_value		4,4
	set_variable		5,1
	set_value		6,3
	set_variable		7,4
	put_func		3,2,collect_value
	write_element_value		3,1,20
	set_value		8,3
	enqueue_goal		8,is_not_refed_in_body_and_last_8_0
	create_goal		4
	set_value		1,13
	set_value		2,5
	set_value		3,20
	set_value		4,1
	enqueue_goal		4,body_ref_check_4_0
	put_value		1,7
	put_value		3,20
	execute		4,latest_occurrence_4_0
mrb_one_passive_code_17_10:
	read_elements_inc		17,1,19,2
	get_value		5,6
	put_marked_value		5,3
	b_increment		5,5
	get_value		5,4
	put_reused_func		4,17,wait_variable
	write_element_marked_value		4,1,19
	write_element_value		4,2,20
	put_list_val_val		5,4,2
	create_goal		7
	set_values_inc		1,9,2
	set_variable		3,2
	set_values_inc		4,14,3
	set_value		7,19
	enqueue_goal		7,manage_vector_element_7_0
	create_goal		8
	set_value		1,1
	set_value		2,5
	set_values_inc		3,11,2
	set_variable		5,1
	set_value		6,3
	set_variable		7,4
	put_func		3,2,collect_value
	write_element_value		3,1,19
	set_value		8,3
	enqueue_goal		8,is_not_refed_in_body_and_last_8_0
	create_goal		4
	set_value		1,13
	set_value		2,2
	set_value		3,19
	set_value		4,1
	enqueue_goal		4,body_ref_check_4_0
	put_values_inc		1,7,2
	put_value		3,19
	execute		4,latest_occurrence_4_0
mrb_one_passive_code_17_11:
	read_elements_inc		17,1,19,2
	get_value		15,16
	get_value		9,10
	get_value		7,8
	get_value		5,6
	put_reused_func		5,17,wait_vector
	write_element_marked_value		5,1,19
	write_element_value		5,2,20
	get_list_val_var		1,6,5,5
	b_increment		3,1
	get_value		1,4
	create_goal		6
	set_value		1,5
	set_value		2,2
	set_values_inc		3,11,2
	set_variable		5,4
	put_func		1,2,collect_vector
	write_element_value		1,1,19
	set_value		6,1
	enqueue_goal		6,is_not_refed_in_body_6_0
	put_values_inc		1,13,2
	put_value		3,19
	execute		4,body_ref_check_4_0
mrb_one_passive_code_17_1:
	otherwise		mrb_one_passive_code_17_0
	get_value		15,16
	get_value		13,14
	get_value		9,10
	b_increment		3,3
	put_list		9
	write_car_marked_value		9,17
	write_cdr_value		9,2
	get_list_value		1,9
	create_goal		11
	set_values_inc		1,11,2
	set_values_inc		3,3,6
	set_variable		9,3
	set_integer		10,1
	set_value		11,17
	enqueue_goal		11,mrb_void_check_11_0
	put_value		1,17
	put_void		2
	execute_external		kl1cmp_reader,functor,3
mrb_one_passive_code_17_18:
	suspend		mrb_one_passive_code_17_0
	module_entry		kl1cmp_mrb
	predicate		is_not_refed_in_body_and_last,8
is_not_refed_in_body_and_last_8_0:
	try_me_else		is_not_refed_in_body_and_last_8_1
	wait_atom		5,no
	wait_value		6,7
	collect_value		6
	collect_value		7
	get_value		1,2
	put_list_val_val		1,8,4
	get_list_value		3,1
	proceed
is_not_refed_in_body_and_last_8_1:
	otherwise		is_not_refed_in_body_and_last_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
is_not_refed_in_body_and_last_8_6:
	suspend		is_not_refed_in_body_and_last_8_0
	module_entry		kl1cmp_mrb
	predicate		is_not_refed_in_body,6
is_not_refed_in_body_6_0:
	try_me_else		is_not_refed_in_body_6_1
	atom		5
	branch_on_atom		5,2,is_not_refed_in_body_6_1
	bucket_entry_a		no,is_not_refed_in_body_6_3
	bucket_entry_a		yes,is_not_refed_in_body_6_4
is_not_refed_in_body_6_3:
	get_value		1,2
	put_list_val_val		1,6,4
	get_list_value		3,1
	proceed
is_not_refed_in_body_6_4:
	collect_value		6
	get_value		3,4
	get_value		1,2
	proceed
is_not_refed_in_body_6_1:
	suspend		is_not_refed_in_body_6_0
	module_entry		kl1cmp_mrb
	predicate		manage_vector_element,7
manage_vector_element_7_0:
	create_goal		8
	set_values_inc		1,1,4
	set_variable		5,2
	set_value		6,6
	set_variable		7,4
	set_marked_value		8,7
	enqueue_goal		8,manage_vector_element_8_0
	put_value		1,5
	put_value		3,7
	execute		4,get_var_attr_4_0
manage_vector_element_7_1:
	suspend		manage_vector_element_7_0
	module_entry		kl1cmp_mrb
	predicate		get_var_attr,4
get_var_attr_4_0:
	try_me_else		get_var_attr_4_1
	wait_nil		1
	collect_value		3
	get_nil		4
	get_nil		2
	proceed
get_var_attr_4_1:
	otherwise		get_var_attr_4_0
	try_me_else		get_var_attr_4_6
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	collect_value		6
	collect_vector		3
	put_marked_value		3,4
	b_set_vector_element		1,5,1,3,3
	get_value		1,4
	get_value		3,2
	proceed
get_var_attr_4_6:
	suspend		get_var_attr_4_0
	module_entry		kl1cmp_mrb
	predicate		manage_vector_element,8
manage_vector_element_8_0:
	try_me_else		manage_vector_element_8_1
	jump_on_non_list_var_var		7,manage_vector_element_8_3,12,9
	wait_vector		12,3
	read_element		12,0,10
	wait_atom		10,element
	read_elements_inc		12,1,10,2
	put_value		13,8
	put_reused_func		8,12,element
	write_element_marked_value		8,1,10
	write_element_marked_value		8,2,11
	put_reused_list_val_val		7,7,8,9
	put_values_inc		8,10,2
	put_value		10,13
	execute		10,manage_vector_element_10_0
manage_vector_element_8_3:
	check_nil		7,manage_vector_element_8_1
	collect_value		8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
manage_vector_element_8_1:
	suspend		manage_vector_element_8_0
	module_entry		kl1cmp_mrb
	predicate		manage_vector_element,10
manage_vector_element_10_0:
	try_me_else		manage_vector_element_10_1
	jump_on_non_list_var_var		7,manage_vector_element_10_3,14,11
	wait_vector		14,3
	read_element		14,0,12
	wait_atom		12,element
	read_elements_inc		14,1,12,2
	collect_list		7
	collect_value		13
	collect_vector		14
	create_goal		10
	set_variable		1,13
	set_value		2,2
	set_variable		3,7
	set_value		4,4
	set_variable		5,2
	set_value		6,6
	set_value		7,11
	set_marked_value		8,8
	set_marked_value		9,9
	set_marked_value		10,10
	enqueue_goal		10,manage_vector_element_10_0
	create_goal		12
	set_value		1,1
	set_value		2,13
	set_variable		3,6
	set_value		4,7
	set_value		5,5
	set_value		6,2
	set_variable		7,4
	set_variable		8,1
	set_marked_value		9,12
	set_values_inc		10,8,3
	enqueue_goal		12,mark_element_or_not_12_0
	create_goal		4
	set_variable		1,2
	set_value		2,6
	set_value		3,10
	set_value		4,1
	enqueue_goal		4,body_ref_check_4_0
	put_value		1,3
	put_value		3,12
	execute		4,body_ref_check_4_0
manage_vector_element_10_3:
	check_nil		7,manage_vector_element_10_1
	collect_value		10
	collect_value		9
	collect_value		8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
manage_vector_element_10_1:
	suspend		manage_vector_element_10_0
	module_entry		kl1cmp_mrb
	predicate		body_ref_check,4
body_ref_check_4_0:
	try_me_else		body_ref_check_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_elements_inc		1,1,5,2
	wait_vector		3,3
	read_element		3,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		3,1,7,2
	collect_value		8
	collect_vector		3
	put_marked_variable		3,8
	b_set_vector_element		6,7,6,3,3
	get_value		6,8
	put_reused_func		1,1,-
	write_element_value		1,1,5
	write_element_value		1,2,3
	get_vector_value		2,1
	put_value		1,8
	put_value		2,4
	execute		2,body_ref_check_2_0
body_ref_check_4_1:
	suspend		body_ref_check_4_0
	module_entry		kl1cmp_mrb
	predicate		body_ref_check,2
body_ref_check_2_0:
	try_me_else		body_ref_check_2_1
	wait_integer		1,0
	get_atom		2,no
	proceed
body_ref_check_2_1:
	otherwise		body_ref_check_2_0
	collect_value		1
	get_atom		2,yes
	proceed
body_ref_check_2_6:
	suspend		body_ref_check_2_0
	module_entry		kl1cmp_mrb
	predicate		mark_element_or_not,12
mark_element_or_not_12_0:
	try_me_else		mark_element_or_not_12_1
	atom		7
	branch_on_atom		7,2,mark_element_or_not_12_1
	bucket_entry_a		no,mark_element_or_not_12_3
	bucket_entry_a		yes,mark_element_or_not_12_4
mark_element_or_not_12_3:
	wait_atom		8,yes
	collect_value		9
	get_value		3,4
	put_func		3,4,mark_element
	write_element_marked_value		3,1,10
	write_element_value		3,2,11
	write_element_marked_value		3,3,12
	put_list_val_val		4,3,2
	get_list_value		1,4
	put_values_inc		1,5,2
	put_value		3,10
	put_value		4,12
	execute		4,clear_attr_4_0
mark_element_or_not_12_4:
	wait_atom		8,yes
	collect_value		9
	get_value		3,4
	put_func		3,4,mark_element
	write_element_marked_value		3,1,10
	write_element_value		3,2,11
	write_element_marked_value		3,3,12
	put_list_val_val		4,3,2
	get_list_value		1,4
	put_values_inc		1,5,2
	put_value		3,10
	put_value		4,12
	execute		4,clear_attr_4_0
mark_element_or_not_12_1:
	otherwise		mark_element_or_not_12_0
	collect_value		8
	collect_value		7
	create_goal		10
	set_values_inc		1,1,4
	set_variable		5,2
	set_value		6,6
	set_variable		7,4
	set_values_inc		8,10,3
	enqueue_goal		10,manage_vector_element_10_0
	put_value		1,5
	put_value		3,9
	execute		4,get_var_attr_4_0
mark_element_or_not_12_7:
	suspend		mark_element_or_not_12_0
	module_entry		kl1cmp_mrb
	predicate		clear_attr,4
clear_attr_4_0:
	try_me_else		clear_attr_4_1
	wait_vector		4,3
	read_element		4,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		4,1,5,2
	collect_value		6
	collect_vector		4
	put_variable		6,4
	b_set_vector_element		1,5,1,6,5
	get_value		5,2
	put_values_inc		2,3,2
	execute		3,clear_one_attr_3_0
clear_attr_4_1:
	suspend		clear_attr_4_0
	module_entry		kl1cmp_mrb
	predicate		clear_one_attr,3
clear_one_attr_3_0:
	try_me_else		clear_one_attr_3_1
	jump_on_non_list_var_var		1,clear_one_attr_3_3,8,4
	wait_vector		8,4
	read_element		8,0,5
	wait_atom		5,element
	read_elements_inc		8,1,5,3
	wait_value		5,2
	collect_list		1
	collect_value		7
	collect_value		6
	collect_value		2
	collect_vector		8
	put_values_inc		1,4,2
	execute		3,clear_one_attr_3_0
clear_one_attr_3_3:
	check_nil		1,clear_one_attr_3_1
	collect_value		2
	get_nil		3
	proceed
clear_one_attr_3_1:
	otherwise		clear_one_attr_3_0
	try_me_else		clear_one_attr_3_8
	wait_list_var_var		1,4,5
	get_reused_list_val_var		3,1,1,4,4
	put_value		1,5
	put_value		3,4
	execute		3,clear_one_attr_3_0
clear_one_attr_3_8:
	suspend		clear_one_attr_3_0
	module_entry		kl1cmp_mrb
	predicate		latest_or_not,8
latest_or_not_8_0:
	try_me_else		latest_or_not_8_1
	wait_value		5,8
	collect_value		5
	collect_value		8
	get_value		1,2
	put_vector		1,2
	write_elements_inc		1,0,6,2
	put_list_val_val		2,1,4
	get_list_value		3,2
	proceed
latest_or_not_8_1:
	otherwise		latest_or_not_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_value		3,4
	get_value		1,2
	proceed
latest_or_not_8_3:
	suspend		latest_or_not_8_0
	module_entry		kl1cmp_mrb
	predicate		merge_read_variable,6
merge_read_variable_6_0:
	try_me_else		merge_read_variable_6_1
	jump_on_non_list_var_var		5,merge_read_variable_6_3,7,8
	get_reused_list_val_var		1,9,5,7,5
	put_value		1,5
	put_value		5,8
	execute		6,merge_read_variable_6_0
merge_read_variable_6_3:
	check_nil		5,merge_read_variable_6_1
	get_value		1,2
	put_values_inc		1,3,2
	put_value		3,6
	execute		3,out_to_stream_3_0
merge_read_variable_6_1:
	suspend		merge_read_variable_6_0
	module_entry		kl1cmp_mrb
	predicate		check_mrb_instr,6
check_mrb_instr_6_0:
	try_me_else		check_mrb_instr_6_1
	jump_on_non_list_var_var		3,check_mrb_instr_6_3,7,8
	wait_atom		5,no
	collect_list		3
	create_goal		6
	set_variable		1,3
	set_value		2,2
	set_value		3,8
	set_marked_value		4,4
	set_variable		5,8
	set_value		6,6
	enqueue_goal		6,check_mrb_instr_6_0
	put_value		2,3
	put_value		3,7
	put_atom		5,no
	put_value		6,8
	execute		6,look_for_Ai_6_0
check_mrb_instr_6_3:
	check_nil		3,check_mrb_instr_6_1
	collect_value		4
	get_value		1,2
	get_value		5,6
	proceed
check_mrb_instr_6_1:
	try_me_else		check_mrb_instr_6_4
	wait_atom		5,yes
	collect_value		4
	get_atom		6,yes
	execute		3,out_to_stream_3_0
check_mrb_instr_6_4:
	suspend		check_mrb_instr_6_0
	module_entry		kl1cmp_mrb
	predicate		look_for_Ai,6
look_for_Ai_6_0:
	try_me_else		look_for_Ai_6_1
	vector		3
	wait_atom		5,no
	g_vector		3,5
	put_list		8
	write_car_variable		8,7
	write_cdr_value		8,2
	get_list_value		1,8
	put_value		1,5
	put_value		2,3
	put_value		3,7
	put_atom		5,no
	execute		6,look_for_Ai_for_args_6_0
look_for_Ai_6_1:
	try_me_else		look_for_Ai_6_4
	wait_atom		5,yes
	collect_value		4
	get_atom		6,yes
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
look_for_Ai_6_4:
	otherwise		look_for_Ai_6_0
	collect_value		4
	collect_value		3
	get_value		1,2
	get_value		5,6
	proceed
look_for_Ai_6_12:
	suspend		look_for_Ai_6_0
	module_entry		kl1cmp_mrb
	predicate		look_for_Ai_for_args,6
look_for_Ai_for_args_6_0:
	try_me_else		look_for_Ai_for_args_6_1
	wait_integer		1,1
	collect_value		4
	get_value		5,6
	get_value		2,3
	proceed
look_for_Ai_for_args_6_1:
	otherwise		look_for_Ai_for_args_6_0
	try_me_else		look_for_Ai_for_args_6_6
	wait_integer		1,1
	wait_atom		5,yes
	collect_value		4
	get_atom		6,yes
	get_value		3,2
	proceed
look_for_Ai_for_args_6_6:
	try_me_else		look_for_Ai_for_args_6_8
	wait_atom		5,no
	b_decrement		1,1
	put_marked_value		7,1
	put_marked_variable		8,5
	b_set_vector_element		2,7,7,8,2
	get_value		7,5
	create_goal		6
	set_values_inc		1,1,3
	set_marked_value		4,4
	set_variable		5,3
	set_value		6,6
	enqueue_goal		6,look_for_Ai_for_args_6_0
	put_values_inc		1,4,2
	execute		3,check_args_3_0
look_for_Ai_for_args_6_8:
	suspend		look_for_Ai_for_args_6_0
	module_entry		kl1cmp_mrb
	predicate		check_args,3
check_args_3_0:
	try_me_else		check_args_3_1
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_atom		3,yes
	proceed
check_args_3_1:
	otherwise		check_args_3_0
	collect_value		2
	collect_value		1
	get_atom		3,no
	proceed
check_args_3_3:
	suspend		check_args_3_0
	module_entry		kl1cmp_mrb
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
	module_entry		kl1cmp_mrb
	predicate		out_read_value,5
out_read_value_5_0:
	try_me_else		out_read_value_5_1
	atom		3
	branch_on_atom		3,2,out_read_value_5_1
	bucket_entry_a		no,out_read_value_5_3
	bucket_entry_a		yes,out_read_value_5_4
out_read_value_5_3:
	collect_value		4
	put_func		3,2,read_value
	write_element_value		3,1,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
out_read_value_5_4:
	put_func		3,3,wait_value
	write_element_value		3,1,5
	write_element_marked_value		3,2,4
	put_list_val_val		5,3,2
	put_func		2,2,read_variable
	write_element_value		2,1,4
	put_list_val_val		3,2,5
	get_list_value		1,3
	proceed
out_read_value_5_1:
	suspend		out_read_value_5_0
	module_entry		kl1cmp_mrb
	predicate		out_read_constant,5
out_read_constant_5_0:
	try_me_else		out_read_constant_5_1
	atom		3
	branch_on_atom		3,2,out_read_constant_5_1
	bucket_entry_a		no,out_read_constant_5_3
	bucket_entry_a		yes,out_read_constant_5_4
out_read_constant_5_3:
	collect_value		4
	put_func		3,2,read_constant
	write_element_value		3,1,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
out_read_constant_5_4:
	put_func		3,3,wait_constant
	write_element_marked_value		3,1,4
	write_element_value		3,2,5
	put_list_val_val		5,3,2
	put_func		2,2,read_variable
	write_element_value		2,1,4
	put_list_val_val		3,2,5
	get_list_value		1,3
	proceed
out_read_constant_5_1:
	suspend		out_read_constant_5_0
	module_entry		kl1cmp_mrb
	predicate		mrb_void_check,11
mrb_void_check_11_0:
	try_me_else		mrb_void_check_11_1
	integer		9
	test_integer		9,0,mrb_void_check_11_3
	collect_value		11
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
mrb_void_check_11_3:
	put_integer		12,0
	g_less_than		12,9
	put_marked_value		12,10
	put_nil		13
	b_set_vector_element		11,12,11,13,12
	b_increment		10,10
	b_decrement		9,9
	create_goal		11
	set_variable		1,13
	set_value		2,2
	set_variable		3,2
	set_value		4,4
	set_variable		5,4
	set_value		6,6
	set_variable		7,6
	set_values_inc		8,8,3
	set_value		11,12
	enqueue_goal		11,mrb_void_check_11_0
	create_goal		11
	set_value		1,1
	set_value		2,13
	set_values_dec		3,3,2
	set_variable		5,2
	set_value		6,4
	set_variable		7,4
	set_value		8,6
	set_marked_value		9,11
	set_variable		10,6
	set_variable		11,8
	enqueue_goal		11,mrb_one_void_check_11_0
	put_value		1,5
	put_value		3,7
	put_value		5,11
	put_value		7,8
	execute		7,first_and_latest_occurrence_7_0
mrb_void_check_11_1:
	suspend		mrb_void_check_11_0
	module_entry		kl1cmp_mrb
	predicate		mrb_one_void_check,11
mrb_one_void_check_11_0:
	try_me_else		mrb_one_void_check_11_1
	wait_vector		9,3
	read_element		9,0,12
	wait_atom		12,'$VAR'
	read_elements_inc		9,1,12,2
	integer		10
	integer		11
	g_equal		10,11
	get_value		7,8
	get_value		5,6
	get_value		3,4
	put_reused_func		3,9,'$VAR'
	write_elements_inc		3,1,12,2
	put_func		4,2,collect_value
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
mrb_one_void_check_11_1:
	otherwise		mrb_one_void_check_11_0
	collect_value		11
	collect_value		10
	collect_value		9
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
mrb_one_void_check_11_6:
	suspend		mrb_one_void_check_11_0
	module_entry		kl1cmp_mrb
	predicate		mrb_update_optimal_code,7
mrb_update_optimal_code_7_0:
	try_me_else		mrb_update_optimal_code_7_1
	jump_on_non_list		6,mrb_update_optimal_code_7_3
	read_car		6,8
	jump_on_non_atom		8,mrb_update_optimal_code_7_5
	test_atom		8,collect_stack,mrb_update_optimal_code_7_1
	read_cdr		6,9
	collect_list		6
	collect_value		7
	put_value		6,9
	put_atom		7,yes
	execute		7,mrb_update_optimal_code_7_0
mrb_update_optimal_code_7_5:
	is_vector		8,mrb_update_optimal_code_7_1
	jump_on_arity		8,5,mrb_update_optimal_code_7_1
	table_entry		mrb_update_optimal_code_7_1
	table_entry		mrb_update_optimal_code_7_1
	table_entry		mrb_update_optimal_code_7_6
	table_entry		mrb_update_optimal_code_7_1
	table_entry		mrb_update_optimal_code_7_7
mrb_update_optimal_code_7_6:
	read_element		8,0,9
	atom		9
	branch_on_atom		9,3,mrb_update_optimal_code_7_1
	bucket_entry_a		collect_list,mrb_update_optimal_code_7_9
	bucket_entry_a		collect_value,mrb_update_optimal_code_7_10
	bucket_entry_a		collect_vector,mrb_update_optimal_code_7_11
mrb_update_optimal_code_7_9:
	read_cdr		6,10
	read_element		8,1,11
	put_value		9,1
	put_value		12,3
	put_reused_func		1,8,collect_list
	write_element_marked_value		1,1,11
	get_reused_list_val_var		4,3,6,1,1
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_marked_value		3,12
	set_value		4,1
	set_value		5,5
	set_value		6,10
	set_value		7,7
	enqueue_goal		7,mrb_update_optimal_code_7_0
	put_value		1,11
	put_value		2,9
	put_value		4,12
	execute		4,set_pc_to_comitted_4_0
mrb_update_optimal_code_7_10:
	read_cdr		6,10
	read_element		8,1,11
	put_value		9,1
	put_value		12,3
	put_reused_func		1,8,collect_value
	write_element_marked_value		1,1,11
	get_reused_list_val_var		4,3,6,1,1
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_marked_value		3,12
	set_value		4,1
	set_value		5,5
	set_value		6,10
	set_value		7,7
	enqueue_goal		7,mrb_update_optimal_code_7_0
	put_value		1,11
	put_value		2,9
	put_value		4,12
	execute		4,set_pc_to_comitted_4_0
mrb_update_optimal_code_7_11:
	read_cdr		6,10
	read_element		8,1,11
	put_value		9,1
	put_value		12,3
	put_reused_func		1,8,collect_vector
	write_element_marked_value		1,1,11
	get_reused_list_val_var		4,3,6,1,1
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_marked_value		3,12
	set_value		4,1
	set_value		5,5
	set_value		6,10
	set_value		7,7
	enqueue_goal		7,mrb_update_optimal_code_7_0
	put_value		1,11
	put_value		2,9
	put_value		4,12
	execute		4,set_pc_to_comitted_4_0
mrb_update_optimal_code_7_7:
	read_cdr		6,9
	read_element		8,0,10
	wait_atom		10,mark_element
	read_elements_inc		8,1,10,3
	put_value		13,1
	put_value		14,3
	put_reused_func		1,8,mark_element
	write_element_marked_value		1,1,10
	write_element_marked_value		1,2,11
	write_element_marked_value		1,3,12
	get_reused_list_val_var		4,3,6,1,1
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_marked_value		3,14
	set_value		4,1
	set_value		5,5
	set_value		6,9
	set_value		7,7
	enqueue_goal		7,mrb_update_optimal_code_7_0
	create_goal		4
	set_value		1,12
	set_variable		2,1
	set_value		3,3
	set_value		4,14
	enqueue_goal		4,set_pc_to_comitted_4_0
	create_goal		4
	set_value		1,11
	set_variable		2,3
	set_value		3,1
	set_value		4,14
	enqueue_goal		4,set_pc_to_comitted_4_0
	put_value		1,10
	put_value		2,13
	put_value		4,14
	execute		4,set_pc_to_comitted_4_0
mrb_update_optimal_code_7_3:
	check_nil		6,mrb_update_optimal_code_7_1
	atom		7
	branch_on_atom		7,2,mrb_update_optimal_code_7_1
	bucket_entry_a		no,mrb_update_optimal_code_7_13
	bucket_entry_a		yes,mrb_update_optimal_code_7_14
mrb_update_optimal_code_7_13:
	collect_value		3
	get_value		4,5
	get_value		1,2
	proceed
mrb_update_optimal_code_7_14:
	collect_value		3
	get_value		1,2
	put_list		1
	write_car_atom		1,collect_stack
	write_cdr_value		1,5
	get_list_value		4,1
	proceed
mrb_update_optimal_code_7_1:
	suspend		mrb_update_optimal_code_7_0
	module_entry		kl1cmp_mrb
	predicate		set_pc_to_comitted,4
set_pc_to_comitted_4_0:
	try_me_else		set_pc_to_comitted_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		1,1,5,2
	collect_value		6
	collect_vector		1
	put_variable		1,6
	b_set_vector_element		2,5,1,1,2
	get_value		2,3
	put_value		2,4
	put_value		3,6
	execute		3,return_greater_3_0
set_pc_to_comitted_4_1:
	suspend		set_pc_to_comitted_4_0
	module_entry		kl1cmp_mrb
	predicate		return_greater,3
return_greater_3_0:
	try_me_else		return_greater_3_1
	integer		1
	integer		2
	g_less_than		2,1
	get_value		3,1
	proceed
return_greater_3_1:
	otherwise		return_greater_3_0
	collect_value		1
	get_value		3,2
	proceed
return_greater_3_5:
	suspend		return_greater_3_0
	module_entry		kl1cmp_mrb
	predicate		mrb_body_code,10
mrb_body_code_10_0:
	try_me_else		mrb_body_code_10_1
	jump_on_non_list_var_var		9,mrb_body_code_10_3,11,12
	collect_list		9
	b_increment		3,3
	create_goal		10
	set_variable		1,9
	set_values_inc		2,2,7
	set_value		9,12
	set_variable		10,4
	enqueue_goal		10,mrb_body_code_10_0
	put_values_inc		2,9,2
	put_value		5,11
	execute		5,mrb_one_body_code_5_0
mrb_body_code_10_3:
	check_nil		9,mrb_body_code_10_1
	collect_value		10
	get_value		7,8
	get_value		5,6
	get_value		3,4
	get_value		1,2
	proceed
mrb_body_code_10_1:
	suspend		mrb_body_code_10_0
	module_entry		kl1cmp_mrb
	predicate		mrb_one_body_code,5
mrb_one_body_code_5_0:
	try_me_else		mrb_one_body_code_5_1
	vector		5
	jump_on_arity		5,4,mrb_one_body_code_5_1
	table_entry		mrb_one_body_code_5_1
	table_entry		mrb_one_body_code_5_1
	table_entry		mrb_one_body_code_5_3
	table_entry		mrb_one_body_code_5_4
mrb_one_body_code_5_3:
	read_element		5,0,6
	atom		6
	branch_on_atom		6,2,mrb_one_body_code_5_1
	bucket_entry_a		write_value,mrb_one_body_code_5_6
	bucket_entry_a		write_variable,mrb_one_body_code_5_7
mrb_one_body_code_5_6:
	read_element		5,1,7
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,8
	set_variable		4,6
	set_marked_value		5,7
	put_reused_func		1,5,write_value
	write_element_value		1,1,7
	set_value		6,1
	put_func		1,2,write_marked_value
	write_element_value		1,1,7
	set_value		7,1
	enqueue_goal		7,mrb_black_or_white_val_7_0
	put_values_inc		1,3,2
	put_values_inc		3,7,2
	put_value		5,6
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_7:
	read_element		5,1,7
	create_goal		5
	set_values_inc		1,1,2
	set_variable		3,6
	put_reused_func		1,5,write_variable
	write_element_marked_value		1,1,7
	set_value		4,1
	put_func		1,2,write_marked_variable
	write_element_value		1,1,7
	set_value		5,1
	enqueue_goal		5,mrb_black_or_white_var_5_0
	put_values_inc		1,3,2
	put_values_dec		3,7,2
	execute		4,seen_n_times_4_0
mrb_one_body_code_5_4:
	read_element		5,0,6
	atom		6
	hash_on_atom		6,9,mrb_one_body_code_5_1
	bucket_entry_a		get_constant,mrb_one_body_code_5_9
	bucket_entry_a		get_list_value,mrb_one_body_code_5_10
	bucket_entry_a		get_value,mrb_one_body_code_5_11
	bucket_entry_a		get_vector_value,mrb_one_body_code_5_12
	bucket_entry_a		put_value,mrb_one_body_code_5_13
	bucket_entry_a		put_variable,mrb_one_body_code_5_14
	bucket_entry_a		set_value,mrb_one_body_code_5_15
	bucket_entry_a		set_variable,mrb_one_body_code_5_16
	bucket_entry_a		trans_value,mrb_one_body_code_5_17
mrb_one_body_code_5_9:
	read_elements_inc		5,1,7,2
	put_reused_func		5,5,get_constant
	write_element_value		5,1,7
	write_element_marked_value		5,2,8
	put_list_val_val		6,5,2
	create_goal		5
	set_value		1,1
	set_value		2,6
	set_value		3,8
	set_variable		4,6
	set_variable		5,5
	enqueue_goal		5,mark_or_not_get_constant_arg_5_0
	put_values_inc		1,3,2
	put_value		3,8
	put_value		4,6
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_10:
	read_elements_inc		5,1,7,2
	put_reused_func		5,5,get_list_value
	write_element_marked_value		5,1,7
	write_element_marked_value		5,2,8
	put_list_val_val		6,5,2
	create_goal		8
	set_value		1,1
	set_values_inc		2,6,3
	set_variable		5,6
	set_variable		6,5
	set_variable		7,9
	set_variable		8,1
	enqueue_goal		8,mark_or_not_get_arg_8_0
	create_goal		5
	set_variable		1,2
	set_value		2,4
	set_values_inc		3,8,2
	set_value		5,1
	enqueue_goal		5,seen_n_times_5_0
	put_value		1,3
	put_values_dec		3,7,2
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_11:
	read_elements_inc		5,1,7,2
	put_reused_func		5,5,get_value
	write_element_marked_value		5,1,7
	write_element_marked_value		5,2,8
	put_list_val_val		6,5,2
	create_goal		8
	set_value		1,1
	set_values_inc		2,6,3
	set_variable		5,6
	set_variable		6,5
	set_variable		7,9
	set_variable		8,1
	enqueue_goal		8,mark_or_not_get_arg_8_0
	create_goal		5
	set_variable		1,2
	set_value		2,4
	set_values_inc		3,8,2
	set_value		5,1
	enqueue_goal		5,seen_n_times_5_0
	put_value		1,3
	put_values_dec		3,7,2
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_12:
	read_elements_inc		5,1,7,2
	put_reused_func		5,5,get_vector_value
	write_element_marked_value		5,1,7
	write_element_marked_value		5,2,8
	put_list_val_val		6,5,2
	create_goal		8
	set_value		1,1
	set_values_inc		2,6,3
	set_variable		5,6
	set_variable		6,5
	set_variable		7,9
	set_variable		8,1
	enqueue_goal		8,mark_or_not_get_arg_8_0
	create_goal		5
	set_variable		1,2
	set_value		2,4
	set_values_inc		3,8,2
	set_value		5,1
	enqueue_goal		5,seen_n_times_5_0
	put_value		1,3
	put_values_dec		3,7,2
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_13:
	read_elements_inc		5,1,7,2
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,9
	set_variable		4,6
	set_marked_value		5,7
	put_reused_func		1,5,put_value
	write_element_value		1,1,7
	write_element_marked_value		1,2,8
	set_value		6,1
	put_func		1,3,put_marked_value
	write_elements_inc		1,1,7,2
	set_value		7,1
	enqueue_goal		7,mrb_black_or_white_val_7_0
	put_values_inc		1,3,2
	put_value		3,7
	put_value		4,9
	put_value		5,6
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_14:
	read_elements_inc		5,1,7,2
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,6
	set_variable		4,1
	put_reused_func		2,5,put_variable
	write_element_marked_value		2,1,7
	write_element_marked_value		2,2,8
	set_value		5,2
	put_func		2,3,put_marked_variable
	write_elements_inc		2,1,7,2
	set_value		6,2
	put_func		2,3,put_marked_variable
	write_elements_dec		2,1,8,2
	set_value		7,2
	enqueue_goal		7,mrb_black_or_white_var_7_0
	create_goal		4
	set_variable		1,2
	set_value		2,4
	set_value		3,8
	set_value		4,1
	enqueue_goal		4,seen_n_times_4_0
	put_value		1,3
	put_values_dec		3,7,2
	execute		4,seen_n_times_4_0
mrb_one_body_code_5_15:
	read_elements_inc		5,1,7,2
	create_goal		7
	set_values_inc		1,1,2
	set_variable		3,9
	set_variable		4,6
	set_marked_value		5,7
	put_reused_func		1,5,set_value
	write_element_value		1,1,7
	write_element_marked_value		1,2,8
	set_value		6,1
	put_func		1,3,set_marked_value
	write_elements_inc		1,1,7,2
	set_value		7,1
	enqueue_goal		7,mrb_black_or_white_val_7_0
	put_values_inc		1,3,2
	put_value		3,7
	put_value		4,9
	put_value		5,6
	execute		5,seen_n_times_5_0
mrb_one_body_code_5_16:
	read_elements_inc		5,1,7,2
	create_goal		5
	set_values_inc		1,1,2
	set_variable		3,6
	put_reused_func		1,5,set_variable
	write_element_marked_value		1,1,7
	write_element_marked_value		1,2,8
	set_value		4,1
	put_func		1,3,set_marked_variable
	write_elements_inc		1,1,7,2
	set_value		5,1
	enqueue_goal		5,mrb_black_or_white_var_5_0
	put_values_inc		1,3,2
	put_values_dec		3,7,2
	execute		4,seen_n_times_4_0
mrb_one_body_code_5_17:
	read_elements_inc		5,1,7,2
	get_value		3,4
	put_reused_func		3,5,trans_value
	write_elements_inc		3,1,7,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
mrb_one_body_code_5_1:
	otherwise		mrb_one_body_code_5_0
	get_value		3,4
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
mrb_one_body_code_5_24:
	suspend		mrb_one_body_code_5_0
	module_entry		kl1cmp_mrb
	predicate		seen_n_times,4
seen_n_times_4_0:
	try_me_else		seen_n_times_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,-
	read_elements_inc		1,1,5,2
	wait_vector		3,3
	read_element		3,0,7
	wait_atom		7,'$VAR'
	read_elements_inc		3,1,7,2
	collect_value		8
	collect_vector		3
	put_integer		3,0
	b_set_vector_element		6,7,6,3,3
	get_value		6,4
	put_reused_func		1,1,-
	write_element_value		1,1,5
	write_element_value		1,2,3
	get_vector_value		2,1
	proceed
seen_n_times_4_1:
	suspend		seen_n_times_4_0
	module_entry		kl1cmp_mrb
	predicate		seen_n_times,5
seen_n_times_5_0:
	try_me_else		seen_n_times_5_1
	wait_vector		1,3
	read_element		1,0,6
	wait_atom		6,-
	read_elements_inc		1,1,6,2
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	collect_value		9
	collect_vector		3
	put_marked_value		3,8
	put_integer		9,0
	b_set_vector_element		6,3,6,9,3
	get_value		6,4
	put_integer		4,0
	b_set_vector_element		7,8,6,4,4
	get_value		6,5
	put_reused_func		1,1,-
	write_elements_inc		1,1,3,2
	get_vector_value		2,1
	proceed
seen_n_times_5_1:
	suspend		seen_n_times_5_0
	module_entry		kl1cmp_mrb
	predicate		mark_or_not_get_arg,8
mark_or_not_get_arg_8_0:
	try_me_else		mark_or_not_get_arg_8_1
	integer		5
	integer		6
	try_me_else		mark_or_not_get_arg_8_4
	put_integer		9,0
	g_equal		5,9
	put_integer		9,2
	g_less_than		9,6
	collect_value		8
	collect_value		7
	put_func		5,3,put_marked_value
	write_element_marked_value		5,1,4
	write_element_value		5,2,4
	put_list_val_val		4,5,2
	put_func		2,3,put_marked_value
	write_element_marked_value		2,1,3
	write_element_value		2,2,3
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
mark_or_not_get_arg_8_4:
	try_me_else		mark_or_not_get_arg_8_1
	put_integer		9,1
	g_equal		5,9
	put_integer		9,1
	g_less_than		9,6
	collect_value		8
	collect_value		7
	put_func		5,3,put_marked_value
	write_element_marked_value		5,1,4
	write_element_value		5,2,4
	put_list_val_val		4,5,2
	put_func		2,3,put_marked_value
	write_element_marked_value		2,1,3
	write_element_value		2,2,3
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
mark_or_not_get_arg_8_1:
	try_me_else		mark_or_not_get_arg_8_5
	integer		7
	integer		8
	try_me_else		mark_or_not_get_arg_8_8
	put_integer		9,0
	g_equal		7,9
	put_integer		9,2
	g_less_than		9,8
	collect_value		6
	collect_value		5
	put_func		5,3,put_marked_value
	write_element_marked_value		5,1,4
	write_element_value		5,2,4
	put_list_val_val		4,5,2
	put_func		2,3,put_marked_value
	write_element_marked_value		2,1,3
	write_element_value		2,2,3
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
mark_or_not_get_arg_8_8:
	try_me_else		mark_or_not_get_arg_8_5
	put_integer		9,1
	g_equal		7,9
	put_integer		9,1
	g_less_than		9,8
	collect_value		6
	collect_value		5
	put_func		5,3,put_marked_value
	write_element_marked_value		5,1,4
	write_element_value		5,2,4
	put_list_val_val		4,5,2
	put_func		2,3,put_marked_value
	write_element_marked_value		2,1,3
	write_element_value		2,2,3
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
mark_or_not_get_arg_8_5:
	otherwise		mark_or_not_get_arg_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
mark_or_not_get_arg_8_18:
	suspend		mark_or_not_get_arg_8_0
	module_entry		kl1cmp_mrb
	predicate		mark_or_not_get_constant_arg,5
mark_or_not_get_constant_arg_5_0:
	try_me_else		mark_or_not_get_constant_arg_5_1
	integer		4
	jump_on_integer		4,2,mark_or_not_get_constant_arg_5_1
	table_entry		mark_or_not_get_constant_arg_5_3
	table_entry		mark_or_not_get_constant_arg_5_4
mark_or_not_get_constant_arg_5_3:
	integer		5
	put_integer		6,2
	g_less_than		6,5
	put_func		4,3,put_marked_value
	write_element_marked_value		4,1,3
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
mark_or_not_get_constant_arg_5_4:
	integer		5
	put_integer		6,1
	g_less_than		6,5
	put_func		4,3,put_marked_value
	write_element_marked_value		4,1,3
	write_element_value		4,2,3
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
mark_or_not_get_constant_arg_5_1:
	otherwise		mark_or_not_get_constant_arg_5_0
	collect_value		5
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
mark_or_not_get_constant_arg_5_7:
	suspend		mark_or_not_get_constant_arg_5_0
	module_entry		kl1cmp_mrb
	predicate		mrb_black_or_white_var,5
mrb_black_or_white_var_5_0:
	try_me_else		mrb_black_or_white_var_5_1
	integer		3
	try_me_else		mrb_black_or_white_var_5_3
	put_integer		6,2
	g_less_than		6,3
	collect_value		4
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
mrb_black_or_white_var_5_3:
	collect_value		5
	put_list_val_val		3,4,2
	get_list_value		1,3
	proceed
mrb_black_or_white_var_5_1:
	suspend		mrb_black_or_white_var_5_0
	module_entry		kl1cmp_mrb
	predicate		mrb_black_or_white_var,7
mrb_black_or_white_var_7_0:
	try_me_else		mrb_black_or_white_var_7_1
	integer		3
	try_me_else		mrb_black_or_white_var_7_3
	integer		4
	put_integer		8,2
	g_not_less_than		8,4
	put_integer		8,2
	g_not_less_than		8,3
	collect_value		7
	collect_value		6
	put_list_val_val		3,5,2
	get_list_value		1,3
	proceed
mrb_black_or_white_var_7_3:
	try_me_else		mrb_black_or_white_var_7_1
	put_integer		8,2
	g_less_than		8,3
	collect_value		7
	collect_value		5
	collect_value		4
	put_list_val_val		3,6,2
	get_list_value		1,3
	proceed
mrb_black_or_white_var_7_1:
	try_me_else		mrb_black_or_white_var_7_5
	integer		4
	put_integer		8,2
	g_less_than		8,4
	collect_value		6
	collect_value		5
	collect_value		3
	put_list_val_val		3,7,2
	get_list_value		1,3
	proceed
mrb_black_or_white_var_7_5:
	suspend		mrb_black_or_white_var_7_0
	module_entry		kl1cmp_mrb
	predicate		mrb_black_or_white_val,7
mrb_black_or_white_val_7_0:
	try_me_else		mrb_black_or_white_val_7_1
	integer		3
	integer		4
	try_me_else		mrb_black_or_white_val_7_4
	put_integer		8,1
	g_equal		3,8
	put_integer		8,1
	g_less_than		8,4
	collect_value		6
	collect_value		5
	put_list_val_val		3,7,2
	get_list_value		1,3
	proceed
mrb_black_or_white_val_7_4:
	try_me_else		mrb_black_or_white_val_7_1
	put_integer		8,0
	g_equal		3,8
	put_integer		8,2
	g_less_than		8,4
	collect_value		6
	collect_value		5
	put_list_val_val		3,7,2
	get_list_value		1,3
	proceed
mrb_black_or_white_val_7_1:
	otherwise		mrb_black_or_white_val_7_0
	collect_value		7
	collect_value		5
	collect_value		4
	collect_value		3
	put_list_val_val		3,6,2
	get_list_value		1,3
	proceed
mrb_black_or_white_val_7_10:
	suspend		mrb_black_or_white_val_7_0
	module_entry		kl1cmp_mrb
	predicate		first_and_latest_occurrence,7
first_and_latest_occurrence_7_0:
	try_me_else		first_and_latest_occurrence_7_1
	wait_vector		5,3
	read_element		5,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		5,1,8,2
	collect_value		9
	collect_vector		5
	put_marked_value		5,8
	put_marked_value		9,6
	b_set_vector_element		1,5,1,9,5
	get_value		1,6
	get_value		5,2
	put_marked_value		1,7
	b_set_vector_element		3,8,1,1,2
	get_value		1,7
	get_value		2,4
	proceed
first_and_latest_occurrence_7_1:
	otherwise		first_and_latest_occurrence_7_0
	collect_value		5
	get_nil		6
	get_nil		7
	get_value		1,2
	get_value		3,4
	proceed
first_and_latest_occurrence_7_6:
	suspend		first_and_latest_occurrence_7_0
	module_entry		kl1cmp_mrb
	predicate		'$compile_for_pdss/6_0',3
'$compile_for_pdss/6_0_3_0':
	try_me_else		'$compile_for_pdss/6_0_3_1'
	atom		3
	branch_on_atom		3,2,'$compile_for_pdss/6_0_3_1'
	bucket_entry_a		error,'$compile_for_pdss/6_0_3_3'
	bucket_entry_a		non_error,'$compile_for_pdss/6_0_3_4'
'$compile_for_pdss/6_0_3_3':
	collect_value		2
	get_atom		1,error
	proceed
'$compile_for_pdss/6_0_3_4':
	get_value		1,2
	proceed
'$compile_for_pdss/6_0_3_1':
	suspend		'$compile_for_pdss/6_0_3_0'
	module_entry		kl1cmp_mrb
	predicate		latest_occurrence,4
latest_occurrence_4_0:
	try_me_else		latest_occurrence_4_1
	wait_vector		3,3
	read_element		3,0,5
	wait_atom		5,'$VAR'
	read_elements_inc		3,1,5,2
	collect_value		6
	collect_vector		3
	put_marked_value		3,4
	b_set_vector_element		1,5,1,3,3
	get_value		1,4
	get_value		3,2
	proceed
latest_occurrence_4_1:
	suspend		latest_occurrence_4_0
	module_entry		kl1cmp_mrb
	predicate		compile_for_pdss,6
compile_for_pdss_6_0:
	b_merge		11,7
	put_vector		12,3
	write_element_variable		12,0,9
	write_element_variable		12,1,10
	write_element_variable		12,2,8
	get_vector_value		11,12
	create_goal		3
	set_value		1,6
	set_variable		2,11
	set_variable		3,6
	enqueue_goal		3,'$compile_for_pdss/6_0_3_0'
	create_goal		7
	set_value		1,3
	put_func		3,2,close
	write_element_value		3,1,11
	put_list		11
	write_car_value		11,3
	write_cdr_nil		11
	set_value		2,11
	set_value		3,4
	set_nil		4
	set_atom		5,non_error
	set_values_inc		6,6,2
	enqueue_goal_external		kl1cmp_command,message_distributer,7
	create_goal		5
	set_value		1,2
	set_nil		2
	set_value		3,10
	set_nil		4
	set_variable		5,3
	enqueue_goal_external		kl1cmp_reader,create_reader,5
	put_integer		2,-1024
	b_rltv		2,2
	create_goal		8
	set_value		1,3
	set_nil		2
	set_value		3,9
	set_nil		4
	set_value		5,8
	set_nil		6
	set_value		7,1
	set_value		8,5
	enqueue_goal_with_priority		8,'$kl1cmp_command:ghccompile/8_8_0',2
	proceed
compile_for_pdss_6_1:
	suspend		compile_for_pdss_6_0
	module_entry		kl1cmp_mrb
	predicate		unique,3
unique_3_0:
	try_me_else		unique_3_1
	jump_on_non_list_var_var		3,unique_3_3,4,5
	put_reused_list		6,3
	write_car_marked_value		6,4
	write_cdr_variable		6,3
	get_list_value		1,6
	create_goal		3
	set_values_dec		1,3,2
	set_variable		3,1
	enqueue_goal		3,unique_3_0
	put_nil		2
	put_values_inc		3,4,2
	execute		4,unique_4_0
unique_3_3:
	check_nil		3,unique_3_1
	get_value		1,2
	proceed
unique_3_1:
	suspend		unique_3_0
	module_entry		kl1cmp_mrb
	predicate		unique,4
unique_4_0:
	try_me_else		unique_4_1
	jump_on_non_list		4,unique_4_3
	read_car		4,6
	wait_value		6,3
	read_cdr		4,5
	collect_list		4
	collect_value		6
	put_value		4,5
	execute		4,unique_4_0
unique_4_3:
	check_nil		4,unique_4_1
	collect_value		3
	get_value		1,2
	proceed
unique_4_1:
	otherwise		unique_4_0
	try_me_else		unique_4_8
	wait_list_var_var		4,5,6
	get_reused_list_val_var		1,7,4,5,4
	put_value		1,4
	put_value		4,6
	execute		4,unique_4_0
unique_4_8:
	suspend		unique_4_0
	module_entry		kl1cmp_mrb
	predicate		'$kl1cmp_command:ghccompile/8',8
'$kl1cmp_command:ghccompile/8_8_0':
	execute_external		kl1cmp_command,ghccompile,8
'$kl1cmp_command:ghccompile/8_8_1':
	suspend		'$kl1cmp_command:ghccompile/8_8_0'
