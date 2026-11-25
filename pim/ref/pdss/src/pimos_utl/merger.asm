merger:
	module		merger
	entry		merge,4,merge_4_0
	entry		key_merge,4,key_merge_4_0
	module_entry		merger
	predicate		merge,4
merge_4_0:
	try_me_else		merge_4_1
	jump_on_non_list_var_var		1,merge_4_3,5,6
	wait_list_var_var		2,7,8
	jump_on_non_atom		3,merge_4_6
	branch_on_atom		3,2,merge_4_1
	bucket_entry_a		ascending,merge_4_7
	bucket_entry_a		descending,merge_4_8
merge_4_7:
	collect_list		1
	collect_list		2
	put_value		9,4
	put_value		1,6
	put_value		2,8
	put_value		3,5
	put_value		4,7
	put_value		5,9
	execute		5,merge_5_0
merge_4_8:
	collect_list		1
	collect_list		2
	put_value		9,4
	put_value		1,6
	put_value		2,8
	put_value		3,5
	put_value		4,7
	put_value		5,9
	execute		5,merge_descending_5_0
merge_4_6:
	check_vector		3,3,merge_4_1
	read_elements_inc		3,0,9,3
	atom		9
	atom		10
	integer		11
	collect_list		1
	collect_list		2
	put_value		13,4
	put_reused_vector		12,3
	write_elements_inc		12,0,9,3
	put_value		1,6
	put_value		2,8
	put_value		3,5
	put_value		4,7
	put_values_dec		5,13,2
	execute		6,merge_user_defined_6_0
merge_4_3:
	check_nil		1,merge_4_1
	collect_value		3
	get_value		2,4
	proceed
merge_4_1:
	try_me_else		merge_4_9
	wait_nil		2
	collect_value		3
	get_value		1,4
	proceed
merge_4_9:
	otherwise		merge_4_0
	collect_value		3
	get_nil		4
	create_goal		1
	set_value		1,2
	enqueue_goal		1,if_raise_error_1_0
	execute		1,if_raise_error_1_0
merge_4_22:
	suspend		merge_4_0
	module_entry		merger
	predicate		merge,5
merge_5_0:
	try_me_else		merge_5_1
	jump_on_non_list_var_var		1,merge_5_3,6,7
	wait		3
	switch_on_type		3,merge_5_4,merge_5_5,merge_5_1,merge_5_1,merge_5_1,merge_5_6
merge_5_4:
	atom		4
	g_tag_and_value		3,8,9
	g_tag_and_value		4,8,10
	g_not_less_than		10,9
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_5:
	integer		4
	g_not_less_than		4,3
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_6:
	is_float		3,merge_5_1
	float		4
	g_float_not_less_than		4,3
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_3:
	check_nil		1,merge_5_1
	wait		3
	switch_on_type		3,merge_5_7,merge_5_8,merge_5_1,merge_5_1,merge_5_1,merge_5_9
merge_5_7:
	atom		4
	g_tag_and_value		3,6,7
	g_tag_and_value		4,6,8
	g_not_less_than		8,7
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_5_8:
	integer		4
	g_not_less_than		4,3
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_5_9:
	is_float		3,merge_5_1
	float		4
	g_float_not_less_than		4,3
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_5_1:
	try_me_else		merge_5_10
	jump_on_non_list_var_var		2,merge_5_12,6,7
	wait		3
	switch_on_type		3,merge_5_13,merge_5_14,merge_5_10,merge_5_10,merge_5_10,merge_5_15
merge_5_13:
	atom		4
	g_tag_and_value		3,8,9
	g_tag_and_value		4,8,10
	g_less_than		10,9
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_14:
	integer		4
	g_less_than		4,3
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_15:
	is_float		3,merge_5_10
	float		4
	g_float_less_than		4,3
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_5_0
merge_5_12:
	check_nil		2,merge_5_10
	wait		3
	switch_on_type		3,merge_5_16,merge_5_17,merge_5_10,merge_5_10,merge_5_10,merge_5_18
merge_5_16:
	atom		4
	g_tag_and_value		3,6,7
	g_tag_and_value		4,6,8
	g_less_than		8,7
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_5_17:
	integer		4
	g_less_than		4,3
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_5_18:
	is_float		3,merge_5_10
	float		4
	g_float_less_than		4,3
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_5_10:
	otherwise		merge_5_0
	create_goal		6
	set_values_inc		1,1,2
	set_variable		3,7
	set_variable		4,6
	set_value		5,5
	set_variable		6,5
	enqueue_goal		6,wait_comp_6_0
	put_values_inc		1,3,2
	put_values_dec		3,7,2
	execute_external		comparator,sort0,5
