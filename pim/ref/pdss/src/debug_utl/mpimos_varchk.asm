mpimos_varchk:
	module		mpimos_varchk
	entry		go,2,go_2_0
	entry		go,3,go_3_0
	entry		go_f,3,go_f_3_0
	entry		start,4,start_4_0
	entry		go_p,3,go_p_3_0
	module_entry		mpimos_varchk
	predicate		go,2
go_2_0:
	create_goal		4
	set_value		1,1
	set_variable		2,3
	put_func		1,2,getl
	write_element_void		1,1
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	set_value		3,4
	set_value		4,2
	enqueue_goal		4,start_4_0
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	put_structured_constant		2,'$SCNST_0'
	execute_external		mpimos_window,create,2
go_2_1:
	suspend		go_2_0
	module_entry		mpimos_varchk
	predicate		go,3
go_3_0:
	create_goal		4
	set_value		1,1
	set_variable		2,4
	put_func		1,2,getl
	write_element_void		1,1
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	set_value		3,5
	set_value		4,3
	enqueue_goal		4,start_4_0
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,4
	execute_external		mpimos_window,create,2
go_3_1:
	suspend		go_3_0
	module_entry		mpimos_varchk
	predicate		go_f,3
go_f_3_0:
	create_goal		4
	set_value		1,1
	set_variable		2,1
	set_nil		3
	set_value		4,3
	enqueue_goal		4,start_4_0
	put_atom		3,w
	execute_external		mpimos_file,create,3
go_f_3_1:
	suspend		go_f_3_0
	module_entry		mpimos_varchk
	predicate		go_p,3
go_p_3_0:
	create_goal		4
	set_value		1,1
	set_variable		2,4
	put_func		1,2,getl
	write_element_void		1,1
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	set_value		3,5
	set_value		4,3
	enqueue_goal		4,start_4_0
	create_goal		2
	set_value		1,4
	set_variable		2,3
	enqueue_goal_external		mpimos_pretty_printer,pprinter,2
	put_list		1
	write_car_atom		1,show
	write_cdr_value		1,3
	execute_external		mpimos_window,create,2
go_p_3_1:
	suspend		go_p_3_0
	module_entry		mpimos_varchk
	predicate		start,4
start_4_0:
	try_me_else		start_4_1
	atom		4
	put_value		8,1
	put_list		1
	write_car_atom		1,nl
	write_cdr_variable		1,7
	put_func		5,2,putt
	write_element_marked_value		5,1,8
	put_list_val_val		6,5,1
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		5,1,6
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		6,1,5
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		5,1,6
	get_list_value		2,5
	b_merge		5,9
	put_vector		6,2
	write_element_variable		6,0,2
	write_element_variable		6,1,1
	get_vector_value		5,6
	get_value		9,7
	create_goal		4
	set_variable		1,5
	set_value		2,1
	set_values_inc		3,3,2
	enqueue_goal		4,loop_4_0
	create_goal		5
	set_variable		1,1
	set_nil		2
	set_variable		3,3
	set_nil		4
	set_value		5,5
	enqueue_goal_external		kl1cmp_reader,create_varchk_reader,5
	create_goal		3
	set_value		1,2
	set_nil		2
	set_value		3,3
	enqueue_goal_external		kl1cmp_reader,trans_io_instr,3
	put_value		2,8
	put_atom		3,r
	execute_external		mpimos_file,create,3
start_4_1:
	suspend		start_4_0
	module_entry		mpimos_varchk
	predicate		loop,4
loop_4_0:
	put_func		5,3,read_predicate
	write_element_variable		5,1,7
	write_element_variable		5,2,6
	get_list_val_var		1,8,5,5
	put_value		1,5
	put_value		5,7
	execute		6,loop0_6_0
loop_4_1:
	suspend		loop_4_0
	module_entry		mpimos_varchk
	predicate		loop0,6
loop0_6_0:
	try_me_else		loop0_6_1
	atom		6
	branch_on_atom		6,2,loop0_6_1
	bucket_entry_a		directive,loop0_6_3
	bucket_entry_a		end_of_file,loop0_6_4
loop0_6_3:
	execute		5,check_directives_5_0
loop0_6_4:
	collect_value		5
	collect_value		4
	get_nil		1
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		4,1,3
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,1
	get_list_value		2,3
	proceed
loop0_6_1:
	otherwise		loop0_6_0
	collect_value		6
	execute		5,loop1_5_0
loop0_6_7:
	suspend		loop0_6_0
	module_entry		mpimos_varchk
	predicate		check_directives,5
check_directives_5_0:
	try_me_else		check_directives_5_1
	jump_on_non_list_var_var		5,check_directives_5_3,10,6
	wait_vector		10,2
	read_element		10,0,7
	wait_atom		7,:-
	read_element		10,1,11
	wait_vector		11,4
	read_element		11,0,7
	wait_atom		7,op
	read_elements_inc		11,1,7,3
	integer		7
	put_integer		12,1
	g_not_less_than		7,12
	put_integer		12,1200
	g_not_less_than		12,7
	atom		8
	atom		9
	collect_vector		10
	put_reused_func		10,11,add_op
	write_elements_inc		10,1,7,3
	get_reused_list_val_var		2,7,5,10,5
	put_value		2,5
	put_value		5,6
	execute		5,check_directives_5_0
check_directives_5_3:
	check_nil		5,check_directives_5_1
	execute		4,loop_4_0
check_directives_5_1:
	otherwise		check_directives_5_0
	try_me_else		check_directives_5_8
	wait_list_var_var		5,6,7
	collect_list		5
	collect_value		6
	put_value		5,7
	execute		5,check_directives_5_0
