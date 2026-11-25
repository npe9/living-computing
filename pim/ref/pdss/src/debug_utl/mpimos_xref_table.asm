mpimos_xref_table:
	module		mpimos_xref_table
	entry		predicate_table,4,predicate_table_4_0
	entry		module_table,7,module_table_7_0
	entry		init_module_table,2,init_module_table_2_0
	module_entry		mpimos_xref_table
	predicate		predicate_table,4
predicate_table_4_0:
	b_merge		6,5
	get_value		6,3
	put_integer		3,16
	b_new_vector		3,3
	create_goal		7
	set_values_inc		1,1,2
	set_value		3,5
	set_variable		4,5
	set_value		5,4
	set_nil		6
	set_integer		7,1
	enqueue_goal		7,predicate_7_0
	put_integer		1,0
	put_integer		2,16
	put_value		4,5
	execute		4,set_nil_4_0
predicate_table_4_1:
	suspend		predicate_table_4_0
	module_entry		mpimos_xref_table
	predicate		predicate,7
predicate_7_0:
	try_me_else		predicate_7_1
	jump_on_non_list		3,predicate_7_3
	read_car		3,8
	wait_vector		8,4
	read_element		8,0,9
	atom		9
	branch_on_atom		9,2,predicate_7_1
	bucket_entry_a		call,predicate_7_6
	bucket_entry_a		entry,predicate_7_7
predicate_7_6:
	read_cdr		3,10
	read_elements_inc		8,1,11,3
	collect_vector		8
	put_vector		8,3
	write_elements_inc		8,0,11,3
	put_reused_list_val_val		9,3,8,6
	put_value		3,10
	put_value		6,9
	execute		7,predicate_7_0
predicate_7_7:
	read_cdr		3,10
	read_elements_inc		8,1,11,3
	collect_list		3
	collect_vector		8
	put_vector		3,3
	write_element_variable		3,0,8
	write_element_marked_value		3,1,11
	write_element_marked_value		3,2,12
	get_vector_value		13,3
	create_goal		7
	set_values_inc		1,1,2
	set_value		3,10
	set_variable		4,3
	set_values_inc		5,5,2
	set_variable		7,1
	enqueue_goal		7,predicate_7_0
	create_goal		7
	set_value		1,7
	set_value		2,1
	set_variable		3,5
	set_variable		4,6
	set_values_inc		5,11,2
	set_value		7,8
	enqueue_goal		7,entry_table_7_0
	put_value		1,11
	put_value		2,4
	put_value		4,6
	execute		5,get_list_from_table_5_0
predicate_7_3:
	check_nil		3,predicate_7_1
	collect_value		7
	put_func		3,2,flush
	write_element_void		3,1
	put_list_val_var		7,3,8
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,7
	put_structured_constant		7,'$SCNST_0'
	put_list_val_val		9,7,3
	get_list_value		1,9
	put_value		1,8
	put_values_inc		3,4,3
	execute		5,predicate_reference_5_0
predicate_7_1:
	suspend		predicate_7_0
	module_entry		mpimos_xref_table
	predicate		entry_table,7
entry_table_7_0:
	try_me_else		entry_table_7_1
	jump_on_non_list_var_var		4,entry_table_7_3,8,9
	vector		8
	put_integer		10,1
	g_vector_element		8,10,10
	wait_value		5,10
	put_integer		10,2
	g_vector_element		8,10,10
	wait_value		6,10
	get_value		1,2
	put_reused_list_val_val		1,4,8,9
	get_list_value		3,1
	get_atom		7,doubly
	proceed
entry_table_7_3:
	check_nil		4,entry_table_7_1
	put_nil		8
	put_vector		4,4
	write_element_marked_value		4,0,1
	write_element_marked_value		4,1,5
	write_element_marked_value		4,2,6
	write_element_nil		4,3
	put_list_val_val		9,4,8
	get_list_value		3,9
	b_increment		1,1
	get_value		1,2
	put_values_inc		1,5,3
	execute		3,check_builtin_type_3_0
entry_table_7_1:
	otherwise		entry_table_7_0
	try_me_else		entry_table_7_8
	wait_list_var_var		4,8,9
	get_reused_list_val_var		3,10,4,8,4
	put_value		3,4
	put_value		4,9
	execute		7,entry_table_7_0
entry_table_7_8:
	suspend		entry_table_7_0
	module_entry		mpimos_xref_table
	predicate		predicate_reference,5
predicate_reference_5_0:
	b_merge		6,7
	create_goal		3
	set_variable		1,8
	set_value		2,2
	set_marked_value		3,4
	enqueue_goal		3,uncalled_predicate_3_0
	create_goal		3
	set_value		1,1
	set_values_dec		2,8,2
	enqueue_goal		3,undefined_predicate_3_0
	put_values_inc		1,3,2
	put_values_dec		3,6,2
	execute		4,predicate_reference_entry_4_0
predicate_reference_5_1:
	suspend		predicate_reference_5_0
	module_entry		mpimos_xref_table
	predicate		predicate_reference_entry,4
predicate_reference_entry_4_0:
	try_me_else		predicate_reference_entry_4_1
	jump_on_non_list_var_var		4,predicate_reference_entry_4_3,9,5
	wait_vector		9,3
	read_elements_inc		9,0,6,3
	collect_list		4
	collect_vector		9
	put_value		9,1
	put_vector		10,2
	write_element_variable		10,0,4
	write_element_variable		10,1,1
	get_vector_value		3,10
	create_goal		4
	set_variable		1,3
	set_value		2,2
	set_values_inc		3,4,2
	enqueue_goal		4,predicate_reference_entry_4_0
	create_goal		6
	set_variable		1,5
	set_value		2,1
	set_variable		3,4
	set_marked_value		4,6
	set_values_inc		5,7,2
	enqueue_goal		6,predicate_ref_entry_list_6_0
	put_value		1,6
	put_value		2,9
	execute		5,get_list_from_table_5_0
predicate_reference_entry_4_3:
	check_nil		4,predicate_reference_entry_4_1
	get_nil		3
	get_value		1,2
	proceed
predicate_reference_entry_4_1:
	suspend		predicate_reference_entry_4_0
	module_entry		mpimos_xref_table
	predicate		predicate_ref_entry_list,6
predicate_ref_entry_list_6_0:
	try_me_else		predicate_ref_entry_list_6_1
	jump_on_non_list_var_var		3,predicate_ref_entry_list_6_3,7,8
	vector		7
	put_integer		9,1
	g_vector_element		7,9,9
	wait_value		4,9
	put_integer		9,2
	g_vector_element		7,9,9
	wait_value		5,9
	get_nil		2
	put_integer		4,3
	put_reused_list_val_var		2,3,6,3
	b_set_vector_element		7,4,4,2,2
	get_value		4,3
	put_list_val_val		3,2,8
	get_list_value		1,3
	proceed
predicate_ref_entry_list_6_3:
	check_nil		3,predicate_ref_entry_list_6_1
	get_nil		1
	put_nil		3
	put_vector		1,3
	write_elements_inc		1,0,4,3
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
predicate_ref_entry_list_6_1:
	otherwise		predicate_ref_entry_list_6_0
	try_me_else		predicate_ref_entry_list_6_8
	wait_list_var_var		3,7,8
	get_reused_list_val_var		1,9,3,7,3
	put_value		1,3
	put_value		3,8
	execute		6,predicate_ref_entry_list_6_0
predicate_ref_entry_list_6_8:
	suspend		predicate_ref_entry_list_6_0
	module_entry		mpimos_xref_table
	predicate		undefined_predicate,3
undefined_predicate_3_0:
	try_me_else		undefined_predicate_3_1
	jump_on_non_list_var_var		3,undefined_predicate_3_3,11,4
	wait_vector		11,3
	read_elements_inc		11,0,5,3
	put_func		8,2,flush
	write_element_void		8,1
	put_reused_list_val_var		3,3,8,10
	put_structured_constant		8,'$SCNST_1'
	put_list_val_val		9,8,3
	put_func		3,2,putt
	write_element_value		3,1,7
	put_list_val_val		7,3,9
	put_structured_constant		3,'$SCNST_2'
	put_list_val_val		8,3,7
	put_reused_func		3,11,/
	write_elements_inc		3,1,5,2
	put_func		5,2,putt
	write_element_value		5,1,3
	put_list_val_val		3,5,8
	put_structured_constant		5,'$SCNST_3'
	put_list_val_val		6,5,3
	get_list_value		1,6
	put_value		1,10
	put_value		3,4
	execute		3,undefined_predicate_3_0
undefined_predicate_3_3:
	check_nil		3,undefined_predicate_3_1
	get_value		1,2
	proceed
undefined_predicate_3_1:
	suspend		undefined_predicate_3_0
	module_entry		mpimos_xref_table
	predicate		uncalled_predicate,3
uncalled_predicate_3_0:
	b_merge		5,4
	get_value		5,3
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,3
	enqueue_goal		3,uncalled_predicate_list_3_0
	put_value		1,4
	put_integer		2,0
	execute_external		mpimos_utility,qsortv,3
uncalled_predicate_3_1:
	suspend		uncalled_predicate_3_0
	module_entry		mpimos_xref_table
	predicate		uncalled_predicate_list,3
uncalled_predicate_list_3_0:
	try_me_else		uncalled_predicate_list_3_1
	jump_on_non_list_var_var		3,uncalled_predicate_list_3_3,9,4
	wait_vector		9,4
	read_elements_inc		9,0,5,4
	collect_list		3
	collect_value		5
	collect_vector		9
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,uncalled_predicate_list_3_0
	create_goal		5
	set_value		1,1
	set_value		2,3
	set_marked_value		3,6
	set_marked_value		4,7
	set_variable		5,4
	enqueue_goal		5,uncalled_predicate_warning_5_0
	put_values_inc		1,6,3
	execute		4,self_check_4_0
uncalled_predicate_list_3_3:
	check_nil		3,uncalled_predicate_list_3_1
	get_value		1,2
	proceed
