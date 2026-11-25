quick_sort:
	module		quick_sort
	entry		sort,3,sort_3_0
	entry		key_sort,3,key_sort_3_0
	module_entry		quick_sort
	predicate		sort,3
sort_3_0:
	put_nil		4
	execute		4,sort_4_0
sort_3_1:
	suspend		sort_3_0
	module_entry		quick_sort
	predicate		sort,4
sort_4_0:
	try_me_else		sort_4_1
	jump_on_non_list_var_var		1,sort_4_3,5,6
	put_value		8,2
	create_goal		4
	set_variable		1,10
	set_marked_value		2,8
	set_variable		3,7
	set_value		4,4
	enqueue_goal		4,sort_4_0
	create_goal		4
	set_variable		1,4
	set_value		2,8
	set_value		3,3
	put_reused_list		1,1
	write_car_variable		1,3
	write_cdr_variable		1,9
	set_value		4,1
	enqueue_goal		4,sort_4_0
	put_values_dec		1,6,2
	put_values_dec		5,10,2
	execute		8,part_8_0
sort_4_3:
	check_nil		1,sort_4_1
	collect_value		2
	get_value		3,4
	proceed
sort_4_1:
	suspend		sort_4_0
	module_entry		quick_sort
	predicate		part,8
part_8_0:
	try_me_else		part_8_1
	atom		2
	atom		8
	branch_on_atom		8,2,part_8_1
	bucket_entry_a		ascending,part_8_4
	bucket_entry_a		descending,part_8_5
part_8_4:
	g_tag_and_value		2,8,9
	put_value		8,9
	execute		8,part_atom_8_0
part_8_5:
	g_tag_and_value		2,8,9
	put_value		8,9
	execute		8,part_descending_atom_8_0
part_8_1:
	otherwise		part_8_0
	try_me_else		part_8_9
	jump_on_non_atom		8,part_8_11
	branch_on_atom		8,2,part_8_9
	bucket_entry_a		ascending,part_8_12
	bucket_entry_a		descending,part_8_13
part_8_12:
	execute		7,part_7_0
part_8_13:
	execute		7,part_descending_7_0
part_8_11:
	check_vector		8,3,part_8_9
	read_elements_inc		8,0,9,3
	atom		9
	atom		10
	integer		11
	put_reused_vector		8,8
	write_elements_inc		8,0,9,3
	execute		8,part_user_defined_8_0
part_8_9:
	suspend		part_8_0
	module_entry		quick_sort
	predicate		part,7
part_7_0:
	try_me_else		part_7_1
	jump_on_non_list		1,part_7_3
	read_car		1,8
	try_me_else		part_7_4
	jump_on_non_integer		8,part_7_6
	read_cdr		1,9
	integer		2
	try_me_else		part_7_8
	g_less_than		8,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,9
	put_value		4,8
	execute		7,part_7_0
part_7_8:
	try_me_else		part_7_4
	g_less_than		2,8
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,9
	put_value		5,8
	execute		7,part_7_0
part_7_6:
	is_float		8,part_7_4
	read_cdr		1,9
	float		2
	try_me_else		part_7_10
	g_float_less_than		8,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,9
	put_value		4,8
	execute		7,part_7_0
part_7_10:
	try_me_else		part_7_4
	g_float_less_than		2,8
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,9
	put_value		5,8
	execute		7,part_7_0
part_7_4:
	read_cdr		1,9
	try_me_else		part_7_1
	wait_value		2,8
	collect_value		8
	put_reused_list		1,1
	write_car_marked_value		1,2
	write_cdr_variable		1,8
	get_list_value		6,1
	put_value		1,9
	put_value		6,8
	execute		7,part_7_0
part_7_3:
	check_nil		1,part_7_1
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
part_7_1:
	otherwise		part_7_0
	try_me_else		part_7_24
	wait_list_var_var		1,8,9
	collect_list		1
	create_goal		9
	set_value		1,9
	set_variable		2,9
	set_values_inc		3,3,5
	set_variable		8,3
	set_variable		9,5
	enqueue_goal		9,wait_comp_9_0
	put_value		1,8
	put_value		4,9
	execute_external		comparator,sort0,5
part_7_24:
	suspend		part_7_0
	module_entry		quick_sort
	predicate		wait_comp,9