check_directives_5_8:
	suspend		check_directives_5_0
	module_entry		mpimos_varchk
	predicate		loop1,5
loop1_5_0:
	try_me_else		loop1_5_1
	jump_on_non_list		5,loop1_5_3
	read_car		5,6
	jump_on_non_list		6,loop1_5_5
	read_cdr		5,7
	collect_list		5
	put_value		5,7
	put_atom		7,done
	execute		7,loop2_7_0
loop1_5_5:
	is_atom		6,loop1_5_1
	branch_on_atom		6,2,loop1_5_1
	bucket_entry_a		alternatively,loop1_5_6
	bucket_entry_a		otherwise,loop1_5_7
loop1_5_6:
	read_cdr		5,7
	collect_list		5
	put_value		5,7
	execute		5,loop1_5_0
loop1_5_7:
	read_cdr		5,7
	collect_list		5
	put_value		5,7
	execute		5,loop1_5_0
loop1_5_3:
	check_nil		5,loop1_5_1
	execute		4,loop_4_0
loop1_5_1:
	suspend		loop1_5_0
	module_entry		mpimos_varchk
	predicate		loop2,7
loop2_7_0:
	try_me_else		loop2_7_1
	jump_on_non_list_var_var		6,loop2_7_3,11,8
	wait_vector		11,3
	read_element		11,0,9
	wait_atom		9,+
	read_elements_inc		11,1,9,2
	wait_atom		7,done
	collect_vector		11
	put_value		7,2
	create_goal		7
	set_value		1,1
	set_variable		2,2
	set_value		3,3
	set_marked_value		4,4
	set_value		5,5
	set_value		6,8
	set_variable		7,3
	enqueue_goal		7,loop2_7_0
	put_func		1,2,flush
	write_element_value		1,1,3
	put_reused_list_val_val		5,6,1,2
	put_values_inc		1,9,2
	put_value		3,4
	put_value		4,7
	execute		5,varchk_5_0
loop2_7_3:
	check_nil		6,loop2_7_1
	collect_value		7
	execute		5,loop1_5_0
loop2_7_1:
	otherwise		loop2_7_0
	try_me_else		loop2_7_8
	wait_list_var_var		6,8,9
	wait_atom		7,done
	create_goal		7
	set_value		1,1
	set_variable		2,7
	set_value		3,3
	set_marked_value		4,4
	set_value		5,5
	set_value		6,9
	set_variable		7,5
	enqueue_goal		7,loop2_7_0
	create_goal		5
	set_marked_value		1,8
	set_variable		2,3
	set_value		3,4
	set_value		4,2
	put_func		1,2,flush
	write_element_value		1,1,5
	put_reused_list_val_val		2,6,1,7
	set_value		5,2
	enqueue_goal		5,varchk_5_0
	put_value		1,8
	put_integer		2,0
	execute_external		kl1cmp_reader,count_variables,3
loop2_7_8:
	suspend		loop2_7_0
	module_entry		mpimos_varchk
	predicate		varchk,5
varchk_5_0:
	create_goal		4
	set_variable		1,8
	set_marked_value		2,1
	set_value		3,4
	set_variable		4,4
	enqueue_goal		4,varchk2_4_0
	create_goal		9
	set_values_inc		1,4,2
	set_integer		3,0
	set_marked_value		4,2
	set_variable		5,7
	set_variable		6,6
	set_variable		7,5
	set_marked_variable		8,4
	set_value		9,8
	enqueue_goal		9,varchk3_9_0
	create_goal		6
	set_values_inc		1,1,2
	set_value		3,4
	set_values_dec		4,7,3
	enqueue_goal		6,make_tbl_6_0
	put_values_inc		1,3,2
	execute		2,option_2_0
varchk_5_1:
	suspend		varchk_5_0
	module_entry		mpimos_varchk
	predicate		varchk2,4
varchk2_4_0:
	try_me_else		varchk2_4_1
	integer		1
	test_integer		1,0,varchk2_4_3
	collect_value		2
	get_value		3,4
	proceed
varchk2_4_3:
	put_integer		5,0
	g_less_than		5,1
	put_structured_constant		1,'$SCNST_5'
	put_list_val_val		5,1,4
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,5
	put_list		4
	write_car_atom		4,nl
	write_cdr_value		4,1
	put_structured_constant		1,'$SCNST_6'
	put_list_val_val		5,1,4
	put_func		1,2,puttq
	write_element_value		1,1,2
	put_list_val_val		2,1,5
	put_structured_constant		1,'$SCNST_7'
	put_list_val_val		4,1,2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,1
	get_list_value		3,2
	proceed
varchk2_4_1:
	suspend		varchk2_4_0
	module_entry		mpimos_varchk
	predicate		varchk3,9
varchk3_9_0:
	try_me_else		varchk3_9_1
	integer		3
	integer		4
	try_me_else		varchk3_9_4
	g_less_than		3,4
	put_marked_value		10,3
	b_string_element		5,10,5,10
	b_string_element		6,3,6,11
	create_goal		10
	set_variable		1,12
	set_values_inc		2,1,4
	set_values_inc		6,10,2
	set_value		8,7
	set_marked_value		9,8
	set_value		10,9
	enqueue_goal		10,wait_check_10_0
	put_values_inc		1,5,2
	put_value		3,8
	put_value		4,12
	execute		4,check_4_0
varchk3_9_4:
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	get_value		1,2
	get_integer		9,0
	proceed
varchk3_9_1:
	suspend		varchk3_9_0
	module_entry		mpimos_varchk
	predicate		wait_check,10
