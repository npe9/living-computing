mpimos_cmd_utl:
	module		mpimos_cmd_utl
	entry		send_shell,3,send_shell_3_0
	entry		protect,2,protect_2_0
	entry		wait_send,4,wait_send_4_0
	entry		check_savedir,5,check_savedir_5_0
	entry		os_check_loaddir,5,os_check_loaddir_5_0
	entry		apply_action,3,apply_action_3_0
	entry		apply_action,4,apply_action_4_0
	module_entry		mpimos_cmd_utl
	predicate		send_shell,3
send_shell_3_0:
	create_goal		3
	set_variable		1,4
	set_values_inc		2,2,2
	enqueue_goal		3,send_shell0_3_0
	put_value		2,4
	execute		2,protect_2_0
send_shell_3_1:
	suspend		send_shell_3_0
	module_entry		mpimos_cmd_utl
	predicate		send_shell0,3
send_shell0_3_0:
	try_me_else		send_shell0_3_1
	wait		1
	put_list_val_val		4,1,3
	get_list_value		2,4
	proceed
send_shell0_3_1:
	suspend		send_shell0_3_0
	module_entry		mpimos_cmd_utl
	predicate		protect,2
protect_2_0:
	try_me_else		protect_2_1
	wait		1
	switch_on_type		1,protect_2_2,protect_2_3,protect_2_4,protect_2_5,protect_2_6,protect_2_7
protect_2_4:
	read_car		1,3
	read_cdr		1,4
	collect_list		1
	create_goal		3
	set_variable		1,5
	set_variable		2,1
	set_value		3,2
	enqueue_goal		3,protect_list_3_0
	create_goal		2
	set_value		1,4
	set_value		2,1
	enqueue_goal		2,protect_2_0
	put_value		1,3
	put_value		2,5
	execute		2,protect_2_0
protect_2_2:
	get_value		2,1
	proceed
protect_2_3:
	get_value		2,1
	proceed
protect_2_5:
	g_vector		1,3
	put_marked_value		4,3
	b_new_vector		4,4
	b_decrement		3,3
	put_value		5,3
	put_values_inc		3,4,2
	execute		4,protect_vector_4_0
protect_2_6:
	get_value		2,1
	proceed
protect_2_7:
	is_float		1,protect_2_1
	get_value		2,1
	proceed
protect_2_1:
	suspend		protect_2_0
	module_entry		mpimos_cmd_utl
	predicate		protect_vector,4
protect_vector_4_0:
	try_me_else		protect_vector_4_1
	vector		1
	integer		4
	g_vector_element		1,4,5
	mark_element		1,4
	create_goal		5
	set_values_inc		1,1,2
	set_variable		3,2
	set_values_inc		4,3,2
	enqueue_goal		5,protect_vector0_5_0
	put_marked_value		1,5
	execute		2,protect_2_0
protect_vector_4_1:
	try_me_else		protect_vector_4_4
	integer		4
	put_integer		5,0
	g_less_than		4,5
	collect_value		1
	get_value		2,3
	proceed
protect_vector_4_4:
	suspend		protect_vector_4_0
	module_entry		mpimos_cmd_utl
	predicate		protect_vector0,5
protect_vector0_5_0:
	try_me_else		protect_vector0_5_1
	wait		3
	put_marked_value		6,5
	b_set_vector_element		4,6,3,3,4
	b_decrement		5,3
	put_value		5,3
	put_values_inc		3,4,2
	execute		4,protect_vector_4_0
protect_vector0_5_1:
	suspend		protect_vector0_5_0
	module_entry		mpimos_cmd_utl
	predicate		protect_list,3
protect_list_3_0:
	try_me_else		protect_list_3_1
	wait		1
	wait		2
	put_list_val_val		4,1,2
	get_list_value		3,4
	proceed
protect_list_3_1:
	suspend		protect_list_3_0
	module_entry		mpimos_cmd_utl
	predicate		wait_send,4
wait_send_4_0:
	try_me_else		wait_send_4_1
	jump_on_non_list_var_var		1,wait_send_4_3,5,6
	wait		5
	collect_list		1
	collect_value		5
	put_value		1,6
	execute		4,wait_send_4_0
wait_send_4_3:
	check_nil		1,wait_send_4_1
	put_list_val_val		1,2,4
	get_list_value		3,1
	proceed