wait_comp_9_0:
	try_me_else		wait_comp_9_1
	atom		9
	branch_on_atom		9,2,wait_comp_9_1
	bucket_entry_a		greater,wait_comp_9_3
	bucket_entry_a		less,wait_comp_9_4
wait_comp_9_3:
	get_list_val_var		5,9,8,8
	put_value		5,8
	execute		7,part_7_0
wait_comp_9_4:
	get_list_val_var		4,9,8,8
	put_value		4,8
	execute		7,part_7_0
wait_comp_9_1:
	suspend		wait_comp_9_0
	module_entry		quick_sort
	predicate		part_atom,8
part_atom_8_0:
	try_me_else		part_atom_8_1
	jump_on_non_list		1,part_atom_8_3
	read_car		1,9
	atom		9
	read_cdr		1,10
	integer		8
	try_me_else		part_atom_8_6
	g_tag_and_value		9,11,12
	wait_value		12,8
	get_reused_list_val_var		6,1,1,9,9
	put_value		1,10
	put_value		6,9
	execute		8,part_atom_8_0
part_atom_8_6:
	try_me_else		part_atom_8_7
	g_tag_and_value		9,11,12
	g_less_than		12,8
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,10
	put_value		4,9
	execute		8,part_atom_8_0
part_atom_8_7:
	try_me_else		part_atom_8_1
	g_tag_and_value		9,11,12
	g_less_than		8,12
	get_reused_list_val_var		5,1,1,9,9
	put_value		1,10
	put_value		5,9
	execute		8,part_atom_8_0
part_atom_8_3:
	check_nil		1,part_atom_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
part_atom_8_1:
	otherwise		part_atom_8_0
	try_me_else		part_atom_8_16
	wait_list_var_var		1,9,10
	collect_list		1
	create_goal		10
	set_value		1,10
	set_variable		2,10
	set_values_inc		3,3,6
	set_variable		9,3
	set_variable		10,5
	enqueue_goal		10,wait_comp_atom_10_0
	put_value		1,9
	put_value		4,10
	execute_external		comparator,sort0,5
part_atom_8_16:
	suspend		part_atom_8_0
	module_entry		quick_sort
	predicate		wait_comp_atom,10
wait_comp_atom_10_0:
	try_me_else		wait_comp_atom_10_1
	atom		10
	branch_on_atom		10,2,wait_comp_atom_10_1
	bucket_entry_a		greater,wait_comp_atom_10_3
	bucket_entry_a		less,wait_comp_atom_10_4
wait_comp_atom_10_3:
	get_list_val_var		5,10,9,9
	put_value		5,9
	execute		8,part_atom_8_0
wait_comp_atom_10_4:
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,part_atom_8_0
wait_comp_atom_10_1:
	suspend		wait_comp_atom_10_0
	module_entry		quick_sort
	predicate		part_descending,7
part_descending_7_0:
	try_me_else		part_descending_7_1
	jump_on_non_list		1,part_descending_7_3
	read_car		1,8
	try_me_else		part_descending_7_4
	jump_on_non_integer		8,part_descending_7_6
	read_cdr		1,9
	integer		2
	try_me_else		part_descending_7_8
	g_less_than		2,8
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,9
	put_value		4,8
	execute		7,part_descending_7_0
part_descending_7_8:
	try_me_else		part_descending_7_4
	g_less_than		8,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,9
	put_value		5,8
	execute		7,part_descending_7_0
part_descending_7_6:
	is_float		8,part_descending_7_4
	read_cdr		1,9
	float		2
	try_me_else		part_descending_7_10
	g_float_less_than		2,8
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,9
	put_value		4,8
	execute		7,part_descending_7_0
part_descending_7_10:
	try_me_else		part_descending_7_4
	g_float_less_than		8,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,9
	put_value		5,8
	execute		7,part_descending_7_0
part_descending_7_4:
	read_cdr		1,9
	try_me_else		part_descending_7_1
	wait_value		2,8
	collect_value		8
	put_reused_list		1,1
	write_car_marked_value		1,2
	write_cdr_variable		1,8
	get_list_value		6,1
	put_value		1,9
	put_value		6,8
	execute		7,part_descending_7_0