wait_check_10_0:
	try_me_else		wait_check_10_1
	wait_atom		1,on
	put_marked_value		1,4
	b_vector_element		8,1,1,8
	put_structured_constant		11,'$SCNST_8'
	put_list_val_var		12,11,13
	put_func		11,2,putb
	write_element_value		11,1,1
	put_list_val_val		1,11,12
	get_list_value		2,1
	b_increment		4,1
	put_value		4,1
	put_variable		1,11
	b_increment		1,1
	get_value		10,1
	put_value		1,13
	put_values_inc		2,3,7
	put_value		9,11
	execute		9,varchk3_9_0
wait_check_10_1:
	otherwise		wait_check_10_0
	collect_value		1
	b_increment		4,1
	put_value		4,1
	put_values_inc		1,2,9
	execute		9,varchk3_9_0
wait_check_10_6:
	suspend		wait_check_10_0
	module_entry		mpimos_varchk
	predicate		count,5
count_5_0:
	try_me_else		count_5_1
	jump_on_non_list_var_var		1,count_5_3,6,7
	collect_list		1
	create_goal		5
	set_value		1,7
	set_variable		2,8
	set_value		3,3
	set_variable		4,7
	set_value		5,5
	enqueue_goal		5,count_5_0
	put_value		1,6
	put_value		3,8
	put_value		5,7
	execute		5,count_5_0
count_5_3:
	check_vector		1,3,count_5_1
	read_element		1,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		1,1,6,2
	put_structured_constant		8,'$SCNST_9'
	wait		8
	wait_value		7,8
	integer		6
	put_integer		9,0
	g_not_less_than		6,9
	collect_value		7
	collect_value		8
	collect_vector		1
	get_value		4,5
	get_value		2,3
	proceed
count_5_1:
	otherwise		count_5_0
	try_me_else		count_5_8
	wait_vector		1,3
	read_element		1,0,6
	wait_atom		6,'$VAR'
	read_elements_inc		1,1,6,2
	integer		6
	put_integer		8,0
	g_not_less_than		6,8
	string		7
	g_string		7,8,9
	wait_integer		9,8
	string		2
	g_string_element		2,6,8
	collect_vector		1
	b_increment		8,1
	put_marked_value		8,6
	b_set_vector_element		4,8,4,7,7
	get_value		7,5
	b_set_string_element		2,6,1,1
	get_value		1,3
	proceed
count_5_8:
	otherwise		count_5_0
	try_me_else		count_5_13
	vector		1
	g_vector		1,7
	put_integer		6,0
	execute		7,count_vector_7_0
count_5_13:
	otherwise		count_5_0
	collect_value		1
	get_value		4,5
	get_value		2,3
	proceed
count_5_17:
	suspend		count_5_0
	module_entry		mpimos_varchk
	predicate		count_vector,7
count_vector_7_0:
	try_me_else		count_vector_7_1
	integer		6
	integer		7
	try_me_else		count_vector_7_4
	g_less_than		6,7
	put_marked_value		8,6
	put_nil		9
	b_set_vector_element		1,8,1,9,8
	b_increment		6,6
	create_goal		7
	set_value		1,8
	set_variable		2,9
	set_value		3,3
	set_variable		4,8
	set_values_inc		5,5,3
	enqueue_goal		7,count_vector_7_0
	put_value		3,9
	put_value		5,8
	execute		5,count_5_0
count_vector_7_4:
	collect_value		1
	get_value		4,5
	get_value		2,3
	proceed
count_vector_7_1:
	suspend		count_vector_7_0
	module_entry		mpimos_varchk
	predicate		count_goals,8
count_goals_8_0:
	try_me_else		count_goals_8_1
	vector		1
	jump_on_arity		1,6,count_goals_8_1
	table_entry		count_goals_8_1
	table_entry		count_goals_8_1
	table_entry		count_goals_8_1
	table_entry		count_goals_8_3
	table_entry		count_goals_8_4
	table_entry		count_goals_8_5
count_goals_8_3:
	read_element		1,0,9
	wait_atom		9,','
	read_elements_inc		1,1,9,2
	collect_vector		1
	create_goal		8
	set_value		1,10
	set_variable		2,12
	set_value		3,3
	set_variable		4,11
	set_value		5,5
	set_variable		6,10
	set_value		7,7
	set_marked_value		8,8
	enqueue_goal		8,count_goals_8_0
	put_value		1,9
	put_value		3,12
	put_value		5,11
	put_value		7,10
	execute		8,count_goals_8_0
count_goals_8_4:
	read_element		1,0,9
	wait_atom		9,vector_element
	read_element		1,1,13
	read_elements_inc		1,2,9,2
	wait_vector		13,3
	read_element		13,0,11
	wait_atom		11,'$VAR'
	read_elements_inc		13,1,11,2
	wait_atom		8,guard
	integer		11
	put_integer		14,0
	g_not_less_than		11,14
	collect_vector		1
	put_vector		1,2
	write_element_marked_value		1,0,11
	write_element_variable		1,1,8
	put_list_val_val		14,1,7
	get_list_value		6,14
	create_goal		7
	set_value		1,8
	set_nil		2
	set_value		3,10
	set_variable		4,6
	set_value		5,3
	set_variable		6,1
	set_value		7,5
	enqueue_goal		7,count_mrb_7_0
	create_goal		5
	set_value		1,9
	set_variable		2,3
	set_value		3,6
	set_variable		4,5
	set_value		5,1
	enqueue_goal		5,count_5_0
	put_reused_func		1,13,'$VAR'
	write_elements_inc		1,1,11,2
	execute		5,count_5_0
