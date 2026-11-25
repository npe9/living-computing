mpimos_pretty_printer:
	module		mpimos_pretty_printer
	entry		pprinter,2,pprinter_2_0
	module_entry		mpimos_pretty_printer
	predicate		pprinter,2
pprinter_2_0:
	execute		2,command_2_0
pprinter_2_1:
	suspend		pprinter_2_0
	module_entry		mpimos_pretty_printer
	predicate		command,2
command_2_0:
	try_me_else		command_2_1
	jump_on_non_list		1,command_2_3
	read_car		1,3
	vector		3
	jump_on_arity		3,5,command_2_1
	table_entry		command_2_1
	table_entry		command_2_1
	table_entry		command_2_5
	table_entry		command_2_1
	table_entry		command_2_6
command_2_5:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,command_2_1
	bucket_entry_a		putt,command_2_8
	bucket_entry_a		puttq,command_2_9
command_2_8:
	read_cdr		1,5
	read_element		3,1,6
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,3
	enqueue_goal		2,command_2_0
	put_values_inc		1,2,2
	put_atom		3,putt
	put_value		4,6
	execute		4,transform_4_0
command_2_9:
	read_cdr		1,5
	read_element		3,1,6
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,3
	enqueue_goal		2,command_2_0
	put_values_inc		1,2,2
	put_atom		3,puttq
	put_value		4,6
	execute		4,transform_4_0
command_2_6:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,command_2_1
	bucket_entry_a		putt,command_2_11
	bucket_entry_a		puttq,command_2_12
command_2_11:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,4
	enqueue_goal		2,command_2_0
	put_func		3,3,putt
	write_elements_inc		3,1,7,2
	put_value		1,2
	put_value		2,4
	put_value		4,6
	execute		4,transform_4_0
command_2_12:
	read_cdr		1,5
	read_elements_inc		3,1,6,3
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,4
	enqueue_goal		2,command_2_0
	put_func		3,3,puttq
	write_elements_inc		3,1,7,2
	put_value		1,2
	put_value		2,4
	put_value		4,6
	execute		4,transform_4_0
command_2_3:
	check_nil		1,command_2_1
	get_nil		2
	proceed
command_2_1:
	otherwise		command_2_0
	try_me_else		command_2_23
	wait_list_var_var		1,3,4
	get_reused_list_val_var		2,1,1,3,3
	put_values_dec		1,4,2
	execute		2,command_2_0
command_2_23:
	suspend		command_2_0
	module_entry		mpimos_pretty_printer
	predicate		transform,4
transform_4_0:
	try_me_else		transform_4_1
	vector		4
	jump_on_arity		4,4,transform_4_1
	table_entry		transform_4_1
	table_entry		transform_4_1
	table_entry		transform_4_3
	table_entry		transform_4_4
transform_4_3:
	read_element		4,0,5
	wait_atom		5,:-
	read_element		4,1,7
	wait_vector		7,2
	read_elements_inc		7,0,5,2
	collect_vector		4
	collect_vector		7
	create_goal		4
	set_variable		1,4
	set_values_inc		2,2,2
	set_value		4,6
	enqueue_goal		4,put_guard_4_0
	create_goal		3
	set_variable		1,2
	set_values_inc		2,4,2
	enqueue_goal		3,put_declaration_3_0
	put_atom		3,:-
	execute		3,put_declaration_3_0
transform_4_4:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,transform_4_1
	bucket_entry_a		-->,transform_4_6
	bucket_entry_a		:-,transform_4_7
transform_4_6:
	read_element		4,1,6
	read_element		4,2,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'|'
	read_elements_inc		9,1,7,2
	collect_vector		4
	collect_vector		9
	create_goal		6
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_atom		4,nl
	set_integer		5,0
	set_value		6,8
	enqueue_goal		6,put_body_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,'|'
	enqueue_goal		3,put_bar_3_0
	create_goal		4
	set_variable		1,4
	set_values_inc		2,2,2
	set_value		4,7
	enqueue_goal		4,put_guard_4_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,-->
	enqueue_goal		3,put_neck_3_0
	put_value		4,6
	execute		4,put_term_4_0
transform_4_7:
	read_element		4,1,6
	read_element		4,2,9
	wait_vector		9,3
	read_element		9,0,7
	wait_atom		7,'|'
	read_elements_inc		9,1,7,2
	collect_vector		4
	collect_vector		9
	create_goal		6
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_atom		4,nl
	set_integer		5,0
	set_value		6,8
	enqueue_goal		6,put_body_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,'|'
	enqueue_goal		3,put_bar_3_0
	create_goal		4
	set_variable		1,4
	set_values_inc		2,2,2
	set_value		4,7
	enqueue_goal		4,put_guard_4_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,:-
	enqueue_goal		3,put_neck_3_0
	put_value		4,6
	execute		4,put_term_4_0