uncalled_predicate_list_3_1:
	suspend		uncalled_predicate_list_3_0
	module_entry		mpimos_xref_table
	predicate		self_check,4
self_check_4_0:
	try_me_else		self_check_4_1
	jump_on_non_list_var_var		3,self_check_4_3,7,5
	wait_vector		7,3
	read_element		7,0,6
	wait_atom		6,/
	read_element		7,1,8
	read_element		7,2,6
	wait_vector		8,3
	read_element		8,0,9
	wait_atom		9,/
	read_element		8,1,9
	wait_value		9,1
	read_element		8,2,10
	wait_value		10,2
	collect_list		3
	collect_value		6
	collect_value		9
	collect_value		10
	collect_vector		7
	collect_vector		8
	put_value		3,5
	execute		4,self_check_4_0
self_check_4_3:
	check_nil		3,self_check_4_1
	collect_value		2
	collect_value		1
	get_atom		4,none
	proceed
self_check_4_1:
	otherwise		self_check_4_0
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		4,called
	proceed
self_check_4_8:
	suspend		self_check_4_0
	module_entry		mpimos_xref_table
	predicate		uncalled_predicate_warning,5
uncalled_predicate_warning_5_0:
	try_me_else		uncalled_predicate_warning_5_1
	atom		5
	branch_on_atom		5,2,uncalled_predicate_warning_5_1
	bucket_entry_a		called,uncalled_predicate_warning_5_3
	bucket_entry_a		none,uncalled_predicate_warning_5_4
uncalled_predicate_warning_5_3:
	collect_value		4
	collect_value		3
	get_value		1,2
	proceed
uncalled_predicate_warning_5_4:
	put_structured_constant		5,'$SCNST_4'
	put_list_val_val		6,5,2
	put_func		2,3,/
	write_elements_inc		2,1,3,2
	put_func		3,2,putt
	write_element_value		3,1,2
	put_list_val_val		2,3,6
	put_structured_constant		3,'$SCNST_5'
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
uncalled_predicate_warning_5_1:
	suspend		uncalled_predicate_warning_5_0
	module_entry		mpimos_xref_table
	predicate		module_table,7
module_table_7_0:
	b_merge		9,8
	get_value		9,3
	put_integer		3,16
	b_new_vector		3,3
	put_integer		9,16
	b_new_vector		9,9
	put_integer		10,16
	b_new_vector		10,10
	create_goal		14
	set_values_inc		1,1,2
	set_value		3,8
	set_variable		4,8
	set_value		5,4
	set_nil		6
	set_variable		7,1
	set_value		8,5
	set_nil		9
	set_variable		10,2
	set_value		11,6
	set_nil		12
	set_integer		13,1
	set_value		14,7
	enqueue_goal		14,module_14_0
	create_goal		4
	set_integer		1,0
	set_integer		2,16
	set_value		3,10
	set_value		4,2
	enqueue_goal		4,set_nil_4_0
	create_goal		4
	set_integer		1,0
	set_integer		2,16
	set_value		3,9
	set_value		4,1
	enqueue_goal		4,set_nil_4_0
	put_integer		1,0
	put_integer		2,16
	put_value		4,8
	execute		4,set_nil_4_0
module_table_7_1:
	suspend		module_table_7_0
	module_entry		mpimos_xref_table
	predicate		module,14
module_14_0:
	try_me_else		module_14_1
	jump_on_non_list		3,module_14_3
	read_car		3,15
	vector		15
	jump_on_arity		15,7,module_14_1
	table_entry		module_14_1
	table_entry		module_14_1
	table_entry		module_14_1
	table_entry		module_14_5
	table_entry		module_14_6
	table_entry		module_14_7
	table_entry		module_14_8
module_14_5:
	read_cdr		3,16
	read_element		15,0,17
	wait_atom		17,entry
	read_elements_inc		15,1,17,2
	collect_list		3
	collect_vector		15
	create_goal		14
	set_values_inc		1,1,2
	set_value		3,16
	set_variable		4,2
	set_values_inc		5,5,8
	set_variable		13,5
	set_marked_value		14,14
	enqueue_goal		14,module_14_0
	put_value		1,4
	put_value		3,13
	put_value		4,5
	put_values_inc		5,17,2
	put_vector		7,0
	put_nil		8
	put_value		9,14
	put_void		10
	execute		10,module_entry_table_10_0
module_14_6:
	read_element		15,0,16
	atom		16
	branch_on_atom		16,2,module_14_1
	bucket_entry_a		body_builtin,module_14_10
	bucket_entry_a		guard_builtin,module_14_11
module_14_10:
	read_cdr		3,17
	read_elements_inc		15,1,18,3
	collect_vector		15
	put_vector		15,3
	write_elements_inc		15,0,18,3
	put_reused_list_val_val		16,3,15,12
	put_value		3,17
	put_value		12,16
	execute		14,module_14_0
module_14_11:
	read_cdr		3,17
	read_elements_inc		15,1,18,3
	collect_vector		15
	put_vector		15,3
	write_elements_inc		15,0,18,3
	put_reused_list_val_val		16,3,15,9
	put_value		3,17
	put_value		9,16
	execute		14,module_14_0
module_14_7:
	read_cdr		3,16
	read_element		15,0,17
	wait_atom		17,call
	read_elements_inc		15,1,17,4
	collect_vector		15
	put_vector		15,4
	write_elements_inc		15,0,17,4
	put_reused_list_val_val		17,3,15,6
	put_value		3,16
	put_value		6,17
	execute		14,module_14_0
module_14_8:
	read_cdr		3,16
	read_element		15,0,17
	wait_atom		17,entry
	read_elements_inc		15,1,17,5
	collect_list		3
	collect_vector		15
	create_goal		14
	set_values_inc		1,1,2
	set_value		3,16
	set_variable		4,2
	set_values_inc		5,5,8
	set_variable		13,5
	set_marked_value		14,14
	enqueue_goal		14,module_14_0
	put_value		1,4
	put_value		3,13
	put_value		4,5
	put_values_inc		5,17,4
	put_value		9,14
	put_value		10,21
	execute		10,module_entry_table_10_0
module_14_3:
	check_nil		3,module_14_1
	collect_value		14
	collect_value		13
	create_goal		3
	set_values_inc		1,10,3
	enqueue_goal		3,builtin_reference_entry_3_0
	create_goal		3
	set_values_inc		1,7,3
	enqueue_goal		3,builtin_reference_entry_3_0
	put_values_inc		3,4,3
	execute		5,module_reference_5_0
module_14_1:
	suspend		module_14_0
	module_entry		mpimos_xref_table
	predicate		module_entry_table,10
module_entry_table_10_0:
	put_value		13,1
	put_value		11,2
	create_goal		10
	set_variable		1,12
	set_values_inc		2,3,2
	set_variable		4,4
	set_marked_value		5,5
	set_values_inc		6,6,5
	enqueue_goal		10,module_entry_list_10_0
	put_value		1,5
	put_value		2,13
	put_value		3,11
	put_value		5,12
	execute		5,get_list_from_table_5_0
module_entry_table_10_1:
	suspend		module_entry_table_10_0
	module_entry		mpimos_xref_table
	predicate		module_entry_list,10
module_entry_list_10_0:
	try_me_else		module_entry_list_10_1
	jump_on_non_list		4,module_entry_list_10_3
	read_car		4,11
	vector		11
	read_cdr		4,12
	atom		9
	branch_on_atom		9,2,module_entry_list_10_1
	bucket_entry_a		protect,module_entry_list_10_6
	bucket_entry_a		update,module_entry_list_10_7
module_entry_list_10_6:
	put_integer		13,1
	g_vector_element		11,13,14
	wait_value		5,14
	mark_element		11,13
	mark_element		11,13
	collect_value		8
	collect_value		7
	collect_value		6
	put_marked_value		5,5
	get_value		2,3
	put_reused_list_val_val		2,4,11,12
	get_list_value		1,2
	put_func		1,2,doubly
	write_element_value		1,1,5
	get_vector_value		10,1
	proceed
module_entry_list_10_7:
	put_integer		13,1
	g_vector_element		11,13,14
	wait_value		5,14
	mark_element		11,13
	mark_element		11,13
	collect_value		11
	put_vector		9,5
	write_element_marked_value		9,0,2
	write_element_marked_value		9,1,5
	write_elements_inc		9,2,6,3
	put_reused_list_val_val		4,4,9,12
	get_list_value		1,4
	b_increment		2,1
	get_value		1,3
	put_func		1,2,success
	write_element_value		1,1,5
	get_vector_value		10,1
	proceed
module_entry_list_10_3:
	check_nil		4,module_entry_list_10_1
	collect_value		9
	put_nil		9
	put_vector		4,5
	write_element_marked_value		4,0,2
	write_element_marked_value		4,1,5
	write_elements_inc		4,2,6,3
	put_list_val_val		6,4,9
	get_list_value		1,6
	b_increment		2,1
	get_value		1,3
	put_func		1,2,success
	write_element_value		1,1,5
	get_vector_value		10,1
	proceed
module_entry_list_10_1:
	otherwise		module_entry_list_10_0
	try_me_else		module_entry_list_10_15
	wait_list_var_var		4,11,12
	get_reused_list_val_var		1,13,4,11,4
	put_value		1,4
	put_value		4,12
	execute		10,module_entry_list_10_0
module_entry_list_10_15:
	suspend		module_entry_list_10_0
	module_entry		mpimos_xref_table
	predicate		module_reference,5
module_reference_5_0:
	b_merge		6,7
	b_merge		8,9
	create_goal		3
	set_variable		1,10
	set_value		2,2
	set_value		3,9
	enqueue_goal		3,undefined_public_3_0
	create_goal		3
	set_value		1,1
	set_value		2,10
	set_value		3,7
	enqueue_goal		3,undefined_module_3_0
	put_values_inc		1,3,2
	put_value		3,6
	put_value		4,8
	execute		5,module_reference_entry_5_0
