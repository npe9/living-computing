mpimos_unparser:
	module		mpimos_unparser
	entry		create,2,create_2_0
	entry		make_variable_name,2,make_variable_name_2_0
	module_entry		mpimos_unparser
	predicate		create,2
create_2_0:
	put_value		5,2
	put_integer		2,10
	put_integer		3,10
	put_atom		4,na
	execute		5,do_5_0
create_2_1:
	suspend		create_2_0
	module_entry		mpimos_unparser
	predicate		do,5
do_5_0:
	try_me_else		do_5_1
	jump_on_non_list		1,do_5_3
	read_car		1,6
	vector		6
	jump_on_arity		6,4,do_5_1
	table_entry		do_5_1
	table_entry		do_5_1
	table_entry		do_5_5
	table_entry		do_5_6
do_5_5:
	read_element		6,0,7
	atom		7
	branch_on_atom		7,3,do_5_1
	bucket_entry_a		print_depth,do_5_8
	bucket_entry_a		print_length,do_5_9
	bucket_entry_a		print_var_mode,do_5_10
do_5_8:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	collect_list		1
	collect_value		3
	collect_vector		6
	put_value		1,8
	put_value		3,9
	execute		5,do_5_0
do_5_9:
	read_cdr		1,8
	read_element		6,1,9
	integer		9
	collect_list		1
	collect_value		2
	collect_vector		6
	put_values_inc		1,8,2
	execute		5,do_5_0
do_5_10:
	read_element		6,1,8
	atom		8
	branch_on_atom		8,3,do_5_1
	bucket_entry_a		di,do_5_12
	bucket_entry_a		na,do_5_13
	bucket_entry_a		nu,do_5_14
do_5_12:
	read_cdr		1,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,9
	put_atom		4,di
	execute		5,do_5_0
do_5_13:
	read_cdr		1,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,9
	put_atom		4,na
	execute		5,do_5_0
do_5_14:
	read_cdr		1,9
	collect_list		1
	collect_value		4
	collect_vector		6
	put_value		1,9
	put_atom		4,nu
	execute		5,do_5_0
do_5_6:
	read_element		6,0,7
	atom		7
	branch_on_atom		7,3,do_5_1
	bucket_entry_a		putet,do_5_16
	bucket_entry_a		putt,do_5_17
	bucket_entry_a		puttq,do_5_18
do_5_16:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	collect_list		1
	collect_vector		6
	put_value		12,2
	put_values_inc		6,3,2
	put_value		13,5
	create_goal		5
	set_value		1,8
	set_marked_value		2,12
	set_marked_value		3,6
	set_marked_value		4,7
	set_variable		5,11
	enqueue_goal		5,do_5_0
	put_integer		1,1
	put_values_inc		2,9,2
	put_nil		4
	put_value		5,12
	put_integer		8,1
	put_value		9,13
	put_value		10,11
	put_integer		11,0
	put_void		12
	put_integer		13,1200
	execute		13,term_13_0
do_5_17:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	collect_list		1
	collect_vector		6
	put_value		12,2
	put_values_inc		6,3,2
	put_value		13,5
	create_goal		5
	set_value		1,8
	set_marked_value		2,12
	set_marked_value		3,6
	set_marked_value		4,7
	set_variable		5,11
	enqueue_goal		5,do_5_0
	put_integer		1,0
	put_values_inc		2,9,2
	put_nil		4
	put_value		5,12
	put_integer		8,0
	put_value		9,13
	put_value		10,11
	put_integer		11,0
	put_void		12
	put_integer		13,1200
	execute		13,term_13_0
do_5_18:
	read_cdr		1,8
	read_elements_inc		6,1,9,2
	collect_list		1
	collect_vector		6
	put_value		12,2
	put_values_inc		6,3,2
	put_value		13,5
	create_goal		5
	set_value		1,8
	set_marked_value		2,12
	set_marked_value		3,6
	set_marked_value		4,7
	set_variable		5,11
	enqueue_goal		5,do_5_0
	put_integer		1,0
	put_values_inc		2,9,2
	put_nil		4
	put_value		5,12
	put_integer		8,1
	put_value		9,13
	put_value		10,11
	put_integer		11,0
	put_void		12
	put_integer		13,1200
	execute		13,term_13_0
do_5_3:
	check_nil		1,do_5_1
	collect_value		4
	collect_value		3
	collect_value		2
	get_nil		5
	proceed
do_5_1:
	suspend		do_5_0
	module_entry		mpimos_unparser
	predicate		term,13
term_13_0:
	try_me_else		term_13_1
	vector		2
	jump_on_arity		2,4,term_13_1
	table_entry		term_13_1
	table_entry		term_13_1
	table_entry		term_13_3
	table_entry		term_13_4
term_13_3:
	read_element		2,0,14
	jump_on_non_atom		14,term_13_6
	test_atom		14,'$VAR',term_13_1
	read_element		2,1,15
	integer		15
	put_integer		16,0
	g_not_less_than		15,16
	collect_value		13
	collect_value		1
	collect_vector		2
	get_value		9,10
	put_value		1,15
	put_values_inc		2,3,6
	put_values_inc		8,11,2
	execute		9,variable1_9_0
term_13_6:
	is_integer		14,term_13_1
	read_element		2,1,15
	put_integer		16,1346655059
	g_equal		14,16
	collect_value		7
	collect_vector		2
	put_value		2,15
	put_atom		7,di
	execute		13,term_13_0
term_13_4:
	read_element		2,0,14
	wait_atom		14,'$VAR'
	read_elements_inc		2,1,14,2
	integer		14
	put_integer		16,0
	g_not_less_than		14,16
	string		15
	g_string		15,16,17
	wait_integer		17,8
	collect_value		13
	collect_value		1
	collect_vector		2
	get_value		9,10
	put_value		1,14
	put_values_inc		2,3,6
	put_values_inc		8,11,2
	put_value		10,15
	execute		10,variable2_10_0
term_13_1:
	otherwise		term_13_0
	try_me_else		term_13_13
	wait_integer		1,1
	put_integer		1,1
	execute		13,ex_term_13_0
term_13_13:
	otherwise		term_13_0
	try_me_else		term_13_18
	wait		2
	switch_on_type		2,term_13_19,term_13_20,term_13_21,term_13_22,term_13_23,term_13_24
term_13_21:
	collect_value		13
	execute		12,list_12_0
term_13_19:
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	put_values_inc		1,2,3
	put_values_inc		4,8,6
	execute		9,atom_9_0
term_13_20:
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	b_get_print_image		2,8,11,1,2,5
	get_value		5,12
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
term_13_22:
	test_arity		2,0,term_13_25
	collect_value		13
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	get_integer		12,125
	put_structured_constant		1,'$SCNST_0'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