part_descending_7_3:
	check_nil		1,part_descending_7_1
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
part_descending_7_1:
	otherwise		part_descending_7_0
	try_me_else		part_descending_7_24
	wait_list_var_var		1,8,9
	collect_list		1
	create_goal		9
	set_value		1,9
	set_variable		2,9
	set_values_inc		3,3,5
	set_variable		8,3
	set_variable		9,5
	enqueue_goal		9,wait_comp_descending_9_0
	put_value		1,8
	put_value		4,9
	execute_external		comparator,sort0,5
part_descending_7_24:
	suspend		part_descending_7_0
	module_entry		quick_sort
	predicate		wait_comp_descending,9
wait_comp_descending_9_0:
	try_me_else		wait_comp_descending_9_1
	atom		9
	branch_on_atom		9,2,wait_comp_descending_9_1
	bucket_entry_a		greater,wait_comp_descending_9_3
	bucket_entry_a		less,wait_comp_descending_9_4
wait_comp_descending_9_3:
	get_list_val_var		4,9,8,8
	put_value		4,8
	execute		7,part_descending_7_0
wait_comp_descending_9_4:
	get_list_val_var		5,9,8,8
	put_value		5,8
	execute		7,part_descending_7_0
wait_comp_descending_9_1:
	suspend		wait_comp_descending_9_0
	module_entry		quick_sort
	predicate		part_descending_atom,8
part_descending_atom_8_0:
	try_me_else		part_descending_atom_8_1
	jump_on_non_list		1,part_descending_atom_8_3
	read_car		1,9
	atom		9
	read_cdr		1,10
	integer		8
	try_me_else		part_descending_atom_8_6
	g_tag_and_value		9,11,12
	wait_value		12,8
	get_reused_list_val_var		6,1,1,9,9
	put_value		1,10
	put_value		6,9
	execute		8,part_descending_atom_8_0
part_descending_atom_8_6:
	try_me_else		part_descending_atom_8_7
	g_tag_and_value		9,11,12
	g_less_than		8,12
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,10
	put_value		4,9
	execute		8,part_descending_atom_8_0
part_descending_atom_8_7:
	try_me_else		part_descending_atom_8_1
	g_tag_and_value		9,11,12
	g_less_than		12,8
	get_reused_list_val_var		5,1,1,9,9
	put_value		1,10
	put_value		5,9
	execute		8,part_descending_atom_8_0
part_descending_atom_8_3:
	check_nil		1,part_descending_atom_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
part_descending_atom_8_1:
	otherwise		part_descending_atom_8_0
	try_me_else		part_descending_atom_8_16
	wait_list_var_var		1,9,10
	collect_list		1
	create_goal		10
	set_value		1,10
	set_variable		2,10
	set_values_inc		3,3,6
	set_variable		9,3
	set_variable		10,5
	enqueue_goal		10,wait_comp_descending_atom_10_0
	put_value		1,9
	put_value		4,10
	execute_external		comparator,sort0,5
part_descending_atom_8_16:
	suspend		part_descending_atom_8_0
	module_entry		quick_sort
	predicate		wait_comp_descending_atom,10
wait_comp_descending_atom_10_0:
	try_me_else		wait_comp_descending_atom_10_1
	atom		10
	branch_on_atom		10,2,wait_comp_descending_atom_10_1
	bucket_entry_a		greater,wait_comp_descending_atom_10_3
	bucket_entry_a		less,wait_comp_descending_atom_10_4
wait_comp_descending_atom_10_3:
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,part_descending_atom_8_0
wait_comp_descending_atom_10_4:
	get_list_val_var		5,11,2,10
	put_value		2,9
	put_value		5,10
	execute		8,part_descending_atom_8_0
wait_comp_descending_atom_10_1:
	suspend		wait_comp_descending_atom_10_0
	module_entry		quick_sort
	predicate		part_user_defined,8
part_user_defined_8_0:
	try_me_else		part_user_defined_8_1
	jump_on_non_list_var_var		1,part_user_defined_8_3,9,10
	wait_value		9,2
	collect_value		2
	put_reused_list		1,1
	write_car_marked_value		1,9
	write_cdr_variable		1,11
	get_list_value		6,1
	put_values_dec		1,10,2
	put_value		6,11
	execute		8,part_user_defined_8_0