merge_5_32:
	suspend		merge_5_0
	module_entry		merger
	predicate		wait_comp,6
wait_comp_6_0:
	try_me_else		wait_comp_6_1
	jump_on_non_list_var_var		2,wait_comp_6_3,7,8
	wait_atom		6,greater
	get_reused_list_val_var		5,2,2,4,6
	put_value		2,8
	put_values_dec		4,7,2
	execute		5,merge_5_0
wait_comp_6_3:
	check_nil		2,wait_comp_6_1
	wait_atom		6,greater
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
wait_comp_6_1:
	otherwise		wait_comp_6_0
	try_me_else		wait_comp_6_8
	jump_on_non_list_var_var		1,wait_comp_6_10,7,8
	collect_value		6
	get_reused_list_val_var		5,1,1,3,6
	put_value		1,8
	put_value		3,7
	put_value		5,6
	execute		5,merge_5_0
wait_comp_6_10:
	check_nil		1,wait_comp_6_8
	collect_value		6
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
wait_comp_6_8:
	suspend		wait_comp_6_0
	module_entry		merger
	predicate		merge_descending,5
merge_descending_5_0:
	try_me_else		merge_descending_5_1
	jump_on_non_list_var_var		1,merge_descending_5_3,6,7
	wait		3
	switch_on_type		3,merge_descending_5_4,merge_descending_5_5,merge_descending_5_1,merge_descending_5_1,merge_descending_5_1,merge_descending_5_6
merge_descending_5_4:
	atom		4
	g_tag_and_value		3,8,9
	g_tag_and_value		4,8,10
	g_not_less_than		9,10
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_5:
	integer		4
	g_not_less_than		3,4
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_6:
	is_float		3,merge_descending_5_1
	float		4
	g_float_not_less_than		3,4
	get_reused_list_val_var		5,1,1,3,8
	put_value		1,7
	put_value		3,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_3:
	check_nil		1,merge_descending_5_1
	wait		3
	switch_on_type		3,merge_descending_5_7,merge_descending_5_8,merge_descending_5_1,merge_descending_5_1,merge_descending_5_1,merge_descending_5_9
merge_descending_5_7:
	atom		4
	g_tag_and_value		3,6,7
	g_tag_and_value		4,6,8
	g_not_less_than		7,8
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_descending_5_8:
	integer		4
	g_not_less_than		3,4
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_descending_5_9:
	is_float		3,merge_descending_5_1
	float		4
	g_float_not_less_than		3,4
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
merge_descending_5_1:
	try_me_else		merge_descending_5_10
	jump_on_non_list_var_var		2,merge_descending_5_12,6,7
	wait		3
	switch_on_type		3,merge_descending_5_13,merge_descending_5_14,merge_descending_5_10,merge_descending_5_10,merge_descending_5_10,merge_descending_5_15
merge_descending_5_13:
	atom		4
	g_tag_and_value		3,8,9
	g_tag_and_value		4,8,10
	g_less_than		9,10
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_14:
	integer		4
	g_less_than		3,4
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_15:
	is_float		3,merge_descending_5_10
	float		4
	g_float_less_than		3,4
	get_reused_list_val_var		5,2,2,4,8
	put_value		2,7
	put_value		4,6
	put_value		5,8
	execute		5,merge_descending_5_0
merge_descending_5_12:
	check_nil		2,merge_descending_5_10
	wait		3
	switch_on_type		3,merge_descending_5_16,merge_descending_5_17,merge_descending_5_10,merge_descending_5_10,merge_descending_5_10,merge_descending_5_18
merge_descending_5_16:
	atom		4
	g_tag_and_value		3,6,7
	g_tag_and_value		4,6,8
	g_less_than		7,8
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_descending_5_17:
	integer		4
	g_less_than		3,4
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_descending_5_18:
	is_float		3,merge_descending_5_10
	float		4
	g_float_less_than		3,4
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
merge_descending_5_10:
	otherwise		merge_descending_5_0
	create_goal		6
	set_values_inc		1,1,2
	set_variable		3,7
	set_variable		4,6
	set_value		5,5
	set_variable		6,5
	enqueue_goal		6,wait_comp_descending_6_0
	put_values_inc		1,3,2
	put_values_dec		3,7,2
	execute_external		comparator,sort0,5
