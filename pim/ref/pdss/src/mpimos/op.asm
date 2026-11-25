mpimos_operator_manipulator:
	module		mpimos_operator_manipulator
	entry		create,1,create_1_0
	module_entry		mpimos_operator_manipulator
	predicate		create,1
create_1_0:
	create_goal		2
	set_variable		1,3
	set_variable		2,2
	enqueue_goal		2,op_table_2_0
	create_goal		2
	set_value		1,3
	set_value		2,1
	enqueue_goal		2,init_op_table_2_0
	put_value		1,2
	execute		1,make_op_table_1_0
create_1_1:
	suspend		create_1_0
	module_entry		mpimos_operator_manipulator
	predicate		make_op_table,1
make_op_table_1_0:
	put_value		4,1
	put_integer		1,16
	b_new_vector		3,1
	put_integer		1,0
	put_integer		2,16
	execute		4,set_empty_4_0
make_op_table_1_1:
	suspend		make_op_table_1_0
	module_entry		mpimos_operator_manipulator
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
	module_entry		mpimos_operator_manipulator
	predicate		op_table,2
op_table_2_0:
	try_me_else		op_table_2_1
	jump_on_non_list		1,op_table_2_3
	read_car		1,3
	vector		3
	jump_on_arity		3,6,op_table_2_1
	table_entry		op_table_2_1
	table_entry		op_table_2_1
	table_entry		op_table_2_1
	table_entry		op_table_2_5
	table_entry		op_table_2_1
	table_entry		op_table_2_6
op_table_2_5:
	read_element		3,0,4
	atom		4
	hash_on_atom		4,4,op_table_2_1
	bucket_entry_a		attach_op_type,op_table_2_8
	bucket_entry_a		operator,op_table_2_9
	bucket_entry_a		remove_operator,op_table_2_10
	bucket_entry_a		replace_operator_pool,op_table_2_11
op_table_2_8:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	collect_list		1
	collect_vector		3
	put_value		3,2
	create_goal		2
	set_value		1,5
	set_marked_value		2,3
	enqueue_goal		2,op_table_2_0
	put_values_inc		1,6,2
	execute		3,attach_op_type_3_0
op_table_2_9:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	collect_list		1
	collect_vector		3
	put_value		3,2
	create_goal		2
	set_value		1,5
	set_variable		2,4
	enqueue_goal		2,op_table_2_0
	put_values_inc		1,6,2
	execute		4,list_op_4_0
op_table_2_10:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,3
	enqueue_goal		2,op_table_2_0
	put_value		1,2
	put_value		2,6
	put_value		4,7
	execute		4,remove_operator_all_4_0
op_table_2_11:
	read_cdr		1,5
	read_elements_inc		3,1,6,2
	collect_list		1
	collect_vector		3
	b_merge		1,3
	get_value		1,2
	get_value		3,6
	create_goal		2
	set_value		1,5
	set_variable		2,2
	enqueue_goal		2,op_table_2_0
	create_goal		3
	set_value		1,7
	set_variable		2,1
	set_value		3,2
	enqueue_goal		3,replace_operator_pool_3_0
	execute		1,make_op_table_1_0
op_table_2_6:
	read_element		3,0,4
	atom		4
	branch_on_atom		4,2,op_table_2_1
	bucket_entry_a		add_operator,op_table_2_13
	bucket_entry_a		remove_operator,op_table_2_14
op_table_2_13:
	read_cdr		1,5
	read_elements_inc		3,1,6,4
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,5
	enqueue_goal		2,op_table_2_0
	put_value		1,2
	put_values_dec		2,8,3
	put_value		6,9
	execute		6,add_operator_6_0
op_table_2_14:
	read_cdr		1,5
	read_elements_inc		3,1,6,4
	collect_list		1
	collect_vector		3
	create_goal		2
	set_value		1,5
	set_variable		2,5
	enqueue_goal		2,op_table_2_0
	put_value		1,2
	put_values_dec		2,8,3
	put_value		6,9
	execute		6,remove_operator_6_0
op_table_2_3:
	check_nil		1,op_table_2_1
	collect_value		2
	proceed
op_table_2_1:
	suspend		op_table_2_0
	module_entry		mpimos_operator_manipulator
	predicate		list_op,4
list_op_4_0:
	try_me_else		list_op_4_1
	atom		1
	put_value		5,2
	put_values_inc		2,3,3
	execute		4,search_op_table_4_0