part_user_defined_8_3:
	check_nil		1,part_user_defined_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
part_user_defined_8_1:
	otherwise		part_user_defined_8_0
	try_me_else		part_user_defined_8_8
	wait_list_var_var		1,9,10
	collect_list		1
	put_marked_value		12,8
	put_vector		1,5
	write_element_value		1,0,9
	write_element_value		1,1,2
	write_element_variable		1,2,9
	write_element_variable		1,3,2
	write_element_variable		1,4,11
	b_apply		12,1
	put_value		1,10
	put_value		10,11
	execute		10,wait_comp_user_defined_10_0
part_user_defined_8_8:
	suspend		part_user_defined_8_0
	module_entry		quick_sort
	predicate		wait_comp_user_defined,10
wait_comp_user_defined_10_0:
	try_me_else		wait_comp_user_defined_10_1
	atom		10
	branch_on_atom		10,2,wait_comp_user_defined_10_1
	bucket_entry_a		no,wait_comp_user_defined_10_3
	bucket_entry_a		yes,wait_comp_user_defined_10_4
wait_comp_user_defined_10_3:
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,part_user_defined_8_0
wait_comp_user_defined_10_4:
	get_list_val_var		5,11,2,10
	put_value		2,9
	put_value		5,10
	execute		8,part_user_defined_8_0
wait_comp_user_defined_10_1:
	suspend		wait_comp_user_defined_10_0
	module_entry		quick_sort
	predicate		key_sort,3
key_sort_3_0:
	put_nil		4
	execute		4,key_sort_4_0
key_sort_3_1:
	suspend		key_sort_3_0
	module_entry		quick_sort
	predicate		key_sort,4
key_sort_4_0:
	try_me_else		key_sort_4_1
	jump_on_non_list_var_var		1,key_sort_4_3,11,5
	wait_vector		11,2
	read_elements_inc		11,0,6,2
	put_value		8,2
	create_goal		4
	set_variable		1,10
	set_marked_value		2,8
	set_variable		3,9
	set_value		4,4
	enqueue_goal		4,key_sort_4_0
	create_goal		4
	set_variable		1,4
	set_value		2,8
	set_value		3,3
	put_reused_vector		2,11
	write_element_variable		2,0,3
	write_element_value		2,1,7
	put_reused_list_val_var		1,1,2,7
	set_value		4,1
	enqueue_goal		4,key_sort_4_0
	put_values_inc		1,5,2
	put_value		5,10
	put_value		6,7
	put_value		7,9
	execute		8,kpart_8_0
key_sort_4_3:
	check_nil		1,key_sort_4_1
	collect_value		2
	get_value		3,4
	proceed
key_sort_4_1:
	otherwise		key_sort_4_0
	try_me_else		key_sort_4_8
	wait_list_var_var		1,5,6
	collect_list		1
	collect_value		2
	collect_value		6
	get_value		3,4
	put_value		1,5
	execute		1,raise_error_1_0
key_sort_4_8:
	suspend		key_sort_4_0
	module_entry		quick_sort
	predicate		kpart,8
kpart_8_0:
	try_me_else		kpart_8_1
	atom		2
	atom		8
	branch_on_atom		8,2,kpart_8_1
	bucket_entry_a		ascending,kpart_8_4
	bucket_entry_a		descending,kpart_8_5
kpart_8_4:
	g_tag_and_value		2,8,9
	put_value		8,9
	execute		8,kpart_atom_8_0
kpart_8_5:
	g_tag_and_value		2,8,9
	put_value		8,9
	execute		8,kpart_descending_atom_8_0
kpart_8_1:
	otherwise		kpart_8_0
	try_me_else		kpart_8_9
	jump_on_non_atom		8,kpart_8_11
	branch_on_atom		8,2,kpart_8_9
	bucket_entry_a		ascending,kpart_8_12
	bucket_entry_a		descending,kpart_8_13
kpart_8_12:
	execute		7,kpart_7_0
kpart_8_13:
	execute		7,kpart_descending_7_0
kpart_8_11:
	check_vector		8,3,kpart_8_9
	read_elements_inc		8,0,9,3
	atom		9
	atom		10
	integer		11
	put_reused_vector		8,8
	write_elements_inc		8,0,9,3
	execute		8,kpart_user_defined_8_0