merge_descending_5_32:
	suspend		merge_descending_5_0
	module_entry		merger
	predicate		wait_comp_descending,6
wait_comp_descending_6_0:
	try_me_else		wait_comp_descending_6_1
	jump_on_non_list_var_var		2,wait_comp_descending_6_3,7,8
	wait_atom		6,less
	get_reused_list_val_var		5,2,2,4,6
	put_value		2,8
	put_values_dec		4,7,2
	execute		5,merge_descending_5_0
wait_comp_descending_6_3:
	check_nil		2,wait_comp_descending_6_1
	wait_atom		6,less
	put_list_val_val		2,3,1
	put_list_val_val		1,4,2
	get_list_value		5,1
	proceed
wait_comp_descending_6_1:
	otherwise		wait_comp_descending_6_0
	try_me_else		wait_comp_descending_6_8
	jump_on_non_list_var_var		1,wait_comp_descending_6_10,7,8
	collect_value		6
	get_reused_list_val_var		5,1,1,3,6
	put_value		1,8
	put_value		3,7
	put_value		5,6
	execute		5,merge_descending_5_0
wait_comp_descending_6_10:
	check_nil		1,wait_comp_descending_6_8
	collect_value		6
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
wait_comp_descending_6_8:
	suspend		wait_comp_descending_6_0
	module_entry		merger
	predicate		merge_user_defined,6
merge_user_defined_6_0:
	put_marked_value		9,6
	put_vector		7,5
	write_elements_inc		7,0,3,2
	write_element_variable		7,2,3
	write_element_variable		7,3,4
	write_element_variable		7,4,8
	b_apply		9,7
	put_value		7,8
	execute		7,wait_comp_user_defined_7_0
merge_user_defined_6_1:
	suspend		merge_user_defined_6_0
	module_entry		merger
	predicate		wait_comp_user_defined,7
wait_comp_user_defined_7_0:
	try_me_else		wait_comp_user_defined_7_1
	jump_on_non_list_var_var		1,wait_comp_user_defined_7_3,8,9
	wait_atom		7,no
	get_reused_list_val_var		5,1,1,3,7
	put_value		1,9
	put_value		3,8
	put_value		5,7
	execute		6,merge_user_defined_6_0
wait_comp_user_defined_7_3:
	check_nil		1,wait_comp_user_defined_7_1
	wait_atom		7,no
	collect_value		6
	put_list_val_val		1,4,2
	put_list_val_val		2,3,1
	get_list_value		5,2
	proceed
wait_comp_user_defined_7_1:
	try_me_else		wait_comp_user_defined_7_4
	jump_on_non_list_var_var		2,wait_comp_user_defined_7_6,8,9
	wait_atom		7,yes
	get_reused_list_val_var		5,2,2,3,7
	put_value		2,9
	put_value		3,4
	put_values_dec		4,8,2
	execute		6,merge_user_defined_6_0
wait_comp_user_defined_7_6:
	check_nil		2,wait_comp_user_defined_7_4
	wait_atom		7,yes
	collect_value		6
	put_list_val_val		2,4,1
	put_list_val_val		1,3,2
	get_list_value		5,1
	proceed
wait_comp_user_defined_7_4:
	suspend		wait_comp_user_defined_7_0
	module_entry		merger
	predicate		key_merge,4
key_merge_4_0:
	try_me_else		key_merge_4_1
	jump_on_non_list		1,key_merge_4_3
	read_car		1,5
	wait_vector		5,2
	read_elements_inc		5,0,6,2
	read_cdr		1,8
	list		2
	read_car		2,9
	wait_vector		9,2
	read_elements_inc		9,0,10,2
	read_cdr		2,12
	jump_on_non_atom		3,key_merge_4_8
	branch_on_atom		3,2,key_merge_4_1
	bucket_entry_a		ascending,key_merge_4_9
	bucket_entry_a		descending,key_merge_4_10