list_op_4_1:
	otherwise		list_op_4_0
	collect_value		1
	get_nil		2
	get_value		4,3
	proceed
list_op_4_5:
	suspend		list_op_4_0
	module_entry		mpimos_operator_manipulator
	predicate		attach_op_type,3
attach_op_type_3_0:
	try_me_else		attach_op_type_3_1
	jump_on_non_list		1,attach_op_type_3_3
	read_car		1,4
	jump_on_non_atom		4,attach_op_type_3_5
	test_atom		4,'|',attach_op_type_3_1
	read_cdr		1,5
	put_func		4,3,atom
	write_element_atom		4,1,'|'
	write_element_variable		4,2,6
	get_reused_list_val_var		2,7,1,4,1
	create_goal		3
	set_value		1,5
	set_value		2,1
	set_variable		3,4
	enqueue_goal		3,attach_op_type_3_0
	put_atom		1,'|'
	put_values_inc		2,3,2
	put_value		4,6
	execute		4,search_op_table_4_0
attach_op_type_3_5:
	check_vector		4,2,attach_op_type_3_1
	read_element		4,0,5
	atom		5
	branch_on_atom		5,3,attach_op_type_3_1
	bucket_entry_a		atom,attach_op_type_3_7
	bucket_entry_a		open,attach_op_type_3_8
	bucket_entry_a		sign,attach_op_type_3_9
attach_op_type_3_7:
	read_cdr		1,6
	read_element		4,1,7
	collect_vector		4
	put_func		4,3,atom
	write_element_marked_value		4,1,7
	write_element_variable		4,2,5
	get_reused_list_val_var		2,8,1,4,1
	create_goal		3
	set_value		1,6
	set_value		2,1
	set_variable		3,4
	enqueue_goal		3,attach_op_type_3_0
	put_value		1,7
	put_values_inc		2,3,3
	execute		4,search_op_table_4_0
attach_op_type_3_8:
	read_cdr		1,6
	read_element		4,1,7
	collect_vector		4
	put_func		4,3,open
	write_element_marked_value		4,1,7
	write_element_variable		4,2,5
	get_reused_list_val_var		2,8,1,4,1
	create_goal		3
	set_value		1,6
	set_value		2,1
	set_variable		3,4
	enqueue_goal		3,attach_op_type_3_0
	put_value		1,7
	put_values_inc		2,3,3
	execute		4,search_op_table_4_0
attach_op_type_3_9:
	read_cdr		1,6
	read_element		4,1,7
	collect_vector		4
	put_func		4,3,sign
	write_element_marked_value		4,1,7
	write_element_variable		4,2,5
	get_reused_list_val_var		2,8,1,4,1
	create_goal		3
	set_value		1,6
	set_value		2,1
	set_variable		3,4
	enqueue_goal		3,attach_op_type_3_0
	put_value		1,7
	put_values_inc		2,3,3
	execute		4,search_op_table_4_0
attach_op_type_3_3:
	check_nil		1,attach_op_type_3_1
	collect_value		3
	get_nil		2
	proceed
attach_op_type_3_1:
	otherwise		attach_op_type_3_0
	try_me_else		attach_op_type_3_21
	wait_list_var_var		1,4,5
	get_reused_list_val_var		2,1,1,4,4
	put_values_dec		1,5,2
	execute		3,attach_op_type_3_0
attach_op_type_3_21:
	suspend		attach_op_type_3_0
	module_entry		mpimos_operator_manipulator
	predicate		search_op_table,4
search_op_table_4_0:
	b_hash		1,1,5
	put_integer		6,15
	b_and		1,6,1
	put_variable		7,6
	b_set_vector_element		2,1,1,7,2
	get_value		2,3
	put_values_dec		2,5,2
	put_value		4,6
	execute		4,search_table_4_0
search_op_table_4_1:
	suspend		search_op_table_4_0
	module_entry		mpimos_operator_manipulator
	predicate		search_table,4
search_table_4_0:
	try_me_else		search_table_4_1
	jump_on_non_list_var_var		1,search_table_4_3,8,5
	wait_vector		8,2
	read_elements_inc		8,0,6,2
	wait_value		6,2
	collect_value		2
	put_marked_value		7,7
	get_value		7,3
	put_reused_vector		2,8
	write_elements_inc		2,0,6,2
	put_reused_list_val_val		1,1,2,5
	get_list_value		4,1
	proceed
