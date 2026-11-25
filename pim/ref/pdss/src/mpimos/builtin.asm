mpimos_builtin_predicate:
	module		mpimos_builtin_predicate
	entry		is_command,2,is_command_2_0
	entry		do_command,2,do_command_2_0
	entry		help,2,help_2_0
	module_entry		mpimos_builtin_predicate
	predicate		is_command,2
is_command_2_0:
	try_me_else		is_command_2_1
	jump_on_non_atom		1,is_command_2_3
	test_atom		1,true,is_command_2_1
	get_atom		2,yes
	proceed
is_command_2_3:
	is_vector		1,is_command_2_1
	jump_on_arity		1,7,is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_1
	table_entry		is_command_2_4
	table_entry		is_command_2_5
	table_entry		is_command_2_6
	table_entry		is_command_2_7
	table_entry		is_command_2_8
is_command_2_4:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,is_command_2_1
	bucket_entry_a		consume_resource,is_command_2_10
	bucket_entry_a		new_atom,is_command_2_11
is_command_2_10:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_11:
	read_element		1,1,4
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_5:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,33,is_command_2_1
	bucket_entry_a		abs,is_command_2_13
	bucket_entry_a		apply,is_command_2_14
	bucket_entry_a		atom_name,is_command_2_15
	bucket_entry_a		atom_number,is_command_2_16
	bucket_entry_a		complement,is_command_2_17
	bucket_entry_a		current_node,is_command_2_18
	bucket_entry_a		decrement,is_command_2_19
	bucket_entry_a		floating_point_abs,is_command_2_20
	bucket_entry_a		floating_point_acos,is_command_2_21
	bucket_entry_a		floating_point_asin,is_command_2_22
	bucket_entry_a		floating_point_atan,is_command_2_23
	bucket_entry_a		floating_point_cos,is_command_2_24
	bucket_entry_a		floating_point_cosh,is_command_2_25
	bucket_entry_a		floating_point_exp,is_command_2_26
	bucket_entry_a		floating_point_floor,is_command_2_27
	bucket_entry_a		floating_point_ln,is_command_2_28
	bucket_entry_a		floating_point_log,is_command_2_29
	bucket_entry_a		floating_point_minus,is_command_2_30
	bucket_entry_a		floating_point_sin,is_command_2_31
	bucket_entry_a		floating_point_sinh,is_command_2_32
	bucket_entry_a		floating_point_sqrt,is_command_2_33
	bucket_entry_a		floating_point_tan,is_command_2_34
	bucket_entry_a		floating_point_tanh,is_command_2_35
	bucket_entry_a		floating_point_to_integer,is_command_2_36
	bucket_entry_a		increment,is_command_2_37
	bucket_entry_a		integer_to_floating_point,is_command_2_38
	bucket_entry_a		intern_atom,is_command_2_39
	bucket_entry_a		merge,is_command_2_40
	bucket_entry_a		minus,is_command_2_41
	bucket_entry_a		new_vector,is_command_2_42
	bucket_entry_a		string_complement,is_command_2_43
	bucket_entry_a		unbound,is_command_2_44
	bucket_entry_a		unify,is_command_2_45
