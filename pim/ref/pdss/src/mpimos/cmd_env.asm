mpimos_cmd_environment:
	module		mpimos_cmd_environment
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_cmd_environment
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	branch_on_atom		1,2,is_command_2_1
	bucket_entry_a		printenv,is_command_2_4
	bucket_entry_a		resetenv,is_command_2_5
is_command_2_4:
	get_atom		2,yes
	proceed
is_command_2_5:
	get_atom		2,yes
	proceed
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,4,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_6
	table_entry		is_command_2_7
is_command_2_6:
	read_element		1,0,3
	wait_atom		3,printenv
	read_element		1,1,3
	collect_value		3
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_7:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,is_command_2_1
	bucket_entry_a		getenv,is_command_2_9
	bucket_entry_a		setenv,is_command_2_10
is_command_2_9:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_10:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_1:
	otherwise		is_command_2_0
	collect_value		1
	get_atom		2,no
	proceed
is_command_2_16:
	suspend		is_command_2_0
	module_entry		mpimos_cmd_environment
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	branch_on_atom		1,2,do_command_2_1
	bucket_entry_a		printenv,do_command_2_4
	bucket_entry_a		resetenv,do_command_2_5
do_command_2_4:
	put_func		1,2,getenv
	write_element_variable		1,1,3
	get_list_val_var		2,4,1,1
	put_value		2,3
	execute		2,print_env_2_0
do_command_2_5:
	put_func		1,2,pathname
	write_element_variable		1,1,4
	put_list		3
	write_car_value		3,1
	write_cdr_nil		3
	put_func		1,2,directory
	write_element_value		1,1,3
	get_list_val_var		2,3,1,1
	put_structured_constant		2,'$SCNST_0'
	put_value		3,4
	execute_external		mpimos_command_interpreter,initenv,3
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,4,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_6
	table_entry		do_command_2_7
do_command_2_6:
	read_element		1,0,3
	wait_atom		3,printenv
	read_element		1,1,4
	jump_on_non_list		4,do_command_2_10
	collect_vector		1
	put_value		3,2
	put_atom		1,printenv
	put_value		2,4
	execute_external		mpimos_cmd_utl,apply_action,3
do_command_2_10:
	is_atom		4,do_command_2_1
	test_nil		4,do_command_2_11
	collect_vector		1
	get_nil		2
	proceed
do_command_2_11:
	put_nil		5
	g_diff		4,5
	collect_value		5
	put_reused_func		1,1,getenv
	write_element_variable		1,1,5
	get_list_val_var		2,3,1,1
	create_goal		3
	set_value		1,1
	set_marked_value		2,4
	set_variable		3,3
	enqueue_goal		3,is_print_member_3_0
	put_values_inc		1,4,2
	execute		3,member_3_0
do_command_2_7:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,do_command_2_1
	bucket_entry_a		getenv,do_command_2_13
	bucket_entry_a		setenv,do_command_2_14
do_command_2_13:
	read_elements_inc		1,1,4,2
	atom		4
	collect_vector		1
	put_func		1,2,getenv
	write_element_variable		1,1,6
	get_list_val_var		2,3,1,1
	create_goal		4
	set_value		1,1
	set_value		2,5
	set_marked_value		3,4
	set_variable		4,3
	enqueue_goal		4,is_getenv_member_4_0
	put_value		1,4
	put_value		2,6
	execute		3,member_3_0
do_command_2_14:
	read_elements_inc		1,1,4,2
	atom		4
	collect_vector		1
	put_func		1,2,getenv
	write_element_variable		1,1,6
	get_list_val_var		2,3,1,1
	create_goal		4
	set_value		1,1
	set_value		2,5
	set_marked_value		3,4
	set_variable		4,3
	enqueue_goal		4,is_setenv_member_4_0
	put_value		1,4
	put_value		2,6
	execute		3,member_3_0
do_command_2_1:
	otherwise		do_command_2_0
	create_goal		1
	set_variable		1,7
	enqueue_goal		1,fail_action_1_0
	create_goal		3
	put_structured_constant		3,'$SCNST_1'
	put_func		4,2,putt
	write_element_variable		4,1,6
	put_list_val_val		5,4,3
	put_structured_constant		3,'$SCNST_2'
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
do_command_2_27:
	suspend		do_command_2_0
	module_entry		mpimos_cmd_environment
	predicate		member,3
member_3_0:
	try_me_else		member_3_1
	jump_on_non_list_var_var		2,member_3_3,4,5
	try_me_else		member_3_4
	g_diff		1,4
	collect_list		2
	collect_value		4
	put_value		2,5
	execute		3,member_3_0
member_3_4:
	try_me_else		member_3_1
	wait_value		1,4
	collect_list		2
	collect_value		5
	collect_value		1
	collect_value		4
	get_atom		3,true
	proceed
member_3_3:
	check_nil		2,member_3_1
	collect_value		1
	get_atom		3,false
	proceed
member_3_1:
	suspend		member_3_0
	module_entry		mpimos_cmd_environment
	predicate		is_setenv_member,4