module_reference_5_1:
	suspend		module_reference_5_0
	module_entry		mpimos_xref_table
	predicate		module_reference_entry,5
module_reference_entry_5_0:
	try_me_else		module_reference_entry_5_1
	jump_on_non_list_var_var		5,module_reference_entry_5_3,11,6
	wait_vector		11,4
	read_elements_inc		11,0,7,4
	collect_list		5
	collect_vector		11
	put_value		13,1
	put_vector		11,2
	write_element_variable		11,0,5
	write_element_variable		11,1,1
	get_vector_value		3,11
	put_vector		3,2
	write_element_variable		3,0,12
	write_element_variable		3,1,11
	get_vector_value		4,3
	create_goal		5
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	set_value		4,12
	set_value		5,6
	enqueue_goal		5,module_reference_entry_5_0
	create_goal		8
	set_variable		1,5
	set_value		2,1
	set_value		3,11
	set_variable		4,4
	set_marked_value		5,7
	set_values_inc		6,8,3
	enqueue_goal		8,module_ref_entry_list_8_0
	put_value		1,7
	put_value		2,13
	execute		5,get_list_from_table_5_0
module_reference_entry_5_3:
	check_nil		5,module_reference_entry_5_1
	get_nil		3
	get_nil		4
	get_value		1,2
	proceed
module_reference_entry_5_1:
	suspend		module_reference_entry_5_0
	module_entry		mpimos_xref_table
	predicate		module_ref_entry_list,8
module_ref_entry_list_8_0:
	try_me_else		module_ref_entry_list_8_1
	jump_on_non_list_var_var		4,module_ref_entry_list_8_3,9,10
	vector		9
	put_integer		11,1
	g_vector_element		9,11,12
	wait_value		5,12
	mark_element		9,11
	mark_element		9,11
	put_value		11,3
	put_marked_value		12,5
	put_values_inc		13,6,3
	get_nil		2
	put_integer		2,2
	put_variable		3,6
	b_set_vector_element		9,2,5,3,2
	put_integer		3,3
	put_variable		8,7
	b_set_vector_element		2,3,2,8,3
	put_reused_list_val_val		4,4,3,10
	get_list_value		1,4
	put_value		1,6
	put_value		3,7
	put_value		4,11
	put_values_inc		6,12,4
	execute		9,public_ref_entry_list_9_0
module_ref_entry_list_8_3:
	check_nil		4,module_ref_entry_list_8_1
	get_nil		1
	put_nil		4
	get_nil		3
	put_vector		1,4
	write_elements_inc		1,0,5,4
	put_list_val_val		3,1,4
	get_list_value		2,3
	proceed
module_ref_entry_list_8_1:
	otherwise		module_ref_entry_list_8_0
	try_me_else		module_ref_entry_list_8_8
	wait_list_var_var		4,9,10
	get_reused_list_val_var		1,11,4,9,4
	put_value		1,4
	put_value		4,10
	execute		8,module_ref_entry_list_8_0
module_ref_entry_list_8_8:
	suspend		module_ref_entry_list_8_0
	module_entry		mpimos_xref_table
	predicate		public_ref_entry_list,9
public_ref_entry_list_9_0:
	try_me_else		public_ref_entry_list_9_1
	jump_on_non_list_var_var		5,public_ref_entry_list_9_3,13,10
	wait_vector		13,2
	read_elements_inc		13,0,11,2
	wait_value		11,7
	wait_value		12,8
	collect_value		6
	collect_value		8
	get_nil		4
	put_reused_vector		4,13
	write_element_marked_value		4,0,11
	write_element_marked_value		4,1,12
	put_reused_list_val_val		5,5,4,10
	get_list_value		1,5
	put_values_inc		1,2,2
	put_values_inc		3,11,2
	put_value		5,9
	execute		5,reference_entry_5_0
public_ref_entry_list_9_3:
	check_nil		5,public_ref_entry_list_9_1
	get_nil		1
	put_nil		5
	get_value		2,3
	put_vector		1,4
	write_elements_inc		1,0,6,4
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
public_ref_entry_list_9_1:
	otherwise		public_ref_entry_list_9_0
	try_me_else		public_ref_entry_list_9_8
	wait_list_var_var		5,10,11
	get_reused_list_val_var		1,12,5,10,5
	put_value		1,5
	put_value		5,11
	execute		9,public_ref_entry_list_9_0
public_ref_entry_list_9_8:
	suspend		public_ref_entry_list_9_0
	module_entry		mpimos_xref_table
	predicate		reference_entry,5
reference_entry_5_0:
	try_me_else		reference_entry_5_1
	wait_vector		1,0
	put_integer		1,16
	b_new_vector		6,1
	create_goal		6
	set_variable		1,1
	set_integer		2,1
	set_variable		3,7
	set_marked_value		4,3
	set_values_inc		5,4,2
	enqueue_goal		6,ref_entry_list_6_0
	create_goal		5
	set_value		1,3
	set_variable		2,4
	set_value		3,2
	set_value		4,7
	set_value		5,1
	enqueue_goal		5,get_list_from_table_5_0
	put_integer		1,0
	put_integer		2,16
	put_value		3,6
	execute		4,set_nil_4_0
reference_entry_5_1:
	otherwise		reference_entry_5_0
	put_values_inc		8,1,2
	create_goal		6
	set_variable		1,6
	set_integer		2,1
	set_variable		3,7
	set_marked_value		4,3
	set_values_inc		5,4,2
	enqueue_goal		6,ref_entry_list_6_0
	put_value		1,3
	put_values_inc		2,8,2
	put_values_dec		4,7,2
	execute		5,get_list_from_table_5_0
reference_entry_5_6:
	suspend		reference_entry_5_0
	module_entry		mpimos_xref_table
	predicate		ref_entry_list,6
ref_entry_list_6_0:
	try_me_else		ref_entry_list_6_1
	jump_on_non_list_var_var		3,ref_entry_list_6_3,7,8
	vector		7
	put_integer		9,1
	g_vector_element		7,9,9
	wait_value		4,9
	put_integer		9,2
	g_vector_element		7,9,9
	wait_value		5,9
	collect_value		2
	put_integer		4,3
	put_reused_list_val_var		2,3,6,3
	b_set_vector_element		7,4,4,2,2
	get_value		4,3
	put_list_val_val		3,2,8
	get_list_value		1,3
	proceed
ref_entry_list_6_3:
	check_nil		3,ref_entry_list_6_1
	put_nil		7
	put_list		3
	write_car_value		3,6
	write_cdr_nil		3
	put_vector		6,4
	write_element_value		6,0,2
	write_elements_inc		6,1,4,2
	write_element_value		6,3,3
	put_list_val_val		2,6,7
	get_list_value		1,2
	proceed
ref_entry_list_6_1:
	otherwise		ref_entry_list_6_0
	try_me_else		ref_entry_list_6_8
	wait_list_var_var		3,7,8
	get_reused_list_val_var		1,9,3,7,3
	b_increment		2,2
	put_value		1,3
	put_value		3,8
	execute		6,ref_entry_list_6_0
ref_entry_list_6_8:
	suspend		ref_entry_list_6_0
	module_entry		mpimos_xref_table
	predicate		undefined_module,3
undefined_module_3_0:
	try_me_else		undefined_module_3_1
	jump_on_non_list_var_var		3,undefined_module_3_3,9,4
	wait_vector		9,4
	read_elements_inc		9,0,5,4
	collect_vector		9
	put_structured_constant		9,'$SCNST_6'
	put_reused_list_val_var		3,3,9,10
	put_func		9,2,putt
	write_element_value		9,1,8
	put_list_val_val		8,9,3
	put_structured_constant		3,'$SCNST_7'
	put_list_val_val		9,3,8
	put_func		3,3,/
	write_elements_inc		3,1,6,2
	put_func		6,3,:
	write_element_value		6,1,5
	write_element_value		6,2,3
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		5,3,9
	put_structured_constant		3,'$SCNST_8'
	put_list_val_val		6,3,5
	get_list_value		1,6
	put_value		1,10
	put_value		3,4
	execute		3,undefined_module_3_0
undefined_module_3_3:
	check_nil		3,undefined_module_3_1
	get_value		1,2
	proceed
undefined_module_3_1:
	suspend		undefined_module_3_0
	module_entry		mpimos_xref_table
	predicate		undefined_public,3
undefined_public_3_0:
	try_me_else		undefined_public_3_1
	jump_on_non_list_var_var		3,undefined_public_3_3,9,4
	wait_vector		9,4
	read_elements_inc		9,0,5,4
	collect_vector		9
	put_structured_constant		9,'$SCNST_9'
	put_reused_list_val_var		3,3,9,10
	put_func		9,2,putt
	write_element_value		9,1,8
	put_list_val_val		8,9,3
	put_structured_constant		3,'$SCNST_10'
	put_list_val_val		9,3,8
	put_func		3,3,/
	write_elements_inc		3,1,6,2
	put_func		6,3,:
	write_element_value		6,1,5
	write_element_value		6,2,3
	put_func		3,2,putt
	write_element_value		3,1,6
	put_list_val_val		5,3,9
	put_structured_constant		3,'$SCNST_11'
	put_list_val_val		6,3,5
	get_list_value		1,6
	put_value		1,10
	put_value		3,4
	execute		3,undefined_public_3_0
undefined_public_3_3:
	check_nil		3,undefined_public_3_1
	get_value		1,2
	proceed
undefined_public_3_1:
	suspend		undefined_public_3_0
	module_entry		mpimos_xref_table
	predicate		builtin_reference_entry,3
builtin_reference_entry_3_0:
	try_me_else		builtin_reference_entry_3_1
	jump_on_non_list_var_var		3,builtin_reference_entry_3_3,8,4
	wait_vector		8,3
	read_elements_inc		8,0,5,3
	collect_list		3
	collect_vector		8
	put_value		9,1
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,builtin_reference_entry_3_0
	create_goal		5
	set_variable		1,8
	set_variable		2,4
	set_marked_value		3,5
	set_values_inc		4,6,2
	enqueue_goal		5,builtin_ref_entry_list_5_0
	put_value		1,5
	put_value		2,9
	put_value		5,8
	execute		5,get_list_from_table_5_0