wait_send_4_1:
	suspend		wait_send_4_0
	module_entry		mpimos_cmd_utl
	predicate		check_savedir,5
check_savedir_5_0:
	try_me_else		check_savedir_5_1
	string		1
	put_value		7,1
	g_string		7,6,8
	wait_integer		8,8
	create_goal		7
	set_variable		1,6
	set_value		2,3
	set_variable		3,1
	set_marked_value		4,7
	set_value		5,2
	set_values_inc		6,4,2
	enqueue_goal		7,check_savedir0_7_0
	put_values_dec		2,7,2
	execute_external		mpimos_directory,create,3
check_savedir_5_1:
	otherwise		check_savedir_5_0
	put_values_inc		8,1,2
	put_values_inc		6,4,2
	put_atom		1,fail
	put_value		2,3
	put_void		3
	put_values_inc		4,8,2
	execute		7,check_savedir0_7_0
check_savedir_5_5:
	suspend		check_savedir_5_0
	module_entry		mpimos_cmd_utl
	predicate		check_savedir0,7
check_savedir0_7_0:
	try_me_else		check_savedir0_7_1
	wait_atom		1,success
	collect_value		4
	get_atom		2,success
	put_func		1,2,pathname
	write_element_value		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	get_value		6,7
	proceed
check_savedir0_7_1:
	otherwise		check_savedir0_7_0
	collect_value		3
	collect_value		1
	get_atom		2,fail
	put_structured_constant		1,'$SCNST_0'
	get_value		5,1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_func		2,2,putt
	write_element_value		2,1,4
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_1'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
check_savedir0_7_6:
	suspend		check_savedir0_7_0
	module_entry		mpimos_cmd_utl
	predicate		os_check_loaddir,5
os_check_loaddir_5_0:
	try_me_else		os_check_loaddir_5_1
	string		1
	put_value		7,1
	g_string		7,6,8
	wait_integer		8,8
	put_func		1,2,system_stream
	write_element_variable		1,1,9
	get_list_val_var		4,6,1,8
	create_goal		7
	set_variable		1,6
	set_value		2,3
	set_variable		3,1
	set_marked_value		4,7
	set_value		5,2
	set_value		6,8
	set_value		7,5
	enqueue_goal		7,check_loaddir0_7_0
	put_value		2,7
	put_void		3
	put_value		4,9
	put_nil		5
	execute_external		mpimos_directory,os_create,6
os_check_loaddir_5_1:
	otherwise		os_check_loaddir_5_0
	put_values_inc		8,1,2
	put_values_inc		6,4,2
	put_atom		1,fail
	put_value		2,3
	put_void		3
	put_values_inc		4,8,2
	execute		7,check_loaddir0_7_0
os_check_loaddir_5_5:
	suspend		os_check_loaddir_5_0
	module_entry		mpimos_cmd_utl
	predicate		check_loaddir0,7
check_loaddir0_7_0:
	try_me_else		check_loaddir0_7_1
	wait_atom		1,success
	collect_value		4
	get_atom		2,success
	put_func		1,2,pathname
	write_element_value		1,1,5
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	get_list_value		3,2
	get_value		6,7
	proceed
check_loaddir0_7_1:
	otherwise		check_loaddir0_7_0
	collect_value		3
	collect_value		1
	get_atom		2,fail
	put_structured_constant		1,'$SCNST_2'
	get_value		5,1
	put_func		1,2,flush
	write_element_void		1,1
	put_list		2
	write_car_value		2,1
	write_cdr_nil		2
	put_list		1
	write_car_atom		1,nl
	write_cdr_value		1,2
	put_func		2,2,putt
	write_element_value		2,1,4
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_3'
	put_list_val_val		2,1,3
	put_func		1,2,window
	write_element_value		1,1,2
	put_list_val_val		2,1,7
	get_list_value		6,2
	proceed
check_loaddir0_7_6:
	suspend		check_loaddir0_7_0
	module_entry		mpimos_cmd_utl
	predicate		apply_action,3