kpart_8_9:
	suspend		kpart_8_0
	module_entry		quick_sort
	predicate		kpart,7
kpart_7_0:
	try_me_else		kpart_7_1
	jump_on_non_list		1,kpart_7_3
	read_car		1,8
	wait_vector		8,2
	read_element		8,0,9
	try_me_else		kpart_7_5
	jump_on_non_integer		9,kpart_7_7
	read_element		8,1,10
	read_cdr		1,11
	integer		2
	try_me_else		kpart_7_9
	g_less_than		9,2
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,11
	put_value		4,8
	execute		7,kpart_7_0
kpart_7_9:
	try_me_else		kpart_7_5
	g_less_than		2,9
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,11
	put_value		5,8
	execute		7,kpart_7_0
kpart_7_7:
	is_float		9,kpart_7_5
	read_element		8,1,10
	read_cdr		1,11
	float		2
	try_me_else		kpart_7_11
	g_float_less_than		9,2
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,11
	put_value		4,8
	execute		7,kpart_7_0
kpart_7_11:
	try_me_else		kpart_7_5
	g_float_less_than		2,9
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,11
	put_value		5,8
	execute		7,kpart_7_0
kpart_7_5:
	read_element		8,1,10
	read_cdr		1,11
	try_me_else		kpart_7_1
	wait_value		2,9
	collect_value		9
	put_reused_vector		8,8
	write_element_marked_value		8,0,2
	write_element_value		8,1,10
	get_reused_list_val_var		6,1,1,8,8
	put_value		1,11
	put_value		6,8
	execute		7,kpart_7_0
kpart_7_3:
	check_nil		1,kpart_7_1
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
kpart_7_1:
	otherwise		kpart_7_0
	try_me_else		kpart_7_28
	wait_list_var_var		1,11,8
	wait_vector		11,2
	read_elements_inc		11,0,9,2
	collect_list		1
	create_goal		9
	set_value		1,8
	set_variable		2,8
	set_values_inc		3,3,5
	put_reused_vector		1,11
	write_element_variable		1,0,3
	write_element_value		1,1,10
	set_value		8,1
	set_variable		9,5
	enqueue_goal		9,wait_kcomp_9_0
	put_value		1,9
	put_value		4,8
	execute_external		comparator,sort0,5
kpart_7_28:
	otherwise		kpart_7_0
	try_me_else		kpart_7_32
	wait_list_var_var		1,8,9
	collect_list		1
	collect_value		3
	collect_value		2
	collect_value		9
	get_nil		4
	get_nil		5
	get_value		6,7
	put_value		1,8
	execute		1,raise_error_1_0
kpart_7_32:
	suspend		kpart_7_0
	module_entry		quick_sort
	predicate		wait_kcomp,9
wait_kcomp_9_0:
	try_me_else		wait_kcomp_9_1
	atom		9
	branch_on_atom		9,2,wait_kcomp_9_1
	bucket_entry_a		greater,wait_kcomp_9_3
	bucket_entry_a		less,wait_kcomp_9_4
wait_kcomp_9_3:
	get_list_val_var		5,9,8,8
	put_value		5,8
	execute		7,kpart_7_0
wait_kcomp_9_4:
	get_list_val_var		4,9,8,8
	put_value		4,8
	execute		7,kpart_7_0
wait_kcomp_9_1:
	suspend		wait_kcomp_9_0
	module_entry		quick_sort
	predicate		kpart_atom,8
kpart_atom_8_0:
	try_me_else		kpart_atom_8_1
	jump_on_non_list		1,kpart_atom_8_3
	read_car		1,9
	wait_vector		9,2
	read_element		9,0,10
	atom		10
	read_element		9,1,11
	read_cdr		1,12
	integer		8
	try_me_else		kpart_atom_8_7
	g_tag_and_value		10,13,14
	wait_value		14,8
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		6,1,1,9,9
	put_value		1,12
	put_value		6,9
	execute		8,kpart_atom_8_0
kpart_atom_8_7:
	try_me_else		kpart_atom_8_8
	g_tag_and_value		10,13,14
	g_less_than		14,8
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,12
	put_value		4,9
	execute		8,kpart_atom_8_0