is_setenv_member_4_0:
	try_me_else		is_setenv_member_4_1
	wait		2
	wait		3
	wait_atom		4,true
	put_value		4,1
	put_func		1,3,setenv
	write_elements_dec		1,1,3,2
	put_value		2,4
	put_structured_constant		3,'$SCNST_3'
	execute_external		mpimos_cmd_utl,send_shell,3
is_setenv_member_4_1:
	try_me_else		is_setenv_member_4_3
	wait		3
	wait_atom		4,false
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	put_structured_constant		2,'$SCNST_4'
	put_list_val_val		4,2,3
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_void		1
	put_value		2,5
	execute		2,raise_fail_2_0
is_setenv_member_4_3:
	suspend		is_setenv_member_4_0
	module_entry		mpimos_cmd_environment
	predicate		is_getenv_member,4
is_getenv_member_4_0:
	try_me_else		is_getenv_member_4_1
	wait		3
	atom		4
	branch_on_atom		4,2,is_getenv_member_4_1
	bucket_entry_a		false,is_getenv_member_4_3
	bucket_entry_a		true,is_getenv_member_4_4
is_getenv_member_4_3:
	collect_value		2
	put_func		2,2,flush
	write_element_variable		2,1,5
	put_list		4
	write_car_value		4,2
	write_cdr_nil		4
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_func		4,2,putt
	write_element_value		4,1,3
	put_list_val_val		3,4,2
	put_structured_constant		2,'$SCNST_5'
	put_list_val_val		4,2,3
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,5
	execute		1,wait_1_0
is_getenv_member_4_4:
	put_func		4,3,getenv
	write_element_value		4,1,3
	write_element_variable		4,2,3
	put_list		5
	write_car_value		5,4
	write_cdr_nil		5
	get_list_value		1,5
	put_value		1,3
	execute_external		mpimos_cmd_utl,protect,2
is_getenv_member_4_1:
	suspend		is_getenv_member_4_0
	module_entry		mpimos_cmd_environment
	predicate		is_print_member,3
is_print_member_3_0:
	try_me_else		is_print_member_3_1
	wait		2
	wait_atom		3,false
	put_func		3,2,flush
	write_element_variable		3,1,5
	put_list		4
	write_car_value		4,3
	write_cdr_nil		4
	put_list		3
	write_car_atom		3,nl
	write_cdr_value		3,4
	put_func		4,2,putt
	write_element_value		4,1,2
	put_list_val_val		2,4,3
	put_structured_constant		3,'$SCNST_6'
	put_list_val_val		4,3,2
	put_func		2,2,window
	write_element_value		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_void		1
	put_value		2,5
	execute		2,raise_fail_2_0
is_print_member_3_1:
	try_me_else		is_print_member_3_3
	wait_atom		3,true
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_value		2,3
	execute		2,print_env_2_0
is_print_member_3_3:
	suspend		is_print_member_3_0
	module_entry		mpimos_cmd_environment
	predicate		print_env,2
print_env_2_0:
	try_me_else		print_env_2_1
	jump_on_non_list_var_var		2,print_env_2_3,3,4
	atom		3
	put_func		5,3,getenv
	write_element_marked_value		5,1,3
	write_element_variable		5,2,6
	get_reused_list_val_var		1,7,2,5,2
	put_value		1,2
	put_value		2,6
	execute		4,print_env0_4_0
print_env_2_3:
	check_nil		2,print_env_2_1
	put_func		2,2,flush
	write_element_variable		2,1,4
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	put_func		2,2,window
	write_element_value		2,1,3
	put_list		3
	write_car_value		3,2
	write_cdr_nil		3
	get_list_value		1,3
	put_value		1,4
	execute		1,wait_1_0
print_env_2_1:
	suspend		print_env_2_0
	module_entry		mpimos_cmd_environment
	predicate		print_env0,4
print_env0_4_0:
	try_me_else		print_env0_4_1
	wait		2
	put_structured_constant		5,'$SCNST_7'
	put_func		6,2,putt
	write_element_value		6,1,2
	put_list_val_val		2,6,5
	put_structured_constant		5,'$SCNST_8'
	put_list_val_val		6,5,2
	put_func		2,2,putt
	write_element_value		2,1,3
	put_list_val_val		3,2,6
	put_func		2,2,window
	write_element_value		2,1,3
	get_list_val_var		1,3,2,2
	put_value		1,2
	put_value		2,4
	execute		2,print_env_2_0
print_env0_4_1:
	suspend		print_env0_4_0
	module_entry		mpimos_cmd_environment
	predicate		wait,1
wait_1_0:
	try_me_else		wait_1_1
	wait		1
	proceed
wait_1_1:
	suspend		wait_1_0
	module_entry		mpimos_cmd_environment
	predicate		raise_fail,2
raise_fail_2_0:
	try_me_else		raise_fail_2_1
	wait_atom		2,done
	put_integer		3,131072
	put_structured_constant		2,'$SCNST_9'
	b_raise		3,2,1
	proceed