builtin_reference_entry_3_3:
	check_nil		3,builtin_reference_entry_3_1
	get_value		1,2
	proceed
builtin_reference_entry_3_1:
	suspend		builtin_reference_entry_3_0
	module_entry		mpimos_xref_table
	predicate		builtin_ref_entry_list,5
builtin_ref_entry_list_5_0:
	try_me_else		builtin_ref_entry_list_5_1
	jump_on_non_list_var_var		2,builtin_ref_entry_list_5_3,10,6
	wait_vector		10,3
	read_elements_inc		10,0,7,3
	wait_value		7,3
	wait_value		8,4
	collect_value		4
	put_reused_list_val_val		2,2,5,9
	put_reused_vector		3,10
	write_elements_inc		3,0,7,2
	write_element_value		3,2,2
	put_list_val_val		2,3,6
	get_list_value		1,2
	proceed
builtin_ref_entry_list_5_3:
	check_nil		2,builtin_ref_entry_list_5_1
	put_nil		6
	put_list		2
	write_car_value		2,5
	write_cdr_nil		2
	put_vector		5,3
	write_elements_inc		5,0,3,2
	write_element_value		5,2,2
	put_list_val_val		2,5,6
	get_list_value		1,2
	proceed
builtin_ref_entry_list_5_1:
	otherwise		builtin_ref_entry_list_5_0
	try_me_else		builtin_ref_entry_list_5_8
	wait_list_var_var		2,6,7
	get_reused_list_val_var		1,8,2,6,2
	put_value		1,2
	put_value		2,7
	execute		5,builtin_ref_entry_list_5_0
builtin_ref_entry_list_5_8:
	suspend		builtin_ref_entry_list_5_0
	module_entry		mpimos_xref_table
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
	module_entry		mpimos_xref_table
	predicate		set_nil,4
set_nil_4_0:
	try_me_else		set_nil_4_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		5,1
	put_nil		6
	b_set_vector_element		3,5,3,6,5
	b_increment		1,1
	put_value		3,5
	execute		4,set_nil_4_0
set_nil_4_1:
	try_me_else		set_nil_4_3
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_value		3,4
	proceed
set_nil_4_3:
	suspend		set_nil_4_0
	module_entry		mpimos_xref_table
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
	module_entry		mpimos_xref_table
	predicate		init_module_table,2
init_module_table_2_0:
	put_structured_constant		3,'$SCNST_12'
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_13'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_14'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_15'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_16'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_17'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_18'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_19'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_20'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_21'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_22'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_23'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_24'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_25'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_26'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_27'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_28'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_29'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_30'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_31'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_32'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_33'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_34'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_35'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_36'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_37'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_38'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_39'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_40'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_41'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_42'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_43'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_44'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_45'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_46'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_47'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_48'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_49'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_50'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_51'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_52'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_53'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_54'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_55'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_56'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_57'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_58'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_59'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_60'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_61'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_62'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_63'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_64'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_65'
	put_list_val_val		3,2,4
	put_structured_constant		2,'$SCNST_66'
	put_list_val_val		4,2,3
	put_structured_constant		2,'$SCNST_67'
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
init_module_table_2_1:
	suspend		init_module_table_2_0
	begin_const_section		mpimos_xref_table
'$SCNST_0_1':
	define_desc		11,1
	define_integer		4476485
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		27,1
	define_integer		46
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_1_1'
'$SCNST_9':
'$SCNST_6':
'$SCNST_4':
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		3,1
	define_integer		544106784
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_10':
'$SCNST_7':
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		27,10
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1684960544
	define_integer		1852401253
	define_integer		1881171045
	define_integer		1768187250
	define_integer		1702125923
	define_integer		976894496
	define_integer		32
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_5_1':
	define_desc		3,11
	define_integer		540950078
	define_integer		1852989783
	define_integer		543649385
	define_integer		1936269375
	define_integer		1952541807
	define_integer		1881171045
	define_integer		1768187250
	define_integer		1702125923
	define_integer		1769497888
	define_integer		544437363
	define_integer		540686906
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_8_1':
	define_desc		11,9
	define_integer		540950078
	define_integer		1852989783
	define_integer		543649385
	define_integer		1853169727
	define_integer		1768318308
	define_integer		543450478
	define_integer		1969516397
	define_integer		975201644
	define_integer		2112058
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_11_1':
	define_desc		19,9
	define_integer		540950078
	define_integer		1869771333
	define_integer		555819122
	define_integer		1684960544
	define_integer		1852401253
	define_integer		1881171045
	define_integer		1768710773
	define_integer		976887907
	define_integer		8250
'$SCNST_11_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_11_1'
'$SCNST_11':
	define_vector		'$SCNST_11_0'
'$SCNST_12_2':
	define_desc		0,2
	define_atom		struct_processor
	define_integer		5
'$SCNST_12_4':
	define_desc		0,2
	define_atom		test
	define_integer		0
'$SCNST_12_6':
	define_desc		0,2
	define_atom		calcurate_right_hand
	define_integer		4
'$SCNST_12_5':
	define_vector		'$SCNST_12_6'
	define_atom		[]
'$SCNST_12_3':
	define_vector		'$SCNST_12_4'
	define_list		'$SCNST_12_5'
'$SCNST_12_1':
	define_vector		'$SCNST_12_2'
	define_list		'$SCNST_12_3'
'$SCNST_12_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_struct
	define_list		'$SCNST_12_1'
'$SCNST_12':
	define_vector		'$SCNST_12_0'
'$SCNST_13_2':
	define_desc		0,2
	define_atom		compile_predicate
	define_integer		9
'$SCNST_13_1':
	define_vector		'$SCNST_13_2'
	define_atom		[]
'$SCNST_13_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_register
	define_list		'$SCNST_13_1'
'$SCNST_13':
	define_vector		'$SCNST_13_0'
'$SCNST_14_2':
	define_desc		0,2
	define_atom		count_variables
	define_integer		3
'$SCNST_14_4':
	define_desc		0,2
	define_atom		create_reader
	define_integer		5
'$SCNST_14_6':
	define_desc		0,2
	define_atom		create_varchk_reader
	define_integer		5
'$SCNST_14_8':
	define_desc		0,2
	define_atom		functor
	define_integer		3
'$SCNST_14_10':
	define_desc		0,2
	define_atom		gen_functor
	define_integer		3
'$SCNST_14_12':
	define_desc		0,2
	define_atom		herrey
	define_integer		3
'$SCNST_14_14':
	define_desc		0,2
	define_atom		trans_io_instr
	define_integer		3
'$SCNST_14_16':
	define_desc		0,2
	define_atom		test_reader
	define_integer		0
'$SCNST_14_18':
	define_desc		0,2
	define_atom		convert_integer_to_string
	define_integer		2
'$SCNST_14_20':
	define_desc		0,2
	define_atom		convert_integer_to_list
	define_integer		3
'$SCNST_14_22':
	define_desc		0,2
	define_atom		convert_list_to_string
	define_integer		3
'$SCNST_14_21':
	define_vector		'$SCNST_14_22'
	define_atom		[]
'$SCNST_14_19':
	define_vector		'$SCNST_14_20'
	define_list		'$SCNST_14_21'
'$SCNST_14_17':
	define_vector		'$SCNST_14_18'
	define_list		'$SCNST_14_19'
'$SCNST_14_15':
	define_vector		'$SCNST_14_16'
	define_list		'$SCNST_14_17'
'$SCNST_14_13':
	define_vector		'$SCNST_14_14'
	define_list		'$SCNST_14_15'
'$SCNST_14_11':
	define_vector		'$SCNST_14_12'
	define_list		'$SCNST_14_13'
'$SCNST_14_9':
	define_vector		'$SCNST_14_10'
	define_list		'$SCNST_14_11'
'$SCNST_14_7':
	define_vector		'$SCNST_14_8'
	define_list		'$SCNST_14_9'
'$SCNST_14_5':
	define_vector		'$SCNST_14_6'
	define_list		'$SCNST_14_7'
'$SCNST_14_3':
	define_vector		'$SCNST_14_4'
	define_list		'$SCNST_14_5'
'$SCNST_14_1':
	define_vector		'$SCNST_14_2'
	define_list		'$SCNST_14_3'
'$SCNST_14_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_reader
	define_list		'$SCNST_14_1'
'$SCNST_14':
	define_vector		'$SCNST_14_0'
'$SCNST_15_2':
	define_desc		0,2
	define_atom		write_code_end
	define_integer		3
'$SCNST_15_4':
	define_desc		0,2
	define_atom		write_code_header
	define_integer		4
'$SCNST_15_6':
	define_desc		0,2
	define_atom		write_label
	define_integer		3
'$SCNST_15_8':
	define_desc		0,2
	define_atom		erace_or_convert_instruction
	define_integer		8
'$SCNST_15_10':
	define_desc		0,2
	define_atom		write_vector
	define_integer		3
'$SCNST_15_12':
	define_desc		0,2
	define_atom		write_rkp_information
	define_integer		6
'$SCNST_15_14':
	define_desc		0,2
	define_atom		write_messages
	define_integer		3
'$SCNST_15_16':
	define_desc		0,2
	define_atom		convert_code_for_PDSS
	define_integer		3
'$SCNST_15_18':
	define_desc		0,2
	define_atom		write_object_code
	define_integer		3
'$SCNST_15_20':
	define_desc		0,2
	define_atom		write_otherwise
	define_integer		3
'$SCNST_15_22':
	define_desc		0,2
	define_atom		write_alternatively
	define_integer		2
'$SCNST_15_24':
	define_desc		0,2
	define_atom		output_const_code
	define_integer		3
'$SCNST_15_23':
	define_vector		'$SCNST_15_24'
	define_atom		[]
'$SCNST_15_21':
	define_vector		'$SCNST_15_22'
	define_list		'$SCNST_15_23'