key_merge_4_9:
	collect_list		1
	collect_list		2
	put_value		14,4
	put_reused_vector		13,5
	write_element_void		13,0
	write_element_value		13,1,7
	put_reused_vector		7,9
	write_element_void		7,0
	write_element_value		7,1,11
	put_value		1,8
	put_value		2,12
	put_value		3,6
	put_value		4,10
	put_values_dec		5,14,2
	execute		7,kmerge_7_0
key_merge_4_10:
	collect_list		1
	collect_list		2
	put_value		14,4
	put_reused_vector		13,5
	write_element_void		13,0
	write_element_value		13,1,7
	put_reused_vector		7,9
	write_element_void		7,0
	write_element_value		7,1,11
	put_value		1,8
	put_value		2,12
	put_value		3,6
	put_value		4,10
	put_values_dec		5,14,2
	execute		7,kmerge_descending_7_0
key_merge_4_8:
	check_vector		3,3,key_merge_4_1
	read_elements_inc		3,0,13,3
	atom		13
	atom		14
	integer		15
	collect_list		1
	collect_list		2
	put_value		17,4
	put_reused_vector		16,5
	write_element_void		16,0
	write_element_value		16,1,7
	put_reused_vector		7,9
	write_element_void		7,0
	write_element_value		7,1,11
	put_reused_vector		9,3
	write_elements_inc		9,0,13,3
	put_value		1,8
	put_value		2,12
	put_value		3,6
	put_value		4,10
	put_values_dec		5,17,2
	put_value		8,9
	execute		8,kmerge_user_defined_8_0
key_merge_4_3:
	check_nil		1,key_merge_4_1
	collect_value		3
	get_value		2,4
	proceed
key_merge_4_1:
	try_me_else		key_merge_4_11
	wait_nil		2
	collect_value		3
	get_value		1,4
	proceed
key_merge_4_11:
	otherwise		key_merge_4_0
	collect_value		3
	get_nil		4
	create_goal		1
	set_value		1,2
	enqueue_goal		1,if_raise_error_1_0
	execute		1,if_raise_error_1_0
key_merge_4_30:
	suspend		key_merge_4_0
	module_entry		merger
	predicate		kmerge,7
kmerge_7_0:
	try_me_else		kmerge_7_1
	jump_on_non_list		1,kmerge_7_3
	read_car		1,8
	wait_vector		8,2
	read_elements_inc		8,0,9,2
	read_cdr		1,11
	wait		3
	switch_on_type		3,kmerge_7_5,kmerge_7_6,kmerge_7_1,kmerge_7_1,kmerge_7_1,kmerge_7_7
kmerge_7_5:
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	atom		4
	g_tag_and_value		3,14,15
	g_tag_and_value		4,14,16
	g_not_less_than		16,15
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_6:
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	integer		4
	g_not_less_than		4,3
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_7:
	is_float		3,kmerge_7_1
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	float		4
	g_float_not_less_than		4,3
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_3:
	check_nil		1,kmerge_7_1
	wait		3
	switch_on_type		3,kmerge_7_8,kmerge_7_9,kmerge_7_1,kmerge_7_1,kmerge_7_1,kmerge_7_10
kmerge_7_8:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	atom		4
	g_tag_and_value		3,12,13
	g_tag_and_value		4,12,14
	g_not_less_than		14,13
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_7_9:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	integer		4
	g_not_less_than		4,3
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_7_10:
	is_float		3,kmerge_7_1
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	float		4
	g_float_not_less_than		4,3
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_7_1:
	try_me_else		kmerge_7_11
	jump_on_non_list		2,kmerge_7_13
	read_car		2,8
	wait_vector		8,2
	read_elements_inc		8,0,9,2
	read_cdr		2,11
	wait		3
	switch_on_type		3,kmerge_7_15,kmerge_7_16,kmerge_7_11,kmerge_7_11,kmerge_7_11,kmerge_7_17
kmerge_7_15:
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	atom		4
	g_tag_and_value		3,14,15
	g_tag_and_value		4,14,16
	g_less_than		16,15
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_16:
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	integer		4
	g_less_than		4,3
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_17:
	is_float		3,kmerge_7_11
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	float		4
	g_float_less_than		4,3
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_7_0
kmerge_7_13:
	check_nil		2,kmerge_7_11
	wait		3
	switch_on_type		3,kmerge_7_18,kmerge_7_19,kmerge_7_11,kmerge_7_11,kmerge_7_11,kmerge_7_20
