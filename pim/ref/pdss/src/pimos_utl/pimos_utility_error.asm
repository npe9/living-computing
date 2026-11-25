pimos_utility_error:
	module		pimos_utility_error
	entry		error,3,error_3_0
	module_entry		pimos_utility_error
	predicate		error,3
error_3_0:
	create_goal		3
	set_values_inc		1,1,2
	set_variable		3,2
	enqueue_goal		3,shoen_raise_3_0
	put_value		1,3
	execute_external		mpimos_utility,freeze,2
error_3_1:
	suspend		error_3_0
	module_entry		pimos_utility_error
	predicate		shoen_raise,3
shoen_raise_3_0:
	try_me_else		shoen_raise_3_1
	wait		3
	put_integer		6,262144
	put_atom		7,error
	put_structured_constant		4,'$SCNST_0'
	put_func		5,2,puttq
	write_element_value		5,1,3
	put_list_val_val		3,5,4
	put_structured_constant		4,'$SCNST_1'
	put_list_val_val		5,4,3
	put_func		3,2,putl
	write_element_value		3,1,2
	put_list_val_val		2,3,5
	put_structured_constant		3,'$SCNST_2'
	put_list_val_val		4,3,2
	put_list		2
	write_car_atom		2,nl
	write_cdr_value		2,4
	put_func		3,2,putt
	write_element_value		3,1,1
	put_list_val_val		1,3,2
	put_structured_constant		2,'$SCNST_3'
	put_list_val_val		3,2,1
	put_structured_constant		1,'$SCNST_4'
	put_list_val_val		2,1,3
	b_raise		6,7,2
	proceed
shoen_raise_3_1:
	suspend		shoen_raise_3_0
	begin_const_section		pimos_utility_error
'$SCNST_0_0':
	define_atom		nl
	define_atom		[]
'$SCNST_0':
	define_list		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		3,2
	define_integer		1952531488
	define_integer		540942433
'$SCNST_1_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
'$SCNST_2_1':
	define_desc		3,2
	define_integer		1718503712
	define_integer		540942447
'$SCNST_2_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_2_1'
'$SCNST_2':
	define_vector		'$SCNST_2_0'
'$SCNST_3_1':
	define_desc		3,2
	define_integer		1869771333
	define_integer		540950130
'$SCNST_3_0':
	define_desc		0,2
	define_atom		putb
	define_string		'$SCNST_3_1'
'$SCNST_3':
	define_vector		'$SCNST_3_0'
'$SCNST_4_1':
	define_desc		11,8
	define_integer		1330465104
	define_integer		1414868307
	define_integer		1414089801
	define_integer		1919230041
	define_integer		544370546
	define_integer		1869636978
	define_integer		1684370546
	define_integer		2171168
'$SCNST_4_0':
	define_desc		0,2
	define_atom		putl
	define_string		'$SCNST_4_1'
'$SCNST_4':
	define_vector		'$SCNST_4_0'
