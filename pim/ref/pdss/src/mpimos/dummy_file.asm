file:
	module		file
	entry		create,3,create_3_0
	entry		create,4,create_4_0
	entry		os_create,7,os_create_7_0
	entry		request,4,request_4_0
	module_entry		file
	predicate		create,3
create_3_0:
	execute_external		mpimos_file,create,3
create_3_1:
	suspend		create_3_0
	module_entry		file
	predicate		create,4
create_4_0:
	execute_external		mpimos_file,create,4
create_4_1:
	suspend		create_4_0
	module_entry		file
	predicate		request,4
request_4_0:
	execute_external		mpimos_file,request,4
request_4_1:
	suspend		request_4_0
	module_entry		file
	predicate		os_create,7
os_create_7_0:
	execute_external		mpimos_file,os_create,7
os_create_7_1:
	suspend		os_create_7_0