term_13_25:
	g_vector		2,15
	put_integer		14,1
	g_less_than		14,15
	put_integer		16,0
	g_vector_element		2,16,14
	atom		14
	put_nil		17
	g_diff		14,17
	mark_element		2,16
	collect_value		17
	put_marked_value		14,14
	execute		15,functor_15_0
term_13_23:
	g_string		2,14,15
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		1
	put_value		7,3
	put_value		13,4
	put_value		6,5
	get_value		9,10
	put_value		1,2
	put_values_inc		2,14,2
	put_value		4,7
	put_value		5,13
	put_value		7,8
	put_values_inc		8,11,2
	execute		9,string_9_0
term_13_24:
	is_float		2,term_13_18
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	b_get_print_image		2,8,11,1,2,5
	get_value		5,12
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
term_13_18:
	otherwise		term_13_0
	try_me_else		term_13_29
	vector		2
	g_vector		2,14
	put_integer		15,1
	g_not_less_than		14,15
	collect_value		13
	put_value		13,14
	execute		13,vector_13_0
term_13_29:
	otherwise		term_13_0
	collect_value		13
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		12,34
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
term_13_33:
	suspend		term_13_0
	module_entry		mpimos_unparser
	predicate		ex_term,13
ex_term_13_0:
	try_me_else		ex_term_13_1
	vector		2
	jump_on_arity		2,5,ex_term_13_1
	table_entry		ex_term_13_1
	table_entry		ex_term_13_1
	table_entry		ex_term_13_3
	table_entry		ex_term_13_4
	table_entry		ex_term_13_5
ex_term_13_3:
	read_element		2,0,14
	atom		14
	hash_on_atom		14,4,ex_term_13_1
	bucket_entry_a		atom,ex_term_13_7
	bucket_entry_a		floating_point,ex_term_13_8
	bucket_entry_a		integer,ex_term_13_9
	bucket_entry_a		list,ex_term_13_10
ex_term_13_7:
	read_element		2,1,15
	atom		15
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	collect_vector		2
	put_value		1,15
	put_values_inc		2,3,2
	put_values_inc		4,8,6
	execute		9,atom_9_0
ex_term_13_8:
	read_element		2,1,15
	float		15
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	collect_vector		2
	b_get_print_image		15,8,11,1,2,5
	get_value		5,12
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
ex_term_13_9:
	read_element		2,1,15
	integer		15
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	collect_vector		2
	b_get_print_image		15,8,11,1,2,5
	get_value		5,12
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
ex_term_13_10:
	read_element		2,1,15
	list		15
	collect_value		13
	collect_vector		2
	put_value		2,15
	execute		12,list_12_0
ex_term_13_4:
	read_element		2,0,14
	wait_atom		14,vector
	read_element		2,1,15
	vector		15
	test_arity		15,0,ex_term_13_13
	try_me_else		ex_term_13_13
	read_element		2,2,16
	wait_integer		16,0
	collect_value		13
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		1
	collect_vector		2
	get_integer		12,125
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
ex_term_13_13:
	read_element		2,2,16
	try_me_else		ex_term_13_1
	integer		16
	g_vector		15,17
	wait_value		17,16
	put_integer		17,1
	g_less_than		17,16
	put_integer		18,0
	g_vector_element		15,18,17
	wait_vector		17,2
	read_element		17,0,19
	wait_atom		19,atom
	read_element		17,1,17
	atom		17
	put_nil		19
	g_diff		17,19
	mark_element		15,18
	collect_value		19
	collect_vector		2
	put_value		2,15
	put_marked_value		14,17
	put_value		15,16
	execute		15,functor_15_0
ex_term_13_5:
	read_element		2,0,14
	wait_atom		14,string
	read_elements_inc		2,1,14,3
	string		14
	g_string		14,17,18
	wait_value		17,15
	wait_value		18,16
	collect_value		13
	collect_value		7
	collect_value		6
	collect_value		1
	collect_value		17
	collect_value		18
	collect_vector		2
	put_value		7,3
	put_value		13,4
	put_value		6,5
	get_value		9,10
	put_values_inc		1,14,3
	put_value		4,7
	put_value		5,13
	put_value		7,8
	put_values_inc		8,11,2
	execute		9,string_9_0
ex_term_13_1:
	otherwise		ex_term_13_0
	try_me_else		ex_term_13_27
	wait_vector		2,3
	read_element		2,0,14
	wait_atom		14,vector
	read_elements_inc		2,1,14,2
	vector		14
	g_vector		14,16
	wait_value		16,15
	integer		15
	put_integer		17,1
	g_not_less_than		15,17
	collect_value		13
	collect_value		16
	collect_vector		2
	put_value		2,14
	put_value		13,15
	execute		13,vector_13_0
ex_term_13_27:
	otherwise		ex_term_13_0
	collect_value		13
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		12,34
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
ex_term_13_32:
	suspend		ex_term_13_0
	module_entry		mpimos_unparser
	predicate		atom,9
atom_9_0:
	put_func		10,3,operator
	write_element_marked_value		10,1,1
	write_element_variable		10,2,11
	get_list_val_var		5,12,10,10
	put_value		5,10
	put_value		10,11
	execute		10,atom_10_0
atom_9_1:
	suspend		atom_9_0
	module_entry		mpimos_unparser
	predicate		atom,10
atom_10_0:
	try_me_else		atom_10_1
	wait_atom		1,','
	try_me_else		atom_10_3
	integer		9
	wait_list_var_var		10,14,11
	wait_vector		14,2
	read_elements_inc		14,0,12,2
	integer		12
	g_less_than		9,12
	collect_value		11
	collect_value		13
	collect_vector		14
	get_integer		8,41
	put_structured_constant		1,'$SCNST_4'
	put_reused_list_val_val		8,10,1,3
	put_list		1
	write_car_variable		1,9
	write_cdr_value		1,8
	put_structured_constant		3,'$SCNST_5'
	put_list_val_val		8,3,1
	get_value		5,6
	create_goal		3
	set_value		1,7
	set_value		2,2
	set_value		3,8
	enqueue_goal		3,parenthesis_left_space_3_0
	put_value		1,4
	put_integer		2,40
	put_value		3,9
	put_void		4
	execute		4,get_comma_image_4_0
atom_10_3:
	try_me_else		atom_10_1
	wait_nil		10
	collect_value		9
	put_list		1
	write_car_variable		1,9
	write_cdr_value		1,3
	get_list_value		2,1
	get_value		5,6
	put_value		1,4
	put_value		2,7
	put_values_dec		3,9,2
	execute		4,get_comma_image_4_0
