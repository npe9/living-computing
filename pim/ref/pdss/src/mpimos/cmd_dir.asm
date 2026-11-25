mpimos_cmd_directory:
	module		mpimos_cmd_directory
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_cmd_directory
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	test_atom		1,pwd,is_command_2_1
	get_atom		2,yes
	proceed
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,4,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_4
	table_entry		is_command_2_5
is_command_2_4:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,is_command_2_1
	bucket_entry_a		cd,is_command_2_7
	bucket_entry_a		ls,is_command_2_8
	bucket_entry_a		pwd,is_command_2_9
	bucket_entry_a		rm,is_command_2_10
is_command_2_7:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_8:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_9:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_10:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_5:
	read_element		1,0,3
	wait_atom		3,ls
	read_elements_inc		1,1,3,2
	collect_value		4
	collect_value		3
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_1:
	otherwise		is_command_2_0
	collect_value		1
	get_atom		2,no
	proceed
is_command_2_17:
	suspend		is_command_2_0
	module_entry		mpimos_cmd_directory
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	test_atom		1,pwd,do_command_2_1
	put_value		4,2
	put_integer		1,0
	put_integer		2,8
	b_new_string		1,1,2
	create_goal		3
	set_variable		1,6
	set_variable		2,5
	set_variable		3,3
	enqueue_goal		3,pwd_3_0
	put_func		2,2,pathname
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_value		2,3
	put_value		3,6
	execute		5,command_to_directory_5_0
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,4,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_4
	table_entry		do_command_2_5
do_command_2_4:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,4,do_command_2_1
	bucket_entry_a		cd,do_command_2_7
	bucket_entry_a		ls,do_command_2_8
	bucket_entry_a		pwd,do_command_2_9
	bucket_entry_a		rm,do_command_2_10
do_command_2_7:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_12
	b_atom_name		4,3
	put_reused_func		1,1,cd
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_12:
	is_string		4,do_command_2_1
	g_string		4,5,6
	wait_integer		6,8
	collect_vector		1
	put_func		1,3,getenv
	write_element_atom		1,1,world
	write_element_variable		1,2,3
	get_list_val_var		2,5,1,1
	put_value		2,4
	execute		3,change_directory_3_0
do_command_2_8:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_14
	b_atom_name		4,3
	put_reused_func		1,1,ls
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_14:
	is_string		4,do_command_2_1
	g_string		4,5,6
	wait_integer		6,8
	collect_vector		1
	create_goal		4
	set_variable		1,6
	set_variable		2,7
	set_variable		3,8
	set_variable		4,9
	enqueue_goal		4,file_list_4_0
	create_goal		5
	set_variable		1,5
	put_func		1,4,listing
	write_element_variable		1,1,3
	write_elements_dec		1,2,9,2
	put_list		8
	write_car_value		8,1
	write_cdr_nil		8
	set_values_dec		2,8,2
	set_value		4,2
	set_value		5,6
	enqueue_goal		5,command_to_directory_5_0
	put_values_inc		1,4,2
	execute		3,split_wildcard_3_0
do_command_2_9:
	read_element		1,1,4
	put_value		6,2
	put_integer		2,0
	put_integer		3,8
	b_new_string		2,2,3
	create_goal		4
	set_value		1,4
	set_variable		2,4
	set_variable		3,5
	set_variable		4,3
	enqueue_goal		4,pwd_4_0
	put_reused_func		1,1,pathname
	write_element_value		1,1,3
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_values_inc		1,2,3
	put_value		4,6
	execute		5,command_to_directory_5_0
do_command_2_10:
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_16
	b_atom_name		4,3
	put_reused_func		1,1,rm
	write_element_value		1,1,3
	execute		2,do_command_2_0
