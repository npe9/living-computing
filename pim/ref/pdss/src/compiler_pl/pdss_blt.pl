%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%  PDSS (PIMOS Development Support System)  Version 2.52		 %
%  (C) Copyright 1988,1989,1990,1991,1992.				 %
%  Institute for New Generation Computer Technology (ICOT), Japan.	 %
%  Read "../COPYRIGHT" for detailed information.			 %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%     Builtin Predicate Table for PDSS V2.5    %%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%%%%% Builtin predicates for passive part

:- public builtin/6.
% builtin(BuiltinPredicate
%         [InputArgumentsList], [OutputArgumentsList],
%	  [InsertedCodeList],
%         [ArgumentTypeList],
%	  Type(calculate/branch/compare/check), Mode(user/pdss))

%% Type check.
%% ( float(X) is macro-expanded term, real builtin is floating_point(X) )
builtin(wait(X),    [1], [], [],        [(X,(wait))],  check, user):- !.
builtin(atom(X),    [1], [], [wait(X)], [(X,atom)],    check, user):- !.
builtin(integer(X), [1], [], [wait(X)], [(X,integer)], check, user):- !.
builtin(float(X),   [1], [], [wait(X)], [(X,float)],   check, user):- !.
builtin(list(X),    [1], [], [wait(X)], [(X,list)],    check, user):- !.
builtin(vector(X),  [1], [], [wait(X)], [(X,vector)],  check, user):- !.
builtin(string(X),  [1], [], [wait(X)], [(X,string)],  check, user):- !.

%% Compare.
builtin(diff(X,Y),          [1,2], [], [],
	[],                        compare, user):- !.

builtin(equal(X,Y),         [1,2], [], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)], compare, user):- !.
builtin(not_equal(X,Y),     [1,2], [], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)], compare, user):- !.
builtin(less_than(X,Y),     [1,2], [], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)], compare, user):- !.
builtin(not_less_than(X,Y), [1,2], [], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)], compare, user):- !.