atom_10_1:
	try_me_else		atom_10_6
	integer		9
	list		10
	read_car		10,11
	wait_vector		11,2
	read_element		11,0,12
	integer		12
	read_element		11,1,13
	read_cdr		10,14
	try_me_else		atom_10_11
	g_not_less_than		9,12
	collect_list		10
	collect_value		13
	collect_vector		11
	put_value		10,14
	execute		10,atom_10_0
atom_10_11:
	try_me_else		atom_10_6
	put_atom		15,','
	g_diff		1,15
	collect_value		14
	collect_value		13
	collect_vector		11
	put_integer		9,40
	b_get_print_image		1,4,9,1,4,9
	get_integer		8,41
	put_structured_constant		4,'$SCNST_6'
	put_reused_list_val_val		8,10,4,3
	put_list_val_val		3,1,8
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		4,1,3
	get_value		5,6
	put_value		1,7
	put_value		3,4
	execute		3,parenthesis_left_space_3_0
atom_10_6:
	try_me_else		atom_10_12
	wait_nil		10
	put_atom		11,','
	g_diff		1,11
	collect_value		9
	b_get_print_image		1,4,7,1,4,7
	get_value		7,8
	put_list_val_val		4,1,3
	get_list_value		2,4
	get_value		5,6
	proceed
atom_10_12:
	suspend		atom_10_0
	module_entry		mpimos_unparser
	predicate		get_comma_image,4
get_comma_image_4_0:
	try_me_else		get_comma_image_4_1
	integer		1
	jump_on_integer		1,2,get_comma_image_4_1
	table_entry		get_comma_image_4_3
	table_entry		get_comma_image_4_4
get_comma_image_4_3:
	collect_value		2
	put_structured_constant		1,'$SCNST_8'
	get_value		3,1
	get_integer		4,44
	proceed
get_comma_image_4_4:
	integer		2
	test_integer		2,39,get_comma_image_4_6
	put_structured_constant		1,'$SCNST_9'
	get_value		3,1
	get_integer		4,39
	proceed
get_comma_image_4_6:
	put_integer		5,48
	g_not_less_than		2,5
	put_integer		5,57
	g_not_less_than		5,2
	put_structured_constant		1,'$SCNST_10'
	get_value		3,1
	get_integer		4,39
	proceed
get_comma_image_4_1:
	otherwise		get_comma_image_4_0
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_11'
	get_value		3,1
	get_integer		4,39
	proceed
get_comma_image_4_11:
	suspend		get_comma_image_4_0
	module_entry		mpimos_unparser
	predicate		variable1,9
variable1_9_0:
	try_me_else		variable1_9_1
	atom		6
	branch_on_atom		6,3,variable1_9_1
	bucket_entry_a		di,variable1_9_3
	bucket_entry_a		na,variable1_9_4
	bucket_entry_a		nu,variable1_9_5
variable1_9_3:
	collect_value		5
	collect_value		4
	get_integer		9,41
	put_atom		4,'$VAR'
	put_marked_value		5,7
	b_get_print_image		4,5,8,4,5,6
	put_integer		5,40
	b_get_print_image		1,7,5,1,5,6
	put_structured_constant		5,'$SCNST_12'
	put_list_val_val		6,5,3
	put_list_val_val		3,1,6
	put_structured_constant		1,'$SCNST_13'
	put_list_val_val		5,1,3
	put_list_val_val		1,4,5
	get_list_value		2,1
	proceed
variable1_9_4:
	collect_value		7
	collect_value		5
	collect_value		4
	get_integer		9,65
	put_list		4
	write_car_variable		4,5
	write_cdr_value		4,3
	create_goal		3
	set_value		1,8
	set_value		2,2
	set_value		3,4
	enqueue_goal		3,variable_left_space_3_0
	put_value		2,5
	execute		2,make_variable_name_2_0
variable1_9_5:
	collect_value		5
	collect_value		4
	put_integer		4,0
	b_get_print_image		1,7,4,1,4,5
	get_value		5,9
	put_list_val_val		4,1,3
	put_structured_constant		1,'$SCNST_14'
	put_list_val_val		3,1,4
	put_value		1,8
	execute		3,variable_left_space_3_0
variable1_9_1:
	suspend		variable1_9_0
	module_entry		mpimos_unparser
	predicate		variable2,10
variable2_10_0:
	try_me_else		variable2_10_1
	atom		6
	branch_on_atom		6,3,variable2_10_1
	bucket_entry_a		di,variable2_10_3
	bucket_entry_a		na,variable2_10_4
	bucket_entry_a		nu,variable2_10_5
variable2_10_3:
	collect_value		5
	collect_value		4
	get_integer		9,41
	put_atom		4,'$VAR'
	put_marked_value		5,7
	b_get_print_image		4,5,8,4,5,6
	put_integer		5,40
	b_get_print_image		1,7,5,1,5,6
	put_integer		5,44
	b_get_print_image		10,7,5,5,6,7
	put_structured_constant		6,'$SCNST_15'
	put_list_val_val		7,6,3
	put_list_val_val		3,5,7
	put_structured_constant		5,'$SCNST_16'
	put_list_val_val		6,5,3
	put_list_val_val		3,1,6
	put_structured_constant		1,'$SCNST_17'
	put_list_val_val		5,1,3
	put_list_val_val		1,4,5
	get_list_value		2,1
	proceed
variable2_10_4:
	collect_value		7
	collect_value		5
	collect_value		4
	collect_value		1
	get_integer		9,65
	put_list_val_val		4,10,3
	put_value		1,8
	put_value		3,4
	execute		3,variable_left_space_3_0
variable2_10_5:
	collect_value		10
	collect_value		5
	collect_value		4
	put_integer		4,0
	b_get_print_image		1,7,4,1,4,5
	get_value		5,9
	put_list_val_val		4,1,3
	put_structured_constant		1,'$SCNST_18'
	put_list_val_val		3,1,4
	put_value		1,8
	execute		3,variable_left_space_3_0
variable2_10_1:
	suspend		variable2_10_0
	module_entry		mpimos_unparser
	predicate		variable_left_space,3
variable_left_space_3_0:
	try_me_else		variable_left_space_3_1
	integer		1
	test_integer		1,95,variable_left_space_3_3
	put_structured_constant		1,'$SCNST_19'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
variable_left_space_3_3:
	try_me_else		variable_left_space_3_4
	put_integer		4,48
	g_not_less_than		1,4
	put_integer		4,57
	g_not_less_than		4,1
	put_structured_constant		1,'$SCNST_20'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