count_goals_8_5:
	read_element		1,0,9
	wait_atom		9,vector_element
	read_elements_inc		1,1,9,4
	wait_atom		8,body
	collect_vector		1
	create_goal		5
	set_value		1,12
	set_variable		2,1
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	enqueue_goal		5,count_5_0
	create_goal		7
	set_values_inc		1,6,2
	set_value		3,11
	set_variable		4,5
	set_value		5,1
	set_variable		6,1
	set_value		7,3
	enqueue_goal		7,count_mrb_7_0
	create_goal		5
	set_value		1,10
	set_variable		2,3
	set_value		3,5
	set_variable		4,5
	set_value		5,1
	enqueue_goal		5,count_5_0
	put_value		1,9
	execute		5,count_5_0
count_goals_8_1:
	otherwise		count_goals_8_0
	collect_value		8
	get_value		6,7
	execute		5,count_5_0
count_goals_8_8:
	suspend		count_goals_8_0
	module_entry		mpimos_varchk
	predicate		count_mrb,7
count_mrb_7_0:
	try_me_else		count_mrb_7_1
	jump_on_non_list_var_var		3,count_mrb_7_3,8,9
	collect_list		3
	create_goal		7
	set_variable		1,3
	set_value		2,2
	set_value		3,9
	set_variable		4,10
	set_value		5,5
	set_variable		6,9
	set_value		7,7
	enqueue_goal		7,count_mrb_7_0
	put_value		2,3
	put_value		3,8
	put_value		5,10
	put_value		7,9
	execute		7,count_mrb_7_0
count_mrb_7_3:
	check_vector		3,3,count_mrb_7_1
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	put_structured_constant		10,'$SCNST_10'
	wait		10
	wait_value		9,10
	integer		8
	put_integer		11,0
	g_not_less_than		8,11
	collect_value		9
	collect_value		10
	collect_vector		3
	get_value		1,2
	get_value		6,7
	get_value		4,5
	proceed
count_mrb_7_1:
	otherwise		count_mrb_7_0
	try_me_else		count_mrb_7_8
	wait_vector		3,3
	read_element		3,0,8
	wait_atom		8,'$VAR'
	read_elements_inc		3,1,8,2
	integer		8
	put_integer		10,0
	g_not_less_than		8,10
	string		9
	g_string		9,10,11
	wait_integer		11,8
	string		4
	g_string_element		4,8,10
	collect_vector		3
	b_increment		10,3
	put_marked_value		10,8
	b_set_vector_element		6,10,6,9,9
	get_value		9,7
	b_set_string_element		4,8,3,3
	get_value		3,5
	put_list_val_val		3,8,2
	get_list_value		1,3
	proceed
count_mrb_7_8:
	otherwise		count_mrb_7_0
	try_me_else		count_mrb_7_13
	vector		3
	g_vector		3,9
	put_integer		8,0
	execute		9,count_mrb_vector_9_0
count_mrb_7_13:
	otherwise		count_mrb_7_0
	collect_value		3
	get_value		1,2
	get_value		6,7
	get_value		4,5
	proceed
count_mrb_7_17:
	suspend		count_mrb_7_0
	module_entry		mpimos_varchk
	predicate		count_mrb_vector,9
count_mrb_vector_9_0:
	try_me_else		count_mrb_vector_9_1
	integer		8
	integer		9
	try_me_else		count_mrb_vector_9_4
	g_less_than		8,9
	put_marked_value		10,8
	put_nil		11
	b_set_vector_element		3,10,3,11,10
	b_increment		8,8
	create_goal		9
	set_variable		1,12
	set_value		2,2
	set_value		3,10
	set_variable		4,11
	set_value		5,5
	set_variable		6,10
	set_values_inc		7,7,3
	enqueue_goal		9,count_mrb_vector_9_0
	put_value		2,12
	put_value		5,11
	put_value		7,10
	execute		7,count_mrb_7_0
count_mrb_vector_9_4:
	collect_value		3
	get_value		1,2
	get_value		6,7
	get_value		4,5
	proceed
count_mrb_vector_9_1:
	suspend		count_mrb_vector_9_0
	module_entry		mpimos_varchk
	predicate		option,2
option_2_0:
	try_me_else		option_2_1
	atom		1
	hash_on_atom		1,6,option_2_1
	bucket_entry_a		a,option_2_3
	bucket_entry_a		all,option_2_4
	bucket_entry_a		m,option_2_5
	bucket_entry_a		mrb,option_2_6
	bucket_entry_a		o,option_2_7
	bucket_entry_a		one,option_2_8
option_2_3:
	get_atom		2,all
	proceed
option_2_4:
	get_atom		2,all
	proceed
option_2_5:
	get_atom		2,mrb
	proceed
option_2_6:
	get_atom		2,mrb
	proceed
option_2_7:
	get_atom		2,one
	proceed
option_2_8:
	get_atom		2,one
	proceed
option_2_1:
	otherwise		option_2_0
	collect_value		1
	get_atom		2,bad
	proceed
option_2_11:
	suspend		option_2_0
	module_entry		mpimos_varchk
	predicate		check,4
check_4_0:
	create_goal		3
	set_value		1,3
	set_variable		2,3
	set_value		3,4
	enqueue_goal		3,check0_3_0
	execute		3,check_tbl_3_0
check_4_1:
	suspend		check_4_0
	module_entry		mpimos_varchk
	predicate		check0,3
check0_3_0:
	try_me_else		check0_3_1
	atom		1
	branch_on_atom		1,3,check0_3_1
	bucket_entry_a		all,check0_3_3
	bucket_entry_a		mrb,check0_3_4
	bucket_entry_a		one,check0_3_5
check0_3_3:
	put_integer		4,0
	g_diff		2,4
	collect_value		2
	get_atom		3,on
	proceed
check0_3_4:
	wait_integer		2,2
	get_atom		3,on
	proceed
check0_3_5:
	wait_integer		2,1
	get_atom		3,on
	proceed
