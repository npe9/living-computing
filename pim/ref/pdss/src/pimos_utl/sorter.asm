sorter:
	module		sorter
	entry		sort,2,sort_2_0
	entry		sort,3,sort_3_0
	entry		key_sort,2,key_sort_2_0
	entry		key_sort,3,key_sort_3_0
	entry		merge,3,merge_3_0
	entry		merge,4,merge_4_0
	entry		key_merge,3,key_merge_3_0
	entry		key_merge,4,key_merge_4_0
	module_entry		sorter
	predicate		sort,2
sort_2_0:
	put_value		3,2
	put_atom		2,ascending
	execute		3,sort_3_0
sort_2_1:
	suspend		sort_2_0
	module_entry		sorter
	predicate		key_sort,2
key_sort_2_0:
	put_value		3,2
	put_atom		2,ascending
	execute		3,key_sort_3_0
key_sort_2_1:
	suspend		key_sort_2_0
	module_entry		sorter
	predicate		merge,3
merge_3_0:
	put_value		4,3
	put_atom		3,ascending
	execute_external		merger,merge,4
merge_3_1:
	suspend		merge_3_0
	module_entry		sorter
	predicate		merge,4
merge_4_0:
	execute_external		merger,merge,4
merge_4_1:
	suspend		merge_4_0
	module_entry		sorter
	predicate		key_merge,3
key_merge_3_0:
	put_value		4,3
	put_atom		3,ascending
	execute_external		merger,key_merge,4
key_merge_3_1:
	suspend		key_merge_3_0
	module_entry		sorter
	predicate		key_merge,4
key_merge_4_0:
	execute_external		merger,key_merge,4
key_merge_4_1:
	suspend		key_merge_4_0
	module_entry		sorter
	predicate		sort,3
sort_3_0:
	b_merge		5,4
	get_value		5,1
	create_goal		3
	set_variable		1,5
	set_marked_value		2,2
	set_value		3,3
	enqueue_goal		3,merge_sort_3_0
	put_value		1,4
	put_value		3,5
	put_integer		4,0
	put_integer		5,50
	execute		5,cut_and_sort_respectively_5_0
sort_3_1:
	suspend		sort_3_0
	module_entry		sorter
	predicate		cut_and_sort_respectively,5
cut_and_sort_respectively_5_0:
	try_me_else		cut_and_sort_respectively_5_1
	jump_on_non_list_var_var		1,cut_and_sort_respectively_5_3,6,7
	put_reused_list		9,1
	write_car_variable		9,1
	write_cdr_variable		9,8
	get_list_value		3,9
	b_increment		4,4
	create_goal		3
	put_list_val_var		3,6,6
	set_value		1,3
	set_marked_value		2,2
	set_value		3,1
	enqueue_goal_external		quick_sort,sort,3
	put_value		1,7
	put_value		3,8
	execute		6,cut_6_0
cut_and_sort_respectively_5_3:
	check_nil		1,cut_and_sort_respectively_5_1
	collect_value		5
	collect_value		4
	collect_value		2
	get_nil		3
	proceed
cut_and_sort_respectively_5_1:
	suspend		cut_and_sort_respectively_5_0
	module_entry		sorter
	predicate		cut,6
cut_6_0:
	try_me_else		cut_6_1
	jump_on_non_list_var_var		1,cut_6_3,7,8
	integer		4
	integer		5
	g_less_than		4,5
	get_reused_list_val_var		6,1,1,7,7
	b_increment		4,4
	put_value		1,8
	put_value		6,7
	execute		6,cut_6_0
cut_6_3:
	check_nil		1,cut_6_1
	integer		4
	integer		5
	g_less_than		4,5
	collect_value		2
	get_nil		3
	get_nil		6
	proceed
cut_6_1:
	try_me_else		cut_6_4
	wait_value		4,5
	collect_value		5
	put_value		5,4
	get_nil		6
	put_integer		4,0
	execute		5,cut_and_sort_respectively_5_0
cut_6_4:
	suspend		cut_6_0
	module_entry		sorter
	predicate		merge_sort,3
merge_sort_3_0:
	try_me_else		merge_sort_3_1
	jump_on_non_list_var_var		1,merge_sort_3_3,4,5
	jump_on_non_list_var_var		5,merge_sort_3_5,6,7
	create_goal		3
	set_variable		1,8
	set_marked_value		2,2
	set_value		3,3
	enqueue_goal		3,merge_sort_3_0
	put_reused_list_val_val		1,1,6,7
	put_reused_list_val_val		3,5,4,1
	put_value		1,3
	put_value		3,8
	execute		3,do_merge_sort_3_0
merge_sort_3_5:
	check_nil		5,merge_sort_3_1
	collect_list		1
	collect_value		2
	get_value		3,4
	proceed
merge_sort_3_3:
	check_nil		1,merge_sort_3_1
	collect_value		2
	get_nil		3
	proceed
merge_sort_3_1:
	suspend		merge_sort_3_0
	module_entry		sorter
	predicate		do_merge_sort,3
