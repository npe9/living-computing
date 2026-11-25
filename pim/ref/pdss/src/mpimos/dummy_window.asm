window:
	module		window
	entry		create,2,create_2_0
	entry		create,3,create_3_0
	entry		request,7,request_7_0
	entry		os_create,6,os_create_6_0
	module_entry		window
	predicate		create,2
create_2_0:
	execute_external		mpimos_window,create,2
create_2_1:
	suspend		create_2_0
	module_entry		window
	predicate		create,3
create_3_0:
	execute_external		mpimos_window,create,3
create_3_1:
	suspend		create_3_0
	module_entry		window
	predicate		request,7
request_7_0:
	execute_external		mpimos_window,request,7
request_7_1:
	suspend		request_7_0
	module_entry		window
	predicate		os_create,6
os_create_6_0:
	execute_external		mpimos_window,os_create,6
os_create_6_1:
	suspend		os_create_6_0