kpart_atom_8_8:
	try_me_else		kpart_atom_8_1
	g_tag_and_value		10,13,14
	g_less_than		8,14
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		5,1,1,9,9
	put_value		1,12
	put_value		5,9
	execute		8,kpart_atom_8_0
kpart_atom_8_3:
	check_nil		1,kpart_atom_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
kpart_atom_8_1:
	otherwise		kpart_atom_8_0
	try_me_else		kpart_atom_8_20
	wait_list_var_var		1,12,9
	wait_vector		12,2
	read_elements_inc		12,0,10,2
	collect_list		1
	create_goal		10
	set_value		1,9
	set_variable		2,9
	set_values_inc		3,3,6
	put_reused_vector		1,12
	write_element_variable		1,0,3
	write_element_value		1,1,11
	set_value		9,1
	set_variable		10,5
	enqueue_goal		10,wait_kcomp_atom_10_0
	put_value		1,10
	put_value		4,9
	execute_external		comparator,sort0,5
kpart_atom_8_20:
	otherwise		kpart_atom_8_0
	try_me_else		kpart_atom_8_24
	wait_list_var_var		1,9,10
	collect_list		1
	collect_value		8
	collect_value		3
	collect_value		2
	collect_value		10
	get_nil		4
	get_nil		5
	get_value		6,7
	put_value		1,9
	execute		1,raise_error_1_0
kpart_atom_8_24:
	suspend		kpart_atom_8_0
	module_entry		quick_sort
	predicate		wait_kcomp_atom,10
wait_kcomp_atom_10_0:
	try_me_else		wait_kcomp_atom_10_1
	atom		10
	branch_on_atom		10,2,wait_kcomp_atom_10_1
	bucket_entry_a		greater,wait_kcomp_atom_10_3
	bucket_entry_a		less,wait_kcomp_atom_10_4
wait_kcomp_atom_10_3:
	get_list_val_var		5,10,9,9
	put_value		5,9
	execute		8,kpart_atom_8_0
wait_kcomp_atom_10_4:
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,kpart_atom_8_0
wait_kcomp_atom_10_1:
	suspend		wait_kcomp_atom_10_0
	module_entry		quick_sort
	predicate		kpart_descending,7
kpart_descending_7_0:
	try_me_else		kpart_descending_7_1
	jump_on_non_list		1,kpart_descending_7_3
	read_car		1,8
	wait_vector		8,2
	read_element		8,0,9
	try_me_else		kpart_descending_7_5
	jump_on_non_integer		9,kpart_descending_7_7
	read_element		8,1,10
	read_cdr		1,11
	integer		2
	try_me_else		kpart_descending_7_9
	g_less_than		2,9
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,11
	put_value		4,8
	execute		7,kpart_descending_7_0
kpart_descending_7_9:
	try_me_else		kpart_descending_7_5
	g_less_than		9,2
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,11
	put_value		5,8
	execute		7,kpart_descending_7_0
kpart_descending_7_7:
	is_float		9,kpart_descending_7_5
	read_element		8,1,10
	read_cdr		1,11
	float		2
	try_me_else		kpart_descending_7_11
	g_float_less_than		2,9
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		4,1,1,8,8
	put_value		1,11
	put_value		4,8
	execute		7,kpart_descending_7_0
kpart_descending_7_11:
	try_me_else		kpart_descending_7_5
	g_float_less_than		9,2
	put_reused_vector		8,8
	write_elements_inc		8,0,9,2
	get_reused_list_val_var		5,1,1,8,8
	put_value		1,11
	put_value		5,8
	execute		7,kpart_descending_7_0
kpart_descending_7_5:
	read_element		8,1,10
	read_cdr		1,11
	try_me_else		kpart_descending_7_1
	wait_value		2,9
	collect_value		9
	put_reused_vector		8,8
	write_element_marked_value		8,0,2
	write_element_value		8,1,10
	get_reused_list_val_var		6,1,1,8,8
	put_value		1,11
	put_value		6,8
	execute		7,kpart_descending_7_0