kmerge_7_18:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	atom		4
	g_tag_and_value		3,12,13
	g_tag_and_value		4,12,14
	g_less_than		14,13
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_7_19:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	integer		4
	g_less_than		4,3
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_7_20:
	is_float		3,kmerge_7_11
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	float		4
	g_float_less_than		4,3
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_7_11:
	otherwise		kmerge_7_0
	create_goal		8
	set_values_inc		1,1,2
	set_variable		3,9
	set_variable		4,8
	set_values_inc		5,5,3
	set_variable		8,5
	enqueue_goal		8,wait_kcomp_8_0
	put_values_inc		1,3,2
	put_values_dec		3,9,2
	execute_external		comparator,sort0,5
kmerge_7_40:
	suspend		kmerge_7_0
	module_entry		merger
	predicate		wait_kcomp,8
wait_kcomp_8_0:
	try_me_else		wait_kcomp_8_1
	jump_on_non_list		1,wait_kcomp_8_3
	read_car		1,9
	wait_vector		9,2
	read_elements_inc		9,0,10,2
	read_cdr		1,12
	wait_vector		6,2
	read_elements_inc		6,0,13,2
	atom		8
	branch_on_atom		8,2,wait_kcomp_8_1
	bucket_entry_a		less,wait_kcomp_8_7
	bucket_entry_a		same,wait_kcomp_8_8
wait_kcomp_8_7:
	collect_value		13
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,14
	get_reused_list_val_var		5,1,1,6,8
	put_reused_vector		6,9
	write_element_void		6,0
	write_element_value		6,1,11
	put_value		1,12
	put_value		3,10
	put_value		5,8
	execute		7,kmerge_7_0
wait_kcomp_8_8:
	collect_value		13
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,14
	get_reused_list_val_var		5,1,1,6,8
	put_reused_vector		6,9
	write_element_void		6,0
	write_element_value		6,1,11
	put_value		1,12
	put_value		3,10
	put_value		5,8
	execute		7,kmerge_7_0
wait_kcomp_8_3:
	check_nil		1,wait_kcomp_8_1
	wait_vector		6,2
	read_elements_inc		6,0,9,2
	wait_vector		7,2
	read_elements_inc		7,0,11,2
	atom		8
	branch_on_atom		8,2,wait_kcomp_8_1
	bucket_entry_a		less,wait_kcomp_8_12
	bucket_entry_a		same,wait_kcomp_8_13
wait_kcomp_8_12:
	collect_value		11
	collect_value		9
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,10
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_8_13:
	collect_value		11
	collect_value		9
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,10
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_8_1:
	try_me_else		wait_kcomp_8_14
	jump_on_non_list_var_var		2,wait_kcomp_8_16,14,9
	wait_vector		14,2
	read_elements_inc		14,0,10,2
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	wait_atom		8,greater
	collect_value		12
	put_reused_vector		8,14
	write_element_value		8,0,4
	write_element_value		8,1,13
	get_reused_list_val_var		5,2,2,8,8
	put_reused_vector		7,7
	write_element_void		7,0
	write_element_value		7,1,11
	put_value		2,9
	put_value		4,10
	put_value		5,8
	execute		7,kmerge_7_0
wait_kcomp_8_16:
	check_nil		2,wait_kcomp_8_14
	wait_vector		6,2
	read_elements_inc		6,0,9,2
	wait_vector		7,2
	read_elements_inc		7,0,11,2
	wait_atom		8,greater
	collect_value		11
	collect_value		9
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,10
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
wait_kcomp_8_14:
	otherwise		wait_kcomp_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		4
	collect_value		3
	get_nil		5
	create_goal		1
	set_value		1,2
	enqueue_goal		1,if_raise_error_1_0
	execute		1,if_raise_error_1_0
wait_kcomp_8_39:
	suspend		wait_kcomp_8_0
	module_entry		merger
	predicate		kmerge_descending,7
kmerge_descending_7_0:
	try_me_else		kmerge_descending_7_1
	jump_on_non_list		1,kmerge_descending_7_3
	read_car		1,8
	wait_vector		8,2
	read_elements_inc		8,0,9,2
	read_cdr		1,11
	wait		3
	switch_on_type		3,kmerge_descending_7_5,kmerge_descending_7_6,kmerge_descending_7_1,kmerge_descending_7_1,kmerge_descending_7_1,kmerge_descending_7_7