search_table_4_3:
	check_nil		1,search_table_4_1
	collect_value		2
	get_nil		4
	get_nil		3
	proceed
search_table_4_1:
	otherwise		search_table_4_0
	try_me_else		search_table_4_8
	wait_list_var_var		1,5,6
	get_reused_list_val_var		4,1,1,5,5
	put_value		1,6
	put_value		4,5
	execute		4,search_table_4_0
search_table_4_8:
	suspend		search_table_4_0
	module_entry		mpimos_operator_manipulator
	predicate		add_operator,6
add_operator_6_0:
	b_hash		2,2,7
	put_integer		8,15
	b_and		2,8,2
	put_variable		9,8
	b_set_vector_element		1,2,1,9,2
	get_value		2,5
	put_value		2,7
	put_value		5,8
	execute		6,search_table_and_add_6_0
add_operator_6_1:
	suspend		add_operator_6_0
	module_entry		mpimos_operator_manipulator
	predicate		search_table_and_add,6
search_table_and_add_6_0:
	try_me_else		search_table_and_add_6_1
	jump_on_non_list_var_var		1,search_table_and_add_6_3,10,7
	wait_vector		10,2
	read_elements_inc		10,0,8,2
	wait_value		8,2
	collect_value		2
	put_reused_vector		2,10
	write_element_value		2,0,8
	write_element_variable		2,1,8
	put_reused_list_val_val		1,1,2,7
	get_list_value		5,1
	put_value		1,9
	put_values_inc		2,3,2
	put_value		4,8
	put_value		5,6
	execute		5,check_op_defs_5_0
search_table_and_add_6_3:
	check_nil		1,search_table_and_add_6_1
	put_vector		1,2
	write_element_value		1,0,2
	write_element_variable		1,1,2
	put_list		7
	write_car_value		7,1
	write_cdr_nil		7
	get_list_value		5,7
	put_vector		1,2
	write_elements_dec		1,0,4,2
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	get_atom		6,success
	proceed
search_table_and_add_6_1:
	otherwise		search_table_and_add_6_0
	try_me_else		search_table_and_add_6_8
	wait_list_var_var		1,7,8
	get_reused_list_val_var		5,1,1,7,7
	put_value		1,8
	put_value		5,7
	execute		6,search_table_and_add_6_0
search_table_and_add_6_8:
	suspend		search_table_and_add_6_0
	module_entry		mpimos_operator_manipulator
	predicate		check_op_defs,5
check_op_defs_5_0:
	try_me_else		check_op_defs_5_1
	jump_on_non_list_var_var		1,check_op_defs_5_3,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	wait_value		8,2
	wait_value		7,3
	collect_value		3
	put_reused_vector		2,9
	write_elements_inc		2,0,7,2
	put_reused_list_val_val		1,1,2,6
	get_list_value		4,1
	get_atom		5,already_exist
	proceed
check_op_defs_5_3:
	check_nil		1,check_op_defs_5_1
	put_vector		1,2
	write_elements_dec		1,0,3,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		4,2
	get_atom		5,success
	proceed
check_op_defs_5_1:
	otherwise		check_op_defs_5_0
	try_me_else		check_op_defs_5_8
	wait_list_var_var		1,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	collect_list		1
	create_goal		7
	set_value		1,6
	set_marked_value		2,2
	set_values_inc		3,3,3
	put_reused_vector		1,9
	write_element_value		1,0,7
	write_element_marked_value		1,1,8
	set_value		6,1
	set_variable		7,3
	enqueue_goal		7,replace_op_defs_7_0
	put_value		1,8
	execute		3,coexist_3_0
check_op_defs_5_8:
	suspend		check_op_defs_5_0
	module_entry		mpimos_operator_manipulator
	predicate		replace_op_defs,7
replace_op_defs_7_0:
	try_me_else		replace_op_defs_7_1
	atom		7
	branch_on_atom		7,2,replace_op_defs_7_1
	bucket_entry_a		no,replace_op_defs_7_3
	bucket_entry_a		yes,replace_op_defs_7_4
replace_op_defs_7_3:
	collect_value		6
	put_vector		6,2
	write_elements_dec		6,0,3,2
	put_list_val_val		2,6,1
	get_list_value		4,2
	get_atom		5,success
	proceed
replace_op_defs_7_4:
	get_list_val_var		4,7,6,6
	put_value		4,6
	execute		5,check_op_defs_5_0
replace_op_defs_7_1:
	suspend		replace_op_defs_7_0
	module_entry		mpimos_operator_manipulator
	predicate		remove_operator,6