check0_3_1:
	otherwise		check0_3_0
	collect_value		2
	collect_value		1
	get_atom		3,off
	proceed
check0_3_8:
	suspend		check0_3_0
	module_entry		mpimos_varchk
	predicate		check_tbl,3
check_tbl_3_0:
	try_me_else		check_tbl_3_1
	integer		1
	jump_on_integer		1,2,check_tbl_3_3
	table_entry		check_tbl_3_4
	table_entry		check_tbl_3_5
check_tbl_3_4:
	try_me_else		check_tbl_3_3
	integer		2
	jump_on_integer		2,3,check_tbl_3_7
	table_entry		check_tbl_3_8
	table_entry		check_tbl_3_9
	table_entry		check_tbl_3_10
check_tbl_3_8:
	get_integer		3,0
	proceed
check_tbl_3_9:
	get_integer		3,1
	proceed
check_tbl_3_10:
	get_integer		3,0
	proceed
check_tbl_3_7:
	put_integer		4,2
	g_less_than		4,2
	get_integer		3,2
	proceed
check_tbl_3_5:
	try_me_else		check_tbl_3_3
	integer		2
	jump_on_integer		2,3,check_tbl_3_12
	table_entry		check_tbl_3_13
	table_entry		check_tbl_3_14
	table_entry		check_tbl_3_15
check_tbl_3_13:
	get_integer		3,1
	proceed
check_tbl_3_14:
	get_integer		3,0
	proceed
check_tbl_3_15:
	get_integer		3,2
	proceed
check_tbl_3_12:
	put_integer		4,2
	g_less_than		4,2
	get_integer		3,2
	proceed
check_tbl_3_3:
	try_me_else		check_tbl_3_1
	integer		2
	jump_on_integer		2,3,check_tbl_3_17
	table_entry		check_tbl_3_18
	table_entry		check_tbl_3_19
	table_entry		check_tbl_3_20
check_tbl_3_18:
	try_me_else		check_tbl_3_17
	put_integer		4,1
	g_less_than		4,1
	get_integer		3,0
	proceed
check_tbl_3_19:
	try_me_else		check_tbl_3_17
	put_integer		4,1
	g_less_than		4,1
	get_integer		3,0
	proceed
check_tbl_3_20:
	try_me_else		check_tbl_3_17
	put_integer		4,1
	g_less_than		4,1
	get_integer		3,2
	proceed
check_tbl_3_17:
	try_me_else		check_tbl_3_1
	put_integer		4,1
	g_less_than		4,1
	put_integer		4,2
	g_less_than		4,2
	get_integer		3,2
	proceed
check_tbl_3_1:
	suspend		check_tbl_3_0
	module_entry		mpimos_varchk
	predicate		make_tbl,6
make_tbl_6_0:
	try_me_else		make_tbl_6_1
	atom		3
	branch_on_atom		3,2,make_tbl_6_1
	bucket_entry_a		all,make_tbl_6_3
	bucket_entry_a		mrb,make_tbl_6_4
make_tbl_6_3:
	put_marked_value		3,2
	b_new_vector		7,3
	put_integer		3,32
	b_new_string		3,2,3
	put_integer		8,32
	b_new_string		2,2,8
	create_goal		3
	set_variable		1,9
	set_variable		2,10
	set_value		3,5
	enqueue_goal		3,mrb_body_vector_element_3_0
	create_goal		3
	set_variable		1,8
	set_variable		2,5
	set_value		3,10
	enqueue_goal		3,mrb_guard_vector_element_3_0
	create_goal		7
	set_marked_value		1,1
	set_value		2,2
	set_value		3,5
	set_variable		4,5
	set_value		5,6
	set_value		6,9
	set_nil		7
	enqueue_goal		7,count_body_mrb_7_0
	put_values_inc		2,3,2
	put_value		4,7
	put_value		6,8
	put_nil		7
	execute		7,count_guard_mrb_7_0
make_tbl_6_4:
	put_marked_value		3,2
	b_new_vector		7,3
	put_integer		3,32
	b_new_string		3,2,3
	put_integer		8,32
	b_new_string		2,2,8
	create_goal		3
	set_variable		1,9
	set_variable		2,10
	set_value		3,5
	enqueue_goal		3,mrb_body_vector_element_3_0
	create_goal		3
	set_variable		1,8
	set_variable		2,5
	set_value		3,10
	enqueue_goal		3,mrb_guard_vector_element_3_0
	create_goal		7
	set_marked_value		1,1
	set_value		2,2
	set_value		3,5
	set_variable		4,5
	set_value		5,6
	set_value		6,9
	set_nil		7
	enqueue_goal		7,count_body_mrb_7_0
	put_values_inc		2,3,2
	put_value		4,7
	put_value		6,8
	put_nil		7
	execute		7,count_guard_mrb_7_0
make_tbl_6_1:
	otherwise		make_tbl_6_0
	collect_value		3
	put_marked_value		3,2
	b_new_vector		7,3
	put_integer		3,32
	b_new_string		3,2,3
	put_integer		8,32
	b_new_string		2,2,8
	create_goal		5
	set_marked_value		1,1
	set_value		2,2
	set_value		3,5
	set_variable		4,5
	set_value		5,6
	enqueue_goal		5,count_body_5_0
	put_values_inc		2,3,2
	put_value		4,7
	execute		5,count_guard_5_0
make_tbl_6_7:
	suspend		make_tbl_6_0
	module_entry		mpimos_varchk
	predicate		count_guard,5
count_guard_5_0:
	try_me_else		count_guard_5_1
	wait_vector		1,3
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,count_guard_5_1
	bucket_entry_a		-->,count_guard_5_4
	bucket_entry_a		:-,count_guard_5_5
