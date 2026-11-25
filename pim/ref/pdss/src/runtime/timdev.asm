pdss_timer_device:
	module		pdss_timer_device
	entry		timer,1,timer_1_0
	module_entry		pdss_timer_device
	predicate		timer,1
timer_1_0:
	try_me_else		timer_1_1
	put_integer		2,2
	g_device_dup_check		2
	execute		1,timer2_1_0
timer_1_1:
	suspend		timer_1_0
	module_entry		pdss_timer_device
	predicate		timer2,1
timer2_1_0:
	try_me_else		timer2_1_1
	jump_on_non_atom		1,timer2_1_3
	test_nil		1,timer2_1_1
	proceed
timer2_1_3:
	is_vector		1,timer2_1_1
	jump_on_arity		1,6,timer2_1_1
	table_entry		timer2_1_1
	table_entry		timer2_1_1
	table_entry		timer2_1_1
	table_entry		timer2_1_1
	table_entry		timer2_1_4
	table_entry		timer2_1_5
timer2_1_4:
	read_element		1,0,2
	wait_atom		2,get_count
	read_elements_inc		1,1,2,3
	collect_vector		1
	b_get_time_count		1,5
	put_integer		6,1000
	b_multiply		1,6,1
	put_value		6,1
	create_goal		1
	set_value		1,4
	enqueue_goal		1,timer2_1_0
	put_values_inc		1,2,2
	put_values_dec		3,6,2
	execute		4,wait_get_count_4_0
timer2_1_5:
	read_element		1,0,2
	atom		2
	branch_on_atom		2,2,timer2_1_1
	bucket_entry_a		on_after,timer2_1_7
	bucket_entry_a		on_at,timer2_1_8
timer2_1_7:
	read_elements_inc		1,1,3,4
	integer		3
	collect_vector		1
	put_integer		1,999
	b_add		3,1,1
	put_integer		2,1000
	b_divide		1,2,1
	b_on_after		1,3,7
	create_goal		1
	set_value		1,6
	enqueue_goal		1,timer2_1_0
	put_values_inc		1,4,2
	put_value		4,7
	execute		4,wait_on_after_4_0
timer2_1_8:
	read_elements_inc		1,1,3,4
	integer		3
	collect_vector		1
	put_integer		1,999
	b_add		3,1,1
	put_integer		2,1000
	b_divide		1,2,1
	b_on_at		1,3,7
	create_goal		1
	set_value		1,6
	enqueue_goal		1,timer2_1_0
	put_values_inc		1,4,2
	put_value		4,7
	execute		4,wait_on_at_4_0
timer2_1_1:
	suspend		timer2_1_0
	module_entry		pdss_timer_device
	predicate		wait_get_count,4
wait_get_count_4_0:
	try_me_else		wait_get_count_4_1
	wait_integer		4,0
	get_value		1,3
	get_atom		2,'fep#normal'
	proceed
wait_get_count_4_1:
	try_me_else		wait_get_count_4_3
	put_integer		5,0
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_get_count_4_3:
	suspend		wait_get_count_4_0
	module_entry		pdss_timer_device
	predicate		wait_on_at,4
wait_on_at_4_0:
	try_me_else		wait_on_at_4_1
	wait_integer		4,0
	get_atom		2,'fep#normal'
	put_value		2,3
	execute		2,wait_now_2_0
wait_on_at_4_1:
	try_me_else		wait_on_at_4_3
	put_integer		5,0
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_on_at_4_3:
	suspend		wait_on_at_4_0
	module_entry		pdss_timer_device
	predicate		wait_on_after,4
wait_on_after_4_0:
	try_me_else		wait_on_after_4_1
	wait_integer		4,0
	get_atom		2,'fep#normal'
	put_value		2,3
	execute		2,wait_now_2_0
wait_on_after_4_1:
	try_me_else		wait_on_after_4_3
	put_integer		5,0
	g_diff		4,5
	collect_value		4
	collect_value		3
	collect_value		1
	get_atom		2,'fep#abnormal'
	proceed
wait_on_after_4_3:
	suspend		wait_on_after_4_0
	module_entry		pdss_timer_device
	predicate		wait_now,2
wait_now_2_0:
	try_me_else		wait_now_2_1
	wait		2
	get_atom		1,'fep#wake_up'
	proceed
wait_now_2_1:
	suspend		wait_now_2_0