kmerge_descending_7_5:
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	atom		4
	g_tag_and_value		3,14,15
	g_tag_and_value		4,14,16
	g_not_less_than		15,16
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_6:
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	integer		4
	g_not_less_than		3,4
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_7:
	is_float		3,kmerge_descending_7_1
	wait_vector		6,2
	read_elements_inc		6,0,12,2
	float		4
	g_float_not_less_than		3,4
	collect_value		12
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,13
	get_reused_list_val_var		5,1,1,6,12
	put_reused_vector		6,8
	write_element_void		6,0
	write_element_value		6,1,10
	put_value		1,11
	put_value		3,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_3:
	check_nil		1,kmerge_descending_7_1
	wait		3
	switch_on_type		3,kmerge_descending_7_8,kmerge_descending_7_9,kmerge_descending_7_1,kmerge_descending_7_1,kmerge_descending_7_1,kmerge_descending_7_10
kmerge_descending_7_8:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	atom		4
	g_tag_and_value		3,12,13
	g_tag_and_value		4,12,14
	g_not_less_than		13,14
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_descending_7_9:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	integer		4
	g_not_less_than		3,4
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_descending_7_10:
	is_float		3,kmerge_descending_7_1
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	float		4
	g_float_not_less_than		3,4
	collect_value		10
	collect_value		8
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,9
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
kmerge_descending_7_1:
	try_me_else		kmerge_descending_7_11
	jump_on_non_list		2,kmerge_descending_7_13
	read_car		2,8
	wait_vector		8,2
	read_elements_inc		8,0,9,2
	read_cdr		2,11
	wait		3
	switch_on_type		3,kmerge_descending_7_15,kmerge_descending_7_16,kmerge_descending_7_11,kmerge_descending_7_11,kmerge_descending_7_11,kmerge_descending_7_17
kmerge_descending_7_15:
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	atom		4
	g_tag_and_value		3,14,15
	g_tag_and_value		4,14,16
	g_less_than		15,16
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_16:
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	integer		4
	g_less_than		3,4
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_17:
	is_float		3,kmerge_descending_7_11
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	float		4
	g_float_less_than		3,4
	collect_value		12
	put_reused_vector		7,7
	write_element_value		7,0,4
	write_element_value		7,1,13
	get_reused_list_val_var		5,2,2,7,12
	put_reused_vector		7,8
	write_element_void		7,0
	write_element_value		7,1,10
	put_value		2,11
	put_value		4,9
	put_value		5,12
	execute		7,kmerge_descending_7_0
kmerge_descending_7_13:
	check_nil		2,kmerge_descending_7_11
	wait		3
	switch_on_type		3,kmerge_descending_7_18,kmerge_descending_7_19,kmerge_descending_7_11,kmerge_descending_7_11,kmerge_descending_7_11,kmerge_descending_7_20
kmerge_descending_7_18:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	atom		4
	g_tag_and_value		3,12,13
	g_tag_and_value		4,12,14
	g_less_than		13,14
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_descending_7_19:
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	integer		4
	g_less_than		3,4
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_descending_7_20:
	is_float		3,kmerge_descending_7_11
	wait_vector		6,2
	read_elements_inc		6,0,8,2
	wait_vector		7,2
	read_elements_inc		7,0,10,2
	float		4
	g_float_less_than		3,4
	collect_value		10
	collect_value		8
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,9
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,11
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
kmerge_descending_7_11:
	otherwise		kmerge_descending_7_0
	create_goal		8
	set_values_inc		1,1,2
	set_variable		3,9
	set_variable		4,8
	set_values_inc		5,5,3
	set_variable		8,5
	enqueue_goal		8,wait_kcomp_descending_8_0
	put_values_inc		1,3,2
	put_values_dec		3,9,2
	execute_external		comparator,sort0,5
kmerge_descending_7_40:
	suspend		kmerge_descending_7_0
	module_entry		merger
	predicate		wait_kcomp_descending,8
wait_kcomp_descending_8_0:
	try_me_else		wait_kcomp_descending_8_1
	jump_on_non_list		1,wait_kcomp_descending_8_3
	read_car		1,9
	wait_vector		9,2
	read_elements_inc		9,0,10,2
	read_cdr		1,12
	wait_vector		6,2
	read_elements_inc		6,0,13,2
	atom		8
	branch_on_atom		8,2,wait_kcomp_descending_8_1
	bucket_entry_a		greater,wait_kcomp_descending_8_7
	bucket_entry_a		same,wait_kcomp_descending_8_8