%% Arithmetic operation.
builtin(add(X,Y,Z),          [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(subtract(X,Y,Z),     [1,2], [3], [integer(X),integer(Y)],
	[(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(multiply(X,Y,Z),     [1,2], [3], [integer(X),integer(Y)],
	[(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(divide(X,Y,Z),       [1,2], [3], [integer(X),integer(Y)],
	[(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(modulo(X,Y,Z),       [1,2], [3], [integer(X),integer(Y)],
	[(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(minus(X,Y),          [1],   [2], [integer(X)], 
	[(X,integer),(Y,integer)],             branch, user):- !.
builtin(increment(X,Y),	     [1],   [2], [integer(X)],
        [(X,integer),(Y,integer)],             branch, user):- !.
builtin(decrement(X,Y),	     [1],   [2], [integer(X)],
        [(X,integer),(Y,integer)],             branch, user):- !.
builtin(abs(X,Y),	     [1],   [2], [integer(X)],
        [(X,integer),(Y,integer)],             branch, user):- !.
builtin(min(X,Y,Z),	     [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)],             calculate, user):- !.
builtin(max(X,Y,Z),	     [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer)],             calculate, user):- !.
builtin(and(X,Y,Z),          [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], calculate, user):- !.
builtin(or(X,Y,Z),           [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], calculate, user):- !.
builtin(exclusive_or(X,Y,Z), [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], calculate, user):- !.
builtin(complement(X,Y),     [1],   [2], [integer(X)],
        [(X,integer),(Y,integer)],             calculate, user):- !.
builtin(shift_left(X,Y,Z),   [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], branch, user):- !.
builtin(shift_right(X,Y,Z),  [1,2], [3], [integer(X),integer(Y)],
        [(X,integer),(Y,integer),(Z,integer)], branch, user):- !.

%% Vector & String
builtin(vector(X,Y),           [1],   [2],   [vector(X)],
	[(X,vector),(Y,integer)], calculate, user):- !.
builtin(vector_element(X,Y,Z), [1,2], [3],   [vector(X),integer(Y)],
	[(X,vector),(Y,integer)], branch, user):- !.
builtin(string(X,Y,Z),         [1],   [2,3], [string(X)],
	[(X,string),(Y,integer),(Z,integer)], calculate, user):- !.
builtin(string_element(X,Y,Z), [1,2], [3],   [string(X),integer(Y)],
	[(X,string),(Y,integer),(Z,integer)], branch, user):- !.

%% Console I/O
builtin(put_console(X),     [1], [],  [], [], calculate, user):- !.
builtin(display_console(X), [1], [],  [], [], calculate, user):- !.
builtin(read_console(X),    [],  [1], [], [], calculate, user):- !.

%% Compare (float).
builtin(floating_point_equal(X,Y),         [1,2], [], [float(X),float(Y)],
        [(X,float),(Y,float)], compare, user):- !.
builtin(floating_point_not_equal(X,Y),     [1,2], [], [float(X),float(Y)],
        [(X,float),(Y,float)], compare, user):- !.
builtin(floating_point_less_than(X,Y),     [1,2], [], [float(X),float(Y)],
        [(X,float),(Y,float)], compare, user):- !.
builtin(floating_point_not_less_than(X,Y), [1,2], [], [float(X),float(Y)],
        [(X,float),(Y,float)], compare, user):- !.

%% Arithmetic operation (float).
builtin(floating_point_add(X,Y,Z),      [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], branch, user):- !.
builtin(floating_point_subtract(X,Y,Z), [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], branch, user):- !.
builtin(floating_point_multiply(X,Y,Z), [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], branch, user):- !.
builtin(floating_point_divide(X,Y,Z),   [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], branch, user):- !.
builtin(floating_point_minus(X,Y),      [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_abs(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_min(X,Y,Z),      [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], calculate, user):- !.
builtin(floating_point_max(X,Y,Z),      [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], calculate, user):- !.
builtin(floating_point_floor(X,Y),      [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_sqrt(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_ln(X,Y),         [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_log(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_exp(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_pow(X,Y,Z),      [1,2], [3], [float(X),float(Y)],
        [(X,float),(Y,float),(Z,float)], branch, user):- !.
builtin(floating_point_sin(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_cos(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_tan(X,Y),        [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_asin(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_acos(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], branch, user):- !.
builtin(floating_point_atan(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_atan(X,Y,Z),     [1,2], [3], [float(X),float(X)],
        [(X,float),(Y,float),(Z,float)], calculate, user):- !.
builtin(floating_point_sinh(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_cosh(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.
builtin(floating_point_tanh(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,float)], calculate, user):- !.

builtin(floating_point_to_integer(X,Y),       [1],   [2], [float(X)],
        [(X,float),(Y,integer)], branch, user):- !.
builtin(integer_to_floating_point(X,Y),       [1],   [2], [integer(X)],
        [(X,integer),(Y,float)], calculate, user):- !.

%% Special
builtin(nop,                [],  [],  [], [], calculate, pdss):- !.
builtin(statistics(A,B,C,D,E,F),       [], [1,2,3,4,5,6], [],
    [(A,integer),(B,integer),(C,integer),(D,integer),(E,integer),(F,integer)],
	calculate, pdss):- !.
builtin(get_cpu_time(A),               [], [1],           [], [(A,integer)],
	calculate, pdss):- !.
builtin(get_current_time(A,B,C,D,E,F), [], [1,2,3,4,5,6], [],
    [(A,integer),(B,integer),(C,integer),(D,integer),(E,integer),(F,integer)],
	calculate, pdss):- !.
builtin(halt(A),            [1], [],  [], [], branch, pdss):- !.
builtin(request_gc(A),      [1], [],  [], [], branch, pdss):- !.
builtin(set_scheduling_switch(A),    [1],     [], [], [], branch, pdss):- !.
builtin(set_trace_switch(A),         [1],     [], [], [], branch, pdss):- !.
builtin(set_backtrace_switch(A),     [1],     [], [], [], branch, pdss):- !.
builtin(device_dup_check(A),         [1],     [], [], [], branch, pdss):- !.

%% Firm Test	90.3.19 Nishizaki
builtin(tag_and_value(X,Y,Z), [1], [2,3],   [],
	[(Y,integer),(Z,integer)], branch, pdss):- !.
builtin(register_tag_and_value(X,Y,Z), [1], [2,3],   [],
	[(Y,integer),(Z,integer)], branch, pdss):- !.
builtin(word(X,Y,Z), [1], [2,3],   [],
	[(Y,integer),(Z,integer)], branch, pdss):- !.
builtin(set_tag_and_value(X,Y,Z), [2,3], [1],
	[integer(Y),integer(Z)], [], calculate, pdss):- !.


%%% Builtin predicates for active part

:- public body_blt/6.
%:- mode body_blt(+, +, -, -, -).

body_blt(':=', 2, ':=', [2], [1], user):- !.
body_blt('$:=', 2, '$:=', [2], [1], user):- !.
body_blt('=',  2, '=', [2,1], [], user):- !.

%% Arithmetic/Logical operation
body_blt(add,		3, b_add,          [1,2], [3], user):- !.
body_blt(subtract,	3, b_subtract,     [1,2], [3], user):- !.
body_blt(multiply,	3, b_multiply,     [1,2], [3], user):- !.
body_blt(divide,	3, b_divide,       [1,2], [3], user):- !.
body_blt(modulo,	3, b_modulo,       [1,2], [3], user):- !.
body_blt(minus,		2, b_minus,        [1],   [2], user):- !.
body_blt(increment,	2, b_increment,    [1],   [2], user):- !.
body_blt(decrement,	2, b_decrement,    [1],   [2], user):- !.
body_blt(abs,		2, b_abs,	   [1],   [2], user):- !.
body_blt(min,		3, b_min,	   [1,2], [3], user):- !.
body_blt(max,		3, b_max,	   [1,2], [3], user):- !.
body_blt(and,		3, b_and,          [1,2], [3], user):- !.
body_blt(or,		3, b_or,           [1,2], [3], user):- !.
body_blt(exclusive_or,	3, b_exclusive_or, [1,2], [3], user):- !.
body_blt(complement,	2, b_complement,   [1],   [2], user):- !.
body_blt(shift_left,	3, b_shift_left,   [1,2], [3], user):- !.
body_blt(shift_right,	3, b_shift_right,  [1,2], [3], user):- !.

%% Vector.
body_blt(vector,	     3, b_vector,           [1],     [2,3], user):- !.
body_blt(new_vector,	     2, b_new_vector,	    [2],     [1],   user):- !.
body_blt(vector_element,     4, b_vector_element,   [1,2],   [3,4], user):- !.
body_blt(set_vector_element, 5, b_set_vector_element,[1,2,4],[3,5], user):- !.

%% String.
body_blt(string,	     4, b_string,           [1],    [2,3,4], user):- !.
body_blt(new_string,	     3, b_new_string,       [2,3],    [1],   user):- !.
body_blt(string_element,     4, b_string_element,   [1,2],    [3,4], user):- !.
body_blt(set_string_element, 4, b_set_string_element,[1,2,3], [4],   user):- !.
body_blt(substring,	     5, b_substring,	    [1,2,3],  [4,5], user):- !.
body_blt(set_substring,      4, b_set_substring,    [1,2,3],  [4],   user):- !.
body_blt(append_string,      3, b_append_string,    [1,2],    [3],   user):- !.
body_blt(string_and,	     4, b_string_and,	    [1,2],    [3,4], user):- !.
body_blt(string_or,	     4, b_string_or,	    [1,2],    [3,4], user):- !.
body_blt(string_exclusive_or,4, b_string_exclusive_or,[1,2],  [3,4], user):- !.
body_blt(string_complement,  2, b_string_complement,[1],      [2],   user):- !.

%% Atom.
body_blt(new_atom,    1, b_new_atom,    [],  [1], user):- !. 
body_blt(intern_atom, 2, b_intern_atom, [2], [1], user):- !. 
body_blt(atom_name,   2, b_atom_name,   [1], [2], user):- !. 
body_blt(atom_number, 2, b_atom_number, [1], [2], user):- !. 

%% Code
body_blt(predicate_to_code,  4, b_predicate_to_code, [1,2,3], [4], user):- !.
body_blt(code_to_predicate,  5, b_code_to_predicate, [1], [2,3,4,5], user):- !.

%% Others.
body_blt(apply,    2, b_apply,    [1,2],   [],    user):- !.
body_blt(raise,    3, b_raise,    [1,2,3], [],    user):- !.
body_blt(merge,    2, b_merge,    [],      [1,2], user):- !.
body_blt(current_processor, 3, b_current_processor, [], [1,2,3], user):- !.
body_blt(current_node,      2, b_current_node,      [], [1,2],   user):- !.
body_blt(current_priority,  3, b_current_priority,  [], [1,2,3], user):- !.
body_blt('RATE',   2, b_rate,     [1],     [2],   user):- !.
body_blt('RLTV',   2, b_rltv,     [1],     [2],   user):- !.
body_blt(hash,     3, b_hash,     [1],     [2,3], user):- !.
body_blt(unbound,  4, b_unbound,  [1],     [2,3,4], user):- !.
body_blt(unbound,  2, b_unbound2, [1],     [2], user):- !.
body_blt(get_print_image, 6, b_get_print_image, [1,2,3], [4,5,6], pdss):- !.

%% Arithmetic operation (float)
body_blt(floating_point_add,	  3, b_float_add,      [1,2], [3], user):- !.
body_blt(floating_point_subtract, 3, b_float_subtract, [1,2], [3], user):- !.
body_blt(floating_point_multiply, 3, b_float_multiply, [1,2], [3], user):- !.
body_blt(floating_point_divide,   3, b_float_divide,   [1,2], [3], user):- !.
body_blt(floating_point_minus,    2, b_float_minus,    [1],   [2], user):- !.
body_blt(floating_point_abs,      2, b_float_abs,      [1],   [2], user):- !.
body_blt(floating_point_min,      3, b_float_min,      [1,2], [3], user):- !.
body_blt(floating_point_max,      3, b_float_max,      [1,2], [3], user):- !.
body_blt(floating_point_floor,    2, b_float_floor,    [1],   [2], user):- !.
body_blt(floating_point_sqrt,     2, b_float_sqrt,     [1],   [2], user):- !.
body_blt(floating_point_ln,       2, b_float_ln,       [1],   [2], user):- !.
body_blt(floating_point_log,      2, b_float_log,      [1],   [2], user):- !.
body_blt(floating_point_exp,      2, b_float_exp,      [1],   [2], user):- !.
body_blt(floating_point_pow,	  3, b_float_pow,      [1,2], [3], user):- !.
body_blt(floating_point_sin,      2, b_float_sin,      [1],   [2], user):- !.
body_blt(floating_point_cos,      2, b_float_cos,      [1],   [2], user):- !.
body_blt(floating_point_tan,      2, b_float_tan,      [1],   [2], user):- !.
body_blt(floating_point_asin,     2, b_float_asin,     [1],   [2], user):- !.
body_blt(floating_point_acos,     2, b_float_acos,     [1],   [2], user):- !.
body_blt(floating_point_atan,     2, b_float_atan,     [1],   [2], user):- !.
body_blt(floating_point_atan,	  3, b_float_atan2,    [1,2], [3], user):- !.
body_blt(floating_point_sinh,     2, b_float_sinh,     [1],   [2], user):- !.
body_blt(floating_point_cosh,     2, b_float_cosh,     [1],   [2], user):- !.
body_blt(floating_point_tanh,     2, b_float_tanh,     [1],   [2], user):- !.

body_blt(floating_point_to_integer, 2, b_float_to_integer, [1], [2], user):- !.
body_blt(integer_to_floating_point, 2, b_integer_to_float, [1], [2], user):- !.

%% Builtin predicate (system-body) %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% Shoen control.
body_blt(create_shoen,     7, b_create_shoen,     [1,2,3,4,5],[6,7], pdss):- !.
body_blt(start_shoen,      2, b_start_shoen,      [1], [2],   pdss):- !.
body_blt(stop_shoen,       2, b_stop_shoen,       [1], [2],   pdss):- !.
body_blt(abort_shoen,      2, b_abort_shoen,      [1], [2],   pdss):- !.
body_blt(remove_shoen,     1, b_remove_shoen,     [1], [],    pdss):- !.
body_blt(shoen_statistics, 3, b_shoen_statistics, [1], [2,3], pdss):- !.
body_blt(shoen_add_resource, 3,
	b_shoen_add_resource, [1,2], [3], pdss):- !.
body_blt(consume_resource, 1, b_consume_resource, [1], [],    pdss):- !.

%% Window.
body_blt(create_window, 4, b_create_window, [1], [2,3,4], pdss):- !.
body_blt(remove_window, 2, b_remove_window, [1], [2],     pdss):- !.
body_blt(show_window,   3, b_show_window,   [1], [2,3],   pdss):- !.
body_blt(hide_window,   3, b_hide_window,   [1], [2,3],   pdss):- !.

%% File.
body_blt(create_file, 2, b_create_file, [],      [1,2], pdss):- !.
body_blt(remove_file, 2, b_remove_file, [1],     [2],   pdss):- !.
body_blt(open_file,   5, b_open_file,   [1,2,3], [4,5], pdss):- !.
body_blt(close_file,  3, b_close_file,  [1],     [2,3], pdss):- !.

%% File & Window I/O.
body_blt(write_char,    4, b_write_char,    [1,2],     [3,4], pdss):- !.
body_blt(write_line,    4, b_write_line,    [1,2],     [3,4], pdss):- !.
body_blt(write_buffer,  4, b_write_buffer,  [1,2],     [3,4], pdss):- !.
body_blt(write_term,    6, b_write_term,    [1,2,3,4], [5,6], pdss):- !.
body_blt(read_char,     4, b_read_char,     [1],       [2,3,4], pdss):- !.
body_blt(read_line,     4, b_read_line,     [1],       [2,3,4], pdss):- !.
body_blt(read_buffer,   5, b_read_buffer,   [1,2],     [3,4,5], pdss):- !.
body_blt(read_token,    5, b_read_token,    [1],       [2,3,4,5], pdss):- !.
body_blt(abort_read_command, 3, b_abort_read_command, [1], [2,3], pdss):- !.

%% Directory.
body_blt(test_directory,     2, b_test_directory,     [1],   [2],   pdss):- !.
body_blt(directory_pathname, 3, b_directory_pathname, [1],   [2,3], pdss):- !.
body_blt(listing_files,      4, b_listing_files,      [1,2], [3,4], pdss):- !.
body_blt(delete_files,       3, b_delete_files,       [1,2], [3],   pdss):- !.

%% Timer.
body_blt(get_time_count,     2, b_get_time_count,     [],  [1,2], pdss):- !.
body_blt(on_at,              3, b_on_at,              [1], [2,3], pdss):- !.
body_blt(on_after,           3, b_on_after,           [1], [2,3], pdss):- !.

%% Code.
body_blt(save_module,           3, b_save_module,      [1,2], [3], pdss):- !.
body_blt(load_module,           3, b_load_module,      [2], [1,3], pdss):- !.
body_blt(assemble_module,       3, b_assemble_module,  [2], [1,3], pdss):- !.
body_blt(remove_module,         2, b_remove_module,    [1], [2],   pdss):- !.
body_blt(get_public_predicates, 3, b_get_public_predicates,[1],[2,3],pdss):- !.
body_blt(trace_module,          3, b_trace_module,     [1,2], [3], pdss):- !.
body_blt(get_module_status,     3, b_get_module_status, [1], [2,3], pdss):- !.
body_blt(spy_predicate,         3, b_spy_predicate,     [1,2], [3], pdss):- !.
body_blt(get_spied_predicates,  3, b_get_spied_predicates,[1],[2,3], pdss):- !.
body_blt(reset_profile_info,    2, b_reset_profile_info,  [1], [2],  pdss):- !.
body_blt(get_profile_info,      3, b_get_profile_info,   [1], [2,3], pdss):- !.

body_blt(get_all_atom_name,	1, b_get_all_atom_name,   [], [1], pdss):- !.
body_blt(unix,			3, b_unix,		 [1,2], [3], pdss):- !.
body_blt(debug_monitor_stream,	3, b_debug_monitor_stream,[1,2,3],[],pdss):- !.
body_blt(get_library_directory,	1, b_get_library_directory, [], [1], pdss):- !.