is_command_2_13:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_14:
	read_elements_inc		1,1,4,2
	vector		5
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_15:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_16:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_17:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_18:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_19:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_20:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_21:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_22:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_23:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_24:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_25:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_26:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_27:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_28:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_29:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_30:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_31:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_32:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_33:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_34:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_35:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_36:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_37:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_38:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_39:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_40:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_41:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_42:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_43:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_44:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_45:
	read_elements_inc		1,1,4,2
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_6:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,27,is_command_2_1
	bucket_entry_a		add,is_command_2_47
	bucket_entry_a		and,is_command_2_48
	bucket_entry_a		append_string,is_command_2_49
	bucket_entry_a		current_priority,is_command_2_50
	bucket_entry_a		current_processor,is_command_2_51
	bucket_entry_a		divide,is_command_2_52
	bucket_entry_a		exclusive_or,is_command_2_53
	bucket_entry_a		floating_point_add,is_command_2_54
	bucket_entry_a		floating_point_atan,is_command_2_55
	bucket_entry_a		floating_point_divide,is_command_2_56
	bucket_entry_a		floating_point_max,is_command_2_57
	bucket_entry_a		floating_point_min,is_command_2_58
	bucket_entry_a		floating_point_multiply,is_command_2_59
	bucket_entry_a		floating_point_pow,is_command_2_60
	bucket_entry_a		floating_point_subtract,is_command_2_61
	bucket_entry_a		hash,is_command_2_62
	bucket_entry_a		max,is_command_2_63
	bucket_entry_a		min,is_command_2_64
	bucket_entry_a		modulo,is_command_2_65
	bucket_entry_a		multiply,is_command_2_66
	bucket_entry_a		new_string,is_command_2_67
	bucket_entry_a		or,is_command_2_68
	bucket_entry_a		raise,is_command_2_69
	bucket_entry_a		shift_left,is_command_2_70
	bucket_entry_a		shift_right,is_command_2_71
	bucket_entry_a		subtract,is_command_2_72
	bucket_entry_a		vector,is_command_2_73
is_command_2_47:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_48:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_49:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_50:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_51:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_52:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_53:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_54:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_55:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_56:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_57:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_58:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_59:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_60:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_61:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_62:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_63:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_64:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_65:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_66:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_67:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_68:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_69:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_70:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_71:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_72:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_73:
	read_elements_inc		1,1,4,3
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_7:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,10,is_command_2_1
	bucket_entry_a		predicate_to_code,is_command_2_75
	bucket_entry_a		set_string_element,is_command_2_76
	bucket_entry_a		set_substring,is_command_2_77
	bucket_entry_a		string,is_command_2_78
	bucket_entry_a		string_and,is_command_2_79
	bucket_entry_a		string_element,is_command_2_80
	bucket_entry_a		string_exclusive_or,is_command_2_81
	bucket_entry_a		string_or,is_command_2_82
	bucket_entry_a		unbound,is_command_2_83
	bucket_entry_a		vector_element,is_command_2_84
is_command_2_75:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_76:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_77:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_78:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_79:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_80:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_81:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_82:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_83:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_84:
	read_elements_inc		1,1,4,4
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_8:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,is_command_2_1
	bucket_entry_a		code_to_predicate,is_command_2_86
	bucket_entry_a		set_vector_element,is_command_2_87
	bucket_entry_a		substring,is_command_2_88
is_command_2_86:
	read_elements_inc		1,1,4,5
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_87:
	read_elements_inc		1,1,4,5
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		5
	collect_value		4
	collect_vector		1
	get_atom		2,yes
	proceed
is_command_2_88:
	read_elements_inc		1,1,4,5
	collect_value		8
	collect_value		7
	collect_value		6
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
is_command_2_103:
	suspend		is_command_2_0
	module_entry		mpimos_builtin_predicate
	predicate		do_command,2
do_command_2_0:
	try_me_else		do_command_2_1
	jump_on_non_atom		1,do_command_2_3
	test_atom		1,true,do_command_2_1
	get_nil		2
	proceed
do_command_2_3:
	is_vector		1,do_command_2_1
	jump_on_arity		1,7,do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_1
	table_entry		do_command_2_4
	table_entry		do_command_2_5
	table_entry		do_command_2_6
	table_entry		do_command_2_7
	table_entry		do_command_2_8
do_command_2_4:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,2,do_command_2_1
	bucket_entry_a		consume_resource,do_command_2_10
	bucket_entry_a		new_atom,do_command_2_11
do_command_2_10:
	read_element		1,1,4
	collect_vector		1
	get_nil		2
	b_consume_resource		4
	proceed
do_command_2_11:
	read_element		1,1,4
	collect_vector		1
	get_nil		2
	b_new_atom		1
	get_value		1,4
	proceed