count_guard_5_4:
	read_elements_inc		1,1,7,2
	vector		8
	g_vector		8,9
	wait_integer		9,3
	put_integer		9,0
	g_vector_element		8,9,9
	wait_atom		9,'|'
	put_integer		9,1
	g_vector_element		8,9,6
	mark_element		8,9
	collect_value		8
	collect_vector		1
	create_goal		5
	set_value		1,6
	set_variable		2,8
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	enqueue_goal		5,count_5_0
	put_value		1,7
	put_value		3,8
	put_value		5,6
	execute		5,count_5_0
count_guard_5_5:
	read_elements_inc		1,1,7,2
	vector		8
	g_vector		8,9
	wait_integer		9,3
	put_integer		9,0
	g_vector_element		8,9,9
	wait_atom		9,'|'
	put_integer		9,1
	g_vector_element		8,9,6
	mark_element		8,9
	collect_value		8
	collect_vector		1
	create_goal		5
	set_value		1,6
	set_variable		2,8
	set_value		3,3
	set_variable		4,6
	set_value		5,5
	enqueue_goal		5,count_5_0
	put_value		1,7
	put_value		3,8
	put_value		5,6
	execute		5,count_5_0
count_guard_5_1:
	otherwise		count_guard_5_0
	try_me_else		count_guard_5_11
	wait_vector		1,3
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,count_guard_5_11
	bucket_entry_a		-->,count_guard_5_14
	bucket_entry_a		:-,count_guard_5_15
count_guard_5_14:
	read_elements_inc		1,1,7,2
	collect_value		8
	collect_vector		1
	put_value		1,7
	execute		5,count_5_0
count_guard_5_15:
	read_elements_inc		1,1,7,2
	collect_value		8
	collect_vector		1
	put_value		1,7
	execute		5,count_5_0
count_guard_5_11:
	otherwise		count_guard_5_0
	try_me_else		count_guard_5_21
	wait_vector		1,2
	read_element		1,0,6
	wait_atom		6,:-
	read_element		1,1,6
	collect_value		6
	collect_vector		1
	get_value		2,3
	get_value		4,5
	proceed
count_guard_5_21:
	otherwise		count_guard_5_0
	execute		5,count_5_0
count_guard_5_26:
	suspend		count_guard_5_0
	module_entry		mpimos_varchk
	predicate		count_guard_mrb,7
count_guard_mrb_7_0:
	try_me_else		count_guard_mrb_7_1
	wait_vector		1,3
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,count_guard_mrb_7_1
	bucket_entry_a		-->,count_guard_mrb_7_4
	bucket_entry_a		:-,count_guard_mrb_7_5
count_guard_mrb_7_4:
	read_elements_inc		1,1,9,2
	vector		10
	g_vector		10,11
	wait_integer		11,3
	put_integer		11,0
	g_vector_element		10,11,11
	wait_atom		11,'|'
	put_integer		11,1
	g_vector_element		10,11,8
	mark_element		10,11
	collect_value		10
	collect_vector		1
	create_goal		8
	set_value		1,8
	set_variable		2,10
	set_value		3,3
	set_variable		4,8
	set_values_inc		5,5,3
	set_atom		8,guard
	enqueue_goal		8,count_goals_8_0
	put_value		1,9
	put_value		3,10
	put_value		5,8
	execute		5,count_5_0
count_guard_mrb_7_5:
	read_elements_inc		1,1,9,2
	vector		10
	g_vector		10,11
	wait_integer		11,3
	put_integer		11,0
	g_vector_element		10,11,11
	wait_atom		11,'|'
	put_integer		11,1
	g_vector_element		10,11,8
	mark_element		10,11
	collect_value		10
	collect_vector		1
	create_goal		8
	set_value		1,8
	set_variable		2,10
	set_value		3,3
	set_variable		4,8
	set_values_inc		5,5,3
	set_atom		8,guard
	enqueue_goal		8,count_goals_8_0
	put_value		1,9
	put_value		3,10
	put_value		5,8
	execute		5,count_5_0
count_guard_mrb_7_1:
	otherwise		count_guard_mrb_7_0
	try_me_else		count_guard_mrb_7_11
	wait_vector		1,3
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,count_guard_mrb_7_11
	bucket_entry_a		-->,count_guard_mrb_7_14
	bucket_entry_a		:-,count_guard_mrb_7_15
count_guard_mrb_7_14:
	read_elements_inc		1,1,9,2
	collect_value		10
	collect_vector		1
	get_value		6,7
	put_value		1,9
	execute		5,count_5_0
count_guard_mrb_7_15:
	read_elements_inc		1,1,9,2
	collect_value		10
	collect_vector		1
	get_value		6,7
	put_value		1,9
	execute		5,count_5_0
count_guard_mrb_7_11:
	otherwise		count_guard_mrb_7_0
	try_me_else		count_guard_mrb_7_21
	wait_vector		1,2
	read_element		1,0,8
	wait_atom		8,:-
	read_element		1,1,8
	collect_value		8
	collect_vector		1
	get_value		2,3
	get_value		4,5
	get_value		6,7
	proceed
count_guard_mrb_7_21:
	otherwise		count_guard_mrb_7_0
	get_value		6,7
	execute		5,count_5_0
count_guard_mrb_7_26:
	suspend		count_guard_mrb_7_0
	module_entry		mpimos_varchk
	predicate		count_body,5
count_body_5_0:
	try_me_else		count_body_5_1
	wait_vector		1,3
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,count_body_5_1
	bucket_entry_a		-->,count_body_5_4
	bucket_entry_a		:-,count_body_5_5