remove_operator_6_0:
	b_hash		2,2,7
	put_integer		8,15
	b_and		2,8,2
	put_variable		9,8
	b_set_vector_element		1,2,1,9,2
	get_value		2,5
	put_value		2,7
	put_value		5,8
	execute		6,search_table_and_remove_6_0
remove_operator_6_1:
	suspend		remove_operator_6_0
	module_entry		mpimos_operator_manipulator
	predicate		search_table_and_remove,6
search_table_and_remove_6_0:
	try_me_else		search_table_and_remove_6_1
	jump_on_non_list_var_var		1,search_table_and_remove_6_3,10,7
	wait_vector		10,2
	read_elements_inc		10,0,8,2
	wait_value		8,2
	collect_value		2
	put_reused_vector		2,10
	write_element_marked_value		2,0,8
	write_element_variable		2,1,10
	put_reused_list_val_val		1,1,2,7
	get_list_value		5,1
	create_goal		5
	set_variable		1,5
	set_value		2,8
	set_marked_value		3,3
	set_marked_value		4,4
	set_value		5,6
	enqueue_goal		5,remove_result_5_0
	put_value		1,9
	put_values_inc		2,3,2
	put_value		4,10
	execute		5,check_op_defs_and_remove_5_0
search_table_and_remove_6_3:
	check_nil		1,search_table_and_remove_6_1
	get_nil		5
	put_func		1,4,not_find
	write_elements_dec		1,1,4,3
	get_vector_value		6,1
	proceed
search_table_and_remove_6_1:
	otherwise		search_table_and_remove_6_0
	try_me_else		search_table_and_remove_6_8
	wait_list_var_var		1,7,8
	get_reused_list_val_var		5,1,1,7,7
	put_value		1,8
	put_value		5,7
	execute		6,search_table_and_remove_6_0
search_table_and_remove_6_8:
	suspend		search_table_and_remove_6_0
	module_entry		mpimos_operator_manipulator
	predicate		remove_result,5
remove_result_5_0:
	try_me_else		remove_result_5_1
	wait_atom		1,not_find
	put_func		1,4,not_find
	write_elements_dec		1,1,4,3
	get_vector_value		5,1
	proceed
remove_result_5_1:
	otherwise		remove_result_5_0
	collect_value		4
	collect_value		3
	collect_value		2
	collect_value		1
	get_atom		5,success
	proceed
remove_result_5_6:
	suspend		remove_result_5_0
	module_entry		mpimos_operator_manipulator
	predicate		check_op_defs_and_remove,5
check_op_defs_and_remove_5_0:
	try_me_else		check_op_defs_and_remove_5_1
	jump_on_non_list_var_var		1,check_op_defs_and_remove_5_3,9,6
	wait_vector		9,2
	read_elements_inc		9,0,7,2
	wait_value		8,2
	wait_value		7,3
	collect_list		1
	collect_value		7
	collect_value		8
	collect_value		3
	collect_vector		9
	get_value		4,6
	get_atom		5,success
	proceed
check_op_defs_and_remove_5_3:
	check_nil		1,check_op_defs_and_remove_5_1
	collect_value		3
	collect_value		2
	get_nil		4
	get_atom		5,not_find
	proceed
check_op_defs_and_remove_5_1:
	otherwise		check_op_defs_and_remove_5_0
	try_me_else		check_op_defs_and_remove_5_8
	wait_list_var_var		1,6,7
	get_reused_list_val_var		4,1,1,6,6
	put_value		1,7
	put_value		4,6
	execute		5,check_op_defs_and_remove_5_0
check_op_defs_and_remove_5_8:
	suspend		check_op_defs_and_remove_5_0
	module_entry		mpimos_operator_manipulator
	predicate		remove_operator_all,4
remove_operator_all_4_0:
	b_hash		2,2,5
	put_integer		6,15
	b_and		2,6,2
	put_variable		7,6
	b_set_vector_element		1,2,1,7,2
	get_value		2,3
	put_values_inc		2,5,2
	execute		4,search_table_and_remove_all_4_0
remove_operator_all_4_1:
	suspend		remove_operator_all_4_0
	module_entry		mpimos_operator_manipulator
	predicate		search_table_and_remove_all,4