kpart_descending_7_3:
	check_nil		1,kpart_descending_7_1
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
kpart_descending_7_1:
	otherwise		kpart_descending_7_0
	try_me_else		kpart_descending_7_28
	wait_list_var_var		1,11,8
	wait_vector		11,2
	read_elements_inc		11,0,9,2
	collect_list		1
	create_goal		9
	set_value		1,8
	set_variable		2,8
	set_values_inc		3,3,5
	put_reused_vector		1,11
	write_element_variable		1,0,3
	write_element_value		1,1,10
	set_value		8,1
	set_variable		9,5
	enqueue_goal		9,wait_kcomp_descending_9_0
	put_value		1,9
	put_value		4,8
	execute_external		comparator,sort0,5
kpart_descending_7_28:
	otherwise		kpart_descending_7_0
	try_me_else		kpart_descending_7_32
	wait_list_var_var		1,8,9
	collect_list		1
	collect_value		3
	collect_value		2
	collect_value		9
	get_nil		4
	get_nil		5
	get_value		6,7
	put_value		1,8
	execute		1,raise_error_1_0
kpart_descending_7_32:
	suspend		kpart_descending_7_0
	module_entry		quick_sort
	predicate		wait_kcomp_descending,9
wait_kcomp_descending_9_0:
	try_me_else		wait_kcomp_descending_9_1
	atom		9
	branch_on_atom		9,2,wait_kcomp_descending_9_1
	bucket_entry_a		greater,wait_kcomp_descending_9_3
	bucket_entry_a		less,wait_kcomp_descending_9_4
wait_kcomp_descending_9_3:
	get_list_val_var		4,9,8,8
	put_value		4,8
	execute		7,kpart_descending_7_0
wait_kcomp_descending_9_4:
	get_list_val_var		5,9,8,8
	put_value		5,8
	execute		7,kpart_descending_7_0
wait_kcomp_descending_9_1:
	suspend		wait_kcomp_descending_9_0
	module_entry		quick_sort
	predicate		kpart_descending_atom,8
kpart_descending_atom_8_0:
	try_me_else		kpart_descending_atom_8_1
	jump_on_non_list		1,kpart_descending_atom_8_3
	read_car		1,9
	wait_vector		9,2
	read_element		9,0,10
	atom		10
	read_element		9,1,11
	read_cdr		1,12
	integer		8
	try_me_else		kpart_descending_atom_8_7
	g_tag_and_value		10,13,14
	wait_value		14,8
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		6,1,1,9,9
	put_value		1,12
	put_value		6,9
	execute		8,kpart_descending_atom_8_0
kpart_descending_atom_8_7:
	try_me_else		kpart_descending_atom_8_8
	g_tag_and_value		10,13,14
	g_less_than		8,14
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		4,1,1,9,9
	put_value		1,12
	put_value		4,9
	execute		8,kpart_descending_atom_8_0
kpart_descending_atom_8_8:
	try_me_else		kpart_descending_atom_8_1
	g_tag_and_value		10,13,14
	g_less_than		14,8
	put_reused_vector		9,9
	write_elements_inc		9,0,10,2
	get_reused_list_val_var		5,1,1,9,9
	put_value		1,12
	put_value		5,9
	execute		8,kpart_descending_atom_8_0
kpart_descending_atom_8_3:
	check_nil		1,kpart_descending_atom_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
kpart_descending_atom_8_1:
	otherwise		kpart_descending_atom_8_0
	try_me_else		kpart_descending_atom_8_20
	wait_list_var_var		1,12,9
	wait_vector		12,2
	read_elements_inc		12,0,10,2
	collect_list		1
	create_goal		10
	set_value		1,9
	set_variable		2,9
	set_values_inc		3,3,6
	put_reused_vector		1,12
	write_element_variable		1,0,3
	write_element_value		1,1,11
	set_value		9,1
	set_variable		10,5
	enqueue_goal		10,wait_kcomp_descending_atom_10_0
	put_value		1,10
	put_value		4,9
	execute_external		comparator,sort0,5
kpart_descending_atom_8_20:
	otherwise		kpart_descending_atom_8_0
	try_me_else		kpart_descending_atom_8_24
	wait_list_var_var		1,9,10
	collect_list		1
	collect_value		8
	collect_value		3
	collect_value		2
	collect_value		10
	get_nil		4
	get_nil		5
	get_value		6,7
	put_value		1,9
	execute		1,raise_error_1_0