do_command_2_5:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,33,do_command_2_1
	bucket_entry_a		abs,do_command_2_13
	bucket_entry_a		apply,do_command_2_14
	bucket_entry_a		atom_name,do_command_2_15
	bucket_entry_a		atom_number,do_command_2_16
	bucket_entry_a		complement,do_command_2_17
	bucket_entry_a		current_node,do_command_2_18
	bucket_entry_a		decrement,do_command_2_19
	bucket_entry_a		floating_point_abs,do_command_2_20
	bucket_entry_a		floating_point_acos,do_command_2_21
	bucket_entry_a		floating_point_asin,do_command_2_22
	bucket_entry_a		floating_point_atan,do_command_2_23
	bucket_entry_a		floating_point_cos,do_command_2_24
	bucket_entry_a		floating_point_cosh,do_command_2_25
	bucket_entry_a		floating_point_exp,do_command_2_26
	bucket_entry_a		floating_point_floor,do_command_2_27
	bucket_entry_a		floating_point_ln,do_command_2_28
	bucket_entry_a		floating_point_log,do_command_2_29
	bucket_entry_a		floating_point_minus,do_command_2_30
	bucket_entry_a		floating_point_sin,do_command_2_31
	bucket_entry_a		floating_point_sinh,do_command_2_32
	bucket_entry_a		floating_point_sqrt,do_command_2_33
	bucket_entry_a		floating_point_tan,do_command_2_34
	bucket_entry_a		floating_point_tanh,do_command_2_35
	bucket_entry_a		floating_point_to_integer,do_command_2_36
	bucket_entry_a		increment,do_command_2_37
	bucket_entry_a		integer_to_floating_point,do_command_2_38
	bucket_entry_a		intern_atom,do_command_2_39
	bucket_entry_a		merge,do_command_2_40
	bucket_entry_a		minus,do_command_2_41
	bucket_entry_a		new_vector,do_command_2_42
	bucket_entry_a		string_complement,do_command_2_43
	bucket_entry_a		unbound,do_command_2_44
	bucket_entry_a		unify,do_command_2_45
do_command_2_13:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_abs		4,1
	get_value		1,5
	proceed
do_command_2_14:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_apply		4,5
	proceed
do_command_2_15:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_atom_name		4,1
	get_value		1,5
	proceed
do_command_2_16:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_atom_number		4,1
	get_value		1,5
	proceed
do_command_2_17:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_complement		4,1
	get_value		1,5
	proceed
do_command_2_18:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_current_node		1,2
	get_value		1,4
	get_value		2,5
	proceed
do_command_2_19:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_decrement		4,1
	get_value		1,5
	proceed
do_command_2_20:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_abs		4,1
	get_value		1,5
	proceed
do_command_2_21:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_acos		4,1
	get_value		1,5
	proceed
do_command_2_22:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_asin		4,1
	get_value		1,5
	proceed
do_command_2_23:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_atan		4,1
	get_value		1,5
	proceed
do_command_2_24:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_cos		4,1
	get_value		1,5
	proceed
do_command_2_25:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_cosh		4,1
	get_value		1,5
	proceed
do_command_2_26:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_exp		4,1
	get_value		1,5
	proceed
do_command_2_27:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_floor		4,1
	get_value		1,5
	proceed
do_command_2_28:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_ln		4,1
	get_value		1,5
	proceed
do_command_2_29:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_log		4,1
	get_value		1,5
	proceed
do_command_2_30:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_minus		4,1
	get_value		1,5
	proceed
do_command_2_31:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_sin		4,1
	get_value		1,5
	proceed
do_command_2_32:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_sinh		4,1
	get_value		1,5
	proceed
do_command_2_33:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_sqrt		4,1
	get_value		1,5
	proceed
do_command_2_34:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_tan		4,1
	get_value		1,5
	proceed
do_command_2_35:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_tanh		4,1
	get_value		1,5
	proceed
do_command_2_36:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_float_to_integer		4,1
	get_value		1,5
	proceed