search_table_and_remove_all_4_0:
	try_me_else		search_table_and_remove_all_4_1
	jump_on_non_list_var_var		1,search_table_and_remove_all_4_3,8,5
	wait_vector		8,2
	read_elements_inc		8,0,6,2
	wait_value		6,2
	collect_list		1
	collect_value		6
	collect_value		7
	collect_value		2
	collect_vector		8
	get_value		3,5
	get_atom		4,success
	proceed
search_table_and_remove_all_4_3:
	check_nil		1,search_table_and_remove_all_4_1
	get_nil		3
	put_func		1,2,not_find
	write_element_value		1,1,2
	get_vector_value		4,1
	proceed
search_table_and_remove_all_4_1:
	otherwise		search_table_and_remove_all_4_0
	try_me_else		search_table_and_remove_all_4_8
	wait_list_var_var		1,5,6
	get_reused_list_val_var		3,1,1,5,5
	put_value		1,6
	put_value		3,5
	execute		4,search_table_and_remove_all_4_0
search_table_and_remove_all_4_8:
	suspend		search_table_and_remove_all_4_0
	module_entry		mpimos_operator_manipulator
	predicate		replace_operator_pool,3
replace_operator_pool_3_0:
	try_me_else		replace_operator_pool_3_1
	jump_on_non_list_var_var		1,replace_operator_pool_3_3,7,4
	wait_vector		7,2
	read_elements_inc		7,0,5,2
	collect_list		1
	collect_vector		7
	b_hash		5,1,5
	put_integer		7,15
	b_and		1,7,1
	put_variable		7,8
	b_set_vector_element		2,1,7,7,1
	create_goal		3
	set_value		1,4
	set_value		2,1
	set_value		3,3
	enqueue_goal		3,replace_operator_pool_3_0
	put_values_inc		1,5,4
	execute		4,add_operator_defs_4_0
replace_operator_pool_3_3:
	check_nil		1,replace_operator_pool_3_1
	get_value		3,2
	proceed
replace_operator_pool_3_1:
	suspend		replace_operator_pool_3_0
	module_entry		mpimos_operator_manipulator
	predicate		add_operator_defs,4
add_operator_defs_4_0:
	try_me_else		add_operator_defs_4_1
	jump_on_non_list_var_var		2,add_operator_defs_4_3,8,5
	wait_vector		8,2
	read_elements_inc		8,0,6,2
	collect_list		2
	collect_vector		8
	put_value		2,1
	create_goal		4
	set_marked_value		1,2
	set_value		2,5
	set_variable		3,5
	set_value		4,4
	enqueue_goal		4,add_operator_defs_4_0
	put_value		1,3
	put_values_dec		3,7,2
	put_void		6
	execute		6,search_table_and_add_6_0
add_operator_defs_4_3:
	check_nil		2,add_operator_defs_4_1
	collect_value		1
	get_value		4,3
	proceed
add_operator_defs_4_1:
	suspend		add_operator_defs_4_0
	module_entry		mpimos_operator_manipulator
	predicate		coexist,3
coexist_3_0:
	try_me_else		coexist_3_1
	atom		1
	hash_on_atom		1,7,coexist_3_1
	bucket_entry_a		fx,coexist_3_3
	bucket_entry_a		fy,coexist_3_4
	bucket_entry_a		xf,coexist_3_5
	bucket_entry_a		xfx,coexist_3_6
	bucket_entry_a		xfy,coexist_3_7
	bucket_entry_a		yf,coexist_3_8
	bucket_entry_a		yfx,coexist_3_9
coexist_3_3:
	wait_atom		2,fy
	get_atom		3,no
	proceed
coexist_3_4:
	wait_atom		2,fx
	get_atom		3,no
	proceed
coexist_3_5:
	wait_atom		2,yf
	get_atom		3,no
	proceed
coexist_3_6:
	atom		2
	branch_on_atom		2,2,coexist_3_1
	bucket_entry_a		xfy,coexist_3_11
	bucket_entry_a		yfx,coexist_3_12
coexist_3_11:
	get_atom		3,no
	proceed
coexist_3_12:
	get_atom		3,no
	proceed
coexist_3_7:
	atom		2
	branch_on_atom		2,2,coexist_3_1
	bucket_entry_a		xfx,coexist_3_14
	bucket_entry_a		yfx,coexist_3_15
coexist_3_14:
	get_atom		3,no
	proceed
coexist_3_15:
	get_atom		3,no
	proceed
coexist_3_8:
	wait_atom		2,xf
	get_atom		3,no
	proceed