apply_action_3_0:
	try_me_else		apply_action_3_1
	jump_on_non_atom		1,apply_action_3_3
	wait_list_var_var		2,4,5
	collect_list		2
	put_vector		7,2
	write_element_variable		7,0,6
	write_element_variable		7,1,2
	get_vector_value		3,7
	create_goal		3
	set_marked_value		1,1
	set_values_inc		2,5,2
	enqueue_goal		3,apply_action_3_0
	create_goal		2
	set_variable		1,3
	set_value		2,2
	enqueue_goal		2,apply_goal_2_0
	put_value		2,4
	execute		3,make_command_3_0
apply_action_3_3:
	check_vector		1,3,apply_action_3_1
	read_element		1,0,4
	wait_atom		4,:
	read_elements_inc		1,1,4,2
	wait_list_var_var		2,6,7
	collect_list		2
	put_vector		9,2
	write_element_variable		9,0,8
	write_element_variable		9,1,2
	get_vector_value		3,9
	create_goal		3
	put_reused_func		1,1,:
	write_element_marked_value		1,1,4
	write_element_marked_value		1,2,5
	set_value		1,1
	set_values_inc		2,7,2
	enqueue_goal		3,apply_action_3_0
	create_goal		2
	put_func		1,3,:
	write_element_value		1,1,4
	write_element_variable		1,2,3
	set_values_inc		1,1,2
	enqueue_goal		2,apply_goal_2_0
	put_values_inc		1,5,2
	execute		3,make_command_3_0
apply_action_3_1:
	try_me_else		apply_action_3_4
	wait_nil		2
	collect_value		1
	get_nil		3
	proceed
apply_action_3_4:
	suspend		apply_action_3_0
	module_entry		mpimos_cmd_utl
	predicate		apply_action,4
apply_action_4_0:
	try_me_else		apply_action_4_1
	jump_on_non_atom		1,apply_action_4_3
	wait_list_var_var		2,5,6
	collect_list		2
	put_vector		8,2
	write_element_variable		8,0,7
	write_element_variable		8,1,2
	get_vector_value		4,8
	create_goal		4
	set_marked_value		1,1
	set_value		2,6
	set_marked_value		3,3
	set_value		4,7
	enqueue_goal		4,apply_action_4_0
	create_goal		2
	set_variable		1,4
	set_value		2,2
	enqueue_goal		2,apply_goal_2_0
	put_value		2,5
	execute		4,make_command_4_0
apply_action_4_3:
	check_vector		1,3,apply_action_4_1
	read_element		1,0,5
	wait_atom		5,:
	read_elements_inc		1,1,5,2
	wait_list_var_var		2,7,8
	collect_list		2
	put_vector		10,2
	write_element_variable		10,0,9
	write_element_variable		10,1,2
	get_vector_value		4,10
	create_goal		4
	put_reused_func		1,1,:
	write_element_marked_value		1,1,5
	write_element_marked_value		1,2,6
	set_value		1,1
	set_value		2,8
	set_marked_value		3,3
	set_value		4,9
	enqueue_goal		4,apply_action_4_0
	create_goal		2
	put_func		1,3,:
	write_element_value		1,1,5
	write_element_variable		1,2,4
	set_values_inc		1,1,2
	enqueue_goal		2,apply_goal_2_0
	put_values_inc		1,6,2
	execute		4,make_command_4_0
apply_action_4_1:
	try_me_else		apply_action_4_4
	wait_nil		2
	collect_value		3
	collect_value		1
	get_nil		4
	proceed
apply_action_4_4:
	suspend		apply_action_4_0
	module_entry		mpimos_cmd_utl
	predicate		apply_goal,2
apply_goal_2_0:
	create_goal		1
	set_variable		1,3
	enqueue_goal_external		mpimos_command_interpreter,apply_goals,1
	execute_external		mpimos_command_interpreter,command_analyzer,3
apply_goal_2_1:
	suspend		apply_goal_2_0
	module_entry		mpimos_cmd_utl
	predicate		make_command,3
make_command_3_0:
	try_me_else		make_command_3_1
	vector		2
	put_value		6,2
	g_vector		6,4
	put_integer		5,0
	g_less_than		5,4
	put_value		7,3
	put_marked_value		2,4
	b_increment		2,2
	b_new_vector		2,2
	put_integer		3,0
	b_set_vector_element		2,3,1,1,5
	put_integer		1,0
	put_value		2,4
	put_values_dec		3,6,2
	put_value		5,7
	execute		5,copy_args_5_0