count_body_5_4:
	read_elements_inc		1,1,7,2
	vector		8
	g_vector		8,9
	wait_integer		9,3
	put_integer		9,0
	g_vector_element		8,9,9
	wait_atom		9,'|'
	put_integer		9,2
	g_vector_element		8,9,6
	mark_element		8,9
	collect_value		8
	collect_value		7
	collect_vector		1
	put_value		1,6
	execute		5,count_5_0
count_body_5_5:
	read_elements_inc		1,1,7,2
	vector		8
	g_vector		8,9
	wait_integer		9,3
	put_integer		9,0
	g_vector_element		8,9,9
	wait_atom		9,'|'
	put_integer		9,2
	g_vector_element		8,9,6
	mark_element		8,9
	collect_value		8
	collect_value		7
	collect_vector		1
	put_value		1,6
	execute		5,count_5_0
count_body_5_1:
	otherwise		count_body_5_0
	try_me_else		count_body_5_11
	wait_vector		1,3
	read_element		1,0,6
	atom		6
	branch_on_atom		6,2,count_body_5_11
	bucket_entry_a		-->,count_body_5_14
	bucket_entry_a		:-,count_body_5_15
count_body_5_14:
	read_elements_inc		1,1,7,2
	collect_value		7
	collect_vector		1
	put_value		1,8
	execute		5,count_5_0
count_body_5_15:
	read_elements_inc		1,1,7,2
	collect_value		7
	collect_vector		1
	put_value		1,8
	execute		5,count_5_0
count_body_5_11:
	otherwise		count_body_5_0
	try_me_else		count_body_5_21
	wait_vector		1,2
	read_element		1,0,6
	wait_atom		6,:-
	read_element		1,1,6
	collect_vector		1
	put_value		1,6
	execute		5,count_5_0
count_body_5_21:
	otherwise		count_body_5_0
	collect_value		1
	get_value		2,3
	get_value		4,5
	proceed
count_body_5_26:
	suspend		count_body_5_0
	module_entry		mpimos_varchk
	predicate		count_body_mrb,7
count_body_mrb_7_0:
	try_me_else		count_body_mrb_7_1
	wait_vector		1,3
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,count_body_mrb_7_1
	bucket_entry_a		-->,count_body_mrb_7_4
	bucket_entry_a		:-,count_body_mrb_7_5
count_body_mrb_7_4:
	read_elements_inc		1,1,9,2
	vector		10
	g_vector		10,11
	wait_integer		11,3
	put_integer		11,0
	g_vector_element		10,11,11
	wait_atom		11,'|'
	put_integer		11,2
	g_vector_element		10,11,8
	mark_element		10,11
	collect_value		10
	collect_value		9
	collect_vector		1
	put_value		1,8
	put_atom		8,body
	execute		8,count_goals_8_0
count_body_mrb_7_5:
	read_elements_inc		1,1,9,2
	vector		10
	g_vector		10,11
	wait_integer		11,3
	put_integer		11,0
	g_vector_element		10,11,11
	wait_atom		11,'|'
	put_integer		11,2
	g_vector_element		10,11,8
	mark_element		10,11
	collect_value		10
	collect_value		9
	collect_vector		1
	put_value		1,8
	put_atom		8,body
	execute		8,count_goals_8_0
count_body_mrb_7_1:
	otherwise		count_body_mrb_7_0
	try_me_else		count_body_mrb_7_11
	wait_vector		1,3
	read_element		1,0,8
	atom		8
	branch_on_atom		8,2,count_body_mrb_7_11
	bucket_entry_a		-->,count_body_mrb_7_14
	bucket_entry_a		:-,count_body_mrb_7_15
count_body_mrb_7_14:
	read_elements_inc		1,1,9,2
	collect_value		9
	collect_vector		1
	put_value		1,10
	put_atom		8,body
	execute		8,count_goals_8_0
count_body_mrb_7_15:
	read_elements_inc		1,1,9,2
	collect_value		9
	collect_vector		1
	put_value		1,10
	put_atom		8,body
	execute		8,count_goals_8_0
count_body_mrb_7_11:
	otherwise		count_body_mrb_7_0
	try_me_else		count_body_mrb_7_21
	wait_vector		1,2
	read_element		1,0,8
	wait_atom		8,:-
	read_element		1,1,8
	collect_vector		1
	get_value		6,7
	put_value		1,8
	execute		5,count_5_0
count_body_mrb_7_21:
	otherwise		count_body_mrb_7_0
	collect_value		1
	get_value		2,3
	get_value		4,5
	get_value		6,7
	proceed
count_body_mrb_7_26:
	suspend		count_body_mrb_7_0
	module_entry		mpimos_varchk
	predicate		mrb_guard_vector_element,3
mrb_guard_vector_element_3_0:
	try_me_else		mrb_guard_vector_element_3_1
	jump_on_non_list		1,mrb_guard_vector_element_3_3
	read_car		1,4
	wait_vector		4,2
	read_element		4,0,5
	integer		5
	read_element		4,1,6
	read_cdr		1,7
	string		2
	try_me_else		mrb_guard_vector_element_3_7
	g_string_element		2,5,8
	put_integer		9,0
	g_less_than		9,8
	collect_list		1
	collect_vector		4
	create_goal		3
	set_variable		1,4
	set_variable		2,1
	set_value		3,3
	enqueue_goal		3,mrb_guard_vector_element_3_0
	create_goal		5
	set_marked_value		1,6
	set_value		2,7
	set_value		3,4
	set_variable		4,3
	set_value		5,1
	enqueue_goal		5,mrb_guard_vector_element_sub_5_0
	put_value		1,6
	execute		3,mrb_guard_vector_element_mark_3_0