do_command_2_37:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_increment		4,1
	get_value		1,5
	proceed
do_command_2_38:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_integer_to_float		4,1
	get_value		1,5
	proceed
do_command_2_39:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_intern_atom		1,5
	get_value		1,4
	proceed
do_command_2_40:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_merge		1,2
	get_value		1,4
	get_value		2,5
	proceed
do_command_2_41:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_minus		4,1
	get_value		1,5
	proceed
do_command_2_42:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_new_vector		1,5
	get_value		1,4
	proceed
do_command_2_43:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_string_complement		4,1
	get_value		1,5
	proceed
do_command_2_44:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	b_unbound2		4,1
	get_value		1,5
	proceed
do_command_2_45:
	read_elements_inc		1,1,4,2
	collect_vector		1
	get_nil		2
	get_value		4,5
	proceed
do_command_2_6:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,27,do_command_2_1
	bucket_entry_a		add,do_command_2_47
	bucket_entry_a		and,do_command_2_48
	bucket_entry_a		append_string,do_command_2_49
	bucket_entry_a		current_priority,do_command_2_50
	bucket_entry_a		current_processor,do_command_2_51
	bucket_entry_a		divide,do_command_2_52
	bucket_entry_a		exclusive_or,do_command_2_53
	bucket_entry_a		floating_point_add,do_command_2_54
	bucket_entry_a		floating_point_atan,do_command_2_55
	bucket_entry_a		floating_point_divide,do_command_2_56
	bucket_entry_a		floating_point_max,do_command_2_57
	bucket_entry_a		floating_point_min,do_command_2_58
	bucket_entry_a		floating_point_multiply,do_command_2_59
	bucket_entry_a		floating_point_pow,do_command_2_60
	bucket_entry_a		floating_point_subtract,do_command_2_61
	bucket_entry_a		hash,do_command_2_62
	bucket_entry_a		max,do_command_2_63
	bucket_entry_a		min,do_command_2_64
	bucket_entry_a		modulo,do_command_2_65
	bucket_entry_a		multiply,do_command_2_66
	bucket_entry_a		new_string,do_command_2_67
	bucket_entry_a		or,do_command_2_68
	bucket_entry_a		raise,do_command_2_69
	bucket_entry_a		shift_left,do_command_2_70
	bucket_entry_a		shift_right,do_command_2_71
	bucket_entry_a		subtract,do_command_2_72
	bucket_entry_a		vector,do_command_2_73
do_command_2_47:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_add		4,5,1
	get_value		1,6
	proceed
do_command_2_48:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_and		4,5,1
	get_value		1,6
	proceed
do_command_2_49:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_append_string		4,5,1
	get_value		1,6
	proceed
do_command_2_50:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_current_priority		1,2,3
	get_value		1,4
	get_value		2,5
	get_value		3,6
	proceed
do_command_2_51:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_current_processor		1,2,3
	get_value		1,4
	get_value		2,5
	get_value		3,6
	proceed
do_command_2_52:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_divide		4,5,1
	get_value		1,6
	proceed
do_command_2_53:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_exclusive_or		4,5,1
	get_value		1,6
	proceed
do_command_2_54:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_add		4,5,1
	get_value		1,6
	proceed
do_command_2_55:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_atan2		4,5,1
	get_value		1,6
	proceed
do_command_2_56:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_divide		4,5,1
	get_value		1,6
	proceed
do_command_2_57:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_max		4,5,1
	get_value		1,6
	proceed
do_command_2_58:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_min		4,5,1
	get_value		1,6
	proceed
do_command_2_59:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_multiply		4,5,1
	get_value		1,6
	proceed
do_command_2_60:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_pow		4,5,1
	get_value		1,6
	proceed
do_command_2_61:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_float_subtract		4,5,1
	get_value		1,6
	proceed
do_command_2_62:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_hash		4,1,2
	get_value		1,5
	get_value		2,6
	proceed