do_command_2_16:
	is_string		4,do_command_2_1
	g_string		4,5,6
	wait_integer		6,8
	collect_vector		1
	create_goal		3
	set_variable		1,6
	set_variable		2,7
	set_variable		3,8
	enqueue_goal		3,wait_remove_3_0
	create_goal		5
	set_variable		1,5
	put_func		1,3,delete
	write_element_variable		1,1,3
	write_element_value		1,2,8
	put_list		8
	write_car_value		8,1
	write_cdr_nil		8
	set_values_dec		2,8,2
	set_value		4,2
	set_value		5,6
	enqueue_goal		5,command_to_directory_5_0
	put_values_inc		1,4,2
	execute		3,split_wildcard_3_0
do_command_2_5:
	read_element		1,0,3
	wait_atom		3,ls
	read_element		1,1,4
	jump_on_non_atom		4,do_command_2_19
	read_element		1,2,5
	b_atom_name		4,3
	put_reused_func		1,1,ls
	write_element_value		1,1,3
	write_element_value		1,2,5
	execute		2,do_command_2_0
do_command_2_19:
	is_string		4,do_command_2_1
	read_element		1,2,5
	g_string		4,6,7
	wait_integer		7,8
	collect_vector		1
	create_goal		5
	set_variable		1,7
	set_variable		2,8
	set_variable		3,9
	set_value		4,5
	set_variable		5,6
	enqueue_goal		5,wait_st_5_0
	create_goal		5
	set_variable		1,5
	put_func		1,4,listing
	write_element_variable		1,1,3
	write_elements_dec		1,2,9,2
	put_list		8
	write_car_value		8,1
	write_cdr_nil		8
	set_values_dec		2,8,2
	set_value		4,2
	set_value		5,6
	enqueue_goal		5,command_to_directory_5_0
	put_values_inc		1,4,2
	execute		3,split_wildcard_3_0
do_command_2_1:
	otherwise		do_command_2_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_0'
	put_func		4,2,putt
	write_element_variable		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_1'
	put_list_val_val		4,3,5
	put_func		3,2,window
	write_element_value		3,1,4
	set_values_dec		1,3,2
	put_func		2,2,flush
	write_element_value		2,1,7
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	set_value		3,3
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_value		2,6
	execute_external		mpimos_utility,freeze,2
do_command_2_42:
	suspend		do_command_2_0
	module_entry		mpimos_cmd_directory
	predicate		command_to_directory,5
command_to_directory_5_0:
	put_func		6,3,getenv
	write_element_atom		6,1,world
	write_element_variable		6,2,7
	get_list_val_var		4,8,6,6
	put_value		4,6
	put_value		6,7
	execute		6,check_world_6_0
command_to_directory_5_1:
	suspend		command_to_directory_5_0
	module_entry		mpimos_cmd_directory
	predicate		check_world,6
check_world_6_0:
	try_me_else		check_world_6_1
	string		6
	g_string		6,7,8
	wait_integer		8,8
	put_value		7,1
	create_goal		4
	set_values_inc		1,4,2
	set_value		3,3
	set_variable		4,1
	enqueue_goal		4,check_world_0_4_0
	create_goal		3
	set_value		1,2
	set_variable		2,3
	set_value		3,1
	enqueue_goal_external		mpimos_directory,create,3
	put_values_inc		1,6,2
	execute_external		mpimos_utility,pathname,3
check_world_6_1:
	otherwise		check_world_6_0
	collect_value		2
	collect_value		1
	get_atom		3,fail
	put_func		1,2,flush
	write_element_void		1,1
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_func		2,2,putt
	write_element_value		2,1,6
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_2'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_list_val_val		2,1,5
	get_list_value		4,2
	proceed
check_world_6_5:
	suspend		check_world_6_0
	module_entry		mpimos_cmd_directory
	predicate		check_world_0,4
check_world_0_4_0:
	try_me_else		check_world_0_4_1
	wait_atom		4,success
	get_atom		3,success
	get_value		1,2
	proceed