wait_kcomp_descending_8_7:
	collect_value		13
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,14
	get_reused_list_val_var		5,1,1,6,8
	put_reused_vector		6,9
	write_element_void		6,0
	write_element_value		6,1,11
	put_value		1,12
	put_value		3,10
	put_value		5,8
	execute		7,kmerge_descending_7_0
wait_kcomp_descending_8_8:
	collect_value		13
	put_reused_vector		6,6
	write_element_value		6,0,3
	write_element_value		6,1,14
	get_reused_list_val_var		5,1,1,6,8
	put_reused_vector		6,9
	write_element_void		6,0
	write_element_value		6,1,11
	put_value		1,12
	put_value		3,10
	put_value		5,8
	execute		7,kmerge_descending_7_0
wait_kcomp_descending_8_3:
	check_nil		1,wait_kcomp_descending_8_1
	wait_vector		6,2
	read_elements_inc		6,0,9,2
	wait_vector		7,2
	read_elements_inc		7,0,11,2
	atom		8
	branch_on_atom		8,2,wait_kcomp_descending_8_1
	bucket_entry_a		greater,wait_kcomp_descending_8_12
	bucket_entry_a		same,wait_kcomp_descending_8_13
wait_kcomp_descending_8_12:
	collect_value		11
	collect_value		9
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,10
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_descending_8_13:
	collect_value		11
	collect_value		9
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,10
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_descending_8_1:
	try_me_else		wait_kcomp_descending_8_14
	jump_on_non_list_var_var		2,wait_kcomp_descending_8_16,14,9
	wait_vector		14,2
	read_elements_inc		14,0,10,2
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	wait_atom		8,less
	collect_value		12
	put_reused_vector		8,14
	write_element_value		8,0,4
	write_element_value		8,1,13
	get_reused_list_val_var		5,2,2,8,8
	put_reused_vector		7,7
	write_element_void		7,0
	write_element_value		7,1,11
	put_value		2,9
	put_value		4,10
	put_value		5,8
	execute		7,kmerge_descending_7_0
wait_kcomp_descending_8_16:
	check_nil		2,wait_kcomp_descending_8_14
	wait_vector		6,2
	read_elements_inc		6,0,9,2
	wait_vector		7,2
	read_elements_inc		7,0,11,2
	wait_atom		8,less
	collect_value		11
	collect_value		9
	put_reused_vector		2,6
	write_element_value		2,0,3
	write_element_value		2,1,10
	put_list_val_val		3,2,1
	put_reused_vector		1,7
	write_element_value		1,0,4
	write_element_value		1,1,12
	put_list_val_val		2,1,3
	get_list_value		5,2
	proceed
wait_kcomp_descending_8_14:
	otherwise		wait_kcomp_descending_8_0
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		4
	collect_value		3
	get_nil		5
	create_goal		1
	set_value		1,2
	enqueue_goal		1,if_raise_error_1_0
	execute		1,if_raise_error_1_0
wait_kcomp_descending_8_39:
	suspend		wait_kcomp_descending_8_0
	module_entry		merger
	predicate		kmerge_user_defined,8
kmerge_user_defined_8_0:
	put_marked_value		11,8
	put_vector		9,5
	write_elements_inc		9,0,3,2
	write_element_variable		9,2,3
	write_element_variable		9,3,4
	write_element_variable		9,4,10
	b_apply		11,9
	put_value		9,10
	execute		9,wait_kcomp_user_defined_9_0
kmerge_user_defined_8_1:
	suspend		kmerge_user_defined_8_0
	module_entry		merger
	predicate		wait_kcomp_user_defined,9
wait_kcomp_user_defined_9_0:
	try_me_else		wait_kcomp_user_defined_9_1
	jump_on_non_list_var_var		1,wait_kcomp_user_defined_9_3,15,10
	wait_vector		15,2
	read_elements_inc		15,0,11,2
	wait_vector		6,2
	read_elements_inc		6,0,13,2
	wait_atom		9,no
	collect_value		13
	put_reused_vector		9,15
	write_element_value		9,0,3
	write_element_value		9,1,14
	get_reused_list_val_var		5,1,1,9,9
	put_reused_vector		6,6
	write_element_void		6,0
	write_element_value		6,1,12
	put_value		1,10
	put_value		3,11
	put_value		5,9
	execute		8,kmerge_user_defined_8_0