do_command_2_63:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_max		4,5,1
	get_value		1,6
	proceed
do_command_2_64:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_min		4,5,1
	get_value		1,6
	proceed
do_command_2_65:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_modulo		4,5,1
	get_value		1,6
	proceed
do_command_2_66:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_multiply		4,5,1
	get_value		1,6
	proceed
do_command_2_67:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_new_string		1,5,6
	get_value		1,4
	proceed
do_command_2_68:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_or		4,5,1
	get_value		1,6
	proceed
do_command_2_69:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_raise		4,5,6
	proceed
do_command_2_70:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_shift_left		4,5,1
	get_value		1,6
	proceed
do_command_2_71:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_shift_right		4,5,1
	get_value		1,6
	proceed
do_command_2_72:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_subtract		4,5,1
	get_value		1,6
	proceed
do_command_2_73:
	read_elements_inc		1,1,4,3
	collect_vector		1
	get_nil		2
	b_vector		4,1,2
	get_value		1,5
	get_value		2,6
	proceed
do_command_2_7:
	read_element		1,0,3
	atom		3
	hash_on_atom		3,10,do_command_2_1
	bucket_entry_a		predicate_to_code,do_command_2_75
	bucket_entry_a		set_string_element,do_command_2_76
	bucket_entry_a		set_substring,do_command_2_77
	bucket_entry_a		string,do_command_2_78
	bucket_entry_a		string_and,do_command_2_79
	bucket_entry_a		string_element,do_command_2_80
	bucket_entry_a		string_exclusive_or,do_command_2_81
	bucket_entry_a		string_or,do_command_2_82
	bucket_entry_a		unbound,do_command_2_83
	bucket_entry_a		vector_element,do_command_2_84
do_command_2_75:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_predicate_to_code		4,5,6,1
	get_value		1,7
	proceed
do_command_2_76:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_set_string_element		4,5,6,1
	get_value		1,7
	proceed
do_command_2_77:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_set_substring		4,5,6,1
	get_value		1,7
	proceed
do_command_2_78:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_string		4,1,2,3
	get_value		1,5
	get_value		2,6
	get_value		3,7
	proceed
do_command_2_79:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_string_and		4,5,1,2
	get_value		1,6
	get_value		2,7
	proceed
do_command_2_80:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_string_element		4,5,1,2
	get_value		1,6
	get_value		2,7
	proceed
do_command_2_81:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_string_exclusive_or		4,5,1,2
	get_value		1,6
	get_value		2,7
	proceed
do_command_2_82:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_string_or		4,5,1,2
	get_value		1,6
	get_value		2,7
	proceed
do_command_2_83:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_unbound		4,1,2,3
	get_value		1,5
	get_value		2,6
	get_value		3,7
	proceed
do_command_2_84:
	read_elements_inc		1,1,4,4
	collect_vector		1
	get_nil		2
	b_vector_element		4,5,1,2
	get_value		1,6
	get_value		2,7
	proceed
do_command_2_8:
	read_element		1,0,3
	atom		3
	branch_on_atom		3,3,do_command_2_1
	bucket_entry_a		code_to_predicate,do_command_2_86
	bucket_entry_a		set_vector_element,do_command_2_87
	bucket_entry_a		substring,do_command_2_88
do_command_2_86:
	read_elements_inc		1,1,4,5
	collect_vector		1
	get_nil		2
	b_code_to_predicate		4,1,2,3,4
	get_value		1,5
	get_value		2,6
	get_value		3,7
	get_value		4,8
	proceed
do_command_2_87:
	read_elements_inc		1,1,4,5
	collect_vector		1
	get_nil		2
	b_set_vector_element		4,5,1,7,2
	get_value		1,6
	get_value		2,8
	proceed
do_command_2_88:
	read_elements_inc		1,1,4,5
	collect_vector		1
	get_nil		2
	b_substring		4,5,6,1,2
	get_value		1,7
	get_value		2,8
	proceed