do_merge_sort_3_0:
	try_me_else		do_merge_sort_3_1
	wait_list_var_var		1,4,7
	wait_list_var_var		7,5,6
	collect_list		7
	put_value		8,2
	put_reused_list		2,1
	write_car_variable		2,7
	write_cdr_variable		2,1
	get_list_value		3,2
	create_goal		3
	set_value		1,6
	set_marked_value		2,8
	set_value		3,1
	enqueue_goal		3,do_merge_sort_3_0
	put_values_inc		1,4,2
	put_values_dec		3,8,2
	execute_external		merger,merge,4
do_merge_sort_3_1:
	otherwise		do_merge_sort_3_0
	collect_value		2
	get_value		1,3
	proceed
do_merge_sort_3_5:
	suspend		do_merge_sort_3_0
	module_entry		sorter
	predicate		key_sort,3
key_sort_3_0:
	b_merge		5,4
	get_value		5,1
	create_goal		3
	set_variable		1,5
	set_marked_value		2,2
	set_value		3,3
	enqueue_goal		3,kmerge_sort_3_0
	put_value		1,4
	put_value		3,5
	put_integer		4,0
	put_integer		5,50
	execute		5,kcut_and_sort_respectively_5_0
key_sort_3_1:
	suspend		key_sort_3_0
	module_entry		sorter
	predicate		kcut_and_sort_respectively,5
kcut_and_sort_respectively_5_0:
	try_me_else		kcut_and_sort_respectively_5_1
	jump_on_non_list_var_var		1,kcut_and_sort_respectively_5_3,6,7
	put_reused_list		9,1
	write_car_variable		9,1
	write_cdr_variable		9,8
	get_list_value		3,9
	b_increment		4,4
	create_goal		3
	put_list_val_var		3,6,6
	set_value		1,3
	set_marked_value		2,2
	set_value		3,1
	enqueue_goal_external		quick_sort,key_sort,3
	put_value		1,7
	put_value		3,8
	execute		6,kcut_6_0
kcut_and_sort_respectively_5_3:
	check_nil		1,kcut_and_sort_respectively_5_1
	collect_value		5
	collect_value		4
	collect_value		2
	get_nil		3
	proceed
kcut_and_sort_respectively_5_1:
	suspend		kcut_and_sort_respectively_5_0
	module_entry		sorter
	predicate		kcut,6
kcut_6_0:
	try_me_else		kcut_6_1
	jump_on_non_list_var_var		1,kcut_6_3,7,8
	integer		4
	integer		5
	g_less_than		4,5
	get_reused_list_val_var		6,1,1,7,7
	b_increment		4,4
	put_value		1,8
	put_value		6,7
	execute		6,kcut_6_0
kcut_6_3:
	check_nil		1,kcut_6_1
	integer		4
	integer		5
	g_less_than		4,5
	collect_value		2
	get_nil		3
	get_nil		6
	proceed
kcut_6_1:
	try_me_else		kcut_6_4
	wait_value		4,5
	collect_value		5
	put_value		5,4
	get_nil		6
	put_integer		4,0
	execute		5,kcut_and_sort_respectively_5_0
kcut_6_4:
	suspend		kcut_6_0
	module_entry		sorter
	predicate		kmerge_sort,3
kmerge_sort_3_0:
	try_me_else		kmerge_sort_3_1
	jump_on_non_list_var_var		1,kmerge_sort_3_3,4,5
	jump_on_non_list_var_var		5,kmerge_sort_3_5,6,7
	create_goal		3
	set_variable		1,8
	set_marked_value		2,2
	set_value		3,3
	enqueue_goal		3,kmerge_sort_3_0
	put_reused_list_val_val		1,1,6,7
	put_reused_list_val_val		3,5,4,1
	put_value		1,3
	put_value		3,8
	execute		3,do_kmerge_sort_3_0
kmerge_sort_3_5:
	check_nil		5,kmerge_sort_3_1
	collect_list		1
	collect_value		2
	get_value		3,4
	proceed
kmerge_sort_3_3:
	check_nil		1,kmerge_sort_3_1
	collect_value		2
	get_nil		3
	proceed
kmerge_sort_3_1:
	suspend		kmerge_sort_3_0
	module_entry		sorter
	predicate		do_kmerge_sort,3
do_kmerge_sort_3_0:
	try_me_else		do_kmerge_sort_3_1
	wait_list_var_var		1,4,7
	wait_list_var_var		7,5,6
	collect_list		7
	put_value		8,2
	put_reused_list		2,1
	write_car_variable		2,7
	write_cdr_variable		2,1
	get_list_value		3,2
	create_goal		3
	set_value		1,6
	set_marked_value		2,8
	set_value		3,1
	enqueue_goal		3,do_kmerge_sort_3_0
	put_values_inc		1,4,2
	put_values_dec		3,8,2
	execute_external		merger,key_merge,4
do_kmerge_sort_3_1:
	otherwise		do_kmerge_sort_3_0
	collect_value		2
	get_value		1,3
	proceed
do_kmerge_sort_3_5:
	suspend		do_kmerge_sort_3_0
