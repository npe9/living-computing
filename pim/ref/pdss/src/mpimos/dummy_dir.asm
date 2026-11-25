directory:
	module		directory
	entry		create,3,create_3_0
	entry		os_create,6,os_create_6_0
	entry		request,4,request_4_0
	module_entry		directory
	predicate		create,3
create_3_0:
	execute_external		mpimos_directory,create,3
create_3_1:
	suspend		create_3_0
	module_entry		directory
	predicate		os_create,6
os_create_6_0:
	execute_external		mpimos_directory,os_create,6
os_create_6_1:
	suspend		os_create_6_0
	module_entry		directory
	predicate		request,4
request_4_0:
	execute_external		mpimos_directory,request,4
request_4_1:
	suspend		request_4_0