do_command_2_1:
	suspend		do_command_2_0
	module_entry		mpimos_builtin_predicate
	predicate		help,2
help_2_0:
	try_me_else		help_2_1
	atom		1
	branch_on_atom		1,3,help_2_1
	bucket_entry_a		item,help_2_3
	bucket_entry_a		menu,help_2_4
	bucket_entry_a		message,help_2_5
help_2_3:
	get_atom		2,builtin
	proceed
help_2_4:
	put_structured_constant		1,'$SCNST_0'
	get_value		2,1
	proceed
help_2_5:
	put_structured_constant		1,'$SCNST_1'
	get_value		2,1
	proceed
help_2_1:
	suspend		help_2_0
	begin_const_section		mpimos_builtin_predicate
'$SCNST_0_0':
	define_desc		19,7
	define_integer		1818850658
	define_integer		544106868
	define_integer		1684370032
	define_integer		1952539497
	define_integer		673215333
	define_integer		2036625250
	define_integer		11817
'$SCNST_0':
	define_string		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		3,12
	define_integer		544567129
	define_integer		544104803
	define_integer		543519605
	define_integer		2036625250
	define_integer		1769300512
	define_integer		1852404844
	define_integer		1701998624
	define_integer		1633904996
	define_integer		544433524
	define_integer		1663071073
	define_integer		1634561391
	define_integer		779314286
'$SCNST_1_3':
	define_desc		11,9
	define_integer		1769170242
	define_integer		539780452
	define_integer		1919248500
	define_integer		1918967909
	define_integer		1868963941
	define_integer		2003790956
	define_integer		543649385
	define_integer		1919115629
	define_integer		3044207
'$SCNST_1_5':
	define_desc		3,10
	define_integer		1718185557
	define_integer		1952539497
	define_integer		544108393
	define_integer		757935392
	define_integer		1853169696
	define_integer		679044713
	define_integer		692202561
	define_integer		1919885344
	define_integer		541138976
	define_integer		776085565
'$SCNST_1_7':
	define_desc		27,6
	define_integer		1953067585
	define_integer		1952804200
	define_integer		1159750505
	define_integer		1701998712
	define_integer		1869181811
	define_integer		110
'$SCNST_1_9':
	define_desc		11,12
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757935392
	define_integer		541138976
	define_integer		1008745786
	define_integer		1953067617
	define_integer		1952804200
	define_integer		1696621417
	define_integer		1701998712
	define_integer		1869181811
	define_integer		3030638
'$SCNST_1_11':
	define_desc		3,9
	define_integer		1634692166
	define_integer		1735289204
	define_integer		1768902688
	define_integer		1092645998
	define_integer		1752459634
	define_integer		1769235821
	define_integer		2017796195
	define_integer		1936028272
	define_integer		1852795251
'$SCNST_1_13':
	define_desc		3,12
	define_integer		538976288
	define_integer		538976288
	define_integer		538976288
	define_integer		757935392
	define_integer		541138976
	define_integer		540883492
	define_integer		1769103676
	define_integer		1701668980
	define_integer		543385972
	define_integer		1919973477
	define_integer		1769173861
	define_integer		775843439
'$SCNST_1_12':
	define_string		'$SCNST_1_13'
	define_atom		[]
'$SCNST_1_10':
	define_string		'$SCNST_1_11'
	define_list		'$SCNST_1_12'
'$SCNST_1_8':
	define_string		'$SCNST_1_9'
	define_list		'$SCNST_1_10'
'$SCNST_1_6':
	define_string		'$SCNST_1_7'
	define_list		'$SCNST_1_8'
'$SCNST_1_4':
	define_string		'$SCNST_1_5'
	define_list		'$SCNST_1_6'
'$SCNST_1_2':
	define_string		'$SCNST_1_3'
	define_list		'$SCNST_1_4'
'$SCNST_1_0':
	define_string		'$SCNST_1_1'
	define_list		'$SCNST_1_2'
'$SCNST_1':
	define_list		'$SCNST_1_0'