raise_fail_2_1:
	suspend		raise_fail_2_0
	module_entry		mpimos_cmd_environment
	predicate		fail_action,1
fail_action_1_0:
	try_me_else		fail_action_1_1
	wait		1
	put_integer		2,131072
	put_structured_constant		1,'$SCNST_10'
	put_void		3
	b_raise		2,1,3
	proceed
fail_action_1_1:
	suspend		fail_action_1_0
	module_entry		mpimos_cmd_environment
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,env
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_11'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_12'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_cmd_environment
'$SCNST_0_0':
	define_atom		initenv
	define_atom		[]
'$SCNST_3':
'$SCNST_0':
	define_list		'$SCNST_0_0'
'$SCNST_1_0':
	define_atom		nl
	define_atom		[]
'$SCNST_7':
'$SCNST_1':
	define_list		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		19,7
	define_integer		1969713729
	define_integer		1953391981
	define_integer		1869771333
	define_integer		1701060722
	define_integer		1952671092
	define_integer		1763730533
	define_integer		8302
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_4_1':
	define_desc		27,9
	define_integer		1701604425
	define_integer		543973735
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		976894496
	define_integer		32
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_4_1'
'$SCNST_6':
'$SCNST_5':
'$SCNST_4':
	define_vector		'$SCNST_4_0'
'$SCNST_8_1':
	define_desc		11,1
	define_integer		2112800
'$SCNST_8_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_8_1'
'$SCNST_8':
	define_vector		'$SCNST_8_0'
'$SCNST_9_0':
	define_desc		0,2
	define_atom		shell
	define_atom		fail
'$SCNST_10':
'$SCNST_9':
	define_vector		'$SCNST_9_0'
'$SCNST_11_0':
	define_desc		3,9
	define_integer		1702126963
	define_integer		1730967150
	define_integer		1852142693
	define_integer		1919954038
	define_integer		1702129257
	define_integer		1915516526
	define_integer		1952805733
	define_integer		745959013
	define_integer		778269797
'$SCNST_11':
	define_string		'$SCNST_11_0'
'$SCNST_12_1':
	define_desc		27,11
	define_integer		1919248468
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1835888483
	define_integer		1935961697
	define_integer		46
'$SCNST_12_3':
	define_desc		19,16
	define_integer		1702126963
	define_integer		1311274606
	define_integer		742739265
	define_integer		1431060822
	define_integer		757082437
	define_integer		1394617645
	define_integer		1444967525
	define_integer		1163217985
	define_integer		544175136
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		1296125472
	define_integer		11845
'$SCNST_12_5':
	define_desc		19,16
	define_integer		1702126951
	define_integer		1311274606
	define_integer		742739265
	define_integer		1431060822
	define_integer		757082437
	define_integer		1193291053
	define_integer		1444967525
	define_integer		1163217985
	define_integer		543584032
	define_integer		1769369189
	define_integer		1835954034
	define_integer		544501349
	define_integer		1769103734
	define_integer		1701601889
	define_integer		1296125472
	define_integer		11845
'$SCNST_12_7':
	define_desc		3,16
	define_integer		1852404336
	define_integer		1986946420
	define_integer		1296125480
	define_integer		538978629
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1818326560
	define_integer		1864394101
	define_integer		1852121190
	define_integer		1869769078
	define_integer		1852140910
	define_integer		1635131508
	define_integer		1650551154
	define_integer		1310745964
	define_integer		776293697
'$SCNST_12_9':
	define_desc		27,17
	define_integer		1852404336
	define_integer		1986946420
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1344285997
	define_integer		1953393010
	define_integer		1818326560
	define_integer		544433525
	define_integer		1629513327
	define_integer		1696623724
	define_integer		1919514222
	define_integer		1701670511
	define_integer		1981838446
	define_integer		1634300513
	define_integer		1936026722
	define_integer		46
'$SCNST_12_11':
	define_desc		27,17
	define_integer		1702061426
	define_integer		1986946420
	define_integer		538976288
	define_integer		538976288
	define_integer		757080096
	define_integer		1377840429
	define_integer		1952805733
	define_integer		1818326560
	define_integer		544433525
	define_integer		1629513327
	define_integer		1696623724
	define_integer		1919514222
	define_integer		1701670511
	define_integer		1981838446
	define_integer		1634300513
	define_integer		1936026722
	define_integer		46
'$SCNST_12_10':
	define_string		'$SCNST_12_11'
	define_atom		[]
'$SCNST_12_8':
	define_string		'$SCNST_12_9'
	define_list		'$SCNST_12_10'
'$SCNST_12_6':
	define_string		'$SCNST_12_7'
	define_list		'$SCNST_12_8'
'$SCNST_12_4':
	define_string		'$SCNST_12_5'
	define_list		'$SCNST_12_6'
'$SCNST_12_2':
	define_string		'$SCNST_12_3'
	define_list		'$SCNST_12_4'
'$SCNST_12_0':
	define_string		'$SCNST_12_1'
	define_list		'$SCNST_12_2'
'$SCNST_12':
	define_list		'$SCNST_12_0'