check_world_0_4_1:
	otherwise		check_world_0_4_0
	try_me_else		check_world_0_4_6
	wait_vector		4,2
	read_element		4,0,5
	wait_atom		5,error
	read_element		4,1,5
	put_reused_func		4,4,error
	write_element_value		4,1,5
	get_vector_value		3,4
	get_value		1,2
	proceed
check_world_0_4_6:
	suspend		check_world_0_4_0
	module_entry		mpimos_cmd_directory
	predicate		change_directory,3
change_directory_3_0:
	try_me_else		change_directory_3_1
	string		3
	g_string		3,4,5
	wait_integer		5,8
	create_goal		3
	set_value		1,1
	set_variable		2,4
	set_variable		3,1
	enqueue_goal		3,change_directory0_3_0
	create_goal		3
	set_value		1,4
	set_variable		2,4
	set_value		3,1
	enqueue_goal_external		mpimos_directory,create,3
	put_value		1,3
	put_value		3,4
	execute_external		mpimos_utility,pathname,3
change_directory_3_1:
	otherwise		change_directory_3_0
	collect_value		3
	create_goal		3
	set_value		1,1
	set_variable		2,1
	set_variable		3,3
	enqueue_goal		3,change_directory0_3_0
	execute_external		mpimos_directory,create,3
change_directory_3_5:
	suspend		change_directory_3_0
	module_entry		mpimos_cmd_directory
	predicate		change_directory0,3
change_directory0_3_0:
	try_me_else		change_directory0_3_1
	jump_on_non_atom		3,change_directory0_3_3
	test_atom		3,success,change_directory0_3_1
	put_value		6,1
	put_func		1,2,pathname
	write_element_marked_variable		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	create_goal		1
	set_variable		1,5
	enqueue_goal		1,wait_1_0
	put_structured_constant		1,'$SCNST_3'
	put_func		2,2,putb
	write_element_value		2,1,4
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_func		2,3,setenv
	write_element_atom		2,1,world
	write_element_value		2,2,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,flush
	write_element_value		2,1,5
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_func		2,2,window
	write_element_value		2,1,4
	put_list_val_val		4,2,3
	put_value		2,6
	put_value		3,4
	execute_external		mpimos_cmd_utl,send_shell,3
change_directory0_3_3:
	check_vector		3,2,change_directory0_3_1
	read_element		3,0,4
	wait_atom		4,error
	read_element		3,1,4
	collect_value		4
	get_nil		2
	put_reused_func		2,3,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_5'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_fail_1_0
change_directory0_3_1:
	suspend		change_directory0_3_0
	module_entry		mpimos_cmd_directory
	predicate		file_list,4
file_list_4_0:
	try_me_else		file_list_4_1
	atom		2
	branch_on_atom		2,2,file_list_4_1
	bucket_entry_a		fail,file_list_4_3
	bucket_entry_a		success,file_list_4_4
file_list_4_3:
	collect_value		4
	collect_value		3
	get_nil		1
	put_atom		1,done
	execute		1,wait_fail_1_0
file_list_4_4:
	wait_atom		3,success
	list		4
	create_goal		1
	set_variable		1,2
	enqueue_goal		1,wait_1_0
	create_goal		3
	put_func		5,2,window
	write_element_variable		5,1,3
	set_value		1,5
	set_value		2,1
	put_func		1,2,flush
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_func		1,2,window
	write_element_value		1,1,2
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	set_value		3,2
	enqueue_goal_external		mpimos_cmd_utl,send_shell,3
	put_values_dec		1,4,2
	execute		2,file_list0_2_0
file_list_4_1:
	otherwise		file_list_4_0
	collect_value		4
	collect_value		3
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_6'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_fail_1_0
file_list_4_7:
	suspend		file_list_4_0
	module_entry		mpimos_cmd_directory
	predicate		file_list0,2
file_list0_2_0:
	try_me_else		file_list0_2_1
	jump_on_non_list_var_var		1,file_list0_2_3,3,4
	string		3
	g_string		3,5,6
	put_func		5,2,putl
	write_element_value		5,1,3
	get_reused_list_val_var		2,1,1,5,3
	put_values_dec		1,4,2
	execute		2,file_list0_2_0