'$SCNST_15_19':
	define_vector		'$SCNST_15_20'
	define_list		'$SCNST_15_21'
'$SCNST_15_17':
	define_vector		'$SCNST_15_18'
	define_list		'$SCNST_15_19'
'$SCNST_15_15':
	define_vector		'$SCNST_15_16'
	define_list		'$SCNST_15_17'
'$SCNST_15_13':
	define_vector		'$SCNST_15_14'
	define_list		'$SCNST_15_15'
'$SCNST_15_11':
	define_vector		'$SCNST_15_12'
	define_list		'$SCNST_15_13'
'$SCNST_15_9':
	define_vector		'$SCNST_15_10'
	define_list		'$SCNST_15_11'
'$SCNST_15_7':
	define_vector		'$SCNST_15_8'
	define_list		'$SCNST_15_9'
'$SCNST_15_5':
	define_vector		'$SCNST_15_6'
	define_list		'$SCNST_15_7'
'$SCNST_15_3':
	define_vector		'$SCNST_15_4'
	define_list		'$SCNST_15_5'
'$SCNST_15_1':
	define_vector		'$SCNST_15_2'
	define_list		'$SCNST_15_3'
'$SCNST_15_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_output
	define_list		'$SCNST_15_1'
'$SCNST_15':
	define_vector		'$SCNST_15_0'
'$SCNST_16_2':
	define_desc		0,2
	define_atom		normalize
	define_integer		11
'$SCNST_16_4':
	define_desc		0,2
	define_atom		variable_generator
	define_integer		3
'$SCNST_16_3':
	define_vector		'$SCNST_16_4'
	define_atom		[]
'$SCNST_16_1':
	define_vector		'$SCNST_16_2'
	define_list		'$SCNST_16_3'
'$SCNST_16_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_normalize
	define_list		'$SCNST_16_1'
'$SCNST_16':
	define_vector		'$SCNST_16_0'
'$SCNST_17_2':
	define_desc		0,2
	define_atom		mrb_optimization
	define_integer		13
'$SCNST_17_4':
	define_desc		0,2
	define_atom		compile_for_pdss
	define_integer		6
'$SCNST_17_3':
	define_vector		'$SCNST_17_4'
	define_atom		[]
'$SCNST_17_1':
	define_vector		'$SCNST_17_2'
	define_list		'$SCNST_17_3'
'$SCNST_17_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_mrb
	define_list		'$SCNST_17_1'
'$SCNST_17':
	define_vector		'$SCNST_17_0'
'$SCNST_18_2':
	define_desc		0,2
	define_atom		generate_macro_table_process
	define_integer		7
'$SCNST_18_4':
	define_desc		0,2
	define_atom		make_table
	define_integer		5
'$SCNST_18_3':
	define_vector		'$SCNST_18_4'
	define_atom		[]
'$SCNST_18_1':
	define_vector		'$SCNST_18_2'
	define_list		'$SCNST_18_3'
'$SCNST_18_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_mtbl
	define_list		'$SCNST_18_1'
'$SCNST_18':
	define_vector		'$SCNST_18_0'
'$SCNST_19_2':
	define_desc		0,2
	define_atom		test
	define_integer		0
'$SCNST_19_4':
	define_desc		0,2
	define_atom		generate_macro_expander
	define_integer		6
'$SCNST_19_3':
	define_vector		'$SCNST_19_4'
	define_atom		[]
'$SCNST_19_1':
	define_vector		'$SCNST_19_2'
	define_list		'$SCNST_19_3'
'$SCNST_19_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_macro
	define_list		'$SCNST_19_1'
'$SCNST_19':
	define_vector		'$SCNST_19_0'
'$SCNST_20_2':
	define_desc		0,2
	define_atom		init_macro_table
	define_integer		1
'$SCNST_20_4':
	define_desc		0,2
	define_atom		read_macro_file
	define_integer		5
'$SCNST_20_3':
	define_vector		'$SCNST_20_4'
	define_atom		[]
'$SCNST_20_1':
	define_vector		'$SCNST_20_2'
	define_list		'$SCNST_20_3'
'$SCNST_20_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_macro_arg
	define_list		'$SCNST_20_1'
'$SCNST_20':
	define_vector		'$SCNST_20_0'
'$SCNST_21_2':
	define_desc		0,2
	define_atom		compile_one_clause
	define_integer		17
'$SCNST_21_1':
	define_vector		'$SCNST_21_2'
	define_atom		[]
'$SCNST_21_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_compile
	define_list		'$SCNST_21_1'
'$SCNST_21':
	define_vector		'$SCNST_21_0'
'$SCNST_22_2':
	define_desc		0,2
	define_atom		tsscomp
	define_integer		1
'$SCNST_22_4':
	define_desc		0,2
	define_atom		tsscomp
	define_integer		0
'$SCNST_22_6':
	define_desc		0,2
	define_atom		kl1compile
	define_integer		0
'$SCNST_22_8':
	define_desc		0,2
	define_atom		ghccompile
	define_integer		8
'$SCNST_22_10':
	define_desc		0,2
	define_atom		message_distributer
	define_integer		7
'$SCNST_22_12':
	define_desc		0,2
	define_atom		write_string
	define_integer		3
'$SCNST_22_14':
	define_desc		0,2
	define_atom		compile_for_pdss
	define_integer		6
'$SCNST_22_13':
	define_vector		'$SCNST_22_14'
	define_atom		[]
'$SCNST_22_11':
	define_vector		'$SCNST_22_12'
	define_list		'$SCNST_22_13'
'$SCNST_22_9':
	define_vector		'$SCNST_22_10'
	define_list		'$SCNST_22_11'
'$SCNST_22_7':
	define_vector		'$SCNST_22_8'
	define_list		'$SCNST_22_9'
'$SCNST_22_5':
	define_vector		'$SCNST_22_6'
	define_list		'$SCNST_22_7'
'$SCNST_22_3':
	define_vector		'$SCNST_22_4'
	define_list		'$SCNST_22_5'
'$SCNST_22_1':
	define_vector		'$SCNST_22_2'
	define_list		'$SCNST_22_3'
'$SCNST_22_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_command
	define_list		'$SCNST_22_1'
'$SCNST_22':
	define_vector		'$SCNST_22_0'
'$SCNST_23_2':
	define_desc		0,2
	define_atom		builtin
	define_integer		7
'$SCNST_23_4':
	define_desc		0,2
	define_atom		active_builtin
	define_integer		5
'$SCNST_23_6':
	define_desc		0,2
	define_atom		expression
	define_integer		6
'$SCNST_23_8':
	define_desc		0,2
	define_atom		float_expression
	define_integer		6
'$SCNST_23_7':
	define_vector		'$SCNST_23_8'
	define_atom		[]
'$SCNST_23_5':
	define_vector		'$SCNST_23_6'
	define_list		'$SCNST_23_7'
'$SCNST_23_3':
	define_vector		'$SCNST_23_4'
	define_list		'$SCNST_23_5'
'$SCNST_23_1':
	define_vector		'$SCNST_23_2'
	define_list		'$SCNST_23_3'
'$SCNST_23_0':
	define_desc		0,3
	define_atom		entry
	define_atom		kl1cmp_blttbl
	define_list		'$SCNST_23_1'
'$SCNST_23':
	define_vector		'$SCNST_23_0'
'$SCNST_24_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_24_1':
	define_vector		'$SCNST_24_2'
	define_atom		[]
'$SCNST_24_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_window_manager
	define_list		'$SCNST_24_1'
'$SCNST_24':
	define_vector		'$SCNST_24_0'
'$SCNST_25_2':
	define_desc		0,2
	define_atom		create
	define_integer		7
'$SCNST_25_4':
	define_desc		0,2
	define_atom		device_create
	define_integer		6
'$SCNST_25_3':
	define_vector		'$SCNST_25_4'
	define_atom		[]
'$SCNST_25_1':
	define_vector		'$SCNST_25_2'
	define_list		'$SCNST_25_3'
'$SCNST_25_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_window_device_driver
	define_list		'$SCNST_25_1'
'$SCNST_25':
	define_vector		'$SCNST_25_0'
'$SCNST_26_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_26_1':
	define_vector		'$SCNST_26_2'
	define_atom		[]
'$SCNST_26_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_timer_manager
	define_list		'$SCNST_26_1'
'$SCNST_26':
	define_vector		'$SCNST_26_0'
'$SCNST_27_2':
	define_desc		0,2
	define_atom		create
	define_integer		1
'$SCNST_27_1':
	define_vector		'$SCNST_27_2'
	define_atom		[]
'$SCNST_27_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_monogyny_list_index
	define_list		'$SCNST_27_1'
'$SCNST_27':
	define_vector		'$SCNST_27_0'
'$SCNST_28_2':
	define_desc		0,2
	define_atom		predicate_table
	define_integer		4
'$SCNST_28_4':
	define_desc		0,2
	define_atom		module_table
	define_integer		7
'$SCNST_28_6':
	define_desc		0,2
	define_atom		init_module_table
	define_integer		2
'$SCNST_28_5':
	define_vector		'$SCNST_28_6'
	define_atom		[]
'$SCNST_28_3':
	define_vector		'$SCNST_28_4'
	define_list		'$SCNST_28_5'
'$SCNST_28_1':
	define_vector		'$SCNST_28_2'
	define_list		'$SCNST_28_3'
'$SCNST_28_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_xref_table
	define_list		'$SCNST_28_1'
'$SCNST_28':
	define_vector		'$SCNST_28_0'
'$SCNST_29_2':
	define_desc		0,2
	define_atom		go
	define_integer		2
'$SCNST_29_4':
	define_desc		0,2
	define_atom		go
	define_integer		3
'$SCNST_29_6':
	define_desc		0,2
	define_atom		go_f
	define_integer		3
'$SCNST_29_8':
	define_desc		0,2
	define_atom		go_f
	define_integer		4
'$SCNST_29_7':
	define_vector		'$SCNST_29_8'
	define_atom		[]