variable_left_space_3_4:
	try_me_else		variable_left_space_3_5
	put_integer		4,65
	g_not_less_than		1,4
	put_integer		4,90
	g_not_less_than		4,1
	put_structured_constant		1,'$SCNST_21'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
variable_left_space_3_5:
	try_me_else		variable_left_space_3_1
	put_integer		4,97
	g_not_less_than		1,4
	put_integer		4,122
	g_not_less_than		4,1
	put_structured_constant		1,'$SCNST_22'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
variable_left_space_3_1:
	otherwise		variable_left_space_3_0
	collect_value		1
	get_value		2,3
	proceed
variable_left_space_3_11:
	suspend		variable_left_space_3_0
	module_entry		mpimos_unparser
	predicate		make_variable_name,2
make_variable_name_2_0:
	try_me_else		make_variable_name_2_1
	integer		1
	put_integer		3,0
	g_not_less_than		1,3
	put_value		4,2
	put_marked_value		2,1
	put_integer		3,26
	b_divide		2,3,2
	put_integer		3,26
	b_modulo		1,3,1
	put_integer		3,65
	b_add		1,3,1
	put_integer		3,1
	put_integer		5,8
	b_new_string		3,3,5
	put_integer		5,0
	b_set_string_element		3,5,1,3
	put_values_inc		1,2,3
	execute		3,make_variable_name0_3_0
make_variable_name_2_1:
	suspend		make_variable_name_2_0
	module_entry		mpimos_unparser
	predicate		make_variable_name0,3
make_variable_name0_3_0:
	try_me_else		make_variable_name0_3_1
	integer		1
	test_integer		1,0,make_variable_name0_3_3
	get_value		3,2
	proceed
make_variable_name0_3_3:
	put_integer		4,0
	g_less_than		4,1
	put_marked_value		4,1
	put_integer		5,26
	b_divide		4,5,4
	put_integer		5,26
	b_modulo		1,5,1
	put_integer		5,65
	b_add		1,5,1
	put_integer		5,1
	put_integer		6,8
	b_new_string		5,5,6
	put_integer		6,0
	b_set_string_element		5,6,1,1
	b_append_string		1,2,2
	put_value		1,4
	execute		3,make_variable_name0_3_0
make_variable_name0_3_1:
	suspend		make_variable_name0_3_0
	module_entry		mpimos_unparser
	predicate		string,9
string_9_0:
	try_me_else		string_9_1
	wait_integer		3,8
	collect_value		6
	collect_value		2
	b_get_print_image		1,7,8,1,2,3
	get_value		3,9
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
string_9_1:
	otherwise		string_9_0
	collect_value		8
	put_value		10,2
	put_value		11,6
	put_marked_value		2,7
	put_integer		6,40
	b_get_print_image		3,2,6,2,3,6
	put_structured_constant		3,'$SCNST_23'
	put_list_val_var		6,3,8
	put_list_val_val		3,2,6
	put_structured_constant		2,'$SCNST_24'
	put_list_val_val		6,2,3
	get_list_value		4,6
	get_integer		9,125
	put_integer		2,0
	put_value		3,10
	put_value		4,8
	put_value		6,7
	put_value		7,11
	execute		7,string_args_7_0
string_9_6:
	suspend		string_9_0
	module_entry		mpimos_unparser
	predicate		string_args,7
string_args_7_0:
	try_me_else		string_args_7_1
	wait_integer		3,0
	collect_value		7
	collect_value		6
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_25'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
string_args_7_1:
	otherwise		string_args_7_0
	try_me_else		string_args_7_6
	integer		7
	test_integer		7,0,string_args_7_8
	collect_value		6
	collect_value		3
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_26'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
string_args_7_8:
	put_integer		8,0
	g_less_than		8,7
	put_marked_value		8,2
	b_string_element		1,8,1,8
	put_marked_value		9,6
	put_integer		10,123
	b_get_print_image		1,9,10,1,9,10
	put_list_val_var		9,1,10
	put_structured_constant		1,'$SCNST_27'
	put_list_val_val		11,1,9
	get_list_value		4,11
	b_increment		2,1
	put_value		2,1
	b_decrement		7,1
	put_value		7,1
	put_value		1,8
	put_value		4,10
	execute		7,string_args2_7_0
string_args_7_6:
	suspend		string_args_7_0
	module_entry		mpimos_unparser
	predicate		string_args2,7
string_args2_7_0:
	try_me_else		string_args2_7_1
	wait_value		2,3
	collect_value		7
	collect_value		6
	collect_value		2
	collect_value		1
	collect_value		3
	put_structured_constant		1,'$SCNST_28'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
string_args2_7_1:
	otherwise		string_args2_7_0
	try_me_else		string_args2_7_3
	integer		2
	integer		7
	try_me_else		string_args2_7_6
	g_not_less_than		7,2
	put_marked_value		8,2
	b_string_element		1,8,1,8
	put_marked_value		9,6
	put_integer		10,44
	b_get_print_image		1,9,10,1,9,10
	put_list_val_var		9,1,10
	put_structured_constant		1,'$SCNST_29'
	put_list_val_val		11,1,9
	get_list_value		4,11
	b_increment		2,1
	put_value		2,1
	b_decrement		7,1
	put_value		7,1
	put_value		1,8
	put_value		4,10
	execute		7,string_args2_7_0
string_args2_7_6:
	collect_value		6
	collect_value		3
	collect_value		1
	put_structured_constant		1,'$SCNST_30'
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
string_args2_7_3:
	suspend		string_args2_7_0
	module_entry		mpimos_unparser
	predicate		list,12
list_12_0:
	try_me_else		list_12_1
	wait_list_var_var		2,13,14
	integer		6
	put_integer		15,0
	g_less_than		15,6
	collect_value		11
	b_decrement		6,6
	put_marked_value		11,5
	b_decrement		11,11
	put_structured_constant		15,'$SCNST_31'
	get_reused_list_val_var		3,2,2,15,15
	create_goal		13
	set_marked_value		1,1
	set_value		2,14
	set_variable		3,17
	set_values_inc		4,4,2
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,16
	set_values_inc		10,10,2
	set_variable		12,14
	set_value		13,12
	enqueue_goal		13,list_13_0
	put_value		2,13
	put_value		3,15
	put_value		4,17
	put_value		10,16
	put_integer		11,91
	put_value		12,14
	put_integer		13,999
	execute		13,term_13_0
list_12_1:
	try_me_else		list_12_3
	integer		6
	put_integer		13,0
	g_not_less_than		13,6
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	get_integer		12,93
	put_structured_constant		1,'$SCNST_32'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
list_12_3:
	suspend		list_12_0
	module_entry		mpimos_unparser
	predicate		list,13