mrb_guard_vector_element_3_7:
	try_me_else		mrb_guard_vector_element_3_1
	g_string_element		2,5,8
	wait_integer		8,0
	collect_list		1
	collect_value		6
	collect_vector		4
	put_value		1,7
	execute		3,mrb_guard_vector_element_3_0
mrb_guard_vector_element_3_3:
	check_nil		1,mrb_guard_vector_element_3_1
	get_value		2,3
	proceed
mrb_guard_vector_element_3_1:
	suspend		mrb_guard_vector_element_3_0
	module_entry		mpimos_varchk
	predicate		mrb_guard_vector_element_mark,3
mrb_guard_vector_element_mark_3_0:
	try_me_else		mrb_guard_vector_element_mark_3_1
	jump_on_non_list		1,mrb_guard_vector_element_mark_3_3
	read_car		1,4
	integer		4
	read_cdr		1,5
	string		2
	try_me_else		mrb_guard_vector_element_mark_3_6
	g_string_element		2,4,6
	wait_integer		6,1
	collect_list		1
	put_integer		1,3
	b_set_string_element		2,4,1,2
	put_value		1,5
	execute		3,mrb_guard_vector_element_mark_3_0
mrb_guard_vector_element_mark_3_6:
	try_me_else		mrb_guard_vector_element_mark_3_1
	g_string_element		2,4,6
	put_integer		7,1
	g_not_equal		6,7
	collect_list		1
	put_value		1,5
	execute		3,mrb_guard_vector_element_mark_3_0
mrb_guard_vector_element_mark_3_3:
	check_nil		1,mrb_guard_vector_element_mark_3_1
	get_value		2,3
	proceed
mrb_guard_vector_element_mark_3_1:
	suspend		mrb_guard_vector_element_mark_3_0
	module_entry		mpimos_varchk
	predicate		mrb_guard_vector_element_sub,5
mrb_guard_vector_element_sub_5_0:
	try_me_else		mrb_guard_vector_element_sub_5_1
	jump_on_non_list_var_var		1,mrb_guard_vector_element_sub_5_3,6,7
	collect_list		1
	create_goal		5
	set_value		1,7
	set_variable		2,8
	set_value		3,3
	set_variable		4,7
	set_value		5,5
	enqueue_goal		5,mrb_guard_vector_element_sub_5_0
	put_value		1,6
	put_value		3,8
	put_value		5,7
	execute		5,mrb_guard_vector_element_sub_var_5_0
mrb_guard_vector_element_sub_5_3:
	check_nil		1,mrb_guard_vector_element_sub_5_1
	get_value		2,3
	get_value		4,5
	proceed
mrb_guard_vector_element_sub_5_1:
	suspend		mrb_guard_vector_element_sub_5_0
	module_entry		mpimos_varchk
	predicate		mrb_guard_vector_element_sub_var,5
mrb_guard_vector_element_sub_var_5_0:
	try_me_else		mrb_guard_vector_element_sub_var_5_1
	integer		1
	list		2
	read_car		2,6
	wait_vector		6,2
	read_element		6,0,7
	integer		7
	read_element		6,1,8
	read_cdr		2,9
	try_me_else		mrb_guard_vector_element_sub_var_5_6
	g_equal		1,7
	collect_list		2
	collect_vector		6
	create_goal		5
	set_value		1,1
	set_value		2,9
	set_value		3,3
	set_variable		4,3
	set_value		5,5
	enqueue_goal		5,mrb_guard_vector_element_sub_var_5_0
	put_value		1,8
	put_value		2,4
	execute		3,mrb_guard_vector_element_mark_3_0
mrb_guard_vector_element_sub_var_5_6:
	put_reused_vector		6,6
	write_elements_inc		6,0,7,2
	get_reused_list_val_var		3,2,2,6,6
	put_value		2,9
	put_value		3,6
	execute		5,mrb_guard_vector_element_sub_var_5_0
mrb_guard_vector_element_sub_var_5_1:
	try_me_else		mrb_guard_vector_element_sub_var_5_7
	wait_nil		2
	collect_value		1
	get_nil		3
	get_value		4,5
	proceed
mrb_guard_vector_element_sub_var_5_7:
	suspend		mrb_guard_vector_element_sub_var_5_0
	module_entry		mpimos_varchk
	predicate		mrb_body_vector_element,3
mrb_body_vector_element_3_0:
	try_me_else		mrb_body_vector_element_3_1
	jump_on_non_list_var_var		1,mrb_body_vector_element_3_3,4,5
	collect_list		1
	put_integer		1,3
	b_set_string_element		2,4,1,2
	put_value		1,5
	execute		3,mrb_body_vector_element_3_0
mrb_body_vector_element_3_3:
	check_nil		1,mrb_body_vector_element_3_1
	get_value		2,3
	proceed
mrb_body_vector_element_3_1:
	suspend		mrb_body_vector_element_3_0
	begin_const_section		mpimos_varchk
'$SCNST_0_0':
	define_desc		19,2
	define_integer		1668440438
	define_integer		27496
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		3,3
	define_integer		1701603654
	define_integer		1835093536
	define_integer		540680293
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_0':
	define_desc		0,2
	define_atom		print_depth
	define_integer		30
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_0':
	define_desc		0,2
	define_atom		print_length
	define_integer		30
'$SCNST_3':
	define_vector		'$SCNST_3_0'
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
'$SCNST_5_1':
	define_desc		3,1
	define_integer		540686906
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putc
	define_integer		46
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		3,13
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
	define_integer		707406378
	define_integer		707406378
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_0':
	define_desc		0,2
	define_atom		tab
	define_integer		1
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_9_0':
	define_desc		27,1
	define_integer		95
'$SCNST_10':
'$SCNST_9':
	define_string		'$SCNST_9_0'
