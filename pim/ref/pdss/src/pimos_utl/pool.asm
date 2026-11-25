pool:
	module		pool
	entry		bag,1,bag_1_0
	entry		stack,1,stack_1_0
	entry		queue,1,queue_1_0
	entry		sorted_bag,1,sorted_bag_1_0
	entry		sorted_bag,2,sorted_bag_2_0
	entry		keyed_bag,1,keyed_bag_1_0
	entry		keyed_bag,2,keyed_bag_2_0
	entry		keyed_bag,3,keyed_bag_3_0
	entry		keyed_set,1,keyed_set_1_0
	entry		keyed_set,2,keyed_set_2_0
	entry		keyed_set,3,keyed_set_3_0
	entry		keyed_sorted_bag,1,keyed_sorted_bag_1_0
	entry		keyed_sorted_bag,2,keyed_sorted_bag_2_0
	entry		keyed_sorted_set,1,keyed_sorted_set_1_0
	entry		keyed_sorted_set,2,keyed_sorted_set_2_0
	entry		multiply_keyed_bag,2,multiply_keyed_bag_2_0
	entry		multiply_keyed_bag,3,multiply_keyed_bag_3_0
	module_entry		pool
	predicate		bag,1
bag_1_0:
	put_atom		2,bag
	execute_external		stack,stack,2
bag_1_1:
	suspend		bag_1_0
	module_entry		pool
	predicate		stack,1
stack_1_0:
	put_atom		2,stack
	execute_external		stack,stack,2
stack_1_1:
	suspend		stack_1_0
	module_entry		pool
	predicate		queue,1
queue_1_0:
	execute_external		queue,queue,1
queue_1_1:
	suspend		queue_1_0
	module_entry		pool
	predicate		sorted_bag,1
sorted_bag_1_0:
	put_value		2,1
	put_atom		1,ascending
	execute_external		keyed_sorted_bag,sorted_bag,2
sorted_bag_1_1:
	suspend		sorted_bag_1_0
	module_entry		pool
	predicate		sorted_bag,2
sorted_bag_2_0:
	execute_external		keyed_sorted_bag,sorted_bag,2
sorted_bag_2_1:
	suspend		sorted_bag_2_0
	module_entry		pool
	predicate		keyed_bag,1
keyed_bag_1_0:
	put_value		2,1
	put_atom		1,default
	put_integer		3,1
	execute_external		keyed_bag,keyed_bag,3
keyed_bag_1_1:
	suspend		keyed_bag_1_0
	module_entry		pool
	predicate		keyed_bag,2
keyed_bag_2_0:
	put_value		4,1
	put_value		3,2
	put_atom		1,default
	put_value		2,4
	execute_external		keyed_bag,keyed_bag,3
keyed_bag_2_1:
	suspend		keyed_bag_2_0
	module_entry		pool
	predicate		keyed_bag,3
keyed_bag_3_0:
	execute_external		keyed_bag,keyed_bag,3
keyed_bag_3_1:
	suspend		keyed_bag_3_0
	module_entry		pool
	predicate		keyed_set,1
keyed_set_1_0:
	put_value		2,1
	put_atom		1,default
	put_integer		3,1
	execute_external		keyed_bag,keyed_set,3
keyed_set_1_1:
	suspend		keyed_set_1_0
	module_entry		pool
	predicate		keyed_set,2
keyed_set_2_0:
	put_value		4,1
	put_value		3,2
	put_atom		1,default
	put_value		2,4
	execute_external		keyed_bag,keyed_set,3
keyed_set_2_1:
	suspend		keyed_set_2_0
	module_entry		pool
	predicate		keyed_set,3
keyed_set_3_0:
	execute_external		keyed_bag,keyed_set,3
keyed_set_3_1:
	suspend		keyed_set_3_0
	module_entry		pool
	predicate		keyed_sorted_bag,1
keyed_sorted_bag_1_0:
	put_value		2,1
	put_atom		1,ascending
	execute_external		keyed_sorted_bag,keyed_sorted_bag,2
keyed_sorted_bag_1_1:
	suspend		keyed_sorted_bag_1_0
	module_entry		pool
	predicate		keyed_sorted_bag,2
keyed_sorted_bag_2_0:
	execute_external		keyed_sorted_bag,keyed_sorted_bag,2
keyed_sorted_bag_2_1:
	suspend		keyed_sorted_bag_2_0
	module_entry		pool
	predicate		keyed_sorted_set,1
keyed_sorted_set_1_0:
	put_value		2,1
	put_atom		1,ascending
	execute_external		keyed_sorted_bag,keyed_sorted_set,2
keyed_sorted_set_1_1:
	suspend		keyed_sorted_set_1_0
	module_entry		pool
	predicate		keyed_sorted_set,2
keyed_sorted_set_2_0:
	execute_external		keyed_sorted_bag,keyed_sorted_set,2
keyed_sorted_set_2_1:
	suspend		keyed_sorted_set_2_0
	module_entry		pool
	predicate		multiply_keyed_bag,2
multiply_keyed_bag_2_0:
	put_value		3,2
	put_integer		2,1
	execute_external		multiply_keyed_bag,multiply_keyed_bag,3
multiply_keyed_bag_2_1:
	suspend		multiply_keyed_bag_2_0
	module_entry		pool
	predicate		multiply_keyed_bag,3
multiply_keyed_bag_3_0:
	execute_external		multiply_keyed_bag,multiply_keyed_bag,3
multiply_keyed_bag_3_1:
	suspend		multiply_keyed_bag_3_0