'$SCNST_29_5':
	define_vector		'$SCNST_29_6'
	define_list		'$SCNST_29_7'
'$SCNST_29_3':
	define_vector		'$SCNST_29_4'
	define_list		'$SCNST_29_5'
'$SCNST_29_1':
	define_vector		'$SCNST_29_2'
	define_list		'$SCNST_29_3'
'$SCNST_29_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_xref
	define_list		'$SCNST_29_1'
'$SCNST_29':
	define_vector		'$SCNST_29_0'
'$SCNST_30_2':
	define_desc		0,2
	define_atom		create
	define_integer		2
'$SCNST_30_4':
	define_desc		0,2
	define_atom		make_variable_name
	define_integer		2
'$SCNST_30_3':
	define_vector		'$SCNST_30_4'
	define_atom		[]
'$SCNST_30_1':
	define_vector		'$SCNST_30_2'
	define_list		'$SCNST_30_3'
'$SCNST_30_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_unparser
	define_list		'$SCNST_30_1'
'$SCNST_30':
	define_vector		'$SCNST_30_0'
'$SCNST_31_2':
	define_desc		0,2
	define_atom		go
	define_integer		2
'$SCNST_31_4':
	define_desc		0,2
	define_atom		go
	define_integer		3
'$SCNST_31_6':
	define_desc		0,2
	define_atom		go_f
	define_integer		3
'$SCNST_31_8':
	define_desc		0,2
	define_atom		start
	define_integer		4
'$SCNST_31_10':
	define_desc		0,2
	define_atom		go_p
	define_integer		3
'$SCNST_31_9':
	define_vector		'$SCNST_31_10'
	define_atom		[]
'$SCNST_31_7':
	define_vector		'$SCNST_31_8'
	define_list		'$SCNST_31_9'
'$SCNST_31_5':
	define_vector		'$SCNST_31_6'
	define_list		'$SCNST_31_7'
'$SCNST_31_3':
	define_vector		'$SCNST_31_4'
	define_list		'$SCNST_31_5'
'$SCNST_31_1':
	define_vector		'$SCNST_31_2'
	define_list		'$SCNST_31_3'
'$SCNST_31_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_varchk
	define_list		'$SCNST_31_1'
'$SCNST_31':
	define_vector		'$SCNST_31_0'
'$SCNST_32_2':
	define_desc		0,2
	define_atom		timer
	define_integer		1
'$SCNST_32_4':
	define_desc		0,2
	define_atom		timer_request
	define_integer		3
'$SCNST_32_3':
	define_vector		'$SCNST_32_4'
	define_atom		[]
'$SCNST_32_1':
	define_vector		'$SCNST_32_2'
	define_list		'$SCNST_32_3'
'$SCNST_32_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_timer_device
	define_list		'$SCNST_32_1'
'$SCNST_32':
	define_vector		'$SCNST_32_0'
'$SCNST_33_2':
	define_desc		0,2
	define_atom		windows
	define_integer		1
'$SCNST_33_4':
	define_desc		0,2
	define_atom		window_request
	define_integer		3
'$SCNST_33_3':
	define_vector		'$SCNST_33_4'
	define_atom		[]
'$SCNST_33_1':
	define_vector		'$SCNST_33_2'
	define_list		'$SCNST_33_3'
'$SCNST_33_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_window_device
	define_list		'$SCNST_33_1'
'$SCNST_33':
	define_vector		'$SCNST_33_0'
'$SCNST_34_2':
	define_desc		0,2
	define_atom		pprinter
	define_integer		2
'$SCNST_34_1':
	define_vector		'$SCNST_34_2'
	define_atom		[]
'$SCNST_34_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_pretty_printer
	define_list		'$SCNST_34_1'
'$SCNST_34':
	define_vector		'$SCNST_34_0'
'$SCNST_35_2':
	define_desc		0,2
	define_atom		windows
	define_integer		1
'$SCNST_35_4':
	define_desc		0,2
	define_atom		window_request
	define_integer		3
'$SCNST_35_6':
	define_desc		0,2
	define_atom		files
	define_integer		1
'$SCNST_35_8':
	define_desc		0,2
	define_atom		file_request
	define_integer		4
'$SCNST_35_10':
	define_desc		0,2
	define_atom		timer
	define_integer		1
'$SCNST_35_12':
	define_desc		0,2
	define_atom		timer_request
	define_integer		3
'$SCNST_35_11':
	define_vector		'$SCNST_35_12'
	define_atom		[]
'$SCNST_35_9':
	define_vector		'$SCNST_35_10'
	define_list		'$SCNST_35_11'
'$SCNST_35_7':
	define_vector		'$SCNST_35_8'
	define_list		'$SCNST_35_9'
'$SCNST_35_5':
	define_vector		'$SCNST_35_6'
	define_list		'$SCNST_35_7'
'$SCNST_35_3':
	define_vector		'$SCNST_35_4'
	define_list		'$SCNST_35_5'
'$SCNST_35_1':
	define_vector		'$SCNST_35_2'
	define_list		'$SCNST_35_3'
'$SCNST_35_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_io_device
	define_list		'$SCNST_35_1'
'$SCNST_35':
	define_vector		'$SCNST_35_0'
'$SCNST_36_2':
	define_desc		0,2
	define_atom		do
	define_integer		3
'$SCNST_36_1':
	define_vector		'$SCNST_36_2'
	define_atom		[]
'$SCNST_36_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_parser
	define_list		'$SCNST_36_1'
'$SCNST_36':
	define_vector		'$SCNST_36_0'
'$SCNST_37_2':
	define_desc		0,2
	define_atom		files
	define_integer		1
'$SCNST_37_4':
	define_desc		0,2
	define_atom		file_request
	define_integer		4
'$SCNST_37_3':
	define_vector		'$SCNST_37_4'
	define_atom		[]
'$SCNST_37_1':
	define_vector		'$SCNST_37_2'
	define_list		'$SCNST_37_3'
'$SCNST_37_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_file_device
	define_list		'$SCNST_37_1'
'$SCNST_37':
	define_vector		'$SCNST_37_0'
'$SCNST_38_2':
	define_desc		0,2
	define_atom		create
	define_integer		12
'$SCNST_38_4':
	define_desc		0,2
	define_atom		error_monitor
	define_integer		2
'$SCNST_38_6':
	define_desc		0,2
	define_atom		error_monitor
	define_integer		3
'$SCNST_38_5':
	define_vector		'$SCNST_38_6'
	define_atom		[]
'$SCNST_38_3':
	define_vector		'$SCNST_38_4'
	define_list		'$SCNST_38_5'
'$SCNST_38_1':
	define_vector		'$SCNST_38_2'
	define_list		'$SCNST_38_3'
'$SCNST_38_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_task_monitor
	define_list		'$SCNST_38_1'
'$SCNST_38':
	define_vector		'$SCNST_38_0'
'$SCNST_39_2':
	define_desc		0,2
	define_atom		create
	define_integer		2
'$SCNST_39_1':
	define_vector		'$SCNST_39_2'
	define_atom		[]
'$SCNST_39_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_module_pool
	define_list		'$SCNST_39_1'
'$SCNST_39':
	define_vector		'$SCNST_39_0'
'$SCNST_40_2':
	define_desc		0,2
	define_atom		create
	define_integer		1
'$SCNST_40_1':
	define_vector		'$SCNST_40_2'
	define_atom		[]
'$SCNST_40_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_macro_expander
	define_list		'$SCNST_40_1'
'$SCNST_40':
	define_vector		'$SCNST_40_0'
'$SCNST_41_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_41_1':
	define_vector		'$SCNST_41_2'
	define_atom		[]
'$SCNST_41_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_file_manager
	define_list		'$SCNST_41_1'
'$SCNST_41':
	define_vector		'$SCNST_41_0'
'$SCNST_42_2':
	define_desc		0,2
	define_atom		create
	define_integer		7
'$SCNST_42_4':
	define_desc		0,2
	define_atom		device_create
	define_integer		7
'$SCNST_42_3':
	define_vector		'$SCNST_42_4'
	define_atom		[]
'$SCNST_42_1':
	define_vector		'$SCNST_42_2'
	define_list		'$SCNST_42_3'
'$SCNST_42_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_file_device_driver
	define_list		'$SCNST_42_1'
'$SCNST_42':
	define_vector		'$SCNST_42_0'
'$SCNST_43_2':
	define_desc		0,2
	define_atom		create
	define_integer		1
'$SCNST_43_1':
	define_vector		'$SCNST_43_2'
	define_atom		[]
'$SCNST_43_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_operator_manipulator
	define_list		'$SCNST_43_1'
'$SCNST_43':
	define_vector		'$SCNST_43_0'
'$SCNST_44_2':
	define_desc		0,2
	define_atom		create
	define_integer		2
'$SCNST_44_4':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_44_6':
	define_desc		0,2
	define_atom		request
	define_integer		7
'$SCNST_44_8':
	define_desc		0,2
	define_atom		os_create
	define_integer		6
'$SCNST_44_7':
	define_vector		'$SCNST_44_8'
	define_atom		[]
'$SCNST_44_5':
	define_vector		'$SCNST_44_6'
	define_list		'$SCNST_44_7'
'$SCNST_44_3':
	define_vector		'$SCNST_44_4'
	define_list		'$SCNST_44_5'
'$SCNST_44_1':
	define_vector		'$SCNST_44_2'
	define_list		'$SCNST_44_3'
'$SCNST_44_0':
	define_desc		0,3
	define_atom		entry
	define_atom		window
	define_list		'$SCNST_44_1'
'$SCNST_44':
	define_vector		'$SCNST_44_0'
'$SCNST_45_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_45_4':
	define_desc		0,2
	define_atom		create
	define_integer		4
'$SCNST_45_6':
	define_desc		0,2
	define_atom		os_create
	define_integer		7
'$SCNST_45_8':
	define_desc		0,2
	define_atom		request
	define_integer		4
