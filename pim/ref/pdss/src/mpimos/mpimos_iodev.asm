mpimos_io_device:
	module		mpimos_io_device
	entry		windows,1,windows_1_0
	entry		window_request,3,window_request_3_0
	entry		files,1,files_1_0
	entry		file_request,4,file_request_4_0
	entry		timer,1,timer_1_0
	entry		timer_request,3,timer_request_3_0
	module_entry		mpimos_io_device
	predicate		windows,1
windows_1_0:
	execute_external		mpimos_window_device,windows,1
windows_1_1:
	suspend		windows_1_0
	module_entry		mpimos_io_device
	predicate		window_request,3
window_request_3_0:
	execute_external		mpimos_window_device,window_request,3
window_request_3_1:
	suspend		window_request_3_0
	module_entry		mpimos_io_device
	predicate		files,1
files_1_0:
	execute_external		mpimos_file_device,files,1
files_1_1:
	suspend		files_1_0
	module_entry		mpimos_io_device
	predicate		file_request,4
file_request_4_0:
	execute_external		mpimos_file_device,file_request,4
file_request_4_1:
	suspend		file_request_4_0
	module_entry		mpimos_io_device
	predicate		timer,1
timer_1_0:
	execute_external		mpimos_timer_device,timer,1
timer_1_1:
	suspend		timer_1_0
	module_entry		mpimos_io_device
	predicate		timer_request,3
timer_request_3_0:
	execute_external		mpimos_timer_device,timer_request,3
timer_request_3_1:
	suspend		timer_request_3_0