list_13_0:
	try_me_else		list_13_1
	integer		1
	jump_on_integer		1,2,list_13_1
	table_entry		list_13_3
	table_entry		list_13_4
list_13_3:
	jump_on_non_list_var_var		2,list_13_6,14,15
	integer		11
	try_me_else		list_13_8
	put_integer		16,0
	g_less_than		16,11
	collect_value		12
	b_decrement		11,1
	put_structured_constant		11,'$SCNST_33'
	get_reused_list_val_var		3,2,2,11,11
	create_goal		13
	set_integer		1,0
	set_value		2,15
	set_variable		3,16
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,15
	set_value		10,10
	set_value		11,1
	set_variable		12,12
	set_value		13,13
	enqueue_goal		13,list_13_0
	put_integer		1,0
	put_value		2,14
	put_value		3,11
	put_value		4,16
	put_value		10,15
	put_integer		11,44
	put_integer		13,999
	execute		13,term_13_0
list_13_8:
	collect_value		12
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		15
	collect_value		14
	get_integer		13,93
	put_structured_constant		1,'$SCNST_34'
	put_reused_list_val_val		2,2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
list_13_6:
	check_nil		2,list_13_1
	collect_value		12
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_integer		13,93
	put_structured_constant		1,'$SCNST_35'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
list_13_4:
	wait_vector		2,2
	read_element		2,0,14
	atom		14
	branch_on_atom		14,2,list_13_1
	bucket_entry_a		atom,list_13_11
	bucket_entry_a		list,list_13_12
list_13_11:
	read_element		2,1,15
	wait_nil		15
	collect_value		12
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_vector		2
	get_integer		13,93
	put_structured_constant		1,'$SCNST_36'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
list_13_12:
	read_element		2,1,15
	wait_list_var_var		15,16,17
	integer		11
	try_me_else		list_13_15
	put_integer		18,0
	g_less_than		18,11
	collect_value		12
	collect_vector		2
	b_decrement		11,1
	put_structured_constant		2,'$SCNST_37'
	get_reused_list_val_var		3,12,15,2,11
	create_goal		13
	set_integer		1,1
	set_value		2,17
	set_variable		3,15
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,14
	set_value		10,10
	set_value		11,1
	set_variable		12,12
	set_value		13,13
	enqueue_goal		13,list_13_0
	put_integer		1,1
	put_value		2,16
	put_value		3,11
	put_value		4,15
	put_value		10,14
	put_integer		11,44
	put_integer		13,999
	execute		13,term_13_0
list_13_15:
	collect_value		12
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		17
	collect_value		16
	collect_vector		2
	get_integer		13,93
	put_structured_constant		1,'$SCNST_38'
	put_reused_list_val_val		2,15,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
list_13_1:
	otherwise		list_13_0
	collect_value		12
	collect_value		11
	put_structured_constant		11,'$SCNST_39'
	get_list_val_var		3,14,11,12
	get_integer		13,93
	put_structured_constant		3,'$SCNST_40'
	put_list_val_val		11,3,4
	put_values_dec		3,12,2
	put_integer		11,124
	put_void		12
	put_integer		13,999
	execute		13,term_13_0
list_13_32:
	suspend		list_13_0
	module_entry		mpimos_unparser
	predicate		functor,15
functor_15_0:
	try_me_else		functor_15_1
	integer		6
	try_me_else		functor_15_3
	integer		15
	jump_on_integer		15,4,functor_15_3
	table_entry		functor_15_3
	table_entry		functor_15_3
	table_entry		functor_15_5
	table_entry		functor_15_6
functor_15_5:
	put_integer		16,0
	g_less_than		16,6
	b_decrement		6,6
	put_func		15,3,operator
	write_element_marked_value		15,1,14
	write_element_variable		15,2,16
	get_list_val_var		9,17,15,15
	put_value		9,15
	put_value		15,16
	execute		15,functor1_15_0
functor_15_6:
	put_integer		16,0
	g_less_than		16,6
	b_decrement		6,6
	put_func		15,3,operator
	write_element_marked_value		15,1,14
	write_element_variable		15,2,16
	get_list_val_var		9,17,15,15
	put_value		9,15
	put_value		15,16
	execute		15,functor2_15_0
functor_15_3:
	try_me_else		functor_15_1
	put_integer		16,0
	g_not_less_than		16,6
	collect_value		15
	collect_value		13
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	b_get_print_image		14,8,11,1,2,5
	get_integer		12,41
	put_structured_constant		2,'$SCNST_41'
	put_list_val_val		5,2,4
	put_list_val_val		2,1,5
	get_list_value		3,2
	get_value		9,10
	proceed
functor_15_1:
	otherwise		functor_15_0
	collect_value		13
	b_decrement		6,6
	put_values_inc		13,14,2
	execute		14,functor3_14_0
functor_15_10:
	suspend		functor_15_0
	module_entry		mpimos_unparser
	predicate		functor1,15
functor1_15_0:
	try_me_else		functor1_15_1
	wait_vector		2,2
	read_elements_inc		2,0,16,2
	integer		13
	list		15
	read_car		15,18
	wait_vector		18,2
	read_element		18,0,19
	integer		19
	read_element		18,1,20
	atom		20
	hash_on_atom		20,4,functor1_15_1
	bucket_entry_a		fx,functor1_15_8
	bucket_entry_a		fy,functor1_15_9
	bucket_entry_a		xf,functor1_15_10
	bucket_entry_a		yf,functor1_15_11
functor1_15_8:
	read_cdr		15,21
	try_me_else		functor1_15_12
	g_not_less_than		13,19
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_value		16,2
	put_marked_value		2,8
	b_get_print_image		14,2,11,2,11,13
	get_reused_list_val_var		3,14,15,2,11
	put_value		2,17
	put_value		3,11
	put_value		11,13
	put_value		13,16
	execute		13,term_13_0
functor1_15_12:
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_marked_value		13,8
	put_integer		16,40
	b_get_print_image		14,13,16,13,14,16
	put_reused_list_val_var		14,15,13,18
	put_structured_constant		13,'$SCNST_42'
	put_list_val_val		15,13,14
	get_integer		12,41
	create_goal		13
	set_value		1,1
	set_values_inc		2,17,2
	put_structured_constant		1,'$SCNST_43'
	put_list_val_val		12,1,4
	set_value		4,12
	set_values_inc		5,5,6
	set_value		11,16
	set_void		12
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor1_15_9:
	read_cdr		15,21
	try_me_else		functor1_15_13
	g_not_less_than		13,19
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_value		16,2
	put_marked_value		2,8
	b_get_print_image		14,2,11,2,11,13
	get_reused_list_val_var		3,14,15,2,11
	put_value		2,17
	put_value		3,11
	put_value		11,13
	put_value		13,16
	execute		13,term_13_0