coexist_3_9:
	atom		2
	branch_on_atom		2,2,coexist_3_1
	bucket_entry_a		xfx,coexist_3_17
	bucket_entry_a		xfy,coexist_3_18
coexist_3_17:
	get_atom		3,no
	proceed
coexist_3_18:
	get_atom		3,no
	proceed
coexist_3_1:
	try_me_else		coexist_3_19
	wait_value		1,2
	collect_value		1
	collect_value		2
	get_atom		3,no
	proceed
coexist_3_19:
	otherwise		coexist_3_0
	collect_value		2
	collect_value		1
	get_atom		3,yes
	proceed
coexist_3_25:
	suspend		coexist_3_0
	module_entry		mpimos_operator_manipulator
	predicate		init_op_table,2
init_op_table_2_0:
	put_func		3,5,add_operator
	write_element_integer		3,1,80
	write_element_atom		3,2,fx
	write_element_atom		3,3,module
	write_element_void		3,4
	put_list_val_val		4,3,2
	put_func		2,5,add_operator
	write_element_integer		2,1,90
	write_element_atom		2,2,xfx
	write_element_atom		2,3,::
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,100
	write_element_atom		2,2,fx
	write_element_atom		2,3,#
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,100
	write_element_atom		2,2,xfx
	write_element_atom		2,3,#
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,150
	write_element_atom		2,2,xf
	write_element_atom		2,3,--
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,150
	write_element_atom		2,2,xf
	write_element_atom		2,3,++
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,200
	write_element_atom		2,2,fx
	write_element_atom		2,3,&
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,300
	write_element_atom		2,2,xfy
	write_element_atom		2,3,**
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,300
	write_element_atom		2,2,xfx
	write_element_atom		2,3,mod
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,400
	write_element_atom		2,2,yfx
	write_element_atom		2,3,>>
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,400
	write_element_atom		2,2,yfx
	write_element_atom		2,3,<<
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,400
	write_element_atom		2,2,yfx
	write_element_atom		2,3,/
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,400
	write_element_atom		2,2,yfx
	write_element_atom		2,3,*
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,yfx
	write_element_atom		2,3,xor
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,yfx
	write_element_atom		2,3,\/
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,yfx
	write_element_atom		2,3,/\
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,fx
	write_element_atom		2,3,-
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,yfx
	write_element_atom		2,3,-
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,fx
	write_element_atom		2,3,+
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,500
	write_element_atom		2,2,yfx
	write_element_atom		2,3,+
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfy
	write_element_atom		2,3,@
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$>=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$>
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$=<
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$<
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$=\=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$=:=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$<=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,$:=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,<<=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,<=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,:=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,>=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,=<
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,>
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,<
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,==
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,=:=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,=\=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,\=
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,700
	write_element_atom		2,2,xfx
	write_element_atom		2,3,=
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,800
	write_element_atom		2,2,xfx
	write_element_atom		2,3,:
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1000
	write_element_atom		2,2,xfy
	write_element_atom		2,3,','
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1050
	write_element_atom		2,2,xfy
	write_element_atom		2,3,->
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1090
	write_element_atom		2,2,xfx
	write_element_atom		2,3,=>
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1100
	write_element_atom		2,2,xfy
	write_element_atom		2,3,'|'
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1100
	write_element_atom		2,2,xfy
	write_element_atom		2,3,;
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1150
	write_element_atom		2,2,fx
	write_element_atom		2,3,user_macro
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1150
	write_element_atom		2,2,fx
	write_element_atom		2,3,with_macro
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1150
	write_element_atom		2,2,fx
	write_element_atom		2,3,local_implicit
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1150
	write_element_atom		2,2,fx
	write_element_atom		2,3,implicit
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1150
	write_element_atom		2,2,fx
	write_element_atom		2,3,public
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1200
	write_element_atom		2,2,xfx
	write_element_atom		2,3,-->
	write_element_void		2,4
	put_list_val_val		4,2,3
	put_func		2,5,add_operator
	write_element_integer		2,1,1200
	write_element_atom		2,2,fx
	write_element_atom		2,3,:-
	write_element_void		2,4
	put_list_val_val		3,2,4
	put_func		2,5,add_operator
	write_element_integer		2,1,1200
	write_element_atom		2,2,xfx
	write_element_atom		2,3,:-
	write_element_void		2,4
	put_list_val_val		4,2,3
	get_list_value		1,4
	proceed
init_op_table_2_1:
	suspend		init_op_table_2_0