kpart_descending_atom_8_24:
	suspend		kpart_descending_atom_8_0
	module_entry		quick_sort
	predicate		wait_kcomp_descending_atom,10
wait_kcomp_descending_atom_10_0:
	try_me_else		wait_kcomp_descending_atom_10_1
	atom		10
	branch_on_atom		10,2,wait_kcomp_descending_atom_10_1
	bucket_entry_a		greater,wait_kcomp_descending_atom_10_3
	bucket_entry_a		less,wait_kcomp_descending_atom_10_4
wait_kcomp_descending_atom_10_3:
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,kpart_descending_atom_8_0
wait_kcomp_descending_atom_10_4:
	get_list_val_var		5,11,2,10
	put_value		2,9
	put_value		5,10
	execute		8,kpart_descending_atom_8_0
wait_kcomp_descending_atom_10_1:
	suspend		wait_kcomp_descending_atom_10_0
	module_entry		quick_sort
	predicate		kpart_user_defined,8
kpart_user_defined_8_0:
	try_me_else		kpart_user_defined_8_1
	jump_on_non_list_var_var		1,kpart_user_defined_8_3,12,9
	wait_vector		12,2
	read_elements_inc		12,0,10,2
	wait_value		10,2
	collect_value		2
	put_reused_vector		2,12
	write_element_marked_value		2,0,10
	write_element_value		2,1,11
	get_reused_list_val_var		6,1,1,2,11
	put_values_inc		1,9,2
	put_value		6,11
	execute		8,kpart_user_defined_8_0
kpart_user_defined_8_3:
	check_nil		1,kpart_user_defined_8_1
	collect_value		8
	get_value		2,3
	get_nil		4
	get_nil		5
	get_value		6,7
	proceed
kpart_user_defined_8_1:
	otherwise		kpart_user_defined_8_0
	try_me_else		kpart_user_defined_8_8
	wait_list_var_var		1,14,9
	wait_vector		14,2
	read_elements_inc		14,0,10,2
	collect_list		1
	put_marked_value		15,8
	put_vector		1,5
	write_element_value		1,0,10
	write_element_value		1,1,2
	write_element_variable		1,2,13
	write_element_variable		1,3,2
	write_element_variable		1,4,12
	b_apply		15,1
	put_reused_vector		10,14
	write_element_value		10,0,13
	write_element_value		10,1,11
	put_value		1,9
	put_value		9,10
	put_value		10,12
	execute		10,wait_kcomp_user_defined_10_0
kpart_user_defined_8_8:
	otherwise		kpart_user_defined_8_0
	try_me_else		kpart_user_defined_8_12
	wait_list_var_var		1,9,10
	collect_list		1
	collect_value		8
	collect_value		3
	collect_value		2
	collect_value		10
	get_nil		4
	get_nil		5
	get_value		6,7
	put_value		1,9
	execute		1,raise_error_1_0
kpart_user_defined_8_12:
	suspend		kpart_user_defined_8_0
	module_entry		quick_sort
	predicate		wait_kcomp_user_defined,10
wait_kcomp_user_defined_10_0:
	try_me_else		wait_kcomp_user_defined_10_1
	wait_vector		9,2
	read_elements_inc		9,0,11,2
	wait_atom		10,yes
	put_reused_vector		9,9
	write_element_value		9,0,2
	write_element_value		9,1,12
	get_list_val_var		5,2,9,9
	put_value		2,11
	put_value		5,9
	execute		8,kpart_user_defined_8_0
wait_kcomp_user_defined_10_1:
	try_me_else		wait_kcomp_user_defined_10_3
	wait_atom		10,no
	get_list_val_var		4,10,9,9
	put_value		4,9
	execute		8,kpart_user_defined_8_0
wait_kcomp_user_defined_10_3:
	suspend		wait_kcomp_user_defined_10_0
	module_entry		quick_sort
	predicate		raise_error,1
raise_error_1_0:
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_0'
	b_raise		3,2,1
	proceed
raise_error_1_1:
	suspend		raise_error_1_0
	begin_const_section		quick_sort
'$SCNST_0_1':
	define_desc		27,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1869770847
	define_integer		1868787572
	define_integer		108
'$SCNST_0_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		key_sort
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