functor1_15_13:
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_marked_value		13,8
	put_integer		16,40
	b_get_print_image		14,13,16,13,14,16
	put_reused_list_val_var		14,15,13,18
	put_structured_constant		13,'$SCNST_44'
	put_list_val_val		15,13,14
	get_integer		12,41
	create_goal		13
	set_value		1,1
	set_values_inc		2,17,2
	put_structured_constant		1,'$SCNST_45'
	put_list_val_val		12,1,4
	set_value		4,12
	set_values_inc		5,5,6
	set_value		11,16
	set_void		12
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor1_15_10:
	read_cdr		15,21
	try_me_else		functor1_15_14
	g_not_less_than		13,19
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_value		16,2
	put_marked_value		2,8
	put_variable		13,18
	b_get_print_image		14,2,13,2,13,14
	get_value		14,12
	put_reused_list_val_val		12,15,2,4
	put_value		2,17
	put_value		4,12
	put_value		12,18
	put_value		13,16
	execute		13,term_13_0
functor1_15_14:
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_marked_value		13,8
	put_variable		16,18
	b_get_print_image		14,13,16,13,14,16
	put_structured_constant		14,'$SCNST_46'
	put_reused_list_val_var		15,15,14,14
	get_integer		12,41
	create_goal		13
	set_value		1,1
	set_value		2,17
	set_value		3,14
	put_structured_constant		1,'$SCNST_47'
	put_list_val_val		12,1,4
	put_list_val_val		1,13,12
	set_value		4,1
	set_values_inc		5,5,6
	set_integer		11,40
	set_value		12,18
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor1_15_11:
	read_cdr		15,21
	try_me_else		functor1_15_15
	g_not_less_than		13,19
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_value		16,2
	put_marked_value		2,8
	put_variable		13,18
	b_get_print_image		14,2,13,2,13,14
	get_value		14,12
	put_reused_list_val_val		12,15,2,4
	put_value		2,17
	put_value		4,12
	put_value		12,18
	put_value		13,16
	execute		13,term_13_0
functor1_15_15:
	collect_value		21
	collect_value		16
	collect_vector		2
	collect_vector		18
	b_decrement		19,2
	put_structured_constant		13,'$SCNST_48'
	put_reused_list_val_var		15,15,13,16
	get_integer		12,41
	put_marked_value		12,8
	put_variable		13,18
	b_get_print_image		14,12,13,12,13,14
	create_goal		13
	set_value		1,1
	set_values_dec		2,17,2
	put_structured_constant		1,'$SCNST_49'
	put_list_val_val		13,1,4
	put_list_val_val		1,12,13
	set_value		4,1
	set_values_inc		5,5,6
	set_integer		11,40
	set_value		12,18
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor1_15_1:
	try_me_else		functor1_15_16
	wait_nil		15
	collect_value		13
	put_value		13,14
	put_integer		14,2
	execute		14,functor3_14_0
functor1_15_16:
	otherwise		functor1_15_0
	try_me_else		functor1_15_39
	wait_list_var_var		15,16,17
	collect_list		15
	collect_value		16
	put_value		15,17
	execute		15,functor1_15_0
functor1_15_39:
	suspend		functor1_15_0
	module_entry		mpimos_unparser
	predicate		functor2,15
functor2_15_0:
	try_me_else		functor2_15_1
	wait_vector		2,3
	read_elements_inc		2,0,16,3
	integer		13
	list		15
	read_car		15,19
	wait_vector		19,2
	read_element		19,0,20
	integer		20
	read_element		19,1,21
	atom		21
	branch_on_atom		21,3,functor2_15_1
	bucket_entry_a		xfx,functor2_15_8
	bucket_entry_a		xfy,functor2_15_9
	bucket_entry_a		yfx,functor2_15_10
functor2_15_8:
	read_cdr		15,22
	try_me_else		functor2_15_11
	g_not_less_than		13,20
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	b_decrement		20,2
	put_value		16,2
	put_marked_value		2,8
	put_variable		13,19
	b_get_print_image		14,2,13,2,13,14
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,13
	set_value		10,10
	set_value		11,14
	set_value		12,12
	set_marked_value		13,16
	enqueue_goal		13,term_13_0
	put_reused_list_val_val		4,15,2,18
	put_value		2,17
	put_value		10,13
	put_value		12,19
	put_value		13,16
	execute		13,term_13_0
functor2_15_11:
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	b_decrement		20,2
	put_marked_value		13,8
	put_variable		16,19
	b_get_print_image		14,13,16,13,14,16
	get_integer		12,41
	put_structured_constant		12,'$SCNST_50'
	put_reused_list_val_var		14,15,12,15
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	put_structured_constant		12,'$SCNST_51'
	put_list_val_val		20,12,4
	set_value		4,20
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,4
	set_value		10,10
	set_value		11,16
	set_void		12
	set_marked_value		13,2
	enqueue_goal		13,term_13_0
	create_goal		13
	set_value		1,1
	set_value		2,17
	set_value		3,15
	put_list_val_val		1,13,18
	set_value		4,1
	set_values_inc		5,5,5
	set_value		10,4
	set_integer		11,40
	set_value		12,19
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,14
	execute		3,parenthesis_left_space_3_0
functor2_15_9:
	read_cdr		15,22
	try_me_else		functor2_15_12
	g_not_less_than		13,20
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	put_marked_value		2,20
	b_decrement		2,2
	put_value		16,2
	put_marked_value		2,8
	put_variable		13,19
	b_get_print_image		14,2,13,2,13,14
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,13
	set_value		10,10
	set_value		11,14
	set_value		12,12
	set_value		13,20
	enqueue_goal		13,term_13_0
	put_reused_list_val_val		4,15,2,18
	put_value		2,17
	put_value		10,13
	put_value		12,19
	put_value		13,16
	execute		13,term_13_0