transform_4_1:
	otherwise		transform_4_0
	try_me_else		transform_4_12
	vector		4
	jump_on_arity		4,4,transform_4_12
	table_entry		transform_4_12
	table_entry		transform_4_12
	table_entry		transform_4_14
	table_entry		transform_4_15
transform_4_14:
	read_element		4,0,5
	wait_atom		5,:-
	read_element		4,1,5
	collect_value		3
	collect_vector		4
	create_goal		3
	set_variable		1,3
	set_value		2,2
	set_value		3,5
	enqueue_goal		3,put_declaration_3_0
	put_value		2,3
	put_atom		3,:-
	execute		3,put_declaration_3_0
transform_4_15:
	read_element		4,0,5
	atom		5
	branch_on_atom		5,2,transform_4_12
	bucket_entry_a		-->,transform_4_17
	bucket_entry_a		:-,transform_4_18
transform_4_17:
	read_elements_inc		4,1,6,2
	collect_vector		4
	create_goal		6
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_atom		4,nl
	set_integer		5,0
	set_value		6,7
	enqueue_goal		6,put_body_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,-->
	enqueue_goal		3,put_non_guard_neck_3_0
	put_value		4,6
	execute		4,put_term_4_0
transform_4_18:
	read_elements_inc		4,1,6,2
	collect_vector		4
	create_goal		6
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_atom		4,nl
	set_integer		5,0
	set_value		6,7
	enqueue_goal		6,put_body_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,:-
	enqueue_goal		3,put_non_guard_neck_3_0
	put_value		4,6
	execute		4,put_term_4_0
transform_4_12:
	otherwise		transform_4_0
	execute		4,put_term_4_0
transform_4_23:
	suspend		transform_4_0
	module_entry		mpimos_pretty_printer
	predicate		put_guard,4
put_guard_4_0:
	try_me_else		put_guard_4_1
	wait_vector		4,3
	read_element		4,0,5
	wait_atom		5,','
	read_elements_inc		4,1,5,2
	collect_vector		4
	create_goal		4
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_value		4,6
	enqueue_goal		4,put_guard_4_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,','
	enqueue_goal		3,put_guard_separator_3_0
	put_value		4,5
	execute		4,put_guard_4_0
put_guard_4_1:
	otherwise		put_guard_4_0
	execute		4,put_term_4_0
put_guard_4_6:
	suspend		put_guard_4_0
	module_entry		mpimos_pretty_printer
	predicate		put_body,6
put_body_6_0:
	try_me_else		put_body_6_1
	vector		6
	jump_on_arity		6,4,put_body_6_1
	table_entry		put_body_6_1
	table_entry		put_body_6_3
	table_entry		put_body_6_1
	table_entry		put_body_6_4
put_body_6_3:
	read_element		6,0,8
	vector		8
	g_vector		8,7
	put_integer		9,0
	g_less_than		9,7
	collect_vector		6
	put_structured_constant		6,'$SCNST_0'
	get_list_val_var		1,10,6,9
	put_integer		1,3
	b_add		5,1,5
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		6,1,2
	put_value		1,9
	put_value		2,6
	put_integer		6,0
	execute		8,put_body_vector_8_0
put_body_6_4:
	read_element		6,0,7
	atom		7
	branch_on_atom		7,3,put_body_6_1
	bucket_entry_a		',',put_body_6_6
	bucket_entry_a		->,put_body_6_7
	bucket_entry_a		;,put_body_6_8
put_body_6_6:
	read_elements_inc		6,1,8,2
	collect_vector		6
	create_goal		6
	set_variable		1,6
	set_value		2,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_value		6,9
	enqueue_goal		6,put_body_6_0
	create_goal		5
	set_variable		1,2
	set_value		2,6
	set_values_inc		3,4,2
	set_atom		5,','
	enqueue_goal		5,put_body_separator_5_0
	put_value		6,8
	execute		6,put_body_6_0
put_body_6_7:
	read_elements_inc		6,1,8,2
	put_structured_constant		7,'$SCNST_2'
	get_list_val_var		1,11,7,10
	b_increment		5,5
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		7,1,2
	put_reused_func		6,6,->
	write_elements_inc		6,1,8,2
	put_value		1,10
	put_value		2,7
	execute		6,put_body_case_6_0