file_list0_2_3:
	check_nil		1,file_list0_2_1
	get_nil		2
	proceed
file_list0_2_1:
	suspend		file_list0_2_0
	module_entry		mpimos_cmd_directory
	predicate		wait_st,5
wait_st_5_0:
	try_me_else		wait_st_5_1
	atom		1
	branch_on_atom		1,2,wait_st_5_1
	bucket_entry_a		fail,wait_st_5_3
	bucket_entry_a		success,wait_st_5_4
wait_st_5_3:
	collect_value		3
	collect_value		2
	get_nil		4
	get_nil		5
	put_atom		1,done
	execute		1,wait_fail_1_0
wait_st_5_4:
	wait_atom		2,success
	get_nil		5
	get_value		3,4
	proceed
wait_st_5_1:
	otherwise		wait_st_5_0
	collect_value		3
	collect_value		2
	collect_value		1
	get_nil		4
	get_nil		5
	proceed
wait_st_5_7:
	suspend		wait_st_5_0
	module_entry		mpimos_cmd_directory
	predicate		wait_remove,3
wait_remove_3_0:
	try_me_else		wait_remove_3_1
	atom		2
	branch_on_atom		2,2,wait_remove_3_1
	bucket_entry_a		fail,wait_remove_3_3
	bucket_entry_a		success,wait_remove_3_4
wait_remove_3_3:
	collect_value		3
	get_nil		1
	put_atom		1,done
	execute		1,wait_fail_1_0
wait_remove_3_4:
	wait_atom		3,success
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_7'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_1_0
wait_remove_3_1:
	otherwise		wait_remove_3_0
	collect_value		3
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,3
	put_structured_constant		3,'$SCNST_8'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_fail_1_0
wait_remove_3_7:
	suspend		wait_remove_3_0
	module_entry		mpimos_cmd_directory
	predicate		pwd,3
pwd_3_0:
	try_me_else		pwd_3_1
	wait_atom		1,success
	put_func		1,2,flush
	write_element_variable		1,1,5
	put_list		4
	write_car_value		4,1
	write_cdr_nil		4
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,4
	put_func		4,2,putb
	write_element_value		4,1,3
	put_list_val_val		3,4,1
	put_structured_constant		1,'$SCNST_9'
	put_list_val_val		4,1,3
	put_func		1,2,window
	write_element_value		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	get_list_value		2,3
	put_value		1,5
	execute		1,wait_1_0
pwd_3_1:
	otherwise		pwd_3_0
	collect_value		3
	collect_value		1
	get_nil		2
	put_atom		1,done
	execute		1,wait_fail_1_0
pwd_3_6:
	suspend		pwd_3_0
	module_entry		mpimos_cmd_directory
	predicate		pwd,4
pwd_4_0:
	try_me_else		pwd_4_1
	wait_atom		2,success
	get_value		1,4
	get_nil		3
	proceed
pwd_4_1:
	otherwise		pwd_4_0
	collect_value		4
	collect_value		2
	put_integer		2,0
	put_integer		4,8
	b_new_string		2,2,4
	get_value		2,1
	get_nil		3
	put_atom		1,done
	execute		1,wait_fail_1_0
pwd_4_6:
	suspend		pwd_4_0
	module_entry		mpimos_cmd_directory
	predicate		split_wildcard,3
split_wildcard_3_0:
	try_me_else		split_wildcard_3_1
	string		1
	g_string		1,4,5
	wait_integer		5,8
	put_marked_value		5,4
	b_decrement		5,5
	create_goal		5
	set_variable		1,6
	set_values_inc		2,2,2
	set_values_dec		4,5,2
	enqueue_goal		5,split_wildcard_5_0
	put_value		2,6
	execute_external		mpimos_utility,compress,2
split_wildcard_3_1:
	suspend		split_wildcard_3_0
	module_entry		mpimos_cmd_directory
	predicate		split_wildcard,5