'$SCNST_45_7':
	define_vector		'$SCNST_45_8'
	define_atom		[]
'$SCNST_45_5':
	define_vector		'$SCNST_45_6'
	define_list		'$SCNST_45_7'
'$SCNST_45_3':
	define_vector		'$SCNST_45_4'
	define_list		'$SCNST_45_5'
'$SCNST_45_1':
	define_vector		'$SCNST_45_2'
	define_list		'$SCNST_45_3'
'$SCNST_45_0':
	define_desc		0,3
	define_atom		entry
	define_atom		file
	define_list		'$SCNST_45_1'
'$SCNST_45':
	define_vector		'$SCNST_45_0'
'$SCNST_46_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_46_4':
	define_desc		0,2
	define_atom		os_create
	define_integer		6
'$SCNST_46_6':
	define_desc		0,2
	define_atom		request
	define_integer		4
'$SCNST_46_5':
	define_vector		'$SCNST_46_6'
	define_atom		[]
'$SCNST_46_3':
	define_vector		'$SCNST_46_4'
	define_list		'$SCNST_46_5'
'$SCNST_46_1':
	define_vector		'$SCNST_46_2'
	define_list		'$SCNST_46_3'
'$SCNST_46_0':
	define_desc		0,3
	define_atom		entry
	define_atom		directory
	define_list		'$SCNST_46_1'
'$SCNST_46':
	define_vector		'$SCNST_46_0'
'$SCNST_47_2':
	define_desc		0,2
	define_atom		create
	define_integer		6
'$SCNST_47_1':
	define_vector		'$SCNST_47_2'
	define_atom		[]
'$SCNST_47_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_directory_device_driver
	define_list		'$SCNST_47_1'
'$SCNST_47':
	define_vector		'$SCNST_47_0'
'$SCNST_48_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_48_4':
	define_desc		0,2
	define_atom		create
	define_integer		4
'$SCNST_48_6':
	define_desc		0,2
	define_atom		os_create
	define_integer		7
'$SCNST_48_8':
	define_desc		0,2
	define_atom		request
	define_integer		4
'$SCNST_48_7':
	define_vector		'$SCNST_48_8'
	define_atom		[]
'$SCNST_48_5':
	define_vector		'$SCNST_48_6'
	define_list		'$SCNST_48_7'
'$SCNST_48_3':
	define_vector		'$SCNST_48_4'
	define_list		'$SCNST_48_5'
'$SCNST_48_1':
	define_vector		'$SCNST_48_2'
	define_list		'$SCNST_48_3'
'$SCNST_48_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_file
	define_list		'$SCNST_48_1'
'$SCNST_48':
	define_vector		'$SCNST_48_0'
'$SCNST_49_2':
	define_desc		0,2
	define_atom		melt
	define_integer		3
'$SCNST_49_4':
	define_desc		0,2
	define_atom		freeze
	define_integer		2
'$SCNST_49_6':
	define_desc		0,2
	define_atom		get_predicate
	define_integer		3
'$SCNST_49_8':
	define_desc		0,2
	define_atom		write
	define_integer		1
'$SCNST_49_10':
	define_desc		0,2
	define_atom		symbol_append
	define_integer		2
'$SCNST_49_12':
	define_desc		0,2
	define_atom		string_append
	define_integer		2
'$SCNST_49_14':
	define_desc		0,2
	define_atom		symbol_to_string
	define_integer		2
'$SCNST_49_16':
	define_desc		0,2
	define_atom		pathname
	define_integer		3
'$SCNST_49_18':
	define_desc		0,2
	define_atom		extend_name
	define_integer		3
'$SCNST_49_20':
	define_desc		0,2
	define_atom		compress
	define_integer		2
'$SCNST_49_22':
	define_desc		0,2
	define_atom		integer_to_string
	define_integer		2
'$SCNST_49_24':
	define_desc		0,2
	define_atom		qsort
	define_integer		2
'$SCNST_49_26':
	define_desc		0,2
	define_atom		qsort
	define_integer		3
'$SCNST_49_28':
	define_desc		0,2
	define_atom		qsortv
	define_integer		3
'$SCNST_49_30':
	define_desc		0,2
	define_atom		qsortv
	define_integer		4
'$SCNST_49_32':
	define_desc		0,2
	define_atom		report_tokens
	define_integer		3
'$SCNST_49_34':
	define_desc		0,2
	define_atom		report_tokens
	define_integer		2
'$SCNST_49_36':
	define_desc		0,2
	define_atom		copy_string_elements
	define_integer		7
'$SCNST_49_38':
	define_desc		0,2
	define_atom		append_string
	define_integer		2
'$SCNST_49_37':
	define_vector		'$SCNST_49_38'
	define_atom		[]
'$SCNST_49_35':
	define_vector		'$SCNST_49_36'
	define_list		'$SCNST_49_37'
'$SCNST_49_33':
	define_vector		'$SCNST_49_34'
	define_list		'$SCNST_49_35'
'$SCNST_49_31':
	define_vector		'$SCNST_49_32'
	define_list		'$SCNST_49_33'
'$SCNST_49_29':
	define_vector		'$SCNST_49_30'
	define_list		'$SCNST_49_31'
'$SCNST_49_27':
	define_vector		'$SCNST_49_28'
	define_list		'$SCNST_49_29'
'$SCNST_49_25':
	define_vector		'$SCNST_49_26'
	define_list		'$SCNST_49_27'
'$SCNST_49_23':
	define_vector		'$SCNST_49_24'
	define_list		'$SCNST_49_25'
'$SCNST_49_21':
	define_vector		'$SCNST_49_22'
	define_list		'$SCNST_49_23'
'$SCNST_49_19':
	define_vector		'$SCNST_49_20'
	define_list		'$SCNST_49_21'
'$SCNST_49_17':
	define_vector		'$SCNST_49_18'
	define_list		'$SCNST_49_19'
'$SCNST_49_15':
	define_vector		'$SCNST_49_16'
	define_list		'$SCNST_49_17'
'$SCNST_49_13':
	define_vector		'$SCNST_49_14'
	define_list		'$SCNST_49_15'
'$SCNST_49_11':
	define_vector		'$SCNST_49_12'
	define_list		'$SCNST_49_13'
'$SCNST_49_9':
	define_vector		'$SCNST_49_10'
	define_list		'$SCNST_49_11'
'$SCNST_49_7':
	define_vector		'$SCNST_49_8'
	define_list		'$SCNST_49_9'
'$SCNST_49_5':
	define_vector		'$SCNST_49_6'
	define_list		'$SCNST_49_7'
'$SCNST_49_3':
	define_vector		'$SCNST_49_4'
	define_list		'$SCNST_49_5'
'$SCNST_49_1':
	define_vector		'$SCNST_49_2'
	define_list		'$SCNST_49_3'
'$SCNST_49_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_utility
	define_list		'$SCNST_49_1'
'$SCNST_49':
	define_vector		'$SCNST_49_0'
'$SCNST_50_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_50_4':
	define_desc		0,2
	define_atom		os_create
	define_integer		6
'$SCNST_50_6':
	define_desc		0,2
	define_atom		request
	define_integer		4
'$SCNST_50_5':
	define_vector		'$SCNST_50_6'
	define_atom		[]
'$SCNST_50_3':
	define_vector		'$SCNST_50_4'
	define_list		'$SCNST_50_5'
'$SCNST_50_1':
	define_vector		'$SCNST_50_2'
	define_list		'$SCNST_50_3'
'$SCNST_50_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_directory
	define_list		'$SCNST_50_1'
'$SCNST_50':
	define_vector		'$SCNST_50_0'
'$SCNST_51_2':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_51_4':
	define_desc		0,2
	define_atom		request
	define_integer		3
'$SCNST_51_6':
	define_desc		0,2
	define_atom		get_command_stream
	define_integer		1
'$SCNST_51_8':
	define_desc		0,2
	define_atom		os_get_command_stream
	define_integer		3
'$SCNST_51_7':
	define_vector		'$SCNST_51_8'
	define_atom		[]
'$SCNST_51_5':
	define_vector		'$SCNST_51_6'
	define_list		'$SCNST_51_7'
'$SCNST_51_3':
	define_vector		'$SCNST_51_4'
	define_list		'$SCNST_51_5'
'$SCNST_51_1':
	define_vector		'$SCNST_51_2'
	define_list		'$SCNST_51_3'
'$SCNST_51_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_code_manager
	define_list		'$SCNST_51_1'
'$SCNST_51':
	define_vector		'$SCNST_51_0'
'$SCNST_52_2':
	define_desc		0,2
	define_atom		send_shell
	define_integer		3
'$SCNST_52_4':
	define_desc		0,2
	define_atom		protect
	define_integer		2
'$SCNST_52_6':
	define_desc		0,2
	define_atom		wait_send
	define_integer		4
'$SCNST_52_8':
	define_desc		0,2
	define_atom		check_savedir
	define_integer		5
'$SCNST_52_10':
	define_desc		0,2
	define_atom		os_check_loaddir
	define_integer		5
'$SCNST_52_12':
	define_desc		0,2
	define_atom		apply_action
	define_integer		3
'$SCNST_52_14':
	define_desc		0,2
	define_atom		apply_action
	define_integer		4
'$SCNST_52_13':
	define_vector		'$SCNST_52_14'
	define_atom		[]
'$SCNST_52_11':
	define_vector		'$SCNST_52_12'
	define_list		'$SCNST_52_13'
'$SCNST_52_9':
	define_vector		'$SCNST_52_10'
	define_list		'$SCNST_52_11'
'$SCNST_52_7':
	define_vector		'$SCNST_52_8'
	define_list		'$SCNST_52_9'
'$SCNST_52_5':
	define_vector		'$SCNST_52_6'
	define_list		'$SCNST_52_7'
'$SCNST_52_3':
	define_vector		'$SCNST_52_4'
	define_list		'$SCNST_52_5'
'$SCNST_52_1':
	define_vector		'$SCNST_52_2'
	define_list		'$SCNST_52_3'