put_body_6_8:
	read_elements_inc		6,1,8,2
	put_structured_constant		7,'$SCNST_4'
	get_list_val_var		1,11,7,10
	b_increment		5,5
	put_structured_constant		1,'$SCNST_5'
	put_list_val_val		7,1,2
	put_reused_func		6,6,;
	write_elements_inc		6,1,8,2
	put_value		1,10
	put_value		2,7
	execute		6,put_body_case_6_0
put_body_6_1:
	otherwise		put_body_6_0
	collect_value		5
	collect_value		4
	put_value		4,6
	execute		4,put_term_4_0
put_body_6_13:
	suspend		put_body_6_0
	module_entry		mpimos_pretty_printer
	predicate		put_body_vector,8
put_body_vector_8_0:
	try_me_else		put_body_vector_8_1
	integer		6
	integer		7
	g_less_than		6,7
	put_marked_value		9,6
	put_void		10
	b_set_vector_element		8,9,8,10,9
	b_increment		6,6
	create_goal		8
	set_variable		1,10
	set_value		2,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_values_inc		6,6,2
	set_value		8,9
	enqueue_goal		8,put_body_vector1_8_0
	put_value		2,10
	put_value		6,8
	execute		6,put_body_6_0
put_body_vector_8_1:
	suspend		put_body_vector_8_0
	module_entry		mpimos_pretty_printer
	predicate		put_body_vector1,8
put_body_vector1_8_0:
	try_me_else		put_body_vector1_8_1
	integer		6
	integer		7
	g_less_than		6,7
	put_marked_value		9,6
	put_void		10
	b_set_vector_element		8,9,8,10,9
	b_increment		6,6
	create_goal		8
	set_variable		1,10
	set_value		2,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_values_inc		6,6,2
	set_value		8,9
	enqueue_goal		8,put_body_vector1_8_0
	create_goal		6
	set_variable		1,2
	set_value		2,10
	set_values_inc		3,3,3
	set_value		6,8
	enqueue_goal		6,put_body_6_0
	put_values_inc		3,4,2
	put_atom		5,','
	execute		5,put_body_separator_5_0
put_body_vector1_8_1:
	try_me_else		put_body_vector1_8_3
	wait_value		6,7
	collect_value		8
	collect_value		6
	collect_value		5
	collect_value		4
	collect_value		3
	collect_value		7
	get_value		1,2
	proceed
put_body_vector1_8_3:
	suspend		put_body_vector1_8_0
	module_entry		mpimos_pretty_printer
	predicate		put_body_case,6
put_body_case_6_0:
	try_me_else		put_body_case_6_1
	wait_vector		6,3
	read_element		6,0,7
	atom		7
	branch_on_atom		7,2,put_body_case_6_1
	bucket_entry_a		->,put_body_case_6_4
	bucket_entry_a		;,put_body_case_6_5
put_body_case_6_4:
	read_elements_inc		6,1,8,2
	collect_value		4
	collect_vector		6
	create_goal		6
	set_variable		1,4
	set_value		2,2
	set_marked_value		3,3
	set_atom		4,flat
	set_value		5,5
	set_value		6,9
	enqueue_goal		6,put_body_6_0
	create_goal		3
	set_variable		1,2
	set_value		2,4
	set_atom		3,->
	enqueue_goal		3,put_body_bar_3_0
	put_value		4,8
	execute		4,put_guard_4_0
put_body_case_6_5:
	read_elements_inc		6,1,8,2
	collect_vector		6
	create_goal		6
	set_variable		1,6
	set_value		2,2
	set_marked_value		3,3
	set_marked_value		4,4
	set_marked_value		5,5
	set_value		6,9
	enqueue_goal		6,put_body_case_6_0
	create_goal		5
	set_variable		1,2
	set_value		2,6
	set_atom		3,nl
	set_value		4,5
	set_atom		5,;
	enqueue_goal		5,put_body_separator_5_0
	put_value		6,8
	execute		6,put_body_case_6_0
put_body_case_6_1:
	otherwise		put_body_case_6_0
	collect_value		5
	collect_value		4
	put_value		4,6
	execute		4,put_term_4_0
put_body_case_6_11:
	suspend		put_body_case_6_0
	module_entry		mpimos_pretty_printer
	predicate		put_neck,3
put_neck_3_0:
	put_structured_constant		4,'$SCNST_6'
	put_list_val_val		5,4,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	put_structured_constant		2,'$SCNST_7'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_neck_3_1:
	suspend		put_neck_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_non_guard_neck,3