make_command_3_1:
	put_vector		4,2
	write_elements_inc		4,0,1,2
	get_vector_value		3,4
	proceed
make_command_3_5:
	suspend		make_command_3_0
	module_entry		mpimos_cmd_utl
	predicate		make_command,4
make_command_4_0:
	try_me_else		make_command_4_1
	vector		2
	g_vector		2,5
	put_integer		6,0
	g_less_than		6,5
	put_marked_value		6,5
	b_increment		6,6
	put_variable		8,7
	b_add		6,8,6
	b_new_vector		6,6
	put_integer		8,0
	b_set_vector_element		6,8,1,1,6
	b_increment		5,1
	create_goal		4
	set_variable		1,9
	set_value		2,1
	set_variable		3,8
	set_value		4,4
	enqueue_goal		4,set_option_4_0
	create_goal		5
	set_integer		1,0
	set_value		2,5
	set_value		3,2
	set_value		4,6
	set_value		5,9
	enqueue_goal		5,copy_args_5_0
	put_value		1,3
	put_values_dec		2,8,2
	execute		3,get_option_3_0
make_command_4_1:
	put_integer		5,2
	put_variable		7,6
	b_add		5,7,5
	b_new_vector		5,5
	put_integer		7,0
	b_set_vector_element		5,7,1,1,5
	put_integer		1,1
	b_set_vector_element		5,1,1,2,2
	create_goal		4
	set_value		1,2
	set_integer		2,2
	set_variable		3,2
	set_value		4,4
	enqueue_goal		4,set_option_4_0
	put_value		1,3
	put_value		3,6
	execute		3,get_option_3_0
make_command_4_5:
	suspend		make_command_4_0
	module_entry		mpimos_cmd_utl
	predicate		copy_args,5
copy_args_5_0:
	try_me_else		copy_args_5_1
	integer		1
	integer		2
	g_less_than		1,2
	put_marked_value		6,1
	b_increment		6,6
	put_nil		7
	b_set_vector_element		3,1,1,7,3
	put_marked_value		7,6
	b_set_vector_element		4,7,1,1,4
	put_value		1,6
	execute		5,copy_args_5_0
copy_args_5_1:
	try_me_else		copy_args_5_3
	wait_value		1,2
	collect_value		3
	collect_value		1
	collect_value		2
	get_value		5,4
	proceed
copy_args_5_3:
	suspend		copy_args_5_0
	module_entry		mpimos_cmd_utl
	predicate		get_option,3
get_option_3_0:
	put_value		4,3
	put_integer		3,1
	execute		4,get_option_4_0
get_option_3_1:
	suspend		get_option_3_0
	module_entry		mpimos_cmd_utl
	predicate		get_option,4
get_option_4_0:
	try_me_else		get_option_4_1
	wait_vector		1,3
	read_element		1,0,5
	wait_atom		5,','
	read_elements_inc		1,1,5,2
	collect_vector		1
	get_list_val_var		2,1,5,5
	b_increment		3,1
	put_value		3,1
	put_values_dec		1,6,2
	execute		4,get_option_4_0
get_option_4_1:
	put_list		5
	write_car_value		5,1
	write_cdr_nil		5
	get_list_value		2,5
	get_value		4,3
	proceed
get_option_4_6:
	suspend		get_option_4_0
	module_entry		mpimos_cmd_utl
	predicate		set_option,4
set_option_4_0:
	try_me_else		set_option_4_1
	jump_on_non_list_var_var		3,set_option_4_3,5,6
	collect_list		3
	put_marked_value		3,2
	b_set_vector_element		1,3,1,5,3
	b_increment		2,1
	put_value		2,1
	put_value		1,3
	put_value		3,6
	execute		4,set_option_4_0
set_option_4_3:
	check_nil		3,set_option_4_1
	collect_value		2
	get_value		4,1
	proceed
set_option_4_1:
	suspend		set_option_4_0
	begin_const_section		mpimos_cmd_utl
'$SCNST_0_0':
	define_desc		11,3
	define_integer		1345204094
	define_integer		1934840644
	define_integer		6649441
'$SCNST_2':
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		11,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		1986097952
	define_integer		1919509605
	define_integer		2112800
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_3_1':
	define_desc		11,11
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		1634692128
	define_integer		1919509604
	define_integer		2112800
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