functor2_15_12:
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	put_marked_value		2,20
	b_decrement		2,2
	put_marked_value		13,8
	put_variable		16,19
	b_get_print_image		14,13,16,13,14,16
	put_structured_constant		14,'$SCNST_52'
	put_reused_list_val_var		15,15,14,14
	get_integer		12,41
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	put_structured_constant		12,'$SCNST_53'
	put_list_val_val		21,12,4
	set_value		4,21
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,4
	set_value		10,10
	set_value		11,16
	set_void		12
	set_value		13,20
	enqueue_goal		13,term_13_0
	create_goal		13
	set_value		1,1
	set_value		2,17
	set_value		3,14
	put_list_val_val		1,13,18
	set_value		4,1
	set_values_inc		5,5,5
	set_value		10,4
	set_integer		11,40
	set_value		12,19
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor2_15_10:
	read_cdr		15,22
	try_me_else		functor2_15_13
	g_not_less_than		13,20
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	put_marked_value		2,20
	b_decrement		2,2
	put_marked_value		13,8
	put_variable		16,19
	b_get_print_image		14,13,16,13,14,16
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,14
	set_value		10,10
	set_value		11,16
	set_value		12,12
	set_value		13,2
	enqueue_goal		13,term_13_0
	put_reused_list_val_val		4,15,13,18
	put_value		2,17
	put_value		10,14
	put_values_inc		12,19,2
	execute		13,term_13_0
functor2_15_13:
	collect_value		22
	collect_value		16
	collect_vector		2
	collect_vector		19
	put_marked_value		2,20
	b_decrement		2,2
	put_marked_value		13,8
	put_variable		16,19
	b_get_print_image		14,13,16,13,14,16
	put_structured_constant		14,'$SCNST_54'
	put_reused_list_val_var		15,15,14,14
	get_integer		12,41
	create_goal		13
	set_marked_value		1,1
	set_value		2,18
	set_variable		3,18
	put_structured_constant		12,'$SCNST_55'
	put_list_val_val		21,12,4
	set_value		4,21
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,4
	set_value		10,10
	set_value		11,16
	set_void		12
	set_value		13,2
	enqueue_goal		13,term_13_0
	create_goal		13
	set_value		1,1
	set_value		2,17
	set_value		3,14
	put_list_val_val		1,13,18
	set_value		4,1
	set_values_inc		5,5,5
	set_value		10,4
	set_integer		11,40
	set_values_inc		12,19,2
	enqueue_goal		13,term_13_0
	put_value		1,11
	put_value		2,3
	put_value		3,15
	execute		3,parenthesis_left_space_3_0
functor2_15_1:
	try_me_else		functor2_15_14
	wait_nil		15
	collect_value		13
	put_value		13,14
	put_integer		14,3
	execute		14,functor3_14_0
functor2_15_14:
	otherwise		functor2_15_0
	try_me_else		functor2_15_35
	wait_list_var_var		15,16,17
	collect_list		15
	collect_value		16
	put_value		15,17
	execute		15,functor2_15_0
functor2_15_35:
	suspend		functor2_15_0
	module_entry		mpimos_unparser
	predicate		functor3,14
functor3_14_0:
	put_marked_value		15,8
	b_get_print_image		13,15,11,11,13,15
	put_structured_constant		13,'$SCNST_56'
	put_list_val_var		15,13,13
	put_list_val_val		16,11,15
	get_list_value		3,16
	get_integer		12,41
	put_integer		3,1
	put_nil		11
	b_set_vector_element		2,3,2,11,3
	create_goal		12
	set_marked_value		1,1
	set_value		2,3
	set_variable		3,12
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_value		8,8
	set_variable		9,11
	set_value		10,10
	set_value		11,14
	set_integer		12,2
	enqueue_goal		12,functor32_12_0
	put_values_dec		3,13,2
	put_value		10,11
	put_integer		11,40
	put_void		12
	put_integer		13,999
	execute		13,term_13_0
functor3_14_1:
	suspend		functor3_14_0
	module_entry		mpimos_unparser
	predicate		functor32,12
functor32_12_0:
	try_me_else		functor32_12_1
	integer		5
	integer		11
	integer		12
	g_less_than		12,11
	try_me_else		functor32_12_5
	g_not_less_than		5,12
	put_marked_value		13,12
	b_increment		13,13
	put_structured_constant		14,'$SCNST_57'
	get_list_val_var		3,15,14,14
	put_nil		3
	b_set_vector_element		2,12,2,3,3
	create_goal		12
	set_marked_value		1,1
	set_value		2,3
	set_variable		3,15
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,12
	set_values_inc		10,10,2
	set_value		12,13
	enqueue_goal		12,functor32_12_0
	put_values_inc		3,14,2
	put_value		10,12
	put_integer		11,44
	put_void		12
	put_integer		13,999
	execute		13,term_13_0
functor32_12_5:
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_58'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
functor32_12_1:
	try_me_else		functor32_12_6
	integer		11
	integer		12
	g_not_less_than		12,11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_59'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
functor32_12_6:
	suspend		functor32_12_0
	module_entry		mpimos_unparser
	predicate		vector,13
vector_13_0:
	try_me_else		vector_13_1
	integer		6
	try_me_else		vector_13_3
	put_integer		14,0
	g_less_than		14,6
	collect_value		11
	b_decrement		6,6
	put_structured_constant		11,'$SCNST_60'
	get_list_val_var		3,14,11,11
	get_integer		12,125
	put_integer		3,0
	put_nil		12
	b_set_vector_element		2,3,2,12,3
	create_goal		12
	set_marked_value		1,1
	set_value		2,3
	set_variable		3,14
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,12
	set_value		10,10
	set_value		11,13
	set_integer		12,1
	enqueue_goal		12,vector0_12_0
	put_value		3,11
	put_value		4,14
	put_value		10,12
	put_integer		11,123
	put_void		12
	put_integer		13,999
	execute		13,term_13_0
vector_13_3:
	collect_value		13
	collect_value		11
	collect_value		8
	collect_value		7
	collect_value		5
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_61'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_integer		12,125
	get_value		9,10
	proceed
vector_13_1:
	suspend		vector_13_0
	module_entry		mpimos_unparser
	predicate		vector0,12
vector0_12_0:
	try_me_else		vector0_12_1
	integer		5
	integer		11
	integer		12
	g_less_than		12,11
	try_me_else		vector0_12_5
	g_not_less_than		5,12
	put_marked_value		13,12
	b_increment		13,13
	put_structured_constant		14,'$SCNST_62'
	get_list_val_var		3,15,14,14
	put_nil		3
	b_set_vector_element		2,12,2,3,3
	create_goal		12
	set_marked_value		1,1
	set_value		2,3
	set_variable		3,15
	set_value		4,4
	set_marked_value		5,5
	set_marked_value		6,6
	set_marked_value		7,7
	set_marked_value		8,8
	set_variable		9,12
	set_values_inc		10,10,2
	set_value		12,13
	enqueue_goal		12,vector0_12_0
	put_values_inc		3,14,2
	put_value		10,12
	put_integer		11,44
	put_void		12
	put_integer		13,999
	execute		13,term_13_0