'$SCNST_52_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_utl
	define_list		'$SCNST_52_1'
'$SCNST_52':
	define_vector		'$SCNST_52_0'
'$SCNST_53_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_53_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_53_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_53_5':
	define_vector		'$SCNST_53_6'
	define_atom		[]
'$SCNST_53_3':
	define_vector		'$SCNST_53_4'
	define_list		'$SCNST_53_5'
'$SCNST_53_1':
	define_vector		'$SCNST_53_2'
	define_list		'$SCNST_53_3'
'$SCNST_53_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_environment
	define_list		'$SCNST_53_1'
'$SCNST_53':
	define_vector		'$SCNST_53_0'
'$SCNST_54_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_54_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_54_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_54_5':
	define_vector		'$SCNST_54_6'
	define_atom		[]
'$SCNST_54_3':
	define_vector		'$SCNST_54_4'
	define_list		'$SCNST_54_5'
'$SCNST_54_1':
	define_vector		'$SCNST_54_2'
	define_list		'$SCNST_54_3'
'$SCNST_54_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_directory
	define_list		'$SCNST_54_1'
'$SCNST_54':
	define_vector		'$SCNST_54_0'
'$SCNST_55_2':
	define_desc		0,2
	define_atom		create
	define_integer		1
'$SCNST_55_4':
	define_desc		0,2
	define_atom		kl1cmp_create
	define_integer		1
'$SCNST_55_6':
	define_desc		0,2
	define_atom		initenv
	define_integer		3
'$SCNST_55_8':
	define_desc		0,2
	define_atom		apply_goals
	define_integer		1
'$SCNST_55_10':
	define_desc		0,2
	define_atom		command_analyzer
	define_integer		3
'$SCNST_55_12':
	define_desc		0,2
	define_atom		unit
	define_integer		4
'$SCNST_55_11':
	define_vector		'$SCNST_55_12'
	define_atom		[]
'$SCNST_55_9':
	define_vector		'$SCNST_55_10'
	define_list		'$SCNST_55_11'
'$SCNST_55_7':
	define_vector		'$SCNST_55_8'
	define_list		'$SCNST_55_9'
'$SCNST_55_5':
	define_vector		'$SCNST_55_6'
	define_list		'$SCNST_55_7'
'$SCNST_55_3':
	define_vector		'$SCNST_55_4'
	define_list		'$SCNST_55_5'
'$SCNST_55_1':
	define_vector		'$SCNST_55_2'
	define_list		'$SCNST_55_3'
'$SCNST_55_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_command_interpreter
	define_list		'$SCNST_55_1'
'$SCNST_55':
	define_vector		'$SCNST_55_0'
'$SCNST_56_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_56_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_56_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_56_5':
	define_vector		'$SCNST_56_6'
	define_atom		[]
'$SCNST_56_3':
	define_vector		'$SCNST_56_4'
	define_list		'$SCNST_56_5'
'$SCNST_56_1':
	define_vector		'$SCNST_56_2'
	define_list		'$SCNST_56_3'
'$SCNST_56_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_debug
	define_list		'$SCNST_56_1'
'$SCNST_56':
	define_vector		'$SCNST_56_0'
'$SCNST_57_2':
	define_desc		0,2
	define_atom		create
	define_integer		2
'$SCNST_57_4':
	define_desc		0,2
	define_atom		create
	define_integer		3
'$SCNST_57_6':
	define_desc		0,2
	define_atom		request
	define_integer		7
'$SCNST_57_8':
	define_desc		0,2
	define_atom		os_create
	define_integer		6
'$SCNST_57_7':
	define_vector		'$SCNST_57_8'
	define_atom		[]
'$SCNST_57_5':
	define_vector		'$SCNST_57_6'
	define_list		'$SCNST_57_7'
'$SCNST_57_3':
	define_vector		'$SCNST_57_4'
	define_list		'$SCNST_57_5'
'$SCNST_57_1':
	define_vector		'$SCNST_57_2'
	define_list		'$SCNST_57_3'
'$SCNST_57_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_window
	define_list		'$SCNST_57_1'
'$SCNST_57':
	define_vector		'$SCNST_57_0'
'$SCNST_58_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_58_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_58_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_58_5':
	define_vector		'$SCNST_58_6'
	define_atom		[]
'$SCNST_58_3':
	define_vector		'$SCNST_58_4'
	define_list		'$SCNST_58_5'
'$SCNST_58_1':
	define_vector		'$SCNST_58_2'
	define_list		'$SCNST_58_3'
'$SCNST_58_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_code
	define_list		'$SCNST_58_1'
'$SCNST_58':
	define_vector		'$SCNST_58_0'
'$SCNST_59_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_59_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_59_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_59_5':
	define_vector		'$SCNST_59_6'
	define_atom		[]
'$SCNST_59_3':
	define_vector		'$SCNST_59_4'
	define_list		'$SCNST_59_5'
'$SCNST_59_1':
	define_vector		'$SCNST_59_2'
	define_list		'$SCNST_59_3'
'$SCNST_59_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_cmd_basic
	define_list		'$SCNST_59_1'
'$SCNST_59':
	define_vector		'$SCNST_59_0'
'$SCNST_60_2':
	define_desc		0,2
	define_atom		op
	define_integer		2
'$SCNST_60_1':
	define_vector		'$SCNST_60_2'
	define_atom		[]
'$SCNST_60_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_opcode_table
	define_list		'$SCNST_60_1'
'$SCNST_60':
	define_vector		'$SCNST_60_0'
'$SCNST_61_2':
	define_desc		0,2
	define_atom		start
	define_integer		0
'$SCNST_61_4':
	define_desc		0,2
	define_atom		kl1cmp_start
	define_integer		0
'$SCNST_61_6':
	define_desc		0,2
	define_atom		process_name_list
	define_integer		2
'$SCNST_61_5':
	define_vector		'$SCNST_61_6'
	define_atom		[]
'$SCNST_61_3':
	define_vector		'$SCNST_61_4'
	define_list		'$SCNST_61_5'
'$SCNST_61_1':
	define_vector		'$SCNST_61_2'
	define_list		'$SCNST_61_3'
'$SCNST_61_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_booter
	define_list		'$SCNST_61_1'
'$SCNST_61':
	define_vector		'$SCNST_61_0'
'$SCNST_62_2':
	define_desc		0,2
	define_atom		is_command
	define_integer		2
'$SCNST_62_4':
	define_desc		0,2
	define_atom		do_command
	define_integer		2
'$SCNST_62_6':
	define_desc		0,2
	define_atom		help
	define_integer		2
'$SCNST_62_5':
	define_vector		'$SCNST_62_6'
	define_atom		[]
'$SCNST_62_3':
	define_vector		'$SCNST_62_4'
	define_list		'$SCNST_62_5'
'$SCNST_62_1':
	define_vector		'$SCNST_62_2'
	define_list		'$SCNST_62_3'
'$SCNST_62_0':
	define_desc		0,3
	define_atom		entry
	define_atom		mpimos_builtin_predicate
	define_list		'$SCNST_62_1'
'$SCNST_62':
	define_vector		'$SCNST_62_0'
'$SCNST_63_2':
	define_desc		0,2
	define_atom		windows
	define_integer		1
'$SCNST_63_1':
	define_vector		'$SCNST_63_2'
	define_atom		[]
'$SCNST_63_0':
	define_desc		0,3
	define_atom		entry
	define_atom		pdss_window_device
	define_list		'$SCNST_63_1'
'$SCNST_63':
	define_vector		'$SCNST_63_0'
'$SCNST_64_2':
	define_desc		0,2
	define_atom		timer
	define_integer		1
'$SCNST_64_1':
	define_vector		'$SCNST_64_2'
	define_atom		[]
'$SCNST_64_0':
	define_desc		0,3
	define_atom		entry
	define_atom		pdss_timer_device
	define_list		'$SCNST_64_1'
'$SCNST_64':
	define_vector		'$SCNST_64_0'
'$SCNST_65_2':
	define_desc		0,2
	define_atom		files
	define_integer		1
'$SCNST_65_1':
	define_vector		'$SCNST_65_2'
	define_atom		[]
'$SCNST_65_0':
	define_desc		0,3
	define_atom		entry
	define_atom		pdss_file_device
	define_list		'$SCNST_65_1'
'$SCNST_65':
	define_vector		'$SCNST_65_0'
'$SCNST_66_2':
	define_desc		0,2
	define_atom		create
	define_integer		8
'$SCNST_66_4':
	define_desc		0,2
	define_atom		create
	define_integer		7
'$SCNST_66_6':
	define_desc		0,2
	define_atom		execute
	define_integer		8
'$SCNST_66_8':
	define_desc		0,2
	define_atom		execute
	define_integer		7
'$SCNST_66_10':
	define_desc		0,2
	define_atom		raise
	define_integer		3
'$SCNST_66_9':
	define_vector		'$SCNST_66_10'
	define_atom		[]
'$SCNST_66_7':
	define_vector		'$SCNST_66_8'
	define_list		'$SCNST_66_9'
'$SCNST_66_5':
	define_vector		'$SCNST_66_6'
	define_list		'$SCNST_66_7'
'$SCNST_66_3':
	define_vector		'$SCNST_66_4'
	define_list		'$SCNST_66_5'
'$SCNST_66_1':
	define_vector		'$SCNST_66_2'
	define_list		'$SCNST_66_3'
'$SCNST_66_0':
	define_desc		0,3
	define_atom		entry
	define_atom		'Sho-en'
	define_list		'$SCNST_66_1'
'$SCNST_66':
	define_vector		'$SCNST_66_0'
'$SCNST_67_2':
	define_desc		0,2
	define_atom		do
	define_integer		1
'$SCNST_67_1':
	define_vector		'$SCNST_67_2'
	define_atom		[]
'$SCNST_67_0':
	define_desc		0,3
	define_atom		entry
	define_atom		pdss_code_device
	define_list		'$SCNST_67_1'
'$SCNST_67':
	define_vector		'$SCNST_67_0'