wait_kcomp_user_defined_9_3:
	check_nil		1,wait_kcomp_user_defined_9_1
	wait_vector		6,2
	read_elements_inc		6,0,10,2
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	wait_atom		9,no
	collect_value		8
	collect_value		12
	collect_value		10
	put_reused_vector		1,6
	write_element_value		1,0,4
	write_element_value		1,1,13
	put_list_val_val		4,1,2
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,11
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_user_defined_9_1:
	try_me_else		wait_kcomp_user_defined_9_4
	jump_on_non_list_var_var		2,wait_kcomp_user_defined_9_6,15,10
	wait_vector		15,2
	read_elements_inc		15,0,11,2
	wait_vector		7,2
	read_elements_inc		7,0,13,2
	wait_atom		9,yes
	collect_value		13
	put_reused_vector		9,15
	write_element_value		9,0,3
	write_element_value		9,1,14
	get_reused_list_val_var		5,2,2,9,9
	put_reused_vector		7,7
	write_element_void		7,0
	write_element_value		7,1,12
	put_value		2,10
	put_value		3,4
	put_value		4,11
	put_value		5,9
	execute		8,kmerge_user_defined_8_0
wait_kcomp_user_defined_9_6:
	check_nil		2,wait_kcomp_user_defined_9_4
	wait_vector		6,2
	read_elements_inc		6,0,10,2
	wait_vector		7,2
	read_elements_inc		7,0,12,2
	wait_atom		9,yes
	collect_value		8
	collect_value		12
	collect_value		10
	put_reused_vector		2,6
	write_element_value		2,0,4
	write_element_value		2,1,11
	put_list_val_val		4,2,1
	put_reused_vector		1,7
	write_element_value		1,0,3
	write_element_value		1,1,13
	put_list_val_val		2,1,4
	get_list_value		5,2
	proceed
wait_kcomp_user_defined_9_4:
	otherwise		wait_kcomp_user_defined_9_0
	collect_value		9
	collect_value		8
	collect_value		7
	collect_value		6
	collect_value		4
	collect_value		3
	get_nil		5
	create_goal		1
	set_value		1,2
	enqueue_goal		1,if_raise_error_1_0
	execute		1,if_raise_error_1_0
wait_kcomp_user_defined_9_14:
	suspend		wait_kcomp_user_defined_9_0
	module_entry		merger
	predicate		if_raise_error,1
if_raise_error_1_0:
	try_me_else		if_raise_error_1_1
	wait_list_var_var		1,2,3
	collect_list		1
	collect_value		3
	put_value		1,2
	execute		1,if_raise_error_data_protocol_1_0
if_raise_error_1_1:
	otherwise		if_raise_error_1_0
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_0'
	b_raise		3,2,1
	proceed
if_raise_error_1_5:
	suspend		if_raise_error_1_0
	module_entry		merger
	predicate		if_raise_error_data_protocol,1
if_raise_error_data_protocol_1_0:
	try_me_else		if_raise_error_data_protocol_1_1
	wait_vector		1,2
	read_elements_inc		1,0,2,2
	collect_value		3
	collect_value		2
	collect_vector		1
	proceed
if_raise_error_data_protocol_1_1:
	otherwise		if_raise_error_data_protocol_1_0
	put_integer		3,1024
	put_structured_constant		2,'$SCNST_1'
	b_raise		3,2,1
	proceed
if_raise_error_data_protocol_1_6:
	suspend		if_raise_error_data_protocol_1_0
	begin_const_section		merger
'$SCNST_0_1':
	define_desc		3,4
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1953460848
	define_integer		1819239279
'$SCNST_0_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		key_merge
	define_string		'$SCNST_0_1'
'$SCNST_0':
	define_vector		'$SCNST_0_0'
'$SCNST_1_1':
	define_desc		27,6
	define_integer		1701604457
	define_integer		1600938343
	define_integer		1635017060
	define_integer		1869770847
	define_integer		1868787572
	define_integer		108
'$SCNST_1_0':
	define_desc		0,3
	define_atom		'$PIMOS$'
	define_atom		key_merge
	define_string		'$SCNST_1_1'
'$SCNST_1':
	define_vector		'$SCNST_1_0'