put_non_guard_neck_3_0:
	put_structured_constant		4,'$SCNST_8'
	put_list_val_val		5,4,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	put_structured_constant		2,'$SCNST_9'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_non_guard_neck_3_1:
	suspend		put_non_guard_neck_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_bar,3
put_bar_3_0:
	put_structured_constant		4,'$SCNST_10'
	put_list_val_val		5,4,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,5
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	put_structured_constant		2,'$SCNST_11'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_bar_3_1:
	suspend		put_bar_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_declaration,3
put_declaration_3_0:
	put_structured_constant		4,'$SCNST_12'
	put_list_val_val		5,4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,5
	get_list_value		1,3
	proceed
put_declaration_3_1:
	suspend		put_declaration_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_guard_separator,3
put_guard_separator_3_0:
	put_structured_constant		4,'$SCNST_13'
	put_list_val_val		5,4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,5
	get_list_value		1,3
	proceed
put_guard_separator_3_1:
	suspend		put_guard_separator_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_body_bar,3
put_body_bar_3_0:
	put_structured_constant		4,'$SCNST_14'
	put_list_val_val		5,4,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,5
	put_structured_constant		2,'$SCNST_15'
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
put_body_bar_3_1:
	suspend		put_body_bar_3_0
	module_entry		mpimos_pretty_printer
	predicate		put_body_separator,5
put_body_separator_5_0:
	try_me_else		put_body_separator_5_1
	atom		3
	branch_on_atom		3,2,put_body_separator_5_1
	bucket_entry_a		flat,put_body_separator_5_3
	bucket_entry_a		nl,put_body_separator_5_4
put_body_separator_5_3:
	collect_value		4
	put_structured_constant		3,'$SCNST_16'
	put_list_val_val		4,3,2
	put_func		2,2,putt
	write_element_value		2,1,5
	put_list_val_val		3,2,4
	get_list_value		1,3
	proceed
put_body_separator_5_4:
	integer		4
	test_integer		4,0,put_body_separator_5_6
	put_structured_constant		3,'$SCNST_17'
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_func		3,2,putt
	write_element_value		3,1,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_body_separator_5_6:
	put_integer		6,0
	g_less_than		6,4
	put_func		3,2,tab
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	put_structured_constant		2,'$SCNST_18'
	put_list_val_val		3,2,4
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_func		3,2,putt
	write_element_value		3,1,5
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_body_separator_5_1:
	suspend		put_body_separator_5_0
	module_entry		mpimos_pretty_printer
	predicate		put_term,4
put_term_4_0:
	try_me_else		put_term_4_1
	jump_on_non_atom		3,put_term_4_3
	branch_on_atom		3,2,put_term_4_1
	bucket_entry_a		putt,put_term_4_4
	bucket_entry_a		puttq,put_term_4_5
put_term_4_4:
	put_func		3,2,putt
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_term_4_5:
	put_func		3,2,puttq
	write_element_value		3,1,4
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_term_4_3:
	check_vector		3,3,put_term_4_1
	read_element		3,0,5
	atom		5
	branch_on_atom		5,2,put_term_4_1
	bucket_entry_a		putt,put_term_4_7
	bucket_entry_a		puttq,put_term_4_8
put_term_4_7:
	read_elements_inc		3,1,6,2
	collect_vector		3
	put_func		3,4,putt
	write_element_value		3,1,4
	write_elements_inc		3,2,6,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_term_4_8:
	read_elements_inc		3,1,6,2
	collect_vector		3
	put_func		3,4,puttq
	write_element_value		3,1,4
	write_elements_inc		3,2,6,2
	put_list_val_val		4,3,2
	get_list_value		1,4
	proceed
put_term_4_1:
	suspend		put_term_4_0
	begin_const_section		mpimos_pretty_printer
'$SCNST_0_1':
	define_desc		11,1
	define_integer		2128763
'$SCNST_0_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		11,1
	define_integer		8224032
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		27,1
	define_integer		40
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_4':
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		27,1
	define_integer		41
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_5':
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_6_0':
	define_desc		0,2
	define_atom		tab
	define_integer		4
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putc
	define_integer		32
'$SCNST_16':
'$SCNST_15':
'$SCNST_14':
'$SCNST_13':
'$SCNST_12':
'$SCNST_11':
'$SCNST_9':
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putc
	define_integer		9
'$SCNST_18':
'$SCNST_17':
'$SCNST_10':
'$SCNST_8':
	define_vector		'$SCNST_8_0'