vector0_12_5:
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_63'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
vector0_12_1:
	try_me_else		vector0_12_6
	integer		11
	integer		12
	g_not_less_than		12,11
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		2
	collect_value		1
	put_structured_constant		1,'$SCNST_64'
	put_list_val_val		2,1,4
	get_list_value		3,2
	get_value		9,10
	proceed
vector0_12_6:
	suspend		vector0_12_0
	module_entry		mpimos_unparser
	predicate		parenthesis_left_space,3
parenthesis_left_space_3_0:
	try_me_else		parenthesis_left_space_3_1
	integer		1
	hash_on_integer		1,5,parenthesis_left_space_3_3
	bucket_entry_i		0,parenthesis_left_space_3_4
	bucket_entry_i		33,parenthesis_left_space_3_5
	bucket_entry_i		44,parenthesis_left_space_3_6
	bucket_entry_i		91,parenthesis_left_space_3_7
	bucket_entry_i		93,parenthesis_left_space_3_8
parenthesis_left_space_3_4:
	get_value		2,3
	proceed
parenthesis_left_space_3_5:
	get_value		2,3
	proceed
parenthesis_left_space_3_6:
	get_value		2,3
	proceed
parenthesis_left_space_3_7:
	get_value		2,3
	proceed
parenthesis_left_space_3_8:
	get_value		2,3
	proceed
parenthesis_left_space_3_3:
	try_me_else		parenthesis_left_space_3_9
	put_integer		4,40
	g_not_less_than		1,4
	put_integer		4,41
	g_not_less_than		4,1
	get_value		2,3
	proceed
parenthesis_left_space_3_9:
	try_me_else		parenthesis_left_space_3_1
	put_integer		4,123
	g_not_less_than		1,4
	put_integer		4,125
	g_not_less_than		4,1
	get_value		2,3
	proceed
parenthesis_left_space_3_1:
	otherwise		parenthesis_left_space_3_0
	collect_value		1
	put_structured_constant		1,'$SCNST_65'
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
parenthesis_left_space_3_14:
	suspend		parenthesis_left_space_3_0
	begin_const_section		mpimos_unparser
'$SCNST_0_0':
	define_desc		19,1
	define_integer		32123
'$SCNST_25':
'$SCNST_2':
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_0':
	define_desc		3,3
	define_integer		1701860132
	define_integer		1818323299
	define_integer		1635017028
'$SCNST_1':
	define_string		'$SCNST_1_0'
'$SCNST_3_0':
	define_desc		11,1
	define_integer		4144959
'$SCNST_3':
	define_string		'$SCNST_3_0'
'$SCNST_4_0':
	define_desc		27,1
	define_integer		41
'$SCNST_59':
'$SCNST_55':
'$SCNST_53':
'$SCNST_51':
'$SCNST_49':
'$SCNST_47':
'$SCNST_45':
'$SCNST_43':
'$SCNST_15':
'$SCNST_12':
'$SCNST_6':
'$SCNST_4':
	define_string		'$SCNST_4_0'
'$SCNST_5_0':
	define_desc		27,1
	define_integer		40
'$SCNST_56':
'$SCNST_54':
'$SCNST_52':
'$SCNST_50':
'$SCNST_48':
'$SCNST_46':
'$SCNST_44':
'$SCNST_42':
'$SCNST_17':
'$SCNST_13':
'$SCNST_7':
'$SCNST_5':
	define_string		'$SCNST_5_0'
'$SCNST_8_0':
	define_desc		27,1
	define_integer		44
'$SCNST_62':
'$SCNST_57':
'$SCNST_37':
'$SCNST_33':
'$SCNST_29':
'$SCNST_16':
'$SCNST_8':
	define_string		'$SCNST_8_0'
'$SCNST_9_0':
	define_desc		3,1
	define_integer		657205024
'$SCNST_10':
'$SCNST_9':
	define_string		'$SCNST_9_0'
'$SCNST_11_0':
	define_desc		11,1
	define_integer		2567207
'$SCNST_11':
	define_string		'$SCNST_11_0'
'$SCNST_14_0':
	define_desc		27,1
	define_integer		95
'$SCNST_18':
'$SCNST_14':
	define_string		'$SCNST_14_0'
'$SCNST_19_0':
	define_desc		27,1
	define_integer		32
'$SCNST_65':
'$SCNST_22':
'$SCNST_21':
'$SCNST_20':
'$SCNST_19':
	define_string		'$SCNST_19_0'
'$SCNST_23_0':
	define_desc		19,1
	define_integer		9001
'$SCNST_23':
	define_string		'$SCNST_23_0'
'$SCNST_24_0':
	define_desc		3,2
	define_integer		1920234272
	define_integer		677867113
'$SCNST_24':
	define_string		'$SCNST_24_0'
'$SCNST_26_0':
	define_desc		27,2
	define_integer		774778491
	define_integer		125
'$SCNST_61':
'$SCNST_26':
	define_string		'$SCNST_26_0'
'$SCNST_27_0':
	define_desc		27,1
	define_integer		123
'$SCNST_60':
'$SCNST_27':
	define_string		'$SCNST_27_0'
'$SCNST_28_0':
	define_desc		27,1
	define_integer		125
'$SCNST_64':
'$SCNST_28':
	define_string		'$SCNST_28_0'
'$SCNST_30_0':
	define_desc		3,1
	define_integer		2100178478
'$SCNST_30':
	define_string		'$SCNST_30_0'
'$SCNST_31_0':
	define_desc		27,1
	define_integer		91
'$SCNST_31':
	define_string		'$SCNST_31_0'
'$SCNST_32_0':
	define_desc		27,2
	define_integer		774778459
	define_integer		93
'$SCNST_32':
	define_string		'$SCNST_32_0'
'$SCNST_34_0':
	define_desc		27,2
	define_integer		774778412
	define_integer		93
'$SCNST_38':
'$SCNST_34':
	define_string		'$SCNST_34_0'
'$SCNST_35_0':
	define_desc		27,1
	define_integer		93
'$SCNST_40':
'$SCNST_36':
'$SCNST_35':
	define_string		'$SCNST_35_0'
'$SCNST_39_0':
	define_desc		27,1
	define_integer		124
'$SCNST_39':
	define_string		'$SCNST_39_0'
'$SCNST_41_0':
	define_desc		27,2
	define_integer		774778408
	define_integer		41
'$SCNST_41':
	define_string		'$SCNST_41_0'
'$SCNST_58_0':
	define_desc		27,2
	define_integer		774778412
	define_integer		41
'$SCNST_58':
	define_string		'$SCNST_58_0'
'$SCNST_63_0':
	define_desc		27,2
	define_integer		774778412
	define_integer		125
'$SCNST_63':
	define_string		'$SCNST_63_0'