split_wildcard_5_0:
	try_me_else		split_wildcard_5_1
	string		1
	integer		4
	test_integer		4,0,split_wildcard_5_4
	try_me_else		split_wildcard_5_4
	put_integer		6,0
	g_string_element		1,6,6
	wait_integer		6,126
	collect_value		5
	get_value		2,1
	put_integer		1,0
	put_integer		2,8
	b_new_string		1,1,2
	get_value		1,3
	proceed
split_wildcard_5_4:
	try_me_else		split_wildcard_5_1
	integer		5
	g_string_element		1,4,6
	g_decrement		5,7
	try_me_else		split_wildcard_5_6
	g_equal		4,7
	try_me_else		split_wildcard_5_1
	wait_integer		6,47
	put_integer		5,0
	b_substring		1,5,4,4,1
	get_value		4,2
	put_integer		1,0
	put_integer		2,8
	b_new_string		1,1,2
	get_value		1,3
	proceed
split_wildcard_5_6:
	try_me_else		split_wildcard_5_1
	wait_integer		6,47
	put_integer		6,0
	put_marked_value		7,4
	b_substring		1,6,7,6,1
	get_value		6,2
	b_increment		4,2
	b_subtract		5,4,4
	b_decrement		4,4
	b_substring		1,2,4,2,1
	get_value		2,3
	proceed
split_wildcard_5_1:
	try_me_else		split_wildcard_5_7
	integer		4
	put_integer		6,0
	g_less_than		4,6
	collect_value		5
	put_integer		4,0
	put_integer		5,8
	b_new_string		4,4,5
	get_value		4,2
	get_value		3,1
	proceed
split_wildcard_5_7:
	otherwise		split_wildcard_5_0
	b_decrement		4,4
	execute		5,split_wildcard_5_0
split_wildcard_5_18:
	suspend		split_wildcard_5_0
	module_entry		mpimos_cmd_directory
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait		1
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_cmd_directory
	predicate		wait_fail,1
wait_fail_1_0:
	try_me_else		wait_fail_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_10'
	put_void		3
	b_raise		2,1,3
	proceed
wait_fail_1_1:
	suspend		wait_fail_1_0
	module_entry		mpimos_cmd_directory
	predicate		fail_action,1
fail_action_1_0:
	try_me_else		fail_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_11'
	put_void		3
	b_raise		2,1,3
	proceed
fail_action_1_1:
	suspend		fail_action_1_0
	module_entry		mpimos_cmd_directory
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,dir
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_12'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_13'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_cmd_directory
'$SCNST_0_0':
	define_atom		nl
	define_atom		[]
'$SCNST_3':
'$SCNST_0':
	define_list		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		19,7
	define_integer		1969713729
	define_integer		1953391981
	define_integer		1869771333
	define_integer		1701060722
	define_integer		1952671092
	define_integer		1763730533
	define_integer		8302
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		27,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		1919907616
	define_integer		1025533036
	define_integer		32
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_4_1':
	define_desc		3,2
	define_integer		1819438967
	define_integer		540876900
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_9':
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_5_1':
	define_desc		27,5
	define_integer		1931505486
	define_integer		543712117
	define_integer		1701996900
	define_integer		1919906915
	define_integer		121
'$SCNST_5_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_5_1'
'$SCNST_5':
	define_vector		'$SCNST_5_0'
'$SCNST_6_1':
	define_desc		19,3
	define_integer		544501582
	define_integer		1853189990
	define_integer		11876
'$SCNST_6_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_6_1'
'$SCNST_6':
	define_vector		'$SCNST_6_0'
'$SCNST_7_1':
	define_desc		27,2
	define_integer		1701736260
	define_integer		46
'$SCNST_7_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_7_1'
'$SCNST_7':
	define_vector		'$SCNST_7_0'
'$SCNST_8_1':
	define_desc		3,3
	define_integer		1701736270
	define_integer		1953720696
	define_integer		779382373
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_10_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_11':
'$SCNST_10':
	define_vector		'$SCNST_10_0'
'$SCNST_12_0':
	define_desc		27,5
	define_integer		1881957475
	define_integer		1814848631
	define_integer		1836199027
	define_integer		1668572460
	define_integer		46
'$SCNST_12':
	define_string		'$SCNST_12_0'
'$SCNST_13_1':
	define_desc		11,10
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1701996900
	define_integer		1919906915
	define_integer		1868767353
	define_integer		1851878765
	define_integer		3044196
'$SCNST_13_3':
	define_desc		27,16
	define_integer		1143497827
	define_integer		1128616521
	define_integer		1498566484
	define_integer		538976297
	define_integer		757080096
	define_integer		1126182189
	define_integer		1735287144
	define_integer		1969430629
	define_integer		1852142194
	define_integer		1768169588
	define_integer		1952671090
	define_integer		544830063
	define_integer		1142976372
	define_integer		1128616521
	define_integer		1498566484
	define_integer		46
'$SCNST_13_5':
	define_desc		11,12
	define_integer		543455088
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1920295712
	define_integer		1953391986
	define_integer		1953063968
	define_integer		1869898610
	define_integer		3045746
'$SCNST_13_7':
	define_desc		19,15
	define_integer		677672816
	define_integer		1163020612
	define_integer		1380930627
	define_integer		538978649
	define_integer		757080096
	define_integer		1193291053
	define_integer		1663071333
	define_integer		1701999221
	define_integer		1679848558
	define_integer		1668445289
	define_integer		2037542772
	define_integer		544175136
	define_integer		1163020612
	define_integer		1380930627
	define_integer		11865
'$SCNST_13_9':
	define_desc		11,15
	define_integer		1462268780
	define_integer		1128549449
	define_integer		692343361
	define_integer		538976288
	define_integer		757080096
	define_integer		1277177133
	define_integer		1769239401
	define_integer		1713399662
	define_integer		543517801
	define_integer		1701667182
	define_integer		1634541683
	define_integer		1701340020
	define_integer		1230446692
	define_integer		1094927436
	define_integer		3032146
'$SCNST_13_11':
	define_desc		3,17
	define_integer		1462268780
	define_integer		1128549449
	define_integer		742675009
	define_integer		1162627398
	define_integer		757082451
	define_integer		1277177133
	define_integer		1769239401
	define_integer		1713399662
	define_integer		543517801
	define_integer		1701667182
	define_integer		1634541683
	define_integer		1701340020
	define_integer		1230446692
	define_integer		1094927436
	define_integer		1948271698
	define_integer		1229332591
	define_integer		777209164
'$SCNST_13_13':
	define_desc		27,14
	define_integer		1462267250
	define_integer		1128549449
	define_integer		692343361
	define_integer		538976288
	define_integer		757080096
	define_integer		1142959405
	define_integer		1952803941
	define_integer		1768300645
	define_integer		544433516
	define_integer		1668571501
	define_integer		543450472
	define_integer		1145850199
	define_integer		1146241347
	define_integer		46
'$SCNST_13_12':
	define_string		'$SCNST_13_13'
	define_atom		[]
'$SCNST_13_10':
	define_string		'$SCNST_13_11'
	define_list		'$SCNST_13_12'
'$SCNST_13_8':
	define_string		'$SCNST_13_9'
	define_list		'$SCNST_13_10'
'$SCNST_13_6':
	define_string		'$SCNST_13_7'
	define_list		'$SCNST_13_8'
'$SCNST_13_4':
	define_string		'$SCNST_13_5'
	define_list		'$SCNST_13_6'
'$SCNST_13_2':
	define_string		'$SCNST_13_3'
	define_list		'$SCNST_13_4'
'$SCNST_13_0':
	define_string		'$SCNST_13_1'
	define_list		'$SCNST_13_2'
'$SCNST_13':
	define_list		'$SCNST_13_0'
